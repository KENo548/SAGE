import time
from typing import Optional

import numpy as np

from jarvis.capabilities import CapabilityLog
from jarvis.core.reasoning_loop import ReasoningLoop
from jarvis.embodiment.operational_logger import OperationalLogger


# ── Help banner ────────────────────────────────────────────────────────
_SLASH_HELP = """Slash commands:
  /backend <name>   Switch TTS backend (piper, kokoro)
  /voice <name>     Switch voice for current backend
  /voices           List available voices for current backend
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

    # ── Slash commands ─────────────────────────────────────────────────
    def handle_command(self, cmd: str) -> str:
        parts = cmd.strip().split(maxsplit=1)
        verb = parts[0].lower()

        if verb == "/help":
            return _SLASH_HELP

        if verb == "/backend":
            name = parts[1].strip().lower() if len(parts) > 1 else ""
            return self._switch_backend(name)

        if verb == "/voice":
            name = parts[1].strip() if len(parts) > 1 else ""
            return self._switch_voice(name)

        if verb == "/voices":
            return self._list_voices()

        return f"Unknown command: {verb}. Type /help for available commands."

    def _switch_backend(self, name: str) -> str:
        from jarvis.embodiment.tts import create_tts_backend, list_voices

        if name not in ("piper", "kokoro"):
            return f"Unknown backend: {name}. Choose piper or kokoro."
        self.tts = create_tts_backend(name)
        tag = type(self.tts).__name__.removesuffix("Backend")
        return f"Switched TTS backend to {tag} (voice: {self._current_voice_name()})."

    def _switch_voice(self, name: str) -> str:
        from jarvis.embodiment.tts import create_tts_backend

        if not name:
            return "Usage: /voice <name>. Try /voices to see available options."
        tag = type(self.tts).__name__.removesuffix("Backend").lower()
        self.tts = create_tts_backend(tag, voice=name)
        return f"Switched voice to {name}."

    def _list_voices(self) -> str:
        from jarvis.embodiment.tts import list_voices

        tag = type(self.tts).__name__.removesuffix("Backend").lower()
        voices = list_voices(tag)
        header = f"Available {tag} voices ({len(voices)}):"
        return header + "\n  " + "\n  ".join(voices)

    def _current_voice_name(self) -> str:
        tts = self.tts
        if hasattr(tts, "_voice_name"):
            return tts._voice_name
        if hasattr(tts, "_voice"):
            return getattr(tts, "_voice", "?")
        return "?"

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
                self.tts.speak(result.response)
            return result.response

        tts_ms = 0.0
        if speak:
            t2 = time.perf_counter()
            self.tts.speak(result.response)
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
