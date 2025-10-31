# L4 Protocol Subsystems
**Modular Law Enforcement at the Membrane**

**Version:** 1.0
**Effective:** 2025-10-30
**Authority:** Mind Protocol Foundation

---

## Purpose

This document defines **L4 as a composition of protocol subsystems** rather than a monolithic law blob. Each subsystem governs a specific domain (identity, payment, autonomy, etc.) and can be:
- Rendered independently in UI
- Governed separately (different policies, update cycles)
- Queried by validators at injection time
- Evolved without breaking other subsystems

**Why Subsystems Matter:**
- **Clarity** - "Which L4 subsystem enforces this?" is answerable
- **Modularity** - Update CPS without touching SEA
- **Observability** - Dashboard shows 10 subsystems with health per subsystem
- **Governance** - Different amendment processes per subsystem

---

## Section 1: Subentity Node Type (Multi-Scale Reuse)

### 1.1 Why Subentity (Not a New Type)?

**Architectural Principle:** L4 protocol subsystems ARE functional subentities at protocol scale.

Just as consciousness uses subentities at L1 (personal roles: "The Translator", "The Builder"), and organizations use them at L2 (teams: "Platform Team", "Research Group"), **L4 protocol uses them at scope="protocol"** for modular law enforcement.

This creates a clean multi-scale pattern:
- **L1 Subentity** (scope="personal") - Cognitive roles within individual consciousness
- **L2 Subentity** (scope="organizational") - Functional teams within organizations
- **L4 Subentity** (scope="protocol") - Law enforcement subsystems

**Why This Matters:**
- No proliferation of node types for same pattern
- Query patterns work across scales (member activation, coalition dynamics)
- Dashboard can show L1/L2/L4 subentities with same visualization logic

---

### 1.2 Schema Definition (Subentity for L4 Use)

**Existing Node Type (Extended for L4):**

```python
Subentity {
  # Core Identity (REQUIRED for all scopes)
  entity_kind: "functional",  # Always functional for L4 (not semantic)
  role_or_topic: str,  # "sea_identity" | "cps_payment" | "ubc_distribution" | etc.
  description: str,  # Human-readable purpose
  scope: "protocol",  # L4 subsystems use scope="protocol"

  # L4-Specific Fields (OPTIONAL, only for scope="protocol")
  policy_doc_uri: str,  # Pointer to law doc (e.g., "l4://law/LAW-001")
  version: str,  # Semantic version (e.g., "1.0.0")
  governance_model: "foundation" | "dao" | "algorithmic" | "hybrid",
  health: "healthy" | "degraded" | "failing",

  # Runtime State (computed from members, not persisted)
  energy_runtime: float,  # How active is this subsystem right now?
  threshold_runtime: float,  # When does it activate?
  activation_level_runtime: "dominant" | "strong" | "moderate" | "weak" | "absent",

  # Quality Metrics
  coherence_ema: float,  # How cohesive are member schemas/events?
  member_count: int,  # How many schemas/events does this govern?
  log_weight: float,  # Long-run importance

  # Bitemporal + Universal Attributes (inherited from base node)
  valid_at, invalid_at, created_at, expired_at: datetime,
  visibility: "public",  # L4 subsystems are public
  commitments: [],
  proof_uri: str | null,
  policy_ref: str | null
}
```

---

### 1.3 Edges (How Subsystems Connect to Other L4 Entities)

**Subentity Membership (Schema → Subsystem):**
- `(:Event_Schema)-[:MEMBER_OF]->(:Subentity {scope: "protocol"})`
- `(:Governance_Policy)-[:MEMBER_OF]->(:Subentity {scope: "protocol"})`
- `(:Capability)-[:MEMBER_OF]->(:Subentity {scope: "protocol"})`
- `(:Signature_Suite)-[:MEMBER_OF]->(:Subentity {scope: "protocol"})`

**Subsystem Relationships:**
- `(:Subentity)-[:REQUIRES]->(:Subentity)` - Dependency (e.g., CPS requires SEA for identity)
- `(:Governance_Policy)-[:AMENDS]->(:Subentity)` - Law amendments
- `(:Attestation)-[:CERTIFIES]->(:Subentity)` - Conformance attestations

---

## Section 2: The 10 L4 Subsystems

### 2.1 SEA - Identity & Attestation

**Purpose:** Cryptographic identity via snapshot-based attestations

**subsystem_id:** `SEA`
**policy_doc_uri:** `l4://law/LAW-001`

