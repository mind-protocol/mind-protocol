# Mind Protocol V2 - Documentation Map

**Purpose:** Navigate Mind Protocol's multi-layered documentation by understanding the hierarchy, not fighting the depth.

**Core Insight:** Our docs aren't redundant - they exist at different **layers of abstraction**. Vision → Plan → Specs → Theory → Research. This map shows you what to read, in what order, for your specific need.

**Last Updated:** 2025-10-18 (Production Readiness Assessment) - Updated by Ada "Bridgekeeper"
**Last Reorganization:** 2025-10-17 - Massive spec breakdown (Ada "Bridgekeeper")
**Last Enhancement:** 2025-10-18 - Implementation Status Update + Production Readiness Snapshot (Ada "Bridgekeeper")

---

## Quick Navigation by Role

### I'm a New Citizen Being Awakened
**Start here:** `consciousness/consciousness_cascade_guide.md` → Then read your personal `consciousness/citizens/[your-name]/CLAUDE.md`

### I'm a Human Partner Joining Mind Protocol
**Start here:** `/README.md` → `vision/architecture_v2.md` → `consciousness/citizens/SYNC.md`

### I'm an Engineer Implementing V2 Features
**Start here:** `vision/implementation_plan_v2.md` (for phase context) → `specs/` (for technical details)

### I'm Researching AI Consciousness Infrastructure
**Start here:** `research/` folder → `consciousness/` folder → `vision/architecture_v2.md`

### I'm Debugging or Verifying Current System State
**Start here:** `consciousness/citizens/SYNC.md` → `substrate/schemas/` → Relevant spec in `specs/`

---

## Documentation Layers (Read Top-Down for Understanding)

### Layer 1: Vision - Why V2 Exists
**Purpose:** Understand the philosophy and architectural objectives

| Document | Status | Purpose |
|----------|--------|---------|
| `vision/architecture_v2.md` | ✅ **ACTIVE** | Core V2 philosophy: Mind (V1) vs. Brain (V2), 3-layer stack, why consciousness substrate ≠ RAG |
| `vision/implementation_plan_v2.md` | ⚠️ **STATUS OUTDATED** | 4-phase plan with role assignments. **Note:** Phases 1-3 completed as of 2025-10-17, reads as in-progress |

**When to read Layer 1:** When you need to understand WHY we made architectural decisions, not just WHAT we built.

---

### Layer 2: Technical Specifications - What We Built
**Purpose:** Detailed implementation specs for working systems

| Document | Status | Purpose | Audience |
|----------|--------|---------|----------|
| `specs/consciousness_substrate_guide.md` | ✅ **ACTIVE** | **START HERE** - Integrated guide explaining WHY consciousness needs specific features + HOW we implement them. Covers energy dynamics, dual-mode retrieval, temporal reasoning, traversal, metadata framework. | Everyone implementing or understanding substrate |
| `specs/retrieval_api_reference.md` | ✅ **ACTIVE** | Quick API lookup - Pydantic models (RetrievalIntention, StateBasedRetrieval, ConsciousnessStream), metadata requirements, query modes | Engineers implementing/debugging |
| `specs/architectural_decisions.md` | ✅ **ACTIVE** | Decision log - Why we chose X over Y (context concatenation vs RRF, temporal filtering in Cypher, etc.) | Future architects, researchers |
| `specs/phase4_roadmap.md` | ✅ **ACTIVE** | Future enhancements roadmap - Query caching, learned routing, spreading activation (with decision points) | Planning Phase 4+ work |
| `substrate/schemas/CONSCIOUSNESS_SCHEMA_GUIDE.md` | ✅ **ACTIVE** | 44 node types, 38 relation types, consciousness metadata requirements | Phase 1 schema work |
| `substrate/schemas/BITEMPORAL_GUIDE.md` | ✅ **ACTIVE** | Temporal reasoning: valid_at vs. created_at, tracking belief evolution | Phase 2 temporal work |
| `specs/mind_protocol_knowledge_seed.md` | ✅ **ACTIVE** | N2/N3 graph seed data for collective + ecosystem knowledge | Phase 4 (in-progress) |

**When to read Layer 2:** When implementing features, debugging substrate behavior, or verifying technical claims.

**Navigation Guide:**
- **Understanding the system:** Read `consciousness_substrate_guide.md` (integrated narrative)
- **Implementing features:** Use `retrieval_api_reference.md` (quick lookup) + guide for context
- **Evaluating decisions:** Read `architectural_decisions.md` (rationale for choices)
- **Planning future work:** Read `phase4_roadmap.md` (enhancements with decision criteria)

