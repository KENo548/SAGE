import os
from datetime import datetime, timezone

LOG_DIR = "data/capability_logs"


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


class CapabilityLog:
    def __init__(self) -> None:
        _ensure_log_dir()
        self._log_file = os.path.join(LOG_DIR, "execution_log.txt")

    def write(
        self,
        capability_id: str,
        user_input: str,
        success: bool,
        duration_ms: int,
        tier: int,
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        flag = "+" if success else "-"
        tier_str = f"t{max(0, tier)}"
        line = f"{timestamp} | {flag} | {tier_str} | {capability_id} | {duration_ms}ms | {user_input[:120]}\n"
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def read_recent(self, n: int = 10) -> list[str]:
        if not os.path.exists(self._log_file):
            return []
        with open(self._log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [l.strip() for l in lines[-n:]]
