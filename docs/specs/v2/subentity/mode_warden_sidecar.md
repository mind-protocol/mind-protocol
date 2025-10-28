# Mode Warden Sidecar Specification

**Created:** 2025-10-26
**Status:** Normative (supersedes daily batch approach)
**Depends on:** emergent_ifs_modes.md, TIER2_REDLINES (Amendments 1,2,3,6)

---

## Purpose

**The mode_warden is a reactive sidecar that detects Mode emergence incrementally by subscribing to co-activation updates and running incremental community detection when learned change-points fire.**

This supersedes the daily batch job approach with an event-driven, substrate-native system that feels emergent rather than scheduled.

---

## Why Not Daily Batch?

**Problems with scheduled detection:**
1. **Latency:** Learn co-activation all day, mint modes tomorrow
2. **Arbitrary constants:** "once/day" violates zero-constant architecture
3. **Cost locality:** Recomputes communities even when nothing changed
4. **Phenomenology:** Scheduled batches feel mechanical, not emergent

**The reactive solution:**
- Modes crystallize **when substrate changes enough** (learned contours)
- Detection feels **continuous** (seconds, not days)
- Cost **proportional to change** (only recompute affected neighborhoods)
- Architecture is **substrate-native** (reacts to events, no schedules)

---

## Architecture

### Sidecar Pattern

**mode_warden** runs as lightweight sidecar process:
- **Not inside engine loop** (keeps hot path lean, preserves determinism)
- **Same process group** as ws/db adapters (low-latency event delivery)
- **Subscribes to substrate events** (coactivation.updated, wm.selected)
- **Emits mode lifecycle events** (mode.seeded, mode.matured, mode.dissolved)

### Data Flow

```
Consciousness Engine (hot path)
  ↓ emits wm.selected
SubEntity co-activation tracking (TIER2 Amendment 2)
  ↓ emits coactivation.updated
mode_warden sidecar (THIS SPEC)
  ↓ maintains cached role graph
  ↓ detects change-points (learned contours)
  ↓ runs incremental community detection
  ↓ reconciles modes (seed/mature/dissolve/merge)
  ↓ updates AFFILIATES_WITH edges
  ↓ emits mode.* events
WebSocket server broadcasts to dashboard
```

---

## Reactive Triggers (No Constants)

**Run incremental detection when ANY is true:**

### 1. Edge Drift
```python
ΔU(A,B) > percentile(edge_drift_contour, 85)  # Learned per citizen
```
When co-activation utility change exceeds learned contour.

### 2. Modularity Drop
```python
Q_current < Q_baseline * (1 - learned_margin)  # Learned margin ~0.05
```
When partition modularity degrades beyond learned tolerance.

### 3. Persistence Shift
```python
NMI(short, long) < percentile(persistence_contour, 30)  # Learned per citizen
```
When short/long window NMI diverges (frog-boiling detection).

**All contours learned from historical distributions.** Zero constants.

---

## Algorithm: Incremental Mode Detection

### Input Events

**From:** SubEntity co-activation tracking
**Event:** `coactivation.updated`
**Payload:**
```python
{
  "citizen_id": "luca",
  "edges_changed": [
    {"A": "subentity_translator", "B": "subentity_architect", "U_new": 0.73},
    ...
  ],
  "timestamp": "2025-10-26T12:34:56Z"
}
```

### Step 0: Update Cached Role Graph

```python
def on_coactivation_update(edges_changed):
    """
    Update role graph weights for changed edges.
    Graph cached in memory for low-latency queries.
    """
    for (A, B, U_new) in edges_changed:
        # Fuse multiple signals (log-domain RRF, learned θ)
        W[A,B] = fuse(
            U_new,                              # Co-activation utility
            ease(A, B),                         # RELATES_TO.ease
            affect_similarity(A, B),            # Emotion vector cosine
            procedural_overlap(A, B)            # Tool usage Jaccard
        )

        # Track drift for change-point detection
        drift[A,B] = abs(W[A,B] - W_prev[A,B])
```

**Complexity:** O(k) where k = edges changed (typically <10)

