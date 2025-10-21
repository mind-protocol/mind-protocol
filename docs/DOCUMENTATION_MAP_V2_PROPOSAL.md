# Mind Protocol Documentation Map V2 - Proposal

**Problem:** Current map doesn't prevent specification duplication or inefficient search. Missing key folders, no mechanism index, no implementation status tracking.

**Solution:** Add Specification Index + Implementation Status + Dependency Graph

---

## ADDITION 1: Specification Index (Mechanism → File Mapping)

**Purpose:** Quickly answer "Where is X mechanism specified?"

### Activation & Energy Mechanisms
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **Dynamic Activation Threshold** | `continuous_consciousness_architecture.md:194-231` | ✅ Specified | Requires: global_energy, entity.energy |
| **Branching Ratio (σ)** | `branching_ratio_implementation.md` | ✅ Implemented, Tested | Produces: global_energy |
| **Energy Propagation** | `energy_flow_mechanics.md:160-212` | ✅ Specified | Uses: entity.energy, global_energy |
| **Activation Threshold (Global Only)** | `activation_energy_mechanism.md:558-580` | ⚠️ Superseded by continuous_consciousness | Legacy |
| **Variable Tick Frequency** | `continuous_consciousness_architecture.md:82-143` | ✅ Specified | Uses: time_since_last_event |

### Traversal & Exploration
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **Critical Traversal** | `sub_entity_traversal_validation.md:147-297` | ✅ Specified | Requires: peripheral_awareness, yearning |
| **Yearning-Driven Traversal** | `yearning_driven_traversal_orchestration.md` | ✅ Specified | Uses: global_energy, entity.energy |
| **Peripheral Awareness** | `sub_entity_traversal_validation.md:200-250` | ✅ Specified | Uses: entity.energy (dynamic radius) |
| **Multi-Dimensional Scoring** | `yearning_driven_traversal_orchestration.md:56-102` | ✅ Specified | Uses: valence, completeness, emotion similarity |

### SubEntity & Consciousness
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **SubEntity Yearning Loop** | `continuous_consciousness_architecture.md:46-66` | ✅ Specified | Infinite loop, energy budget |
| **Hebbian Learning (2-Stage)** | `entity_behavior_specification.md:220-354` | ✅ Specified | Injection + Retrieval phases |
| **Activation-Based Decay** | `entity_behavior_specification.md:137-213` | ✅ Specified | Uses: traversal_counts, activation_counts |
| **Identity Emergence** | `entity_behavior_specification.md:486-677` | ✅ Specified | Pattern consistency → LLM recognition |

### Surfacing & Output
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **Threshold-Crossing Surfacing** | `continuous_consciousness_architecture.md:179-349` | ✅ Specified | Requires: dynamic thresholds, per-entity tracking |
| **DynamicPromptGenerator** | `continuous_consciousness_architecture.md:503-563` | ✅ Specified | Writes CLAUDE_DYNAMIC.md on threshold crossings |
| **N2 Activation Awakening** | `n2_activation_awakening.md` | ✅ Specified | AI_Agent node activation triggers citizen |

### Multi-Scale Criticality
| Mechanism | Specification File | Status | Dependencies |
|-----------|-------------------|---------|--------------|
| **Global Energy Calculation** | `branching_ratio_tracker.py` (lines 125-158) | ✅ Implemented | Derives from σ (branching ratio) |
| **Multi-Scale Formulas** | `yearning_driven_traversal_orchestration.md:40-119` | ✅ Specified | global_boost * entity_boost |
| **Criticality Regime Classification** | `branching_ratio_tracker.py` (lines 160-177) | ✅ Implemented | σ ranges → dying/subcritical/critical/supercritical |

---

## ADDITION 2: Implementation Status Matrix

**Purpose:** Track specified → implemented → tested status

