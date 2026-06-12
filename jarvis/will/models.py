from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class GoalState(str, Enum):
    pending = "pending"
    active = "active"
    paused = "paused"
    completed = "completed"
    failed = "failed"
    archived = "archived"


TERMINAL_STATES: set[GoalState] = {GoalState.completed, GoalState.failed, GoalState.archived}


@dataclass
class Goal:
    id: str
    description: str
    priority: str  # critical, high, normal, low
    state: GoalState = GoalState.pending
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Will:
    active_goal: Goal | None
    current_goals: list[Goal]
    history: list[Goal]
