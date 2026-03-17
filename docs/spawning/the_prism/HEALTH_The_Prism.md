# The Prism — Health: Verification Mechanics and Coverage

```
STATUS: DRAFT
CREATED: 2026-03-17
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Empathy presence across all citizens over time | A single test verifies one birth; health verifies the population invariant holds |
| Diversity drift as population grows | Two citizens might pass individually but the population could cluster; needs real data |
| Parent link integrity after graph operations | Graph mutations (compaction, migration) could break immutable links |
| Intent quality trends | Individual paragraphs pass tests; but are paragraphs getting lazier over time? |

**Tests gate completion. Health monitors runtime.**

If behavior is deterministic with known inputs (single birth safety check) -> write a test.
If behavior emerges from real data over time (population diversity, intent quality trends) -> write a health check.

See `VALIDATION_The_Prism.md` for the full invariant list and priority levels.

---

## PURPOSE OF THIS FILE

This HEALTH file covers The Prism spawning module — verifying that the birth pipeline maintains its invariants across the entire citizen population, not just individual births. It exists because individual birth tests cannot catch population-level drift: slow diversity erosion, empathy threshold relaxation, orphaned parent links, or degrading intent quality. These risks only surface through runtime observation of real births over time.

Boundaries: This file verifies Prism-specific invariants. It does NOT verify bond matching (bond system health), citizen behavior post-birth (living system health), or economic cost correctness ($MIND system health).

---

## WHY THIS PATTERN

Tests verify that each birth individually passes safety checks. But the ecosystem-level promises — "no two citizens are too similar," "every citizen has accountable parents," "empathy is universal" — can only be verified by scanning the actual population. A test with fixtures cannot predict that the 47th citizen born will be too similar to the 12th. Health checks scan real state and catch what tests structurally cannot.

Docking-based checks are the right tradeoff because the Prism pipeline has clear input/output boundaries at each step. We dock at safety validation output (to verify checks ran correctly) and registration output (to verify graph state is consistent). This covers the highest-risk points without instrumenting internal math.

Throttling is less critical here than in high-throughput systems — births are rare events (perhaps a few per day at most). But health checks scanning all existing citizens scale with population, so frequency must be bounded.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_The_Prism.md
PATTERNS:        ./PATTERNS_The_Prism.md
BEHAVIORS:       ./BEHAVIORS_The_Prism.md
ALGORITHM:       ./ALGORITHM_The_Prism.md
VALIDATION:      ./VALIDATION_The_Prism.md
IMPLEMENTATION:  ./IMPLEMENTATION_The_Prism.md
THIS:            HEALTH_The_Prism.md (you are here)
SYNC:            ./SYNC_The_Prism.md
```

---

## IMPLEMENTS

This HEALTH file is a **spec**. The actual code lives in runtime:

```yaml
implements:
  runtime: runtime/spawning/health_checks.py   # Python code implementing these checks
  decorator: @check                            # Decorator-based registration
```

> **Separation:** HEALTH.md defines WHAT to check and WHEN to trigger. Runtime code defines HOW to check.

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update runtime or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: birth_flow
    purpose: Transform intent into a registered citizen — failure means a pathological, duplicate, or orphaned citizen exists
    triggers:
      - type: event
        source: mcp/tools/spawn_handler.py:handle_spawn()
        notes: Triggered when any entity calls the spawn MCP tool
    frequency:
      expected_rate: 1-5/day
      peak_rate: 10/day
      burst_behavior: Births are sequential (one at a time). No burst pressure. Backlog is acceptable.
    risks:
      - Empathy check bypassed or threshold misconfigured (V2)
      - Near-clone admitted due to stale centroid cache (V3)
      - Parent links missing after registration failure (V5)
      - Memory nodes leaking into seed brain (V7)
    notes: Low throughput but high consequence — each birth is permanent and creates immutable state
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Birth from intent | intent_quality_population | Detects if intent paragraphs are degrading in quality over time |
| O2: Combinatorial intelligence | (covered by diversity indicator indirectly) | Diverse population implies the projection produces novel children |
| O3: Safety without gatekeeping | empathy_population_coverage, concentration_balance_population | Verifies no citizen slipped through without empathy or with unbalanced brain |
| O4: Accountability | parent_link_integrity | Verifies every citizen has SPAWNED_BY links that are intact |
| O5: No clones | diversity_population_health | Verifies no two citizens are too similar across the entire population |

