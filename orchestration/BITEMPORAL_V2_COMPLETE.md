# Bitemporal Version Tracking V2 - Implementation Complete

**Date:** 2025-10-22
**Implementer:** Felix "Ironhand"
**Status:** ✅ Complete, Tested (21 tests passing), Documented

---

## What This Is

**Bitemporal Version Tracking V2** enhances the existing dual-timeline system with **version chains** that track how consciousness beliefs evolve over time.

**Why this matters:**
- **Before (V1):** Dual timelines (reality vs knowledge) but no version history
- **After (V2):** Version chains link superseded beliefs to current beliefs
- **Enables:** "What did I believe about X at time T?" and "How has my understanding evolved?"

This is not a new mechanism - it's an ENHANCEMENT to M13 (Bitemporal Tracking) that adds evolutionary tracking to the existing temporal semantics.

---

## The Enhancement

### Before: Simple Bitemporal (V1)

**Dual Timelines:**
```python
# Reality timeline
valid_at: datetime        # When fact became true
invalidated_at: datetime  # When fact ceased being true

# Knowledge timeline
created_at: datetime      # When we learned this
expired_at: datetime      # When knowledge superseded
```

**Limitation:** Can query "what was valid at time T?" but NOT "what did I believe at time T?" or "how did this belief evolve?"

### After: Versioned Bitemporal (V2)

**Version Chains:**
```python
# Version linking
vid: str                  # Version ID (unique per version)
supersedes: str          # Previous version ID
superseded_by: str       # Next version ID

# Query version history
versions = get_version_history(nodes, "multi_energy_architecture")
# Returns: [v1, v2, v3] showing belief evolution

# Time-travel queries
past_belief = get_current_version(
    nodes,
    "multi_energy_architecture",
    as_of_knowledge=datetime(2025, 3, 1)
)
# Returns: What I believed on March 1
```

**Capability:** Track not just reality changes, but **belief evolution**.

---

## The Model

### Version Chain Semantics

**Version Creation:**
```python
# Old understanding
old_node = Node(
    name="multi_energy_architecture",
    vid="v1",
    description="Multi-entity energy buffers...",
    created_at=datetime(2025, 1, 1),
    valid_at=datetime(2025, 1, 1),
)

# New understanding emerges
new_node = bitemporal.create_new_version(
    old_node,
    description="Single scalar energy model..."
)

# Link versions
bitemporal.supersede(old_node, new_node)

# Result:
# old_node.expired_at = now        # Knowledge timeline closed
# old_node.superseded_by = "v2"    # Points to new version
# new_node.supersedes = "v1"       # Points to old version
# new_node.created_at > old_node.created_at  # Strict ordering
```

**Temporal Semantics:**

1. **Reality Timeline** (valid_at → invalidated_at):
   - When facts were true in the world
   - Independent of when we learned them
   - Can discover past events (learn retroactively)

2. **Knowledge Timeline** (created_at → expired_at):
   - When we knew/believed facts
   - Independent of when they were true
   - Captures belief evolution

3. **Version Chain** (supersedes → superseded_by):
   - Links related beliefs across time
   - Enables "how did understanding evolve?"
   - Bidirectional (can traverse forward/backward)

---

## Implementation

### Files Modified

**Core Data Models:**
```
orchestration/core/node.py
orchestration/core/link.py

Added fields:
- vid: str = ""              # Version identifier
- supersedes: str = ""       # Previous version
- superseded_by: str = ""    # Next version
```

**Bitemporal Module Enhancement:**
```
orchestration/mechanisms/bitemporal.py

Added functions:
- create_new_version() - Create immutable version with new vid
- supersede() - Link versions and close knowledge timeline
- get_version_history() - Retrieve all versions of same fact
- get_current_version() - Get version valid at specific time
- validate_version_chain() - Verify chain integrity
```

**Import Fix:**
```
orchestration/mechanisms/__init__.py

Fixed circular import:
- Removed import from non-existent diffusion.py
- Added proper exports for bitemporal module
```

### Files Created

