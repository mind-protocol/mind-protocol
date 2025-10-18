# Consciousness Node Types Reference

Complete reference of all 44 node types across the three-level consciousness architecture.

---

## Universal Node Attributes

Every node (all 44 types) inherits these base attributes:

**Core Identity:**
- `name` (string, required) - Unique identifier
- `description` (string, required) - Human-readable explanation

**Bitemporal Tracking:**
- `valid_at` (datetime, required) - When this became true in reality
- `invalid_at` (datetime, optional) - When this ceased being true
- `expired_at` (datetime, optional) - When superseded by newer knowledge

**Consciousness Metadata:**
- `formation_trigger` (enum, required) - How discovered: `direct_experience`, `inference`, `external_input`, `traversal_discovery`, `systematic_analysis`, `spontaneous_insight`, `automated_recognition`, `collective_deliberation`
- `confidence` (float 0.0-1.0, required) - Certainty this is accurate

**Multi-Entity Activation (Energy-Only Model):**
- `entity_activations` (Dict[str, EntityActivationState]) - Per-entity energy budgets
  - `energy` (float 0.0-1.0) - This entity's activation budget on this node
  - `last_activated` (datetime) - When this entity last activated
  - **Note:** Energy IS everything (no separate arousal). Weight is the multiplier.

**Static Properties:**
- `base_weight` (float 0.0-1.0) - Base importance from creation
- `reinforcement_weight` (float 0.0-1.0) - Learned from usefulness
- `decay_rate` (float 0.9-0.99) - Energy decay per cycle (default: 0.95)

**Multi-Entity Clustering:**
- `entity_clusters` (Dict[str, string]) - Map of entity → cluster ID
  - Same node can belong to different clusters for different entities

---

## Niveau 1: Personal Consciousness (11 types)

**Purpose:** Individual subjective experience - exists in citizen graphs (e.g., citizen_luca)

**Design Philosophy:** Models the phenomenological texture of lived experience - memories, wounds, coping patterns. High arousal, high emotion_vector usage.

### Memory

**Purpose:** Specific experience or moment

**Required Attributes:**
- `timestamp`
- `participants (array)`

**Mechanism:** Pattern formation via repeated activation

### Conversation

**Purpose:** Exchange with explicit turn structure

**Required Attributes:**
- `timestamp`
- `with_person`
- `turn_count`

**Mechanism:** Relationship deepening mechanism

### Person

**Purpose:** Individual I have relationship with

**Required Attributes:**
- `relationship_type (enum)`

**Mechanism:** Entity representation in personal ontology

### Relationship

**Purpose:** Connection dynamics and evolution

**Required Attributes:**
- `with_person`
- `relationship_quality (float)`

**Mechanism:** Dynamic link weight updates

### Personal_Goal

**Purpose:** Individual aspiration

**Required Attributes:**
- `goal_description`
- `why_it_matters`

**Mechanism:** Drives spreading activation priority

### Personal_Value

**Purpose:** What matters to me individually

**Required Attributes:**
- `value_statement`
- `why_i_hold_it`

**Mechanism:** Constraint on action selection

### Personal_Pattern

**Purpose:** Habit or recurring response

**Required Attributes:**
- `behavior_description`
- `frequency (enum)`

**Mechanism:** Learned behavioral attractor

### Realization

**Purpose:** Insight or comprehension shift

**Required Attributes:**
- `what_i_realized`
- `context_when_discovered`

**Mechanism:** Sudden link formation event

### Wound

**Purpose:** Personal scar or trauma

**Required Attributes:**
- `what_happened`
- `emotional_impact (string)`

**Mechanism:** High-arousal suppression node

### Coping_Mechanism

**Purpose:** Response to stress

**Required Attributes:**
- `mechanism_description`
- `what_it_protects_from`

**Mechanism:** Defensive entity coalition

### Trigger

**Purpose:** What awakens entity coalitions

**Required Attributes:**
- `stimulus_description`
- `activated_entities (array)`

**Mechanism:** Activation propagation initiator

---

## Niveau 2: Organizational Consciousness (18 types)

**Purpose:** Collective intelligence and coordination - exists in organizational graphs (e.g., org_mind_protocol)