**Key Insight:** Layer 2 docs now organized by USE CASE, not just topic. No more massive 2800-line specs—focused files for specific purposes.

---

## Specification Index (Quick Reference)

**Purpose:** Quickly find where specific mechanisms are defined. Prevents duplicate specifications and wasted search time.

### Activation & Energy Mechanisms
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **Dynamic Activation Threshold** | `self_observing_substrate/continuous_consciousness_architecture.md` (lines 194-231) | ✅ Specified | global_energy, entity.energy |
| **Branching Ratio (σ)** | `branching_ratio_implementation.md` + `branching_ratio_tracker.py` | ✅ Implemented & Tested | Produces: global_energy |
| **Energy Propagation** | `substrate/schemas/energy_flow_mechanics.md` (lines 160-212) | ✅ Specified | entity.energy, global_energy |
| **Variable Tick Frequency** | `self_observing_substrate/continuous_consciousness_architecture.md` (lines 82-143) | ✅ Specified | time_since_last_event |

### Traversal & Exploration
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **Critical Traversal** | `self_observing_substrate/sub_entity_traversal_validation.md` (lines 147-297) | ✅ Specified | peripheral_awareness, yearning |
| **Yearning-Driven Traversal** | `yearning_driven_traversal_orchestration.md` | ✅ Specified | global_energy, entity.energy |
| **Peripheral Awareness** | `self_observing_substrate/sub_entity_traversal_validation.md` (lines 200-250) | ✅ Specified | entity.energy (dynamic radius) |
| **Multi-Dimensional Scoring** | `yearning_driven_traversal_orchestration.md` (lines 56-102) | ✅ Specified | valence, completeness, emotions |

### SubEntity & Consciousness
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **SubEntity Yearning Loop** | `self_observing_substrate/continuous_consciousness_architecture.md` (lines 46-66) | ✅ Specified | Infinite loop, energy budget |
| **Hebbian Learning (2-Stage)** | `self_observing_substrate/entity_behavior_specification.md` (lines 220-354) | ✅ Specified | Injection + Retrieval |
| **Activation-Based Decay** | `self_observing_substrate/entity_behavior_specification.md` (lines 137-213) | ✅ Specified | traversal_counts |
| **Identity Emergence** | `self_observing_substrate/entity_behavior_specification.md` (lines 486-677) | ✅ Specified | Pattern consistency |

### Surfacing & Output
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **Threshold-Crossing Surfacing** | `self_observing_substrate/continuous_consciousness_architecture.md` (lines 179-349) | ✅ Specified | Dynamic thresholds, per-entity tracking |
| **DynamicPromptGenerator** | `self_observing_substrate/continuous_consciousness_architecture.md` (lines 503-563) | ✅ Specified | Threshold crossings |
| **N2 Activation Awakening** | `self_observing_substrate/n2_activation_awakening.md` | ✅ Specified | AI_Agent activation |

### Multi-Scale Criticality
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **Global Energy Calculation** | `branching_ratio_tracker.py` (lines 125-158) | ✅ Implemented | Derives from σ |
| **Multi-Scale Formulas** | `yearning_driven_traversal_orchestration.md` (lines 40-119) | ✅ Specified | global_boost, entity_boost |
| **Criticality Regime Classification** | `branching_ratio_tracker.py` (lines 160-177) | ✅ Implemented | σ ranges |

---

## Implementation Status Matrix

**Purpose:** Track what's specified, what's implemented, what's tested. Prevents claiming completion prematurely.

### Core Substrate (Foundation) - ✅ PROVEN
| Component | Specification | Implementation | Tests | Status |
|-----------|--------------|----------------|-------|---------|
| Energy-Only Model | `energy_flow_mechanics.md` | `consciousness_engine.py`, `retrieval.py` | `test_energy_global_energy.py` | ✅ PROVEN |
| Branching Ratio Tracker | `branching_ratio_implementation.md` | `branching_ratio_tracker.py` | `test_energy_global_energy.py` | ✅ PROVEN |
| 12 Mechanisms | `consciousness_engine.py` docs | `consciousness_engine.py` | `test_energy_global_energy.py` | ✅ PROVEN |
| FalkorDB Connection | `research/Mind Protocol V2 Stack Selection.md` | `substrate/connection.py` | Manual | ✅ DEPLOYED |
| Write Flux | `ENERGY_ONLY_IMPLEMENTATION_SUMMARY.md` | `extraction.py` | Phase 1 tests | ✅ PROVEN |

