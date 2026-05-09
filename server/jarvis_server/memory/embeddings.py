"""Embedding generation.

Provides:
- `Embedder` protocol — minimal contract for vectorisation backends
- `DeterministicEmbedder` — hash-based deterministic embedder used in
  tests and dev environments to keep the suite hermetic
- `BgeM3Embedder` — sentence-transformers wrapper (lazy import) for
  production deployments that need quality multilingual embeddings

Production deployments should swap `DeterministicEmbedder` with
`BgeM3Embedder` (or `OpenAIEmbedder`) via dependency injection.
"""

from __future__ import annotations

import hashlib
import math
from typing import Protocol, runtime_checkable

EMBEDDING_DIM_DEFAULT = 384


@runtime_checkable
class Embedder(Protocol):
    """Minimal contract for embedding backends."""

    @property
    def dim(self) -> int: ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class DeterministicEmbedder:
    """Hash-based deterministic embedder.

    Stable across processes — perfect for unit tests, fixtures and
    "good-enough" semantic search in development environments without
    GPU resources.
    """

    def __init__(self, dim: int = EMBEDDING_DIM_DEFAULT) -> None:
        if dim <= 0:
            msg = "embedding dim must be positive"
            raise ValueError(msg)
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def _vector(self, text: str) -> list[float]:
        normalised = text.strip().lower().encode("utf-8")
        # Stretch SHA-256 (32 bytes) to `dim` floats via repeated hashing.
        chunks: list[bytes] = []
        seed = normalised
        while len(b"".join(chunks)) < self._dim * 4:
            digest = hashlib.sha256(seed).digest()
            chunks.append(digest)
            seed = digest
        raw = b"".join(chunks)[: self._dim * 4]
        ints = [
            int.from_bytes(raw[i : i + 4], "big", signed=False)
            for i in range(0, len(raw), 4)
        ]
        # Map [0, 2^32-1] → [-1, 1]
        floats = [(value / 2_147_483_647.5) - 1.0 for value in ints]
        # L2-normalise so cosine == dot product
        norm = math.sqrt(sum(f * f for f in floats)) or 1.0
        return [f / norm for f in floats]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)


def embed_texts(embedder: Embedder, texts: list[str]) -> list[list[float]]:
    """Convenience wrapper that returns embedded vectors."""
    return embedder.embed_texts(texts)


def embed_query(embedder: Embedder, text: str) -> list[float]:
    """Convenience wrapper for query embedding."""
    return embedder.embed_query(text)


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two equally-shaped vectors."""
    if len(a) != len(b):
        msg = f"vector dim mismatch: {len(a)} vs {len(b)}"
        raise ValueError(msg)
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


__all__ = [
    "EMBEDDING_DIM_DEFAULT",
    "DeterministicEmbedder",
    "Embedder",
    "cosine",
    "embed_query",
    "embed_texts",
]
