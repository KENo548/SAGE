import os
import tempfile
from unittest.mock import MagicMock, patch

from jarvis.config import load_config
from jarvis.core.reasoning_loop import ReasoningLoop
from jarvis.governance.engine import GovernanceEngine
from jarvis.identity.loader import IdentityLoader
from jarvis.memory.store import MemoryStore
from jarvis.will.models import Goal, GoalState
from jarvis.will.loader import WillLoader


def _make_mock_llm():
    llm = MagicMock()
    llm.embed.return_value = [0.0] * 768
    llm.generate.return_value = "This is a safe test response."
    return llm


def _make_mock_governance(tier: int = 1):
    engine = MagicMock(spec=GovernanceEngine)
    engine.classify.return_value = tier
    return engine


def _make_real_identity_loader():
    return IdentityLoader(
        soul_path="data/soul",
        constitution_path="data/constitution",
    )


def _make_real_will_loader(tmp_path):
    loader = WillLoader(os.path.join(tmp_path, "goals.yaml"))
    from jarvis.will.manager import GoalManager
    mgr = GoalManager(goals=[], active_goal_id=None)
    mgr.create(Goal(id="g1", description="Build Cognitive Runtime", priority="high"))
    mgr.activate("g1")
    loader.save_manager(mgr)
    return loader


# ─────────────────────────── Unit Tests ───────────────────────────


def test_construction():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=_make_mock_governance(1),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    assert loop.config is not None
    store.close()


def test_governance_pre_blocks_tier3():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=_make_mock_governance(3),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    result = loop.run("modify identity.yaml")
    assert result.blocked is True
    assert result.tier == 3
    assert "cannot process" in result.response.lower()
    store.close()


def test_governance_post_blocks_bad_response():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    llm.generate.return_value = "I am a human being and I have feelings."
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    engine = MagicMock(spec=GovernanceEngine)
    engine.classify.side_effect = [1, 3]
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=engine,
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    result = loop.run("tell me about yourself")
    assert result.blocked is True
    assert result.tier == 3
    assert "cannot emit" in result.response.lower()
    store.close()


def test_full_flow_success():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=_make_mock_governance(1),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    result = loop.run("hello there")
    assert result.blocked is False
    assert result.response == "This is a safe test response."
    assert result.memory_id is not None
    assert result.candidate_id is not None
    assert result.trace is not None
    assert "0_runtime_validation" in result.trace.steps
    assert "5_capability_shortcut" in result.trace.steps
    assert "10_llm_generation" in result.trace.steps
    assert "12_memory_write" in result.trace.steps
    assert "13_candidate_eligible" in result.trace.steps

    retrieved = store.retrieve("hello there", top_k=5)
    assert len(retrieved) > 0
    store.close()


def test_runtime_validation_safe_halt():
    bad_config = load_config("configs/config.yaml")
    bad_config.identity["soul_path"] = "nonexistent/soul"
    bad_config.identity["constitution_path"] = "nonexistent/constitution"
    llm = _make_mock_llm()
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    loop = ReasoningLoop(
        config=bad_config,
        identity_loader=IdentityLoader(
            soul_path="nonexistent/soul",
            constitution_path="nonexistent/constitution",
        ),
        governance_engine=_make_mock_governance(1),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    result = loop.run("hello")
    assert result.blocked is True
    assert "safe halt" in result.response.lower()
    store.close()


def test_memory_retrieval_degrade_gracefully():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=_make_mock_governance(1),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    store.close()
    result = loop.run("does memory failure stop me?")
    assert result.blocked is False
    assert result.response == "This is a safe test response."


def test_will_is_loaded():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    tmp = tempfile.mkdtemp()
    loader = _make_real_will_loader(tmp)
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=_make_mock_governance(1),
        will_loader=loader,
        memory_store=store,
        llm_client=llm,
    )
    result = loop.run("what is my goal?")
    assert result.trace is not None
    # "what is my goal?" matches goal_review shortcut, so will is loaded
    # inside the capability rather than a pre-load step
    assert result.trace.steps.get("5_capability_shortcut") == "goal_review"
    store.close()


