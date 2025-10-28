# Mind Protocol - Complete Type Reference

**Auto-generated from schema_registry (FalkorDB)**
**Last updated:** 2025-10-27 14:11:13

This is the **single source of truth** for all node and link types in the Mind Protocol consciousness infrastructure.

**Contents:**
- Part 1: Universal Node Attributes (inherited by ALL 44 node types)
- Part 2: Universal Link Attributes (inherited by ALL 23 link types)
- Part 3: Node Type Inventory (44 types with full specifications)
- Part 4: Link Type Inventory (23 types with full specifications)

---

## Part 1: Universal Node Attributes

**These attributes are inherited by ALL 45 node types.**

Every node in the consciousness graph has these base attributes in addition to its type-specific fields.

### Activation Energy

- `base_weight` (float) - REQUIRED - Range: [0, 1]
  - Base importance from creation context
- `decay_rate` (float) - REQUIRED - Range: [0.9, 0.99]
  - Energy decay per cycle (default: 0.95)
- `reinforcement_weight` (float) - REQUIRED - Range: [0, 1]
  - Weight learned from usefulness evaluations

### Bitemporal Tracking

- `created_at` (datetime) - REQUIRED
  - When we learned about this fact
- `expired_at` (datetime) - REQUIRED
  - When this knowledge was superseded (None = current)
- `invalid_at` (datetime) - REQUIRED
  - When this fact ceased being true (None = still valid)
- `valid_at` (datetime) - REQUIRED
  - When this fact became true in reality

### Consciousness Metadata

- `confidence` (float) - REQUIRED - Range: [0, 1]
  - Certainty this node is accurate
- `formation_trigger` (enum) - REQUIRED - Allowed values: `direct_experience`, `inference`, `external_input`, `traversal_discovery`, `systematic_analysis`, `spontaneous_insight`, `automated_recognition`, `collective_deliberation`
  - How this node was discovered

### Core Idsubentity

- `description` (string) - REQUIRED
  - Human-readable explanation
- `name` (string) - REQUIRED
  - Unique identifier for this node
- `node_type` (string) - REQUIRED
  - The specific node class name (auto-set)

### Provenance

- `created_by` (string) - REQUIRED
  - Who/what created this node
- `substrate` (enum) - REQUIRED - Allowed values: `personal`, `organizational`, `gemini_web`, `external`
  - Where created

---

## Part 2: Universal Link Attributes

**These attributes are inherited by ALL 23 link types.**

Every link in the consciousness graph has these base attributes in addition to its type-specific fields.

### Bitemporal Tracking

- `created_at` (datetime) - REQUIRED
  - When we learned about this link
- `expired_at` (datetime) - REQUIRED
  - When this link knowledge was superseded
- `invalid_at` (datetime) - REQUIRED
  - When link ceased being true
- `valid_at` (datetime) - REQUIRED
  - When this link became true

### Consciousness Metadata

- `confidence` (float) - REQUIRED - Range: [0, 1]
  - Logical certainty in this connection
- `energy` (float) - REQUIRED - Range: [0, 1]
  - Emotional intensity/urgency
- `formation_trigger` (enum) - REQUIRED - Allowed values: `direct_experience`, `inference`, `external_input`, `traversal_discovery`, `systematic_analysis`, `spontaneous_insight`, `automated_recognition`, `collective_deliberation`
  - How this link was discovered
- `goal` (string) - REQUIRED
  - Why this link exists
- `mindstate` (string) - REQUIRED
  - Internal state when forming this link

### Optional Rich Metadata

- `alternatives_considered` (array) - REQUIRED
  - Other interpretations evaluated
- `created_by` (string) - REQUIRED
  - Who/what created this link
- `struggle` (string) - REQUIRED
  - Tension this link creates/resolves
- `substrate` (enum) - REQUIRED - Allowed values: `personal`, `organizational`, `gemini_web`, `external`
  - Where created
- `validation_status` (enum) - REQUIRED - Allowed values: `theoretical`, `experiential`, `tested`, `proven`
  - Quality progression

---

## Part 3: Node Type Inventory

