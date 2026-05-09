"""Health and readiness endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from jarvis_server import __version__
from jarvis_server.config import Settings, get_settings

router = APIRouter(tags=["system"])


class DependencyHealth(BaseModel):
    """Reports the health of a single downstream dependency."""

    name: str
    status: Literal["ok", "degraded", "down", "skipped"]
    detail: str | None = None


class HealthResponse(BaseModel):
    """Top-level health response payload."""

    status: Literal["ok", "degraded", "down"]
    version: str = Field(description="Semantic version of the running server")
    environment: str
    timestamp: datetime
    dependencies: list[DependencyHealth] = Field(default_factory=list)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Server liveness and readiness probe",
    response_description="Aggregated health of the server and its dependencies",
)
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Return the aggregated health of the server.

    Lightweight probe suitable for Kubernetes liveness/readiness, Docker
    healthchecks and external monitoring. Future iterations will report on
    PostgreSQL, Redis, Qdrant and configured LLM providers.
    """
    deps: list[DependencyHealth] = [
        DependencyHealth(
            name="postgres",
            status="skipped",
            detail="not yet wired in this phase",
        ),
        DependencyHealth(
            name="redis",
            status="skipped",
            detail="not yet wired in this phase",
        ),
        DependencyHealth(
            name="qdrant",
            status="skipped",
            detail="not yet wired in this phase",
        ),
    ]

    return HealthResponse(
        status="ok",
        version=__version__,
        environment=str(settings.environment),
        timestamp=datetime.now(tz=UTC),
        dependencies=deps,
    )


__all__ = ["DependencyHealth", "HealthResponse", "router"]
