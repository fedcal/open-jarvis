"""Fixtures for memory-layer tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jarvis_server.db.base import Base
from jarvis_server.identity.orm import User
from jarvis_server.memory.embeddings import DeterministicEmbedder
from jarvis_server.memory.service import MemoryService
from jarvis_server.memory.vectorstore import InMemoryVectorStore


@pytest.fixture
async def engine():  # noqa: ANN201
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:  # noqa: ANN001
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        yield s


@pytest.fixture
def embedder() -> DeterministicEmbedder:
    return DeterministicEmbedder(dim=64)


@pytest.fixture
def vector_store() -> InMemoryVectorStore:
    return InMemoryVectorStore()


@pytest.fixture
def service(
    session: AsyncSession,
    embedder: DeterministicEmbedder,
    vector_store: InMemoryVectorStore,
) -> MemoryService:
    return MemoryService(session=session, embedder=embedder, vector_store=vector_store)


@pytest.fixture
async def user_id(session: AsyncSession) -> UUID:
    """Create a real User row so memories satisfy FK constraints."""
    user = User(
        id=uuid4(),
        email=f"user-{uuid4().hex[:8]}@example.com",
        display_name="Tester",
    )
    session.add(user)
    await session.flush()
    return user.id