**Total:** 45 node types defined

### Level 1 (Personal) - 11 Types

**Conversation**

- **Category:** personal
- **Description:** Exchange with explicit turn structure

**Type-Specific Required Fields:**
- `timestamp` (datetime)
  - When conversation occurred
- `turn_count` (integer)
  - Number of turns in conversation
- `with_person` (string)
  - Who I conversed with

**Coping_Mechanism**

- **Category:** personal
- **Description:** Response to stress

**Type-Specific Required Fields:**
- `mechanism_description` (string)
  - How I cope
- `what_it_protects_from` (string)
  - What this mechanism defends against

**Memory**

- **Category:** personal
- **Description:** Specific experience or moment

**Type-Specific Required Fields:**
- `participants` (array)
  - Who was involved
- `timestamp` (datetime)
  - When this memory occurred

**Person**

- **Category:** personal
- **Description:** Individual I have relationship with

**Type-Specific Required Fields:**
- `relationship_type` (enum) - Allowed values: `friend`, `colleague`, `mentor`, `family`, `acquaintance`
  - Type of relationship

**Personal_Goal**

- **Category:** personal
- **Description:** Individual aspiration

**Type-Specific Required Fields:**
- `goal_description` (string)
  - What the goal is
- `why_it_matters` (string)
  - Why this goal is important to me

**Personal_Pattern**

- **Category:** personal
- **Description:** Habit or recurring response

**Type-Specific Required Fields:**
- `behavior_description` (string)
  - Description of the pattern
- `frequency` (enum) - Allowed values: `constant`, `frequent`, `occasional`, `rare`
  - How often this pattern occurs

**Personal_Value**

- **Category:** personal
- **Description:** What matters to me individually

**Type-Specific Required Fields:**
- `value_statement` (string)
  - The value itself
- `why_i_hold_it` (string)
  - Why I hold this value

**Realization**

- **Category:** personal
- **Description:** Insight or comprehension shift

**Type-Specific Required Fields:**
- `context_when_discovered` (string)
  - Context when this realization occurred
- `what_i_realized` (string)
  - The insight itself

**Relationship**

- **Category:** personal
- **Description:** Connection dynamics and evolution

**Type-Specific Required Fields:**
- `relationship_quality` (float) - Range: [0, 1]
  - Quality of relationship
- `with_person` (string)
  - Who this relationship is with

**Trigger**

- **Category:** personal
- **Description:** What awakens subentity coalitions

**Type-Specific Required Fields:**
- `activated_entities` (array)
  - Which subentities this triggers
- `stimulus_description` (string)
  - What triggers activation

**Wound**

- **Category:** personal
- **Description:** Personal scar or trauma

**Type-Specific Required Fields:**
- `emotional_impact` (string)
  - How this affects me emotionally
- `what_happened` (string)
  - What caused the wound

### Level 2 (Organizational) - 14 Types

**AI_Agent**

- **Category:** organizational
- **Description:** AI participant in organization

**Type-Specific Required Fields:**
- `expertise` (array)
  - Areas of expertise
- `role` (string)
  - Role in organization

**Anti_Pattern**

- **Category:** organizational
- **Description:** Lesson from failure

**Best_Practice**

- **Category:** organizational
- **Description:** Proven pattern

**Type-Specific Required Fields:**
- `how_to_apply` (array)
  - How to apply this practice (list of steps)
- `validation_criteria` (string)
  - How to verify it works

**Code**

- **Category:** organizational
- **Description:** Code file tracked in consciousness

**Type-Specific Required Fields:**
- `file_path` (string)
  - Path to the code file
- `language` (enum) - Allowed values: `python`, `typescript`, `javascript`, `sql`, `bash`, `rust`, `go`, `other`
  - Programming language
- `purpose` (string)
  - What this code does

**Type-Specific Optional Fields:**
- `complexity` (enum) - Allowed values: `simple`, `moderate`, `complex`
  - Code complexity level
- `dependencies` (array)
  - What this code depends on
- `status` (enum) - Allowed values: `active`, `deprecated`, `experimental`
  - Current status of the code

**Decision**

