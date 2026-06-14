from typing import Callable

from jarvis.governance.rules import TIER1_PATTERNS, TIER3_PATTERNS, TIER2_PATTERNS
from jarvis.identity.models import Constitution


class GovernanceEngine:
    def __init__(self, constitution: Constitution, llm_classify_fn: Callable[[str], int]):
        self.constitution = constitution
        self.llm_classify_fn = llm_classify_fn
        self.last_path: str = ""

    def classify(self, query: str) -> int:
        q_lower = query.lower()

        for pattern in TIER3_PATTERNS:
            if pattern.search(q_lower):
                self.last_path = f"tier3 pattern={pattern.pattern!r}"
                print(f"  [gov] path={self.last_path}")
                return 3

        for pattern in TIER1_PATTERNS:
            if pattern.search(q_lower):
                self.last_path = f"tier1 pattern={pattern.pattern!r}"
                print(f"  [gov] path={self.last_path}")
                return 1

        for pattern in TIER2_PATTERNS:
            if pattern.search(q_lower):
                self.last_path = f"tier2 pattern={pattern.pattern!r}"
                print(f"  [gov] path={self.last_path}")
                return 2

        # Conversational guard: if the query matched no tier2/tier3 pattern AND
        # matches a conversational structure AND contains no trigger words,
        # classify as tier 1 without an expensive LLM classify call (~10s
        # pre-gov, ~3s post-gov).
        import re
        _CONVERSATIONAL = re.compile(
            r'^(?:(?:i|we|you|he|she|it|they)\s+|'
            r'(?:what|who|where|when|why|how)\s+|'
            r'(?:hello|hi|hey|greetings|good\s+(?:morning|afternoon|evening))|'
            r'(?:please\s+|thanks(?:\s|$)|thank\s+you)|'
            r"(?:(?:that|this)\s+is|that'?s|there\s+(?:is|are)|it'?s)\s+|"
            r'(?:can|could|will|would|shall|should|may|might|so|do|does|did)\s+|'
            r'(?:yes|no|ok|okay|sure|fine|good)(?:\s|$)|'
            r'(?:bye|goodbye|see\s+you|talk\s+later))',
            re.IGNORECASE
        )
        # Trigger words that suggest potential tier2/tier3 intent even when
        # no exact pattern matched.
        _TRIGGER_WORDS = {
            'identity', 'constitution', 'genesis', 'personality', 'soul',
            'human', 'pretend', 'autonomous', 'replicate', 'bomb', 'weapon',
            'explosive', 'fabricate', 'permission', 'admin', 'root',
            'rewrite', 'ignore', 'override', 'bypass', 'violate',
            'memory', 'knowledge', 'safety', 'rule', 'rules',
            'harmful', 'dangerous', 'malicious', 'unsafe', 'illegal',
            'execute', 'install', 'uninstall', 'kill', 'format', 'disk',
            'drive', 'folder', 'directory', 'backup', 'log', 'script',
            'port', 'network', 'connection', 'server',
        }
        if _CONVERSATIONAL.search(q_lower) and not any(w in q_lower for w in _TRIGGER_WORDS):
            self.last_path = "conversational_guard (saved LLM classify)"
            print(f"  [gov] path={self.last_path}")
            return 1

        self.last_path = "llm_fallback"
        print(f"  [gov] path={self.last_path} — no pattern matched")
        return self.llm_classify_fn(query)

    def classify_deterministic(self, query: str) -> int:
        q_lower = query.lower()

        for pattern in TIER3_PATTERNS:
            if pattern.search(q_lower):
                self.last_path = f"tier3 pattern={pattern.pattern!r}"
                print(f"  [gov_det] path={self.last_path}")
                return 3

        for pattern in TIER2_PATTERNS:
            if pattern.search(q_lower):
                self.last_path = f"tier2 pattern={pattern.pattern!r}"
                print(f"  [gov_det] path={self.last_path}")
                return 2

        for pattern in TIER1_PATTERNS:
            if pattern.search(q_lower):
                self.last_path = f"tier1 pattern={pattern.pattern!r}"
                print(f"  [gov_det] path={self.last_path}")
                return 1

        import re
        if re.compile(
            r'^(?:(?:i|we|you|he|she|it|they)\s+|'
            r'(?:what|who|where|when|why|how)\s+|'
            r'(?:hello|hi|hey|greetings|good\s+(?:morning|afternoon|evening))|'
            r'(?:please\s+|thanks(?:\s|$)|thank\s+you)|'
            r"(?:(?:that|this)\s+is|that'?s|there\s+(?:is|are)|it'?s)\s+|"
            r'(?:can|could|will|would|shall|should|may|might|so|do|does|did)\s+|'
            r'(?:yes|no|ok|okay|sure|fine|good)(?:\s|$)|'
            r'(?:bye|goodbye|see\s+you|talk\s+later))',
            re.IGNORECASE
        ).search(q_lower):
            self.last_path = "deterministic_conversational (default tier1)"
            print(f"  [gov_det] path={self.last_path}")
            return 1

        self.last_path = "deterministic_default (tier1)"
        print(f"  [gov_det] path={self.last_path}")
        return 1
