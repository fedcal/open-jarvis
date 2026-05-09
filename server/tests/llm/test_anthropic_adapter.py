"""Mocked HTTP tests for AnthropicAdapter."""

from __future__ import annotations

import httpx
import pytest
import respx

from jarvis_server.llm.adapter import ChatMessage, Role
from jarvis_server.llm.adapters.anthropic import AnthropicAdapter


class TestAnthropicAdapter:
    def test_construction_requires_api_key(self) -> None:
        with pytest.raises(ValueError):
            AnthropicAdapter(api_key="")

    @respx.mock
    async def test_chat_concatenates_text_blocks(self) -> None:
        respx.post("https://api.anthropic.com/v1/messages").mock(
            return_value=httpx.Response(
                200,
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "content": [
                        {"type": "text", "text": "Ciao "},
                        {"type": "text", "text": "Federico"},
                    ],
                    "usage": {"input_tokens": 9, "output_tokens": 4},
                },
            ),
        )
        adapter = AnthropicAdapter(api_key="sk-ant-fake")
        out = await adapter.chat(
            [
                ChatMessage(role=Role.SYSTEM, content="be polite"),
                ChatMessage(role=Role.USER, content="hi"),
            ],
        )
        assert out.content == "Ciao Federico"
        assert out.backend == "anthropic"
        assert out.prompt_tokens == 9

    @respx.mock
    async def test_stream_emits_message_stop(self) -> None:
        body = (
            'data: {"type":"content_block_delta","delta":{"text":"Ho"}}\n'
            'data: {"type":"content_block_delta","delta":{"text":"la"}}\n'
            'data: {"type":"message_stop"}\n'
        )
        respx.post("https://api.anthropic.com/v1/messages").mock(
            return_value=httpx.Response(
                200,
                content=body,
                headers={"Content-Type": "text/event-stream"},
            ),
        )
        adapter = AnthropicAdapter(api_key="sk-ant-fake")
        chunks = []
        async for c in adapter.stream(
            [ChatMessage(role=Role.USER, content="hi")],
        ):
            chunks.append(c)
        assert chunks[-1].finished is True
        assert "".join(c.delta for c in chunks) == "Hola"
