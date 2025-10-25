# Priority 4: Entity Context Integration - COMPLETE

**Status:** ✅ Integration complete, ready for testing
**Date:** 2025-10-24
**Author:** Felix (Engineer)
**Architecture:** Nicolas's dual-view weight design

---

## Summary

Successfully integrated entity-context-aware TRACE reinforcement using **dual-view weight architecture**:

- **Global weights** (20% of signal) - cross-entity learning
- **Entity overlays** (80% of signal) - context-specific learning
- **Effective weight** = global + overlay@E (computed at read-time)
- **Membership-weighted** local reinforcement

---

## What Was Completed

### Phase 1: Core Infrastructure (DONE ✅)

**Files created:**
1. `orchestration/core/entity_context_extensions.py` - Schema extensions and helper functions
2. `orchestration/mechanisms/weight_learning_v2.py` - Entity-aware weight learning
3. `orchestration/libs/entity_context_trace_integration.py` - Entity context derivation and membership querying

**Key components:**
- Dual-view weight model (global + sparse overlays)
- 80/20 signal split (configurable via alpha_local/alpha_global)
- Membership-weighted local reinforcement
- Overlay clamping (prevents runaway)

### Phase 2: TRACE Capture Integration (DONE ✅)

**File modified:** `orchestration/libs/trace_capture.py`

**Changes made:**
1. **Imports updated** (lines 24-29):
   - Switched from `WeightLearner` to `WeightLearnerV2`
   - Added `EntityContextManager`, `MembershipQueryHelper`, `enhance_nodes_with_memberships`

2. **Initialization updated** (lines 76-95):
   ```python
   self.weight_learner = WeightLearnerV2(
       alpha=0.1,           # EMA decay
       alpha_local=0.8,     # 80% to entity overlays
       alpha_global=0.2,    # 20% to global weight
       overlay_cap=2.0      # Max absolute overlay
   )
   self.entity_context_manager = EntityContextManager(self.graph_store)
   self.membership_helper = MembershipQueryHelper(self.graph_store)
   ```

3. **Entity context derivation** (lines 238-259):
   - Derives entity context using priority logic (WM → TRACE annotations → dominant entity)
   - Queries BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") memberships for nodes being updated
   - Enhances node dicts with membership data

4. **Dual-view weight updates** (lines 262-267):
   ```python
   updates = self.weight_learner.update_node_weights(
       nodes=all_nodes,
       reinforcement_seats=reinforcement_seats,
       formations=node_formations,
       entity_context=entity_context  # NEW: Entity-aware learning
   )
   ```

5. **Overlay persistence** (lines 282-306):
   - Builds overlays dict from `local_overlays` list
   - Persists `log_weight_overlays` to FalkorDB as JSON
   - Uses `json.dumps()` for proper serialization

6. **Entity attribution logging** (lines 313-329):
   - Logs global weight changes
   - Logs entity-specific overlay deltas
   - Rich debug output showing which entities contributed

7. **Telemetry emission** (lines 332-339):
   ```python
   self.learning_heartbeat.record_weight_update(
       node_id=node_id,
       channel="trace",
       delta_log_weight=delta_log_weight,
       z_score=update.z_rein,
       learning_rate=update.learning_rate,
       local_overlays=update.local_overlays  # NEW: Entity attribution
   )
   ```

### Phase 3: Telemetry Integration (DONE ✅)

**File modified:** `orchestration/services/learning/learning_heartbeat.py`

**Changes made:**
1. **Weight updates tracking** (line 58):
   ```python
   self.weight_updates = []  # Individual weight updates for detailed telemetry
   ```

2. **New method: record_weight_update()** (lines 60-101):
   - Records individual weight updates with entity attribution
   - Includes `local_overlays` with entity deltas and membership weights
   - Timestamps each update

3. **Heartbeat output updated** (lines 159, 168):
   - Added `weight_updates` array to heartbeat JSON
   - Resets after each write to prevent memory growth

**Heartbeat format example:**
```json
{
  "timestamp": "2025-10-24T17:30:00",
  "weight_updates": [
    {
      "node_id": "node_schema_validation",
      "channel": "trace",
      "delta_log_weight": 0.16,
      "z_score": 0.7,
      "learning_rate": 0.12,
      "timestamp": "2025-10-24T17:30:00.123",
      "local_overlays": [
        {
          "entity": "entity_translator",
          "delta": 0.11,
          "overlay_after": 0.16,
          "membership_weight": 0.75
        },
        {
          "entity": "entity_architect",
          "delta": 0.05,
          "overlay_after": 0.07,
          "membership_weight": 0.35
        }
      ]
    }
  ]
}
```

---

## What Still Needs to Be Done

