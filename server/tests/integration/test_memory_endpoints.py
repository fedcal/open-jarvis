"""HTTP integration tests for `/api/v1/memory/*` (auth + RBAC enforced)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jarvis_server.api.app import create_app
from jarvis_server.api.deps import get_db
from jarvis_server.config.settings import Environment, Settings
from jarvis_server.db.base import Base


@pytest.fixture
async def memory_app() -> AsyncIterator[FastAPI]:
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
async def memory_client(memory_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=memory_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _login(c: httpx.AsyncClient, email: str = "memuser@example.com") -> str:
    """Register + login, return access token."""
    await c.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery-staple-99",
            "display_name": "Mem User",
        },
    )
    r = await c.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-horse-battery-staple-99"},
    )
    return r.json()["access_token"]


@pytest.mark.integration
class TestMemoryEndpoints:
    async def test_unauthenticated_requests_rejected(
        self, memory_client: httpx.AsyncClient,
    ) -> None:
        r = await memory_client.post(
            "/api/v1/memory/record", json={"content": "x"},
        )
        assert r.status_code == 401

    async def test_record_then_search(self, memory_client: httpx.AsyncClient) -> None:
        token = await _login(memory_client)
        h = {"Authorization": f"Bearer {token}"}

        r = await memory_client.post(
            "/api/v1/memory/record",
            headers=h,
            json={"content": "I love sailing in Portofino", "kind": "preference"},
        )
        assert r.status_code == 201
        item_id = r.json()["id"]

        s = await memory_client.post(
            "/api/v1/memory/search",
            headers=h,
            json={"query": "I love sailing in Portofino", "top_k": 3},
        )
        assert s.status_code == 200
        hits = s.json()["hits"]
        assert any(h_["item"]["id"] == item_id for h_ in hits)

    async def test_list_returns_recent(self, memory_client: httpx.AsyncClient) -> None:
        token = await _login(memory_client, "list@example.com")
        h = {"Authorization": f"Bearer {token}"}
        await memory_client.post(
            "/api/v1/memory/record", headers=h, json={"content": "alpha"},
        )
        await memory_client.post(
            "/api/v1/memory/record", headers=h, json={"content": "beta"},
        )
        r = await memory_client.get("/api/v1/memory/list", headers=h)
        assert r.status_code == 200
        body = r.json()
        contents = [item["content"] for item in body]
        assert "alpha" in contents and "beta" in contents

    async def test_forget_single_item(self, memory_client: httpx.AsyncClient) -> None:
        token = await _login(memory_client, "forget@example.com")
        h = {"Authorization": f"Bearer {token}"}
        r = await memory_client.post(
            "/api/v1/memory/record", headers=h, json={"content": "ephemeral"},
        )
        item_id = r.json()["id"]
        d = await memory_client.delete(f"/api/v1/memory/{item_id}", headers=h)
        assert d.status_code == 204
        d2 = await memory_client.delete(f"/api/v1/memory/{item_id}", headers=h)
        assert d2.status_code == 404

    async def test_forget_all(self, memory_client: httpx.AsyncClient) -> None:
        token = await _login(memory_client, "forgetall@example.com")
        h = {"Authorization": f"Bearer {token}"}
        for i in range(3):
            await memory_client.post(
                "/api/v1/memory/record", headers=h, json={"content": f"x{i}"},
            )
        r = await memory_client.delete("/api/v1/memory", headers=h)
        assert r.status_code == 200
        assert r.json()["deleted"] == 3

    async def test_validation_rejects_empty_content(
        self, memory_client: httpx.AsyncClient,
    ) -> None:
        token = await _login(memory_client, "valid@example.com")
        h = {"Authorization": f"Bearer {token}"}
        r = await memory_client.post(
            "/api/v1/memory/record", headers=h, json={"content": ""},
        )
        assert r.status_code == 422
