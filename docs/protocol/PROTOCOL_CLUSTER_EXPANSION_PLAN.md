# Protocol Cluster Expansion Plan: Self-Sufficient L4

**Current State:** 35 nodes (1 SubEntity anchor + 4 Principles + 1 Process + 9 Mechanisms + 5 Interfaces + 5 Events + 7 Metrics + 3 Tasks)

**Goal:** Expand to complete self-sufficient protocol cluster with bus wiring, versioning, conformance, and governance.

---

## A) Protocol Core (Bus + Schemas) - MISSING

**Nodes to Add:**

1. **Envelope_Schema** (1 node)
   - Canonical transport envelope schema
   - Defines: `{type, id, ts, spec:{name,rev}, provenance:{scope, citizen_id?, component?, mission_id?}, sig, ...}`
   - Every event MUST conform to this envelope

2. **Event_Schema** (14 nodes)
   - Core membrane events:
     - `membrane.inject`
     - `membrane.transfer.up`
     - `membrane.transfer.down`
     - `membrane.permeability.updated`
   - Graph deltas:
     - `graph.delta.node.upsert`
     - `graph.delta.link.upsert`
   - Consciousness events:
     - `wm.emit`
     - `percept.frame`
     - `mission.completed`
   - Emergence telemetry:
     - `gap.detected`
     - `emergence.candidate`
     - `emergence.spawn`
     - `candidate.redirected`
     - `spawn.validated`
     - `membership.updated`

3. **Topic_Namespace** (3 nodes)
   - `org/{org_id}/broadcast/*`
   - `citizen/{id}/broadcast/*`
   - `org/{org_id}/proto/*` (protocol governance)

4. **Transport_Spec** (1 node)
   - WebSocket transport with QoS settings
   - `{type: "ws", qos: {durable: false, acks: true, ...}}`

5. **Bus_Instance** (1 node)
   - Concrete endpoint: `ws://localhost:8000/ws`
   - Links to Transport_Spec and Retention_Policy

6. **Retention_Policy** (1 node)
   - Dedupe window: 10 seconds
   - Time limit: 7 days
   - Size limit: 1GB

7. **Security_Profile** (1 node)
   - Required signature suites
   - Min key length: 256 bits
   - Required header paths

8. **Signature_Suite** (1 node)
   - Algorithm: ed25519
   - Pubkey encoding: base64
   - Signature field path: `$.sig.signature`

**Links to Add (8 types):**

- `MAPS_TO_TOPIC (Event_Schema → Topic_Namespace)` - 14 links
- `REQUIRES_SIG (Event_Schema → Signature_Suite)` - 14 links (all events require signatures)
- `GOVERNS (Governance_Policy → Event_Schema|Topic_Namespace)` - TBD after governance added
- `SERVES_NAMESPACE (Bus_Instance → Topic_Namespace)` - 3 links
- `ROUTES_OVER (Topic_Namespace → Transport_Spec)` - 3 links
- `APPLIES_TO (Retention_Policy → Topic_Namespace)` - 3 links
- `DEFAULTS_FOR (Security_Profile → Topic_Namespace)` - 3 links
- `REQUIRES_ENVELOPE (Event_Schema → Envelope_Schema)` - 14 links (all events use envelope)

**Total: +23 nodes, +57 links**

---

## B) Versioning & Releases - MISSING

**Nodes to Add:**

1. **Protocol_Version** (2 nodes)
   - v1.0.0 (Initial release)
   - v1.1.0 (Membrane hardening)

2. **Schema_Bundle** (2 nodes)
   - Bundle for v1.0.0 (hash of all schemas)
   - Bundle for v1.1.0 (updated schemas)

3. **SDK_Release** (3 nodes)
   - TypeScript SDK v1.0.0
   - Python SDK v1.0.0
   - Go SDK v1.0.0

4. **Sidecar_Release** (1 node)
   - Sidecar v1.0.0 (buffer_offline, replay)

5. **Compatibility_Matrix** (1 node)
   - Matrix showing SDK/Sidecar/Schema compatibility

