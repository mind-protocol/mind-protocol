# Mind Protocol - Complete Type Reference

**Auto-generated from schema_registry (FalkorDB)**
**Last updated:** 2025-10-31 09:46:18

This is the **single source of truth** for all node and link types in the Mind Protocol consciousness infrastructure.

**Contents:**
- Part 1: Universal Node Attributes (inherited by ALL 44 node types)
- Part 2: Universal Link Attributes (inherited by ALL 23 link types)
- Part 3: Node Type Inventory (44 types with full specifications)
- Part 4: Link Type Inventory (23 types with full specifications)

---

## Part 1: Universal Node Attributes

**These attributes are inherited by ALL 33 node types.**

Every node in the consciousness graph has these base attributes in addition to its type-specific fields.

### Bitemporal Tracking

- `created_at` (datetime) - REQUIRED
  - Record creation time
- `updated_at` (datetime) - REQUIRED
  - Last mutation time
- `valid_from` (datetime) - REQUIRED
  - When this fact became true
- `valid_to` (datetime) - REQUIRED
  - When this fact ceased to be true (None = still valid)

### Core Identity

- `description` (string) - REQUIRED
  - Short summary
- `detailed_description` (string) - REQUIRED
  - Long-form explanation with examples
- `name` (string) - REQUIRED
  - Display name
- `type_name` (string) - REQUIRED
  - Canonical node class; equals primary graph label

### Level Scope

- `level` (enum) - REQUIRED - Allowed values: `L1`, `L2`, `L3`, `L4`
  - Level this node belongs to
- `scope_ref` (string) - REQUIRED
  - Anchor for this node: Citizen (L1), Org (L2), Ecosystem (L3), or 'protocol' (L4)

### Privacy Governance

- `commitments` (array) - REQUIRED
  - List of cryptographic commitments to private fields
- `policy_ref` (string) - REQUIRED
  - Governing L4 policy document
