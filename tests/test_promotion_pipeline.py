import os
import tempfile
import hashlib
import shutil
from datetime import datetime, timezone

from jarvis.memory.store import MemoryStore
from jarvis.memory.schemas import MemoryEntry, KnowledgeEntry
from jarvis.promotion.pipeline import (
    compute_similarity_matrix,
    cluster_by_average_linkage,
    run_promotion_pipeline,
)


_store_instance = None
_chroma_path = None


def _create_store():
    global _store_instance, _chroma_path
    _chroma_path = tempfile.mkdtemp()
    _store_instance = MemoryStore(chroma_path=_chroma_path, embedding_fn=_mock_embed)
    return _store_instance


def _destroy_store():
    global _store_instance, _chroma_path
    if _store_instance:
        try:
            _store_instance.close()
        except Exception:
            pass
        _store_instance = None
    if _chroma_path and os.path.exists(_chroma_path):
        shutil.rmtree(_chroma_path, ignore_errors=True)
        _chroma_path = None


def _mock_embed(text: str) -> list[float]:
    h = hashlib.md5(text.encode()).digest()
    vec = [b / 255.0 for b in h[:8]]
    return vec + [0.0] * 760


def _mock_embed_dense(text: str) -> list[float]:
    h = hashlib.md5(text.encode()).digest()
    return [b / 255.0 for b in h]


def test_compute_similarity_matrix():
    embeddings = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
    matrix = compute_similarity_matrix(embeddings)
    assert abs(matrix[0][1] - 1.0) < 0.001
    assert abs(matrix[0][2] - 0.0) < 0.001
    assert abs(matrix[1][2] - 0.0) < 0.001


def test_cluster_by_average_linkage():
    sim_matrix = [
        [1.0, 0.9, 0.3],
        [0.9, 1.0, 0.3],
        [0.3, 0.3, 1.0],
    ]
    clusters = cluster_by_average_linkage(sim_matrix, threshold=0.8)
    cluster_sizes = [len(c) for c in clusters]
    assert 2 in cluster_sizes
    assert 1 in cluster_sizes


def test_average_linkage_prevents_chaining():
    sim_matrix = [
        [1.0, 0.9, 0.5, 0.3],
        [0.9, 1.0, 0.9, 0.5],
        [0.5, 0.9, 1.0, 0.9],
        [0.3, 0.5, 0.9, 1.0],
    ]
    clusters = cluster_by_average_linkage(sim_matrix, threshold=0.8)
    for c in clusters:
        assert len(c) <= 2


def test_pipeline_no_candidates():
    store = _create_store()
    result = run_promotion_pipeline(store, _mock_embed)
    assert result == []
    _destroy_store()


def test_pipeline_with_cluster():
    store = _create_store()
    similar_texts = [
        "I prefer morning meetings",
        "Morning meetings work best for me",
        "I like meetings in the morning",
    ]
    for t in similar_texts:
        eid = store.write_user_message(t, _mock_embed(t))
        store.write_candidate([eid])

    result = run_promotion_pipeline(
        store, _mock_embed_dense, threshold=0.5, min_cluster_size=3,
        llm_summarize_fn=lambda texts: "Prefers morning meetings",
    )
    assert len(result) > 0
    assert "morning" in result[0].content.lower()
    _destroy_store()
