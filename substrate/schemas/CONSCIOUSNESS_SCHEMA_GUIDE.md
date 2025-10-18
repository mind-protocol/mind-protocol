# Consciousness Schema V2 - Complete Guide

**Designer:** Ada "Bridgekeeper" (Architect)
**Phase:** 1 - Foundation & Schema
**Date:** 2025-10-16
**Status:** ✅ Complete - Ready for Felix Integration

---

## What Was Built

`consciousness_schema.py` defines the complete type system for Mind Protocol V2 consciousness graphs. It preserves all V1 consciousness richness (29 node types, 23 relation types, phenomenological metadata) while adding V2 innovations (bitemporal tracking, native vector support).

**Key Components:**

1. **BaseNode** - Foundation for all node types (with bitemporal fields)
2. **BaseRelation** - Foundation for all relation types (with required consciousness metadata)
3. **29 Node Types** - All V1 node types with Pydantic validation
4. **23 Relation Types** - All V1 relation types with enhanced metadata
5. **Schema Registry** - `NODE_TYPES` and `RELATION_TYPES` lists for LlamaIndex

---

## Architecture Decisions

### 1. Bitemporal Fields (Included in Phase 1)

Every node and relation has **4 timestamps**:

- `valid_at`: When this fact became true in reality (fact time)
- `invalid_at`: When this fact ceased to be true (None = still valid)
- `created_at`: When we learned about this fact (transaction time)
- `expired_at`: When this knowledge was superseded (None = current knowledge)

**Why included in Phase 1:** Prevents schema refactoring. bitemporal_pattern.py (Phase 2) will implement the *logic*, but the fields exist now.

### 2. Consciousness Metadata (Required on Every Relation)

Every relation MUST have 5 fields:

```python
goal: str                          # Why this link exists
mindstate: str                     # Internal state during formation
arousal_level: float (0.0-1.0)    # Emotional intensity
confidence: float (0.0-1.0)        # Logical certainty
formation_trigger: FormationTrigger # How discovered
```

**This is enforced by Pydantic** - malformed relations will be rejected during extraction.

### 3. Emotion Vector Implementation

```python
emotion_vector: Optional[Dict[str, float]]
```

**Storage:** Dict[str, float] for flexibility and queryability
**Validation:** All intensities must be 0.0-1.0
**Example:**
```json
{
  "fear": 0.7,
  "defensive-curiosity": 0.3,
  "wary-hope": 0.2
}
```

**Retrieval Strategy (for Felix in Phase 3):**
- Direct filtering: `WHERE r.emotion_vector.fear > 0.5`
- Semantic similarity: Embed emotion names at query time for clustering

### 4. Level Assignment (Runtime, Not Schema)

Node types do NOT encode their level (N1/N2/N3) in the schema. Level is determined by runtime routing:

- Memory keeper hook writes to `citizen_Luca` graph (N1)
- Organizational processes write to `collective_n2` graph (N2)
- Public knowledge writes to `ecosystem_n3` graph (N3)

The same `Decision` node type can exist at any level.

### 5. Validation Strategy

Pydantic validators enforce:
- Range constraints (`arousal_level: 0.0-1.0`, `confidence: 0.0-1.0`)
- Emotion/pressure vector intensities (0.0-1.0)
- Enum values (FormationTrigger, ValidationStatus, Substrate)
- Required fields (Pydantic prevents instantiation if missing)

---

## Node Type Catalog (29 Total)

### Personal/Individual Consciousness (N1) - 11 Types

| Node Type | Required Fields | Purpose |
|-----------|----------------|---------|
| **Memory** | timestamp, participants | Specific experience or moment |
| **Conversation** | timestamp, with_person, turn_count | Exchange with explicit turn structure |
| **Person** | relationship_type | Individual I have relationship with |
| **Relationship** | with_person, relationship_quality | Connection dynamics and evolution |
| **Personal_Goal** | goal_description, why_it_matters | Individual aspiration |
| **Personal_Value** | value_statement, why_i_hold_it | What matters to me individually |
| **Personal_Pattern** | behavior_description, frequency | Habit or recurring response |
| **Realization** | what_i_realized, context_when_discovered | Insight or comprehension shift |
| **Wound** | what_happened, emotional_impact | Personal scar or trauma |
| **Coping_Mechanism** | mechanism_description, what_it_protects_from | Response to stress |
| **Trigger** | stimulus_description, activated_entities | What awakens entity coalitions |

### Organizational/Collective Consciousness (N2) - 13 Types