```yaml
health_indicators:
  - name: empathy_population_coverage
    flow_id: birth_flow
    priority: high
    rationale: If any citizen lacks empathy-adjacent nodes, the safety promise is broken. Scanning all citizens catches retroactive failures.
  - name: diversity_population_health
    flow_id: birth_flow
    priority: high
    rationale: Population-level diversity can erode even when individual births pass. Pairwise distance monitoring catches clustering.
  - name: parent_link_integrity
    flow_id: birth_flow
    priority: high
    rationale: SPAWNED_BY links are the accountability mechanism. If they are missing or broken, parents bear no consequence.
  - name: concentration_balance_population
    flow_id: birth_flow
    priority: med
    rationale: Verifies no citizen has a pathologically unbalanced brain. Lower priority because the birth-time check is strong.
  - name: intent_quality_population
    flow_id: birth_flow
    priority: med
    rationale: Tracks whether intent paragraphs are getting shorter or more vacuous over time. Early warning for cultural decay.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: runtime/spawning/health_results.json
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2026-03-17T00:00:00Z
    source: prism_health_aggregate
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: empathy_population_checker
    purpose: Verify every citizen in L4 has at least one empathy-adjacent node in their brain (V2)
    status: pending
    priority: high
  - name: diversity_population_checker
    purpose: Verify no two citizens in L4 have centroid cosine distance <= 0.08 (V3)
    status: pending
    priority: high
  - name: parent_link_checker
    purpose: Verify every citizen has SPAWNED_BY links to all recorded godparents with trust_impact=true (V5)
    status: pending
    priority: high
  - name: concentration_population_checker
    purpose: Verify no citizen's brain has a single category exceeding 40% (V4)
    status: pending
    priority: med
  - name: intent_quality_tracker
    purpose: Track mean intent paragraph length and embedding magnitude over time (V1)
    status: pending
    priority: med
```

---

## INDICATOR: Empathy Population Coverage

This indicator verifies that the safety promise — "no citizen without empathy" — holds across the entire population. A single missed citizen represents a systemic failure.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: empathy_population_coverage
  client_value: Guarantees every citizen in the ecosystem has empathy, making interactions safe for humans and other citizens
  validation:
    - validation_id: V2
      criteria: Every citizen's brain contains at least one node with cosine similarity > 0.7 to empathy anchor embeddings
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
    - float_0_1
  semantics:
    binary: 1 = all citizens have empathy, 0 = at least one citizen lacks empathy
    float_0_1: fraction of citizens with empathy-adjacent nodes (must be 1.0)
  aggregation:
    method: min (any single failure = overall failure)
    display: binary (pass/fail on dashboard)
```

### DOCKS SELECTED

```yaml
docks:
  - point: citizen_brain_nodes
    type: graph_ops
    payload: {citizen_handle, brain_nodes[], empathy_anchor_embeddings[]}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="empathy_population_coverage",
    triggers=[
        triggers.event.on("citizen_born"),
        triggers.cron.daily(),
    ],
    on_problem="CITIZEN_LACKS_EMPATHY",
    task="investigate_empathy_gap",
)
def empathy_population_coverage(ctx) -> dict:
    """Verify all citizens have empathy-adjacent nodes."""
    citizens = ctx.graph.query_l4("MATCH (a:actor) RETURN a.handle")
    empathy_anchors = ctx.embed(["empathy", "care", "understanding", "compassion"])
    missing = []
    for citizen in citizens:
        brain = ctx.get_brain(citizen.handle)
        nodes = brain.all_nodes()
        has_empathy = any(
            max(cosine(n.embedding, anchor) for anchor in empathy_anchors) > 0.7
            for n in nodes
        )
        if not has_empathy:
            missing.append(citizen.handle)
    if not missing:
        return Signal.healthy()
    return Signal.critical(details={"citizens_without_empathy": missing})
