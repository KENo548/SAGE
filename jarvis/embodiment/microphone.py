from typing import Optional
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000


def record_toggle(
    sample_rate: int = SAMPLE_RATE,
    device: Optional[int] = None,
    max_seconds: float = 30.0,
) -> np.ndarray:
    recording: list[np.ndarray] = []
    stream = sd.InputStream(
        samplerate=sample_rate,
        device=device,
        channels=1,
        dtype="float32",
        callback=lambda indata, frames, time_info, status: recording.append(indata.copy()),
    )
    stream.start()
    print("Recording... Press ENTER to stop.")
    input()
    stream.stop()
    stream.close()
    if not recording:
        return np.zeros(0, dtype=np.float32)
    audio = np.concatenate(recording)
    duration = len(audio) / sample_rate
    print(f"Recorded {duration:.1f}s")
    return audio
