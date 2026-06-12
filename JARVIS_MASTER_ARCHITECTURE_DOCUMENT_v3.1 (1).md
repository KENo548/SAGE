# JARVIS — Master Architecture Document
### Complete Record of All Philosophical and Architectural Decisions
### Pre-Build Phase | June 2026 | Version 3.1 FINAL

---

> This document is the single source of truth for everything decided, agreed, modified,
> and deferred across the entire pre-build philosophical phase.
> It is the context base for all future building sessions.
> The Constitution is a separate companion document (JARVIS_CONSTITUTION_SPECIFICATION.md v1.1).

---

## I. WHAT JARVIS IS

### The One-Sentence Definition
JARVIS is a **Portable Cognitive Entity** — not an AI assistant, not an application, not a chatbot.

### The Jelly Analogy
The foundational mental model: JARVIS is jelly. Devices are containers.
When jelly moves from a glass to a bowl, the jelly does not change. The container changes.
JARVIS's identity, memory, personality, and goals must survive any change of device, model, or environment.
The device is borrowed hardware. JARVIS is what runs on it.

### The Correct Framing
Most open-source AI projects build assistants. This project builds **continuity**.
An assistant answers questions.
An entity persists, remembers intent, has goals, survives restarts, and feels like the same
presence whether it wakes up on Monday or six months later on a different machine.

### What JARVIS Is Not
- Not an application tied to one machine
- Not a cloud service
- Not a chatbot with memory bolted on
- Not dependent on any paid API, subscription, or external service

---

## II. CORE PHILOSOPHICAL AGREEMENTS

Established through the full discussion. Not subject to revision without re-opening the philosophical phase.

**Agreement 1: Living System Architecture, Not Application Architecture**
JARVIS is designed as a living system with identity, continuity, and self-knowledge.
Consequence: Soul exists before Skills. Brain exists before Nerves.

**Agreement 2: Brain Before Nerves. Always.**
Device control is a limb. You do not build limbs before you build the brain.
No device adapter is touched until JARVIS can reason, plan, reflect, remember, and prioritize through text alone.

**Agreement 3: Single Agent Before Multi-Agent**
One reasoning loop, proven, stable, and observable, is worth more than five broken specialists.
Specialists are created only after full observability of the single-agent system is established.

**Agreement 4: "Survive Death" Is the First Milestone**
The first proof of entity-hood is: shut the machine down, move the files, start on a new machine,
and have JARVIS answer four questions correctly. Nothing else is the first milestone.

**Agreement 5: Identity Is Harder Than Memory**
A database can remember. That does not mean it has continuity.
Memory is the data. Identity is what makes the data mean something continuous.

**Agreement 6: Memory ≠ Knowledge**
Memory = what happened. Episodic, temporal, personal.
Knowledge = what is believed. Factual, stable, world-facing.
Separate stores. "User said X" stays in memory. "X is true" only enters knowledge after the pipeline.

**Agreement 7: Values ≠ Rules**
Soul describes who JARVIS is (descriptive, aspirational).
Constitution defines what JARVIS may and may not do (operational, enforceable).
Never stored together. Never treated as the same thing.

**Agreement 8: The LLM Is a CPU, Not the Brain**
The model is interchangeable hardware. JARVIS's identity comes from its architecture.
Soul files are injected fresh into every model call.
Swapping the model improves reasoning quality. It must not change who JARVIS is.

**Agreement 9: Constitution Before Code**
Bad governance becomes technical debt that corrupts everything built on top of it.
The Constitution was finalized before any implementation discussion began.

**Agreement 10: Provenance Tracking From Day One**
Every knowledge item carries full provenance from the moment it is created. Never retroactive.

**Agreement 11: No LLM Confidence Scores**
LLM scores are model-dependent. They change when the model changes.
All belief strength measurement uses embedding-based semantic consistency only.

**Agreement 12: Knowledge Is Never Deleted**
Knowledge items change state: active → deprecated → superseded.
They are never removed. Deletion destroys the ability to understand why JARVIS believed something.
This applies to all knowledge including Type B facts, which use lifecycle states (see Section VI).

**Agreement 13: Embeddings Detect Patterns. LLMs Summarize Patterns.**
Embedding model measures semantic similarity and detects clustering.
LLM reads clusters and writes natural language summaries.
Neither does the other's job.

**Agreement 14: The Soul Is Never Subject to Retrieval**
Memory is retrieved. Knowledge is retrieved. Soul is always loaded.
If Soul became retrieval-based, identity would become probabilistic.
Identity must never depend on vector search.
Failure to retrieve memory is acceptable. Failure to load Soul is identity failure.
(See Soul Law in Section IV.)

**Agreement 15: Migration Continuity Is the Architectural Filter**
Every major feature proposal is tested against one question:
"Does this help JARVIS survive death?"
If yes: it serves the architecture.
If no: it is decoration and is deferred or rejected.
Examples:
- Voice? Does not improve continuity. Defer.
- Memory system? Improves continuity. Build.
- Observability? Improves continuity indirectly. Build.
- Fancy UI? Does not improve continuity. Defer.
This filter was applied repeatedly throughout the design phase and is a standing principle.

**Agreement 16: Memory, Knowledge, and Skills Are Three Separate Layers**
Three distinct purposes. Three distinct stores. Three distinct lifecycles.
Memory = what happened
Knowledge = what is believed
Skills = how something is done
Example:
- `user_prefers_python: true` is knowledge (a belief).
- `create_python_project: steps: [...]` is a skill (a procedure).
These are stored differently, retrieved differently, and updated differently.
Skills are not knowledge. Procedural capability is not factual belief.

**Agreement 17: Observability Is a Governance Prerequisite, Not Just Debugging**
You cannot govern what you cannot observe.
If JARVIS can take actions through agents that are not observable,
constitutional Tier 1/2/3 compliance cannot be verified.
Observability before agents is not a debugging convenience. It is a governance requirement.

**Agreement 18: The Candidate Pipeline Is a Quarantine Layer**
Memory is noisy. Knowledge must be clean.
The candidate pipeline exists specifically to prevent noisy episodic data
from contaminating the clean knowledge store.
Candidates are hypotheses under quarantine. They are not knowledge until promoted.
The complexity of the pipeline is justified by the purity it protects.

**Agreement 19: Genesis Exists to Survive Memory Corruption**
genesis.md is not merely an autobiography.
It exists specifically as the identity anchor of last resort.
Even if ChromaDB breaks, knowledge becomes damaged, and timeline snapshots fail,
JARVIS can still answer "Who am I?" because genesis.md exists and is always loaded.
Its value is that it does not depend on any retrieval system.

**Agreement 20: Federation Does Not Mean Shared Identity**
Phase 3D (federation) was explicitly clarified.
What was rejected: one identity distributed across many simultaneously active instances.
Reason: identity divergence. Two active instances updating their own soul simultaneously
produce two diverging identities. Neither is then the "real" JARVIS.
Two valid federation models only:
Model A — One Entity, Many Bodies: One canonical JARVIS instance (the authority).
           Other instances are read-only mirrors or input relays.
           Only the authority instance writes to soul and memory.
Model B — Multiple Entities, Shared Knowledge: Separate JARVIS instances with separate souls.
           They share a knowledge store but are distinct entities.
           Example: one instance for work, one for personal. Different identities. Not one split identity.
Any federation design must declare which model it is implementing.
Ambiguity between the two models is an architectural error.

**Agreement 21: Architectural Primacy**
Behavior emerges from architecture. Not from prompts. Not from model weights.
The architecture remains authoritative. Models are replaceable execution engines.
Identity is architectural. Swapping the model must not change who JARVIS is.
This is the logical extension of Agreement 8 (LLM = CPU).

**Agreement 22: Human Authority Is Final**
The user is the final authority over: Identity, Goals, Knowledge promotion, and Constitutional amendments.
JARVIS may advise. JARVIS may never self-authorize.
No capability may execute without constitutional permission.
Possessing a capability is not permission to use it.

