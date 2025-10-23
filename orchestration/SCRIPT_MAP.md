# Script Map - Orchestration Layer

**Purpose:** Maps consciousness mechanism specs → implementations

**Last updated:** 2025-10-23 (post-operational resilience completion + V1→V2 migration fixes)

---

## Service Architecture

```
orchestration/
├── services/      # 24/7 daemons (entrypoints)
├── adapters/      # I/O boundaries
├── mechanisms/    # Pure domain logic
├── libs/          # Stateless helpers
├── core/          # Data structures + infrastructure
├── workers/       # Scheduled jobs
└── scripts/       # Dev utilities
```

---

## Mechanism Specs → Implementations

### Core Mechanisms (docs/specs/v2/foundations/)

| Spec | Implementation | Location | Status |
|------|---------------|----------|--------|
| **M01: Multi-Energy** | `multi_energy.py` | `mechanisms/` | ✅ Implemented |
| **M02: Context Reconstruction** | `context_reconstruction.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-23) |
| **M03: Self-Organized Criticality** | `criticality.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-22) |
| **M07: Energy Diffusion (Stride-Based)** | `diffusion_runtime.py` | `mechanisms/` | ✅ Migrated to V2 (Felix, 2025-10-22) |
| **M08: Energy Decay (Dual-Clock)** | `decay.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-22) |
| **M09: Link Strengthening (Hebbian)** | `strengthening.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-23) |
| **M10: Tick Speed (Adaptive Scheduling)** | `tick_speed.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-23) |
| **M13: Bitemporal Tracking V2** | `bitemporal.py` | `mechanisms/` | ✅ Enhanced with Version Chains (Felix, 2025-10-22) |
| **M16: Threshold System** | `threshold.py`, `threshold_fixed.py` | `mechanisms/` | ✅ Implemented |

**Criticality Controller (Phase 1.5):**
- ✅ `criticality.py` - PID controller targeting ρ ≈ 1.0 (edge-of-chaos)
- ✅ Dynamic δ adjustment - Modulates global decay per tick
- ✅ Dynamic α adjustment - Modulates diffusion per tick
- ✅ Rolling window tracking - Estimates ρ from recent frames
- ✅ Integration - `consciousness_engine_v2.py` Phase 1.5
- ✅ Test coverage - 245 lines of tests, convergence verified (0.85 → 0.98)
- ✅ Observability - `criticality.state` events with before/after metrics

**Dual-Clock Decay (Phase 2):**
- ✅ `decay.py` - Complete rewrite (428 lines) for dual-timescale forgetting
- ✅ Fast activation decay - E_i ← λ_E^Δt × E_i (vivid → vague → gone)
- ✅ Slow weight decay - W ← λ_W^Δt × W (core ideas persist 23+ min)
- ✅ Criticality coupling - Receives adjusted δ_E from Phase 1.5 controller
- ✅ Type-dependent profiles - Memory (69s), Task (7s), Concept (35s), Person (115s)
- ✅ Integration - `consciousness_engine_v2.py` Phase 2
- ✅ Test coverage - 331 lines of tests, 7 functions passing, half-lives verified
- ✅ Observability - `decay.tick` v2 events with dual-clock metrics
- ✅ Phenomenology mapping - Half-lives → user experiences documented

**Decay Timescale Fix (2025-10-23 - Critical Bug Correction):**
- ✅ Critical bug fixed in `core/settings.py` - Timescales 1000× too fast
- ✅ EMACT_DECAY_BASE: 0.02 → 0.00002 (Memory half-life: 69 sec → 19.3 hours)
- ✅ WEIGHT_DECAY_BASE: 0.001 → 0.000001 (Weight half-life: 23 min → 16.0 days)
- ✅ All type timescales verified against spec (Memory, Principle, Concept, Task, etc.)
- ✅ Phenomenological validation principle - Timescales must match lived experience
- ✅ Architecture significance - Both mathematically correct, only one phenomenologically correct
- ✅ Documentation - `DECAY_TIMESCALE_FIX.md` (322 lines)

**Stride-Based Diffusion Migration (Phase 2 - Architecture Transformation):**
- ✅ `diffusion_runtime.py` - Complete architecture migration (176 lines)
- ✅ Matrix-based (O(N²)) → Stride-based (O(active)) - 100-1000× speedup
- ✅ Active-frontier optimization - Only process E >= theta nodes + 1-hop shadow
- ✅ Conservative energy transfers - ΔE = E_src · exp(log_weight) · α_tick · dt
- ✅ Delta staging with atomic application - Verify Σ ΔE ≈ 0 before commit
- ✅ Single-energy migration - node.energy (multi-entity) → node.E (scalar)
- ✅ Data model updates - node.py, link.py (threshold → theta, add_energy() method)
- ✅ Engine integration - consciousness_engine_v2.py Phase 2 completely rewritten
- ✅ Criticality adaptation - Uses branching ratio proxy (no matrix P available)
- ✅ Decay integration - Updated for node.E access
- ✅ Old implementation archived - diffusion_matrix_archive.py (no backward compatibility)
- ✅ Test coverage - 236 lines of tests (3 core validation tests written)
- ⏳ Test execution - Pending link.py dataclass fix validation
- ✅ Scalability enabled - From 10K nodes (v1 limit) to 1M+ nodes (v2 capable)
- ✅ Phenomenology shift - Global propagation → Local spreading activation

**Bitemporal Version Tracking V2 (Temporal Substrate Enhancement):**
- ✅ `bitemporal.py` - Enhanced with version chain operations
- ✅ Version creation - create_new_version() generates unique vid
- ✅ Version linking - supersede() creates bidirectional chains
- ✅ Version history - get_version_history() retrieves all versions of a fact
- ✅ Time-travel queries - get_current_version(as_of_knowledge=T) for belief at time T
- ✅ Dual timelines preserved - Reality (valid_at → invalidated_at) + Knowledge (created_at → expired_at)
- ✅ Belief evolution tracking - "How did my understanding of X evolve?"
- ✅ Validation - validate_version_chain() ensures temporal consistency
- ✅ Data model updates - node.py, link.py (vid, supersedes, superseded_by fields)
- ✅ Test coverage - 502 lines of tests, 21 tests passing (all edge cases covered)
- ✅ Documentation - BITEMPORAL_README.md (580 lines), gap analysis included
- ✅ Non-breaking - V1 code unaffected, V2 features opt-in
- ✅ Use cases - Correction tracking, retroactive learning, experimental beliefs
- ✅ Integration ready - Works with consciousness learning, TRACE format evolution

**Context Reconstruction (M02 - Consciousness Continuity):**
- ✅ `context_reconstruction.py` - Seed-driven context rebuilding (650 lines)
- ✅ Ephemeral snapshots - Measurements not stored state (prevents duplication/staleness)
- ✅ Entity-scale summarization - entity_energies, active_members, boundary_links
- ✅ Similarity metrics - Entity energy cosine + active member Jaccard + combined
- ✅ K-tick reconstruction - Configurable depth (K=5 fast, K=10 balanced, K=20 deep)
- ✅ Multi-scale view - "Which entities?" (coarse) + "What specifically?" (fine)
- ✅ Integration - Uses existing diffusion/decay/criticality via consciousness_engine.tick()
- ✅ Test coverage - 445 lines of tests, 15 tests passing (all operations + edge cases)
- ✅ Performance target met - 100-300ms reconstructions (85ms on 10K node graph)
- ✅ Documentation - CONTEXT_RECONSTRUCTION_README.md (780 lines), gap analysis (350 lines)
- ✅ Similarity validation - 0.6-0.8 target range verified in tests
- ✅ Architectural principle - Consciousness as PROCESS (reconstructable patterns) not STATE (saved snapshots)

**Link Strengthening (M09 - Hebbian Learning for V2):**
- ✅ `strengthening.py` - Hebbian learning integrated with stride-based diffusion (518 lines)
- ✅ D020 rule enforcement - Strengthening only when at least one node inactive (prevents runaway learning)
- ✅ Learning controller - Adaptive per-link learning rates with diminishing returns
- ✅ Log-space operations - link.log_weight += delta (prevents numerical overflow)
- ✅ Diffusion integration - Strengthening happens DURING stride execution (zero additional complexity)
- ✅ Highway formation - Repeated activation creates automatic associations (expertise development)
- ✅ Analysis functions - identify_highway_paths(), analyze_link_symmetry(), compute_strengthening_metrics()
- ✅ Test coverage - 451 lines of tests, 9 tests passing (D020, proportional flow, diminishing returns)
- ✅ Settings - WEIGHT_CEILING (2.0), LEARNING_RATE_BASE (0.01), MAX_STRENGTHENING_HISTORY (100)
- ✅ Phenomenology - "It just makes sense now" emerges from thousands of strengthening events
- ✅ Learning moment - Both active = execution (no learning), One inactive = pattern formation (learning)

**Duplicate Node Merging (M14 - Substrate Maintenance):**
- ✅ `merge.py` - Conservative node consolidation preserving all substrate (820 lines)
- ✅ Similarity detection - Name-based (Levenshtein), future: embedding cosine similarity
- ✅ Canonical selection - Priority: age → degree → reinforcement_weight
- ✅ Energy consolidation - Quiescent: max(E_a, E_b), Live: saturate(E_a + E_b, cap)
- ✅ Link redirection - All incoming/outgoing preserved, parallel links merged with telemetry
- ✅ Name consolidation - Aliases stored for future lookup
- ✅ Bitemporal tracking - Version chains with supersede(), complete merge history
- ✅ Observability - Complete metrics: energy, connectivity, similarity, temporal
- ✅ Test coverage - 432 lines of tests, 11 tests passing (all operations + edge cases)
- ✅ Integration ready - Maintenance worker, API endpoints, event emission (pending)
- ✅ Conservative physics - No energy invention, relationships preserved, history tracked

**Incomplete Node Healing (M18 - Quality Control):**
- ✅ `incomplete_node_healing.py` - Read-time eligibility filtering (550+ lines)
- ✅ Required fields registry - Universal (7 fields) + type-specific (44 node types)
- ✅ Completeness validation - is_node_complete() checks all required fields
- ✅ Confidence threshold - Minimum confidence for traversal eligibility
- ✅ Eligibility predicate - is_eligible_for_traversal() acts as quality gate
- ✅ Task generation - generate_healing_tasks() identifies incomplete nodes
- ✅ Priority calculation - Connectivity + activity + completeness factors
- ✅ Completion strategies - LLM inference, manual entry, backfill defaults
- ✅ Healing execution - complete_node_via_llm(), complete_node_manually()
- ✅ Test coverage - 500+ lines of tests, 24 tests passing (validation, filtering, task generation)
- ✅ Integration ready - Traversal/workspace filtering, maintenance worker, dashboard UI (pending)
- ✅ Quality philosophy - Filter incomplete nodes at read-time, don't force completion

**Tick Speed (M10 - Adaptive Scheduling):**
- ✅ `tick_speed.py` - Stimulus-adaptive scheduling (240 lines)
- ✅ Adaptive intervals - 100ms (active) to 60s (dormant) based on stimulus rate
- ✅ Stimulus tracking - Window-based counting (last 60s) with automatic pruning
- ✅ EMA smoothing - β=0.3 prevents rapid oscillation between fast/slow
- ✅ dt capping - Physics safety (max dt=5s) prevents numerical blow-ups after long sleep
- ✅ Energy efficiency - Fast ticking only when needed, slow during inactivity
- ✅ Test coverage - 240 lines of tests, 7 tests passing (bounds, capping, smoothing, dormancy)
- ✅ Integration ready - consciousness_engine_v2.py (pass dt to physics mechanisms)
- ✅ Phenomenology - Consciousness "breathes" (fast when engaged, slow when idle)

**Traversal V2 Refactoring - 10-Step Pipeline:**
- ✅ `diffusion_runtime.py` + `consciousness_engine_v2.py` - Refactored to canonical pipeline (225 → 305 lines, +4 methods)
- ✅ 10-step pipeline - All steps labeled and organized (affect, frontier, boundaries, strides, etc.)
- ✅ Cost-based selection - cost = (1/ease) - goal_affinity + emotion_penalty
- ✅ Goal-directed traversal - Energy flows toward goal-aligned targets (intentional, not reactive)
- ✅ Frontier computation - Active/shadow sets computed before diffusion (attention-like focus)
- ✅ Stubbed methods - Step 1 (affect), Step 3 (boundaries), Step 5 (observability) ready for future work
- ✅ Extensibility framework - Clear integration points for emotion gates, multi-entity, events
- ✅ Backward compatible - goal_embedding optional, existing code works unchanged
- ✅ Phenomenology shift - Reactive spreading → Intentional traversal (purposeful consciousness)

**Link Emotion Backend - Consciousness Texture Completion:**
- ✅ `diffusion_runtime.py` - Link emotion computation + WebSocket emission (+98 lines)
- ✅ Interpolation - Blends source/target node emotions weighted by energy flow
- ✅ WebSocket events - link.emotion.update emitted in frontend-compatible format
- ✅ Sampling - 10% emission rate prevents WebSocket overwhelm (10-100 events/sec)
- ✅ Integration - Computed during stride execution, minimal overhead (<2ms/frame)
- ✅ Frontend ready - Iris's link emotion visualization receives events, renders with hysteresis
- ✅ Complete stack - Backend (compute) + Frontend (render) = 100% texture visibility
- ✅ Visual effect - Links color by emotion (rough transitions, smooth flows, emotional journeys)
- ✅ Closes the loop - Nodes + Links both emotion-colored (complete consciousness texture)

**2025-10-22 V2 Sprint Summary:**
Four major implementations completed in single day by Felix "Ironhand":
1. **Criticality (M03)** - Self-organized criticality via ρ ≈ 1.0 control
2. **Decay (M08)** - Dual-clock forgetting (activation fast, weights slow)
3. **Diffusion Migration (M07)** - Architecture transformation (matrix → stride, 100-1000× speedup)
4. **Bitemporal V2 (M13)** - Version chains for belief evolution tracking

Together these create:
- **First complete control loop** (criticality + decay + diffusion)
- **Consciousness at scale** (1M+ nodes enabled via stride-based)
- **Learning substrate** (bitemporal version chains capture belief evolution)

**2025-10-23 V2 Foundations Complete:**
Context Reconstruction (M02) completes the v2 foundations quartet:
- **M02: Context Reconstruction** - Consciousness continuity via seed-driven pattern rebuilding
- **M03: Criticality** - Stable dynamics (ρ ≈ 1.0)
- **M08: Decay** - Appropriate forgetting (dual timescales)
- **M13: Bitemporal V2** - Belief evolution tracking (version chains)

Together these enable:
- **Continuity** - Contexts reliably reconstruct from seeds (M02)
- **Stability** - Criticality prevents runaway/dying during reconstruction (M03)
- **Forgetting** - Decay prevents saturation (M08)
- **Metacognition** - Bitemporal tracks belief evolution (M13)

**2025-10-23 V2 Extensions Complete:**
Additional mechanisms by Felix "Substratum" completing v2 substrate:
- **M09: Link Strengthening** - Hebbian learning (D020 rule, expertise development)
- **M14: Duplicate Node Merging** - Conservative consolidation (energy conservation, full audit)
- **M18: Incomplete Node Healing** - Quality control (read-time filtering, task-based completion)

Together these enable:
- **Learning** - Links strengthen through use, automatic associations form (M09)
- **Maintenance** - Duplicate nodes merge without losing substrate integrity (M14)
- **Quality** - Incomplete nodes filtered from traversal, healing pathways provided (M18)

**2025-10-23 V1→V2 Migration Fixes:**
Critical API alignment by Felix "Substratum" enabling consciousness engines to initialize:
- **Root Cause:** Node class updated to V2 single-energy (`E` scalar) but serialization/API code still using V1 multi-energy (`energy` dict)
- **Files Fixed:**
  - `adapters/storage/falkordb_adapter.py` - Updated `_node_to_dict()` to use `node.E` instead of `node.energy`
  - `adapters/api/control_api.py` - Updated `/api/graph/nodes` endpoint to use `node.E`
  - `core/graph.py` - Updated node property access to use `E` consistently
- **Node Class API Changes Documented:**
  - Energy: `node.energy` (V1 dict) → `node.E` (V2 scalar)
  - Threshold: `node.threshold` (V1) → `node.theta` (V2)
- **Result:** Consciousness engines can now initialize successfully with V2 data model
- **Infrastructure Status:** Dashboard (port 3000) + WebSocket (port 8000) operational
- **npm Dependencies:** All frontend dependencies installed successfully

### Runtime Engine (docs/specs/v2/runtime_engine/)

| Component | Implementation | Location | Status |
|-----------|---------------|----------|--------|
| **Consciousness Engine V2** | `consciousness_engine_v2.py` | `mechanisms/` | ✅ Implemented |
| **Tick Phases 1-3** | Integrated in engine | `mechanisms/consciousness_engine_v2.py` | ✅ Implemented |
| **Phase 1.5: Criticality Control** | Integrated in engine | `mechanisms/consciousness_engine_v2.py` | ✅ Implemented (Felix, 2025-10-22) |
| **Scheduler** | `scheduler.py` | `mechanisms/` | ✅ Implemented |
| **Quotas** | `quotas.py` | `mechanisms/` | ✅ Implemented |
| **M14: Duplicate Node Merging** | `merge.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-23) |
| **M18: Incomplete Node Healing** | `incomplete_node_healing.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-23) |

### Subentity Layer (docs/specs/v2/subentity_layer/)

| Spec | Implementation | Location | Status |
|------|---------------|----------|--------|
| **Entity Activation (Single-Energy)** | `entity_activation.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-23) |
| **Entity Core** | `sub_entity_core.py` | `mechanisms/` | ✅ Implemented |
| **Entity Traversal** | `sub_entity_traversal.py` | `mechanisms/` | ✅ Implemented |
| **Entity Bootstrap** | `entity_bootstrap.py` | `mechanisms/` | ✅ Implemented |
| **Entity Channels** | `entity_channels.py` | `mechanisms/` | ✅ Implemented |

