# Mind Protocol - Complete Type Reference

**Auto-generated from schema_registry (FalkorDB)**
**Last updated:** 2025-10-30 01:20:10

This is the **single source of truth** for all node and link types in the Mind Protocol consciousness infrastructure.

**Contents:**
- Part 1: Universal Node Attributes (inherited by ALL 44 node types)
- Part 2: Universal Link Attributes (inherited by ALL 23 link types)
- Part 3: Node Type Inventory (44 types with full specifications)
- Part 4: Link Type Inventory (23 types with full specifications)

---

## Part 1: Universal Node Attributes

**These attributes are inherited by ALL 88 node types.**

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

**These attributes are inherited by ALL 61 link types.**

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

**Total:** 88 node types defined

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

### Level 3 (Ecosystem) - 34 Types

**Agreement**

- **Category:** ecosystem
- **Description:** Signed agreement associated with a deal

**Type-Specific Required Fields:**
- `agreement_type` (enum) - Allowed values: `MSA`, `NDA`, `SLA`, `Confirmation`
  - Agreement type
- `effective_at` (datetime)
  - Effective date

**Type-Specific Optional Fields:**
- `expires_at` (datetime)
  - Expiration date, if any

**Attestation**

- **Category:** evidence
- **Description:** Signed attestation backing an artefact

**Type-Specific Required Fields:**
- `issuer` (string)
  - Issuing party
- `purpose` (string)
  - Purpose of the attestation
- `sig` (string)
  - Signature or hash

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

**Capability_Descriptor**

- **Category:** ecosystem
- **Description:** Descriptor of a capability (mapped to L4 schema references)

**Type-Specific Required Fields:**
- `name` (string)
  - Capability name
- `schema_ref` (string)
  - Reference to L4 schema or SDK module

**Type-Specific Optional Fields:**
- `cost_hint` (string)
  - Human readable pricing hint

**Citizen_Template**

- **Category:** ecosystem
- **Description:** Citizen template provided by ecosystem bootstrap

**Type-Specific Required Fields:**
- `default_publish` (array)
  - Default inject channels
- `default_subscribe` (array)
  - Default broadcast topics to subscribe
- `image` (string)
  - Container image or package ref

**Type-Specific Optional Fields:**
- `limits` (object)
  - Resource limits (cpu/mem)

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

**Contact_Channel**

- **Category:** ecosystem
- **Description:** Contact channel for a public presence

**Type-Specific Required Fields:**
- `address` (string)
  - Contact address / endpoint
- `channel_type` (enum) - Allowed values: `email`, `api`, `portal`
  - Channel modality

**Counterparty**

- **Category:** ecosystem
- **Description:** Counterparty participating in deals

**Type-Specific Required Fields:**
- `company_type` (enum) - Allowed values: `startup`, `enterprise`, `dao`, `protocol`
  - Type of counterparty
- `status` (enum) - Allowed values: `active`, `inactive`, `suspended`
  - Status in ecosystem

**Type-Specific Optional Fields:**
- `website` (string)
  - Website or landing page

**Deal**

- **Category:** evidence
- **Description:** Business deal / transaction record

**Type-Specific Required Fields:**
- `deal_type` (enum) - Allowed values: `trade`, `partnership`, `service`
  - Deal category
- `instrument` (enum) - Allowed values: `TermSheet`, `Confirmation`
  - Instrument used
- `state` (enum) - Allowed values: `Proposed`, `Negotiating`, `Agreed`, `Settled`, `Cancelled`
  - Lifecycle state

**Type-Specific Optional Fields:**
- `incoterm` (string)
  - Applicable incoterm
- `price` (float)
  - Price agreed
- `qty` (float)
  - Quantity involved

**Ecosystem**

- **Category:** ecosystem
- **Description:** Domain container (e.g. trading commodities)

**Type-Specific Required Fields:**
- `domain` (string)
  - Domain vertical
- `slug` (string)
  - URL-friendly identifier
- `version` (string)
  - Manifest version

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

**Info_Asset**

- **Category:** evidence
- **Description:** Shareable information asset

**Type-Specific Required Fields:**
- `access` (enum) - Allowed values: `public`, `bilateral`, `paid`
  - Access level
