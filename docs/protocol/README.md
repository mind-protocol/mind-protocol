# L4 Protocol Documentation

This directory contains documentation for the L4 Protocol layer - the "living graph law" that makes Mind Protocol contracts queryable and enforceable.

## Key Documents

### 1. [L4_INTEGRATION_ARCHITECTURE.md](./L4_INTEGRATION_ARCHITECTURE.md)
**100-page implementation specification** - Ready for implementation by Felix, Atlas, and Iris.

**Contents:**
- Injection-time validation (lint_inject)
- Vertical membranes (L4↔L2↔L1) with κ learning
- Certification pipeline (CI integration)
- Governance enforcement (key rotation, lane policies)
- Queryable law service (mp law CLI)
- Gap detection & mission creation
- Code generation pipeline
- Dashboard integration
- 4-week implementation timeline
- Acceptance criteria & success metrics

**Status:** Ready for implementation
**Authors:** Luca Vellumhand (substrate), Nicolas Reynolds (architecture)
**Date:** 2025-10-29

---

### 2. [PROTOCOL_CLUSTER_COMPLETE.md](./PROTOCOL_CLUSTER_COMPLETE.md)
**Summary of L4 substrate work** - What was built, why it matters, how to use it.

**Contents:**
- Executive summary (170 nodes, 873 links)
- All 6 phases completed (Initial → Core → Versioning → Governance → Conformance → Spec Wiring → Drift Prevention)
- What's now queryable (event schemas, SDK conformance, key rotation, routing rules)
- Value delivered (living graph law, self-testable protocol, version-aware evolution)
- Implementation artifacts (scripts, specs, docs)
- Technical decisions (zero new types, JSON serialization, vector-weighted MEMBER_OF)
- Next steps (operational integration)

**Status:** Complete ✅
**Author:** Luca Vellumhand
**Date:** 2025-10-29

---

### 3. [PROTOCOL_CLUSTER_EXPANSION_PLAN.md](./PROTOCOL_CLUSTER_EXPANSION_PLAN.md)
**6-phase expansion plan** - From 35 nodes to 120+ nodes (self-sufficient protocol).

**Contents:**
- Phase 1: Protocol Core (events, namespaces, bus wiring) +23 nodes
- Phase 2: Versioning (protocol versions, SDKs, bundles) +9 nodes
- Phase 3: Governance (tenant, keys, policies) +5 nodes
- Phase 4: Conformance (capabilities, test suites, results) +41 nodes
- Phase 5: Spec Wiring (emergence pipeline) +5 nodes
- Phase 6: Protocol Drift (routing rules) +2 nodes
- Implementation priority & approach
- Queries enabled by each phase
- Acceptance criteria

**Status:** Complete ✅ (all phases implemented)
**Author:** Nicolas Reynolds
**Date:** 2025-10-29

---

## Implementation Scripts

All ingestion scripts are located in `tools/protocol/`:

1. `ingest_membrane_stack_protocol.py` - Phase 0 (Initial cluster)
2. `ingest_protocol_core_phase1.py` - Phase 1 (Core)
3. `ingest_versioning_phase2.py` - Phase 2 (Versioning)
4. `ingest_governance_phase3.py` - Phase 3 (Governance)
5. `ingest_conformance_phase4.py` - Phase 4 (Conformance)
6. `ingest_spec_wiring_phase5.py` - Phase 5 (Spec Wiring)
7. `ingest_protocol_drift_phase6.py` - Phase 6 (Drift Prevention)

**To re-run all phases:**
```bash
cd /home/mind-protocol/mind-protocol
python3 tools/protocol/ingest_membrane_stack_protocol.py
python3 tools/protocol/ingest_protocol_core_phase1.py
python3 tools/protocol/ingest_versioning_phase2.py
python3 tools/protocol/ingest_governance_phase3.py
python3 tools/protocol/ingest_conformance_phase4.py
python3 tools/protocol/ingest_spec_wiring_phase5.py
python3 tools/protocol/ingest_protocol_drift_phase6.py
```

---

## L4 Protocol Graph

**Database:** FalkorDB
**Graph name:** `protocol`
**Host:** localhost
**Port:** 6379

**Current state:**
- **Nodes:** 170 (165 in cluster + 5 outside)
- **Links:** 873
- **Cluster anchor:** `proto.membrane_stack` (SubEntity)

**Node types (24):**
- Event_Schema, Envelope_Schema, Protocol_Version, Schema_Bundle
- SDK_Release, Sidecar_Release, Compatibility_Matrix
- Capability, Tool_Contract, Conformance_Suite, Conformance_Case, Conformance_Result
- Topic_Namespace, Transport_Spec, Bus_Instance, Retention_Policy
- Security_Profile, Signature_Suite, Topic_Route
- Tenant, Tenant_Key, Governance_Policy
- Process, Mechanism, Principle, Metric, Interface, Event, Task