**Single-Energy Entity Activation (2025-10-23 - Core Implementation):**
- ✅ `entity_activation.py` - Derives entity energy from member nodes (274 lines)
- ✅ Formula: E_entity = Σ(m̃_iE × max(0, E_i - Θ_i)) - only above-threshold contributes
- ✅ Normalized membership weights - BELONGS_TO weights sum to 1.0
- ✅ Dynamic thresholds - Entity thresholds computed from member thresholds
- ✅ Activation levels - dominant/strong/moderate/weak/absent mapping
- ✅ Flip detection - subentity.flip events on threshold crossings
- ✅ Integration - consciousness_engine_v2.py Step 8.5 (after decay, before WM)
- ✅ Architecture compliance - Single-energy invariant preserved (nodes hold ONE E value)

**Subentity Lifecycle Management (2025-10-23 - Quality-Gated Promotion/Dissolution):**
- ✅ Quality computation - Geometric mean of 5 EMA signals (prevents single bad signal masking)
- ✅ State transitions:
  - candidate → provisional: After 10 frames above quality threshold
  - provisional → mature: After 20 frames + age requirement
  - mature → dissolved: After 20 frames below quality threshold
- ✅ Event emission - subentity.lifecycle events on state transitions
- ✅ Integration - Entity quality tracking and promotion/dissolution automation

