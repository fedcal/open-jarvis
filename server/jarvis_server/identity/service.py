"""Identity service — orchestrates user lifecycle, sessions and tokens.

The service is **pure async**, takes a `Settings` for configuration and
an `AsyncSession` for persistence. It is designed to be unit-tested in
isolation and reused by HTTP routes, MCP servers, CLI tools, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis_server.identity import passwords as pw
from jarvis_server.identity import tokens as tk
from jarvis_server.identity.enums import (
    DevicePlatform,
    MfaMethod,
    Role,
)
from jarvis_server.identity.orm import (
    AuditEvent,
    Device,
    MfaCredential,
    Session,
    User,
)
from jarvis_server.identity.schemas import (
    LoginRequest,
    MfaChallenge,
    RegisterRequest,
    TokenPair,
    UserPublic,
)


class IdentityError(Exception):
    """Base error for the identity service."""


class EmailAlreadyRegistered(IdentityError):  # noqa: N818 — domain-flavoured naming
    """The email address is already in use."""


class InvalidCredentials(IdentityError):  # noqa: N818
    """Wrong email or password (kept generic to avoid user enumeration)."""


class AccountDisabled(IdentityError):  # noqa: N818
    """The user is currently disabled."""


class RefreshReuseDetected(IdentityError):  # noqa: N818
    """A refresh token from a revoked / rotated family was presented."""


class RefreshExpired(IdentityError):  # noqa: N818
    """The refresh token is past its expiry date."""


@dataclass(frozen=True)
class JwtKeys:
    """Asymmetric JWT key pair used by the service."""

    private_pem: str
    public_pem: str


@dataclass(frozen=True)
class IdentityConfig:
    access_ttl: timedelta
    refresh_ttl: timedelta


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


def _ensure_aware(value: datetime) -> datetime:
    """SQLite drops tzinfo on round-trip — re-attach UTC if missing."""
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def _to_user_public(user: User) -> UserPublic:
    """Convert an ORM User into a frozen Pydantic projection."""
    return UserPublic.model_validate(user, from_attributes=True)


class IdentityService:
    """High-level identity workflows."""

    def __init__(
        self,
        session: AsyncSession,
        keys: JwtKeys,
        config: IdentityConfig,
    ) -> None:
        self._db = session
        self._keys = keys
        self._cfg = config

    # ------------------------------------------------------------------ #
    # Registration                                                        #
    # ------------------------------------------------------------------ #

    async def register(self, payload: RegisterRequest) -> UserPublic:
        """Create a new user with an Argon2id password hash."""
        existing = await self._db.scalar(
            select(User).where(User.email == payload.email),
        )
        if existing is not None:
            raise EmailAlreadyRegistered(payload.email)

        user = User(
            email=payload.email,
            display_name=payload.display_name,
            password_hash=pw.hash_password(payload.password),
            role=Role.MEMBER.value,
        )
        self._db.add(user)
        try:
            await self._db.flush()
        except IntegrityError as exc:  # pragma: no cover - race
            raise EmailAlreadyRegistered(payload.email) from exc

        await self._audit(
            user_id=user.id, action="user.register", outcome="success",
        )
        return _to_user_public(user)

    # ------------------------------------------------------------------ #
    # Login                                                               #
    # ------------------------------------------------------------------ #

    async def login(
        self,
        payload: LoginRequest,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenPair | MfaChallenge:
        """Verify password, register (or reuse) device, issue tokens."""
        user = await self._db.scalar(
            select(User).where(User.email == payload.email),
        )
        # Constant-time path: always run verify_password even if user is None
        ok = pw.verify_password(
            payload.password,
            user.password_hash if user else None,
        )
        if user is None or not ok:
            await self._audit(
                user_id=user.id if user else None,
                action="user.login",
                outcome="fail",
                ip_address=ip_address,
            )
            raise InvalidCredentials

        if not user.is_active:
            await self._audit(
                user_id=user.id, action="user.login",
                outcome="fail.disabled", ip_address=ip_address,
            )
            raise AccountDisabled

        # Rehash on the fly if Argon2 parameters changed
        if pw.needs_rehash(user.password_hash or ""):
            user.password_hash = pw.hash_password(payload.password)

        device = await self._upsert_device(
            user_id=user.id,
            name=payload.device_name,
            platform=payload.device_platform,
        )

        # MFA gate (returns challenge instead of tokens if enrolled)
        if await self._has_active_mfa(user.id):
            return await self._issue_mfa_challenge(user, device)

        tokens = await self._issue_tokens(
            user=user,
            device=device,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        user.last_login_at = _utcnow()
        await self._audit(
            user_id=user.id, action="user.login",
            outcome="success", ip_address=ip_address,
        )
        return tokens

    # ------------------------------------------------------------------ #
    # Refresh rotation                                                    #
    # ------------------------------------------------------------------ #

    async def refresh(
        self,
        raw_refresh_token: str,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenPair:
        """Rotate the refresh token; revoke the entire family on reuse."""
        hashed = tk.hash_refresh(raw_refresh_token)
        row = await self._db.scalar(
            select(Session).where(Session.refresh_token_hash == hashed),
        )
        if row is None:
            raise InvalidCredentials

        now = _utcnow()
        if _ensure_aware(row.expires_at) <= now:
            raise RefreshExpired
        if row.is_revoked:
            # Reuse-detection: invalidate the whole family
            await self._db.execute(
                update(Session)
                .where(Session.family_id == row.family_id)
                .values(is_revoked=True),
            )
            await self._audit(
                user_id=row.user_id, action="session.reuse",
                outcome="fail", ip_address=ip_address,
            )
            raise RefreshReuseDetected

        user = await self._db.get(User, row.user_id)
        if user is None or not user.is_active:
            raise AccountDisabled

        # Rotate: revoke current, issue a fresh one in the same family
        row.is_revoked = True

        device = await self._db.get(Device, row.device_id) if row.device_id else None
        new_pair = tk.rotate_refresh(family_id=row.family_id)
        access_token, access_exp = tk.issue_access_token(
            user_id=str(user.id),
            role=user.role,
            jti=new_pair.jti,
            family_id=new_pair.family_id,
            private_key_pem=self._keys.private_pem,
            device_id=str(device.id) if device else None,
            ttl=self._cfg.access_ttl,
        )
        self._db.add(
            Session(
                user_id=user.id,
                device_id=device.id if device else None,
                jti=new_pair.jti,
                family_id=new_pair.family_id,
                refresh_token_hash=new_pair.hashed,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=new_pair.expires_at,
            ),
        )
        await self._audit(
            user_id=user.id, action="session.refresh",
            outcome="success", ip_address=ip_address,
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=new_pair.raw,
            expires_in=int((access_exp - now).total_seconds()),
            user=_to_user_public(user),
        )

    async def revoke_session(self, jti: str) -> None:
        """Revoke a single session (e.g. on logout)."""
        await self._db.execute(
            update(Session).where(Session.jti == jti).values(is_revoked=True),
        )

    async def revoke_all_user_sessions(self, user_id: UUID) -> None:
        """Force-logout every session of a given user."""
        await self._db.execute(
            update(Session).where(Session.user_id == user_id).values(is_revoked=True),
        )

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #

    async def _upsert_device(
        self,
        *,
        user_id: UUID,
        name: str,
        platform: DevicePlatform,
    ) -> Device:
        existing = await self._db.scalar(
            select(Device).where(
                Device.user_id == user_id,
                Device.name == name,
                Device.platform == platform.value,
            ),
        )
        if existing is not None:
            existing.last_seen = _utcnow()
            return existing
        device = Device(
            user_id=user_id,
            name=name,
            platform=platform.value,
        )
        self._db.add(device)
        await self._db.flush()
        return device

    async def _issue_tokens(
        self,
        *,
        user: User,
        device: Device | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> TokenPair:
        now = _utcnow()
        refresh = tk.new_refresh_token()
        access_token, access_exp = tk.issue_access_token(
            user_id=str(user.id),
            role=user.role,
            jti=refresh.jti,
            family_id=refresh.family_id,
            private_key_pem=self._keys.private_pem,
            device_id=str(device.id) if device else None,
            ttl=self._cfg.access_ttl,
        )
        self._db.add(
            Session(
                user_id=user.id,
                device_id=device.id if device else None,
                jti=refresh.jti,
                family_id=refresh.family_id,
                refresh_token_hash=refresh.hashed,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=refresh.expires_at,
            ),
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh.raw,
            expires_in=int((access_exp - now).total_seconds()),
            user=_to_user_public(user),
        )

    async def _has_active_mfa(self, user_id: UUID) -> bool:
        row = await self._db.scalar(
            select(MfaCredential.id).where(
                MfaCredential.user_id == user_id,
                MfaCredential.is_active.is_(True),
            ),
        )
        return row is not None

    async def _issue_mfa_challenge(
        self, user: User, device: Device,
    ) -> MfaChallenge:
        """Stub: real implementation lands in Step 5 (MFA)."""
        from jarvis_server.identity.tokens import new_refresh_token  # local

        challenge = new_refresh_token()
        return MfaChallenge(
            challenge_token=challenge.raw,
            allowed_methods=[MfaMethod.TOTP, MfaMethod.EMAIL_OTP],
            expires_in=300,
        )

    async def _audit(
        self,
        *,
        user_id: UUID | None,
        action: str,
        outcome: str,
        ip_address: str | None = None,
    ) -> None:
        self._db.add(
            AuditEvent(
                user_id=user_id,
                actor_type="user",
                action=action,
                outcome=outcome,
                ip_address=ip_address,
            ),
        )


__all__ = [
    "AccountDisabled",
    "EmailAlreadyRegistered",
    "IdentityConfig",
    "IdentityError",
    "IdentityService",
    "InvalidCredentials",
    "JwtKeys",
    "RefreshExpired",
    "RefreshReuseDetected",
]
