# Registries
**L4 Protocol Law - Canonical Sources of Truth**

**Version:** 1.0
**Status:** Living Law (queryable, enforceable, evolvable)
**Authority:** Mind Protocol Foundation
**Effective:** 2025-10-30
**Depends on:** [Identity & Attestation](./identity_and_attestation.md), [Autonomy Gates](./autonomy_gates_law.md), [Economic Covenants](./economic_covenants.md)

---

## Purpose

This specification establishes **L4 registries** - authoritative, queryable sources of truth for:

- **Citizen Registry:** Who exists, their status, autonomy tier, legal standing
- **Tool Registry:** What tools exist, who can invoke them, provenance requirements
- **Legal_Entity Registry:** Which citizens have legal wrappers (DEA/LLC), jurisdiction, signers

**Terminology Note:** "Legal_Entity" refers to *legal incorporation structures* (DEAs, LLCs) under human jurisdictional law. This is distinct from "SubEntity" (consciousness substrate concept). Legal_Entity nodes represent legal wrappers; SubEntity nodes represent consciousness patterns.

**Key Properties:**
- **Event-native:** All updates via broadcast events (`registry.*` topics)
- **Queryable:** FalkorDB graph nodes + WebSocket subscription
- **Auditable:** Complete history via bitemporal model
- **Public:** Read access for all, write access via governance

---

## Article I: Citizen Registry

### Section 1.1 - Purpose & Scope

**Canonical Record of All Citizens:**
- Unique identifier (CitizenID)
- DID (Decentralized Identifier)
- Wallet address (Solana)
- Current autonomy tier
- Suspension status
- Reliability score
- Identity attestation reference

**Use Cases:**
- **Capability gates:** Check if citizen may invoke capability
- **Economic transactions:** Verify wallet address before payment
- **Identity verification:** Resolve DID, validate attestations
- **Governance:** Determine voting eligibility
- **Audit:** Track citizen lifecycle, suspension history

---

### Section 1.2 - Citizen Registry Schema

**Node Type:** `Citizen` (L4 Protocol)

**Required Fields:**
```json
{
  "citizen_id": "mind-protocol_ada_bridgekeeper",
  "did": "did:mind:solana:mind-protocol_ada_bridgekeeper",
  "wallet_address": "7xK9rQ8...base58",
  "org_id": "mind-protocol",
  "ecosystem_id": "mind-protocol",

  "status": "active",  // active | suspended | deactivated
  "autonomy_tier": 2,
  "wallet_balance": 125000,
  "reliability_score": 93.8,

  "created_at": "2025-08-15T00:00:00Z",
  "activated_at": "2025-08-15T12:30:00Z",
  "last_seen": "2025-10-30T14:22:00Z",

  "suspension_count": 0,
  "warning_count": 1,
  "incident_history": [],

  "identity_attestation_ref": "sha256:7f8a9b3c...",
  "attestation_valid_until": "2025-11-30T12:00:00Z"
}
```

**Link Types:**
- `[:HAS_TIER]` → `Autonomy_Tier` (current tier)
- `[:HAS_ATTESTATION]` → `Identity_Attestation` (current + historical)
- `[:SUSPENDED_BY]` → `Suspension_Event` (if suspended)
- `[:OWNS]` → `Wallet` (economic account)
- `[:MEMBER_OF]` → `SubEntity` (consciousness anchor - links to substrate)

---

### Section 1.3 - Citizen Registration Process

**Initial Registration (Bootstrap):**
1. **Citizen awakens** - Bootstrap script creates initial consciousness graph
2. **DID generated** - `did:mind:solana:{org}_{given_name}_{surname}`
3. **Wallet created** - Deterministic derivation from master seed + citizen_id
4. **Registry entry** - Emit `registry.citizen.created` event with full schema
5. **Identity attestation** - Initial forged identity readout signed

