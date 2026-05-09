"""Password hashing using Argon2id with OWASP-2025 parameters.

The chosen parameters (`time_cost=3`, `memory_cost=128 MiB`,
`parallelism=4`) match the most recent OWASP / IETF guidance for
interactive logins on commodity server hardware.

The `verify_password` helper is constant-time; mismatching is
indistinguishable from non-existent users at the timing-attack level.
"""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHash,
    VerificationError,
    VerifyMismatchError,
)

# OWASP Password Storage Cheat Sheet (May 2025)
_HASHER = PasswordHasher(
    time_cost=3,
    memory_cost=131_072,  # 128 MiB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain: str) -> str:
    """Return an Argon2id hash of *plain* in PHC-string format."""
    if not plain:
        msg = "password must not be empty"
        raise ValueError(msg)
    return _HASHER.hash(plain)


def verify_password(plain: str, hashed: str | None) -> bool:
    """Return True iff *plain* matches *hashed* (constant-time).

    A `None` or empty `hashed` always returns False so we can use the
    same code path for users without a stored password (passkey-only).
    """
    if not hashed:
        return False
    try:
        return _HASHER.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


def needs_rehash(hashed: str) -> bool:
    """True if the hash uses outdated Argon2 parameters."""
    try:
        return _HASHER.check_needs_rehash(hashed)
    except InvalidHash:
        return True


__all__ = ["hash_password", "needs_rehash", "verify_password"]
