"""Unit tests for the MFA helpers (TOTP, email OTP, backup codes)."""

from __future__ import annotations

import pyotp
import pytest

from jarvis_server.identity import mfa


class TestTotp:
    def test_secret_is_32_chars(self) -> None:
        assert len(mfa.new_totp_secret()) == 32

    def test_otpauth_uri_includes_issuer(self) -> None:
        uri = mfa.totp_otpauth_uri("ABCDEFGHIJKLMNOP", "user@example.com")
        assert uri.startswith("otpauth://totp/")
        assert "issuer=Open-Jarvis" in uri

    def test_qr_png_base64_decodes(self) -> None:
        enrol = mfa.begin_totp_enrol("u@example.com")
        assert enrol.qr_png_base64
        # Should start with PNG signature once decoded
        import base64
        raw = base64.b64decode(enrol.qr_png_base64)
        assert raw.startswith(b"\x89PNG")

    def test_verify_correct_code(self) -> None:
        secret = mfa.new_totp_secret()
        code = pyotp.TOTP(secret).now()
        assert mfa.verify_totp(secret, code) is True

    def test_verify_rejects_non_digit_code(self) -> None:
        secret = mfa.new_totp_secret()
        assert mfa.verify_totp(secret, "ABCDEF") is False

    def test_verify_rejects_wrong_length(self) -> None:
        secret = mfa.new_totp_secret()
        assert mfa.verify_totp(secret, "12345") is False


class TestEmailOtp:
    def test_default_length_is_6_digits(self) -> None:
        otp = mfa.new_email_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    @pytest.mark.parametrize("length", [4, 6, 8, 10])
    def test_custom_length(self, length: int) -> None:
        otp = mfa.new_email_otp(length=length)
        assert len(otp) == length

    @pytest.mark.parametrize("length", [3, 11, 0])
    def test_invalid_length_rejected(self, length: int) -> None:
        with pytest.raises(ValueError):
            mfa.new_email_otp(length=length)

    def test_hash_round_trip(self) -> None:
        otp = mfa.new_email_otp()
        h = mfa.hash_otp(otp)
        assert mfa.verify_otp(otp, h) is True
        assert mfa.verify_otp("000000", h) is False


class TestBackupCodes:
    def test_default_count(self) -> None:
        codes = mfa.generate_backup_codes()
        assert len(codes) == mfa.BACKUP_CODE_COUNT

    def test_codes_are_unique(self) -> None:
        codes = mfa.generate_backup_codes(count=20)
        assert len(set(codes)) == 20

    def test_format_is_4x4_groups(self) -> None:
        for c in mfa.generate_backup_codes(count=3):
            parts = c.split("-")
            assert len(parts) == 4
            assert all(len(p) == 4 for p in parts)

    def test_verify_returns_index(self) -> None:
        codes = mfa.generate_backup_codes(count=3)
        hashes = mfa.hash_backup_codes(codes)
        assert mfa.verify_backup_code(codes[1], hashes) == 1

    def test_verify_rejects_unknown_code(self) -> None:
        codes = mfa.generate_backup_codes(count=2)
        hashes = mfa.hash_backup_codes(codes)
        assert mfa.verify_backup_code("AAAA-AAAA-AAAA-AAAA", hashes) is None
