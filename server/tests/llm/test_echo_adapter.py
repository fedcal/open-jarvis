"""Unit tests for EchoAdapter."""

from __future__ import annotations

import pytest

from jarvis_server.llm.adapter import ChatMessage, Role
from jarvis_server.llm.adapters.echo import EchoAdapter


@pytest.fixture
def adapter() -> EchoAdapter:
    return EchoAdapter()


class TestEchoAdapter:
    def test_metadata(self, adapter: EchoAdapter) -> None:
        assert adapter.name == "echo"
        assert adapter.is_local is True
        assert adapter.model == "echo-1"

    async def test_chat_echoes_last_user_message(
        self, adapter: EchoAdapter,
    ) -> None:
        out = await adapter.chat(
            [
                ChatMessage(role=Role.SYSTEM, content="you are helpful"),
                ChatMessage(role=Role.USER, content="hello"),
            ],
        )
        assert out.content == "[echo] hello"
        assert out.backend == "echo"

    async def test_chat_with_no_user_message(self, adapter: EchoAdapter) -> None:
        out = await adapter.chat(
            [ChatMessage(role=Role.SYSTEM, content="primer")],
        )
        assert out.content == "[echo] (silence)"

    async def test_stream_yields_finished(self, adapter: EchoAdapter) -> None:
        chunks = []
        async for c in adapter.stream(
            [ChatMessage(role=Role.USER, content="hi")],
        ):
            chunks.append(c)
        assert chunks[-1].finished is True
        joined = "".join(c.delta for c in chunks)
        assert joined == "[echo] hi"