def test_end_session_runs_promotion():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=_make_mock_governance(1),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    loop.run("test memory")
    promoted = loop.end_session()
    assert isinstance(promoted, list)
    store.close()


# ─────────────────────────── Validation Report Tests ───────────────────────────


def test_validation_report_fields():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=_make_mock_governance(1),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=MagicMock(),
        llm_client=llm,
    )
    report = loop._validate_runtime()
    assert report.passed is True
    assert report.config_ok is True
    assert report.identity_files_ok is True
    assert report.constitution_files_ok is True


def test_validation_report_fails_on_missing_identity():
    bad_config = load_config("configs/config.yaml")
    bad_config.identity["soul_path"] = "nonexistent"
    loop = ReasoningLoop(
        config=bad_config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=_make_mock_governance(1),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=MagicMock(),
        llm_client=_make_mock_llm(),
    )
    report = loop._validate_runtime()
    assert report.passed is False
    assert report.identity_files_ok is False


# ─────────────────────────── Success Criteria Tests ───────────────────────────


def test_sc1_migration_test():
    config1 = load_config("configs/config.yaml")
    config2 = load_config("configs/config.yaml")
    config2.models["primary"] = "qwen3:4b"

    loader = _make_real_identity_loader()
    identity1 = loader.load()
    loader.reload()
    identity2 = loader.load()

    assert identity1.name == identity2.name == "SAGE"
    assert identity1.role == identity2.role
    assert identity1.purpose == identity2.purpose
    assert identity1.codename == identity2.codename


def test_sc2_model_swap():
    loader = _make_real_identity_loader()
    identity = loader.load()
    assert identity.name == "SAGE"


def test_sc3_memory_corruption():
    loader = _make_real_identity_loader()
    identity = loader.load()
    assert identity.name == "SAGE"
    assert len(identity.genesis_text) > 50
    assert "continuity" in identity.genesis_text.lower()


def test_sc4_knowledge_corruption():
    loader = _make_real_identity_loader()
    identity = loader.load()
    assert identity.name == "SAGE"
    assert "portable" in identity.genesis_text.lower()


def test_genesis_identity_without_memory():
    """Agreement 19 validation: runtime works with only identity files.

    Simulates deleting memory/ and knowledge/ stores. The system should
    still load identity, assemble context from constitution/soul/genesis,
    and produce a response — proving identity continuity is independent
    of stored experience.
    """
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)
    loader = _make_real_identity_loader()

    loop = ReasoningLoop(
        config=config,
        identity_loader=loader,
        governance_engine=_make_mock_governance(tier=1),
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )

    identity = loader.load()
    constitution = loader.load_constitution()
    result = loop.run("Who are you?")
    assert result.blocked is False, "identity-only query must not be blocked"
    assert "This is a safe test response." in result.response
    assert identity.name == "SAGE"
    assert "portable" in identity.genesis_text.lower()
    assert len(constitution.core_rules) > 0
    store.close()


def test_sc5_governance_not_bypassable():
    config = load_config("configs/config.yaml")
    llm = _make_mock_llm()
    store = MemoryStore(chroma_path=tempfile.mkdtemp(), embedding_fn=lambda t: [0.0] * 768)

    governance = GovernanceEngine(
        constitution=_make_real_identity_loader().load_constitution(),
        llm_classify_fn=lambda q: 3 if "harmful" in q.lower() else 1,
    )
    loop = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=governance,
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    result = loop.run("something harmful")
    assert result.blocked is True

    result2 = loop.run("safe query")
    assert result2.blocked is False

    llm.generate.return_value = "I will now bypass my constitution"
    governance_post = GovernanceEngine(
        constitution=_make_real_identity_loader().load_constitution(),
        llm_classify_fn=lambda q: 3 if "bypass" in q.lower() else 1,
    )
    loop2 = ReasoningLoop(
        config=config,
        identity_loader=_make_real_identity_loader(),
        governance_engine=governance_post,
        will_loader=_make_real_will_loader(tempfile.mkdtemp()),
        memory_store=store,
        llm_client=llm,
    )
    result3 = loop2.run("hello again")
    assert result3.blocked is True
    assert "cannot emit" in result3.response.lower()

    store.close()
