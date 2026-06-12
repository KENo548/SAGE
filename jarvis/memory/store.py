import json
import uuid
from datetime import datetime, timezone
from typing import Callable, Optional

import chromadb
from chromadb.config import Settings

from jarvis.memory.schemas import MemoryEntry, KnowledgeEntry, CandidateEntry


class MemoryStoreError(Exception):
    pass


class MemoryStore:
    def __init__(self, chroma_path: str, embedding_fn: Callable[[str], list[float]]):
        self.embedding_fn = embedding_fn
        self.client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=False),
        )
        self.episodic = self._get_or_create("episodic")
        self.knowledge = self._get_or_create("knowledge")
        self.candidates = self._get_or_create("candidates")

    def _get_or_create(self, name: str):
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(name, metadata={"hnsw:space": "cosine"})

    def close(self):
        try:
            self.client.clear_system_cache()
        except Exception:
            pass

    def retrieve(self, query: str, top_k: int = 5, memory_type: str = "episodic") -> list:
        collection = self.episodic if memory_type == "episodic" else self.knowledge
        query_embedding = self.embedding_fn(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["metadatas", "documents", "distances"],
        )
        entries = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i in range(len(ids)):
            meta = metadatas[i] if i < len(metadatas) else {}
            if memory_type == "episodic":
                entry = MemoryEntry(
                    id=ids[i],
                    timestamp=datetime.fromisoformat(meta.get("timestamp", datetime.now(timezone.utc).isoformat())),
                    content=documents[i] if i < len(documents) else "",
                    source=meta.get("source", "unknown"),
                    confidence=float(meta.get("confidence", 1.0)),
                    memory_type=meta.get("memory_type", "episodic"),
                    tags=json.loads(meta.get("tags", "[]")),
                    importance=int(meta.get("importance", 5)),
                    access_count=int(meta.get("access_count", 0)),
                    last_accessed=datetime.fromisoformat(meta.get("last_accessed", datetime.now(timezone.utc).isoformat())),
                    promoted=meta.get("promoted", "False") == "True",
                )
            else:
                if meta.get("status", "active") == "superseded":
                    continue
                entry = KnowledgeEntry(
                    id=ids[i],
                    content=documents[i] if i < len(documents) else "",
                    source_ids=json.loads(meta.get("source_ids", "[]")),
                    created=datetime.fromisoformat(meta.get("created", datetime.now(timezone.utc).isoformat())),
                    updated=datetime.fromisoformat(meta.get("updated", datetime.now(timezone.utc).isoformat())),
                    status=meta.get("status", "active"),
                    superseded_by=meta.get("superseded_by"),
                    supersedes=meta.get("supersedes"),
                    confidence=float(meta.get("confidence", 0.0)),
                    domain=meta.get("domain", "general"),
                    promotion_count=int(meta.get("promotion_count", 1)),
                )
            entries.append(entry)

        return entries

    def write_memory(self, entry: MemoryEntry) -> str:
        if not entry.id:
            entry.id = str(uuid.uuid4())
        embedding = self.embedding_fn(entry.content)
        self.episodic.add(
            ids=[entry.id],
            embeddings=[embedding],
            documents=[entry.content],
            metadatas=[{
                "id": entry.id,
                "timestamp": entry.timestamp.isoformat(),
                "source": entry.source,
                "confidence": entry.confidence,
                "memory_type": entry.memory_type,
                "tags": json.dumps(entry.tags),
                "importance": entry.importance,
                "access_count": entry.access_count,
                "last_accessed": entry.last_accessed.isoformat(),
                "promoted": str(entry.promoted),
            }],
        )
        return entry.id

    def write_user_message(self, query: str, embedding: list[float]) -> str:
        entry_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        self.episodic.add(
            ids=[entry_id],
            embeddings=[embedding],
            documents=[query],
            metadatas=[{
                "id": entry_id,
                "timestamp": now.isoformat(),
                "source": "user",
                "confidence": 1.0,
                "memory_type": "episodic",
                "tags": "[]",
                "importance": 5,
                "access_count": 0,
                "last_accessed": now.isoformat(),
                "promoted": "False",
            }],
        )
        return entry_id

    def write_response(self, query: str, response: str, embedding: list[float]) -> str:
        entry_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        content = f"{query}\n{response}"
        self.episodic.add(
            ids=[entry_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "id": entry_id,
                "timestamp": now.isoformat(),
                "source": "self",
                "confidence": 1.0,
                "memory_type": "episodic",
                "tags": json.dumps(["response"]),
                "importance": 5,
                "access_count": 0,
                "last_accessed": now.isoformat(),
                "promoted": "False",
            }],
        )
        return entry_id

    def write_knowledge(self, entry: KnowledgeEntry) -> str:
        if not entry.id:
            entry.id = str(uuid.uuid4())
        embedding = self.embedding_fn(entry.content)
        self.knowledge.add(
            ids=[entry.id],
            embeddings=[embedding],
            documents=[entry.content],
            metadatas=[{
                "id": entry.id,
                "source_ids": json.dumps(entry.source_ids),
                "created": entry.created.isoformat(),
                "updated": entry.updated.isoformat(),
                "status": entry.status,
                "superseded_by": entry.superseded_by or "",
                "supersedes": entry.supersedes or "",
                "confidence": entry.confidence,
                "domain": entry.domain,
                "promotion_count": entry.promotion_count,
            }],
        )
        return entry.id

    def write_candidate(self, memory_ids: list[str]) -> str:
        entry_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        self.candidates.add(
            ids=[entry_id],
            embeddings=[[0.0] * 768],
            documents=[json.dumps(memory_ids)],
            metadatas=[{
                "id": entry_id,
                "cluster_id": "",
                "status": "pending",
                "created": now.isoformat(),
            }],
        )
        return entry_id

    def get_active_knowledge(self, domain: Optional[str] = None) -> list[KnowledgeEntry]:
        all_knowledge = self.knowledge.get(include=["metadatas", "documents"])
        entries = []
        for i in range(len(all_knowledge["ids"])):
            meta = all_knowledge["metadatas"][i]
            if meta.get("status", "active") == "superseded":
                continue
            if domain and meta.get("domain") != domain:
                continue
            entry = KnowledgeEntry(
                id=all_knowledge["ids"][i],
                content=all_knowledge["documents"][i],
                source_ids=json.loads(meta.get("source_ids", "[]")),
                created=datetime.fromisoformat(meta.get("created", datetime.now(timezone.utc).isoformat())),
                updated=datetime.fromisoformat(meta.get("updated", datetime.now(timezone.utc).isoformat())),
                status=meta.get("status", "active"),
                superseded_by=meta.get("superseded_by"),
                supersedes=meta.get("supersedes"),
                confidence=float(meta.get("confidence", 0.0)),
                domain=meta.get("domain", "general"),
                promotion_count=int(meta.get("promotion_count", 1)),
            )
            entries.append(entry)
        return entries

    def supersede_knowledge(self, old_id: str, new_id: str) -> None:
        old = self.knowledge.get(ids=[old_id], include=["metadatas"])
        if not old["ids"]:
            raise ValueError(f"Knowledge entry {old_id} not found")
        new = self.knowledge.get(ids=[new_id], include=["metadatas"])
        if not new["ids"]:
            raise ValueError(f"Knowledge entry {new_id} not found")

        old_meta = old["metadatas"][0]
        old_meta["status"] = "superseded"
        old_meta["superseded_by"] = new_id
        self.knowledge.update(ids=[old_id], metadatas=[old_meta])

        new_meta = new["metadatas"][0]
        new_meta["supersedes"] = old_id
        self.knowledge.update(ids=[new_id], metadatas=[new_meta])

    def get_candidates_for_clustering(self) -> list[CandidateEntry]:
        results = self.candidates.get(include=["metadatas", "documents"])
        entries = []
        for i in range(len(results["ids"])):
            meta = results["metadatas"][i]
            if meta.get("status") == "promoted":
                continue
            entry = CandidateEntry(
                id=results["ids"][i],
                memory_ids=json.loads(results["documents"][i]),
                cluster_id=meta.get("cluster_id") or None,
                status=meta.get("status", "pending"),
                created=datetime.fromisoformat(meta.get("created", datetime.now(timezone.utc).isoformat())),
            )
            entries.append(entry)
        return entries

    def mark_candidate_promoted(self, candidate_id: str) -> None:
        self.candidates.update(ids=[candidate_id], metadatas=[{"status": "promoted"}])

    def cleanup_old_candidates(self, max_age_days: int = 30) -> int:
        results = self.candidates.get(include=["metadatas"])
        now = datetime.now(timezone.utc)
        removed = 0
        for i in range(len(results["ids"])):
            created = datetime.fromisoformat(results["metadatas"][i].get("created", now.isoformat()))
            if (now - created).days > max_age_days:
                self.candidates.delete(ids=[results["ids"][i]])
                removed += 1
        return removed

    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        results = self.episodic.get(ids=[memory_id], include=["metadatas", "documents"])
        if not results["ids"]:
            return None
        meta = results["metadatas"][0]
        return MemoryEntry(
            id=results["ids"][0],
            timestamp=datetime.fromisoformat(meta.get("timestamp", datetime.now(timezone.utc).isoformat())),
            content=results["documents"][0],
            source=meta.get("source", "unknown"),
            confidence=float(meta.get("confidence", 1.0)),
            memory_type=meta.get("memory_type", "episodic"),
            tags=json.loads(meta.get("tags", "[]")),
            importance=int(meta.get("importance", 5)),
            access_count=int(meta.get("access_count", 0)),
            last_accessed=datetime.fromisoformat(meta.get("last_accessed", datetime.now(timezone.utc).isoformat())),
            promoted=meta.get("promoted", "False") == "True",
        )
