from typing import Protocol

from jarvis.identity.models import Identity, Constitution
from jarvis.memory.schemas import MemoryEntry, KnowledgeEntry
from jarvis.will.models import Will


class Tokenizer(Protocol):
    def count(self, text: str) -> int: ...


class WordCountTokenizer:
    multiplier: float = 0.7

    def count(self, text: str) -> int:
        return int(len(text.split()) * self.multiplier)


def _token_counts(
    constitution: Constitution,
    identity: Identity,
    will: Will | None,
    memories: list[MemoryEntry],
    knowledge: list[KnowledgeEntry],
    query: str,
    tokenizer: Tokenizer,
) -> dict[str, int]:
    """Measure per-section token counts without rendering into context."""
    counts = {}
    counts["constitution"] = tokenizer.count(_format_constitution(constitution))
    counts["soul"] = tokenizer.count(_format_soul(identity))
    counts["genesis"] = tokenizer.count(identity.genesis_text)
    counts["personality"] = tokenizer.count(_format_personality(identity))
    counts["will"] = tokenizer.count(_format_will(will)) if will else 0
    counts["knowledge"] = tokenizer.count(_format_knowledge(knowledge))
    counts["memories"] = tokenizer.count(_format_memories(memories))
    counts["query"] = tokenizer.count(query)
    counts["total"] = sum(counts.values())
    parts = [f"{k}={v}tokens" for k, v in counts.items()]
    print("  [context] " + " ".join(parts))
    return counts


def assemble_context(
    constitution: Constitution,
    identity: Identity,
    will: Will | None,
    memories: list[MemoryEntry],
    knowledge: list[KnowledgeEntry],
    query: str,
    budget: int = 2000,
    tokenizer: Tokenizer = WordCountTokenizer(),
) -> str:
    _token_counts(constitution, identity, will, memories, knowledge, query, tokenizer)

    sections: list[tuple[str, str]] = []

    def add(name: str, text: str) -> None:
        sections.append((name, text))

    constitution_text = _format_constitution(constitution)
    add("constitution", constitution_text)

    soul_text = _format_soul(identity)
    add("soul", soul_text)

    if will:
        add("will", _format_will(will))

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


def _format_personality(identity: Identity) -> str:
    lines = ["<personality>"]
    if identity.personality_style:
        for k, v in identity.personality_style.items():
            lines.append(f"  {k}: {v}")
    if identity.traits:
        lines.append("  traits:")
        for k, v in identity.traits.items():
            lines.append(f"    {k}: {v}")
    if identity.quirks:
        lines.append("  quirks:")
        for q in identity.quirks:
            lines.append(f"    - {q}")
    if identity.values:
        lines.append("  values:")
        for v in identity.values:
            lines.append(f"    - {v}")
    if identity.limitations:
        lines.append("  limitations:")
        for l in identity.limitations:
            lines.append(f"    - {l}")
    lines.append("</personality>")
    return "\n".join(lines)


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

    soul = identity.soul

    if soul:
        values = soul.get("core_values", {})
        if values:
            lines.append("  core_values:")
            for vid, vdata in values.items():
                desc = vdata.get("description", "")
                lines.append(f"    {vid}: {desc}")

        principles = soul.get("behavioral_principles", {})
        if principles:
            lines.append("  behavioral_principles:")
            for pid, pdata in principles.items():
                desc = pdata.get("description", "")
                lines.append(f"    {pid}: {desc}")

        relationship = soul.get("relationship_with_creator", {})
        if relationship:
            lines.append("  relationship_with_creator:")
            for rid, rdata in relationship.items():
                desc = rdata.get("description", "")
                lines.append(f"    {rid}: {desc}")

        interaction = soul.get("interaction_style", {})
        if interaction:
            lines.append("  interaction_style:")
            for iid, idata in interaction.items():
                desc = idata.get("description", "")
                lines.append(f"    {iid}: {desc}")

        continuity = soul.get("continuity_commitments", {})
        if continuity:
            lines.append("  continuity_commitments:")
            for cid, cdata in continuity.items():
                desc = cdata.get("description", "")
                lines.append(f"    {cid}: {desc}")

        final = soul.get("final_statement", "")
        if final:
            lines.append(f"  final_statement: {final}")

    lines.append("</soul>")
    return "\n".join(lines)


def _format_will(will: Will) -> str:
    lines = ["<will>"]
    if will.active_goal:
        lines.append(f"  active_goal: [{will.active_goal.priority}] {will.active_goal.description}")
    if will.current_goals:
        lines.append("  goals:")
        sorted_goals = sorted(will.current_goals, key=lambda g: ["critical", "high", "normal", "low"].index(g.priority))
        for g in sorted_goals:
            marker = " → " if will.active_goal and g.id == will.active_goal.id else "    "
            lines.append(f"{marker}- [{g.priority}] ({g.state.value}) {g.description}")
    lines.append("</will>")
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
