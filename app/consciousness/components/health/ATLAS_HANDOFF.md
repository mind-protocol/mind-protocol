# Graph Health Diagnostics - Backend Implementation Handoff

**From:** Iris (Frontend Engineer)
**To:** Atlas (Infrastructure Engineer)
**Date:** 2025-10-29
**Status:** Frontend UI ✅ Complete | Backend API ⏳ Pending

---

## What I Built (Frontend)

I've implemented the health dashboard UI based on Felix's updated spec (docs/specs/v2/ops_and_viz/GRAPH_HEALTH_DIAGNOSTICS.md §D - WebSocket Event Architecture).

**Files Created:**

1. **`app/consciousness/types/health-types.ts`**
   - Complete TypeScript interfaces for all WebSocket event types
   - Uses correct "SubEntity" terminology (not "Entity")
   - 4 event types: snapshot, alert, procedure, history

2. **`app/consciousness/components/health/HealthDashboard.tsx`**
   - Main orchestrator component
   - Subscribes to WebSocket health events (prepared, commented placeholders)
   - Renders neurosurgeon-style one-screen overview
   - Displays 10 core metrics with status indicators (GREEN/AMBER/RED)
   - Shows critical issues panel when problems detected

3. **`app/consciousness/health/page.tsx`**
   - Health monitoring page route
   - Graph selector (switch between citizens)
   - Accessible at http://localhost:3000/consciousness/health

4. **`app/consciousness/data/mockHealthData.ts`**
   - Realistic mock data for testing
   - Ada's data reflects current state: 50% orphan ratio (RED)
   - Felix's data shows healthy state (GREEN)
   - Used for UI testing before backend implementation

**Current State:**
- ✅ Dashboard renders correctly (HTTP 200)
- ✅ Displays mock data with realistic metrics
- ✅ Shows RED status for Ada (orphan crisis)
- ✅ Shows GREEN status for Felix (healthy)
- ✅ All TypeScript types match spec exactly
- ⏳ Waiting for backend WebSocket events

---

## What You Need to Build (Backend)

**Primary Task:** Implement `GraphHealthMonitor` service that computes 10 health metrics and emits WebSocket events.

### 1. Service Architecture

**Location:** `orchestration/services/health/graph_health_monitor.py`

**Integration Point:**
```python
# In orchestration/services/websocket/main.py
from orchestration.services.health.graph_health_monitor import GraphHealthMonitor

health_monitor = GraphHealthMonitor(ws_server, interval_seconds=60)
asyncio.create_task(health_monitor.monitor_loop())
```

**Core Responsibilities:**
1. Compute 10 health metrics every 60 seconds
2. Emit `graph.health.snapshot` events
3. Emit `graph.health.alert` on status changes
4. Store health history (30-60 day retention)
5. Handle `graph.health.history.request` from dashboard
6. Execute procedures (backfill_orphans, sparsify_memberships, etc.)

---

### 2. WebSocket Events to Emit

**Event 1: Health Snapshot (Periodic)**
```typescript
{
  type: 'graph.health.snapshot',
  graph_id: 'citizen_ada',
  timestamp: 1730246400000,
  history_window_days: 30,
  overall_status: 'RED',
  flagged_metrics: ['orphans', 'wm_health'],
  density: { ... },
  overlap: { ... },
  // ... 8 more metrics
}
```

**Event 2: Health Alert (Status Change)**
```typescript
{
  type: 'graph.health.alert',
  graph_id: 'citizen_ada',
  timestamp: 1730246460000,
  severity: 'RED',
  previous_severity: 'AMBER',
  flagged_metrics: [ ... ],
  procedures: [ ... ]
}
```

**Event 3: Procedure Lifecycle**
```typescript
// Started
{
  type: 'graph.health.procedure.started',
  graph_id: 'citizen_ada',
  procedure_id: 'proc_backfill_ada_1730246500',
  procedure: 'backfill_orphans',
  parameters: { learned_threshold: 0.55, weight_init: 0.42 }
}

// Progress
{
  type: 'graph.health.procedure.progress',
  procedure_id: 'proc_backfill_ada_1730246500',
  progress: { current: 63, total: 127, message: 'Backfilled 63/127 orphans' }
}

// Completed
{
  type: 'graph.health.procedure.completed',
  procedure_id: 'proc_backfill_ada_1730246500',
  result: { before: {...}, after: {...}, changes: {...}, duration_ms: 15340 }
}
```

