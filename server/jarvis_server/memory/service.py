"""Memory service — orchestrates persistence, embedding and vector search.

The service is **user-scoped**: every public method takes a `user_id`
and never returns rows belonging to other users. The HTTP layer is
responsible for resolving the caller from the access token (see
`api/deps.require_access_token`).
"""

from __future__ import annotations

import secrets
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis_server.memory.embeddings import Embedder
from jarvis_server.memory.orm import MemoryItem
from jarvis_server.memory.schemas import (
    MemoryHit,
    MemoryItemPublic,
    MemoryRecordRequest,
    MemorySearchRequest,
)
from jarvis_server.memory.vectorstore import VectorStore


class MemoryError(Exception):
    """Base error for the memory layer."""


class MemoryNotFound(MemoryError):  # noqa: N818 — domain-flavoured
    """The requested memory item does not exist for this user."""


def _new_vector_id() -> str:
    return secrets.token_urlsafe(16)


def _to_public(row: MemoryItem) -> MemoryItemPublic:
    """Convert ORM → DTO, mapping the SQL `metadata` column."""
    return MemoryItemPublic(
        id=row.id,
        user_id=row.user_id,
        kind=row.kind,
        content=row.content,
        summary=row.summary,
        source=row.source,
        metadata=row.extra_metadata,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class MemoryService:
    """Record, search and forget memories for a single user."""

    def __init__(
        self,
        session: AsyncSession,
        embedder: Embedder,
        vector_store: VectorStore,
    ) -> None:
        self._db = session
        self._embedder = embedder
        self._store = vector_store

    async def record(
        self,
        *,
        user_id: UUID,
        payload: MemoryRecordRequest,
    ) -> MemoryItemPublic:
        """Persist a memory + embedding atomically (best-effort 2PC).

        The DB row is created first; if vector indexing fails the row
        is rolled back to keep the two stores consistent.
        """
        vector_id = _new_vector_id()
        row = MemoryItem(
            id=uuid4(),
            user_id=user_id,
            kind=payload.kind,
            content=payload.content,
            summary=payload.summary,
            source=payload.source,
            vector_id=vector_id,
            extra_metadata=payload.metadata,
        )
        self._db.add(row)
        await self._db.flush()

        embedding = self._embedder.embed_query(payload.content)
        try:
            await self._store.upsert(
                user_id=user_id,
                vector_id=vector_id,
                embedding=embedding,
                metadata={
                    "memory_id": str(row.id),
                    "kind": row.kind,
                    "source": row.source or "",
                },
            )
        except Exception:
            await self._db.rollback()
            raise

        return _to_public(row)

    async def search(
        self,
        *,
        user_id: UUID,
        payload: MemorySearchRequest,
    ) -> list[MemoryHit]:
        """Cosine-similarity search inside the user's vector partition."""
        embedding = self._embedder.embed_query(payload.query)
        hits = await self._store.query(
            user_id=user_id, embedding=embedding, top_k=payload.top_k,
        )
        if not hits:
            return []
        ids = [hit.vector_id for hit in hits]
        rows = (
            await self._db.scalars(
                select(MemoryItem).where(
                    MemoryItem.user_id == user_id,
                    MemoryItem.vector_id.in_(ids),
                ),
            )
        ).all()
        by_vid = {row.vector_id: row for row in rows}
        results: list[MemoryHit] = []
        for hit in hits:
            row = by_vid.get(hit.vector_id)
            if row is None:
                continue
            if payload.kind and row.kind != payload.kind:
                continue
            results.append(MemoryHit(item=_to_public(row), score=hit.score))
        return results

    async def list_recent(
        self,
        *,
        user_id: UUID,
        limit: int = 50,
        kind: str | None = None,
    ) -> list[MemoryItemPublic]:
        """Reverse-chronological list (no embedding involved)."""
        stmt = select(MemoryItem).where(MemoryItem.user_id == user_id)
        if kind:
            stmt = stmt.where(MemoryItem.kind == kind)
        stmt = stmt.order_by(MemoryItem.created_at.desc()).limit(limit)
        rows = (await self._db.scalars(stmt)).all()
        return [_to_public(r) for r in rows]

    async def forget(self, *, user_id: UUID, memory_id: UUID) -> None:
        """Delete a memory + its vector. 404 if the item is not the caller's."""
        row = await self._db.scalar(
            select(MemoryItem).where(
                MemoryItem.id == memory_id, MemoryItem.user_id == user_id,
            ),
        )
        if row is None:
            raise MemoryNotFound(memory_id)
        if row.vector_id:
            await self._store.delete(user_id=user_id, vector_id=row.vector_id)
        await self._db.execute(
            delete(MemoryItem).where(
                MemoryItem.id == memory_id, MemoryItem.user_id == user_id,
            ),
        )

    async def forget_all(self, *, user_id: UUID) -> int:
        """Delete every memory belonging to the user. Returns count."""
        rows = (
            await self._db.scalars(
                select(MemoryItem).where(MemoryItem.user_id == user_id),
            )
        ).all()
        await self._store.delete_user(user_id)
        await self._db.execute(
            delete(MemoryItem).where(MemoryItem.user_id == user_id),
        )
        return len(rows)


__all__ = ["MemoryError", "MemoryNotFound", "MemoryService"]
