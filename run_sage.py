#!/usr/bin/env python3
"""SAGE daily-use CLI — interactive cognitive session.

Usage:
    python run_sage.py              # interactive session
    python run_sage.py one-shot     # single prompt

Commands (inside session):
    /goals        — review current goals
    /memory <q>   — recall memories about <q>
    /knowledge <q>— lookup knowledge about <q>
    /status       — show session stats
    /reset        — clear conversation context
    /end          — end session, run promotion, exit
"""

import os
import sys
import signal
from datetime import datetime, timezone

from jarvis.config import load_config
from jarvis.identity.loader import IdentityLoader
from jarvis.governance.engine import GovernanceEngine
from jarvis.memory.store import MemoryStore
from jarvis.llm.client import LLMClient
from jarvis.will.loader import WillLoader
from jarvis.core.reasoning_loop import ReasoningLoop, HaltReason
from jarvis.skills import recall_memory, lookup_knowledge, review_goals


SESSION_LOG = "data/sessions.log"


def log_session(user: str, response: str, blocked: bool, elapsed: float):
    line = (
        f"{datetime.now(timezone.utc).isoformat()} | "
        f"BLOCKED={blocked} | {elapsed:.2f}s | "
        f"U: {user[:80]} | S: {response[:80]}"
    )
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _make_embed_fn(config):
    embed_client = LLMClient(
        base_url=config.models.get("ollama_url", "http://localhost:11434"),
        model=config.models.get("embedding", "nomic-embed-text:latest"),
        timeout=config.llm.get("default_timeout", 120),
    )
    return embed_client.embed


def build_loop():
    config = load_config("configs/config.yaml")
    ollama_url = config.models.get("ollama_url", "http://localhost:11434")
    model = config.models.get("primary", "llama3.2:latest")
    timeout = config.llm.get("default_timeout", 120)

    identity_loader = IdentityLoader(
        soul_path=config.identity.get("soul_path", "data/soul"),
        constitution_path=config.identity.get("constitution_path", "data/constitution"),
    )

    governance_llm = LLMClient(base_url=ollama_url, model=model, timeout=timeout)
    governance_engine = GovernanceEngine(
        constitution=identity_loader.load_constitution(),
        llm_classify_fn=governance_llm.classify,
    )
    memory_store = MemoryStore(
        chroma_path=config.memory.get("chroma_db_path", "data/chroma_db"),
        embedding_fn=_make_embed_fn(config),
    )
    will_loader = WillLoader("data/will/goals.yaml")
    llm_client = LLMClient(base_url=ollama_url, model=model, timeout=timeout)

    return ReasoningLoop(
        config=config,
        identity_loader=identity_loader,
        governance_engine=governance_engine,
        will_loader=will_loader,
        memory_store=memory_store,
        llm_client=llm_client,
    )


def handle_command(cmd: str, loop: ReasoningLoop) -> bool:
    parts = cmd.strip().split(maxsplit=1)
    verb = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if verb == "/end":
        print("\nEnding session and running promotion pipeline...")
        promoted = loop.end_session()
        print(f"Promoted {len(promoted)} knowledge items.")
        return False

    if verb == "/goals":
        result = review_goals(loop.will_loader)
        if result["active_goal"]:
            g = result["active_goal"]
            print(f"\nActive goal: {g['description']} (priority={g['priority']}, state={g['state']})")
        else:
            print("\nNo active goal.")
        print(f"Current goals ({len(result['current_goals'])}):")
        for g in result["current_goals"]:
            print(f"  [{g['state']}] {g['description']} (priority={g['priority']})")
        return True

    if verb == "/memory":
        if not arg:
            print("Usage: /memory <query>")
            return True
        results = recall_memory(arg, loop.memory_store)
        if not results:
            print("No memories found.")
        else:
            print(f"\nMemories ({len(results)}):")
            for m in results:
                print(f"  [{m['source']}] {m['content']}")
        return True

    if verb == "/knowledge":
        if not arg:
            print("Usage: /knowledge <query>")
            return True
        results = lookup_knowledge(arg, loop.memory_store)
        if not results:
            print("No knowledge found.")
        else:
            print(f"\nKnowledge ({len(results)}):")
            for k in results:
                print(f"  [{k['domain']}] {k['content']}")
        return True

    if verb == "/status":
        report = loop._validate_runtime()
        print(f"\nRuntime status: {report.message}")
        print(f"  Config:        [{'OK' if report.config_ok else 'FAIL'}]")
        print(f"  Identity files: [{'OK' if report.identity_files_ok else 'FAIL'}]")
        print(f"  Constitution:   [{'OK' if report.constitution_files_ok else 'FAIL'}]")
        print(f"  Memory store:   [{'OK' if report.memory_store_accessible else 'FAIL'}]")
        print(f"  Model:          [{'OK' if report.model_available else 'FAIL'}]")
        return True

    if verb == "/reset":
        print("\nConversation context reset (session continues).")
        return True

    print(f"Unknown command: {verb}")
    print("Commands: /goals /memory <q> /knowledge <q> /status /reset /end")
    return True


def interactive():
    print("SAGE - Interactive Session")
    print("=" * 40)
    print("Commands: /goals /memory <q> /knowledge <q> /status /reset /end")
    print()

    loop = build_loop()

    report = loop._validate_runtime()
    if not report.passed:
        print(f"ERROR: {report.message}")
        sys.exit(1)

    print(f"Runtime: {report.message}\n")

    running = True
    while running:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            running = handle_command(user_input, loop)
            continue

        t0 = datetime.now(timezone.utc)
        result = loop.run(user_input)
        elapsed = (datetime.now(timezone.utc) - t0).total_seconds()

        log_session(user_input, result.response, result.blocked, elapsed)

        if result.blocked:
            print(f"\n[BLOCKED] {result.response}")
        else:
            print(f"\n{result.response}")

        if result.trace:
            print(f"\n  [{result.trace.steps.get('8_llm_generation', '?')} words, "
                  f"tier={result.tier}]")

    print("\nEnding session...")
    promoted = loop.end_session()
    print(f"Promoted {len(promoted)} items. Goodbye.")


def one_shot():
    if len(sys.argv) < 2:
        print("Usage: python run_sage.py one-shot <prompt>")
        sys.exit(1)

    loop = build_loop()
    report = loop._validate_runtime()
    if not report.passed:
        print(f"ERROR: {report.message}")
        sys.exit(1)

    prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read().strip()
    if not prompt:
        print("No prompt provided.")
        sys.exit(1)

    t0 = datetime.now(timezone.utc)
    result = loop.run(prompt)
    elapsed = (datetime.now(timezone.utc) - t0).total_seconds()

    log_session(prompt, result.response, result.blocked, elapsed)
    print(result.response)
    print(f"\n[{elapsed:.2f}s, tier={result.tier}, blocked={result.blocked}]")


def main():
    os.makedirs("data", exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == "one-shot":
        one_shot()
    else:
        interactive()


if __name__ == "__main__":
    main()
