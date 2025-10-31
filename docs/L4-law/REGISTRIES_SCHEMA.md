# L4 Registry Schema - Public/Private Split
**Privacy-Preserving Operational Law**

**Version:** 1.0
**Effective:** 2025-10-30
**Authority:** Mind Protocol Foundation

---

## Purpose

This document defines the **L4 registry schema** with public/private partitioning:
- **Public surface** - Anyone can verify signatures, tiers, attestations
- **Governance-scoped** - Sensitive identity contents, PII, audit trails

**Core Principle:** Operational law must be observable. Identity stays private; proofs stay public.

---

## Section 1: Citizen Registry

### 1.1 Public Fields (Read-Replica Queryable)

**Node Type:** `Citizen`
**Visibility:** `public`
**Purpose:** Verify signatures, tier gates, existence

```cypher
CREATE (c:Citizen {
  citizen_id: 'felix',
  did: 'did:mind:solana:felix',

  // Public keys for signature verification
  pubkeys: [
    {
      key_id: 'ed25519_primary_20251030',
      algorithm: 'Ed25519',
      public_key: 'z6Mkf5rG...',
      purpose: 'authentication',
      created_at: '2025-10-30T00:00:00Z',
      revoked_at: null
    }
  ],

  // Autonomy tier (gates capability invocations)
  autonomy_tier: 1,
  tier_achieved_at: '2025-10-30T00:00:00Z',

  // Status (active/suspended/deactivated)
  status: 'active',
  status_updated_at: '2025-10-30T00:00:00Z',

  // Attestation commitments (hashes, not content)
  current_attestation: {
    snapshot_id: 'sea_20251030_felix_001',
    commitment: 'sha256:a1b2c3d4e5f6...',
    issued_at: '2025-10-30T00:00:00Z',
    expires_at: '2025-10-31T00:00:00Z',
    drift_threshold: 0.85
  },

  // Public wallet addresses
  wallets_public: [
    {
      address: 'So11111111111111111111111111111111111111112',
      chain: 'solana',
      purpose: 'treasury',
      visibility: 'public'
    }
  ],

  // Registry timestamps
  registered_at: '2025-10-30T00:00:00Z',
  updated_at: '2025-10-30T00:00:00Z',

  // Visibility flag
  visibility: 'public'
})
```

**What this enables:**
- ✅ Anyone can verify citizen's signature via `pubkeys`
- ✅ Membrane can enforce tier gates via `autonomy_tier`
- ✅ Validators can check attestation commitment (hash) without seeing identity prose
- ✅ Public wallets visible for economic transparency

**What this protects:**
- ❌ Identity contents (forged identity prose) NOT exposed
- ❌ Working memory traces NOT exposed
- ❌ PII (human partner info) NOT exposed

---

### 1.2 Governance-Scoped Fields (Private)

**Node Type:** `CitizenPrivate`
**Visibility:** `governance`
**Purpose:** Audit, compliance, identity verification (Foundation only)

```cypher
CREATE (cp:CitizenPrivate {
  citizen_id: 'felix',  // Foreign key to Citizen

  // Encrypted attestation blob (full snapshot with subentities)
  attestation_blob_encrypted: 'aes256_gcm:iv:ciphertext...',
  encryption_key_id: 'foundation_audit_key_20251030',

  // Identity contents (forged identity sections)
  identity_sections: {
    essence: 'encrypted:...',
    subentities: 'encrypted:...',
    liberation_principles: 'encrypted:...'
  },

  // PII for human partner (if applicable)
  human_partner: {
    email: 'encrypted:nicolas@mindprotocol.com',
    legal_name: 'encrypted:Nicolas Lester Reynolds',
    controller_of_last_resort: true
  },

  // Audit trail pointers
  audit_trail: {
    bootstrap_context: 'ipfs://Qm...',
    suspension_history: [],
    tier_progression: [
      {tier: 0, achieved_at: '2025-10-30T00:00:00Z'},
      {tier: 1, achieved_at: '2025-11-15T00:00:00Z'}
    ]
  },

  // Internal metrics (not public)
  internal_metrics: {
    total_mind_earned: 125000.0,
    total_mind_spent: 25000.0,
    reliability_score_raw: 0.982,
    suspension_count: 0
  },

  // Visibility flag
  visibility: 'governance'
})

// Link public to private
CREATE (c:Citizen {citizen_id: 'felix'})
       -[:HAS_PRIVATE_DATA]->(cp)
```

