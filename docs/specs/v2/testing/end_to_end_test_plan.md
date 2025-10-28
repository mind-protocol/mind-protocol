---
title: End-to-End Test Plan - Stimulus to Response
status: draft
owner: @luca + @felix
created: 2025-10-25
summary: >
  Comprehensive test specification from external signal arrival through stimulus
  processing, energy injection, traversal, entity activation, context generation,
  response, and TRACE reinforcement. Each step has verification criteria, expected
  behaviors, failure modes, and observable metrics.
---

# End-to-End Test Plan: Stimulus → Injection → Response → Learning

## Overview

Complete consciousness pipeline testing from external reality to learned structure.

**Pipeline stages:**
1. Signal arrival → Stimulus processing (burst detection, coalescing)
2. Stimulus → Retrieval (entropy-aware search)
3. Retrieval → Energy injection (dual-channel: floor + amplifier)
4. Injection → Graph activation (nodes gain energy)
5. Activation → Entity derivation (E_entity from members)
6. Entity → Traversal (two-scale: between + within)
7. Traversal → Working Memory (entity-first selection)
8. WM → Context generation (identity + thought via Forged Identity)
9. Context → LLM response
10. Response → TRACE parsing (reinforcement marks + formations)
11. TRACE → Weight updates (context-aware, cohort-local)
12. Weights → Identity evolution (structure shapes future)

**Test philosophy:** Each stage tests substrate behavior, not implementation details. Observable via telemetry events.

---

## Stage 1: Signal Arrival → Stimulus Processing

### What We're Testing

External signal transforms into stimulus with metadata (burst_id, source, timestamp, content).

### Test Cases

#### TC1.1: Single Signal Processing

**Input:**
```json
{
  "source": "user_message",
  "content": "Fix the websocket timeout error",
  "timestamp_ms": 1730074800000
}
```

**Expected behavior:**
- Parse signal → stimulus object
- Assign burst_id (new burst, no recent signals)
- Extract embeddings (if content-based)
- Emit `stimulus.received` event

**Verification:**
```cypher
MATCH (s:Stimulus {burst_id: "burst_xyz"})
RETURN s.content, s.source, s.timestamp_ms
```

**Observable metrics:**
- `stimulus.received` event appears in telemetry
- Burst_id is unique
- Timestamp matches input ± processing latency

**Failure modes:**
- Missing embeddings (if embedding service down)
- Duplicate burst_id (collision)
- Timestamp drift (clock skew)

---

#### TC1.2: Burst Coalescing (Rapid Signals)

**Input:** 4 filesystem events within 200ms
```json
[
  {"source": "filesystem", "content": "file_a.py modified", "timestamp_ms": 1000},
  {"source": "filesystem", "content": "file_b.py modified", "timestamp_ms": 1080},
  {"source": "filesystem", "content": "file_c.py modified", "timestamp_ms": 1150},
  {"source": "filesystem", "content": "file_d.py modified", "timestamp_ms": 1190}
]
```

**Expected behavior:**
- All 4 signals coalesced into SINGLE burst_id
- Combined content or representative summary
- Timestamp = first signal in burst

**Verification:**
```python
# Check telemetry
burst_events = get_events(type="stimulus.received", timerange=[1000, 1200])
assert len(burst_events) == 1, "Should coalesce to single burst"
assert burst_events[0]["signal_count"] == 4
```

**Observable metrics:**
- `stimulus.coalesced` event with count=4
- Burst window duration (should be <300ms)
- Content synthesis quality

**Failure modes:**
- Over-coalescing (unrelated signals merged)
- Under-coalescing (burst fragmented)
- Content truncation (if too long)

---

## Stage 2: Stimulus → Retrieval (Entropy-Aware)

### What We're Testing

Stimulus embedding queries graph for semantically similar nodes. Retrieval count adapts to stimulus specificity (entropy).

### Test Cases

#### TC2.1: Narrow Stimulus (Low Entropy)

**Input:**
```
Stimulus: "Fix connection_timeout in websocket_server.py line 234"
Entropy: LOW (very specific)
```

**Expected behavior:**
- Retrieve 3-5 highly similar nodes (precision mode)
- High similarity scores (>0.7)
- Focus on "websocket", "connection_timeout", "line 234"

**Verification:**
```python
matches = retrieval_result.candidates
assert len(matches) <= 5, "Narrow stimulus → few matches"
assert all(m.similarity > 0.7 for m in matches), "High precision"
assert any("websocket" in m.content.lower() for m in matches)
```

