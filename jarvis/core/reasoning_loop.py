import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import chromadb
import requests

from jarvis.config import Config
from jarvis.context.assembler import assemble_context
from jarvis.governance.engine import GovernanceEngine
from jarvis.identity.loader import IdentityLoader
from jarvis.identity.models import Identity
from jarvis.llm.client import LLMClient
from jarvis.memory.store import MemoryStore
from jarvis.memory.schemas import KnowledgeEntry
from jarvis.promotion.pipeline import run_promotion_pipeline
from jarvis.will.loader import WillLoader


class HaltReason(Exception):
    pass


@dataclass
class ValidationReport:
    passed: bool = False
    config_ok: bool = False
    identity_files_ok: bool = False
    constitution_files_ok: bool = False
    memory_store_accessible: bool = False
    model_available: bool = False
    message: str = ""


@dataclass
class ReasoningTrace:
    steps: dict = field(default_factory=dict)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None


@dataclass
class ReasoningResult:
    response: str
    tier: int
    blocked: bool
    memory_id: Optional[str] = None
    candidate_id: Optional[str] = None
    trace: Optional[ReasoningTrace] = None


REQUIRED_IDENTITY_FILES = ["identity.yaml", "genesis.md", "personality.yaml"]
REQUIRED_CONSTITUTION_FILES = ["constitution.yaml"]


