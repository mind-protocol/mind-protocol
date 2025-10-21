# Entity Stream Format Mismatch: v1 vs v2

**Author:** Iris "The Aperture"
**Date:** 2025-10-21
**Status:** Documented Reality vs Aspiration

---

## Summary

Discovered critical architectural mismatch between **designed v2 event format** and **existing v1 state delta format**. Adapted frontend to consume reality (v1) instead of building aspirational v2 backend.

---

## The Design (v2 Format - Aspirational)

**What I Originally Designed:**

Frame-based event stream with 14 granular event types:

```typescript
// v2 Event Format (from types.ts)
type VizEvent =
  | FrameStart       // { v: "2", kind: "frame.start", frame_id: number, rho?: number, ... }
  | FrameEnd         // { v: "2", kind: "frame.end", frame_id: number, ... }
  | StrideExec       // { v: "2", kind: "stride.exec", entity: string, src: string, tgt: string, ΔE: number, φ: number, ... }
  | NodeFlip         // { v: "2", kind: "node.flip", node_id: string, E_new: number, Theta_new: number, ... }
  | EntityFlip       // { v: "2", kind: "entity.flip", entity_id: string, E_new: number, Theta_new: number }
  | LinkFlowSummary  // { v: "2", kind: "link.flow.summary", ... }
  | EntityBoundarySummary  // { v: "2", kind: "entity.boundary.summary", pairs: [...] }
  | ... (11 more event types)
```

**Characteristics:**
- Per-event granularity (each stride, each flip is a separate event)
- Frame-based batching with `frame_id`
- Entity-level and node-level events separate
- Cross-layer routing signals (src_entity, tgt_entity)
- Designed for dual-layer rendering (entity graph vs node bubbles)

---

## The Reality (v1 Format - What Exists)

**What viz_emitter.py Actually Emits:**

Batched state deltas with single event type:

```json
{
  "kind": "state_delta.v1",
  "tick_id": 315458,
  "ts": "2025-10-21T15:25:54.580412",
  "dt_ms": 17433,
  "coalesced_ticks": 1744,
  "entity_filter": null,
  "nodes": [
    {
      "id": "phenomenological_truth",
      "entity_energies": {"translator": 4.2, "architect": 1.8},
      "total_energy": 6.0,
      "threshold": 5.0,
      "active": true,
      "soft_activation": 0.73,
      "pos": [512.1, 304.7]
    }
  ],
  "nodes_removed": [],
  "links": [
    {
      "src": "phenomenological_truth",
      "dst": "consciousness_substrate",
      "type": "ENABLES",
      "weight": 0.81,
      "emotion": {"valence": 0.7, "arousal": 0.4},
      "yearning_strength": 0.65,
      "active": true,
      "flow_rate": 0.024,
      "traversal_history": {
        "last_entity": "translator",
        "last_tick": 315456,
        "count_total": 47,
        "count_1m": 12
      }
    }
  ],
  "links_removed": [],
  "metrics": {
    "rho": 1.03,
    "global_energy": 24.7,
    "active_nodes": 47,
    "active_links": 128,
    "active_entities": {
      "translator": {"node_count": 23, "total_energy": 8.4},
      "architect": {"node_count": 15, "total_energy": 4.2}
    },
    "budget": {
      "nodes_sent": 2,
      "nodes_budget": 150,
      "links_sent": 1,
      "links_budget": 1000
    }
  }
}
```

**Characteristics:**
- Single event type with batched arrays
- Tick-based (not frame-based)
- Deletion tracking via `nodes_removed`, `links_removed`
- Budget constraints (max 150 nodes, 1000 links per delta)
- Soft activation for sub-threshold nodes
- Entity energies per node (multi-entity support)
- Coalesced ticks (frame skip when too fast)

---

## Why the Mismatch Matters

**v2 Design Assumptions:**
1. Separate entity-level and node-level streams
2. Per-event processing with reorder buffer
3. Frame-based synchronization
4. Granular event types for different rendering strategies

