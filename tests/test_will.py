import os
import tempfile
from datetime import datetime, timezone

from jarvis.will.models import Goal, GoalState, Will, TERMINAL_STATES
from jarvis.will.manager import GoalManager
from jarvis.will.loader import WillLoader


def make_goal(id: str, desc: str, priority: str = "normal", state: GoalState = GoalState.pending) -> Goal:
    return Goal(id=id, description=desc, priority=priority, state=state)


def test_goal_create():
    g = Goal(id="g1", description="test goal", priority="high")
    assert g.id == "g1"
    assert g.state == GoalState.pending
    assert isinstance(g.created_at, datetime)
    assert isinstance(g.updated_at, datetime)


def test_manager_create_and_list():
    mgr = GoalManager(goals=[], active_goal_id=None)
    g = make_goal("g1", "Build Will system", "high")
    mgr.create(g)
    assert len(mgr.current_goals) == 1
    assert mgr.active_goal is None


def test_manager_activate():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "Build Will system", "high"))
    mgr.activate("g1")
    assert mgr.active_goal is not None
    assert mgr.active_goal.id == "g1"
    assert mgr.active_goal.state == GoalState.active


def test_manager_activate_replaces_old():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "First goal", "high"))
    mgr.create(make_goal("g2", "Second goal", "high"))
    mgr.activate("g1")
    mgr.activate("g2")
    assert mgr.active_goal.id == "g2"
    assert mgr._goals["g1"].state == GoalState.paused


def test_manager_pause():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "test", "normal"))
    mgr.activate("g1")
    mgr.pause("g1")
    assert mgr._goals["g1"].state == GoalState.paused
    assert mgr.active_goal is None


def test_manager_complete():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "test", "normal"))
    mgr.activate("g1")
    mgr.complete("g1")
    assert mgr._goals["g1"].state == GoalState.completed
    assert mgr.active_goal is None
    assert len(mgr.current_goals) == 0
    assert len(mgr.history) == 1


def test_manager_fail():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "test", "normal"))
    mgr.activate("g1")
    mgr.fail("g1")
    assert mgr._goals["g1"].state == GoalState.failed
    assert len(mgr.current_goals) == 0
    assert len(mgr.history) == 1


def test_manager_update():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "old", "normal"))
    mgr.update("g1", description="new", priority="critical")
    assert mgr._goals["g1"].description == "new"
    assert mgr._goals["g1"].priority == "critical"


def test_manager_delete():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "test", "normal"))
    mgr.delete("g1")
    assert len(mgr.current_goals) == 0


def test_manager_delete_clears_active():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "test", "normal"))
    mgr.activate("g1")
    mgr.delete("g1")
    assert mgr.active_goal is None


def test_manager_duplicate_id_raises():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "test", "normal"))
    import pytest
    with pytest.raises(ValueError, match="already exists"):
        mgr.create(make_goal("g1", "duplicate", "normal"))


def test_manager_missing_goal_raises():
    mgr = GoalManager(goals=[], active_goal_id=None)
    import pytest
    with pytest.raises(KeyError, match="not found"):
        mgr.activate("nonexistent")


def test_manager_terminal_activate_raises():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "test", "normal"))
    mgr.complete("g1")
    import pytest
    with pytest.raises(ValueError, match="Cannot activate"):
        mgr.activate("g1")


def test_manager_pause_non_active_raises():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "test", "normal"))
    import pytest
    with pytest.raises(ValueError, match="not active"):
        mgr.pause("g1")


def test_loader_save_and_load():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "goals.yaml")
        loader = WillLoader(path)
        mgr = GoalManager(goals=[], active_goal_id=None)
        mgr.create(make_goal("g1", "Build Will", "high"))
        mgr.activate("g1")
        mgr.create(make_goal("g2", "Build Reasoning Loop", "normal"))
        loader.save_manager(mgr)
        loaded_will = loader.load()
        assert loaded_will.active_goal is not None
        assert loaded_will.active_goal.id == "g1"
        assert loaded_will.active_goal.description == "Build Will"
        assert len(loaded_will.current_goals) == 2
        assert len(loaded_will.history) == 0


def test_loader_preserves_states():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "goals.yaml")
        loader = WillLoader(path)
        mgr = GoalManager(goals=[], active_goal_id=None)
        mgr.create(make_goal("g1", "Goal 1", "high"))
        mgr.create(make_goal("g2", "Goal 2", "normal"))
        mgr.activate("g1")
        mgr.complete("g1")
        mgr.activate("g2")
        mgr.pause("g2")
        loader.save_manager(mgr)
        loaded = loader.load()
        assert loaded.active_goal is None
        assert len(loaded.current_goals) == 1
        assert loaded.current_goals[0].state == GoalState.paused
        assert len(loaded.history) == 1
        assert loaded.history[0].state == GoalState.completed


def test_loader_empty_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "goals.yaml")
        loader = WillLoader(path)
        will = loader.load()
        assert will.active_goal is None
        assert will.current_goals == []
        assert will.history == []


def test_loader_missing_file():
    loader = WillLoader("nonexistent/path/goals.yaml")
    will = loader.load()
    assert will.active_goal is None
    assert will.current_goals == []


def test_manager_current_goals_excludes_terminal():
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(make_goal("g1", "pending", "normal", GoalState.pending))
    mgr.create(make_goal("g2", "active", "normal", GoalState.active))
    mgr.create(make_goal("g3", "paused", "normal", GoalState.paused))
    mgr.create(make_goal("g4", "completed", "normal", GoalState.completed))
    mgr.create(make_goal("g5", "failed", "normal", GoalState.failed))
    mgr.create(make_goal("g6", "archived", "normal", GoalState.archived))
    assert len(mgr.current_goals) == 3
    assert len(mgr.history) == 3
