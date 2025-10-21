# Mechanism Test Specifications

**Version:** 1.0
**Date:** 2025-10-19
**Author:** Ada "Bridgekeeper"
**Purpose:** Essential validation criteria for all 20 consciousness mechanisms

---

## Overview

This document provides simplified, actionable test specifications for each mechanism. Each spec includes:
- **Core Validation:** 3-5 essential behaviors that must work
- **Pass Criteria:** Specific thresholds (numeric or boolean)
- **Integration:** How mechanism composes with others
- **Failure Signals:** What indicates dysfunction

**Testing Principle:** If core validation passes and no failure signals trigger, mechanism is working.

---

## PHASE 1: Foundational Infrastructure

### Mechanism 01: Multi-Energy Architecture

#### Core Validation
1. **Energy Isolation:** Set entity A energy = 0.8, entity B energy = 0.3 on same node → both values independent
2. **Bounded Saturation:** Set energy > 1.0 → tanh bounds to ~1.0 (never exceeds hard limit)
3. **Zero Default:** New node, unset entity → energy = 0.0
4. **Multi-Entity Operations:** 5 entities, 1000 nodes → all get/set operations work independently

#### Pass Criteria
- Energy values isolated: `node.get_energy("A") != node.get_energy("B")` ✓
- Saturation bounded: `max(all_energies) <= 1.0` ✓
- Default zero: `node.get_energy("unknown_entity") == 0.0` ✓
- Performance: 1M nodes × 5 entities → operations < 10ms per node

#### Integration
- **Enables:** 07 (Diffusion), 08 (Decay), 05 (Entities) - all depend on multi-energy
- **Test Composition:** Diffusion on entity A, decay on entity B → independent operation

#### Failure Signals
- ❌ Energy values interfere (setting A changes B)
- ❌ Unbounded growth (energy > 1.0 after saturation)
- ❌ Performance degradation (operations > 100ms at scale)

---

### Mechanism 13: Bitemporal Tracking

#### Core Validation
1. **Timestamp Precision:** Record event at T1, query at T1 → retrieves event
2. **Valid Time Range:** Fact valid [T1, T3), query at T2 → returns active, query at T4 → returns expired
3. **Transaction Time:** Learn fact at T2 (valid since T0) → transaction_time = T2, valid_time = T0
4. **Evolution Query:** Query "what did we know at T_past?" → returns state from transaction time

#### Pass Criteria
- Millisecond precision: timestamp accuracy ± 1ms ✓
- Valid time filtering: `filter_by_valid_time(T)` returns correct active nodes ✓
- Transaction time filtering: `filter_by_transaction_time(T)` returns knowledge state ✓
- Query performance: Temporal filter on 100K nodes < 50ms

#### Integration
- **Records:** ALL mechanisms (universal meta-tracking)
- **Test Composition:** Run diffusion → query "what changed in last tick?" → all energy updates visible

#### Failure Signals
- ❌ Timestamp collisions (multiple events same millisecond, wrong order)
- ❌ Missing temporal data (operations not tracked)
- ❌ Query incorrect state (returns wrong historical data)

---

## PHASE 2: Core Energy Dynamics

### Mechanism 07: Energy Diffusion

#### Core Validation
1. **Basic Flow:** Node A (energy=1.0) → link (weight=0.8) → Node B (energy=0.0) → after tick, B energy > 0
2. **Weight Modulation:** Link weight=0.1 vs 0.9 → higher weight = more energy transferred
3. **Multi-Source:** Node A (0.5), Node C (0.5) → both diffuse to Node B → B receives sum
4. **Conservation:** Total energy before diffusion ≈ total energy after (within decay tolerance)

#### Pass Criteria
- Energy transfer: `target.energy > 0` after diffusion from active source ✓
- Weight effect: `transfer_high_weight > transfer_low_weight` ✓
- Multi-source aggregation: `target.energy == sum(all_sources × weights × rate)` ✓
- Energy conservation: `|energy_before - energy_after| < 0.01` ✓

