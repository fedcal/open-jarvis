"""LLM router — selects an adapter given a policy."""

from __future__ import annotations

from collections.abc import AsyncIterator

from jarvis_server.llm.adapter import (
    ChatMessage,
    LLMAdapter,
    LLMResponse,
    StreamChunk,
)
from jarvis_server.llm.policy import BackendPreference, LLMRequestPolicy


class NoBackendAvailable(Exception):  # noqa: N818 — domain-flavoured
    """No registered adapter satisfies the requested policy."""


class LLMRouter:
    """Pick a backend per request and dispatch chat / stream calls."""

    def __init__(self, adapters: list[LLMAdapter]) -> None:
        if not adapters:
            msg = "LLMRouter requires at least one adapter"
            raise ValueError(msg)
        self._adapters: dict[str, LLMAdapter] = {a.name: a for a in adapters}

    @property
    def adapters(self) -> dict[str, LLMAdapter]:
        return dict(self._adapters)

    def select(self, policy: LLMRequestPolicy | None = None) -> LLMAdapter:
        """Resolve the policy → concrete adapter."""
        policy = policy or LLMRequestPolicy()
        if policy.backend_hint:
            adapter = self._adapters.get(policy.backend_hint)
            if adapter is None:
                msg = f"unknown backend hint '{policy.backend_hint}'"
                raise NoBackendAvailable(msg)
            return adapter

        local = [a for a in self._adapters.values() if a.is_local]
        cloud = [a for a in self._adapters.values() if not a.is_local]
        ordered: list[LLMAdapter]
        match policy.preference:
            case BackendPreference.LOCAL_ONLY:
                ordered = local
            case BackendPreference.CLOUD_ONLY:
                ordered = cloud
            case BackendPreference.LOCAL_FIRST:
                ordered = [*local, *cloud]
            case BackendPreference.CLOUD_FIRST:
                ordered = [*cloud, *local]
        if not ordered:
            msg = f"no adapter satisfies preference {policy.preference}"
            raise NoBackendAvailable(msg)
        return ordered[0]

    async def chat(
        self,
        messages: list[ChatMessage],
        policy: LLMRequestPolicy | None = None,
    ) -> LLMResponse:
        adapter = self.select(policy)
        return await adapter.chat(messages)

    async def stream(
        self,
        messages: list[ChatMessage],
        policy: LLMRequestPolicy | None = None,
    ) -> AsyncIterator[StreamChunk]:
        adapter = self.select(policy)
        async for chunk in adapter.stream(messages):
            yield chunk


__all__ = ["LLMRouter", "NoBackendAvailable"]