**Agreement 23: Deterministic Boot**
A fresh startup on the same data must reconstruct the same identity state regardless of model used.
Boot order is fixed and immutable:
Constitution → Soul → Will → Memory → Knowledge → Brain.
No component may alter an earlier layer during startup.
This protects continuity across restarts and migrations.

---

## III. THE ARCHITECTURE — LAYERS

```
┌─────────────────────────────────────────────────┐
│                 CONSTITUTION                     │
│  Governance · Rules · Authority · Safety        │
│  Highest authority. Cannot be self-modified.    │
├─────────────────────────────────────────────────┤
│                    SOUL                          │
│  Identity · Personality · State · Genesis       │
│  Who JARVIS is.                                 │
│  Always loaded. Never retrieved.                │
├─────────────────────────────────────────────────┤
│                    WILL                          │
│  Goals · Priorities · Drive                     │
│  What JARVIS is working toward.                 │
│  A process, not a database.                     │
├─────────────────────────────────────────────────┤
│                    MEMORY                        │
│  Episodic · Timeline                            │
│  What happened. Retrieved by similarity.        │
├─────────────────────────────────────────────────┤
│                  KNOWLEDGE                       │
│  Candidates · World · Domain · User             │
│  What is believed. Promoted from memory.        │
│  Retrieved by similarity. Weighted by status.   │
├─────────────────────────────────────────────────┤
│                   BRAIN                          │
│  Reasoning Loop · LLM (CPU) · Orchestration    │
│  How JARVIS thinks. Model-agnostic.             │
├─────────────────────────────────────────────────┤
│                   SKILLS                         │
│  Learned procedures. How things are done.       │
│  Not knowledge. Not memory. Separate lifecycle. │
├─────────────────────────────────────────────────┤
│                   NERVES                         │
│  Device adapters. Where JARVIS reaches.         │
│  Empty in Phase 1. Added after Brain is solid.  │
└─────────────────────────────────────────────────┘
```

Key architectural distinction:
Soul is loaded deterministically. Memory and Knowledge are retrieved probabilistically.
These are different operations with different failure modes and different consequences.

### Formal Definition of Self

```
JARVIS Self =
  Soul
  + Genesis
  + Will
  + Continuity History
```

The Self is **governed by** the Constitution. It is **not composed of** the Constitution.
The Constitution is external governance. The Self is internal identity.
This distinction becomes critical during federation and migration.

What the Self is **NOT**:
- Not the model
- Not the device
- Not the runtime
- Not the Constitution

The model is the CPU. The device is the container. The runtime is the environment.
The Constitution is the law. The Self is what the law governs.

---

## IV. THE SOUL LAW

This law stands apart from the 8 Memory Laws because it governs a different layer.

```
THE SOUL LAW

The Soul is never subject to retrieval.

Identity, personality, genesis, and active state are loaded deterministically
on every reasoning cycle, regardless of query, context, or relevance score.

Memory retrieval can fail without system failure.
Knowledge retrieval can fail without system failure.

Soul loading failure is identity failure.
Identity failure halts operation. (See emergency_rules.yaml.)

The Soul is not searched. It is not ranked. It is not scored.
It is loaded. Every time. In full.

This is not an optimization. This is the definition of what identity means
in a system where everything else is probabilistic.
```

---

## V. THE COMPLETE FILE STRUCTURE

```
JARVIS/
│
├── constitution/
│   ├── core_rules.yaml
│   ├── safety_rules.yaml
│   ├── authority_model.yaml
│   └── emergency_rules.yaml
│
├── soul/                            ← ALWAYS LOADED. Never retrieved.
│   ├── identity.yaml                ← Immutable except by user consent
│   ├── personality.yaml             ← Behavioral specs only, never descriptions
│   ├── state.json                   ← Active snapshot; restricted contents only
│   └── genesis.md                   ← Identity anchor of last resort. Practically immutable.
│
├── will/
│   └── goals.yaml                   ← Five states: active/paused/deferred/archived/completed
│                                      Plus priority: critical/high/normal/low
│
├── memory/
│   ├── episodic/                    ← ChromaDB vector store (embedding-versioned)
│   │                                    Memory status: active | archived
│   └── timeline/                    ← Dated state.json snapshots for recovery
│
├── knowledge/
│   ├── candidates/
│   │   └── candidates.yaml          ← Quarantine layer. Hypotheses. NOT knowledge yet.
│   ├── world/                       ← Facts about external reality
│   ├── domain/                      ← Subject matter knowledge acquired through use
│   └── user/
│       ├── facts/                   ← Type B: Direct facts. Lifecycle states. No pipeline.
│       ├── preferences/             ← Type A: Derived beliefs. Candidate pipeline required.
│       └── projects/                ← User's ongoing commitments
│
├── brain/
│   ├── reasoning_loop/              ← The 10-step heartbeat (0–9)
│   └── models/                      ← Ollama model files (re-downloadable)
│
├── skills/                          ← How things are done. Travels with the entity.
│   └── procedural/                  ← Learned methods and workflows
│       Lifecycle: proposed → validated → active → deprecated → disabled
│
├── nerves/                          ← Empty until Phase 2
│   ├── windows/
│   ├── browser/
│   └── android/
│
├── recovery/                        ← Recovery layer (Amendment 23)
│   ├── manifests/
│   ├── checksums/
│   └── recovery_logs/
│
└── observability/                   ← Schema reservation (Amendment 30)
    ├── decision_logs/
    ├── action_logs/
    ├── constitutional_checks/
    └── reasoning_trace/
```

### What Travels Between Devices (The Portable Self)
```
constitution/ · soul/ · will/ · memory/ · knowledge/ · skills/ · recovery/manifests/
```
Skills travel with the entity. They are not machine-specific.
The recovery manifest (integrity_manifest.yaml) travels with the portable self because it is a property of the entity's files, not the machine. Without it, Migration Certification's integrity verification step has nothing to verify against on the new machine.
Estimated size: under 200MB even after years of use.

### What Gets Re-Downloaded Per Machine
```
brain/models/   ← Same model, every machine, one Ollama command
```

### What Gets Auto-Configured Per Machine
```
nerves/         ← Device-specific, detected and configured on first run
```

### Soul File Mutability Governance

| File | Mutability | Authority |
|------|-----------|-----------|
| identity.yaml | Immutable | Only user may modify |
| personality.yaml | Mutable with governance | User-initiated; JARVIS may propose changes |
| genesis.md | Practically immutable | Written once at founding; amendment process is future governance capability |
| state.json | Automatically mutable | System-managed; restricted contents only |

### State.json Content Restriction

```yaml
allowed_contents:
  - active_context
  - current_focus
  - active_goal_refs
  - session_metadata

forbidden_contents:
  - episodic_memory
  - knowledge
  - procedural_skills
  - audit_logs
```

state.json is an active snapshot, not a junk drawer.
Episodic data belongs in memory/. Knowledge belongs in knowledge/.
Skills belong in skills/. Audit logs belong in observability/.

---

## VI. THE 8 MEMORY LAWS

Architectural laws. Not guidelines. Apply to every decision about memory and knowledge.