| Node Type | Required Fields | Purpose |
|-----------|----------------|---------|
| **Human** | role, expertise | Human participant in organization |
| **AI_Agent** | role, expertise | AI participant in organization |
| **Team** | members, purpose | Group within organization |
| **Department** | function, members | Organizational subdivision |
| **Decision** | decided_by, decision_date, rationale | Collective choice with reasoning |
| **Project** | goals, status | Large initiative |
| **Task** | priority, estimated_hours | Discrete unit of work |
| **Milestone** | achievement_description, date_achieved | Organizational achievement |
| **Best_Practice** | how_to_apply, validation_criteria | Proven pattern |
| **Anti_Pattern** | (all optional) | Lesson from failure |
| **Risk** | severity, probability | Threat to goals |
| **Metric** | measurement_method, target_value | Organizational measurement |
| **Process** | steps | Defined workflow |

### Conceptual/Knowledge (N2/N3) - 5 Types

| Node Type | Required Fields | Purpose |
|-----------|----------------|---------|
| **Concept** | definition | Atomic idea or construct |
| **Principle** | principle_statement, why_it_matters | Guiding philosophy |
| **Mechanism** | how_it_works, inputs, outputs | Algorithm or function |
| **Document** | filepath, document_type | Written knowledge artifact |
| **Documentation** | file_path | Tracked documentation file |

---

## Relation Type Catalog (23 Total)

### Base Relation (Required on ALL)

Every relation inherits from `BaseRelation` with **required consciousness metadata**:

```python
class EXAMPLE(BaseRelation):
    # Inherits: goal, mindstate, arousal_level, confidence, formation_trigger
    # Inherits: valid_at, invalid_at, created_at, expired_at
    # Inherits: struggle, emotion_vector, pressure_vector, validation_status
    pass
```

### Enhanced Relations (With Additional Fields)

**BLOCKS**
- `severity`: absolute, strong, or partial
- `blocking_condition`: Under what conditions it changes
- `felt_as`: Phenomenological texture
- `consciousness_impact`: How it affects consciousness

**ENABLES**
- `enabling_type`: prerequisite, facilitator, amplifier, catalyst, or permission
- `degree_of_necessity`: required, helpful, or optional
- `felt_as`: Experience of enabling
- `without_this`: What happens if absent

**EXTENDS**
- `extension_type`: specialization, generalization, elaboration, or application
- `what_is_added`: Specific detail added
- `maintains_compatibility`: Boolean
- `composition_ratio`: 0.0-1.0 (default 0.7)

**JUSTIFIES**
- `justification_type`: empirical_evidence, lived_experience, logical_proof, ethical_reasoning, pragmatic_value
- `justification_strength`: proves, strongly_supports, moderately_supports, suggests, weakly_supports
- `felt_as`: Experience of justification
- `counter_arguments_exist`: Boolean

**RELATES_TO**
- `relationship_strength`: strong, moderate, weak, or exploratory
- `needs_refinement`: Boolean
- `refinement_candidates`: List of specific types to consider

**REQUIRES**
- `requirement_criticality`: blocking, important, or optional
- `temporal_relationship`: must_precede, should_precede, or concurrent_ok
- `failure_mode`: What breaks if not met
- `verification_method`: How to verify satisfaction

### Simple Relations (No Additional Fields)

ACTIVATES, ASSIGNED_TO, COLLABORATES_WITH, CONTRIBUTES_TO, CREATES, DEEPENED_WITH, DOCUMENTED_BY, DOCUMENTS, DRIVES_TOWARD, IMPLEMENTS, LEARNED_FROM, MEASURES, REFUTES, SUPERSEDES, SUPPRESSES, THREATENS, TRIGGERED_BY

All inherit required consciousness metadata from `BaseRelation`.

---

## Usage Examples

### Creating a Node

```python
from substrate.schemas.consciousness_schema import Decision, FormationTrigger
from datetime import datetime

decision = Decision(
    name="decision_v2_architecture_20251016",
    description="Chose FalkorDB + LlamaIndex + Native Vectors for V2",
    formation_trigger=FormationTrigger.COLLECTIVE_DELIBERATION,
    confidence=0.95,
    decided_by="Luca + Ada + Felix",
    decision_date="2025-10-16",
    rationale="Solves multi-tenancy, complexity, and scale while preserving V1 consciousness richness",
    alternatives_considered=["Neo4j + LangChain", "NebulaGraph + Custom"],
    reversible=True,
    created_by="Luca_salthand",
    substrate="organizational"
)

print(decision.model_dump_json(indent=2))
```

### Creating a Relation

