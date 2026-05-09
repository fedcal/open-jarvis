"""Tests for the in-house StateGraph + Orchestrator."""

from __future__ import annotations

from uuid import uuid4

from jarvis_server.llm.adapter import ChatMessage, Role
from jarvis_server.orchestration.graph import (
    Orchestrator,
    OrchestratorState,
    StateGraph,
    system_message,
)


class TestStateGraph:
    async def test_runs_nodes_in_order(self) -> None:
        order: list[str] = []

        async def n1(s: OrchestratorState) -> OrchestratorState:
            order.append("n1")
            s.metadata["after_n1"] = True
            return s

        async def n2(s: OrchestratorState) -> OrchestratorState:
            order.append("n2")
            assert s.metadata["after_n1"]
            return s

        graph = StateGraph().add("n1", n1).add("n2", n2)
        out = await graph.run(OrchestratorState(user_id=uuid4()))
        assert order == ["n1", "n2"]
        assert out.metadata["after_n1"] is True

    async def test_empty_graph_returns_state(self) -> None:
        s = OrchestratorState(user_id=uuid4())
        out = await StateGraph().run(s)
        assert out is s


class TestOrchestratorEvents:
    async def test_emits_final_event(self) -> None:
        async def fill(s: OrchestratorState) -> OrchestratorState:
            s.final_response = "done"
            s.final_backend = "echo"
            s.final_model = "echo-1"
            return s

        graph = StateGraph().add("fill", fill)
        events = []
        async for ev in Orchestrator(graph).stream(
            OrchestratorState(user_id=uuid4()),
        ):
            events.append(ev)
        assert events[-1].type == "llm.final"
        assert events[-1].payload["content"] == "done"
        assert events[-1].payload["backend"] == "echo"

    async def test_emits_memory_event_when_present(self) -> None:
        async def fill(s: OrchestratorState) -> OrchestratorState:
            s.retrieved_memories = ["likes pizza"]
            return s

        graph = StateGraph().add("fill", fill)
        events = []
        async for ev in Orchestrator(graph).stream(
            OrchestratorState(user_id=uuid4()),
        ):
            events.append(ev)
        types = [ev.type for ev in events]
        assert "memory.retrieved" in types

    async def test_stream_node_emits_deltas(self) -> None:
        async def fill_buf(s: OrchestratorState) -> OrchestratorState:
            buf = s.metadata.setdefault("__deltas__", [])
            buf.extend(["He", "llo"])
            s.final_response = "Hello"
            return s

        graph = StateGraph()
        events = []
        async for ev in Orchestrator(graph).stream(
            OrchestratorState(
                user_id=uuid4(),
                messages=[ChatMessage(role=Role.USER, content="hi")],
            ),
            stream_node=fill_buf,
        ):
            events.append(ev)
        deltas = [e.payload["delta"] for e in events if e.type == "llm.delta"]
        assert deltas == ["He", "llo"]
        assert events[-1].type == "llm.final"


def test_system_message_helper() -> None:
    msg = system_message("hi")
    assert msg.role is Role.SYSTEM and msg.content == "hi"
