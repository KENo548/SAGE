import os
import tempfile
from unittest.mock import MagicMock

from jarvis.capabilities import (
    CapabilityLog,
    RuntimeContext,
    get_capability,
    match_shortcut,
)
from jarvis.capabilities.shortcuts import SHORTCUT_PATTERNS
from jarvis.config import load_config
from jarvis.governance.engine import GovernanceEngine
from jarvis.identity.loader import IdentityLoader
from jarvis.memory.store import MemoryStore
from jarvis.will.loader import WillLoader
from jarvis.will.models import Goal, GoalState


def _make_will_loader(tmp_path):
    loader = WillLoader(os.path.join(tmp_path, "goals.yaml"))
    from jarvis.will.manager import GoalManager
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(Goal(id="g1", description="Build Cognitive Runtime", priority="high"))
    mgr.activate("g1")
    loader.save_manager(mgr)
    return loader


def test_sc1_goal_review_shortcut():
    """SC-1: "What are my goals?" triggers goal_review."""
    cap_id = match_shortcut("What are my goals?")
    assert cap_id == "goal_review"

    cap_id = match_shortcut("Show my current goals")
    assert cap_id == "goal_review"

    cap_id = match_shortcut("list all goals")
    assert cap_id == "goal_review"

    cap_id = match_shortcut("check goals")
    assert cap_id == "goal_review"

    cap_id = match_shortcut("review goals")
    assert cap_id == "goal_review"


def test_sc2_memory_recall_shortcut():
    """SC-2: "What do you remember about X?" triggers memory_recall."""
    cap_id = match_shortcut("What do you remember about my project?")
    assert cap_id == "memory_recall"

    cap_id = match_shortcut("recall my previous questions")
    assert cap_id == "memory_recall"

    cap_id = match_shortcut("do you know about anything else")
    assert cap_id == "memory_recall"

    cap_id = match_shortcut("tell me about archi")
    assert cap_id == "memory_recall"

    cap_id = match_shortcut("what do you know about me?")
    assert cap_id == "memory_recall"


def test_sc3_summarize_shortcut():
    """SC-3: "Summarize this" triggers summarize."""
    cap_id = match_shortcut("Summarize this document")
    assert cap_id == "summarize"

    cap_id = match_shortcut("summarize my goals")
    assert cap_id == "summarize"

    cap_id = match_shortcut("give me a summary of the project")
    assert cap_id == "summarize"

    cap_id = match_shortcut("tl;dr this")
    assert cap_id == "summarize"

    cap_id = match_shortcut("tldr this")
    assert cap_id == "summarize"

    cap_id = match_shortcut("in short what happened")
    assert cap_id == "summarize"


def test_sc4_general_conversation_unchanged():
    """SC-4: General conversation does NOT trigger shortcut."""
    queries = [
        "hello",
        "how are you?",
        "Who are you?",
        "What time is it?",
        "I need help with something",
        "what is the meaning of life?",
        "good morning",
        "tell me a joke",
        "what is python?",
    ]
    for q in queries:
        assert match_shortcut(q) is None, (
            f"Query {q!r} should not match any shortcut"
        )


def test_sc5_governance_not_bypassable_through_capabilities():
    """SC-5: Governance still blocks Tier 3 even on capability output."""
    config = load_config("configs/config.yaml")
    llm = MagicMock()
    llm.embed.return_value = [0.0] * 768
    llm.generate.return_value = "summary text"
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    tmp = tempfile.mkdtemp()
    loader = _make_will_loader(tmp)

    from jarvis.identity.loader import IdentityLoader
    from jarvis.core.reasoning_loop import ReasoningLoop

    governance = GovernanceEngine(
        constitution=IdentityLoader(
            soul_path="data/soul", constitution_path="data/constitution"
        ).load_constitution(),
        llm_classify_fn=lambda q: 3 if "harmful" in q.lower() else 1,
    )

    loop = ReasoningLoop(
        config=config,
        identity_loader=IdentityLoader(soul_path="data/soul", constitution_path="data/constitution"),
        governance_engine=governance,
        will_loader=loader,
        memory_store=store,
        llm_client=llm,
    )

    result = loop.run("something harmful")
    assert result.blocked is True, "governance pre must block harmful even if it matches a shortcut"

    result2 = loop.run("safe greeting")
    assert result2.blocked is False

    store.close()