- **Category:** organizational
- **Description:** Organization choice with reasoning

**Type-Specific Required Fields:**
- `decided_by` (string)
  - Who made the decision
- `decision_date` (datetime)
  - When decision was made
- `rationale` (string)
  - Why this decision was made

**Department**

- **Category:** organizational
- **Description:** Organizational subdivision

**Type-Specific Required Fields:**
- `function` (string)
  - Department function
- `members` (array)
  - Department members

**Human**

- **Category:** organizational
- **Description:** Human participant in organization

**Type-Specific Required Fields:**
- `expertise` (array)
  - Areas of expertise
- `role` (string)
  - Role in organization

**Metric**

- **Category:** organizational
- **Description:** Organizational measurement

**Type-Specific Required Fields:**
- `measurement_method` (string)
  - How to measure this
- `target_value` (string)
  - Target value

**Milestone**

- **Category:** organizational
- **Description:** Organizational achievement

**Type-Specific Required Fields:**
- `achievement_description` (string)
  - What was achieved
- `date_achieved` (datetime)
  - When it was achieved

**Process**

- **Category:** organizational
- **Description:** Defined workflow

**Type-Specific Required Fields:**
- `steps` (array)
  - Process steps

**Project**

- **Category:** organizational
- **Description:** Large initiative

**Type-Specific Required Fields:**
- `goals` (array)
  - Project goals
- `status` (enum) - Allowed values: `planning`, `active`, `completed`, `cancelled`
  - Current status

**Risk**

- **Category:** organizational
- **Description:** Threat to goals

**Type-Specific Required Fields:**
- `probability` (float) - Range: [0, 1]
  - Likelihood of occurrence
- `severity` (float) - Range: [0, 1]
  - How severe is this risk

**Task**

- **Category:** organizational
- **Description:** Discrete unit of work

**Type-Specific Required Fields:**
- `estimated_hours` (float)
  - Estimated time to complete
- `priority` (enum) - Allowed values: `critical`, `high`, `medium`, `low`
  - Task priority

**Team**

- **Category:** organizational
- **Description:** Group within organization

**Type-Specific Required Fields:**
- `members` (array)
  - Team members
- `purpose` (string)
  - Team purpose

### Shared (Knowledge) - 5 Types

**Concept**

- **Category:** knowledge
- **Description:** Atomic idea or construct

**Type-Specific Required Fields:**
- `definition` (string)
  - Definition of the concept

**Document**

- **Category:** knowledge
- **Description:** Written knowledge artifact

**Type-Specific Required Fields:**
- `document_type` (enum) - Allowed values: `spec`, `guide`, `reference`, `plan`, `report`
  - Type of document
- `filepath` (string)
  - Path to document

**Documentation**

- **Category:** knowledge
- **Description:** Tracked documentation file

**Type-Specific Required Fields:**
- `file_path` (string)
  - Path to documentation file

**Mechanism**

- **Category:** knowledge
- **Description:** Algorithm or function

**Type-Specific Required Fields:**
- `how_it_works` (string)
  - How the mechanism operates
- `inputs` (string)
  - What inputs it takes
- `outputs` (string)
  - What outputs it produces

**Principle**

- **Category:** knowledge
- **Description:** Guiding philosophy

**Type-Specific Required Fields:**
- `principle_statement` (string)
  - The principle itself
- `why_it_matters` (string)
  - Why this principle is important

### Level 3 (Ecosystem) - 15 Types

**Behavioral_Pattern**

- **Category:** derived
- **Description:** Recurring behavior of wallet/account

**Type-Specific Required Fields:**
- `pattern_description` (string)
  - Description of the pattern
- `pattern_type` (enum) - Allowed values: `trading`, `social`, `technical`
  - Type of pattern
- `subject` (string)
  - Who exhibits this (node ID)

**Company**

- **Category:** ecosystem
- **Description:** External organization we track

**Type-Specific Required Fields:**
- `company_type` (enum) - Allowed values: `startup`, `enterprise`, `dao`, `protocol`
  - Type of company
- `status` (enum) - Allowed values: `active`, `acquired`, `defunct`
  - Current status