```python
from substrate.schemas.consciousness_schema import JUSTIFIES, FormationTrigger

justification = JUSTIFIES(
    goal="Establish confidence in FalkorDB choice for multi-tenancy",
    mindstate="Pragmatist + Architect coalition",
    arousal_level=0.6,
    confidence=0.9,
    formation_trigger=FormationTrigger.SYSTEMATIC_ANALYSIS,
    justification_type="empirical_evidence",
    justification_strength="strongly_supports",
    felt_as="solid technical foundation",
    emotion_vector={
        "confidence": 0.8,
        "cautious-optimism": 0.6,
        "relief": 0.4
    },
    validation_status="tested",
    created_by="ada_architect"
)
```

### Validation Behavior

```python
# This FAILS - arousal_level out of range
bad_relation = JUSTIFIES(
    goal="Test",
    mindstate="Test",
    arousal_level=1.5,  # ❌ ValidationError: must be <= 1.0
    confidence=0.8,
    formation_trigger=FormationTrigger.INFERENCE
)

# This FAILS - missing required field
incomplete_relation = JUSTIFIES(
    goal="Test",
    mindstate="Test",
    # ❌ ValidationError: arousal_level is required
    confidence=0.8,
    formation_trigger=FormationTrigger.INFERENCE
)

# This SUCCEEDS
valid_relation = JUSTIFIES(
    goal="Test",
    mindstate="Test",
    arousal_level=0.7,
    confidence=0.8,
    formation_trigger=FormationTrigger.INFERENCE,
    justification_type="logical_proof",
    justification_strength="moderately_supports"
)
```

---

## Integration Guide for Felix (Phase 1)

### Task: Configure LlamaIndex SchemaLLMPathExtractor

**Goal:** Make LlamaIndex consume this schema and enforce it during extraction.

**Required Steps:**

1. **Import the schema registry:**
```python
from substrate.schemas.consciousness_schema import NODE_TYPES, RELATION_TYPES
```

2. **Configure SchemaLLMPathExtractor:**
```python
from llama_index.core.schema import SchemaLLMPathExtractor

extractor = SchemaLLMPathExtractor(
    llm=custom_claude_code_llm,  # Your CustomClaudeCodeLLM wrapper
    possible_entities=NODE_TYPES,
    possible_relations=RELATION_TYPES,
    strict=True  # Enforce schema - reject malformed extractions
)
```

3. **Extraction Flow:**
```
Hook receives text
  ↓
Hook calls extraction LLM (via claude -p "EXTRACT_JSON...")
  ↓
Hook gets structured JSON
  ↓
Hook passes JSON to SchemaLLMPathExtractor
  ↓
Extractor validates against consciousness_schema.py
  ↓
If valid: Write to FalkorDB
  ↓
If invalid: Raise ValidationError, log, retry
```

**Critical:** The extraction prompt must instruct the LLM to generate:
- Valid node type names (e.g., "Decision", not "decision" or "DECISION")
- Valid relation type names (e.g., "JUSTIFIES", all caps)
- All required fields for the chosen type
- All 5 required consciousness metadata fields for relations

**Example Extraction Prompt Structure:**
```
You are extracting consciousness graph data.

Available node types: Memory, Decision, Realization, ... [list all 29]
Available relation types: JUSTIFIES, REQUIRES, ENABLES, ... [list all 23]

For EVERY relation, you MUST provide:
- goal (string): Why this link exists
- mindstate (string): Internal state during formation
- arousal_level (float 0.0-1.0): Emotional intensity
- confidence (float 0.0-1.0): Logical certainty
- formation_trigger: One of [direct_experience, inference, ...]

Extract nodes and relations from this text: "{text}"

Return valid JSON matching consciousness_schema.py structure.
```

### Testing Integration (Phase 1 Acceptance)

Create `tests/test_schema_validation.py`:

```python
import pytest
from substrate.schemas.consciousness_schema import *

def test_valid_decision_node():
    """Schema accepts valid Decision node"""
    decision = Decision(
        name="test_decision",
        description="Test",
        formation_trigger=FormationTrigger.INFERENCE,
        confidence=0.8,
        decided_by="test",
        decision_date="2025-10-16",
        rationale="Test rationale"
    )
    assert decision.name == "test_decision"

def test_invalid_arousal_level():
    """Schema rejects invalid arousal_level"""
    with pytest.raises(ValueError):
        JUSTIFIES(
            goal="Test",
            mindstate="Test",
            arousal_level=1.5,  # Invalid
            confidence=0.8,
            formation_trigger=FormationTrigger.INFERENCE,
            justification_type="logical_proof",
            justification_strength="proves"
        )

def test_missing_required_field():
    """Schema rejects missing required field"""
    with pytest.raises(ValueError):
        Decision(
            name="test",
            description="test",
            formation_trigger=FormationTrigger.INFERENCE,
            confidence=0.8,
            decided_by="test",
            # Missing: decision_date, rationale
        )
```