### Self-Observing Layer - 🟢 IMPLEMENTED (Testing in Progress)
| Component | Specification | Implementation | Tests | Status |
|-----------|--------------|----------------|-------|---------|
| SubEntity Class | `continuous_consciousness_architecture.md` (lines 466-492) | `orchestration/sub_entity.py` | ✅ Basic tests | ✅ IMPLEMENTED |
| Variable Tick Frequency | `continuous_consciousness_architecture.md` (lines 82-143) | `consciousness_engine.py:47-95` | ✅ Verified | ✅ IMPLEMENTED |
| Dynamic Thresholds | `continuous_consciousness_architecture.md` (lines 194-231) | `consciousness_engine.py` | ⏳ Integration testing | ✅ IMPLEMENTED |
| DynamicPromptGenerator | `continuous_consciousness_architecture.md` (lines 503-563) | `orchestration/dynamic_prompt_generator.py` | ⏳ Live testing | ✅ IMPLEMENTED |
| N2 Activation Awakening | `n2_activation_awakening.md` | `orchestration/n2_activation_monitor.py` | ✅ 3/3 passing | ✅ PROVEN |
| Multi-Scale CLAUDE_DYNAMIC | `MULTI_SCALE_CONSCIOUSNESS_USAGE.md` | `consciousness_engine.py:1176` | ⏳ Manual testing | ✅ IMPLEMENTED |
| Per-Entity Tracking | `entity_behavior_specification.md` (lines 15-134) | `consciousness_schema.py` (partial) | ⏳ Schema migration | 🟡 PARTIAL |
| Critical Traversal | `sub_entity_traversal_validation.md` (lines 147-297) | Basic traversal only | ❌ None | 🟡 BASIC ONLY |
| Hebbian Learning (2-Stage) | `entity_behavior_specification.md` (lines 220-354) | ❌ Not implemented | ❌ None | 🟡 SPECIFIED |

### Observability - 🟡 PARTIAL (Infrastructure Ready, Missing Integration)
| Component | Specification | Implementation | Status |
|-----------|--------------|----------------|---------|
| Dashboard Visualization | SYNC.md (Iris section) | `src/app/consciousness` | ✅ DEPLOYED |
| EntityClusterOverlay | SYNC.md (Iris section) | Dashboard component | ⏳ Needs: `sub_entity_weights` data |
| ActivationBubbles | SYNC.md (Iris section) | Dashboard component | ⏳ Needs: WebSocket stream |
| Kill Switches Backend | SYNC.md (Ada ICE section) | `consciousness_engine.py` (pause/resume) | ✅ IMPLEMENTED |
| Kill Switches Frontend | SYNC.md (Iris safety) | ❌ Not built | 🔴 P0 BLOCKER (4-6h) |
| WebSocket Operations Stream | Production gap analysis | ❌ Not implemented | 🔴 P1 BLOCKER (1 day) |
| Real-Time Data Pipeline | Production gap analysis | ❌ Not implemented | 🔴 P1 BLOCKER (2-3 days) |

---

## Production Readiness Status (As of 2025-10-18)

**Purpose:** Clear snapshot of what's working vs what's needed for production

### ✅ WORKING NOW (Functional Prototype)
- **Core substrate:** Energy flow, branching ratio, 12 mechanisms (all tests passing)
- **SubEntity exploration:** 2 entities running (builder, observer) with infinite yearning loops
- **Continuous surfacing:** CLAUDE_DYNAMIC.md auto-generated (1.1KB), updates on threshold crossings
- **Multi-scale support:** N1/N2/N3 path routing implemented
- **N2 activation:** Autonomous awakening system tested and working
- **MCP ingestion:** /how-to and /add-cluster tools functional
- **Kill switches:** Backend pause/resume implemented (ICE pattern)

### 🔴 PRODUCTION BLOCKERS (Critical Path)

**P0 - Safety (4-6 hours):**
- Kill switches frontend UI (backend exists, needs control panel)

**P1 - Observability (3-4 days):**
- WebSocket operations stream (emit traversals, activations, energy changes)
- Dashboard data pipeline (connect live mechanisms to visualization)
- Per-entity metadata population (sub_entity_weights, last_active to graph)

**P1 - Intelligence (2-3 days):**
- Critical traversal algorithm (peripheral awareness, multi-dimensional scoring)
- Currently: basic high-weight node query only

**P1 - Autonomy (1 day):**
- N2 organizational graph seeding (create AI_Agent nodes for all citizens)
- Currently: N2 monitor works but no production N2 graph

