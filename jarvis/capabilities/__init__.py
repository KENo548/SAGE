from jarvis.capabilities.base import Capability, CapabilityResult, RuntimeContext
from jarvis.capabilities.registry import REGISTRY, register_capability, get_capability
from jarvis.capabilities.shortcuts import match_shortcut
from jarvis.capabilities.log import CapabilityLog
from jarvis.capabilities.builtins import GoalReview, MemoryRecall, KnowledgeLookup, Summarize

register_capability(GoalReview())
register_capability(MemoryRecall())
register_capability(KnowledgeLookup())
register_capability(Summarize())

__all__ = [
    "Capability", "CapabilityResult", "RuntimeContext",
    "REGISTRY", "register_capability", "get_capability",
    "match_shortcut",
    "CapabilityLog",
]