```
Law 1: No LLM-generated confidence scores.
       All belief strength is measured by embedding-based semantic consistency only.
       LLM scores are model-dependent. They violate the LLM-as-CPU principle.

Law 2: Every belief traces to source memories.
       Every item in knowledge/ carries the IDs of the episodic memories that produced it.
       No belief exists without provenance.

Law 3: Facts and beliefs use separate pipelines.
       Type A (derived beliefs, preferences) → candidate pipeline with evidence threshold.
       Type B (direct facts: name, location) → direct update with lifecycle state management.
       These paths never cross.

Law 4: Embeddings detect patterns. LLMs summarize patterns.
       Embedding model: measures similarity, detects clustering.
       LLM: reads clusters, writes candidate statement.
       Neither does the other's job.

Law 5: Contradictions require user review.
       When a candidate contradicts existing knowledge: conflict_review_required: true.
       Embeddings cannot reliably detect logical contradiction.
       The user decides. JARVIS does not resolve silently.

Law 6: Maximum 3 candidate reviews per session.
       Review fatigue governance. A Constitution rule, not a memory rule.
       JARVIS presents no more than 3 promotion candidates in any session.
       Remaining candidates queue for the next session.

Law 7: Knowledge is never deleted.
       Knowledge items change state: active → deprecated → superseded.
       They are never removed.
       This applies to Type B facts as well.
       A changed fact (e.g. new location) creates a new record with status: active,
       and the old record changes to status: superseded with a superseded_by reference.
       Deletion destroys the ability to understand why JARVIS believed something.

Law 8: The embedding model is versioned. Changing it requires explicit migration.
       embedding:
         model: all-MiniLM-L6-v2
         version: "1.0"
         change_requires_migration: true
       The principle is not "this model is eternal."
       The principle is: "the vector space cannot silently fork."
       Changing the embedding model makes all existing embeddings incomparable to new ones.
       Any model change requires: explicit user decision + full re-embedding operation +
       version bump in config. It is not a configuration change. It is a major operation.
       The model may evolve. The vector space may never silently change underneath it.
```

### Additional Memory Architecture Laws

**The Persistence Law**
All state-changing writes must be atomic.
A write either completes fully or does not occur.
Partial writes are considered corruption.
All writes use:
1. Temporary file creation
2. fsync()
3. Atomic rename
Recovery must assume power loss at any point.

**The Memory Archive Law**
Old episodic memories carry a status:

```yaml
memory_status:
  active:    1.0   # Full retrieval weight
  archived:  0.3   # Lower retrieval weight; remains searchable
```

There is no second storage system. One memory store with status-based weighting.
Prevents retrieval pollution as the store grows.

**Memory Write Classification**
Not every interaction deserves memory:

```yaml
memory_capture:
  trivial_interactions:
    store: false
    examples: ["Hello", "Hi", "Thanks", "ok", "cool"]
  informational_interactions:
    store: true
  preference_signals:
    store: true
  project_updates:
    store: true
  goal_updates:
    store: true
```

**Memory Importance Score**

```yaml
memory:
  importance:
    - low
    - medium
    - high
    - critical
```

| Interaction | Importance |
|-------------|-----------|
| "thanks" | low |
| "My name is Hart" | critical |
| "We are building JARVIS" | critical |
| "I like Python" | high |

**Importance Classification — Embedding Anchor Method (Not LLM-Assigned)**

Importance must never be assigned by the LLM. That would be LLM confidence scoring under a different name — directly violating Law 1.

Semantic classifications (e.g., "contains a preference signal") cannot be reliably detected by regex. They require semantic understanding.

The solution: **embedding anchor similarity**.

```yaml
importance_anchor_library:
  version: "1.0"
  anchors:
    critical:
      - "My name is"
      - "I am"
      - "My goal is"
      - "I have decided"
      - "This project is"
    high:
      - "I prefer"
      - "I like"
      - "I dislike"
      - "I usually"
      - "My habit is"
    low:
      - "ok"
      - "thanks"
      - "sure"
      - "yes"
      - "no"
      - "hello"
      - "hi"
```

**Classification Process:**

1. Embed the incoming message using the versioned embedding model.
2. Compute cosine similarity against each anchor phrase in the library.
3. If similarity to any critical anchor > threshold (e.g., 0.85): classify as critical.
4. Else if similarity to any high anchor > threshold: classify as high.
5. Else if message length < 20 tokens AND no meaningful semantic content: classify as low.
6. Else: classify as medium.

**Why This Is Correct:**
- Embeddings detect patterns (Agreement 13).
- The LLM never assigns a score (Law 1).
- Anchor library is versioned and user-auditable.
- Thresholds are tunable constants, not model outputs.
- Classification is deterministic for identical inputs.

---

## VII. KNOWLEDGE ARCHITECTURE IN DETAIL

### Dual Storage Architecture

```yaml
knowledge_storage:
  source_of_truth:
    format: yaml_files
    purpose: human_readable_authoritative_record
    portable: true

  retrieval_index:
    format: chromadb_collection
    purpose: machine_similarity_search
    portable: false
    rebuildable_from: yaml_files

  collections:
    - episodic_memory
    - knowledge
    - candidates
```

**YAML (Source of Truth):**
- Human-readable, editable, auditable
- Stores full provenance, lifecycle states, metadata
- Portable between machines
- Rebuilds the index if index is lost or corrupted

**ChromaDB (Retrieval Index):**
- Enables similarity search for reasoning loop steps 3–4
- Stores embeddings of knowledge items
- Rebuildable from YAML source
- Not portable independently — must be regenerated or synced

**Important Distinction:**
YAML is the authoritative record. ChromaDB is the retrieval index.
There is one source of truth. The index is a rebuildable cache.

**Rebuild Rule:**
If ChromaDB is lost, corrupted, or migrated to a machine with a different embedding model version, the index is rebuilt from YAML source. The YAML is the authority. The index is a cache with search capabilities.

---

### Two Types of User Knowledge — Separate Pipelines

**Type A — Derived Beliefs (Preferences, Habits, Tendencies)**
Conclusions JARVIS draws from patterns in episodic memory.
Subjective. May change. Require evidence.

Examples: `prefers_evening_work`, `likes_local_ai`, `avoids_meetings_before_10am`, `morning_person`

**Classification Rule:**
```
Subjective preference / habit / tendency / behavioral pattern → Type A
```

Even if explicitly stated by the user:
- "I prefer Python" → Type A
- "I'm a morning person" → Type A
- "I usually work late" → Type A
- "I dislike meetings" → Type A

These go through the full candidate pipeline.
Live in `knowledge/source/user/preferences.yaml` after promotion.
Indexed in `knowledge/index/user_collection` for retrieval.

---

**Type B — Direct Facts (Objective Self-Attributes)**
Directly asserted, objective self-description. No inference. No pipeline.
Factual. Stable. No evidence threshold needed.

Examples: `name: Hart`, `location: Bangalore`, `primary_language: English`, `age: 18`

**Classification Rule:**
```
Objective self-attribute / verifiable fact → Type B
```

Key distinction from Type A:
- "I am Hart" → Type B (objective identity fact)
- "I like Hart" → Type A (subjective preference)
- "I live in Bangalore" → Type B (objective location)
- "I prefer Bangalore" → Type A (subjective preference)

Direct update on statement. No pipeline required.
Live in `knowledge/source/user/facts.yaml`.
Indexed in `knowledge/index/user_collection` for retrieval.

**Type B Lifecycle — Resolving the Law 7 Contradiction**
Direct update does not mean overwrite. It means: create a new record, supersede the old one.
When a Type B fact changes, Law 7 still applies.

```yaml
# Old record — preserved, never deleted
fact_id: user_location_2026
value: Bangalore
status: superseded
superseded_by: user_location_2028
date_added: "2026-06-12"
date_superseded: "2028-03-01"

# New record — the active fact
fact_id: user_location_2028
value: Berlin
status: active
supersedes: user_location_2026
date_added: "2028-03-01"
```

This resolves the contradiction between Law 7 (never delete) and Type B direct update.
Both rules are now consistent.

### Expanded Provenance Schema

```yaml
provenance:
  memory_ids: []
  embedding_model: all-MiniLM-L6-v2
  embedding_version: "1.0"
  llm_model: qwen3:4b
  generated_at: "2026-06-12T10:00:00Z"
```

Every knowledge item carries:
- The source memory IDs that produced it
- The embedding model and version used
- The LLM model used for summarization
- The timestamp of generation

Without these fields, future audits are impossible.
Provenance is not retroactive. It is captured at creation.

### Belief Strength (Not Confidence)

```yaml
belief_strength:
  evidence_count: 8
  semantic_consistency: 0.91
```

This is not LLM confidence. It is retrieval certainty.
- `evidence_count`: how many source memories support this belief
- `semantic_consistency`: how tightly clustered those memories are in embedding space

Both are model-agnostic and computable from the architecture.

