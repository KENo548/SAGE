import time
from typing import Callable

from jarvis.capabilities.base import Capability, CapabilityResult, RuntimeContext
from jarvis.skills import recall_memory, lookup_knowledge, review_goals, summarize as summarize_skill


class GoalReview(Capability):
    id = "goal_review"
    description = "Review current active goals, priorities, and history"

    def execute(self, context: RuntimeContext) -> CapabilityResult:
        data = review_goals(context.will_loader)
        lines = []
        if data["active_goal"]:
            g = data["active_goal"]
            lines.append(f"Active goal: {g['description']} (priority={g['priority']}, state={g['state']})")
        else:
            lines.append("No active goal.")
        if data["current_goals"]:
            lines.append("Current goals:")
            for g in data["current_goals"]:
                lines.append(f"  [{g['state']}] {g['description']} (priority={g['priority']})")
        else:
            lines.append("No current goals.")
        if data["history"]:
            lines.append("History:")
            for g in data["history"]:
                lines.append(f"  [{g['state']}] {g['description']}")
        return CapabilityResult(
            output="\n".join(lines),
            capability_id=self.id,
            success=True,
        )


class MemoryRecall(Capability):
    id = "memory_recall"
    description = "Recall episodic memories about a topic"

    def execute(self, context: RuntimeContext) -> CapabilityResult:
        results = recall_memory(context.user_input, context.memory_store)
        if not results:
            return CapabilityResult(
                output="No memories found.",
                capability_id=self.id,
                success=True,
            )
        lines = [f"Memories ({len(results)}):"]
        for m in results:
            lines.append(f"  [{m['source']}] {m['content']}")
        return CapabilityResult(
            output="\n".join(lines),
            capability_id=self.id,
            success=True,
        )


class KnowledgeLookup(Capability):
    id = "knowledge_lookup"
    description = "Look up knowledge about a topic"

    def execute(self, context: RuntimeContext) -> CapabilityResult:
        results = lookup_knowledge(context.user_input, context.memory_store)
        if not results:
            return CapabilityResult(
                output="No knowledge found.",
                capability_id=self.id,
                success=True,
            )
        lines = [f"Knowledge ({len(results)}):"]
        for k in results:
            lines.append(f"  [{k['domain']}] {k['content']}")
        return CapabilityResult(
            output="\n".join(lines),
            capability_id=self.id,
            success=True,
        )


class Summarize(Capability):
    id = "summarize"
    description = "Summarize text concisely"

    def execute(self, context: RuntimeContext) -> CapabilityResult:
        summary = summarize_skill(
            text=context.user_input,
            llm_generate=context.llm_generate,
        )
        return CapabilityResult(
            output=summary,
            capability_id=self.id,
            success=True,
        )