- `pointer` (string)
  - CID/URI reference
- `title` (string)
  - Title of the asset

**Type-Specific Optional Fields:**
- `tags` (array)
  - Classification tags

**Info_Offer**

- **Category:** ecosystem
- **Description:** Offer to provide access to an information asset

**Type-Specific Required Fields:**
- `price_model` (enum) - Allowed values: `free`, `one_off`, `subscription`
  - Pricing model
- `terms` (string)
  - Key terms of access

**Info_Request**

- **Category:** ecosystem
- **Description:** Request for information

**Type-Specific Required Fields:**
- `deadline` (datetime)
  - Deadline for response
- `topic` (string)
  - Topic of interest

**Type-Specific Optional Fields:**
- `constraints` (string)
  - Constraints / filters

**Instrument**

- **Category:** ecosystem
- **Description:** Negotiation instrument / template

**Type-Specific Required Fields:**
- `instrument_type` (enum) - Allowed values: `TermSheet`, `Confirmation`
  - Type of instrument
- `template_uri` (string)
  - URI to template or repository
- `version` (string)
  - Template version

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

**Market**

- **Category:** ecosystem
- **Description:** Market segment / geography

**Type-Specific Required Fields:**
- `name` (string)
  - Market name

**Type-Specific Optional Fields:**
- `product_class` (string)
  - Product class or family
- `region` (string)
  - Geographical region

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

**Org_Profile**

- **Category:** ecosystem
- **Description:** Organization profile within the ecosystem layer

**Type-Specific Required Fields:**
- `jurisdiction` (string)
  - Primary legal jurisdiction
- `org_id` (string)
  - Organization identifier

**Type-Specific Optional Fields:**
- `tags` (array)
  - Free-form labels for search

**Policy_Lane**

- **Category:** ecosystem
- **Description:** Lane definition used by orchestrator

**Type-Specific Required Fields:**
- `ack_policy` (enum) - Allowed values: `none`, `human_required`, `tool_required`
  - Acknowledgement policy
- `capacity` (int)
  - Concurrent capacity
- `lane_id` (string)
  - Lane identifier

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

**Public_Presence**

- **Category:** ecosystem
- **Description:** Published surface of an organization (capabilities, channels)

**Type-Specific Required Fields:**
- `capabilities` (array)
  - Capabilities exposed publicly
- `channels` (array)
  - List of supported public channels
- `visibility` (enum) - Allowed values: `public`, `partners`, `private`
  - Audience scope

**Type-Specific Optional Fields:**
- `attestations` (array)
  - Evidence node IDs backing the presence

**Quote**

- **Category:** evidence
- **Description:** Offer of price responding to an RFQ

**Type-Specific Required Fields:**
- `currency` (string)
  - ISO currency code
- `price` (float)
  - Quoted price
- `terms` (string)
  - Key contractual terms
- `valid_until` (datetime)
  - Expiration timestamp

**RFQ**

- **Category:** evidence
- **Description:** Structured request for quote

**Type-Specific Required Fields:**
- `commodity` (string)
  - Requested commodity / product
- `delivery_window` (object)
  - Object {from, to} specifying delivery period
- `incoterm` (string)
  - Incoterm (FOB, CIF, etc.)
- `qty` (object)
  - Quantity object {value, unit}

**Type-Specific Optional Fields:**
- `counterparty_pref` (array)
  - Preferred counterparties

**Renderer_Template**

- **Category:** ecosystem
- **Description:** Renderer template for publications

**Type-Specific Required Fields:**
- `output` (enum) - Allowed values: `git:publications`, `site:static`
  - Output target
- `triggers` (array)
  - Events that trigger rendering

**Type-Specific Optional Fields:**
- `branch_prefix` (string)
  - Branch prefix used for PRs

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

**Tool_Template**

- **Category:** ecosystem
- **Description:** Tool runner template

**Type-Specific Required Fields:**
- `capabilities` (array)
  - Capabilities served
- `runner_image` (string)
  - Container image

**Type-Specific Optional Fields:**
- `resources` (object)
  - Resource hints (cpu/mem)

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

### Level 4 (Protocol) - 24 Types

**Adapter_Release**

- **Category:** artifact
- **Description:** Release metadata for provider adapters (Claude/Codex/Gemini).

