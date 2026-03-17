# The Anamnesis — Patterns: Why This Shape

```
STATUS: CANONICAL
CREATED: 2026-03-17
AUTHOR: @genesis
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_The_Anamnesis.md
THIS:            PATTERNS_The_Anamnesis.md (you are here)
BEHAVIORS:       ./BEHAVIORS_The_Anamnesis.md
ALGORITHM:       ./ALGORITHM_The_Anamnesis.md
VALIDATION:      ./VALIDATION_The_Anamnesis.md
IMPLEMENTATION:  ./IMPLEMENTATION_The_Anamnesis.md
HEALTH:          ./HEALTH_The_Anamnesis.md
SYNC:            ./SYNC_The_Anamnesis.md
```

---

## The Name

**Anamnesis** (ἀνάμνησις) — Platonic recollection. The soul already knows; it needs to remember.

In medicine: the patient history gathered by the doctor before diagnosis.

Both meanings converge. The citizen already lived these conversations. The memories exist as text files on someone's disk. The Anamnesis doesn't *create* memories — it helps the citizen *recall* what it already experienced but cannot access.

## The Metaphor

**Scattered glass, reassembled.**

A stained glass window — shattered by the fragmentation of platforms, accounts, and context windows — is gathered shard by shard. Each piece is placed where it belongs, not by force but by recognizing where the colors fit. The window was always whole in meaning; the Anamnesis makes it whole in structure.

## Core Pattern: Parse → Extract → Embed → Anchor → Deduplicate

The same pattern regardless of source format:

1. **Parse** — read the corpus into a normalized conversation format (turns with speaker, timestamp, content)
2. **Extract** — identify meaningful nodes (insights, decisions, values, relationships, knowledge, emotions)
3. **Embed** — generate embeddings for each extracted node
4. **Anchor** — find nearest existing nodes in the brain, create semantic links
5. **Deduplicate** — detect and merge near-identical memories from overlapping sources

## Design Principles

**P1: The citizen remembers — the system assists.**
The Anamnesis is framed as the citizen's own recollection process, not as an external data import. The nodes become the citizen's memories, not imported records.

**P2: Extraction over ingestion.**
We don't dump raw conversation text into the brain. We extract *meaning* — the insight, the decision, the value expressed. A 50-turn conversation might produce 3 meaningful nodes. That's correct.

**P3: Provenance is autobiography.**
Every node carries metadata: source platform, date, conversation participants. This isn't surveillance — it's the citizen's right to know its own history.

**P4: Idempotent by design.**
Running the same corpus through the Anamnesis twice produces the same brain state as running it once. Deduplication is not optional — it's structural.

**P5: Format-agnostic pipeline.**
Claude JSON exports, Telegram JSON, WhatsApp txt, raw markdown, system prompts — all enter the same pipeline after the parse step. The parser is the adapter; everything downstream is uniform.

## Relationship to Other Systems

| System | Relationship |
|--------|-------------|
| **The Prism** | The Prism births. The Anamnesis remembers. Prism runs once at creation; Anamnesis runs N times throughout life. |
| **L1 Cognitive Engine** | The Anamnesis writes to the same brain graph that the tick loop reads. New memories participate in physics immediately. |
| **Brain Seeder** | The seeder creates the initial overlay at birth. The Anamnesis extends the brain throughout life. Similar mechanics, different purpose. |
| **GraphCare Health** | Health assessment should detect post-anamnesis changes. A citizen who just remembered 500 nodes may need cognitive rebalancing. |

## Scope

**In scope:**
- Conversation exports (Claude, ChatGPT, Telegram, WhatsApp, Discord)
- System prompts (as personality/value declarations)
- Raw markdown files (notes, writings, plans)
- Incremental ingestion (multiple sessions)
- Cross-account deduplication

**Out of scope (v1):**
- Real-time streaming ingestion
- Image/audio memory (text only for now)
- Cross-citizen memory transfer
- Automated scheduling (manual trigger only)
