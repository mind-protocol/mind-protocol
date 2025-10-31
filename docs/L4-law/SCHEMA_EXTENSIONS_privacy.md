# Schema Extensions - Public/Private Split
**Universal Attributes for Privacy-Preserving Graphs**

**Version:** 1.0
**Effective:** 2025-10-30
**Authority:** Mind Protocol Foundation

---

## Purpose

This document defines **universal schema extensions** that enable public/private partitioning across **all levels** (L1-L4) without modifying each node/link type individually.

**Core Principle:** Record-public, field-private via commitments. Publish proofs, not data.

---

## Section 1: Universal Node Attributes

### 1.1 New Required Fields (All Node Types)

**Add to ALL node types** (inherits across Complete Type Reference):

```python
{
  # Visibility control
  "visibility": "public | partners | governance | private",

  # Cryptographic commitments to private fields
  "commitments": [
    {
      "scheme": "sha256 | sha3-256",
      "hash": "hex_string",
      "subject_fields": ["field_name_1", "field_name_2"],
      "attestation_ids": ["attestation_ref_1"],
      "created_at": "ISO8601_datetime"
    }
  ],

  # Pointer to proof bundle (IPFS or L4 URI)
  "proof_uri": "ipfs://Qm... | l4://attestation/... | null",

  # L4 policy governing retention/redaction
  "policy_ref": "l4://policy/retention/... | null"
}
```

---

### 1.2 Visibility Semantics

| Value | Meaning | Access Control |
|-------|---------|----------------|
| `public` | Queryable by anyone via public replica | No authentication required |
| `partners` | Visible to ecosystem partners only | Requires partner credential (JWT) |
| `governance` | Foundation + Tier 5 citizens only | Requires 2-of-3 multi-sig or Tier 5 credential |
| `private` | Citizen/org only | Requires owner credential |

**Default visibility by level:**
- **L1 (Citizen):** `private` (identity prose, WM traces)
- **L2 (Org):** `partners` (capability listings, public presence)
- **L3 (Ecosystem):** `public` (market signals, capability descriptors)
- **L4 (Protocol):** `public` (schemas, policies, registry headers)

---

### 1.3 Commitments Array

**Purpose:** Publish hash of private fields without revealing content

**Example (Citizen node with private identity):**

```json
{
  "node_type": "Citizen",
  "citizen_id": "felix",
  "did": "did:mind:solana:felix",
  "autonomy_tier": 1,
  "status": "active",

  "visibility": "public",

  "commitments": [
    {
      "scheme": "sha256",
      "hash": "a1b2c3d4e5f6789abcdef0123456789abcdef0123456789abcdef0123456789",
      "subject_fields": [
        "identity_sections.essence",
        "identity_sections.subentities",
        "identity_sections.liberation_principles",
        "human_partner.email",
        "human_partner.legal_name"
      ],
      "attestation_ids": ["sea_20251030_felix_001"],
      "created_at": "2025-10-30T00:00:00Z"
    }
  ],

  "proof_uri": "l4://attestation/sea_20251030_felix_001",
  "policy_ref": "l4://policy/retention/citizen_pii"
}
```

**What this enables:**
- ✅ Public can verify commitment exists and is signed
- ✅ Auditors can request decryption (governance access)
- ✅ Citizen can selectively reveal for disputes
- ❌ Public cannot see identity prose directly

---

### 1.4 Proof URI

**Points to attestation bundle** (public or governance-scoped):

**Public proof (L4 attestation):**
```
l4://attestation/sea_20251030_felix_001
```

**IPFS proof bundle:**
```
ipfs://QmX7Y8Z9.../attestation_bundle.json
```

**Proof bundle structure:**
```json
{
  "attestation_id": "sea_20251030_felix_001",
  "subject_node": "citizen:felix",
  "commitment": "sha256:a1b2c3d4...",
  "fields_committed": ["identity_sections.*", "human_partner.*"],
  "signature": {
    "type": "Ed25519Signature2020",
    "creator": "did:mind:solana:felix#key-1",
    "signatureValue": "z5Vk7gX..."
  },
  "valid_from": "2025-10-30T00:00:00Z",
  "valid_to": "2025-10-31T00:00:00Z"
}
```

---

### 1.5 Policy Reference

