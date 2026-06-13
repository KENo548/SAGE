import os
from typing import Optional

import yaml

from jarvis.embodiment.tts_backends.base import TTSBackend
from jarvis.embodiment.tts_backends.piper import PiperBackend, clean_for_speech
from jarvis.embodiment.tts_backends.kokoro import KokoroBackend

CONFIG_PATH = "configs/config.yaml"
DEFAULT_BACKEND = "piper"

KOKORO_KNOWN_VOICES: list[str] = [
    "af_bella", "af_heart", "af_nicole", "af_sarah", "af_sky",
    "am_adam", "am_fenrir", "am_michael",
    "bf_emma", "bf_isabella",
    "bm_george", "bm_lewis",
]


def _load_config_backend() -> str:
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_BACKEND
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f) or {}
    tts_cfg = cfg.get("tts", {}) or {}
    return tts_cfg.get("backend", DEFAULT_BACKEND)


def _load_config_voice() -> str:
    if not os.path.exists(CONFIG_PATH):
        return ""
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f) or {}
    tts_cfg = cfg.get("tts", {}) or {}
    return tts_cfg.get("voice", "")


def create_tts_engine() -> TTSBackend:
    backend_name = _load_config_backend()
    voice_name = _load_config_voice()
    return create_tts_backend(backend_name, voice=voice_name)


def create_tts_backend(backend: str, voice: str = "") -> TTSBackend:
    if backend == "kokoro":
        v = voice or "af_bella"
        return KokoroBackend(voice=v)
    v = voice or "en_US-amy-low"
    return PiperBackend(voice_name=v)


def list_voices(backend: str) -> list[str]:
    if backend == "kokoro":
        return list(KOKORO_KNOWN_VOICES)
    if not os.path.isdir("data/voices"):
        return []
    return sorted(
        f.removesuffix(".onnx")
        for f in os.listdir("data/voices")
        if f.endswith(".onnx")
    )


__all__ = [
    "TTSBackend",
    "PiperBackend",
    "KokoroBackend",
    "create_tts_engine",
    "create_tts_backend",
    "list_voices",
    "clean_for_speech",
]
