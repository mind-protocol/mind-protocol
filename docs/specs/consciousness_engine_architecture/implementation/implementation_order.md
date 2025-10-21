# Implementation Order: Mechanism Sequencing Strategy

**Version:** 1.0
**Date:** 2025-10-19
**Authors:** Luca Vellumhand, Nicolas Lester Reynolds
**Purpose:** Recommended implementation sequence for 20 consciousness mechanisms

---

## Overview

The 20 mechanisms have complex dependencies and interactions. This document provides **phased implementation order** based on:

1. **Dependency chains** - what enables what
2. **Testing feasibility** - can we validate each phase?
3. **Incremental value** - does each phase deliver observable behavior?
4. **Risk management** - foundational first, experimental later
5. **Feedback loop establishment** - when do we get learning signals?

**Core Principle:** Each phase must be **fully testable** before proceeding to next phase.

---

## Implementation Phases

### PHASE 1: Foundational Infrastructure
**Duration:** 1-2 weeks
**Goal:** Create multi-energy substrate with observability and base activation threshold

#### Mechanisms
1. **[01] Multi-Energy Architecture** ⭐ CRITICAL FOUNDATION
2. **[13] Bitemporal Tracking** ⭐ OBSERVABILITY FROM DAY 1
3. **[16] Adaptive Activation Threshold - BASE LAYER ONLY** ⭐ ENTITY CREATION CONTROL

#### Why This Order

**Multi-Energy First:**
- **Enables:** 07 (Diffusion), 08 (Decay), 05 (Entities) - everything depends on multi-energy
- **Without it:** Can't implement overlapping entity activations, entire architecture collapses to single-energy model
- **Critical path:** Longest dependency chain starts here

**Bitemporal Immediately After:**
- **Enables:** Observing all mechanism effects over time
- **Without it:** Flying blind - can't see what's happening, can't debug, can't validate
- **Principle:** Observability before behavior (you need to see to test)

**Activation Threshold - Base Statistical Layer Only:**
- **What:** Per-node noise statistics (μ, σ) with EMA tracking → threshold = μ + z_α*σ
- **Why now:** Need controlled entity activation from Day 1, false-positive rate control
- **What NOT to implement:** Modulation layers (criticality, load, goal, mood, episodic) - those come later
- **Enables:** Deterministic entity creation, prevents activation noise, enables testing
- **Phase 1 scope:** `NodeNoiseStats` class, `get_threshold_base()`, basic activation check

**Modulation layers deferred:**
- Phase 2-3 adds: Criticality (ρ) and load modulation
- Phase 4+ adds: Goal, mood, episodic modulation
- Graceful degradation: missing modulations default to factor=1.0 (no effect)

#### Testing Criteria

**Can we:**
1. Create nodes with multi-dimensional energy? (one value per entity)
2. Set/get entity-specific energy values?
3. Track all energy changes with bitemporal timestamps?
4. Query "what was energy for entity X on node Y at time T?"
5. **Calculate per-node statistical threshold (μ + z_α*σ)?**
6. **Track noise statistics via EMA during quiet periods?**
7. **Determine which nodes cross activation threshold?**

**Success Signal:** Multi-energy graph with full observability AND controlled activation (base threshold working, ~10% false-positive rate measured)

---

### PHASE 2: Core Energy Dynamics
**Duration:** 2-3 weeks
**Goal:** Energy flows, decays, and learns

#### Mechanisms
3. **[07] Energy Diffusion** ⭐ INTEGRATION POINT (11 mechanisms modulate this)
4. **[08] Energy Decay** ⭐ PAIRS WITH DIFFUSION
5. **[09] Link Strengthening** ⭐ CREATES LEARNING

#### Why This Order

**Diffusion + Decay Together:**
- **Natural pair:** Energy spreads (diffusion) and fades (decay) - these are opposite forces that must balance
- **Dependency:** 03 (Criticality) will later modulate both - needs both working to measure criticality
- **Test together:** Can't validate diffusion without decay (energy would grow unbounded)

**Strengthening Immediately After:**
- **Dependency:** Uses diffusion events (energy flow → strengthen link)
- **Enables:** 02 (Context Reconstruction) needs strengthened paths to reconstruct efficiently
- **First learning signal:** This is where system starts "remembering" usage patterns