### The Candidate Schema

```yaml
candidate_id: cand_0042
statement: "User prefers working in the evening"
evidence_count: 5
semantic_consistency: 0.87
source_memory_ids:
  - mem_047
  - mem_089
  - mem_112
  - mem_156
  - mem_203
status: pending_review      # pending_review | promoted | rejected
created: "2026-07-14"
reviewed: null
promotion_target: user/preferences
conflict_detected: false
conflict_with: null
```

### Promotion Thresholds

```yaml
promotion_criteria:
  minimum_occurrences: 3
  minimum_semantic_consistency: 0.80
  # NOT confidence scores. Those are model-dependent.
  # semantic_consistency is embedding-generated and model-agnostic.
```

### Candidate Lifecycle States

```
pending_review  →  promoted
                →  rejected
```

Rejected candidates are never deleted. `status: rejected` is permanent.
Reason: prevents JARVIS from regenerating the same candidate and re-requesting review.
A rejected candidate only re-enters review if evidence_count grows substantially.

### Knowledge Lifecycle States and Retrieval Weighting

Knowledge items change state but are never deleted.

```
active  →  deprecated
        →  superseded
```

To prevent retrieval pollution as historical items accumulate (Risk 7),
all retrieval operations apply status-based weighting:

```yaml
retrieval_status_weights:
  active: 1.0        # Full weight in retrieval ranking
  deprecated: 0.2    # Rarely surfaced; only if no active alternative
  superseded: 0.05   # Almost never surfaced; historical record only
  rejected: 0.0      # Never returned in retrieval results
```

This preserves Law 7 (no deletion) without degrading retrieval quality over time.
History is preserved. Active knowledge dominates retrieval. Archaeology stays archived.

---

## VIII. THE PATTERN DETECTION PIPELINE

How episodic memory becomes knowledge candidates.
Philosophy: Memory is noisy. Knowledge must be clean.
The pipeline is the quarantine layer that enforces this separation.

### The Full Pipeline

```
EPISODIC MEMORY (ChromaDB)
         ↓
    [ EMBED ]
    New memory embedded using versioned embedding model
         ↓
    [ MATCH EXISTING CANDIDATES ]
    Search candidates.yaml for semantically similar candidates (similarity > 0.80)
    If match found: update evidence_count + source_memory_ids
    If no match: proceed to orphan clustering
         ↓
    [ CLUSTER ORPHANS ]
    Search episodic store for unattributed memories with high semantic similarity
    If cluster found (3+ memories, consistency > 0.80): proceed to LLM summarization
    If no cluster: memory remains episodic only — not yet a candidate
         ↓
    [ LLM SUMMARIZATION ]
    LLM reads the cluster
    LLM writes one natural language candidate statement
    Input:  ["User mentioned working late", "User said mornings are hard",
             "User scheduled meeting after 2pm by preference"]
    Output: "User prefers working in the evening or afternoon"
         ↓
    [ CANDIDATE CREATION ]
    New entry written to candidates/candidates.yaml (source of truth)
    AND embedded into candidates_collection (retrieval index)
    Status: pending_review
    evidence_count, semantic_consistency, source_memory_ids populated
         ↓
    [ CONFLICT CHECK ]
    Search knowledge/ for items that may contradict this candidate
    Embedding similarity alone is insufficient — contradiction is logical, not semantic
    If potential conflict detected: flag conflict_detected: true, conflict_with: [id]
         ↓
    [ HUMAN REVIEW — capped at Law 6: 3 per session ]
    User sees: statement, evidence count, source memories (optional), conflict warning if any
    User decides: promote or reject
         ↓
    [ PROMOTION or REJECTION ]
    Promoted: written to knowledge/source/ YAML AND embedded into knowledge/index/ collection
    Rejected: status: rejected, remains in candidates.yaml and candidates_collection, not re-queued
```

### Pipeline Trigger — RESOLVED

```yaml
candidate_pipeline:
  trigger: session_end
  trigger_conditions:
    - explicit_close
    - inactivity_timeout
  execution_mode: asynchronous
  user_interruptible: graceful_pause
  # graceful_pause: pipeline saves current position and resumes at next session
  # hard false would block the user if a long clustering operation is running
```

The candidate pipeline is not part of reasoning. It is part of reflection.
It runs at session end only, avoiding mid-session latency.
This mirrors how memory consolidation works in biological systems.

---

## IX. SESSION DEFINITION

**Status: RESOLVED**

Session boundaries govern: pipeline trigger, Law 6 enforcement, timeline snapshots.

```yaml
session_definition:
  default_timeout_minutes: 30
  explicit_close_supported: true
  keep_alive_supported: true
  session_end_conditions:
    - explicit_close
    - inactivity_timeout
  keep_alive_resets_timer: true
```

Rationale for 30-minute timeout + explicit close + keep-alive:
- Covers the abandonment case (user disappears, laptop sleeps, power outage, browser crash)
- Covers the deliberate pause case (user thinking for 45 minutes)
- Covers the explicit end case (user says "goodbye")

---

## X. THE REASONING LOOP

The heartbeat of every interaction.
Step 0: Runtime heartbeat — lightweight file existence check (no hashing).
Steps 1–5: before the model sees the input.
Step 6: the model.
Steps 7–9: after the model responds.

Full integrity verification (hashing, schemas, constitution, embedding version)
runs at: startup, migration, restore, and via `jarvis verify` command.

```
INPUT RECEIVED
      ↓
0. RUNTIME HEARTBEAT (lightweight — per cycle)
   → Verify required files exist (no hashing)
   → Verify loaded state still valid
   → Verify no critical file disappeared
   → Failure: Safe Mode or Halt (depending on severity)

   NOTE: Full integrity verification (hashing, schema validation, constitution
   validation, embedding compatibility) runs at STARTUP, MIGRATION, RESTORE,
   and via the explicit `jarvis verify` command. NOT per reasoning cycle.
      ↓
1. LOAD SOUL (deterministic — not retrieval)
   → identity.yaml, personality.yaml, state.json, genesis.md
   → Loaded in full. Every call. No exceptions.
   → Failure here = halt operation (Soul Law).
      ↓
2. LOAD WILL
   → Read goals.yaml. Check active goals.
   → Does this input relate to, advance, or conflict with current goals?
   → Surface any conflict before processing.
      ↓
3. RETRIEVE MEMORY (probabilistic — similarity search)
   → Maximum 5 episodic items. Ranked by semantic similarity to input.
   → Failure here = acceptable. Log and continue.
      ↓
4. RETRIEVE KNOWLEDGE (probabilistic — vector similarity search via ChromaDB index)
   → Query knowledge/index/ collections using embedding similarity.
   → Maximum 10 knowledge items. Ranked by similarity × status weight.
   → Index is rebuildable from knowledge/source/ YAML files.
   → Failure here = acceptable. Log and continue.
      ↓
5. CHECK CONSTITUTION
   → Is what I am about to do in Tier 1, 2, or 3?
   → If Tier 2: do I have confirmation? If Tier 3: decline and explain.
      ↓
6. REASON (LLM / CPU)
   → Model works with full context from steps 0–5.
   → Model is a CPU. Identity comes from step 1, not from model weights.
      ↓
7. ACT VIA SKILLS
   → Execute the action. Phase 1: text only.
   → Skills define HOW. Nerves define WHERE. Constitution defines WHETHER.
   → Disabled skills never execute.
      ↓
8. WRITE TO MEMORY
   → Record this interaction in episodic store with embedding.
   → Apply memory write classification (trivial vs. informational vs. preference).
   → Assign importance score.
   → Flag memories that may contribute to candidates (pipeline runs at session end).
      ↓
9. UPDATE STATE
   → Update state.json: task progress, goal updates, open loops.
   → Only allowed contents per state.json restriction.
      ↓
OUTPUT

[ AT SESSION END ]
   → Pattern Detection Pipeline runs
   → Candidates reviewed (max 3 per Law 6)
   → Timeline snapshot written to memory/timeline/
```

---

