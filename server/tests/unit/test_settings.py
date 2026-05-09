"""Unit tests for `jarvis_server.config.settings`."""

from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from jarvis_server.config.settings import Environment, LogLevel, Settings


@pytest.mark.unit
class TestSettingsDefaults:
    """Default values must remain stable for backward compatibility.

    The shared `_isolate_env` fixture pins `JARVIS_ENVIRONMENT=test` to keep
    every test deterministic; these checks therefore explicitly remove that
    override to verify the package-shipped defaults.
    """

    def test_defaults_to_development(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("JARVIS_ENVIRONMENT", raising=False)
        s = Settings()
        assert s.environment is Environment.DEVELOPMENT
        assert s.log_level is LogLevel.INFO
        assert s.app_name == "Open-Jarvis"

    def test_default_port_is_8080(self) -> None:
        s = Settings()
        assert s.server_port == 8080

    def test_default_origins_include_local(self) -> None:
        s = Settings()
        assert "http://localhost:3000" in s.allowed_origins
        assert "http://localhost:8080" in s.allowed_origins

    def test_feature_flags_default_off(self) -> None:
        s = Settings()
        assert s.feature_voice is False
        assert s.feature_health is False
        assert s.feature_finance is False
        assert s.feature_maker is False


@pytest.mark.unit
class TestSettingsEnvLoading:
    """Environment variables override defaults."""

    def test_env_override_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_ENVIRONMENT", "production")
        monkeypatch.setenv("JARVIS_SERVER_SECRET_KEY", "x" * 32)
        s = Settings()
        assert s.is_production is True
        assert s.is_test is False

    def test_env_override_origins_csv(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(
            "JARVIS_ALLOWED_ORIGINS",
            "https://a.example.com,https://b.example.com,",
        )
        s = Settings()
        assert s.allowed_origins == [
            "https://a.example.com",
            "https://b.example.com",
        ]

    def test_invalid_port_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("JARVIS_SERVER_PORT", "70000")
        with pytest.raises(ValidationError):
            Settings()


@pytest.mark.unit
class TestProductionSafety:
    """`assert_production_safe()` enforces critical invariants."""

    def test_default_secret_in_production_raises(self) -> None:
        s = Settings(environment=Environment.PRODUCTION)
        with pytest.raises(RuntimeError, match="default placeholder"):
            s.assert_production_safe()

    def test_rotated_secret_in_production_passes(self) -> None:
        s = Settings(
            environment=Environment.PRODUCTION,
            server_secret_key=SecretStr("a" * 64),
            jwt_private_key_pem=SecretStr(
                "-----BEGIN PRIVATE KEY-----\nfake\n-----END PRIVATE KEY-----\n"
            ),
            jwt_public_key_pem=SecretStr(
                "-----BEGIN PUBLIC KEY-----\nfake\n-----END PUBLIC KEY-----\n"
            ),
        )
        s.assert_production_safe()  # must not raise

    def test_missing_jwt_keys_in_production_raises(self) -> None:
        s = Settings(
            environment=Environment.PRODUCTION,
            server_secret_key=SecretStr("a" * 64),
        )
        with pytest.raises(RuntimeError, match="JWT_PRIVATE_KEY_PEM"):
            s.assert_production_safe()

    def test_no_check_in_development(self) -> None:
        s = Settings(environment=Environment.DEVELOPMENT)
        s.assert_production_safe()  # must not raise

    def test_no_check_in_test(self) -> None:
        s = Settings(environment=Environment.TEST)
        s.assert_production_safe()  # must not raise


@pytest.mark.unit
def test_is_test_helper() -> None:
    s = Settings(environment=Environment.TEST)
    assert s.is_test is True
    assert s.is_production is False
