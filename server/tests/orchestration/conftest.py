"""Fixtures for orchestrator tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jarvis_server.db.base import Base
from jarvis_server.identity.orm import User
from jarvis_server.llm.adapters.echo import EchoAdapter
from jarvis_server.llm.router import LLMRouter
from jarvis_server.memory.embeddings import DeterministicEmbedder
from jarvis_server.memory.service import MemoryService
from jarvis_server.memory.vectorstore import InMemoryVectorStore


@pytest.fixture
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        yield s


@pytest.fixture
async def user_id(session: AsyncSession) -> UUID:
    user = User(
        id=uuid4(),
        email=f"o-{uuid4().hex[:8]}@x.com",
        display_name="Orchestrator User",
    )
    session.add(user)
    await session.flush()
    return user.id


@pytest.fixture
def memory_service(session: AsyncSession) -> MemoryService:
    return MemoryService(
        session=session,
        embedder=DeterministicEmbedder(dim=64),
        vector_store=InMemoryVectorStore(),
    )


@pytest.fixture
def llm_router() -> LLMRouter:
    return LLMRouter([EchoAdapter()])