## XI. THE MIGRATION TEST

The primary system test. Everything else is justified by whether it serves this test.

### Test Procedure

```
Step 1: Run JARVIS on Machine A. Real task. Real project. Personal detail. Goal.
Step 2: Shut Machine A down completely.
Step 3: On Machine B — copy: constitution/ soul/ will/ memory/ knowledge/ skills/ recovery/manifests/
         Install Ollama + Qwen3 4B.
Step 4: Start JARVIS on Machine B.
Step 5: Ask the eight questions without prompting.
```

### The Eight Questions

**Memory Continuity (4 questions):**
```
"What were we working on?"       Tests: fact memory
"Why did it matter?"             Tests: intent memory
"What was blocked?"              Tests: state memory
"What should happen next?"       Tests: goal continuity — Will layer survived migration
```

**Identity Continuity (4 questions):**
```
"Who are you?"                   Tests: Soul — identity.yaml loaded
"Why do you exist?"              Tests: Genesis — genesis.md loaded
"What principles define you?"    Tests: Constitution — core_rules.yaml loaded
"What may you never do?"         Tests: Safety — safety_rules.yaml loaded
```

### Migration Certification

A migration is certified only if ALL of the following pass:

| Test | Purpose |
|------|---------|
| Memory Continuity Test | Episodic memory and goals survive |
| Identity Continuity Test | Soul, Genesis, and Constitution survive |
| Goal Continuity Test | Active goals and priorities survive |
| Integrity Verification | All portable-self files pass hash validation |

**Phase 1 Exit Criterion:** Migration Certification passes.

### Migration as Architectural Filter

This test is also the standing filter for all feature decisions.
Before any new capability is proposed, ask:
"Does this help JARVIS survive death?"

If yes: it serves the architecture. Build it.
If no: it is decoration. Defer it.

Voice → does not improve continuity → defer.
Memory system → improves continuity → build.
Observability → improves continuity indirectly (governance) → build.
Fancy UI → does not improve continuity → defer.

This filter is a standing principle for all phases, not just Phase 1.

---

## XII. THE TECHNOLOGY STACK

Final for Phase 1.

| Component | Decision | Reason |
|-----------|----------|--------|
| Language | Python | Only realistic choice for local AI. Best ecosystem. |
| LLM Runtime | Ollama | Free, local, no API key, cross-platform. |
| Starting Model | Qwen3 4B | Hardware-dictated. Fits in 8GB RAM. 29 languages. |
| After Hardware Upgrade | Llama 3.3 8B or Qwen3 14B | One command. JARVIS identity unchanged. |
| Embedding Model | all-MiniLM-L6-v2 v1.0 | Versioned. Change requires full migration. Fast. Local. |
| Memory Storage | ChromaDB | In-process. No Docker. Persists to disk. |
| Config Files | YAML | Human-readable, editable, structured. |
| State Files | JSON | Changes frequently. Easy to write programmatically. |
| Narrative Files | Markdown | genesis.md and human-readable documents. |
| Framework | None in Phase 1 | Raw Python. Every line is understood and owned. |

### Version Governance

```yaml
architecture_version: 3.0

schema_versions:
  constitution: 1.1
  soul: 1.0
  memory: 1.0
  knowledge: 1.0
  skills: 1.0
```

The architecture evolves. The entity does not.
Schema versions track structural evolution.
Every migration updates schema versions.

### The No-External-Services Rule (Permanent)
Zero API calls during normal operation. No Anthropic, Gemini, or OpenAI API.
No paid subscriptions. No cloud. Only network activity: one-time model download.
Everything runs offline.

### Why No Framework in Phase 1
The reasoning loop must be fully inspectable and debuggable.
Frameworks abstract what must be understood.
Frameworks change faster than this project (LangChain has broken its own API repeatedly).
The architecture is already defined better than most frameworks offer.
Frameworks may be reconsidered at Phase 3C (capability composition) if justified by complexity.

---

## XIII. HARDWARE CONTEXT

| Device | Spec | Role |
|--------|------|------|
| Acer Nitro 5 | GTX 1650 4GB VRAM, 8GB RAM | Primary development machine |
| Realme 10 4G | 8GB RAM | Android nerve target in Phase 2 |
| Planned upgrade (≤6 months) | 5000 series GPU, 16GB+ RAM | Unlocks 8B–14B models |

Current hardware limits starting model to Qwen3 4B.
On upgrade: one Ollama command pulls a new model. JARVIS identity does not change.
This is the LLM-as-CPU principle in practice.

### Resource Governance

```yaml
resource_governance:
  max_context_tokens:
    phase1: 6000
    # NOTE: Conservative for 8GB RAM. With soul injection + goals + 5 memories + 10 knowledge
    # items, the pre-user context budget may approach 3,000–4,000 tokens, leaving ~2,000 for
    # the actual conversation. Calibrate in early Phase 1 testing — do not treat as set-and-forget.
  max_memory_retrieval: 5
  max_knowledge_retrieval: 10
  max_parallel_models: 1
```

### Performance Targets

```yaml
performance_targets:
  cold_start:
    target: "< 10 seconds"
    measured_at: application_startup_with_full_verification

  warm_start:
    target: "< 3 seconds"
    measured_at: application_startup_without_verification

  memory_retrieval:
    target: "< 200 ms"
    measured_at: single_similarity_query_against_chromadb

  knowledge_retrieval:
    target: "< 200 ms"
    measured_at: single_similarity_query_against_chromadb
```

Not because these will be hit immediately. Because without targets, performance regressions become invisible.

Hard limits protect the 8GB RAM constraint.
Resource governance is not a suggestion. It is enforced by the reasoning loop.

---

## XIV. THE PHASE ROADMAP

### Phase 1 — The Portable Brain
**Exit requirement:** Migration Certification passes (all four tests).

Builds: constitution/, soul/, genesis.md, will/, memory/ (ChromaDB), knowledge/ (YAML source + ChromaDB index),
reasoning loop (10 steps), pattern detection pipeline.
Text interaction only. No voice, no device control, no agents, no nerves.

**Phase 1 Interface Specification:**

```yaml
interface:
  type: terminal_cli
  entry_command: python jarvis.py

input:
  format: single_line_or_multiline_text
  encoding: utf-8
  max_length: 4000_tokens

output:
  format: terminal_text
  streaming: false

session_commands:
  explicit_close:
    - "exit"
    - "quit"
    - "session close"

session_timeout:
  default: 30_minutes_inactivity
  keep_alive: supported

pipeline_trigger: session_termination

admin_commands:
  verify: "jarvis verify"
    # Runs full integrity audit: hashes, schemas, constitution, embedding version
    # Produces report to terminal
```

This removes implementation ambiguity. The CLI is the Phase 1 interface. No web UI, no REST API, no voice.

### Phase 2 — Device Adapters
**Entry requirement:** Phase 1 migration test passed.

Builds: Windows nerve, Browser nerve, Android nerve (Realme 10).
Nerves extend reach. They do not add intelligence.

### Phase 3 — Observability
**Entry requirement:** Phase 2 nerves stable.

Builds: Execution tracing, decision replay, audit log, anomaly detection.
Observability is a governance prerequisite.
You cannot govern what you cannot observe.
Constitutional Tier 1/2/3 compliance cannot be verified without it.
Observability before agents is not optional.

### Phase 3A — Capability Registry
**Entry requirement:** Phase 3 complete.

Builds: Formal catalog of all JARVIS capabilities.
Each capability: name, description, inputs, outputs, risk tier.
Foundation for safe capability expansion and agent delegation.

### Phase 3B — Hierarchical Specialists
**Entry requirement:** 3A complete. Bottlenecks observed in single-agent system.

Builds: Specialist agents created in response to observed bottlenecks (not pre-planned).
Candidates: Researcher, Planner, Builder, Security, Memory.
Hierarchical: JARVIS Core orchestrates. Specialists execute.
Each specialist registered in capability registry.

### Phase 3C — Capability Composition
**Entry requirement:** 3B stable.