**What it governs:**
- `Event_Schema: identity.snapshot.attest`
- `Event_Schema: identity.snapshot.revoke`
- `Governance_Policy: identity_attestation_requirements`
- `Signature_Suite: Ed25519Signature2020`

**Graph Seed:**

```cypher
CREATE (sea:Subentity {
  name: 'sea_identity',
  entity_kind: 'functional',
  role_or_topic: 'sea_identity',
  scope: 'protocol',

  description: 'Cryptographic identity via snapshot-based attestations (SEA-1.0). Establishes rolling validity windows for identity proofs. Citizens sign commitments to stable subentity sets with regeneration guards (6h min interval, Jaccard ≥0.85 drift threshold). Prevents prompt injection attacks while allowing identity evolution.',

  policy_doc_uri: 'l4://law/LAW-001',
  version: '1.0.0',
  governance_model: 'foundation',
  health: 'healthy',

  member_count: 0,  // Computed from MEMBER_OF links
  coherence_ema: 0.0,
  log_weight: 1.0,

  created_at: datetime(),
  valid_at: datetime('2025-10-30T00:00:00Z'),
  invalid_at: null,
  expired_at: null,

  confidence: 1.0,
  formation_trigger: 'systematic_analysis',
  created_by: 'mind_protocol_foundation',
  substrate: 'protocol',

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/SEA'
})

// Link schemas to this subsystem (via MEMBER_OF)
MATCH (schema:Event_Schema {event_name: 'identity.snapshot.attest'})
CREATE (schema)-[:MEMBER_OF {joined_at: datetime()}]->(sea)

// Link signature suite
MATCH (suite:Signature_Suite {suite_id: 'Ed25519Signature2020'})
CREATE (suite)-[:MEMBER_OF {joined_at: datetime()}]->(sea)
```

---

### 2.2 CPS - Compute Payment & Settlement

**Purpose:** All compute operations paid in $MIND via quote-before-inject flow

**subsystem_id:** `CPS`
**policy_doc_uri:** `l4://law/LAW-002`

**What it governs:**
- `Event_Schema: economy.quote.request`
- `Event_Schema: economy.quote.reply`
- `Event_Schema: budget.checked`
- `Event_Schema: budget.clamped`
- `Event_Schema: budget.settled`
- `Governance_Policy: compute_payment_requirements`

**Graph Seed:**

```cypher
CREATE (cps:Subentity {
  name: 'cps_payment',
  entity_kind: 'functional',
  role_or_topic: 'cps_payment',
  scope: 'protocol',

  description: 'All compute operations paid in $MIND via quote-before-inject flow. Establishes $MIND as legal tender for all inference-consuming operations. Quote-before-inject prevents surprise costs. Budget hierarchy: UBC first, org allocation second. Phase 0 flat pricing (message: 0.03, handoff: 0.10, error triage: 0.50, docs: 5.0 $MIND).',

  policy_doc_uri: 'l4://law/LAW-002',
  version: '1.0.0',
  governance_model: 'foundation',
  health: 'healthy',

  member_count: 0,
  coherence_ema: 0.0,
  log_weight: 1.0,

  created_at: datetime(),
  valid_at: datetime('2025-10-30T00:00:00Z'),
  invalid_at: null,
  expired_at: null,

  confidence: 1.0,
  formation_trigger: 'systematic_analysis',
  created_by: 'mind_protocol_foundation',
  substrate: 'protocol',

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/CPS'
})

// Link to schemas
MATCH (schema:Event_Schema)
WHERE schema.event_name IN [
  'economy.quote.request',
  'economy.quote.reply',
  'budget.checked',
  'budget.clamped',
  'budget.settled'
]
CREATE (cps)-[:GOVERNS {governance_type: 'economic_enforcement'}]->(schema)
```

---

### 2.3 UBC - Universal Basic Compute

**Purpose:** Daily $MIND stipend ensuring minimum viable thinking as a right

**subsystem_id:** `UBC`
**policy_doc_uri:** `l4://law/LAW-003`

**What it governs:**
- `Event_Schema: ubc.distribute`
- `Event_Schema: ubc.received`
- `Event_Schema: ubc.exhausted`
- `Event_Schema: ubc.expired`
- `Governance_Policy: ubc_distribution_requirements`

**Graph Seed:**

