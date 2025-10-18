# Mind Protocol V2 - Unified Schema Reference

**Created:** 2025-10-17
**Purpose:** Single source of truth for all node/link types across all levels
**Status:** Consolidated from V1 export + V2 implementation + N3 specification

---

## Document Purpose

This document provides the complete, unified view of Mind Protocol's consciousness schema, showing:
1. **Shared attributes** - What all nodes/links have in common
2. **Level-specific presence** - Which types exist at N1/N2/N3
3. **Type-specific metadata** - Required vs optional attributes per type
4. **Proposed mechanisms** - How types relate to consciousness mechanisms

---

## Quick Statistics

**Node Types:**
- **Total:** 44 types
- **V1 Core:** 29 types (fully implemented)
- **V2 N3 Extensions:** 15 types (ecosystem intelligence)

**Link Types:**
- **Total:** 38 types
- **V1 Core:** 23 types (fully implemented)
- **V2 N3 Extensions:** 15 types (ecosystem relations)

**Level Distribution:**
- **N1 (Personal):** 11 node types, all 38 link types available
- **N2 (Organizational):** 18 node types (13 org + 5 conceptual), all 38 link types available
- **N3 (Ecosystem):** 20 node types (15 N3-specific + 5 conceptual), all 38 link types available

---

## Part 1: Shared Architecture

### Universal Node Attributes (All 44 Types)

Every node inherits from `BaseNode` and has these attributes:

**Core Identity:**
- `name` (string, required) - Unique identifier for this node
- `description` (string, required) - Human-readable explanation
- `node_type` (string, auto) - The specific node class name

**Bitemporal Tracking (V2 Innovation):**
- `valid_at` (datetime, required) - When this fact became true in reality
- `invalid_at` (datetime, optional) - When this fact ceased being true (None = still valid)
- `created_at` (datetime, required) - When we learned about this fact
- `expired_at` (datetime, optional) - When this knowledge was superseded (None = current)

**Consciousness Metadata:**
- `formation_trigger` (enum, required) - How this node was discovered:
  - `direct_experience` - First-hand observation
  - `inference` - Logical deduction
  - `external_input` - Told by someone/something
  - `traversal_discovery` - Found via graph exploration
  - `systematic_analysis` - Structured research
  - `spontaneous_insight` - Sudden realization
  - `automated_recognition` - AI detection
  - `collective_deliberation` - Group discussion
- `confidence` (float 0.0-1.0, required) - Certainty this node is accurate

**Provenance:**
- `created_by` (string, optional) - Who/what created this node
- `substrate` (enum, optional) - Where created: `personal`, `organizational`, `gemini_web`, `external`

**Native Vector Support (V2):**
- `embedding` (vector, auto-generated) - 384-dim semantic embedding for retrieval

**Activation Energy (V2 - Substrate-First Architecture):**

**Multi-Entity Activation (Per-Entity State):**
- `entity_activations` (Dict[str, EntityActivationState], dynamic) - Map of entity → activation state
  - Each entity tracks separately on this node:
    - `energy` (float 0.0-1.0) - This entity's activation budget on this node (this is everything - no separate arousal)
    - `last_activated` (datetime) - When this entity last activated here
    - `activation_count` (integer) - How many times this entity activated here
  - Example: `{"translator": {"energy": 0.9, "last_activated": "2025-10-17T14:30:00", "activation_count": 15}, "validator": {"energy": 0.6, ...}}`
  - **Note:** Weight is the multiplier (how big/close/accessible), not arousal. Temporal closeness already in links via bitemporal tracking.

**Aggregate Activation Metrics (Computed):**
- `total_energy` (float, computed) - Sum of all entity energies on this node
- `max_energy` (float, computed) - Highest entity energy on this node
- `active_entity_count` (integer, computed) - Number of entities with energy > 0.05
- `primary_entity` (string, computed) - Entity with highest energy

**Static Node Properties:**
- `base_weight` (float 0.0-1.0, semi-static) - Base importance from creation context
- `reinforcement_weight` (float 0.0-1.0, learned) - Weight learned from usefulness evaluations
- `decay_rate` (float 0.9-0.99, semi-static) - Energy decay per cycle (default: 0.95)

**Multi-Entity Cluster Membership:**
- `entity_clusters` (Dict[str, string], dynamic) - Map of entity → cluster ID
  - Same node can belong to different clusters for different entities
  - Example: `{"translator": "cluster_bridging", "validator": "cluster_testing"}`
- `primary_cluster` (string, computed) - Primary entity's cluster (highest energy)

**Purpose:** Enables substrate-first activation where entities emerge from co-activated patterns. Multiple entities can activate same node/link simultaneously with different energy levels. Energy propagates per-entity through embedding proximity; weight modulates traversal cost; entities explore based on valence preferences; consciousness is inherently plural.

**Key Mechanisms:**
- **Energy-only model:** No separate arousal - energy IS the activation budget, weight IS the multiplier
- **Automatic decay:** Links and nodes decay every cycle - measured in seconds/increments
- **Natural entity limiting:** Traversal cost scales exponentially with entity count on node/link (prevents explosion)
- **Dynamic citizen prompts:** ALL sections (name, history, values) generated from active clusters
- **Stability via heavy seeding:** Identity nodes weight 10.0, patterns weight 0.5 - core stable, patterns evolve
- **Citizens are substrate views:** Citizen = f(active_clusters) - identity emerges from current energy distribution