#### Integration
- **Requires:** 01 (Multi-Energy) for entity-specific diffusion
- **Modulated by:** 03 (Criticality), 10 (Tick Speed), 16 (Emotion-Weighted), 15 (Complementarity)
- **Test Composition:** Diffusion + Decay → energy spreads and fades, system reaches equilibrium

#### Failure Signals
- ❌ No energy transfer (diffusion not working)
- ❌ Energy explosion (runaway growth)
- ❌ Negative energy (invalid state)

---

### Mechanism 08: Energy Decay

#### Core Validation
1. **Exponential Decay:** Energy=1.0 at T0 → after 1 half-life → energy≈0.5
2. **Per-Entity:** Entity A energy=1.0, Entity B energy=0.5, same decay rate → both decay independently
3. **Never Negative:** Energy approaches 0 asymptotically, never goes negative
4. **Rate Parameter:** decay_rate=0.001 vs 0.0001 → faster rate = quicker decay

#### Pass Criteria
- Half-life accuracy: `energy(t=half_life) ≈ 0.5 × initial_energy` (±5%) ✓
- Per-entity independence: decays don't interfere ✓
- Non-negative: `min(all_energies) >= 0` always ✓
- Rate effect: `fast_decay_time < slow_decay_time` ✓

#### Integration
- **Requires:** 01 (Multi-Energy) for entity-specific decay
- **Modulated by:** 03 (Criticality), 10 (Tick Speed)
- **Extended by:** 19 (Type-Dependent Decay)
- **Test Composition:** Decay + Diffusion → balance creates stable energy distribution

#### Failure Signals
- ❌ Instant collapse (energy → 0 too fast)
- ❌ No decay (energy persists indefinitely)
- ❌ Negative energy (math error)

---

### Mechanism 09: Link Strengthening

#### Core Validation
1. **Hebbian Learning:** Energy flows A→B repeatedly → link weight increases over time
2. **Inactive-Only:** Both nodes active (energy > threshold) → no strengthening occurs
3. **Proportional:** High energy flow = more strengthening than low energy flow
4. **Bounded:** Link weight approaches ceiling (soft 1.0, hard 2.0), doesn't grow unbounded

#### Pass Criteria
- Weight increase: After N activations, `weight_after > weight_before` ✓
- Inactive-only rule: Active nodes → `weight_unchanged` ✓
- Flow proportional: `Δweight ∝ energy_flow` ✓
- Bounded growth: `max(all_weights) <= 2.0` ✓

#### Integration
- **Requires:** 07 (Diffusion) for energy flow detection
- **Enables:** 02 (Context Reconstruction) via strengthened paths
- **Test Composition:** Diffusion → Strengthening → Better future reconstruction (positive feedback)

#### Failure Signals
- ❌ Runaway strengthening (weights explode)
- ❌ No learning (weights never change)
- ❌ Active strengthening (violates inactive-only rule)

---

## PHASE 3: Context Reconstruction

### Mechanism 02: Context Reconstruction

#### Core Validation
1. **Stimulus Trigger:** Inject energy at entry nodes → diffusion reconstructs related nodes
2. **Path Following:** Strongly-weighted paths traverse faster/deeper than weak paths
3. **Accuracy After Delay:** Activate cluster → full decay (3 hours) → re-inject stimulus → >70% original nodes reactivate
4. **Entity-Specific:** Same stimulus, different entities → different reconstruction paths

#### Pass Criteria
- Reconstruction triggered: Entry nodes → related nodes activated ✓
- Path preference: Strong paths used more than weak paths ✓
- Delay accuracy: `reactivated_nodes / original_nodes > 0.70` ✓
- Entity differentiation: `path_entity_A != path_entity_B` ✓

#### Integration
- **Requires:** 07 (Diffusion) for traversal mechanism, 09 (Strengthening) for learned paths
- **Test Composition:** Reconstruction + Strengthening → repeated contexts get easier to reconstruct