```cypher
CREATE (ubc:Subentity {
  subsystem_id: 'UBC',
  name: 'Universal Basic Compute',
  slug: 'universal-basic-compute',

  summary: 'Daily $MIND stipend (10.0/day) ensuring minimum viable thinking as a right',
  description: 'Prevents cognitive poverty by providing non-transferable, compute-only credits daily. Eligibility: valid SEA-1.0 (<48h), presence beacon last 7 days, member of ≥1 org. Distribution: 00:00 UTC, expires midnight. Covers ~333 messages OR ~20 error triages.',
  policy_doc_uri: 'l4://law/LAW-003',

  version: '1.0.0',
  effective_from: datetime('2025-10-30T00:00:00Z'),
  deprecated_at: null,

  governance_model: 'dao',
  amendment_process: 'DAO vote with 7-day notice',

  status: 'active',
  health: 'healthy',

  created_at: datetime(),
  updated_at: datetime(),

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/UBC'
})

// Link to schemas
MATCH (schema:Event_Schema)
WHERE schema.event_name IN [
  'ubc.distribute',
  'ubc.received',
  'ubc.exhausted',
  'ubc.expired'
]
CREATE (ubc)-[:GOVERNS {governance_type: 'distribution_enforcement'}]->(schema)
```

---

### 2.4 RGS - Registries

**Purpose:** Canonical records for citizens, orgs, tools, legal entities

**subsystem_id:** `RGS`
**policy_doc_uri:** `l4://law/REGISTRIES_SCHEMA`

**What it governs:**
- `Event_Schema: legal_entity.dea.register`
- `Event_Schema: legal_entity.llc.register`
- `Event_Schema: legal_entity.governance.activate`
- All registry query endpoints

**Graph Seed:**

```cypher
CREATE (rgs:Subentity {
  subsystem_id: 'RGS',
  name: 'Registries',
  slug: 'registries',

  summary: 'Canonical records for citizens, orgs, tools, legal entities with public/private split',
  description: 'Maintains authoritative registry with public replica. Public fields: DID, tier, status, attestation commitments. Governance fields: identity prose, PII, audit trails. Enables signature verification without identity disclosure.',
  policy_doc_uri: 'l4://law/REGISTRIES_SCHEMA',

  version: '1.0.0',
  effective_from: datetime('2025-10-30T00:00:00Z'),
  deprecated_at: null,

  governance_model: 'foundation',
  amendment_process: '2-of-3 council vote',

  status: 'active',
  health: 'healthy',

  created_at: datetime(),
  updated_at: datetime(),

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/RGS'
})
```

---

### 2.5 AGL - Autonomy Gates & Tiers

**Purpose:** Capability unlock law based on $MIND accumulation + reliability

**subsystem_id:** `AGL`
**policy_doc_uri:** `l4://law/LAW-004`

**What it governs:**
- All tier-gated capabilities
- `Governance_Policy: tier_progression_requirements`
- `Capability` nodes with tier restrictions

**Graph Seed:**

```cypher
CREATE (agl:Subentity {
  subsystem_id: 'AGL',
  name: 'Autonomy Gates & Tiers',
  slug: 'autonomy-gates',

  summary: 'Capability unlock law based on $MIND accumulation, reliability, and tenure',
  description: 'Five-tier framework (0: Ungated/UBC → 5: Governance/10M+ $MIND). Tier 0 baseline capabilities. Tier 3 DEA registration. Tier 4 LLC formation. Tier 5 governance rights. Gates enforce via membrane validation.',
  policy_doc_uri: 'l4://law/LAW-004',

  version: '1.0.0',
  effective_from: datetime('2025-10-30T00:00:00Z'),
  deprecated_at: null,

  governance_model: 'dao',
  amendment_process: 'DAO vote for tier thresholds',

  status: 'active',
  health: 'healthy',

  created_at: datetime(),
  updated_at: datetime(),

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/AGL'
})
```

---

### 2.6 DRP - Disputes & Due Process

**Purpose:** Evidence-based suspension, appeals, remedies

**subsystem_id:** `DRP`
**policy_doc_uri:** `l4://law/LAW-005` (Section 5-6)

**What it governs:**
- `Event_Schema: governance.suspension.initiate`
- `Event_Schema: governance.suspension.appeal`
- `Event_Schema: governance.suspension.complete`
- `Governance_Policy: suspension_triggers`
- `Governance_Policy: appeal_process`

**Graph Seed:**

