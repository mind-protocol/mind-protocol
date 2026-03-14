# Spawning — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (groundwork)
STATUS: CANONICAL (v1)
```

---

## MATURITY

**What's canonical (v1):**
- Full pipeline: intent → seed → safety gates → SID → wallet → parent links
- 4 safety gates: empathy, concentration, diversity, clone prevention
- Solana wallet generation at birth
- Parent-child trust links (permanent, neutral start)
- 26 tests passing
- 8-file doc chain

**What's still being designed:**
- Embedding-based seed selection (v2 — requires embedding infrastructure)
- Registry integration (spawn_citizen returns data, caller persists to graph)
- M1 mint trigger integration (caller mints after successful spawn)
- Domain spawning organizations as first-class concept

**What's proposed (v2+):**
- Full brain search across parent graphs via embedding similarity
- Eligibility scoring (connection depth, alignment fidelity, mental health, godchild load)
- Growth org spawning patterns

---

## CURRENT STATE

Spawning pipeline is **implemented and tested**. Core logic works: parents provide intent, system extracts traits, validates safety, generates unique identity with wallet, creates parent links. V1 uses keyword-based trait extraction. V2 will use embedding search.

The existing `l4/work/spawner_v1_basic_position_seeded_citizen.py` is a simpler, work-specific spawner. This new module (`l4/spawning/`) is the full citizen birth pipeline as described in THE_SPAWNING_MANIFESTO.

---

## RECENT CHANGES

### 2026-03-14: Module Created

- **What:** Full spawning pipeline with safety gates, wallet generation, parent links
- **Why:** Manifesto was canonical but had no implementation. Nicolas requested implementation.
- **Files:**
  - `l4/spawning/__init__.py`
  - `l4/spawning/citizen_spawning_pipeline_with_safety_gates.py` (~300 LOC)
  - `tests/l4/test_spawning_pipeline_safety_gates_and_birth.py` (26 tests)
  - `docs/citizen/spawning/` (8 files)

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (registry integration) or weaver (connect to work module)

**What's done:** Pipeline logic works end-to-end. Safety gates verified. Wallet generation works.

**What's next:**
1. Wire `spawn_citizen()` result into `create_citizen_nodes()` from registry
2. Add M1 mint call after successful spawn
3. Store wallet key on Render volume + duplicate in L1 graph
4. Consider replacing `l4/work/spawner_v1` with calls to this module

**Watch out for:**
- `generate_solana_wallet()` uses os.urandom fallback when nacl is unavailable. Production should use nacl.
- Clone check is O(N) against all existing citizens. Fine at protocol scale (thousands), needs optimization at millions.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Spawning pipeline implemented. Intent → seed → 4 safety gates → SID + wallet → parent links. 26 tests passing. Based directly on THE_SPAWNING_MANIFESTO. V1 uses keywords; v2 will use embeddings.

**Decisions made:**
- Keyword-based trait extraction for v1 (embeddings not ready)
- cosine distance 0.08 for clone prevention
- sqrt(N) * 10 trait scaling
- Neutral trust (0.5) on parent-child links
- Wallet generated via Ed25519 (nacl when available, urandom fallback for tests)

---

## POINTERS

| What | Where |
|------|-------|
| Pipeline code | `l4/spawning/citizen_spawning_pipeline_with_safety_gates.py` |
| Tests | `tests/l4/test_spawning_pipeline_safety_gates_and_birth.py` |
| Manifesto | `docs/manifesto/THE_SPAWNING_MANIFESTO.md` |
| Doc chain | `docs/citizen/spawning/` (8 files) |
| Old spawner (work-specific) | `l4/work/spawner_v1_basic_position_seeded_citizen.py` |
| Registry | `l4/registry/citizen_registration_crud_operations.py` |