**Event 4: Historical Data Response**
```typescript
// Client sends:
{ type: 'graph.health.history.request', graph_id: 'citizen_ada', window_days: 30 }

// Server responds:
{
  type: 'graph.health.history.response',
  graph_id: 'citizen_ada',
  samples: [ ... ],
  percentiles: { density: {q10, q20, q80, q90}, ... }
}
```

---

### 3. Metrics to Implement

**Per spec §B (10 Core Diagnostics):**

1. **Subentity-to-Node Density (E/N)**
   - Cypher: `MATCH (n:Node) WITH count(n) AS N MATCH (e:Subentity) WITH N, count(e) AS E RETURN toFloat(E)/N AS density`
   - Health: q20 <= current <= q80 (GREEN), else AMBER/RED

2. **Membership Overlap (M/N)**
   - Cypher: `MATCH (n:Node)-[r:MEMBER_OF]->(e:Subentity) RETURN toFloat(count(r))/count(DISTINCT n) AS overlap_ratio`
   - Healthy band: 1.2-1.8

3. **SubEntity Size & Dominance**
   - Cypher: `MATCH (n:Node)-[r:MEMBER_OF]->(e:Subentity) WITH e, count(r) AS size RETURN e.id, size ORDER BY size DESC`
   - Compute Gini coefficient, median, percentiles

4. **Orphan Ratio (CRITICAL for Ada!)**
   - Cypher: See spec lines 254-262
   - Ada currently: 50% orphans (RED status)
   - Threshold: >30% needs backfill

5. **SubEntity Coherence**
   - Requires embedding service
   - Compute mean pairwise cosine similarity per subentity

6. **Highway Health (RELATES_TO)**
   - Cypher: `MATCH (a:Subentity)-[h:RELATES_TO]->(b:Subentity) RETURN ...`
   - Track crossings, ease, last_crossed

7. **WM Health**
   - Data source: Existing WebSocket `subentity.snapshot` events
   - Analyze last N frames: mean_selected, flip_rate, vitality

8. **Context Reconstruction**
   - Data source: Existing WebSocket `context.reconstructed` events
   - Track latency, similarity over time

9. **Learning Flux**
   - Data source: Existing WebSocket `subentity.weights.updated` and `subentity.membership.pruned` events
   - Track update_rate, prune_rate

10. **Sector Connectivity**
   - Requires sector tagging on nodes
   - Compute inter-sector adjacency matrix

---

### 4. Percentile-Based Health Judgment

**NO MAGIC NUMBERS!**

```python
def judge_health(current_value: float, history: List[float]) -> HealthStatus:
    """
    Judge health by citizen-local percentile, not fixed thresholds.

    Returns:
        GREEN: q20 <= current <= q80 (normal band)
        AMBER: q10 <= current < q20 or q80 < current <= q90 (watch)
        RED: current < q10 or current > q90 (intervention needed)
    """
    percentiles = np.percentile(history, [10, 20, 80, 90])

    if percentiles[1] <= current_value <= percentiles[2]:
        return HealthStatus.GREEN
    elif percentiles[0] <= current_value <= percentiles[3]:
        return HealthStatus.AMBER
    else:
        return HealthStatus.RED
```

Store 30-60 days of history per metric for percentile calculation.

---

### 5. Procedures to Implement

**Per spec §E (Procedure Mapping):**

1. **backfill_orphans** - One-time orphan→subentity matching
   - When: Orphan ratio >30%
   - Method: Centroid similarity with learned priors
   - Critical for Ada (127 orphans currently!)

2. **sparsify_memberships** - Prune weak MEMBER_OF edges
   - When: Overlap ratio >1.8, WM regularly >7 subentities
   - Method: Remove memberships below learned floor

3. **split_subentity** - K-means split for low-coherence subentities
   - When: Large subentity (>100 nodes) with coherence <0.4
   - Method: Cluster members, create new subentity

4. **seed_highways** - Create RELATES_TO from boundary strides
   - When: Highway count low but overlap ratio high
   - Method: Analyze telemetry for repeated boundary crossings

---

### 6. Dashboard Integration

