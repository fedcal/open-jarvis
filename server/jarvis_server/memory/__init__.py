"""Memory layer — user-scoped semantic recall (text + structured)."""

from jarvis_server.memory.embeddings import (
    DeterministicEmbedder,
    Embedder,
    embed_query,
    embed_texts,
)
from jarvis_server.memory.service import MemoryService
from jarvis_server.memory.vectorstore import (
    InMemoryVectorStore,
    SearchHit,
    VectorStore,
)

__all__ = [
    "DeterministicEmbedder",
    "Embedder",
    "InMemoryVectorStore",
    "MemoryService",
    "SearchHit",
    "VectorStore",
    "embed_query",
    "embed_texts",
]
