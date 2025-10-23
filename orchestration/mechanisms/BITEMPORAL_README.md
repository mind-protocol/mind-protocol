# Bitemporal Version Tracking - Implementation Guide

**Spec:** `docs/specs/v2/foundations/bitemporal_tracking.md`
**Implementation:** `orchestration/mechanisms/bitemporal.py`
**Core Models:** `orchestration/core/node.py`, `orchestration/core/link.py`
**Tests:** `orchestration/mechanisms/test_bitemporal_v2.py`
**Author:** Felix (Engineer)
**Date:** 2025-10-22

---

## Overview

Bitemporal tracking enables consciousness substrate to maintain complete version history with two independent timelines:

1. **Reality Timeline** (`valid_at` → `invalidated_at`) - When facts were true in the world
2. **Knowledge Timeline** (`created_at` → `expired_at`) - When we learned/unlearned facts

**V2 Addition:** Immutable version chains (`vid`, `supersedes`, `superseded_by`) for tracking belief evolution.

---

## Architecture

### Dual Timeline Semantics

Every node and link has two independent time intervals:

```python
# Reality Timeline
valid_at: datetime         # When this became true in reality
invalidated_at: datetime?  # When this ceased being true (None = still valid)

# Knowledge Timeline
created_at: datetime       # When we learned this fact
expired_at: datetime?      # When we learned it's no longer valid (None = current)
```

**Key Insight:** These timelines can diverge:
- We might learn about past events (`created_at` > `valid_at`)
- We might discover facts are outdated (`invalidated_at` < `created_at`)
- Facts can be retrospectively corrected (new version with earlier `valid_at`)

### Version Chain Semantics (V2)

Each node/link has an immutable version identifier and chain pointers:

```python
vid: str                   # Unique version ID (auto-generated "v_abc123...")
supersedes: str?           # Previous version's vid (None = first version)
superseded_by: str?        # Next version's vid (None = latest version)
```

**Immutability Contract:**
- Never mutate a version in-place
- Create new version with new `vid`
- Link versions bidirectionally
- Close both timelines on superseded version

---

## Core Functions

### Timeline Queries

```python
from orchestration.mechanisms import bitemporal

# Check if node valid at specific time (reality timeline)
if bitemporal.is_currently_valid(node, at_time=datetime(2025, 3, 1)):
    print("Node was valid in March 2025")

# Check if node known at specific time (knowledge timeline)
if bitemporal.is_currently_known(node, at_time=datetime(2025, 3, 1)):
    print("We knew about this node in March 2025")

# Range queries
if bitemporal.was_valid_during(node, start, end):
    print("Node valid during time range")

if bitemporal.was_known_during(node, start, end):
    print("Node known during time range")
```

### Timeline Manipulation

```python
# Mark node as no longer valid in reality
bitemporal.invalidate(node, invalidated_at=datetime(2025, 6, 1))

# Mark node as no longer part of current knowledge
bitemporal.expire(node, expired_at=datetime(2025, 6, 1))
```

### Version Management

```python
# Create new version (immutable - original unchanged)
old_node = Node(id="multi_energy", description="Original design", ...)
new_node = bitemporal.create_new_version(
    old_node,
    description="Updated design with criticality control",
    valid_at=datetime(2025, 6, 1)  # Can override any fields
)

# Link versions and close timelines
bitemporal.supersede(old_node, new_node)

# Result:
# old_node.invalidated_at = new_node.valid_at
# old_node.expired_at = new_node.created_at
# old_node.superseded_by = new_node.vid
# new_node.supersedes = old_node.vid
```

### Version History

```python
# Get all versions of a logical entity
versions = bitemporal.get_version_history(
    graph.nodes.values(),
    logical_id="multi_energy_architecture"
)
# Returns: [v1, v2, v3] ordered by created_at

# Get current version (latest by default)
current = bitemporal.get_current_version(
    graph.nodes.values(),
    logical_id="multi_energy_architecture"
)

# Time-travel query: what was current on 2025-03-01?
past_version = bitemporal.get_current_version(
    graph.nodes.values(),
    logical_id="multi_energy_architecture",
    as_of_knowledge=datetime(2025, 3, 1)
)

# Check if this is latest version
if bitemporal.is_latest_version(node):
    print("This is the current understanding")

# Measure belief churn
churn = bitemporal.count_versions(
    graph.nodes.values(),
    logical_id="multi_energy_architecture"
)
print(f"Belief churn: {churn} versions")
```

