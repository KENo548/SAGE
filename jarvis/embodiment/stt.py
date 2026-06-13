import time
from typing import Optional

import numpy as np
import whisper


class STTEngine:
    def __init__(self, model_name: str = "tiny") -> None:
        t0 = time.time()
        print(f"Loading whisper-{model_name}...")
        self._model = whisper.load_model(model_name)
        print(f"Whisper loaded in {time.time() - t0:.1f}s")

    def transcribe(self, audio: np.ndarray) -> str:
        if len(audio) == 0:
            return ""
        result = self._model.transcribe(audio, language="en", fp16=False)
        return result["text"].strip()