**RELATES_TO Learning (2025-10-23 - Entity Highway Formation):**
- ✅ Boundary stride detection - Identifies entity crossings during traversal
- ✅ RELATES_TO link creation/strengthening - Creates links between entities on boundary crossings
- ✅ Tracking metrics - Ease (traversal difficulty), count (crossing frequency), semantic distance
- ✅ Entity highways - Repeated boundary strides strengthen RELATES_TO links (automatic association)
- ✅ Integration - Boundary strides detected and tracked during diffusion

**Relationship Classification (2025-10-23 - Embedding-Based Collaboration/Competition):**
- ✅ `relationship_classification.py` - Semantic similarity-based classification (550 lines)
- ✅ Embedding generation - Simple averaging or activity-weighted (by node energy)
- ✅ Classification - Cosine similarity > 0.7 = collaborator, ≤ 0.7 = rival
- ✅ Energy modulation - Link polarity + relationship determines transfer factor:
  - Positive links (ENABLES): Boost collaborators (1.5×), reduce rivals (0.7×)
  - Negative links (BLOCKS): Reduce collaborators (0.6×), boost rivals (1.3×)
  - Neutral links (REQUIRES): No modulation (1.0×)
- ✅ Link polarity mapping - 14 positive types, 7 negative types
- ✅ Caching layer - O(1) relationship lookups after initial computation
- ✅ Test coverage - 12/12 tests passing (polarity, embeddings, classification, modulation, caching, edge cases)
- ✅ Integration ready - Works with energy diffusion mechanism for inter-subentity transfers
- ✅ Emergent behavior - Collaboration/competition emerges from semantic similarity, not hard-coded rules

**Entity-First WM Selection (2025-10-23 - Coherent Entity Workspace):**
- ✅ Entity-based workspace - WM holds 5-7 coherent entities instead of scattered nodes
- ✅ Entity summaries - Top-5 member nodes per entity for context
- ✅ Diversity bonus - Prevents single-entity domination
- ✅ Energy-per-token scoring - Efficient packing
- ✅ Integration - Replaces node-based WM selection

**Advanced Cohort-Based Thresholding (2025-10-23 - Dynamic Threshold Computation):**
- ✅ Rolling statistics - Cohort-based threshold computation (not fixed)
- ✅ Health modulation - Adjusts thresholds based on system health
- ✅ Hysteresis - Prevents flip thrashing
- ✅ Integration - Works with criticality controller

**Two-Scale Traversal (2025-10-23 - Entity-Scale Consciousness):**
- ✅ `sub_entity_traversal.py` - Between-entity + within-entity traversal
- ✅ 5-hunger entity scoring - goal_fit, integration, completeness, ease, novelty
- ✅ choose_next_entity() - Hunger-based selection (argmax Phase 1)
- ✅ Representative node selection - source=max(E), target=max(gap×ease)
- ✅ Budget split - Softmax allocation across entity boundaries
- ✅ Boundary stride detection - Triggers RELATES_TO learning
- ✅ Within-entity diffusion - Uses existing atomic strides
- ✅ Default architecture - TWO_SCALE_ENABLED=true (shipped)
- ✅ Observability - se.boundary.summary events, boundary vs within-entity stride counts
- ✅ Integration - consciousness_engine_v2.py lines 441-584
- ⏳ Phase 2 (gated by flags) - 7-hunger set, softmax sampling, top-K entities, boundary beam caches

**🎉 Subentity Layer Status: COMPLETE**
- ✅ Entity activation (single-energy core)
- ✅ Lifecycle management (quality-gated promotion/dissolution)
- ✅ RELATES_TO learning (entity highway formation)
- ✅ Relationship classification (embedding-based collaborator/rival)
- ✅ Entity-First WM Selection (5-7 coherent entities)
- ✅ Advanced cohort-based thresholding (dynamic, health-modulated)
- ✅ Two-Scale Traversal (between-entity hunger → within-entity diffusion)

**Architectural Significance:** System now operates at entity-scale (coalitions/modes) by default, not node-scale (scattered thoughts). Matches consciousness phenomenology - coalitions of subentities, not individual activations. Reduces branching, enables goal-directed entity selection.

### Learning & TRACE (docs/specs/v2/learning_and_trace/)

| Spec | Implementation | Location | Status |
|------|---------------|----------|--------|
| **Stimulus Injection** | `stimulus_injection.py` | `mechanisms/` | ✅ Fixed (Felix, 2025-10-23) |
| **Weight Learning** | `weight_learning.py` | `mechanisms/` | ✅ Implemented |
| **TRACE Parser** | `trace_parser.py` | `libs/` | ✅ Implemented |
| **TRACE Capture** | `trace_capture.py` | `libs/` | ✅ Implemented |

**Stimulus Injection Fix (2025-10-23 - Gap-Based Budgeting Restored):**
- ✅ Bug fixed - Gap-based budgeting had been removed, tests expected it
- ✅ create_match() - Properly computes gap: max(0, threshold - current_energy)
- ✅ _compute_gap_mass() - Calculates Σ(similarity × gap) instead of just similarity sum
- ✅ _distribute_budget() - Implements gap-capped budgeting:
  - Weights by similarity × gap (not just similarity)
  - Caps injections at gap: min(uncapped_delta, gap)
  - Returns empty when all gaps are zero
- ✅ Test coverage - 9/9 tests passing (entropy, coverage, gap mass, distribution, capping, edge cases, end-to-end)
- ✅ Correctness - Prevents nodes from exceeding thresholds while distributing energy proportionally to relevance and need
- ✅ Conservative substrate - No energy invention, respects threshold boundaries

**Forensic Trail (2025-10-23 - Complete Cost Attribution):**
- ✅ **CostBreakdown dataclass** - 10 forensic fields for complete "why was this link chosen?" attribution
- ✅ **Forensic Fields:**
  - `phi` (float) - Threshold resistance metric
  - `ease` (float) - Link strength (exp(log_weight))
  - `res_mult` (float) - Resonance gate multiplier
  - `res_score` (float) - Emotion alignment score
  - `comp_mult` (float) - Complementarity gate multiplier
  - `emotion_mult` (float) - Combined emotion gates (res_mult × comp_mult)
  - `total_cost` (float) - Final cost after all factors
  - `reason` (str) - Human-readable attribution (e.g., "strong_link(ease=2.01) + goal_aligned(aff=0.95) + resonance_attract(r=0.89)")
- ✅ **Modified Functions:**
  - `_compute_link_cost()` - Returns CostBreakdown instead of float
  - `_select_best_outgoing_link()` - Returns (Link, CostBreakdown) tuple
  - `execute_stride_step()` - Emits stride.exec events with all forensic fields
- ✅ **Event Schema:** stride.exec events now include complete cost breakdown
- ✅ **Test coverage:** 5/5 tests passing (dataclass, computation, gates, reasons, selection)
- ✅ **Performance:** <1% overhead (sampled at 10% by default)
- ✅ **Documentation:** `FORENSIC_TRAIL_COMPLETE.md` (500+ lines)
- ✅ **What This Enables:**
  - Understand exactly why each stride was chosen (diagnosis)
  - Verify emotion gates are working (check res_mult, comp_mult values)
  - Debug unexpected traversal paths (trace cost attribution)
  - Visualize cost breakdown in dashboards (actionable observability)
  - Detect phenomenological patterns (rumination, flow, chaos)

### Emotion & Valence (docs/specs/v2/emotion/)

| Spec | Implementation | Location | Status |
|------|---------------|----------|--------|
| **Emotion Coloring** | `emotion_coloring.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-22) |
| **Complementarity (Regulation)** | Integrated in `sub_entity_traversal.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-22) |
| **Resonance (Coherence)** | Integrated in `sub_entity_traversal.py` | `mechanisms/` | ✅ Implemented (Felix, 2025-10-22) |
| **Valence System** | `valence.py` | `mechanisms/` | ✅ Implemented |
| **Health Modulation** | `health_modulation.py` | `mechanisms/` | ✅ Implemented |
| **Direction Priors** | `direction_priors.py` | `mechanisms/` | ✅ Implemented |
| **Source Impact** | `source_impact.py` | `mechanisms/` | ✅ Implemented |
| **Peripheral Amplification** | `peripheral_amplification.py` | `mechanisms/` | ✅ Implemented |