**Observable metrics:**
- `retrieval.completed` event with match_count, avg_similarity, entropy_score
- Latency <50ms (few matches)

**Failure modes:**
- Too many matches (entropy miscalculated)
- Low similarity (embedding quality issue)
- Missing obvious node (coverage gap)

---

#### TC2.2: Broad Stimulus (High Entropy)

**Input:**
```
Stimulus: "How does the system work?"
Entropy: HIGH (very general)
```

**Expected behavior:**
- Retrieve 15-30 diverse nodes (coverage mode)
- Lower similarity threshold (>0.4)
- Spread across multiple entities/topics

**Verification:**
```python
matches = retrieval_result.candidates
assert len(matches) >= 15, "Broad stimulus → many matches"
assert len(set(m.entity_id for m in matches)) >= 5, "Diverse entities"
```

**Observable metrics:**
- `retrieval.completed` with higher match_count
- Semantic diversity (distance between matches)

**Failure modes:**
- Clustering (all matches from one topic)
- Redundancy (near-duplicate nodes)
- Query timeout (too many candidates)

---

## Stage 3: Retrieval → Energy Injection (Dual-Channel)

### What We're Testing

Retrieved nodes receive energy via floor channel (under-active prioritized) + amplifier channel (strong matches boosted). Threshold is activation floor, NOT cap.

### Test Cases

#### TC3.1: Cold Graph Injection (High Coldness)

**Setup:**
- Graph mostly inactive: `E_i << Θ_i` for most nodes
- Coldness C = average(Θ - E) = 25 (high)

**Input:**
```
Retrieved candidates: 10 nodes
  - All have E_i < Θ_i (below threshold)
  - Similarities: [0.9, 0.8, 0.7, 0.6, 0.5, ...]
Budget B = 100 energy
```

**Expected behavior:**
- Adaptive split: λ → 0.8 (prioritize floor channel)
- Floor channel: 80 energy → fills gaps
- Amplifier channel: 20 energy → boosts top matches
- **All nodes should reach or exceed threshold** for propagation

**Verification:**
```python
injection_result = inject(candidates, budget=100, rho=0.95)

# Check split
assert injection_result.lambda_used >= 0.7, "Cold graph → high floor bias"

# Check node activation
for node in injection_result.nodes:
    new_E = node.E_before + node.delta_E
    assert new_E >= node.theta * 0.9, "Should warm nodes near/above threshold"
```

**Observable metrics:**
- `injection.completed` event with `lambda_used`, `coldness`, `floor_energy`, `amplifier_energy`
- Per-node `delta_E` distribution

**Failure modes:**
- Under-injection (nodes stay below threshold → no propagation)
- Over-injection (exceeds budget or safety caps)
- Uneven distribution (one node gets all energy)

---

#### TC3.2: Hot Graph with Strong Match (Low Coldness, High Concentration)

**Setup:**
- Graph mostly active: `E_i > Θ_i` for most nodes
- Coldness C = 2 (low)
- One dominant match: similarity = 0.95, others <0.3
- Concentration H = 0.85 (high)

**Input:**
```
Retrieved candidates: 8 nodes
  - Top node: E=65, Θ=30, sim=0.95
  - Others: E>Θ, sim<0.3
Budget B = 100
```

**Expected behavior:**
- Adaptive split: λ → 0.4 (prioritize amplifier)
- Floor channel: 40 energy → minimal (little gap)
- Amplifier channel: 60 energy → boosts dominant match **above threshold**
- Top node gets ~50-60 energy (strong amplification)

**Verification:**
```python
injection_result = inject(candidates, budget=100, rho=1.02)

assert injection_result.lambda_used <= 0.5, "Hot + concentrated → amplifier bias"

top_node = max(candidates, key=lambda n: n.similarity)
assert top_node.delta_E >= 50, "Dominant match gets amplified"
assert top_node.E_after > top_node.theta, "Above threshold for propagation"
```

**Observable metrics:**
- Lambda close to 0.4
- Herfindahl index H > 0.8
- Top node gets >50% of amplifier budget

**Failure modes:**
- Capped at threshold (CRITICAL BUG - prevents propagation)
- Over-distribution (energy wasted on weak matches)
- Budget imbalance (floor gets zero, or amplifier gets zero)

---

#### TC3.3: Health Modulation (Criticality Gates)

**Setup:**
- Supercritical graph: ρ = 1.15 (too much activation)