### Step 1: Detect Change-Point

```python
def should_recompute(edges_changed):
    """
    Check if any trigger threshold crossed.
    """
    # Trigger 1: Edge drift
    max_drift = max(drift[e] for e in edges_changed)
    if max_drift > learned_contour("edge_drift", 85):
        return True

    # Trigger 2: Modularity drop
    Q_current = modularity(cached_communities, W)
    if Q_current < Q_baseline * (1 - learned_margin):
        return True

    # Trigger 3: Persistence shift
    nmi = NMI(communities_short, communities_long)
    if nmi < learned_contour("persistence", 30):
        return True

    return False  # No recomputation needed
```

**Typical behavior:** 95% of updates return False (no-op).

### Step 2: Incremental Community Detection

```python
def incremental_community_detection(edges_changed):
    """
    Recompute communities only for affected neighborhoods.
    Uses dynamic label propagation or incremental Louvain.
    """
    # Identify affected neighborhood (radius=2 from changed edges)
    affected_nodes = set()
    for (A, B, _) in edges_changed:
        affected_nodes |= neighborhood(A, radius=2)
        affected_nodes |= neighborhood(B, radius=2)

    # Seed with previous labels (preserve stable communities)
    seed_labels = {n: prev_label[n] for n in affected_nodes}

    # Run incremental Louvain
    communities = incremental_louvain(
        W,                          # Role graph (updated weights)
        nodes=affected_nodes,       # Only recompute these
        seed_labels=seed_labels,    # Start from previous
        max_iterations=10           # Fast convergence
    )

    # Merge with unchanged communities
    return merge_communities(communities, prev_communities)
```

**Complexity:** O(k·d²·log(d)) where k=edges changed, d=neighborhood diameter
**Typical:** d~20, k~5 → milliseconds, not seconds

### Step 3: Mode Reconciliation

```python
def reconcile_modes(communities_new, communities_prev):
    """
    Determine which modes to seed/mature/dissolve/merge.
    All decisions via learned percentile contours.
    """
    for C in communities_new:
        # Compute mode quality (cohesion, boundary, affect, procedural)
        Q_mode = mode_quality(C)

        # Update persistence tracking (two-timescale EMA)
        update_persistence(C, Q_mode)
        persistence = get_persistence(C)

        # Decision gates (learned contours)
        seed_contour = learned_contour("mode_quality_seed", 70)
        mature_contour = learned_contour("mode_persistence", 75)
        dissolve_contour = learned_contour("mode_quality_min", 30)

        if C not in prev_communities:
            # NEW community detected
            if Q_mode > seed_contour and persistence_rising(C):
                seed_mode(C, Q_mode)
                emit_event("mode.seeded", C)

        elif Q_mode > mature_contour and persistence > mature_contour:
            # MATURE existing mode
            if not is_mature(C):
                mature_mode(C, Q_mode, persistence)
                emit_event("mode.matured", C)

        elif Q_mode < dissolve_contour or persistence < dissolve_contour:
            # DISSOLVE degraded mode
            dissolve_mode(C)
            emit_event("mode.dissolved", C)

        else:
            # UPDATE existing mode (signature, affiliations)
            update_mode_signature(C, Q_mode)
            update_affiliations(C)
            emit_event("mode.affiliation.updated", C)

    # Check for mode merges (redundancy detection)
    check_mode_redundancy()  # Uses S_red/S_use from entity_differentiation
```

---

## Mode Quality Formula

**Q_mode** = weighted blend of four components:

### 1. Internal Cohesion
```python
cohesion = mean(W[i,j] for i,j in community_edges(C))
```
Average edge weight within community.

### 2. Boundary Sharpness
```python
boundary = 1 - (mean(W[i,j]) for i∈C, j∉C)
```
Low weight to external nodes.

### 3. Affective Consistency
```python
affect_consistency = 1 - std(emotion_vectors(C))
```
Low variance in emotion vectors across members.

### 4. Procedural Coherence
```python
procedural = jaccard(tools_used(C))
```
High tool overlap across members.

**Fusion:** Log-domain RRF with learned θ (TIER2 Amendment 5).

