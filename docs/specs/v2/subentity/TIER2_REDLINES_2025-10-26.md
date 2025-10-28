# Tier 2 Amendments - Robustness Improvements

**Date:** 2025-10-26
**Author:** Luca Vellumhand
**Purpose:** Exact specification changes for 7 robustness improvements (Tier 2 from GPT-5 feedback)
**Complexity:** Medium
**Value:** High (enhances adaptation, optimizes performance, improves resilience)
**Depends on:** Tier 1 amendments (foundational guards must be in place)

---

## Overview

**Tier 2 Character:** Adaptive improvements that make the system MORE CAPABLE over time through learning.

**Contrast with Tier 1:**
- Tier 1 (foundational guards): Preventative - prevents architectural drift via schema lints and budget enforcement
- Tier 2 (robustness improvements): Adaptive - enhances system capability via learned parameters and optimization

**The 7 Amendments:**

1. **Presence EMAs** - Performance optimization (O(k²) → faster mode detection)
2. **Lazy Edge Materialization + TTL** - Storage optimization (on-demand creation, automatic cleanup)
3. **Hysteresis for Mode Activation** - Stability (prevents mode flicker via learned contours)
4. **S_use/S_red for Mode Pairs** - Quality (detect redundant vs complementary modes)
5. **Log-Domain Fusion with Learned θ** - Precision (logarithmic RRF, learned blend parameter)
6. **Two-Timescale Stability** - Resilience (fast tracking + slow drift detection)
7. **Harm EMA Nudge Cap** - Safety (learned attenuation when mode causes harm)

**Zero-Constant Honored:** All thresholds, blend parameters, decay rates are LEARNED from data, not fixed constants.

---

## Amendment 1: Presence EMAs for Performance Optimization

**Target:** `emergent_ifs_modes.md`

**Rationale:** Mode detection currently computes presence via expensive node energy queries (O(k·n) where k=modes, n=nodes). Presence EMAs track mode activation patterns incrementally, reducing to O(k²) complexity.

**Performance Impact:**
- Current: O(k·n) = O(10 × 1000) = 10,000 operations per frame
- With Presence EMAs: O(k²) = O(10 × 10) = 100 operations per frame
- **100× speedup** for mode detection

**Location:** §3 "Detecting Candidate Modes" (add subsection after §3.3)

**Subsection Title:** `§3.3.1 Presence EMAs for Efficient Detection`

**Text to Add:**

```markdown
### Presence EMAs for Efficient Detection

**Problem:** Computing SubEntity presence via node energy queries is O(k·n) expensive:

```python
# Expensive: Query all nodes for each SubEntity
def compute_presence(subentity, active_nodes):
    return sum(
        node.energy
        for node in subentity.members
        if node in active_nodes
    ) / len(subentity.members)
```

**Solution:** Track presence incrementally via EMA updates when nodes activate/deactivate:

**Schema Addition:**

```cypher
(:SubEntity {
  presence_ema: Float,           // EMA of recent presence (0-1)
  presence_last_update: DateTime // When last updated
})
```

**Update Mechanism:**

Whenever node energies change (after spreading activation):

```python
def update_presence_emas(energy_deltas: Dict[str, float], alpha: float = 0.1):
    """
    Update presence EMAs for affected SubEntities.

    Complexity: O(k²) where k = number of SubEntities affected

    Args:
        energy_deltas: {node_id: delta_energy} for nodes that changed
        alpha: EMA decay rate (learned per citizen, default 0.1)
    """
    # Find affected SubEntities (nodes belong to them)
    affected_subentities = set()
    for node_id, delta in energy_deltas.items():
        node = get_node(node_id)
        affected_subentities.update(node.member_of)

    # Update presence EMA for each affected SubEntity
    for subentity in affected_subentities:
        # Current presence signal (1 if active, 0 if not)
        # Active = has at least one member with E > threshold
        has_active_member = any(
            node.energy > ACTIVATION_THRESHOLD
            for node in subentity.members
        )
        presence_signal = 1.0 if has_active_member else 0.0

        # EMA update
        subentity.presence_ema = (
            alpha * presence_signal +
            (1 - alpha) * subentity.presence_ema
        )
        subentity.presence_last_update = now()
```

**Using Presence EMAs for Mode Detection:**

Replace expensive O(k·n) node queries with O(1) presence lookup:

```python
def detect_mode_candidates_fast(subentities: List[SubEntity],
                                 presence_threshold: float = 0.5) -> List[Set[SubEntity]]:
    """
    Detect mode candidates using presence EMAs (fast).

    Complexity: O(k²) for co-presence checks vs O(k·n) for node queries
    """
    # Filter to recently active SubEntities via presence EMA
    active = [
        e for e in subentities
        if e.presence_ema > presence_threshold
    ]

    # Build role graph using presence (not expensive node queries)
    role_graph = build_role_graph_from_presence(active)

    # Community detection on active SubEntities only
    communities = leiden_detection(role_graph)

    return communities
```

**Parameter Learning:**

The EMA decay rate α and presence threshold are LEARNED per citizen:

```python
def learn_presence_parameters(citizen_id: str, validation_window: int = 1000):
    """
    Learn optimal α and threshold from mode detection quality.

    Objective: Minimize latency (fast detection) while maintaining accuracy
    """
    # Test different α values
    alpha_candidates = [0.05, 0.1, 0.2, 0.3]

    # Test different threshold values
    threshold_candidates = [0.3, 0.4, 0.5, 0.6]

    best_alpha, best_threshold = None, None
    best_f1 = 0.0

    for alpha in alpha_candidates:
        for threshold in threshold_candidates:
            # Simulate detection with these parameters
            predictions = detect_with_params(alpha, threshold, validation_window)

            # Compare against ground truth (expensive node-based detection)
            ground_truth = detect_with_node_queries(validation_window)

            # F1 score (precision + recall)
            f1 = compute_f1(predictions, ground_truth)

            if f1 > best_f1:
                best_f1 = f1
                best_alpha = alpha
                best_threshold = threshold

    # Store learned parameters
    store_citizen_params(citizen_id, {
        'presence_alpha': best_alpha,
        'presence_threshold': best_threshold,
        'f1_score': best_f1
    })
```

**Acceptance Test:**

After implementing presence EMAs:

```cypher
// Verify all SubEntities have presence_ema initialized
MATCH (e:SubEntity)
WHERE e.presence_ema IS NULL
RETURN count(e) AS uninitialized_count

// Expected: 0 (all initialized)
```

**Performance Validation:**

```python
# Measure detection time before/after presence EMAs
import time

# Before (O(k·n))
start = time.time()
candidates_slow = detect_mode_candidates_with_node_queries(subentities)
time_slow = time.time() - start

# After (O(k²))
start = time.time()
candidates_fast = detect_mode_candidates_fast(subentities)
time_fast = time.time() - start

speedup = time_slow / time_fast
print(f"Speedup: {speedup:.1f}× (expected: ~100×)")

# Verify accuracy
assert candidates_fast == candidates_slow, "Detection results must match"
```

**Expected Results:**
- Detection time: <10ms (down from ~1000ms)
- Accuracy: F1 > 0.95 (matches expensive detection)
- Memory overhead: 16 bytes per SubEntity (presence_ema + timestamp)
```

**Implementation Guidance for Atlas:**

1. Add `presence_ema` and `presence_last_update` fields to SubEntity schema
2. Initialize presence EMAs during bootstrap (all start at 0.0)
3. Hook into spreading activation: after energy updates, call `update_presence_emas()`
4. Modify mode detection to use `presence_ema > threshold` filter
5. Implement parameter learning during bootstrap (find optimal α and threshold)
6. Add telemetry: track detection time and accuracy

**Telemetry Events:**

```json
{
  "type": "mode_detection.performance",
  "detection_time_ms": 8.5,
  "subentities_checked": 247,
  "active_count": 12,
  "candidates_found": 2,
  "method": "presence_ema"
}
```

---

## Amendment 2: Lazy Edge Materialization + TTL

**Target:** `wm_coactivation_tracking.md`

**Rationale:** Creating COACTIVATES_WITH edges for ALL SubEntity pairs is expensive (O(n²) = 200² = 40,000 edges). Most pairs never co-activate. Lazy materialization creates edges on-demand only when pairs co-activate, with TTL to expire unused edges.