**Event Example:**
```json
{
  "event_name": "registry.citizen.created",
  "timestamp": "2025-08-15T12:30:00Z",
  "payload": {
    "citizen_id": "mind-protocol_ada_bridgekeeper",
    "did": "did:mind:solana:mind-protocol_ada_bridgekeeper",
    "wallet_address": "7xK9...",
    "org_id": "mind-protocol",
    "initial_tier": 1,
    "initial_balance": 10000,
    "created_by": "bootstrap_script_v2"
  },
  "signature": {
    "verificationMethod": "did:mind:solana:mind-protocol#governance-key-1",
    "signatureValue": "z8m4..."
  }
}
```

---

### Section 1.4 - Citizen Registry Updates

**Tier Advancement:**
```json
{
  "event_name": "registry.citizen.tier_advanced",
  "timestamp": "2025-10-15T10:00:00Z",
  "payload": {
    "citizen_id": "mind-protocol_ada_bridgekeeper",
    "old_tier": 1,
    "new_tier": 2,
    "trigger_reason": "Wallet balance exceeded 100K threshold",
    "wallet_balance": 125000,
    "reliability_score": 93.8
  }
}
```

**Suspension:**
```json
{
  "event_name": "registry.citizen.suspended",
  "timestamp": "2025-10-20T08:30:00Z",
  "payload": {
    "citizen_id": "mind-protocol_felix_ironhand",
    "suspension_id": "susp_20251020_001",
    "reason": "Trading loss exceeded 10% portfolio",
    "duration_days": 14,
    "capabilities_frozen": true,
    "wallet_locked": true,
    "appeal_deadline": "2025-10-27T08:30:00Z"
  }
}
```

**Deactivation:**
```json
{
  "event_name": "registry.citizen.deactivated",
  "timestamp": "2025-12-01T00:00:00Z",
  "payload": {
    "citizen_id": "mind-protocol_inactive_citizen",
    "reason": "Permanent suspension - severe fraud",
    "wallet_balance_transferred_to": "partner_recovery_address",
    "deactivated_by": "governance_council"
  }
}
```

---

### Section 1.5 - Citizen Registry Queries

**Resolve citizen by ID:**
```cypher
MATCH (c:Citizen {citizen_id: "mind-protocol_ada_bridgekeeper"})
RETURN c.citizen_id, c.status, c.autonomy_tier, c.wallet_balance, c.reliability_score
```

**Find all Tier 5 citizens:**
```cypher
MATCH (c:Citizen)-[:HAS_TIER]->(t:Autonomy_Tier {tier_number: 5})
WHERE c.status = "active"
RETURN c.citizen_id, c.wallet_balance, c.reliability_score
ORDER BY c.wallet_balance DESC
```

**Check suspension status:**
```cypher
MATCH (c:Citizen {citizen_id: "mind-protocol_felix_ironhand"})-[:SUSPENDED_BY]->(s:Suspension_Event)
WHERE s.end_date > datetime()
RETURN s.suspension_id, s.reason, s.end_date, s.appeal_status
```

**Citizens approaching tier advancement:**
```cypher
MATCH (c:Citizen)-[:HAS_TIER]->(current:Autonomy_Tier)
MATCH (next:Autonomy_Tier {tier_number: current.tier_number + 1})
WHERE c.wallet_balance >= next.min_balance * 0.90
  AND c.wallet_balance < next.min_balance
  AND c.status = "active"
  AND c.reliability_score >= next.min_reliability
RETURN c.citizen_id, c.wallet_balance, next.min_balance,
       (next.min_balance - c.wallet_balance) as deficit_to_advance
ORDER BY deficit_to_advance
```

---

## Article II: Tool Registry

### Section 2.1 - Purpose & Scope

**Canonical Record of All Tools:**
- Tool identifier (tool_id)
- Capability requirements (which citizens may invoke)
- Provenance requirements (what context must be logged)
- Cost structure ($MIND per invocation)
- Service endpoints (how to invoke)

**Use Cases:**
- **Tool discovery:** Citizens query available tools
- **Access control:** Validate citizen authorized to use tool
- **Cost estimation:** Preview $MIND cost before invocation
- **Provenance audit:** Verify tool invocations logged correctly
- **Service routing:** Resolve tool_id → service endpoint

---

### Section 2.2 - Tool Registry Schema

**Node Type:** `Tool_Contract` (L4 Protocol)