**Type-Specific Required Fields:**
- `features` (array)
  - Supported feature list
- `provider` (enum) - Allowed values: `claude`, `codex`, `gemini`, `other`
  - Provider identifier
- `version` (string)
  - Adapter version

**Bus_Instance**

- **Category:** infra
- **Description:** Concrete bus instance available to tenants.

**Type-Specific Required Fields:**
- `endpoint` (string)
  - Endpoint URI
- `retention_policy_ref` (string)
  - Reference to Retention_Policy
- `transport_ref` (string)
  - Reference to Transport_Spec

**Capability**

- **Category:** protocol
- **Description:** Logical capability exposed through the protocol.

**Type-Specific Required Fields:**
- `capability` (string)
  - Capability identifier (e.g. git.commit)
- `input_schema_ref` (string)
  - Reference to input Event_Schema
- `output_schema_ref` (string)
  - Reference to output Event_Schema

**Compatibility_Matrix**

- **Category:** protocol
- **Description:** Compatibility matrix between releases and schemas.

**Type-Specific Required Fields:**
- `generated_at` (datetime)
  - Generation timestamp
- `matrix` (array)
  - Rows describing compatibility states

**Conformance_Case**

- **Category:** protocol
- **Description:** Individual conformance test case.

**Type-Specific Required Fields:**
- `case_id` (string)
  - Case identifier
- `description` (string)
  - Case description
- `expected` (enum) - Allowed values: `pass`, `fail`, `warn`
  - Expected outcome

**Conformance_Result**

- **Category:** protocol
- **Description:** Execution result for a conformance suite.

**Type-Specific Required Fields:**
- `failing_cases` (array)
  - Identifiers of failing cases
- `pass_rate` (float)
  - Pass ratio (0..1)
- `suite_id` (string)
  - Suite identifier
- `target_release` (string)
  - Target release identifier (e.g. sdk.ts@1.2.0)

**Conformance_Suite**

- **Category:** protocol
- **Description:** Suite of protocol conformance tests.

**Type-Specific Required Fields:**
- `cases_count` (int)
  - Number of test cases
- `schema_set_ref` (string)
  - Reference to schema set
- `suite_id` (string)
  - Suite identifier

**Deprecation_Notice**

- **Category:** governance
- **Description:** Notice announcing protocol deprecation of schema or release.

**Type-Specific Required Fields:**
- `effective_at` (datetime)
  - Effective timestamp
- `end_of_support` (datetime)
  - End-of-support timestamp
- `target_kind` (enum) - Allowed values: `Event_Schema`, `Capability`, `SDK_Release`, `Sidecar_Release`
  - Kind being deprecated
- `target_ref` (string)
  - Reference to deprecated element

**Envelope_Schema**

- **Category:** protocol
- **Description:** Schema for the transport envelope (metadata, signature, TTL).

**Type-Specific Required Fields:**
- `fields` (array)
  - Canonical fields with constraints
- `name` (string)
  - Envelope schema name
- `signature_path` (string)
  - JSON path to signature payload (e.g. $.sig)
- `version` (string)
  - Envelope schema version

**Event_Schema**

- **Category:** protocol
- **Description:** JSON schema describing a protocol event (inject or broadcast).

**Type-Specific Required Fields:**
- `direction` (enum) - Allowed values: `inject`, `broadcast`
  - Flow direction
- `name` (string)
  - Event name (e.g. membrane.inject)
- `schema_hash` (string)
  - SHA256 of the JSON schema
- `schema_uri` (string)
  - Location of the JSON schema
- `topic_pattern` (string)
  - Topic pattern used on the bus
- `version` (string)
  - Schema version string

**Governance_Policy**

- **Category:** governance
- **Description:** Protocol policy (lanes, backpressure, governance defaults).

**Type-Specific Required Fields:**
- `defaults` (object)
  - Default settings (e.g. ack_policy)
- `name` (string)
  - Policy identifier
- `policy_doc_uri` (string)
  - URI to policy documentation

**Protocol_Version**

- **Category:** protocol
- **Description:** Semantic version of the protocol specification.

**Type-Specific Required Fields:**
- `released_at` (datetime)
  - Release timestamp
