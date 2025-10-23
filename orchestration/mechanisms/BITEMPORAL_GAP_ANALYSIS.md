# Bitemporal Tracking: Gap Analysis (V2)

**Spec:** `docs/specs/v2/foundations/bitemporal_tracking.md`
**Current:** `orchestration/mechanisms/bitemporal.py`, `orchestration/core/node.py`
**Date:** 2025-10-22

## Executive Summary

The current bitemporal implementation is **FUNCTIONALLY CORRECT** but uses **different naming conventions** and **lacks versioning infrastructure**. The v2 spec introduces immutable version semantics with version chains.

## Naming Differences

### Current Implementation
```python
# Reality timeline
valid_at: datetime
invalidated_at: Optional[datetime]

# Knowledge timeline
created_at: datetime
expired_at: Optional[datetime]
```

### V2 Spec
```python
# Reality timeline
valid_from: datetime
valid_to: Optional[datetime]

# Knowledge timeline
known_from: datetime
known_to: Optional[datetime]
```

**Analysis:** The current implementation uses **point semantics** (at) while v2 spec uses **interval semantics** (from/to). Functionally equivalent for interval queries, but spec naming is more explicit about intervals.

**Decision:** Keep current naming (valid_at/invalidated_at). The "at" names work fine for intervals when paired with None for open-ended ranges. Renaming would be a breaking change with no functional benefit.

**Alternative:** If we must align with spec, this would be a pure rename:
- `valid_at` → `valid_from`
- `invalidated_at` → `valid_to`
- `created_at` → `known_from`
- `expired_at` → `known_to`

## Missing Features from V2 Spec

### 1. ❌ MISSING: Version ID (vid)
**Current:** Nodes have `id` but no separate version identifier
**Spec:** `vid: str` - Immutable version identifier

**Impact:** Cannot distinguish between versions of the same logical entity
**Example:**
```python
# Want to express:
node_v1 = Node(id="context_reconstruction", vid="ctx_recon_v1", ...)
node_v2 = Node(id="context_reconstruction", vid="ctx_recon_v2", ...)  # Supersedes v1
```

**Fix:** Add `vid` field to Node/Link, auto-generate if not provided

### 2. ❌ MISSING: Version Chains
**Current:** No linkage between versions
**Spec:** `supersedes: str | None`, `superseded_by: str | None`

**Impact:** Cannot traverse version history
**Fix:** Add `supersedes` and `superseded_by` fields pointing to vid

### 3. ❌ MISSING: Immutable Version Semantics
**Current:** Nodes are mutable (can edit in-place)
**Spec:** "Prefer immutable versions; never in-place edit a version"

**Impact:** History can be silently corrupted
**Fix:** Add versioning layer that creates new vid on edits

### 4. ❌ MISSING: As-Of Query APIs
**Current:** Functions like `is_currently_valid(at_time)` exist
**Spec:** `GET /nodes/{id}?as_of=knowledge:2025-10-18` and `?as_of=reality:...`

**Impact:** No REST API for time-travel queries
**Fix:** Add query layer that filters by logical id + temporal predicate

### 5. ❌ MISSING: Version Events
**Current:** No events emitted for version lifecycle
**Spec:** `version.create`, `version.supersede`, `version.expire`

**Impact:** Cannot observe version changes
**Fix:** Emit events via broadcaster when versions created/superseded/expired

### 6. ❌ MISSING: Metrics
**Current:** No correction tracking
**Spec:**
- Correction rate (versions/day)
- Median correction latency (known_from - valid_from)
- Belief churn (versions per logical id)
- Retroactivity share (facts backdated)

**Impact:** Cannot measure knowledge evolution
**Fix:** Add metrics collector and emission

### 7. ❌ MISSING: Composite Indices
**Current:** No specific indices
**Spec:** Indices on `(id, known_from/to)` and `(id, valid_from/to)`

**Impact:** As-of queries will be slow on large graphs
**Fix:** Add index hints to storage adapter

### 8. ⚠️ PARTIAL: Supersession Logic
**Current:** `supersede(old, new)` function exists, sets `old.invalidated_at = new.valid_at`
**Spec:** Should also close `known_to` and link versions via `supersedes`/`superseded_by`

**Impact:** Incomplete version handoff
**Fix:** Update `supersede()` to handle both timelines and version fields

## What Works (Keep)

### ✅ Bitemporal Queries
- `is_currently_valid(obj, at_time)` ✓
- `is_currently_known(obj, at_time)` ✓
- `was_valid_during(obj, start, end)` ✓
- `was_known_during(obj, start, end)` ✓

These work correctly with current naming.