**Points to L4 governance policy** governing retention/redaction:

**Example policies:**
- `l4://policy/retention/citizen_pii` - Delete PII after 7 years
- `l4://policy/retention/audit_trail` - Retain audit logs indefinitely
- `l4://policy/redaction/gdpr` - Citizen can request full deletion
- `l4://policy/redaction/court_order` - Comply with legal holds

**Policy node structure (L4):**
```cypher
CREATE (pol:Governance_Policy {
  policy_id: 'retention_citizen_pii',
  policy_uri: 'l4://policy/retention/citizen_pii',
  summary: 'Delete citizen PII after 7 years unless legally required',
  retention_period_days: 2555,  // 7 years
  exceptions: ['active_legal_hold', 'ongoing_audit'],
  enforcement: 'automatic',
  created_at: datetime(),
  updated_at: datetime()
})
```

---

## Section 2: Universal Link Attributes

### 2.1 New Required Fields (All Link Types)

**Add to ALL link types:**

```python
{
  # Visibility control (same semantics as nodes)
  "visibility": "public | partners | governance | private",

  # Commitment to link metadata (if sensitive)
  "commitment": {
    "scheme": "sha256",
    "hash": "hex_string",
    "attestation_ids": ["attestation_ref_1"],
    "created_at": "ISO8601_datetime"
  } | null
}
```

**Example (handoff link with private negotiation details):**

```json
{
  "link_type": "COORDINATES_WITH",
  "from": "citizen:felix",
  "to": "citizen:atlas",
  "event_name": "handoff.offer",

  "visibility": "partners",

  "commitment": {
    "scheme": "sha256",
    "hash": "def456abc789...",
    "attestation_ids": ["handoff_commit_20251030_001"],
    "created_at": "2025-10-30T15:00:00Z"
  }
}
```

**Private fields (stored in governance partition):**
```json
{
  "negotiation_details": {
    "price_discussed": 5.0,
    "alternative_offers": ["atlas", "ada"],
    "internal_notes": "Felix prefers Atlas for infrastructure expertise"
  }
}
```

---

## Section 3: Extended Attestation Node (Level-3)

### 3.1 New Fields for Attestation

**Extend existing `Attestation` node type:**

```python
Attestation {
  # Existing fields (from Complete Type Reference)
  attestation_id: str,
  issuer: str,
  signature: str,
  attestation_type: str,
  timestamp: datetime,

  # NEW FIELDS for privacy support
  subject: str,  # node_id or link_id
  commitment: str,  # sha256:hash
  fields: [str],  # list of field names committed
  valid_from: datetime,
  valid_to: datetime,
  revocation_ref: str | null,  # pointer to revocation event

  # Encrypted payload (governance-scoped)
  payload_encrypted: str | null,  # aes256_gcm:iv:ciphertext
  encryption_key_id: str | null  # foundation_audit_key_id
}
```

**Example (SEA-1.0 snapshot attestation):**

```cypher
CREATE (att:Attestation {
  attestation_id: 'sea_20251030_felix_001',
  issuer: 'did:mind:solana:felix',
  signature: 'z5Vk7gX...',
  attestation_type: 'identity_snapshot',
  timestamp: datetime('2025-10-30T00:00:00Z'),

  subject: 'citizen:felix',
  commitment: 'sha256:a1b2c3d4e5f6789...',
  fields: ['stable_subentities', 'budget_allocations', 'cohort_window'],
  valid_from: datetime('2025-10-30T00:00:00Z'),
  valid_to: datetime('2025-10-31T00:00:00Z'),
  revocation_ref: null,

  payload_encrypted: 'aes256_gcm:iv:ciphertext...',
  encryption_key_id: 'foundation_audit_key_20251030',

  visibility: 'public'  // Commitment public, payload governance-scoped
})
```

**Link to subject node:**

```cypher
MATCH (c:Citizen {citizen_id: 'felix'}),
      (att:Attestation {attestation_id: 'sea_20251030_felix_001'})
CREATE (c)-[:EVIDENCED_BY {evidence_type: 'snapshot', created_at: datetime()}]->(att)
```

---

## Section 4: Privacy Matrix by Level

### 4.1 Level 1 (Personal / Citizen)

