"""Mocked HTTP tests for OpenAIAdapter."""

from __future__ import annotations

import httpx
import pytest
import respx

from jarvis_server.llm.adapter import ChatMessage, Role
from jarvis_server.llm.adapters.openai import OpenAIAdapter


class TestOpenAIAdapter:
    def test_construction_requires_api_key(self) -> None:
        with pytest.raises(ValueError):
            OpenAIAdapter(api_key="")

    @respx.mock
    async def test_chat_round_trip(self) -> None:
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "x",
                    "model": "gpt-4o-mini",
                    "choices": [
                        {"message": {"role": "assistant", "content": "ok"}, "index": 0},
                    ],
                    "usage": {"prompt_tokens": 4, "completion_tokens": 2},
                },
            ),
        )
        adapter = OpenAIAdapter(api_key="sk-fake")
        out = await adapter.chat([ChatMessage(role=Role.USER, content="hi")])
        assert out.content == "ok"
        assert out.backend == "openai"
        assert out.prompt_tokens == 4

    @respx.mock
    async def test_stream_handles_done_marker(self) -> None:
        body = (
            'data: {"model":"gpt-4o-mini","choices":[{"delta":{"content":"He"}}]}\n'
            'data: {"model":"gpt-4o-mini","choices":[{"delta":{"content":"llo"}}]}\n'
            "data: [DONE]\n"
        )
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                content=body,
                headers={"Content-Type": "text/event-stream"},
            ),
        )
        adapter = OpenAIAdapter(api_key="sk-fake")
        chunks = []
        async for c in adapter.stream(
            [ChatMessage(role=Role.USER, content="hi")],
        ):
            chunks.append(c)
        assert chunks[-1].finished is True
        assert "".join(c.delta for c in chunks) == "Hello"
