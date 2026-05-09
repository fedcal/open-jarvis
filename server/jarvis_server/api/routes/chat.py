"""Chat endpoints — REST streaming (SSE) + WebSocket.

Phase 1.5: the orchestrator drives the conversation through the LLM
router and the user's memory partition. The HTTP layer only renders
events.

Authentication: REST requires a Bearer access token. WebSocket accepts
an `Authorization` header (browsers can use the `Sec-WebSocket-Protocol`
fallback `bearer.<jwt>` per RFC 6455).
"""

from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from jarvis_server.api.deps import (
    get_jwt_keys,
    get_orchestrator,
    require_access_token,
)
from jarvis_server.domain.chat import (
    ChatResponseSummary,
    ChatTurn,
    Modality,
    StreamEvent,
    StreamEventType,
)
from jarvis_server.identity import tokens as tk
from jarvis_server.identity.service import JwtKeys
from jarvis_server.llm.adapter import ChatMessage, Role
from jarvis_server.orchestration.graph import (
    Orchestrator,
    OrchestratorEvent,
    OrchestratorState,
)
from jarvis_server.orchestration.tools import LLMTool

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _format_sse(event: StreamEvent) -> bytes:
    payload = event.model_dump_json(exclude_none=True)
    return f"event: {event.type.value}\ndata: {payload}\n\n".encode()


def _to_messages(turn: ChatTurn) -> list[ChatMessage]:
    """Convert the turn into LLM-compatible messages."""
    return [ChatMessage(role=Role.USER, content=turn.message)]


def _state(turn: ChatTurn) -> OrchestratorState:
    return OrchestratorState(
        user_id=turn.user_id,
        messages=_to_messages(turn),
        metadata={"modality": turn.modality.value, "language": turn.language},
    )


async def _stream_orchestrator(
    orch: Orchestrator,
    turn: ChatTurn,
) -> AsyncIterator[StreamEvent]:
    """Translate `OrchestratorEvent`s → SSE-friendly `StreamEvent`s."""
    sequence = 0
    yield StreamEvent(
        type=StreamEventType.START,
        turn_id=turn.turn_id,
        sequence=sequence,
        metadata={"modality": turn.modality.value, "language": turn.language},
    )

    # Pull the LLM tool out of the graph for streaming
    llm_tool = next(
        (n for _name, n in orch.graph.nodes if isinstance(n, LLMTool)), None,
    )

    state = _state(turn)
    async for ev in orch.stream(
        state, stream_node=llm_tool.stream if llm_tool else None,
    ):
        sequence += 1
        yield _orchestrator_to_stream_event(ev, turn, sequence)

    sequence += 1
    yield StreamEvent(
        type=StreamEventType.END,
        turn_id=turn.turn_id,
        sequence=sequence,
        metadata={"status": "ok"},
    )


def _orchestrator_to_stream_event(
    ev: OrchestratorEvent,
    turn: ChatTurn,
    sequence: int,
) -> StreamEvent:
    if ev.type == "memory.retrieved":
        return StreamEvent(
            type=StreamEventType.SOURCES,
            turn_id=turn.turn_id,
            sequence=sequence,
            metadata={"count": len(ev.payload.get("items") or [])},
        )
    if ev.type == "llm.delta":
        return StreamEvent(
            type=StreamEventType.CHUNK,
            turn_id=turn.turn_id,
            sequence=sequence,
            content=ev.payload.get("delta", ""),
        )
    if ev.type == "llm.final":
        backend = ev.payload.get("backend") or ""
        model = ev.payload.get("model") or ""
        meta: dict[str, str | int | float | bool] = {
            "phase": "final",
        }
        if backend:
            meta["backend"] = backend
        if model:
            meta["model"] = model
        return StreamEvent(
            type=StreamEventType.SOURCES,
            turn_id=turn.turn_id,
            sequence=sequence,
            metadata=meta,
        )
    return StreamEvent(
        type=StreamEventType.ERROR,
        turn_id=turn.turn_id,
        sequence=sequence,
        metadata={"original_type": ev.type},
    )


# --------------------------------------------------------------------------- #
# REST endpoint                                                                #
# --------------------------------------------------------------------------- #


@router.post(
    "",
    summary="Submit a chat turn (text or voice-transcribed) and stream the response",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "SSE stream of `StreamEvent` records",
            "content": {"text/event-stream": {}},
        },
    },
)
async def chat_stream(
    turn: ChatTurn,
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    orch: Annotated[Orchestrator, Depends(get_orchestrator)],
) -> StreamingResponse:
    if str(turn.user_id) != claims.subject:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id does not match access token subject",
        )

    async def event_source() -> AsyncIterator[bytes]:
        async for event in _stream_orchestrator(orch, turn):
            yield _format_sse(event)

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --------------------------------------------------------------------------- #
# WebSocket endpoint                                                           #
# --------------------------------------------------------------------------- #


def _extract_ws_token(websocket: WebSocket) -> str | None:
    auth = websocket.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1]
    proto = websocket.headers.get("sec-websocket-protocol")
    if proto:
        for part in proto.split(","):
            part = part.strip()
            if part.startswith("bearer."):
                return part.removeprefix("bearer.")
    return None


@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    keys: Annotated[JwtKeys, Depends(get_jwt_keys)],
    orch: Annotated[Orchestrator, Depends(get_orchestrator)],
) -> None:
    """Bidirectional chat over WebSocket (auth via Bearer token)."""
    token = _extract_ws_token(websocket)
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        claims = tk.decode_access_token(token, keys.public_pem)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                turn = ChatTurn.model_validate_json(raw)
            except ValidationError as exc:
                await websocket.send_text(exc.json())
                continue

            if str(turn.user_id) != claims.subject:
                await websocket.send_text(
                    json.dumps({"error": "user_id mismatch"}),
                )
                continue

            started = time.perf_counter()
            async for event in _stream_orchestrator(orch, turn):
                await websocket.send_text(event.model_dump_json(exclude_none=True))

            summary = ChatResponseSummary(
                turn_id=turn.turn_id,
                status="ok",
                latency_ms=int((time.perf_counter() - started) * 1000),
                provider="orchestrator",
                model="",
            )
            await websocket.send_text(summary.model_dump_json())
    except WebSocketDisconnect:
        return


def _modality_marker(turn: ChatTurn) -> str:
    """Diagnostic helper kept for backwards compatibility."""
    return "voice" if turn.modality is Modality.VOICE else "text"


__all__ = ["router"]
