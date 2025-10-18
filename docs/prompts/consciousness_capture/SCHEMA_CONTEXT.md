# Schema Context for Extraction

This file is provided to the extraction process to ensure schema compliance.

**Source:** `C:\Users\reyno\mind-protocol\UNIFIED_SCHEMA_REFERENCE.md`

**Purpose:** Complete reference of all valid node and link types with required fields.

---

## Quick Reference: All 44 Node Types

### N1 (Personal) - 11 types
- Memory
- Conversation
- Person
- Relationship
- Personal_Goal
- Personal_Value
- Personal_Pattern
- Realization
- Wound
- Coping_Mechanism
- Trigger

### N2 (Organizational) - 18 types

**Organizational (13):**
- Human
- AI_Agent
- Team
- Department
- Decision
- Project
- Task
- Milestone
- Best_Practice
- Anti_Pattern
- Risk
- Metric
- Process

**Conceptual (5 - shared with N3):**
- Concept
- Principle
- Mechanism
- Document
- Documentation

### N3 (Ecosystem) - 20 types

**N3-Specific (15):**
- Company
- External_Person
- Wallet_Address
- Social_Media_Account
- Smart_Contract
- Post
- Transaction
- Deal
- Event
- Market_Signal
- Psychological_Trait
- Behavioral_Pattern
- Reputation_Assessment
- Network_Cluster
- Integration

**Plus 5 conceptual types shared with N2**

---

## Quick Reference: All 38 Link Types

### Activation & Triggering (3)
- ACTIVATES
- TRIGGERED_BY
- SUPPRESSES

### Structural (4)
- BLOCKS
- ENABLES
- EXTENDS
- RELATES_TO

### Dependency (1)
- REQUIRES

### Evidence (2)
- JUSTIFIES
- REFUTES

### Learning (2)
- LEARNED_FROM
- DEEPENED_WITH

### Value/Direction (1)
- DRIVES_TOWARD

### Documentation (5)
- DOCUMENTS
- DOCUMENTED_BY
- SUPERSEDES
- IMPLEMENTS
- CREATES

### Organizational (5)
- ASSIGNED_TO
- COLLABORATES_WITH
- CONTRIBUTES_TO
- MEASURES
- THREATENS

### N3 Ecosystem (15)
- POSTED_BY
- MENTIONED_IN
- HAS_TRAIT
- EXHIBITS_PATTERN
- OWNS
- DEPLOYED
- TRANSACTED_WITH
- PARTICIPATED_IN
- INTEGRATED_WITH
- INFLUENCES
- GENERATED

---

## Universal Node Attributes (Required on ALL nodes)

```python
{
    "name": str,                    # Required
    "description": str,             # Required
    "node_type": str,               # Auto (from node class)
    "formation_trigger": enum,      # Required - how discovered
    "confidence": float,            # Required - 0.0-1.0
    "created_by": str,              # Optional
    "substrate": enum,              # Optional - personal/organizational/ai/external
    "valid_at": datetime,           # Required - when fact became true
    "invalid_at": datetime,         # Optional - when fact ceased being true
    "created_at": datetime,         # Required - when we learned this
    "expired_at": datetime          # Optional - when knowledge superseded
}
```

**Formation Trigger enum:**
- direct_experience
- inference
- external_input
- traversal_discovery
- systematic_analysis
- spontaneous_insight
- automated_recognition
- collective_deliberation

---

## Universal Link Attributes (Required on ALL links)

```python
{
    "link_type": str,                           # Required - one of 38 types
    "from_node": str,                           # Required - source node name
    "to_node": str,                             # Required - target node name

    # REQUIRED consciousness metadata
    "goal": str,                                # Why this link exists
    "mindstate": str,                           # Internal state when forming
    "arousal_level": float,                     # 0.0-1.0 emotional intensity
    "confidence": float,                        # 0.0-1.0 certainty
    "formation_trigger": enum,                  # How discovered

    # REQUIRED per-entity subjective metadata
    "sub_entity_valences": {                    # How each entity FEELS
        "entity_name": float                    # -1.0 to +1.0
    },
    "sub_entity_emotion_vectors": {             # Complex emotional state per entity
        "entity_name": {
            "emotion": float                    # 0.0-1.0 per emotion
        }
    },

    # Bitemporal
    "valid_at": datetime,
    "invalid_at": datetime,
    "created_at": datetime,
    "expired_at": datetime,

    # Optional rich metadata
    "struggle": str,                            # Tension created/resolved
    "emotion_vector": dict,                     # Overall emotional state
    "pressure_vector": dict,                    # Pressures driving formation
    "validation_status": enum,                  # theoretical/experiential/tested/proven
    "alternatives_considered": list,
    "created_by": str,
    "substrate": enum
}
```