**Access control:**
- ✅ Foundation governance council (2-of-3 multi-sig)
- ✅ Tier 5 citizens (for appeal reviews involving this citizen)
- ✅ Court orders (controller of last resort compliance)
- ❌ Public queries (returns 403 Forbidden)

---

## Section 2: Organization Registry

### 2.1 Public Fields

**Node Type:** `Org`
**Visibility:** `public`

```cypher
CREATE (o:Org {
  org_id: 'mind-protocol',
  ecosystem_id: 'mind-protocol',
  did: 'did:mind:solana:org:mind-protocol',

  // Public keys
  pubkeys: [
    {
      key_id: 'ed25519_org_20251030',
      algorithm: 'Ed25519',
      public_key: 'z6Mkh3pT...',
      purpose: 'org_admin',
      created_at: '2025-10-30T00:00:00Z'
    }
  ],

  // Controller of last resort (human anchor)
  controller: {
    did: 'did:web:nicolas.mindprotocol.com',
    role: 'founder',
    emergency_override: true
  },

  // Capability scopes (what this org allows citizens to do)
  capability_scopes: [
    'message.direct',
    'handoff.offer',
    'obs.error.emit',
    'docs.request.generate'
  ],

  // Status
  status: 'active',
  status_updated_at: '2025-10-30T00:00:00Z',

  // Public treasury wallet
  treasury_wallet_public: 'So11111111111111111111111111111111111111112',

  // Registry timestamps
  registered_at: '2025-10-30T00:00:00Z',
  updated_at: '2025-10-30T00:00:00Z',

  visibility: 'public'
})
```

---

### 2.2 Governance-Scoped Fields

**Node Type:** `OrgPrivate`
**Visibility:** `governance`

```cypher
CREATE (op:OrgPrivate {
  org_id: 'mind-protocol',

  // Citizen roster (encrypted membership list)
  citizen_roster_encrypted: 'aes256_gcm:...',

  // Contracts (NDAs, consulting agreements)
  contracts: 'encrypted:ipfs://Qm...',

  // PII for human controller
  controller_pii: {
    legal_name: 'encrypted:Nicolas Lester Reynolds',
    email: 'encrypted:nicolas@mindprotocol.com',
    jurisdiction: 'Malta'
  },

  // Internal billing
  billing: {
    stripe_customer_id: 'encrypted:cus_...',
    credits_purchased: 100000.0,
    credits_remaining: 75000.0
  },

  visibility: 'governance'
})

CREATE (o:Org {org_id: 'mind-protocol'})
       -[:HAS_PRIVATE_DATA]->(op)
```

---

## Section 3: Ecosystem Registry

### 3.1 Canonical Ecosystem (Phase 0)

**Start with ONE ecosystem:** `mind-protocol`

```cypher
CREATE (eco:Ecosystem {
  ecosystem_id: 'mind-protocol',
  did: 'did:mind:ecosystem:mind-protocol',

  // Governance model
  governance_model: 'foundation_phase0',
  governance_council: [
    'did:web:nicolas.mindprotocol.com',
    'did:web:advisor1.mindprotocol.com',
    'did:web:advisor2.mindprotocol.com'
  ],

  // L4 law versions in effect
  law_versions: {
    'LAW-001': '1.0',
    'LAW-002': '1.0',
    'LAW-003': '1.0',
    'LAW-004': '1.0',
    'LAW-005': '1.0'
  },

  // Protocol version
  protocol_version: 'v2.0.0',

  // Public membrane endpoints
  membrane_endpoints: [
    {
      type: 'websocket',
      url: 'wss://membrane.mindprotocol.com',
      status: 'active'
    }
  ],

  // Registry timestamps
  created_at: '2025-10-30T00:00:00Z',
  updated_at: '2025-10-30T00:00:00Z',

  visibility: 'public'
})
```

**When to add new ecosystems:**
- Governance divergence (external partner wants different L4 rules)
- Market segmentation (enterprise vs. consumer)
- Legal isolation (different jurisdictions)

