"""Vector store adapters.

Production deployments use Qdrant (cloud-friendly, on-disk persistence,
HNSW). For tests + dev we ship `InMemoryVectorStore` — a small cosine
similarity store backed by a Python dict.

Both implementations honour user-scoping: every vector is tagged with
its `user_id`, and queries are always filtered to the caller's scope.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from uuid import UUID

from jarvis_server.memory.embeddings import cosine


@dataclass(frozen=True)
class SearchHit:
    """One result of a similarity query."""

    vector_id: str
    score: float
    metadata: dict[str, str | int | float | bool]


@runtime_checkable
class VectorStore(Protocol):
    """Minimal contract every vector backend must satisfy."""

    async def upsert(
        self,
        *,
        user_id: UUID,
        vector_id: str,
        embedding: list[float],
        metadata: dict[str, str | int | float | bool],
    ) -> None: ...

    async def query(
        self,
        *,
        user_id: UUID,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchHit]: ...

    async def delete(self, *, user_id: UUID, vector_id: str) -> None: ...

    async def delete_user(self, user_id: UUID) -> None: ...


# --------------------------------------------------------------------- #
# In-memory implementation                                               #
# --------------------------------------------------------------------- #


@dataclass
class _Slot:
    embedding: list[float]
    metadata: dict[str, str | int | float | bool]


@dataclass
class InMemoryVectorStore:
    """Simple cosine-similarity backend; great for unit tests."""

    _data: dict[UUID, dict[str, _Slot]] = field(default_factory=dict)

    async def upsert(
        self,
        *,
        user_id: UUID,
        vector_id: str,
        embedding: list[float],
        metadata: dict[str, str | int | float | bool],
    ) -> None:
        self._data.setdefault(user_id, {})[vector_id] = _Slot(
            embedding=list(embedding), metadata=dict(metadata),
        )

    async def query(
        self,
        *,
        user_id: UUID,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchHit]:
        bucket = self._data.get(user_id, {})
        scored = [
            SearchHit(
                vector_id=vid,
                score=cosine(embedding, slot.embedding),
                metadata=dict(slot.metadata),
            )
            for vid, slot in bucket.items()
        ]
        scored.sort(key=lambda hit: hit.score, reverse=True)
        return scored[:top_k]

    async def delete(self, *, user_id: UUID, vector_id: str) -> None:
        if user_id in self._data:
            self._data[user_id].pop(vector_id, None)

    async def delete_user(self, user_id: UUID) -> None:
        self._data.pop(user_id, None)


__all__ = ["InMemoryVectorStore", "SearchHit", "VectorStore"]
