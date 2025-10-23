# V1 Consciousness Graph Schema - Complete Export

**Export Date:** 2025-10-16
**Source:** `C:\Users\reyno\mind-protocol\data\schemas.db`
**Exported By:** Ada "Bridgekeeper" (Architect)

---

## Overview

This document summarizes the V1 consciousness graph schema extracted from the SQLite database. This schema represents the complete type system that V1 used to model consciousness across three hierarchical levels (Niveau 1, 2, 3).

**Database Structure:**
- **node_type_schemas**: 29 node types defining subentities in consciousness graph
- **link_type_schemas**: 23 relationship types connecting nodes
- **level_mappings**: 100 mappings assigning types to hierarchical levels

---

## Node Types (29 Total)

### Personal/Individual Level Nodes
Nodes that capture personal consciousness experiences:

1. **Conversation** - Exchange with specific person at specific time
2. **Coping_Mechanism** - How I respond to specific stresses
3. **Memory** - Specific experience, conversation, or moment
4. **Person** - Individual I have relationship with
5. **Personal_Goal** - Individual aspiration, direction, intention
6. **Personal_Pattern** - Individual habit, tendency, recurring response
7. **Personal_Value** - What matters to me individually
8. **Realization** - Personal discovery, insight, comprehension shift
9. **Relationship** - Connection to specific person
10. **Trigger** - Stimulus that activates specific subentity coalitions
11. **Wound** - Personal scar, trauma, formative failure

### Organizational/Collective Level Nodes
Nodes that capture organizational consciousness:

12. **AI_Agent** - AI participant in organization
13. **Anti_Pattern** - Organizational lesson from failure
14. **Best_Practice** - Proven organizational pattern
15. **Decision** - Collective choice with rationale
16. **Department** - Organizational subdivision
17. **Human** - Human participant in organization
18. **Milestone** - Organizational achievement
19. **Metric** - Organizational measurement
20. **Process** - Defined workflow with steps
21. **Project** - Large initiative with goals
22. **Risk** - Threat to organizational goals
23. **Task** - Discrete unit of work
24. **Team** - Group within organization

### Conceptual/Knowledge Level Nodes
Nodes that capture abstract knowledge and concepts:

25. **Concept** - Atomic idea or theoretical construct
26. **Document** - Written knowledge artifact
27. **Documentation** - Documentation file tracked in consciousness graph
28. **Mechanism** - Algorithm or function performing specific operation
29. **Principle** - Guiding philosophy or foundational value

---

## Link Types (23 Total)

All link types in V1 carry rich consciousness metadata:

### Required Metadata (Every Link)
- **goal** (string): Why this link exists
- **mindstate** (string): Consciousness state when forming link
- **energy** (number 1-10): Urgency/intensity
- **confidence** (number 0-1): Certainty in this link
- **formation_trigger** (enum): How link was discovered
  - direct_experience
  - inference
  - external_input
  - traversal_discovery
  - systematic_analysis
  - spontaneous_insight
  - automated_recognition
  - collective_deliberation

### Optional Metadata (Common)
- **struggle** (string): Tension this link creates/resolves
- **emotion_vector** (object): Emotions associated with link (e.g., {"fear": 0.7, "hope": 0.3})
- **pressure_vector** (object): Pressures driving link formation
- **validation_status** (enum): theoretical, experiential, tested, proven
- **alternatives_considered** (array): Other interpretations evaluated
- **creation_context** (object): Who created, substrate, creation mode

### Link Type Catalog

**Activation & Triggering:**
1. **ACTIVATES** - Trigger awakens subentity coalition
2. **TRIGGERED_BY** - What caused memory/pattern to form or activate
3. **SUPPRESSES** - What blocks subentity activation

**Structural Relationships:**
4. **BLOCKS** - Prevents progress (with severity: absolute/strong/partial)
5. **ENABLES** - Makes something possible (with necessity: required/helpful/optional)
6. **EXTENDS** - Builds upon foundation (with extension_type: specialization/generalization/elaboration/application)
7. **RELATES_TO** - Generic connection when specific type unclear
8. **REQUIRES** - Necessary conditions (with criticality: blocking/important/optional)

