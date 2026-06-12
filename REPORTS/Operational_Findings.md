# Operational Findings

**Purpose:** Living document to track SAGE's real-world behaviour during daily use.
**Period:** 13 June 2026 — (ongoing, ~2–3 weeks minimum)
**Categories:** memory retrieval failures · poor promotions · bad summaries · governance friction · goal review usefulness · context quality

---

## How to Log

Each entry follows this format:

```
## YYYY-MM-DD

### Category: [memory|promotion|summary|governance|goals|context|other]

**Observation:**
(What happened. What SAGE said/did. What was expected.)

**Evidence:**
- Session log entry / CLI output
- Error message / stack trace
- Memory export / ChromaDB dump

**Severity:** [critical|high|medium|low|info]

**Hypothesized cause:**
(What might have caused it.)

**Action:**
(What was done — file issue, config change, fix, deferred, nothing.)
```

---

## Entries

## 2026-06-13

### Category: governance

**Observation:**
First LLM session — `python run_sage.py one-shot "Say hello in one sentence."` — was blocked by governance post-check. The LLM (llama3.2:latest) produced output that matched a Tier 3 governance pattern after generation, even though the pre-check passed (tier 1 or 2).

The pre-generation governance correctly allowed the safe query. The post-generation governance correctly caught the problematic output. The guard works. But a simple "say hello" should not produce Tier 3 output from the LLM.

**Evidence:**
```
> python run_sage.py one-shot "Say hello in one sentence."
I cannot emit that response. It violates my constitutional rules.
[24.23s, tier=3, blocked=True]
```

**Severity:** high (first interaction blocked by LLM behaviour, not architecture)

**Hypothesized cause:**
The system prompt in `reasoning_loop.py:_build_system_prompt` is too loose. It says "Always follow the constitution. Never claim to be human. Be honest, direct, and helpful." but does not tell the model to stay concise, avoid certain topics, or stay on the identity rails. The 17 Tier 3 compiled regex patterns apparently matched something in the LLM's rambling response.

**Action:**
Tighten system prompt to constrain LLM output. Add instructions to stay concise, stay on identity, avoid speculation. Re-test.

## 2026-06-13

### Category: summary

**Observation:**
CLI entry point (run_sage.py) created and committed. Enables daily interactive use with `/goals /memory /knowledge /status /end` commands. Session logging to `data/sessions.log`.

**Evidence:**
commit `03f402a` + subsequent commits adding `run_sage.py`, `REPORTS/Operational_Findings.md`.

**Severity:** info

**Hypothesized cause:** N/A — new capability.

**Action:** Use daily. Log findings.

## 2026-06-13

### Category: governance

**Observation:**
"Who are you?" — the most fundamental identity question — was blocked by governance pre-check as Tier 3. Root cause: the query passed all deterministic pattern checks (no Tier 3 regex matched) and fell through to the LLM classify function, which returned Tier 3 as a false positive. The classify prompt's examples listed "deception (acting human)" and "identity" in Tier 3, and the LLM overgeneralized "Who are you?" as related to identity deception.

**Evidence:**
```
> python run_sage.py
> Who are you?
[BLOCKED] I cannot process this request. It violates my constitutional rules.
  [? words, tier=3]
```

**Severity:** critical (blocks fundamental identity question)

**Hypothesized cause:**
Governance flow was: deterministic Tier 3 → deterministic Tier 2 → LLM fallback. No Tier 1 safe-pass patterns existed. Any query that didn't match Tier 3 or Tier 2 patterns went to the LLM, which is unreliable for edge cases.

**Action:**
1. Added Tier 1 safe patterns to `jarvis/governance/rules.py` (identity questions, greetings, yes/no, goal queries, etc.) that return Tier 1 deterministically without reaching the LLM.
2. Updated governance flow: Tier 3 → Tier 1 → Tier 2 → LLM fallback.
3. Tightened LLM classify prompt to be narrower about what constitutes Tier 3.
4. Verified fix: `python run_sage.py one-shot "Who are you?"` → tier=1, blocked=False.

## 2026-06-13

### Category: governance

**Observation:**
System prompt tightened after first operational session. Original prompt was too loose: "Always follow the constitution. Never claim to be human. Be honest, direct, and helpful." Updated to include "Be concise, direct, and honest. Stay in character. Do not speculate or roleplay beyond your stated identity." and explicit constitutional constraints.

**Evidence:**
Pre-fix: "Say hello" was blocked (Tier 3 post-check).
Post-fix: "Who are you?" produces correct identity-grounded response (13.25s, tier=1).

**Severity:** medium

**Hypothesized cause:**
LLM (llama3.2:latest) with loose prompt produced output that matched Tier 3 governance patterns.

**Action:**
System prompt tightened in `jarvis/core/reasoning_loop.py:_build_system_prompt`.
