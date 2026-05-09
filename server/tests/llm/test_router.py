"""Unit tests for LLMRouter and selection policies."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

import pytest

from jarvis_server.llm.adapter import (
    ChatMessage,
    LLMResponse,
    Role,
    StreamChunk,
)
from jarvis_server.llm.adapters.echo import EchoAdapter
from jarvis_server.llm.policy import BackendPreference, LLMRequestPolicy
from jarvis_server.llm.router import LLMRouter, NoBackendAvailable


@dataclass
class _CloudStub:
    """Trivial cloud-like adapter for selection tests."""

    name: str = "cloud-stub"
    is_local: bool = False
    _model: str = "stub-1"

    @property
    def model(self) -> str:
        return self._model

    async def chat(self, messages: list[ChatMessage]) -> LLMResponse:
        return LLMResponse(content="cloud", model=self._model, backend=self.name)

    async def stream(
        self, messages: list[ChatMessage],
    ) -> AsyncIterator[StreamChunk]:
        yield StreamChunk(delta="c", backend=self.name)
        yield StreamChunk(delta="", finished=True, backend=self.name)


class TestLLMRouterConstruction:
    def test_empty_adapter_list_raises(self) -> None:
        with pytest.raises(ValueError):
            LLMRouter([])

    def test_register_local(self) -> None:
        router = LLMRouter([EchoAdapter()])
        assert "echo" in router.adapters


class TestSelection:
    def _router(self) -> LLMRouter:
        return LLMRouter([EchoAdapter(), _CloudStub()])

    def test_default_prefers_local(self) -> None:
        chosen = self._router().select()
        assert chosen.name == "echo"

    def test_cloud_first(self) -> None:
        chosen = self._router().select(
            LLMRequestPolicy(preference=BackendPreference.CLOUD_FIRST),
        )
        assert chosen.name == "cloud-stub"

    def test_cloud_only_with_local_only_set_raises(self) -> None:
        router = LLMRouter([EchoAdapter()])
        with pytest.raises(NoBackendAvailable):
            router.select(
                LLMRequestPolicy(preference=BackendPreference.CLOUD_ONLY),
            )

    def test_local_only_with_cloud_only_set_raises(self) -> None:
        router = LLMRouter([_CloudStub()])
        with pytest.raises(NoBackendAvailable):
            router.select(
                LLMRequestPolicy(preference=BackendPreference.LOCAL_ONLY),
            )

    def test_backend_hint_overrides(self) -> None:
        router = self._router()
        chosen = router.select(LLMRequestPolicy(backend_hint="cloud-stub"))
        assert chosen.name == "cloud-stub"

    def test_unknown_hint_raises(self) -> None:
        with pytest.raises(NoBackendAvailable):
            self._router().select(LLMRequestPolicy(backend_hint="ghost"))


class TestRouterDispatch:
    async def test_chat_dispatches_to_selected(self) -> None:
        router = LLMRouter([EchoAdapter()])
        out = await router.chat([ChatMessage(role=Role.USER, content="ping")])
        assert out.content == "[echo] ping"

    async def test_stream_dispatches_to_selected(self) -> None:
        router = LLMRouter([EchoAdapter()])
        chunks = []
        async for c in router.stream(
            [ChatMessage(role=Role.USER, content="hi")],
        ):
            chunks.append(c)
        assert chunks[-1].finished is True
