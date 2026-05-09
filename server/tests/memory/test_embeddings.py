"""Unit tests for the embeddings module."""

from __future__ import annotations

import math

import pytest

from jarvis_server.memory.embeddings import (
    DeterministicEmbedder,
    cosine,
    embed_query,
    embed_texts,
)


class TestDeterministicEmbedder:
    def test_dim_default(self) -> None:
        e = DeterministicEmbedder()
        assert e.dim == 384

    def test_custom_dim(self) -> None:
        e = DeterministicEmbedder(dim=128)
        assert len(e.embed_query("hello")) == 128

    def test_zero_dim_rejected(self) -> None:
        with pytest.raises(ValueError):
            DeterministicEmbedder(dim=0)

    def test_same_text_same_vector(self) -> None:
        e = DeterministicEmbedder(dim=64)
        a = e.embed_query("hello world")
        b = e.embed_query("hello world")
        assert a == b

    def test_case_and_whitespace_insensitive(self) -> None:
        e = DeterministicEmbedder(dim=64)
        a = e.embed_query("Hello World")
        b = e.embed_query("  hello world  ")
        assert a == b

    def test_different_texts_different_vectors(self) -> None:
        e = DeterministicEmbedder(dim=64)
        a = e.embed_query("hello world")
        b = e.embed_query("ciao mondo")
        assert a != b

    def test_l2_normalised(self) -> None:
        e = DeterministicEmbedder(dim=64)
        v = e.embed_query("anything")
        norm = math.sqrt(sum(x * x for x in v))
        assert math.isclose(norm, 1.0, rel_tol=1e-6)


class TestEmbedHelpers:
    def test_embed_texts_returns_n_vectors(self) -> None:
        e = DeterministicEmbedder(dim=32)
        out = embed_texts(e, ["a", "b", "c"])
        assert len(out) == 3
        assert all(len(v) == 32 for v in out)

    def test_embed_query_passthrough(self) -> None:
        e = DeterministicEmbedder(dim=32)
        assert embed_query(e, "x") == e.embed_query("x")


class TestCosine:
    def test_identical_vectors_score_one(self) -> None:
        v = [0.5, 0.5, 0.5, 0.5]
        assert math.isclose(cosine(v, v), 1.0, rel_tol=1e-9)

    def test_orthogonal_vectors_score_zero(self) -> None:
        assert cosine([1, 0], [0, 1]) == 0.0

    def test_dim_mismatch_raises(self) -> None:
        with pytest.raises(ValueError):
            cosine([1, 2], [1, 2, 3])

    def test_zero_vector_returns_zero(self) -> None:
        assert cosine([0, 0, 0], [1, 2, 3]) == 0.0