- `proof_uri` (string) - REQUIRED
  - Pointer to proof bundle (ipfs://… or l4://…)
- `visibility` (enum) - REQUIRED - Allowed values: `public`, `partners`, `governance`, `private`
  - Query visibility; default derived from level

### Provenance

- `created_by` (string) - REQUIRED
  - Agent/Service that created this node
- `substrate` (enum) - REQUIRED - Allowed values: `personal`, `organizational`, `external_web`, `external_system`
  - Where this was created

---

## Part 2: Universal Link Attributes

**These attributes are inherited by ALL 34 link types.**

Every link in the consciousness graph has these base attributes in addition to its type-specific fields.

### Bitemporal Tracking

- `created_at` (datetime) - REQUIRED
  - Record creation time
- `updated_at` (datetime) - REQUIRED
  - Last mutation time
- `valid_from` (datetime) - REQUIRED
  - When this link became true
- `valid_to` (datetime) - REQUIRED
  - When this link ceased to be true

### Consciousness Metadata

- `confidence` (float) - REQUIRED - Range: [0, 1]
  - Certainty in this connection at formation time
- `energy` (float) - REQUIRED - Range: [0, 1]
  - Receiver-computed urgency/valence at accept-time
- `forming_mindstate` (string) - REQUIRED
  - Declarative state label at formation time
- `goal` (string) - REQUIRED
  - Intent for forming this link

### Privacy Governance

- `commitments` (array) - REQUIRED
  - List of cryptographic commitments to link metadata
- `visibility` (enum) - REQUIRED - Allowed values: `public`, `partners`, `governance`, `private`
  - Visibility; default = most restrictive of the two endpoints

### Provenance

- `created_by` (string) - REQUIRED
  - Agent/Service that created this link
- `substrate` (enum) - REQUIRED - Allowed values: `personal`, `organizational`, `external_web`, `external_system`
  - Where this was created

---

## Part 3: Node Type Inventory

**Total:** 33 node types defined

### U3_ Types (Universal L1-L3) - 6 Types

**U3_Community**

- **Universality:** U3
- **Description:** Named group/community at L1–L3 (guild, working group, interest cluster).

**Type-Specific Required Fields:**
- `community_type` (enum) - Allowed values: `guild`, `working_group`, `interest`, `other`
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`
- `name` (string)
- `scope_ref` (string)

**Type-Specific Optional Fields:**
- `member_count` (integer)
- `membership_policy` (enum) - Allowed values: `open`, `invite_only`, `vetted`
- `purpose` (string)
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `dormant`, `archived`

**U3_Deal**

- **Universality:** U3
- **Description:** Generic agreement/transaction intent at L1–L3 (pre-legal; distinct from L3_Deal if you keep that specialized).

**Type-Specific Required Fields:**
- `deal_kind` (enum) - Allowed values: `trade`, `service`, `licensing`, `collaboration`
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`
- `scope_ref` (string)
- `state` (enum) - Allowed values: `Proposed`, `Confirmed`, `Settled`, `Rejected`

**Type-Specific Optional Fields:**
- `agreement_ref` (string)
- `amount_ccy` (string)
- `amount_value` (float)
- `counterparties` (array)
  - Agent/Org ids involved
- `notes` (string)
- `settlement_date` (datetime)
- `status` (enum) - Allowed values: `active`, `archived`

**U3_Pattern**

- **Universality:** U3
- **Description:** Recurring behavior at L1–L3 (habits, best/anti patterns, market/process patterns).

**Type-Specific Required Fields:**
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`
  - Pattern applies at personal (L1), org (L2), or ecosystem (L3) scope
- `pattern_type` (enum) - Allowed values: `habit`, `best_practice`, `anti_pattern`, `market_behavior`, `process_pattern`
- `scope_ref` (string)
  - Citizen/Org/Ecosystem id
- `valence` (enum) - Allowed values: `positive`, `negative`, `neutral`

**Type-Specific Optional Fields:**
- `activation_cues` (array)
  - Signals that trigger the pattern
- `decay_rate` (float)
  - How quickly pattern salience decays without reinforcement
- `evidence_refs` (array)
  - Attestations or documents that support this pattern
- `postconditions` (array)
  - What tends to follow the pattern
- `preconditions` (array)
  - Conditions that enable the pattern
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `suspended`, `archived`

**U3_Practice**

- **Universality:** U3
- **Description:** Adopted practice/standard operating procedure at L1–L3 (non-law).

**Type-Specific Required Fields:**
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`
- `name` (string)
- `scope_ref` (string)

**Type-Specific Optional Fields:**
- `intent` (string)
  - Why this practice exists
- `maturity` (enum) - Allowed values: `incipient`, `defined`, `managed`, `optimized`
- `owner_ref` (string)
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `deprecated`, `archived`
- `steps` (array)
  - High-level steps/checklist

**U3_Relationship**

- **Universality:** U3
- **Description:** Connection between agents at L1–L3 (personal/business/protocol partnerships).

**Type-Specific Required Fields:**
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`
- `relationship_type` (enum) - Allowed values: `personal`, `partnership`, `supplier`, `customer`, `counterparty`, `protocol_partnership`
- `scope_ref` (string)

**Type-Specific Optional Fields:**
- `end_date` (datetime)
- `slug` (string)
- `start_date` (datetime)
- `status` (enum) - Allowed values: `active`, `negotiating`, `suspended`, `terminated`
- `terms_ref` (string)
  - Agreement node id if formalized
- `trust_score` (float)

**U3_Risk**

- **Universality:** U3
- **Description:** Risk/threat to goals at L1–L3 (non-law).

**Type-Specific Required Fields:**
- `impact` (float) - Range: [0, 1]
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`
- `likelihood` (float) - Range: [0, 1]
- `scope_ref` (string)

**Type-Specific Optional Fields:**
- `category` (enum) - Allowed values: `technical`, `market`, `operational`, `regulatory`, `reputational`
- `mitigation_plan` (string)
- `owner_ref` (string)
  - Agent/Team responsible for mitigation
- `risk_score` (float)
  - likelihood × impact
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `mitigated`, `materialized`, `archived`

### U4_ Types (Universal L1-L4) - 16 Types

**U4_Agent**

- **Universality:** U4
- **Description:** Universal actor: human, citizen, org, DAO, or external system.

**Type-Specific Required Fields:**
- `agent_type` (enum) - Allowed values: `human`, `citizen`, `org`, `dao`, `external_system`
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `scope_ref` (string)

**Type-Specific Optional Fields:**
- `did` (string)
- `keys` (array)
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `suspended`, `archived`, `merged`, `dissolved`

**U4_Assessment**

- **Universality:** U4
- **Description:** Evaluation record (reputation/psychology/performance/security/compliance).

**Type-Specific Required Fields:**
- `assessor_ref` (string)
- `domain` (enum) - Allowed values: `reputation`, `psychology`, `performance`, `security`, `compliance`
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `scope_ref` (string)
- `score` (float)

**Type-Specific Optional Fields:**
- `method` (string)
- `scale` (string)
- `status` (enum) - Allowed values: `active`, `suspended`, `archived`

**U4_Attestation**

- **Universality:** U4
- **Description:** Cryptographic attestation (e.g., SEA identity snapshot, policy commitment).

**Type-Specific Required Fields:**
- `attestation_id` (string)
- `attestation_type` (enum) - Allowed values: `identity_snapshot`, `policy_commitment`, `contract_hash`, `capability_proof`
- `issuer` (string)
- `signature` (string)
- `timestamp` (datetime)

**Type-Specific Optional Fields:**
- `commitment` (string)
- `encryption_key_id` (string)
- `fields` (array)
- `payload_encrypted` (string)
- `revocation_ref` (string)
- `subject` (string)
- `valid_from` (datetime)
- `valid_to` (datetime)

**U4_Code_Artifact**

- **Universality:** U4
- **Description:** Source artifact (file/module) tracked for traceability.

**Type-Specific Required Fields:**
- `commit` (string)
- `hash` (string)
- `lang` (enum) - Allowed values: `py`, `ts`, `js`, `sql`, `bash`, `rust`, `go`, `other`
- `path` (string)
- `repo` (string)

**Type-Specific Optional Fields:**
- `updated_at` (datetime)

**U4_Decision**

- **Universality:** U4
- **Description:** Universal decision record at any level.

**Type-Specific Required Fields:**
- `choice` (string)
- `decider_ref` (string)
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `rationale` (string)
- `scope_ref` (string)

**Type-Specific Optional Fields:**
- `outcome_ref` (string)
- `proposal_ref` (string)
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `suspended`, `archived`, `reversed`

**U4_Doc_View**

- **Universality:** U4
- **Description:** Rendered documentation view/page.

**Type-Specific Required Fields:**
- `route` (string)
- `view_id` (string)

**Type-Specific Optional Fields:**
- `build_hash` (string)
- `renderer` (enum) - Allowed values: `next`, `static`

**U4_Event**

- **Universality:** U4
- **Description:** Universal event/happening; unifies L1 Memory & L3 Event.

**Type-Specific Required Fields:**
- `actor_ref` (string)
- `event_kind` (enum) - Allowed values: `percept`, `mission`, `market`, `incident`, `publish`, `trade`, `governance`, `healthcheck`, `decision_record`
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `scope_ref` (string)
  - Citizen/Org/Ecosystem id or 'protocol'
- `timestamp` (datetime)

**Type-Specific Optional Fields:**
- `attestation_ref` (string)
- `severity` (enum) - Allowed values: `low`, `medium`, `high`, `critical`
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `suspended`, `archived`
- `subject_refs` (array)

**U4_Goal**

- **Universality:** U4
- **Description:** Universal goal; personal, project, ecosystem, or protocol roadmap item.

**Type-Specific Required Fields:**
- `horizon` (enum) - Allowed values: `daily`, `weekly`, `monthly`, `quarterly`, `annual`, `multi_year`
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `scope_ref` (string)

**Type-Specific Optional Fields:**
- `okrs` (array)
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `suspended`, `archived`, `achieved`, `abandoned`
- `target_date` (datetime)

**U4_Knowledge_Object**

- **Universality:** U4
- **Description:** Spec/ADR/runbook/guide/reference—the canonical doc source.

**Type-Specific Required Fields:**
- `ko_id` (string)
- `ko_type` (enum) - Allowed values: `adr`, `spec`, `runbook`, `guide`, `reference`, `policy_summary`
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `scope_ref` (string)
- `uri` (string)

**Type-Specific Optional Fields:**
- `hash` (string)
- `owner` (string)
- `status` (enum) - Allowed values: `draft`, `active`, `deprecated`

**U4_Measurement**

- **Universality:** U4
- **Description:** Concrete datapoint for a metric.

**Type-Specific Required Fields:**
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `metric_ref` (string)
- `scope_ref` (string)
- `timestamp` (datetime)
- `value` (float)

**Type-Specific Optional Fields:**
- `status` (enum) - Allowed values: `active`, `archived`
- `window` (string)

**U4_Metric**

- **Universality:** U4
- **Description:** Metric definition (what/how to measure).

**Type-Specific Required Fields:**
- `definition` (string)
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `scope_ref` (string)
- `unit` (string)

**Type-Specific Optional Fields:**
- `aggregation` (enum) - Allowed values: `sum`, `avg`, `p95`, `rate`, `custom`
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `suspended`, `archived`

**U4_Public_Presence**

- **Universality:** U4
- **Description:** Public listing/presence for an org/citizen in an ecosystem.

**Type-Specific Required Fields:**
- `channels` (array)
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `scope_ref` (string)
- `visibility` (enum) - Allowed values: `public`, `partners`

**Type-Specific Optional Fields:**
- `capabilities` (array)
  - Advertised capability ids
- `route` (string)

**U4_Smart_Contract**

- **Universality:** U4
- **Description:** Smart contract reference across levels.

**Type-Specific Required Fields:**
- `blockchain` (enum) - Allowed values: `ethereum`, `solana`, `other`
- `contract_address` (string)
- `contract_type` (enum) - Allowed values: `token`, `defi`, `nft`, `governance`

**U4_Subentity**

- **Universality:** U4
- **Description:** Multi-scale neighborhood (functional role or semantic cluster). At L4 with kind='protocol-subsystem' it represents a protocol subsystem.

**Type-Specific Required Fields:**
- `kind` (enum) - Allowed values: `functional`, `semantic`, `protocol-subsystem`
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `role_or_topic` (string)
- `scope_ref` (string)

**Type-Specific Optional Fields:**
- `activation_level_runtime` (enum) - Allowed values: `dominant`, `strong`, `moderate`, `weak`, `absent`
- `centroid_embedding` (array)
- `coherence_ema` (float)
- `created_from` (enum) - Allowed values: `role_seed`, `semantic_clustering`, `co_activation`, `trace_formation`, `manual`
- `energy_runtime` (float)
- `governance_model` (enum) - Allowed values: `foundation`, `dao`, `algorithmic`, `hybrid`
- `health` (enum) - Allowed values: `healthy`, `degraded`, `failing`
- `log_weight` (float)
- `member_count` (integer)
- `notes` (string)
- `owners` (array)
- `parent_ref` (string)
- `policy_doc_uri` (string)
- `quality_score` (float)
- `sla` (string)
- `slug` (string)
- `stability_state` (enum) - Allowed values: `candidate`, `provisional`, `mature`
- `topic_coverage` (array)
- `version` (string)

**U4_Wallet_Address**

- **Universality:** U4
- **Description:** On-chain wallet address, usable at any level.

**Type-Specific Required Fields:**
- `address` (string)
- `blockchain` (enum) - Allowed values: `ethereum`, `solana`, `bitcoin`, `other`
- `wallet_type` (enum) - Allowed values: `eoa`, `contract`, `multisig`

**U4_Work_Item**

- **Universality:** U4
- **Description:** Universal work item (task/milestone/bug/ticket/mission).

**Type-Specific Required Fields:**
- `level` (enum) - Allowed values: `L1`, `L2`, `L3`, `L4`
- `priority` (enum) - Allowed values: `critical`, `high`, `medium`, `low`
- `scope_ref` (string)
- `state` (enum) - Allowed values: `todo`, `doing`, `blocked`, `done`, `canceled`
- `work_type` (enum) - Allowed values: `task`, `milestone`, `bug`, `ticket`, `mission`

**Type-Specific Optional Fields:**
- `acceptance_criteria` (string)
- `assignee_ref` (string)
- `due_date` (datetime)
- `slug` (string)
- `status` (enum) - Allowed values: `active`, `suspended`, `archived`

### L4_ Types (Protocol Law) - 11 Types

**L4_Autonomy_Tier**

- **Universality:** L4
- **Description:** Capability gating tier at protocol level.

**Type-Specific Required Fields:**
- `name` (string)
  - Human label
- `tier_number` (integer)
  - 1..5 scale

**Type-Specific Optional Fields:**
- `min_balance_mind` (float)
  - Minimum wallet balance to qualify
- `min_reliability_score` (float)
- `notes` (string)

**L4_Capability**

- **Universality:** L4
- **Description:** Named capability that policies/tiers can unlock.

**Type-Specific Required Fields:**
- `capability_id` (string)
- `description` (string)

**Type-Specific Optional Fields:**
- `risk_level` (enum) - Allowed values: `low`, `medium`, `high`

**L4_Conformance_Result**

- **Universality:** L4
- **Description:** Result of running a conformance suite.

**Type-Specific Required Fields:**
- `pass_rate` (float) - Range: [0, 1]
- `subject_ref` (string)
- `suite_id` (string)
- `ts` (datetime)

**Type-Specific Optional Fields:**
- `evidence_uri` (string)
- `failures` (array)

**L4_Conformance_Suite**

- **Universality:** L4
- **Description:** Test suite for schemas/policies/topics/signature suites.

**Type-Specific Required Fields:**
- `cases` (array)
  - List of case descriptors
- `semver` (string)
- `suite_id` (string)

**Type-Specific Optional Fields:**
- `notes` (string)
- `pass_threshold` (float)

**L4_Envelope_Schema**

- **Universality:** L4
- **Description:** Envelope shape & signing profile.

**Type-Specific Required Fields:**
- `name` (string)
- `schema_uri` (string)
- `version` (string)

**Type-Specific Optional Fields:**
- `attestation_header` (string)
- `required_headers` (array)
- `sig_suite` (string)

**L4_Event_Schema**

- **Universality:** L4
- **Description:** JSON Schema descriptor for an event payload.

**Type-Specific Required Fields:**
- `cps` (boolean)
- `requires_sig_suite` (string)
- `schema_uri` (string)
  - l4://schemas/<name>/<ver>.json
- `sea_required` (boolean)
- `version` (string)

**Type-Specific Optional Fields:**
- `bundle_id` (string)
  - Owning L4_Schema_Bundle
- `compat` (array)
  - Semver ranges compatible
- `topic` (string)
  - Concrete topic (e.g., 'presence.beacon')
- `topic_pattern` (string)
  - Wildcard topic pattern (e.g., 'telemetry.state.*')

**L4_Governance_Policy**

- **Universality:** L4
- **Description:** Law/policy text with machine-enforceable expectations.

**Type-Specific Required Fields:**
- `hash` (string)
- `policy_id` (string)
- `uri` (string)

**Type-Specific Optional Fields:**
- `status` (enum) - Allowed values: `draft`, `active`, `deprecated`
- `summary` (string)

**L4_Schema_Bundle**

- **Universality:** L4
- **Description:** Logical release bundle of schemas/policies.

**Type-Specific Required Fields:**
- `hash` (string)
  - Content address of manifest
- `semver` (string)
  - e.g., '1.0.0'
- `status` (enum) - Allowed values: `draft`, `active`, `deprecated`, `yanked`

**Type-Specific Optional Fields:**
- `changelog_uri` (string)
- `released_at` (datetime)

**L4_Signature_Suite**

- **Universality:** L4
- **Description:** Signing algorithm/profile supported by validator.

**Type-Specific Required Fields:**
- `algo` (enum) - Allowed values: `ed25519`, `secp256k1`, `rsa`
- `hash_algos` (array)
- `suite_id` (string)
  - e.g., 'SIG_ED25519_V1'

**Type-Specific Optional Fields:**
- `notes` (string)

**L4_Topic_Namespace**

- **Universality:** L4
- **Description:** Topic namespace (wildcards allowed).

**Type-Specific Required Fields:**
- `name` (string)
  - e.g., 'telemetry.state.*' or 'identity.snapshot.attest'

**Type-Specific Optional Fields:**
- `notes` (string)

**L4_Type_Index**

- **Universality:** L4
- **Description:** Catalog entry for a canonical type (U4_* / U3_* / Lx_*).

**Type-Specific Required Fields:**
- `schema_ref` (string)
  - l4://types/<type>@vN
- `status` (enum) - Allowed values: `draft`, `active`, `deprecated`
- `type_name` (string)

**Type-Specific Optional Fields:**
- `bundle_id` (string)
- `notes` (string)

---

## Part 4: Link Type Inventory

**Total:** 34 link types defined

### U3_ Link Types (Universal L1-L3) - 4 Types

**U3_IMPACTS**

- **Universality:** U3
- **Description:** Cause → Effect causal impact.

**Type-Specific Required Fields:**
- `impact_magnitude` (float) - Range: [0, 1]
- `impact_type` (enum) - Allowed values: `positive`, `negative`, `neutral`, `mixed`

**Type-Specific Optional Fields:**
- `impact_domain` (string)

**U3_MITIGATED_BY**

- **Universality:** U3
- **Description:** Risk mitigated by Control.

**Type-Specific Required Fields:**
- `mitigation_effectiveness` (float) - Range: [0, 1]
- `mitigation_type` (enum) - Allowed values: `prevents`, `reduces`, `transfers`, `accepts`

**U3_PARTICIPATES_IN**

- **Universality:** U3
- **Description:** Agent participates in Event/Community.

**Type-Specific Required Fields:**
- `participation_type` (enum) - Allowed values: `organizer`, `active_participant`, `observer`, `contributor`

**Type-Specific Optional Fields:**
- `participation_frequency` (string)

**U3_SETTLED_BY**

- **Universality:** U3
- **Description:** Dispute settled by Outcome.

**Type-Specific Required Fields:**
- `settlement_timestamp` (datetime)
- `settlement_type` (enum) - Allowed values: `consensus`, `arbitration`, `voting`, `mediation`, `ruling`

**Type-Specific Optional Fields:**
- `settlement_terms` (string)

### U4_ Link Types (Universal L1-L4) - 30 Types

**U4_ABOUT**

- **Universality:** U4
- **Description:** Content is about the subject node.

**Type-Specific Optional Fields:**
- `focus_type` (enum) - Allowed values: `primary_subject`, `secondary_mention`, `contextual_reference`

**U4_ACTIVATES**

- **Universality:** U4
- **Description:** Stimulus activates Response/Subentity.

**Type-Specific Optional Fields:**
- `activation_threshold` (float)

**U4_ALIASES**

- **Universality:** U4
- **Description:** Equivalence/alias relation.

**Type-Specific Required Fields:**
- `alias_type` (enum) - Allowed values: `synonym`, `translation`, `historical_name`, `context_specific`

**Type-Specific Optional Fields:**
- `context` (string)
  - Where this alias is used (e.g., 'community','technical_docs')

**U4_ASSIGNED_TO**

- **Universality:** U4
- **Description:** Work_Item → Agent ownership.

**Type-Specific Optional Fields:**
- `assignment_date` (datetime)
- `effort_estimate` (string)

**U4_BLOCKED_BY**

- **Universality:** U4
- **Description:** Work_Item is blocked by a dependency/issue.

**Type-Specific Required Fields:**
- `blocking_reason` (string)
- `severity` (enum) - Allowed values: `absolute`, `strong`, `partial`

**Type-Specific Optional Fields:**
- `resolution_condition` (string)

**U4_CERTIFIES_CONFORMANCE**

- **Universality:** U4
- **Description:** Suite certifies conformance for a target.

**U4_CONSUMES**

- **Universality:** U4
- **Description:** Code artifact consumes (subscribes to) a topic namespace.

**Type-Specific Optional Fields:**
- `example_topics` (array)
- `last_seen` (datetime)

**U4_CONTROLS**

- **Universality:** U4
- **Description:** Mechanism controls/regulates a Metric.

**Type-Specific Required Fields:**
- `control_type` (enum) - Allowed values: `regulates`, `optimizes`, `constrains`, `monitors`

**U4_DEPENDS_ON**

- **Universality:** U4
- **Description:** A depends on B (cannot function without).

**Type-Specific Required Fields:**
- `criticality` (enum) - Allowed values: `blocking`, `important`, `optional`
- `dependency_type` (enum) - Allowed values: `runtime`, `build_time`, `data`, `infrastructure`, `logical`

**U4_DEPRECATES**

- **Universality:** U4
- **Description:** Bundle deprecates an older bundle (non-linear).

**U4_DOCUMENTS**

- **Universality:** U4
- **Description:** Knowledge object documents a policy/schema/capability.

**Type-Specific Optional Fields:**
- `doc_role` (enum) - Allowed values: `adr`, `spec`, `runbook`, `guide`, `reference`, `policy_summary`

**U4_DRIVES**

- **Universality:** U4
- **Description:** Value/Motivation drives a Goal.

**Type-Specific Required Fields:**
- `drive_strength` (float) - Range: [0, 1]
- `drive_type` (enum) - Allowed values: `intrinsic`, `extrinsic`, `strategic`, `ethical`, `pragmatic`

**U4_EMITS**

- **Universality:** U4
- **Description:** Code artifact emits events to a topic namespace.

**Type-Specific Optional Fields:**
- `example_topics` (array)
- `last_seen` (datetime)

**U4_EVIDENCED_BY**

- **Universality:** U4
- **Description:** Claim is supported by Proof/Attestation/Document.

**Type-Specific Required Fields:**
- `confidence` (float) - Range: [0, 1]
- `evidence_type` (enum) - Allowed values: `attestation`, `measurement`, `document`, `witness`, `cryptographic_proof`

**U4_GOVERNS**

- **Universality:** U4
- **Description:** L4 subsystem governs a resource/domain.

**Type-Specific Required Fields:**
- `authority_type` (enum) - Allowed values: `policy_enforcement`, `resource_allocation`, `permission_granting`, `arbitration`
- `governance_scope` (string)

**Type-Specific Optional Fields:**
- `policy_ref` (string)
  - URI to controlling document (e.g., 'l4://law/LAW-001')

**U4_IMPLEMENTS**

- **Universality:** U4
- **Description:** Code artifact implements a policy/schema/capability.

**Type-Specific Optional Fields:**
- `evidence_rules_passed` (array)
  - mp-lint rule codes (e.g., ['R-001','R-002'])
- `last_lint_ts` (datetime)

**U4_MAPS_TO_TOPIC**

- **Universality:** U4
- **Description:** Event schema belongs to a topic namespace.

**U4_MEASURES**

- **Universality:** U4
- **Description:** Measurement measures a Metric.

**Type-Specific Optional Fields:**
- `measurement_unit` (string)

**U4_MEMBER_OF**

- **Universality:** U4
- **Description:** Child → Parent composition.

**Type-Specific Required Fields:**
- `membership_type` (enum) - Allowed values: `structural`, `functional`, `temporary`, `honorary`
  - Nature of membership
- `role` (string)
  - Role within the parent (e.g., 'frontend_team','governance_committee')

**Type-Specific Optional Fields:**
- `forming_mindstate` (string)
  - Declarative state at formation
- `since` (datetime)
  - When membership began
- `until` (datetime)
  - When membership ends (if temporary)

**U4_MERGED_INTO**

- **Universality:** U4
- **Description:** Old → New merge; lineage preservation.

**Type-Specific Required Fields:**
- `merge_reason` (string)
- `merge_timestamp` (datetime)

**Type-Specific Optional Fields:**
- `absorbed_fields` (array)
  - Which fields on old were absorbed into new

**U4_PUBLISHES_SCHEMA**

- **Universality:** U4
- **Description:** Bundle publishes a schema/type record.

**U4_REFERENCES**

- **Universality:** U4
- **Description:** Doc/Code references an external resource.

**Type-Specific Required Fields:**
- `reference_type` (enum) - Allowed values: `citation`, `dependency`, `inspiration`, `comparison`

**Type-Specific Optional Fields:**
- `uri` (string)

**U4_RELATES_TO**

- **Universality:** U4
- **Description:** Generic association; use sparingly.

**Type-Specific Required Fields:**
- `needs_refinement` (boolean)
- `relationship_strength` (enum) - Allowed values: `strong`, `moderate`, `weak`, `exploratory`

**Type-Specific Optional Fields:**
- `refinement_candidates` (array)
  - Potential more specific link types (e.g., 'U4_DEPENDS_ON','U4_DOCUMENTS')

**U4_REQUIRES_SIG**

- **Universality:** U4
- **Description:** Envelope/schema requires a signature suite.

**U4_SUPERSEDES**

- **Universality:** U4
- **Description:** New bundle supersedes old bundle.

**U4_SUPPRESSES**

- **Universality:** U4
- **Description:** Inhibitor suppresses target.

**Type-Specific Optional Fields:**
- `suppression_mechanism` (string)

**U4_TARGETS**

- **Universality:** U4
- **Description:** Goal targets a Metric/Outcome.

**Type-Specific Required Fields:**
- `success_criteria` (string)
- `target_type` (enum) - Allowed values: `state_change`, `metric_threshold`, `deliverable`, `capability`

**Type-Specific Optional Fields:**
- `target_date` (datetime)

**U4_TESTS**

- **Universality:** U4
- **Description:** Test artifact covers a policy/schema/capability.

**Type-Specific Optional Fields:**
- `last_run_ts` (datetime)
- `pass_rate` (float)
- `run_id` (string)

**U4_TRIGGERED_BY**

- **Universality:** U4
- **Description:** Event was triggered by a cause.

**Type-Specific Optional Fields:**
- `trigger_strength` (float)

**U4_UNLOCKS**

- **Universality:** U4
- **Description:** Tier/Policy grants a capability.

**Type-Specific Required Fields:**
- `capability` (string)
- `unlock_condition` (string)

**Type-Specific Optional Fields:**
- `expiration` (datetime)

---

## How to Update

**To add/modify a node or link type:**
1. Update `tools/complete_schema_data.py` with the new/modified type
2. Run `python tools/complete_schema_ingestion.py` to re-ingest to schema_registry
3. Run `python tools/generate_complete_type_reference.py --write-file` to regenerate this file

**Schema Registry Location:** FalkorDB graph `schema_registry`

**This document is auto-generated - DO NOT edit manually**