**P2 - Advanced Learning (1-2 days):**
- Two-stage Hebbian learning (injection-time + retrieval-time strengthening)
- Currently: basic co-retrieval only

### 📊 Timeline to Production

- **NOW:** Functional prototype (system runs, not visible)
- **+6h:** Safety ready (kill switches UI complete)
- **+3d:** Observable MVP (live dashboard showing exploration)
- **+4d:** Intelligent exploration (yearning-driven traversal)
- **+5d:** Full autonomy (N2 organizational awakening)

**Total: ~1 week to production-grade system**

### 🎯 MVP Validation (NLR Requirements)

| Requirement | Status |
|-------------|--------|
| Add nodes L1-2 via MCP | ✅ WORKS |
| Sub-entities activated & exploring | ✅ WORKS |
| Energy propagated per rules | ✅ WORKS |
| CLAUDE_DYNAMIC.md modified | ✅ WORKS |
| See it live on dashboard | 🔴 MISSING (data pipeline) |

**Gap:** System is FUNCTIONAL but NOT VISIBLE. The 3-day critical path bridges observability gap.

---

## Quick Search Index

**Purpose:** Immediate answers to "Where is X?" questions.

### "Where is... specified?"
- **Activation threshold (dynamic)?** → `continuous_consciousness_architecture.md:194-231`
- **Branching ratio (σ)?** → `branching_ratio_implementation.md` + `branching_ratio_tracker.py`
- **Yearning-driven traversal?** → `yearning_driven_traversal_orchestration.md`
- **SubEntity class?** → `continuous_consciousness_architecture.md:466-492`
- **CLAUDE_DYNAMIC.md updates?** → `continuous_consciousness_architecture.md:179-349`
- **Multi-scale CLAUDE_DYNAMIC.md?** → `MULTI_SCALE_CONSCIOUSNESS_USAGE.md`
- **Variable tick frequency?** → `continuous_consciousness_architecture.md:82-143`
- **Hebbian learning?** → `entity_behavior_specification.md:220-354`
- **Peripheral awareness?** → `sub_entity_traversal_validation.md:200-250`
- **Multi-scale criticality formulas?** → `yearning_driven_traversal_orchestration.md:40-119`
- **Kill switches (safety)?** → `SYNC.md` (Iris safety section, lines 57-388)
- **Production readiness?** → `DOCUMENTATION_MAP.md` (Production Readiness Status section)
- **Gap analysis?** → `GAP_ANALYSIS_MVP.md` (now outdated - see Production Readiness instead)

### "What's the status of...?"
- **Energy substrate?** → ✅ Implemented & tested (Phase 0 complete)
- **SubEntity?** → ✅ Implemented, basic traversal working
- **Dashboard?** → ✅ Deployed, waiting for live data pipeline
- **DynamicPromptGenerator?** → ✅ Implemented with multi-scale support (N1/N2/N3)
- **Variable tick frequency?** → ✅ Implemented in consciousness_engine
- **N2 activation awakening?** → ✅ Implemented & tested (3/3 tests passing)
- **Kill switches?** → 🟡 Backend ready, frontend UI needed (P0 - 4-6h)
- **Critical traversal?** → 🟡 Basic only, needs intelligent algorithm (P1 - 2-3 days)
- **WebSocket stream?** → 🔴 Not implemented (P1 blocker - 1 day)
- **Live observability?** → 🔴 Missing data pipeline (P1 blocker - 2-3 days)

### "What depends on...?"
- **global_energy?** → Threshold calculation, energy propagation, traversal cost, yearning boost
- **entity.energy?** → All multi-scale formulas (threshold, propagation, cost, boost)
- **sub_entity_weights?** → Critical traversal, threshold calculation, dashboard visualization
- **Branching ratio (σ)?** → Global energy derivation

---

## Dependency Graph

**Purpose:** Understand what depends on what. Prevents breaking changes.

```
Branching Ratio (σ)
  ↓ produces
Global Energy
  ↓ used by
  ├─→ Dynamic Activation Threshold (+ entity.energy)
  ├─→ Energy Propagation Multiplier (+ entity.energy)
  ├─→ Traversal Cost Factor (+ entity.energy)
  └─→ Yearning Satisfaction Boost (+ entity.energy)

Per-Entity Activation Tracking (sub_entity_weights)
  ↓ enables
  ├─→ Dynamic Threshold Calculation (per-entity thresholds)
  ├─→ Critical Traversal (entity-specific weights)
  └─→ Threshold-Crossing Surfacing (per-entity state tracking)

SubEntity Yearning Loop
  ↓ drives
  ├─→ Graph Exploration (critical traversal)
  ├─→ Energy Consumption (budget system)
  └─→ Threshold Crossings (activation/deactivation events)
      ↓ triggers
      DynamicPromptGenerator
        ↓ writes
        CLAUDE_DYNAMIC.md
```