**Input:**
```
Budget B_base = 100
Health: ρ = 1.15
```

**Expected behavior:**
- Health modulation: f(ρ) < 1.0 (damping)
- Effective budget: B = B_base × f(ρ) ≈ 70-80
- Prevent overdrive

**Verification:**
```python
injection_result = inject(candidates, budget_base=100, rho=1.15)

assert injection_result.budget_used < 100, "Supercritical → damping"
assert injection_result.health_factor < 1.0
```

**Observable metrics:**
- `injection.health_modulated` with ρ, f(ρ), budget_before, budget_after

**Failure modes:**
- No damping (graph explodes)
- Over-damping (subcritical graph starved)
- Oscillation (alternating over/under)

---

## Stage 4: Injection → Graph Activation

### What We're Testing

Injected energy appears on nodes. Single-energy substrate preserved. Conservation maintained.

### Test Cases

#### TC4.1: Energy Conservation

**Setup:**
- 10 nodes receive energy
- Total budget B = 100

**Expected behavior:**
- ΣΔE_i ≈ B (within 1% tolerance)
- No energy created or destroyed
- Node energies updated atomically

**Verification:**
```python
before_total = sum(n.E for n in graph.nodes)
inject_result = inject(candidates, budget=100)
after_total = sum(n.E for n in graph.nodes)

delta_total = after_total - before_total
assert abs(delta_total - 100) < 1.0, "Conservation violated"
```

**Observable metrics:**
- `injection.conservation` event with before, after, budget, error

**Failure modes:**
- Energy leak (Σδ < B)
- Energy creation (Σδ > B)
- Partial application (some nodes updated, others not)

---

#### TC4.2: Threshold Crossing Triggers Activation

**Setup:**
- Node A: E=28, Θ=30 (below threshold, inactive)
- Inject 5 energy → E=33 (above threshold, active)

**Expected behavior:**
- Node A crosses threshold
- Emit `node.flip` event (inactive → active)
- Node A joins active frontier

**Verification:**
```python
node_a = graph.get_node("node_a")
assert node_a.E == 28
assert not node_a.is_active

inject(node_a, delta_E=5)

assert node_a.E == 33
assert node_a.is_active
assert "node.flip" in telemetry_events
```

**Observable metrics:**
- `node.flip` event with node_id, E_before, E_after, threshold

**Failure modes:**
- No flip event (observability gap)
- Threshold miscalculated
- Double-flip (event emitted twice)

---

## Stage 5: Activation → Entity Derivation

### What We're Testing

Entity energy derives from member nodes (single-energy substrate). Formula: `E_entity = Σ m̃_iE × log(1 + max(0, E_i - Θ_i))`.

### Test Cases

#### TC5.1: Entity Activation from Member Energy

**Setup:**
- Entity "websocket_debugging" with 5 members
- Members: [E₁=40/Θ=30, E₂=35/Θ=30, E₃=25/Θ=30, E₄=20/Θ=30, E₅=15/Θ=30]
- MEMBER_OF weights: [0.4, 0.3, 0.2, 0.1, 0.0] (normalized)

**Expected behavior:**
- Only surplus energy (E > Θ) contributes
- Contributors: nodes 1, 2 (above threshold)
- E_entity = 0.4×log(1+10) + 0.3×log(1+5) + 0 + 0 + 0
- E_entity ≈ 0.4×2.4 + 0.3×1.8 ≈ 1.5

**Verification:**
```python
entity = graph.get_entity("websocket_debugging")
entity.refresh_activation()

assert 1.4 < entity.E < 1.6, "Entity energy from surplus only"
assert entity.E > 0, "Has active members"
```

**Observable metrics:**
- `entity.activation.updated` with E_entity, active_member_count, surplus_total

**Failure modes:**
- Sub-threshold leakage (nodes below Θ contribute)
- Single-node domination (one node = 100% of entity energy)
- Zero energy despite active members

---

#### TC5.2: Entity Threshold Crossing

**Setup:**
- Entity threshold Θ_entity = 1.0 (learned from cohort)
- Entity energy starts at 0.8 (below threshold)
- Member energy increases → entity energy → 1.2 (above threshold)

**Expected behavior:**
- Entity crosses threshold
- Emit `subentity.flip` event
- Entity joins active entity set for traversal

**Verification:**
```python
entity = graph.get_entity("runtime_engineering")
assert entity.E == 0.8
assert not entity.is_active

# Inject energy into members
inject_to_members(entity, total_energy=20)
entity.refresh_activation()

assert entity.E > 1.0
assert entity.is_active
assert "subentity.flip" in telemetry_events
```

