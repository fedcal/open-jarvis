"""Async SQLAlchemy engine, session factory and declarative `Base`.

A single global engine is created lazily from `Settings.database_url`.
Tests override the engine via the `init_engine()` function so they can
use SQLite in-memory or a Postgres test container.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column

# --------------------------------------------------------------------- #
# Reusable column types                                                  #
# --------------------------------------------------------------------- #

UuidPK = Annotated[UUID, mapped_column(primary_key=True, default=uuid4)]
TimestampUTC = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC)),
]


class Base(MappedAsDataclass, AsyncAttrs, DeclarativeBase):
    """Declarative base shared by every ORM model in the project."""


# --------------------------------------------------------------------- #
# Engine + session factory (lazy, swappable from tests)                  #
# --------------------------------------------------------------------- #

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    """Build (or replace) the global async engine + session factory."""
    global _engine, _session_factory
    _engine = create_async_engine(
        database_url,
        echo=echo,
        future=True,
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(
        _engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    return _engine


def get_engine() -> AsyncEngine:
    if _engine is None:  # pragma: no cover - defensive
        msg = "Engine not initialised — call init_engine() at startup"
        raise RuntimeError(msg)
    return _engine


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a transactional session."""
    if _session_factory is None:  # pragma: no cover - defensive
        msg = "Session factory not initialised — call init_engine() at startup"
        raise RuntimeError(msg)
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


__all__ = ["Base", "TimestampUTC", "UuidPK", "get_engine", "get_session", "init_engine"]