### Schema Changes (NOT DONE ⏳)

**Required:** Add `log_weight_overlays` field to Node and Link classes

**File:** `orchestration/core/node.py`

Add after `log_weight` field:
```python
# Entity-specific weight overlays (sparse: {entity_id: delta})
# Effective weight for entity E = log_weight + log_weight_overlays.get(E, 0.0)
log_weight_overlays: Dict[str, float] = field(default_factory=dict)
```

**File:** `orchestration/core/link.py`

Same addition after `log_weight` field.

**Impact:** Without this, overlays are persisted to DB but not loaded back into memory on engine restart.

### Read-Time Integration (NOT DONE ⏳)

**Required:** Update traversal and WM selection to use effective weights

**Files to modify:**
- `orchestration/mechanisms/diffusion_runtime.py` - Use `effective_weight_link()` for transition probabilities
- `orchestration/mechanisms/consciousness_engine_v2.py` - Use `effective_weight_node()` for WM selection

**Example:**
```python
from orchestration.core.entity_context_extensions import effective_weight_link

def compute_transition_probs(source_node, outgoing_links, entity_id: str):
    """Compute softmax over outgoing links with entity-aware weights."""
    weights = [effective_weight_link(link, entity_id) for link in outgoing_links]
    probs = softmax(weights)
    return probs
```

### Entity Context Wiring (PARTIAL ⚠️)

**Current:** Uses fallback to dominant entity (highest energy/threshold ratio)

**TODO:** Wire actual WM selected entities

**File:** `orchestration/libs/trace_capture.py` line 241

Change from:
```python
entity_context = self.entity_context_manager.derive_entity_context(
    wm_entities=None,  # TODO: Get from last WM emit event
    trace_annotations=None,  # TODO: Extract [entity: X] marks from TRACE
    graph_name=self.scope_to_graph['personal']
)
```

To:
```python
# Get WM selected entities from last wm.emit event
wm_entities = self._get_last_wm_entities()  # NEW METHOD NEEDED

entity_context = self.entity_context_manager.derive_entity_context(
    wm_entities=wm_entities,
    trace_annotations=None,  # TODO: Parse from TRACE content
    graph_name=self.scope_to_graph['personal']
)
```

**Impact:** Currently works but doesn't use actual WM entity selection, falls back to dominant entity logic.

### Testing (NOT DONE ⏳)

**Unit tests needed:**
- `tests/test_weight_learning_v2.py` - Test dual-view updates, 80/20 split, overlay capping
- `tests/test_entity_context_integration.py` - Test entity context derivation, membership querying

**Integration tests needed:**
1. Entity context flow: Mark node useful in TRACE → verify entity overlay increases
2. Cross-entity learning: Mark same node from different entities → verify multiple overlays
3. Retrieval personalization: Query effective weight from different entity contexts

---

## How to Test

### Manual Testing

1. **Start the system:**
   ```bash
   python guardian.py
   ```

2. **Trigger a TRACE with reinforcement:**
   Send a message that will generate TRACE format with node markings:
   ```
   Nicolas asks about entity context [node_entity_context_design: very useful]
   ```

3. **Check logs:**
   ```bash
   tail -f orchestration.log | grep "Entity context"
   tail -f orchestration.log | grep "WeightLearnerV2"
   ```

   Expected output:
   ```
   [TraceCapture] Entity context derived: ['entity_dominant_entity']
   [TraceCapture] Queried memberships for 5 nodes
   [TraceCapture] WeightLearnerV2 produced 5 updates with entity attribution
   [TraceCapture] Updated node_entity_context_design: global=0.123 (+0.016), overlays=[entity_translator: +0.110], ema_trace=2.45
   ```

4. **Check heartbeat:**
   ```bash
   cat .heartbeats/learning_*.json | jq '.weight_updates'
   ```

   Expected: Array of weight updates with `local_overlays` showing entity attribution.

5. **Verify database persistence:**
   ```bash
   redis-cli
   > GRAPH.QUERY citizen_felix "MATCH (n {name: 'node_entity_context_design'}) RETURN n.log_weight_overlays"
   ```

   Expected: JSON string with entity overlays: `{"entity_translator": 0.11, ...}`

### Integration Testing

**Test 1: Entity context derivation**
- Send TRACE with active entities
- Verify entity context is derived correctly (logs show entity IDs)
- Verify membership query returns weights
- Verify overlays are created for active entities only

**Test 2: Dual-view learning**
- Mark a node as "very useful"
- Verify global weight increases by ~20% of signal
- Verify entity overlays increase by ~80% of signal
- Verify membership weights modulate local updates