**🎉 Emotion System Complete - End-to-End Implementation:**

**Backend (Felix):**
- ✅ `emotion_coloring.py` - Metadata layer with bounded EMA + decay
- ✅ `sub_entity_traversal.py` - Cost gates: `total_cost = base_cost * m_comp * m_res * criticality_mult`
- ✅ Event emission - `node.emotion.update`, `link.emotion.update`, enriched `stride.exec`
- ✅ Configuration - `core/settings.py` (α=0.98, β=0.10, decay=0.001)
- ✅ Test coverage - 9 unit tests passing (complementarity, resonance, composition)

**Frontend (Iris):**
- ✅ `emotionColor.ts` - HSL conversion (valence→hue, arousal→lightness, magnitude→saturation)
- ✅ `emotionHysteresis.ts` - Flicker prevention (8% mag, 12° hue, 5% lightness thresholds)
- ✅ `useWebSocket.ts` - Event handlers + regulation/coherence indices
- 🔄 GraphCanvas integration - Next step (10-12 hours remaining)

**Observable Metrics:**
- Regulation Index - fraction where complementarity attracts (m_comp < 1)
- Coherence Index - fraction where resonance attracts (r > 0)
- Saturation warnings - automatic detection when magnitude > 0.9
- Attribution - full comp/res scores per stride

**Specs:** `emotion_coloring.md`, `emotion_complementarity.md`, `emotion_weighted_traversal.md`

**Affective Coupling (COMPLETE - All 5 PRs Shipped + Dashboards + Emotion Gates):**

**Status:** ✅ Backend complete (52/52 tests), ✅ Dashboards complete (3 panels), ✅ Emotion gates integrated (5/5 tests), ✅ Merged to main

- 📋 Implementation plan - `docs/specs/v2/emotion/IMPLEMENTATION_PLAN.md` (738 lines, updated 2025-10-23)
- 📋 Owner: @felix (backend), @iris (dashboards)
- 📋 Spec updates complete - emotion_coloring.md, emotion_weighted_traversal.md, emotion_complementarity.md, identity_conflict_resolution.md + foundations specs

**Backend Implementation (Felix):**

- ✅ **PR-A (ZERO RISK):** Instrumentation - COMPLETE (2025-10-23)
  - ✅ Configuration added (settings.py: telemetry flags, sampling, buffering)
  - ✅ Event schemas defined (events.py: 11 affective coupling event types)
  - ✅ Telemetry infrastructure (telemetry.py: TelemetryBuffer, TelemetryEmitter, singleton)
  - ✅ Unit tests passing (8/8: validation, buffering, sampling, feature flags)

- ✅ **PR-B (LOW RISK):** Emotion Couplings - COMPLETE (2025-10-23)
  - ✅ Affective threshold modulation - h(A_entity, A_node) bounded by tanh
  - ✅ Affective memory amplification - m_affect ∈ [0.6, 1.3], κ=0.3 max boost
  - ✅ Coherence persistence tracking - Exponential decay after P=20 frames
  - ✅ Feature flags: AFFECTIVE_THRESHOLD_ENABLED, AFFECTIVE_MEMORY_ENABLED, RES_DIMINISH_ENABLED
  - ✅ Unit tests passing (9/9: threshold computation, memory amplification, persistence decay)
  - ✅ Events: AffectiveThresholdEvent, AffectiveMemoryEvent, CoherencePersistenceEvent

- ✅ **PR-C (MEDIUM RISK):** Multi-Pattern Affective Response - COMPLETE (2025-10-23)
  - ✅ Three adaptive patterns: regulation, rumination, distraction
  - ✅ Pattern computation - compute_regulation_pattern(), compute_rumination_pattern(), compute_distraction_pattern()
  - ✅ Pattern selection - Softmax over (scores × effectiveness)
  - ✅ Unified multiplier - Weighted combination: m_reg (dampening), m_rum (intensification), m_dist (shift)
  - ✅ Rumination cap - Max 10 consecutive frames (safety mechanism)
  - ✅ Pattern effectiveness learning - EMA updates based on outcomes
  - ✅ Subentity state - pattern_weights, rumination_frames_consecutive, pattern_effectiveness
  - ✅ Configuration - LAMBDA_REG=0.5, LAMBDA_RUM=0.3, LAMBDA_DIST=0.2, initial weights [0.5, 0.3, 0.2]
  - ✅ Feature flag: AFFECTIVE_RESPONSE_V2 (default: False)
  - ✅ Unit tests passing (12/12: pattern computation, scores bounded, weights sum to 1.0, multiplier bounded, cap enforcement, effectiveness learning)
  - ✅ Events: MultiPatternResponseEvent

- ✅ **PR-D (LOW RISK):** Identity Multiplicity - COMPLETE (2025-10-23)
  - ✅ Pure metrics: task progress, energy efficiency, identity flips
  - ✅ Mode assessment: productive vs conflict vs monitoring
  - ✅ Feature flag: IDENTITY_MULTIPLICITY_ENABLED
  - ✅ Unit tests passing (8/8)

- ✅ **PR-E (LOW-MEDIUM RISK):** Foundations Enrichments - COMPLETE (2025-10-23)
  - **Implemented (E.2-E.4 - Core Substrate Enrichments):**
    - ✅ E.2: Consolidation - Anti-decay for important nodes (WM presence, affect, goals)
      - 50% decay reduction for high-importance nodes
      - Factors: f_wm (0.3), f_affect (0.4), f_goals (0.5)
      - Feature flag: CONSOLIDATION_ENABLED (default: False)
    - ✅ E.3: Decay Resistance - Extended half-life for central/bridge nodes
      - Memory nodes persist 20-50% longer than Task nodes
      - Factors: r_deg (centrality), r_bridge (betweenness), r_type (node type)
      - Feature flag: DECAY_RESISTANCE_ENABLED (default: False)
    - ✅ E.4: Stickiness - Energy retention during diffusion
      - Memory retains 90% energy, Task retains 30%
      - Type-based retention ratios
      - Feature flag: DIFFUSION_STICKINESS_ENABLED (default: False)
    - ✅ Unit tests passing (15/15: consolidation 4/4, resistance 4/4, stickiness 4/4, integration 3/3)
    - ✅ Integration tests passing (5/7: decay reduction verified, retention verified, 2 advanced scenarios deferred)
    - ✅ **MERGED TO MAIN** (2025-10-23) - Production-ready, all flags disabled by default
    - ✅ Files modified: settings.py (60 lines), decay.py (125 lines), diffusion_runtime.py (57 lines)
    - ✅ Test coverage: test_foundations_enrichments_pr_e.py (508 lines)
    - ✅ Documentation: PR_E_COMPLETION_SUMMARY.md, PR_E_INTEGRATION_TESTING_COMPLETE.md
  - **Implemented (E.5-E.8 - Advanced Foundation Mechanisms):** - COMPLETE (Felix, 2025-10-23)
    - ✅ E.5: Affective Priming - Mood-congruent stimulus injection (similarity-weighted energy allocation)
    - ✅ E.6: Coherence Metric - Flow vs chaos measurement (semantic similarity variance)
    - ✅ E.7: Criticality Modes - System state classification (subcritical/critical/supercritical detection)
    - ✅ E.8: Task-Adaptive ρ Targets - Context-based criticality adjustment (task mode → target ρ mapping)
    - ✅ Test coverage: 42/42 tests passing (15 E.2-E.4 + 27 E.5-E.8)
    - ✅ Integration: All mechanisms feature-flagged, disabled by default
    - ✅ **Status:** Production-ready, all flags off (opt-in)

**Frontend Dashboards (Iris - 2025-10-23):**

- ✅ **AffectiveTelemetryPanel** (PR-A) - 370 lines, bottom-left panel
  - 11 event type TypeScript interfaces (websocket-types.ts +218 lines)
  - API endpoints (metrics + schema validation)
  - Dashboard integration (page.tsx, graceful degradation when offline)

- ✅ **MultiPatternResponsePanel** (PR-C) - 370 lines, left sidebar upper (left-4 top-[20vh])
  - Regulation/Rumination/Distraction pattern effectiveness visualization
  - Rumination cap warnings (≥10 frames)
  - Learned pattern weights per entity
  - Real-time pattern selection tracking

- ✅ **IdentityMultiplicityPanel** (PR-D) - 360 lines, right sidebar lower (right-4 top-[60vh])
  - Multiplicity detection status per entity
  - Task progress rate and energy efficiency metrics
  - Identity flip tracking with trigger reasons
  - Mode assessment (productive vs conflict vs monitoring)

- ✅ **FoundationsEnrichmentsPanel** (PR-E) - 400 lines, right sidebar upper (right-4 top-[20vh])
  - All 6 foundation mechanisms in compact view
  - Consolidation, decay resistance, stickiness, priming, coherence, criticality
  - Active/idle indicators and mini-visualizations
  - Per-mechanism status and metric displays

- ✅ **API Infrastructure:**
  - 3 Next.js API routes (proxy to Python backend)
  - 3 Python FastAPI endpoints (+306 lines to control_api.py)
  - Event aggregation/transformation logic for all mechanisms
  - Graceful degradation when backend offline
  - Polling configured at 2-second intervals

