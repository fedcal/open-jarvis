"""OpenAI-compatible adapter.

Speaks the `/v1/chat/completions` protocol — works with OpenAI, Together
AI, Groq, Fireworks and any compatible self-hosted stack (vLLM,
LocalAI, …).
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from jarvis_server.llm.adapter import (
    ChatMessage,
    LLMResponse,
    StreamChunk,
)


@dataclass
class OpenAIAdapter:
    """Adapter for OpenAI-compatible chat completion APIs."""

    api_key: str
    base_url: str = "https://api.openai.com/v1"
    _model: str = "gpt-4o-mini"
    timeout: float = 60.0
    name: str = "openai"
    is_local: bool = False

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 60.0,
    ) -> None:
        if not api_key:
            msg = "OpenAI adapter requires a non-empty API key"
            raise ValueError(msg)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.timeout = timeout
        self.name = "openai"
        self.is_local = False

    @property
    def model(self) -> str:
        return self._model

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

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
            r = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=self._payload(messages, stream=False),
            )
            r.raise_for_status()
            body = r.json()
        choice = body["choices"][0]
        usage = body.get("usage", {})
        return LLMResponse(
            content=choice["message"]["content"],
            model=body.get("model", self._model),
            backend=self.name,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
        )

    async def stream(
        self, messages: list[ChatMessage],
    ) -> AsyncIterator[StreamChunk]:
        async with httpx.AsyncClient(timeout=self.timeout) as client, client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=self._payload(messages, stream=True),
        ) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line.removeprefix("data:").strip()
                if payload == "[DONE]":
                    yield StreamChunk(delta="", finished=True, backend=self.name)
                    return
                try:
                    chunk = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                delta = chunk["choices"][0]["delta"].get("content", "")
                yield StreamChunk(
                    delta=delta,
                    model=chunk.get("model", self._model),
                    backend=self.name,
                )


__all__ = ["OpenAIAdapter"]
