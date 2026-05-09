"""Unit tests for InMemoryVectorStore."""

from __future__ import annotations

from uuid import uuid4

import pytest

from jarvis_server.memory.vectorstore import InMemoryVectorStore


@pytest.fixture
def store() -> InMemoryVectorStore:
    return InMemoryVectorStore()


class TestInMemoryVectorStore:
    async def test_upsert_and_query(self, store: InMemoryVectorStore) -> None:
        u = uuid4()
        await store.upsert(
            user_id=u, vector_id="v1",
            embedding=[1.0, 0.0, 0.0],
            metadata={"k": "hello"},
        )
        hits = await store.query(user_id=u, embedding=[1.0, 0.0, 0.0])
        assert len(hits) == 1
        assert hits[0].vector_id == "v1"
        assert hits[0].score == 1.0

    async def test_top_k_ordering(self, store: InMemoryVectorStore) -> None:
        u = uuid4()
        await store.upsert(user_id=u, vector_id="v1", embedding=[1, 0, 0], metadata={})
        await store.upsert(user_id=u, vector_id="v2", embedding=[0.9, 0.1, 0], metadata={})
        await store.upsert(user_id=u, vector_id="v3", embedding=[0, 1, 0], metadata={})
        hits = await store.query(user_id=u, embedding=[1, 0, 0], top_k=2)
        assert [h.vector_id for h in hits] == ["v1", "v2"]

    async def test_user_partition_is_strict(self, store: InMemoryVectorStore) -> None:
        a, b = uuid4(), uuid4()
        await store.upsert(user_id=a, vector_id="v1", embedding=[1, 0], metadata={})
        hits = await store.query(user_id=b, embedding=[1, 0])
        assert hits == []

    async def test_delete_one(self, store: InMemoryVectorStore) -> None:
        u = uuid4()
        await store.upsert(user_id=u, vector_id="v1", embedding=[1, 0], metadata={})
        await store.delete(user_id=u, vector_id="v1")
        assert await store.query(user_id=u, embedding=[1, 0]) == []

    async def test_delete_user_clears_partition(self, store: InMemoryVectorStore) -> None:
        u = uuid4()
        await store.upsert(user_id=u, vector_id="v1", embedding=[1, 0], metadata={})
        await store.upsert(user_id=u, vector_id="v2", embedding=[0, 1], metadata={})
        await store.delete_user(u)
        assert await store.query(user_id=u, embedding=[1, 0]) == []