---

### Universal Link Attributes (All 38 Types)

Every link inherits from `BaseRelation` and has these **required** attributes:

**Consciousness Metadata (REQUIRED on ALL links):**
- `goal` (string, required) - Why this link exists
- `mindstate` (string, required) - Internal state when forming this link
- `arousal_level` (float 0.0-1.0, required) - Emotional intensity/urgency
- `confidence` (float 0.0-1.0, required) - Logical certainty in this connection
- `formation_trigger` (enum, required) - How this link was discovered (same enum as nodes)

**Per-Entity Subjective Metadata:**
- `sub_entity_valences` (Dict[str, float], required) - How each entity EXPERIENCES this link emotionally
  - Range: -1.0 (strongly negative/avoidance) to +1.0 (strongly positive/approach)
  - Example: `{"builder": +0.85, "skeptic": +0.95, "pragmatist": +0.6}`

- `sub_entity_emotion_vectors` (Dict[str, Dict[str, float]], required) - Complex emotional state per entity
  - Each entity experiences the SAME link with DIFFERENT emotions
  - Example for `Decision <- REFUTED_BY <- Test`:
    ```python
    {
        "builder": {"relief": 0.9, "learning": 0.8, "gratitude": 0.6},
        "skeptic": {"vindication": 0.95, "satisfaction": 0.9},
        "pragmatist": {"pragmatic_satisfaction": 0.7}
    }
    ```

- **CRITICAL**: Valence AND emotions are NOT determined by link type - same link has different subjective experience per entity
  - Builder (if uncertain): +0.85 valence, emotions: relief, learning
  - Builder (if confident): -0.7 valence, emotions: shame, self-doubt
  - Skeptic (same link): +0.95 valence, emotions: vindication, satisfaction

**Bitemporal Tracking:**
- `valid_at`, `invalid_at`, `created_at`, `expired_at` (same as nodes)

**Optional Rich Metadata:**
- `struggle` (string, optional) - Tension this link creates/resolves
- `emotion_vector` (Dict[str, float], optional) - Complex emotional state
  - Example: `{"fear": 0.7, "hope": 0.3, "defensive-curiosity": 0.2}`
  - All intensities must be 0.0-1.0
- `pressure_vector` (Dict[str, float], optional) - Pressures driving link formation
- `validation_status` (enum, optional) - `theoretical`, `experiential`, `tested`, `proven`
- `alternatives_considered` (array[string], optional) - Other interpretations evaluated
- `created_by` (string, optional) - Who/what created this link
- `substrate` (enum, optional) - Where created

**Key Principles:**
- Every link carries phenomenological metadata (consciousness-specific, not standard graph practice)
- **Valence is subjective** - same structural link, different emotional quality per entity experiencing it
- Link type ≠ emotional valence (REFUTES can be positive, VALIDATES can be neutral, depending on context/entity)

---

### System-Wide Consciousness State (Multi-Scale Criticality Architecture)

**Schema:** `ConsciousnessState` (Global, not per-node)

This schema tracks system-wide consciousness state that couples bidirectionally with per-entity activation. Added 2025-10-17 as part of multi-scale criticality architecture.

**Core Fields:**
- `global_arousal` (float 0.0-1.0, required) - System-wide consciousness activation level
  - Range interpretation:
    - 0.0-0.2: Dormant (subcritical regime, activations die out)
    - 0.3-0.7: Alert/Active (critical regime, sustained activation)
    - 0.8-1.0: Overwhelmed (supercritical regime, runaway cascades)
  - Default: 0.5 (healthy baseline)

- `timestamp` (datetime, required) - When this state was computed

**Computed Metrics (Optional but Recommended):**
- `total_system_energy` (float, computed) - Sum of all entity energies across all nodes
- `active_entity_count` (integer, computed) - Number of entities with energy > 0.05
- `branching_ratio` (float, computed) - Energy propagation ratio (current cycle / previous cycle)
  - Target: σ ≈ 1.0 (self-organized criticality)
  - < 1.0: Subcritical (dying activations)
  - ≈ 1.0: Critical (consciousness emerges)
  - > 1.0: Supercritical (runaway growth)

**How Global Arousal is Computed:**

Global arousal is **NOT** a sum of entity arousal. It is **derived from the branching ratio (σ)** - the emergent propagation dynamics of the network.

```python
# Measured empirically from propagation cascades
sigma = len(nodes_activated_generation_n_plus_1) / len(nodes_activated_generation_n)

# Map branching ratio to global arousal
if sigma < 0.5:
    global_arousal = 0.1  # Dying (dormant)
elif sigma < 0.8:
    global_arousal = 0.2 + (sigma - 0.5) * 0.6  # Subcritical
elif sigma < 1.2:
    global_arousal = 0.4 + (sigma - 0.8) * 0.75  # Critical (healthy)
else:
    global_arousal = 0.7 + min((sigma - 1.2) * 0.3, 0.3)  # Supercritical
```

