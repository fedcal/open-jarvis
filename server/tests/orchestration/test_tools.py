"""Tests for orchestrator tools (memory + LLM nodes)."""

from __future__ import annotations

from uuid import UUID

from jarvis_server.llm.adapter import ChatMessage, Role
from jarvis_server.llm.router import LLMRouter
from jarvis_server.memory.schemas import MemoryRecordRequest
from jarvis_server.memory.service import MemoryService
from jarvis_server.orchestration.graph import (
    Orchestrator,
    OrchestratorState,
    StateGraph,
)
from jarvis_server.orchestration.tools import (
    LLMTool,
    MemorySearchTool,
    MemoryWriteTool,
)


class TestMemorySearchTool:
    async def test_no_user_message_is_noop(
        self,
        memory_service: MemoryService,
        user_id: UUID,
    ) -> None:
        tool = MemorySearchTool(service=memory_service)
        s = OrchestratorState(user_id=user_id, messages=[])
        out = await tool(s)
        assert out.retrieved_memories == []

    async def test_injects_memory_into_messages(
        self,
        memory_service: MemoryService,
        user_id: UUID,
    ) -> None:
        await memory_service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="My favourite team is Roma"),
        )
        tool = MemorySearchTool(service=memory_service, top_k=3)
        state = OrchestratorState(
            user_id=user_id,
            messages=[ChatMessage(role=Role.USER, content="My favourite team is Roma")],
        )
        out = await tool(state)
        assert any("Roma" in m.content for m in out.messages if m.role is Role.SYSTEM)
        assert out.retrieved_memories


class TestLLMTool:
    async def test_chat_appends_assistant_message(
        self, llm_router: LLMRouter, user_id: UUID,
    ) -> None:
        tool = LLMTool(router=llm_router)
        state = OrchestratorState(
            user_id=user_id,
            messages=[ChatMessage(role=Role.USER, content="ping")],
        )
        out = await tool(state)
        assert out.final_response == "[echo] ping"
        assert out.messages[-1].role is Role.ASSISTANT

    async def test_does_not_duplicate_system_prompt(
        self, llm_router: LLMRouter, user_id: UUID,
    ) -> None:
        tool = LLMTool(router=llm_router)
        state = OrchestratorState(
            user_id=user_id,
            messages=[
                ChatMessage(role=Role.SYSTEM, content="custom"),
                ChatMessage(role=Role.USER, content="ping"),
            ],
        )
        out = await tool(state)
        system_messages = [m for m in out.messages if m.role is Role.SYSTEM]
        assert len(system_messages) == 1
        assert system_messages[0].content == "custom"

    async def test_stream_fills_deltas_buffer(
        self, llm_router: LLMRouter, user_id: UUID,
    ) -> None:
        tool = LLMTool(router=llm_router)
        state = OrchestratorState(
            user_id=user_id,
            messages=[ChatMessage(role=Role.USER, content="hi")],
        )
        out = await tool.stream(state)
        deltas = out.metadata.get("__deltas__", [])
        assert "".join(deltas) == "[echo] hi"
        assert out.final_response == "[echo] hi"


class TestMemoryWriteTool:
    async def test_skipped_without_flag(
        self, memory_service: MemoryService, user_id: UUID,
    ) -> None:
        tool = MemoryWriteTool(service=memory_service)
        state = OrchestratorState(
            user_id=user_id,
            messages=[ChatMessage(role=Role.USER, content="remember this")],
        )
        out = await tool(state)
        assert "__memory_written__" not in out.metadata

    async def test_persists_when_flagged(
        self, memory_service: MemoryService, user_id: UUID,
    ) -> None:
        tool = MemoryWriteTool(service=memory_service)
        state = OrchestratorState(
            user_id=user_id,
            messages=[ChatMessage(role=Role.USER, content="cat name is Mistik")],
            metadata={"record_user_message": True},
        )
        out = await tool(state)
        assert out.metadata["__memory_written__"] is True
        recent = await memory_service.list_recent(user_id=user_id)
        assert any("Mistik" in r.content for r in recent)


class TestOrchestratorPipeline:
    async def test_end_to_end_with_memory_and_llm(
        self,
        memory_service: MemoryService,
        llm_router: LLMRouter,
        user_id: UUID,
    ) -> None:
        await memory_service.record(
            user_id=user_id,
            payload=MemoryRecordRequest(content="user lives in Milano"),
        )
        graph = (
            StateGraph()
            .add("memory", MemorySearchTool(service=memory_service))
            .add("llm", LLMTool(router=llm_router))
        )
        out = await Orchestrator(graph).run(
            OrchestratorState(
                user_id=user_id,
                messages=[ChatMessage(role=Role.USER, content="user lives in Milano")],
            ),
        )
        assert out.final_response is not None
        assert out.final_backend == "echo"
        assert out.retrieved_memories  # Milano memory was retrieved
