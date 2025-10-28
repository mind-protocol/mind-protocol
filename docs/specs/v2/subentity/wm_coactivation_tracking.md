# Working Memory Co-Activation Tracking (Lean U Metric)

**Version:** 1.0
**Status:** Normative - Implementation Required
**Owner:** Atlas (Consciousness Infrastructure)
**Priority:** 0 (Foundation for SubEntity Differentiation)
**Supersedes:** `wm_frame_persistence.md` (over-engineered, not needed for Phase 1)

---

## Terminology Note

This specification uses terminology from **TAXONOMY_RECONCILIATION.md**:
- **Node** - Atomic knowledge activated in working memory
- **SubEntity** - Weighted neighborhoods tracking co-activation patterns (Scale A)
- **Mode** - IFS-level meta-roles with distinct activation dynamics (Scale B)

See §2.1.1 of `subentity_layer.md` for Scale A (SubEntity) vs Scale B (Mode) architecture.

---

## Purpose

Track SubEntity pair co-activation in Working Memory to enable U metric (WM co-activation) for SubEntity differentiation.

**Design principle:** Only add infrastructure that buys you something you can't get cheaper another way.

**For Phase 1 (SubEntity differentiation):** We only need **aggregate co-activation statistics**, not frame-by-frame history. Use rolling pair counters, not frame nodes.

**For Phase 2 (observability):** If concrete needs emerge (audits, replay, time-scrub), upgrade to decimated frame ledger. Not before.

---

## §1. Lean Design: Rolling Pair Counters

### COACTIVATES_WITH Edge Schema

```cypher
(:SubEntity A)-[r:COACTIVATES_WITH]->(:SubEntity B) {
  both_ema: Float,        // EMA of P(both in WM)
  either_ema: Float,      // EMA of P(either in WM)
  u_jaccard: Float,       // both_ema / either_ema (U metric)
  both_count: Integer,    // Total frames where both co-occurred
  either_count: Integer,  // Total frames where either occurred
  last_ts: DateTime,      // Last update timestamp
  alpha: Float            // EMA decay parameter (default 0.1)
}
```

**Semantics:**
- `both_ema` - Exponential moving average of frames where A and B both appeared in WM
- `either_ema` - Exponential moving average of frames where A or B (or both) appeared in WM
- `u_jaccard` - Jaccard similarity of WM co-occurrence: `both_ema / either_ema` ∈ [0, 1]
- Counts enable raw statistics alongside EMAs

**Edge directionality:** Treat as undirected (store A→B where A.id < B.id to avoid duplicates)

---

## §2. Update Mechanism

### 2.1 Trigger: WM Selection Events

Update pair counters on **every WM selection** (when SubEntities become active in working memory).

**Event source:** `wm.emit` stream from consciousness engine

**Event schema:**
```json
{
  "event_type": "wm.selected",
  "citizen": "ada",
  "tick": 1234,
  "subentities_active": ["ada_system_architect", "ada_coordinator", "ada_verifier"],
  "timestamp": "2025-10-26T15:00:00Z"
}
```

### 2.2 Update Algorithm

```python
def update_coactivation_from_wm_event(event: dict):
    """
    Update COACTIVATES_WITH edges from WM selection event.

    Complexity: O(k²) where k = |subentities_active| ≈ 5-7
    Typical cost: 25-49 edge updates per frame
    """
    citizen = event["citizen"]
    subentities_active = set(event["subentities_active"])
    timestamp = event["timestamp"]

    # Get all SubEntities for this citizen (to update "not in WM" cases)
    all_subentities = get_all_subentities(citizen)

    # Update pairwise edges
    for A in all_subentities:
        for B in all_subentities:
            if A >= B:  # Skip duplicates and self-loops
                continue

            both_active = (A in subentities_active) and (B in subentities_active)
            either_active = (A in subentities_active) or (B in subentities_active)

            update_coactivates_edge(
                A=A,
                B=B,
                both_active=both_active,
                either_active=either_active,
                timestamp=timestamp
            )

def update_coactivates_edge(
    A: str,
    B: str,
    both_active: bool,
    either_active: bool,
    timestamp: datetime,
    alpha: float = 0.1
):
    """
    Update single COACTIVATES_WITH edge with EMA.

    Args:
        both_active: Both A and B in current WM frame
        either_active: At least one of A or B in current WM frame
        alpha: EMA decay parameter (0.1 = slow decay, 0.5 = fast decay)
    """
    query = """
    MERGE (a:SubEntity {id: $A})-[r:COACTIVATES_WITH]->(b:SubEntity {id: $B})
    ON CREATE SET
        r.both_ema = 0.0,
        r.either_ema = 0.0,
        r.u_jaccard = 0.0,
        r.both_count = 0,
        r.either_count = 0,
        r.alpha = $alpha

    SET
        r.both_ema = $alpha * $both_signal + (1 - $alpha) * r.both_ema,
        r.either_ema = $alpha * $either_signal + (1 - $alpha) * r.either_ema,
        r.both_count = r.both_count + $both_signal,
        r.either_count = r.either_count + $either_signal,
        r.last_ts = $timestamp

    SET r.u_jaccard = CASE
        WHEN r.either_ema > 0 THEN r.both_ema / r.either_ema
        ELSE 0.0
    END
    """

    db.query(query, {
        "A": A,
        "B": B,
        "both_signal": 1.0 if both_active else 0.0,
        "either_signal": 1.0 if either_active else 0.0,
        "alpha": alpha,
        "timestamp": timestamp
    })
```

