from datetime import datetime, timezone

from jarvis.will.models import Goal, GoalState, TERMINAL_STATES


class GoalManager:
    def __init__(self, goals: list[Goal], active_goal_id: str | None) -> None:
        self._goals: dict[str, Goal] = {g.id: g for g in goals}
        self._active_goal_id: str | None = active_goal_id

    @property
    def active_goal(self) -> Goal | None:
        if self._active_goal_id is None:
            return None
        return self._goals.get(self._active_goal_id)

    @property
    def current_goals(self) -> list[Goal]:
        return [g for g in self._goals.values() if g.state not in TERMINAL_STATES]

    @property
    def history(self) -> list[Goal]:
        return [g for g in self._goals.values() if g.state in TERMINAL_STATES]

    @property
    def all_goals(self) -> list[Goal]:
        return list(self._goals.values())

    def create(self, goal: Goal) -> None:
        if goal.id in self._goals:
            raise ValueError(f"Goal with id '{goal.id}' already exists")
        goal.updated_at = datetime.now(timezone.utc)
        self._goals[goal.id] = goal

    def update(self, goal_id: str, description: str | None = None, priority: str | None = None) -> Goal:
        goal = self._get(goal_id)
        if description is not None:
            goal.description = description
        if priority is not None:
            goal.priority = priority
        goal.updated_at = datetime.now(timezone.utc)
        return goal

    def delete(self, goal_id: str) -> None:
        goal = self._get(goal_id)
        if self._active_goal_id == goal_id:
            self._active_goal_id = None
        del self._goals[goal.id]

    def activate(self, goal_id: str) -> Goal:
        goal = self._get(goal_id)
        if goal.state in TERMINAL_STATES:
            raise ValueError(f"Cannot activate goal '{goal_id}' in terminal state '{goal.state.value}'")
        if self._active_goal_id is not None and self._active_goal_id != goal_id:
            old_active = self._goals.get(self._active_goal_id)
            if old_active and old_active.state == GoalState.active:
                old_active.state = GoalState.paused
                old_active.updated_at = datetime.now(timezone.utc)
        goal.state = GoalState.active
        goal.updated_at = datetime.now(timezone.utc)
        self._active_goal_id = goal_id
        return goal

    def pause(self, goal_id: str) -> Goal:
        goal = self._get(goal_id)
        if goal.state != GoalState.active:
            raise ValueError(f"Goal '{goal_id}' is not active (state: {goal.state.value})")
        goal.state = GoalState.paused
        goal.updated_at = datetime.now(timezone.utc)
        if self._active_goal_id == goal_id:
            self._active_goal_id = None
        return goal

    def complete(self, goal_id: str) -> Goal:
        goal = self._get(goal_id)
        if goal.state in TERMINAL_STATES:
            raise ValueError(f"Goal '{goal_id}' is already in terminal state '{goal.state.value}'")
        goal.state = GoalState.completed
        goal.updated_at = datetime.now(timezone.utc)
        if self._active_goal_id == goal_id:
            self._active_goal_id = None
        return goal

    def fail(self, goal_id: str) -> Goal:
        goal = self._get(goal_id)
        if goal.state in TERMINAL_STATES:
            raise ValueError(f"Goal '{goal_id}' is already in terminal state '{goal.state.value}'")
        goal.state = GoalState.failed
        goal.updated_at = datetime.now(timezone.utc)
        if self._active_goal_id == goal_id:
            self._active_goal_id = None
        return goal

    def _get(self, goal_id: str) -> Goal:
        if goal_id not in self._goals:
            raise KeyError(f"Goal '{goal_id}' not found")
        return self._goals[goal_id]
