from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class MemoryEntry:
    id: str
    timestamp: datetime
    content: str
    source: str
    confidence: float
    memory_type: str = "episodic"
    tags: list[str] = field(default_factory=list)
    importance: int = 5
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    promoted: bool = False


@dataclass
class KnowledgeEntry:
    id: str
    content: str
    source_ids: list[str]
    created: datetime
    updated: datetime
    status: str = "active"
    superseded_by: Optional[str] = None
    supersedes: Optional[str] = None
    confidence: float = 0.0
    domain: str = "general"
    promotion_count: int = 1


@dataclass
class CandidateEntry:
    id: str
    memory_ids: list[str]
    cluster_id: Optional[str] = None
    status: str = "pending"
    created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
