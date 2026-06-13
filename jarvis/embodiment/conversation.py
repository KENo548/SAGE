from typing import Optional

import numpy as np

from jarvis.capabilities import CapabilityLog
from jarvis.core.reasoning_loop import ReasoningLoop


class VoiceConversation:
    def __init__(self, loop: ReasoningLoop, stt_engine, tts_engine) -> None:
        self._loop = loop
        self.stt = stt_engine
        self.tts = tts_engine
        self._capability_log = CapabilityLog()

    def run_one(self, audio: np.ndarray) -> str:
        text = self.stt.transcribe(audio)
        if not text:
            return ""
        return self._process(text, speak=True)

    def run_one_text(self, text: str) -> str:
        if not text.strip():
            return ""
        return self._process(text, speak=False)

    def _process(self, text: str, speak: bool = True) -> str:
        print(f"\nYou: {text}")
        result = self._loop.run(text)

        if result.blocked:
            print(f"SAGE: {result.response}")
            if speak:
                self.tts.speak(result.response)
            return result.response

        print(f"SAGE: {result.response}")
        if speak:
            self.tts.speak(result.response)

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