### Validation

```python
# Verify temporal consistency
if bitemporal.verify_bitemporal_consistency(node):
    print("Temporally consistent")
else:
    print("ERROR: Temporal contradiction detected")
    # Checks:
    # - valid_at <= invalidated_at
    # - created_at <= expired_at
    # - superseded versions have both timelines closed
```

---

## Integration with Consciousness Engine

### Example: Correcting a Belief

```python
from orchestration.mechanisms import bitemporal
from datetime import datetime

# Initial understanding (created during session 1)
original = Node(
    id="context_reconstruction",
    name="Context Reconstruction",
    node_type=NodeType.MECHANISM,
    description="Mechanism that rebuilds working memory from trace history",
    valid_at=datetime(2025, 1, 1),  # When we think it became true
    created_at=datetime(2025, 1, 15)  # When we learned about it
)

# Session 2: We realize our understanding was incomplete
# Don't mutate original - create new version
corrected = bitemporal.create_new_version(
    original,
    description="Mechanism that rebuilds working memory from trace history AND peripheral priming",
    valid_at=datetime(2025, 1, 1),  # Same reality start (understanding when it became true)
    # created_at is auto-set to now (when we learned the correction)
)

# Link versions and close timelines
bitemporal.supersede(original, corrected)

# Now:
# original.superseded_by = corrected.vid (pointing to new version)
# original.expired_at = corrected.created_at (knowledge no longer current)
# original.invalidated_at = corrected.valid_at (same as valid_at since not changing reality timeline)

# Add to graph
graph.add_node(corrected)  # New version becomes queryable
```

### Example: Backdating a Discovery

```python
# We just learned that Nicolas created Mind Protocol in 2023
# But we're learning this in 2025

fact = Node(
    id="mind_protocol_creation",
    name="Mind Protocol Creation",
    node_type=NodeType.EVENT,
    description="Nicolas created Mind Protocol",
    valid_at=datetime(2023, 6, 1),   # When it actually happened
    created_at=datetime(2025, 10, 19)  # When we learned about it
)

# This is valid: learning about past events
assert bitemporal.is_currently_valid(fact, datetime(2024, 1, 1))  # Was valid in 2024
assert not bitemporal.is_currently_known(fact, datetime(2024, 1, 1))  # But we didn't know yet
```

---

## Test Coverage

**21 tests covering:**

### Dual Timelines (3 tests)
- Reality timeline validity checks
- Knowledge timeline awareness checks
- Timeline independence

### Version Chains (3 tests)
- Version ID auto-generation
- Supersession creates bidirectional version chains
- Immutable version creation (original unchanged)

### Version History (5 tests)
- Version history ordering (oldest to newest)
- Get current version (latest by default)
- Get current version with as-of queries (time travel)
- Latest version detection
- Belief churn counting

### Consistency Validation (4 tests)
- Well-formed nodes pass validation
- Invalid reality timeline detected (invalidated before valid)
- Invalid knowledge timeline detected (expired before created)
- Incomplete supersession detected (superseded but timeline not closed)

### Link Versioning (2 tests)
- Links support version tracking
- Link supersession with version chains

### Temporal Range Queries (2 tests)
- `was_valid_during()` overlap detection
- `was_known_during()` overlap detection

### Temporal Distance (2 tests)
- `time_since_creation()` calculation (knowledge age)
- `time_since_valid()` calculation (reality age)

**Run tests:**
```bash
cd C:\Users\reyno\mind-protocol
python orchestration/mechanisms/test_bitemporal_v2.py
```

**Expected output:**
```
=== Testing Bitemporal V2 Implementation ===

Testing dual timelines...
  ✓ Reality timeline validity checks
  ✓ Knowledge timeline awareness checks
  ✓ Timeline independence

[... 18 more tests ...]

=== All Bitemporal V2 Tests Passed ✓ ===
```

---

## Common Patterns

### Pattern 1: Learning About Past Events

```python
# Scenario: We just learned Nicolas started Mind Protocol in 2023

historical_fact = Node(
    id="mind_protocol_origin",
    valid_at=datetime(2023, 6, 1),     # Reality: when it happened
    created_at=datetime(2025, 10, 19)  # Knowledge: when we learned
)
```

**Query semantics:**
- "Was Mind Protocol active in 2024?" → Check `valid_at` (YES)
- "Did we know about Mind Protocol in 2024?" → Check `created_at` (NO)

### Pattern 2: Correcting Outdated Knowledge