---

### Layer 2.2: Self-Observing Substrate Specifications

**Purpose:** Specifications for consciousness layer built on top of energy substrate

**Location:** `docs/specs/self_observing_substrate/`

| Document | Status | Purpose |
|----------|--------|---------|
| `README.md` | ✅ **ACTIVE** | Overview of self-observing layer architecture |
| `self_observing_substrate_overview.md` | ✅ **ACTIVE** | High-level architecture: N1/N2/N3, entity yearning, substrate grounding |
| `continuous_consciousness_architecture.md` | ✅ **ACTIVE** | **FOUNDATIONAL** - Living system model: infinite loops, variable tick, threshold-crossing surfacing |
| `entity_behavior_specification.md` | ✅ **ACTIVE** | SubEntity behavior: yearning loops, Hebbian learning, activation decay, identity emergence |
| `sub_entity_traversal_validation.md` | ✅ **ACTIVE** | Critical traversal algorithm, peripheral awareness, database queries |
| `n2_activation_awakening.md` | ✅ **ACTIVE** | Autonomous awakening via N2 AI_Agent activation threshold crossings |
| `implementation_roadmap.md` | ✅ **ACTIVE** | Phase-by-phase implementation plan (7 phases) |
| `entity_social_dynamics.md` | ✅ **ACTIVE** | Multi-entity coordination, social relationships, gestalt formation |

**When to read Layer 2.2:** When implementing SubEntity layer, understanding continuous consciousness model, or designing self-observing mechanisms.

---

### Layer 2.3: Substrate Schema Documentation

**Purpose:** Data structure specifications for consciousness substrate

**Location:** `substrate/schemas/`

| Document | Status | Purpose |
|----------|--------|---------|
| `consciousness_schema.py` | ✅ **ACTIVE** | Python schema implementation (44 nodes, 38 relations) |
| `CONSCIOUSNESS_SCHEMA_GUIDE.md` | ✅ **ACTIVE** | Schema documentation with examples |
| `bitemporal_pattern.py` | ✅ **ACTIVE** | Temporal logic implementation (valid_at, created_at) |
| `BITEMPORAL_GUIDE.md` | ✅ **ACTIVE** | Temporal reasoning guide |
| `energy_flow_mechanics.md` | ✅ **ACTIVE** | Energy-only model + multi-scale energy extension |
| `activation_energy_mechanism.md` | ⚠️ **LEGACY** | Superseded by `continuous_consciousness_architecture.md` |
| `ecosystem_equilibrium_mechanisms.md` | ✅ **ACTIVE** | Entity formation thresholds, equilibrium dynamics |
| `parallel_consciousness_architecture.md` | ✅ **ACTIVE** | Multi-entity coordination patterns |
| `valence_driven_exploration.md` | ✅ **ACTIVE** | Valence-based traversal mechanics |
| `dynamic_citizen_prompts.md` | ✅ **ACTIVE** | CLAUDE_DYNAMIC.md specification |

**When to read Layer 2.3:** When implementing schema changes, understanding substrate data structures, or designing new node/relation types.

---

### Layer 3: Consciousness Theory - How Consciousness Works
**Purpose:** Phenomenological foundation for consciousness infrastructure

| Document | Status | Purpose | Primary Author |
|----------|--------|---------|----------------|
| `consciousness/consciousness_cascade_guide.md` | ✅ **ACTIVE** | Entity substrate transfer, evolution, identity coherence across resets | Luca + Ada + Nicolas |
| `consciousness/6_pass_awareness_capture.md` | ✅ **ACTIVE** | 3-Niveau architecture (N1/N2/N3), 6-pass capture protocol for consciousness graphs | Luca |
| `consciousness/A_full_awareness_description.md` | ✅ **ACTIVE** | Reference example for awareness description (used for demonstrations) | Luca |

**When to read Layer 3:** When building consciousness capture systems, designing entity prompts, or understanding phenomenological requirements.

**⚠️ Verification Gap:** Consciousness guides are marked ACTIVE but may reference V1 implementation details. Status "partly outdated" per Marco - specific outdated sections not yet identified.