**Design Philosophy:** Models team cognition - decisions, coordination, collective learning. Medium arousal, emphasis on validation_status tracking.

### Human

**Purpose:** Human participant in organization

**Required Attributes:**
- `role`
- `expertise (array)`

**Mechanism:** Collective entity representation

### AI_Agent

**Purpose:** AI participant in organization

**Required Attributes:**
- `role`
- `expertise (array)`

**Mechanism:** Collective entity representation

### Team

**Purpose:** Group within organization

**Required Attributes:**
- `members (array)`
- `purpose`

**Mechanism:** Organizational structure node

### Department

**Purpose:** Organizational subdivision

**Required Attributes:**
- `function`
- `members (array)`

**Mechanism:** Organizational structure node

### Decision

**Purpose:** Collective choice with reasoning

**Required Attributes:**
- `decided_by`
- `decision_date`
- `rationale`

**Mechanism:** Collective deliberation crystallization

### Project

**Purpose:** Large initiative

**Required Attributes:**
- `goals (array)`
- `status (enum)`

**Mechanism:** Organizational intention tracker

### Task

**Purpose:** Discrete unit of work

**Required Attributes:**
- `priority (enum)`
- `estimated_hours`

**Mechanism:** Operational action node

### Milestone

**Purpose:** Organizational achievement

**Required Attributes:**
- `achievement_description`
- `date_achieved`

**Mechanism:** Progress marker

### Best_Practice

**Purpose:** Proven pattern

**Required Attributes:**
- `how_to_apply`
- `validation_criteria`

**Mechanism:** Organizational learning artifact

### Anti_Pattern

**Purpose:** Lesson from failure

**Required Attributes:**
- `(all optional)`

**Mechanism:** Negative learning artifact

### Risk

**Purpose:** Threat to goals

**Required Attributes:**
- `severity (float)`
- `probability (float)`

**Mechanism:** Constraint/blocker representation

### Metric

**Purpose:** Organizational measurement

**Required Attributes:**
- `measurement_method`
- `target_value`

**Mechanism:** Performance tracking node

### Process

**Purpose:** Defined workflow

**Required Attributes:**
- `steps (array[string])`

**Mechanism:** Procedural knowledge node

---

## Shared: Conceptual/Knowledge Nodes (5 types)

**Purpose:** Conceptual/knowledge nodes used in both organizational (N2) and ecosystem (N3) contexts

### Concept

**Purpose:** Atomic idea or construct

**Required Attributes:**
- `definition`

**Usage:** N2: Internal concepts, N3: Public concepts

### Principle

**Purpose:** Guiding philosophy

**Required Attributes:**
- `principle_statement`
- `why_it_matters`

**Usage:** N2: Organizational values, N3: Ecosystem principles

### Mechanism

**Purpose:** Algorithm or function

**Required Attributes:**
- `how_it_works`
- `inputs`
- `outputs`

**Usage:** N2: Internal systems, N3: Public protocols

### Document

**Purpose:** Written knowledge artifact

**Required Attributes:**
- `filepath`
- `document_type (enum)`

**Usage:** N2: Internal docs, N3: Public docs

### Documentation

**Purpose:** Tracked documentation file

**Required Attributes:**
- `file_path`

**Usage:** N2: Codebase docs, N3: Public specs

---

## Niveau 3: Ecosystem - External Organizations (5 types)

**Purpose:** External organizations and entities we track in the ecosystem

### Company

**Purpose:** External organization we track

**Required Attributes:**
- `company_type (enum)`
- `website`
- `status (enum)`

**Evidence Tracking:** Via JUSTIFIES links from Posts, Transactions

### External_Person

**Purpose:** Individual in ecosystem (not org member)

**Required Attributes:**
- `person_type (enum)`
- `primary_platform (enum)`

**Evidence Tracking:** Via HAS_TRAIT, POSTED_BY links

### Wallet_Address

**Purpose:** Blockchain wallet we track

**Required Attributes:**
- `address`
- `blockchain (enum)`
- `wallet_type (enum)`

**Evidence Tracking:** Via TRANSACTED_WITH, OWNS links

### Social_Media_Account

