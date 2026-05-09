"""Fixtures for identity-layer tests.

Each test gets a fresh in-memory SQLite engine so the suite stays
fully hermetic and parallelisable.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jarvis_server.db.base import Base
from jarvis_server.identity.service import IdentityConfig, IdentityService, JwtKeys
from jarvis_server.security.keys import generate_es256_keypair


@pytest.fixture
async def engine():  # noqa: ANN201 — pytest fixture
    """Spin up a fresh in-memory SQLite engine and run all migrations."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:  # noqa: ANN001
    """Async session fixture bound to the per-test engine."""
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as s:
        yield s
        await s.rollback()


@pytest.fixture(scope="session")
def jwt_keys() -> JwtKeys:
    """One key pair shared across all identity tests."""
    pair = generate_es256_keypair()
    return JwtKeys(private_pem=pair.private_pem, public_pem=pair.public_pem)


@pytest.fixture
def identity_config() -> IdentityConfig:
    return IdentityConfig(
        access_ttl=timedelta(minutes=15),
        refresh_ttl=timedelta(days=30),
    )


@pytest.fixture
def service(
    session: AsyncSession,
    jwt_keys: JwtKeys,
    identity_config: IdentityConfig,
) -> IdentityService:
    return IdentityService(session=session, keys=jwt_keys, config=identity_config)
