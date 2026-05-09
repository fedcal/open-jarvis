"""Mocked HTTP tests for OllamaAdapter (uses respx to stub the daemon)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from jarvis_server.llm.adapter import ChatMessage, Role
from jarvis_server.llm.adapters.ollama import OllamaAdapter


class TestOllamaChat:
    @respx.mock
    async def test_chat_parses_message_content(self) -> None:
        respx.post("http://127.0.0.1:11434/api/chat").mock(
            return_value=httpx.Response(
                200,
                json={
                    "model": "llama3.2:3b",
                    "message": {"role": "assistant", "content": "ciao!"},
                    "prompt_eval_count": 7,
                    "eval_count": 5,
                    "done": True,
                },
            ),
        )
        adapter = OllamaAdapter()
        out = await adapter.chat([ChatMessage(role=Role.USER, content="ciao")])
        assert out.content == "ciao!"
        assert out.backend == "ollama"
        assert out.prompt_tokens == 7
        assert out.completion_tokens == 5

    @respx.mock
    async def test_stream_yields_finished_when_done(self) -> None:
        body_lines = [
            json.dumps({"message": {"content": "Hel"}, "done": False}),
            json.dumps({"message": {"content": "lo"}, "done": False}),
            json.dumps({"message": {"content": "!"}, "done": True}),
        ]
        respx.post("http://127.0.0.1:11434/api/chat").mock(
            return_value=httpx.Response(
                200,
                content="\n".join(body_lines),
                headers={"Content-Type": "application/x-ndjson"},
            ),
        )
        adapter = OllamaAdapter()
        chunks = []
        async for c in adapter.stream(
            [ChatMessage(role=Role.USER, content="hi")],
        ):
            chunks.append(c)
        assert chunks[-1].finished is True
        assert "".join(c.delta for c in chunks) == "Hello!"

    @respx.mock
    async def test_5xx_raises(self) -> None:
        respx.post("http://127.0.0.1:11434/api/chat").mock(
            return_value=httpx.Response(503),
        )
        adapter = OllamaAdapter()
        with pytest.raises(httpx.HTTPStatusError):
            await adapter.chat([ChatMessage(role=Role.USER, content="x")])