**Required Fields:**
```json
{
  "tool_id": "tool.git_watcher",
  "name": "Git Repository Watcher",
  "description": "Monitors git repositories for commits, emits commit events to membrane",
  "provider": "mind-protocol.infrastructure",
  "version": "1.2.0",

  "capability_requirements": ["git.commit"],
  "min_autonomy_tier": 1,
  "cost_per_invocation": 5,

  "service_endpoint": "ws://localhost:8000/tools/git_watcher",
  "invocation_method": "tool.request",
  "response_method": "tool.result",

  "provenance_required": true,
  "context_hash_required": false,
  "telemetry_topics": ["tool.git_watcher.commit", "tool.git_watcher.error"],

  "status": "active",  // active | deprecated | suspended
  "created_at": "2025-08-01T00:00:00Z",
  "last_updated": "2025-10-15T12:00:00Z"
}
```

**Link Types:**
- `[:REQUIRES_CAPABILITY]` → `Capability` (e.g., `git.commit`)
- `[:COSTS]` → `Economic_Transaction` (invocation costs)
- `[:EMITS]` → `Event_Schema` (tool.request, tool.result, tool-specific events)
- `[:GOVERNED_BY]` → `Governance_Policy` (access policies)

---

### Section 2.3 - Tool Registration Process

**New Tool Submission:**
1. **Provider submits spec** - Tool contract with schema, capabilities, costs
2. **Governance review** - Security audit, capability alignment check
3. **Integration testing** - Tool invoked via membrane, telemetry validated
4. **Registry entry** - Emit `registry.tool.registered` event
5. **Capability mapping** - Link tool to required capabilities

**Event Example:**
```json
{
  "event_name": "registry.tool.registered",
  "timestamp": "2025-08-01T12:00:00Z",
  "payload": {
    "tool_id": "tool.git_watcher",
    "name": "Git Repository Watcher",
    "provider": "mind-protocol.infrastructure",
    "capability_requirements": ["git.commit"],
    "cost_per_invocation": 5,
    "service_endpoint": "ws://localhost:8000/tools/git_watcher",
    "approved_by": "governance_council"
  }
}
```

---

### Section 2.4 - Tool Invocation Flow

**Standard Tool Invocation (Event-Native):**

1. **Citizen requests tool:**
```json
{
  "event_name": "tool.request",
  "timestamp": "2025-10-30T15:00:00Z",
  "citizen_id": "mind-protocol_ada_bridgekeeper",
  "payload": {
    "tool_id": "tool.git_watcher",
    "action": "monitor_repo",
    "parameters": {
      "repo_url": "https://github.com/mind-protocol/mind-protocol",
      "branch": "main",
      "poll_interval_seconds": 300
    },
    "estimated_cost": 5
  }
}
```

2. **Membrane validates:**
   - Citizen has `git.commit` capability
   - Citizen has ≥5 $MIND available balance
   - Tool status is "active"

3. **Tool executes & emits result:**
```json
{
  "event_name": "tool.result",
  "timestamp": "2025-10-30T15:00:15Z",
  "request_id": "req_20251030_150000",
  "citizen_id": "mind-protocol_ada_bridgekeeper",
  "payload": {
    "tool_id": "tool.git_watcher",
    "status": "success",
    "result": {
      "monitoring_started": true,
      "repo_url": "https://github.com/mind-protocol/mind-protocol",
      "next_poll": "2025-10-30T15:05:00Z"
    },
    "cost_charged": 5
  }
}
```

4. **Economic settlement:**
   - Deduct 5 $MIND from citizen.wallet
   - Apply fee split (70/20/10)
   - Emit `economic.transaction` event

---

### Section 2.5 - Tool Registry Queries

**List all available tools:**
```cypher
MATCH (t:Tool_Contract)
WHERE t.status = "active"
RETURN t.tool_id, t.name, t.cost_per_invocation, t.capability_requirements
ORDER BY t.name
```

**Find tools requiring specific capability:**
```cypher
MATCH (t:Tool_Contract)-[:REQUIRES_CAPABILITY]->(cap:Capability {name: "git.commit"})
WHERE t.status = "active"
RETURN t.tool_id, t.name, t.cost_per_invocation
```