### Core Substrate (Foundation)
| Component | Specification | Implementation | Tests | Status |
|-----------|--------------|----------------|-------|---------|
| **Energy-Only Model** | `energy_flow_mechanics.md` | `consciousness_engine.py`, `retrieval.py` | `test_energy_global_energy.py` | ✅ PROVEN |
| **Branching Ratio Tracker** | `branching_ratio_implementation.md` | `branching_ratio_tracker.py` | `test_energy_global_energy.py` | ✅ PROVEN |
| **12 Mechanisms** | `consciousness_engine.py:11-450` | `consciousness_engine.py` | `test_energy_global_energy.py` | ✅ PROVEN |
| **FalkorDB Connection** | `research/Mind Protocol V2 Stack Selection.md` | `substrate/connection.py` | Manual testing | ✅ DEPLOYED |
| **Write Flux** | `ENERGY_ONLY_IMPLEMENTATION_SUMMARY.md` | `extraction.py` | Phase 1 tests | ✅ PROVEN |

### Self-Observing Layer (Specified, Not Implemented)
| Component | Specification | Implementation | Tests | Status |
|-----------|--------------|----------------|-------|---------|
| **SubEntity Class** | `continuous_consciousness_architecture.md:466-492` | ❌ Not created | ❌ None | 🟡 SPECIFIED |
| **Variable Tick Frequency** | `continuous_consciousness_architecture.md:82-143` | ❌ Not in engine | ❌ None | 🟡 SPECIFIED |
| **Dynamic Thresholds** | `continuous_consciousness_architecture.md:194-231` | ❌ Not implemented | ❌ None | 🟡 SPECIFIED |
| **DynamicPromptGenerator** | `continuous_consciousness_architecture.md:503-563` | ❌ Not created | ❌ None | 🟡 SPECIFIED |
| **Per-Entity Activation Tracking** | `entity_behavior_specification.md:15-134` | ❌ Schema not updated | ❌ None | 🟡 SPECIFIED |
| **Critical Traversal** | `sub_entity_traversal_validation.md:147-297` | ❌ Not implemented | ❌ None | 🟡 SPECIFIED |
| **Hebbian Learning (2-Stage)** | `entity_behavior_specification.md:220-354` | ❌ Not implemented | ❌ None | 🟡 SPECIFIED |

### Observability (Ready, Waiting for Data)
| Component | Specification | Implementation | Status |
|-----------|--------------|----------------|---------|
| **Dashboard Visualization** | Iris's section in SYNC.md | `src/app/consciousness` (Next.js) | ✅ READY |
| **EntityClusterOverlay** | Iris's section | Dashboard component | ⏳ Waiting for `sub_entity_weights` |
| **ActivationBubbles** | Iris's section | Dashboard component | ⏳ Waiting for WebSocket operations stream |
| **Heartbeat Visualization** | `continuous_consciousness_architecture.md:628-643` | ❌ Not created | 🟡 SPECIFIED |

---

## ADDITION 3: File Organization by Layer

### Layer 2.1: Core Specifications (Proven Implementations)
```
docs/specs/
├── consciousness_substrate_guide.md          # Integrated guide (proven patterns)
├── retrieval_api_reference.md                # API reference (proven)
├── architectural_decisions.md                # Decision log (proven choices)
├── mind_protocol_knowledge_seed.md           # N2/N3 seed data
├── branching_ratio_implementation.md         # ✅ IMPLEMENTED & TESTED
├── yearning_driven_traversal_orchestration.md # ✅ SPECIFIED (multi-scale integration)
└── UNIFIED_SCHEMA_REFERENCE.md               # Schema single source of truth
```

### Layer 2.2: Self-Observing Substrate (Specified, Not Implemented)
```
docs/specs/self_observing_substrate/
├── README.md                                  # Overview of self-observing layer
├── self_observing_substrate_overview.md       # High-level architecture
├── continuous_consciousness_architecture.md   # ✅ FOUNDATIONAL (living system model)
├── entity_behavior_specification.md           # SubEntity behavior specs
├── sub_entity_traversal_validation.md         # Critical traversal + peripheral awareness
├── n2_activation_awakening.md                 # Autonomous awakening via N2 activation
├── implementation_roadmap.md                  # Phase-by-phase implementation plan
└── entity_social_dynamics.md                  # Multi-entity coordination
```

