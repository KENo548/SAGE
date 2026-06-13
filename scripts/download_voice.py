#!/usr/bin/env python3
"""Download voice model files for SAGE TTS.

Usage:
    python scripts/download_voice.py
    python scripts/download_voice.py --voice en_US-amy-low
"""

import os
import sys
import urllib.request

VOICE_DIR = "data/voices"
DEFAULT_VOICE = "en_US-lessac-medium"

VOICE_URLS = {
    "en_US-lessac-medium": {
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
    },
    "en_US-amy-low": {
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json",
    },
}


def download_voice(voice_name: str) -> None:
    if voice_name not in VOICE_URLS:
        print(f"Unknown voice: {voice_name}")
        print(f"Available: {', '.join(VOICE_URLS.keys())}")
        sys.exit(1)

    os.makedirs(VOICE_DIR, exist_ok=True)
    urls = VOICE_URLS[voice_name]

    for label, url in urls.items():
        fname = f"{voice_name}.onnx.json" if label == "json" else f"{voice_name}.onnx"
        dest = os.path.join(VOICE_DIR, fname)
        if os.path.exists(dest):
            print(f"Already exists: {dest}")
            continue
        print(f"Downloading {fname} ({url})...")
        urllib.request.urlretrieve(url, dest)
        mb = os.path.getsize(dest) / 1024 / 1024
        print(f"  Saved: {dest} ({mb:.0f}MB)")


def main():
    voice = DEFAULT_VOICE
    if len(sys.argv) > 2 and sys.argv[1] == "--voice":
        voice = sys.argv[2]
    download_voice(voice)


if __name__ == "__main__":
    main()
