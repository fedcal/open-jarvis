"""A minimal async state graph for conversation orchestration.

Why not LangGraph? LangGraph is excellent but pulls in a heavy
dependency tree. Open-Jarvis ships its own minimal graph so the core
remains light; users that want LangGraph can subclass `Orchestrator`
and replace `_run_graph()` without touching the HTTP layer.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Literal
from uuid import UUID

from jarvis_server.llm.adapter import ChatMessage, Role

# --------------------------------------------------------------------- #
# State + event types                                                    #
# --------------------------------------------------------------------- #


@dataclass
class OrchestratorState:
    """Mutable state passed between graph nodes.

    Although the dataclass is mutable for ergonomic use inside nodes,
    the orchestrator returns a *fresh* state to callers.
    """

    user_id: UUID
    messages: list[ChatMessage] = field(default_factory=list)
    retrieved_memories: list[str] = field(default_factory=list)
    final_response: str | None = None
    final_backend: str | None = None
    final_model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrchestratorEvent:
    """One event emitted by the orchestrator stream."""

    type: Literal[
        "memory.retrieved",
        "llm.delta",
        "llm.final",
        "memory.written",
        "error",
    ]
    payload: dict[str, Any] = field(default_factory=dict)


Node = Callable[[OrchestratorState], Awaitable[OrchestratorState]]


# --------------------------------------------------------------------- #
# StateGraph                                                             #
# --------------------------------------------------------------------- #


@dataclass
class StateGraph:
    """A linear pipeline of async nodes (with optional branches).

    Branches are not implemented for the MVP — we stick to a deterministic
    sequence. Real branching can be added by composing graphs.
    """

    nodes: list[tuple[str, Node]] = field(default_factory=list)

    def add(self, name: str, node: Node) -> StateGraph:
        self.nodes.append((name, node))
        return self

    async def run(self, state: OrchestratorState) -> OrchestratorState:
        current = state
        for _name, node in self.nodes:
            current = await node(current)
        return current


# --------------------------------------------------------------------- #
# Orchestrator                                                           #
# --------------------------------------------------------------------- #


class Orchestrator:
    """High-level entry point used by the chat HTTP layer."""

    def __init__(self, graph: StateGraph) -> None:
        self._graph = graph

    @property
    def graph(self) -> StateGraph:
        return self._graph

    async def run(self, state: OrchestratorState) -> OrchestratorState:
        """Execute the graph end-to-end (non-streaming)."""
        return await self._graph.run(state)

    async def stream(
        self,
        state: OrchestratorState,
        *,
        stream_node: Node | None = None,
    ) -> AsyncIterator[OrchestratorEvent]:
        """Run nodes sequentially, yielding events as they arrive.

        The orchestrator emits structured events (`OrchestratorEvent`) so
        the chat layer can translate them into SSE / WebSocket frames.

        If a `stream_node` is provided it is invoked **last**: it is
        expected to mutate `state.final_response` while emitting deltas
        through `state.metadata["__deltas__"]` (see `LLMTool.stream`).
        """
        current = state
        for _name, node in self._graph.nodes:
            current = await node(current)
            if current.retrieved_memories and not current.metadata.get("__memory_announced__"):
                yield OrchestratorEvent(
                    type="memory.retrieved",
                    payload={"items": list(current.retrieved_memories)},
                )
                current.metadata["__memory_announced__"] = True
        if stream_node is not None:
            buffer: list[str] = []
            current.metadata["__deltas__"] = buffer
            current = await stream_node(current)
            for delta in buffer:
                yield OrchestratorEvent(type="llm.delta", payload={"delta": delta})
        yield OrchestratorEvent(
            type="llm.final",
            payload={
                "content": current.final_response or "",
                "backend": current.final_backend,
                "model": current.final_model,
            },
        )


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def system_message(text: str) -> ChatMessage:
    """Build a system message — small helper exported for tests."""
    return ChatMessage(role=Role.SYSTEM, content=text)


__all__ = [
    "Node",
    "Orchestrator",
    "OrchestratorEvent",
    "OrchestratorState",
    "StateGraph",
    "system_message",
]