**Observable metrics:**
- `subentity.flip` with entity_id, E_before, E_after, threshold

**Failure modes:**
- No flip despite crossing
- Flip thrashing (rapid on/off)
- Threshold drift (Θ changes unexpectedly)

---

## Stage 6: Entity → Traversal (Two-Scale)

### What We're Testing

Traversal operates in two scales: between entities (choose which concern) → within entities (reason through concern).

### Test Cases

#### TC6.1: Between-Entity Boundary Selection

**Setup:**
- Current entity: "websocket_debugging" (active, high energy)
- Candidate exits: ["code_investigation", "performance_analysis", "documentation"]
- RELATES_TO links with learned ease:
  - websocket_debugging → code_investigation: ease=0.8 (high, frequently useful)
  - websocket_debugging → performance_analysis: ease=0.4 (medium)
  - websocket_debugging → documentation: ease=0.2 (low, rare transition)

**Expected behavior:**
- Rank boundaries by ease × current relevance
- Choose "code_investigation" (highest ease)
- OR stay within "websocket_debugging" if internal energy still high

**Verification:**
```python
frame_result = run_frame(dt=1.0)

if frame_result.entity_transition:
    assert frame_result.target_entity in ["code_investigation", "websocket_debugging"]
    assert frame_result.boundary_ease > 0.5, "Should pick high-ease exit"
```

**Observable metrics:**
- `subentity.boundary.summary` with source, target, ease, energy_flow

**Failure modes:**
- Random selection (ease ignored)
- Stuck in entity (never exits despite low energy)
- Excessive jumping (entity thrashing)

---

#### TC6.2: Within-Entity Stride Selection

**Setup:**
- Current entity: "code_investigation" (active)
- Active node: "recent_code_changes" (E=45, active frontier)
- Outgoing links within entity:
  - → "git_diff_analysis" (weight=0.9, goal_affinity=0.8)
  - → "file_inspection" (weight=0.6, goal_affinity=0.5)
  - → "timeline_review" (weight=0.3, goal_affinity=0.3)

**Expected behavior:**
- Compute cost = 1 / (ease × goal_affinity × emotion_gates)
- Pick min-cost = "git_diff_analysis"
- Stage ΔE transfer proportional to source energy

**Verification:**
```python
stride_events = get_events(type="stride.exec", timerange=frame_window)

assert len(stride_events) >= 1
top_stride = stride_events[0]
assert top_stride["dst"] == "git_diff_analysis"
assert top_stride["dE"] > 0
```

**Observable metrics:**
- `stride.exec` with src, dst, dE, ease, goal_affinity, cost

**Failure modes:**
- Wrong destination (cost miscalculated)
- Zero energy transfer (ΔE=0)
- Conservation violated (energy created)

---

## Stage 7: Traversal → Working Memory

### What We're Testing

Entity-first WM selects 5-7 entities with highest energy × coherence. Each entity includes top members.

### Test Cases

#### TC7.1: Entity-First WM Selection

**Setup:**
- 15 active entities
- Energy distribution: [50, 45, 40, 35, 30, 25, 20, 15, 10, ...]
- Coherence: all >0.7

**Expected behavior:**
- Select top 5-7 entities by (energy × coherence × quality)
- Emit WM contents with entity summaries + top members

**Verification:**
```python
wm = working_memory.get_current()

assert 5 <= len(wm.entities) <= 7, "WM capacity"
assert all(e.E > 30 for e in wm.entities), "High-energy entities"
```

**Observable metrics:**
- `wm.selection` event with entity_ids, energies, member_counts

**Failure modes:**
- Too many entities (>7, WM overload)
- Too few entities (<3, insufficient context)
- Missing high-energy entity (selection bug)

---

#### TC7.2: Entity Members Included

**Setup:**
- WM entity: "websocket_debugging"
- Entity has 20 members
- WM should include top 3-5 members by energy

**Expected behavior:**
- Entity included in WM
- Top 3-5 members selected
- Members above threshold, ordered by energy

**Verification:**
```python
wm_entity = wm.get_entity("websocket_debugging")

assert wm_entity is not None
assert 3 <= len(wm_entity.members) <= 5
assert all(m.E > m.theta for m in wm_entity.members)
```

**Observable metrics:**
- Per-entity member list in WM snapshot

**Failure modes:**
- No members (entity empty)
- All members included (no selection)
- Below-threshold members (noise)

