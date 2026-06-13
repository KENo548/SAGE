import time
from typing import Optional

import numpy as np
import whisper

MAX_SAMPLES = 60 * 16000


class STTEngine:
    def __init__(self, model_name: str = "tiny") -> None:
        t0 = time.time()
        print(f"Loading whisper-{model_name}...")
        self._model = whisper.load_model(model_name)
        print(f"Whisper loaded in {time.time() - t0:.1f}s")

    def transcribe(self, audio: np.ndarray) -> str:
        if len(audio) == 0:
            return ""
        audio = np.asarray(audio).ravel()
        if len(audio) > MAX_SAMPLES:
            print(f"Audio too long ({len(audio)/16000:.1f}s), trimming to 60s")
            audio = audio[:MAX_SAMPLES]
        result = self._model.transcribe(audio, language="en", fp16=False)
        return result["text"].strip()