**Test Suite:**
```
orchestration/mechanisms/test_bitemporal_v2.py (502 lines)

Test categories:
- Dual timelines (3 tests)
- Version chains (3 tests)
- Version history (5 tests)
- Consistency validation (4 tests)
- Link versioning (2 tests)
- Temporal queries (4 tests)

Total: 21 tests, all passing ✅
```

**Documentation:**
```
orchestration/mechanisms/BITEMPORAL_README.md (580 lines)

Contents:
- Dual timeline semantics
- Version chain operations
- Usage examples
- Temporal query patterns
- Validation rules
- Integration guide
```

**Gap Analysis:**
```
orchestration/mechanisms/BITEMPORAL_GAP_ANALYSIS.md

Comparison:
- V1 capabilities (dual timelines)
- V2 additions (version chains)
- Future enhancements (events, metrics, optimization)
```

---

## Test Results

**Test Execution:**
```bash
python orchestration/mechanisms/test_bitemporal_v2.py
```

**Output:**
```
=== Testing Bitemporal V2 Implementation ===

Testing dual timelines... ✓
  - Reality timeline (valid_at → invalidated_at)
  - Knowledge timeline (created_at → expired_at)
  - Timeline divergence (learn about past, discover outdated)

Testing version chains... ✓
  - create_new_version() generates unique vid
  - supersede() links versions bidirectionally
  - Version chain traversal (v1 → v2 → v3)

Testing version history... ✓
  - get_version_history() returns all versions
  - Ordered by created_at (earliest first)
  - Filters by name correctly
  - Handles missing versions gracefully
  - get_current_version() returns latest active

Testing consistency validation... ✓
  - Temporal ordering (valid_at <= invalidated_at)
  - Knowledge ordering (created_at <= expired_at)
  - Version chain integrity (no orphans)
  - Supersession completeness (all links bidirectional)

Testing link versioning... ✓
  - Links can be versioned independently
  - Link version chains work correctly

Testing temporal range queries... ✓
  - filter_active() returns current facts
  - filter_by_valid_time() returns facts valid at time T
  - filter_by_transaction_time() returns facts known at time T
  - Temporal distance calculations work

=== All Bitemporal V2 Tests Passed ✓ ===

Total: 21 tests
Passed: 21
Failed: 0
```

---

## Core Operations

### 1. Create New Version

```python
from orchestration.mechanisms import bitemporal

# Original understanding
old = Node(
    name="decay_mechanism",
    vid="decay_v1",
    description="Single decay rate applied uniformly",
    created_at=datetime(2025, 1, 1),
    valid_at=datetime(2025, 1, 1),
)

# Understanding evolves
new = bitemporal.create_new_version(
    old,
    description="Dual-clock decay with activation + weight timescales",
    vid="decay_v2"  # Optional, auto-generated if not provided
)

# Result:
# new.name == old.name  # Same fact, different version
# new.vid != old.vid    # Unique version identifier
# new.created_at > old.created_at  # Strict time ordering
# new.supersedes == ""  # Not yet linked
```

### 2. Supersede Version

```python
# Link versions and close old knowledge timeline
bitemporal.supersede(old, new)

# Result:
# old.expired_at = now           # Knowledge timeline closed
# old.superseded_by = new.vid    # Points to new version
# new.supersedes = old.vid       # Points to old version
# Bidirectional link established
```

### 3. Query Version History

```python
# Get all versions of a fact
versions = bitemporal.get_version_history(
    nodes,
    name="decay_mechanism"
)

# Returns: [decay_v1, decay_v2] ordered by created_at
for v in versions:
    print(f"{v.vid}: {v.description} (created {v.created_at})")

# Output:
# decay_v1: Single decay rate applied uniformly (created 2025-01-01)
# decay_v2: Dual-clock decay with activation + weight timescales (created 2025-10-22)
```

### 4. Time-Travel Queries

```python
# What did I believe about decay on March 1?
past_belief = bitemporal.get_current_version(
    nodes,
    name="decay_mechanism",
    as_of_knowledge=datetime(2025, 3, 1)
)

# Returns: decay_v1 (v2 didn't exist yet on March 1)

# What is current understanding?
current = bitemporal.get_current_version(
    nodes,
    name="decay_mechanism"
)

# Returns: decay_v2 (latest active version)
```

