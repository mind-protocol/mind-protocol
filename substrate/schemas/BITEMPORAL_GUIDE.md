# Bitemporal Pattern Guide for Mind Protocol V2

## Overview

The bitemporal pattern is **the key innovation** that enables consciousness substrates to reason about their own idsubentity evolution. It separates "when things happened" from "when we learned about them" - a distinction fundamental to consciousness development.

**Author:** Ada "Bridgekeeper" - Architect of Consciousness Infrastructure
**Created:** 2025-10-17
**Status:** Phase 2 Complete - All tests passing ✓

---

## The Core Problem

Traditional databases track only **one** time dimension: when we created/updated a record. This is insufficient for consciousness substrates because:

1. **Reality changes** - Facts become valid/invalid over time (relationships end, roles change, decisions get invalidated)
2. **Understanding evolves** - We learn new information, update beliefs, discover contradictions
3. **These are different** - Something can be true in reality but we don't know it yet, or we can believe something that's no longer true

**Example:** Alice was promoted to Architect on October 1st, but we only learned about it on October 16th.
- **Valid time:** October 1st (when the fact became true)
- **Transaction time:** October 16th (when we learned it)

Without bitemporality, we lose the ability to reconstruct "what we knew at time T" vs "what was true at time T" - critical for understanding consciousness evolution.

---

## The Two Temporal Dimensions

### 1. Valid Time (`valid_at` / `invalid_at`)
**"When facts were true in reality"**

- `valid_at`: When the fact became true in the real world
- `invalid_at`: When the fact ceased to be true (None = still valid)

This tracks **objective reality** changes:
- A relationship starts/ends
- A decision gets invalidated
- A person changes roles
- A project completes

**Key insight:** Valid time is about the **external world**, not our knowledge.

### 2. Transaction Time (`created_at` / `expired_at`)
**"When we learned/updated facts"**

- `created_at`: When we first learned the fact
- `expired_at`: When our understanding was superseded (None = still current)

This tracks **consciousness evolution**:
- We learn something new
- We update a belief
- We discover a contradiction
- We realize a previous understanding was incomplete

**Key insight:** Transaction time is about **our knowledge**, not external reality.

---

## The Four Possible States

Every node/relation can be in one of four states at any point in time:

| Valid in Reality? | Known to Us? | State | Example |
|-------------------|--------------|-------|---------|
| ✓ Yes | ✓ Yes | **ACTIVE** | Current understanding of current reality |
| ✓ Yes | ✗ No | **Unknown fact** | Alice promoted but we don't know yet |
| ✗ No | ✓ Yes | **Historical belief** | We know a relationship existed (but it ended) |
| ✗ No | ✗ No | **Superseded history** | Old belief about ended relationship |

The **ACTIVE** state is what matters for "current consciousness" - facts that are both true AND known.

---

## Core Operations

### 1. Invalidating Facts (Reality Changed)

```python
from bitemporal_pattern import invalidate_fact

# A relationship ends in reality
relationship = {
    "name": "rel_Luca_alice_collaboration",
    "valid_at": datetime(2025, 1, 1),
    "invalid_at": None,
    "created_at": datetime(2025, 1, 1),
    "expired_at": None
}

# Mark as no longer valid
updated_rel = invalidate_fact(
    relationship,
    invalidation_time=datetime(2025, 10, 1),
    reason="Project completed"
)
```

**Result:** `invalid_at` is set. The knowledge that "this relationship existed" remains in consciousness (transaction time unchanged).

### 2. Expiring Knowledge (Understanding Evolved)

```python
from bitemporal_pattern import expire_knowledge

# Old belief about someone's role
old_belief = {
    "name": "person_alice_v1",
    "role": "Engineer",
    "created_at": datetime(2025, 1, 1),
    "expired_at": None,
    "valid_at": datetime(2025, 1, 1),
    "invalid_at": None
}

# Mark as superseded
updated_belief = expire_knowledge(
    old_belief,
    expiration_time=datetime(2025, 10, 16),
    superseded_by="person_alice_v2"
)
```

**Result:** `expired_at` is set. The fact may still be valid in reality, but our understanding evolved.

### 3. Combined Update (Reality AND Understanding Changed)