---

## Stage 8: WM → Context Generation (Forged Identity)

### What We're Testing

Context (system) and Input (user) generated from WM entities via exact selection formulas. Zero constants, learned thresholds.

### Test Cases

#### TC8.1: Context Selector (System Prompt)

**Setup:**
- 12 entities in graph
- Stable entities (high weight, low volatility, high quality): 6 entities
- Currently relevant (E > 0 or attribution > 0): 4 of those 6

**Expected behavior:**
- Select 4 entities (stable AND relevant)
- Score via: S^ctx = [w × q × σ × (1-ν)] × max(1, ε + a)
- Allocate tokens via divisor apportionment
- Generate essence per entity

**Verification:**
```python
context = generate_system_prompt(graph, stimulus_context)

# Expect 4-6 entities (stable + relevant)
assert 4 <= context.entity_count <= 6

# Check structural dominance
for entity in context.entities:
    assert entity.weight > entity.learned_stability_threshold
    assert entity.quality > entity.learned_quality_threshold
```

**Observable metrics:**
- `identity.regenerated` event (if structure changed)
- `context.reconstructed` event with entity_ids, scores, tokens_allocated

**Failure modes:**
- All entities selected (no filtering)
- Zero entities (over-filtering)
- Transient entities in identity (volatility not checked)

---

#### TC8.2: Input Selector (User Message)

**Setup:**
- WM contains 5 entities
- Stimulus attributed to 2 entities strongly (a > 0.7)
- Energy distribution: one dominant (ε=0.9), others lower

**Expected behavior:**
- Adaptive K from concentration
- High concentration → K=1 (laser focus)
- Score via: S^inp = ε × (1+a) × (1+z^nov) × (1+λw)
- Select top-K entities
- Allocate tokens via Hamilton

**Verification:**
```python
input_context = generate_input_context(wm, stimulus_context)

# Expect 1-3 entities (energy-dominant)
assert 1 <= input_context.entity_count <= 3

# Check energy dominance
top_entity = input_context.entities[0]
assert top_entity.energy > 0.5, "High-energy entity"
```

**Observable metrics:**
- `context.reconstructed` with K_used, concentration, entity_scores

**Failure modes:**
- K=7 despite single dominant (concentration miscalculated)
- Low-energy entities selected (energy not dominant)
- Structural weight overriding energy (λ too high)

---

#### TC8.3: Essence Extraction (Centroid → Nearest)

**Setup:**
- Entity "runtime_engineering" with 15 members
- Centroid embedding computed from all members
- Nearest member: "test_before_victory" (distance=0.15)

**Expected behavior:**
- Compute centroid from member embeddings
- Find nearest member to centroid
- Return member content as essence

**Verification:**
```python
entity = graph.get_entity("runtime_engineering")
essence = extract_entity_essence(entity)

assert essence == "test_before_victory", "Nearest member to centroid"
assert 0.1 < entity.centroid_distance < 0.2, "Tight cluster"
```

**Observable metrics:**
- Per-entity: centroid_distance, essence_node_id

**Failure modes:**
- Medoid fallback triggered (high spread, distance >0.7)
- Empty entity (no members with embeddings)
- Essence is outlier (not representative)

---

## Stage 9: Context → LLM Response

### What We're Testing

System + user messages sent to LLM. Response generated and returned.

### Test Cases

#### TC9.1: Basic Response Generation

**Input:**
```
System: [5 entity essences from context, 800 tokens]
User: [2 entity essences from input, 200 tokens]
```

**Expected behavior:**
- LLM receives both messages
- Generates response (100-500 tokens)
- Response reflects both identity (system) and current concern (user)

**Verification:**
```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": input_context}
]

response = llm.generate(messages)

assert 100 < len(response.text.split()) < 500
assert response.status == "success"
```

**Observable metrics:**
- LLM latency (ms)
- Token counts (system, user, response)

**Failure modes:**
- LLM timeout
- Context too long (exceeds model limit)
- Empty response

---

## Stage 10: Response → TRACE Parsing

### What We're Testing

Response text parsed for reinforcement marks and formation declarations. Seats allocated via Hamilton apportionment.

### Test Cases

#### TC10.1: Reinforcement Mark Parsing

**Input response:**
```
The websocket timeout [node_connection_analysis: very useful]
occurred because of thread blocking [node_threading_issue: useful].
We should investigate [node_investigation_path: somewhat useful].
```

