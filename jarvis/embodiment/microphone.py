import threading
import time
from typing import Optional

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000


def record_toggle(
    sample_rate: int = SAMPLE_RATE,
    device: Optional[int] = None,
    max_seconds: float = 120.0,
) -> np.ndarray:
    recording: list[np.ndarray] = []
    stop_event = threading.Event()

    def wait_for_enter() -> None:
        try:
            input()
        except EOFError:
            pass
        finally:
            stop_event.set()

    waiter = threading.Thread(target=wait_for_enter, daemon=True)
    waiter.start()

    stream = sd.InputStream(
        samplerate=sample_rate,
        device=device,
        channels=1,
        dtype="float32",
        callback=lambda indata, frames, time_info, status: recording.append(indata.copy()),
    )
    stream.start()
    print(f"Recording... Press ENTER to stop (auto-stops after {max_seconds:.0f}s).")

    deadline = time.time() + max_seconds
    while not stop_event.is_set() and time.time() < deadline:
        sd.sleep(100)

    stream.stop()
    stream.close()
    stop_event.set()

    if not recording:
        return np.zeros(0, dtype=np.float32)
    audio = np.concatenate(recording).ravel()
    duration = len(audio) / sample_rate
    print(f"Recorded {duration:.1f}s")
    return audio