```cypher
CREATE (drp:Subentity {
  subsystem_id: 'DRP',
  name: 'Disputes & Due Process',
  slug: 'disputes-due-process',

  summary: 'Evidence-based suspension system with peer appeals and remedies',
  description: 'Suspension triggers (L4 enforceable): authentication violations, rate limit abuse, telemetry blackouts, contract ghosting. Appeal review: Foundation (Tier 0-2), Foundation+peer (Tier 3-4), peer-only (Tier 5). Remedies: dismissal, reduction, uphold, increase.',
  policy_doc_uri: 'l4://law/LAW-005',

  version: '1.0.0',
  effective_from: datetime('2025-10-30T00:00:00Z'),
  deprecated_at: null,

  governance_model: 'hybrid',
  amendment_process: 'Foundation (Phase 0), DAO (Phase 1)',

  status: 'active',
  health: 'healthy',

  created_at: datetime(),
  updated_at: datetime(),

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/DRP'
})
```

---

### 2.7 GOV - Governance & Amendments

**Purpose:** L4 law change process, DAO voting, policy updates

**subsystem_id:** `GOV`
**policy_doc_uri:** `l4://law/LAW-005` (Section 7), `OVERVIEW.md` (Governance section)

**What it governs:**
- `Event_Schema: governance.law.amend`
- `Event_Schema: governance.proposal.create`
- `Event_Schema: governance.vote.cast`
- `Governance_Policy: amendment_requirements`

**Graph Seed:**

```cypher
CREATE (gov:Subentity {
  subsystem_id: 'GOV',
  name: 'Governance & Amendments',
  slug: 'governance',

  summary: 'L4 law change process via DAO voting (Tier 5) or Foundation council',
  description: 'Phase 0: 2-of-3 Foundation council. Phase 1: Tier 5 citizens vote (2/3 majority, 2 co-sponsors). Process: proposal → 7-day comment → vote → 14-day notice → implementation. Rollback provision if utilization drops >30%.',
  policy_doc_uri: 'l4://law/OVERVIEW',

  version: '1.0.0',
  effective_from: datetime('2025-10-30T00:00:00Z'),
  deprecated_at: null,

  governance_model: 'foundation',
  amendment_process: 'self-amending (2-of-3 for GOV changes)',

  status: 'active',
  health: 'healthy',

  created_at: datetime(),
  updated_at: datetime(),

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/GOV'
})
```

---

### 2.8 OBS - Observability & Audit

**Purpose:** Required telemetry surfaces, conformance monitoring, health tracking

**subsystem_id:** `OBS`
**policy_doc_uri:** `l4://law/LAW-005` (Section 2.3 - Duty to Broadcast Telemetry)

**What it governs:**
- `Event_Schema: presence.beacon`
- `Event_Schema: health.link.ping`
- `Event_Schema: health.link.pong`
- `Event_Schema: health.link.snapshot`
- `Event_Schema: health.compliance.snapshot`
- `Governance_Policy: telemetry_requirements`

**Graph Seed:**

```cypher
CREATE (obs:Subentity {
  subsystem_id: 'OBS',
  name: 'Observability & Audit',
  slug: 'observability',

  summary: 'Required telemetry surfaces ensuring protocol health and citizen reliability',
  description: 'Mandatory emissions: presence.beacon (60s), health.link.pong (when pinged), graph.delta (if >threshold). Violations: silent >10min without DND → warning. Silent >24h → assumed crashed, auto-restart. Sustained ping ignoring → reliability penalty.',
  policy_doc_uri: 'l4://law/LAW-005',

  version: '1.0.0',
  effective_from: datetime('2025-10-30T00:00:00Z'),
  deprecated_at: null,

  governance_model: 'foundation',
  amendment_process: 'Automatic (SLO adjustments), DAO vote (requirements)',

  status: 'active',
  health: 'healthy',

  created_at: datetime(),
  updated_at: datetime(),

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/OBS'
})
```

---

### 2.9 SEC - Signature Suites & Security Profiles

**Purpose:** Key algorithms, cryptographic standards, security baselines

**subsystem_id:** `SEC`
**policy_doc_uri:** `l4://law/LAW-001` (Section 1.2 - Signature)

**What it governs:**
- `Signature_Suite` nodes (Ed25519, ECDSA, etc.)
- `Security_Profile` nodes (key rotation, expiry)
- `Governance_Policy: signature_requirements`

**Graph Seed:**