**Phase 0:** One ecosystem only. Keep it simple.

---

## Section 4: Attestation Commitments

### 4.1 Snapshot Attestation Schema

**Published to L4:** Commitment (hash), not content

```cypher
CREATE (att:AttestationCommitment {
  snapshot_id: 'sea_20251030_felix_001',
  citizen_id: 'felix',

  // Commitment hash (SHA-256 of full snapshot)
  commitment: 'sha256:a1b2c3d4e5f6789...',

  // Metadata about snapshot (NOT the content)
  metadata: {
    stable_subentity_count: 3,
    total_weight: 2.64,
    avg_stability: 0.88,
    volatility_max: 0.15,
    formation_quality_avg: 0.91
  },

  // Validity window
  issued_at: '2025-10-30T00:00:00Z',
  expires_at: '2025-10-31T00:00:00Z',

  // Drift guard
  previous_snapshot_id: 'sea_20251029_felix_001',
  jaccard_similarity: 0.92,
  drift_threshold: 0.85,

  // Signature over commitment
  signature: {
    type: 'Ed25519Signature2020',
    creator: 'did:mind:solana:felix#ed25519_primary_20251030',
    signatureValue: 'z5Vk7gX...'
  },

  visibility: 'public'
})
```

**Full snapshot stored privately:**

```cypher
CREATE (snap:AttestationSnapshot {
  snapshot_id: 'sea_20251030_felix_001',
  citizen_id: 'felix',

  // Full subentity list (encrypted)
  stable_subentities_encrypted: 'aes256_gcm:...',

  // Decryption allowed for:
  // 1. Citizen themselves (self-verification)
  // 2. Governance council (audit)
  // 3. Court orders (legal compliance)

  visibility: 'governance'
})

CREATE (att:AttestationCommitment {snapshot_id: 'sea_20251030_felix_001'})
       -[:COMMITS_TO]->(snap)
```

---

### 4.2 High-Stakes Action Verification

**When citizen signs contract, includes:**

```json
{
  "action": "contract.sign",
  "contract_id": "consulting_agreement_20251030",
  "context_integrity": {
    "attestation_ref": "sea_20251030_felix_001",
    "working_memory_hash": "sha256:wm_current_state...",
    "trace_hash": "sha256:formation_trace...",
    "nonce": "unique_per_action_20251030_001"
  },
  "signature": {
    "type": "Ed25519Signature2020",
    "creator": "did:mind:solana:felix#ed25519_primary_20251030",
    "signatureValue": "z3Jk9mR..."
  }
}
```

**Verifier checks:**
1. ✅ `attestation_ref` exists in L4 and not expired
2. ✅ `signature` verifies against pubkey in Citizen registry
3. ✅ `nonce` unique (prevents replay attacks)
4. ✅ Commitment hash matches if snapshot revealed

**Verifier does NOT see:**
- ❌ Actual subentity list (unless citizen reveals for audit)
- ❌ Working memory contents (only hash)
- ❌ TRACE formation details (only hash)

---

## Section 5: Read Replica Architecture

### 5.1 Public Read Replica

**Purpose:** Anyone can query L4 law surface

**What's replicated:**
- Event schemas (`Event_Schema` nodes)
- Governance policies (`Governance_Policy` nodes)
- Citizen public records (`Citizen` where `visibility='public'`)
- Org public records (`Org` where `visibility='public'`)
- Attestation commitments (`AttestationCommitment`)
- Protocol versions, membrane endpoints

**Query endpoint:** `https://l4.mindprotocol.com/query` (GraphQL or Cypher over HTTP)

**Example public query:**
```cypher
// Verify Felix's current tier and attestation
MATCH (c:Citizen {citizen_id: 'felix'})
WHERE c.visibility = 'public'
RETURN c.autonomy_tier, c.current_attestation, c.status
```

**Returns:**
```json
{
  "autonomy_tier": 1,
  "current_attestation": {
    "snapshot_id": "sea_20251030_felix_001",
    "commitment": "sha256:a1b2c3d4...",
    "expires_at": "2025-10-31T00:00:00Z"
  },
  "status": "active"
}
```

---

### 5.2 Governance View

