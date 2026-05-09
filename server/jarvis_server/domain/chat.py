"""Chat domain models.

Open-Jarvis exposes a single conversation regardless of how the user
interacts with it. The same `ChatTurn` represents both:

- a typed message coming from a web/mobile/CLI client
- a transcribed audio utterance coming from the voice agent

Downstream the orchestrator and memory layer treat both modes
identically; the `modality` field is preserved only for telemetry,
audit log and rendering hints (e.g. responding in voice if the input
was voice).
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Modality(StrEnum):
    """Where the message originated.

    `text` — typed input from a chat UI, REST API or CLI.
    `voice` — captured audio that has already been transcribed by the
              voice agent. The orchestrator does not see audio bytes.
    """

    TEXT = "text"
    VOICE = "voice"


class ChatTurn(BaseModel):
    """A single user turn flowing into the system."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    turn_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    device_id: UUID
    user_id: UUID
    modality: Modality = Modality.TEXT
    message: Annotated[str, Field(min_length=1, max_length=8192)]
    language: str = Field(default="it", pattern=r"^[a-z]{2}(-[A-Z]{2})?$")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @field_validator("message")
    @classmethod
    def strip_control_chars(cls, value: str) -> str:
        """Strip null bytes and unprintable control characters."""
        cleaned = "".join(c for c in value if c >= " " or c in "\n\r\t")
        if not cleaned.strip():
            raise ValueError("message is empty after sanitization")
        return cleaned


class StreamEventType(StrEnum):
    """SSE / WebSocket event types emitted while answering."""

    START = "start"
    CHUNK = "chunk"
    SOURCES = "sources"
    TOOL_CALL = "tool_call"
    ERROR = "error"
    END = "end"


class StreamEvent(BaseModel):
    """A single event in the streamed response."""

    model_config = ConfigDict(extra="forbid")

    type: StreamEventType
    turn_id: UUID
    sequence: int = Field(ge=0)
    content: str | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ChatResponseSummary(BaseModel):
    """Summary returned at the end of a streamed turn."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    turn_id: UUID
    status: Literal["ok", "degraded", "error"]
    input_tokens: int = Field(ge=0, default=0)
    output_tokens: int = Field(ge=0, default=0)
    latency_ms: int = Field(ge=0, default=0)
    provider: str = ""
    model: str = ""


__all__ = [
    "ChatResponseSummary",
    "ChatTurn",
    "Modality",
    "StreamEvent",
    "StreamEventType",
]
