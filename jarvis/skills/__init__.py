from typing import Callable, Optional

from jarvis.memory.store import MemoryStore
from jarvis.will.loader import WillLoader
from jarvis.will.models import Will


def maintain_conversation(user_input: str, response: str) -> dict:
    return {"input": user_input, "response": response, "skill": "conversation"}


def summarize(
    text: str,
    llm_generate: Callable[[str, str], str],
    max_words: int = 50,
) -> str:
    system = "You are a precise summarizer. Be concise and accurate."
    prompt = f"Summarize the following in at most {max_words} words:\n\n{text}"
    return llm_generate(system=system, prompt=prompt)


def recall_memory(
    query: str,
    memory_store: MemoryStore,
    top_k: int = 5,
) -> list[dict]:
    results = memory_store.retrieve(query, top_k=top_k, memory_type="episodic")
    return [
        {
            "id": m.id,
            "content": m.content[:200],
            "source": m.source,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in results
    ]


def lookup_knowledge(
    query: str,
    memory_store: MemoryStore,
    top_k: int = 5,
) -> list[dict]:
    results = memory_store.retrieve(query, top_k=top_k, memory_type="knowledge")
    return [
        {
            "id": k.id,
            "content": k.content[:200],
            "domain": k.domain,
            "status": k.status,
        }
        for k in results
    ]


def review_goals(will_loader: WillLoader) -> dict:
    will = will_loader.load()
    return {
        "active_goal": {
            "id": will.active_goal.id,
            "description": will.active_goal.description,
            "priority": will.active_goal.priority,
            "state": will.active_goal.state.value,
        } if will.active_goal else None,
        "current_goals": [
            {
                "id": g.id,
                "description": g.description,
                "priority": g.priority,
                "state": g.state.value,
            }
            for g in will.current_goals
        ],
        "history": [
            {
                "id": g.id,
                "description": g.description,
                "state": g.state.value,
            }
            for g in will.history
        ],
    }