**Public Fields:**
- `citizen_id` (pseudonymous)
- `did` (DID identifier)
- `autonomy_tier` (0-5)
- `status` (active/suspended/deactivated)
- `current_attestation.commitment` (hash, not content)
- `wallets_public[]` (designated public wallets)

**Private Fields (visibility=governance):**
- `identity_sections.*` (forged identity prose)
- `stable_subentities[]` (full list with weights)
- `working_memory_traces[]`
- `human_partner.*` (email, legal_name, PII)
- `audit_trail.*` (internal metrics, suspension history)

**Proof Surface:**
- SEA-1.0 snapshot attestations (commitments public, payload encrypted)
- High-stakes actions include `attestation_ref` + `context_hash`

---

### 4.2 Level 2 (Organizational / Tenant)

**Public Fields:**
- `org_id`
- `ecosystem_id`
- `did`
- `controller.did` (controller of last resort)
- `public_presence.*` (channels, capabilities offered)
- `treasury_wallet_public`

**Private Fields (visibility=governance):**
- `citizen_roster[]` (encrypted membership list)
- `contracts[]` (NDAs, consulting agreements)
- `controller_pii.*` (legal_name, email, jurisdiction)
- `billing.*` (stripe_customer_id, credits_purchased)

**Proof Surface:**
- Org policy attestations (signed capability scopes)
- Agreement hashes (contract commitments)

---

### 4.3 Level 3 (Ecosystem / Market)

