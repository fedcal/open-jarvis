"""Unit tests for ES256 JWT issuance, verification and refresh tokens."""

from __future__ import annotations

from datetime import timedelta

import pytest

from jarvis_server.identity import tokens as tk
from jarvis_server.security.keys import generate_es256_keypair


@pytest.fixture(scope="module")
def keys() -> tuple[str, str]:
    pair = generate_es256_keypair()
    return pair.private_pem, pair.public_pem


class TestRefreshToken:
    def test_new_token_has_consistent_hash(self) -> None:
        issued = tk.new_refresh_token()
        assert tk.hash_refresh(issued.raw) == issued.hashed

    def test_new_tokens_have_distinct_jti_and_family(self) -> None:
        a = tk.new_refresh_token()
        b = tk.new_refresh_token()
        assert a.jti != b.jti
        assert a.family_id != b.family_id

    def test_rotate_keeps_family_changes_jti(self) -> None:
        a = tk.new_refresh_token()
        b = tk.rotate_refresh(family_id=a.family_id)
        assert a.family_id == b.family_id
        assert a.jti != b.jti
        assert a.raw != b.raw


class TestAccessToken:
    def test_round_trip_decodes_subject(self, keys: tuple[str, str]) -> None:
        priv, pub = keys
        issued = tk.new_refresh_token()
        token, _exp = tk.issue_access_token(
            user_id="11111111-1111-1111-1111-111111111111",
            role="member",
            jti=issued.jti,
            family_id=issued.family_id,
            private_key_pem=priv,
        )
        claims = tk.decode_access_token(token, pub)
        assert claims.subject == "11111111-1111-1111-1111-111111111111"
        assert claims.role == "member"
        assert claims.jti == issued.jti

    def test_token_signed_with_other_key_is_rejected(self) -> None:
        priv1 = generate_es256_keypair().private_pem
        pub2 = generate_es256_keypair().public_pem
        issued = tk.new_refresh_token()
        token, _ = tk.issue_access_token(
            user_id="abc",
            role="member",
            jti=issued.jti,
            family_id=issued.family_id,
            private_key_pem=priv1,
        )
        with pytest.raises(ValueError):
            tk.decode_access_token(token, pub2)

    def test_expired_token_is_rejected(self, keys: tuple[str, str]) -> None:
        priv, pub = keys
        issued = tk.new_refresh_token()
        token, _ = tk.issue_access_token(
            user_id="abc",
            role="member",
            jti=issued.jti,
            family_id=issued.family_id,
            private_key_pem=priv,
            ttl=timedelta(seconds=-1),
        )
        with pytest.raises(ValueError):
            tk.decode_access_token(token, pub)
