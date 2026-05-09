"""Chat endpoints — REST streaming (SSE) + WebSocket.

This module exposes the unified chat surface for Open-Jarvis. Both text
and voice interactions go through these endpoints; the only difference
is the `modality` field on the incoming `ChatTurn`.

Phase 1.x: the `_stub_responder` echoes the user message in chunks. The
real implementation will route through the LLM router and orchestrator
(separate branches `feat/llm-router-providers` and
`feat/orchestrator-langgraph`).
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from jarvis_server.domain.chat import (
    ChatResponseSummary,
    ChatTurn,
    Modality,
    StreamEvent,
    StreamEventType,
)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

_CHUNK_DELAY_S = 0.04  # ~25 chunks/second, smooth perceived streaming


# --------------------------------------------------------------------------- #
# Stub responder — replaced when LLM router lands                              #
# --------------------------------------------------------------------------- #


async def _stub_responder(turn: ChatTurn) -> AsyncIterator[StreamEvent]:
    """Yield a deterministic, modality-aware response.

    Will be replaced by a call to the orchestrator/LLM router. The shape
    of the events MUST stay stable so clients can be implemented now.
    """
    sequence = 0
    yield StreamEvent(
        type=StreamEventType.START,
        turn_id=turn.turn_id,
        sequence=sequence,
        metadata={"modality": turn.modality.value, "language": turn.language},
    )

    prefix = "Hai detto a voce" if turn.modality is Modality.VOICE else "Hai scritto"
    text = f"{prefix}: «{turn.message}». Ti rispondo qui appena il router LLM è pronto."
    for word in text.split():
        sequence += 1
        yield StreamEvent(
            type=StreamEventType.CHUNK,
            turn_id=turn.turn_id,
            sequence=sequence,
            content=word + " ",
        )
        await asyncio.sleep(_CHUNK_DELAY_S)

    sequence += 1
    yield StreamEvent(
        type=StreamEventType.END,
        turn_id=turn.turn_id,
        sequence=sequence,
        metadata={"status": "ok"},
    )


# --------------------------------------------------------------------------- #
# REST endpoint with Server-Sent Events                                        #
# --------------------------------------------------------------------------- #


def _format_sse(event: StreamEvent) -> bytes:
    """Format a `StreamEvent` as a single SSE record."""
    payload = event.model_dump_json(exclude_none=True)
    return f"event: {event.type.value}\ndata: {payload}\n\n".encode()


@router.post(
    "",
    summary="Submit a chat turn (text or voice-transcribed) and stream the response",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "SSE stream of `StreamEvent` records",
            "content": {"text/event-stream": {}},
        }
    },
)
async def chat_stream(turn: ChatTurn) -> StreamingResponse:
    """Streams a chat answer back via Server-Sent Events.

    Clients can use the same endpoint for text chat (web/mobile/CLI) and
    for voice (passing the transcription produced by the voice agent
    with `modality="voice"`).
    """

    async def event_source() -> AsyncIterator[bytes]:
        async for event in _stub_responder(turn):
            yield _format_sse(event)

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --------------------------------------------------------------------------- #
# WebSocket endpoint                                                           #
# --------------------------------------------------------------------------- #


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket) -> None:
    """Bidirectional chat over WebSocket.

    Clients send a JSON-encoded `ChatTurn` per message; the server
    streams back `StreamEvent` JSON records. This keeps a long-lived
    connection useful for typing indicators, interruption (barge-in
    in voice mode) and back-pressure.
    """
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                turn = ChatTurn.model_validate_json(raw)
            except ValidationError as exc:
                await websocket.send_text(exc.json())
                continue

            started = time.perf_counter()
            async for event in _stub_responder(turn):
                await websocket.send_text(event.model_dump_json(exclude_none=True))

            summary = ChatResponseSummary(
                turn_id=turn.turn_id,
                status="ok",
                latency_ms=int((time.perf_counter() - started) * 1000),
                provider="stub",
                model="echo",
            )
            await websocket.send_text(summary.model_dump_json())
    except WebSocketDisconnect:
        return
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        raise


__all__ = ["router"]
