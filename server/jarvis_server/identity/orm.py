"""SQLAlchemy ORM models for the identity layer.

Tables:
- ``users`` — owner of one or more devices
- ``devices`` — one row per paired device (desktop, mobile, watch, …)
- ``sessions`` — refresh-token records, family-grouped for cascade revocation
- ``mfa_credentials`` — TOTP secrets, backup-code hashes, passkeys
- ``audit_events`` — append-only audit log

The models use SQLAlchemy 2 typed mappings (`Mapped`) and the modern
``MappedAsDataclass`` style for ergonomic construction in tests.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jarvis_server.db.base import Base


def _uuid_factory() -> UUID:
    return uuid4()


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


class User(Base):
    """An owner of devices and conversations."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=_uuid_factory)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(64))
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    role: Mapped[str] = mapped_column(String(16), default="member")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None,
    )

    devices: Mapped[list[Device]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        default_factory=list,
    )
    sessions: Mapped[list[Session]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        default_factory=list,
    )
    mfa_credentials: Mapped[list[MfaCredential]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        default_factory=list,
    )


class Device(Base):
    """A device paired with a user (laptop, smartphone, smartwatch, …)."""

    __tablename__ = "devices"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=_uuid_factory)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True,
    )
    name: Mapped[str] = mapped_column(String(128))
    platform: Mapped[str] = mapped_column(String(32))
    public_key_id: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, unique=True,
    )
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow,
    )

    user: Mapped[User] = relationship(back_populates="devices", default=None)


class Session(Base):
    """A refresh-token issuance record.

    The `family_id` groups together all rotations of one logical session.
    On reuse detection, every row sharing a `family_id` is invalidated.
    """

    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_family_id", "family_id"),
        Index("ix_sessions_expires_at", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=_uuid_factory)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True,
    )
    device_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, default=None,
    )
    jti: Mapped[str] = mapped_column(String(64), unique=True)
    family_id: Mapped[str] = mapped_column(String(64))
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, default=None)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped[User] = relationship(back_populates="sessions", default=None)


class MfaCredential(Base):
    """One MFA factor enrolled by a user (TOTP, backup code, passkey)."""

    __tablename__ = "mfa_credentials"
    __table_args__ = (
        UniqueConstraint("user_id", "method", "label", name="uq_mfa_user_method_label"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=_uuid_factory)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True,
    )
    method: Mapped[str] = mapped_column(String(16))
    label: Mapped[str] = mapped_column(String(64), default="default")
    # encrypted secret (e.g. TOTP seed) or hash (backup codes); never plain
    secret_or_hash: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None,
    )

    user: Mapped[User] = relationship(back_populates="mfa_credentials", default=None)


class AuditEvent(Base):
    """Append-only audit log."""

    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_user_id", "user_id"),
        Index("ix_audit_action", "action"),
        Index("ix_audit_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=_uuid_factory)
    user_id: Mapped[UUID | None] = mapped_column(nullable=True, default=None)
    actor_type: Mapped[str] = mapped_column(String(16), default="user")
    action: Mapped[str] = mapped_column(String(64), default="")
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    outcome: Mapped[str] = mapped_column(String(16), default="success")
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, default=None)
    metadata_: Mapped[dict[str, str | int | float | bool] | None] = mapped_column(
        "metadata", JSON, nullable=True, default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow,
    )


# Reverse-side type hints used in default_factory above
__all__ = [
    "AuditEvent",
    "Device",
    "MfaCredential",
    "Session",
    "User",
]
