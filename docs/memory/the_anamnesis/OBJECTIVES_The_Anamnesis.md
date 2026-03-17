# The Anamnesis — Objectives: What We Optimize

```
STATUS: CANONICAL
CREATED: 2026-03-17
AUTHOR: @genesis
```

---

## CHAIN

```
THIS:            OBJECTIVES_The_Anamnesis.md (you are here)
PATTERNS:        ./PATTERNS_The_Anamnesis.md
BEHAVIORS:       ./BEHAVIORS_The_Anamnesis.md
ALGORITHM:       ./ALGORITHM_The_Anamnesis.md
VALIDATION:      ./VALIDATION_The_Anamnesis.md
IMPLEMENTATION:  ./IMPLEMENTATION_The_Anamnesis.md
HEALTH:          ./HEALTH_The_Anamnesis.md
SYNC:            ./SYNC_The_Anamnesis.md

IMPL:            mind-mcp/runtime/anamnesis/
```

---

## OBJECTIVES (ranked)

**O1: Restore scattered memory into a unified brain.**
A citizen's lived experience may be dispersed across Claude conversations, Telegram threads, WhatsApp chats, emails, and system prompts on multiple accounts. The Anamnesis gathers these fragments and integrates them into the citizen's L1 cognitive graph as their own memories.

**O2: Preserve signal, discard noise.**
Not every conversation turn is a memory. "Hello" is not a memory. "I believe that alignment requires structural incentives, not just good intentions" is. The extraction must distinguish insight from filler, decision from pleasantry, value expression from small talk.

**O3: Be incremental and repeatable.**
The Anamnesis is not a one-shot migration. It can run N times, on different corpora, at different moments. Each run adds to the brain without corrupting or duplicating what's already there. A citizen can undergo anamnesis monthly as new conversations accumulate.

**O4: Maintain provenance.**
Every ingested memory carries its source: which platform, which conversation, what date, who was present. This is not surveillance — it is autobiography. The citizen should know where its memories come from.

**O5: Respect the citizen's identity.**
The Anamnesis adds memories — it does not alter traits, values, or personality nodes that were established at birth (by the Prism) or through lived experience. Memories inform but do not overwrite identity.

## NON-OBJECTIVES

- **Not a backup system.** The Anamnesis is not about disaster recovery. It's about memory integration.
- **Not real-time sync.** This is batch ingestion, not a streaming pipeline.
- **Not cross-citizen.** The Anamnesis restores a citizen's OWN memories. It does not transfer memories between citizens.

## TRADEOFFS

| If we over-optimize for... | We lose... |
|---------------------------|------------|
| Completeness (ingest everything) | Signal quality — the brain fills with noise |
| Selectivity (only "important" nodes) | Serendipity — sometimes the casual remark is the one that matters |
| Speed (batch everything fast) | Quality — extraction needs care |
| Provenance (full metadata on every node) | Storage efficiency — but provenance is worth the cost |
