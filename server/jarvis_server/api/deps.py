"""Reusable FastAPI dependencies for HTTP routes.

Centralised here so that routes stay declarative and testing can swap
out a single dependency (e.g. `get_identity_service`) without touching
route code.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis_server.config import get_settings
from jarvis_server.config.settings import Settings
from jarvis_server.db.base import get_session
from jarvis_server.identity import tokens as tk
from jarvis_server.identity.enums import Permission, Role, role_satisfies
from jarvis_server.identity.service import (
    IdentityConfig,
    IdentityService,
    JwtKeys,
)
from jarvis_server.llm.adapters.echo import EchoAdapter
from jarvis_server.llm.router import LLMRouter
from jarvis_server.memory.embeddings import DeterministicEmbedder, Embedder
from jarvis_server.memory.service import MemoryService
from jarvis_server.memory.vectorstore import InMemoryVectorStore, VectorStore
from jarvis_server.orchestration.graph import Orchestrator, StateGraph
from jarvis_server.orchestration.tools import LLMTool, MemorySearchTool
from jarvis_server.security.keys import generate_es256_keypair

_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _ephemeral_keys() -> JwtKeys:
    """Generate a process-local key pair for development environments."""
    pair = generate_es256_keypair()
    return JwtKeys(private_pem=pair.private_pem, public_pem=pair.public_pem)


def get_jwt_keys(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JwtKeys:
    """Return the JWT key pair, generating an ephemeral one if missing."""
    if settings.jwt_private_key_pem and settings.jwt_public_key_pem:
        return JwtKeys(
            private_pem=settings.jwt_private_key_pem.get_secret_value(),
            public_pem=settings.jwt_public_key_pem.get_secret_value(),
        )
    return _ephemeral_keys()


def get_identity_config(
    settings: Annotated[Settings, Depends(get_settings)],
) -> IdentityConfig:
    return IdentityConfig(
        access_ttl=timedelta(seconds=settings.jwt_access_ttl_seconds),
        refresh_ttl=timedelta(seconds=settings.jwt_refresh_ttl_seconds),
    )


async def get_db() -> AsyncIterator[AsyncSession]:
    """Re-export of the DB session dependency (single import-point)."""
    async for session in get_session():
        yield session


def get_identity_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    keys: Annotated[JwtKeys, Depends(get_jwt_keys)],
    config: Annotated[IdentityConfig, Depends(get_identity_config)],
) -> IdentityService:
    return IdentityService(session=db, keys=keys, config=config)


# --------------------------------------------------------------------- #
# Memory layer                                                           #
# --------------------------------------------------------------------- #


@lru_cache(maxsize=1)
def _default_embedder() -> Embedder:
    """Process-wide deterministic embedder used when no real backend is wired."""
    return DeterministicEmbedder()


@lru_cache(maxsize=1)
def _default_vector_store() -> VectorStore:
    """Process-wide in-memory vector store; swap with Qdrant in prod."""
    return InMemoryVectorStore()


def get_embedder() -> Embedder:
    return _default_embedder()


def get_vector_store() -> VectorStore:
    return _default_vector_store()


def get_memory_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    embedder: Annotated[Embedder, Depends(get_embedder)],
    store: Annotated[VectorStore, Depends(get_vector_store)],
) -> MemoryService:
    return MemoryService(session=db, embedder=embedder, vector_store=store)


# --------------------------------------------------------------------- #
# LLM router + Orchestrator                                              #
# --------------------------------------------------------------------- #


@lru_cache(maxsize=1)
def _default_llm_router() -> LLMRouter:
    """Default router: only the local Echo adapter is wired by default.

    Production deployments override `get_llm_router` with a configured
    multi-backend router (Ollama + cloud). Tests override it via FastAPI
    dependency injection.
    """
    return LLMRouter([EchoAdapter()])


def get_llm_router() -> LLMRouter:
    return _default_llm_router()


def get_orchestrator(
    memory: Annotated[MemoryService, Depends(get_memory_service)],
    llm_router: Annotated[LLMRouter, Depends(get_llm_router)],
) -> Orchestrator:
    """Build a per-request orchestrator wiring memory retrieval + LLM."""
    graph = (
        StateGraph()
        .add("memory", MemorySearchTool(service=memory))
        .add("llm", LLMTool(router=llm_router))
    )
    return Orchestrator(graph)


# --------------------------------------------------------------------- #
# Authentication                                                         #
# --------------------------------------------------------------------- #


async def require_access_token(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    keys: Annotated[JwtKeys, Depends(get_jwt_keys)],
) -> tk.AccessTokenClaims:
    """Validate the `Authorization: Bearer <jwt>` header and return claims."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        claims = tk.decode_access_token(credentials.credentials, keys.public_pem)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    request.state.user_id = claims.subject
    request.state.role = claims.role
    return claims


def require_role(minimum: Role):
    """FastAPI dependency factory enforcing a minimum role."""

    async def _check(
        claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    ) -> tk.AccessTokenClaims:
        if not role_satisfies(Role(claims.role), minimum):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"role '{minimum.value}' or higher required",
            )
        return claims

    return _check


def require_permission(permission: Permission):
    """FastAPI dependency factory enforcing one specific permission."""
    from jarvis_server.identity.enums import ROLE_PERMISSIONS

    async def _check(
        claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    ) -> tk.AccessTokenClaims:
        permissions = ROLE_PERMISSIONS[Role(claims.role)]
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"missing permission '{permission.value}'",
            )
        return claims

    return _check


__all__ = [
    "get_db",
    "get_embedder",
    "get_identity_config",
    "get_identity_service",
    "get_jwt_keys",
    "get_llm_router",
    "get_memory_service",
    "get_orchestrator",
    "get_vector_store",
    "require_access_token",
    "require_permission",
    "require_role",
]
