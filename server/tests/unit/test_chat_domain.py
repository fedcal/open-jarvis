"""Unit tests for `jarvis_server.domain.chat` models."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from jarvis_server.domain.chat import (
    ChatTurn,
    Modality,
    StreamEvent,
    StreamEventType,
)


def _ids() -> dict:
    return {"session_id": uuid4(), "device_id": uuid4(), "user_id": uuid4()}


@pytest.mark.unit
class TestModality:
    """Modality is the only field that distinguishes text from voice input."""

    def test_default_is_text(self) -> None:
        turn = ChatTurn(message="hi", **_ids())
        assert turn.modality is Modality.TEXT

    def test_voice_modality_accepted(self) -> None:
        turn = ChatTurn(message="hi", modality=Modality.VOICE, **_ids())
        assert turn.modality is Modality.VOICE

    def test_serialises_as_string(self) -> None:
        assert Modality.TEXT.value == "text"
        assert Modality.VOICE.value == "voice"


@pytest.mark.unit
class TestChatTurnValidation:
    def test_message_required(self) -> None:
        with pytest.raises(ValidationError):
            ChatTurn(**_ids())  # type: ignore[call-arg]

    def test_message_strips_control_chars(self) -> None:
        turn = ChatTurn(message="hello\x00\x01world", **_ids())
        assert "\x00" not in turn.message
        assert "hello" in turn.message and "world" in turn.message

    def test_whitespace_only_message_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ChatTurn(message="   \t\n   ", **_ids())

    def test_message_max_length(self) -> None:
        with pytest.raises(ValidationError):
            ChatTurn(message="a" * 8193, **_ids())

    def test_language_pattern_enforced(self) -> None:
        with pytest.raises(ValidationError):
            ChatTurn(message="hi", language="italian", **_ids())

    def test_language_with_region_accepted(self) -> None:
        turn = ChatTurn(message="hi", language="it-IT", **_ids())
        assert turn.language == "it-IT"

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            ChatTurn(message="hi", secret="x", **_ids())  # type: ignore[call-arg]

    def test_chat_turn_is_frozen(self) -> None:
        turn = ChatTurn(message="hi", **_ids())
        with pytest.raises(ValidationError):
            turn.message = "modified"  # type: ignore[misc]


@pytest.mark.unit
class TestStreamEvent:
    def test_chunk_event_serialisation(self) -> None:
        evt = StreamEvent(
            type=StreamEventType.CHUNK,
            turn_id=uuid4(),
            sequence=3,
            content="ciao ",
        )
        payload = evt.model_dump()
        assert payload["type"] == "chunk"
        assert payload["sequence"] == 3
        assert payload["content"] == "ciao "

    def test_negative_sequence_rejected(self) -> None:
        with pytest.raises(ValidationError):
            StreamEvent(type=StreamEventType.START, turn_id=uuid4(), sequence=-1)