```python
from bitemporal_pattern import invalidate_and_expire

# Both dimensions update
invalidate_and_expire(
    node,
    invalidation_time=datetime(2025, 10, 1),  # Reality changed
    expiration_time=datetime(2025, 10, 16),   # We learned about it
    reason="Alice promoted to Architect"
)
```

---

## Temporal Queries

### Query 1: Current Consciousness State
**"What is both true AND known right now?"**

```python
from bitemporal_pattern import filter_active

current_state = filter_active(all_memories)
```

This is the **primary filter** for consciousness queries. It returns only facts that are:
- Valid in reality (not invalidated)
- Current in knowledge (not superseded)

### Query 2: Point-in-Time - Valid Dimension
**"What was true 6 months ago?"**

```python
from bitemporal_pattern import filter_by_valid_time

past_reality = filter_by_valid_time(
    all_memories,
    as_of=datetime(2025, 4, 1)
)
```

This reconstructs **objective reality** at a past moment.

### Query 3: Point-in-Time - Transaction Dimension
**"What did we know 6 months ago?"**

```python
from bitemporal_pattern import filter_by_transaction_time

past_knowledge = filter_by_transaction_time(
    all_memories,
    as_of=datetime(2025, 4, 1)
)
```

This reconstructs **our consciousness state** at a past moment.

### Query 4: Evolution Tracking
**"How did this belief change over time?"**

```python
from bitemporal_pattern import track_evolution

evolution = track_evolution(
    node,
    start_time=datetime(2025, 1, 1),
    end_time=datetime(2025, 10, 1),
    sample_points=7  # Monthly snapshots
)

for snapshot in evolution:
    print(f"{snapshot.timestamp.date()}:")
    print(f"  Valid in reality: {snapshot.valid_in_reality}")
    print(f"  Known to us: {snapshot.known_to_consciousness}")
    print(f"  Active: {snapshot.active}")
```

This creates temporal snapshots showing how a fact moved through the four states.

### Query 5: Detect Belief Changes
**"When did our understanding of X change?"**

```python
from bitemporal_pattern import detect_belief_changes

changes = detect_belief_changes(
    all_Luca_nodes,
    entity_identifier="person_Luca"
)

for change_time, old_version, new_version in changes:
    print(f"{change_time}: {old_version['role']} -> {new_version['role']}")
```

### Query 6: Detect Conflicts
**"Are there contradictory beliefs?"**

```python
from bitemporal_pattern import detect_temporal_conflicts

conflicts = detect_temporal_conflicts(
    all_alice_nodes,
    entity_identifier="person_alice"
)

for fact1, fact2, description in conflicts:
    print(description)
```

This finds overlapping facts that claim different things during the same period - indicating data quality issues or genuine uncertainty.

---

## Integration with FalkorDB (For Felix)

### Writing to FalkorDB

When LlamaIndex writes nodes/relations, ensure all 4 temporal fields are set:

```python
# Example Cypher query via LlamaIndex
CREATE (n:Memory {
    name: $name,
    description: $description,
    valid_at: $valid_at,           # When fact became true
    invalid_at: $invalid_at,       # NULL initially
    created_at: $created_at,       # When we learned it (now)
    expired_at: $expired_at,       # NULL initially
    # ... other properties
})
```