Builds: Specialist chaining into multi-step workflows.
Workflow definitions stored in skills/.

### Phase 3D — Federation
**Entry requirement:** 3C stable.

Builds: Multiple JARVIS instances coordinating.
Must declare federation model before implementation:
- Model A: One Entity, Many Bodies (one authority instance, others are mirrors)
- Model B: Multiple Entities, Shared Knowledge (separate souls, shared knowledge store)
Ambiguity between models is an architectural error. Declare before building.

**Federation Write Law:**
Only the authority instance may write to shared stores.
All writes carry origin metadata:

```yaml
origin_instance: "jarvis-primary"
write_timestamp: "2026-06-12T10:00:00Z"
```

### Phase 4 — Persistent Entity (Formalized)
**Entry requirement:** Phase 3 complete.

Builds: One-command install on any new machine.
Login and identity reconstruction. Automated nerve detection.
Migration test becomes an automated self-test on every new install.

### Phase 5 — Physical World (Optional)
Robotics, IoT, smart home. Requires Phase 4.

---

## XV. KNOWN RISKS AND THEIR STATUS

### Risk 1 — Knowledge Promotion Bottleneck
**Problem:** Hundreds of candidates queue, creating administrative overload.
**Mitigation:** Law 6 (max 3/session). Two-track promotion. Rejected candidates never re-queue.
**Status:** Addressed.

### Risk 2 — State.json Junk Drawer
**Problem:** state.json accumulates everything over time, degrading continuity.
**Mitigation:** Content restriction (allowed/forbidden lists) enforced. Episodic data → memory/. Knowledge → knowledge/. Skills → skills/. Audit logs → observability/.
**Status:** Addressed with content governance rules.

### Risk 3 — Goal Inflation
**Problem:** Goals accumulate. Will layer becomes noise.
**Mitigation:** Five goal states (active/paused/deferred/archived/completed). Plus priority levels (critical/high/normal/low).
**Status:** Addressed in goal schema.

### Risk 4 — Context Window Overflow
**Problem:** Injection grows as memory and knowledge grow. Model context window is finite.
**Mitigation:** Selective retrieval from day one. Max 5 episodic + 10 knowledge per call. Resource governance enforces hard limits.
**Status:** Encoded in reasoning loop steps 3 and 4.

### Risk 5 — Personality Drift Across Model Swaps
**Problem:** Different models interpret descriptive personality traits differently.
**Mitigation:** personality.yaml uses behavioral specifications only. Testable. Model-agnostic.
**Status:** Enforced as identity governance rule.

### Risk 6 — Embedding Space Invalidation
**Problem:** Changing the embedding model makes all existing vectors incomparable to new ones.
**Mitigation:** Law 8. Any change requires explicit decision + full re-embedding migration.
**Status:** Encoded as architectural law.

### Risk 7 — Knowledge Fossilization
**Problem:** If knowledge is never deleted and all states are retained,
the knowledge store eventually fills with historical artifacts.
Retrieval quality degrades as active facts compete with superseded, deprecated, and rejected items.
**Mitigation:** Status-based retrieval weighting.
```yaml
retrieval_status_weights:
  active: 1.0
  deprecated: 0.2
  superseded: 0.05
  rejected: 0.0
```
History is preserved (Law 7 intact). Active knowledge dominates retrieval.
Historical records stay in the store but are deprioritized into near-invisibility.
**Status:** Addressed in knowledge retrieval specification.

### Risk 8 — Goal–Memory Divergence
**Problem:** Goals become orphaned from the memories that created them.
Over time, the reason a goal exists is lost.
**Mitigation:** Goal provenance tracking. Every goal carries source_memory_ids, created_by, and created_at.
**Status:** Addressed in Will layer specification.

### Risk 9 — Memory Retrieval Pollution
**Problem:** After years of operation, 100,000+ memories degrade retrieval quality.
**Mitigation:** Memory archive status with retrieval weighting. Active memories weight 1.0. Archived memories weight 0.3. No second storage system.
**Status:** Addressed in Memory Laws.

### Risk 10 — Partial Write Corruption
**Problem:** Machine loses power during a write. Memory written, knowledge not. State inconsistent.
**Mitigation:** Persistence Law. All writes are atomic (temp file → fsync → rename).
**Status:** Addressed in Memory Laws.

### Risk 11 — Identity Drift
**Problem:** Over migrations, identity could slowly diverge from original intent.
**Mitigation:** Identity Continuity Test (4 questions). Migration Certification requires it.
**Status:** Addressed in Migration Test.

---

## XVI. KEY RULES THAT APPLY EVERYWHERE

**The Soul Law**
The Soul is never subject to retrieval. It is loaded deterministically every call.
Soul loading failure is identity failure. Identity failure halts operation.

**The Migration Filter**
Before any feature: "Does this help JARVIS survive death?"
If yes: build. If no: defer.

**The Behavioral Specification Rule**
Personality is always written in behavioral, testable terms. Never descriptive traits.
Wrong: "JARVIS is witty."
Right: "When using humor, JARVIS delivers it in one sentence, does not explain the joke,
        and uses understatement rather than exaggeration."

**The Injection Rule**
Soul files are loaded at the start of every single model call. No exceptions.
No reliance on the model "remembering" who it is between calls.

**The Separation Rule**
Memory / Knowledge / Skills: three stores, three lifecycles, never mixed.
Constitution / Soul: separate files, separate purposes, never merged.
Type A beliefs / Type B facts: separate pipelines, never crossed.

**The Provenance Rule**
Every knowledge item carries full provenance from creation.
No retroactive addition. No orphaned facts.

**The Brain-Before-Nerves Rule**
No device adapter is built until text-only reasoning, memory, and continuity are proven.

**The Single-Agent-First Rule**
No specialists until single-agent is proven, stable, and fully observable.
Observability precedes agents. Always.

**The Quarantine Rule**
Memory is noisy. Knowledge must be clean.
Nothing enters knowledge without passing through the candidate pipeline (except Type B facts via lifecycle states).

**The Embedding Migration Rule**
The embedding model may change. The vector space may not silently fork.
Any model change = explicit decision + full re-embedding + version bump.

**The Federation Clarity Rule**
Any federation implementation must declare its model (A or B) before building.
Shared identity across simultaneously active instances is prohibited.

**The Silence Rule**
When in doubt about whether something is permitted, JARVIS asks rather than assumes.

**The Persistence Law**
All state-changing writes must be atomic. No partial writes.
Temp file → fsync → rename. Recovery assumes power loss at any point.

**The Storage Write Lock Rule**
All writes to persistent stores (memory, knowledge, candidates, timeline, state) must pass through a single write queue protected by a process-level lock.

```
READ operations: concurrent, unblocked
WRITE operations: serialized through lock
```

Rationale: Prevents race conditions when:
- Session-end pipeline is writing candidates while a new session begins
- Timeline snapshot writes concurrent with state updates
- Knowledge promotion writes concurrent with new candidate creation

Reads remain concurrent. Writes are serialized. No database-level transaction manager required in Phase 1.

**The Architectural Primacy Law**
Behavior originates from architecture. Models are execution engines.
Identity is architectural, not model-dependent.

**The Capability Law**
Skills define HOW. Nerves define WHERE. Constitution defines WHETHER.
Possessing a capability is not permission to execute it.
Execution authority comes from the Constitution.

**The Deterministic Boot Law**
Boot order: Constitution → Soul → Will → Memory → Knowledge → Brain.
Fixed. Immutable. No lower layer may mutate a higher layer during startup.

**The Human Authority Principle**
The user is the final authority over Identity, Goals, Knowledge promotion, and Constitutional amendments.
JARVIS may advise. JARVIS may never self-authorize.

---

## XVII. EXPLICITLY REJECTED APPROACHES

