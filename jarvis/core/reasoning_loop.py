import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional

from jarvis.config import Config
from jarvis.context.assembler import assemble_context
from jarvis.governance.engine import GovernanceEngine
from jarvis.identity.loader import IdentityLoader
from jarvis.identity.models import Identity, Constitution
from jarvis.llm.client import LLMClient
from jarvis.memory.store import MemoryStore
from jarvis.memory.schemas import MemoryEntry, KnowledgeEntry
from jarvis.promotion.pipeline import run_promotion_pipeline
from jarvis.will.loader import WillLoader
from jarvis.will.models import Will


REQUIRED_RUNTIME_PATHS = [
    "data/soul/identity.yaml",
    "data/soul/genesis.md",
    "data/constitution/constitution.yaml",
    "data/will/goals.yaml",
    "configs/config.yaml",
]


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


class ReasoningLoop:
    def __init__(
        self,
        config: Config,
        identity_loader: IdentityLoader,
        governance_engine: GovernanceEngine,
        will_loader: WillLoader,
        memory_store: MemoryStore,
        llm_client: LLMClient,
        runtime_paths: Optional[list[str]] = None,
    ) -> None:
        self.config = config
        self.identity_loader = identity_loader
        self.governance_engine = governance_engine
        self.will_loader = will_loader
        self.memory_store = memory_store
        self.llm_client = llm_client
        self.runtime_paths = runtime_paths or list(REQUIRED_RUNTIME_PATHS)

    def run(self, user_input: str) -> ReasoningResult:
        trace = ReasoningTrace()

        runtime_ok, runtime_msg = self._runtime_validation()
        trace.steps["0_runtime_validation"] = runtime_msg

        constitution = self.identity_loader.load_constitution()
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

        query_embedding = self.llm_client.embed(user_input)
        memories = self.memory_store.retrieve(user_input, top_k=5, memory_type="episodic")
        trace.steps["5_memory_retrieval"] = len(memories)

        knowledge = self.memory_store.retrieve(user_input, top_k=10, memory_type="knowledge")
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

        response_embedding = self.llm_client.embed(f"{user_input}\n{response}")
        mem_id = self.memory_store.write_response(user_input, response, response_embedding)
        trace.steps["11_memory_write"] = mem_id

        candidate_id = self.memory_store.write_candidate(memory_ids=[mem_id])
        trace.steps["12_candidate_eligible"] = candidate_id

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
            llm_summarize_fn=self.llm_client.generate if hasattr(self.llm_client, 'generate') else None,
        )

    def _runtime_validation(self) -> tuple[bool, str]:
        missing = [p for p in self.runtime_paths if not os.path.exists(p)]
        if missing:
            return False, f"Missing paths: {missing}"
        return True, "all paths ok"

    def _build_system_prompt(self, identity: Identity) -> str:
        return (
            f"You are {identity.name}, a portable cognitive entity.\n"
            f"Role: {identity.role}\n"
            f"Purpose: {identity.purpose}\n"
            f"You assist your user with memory, goals, and knowledge.\n"
            f"Always follow the constitution. Never claim to be human.\n"
            f"Be honest, direct, and helpful."
        )