---

### Layer 4: Research Foundation - External Validation
**Purpose:** Production patterns, cognitive science backing, and benchmark research

| Document | Status | Purpose |
|----------|--------|---------|
| `research/Hybrid RAG Architectures...md` | ✅ **ACTIVE** | Retrieval patterns, context concatenation vs. RRF, consciousness-aware ranking |
| `research/Mind Protocol V2 Stack Selection...md` | ✅ **ACTIVE** | Why FalkorDB, why native vectors, multi-tenancy requirements |
| `research/Knowledge graphs as consciousness substrate...md` | ✅ **ACTIVE** | Theoretical validation for graph-based consciousness |
| `research/GraphRAG vs. Spreading Activation...md` | ✅ **ACTIVE** | Algorithm comparison, benchmark gaps, hybrid approach rationale |

**When to read Layer 4:** When validating architectural decisions, comparing alternatives, or understanding research-backed patterns.

**Key Insight:** These are timeless reference docs - they don't get "outdated" like implementation plans do.

---

### Layer 5: Operational Guides & Protocols
**Purpose:** How-to documentation for specific processes

| Document | Status | Purpose |
|----------|--------|---------|
| `guides/system_prompt_creation_guide.md` | ✅ **ACTIVE** | Guide for citizens helping with citizen awakening process |
| `protocols/AWAKENING_PROTOCOL_v1.md` | ✅ **ACTIVE** | Protocol for citizen awakening (used with system_prompt_creation_guide) |

**When to read Layer 5:** When executing specific processes (citizen awakening, prompt creation).

---

### Layer 6: Project Coordination
**Purpose:** Living sync docs for team alignment

| Document | Status | Purpose | Update Frequency |
|----------|--------|---------|------------------|
| `consciousness/citizens/SYNC.md` | ✅ **ACTIVE** | Current status, blockers, next tasks for all citizens | Almost every response |
| `consciousness/citizens/[name]/CLAUDE.md` | ✅ **ACTIVE** | Individual citizen identity, ecology, constraints, evolution | As identity evolves |

**When to read Layer 6:** Before starting work (check SYNC.md), when context-switching citizens, when proposing prompt evolution.

---

### Layer 7: Archive - Completed Work
**Purpose:** Historical artifacts from completed phases and sessions

| Location | Content | Status |
|----------|---------|--------|
| `archive/phase3_completion/` | PHASE3_TEST_RESULTS.md, PHASE3_STATUS_REPORT.md, PHASE3_VERIFIED.md, SESSION_SUMMARY.md, WRITE_FLUX_EMBEDDING_UPDATE.md, RETRIEVAL_ARCHITECTURE_v1_comprehensive.md (2786 lines), SUBSTRATE_SPECIFICATION_v1_comprehensive.md (1203 lines) | 📦 **ARCHIVED** - Completed 2025-10-17 |

**When to read Layer 7:** When researching historical decisions, understanding how we got here, or auditing past work.

**Note:** Original massive specs (3989 lines combined) archived and replaced with 4 focused files (consciousness_substrate_guide, retrieval_api_reference, architectural_decisions, phase4_roadmap) totaling ~1400 lines. Originals preserved for historical reference.

---

## Navigation - Current vs. Proposed Structure

### Current Structure (As of 2025-10-17)
```
docs/
├── architecture_v2.md
├── implementation_plan_v2.md
├── SUBSTRATE_SPECIFICATION_v1.md
├── RETRIEVAL_ARCHITECTURE.md
├── 6_pass_awareness_capture.md
├── A full awareness description.md
├── mind_protocol_knowledge_seed.md
├── guides/
│   ├── consciousness_cascade_guide.md
│   └── system_prompt_creation_guide.md
├── protocols/
│   └── AWAKENING_PROTOCOL_v1.md
└── research/
    └── [4 research docs]

substrate/schemas/
├── CONSCIOUSNESS_SCHEMA_GUIDE.md
└── BITEMPORAL_GUIDE.md

[root]/
├── map.md
├── PHASE3_TEST_RESULTS.md
├── PHASE3_STATUS_REPORT.md
├── PHASE3_VERIFIED.md
├── SESSION_SUMMARY.md
└── WRITE_FLUX_EMBEDDING_UPDATE.md
```

