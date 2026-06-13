import json
import os
import time
from typing import Optional


class OperationalLogger:
    def __init__(self, path: str = "logs/operational_log.jsonl") -> None:
        self._path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def log(
        self,
        *,
        user_input: str,
        response: str,
        capability: str,
        stt_ms: float = 0.0,
        runtime_ms: float = 0.0,
        tts_ms: float = 0.0,
        blocked: bool = False,
        note: str = "",
    ) -> None:
        total_ms = stt_ms + runtime_ms + tts_ms
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "input": user_input,
            "response_len": len(response),
            "capability": capability,
            "stt_ms": round(stt_ms, 1),
            "runtime_ms": round(runtime_ms, 1),
            "tts_ms": round(tts_ms, 1),
            "total_ms": round(total_ms, 1),
            "blocked": blocked,
        }
        if note:
            entry["note"] = note
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