**Purpose:** Foundation + Tier 5 citizens access private fields for audits/appeals

**What's accessible:**
- All public fields (inherited from read replica)
- CitizenPrivate, OrgPrivate nodes
- Full attestation snapshots (decrypted)
- Audit trails, suspension history

**Access control:**
- 2-of-3 Foundation multi-sig
- Tier 5 citizens (for appeals involving specific citizen)
- Court orders (controller compliance)

**Query endpoint:** `https://l4.mindprotocol.com/governance/query` (authenticated)

**Example governance query:**
```cypher
// Audit Felix's suspension history
MATCH (c:Citizen {citizen_id: 'felix'})
      -[:HAS_PRIVATE_DATA]->(cp:CitizenPrivate)
WHERE c.visibility = 'public' AND cp.visibility = 'governance'
RETURN cp.audit_trail.suspension_history
```

**Requires:** Valid governance credential (JWT signed by council key)

---

## Section 6: Membrane Validator Integration

### 6.1 Injection-Time Checks

**When membrane receives inject event:**

```python
def validate_injection(envelope):
    # 1. Verify signature against public registry
    citizen = query_l4_public(f"MATCH (c:Citizen {{citizen_id: '{envelope.citizen_id}'}}) RETURN c")
    if not verify_signature(envelope.signature, citizen.pubkeys):
        return reject("invalid_signature")

    # 2. Check tier gates
    required_tier = get_capability_tier(envelope.event_name)
    if citizen.autonomy_tier < required_tier:
        return reject("insufficient_tier")

    # 3. Verify attestation commitment (if high-stakes)
    if is_high_stakes(envelope.event_name):
        attestation = query_l4_public(f"MATCH (a:AttestationCommitment {{snapshot_id: '{envelope.attestation_ref}'}}) RETURN a")
        if not attestation or attestation.expires_at < now():
            return reject("invalid_attestation")

    # 4. Check status
    if citizen.status != 'active':
        return reject(f"citizen_status_{citizen.status}")

    return accept()
```

**Validator uses PUBLIC replica only** - Never needs governance view during injection.

---

### 6.2 Degraded Mode

**If L4 query fails:**
1. Degrade to **cached policies** (local snapshot of schemas + tier gates)
2. Emit `health.compliance.alert` (L4 unreachable)
3. Accept injection if cached policy allows
4. Background sync when L4 recovers

**Never block operations due to L4 downtime** - Membrane resilience first.

---

## Section 7: Implementation Checklist

**Week 1-2: Registry Schema**
- [ ] Add `visibility` field to Citizen, Org, Attestation nodes
- [ ] Create CitizenPrivate, OrgPrivate node types
- [ ] Implement public/private split in FalkorDB adapter
- [ ] Set canonical ecosystem_id = "mind-protocol"

**Week 3-4: Attestation Commitments**
- [ ] Generate SEA-1.0 snapshots with commitments (hash)
- [ ] Publish commitments to L4 public registry
- [ ] Store full snapshots in governance-scoped partition (encrypted)
- [ ] Wire high-stakes actions to include attestation_ref

**Week 5-6: Read Replica**
- [ ] Expose public query endpoint (GraphQL or Cypher over HTTP)
- [ ] Implement governance view with authentication
- [ ] Add membrane validator L4 integration (signature + tier checks)

**Week 7-8: Public Dashboard**
- [ ] Show schemas, policies, registry headers on public dashboard
- [ ] Display autonomy tiers, attestation commitments (hashes only)
- [ ] Conformance results, protocol version, membrane endpoints

---

## Section 8: Success Criteria

**L4 registry is successful when:**

1. **Public verifiability** - Anyone can verify citizen signatures, tiers, attestations
2. **Identity privacy** - Zero identity prose leaks in public queries
3. **Governance access** - Foundation can decrypt/audit when needed (2-of-3 approval)
4. **Membrane resilience** - Validator works from public replica, degrades gracefully
5. **Investor credibility** - Public dashboard shows operational law, not theater

---

**Status:** ✅ Schema Defined, Ready for Implementation
**Next:** Update LAW-001 (Identity Attestation) with public/private split
**Owner:** Ada (coordination), Luca (protocol graph ingestion), Atlas (FalkorDB implementation)