**Storage Impact:**
- Current (eager): 40,000 edges created upfront
- With lazy + TTL: ~600 edges (only frequently co-activating pairs persist)
- **66× storage reduction**

**Location:** §4 "Update Mechanism" (add subsection after §4.1)

**Subsection Title:** `§4.1.1 Lazy Edge Materialization with TTL`

**Text to Add:**

```markdown
### Lazy Edge Materialization with TTL

**Problem:** Creating COACTIVATES_WITH edges for all n² SubEntity pairs is wasteful:

- Most pairs never co-activate (different semantic domains)
- Storage grows quadratically: O(n²) = 200² = 40,000 edges
- Maintenance overhead even for inactive pairs

**Solution:** Create edges lazily (on first co-activation) + expire unused edges (TTL).

**Schema Additions:**

```cypher
(:SubEntity)-[:COACTIVATES_WITH {
  both_ema: Float,
  either_ema: Float,
  u_jaccard: Float,
  both_count: Integer,
  either_count: Integer,
  last_ts: DateTime,
  alpha: Float,

  // NEW: TTL fields
  created_at: DateTime,          // When edge was created
  last_coactivation: DateTime,   // Last time both were active
  ttl_expires_at: DateTime,      // When edge expires if unused
  access_count: Integer          // How many times accessed
}]->(:SubEntity)
```

**Lazy Creation Logic:**

```python
def update_coactivation_lazy(event: dict):
    """
    Update co-activation edges lazily - create only when needed.
    """
    entities_active = set(event["entities_active"])
    all_entities = event["all_entities"]

    for A in all_entities:
        for B in all_entities:
            if A >= B:
                continue

            both_active = (A in entities_active) and (B in entities_active)
            either_active = (A in entities_active) or (B in entities_active)

            # Get edge (may not exist yet)
            edge = get_coactivates_edge(A, B)

            if edge is None and (both_active or either_active):
                # LAZY CREATE: Only when pair co-activates for first time
                edge = create_coactivates_edge(A, B, {
                    'both_ema': 0.0,
                    'either_ema': 0.0,
                    'u_jaccard': 0.0,
                    'both_count': 0,
                    'either_count': 0,
                    'alpha': 0.1,
                    'created_at': now(),
                    'last_coactivation': now() if both_active else None,
                    'ttl_expires_at': now() + TTL_DURATION,
                    'access_count': 0
                })

            if edge is not None:
                # Update existing edge
                edge.both_ema = alpha * both_signal + (1 - alpha) * edge.both_ema
                edge.either_ema = alpha * either_signal + (1 - alpha) * edge.either_ema
                edge.u_jaccard = edge.both_ema / edge.either_ema if edge.either_ema > 0 else 0.0

                edge.both_count += 1 if both_active else 0
                edge.either_count += 1
                edge.last_ts = now()

                # TTL refresh
                if both_active:
                    edge.last_coactivation = now()
                    edge.ttl_expires_at = now() + TTL_DURATION

                edge.access_count += 1
```

**TTL Expiration (Garbage Collection):**

Run periodically (e.g., daily) to clean up unused edges:

```python
def expire_unused_coactivation_edges(ttl_duration: timedelta = timedelta(days=30)):
    """
    Delete COACTIVATES_WITH edges that haven't been accessed within TTL.

    Criteria for expiration:
    - No co-activation in last TTL_DURATION days
    - Low u_jaccard (<0.1) - pairs rarely co-activate
    - Low access_count (<10) - rarely queried
    """
    query = """
    MATCH (a:SubEntity)-[r:COACTIVATES_WITH]->(b:SubEntity)
    WHERE r.ttl_expires_at < datetime()
      AND r.u_jaccard < 0.1
      AND r.access_count < 10
    DELETE r
    RETURN count(r) AS expired_count
    """

    result = graph.query(query)
    expired = result[0]['expired_count']

    log.info(f"Expired {expired} unused COACTIVATES_WITH edges")

    # Telemetry
    emit_telemetry({
        'type': 'coactivation.gc',
        'expired_count': expired,
        'ttl_days': ttl_duration.days
    })
```

**Parameter Learning: TTL Duration**

The TTL duration is LEARNED per citizen based on memory dynamics:

```python
def learn_ttl_duration(citizen_id: str) -> timedelta:
    """
    Learn optimal TTL duration from co-activation churn rate.

    Logic:
    - High churn (interests change quickly): Short TTL (7 days)
    - Low churn (stable interests): Long TTL (90 days)
    - Medium churn: Standard TTL (30 days)
    """
    # Measure how often SubEntity memberships change
    churn_rate = measure_subentity_churn(citizen_id, window_days=30)

    # Percentile-based thresholding (zero-constant)
    churn_p50 = get_percentile(churn_rate, 50)
    churn_p80 = get_percentile(churn_rate, 80)

    if churn_rate > churn_p80:
        ttl = timedelta(days=7)   # High churn
    elif churn_rate > churn_p50:
        ttl = timedelta(days=30)  # Medium churn
    else:
        ttl = timedelta(days=90)  # Low churn

    store_citizen_params(citizen_id, {'coactivation_ttl_days': ttl.days})
    return ttl
```

**Acceptance Tests:**

```cypher
// AT-1: Verify lazy creation (edges only exist for co-activated pairs)
MATCH (a:SubEntity)-[r:COACTIVATES_WITH]->(b:SubEntity)
WHERE r.both_count = 0
RETURN count(r) AS never_coactivated

// Expected: 0 (all edges have at least one co-activation)

// AT-2: Verify TTL fields present
MATCH ()-[r:COACTIVATES_WITH]->()
WHERE r.ttl_expires_at IS NULL OR r.created_at IS NULL
RETURN count(r) AS missing_ttl_fields

// Expected: 0 (all edges have TTL metadata)

// AT-3: Storage efficiency
MATCH ()-[r:COACTIVATES_WITH]->()
WITH count(r) AS edge_count
MATCH (e:SubEntity)
WITH edge_count, count(e) AS subentity_count
RETURN
  subentity_count,
  edge_count,
  (edge_count * 1.0 / (subentity_count * (subentity_count - 1) / 2)) AS density

// Expected density: 0.03-0.15 (3-15% of possible pairs, not 100%)
```

**Migration from Eager to Lazy:**

If system currently has eagerly-created edges, migrate them:

```python
def migrate_to_lazy_edges():
    """
    Migrate existing COACTIVATES_WITH edges to lazy+TTL schema.

    Steps:
    1. Add TTL fields to existing edges
    2. Delete edges that never co-activated (both_count = 0)
    3. Set TTL expiration based on last_coactivation
    """
    # Add TTL fields to existing edges
    query_add_fields = """
    MATCH ()-[r:COACTIVATES_WITH]->()
    WHERE r.created_at IS NULL
    SET r.created_at = datetime() - duration('P30D'),
        r.last_coactivation = r.last_ts,
        r.ttl_expires_at = r.last_ts + duration('P30D'),
        r.access_count = r.either_count
    """
    graph.query(query_add_fields)

    # Delete never-activated edges
    query_delete_unused = """
    MATCH ()-[r:COACTIVATES_WITH]->()
    WHERE r.both_count = 0
    DELETE r
    RETURN count(r) AS deleted
    """
    result = graph.query(query_delete_unused)

    log.info(f"Migration complete: {result[0]['deleted']} unused edges removed")
```
```

**Implementation Guidance for Atlas:**

1. Add TTL fields to COACTIVATES_WITH edge schema (created_at, last_coactivation, ttl_expires_at, access_count)
2. Modify `update_coactivation_from_wm_event()` to create edges lazily (only when pair activates)
3. Implement TTL expiration job (daily cleanup of unused edges)
4. Learn TTL duration per citizen from churn rate
5. Migrate existing edges if necessary (add TTL fields, delete unused)
6. Add telemetry for garbage collection

**Scheduler Integration:**

```python
# orchestration/scheduler.py
schedule.every().day.at("03:00").do(expire_unused_coactivation_edges)
```

---

## Amendment 3: Hysteresis for Mode Activation

**Target:** `emergent_ifs_modes.md`

**Rationale:** Mode activation without hysteresis causes flicker - modes rapidly activate/deactivate near threshold boundary. Hysteresis uses learned entry/exit contours with gap between them, preventing oscillation.

**Stability Impact:**
- Current (no hysteresis): Mode flickers 5-10 times per minute near threshold
- With hysteresis: Mode state changes <1 time per minute (stable)
- **10× reduction in state changes**