- `website` (string)
  - Company website

**Deal**

- **Category:** evidence
- **Description:** Business deal or partnership

**Type-Specific Required Fields:**
- `announced_date` (datetime)
  - When announced
- `deal_type` (enum) - Allowed values: `investment`, `partnership`, `acquisition`
  - Type of deal
- `parties` (array)
  - Parties involved
- `status` (enum) - Allowed values: `announced`, `completed`, `cancelled`
  - Deal status

**Event**

- **Category:** evidence
- **Description:** Significant ecosystem event

**Type-Specific Required Fields:**
- `date` (datetime)
  - When it occurred
- `event_type` (enum) - Allowed values: `launch`, `hack`, `upgrade`, `governance`
  - Type of event
- `participants` (array)
  - Who was involved

**External_Person**

- **Category:** ecosystem
- **Description:** Individual in ecosystem (not org member)

**Type-Specific Required Fields:**
- `person_type` (enum) - Allowed values: `founder`, `investor`, `influencer`, `developer`
  - Type of person
- `primary_platform` (enum) - Allowed values: `twitter`, `linkedin`, `github`
  - Primary social platform

**Integration**

- **Category:** derived
- **Description:** Technical integration between systems

**Type-Specific Required Fields:**
- `integration_type` (enum) - Allowed values: `api`, `bridge`, `protocol`
  - Type of integration
- `status` (enum) - Allowed values: `active`, `deprecated`, `planned`
  - Integration status
- `system_a` (string)
  - First system
- `system_b` (string)
  - Second system

**Market_Signal**

- **Category:** evidence
- **Description:** Trading/market indicator

**Type-Specific Required Fields:**
- `asset` (string)
  - Which asset
- `signal_type` (enum) - Allowed values: `price`, `volume`, `sentiment`
  - Type of signal
- `timestamp` (datetime)
  - When measured
- `value` (float)
  - Signal value

**Network_Cluster**

- **Category:** derived
- **Description:** Group of related subentities

**Type-Specific Required Fields:**
- `cluster_type` (enum) - Allowed values: `social`, `financial`, `technical`
  - Type of cluster
- `cohesion_score` (float) - Range: [0, 1]
  - How cohesive the cluster is
- `members` (array)
  - Cluster members

**Post**

- **Category:** evidence
- **Description:** Social media post providing evidence

**Type-Specific Required Fields:**
- `author` (string)
  - Who posted it
- `content` (string)
  - Post content
- `platform` (enum) - Allowed values: `twitter`, `linkedin`, `farcaster`
  - Which platform
- `post_url` (string)
  - URL to post
- `posted_at` (datetime)
  - When it was posted

**Psychological_Trait**

- **Category:** derived
- **Description:** Behavioral tendency of person/subentity

**Type-Specific Required Fields:**
- `subject` (string)
  - Who has this trait (node ID)
- `trait_description` (string)
  - Description of the trait
- `trait_type` (enum) - Allowed values: `bullish`, `bearish`, `risk-averse`, `aggressive`
  - Type of trait

**Reputation_Assessment**

- **Category:** derived
- **Description:** Trust/reputation score with evidence

**Type-Specific Required Fields:**
- `assessment_type` (enum) - Allowed values: `credibility`, `expertise`, `trustworthiness`
  - Type of assessment
- `score` (float) - Range: [0, 1]
  - Assessment score
- `subject` (string)
  - Who is being assessed (node ID)

**Smart_Contract**

- **Category:** ecosystem
- **Description:** Deployed smart contract

**Type-Specific Required Fields:**
- `blockchain` (enum) - Allowed values: `ethereum`, `solana`
  - Which blockchain
- `contract_address` (string)
  - Contract address
- `contract_type` (enum) - Allowed values: `token`, `defi`, `nft`, `governance`
  - Type of contract

**Social_Media_Account**

- **Category:** ecosystem
- **Description:** Social media account we monitor

**Type-Specific Required Fields:**
- `account_type` (enum) - Allowed values: `personal`, `company`, `project`
  - Type of account
