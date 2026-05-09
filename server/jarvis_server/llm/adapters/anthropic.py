"""Anthropic Claude adapter (Messages API)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx

from jarvis_server.llm.adapter import (
    ChatMessage,
    LLMResponse,
    Role,
    StreamChunk,
)

DEFAULT_API_VERSION = "2023-06-01"


@dataclass
class AnthropicAdapter:
    """Adapter for the Claude Messages API."""

    api_key: str
    base_url: str = "https://api.anthropic.com/v1"
    _model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 1024
    timeout: float = 60.0
    api_version: str = DEFAULT_API_VERSION
    name: str = "anthropic"
    is_local: bool = False

    def __init__(
        self,
        api_key: str,
        model: str = "claude-haiku-4-5-20251001",
        base_url: str = "https://api.anthropic.com/v1",
        max_tokens: int = 1024,
        timeout: float = 60.0,
        api_version: str = DEFAULT_API_VERSION,
    ) -> None:
        if not api_key:
            msg = "Anthropic adapter requires a non-empty API key"
            raise ValueError(msg)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.api_version = api_version
        self.name = "anthropic"
        self.is_local = False

    @property
    def model(self) -> str:
        return self._model

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json",
        }

    @staticmethod
    def _split_system(messages: list[ChatMessage]) -> tuple[str | None, list[ChatMessage]]:
        system_parts = [m.content for m in messages if m.role is Role.SYSTEM]
        rest = [m for m in messages if m.role is not Role.SYSTEM]
        return ("\n".join(system_parts) or None, rest)

    def _payload(
        self, messages: list[ChatMessage], *, stream: bool,
    ) -> dict[str, object]:
        system, conversation = self._split_system(messages)
        body: dict[str, object] = {
            "model": self._model,
            "max_tokens": self.max_tokens,
            "stream": stream,
            "messages": [
                {"role": str(m.role), "content": m.content} for m in conversation
            ],
        }
        if system:
            body["system"] = system
        return body

    async def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/messages",
                headers=self._headers(),
                json=self._payload(messages, stream=False),
            )
            r.raise_for_status()
            body = r.json()
        text_blocks = [
            blk.get("text", "") for blk in body.get("content", []) if blk.get("type") == "text"
        ]
        usage = body.get("usage", {})
        return LLMResponse(
            content="".join(text_blocks),
            model=body.get("model", self._model),
            backend=self.name,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
        )

    async def stream(
        self, messages: list[ChatMessage],
    ) -> AsyncIterator[StreamChunk]:
        async with httpx.AsyncClient(timeout=self.timeout) as client, client.stream(
            "POST",
            f"{self.base_url}/messages",
            headers=self._headers(),
            json=self._payload(messages, stream=True),
        ) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line.removeprefix("data:").strip()
                try:
                    evt = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                etype = evt.get("type")
                if etype == "content_block_delta":
                    delta = evt.get("delta", {}).get("text", "")
                    yield StreamChunk(delta=delta, backend=self.name)
                elif etype == "message_stop":
                    yield StreamChunk(delta="", finished=True, backend=self.name)
                    return


__all__ = ["AnthropicAdapter"]
