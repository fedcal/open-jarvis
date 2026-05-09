"""Common types and the `LLMAdapter` protocol.

Every backend (Ollama, OpenAI, Anthropic, MLX, vLLM, …) implements
this protocol. The router selects one based on policy.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, runtime_checkable


class Role(StrEnum):
    """Chat-message authoring role."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class ChatMessage:
    """One turn of a conversation."""

    role: Role
    content: str
    name: str | None = None  # used by tool calls


@dataclass(frozen=True)
class LLMResponse:
    """Non-streaming LLM reply."""

    content: str
    model: str
    backend: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    extra: dict[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class StreamChunk:
    """One delta yielded during streaming."""

    delta: str
    finished: bool = False
    model: str | None = None
    backend: str | None = None


@runtime_checkable
class LLMAdapter(Protocol):
    """Minimal contract for any chat backend."""

    @property
    def name(self) -> str: ...

    @property
    def is_local(self) -> bool: ...

    @property
    def model(self) -> str: ...

    async def chat(self, messages: list[ChatMessage]) -> LLMResponse: ...

    async def stream(
        self, messages: list[ChatMessage],
    ) -> AsyncIterator[StreamChunk]: ...


__all__ = [
    "ChatMessage",
    "LLMAdapter",
    "LLMResponse",
    "Role",
    "StreamChunk",
]