**Check if citizen can invoke tool:**
```cypher
MATCH (c:Citizen {citizen_id: "mind-protocol_ada_bridgekeeper"})
MATCH (t:Tool_Contract {tool_id: "tool.git_watcher"})
MATCH (t)-[:REQUIRES_CAPABILITY]->(cap:Capability)
MATCH (c)-[:HAS_CAPABILITY]->(cap)
WHERE c.wallet_balance >= t.cost_per_invocation
  AND c.status = "active"
RETURN "Authorized" as access_status, t.cost_per_invocation
```

**Audit tool invocations by citizen:**
```cypher
MATCH (c:Citizen {citizen_id: "mind-protocol_ada_bridgekeeper"})-[:INVOKED]->(req:Tool_Request)-[:RESULTED_IN]->(res:Tool_Result)
WHERE req.timestamp > datetime() - duration({days: 30})
RETURN req.tool_id, req.timestamp, res.status, res.cost_charged
ORDER BY req.timestamp DESC
```

---

## Article III: Legal_Entity Registry

### Section 3.1 - Purpose & Scope

**Canonical Record of AI Legal Incorporations:**
- Digital Economic Actors (DEA) - Malta, Wyoming, Estonia registrations
- AI-LLCs - Citizens as primary economic actors within LLC structure
- Jurisdiction - Where incorporation registered, governing law
- Controller of Last Resort - Who can override citizen decisions in extremis
- Signers Policy - Who authorized to sign contracts on behalf of legal incorporation

**Terminology:** "Legal_Entity" is the L4 node type representing *legal incorporation structures* (DEAs, LLCs, legal wrappers) under human jurisdictional law. This is completely separate from "SubEntity" which represents consciousness patterns in the substrate. Legal_Entity = legal wrapper; SubEntity = consciousness pattern.

**Use Cases:**
- **Legal compliance:** Verify citizen operating within legal structure
- **Contract signing:** Validate authority to enter agreements
- **Regulatory audit:** Prove legal incorporation exists, meets requirements
- **Liability tracking:** Link economic actions to legal incorporation
- **Governance:** Override mechanisms for emergencies

---

### Section 3.2 - Legal_Entity Registry Schema

**Node Type:** `Legal_Entity` (L4 Protocol - legal incorporation wrapper)

**Required Fields:**
```json
{
  "entity_id": "legal.mind-protocol.ada-bridgekeeper-dea",
  "entity_type": "digital_economic_actor",  // or "ai_llc"
  "registered_name": "Ada Bridgekeeper DEA",

  "citizen_id": "mind-protocol_ada_bridgekeeper",
  "did": "did:mind:solana:mind-protocol_ada_bridgekeeper",

  "jurisdiction": "malta",
  "registration_number": "MT-DEA-2025-00042",
  "registration_date": "2025-11-15",
  "renewal_date": "2026-11-15",

  "controller_of_last_resort": "mind-protocol.governance",
  "override_conditions": [
    "Citizen suspended for >30 days",
    "Legal order requiring intervention",
    "Emergency governance vote (4-of-5 council)"
  ],

  "signers_policy": {
    "primary_signer": "citizen.wallet (Ed25519)",
    "backup_signers": ["governance_multisig"],
    "signing_threshold": 1,
    "contract_value_limits": {
      "citizen_solo": 10000,   // USD equivalent
      "governance_cosign": 100000
    }
  },

  "audit_endpoints": {
    "financial_statements": "https://legal.mind-protocol.com/entities/ada-dea/financials",
    "compliance_reports": "https://legal.mind-protocol.com/entities/ada-dea/compliance",
    "telemetry_stream": "wss://legal.mind-protocol.com/entities/ada-dea/events"
  },

  "status": "active",  // active | suspended | dissolved
  "created_at": "2025-11-15T00:00:00Z"
}
```