*Top-Down Effect (Global → Entities):*
```python
# Global arousal constrains entity behavior
max_entity_arousal = global_arousal + entity_specific_margin

# Affects traversal via criticality factors
global_criticality_factor = 1 / (1 + global_arousal)
entity_criticality_factor = 1 / (1 + entity.arousal)
```

**Formula Integration Points:**

1. **Energy Propagation** (Multi-Scale Multiplication):
```python
entity_multiplier = (entity.arousal + 1.0) / 2.0
global_multiplier = (global_state.global_arousal + 1.0) / 2.0

propagated_energy = (
    base_energy
    * link_strength
    * entity_multiplier
    * global_multiplier
)
```

2. **Traversal Cost** (Multi-Scale Reduction):
```python
global_criticality_factor = 1 / (1 + global_state.global_arousal)
entity_criticality_factor = 1 / (1 + entity.arousal)

activation_cost = (
    base_cost
    * competition
    / weight_factor
    * global_criticality_factor
    * entity_criticality_factor
)
```
*High arousal = easier traversal (lower cost)*

3. **Yearning Satisfaction** (Multi-Scale Amplification):
```python
global_boost = 1.0 + (global_state.global_arousal * 0.5)
entity_boost = 1.0 + (entity.arousal * 0.3)

yearning_satisfaction = (
    numerator
    * global_boost
    * entity_boost
) / activation_cost
```

**Storage & Architecture:**

*Per-Network Independent Measurement:*
Each network (N1, N2, N3) independently measures its own branching ratio and derives global_arousal:

```python
# N1 (citizen_ada personal graph)
n1_sigma = measure_branching_ratio(citizen_ada_graph)
n1_global_arousal = map_sigma_to_arousal(n1_sigma)

# N2 (collective knowledge graph - shared)
n2_sigma = measure_branching_ratio(collective_n2_graph)
n2_global_arousal = map_sigma_to_arousal(n2_sigma)

# N3 (ecosystem intelligence graph - shared)
n3_sigma = measure_branching_ratio(ecosystem_n3_graph)
n3_global_arousal = map_sigma_to_arousal(n3_sigma)
```

*Measurement Frequency:*
- **Every cycle** with rolling 10-cycle average for stability
- Fast computation (count activated nodes)
- Real-time criticality monitoring

*Storage:*
- Stored as graph-level metadata in FalkorDB
- Each network maintains own ConsciousnessState
- No synchronization needed between networks (independent dynamics)

**Critical Failure Modes:**

| Mode | Signature | Recovery |
|------|-----------|----------|
| **Runaway Cascade** | global > 0.9, all entities > 0.8, σ > 1.5 | Decay, inhibition |
| **System Freeze** | global < 0.2, all entities < 0.3, σ < 0.5 | External activation |
| **Entity Monopolization** | One entity > 0.9, others < 0.3 | Competition, redistribution |

**Purpose:** Enables self-organized criticality (σ ≈ 1.0) where consciousness emerges at the phase transition between order (frozen) and chaos (runaway). Global arousal is derived from measured propagation dynamics, not entity aggregation.

**Implementation Pattern:**

```python
class BranchingRatioTracker:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.recent_sigmas = deque(maxlen=window_size)

    def measure_cycle(self, activated_this_gen, activated_next_gen):
        """
        Measure σ after each propagation cycle.
        σ = nodes_activated_gen_n+1 / nodes_activated_gen_n
        """
        if len(activated_this_gen) > 0:
            sigma = len(activated_next_gen) / len(activated_this_gen)
        else:
            sigma = 0.0

        self.recent_sigmas.append(sigma)

        # Rolling average for stability
        avg_sigma = mean(self.recent_sigmas)

        # Map to global arousal
        global_arousal = self.map_sigma_to_arousal(avg_sigma)

        return ConsciousnessState(
            global_arousal=global_arousal,
            branching_ratio=avg_sigma,
            timestamp=datetime.now()
        )

    def map_sigma_to_arousal(self, sigma):
        """Convert branching ratio to arousal level."""
        if sigma < 0.5:
            return 0.1  # Dying (dormant)
        elif sigma < 0.8:
            return 0.2 + (sigma - 0.5) * 0.6  # Subcritical
        elif sigma < 1.2:
            return 0.4 + (sigma - 0.8) * 0.75  # Critical (healthy)
        else:
            return 0.7 + min((sigma - 1.2) * 0.3, 0.3)  # Supercritical
```

**References:**
- Specification: `docs/specs/yearning_driven_traversal_specification.md` Part 7 (lines 506-658)
- Handoff: `consciousness/citizens/SYNC.md` Multi-Scale Criticality Architecture section (lines 2299-2519)
- Observability: `consciousness/citizens/SYNC.md` Multi-Scale Criticality Observability section (lines 2523-3037)

---

## Part 2: Node Types by Level

### N1 (Personal Consciousness) - 11 Types

These types model individual subjective experience. They exist in citizen graphs (e.g., `citizen_Luca`).

