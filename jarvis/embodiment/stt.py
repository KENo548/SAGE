import time
from typing import Optional

import numpy as np
import whisper

MAX_SAMPLES = 60 * 16000

# Common Whisper mis-transcriptions of "SAGE" — correction applied only to first 2 words
_WAKE_CORRECTIONS: dict[str, str] = {
    "sage": "SAGE",
    "stage": "SAGE",
    "say": "SAGE",
    "sade": "SAGE",
    "sate": "SAGE",
    "saye": "SAGE",
}

# Proper nouns Whisper consistently mangles — applied anywhere
_PROPER_NOUNS: dict[str, str] = {
    "bikoni": "Bocconi",
    "bikone": "Bocconi",
    "ultraviolet": "ultraviolet",
}

_GREETINGS = {"hello", "hi", "hey", "good"}


def _normalize(text: str) -> str:
    """Correct known STT errors while avoiding false positives on mid-utterance words."""
    words = text.split()
    if not words:
        return text

    result: list[str] = []

    for i, w in enumerate(words):
        clean = w.strip(".,!?;:")
        lower = clean.lower()
        punctuation_trail = w[len(clean):] if len(clean) < len(w) else ""

        # 1. Proper noun lookup (any position)
        if lower in _PROPER_NOUNS:
            result.append(_PROPER_NOUNS[lower] + punctuation_trail)
            continue

        # 2. Wake-word correction: first word, or second word if first is a greeting
        if i == 0 or (i == 1 and words[0].strip(".,!?;:").lower() in _GREETINGS):
            if lower in _WAKE_CORRECTIONS:
                result.append(_WAKE_CORRECTIONS[lower] + punctuation_trail)
                continue

        result.append(w)

    return " ".join(result)


class STTEngine:
    def __init__(self, model_name: str = "tiny") -> None:
        t0 = time.time()
        print(f"Loading whisper-{model_name}...")
        self._model = whisper.load_model(model_name)
        self._last_corrected: bool = False
        print(f"Whisper loaded in {time.time() - t0:.1f}s")

    @property
    def last_corrected(self) -> bool:
        return self._last_corrected

    def transcribe(self, audio: np.ndarray) -> str:
        if len(audio) == 0:
            self._last_corrected = False
            return ""
        audio = np.asarray(audio).ravel()
        if len(audio) > MAX_SAMPLES:
            print(f"Audio too long ({len(audio)/16000:.1f}s), trimming to 60s")
            audio = audio[:MAX_SAMPLES]
        result = self._model.transcribe(audio, language="en", fp16=False)
        raw = result["text"].strip()
        normalized = _normalize(raw)
        self._last_corrected = (normalized != raw)
        return normalized