6. **Deprecation_Notice** (0 nodes for now)
   - Add when deprecating old schemas/releases

**Links to Add (6 types):**

- `PUBLISHES_SCHEMA (Protocol_Version → Event_Schema|Envelope_Schema)` - 30 links (2 versions × 15 schemas)
- `BUNDLES (Schema_Bundle → Event_Schema)` - 28 links (2 bundles × 14 events)
- `IMPLEMENTS (SDK_Release → Event_Schema)` - 42 links (3 SDKs × 14 events)
- `SUPPORTS (Sidecar_Release → Event_Schema)` - 14 links (1 sidecar × 14 events)
- `COMPATIBLE_WITH (SDK_Release ↔ Sidecar_Release)` - 6 links (3 SDKs × 1 sidecar × 2 directions)
- `SUPERSEDES (Protocol_Version v1.1 → v1.0)` - 1 link

**Total: +9 nodes, +121 links**

---

## C) Conformance & Capabilities - MISSING

**Nodes to Add:**

1. **Capability** (10 nodes)
   - `git.commit` - Code commit capability
   - `tool.request.fetch` - Tool request capability
   - `signals.fe.error` - Frontend error signaling
   - `signals.script.log` - Script logging
   - `signals.tool.telegram` - Telegram integration
   - `membrane.inject` - Stimulus injection
   - `membrane.transfer` - Cross-level transfer
   - `graph.delta` - Graph mutation
   - `subentity.spawn` - Emergence capability
   - `mission.lifecycle` - Mission management

2. **Tool_Contract** (5 nodes)
   - Git watcher contract
   - Telegram listener contract
   - FE error collector contract
   - Logs collector contract
   - Code watcher contract

3. **Conformance_Suite** (3 nodes)
   - Membrane Events Conformance Suite
   - Emergence Events Conformance Suite
   - Graph Delta Conformance Suite

4. **Conformance_Case** (20 nodes)
   - ~5-7 cases per suite testing:
     - Valid payloads
     - Invalid payloads (missing fields)
     - Edge cases (size limits, malformed)
     - Idempotency (same ID twice)

5. **Conformance_Result** (3 nodes)
   - TypeScript SDK v1.0.0 conformance result (pass_rate: 0.95)
   - Python SDK v1.0.0 conformance result (pass_rate: 0.92)
   - Go SDK v1.0.0 conformance result (pass_rate: 0.88)

**Links to Add (3 types):**

- `TESTS (Conformance_Suite → Event_Schema)` - 42 links (3 suites × 14 events)
- `CERTIFIES_CONFORMANCE (Conformance_Result → SDK_Release)` - 3 links
- `CONFORMS_TO (SDK_Release → Event_Schema)` with evidence_uri - 42 links (3 SDKs × 14 events)

**Total: +41 nodes, +87 links**

---

## D) Governance & Identity - MISSING

**Nodes to Add:**

1. **Tenant** (1 node)
   - Mind Protocol organization
   - `{org_id: "mind-protocol", display_name: "Mind Protocol"}`

2. **Tenant_Key** (2 nodes)
   - Current key (v2)
   - Rotated key (v1, expired)

3. **Governance_Policy** (2 nodes)
   - Default policy (ack_policy: "leader", lanes: 3, backpressure: "drop_oldest")
   - Proto namespace policy (requires signatures, idempotency checks)

**Links to Add (4 types):**

- `ASSIGNED_TO_TENANT (Tenant_Key → Tenant)` - 2 links
- `SIGNED_WITH (Tenant_Key → Signature_Suite)` - 2 links
- `DEFAULTS_FOR (Security_Profile → Topic_Namespace)` - 3 links
- `GOVERNS (Governance_Policy → Topic_Namespace)` - 3 links

**Total: +5 nodes, +10 links**

---

## E) Wire Three Core Specs into Protocol - PARTIALLY DONE