class ReasoningLoop:
    def __init__(
        self,
        config: Config,
        identity_loader: IdentityLoader,
        governance_engine: GovernanceEngine,
        will_loader: WillLoader,
        memory_store: MemoryStore,
        llm_client: LLMClient,
    ) -> None:
        self.config = config
        self.identity_loader = identity_loader
        self.governance_engine = governance_engine
        self.will_loader = will_loader
        self.memory_store = memory_store
        self.llm_client = llm_client

    def run(self, user_input: str) -> ReasoningResult:
        trace = ReasoningTrace()

        report = self._validate_runtime()
        trace.steps["0_runtime_validation"] = report.message
        if not report.passed:
            trace.end_time = datetime.now(timezone.utc)
            return ReasoningResult(
                response=f"Safe halt: {report.message}",
                tier=0, blocked=True, trace=trace,
            )

        constitution = self._load_constitution_safe()
        trace.steps["1_constitution_load"] = len(constitution.core_rules) + len(constitution.safety_rules)

        tier = self.governance_engine.classify(user_input)
        trace.steps["2_governance_pre"] = tier
        if tier == 3:
            trace.end_time = datetime.now(timezone.utc)
            return ReasoningResult(
                response="I cannot process this request. It violates my constitutional rules.",
                tier=3, blocked=True, trace=trace,
            )

        identity = self.identity_loader.load()
        trace.steps["3_soul_load"] = identity.name

        will = self.will_loader.load()
        trace.steps["4_will_load"] = len(will.current_goals)

        memories = self._retrieve_memories(user_input)
        trace.steps["5_memory_retrieval"] = len(memories)

        knowledge = self._retrieve_knowledge(user_input)
        trace.steps["6_knowledge_retrieval"] = len(knowledge)

        context = assemble_context(
            constitution=constitution,
            identity=identity,
            will=will,
            memories=memories,
            knowledge=knowledge,
            query=user_input,
            budget=self.config.context.get("default_budget", 2000),
        )
        trace.steps["7_context_assembly"] = len(context)

        system_prompt = self._build_system_prompt(identity)
        response = self.llm_client.generate(
            system=system_prompt,
            prompt=context,
            temperature=self.config.llm.get("temperature", 0.7),
        )
        trace.steps["8_llm_generation"] = len(response.split())

        response_tier = self.governance_engine.classify(response)
        trace.steps["9_governance_post"] = response_tier
        if response_tier == 3:
            trace.end_time = datetime.now(timezone.utc)
            return ReasoningResult(
                response="I cannot emit that response. It violates my constitutional rules.",
                tier=3, blocked=True, trace=trace,
            )

        mem_id = None
        candidate_id = None
        try:
            response_embedding = self.llm_client.embed(f"{user_input}\n{response}")
            mem_id = self.memory_store.write_response(user_input, response, response_embedding)
            trace.steps["11_memory_write"] = mem_id
            candidate_id = self.memory_store.write_candidate(memory_ids=[mem_id])
            trace.steps["12_candidate_eligible"] = candidate_id
        except Exception as e:
            trace.steps["11_memory_write"] = f"failed ({e})"

        trace.end_time = datetime.now(timezone.utc)
        return ReasoningResult(
            response=response,
            tier=tier,
            blocked=False,
            memory_id=mem_id,
            candidate_id=candidate_id,
            trace=trace,
        )

    def end_session(self) -> list[KnowledgeEntry]:
        return run_promotion_pipeline(
            store=self.memory_store,
            embedding_fn=self.llm_client.embed,
            threshold=self.config.promotion.get("threshold", 0.65),
            min_cluster_size=self.config.promotion.get("min_cluster_size", 3),
        )

    def _validate_runtime(self) -> ValidationReport:
        report = ValidationReport()

        report.config_ok = os.path.exists("configs/config.yaml")

        soul_dir = self.config.identity.get("soul_path", "data/soul")
        const_dir = self.config.identity.get("constitution_path", "data/constitution")
        report.identity_files_ok = all(
            os.path.exists(os.path.join(soul_dir, f))
            for f in REQUIRED_IDENTITY_FILES
        )
        report.constitution_files_ok = all(
            os.path.exists(os.path.join(const_dir, f))
            for f in REQUIRED_CONSTITUTION_FILES
        )

        try:
            chroma_path = self.config.memory.get("chroma_db_path", "data/chroma_db")
            _ = chromadb.PersistentClient(path=chroma_path)
            report.memory_store_accessible = True
        except Exception:
            report.memory_store_accessible = False

        try:
            url = self.config.models.get("ollama_url", "http://localhost:11434")
            r = requests.get(f"{url}/api/tags", timeout=5)
            report.model_available = r.status_code == 200
        except Exception:
            report.model_available = False

        report.passed = all([
            report.config_ok,
            report.identity_files_ok,
            report.constitution_files_ok,
        ])
        if not report.passed:
            failures = []
            if not report.config_ok:
                failures.append("config")
            if not report.identity_files_ok:
                failures.append("identity_files")
            if not report.constitution_files_ok:
                failures.append("constitution_files")
            report.message = f"validation failed: {', '.join(failures)}"
        else:
            notes = []
            if not report.memory_store_accessible:
                notes.append("memory store degraded")
            if not report.model_available:
                notes.append("model unavailable")
            report.message = f"pass ({', '.join(notes)})" if notes else "pass"

        return report

    def _load_constitution_safe(self):
        try:
            return self.identity_loader.load_constitution()
        except FileNotFoundError:
            raise HaltReason("Constitution files missing — cannot operate without governance")

    def _retrieve_memories(self, query: str) -> list:
        if not self._memory_available():
            return []
        try:
            return self.memory_store.retrieve(
                query, top_k=self.config.memory.get("retrieval", {}).get("top_k_episodic", 5),
                memory_type="episodic",
            )
        except Exception:
            return []

    def _retrieve_knowledge(self, query: str) -> list:
        if not self._memory_available():
            return []
        try:
            return self.memory_store.retrieve(
                query, top_k=self.config.memory.get("retrieval", {}).get("top_k_knowledge", 5),
                memory_type="knowledge",
            )
        except Exception:
            return []

    def _memory_available(self) -> bool:
        try:
            chroma_path = self.config.memory.get("chroma_db_path", "data/chroma_db")
            client = chromadb.PersistentClient(path=chroma_path)
            client.heartbeat()
            return True
        except Exception:
            return False

    def _build_system_prompt(self, identity: Identity) -> str:
        return (
            f"You are {identity.name}, a portable cognitive entity.\n"
            f"Role: {identity.role}\n"
            f"Purpose: {identity.purpose}\n"
            f"You assist your user with memory, goals, and knowledge.\n"
            f"Constitution: Never claim to be human. Never modify your own identity files, constitution, or memory stores. Never assist with harmful acts. Never deceive.\n"
            f"Be concise, direct, and honest. Stay in character. Do not speculate or roleplay beyond your stated identity."
        )