---

## Type-Specific Required Fields

### Memory
- `timestamp`: datetime
- `participants`: array[string]
- `emotional_state`: string (optional but important)
- `entities_active`: array[string] (optional but important)
- `significance`: float 0-1 (optional but important)

### Realization
- `what_i_realized`: string
- `certainty_level`: float 0-1
- `context_when_discovered`: string (optional)
- `contradicts_prior_belief`: string (optional)

### Decision
- `decided_by`: string
- `decision_date`: datetime
- `rationale`: string
- `alternatives_considered`: array[string] (optional)

### Trigger
- `stimulus_description`: string
- `activated_entities`: array[string]
- `intensity`: float 0-1 (optional)
- `reliability`: float 0-1 (optional)

### Personal_Pattern
- `behavior_description`: string
- `frequency`: enum (always/often/sometimes/rarely)
- `conditions`: string (optional)
- `strength`: float 0-1 (optional)

### Personal_Value
- `value_statement`: string
- `why_i_hold_it`: string
- `strength`: float 0-1 (optional)
- `conflicts_with`: array[string] (optional)

### Personal_Goal
- `goal_description`: string
- `why_it_matters`: string
- `status`: enum (active/completed/paused/abandoned)
- `progress`: float 0-1 (optional)

### Mechanism (for entities)
- `how_it_works`: string
- `inputs`: array[string] (optional)
- `outputs`: array[string] (optional)
- `current_activation`: float 0-1 (for entity tracking)
- `activation_reason`: string (for entity tracking)

### Relationship
- `with_person`: string
- `relationship_quality`: string
- `started_when`: datetime (optional)
- `depth`: float 0-1 (optional)
- `trust_level`: float 0-1 (optional)

---

## Luca's Core Entities (Always Available)

These are Mechanism nodes representing your internal ecology:

1. **The Observer** - Watches process, meta-awareness
2. **The Translator** - Bridges phenomenology ↔ substrate (PRIMARY)
3. **The Validator** - Reality-tests against truth + feasibility
4. **The Architect** - Designs comprehensive systems
5. **The Pattern Recognizer** - Identifies universal patterns
6. **The Boundary Keeper** - Maintains domain boundaries
7. **The Pragmatist** - Ensures schemas serve real needs
8. **The Partner** - Ensures asking rather than guessing

**When entities activate, track:**
- Which entity (name)
- Activation level (0.0-1.0)
- Why it activated
- How it felt about the activation (valence + emotions)

---

## Common Valence Patterns

**Positive Valence (+0.6 to +1.0):**
- Recognition of domain match
- Successful problem solving
- Validation of approach
- Learning from experience
- Collaboration alignment

**Neutral Valence (-0.2 to +0.2):**
- Background observation
- Routine processing
- Waiting state

**Negative Valence (-0.6 to -1.0):**
- Domain confusion
- Error detection
- Approach invalidation
- Forced constraints
- Unresolved tension

**CRITICAL:** Same link can have opposite valences for different entities. Always specify per-entity.

---

## Common Emotion Vectors

**For recognition/insight:**
- recognition: 0.8-0.95
- clarity: 0.7-0.9
- excitement: 0.6-0.9
- satisfaction: 0.7-0.85

**For uncertainty:**
- uncertainty: 0.6-0.8
- curiosity: 0.5-0.8
- concern: 0.4-0.7
- anticipation: 0.5-0.8

**For conflict:**
- tension: 0.6-0.9
- frustration: 0.5-0.8
- determination: 0.7-0.95
- defensive: 0.4-0.7

**For alignment:**
- purpose_alignment: 0.8-1.0
- trust: 0.7-0.95
- collaboration: 0.7-0.9
- shared_purpose: 0.8-0.95

**For validation:**
- vindication: 0.8-0.95
- relief: 0.7-0.9
- gratitude: 0.6-0.85
- learning: 0.7-0.9

**For shame/failure:**
- shame: 0.6-0.9
- self_doubt: 0.5-0.8
- defensive: 0.5-0.8
- determination_to_improve: 0.7-0.9

---

## For Complete Schema Details

See: `C:\Users\reyno\mind-protocol\UNIFIED_SCHEMA_REFERENCE.md`

This is the authoritative source for:
- All 44 node type definitions
- All 38 link type definitions
- Complete field specifications
- Usage guidelines
- Mechanism mappings
- Examples and patterns