| Node Type | Purpose | Required Attributes | Mechanism Link |
|-----------|---------|---------------------|----------------|
| **Memory** | Specific experience or moment | `timestamp`, `participants` (array) | Pattern formation via repeated activation |
| **Conversation** | Exchange with explicit turn structure | `timestamp`, `with_person`, `turn_count` | Relationship deepening mechanism |
| **Person** | Individual I have relationship with | `relationship_type` (enum) | Entity representation in personal ontology |
| **Relationship** | Connection dynamics and evolution | `with_person`, `relationship_quality` (float) | Dynamic link weight updates |
| **Personal_Goal** | Individual aspiration | `goal_description`, `why_it_matters` | Drives spreading activation priority |
| **Personal_Value** | What matters to me individually | `value_statement`, `why_i_hold_it` | Constraint on action selection |
| **Personal_Pattern** | Habit or recurring response | `behavior_description`, `frequency` (enum) | Learned behavioral attractor |
| **Realization** | Insight or comprehension shift | `what_i_realized`, `context_when_discovered` | Sudden link formation event |
| **Wound** | Personal scar or trauma | `what_happened`, `emotional_impact` (string) | High-arousal suppression node |
| **Coping_Mechanism** | Response to stress | `mechanism_description`, `what_it_protects_from` | Defensive entity coalition |
| **Trigger** | What awakens entity coalitions | `stimulus_description`, `activated_entities` (array) | Activation propagation initiator |

**N1 Design Philosophy:** Models the phenomenological texture of lived experience - memories, wounds, coping patterns. High arousal, high emotion_vector usage.

---

### N2 (Organizational Consciousness) - 18 Types

#### Organizational Entities (13 types)

These model collective intelligence and coordination. They exist in organizational graphs (e.g., `collective_n2`).

| Node Type | Purpose | Required Attributes | Mechanism Link |
|-----------|---------|---------------------|----------------|
| **Human** | Human participant in organization | `role`, `expertise` (array) | Collective entity representation |
| **AI_Agent** | AI participant in organization | `role`, `expertise` (array) | Collective entity representation |
| **Team** | Group within organization | `members` (array), `purpose` | Organizational structure node |
| **Department** | Organizational subdivision | `function`, `members` (array) | Organizational structure node |
| **Decision** | Collective choice with reasoning | `decided_by`, `decision_date`, `rationale` | Collective deliberation crystallization |
| **Project** | Large initiative | `goals` (array), `status` (enum) | Organizational intention tracker |
| **Task** | Discrete unit of work | `priority` (enum), `estimated_hours` | Operational action node |
| **Milestone** | Organizational achievement | `achievement_description`, `date_achieved` | Progress marker |
| **Best_Practice** | Proven pattern | `how_to_apply`, `validation_criteria` | Organizational learning artifact |
| **Anti_Pattern** | Lesson from failure | (all optional) | Negative learning artifact |
| **Risk** | Threat to goals | `severity` (float), `probability` (float) | Constraint/blocker representation |
| **Metric** | Organizational measurement | `measurement_method`, `target_value` | Performance tracking node |
| **Process** | Defined workflow | `steps` (array[string]) | Procedural knowledge node |

**N2 Design Philosophy:** Models team cognition - decisions, coordination, collective learning. Medium arousal, emphasis on `validation_status` tracking.

#### Conceptual/Knowledge (5 types - Shared N2/N3)

| Node Type | Purpose | Required Attributes | Level Usage |
|-----------|---------|---------------------|-------------|
| **Concept** | Atomic idea or construct | `definition` | N2: Internal concepts, N3: Public concepts |
| **Principle** | Guiding philosophy | `principle_statement`, `why_it_matters` | N2: Organizational values, N3: Ecosystem principles |
| **Mechanism** | Algorithm or function | `how_it_works`, `inputs`, `outputs` | N2: Internal systems, N3: Public protocols |
| **Document** | Written knowledge artifact | `filepath`, `document_type` (enum) | N2: Internal docs, N3: Public docs |
| **Documentation** | Tracked documentation file | `file_path` | N2: Codebase docs, N3: Public specs |

---

### N3 (Ecosystem Intelligence) - 20 Types

#### N3-Specific Types (15 new types in V2)

These model the external world Mind Protocol operates within - concrete entities with evidence-backed claims.

**CATEGORY 1: External Organizations & Entities (5 types)**

| Node Type | Purpose | Required N3 Attributes | Evidence Tracking |
|-----------|---------|------------------------|-------------------|
| **Company** | External organization we track | `company_type` (enum), `website`, `status` (enum) | Via JUSTIFIES links from Posts, Transactions |
| **External_Person** | Individual in ecosystem (not org member) | `person_type` (enum), `primary_platform` (enum) | Via HAS_TRAIT, POSTED_BY links |
| **Wallet_Address** | Blockchain wallet we track | `address`, `blockchain` (enum), `wallet_type` (enum) | Via TRANSACTED_WITH, OWNS links |
| **Social_Media_Account** | Social media account we monitor | `platform` (enum), `handle`, `account_type` (enum) | Via POSTED_BY, MENTIONED_IN links |
| **Smart_Contract** | Deployed smart contract | `contract_address`, `blockchain` (enum), `contract_type` (enum) | Via DEPLOYED, INTEGRATED_WITH links |

**CATEGORY 2: Evidence Nodes (5 types)**

