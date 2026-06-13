from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import sounddevice as sd


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