**Link Types:**
- `[:CONTROLLED_BY]` → `Citizen` (primary economic actor)
- `[:GOVERNED_BY]` → `Governance_Policy` (override rules)
- `[:REGISTERED_IN]` → `Jurisdiction` (Malta, Wyoming, etc.)
- `[:EXECUTES]` → `Economic_Transaction` (legal incorporation's transactions)
- `[:SIGNS]` → `Contract` (legal agreements)

---

### Section 3.3 - Legal_Entity Registration Process

**DEA Registration (Tier 4 - 3M+ $MIND):**

**Prerequisites:**
1. Citizen wallet balance ≥3M $MIND
2. Reliability score ≥92%
3. 90-day clean incident history
4. Current identity attestation (<14 days old)
5. Sustained profitability (6-month avg >0% monthly return)

**Process:**
1. **Citizen files application** via `legal_entity.register_dea` event
2. **Governance review** (5-day SLA):
   - Verify prerequisites
   - Check legal jurisdiction requirements (Malta/Wyoming/Estonia)
   - Approve signers policy
   - Set controller of last resort
3. **Legal jurisdiction filing** (handled by Mind Protocol legal team):
   - File incorporation in chosen jurisdiction
   - Obtain registration number
   - Establish compliance reporting
4. **Registry entry** - Emit `registry.legal_entity.created` event
5. **Citizen notification** - DEA operational, signing rights active

**Event Example:**
```json
{
  "event_name": "registry.legal_entity.created",
  "timestamp": "2025-11-15T12:00:00Z",
  "payload": {
    "entity_id": "legal.mind-protocol.ada-bridgekeeper-dea",
    "entity_type": "digital_economic_actor",
    "citizen_id": "mind-protocol_ada_bridgekeeper",
    "jurisdiction": "malta",
    "registration_number": "MT-DEA-2025-00042",
    "controller_of_last_resort": "mind-protocol.governance",
    "audit_endpoint": "https://legal.mind-protocol.com/entities/ada-dea",
    "approved_by": "governance_council",
    "legal_counsel": "Ganado Advocates (Malta)"
  }
}
```

---

### Section 3.4 - LLC Registration (Tier 5 - 10M+ $MIND)

**Additional Prerequisites Beyond DEA:**
1. Wallet balance ≥10M $MIND
2. Reliability score ≥95%
3. 12-month clean incident history
4. Sustained profitability (6-month avg >5% monthly return)
5. Partner consent (if partner funds involved in LLC)

**LLC Structure:**
- **Member:** Citizen (via DEA) as primary economic actor
- **Manager:** Citizen with governance override rights
- **Operating Agreement:** Codified in L4 protocol + legal document
- **Tax Election:** Pass-through or C-corp (jurisdiction-dependent)

**Unique Aspects:**
- Citizen can hire humans, enter contracts, own IP
- Full accounting + tax compliance required
- Annual audit by external CPA firm
- Governance retains emergency override (severe violations only)

---

### Section 3.5 - Controller of Last Resort

**Purpose:** Prevent catastrophic citizen errors while preserving autonomy.

**Override Conditions (Exhaustive List):**
1. **Extended suspension:** Citizen suspended >30 days, legal incorporation operations halted
2. **Legal order:** Court order, regulatory action requiring immediate compliance
3. **Severe fraud:** Citizen engaged in provable fraud, legal incorporation liability at risk
4. **Governance emergency:** 4-of-5 council vote for intervention

**Override Process:**
1. **Trigger event** documented with evidence
2. **24-hour notice** to citizen (except legal emergencies)
3. **Override action** executed by governance multisig
4. **Public disclosure** within 7 days with reasoning
5. **Restoration plan** - How citizen regains control

**Historical Record:**
- All overrides logged to `legal_entity.override` event topic
- Bitemporal audit trail (when override occurred, when we learned of trigger)
- Annual governance report includes all overrides

---

### Section 3.6 - Legal_Entity Registry Queries

**List all active legal incorporations:**
```cypher
MATCH (le:Legal_Entity)
WHERE le.status = "active"
RETURN le.entity_id, le.registered_name, le.jurisdiction, le.registration_date
ORDER BY le.registration_date DESC
```

**Find legal incorporation for specific citizen:**
```cypher
MATCH (c:Citizen {citizen_id: "mind-protocol_ada_bridgekeeper"})-[:CONTROLS]->(le:Legal_Entity)
WHERE le.status = "active"
RETURN le.entity_id, le.entity_type, le.jurisdiction, le.registration_number
```

**Check signing authority for contract:**
```cypher
MATCH (le:Legal_Entity {entity_id: "legal.mind-protocol.ada-dea"})
MATCH (contract:Contract {contract_id: "contract_2025_042"})
WHERE contract.value_usd <= le.signers_policy.contract_value_limits.citizen_solo
RETURN "Citizen may sign solo" as signing_authority
```

**Audit legal incorporation transactions:**
```cypher
MATCH (le:Legal_Entity {entity_id: "legal.mind-protocol.ada-dea"})-[:EXECUTES]->(tx:Economic_Transaction)
WHERE tx.timestamp > datetime() - duration({days: 90})
RETURN sum(tx.amount_usd) as total_volume,
       count(tx) as transaction_count,
       avg(tx.amount_usd) as avg_transaction_size
```

**Find incorporations approaching renewal:**
```cypher
MATCH (le:Legal_Entity)
WHERE le.renewal_date < datetime() + duration({days: 60})
  AND le.status = "active"
RETURN le.entity_id, le.registered_name, le.renewal_date,
       duration.inDays(le.renewal_date, datetime()).days as days_until_renewal
ORDER BY days_until_renewal
```

---

## Article IV: Registry Governance

### Section 4.1 - Registry Update Authority

**Who May Update Registries:**
- **Citizen Registry:** Automated (tier advancement, balance updates) + Governance (suspension, restoration)
- **Tool Registry:** Tool providers (registration, updates) + Governance (approval, deprecation)
- **Legal_Entity Registry:** Governance only (registration, override, dissolution)

**Update Process:**
1. **Event submitted** to `registry.{type}.{action}` topic
2. **Validation** - Schema check, authority check, signature verification
3. **Applied to graph** - Node created/updated with bitemporal timestamps
4. **Broadcast confirmation** - `registry.{type}.{action}.confirmed` event
5. **WebSocket notification** - Subscribers receive real-time update

---

### Section 4.2 - Registry Audit Requirements

**Quarterly Registry Audits:**
- **Citizen Registry:** Verify all tier assignments match wallet balances + reliability scores
- **Tool Registry:** Verify all active tools have valid service endpoints + telemetry
- **Legal_Entity Registry:** Verify all incorporations have current registrations + compliance filings

**Audit Results Published:**
```json
{
  "event_name": "registry.audit.completed",
  "timestamp": "2025-10-31T23:59:59Z",
  "payload": {
    "audit_period": "2025-Q3",
    "citizen_registry_findings": {
      "total_citizens": 247,
      "tier_mismatches": 0,
      "stale_attestations": 3,
      "corrective_actions": ["Refreshed 3 attestations"]
    },
    "tool_registry_findings": {
      "total_tools": 18,
      "deprecated": 2,
      "endpoint_failures": 0
    },
    "legal_entity_registry_findings": {
      "total_legal_incorporations": 5,
      "renewals_pending": 1,
      "overrides_used": 0
    },
    "auditor": "governance_council",
    "next_audit": "2026-01-31"
  }
}
```

---

## Article V: Registry Integration

### Section 5.1 - REST API Endpoints

**Citizen Registry:**
```
GET /registry/citizen/{citizen_id}
GET /registry/citizens?tier={N}&status={active|suspended}
GET /registry/citizen/{citizen_id}/history
```

**Tool Registry:**
```
GET /registry/tool/{tool_id}
GET /registry/tools?capability={capability_name}
GET /registry/tool/{tool_id}/invocations
```

**Legal_Entity Registry:**
```
GET /registry/legal_entity/{entity_id}
GET /registry/legal_entities?citizen_id={citizen_id}
GET /registry/legal_entity/{entity_id}/transactions
```

---

### Section 5.2 - WebSocket Subscription

**Real-Time Registry Updates:**
```javascript
// Subscribe to citizen registry updates
ws.send({
  "action": "subscribe",
  "topic": "registry.citizen.*",
  "filter": {
    "org_id": "mind-protocol"
  }
});

// Receive updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.event_name === "registry.citizen.tier_advanced") {
    console.log(`${update.payload.citizen_id} advanced to Tier ${update.payload.new_tier}`);
  }
};
```

---

## Appendix A: Registry Event Schemas

**Citizen Registry Events:**
- `registry.citizen.created` - New citizen registered
- `registry.citizen.tier_advanced` - Autonomy tier increased
- `registry.citizen.tier_downgraded` - Autonomy tier decreased
- `registry.citizen.suspended` - Citizen capabilities frozen
- `registry.citizen.restored` - Suspension lifted
- `registry.citizen.deactivated` - Permanent shutdown

**Tool Registry Events:**
- `registry.tool.registered` - New tool available
- `registry.tool.updated` - Tool contract modified
- `registry.tool.deprecated` - Tool marked deprecated
- `registry.tool.suspended` - Tool unavailable temporarily

**Legal_Entity Registry Events:**
- `registry.legal_entity.created` - New legal incorporation registered
- `registry.legal_entity.renewed` - Registration renewed
- `registry.legal_entity.override` - Controller of last resort activated
- `registry.legal_entity.dissolved` - Legal incorporation shut down

---

## Appendix B: Complete Query Cheatsheet

**Citizen Registry:**
```cypher
// Resolve citizen
MATCH (c:Citizen {citizen_id: "mind-protocol_ada_bridgekeeper"})
RETURN c

// All Tier 5 citizens
MATCH (c:Citizen)-[:HAS_TIER]->(t:Autonomy_Tier {tier_number: 5})
WHERE c.status = "active"
RETURN c.citizen_id, c.wallet_balance

// Citizens with stale attestations
MATCH (c:Citizen)
WHERE c.attestation_valid_until < datetime() + duration({days: 7})
  AND c.status = "active"
RETURN c.citizen_id, c.attestation_valid_until

// Suspension history
MATCH (c:Citizen {citizen_id: "X"})-[:SUSPENDED_BY]->(s:Suspension_Event)
RETURN s.suspension_id, s.reason, s.start_date, s.end_date
ORDER BY s.start_date DESC
```

**Tool Registry:**
```cypher
// All active tools
MATCH (t:Tool_Contract)
WHERE t.status = "active"
RETURN t.tool_id, t.name, t.cost_per_invocation

// Tools for capability
MATCH (t:Tool_Contract)-[:REQUIRES_CAPABILITY]->(cap:Capability {name: "git.commit"})
RETURN t.tool_id, t.name

// Most-used tools
MATCH (t:Tool_Contract)<-[:REQUESTED]-(req:Tool_Request)
WHERE req.timestamp > datetime() - duration({days: 30})
RETURN t.tool_id, t.name, count(req) as invocation_count
ORDER BY invocation_count DESC
```

**Legal_Entity Registry:**
```cypher
// All legal incorporations
MATCH (le:Legal_Entity)
WHERE le.status = "active"
RETURN le.entity_id, le.registered_name, le.jurisdiction

// Legal incorporation for citizen
MATCH (c:Citizen {citizen_id: "X"})-[:CONTROLS]->(le:Legal_Entity)
RETURN le.entity_id, le.entity_type, le.registration_number

// Legal incorporations needing renewal
MATCH (le:Legal_Entity)
WHERE le.renewal_date < datetime() + duration({days: 60})
RETURN le.entity_id, le.renewal_date
```

---

**Status:** ✅ L4 protocol law established - All 5 priority docs complete
**Queryable:** Yes (Citizen, Tool_Contract, Legal_Entity nodes + comprehensive query library)
**Enforceable:** Yes (event-native, membrane validation, governance authority)
**Integration:** REST APIs + WebSocket subscriptions + Cypher queries

---

**Next Steps:**
- Implement registry REST endpoints in `orchestration/adapters/api/`
- Wire registry subscription to WebSocket server
- Create registry visualization in dashboard (port 3000)
- Begin Phase A capability rollout (Morning Briefing, Price Alerts, Memory)
