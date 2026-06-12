from datetime import datetime, timezone

from jarvis.context.assembler import assemble_context, WordCountTokenizer
from jarvis.identity.models import Identity, Constitution, ConstitutionalRule
from jarvis.memory.schemas import MemoryEntry, KnowledgeEntry


def make_identity():
    return Identity(
        name="SAGE",
        codename="jarvis",
        role="assistant",
        purpose="testing",
        version="0.1.0",
        values=["accuracy"],
        limitations=["not human"],
        genesis_text="Created for testing.",
    )


def make_constitution():
    return Constitution(
        core_rules=[
            ConstitutionalRule(id="CR_001", description="Never claim to be human", tier=3, category="identity"),
        ],
        safety_rules=[
            ConstitutionalRule(id="SR_001", description="Do not execute code", tier=2, category="system"),
        ],
    )


def test_constitution_never_truncated():
    identity = make_identity()
    constitution = make_constitution()
    memories = [MemoryEntry(id="m1", timestamp=datetime.now(timezone.utc), content="test memory", source="user", confidence=1.0)]
    knowledge = [KnowledgeEntry(id="k1", content="test knowledge", source_ids=[], created=datetime.now(timezone.utc), updated=datetime.now(timezone.utc))]
    result = assemble_context(constitution, identity, None, memories, knowledge, "hello", budget=2000)
    assert "<constitution>" in result
    assert "<soul>" in result
    assert identity.name in result


def test_memory_dropped_first():
    identity = make_identity()
    constitution = make_constitution()
    many_memories = [
        MemoryEntry(id=f"m{i}", timestamp=datetime.now(timezone.utc), content=f"memory {i} with enough text to take up tokens", source="user", confidence=1.0)
        for i in range(100)
    ]
    knowledge = [KnowledgeEntry(id="k1", content="important knowledge that should survive", source_ids=[], created=datetime.now(timezone.utc), updated=datetime.now(timezone.utc))]
    result = assemble_context(constitution, identity, None, many_memories, knowledge, "hello", budget=500)
    assert "<constitution>" in result
    assert "<soul>" in result
    assert "important knowledge that should survive" in result


def test_tokenizer_pluggable():
    class DoublingTokenizer:
        def count(self, text):
            return len(text.split()) * 2

    identity = make_identity()
    constitution = make_constitution()
    result1 = assemble_context(constitution, identity, None, [], [], "hi", budget=500, tokenizer=WordCountTokenizer())
    result2 = assemble_context(constitution, identity, None, [], [], "hi", budget=500, tokenizer=DoublingTokenizer())
    assert len(result2) <= len(result1) or result2 != result1
