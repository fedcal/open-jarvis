"""Service-level tests for MemoryService."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis_server.memory.orm import MemoryItem
from jarvis_server.memory.schemas import MemoryRecordRequest, MemorySearchRequest
from jarvis_server.memory.service import MemoryNotFound, MemoryService


class TestRecord:
    async def test_creates_row_and_vector(
        self,
        service: MemoryService,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        out = await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="My favourite colour is blue."),
        )
        assert out.user_id == user_id
        assert out.kind == "note"

        row = await session.scalar(
            select(MemoryItem).where(MemoryItem.id == out.id),
        )
        assert row is not None
        assert row.vector_id

    async def test_metadata_round_trip(
        self,
        service: MemoryService,
        user_id: UUID,
    ) -> None:
        out = await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(
                content="x",
                kind="preference",
                metadata={"importance": 0.9, "topic": "music"},
            ),
        )
        assert out.metadata == {"importance": 0.9, "topic": "music"}


class TestSearch:
    async def test_returns_recorded_items(
        self,
        service: MemoryService,
        user_id: UUID,
    ) -> None:
        await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="My dog is named Bruno."),
        )
        await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="I drive a red Tesla."),
        )
        hits = await service.search(
            user_id=user_id,
            payload=MemorySearchRequest(query="My dog is named Bruno.", top_k=3),
        )
        assert len(hits) >= 1
        assert any("Bruno" in h.item.content for h in hits)

    async def test_kind_filter_excludes_others(
        self,
        service: MemoryService,
        user_id: UUID,
    ) -> None:
        await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="loves pizza", kind="preference"),
        )
        await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="meeting at 5pm", kind="event"),
        )
        hits = await service.search(
            user_id=user_id,
            payload=MemorySearchRequest(query="pizza", top_k=5, kind="event"),
        )
        assert all(h.item.kind == "event" for h in hits)

    async def test_isolation_between_users(
        self,
        service: MemoryService,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        from jarvis_server.identity.orm import User
        other = User(
            id=uuid4(),
            email=f"o-{uuid4().hex[:8]}@x.com",
            display_name="Other",
        )
        session.add(other)
        await session.flush()
        await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="my private secret"),
        )
        hits = await service.search(
            user_id=other.id,
            payload=MemorySearchRequest(query="my private secret"),
        )
        assert hits == []


class TestForget:
    async def test_removes_row_and_vector(
        self,
        service: MemoryService,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        out = await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="ephemeral"),
        )
        await service.forget(user_id=user_id, memory_id=out.id)
        assert await session.scalar(
            select(MemoryItem).where(MemoryItem.id == out.id),
        ) is None

    async def test_unknown_id_raises(
        self,
        service: MemoryService,
        user_id: UUID,
    ) -> None:
        with pytest.raises(MemoryNotFound):
            await service.forget(user_id=user_id, memory_id=uuid4())

    async def test_other_user_cannot_forget(
        self,
        service: MemoryService,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        from jarvis_server.identity.orm import User
        attacker = User(
            id=uuid4(),
            email=f"a-{uuid4().hex[:8]}@x.com",
            display_name="Mallory",
        )
        session.add(attacker)
        await session.flush()
        out = await service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="confidential"),
        )
        with pytest.raises(MemoryNotFound):
            await service.forget(user_id=attacker.id, memory_id=out.id)


class TestForgetAll:
    async def test_clears_all_user_memories(
        self,
        service: MemoryService,
        session: AsyncSession,
        user_id: UUID,
    ) -> None:
        for i in range(3):
            await service.record(
                user_id=user_id,
                payload=MemoryRecordRequest(content=f"item {i}"),
            )
        deleted = await service.forget_all(user_id=user_id)
        assert deleted == 3
        rows = (
            await session.scalars(
                select(MemoryItem).where(MemoryItem.user_id == user_id),
            )
        ).all()
        assert rows == []


class TestListRecent:
    async def test_orders_newest_first(
        self,
        service: MemoryService,
        user_id: UUID,
    ) -> None:
        a = await service.record(
            user_id=user_id, payload=MemoryRecordRequest(content="first"),
        )
        b = await service.record(
            user_id=user_id, payload=MemoryRecordRequest(content="second"),
        )
        items = await service.list_recent(user_id=user_id)
        ids = [i.id for i in items]
        assert ids.index(b.id) < ids.index(a.id)