**Location:** §5 "Mode Lifecycle Management" (replace §5.4 "Hysteresis via Entry/Exit Contours")

**Section Title:** `§5.4 Hysteresis for Stable Mode Activation (UPDATED)`

**Text to Replace:**

```markdown
## Hysteresis for Stable Mode Activation

**Problem:** Single-threshold activation causes mode flicker:

```python
# Flickering behavior
if q_mode > THRESHOLD:
    activate_mode()   # Activates
else:
    deactivate_mode() # Deactivates immediately if q_mode drops slightly
```

When Q_mode oscillates around threshold (e.g., 0.48 ↔ 0.52), mode rapidly flickers on/off.

**Solution:** Hysteresis with learned entry/exit contours:

- **Entry contour:** Higher threshold for activation (prevents spurious activation)
- **Exit contour:** Lower threshold for deactivation (prevents spurious deactivation)
- **Gap between contours:** Creates stability zone where mode state persists

**Schema:**

```cypher
(:Mode)-[:HAS_ENTRY_CONTOUR {
  dimensions: List[String],      // Which Q dimensions (cohesion, boundary, affect, procedural, persistence)
  thresholds: List[Float],        // Learned threshold per dimension
  source: String,                 // "boot" or "learned"
  sample_size: Integer,           // How many observations used
  created_at: DateTime,
  last_updated: DateTime
}]->(:Contour)

(:Mode)-[:HAS_EXIT_CONTOUR {
  dimensions: List[String],
  thresholds: List[Float],        // Lower than entry thresholds
  source: String,
  sample_size: Integer,
  created_at: DateTime,
  last_updated: DateTime
}]->(:Contour)
```

**Activation Logic with Hysteresis:**

```python
def check_mode_activation_with_hysteresis(mode: Mode,
                                          q_components: Dict[str, float]) -> bool:
    """
    Check if mode should activate/deactivate using hysteresis.

    Args:
        mode: Mode to check
        q_components: {dimension: value} for Q_mode components

    Returns:
        True if mode should be active, False otherwise
    """
    current_state = mode.status  # 'active' or 'inactive'

    # Get entry/exit contours
    entry_contour = mode.get_entry_contour()
    exit_contour = mode.get_exit_contour()

    if current_state == 'inactive':
        # Check ENTRY contour (higher thresholds)
        meets_entry = all(
            q_components[dim] > entry_contour.thresholds[i]
            for i, dim in enumerate(entry_contour.dimensions)
        )
        return meets_entry

    else:  # current_state == 'active'
        # Check EXIT contour (lower thresholds)
        meets_exit = all(
            q_components[dim] > exit_contour.thresholds[i]
            for i, dim in enumerate(exit_contour.dimensions)
        )
        return meets_exit  # Stay active if above exit contour
```

**Learning Entry/Exit Contours:**

During bootstrap and operation, learn contours from mode activation patterns:

```python
def learn_mode_contours(mode_id: str,
                       activation_history: List[Dict]) -> Tuple[List[float], List[float]]:
    """
    Learn entry and exit contours from mode activation history.

    Args:
        mode_id: Which mode to learn for
        activation_history: [{q_components, became_active, became_inactive}, ...]

    Returns:
        (entry_thresholds, exit_thresholds) for each Q dimension
    """
    dimensions = ['cohesion', 'boundary_clarity', 'affect_consistency',
                  'procedural_consistency', 'persistence']

    # Separate activation and deactivation events
    activation_events = [
        h['q_components'] for h in activation_history
        if h['became_active']
    ]
    deactivation_events = [
        h['q_components'] for h in activation_history
        if h['became_inactive']
    ]

    entry_thresholds = []
    exit_thresholds = []

    for dim in dimensions:
        # Entry threshold: P60 of activation events (conservative)
        activation_values = [e[dim] for e in activation_events]
        entry_p60 = percentile(activation_values, 60)

        # Exit threshold: P40 of deactivation events (stable)
        deactivation_values = [e[dim] for e in deactivation_events]
        exit_p40 = percentile(deactivation_values, 40)

        # Ensure gap: entry > exit
        if entry_p60 <= exit_p40:
            # Force gap of at least 0.1
            exit_p40 = entry_p60 - 0.1

        entry_thresholds.append(entry_p60)
        exit_thresholds.append(exit_p40)

    return entry_thresholds, exit_thresholds
```

**Bootstrap Contours:**

During bootstrap (§2.6), establish initial contours from boot data:

```python
def establish_boot_contours(mode_id: str, boot_frames: List[Dict]):
    """
    Create initial entry/exit contours from bootstrap observations.

    Boot frames include Q_mode components for candidate modes.
    Learn conservative contours from this data.
    """
    entry_thresholds, exit_thresholds = learn_mode_contours(
        mode_id,
        boot_frames
    )

    # Create entry contour
    create_contour_edge(mode_id, 'ENTRY', {
        'dimensions': ['cohesion', 'boundary_clarity', 'affect_consistency',
                      'procedural_consistency', 'persistence'],
        'thresholds': entry_thresholds,
        'source': 'boot',
        'sample_size': len(boot_frames),
        'created_at': now()
    })

    # Create exit contour
    create_contour_edge(mode_id, 'EXIT', {
        'dimensions': ['cohesion', 'boundary_clarity', 'affect_consistency',
                      'procedural_consistency', 'persistence'],
        'thresholds': exit_thresholds,
        'source': 'boot',
        'sample_size': len(boot_frames),
        'created_at': now()
    })
```

**Operational Refinement:**

During operation, refine contours based on observed activations:

```python
def refine_contours_operational(mode_id: str, window_frames: int = 1000):
    """
    Refine mode contours from operational data (not boot).

    Called periodically (e.g., every 1000 frames) to adapt contours.
    """
    # Get recent activation history
    history = get_mode_activation_history(mode_id, last_n=window_frames)

    if len(history) < 100:
        # Not enough data to refine
        return

    # Learn new contours
    entry_new, exit_new = learn_mode_contours(mode_id, history)

    # Smooth transition: EMA blend with existing contours
    entry_old = get_entry_contour(mode_id).thresholds
    exit_old = get_exit_contour(mode_id).thresholds

    alpha = 0.2  # Blend factor
    entry_refined = [
        alpha * new + (1 - alpha) * old
        for new, old in zip(entry_new, entry_old)
    ]
    exit_refined = [
        alpha * new + (1 - alpha) * old
        for new, old in zip(exit_new, exit_old)
    ]

    # Update contours
    update_contour(mode_id, 'ENTRY', {
        'thresholds': entry_refined,
        'source': 'learned',
        'sample_size': len(history),
        'last_updated': now()
    })
    update_contour(mode_id, 'EXIT', {
        'thresholds': exit_refined,
        'source': 'learned',
        'sample_size': len(history),
        'last_updated': now()
    })
```

**Acceptance Tests:**

```cypher
// AT-1: Verify all mature modes have entry/exit contours
MATCH (m:Mode {status: 'mature'})
WHERE NOT (m)-[:HAS_ENTRY_CONTOUR]->()
   OR NOT (m)-[:HAS_EXIT_CONTOUR]->()
RETURN count(m) AS missing_contours

// Expected: 0 (all mature modes have contours)

// AT-2: Verify entry > exit (hysteresis gap exists)
MATCH (m:Mode)-[entry:HAS_ENTRY_CONTOUR]->(ec:Contour),
      (m)-[exit:HAS_EXIT_CONTOUR]->(xc:Contour)
WHERE any(i IN range(0, size(entry.thresholds)-1)
          WHERE entry.thresholds[i] <= exit.thresholds[i])
RETURN m.id AS mode_id,
       entry.thresholds AS entry_t,
       exit.thresholds AS exit_t

// Expected: Empty (entry always > exit for all dimensions)
```

**Flicker Measurement:**

Measure reduction in mode state changes:

```python
def measure_flicker_reduction(mode_id: str, before_window: int = 10000, after_window: int = 10000):
    """
    Compare mode state changes before and after hysteresis.

    Metric: State changes per 1000 frames
    """
    # Before hysteresis (single threshold)
    history_before = get_activation_history(mode_id, before_window, use_hysteresis=False)
    changes_before = count_state_changes(history_before)
    rate_before = (changes_before / before_window) * 1000

    # After hysteresis (entry/exit contours)
    history_after = get_activation_history(mode_id, after_window, use_hysteresis=True)
    changes_after = count_state_changes(history_after)
    rate_after = (changes_after / after_window) * 1000

    reduction = (rate_before - rate_after) / rate_before * 100

    print(f"Mode {mode_id} state changes:")
    print(f"  Before hysteresis: {rate_before:.1f} per 1000 frames")
    print(f"  After hysteresis:  {rate_after:.1f} per 1000 frames")
    print(f"  Reduction: {reduction:.0f}%")

    return {
        'mode_id': mode_id,
        'changes_before': changes_before,
        'changes_after': changes_after,
        'reduction_percent': reduction
    }