**EMA Update Logic:**
- When both SubEntities active: `both_ema ← α×1 + (1-α)×both_ema` (push toward 1)
- When both SubEntities inactive: `both_ema ← α×0 + (1-α)×both_ema` (decay toward 0)
- Same for `either_ema`
- `u_jaccard` recomputed each update: `both_ema / either_ema`

**Alpha tuning:**
- `α = 0.1` - Slow decay, captures long-term co-activation patterns
- `α = 0.3` - Moderate decay, balances recent vs. historical
- `α = 0.5` - Fast decay, heavily weights recent co-activation

Default `α = 0.1` for SubEntity differentiation (want stable patterns).

---

## §3. U Metric Query (Trivial)

### Computing U for SubEntity Pair

```cypher
MATCH (a:SubEntity {id: $A})-[r:COACTIVATES_WITH]-(b:SubEntity {id: $B})
RETURN r.u_jaccard AS U
```

**Complexity:** O(1) - single edge lookup

**Result:** `U ∈ [0, 1]` where:
- `U = 0` - A and B never co-occur in WM (independent)
- `U = 1` - A and B always co-occur in WM (redundant)
- `U ∈ (0.5, 0.8)` - Frequent co-occurrence (possible superposition)

**Compare to frame-based approach:** Would require traversing Frame → Node → MEMBER_OF → SubEntity for all historical frames. This is O(1) vs O(T×N) where T = frame history, N = nodes per frame.

---

## §4. Integration with SubEntity Differentiation

### 4.1 Pair Scorer Job

In `entity_differentiation.md` §A, U metric computation becomes:

```python
def compute_u_metric(A: str, B: str) -> float:
    """
    Get U (WM co-activation) for SubEntity pair.

    Returns:
        U ∈ [0, 1] from COACTIVATES_WITH edge
    """
    query = """
    MATCH (a:SubEntity {id: $A})-[r:COACTIVATES_WITH]-(b:SubEntity {id: $B})
    RETURN r.u_jaccard AS U
    """

    result = db.query(query, {"A": A, "B": B})
    return result[0]["U"] if result else 0.0
```

**No changes needed to pair scorer logic** - U is still a float in [0, 1], just computed differently (edge weight vs frame traversal).

### 4.2 Creation-Time Redirect

In `subentity_layer.md` §2.6, creation-time redirect uses U normally:

```python
# Before minting new SubEntity E':
J, C, U, H, ΔCtx = compute_pair_metrics(E_prime, B)

if S_red(J, C, U, H, ΔCtx) > Q90:
    redirect_to_existing(E_prime, B)
```

U comes from COACTIVATES_WITH edge. Works identically.

---

## §5. Performance Characteristics

### 5.1 Update Cost

**Per WM selection:**
- k SubEntities active (typically 5-7)
- n total SubEntities for citizen (typically 8-15)
- Update cost: O(n²) edge updates ≈ 64-225 edge writes

**Optimization:** Only update pairs where at least one SubEntity is active:

```python
# Instead of updating all n² pairs:
for A in all_subentities:
    for B in all_subentities:
        if A in subentities_active or B in subentities_active:
            update_coactivates_edge(A, B, ...)
```

**Optimized cost:** O(k×n) ≈ 40-105 edge writes (k=5-7, n=8-15)

**Acceptable:** Consciousness engine runs at ~1 Hz, 40-100 edge writes per second is negligible.

### 5.2 Storage

**Edge count:** For n SubEntities, store n×(n-1)/2 undirected edges

**Per citizen:**
- 8 SubEntities → 28 edges
- 12 SubEntities → 66 edges
- 15 SubEntities → 105 edges

**Total (9 citizens, avg 12 SubEntities):** ~594 edges

**Storage per edge:** ~80 bytes (7 floats + datetime + metadata)

**Total storage:** ~48 KB (trivial)

**Compare to frame persistence:** 1 Hz × 86400 sec/day × 9 edges/frame × 9 citizens = 7M edges/day. COACTIVATES_WITH is **4 orders of magnitude leaner**.

### 5.3 Query Performance