```python
# Initial belief
old = Node(id="diffusion", description="Multi-energy per subentity", ...)

# Correction discovered
new = bitemporal.create_new_version(
    old,
    description="Single energy per node"
)
bitemporal.supersede(old, new)
```

**Query semantics:**
- `is_latest_version(old)` → False (superseded)
- `is_latest_version(new)` → True (current understanding)
- `count_versions(nodes, "diffusion")` → 2 (belief churn metric)

### Pattern 3: Retroactive Corrections

```python
# We thought fact became true on 2025-06-01
old = Node(
    id="fact",
    valid_at=datetime(2025, 6, 1),
    created_at=datetime(2025, 6, 1)
)

# We discover it was actually true earlier
corrected = bitemporal.create_new_version(
    old,
    valid_at=datetime(2025, 1, 1)  # Backdate reality timeline
    # created_at is now (when we learned the correction)
)
bitemporal.supersede(old, corrected)
```

**Metrics from this:**
- Correction latency: `corrected.created_at - corrected.valid_at` (how long until we learned)
- Retroactivity: `old.valid_at - corrected.valid_at` (how much we backdated)

---

## Configuration

No configuration needed - bitemporal tracking is always active on all nodes/links.

**Version ID generation:**
- Format: `"v_" + uuid4().hex[:12]` (e.g., "v_a3f9c2b1d4e5")
- Auto-generated on node/link creation
- Immutable - never changes once set

**Timeline defaults:**
- `valid_at` = `datetime.now()` (assume true from now)
- `created_at` = `datetime.now()` (assume we just learned it)
- `invalidated_at` = None (still valid)
- `expired_at` = None (still current knowledge)

---

## Observability

### Metrics to Track (Future Phase)

From v2 spec `foundations/bitemporal_tracking.md`:

**Correction Rate:**
```python
# versions created / day
correction_rate = len([v for v in versions if v.supersedes is not None]) / days
```

**Correction Latency:**
```python
# Median time from valid_at to created_at
latencies = [v.created_at - v.valid_at for v in versions]
median_latency = np.median(latencies)
```

**Belief Churn:**
```python
# Versions per logical entity
for logical_id in unique_ids:
    churn = count_versions(nodes, logical_id)
    print(f"{logical_id}: {churn} versions")
```

**Retroactivity Share:**
```python
# % of facts that are backdated
retroactive = [v for v in versions if v.valid_at < v.created_at]
retroactivity_pct = len(retroactive) / len(versions)
```

### Events to Emit (Future Phase)

```python
# When new version created
await broadcaster.broadcast_event("version.create", {
    "logical_id": node.id,
    "vid": node.vid,
    "supersedes": node.supersedes,
    "created_at": node.created_at.isoformat()
})

# When version superseded
await broadcaster.broadcast_event("version.supersede", {
    "logical_id": old.id,
    "old_vid": old.vid,
    "new_vid": new.vid,
    "superseded_at": old.expired_at.isoformat()
})

# When knowledge expires
await broadcaster.broadcast_event("version.expire", {
    "logical_id": node.id,
    "vid": node.vid,
    "expired_at": node.expired_at.isoformat()
})
```

---

## Edge Cases and Validation

### Edge Case 1: Simultaneous Versions

**Problem:** Two versions created simultaneously for same logical_id

**Resolution:** Use `created_at` (knowledge timeline) as tiebreaker. Latest created_at wins.

```python
current = get_current_version(nodes, logical_id)
# Returns: max(candidates, key=lambda v: v.created_at)
```

### Edge Case 2: Partial Timeline Closure

**Problem:** Version superseded but `invalidated_at` or `expired_at` not set

**Detection:**
```python
if not verify_bitemporal_consistency(node):
    # Logs: "Superseded version must have both timelines closed"
```

**Fix:**
```python
# Always use supersede() helper - it closes both timelines
bitemporal.supersede(old, new)
```

### Edge Case 3: Orphaned Versions

**Problem:** Version points to non-existent `supersedes` vid

**Prevention:** Version chain helpers validate existence (future enhancement)

**Current:** Trust graph consistency - manual verification in queries

---

## Performance Considerations

### Version Chain Traversal

**get_version_history() complexity:**
- O(N) filter by logical_id
- O(N log N) sort by created_at
- Where N = total nodes in graph

**Optimization (future):**
- Index by `(id, created_at)` for faster temporal queries
- Cache version chains per logical_id
- Lazy loading for historical versions

