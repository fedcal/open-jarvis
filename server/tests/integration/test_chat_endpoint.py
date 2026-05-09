"""Integration tests for the unified chat API (text + voice modalities).

Uses an isolated in-memory DB + auth-protected endpoints, mirroring the
pattern of `test_auth_endpoints.py` and `test_memory_endpoints.py`.
"""

from __future__ import annotations

import json
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
async def chat_app() -> AsyncIterator[FastAPI]:
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
async def chat_client(chat_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=chat_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _login_returning_user(c: httpx.AsyncClient) -> dict[str, str]:
    """Register + login, return {access_token, refresh_token, user_id}."""
    email = f"chat-{uuid4().hex[:8]}@example.com"
    await c.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "correct-horse-battery-staple-99",
            "display_name": "Chat User",
        },
    )
    r = await c.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-horse-battery-staple-99"},
    )
    body = r.json()
    return {
        "access_token": body["access_token"],
        "user_id": body["user"]["id"],
    }


def _turn(user_id: str, modality: str = "text", message: str = "Ciao Jarvis") -> dict:
    return {
        "session_id": str(uuid4()),
        "device_id": str(uuid4()),
        "user_id": user_id,
        "modality": modality,
        "message": message,
        "language": "it",
    }


@pytest.mark.integration
class TestChatStreamSSE:
    async def test_unauthenticated_rejected(
        self, chat_client: httpx.AsyncClient,
    ) -> None:
        r = await chat_client.post(
            "/api/v1/chat", json=_turn(str(uuid4())),
        )
        assert r.status_code == 401

    async def test_text_modality_returns_sse_stream(
        self, chat_client: httpx.AsyncClient,
    ) -> None:
        creds = await _login_returning_user(chat_client)
        headers = {"Authorization": f"Bearer {creds['access_token']}"}
        async with chat_client.stream(
            "POST", "/api/v1/chat",
            headers=headers,
            json=_turn(creds["user_id"], "text", "Ciao!"),
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            body = await response.aread()
        assert b"event: start" in body
        assert b"event: chunk" in body
        assert b"event: end" in body

    async def test_voice_modality_metadata_propagated(
        self, chat_client: httpx.AsyncClient,
    ) -> None:
        creds = await _login_returning_user(chat_client)
        headers = {"Authorization": f"Bearer {creds['access_token']}"}
        async with chat_client.stream(
            "POST", "/api/v1/chat",
            headers=headers,
            json=_turn(creds["user_id"], "voice", "Briefing"),
        ) as response:
            assert response.status_code == 200
            body = await response.aread()
        assert b'"modality":"voice"' in body

    async def test_user_id_must_match_token(
        self, chat_client: httpx.AsyncClient,
    ) -> None:
        creds = await _login_returning_user(chat_client)
        headers = {"Authorization": f"Bearer {creds['access_token']}"}
        r = await chat_client.post(
            "/api/v1/chat", headers=headers, json=_turn(str(uuid4())),
        )
        assert r.status_code == 403

    async def test_empty_message_is_rejected(
        self, chat_client: httpx.AsyncClient,
    ) -> None:
        creds = await _login_returning_user(chat_client)
        headers = {"Authorization": f"Bearer {creds['access_token']}"}
        payload = _turn(creds["user_id"])
        payload["message"] = "   "
        r = await chat_client.post("/api/v1/chat", headers=headers, json=payload)
        assert r.status_code == 422

    async def test_unknown_modality_is_rejected(
        self, chat_client: httpx.AsyncClient,
    ) -> None:
        creds = await _login_returning_user(chat_client)
        headers = {"Authorization": f"Bearer {creds['access_token']}"}
        payload = _turn(creds["user_id"])
        payload["modality"] = "telepathy"
        r = await chat_client.post("/api/v1/chat", headers=headers, json=payload)
        assert r.status_code == 422


@pytest.mark.integration
class TestChatWebSocket:
    async def test_ws_requires_token(self, chat_app: FastAPI) -> None:
        from fastapi.testclient import TestClient
        with (
            TestClient(chat_app) as client,
            pytest.raises(Exception),  # noqa: B017
            client.websocket_connect("/api/v1/chat/ws"),
        ):
            pass

    async def test_ws_round_trip(self, chat_app: FastAPI) -> None:
        from fastapi.testclient import TestClient
        with TestClient(chat_app) as bootstrap:
            bootstrap.post(
                "/api/v1/auth/register",
                json={
                    "email": "ws@example.com",
                    "password": "correct-horse-battery-staple-99",
                    "display_name": "WS User",
                },
            )
            r = bootstrap.post(
                "/api/v1/auth/login",
                json={
                    "email": "ws@example.com",
                    "password": "correct-horse-battery-staple-99",
                },
            )
            data = r.json()
            user_id = data["user"]["id"]
            access = data["access_token"]

            with bootstrap.websocket_connect(
                "/api/v1/chat/ws",
                headers={"Authorization": f"Bearer {access}"},
            ) as ws:
                ws.send_text(json.dumps(_turn(user_id, message="Ping")))
                first = json.loads(ws.receive_text())
                assert first["type"] == "start"

                events: list[dict] = [first]
                while True:
                    event = json.loads(ws.receive_text())
                    events.append(event)
                    if event.get("type") == "end":
                        break
                summary = json.loads(ws.receive_text())
                assert summary["status"] == "ok"
                assert summary["provider"] == "orchestrator"

        chunk_count = sum(1 for e in events if e.get("type") == "chunk")
        assert chunk_count > 0


@pytest.mark.integration
class TestChatOpenAPI:
    async def test_chat_path_in_schema(self, chat_client: httpx.AsyncClient) -> None:
        response = await chat_client.get("/openapi.json")
        schema = response.json()
        assert "/api/v1/chat" in schema["paths"]
        assert "chat" in schema["paths"]["/api/v1/chat"]["post"]["tags"]
