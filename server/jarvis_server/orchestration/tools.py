"""Reusable graph nodes — memory retrieval, LLM call, persistence."""

from __future__ import annotations

from dataclasses import dataclass

from jarvis_server.llm.adapter import ChatMessage, Role
from jarvis_server.llm.policy import LLMRequestPolicy
from jarvis_server.llm.router import LLMRouter
from jarvis_server.memory.schemas import (
    MemoryRecordRequest,
    MemorySearchRequest,
)
from jarvis_server.memory.service import MemoryService
from jarvis_server.orchestration.graph import OrchestratorState

DEFAULT_SYSTEM_PROMPT = (
    "You are Jarvis, a privacy-first personal assistant. "
    "Use the user's stored memories to personalise replies. "
    "Be concise, accurate, and ask for clarification only when needed."
)


@dataclass
class MemorySearchTool:
    """Graph node that retrieves the top-K most relevant memories."""

    service: MemoryService
    top_k: int = 5

    async def __call__(self, state: OrchestratorState) -> OrchestratorState:
        last_user = next(
            (m for m in reversed(state.messages) if m.role is Role.USER),
            None,
        )
        if last_user is None or not last_user.content.strip():
            return state
        hits = await self.service.search(
            user_id=state.user_id,
            payload=MemorySearchRequest(query=last_user.content, top_k=self.top_k),
        )
        snippets = [hit.item.content for hit in hits]
        if not snippets:
            return state
        state.retrieved_memories = snippets
        # Inject a system message exposing the memory snippets to the LLM
        memory_block = "\n".join(f"- {s}" for s in snippets)
        memory_msg = ChatMessage(
            role=Role.SYSTEM,
            content=(
                "Relevant memories about the user (most-recent context):\n"
                + memory_block
            ),
        )
        state.messages = [memory_msg, *state.messages]
        return state


@dataclass
class LLMTool:
    """Graph node that produces the assistant reply via the LLM router."""

    router: LLMRouter
    policy: LLMRequestPolicy | None = None
    system_prompt: str | None = DEFAULT_SYSTEM_PROMPT

    def _augment(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        if self.system_prompt is None:
            return messages
        if any(m.role is Role.SYSTEM for m in messages):
            return messages
        return [ChatMessage(role=Role.SYSTEM, content=self.system_prompt), *messages]

    async def __call__(self, state: OrchestratorState) -> OrchestratorState:
        messages = self._augment(state.messages)
        response = await self.router.chat(messages, self.policy)
        state.final_response = response.content
        state.final_backend = response.backend
        state.final_model = response.model
        state.messages = [
            *state.messages,
            ChatMessage(role=Role.ASSISTANT, content=response.content),
        ]
        return state

    async def stream(self, state: OrchestratorState) -> OrchestratorState:
        """Stream variant — fills `state.metadata['__deltas__']` and final."""
        messages = self._augment(state.messages)
        deltas: list[str] = state.metadata.setdefault("__deltas__", [])
        adapter = self.router.select(self.policy)
        state.final_backend = adapter.name
        state.final_model = adapter.model
        chunks: list[str] = []
        async for chunk in adapter.stream(messages):
            if chunk.delta:
                chunks.append(chunk.delta)
                deltas.append(chunk.delta)
        full = "".join(chunks)
        state.final_response = full
        state.messages = [
            *state.messages,
            ChatMessage(role=Role.ASSISTANT, content=full),
        ]
        return state


@dataclass
class MemoryWriteTool:
    """Persist a new memory after the assistant reply.

    Heuristic: the latest user message is treated as a candidate fact
    (kind="note") only if `state.metadata['record_user_message']` is
    True. Real auto-memory rules will live in M2.
    """

    service: MemoryService

    async def __call__(self, state: OrchestratorState) -> OrchestratorState:
        if not state.metadata.get("record_user_message"):
            return state
        last_user = next(
            (m for m in reversed(state.messages) if m.role is Role.USER),
            None,
        )
        if last_user is None:
            return state
        await self.service.record(
            user_id=state.user_id,
            payload=MemoryRecordRequest(
                content=last_user.content,
                kind="note",
                source="auto-memory",
            ),
        )
        state.metadata["__memory_written__"] = True
        return state


__all__ = [
    "DEFAULT_SYSTEM_PROMPT",
    "LLMTool",
    "MemorySearchTool",
    "MemoryWriteTool",
]