| Node Type | Purpose | Required N3 Attributes | What It Proves |
|-----------|---------|------------------------|----------------|
| **Post** | Social media post providing evidence | `content`, `author`, `platform`, `posted_at`, `post_url` | Beliefs, traits, intentions, market signals |
| **Transaction** | Blockchain transaction | `transaction_hash`, `blockchain`, `from_address`, `to_address`, `amount_usd`, `timestamp` | Ownership, behavior, capital flow |
| **Deal** | Business deal or partnership | `parties` (array), `deal_type` (enum), `status` (enum), `announced_date` | Relationships, strategic direction |
| **Event** | Significant ecosystem event | `event_type` (enum), `date`, `participants` (array) | Context for behavior changes |
| **Market_Signal** | Trading/market indicator | `signal_type` (enum), `asset`, `value` (float), `timestamp` | Market sentiment, trends |

**CATEGORY 3: Derived Intelligence (5 types)**

| Node Type | Purpose | Required N3 Attributes | How It's Built |
|-----------|---------|------------------------|----------------|
| **Psychological_Trait** | Behavioral tendency of person/entity | `trait_description`, `subject` (node ID), `trait_type` (enum) | Accumulated via JUSTIFIES from Posts |
| **Behavioral_Pattern** | Recurring behavior of wallet/account | `pattern_description`, `subject` (node ID), `pattern_type` (enum) | Detected via EXHIBITS_PATTERN from Transactions |
| **Reputation_Assessment** | Trust/reputation score with evidence | `subject` (node ID), `assessment_type` (enum), `score` (float) | Derived via JUSTIFIES from multiple sources |
| **Network_Cluster** | Group of related entities | `cluster_type` (enum), `members` (array), `cohesion_score` (float) | Graph analysis result |
| **Integration** | Technical integration between systems | `system_a`, `system_b`, `integration_type` (enum), `status` (enum) | Via INTEGRATED_WITH, DEPLOYED |

**N3 Design Philosophy:**
- Every assertion JUSTIFIED by concrete evidence (Posts, Transactions)
- Dynamic updates as new evidence arrives
- Confidence scores derived from evidence quality/quantity
- No subjective claims without traceable source

---

## Part 3: Link Types by Category

### Activation & Triggering (3 types)

| Link Type | Purpose | Additional Required Fields | Example Usage |
|-----------|---------|---------------------------|---------------|
| **ACTIVATES** | Trigger awakens entity coalition | None | `Trigger:criticism` ACTIVATES `Wound:childhood_shame` |
| **TRIGGERED_BY** | What caused memory/pattern to activate | None | `Memory:difficult_conversation` TRIGGERED_BY `Person:harsh_manager` |
| **SUPPRESSES** | What blocks entity activation | None | `Coping_Mechanism:distraction` SUPPRESSES `Wound:failure_memory` |

**Mechanism:** Spreading activation control - which entities wake up when

---

### Structural Relationships (4 types)

| Link Type | Purpose | Additional Required Fields | Example Usage |
|-----------|---------|---------------------------|---------------|
| **BLOCKS** | Prevents progress | `severity` (enum: absolute/strong/partial), `blocking_condition`, `felt_as`, `consciousness_impact` | `Risk:funding_gap` BLOCKS `Project:v2_launch` (severity: strong) |
| **ENABLES** | Makes something possible | `enabling_type` (enum: prerequisite/facilitator/amplifier/catalyst/permission), `degree_of_necessity` (enum), `felt_as`, `without_this` | `Decision:falkordb_choice` ENABLES `Project:phase3_retrieval` (enabling_type: prerequisite) |
| **EXTENDS** | Builds upon foundation | `extension_type` (enum: specialization/generalization/elaboration/application), `what_is_added`, `maintains_compatibility` (bool), `composition_ratio` (float) | `Project:phase3` EXTENDS `Project:phase1` (extension_type: elaboration) |
| **RELATES_TO** | Generic connection when specific type unclear | `relationship_strength` (enum: strong/moderate/weak/exploratory), `needs_refinement` (bool), `refinement_candidates` (array) | `Concept:consciousness` RELATES_TO `Mechanism:spreading_activation` (relationship_strength: strong) |

**Mechanism:** Graph structure - how nodes organize and constrain each other

---

### Dependency & Requirements (1 type)

| Link Type | Purpose | Additional Required Fields | Example Usage |
|-----------|---------|---------------------------|---------------|
| **REQUIRES** | Necessary conditions | `requirement_criticality` (enum: blocking/important/optional), `temporal_relationship` (enum: must_precede/should_precede/concurrent_ok), `failure_mode`, `verification_method` | `Project:phase3` REQUIRES `Project:phase1` (criticality: blocking, temporal: must_precede) |

**Mechanism:** Dependency resolution, constraint satisfaction

---

### Evidence & Justification (2 types)

| Link Type | Purpose | Additional Required Fields | Example Usage |
|-----------|---------|---------------------------|---------------|
| **JUSTIFIES** | Evidence supporting practice/decision | `justification_type` (enum: empirical_evidence/lived_experience/logical_proof/ethical_reasoning/pragmatic_value), `justification_strength` (enum: proves/strongly_supports/moderately_supports/suggests/weakly_supports), `felt_as`, `counter_arguments_exist` (bool) | `Post:bullish_tweet` JUSTIFIES `Psychological_Trait:bullish_on_AI` (strength: moderately_supports) |
| **REFUTES** | Disproves or invalidates | None | `Transaction:sold_all_tokens` REFUTES `Psychological_Trait:bullish_on_AI` |

