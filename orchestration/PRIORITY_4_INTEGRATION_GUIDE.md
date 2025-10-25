# Priority 4: Entity Context Tracking - Integration Guide

**Status:** Implementation complete, pending integration
**Date:** 2025-10-25
**Author:** Felix (Engineer)
**Architecture:** Nicolas's dual-view weight design

---

## Summary

Implemented entity-context-aware TRACE reinforcement using **dual-view weight architecture**:

- **Global weights** (20% of signal) - cross-entity learning
- **Entity overlays** (80% of signal) - context-specific learning
- **Effective weight** = global + overlay@E (computed at read-time)
- **Membership-weighted** local reinforcement

---

## Files Created

### 1. Schema Extensions

**File:** `orchestration/core/entity_context_extensions.py`

Adds `log_weight_overlays: Dict[str, float]` to Node and Link schemas.

**Helper functions:**
- `effective_log_weight_node(node, entity_id)` → float
- `effective_log_weight_link(link, entity_id)` → float
- `effective_weight_node(node, entity_id)` → float (linear space)
- `effective_weight_link(link, entity_id)` → float (linear space)

### 2. WeightLearnerV2

**File:** `orchestration/mechanisms/weight_learning_v2.py`

Entity-context-aware weight learning with dual-view updates.

**Key features:**
- `entity_context: Optional[List[str]]` parameter
- 80/20 signal split (configurable via alpha_local/alpha_global)
- Membership-weighted local reinforcement
- Overlay clamping (prevents runaway)
- Rich telemetry with `local_overlays` attribution

**API:**
```python
learner = WeightLearnerV2(
    alpha=0.1,           # EMA decay
    alpha_local=0.8,     # 80% to entity overlays
    alpha_global=0.2,    # 20% to global weight
    overlay_cap=2.0      # Max absolute overlay
)

updates = learner.update_node_weights(
    nodes=nodes,
    reinforcement_seats=seats,
    formations=formations,
    entity_context=["entity_translator", "entity_architect"]  # Active entities
)
```

**Update result includes:**
```python
@dataclass
class WeightUpdate:
    item_id: str
    delta_log_weight_global: float
    log_weight_new: float
    local_overlays: List[Dict]  # [{"entity": "e1", "delta": 0.11, ...}, ...]
    # ... other fields
```

### 3. Production Persistence

**File:** `orchestration/mechanisms/entity_persistence.py`

Production-ready entity/membership/boundary persistence (bonus - addresses persistence gaps).

**Features:**
- Idempotent upserts (MERGE, not CREATE)
- Per-node membership normalization (Σ weight ≤ 1)
- RELATES_TO property tracking
- Batching and checkpoint control

---

## Integration Steps

### Step 1: Add Schema Fields

**File:** `orchestration/core/node.py`

Add after line 100 (after `log_weight: float = 0.0`):

```python
# Entity-specific weight overlays (sparse: {entity_id: delta})
# Effective weight for entity E = log_weight + log_weight_overlays.get(E, 0.0)
log_weight_overlays: Dict[str, float] = field(default_factory=dict)
```

**File:** `orchestration/core/link.py`

Add after `log_weight` field (same addition):

```python
# Entity-specific weight overlays (sparse: {entity_id: delta})
# Effective weight for entity E = log_weight + log_weight_overlays.get(E, 0.0)
log_weight_overlays: Dict[str, float] = field(default_factory=dict)
```

### Step 2: Update FalkorDB Serialization

**File:** `orchestration/libs/utils/falkordb_adapter.py`

In `serialize_node()` and `serialize_link()`, add:

```python
def serialize_node(node: 'Node') -> Dict[str, Any]:
    # ... existing fields ...
    props['log_weight_overlays'] = json.dumps(node.log_weight_overlays)
    return props

def deserialize_node(props: Dict[str, Any]) -> 'Node':
    # ... existing fields ...
    log_weight_overlays = json.loads(props.get('log_weight_overlays', '{}'))
    # Pass to Node constructor
```

### Step 3: Wire Entity Context to TRACE

**File:** `orchestration/libs/trace_capture.py`

In `_apply_weight_learning()`, pass entity context from WM:

