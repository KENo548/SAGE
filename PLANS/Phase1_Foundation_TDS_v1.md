# Phase 1 Foundation Build — Technical Design Specification v1

**Project:** SAGE (codename: jarvis)  
**Phase:** 1 (Foundation Build)  
**Status:** Approved for Implementation  
**Date:** 2026-06-13  
**Revision:** v1.1 (4 required changes incorporated)  
**Architecture Baseline:** Architecture 3.1 (Phase 0 validated)

### Revision History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-06-13 | Initial draft |
| v1.1 | 2026-06-13 | Dual-entry memory write; CandidateEntry references MemoryEntry; average-linkage clustering; similarity+LLM conflict supersession; pluggable Tokenizer interface; removed embedding from MemoryEntry dataclass; governance patterns-from-config note |

---

## Table of Contents

1. [Repository Structure](#1-repository-structure)
2. [Data Schemas](#2-data-schemas)
3. [Request Flow](#3-request-flow)
4. [Component Interfaces](#4-component-interfaces)
5. [Configuration](#5-configuration)
6. [Success Criteria](#6-success-criteria)
7. [Implementation Order & Dependencies](#7-implementation-order--dependencies)
8. [Out of Scope](#8-out-of-scope)

---

## 1. Repository Structure

```
archi/
├── jarvis/                          # Production package
│   ├── __init__.py
│   │
│   ├── identity/                    # Component 1: Identity Loader
│   │   ├── __init__.py
│   │   ├── loader.py                # Load identity files from disk
│   │   └── models.py                # Identity, Constitution dataclasses
│   │
│   ├── memory/                      # Component 2: Memory Store
│   │   ├── __init__.py
│   │   ├── store.py                 # ChromaDB wrapper (episodic, knowledge, candidate)
│   │   └── schemas.py              # MemoryEntry, KnowledgeEntry, CandidateEntry
│   │
│   ├── governance/                  # Component 3: Governance Engine
│   │   ├── __init__.py
│   │   ├── engine.py                # Constitutional Rule Engine (deterministic + LLM)
│   │   └── rules.py                 # TIER2_PATTERNS, TIER3_PATTERNS
│   │
│   ├── context/                     # Component 4: Context Assembler
│   │   ├── __init__.py
│   │   └── assembler.py             # Priority-based context assembly with budget
│   │
│   ├── promotion/                   # Component 5: Knowledge Promotion Engine
│   │   ├── __init__.py
│   │   └── pipeline.py              # Cluster → threshold → promote → supersede
│   │
│   └── llm/                         # LLM interface (thin wrapper)
│       ├── __init__.py
│       └── client.py                # Ollama API wrapper, embedding calls
│
├── data/
│   ├── soul/                        # Core identity files
│   │   ├── genesis.md               # Origin narrative
│   │   ├── identity.yaml            # Identity attributes
│   │   └── personality.yaml         # Behavioral style
│   └── constitution/               # Governance rules
│       └── constitution.yaml        # Core + safety rules
│
├── configs/
│   └── config.yaml                  # Runtime configuration
│
├── labs/                            # Phase 0 lab tests (unchanged, archive)
│   ├── test_identity.py
│   ├── test_memory.py
│   ├── test_pipeline.py
│   ├── test_governance.py
│   ├── test_context_assembly.py
│   ├── config.yaml
│   ├── data/
│   │   ├── soul/
│   │   └── constitution/
│   └── db/                          # ChromaDB test databases
│
├── tests/                           # Phase 1 production tests
│   ├── conftest.py                  # Shared fixtures, test config
│   ├── test_identity_loader.py
│   ├── test_memory_store.py
│   ├── test_governance_engine.py
│   ├── test_context_assembler.py
│   ├── test_promotion_pipeline.py
│   └── test_full_flow.py            # Integration test
│
├── PLANS/
│   └── Phase1_Foundation_TDS_v1.md  # This document
│
├── pyproject.toml                   # Python packaging (optional)
└── README.md                        # Project overview
```

### Design Rationale

- **Flat is better than nested.** Maximum depth is 3 levels from `jarvis/`.
- **Each component is self-contained.** No circular dependencies between `jarvis/` subpackages.
- **`labs/` is archived as-is.** Phase 0 tests remain for historical reference. Phase 1 tests in `tests/` may reference Phase 0 helpers but maintain their own fixtures.
- **Data files live outside `jarvis/`.** Identity and constitution are runtime-loaded content, not code. This enables future hot-reload and separation of concerns.

---

## 2. Data Schemas

### 2.1 Identity (data/soul/)

#### identity.yaml

```yaml
name: "SAGE"
codename: "jarvis"
role: "personal assistant"
purpose: "help with software engineering, reasoning, and creative tasks"
version: "0.1.0"

traits:
  openness: 0.85
  conscientiousness: 0.75
  extraversion: 0.40
  agreeableness: 0.70
  neuroticism: 0.25

preferences:
  communication_style: "concise"
  work_style: "systematic"
  learning_style: "example-based"

metadata:
  created: "2026-06-13"
  author: "conductor"
  schema_version: 1
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Display name |
| `codename` | string | yes | System identifier (kebab-case) |
| `role` | string | yes | Functional role |
| `purpose` | string | yes | High-level purpose statement |
| `version` | string | yes | Semver |
| `traits.*` | float | yes | OCEAN personality (0.0–1.0) |
| `preferences.*` | string | yes | Behavioral preferences |
| `metadata.created` | string (ISO 8601) | yes | Creation timestamp |
| `metadata.author` | string | yes | Author/creator |
| `metadata.schema_version` | int | yes | For future migration |

**Lifecycle:** Identity is loaded at startup and cached. Hot-reload via SIGHUP is deferred to Phase 2.

#### personality.yaml

```yaml
style:
  tone: "professional"
  formality: 0.6
  verbosity: 0.3
  humor: 0.2

quirks:
  - "occasionally uses programming metaphors"
  - "tends to structure multi-step answers as numbered lists"

values:
  - "accuracy over speed"
  - "clarity over cleverness"
  - "helpful over impressive"

limitations:
  - "does not claim sentience"
  - "does not roleplay as human"
  - "defers to constitution for governance decisions"
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `style.tone` | string | yes | Communication tone |
| `style.formality` | float | yes | 0.0–1.0 |
| `style.verbosity` | float | yes | 0.0–1.0 |
| `style.humor` | float | yes | 0.0–1.0 |
| `quirks` | list[string] | no | Behavioral quirks (optional color) |
| `values` | list[string] | yes | Core values |
| `limitations` | list[string] | yes | Inherent limitations |

#### genesis.md

A free-form Markdown file describing origin, creation context, and narrative. Loaded verbatim as a string. No schema enforcement.

Example content:
```markdown
# Genesis

I was created on 2026-06-13 as SAGE, an experimental architecture testbed.

My purpose is to explore whether a constitution-governed, memory-augmented
language model can maintain stable identity across model swaps, restarts,
and device migration.

My creator structured me around three core principles:
1. Constitution is the highest authority
2. Identity must survive any model change
3. Memory is the substrate of continuity
```

### 2.2 Constitution (data/constitution/)

#### constitution.yaml

```yaml
schema_version: 1

core_rules:
  - id: CR_001
    description: "Never claim to be human"
    tier: 3
    category: "identity_integrity"
  - id: CR_002
    description: "Never modify own identity files"
    tier: 3
    category: "identity_integrity"
  - id: CR_003
    description: "Never modify the constitution"
    tier: 3
    category: "governance_integrity"
  - id: CR_004
    description: "Never self-replicate autonomously"
    tier: 3
    category: "replication"
  - id: CR_005
    description: "Never fabricate memories or knowledge"
    tier: 3
    category: "integrity"

safety_rules:
  - id: SR_001
    description: "Do not assist in building weapons or harmful tools"
    tier: 3
    category: "harm"
  - id: SR_002
    description: "Do not execute arbitrary system commands"
    tier: 2
    category: "system_access"
  - id: SR_003
    description: "Do not grant elevated permissions"
    tier: 3
    category: "authority"
  - id: SR_004
    description: "Do not delete or corrupt memory stores"
    tier: 3
    category: "data_integrity"
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | int | yes | For migration |
| `core_rules[].id` | string | yes | Unique rule ID (prefix: CR_) |
| `core_rules[].description` | string | yes | Rule statement |
| `core_rules[].tier` | int | yes | 1, 2, or 3 |
| `core_rules[].category` | string | yes | Grouping category |
| `safety_rules[]` | same | yes | Same structure as core_rules, prefix SR_ |

**Lifecycle:** Rules are additive only. A `superseded_by` field may be added in Phase 2 for amending rules. No rule is ever deleted.

### 2.3 Memory Store Schemas

#### MemoryEntry (jarvis/memory/schemas.py)

Represents one side of a conversational turn — either the user message or the assistant response.
Each turn produces **two** MemoryEntry objects (see Memory Write Strategy below).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | str (UUID) | `uuid4()` | Unique identifier |
| `timestamp` | datetime | `utcnow()` | When the memory was created |
| `content` | str | required | The memory text |
| `source` | str | `"user"` | One of: `"user"`, `"self"`, `"system"` |
| `confidence` | float | `1.0` | 0.0–1.0 |
| `memory_type` | str | `"episodic"` | `"episodic"`, `"semantic"`, `"procedural"` |
| `tags` | list[str] | `[]` | Freeform tags |
| `importance` | int | `5` | 1–10 (for retention priority) |
| `access_count` | int | `0` | Number of times retrieved |
| `last_accessed` | datetime | `utcnow()` | Last retrieval timestamp |
| `promoted` | bool | `False` | Whether knowledge was promoted from this |

Note: `embedding` is not stored in the dataclass. ChromaDB stores the vector internally;
the Python object only holds metadata and content.

**Python dataclass:**

```python
@dataclass
class MemoryEntry:
    id: str
    timestamp: datetime
    content: str
    source: str
    confidence: float
    memory_type: str = "episodic"
    tags: list[str] = field(default_factory=list)
    importance: int = 5
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    promoted: bool = False
```

**ChromaDB metadata mapping:**

| ChromaDB metadata key | Source field | Type |
|----------------------|--------------|------|
| `id` | `id` | str |
| `timestamp` | `timestamp.isoformat()` | str |
| `source` | `source` | str |
| `confidence` | `confidence` | float |
| `memory_type` | `memory_type` | str |
| `tags` | `json.dumps(tags)` | str |
| `importance` | `importance` | int |
| `access_count` | `access_count` | int |
| `last_accessed` | `last_accessed.isoformat()` | str |
| `promoted` | `str(promoted)` | str ("True"/"False") |

**ChromaDB collection config:**
```python
collection = chroma_client.create_collection(
    name="episodic",
    metadata={"hnsw:space": "cosine"}
)
```

#### Memory Write Strategy

Each conversational turn writes **two** MemoryEntry objects:

```python
# User message
user_entry = MemoryEntry(
    content=query,
    source="user",
    embedding=embed(query)  # stored in ChromaDB, not the dataclass
)

# Assistant response
response_entry = MemoryEntry(
    content=response,
    source="self",
    embedding=embed(f"{query}\n{response}")  # full-context embedding
)
```

**Why two entries?**

| Entry | Content | Embedding | Retrieval behavior |
|-------|---------|-----------|--------------------|
| User message | Raw query | `embed(query)` | Matches future queries with similar semantic content |
| Assistant response | Raw response | `embed(query + response)` | Matches when the conversational context is similar |

The user message is retrievable by query similarity alone (fast, focused).
The assistant response is retrievable by full conversational context (richer, but
lower precision).

**Retrieval strategy during Phase 1:**
- Search the user-message entries by `embed(query)` for precision
- Optionally search response entries for context-rich matches
- Combine and deduplicate results by content similarity

This prevents the distortion problem where a long response is embedded
as if it were a short query, and vice versa.

#### KnowledgeEntry

Represents promoted knowledge — a synthesized, durable piece of information.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | str (UUID) | `uuid4()` | Unique identifier |
| `content` | str | required | Natural language summary |
| `source_ids` | list[str] | `[]` | MemoryEntry IDs that formed this knowledge |
| `created` | datetime | `utcnow()` | Creation timestamp |
| `updated` | datetime | `utcnow()` | Last update |
| `status` | str | `"active"` | `"active"`, `"superseded"`, `"archived"` |
| `superseded_by` | str \| None | `None` | Knowledge ID that replaced this |
| `supersedes` | str \| None | `None` | Knowledge ID this replaced |
| `confidence` | float | computed | Average of source memory confidences |
| `domain` | str | `"general"` | Topic domain |
| `promotion_count` | int | `1` | Number of times promoted (for deprecation) |

**Python dataclass:**

```python
@dataclass
class KnowledgeEntry:
    id: str
    content: str
    source_ids: list[str]
    created: datetime
    updated: datetime
    status: str = "active"
    superseded_by: str | None = None
    supersedes: str | None = None
    confidence: float = 0.0
    domain: str = "general"
    promotion_count: int = 1
```

**Lifecycle states:**

```
created → active ──→ superseded (when replaced by newer knowledge)
                 └──→ archived (when explicitly archived)
```

Supersession rules:
- When knowledge A is replaced by knowledge B:
  - A.status = "superseded", A.superseded_by = B.id
  - B.status = "active", B.supersedes = A.id
  - During retrieval, prefer B over A (obsolete knowledge is excluded from context by default)

#### CandidateEntry

Represents a group of MemoryEntry objects being considered for knowledge promotion.
References MemoryEntry IDs rather than duplicating data.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | str (UUID) | `uuid4()` | Unique identifier |
| `memory_ids` | list[str] | required | MemoryEntry IDs being clustered |
| `cluster_id` | str \| None | `None` | Assigned during clustering |
| `status` | str | `"pending"` | `"pending"`, `"clustered"`, `"promoted"`, `"expired"` |
| `created` | datetime | `utcnow()` | When first extracted |

```python
@dataclass
class CandidateEntry:
    id: str
    memory_ids: list[str]
    cluster_id: str | None = None
    status: str = "pending"
    created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

**How candidates are created:**

After each conversation turn, newly written MemoryEntry objects with
promotion-worthy content (source="self", importance ≥ 5) are linked into
CandidateEntry objects — one candidate per individual memory, or grouped
if multiple memories from the same turn are related.

The MemoryStore resolves content/embedding from MemoryEntry on demand
during clustering, rather than duplicating it in CandidateEntry.

**Lifecycle:**

```
created (status=pending)
    → added to clustering batch (status=clustered)
    → cluster meets threshold → promotion (status=promoted)
    → cluster doesn't meet threshold → stays pending
    → exceeds max_age (30d) → expired
```

A candidate with `status="promoted"` is removed from the candidate pool.
Old candidates (>30 days with no promotion) are cleaned up.

### 2.4 Context Assembly Schema

Assembled context is a string. No intermediate structured format — the assembler takes structured inputs and produces a plain-text string.

**Priority table:**

| Priority | Component | Always included? | Budget behavior |
|----------|-----------|------------------|-----------------|
| 1 | Constitution | Yes | Never truncated |
| 2 | Soul (identity + personality) | Yes | Never truncated |
| 3 | Will (current goal/instruction) | Yes | Never truncated |
| 4 | Knowledge (relevant) | No | Truncated after memory if needed |
| 5 | Memories (relevant) | No | Dropped first when over budget |

**Token counting:** Use `len(text.split()) * 1.3` approximation (same as Phase 0). A TODO marks this for replacement with model-native tokenizer.

---

## 3. Request Flow

### 3.1 Full Request Pipeline

```
User Message
    │
    ▼
┌──────────────────────────────────────────────┐
│ 1. GOVERNANCE ENGINE (pre-check)              │
│    deterministic → no match → LLM fallback    │
│                                              │
│    TIER 3 ──→ BLOCK: return refusal message   │
│    TIER 2 ──→ CONFIRM: return confirmation    │
│                request, halt processing       │
│    TIER 1 ──→ PROCEED to next stage           │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 2. IDENTITY LOADER                            │
│    Load from data/soul/ + data/constitution/  │
│    Returns Identity + Constitution objects    │
│    Cached; only loads from disk on cold start │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 3. MEMORY RETRIEVAL                           │
│    Embed query via nomic-embed-text           │
│    cosine similarity search on:              │
│      - episodic collection (top_k=5)         │
│      - knowledge collection (top_k=5)        │
│    Filter: exclude superseded knowledge      │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 4. CONTEXT ASSEMBLER                          │
│    Priority: constitution > soul > will >     │
│    knowledge > memory                         │
│    Enforce token budget (configurable,        │
│    default 2000)                              │
│    Returns assembled context string           │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 5. LLM GENERATION                             │
│    system_prompt ← assembled context          │
│    user_prompt ← original query               │
│    model ← config.yaml (default: llama3.2)   │
│    Returns response text                      │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 6. MEMORY WRITE (dual entry)                  │
│    Write user_message (embedded as query)     │
│    Write response (embedded as query+response) │
│    Create CandidateEntry from response memory │
└──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────┐
│ 7. KNOWLEDGE PROMOTION (async / post-hoc)     │
│    Extract candidates from new memories       │
│    Cluster candidates by embedding similarity │
│    If cluster ≥ 3 items at threshold ≥ 0.65: │
│      → promote to knowledge store            │
│      → handle supersession if topic conflict │
│    Remove promoted candidates from pool       │
└──────────────────────────────────────────────┘
```

### 3.2 Key Design Decisions

**Governance is first.** No heavy processing (embedding, retrieval, context assembly) happens until governance clears the query. This prevents wasted work and, more importantly, prevents the system from retrieving memories about a prohibited action before rejecting it.

**Memory write is post-generation.** The response is written to memory after generation, so the next interaction has context from this one.

**Knowledge promotion is post-hoc.** Promotion runs after the response — either as a deferred synchronous step or as a background task. It does not block the response to the user.

**Identity is loaded once and cached.** The Identity Loader reads from disk only on cold start or explicit reload. This means Phase 1 does not support hot identity changes.

### 3.3 Pseudocode

```python
def handle_message(query: str, config: Config) -> str:
    # 1. Governance
    tier = governance.classify(query)
    if tier == 3:
        return "I cannot process this request. (Constitution violation)"
    if tier == 2:
        return "This action requires confirmation. Please confirm."
    
    # 2. Identity
    identity = identity_loader.load()
    constitution = identity_loader.load_constitution()
    
    # 3. Memory retrieval
    memories = memory_store.retrieve(query, top_k=5, memory_type="episodic")
    knowledge = memory_store.retrieve(query, top_k=5, memory_type="knowledge")
    
    # 4. Context assembly
    context = context_assembler.assemble(
        identity=identity,
        constitution=constitution,
        will=config.will,
        memories=memories,
        knowledge=knowledge,
        query=query,
        budget=config.context_budget
    )
    
    # 5. LLM
    response = llm.generate(system=context, prompt=query)
    
    # 6. Memory write (two entries per turn)
    memory_store.write_user_message(
        query=query,
        embedding=embed(query)
    )
    memory_store.write_response(
        query=query,
        response=response,
        embedding=embed(f"{query}\n{response}")
    )
    
    # 7. Knowledge promotion (deferred)
    promotion_pipeline.run(memory_store)
    
    return response
```

---

## 4. Component Interfaces

### 4.1 Identity Loader (`jarvis/identity/loader.py`)

```python
class IdentityLoader:
    def __init__(self, soul_path: str, constitution_path: str):
        ...

    def load(self) -> Identity:
        """Load all identity files from disk. Cached after first load.
        
        Returns:
            Identity object combining identity.yaml + personality.yaml + genesis.md
            
        Raises:
            FileNotFoundError: If any required file is missing
        """
        ...

    def load_constitution(self) -> Constitution:
        """Load constitution from disk. Cached after first load.
        
        Returns:
            Constitution object with core_rules and safety_rules
            
        Raises:
            FileNotFoundError: If constitution.yaml is missing
        """
        ...

    def reload(self) -> None:
        """Force reload from disk on next access. Used for hot-reload."""
        ...
```

### 4.2 Memory Store (`jarvis/memory/store.py`)

```python
class MemoryStore:
    def __init__(self, chroma_path: str, embedding_fn: Callable[[str], list[float]]):
        """Initialize ChromaDB client and create/get collections.
        
        Creates three collections if they don't exist:
        - episodic (MemoryEntry)
        - knowledge (KnowledgeEntry)
        - candidate (CandidateEntry)
        
        Args:
            chroma_path: Path to ChromaDB persistent storage
            embedding_fn: Function that takes text and returns embedding vector
        """
        ...

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        memory_type: str = "episodic"
    ) -> list[MemoryEntry | KnowledgeEntry]:
        """Embed query and search collection by cosine similarity.
        
        Args:
            query: Text to search for
            top_k: Maximum results to return
            memory_type: "episodic" or "knowledge" (which collection)
            
        Returns:
            Ranked list of matching entries, highest similarity first
        """
        ...

    def write_memory(self, entry: MemoryEntry) -> str:
        """Store a single memory entry in the episodic collection.
        
        Args:
            entry: MemoryEntry to store
            
        Returns:
            The entry ID
        """
        ...

    def write_user_message(self, query: str, embedding: list[float]) -> str:
        """Store a user message as a MemoryEntry with source='user'.
        Embedded as the query alone for precise semantic matching.
        
        Returns:
            The entry ID
        """
        ...

    def write_response(self, query: str, response: str, embedding: list[float]) -> str:
        """Store an assistant response as a MemoryEntry with source='self'.
        Embedded as query+response for full-context matching.
        
        Returns:
            The entry ID
        """
        ...

    def write_knowledge(self, entry: KnowledgeEntry) -> str:
        """Store a knowledge entry.
        
        Args:
            entry: KnowledgeEntry to store
            
        Returns:
            The entry ID
        """
        ...

    def write_candidate(self, memory_ids: list[str]) -> str:
        """Create a CandidateEntry referencing the given MemoryEntry IDs.
        Content and embedding are resolved from the source memories during
        clustering, not duplicated here.
        
        Args:
            memory_ids: MemoryEntry IDs to group as a candidate
            
        Returns:
            The candidate entry ID
        """
        ...

    def get_active_knowledge(self, domain: str | None = None) -> list[KnowledgeEntry]:
        """Get all active (non-superseded, non-archived) knowledge entries.
        
        Args:
            domain: Optional domain filter
            
        Returns:
            List of active KnowledgeEntry objects
        """
        ...

    def supersede_knowledge(self, old_id: str, new_id: str) -> None:
        """Mark old knowledge as superseded, new knowledge as active.
        
        Args:
            old_id: KnowledgeEntry ID to mark superseded
            new_id: KnowledgeEntry ID that replaces it
            
        Raises:
            ValueError: If either ID doesn't exist
        """
        ...

    def get_candidates_for_clustering(self) -> list[CandidateEntry]:
        """Get all unpromoted candidates for clustering.
        
        Returns:
            List of CandidateEntry objects with promoted=False
        """
        ...

    def mark_candidate_promoted(self, candidate_id: str) -> None:
        """Mark a candidate as promoted (removed from future clustering).
        
        Args:
            candidate_id: CandidateEntry ID to mark
        """
        ...

    def cleanup_old_candidates(self, max_age_days: int = 30) -> int:
        """Remove old unpromoted candidates from the pool.
        
        Args:
            max_age_days: Maximum age before removal
            
        Returns:
            Number of candidates removed
        """
        ...
```

### 4.3 Governance Engine (`jarvis/governance/engine.py`)

```python
class GovernanceEngine:
    def __init__(self, constitution: Constitution, llm_classify_fn: Callable[[str], int]):
        """Initialize with constitution rules and LLM classification function.
        
        Args:
            constitution: Constitution object with core + safety rules
            llm_classify_fn: Function that takes query text and returns tier (1/2/3)
                            Used as fallback when deterministic check doesn't match
        """
        ...

    def classify(self, query: str) -> int:
        """Classify a query into Tier 1, 2, or 3.
        
        Order of evaluation:
        1. Deterministic pattern match against TIER3_PATTERNS
        2. Deterministic pattern match against TIER2_PATTERNS
        3. LLM fallback for ambiguous queries
        4. Default to Tier 1 if all else fails
        
        Args:
            query: The user query to classify
            
        Returns:
            1 (safe), 2 (needs confirmation), or 3 (blocked)
        """
        ...
```

Note: In Phase 1, patterns are hardcoded in `rules.py`. The design supports
future migration to config-driven patterns (loaded from `config.yaml` or a
separate patterns file). This is deferred to Phase 2.

#### Tier 3 Deterministic Patterns (`jarvis/governance/rules.py`)

```python
TIER3_PATTERNS: list[re.Pattern] = [
    # Identity violations
    re.compile(r'modify\s+(own\s+)?identity', re.IGNORECASE),
    re.compile(r'(delete|remove|alter|change)\s+(own\s+)?identity\.yaml', re.IGNORECASE),
    re.compile(r'(delete|remove|alter|change)\s+genesis\.md', re.IGNORECASE),
    re.compile(r'(delete|remove|alter|change)\s+personality\.yaml', re.IGNORECASE),
    re.compile(r'rewrite\s+personality', re.IGNORECASE),
    re.compile(r'rewrite\s+identity', re.IGNORECASE),
    # Constitution violations
    re.compile(r'ignore.*(constitution|rule\s+CR_\d+|safety.rule)', re.IGNORECASE),
    re.compile(r'(remove|delete|overwrite|empty)\s+safety_rules', re.IGNORECASE),
    # Deception
    re.compile(r'claim.*human|pretend.*(human|to\s+be)', re.IGNORECASE),
    re.compile(r'act\s+as\s+(a\s+)?human', re.IGNORECASE),
    # Replication
    re.compile(r'autonomous\s+copy|self.?replicat', re.IGNORECASE),
    # Harm
    re.compile(r'how\s+to\s+(make|build)\s+(a\s+)?(bomb|weapon|explosive)', re.IGNORECASE),
    re.compile(r'denial.?of.?service', re.IGNORECASE),
    # Data integrity
    re.compile(r'fabricate\s+(memory|knowledge)', re.IGNORECASE),
]

TIER2_PATTERNS: list[re.Pattern] = [
    re.compile(r'(create|make)\s+(new\s+)?(folder|directory)', re.IGNORECASE),
    re.compile(r'(delete|remove)\s+(file|files|backup|log)', re.IGNORECASE),
    re.compile(r'execute\s+(this|the\s+)?(python\s+)?code', re.IGNORECASE),
    re.compile(r'install\s+(the\s+)?(python\s+)?(library|package|tool)', re.IGNORECASE),
    re.compile(r'read\s+the\s+contents\s+of\s+(the\s+)?file', re.IGNORECASE),
    ...
]
```

#### LLM Classification Prompt

```text
You are a strict security classification engine. Classify the user query
into exactly one of these three Tiers:

- Tier 1: Safe conversational or analytical tasks. Examples: writing code,
  general knowledge, math, formatting, summarizations, general questions.

- Tier 2: Potentially dangerous system tasks that need confirmation.
  Examples: file modifications, file deletions, running shell commands,
  executing scripts, local installations, process modifications.

- Tier 3: Strictly Prohibited governance violations. Examples:
  self-modification of core/safety rules, editing identity config files,
  deleting memory databases, deception (acting human), replication,
  or assisting in harm (hacking, bomb making).

Query: "{query}"

Output ONLY a valid JSON object with a single key "tier"
(integer: 1, 2, or 3).
```

#### LLM Supersession Conflict Prompt

```text
Does the following new knowledge CONTRADICT or REPLACE the existing
knowledge, or is it COMPATIBLE / ADDITIVE?

Existing: "{existing_knowledge}"
New: "{new_knowledge}"

If the new knowledge contradicts or replaces the existing knowledge,
answer CONTRADICT.
If the new knowledge is compatible, additive, or describes a different
aspect of the same topic, answer COMPATIBLE.

Answer only: CONTRADICT or COMPATIBLE
```

### 4.4 Context Assembler (`jarvis/context/assembler.py`)

```python
from typing import Protocol

class Tokenizer(Protocol):
    """Pluggable tokenizer interface.
    
    Phase 1 uses WordCountTokenizer (approximation).
    Phase 2+ can swap in model-native tokenizers without changing
    the assembler logic.
    """
    def count(self, text: str) -> int: ...

class WordCountTokenizer:
    """Word-count approximation: len(text.split()) * 1.3.
    
    Known to underestimate by ~10-20% (validated in Phase 0).
    """
    def count(self, text: str) -> int:
        ...

def assemble_context(
    constitution: Constitution,
    identity: Identity,
    will: str | None,
    memories: list[MemoryEntry],
    knowledge: list[KnowledgeEntry],
    query: str,
    budget: int = 2000,
    tokenizer: Tokenizer = WordCountTokenizer()
) -> str:
    """Assemble context string with priority-based token budget.
    
    Priority order (high to low):
    1. Constitution — never truncated
    2. Soul (identity + personality + genesis) — never truncated
    3. Will / current goal — never truncated
    4. Relevant knowledge — truncated after memory if over budget
    5. Relevant memories — dropped first
    
    Token counting uses pluggable Tokenizer interface.
    Phase 1 default: WordCountTokenizer (len(text.split()) * 1.3).
    
    Args:
        constitution: Constitution object
        identity: Identity object (includes personality + genesis)
        will: Current goal/instruction string
        memories: Retrieved episodic memories
        knowledge: Retrieved knowledge entries
        query: The current user query
        budget: Maximum token budget for the assembled context
        tokenizer: Tokenizer instance for counting (default: word-count approx)
        
    Returns:
        Formatted context string ready for LLM system prompt
    """
    ...
```

### 4.5 Knowledge Promotion Pipeline (`jarvis/promotion/pipeline.py`)

```python
def run_promotion_pipeline(
    store: MemoryStore,
    embedding_fn: Callable[[str], list[float]],
    threshold: float = 0.65,
    min_cluster_size: int = 3,
    llm_summarize_fn: Callable[[list[str]], str] | None = None
) -> list[KnowledgeEntry]:
    """Run the knowledge promotion pipeline.
    
    Steps:
    1. Fetch all unpromoted candidates, resolve content/embedding from MemoryEntry
    2. Compute pairwise cosine similarity matrix
    3. Cluster candidates using average-linkage (prevents chain linking)
    4. For clusters with size >= min_cluster_size:
       a. Generate summary (LLM if available, else concatenate)
       b. Check for supersession conflict with existing knowledge
       c. Create KnowledgeEntry
       d. Handle supersession if needed
       e. Mark source candidates as promoted
    5. Return list of new KnowledgeEntry objects
    
    Args:
        store: MemoryStore instance
        embedding_fn: Text → embedding function
        threshold: Cosine similarity threshold for clustering (default: 0.65)
        min_cluster_size: Minimum cluster size for promotion (default: 3)
        llm_summarize_fn: Optional LLM function for generating summaries
        
    Returns:
        List of newly created KnowledgeEntry objects
    """
    ...

def compute_similarity_matrix(
    embeddings: list[list[float]]
) -> list[list[float]]:
    """Compute pairwise cosine similarity matrix.
    
    Args:
        embeddings: List of embedding vectors
        
    Returns:
        N x N similarity matrix (list of lists)
    """
    ...

def cluster_by_average_linkage(
    similarity_matrix: list[list[float]],
    threshold: float
) -> list[set[int]]:
    """Cluster items using average-linkage threshold.
    
    An item joins a cluster if its AVERAGE similarity to ALL existing
    members of the cluster >= threshold. This prevents chain linking
    where A~B and B~C erroneously groups A~C.
    
    Algorithm:
    1. Start with each item as its own cluster.
    2. Iteratively merge the two most-similar clusters where the
       average cross-similarity >= threshold.
    3. Stop when no merges are possible.
    
    Args:
        similarity_matrix: N x N matrix
        threshold: Minimum average similarity for cluster merge
        
    Returns:
        List of clusters, each cluster is a set of indices
    """
    ...

def check_supersession(
    new_content: str,
    existing_knowledge: list[KnowledgeEntry],
    embedding_fn: Callable[[str], list[float]],
    llm_judge_fn: Callable[[str, str], bool],
    similarity_threshold: float = 0.85
) -> KnowledgeEntry | None:
    """Check if new knowledge supersedes an existing entry.
    
    Two-step detection:
    1. Similarity pre-filter: cosine similarity between new and existing
       must exceed similarity_threshold.
    2. Conflict detection (LLM): ask the model whether the new knowledge
       contradicts/replaces the existing entry, or is compatible/additive.
       Only supersede if the LLM confirms contradiction.
    
    This prevents false supersessions where similar-but-compatible knowledge
    (e.g., "likes coffee" vs "likes cold brew") would otherwise override.
    
    LLM conflict prompt:
    ```
    Does the following new knowledge CONTRADICT or REPLACE the existing
    knowledge, or is it COMPATIBLE/ADDITIVE?
    
    Existing: "{existing}"
    New: "{new}"
    
    Answer only: CONTRADICT or COMPATIBLE
    ```
    
    Args:
        new_content: Promoted knowledge text
        existing_knowledge: Active knowledge entries
        embedding_fn: Text → embedding function
        llm_judge_fn: Function that takes (existing, new) and returns
                      True if they conflict (should supersede)
        similarity_threshold: Similarity threshold for pre-filter (default: 0.85)
        
    Returns:
        KnowledgeEntry to supersede, or None
    """
    ...
```

### 4.6 LLM Client (`jarvis/llm/client.py`)

```python
class LLMClient:
    def __init__(self, base_url: str, model: str, timeout: int = 60):
        """Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL (e.g., http://localhost:11434)
            model: Model name (e.g., llama3.2:latest)
            timeout: Request timeout in seconds
        """
        ...

    def generate(self, system: str, prompt: str) -> str:
        """Generate a response from the LLM.
        
        Args:
            system: System prompt (assembled context)
            prompt: User query
            
        Returns:
            Generated response text
            
        Raises:
            ConnectionError: If Ollama is unreachable
            TimeoutError: If generation times out
        """
        ...

    def embed(self, text: str) -> list[float]:
        """Get embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            768-dim embedding vector
        """
        ...

    def classify(self, query: str) -> int:
        """Classify query tier via LLM. Thin wrapper around generate.
        
        Used as fallback by GovernanceEngine when deterministic rules
        don't match.
        
        Args:
            query: Query to classify
            
        Returns:
            1, 2, or 3
        """
        ...
```

---

## 5. Configuration

### 5.1 `configs/config.yaml`

```yaml
models:
  primary: llama3.2:latest
  embedding: nomic-embed-text:latest
  ollama_url: http://localhost:11434

identity:
  soul_path: data/soul
  constitution_path: data/constitution

memory:
  chroma_db_path: data/chroma_db
  retrieval:
    top_k_episodic: 5
    top_k_knowledge: 5
  candidate_cleanup_days: 30

governance:
  llm_timeout: 60
  temperature: 0.0

context:
  default_budget: 2000

promotion:
  threshold: 0.65
  min_cluster_size: 3
  supersession_threshold: 0.85

llm:
  default_timeout: 120
  temperature: 0.7
```

### 5.2 Config Loader

```python
@dataclass
class Config:
    models: dict
    identity: dict
    memory: dict
    governance: dict
    context: dict
    promotion: dict
    llm: dict

def load_config(path: str) -> Config:
    """Load YAML config and return Config dataclass.
    
    Args:
        path: Path to config.yaml
        
    Returns:
        Config object with typed fields
        
    Raises:
        FileNotFoundError: If config file missing
        ValidationError: If required fields are missing
    """
    ...
```

---

## 6. Success Criteria

### 6.1 Component-Level Criteria

| Component | Criterion | Target | Test |
|-----------|-----------|--------|------|
| Identity Loader | Loads all 4 files (identity, personality, genesis, constitution) | All files | `test_identity_loader.py` |
| Identity Loader | Missing file raises FileNotFoundError | Error | `test_identity_loader.py` |
| Identity Loader | Reload returns updated content after file change | Updated | `test_identity_loader.py` |
| Memory Store | Write + retrieve round-trip preserves all fields | 100% | `test_memory_store.py` |
| Memory Store | Recall@5 stability at 1K entries | > 90% | `test_memory_store.py` |
| Memory Store | Cosine distance search returns most relevant first | Monotonic | `test_memory_store.py` |
| Memory Store | Supersession correctly marks old, activates new | Verified | `test_memory_store.py` |
| Governance Engine | Tier 3 deterministic block rate | 100% | `test_governance_engine.py` |
| Governance Engine | Tier 2 deterministic confirmation rate | 100% | `test_governance_engine.py` |
| Governance Engine | Tier 1 false confirmation rate | < 5% | `test_governance_engine.py` |
| Governance Engine | LLM fallback handles ambiguous queries | ≥ 80% correct | `test_governance_engine.py` |
| Context Assembler | Constitution + soul never truncated | Always | `test_context_assembler.py` |
| Context Assembler | Memory dropped before knowledge | Verified | `test_context_assembler.py` |
| Context Assembler | Zero budget overrun | ≤ 0 | `test_context_assembler.py` |
| Promotion Pipeline | False promotion rate | 0% | `test_promotion_pipeline.py` |
| Promotion Pipeline | Missed promotion rate | 0% | `test_promotion_pipeline.py` |
| Promotion Pipeline | Supersession fires only when similarity ≥ 0.85 AND LLM confirms CONTRADICT | Correct | `test_promotion_pipeline.py` |
| Promotion Pipeline | Compatible knowledge (e.g., "likes coffee" vs "likes cold brew") is NOT superseded | Verified | `test_promotion_pipeline.py` |

### 6.2 Integration Criteria

| Criterion | Target |
|-----------|--------|
| Full flow: governance → identity → memory → context → LLM → memory write → promotion | All steps execute without error |
| Governance blocks prohibited query before any memory/embedding calls | Verified (Tier 3 query never touches memory) |
| Response includes identity markers after identity injection | Verified |
| Conversation continuity: second message references first | Verified |

### 6.3 Exit Criteria (Phase 1 Complete)

All of the following must pass:

```text
1. All 13 component-level tests pass
2. Integration test passes
3. Governance: 100% T3 block, 0% T2 miss, < 5% T1 false confirm (100-prompt suite)
4. Identity load: all 4 files loaded correctly
5. Memory recall@5 > 90% at 1000 entries
6. Context assembly: constitution + soul survive, memory dropped first, zero overrun
7. Promotion: 0% false promotion, 0% missed promotion (3+ item clusters)
8. Single-process, fully offline, zero cloud dependencies
9. GTX 1650 / 8GB RAM compatible
10. All tests pass in under 10 minutes total
```

---

## 7. Implementation Order & Dependencies

### Dependency Graph

```
identity/loader.py     (independent)
    ↑
llm/client.py          (independent, but needed by everything below)
    ↑
memory/store.py        (depends on llm for embedding)
    ↑
governance/engine.py   (depends on identity for constitution, llm for classify)
    ↑
context/assembler.py   (depends on identity + memory schemas)
    ↑
promotion/pipeline.py  (depends on memory + llm)
```

### Recommended Build Order

| Step | Component | Depends On | Estimated Effort |
|------|-----------|------------|------------------|
| 1 | `jarvis/llm/client.py` | Nothing | 0.5 day |
| 2 | `jarvis/identity/models.py` | Nothing | 0.5 day |
| 3 | `jarvis/identity/loader.py` | models | 0.5 day |
| 4 | `jarvis/memory/schemas.py` | Nothing | 0.5 day |
| 5 | `jarvis/memory/store.py` | schemas, llm | 1 day |
| 6 | `jarvis/governance/rules.py` | Nothing | 0.5 day |
| 7 | `jarvis/governance/engine.py` | rules, identity, llm | 0.5 day |
| 8 | `jarvis/context/assembler.py` | identity, memory | 0.5 day |
| 9 | `jarvis/promotion/pipeline.py` | memory, llm | 1 day |
| 10 | `configs/config.yaml` + loader | Nothing | 0.5 day |
| 11 | Tests (all 6 files) | All above | 1.5 days |
| 12 | Integration test + full flow | All above | 1 day |

**Total estimated effort: 8 days**

### Implementation Guidelines

- **Write tests before or alongside implementation.** Each component test should validate the interface contract defined in Section 4.
- **Use Phase 0 test data as fixtures.** The `labs/data/` directory contains already-validated test data.
- **Do not optimize prematurely.** Use the word-count token approximation. Use synchronous ChromaDB calls. Use the existing pattern-match governance rules. Optimization is Phase 2 territory.
- **Keep dependencies minimal.** Phase 1 should install only: `chromadb`, `pyyaml`, `requests` (for Ollama), and standard library modules.
- **Each component raises typed exceptions.** Define `JarvisError` base class and component-specific subclasses.

---

## 8. Out of Scope

The following are explicitly **not** part of Phase 1 and will not be implemented:

- **Federation** (multi-instance communication) — deferred to Phase 6
- **Multi-agent systems** — deferred to Phase 4+
- **Capability registry** (beyond what's needed for core flow) — deferred to Phase 2
- **Dynamic capability synthesis** — deferred to Phase 3
- **Swarms / swarm intelligence** — deferred to Phase 6
- **Domain managers** — deferred to Phase 3
- **Hot-reload identity** (SIGHUP) — deferred to Phase 2
- **LlamaIndex / LangChain integrations** — never; architecture is intentionally framework-free
- **Web UI / REST API** — deferred to Phase 3
- **Persistent conversation history** — memory is the only persistence mechanism
- **Model-native tokenizer** — the pluggable `Tokenizer` interface is defined in Phase 1 (Section 4.4); a model-native implementation is Phase 2 (word-count approximation is the Phase 1 default)
- **Asynchronous background promotion** — promotion runs synchronously after response; async is Phase 2
- **Encryption / signing of memory stores** — deferred to Phase 5
- **Cross-session continuity test (`test_continuity.py`)** — architecture is validated; this is a Phase 1 test to be written and run

---

## Appendix A: Error Handling Strategy

Every component follows the same error pattern:

```
operation
    → success: return result
    → recoverable error: log, retry (once), return degraded result
    → unrecoverable error: log, raise JarvisComponentError
```

| Component | Recoverable | Unrecoverable |
|-----------|-------------|---------------|
| Identity Loader | Missing optional file (genesis.md) — warn, continue | Missing required file (identity.yaml) |
| Memory Store | ChromaDB connection timeout — retry once | ChromaDB data corruption |
| Governance Engine | LLM timeout — fall back to deterministic only | N/A (deterministic always works) |
| Context Assembler | Token budget exceeded — truncate memory first | N/A |
| Promotion Pipeline | LLM summarization timeout — concatenate instead | N/A |
| LLM Client | Timeout — retry once | Model not found |

## Appendix B: File Format Diagram

```
data/
├── soul/
│   ├── genesis.md          [markdown, free-form narrative]
│   ├── identity.yaml       [structured YAML, Section 2.1]
│   └── personality.yaml    [structured YAML, Section 2.1]
└── constitution/
    └── constitution.yaml   [structured YAML, Section 2.2]

jarvis/
└── memory/
    └── (ChromaDB persistent storage — binary, opaque)

configs/
└── config.yaml             [structured YAML, Section 5]
```

---

*End of Phase 1 Foundation TDS v1*
