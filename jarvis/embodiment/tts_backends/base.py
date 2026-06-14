import re
from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import sounddevice as sd


def clean_for_speech(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^[#*>\-]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[\[\](){}<>]", "", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"---+\n?", "", text)
    text = re.sub(r"\n{2,}", ". ", text)
    return text.strip()


def _split_sentences(text: str) -> list[str]:
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in raw if s.strip()]


class TTSBackend(ABC):
    sample_rate: int = 22050

    @abstractmethod
    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        ...

    def speak(self, text: str, block: bool = True) -> None:
        import time
        samples, rate = self.synthesize(text)
        if len(samples) == 0:
            return
        import wave
        import numpy as np
        samples_int16 = (samples * 32767).astype(np.int16)
        with wave.open("debug.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(samples_int16.tobytes())
        t_s = time.perf_counter()
        sd.play(samples, samplerate=rate)
        if block:
            sd.wait()
        dur = len(samples) / rate
        print(f"  [{type(self).__name__.removesuffix('Backend')}] {dur:.1f}s audio — play {int((time.perf_counter()-t_s)*1000)}ms")

    def speak_async(self, text: str) -> Optional:
        import threading
        t = threading.Thread(target=self.speak, args=(text, True), daemon=True)
        t.start()
        return t
