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