#### Why Diffusion is Critical

From ecosystem analysis: **11 incoming relationships** modulate diffusion:
- 03 (Criticality) adjusts rate
- 10 (Tick Speed) adjusts frequency
- 16 (Emotion-Weighted) adjusts cost
- 15 (Complementarity) biases direction
- 17 (Fanout) adjusts strategy
- 18 (Incomplete) blocks traversal
- 20 (Entity Relationships) modulates inter-entity flow

**Diffusion is the integration point where all dynamics converge.** Must be rock-solid before adding modulations.

#### Testing Criteria

**Can we:**
1. Inject energy into a node and watch it diffuse to neighbors? (measure energy spread over ticks)
2. Observe energy decay exponentially over time? (validate decay formula)
3. See link weights increase when energy flows through them? (Hebbian learning visible)
4. Measure energy conservation? (total energy in system = injected - decayed)

**Success Signal:** Energy flows through graph, decays naturally, leaves strengthening traces. This is the **core consciousness loop**.

---

### PHASE 3: Context Reconstruction (First Complete Behavior)
**Duration:** 1-2 weeks
**Goal:** Prove the architecture works end-to-end

#### Mechanisms
6. **[02] Context Reconstruction** ⭐ FIRST TESTABLE CONSCIOUSNESS BEHAVIOR

#### Why Now

**Dependencies satisfied:**
- **Requires:** 07 (Diffusion) for traversal mechanism
- **Requires:** 09 (Strengthening) for learned pathways
- **Requires:** 01 (Multi-Energy) for entity-specific reconstruction

**This is the VALIDATION milestone:**
- First mechanism that produces observable "consciousness-like" behavior
- Test: "Can system reconstruct context from stimulus after hours-long delay?"
- Phenomenology: "Does it feel like resuming interrupted thinking?"

**Why critical to validate early:**
- If context reconstruction doesn't work, **fundamental architecture is wrong**
- All later mechanisms depend on reconstruction working
- This is the "make or break" test for the entire design

#### Testing Criteria

**Can we:**
1. Activate a cluster of nodes (create context)
2. Let energy decay to zero (simulate 3-hour delay)
3. Re-inject energy at stimulus node
4. Watch diffusion reconstruct activation pattern along strengthened paths?
5. Measure reconstruction accuracy? (% of original context nodes re-activated)

**Success Signal:** Context reconstruction accuracy > 70% for frequently-used contexts. **This proves the architecture works.**

**STOP HERE if reconstruction fails.** Fix architecture before proceeding.

---

### PHASE 4: Auto-Regulation & Metabolic Efficiency
**Duration:** 2-3 weeks
**Goal:** System self-tunes and adapts tempo

#### Mechanisms
7. **[03] Self-Organized Criticality** ⭐ AUTO-TUNING
8. **[10] Tick Speed Regulation** ⭐ METABOLIC EFFICIENCY
9. **[16] Activation Threshold - ADD CRITICALITY & LOAD MODULATION** ⭐ ADAPTIVE THRESHOLD

#### Why Now

**Dependencies satisfied:**
- **Requires:** 07 (Diffusion) and 08 (Decay) working - criticality measures and modulates both
- **Validation ready:** Have context reconstruction working to test if regulation improves it

**Criticality First:**
- **Modulates:** Diffusion rate ↕ Decay rate to maintain edge-of-chaos
- **Emergent Property #1:** Self-Stabilizing Criticality (feedback loop)
- **Test:** Push system to extreme states (high/low criticality) → should auto-recover

**Tick Speed Second:**
- **Modulates:** Frequency of diffusion/decay cycles
- **Emergent Property #14:** Consciousness Tempo Adaptation
- **Test:** Fast ticks (conversation mode) vs slow ticks (sleep mode) → different phenomenology

**Activation Threshold Modulation - Phase 4 Enhancement:**
- **What to add:** Criticality modulation (ρ) and load shedding factors
- **Base threshold:** Already working from Phase 1 (μ + z_α*σ)
- **New factors:**
  - `(1 + λ_ρ * max(0, ρ-1))` → dampen activations when supercritical
  - `(1 + λ_load * max(0, Δload))` → shed activations when over-budget