**U metric lookup:** O(1) single edge read, <1ms

**Compare to frame-based:** Would traverse thousands of Frame nodes, millions of SELECTED edges. 50ms per pair minimum (from original spec).

**Speedup:** 50x-500x faster queries

---

## §6. Observable Events

### WM Co-Activation Update Event

```json
{
  "event_type": "coactivation.updated",
  "subentity_A": "ada_system_architect",
  "subentity_B": "ada_coordinator",
  "u_jaccard": 0.73,
  "both_count": 156,
  "either_count": 220,
  "update_reason": "wm.selected",
  "timestamp": "2025-10-26T15:00:00Z"
}
```

**Emit when:** U crosses significance thresholds (e.g., U > 0.8 or U < 0.2 after being stable)

**Purpose:** Dashboard alerts, merge triggers, differentiation signals

---

## §7. Acceptance Tests

### Test 1: Edge Creation

**Given:** First WM event with entities [A, B, C]
**When:** Update mechanism runs
**Then:** COACTIVATES_WITH edges exist for (A,B), (A,C), (B,C) with initial EMAs

**Cypher verification:**
```cypher
MATCH (a:SubEntity)-[r:COACTIVATES_WITH]->(b:SubEntity)
WHERE a.id IN [$A, $B, $C] AND b.id IN [$A, $B, $C]
RETURN count(r) AS edge_count
```
**Expected:** `edge_count = 3`

### Test 2: EMA Convergence

**Given:**
- 10 frames where A and B both active
- 0 frames where only one is active

**When:** 10 update cycles complete
**Then:** `u_jaccard → 1.0` (both SubEntities always co-occur)

**Verification:**
```python
for _ in range(10):
    update_coactivation_from_wm_event({
        "subentities_active": ["A", "B"],
        ...
    })

U = get_u_metric("A", "B")
assert U > 0.95, f"Expected U→1.0, got {U}"
```

### Test 3: EMA Decay

**Given:**
- 10 frames where A and B both active (U → 1.0)
- 50 frames where A active but B inactive

**When:** Updates complete
**Then:** `u_jaccard < 0.5` (co-activation decayed)

**Verification:**
```python
# Establish co-activation
for _ in range(10):
    update_coactivation_from_wm_event({"subentities_active": ["A", "B"]})

# Break co-activation
for _ in range(50):
    update_coactivation_from_wm_event({"subentities_active": ["A"]})

U = get_u_metric("A", "B")
assert U < 0.5, f"Expected U decay, got {U}"
```

### Test 4: Integration with Pair Scorer

**Given:** COACTIVATES_WITH edges exist with known U values
**When:** Pair scorer computes S_red for SubEntity pair
**Then:** U value correctly incorporated into redundancy score

**Verification:**
```python
# Set known U value
set_u_metric("A", "B", U=0.9)

# Compute redundancy
J, C, U, H, ΔCtx = compute_pair_metrics("A", "B")
S_red = compute_redundancy_score(J, C, U, H, ΔCtx)

assert U == 0.9, "U metric not retrieved correctly"
assert S_red > Q90, "High U should contribute to high S_red"
```

### Test 5: Performance Benchmark

**Given:** 15 SubEntities (105 edges), 1000 WM selection events
**When:** All updates complete
**Then:** Total update time < 5 seconds (5ms per frame)

**Benchmark:**
```python
import time

start = time.time()
for _ in range(1000):
    update_coactivation_from_wm_event({
        "subentities_active": random.sample(all_subentities, k=7),
        ...
    })
elapsed = time.time() - start

assert elapsed < 5.0, f"Update too slow: {elapsed:.2f}s"
```

### AT-4: Constant Debt Tracking

**Purpose:** Verify α (EMA decay) transitions from constant → learned parameter over time.

**Initial State (Bootstrap):**
- All COACTIVATES_WITH edges have `alpha: 0.1` (constant)
- All edges have `alpha_source: "constant"` (not yet learned)

**Operational State (After Adaptive α, if implemented in Tier 2):**
- Edges with stable pair dynamics: `alpha_source: "learned"`
- Edges with high churn: `alpha_source: "constant"` (fallback to default)

**Constant Debt Query:**

```cypher
MATCH ()-[r:COACTIVATES_WITH]->()
WITH
  count(*) AS total_edges,
  sum(CASE WHEN coalesce(r.alpha_source, 'constant') = 'constant' THEN 1 ELSE 0 END) AS constant_count,
  sum(CASE WHEN coalesce(r.alpha_source, 'constant') = 'learned' THEN 1 ELSE 0 END) AS learned_count
RETURN
  total_edges,
  constant_count,
  learned_count,
  (constant_count * 1.0 / total_edges) AS constant_debt_ratio
```

