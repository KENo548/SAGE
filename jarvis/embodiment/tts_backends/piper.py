import os
import re
import time

import numpy as np
from piper import PiperVoice

from jarvis.embodiment.tts_backends.base import TTSBackend

VOICE_DIR = "data/voices"
VOICE_NAME = "en_US-amy-low"


def _split_sentences(text: str) -> list[str]:
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in raw if s.strip()]


def clean_for_speech(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^[#*>\-]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[\[\](){}<>]", "", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"---+\n?", "", text)
    text = re.sub(r"\n{2,}", ". ", text)
    return text.strip()


class PiperBackend(TTSBackend):
    sample_rate = 22050

    def __init__(self, voice_name: str = VOICE_NAME, voice_dir: str = VOICE_DIR) -> None:
        onnx_path = os.path.join(voice_dir, f"{voice_name}.onnx")
        if not os.path.exists(onnx_path):
            raise FileNotFoundError(f"Voice model not found: {onnx_path}")
        t0 = time.time()
        print(f"Loading Piper voice ({voice_name})...")
        self._voice = PiperVoice.load(onnx_path)
        print(f"Piper loaded in {time.time() - t0:.1f}s")

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        text = clean_for_speech(text)
        sentences = _split_sentences(text)
        if not sentences:
            return np.array([], dtype=np.int16), self.sample_rate
        chunks: list[np.ndarray] = []
        for sentence in sentences:
            for c in self._voice.synthesize(sentence):
                chunks.append(np.frombuffer(c.audio_int16_bytes, dtype=np.int16))
        if not chunks:
            return np.array([], dtype=np.int16), self.sample_rate
        return np.concatenate(chunks), self.sample_rate
