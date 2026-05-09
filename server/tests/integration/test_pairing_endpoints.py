"""HTTP integration tests for `/api/v1/pairing/*`."""

from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jarvis_server.api.app import create_app
from jarvis_server.api.deps import get_db
from jarvis_server.config.settings import Environment, Settings
from jarvis_server.db.base import Base


@pytest.fixture
async def pairing_app() -> AsyncIterator[FastAPI]:
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
async def pairing_client(pairing_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=pairing_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _login(c: httpx.AsyncClient) -> str:
    email = f"pair-{uuid4().hex[:8]}@x.com"
    await c.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery-staple-99",
            "display_name": "Pairing User",
        },
    )
    r = await c.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-horse-battery-staple-99"},
    )
    return r.json()["access_token"]


@pytest.mark.integration
class TestPairingFlow:
    async def test_initiate_returns_code_and_token(
        self, pairing_client: httpx.AsyncClient,
    ) -> None:
        token = await _login(pairing_client)
        r = await pairing_client.post(
            "/api/v1/pairing/initiate",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        body = r.json()
        assert len(body["code"]) == 6 and body["code"].isdigit()
        assert len(body["raw_token"]) >= 32
        assert body["expires_in"] > 0
        assert body["qr_payload"].startswith("jarvispair://")

    async def test_redeem_creates_device_and_token_pair(
        self, pairing_client: httpx.AsyncClient,
    ) -> None:
        access = await _login(pairing_client)
        init = await pairing_client.post(
            "/api/v1/pairing/initiate",
            headers={"Authorization": f"Bearer {access}"},
        )
        raw = init.json()["raw_token"]
        r = await pairing_client.post(
            "/api/v1/pairing/redeem",
            json={
                "raw_token": raw,
                "device_name": "iPhone of Federico",
                "device_platform": "mobile_ios",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["access_token"]
        assert body["refresh_token"]
        # The redeemed device-bound access token can call /api/v1/auth/me
        me = await pairing_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {body['access_token']}"},
        )
        assert me.status_code == 200

    async def test_redeem_invalid_token_400(
        self, pairing_client: httpx.AsyncClient,
    ) -> None:
        r = await pairing_client.post(
            "/api/v1/pairing/redeem",
            json={
                "raw_token": "x" * 48,
                "device_name": "rogue",
            },
        )
        assert r.status_code == 400

    async def test_redeem_twice_409(
        self, pairing_client: httpx.AsyncClient,
    ) -> None:
        access = await _login(pairing_client)
        init = await pairing_client.post(
            "/api/v1/pairing/initiate",
            headers={"Authorization": f"Bearer {access}"},
        )
        raw = init.json()["raw_token"]
        await pairing_client.post(
            "/api/v1/pairing/redeem",
            json={"raw_token": raw, "device_name": "first"},
        )
        replay = await pairing_client.post(
            "/api/v1/pairing/redeem",
            json={"raw_token": raw, "device_name": "second"},
        )
        assert replay.status_code == 409

    async def test_initiate_requires_auth(
        self, pairing_client: httpx.AsyncClient,
    ) -> None:
        r = await pairing_client.post("/api/v1/pairing/initiate")
        assert r.status_code == 401