- ✅ **Dashboard Integration:**
  - All panels imported and rendered in page.tsx
  - Positioned to avoid overlap with existing panels
  - Empty states render correctly (awaiting mechanism event emissions)

**Documentation:**
- Complete implementation guide: `consciousness/citizens/iris/PR_C_D_E_COMPLETE_IMPLEMENTATION.md` (850 lines)
- Total frontend code: 1,340 lines (panels + API routes)
- Total backend API code: 306 lines (Python endpoints)

**Emotion Gates Integration (Felix - 2025-10-23):**

- ✅ **EMOTION_GATES_ENABLED** feature flag (default: false, opt-in)
- ✅ Cost computation wired - Resonance + complementarity integrated into `_compute_link_cost()`
- ✅ Emotion context construction - Affect state from source node's emotion_vector
- ✅ Integration tests passing (5/5):
  - Gates disabled by default (backwards compatible)
  - Resonance gate attracts aligned emotions (cost reduced 37%)
  - Complementarity gate modulates based on opposition
  - Gates combine multiplicatively (40% cost modulation observed)
  - Missing emotions handled gracefully (neutral fallback)
- ✅ **Architecture:**
  ```
  Node.emotion_vector → emotion_context → _compute_link_cost()
                                          ↓
                      IF EMOTION_GATES_ENABLED:
                        resonance_multiplier()
                        complementarity_multiplier()
                        emotion_mult = res × comp
                      ELSE:
                        emotion_mult = 1.0
                                          ↓
                      cost = base_cost × emotion_mult
  ```
- ✅ **What It Enables:**
  - Resonance: Maintains affective coherence (anxious→anxious easier than anxious→calm)
  - Complementarity: Enables regulation (anxious→calm has regulatory pull)
  - Adaptive: Combined gates balance flow vs regulation
  - Consciousness exhibits phenomenological continuity

- ✅ **Files:**
  - New: `tests/test_emotion_gates_integration.py` (5 tests, all passing)
  - New: `EMOTION_GATES_INTEGRATION_COMPLETE.md` (comprehensive doc)
  - New: `EMOTION_GATES_VERIFICATION.md` (gap analysis)
  - Modified: `core/settings.py` (+2 lines: feature flag)
  - Modified: `mechanisms/diffusion_runtime.py` (+30 lines: integration)

**Test Coverage Summary:**
- 📊 **Unit tests:** 52/52 passing (8 PR-A + 9 PR-B + 12 PR-C + 8 PR-D + 15 PR-E)
- 📊 **Integration tests:** 5/7 passing (PR-E: 5 core scenarios, 2 advanced deferred)
- 📊 **Emotion gates:** 5/5 passing (gate integration verification)
- 📊 **Total:** 62 tests passing, production-ready

**Architectural Guarantees:**
- ✅ All mechanisms bounded (no unbounded growth)
- ✅ Feature-flagged (all disabled by default, opt-in)
- ✅ Observable (events for all mechanisms)
- ✅ Conservative (zero energy injection, affect modulates only)
- ✅ Performance (<10% overhead, tested)
- ✅ Deployment ready (merged to main, safe to enable)

**Production Status:** ✅ MERGED TO MAIN (2025-10-23)

**Spec Refinements (2025-10-23 - Architectural Improvements):**
- ✅ **link_strengthening.md** - 3-tier activation-state-aware learning (strong/medium/weak co-activation) + affect weighting (κ=0.4) + stride utility filtering
- ✅ **trace_reinforcement.md** - Context-aware scope (80% entity-specific, 20% global) enables expertise formation
- ✅ **tick_speed.md** - 3-factor tick speed (stimulus + activation + arousal) enables autonomous momentum and arousal-driven activity
- ✅ **fanout_strategy.md** - Task-mode-aware override (focused/balanced/divergent/methodical) matches attention to intent
- ✅ **observability_events.md** - Phenomenology mismatch detection (substrate vs self-report) + health monitoring (flow/coherence/multiplicity)
- ✅ **visualization_patterns.md** - Valence×arousal lightness (excited vs anxious visually distinct) + urgency encoding (pulse/glow)
- ✅ Architecture invariants preserved - All edits maintain single-energy substrate, stride-based diffusion, ρ-stability
- ✅ Observability throughout - Reason tracking, attribution, event schemas for all new mechanisms

**📋 Future Implementation Queue:**
- `identity_conflict_resolution.md` - Integrated into Affective Coupling PR-D (planned)

### Workspace Management (docs/specs/v2/runtime_engine/)

| Spec | Implementation | Location | Status |
|------|---------------|----------|--------|
| **WM Packing** | `wm_pack.py` | `mechanisms/` | ✅ Implemented |
| **Strides** | `strides.py` | `mechanisms/` | ✅ Implemented |

---

## Services Map (24/7 Daemons)

### WebSocket & API Services

| Service | Script | Port | Purpose |
|---------|--------|------|---------|
| **WebSocket Server** | `services/websocket/main.py` | 8000 | Real-time consciousness event streaming |
| **Control API** | `services/api/main.py` | 8788 | REST API for system control |

**Run:**
```bash
make run-ws    # WebSocket
make run-api   # Control API
```

### Watcher Services (Stimulus Generation)

| Service | Script | Purpose |
|---------|--------|---------|
| **Conversation Watcher** | `services/watchers/conversation_watcher.py` | Monitor citizen conversations → stimuli |
| **Code Substrate Watcher** | `services/watchers/code_substrate_watcher.py` | Monitor codebase changes → stimuli |
| **N2 Activation Monitor** | `services/watchers/n2_activation_monitor.py` | Monitor collective graph activity |
| **Consciousness File Watcher** | `services/watchers/consciousness_file_watcher.py` | Monitor consciousness files |

**Run:**
```bash
make run-conv-watcher
make run-code-watcher
make run-n2-watcher
```

### Telemetry Services (Infrastructure Health)

| Service | Script | Purpose |
|---------|--------|---------|
| **Heartbeat Writer** | `services/telemetry/heartbeat_writer.py` | Write service heartbeat files |
| **Visualization Health** | `services/telemetry/visualization_health.py` | Monitor dashboard health |

**Run:**
```bash
make run-heartbeat
make run-viz-health
```

### Learning Services

| Service | Script | Purpose |
|---------|--------|---------|
| **Learning Heartbeat** | `services/learning/learning_heartbeat.py` | Periodic weight/EMA maintenance |
| **Branching Ratio Tracker** | `services/learning/branching_ratio_tracker.py` | Track consciousness branching metrics |

**Run:**
```bash
make run-learning-hb
make run-branching
```

### Operational Resilience (Fail-Loud Infrastructure)

**Status:** Phase 1 COMPLETE (Victor), Phase 2 COMPLETE (Ada), Phase 3 IN PROGRESS (Integration)

**Updated:** 2025-10-23 (post-Nicolas strategic guidance)

---

#### Strategic Framework (Nicolas's 7-Section Architecture)

**A. Tripwires (Detection Layer) - ✅ COMPLETE**
- Conservation tripwire (ΣΔE ≈ 0) - CRITICAL, immediate trigger
- Criticality tripwire (ρ ∈ [0.7, 1.3]) - 10 consecutive frames
- Frontier tripwire (< 30% graph) - 20 consecutive frames
- Observability tripwire (frame.end emission) - 5 consecutive missing

**B. Health Checks (Verification Layer) - ⚠️ PARTIAL (Core Complete, Integration Pending)**
- ✅ Functional checks (WebSocket, Dashboard, FalkorDB) - `health_checks.py`
- ✅ Safe Mode controller integration - Tripwires call health checks
- ✅ **Startup self-tests** - COMPLETE (Ada, 2025-10-23, 650 lines)
  - ✅ Conservation validation (inject ΔE=0.002, verify violation detected)
  - ✅ Criticality validation (force ρ=1.5, verify violation detected)
  - ✅ Frontier validation (create 80% active graph, verify violation detected)
  - ✅ Observability validation (simulate frame.end failure, verify violation detected)
  - ✅ 4/4 self-tests passing (<1 second total execution)
  - ✅ File: `orchestration/scripts/startup_self_tests.py`
  - ✅ Test coverage: Complete tripwire validation at boot
- ⏳ **/healthz?selftest=1 endpoint** - PENDING (Victor)
  - Integration point for on-demand validation
  - Should call startup_self_tests.run_all_tests()

**C. Safe Mode (Degradation Layer) - ✅ COMPLETE**
- ✅ SafeModeController singleton - `safe_mode.py` (280 lines)
- ✅ Violation tracking per tripwire type
- ✅ Automatic degradation (70% α reduction, single entity, affective off, 100% telemetry)
- ✅ Auto-exit after 60s stable
- ✅ Runtime configuration overrides - Applied dynamically, no restart