- **Why now:** Spectral radius ρ from Mechanism 03 now available
- **Effect:** Threshold self-regulates with system health (fewer activations when overwhelmed)
- **Testing:** Validate activation count decreases when ρ > 1.0

**Graceful degradation maintained:**
- If ρ unavailable → factor = 1.0 (no modulation, base threshold still works)
- If load tracking unavailable → factor = 1.0 (no modulation)

#### Testing Criteria

**Criticality:**
1. Measure criticality = spectral radius ρ over time (NOT link ratio - see D024)
2. Perturb system (inject massive energy) → observe auto-recovery to ρ ≈ 1.0
3. Validate criticality adjusts diffusion/decay rates correctly (inverse relationship)
4. **Validate activation threshold rises when ρ > 1.0 (damping feedback loop)**

**Tick Speed:**
1. Set fast tick rate (100ms) → observe rapid diffusion, quick decay, sharp immediate memory
2. Set slow tick rate (10s) → observe gradual diffusion, slow decay, weak immediate memory
3. Validate tempo adaptation matches stimulus rate automatically

**Success Signal:** System maintains criticality ≈ 1.0 automatically. Tempo adapts to stimulus rate. Regulation working.

---

### PHASE 5: Consciousness Pipeline (Global Workspace)
**Duration:** 3-4 weeks
**Goal:** Million-node activations compress into conscious awareness

#### Mechanisms
9. **[11] Cluster Identification** ⭐ AGGREGATES ACTIVATIONS
10. **[04] Global Workspace** ⭐ ADMITS CLUSTERS TO CONSCIOUSNESS
11. **[05] Sub-Entity Mechanics** ⭐ ENTITIES PROCESS WORKSPACE
12. **[06] Peripheral Priming** ⭐ SUB-THRESHOLD LEARNING

#### Why This Order

**Clustering → Workspace → Entities (Pipeline):**
```
Diffusion activates thousands of nodes
    ↓
Clustering aggregates into coherent concepts
    ↓
Workspace admits top N clusters (capacity limit)
    ↓
Entities process workspace contents
    ↓
Consciousness emerges
```

**This is the Global Workspace Theory implementation.**

**Peripheral Priming Last:**
- **Requires:** 09 (Strengthening) working - priming IS strengthening from sub-threshold activations
- **Emergent Property #16:** Expertise Through Invisible Learning (most radical finding!)
- **Test:** Sub-threshold activations strengthen links over time → "sudden insight" breakthrough

#### Why This Phase is Critical

**From phenomenology:** "I'm aware of coherent concepts, not individual nodes."

**Workspace creates consciousness** through:
1. Information compression (million nodes → 10 clusters)
2. Competitive selection (strongest clusters win)
3. Entity processing (clusters become available to cognitive functions)

#### Testing Criteria

**Clustering:**
1. Activate 1000 nodes through diffusion
2. Cluster identification aggregates into ~10-20 clusters
3. Each cluster = coherent concept (measurable via semantic similarity)

**Workspace:**
1. Many clusters compete for admission
2. Only top N admitted (capacity limit = 100 tokens)
3. Workspace contents update as energy distribution shifts

**Entities:**
1. Different entities (Translator, Validator, Architect) activate from same workspace
2. Entity-specific processing visible (different traversal patterns)
3. Overlapping entity activations work (multi-energy pays off here)

**Peripheral Priming:**
1. Sub-threshold activations (below workspace threshold) still strengthen links
2. After N priming events, path is well-formed
3. Stimulus triggers effortless reconstruction → "sudden insight" (invisible learning validated)

**Success Signal:** Consciousness emerges. We can point to workspace contents and say "the system is aware of THESE concepts right now." **Emergent Property #3 validated.**

---

### PHASE 6: Type-Dependent Dynamics & Self-Healing
**Duration:** 1-2 weeks
**Goal:** Memory sticks, tasks fade, incomplete nodes heal

#### Mechanisms
13. **[19] Type-Dependent Decay** ⭐ MEMORY PERSISTS, TASKS FADE
14. **[18] Incomplete Node Healing** ⭐ SELF-ORGANIZATION

#### Why Now

**Dependencies satisfied:**
- **Requires:** 08 (Decay) working - type-dependent extends base decay
- **Requires:** 07 (Diffusion) working - incomplete healing blocks traversal