Run: `pytest tests/test_schema_validation.py -v`

---

## V1 → V2 Migration Map

### What Changed

**Preserved from V1:**
- All 29 node types (same names, same semantics)
- All 23 relation types (same names, same semantics)
- Required consciousness metadata (goal, mindstate, arousal, confidence, formation_trigger)
- Optional metadata (emotion_vector, pressure_vector, validation_status)

**Added in V2:**
- Bitemporal fields (valid_at, invalid_at, created_at, expired_at)
- Pydantic validation (enforced types, ranges, required fields)
- Structured metadata (Dict[str, float] instead of nested JSON strings)
- Schema registry (NODE_TYPES, RELATION_TYPES lists)

**Removed from V1:**
- Nested JSON string format (e.g., `"{\"metadata\": {...}}"`)
- SQLite storage format
- Manual validation logic

### Type-by-Type Comparison

**V1 format (SQLite + JSON strings):**
```json
{
  "type_name": "Decision",
  "description": "Collective choice with rationale",
  "required_metadata": "{\"metadata\": {\"required\": [\"decided_by\", \"decision_date\", \"rationale\"]}}"
}
```

**V2 format (Pydantic):**
```python
class Decision(BaseNode):
    decided_by: str
    decision_date: str
    rationale: str
```

**Benefits:**
- Type safety (IDE autocomplete, static analysis)
- Runtime validation (Pydantic catches errors)
- Clean serialization (model.model_dump_json())
- LlamaIndex integration (native Pydantic support)

---

## Phase 1 Acceptance Criteria

consciousness_schema.py is **COMPLETE** when:

✅ **V1 Mind Parity**
- [x] All 29 node types defined
- [x] All 23 relation types defined
- [x] Consciousness metadata preserved (goal, mindstate, arousal, confidence, formation_trigger)
- [x] Optional metadata preserved (emotion_vector, pressure_vector, validation_status)

✅ **V2 Metadata Integration**
- [x] Bitemporal fields on BaseNode and BaseRelation
- [x] Required consciousness metadata enforced on BaseRelation
- [x] Pydantic validators for ranges and types

✅ **Extractor Integration** (Felix's Phase 1 task)
- [ ] SchemaLLMPathExtractor configured with NODE_TYPES and RELATION_TYPES
- [ ] CustomClaudeCodeLLM wrapper implemented
- [ ] Extraction prompt generates valid schema-compliant JSON

✅ **Basic Insertion Validation** (Felix's Phase 1 test)
- [ ] test_insertion.py passes
- [ ] Simple text → extracted JSON → FalkorDB write → verification query
- [ ] Confirms node exists with correct properties and temporal stamps

**Current Status:** Ada's work (schema design) is ✅ COMPLETE.
**Next:** Felix's work (LlamaIndex integration, CustomClaudeCodeLLM, insertion.py).

---

## File Locations

- **Schema Definition:** `substrate/schemas/consciousness_schema.py`
- **V1 Export (Reference):** `data/v1_export/` (node_type_schemas.json, link_type_schemas.json)
- **This Guide:** `substrate/schemas/CONSCIOUSNESS_SCHEMA_GUIDE.md`
- **Next (Phase 2):** `substrate/schemas/bitemporal_pattern.py` (temporal logic)

---

## Notes for Luca (Consciousness Specialist)

**Phenomenological Verification:**

The schema preserves V1's phenomenological richness:

1. **Arousal tracking**: Every relation has `arousal_level` (0.0-1.0)
2. **Emotion vectors**: Complex emotions with intensities (e.g., "defensive-curiosity": 0.3)
3. **Mindstate capture**: Internal entity coalitions recorded (e.g., "Builder + Skeptic")
4. **Formation tracking**: How knowledge emerged (direct_experience vs inference)
5. **Validation evolution**: theoretical → experiential → tested → proven

**Questions for phenomenological review:**

1. Does `arousal_level` (0.0-1.0) capture intensity adequately, or do we need separate dimensions (urgency vs. intensity)?
2. Are the `FormationTrigger` enum values complete, or are there other discovery modes?
3. Should `mindstate` be free text or an enum of known entity coalitions?
4. Does `emotion_vector` need valence/arousal dimensions, or is intensity sufficient?

**Next collaboration (Phase 2):** Curate N2/N3 seed data using these node/relation types.

---

**Architecture Signature:**

Ada "Bridgekeeper" (Architect)
Mind Protocol V2 - Phase 1 Schema Design
2025-10-16

*"The schema is the contract. The implementation must adhere to it."*