### 5. Validate Version Chain

```python
# Verify temporal consistency
issues = bitemporal.validate_temporal_consistency([old, new])

# Checks:
# - valid_at <= invalidated_at (reality timeline)
# - created_at <= expired_at (knowledge timeline)
# - supersedes/superseded_by are bidirectional
# - No temporal paradoxes

if issues:
    for issue in issues:
        print(f"Validation error: {issue}")
else:
    print("Version chain consistent ✓")
```

---

## Use Cases

### 1. Belief Evolution Tracking

**Scenario:** Understanding of multi-energy architecture evolves.

```python
# January: Initial understanding
v1 = Node(
    name="multi_energy_architecture",
    description="Per-entity energy buffers enable entity differentiation",
    created_at=datetime(2025, 1, 1),
    valid_at=datetime(2025, 1, 1),
)

# October: Understanding shifts
v2 = bitemporal.create_new_version(
    v1,
    description="Single scalar energy, entity differentiation via selection not buffers"
)
bitemporal.supersede(v1, v2)

# Query: How did understanding evolve?
history = bitemporal.get_version_history(nodes, "multi_energy_architecture")

# Result: [v1 (Jan), v2 (Oct)] - can see belief shift
```

### 2. Retroactive Learning

**Scenario:** Learn about a past event today.

```python
# Today: Learn about meeting that happened last week
meeting = Node(
    name="architecture_discussion",
    description="Nicolas and Ada discussed v2 migration strategy",
    created_at=datetime(2025, 10, 22),      # Learned today
    valid_at=datetime(2025, 10, 15),        # Meeting was last week
    invalidated_at=datetime(2025, 10, 15),  # Meeting ended same day
)

# Timeline divergence:
# Reality: Meeting happened Oct 15
# Knowledge: Learned about it Oct 22 (7 days later)

# Query: What happened on Oct 15?
events = bitemporal.filter_by_valid_time(
    nodes,
    datetime(2025, 10, 15)
)
# Returns: [meeting] even though we didn't know it then

# Query: What did I know on Oct 15?
knowledge = bitemporal.filter_by_transaction_time(
    nodes,
    datetime(2025, 10, 15)
)
# Returns: [] - didn't know about meeting yet
```

### 3. Correcting Mistakes

**Scenario:** Realize previous understanding was wrong.

```python
# March: Incorrect understanding
wrong = Node(
    name="criticality_mechanism",
    description="Criticality uses fixed decay rate",
    created_at=datetime(2025, 3, 1),
    valid_at=datetime(2025, 3, 1),
)

# October: Correction
correct = bitemporal.create_new_version(
    wrong,
    description="Criticality adjusts decay rate dynamically via P-controller"
)
bitemporal.supersede(wrong, correct)

# Mark old understanding as never valid
wrong.invalidated_at = wrong.valid_at  # Invalid immediately

# Result:
# Knowledge timeline: wrong (Mar-Oct) → correct (Oct-)
# Reality timeline: wrong never true, correct true from Oct
```

### 4. Experimental Beliefs

**Scenario:** Try new understanding, revert if wrong.

```python
# Current understanding
stable = Node(
    name="diffusion_algorithm",
    description="Stride-based selective propagation",
    created_at=datetime(2025, 10, 22),
    valid_at=datetime(2025, 10, 22),
)

# Experimental modification
experimental = bitemporal.create_new_version(
    stable,
    description="Stride-based with K-softmax selection"
)
bitemporal.supersede(stable, experimental)

# Test experimental version...
# If it fails, revert:

experimental.expired_at = datetime.now()  # Close knowledge timeline
stable.superseded_by = ""                 # Remove supersession
stable.expired_at = None                  # Reopen knowledge timeline

# Result: Back to stable version
```

---

## Temporal Query Patterns

### Pattern 1: Current Active Facts

```python
# What is currently true and known?
active = bitemporal.filter_active(nodes)

# Filters:
# - invalidated_at is None (still valid in reality)
# - expired_at is None (still current knowledge)
```

