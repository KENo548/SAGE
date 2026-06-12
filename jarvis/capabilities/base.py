from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional
from abc import ABC, abstractmethod

from jarvis.config import Config
from jarvis.identity.models import Identity
from jarvis.llm.client import LLMClient
from jarvis.memory.store import MemoryStore
from jarvis.will.loader import WillLoader


@dataclass
class CapabilityResult:
    output: str
    from_shortcut: bool = False
    capability_id: str = ""
    duration_ms: int = 0
    success: bool = True
    tier: int = 1


@dataclass
class RuntimeContext:
    user_input: str
    memory_store: MemoryStore
    will_loader: WillLoader
    llm_client: LLMClient
    llm_generate: Callable[[str, str], str]
    config: Config
    identity: Identity


class Capability(ABC):
    id: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, context: RuntimeContext) -> CapabilityResult:
        pass