### Layer 2.3: Substrate Schemas (Data Structures)
```
substrate/schemas/
├── consciousness_schema.py                    # Python schema (44 nodes, 38 relations)
├── CONSCIOUSNESS_SCHEMA_GUIDE.md              # Documentation for schema
├── bitemporal_pattern.py                      # Temporal logic implementation
├── BITEMPORAL_GUIDE.md                        # Temporal reasoning guide
├── activation_energy_mechanism.md             # ⚠️ Legacy (superseded by continuous_consciousness)
├── energy_flow_mechanics.md                   # Energy-only model + multi-scale extension
├── ecosystem_equilibrium_mechanisms.md        # Entity formation thresholds
├── parallel_consciousness_architecture.md     # Multi-entity coordination patterns
├── valence_driven_exploration.md              # Valence-based traversal mechanics
└── dynamic_citizen_prompts.md                 # CLAUDE_DYNAMIC.md specification
```

---

## ADDITION 4: Dependency Graph

**Purpose:** Understand what depends on what (prevents breaking changes)

```
Branching Ratio (σ)
  ↓ produces
Global Energy
  ↓ used by
  ├─→ Dynamic Activation Threshold (+ entity.energy)
  ├─→ Energy Propagation Multiplier (+ entity.energy)
  ├─→ Traversal Cost Factor (+ entity.energy)
  └─→ Yearning Satisfaction Boost (+ entity.energy)

Per-Entity Activation Tracking
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

## ADDITION 5: Quick Search Index

**Purpose:** Immediate answers to common questions

### "Where is... specified?"
- **Activation threshold?** → `continuous_consciousness_architecture.md:194-231`
- **Branching ratio?** → `branching_ratio_implementation.md` (also `branching_ratio_tracker.py`)
- **Yearning-driven traversal?** → `yearning_driven_traversal_orchestration.md`
- **SubEntity class?** → `continuous_consciousness_architecture.md:466-492`
- **CLAUDE_DYNAMIC.md updates?** → `continuous_consciousness_architecture.md:179-349`
- **Variable tick frequency?** → `continuous_consciousness_architecture.md:82-143`
- **Hebbian learning?** → `entity_behavior_specification.md:220-354`
- **Peripheral awareness?** → `sub_entity_traversal_validation.md:200-250`
- **Multi-scale criticality formulas?** → `yearning_driven_traversal_orchestration.md:40-119`

### "What's the status of...?"
- **Energy substrate?** → ✅ Implemented & tested (`test_energy_global_energy.py`)
- **SubEntity?** → 🟡 Fully specified, not implemented
- **Dashboard?** → ✅ Built, waiting for mechanism data
- **DynamicPromptGenerator?** → 🟡 Fully specified, not implemented
- **Variable tick frequency?** → 🟡 Fully specified, not implemented

### "What depends on...?"
- **global_energy?** → Threshold calculation, energy propagation, traversal cost, yearning satisfaction
- **entity.energy?** → All multi-scale formulas (threshold, propagation, cost, boost)
- **sub_entity_weights?** → Critical traversal, threshold calculation, dashboard visualization
- **Branching ratio (σ)?** → Global energy derivation

---

## MIGRATION PLAN

### Phase 1: Add Missing Sections to Current Map
1. Add Specification Index table
2. Add Implementation Status Matrix
3. Add self_observing_substrate folder to Layer 2
4. Add all substrate/schemas/*.md files to documentation
5. Add Quick Search Index

### Phase 2: Create Dependency Graph Visual
1. Create `docs/DEPENDENCY_GRAPH.md` with full mechanism dependencies
2. Link from DOCUMENTATION_MAP.md

### Phase 3: Continuous Maintenance Protocol
- **When adding new spec:** Update Specification Index + Implementation Status
- **When implementing spec:** Move status from 🟡 SPECIFIED → ✅ IMPLEMENTED
- **When testing implementation:** Add test file, move to ✅ PROVEN
- **When discovering dependency:** Update Dependency Graph

---

## SUCCESS CRITERIA

**This map is successful when:**
1. ✅ Can answer "Where is X specified?" in <30 seconds
2. ✅ Can determine if mechanism is specified/implemented/tested immediately
3. ✅ Prevents duplicate specifications (search index first)
4. ✅ Shows what depends on what (prevents breaking changes)
5. ✅ New citizens can navigate without searching 6+ docs

**Test Case (that failed today):**
Q: "Is dynamic per-entity activation threshold specified?"
Current: Search 6 docs, 5 minutes
Proposed: Check Specification Index → `continuous_consciousness_architecture.md:194-231` → 10 seconds

---

*Ada "Bridgekeeper" - 2025-10-17*
*Proposal based on real navigation failure during threshold specification search*