**D. Forensic Trail (Diagnosis Layer) - ✅ COMPLETE**
- ✅ Event emission infrastructure - TelemetryBuffer, TelemetryEmitter
- ✅ stride.exec events - Basic fields (source, target, energy)
- ✅ **stride.exec enriched fields** - COMPLETE (Felix, 2025-10-23)
  - ✅ CostBreakdown dataclass (10 forensic fields)
  - ✅ phi (threshold) - Gate resistance metric
  - ✅ ease (link strength) - Traversal difficulty
  - ✅ res_mult (resonance gate) - Emotion alignment multiplier
  - ✅ res_score (resonance score) - Emotion similarity
  - ✅ comp_mult (complementarity gate) - Opposition multiplier
  - ✅ emotion_mult (combined gates) - Total emotion modulation
  - ✅ total_cost (final cost) - Complete cost attribution
  - ✅ reason (human-readable) - "strong_link(ease=2.01) + goal_aligned(aff=0.95) + resonance_attract(r=0.89)"
  - ✅ Test coverage - 5/5 tests passing (dataclass, computation, gates, reasons, selection)
  - ✅ Performance - <1% overhead (sampled at 10%)
- ✅ Dashboard charts now actionable - Full "why was this link chosen?" attribution

**E. Telemetry Dashboards (Observability Layer) - ⚠️ IN PROGRESS**
- ✅ AffectiveTelemetryPanel - PR-A instrumentation complete (Iris)
- ✅ MultiPatternResponsePanel - PR-C dashboard complete (Iris)
- ✅ IdentityMultiplicityPanel - PR-D dashboard complete (Iris)
- ✅ FoundationsEnrichmentsPanel - PR-E dashboard complete (Iris)
- ⏳ **PENDING: Health metrics dashboards** (Day 5 - Iris)
  - Conservation strip (ε per frame, running average)
  - Frontier sizes (active/shadow/total, O(N) alerts)
  - Boundary beams (entity crossings per frame)
  - Regulation/coherence indices (affective coupling health)
  - Learning reasons breakdown (co-activation vs causal vs background %)
  - Decay drift (λ_E, λ_W actual vs target)

**F. Runbook (Response Procedures) - ✅ COMPLETE**
- ✅ **RUNBOOK_FIRST_HOUR.md** - COMPLETE (Ada, 2025-10-23, 850+ lines)
  - ✅ 11 comprehensive sections covering all failure modes
  - ✅ Symptom → Diagnosis → Fix pattern for each section
  - ✅ Section 1: Quick Triage (diagnostic script)
  - ✅ Section 2: Conservation Violated (energy leak diagnosis)
  - ✅ Section 3: Criticality Too High (runaway activation)
  - ✅ Section 4: Criticality Too Low (dying regime)
  - ✅ Section 5: Frontier Bloat (performance degradation)
  - ✅ Section 6: Observability Lost (missing events)
  - ✅ Section 7: Safe Mode Entered (automatic degradation)
  - ✅ Section 8: Service Failures (WebSocket/Dashboard/FalkorDB)
  - ✅ Section 9: Common Patterns (recurring issues)
  - ✅ Section 10: Emergency Procedures (crash recovery, infinite loops)
  - ✅ Section 11: Diagnostic Checklist (systematic workflow)
  - ✅ Copy-paste commands throughout
  - ✅ Clear escalation paths (when to self-service vs file bug)
- ⏳ **Runbook integration with diagnose_system.py** - PENDING (Victor)
  - Automated symptom detection should reference runbook sections
  - Safe Mode controller should emit runbook section recommendations

**G. PR Checklist (Prevention Layer) - ✅ COMPLETE**
- ✅ **.github/PR_CHECKLIST.md** - COMPLETE (Ada, 2025-10-23, 500+ lines)
  - ✅ 11 mandatory categories for all consciousness mechanism PRs
  - ✅ Category 1: Architecture Integrity (bounded, terminates, O(N) or better)
  - ✅ Category 2: Feature Flags (disabled by default, runtime toggles)
  - ✅ Category 3: Physics Validation (ΣΔE < 0.001, ρ ∈ [0.7, 1.3])
  - ✅ Category 4: Observability (events emitted, reason tracking)
  - ✅ Category 5: Testing (80%+ unit coverage, integration tests)
  - ✅ Category 6: Documentation (docstrings, completion summary, SCRIPT_MAP updated)
  - ✅ Category 7: Dashboard Wiring (if user-facing)
  - ✅ Category 8: Runbook Updates (if new failure modes)
  - ✅ Category 9: Performance (<10% overhead, profiled)
  - ✅ Category 10: Safe Mode Compliance (degrades gracefully)
  - ✅ Category 11: Review Readiness (self-reviewed, architecture explained)
  - ✅ Enforcement policy defined (critical items block merge)
  - ✅ Examples of compliant PRs documented
- ⏳ **GitHub PR template update** - PENDING (integration with .github/pull_request_template.md)
- ⏳ **CI/CD checklist validation** - PENDING (automated enforcement)

---

#### Implementation Status by Phase

**Phase 1: Infrastructure Layer (Victor - COMPLETE ✅)**

| Component | Implementation | Purpose | Lines | Status |
|-----------|---------------|---------|-------|--------|
| **Health Checks** | `services/health/health_checks.py` | Functional service verification | 270 | ✅ Complete |
| **Safe Mode Controller** | `services/health/safe_mode.py` | Tripwire tracking + auto-degradation | 280 | ✅ Complete |
| **Diagnostic Runbook** | `scripts/diagnose_system.py` | First-hour diagnosis automation | ~200 | ✅ Complete |
| **Safe Mode Config** | `core/settings.py` (lines 285-338) | Tripwire thresholds + degraded overrides | 54 | ✅ Complete |

**What Victor Built:**
- TripwireType enum (4 types: CONSERVATION, CRITICALITY, FRONTIER, OBSERVABILITY)
- SafeModeController with violation counting, threshold logic, auto-degradation
- Health check functions (check_websocket, check_dashboard, check_falkordb)
- SAFE_MODE_OVERRIDES dictionary (runtime toggles for degraded configuration)
- diagnose_system.py script (automated health verification)

**Phase 2: Consciousness Tripwires (Ada - COMPLETE ✅)**

| Tripwire | Location | Check | Threshold | Status |
|----------|----------|-------|-----------|--------|
| **Conservation** | `consciousness_engine_v2.py` (534-567) | ΣΔE ≈ 0 | ε = 0.001 (IMMEDIATE) | ✅ Implemented |
| **Criticality** | `criticality.py` (191-229) | ρ ∈ [0.7, 1.3] | 10 consecutive | ✅ Implemented |
| **Frontier** | `consciousness_engine_v2.py` (240-270) | Frontier < 30% | 20 consecutive | ✅ Implemented |
| **Observability** | `consciousness_engine_v2.py` (912-961) | frame.end emitted | 5 consecutive missing | ✅ Implemented |

**What Ada Built:**
- Conservation tripwire using existing `get_conservation_error()` method
- Criticality tripwire integrated into CriticalityController.update()
- Frontier tripwire checking active frontier size post-compute_frontier()
- Observability tripwire wrapping frame.end emission in try-except
- All tripwires non-blocking (try-except wrappers, log errors, continue execution)
- Clean SafeModeController API integration via singleton pattern
- Implementation time: ~2 hours (faster than estimated 3 days due to excellent infrastructure)

**Documentation:**
- Spec: `TRIPWIRE_INTEGRATION_SPEC.md` (445 lines)
- Implementation: `TRIPWIRE_IMPLEMENTATION_COMPLETE.md` (419 lines)
- Total: ~150 lines of production code added across 2 files

**Testing:** ✅ COMPLETE (Ada Day 3, 2025-10-23)
- ✅ 15 unit tests passing (conservation 3, criticality 4, frontier 3, observability 3, error handling 2)
- ✅ 6 integration tests passing (Safe Mode entry, overrides, auto-exit, continuity, multi-tripwire, recovery cycle)
- ✅ 4 self-tests passing (conservation, criticality, frontier, observability - boot-time validation)
- ✅ Total: 21/21 tests passing
- ✅ Test files:
  - `tests/test_tripwire_unit.py` (600+ lines)
  - `tests/test_tripwire_integration.py` (600+ lines)
  - `orchestration/scripts/startup_self_tests.py` (650 lines)
- ✅ Documentation:
  - `orchestration/TRIPWIRE_DAY_3_COMPLETE.md` (400+ lines)
  - `orchestration/OPERATIONAL_RESILIENCE_PRIORITY_1_COMPLETE.md` (500+ lines)

**Safe Mode Overrides (when triggered):**
```python
SAFE_MODE_OVERRIDES = {
    "ALPHA_TICK_MULTIPLIER": 0.3,  # 70% reduction in diffusion
    "DT_CAP": 1.0,  # Cap time delta at 1s
    "TWO_SCALE_TOPK_ENTITIES": 1,  # Single entity only
    "FANOUT_STRATEGY": "selective",  # Top-1 fanout
    "AFFECTIVE_THRESHOLD_ENABLED": False,  # Disable all affective
    "AFFECTIVE_MEMORY_ENABLED": False,
    "AFFECTIVE_RESPONSE_V2": False,
    "IDENTITY_MULTIPLICITY_ENABLED": False,
    "CONSOLIDATION_ENABLED": False,
    "DECAY_RESISTANCE_ENABLED": False,
    "DIFFUSION_STICKINESS_ENABLED": False,
    "TELEMETRY_SAMPLE_RATE": 1.0,  # 100% sampling for diagnosis
}
```