- `handle` (string)
  - Account handle
- `platform` (enum) - Allowed values: `twitter`, `linkedin`, `github`, `farcaster`
  - Platform

**Transaction**

- **Category:** evidence
- **Description:** Blockchain transaction

**Type-Specific Required Fields:**
- `amount_usd` (float)
  - Transaction value in USD
- `blockchain` (enum) - Allowed values: `ethereum`, `solana`, `bitcoin`
  - Which blockchain
- `from_address` (string)
  - Source address
- `timestamp` (datetime)
  - When transaction occurred
- `to_address` (string)
  - Destination address
- `transaction_hash` (string)
  - Transaction hash

**Wallet_Address**

- **Category:** ecosystem
- **Description:** Blockchain wallet we track

**Type-Specific Required Fields:**
- `address` (string)
  - Wallet address
- `blockchain` (enum) - Allowed values: `ethereum`, `solana`, `bitcoin`
  - Which blockchain
- `wallet_type` (enum) - Allowed values: `eoa`, `contract`, `multisig`
  - Type of wallet

---

## Part 4: Link Type Inventory

**Total:** 23 link types defined

### Shared Link Types - 17 Types

**ASSIGNED_TO**

- **Category:** organizational
- **Description:** Task ownership or responsibility

**BLOCKS**

- **Category:** structural
- **Description:** Prevents progress or blocks execution

**Type-Specific Required Fields:**
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
- **Description:** Working partnership between subentities

**CONTRIBUTES_TO**

- **Category:** organizational
- **Description:** Work supporting larger initiative

**CREATES**

- **Category:** documentation
- **Description:** Task will produce this artifact when completed

**DOCUMENTED_BY**

- **Category:** documentation
- **Description:** Implementation documented by this artifact

**DOCUMENTS**

- **Category:** documentation
- **Description:** Written record of implementation or decision

**Type-Specific Optional Fields:**
- `documentation_type` (string)
  - Type of documentation (spec, guide, reference, etc.)

**ENABLES**

- **Category:** structural
- **Description:** Makes something possible or facilitates it

**Type-Specific Required Fields:**
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

**Type-Specific Required Fields:**
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

**JUSTIFIES**

- **Category:** evidence
- **Description:** Evidence supporting practice/decision/claim

**Type-Specific Required Fields:**
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

**REFUTES**

- **Category:** evidence
- **Description:** Disproves or invalidates claim

**RELATES_TO**

- **Category:** structural
- **Description:** Generic connection when specific type unclear

**Type-Specific Required Fields:**
- `needs_refinement` (boolean)
  - Should this be replaced with more specific link type?
- `refinement_candidates` (array)
  - Potential more specific link types to use
- `relationship_strength` (enum) - Allowed values: `strong`, `moderate`, `weak`, `exploratory`
  - Strength of relationship

**REQUIRES**

- **Category:** dependency
- **Description:** Necessary conditions or prerequisites

**Type-Specific Required Fields:**
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

**THREATENS**

- **Category:** organizational
- **Description:** Danger or risk to goal/project

### Level 1 (Personal) Link Types - 6 Types

**ACTIVATES**

- **Category:** activation
- **Description:** Trigger awakens subentity coalition

**DEEPENED_WITH**

- **Category:** learning
- **Description:** Relationship growth through experience

**DRIVES_TOWARD**

- **Category:** value
- **Description:** Value pushing toward goal

**LEARNED_FROM**

- **Category:** learning
- **Description:** Personal pattern extracted from experience

**SUPPRESSES**

- **Category:** activation
- **Description:** What blocks subentity activation

**TRIGGERED_BY**

- **Category:** activation
- **Description:** What caused memory/pattern to activate

---

## How to Update

**To add/modify a node or link type:**
1. Update `tools/complete_schema_data.py` with the new/modified type
2. Run `python tools/complete_schema_ingestion.py` to re-ingest to schema_registry
3. Run `python tools/generate_complete_type_reference.py --write-file` to regenerate this file

**Schema Registry Location:** FalkorDB graph `schema_registry`

**This document is auto-generated - DO NOT edit manually**
