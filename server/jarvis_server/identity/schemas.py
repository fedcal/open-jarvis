"""Pydantic v2 schemas for the identity layer (request / response)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from jarvis_server.identity.enums import (
    ROLE_PERMISSIONS,
    DevicePlatform,
    MfaMethod,
    Permission,
    Role,
)

PasswordStr = Annotated[str, Field(min_length=12, max_length=256)]
DisplayNameStr = Annotated[
    str,
    StringConstraints(min_length=2, max_length=64, strip_whitespace=True),
]


# --------------------------------------------------------------------------- #
# Read schemas (responses)                                                    #
# --------------------------------------------------------------------------- #


class UserPublic(BaseModel):
    """Public profile of a user (safe for any authenticated peer)."""

    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID
    email: EmailStr
    display_name: str
    role: Role
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    last_login_at: datetime | None = None

    @property
    def permissions(self) -> frozenset[Permission]:
        """Permissions derived from the user's role."""
        return ROLE_PERMISSIONS[self.role]


class DevicePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID
    user_id: UUID
    name: str
    platform: DevicePlatform
    is_trusted: bool
    last_seen: datetime
    created_at: datetime


class SessionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID
    user_id: UUID
    device_id: UUID | None
    jti: str
    family_id: str
    is_revoked: bool
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    expires_at: datetime


# --------------------------------------------------------------------------- #
# Write schemas (requests)                                                    #
# --------------------------------------------------------------------------- #


class RegisterRequest(BaseModel):
    """Self-registration of a new user."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: PasswordStr
    display_name: DisplayNameStr


class LoginRequest(BaseModel):
    """Standard email + password login."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: PasswordStr
    device_name: Annotated[str, Field(min_length=1, max_length=128)] = "default"
    device_platform: DevicePlatform = DevicePlatform.WEB


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: Annotated[str, Field(min_length=32, max_length=512)]


class TokenPair(BaseModel):
    """Access + refresh tokens emitted on login or refresh."""

    model_config = ConfigDict(frozen=True)

    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"] = "Bearer"  # noqa: S105 — RFC 6750 token-type marker, not a password
    expires_in: int  # seconds until access_token expires
    user: UserPublic


class MfaChallenge(BaseModel):
    """Returned by login when the user has MFA enrolled.

    The client must complete one of the listed methods within
    `expires_in` seconds before tokens are issued.
    """

    model_config = ConfigDict(frozen=True)

    mfa_required: Literal[True] = True
    challenge_token: str
    allowed_methods: list[MfaMethod]
    expires_in: int


class TotpEnrolBegin(BaseModel):
    """Server reply to start TOTP enrolment."""

    model_config = ConfigDict(frozen=True)

    otpauth_uri: str
    qr_png_base64: str
    secret: str  # Base32; show only once during enrolment


class TotpEnrolConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: Annotated[str, Field(min_length=6, max_length=6, pattern=r"^\d{6}$")]


class MfaVerifyRequest(BaseModel):
    """Submit a TOTP / email / backup code for an active challenge."""

    model_config = ConfigDict(extra="forbid")

    challenge_token: str
    method: MfaMethod
    code: Annotated[str, Field(min_length=6, max_length=12)]


class BackupCodes(BaseModel):
    """One-time recovery codes shown during MFA enrolment."""

    model_config = ConfigDict(frozen=True)

    codes: list[str]


__all__ = [
    "BackupCodes",
    "DevicePublic",
    "DisplayNameStr",
    "LoginRequest",
    "MfaChallenge",
    "MfaVerifyRequest",
    "PasswordStr",
    "RefreshRequest",
    "RegisterRequest",
    "SessionPublic",
    "TokenPair",
    "TotpEnrolBegin",
    "TotpEnrolConfirmRequest",
    "UserPublic",
]
