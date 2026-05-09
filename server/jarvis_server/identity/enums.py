"""Enums shared across the identity layer."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    """Role hierarchy: OWNER > ADMIN > MEMBER > GUEST."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class Permission(StrEnum):
    """Granular permissions evaluated by the ABAC layer."""

    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    HEALTH_READ = "health:read"
    HEALTH_WRITE = "health:write"
    FINANCE_READ = "finance:read"
    FINANCE_WRITE = "finance:write"
    DEVICE_MANAGE = "device:manage"
    USER_MANAGE = "user:manage"
    LLM_CLOUD = "llm:cloud"
    ADMIN_CONFIG = "admin:config"


_OWNER_PERMISSIONS: frozenset[Permission] = frozenset(Permission)
_ADMIN_PERMISSIONS: frozenset[Permission] = frozenset(
    {
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
        Permission.HEALTH_READ,
        Permission.FINANCE_READ,
        Permission.DEVICE_MANAGE,
        Permission.USER_MANAGE,
        Permission.LLM_CLOUD,
    },
)
_MEMBER_PERMISSIONS: frozenset[Permission] = frozenset(
    {
        Permission.MEMORY_READ,
        Permission.MEMORY_WRITE,
        Permission.LLM_CLOUD,
    },
)
_GUEST_PERMISSIONS: frozenset[Permission] = frozenset({Permission.MEMORY_READ})


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OWNER: _OWNER_PERMISSIONS,
    Role.ADMIN: _ADMIN_PERMISSIONS,
    Role.MEMBER: _MEMBER_PERMISSIONS,
    Role.GUEST: _GUEST_PERMISSIONS,
}


_ROLE_RANK: dict[Role, int] = {
    Role.OWNER: 4,
    Role.ADMIN: 3,
    Role.MEMBER: 2,
    Role.GUEST: 1,
}


def role_satisfies(actual: Role, minimum: Role) -> bool:
    """Return True if `actual` role ranks at or above `minimum`."""
    return _ROLE_RANK[actual] >= _ROLE_RANK[minimum]


class DevicePlatform(StrEnum):
    """Supported device families for pairing."""

    DESKTOP = "desktop"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    WATCH = "watch"
    GLASSES = "glasses"
    VR = "vr"
    HOLO = "holo"
    WEB = "web"
    OTHER = "other"


class MfaMethod(StrEnum):
    """MFA factors enrolable per user."""

    TOTP = "totp"
    EMAIL_OTP = "email_otp"
    PASSKEY = "passkey"
    BACKUP_CODE = "backup_code"


__all__ = [
    "ROLE_PERMISSIONS",
    "DevicePlatform",
    "MfaMethod",
    "Permission",
    "Role",
    "role_satisfies",
]
