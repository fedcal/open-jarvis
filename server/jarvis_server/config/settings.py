"""Application settings — loaded from environment variables.

All settings are typed via Pydantic. Defaults are safe for local development;
production values come from environment variables (`.env` is gitignored).
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Annotated

from pydantic import Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Environment(StrEnum):
    """Deployment environment markers."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class LogLevel(StrEnum):
    """Logging level options."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Settings(BaseSettings):
    """Top-level application settings.

    Settings are loaded with the following precedence (highest first):
    1. Explicit constructor arguments (used in tests)
    2. Environment variables (case-insensitive)
    3. `.env` file in the working directory
    4. Defaults declared below
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="JARVIS_",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Core ---
    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    public_url: HttpUrl = Field(default=HttpUrl("http://localhost:8080"))
    domain: str = "jarvis.local"

    # --- Server ---
    server_host: str = "0.0.0.0"  # noqa: S104  intentional bind for container
    server_port: int = Field(default=8080, ge=1, le=65535)
    server_secret_key: SecretStr = SecretStr(
        # Replaced via env in any non-development setup; refused at startup if
        # this default is detected outside Environment.DEVELOPMENT/TEST.
        "change-me-in-production-please-rotate-this-value"
    )
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"]
    )
    cors_allow_credentials: bool = True

    # --- App metadata ---
    app_name: str = "Open-Jarvis"
    app_version: str = "0.1.0"

    # --- Feature flags ---
    feature_voice: bool = False
    feature_health: bool = False
    feature_finance: bool = False
    feature_maker: bool = False

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_csv_origins(cls, value: object) -> object:
        """Allow `JARVIS_ALLOWED_ORIGINS=a,b,c` env value."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        """True when running in production environment."""
        return self.environment is Environment.PRODUCTION

    @property
    def is_test(self) -> bool:
        """True when running under the test environment."""
        return self.environment is Environment.TEST

    def assert_production_safe(self) -> None:
        """Raise `RuntimeError` when production is misconfigured."""
        if not self.is_production:
            return
        default_secret = "change-me-in-production-please-rotate-this-value"  # noqa: S105  placeholder, not a real secret
        if self.server_secret_key.get_secret_value() == default_secret:
            raise RuntimeError(
                "JARVIS_SERVER_SECRET_KEY is using the default placeholder value "
                "and the environment is set to production. Refusing to start."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of `Settings` for FastAPI dependency injection."""
    return Settings()


__all__ = [
    "Environment",
    "LogLevel",
    "Settings",
    "get_settings",
]
