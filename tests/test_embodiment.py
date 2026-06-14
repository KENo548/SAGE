import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np

from jarvis.embodiment.microphone import record_toggle
from jarvis.embodiment.stt import STTEngine
from jarvis.embodiment.tts_backends.base import _split_sentences


def test_split_sentences_basic():
    result = _split_sentences("Hello. This is SAGE. How can I help?")
    assert result == ["Hello.", "This is SAGE.", "How can I help?"]


def test_split_sentences_single():
    result = _split_sentences("Hello world")
    assert result == ["Hello world"]


def test_split_sentences_empty():
    assert _split_sentences("") == []
    assert _split_sentences("   ") == []


def test_split_sentences_with_newlines():
    result = _split_sentences("Line one.\nLine two.\n\nLine three.")
    assert len(result) == 3
    assert "Line one." in result
    assert "Line two." in result
    assert "Line three." in result


def test_stt_engine_empty_audio():
    engine = STTEngine("tiny")
    result = engine.transcribe(np.zeros(0, dtype=np.float32))
    assert result == ""


@patch("jarvis.embodiment.stt.whisper")
def test_stt_engine_transcribe(mock_whisper):
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "  hello world  "}
    mock_whisper.load_model.return_value = mock_model

    engine = STTEngine("tiny")
    audio = np.zeros(16000, dtype=np.float32)
    result = engine.transcribe(audio)
    assert result == "hello world"
    mock_model.transcribe.assert_called_once()


def test_voice_conversation_run_one_text():
    from jarvis.core.reasoning_loop import ReasoningLoop
    from jarvis.embodiment.conversation import VoiceConversation

    mock_loop = MagicMock(spec=ReasoningLoop)
    mock_result = MagicMock()
    mock_result.response = "Test response."
    mock_result.blocked = False
    mock_result.from_shortcut = False
    mock_result.capability_id = ""
    mock_result.tier = 1
    mock_result.trace = MagicMock()
    mock_loop.run.return_value = mock_result

    conv = VoiceConversation(
        loop=mock_loop,
        stt_engine=MagicMock(),
        tts_engine=MagicMock(),
    )
    result = conv.run_one_text("hello")
    assert result == "Test response."
    mock_loop.run.assert_called_once_with("hello")


def test_voice_conversation_run_one_text_blocked():
    from jarvis.core.reasoning_loop import ReasoningLoop
    from jarvis.embodiment.conversation import VoiceConversation

    mock_loop = MagicMock(spec=ReasoningLoop)
    mock_result = MagicMock()
    mock_result.response = "I cannot process this."
    mock_result.blocked = True
    mock_result.tier = 3
    mock_result.capability_id = ""
    mock_loop.run.return_value = mock_result

    conv = VoiceConversation(
        loop=mock_loop,
        stt_engine=MagicMock(),
        tts_engine=MagicMock(),
    )
    result = conv.run_one_text("bad request")
    assert result == "I cannot process this."
    assert "cannot process" in result


def test_voice_conversation_capability_logging():
    from jarvis.core.reasoning_loop import ReasoningLoop
    from jarvis.embodiment.conversation import VoiceConversation

    mock_loop = MagicMock(spec=ReasoningLoop)
    mock_result = MagicMock()
    mock_result.response = "You have one active goal."
    mock_result.blocked = False
    mock_result.from_shortcut = True
    mock_result.capability_id = "goal_review"
    mock_result.tier = 1
    mock_result.trace = MagicMock()
    mock_result.trace.steps = {"8_capability_execution": 5}
    mock_loop.run.return_value = mock_result

    conv = VoiceConversation(
        loop=mock_loop,
        stt_engine=MagicMock(),
        tts_engine=MagicMock(),
    )
    result = conv.run_one_text("what are my goals?")
    assert result == "You have one active goal."


def test_voice_conversation_empty_input():
    from jarvis.embodiment.conversation import VoiceConversation

    conv = VoiceConversation(
        loop=MagicMock(),
        stt_engine=MagicMock(),
        tts_engine=MagicMock(),
    )
    result = conv.run_one_text("")
    assert result == ""
    result = conv.run_one_text("   ")
    assert result == ""


def test_voice_conversation_slash_help():
    from jarvis.embodiment.conversation import VoiceConversation

    conv = VoiceConversation(
        loop=MagicMock(),
        stt_engine=MagicMock(),
        tts_engine=MagicMock(),
    )
    result = conv.handle_command("/help")
    assert "/voice" in result
    assert "/quit" in result


def test_voice_conversation_slash_unknown():
    from jarvis.embodiment.conversation import VoiceConversation

    conv = VoiceConversation(
        loop=MagicMock(),
        stt_engine=MagicMock(),
        tts_engine=MagicMock(),
    )
    result = conv.handle_command("/blah")
    assert "Unknown command" in result