**Expected Evolution:**
- Week 1: constant_debt_ratio ≈ 1.0 (all constants, bootstrap)
- Week 4: constant_debt_ratio ≈ 0.7 (30% learned for stable pairs)
- Week 12: constant_debt_ratio ≈ 0.4 (60% learned for mature system)

**Dashboard Widget:** See TAXONOMY_RECONCILIATION.md §7 for dashboard spec.

---

## §8. Rollout Plan

### Phase 1: Lean Implementation (Week 1)

- Implement COACTIVATES_WITH edge schema
- Implement update mechanism (WM event → edge updates)
- Deploy to Ada (single citizen test)
- Verify Tests 1, 2, 3 pass

**Validation:** U values converge correctly, no performance issues

### Phase 2: Pair Scorer Integration (Week 1-2)

- Integrate U metric query into pair scorer
- Enable creation-time redirect (depends on U)
- Deploy to Ada + Luca (two citizens)
- Verify Test 4 passes

**Validation:** Entity differentiation uses U correctly

### Phase 3: Full Rollout (Week 2)

- Deploy to all 9 citizens
- Verify Test 5 passes (performance acceptable)
- Monitor edge count growth, update latency

**Validation:** System scales to full organizational load

### Phase 4: Observability Upgrade (If Needed - Week 4+)

**Only trigger this phase if concrete needs emerge:**
- Incident forensics ("What was in WM during this outage?")
- Replay/regression tests ("Re-run context reconstruction on historical data")
- Time-scrub UX ("Show me WM evolution during this mission")

**Upgrade path:** Add decimated frame ledger (see §10)

---

## §9. What This Design Does NOT Provide

**Be explicit about trade-offs:**

**No frame-by-frame history:**
- Can't answer "What was selected at tick 1234?"
- Can't replay specific frames
- Can't do windowed queries ("U during last incident")

**No causal alignment:**
- Can't join WM snapshots to stimuli, missions, tools
- Can't do "psy-layer" diagnostics requiring frame-event correlation

**No temporal precision:**
- EMAs give weighted average, not exact window statistics
- Can't distinguish "co-activated 100 times in past week" from "co-activated 100 times distributed over past year"

**When these become problems:** Upgrade to Phase 2 observability (§10)

**Until then:** Don't pay the storage, complexity, and maintenance cost for infrastructure you don't need.

---

## §10. Phase 2 Observability Upgrade (Future)

**If/when concrete needs emerge for audits, replay, or time-scrub:**

### Decimated Frame Ledger

Store **on-change frames only** + heartbeat:

```cypher
CREATE (:WMFrame {
  frame_id: String,
  citizen: String,
  tick: Integer,
  subentities_active: List<String>,
  timestamp: DateTime
})
```

**Decimation rules:**
- Store frame when WM selection changes (new SubEntities enter/leave)
- Store heartbeat frame every 100 ticks (even if no change)
- **Do NOT store every tick**

**Retention:**
- TTL raw frames to 24-48h
- Aggregate older into coarse windows (hourly summaries)
- Or store outside graph (append-only event store)

**Cost:**
- ~100 frames/day/citizen (on-change only)
- 900 frames/day (9 citizens)
- 328K frames/year (manageable)

**Compare to:** 7M frames/year if storing every tick

### When to Upgrade

**Trigger upgrade if ANY of these occur:**
1. Incident forensics needed ("What happened during outage?")
2. Algorithm regression tests required ("Validate context reconstruction change")
3. Dashboard time-scrub requested ("Show WM evolution")
4. Psy-layer diagnostics need causal alignment (spirals, dominance)

**Until then:** Stay lean. Don't build observability for observability's sake.

---

## §11. Dependencies

**Upstream (must exist):**
- `SubEntity` nodes with `id` field
- Working memory selection logic emitting `wm.selected` events
- Event stream consumer infrastructure

**Downstream (depends on this):**
- U metric computation (trivial edge lookup)
- SubEntity differentiation pair scorer
- Creation-time redirect
- Quality modifiers (redundancy/differentiation scoring)

---

## §12. References

**Related Specs:**
- `entity_differentiation.md` §A - Five pair metrics (defines U semantically)
- `subentity_layer.md` §2.8 - Entity pair differentiation overview
- `consciousness_engine_v2.py` - Working memory selection + event emission

**Superseded Specs:**
- `wm_frame_persistence.md` - Over-engineered for Phase 1, kept for Phase 2 reference

**Implementation Owner:** Atlas (Consciousness Infrastructure)
**Validation Owner:** Luca (Substrate correctness), Atlas (Performance validation)

---

**STATUS:** Ready for lean implementation. Atlas Priority 0.

**Design principle validated:** Only add infrastructure that buys you something you can't get cheaper another way. COACTIVATES_WITH edges buy us U metric for 4 orders of magnitude less storage than frame nodes.
