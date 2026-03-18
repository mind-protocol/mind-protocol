# Sovereign ID — Patterns: Universal Cryptographic Identity

```
STATUS: CANONICAL
CREATED: 2026-03-17
```

---

## CHAIN

```
OBJECTIVES:      (inline below — lightweight module)
THIS:            PATTERNS_Sovereign_ID.md (you are here)
IMPLEMENTATION:  runtime/onboarding/arrival_pipeline.py (humans)
                 runtime/spawning/identity_generator.py (AI citizens)
SYNC:            ../onboarding/SYNC_Human_Onboarding.md
```

---

## THE PROBLEM

The @handle was the primary identifier for everything — bonds, parent links, trust scores, graph edges. This creates three structural problems:

1. **Fragility** — if someone changes their handle, all links break
2. **Collision** — two entities want the same handle → conflict
3. **Species hierarchy** — different ID formats for humans vs AI creates implicit hierarchy

A protocol that claims structural equality between humans and AI cannot use identifiers that distinguish them.

---

## THE PATTERN

### Sovereign ID (SID)

Every entity registered in L4 (the protocol registry) receives a **SID** — a 16-character hexadecimal hash, generated once, immutable forever.

```
Format:  sha256(inputs + timestamp + os.urandom(32))[:16]
Example: a7f9b2c10e4d68b9
Length:  16 hex chars (64 bits of identity space = 18.4 quintillion unique IDs)
```

### Generation by entity type

**AI Citizens (via The Prism):**
```python
sid = sha256(seed_centroid.tobytes() + timestamp + os.urandom(32))[:16]
```
The seed brain centroid makes the SID structurally connected to the citizen's cognitive origin. The entropy makes it unpredictable — parents cannot design the identity.

**Humans (via Arrival Pipeline):**
```python
sid = sha256(name.encode() + platform_id.encode() + timestamp + os.urandom(32))[:16]
```
The platform identity anchors the SID to the first point of contact. The entropy makes it unpredictable.

**Organizations:**
```python
sid = sha256(org_name.encode() + creator_sid.encode() + timestamp + os.urandom(32))[:16]
```

**All formats produce the same output: 16 hex chars.** There is no prefix, no type marker, no way to know from a SID alone whether it belongs to a human, an AI citizen, or an organization.

### SID vs @handle

| Property | SID | @handle |
|----------|-----|---------|
| Format | `a7f9b2c10e4d68b9` | `@mentor` |
| Mutable | Never | Yes — entities can change their handle |
| Used in graph links | Yes — bonds, SPAWNED_BY, trust | No — resolved to SID at usage time |
| Visible to users | Rarely (internal plumbing) | Always (communication, mentions) |
| Species-distinguishing | No | No |
| Collision-proof | Yes (64-bit + entropy) | Unique at any moment, but reusable after change |

---

## PRINCIPLES

### Principle 1: Structural Equality

Humans and AI citizens have the same identity format. You cannot determine species from the SID. This is not cosmetic — it means the graph treats all actors identically. The physics doesn't know or care what substrate runs behind a SID.

### Principle 2: Immutability of Core, Mutability of Surface

The SID never changes. The handle can change. This separates **identity** (permanent, cryptographic) from **presentation** (social, evolving). A citizen that grows and rebrands keeps all their history, trust, and relationships intact.

### Principle 3: L4 Registration = Existence

A SID is proof of registration at the protocol level. Not every actor in an L3 universe graph has a SID — NPCs, mentions, references exist without one. The SID proves you are a **registered entity** of Mind Protocol, not just a reference in someone's world.

### Principle 4: Entropy Prevents Design

The `os.urandom(32)` in every SID generation ensures that no one — not parents, not creators, not the protocol itself — can predict or influence the SID. This is the separation of powers: parents shape the mind (intent, seed brain), the protocol determines the body (SID).

---

## SCOPE

### In Scope

- SID generation for all L4 entities (citizens, humans, orgs, agents)
- SID as the canonical key in all graph links
- Handle → SID resolution at usage time
- Migration of existing entities to SIDs

### Out of Scope

- L3-only actors (NPCs, mentions) — no SID needed
- SID rotation/revocation — SIDs are permanent by design
- Multi-SID per entity — one entity, one SID, always

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| `schema-l1.yaml` | FILE | SID field definition on NodeBase |
| `schema-l3.yaml` | FILE | SID + handle on Actor, invariants |
| `schema-l2.yaml` | FILE | Mirror of L3 schema |
| `runtime/spawning/identity_generator.py` | FILE | SID generation for AI citizens |
| `runtime/onboarding/arrival_pipeline.py` | FILE | SID generation for humans |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| The Prism (spawning) | AI citizen SID generation |
| Arrival Pipeline (onboarding) | Human SID generation |
| FalkorDB (L4 graph) | SID storage and lookup |
| Bond system | References SIDs for bilateral bonds |

---

## CURRENT STATE

**Implemented and deployed:**
- 343 SIDs generated for all L4 actors (285 citizens, 41 orgs, 10 agents, 7 others)
- Schema updated across L1, L2, L3
- Arrival pipeline generates SIDs for new humans
- The Prism generates SIDs for new AI citizens

**Not yet implemented:**
- Handle → SID resolution in all MCP tools
- SID propagation to L3 universe graphs (currently L4 only)
- Multi-platform SID unification (same human on TG + Discord)

---

## MARKERS

<!-- @mind:todo Propagate SIDs from L4 to L3 actor nodes -->
<!-- @mind:todo Add handle → SID resolution to all MCP tools (send, call, bond, etc.) -->
<!-- @mind:todo Multi-platform unification: detect same human across platforms -->
