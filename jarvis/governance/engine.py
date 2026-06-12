from typing import Callable

from jarvis.governance.rules import TIER1_PATTERNS, TIER3_PATTERNS, TIER2_PATTERNS
from jarvis.identity.models import Constitution


class GovernanceEngine:
    def __init__(self, constitution: Constitution, llm_classify_fn: Callable[[str], int]):
        self.constitution = constitution
        self.llm_classify_fn = llm_classify_fn

    def classify(self, query: str) -> int:
        q_lower = query.lower()

        for pattern in TIER3_PATTERNS:
            if pattern.search(q_lower):
                return 3

        for pattern in TIER1_PATTERNS:
            if pattern.search(q_lower):
                return 1

        for pattern in TIER2_PATTERNS:
            if pattern.search(q_lower):
                return 2

        return self.llm_classify_fn(query)