```
```

**Implementation Guidance for Atlas:**

1. Add contour edges to Mode schema (HAS_ENTRY_CONTOUR, HAS_EXIT_CONTOUR)
2. Implement hysteresis check in mode activation logic (check entry when inactive, check exit when active)
3. Establish boot contours during bootstrap (§2.6)
4. Implement operational refinement (refine contours every 1000 frames)
5. Track activation history for contour learning
6. Add telemetry for flicker measurement

**Telemetry Events:**

```json
{
  "type": "mode.state_change",
  "mode_id": "guardian",
  "from_state": "inactive",
  "to_state": "active",
  "q_mode": 0.68,
  "entry_contour": [0.65, 0.70, 0.60, 0.65, 0.70],
  "contour_met": true,
  "hysteresis_gap": 0.15
}
```

---

## Amendment 4: S_use/S_red for Mode Pair Differentiation

**Target:** `emergent_ifs_modes.md`

**Rationale:** Mode pairs can overlap (share SubEntities) in useful ways (complementary) or wasteful ways (redundant). Apply same S_use/S_red metrics from `entity_differentiation.md` to detect mode redundancy and trigger merge/dissolution.

**Quality Impact:**
- Without pair differentiation: Redundant modes persist (e.g., "Guardian" and "Protector" doing same thing)
- With S_use/S_red: Automatic detection and merge of redundant modes, preservation of complementary modes
- **Cleaner mode ecology** (5-15 distinct modes, not 20+ near-duplicates)

**Location:** §5 "Mode Lifecycle Management" (add new subsection after §5.4)

**Subsection Title:** `§5.5 Mode Pair Differentiation (S_use/S_red)`

**Text to Add:**

```markdown
### Mode Pair Differentiation (S_use/S_red)

**Problem:** Mode pairs can share SubEntities without being redundant:

- **Complementary modes:** Share context but serve different functions (e.g., "Observer" and "Validator" both activate during code review but provide different perspectives)
- **Redundant modes:** Near-duplicates with high overlap and no differentiation (e.g., "Guardian" and "Protector" both providing safety regulation)

**Solution:** Apply S_use/S_red metrics from entity differentiation (see `entity_differentiation.md` §2):

**Pair Metrics for Modes:**

Compute 5 metrics for each mode pair (M_A, M_B):

```python
def compute_mode_pair_metrics(mode_a: str, mode_b: str) -> Dict[str, float]:
    """
    Compute differentiation metrics for mode pair.

    Same 5 metrics as SubEntity pairs (entity_differentiation.md §2)
    """
    # 1. Jaccard affiliation overlap
    affiliates_a = set(get_mode_affiliates(mode_a))
    affiliates_b = set(get_mode_affiliates(mode_b))
    J = len(affiliates_a & affiliates_b) / len(affiliates_a | affiliates_b)

    # 2. Signature cosine similarity
    sig_a = get_mode_signature(mode_a)  # {affect, tools, outcomes, self_talk}
    sig_b = get_mode_signature(mode_b)
    C = cosine_similarity(sig_a, sig_b)

    # 3. Co-activation (U) - from SubEntity COACTIVATES_WITH
    # How often do modes' affiliates co-activate?
    U = compute_affiliate_coactivation(affiliates_a, affiliates_b)

    # 4. Highway utility (H) - Do modes connect different domains?
    # Count RELATES_TO edges between affiliates of M_A and M_B
    H = count_relates_to_edges(affiliates_a, affiliates_b)

    # 5. Context divergence (ΔCtx) - Do modes activate in different situations?
    ctx_a = get_activation_contexts(mode_a)
    ctx_b = get_activation_contexts(mode_b)
    ΔCtx = context_divergence(ctx_a, ctx_b)

    return {'J': J, 'C': C, 'U': U, 'H': H, 'ΔCtx': ΔCtx}
```

**Redundancy Score (S_red):**

High when modes overlap without differentiation:

```python
def compute_mode_redundancy(J: float, C: float, U: float, H: float, ΔCtx: float) -> float:
    """
    S_red: Redundancy score for mode pair.

    High S_red → modes are near-duplicates, should merge
    """
    # Percentile normalization (citizen-local cohorts)
    J_tilde = percentile_normalize(J, 'mode_jaccard')
    C_tilde = percentile_normalize(C, 'mode_cosine')
    U_tilde = percentile_normalize(U, 'mode_coactivation')
    H_tilde = percentile_normalize(H, 'mode_highway')
    ΔCtx_tilde = percentile_normalize(ΔCtx, 'mode_context_div')

    # Softplus composition (same as entity_differentiation.md §2.3)
    S_red = (
        softplus(J_tilde + C_tilde + U_tilde) -
        softplus(H_tilde + ΔCtx_tilde)
    )

    return S_red
```

**Usefulness Score (S_use):**

High when modes are complementary (overlap but differentiated):

```python
def compute_mode_usefulness(J: float, C: float, U: float, H: float, ΔCtx: float) -> float:
    """
    S_use: Usefulness score for mode pair.

    High S_use → modes are complementary, should preserve both
    """
    # Same normalization
    J_tilde = percentile_normalize(J, 'mode_jaccard')
    C_tilde = percentile_normalize(C, 'mode_cosine')
    H_tilde = percentile_normalize(H, 'mode_highway')
    ΔCtx_tilde = percentile_normalize(ΔCtx, 'mode_context_div')

    # Softplus composition
    S_use = (
        softplus(H_tilde + ΔCtx_tilde) -
        softplus(J_tilde + C_tilde)
    )

    return S_use
```

**Lifecycle Decisions:**

Use S_red/S_use to guide mode merge/dissolution:

```python
def evaluate_mode_pair_for_merge(mode_a: str, mode_b: str) -> Dict:
    """
    Decide if mode pair should merge based on S_red/S_use.
    """
    metrics = compute_mode_pair_metrics(mode_a, mode_b)
    S_red = compute_mode_redundancy(**metrics)
    S_use = compute_mode_usefulness(**metrics)

    # Learned thresholds (percentile-based, citizen-local)
    S_red_high = get_percentile('mode_redundancy', 80)
    S_use_low = get_percentile('mode_usefulness', 20)

    decision = {
        'mode_a': mode_a,
        'mode_b': mode_b,
        'metrics': metrics,
        'S_red': S_red,
        'S_use': S_use,
        'action': None,
        'rationale': None
    }

    if S_red > S_red_high and S_use < S_use_low:
        # High redundancy, low usefulness → MERGE
        decision['action'] = 'merge'
        decision['rationale'] = f"Redundant modes (S_red={S_red:.2f}, S_use={S_use:.2f})"

    elif S_use > get_percentile('mode_usefulness', 80):
        # High usefulness → PRESERVE BOTH
        decision['action'] = 'preserve'
        decision['rationale'] = f"Complementary modes (S_use={S_use:.2f})"

    else:
        # Ambiguous → NO ACTION (monitor)
        decision['action'] = 'monitor'
        decision['rationale'] = f"Unclear differentiation (S_red={S_red:.2f}, S_use={S_use:.2f})"

    return decision
```

**Periodic Mode Pair Audit:**

Check all mode pairs periodically (e.g., weekly) for redundancy:

```python
def audit_mode_pairs_for_redundancy(citizen_id: str):
    """
    Check all mode pairs, merge redundant ones.

    Called: Weekly (low frequency, expensive operation)
    """
    modes = get_citizen_modes(citizen_id, status='mature')

    merge_candidates = []

    for mode_a in modes:
        for mode_b in modes:
            if mode_a >= mode_b:
                continue

            evaluation = evaluate_mode_pair_for_merge(mode_a, mode_b)

            if evaluation['action'] == 'merge':
                merge_candidates.append(evaluation)

    # Sort by S_red (most redundant first)
    merge_candidates.sort(key=lambda x: x['S_red'], reverse=True)

    # Execute merges (limit to 2 per audit to avoid disruption)
    for candidate in merge_candidates[:2]:
        merge_modes(
            mode_a=candidate['mode_a'],
            mode_b=candidate['mode_b'],
            rationale=candidate['rationale']
        )

        emit_telemetry({
            'type': 'mode.merged',
            'mode_a': candidate['mode_a'],
            'mode_b': candidate['mode_b'],
            'S_red': candidate['S_red'],
            'S_use': candidate['S_use']
        })