---

## Persistence Tracking

**Two-timescale EMA** (TIER2 Amendment 6):

```python
# Short window (current state)
persistence_short = EMA(NMI(C_t, C_{t-1}), alpha_fast=0.3)

# Long window (baseline)
persistence_long = EMA(NMI(C_t, C_{t-10}), alpha_slow=0.05)

# Divergence signals gradual drift
persistence_divergence = abs(persistence_short - persistence_long)
```

**Rising:** persistence_short increasing
**Stable:** persistence_short ≈ persistence_long
**Degrading:** persistence_short < persistence_long - margin

---

## Mode Redundancy Detection

**Reuse entity differentiation metrics** (S_use, S_red) for modes:

```python
def check_mode_redundancy():
    """
    Detect redundant mode pairs and merge if S_red is high.
    """
    for (M1, M2) in mode_pairs:
        # Apply 5 metrics from entity_differentiation.md
        J = jaccard_overlap(M1.members, M2.members)
        C = coactivation_correlation(M1, M2)
        U = utility_complementarity(M1, M2)
        H = harmfulness_divergence(M1, M2)
        ΔCtx = context_differentiation(M1, M2)

        # Compute S_use and S_red
        S_use = learned_classifier(J, C, U, H, ΔCtx, label="complementary")
        S_red = learned_classifier(J, C, U, H, ΔCtx, label="redundant")

        if S_red > learned_contour("mode_merge_threshold", 75):
            merge_modes(M1, M2)
            emit_event("mode.merged", {"from": [M1, M2], "to": merged})
```

---

## Integration with TIER2 Amendments

### Amendment 1: Presence EMAs
**Enables:** Fast SubEntity activation queries for community detection
**Without:** Would need O(n) queries, making reactive detection too slow

### Amendment 2: Lazy Edge Materialization
**Enables:** COACTIVATES_WITH edges created on-demand with TTL
**Without:** Expensive to maintain all co-activation edges pre-emptively

### Amendment 3: Hysteresis
**Enables:** Mode seed/dissolve contours prevent flicker from noise
**Without:** Short spikes would cause mode thrash

### Amendment 6: Two-Timescale Stability
**Enables:** Persistence tracking via short/long NMI windows
**Without:** Gradual mode degradation undetected (frog-boiling)

**mode_warden requires TIER2 Amendments 1,2,3,6 to function correctly.**

---

## Events Emitted

### mode.seeded
```python
{
  "event": "mode.seeded",
  "citizen_id": "luca",
  "mode_id": "mode_translator_architect",
  "signature": {
    "name": "Translator-Architect Coalition",
    "affect_centroid": [0.7, 0.2, ...],
    "procedural_tools": ["Edit", "Write", "Read"],
    "member_count": 3
  },
  "quality": 0.78,
  "timestamp": "2025-10-26T12:35:02Z"
}
```

### mode.matured
```python
{
  "event": "mode.matured",
  "citizen_id": "luca",
  "mode_id": "mode_translator_architect",
  "persistence": 0.85,
  "timestamp": "2025-10-26T13:10:15Z"
}
```

### mode.dissolved
```python
{
  "event": "mode.dissolved",
  "citizen_id": "luca",
  "mode_id": "mode_old_pattern",
  "reason": "quality_below_threshold",
  "final_quality": 0.12,
  "timestamp": "2025-10-26T14:22:30Z"
}
```

### mode.affiliation.updated
```python
{
  "event": "mode.affiliation.updated",
  "citizen_id": "luca",
  "mode_id": "mode_translator_architect",
  "affiliations_changed": [
    {"subentity": "subentity_validator", "weight": 0.65, "stability": 0.82}
  ],
  "timestamp": "2025-10-26T12:36:45Z"
}
```

---

## Acceptance Tests

### Test 1: No-ops When Quiet
**Given:** Steady co-activation (no edge changes)
**When:** 1000 ticks pass
**Then:** mode_warden stays idle, zero community recomputes

### Test 2: Fast Reaction to Drift
**Given:** Spike 5 U(A,B) edges beyond contour
**When:** coactivation.updated event received
**Then:** mode.seeded event emitted within 2 seconds

