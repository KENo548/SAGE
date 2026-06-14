import time
from typing import Optional

import numpy as np

from jarvis.capabilities import CapabilityLog
from jarvis.core.reasoning_loop import ReasoningLoop
from jarvis.embodiment.operational_logger import OperationalLogger


_SLASH_HELP = """Slash commands:
  /voice <name>     Switch Kokoro voice
  /voices           List available voices
  /help             Show this message
  /quit             Exit the session"""


class VoiceConversation:
    def __init__(self, loop: ReasoningLoop, stt_engine, tts_engine) -> None:
        self._loop = loop
        self.stt = stt_engine
        self.tts = tts_engine
        self._capability_log = CapabilityLog()
        self._logger = OperationalLogger()

    def run_one(self, audio: np.ndarray) -> str:
        t0 = time.perf_counter()
        text = self.stt.transcribe(audio)
        t1 = time.perf_counter()
        if not text:
            return ""
        return self._process(text, speak=True, stt_ms=(t1 - t0) * 1000)

    def run_one_text(self, text: str) -> str:
        if not text.strip():
            return ""
        return self._process(text, speak=False, stt_ms=0.0)

    def handle_command(self, cmd: str) -> str:
        parts = cmd.strip().split(maxsplit=1)
        verb = parts[0].lower()

        if verb == "/help":
            return _SLASH_HELP

        if verb == "/voice":
            name = parts[1].strip() if len(parts) > 1 else ""
            return self._switch_voice(name)

        if verb == "/voices":
            return self._list_voices()

        return f"Unknown command: {verb}. Type /help for available commands."

    def _switch_voice(self, name: str) -> str:
        from jarvis.embodiment.tts import create_tts_engine

        if not name:
            return "Usage: /voice <name>. Try /voices to see available options."
        self.tts = create_tts_engine(voice=name)
        return f"Switched voice to {name}."

    def _list_voices(self) -> str:
        from jarvis.embodiment.tts import list_voices

        voices = list_voices()
        return f"Available Kokoro voices ({len(voices)}):\n  " + "\n  ".join(voices)

    def _process(
        self, text: str, speak: bool = True, stt_ms: float = 0.0
    ) -> str:
        print(f"\nYou: {text}")

        t0 = time.perf_counter()
        result = self._loop.run(text)
        t1 = time.perf_counter()
        runtime_ms = (t1 - t0) * 1000

        if result.blocked:
            print(f"SAGE: {result.response}")
            self._logger.log(
                user_input=text,
                response=result.response,
                capability=result.capability_id or "governance_block",
                stt_ms=stt_ms,
                runtime_ms=runtime_ms,
                tts_ms=0.0,
                blocked=True,
            )
            if speak:
                msg = result.response
                print(f"  [DIAG] repr: {repr(msg)}")
                self.tts.speak(msg)
            return result.response

        tts_ms = 0.0
        if speak:
            msg = result.response
            print(f"  [DIAG] repr: {repr(msg)}")
            t2 = time.perf_counter()
            self.tts.speak(msg)
            t3 = time.perf_counter()
            tts_ms = (t3 - t2) * 1000

        print(f"SAGE: {result.response}")

        cap_id = result.capability_id or "general_reasoning"
        self._logger.log(
            user_input=text,
            response=result.response,
            capability=cap_id,
            stt_ms=stt_ms,
            runtime_ms=runtime_ms,
            tts_ms=tts_ms,
            blocked=False,
        )

        if result.from_shortcut and result.capability_id:
            duration = 0
            if result.trace and "8_capability_execution" in result.trace.steps:
                duration = result.trace.steps["8_capability_execution"]
            self._capability_log.write(
                capability_id=result.capability_id,
                user_input=text,
                success=True,
                duration_ms=duration,
                tier=result.tier,
            )
        return result.response