- `semver` (string)
  - Semantic version identifier (e.g. 1.1.0)
- `summary` (string)
  - Release highlights

**Retention_Policy**

- **Category:** protocol
- **Description:** Retention and de-duplication policy for the bus.

**Type-Specific Required Fields:**
- `dedupe_window_ms` (int)
  - Deduplication window in milliseconds
- `name` (string)
  - Policy name
- `size_limit_mb` (int)
  - Storage limit in megabytes
- `time_limit` (duration)
  - Retention duration (e.g. 3d)

**SDK_Release**

- **Category:** artifact
- **Description:** Release metadata for SDK distributions.

**Type-Specific Required Fields:**
- `commit_hash` (string)
  - Commit hash for release
- `language` (enum) - Allowed values: `typescript`, `python`, `go`
  - SDK language
- `package_name` (string)
  - Package identifier
- `schema_min_version` (string)
  - Minimum compatible schema version
- `version` (string)
  - SDK version

**Schema_Bundle**

- **Category:** artifact
- **Description:** Versioned archive of protocol schemas.

**Type-Specific Required Fields:**
- `bundle_hash` (string)
  - Hash of bundle contents
- `bundle_uri` (string)
  - URI to bundle (tar/zip)
- `contains` (array)
  - List of schema refs included (name@version)

**Security_Profile**

- **Category:** protocol
- **Description:** Security requirements for namespaces or schemas.

**Type-Specific Required Fields:**
- `min_key_length_bits` (int)
  - Minimum key length in bits
- `profile_name` (string)
  - Profile identifier
- `required_signature_suites` (array)
  - Allowed signature suites

**Sidecar_Release**

- **Category:** artifact
- **Description:** Release metadata for the Sidecar client.

**Type-Specific Required Fields:**
- `features` (array)
  - Feature list (buffer_offline, replay, etc.)
- `image_ref` (string)
  - Container image reference
- `schema_min_version` (string)
  - Minimum compatible schema version
- `version` (string)
  - Release version

**Signature_Suite**

- **Category:** protocol
- **Description:** Cryptographic suite authorised for protocol signatures.

**Type-Specific Required Fields:**
- `algo` (enum) - Allowed values: `ed25519`
  - Signature algorithm
- `pubkey_encoding` (enum) - Allowed values: `base64`, `hex`
  - Public key encoding
- `signature_field` (string)
  - Path to signature field (e.g. sig.signature)

**Tenant**

- **Category:** governance
- **Description:** Protocol-level tenant (organization identity).

**Type-Specific Required Fields:**
- `display_name` (string)
  - Human readable name
- `org_id` (string)
  - Tenant identifier

**Tenant_Key**

- **Category:** governance
- **Description:** Key material associated with a tenant.

**Type-Specific Required Fields:**
- `created_at` (datetime)
  - Creation timestamp
- `key_version` (int)
  - Sequential key version
- `org_id` (string)
  - Tenant identifier
- `pubkey` (string)
  - Public key material
- `rotated_at` (datetime)
  - Rotation timestamp (nullable)

**Tool_Contract**

- **Category:** protocol
- **Description:** Contract describing a tool's capabilities and schemas.

**Type-Specific Required Fields:**
- `args_schema_ref` (string)
  - Reference to arguments schema
- `capabilities` (array)
  - Capabilities served by the tool
- `result_schema_ref` (string)
  - Reference to result schema
- `tool_id` (string)
  - Tool identifier

**Topic_Namespace**

- **Category:** protocol
- **Description:** Bus namespace definition (wildcard patterns, scope).

**Type-Specific Required Fields:**
- `description` (string)
  - Purpose and usage notes