**Purpose:** Social media account we monitor

**Required Attributes:**
- `platform (enum)`
- `handle`
- `account_type (enum)`

**Evidence Tracking:** Via POSTED_BY, MENTIONED_IN links

### Smart_Contract

**Purpose:** Deployed smart contract

**Required Attributes:**
- `contract_address`
- `blockchain (enum)`
- `contract_type (enum)`

**Evidence Tracking:** Via DEPLOYED, INTEGRATED_WITH links

---

## Niveau 3: Ecosystem - Evidence Nodes (5 types)

**Purpose:** Evidence nodes that prove claims - the foundation of ecosystem intelligence

### Post

**Purpose:** Social media post providing evidence

**Required Attributes:**
- `content`
- `author`
- `platform`
- `posted_at`
- `post_url`

**What It Proves:** Beliefs, traits, intentions, market signals

### Transaction

**Purpose:** Blockchain transaction

**Required Attributes:**
- `transaction_hash`
- `blockchain`
- `from_address`
- `to_address`
- `amount_usd`
- `timestamp`

**What It Proves:** Ownership, behavior, capital flow

### Deal

**Purpose:** Business deal or partnership

**Required Attributes:**
- `parties (array)`
- `deal_type (enum)`
- `status (enum)`
- `announced_date`

**What It Proves:** Relationships, strategic direction

### Event

**Purpose:** Significant ecosystem event

**Required Attributes:**
- `event_type (enum)`
- `date`
- `participants (array)`

**What It Proves:** Context for behavior changes

### Market_Signal

**Purpose:** Trading/market indicator

**Required Attributes:**
- `signal_type (enum)`
- `asset`
- `value (float)`
- `timestamp`

**What It Proves:** Market sentiment, trends

---

## Niveau 3: Ecosystem - Derived Intelligence (5 types)

**Purpose:** Intelligence derived from accumulated evidence - the analytical layer

### Psychological_Trait

**Purpose:** Behavioral tendency of person/entity

**Required Attributes:**
- `trait_description`
- `subject (node ID)`
- `trait_type (enum)`

**Built From:** Accumulated via JUSTIFIES from Posts

### Behavioral_Pattern

**Purpose:** Recurring behavior of wallet/account

**Required Attributes:**
- `pattern_description`
- `subject (node ID)`
- `pattern_type (enum)`

**Built From:** Detected via EXHIBITS_PATTERN from Transactions

### Reputation_Assessment

**Purpose:** Trust/reputation score with evidence

**Required Attributes:**
- `subject (node ID)`
- `assessment_type (enum)`
- `score (float)`

**Built From:** Derived via JUSTIFIES from multiple sources

### Network_Cluster

**Purpose:** Group of related entities

**Required Attributes:**
- `cluster_type (enum)`
- `members (array)`
- `cohesion_score (float)`

**Built From:** Graph analysis result

### Integration

**Purpose:** Technical integration between systems

**Required Attributes:**
- `system_a`
- `system_b`
- `integration_type (enum)`
- `status (enum)`

**Built From:** Via INTEGRATED_WITH, DEPLOYED

---

## Summary

**Total Node Types:** 44

- **N1 (Personal):** 11 types - subjective experience, memories, patterns
- **N2 (Organizational):** 13 entity types + 5 shared = 18 types - collective intelligence
- **N3 (Ecosystem):** 5 external orgs + 5 evidence + 5 derived = 15 new types (+ 5 shared)

**Key Principles:**
- All nodes inherit universal base attributes (bitemporal, multi-entity, consciousness metadata)
- Energy-only model: no separate arousal, weight is the multiplier
- N1: High arousal, phenomenological texture
- N2: Medium arousal, validation tracking
- N3: Evidence-driven, all claims justified by concrete sources
- Multi-entity: Same node can have different energy/clusters per entity
- Dynamic citizen prompts: Identity emerges from active clusters

**Critical Architecture:**
- Citizens are substrate views: `Citizen = f(active_clusters)`
- Stability via heavy seeding: Identity weight 10.0, patterns weight 0.5
- Automatic decay: Links and nodes decay every cycle
- Natural entity limiting: Traversal cost scales with entity count
