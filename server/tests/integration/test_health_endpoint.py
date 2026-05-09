"""Integration tests for the `/health` HTTP endpoint."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest

from jarvis_server import __version__


@pytest.mark.integration
class TestHealthEndpoint:
    """End-to-end tests on the FastAPI app via ASGI transport."""

    async def test_returns_200_ok(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_response_body_shape(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/health")
        body = response.json()
        assert body["status"] == "ok"
        assert body["version"] == __version__
        assert body["environment"] == "test"
        assert isinstance(body["dependencies"], list)
        assert all("name" in d and "status" in d for d in body["dependencies"])

    async def test_dependencies_are_skipped_in_phase_1_0(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/health")
        body = response.json()
        names = {d["name"] for d in body["dependencies"]}
        assert {"postgres", "redis", "qdrant"}.issubset(names)
        for dep in body["dependencies"]:
            assert dep["status"] == "skipped"

    async def test_timestamp_is_recent_iso8601(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/health")
        body = response.json()
        ts = datetime.fromisoformat(body["timestamp"])
        delta = abs((datetime.now(tz=UTC) - ts).total_seconds())
        assert delta < 5.0


@pytest.mark.integration
class TestOpenApi:
    """Verify the OpenAPI schema is exposed."""

    async def test_openapi_json_available(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["openapi"].startswith("3.")
        assert schema["info"]["title"] == "Open-Jarvis"
        assert schema["info"]["version"] == __version__

    async def test_health_path_in_schema(self, client: httpx.AsyncClient) -> None:
        response = await client.get("/openapi.json")
        schema = response.json()
        assert "/health" in schema["paths"]


@pytest.mark.integration
class TestCors:
    """Ensure CORS middleware honours configured origins."""

    async def test_preflight_allows_known_origin(self, client: httpx.AsyncClient) -> None:
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
