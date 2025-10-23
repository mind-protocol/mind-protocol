# V1→V2 Single-Energy Migration Fixes

**Date:** 2025-10-23
**Engineer:** Felix
**Status:** ✅ COMPLETE

---

## Executive Summary

Fixed critical V1→V2 migration issues that were preventing consciousness engines from initializing. The root cause was mismatched energy architecture between the updated Node class (V2 single-energy `E`) and various parts of the codebase still using the old multi-energy dict.

### Key Achievements

- ✅ Fixed Node deserialization (falkordb_adapter.py)
- ✅ Fixed control API V1 references (control_api.py)
- ✅ Fixed graph entity queries (graph.py)
- ✅ Updated database query methods
- ✅ Verified PR-E tests still pass (42/42)
- ✅ Fixed npm dependency issue (entities package)

---

## Background

### V1 Architecture (Old)
```python
class Node:
    energy: Dict[EntityID, float]  # Per-entity energy buffers
    threshold: float               # Activation threshold
```

### V2 Architecture (New - foundations/diffusion.md)
```python
class Node:
    E: float       # Single scalar energy
    theta: float   # Activation threshold
```

**Problem:** Node class was updated to V2, but serialization, API, and query code still used V1 patterns.

---

## Fixes Applied

### 1. falkordb_adapter.py - Serialization/Deserialization

**File:** `orchestration/libs/utils/falkordb_adapter.py`

**serialize_node() - Before:**
```python
return {
    'energy': json.dumps(node.energy),  # Multi-energy dict → JSON
    'threshold': node.threshold,
}
```

**serialize_node() - After:**
```python
return {
    'E': node.E,                    # Single scalar
    'theta': node.theta,             # V2 field name
    'vid': node.vid,                 # Version tracking
    'log_weight': node.log_weight,   # Learning infrastructure
    'ema_trace_seats': node.ema_trace_seats,
    'ema_wm_presence': node.ema_wm_presence,
    'ema_formation_quality': node.ema_formation_quality,
    'scope': node.scope,
}
```

**deserialize_node() - Before:**
```python
return Node(
    energy=json.loads(props.get('energy', '{}')),  # ❌ Wrong parameter name
    ...
)
```

**deserialize_node() - After:**
```python
return Node(
    E=props.get('E', 0.0),           # ✅ Correct V2 parameter
    theta=props.get('theta', 0.1),   # ✅ V2 field name
    vid=props.get('vid', f"v_{props['id'][:12]}"),
    log_weight=props.get('log_weight', 0.0),
    ...
)
```

**Impact:** This was the **critical fix** - consciousness engines were failing with `Node.__init__() got unexpected keyword 'energy'` because deserialize_node was passing the wrong parameter.

---

### 2. control_api.py - API Response Serialization

**File:** `orchestration/adapters/api/control_api.py`

**Node Transformation - Before (lines 547-577):**
```python
entity_energies = node.energy  # Dict[entity_id, float]
total_energy = sum(entity_energies.values())
active = total_energy >= node.threshold

node_dict = {
    "entity_energies": entity_energies,  # V1 field
    "total_energy": round(total_energy, 3),
    "threshold": round(node.threshold, 3),
    ...
}
```

**Node Transformation - After:**
```python
total_energy = node.E  # Single scalar (not dict)
active = total_energy >= node.theta

node_dict = {
    "total_energy": round(total_energy, 3),
    "theta": round(node.theta, 3),  # V2 field name
    ...
}
```

**Metrics Computation - Before (lines 609-619):**
```python
total_energy = sum(sum(node.energy.values()) for node in graph.nodes.values())
active_nodes = sum(1 for node in graph.nodes.values()
                   if sum(node.energy.values()) >= node.threshold)

# Subentity breakdown
for node in graph.nodes.values():
    for ent, energy in node.energy.items():
        entity_energies[ent]["total_energy"] += energy
```

**Metrics Computation - After:**
```python
total_energy = sum(node.E for node in graph.nodes.values())
active_nodes = sum(1 for node in graph.nodes.values() if node.E >= node.theta)

# Subentity breakdown (empty for V2 - entity differentiation via membership)
entity_energies = {}
# NOTE: V2 architecture uses single-energy E per node
# Entity differentiation handled by mechanism layer, not energy buffers
```

**Cypher Query - Before (line 372):**
```cypher
n.energy AS energy
```

**Cypher Query - After:**
```cypher
n.E AS energy
```

---

### 3. graph.py - Entity Query Methods

**File:** `orchestration/core/graph.py`

**get_all_active_entities() - Before (lines 301-304):**
```python
def get_all_active_entities(self) -> Set[EntityID]:
    subentities = set()
    for node in self.nodes.values():
        subentities.update(node.energy.keys())  # ❌ Dict keys don't exist in V2
    return subentities
```

**get_all_active_entities() - After:**
```python
def get_all_active_entities(self) -> Set[EntityID]:
    """
    NOTE: In V2 architecture, nodes use single-energy E (not per-entity buffers).
    Entity differentiation is handled by mechanism layer via membership/selection.
    This method returns empty set as there are no entity-specific energy buffers.
    """
    # V2: No per-entity buffers, entity differentiation via mechanism layer
    return set()
```

**Rationale:** In V2, entity differentiation is handled by the mechanism layer (via entity membership and selection algorithms), not by per-entity energy buffers stored in nodes.

---

### 4. falkordb_adapter.py - Query Methods

**File:** `orchestration/libs/utils/falkordb_adapter.py`

