#!/usr/bin/env python3
"""Human-readable summary of SAGE's operational log.

Usage:
    python scripts/summarize_metrics.py          # all time
    python scripts/summarize_metrics.py 7         # last N days
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta


def main() -> int:
    path = os.path.join(os.path.dirname(__file__), "..", "logs", "operational_log.jsonl")
    if not os.path.exists(path):
        print("No log file found yet.")
        print("Run SAGE first — every interaction is logged automatically.")
        print(f"(expected at: {os.path.normpath(path)})")
        return 0

    days = None
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"Ignoring unknown argument {sys.argv[1]!r} (use a number for days)")
    cutoff = datetime.now() - timedelta(days=days) if days else None

    interactions = []
    ratings = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") == "interaction":
                interactions.append(entry)
            elif entry.get("type") == "rating":
                ratings.append(entry)

    if cutoff:
        interactions = [e for e in interactions if _parse_ts(e) >= cutoff]
        ratings = [e for e in ratings if _parse_ts(e) >= cutoff]

    total = len(interactions)
    print(f"SAGE metrics ({'last %d days' % days if days else 'all time'})")
    print("=" * 44)

    if total == 0:
        print("No interactions in this period.")
        return 0

    # ── Volume ──────────────────────────────────────────────────────
    blocked = sum(1 for e in interactions if e.get("blocked"))
    stt_corrected = sum(1 for e in interactions if e.get("stt_corrected"))
    memory_hits = sum(1 for e in interactions if e.get("memory_hits"))
    gov = Counter(e.get("governance_path", "?") for e in interactions)
    caps = Counter(e.get("capability", "?") for e in interactions)

    print(f"Interactions:      {total}")
    print(f"Governance blocks: {blocked}")
    print(f"STT auto-corrects: {stt_corrected}")
    print(f"Memory hits:       {memory_hits}")

    print()
    print("Governance paths:")
    for k, v in gov.most_common():
        print(f"  {k:<22} {v}")
    print("Capabilities:")
    for k, v in caps.most_common():
        print(f"  {k:<22} {v}")

    # ── Latency ─────────────────────────────────────────────────────
    def _avg(field):
        vals = [e[field] for e in interactions if e.get(field)]
        return sum(vals) / len(vals) if vals else 0.0

    stt = _avg("stt_ms")
    run = _avg("runtime_ms")
    tts = _avg("tts_ms")
    tot = _avg("total_ms")
    print()
    print("Average latency:")
    print(f"  STT (listening):  {stt/1000:6.1f}s")
    print(f"  Think (brain):    {run/1000:6.1f}s")
    print(f"  Speak (voice):    {tts/1000:6.1f}s")
    print(f"  Total:            {tot/1000:6.1f}s")

    # ── Ratings ─────────────────────────────────────────────────────
    print()
    rated = [r for r in ratings if r.get("rating") in (1, 2, 3)]
    good = sum(1 for r in rated if r["rating"] == 3)
    okay = sum(1 for r in rated if r["rating"] == 2)
    bad = sum(1 for r in rated if r["rating"] == 1)

    print("Ratings:")
    print(f"  Good (3):  {good}")
    print(f"  Okay (2):  {okay}")
    print(f"  Bad  (1):  {bad}")
    if rated:
        pct = bad / len(rated) * 100
        print(f"  Bad rate:  {pct:.0f}%  ({len(rated)} rated)")

    if bad:
        print()
        print("Bad interactions by category:")
        cat = Counter(r.get("category", "?") for r in rated if r["rating"] == 1)
        for k, v in cat.most_common():
            print(f"  {k:<12} {v}")
        print()
        print("Latest incident notes:")
        for r in [r for r in rated if r["rating"] == 1][-5:]:
            note = r.get("note", "")
            if note:
                print(f"  - {_safe(note[:100])}")

    print()
    print("Log file: logs/operational_log.jsonl (append-only, one JSON line per event)")
    return 0


def _parse_ts(entry) -> datetime:
    raw = entry.get("timestamp", "")
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return datetime.min


def _safe(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


if __name__ == "__main__":
    sys.exit(main())