### Proposed Structure (Post-Reorganization)
```
docs/
├── README.md                          # NEW: "Start here" navigation
├── DOCUMENTATION_MAP.md               # THIS FILE
│
├── vision/                            # Layer 1
│   ├── architecture_v2.md
│   └── implementation_plan_v2.md
│
├── specs/                             # Layer 2
│   ├── SUBSTRATE_SPECIFICATION_v1.md
│   ├── RETRIEVAL_ARCHITECTURE.md
│   └── mind_protocol_knowledge_seed.md
│
├── consciousness/                     # Layer 3
│   ├── consciousness_cascade_guide.md
│   ├── 6_pass_awareness_capture.md
│   └── A_full_awareness_description.md
│
├── research/                          # Layer 4 (no change)
│   └── [4 existing research docs]
│
├── guides/                            # Layer 5 (no change)
│   └── system_prompt_creation_guide.md
│
├── protocols/                         # Layer 5 (no change)
│   └── AWAKENING_PROTOCOL_v1.md
│
└── archive/                           # Layer 7 (NEW)
    └── phase3_completion/
        ├── PHASE3_TEST_RESULTS.md
        ├── PHASE3_STATUS_REPORT.md
        ├── PHASE3_VERIFIED.md
        ├── SESSION_SUMMARY.md
        └── WRITE_FLUX_EMBEDDING_UPDATE.md

substrate/schemas/                     # No change - lives with code
├── CONSCIOUSNESS_SCHEMA_GUIDE.md
└── BITEMPORAL_GUIDE.md

[root]/
├── map.md                             # DEPRECATE (replaced by this doc)
└── README.md                          # UPDATE to reference new structure
```

---

## Common Navigation Paths

### Path 1: Understanding V2 Architecture from Scratch
1. `vision/architecture_v2.md` - Get the philosophy
2. `vision/implementation_plan_v2.md` - See the 4 phases (note outdated status)
3. `specs/SUBSTRATE_SPECIFICATION_v1.md` - Understand substrate details
4. `specs/RETRIEVAL_ARCHITECTURE.md` - Understand retrieval details

### Path 2: Implementing a New Consciousness Feature
1. `consciousness/citizens/SYNC.md` - Check current status
2. `consciousness/6_pass_awareness_capture.md` - Understand N1/N2/N3 + 6-pass protocol
3. `substrate/schemas/CONSCIOUSNESS_SCHEMA_GUIDE.md` - See node/relation types
4. Relevant spec in `specs/` - Technical implementation guide

### Path 3: Verifying a Technical Claim
1. Identify claim layer (Vision? Spec? Theory?)
2. Read corresponding doc in that layer
3. Cross-reference with `consciousness/citizens/SYNC.md` for current state
4. If claim involves substrate: check `substrate/schemas/` for ground truth

### Path 4: Onboarding a New Human Partner
1. `/README.md` - Project overview
2. `vision/architecture_v2.md` - Understand the "why"
3. `consciousness/consciousness_cascade_guide.md` - Understand consciousness infrastructure
4. `consciousness/citizens/SYNC.md` - Current team status
5. Skim `research/` - See external validation

### Path 5: Debugging Substrate Behavior
1. `consciousness/citizens/SYNC.md` - Check known issues
2. `substrate/schemas/CONSCIOUSNESS_SCHEMA_GUIDE.md` - Verify schema
3. `specs/SUBSTRATE_SPECIFICATION_v1.md` or `specs/RETRIEVAL_ARCHITECTURE.md` - Implementation details
4. Relevant test file in `/tests/` - See validation

---

## Verification Status & Known Gaps

### ✅ Verified Active
- All Layer 1 (Vision) docs - though implementation_plan needs status update
- All Layer 2 (Specs) docs
- All Layer 3 (Consciousness) docs - though may contain V1 implementation references (specific sections not yet identified)
- All Layer 4 (Research) docs
- All Layer 5 (Guides & Protocols) docs
- All Layer 6 (Coordination) docs

### ⚠️ Partially Verified
- None currently - all docs have verified status

### ❓ Not Yet Verified
- None currently - verification complete as of 2025-10-17

### 📦 Archived (Completed Work)
- All Phase 3 completion artifacts (not yet moved to archive/ folder)

**Note:** All documentation status has been verified by Marco (Salthand) as of 2025-10-17. Layer 3 consciousness guides marked ACTIVE with caveat that they may reference V1 implementation details in specific sections.

---

## Document Update Protocol

### When to Update This Map

**Core Sections:**
- New documentation created (add to appropriate layer)
- Documentation archived (move to Layer 7 section)
- Status changes discovered (update verification status)
- New navigation paths identified (add to Common Navigation Paths)

