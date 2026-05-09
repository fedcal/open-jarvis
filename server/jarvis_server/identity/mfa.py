"""MFA primitives — TOTP (RFC 6238) + Email OTP + backup codes.

The module exposes pure helpers; orchestration (challenge issuance,
binding to user/session, audit logging) lives in `IdentityService`.
"""

from __future__ import annotations

import base64
import hmac
import io
import secrets
import string
from dataclasses import dataclass
from urllib.parse import quote

import pyotp
import qrcode

from jarvis_server.identity import passwords as pw

ISSUER_LABEL = "Open-Jarvis"
BACKUP_CODE_COUNT = 10
BACKUP_CODE_GROUPS = 4
BACKUP_CODE_GROUP_LEN = 4  # 16 char with dashes


@dataclass(frozen=True)
class TotpEnrol:
    """Material returned to the client during TOTP enrolment."""

    secret_b32: str
    otpauth_uri: str
    qr_png_base64: str


def new_totp_secret() -> str:
    """Generate a fresh Base32 TOTP secret (160 bits)."""
    return pyotp.random_base32()


def totp_otpauth_uri(secret_b32: str, account: str) -> str:
    """Build the otpauth:// URI used by authenticator apps."""
    label = quote(f"{ISSUER_LABEL}:{account}")
    issuer = quote(ISSUER_LABEL)
    return (
        f"otpauth://totp/{label}?secret={secret_b32}&issuer={issuer}"
        "&algorithm=SHA1&digits=6&period=30"
    )


def totp_qr_png_base64(uri: str) -> str:
    """Render the otpauth URI to a PNG QR code, returned as Base64."""
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def begin_totp_enrol(account: str) -> TotpEnrol:
    """Generate a TOTP secret + QR + URI for the given account."""
    secret = new_totp_secret()
    uri = totp_otpauth_uri(secret, account)
    qr = totp_qr_png_base64(uri)
    return TotpEnrol(secret_b32=secret, otpauth_uri=uri, qr_png_base64=qr)


def verify_totp(secret_b32: str, code: str, *, valid_window: int = 1) -> bool:
    """Verify a 6-digit TOTP code with a ±30s window."""
    if not code.isdigit() or len(code) != 6:
        return False
    return pyotp.TOTP(secret_b32).verify(code, valid_window=valid_window)


# --------------------------------------------------------------------- #
# Email OTP                                                              #
# --------------------------------------------------------------------- #


def new_email_otp(length: int = 6) -> str:
    """Generate a numeric OTP suitable for email delivery."""
    if not 4 <= length <= 10:
        msg = "OTP length must be between 4 and 10"
        raise ValueError(msg)
    return "".join(secrets.choice(string.digits) for _ in range(length))


def hash_otp(code: str) -> str:
    """Hash a one-time code for at-rest storage (Argon2id)."""
    return pw.hash_password(code)


def verify_otp(code: str, hashed: str) -> bool:
    """Verify a hashed one-time code (constant-time)."""
    return pw.verify_password(code, hashed)


# --------------------------------------------------------------------- #
# Backup codes                                                           #
# --------------------------------------------------------------------- #


def generate_backup_codes(count: int = BACKUP_CODE_COUNT) -> list[str]:
    """Return *count* human-readable backup codes."""
    alphabet = string.ascii_uppercase + string.digits
    codes: list[str] = []
    for _ in range(count):
        groups = [
            "".join(secrets.choice(alphabet) for _ in range(BACKUP_CODE_GROUP_LEN))
            for _ in range(BACKUP_CODE_GROUPS)
        ]
        codes.append("-".join(groups))
    return codes


def hash_backup_codes(codes: list[str]) -> list[str]:
    """Argon2id-hash each backup code so the DB never holds plaintext."""
    return [pw.hash_password(c) for c in codes]


def verify_backup_code(code: str, hashes: list[str]) -> int | None:
    """Return the index of a matching hash, else None."""
    normalised = code.strip().upper()
    for index, h in enumerate(hashes):
        if pw.verify_password(normalised, h):
            return index
    return None


def constant_time_equals(a: str, b: str) -> bool:
    """Wrapper around `hmac.compare_digest` for string inputs."""
    return hmac.compare_digest(a.encode(), b.encode())


__all__ = [
    "BACKUP_CODE_COUNT",
    "ISSUER_LABEL",
    "TotpEnrol",
    "begin_totp_enrol",
    "constant_time_equals",
    "generate_backup_codes",
    "hash_backup_codes",
    "hash_otp",
    "new_email_otp",
    "new_totp_secret",
    "totp_otpauth_uri",
    "totp_qr_png_base64",
    "verify_backup_code",
    "verify_otp",
    "verify_totp",
]
