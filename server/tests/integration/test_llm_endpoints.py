"""HTTP integration tests for `/api/v1/llm/*`."""

from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

import httpx
import pytest
import respx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jarvis_server.api.app import create_app
from jarvis_server.api.deps import get_db
from jarvis_server.config.settings import Environment, Settings
from jarvis_server.db.base import Base


@pytest.fixture
async def llm_app() -> AsyncIterator[FastAPI]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    app = create_app(settings=Settings(environment=Environment.TEST))

    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    app.dependency_overrides[get_db] = _override_db
    try:
        yield app
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.fixture
async def llm_client(llm_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=llm_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _login(c: httpx.AsyncClient) -> str:
    email = f"llm-{uuid4().hex[:8]}@example.com"
    await c.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery-staple-99",
            "display_name": "LLM User",
        },
    )
    r = await c.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-horse-battery-staple-99"},
    )
    return r.json()["access_token"]


@pytest.mark.integration
class TestLLMBackendsEndpoint:
    async def test_unauthenticated_rejected(
        self, llm_client: httpx.AsyncClient,
    ) -> None:
        r = await llm_client.get("/api/v1/llm/backends")
        assert r.status_code == 401

    async def test_lists_default_adapters(self, llm_client: httpx.AsyncClient) -> None:
        token = await _login(llm_client)
        r = await llm_client.get(
            "/api/v1/llm/backends",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        body = r.json()
        names = {b["name"] for b in body["backends"]}
        # Without API keys we still get echo + ollama (probe-only)
        assert {"echo", "ollama"}.issubset(names)
        assert body["default"] in names


@pytest.mark.integration
class TestOllamaModelsEndpoint:
    @respx.mock
    async def test_returns_reachable_with_models(
        self, llm_client: httpx.AsyncClient,
    ) -> None:
        token = await _login(llm_client)
        respx.get("http://127.0.0.1:11434/api/tags").mock(
            return_value=httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": "llama3.2:3b",
                            "size": 1234567,
                            "modified_at": "2026-05-10T00:00:00Z",
                            "details": {
                                "parameter_size": "3B",
                                "family": "llama",
                                "quantization_level": "Q4_K_M",
                            },
                        },
                    ],
                },
            ),
        )
        r = await llm_client.get(
            "/api/v1/llm/ollama/models",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["reachable"] is True
        assert body["models"][0]["name"] == "llama3.2:3b"
        assert body["models"][0]["parameter_size"] == "3B"

    @respx.mock
    async def test_unreachable_daemon_returns_payload_with_flag(
        self, llm_client: httpx.AsyncClient,
    ) -> None:
        token = await _login(llm_client)
        respx.get("http://127.0.0.1:11434/api/tags").mock(
            side_effect=httpx.ConnectError("nope"),
        )
        r = await llm_client.get(
            "/api/v1/llm/ollama/models",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["reachable"] is False
        assert body["error"]