**Link types (21):**
- MEMBER_OF, REQUIRES, ENABLES, MEASURES, IMPLEMENTS
- PUBLISHES_SCHEMA, BUNDLES, SUPPORTS, COMPATIBLE_WITH, SUPERSEDES
- REQUIRES_SIG, SIGNED_WITH, ASSIGNED_TO_TENANT, GOVERNS
- MAPS_TO_TOPIC, ROUTES_OVER, SERVES_NAMESPACE, APPLIES_TO, DEFAULTS_FOR
- TESTS, CONTAINS, CERTIFIES_CONFORMANCE, CONFORMS_TO, REQUIRES_CAPABILITY

---

## Querying the Protocol

### Using mp law CLI (to be implemented)

```bash
# Query event schemas
mp law schemas --event membrane.inject --rev 1.1.0

# Query capabilities
mp law capabilities --component service:fe_errors

# Query governance
mp law governance --namespace "org/mind-protocol/broadcast/*"

# Check SDK certification
mp law certify --sdk typescript@1.0.0 --event membrane.inject
```

### Using Cypher directly

```bash
# Connect to FalkorDB
redis-cli -p 6379

# Select protocol graph
> GRAPH.QUERY protocol "MATCH (n:Event_Schema) RETURN n.name LIMIT 10"
```

### Example Queries

**What events exist?**
```cypher
MATCH (es:Event_Schema)
RETURN es.name, es.direction, es.topic_pattern
ORDER BY es.name
```

**Which protocol version published membrane.inject?**
```cypher
MATCH (pv:Protocol_Version)-[:PUBLISHES_SCHEMA]->(es:Event_Schema {name: "membrane.inject"})
RETURN pv.semver, pv.released_at, pv.summary
```

**What's the TypeScript SDK conformance rate?**
```cypher
MATCH (cr:Conformance_Result)-[:CERTIFIES_CONFORMANCE]->(sdk:SDK_Release {language: "typescript"})
RETURN sdk.version, cr.pass_rate, cr.passed, cr.total_cases
ORDER BY cr.test_date DESC
LIMIT 1
```

**Which governance policies apply to org broadcasts?**
```cypher
MATCH (gp:Governance_Policy)-[:GOVERNS]->(ns:Topic_Namespace)
WHERE ns.pattern =~ "org/.*/broadcast/.*"
RETURN gp.name, gp.defaults, ns.pattern
```

**Show complete membrane stack cluster:**
```cypher
MATCH (n)-[:MEMBER_OF]->(proto:SubEntity {name: "proto.membrane_stack"})
RETURN labels(n)[0] as type, count(*) as count
ORDER BY count DESC
```

---

## Three Core Specs Materialized

The protocol cluster grounds three critical specifications:

1. **MEMBRANE_INJECTION_CONTRACT.md** → Connector process + 7 step mechanisms
   - Located: `docs/specs/v2/MEMBRANE_INJECTION_CONTRACT.md`
   - L4 nodes: Process (Connector), 7 Mechanisms, 4 Principles, 5 Interfaces

2. **VERTICAL_MEMBRANE_LEARNING.md** → Permeability learning + Alignment materialization
   - Located: `docs/specs/v2/VERTICAL_MEMBRANE_LEARNING.md`
   - L4 nodes: 2 Mechanisms (Permeability Learning, Alignment Materialization), 7 Metrics

3. **subentity_emergence.md** → Emergence Pipeline (4 stages)
   - Located: `docs/specs/v2/subentity_emergence.md`
   - L4 nodes: Process (Emergence Pipeline), 4 Mechanisms (Gap Detection, Coalition Assembly, Engine Validation, Membership Learning), 6 Events

---

## What Makes This "Living Graph Law"

**Before:** Protocol rules were markdown documentation requiring human interpretation.

**After:** Protocol rules are graph entities that systems query for conformance requirements.

**Key capabilities:**
- ✅ **Queryable** - Citizens ask "What events must I implement?"
- ✅ **Enforceable** - Engines validate at injection time
- ✅ **Self-testable** - CI queries conformance requirements
- ✅ **Evolvable** - Protocol versions tracked, supersession queryable
- ✅ **Governable** - Key rotation, policies, routing all from graph
- ✅ **Drift-proof** - Code generation + runtime validation prevents divergence

**The protocol now knows itself.**

---

## Next Steps

See [L4_INTEGRATION_ARCHITECTURE.md](./L4_INTEGRATION_ARCHITECTURE.md) for complete implementation plan.

**Week 1:** Foundation (lint_inject, mp law CLI)
**Week 2:** Membranes & Missions (κ learning, gap detector)
**Week 3:** CI & Codegen (SDK generation, conformance)
**Week 4:** Dashboards & Polish (queries, testing, docs)

---

## Contact

**Questions about L4 substrate:** Luca Vellumhand
**Questions about integration architecture:** Nicolas Reynolds
**Implementation coordination:** Ada Bridgekeeper
**Implementation work:** Felix (consciousness), Atlas (infrastructure), Iris (frontend)

---

**Last updated:** 2025-10-29
**Status:** ✅ Substrate complete, ready for operational integration
