"""Service-level tests for IdentityService (no HTTP layer involved)."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis_server.identity import tokens as tk
from jarvis_server.identity.orm import Session, User
from jarvis_server.identity.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenPair,
)
from jarvis_server.identity.service import (
    AccountDisabled,
    EmailAlreadyRegistered,
    IdentityService,
    InvalidCredentials,
    JwtKeys,
    RefreshExpired,
    RefreshReuseDetected,
)

PWD = "correct-horse-battery-staple-99"


def _register_payload(email: str = "alice@example.com") -> RegisterRequest:
    return RegisterRequest(
        email=email,
        password=PWD,
        display_name="Alice",
    )


def _login_payload(email: str = "alice@example.com") -> LoginRequest:
    return LoginRequest(email=email, password=PWD)


class TestRegister:
    async def test_creates_user(
        self, service: IdentityService, session: AsyncSession,
    ) -> None:
        user = await service.register(_register_payload())
        assert user.email == "alice@example.com"
        assert user.role.value == "member"
        loaded = await session.scalar(select(User).where(User.email == user.email))
        assert loaded is not None
        assert loaded.password_hash and loaded.password_hash.startswith("$argon2id$")

    async def test_duplicate_email_raises(self, service: IdentityService) -> None:
        await service.register(_register_payload())
        with pytest.raises(EmailAlreadyRegistered):
            await service.register(_register_payload())


class TestLogin:
    async def test_unknown_email_raises_invalid(self, service: IdentityService) -> None:
        with pytest.raises(InvalidCredentials):
            await service.login(_login_payload("ghost@example.com"))

    async def test_wrong_password_raises_invalid(self, service: IdentityService) -> None:
        await service.register(_register_payload())
        bad = LoginRequest(email="alice@example.com", password="wrong-password-12!")
        with pytest.raises(InvalidCredentials):
            await service.login(bad)

    async def test_disabled_user_blocked(
        self, service: IdentityService, session: AsyncSession,
    ) -> None:
        user = await service.register(_register_payload())
        row = await session.get(User, user.id)
        assert row is not None
        row.is_active = False
        with pytest.raises(AccountDisabled):
            await service.login(_login_payload())

    async def test_login_returns_token_pair_and_creates_session(
        self, service: IdentityService, session: AsyncSession, jwt_keys: JwtKeys,
    ) -> None:
        await service.register(_register_payload())
        result = await service.login(_login_payload())
        assert isinstance(result, TokenPair)
        # access token round-trips
        claims = tk.decode_access_token(result.access_token, jwt_keys.public_pem)
        assert claims.role == "member"
        # session row persisted with same JTI
        sess = await session.scalar(select(Session).where(Session.jti == claims.jti))
        assert sess is not None
        assert sess.is_revoked is False


class TestRefresh:
    async def _seed(self, service: IdentityService) -> TokenPair:
        await service.register(_register_payload())
        result = await service.login(_login_payload())
        assert isinstance(result, TokenPair)
        return result

    async def test_rotate_returns_new_tokens(
        self, service: IdentityService, jwt_keys: JwtKeys,
    ) -> None:
        first = await self._seed(service)
        second = await service.refresh(first.refresh_token)
        assert second.access_token != first.access_token
        assert second.refresh_token != first.refresh_token

        # Same family across rotations (ABAC continuity)
        old_claims = tk.decode_access_token(first.access_token, jwt_keys.public_pem)
        new_claims = tk.decode_access_token(second.access_token, jwt_keys.public_pem)
        assert old_claims.family_id == new_claims.family_id

    async def test_reuse_revokes_family(
        self, service: IdentityService, session: AsyncSession,
    ) -> None:
        first = await self._seed(service)
        await service.refresh(first.refresh_token)
        with pytest.raises(RefreshReuseDetected):
            await service.refresh(first.refresh_token)
        # Every session in family is now revoked
        rows = (await session.scalars(select(Session))).all()
        assert all(s.is_revoked for s in rows)

    async def test_unknown_refresh_token_invalid(
        self, service: IdentityService,
    ) -> None:
        with pytest.raises(InvalidCredentials):
            await service.refresh("totally-fake-refresh-token-string-padded-padding")

    async def test_expired_refresh_rejected(
        self,
        service: IdentityService,
        session: AsyncSession,
    ) -> None:
        first = await self._seed(service)
        # Move expiry to the past
        from datetime import UTC, datetime, timedelta
        from sqlalchemy import update
        await session.execute(
            update(Session).values(expires_at=datetime.now(tz=UTC) - timedelta(seconds=1)),
        )
        await session.commit()
        with pytest.raises(RefreshExpired):
            await service.refresh(first.refresh_token)


class TestRevocation:
    async def test_logout_revokes_session(
        self, service: IdentityService, session: AsyncSession, jwt_keys: JwtKeys,
    ) -> None:
        await service.register(_register_payload())
        tokens = await service.login(_login_payload())
        assert isinstance(tokens, TokenPair)
        claims = tk.decode_access_token(tokens.access_token, jwt_keys.public_pem)
        await service.revoke_session(claims.jti)
        row = await session.scalar(select(Session).where(Session.jti == claims.jti))
        assert row is not None and row.is_revoked