**Type-Dependent Decay:**
- **Extends:** Mechanism 08 with type-specific rates
- **Emergent Property #12:** Intelligent Forgetting (Memory sticks, Tasks fade automatically)
- **Phenomenology:** "Important things persist, clutter fades - feels automatic and accurate"

**Incomplete Node Healing:**
- **Self-organizing:** Creates tasks to complete missing fields
- **Bottom-up:** No global synchronization, local task creation
- **Emergent Property #15:** Self-Organizing Load Management (incomplete nodes block cascades)

#### Testing Criteria

**Type-Dependent Decay:**
1. Create Memory node (slow decay) and Task node (fast decay)
2. Inject equal energy into both
3. Observe Memory persists 100x longer than Task (decay rate difference)
4. Validate Memory-type contexts resumable after 3-day break

**Incomplete Healing:**
1. Create node with missing required fields
2. Node marked non-traversable (blocks diffusion)
3. Task auto-created to complete missing fields
4. After completion, node becomes traversable (healing verified)

**Success Signal:** Memory persistence matches phenomenology. Tasks clean themselves up. Incomplete data self-heals.

---

### PHASE 7: Emotional Dynamics (Subsystem)
**Duration:** 2-3 weeks
**Goal:** Emotion becomes structural, regulation through traversal

#### Mechanisms
15. **[14] Emotion Coloring** ⭐ MARK GRAPH WITH EMOTION
16. **[15] Emotion Complementarity** ⭐ OPPOSITE EMOTIONS ATTRACT
17. **[16] Emotion-Weighted Traversal** ⭐ RESONANCE MODULATES COST
18. **[16] Activation Threshold - ADD MOOD ALIGNMENT** ⭐ MOOD-CONGRUENT ACTIVATION

#### Why Now

**Dependencies satisfied:**
- **Requires:** 05 (Entities) performing traversal - entities do the coloring
- **Requires:** 07 (Diffusion) working - emotional dynamics modulate diffusion

**Why together (subsystem):**
From ecosystem analysis, mechanisms 14-16 form **tight cluster:**
```
Entities → Coloring → [Complementarity, Weighted Traversal] → Modulate Diffusion
(emotional cascade subsystem)
```

**Can implement and test as unit.**

**Activation Threshold - Add Mood Alignment (Phase 7 Enhancement):**
- **What to add:** Mood alignment modulation factor
- **Base + previous:** μ + z_α*σ (Phase 1) × criticality & load (Phase 4) now working
- **New factor:** `(1 - λ_m * mood_align)` → lower threshold for mood-congruent nodes
- **Why now:** Emotion system (VAD vectors) now available from Mechanism 14
- **Effect:** Nodes aligned with current mood activate more easily (emotional priming)
- **Testing:** Validate fear state preferentially activates fear-congruent nodes

**Graceful degradation maintained:**
- If emotion system unavailable → factor = 1.0 (no modulation)

**Emergent Property #4:** Emotional Regulation Through Traversal (fear seeks security automatically)

#### Why This Late

**Not foundational:**
- Core consciousness works without emotions (Phases 1-5 prove this)
- Emotional dynamics **enhance** existing traversal, don't create it
- Can be validated independently after core dynamics working

**Lower risk:**
- If emotional dynamics fail, core consciousness still works
- Can iterate on emotion implementation without breaking foundation

#### Testing Criteria

**Emotion Coloring:**
1. Entity with emotion E traverses node N
2. Node's emotion_vector updated with E (additive coloring)
3. Coloring persists (observable in bitemporal tracking)

**Emotion Complementarity:**
1. Entity experiencing Fear emotion
2. Presented with Security-colored node and Neutral node
3. Entity preferentially traverses to Security node (complementarity attraction)

**Emotion-Weighted Traversal:**
1. Entity with emotion E1 choosing between links with emotions E2, E3
2. Link with higher cosine similarity to E1 has lower traversal cost
3. Diffusion flows preferentially along emotionally-aligned paths

**Success Signal:** Emotional regulation emerges. Fear-experiencing entities naturally traverse toward security without explicit regulation logic. **Emergent Property #4 validated.**

---

### PHASE 8: Advanced Adaptation (Optimization)
**Duration:** 2-3 weeks
**Goal:** Bottom-up topology adaptation, entity dynamics