- `pattern` (string)
  - Topic pattern (e.g. org/{org_id}/broadcast/*)
- `scope` (enum) - Allowed values: `org`, `global`
  - Namespace scope

**Topic_Route**

- **Category:** infra
- **Description:** Documentation of logical routing between namespaces and components.

**Type-Specific Required Fields:**
- `from_namespace` (string)
  - Source namespace pattern
- `routing_notes` (string)
  - Routing behaviour description
- `to_component` (string)
  - Destination component (e.g. orchestrator)

**Transport_Spec**

- **Category:** infra
- **Description:** Transport semantics (WS/NATS/Kafka) for the bus.

**Type-Specific Required Fields:**
- `qos` (object)
  - Quality-of-service settings (durable, acks, etc.)
- `type` (enum) - Allowed values: `ws`, `nats`, `kafka`
  - Transport type

---

## Part 4: Link Type Inventory

**Total:** 61 link types defined

### Shared Link Types - 15 Types

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

**THREATENS**

- **Category:** organizational
- **Description:** Danger or risk to goal/project

### Level 1 (Personal) Link Types - 5 Types

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

### Level 3 (Ecosystem) Link Types - 21 Types

**ACTIVATES**

- **Category:** ecosystem
- **Description:** Ecosystem activates template (citizen/tool/renderer)

**Type-Specific Required Fields:**
- `activation_id` (string)
  - Activation identifier

**CONFORMS_TO**

- **Category:** ecosystem
- **Description:** Descriptor/template conforms to L4 schema

**Type-Specific Required Fields:**
- `schema_version` (string)
  - Schema version

**DEPLOYS**

- **Category:** ecosystem
- **Description:** Ecosystem deploys org profile into workspace

**Type-Specific Required Fields:**
- `deployment_id` (string)
  - Deployment identifier

**ENDORSES**

- **Category:** ecosystem
- **Description:** Org endorses another org/capability

**Type-Specific Required Fields:**
- `endorsement_type` (enum) - Allowed values: `reputation`, `capability`
  - Nature of endorsement

**EVIDENCED_BY**

- **Category:** ecosystem
- **Description:** Artefact evidenced by attestation

**Type-Specific Required Fields:**
- `evidence_type` (enum) - Allowed values: `doc`, `hash`
  - Evidence modality

**HAS_CHANNEL**

- **Category:** ecosystem
- **Description:** Public presence exposes a contact channel

**Type-Specific Required Fields:**
- `priority` (enum) - Allowed values: `primary`, `secondary`
  - Priority of channel

**LISTS_CAPABILITY**

- **Category:** ecosystem
- **Description:** Public presence lists a capability descriptor

**NEGOTIATES**

- **Category:** ecosystem
- **Description:** Org negotiates a deal

**Type-Specific Required Fields:**
- `role` (enum) - Allowed values: `buyer`, `seller`
  - Role in negotiation

**OFFERS**

- **Category:** ecosystem
- **Description:** Org offers an info asset or info offer

**Type-Specific Required Fields:**
- `access_level` (enum) - Allowed values: `public`, `bilateral`, `paid`
  - Access level granted

**PROPOSES**

- **Category:** ecosystem
- **Description:** Org proposes a deal or RFQ

**PUBLISHES**

- **Category:** ecosystem
- **Description:** Org profile publishes a public presence

**Type-Specific Required Fields:**
- `audience` (enum) - Allowed values: `public`, `partners`
  - Intended audience

**QUOTES_FOR**

- **Category:** ecosystem
- **Description:** Org issues a quote responding to an RFQ

**REFERENCES_MARKET**

- **Category:** ecosystem
- **Description:** Deal/RFQ/Quote references market

**RESPONDS_TO**

- **Category:** ecosystem
- **Description:** Quote responds to an RFQ

**Type-Specific Required Fields:**
- `response_time_ms` (float)
  - Response latency in milliseconds

**RESTRICTED_BY**

- **Category:** ecosystem
- **Description:** Asset or offer restricted by lane or agreement

**Type-Specific Required Fields:**
- `restriction_type` (enum) - Allowed values: `lane`, `agreement`
  - Restriction source

**ROUTES_VIA**

- **Category:** ecosystem
- **Description:** Lane routes requests via capability

**Type-Specific Required Fields:**
- `priority` (int)
  - Routing priority

**SEEKS**

- **Category:** ecosystem
- **Description:** Org seeks an info request

**SETTLED_BY**

- **Category:** ecosystem
- **Description:** Deal settled by an agreement

**Type-Specific Required Fields:**
- `settlement_date` (datetime)
  - Settlement date

**SHARES_WITH**

- **Category:** ecosystem
- **Description:** Info asset is shared with an org profile

**Type-Specific Required Fields:**
- `access_level` (enum) - Allowed values: `trial`, `full`
  - Granted access level

**TRUSTS**

- **Category:** ecosystem
- **Description:** Org trusts a reputation assessment

**Type-Specific Required Fields:**
- `context` (string)
  - Context for trust decision

**USES_INSTRUMENT**

- **Category:** ecosystem
- **Description:** Deal uses a specific instrument

**Type-Specific Required Fields:**
- `version` (string)
  - Instrument version

### Level 4 (Protocol) Link Types - 20 Types

**ADAPTER_SUPPORTS**

- **Category:** artifact
- **Description:** Adapter release exposes a capability.

**Type-Specific Required Fields:**
- `latency_hint_ms` (int)
  - Latency hint in milliseconds

**APPLIES_TO**

- **Category:** protocol
- **Description:** Retention policy applies to namespace or schema.

**ASSIGNED_TO_TENANT**

- **Category:** governance
- **Description:** Associates tenant key with tenant identity.

**Type-Specific Required Fields:**
- `key_version` (int)
  - Version of key assignment

**BUNDLES**

- **Category:** artifact
- **Description:** Schema bundle contains specific schemas.

**CERTIFIES_CONFORMANCE**

- **Category:** protocol
- **Description:** Conformance result certifies a release.

**COMPATIBLE_WITH**

- **Category:** protocol
- **Description:** Declares compatibility between releases.

**Type-Specific Required Fields:**
- `level` (enum) - Allowed values: `schema`, `runtime`
  - Compatibility level
- `status` (enum) - Allowed values: `ok`, `warn`, `no`
  - Compatibility status

**DEFAULTS_FOR**

- **Category:** protocol
- **Description:** Security profile provides defaults for namespace or schema.

**DEPRECATES**

- **Category:** governance
- **Description:** Marks that one element deprecates or replaces an older one.

**Type-Specific Required Fields:**
- `grace_period_days` (int)
  - Grace period before removal

**GOVERNS**

- **Category:** protocol
- **Description:** Schema or policy governs a capability or namespace.

**Type-Specific Required Fields:**
- `governance_scope` (enum) - Allowed values: `schema`, `policy`
  - Scope of governance

**HOSTED_ON**

- **Category:** infra
- **Description:** Bus instance is hosted on a transport spec.

**IMPLEMENTS**

- **Category:** artifact
- **Description:** SDK release implements a schema or capability.

**Type-Specific Required Fields:**
- `coverage` (float)
  - Coverage ratio (0..1)

**MAPS_TO_TOPIC**

- **Category:** protocol
- **Description:** Event schema maps to a topic namespace.

**PUBLISHES_SCHEMA**

- **Category:** protocol
- **Description:** Protocol version publishes an event or envelope schema.

**Type-Specific Required Fields:**
- `release_notes_uri` (string)
  - Link to release notes

**REQUIRES_SIG**

- **Category:** protocol
- **Description:** Event schema requires a specific signature suite.

**ROUTES_OVER**

- **Category:** infra
- **Description:** Namespace or route uses a transport specification.

**SERVES_NAMESPACE**

- **Category:** infra
- **Description:** Bus instance serves a topic namespace.

**SIGNED_WITH**

- **Category:** governance
- **Description:** Tenant key uses a signature suite.

**SUPERSEDES**

- **Category:** artifact
- **Description:** New release supersedes an older release.

**Type-Specific Required Fields:**
- `compat_maintained` (boolean)
  - Whether backwards compatibility is maintained

**SUPPORTS**

- **Category:** artifact
- **Description:** Sidecar release supports a schema or transport.

**Type-Specific Required Fields:**
- `maturity` (enum) - Allowed values: `alpha`, `beta`, `ga`
  - Support maturity level

**TESTS**

- **Category:** protocol
- **Description:** Conformance suite covers specific schemas or capabilities.

---

## How to Update

**To add/modify a node or link type:**
1. Update `tools/complete_schema_data.py` with the new/modified type
2. Run `python tools/complete_schema_ingestion.py` to re-ingest to schema_registry
3. Run `python tools/generate_complete_type_reference.py --write-file` to regenerate this file

**Schema Registry Location:** FalkorDB graph `schema_registry`

**This document is auto-generated - DO NOT edit manually**
