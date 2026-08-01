import os
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from jarvis.embodiment.pronunciation import PronunciationProcessor
from jarvis.embodiment.tts_backends.base import TTSBackend, clean_for_speech

KOKORO_MODEL_DIR = "data/kokoro"
MODEL_FILE = "kokoro-v1.0.onnx"
VOICES_FILE = "voices-v1.0.bin"
DEFAULT_VOICE = "af_heart"
PRONUNCIATION_FILE = os.path.join("data", "pronunciations", "pronunciations.yaml")


@dataclass
class VoiceBlend:
    voice_a: str
    voice_b: str
    weight_a: float = 0.5

    @property
    def blend_id(self) -> str:
        pct = int(self.weight_a * 100)
        return f"blend_{self.voice_a}_{pct}pct_{self.voice_b}_{100-pct}pct"


class KokoroBackend(TTSBackend):
    sample_rate = 24000

    def __init__(
        self,
        voice: str = DEFAULT_VOICE,
        model_dir: str = KOKORO_MODEL_DIR,
        blend: Optional[VoiceBlend] = None,
        pronunciation_file: Optional[str] = PRONUNCIATION_FILE,
    ) -> None:
        self._voice_name = voice
        self._blend = blend
        self._kokoro = None
        self._model_dir = model_dir
        self._pronunciation = None
        t0 = time.time()
        self._kokoro = self._load_kokoro()
        print(f"Kokoro loaded in {time.time() - t0:.1f}s")
        self._pronunciation = self._load_pronunciation(pronunciation_file)

    def _load_kokoro(self):
        try:
            from kokoro_onnx import Kokoro
        except ImportError:
            raise ImportError("kokoro-onnx not installed. Run: pip install -U kokoro-onnx")
        model_path = os.path.join(self._model_dir, MODEL_FILE)
        voices_path = os.path.join(self._model_dir, VOICES_FILE)
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Kokoro model not found at {model_path}. "
                f"Run: python scripts/download_kokoro.py"
            )
        return Kokoro(model_path, voices_path)

    def _load_pronunciation(self, pronunciation_file: Optional[str]) -> Optional[PronunciationProcessor]:
        if not pronunciation_file or not os.path.exists(pronunciation_file):
            return None
        try:
            proc = PronunciationProcessor.from_yaml(
                pronunciation_file, tokenizer=self._kokoro.tokenizer
            )
        except Exception as exc:  # noqa: BLE001 - never break TTS on a bad dictionary
            print(f"  [pronunciation] failed to load {pronunciation_file}: {exc}")
            return None
        if proc.skipped:
            for note in proc.skipped:
                print(f"  [pronunciation] skipped entry: {note}")
        print(
            f"  [pronunciation] {len(proc.spoken)} spoken + "
            f"{len(proc.phonemes)} phoneme entries"
        )
        return proc

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        text = clean_for_speech(text)
        if not text:
            return np.zeros(0, dtype=np.float32), self.sample_rate
        lang = self._resolve_lang()

        if self._pronunciation is not None:
            try:
                _, text = self._pronunciation.apply_spoken(text)
                phonemes = self._pronunciation.to_phonemes(text, lang=lang)
                if phonemes:
                    found = self._pronunciation.entries_with_phonemes(text)
                    if found:
                        print(f"  [pronunciation] applied to: {', '.join(found)}")
                    return self._kokoro.create(
                        phonemes,
                        voice=self._resolve_voice(),
                        speed=1.0,
                        lang=lang,
                        is_phonemes=True,
                    )
            except Exception as exc:  # noqa: BLE001 - fall back to plain text
                print(f"  [pronunciation] phoneme path failed ({exc}); using plain text")

        return self._kokoro.create(
            text,
            voice=self._resolve_voice(),
            speed=1.0,
            lang=lang,
        )

    def _resolve_voice(self) -> str:
        if self._blend:
            return self._blend.blend_id
        return self._voice_name

    def _resolve_lang(self) -> str:
        v = self._voice_name
        if v.startswith("af_") or v.startswith("am_"):
            return "en-us"
        if v.startswith("bf_") or v.startswith("bm_"):
            return "en-gb"
        return "en-us"
