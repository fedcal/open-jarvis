"""Routing policy types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BackendPreference(StrEnum):
    """How the router weighs available backends for a request.

    `LOCAL_FIRST` is the default: a local backend (Ollama, MLX, etc.) is
    preferred whenever it can serve the request. Cloud backends are only
    used when local ones are unavailable or when the policy is overridden.
    """

    LOCAL_ONLY = "local_only"
    LOCAL_FIRST = "local_first"
    CLOUD_FIRST = "cloud_first"
    CLOUD_ONLY = "cloud_only"


@dataclass(frozen=True)
class LLMRequestPolicy:
    """Per-request policy carried by the orchestrator + chat layer."""

    preference: BackendPreference = BackendPreference.LOCAL_FIRST
    require_streaming: bool = False
    max_tokens: int | None = None
    backend_hint: str | None = None  # e.g. "anthropic" — overrides preference


__all__ = ["BackendPreference", "LLMRequestPolicy"]