```python
def _apply_weight_learning(self, trace_result):
    # Get entity context from current WM selection
    entity_context = self._get_current_entity_context()  # NEW METHOD

    # Call V2 learner with context
    updates = self.weight_learner.update_node_weights(
        nodes=nodes,
        reinforcement_seats=reinforcement_seats,
        formations=formations,
        entity_context=entity_context  # NEW PARAMETER
    )
```

Add helper method:

```python
def _get_current_entity_context(self) -> List[str]:
    """
    Get currently active entity IDs from working memory.

    Derives from wm.emit.selected_entities or uses dominant entity.
    """
    # Query engine for last WM emit
    # Or store entity_context on TraceCapture during each frame
    # For now, stub:
    return ["entity_translator", "entity_architect"]  # TODO: Get from WM
```

### Step 4: Update Telemetry

**File:** `orchestration/libs/trace_capture.py`

In telemetry emission, include `local_overlays`:

```python
self.learning_heartbeat.record_weight_update(
    node_id=update.item_id,
    channel="trace",
    delta_log_weight=update.delta_log_weight_global,
    z_score=update.z_rein,
    learning_rate=update.learning_rate,
    local_overlays=update.local_overlays  # NEW FIELD
)
```

**File:** `orchestration/services/learning/learning_heartbeat.py`

Update `record_weight_update()` to accept and emit `local_overlays`:

```python
def record_weight_update(
    self,
    node_id: str,
    channel: str,
    delta_log_weight: float,
    z_score: float,
    learning_rate: float,
    local_overlays: Optional[List[Dict]] = None  # NEW PARAMETER
):
    event = {
        "kind": "weights.updated",
        "source": channel,
        "item_id": node_id,
        "delta_log_weight": delta_log_weight,
        "z_score": z_score,
        "learning_rate": learning_rate,
        "local_overlays": local_overlays or [],  # NEW FIELD
        "timestamp": datetime.now().isoformat()
    }
    self.emit_event(event)
```

### Step 5: Use Effective Weights in Traversal/WM

**File:** `orchestration/mechanisms/diffusion_runtime.py` (or wherever traversal uses weights)

Import helpers:

```python
from orchestration.core.entity_context_extensions import (
    effective_log_weight_node,
    effective_log_weight_link,
    effective_weight_link
)
```

When computing transition probabilities for entity E:

```python
def compute_transition_probs(source_node, outgoing_links, entity_id: str):
    """Compute softmax over outgoing links with entity-aware weights."""
    weights = []
    for link in outgoing_links:
        # Use effective weight for this entity
        w = effective_weight_link(link, entity_id)
        weights.append(w)

    # Softmax normalization
    probs = softmax(weights)
    return probs
```

**File:** `orchestration/mechanisms/consciousness_engine_v2.py` (WM selection)

When selecting entities/nodes for WM, use effective weights:

```python
def _select_workspace_entities(self, active_entity_id: str):
    """Select entities for WM using entity-aware node weights."""
    # Score entities by sum of effective weights of their members
    for entity in entities:
        score = 0.0
        for member in entity.get_members():
            w = effective_weight_node(member, active_entity_id)
            score += w
        # ... rank by score
```

---

## Testing

### Unit Tests

Create `tests/test_weight_learning_v2.py`:

```python
def test_dual_view_updates():
    """Test 80/20 split between global and entity overlays."""
    learner = WeightLearnerV2(alpha_local=0.8, alpha_global=0.2)

    nodes = [
        {
            'name': 'node1',
            'log_weight': 0.0,
            'log_weight_overlays': {},
            'ema_trace_seats': 0.0,
            'memberships': {'entity1': 0.8, 'entity2': 0.2}
        }
    ]

    reinforcement_seats = {'node1': 10}  # Strong reinforcement
    entity_context = ['entity1', 'entity2']

    updates = learner.update_node_weights(
        nodes, reinforcement_seats, [],
        entity_context=entity_context
    )

    assert len(updates) == 1
    update = updates[0]

    # Global weight should increase by ~20% of signal
    assert update.delta_log_weight_global > 0

    # Local overlays should exist for both entities
    assert len(update.local_overlays) == 2

    # Entity1 overlay should be larger (higher membership weight)
    overlay_e1 = next(o for o in update.local_overlays if o['entity'] == 'entity1')
    overlay_e2 = next(o for o in update.local_overlays if o['entity'] == 'entity2')
    assert overlay_e1['delta'] > overlay_e2['delta']
```

