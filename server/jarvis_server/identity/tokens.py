"""JWT issuance and verification.

Open-Jarvis uses **ES256** (ECDSA P-256) for asymmetric token signing:
- the *access token* lives 15 minutes and travels in the `Authorization`
  header on every request,
- the *refresh token* is opaque (random URL-safe string), 30 days TTL,
  hashed with SHA-256 before storage in `sessions.refresh_token_hash`.

A `family_id` groups together every refresh emitted from the same
logical session. On reuse detection (presenting an already-rotated
refresh token), the whole family is revoked.

The signing key pair is loaded from the application Settings; in tests
we generate an ephemeral key on the fly.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final, Literal

from jose import jwt
from jose.exceptions import JWTError

ACCESS_TTL: Final = timedelta(minutes=15)
REFRESH_TTL: Final = timedelta(days=30)
ALGORITHM: Final[str] = "ES256"
ISSUER: Final[str] = "open-jarvis"
AUDIENCE: Final[str] = "jarvis-api"


@dataclass(frozen=True)
class AccessTokenClaims:
    """Decoded representation of an access JWT."""

    subject: str  # user id
    device_id: str | None
    jti: str
    family_id: str
    issued_at: datetime
    expires_at: datetime
    role: str
    type: Literal["access"] = "access"


@dataclass(frozen=True)
class RefreshTokenIssue:
    """Newly minted refresh token: raw value + storage hash."""

    raw: str
    hashed: str
    jti: str
    family_id: str
    expires_at: datetime


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


def hash_refresh(raw: str) -> str:
    """Compute the SHA-256 hex hash of a refresh token for DB storage."""
    return hashlib.sha256(raw.encode()).hexdigest()


def new_refresh_token() -> RefreshTokenIssue:
    """Generate a brand-new refresh token (raw + hash + ids + expiry)."""
    raw = secrets.token_urlsafe(48)
    return RefreshTokenIssue(
        raw=raw,
        hashed=hash_refresh(raw),
        jti=str(uuid.uuid4()),
        family_id=secrets.token_urlsafe(16),
        expires_at=_utcnow() + REFRESH_TTL,
    )


def rotate_refresh(family_id: str) -> RefreshTokenIssue:
    """Generate a new refresh token sharing the same family as a previous one."""
    raw = secrets.token_urlsafe(48)
    return RefreshTokenIssue(
        raw=raw,
        hashed=hash_refresh(raw),
        jti=str(uuid.uuid4()),
        family_id=family_id,
        expires_at=_utcnow() + REFRESH_TTL,
    )


def issue_access_token(
    *,
    user_id: str,
    role: str,
    jti: str,
    family_id: str,
    private_key_pem: str,
    device_id: str | None = None,
    ttl: timedelta = ACCESS_TTL,
) -> tuple[str, datetime]:
    """Sign a fresh access token; returns (encoded_token, expires_at)."""
    now = _utcnow()
    expires = now + ttl
    payload: dict[str, str | int | None] = {
        "sub": user_id,
        "did": device_id,
        "jti": jti,
        "fid": family_id,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "iss": ISSUER,
        "aud": AUDIENCE,
    }
    return jwt.encode(payload, private_key_pem, algorithm=ALGORITHM), expires


def decode_access_token(token: str, public_key_pem: str) -> AccessTokenClaims:
    """Validate signature/expiry and return the decoded claims."""
    try:
        payload = jwt.decode(
            token,
            public_key_pem,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"require": ["sub", "exp", "iat", "jti", "iss", "aud"]},
        )
    except JWTError as exc:
        msg = f"invalid access token: {exc}"
        raise ValueError(msg) from exc

    if payload.get("type") != "access":
        msg = "token type is not 'access'"
        raise ValueError(msg)

    return AccessTokenClaims(
        subject=str(payload["sub"]),
        device_id=payload.get("did"),
        jti=str(payload["jti"]),
        family_id=str(payload["fid"]),
        issued_at=datetime.fromtimestamp(int(payload["iat"]), tz=UTC),
        expires_at=datetime.fromtimestamp(int(payload["exp"]), tz=UTC),
        role=str(payload.get("role", "member")),
    )


__all__ = [
    "ACCESS_TTL",
    "ALGORITHM",
    "AUDIENCE",
    "ISSUER",
    "REFRESH_TTL",
    "AccessTokenClaims",
    "RefreshTokenIssue",
    "decode_access_token",
    "hash_refresh",
    "issue_access_token",
    "new_refresh_token",
    "rotate_refresh",
]
