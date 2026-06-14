import re
from typing import Optional

SHORTCUT_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Anchored patterns first (more specific)
    (re.compile(r"^(summarize|give me a summary|in short|tl;?dr)\s+", re.IGNORECASE), "summarize"),
    (re.compile(r"^(what do you remember|recall|do you remember)\s+", re.IGNORECASE), "memory_recall"),
    (re.compile(r"^(lookup|search|find|query)\s+", re.IGNORECASE), "knowledge_lookup"),
    (re.compile(r"^what do you know about\s+", re.IGNORECASE), "knowledge_lookup"),
    # Un-anchored patterns (catch compound queries: "Hello, what are my goals?")
    (re.compile(r"(what (are|is)\s+.*goal)", re.IGNORECASE), "goal_review"),
    (re.compile(r"(show|list|review|check|display)\s+.*goals?", re.IGNORECASE), "goal_review"),
    (re.compile(r"^my (current|active)?\s*goals?", re.IGNORECASE), "goal_review"),
]


def match_shortcut(user_input: str) -> Optional[str]:
    for pattern, cap_id in SHORTCUT_PATTERNS:
        if pattern.search(user_input):
            return cap_id
    return None