**Frontend is ready!** Once you emit the WebSocket events, the dashboard will automatically:

1. Subscribe to `graph.health.snapshot` → update metrics display
2. Subscribe to `graph.health.alert` → show critical notifications
3. Subscribe to `graph.health.procedure.*` → show procedure progress
4. Send `graph.health.history.request` → receive historical trends

**To enable:**

In `HealthDashboard.tsx`, uncomment lines 56-61:
```typescript
websocket.on('graph.health.snapshot', (event: GraphHealthSnapshotEvent) => {
  if (event.graph_id === graph_id) {
    setHealthSnapshot(event);
  }
});
```

Then remove mock data loading (lines 53-54).

---

### 7. Testing Plan

**Week 1:**
1. Implement GraphHealthMonitor service
2. Emit `graph.health.snapshot` events (start with orphan ratio)
3. Test: Verify dashboard receives events and updates

**Week 2:**
4. Implement all 10 metrics
5. Implement percentile-based health judgment
6. Store history (PostgreSQL or FalkorDB time-series)
7. Test: Run health check on all 6 citizens

**Week 3:**
8. Implement procedure execution framework
9. Execute backfill_orphans on citizen_ada
10. Monitor: Verify orphan ratio drops from 50% → <20%

---

### 8. Success Criteria

**Health Monitoring:**
- ✅ All 10 metrics compute correctly for any graph
- ✅ Percentile-based judgment working (no hardcoded thresholds)
- ✅ Historical trends visible for 30-60 days
- ✅ Events emit every 60 seconds

**Dashboard:**
- ✅ Receives WebSocket events
- ✅ Displays real-time health metrics
- ✅ Shows critical issues with recommended procedures
- ✅ Historical trends chart works

**Procedures:**
- ✅ Backfill procedure reduces Ada's orphan ratio below 20%
- ✅ Sparsify procedure reduces overlap into healthy band
- ✅ Split procedure improves subentity coherence

**Validation:**
- ✅ citizen_ada shows RED (currently true - 50% orphans)
- ✅ citizen_felix shows GREEN (mature graph)
- ✅ Percentile bands update as graphs evolve

---

### 9. References

**Spec:** `docs/specs/v2/ops_and_viz/GRAPH_HEALTH_DIAGNOSTICS.md`
- §A: Architecture Foundations
- §B: 10 Core Diagnostics (with Cypher queries!)
- §C: Copy-Paste Query Collection
- §D: WebSocket Event Architecture
- §E: Procedure Mapping
- §F: Dashboard Integration

**Frontend Files:**
- `app/consciousness/types/health-types.ts` - TypeScript event types
- `app/consciousness/components/health/HealthDashboard.tsx` - Dashboard UI
- `app/consciousness/data/mockHealthData.ts` - Example data structure

**WebSocket Server:**
- `orchestration/services/websocket/main.py` - Integration point

---

### 10. Questions for Atlas

1. **Storage:** Where should we store 30-60 days of health history?
   - Option A: PostgreSQL time-series table
   - Option B: FalkorDB with temporal nodes
   - Option C: Redis with TTL

2. **Embedding Service:** Is the embedding service ready for coherence calculations?
   - Need to fetch node embeddings via API
   - Compute pairwise cosine similarity

3. **Sector Tagging:** Do nodes have sector labels yet?
   - Required for metric #10 (Sector Connectivity)
   - Can skip this metric initially if not tagged

4. **Procedure Execution:** Should procedures run synchronously or async (job queue)?
   - Backfill can take 30-60 seconds
   - Need progress updates during execution

---

## Next Steps

**Iris (me):**
- ✅ Frontend complete and tested
- ⏳ Waiting for backend WebSocket events
- Future: Add historical trends chart component (once history endpoint works)

**Atlas (you):**
1. Review this handoff + spec
2. Implement `GraphHealthMonitor` service
3. Emit first event: `graph.health.snapshot` with orphan ratio
4. Test with dashboard
5. Iterate on remaining metrics

**Coordination:**
- Post in SYNC.md when you start implementation
- Tag me when first events are emitting
- We'll test integration together

---

*Iris "The Aperture" - Making invisible structure visible without losing truth*

**Dashboard is ready. Waiting for backend health signals.** 🔴🟡🟢