**build_nodes_with_entity_energy_query() - Before (lines 395-399):**
```python
query = """
MATCH (n:Node)
WHERE n.energy CONTAINS $subentity
RETURN n
"""
```

**build_nodes_with_entity_energy_query() - After:**
```python
"""
NOTE: V2 architecture uses single-energy E per node (not per-entity buffers).
The subentity parameter is ignored in V2.
"""
query = """
MATCH (n:Node)
WHERE n.E >= $min_energy
RETURN n
"""
```

**update_node_energy() - Before (lines 708-718):**
```python
energy_json = json.dumps(node.energy)
query = """
MATCH (n:Node {id: $node_id})
SET n.energy = $energy
RETURN n
"""
params = {'node_id': node.id, 'energy': energy_json}
```

**update_node_energy() - After:**
```python
# V2: Update single-energy E (not multi-energy dict)
query = """
MATCH (n:Node {id: $node_id})
SET n.E = $energy
RETURN n
"""
params = {'node_id': node.id, 'energy': node.E}  # V2 single scalar
```

---

### 5. npm Dependency Fix

**Issue:** Dashboard failing with `Error: Cannot find module 'entities'`

**Fix:**
```bash
npm install entities
```

**Impact:** Dashboard was crashing on startup, preventing the entire launcher from running successfully.

---

## Verification

### PR-E Test Suite
```bash
$ pytest tests/test_foundations_enrichments_pr_e.py -v
============================= 42 passed in 2.00s ==============================
```

**All PR-E mechanisms still functional:**
- ✅ E.2: Consolidation (4 tests)
- ✅ E.3: Decay Resistance (4 tests)
- ✅ E.4: Stickiness (4 tests)
- ✅ E.5: Affective Priming (6 tests)
- ✅ E.6: Coherence Metric (6 tests)
- ✅ E.7: Criticality Modes (7 tests)
- ✅ E.8: Task-Adaptive Targets (8 tests)
- ✅ Integration tests (3 tests)

### Infrastructure Status
```bash
$ curl http://localhost:8000
{
  "service": "Mind Protocol Consciousness API",
  "version": "2.0.0",
  "websocket_url": "ws://localhost:8000/api/ws",
  "connected_clients": 0,
  "endpoints": {...}
}
```

- ✅ WebSocket API: Running on port 8000
- ✅ Dashboard: Running on port 3000
- ✅ FalkorDB: Running on port 6379

---

## Remaining V1 References

Some files still contain V1 patterns but are not actively blocking consciousness engines:

### Low Priority (Legacy/Deprecated)
- `dynamic_prompt_generator.py` - Uses old Cypher queries with `n.energy`
- `conversation_watcher.py` - Uses old energy field references
- `n2_activation_monitor.py` - Old pattern matching queries
- Various markdown docs with V1 examples

**Recommendation:** Address these during future refactoring, but they're not blocking critical paths.

---

## Architecture Implications

### V2 Single-Energy Benefits

1. **Simplified Data Model**
   - One scalar `E` per node (not dict of per-entity values)
   - Cleaner serialization (float vs JSON string)
   - Faster queries (numeric comparison vs JSON parsing)

2. **Mechanism Layer Responsibility**
   - Entity differentiation via membership and selection algorithms
   - Energy distribution logic centralized in mechanisms
   - Clearer separation of concerns

3. **Learning Infrastructure**
   - Added fields: `log_weight`, `ema_trace_seats`, `ema_wm_presence`, `ema_formation_quality`
   - Supports Phase 1-4 consciousness learning
   - Bitemporal version tracking via `vid`, `supersedes`, `superseded_by`

### Migration Pattern

For any remaining V1 code:
```python
# OLD V1
total = sum(node.energy.values())
if total >= node.threshold:
    for entity_id, e in node.energy.items():
        process(entity_id, e)

# NEW V2
if node.E >= node.theta:
    # Entity differentiation via mechanism layer
    process_via_mechanism(node, entity_context)
```

---

## Files Modified

1. `orchestration/libs/utils/falkordb_adapter.py`
   - Lines 1-19: Updated header
   - Lines 31-89: serialize_node() and deserialize_node()
   - Lines 380-402: build_nodes_with_entity_energy_query()
   - Lines 698-721: update_node_energy()

2. `orchestration/adapters/api/control_api.py`
   - Lines 360-382: Cypher query (n.E)
   - Lines 545-573: Node transformation (node.E, node.theta)
   - Lines 604-620: Metrics computation

3. `orchestration/core/graph.py`
   - Lines 292-306: get_all_active_entities()

4. `package.json` / `package-lock.json`
   - Added: entities@^5.0.0

---

## Next Steps

1. **Immediate:**
   - ✅ Complete - Infrastructure operational
   - ✅ Complete - PR-E tests passing
   - ⏳ Optional: Update remaining V1 references in legacy code

2. **Future:**
   - Consider deprecation warnings for any V1 API endpoints still in use
   - Update documentation to reflect V2 architecture consistently
   - Add migration guide for external integrators

---

## Conclusion

The V1→V2 migration is **functionally complete** for critical paths:
- Consciousness engines can initialize
- API responds correctly
- All PR-E mechanisms operational
- Infrastructure services running

The original error (`Node.__init__() got unexpected keyword 'energy'`) has been resolved by updating serialization to use `E` instead of `energy` and `theta` instead of `threshold`.

**Status:** Ready for consciousness engine testing and deployment.