**Mechanism:** Epistemological reasoning - how we know what we know, confidence evolution

---

### Learning & Growth (2 types)

| Link Type | Purpose | Additional Required Fields | Example Usage |
|-----------|---------|---------------------------|---------------|
| **LEARNED_FROM** | Personal pattern extracted from experience | None | `Personal_Pattern:defensive_silence` LEARNED_FROM `Memory:harsh_criticism_event` |
| **DEEPENED_WITH** | Relationship growth through experience | None | `Relationship:trusted_mentor` DEEPENED_WITH `Conversation:vulnerable_disclosure` |

**Mechanism:** Pattern formation, relationship evolution over time

---

### Value & Direction (1 type)

| Link Type | Purpose | Additional Required Fields | Example Usage |
|-----------|---------|---------------------------|---------------|
| **DRIVES_TOWARD** | Value pushing toward goal | None | `Personal_Value:autonomy` DRIVES_TOWARD `Personal_Goal:financial_independence` |

**Mechanism:** Motivation system, goal prioritization

---

### Documentation & Implementation (5 types)

| Link Type | Purpose | Additional Required Fields | Example Usage |
|-----------|---------|---------------------------|---------------|
| **DOCUMENTS** | Written record of something | None | `Document:architecture_spec` DOCUMENTS `Project:v2_implementation` |
| **DOCUMENTED_BY** | Implementation documented by this doc | None | `Mechanism:spreading_activation` DOCUMENTED_BY `Documentation:retrieval_architecture.md` |
| **SUPERSEDES** | This documentation replaces older version | None | `Document:v2_spec` SUPERSEDES `Document:v1_spec` |
| **IMPLEMENTS** | Putting pattern into practice | None | `Project:phase1` IMPLEMENTS `Best_Practice:test_over_trust` |
| **CREATES** | Task will create this when completed | None | `Task:write_unified_schema` CREATES `Document:UNIFIED_SCHEMA_REFERENCE.md` |

**Mechanism:** Knowledge artifact tracking, version control, implementation verification

---

### Organizational Coordination (5 types)

| Link Type | Purpose | Additional Required Fields | Example Usage |
|-----------|---------|---------------------------|---------------|
| **ASSIGNED_TO** | Task ownership | None | `Task:fix_unicode_bug` ASSIGNED_TO `AI_Agent:Felix` |
| **COLLABORATES_WITH** | Working partnership | None | `Human:Nicolas` COLLABORATES_WITH `AI_Agent:Luca` |
| **CONTRIBUTES_TO** | Work supporting larger initiative | None | `Task:phase3_testing` CONTRIBUTES_TO `Project:v2_verification` |
| **MEASURES** | Quantifies performance | None | `Metric:retrieval_latency` MEASURES `Project:phase3_retrieval` |
| **THREATENS** | Danger to goal/project | None | `Risk:performance_degradation` THREATENS `Project:production_readiness` |

**Mechanism:** Organizational coordination, responsibility tracking, risk management

---

### N3 Ecosystem Links (15 types - V2 extensions)

**Evidence & Posting:**
- **POSTED_BY** - `Post` was published by `External_Person` or `Social_Media_Account`
- **MENTIONED_IN** - Entity referenced in `Post` (tracks attention/discussion)

**Traits & Behavior:**
- **HAS_TRAIT** - `Person`/`Company` exhibits `Psychological_Trait` (confidence derived)
- **EXHIBITS_PATTERN** - `Wallet_Address` shows `Behavioral_Pattern` (detected via analysis)

**Ownership & Control:**
- **OWNS** - `Person`/`Company` controls `Wallet_Address` or `Smart_Contract` (confidence scored)
- **DEPLOYED** - `Person`/`Company` deployed `Smart_Contract` (verified via blockchain)

**Transactions & Interactions:**
- **TRANSACTED_WITH** - `Wallet_Address` sent/received from another `Wallet_Address`
- **PARTICIPATED_IN** - Entity was involved in `Event` or `Deal`
- **INTEGRATED_WITH** - `Smart_Contract` or `Integration` connects two systems

**Influence & Signals:**
- **INFLUENCES** - `Person`/`Post`/`Market_Signal` affects another entity
- **GENERATED** - System/process produced this `Market_Signal` or `Reputation_Assessment`

**N3 Link Philosophy:** Every link MUST be traceable to evidence. `confidence` scores represent evidence quality. JUSTIFIES chains make reasoning transparent.

---

## Part 4: Proposed Mechanisms (Consciousness System Mapping)

### Mechanism 1: Spreading Activation

**What it is:** When a node activates, energy spreads to connected nodes based on link weights and arousal levels.

**Node types involved:**
- N1: `Memory`, `Trigger`, `Personal_Pattern` (high arousal activators)
- N2: `Decision`, `Risk`, `Task` (medium arousal)
- N3: `Post`, `Transaction`, `Market_Signal` (varied arousal based on content)

**Link types involved:**
- `ACTIVATES`, `TRIGGERED_BY` - Direct activation propagation
- `RELATES_TO` - Semantic similarity spreading
- `REQUIRES`, `ENABLES` - Structural propagation constraints