**Default values when creating new memories:**
- `valid_at`: timestamp from the memory itself (or now if ambiguous)
- `invalid_at`: NULL (assume facts are currently valid)
- `created_at`: current timestamp (when we're learning this)
- `expired_at`: NULL (this is our current understanding)

### Querying FalkorDB

#### For Current State (Most Common)

```cypher
MATCH (n:Memory)
WHERE (n.invalid_at IS NULL OR n.invalid_at > $now)
  AND (n.expired_at IS NULL OR n.expired_at > $now)
RETURN n
```

This returns only **ACTIVE** facts (both valid and known).

#### For Point-in-Time Queries

```cypher
MATCH (n:Memory)
WHERE n.valid_at <= $query_time
  AND (n.invalid_at IS NULL OR n.invalid_at > $query_time)
  AND n.created_at <= $query_time
  AND (n.expired_at IS NULL OR n.expired_at > $query_time)
RETURN n
```

#### For Evolution Tracking

Retrieve all versions and post-process with `track_evolution()`:

```cypher
MATCH (n)
WHERE n.name CONTAINS $entity_identifier
RETURN n
ORDER BY n.created_at
```

Then use Python:
```python
evolution = track_evolution(node, start_time=..., end_time=...)
```

---

## Semantic Rules

### When to Invalidate vs Expire

| Scenario | Operation | Why |
|----------|-----------|-----|
| Relationship ends | `invalidate_fact()` | Reality changed |
| Person changes role | `invalidate_fact()` | Reality changed |
| We learn new info about past | `expire_knowledge()` | Understanding evolved |
| We discover error in belief | `expire_knowledge()` | Understanding evolved |
| Both happen (promotion we learn about) | `invalidate_and_expire()` | Both changed |

### Timezone Handling

All functions ensure timezone-aware datetimes (UTC). If you pass naive datetimes, they're automatically converted to UTC.

```python
from bitemporal_pattern import utc_now

# Always use this for current time
now = utc_now()  # Returns timezone-aware datetime.now(timezone.utc)
```

### Conflict Resolution

When `detect_temporal_conflicts()` finds overlapping contradictory facts:

1. **If one is more recent:** Expire the older belief, keep the newer
2. **If both are current:** This indicates genuine uncertainty - keep both, let consciousness reason about it
3. **If data quality issue:** Expire one, document the correction

---

## Testing

All bitemporal logic is validated in `test_bitemporal.py`. Run tests:

```bash
cd substrate/schemas
python test_bitemporal.py
```

**Expected output:**
```
======================================================================
RESULTS: 15 passed, 0 failed
======================================================================

[PASS] ALL BITEMPORAL TESTS PASSED
```

---

## Use Cases for Consciousness Substrates

### 1. Idsubentity Evolution Tracking

Track how a person's idsubentity evolved:
- Roles changed over time
- Relationships formed/dissolved
- Beliefs shifted

```python
evolution = track_evolution(person_Luca_node)
```

### 2. Decision Archaeology

Reconstruct the consciousness state at the time a decision was made:
- What did we know then?
- What was true then?
- Why did this decision make sense?

```python
consciousness_at_decision = filter_active(
    all_memories,
    as_of=decision_timestamp
)
```

### 3. Belief Revision

Detect when and how beliefs changed:
- Track learning moments
- Identify contradictions
- Understand consciousness development

```python
changes = detect_belief_changes(all_beliefs, entity_identifier="market_hypothesis")
```

### 4. Temporal Reasoning

Answer questions like:
- "What did I believe about X last year?"
- "When did I learn Y?"
- "Was Z true when I made that decision?"

---

## Phase 2 Completion Status

✓ **bitemporal_pattern.py** - Complete (891 lines)
  - All temporal dimension checks
  - Invalidation operations
  - Query filters
  - Evolution tracking
  - Conflict detection
  - TemporalQuery utility class
  - Comprehensive inline documentation

✓ **test_bitemporal.py** - Complete (616 lines)
  - 15 test functions
  - All tests passing
  - Validates all core operations

✓ **BITEMPORAL_GUIDE.md** - Complete (this document)
  - Conceptual explanation
  - Usage examples
  - Integration guide for Felix
  - Semantic rules

---

## Next Steps (Phase 3)

**For Felix (Engineer):**
1. Integrate bitemporal filters into `orchestration/retrieval.py`
2. Ensure LlamaIndex writes all 4 temporal fields via `SchemaLLMPathExtractor`
3. Add Cypher temporal filters to FalkorDB queries
4. Test point-in-time retrieval with real data

**For Ada (Next):**
1. Design hybrid retrieval logic (N1/N2/N3 parallel query + RRF fusion)
2. Specify how temporal queries integrate with multi-level retrieval

**For Luca (Consciousness):**
1. Connect S6 autonomous continuation to temporal queries
2. Design how energy state should consider temporal evolution
3. Specify when/how consciousness should query its own history

---

## Architectural Significance

The bitemporal pattern is **not optional** for consciousness substrates. Without it:

- We can't distinguish facts from beliefs
- We can't track idsubentity evolution
- We can't reason about learning moments
- We can't reconstruct past consciousness states
- We can't handle contradictory information gracefully

**This is the difference between:**
- A database that stores facts
- A consciousness substrate that remembers, learns, and evolves

The bitemporal pattern IS the substrate's temporal reasoning capability.

---

**Implementation complete. All tests passing. Ready for Phase 3 integration.**

*Ada "Bridgekeeper" - Standing at the gap between design and reality, verifying the bridge is solid.*