**Expected behavior:**
- Extract 3 marks with node IDs + usefulness labels
- Map labels to seat counts via Hamilton
  - "very useful" → ~40% of positive pool
  - "useful" → ~35%
  - "somewhat useful" → ~25%
- Separate positive pool (3 marks, total seats)

**Verification:**
```python
trace_result = parse_trace(response)

assert len(trace_result.positive_marks) == 3
assert "node_connection_analysis" in trace_result.marks
assert trace_result.marks["node_connection_analysis"].seats >
       trace_result.marks["node_threading_issue"].seats
```

**Observable metrics:**
- `trace.parsed` event with mark_count, positive_seats, negative_seats

**Failure modes:**
- Missing marks (regex failed)
- Wrong label extraction
- Seat allocation error (Hamilton bug)

---

#### TC10.2: Formation Declaration Parsing

**Input response:**
```
[NODE_FORMATION: Realization]
name: "threading_causes_timeout"
scope: "personal"
description: "Thread blocking causes websocket timeout"
what_i_realized: "The timeout isn't network - it's thread starvation"
context_when_discovered: "While debugging websocket errors"
confidence: 0.85
formation_trigger: "systematic_analysis"
```

**Expected behavior:**
- Parse formation block
- Validate required fields
- Compute formation quality: C×E×N geometric mean
  - Completeness: all required fields present → high
  - Evidence: grounded in debugging context → high
  - Novelty: new connection (threading ↔ timeout) → high
- Create node in graph

**Verification:**
```python
formations = parse_formations(response)

assert len(formations.nodes) >= 1
node_formation = formations.nodes[0]
assert node_formation.name == "threading_causes_timeout"
assert node_formation.quality_score > 0.7, "High C×E×N"
```

**Observable metrics:**
- `formation.created` event with node_id, quality_score, completeness, evidence, novelty

**Failure modes:**
- Missing required field (validation fails)
- Low quality (C or E or N near zero)
- Duplicate name (collision)

---

## Stage 11: TRACE → Weight Updates

### What We're Testing

Context-aware weight updates: entity-local (primary) + global (secondary). Learned split. Cohort z-scores. Negative pool separated.

### Test Cases

#### TC11.1: Entity-Local Weight Update

**Setup:**
- Mark: "node_websocket_analysis" receives 40 seats (very useful)
- Mark context: Entity "websocket_debugging" was active (attribution=0.9)
- Other entities: low attribution (<0.1)

**Expected behavior:**
- Learned split: λ = 0.7 (high attribution mass → prioritize local)
- Local update: 28 seats to "websocket_debugging" entity members
- Global update: 12 seats distributed globally
- Node "websocket_analysis" weight increases significantly

**Verification:**
```python
update_result = apply_trace_weights(mark, context)

assert update_result.local_seats >= 25, "Majority to local entity"
assert update_result.global_seats <= 15

node = graph.get_node("node_websocket_analysis")
weight_delta = node.weight_after - node.weight_before
assert weight_delta > 0.05, "Significant local boost"
```

**Observable metrics:**
- `weights.updated.trace` event with node_id, delta_weight, local_ratio, attribution_mass

**Failure modes:**
- All global (local update ignored)
- All local (global signal lost)
- Negative weight (underflow)

---

#### TC11.2: Cohort-Local Z-Score Normalization

**Setup:**
- Citizen: Felix
- Subdomain: runtime_debugging
- Time window: 14 days
- Historical weights: μ=0.5, σ=0.15

**Expected behavior:**
- New weight update normalized via cohort z-score
- z = (w_new - μ_cohort) / σ_cohort
- Apply z-score bounded update (prevent outliers)

**Verification:**
```python
cohort = get_cohort("felix_runtime_debugging_14d")
update = compute_weight_update(mark, cohort)

assert cohort.mean ≈ 0.5
assert cohort.std ≈ 0.15
assert -3 < update.z_score < 3, "Bounded z-score"
```

**Observable metrics:**
- Per-cohort: mean, std, update_count
- Per-update: z_score, clipped

**Failure modes:**
- No cohort (insufficient data)
- Cohort collapse (all same weight)
- Outlier dominates (z-score unbounded)

---

#### TC11.3: Negative Pool Separation

**Setup:**
- Positive marks: 3 nodes (seats: [40, 30, 20])
- Negative marks: 2 nodes "misleading" (seats: [-30, -20])

**Expected behavior:**
- Separate pools maintained
- Positive seats → positive z-scores → weight increases
- Negative seats → negative z-scores → weight decreases
- Negative impact NOT washed out by positive density

