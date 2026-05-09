"""Ollama adapter — local inference for privacy-first deployments.

Talks to a local Ollama daemon over HTTP (default `http://127.0.0.1:11434`).
The adapter is **lazy**: no network call happens at construction.

For unit tests prefer `EchoAdapter`. The Ollama backend is exercised
through `respx`-based mocks in integration tests.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from jarvis_server.llm.adapter import (
    ChatMessage,
    LLMResponse,
    StreamChunk,
)


@dataclass
class OllamaAdapter:
    """Chat against a local Ollama HTTP API."""

    base_url: str = "http://127.0.0.1:11434"
    _model: str = "llama3.2:3b"
    timeout: float = 60.0
    name: str = "ollama"
    is_local: bool = True

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "llama3.2:3b",
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.timeout = timeout
        self.name = "ollama"
        self.is_local = True

    @property
    def model(self) -> str:
        return self._model

    def _payload(
        self, messages: list[ChatMessage], *, stream: bool,
    ) -> dict[str, object]:
        return {
            "model": self._model,
            "messages": [
                {"role": str(m.role), "content": m.content} for m in messages
            ],
            "stream": stream,
        }

    async def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=self._payload(messages, stream=False),
            )
            response.raise_for_status()
            body = response.json()
        return LLMResponse(
            content=body.get("message", {}).get("content", ""),
            model=body.get("model", self._model),
            backend=self.name,
            prompt_tokens=body.get("prompt_eval_count", 0),
            completion_tokens=body.get("eval_count", 0),
        )

    async def stream(
        self, messages: list[ChatMessage],
    ) -> AsyncIterator[StreamChunk]:
        async with httpx.AsyncClient(timeout=self.timeout) as client, client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=self._payload(messages, stream=True),
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                import json
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                delta = chunk.get("message", {}).get("content", "")
                finished = bool(chunk.get("done", False))
                yield StreamChunk(
                    delta=delta,
                    finished=finished,
                    model=chunk.get("model", self._model),
                    backend=self.name,
                )


__all__ = ["OllamaAdapter"]