**Already Have:**
- ✅ 4 Principles (Membrane-First, Single-Energy, Zero-Constants, Broadcast-Only)
- ✅ 1 Process (Seven-Step Connector Integration)
- ✅ 9 Mechanisms (7 steps + 2 learning)
- ✅ 7 Metrics

**Need to Add:**

1. **Membrane & Injection Contract** - Wire existing to new schemas
   - Link Process → Event_Schema (membrane.inject, transfer.up, transfer.down)
   - Link Metrics → Event_Schema (measure rates on actual events)

2. **Vertical Membrane Learning** - Wire mechanisms to new schemas
   - Link Mechanism (permeability_learning) → Event_Schema (membrane.permeability.updated)
   - Link Mechanism (alignment_materialization) → Event_Schema (membership.updated)

3. **SubEntity Emergence** - Add emergence pipeline process
   - **Process:** Emergence Pipeline (gap detection → coalition → validation → spawn)
   - **Mechanisms:** Gap Detection, Coalition Assembly, Engine Validation, Membership Learning
   - Link to Event_Schemas: gap.detected, emergence.candidate, emergence.spawn, candidate.redirected, spawn.validated

**Total: +1 Process, +4 Mechanisms, +40 links**

---

## F) Minimal Governance for Protocol Drift - NEW

**Nodes to Add:**

1. **Topic_Route** (2 nodes)
   - Route from `citizen/*/broadcast/*` → orchestrator
   - Route from `org/*/broadcast/*` → all engines

2. **Enhanced Governance_Policy** for `org/{org_id}/proto/*`
   - Requires: `spec:{name,rev}`, `id`, valid Envelope_Schema signature
   - Evidence caps: ≤64KB (larger via evidence_refs)
   - Idempotency: by `id`

**Links to Add:**
- `GOVERNS (Governance_Policy → Topic_Namespace: proto/*)` - 1 link
- `ROUTES_OVER (Topic_Route → Transport_Spec)` - 2 links

**Total: +2 nodes, +3 links**

---

## GRAND TOTAL

**Existing:** 35 nodes, 60 links

**Expansion:**
- A) Protocol Core: +23 nodes, +57 links
- B) Versioning: +9 nodes, +121 links
- C) Conformance: +41 nodes, +87 links
- D) Governance: +5 nodes, +10 links
- E) Wire Specs: +5 nodes (1 Process + 4 Mechanisms), +40 links
- F) Protocol Drift: +2 nodes, +3 links

**New Totals:**
- **Nodes:** 35 + 85 = **120 nodes**
- **Links:** 60 + 318 = **378 links**

---

## Implementation Priority

**Phase 1: Protocol Core (Highest Value)**
- Add Envelope_Schema + 14 Event_Schemas
- Add Topic_Namespace, Transport_Spec, Bus_Instance
- Wire with MAPS_TO_TOPIC, REQUIRES_SIG, SERVES_NAMESPACE
- **Result:** Events become queryable, namespaces defined

**Phase 2: Versioning (Immediate Need)**
- Add Protocol_Version (v1.0.0, v1.1.0)
- Add Schema_Bundle
- Wire with PUBLISHES_SCHEMA, BUNDLES
- **Result:** Protocol versions queryable, evolution trackable

**Phase 3: Governance (Safety Critical)**
- Add Tenant, Tenant_Key, Governance_Policy
- Wire with GOVERNS, ASSIGNED_TO_TENANT
- **Result:** Key rotation, policies enforceable

**Phase 4: Conformance (CI Spine)**
- Add Capability, Conformance_Suite/Case/Result
- Add SDK_Release, Sidecar_Release
- Wire with TESTS, CERTIFIES_CONFORMANCE, IMPLEMENTS
- **Result:** Self-testable protocol, CI integration

**Phase 5: Complete Spec Wiring (Full Circle)**
- Add Emergence Pipeline process + mechanisms
- Wire all mechanisms to Event_Schemas
- **Result:** Three specs fully materialized in L4

---

## Queries This Enables

