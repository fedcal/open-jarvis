"""End-to-end tests for the `/api/v1/auth/*` HTTP routes.

Strategy:
- Build a fresh in-memory SQLite engine for each test
- Override the FastAPI `get_db` dependency to yield a session bound to it
- Drive the API through `httpx.AsyncClient` over ASGI
"""

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
async def auth_app() -> AsyncIterator[FastAPI]:
    """A FastAPI app with an isolated in-memory DB and tables ready."""
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
async def auth_client(auth_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=auth_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.integration
class TestRegister:
    async def test_201_creates_user(self, auth_client: httpx.AsyncClient) -> None:
        r = await auth_client.post(
            "/api/v1/auth/register",
            json={
                "email": "alice@example.com",
                "password": "correct-horse-battery-staple-99",
                "display_name": "Alice",
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["email"] == "alice@example.com"
        assert "password" not in body and "password_hash" not in body

    async def test_409_duplicate_email(self, auth_client: httpx.AsyncClient) -> None:
        payload = {
            "email": "bob@example.com",
            "password": "correct-horse-battery-staple-99",
            "display_name": "Bob",
        }
        await auth_client.post("/api/v1/auth/register", json=payload)
        r = await auth_client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 409

    async def test_422_short_password(self, auth_client: httpx.AsyncClient) -> None:
        r = await auth_client.post(
            "/api/v1/auth/register",
            json={
                "email": "carol@example.com",
                "password": "short",
                "display_name": "Carol",
            },
        )
        assert r.status_code == 422


@pytest.mark.integration
class TestLogin:
    async def _register(self, c: httpx.AsyncClient, email: str = "dan@example.com") -> None:
        await c.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "correct-horse-battery-staple-99",
                "display_name": "Dan",
            },
        )

    async def test_returns_token_pair(self, auth_client: httpx.AsyncClient) -> None:
        await self._register(auth_client)
        r = await auth_client.post(
            "/api/v1/auth/login",
            json={
                "email": "dan@example.com",
                "password": "correct-horse-battery-staple-99",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["token_type"] == "Bearer"
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["user"]["email"] == "dan@example.com"

    async def test_401_wrong_password(self, auth_client: httpx.AsyncClient) -> None:
        await self._register(auth_client)
        r = await auth_client.post(
            "/api/v1/auth/login",
            json={
                "email": "dan@example.com",
                "password": "definitely-wrong-password-99",
            },
        )
        assert r.status_code == 401

    async def test_401_unknown_user(self, auth_client: httpx.AsyncClient) -> None:
        r = await auth_client.post(
            "/api/v1/auth/login",
            json={
                "email": "ghost@example.com",
                "password": "correct-horse-battery-staple-99",
            },
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestRefreshAndMe:
    async def _login(
        self, c: httpx.AsyncClient, email: str = "eve@example.com",
    ) -> dict[str, str]:
        await c.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "correct-horse-battery-staple-99",
                "display_name": "Eve",
            },
        )
        r = await c.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "correct-horse-battery-staple-99"},
        )
        assert r.status_code == 200
        return r.json()

    async def test_refresh_rotates_tokens(self, auth_client: httpx.AsyncClient) -> None:
        first = await self._login(auth_client)
        r = await auth_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]},
        )
        assert r.status_code == 200
        second = r.json()
        assert second["refresh_token"] != first["refresh_token"]
        assert second["access_token"] != first["access_token"]

    async def test_refresh_reuse_revokes_family(
        self, auth_client: httpx.AsyncClient,
    ) -> None:
        first = await self._login(auth_client)
        await auth_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]},
        )
        replay = await auth_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]},
        )
        assert replay.status_code == 401

    async def test_me_returns_current_user(self, auth_client: httpx.AsyncClient) -> None:
        tokens = await self._login(auth_client)
        r = await auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert r.status_code == 200
        assert r.json()["email"] == "eve@example.com"

    async def test_me_without_token_is_401(self, auth_client: httpx.AsyncClient) -> None:
        r = await auth_client.get("/api/v1/auth/me")
        assert r.status_code == 401

    async def test_logout_revokes_session(self, auth_client: httpx.AsyncClient) -> None:
        tokens = await self._login(auth_client)
        r = await auth_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert r.status_code == 204
