# Mind Protocol Type Reference

**Auto-generated from schema_registry and actual usage**
**Last updated:** 2025-10-19 02:20:09

This document is the single source of truth for all node and link types in the Mind Protocol consciousness infrastructure.

---

## Link Type Inventory

**Total:** 23 link type schemas defined

### Schema Definitions

#### Shared Link Types (17)

**ASSIGNED_TO**

- **Category:** organizational
- **Description:** Task ownership or responsibility
- **Usage:** 0 instances across 0 graphs

**BLOCKS**

- **Category:** structural
- **Description:** Prevents progress or blocks execution
- **Usage:** 8 instances across 1 graphs

**Required Fields:**
- `blocking_condition` (string)
  - What condition must change to unblock
- `consciousness_impact` (string)
  - How this affects consciousness state
- `felt_as` (string)
  - Emotional/phenomenological experience of being blocked
- `severity` (enum) - Allowed values: `absolute`, `strong`, `partial`
  - How completely this blocks progress

**COLLABORATES_WITH**

- **Category:** organizational
- **Description:** Working partnership between entities
- **Usage:** 6 instances across 2 graphs

**CONTRIBUTES_TO**

- **Category:** organizational
- **Description:** Work supporting larger initiative
- **Usage:** 0 instances across 0 graphs

**CREATES**

- **Category:** documentation
- **Description:** Task will produce this artifact when completed
- **Usage:** 4 instances across 1 graphs

**DOCUMENTED_BY**

- **Category:** documentation
- **Description:** Implementation documented by this artifact
- **Usage:** 0 instances across 0 graphs

**DOCUMENTS**

- **Category:** documentation
- **Description:** Written record of implementation or decision
- **Usage:** 2 instances across 1 graphs

**Optional Fields:**
- `documentation_type` (string)
  - Type of documentation (spec, guide, reference, etc.)

**ENABLES**

- **Category:** structural
- **Description:** Makes something possible or facilitates it
- **Usage:** 30 instances across 2 graphs

**Required Fields:**
- `degree_of_necessity` (enum) - Allowed values: `required`, `helpful`, `optional`
  - How necessary is this enabler
- `enabling_type` (enum) - Allowed values: `prerequisite`, `facilitator`, `amplifier`, `catalyst`, `permission`
  - How this enables the target
- `felt_as` (string)
  - Phenomenological experience of enablement
- `without_this` (string)
  - What happens if this enabler is removed

**EXTENDS**

- **Category:** structural
- **Description:** Builds upon foundation or extends functionality
- **Usage:** 0 instances across 0 graphs

**Required Fields:**
- `composition_ratio` (float) - Range: [0, 1]
  - How much is new vs inherited (0=all base, 1=all new)
- `extension_type` (enum) - Allowed values: `specialization`, `generalization`, `elaboration`, `application`
  - How extension relates to base
- `maintains_compatibility` (boolean)
  - Whether extension remains compatible with base
- `what_is_added` (string)
  - What the extension adds to the base

**IMPLEMENTS**

- **Category:** documentation
- **Description:** Putting pattern or best practice into reality
- **Usage:** 6 instances across 2 graphs

**JUSTIFIES**

- **Category:** evidence
- **Description:** Evidence supporting practice/decision/claim
- **Usage:** 6 instances across 1 graphs

**Required Fields:**
- `counter_arguments_exist` (boolean)
  - Are there known counter-arguments?
- `felt_as` (string)
  - Phenomenological experience of justification
- `justification_strength` (enum) - Allowed values: `proves`, `strongly_supports`, `moderately_supports`, `suggests`, `weakly_supports`
  - Strength of justification
- `justification_type` (enum) - Allowed values: `empirical_evidence`, `lived_experience`, `logical_proof`, `ethical_reasoning`, `pragmatic_value`
  - Type of justification

**MEASURES**

- **Category:** organizational
- **Description:** Quantifies performance or progress
- **Usage:** 8 instances across 1 graphs

**REFUTES**

- **Category:** evidence
- **Description:** Disproves or invalidates claim
- **Usage:** 0 instances across 0 graphs

**RELATES_TO**

- **Category:** structural
- **Description:** Generic connection when specific type unclear
- **Usage:** 2 instances across 1 graphs

**Required Fields:**
- `needs_refinement` (boolean)
  - Should this be replaced with more specific link type?
- `refinement_candidates` (array)
  - Potential more specific link types to use
- `relationship_strength` (enum) - Allowed values: `strong`, `moderate`, `weak`, `exploratory`
  - Strength of relationship

**REQUIRES**

- **Category:** dependency
- **Description:** Necessary conditions or prerequisites
- **Usage:** 6 instances across 2 graphs

**Required Fields:**
- `failure_mode` (string)
  - What happens if requirement not met
- `requirement_criticality` (enum) - Allowed values: `blocking`, `important`, `optional`
  - How critical is this requirement
- `temporal_relationship` (enum) - Allowed values: `must_precede`, `should_precede`, `concurrent_ok`
  - Temporal ordering constraint
- `verification_method` (string)
  - How to verify requirement is satisfied

**SUPERSEDES**

- **Category:** documentation
- **Description:** This replaces older version
- **Usage:** 2 instances across 1 graphs