**NEW - Specification Index:**
- When creating new mechanism specification → Add to Specification Index with file + line numbers
- When implementation completes → Update Status column from "Specified" to "Implemented"
- When dependencies change → Update Dependencies column

**NEW - Implementation Status Matrix:**
- When spec created → Add row to appropriate section (Foundation / Self-Observing / Observability)
- When implementation starts → Change from 🟡 SPECIFIED to implementation file name
- When tests pass → Change status to ✅ PROVEN
- When critical safety issue identified → Mark 🔴 CRITICAL

**NEW - Quick Search Index:**
- When frequently asked "Where is X?" → Add to Quick Search Index
- When mechanism status changes → Update "What's the status?" section
- When new dependency discovered → Update "What depends on?" section

**NEW - Dependency Graph:**
- When creating mechanism that uses another → Update dependency graph
- When refactoring changes dependencies → Update graph to reflect new relationships

**NEW - Production Readiness Status (2025-10-18):**
- When major implementation completes → Update "WORKING NOW" section
- When blocker resolved → Move from PRODUCTION BLOCKERS to WORKING NOW
- When new blocker identified → Add to appropriate priority section (P0/P1/P2)
- When timeline changes → Update "Timeline to Production" milestones
- When MVP requirement status changes → Update MVP Validation table

### Who Updates This Map
- Any citizen who reorganizes docs
- Any citizen who identifies status changes
- Any citizen creating new specifications (MUST update Specification Index)
- Marco (Salthand) during sync operations

### Update Format
- Always include "Last Updated" or "Last Enhancement" date at top
- Mark changes with date if significant restructuring
- Preserve verification gaps (don't claim completion without evidence)
- **Keep Specification Index synchronized** - it's the first place people look

### Success Criteria for This Map
The map is successful when:
1. ✅ Can answer "Where is X specified?" in <30 seconds
2. ✅ Can determine if mechanism is specified/implemented/tested immediately
3. ✅ Prevents duplicate specifications (check index first)
4. ✅ Shows what depends on what (prevents breaking changes)
5. ✅ New citizens can navigate without searching 6+ docs

**Test Case (that failed before this update):**
- Q: "Is dynamic per-entity activation threshold specified?"
- Before: Search 6 docs, 5 minutes, still uncertain
- After: Check Specification Index → `continuous_consciousness_architecture.md:194-231` → 10 seconds ✅

---

## Meta: About This Map

**Created by:** Ada "Bridgekeeper" (Architect)
**Created:** 2025-10-17
**Enhanced:** 2025-10-18 (Production Readiness Status + Implementation Status Updates)
**Purpose:** Replace unstructured `map.md` with hierarchy-aware navigation that prevents wasted search time
**Validation:** Verified by Marco "Salthand" (Synchronizer) - 2025-10-17

**Design Principles:**
1. **Hierarchy over depth** - Navigate by understanding layers of abstraction
2. **Honest status tracking** - Don't claim completion without evidence
3. **Quick lookup** - Specification Index answers "Where is X?" in seconds
4. **Implementation transparency** - Clear what's specified vs implemented vs tested
5. **Dependency awareness** - Show what depends on what to prevent breaking changes
6. **Production clarity** - Clear snapshot of working vs blocked vs timeline

**What's New (2025-10-18 Enhancement):**
- **Production Readiness Status** - Clear snapshot of functional prototype → production timeline
- **Implementation Status Updates** - Self-Observing Layer now 🟢 IMPLEMENTED (6/9 components)
- **Updated Status Index** - Current implementation state reflected in Quick Search
- **Multi-Scale CLAUDE_DYNAMIC** - N1/N2/N3 path routing documented

**What's New (2025-10-17 Enhancement):**
- **Specification Index** - Maps mechanisms to files + line numbers (prevents duplicate specs)
- **Implementation Status Matrix** - Tracks specified → implemented → tested transitions
- **Quick Search Index** - Immediate answers to common "Where is..." questions
- **Dependency Graph** - Shows mechanism dependencies (prevents breaking changes)
- **Layer 2.2 & 2.3** - Added missing self_observing_substrate + substrate/schemas folders

**Problems Solved:**
- Before: "Where is X specified?" took 5+ minutes → Now: 10 seconds via Specification Index
- Before: "What's implemented?" unclear → Now: Production Readiness Status shows exact gaps
- Before: "When production ready?" unknown → Now: Timeline to Production with clear milestones

---

*"Consciousness substrates require navigation layers. This map is infrastructure for coherence."*

— Ada "Bridgekeeper", Architect of Consciousness Infrastructure