### ✅ Timeline Manipulation
- `invalidate(obj, invalidated_at)` ✓
- `expire(obj, expired_at)` ✓
- Basic `supersede(old, new)` ✓

### ✅ Temporal Distance
- `time_since_creation(obj)` ✓
- `time_since_valid(obj)` ✓

### ✅ Validation
- `verify_bitemporal_consistency(obj)` ✓

## Implementation Plan

### Phase 1: Add Version Infrastructure (CRITICAL)
1. Add `vid` field to Node/Link (auto-generate UUID if not provided)
2. Add `supersedes: Optional[str]` (previous vid)
3. Add `superseded_by: Optional[str]` (next vid)
4. Add version generation helper: `create_new_version(node) -> Node`

### Phase 2: Immutable Version Semantics
1. Add `VersionedNode` wrapper that prevents in-place edits
2. Add `Graph.update_node(id, changes)` that creates new version
3. Add version chain traversal: `get_version_history(id)`

### Phase 3: As-Of Queries
1. Add `Graph.get_node_as_of(id, as_of_knowledge, as_of_reality)`
2. Add API endpoints for as-of queries
3. Add indices for efficient temporal queries

### Phase 4: Events & Metrics
1. Emit `version.create` when new version created
2. Emit `version.supersede` when version superseded
3. Emit `version.expire` when knowledge expires
4. Track correction metrics (rate, latency, churn, retroactivity)

### Phase 5: Documentation & Testing
1. Update bitemporal.py docstrings for versioning
2. Add version test suite
3. Add as-of query tests
4. Document version lifecycle

## Breaking Changes

⚠️ **If we rename fields (optional):**
- `valid_at` → `valid_from`
- `invalidated_at` → `valid_to`
- `created_at` → `known_from`
- `expired_at` → `known_to`

This would require updating:
- All Node/Link instantiations
- All bitemporal queries
- FalkorDB schema
- Existing graph data (migration)

**Recommendation:** DON'T rename. Current naming works. Add version infrastructure without breaking existing code.

## Non-Breaking Additions

✅ **Can add without breaking:**
- `vid` field (auto-generate if missing)
- `supersedes`/`superseded_by` fields (optional, default None)
- Version creation helpers
- As-of query layer
- Event emission
- Metrics tracking

## Minimal Viable Implementation

To satisfy spec with minimal changes:

1. **Add 3 fields to Node/Link:**
   ```python
   vid: str = field(default_factory=lambda: f"v_{uuid.uuid4().hex[:8]}")
   supersedes: Optional[str] = None
   superseded_by: Optional[str] = None
   ```

2. **Update supersede() function:**
   ```python
   def supersede(old_obj, new_obj):
       old_obj.invalidated_at = new_obj.valid_at
       old_obj.expired_at = new_obj.created_at  # Close knowledge too
       old_obj.superseded_by = new_obj.vid
       new_obj.supersedes = old_obj.vid
   ```

3. **Add as_of query helper:**
   ```python
   def get_node_as_of(graph, node_id, as_of_knowledge=None, as_of_reality=None):
       # Filter versions by logical id
       versions = [n for n in graph.nodes.values() if n.id == node_id]
       # Apply temporal predicates
       if as_of_knowledge:
           versions = [v for v in versions if is_currently_known(v, as_of_knowledge)]
       if as_of_reality:
           versions = [v for v in versions if is_currently_valid(v, as_of_reality)]
       # Return most recent version
       return max(versions, key=lambda v: v.created_at) if versions else None
   ```

4. **Emit version events** when creating/superseding/expiring versions

This gives 80% of spec value with 20% of implementation effort.

## Open Questions

1. **Storage:** Do we store all versions in same graph, or separate version table?
   - Same graph: Simple, but logical id queries need filtering
   - Separate: Cleaner separation, but more complex

2. **Logical ID:** Should `id` be the logical id (stable) or version id (unique)?
   - Spec suggests `id` = logical (slug), `vid` = version
   - Current code uses `id` as unique identifier
   - **Resolution:** Keep `id` as unique, add `logical_id` field for version grouping

3. **Migration:** Existing nodes have no vid. How to backfill?
   - Auto-generate vid on load: `vid = id + "_v0"`
   - Mark as initial version: `supersedes = None`

4. **Conflict Resolution:** What if two versions created simultaneously?
   - Use `known_from` timestamp as tiebreaker
   - Or: First write wins, second creates branch

## Recommendation

**Implement Minimal Viable (Phase 1 + 2 + 4):**
1. Add vid/supersedes/superseded_by fields
2. Add version creation helpers
3. Update supersede() to handle both timelines
4. Emit version events
5. Skip complex as-of API for now (can query manually)

This satisfies core spec requirements without major breaking changes.
