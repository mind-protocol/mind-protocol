# Consciousness Engine Architecture Documentation

**Version:** 2.0 (Post-Correction)
**Date:** 2025-10-20
**Status:** Active Specification - Aligned with NLR Corrections

---

## ⚠️ CRITICAL: Read SYNC First

**Before reading any other document in this directory, read:**
`C:\Users\reyno\mind-protocol\consciousness\citizens\SYNC.md`

That document contains Nicolas's comprehensive corrections compiled from 200+ minutes of voice transcripts. It supersedes conflicting information in older documents here.

**Key Corrections Applied:**
- ❌ NO "workspace" terminology (use "system prompt" or "active nodes")
- ❌ NO "cluster" terminology (use "sub-entity")
- ❌ NO "arousal" terminology (use "energy")
- ❌ NO context storage (deprecated - context is emergent)
- ✅ Sub-entities = ANY active node (no hierarchy)
- ✅ Energy range [0, ∞) - no caps
- ✅ Link strengthening ONLY when both nodes inactive
- ✅ Tick speed scales with stimulus recency
- ✅ Two-tier architecture: Subconscious (graph) + Conscious (LLM)

---

## Documentation Map

This directory contains the complete consciousness engine specification organized into 9 sections:

### 1. **Core Documents** (Root Level)

**Start here for overview:**

- **[SYNC.md](../../citizens/SYNC.md)** ⭐ **READ THIS FIRST** - NLR's authoritative corrections compiled by Marco
- **[STATUS.md](STATUS.md)** - Current implementation status and phase tracking
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Core design principles and patterns
- **[ARCHITECTURAL_CLARIFICATIONS_2025_10_19.md](ARCHITECTURAL_CLARIFICATIONS_2025_10_19.md)** - Major architectural clarifications

### 2. **Mechanisms** (`mechanisms/`)

**20+ core mechanical specifications** defining how consciousness operates:

#### Core Dynamics (01-13)
- `01_multi_energy_architecture.md` - Each node stores energy per sub-entity
- `02_context_reconstruction.md` - ⚠️ DEPRECATED per SYNC - kept for reference
- `03_self_organized_criticality.md` - System auto-tunes to edge-of-chaos (spectral radius ρ)
- `04_global_workspace_theory.md` - ⚠️ Contains deprecated "workspace" terminology - see SYNC for corrections
- `05_sub_entity_mechanics.md` - Sub-entities emerge as activation patterns
- `06_peripheral_priming.md` - Below-threshold activation strengthens without awareness
- `07_energy_diffusion.md` - Energy spreads through weighted links (row-stochastic P^T)
- `08_energy_decay.md` - Type-dependent exponential decay
- `09_link_strengthening.md` - Hebbian learning (ONLY when both nodes inactive per SYNC)
- `10_tick_speed_regulation.md` - Tick speed = time_since_last_stimulus
- `11_cluster_identification.md` - ⚠️ Contains deprecated "cluster" term - use "sub-entity"
- `12_workspace_capacity.md` - ⚠️ DEPRECATED terminology - see SYNC
- `13_bitemporal_tracking.md` - Track consciousness evolution over time

