"""Unit tests for the Argon2id password module."""

from __future__ import annotations

import pytest

from jarvis_server.identity import passwords as pw


class TestHashPassword:
    def test_returns_phc_string(self) -> None:
        h = pw.hash_password("correct horse battery staple")
        assert h.startswith("$argon2id$")

    def test_two_hashes_of_same_password_differ(self) -> None:
        a = pw.hash_password("hunter22-securely")
        b = pw.hash_password("hunter22-securely")
        assert a != b  # salt randomises every hash

    def test_empty_password_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            pw.hash_password("")


class TestVerifyPassword:
    def test_correct_password_returns_true(self) -> None:
        h = pw.hash_password("super-secret-passphrase!")
        assert pw.verify_password("super-secret-passphrase!", h) is True

    def test_wrong_password_returns_false(self) -> None:
        h = pw.hash_password("super-secret-passphrase!")
        assert pw.verify_password("almost-the-same-but-no", h) is False

    def test_none_hash_returns_false(self) -> None:
        assert pw.verify_password("anything", None) is False

    def test_empty_hash_returns_false(self) -> None:
        assert pw.verify_password("anything", "") is False

    def test_corrupted_hash_returns_false_not_raises(self) -> None:
        assert pw.verify_password("x", "not-a-real-hash") is False


class TestNeedsRehash:
    def test_fresh_hash_does_not_need_rehash(self) -> None:
        h = pw.hash_password("anything-12-chars-min")
        assert pw.needs_rehash(h) is False

    def test_invalid_hash_needs_rehash(self) -> None:
        assert pw.needs_rehash("nonsense") is True
