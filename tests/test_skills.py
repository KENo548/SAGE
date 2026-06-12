import os
import tempfile
from unittest.mock import MagicMock

from jarvis.memory.store import MemoryStore
from jarvis.will.models import Goal, GoalState
from jarvis.will.loader import WillLoader
from jarvis.will.manager import GoalManager
from jarvis.skills import maintain_conversation, summarize, recall_memory, lookup_knowledge, review_goals


def test_conversation():
    result = maintain_conversation("hello", "hi there")
    assert result["skill"] == "conversation"
    assert result["input"] == "hello"
    assert result["response"] == "hi there"


def test_summarize():
    llm = MagicMock()
    llm.return_value = "Short summary."
    result = summarize("Long text here " * 100, llm_generate=llm)
    assert isinstance(result, str)
    assert len(result) > 0
    llm.assert_called_once()


def test_recall_memory_empty():
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    results = recall_memory("anything", store)
    assert results == []
    store.close()


def test_recall_memory_with_data():
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    store.write_user_message("user likes python", [0.1] * 768)
    results = recall_memory("python", store)
    assert len(results) > 0
    assert results[0]["source"] == "user"
    store.close()


def test_lookup_knowledge_empty():
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    results = lookup_knowledge("anything", store)
    assert results == []
    store.close()


def test_goal_review_with_goals():
    tmp = tempfile.mkdtemp()
    loader = WillLoader(os.path.join(tmp, "goals.yaml"))
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(Goal(id="g1", description="Build Skills", priority="high"))
    mgr.activate("g1")
    mgr.create(Goal(id="g2", description="Deploy", priority="normal", state=GoalState.pending))
    loader.save_manager(mgr)

    result = review_goals(loader)
    assert result["active_goal"] is not None
    assert result["active_goal"]["description"] == "Build Skills"
    assert len(result["current_goals"]) == 2
    assert len(result["history"]) == 0


def test_goal_review_empty():
    tmp = tempfile.mkdtemp()
    loader = WillLoader(os.path.join(tmp, "goals.yaml"))
    result = review_goals(loader)
    assert result["active_goal"] is None
    assert result["current_goals"] == []
    assert result["history"] == []


def test_goal_review_with_history():
    tmp = tempfile.mkdtemp()
    loader = WillLoader(os.path.join(tmp, "goals.yaml"))
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(Goal(id="g1", description="Phase 1", priority="high"))
    mgr.activate("g1")
    mgr.complete("g1")
    loader.save_manager(mgr)

    result = review_goals(loader)
    assert result["active_goal"] is None
    assert len(result["history"]) == 1
    assert result["history"][0]["state"] == "completed"