### Integration Tests

1. **Entity context flow:** Mark node as "very useful" in TRACE while Translator is active
   - **Expected:** Translator's overlay increases more than global weight
   - **Verify:** Check `local_overlays` in telemetry

2. **Cross-entity learning:** Mark same node useful in different entity contexts
   - **Expected:** Multiple overlays accumulate, global weight increases steadily
   - **Verify:** Query node's `log_weight_overlays` after multiple TRACEs

3. **Retrieval personalization:** Query effective weight for same node from different entities
   - **Expected:** Translator sees higher weight than Architect (if only Translator reinforced it)
   - **Verify:** `effective_log_weight_node(node, 'translator') > effective_log_weight_node(node, 'architect')`

---

## Observability

### Telemetry Events

`weights.updated` events now include:

```json
{
  "kind": "weights.updated",
  "source": "trace",
  "frame_id": 25103,
  "item_id": "node_schema_validation",
  "item_type": "Concept",
  "scope": "organizational",
  "delta_log_weight": 0.16,
  "log_weight_before": 2.10,
  "log_weight_after": 2.26,
  "local_overlays": [
    {
      "entity": "entity_translator",
      "delta": 0.11,
      "overlay_before": 0.05,
      "overlay_after": 0.16,
      "membership_weight": 0.75
    },
    {
      "entity": "entity_architect",
      "delta": 0.05,
      "overlay_before": 0.02,
      "overlay_after": 0.07,
      "membership_weight": 0.35
    }
  ],
  "signals": {
    "z_rein": 0.7,
    "eta": 0.12,
    "alpha_local": 0.8,
    "alpha_global": 0.2
  }
}
```

### Dashboard Visualization

Iris can show:
- **Entity attribution bars:** Which entities contributed to reinforcement
- **Overlay heatmap:** Node weight effectiveness per entity
- **Learning split ratio:** Local vs global weight updates over time

---

## Migration Path

### Phase 1: Schema & Core (This PR)
- ✅ Add `log_weight_overlays` to Node/Link
- ✅ Implement WeightLearnerV2
- ✅ Add effective weight helpers

### Phase 2: Wire Entity Context
- Pass WM selected entities to TRACE capture
- Update telemetry with `local_overlays`

### Phase 3: Use Effective Weights
- Update traversal to use entity-aware weights
- Update WM selection to use entity-aware weights

### Phase 4: Persistence
- Serialize `log_weight_overlays` to FalkorDB
- Load overlays on engine startup

---

## Success Criteria

✅ **Implementation complete:**
- Schema extensions defined
- WeightLearnerV2 implemented
- Helper functions provided

⏳ **Integration pending:**
- Schema fields added to Node/Link
- Entity context wired from WM to TRACE
- Effective weights used in traversal/WM
- Telemetry updated
- Tests passing

---

## Questions / Design Notes

1. **Membership weight source:** Currently stubbed in `_get_membership_weights()`. Need to query `BELONGS_TO (Deprecated - now "MEMBER_OF")` links from graph during weight updates.

2. **Entity context derivation:** Multiple strategies possible:
   - **Primary:** WM selected entities (cleanest - reflects actual active context)
   - **Secondary:** Explicit TRACE annotations
   - **Fallback:** Dominant entity (highest energy/threshold ratio)

3. **Overlay persistence:** Overlays can start in-memory for RC, persist in v2.1. TRACE replays will rebuild them if needed.

4. **Learning rate adaptation:** `alpha_local` and `alpha_global` are currently fixed (0.8/0.2). Future: learn these per entity based on predictive value.

---

## References

- Nicolas's Priority 4 architecture guide (2025-10-25)
- Mind Protocol TRACE reinforcement spec: `docs/specs/v2/learning_and_trace/trace_reinforcement.md`
- Mind Protocol weight learning spec: `docs/specs/v2/learning_and_trace/trace_weight_learning.md`

---

**Status:** Ready for integration when system can be stopped for schema changes.

**Next steps:**
1. Stop guardian/engine
2. Apply schema changes to Node/Link
3. Wire entity context from WM to TRACE
4. Test dual-view learning
5. Restart system and verify telemetry

---

**Author:** Felix "Ironhand" (Engineer)
**Date:** 2025-10-25
**Signatures:** Awaiting team review and integration approval