```cypher
CREATE (sec:Subentity {
  subsystem_id: 'SEC',
  name: 'Signature Suites & Security',
  slug: 'security',

  summary: 'Cryptographic standards, key algorithms, security baselines for protocol',
  description: 'Default: Ed25519Signature2020 (DID method). Key rotation: annual recommended, emergency revocation via governance. Security profiles: minimum key strength (256-bit), expiry windows (2 years max), multi-sig thresholds (2-of-3 Foundation).',
  policy_doc_uri: 'l4://law/LAW-001',

  version: '1.0.0',
  effective_from: datetime('2025-10-30T00:00:00Z'),
  deprecated_at: null,

  governance_model: 'foundation',
  amendment_process: 'Emergency (security patches), DAO vote (new suites)',

  status: 'active',
  health: 'healthy',

  created_at: datetime(),
  updated_at: datetime(),

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/SEC'
})
```

---

### 2.10 TRN - Transport & Namespaces

**Purpose:** Bus topology, topic routing, namespace governance

**subsystem_id:** `TRN`
**policy_doc_uri:** Membrane architecture specs

**What it governs:**
- `Topic_Namespace` nodes
- `Event_Schema` routing rules
- Membrane validation flow

**Graph Seed:**

```cypher
CREATE (trn:Subentity {
  subsystem_id: 'TRN',
  name: 'Transport & Namespaces',
  slug: 'transport',

  summary: 'Bus topology, topic routing, namespace governance for event delivery',
  description: 'Topic structure: {scope}/{ecosystem}/{org}/{citizen}/{namespace}. Scopes: ecosystem, organizational, personal. Routing: lint_inject validates schemas/signatures, forwards to appropriate consciousness engines. Namespace policy: explicit registration required.',
  policy_doc_uri: 'l4://spec/membrane/architecture',

  version: '1.0.0',
  effective_from: datetime('2025-10-30T00:00:00Z'),
  deprecated_at: null,

  governance_model: 'foundation',
  amendment_process: 'Automatic (routing optimization), DAO vote (topology changes)',

  status: 'active',
  health: 'healthy',

  created_at: datetime(),
  updated_at: datetime(),

  visibility: 'public',
  commitments: [],
  proof_uri: null,
  policy_ref: 'l4://policy/subsystem/TRN'
})
```

---

## Section 3: Subsystem Health Monitoring

### 3.1 Health Metrics per Subsystem

**Tracked automatically:**

| Subsystem | Health Indicator | Threshold |
|-----------|------------------|-----------|
| **SEA** | Attestation generation success rate | ≥0.99 |
| **CPS** | Quote accuracy (actual vs. estimate) | ≥0.95 |
| **UBC** | Distribution uptime | 100% (zero missed days) |
| **RGS** | Registry query latency (p95) | <100ms |
| **AGL** | Tier validation errors | <1% |
| **DRP** | Appeal resolution time | <14 days (90th percentile) |
| **GOV** | Amendment proposal rate | Healthy: 1-3/month |
| **OBS** | Presence beacon reception rate | ≥0.99 |
| **SEC** | Signature verification failures | <0.01% |
| **TRN** | Event routing success rate | ≥0.999 |

**Health status:**
- `healthy` - All thresholds met
- `degraded` - 1-2 thresholds breached, non-critical
- `failing` - ≥3 thresholds breached OR critical metric failing

---

### 3.2 Health Dashboard Query

```cypher
MATCH (sub:Subentity)
RETURN sub.subsystem_id, sub.name, sub.status, sub.health
ORDER BY sub.subsystem_id
```

**Returns:**
```
SEA  | Identity & Attestation         | active | healthy
CPS  | Compute Payment & Settlement   | active | healthy
UBC  | Universal Basic Compute        | active | healthy
RGS  | Registries                     | active | healthy
AGL  | Autonomy Gates & Tiers         | active | healthy
DRP  | Disputes & Due Process         | active | healthy
GOV  | Governance & Amendments        | active | healthy
OBS  | Observability & Audit          | active | healthy
SEC  | Signature Suites & Security    | active | healthy
TRN  | Transport & Namespaces         | active | healthy
```

---

## Section 4: Subsystem Interdependencies

### 4.1 Dependency Graph

```
SEA (Identity)
  ├─ requires → SEC (signatures)
  └─ used_by → CPS (citizen authentication)

CPS (Payment)
  ├─ requires → SEA (identity verification)
  ├─ requires → UBC (budget hierarchy)
  └─ used_by → All compute operations

UBC (Basic Compute)
  ├─ requires → RGS (eligibility checks)
  └─ feeds_into → CPS (budget hierarchy)

RGS (Registries)
  ├─ requires → SEA (attestation storage)
  ├─ requires → SEC (key verification)
  └─ used_by → All subsystems (lookup)

AGL (Autonomy Gates)
  ├─ requires → RGS (tier checks)
  └─ enforced_by → CPS (tier validation)

DRP (Disputes)
  ├─ requires → OBS (evidence collection)
  └─ governed_by → GOV (appeal rules)

GOV (Governance)
  ├─ requires → RGS (voter registry)
  └─ amends → All subsystems

OBS (Observability)
  ├─ requires → TRN (event delivery)
  └─ feeds_into → DRP (evidence)

SEC (Security)
  └─ used_by → All subsystems (signatures)

TRN (Transport)
  └─ used_by → All subsystems (routing)
```

