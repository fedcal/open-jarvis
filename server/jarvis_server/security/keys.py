"""ES256 key-pair helpers.

In production the keys are loaded from disk (or HashiCorp Vault). In
tests we generate them on-the-fly to keep the suite hermetic.
"""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


@dataclass(frozen=True)
class KeyPair:
    """A PEM-encoded ES256 (P-256) key pair."""

    private_pem: str
    public_pem: str


def generate_es256_keypair() -> KeyPair:
    """Generate a fresh ES256 (NIST P-256) PEM key pair."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return KeyPair(private_pem=private_pem, public_pem=public_pem)


def load_es256_keypair(private_path: str, public_path: str) -> KeyPair:
    """Read an existing PEM pair from disk."""
    with open(private_path, encoding="utf-8") as fp:
        private_pem = fp.read()
    with open(public_path, encoding="utf-8") as fp:
        public_pem = fp.read()
    return KeyPair(private_pem=private_pem, public_pem=public_pem)


__all__ = ["KeyPair", "generate_es256_keypair", "load_es256_keypair"]
