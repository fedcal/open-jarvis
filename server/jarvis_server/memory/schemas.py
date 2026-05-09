"""Pydantic v2 DTOs for the memory layer."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ContentStr = Annotated[
    str,
    StringConstraints(min_length=1, max_length=8000, strip_whitespace=True),
]
KindStr = Annotated[
    str,
    StringConstraints(min_length=1, max_length=32, strip_whitespace=True),
]


class MemoryItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID
    user_id: UUID
    kind: str
    content: str
    summary: str | None = None
    source: str | None = None
    metadata: dict[str, str | int | float | bool] | None = None
    created_at: datetime
    updated_at: datetime


class MemoryRecordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: ContentStr
    kind: KindStr = "note"
    source: str | None = Field(default=None, max_length=128)
    summary: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, str | int | float | bool] | None = None


class MemorySearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: ContentStr
    top_k: int = Field(default=5, ge=1, le=50)
    kind: KindStr | None = None


class MemoryHit(BaseModel):
    model_config = ConfigDict(frozen=True)

    item: MemoryItemPublic
    score: float


class MemorySearchResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    hits: list[MemoryHit]


__all__ = [
    "ContentStr",
    "KindStr",
    "MemoryHit",
    "MemoryItemPublic",
    "MemoryRecordRequest",
    "MemorySearchRequest",
    "MemorySearchResponse",
]
