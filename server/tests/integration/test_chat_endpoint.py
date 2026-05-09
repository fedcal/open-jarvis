"""Integration tests for the unified chat API (text + voice modalities)."""

from __future__ import annotations

import json
from uuid import uuid4

import httpx
import pytest


def _valid_turn(modality: str = "text", message: str = "Ciao Jarvis") -> dict:
    return {
        "session_id": str(uuid4()),
        "device_id": str(uuid4()),
        "user_id": str(uuid4()),
        "modality": modality,
        "message": message,
        "language": "it",
    }


@pytest.mark.integration
class TestChatStreamSSE:
    """REST `/api/v1/chat` streaming via Server-Sent Events."""

    async def test_text_modality_returns_sse_stream(self, client: httpx.AsyncClient) -> None:
        async with client.stream(
            "POST", "/api/v1/chat", json=_valid_turn(modality="text", message="Ciao!")
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            body = await response.aread()
        assert b"event: start" in body
        assert b"event: chunk" in body
        assert b"event: end" in body

    async def test_voice_modality_is_acknowledged(self, client: httpx.AsyncClient) -> None:
        async with client.stream(
            "POST", "/api/v1/chat", json=_valid_turn(modality="voice", message="Briefing")
        ) as response:
            assert response.status_code == 200
            body = await response.aread()
        # Stub differentiates voice from text via a localised prefix
        assert b"voce" in body.lower() or b"voice" in body.lower()

    async def test_empty_message_is_rejected(self, client: httpx.AsyncClient) -> None:
        payload = _valid_turn()
        payload["message"] = "   "
        response = await client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422

    async def test_unknown_modality_is_rejected(self, client: httpx.AsyncClient) -> None:
        payload = _valid_turn()
        payload["modality"] = "telepathy"
        response = await client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422

    async def test_extra_fields_are_rejected(self, client: httpx.AsyncClient) -> None:
        payload = {**_valid_turn(), "secret": "leak-attempt"}
        response = await client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422


@pytest.mark.integration
class TestChatModelValidation:
    """Edge cases for the `ChatTurn` model on the wire."""

    async def test_message_too_long_rejected(self, client: httpx.AsyncClient) -> None:
        payload = _valid_turn()
        payload["message"] = "x" * 8193
        response = await client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422

    async def test_invalid_language_tag_rejected(self, client: httpx.AsyncClient) -> None:
        payload = _valid_turn()
        payload["language"] = "italian"  # must be ISO 639-1 like 'it'
        response = await client.post("/api/v1/chat", json=payload)
        assert response.status_code == 422

    async def test_default_modality_is_text(self, client: httpx.AsyncClient) -> None:
        payload = _valid_turn()
        del payload["modality"]
        async with client.stream("POST", "/api/v1/chat", json=payload) as response:
            assert response.status_code == 200


@pytest.mark.integration
class TestChatWebSocket:
    """WebSocket bidirectional channel."""

    async def test_websocket_round_trip(self, app) -> None:
        from fastapi.testclient import TestClient

        with TestClient(app) as client, client.websocket_connect("/api/v1/chat/ws") as ws:
            ws.send_text(json.dumps(_valid_turn(message="Ping")))

            first = json.loads(ws.receive_text())
            assert first["type"] == "start"

            events: list[dict] = [first]
            while True:
                event = json.loads(ws.receive_text())
                events.append(event)
                if event.get("type") == "end":
                    break

            # Final summary record
            summary = json.loads(ws.receive_text())
            assert summary["status"] == "ok"
            assert summary["provider"] == "stub"
            assert summary["latency_ms"] >= 0

        chunk_count = sum(1 for e in events if e.get("type") == "chunk")
        assert chunk_count > 0


@pytest.mark.integration
class TestChatOpenAPI:
    """Ensure the chat endpoints are surfaced in the OpenAPI schema."""

    async def test_chat_path_in_schema(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/openapi.json")
        schema = response.json()
        assert "/api/v1/chat" in schema["paths"]
        chat_post = schema["paths"]["/api/v1/chat"]["post"]
        assert "chat" in chat_post["tags"]
