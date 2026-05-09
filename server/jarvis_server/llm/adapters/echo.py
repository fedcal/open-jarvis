"""Echo adapter — returns a deterministic transformation of the prompt.

Used by tests and offline demos. Keeps the LLM contract honest without
requiring any external dependency.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from jarvis_server.llm.adapter import (
    ChatMessage,
    LLMResponse,
    Role,
    StreamChunk,
)


class EchoAdapter:
    """Deterministic adapter that echoes the last user message."""

    name = "echo"
    is_local = True

    def __init__(self, model: str = "echo-1") -> None:
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    @staticmethod
    def _last_user_text(messages: list[ChatMessage]) -> str:
        for m in reversed(messages):
            if m.role is Role.USER:
                return m.content
        return ""

    async def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        text = self._last_user_text(messages)
        reply = f"[echo] {text}" if text else "[echo] (silence)"
        return LLMResponse(
            content=reply,
            model=self._model,
            backend=self.name,
            prompt_tokens=sum(len(m.content) for m in messages) // 4,
            completion_tokens=len(reply) // 4,
        )

    async def stream(
        self, messages: list[ChatMessage],
    ) -> AsyncIterator[StreamChunk]:
        text = self._last_user_text(messages) or "(silence)"
        prefix = "[echo] "
        for ch in prefix + text:
            yield StreamChunk(delta=ch, model=self._model, backend=self.name)
        yield StreamChunk(delta="", finished=True, model=self._model, backend=self.name)


__all__ = ["EchoAdapter"]
