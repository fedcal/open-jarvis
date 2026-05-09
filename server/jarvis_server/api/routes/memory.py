"""HTTP routes for the memory layer (`/api/v1/memory/*`)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from jarvis_server.api.deps import (
    get_memory_service,
    require_access_token,
    require_permission,
)
from jarvis_server.identity import tokens as tk
from jarvis_server.identity.enums import Permission
from jarvis_server.memory.schemas import (
    MemoryItemPublic,
    MemoryRecordRequest,
    MemorySearchRequest,
    MemorySearchResponse,
)
from jarvis_server.memory.service import MemoryNotFound, MemoryService

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.post(
    "/record",
    response_model=MemoryItemPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.MEMORY_WRITE))],
)
async def record(
    payload: MemoryRecordRequest,
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> MemoryItemPublic:
    return await service.record(user_id=UUID(claims.subject), payload=payload)


@router.post(
    "/search",
    response_model=MemorySearchResponse,
    dependencies=[Depends(require_permission(Permission.MEMORY_READ))],
)
async def search(
    payload: MemorySearchRequest,
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> MemorySearchResponse:
    hits = await service.search(user_id=UUID(claims.subject), payload=payload)
    return MemorySearchResponse(hits=hits)


@router.get(
    "/list",
    response_model=list[MemoryItemPublic],
    dependencies=[Depends(require_permission(Permission.MEMORY_READ))],
)
async def list_recent(
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    service: Annotated[MemoryService, Depends(get_memory_service)],
    limit: int = 50,
    kind: str | None = None,
) -> list[MemoryItemPublic]:
    return await service.list_recent(
        user_id=UUID(claims.subject),
        limit=max(1, min(limit, 200)),
        kind=kind,
    )


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.MEMORY_WRITE))],
)
async def forget(
    memory_id: UUID,
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> None:
    try:
        await service.forget(user_id=UUID(claims.subject), memory_id=memory_id)
    except MemoryNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="memory not found",
        ) from exc


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(Permission.MEMORY_WRITE))],
)
async def forget_all(
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> dict[str, int]:
    count = await service.forget_all(user_id=UUID(claims.subject))
    return {"deleted": count}


__all__ = ["router"]