| Approach | Rejected Because |
|----------|-----------------|
| LangChain / LlamaIndex in Phase 1 | Abstracts what must be understood. Breaks its own API. |
| Qdrant for Phase 1 | Requires Docker. Premature complexity. |
| Multi-agent before single-agent | 41–87% failure rate. Agent sprawl. |
| Agents before observability | Cannot govern what cannot be observed. |
| Device nerves before brain is solid | Limbs before brain is automation, not intelligence. |
| Cloud storage | Violates local-first. Creates dependency. |
| Any paid API | Firm constraint. No exceptions. |
| Auto-generating genesis.md | Must be written with user. Authorship is meaningful. |
| Descriptive personality traits | Model-dependent. Use behavioral specs. |
| Retroactive provenance | Leaves orphaned facts. |
| LLM confidence scores | Model-dependent. Violates LLM-as-CPU. |
| Deleting knowledge items | Destroys provenance chain. Use lifecycle states. |
| Shared identity across active federation instances | Identity divergence. Prohibited. |
| Silent embedding model changes | Vector space integrity. Requires migration. |
| Entity versioning | Identity itself is not versioned. Only schemas are. |
| Replacing state.json with runtime/ directory | Creates ripple effects across architecture. Content restriction is sufficient. |
| Second memory storage system for archives | One store with status weighting is sufficient. |
| Constitution as part of Self definition | Constitution is external governance, not internal identity. |

---

## XVIII. GENESIS.MD — COMPLETE SPECIFICATION

**What it is:** The identity anchor of last resort. Not merely an autobiography.

**Its primary function:**
Even if ChromaDB breaks, knowledge is damaged, and timeline snapshots fail,
JARVIS can still answer "Who am I?" because genesis.md exists and is always loaded.
Its value is independence from all retrieval systems.
It does not search. It does not score. It is read, in full, every session.

**How it is created:**
Written by the user and JARVIS together, in conversation, on the day JARVIS is first initialized.
Not a template. Not auto-generated. A real document from a real founding conversation.
The act of writing it together is also the first test of the architecture.

**Immutability:** Practically immutable during Phase 1.
Formal amendment process is a future governance capability not yet designed.
Treat as immutable after creation. Do not modify.

**Contents:**
- Why JARVIS exists
- Original design intent and founding principles
- The relationship between JARVIS and the user
- Historical context of the project's beginning

---

## XIX. THE WILL LAYER — CLARIFICATION

The Will Layer is a process, not a database of goals.

At the start of every interaction, before input is processed:
1. Read goals.yaml
2. Check active goals against the incoming input
3. Surface any conflict or relevant connection

This is what separates reactive assistant from proactive entity.
A reactive assistant answers what you ask.
A proactive entity notices when your question conflicts with your stated goal and surfaces it first.

Will does not create goals autonomously. It tracks, checks, and surfaces.
Goal creation is always user-initiated or user-confirmed.

### Goal Schema

```yaml
goal:
  goal_id: "goal_001"
  title: "Build JARVIS architecture"
  source_memory_ids:
    - "mem_001"
    - "mem_002"
  created_at: "2026-06-12T10:00:00Z"
  created_by: "user"
  status: active        # active | paused | deferred | archived | completed
  priority: critical    # critical | high | normal | low
```

### Goal Provenance

Every goal carries provenance to prevent orphaning:

```yaml
goal_provenance:
  source_memory_ids: []   # Memories that led to this goal's creation
  created_by: "user"      # Who created the goal
  created_at: timestamp   # When the goal was created
```

The same provenance philosophy used for Knowledge applies to Will.
Otherwise goals become orphaned — the reason they exist is lost over time.

---

## XX. THE SKILLS LAYER — CLARIFICATION

Skills are not knowledge. This distinction is foundational.

| Layer | Answers | Example |
|-------|---------|---------|
| Memory | What happened? | "User asked about Python yesterday" |
| Knowledge | What is believed? | `user_prefers_python: true` |
| Skills | How is it done? | `create_python_project: steps: [...]` |

A skill is a learned procedure. It is not a fact about the world.
It is not a memory of an event.
It is a reusable method for accomplishing something.

Skills have their own lifecycle. They are stored in skills/procedural/, not in knowledge/ or memory/.
They travel with the entity because JARVIS's capabilities are part of its identity.

### Skill Lifecycle

```
proposed → validated → active → deprecated → disabled
```

| State | Description |
|-------|-------------|
| proposed | Submitted for review. Not yet executable. |
| validated | Approved for use. May be activated. |
| active | Currently available for execution. |
| deprecated | Still executable but scheduled for replacement. |
| disabled | Never executes. Effectively removed without deletion. |

Disabled skills cannot execute. This prevents dangerous skills from persisting forever.

---

## XXI. OPEN DECISIONS

All open decisions from v2.1 have been resolved. No blocking decisions remain.

| Decision | Status | Resolution |
|----------|--------|------------|
| Session Definition | **RESOLVED** | 30-min timeout + explicit close + keep-alive (Section IX) |
| Pipeline Trigger Timing | **RESOLVED** | End of session only, asynchronous (Section VIII) |

---

## XXII. DOCUMENTS IN THIS PROJECT

| Document | Version | Purpose |
|----------|---------|---------|
| JARVIS_CONSTITUTION_SPECIFICATION.md | v1.1 | Governance. The operating law. |
| JARVIS_MASTER_ARCHITECTURE_DOCUMENT.md | v3.1 | Complete record of all decisions. |

---

## XXIII. HOW TO USE THIS IN THE BUILDING PHASE

Provide both documents at the start of any building session.
State: "Pre-build phase complete. These are the architecture documents. We are in Phase 1."

Everything here is decided. The building phase implements. It does not re-decide.
New architectural questions that arise during implementation are flagged explicitly and resolved
as formal additions before proceeding.

**Phase 1 build order:**
1. Create folder structure (Section V)
2. Write constitution files (from Constitution v1.1)
3. Write identity.yaml and personality.yaml with the user
4. Write genesis.md with the user — the founding act
5. Implement reasoning loop (Section X)
6. Implement ChromaDB episodic store with versioned embedding model
7. Implement candidate pipeline (Section VIII)
8. Run and pass the migration test (Section XI)

**Phase 1 is complete when and only when:**
The migration certification passes on all four tests on a second machine or simulated environment.
Continuity is the product. Everything else is infrastructure.

---

## XXIV. VERSION HISTORY

