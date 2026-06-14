import json
import os
import time
import uuid
from typing import Optional


class OperationalLogger:
    def __init__(self, path: str = "logs/operational_log.jsonl") -> None:
        self._path = path
        self._conversation_id = str(uuid.uuid4())
        os.makedirs(os.path.dirname(path), exist_ok=True)

    @property
    def conversation_id(self) -> str:
        return self._conversation_id

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
        stt_corrected: bool = False,
        response_words: int = 0,
        memory_hits: int = 0,
        knowledge_hits: int = 0,
        governance_path: str = "",
        conversation_sequence: int = 0,
    ) -> None:
        total_ms = stt_ms + runtime_ms + tts_ms
        entry = {
            "type": "interaction",
            "conversation_id": self._conversation_id,
            "sequence": conversation_sequence,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "input": user_input,
            "response_len": len(response),
            "response_words": response_words,
            "capability": capability,
            "stt_ms": round(stt_ms, 1),
            "runtime_ms": round(runtime_ms, 1),
            "tts_ms": round(tts_ms, 1),
            "total_ms": round(total_ms, 1),
            "blocked": blocked,
            "stt_corrected": stt_corrected,
            "memory_hits": memory_hits,
            "knowledge_hits": knowledge_hits,
            "governance_path": governance_path,
        }
        if note:
            entry["note"] = note
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_rating(
        self,
        *,
        sequence: int,
        rating: int,
        category: str = "",
        note: str = "",
    ) -> None:
        entry = {
            "type": "rating",
            "conversation_id": self._conversation_id,
            "sequence": sequence,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "rating": rating,
        }
        if category:
            entry["category"] = category
        if note:
            entry["note"] = note
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