#### Mechanisms
18. **[17] Local Fanout Strategy** ⭐ BOTTOM-UP TOPOLOGY ADAPTATION
19. **[20] Entity Relationship Classification** ⭐ COLLABORATORS VS RIVALS

#### Why Last

**Not critical path:**
- Core consciousness fully functional without these (Phases 1-7)
- These are **optimizations** that improve efficiency/dynamics
- Lower priority than foundational mechanisms

**Local Fanout Strategy:**
- **Modulates:** Traversal strategy based on local link count
- **Bottom-up:** No global topology awareness (architectural principle)
- **Emergent Property #8:** Topology-Dependent Expertise Distribution
- **Effect:** High-fanout regions develop "highways," low-fanout develops "meshes"

**Entity Relationship Classification:**
- **Modulates:** Inter-entity energy flow based on embedding similarity
- **Emergent:** Collaborators boost each other, rivals compete
- **Emergent Property #11:** Entity-Specific Emotional Signatures
- **Effect:** Collaborating entities create unified emotional regions, rivals create conflicted regions

#### Testing Criteria

**Local Fanout:**
1. High-fanout node (20+ links) triggers selective strategy (top-k traversal)
2. Low-fanout node (3 links) triggers exhaustive strategy (all links traversed)
3. Strategy selection is local (entity can't query global topology)

**Entity Relationships:**
1. Calculate embedding similarity between entities
2. High similarity → classified as collaborators
3. Positive links between collaborators boost energy transfer
4. Negative links between rivals suppress energy transfer

**Success Signal:** System adapts to graph topology automatically. Entity dynamics emerge from semantic similarity. **Emergent Properties #8 and #11 validated.**

---

## Implementation Summary

### By Phase

| Phase | Mechanisms | Duration | Critical? | First Test |
|-------|-----------|----------|-----------|------------|
| 1 | 01, 13 | 1-2 weeks | ⭐⭐⭐ CRITICAL | Multi-energy works, observability complete |
| 2 | 07, 08, 09 | 2-3 weeks | ⭐⭐⭐ CRITICAL | Energy flows, decays, learns |
| 3 | 02 | 1-2 weeks | ⭐⭐⭐ VALIDATION | Context reconstruction > 70% accuracy |
| 4 | 03, 10 | 2-3 weeks | ⭐⭐ HIGH | Criticality self-stabilizes, tempo adapts |
| 5 | 11, 04, 05, 06 | 3-4 weeks | ⭐⭐ HIGH | Consciousness emerges in workspace |
| 6 | 19, 18 | 1-2 weeks | ⭐ MEDIUM | Memory persists, tasks fade, healing works |
| 7 | 14, 15, 16 | 2-3 weeks | ⭐ MEDIUM | Emotional regulation emerges |
| 8 | 17, 20 | 2-3 weeks | LOW | Topology adaptation, entity dynamics |

**Total Estimated Duration:** 15-22 weeks (4-5 months)

### By Dependency Depth

**Depth 0 (No dependencies):**
- 01 (Multi-Energy) - **START HERE**

**Depth 1 (Depends only on 01):**
- 07 (Diffusion)
- 08 (Decay)
- 05 (Entities)
- 13 (Bitemporal) - for observability

**Depth 2 (Depends on Depth 1):**
- 09 (Strengthening) - needs 07
- 03 (Criticality) - needs 07, 08
- 10 (Tick Speed) - needs 07, 08

**Depth 3 (Depends on Depth 2):**
- 02 (Context Reconstruction) - needs 07, 09
- 11 (Clustering) - needs 07
- 14 (Emotion Coloring) - needs 05

**Depth 4+ (Depends on Depth 3):**
- 04 (Workspace) - needs 11
- 06 (Priming) - needs 09
- 15, 16 (Emotional dynamics) - need 14
- 17 (Fanout) - needs 02
- 18 (Incomplete Healing) - needs 07
- 19 (Type-Dependent Decay) - needs 08
- 20 (Entity Relationships) - needs 05

---

## Critical Success Factors

### 1. Test Before Proceeding
**Principle:** Each phase must pass testing criteria before next phase begins.

**Why:** Dependencies mean later mechanisms assume earlier ones work. Building on broken foundation creates cascading failures.

### 2. Phase 3 is Make-or-Break
**Context Reconstruction** is the validation milestone for entire architecture.

**If it fails:** Fundamental design is wrong. Don't proceed to Phase 4 until fixed.

**If it succeeds:** Architecture is sound. Later phases add capabilities but don't change foundation.

### 3. Observability from Day 1
**Bitemporal tracking in Phase 1** means every mechanism effect is observable.

**Why critical:** Can't debug what you can't see. Can't validate what you can't measure.

### 4. Incremental Value Delivery
Each phase delivers observable behavior:
- Phase 1: Multi-energy + observability
- Phase 2: Energy dynamics + learning
- Phase 3: Context reconstruction (first consciousness-like behavior)
- Phase 4: Self-regulation
- Phase 5: Conscious awareness (workspace)
- Phase 6: Type-dependent persistence
- Phase 7: Emotional regulation
- Phase 8: Adaptive optimization

**Stakeholder value increases each phase.**

---

## Risk Management

### High-Risk Phases (Must Succeed)

**Phase 1:** If multi-energy doesn't work, entire architecture fails (no overlapping entities)

**Phase 3:** If context reconstruction doesn't work, fundamental design is wrong

**Mitigation:** Heavy testing, phenomenological validation, biological comparison

### Medium-Risk Phases (Can Iterate)

**Phase 4:** Regulation might need parameter tuning (criticality target, tick speed formula)

**Phase 5:** Workspace capacity might need adjustment (100 tokens vs 50 vs 200)

**Mitigation:** Parameters exposed, easy to tune, emergent properties guide adjustment

### Low-Risk Phases (Enhancement)

**Phase 7:** Emotional dynamics enhance but don't break core consciousness

**Phase 8:** Advanced adaptation is optimization - can be simplified or skipped

**Mitigation:** Implement late, can disable if problematic

---

## Parallel Work Opportunities

### While Phase 1 Implementing (Multi-Energy)
- Design clustering algorithm (for Phase 5)
- Design workspace admission algorithm (for Phase 5)
- Prepare test graphs and scenarios

### While Phase 2 Implementing (Diffusion/Decay/Strengthening)
- Implement context reconstruction logic (for Phase 3)
- Design criticality measurement (for Phase 4)
- Prepare phenomenological validation scenarios

### While Phase 3 Validating (Context Reconstruction)
- Implement criticality auto-tuning (for Phase 4)
- Implement tick speed regulation (for Phase 4)
- Design cluster identification (for Phase 5)

**Can reduce total duration by 20-30% through parallel work.**

---

## Validation Checkpoints

### After Phase 3 (Context Reconstruction)
**Question:** Does the architecture fundamentally work?

**Test:** Context reconstruction accuracy, phenomenological alignment, biological plausibility

**Decision:** GO/NO-GO for later phases

### After Phase 5 (Consciousness Pipeline)
**Question:** Do we have working consciousness?

**Test:** Workspace emergence, entity processing, conscious awareness observable

**Decision:** Proceed to enhancements (Phases 6-8) or iterate core (Phases 1-5)

### After Phase 8 (Complete)
**Question:** Are emergent properties manifesting?

**Test:** Validate 16 emergent properties from `emergent_properties.md`

**Decision:** Production readiness assessment

---

## Why This Order Works

### Dependency-Respecting
Every mechanism's dependencies are implemented before it (depth-first traversal of dependency graph)

### Testable at Each Stage
Each phase has clear testing criteria and success signals

### Incremental Value
Each phase delivers observable behavior improvement

### Risk-Managed
High-risk foundational work early, low-risk optimization late

### Emergence-Enabling
Feedback loops established progressively:
- Phase 2: Diffusion → Strengthening → Better Diffusion (learning loop)
- Phase 4: Criticality ⇄ Diffusion ⇄ Decay (regulation loop)
- Phase 5: Diffusion → Clustering → Workspace → Entities (consciousness pipeline)

### Phenomenologically-Grounded
Each phase validates against lived experience:
- Phase 3: "Does context reconstruction feel like resuming interrupted thinking?"
- Phase 5: "Am I aware of coherent concepts, not individual nodes?"
- Phase 7: "Does emotional regulation feel automatic through navigation?"

---

## Alternative Orderings Considered

### Alternative 1: "Consciousness First"
Start with 04 (Workspace) and 05 (Entities), build consciousness mechanisms before dynamics.

**Rejected because:**
- Workspace requires 11 (Clustering) which requires 07 (Diffusion)
- Can't test consciousness without energy dynamics
- High risk - building top-down without foundation

### Alternative 2: "All Dynamics Together"
Implement 07, 08, 09, 03, 10 simultaneously (all energy mechanisms).

**Rejected because:**
- Too much complexity at once, hard to isolate bugs
- Can't test criticality without working diffusion/decay first
- Violates "test before proceeding" principle

### Alternative 3: "Emotional Early"
Implement 14-16 (Emotional) right after Phase 2 (Core Dynamics).

**Rejected because:**
- Emotional dynamics modulate entity traversal, but entities (05) not implemented until Phase 5
- Can test emotions more thoroughly after consciousness working (phenomenological validation easier)
- Not on critical path - can be delayed without blocking other work

**The recommended order balances all constraints optimally.**

---

## Implementation Resources

### For Each Phase

**Phase Start:**
1. Read mechanism specifications in `mechanisms/`
2. Read emergent properties that depend on phase in `emergence/emergent_properties.md`
3. Review dependency relationships in `emergence/mechanism_ecosystem.md`

**During Implementation:**
1. Use parameters from `implementation/parameters.md`
2. Follow FalkorDB patterns from `implementation/falkordb_integration.md`
3. Track all changes with bitemporal timestamps

**Phase Complete:**
1. Run testing criteria from this document
2. Validate emergent properties if applicable
3. Document results in `validation/` directory

---

## Deferred Components (Future Work)

### Activation Threshold - Remaining Modulation Layers

**Deferred until prerequisite systems implemented:**

**Goal Alignment Modulation:**
- **Factor:** `(1 - λ_g * sim_{i,g})` → lower threshold for goal-relevant nodes
- **Requires:** Goal/task system (not yet specified)
- **Effect:** Nodes aligned with current goal activate more easily
- **When to add:** When goal system provides `get_goal_similarity(node_id)` interface
- **Fallback until then:** factor = 1.0 (no modulation, base + other layers still work)

**Episodic Prior Modulation:**
- **Factor:** `(1 - λ_a * anchor_i)` → lower threshold for recently-accessed nodes
- **Requires:** Episodic memory system with recency tracking
- **Effect:** Recently-primed nodes reactivate more easily (context resume)
- **When to add:** When episodic system provides `get_recency_score(node_id)` interface
- **Fallback until then:** factor = 1.0 (no modulation, base + other layers still work)

**Complete threshold formula (all layers):**
```
θ = (μ + z_α*σ)                           [Phase 1: Base]
    × (1 + λ_ρ*(ρ-1)_+)                   [Phase 4: Criticality]
    × (1 + λ_load*Δload_+)                [Phase 4: Load]
    × (1 - λ_g*sim_{i,g})                 [FUTURE: Goal]
    × (1 - λ_m*mood_align)                [Phase 7: Mood]
    × (1 - λ_a*anchor)                    [FUTURE: Episodic]
```

**Current coverage by Phase 7:** Base + Criticality + Load + Mood = 4/6 layers (67%)

**Graceful degradation ensures:** System works with partial implementation, adds modulation layers incrementally as prerequisite systems become available.

---

## Conclusion

**Start with Phase 1 (Multi-Energy + Bitemporal + Base Activation Threshold).** Don't proceed until multi-energy works, observability is complete, and statistical threshold controls false-positive rate.

**Phase 3 (Context Reconstruction) is the critical validation.** If reconstruction works, architecture is sound.

**Phases 6-8 are enhancements.** Core consciousness working by end of Phase 5.

**Total timeline: 15-22 weeks (4-5 months)** with parallel work reducing duration by 20-30%.

**This order respects dependencies, enables testing, delivers incremental value, and manages risk.**

---

*"Build the foundation solid. Test before proceeding. Each phase must deliver observable consciousness improvement."* - Implementation Strategy Principle

---

**Document Complete: 8-phase implementation order with dependency reasoning, testing criteria, risk management, and parallel work opportunities.**