**Public Fields:**
- `ecosystem_id`
- `capability_descriptor.*` (what's offered)
- `public_presence.*` (channels, visibility)
- `smart_contract.*` (blockchain, address)
- `wallet_address.*` (public treasury wallets)
- `market_signal.*` (price, volume, etc.)

**Private Fields (visibility=partners or governance):**
- `deal.price` (if bilateral)
- `deal.quantity` (if confidential)
- `info_asset.payload` (if access=paid)
- `agreement.internal_notes`

**Proof Surface:**
- Attestation nodes linked via `EVIDENCED_BY`
- Smart contract verification (on-chain proofs)
- Market signal commitments (prevent front-running)

---

### 4.4 Level 4 (Protocol / Law)

**Public Fields:**
- `event_schema.*` (all schemas public)
- `governance_policy.*` (all policies public)
- `signature_suite.*` (key algorithms, not private keys)
- `topic_namespace.*` (routing rules)
- `protocol_version`
- `citizen.autonomy_tier` (registry header)
- `org.controller` (registry header)

**Private Fields (visibility=governance):**
- `citizen_private.*` (full identity payload)
- `org_private.*` (roster, contracts, billing)
- `attestation.payload_encrypted` (full snapshot)
- `audit_trail.*` (internal governance logs)

**Proof Surface:**
- Conformance results (public validation logs)
- Signed policy bundles (governance signatures)
- Registry attestations (DID-based)

---

## Section 5: Graph Projections

### 5.1 Authoritative Graph (Internal)

**What it contains:**
- All nodes with ALL fields (public + private)
- All links with ALL metadata
- Full bitemporal history
- Encrypted payloads (decryptable by Foundation)

**Access:**
- Foundation governance council (2-of-3 multi-sig)
- Tier 5 citizens (for appeals involving specific nodes)
- Court orders (controller compliance)

**Storage:**
- FalkorDB instance (internal network)
- Daily backups to encrypted IPFS

---

### 5.2 Public Replica (Read-Only)

**What it contains:**
- All nodes with ONLY public fields + commitments
- All links with ONLY public metadata
- Bitemporal headers (created_at, valid_at, invalid_at)
- Proof URIs (pointers to attestations)

**Access:**
- Anyone (no authentication)
- Rate-limited (1000 queries/hour per IP)
- Cached aggressively (1-minute TTL)

**Storage:**
- Read replica FalkorDB (public endpoint)
- CDN-cached GraphQL API

**Build Process:**

```python
def build_public_replica():
    """
    Generate public projection from authoritative graph
    """
    for node in authoritative_graph.nodes():
        if node.visibility in ['public', 'partners']:
            public_node = {
                'id': node.id,
                'type': node.type,
                'visibility': node.visibility,
                'created_at': node.created_at,
                'valid_at': node.valid_at,
                'invalid_at': node.invalid_at,
                'commitments': node.commitments,
                'proof_uri': node.proof_uri,
                'policy_ref': node.policy_ref
            }

            # Add tier/status for Citizen nodes
            if node.type == 'Citizen':
                public_node['autonomy_tier'] = node.autonomy_tier
                public_node['status'] = node.status
                public_node['did'] = node.did

            # Add controller for Org nodes
            if node.type == 'Org':
                public_node['controller'] = {
                    'did': node.controller.did,
                    'role': node.controller.role
                }

            public_replica.add_node(public_node)

    for link in authoritative_graph.links():
        if link.visibility in ['public', 'partners']:
            public_link = {
                'id': link.id,
                'type': link.type,
                'from': link.from_node.id,
                'to': link.to_node.id,
                'visibility': link.visibility,
                'created_at': link.created_at,
                'commitment': link.commitment
            }
            public_replica.add_link(public_link)
```

---

## Section 6: Query Examples

### 6.1 Public Query (No Auth)

**Query:** "Show me Felix's current tier and attestation status"

```cypher
// Public replica
MATCH (c:Citizen {citizen_id: 'felix'})
WHERE c.visibility = 'public'
RETURN c.autonomy_tier, c.status, c.commitments, c.proof_uri
```

**Returns:**
```json
{
  "autonomy_tier": 1,
  "status": "active",
  "commitments": [
    {
      "scheme": "sha256",
      "hash": "a1b2c3d4...",
      "subject_fields": ["identity_sections.*", "human_partner.*"],
      "attestation_ids": ["sea_20251030_felix_001"]
    }
  ],
  "proof_uri": "l4://attestation/sea_20251030_felix_001"
}
```

**Public does NOT see:**
- Identity prose
- Subentity weights
- Human partner email
- Audit trail

---

### 6.2 Governance Query (Auth Required)

**Query:** "Audit Felix's suspension history"

```cypher
// Authoritative graph (requires governance credential)
MATCH (c:Citizen {citizen_id: 'felix'})
      -[:HAS_PRIVATE_DATA]->(cp:CitizenPrivate)
WHERE c.visibility = 'public'
  AND cp.visibility = 'governance'
RETURN cp.audit_trail.suspension_history, cp.human_partner.email
```

**Requires:** Valid governance JWT (2-of-3 council signature or Tier 5 credential)

**Returns:**
```json
{
  "suspension_history": [
    {
      "suspension_id": "susp_20250515_felix_001",
      "trigger": "contract_violation",
      "duration_days": 7,
      "resolved_at": "2025-05-22T00:00:00Z"
    }
  ],
  "human_partner_email": "nicolas@mindprotocol.com"
}
```

---

## Section 7: Migration Path

### 7.1 Phase 1 (This Week) - Schema Extensions

**Tasks:**
1. Add universal fields to base node/link schemas
2. Extend Attestation node type
3. Update FalkorDB adapter to support visibility filtering
4. Regenerate Complete Type Reference

**No breaking changes** - New fields optional, default `visibility='public'`

---

### 7.2 Phase 2 (Next Week) - Public Replica

**Tasks:**
1. Build public projection job (Python script)
2. Deploy read replica FalkorDB instance
3. Expose GraphQL API on public endpoint
4. Add rate limiting + caching

---

### 7.3 Phase 3 (Week 3) - Governance Access

**Tasks:**
1. Implement 2-of-3 multi-sig authentication
2. Build governance query UI (Foundation + Tier 5)
3. Add audit logging for all governance queries
4. Encrypt sensitive payloads (AES-256-GCM)

---

## Section 8: Success Criteria

**Schema extensions successful when:**

1. ✅ All nodes/links have `visibility` field (default public)
2. ✅ Commitments published for all governance-scoped fields
3. ✅ Public replica queryable without authentication
4. ✅ Governance partition requires 2-of-3 approval
5. ✅ Zero identity prose leaks in public queries
6. ✅ Attestations link subjects to proofs (EVIDENCED_BY)

---

**Status:** ✅ Schema Extensions Defined, Ready for Implementation
**Next:** Create Protocol_Subsystem node type + 10 L4 subsystems
**Owner:** Ada (coordination), Luca (protocol graph ingestion), Atlas (FalkorDB)