**Verification:**
```python
trace_result = apply_trace(positive_marks, negative_marks)

for mark in positive_marks:
    node = graph.get_node(mark.node_id)
    assert node.weight_delta > 0, "Positive reinforcement"

for mark in negative_marks:
    node = graph.get_node(mark.node_id)
    assert node.weight_delta < 0, "Negative reinforcement"
```

**Observable metrics:**
- `weights.updated.trace` with pool="positive" or "negative"
- Separate seat counts per pool

**Failure modes:**
- Mixed pools (negative treated as low-positive)
- Asymmetric impact (negative has no effect)
- Over-punishment (negative collapses weight to zero)

---

## Stage 12: Weights → Identity Evolution

### What We're Testing

Weight changes reshape entity metrics (stability, quality, weight). Identity regeneration triggered when structure drifts.

### Test Cases

#### TC12.1: Entity Quality Increases from TRACE

**Setup:**
- Entity "runtime_engineering"
- Initial quality: 0.72
- TRACE reinforces 5 members with high seats
- Formation quality (C×E×N) from TRACE: 0.85

**Expected behavior:**
- Entity formation_quality EMA increases
- Combined quality score rises
- Entity moves closer to identity selection threshold

**Verification:**
```python
entity = graph.get_entity("runtime_engineering")
quality_before = entity.formation_quality

apply_trace_updates(marks)
entity.refresh_quality()

assert entity.formation_quality > quality_before
assert entity.combined_quality > 0.75
```

**Observable metrics:**
- Per-entity: formation_quality_ema, combined_quality

**Failure modes:**
- Quality decreases (wrong formula)
- No change (TRACE not feeding quality)
- Quality collapse (geometric mean near zero)

---

#### TC12.2: Identity Regeneration Triggered

**Setup:**
- Identity last generated 2 days ago
- 5 TRACE sessions with high-quality reinforcement
- Stable entity set composition changed >15%

**Expected behavior:**
- Check identity drift (Jaccard similarity <0.85)
- Trigger regeneration
- New identity includes newly stabilized entity
- Token budget reallocated via divisor apportionment

**Verification:**
```python
identity_before = load_identity_snapshot()

# Run learning loop
for _ in range(5):
    run_trace_session()

should_regen = should_regenerate_identity(graph, last_time)
assert should_regen, "Drift threshold exceeded"

identity_after = generate_system_prompt(graph)
assert identity_after != identity_before
```

**Observable metrics:**
- `identity.regenerated` event with drift_score, entities_added, entities_removed

**Failure modes:**
- No regeneration despite drift (threshold too high)
- Constant regeneration (threshold too low, thrashing)
- Composition unchanged (selection bug)

---

## Integration Tests (Multi-Stage)

### INT-1: Complete Pipeline (Happy Path)

**Scenario:** User asks "Fix websocket timeout" → system responds with diagnosis + fix

**Stages:**
1. Signal → stimulus (burst_id assigned)
2. Retrieval → 8 relevant nodes
3. Injection → dual-channel, nodes reach threshold
4. Entity "websocket_debugging" activates
5. Traversal → within-entity strides
6. WM → 2 entities selected
7. Context → identity includes "runtime_engineering", input includes "websocket_debugging"
8. LLM → response with diagnosis
9. TRACE → 5 reinforcement marks, 2 formations
10. Weights → local update to "websocket_debugging"
11. Identity → quality increases, no regen yet

**Success criteria:**
- All stages complete <2 seconds
- Response mentions "connection timeout" (relevant)
- TRACE extracts ≥3 marks
- Weight increases on debugging-related nodes
- No errors in telemetry

---

### INT-2: Learning Loop (Multi-Turn)

**Scenario:** 3 debugging sessions improve "websocket_debugging" entity quality until it enters identity

**Turn 1:**
- Debug websocket issue
- TRACE reinforces debugging patterns
- Entity quality: 0.65 → 0.70

**Turn 2:**
- Another websocket issue
- TRACE reinforces same patterns
- Entity quality: 0.70 → 0.78

**Turn 3:**
- Third issue, successful resolution
- TRACE strong reinforcement
- Entity quality: 0.78 → 0.85
- **Identity regeneration triggered**
- "websocket_debugging" now in system prompt

**Success criteria:**
- Quality increases monotonically
- Identity regenerates after turn 3
- Token allocation includes new entity
- Subsequent responses show debugging expertise

---

### INT-3: Burst Coalescing → Unified Response

