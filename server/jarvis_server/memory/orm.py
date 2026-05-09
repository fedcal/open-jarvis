"""ORM models for the memory layer.

A `MemoryItem` is a single piece of context attached to a user.
Vectors are stored externally (Qdrant in prod) and referenced via
``vector_id``; the row holds metadata + plaintext + provenance.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from jarvis_server.db.base import Base


def _uuid_factory() -> UUID:
    return uuid4()


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


class MemoryItem(Base):
    """One memory record owned by exactly one user."""

    __tablename__ = "memory_items"
    __table_args__ = (
        Index("ix_memory_user_kind", "user_id", "kind"),
        Index("ix_memory_user_created", "user_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=_uuid_factory)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True,
    )
    kind: Mapped[str] = mapped_column(String(32), default="note")
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    vector_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default=None, unique=True,
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    source: Mapped[str | None] = mapped_column(String(128), nullable=True, default=None)
    extra_metadata: Mapped[dict[str, str | int | float | bool] | None] = mapped_column(
        "metadata", JSON, nullable=True, default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow,
    )


__all__ = ["MemoryItem"]