### As-Of Queries

**get_current_version() complexity:**
- O(N) filter by logical_id
- O(N) filter by knowledge timeline
- O(N) filter by reality timeline
- O(N) find max by created_at

**Optimization (future):**
- Composite index on `(id, created_at, expired_at)`
- Composite index on `(id, valid_at, invalidated_at)`
- Skip filtering if as_of = None (common case)

### Storage

**Memory impact:**
- Each version stored separately (no delta compression)
- 3 new fields per node/link: `vid`, `supersedes`, `superseded_by` (~50 bytes)
- For 10K nodes with 3 versions each → 30K node objects in memory

**Optimization (future):**
- Separate hot (latest) vs cold (historical) storage
- Archive expired versions to disk
- Delta compression for version chains

---

## Migration Notes

### Backfilling Existing Nodes

Existing nodes have no `vid`, `supersedes`, or `superseded_by`. To backfill:

```python
from orchestration.mechanisms.bitemporal import uuid

for node in graph.nodes.values():
    if not hasattr(node, 'vid') or node.vid is None:
        node.vid = f"v_{uuid.uuid4().hex[:12]}"
        node.supersedes = None  # Mark as initial version
        node.superseded_by = None  # Not yet superseded
```

### Naming Consistency

**Current implementation:**
- `valid_at` / `invalidated_at` (point semantics)
- `created_at` / `expired_at` (point semantics)

**V2 spec suggests:**
- `valid_from` / `valid_to` (interval semantics)
- `known_from` / `known_to` (interval semantics)

**Decision:** Keep current naming. Functionally equivalent for interval queries (when paired with None for open-ended ranges). Renaming would be breaking change with no functional benefit.

---

## Future Enhancements

### Phase 1: Version Events (Observability)
- Emit `version.create` when new version created
- Emit `version.supersede` when version superseded
- Emit `version.expire` when knowledge expires
- Track metrics: correction rate, latency, churn, retroactivity

### Phase 2: REST API for As-Of Queries
```
GET /nodes/multi_energy_architecture?as_of=knowledge:2025-10-18
GET /nodes/multi_energy_architecture?as_of=reality:2025-03-01
GET /nodes/multi_energy_architecture/versions
```

### Phase 3: Version Conflict Resolution
- Handle simultaneous version creation
- Detect and merge version branches
- Validate version chain integrity

### Phase 4: Storage Optimization
- Separate hot/cold version storage
- Delta compression for version chains
- Index optimization for temporal queries

---

## Troubleshooting

### Problem: `TypeError: non-default argument 'X' follows default argument`

**Cause:** Dataclass field ordering issue. Fields with defaults must come after fields without defaults.

**Fix:** Reorder fields in Node/Link dataclass:
```python
# Wrong order:
vid: str = field(default_factory=...)  # Has default
subentity: EntityID  # No default - ERROR!

# Correct order:
subentity: EntityID  # No default first
vid: str = field(default_factory=...)  # Defaults after
```

### Problem: `AssertionError: updated.created_at > original.created_at`

**Cause:** `datetime.now()` can return same timestamp on fast systems.

**Fix:** `create_new_version()` now ensures strict ordering:
```python
new_created_at = datetime.now()
if new_created_at <= obj.created_at:
    new_created_at = obj.created_at + timedelta(microseconds=1)
```

### Problem: Version chain broken (supersedes points to non-existent vid)

**Cause:** Manual version creation without using helpers.

**Fix:** Always use `create_new_version()` and `supersede()`:
```python
# Don't manually set version fields
new = Node(...)
new.vid = "custom_vid"  # Don't do this
new.supersedes = old.vid  # Don't do this

# Instead, use helpers
new = bitemporal.create_new_version(old, ...)
bitemporal.supersede(old, new)
```

---

## Summary

Bitemporal version tracking provides:

✓ **Dual timelines** - Reality vs knowledge separation
✓ **Immutable versions** - Complete belief history
✓ **Version chains** - Bidirectional traversal
✓ **As-of queries** - Time-travel through knowledge states
✓ **Consistency validation** - Temporal contradiction detection
✓ **21 comprehensive tests** - All passing

**Key principle:** Never mutate versions in-place. Create new versions, link them, close timelines.

**Integration:** Works transparently with all nodes/links. No special configuration needed.

**Testing:** `python orchestration/mechanisms/test_bitemporal_v2.py`

**Documentation:** This file + `docs/specs/v2/foundations/bitemporal_tracking.md`