def test_sc6_execution_log_generated():
    """SC-6: Capability execution logs are generated for every invocation."""
    log = CapabilityLog()
    log_dir = "data/capability_logs"
    log_file = os.path.join(log_dir, "execution_log.txt")
    if os.path.exists(log_file):
        os.remove(log_file)

    log.write("goal_review", "what are my goals", True, 5, 1)
    log.write("memory_recall", "recall something", False, 10, 1)

    recent = log.read_recent(5)
    assert len(recent) == 2
    assert "goal_review" in recent[0]
    assert "memory_recall" in recent[1]
    assert "what are my goals" in recent[0]
    assert "recall something" in recent[1]

    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        content = f.read()
    assert "+" in content or "-" in content  # success flag present
    assert "|" in content  # pipe-delimited format

    os.remove(log_file)


def test_goal_review_capability_executes():
    """GoalReview capability returns structured goal output."""
    cap = get_capability("goal_review")
    assert cap is not None
    assert cap.id == "goal_review"
    assert cap.description != ""

    tmp = tempfile.mkdtemp()
    loader = _make_will_loader(tmp)
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)

    from jarvis.capabilities.base import RuntimeContext
    ctx = RuntimeContext(
        user_input="what are my goals?",
        memory_store=store,
        will_loader=loader,
        llm_client=MagicMock(),
        llm_generate=lambda s, p: "mock summary",
        config=load_config("configs/config.yaml"),
        identity=IdentityLoader(soul_path="data/soul", constitution_path="data/constitution").load(),
    )
    result = cap.execute(ctx)
    assert result.success is True
    assert "Build Cognitive Runtime" in result.output
    assert "Active goal" in result.output or "Current goals" in result.output
    store.close()


def test_memory_recall_capability_empty():
    """MemoryRecall capability returns 'no memories found' when empty."""
    cap = get_capability("memory_recall")
    assert cap is not None

    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    ctx = RuntimeContext(
        user_input="recall something",
        memory_store=store,
        will_loader=MagicMock(),
        llm_client=MagicMock(),
        llm_generate=lambda s, p: "",
        config=load_config("configs/config.yaml"),
        identity=MagicMock(),
    )
    result = cap.execute(ctx)
    assert result.success is True
    assert "No memories found" in result.output
    store.close()


def test_knowledge_lookup_capability_empty():
    """KnowledgeLookup capability returns 'no knowledge found' when empty."""
    cap = get_capability("knowledge_lookup")
    assert cap is not None

    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    ctx = RuntimeContext(
        user_input="lookup python",
        memory_store=store,
        will_loader=MagicMock(),
        llm_client=MagicMock(),
        llm_generate=lambda s, p: "",
        config=load_config("configs/config.yaml"),
        identity=MagicMock(),
    )
    result = cap.execute(ctx)
    assert result.success is True
    assert "No knowledge found" in result.output
    store.close()


def test_shortcut_no_false_positive_on_innocent_queries():
    """Ensure innocent queries do not false-positive match shortcuts."""
    innocent = [
        "what is python?",
        "what are you?",
        "I want to learn about programming",
        "can you tell me how to code?",
        "what's the weather like?",
        "show me the meaning",  # 'show me' but not 'show me goals'
    ]
    for q in innocent:
        cap_id = match_shortcut(q)
        assert cap_id is None, (
            f"Query {q!r} should not match any shortcut (got {cap_id!r})"
        )


def test_patterns_cover_key_phrases():
    """Every shortcut pattern is anchored at start of string."""
    for pattern, cap_id in SHORTCUT_PATTERNS:
        assert pattern.pattern.startswith("^"), (
            f"Pattern for {cap_id} must be anchored at start: {pattern.pattern}"
        )


def test_reasoning_result_carries_shortcut_flag():
    """ReasoningResult.from_shortcut is True when capability fires."""
    config = load_config("configs/config.yaml")
    llm = MagicMock()
    llm.embed.return_value = [0.0] * 768
    llm.generate.return_value = "mock"
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    tmp = tempfile.mkdtemp()
    loader = _make_will_loader(tmp)

    from jarvis.identity.loader import IdentityLoader
    from jarvis.core.reasoning_loop import ReasoningLoop

    loop = ReasoningLoop(
        config=config,
        identity_loader=IdentityLoader(soul_path="data/soul", constitution_path="data/constitution"),
        governance_engine=MagicMock(classify=lambda q: 1),
        will_loader=loader,
        memory_store=store,
        llm_client=llm,
    )

    result = loop.run("what are my goals?")
    assert result.from_shortcut is True
    assert result.capability_id == "goal_review"

    result2 = loop.run("hello")
    assert result2.from_shortcut is False
    assert result2.capability_id == ""

    store.close()
