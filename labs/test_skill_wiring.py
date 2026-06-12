#!/usr/bin/env python3
"""End-to-end skill wiring investigation.

Tests whether the runtime actually writes to / retrieves from
memory and will stores through real LLM interaction.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jarvis.config import load_config
from jarvis.identity.loader import IdentityLoader
from jarvis.governance.engine import GovernanceEngine
from jarvis.memory.store import MemoryStore
from jarvis.llm.client import LLMClient
from jarvis.will.loader import WillLoader
from jarvis.will.manager import GoalManager
from jarvis.will.models import Goal
from jarvis.core.reasoning_loop import ReasoningLoop
from jarvis.skills import recall_memory, lookup_knowledge, review_goals


def _make_embed_fn(config):
    embed = LLMClient(
        base_url=config.models.get("ollama_url", "http://localhost:11434"),
        model=config.models.get("embedding", "nomic-embed-text:latest"),
        timeout=config.llm.get("default_timeout", 120),
    )
    return embed.embed


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
        llm_classify_fn=lambda q: 1,
    )

    embed_fn = _make_embed_fn(config)
    import tempfile
    chroma_path = os.path.join(tempfile.mkdtemp(), "chroma")
    memory_store = MemoryStore(
        chroma_path=chroma_path,
        embedding_fn=embed_fn,
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
        embed_fn=embed_fn,
    ), memory_store, will_loader


def test_memory_recall():
    """Test 1: Tell SAGE a fact, then ask about it."""
    print("=== Test 1: Memory Recall ===")

    loop, store, _ = build_loop()

    # Step 1: Tell SAGE a fact
    print("> Remember: my favorite test color is ultraviolet.")
    r1 = loop.run("Remember this: My favorite test color is ultraviolet.")
    print(f"  Response: {r1.response[:100]}...")
    print(f"  Blocked: {r1.blocked}, memory_id: {r1.memory_id}")

    if r1.blocked:
        print("  FAIL: memory write blocked by governance")
        return False
    if r1.memory_id is None:
        print("  FAIL: memory_id is None - write may not have occurred")
    else:
        print(f"  OK: memory written as {r1.memory_id}")

    # Step 2: Ask about the fact
    print("> What is my favorite test color?")
    r2 = loop.run("What is my favorite test color?")
    print(f"  Response: {r2.response[:200]}")
    print(f"  Blocked: {r2.blocked}")

    # Step 3: Check if retrieval actually found it
    recalled = recall_memory("favorite test color ultraviolet", store)
    print(f"  Direct recall_memory() results: {len(recalled)}")
    for m in recalled:
        print(f"    - {m['content'][:100]}")

    has_color = any("ultraviolet" in m["content"].lower() for m in recalled)
    has_llm = "ultraviolet" in r2.response.lower()

    if has_color:
        print("  PASS: direct memory recall found 'ultraviolet'")
    else:
        print("  FAIL: direct memory recall did NOT find 'ultraviolet'")

    if has_llm:
        print("  PASS: LLM response contains 'ultraviolet'")
    else:
        print("  INFO: LLM response did not contain 'ultraviolet'")

    store.close()
    return has_color


def test_goal_persistence():
    """Test 2: Create a goal, then review goals."""
    print("\n=== Test 2: Goal Persistence ===")

    loop, store, will_loader = build_loop()

    # Step 1: Create a goal via GoalManager directly
    mgr = GoalManager(
        goals=will_loader.load().current_goals if os.path.exists("data/will/goals.yaml") else [],
        active_goal_id=will_loader.load().active_goal.id if (os.path.exists("data/will/goals.yaml") and will_loader.load().active_goal) else None,
    )
    # Simplify: create fresh
    mgr = GoalManager(goals=[], active_goal_id=None)
    goal_id = "bocconi"
    mgr.create(Goal(id=goal_id, description="Prepare for Bocconi admissions", priority="high"))
    mgr.activate(goal_id)
    will_loader.save_manager(mgr)
    print(f"  Goal '{goal_id}' created and saved.")

    # Step 2: Reload and check
    loaded_will = will_loader.load()
    active = loaded_will.active_goal
    if active and "bocconi" in active.description.lower():
        print(f"  PASS: loaded active goal = '{active.description}'")
    else:
        print(f"  FAIL: active goal not found or wrong. Got: {active}")

    # Step 3: Use the runtime
    r3 = loop.run("Review my goals. What should I be working on?")
    print(f"  LLM response: {r3.response[:200]}")
    print(f"  Blocked: {r3.blocked}")

    # Step 4: Check via review_goals skill
    reviewed = review_goals(will_loader)
    has_bocconi = any("bocconi" in g["description"].lower() for g in reviewed["current_goals"])
    if has_bocconi:
        print("  PASS: review_goals() returned the goal")
    else:
        print("  FAIL: review_goals() did not return the goal")

    store.close()
    return has_bocconi


def test_conversation():
    """Test 3: Basic conversation works."""
    print("\n=== Test 3: Conversation ===")

    loop, store, _ = build_loop()

    r = loop.run("Say hello and introduce yourself briefly.")
    print(f"  Response: {r.response[:200]}")
    print(f"  Blocked: {r.blocked}, tier={r.tier}")

    store.close()
    return not r.blocked and len(r.response) > 0


def main():
    results = {}
    results["conversation"] = test_conversation()
    results["memory_recall"] = test_memory_recall()
    results["goal_persistence"] = test_goal_persistence()

    print("\n" + "=" * 50)
    print("RESULTS")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")

    if all(results.values()):
        print("\nAll skills wired correctly through runtime.")
        return 0
    else:
        print("\nSome skills NOT wired correctly.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