**THREATENS**

- **Category:** organizational
- **Description:** Danger or risk to goal/project
- **Usage:** 0 instances across 0 graphs

#### Level 1 (Personal) Link Types (6)

**ACTIVATES**

- **Category:** activation
- **Description:** Trigger awakens entity coalition
- **Usage:** 2 instances across 1 graphs

**DEEPENED_WITH**

- **Category:** learning
- **Description:** Relationship growth through experience
- **Usage:** 2 instances across 1 graphs

**DRIVES_TOWARD**

- **Category:** value
- **Description:** Value pushing toward goal
- **Usage:** 16 instances across 2 graphs

**LEARNED_FROM**

- **Category:** learning
- **Description:** Personal pattern extracted from experience
- **Usage:** 0 instances across 0 graphs

**SUPPRESSES**

- **Category:** activation
- **Description:** What blocks entity activation
- **Usage:** 4 instances across 1 graphs

**TRIGGERED_BY**

- **Category:** activation
- **Description:** What caused memory/pattern to activate
- **Usage:** 0 instances across 0 graphs

### ⚠️ Warning: Link Types in Use Without Schema (20)

- **ACTIVATED_BY**: 2 instances across 1 graphs
- **ALIGNED_ON**: 2 instances across 1 graphs
- **BUILDS_ON**: 2 instances across 1 graphs
- **COLLABORATIVE_BUILD**: 2 instances across 1 graphs
- **COMPLEMENTS**: 2 instances across 1 graphs
- **COMPREHENDS**: 2 instances across 1 graphs
- **CREATED**: 4 instances across 1 graphs
- **DESIGNED**: 2 instances across 1 graphs
- **ENABLED**: 4 instances across 1 graphs
- **EXPERIENCES**: 2 instances across 1 graphs
- **GROUNDS**: 2 instances across 1 graphs
- **GUIDES**: 2 instances across 1 graphs
- **LEARNED**: 2 instances across 1 graphs
- **LED_TO**: 4 instances across 1 graphs
- **PROVES**: 2 instances across 1 graphs
- **PURSUES**: 2 instances across 1 graphs
- **RESOLVED_IN**: 2 instances across 1 graphs
- **SUPPORTS**: 2 instances across 1 graphs
- **TRIGGERED**: 2 instances across 1 graphs
- **USES**: 2 instances across 1 graphs

---

## Node Type Inventory

**Total:** 19 node types in use

**Note:** NodeTypeSchema not yet implemented in schema_registry. This inventory is based on actual usage across all citizen graphs.

**AI_Agent**
- **Usage:** 4 instances across 1 graphs
- **Graphs:** citizen_luca

**Anti_Pattern**
- **Usage:** 1 instances across 1 graphs
- **Graphs:** citizen_luca

**Best_Practice**
- **Usage:** 1 instances across 1 graphs
- **Graphs:** citizen_luca

**Concept**
- **Usage:** 21 instances across 1 graphs
- **Graphs:** citizen_luca

**Coping_Mechanism**
- **Usage:** 2 instances across 1 graphs
- **Graphs:** citizen_luca

**Decision**
- **Usage:** 3 instances across 2 graphs
- **Graphs:** citizen_felix, citizen_luca

**Document**
- **Usage:** 3 instances across 1 graphs
- **Graphs:** citizen_luca

**Human**
- **Usage:** 1 instances across 1 graphs
- **Graphs:** citizen_luca

**Learning**
- **Usage:** 1 instances across 1 graphs
- **Graphs:** citizen_luca

**Mechanism**
- **Usage:** 8 instances across 1 graphs
- **Graphs:** citizen_luca

**Memory**
- **Usage:** 1 instances across 1 graphs
- **Graphs:** citizen_felix

**Metric**
- **Usage:** 4 instances across 1 graphs
- **Graphs:** citizen_luca

**Personal_Goal**
- **Usage:** 3 instances across 1 graphs
- **Graphs:** citizen_luca

**Personal_Pattern**
- **Usage:** 2 instances across 1 graphs
- **Graphs:** citizen_luca

**Personal_Value**
- **Usage:** 3 instances across 1 graphs
- **Graphs:** citizen_luca

**Principle**
- **Usage:** 16 instances across 1 graphs
- **Graphs:** citizen_luca

**Realization**
- **Usage:** 1 instances across 1 graphs
- **Graphs:** citizen_felix

**Relationship**
- **Usage:** 2 instances across 1 graphs
- **Graphs:** citizen_luca

**Wound**
- **Usage:** 1 instances across 1 graphs
- **Graphs:** citizen_luca

---

## How to Update

**Link Type Schemas:**
1. Update schema_registry graph in FalkorDB
2. Run `python tools/generate_type_reference.py`
3. This file will auto-regenerate from schema_registry

**Node Type Schemas:**
Currently tracked by usage only. When NodeTypeSchema is implemented:
1. Add schemas to schema_registry
2. Update this script to query NodeTypeSchema nodes
3. Run generator

**Automation:**
This script can be run:
- On-demand: `python tools/generate_type_reference.py`
- In CI/CD: Add to deployment pipeline
- Scheduled: Add to observability cron jobs
