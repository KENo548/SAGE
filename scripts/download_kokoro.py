#!/usr/bin/env python3
"""Download Kokoro-82M ONNX model and voice files.

Usage:
    python scripts/download_kokoro.py             # model + voices bin (~300MB)
    python scripts/download_kokoro.py --voices     # also download .pt voicepacks for blending
"""

import argparse
import os

KOKORO_DIR = "data/kokoro"

REQUIRED_FILES: dict[str, str] = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}

VOICE_PACKS: dict[str, str] = {
    "af_bella.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/af_bella.pt",
    "af_sarah.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/af_sarah.pt",
    "af_nicole.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/af_nicole.pt",
    "af_heart.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/af_heart.pt",
    "af_sky.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/af_sky.pt",
    "am_michael.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/am_michael.pt",
    "am_fenrir.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/am_fenrir.pt",
    "bf_emma.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/bf_emma.pt",
    "bf_isabella.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/bf_isabella.pt",
    "bm_george.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/bm_george.pt",
    "bm_lewis.pt": "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/bm_lewis.pt",
}


def download(url: str, dest: str) -> None:
    import requests
    print(f"Downloading {os.path.basename(dest)}...")
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    written = 0
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            written += len(chunk)
            if total:
                pct = int(written / total * 100)
                print(f"  {pct}% ({written // 1024 // 1024}MB / {total // 1024 // 1024}MB)", end="\r")
    print(f"\nSaved {dest} ({written // 1024 // 1024}MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Kokoro-82M TTS model and voices")
    parser.add_argument("--voices", action="store_true", help="Also download individual .pt voicepacks for blending")
    args = parser.parse_args()

    os.makedirs(KOKORO_DIR, exist_ok=True)

    for fname, url in REQUIRED_FILES.items():
        dest = os.path.join(KOKORO_DIR, fname)
        if os.path.exists(dest):
            print(f"Skipping {fname} (already exists)")
            continue
        download(url, dest)

    if args.voices:
        for fname, url in VOICE_PACKS.items():
            dest = os.path.join(KOKORO_DIR, fname)
            if os.path.exists(dest):
                print(f"Skipping {fname} (already exists)")
                continue
            download(url, dest)

    print(f"\nDone! {len([f for f in os.listdir(KOKORO_DIR) if os.path.isfile(os.path.join(KOKORO_DIR, f))])} files in {KOKORO_DIR}/")
    print("Run: pip install -U kokoro-onnx  (if not already installed)")


if __name__ == "__main__":
    main()