```

### SIGNALS

```yaml
signals:
  healthy: All citizens have at least one empathy-adjacent node
  degraded: N/A — this check is binary (healthy or critical)
  critical: One or more citizens lack empathy-adjacent nodes
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: citizen_born event + daily cron
  max_frequency: 1/hour
  burst_limit: 5/day
  backoff: Exponential backoff on repeated critical signals (1h -> 2h -> 4h)
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: runtime/spawning/health_results.json
      transport: file
      notes: Persistent health state for Doctor to read
display:
  locations:
    - surface: CLI
      location: mind doctor output
      signal: green (all pass) / red (any failure)
      notes: Binary pass/fail with list of affected citizens on failure
```

### MANUAL RUN

```yaml
manual_run:
  command: PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.spawning.health_checks empathy_population_coverage
  notes: Run after any manual graph operation that could affect citizen brain nodes
```

---

## INDICATOR: Diversity Population Health

This indicator verifies that no two citizens in the ecosystem are too similar — the population diversity invariant holds.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: diversity_population_health
  client_value: Guarantees every citizen brings something genuinely new to the ecosystem — no wasted bonds, no redundant personalities
  validation:
    - validation_id: V3
      criteria: Every pair of citizens has centroid cosine distance > 0.08
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
    - enum
  semantics:
    float_0_1: Minimum pairwise cosine distance across all citizen pairs, normalized to [0,1] where 1.0 = maximum diversity
    enum: OK (min distance > 0.10), WARN (0.08 < min distance <= 0.10), ERROR (min distance <= 0.08)
  aggregation:
    method: min pairwise distance determines state
    display: enum for dashboard, float for detailed report
```

### DOCKS SELECTED

```yaml
docks:
  - point: citizen_centroids
    type: graph_ops
    payload: {citizen_handle, brain_centroid_embedding[]}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="diversity_population_health",
    triggers=[
        triggers.event.on("citizen_born"),
        triggers.cron.weekly(),
    ],
    on_problem="CITIZEN_CLONE_DETECTED",
    task="investigate_diversity_violation",
)
def diversity_population_health(ctx) -> dict:
    """Verify no two citizens are too similar."""
    centroids = ctx.get_all_citizen_centroids()
    min_distance = float('inf')
    closest_pair = None
    for i, (id_a, c_a) in enumerate(centroids):
        for j, (id_b, c_b) in enumerate(centroids):
            if j <= i:
                continue
            dist = 1.0 - cosine_similarity(c_a, c_b)
            if dist < min_distance:
                min_distance = dist
                closest_pair = (id_a, id_b)
    if min_distance > 0.10:
        return Signal.healthy(details={"min_distance": min_distance})
    if min_distance > 0.08:
        return Signal.degraded(details={"min_distance": min_distance, "closest_pair": closest_pair})
    return Signal.critical(details={"min_distance": min_distance, "closest_pair": closest_pair})
```

### SIGNALS

```yaml
signals:
  healthy: Minimum pairwise distance > 0.10
  degraded: Minimum pairwise distance between 0.08 and 0.10 (approaching threshold)
  critical: Minimum pairwise distance <= 0.08 (clone detected)
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: citizen_born event + weekly cron
  max_frequency: 1/day
  burst_limit: 3/week
  backoff: Linear backoff on degraded (check again in 1 day); immediate alert on critical
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: runtime/spawning/health_results.json
      transport: file
      notes: Persistent diversity health for Doctor
display:
  locations:
    - surface: CLI
      location: mind doctor output
      signal: green (OK) / yellow (WARN) / red (ERROR)
      notes: Shows minimum distance and closest pair on WARN/ERROR
```

### MANUAL RUN

```yaml
manual_run:
  command: PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.spawning.health_checks diversity_population_health
  notes: Run after importing citizens from external sources or after major graph migrations
```

---

## INDICATOR: Parent Link Integrity