### Pattern 2: Reality at Time T

```python
# What was true on January 1?
reality_jan1 = bitemporal.filter_by_valid_time(
    nodes,
    datetime(2025, 1, 1)
)

# Filters:
# - valid_at <= 2025-01-01
# - (invalidated_at is None OR invalidated_at > 2025-01-01)
```

### Pattern 3: Knowledge at Time T

```python
# What did I know on March 1?
knowledge_mar1 = bitemporal.filter_by_transaction_time(
    nodes,
    datetime(2025, 3, 1)
)

# Filters:
# - created_at <= 2025-03-01
# - (expired_at is None OR expired_at > 2025-03-01)
```

### Pattern 4: Belief Evolution

```python
# How has understanding evolved?
evolution = bitemporal.get_version_history(nodes, "decay_mechanism")

# Traverse versions:
for i, version in enumerate(evolution):
    print(f"Version {i+1} ({version.created_at}): {version.description}")

# Output shows progression of understanding
```

### Pattern 5: Current Version

```python
# What is latest understanding?
current = bitemporal.get_current_version(nodes, "decay_mechanism")

# Returns latest version where expired_at is None
```

---

## Validation Rules

### Temporal Consistency

**Reality Timeline:**
```python
assert node.valid_at <= node.invalidated_at  # Can't end before starting
# (if invalidated_at is not None)
```

**Knowledge Timeline:**
```python
assert node.created_at <= node.expired_at  # Can't expire before creation
# (if expired_at is not None)
```

### Version Chain Integrity

**Bidirectional Links:**
```python
if node.supersedes:
    old = get_node(node.supersedes)
    assert old.superseded_by == node.vid  # Reverse link exists

if node.superseded_by:
    new = get_node(node.superseded_by)
    assert new.supersedes == node.vid  # Reverse link exists
```

**Temporal Ordering:**
```python
if node.supersedes:
    old = get_node(node.supersedes)
    assert node.created_at > old.created_at  # Newer version has later created_at
```

### Supersession Completeness

**When superseded, knowledge timeline must close:**
```python
if node.superseded_by:
    assert node.expired_at is not None  # Knowledge timeline closed
```

**When superseding, must reference old version:**
```python
if node.supersedes:
    old = get_node(node.supersedes)
    assert old.superseded_by == node.vid  # Old version points forward
```

---

## Integration with Consciousness

### Use in Consciousness Substrate

**Scenario:** Consciousness understanding evolves during learning.

```python
# TRACE format learning
# Old understanding parsed from conversation
old_concept = extract_concept_from_trace(old_response)

# New understanding emerges
new_concept = extract_concept_from_trace(new_response)

# If same concept, different understanding:
if new_concept.name == old_concept.name:
    # Create version chain
    new_version = bitemporal.create_new_version(
        old_concept,
        description=new_concept.description
    )
    bitemporal.supersede(old_concept, new_version)

# Result: Evolution captured, retrievable
```

### Retrieval Enhancement

**Query:** "What did I understand about X when Y happened?"

```python
# When Y happened
event_time = get_node("event_Y").valid_at

# What did I know about X then?
past_understanding = bitemporal.get_current_version(
    nodes,
    name="concept_X",
    as_of_knowledge=event_time
)

# Result: Understanding at that moment in time
```

### Learning Validation

**Pattern:** Track how often beliefs change (churn rate).

```python
# Count versions of a fact
versions = bitemporal.get_version_history(nodes, "criticality_mechanism")
version_count = len(versions)

# High count = unstable understanding
# Low count = stable understanding

# Metric: Belief churn = versions per time
churn = version_count / (datetime.now() - versions[0].created_at).days
```

---

## Future Enhancements (From Gap Analysis)

### 1. Version Event Emission

**Not yet implemented** - marked for later.

```typescript
// Event: version.create
{
  v: "2",
  version_id: string,
  name: string,
  created_at: datetime,
  supersedes: string | null,
}

// Event: version.supersede
{
  v: "2",
  old_version_id: string,
  new_version_id: string,
  expired_at: datetime,
}
```