### Test 3: Stability via Hysteresis
**Given:** Short spike in U, then return to baseline
**When:** Persistence not yet rising
**Then:** No mode seeded (hysteresis prevents thrash)

### Test 4: Cost Proportional to Change
**Given:** 5 edges changed out of 20,000 total
**When:** Incremental detection runs
**Then:** Recomputation time <10ms (only affected neighborhood)

### Test 5: Mode Merge Detection
**Given:** Two modes with S_red > 0.75
**When:** Redundancy check runs
**Then:** mode.merged event emitted, AFFILIATES_WITH updated

---

## Deployment

### Process Group
```yaml
# services.yaml (MPSv3)
mode_warden:
  cmd: python orchestration/mechanisms/mode_warden.py --citizen {citizen_id}
  requires: [falkordb, ws_api]
  restart:
    policy: always
    backoff: exponential
  readiness:
    type: tcp
    port: 8003
  liveness:
    type: script
    script: python orchestration/scripts/health_check_mode_warden.py
  watch:
    - orchestration/mechanisms/mode_warden.py
    - orchestration/mechanisms/incremental_louvain.py
```

### Configuration
```python
# orchestration/config/mode_warden.yml
citizen_id: luca
detection:
  edge_drift_percentile: 85      # Learned contour
  modularity_margin: 0.05        # Learned
  persistence_percentile: 30     # Learned
  neighborhood_radius: 2         # Fixed (graph topology constraint)
  max_iterations: 10             # Convergence speed vs accuracy
community:
  algorithm: incremental_louvain # Or dynamic_label_propagation
  seed_quality_percentile: 70    # Learned
  mature_persistence_percentile: 75  # Learned
  dissolve_quality_percentile: 30    # Learned
telemetry:
  emit_events: true
  log_level: INFO
```

---

## Performance Characteristics

**Latency:**
- Idle state: 0 CPU
- Change-point detection: <1ms
- Incremental community detection: 5-50ms (depends on neighborhood size)
- Event emission: <1ms

**Memory:**
- Cached role graph: ~10KB per citizen (200-500 SubEntities, sparse)
- Community labels: ~5KB per citizen
- Persistence tracking: ~2KB per citizen

**Scalability:**
- Linear in number of citizens (independent sidecars)
- Sub-linear in SubEntity count (incremental updates only affect local neighborhoods)

---

## Hybrid Approach (Optional)

**If weekly batch still desired for operational hygiene:**

### Weekly Compactness Sweep
```python
# Runs once per week (Sunday 3am UTC)
def weekly_hygiene():
    """
    Merge dust, re-normalize θ, prune unused modes.
    This is operational cleanup, not emergence cadence.
    """
    merge_dust_modes()           # S_red > 0.9 for modes with <3 members
    renormalize_blend_params()   # Re-fit θ from week's data
    prune_unused_modes()         # No activations in 30 days
    emit_event("mode.hygiene.complete")
```

**Why weekly?** Operational hygiene, not physics. The reactive sidecar handles emergence.

---

## Migration from Daily Batch

**Phase 1:** Deploy mode_warden alongside daily batch (parallel)
**Phase 2:** Compare results for 1 week (expect 95% agreement)
**Phase 3:** Disable daily batch, rely on mode_warden
**Phase 4:** Remove batch job code entirely

**Rollback:** Re-enable daily batch if mode_warden bugs detected.

---

## Status

**Normative:** This spec supersedes daily batch approach
**Depends on:** TIER2_REDLINES Amendments 1,2,3,6
**Implementation priority:** After Tier 1 guards, before Tier 2 robustness
**Timeline:** 2-3 weeks implementation + 1 week validation

---

## References

- `emergent_ifs_modes.md` - Mode (Scale B) architecture
- `TIER2_REDLINES_2025-10-26.md` - Amendments 1,2,3,6
- `entity_differentiation.md` - S_use/S_red metrics for mode redundancy
- `wm_coactivation_tracking.md` - COACTIVATES_WITH edge creation
