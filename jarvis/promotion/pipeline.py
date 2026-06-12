import uuid
from datetime import datetime, timezone
from typing import Callable, Optional

from jarvis.memory.store import MemoryStore
from jarvis.memory.schemas import KnowledgeEntry


def compute_similarity_matrix(embeddings: list[list[float]]) -> list[list[float]]:
    n = len(embeddings)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            sim = _cosine_similarity(embeddings[i], embeddings[j])
            matrix[i][j] = sim
            matrix[j][i] = sim
    return matrix


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(ai * bi for ai, bi in zip(a, b))
    norm_a = sum(ai * ai for ai in a) ** 0.5
    norm_b = sum(bi * bi for bi in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def cluster_by_average_linkage(
    similarity_matrix: list[list[float]],
    threshold: float,
) -> list[set[int]]:
    n = len(similarity_matrix)
    clusters: list[set[int]] = [{i} for i in range(n)]

    while True:
        merged = False
        best_i = best_j = -1
        best_sim = threshold

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                avg_sim = _average_cross_similarity(clusters[i], clusters[j], similarity_matrix)
                if avg_sim >= best_sim:
                    best_sim = avg_sim
                    best_i, best_j = i, j

        if best_i >= 0:
            merged_cluster = clusters[best_i] | clusters[best_j]
            clusters = [c for k, c in enumerate(clusters) if k not in (best_i, best_j)]
            clusters.append(merged_cluster)
            merged = True

        if not merged:
            break

    return clusters


def _average_cross_similarity(
    cluster_a: set[int],
    cluster_b: set[int],
    matrix: list[list[float]],
) -> float:
    total = 0.0
    count = 0
    for i in cluster_a:
        for j in cluster_b:
            total += matrix[i][j]
            count += 1
    return total / count if count > 0 else 0.0


def check_supersession(
    new_content: str,
    existing_knowledge: list[KnowledgeEntry],
    embedding_fn: Callable[[str], list[float]],
    llm_judge_fn: Callable[[str, str], bool],
    similarity_threshold: float = 0.85,
) -> Optional[KnowledgeEntry]:
    new_embedding = embedding_fn(new_content)
    for existing in existing_knowledge:
        existing_embedding = embedding_fn(existing.content)
        sim = _cosine_similarity(new_embedding, existing_embedding)
        if sim >= similarity_threshold:
            if llm_judge_fn(existing.content, new_content):
                return existing
    return None


def run_promotion_pipeline(
    store: MemoryStore,
    embedding_fn: Callable[[str], list[float]],
    threshold: float = 0.65,
    min_cluster_size: int = 3,
    llm_summarize_fn: Optional[Callable[[list[str]], str]] = None,
    llm_conflict_fn: Optional[Callable[[str, str], bool]] = None,
) -> list[KnowledgeEntry]:
    candidates = store.get_candidates_for_clustering()
    if not candidates:
        return []

    all_embeddings: list[list[float]] = []
    all_contents: list[str] = []
    for c in candidates:
        for mem_id in c.memory_ids:
            mem = store.get_memory_by_id(mem_id)
            if mem and not mem.promoted:
                all_embeddings.append(embedding_fn(mem.content))
                all_contents.append(mem.content)
                break

    if len(all_contents) < min_cluster_size:
        return []

    sim_matrix = compute_similarity_matrix(all_embeddings)
    clusters = cluster_by_average_linkage(sim_matrix, threshold)

    new_knowledge_entries: list[KnowledgeEntry] = []
    for cluster in clusters:
        if len(cluster) < min_cluster_size:
            continue

        cluster_indices = sorted(cluster)
        cluster_texts = [all_contents[i] for i in cluster_indices]

        if llm_summarize_fn:
            summary = llm_summarize_fn(cluster_texts)
        else:
            summary = "; ".join(cluster_texts)

        source_ids = []
        for i in cluster_indices:
            for c in candidates:
                for mem_id in c.memory_ids:
                    source_ids.append(mem_id)

        now = datetime.now(timezone.utc)
        entry = KnowledgeEntry(
            id=str(uuid.uuid4()),
            content=summary,
            source_ids=list(set(source_ids)),
            created=now,
            updated=now,
            confidence=1.0,
            domain="general",
            promotion_count=1,
        )

        if llm_conflict_fn:
            existing_entries = store.get_active_knowledge()
            conflict = check_supersession(
                summary, existing_entries, embedding_fn, llm_conflict_fn
            )
            if conflict:
                entry.supersedes = conflict.id

        entry_id = store.write_knowledge(entry)

        if entry.supersedes:
            store.supersede_knowledge(entry.supersedes, entry_id)

        for i in cluster_indices:
            for c in candidates:
                if i < len(all_contents):
                    store.mark_candidate_promoted(c.id)

        new_knowledge_entries.append(entry)

    return new_knowledge_entries
