import os
import tempfile
import hashlib
from datetime import datetime, timezone

from jarvis.memory.store import MemoryStore
from jarvis.memory.schemas import MemoryEntry, KnowledgeEntry


CHROMA_TEST_DIR = None


def _create_store():
    global CHROMA_TEST_DIR
    CHROMA_TEST_DIR = tempfile.mkdtemp()
    return MemoryStore(chroma_path=CHROMA_TEST_DIR, embedding_fn=_mock_embed)


def _destroy_store(store):
    store.close()
    import shutil
    if CHROMA_TEST_DIR and os.path.exists(CHROMA_TEST_DIR):
        shutil.rmtree(CHROMA_TEST_DIR, ignore_errors=True)


def _mock_embed(text: str) -> list[float]:
    h = hashlib.md5(text.encode()).digest()
    vec = [b / 255.0 for b in h[:8]]
    return vec + [0.0] * 760


def test_write_and_retrieve():
    store = _create_store()
    eid = store.write_user_message("hello world", _mock_embed("hello world"))
    assert eid
    results = store.retrieve("hello", top_k=5)
    assert len(results) > 0
    assert results[0].content == "hello world"
    assert results[0].source == "user"
    _destroy_store(store)


def test_write_response():
    store = _create_store()
    eid = store.write_response("hello", "hi there", _mock_embed("hello\nhi there"))
    assert eid
    results = store.retrieve("hi there", top_k=5)
    assert len(results) > 0
    assert results[0].content == "hello\nhi there"
    assert results[0].source == "self"
    _destroy_store(store)


def test_round_trip_preserves_fields():
    store = _create_store()
    entry = MemoryEntry(
        id="", timestamp=datetime.now(timezone.utc), content="test content",
        source="user", confidence=1.0, importance=7,
    )
    eid = store.write_memory(entry)
    results = store.retrieve("test content", top_k=5)
    assert len(results) > 0
    mem = results[0]
    assert mem.id == eid
    assert mem.content == "test content"
    assert mem.source == "user"
    assert mem.importance == 7
    _destroy_store(store)


def test_knowledge_write_and_retrieve():
    store = _create_store()
    k = KnowledgeEntry(
        id="", content="prefers morning meetings", source_ids=["mem1", "mem2"],
        created=datetime.now(timezone.utc), updated=datetime.now(timezone.utc), domain="work",
    )
    kid = store.write_knowledge(k)
    assert kid
    results = store.retrieve("morning meetings", top_k=5, memory_type="knowledge")
    assert len(results) > 0
    assert results[0].content == "prefers morning meetings"
    _destroy_store(store)


def test_supersession():
    store = _create_store()
    k1 = KnowledgeEntry(id="", content="likes coffee", source_ids=[], created=datetime.now(timezone.utc), updated=datetime.now(timezone.utc))
    k2 = KnowledgeEntry(id="", content="switched to tea", source_ids=[], created=datetime.now(timezone.utc), updated=datetime.now(timezone.utc))
    id1 = store.write_knowledge(k1)
    id2 = store.write_knowledge(k2)
    store.supersede_knowledge(id1, id2)
    active = store.get_active_knowledge()
    assert len(active) == 1
    assert active[0].id == id2
    _destroy_store(store)


def test_candidates():
    store = _create_store()
    mem_id = store.write_user_message("test", _mock_embed("test"))
    cid = store.write_candidate([mem_id])
    assert cid
    candidates = store.get_candidates_for_clustering()
    assert len(candidates) > 0
    assert mem_id in candidates[0].memory_ids
    store.mark_candidate_promoted(cid)
    assert len(store.get_candidates_for_clustering()) == 0
    _destroy_store(store)