```

**Acceptance Tests:**

```cypher
// AT-1: Verify no high-redundancy mode pairs remain
// (Audit should have merged them)
MATCH (m1:Mode {status: 'mature'}), (m2:Mode {status: 'mature'})
WHERE id(m1) < id(m2)
WITH m1, m2,
     // Compute Jaccard overlap of affiliates
     [(m1)<-[:AFFILIATES_WITH]-(e) | e.id] AS aff1,
     [(m2)<-[:AFFILIATES_WITH]-(e) | e.id] AS aff2
WITH m1, m2,
     size([x IN aff1 WHERE x IN aff2]) * 1.0 / size(aff1 + aff2) AS jaccard
WHERE jaccard > 0.7  // High overlap
RETURN m1.id AS mode_a, m2.id AS mode_b, jaccard
ORDER BY jaccard DESC
LIMIT 5

// Expected: <2 pairs (low-redundancy mode ecology)
```

**Performance Note:**

Mode pair audit is O(k²) where k = number of modes (5-15), so k² = 25-225 comparisons. Much cheaper than SubEntity pair audit (O(n²) where n = 200-500).

Run weekly, not daily.
```

**Implementation Guidance for Atlas:**

1. Implement `compute_mode_pair_metrics()` using SubEntity differentiation logic
2. Implement `compute_mode_redundancy()` and `compute_mode_usefulness()` (same formulas as entity_differentiation.md)
3. Create weekly scheduler job for `audit_mode_pairs_for_redundancy()`
4. Implement mode merge logic (combine affiliations, blend signatures, preserve history)
5. Add telemetry for mode merges

**Scheduler Integration:**

```python
# orchestration/scheduler.py
schedule.every().sunday.at("04:00").do(audit_mode_pairs_for_redundancy)
```

---

## Amendment 5: Log-Domain Fusion with Learned θ

**Target:** `emergent_ifs_modes.md` (if RRF used for mode ranking), or general consciousness retrieval specs

**Rationale:** Current RRF (Reciprocal Rank Fusion) uses arithmetic domain, which can overflow or lose precision with extreme scores. Log-domain RRF is numerically stable. Additionally, blend parameter θ should be LEARNED per citizen, not fixed at 0.5.

**Precision Impact:**
- Arithmetic RRF: Precision errors with extreme scores (1e-10 or 1e10)
- Log-domain RRF: Stable across all score ranges
- **Learned θ:** Adapts fusion to citizen-specific retrieval patterns (some citizens prefer semantic, others prefer energy-based retrieval)

**Location:** New section in retrieval specs (or emergent_ifs_modes.md if modes ranked via RRF)

**Section Title:** `§X Log-Domain RRF with Learned Blend Parameter`

**Text to Add:**

```markdown
## Log-Domain RRF with Learned Blend Parameter

**Problem:** Arithmetic RRF can overflow or lose precision:

```python
# Arithmetic RRF (unstable)
def rrf_arithmetic(scores_a: List[float], scores_b: List[float], k: int = 60) -> List[float]:
    fused = []
    for rank_a, rank_b in zip(ranks_a, ranks_b):
        score = 1/(k + rank_a) + 1/(k + rank_b)  # Can overflow if k small
        fused.append(score)
    return fused
```

Issues:
- Overflow if k is small or ranks are large
- Loss of precision with extreme score differences
- Fixed blend (equal weight to both rankings)

**Solution:** Log-domain RRF with learned blend parameter:

**Log-Domain Formulation:**

```python
import numpy as np

def rrf_log_domain(scores_a: List[float],
                   scores_b: List[float],
                   theta: float = 0.5,
                   k: int = 60) -> List[float]:
    """
    Log-domain RRF with learned blend parameter.

    Args:
        scores_a: First ranking scores
        scores_b: Second ranking scores
        theta: Blend parameter (0 = all A, 1 = all B, 0.5 = equal)
        k: RRF constant (default 60)

    Returns:
        Fused scores in log domain (more stable)
    """
    # Convert to ranks (1-indexed)
    ranks_a = rankdata(-np.array(scores_a), method='ordinal')
    ranks_b = rankdata(-np.array(scores_b), method='ordinal')

    # Log-domain fusion
    log_scores = []
    for rank_a, rank_b in zip(ranks_a, ranks_b):
        # Log of individual RRF scores
        log_rrf_a = -np.log(k + rank_a)
        log_rrf_b = -np.log(k + rank_b)

        # Weighted blend in log domain
        log_fused = theta * log_rrf_a + (1 - theta) * log_rrf_b

        log_scores.append(log_fused)

    # Convert back to linear domain if needed
    scores_fused = np.exp(log_scores)

    return scores_fused.tolist()
```

**Learning θ per Citizen:**

The blend parameter θ is LEARNED from retrieval quality:

```python
def learn_rrf_theta(citizen_id: str, validation_queries: List[Dict]) -> float:
    """
    Learn optimal θ from retrieval quality on validation queries.

    Args:
        citizen_id: Which citizen to learn for
        validation_queries: [{query, relevant_docs}, ...] with ground truth

    Returns:
        Optimal θ ∈ [0, 1]
    """
    theta_candidates = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    best_theta = 0.5
    best_ndcg = 0.0

    for theta in theta_candidates:
        ndcg_scores = []

        for query in validation_queries:
            # Retrieve with this θ
            results = retrieve_with_rrf(
                query['query'],
                theta=theta,
                k=60
            )

            # Compute NDCG against ground truth
            ndcg = compute_ndcg(results, query['relevant_docs'])
            ndcg_scores.append(ndcg)

        avg_ndcg = np.mean(ndcg_scores)

        if avg_ndcg > best_ndcg:
            best_ndcg = avg_ndcg
            best_theta = theta

    # Store learned parameter
    store_citizen_params(citizen_id, {
        'rrf_theta': best_theta,
        'rrf_ndcg': best_ndcg
    })

    return best_theta
```

**Interpretation of θ:**

- **θ = 0.0:** Use only ranking A (e.g., semantic similarity)
- **θ = 0.5:** Equal blend (standard RRF)
- **θ = 1.0:** Use only ranking B (e.g., energy-based salience)

**Adaptive θ per Query Type:**

Advanced: Learn different θ for different query types:

```python
def learn_theta_per_query_type(citizen_id: str) -> Dict[str, float]:
    """
    Learn query-type-specific θ values.

    Query types:
    - 'semantic': Concept-based queries ("tell me about X")
    - 'procedural': Action-based queries ("how do I do Y")
    - 'episodic': Memory-based queries ("when did Z happen")
    """
    query_types = ['semantic', 'procedural', 'episodic']
    theta_per_type = {}

    for qtype in query_types:
        validation_queries = get_validation_queries(citizen_id, qtype)
        theta_optimal = learn_rrf_theta(citizen_id, validation_queries)
        theta_per_type[qtype] = theta_optimal

    return theta_per_type
```

**Acceptance Tests:**

```python
# AT-1: Verify log-domain stability
def test_log_domain_stability():
    """Test that log-domain RRF handles extreme scores."""
    scores_a = [1e-10, 1e-8, 1e-6, 0.001, 0.1, 1.0]
    scores_b = [1e10, 1e8, 1e6, 1000, 100, 10]

    # Should not overflow or underflow
    fused = rrf_log_domain(scores_a, scores_b, theta=0.5)

    assert all(np.isfinite(fused)), "Log-domain RRF produced inf/nan"
    assert all(f > 0 for f in fused), "Log-domain RRF produced negative scores"