```cypher
// 1. What events can TypeScript SDK v1.0.0 emit?
MATCH (sdk:SDK_Release {language: "typescript", version: "1.0.0"})-[:IMPLEMENTS]->(es:Event_Schema)
RETURN es.name, es.direction

// 2. Which namespaces require signatures?
MATCH (ns:Topic_Namespace)<-[:DEFAULTS_FOR]-(sp:Security_Profile)
WHERE size(sp.required_signature_suites) > 0
RETURN ns.pattern, sp.required_signature_suites

// 3. Is my SDK compatible with the current sidecar?
MATCH (sdk:SDK_Release {language: "python", version: "1.0.0"})-[c:COMPATIBLE_WITH]->(sc:Sidecar_Release)
RETURN sc.version, c.status

// 4. What tests does my event need to pass?
MATCH (cs:Conformance_Suite)-[:TESTS]->(es:Event_Schema {name: "membrane.inject"})
MATCH (cs)-[:CONTAINS]->(cc:Conformance_Case)
RETURN cc.case_id, cc.description, cc.expected

// 5. Which protocol version published the membrane.inject schema?
MATCH (pv:Protocol_Version)-[:PUBLISHES_SCHEMA]->(es:Event_Schema {name: "membrane.inject"})
RETURN pv.semver, pv.released_at, pv.summary

// 6. What's the governance policy for org broadcasts?
MATCH (gp:Governance_Policy)-[:GOVERNS]->(ns:Topic_Namespace {pattern: "org/{org_id}/broadcast/*"})
RETURN gp.defaults

// 7. Show the complete membrane stack protocol cluster
MATCH (n)-[:MEMBER_OF]->(proto:SubEntity {name: "proto.membrane_stack"})
RETURN labels(n), count(*)
ORDER BY count(*) DESC
```

---

## Implementation Approach

**Option 1: Manual Cypher Script (Fast)**
- Write Cypher CREATE statements for all nodes
- Write Cypher MATCH + CREATE for all links
- Run as single transaction
- **Time:** ~2-4 hours

**Option 2: Python Ingestion Script (Maintainable)**
- Extend existing `ingest_membrane_stack_protocol.py`
- Add sections for A) B) C) D) E) F)
- Parameterized data structures
- **Time:** ~4-6 hours

**Option 3: Hybrid (Recommended)**
- Quick Cypher for Phase 1 (Protocol Core) - get value fast
- Python script for Phases 2-5 - maintainable, reusable
- **Time:** ~3-5 hours total

---

## Acceptance Criteria

**Cluster Completeness:**
- ✅ All Event_Schemas have Envelope_Schema parent
- ✅ All Event_Schemas map to Topic_Namespace
- ✅ All Event_Schemas require Signature_Suite
- ✅ All Protocol_Versions publish Schema_Bundles
- ✅ All SDK_Releases implement Event_Schemas with coverage
- ✅ All Conformance_Suites test Event_Schemas
- ✅ All Topic_Namespaces have Governance_Policy
- ✅ All nodes MEMBER_OF proto.membrane_stack

**Query Tests:**
- ✅ Can query "what events does SDK X support?"
- ✅ Can query "which namespaces require sigs?"
- ✅ Can query "is SDK compatible with Sidecar?"
- ✅ Can query "what tests must event X pass?"
- ✅ Can query "which protocol version published schema Y?"
- ✅ Can query "what's the governance policy for namespace Z?"

**Conformance:**
- ✅ CI can run conformance suites against SDKs
- ✅ Results recorded in graph as Conformance_Result
- ✅ Dashboard can show pass rates per SDK/event

---

## Next Steps

1. **Choose implementation approach** (Hybrid recommended)
2. **Start with Phase 1** (Protocol Core) for immediate value
3. **Validate queries work** before proceeding to Phase 2
4. **Iterate through phases** with verification at each step
5. **Update SYNC.md** with progress

**Ready to implement?** I can start with Phase 1 (Protocol Core) now - adding Envelope_Schema, 14 Event_Schemas, Topic_Namespaces, and wiring them with the existing cluster.