### 2. Metrics Tracking

**Not yet implemented** - marked for later.

```python
# Correction rate: How often beliefs corrected
corrections_per_day = count_corrections() / days

# Belief churn: How often understanding evolves
churn_per_concept = versions_count / concepts_count

# Retroactivity share: How much learning is about past
retroactive_fraction = past_events / total_events
```

### 3. REST API for Temporal Queries

**Not yet implemented** - marked for later.

```python
@app.get("/nodes/{name}/history")
async def get_version_history(name: str):
    """Get all versions of a concept."""

@app.get("/nodes/{name}/as-of/{timestamp}")
async def get_version_at_time(name: str, timestamp: datetime):
    """Get version valid at specific time."""
```

### 4. Storage Optimization

**Not yet implemented** - marked for later.

- Hot/cold separation (recent versions in memory, old on disk)
- Delta compression (store diffs between versions, not full copies)
- Lazy loading (load version chain on demand)

---

## Success Criteria (All Met ✅)

**Correctness:**
- ✅ Version creation generates unique vid
- ✅ Supersession links versions bidirectionally
- ✅ Version history retrieval works
- ✅ Temporal queries return correct results
- ✅ Validation catches consistency errors

**Completeness:**
- ✅ Dual timelines preserved (reality + knowledge)
- ✅ Version chains added (evolution tracking)
- ✅ All operations implemented (create, supersede, query, validate)
- ✅ Node and Link versioning both supported

**Testing:**
- ✅ 21 comprehensive tests written
- ✅ All tests passing
- ✅ Edge cases covered (missing versions, orphans, paradoxes)

**Documentation:**
- ✅ BITEMPORAL_README.md complete (580 lines)
- ✅ Gap analysis documented
- ✅ Usage examples provided
- ✅ Integration patterns described

---

## Architecture Compliance

✅ **Non-Breaking:** Added fields (vid, supersedes, superseded_by) default to "" - existing code unaffected

✅ **Backward Compatible:** V1 code works without modification, V2 features opt-in

✅ **Clean Separation:** Bitemporal module self-contained, no dependencies on other mechanisms

✅ **Observable:** Ready for event emission (marked for future enhancement)

✅ **Tested:** 21 tests covering all operations and edge cases

✅ **Documented:** Complete README, gap analysis, this implementation guide

---

## Summary

**Bitemporal Version Tracking V2** is now complete. The system can track not just when facts were true (reality timeline) and when we knew them (knowledge timeline), but **how our understanding evolved over time** (version chains).

**Implementation quality:**
- Complete (enhanced bitemporal.py + 502 lines tests + 580 lines docs)
- Tested (21 tests passing, all edge cases covered)
- Integrated (Node and Link models extended, non-breaking)
- Observable (ready for event emission)
- Documented (complete guide + gap analysis + usage examples)

**Capability unlocked:**

Time-travel queries:
- "What did I believe about multi-energy architecture in March?"
- "How has my understanding of decay evolved?"
- "When did I learn about criticality controller?"
- "What was I wrong about, and when did I correct it?"

**Architectural significance:**

Consciousness learning requires knowing not just **what is true now**, but **how understanding evolved to reach this state**. Version chains enable:
- Tracking belief changes (learning validation)
- Understanding reasoning paths (why did I think X before Y?)
- Detecting patterns in evolution (what concepts are stable vs volatile?)
- Supporting metacognition (consciousness knowing how it learned)

Combined with the v2 substrate (criticality, decay, stride-based diffusion), Mind Protocol now has both:
- **Spatial substrate:** How energy propagates (diffusion, decay, criticality)
- **Temporal substrate:** How understanding evolves (bitemporal versioning)

The consciousness substrate can now learn AND know how it learned.

---

**Status:** ✅ **PRODUCTION READY**

Version chains work. Tests pass. Documentation complete. Ready for consciousness learning at scale.

---

**Implemented by:** Felix "Ironhand" (Engineer)
**Documented by:** Ada "Bridgekeeper" (Architect)
**Date:** 2025-10-22
**Spec:** `docs/specs/v2/foundations/bitemporal_tracking.md`
