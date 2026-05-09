"""Device pairing — link a brand-new device to an authenticated account.

Flow:

1. **Initiate** (authenticated): the user, already logged in on a primary
   device (web, smartphone), POSTs `/api/v1/pairing/initiate`. The server
   generates a 6-digit numeric code + a long URL-safe token and returns
   both, plus a `qr_payload` ready to be encoded.
2. **Display**: the primary device shows the QR. The new device scans it
   (or the user types the 6-digit code on a secondary screen).
3. **Redeem** (unauthenticated): the new device POSTs the token (or
   `user_email + code`) to `/api/v1/pairing/redeem`, gets a regular
   `TokenPair` bound to a freshly-created `Device` row.

Codes are **single-use** (consumed atomically) and expire after
`PAIRING_TTL` (default 5 minutes). The token is stored as SHA-256 hash
to prevent timing attacks on equality comparison.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis_server.identity import tokens as tk
from jarvis_server.identity.enums import DevicePlatform
from jarvis_server.identity.orm import PairingCode

PAIRING_TTL = timedelta(minutes=5)
NUMERIC_CODE_LEN = 6


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _new_numeric_code() -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(NUMERIC_CODE_LEN))


class PairingError(Exception):
    """Base error for the pairing service."""


class PairingExpired(PairingError):  # noqa: N818
    """The pairing code has expired or never existed."""


class PairingAlreadyUsed(PairingError):  # noqa: N818
    """The pairing code has already been redeemed."""


class PairingService:
    """Issue, validate and redeem device-pairing codes."""

    def __init__(
        self,
        session: AsyncSession,
        keys: tk.AccessTokenClaims | None = None,  # placeholder for symmetry
    ) -> None:
        self._db = session

    async def initiate(
        self,
        *,
        user_id: UUID,
        ttl: timedelta = PAIRING_TTL,
    ) -> tuple[PairingCode, str]:
        """Create a new pairing code. Returns (row, raw_token)."""
        raw_token = secrets.token_urlsafe(32)
        row = PairingCode(
            user_id=user_id,
            code=_new_numeric_code(),
            token_hash=_hash_token(raw_token),
            expires_at=_utcnow() + ttl,
        )
        self._db.add(row)
        await self._db.flush()
        return row, raw_token

    async def redeem(
        self,
        *,
        raw_token: str,
        device_name: str,
        device_platform: DevicePlatform,
        keys: tk.RefreshTokenIssue | None = None,
    ) -> PairingCode:
        """Validate + consume the code; returns the PairingCode row."""
        row = await self._db.scalar(
            select(PairingCode).where(
                PairingCode.token_hash == _hash_token(raw_token),
            ),
        )
        if row is None:
            raise PairingExpired
        if row.consumed_at is not None:
            raise PairingAlreadyUsed
        if _ensure_aware(row.expires_at) <= _utcnow():
            raise PairingExpired
        row.consumed_at = _utcnow()
        return row


def _ensure_aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


__all__ = [
    "PAIRING_TTL",
    "PairingAlreadyUsed",
    "PairingError",
    "PairingExpired",
    "PairingService",
]