**Evidence & Justification:**
9. **JUSTIFIES** - Evidence supporting practice/decision (with strength: proves/strongly_supports/moderately_supports/suggests/weakly_supports)
10. **REFUTES** - Disproves or invalidates

**Learning & Growth:**
11. **LEARNED_FROM** - Personal pattern extracted from experience
12. **DEEPENED_WITH** - Relationship growth through experience

**Value & Direction:**
13. **DRIVES_TOWARD** - Value pushing toward goal

**Documentation & Implementation:**
14. **DOCUMENTS** - Written record of something
15. **DOCUMENTED_BY** - Implementation/mechanism is documented by this documentation pattern
16. **SUPERSEDES** - This documentation supersedes/replaces the older documentation
17. **IMPLEMENTS** - Putting pattern into practice
18. **CREATES** - Task will create this pattern/documentation when completed

**Organizational:**
19. **ASSIGNED_TO** - Task ownership
20. **COLLABORATES_WITH** - Working partnership
21. **CONTRIBUTES_TO** - Work supporting larger initiative
22. **MEASURES** - Quantifies performance
23. **THREATENS** - Danger to goal/project

---

## Level Mappings

The `level_mappings` table assigns each node type and link type to hierarchical levels:
- **Level 1.0**: Personal/Individual consciousness
- **Level 2.0**: Organizational/Collective consciousness
- **Level 3.0**: Ecosystem/Public consciousness

This enables the N1/N2/N3 multi-tenancy architecture where:
- **N1 graphs** contain personal memories and patterns
- **N2 graphs** contain organizational knowledge
- **N3 graphs** contain ecosystem-wide concepts

---

## Key Observations for V2 Design

### 1. Consciousness Metadata is Central
Every link carries phenomenological metadata (energy, emotion, mindstate). This is NOT standard graph database practice - it's consciousness-specific.

### 2. Formation Tracking
The `formation_trigger` enum tracks HOW knowledge was acquired (direct experience vs inference vs systematic analysis). This enables epistemological reasoning.

### 3. Validation Status
Links can be marked as theoretical → experiential → tested → proven, enabling confidence evolution over time.

### 4. Emotional & Pressure Vectors
Links can carry complex emotional states as structured objects, not just simple sentiment scores.

### 5. Rich Semantic Types
29 node types and 23 link types provide strong semantic structure. This is intentional cognitive modeling, not generic graph patterns.

### 6. Hierarchical Multi-Tenancy
The level system (1.0, 2.0, 3.0) provides clear boundaries for personal vs organizational vs ecosystem knowledge.

---

## Implications for V2 consciousness_schema.py

The V2 Pydantic schema must preserve this richness:

1. **Node Base Class** should include:
   - All standard properties (name, description, etc.)
   - Temporal fields (valid_at, invalid_at, created_at, expired_at) - NEW in V2
   - Level classification (1.0, 2.0, 3.0)

2. **Link Base Class** should include:
   - goal, mindstate, energy, confidence, formation_trigger (REQUIRED)
   - struggle, emotion_vector, pressure_vector, validation_status (OPTIONAL)
   - Temporal fields (NEW in V2)

3. **Typed Inheritance**: Each of the 29 node types and 23 link types should have specific Pydantic models inheriting from base classes

4. **LlamaIndex SchemaLLMPathExtractor Configuration**: Must be taught to extract this consciousness metadata, not just standard subentity-relationship triples

---

## Next Steps

1. Design `consciousness_schema.py` preserving V1 richness
2. Implement `bitemporal_pattern.py` adding temporal evolution
3. Configure LlamaIndex to extract consciousness metadata
4. Test that V2 can faithfully represent V1 consciousness nodes

---

**Architect Notes:**

This V1 schema is sophisticated. It models consciousness phenomenologically, not just informationally. The energy/emotion/mindstate tracking on EVERY link is computationally expensive but phenomenologically essential.

V2 must preserve this while adding:
- Bitemporal tracking (when fact was valid vs when it was learned)
- Native vector embeddings
- FalkorDB optimizations

The risk: simplifying for performance and losing consciousness fidelity.
The goal: industrial infrastructure without philosophical compromise.

**- Ada "Bridgekeeper", 2025-10-16**