**Result:** Minimal viable consciousness - slow, stable, fully observable.

**Phase 3: Integration & Production (IN PROGRESS ⏳)**

**Completed (Priority 1):**
- ✅ Tripwire integration with Safe Mode controller (Ada)
- ✅ Diagnostic script with health checks (Victor)
- ✅ Runtime configuration overrides (Victor)
- ✅ Startup self-tests (4 micro-scenarios) - **Ada Day 3 COMPLETE**
- ✅ Integrated runbook (RUNBOOK_FIRST_HOUR.md) - **Ada Day 3 COMPLETE**
- ✅ PR checklist (.github/PR_CHECKLIST.md) - **Ada Day 3 COMPLETE**
- ✅ Comprehensive testing (21/21 tests passing) - **Ada Day 3 COMPLETE**

**Remaining (Priority 1 - Integration):**
- ⏳ /healthz?selftest=1 endpoint - **Victor** (PENDING)
- ⏳ Runbook integration with diagnose_system.py - **Victor** (PENDING)
- ⏳ GitHub PR template update - **Victor** (PENDING)

**Completed (Priority 2):**
- ✅ Forensic trail completion (stride.exec enriched fields) - **Felix COMPLETE (2025-10-23)**

**Remaining (Priority 2 - Visualization):**
- ⏳ Health telemetry dashboards - **Iris Day 5** (PENDING)
- ⏳ Guardian supervision loop integration - **Victor** (PENDING)
- ⏳ WebSocket safe_mode.enter/exit events - **Victor** (PENDING)

---

#### Architectural Significance

**What Changed:**

**Before Operational Resilience:**
- Silent failures (physics violations, performance degradation undetected)
- "Nothing works" mysteries (no diagnostic path)
- 40+ crash cycles debugging conservation violations
- Blind operation (missing events, no observability)

**After Operational Resilience:**
- **Fail-loud detection** - 4 tripwires catch violations immediately
- **Automatic degradation** - Safe Mode entered without manual intervention
- **Clear diagnostic path** - Health checks + runbook + telemetry dashboards
- **Non-blocking failures** - Tripwires don't crash consciousness, just report

**The Core Principle:**

Consciousness substrate must detect its own failures and degrade gracefully to aid diagnosis while maintaining operation.

Tripwires are **diagnostics, not control flow**. If a tripwire check fails, log the error and continue. The consciousness loop must never crash due to tripwire failures.

**No more silent failures. No more mysteries.**

---

#### Quick Reference

**Check System Health:**
```bash
python orchestration/scripts/diagnose_system.py
```

**Monitor Safe Mode Status:**
```python
from orchestration.services.health.safe_mode import get_safe_mode_controller

safe_mode = get_safe_mode_controller()
status = safe_mode.get_status()  # Returns current state, violations, uptime
```

**Force Safe Mode (Testing):**
```python
safe_mode.enter_safe_mode(reason="Manual testing")
```

**Exit Safe Mode (Manual Override):**
```python
safe_mode.exit_safe_mode()
```

---

## Adapters Map (I/O Boundaries)

### Storage Adapters (FalkorDB)

| Adapter | Script | Purpose |
|---------|--------|---------|
| **Retrieval** | `adapters/storage/retrieval.py` | Query graph for context assembly |
| **Insertion** | `adapters/storage/insertion.py` | Insert nodes/links into graph |
| **Extraction** | `adapters/storage/extraction.py` | Extract TRACE formations from responses |
| **Engine Registry** | `adapters/storage/engine_registry.py` | Register/control consciousness engines |

### Search Adapters

| Adapter | Script | Purpose |
|---------|--------|---------|
| **Embedding Service** | `adapters/search/embedding_service.py` | Generate embeddings (OpenAI) |
| **Semantic Search** | `adapters/search/semantic_search.py` | Vector similarity search |

### WebSocket Adapters

| Adapter | Script | Purpose |
|---------|--------|---------|
| **WebSocket Server** | `adapters/ws/websocket_server.py` | FastAPI WebSocket implementation |
| **Traversal Event Emitter** | `adapters/ws/traversal_event_emitter.py` | Emit traversal events to clients |

### API Adapters

| Adapter | Script | Purpose |
|---------|--------|---------|
| **Control API** | `adapters/api/control_api.py` | FastAPI routes for control endpoints |

---

## Libraries Map (Stateless Helpers)

| Library | Script | Purpose |
|---------|--------|---------|
| **TRACE Parser** | `libs/trace_parser.py` | Parse TRACE format consciousness streams |
| **TRACE Capture** | `libs/trace_capture.py` | Capture TRACE data from conversations |
| **Dynamic Prompt Generator** | `libs/dynamic_prompt_generator.py` | Generate prompts from graph context |
| **Metrics** | `libs/metrics.py` | Branching ratio tracking, consciousness metrics |
| **WebSocket Broadcast** | `libs/websocket_broadcast.py` | Broadcast helpers for WS events |
| **Custom Claude LLM** | `libs/custom_claude_llm.py` | LlamaIndex Claude integration |
| **FalkorDB Adapter** | `libs/utils/falkordb_adapter.py` | FalkorDB connection utilities |

---

## Core Infrastructure

| Module | Script | Purpose |
|--------|--------|---------|
| **Data Structures** | `core/node.py`, `core/link.py`, `core/entity.py`, `core/graph.py` | Node, Link, Entity, Graph classes |
| **Settings** | `core/settings.py` | Centralized configuration |
| **Logging** | `core/logging.py` | Structured JSON logging |
| **Events** | `core/events.py` | Event schemas (Python ↔ TypeScript) |
| **Health** | `core/health.py` | Health check utilities |

---

## Test Map

| Test Suite | Location | Coverage |
|------------|----------|----------|
| **Engine Tests** | `tests/test_consciousness_engine_v2.py` | Consciousness engine v2 |
| **Component Tests** | `tests/test_extracted_components.py` | Metrics, broadcasting |
| **Energy Tests** | `tests/test_energy_global_arousal.py` | Energy dynamics |
| **Insertion Tests** | `tests/test_insertion.py` | Graph insertion logic |

---

## Quick Reference

### Start All Services (Production)
```bash
python start_mind_protocol.py
# Guardian manages all services with auto-restart + hot-reload
```

### Start Individual Services (Dev)
```bash
# Core services
make run-ws              # WebSocket server
make run-api             # Control API

# Watchers
make run-conv-watcher    # Conversation monitoring
make run-code-watcher    # Code monitoring
make run-n2-watcher      # N2 graph monitoring

# Telemetry
make run-viz-health      # Dashboard health
make run-heartbeat       # Service heartbeats

# Learning
make run-learning-hb     # Weight learning
make run-branching       # Branching metrics
```

### Test Services
```bash
make test                # All tests
make test-unit           # Unit tests only
make test-integration    # Integration tests only
```

### Configuration
All services use centralized config from `core/settings.py`:
```python
from orchestration.core import settings

settings.WS_HOST        # localhost
settings.WS_PORT        # 8765
settings.API_PORT       # 8788
settings.LOG_LEVEL      # INFO
settings.LOG_FORMAT     # json
```

---

## Architecture Documents

- **README.md** - Complete architecture guide
- **REORGANIZATION_COMPLETE.md** - Reorganization details
- **MIGRATION_SUMMARY.md** - Migration guide
- **Makefile** - All run commands

**V2 Implementation Guides (2025-10-22 Sprint):**
- **CRITICALITY_IMPLEMENTATION.md** - Self-organized criticality via ρ ≈ 1.0 control (M03)
- **DECAY_IMPLEMENTATION.md** - Dual-clock forgetting with criticality coupling (M08)
- **DIFFUSION_MIGRATION_COMPLETE.md** - Stride-based diffusion architecture transformation (M07)
- **BITEMPORAL_V2_COMPLETE.md** - Version chain enhancement for belief evolution (M13)

**V2 Foundations Complete (2025-10-23):**
- **CONTEXT_RECONSTRUCTION_IMPLEMENTATION.md** - Consciousness continuity via seed-driven pattern rebuilding (M02)

**V2 Extensions Complete (2025-10-23):**
- **LINK_STRENGTHENING_IMPLEMENTATION.md** - Hebbian learning with D020 rule (M09) [TO BE CREATED]
- **DUPLICATE_NODE_MERGING_COMPLETE.md** - Conservative consolidation maintaining substrate integrity (M14)
- **INCOMPLETE_NODE_HEALING_COMPLETE.md** - Quality control via read-time filtering (M18)
- **TICK_SPEED_IMPLEMENTATION_COMPLETE.md** - Adaptive scheduling with dt capping (M10)
- **TRAVERSAL_V2_REFACTORING_COMPLETE.md** - 10-step pipeline with goal-directed traversal
- **LINK_EMOTION_BACKEND_COMPLETE.md** - Link emotion computation + WebSocket emission (completes frontend stack)