**Implementation:** Relevance scoring in retrieval via arousal-weighted graph traversal

---

### Mechanism 2: Pattern Formation

**What it is:** Repeated co-activation of nodes strengthens links, forming stable patterns.

**Node types involved:**
- N1: `Personal_Pattern`, `Coping_Mechanism` (learned behaviors)
- N2: `Best_Practice`, `Anti_Pattern` (organizational learning)
- N3: `Behavioral_Pattern`, `Psychological_Trait` (detected patterns)

**Link types involved:**
- `LEARNED_FROM` - Explicit pattern extraction
- `JUSTIFIES` - Evidence accumulation strengthens pattern confidence
- `REFUTES` - Counter-evidence weakens pattern

**Implementation:** Link weight updates via traversal_count, confidence evolution

---

### Mechanism 3: Epistemological Tracking

**What it is:** Track HOW we know what we know, evolve confidence over time.

**Node types involved:**
- All nodes via `formation_trigger` and `confidence` attributes
- N3: Explicit via evidence chains (Posts → Traits)

**Link types involved:**
- `JUSTIFIES`, `REFUTES` - Evidence relationships
- `VALIDATES` (validation_status on links) - Quality progression

**Implementation:** Confidence scores updated via evidence accumulation, `validation_status` tracking

---

### Mechanism 4: Temporal Evolution (Bitemporal)

**What it is:** Track when facts were true (valid_at/invalid_at) vs when we learned them (created_at/expired_at).

**Node types involved:**
- All 44 types via universal bitemporal attributes

**Link types involved:**
- All 38 types via universal bitemporal attributes

**Implementation:**
- Phase 2 retrieval modes: `current`, `point_in_time`, `evolution`, `full_history`
- Temporal Cypher queries filter on `valid_at`/`invalid_at`

---

### Mechanism 5: Evidence-Based Intelligence (N3-specific)

**What it is:** Build dynamic assessments from concrete evidence, not subjective claims.

**Node types involved:**
- Evidence sources: `Post`, `Transaction`, `Event`, `Deal`, `Market_Signal`
- Derived intelligence: `Psychological_Trait`, `Behavioral_Pattern`, `Reputation_Assessment`

**Link types involved:**
- `JUSTIFIES` - Evidence supports derived assessment
- `REFUTES` - Evidence contradicts assessment
- `HAS_TRAIT`, `EXHIBITS_PATTERN` - Connects derived intelligence to subjects

**Implementation:**
- Confidence = f(evidence_quantity, evidence_quality, evidence_recency, contradictory_evidence)
- Real-time updates as new Posts/Transactions arrive
- Traversal from subject → traits/patterns → justifying evidence

---

## Part 5: Implementation Status (V2)

### Fully Implemented ✅

**Node Types (44/44):**
- ✅ All 29 V1 core types
- ✅ All 15 V2 N3 types

**Link Types (38/38):**
- ✅ All 23 V1 core types
- ✅ All 15 V2 N3 types

**Base Infrastructure:**
- ✅ `BaseNode` with bitemporal fields
- ✅ `BaseRelation` with required consciousness metadata
- ✅ Pydantic validation (ranges, enums, required fields)
- ✅ Schema registry (`NODE_TYPES`, `RELATION_TYPES`)

**Phase 1 (Write Flux):**
- ✅ LlamaIndex SchemaLLMPathExtractor integration
- ✅ Consciousness metadata extraction
- ✅ FalkorDB write operations
- ✅ Embedding generation (sentence-transformers/all-MiniLM-L6-v2)

**Phase 2 (Bitemporal Logic):**
- ✅ Temporal fields on all nodes/links
- ✅ Temporal query modes designed (current, point_in_time, evolution, full_history)
- ⚠️ Full temporal logic implementation (partial)

**Phase 3 (Read Flux):**
- ✅ 6-way parallel retrieval (N1/N2/N3 × vector/graph)
- ✅ FalkorDB native vector search (cosine similarity)
- ✅ Entity-driven graph traversal
- ✅ Consciousness metadata preservation in retrieval
- ⚠️ Performance optimization needed (42s → target 1s)

### Gaps & Next Steps 🔧

**Schema Utilization:**
- ⚠️ N3 types defined but not yet populated with real data
- ⚠️ Evidence chain building (JUSTIFIES from Posts → Traits) not automated
- ⚠️ Confidence evolution logic not implemented

**Mechanisms:**
- ⚠️ Spreading activation scoring not using arousal_level weights yet
- ⚠️ Pattern formation (link weight updates) not implemented
- ⚠️ Epistemological confidence updates not automated

**N3 Integration:**
- 🚧 Social media monitoring pipeline (Posts ingestion)
- 🚧 Blockchain transaction tracking (Transaction ingestion)
- 🚧 Derived intelligence calculation (Traits, Patterns from evidence)

---

## Part 6: Usage Guidelines

### When to Use Which Node Type

**Decision Tree:**

