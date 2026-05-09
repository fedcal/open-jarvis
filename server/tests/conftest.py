"""Pytest fixtures shared across the test suite."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from jarvis_server.api.app import create_app
from jarvis_server.config import Settings
from jarvis_server.config.settings import Environment, get_settings


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Isolate every test from the host environment.

    Removes any `JARVIS_*` and `.env` related variables so that tests run
    against in-memory defaults unless they explicitly opt in.
    """
    for key in list(os.environ):
        if key.startswith("JARVIS_"):
            monkeypatch.delenv(key, raising=False)
    # Force test environment by default
    monkeypatch.setenv("JARVIS_ENVIRONMENT", "test")
    # Clear lru_cache so each test gets a fresh Settings()
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def settings() -> Settings:
    """Return a fresh Settings() instance bound to the `test` environment."""
    return Settings(environment=Environment.TEST)


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    """Provide a FastAPI app instance built with test settings."""
    return create_app(settings=settings)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    """Async HTTPX client wired to the FastAPI app via ASGITransport."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def anyio_backend() -> str:
    """Pin anyio backend to asyncio (matches FastAPI default)."""
    return "asyncio"


__all__: list[Any] = []
