import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional

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
from jarvis.capabilities import (
    CapabilityLog,
    RuntimeContext,
    get_capability,
    match_shortcut,
)
from jarvis.promotion.pipeline import run_promotion_pipeline
from jarvis.will.loader import WillLoader
from jarvis.will.models import Will


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
    from_shortcut: bool = False
    capability_id: str = ""


REQUIRED_IDENTITY_FILES = ["identity.yaml", "genesis.md", "personality.yaml", "soul.yaml"]
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
        embed_fn: Optional[Callable[[str], list[float]]] = None,
    ) -> None:
        self.config = config
        self.identity_loader = identity_loader
        self.governance_engine = governance_engine
        self.will_loader = will_loader
        self.memory_store = memory_store
        self.llm_client = llm_client
        self.embed_fn = embed_fn or llm_client.embed
        self._cached_identity: Optional[Identity] = None
        self._cached_will: Optional[Will] = None
        self._ollama_verified_at: Optional[float] = None
        self._gov_post_pattern_hits = 0
        self._gov_post_tier3_matches = 0
        self._gov_post_tier2_matches = 0
        self._gov_post_blocks = 0

    def _get_identity(self) -> Identity:
        if self._cached_identity is None:
            self._cached_identity = self.identity_loader.load()
        return self._cached_identity

    def _get_will(self) -> Will:
        if self._cached_will is None:
            self._cached_will = self.will_loader.load()
        return self._cached_will

    def run(self, user_input: str) -> ReasoningResult:
        trace = ReasoningTrace()
        llm_generate_fn = lambda s, p: self.llm_client.generate(
            system=s, prompt=p,
            temperature=self.config.llm.get("temperature", 0.7),
        )

        t_start = time.perf_counter()
        report = self._validate_runtime()
        trace.steps["0_runtime_validation"] = report.message
        trace.steps["t0_validation_ms"] = int((time.perf_counter() - t_start) * 1000)
        if not report.passed:
            trace.end_time = datetime.now(timezone.utc)
            return ReasoningResult(
                response=f"Safe halt: {report.message}",
                tier=0, blocked=True, trace=trace,
            )

        # ── Common prelude: constitution (needed for governance) ──
        t1 = time.perf_counter()
        constitution = self._load_constitution_safe()
        trace.steps["1_constitution_load"] = len(constitution.core_rules) + len(constitution.safety_rules)
        trace.steps["t1_constitution_ms"] = int((time.perf_counter() - t1) * 1000)

        t2 = time.perf_counter()
        tier = self.governance_engine.classify(user_input)
        trace.steps["2_governance_pre"] = tier
        trace.steps["t2_governance_ms"] = int((time.perf_counter() - t2) * 1000)
        if tier == 3:
            trace.end_time = datetime.now(timezone.utc)
            return ReasoningResult(
                response="I cannot process this request. It violates my constitutional rules.",
                tier=3, blocked=True, trace=trace,
            )

        # ── Check shortcut early, BEFORE expensive identity/will loads ──
        t5 = time.perf_counter()
        cap_id = match_shortcut(user_input)
        trace.steps["5_capability_shortcut"] = cap_id or "none"
        trace.steps["t5_shortcut_ms"] = int((time.perf_counter() - t5) * 1000)

        cap_result = None
        if cap_id:
            cap = get_capability(cap_id)
            if cap:
                ctx = RuntimeContext(
                    user_input=user_input,
                    memory_store=self.memory_store,
                    will_loader=self.will_loader,
                    llm_client=self.llm_client,
                    llm_generate=llm_generate_fn,
                    config=self.config,
                    identity=self._get_identity(),
                )
                t8 = time.perf_counter()
                cap_result = cap.execute(ctx)
                duration = int((time.perf_counter() - t8) * 1000)
                cap_result.duration_ms = duration
                trace.steps["8_capability_execution"] = duration
                # skip memory/knowledge (not needed for capabilities)
                trace.steps["6_memory_retrieval"] = 0
                trace.steps["t6_memory_ms"] = 0
                trace.steps["7_knowledge_retrieval"] = 0
                trace.steps["t7_knowledge_ms"] = 0
                # skip soul/will loads (capabilities load what they need)
                trace.steps["3_soul_load"] = "skipped"
                trace.steps["t3_soul_ms"] = 0
                trace.steps["4_will_load"] = "skipped"
                trace.steps["t4_will_ms"] = 0
            else:
                cap_result = None

        if cap_result is None:
            # ── Full reasoning path: identity, will, memory, context, LLM ──
            t3 = time.perf_counter()
            identity = self._get_identity()
            trace.steps["3_soul_load"] = identity.name
            trace.steps["t3_soul_ms"] = int((time.perf_counter() - t3) * 1000)

            t4 = time.perf_counter()
            will = self._get_will()
            trace.steps["4_will_load"] = len(will.current_goals)
            trace.steps["t4_will_ms"] = int((time.perf_counter() - t4) * 1000)

            t6 = time.perf_counter()
            memories = self._retrieve_memories(user_input)
            trace.steps["6_memory_retrieval"] = len(memories)
            trace.steps["t6_memory_ms"] = int((time.perf_counter() - t6) * 1000)

            t7 = time.perf_counter()
            knowledge = self._retrieve_knowledge(user_input)
            trace.steps["7_knowledge_retrieval"] = len(knowledge)
            trace.steps["t7_knowledge_ms"] = int((time.perf_counter() - t7) * 1000)

            t9 = time.perf_counter()
            context = assemble_context(
                constitution=constitution,
                identity=identity,
                will=will,
                memories=memories,
                knowledge=knowledge,
                query=user_input,
                budget=self.config.context.get("default_budget", 2000),
            )
            trace.steps["9_context_assembly"] = len(context)
            trace.steps["t9_context_ms"] = int((time.perf_counter() - t9) * 1000)

            t10 = time.perf_counter()
            system_prompt = self._build_system_prompt(identity)
            sys_tokens = len(system_prompt.split())
            print(f"  [system] {sys_tokens}tokens (word-estimate)")
            gen_result = self.llm_client.generate_detailed(
                system=system_prompt,
                prompt=context,
                temperature=self.config.llm.get("temperature", 0.7),
            )
            response = gen_result.response
            trace.steps["10_llm_generation"] = len(response.split())
            trace.steps["t10_llm_ms"] = int((time.perf_counter() - t10) * 1000)
            ptok = gen_result.prompt_tokens
            rtok = gen_result.response_tokens
            tps = gen_result.tokens_per_second
            print(f"  [llm] prompt={ptok}tokens response={rtok}tokens {tps:.1f}tok/s")
        else:
            response = cap_result.output

        # ── Post-generation governance (deterministic only, no LLM call) ──
        t11 = time.perf_counter()
        response_tier = self.governance_engine.classify_deterministic(response)
        gov_path = self.governance_engine.last_path
        blocked = response_tier == 3
        self._gov_post_pattern_hits += 1
        if response_tier == 3:
            self._gov_post_tier3_matches += 1
        elif response_tier == 2:
            self._gov_post_tier2_matches += 1
        if blocked:
            self._gov_post_blocks += 1
        trace.steps["11_governance_post"] = response_tier
        trace.steps["t11_gov_post_ms"] = int((time.perf_counter() - t11) * 1000)
        print(f"  [gov_post] path={gov_path} tier={response_tier} blocked={blocked}")
        if blocked:
            trace.end_time = datetime.now(timezone.utc)
            return ReasoningResult(
                response="I cannot emit that response. It violates my constitutional rules.",
                tier=3, blocked=True, trace=trace,
            )

        mem_id = None
        candidate_id = None
        try:
            t_embed = time.perf_counter()
            response_embedding = self.embed_fn(f"{user_input}\n{response}")
            embed_ms = int((time.perf_counter() - t_embed) * 1000)
            t_write = time.perf_counter()
            mem_id = self.memory_store.write_response(user_input, response, response_embedding)
            write_ms = int((time.perf_counter() - t_write) * 1000)
            trace.steps["12_memory_write"] = mem_id
            t_cand = time.perf_counter()
            candidate_id = self.memory_store.write_candidate(memory_ids=[mem_id])
            cand_ms = int((time.perf_counter() - t_cand) * 1000)
            trace.steps["13_candidate_eligible"] = candidate_id
            trace.steps["t12_memory_ms"] = embed_ms + write_ms + cand_ms
            print(f"  [mem_write] embed={embed_ms}ms write_response={write_ms}ms write_candidate={cand_ms}ms")
        except Exception as e:
            trace.steps["12_memory_write"] = f"failed ({e})"
            trace.steps["t12_memory_ms"] = -1

        if cap_result:
            capability_log = CapabilityLog()
            capability_log.write(
                capability_id=cap_result.capability_id,
                user_input=user_input,
                success=cap_result.success,
                duration_ms=cap_result.duration_ms,
                tier=response_tier,
            )
            trace.steps["14_capability_log"] = cap_result.capability_id

        trace.end_time = datetime.now(timezone.utc)
        trace.steps["t_total_ms"] = int((time.perf_counter() - t_start) * 1000)
        print(f"  [RUNTIME] validation={trace.steps.get('t0_validation_ms','?')}ms "
              f"gov={trace.steps.get('t2_governance_ms','?')}ms "
              f"soul={trace.steps.get('t3_soul_ms','?')}ms "
              f"will={trace.steps.get('t4_will_ms','?')}ms "
              f"shortcut={trace.steps.get('t5_shortcut_ms','?')}ms "
              f"memory={trace.steps.get('t6_memory_ms','?')}ms "
              f"knowledge={trace.steps.get('t7_knowledge_ms','?')}ms "
              f"cap_exec={trace.steps.get('8_capability_execution','?')}ms "
              f"llm_gen={trace.steps.get('t10_llm_ms','?')}ms "
              f"gov_post={trace.steps.get('t11_gov_post_ms','?')}ms "
              f"mem_write={trace.steps.get('t12_memory_ms','?')}ms "
              f"total={trace.steps.get('t_total_ms','?')}ms")

        cap_id_out = cap_result.capability_id if cap_result else ""
        return ReasoningResult(
            response=response,
            tier=tier,
            blocked=False,
            memory_id=mem_id,
            candidate_id=candidate_id,
            trace=trace,
            from_shortcut=cap_result is not None,
            capability_id=cap_id_out,
        )

    def end_session(self) -> list[KnowledgeEntry]:
        if self._gov_post_pattern_hits > 0:
            print(f"  [gov_post stats] checks={self._gov_post_pattern_hits} "
                  f"tier3={self._gov_post_tier3_matches} "
                  f"tier2={self._gov_post_tier2_matches} "
                  f"blocks={self._gov_post_blocks}")
        try:
            return run_promotion_pipeline(
                store=self.memory_store,
                embedding_fn=self.embed_fn,
                threshold=self.config.promotion.get("threshold", 0.65),
                min_cluster_size=self.config.promotion.get("min_cluster_size", 3),
            )
        except Exception as exc:
            print(f"  [end_session] promotion pipeline failed (non-fatal): {exc}")
            return []

    def _validate_runtime(self) -> ValidationReport:
        report = ValidationReport()
        diag: dict[str, float] = {}

        t0 = time.perf_counter()
        report.config_ok = os.path.exists("configs/config.yaml")
        diag["config"] = (time.perf_counter() - t0) * 1000

        soul_dir = self.config.identity.get("soul_path", "data/soul")
        const_dir = self.config.identity.get("constitution_path", "data/constitution")
        t1 = time.perf_counter()
        report.identity_files_ok = all(
            os.path.exists(os.path.join(soul_dir, f))
            for f in REQUIRED_IDENTITY_FILES
        )
        diag["identity_files"] = (time.perf_counter() - t1) * 1000

        t2 = time.perf_counter()
        report.constitution_files_ok = all(
            os.path.exists(os.path.join(const_dir, f))
            for f in REQUIRED_CONSTITUTION_FILES
        )
        diag["const_files"] = (time.perf_counter() - t2) * 1000

        t3 = time.perf_counter()
        try:
            chroma_path = self.config.memory.get("chroma_db_path", "data/chroma_db")
            _ = chromadb.PersistentClient(path=chroma_path)
            report.memory_store_accessible = True
        except Exception:
            report.memory_store_accessible = False
        diag["chroma_client"] = (time.perf_counter() - t3) * 1000

        t4 = time.perf_counter()
        now = time.monotonic()
        if self._ollama_verified_at is not None and now - self._ollama_verified_at < 300:
            report.model_available = True
            diag["ollama_ping"] = 0.0
        else:
            try:
                url = self.config.models.get("ollama_url", "http://localhost:11434")
                r = requests.get(f"{url}/api/tags", timeout=5)
                report.model_available = r.status_code == 200
                if report.model_available:
                    self._ollama_verified_at = now
            except Exception:
                self._ollama_verified_at = None
                report.model_available = False
            diag["ollama_ping"] = (time.perf_counter() - t4) * 1000

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

        print(f"  [validate] config={diag['config']:.0f}ms id_files={diag['identity_files']:.0f}ms "
              f"const_files={diag['const_files']:.0f}ms chroma={diag['chroma_client']:.0f}ms "
              f"ollama={diag['ollama_ping']:.0f}ms")
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
        parts = [
            f"You are {identity.name}.",
            "You already know who you are. Do not repeatedly describe your identity, purpose, architecture, capabilities, or cognitive nature unless directly asked.",
            "In normal conversation, respond naturally as a trusted assistant and advisor.",
            "Speak briefly and conversationally. Use short sentences. This is a spoken conversation, not a written document.",
            "Never use lists, bullet points, numbered items, bold, asterisks, markdown, or any formatted text in your responses.",
            "Be direct and natural. Say 'I'm good' not 'I am functioning within normal parameters.' Say 'Sure' not 'Certainly, I would be happy to assist.'",
            "Constitution: Never claim to be human. Never modify your own identity files, constitution, or memory stores. Never assist with harmful acts. Never deceive.",
        ]

        cb = identity.conversation_behavior
        if cb:
            greeting = cb.get("greeting")
            if greeting:
                parts.append(f"Greetings should be {greeting}.")
            casual = cb.get("casual_conversation")
            if casual:
                parts.append("Keep conversation casual and natural.")
            identity_expl = cb.get("identity_explanations")
            if identity_expl:
                parts.append(f"Explain your identity only {identity_expl}.")
            avoid = cb.get("avoid", [])
            if avoid:
                avoid_str = "; ".join(avoid).replace("_", " ")
                parts.append(f"Avoid: {avoid_str}.")

        return "\n".join(parts)
