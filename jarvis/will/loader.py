import os
from datetime import datetime, timezone

import yaml

from jarvis.will.models import Goal, GoalState, Will


class WillLoader:
    def __init__(self, path: str) -> None:
        self._path = path

    def load(self) -> Will:
        if not os.path.exists(self._path):
            return Will(active_goal=None, current_goals=[], history=[])
        with open(self._path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        goals_list = data.get("goals", [])
        goals = [self._dict_to_goal(g) for g in goals_list]
        active_goal_id = data.get("active_goal_id")
        active_goal = next((g for g in goals if g.id == active_goal_id), None)
        current = [g for g in goals if g.state not in (GoalState.completed, GoalState.failed, GoalState.archived)]
        history = [g for g in goals if g.state in (GoalState.completed, GoalState.failed, GoalState.archived)]
        return Will(active_goal=active_goal, current_goals=current, history=history)

    def save(self, will: Will) -> None:
        goals: list[dict] = []
        all_ids = set()
        for g in will.current_goals + will.history:
            if g.id not in all_ids:
                goals.append(self._goal_to_dict(g))
                all_ids.add(g.id)
        if will.active_goal and will.active_goal.id not in all_ids:
            goals.append(self._goal_to_dict(will.active_goal))
            all_ids.add(will.active_goal.id)
        data = {"goals": goals, "active_goal_id": will.active_goal.id if will.active_goal else None}
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def save_manager(self, manager: "GoalManager") -> None:
        will = Will(
            active_goal=manager.active_goal,
            current_goals=manager.current_goals,
            history=manager.history,
        )
        self.save(will)

    @staticmethod
    def _dict_to_goal(d: dict) -> Goal:
        return Goal(
            id=d["id"],
            description=d["description"],
            priority=d.get("priority", "normal"),
            state=GoalState(d.get("state", "pending")),
            created_at=_parse_dt(d.get("created_at")),
            updated_at=_parse_dt(d.get("updated_at")),
        )

    @staticmethod
    def _goal_to_dict(g: Goal) -> dict:
        return {
            "id": g.id,
            "description": g.description,
            "priority": g.priority,
            "state": g.state.value,
            "created_at": g.created_at.isoformat(),
            "updated_at": g.updated_at.isoformat(),
        }


def _parse_dt(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)
