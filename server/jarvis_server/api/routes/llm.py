"""HTTP routes for LLM backend introspection (`/api/v1/llm/*`).

Two endpoints:
- `GET /backends`        — list every adapter currently registered in the router
- `GET /ollama/models`   — proxy to the configured Ollama daemon `/api/tags`
"""

from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from jarvis_server.api.deps import get_llm_router, require_access_token
from jarvis_server.config import get_settings
from jarvis_server.config.settings import Settings
from jarvis_server.identity import tokens as tk
from jarvis_server.llm.adapters.ollama import OllamaAdapter
from jarvis_server.llm.router import LLMRouter

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])


class BackendInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    model: str
    is_local: bool


class BackendsResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    backends: list[BackendInfo]
    default: str  # name of the adapter selected by the default policy


class OllamaModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    size: int = 0  # bytes
    parameter_size: str | None = None
    family: str | None = None
    quantization_level: str | None = None
    modified_at: str | None = None


class OllamaModelsResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    base_url: str
    reachable: bool
    models: list[OllamaModel] = []
    error: str | None = None


@router.get(
    "/backends",
    response_model=BackendsResponse,
    summary="List LLM adapters available to the router",
)
async def backends(
    _claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    llm_router: Annotated[LLMRouter, Depends(get_llm_router)],
) -> BackendsResponse:
    items = [
        BackendInfo(name=a.name, model=a.model, is_local=a.is_local)
        for a in llm_router.adapters.values()
    ]
    default = llm_router.select().name
    return BackendsResponse(backends=items, default=default)


def _ollama_base_url(settings: Settings) -> str:
    raw = getattr(settings, "ollama_base_url", None) or "http://127.0.0.1:11434"
    return raw.rstrip("/")


@router.get(
    "/ollama/models",
    response_model=OllamaModelsResponse,
    summary="List models pulled on the local Ollama daemon",
)
async def ollama_models(
    _claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> OllamaModelsResponse:
    base_url = _ollama_base_url(settings)
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            payload = response.json()
    except httpx.RequestError as exc:
        return OllamaModelsResponse(
            base_url=base_url,
            reachable=False,
            error=f"unreachable: {exc.__class__.__name__}",
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ollama returned {exc.response.status_code}",
        ) from exc

    models = [
        OllamaModel(
            name=m.get("name", "?"),
            size=int(m.get("size", 0)),
            parameter_size=(m.get("details") or {}).get("parameter_size"),
            family=(m.get("details") or {}).get("family"),
            quantization_level=(m.get("details") or {}).get("quantization_level"),
            modified_at=m.get("modified_at"),
        )
        for m in payload.get("models", [])
    ]
    return OllamaModelsResponse(base_url=base_url, reachable=True, models=models)


__all__ = ["router"]