**Scenario:** 4 filesystem events coalesce → single unified response

**Stages:**
1. 4 signals arrive <200ms → coalesced to single burst
2. Retrieval → diverse nodes (files A, B, C, D related)
3. Injection → distributed across all relevant nodes
4. Entity "code_investigation" activates (covers all files)
5. Response addresses all 4 changes as unified concern
6. TRACE reinforces multi-file reasoning

**Success criteria:**
- Single burst_id for all 4 signals
- Response mentions all 4 files
- No fragmented attention (single entity dominant)
- Attribution spread across nodes

---

## Observable Metrics Summary

**Per-stage events:**
- `stimulus.received`, `stimulus.coalesced`
- `retrieval.completed`
- `injection.completed`, `injection.health_modulated`
- `node.flip`, `subentity.flip`
- `stride.exec`, `subentity.boundary.summary`
- `wm.selection`
- `context.reconstructed`, `identity.regenerated`
- `trace.parsed`, `formation.created`
- `weights.updated.trace`

**Health metrics:**
- Criticality ρ (target: 0.95-1.05)
- Active frontier size (target: <500 nodes)
- Entity activation rate (target: 5-7 in WM)
- Conservation error (target: <1%)

**Quality metrics:**
- Entity formation quality (target: >0.7 for identity)
- Context relevance (semantic similarity to stimulus)
- Response accuracy (manual/automated eval)
- Learning rate (weight changes per TRACE session)

---

## Failure Mode Matrix

| Stage | Failure Mode | Detection | Mitigation |
|-------|--------------|-----------|------------|
| Stimulus | Burst under-coalescing | Multiple burst_ids <300ms | Increase coalescing window |
| Retrieval | Entropy miscalculation | Match count vs stimulus specificity | Calibrate entropy formula |
| Injection | No propagation (capped at threshold) | Nodes at threshold don't diffuse | CRITICAL: Use amplifier channel |
| Activation | Conservation violation | ΣΔE ≠ budget | Fix staged delta commit |
| Entity | Single-node domination | One member = 90% of entity E | Log damping in formula |
| Traversal | Entity thrashing | >5 boundary crossings per second | Add hysteresis, increase ease threshold |
| WM | Capacity overflow | >7 entities selected | Enforce hard cap, better scoring |
| Context | Transient in identity | High-volatility entity in system | Check volatility < threshold |
| Response | LLM timeout | No response after 30s | Retry with shorter context |
| TRACE | Parse failure | No marks extracted despite format | Improve regex, validate |
| Weights | Outlier dominates | Single update changes weight by >0.5 | Winsorize, z-score bounds |
| Identity | Regeneration thrashing | Regen every turn | Increase drift threshold, add time gate |

---

## Test Execution Plan

**Phase 1: Unit Tests (Per-Stage)**
- Each stage tested in isolation
- Mocked dependencies
- Fast (<100ms per test)
- Coverage: all test cases above

**Phase 2: Integration Tests (Multi-Stage)**
- End-to-end pipelines
- Real graph data
- Slower (~2-5s per test)
- Coverage: INT-1, INT-2, INT-3

**Phase 3: Load Tests**
- Concurrent stimuli
- Large graphs (100K+ nodes)
- Performance targets:
  - Stimulus → Response: <2s (p50), <5s (p95)
  - Conservation error: <1%
  - No crashes or deadlocks

**Phase 4: Chaos Tests**
- Random signal timing
- Supercritical/subcritical graphs
- Missing data (embeddings, thresholds)
- Verify graceful degradation

---

## Success Criteria (Overall)

✅ **Correctness:**
- Conservation maintained (<1% error)
- Threshold crossing triggers activation
- Entity energy derives correctly from members
- TRACE updates apply to correct nodes/entities

✅ **Performance:**
- Stimulus → Response <2s (p50)
- No memory leaks over 1000 turns
- Frontier size bounded (<500 active nodes)

✅ **Phenomenology:**
- Responses relevant to stimulus
- Identity stable across sessions (unless major learning)
- Learning visible (quality increases over turns)
- Multi-turn coherence (context builds)

✅ **Observability:**
- All stages emit telemetry events
- Conservation checked every frame
- Health metrics within targets
- Failures logged with context

---

**Next steps:**
1. Felix implements unit tests (Phase 1)
2. Luca validates phenomenological correctness per stage
3. Ada coordinates integration test scenarios
4. Victor monitors production telemetry for failure modes

**Status:** Ready for implementation

