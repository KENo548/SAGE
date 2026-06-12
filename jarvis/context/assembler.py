from typing import Protocol

from jarvis.identity.models import Identity, Constitution
from jarvis.memory.schemas import MemoryEntry, KnowledgeEntry


class Tokenizer(Protocol):
    def count(self, text: str) -> int: ...


class WordCountTokenizer:
    multiplier: float = 1.3

    def count(self, text: str) -> int:
        return int(len(text.split()) * self.multiplier)


def assemble_context(
    constitution: Constitution,
    identity: Identity,
    will: str | None,
    memories: list[MemoryEntry],
    knowledge: list[KnowledgeEntry],
    query: str,
    budget: int = 2000,
    tokenizer: Tokenizer = WordCountTokenizer(),
) -> str:
    sections: list[tuple[str, int]] = []

    def add(name: str, text: str) -> None:
        sections.append((name, text))

    constitution_text = _format_constitution(constitution)
    add("constitution", constitution_text)

    soul_text = _format_soul(identity)
    add("soul", soul_text)

    if will:
        add("will", f"<will>\n{will}\n</will>")

    knowledge_text = _format_knowledge(knowledge)
    add("knowledge", knowledge_text)

    memories_text = _format_memories(memories)
    add("memories", memories_text)

    assembled: list[str] = []
    remaining = budget

    priority = {
        "constitution": 0,
        "soul": 1,
        "will": 2,
        "knowledge": 3,
        "memories": 4,
    }
    sections.sort(key=lambda s: priority.get(s[0], 99))

    for name, text in sections:
        tokens = tokenizer.count(text)
        if name in ("constitution", "soul", "will"):
            assembled.append(text)
            remaining -= tokens
        elif remaining >= tokens:
            assembled.append(text)
            remaining -= tokens
        elif name == "knowledge":
            truncated = _truncate_by_tokens(text, remaining, tokenizer)
            if truncated:
                assembled.append(truncated)
            break
        else:
            break

    if query:
        assembled.append(f"<query>\n{query}\n</query>")

    return "\n\n".join(assembled)


def _format_constitution(constitution: Constitution) -> str:
    lines = ["<constitution>"]
    for rule in constitution.core_rules + constitution.safety_rules:
        lines.append(f"  [{rule.id}] Tier {rule.tier} — {rule.description}")
    lines.append("</constitution>")
    return "\n".join(lines)


def _format_soul(identity: Identity) -> str:
    lines = ["<soul>"]
    lines.append(f"  name: {identity.name}")
    lines.append(f"  role: {identity.role}")
    lines.append(f"  purpose: {identity.purpose}")
    if identity.values:
        lines.append("  values:")
        for v in identity.values:
            lines.append(f"    - {v}")
    if identity.limitations:
        lines.append("  limitations:")
        for l in identity.limitations:
            lines.append(f"    - {l}")
    if identity.genesis_text:
        lines.append(f"  genesis: {identity.genesis_text[:200]}")
    lines.append("</soul>")
    return "\n".join(lines)


def _format_knowledge(knowledge: list[KnowledgeEntry]) -> str:
    if not knowledge:
        return ""
    lines = ["<knowledge>"]
    for k in knowledge:
        lines.append(f"  - {k.content}")
    lines.append("</knowledge>")
    return "\n".join(lines)


def _format_memories(memories: list[MemoryEntry]) -> str:
    if not memories:
        return ""
    lines = ["<recent_memories>"]
    for m in memories:
        lines.append(f"  [{m.source}] {m.content[:150]}")
    lines.append("</recent_memories>")
    return "\n".join(lines)


def _truncate_by_tokens(text: str, max_tokens: int, tokenizer: Tokenizer) -> str:
    lines = text.split("\n")
    result: list[str] = []
    for line in lines:
        line_tokens = tokenizer.count(line)
        if sum(tokenizer.count(l) for l in result) + line_tokens <= max_tokens:
            result.append(line)
        else:
            break
    return "\n".join(result)