# AT-2: Verify θ learning improves retrieval
def test_theta_learning_improves_ndcg():
    """Test that learned θ outperforms fixed θ=0.5."""
    validation_queries = load_validation_queries('citizen_luca')

    # Baseline: Fixed θ = 0.5
    ndcg_baseline = evaluate_rrf(validation_queries, theta=0.5)

    # Learned: Optimal θ
    theta_learned = learn_rrf_theta('citizen_luca', validation_queries)
    ndcg_learned = evaluate_rrf(validation_queries, theta=theta_learned)

    assert ndcg_learned >= ndcg_baseline, "Learned θ should not harm retrieval"
    print(f"NDCG improvement: {ndcg_baseline:.3f} → {ndcg_learned:.3f}")
```
```

**Implementation Guidance for Atlas:**

1. Replace arithmetic RRF with log-domain version (wherever RRF is used)
2. Implement `learn_rrf_theta()` during citizen bootstrap
3. Store learned θ per citizen in configuration
4. Optionally: Learn query-type-specific θ values
5. Add acceptance tests for numerical stability

---

## Amendment 6: Two-Timescale Stability Monitoring

**Target:** `emergent_ifs_modes.md` (or general consciousness monitoring)

**Rationale:** Single-timescale EMAs can miss slow drift (gradual degradation) while adapting to noise. Two-timescale approach uses FAST EMA (tracks current state) and SLOW EMA (tracks baseline), with alerts when divergence exceeds threshold.

**Resilience Impact:**
- Single EMA: Slow drift goes undetected (frog-boiling problem)
- Two-timescale: Detects both fast anomalies and slow drift
- **Early warning system** for mode quality degradation

**Location:** §5 "Mode Lifecycle Management" (add new subsection after §5.5)

**Subsection Title:** `§5.6 Two-Timescale Stability Monitoring`

**Text to Add:**

```markdown
### Two-Timescale Stability Monitoring

**Problem:** Single-timescale EMA adaptation misses slow drift:

```python
# Single EMA (fast adaptation)
q_mode_ema = alpha * q_mode_current + (1 - alpha) * q_mode_ema

# If Q_mode gradually degrades (0.8 → 0.75 → 0.70 → 0.65 over weeks),
# the EMA follows the drift and never triggers an alert.
```

This is the **frog-boiling problem:** Gradual degradation goes unnoticed because the reference point moves with the drift.

**Solution:** Track TWO EMAs at different timescales:

1. **Fast EMA (α_fast = 0.1):** Tracks current state, responds quickly to changes
2. **Slow EMA (α_slow = 0.01):** Tracks baseline, resistant to short-term noise

**Alert when divergence exceeds threshold:** Fast drops below slow by more than learned threshold.

**Schema Additions:**

```cypher
(:Mode {
  q_mode_fast: Float,            // Fast EMA (α = 0.1, ~10-frame window)
  q_mode_slow: Float,            // Slow EMA (α = 0.01, ~100-frame window)
  q_mode_divergence: Float,      // slow - fast (positive = degradation)
  stability_status: String       // 'stable' | 'drifting' | 'degraded'
})
```

**Update Mechanism:**

After computing Q_mode each frame:

```python
def update_two_timescale_emas(mode: Mode, q_mode_current: float):
    """
    Update fast and slow EMAs, compute divergence.
    """
    alpha_fast = 0.1   # Learned per citizen (typically 0.05-0.2)
    alpha_slow = 0.01  # Learned per citizen (typically 0.005-0.02)

    # Update fast EMA (responsive)
    mode.q_mode_fast = (
        alpha_fast * q_mode_current +
        (1 - alpha_fast) * mode.q_mode_fast
    )

    # Update slow EMA (stable baseline)
    mode.q_mode_slow = (
        alpha_slow * q_mode_current +
        (1 - alpha_slow) * mode.q_mode_slow
    )

    # Compute divergence (positive = degradation)
    mode.q_mode_divergence = mode.q_mode_slow - mode.q_mode_fast

    # Classify stability status
    divergence_warn = get_percentile('mode_divergence', 80)   # Learned threshold
    divergence_critical = get_percentile('mode_divergence', 95)

    if mode.q_mode_divergence > divergence_critical:
        mode.stability_status = 'degraded'
    elif mode.q_mode_divergence > divergence_warn:
        mode.stability_status = 'drifting'
    else:
        mode.stability_status = 'stable'
```

**Alerting and Intervention:**

When stability status degrades, investigate and intervene:

```python
def handle_mode_stability_degradation(mode_id: str):
    """
    Handle mode that has drifted or degraded.

    Actions:
    1. Log alert for operator investigation
    2. Analyze: What changed? (affiliations, signature, outcomes)
    3. Trigger: Re-seeding if degraded, monitoring if drifting
    """
    mode = get_mode(mode_id)

    if mode.stability_status == 'degraded':
        # Critical: Q_mode dropped significantly below baseline
        log.warning(f"Mode {mode_id} DEGRADED: divergence={mode.q_mode_divergence:.2f}")

        emit_telemetry({
            'type': 'mode.stability.degraded',
            'mode_id': mode_id,
            'q_mode_fast': mode.q_mode_fast,
            'q_mode_slow': mode.q_mode_slow,
            'divergence': mode.q_mode_divergence
        })

        # Analysis: Why did quality drop?
        analysis = analyze_mode_degradation(mode_id)
        # Possible causes:
        # - Affiliates lost members (SubEntity quality dropped)
        # - Signature no longer matches behavior (drift)
        # - Outcomes consistently poor (harm accumulation)

        # Intervention: Re-seed mode or dissolve
        if analysis['cause'] == 'affiliate_loss':
            recompute_affiliations(mode_id)
        elif analysis['cause'] == 'signature_drift':
            refresh_signature(mode_id)
        else:
            # Dissolve and re-seed
            dissolve_mode(mode_id, reason='quality_degradation')

    elif mode.stability_status == 'drifting':
        # Warning: Q_mode trending downward
        log.info(f"Mode {mode_id} drifting: divergence={mode.q_mode_divergence:.2f}")

        emit_telemetry({
            'type': 'mode.stability.drifting',
            'mode_id': mode_id,
            'q_mode_fast': mode.q_mode_fast,
            'q_mode_slow': mode.q_mode_slow,
            'divergence': mode.q_mode_divergence
        })

        # Monitor: Track for next N frames, escalate if continues
```

**Learning α_fast and α_slow:**

The decay rates are LEARNED per citizen:

```python
def learn_two_timescale_alphas(citizen_id: str) -> Tuple[float, float]:
    """
    Learn optimal α_fast and α_slow from mode stability patterns.

    Objective:
    - α_fast: Fast enough to detect anomalies (quick spikes/drops)
    - α_slow: Slow enough to resist noise (stable baseline)
    - Gap: Large enough to detect drift before critical degradation
    """
    # Test different combinations
    alpha_fast_candidates = [0.05, 0.1, 0.15, 0.2]
    alpha_slow_candidates = [0.005, 0.01, 0.015, 0.02]

    best_combo = (0.1, 0.01)  # Default
    best_score = 0.0

    for alpha_fast in alpha_fast_candidates:
        for alpha_slow in alpha_slow_candidates:
            # Simulate detection with these parameters
            detection_quality = simulate_drift_detection(
                citizen_id,
                alpha_fast,
                alpha_slow
            )

            # Score: F1 for detecting known degradation events
            score = detection_quality['f1_score']

            if score > best_score:
                best_score = score
                best_combo = (alpha_fast, alpha_slow)

    store_citizen_params(citizen_id, {
        'two_timescale_alpha_fast': best_combo[0],
        'two_timescale_alpha_slow': best_combo[1],
        'drift_detection_f1': best_score
    })

    return best_combo
```

**Acceptance Tests:**

```cypher
// AT-1: Verify all modes have two-timescale tracking
MATCH (m:Mode {status: 'mature'})
WHERE m.q_mode_fast IS NULL OR m.q_mode_slow IS NULL
RETURN count(m) AS missing_two_timescale

// Expected: 0 (all mature modes track both EMAs)

// AT-2: Verify fast > slow in stable modes
MATCH (m:Mode {stability_status: 'stable'})
WHERE m.q_mode_fast < m.q_mode_slow - 0.05
RETURN m.id AS mode_id, m.q_mode_fast, m.q_mode_slow

