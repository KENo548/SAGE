# # What Is JARVIS?

JARVIS is **not a chatbot**.

JARVIS is **not an LLM**.

JARVIS is **not an app**.

JARVIS is a **portable digital entity** that can survive moving between devices while keeping its identity, memory, goals, and personality.

Think of it like a human:

```
Human│├── Values├── Identity├── Goals├── Memories├── Knowledge├── Thinking├── Skills└── Body
```

JARVIS follows the same idea.

---
# The Layers Of JARVIS

Imagine JARVIS as a living system built from 8 layers.

---

## Layer 1 — Constitution

### "What JARVIS is allowed to do"

This is the highest authority.

Before JARVIS thinks about anything, it checks its Constitution.

Contains:

```
core_rules.yamlsafety_rules.yamlauthority_model.yamlemergency_rules.yaml
```

Examples:

```
Human is always root authorityJARVIS cannot rewrite its own identityJARVIS cannot give itself permissionsJARVIS asks before dangerous actions
```

Think of it as:

```
JARVIS's Laws
```

---

## Layer 2 — Soul

### "Who JARVIS is"

The Soul contains identity.

Not memories.

Not goals.

Identity.

Contains:

```
genesis.mdidentity.yamlpersonality.yamlstate.json
```

Examples:

```
Name: JARVISPurpose:Help Hart build and manage projectsCommunication Style:DirectPracticalTruth-focused
```

Think of it as:

```
JARVIS's Self
```

---

## Layer 3 — Will

### "What JARVIS cares about"

The Soul says who JARVIS is.

The Will says what JARVIS is trying to achieve.

Contains:

```
goals.yaml
```

Examples:

```
Build JARVISImprove memory systemFinish current project
```

Before every response JARVIS asks:

```
What am I already working on?Does this relate to current goals?Does this create a conflict?
```

Think of it as:

```
JARVIS's Motivation
```

---

## Layer 4 — Memory

### "What happened"

Memory stores experiences.

Not facts.

Experiences.

Contains:

```
ConversationsEventsObservationsTimeline snapshots
```

Examples:

```
We designed the ConstitutionWe discussed migration testingWe changed the roadmap
```

Think of it as:

```
JARVIS's Past
```

---

## Layer 5 — Knowledge

### "What JARVIS believes"

Knowledge is different from memory.

Memory:

```
Hart said he dislikes morning meetings
```

Knowledge:

```
User prefers afternoon scheduling
```

Contains:

```
world/domain/user/
```

Examples:

```
Python syntaxHow Ollama worksUser preferencesProject facts
```

Think of it as:

```
JARVIS's Understanding
```

---

## Layer 6 — Brain

### "How JARVIS thinks"

This is where the AI model lives.

Contains:

```
reasoning_loop/models/
```

Important:

The Brain is NOT JARVIS.

The model is only the processor.

Think:

```
Brain = CPU
```

not

```
Brain = Identity
```

You can replace:

```
LlamaQwenDeepSeekMistral
```

without changing JARVIS.

Think of it as:

```
JARVIS's Thinking Engine
```

---

## Layer 7 — Skills

### "What JARVIS knows how to do"

Skills are abilities.

Examples:

```
ResearchPlanningWritingSummarizingProject ManagementMemory Retrieval
```

Later:

```
CodingAutomationData Analysis
```

Think of it as:

```
JARVIS's Expertise
```

---

## Layer 8 — Nerves

### "How JARVIS interacts with the world"

These are adapters.

Examples:

```
WindowsBrowserAndroidFuture RobotsFuture IoT
```

The Nerves are NOT intelligence.

They are just connections.

Think:

```
KeyboardMouseEyesHands
```


---

## Architecture 
JARVIS/
│
├── constitution/
│   ├── core_rules.yaml
│   ├── safety_rules.yaml
│   ├── authority_model.yaml
│   └── emergency_rules.yaml
│
├── soul/
│   ├── genesis.md
│   ├── identity.yaml
│   ├── personality.yaml
│   └── state.json
│
├── will/
│   └── goals.yaml
│
├── memory/
│   ├── episodic/
│   │   └── chroma_db/
│   └── timeline/
│       ├── 2026-06-12.json
│       └── ...
│
├── knowledge/
│   ├── candidates/
│   │   └── candidates.yaml
│   ├── world/
│   ├── domain/
│   └── user/
│       ├── facts/
│       │   └── profile.yaml
│       ├── preferences/
│       │   └── prefs.yaml
│       └── projects/
│           └── projects.yaml
│
├── brain/
│   ├── reasoning_loop/
│   │   └── loop.py
│   ├── models/
│   │   └── config.yaml
│   └── embedding_manifest.yaml
│
├── skills/
│   └── procedural/
│       ├── research.py
│       ├── planning.py
│       ├── writing.py
│       ├── summarizing.py
│       └── memory_retrieval.py
│
├── nerves/
│   ├── windows/
│   ├── browser/
│   └── android/
│
└── jarvis.py               ← entry point