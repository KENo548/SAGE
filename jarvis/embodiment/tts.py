import os
import re
import time
import queue
import threading
from typing import Optional

import numpy as np
import sounddevice as sd
from piper import PiperVoice

VOICE_DIR = "data/voices"
VOICE_NAME = "en_US-lessac-medium"


def _split_sentences(text: str) -> list[str]:
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in raw if s.strip()]


class TTSEngine:
    def __init__(self, voice_name: str = VOICE_NAME, voice_dir: str = VOICE_DIR) -> None:
        self._voice_dir = voice_dir
        onnx_path = os.path.join(voice_dir, f"{voice_name}.onnx")
        if not os.path.exists(onnx_path):
            raise FileNotFoundError(f"Voice model not found: {onnx_path}")
        t0 = time.time()
        print(f"Loading TTS voice ({voice_name})...")
        self._voice = PiperVoice.load(onnx_path)
        self._sample_rate = 22050
        print(f"TTS loaded in {time.time() - t0:.1f}s")

    def speak(self, text: str, block: bool = True) -> None:
        sentences = _split_sentences(text)
        if not sentences:
            return
        audio_queue: queue.Queue = queue.Queue()
        done_event = threading.Event()

        def play_thread():
            stream = sd.OutputStream(
                samplerate=self._sample_rate,
                channels=1,
                dtype="int16",
            )
            stream.start()
            while True:
                chunk = audio_queue.get()
                if chunk is None:
                    break
                stream.write(chunk)
            stream.stop()
            stream.close()
            done_event.set()

        player = threading.Thread(target=play_thread, daemon=True)
        player.start()

        for sentence in sentences:
            audio_chunks = list(self._voice.synthesize(sentence))
            for c in audio_chunks:
                audio_queue.put(c.audio_int16_bytes)

        audio_queue.put(None)

        if block:
            done_event.wait()

    def speak_async(self, text: str) -> threading.Thread:
        t = threading.Thread(target=self.speak, args=(text, True), daemon=True)
        t.start()
        return t