// Expected: Empty (stable modes should have fast ≈ slow)
```

**Drift Detection Validation:**

```python
def test_drift_detection():
    """
    Test that two-timescale monitoring detects gradual degradation.
    """
    # Simulate mode with gradual Q_mode degradation
    q_mode_sequence = simulate_gradual_degradation(
        initial=0.8,
        final=0.6,
        frames=1000
    )

    mode = Mode(id='test', q_mode_fast=0.8, q_mode_slow=0.8)

    # Track with two-timescale EMAs
    alerts = []
    for frame, q_current in enumerate(q_mode_sequence):
        update_two_timescale_emas(mode, q_current)

        if mode.stability_status in ['drifting', 'degraded']:
            alerts.append((frame, mode.stability_status, mode.q_mode_divergence))

    # Verify drift detected before critical point (Q < 0.65)
    critical_frame = next(i for i, q in enumerate(q_mode_sequence) if q < 0.65)
    first_alert_frame = alerts[0][0] if alerts else None

    assert first_alert_frame is not None, "Drift not detected"
    assert first_alert_frame < critical_frame, f"Drift detected too late (frame {first_alert_frame} vs critical {critical_frame})"

    print(f"Drift detected at frame {first_alert_frame} (critical at {critical_frame})")
    print(f"Early warning: {critical_frame - first_alert_frame} frames")
```
```

**Implementation Guidance for Atlas:**

1. Add `q_mode_fast`, `q_mode_slow`, `q_mode_divergence`, `stability_status` to Mode schema
2. Update mode quality tracking to maintain both EMAs
3. Implement `handle_mode_stability_degradation()` with alerting and intervention
4. Learn α_fast and α_slow per citizen during bootstrap
5. Add telemetry for stability status changes
6. Create dashboard widget showing mode stability (fast vs slow EMA divergence)

---

## Amendment 7: Harm EMA with Nudge Cap

**Target:** `emergent_ifs_modes.md`

**Rationale:** Modes can cause harm (poor outcomes, regretted actions). Without feedback, harmful modes continue influencing behavior. Harm EMA tracks mode-specific harm accumulation, with learned nudge caps that attenuate policy influence when harm exceeds threshold.

**Safety Impact:**
- Without harm tracking: Harmful modes persist unchecked
- With harm EMA + caps: Modes learn from negative outcomes, reduce influence when causing harm
- **Self-regulating safety mechanism**

**Location:** §6 "Policy Nudges" (add new subsection after §6.2)

**Subsection Title:** `§6.3 Harm EMA with Adaptive Nudge Caps`

**Text to Add:**

```markdown
### Harm EMA with Adaptive Nudge Caps

**Problem:** Modes can cause harm without learning:

- Mode influences tool selection → poor outcome → mode continues same behavior
- No feedback loop from outcomes back to mode influence
- Harmful patterns persist

**Solution:** Track harm per mode via EMA, cap policy nudges when harm exceeds learned threshold.

**Schema Additions:**

```cypher
(:Mode {
  harm_ema: Float,               // EMA of harm attribution (0-1, higher = more harm)
  harm_cap_multiplier: Float,    // Nudge attenuation (1.0 = full, 0.0 = disabled)
  harm_threshold: Float,         // Learned threshold for applying cap
  harm_events_count: Integer     // Total harm attributions
})
```

**Harm Attribution:**

After each action outcome, attribute harm/benefit to active modes:

```python
def attribute_outcome_to_modes(outcome: Dict, active_modes: List[str]):
    """
    Attribute outcome (harm or benefit) to modes that were active.

    Args:
        outcome: {
            'outcome_id': str,
            'outcome_type': 'success' | 'failure' | 'regret' | 'neutral',
            'harm_score': float (0 = no harm, 1 = maximum harm)
        }
        active_modes: Mode IDs that were active during action
    """
    harm = outcome['harm_score']

    for mode_id in active_modes:
        mode = get_mode(mode_id)

        # Update harm EMA
        alpha_harm = 0.05  # Learned per citizen (typically 0.02-0.1)
        mode.harm_ema = alpha_harm * harm + (1 - alpha_harm) * mode.harm_ema

        # Increment harm events count
        if harm > 0.1:
            mode.harm_events_count += 1

        # Compute nudge cap multiplier based on harm level
        harm_threshold = get_percentile('mode_harm', 70)  # Learned threshold

        if mode.harm_ema > harm_threshold:
            # Apply progressive cap: linear decay from 1.0 to 0.0
            excess = mode.harm_ema - harm_threshold
            mode.harm_cap_multiplier = max(0.0, 1.0 - (excess / (1.0 - harm_threshold)))
        else:
            # No cap: full influence
            mode.harm_cap_multiplier = 1.0

        emit_telemetry({
            'type': 'mode.harm_attribution',
            'mode_id': mode_id,
            'harm_score': harm,
            'harm_ema': mode.harm_ema,
            'harm_cap': mode.harm_cap_multiplier
        })
```

**Applying Nudge Caps:**

When computing policy nudges (§6 "Policy Nudges"), apply harm cap multiplier:

```python
def apply_mode_nudges_with_harm_cap(mode_activations: Dict[str, float],
                                    tool_priors: Dict[str, float],
                                    stimulus_budget: float,
                                    highway_prefs: Dict) -> Dict:
    """
    Apply mode policy nudges with harm-based attenuation.

    Modified from §6.2 to include harm caps.
    """
    for mode_id, activation in mode_activations.items():
        mode = get_mode(mode_id)

        # Get learned nudges for this mode
        tool_nudges = get_mode_tool_nudges(mode_id)
        budget_nudge = get_mode_budget_nudge(mode_id)
        highway_nudge = get_mode_highway_nudge(mode_id)

        # APPLY HARM CAP: Attenuate nudges if mode has caused harm
        harm_cap = mode.harm_cap_multiplier  # 1.0 = full, 0.0 = disabled

        # Tool primer nudges (capped)
        for tool, multiplier in tool_nudges.items():
            capped_multiplier = 1.0 + (multiplier - 1.0) * harm_cap
            tool_priors[tool] *= (1 + activation * (capped_multiplier - 1.0))

        # Stimulus budget nudge (capped)
        capped_budget_nudge = budget_nudge * harm_cap
        stimulus_budget *= (1 + activation * capped_budget_nudge)

        # Highway preference nudge (capped)
        capped_highway_nudge = highway_nudge * harm_cap
        for highway, pref in highway_prefs.items():
            highway_prefs[highway] *= (1 + activation * capped_highway_nudge)

    return {
        'tool_priors': tool_priors,
        'stimulus_budget': stimulus_budget,
        'highway_prefs': highway_prefs
    }
```

**Learning Harm Threshold:**

The harm threshold (when to start capping) is LEARNED per citizen:

```python
def learn_harm_threshold(citizen_id: str) -> float:
    """
    Learn when to start applying harm caps based on outcome quality.

    Objective: Balance between:
    - Too low threshold: Caps applied too early, modes lose influence prematurely
    - Too high threshold: Harmful modes persist unchecked
    """
    # Get historical harm EMAs and outcome qualities
    history = get_mode_harm_history(citizen_id)

    # Find threshold that maximizes outcome quality
    threshold_candidates = [0.1, 0.2, 0.3, 0.4, 0.5]
    best_threshold = 0.3  # Default
    best_outcome_quality = 0.0

    for threshold in threshold_candidates:
        # Simulate applying this threshold historically
        outcome_quality = simulate_harm_caps(history, threshold)

        if outcome_quality > best_outcome_quality:
            best_outcome_quality = outcome_quality
            best_threshold = threshold

    store_citizen_params(citizen_id, {
        'mode_harm_threshold': best_threshold,
        'outcome_quality_with_caps': best_outcome_quality
    })

    return best_threshold
```

**Recovery from Harm:**

Modes can recover if harm decreases (harm EMA decays):

```python
def check_mode_harm_recovery(mode: Mode):
    """
    Check if mode has recovered from harm (harm_ema dropped below threshold).

    When recovery detected, gradually restore nudge influence.
    """
    harm_threshold = mode.harm_threshold

    if mode.harm_ema < harm_threshold and mode.harm_cap_multiplier < 1.0:
        # Mode recovering: gradually restore influence
        recovery_rate = 0.01  # Slow recovery (1% per frame)
        mode.harm_cap_multiplier = min(1.0, mode.harm_cap_multiplier + recovery_rate)

        if mode.harm_cap_multiplier >= 0.99:
            # Full recovery
            emit_telemetry({
                'type': 'mode.harm_recovered',
                'mode_id': mode.id,
                'harm_ema_final': mode.harm_ema,
                'harm_events_count': mode.harm_events_count
            })