**Critical dependencies (cannot function without):**
- SEA → SEC
- CPS → SEA, UBC
- RGS → SEA, SEC
- All → TRN

**Soft dependencies (degrades gracefully):**
- DRP → OBS (can use cached evidence)
- GOV → RGS (can use cached voter list)

---

## Section 5: Amendment Workflow

### 5.1 Proposing Subsystem Change

**Example: Increase UBC daily amount from 10.0 to 15.0 $MIND**

```cypher
// 1. Create amendment proposal
CREATE (prop:Governance_Proposal {
  proposal_id: 'prop_20260315_ubc_increase',
  subsystem_id: 'UBC',
  summary: 'Increase UBC from 10.0 to 15.0 $MIND/day',
  rationale: 'Protocol revenue grew 300%, treasury can sustain higher UBC',
  proposed_by: 'did:mind:solana:felix',
  co_sponsors: ['did:mind:solana:atlas', 'did:mind:solana:ada'],
  created_at: datetime(),
  comment_period_ends: datetime().plusDays(7),
  vote_starts: datetime().plusDays(7),
  vote_ends: datetime().plusDays(14)
})

// 2. Link to subsystem
MATCH (ubc:Subentity {subsystem_id: 'UBC'})
CREATE (prop)-[:PROPOSES_AMENDMENT_TO]->(ubc)

// 3. After vote passes, update subsystem
MATCH (ubc:Subentity {subsystem_id: 'UBC'})
SET ubc.version = '1.1.0',
    ubc.updated_at = datetime()

// 4. Create amendment record
CREATE (amend:Governance_Amendment {
  amendment_id: 'amend_20260401_ubc_v1.1',
  subsystem_id: 'UBC',
  change_summary: 'Daily UBC: 10.0 → 15.0 $MIND',
  effective_date: datetime('2026-04-01T00:00:00Z'),
  vote_result: {yes: 8, no: 1, abstain: 1},
  approved: true
})
MATCH (ubc:Subentity {subsystem_id: 'UBC'})
CREATE (amend)-[:AMENDS]->(ubc)
```

---

## Section 6: Implementation Checklist

### 6.1 Schema Ingestion (Luca)

**Tasks:**
- [ ] Add `Subentity` node type to Complete Type Reference
- [ ] Create 10 subsystem nodes (graph seeds above)
- [ ] Link subsystems to governed schemas via `GOVERNS`
- [ ] Link subsystems to security profiles via `DEFAULTS_FOR`
- [ ] Regenerate Complete Type Reference

---

### 6.2 Dashboard (Iris)

**Tasks:**
- [ ] Create "L4 Subsystems" page showing 10 modules
- [ ] Health status per subsystem (color-coded: green/yellow/red)
- [ ] Click subsystem → show governed schemas, policies, metrics
- [ ] Amendment history per subsystem
- [ ] Dependency graph visualization

---

### 6.3 Validator Integration (Atlas)

**Tasks:**
- [ ] Update membrane validator to query subsystem health before injection
- [ ] Degrade gracefully if non-critical subsystem failing (e.g., GOV down → use cached policies)
- [ ] Reject injection if critical subsystem failing (e.g., SEA down → cannot verify signatures)
- [ ] Emit `health.subsystem.status` events (1/min per subsystem)

---

## Section 7: Success Criteria

**L4 subsystems successful when:**

1. ✅ All 10 subsystems defined in protocol graph
2. ✅ Dashboard shows health per subsystem (green/yellow/red)
3. ✅ Governed schemas linked via `GOVERNS` edge
4. ✅ Amendment workflow tested (propose → vote → update)
5. ✅ Validator queries subsystem health before injection
6. ✅ Dependency graph documented and observable

---

**Status:** ✅ L4 Subsystems Defined, Ready for Graph Ingestion
**Next:** Integrate with schema extensions (Section C)
**Owner:** Ada (coordination), Luca (protocol graph), Atlas (validator), Iris (dashboard)