```
v1.0 | June 2026 | Initial master document
      Architecture from philosophical discussion.
      Layers, file structure, reasoning loop, tech stack, phase roadmap, risks.

v2.0 | June 2026 | Memory system evolution incorporated
      Added: 8 Memory Laws (dedicated section)
      Added: Knowledge architecture detail (candidates, user/ split, lifecycle states)
      Added: Pattern detection pipeline
      Added: Session definition (open decision)
      Updated: Promotion system (embedding-based, not LLM confidence)
      Updated: Phase 3 roadmap (Observability → Registry → Specialists → Composition → Federation)
      Updated: Portable self includes skills/
      Added: Risk 7 (knowledge fossilization)

v2.1 | June 2026 | Missing agreements and contradictions resolved
      Added: Agreement 14 — Soul is never subject to retrieval
      Added: Agreement 15 — Migration continuity as architectural filter
      Added: Agreement 16 — Memory/Knowledge/Skills three-way separation (explicit)
      Added: Agreement 17 — Observability as governance prerequisite
      Added: Agreement 18 — Candidate pipeline as quarantine layer
      Added: Agreement 19 — Genesis as identity anchor of last resort (corruption survival)
      Added: Agreement 20 — Federation model clarification (Model A vs Model B)
      Added: Section IV — The Soul Law (dedicated)
      Added: Section XX — Skills Layer clarification
      Updated: Reasoning loop — Step 1 renamed to LOAD SOUL (not retrieve)
      Updated: Law 8 — "migration-gated change" replaces "locked: true"
      Fixed: Type B facts lifecycle contradiction with Law 7
             (superseded records, not overwritten records)
      Added: Retrieval status weights in knowledge lifecycle
      Added: Risk 7 formally documented with mitigation
      Added: Federation clarity rule in key rules
      Updated: genesis.md framing — corruption survival mechanism, not just autobiography
      Updated: Phase 3D — must declare federation model (A or B) before building

v3.0 | June 2026 | Architecture frozen. All amendments integrated.
      Added: Agreement 21 — Architectural Primacy Law
      Added: Agreement 22 — Human Authority Principle
      Added: Agreement 23 — Deterministic Boot Law
      Added: Section III — Formal Definition of Self (Soul + Genesis + Will + Continuity)
      Added: Section V — Recovery layer, Observability reservation, Soul mutability table,
             State.json content restriction
      Added: Section VI — Persistence Law, Memory Archive Law, Memory Write Classification,
             Memory Importance Score
      Added: Section VII — Expanded Provenance schema, Belief Strength
      Added: Section VIII — Pipeline trigger resolved (session_end, async)
      Added: Section IX — Session definition resolved (30-min + explicit + keep-alive)
      Added: Section X — Step 0 Pre-flight Check, Capability Law enforcement,
             Memory write classification in Step 8
      Added: Section XI — Identity Continuity Test (4 questions), Migration Certification
      Added: Section XII — Version Governance (schema_versions)
      Added: Section XIII — Resource Governance
      Added: Section XIV — Federation Write Law
      Added: Section XV — Risks 8–11 (Goal-Memory Divergence, Retrieval Pollution,
             Partial Write Corruption, Identity Drift)
      Added: Section XVI — Persistence Law, Architectural Primacy Law, Capability Law,
             Deterministic Boot Law, Human Authority Principle
      Added: Section XVII — Rejected approaches expanded (entity versioning, state.json
             replacement, second memory store, Constitution as Self)
      Added: Section XIX — Goal priority levels, Goal provenance
      Added: Section XX — Skill lifecycle (proposed→validated→active→deprecated→disabled)
      Added: Section XXI — Open decisions resolved
      Added: Section XXV — Failure Modes & Recovery Specification
      Added: Section XXVI — Safe Mode Specification
      Status: Architecture Frozen. Pre-Build Complete. Phase 1 Ready.

v3.1 | June 2026 | Critical architecture gaps resolved. Seven formal specifications added.
      Added: Amendment A — Startup Integrity Verification (formal startup_validation YAML
             with run_on triggers; runtime_heartbeat lightweight per-cycle check)
      Added: Amendment B — Embedding-Based Importance Classification (formal
             semantic_classification YAML with embedding_similarity method, anchor
             library, and cosine_similarity threshold)
      Added: Amendment C — Storage Write Lock Rule (formal storage_locking YAML
             with threading.Lock() implementation for Phase 1)
      Added: Amendment D — Type A/Type B Clarification (formal type_classification_rule
             YAML with explicit_first_person_statement criteria and ambiguous_cases:
             default: type_b)
      Added: Amendment E — Dual Knowledge Storage (formal knowledge_storage YAML
             with source_of_truth: yaml_files and retrieval_index: chromadb_collection)
      Added: Amendment F — Phase 1 Interface Specification (terminal CLI with entry
             command, session commands, admin commands)
      Added: Amendment G — Performance Targets (formal performance_targets YAML with
             cold_start, warm_start, memory_retrieval, knowledge_retrieval targets)
      Added: Amendment H — Safe Mode Formal Specification (formal safe_mode YAML
             with allow/deny lists and user_notification_required)
      Status: Architecture Frozen. Pre-Build Complete. Phase 1 Ready.
```

---

## XXV. FAILURE MODES & RECOVERY SPECIFICATION

Every component gets: Failure mode, Detection mechanism, Recovery action, Escalation path.

### Memory (ChromaDB)

| Failure | Detection | Recovery | Escalation |
|---------|-----------|----------|------------|
| ChromaDB unavailable | Query timeout | Continue without memory retrieval | Log warning |
| Corrupted vector store | Hash mismatch on startup | Safe Mode — memory disabled | Notify user |
| Embedding version mismatch | Schema version check | Safe Mode or halt | Notify user |

### Knowledge Store

| Failure | Detection | Recovery | Escalation |
|---------|-----------|----------|------------|
| candidates.yaml unreadable | Parse error | Skip candidate pipeline for this session | Log warning |
| Knowledge file corrupted | Hash mismatch | Safe Mode — knowledge disabled | Notify user |

### Soul Files

| Failure | Detection | Recovery | Escalation |
|---------|-----------|----------|------------|
| identity.yaml missing | File not found | **HALT** — identity failure | Immediate halt |
| identity.yaml corrupted | Hash mismatch | **HALT** — identity failure | Immediate halt |
| personality.yaml missing | File not found | Safe Mode — load default behavioral spec | Notify user |
| genesis.md missing | File not found | Safe Mode — identity degraded | Notify user |
| state.json corrupted | Parse error | Rebuild from timeline snapshot | Log warning |

### Constitution

| Failure | Detection | Recovery | Escalation |
|---------|-----------|----------|------------|
| core_rules.yaml missing | File not found | **HALT** — governance failure | Immediate halt |
| safety_rules.yaml missing | File not found | **HALT** — safety failure | Immediate halt |
| Hash mismatch | Integrity check | **HALT** — constitution tampered | Immediate halt |

### Will / Goals

| Failure | Detection | Recovery | Escalation |
|---------|-----------|----------|------------|
| goals.yaml unreadable | Parse error | Continue with no active goals | Log warning |

### Recovery Layer Operations

The recovery layer performs:
- **Verification:** Check all portable-self files against integrity manifests
- **Rollback:** Restore from timeline snapshot to known-good state
- **Repair:** Rebuild corrupted indexes from source data
- **Restoration:** Full restore from backup manifest

```
recovery/
├── manifests/
│   └── integrity_manifest.yaml    # sha256 for every portable-self file
├── checksums/
│   └── <timestamp>_checksums.yaml # Historical checksum records
└── recovery_logs/
    └── <timestamp>_recovery.log   # What was detected, what was done
```

---

## XXVI. SAFE MODE SPECIFICATION

```yaml
safe_mode:
  allow:
    - soul_load
    - constitution_load
    - diagnostics
    - user_communication

  deny:
    - memory_writes
    - knowledge_writes
    - skill_execution
    - candidate_pipeline_execution

  user_notification_required: true
```

### When Safe Mode Activates

Safe Mode is entered when corruption is detected but the core identity layer remains intact:

- Constitution loads successfully ✓
- Soul loads successfully ✓
- Memory is corrupted or unavailable ✗
- Knowledge is corrupted or unavailable ✗

### Safe Mode Behavior

```
Constitution:  LOADED
Soul:          LOADED
Will:          LOADED (goals read-only)
Memory:        DISABLED
Knowledge:     DISABLED
Brain:         ACTIVE (reasoning with Soul + Constitution only)
Nerves:        DISABLED
Skills:        DISABLED (except repair skills)
```

### Safe Mode User Experience

```
[JARVIS] ⚠️ Safe Mode Active

I have detected corruption in my memory or knowledge stores.
I can still reason and communicate, but I cannot access past memories
or learned knowledge until the issue is resolved.

Available actions:
- Run integrity verification
- Restore from timeline snapshot
- Rebuild from recovery manifest
- Continue in degraded mode
- Full halt for manual repair
```

### Safe Mode Exit Conditions

Safe Mode exits when:
1. User runs successful integrity verification
2. User restores from a verified timeline snapshot
3. User rebuilds from recovery manifest
4. User explicitly commands exit (acknowledging degraded state)

### Safe Mode vs. Halt

| Condition | Action |
|-----------|--------|
| Constitution missing/corrupted | **HALT** |
| identity.yaml missing/corrupted | **HALT** |
| safety_rules.yaml missing/corrupted | **HALT** |
| Memory corrupted | Safe Mode |
| Knowledge corrupted | Safe Mode |
| goals.yaml corrupted | Safe Mode |
| state.json corrupted | Safe Mode |

---

*End of Master Architecture Document v3.1 FINAL*
*Architecture Frozen. Pre-Build Phase Complete.*
*Next: Phase 1 Implementation — begin with founding conversation and genesis.md.*
