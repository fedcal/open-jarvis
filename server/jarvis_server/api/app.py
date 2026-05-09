"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jarvis_server import __version__
from jarvis_server.api.routes import auth, chat, health, memory
from jarvis_server.config import get_settings
from jarvis_server.db.base import init_engine

if TYPE_CHECKING:
    from jarvis_server.config.settings import Settings


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run startup / shutdown hooks for the FastAPI application."""
    settings: Settings = get_settings()
    settings.assert_production_safe()
    app.state.settings = settings
    init_engine(settings.database_url)
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and return a configured FastAPI instance."""
    cfg = settings or get_settings()

    app = FastAPI(
        title=cfg.app_name,
        version=__version__,
        description=(
            "Open-Jarvis core server. Provides identity, memory, orchestration "
            "and routing for the Jarvis device mesh."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=_lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allowed_origins,
        allow_credentials=cfg.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(memory.router)
    app.include_router(chat.router)

    return app


__all__ = ["create_app"]