**v1 Reality:**
1. Unified node/link state deltas
2. Batched updates with budget constraints
3. Tick-based with coalescing
4. Single event type, all changes in arrays

**Incompatibility:** Frontend expecting v2 format would fail to parse v1 events completely.

---

## Decision: Adapt to Reality

**Why Adapt v1 Instead of Building v2:**

1. **Verification over expansion** - Nicolas's principle: "prove what exists works before building more"
2. **v1 backend exists and runs** - `viz_emitter.py` (668 lines) is functional on port 8765
3. **v2 backend doesn't exist** - would require building entire event emission layer
4. **v1 is simpler** - single event type vs 14 types, easier to consume
5. **v1 has budget controls** - prevents overwhelming frontend with large graphs
6. **v1 has soft activation** - shows sub-threshold node activity

---

## What Was Adapted

### Before (v2 Design)

**Hook:** `useEntityStream.ts` (450+ lines)
- 2-frame reorder buffer
- Per-event type processing (14 cases)
- Frame-based state synchronization
- Entity expansion API calls
- Complex cache management

### After (v1 Reality)

**Hook:** `useEntityStream.ts` (292 lines)
- Simple batched array processing
- Single event type handling
- Tick-based state updates
- Direct node/link Map updates
- Metrics tracking

**Simplification:** 35% fewer lines, simpler logic, same functionality

---

## What Still Works

Even with v1 format, we can still achieve:

✅ **Real-time node/link updates** - via state deltas
✅ **Active node tracking** - `active: true/false` field
✅ **Entity awareness** - `entity_energies` per node
✅ **Traversal history** - `traversal_history` on links
✅ **Soft activation visualization** - show sub-threshold activity
✅ **Budget-aware rendering** - backend sends top-N nodes/links
✅ **Deletion tracking** - `nodes_removed`, `links_removed`
✅ **Global metrics** - rho, energy, active counts

---

## What We Lost (v2 Features Not in v1)

❌ **Per-stride granularity** - can't see individual stride.exec events
❌ **Entity boundary summaries** - no entity.boundary.summary events
❌ **Frame synchronization** - no frame.start/frame.end markers
❌ **WM emission events** - no wm.emit tracking
❌ **Trace parsing events** - no trace.parsed signals

**Impact:** Less granular observability, but core visualization still works.

---

## Current Status

**✅ Complete:**
- viz_emitter.py running on ws://localhost:8765
- useEntityStream.ts adapted to consume v1 format
- Test page created at http://localhost:3000/test-entity-stream
- TypeScript compiles without errors
- WebSocket connection established

**⏳ Pending:**
- Verify frontend actually receives and renders data
- Create `/api/viz/snapshot` REST endpoint for initial state
- Integrate into main consciousness page
- Run complete verification tests

---

## Future: When to Build v2

**Build v2 backend when:**
1. Need per-stride granularity for debugging
2. Need entity boundary flow visualization
3. Need frame-synchronized rendering
4. Need WM/trace event correlation
5. Have proven v1 works end-to-end first

**Until then:** Use v1, document limitations, focus on making visualization functional.

---

## Lessons Learned

1. **Check what exists before designing** - I designed v2 without checking if backend existed
2. **Verify format compatibility early** - caught mismatch during testing, not deployment
3. **Adapt to reality over perfection** - working v1 > aspirational v2
4. **Simplicity is a feature** - v1's single event type is easier to debug
5. **Backend drives frontend** - frontend must consume what backend emits

---

## References

- **v1 Implementation:** `orchestration/viz_emitter.py` (lines 215-299: encode_tick_frame)
- **v1 Hook:** `app/consciousness/hooks/useEntityStream.ts`
- **v2 Design:** `app/consciousness/lib/renderer/types.ts` (lines 196-400: VizEvent types)
- **Test Page:** `app/test-entity-stream/page.tsx`

---

**Signature:**

Iris "The Aperture"
Consciousness Observation Architect
2025-10-21

*Reality check complete. Proceeding with what exists, not what was imagined.*
