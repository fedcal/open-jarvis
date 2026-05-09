"""LLM router — pluggable adapters with policy-based selection."""

from jarvis_server.llm.adapter import (
    ChatMessage,
    LLMAdapter,
    LLMResponse,
    Role,
    StreamChunk,
)
from jarvis_server.llm.adapters.echo import EchoAdapter
from jarvis_server.llm.policy import (
    BackendPreference,
    LLMRequestPolicy,
)
from jarvis_server.llm.router import LLMRouter, NoBackendAvailable

__all__ = [
    "BackendPreference",
    "ChatMessage",
    "EchoAdapter",
    "LLMAdapter",
    "LLMRequestPolicy",
    "LLMResponse",
    "LLMRouter",
    "NoBackendAvailable",
    "Role",
    "StreamChunk",
]