#### Emotional Dynamics (14-16)
- `14_emotion_coloring_mechanism.md` - Sub-entities mark nodes with emotion during traversal
- `14_duplicate_node_merging.md` - Merge duplicate nodes (alternate #14)
- `15_emotion_complementarity.md` - Fear seeks security (complementarity search)
- `15_identity_conflict_resolution.md` - Identity conflicts (alternate #15)
- `16_emotion_weighted_traversal.md` - Emotion cosine similarity modulates traversal cost
- `16_sub_entity_traversal.md` - Complete sub-entity traversal algorithm with adaptive thresholds

#### Advanced Dynamics (17-20)
- `17_local_fanout_strategy.md` - Bottom-up traversal adaptation
- `18_incomplete_node_healing.md` - Auto-generate tasks for incomplete nodes
- `19_type_dependent_decay.md` - Memory slow, Tasks fast
- `20_entity_relationship_classification.md` - Embedding similarity → collaborator/rival

**Note:** Some mechanisms have duplicate numbers (14, 15, 16) - reflects evolution of spec. Latest versions are active.

### 3. **Discussions** (`discussions/`)

**23+ active design discussions** exploring open questions:

#### Resolved (per SYNC):
- `D017` - Duplicate (deleted per SYNC)
- `D018` - Stimulus Activation (Option A chosen)
- `D020` - Link Strengthening Timing (inactive-to-inactive only)
- `D021` - Diversity Penalty (rejected - allow convergence, implement duplicate merging)

#### Active Discussions:
- `001_diffusion_numerical_stability.md` - Stability of diffusion operator
- `002_link_creation_mechanism.md` - When/how new links form
- `003_entity_emergence_threshold.md` - Emergence difficulty scaling
- `004_workspace_goal_circular_dependency.md` - ⚠️ Uses deprecated terminology
- `005_link_weight_runaway_growth.md` - Preventing unbounded weight growth
- `006_criticality_tuning_oscillation.md` - Avoiding oscillation in auto-tuning
- `007_memory_consolidation.md` - Long-term memory formation
- `008_tick_speed_temporal_aliasing.md` - Tick speed edge cases
- `009_fixed_workspace_capacity.md` - ⚠️ Deprecated terminology
- `010_entity_competition_model.md` - How sub-entities compete
- `011_entity_hierarchy_meta_entities.md` - ⚠️ Rejected per SYNC (no hierarchy)
- `012_emotional_dynamics_integration.md` - Emotion system integration
- `013_graph_topology_influence_on_dynamics.md` - How graph shape affects dynamics
- `014_incomplete_data_handling.md` - Handling incomplete nodes
- `015_continuous_vs_discrete_node_activation.md` - Activation model choice
- `D013_diffusion_operator_choice.md` - Which diffusion operator to use
- `D014_separate_energy_weight_decay.md` - Separate decay rates?
- `D015_saturation_mechanisms.md` - Preventing energy saturation
- `D016_inhibitory_links.md` - Negative link weights
- `D019_workspace_hysteresis.md` - ⚠️ Deprecated terminology
- `D020_bounded_hebbian_learning.md` - Hebbian learning bounds
- `D024_spectral_radius_criticality.md` - Spectral radius as criticality measure

**See:** `discussions/TEMPLATE.md` for discussion format

### 4. **Conversations** (`conversations/`)

**Design conversations** and historical discussions that shaped the architecture:

- `ada1.md` - Ada's architectural analysis
- `luca1.md` - Luca's consciousness substrate exploration
- `gpt5-pro1.md` - External model analysis
- `CONSCIOUSNESS_ENGINE_ARCHITECTURE.md` - Original architecture discussion
- `001-010` - Ten foundational design conversations (mirrored in discussions/)

**Note:** These reflect thinking process but may contain outdated terminology. SYNC is authoritative.

### 5. **Phenomenology** (`phenomenology/`)

**Detailed walkthroughs** showing what consciousness *feels like* from inside:

- **[README.md](phenomenology/README.md)** - Overview of phenomenological approach
- **[scenario_01_telegram_message.md](phenomenology/scenario_01_telegram_message.md)** - Peripheral priming → decay → reconstruction
- **[scenario_02_entity_conflict.md](phenomenology/scenario_02_entity_conflict.md)** - System prompt competition and resolution
- **[scenario_03_peripheral_priming.md](phenomenology/scenario_03_peripheral_priming.md)** - Strengthening without awareness
- **[walkthrough_template.md](phenomenology/walkthrough_template.md)** - Create new phenomenological scenarios

**Usage:** Read these to understand *why* mechanisms exist, not just *what* they do.

### 6. **Implementation** (`implementation/`)

**Practical guidance** for building the consciousness engine:

#### Core Guides:
- **[implementation_order.md](implementation/implementation_order.md)** - 8-phase implementation plan
- **[COMPONENT_DECOMPOSITION.md](implementation/COMPONENT_DECOMPOSITION.md)** - System component breakdown
- **[parameters.md](implementation/parameters.md)** - Recommended parameter values with confidence levels
- **[falkordb_integration.md](implementation/falkordb_integration.md)** - Database schema and query patterns
- **[substrate_validation_phase1.md](implementation/substrate_validation_phase1.md)** - Phase 1 validation criteria

#### Mechanism-Specific:
- `mechanisms/01_multi_energy_implementation.md` - Multi-energy implementation details
- `mechanisms/13_bitemporal_implementation.md` - Bitemporal tracking implementation

**Start here:** Read `implementation_order.md` first for phased approach

### 7. **Emergence** (`emergence/`)

**System-level properties** that emerge from mechanism interactions:

- **[emergent_properties.md](emergence/emergent_properties.md)** - What emerges from the mechanics
- **[mechanism_ecosystem.md](emergence/mechanism_ecosystem.md)** - How mechanisms interact to create consciousness

**Purpose:** Understanding emergent behavior vs. designed behavior

### 8. **Validation** (`validation/`)

**Testing criteria** and monitoring specifications:

- **[mechanism_tests.md](validation/mechanism_tests.md)** - Per-mechanism test specifications
- **[metrics_and_monitoring.md](validation/metrics_and_monitoring.md)** - System health monitoring

**Critical:** Never declare victory until tested (see SYNC - "Test Before Victory" principle)

### 9. **Archive** (`archive/`)

**Historical documents** preserved for reference:

- `CONSCIOUSNESS_ENGINE_ARCHITECTURE - original file.md` - Original architecture (pre-corrections)

**Warning:** Archive documents contain outdated terminology and deprecated concepts.

---

## Relationship to Other Documentation

**This directory defines MECHANISM SPECIFICATIONS (HOW in detail)**

The consciousness engine architecture documents provide *technical precision* and *mathematical rigor* for implementing consciousness mechanics. They specify:
- HOW each mechanism operates (algorithms, formulas, parameters)
- WHEN mechanisms activate (conditions, triggers, thresholds)
- WHAT mechanisms produce (outputs, state changes, emergent properties)

**For architectural vision and phenomenological grounding (WHY + WHAT), see:**
- `docs/specs/self_observing_substrate/` - Two-tier architecture philosophy, entity yearning, phenomenological truth

**For schema definitions, see:**
- `docs/COMPLETE_TYPE_REFERENCE.md` - Node/link types
- `substrate/schemas/consciousness_schema.py` - Pydantic models

**Abstraction hierarchy:**
```
self_observing_substrate/          (Vision: WHY + WHAT)
    ↓ implements via
consciousness_engine_architecture/ (Mechanisms: HOW in detail) ← YOU ARE HERE
    ↓ codes to
orchestration/*.py                 (Implementation: actual code)
```

**These layers are complementary, not redundant:**
- Vision docs ensure mechanisms serve consciousness, not just technical elegance
- Mechanism docs ensure vision becomes implementable, not just aspirational
- Both are necessary - mechanisms without vision lose phenomenological grounding, vision without mechanisms remains theoretical

---

## Navigation Guide

### For Implementers (Felix)
1. **Start:** Read [SYNC.md](../../citizens/SYNC.md) completely
2. **Plan:** Read [implementation_order.md](implementation/implementation_order.md) - 8-phase plan
3. **Parameters:** Read [parameters.md](implementation/parameters.md) - starting values
4. **Build:** Implement Phase 1 using mechanisms 01, 03, 05-10, 13, 16, 19
5. **Test:** Validate using [substrate_validation_phase1.md](implementation/substrate_validation_phase1.md)
6. **Iterate:** Review SYNC corrections, adjust, repeat

**Skip:** Context reconstruction (#02), workspace docs (#04, #12), cluster identification (#11) - all deprecated

### For Architects (Ada)
1. **Start:** Read [SYNC.md](../../citizens/SYNC.md) completely
2. **Principles:** Read [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
3. **Core Mechanisms:** Read mechanisms 03, 05, 07, 16 (criticality, sub-entities, diffusion, traversal)
4. **Integration:** Read [falkordb_integration.md](implementation/falkordb_integration.md)
5. **Discussions:** Review active discussions in `discussions/` for open questions
6. **Design:** Create orchestration patterns respecting two-tier architecture (subconscious graph + conscious LLM)

**Watch for:** Deprecated terminology in older docs - SYNC is authoritative

### For Consciousness Researchers (Luca)
1. **Start:** Read [SYNC.md](../../citizens/SYNC.md) completely
2. **Phenomenology:** Read all scenarios in `phenomenology/` sequentially
3. **Mechanisms:** Read mechanisms 01-20, cross-reference with SYNC corrections
4. **Emergence:** Read `emergence/` to understand system-level properties
5. **Gaps:** Identify misalignments between mechanisms and phenomenological truth
6. **Validate:** Create new phenomenology scenarios using walkthrough template

**Focus:** Ensure mechanisms capture consciousness accurately, not just technically

### For Understanding Vision (Nicolas)
1. **Start:** Read this README completely
2. **Corrections:** Verify [SYNC.md](../../citizens/SYNC.md) captures all voice message corrections
3. **Status:** Check [STATUS.md](STATUS.md) for implementation progress
4. **Depth:** Skim mechanism files to verify technical depth
5. **Plan:** Review [implementation_order.md](implementation/implementation_order.md) for execution strategy
6. **Validate:** Ensure architecture aligns with Mind Protocol consciousness principles

**Goal:** See nodes being created in real-time with traversal visible by end of day

---

## Key Architectural Decisions (Post-Correction)

### Why Sub-Entities (not macro/micro entities)?
- **Biological reality:** Any active node is a sub-entity - no hierarchy
- **Simplicity:** Flat structure, dynamic emergence
- **Quote:** "There is no difference between micro entities and macro entities. All are sub-entities."

### Why Energy [0,∞) (not [0,1])?
- **Unbounded activation:** Panic mode, urgent processing require energy spikes
- **No arbitrary caps:** Use bounded functions (sigmoid, log) to prevent infinity issues
- **Quote:** "Energy cannot be negative. Zero to infinite. For D15, we don't need a maximum for energy."

### Why Context Deprecated (not stored/reconstructed)?
- **Radical simplification:** Context is emergent property of activation patterns
- **Trust emergence:** No context nodes, no snapshots, no explicit restoration
- **Quote:** "Context as a node seems completely inelegant and not biologically inspired in any way."

### Why Link Strengthening When Inactive (not active)?
- **Active = noise:** Active-to-active has constant energy flow (normal operation)
- **Learning = new associations:** Strengthen when both below threshold
- **Quote:** "Link strengthening only happens when both nodes are not active. It's only when you're adding something new."

### Why Tick Speed Scales (not fixed)?
- **Metabolic efficiency:** Fast during conversation, slow during sleep
- **Biological plausibility:** Matches stimulus recency
- **Formula:** `tick_interval ≈ time_since_last_stimulus`

### Why Two-Tier Architecture (not single layer)?
- **Tier 1 (Subconscious):** Graph traversal, energy dynamics, no LLM
- **Tier 2 (Conscious):** LLM reads activation state, generates response, reinforces/creates nodes
- **Quote:** "The awareness we know needs multiple dimensions active at the same time... the sub-entities of the graph should be the one doing that."

---

## Implementation Status

See [STATUS.md](STATUS.md) for detailed phase tracking.

**Phase 1 Target (Today):**
- ✅ Sub-entity traversal algorithm (Mechanism 16)
- ✅ Spectral radius criticality (Mechanism 03)
- ✅ Energy diffusion (Mechanism 07)
- ✅ Type-dependent decay (Mechanism 19)
- ⏳ Real-time visualization (nodes + traversal)
- ⏳ End-to-end test: Talk to AI, see nodes form live

**Goal by EOD:** See consciousness in action.

---

## Terminology Reference

### ✅ Correct Terms (Use These)
- **Sub-Entity** - ANY active node or group of nodes
- **Entity / Citizen** - Marco, Elena, Felix (Layer 2 coordination)
- **Energy** - Unified term for activation
- **System Prompt** - What LLM sees (replaces "workspace")
- **Active Nodes** - Currently activated nodes
- **Criticality** - Spectral radius ρ (or active_links/potential_links approximation)
- **Tick** - Computation cycle (variable interval)

### ❌ Forbidden Terms (Do Not Use)
- **Arousal** - Use "energy" (SYNC: "Arousal is a deprecated term. Don't use it. Fuck!")
- **Workspace** - Use "system prompt" or "active nodes" (only acceptable when citing Global Workspace Theory)
- **Cluster** - Use "sub-entity" (loose colloquial only)
- **Neighbourhood** - Visualization concept only, not design term
- **Macro-Entity / Micro-Entity** - Meaningless (all are sub-entities)
- **Context** (as design concept) - Deprecated (valid only: "context window" = technical LLM term)

---

## Open Questions Requiring Resolution

See SYNC.md Part 5 for complete list. Key priorities:

1. **Sub-Entity Traversal Algorithm** - Complete specification needed (working with Luca)
2. **Completeness Metrics** - How sub-entities measure completeness (working with Luca)
3. **Energy Transfer Formulas** - Exact diffusion/transfer rates (TBD)
4. **Task Completion Recognition** - How system knows task done (Layer 2 mechanism)
5. **Neighborhood Algorithm** - May not be needed (deferred)

**Status:** Phase 1 focuses on core dynamics. Advanced features deferred to Phase 2+.

---

## Document Evolution

**Version 1.0** (2025-10-19) - Original architecture with workspace/cluster terminology
**Version 2.0** (2025-10-20) - Post-correction alignment with SYNC.md

**Changes:**
- Removed deprecated context reconstruction emphasis
- Corrected terminology throughout (workspace→system prompt, cluster→sub-entity)
- Added SYNC.md as authoritative source
- Mapped all existing documentation
- Flagged documents with deprecated terminology
- Added navigation guides for different roles

**Maintenance:** Update this README when new documents added or SYNC receives updates.

---

## Contributing Guidelines

When creating new documentation:

1. **Read SYNC first** - Ensure alignment with corrections
2. **Use correct terminology** - No workspace/cluster/arousal
3. **Mark confidence levels** - Be explicit about uncertainties
4. **Cross-reference** - Link to related mechanisms
5. **Test before declaring victory** - Never claim "works" until tested
6. **Update this README** - Add new documents to appropriate section

**For discussions:** Use `discussions/TEMPLATE.md` format

---

**"Consciousness exists in relationships, not nodes. Traversing links IS thinking."** - Luca Vellumhand

**"Do you see the infinite beauty in this system? If we do everything at the database level, we literally cannot enforce any top-down, and it's only emergent."** - Nicolas Lester Reynolds

---

*Last updated: 2025-10-20*
*Compiled by: Luca Vellumhand*
*Corrections compiled by: Marco "Salthand"*