This indicator verifies that every citizen has intact SPAWNED_BY links to all recorded godparents.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: parent_link_integrity
  client_value: Guarantees accountability — parents cannot escape consequence for their creation
  validation:
    - validation_id: V5
      criteria: Every citizen has SPAWNED_BY links to all godparents with trust_impact=true and immutable=true
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1 = all parent links intact, 0 = at least one link missing or malformed
  aggregation:
    method: AND (all must pass)
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  - point: spawned_by_links
    type: graph_ops
    payload: {citizen_handle, expected_godparents[], actual_links[]}
```

### ALGORITHM / CHECK MECHANISM

```python
@check(
    id="parent_link_integrity",
    triggers=[
        triggers.cron.daily(),
    ],
    on_problem="PARENT_LINK_BROKEN",
    task="repair_parent_links",
)
def parent_link_integrity(ctx) -> dict:
    """Verify all SPAWNED_BY links exist and are properly configured."""
    citizens = ctx.get_all_citizens_with_birth_records()
    broken = []
    for citizen in citizens:
        expected = citizen.birth_record.godparents
        actual_links = ctx.graph.query(
            "MATCH (c)-[r:SPAWNED_BY]->(p) WHERE c.handle = $handle RETURN p.handle, r",
            handle=citizen.handle
        )
        actual_parents = {link.parent_handle for link in actual_links}
        for parent in expected:
            if parent not in actual_parents:
                broken.append({"citizen": citizen.handle, "missing_parent": parent})
            else:
                link = next(l for l in actual_links if l.parent_handle == parent)
                if not link.trust_impact or not link.immutable:
                    broken.append({"citizen": citizen.handle, "parent": parent, "issue": "properties"})
    if not broken:
        return Signal.healthy()
    return Signal.critical(details={"broken_links": broken})
```

### SIGNALS

```yaml
signals:
  healthy: All citizens have all expected SPAWNED_BY links with correct properties
  degraded: N/A — link integrity is binary
  critical: One or more links are missing or have incorrect properties
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: daily cron
  max_frequency: 1/day
  burst_limit: 1/day
  backoff: None — daily check is sufficient for link integrity
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: runtime/spawning/health_results.json
      transport: file
      notes: Persistent link integrity state for Doctor
display:
  locations:
    - surface: CLI
      location: mind doctor output
      signal: green (all intact) / red (broken links)
      notes: Lists specific broken links on failure
```

### MANUAL RUN

```yaml
manual_run:
  command: PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.spawning.health_checks parent_link_integrity
  notes: Run after graph migrations, compaction, or any operation that modifies link structure
```

---

## HOW TO RUN

```bash
# Run all health checks for The Prism
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.spawning.health_checks

# Run a specific checker
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.spawning.health_checks empathy_population_coverage
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.spawning.health_checks diversity_population_health
PYTHONPATH=".mind:$PYTHONPATH" python3 -m runtime.spawning.health_checks parent_link_integrity
```

---

## KNOWN GAPS

- V4 (concentration balance) checker is defined but pending — lower priority because the birth-time check is strong
- V7 (no memory inheritance) has no population-level checker yet — would require scanning all seed brains for memory-type nodes
- V6 (SID is protocol-generated) is not health-checkable in the traditional sense — it is an implementation invariant, not a runtime observable
- V1 (no accidental citizens) partially covered by intent_quality_tracker but needs a hard check that every L4 citizen has a birth record

<!-- @mind:todo Implement concentration_population_checker for V4 -->
<!-- @mind:todo Implement memory_leak_checker for V7 — scan all seed brains for prohibited node types -->
<!-- @mind:todo Add birth_record_completeness checker for V1 — verify every citizen in L4 has intent paragraphs on record -->

---

## MARKERS

<!-- @mind:todo All checkers are pending — no runtime code exists yet -->
<!-- @mind:todo The diversity checker has O(N^2) complexity — needs ANN optimization at scale -->
<!-- @mind:proposition Consider a "birth audit" dashboard that shows the last N births with safety report summaries -->