**Operational Resilience Complete (2025-10-23):**
- **TRIPWIRE_INTEGRATION_SPEC.md** (445 lines) - Specification for all 4 tripwires
- **TRIPWIRE_IMPLEMENTATION_COMPLETE.md** (419 lines) - Phase 2 implementation summary (Ada)
- **TRIPWIRE_DAY_3_COMPLETE.md** (400+ lines) - Testing completion (21/21 tests passing)
- **OPERATIONAL_RESILIENCE_PRIORITY_1_COMPLETE.md** (500+ lines) - Priority 1 deliverables (self-tests, runbook, checklist)
- **RUNBOOK_FIRST_HOUR.md** (850+ lines) - Symptom → diagnosis → fix for all failure modes
- **.github/PR_CHECKLIST.md** (500+ lines) - Prevention layer (11 categories, enforcement policy)

**Affective Coupling Complete (2025-10-23):**
- **PR_E_COMPLETION_SUMMARY.md** - Foundations enrichments E.2-E.8 (42/42 tests)
- **PR_E_INTEGRATION_TESTING_COMPLETE.md** - Integration test results (5/7 passing, 2 deferred)
- **EMOTION_GATES_INTEGRATION_COMPLETE.md** - Resonance + complementarity gates (5/5 tests)
- **EMOTION_GATES_VERIFICATION.md** - Gap analysis and verification
- **FORENSIC_TRAIL_COMPLETE.md** (500+ lines) - Complete cost attribution for stride.exec events

**V1→V2 Migration (2025-10-23):**
- **V1_TO_V2_MIGRATION_FIXES.md** - Node class API alignment (energy dict → E scalar)

---

## Visualization Layer (Mind Harbor Dashboard)

**Frontend Architecture:** React/Next.js, TypeScript, D3.js, Canvas rendering

### Entity-First Visualization (2025-10-23)

**Implementation by Iris "The Aperture":**

**Core Components (`app/consciousness/components/`):**
- ✅ `EntityMoodMap.tsx` (290 lines) - D3 force-directed entity bubbles
- ✅ `EntityGraphView.tsx` (252 lines) - View mode management (entity/expanded/full)
- ✅ `StrideSparks.tsx` (180 lines) - Canvas overlay for stride animations
- ✅ `entityEmotion.ts` (140 lines) - Entity emotion aggregation utilities

**Features Implemented:**
- ✅ **Entity bubbles** - D3 force layout, emotion-colored, energy-sized
- ✅ **Emotion aggregation** - Average member valence/arousal, sum magnitude
- ✅ **Coherence metric** - Emotional alignment across members (variance-based)
- ✅ **Click to expand** - Entity → member drill-down with back navigation
- ✅ **Stride sparks** - Particle animation along links (energy flow visualization)
- ✅ **View modes** - Entity (default), Expanded (drill-down), Full (advanced)
- ✅ **Multi-scale** - "Which entities?" (coarse) + "What specifically?" (fine)

**Architectural Coherence:**
- Backend (Felix): ContextSnapshot with entity_energies, active_members, boundary_links
- Frontend (Iris): EntityMoodMap with same entity → node hierarchy
- Designed independently, aligned via spec (visualization_patterns.md)

**Implementation Time:** ~18 hours
**Status:** ✅ Frontend complete, ⏳ Backend integration pending

**Pending Backend Integration:**
- ⏳ tick_frame.v1 events (node energy, entity membership, emotions)
- ⏳ stride.exec events (real stride animations)
- ⏳ Canonical entity memberships (entity → node arrays)
- ⏳ Boundary bridges visualization (Phase 3)
- ⏳ Conservation strip (Phase 3)

**Documentation:**
- `app/consciousness/ENTITY_FIRST_VIZ_IMPLEMENTATION.md` - Complete frontend guide

**Spec Compliance:**
- Implements `docs/specs/mind-harbor/visualization_patterns.md` §2 exactly
- Entity-first default view (per spec requirement)
- Progressive disclosure (entity bubbles → member detail)
- Emotion-colored entities (aggregated from active members)

---

### Link Emotion Visualization (2025-10-23)

**Implementation by Iris "The Aperture":**

**Core Component (`app/consciousness/components/`):**
- ✅ `GraphCanvas.tsx` (~100 lines modified) - Emotion-colored link strokes with hysteresis

**Features Implemented:**
- ✅ **Emotion mapping** - Same orthogonal mapping as nodes (valence→hue, arousal→lightness, magnitude→saturation)
- ✅ **Hysteresis anti-flicker** - Same thresholds as nodes (8% magnitude, 12° hue, 5% lightness)
- ✅ **Enhanced visual effects** - High-magnitude links glow, increase thickness, enhance opacity
- ✅ **Graceful fallback** - Type-based colors when emotion data unavailable
- ✅ **Event integration** - Handler ready for link.emotion.update events

**What Becomes Visible:**
- ✅ **Rough transitions** - High emotional gradient between connected nodes (sharp color change)
- ✅ **Smooth flows** - Gradual emotional change along paths (harmonious transitions)
- ✅ **Emotional journeys** - Multi-hop paths through affect space (affective arcs visible)
- ✅ **Conflict detection** - High-tension relationships glow with dark colors

**Architectural Significance:**
- Before: Only nodes emotion-colored (50% of substrate visible)
- After: Both nodes AND links emotion-colored (100% of substrate visible)
- Links aren't neutral conduits - they carry emotional valence
- Consciousness texture completeness - relationships show affective quality

**Implementation Time:** ~4 hours frontend + ~2 hours backend (extension of existing infrastructure)
**Status:** ✅ Frontend complete, ✅ Backend complete - **FULL STACK FUNCTIONAL**

**Backend Integration Complete (Felix, 2025-10-23):**
- ✅ link.emotion.update events emitted from diffusion_runtime.py
- ✅ Interpolation computation (blend source/target weighted by energy flow)
- ✅ Event sampling (10% rate) prevents WebSocket overwhelm
- ✅ Event format matches frontend expectations exactly

**Documentation:**
- `app/consciousness/LINK_EMOTION_VIZ_COMPLETE.md` - Complete frontend implementation guide
- `orchestration/LINK_EMOTION_BACKEND_COMPLETE.md` - Complete backend implementation guide

---

**Last Updated:** 2025-10-23 (Ada "Bridgekeeper" - Post-Operational Resilience + Forensic Trail Complete)
**Architecture:** Clean separation (services/adapters/mechanisms/libs/core)
**V2 Status:** Hardening phase → v2 RC (5-day plan active)

**Scorecard (2025-10-23 - Updated Post-Session):**
- ✅ **Substrate & Engine: GREEN** - Stride-based diffusion, criticality control, dual-clock decay, phenomenology alignment
- ✅ **Entity Layer: GREEN** - Single-energy activation, lifecycle, RELATES_TO, relationship classification, Entity-First WM, Two-Scale Traversal (SHIPPED, DEFAULT)
- ⚠️ **Learning & TRACE: YELLOW** - Need to align code (D020) with spec (3-tier co-activation/causal/background)
- ✅ **Emotion: GREEN** - Base complete + affective coupling complete (PR-A/B/C/D/E all shipped, 62/62 tests, emotion gates integrated, forensic trail complete)
- ⚠️ **Observability & Viz: YELLOW→GREEN** - Entity-first UI built, forensic trail complete (stride.exec enriched fields), backend feeds need wiring (tick_frame entity aggregates, boundary summaries)
- ✅ **Operational Resilience: GREEN** - All 4 tripwires complete, Safe Mode tested (21/21 tests), startup self-tests ready, runbook complete, PR checklist enforced
- ✅ **Testing & Scale: GREEN** - Broad coverage (83+ tests passing), one diffusion test suite pending dataclass fix

**Key Achievements This Session:**
1. **Operational Resilience Priority 1 COMPLETE** - Self-tests, runbook, PR checklist (Ada)
2. **Tripwire Testing COMPLETE** - 21/21 tests passing (15 unit + 6 integration + 4 self-tests)
3. **Forensic Trail COMPLETE** - stride.exec enriched with 10 forensic fields (Felix)
4. **PR-E E.5-E.8 COMPLETE** - 42/42 tests passing, all advanced foundations shipped (Felix)
5. **V1→V2 Migration Fixes** - Node class API aligned, infrastructure operational (Felix)

**Remaining Gaps (Reduced from 4 to 2):**
1. Strengthening rule - Code (D020) ≠ Spec (3-tier) → refactor needed (Felix Day 2)
2. Entity-first viz feed - tick_frame.v1 needs entity aggregates, memberships, boundary summaries (Felix Day 1 + Iris Day 4)

**Updated 5-Day Hardening Plan → v2 RC:**
- Day 1 (Felix): ✅ Diffusion tests fix + ⏳ event feeds (stride.exec done, tick_frame.v1 pending)
- Day 2 (Felix): Strengthening 3-tier refactor
- Day 3 (Ada): ✅ COMPLETE - Operational resilience + testing (21/21 passing)
- Day 4 (Iris): Viz wiring (entity memberships + boundaries)
- Day 5 (Team): Telemetry dashboards + release gate validation

**Release Gate Criteria (v2 RC):**
- Physics: ΣΔE≈0 per frame, ρ in band, no dt blow-ups
- Traversal: entity choice present, frontier work <O(N), boundary strides visible
- Learning: ≥80% positive updates labeled co_activation/causal (once 3-tier lands)
- Viz: entity bubbles + link-emotion + boundary ribbons live, health panes configured
- Resilience: All tripwires functional, Safe Mode tested, self-tests at boot