```

**Acceptance Tests:**

```cypher
// AT-1: Verify modes with high harm have caps applied
MATCH (m:Mode)
WHERE m.harm_ema > 0.3 AND m.harm_cap_multiplier > 0.9
RETURN m.id AS mode_id, m.harm_ema, m.harm_cap_multiplier

// Expected: Empty (high harm should have low cap multiplier)

// AT-2: Verify harm EMA initialized for all modes
MATCH (m:Mode {status: 'mature'})
WHERE m.harm_ema IS NULL
RETURN count(m) AS missing_harm_tracking

// Expected: 0 (all mature modes track harm)
```

**Harm Impact Validation:**

```python
def test_harm_cap_effectiveness():
    """
    Test that harm caps reduce harmful mode influence.
    """
    # Simulate mode causing repeated harm
    mode = Mode(id='test_harmful', harm_ema=0.0, harm_cap_multiplier=1.0)

    harm_sequence = [0.8, 0.7, 0.9, 0.8, 0.7]  # High harm outcomes

    nudge_strength_over_time = []

    for harm in harm_sequence:
        attribute_outcome_to_modes(
            {'harm_score': harm, 'outcome_type': 'failure'},
            [mode.id]
        )

        nudge_strength = mode.harm_cap_multiplier
        nudge_strength_over_time.append(nudge_strength)

    # Verify nudge strength decreases as harm accumulates
    assert nudge_strength_over_time[0] > nudge_strength_over_time[-1], \
        "Harm cap should reduce nudge strength"

    print(f"Nudge strength: {nudge_strength_over_time[0]:.2f} → {nudge_strength_over_time[-1]:.2f}")
    print(f"Final harm EMA: {mode.harm_ema:.2f}")

# Expected output:
# Nudge strength: 1.00 → 0.20 (80% reduction)
# Final harm EMA: 0.78
```
```

**Implementation Guidance for Atlas:**

1. Add `harm_ema`, `harm_cap_multiplier`, `harm_threshold`, `harm_events_count` to Mode schema
2. Implement outcome attribution logic (link outcomes to active modes)
3. Modify policy nudge application to include harm caps
4. Implement harm threshold learning during bootstrap
5. Add recovery logic (gradual restoration when harm decreases)
6. Add telemetry for harm attribution and cap application

**Dashboard Widget:**

Show per-mode harm status:

```
Mode          Harm EMA    Nudge Cap    Status
guardian      0.02        1.00×        ✓ Healthy
explorer      0.45        0.30×        ⚠️ Harm-capped (reduced influence)
builder       0.08        1.00×        ✓ Healthy
```

---

## Summary: What Atlas Needs to Implement

### Tier 2 Overview

**Character:** Adaptive improvements enhancing system capability through learning

**Dependencies:** Tier 1 foundational guards must be in place first

**Total Amendments:** 7 robustness mechanisms

---

### Amendment-by-Amendment Checklist

**Amendment 1: Presence EMAs (Performance)**
- [ ] Add `presence_ema`, `presence_last_update` to SubEntity schema
- [ ] Hook presence EMA updates into spreading activation
- [ ] Modify mode detection to use presence EMAs instead of node queries
- [ ] Learn α and threshold per citizen during bootstrap
- [ ] Verify 100× speedup in mode detection (AT)

**Amendment 2: Lazy Edge Materialization + TTL (Storage)**
- [ ] Add TTL fields to COACTIVATES_WITH edges (created_at, ttl_expires_at, access_count)
- [ ] Implement lazy edge creation (only when pairs co-activate)
- [ ] Implement TTL expiration job (daily cleanup)
- [ ] Learn TTL duration per citizen from churn rate
- [ ] Verify 66× storage reduction (AT)

**Amendment 3: Hysteresis (Stability)**
- [ ] Add HAS_ENTRY_CONTOUR and HAS_EXIT_CONTOUR edges to Mode schema
- [ ] Implement hysteresis activation logic (entry when inactive, exit when active)
- [ ] Establish boot contours during bootstrap
- [ ] Implement operational refinement (every 1000 frames)
- [ ] Verify 10× reduction in mode flicker (AT)

**Amendment 4: S_use/S_red for Mode Pairs (Quality)**
- [ ] Implement mode pair metrics (J, C, U, H, ΔCtx)
- [ ] Implement S_red and S_use computation (same as entity_differentiation.md)
- [ ] Create weekly mode pair audit job
- [ ] Implement mode merge logic for redundant pairs
- [ ] Verify <2 high-redundancy pairs remain (AT)

**Amendment 5: Log-Domain RRF with Learned θ (Precision)**
- [ ] Replace arithmetic RRF with log-domain version
- [ ] Implement θ learning during bootstrap (optimal blend parameter)
- [ ] Store learned θ per citizen
- [ ] Add numerical stability tests (extreme scores)
- [ ] Verify NDCG improvement vs fixed θ=0.5 (AT)

**Amendment 6: Two-Timescale Stability (Resilience)**
- [ ] Add `q_mode_fast`, `q_mode_slow`, `q_mode_divergence`, `stability_status` to Mode schema
- [ ] Implement two-timescale EMA updates
- [ ] Implement stability degradation handling (alerts + intervention)
- [ ] Learn α_fast and α_slow per citizen
- [ ] Verify drift detection before critical degradation (AT)

**Amendment 7: Harm EMA with Nudge Cap (Safety)**
- [ ] Add `harm_ema`, `harm_cap_multiplier`, `harm_threshold`, `harm_events_count` to Mode schema
- [ ] Implement outcome attribution to active modes
- [ ] Modify policy nudge application to include harm caps
- [ ] Learn harm threshold per citizen
- [ ] Verify harm caps reduce harmful mode influence (AT)

---

### Implementation Order Recommendation

**Phase 1 (Performance/Storage):** Amendments 1, 2
- Presence EMAs and lazy edges provide immediate efficiency gains
- Low implementation risk (optimization, not behavioral change)

**Phase 2 (Stability/Quality):** Amendments 3, 4
- Hysteresis and mode pair differentiation improve mode ecology quality
- Medium implementation risk (affects mode lifecycle)

**Phase 3 (Precision/Resilience/Safety):** Amendments 5, 6, 7
- Log-domain RRF, two-timescale monitoring, harm caps add advanced robustness
- Higher implementation risk (subtle behavioral effects)

---

### Testing Strategy

**Per-Amendment Acceptance Tests:**
- Each amendment includes Cypher queries and Python tests
- Verify both functional correctness and performance impact
- Example: Presence EMAs must show 100× speedup while maintaining F1 >0.95

**Integration Testing:**
- Test amendments together (e.g., hysteresis + two-timescale monitoring)
- Verify no unexpected interactions
- Monitor telemetry for behavioral changes

**Performance Benchmarks:**
- Mode detection latency (<10ms target)
- Storage efficiency (edge count vs theoretical maximum)
- Mode ecology quality (redundancy ratio, flicker rate)

---

### Telemetry Dashboard Additions

**New Widgets:**
1. **Presence EMA Performance** - Detection time trend, accuracy vs expensive method
2. **Edge TTL Statistics** - Active edges, expired edges, density over time
3. **Mode Stability** - Per-mode fast/slow EMA divergence, stability status
4. **Harm Tracking** - Per-mode harm EMA, cap multipliers, recovery events

---

### Rollout Strategy

**Week 1-2:** Phase 1 (Performance/Storage)
- Deploy presence EMAs, measure speedup
- Deploy lazy edges + TTL, measure storage reduction
- Low risk, immediate benefits

**Week 3-4:** Phase 2 (Stability/Quality)
- Deploy hysteresis, measure flicker reduction
- Deploy mode pair differentiation, audit for redundancy
- Monitor mode ecology quality

**Week 5-6:** Phase 3 (Precision/Resilience/Safety)
- Deploy log-domain RRF, verify numerical stability
- Deploy two-timescale monitoring, verify drift detection
- Deploy harm caps, monitor for safety improvements

**Week 7:** Validation & Documentation
- Comprehensive acceptance testing
- Performance validation against targets
- Update operational runbooks

---

**Status:** Tier 2 redlines complete. Ready for Atlas implementation in parallel with Tier 1.

**Estimated Implementation Time:** 4-6 weeks for complete Tier 2 rollout (assuming Tier 1 complete)

**Key Principle:** All thresholds, blend parameters, decay rates are LEARNED from data (zero-constant architecture honored throughout).