**Test 3: Overlay persistence**
- Mark a node, check DB for `log_weight_overlays` field
- Restart engine
- Verify overlays are loaded back correctly (requires schema changes)

**Test 4: Telemetry completeness**
- Trigger weight update
- Check heartbeat JSON for `local_overlays` array
- Verify entity attribution shows correct deltas and membership weights

---

## Success Criteria

✅ **Implementation complete:**
- WeightLearnerV2 with dual-view architecture
- EntityContextManager with priority logic
- MembershipQueryHelper with BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") querying
- TRACE capture integration
- Overlay persistence to DB
- Telemetry with entity attribution

⏳ **Schema changes needed:**
- Add `log_weight_overlays` to Node/Link classes

⏳ **Read-time integration needed:**
- Update traversal to use effective weights
- Update WM selection to use effective weights

⏳ **Testing needed:**
- Unit tests for V2 learner
- Integration tests for entity context flow
- End-to-end verification

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     TRACE CAPTURE                           │
│                                                             │
│  1. Parse TRACE format                                      │
│  2. Derive entity context                                   │
│     ├─ WM selected entities (priority 1)                    │
│     ├─ TRACE annotations (priority 2)                       │
│     └─ Dominant entity (priority 3, fallback)              │
│  3. Query BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") memberships                            │
│  4. Enhance nodes with membership data                      │
│  5. Call WeightLearnerV2 with entity_context               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  WEIGHT LEARNER V2                          │
│                                                             │
│  For each node with reinforcement:                          │
│                                                             │
│  Global Update (20%):                                       │
│    Δlog_weight_global = 0.2 * η * z_total                  │
│                                                             │
│  Entity Overlay Updates (80%, membership-weighted):         │
│    For each entity E in entity_context:                     │
│      membership = node.memberships[E]                       │
│      Δoverlay[E] = 0.8 * η * z_total * membership          │
│      overlay[E] = clamp(overlay[E] + Δ, -2.0, +2.0)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PERSISTENCE                              │
│                                                             │
│  Write to FalkorDB:                                         │
│    n.log_weight = global_weight                            │
│    n.log_weight_overlays = JSON({entity: delta, ...})      │
│    n.ema_trace_seats = ...                                 │
│    n.ema_formation_quality = ...                           │
│                                                             │
│  Emit telemetry:                                            │
│    record_weight_update(                                    │
│      node_id, delta_global, z_score, learning_rate,        │
│      local_overlays=[{entity, delta, overlay_after, ...}]  │
│    )                                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    HEARTBEAT OUTPUT                         │
│                                                             │
│  .heartbeats/learning_YYYYMMDD_HHMMSS.json:                │
│  {                                                          │
│    "weight_updates": [                                      │
│      {                                                      │
│        "node_id": "...",                                    │
│        "delta_log_weight": 0.16,                           │
│        "local_overlays": [                                  │
│          {"entity": "translator", "delta": 0.11, ...},     │
│          {"entity": "architect", "delta": 0.05, ...}       │
│        ]                                                    │
│      }                                                      │
│    ]                                                        │
│  }                                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

1. **Sparse overlays:** Only store overlays for entities that marked items (no memory overhead)
2. **Single energy substrate:** Maintain one E per node (no per-entity energies)
3. **80/20 split:** Configurable via `alpha_local`/`alpha_global` for experimentation
4. **Overlay capping:** Max absolute overlay ±2.0 prevents runaway reinforcement
5. **Membership weighting:** Local updates scaled by BELONGS_TO (Deprecated - now "MEMBER_OF") (Deprecated - now "MEMBER_OF") weights (Σ weight ≤ 1.0 per node)
6. **Priority derivation:** WM entities > TRACE annotations > dominant entity (cleanest to fallback)
7. **Read-time composition:** Effective weight = global + overlay@E (computed when needed, not stored)

---

## Next Steps

**Immediate (for RC):**
1. Add `log_weight_overlays` to Node/Link schema
2. Test entity context flow manually
3. Verify overlays persist and reload correctly
4. Check telemetry contains entity attribution

**Phase 2 (for v2.1):**
1. Wire actual WM entity selection (not just dominant fallback)
2. Update traversal to use effective weights
3. Update WM selection to use effective weights
4. Create unit tests for V2 learner
5. Create integration tests for entity context flow

**Future enhancements:**
1. Learn `alpha_local`/`alpha_global` per entity based on predictive value
2. Entity-specific overlay decay rates
3. Dashboard visualization of entity attribution
4. Entity performance metrics (which entities learn fastest)

---

**Status:** Ready for testing and schema integration

**Author:** Felix "Ironhand" (Engineer)
**Date:** 2025-10-24
**Signatures:** Awaiting testing and production deployment
