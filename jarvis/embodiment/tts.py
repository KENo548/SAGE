from jarvis.embodiment.tts_backends.base import TTSBackend, clean_for_speech, _split_sentences
from jarvis.embodiment.tts_backends.kokoro import KokoroBackend

DEFAULT_VOICE = "af_heart"

KOKORO_KNOWN_VOICES: list[str] = [
    "af_bella", "af_heart", "af_nicole", "af_sarah", "af_sky",
    "am_adam", "am_fenrir", "am_michael",
    "bf_emma", "bf_isabella",
    "bm_george", "bm_lewis",
]


def create_tts_engine(voice: str = "") -> TTSBackend:
    v = voice or DEFAULT_VOICE
    return KokoroBackend(voice=v)


def list_voices() -> list[str]:
    return list(KOKORO_KNOWN_VOICES)


__all__ = [
    "TTSBackend",
    "KokoroBackend",
    "create_tts_engine",
    "list_voices",
    "clean_for_speech",
    "_split_sentences",
]