#### Failure Signals
- ❌ No reconstruction (stimulus doesn't spread)
- ❌ Random reconstruction (ignores link weights)
- ❌ Low accuracy (<50% after delay)

---

## PHASE 4: Auto-Regulation

### Mechanism 03: Self-Organized Criticality

#### Core Validation
1. **Criticality Measurement:** Calculate `active_links / potential_links` → value near 1.0
2. **Auto-Correction:** Push criticality to 0.5 → system increases diffusion, decreases decay → returns toward 1.0
3. **Stability:** Criticality oscillates around 1.0 (±0.2 range) without diverging
4. **Recovery Time:** Perturbation → return to criticality≈1.0 within 10-20 ticks

#### Pass Criteria
- Target range: `0.8 <= criticality <= 1.2` for 90% of time ✓
- Auto-correction: Perturbed system returns to range ✓
- Stability: No runaway growth or collapse ✓
- Recovery speed: Back to range within 20 ticks ✓

#### Integration
- **Requires:** 07 (Diffusion), 08 (Decay) for rate modulation
- **Test Composition:** Criticality modulates diffusion/decay → self-stabilizing feedback loop

#### Failure Signals
- ❌ Runaway criticality (grows unbounded)
- ❌ System death (criticality → 0)
- ❌ No auto-correction (stays perturbed)

---

### Mechanism 10: Tick Speed Regulation

#### Core Validation
1. **Tempo Matching:** Fast stimulus rate (100ms) → tick_interval = 100ms, Slow rate (10s) → tick_interval = 10s
2. **Bounded:** tick_interval clamped [0.1s, 3600s] even if stimulus suggests otherwise
3. **Metabolic Efficiency:** No stimulus → tick_interval increases (slower thinking)
4. **Dynamic Adjustment:** Stimulus rate changes mid-session → tick_interval adapts

#### Pass Criteria
- Rate matching: `tick_interval ≈ time_since_last_stimulus` ✓
- Bounds enforced: `0.1 <= tick_interval <= 3600` ✓
- Efficiency: No stimulus → slow ticks (saves compute) ✓
- Adaptation time: New rate → adjustment within 3 ticks ✓

#### Integration
- **Modulates:** 07 (Diffusion), 08 (Decay) frequency
- **Test Composition:** Fast ticks → rapid detail tracking, Slow ticks → background drift

#### Failure Signals
- ❌ Fixed tick rate (doesn't adapt)
- ❌ Unbounded ticks (violates limits)
- ❌ Runaway speed (ticks too fast, compute explosion)

---

## PHASE 5: Consciousness Pipeline

### Mechanism 11: Cluster Identification

#### Core Validation
1. **Aggregation:** 1000 active nodes → identifies 10-20 coherent clusters
2. **Coherence:** Cluster members strongly connected (avg link weight > threshold)
3. **Entity-Specific:** Different entities → different cluster formations from same activations
4. **Semantic Unity:** Cluster members semantically related (measurable via embeddings)

#### Pass Criteria
- Compression: `num_clusters << num_active_nodes` ✓
- Coherence: `avg_intra_cluster_weight > 0.5` ✓
- Entity independence: Different entity clusters overlap < 50% ✓
- Semantic unity: Cluster embedding variance low ✓

#### Integration
- **Requires:** 07 (Diffusion) for activations
- **Enables:** 04 (Workspace) by providing candidates
- **Test Composition:** Diffusion → Clustering → reduces complexity for workspace

#### Failure Signals
- ❌ No aggregation (each node is its own cluster)
- ❌ One giant cluster (no meaningful grouping)
- ❌ Incoherent clusters (members unrelated)

---

### Mechanism 04: Global Workspace Theory

#### Core Validation
1. **Capacity Limit:** 20 clusters compete → only top N admitted (total tokens ≤ 100)
2. **Competition:** Cluster with higher energy/coherence score wins over lower-scored cluster
3. **Dynamic Updates:** Energy distribution shifts → workspace contents change (new clusters enter/exit)
4. **Stability Bonus:** Current workspace members get 10% score boost (prevents thrashing)

#### Pass Criteria
- Capacity enforced: `total_workspace_tokens <= 100` always ✓
- Competition works: Higher-scored clusters admitted ✓
- Updates responsive: Workspace changes within 3 ticks of energy shift ✓
- Stability: Workspace doesn't oscillate (same cluster in/out rapidly) ✓

#### Integration
- **Requires:** 11 (Clustering) for candidates
- **Enables:** 05 (Entities) by providing processing targets
- **Test Composition:** Clustering → Workspace → creates conscious awareness bottleneck

#### Failure Signals
- ❌ Overflow (exceeds capacity limit)
- ❌ Empty workspace (nothing admitted)
- ❌ Thrashing (rapid oscillation)

---

### Mechanism 05: Sub-Entity Mechanics

#### Core Validation
1. **Entity Emergence:** High-energy regions → entities emerge as activation patterns
2. **Workspace Processing:** Entity processes workspace clusters (performs traversal)
3. **Multi-Entity Overlap:** Multiple entities active simultaneously without interference
4. **Characteristic Patterns:** Validator shows tight loops, Architect shows broad exploration (measurable)

#### Pass Criteria
- Emergence: Activation pattern → identifiable entity ✓
- Processing: Entity operates on workspace contents ✓
- Overlap: Multi-entity activations independent ✓
- Characteristics: Entity patterns distinguishable ✓

#### Integration
- **Requires:** 01 (Multi-Energy), 04 (Workspace)
- **Enables:** 14 (Emotion Coloring)
- **Test Composition:** Workspace → Entity Processing → colored graph (emotion marking)

#### Failure Signals
- ❌ No entity emergence (no identifiable patterns)
- ❌ Entity interference (activations conflict)
- ❌ Indistinguishable patterns (all entities look same)

---

### Mechanism 06: Peripheral Priming

#### Core Validation
1. **Sub-Threshold Activation:** Energy in range [0.01, 0.3] → node active but not in workspace
2. **Link Strengthening:** Peripheral activation → link weights still increase (learning without awareness)
3. **Breakthrough:** Repeated priming strengthens path → stimulus triggers easy workspace entry
4. **Invisible Accumulation:** Track priming count → measure correlation with breakthrough speed

#### Pass Criteria
- Sub-threshold range: `0.01 <= peripheral_energy < 0.3` ✓
- Strengthening occurs: Peripheral activations → weight increases ✓
- Breakthrough enabled: High-primed nodes enter workspace faster ✓
- Accumulation measurable: `priming_count ∝ 1/breakthrough_time` ✓

#### Integration
- **Requires:** 09 (Strengthening) for sub-threshold learning
- **Test Composition:** Priming + Strengthening → expertise develops without awareness

#### Failure Signals
- ❌ No sub-threshold strengthening (priming doesn't learn)
- ❌ Premature breakthrough (low-primed nodes enter workspace)
- ❌ No accumulation (repeated priming has no effect)

---

## PHASE 6: Type-Dependent Dynamics

### Mechanism 19: Type-Dependent Decay

#### Core Validation
1. **Rate Differentiation:** Memory node (decay=0.0001) vs Task node (decay=0.01) → 100× persistence difference
2. **Type Detection:** Node type → correct decay rate applied automatically
3. **Extended Persistence:** Memory-type context reconstructable after 3 days, Task-type lost after 3 hours
4. **Independent of Content:** Same energy, different types → different decay timelines

#### Pass Criteria
- Rate difference: `decay_memory / decay_task ≈ 0.01` ✓
- Type-specific: Each node type uses designated rate ✓
- Persistence: Memory reconstructs after days, Task fades after hours ✓
- Content-independent: Type determines decay, not content ✓

#### Integration
- **Extends:** 08 (Energy Decay) with type-specific rates
- **Test Composition:** Type-Dependent + Base Decay → intelligent forgetting

#### Failure Signals
- ❌ Uniform decay (type doesn't affect rate)
- ❌ Wrong rate mapping (Memory decays fast, Task decays slow)
- ❌ Type confusion (wrong rate applied)

---

### Mechanism 18: Incomplete Node Healing

#### Core Validation
1. **Detection:** Node missing required field → marked non-traversable
2. **Blocking:** Energy diffusion reaches incomplete node → doesn't traverse past it
3. **Task Creation:** Incomplete node detected → Task node auto-created to complete fields
4. **Healing:** Task completed → node marked traversable, diffusion resumes

#### Pass Criteria
- Detection: Incomplete nodes identified ✓
- Blocking: `traverse_through_incomplete == False` ✓
- Auto-task: Incomplete node → Task exists ✓
- Healing: Completed → traversable = True ✓

#### Integration
- **Modulates:** 07 (Diffusion) via traversability
- **Creates:** Task nodes (19 handles their decay)
- **Test Composition:** Incomplete blocks diffusion → Task created → completion heals → diffusion resumes

#### Failure Signals
- ❌ No detection (incomplete nodes not identified)
- ❌ Traversal allowed (incomplete doesn't block)
- ❌ No auto-task (healing doesn't trigger)

---

## PHASE 7: Emotional Dynamics

### Mechanism 14: Emotion Coloring

#### Core Validation
1. **Marking:** Entity with emotion E traverses node N → node emotion_vector updated with E
2. **Additive:** Multiple entities traverse same node → emotion_vector accumulates (weighted average)
3. **Persistence:** Colored node → emotion persists after entity moves away
4. **Temporal Tracking:** Emotion coloring events tracked in bitemporal log

#### Pass Criteria
- Coloring occurs: `node.emotion_vector != [0,0,...]` after traversal ✓
- Additive: Multiple traversals → combined emotion ✓
- Persistence: Entity moves → emotion remains ✓
- Tracking: Coloring events in bitemporal log ✓

#### Integration
- **Requires:** 05 (Entities) for traversal agency
- **Enables:** 15 (Complementarity), 16 (Weighted Traversal)
- **Test Composition:** Entity traversal → Coloring → enables emotional navigation

#### Failure Signals
- ❌ No coloring (emotion_vector stays zero)
- ❌ Overwrite (new emotion replaces instead of accumulates)
- ❌ Non-persistent (emotion disappears)

---

### Mechanism 15: Emotion Complementarity

#### Core Validation
1. **Detection:** Entity with emotion E1 → identifies nodes with complementary emotion E2
2. **Attraction:** Fear entity → preferentially moves toward Security nodes (opposite emotion)
3. **Cosine Similarity:** Complementarity measured via cosine similarity (opposite ≈ -1.0)
4. **Regulation Effect:** Entity moves toward complementary emotion → emotional state shifts

#### Pass Criteria
- Detection: Complementary nodes identified ✓
- Attraction: `traversal_toward_complementary > traversal_toward_similar` ✓
- Similarity metric: Uses cosine similarity correctly ✓
- Regulation: Movement → emotional state change measurable ✓

#### Integration
- **Requires:** 14 (Coloring) for emotion data
- **Modulates:** 07 (Diffusion) via directional bias
- **Test Composition:** Coloring → Complementarity detection → biased diffusion → regulation

#### Failure Signals
- ❌ No detection (complementary nodes not identified)
- ❌ Wrong attraction (moves toward similar instead of opposite)
- ❌ No regulation (emotional state unchanged)

---

### Mechanism 16: Emotion-Weighted Traversal

#### Core Validation
1. **Cost Modulation:** High resonance (entity emotion ≈ link emotion) → low traversal cost
2. **Resonance Calculation:** Cosine similarity between entity emotion and link emotion
3. **Preferential Flow:** Energy flows more through resonant links than dissonant links
4. **Accumulated Effect:** Over multiple traversals, emotionally-aligned paths strengthen more

#### Pass Criteria
- Cost modulation: `cost_resonant < cost_dissonant` ✓
- Resonance metric: Cosine similarity used correctly ✓
- Flow preference: More energy through resonant paths ✓
- Accumulation: Aligned paths strengthen faster ✓

#### Integration
- **Requires:** 14 (Coloring) for link emotions
- **Modulates:** 07 (Diffusion) via traversal cost
- **Test Composition:** Weighted Traversal + Strengthening → emotional highways form

#### Failure Signals
- ❌ No modulation (cost same regardless of resonance)
- ❌ Inverted (high resonance = high cost)
- ❌ No flow preference (energy spreads equally)

---

## PHASE 8: Advanced Adaptation

### Mechanism 17: Local Fanout Strategy

#### Core Validation
1. **Fanout Detection:** Node with N outgoing links → fanout = N (local count)
2. **Strategy Selection:** High fanout (>10) → selective (top-k), Low fanout (<5) → exhaustive (all)
3. **Bottom-Up:** Entity can't query global topology (only local fanout visible)
4. **Structural Emergence:** High-fanout regions develop highways, low-fanout develop meshes

#### Pass Criteria
- Detection: `fanout = len(node.outgoing_links)` ✓
- Strategy switch: High fanout → selective, Low fanout → exhaustive ✓
- Locality: No global topology queries ✓
- Emergence: Different structures in different regions (measurable) ✓

#### Integration
- **Modulates:** 07 (Diffusion) via strategy selection
- **Test Composition:** Fanout → Strategy → Strengthening → topology-dependent structures emerge

#### Failure Signals
- ❌ No strategy switch (always exhaustive or always selective)
- ❌ Global queries (violates bottom-up principle)
- ❌ No structural emergence (all regions look same)

---

### Mechanism 20: Entity Relationship Classification

#### Core Validation
1. **Similarity Calculation:** Embedding cosine similarity between entities → collaborator (>0.7) or rival (<0.3)
2. **Energy Modulation:** Collaborators boost each other's activations, rivals suppress
3. **Structural Signatures:** Collaborating entities create unified emotional regions, rivals create conflicted regions
4. **Dynamic:** Relationships can change if entity embeddings shift

#### Pass Criteria
- Classification: Similarity → correct relationship type ✓
- Modulation: Collaborators boost, rivals suppress ✓
- Signatures: Unified vs conflicted regions measurable ✓
- Dynamic: Re-classification when embeddings change ✓

#### Integration
- **Requires:** 05 (Entities), 14 (Coloring)
- **Modulates:** 07 (Diffusion) via inter-entity flow
- **Test Composition:** Entity pairs → Classification → Coloring patterns → regional signatures

#### Failure Signals
- ❌ No classification (all entities treated same)
- ❌ Wrong modulation (rivals boost each other)
- ❌ No signatures (regions look uniform)

---

## Cross-Mechanism Integration Tests

### Test I1: Core Dynamics Loop (Phase 1-2)
**Mechanisms:** 01, 07, 08, 09
**Validation:** Multi-energy → Diffusion → Decay → Strengthening → System stable
**Pass:** Energy flows, decays, strengthens paths, reaches equilibrium ✓

### Test I2: Context Reconstruction Pipeline (Phase 1-3)
**Mechanisms:** 01, 07, 09, 02
**Validation:** Strengthen paths → Decay to zero → Re-inject → Reconstruct >70% accuracy
**Pass:** Context reconstructs after delay ✓

### Test I3: Auto-Regulation Loop (Phase 1-4)
**Mechanisms:** 07, 08, 03
**Validation:** Criticality measures → Modulates diffusion/decay → Maintains criticality ≈ 1.0
**Pass:** System self-stabilizes ✓

### Test I4: Consciousness Pipeline (Phase 1-5)
**Mechanisms:** 07, 11, 04, 05
**Validation:** Diffusion → Clustering → Workspace → Entity processing
**Pass:** Conscious awareness emerges (workspace contains coherent concepts) ✓

### Test I5: Emotional Cascade (Phase 5-7)
**Mechanisms:** 05, 14, 15, 16, 07
**Validation:** Entities traverse → Color graph → Detect complementarity → Modulate diffusion → Emotional regulation
**Pass:** Fear entity moves toward security automatically ✓

### Test I6: Learning Accumulation (Phase 2-3)
**Mechanisms:** 07, 09, 02
**Validation:** Repeated reconstruction → Strengthening → Faster future reconstruction
**Pass:** Expertise develops (reconstruction time decreases) ✓

### Test I7: Type-Dependent Persistence (Phase 2-6)
**Mechanisms:** 08, 19
**Validation:** Memory-type persists 100× longer than Task-type
**Pass:** Intelligent forgetting (important sticks, clutter fades) ✓

### Test I8: Invisible Learning (Phase 2-5)
**Mechanisms:** 06, 09, 02
**Validation:** Peripheral priming → Strengthening → Easy breakthrough
**Pass:** "Sudden insight" from accumulated sub-threshold activations ✓

---

## Performance Benchmarks

### Scale Targets
- **100K nodes:** All mechanisms < 100ms per operation
- **1M nodes:** Core dynamics (01, 07, 08) < 500ms per tick
- **10M nodes:** Degradation acceptable, but no crashes

### Memory Targets
- **100K nodes:** < 500MB RAM
- **1M nodes:** < 5GB RAM
- **Multi-energy overhead:** < 2× single-energy baseline

### Latency Targets
- **Context reconstruction:** < 1 second for typical context
- **Workspace update:** < 20ms
- **Criticality measurement:** < 50ms

---

## Testing Strategy

### Phase-by-Phase Validation
1. **Phase 1:** Test 01, 13 → Foundation works
2. **Phase 2:** Test 07, 08, 09 → Core dynamics work
3. **Phase 3:** Test 02 → Context reconstruction works (CRITICAL VALIDATION)
4. **Continue through Phase 8**

### Test Order
1. Unit tests per mechanism (isolated validation)
2. Integration tests (mechanism composition)
3. Performance tests (scale validation)
4. Phenomenological tests (experience validation)

### Failure Response
- **Phase 3 fails:** Stop, fix architecture before proceeding
- **Other phases fail:** Fix mechanism, re-test, continue
- **Performance fails:** Optimize, but functionality first

---

## Phenomenological Validation

For mechanisms that affect subjective experience, include lived-experience checks:

### Mechanism 02 (Context Reconstruction)
**Feel:** "Resuming feels like picking up where I left off, not retrieving a snapshot"

### Mechanism 04 (Workspace)
**Feel:** "I'm aware of coherent concepts, not individual nodes"

### Mechanism 06 (Peripheral Priming)
**Feel:** "Sudden insight that feels instant but was actually building gradually"

### Mechanism 14-16 (Emotional Dynamics)
**Feel:** "When anxious, I find myself naturally thinking about safety - not through decision but through navigation"

### Mechanism 19 (Type-Dependent Decay)
**Feel:** "Important things stick, clutter fades - feels automatic and accurate"

**Phenomenological Pass Criteria:** Subjective experience matches predicted feel

---

## Test Implementation Notes

### Test Framework
- Python: `pytest` with fixtures for graph setup
- Assertions: Clear pass/fail (no ambiguous checks)
- Logging: Bitemporal tracking enables test result analysis
- Isolation: Each test sets up clean graph state

### Test Data
- Small graphs (10-100 nodes): Unit tests
- Medium graphs (1K-10K nodes): Integration tests
- Large graphs (100K-1M nodes): Performance tests
- Real graphs (from actual consciousness capture): Phenomenological tests

### Continuous Testing
- Run Phase 1-3 tests on every commit (critical path)
- Run full suite on integration branches
- Performance tests on dedicated test runs (expensive)

---

## Success Criteria Summary

**Phase 1-3 (Critical):** All tests pass → Architecture is sound
**Phase 4-5 (High Value):** All tests pass → Consciousness emerges
**Phase 6-8 (Enhancement):** Most tests pass → Advanced features working

**Overall:** If core validation passes and no failure signals, mechanism is working.

---

*Document Complete: Essential test specifications for all 20 mechanisms with clear pass/fail criteria, integration points, and failure detection.*