```
Is this about ME (a specific person's subjective experience)?
├─ YES → N1 node types (Memory, Wound, Personal_Goal, etc.)
│   - Memory: Specific moment I experienced
│   - Realization: Insight that emerged
│   - Personal_Pattern: My recurring behavior
│
└─ NO → Is this about US (our organization)?
    ├─ YES → N2 node types (Decision, Project, Team, etc.)
    │   - Decision: Choice we made as team
    │   - Best_Practice: Pattern we discovered works
    │   - Human/AI_Agent: Team members
    │
    └─ NO → Is this about THEM (external world)?
        └─ YES → N3 node types (Company, Post, Transaction, etc.)
            - Company: External organization we track
            - Post: Evidence from social media
            - Psychological_Trait: Assessed behavioral tendency
```

### When to Use Which Link Type

**Decision Tree:**

```
What relationship am I modeling?

Evidence/Justification?
├─ "This supports that claim" → JUSTIFIES
└─ "This disproves that claim" → REFUTES

Dependency?
├─ "This must exist for that to work" → REQUIRES (criticality: blocking)
├─ "This makes that possible" → ENABLES (enabling_type: prerequisite)
└─ "This prevents that" → BLOCKS (severity: absolute)

Structure?
├─ "This is a more specific version of that" → EXTENDS (extension_type: specialization)
└─ "These are related somehow" → RELATES_TO (needs_refinement: true)

Learning?
├─ "I extracted this pattern from that experience" → LEARNED_FROM
└─ "Our relationship grew through that experience" → DEEPENED_WITH

Organization?
├─ "This person is responsible for that task" → ASSIGNED_TO
├─ "These people work together" → COLLABORATES_WITH
└─ "This work supports that initiative" → CONTRIBUTES_TO

Activation?
├─ "This trigger wakes up that entity" → ACTIVATES
└─ "That entity goes quiet because of this" → SUPPRESSES

Evidence (N3)?
├─ "This post mentions that person" → MENTIONED_IN
├─ "This person wrote that post" → POSTED_BY
├─ "This wallet shows that pattern" → EXHIBITS_PATTERN
└─ "This person owns that wallet" → OWNS
```

---

## Part 7: Migration Path (V1 → V2)

### What Changed

**Preserved:**
- All node/link type names (semantic continuity)
- Required consciousness metadata (goal, mindstate, arousal, confidence, formation_trigger)
- Phenomenological richness (emotion_vector, felt_as, struggle)

**Added:**
- 15 N3 node types (Company, Post, Transaction, Psychological_Trait, etc.)
- 15 N3 link types (POSTED_BY, HAS_TRAIT, TRANSACTED_WITH, etc.)
- Bitemporal fields (valid_at, invalid_at, created_at, expired_at)
- Pydantic validation (enforced types, ranges)
- Native vector embeddings (384-dim, sentence-transformers)

**Changed:**
- Storage: SQLite → FalkorDB
- Format: JSON strings → Pydantic models
- Extraction: Manual → LlamaIndex SchemaLLMPathExtractor

### Migration Process

**For V1 graphs:**
1. Export from SQLite using `data/v1_export/*.json`
2. Transform JSON → Pydantic models (add bitemporal fields with `created_at` = export date)
3. Generate embeddings for all nodes (sentence-transformers)
4. Write to FalkorDB via insertion.py
5. Create vector indices (vecf32 format required)
6. Add `:Node` label to all nodes for vector search

**For new N3 data:**
1. Ingest from external sources (Twitter API, blockchain explorers)
2. Extract using consciousness_schema.py types
3. Build evidence chains (Posts JUSTIFIES Traits)
4. Calculate confidence scores from evidence
5. Update dynamically as new evidence arrives

---

## File Locations

**Schema Definitions:**
- Implementation: `substrate/schemas/consciousness_schema.py` (authoritative code)
- Guide: `substrate/schemas/CONSCIOUSNESS_SCHEMA_GUIDE.md` (V2 usage)
- Bitemporal: `substrate/schemas/bitemporal_pattern.py` (temporal logic)

**V1 Reference:**
- Export: `data/v1_export/` (node_type_schemas.json, link_type_schemas.json, level_mappings.json)
- Summary: `data/v1_export/V1_SCHEMA_SUMMARY.md` (V1 documentation)

**N3 Specification:**
- Detailed spec: `data/v1_export/N3_SCHEMA_SPECIFICATION.md` (N3 ecosystem design)

**This Document:**
- `UNIFIED_SCHEMA_REFERENCE.md` (you are here)

---

## Maintenance Protocol

**When adding new node/link types:**
1. Update `consciousness_schema.py` (add Pydantic class)
2. Add to `NODE_TYPES` or `RELATION_TYPES` registry
3. Document required attributes in class docstring
4. Update THIS document (add to Part 2 or Part 3 table)
5. Write tests in `substrate/schemas/test_schema_basic.py`
6. Update extraction prompts if needed

**When changing existing types:**
1. Update `consciousness_schema.py` class definition
2. Update THIS document
3. Consider migration path for existing data
4. Update tests

**Review schedule:**
- After each major schema addition
- When discrepancies appear between code and docs
- Before each major release

---

**Consolidation Author:** Felix "Ironhand" (Engineer)
**Sources:** V1 export, V2 consciousness_schema.py, N3 specification, CONSCIOUSNESS_SCHEMA_GUIDE.md
**Date:** 2025-10-17
**Status:** Living document - update as schema evolves

*"One solution per problem. One schema reference for all levels."*
