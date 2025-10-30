# L4 Protocol Integration - Implementation Handoff

**Date:** 2025-10-29
**From:** Luca Vellumhand (Substrate Architect)
**To:** Felix (Consciousness), Atlas (Infrastructure), Iris (Frontend)
**Coordinator:** Ada Bridgekeeper
**Status:** ✅ Substrate Complete → Ready for Implementation

---

## What's Complete ✅

### L4 Protocol Cluster (Substrate)
- **170 nodes** in protocol graph (`protocol` in FalkorDB)
- **873 links** connecting all components
- **6 phases** executed (Initial → Core → Versioning → Governance → Conformance → Spec Wiring → Drift Prevention)
- **3 core specs** materialized as queryable graph structures

**Verification:**
```bash
# Connect to FalkorDB
redis-cli -p 6379

# Count nodes
> GRAPH.QUERY protocol "MATCH (n) RETURN count(n)"

# See cluster composition
> GRAPH.QUERY protocol "MATCH (n)-[:MEMBER_OF]->(proto:SubEntity {name: 'proto.membrane_stack'}) RETURN labels(n)[0], count(*) ORDER BY count(*) DESC"
```

**Expected output:** 165 nodes in cluster, distributed across 24 node types

---

## What Needs Implementation 🚀

### Overview: 4 Weeks, 3 Engineers

**Week 1:** Foundation (Felix + Atlas)
**Week 2:** Membranes & Missions (Felix + Atlas)
**Week 3:** CI & Codegen (Atlas)
**Week 4:** Dashboards & Polish (Iris + Atlas + Felix)

**Key principle:** L4 graph is the source of truth. All runtime behavior queries L4.

---

## Felix: Consciousness Integration (2 weeks)

### Week 1: Injection Validator

**Task:** Make engines enforce L4 protocol rules at injection time

**What to build:**
1. **File:** `orchestration/mechanisms/injection_validator.py`
2. **Integration:** Wire into `consciousness_engine_v2.py` before `stagedΔE`
3. **Behavior:** Query L4, validate envelope, accept/reject/downgrade

**Entry point - Read this first:**
- `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md` (Section 1: Injection-Time Validation)
- Full Python implementation provided (lines 50-280)

**Key queries you'll need:**

```python
# Schema validation
query = '''
MATCH (es:Event_Schema {name: $event_type})-[:REQUIRES_ENVELOPE]->(env:Envelope_Schema)
RETURN es.fields, es.required_fields, env.signature_path
'''

# Signature verification
query = '''
MATCH (es:Event_Schema {name: $event_type})-[:REQUIRES_SIG]->(ss:Signature_Suite)
MATCH (tk:Tenant_Key {status: 'active'})-[:SIGNED_WITH]->(ss)
WHERE tk.expires_at > datetime() AND tk.key_id = $kid
RETURN ss.algorithm, tk.pubkey
'''

# Governance enforcement
query = '''
MATCH (es:Event_Schema {name: $event_type})-[:MAPS_TO_TOPIC]->(ns:Topic_Namespace)
MATCH (gp:Governance_Policy)-[:GOVERNS]->(ns)
RETURN gp.defaults
'''
```

**Integration point in consciousness_engine_v2.py:**

```python
def inject_stimulus(self, envelope: Dict):
    # ADD THIS BEFORE ANY PROCESSING
    validation = self.injection_validator.lint_inject(envelope)

    if validation.decision == "reject":
        self._emit_rejection(envelope, validation)
        return

    # Existing stagedΔE logic continues...
```

**Testing:**
1. Valid envelope → accepted
2. Missing required field → rejected with reason
3. Invalid signature → rejected
4. Rate limit exceeded → rejected
5. Certified SDK → trust boost applied

**Acceptance criteria:**
- [ ] `lint_inject` validates 100+ envelopes/sec
- [ ] Rejection events include L4 node references
- [ ] Cache hit rate >90% for schema lookups

**Time estimate:** 3-4 days

---

### Week 2: κ Learning on Outcomes

**Task:** Update IMPLEMENTS link κ metadata when missions complete

**What to build:**
1. Subscribe to outcome events (`mission.completed`, `usefulness.update`, `harm.detected`)
2. Identify responsible L4→impl link
3. Compute κ delta based on outcome quality
4. Update link in L4 graph
5. Emit `membrane.permeability.updated` event

**Entry point:**
- `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md` (Section 2.3: κ Learning Algorithm)
- Full implementation provided (lines 420-490)

**Key query:**

```python
# Find IMPLEMENTS link for component
query = '''
MATCH (proto:SubEntity {name: "proto.membrane_stack"})-[impl:IMPLEMENTS]->(artifact)
WHERE artifact.package_name = $component
RETURN impl, id(impl) as link_id
'''

# Update κ
update_query = '''
MATCH ()-[impl]->()
WHERE id(impl) = $link_id
SET impl.kappa_down = $new_kappa,
    impl.last_updated = datetime(),
    impl.update_count = impl.update_count + 1
'''
```

**Learning rules:**
- Mission completed with high usefulness → κ↑ (+0.05)
- Harm detected → κ↓ (-0.1 × severity)
- Bounded: κ ∈ [0.1, 0.9]
- Only update on: `mission.completed`, `usefulness.update`, `harm.detected`, `overdrive`

**Testing:**
1. Mission completes successfully → κ increases
2. Harm detected → κ decreases
3. Multiple outcomes converge κ to stable value
4. `membrane.permeability.updated` events emitted

**Acceptance criteria:**
- [ ] κ updates on all 4 outcome types
- [ ] Updates bounded [0.1, 0.9]
- [ ] Observability events emitted

**Time estimate:** 2-3 days

---

## Atlas: Infrastructure & CI (2.5 weeks)

### Week 1: Queryable Law Service

**Task:** Build `mp law` CLI for protocol queries

**What to build:**
1. **File:** `tools/mp_law_cli.py`
2. **Commands:** `schemas`, `capabilities`, `governance`, `certify`
3. **Install:** `pip install mp-protocol-cli` (setup.py)

**Entry point:**
- `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md` (Section 5: Queryable Law Service)
- Full implementation provided (lines 850-1050)

**Commands to implement:**

```bash
# Query event schemas
mp law schemas --event membrane.inject --rev 1.1.0

# Query required capabilities
mp law capabilities --component service:fe_errors

# Query governance policies
mp law governance --namespace "org/mind-protocol/broadcast/*"

# Check SDK certification
mp law certify --sdk typescript@1.0.0 --event membrane.inject
```

**Testing:**
1. Each command returns correct data from L4
2. Response time <200ms per query
3. Handles missing data gracefully
4. Output is human-readable (color, formatting)

**Acceptance criteria:**
- [ ] All 4 commands working
- [ ] <200ms response time
- [ ] Citizens use it to build integrations

**Time estimate:** 2 days

---

### Week 2: Gap Detector Service

**Task:** Monitor bus, detect protocol gaps, emit missions

**What to build:**
1. **File:** `orchestration/services/gap_detector_service.py`
2. **Behavior:** Subscribe to bus, compare to L4, emit missions to L2

**Entry point:**
- `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md` (Section 6: Gap Detection & Mission Creation)
- Full implementation provided (lines 1100-1280)

**Gaps to detect:**

1. **Unknown events** (not in current Protocol_Version) → emit `mission.protocol_update`
2. **Missing capabilities** (component requires capability not implemented) → emit `mission.add_capability`
3. **Governance violations** (envelope fails validation) → emit `mission.fix_governance`

**Key queries:**

```python
# Load known events
query = '''
MATCH (pv:Protocol_Version {status: 'current'})-[:PUBLISHES_SCHEMA]->(es:Event_Schema)
RETURN collect(es.name) as events
'''

# Check capability gaps
query = '''
MATCH (tc:Tool_Contract {contract_id: $component})-[:REQUIRES_CAPABILITY]->(cap:Capability)
WHERE NOT EXISTS {
    MATCH (impl)-[:IMPLEMENTS]->(cap)
}
RETURN cap.cap_id, cap.description
'''
```

**Mission routing:**
- Emit to **L2 (org scope)**, not L1 directly
- L2→L1 membranes deliver automatically
- Target: `target_scope: "org"`, `target_org: "mind-protocol"`

**Testing:**
1. Unknown event observed → mission.protocol_update emitted within 10s
2. Missing capability → mission.add_capability emitted
3. Governance violation → mission.fix_governance emitted
4. Missions delivered to L2, exported to L1

**Acceptance criteria:**
- [ ] Missions created within 10s of gap detection
- [ ] All 3 gap types handled
- [ ] Missions routed to L2 (not L1 directly)

**Time estimate:** 3 days

---

### Week 3: Code Generation & CI Pipeline

**Task 1: SDK Stub Generation**

**What to build:**
1. **File:** `tools/codegen/generate_sdk.py`
2. **Input:** L4 Event_Schema nodes
3. **Output:** TypeScript/Python/Go type definitions

**Entry point:**
- `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md` (Section 7: Code Generation Pipeline)
- Example implementation provided (lines 1300-1400)

**Key query:**

```python
query = '''
MATCH (pv:Protocol_Version {semver: $version})-[:PUBLISHES_SCHEMA]->(es:Event_Schema)
RETURN es.name, es.fields, es.required_fields, es.description
'''
```

**Generate for each language:**
- TypeScript: `interface {EventName}Event { ... }`
- Python: `class {EventName}Event(BaseModel): ...`
- Go: `type {EventName}Event struct { ... }`

**Testing:**
1. Generate SDK from L4 → valid type definitions
2. Hash matches checked-in code → CI passes
3. Change L4 schema → regenerate → CI fails until committed

**Acceptance criteria:**
- [ ] Generates valid code for 3 languages
- [ ] CI fails on drift (hand-edits diverge from L4)

**Time estimate:** 3-4 days

---

**Task 2: Conformance Test Pipeline**

**What to build:**
1. **File:** `tools/conformance/generate_tests.py` - Generate tests from L4
2. **File:** `tools/conformance/record_results.py` - Write results to L4
3. **GitHub Action:** `.github/workflows/conformance.yml`

**Entry point:**
- `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md` (Section 3: Certification Pipeline)
- Full implementation provided (lines 550-750)

**Workflow:**

```yaml
name: SDK Conformance Tests

on:
  push:
    branches: [main]
    paths: ['sdk/**']

jobs:
  conformance:
    steps:
      - name: Generate tests from L4
        run: python tools/conformance/generate_tests.py --suite conformance.membrane_events

      - name: Run conformance tests
        run: npm test -- tests/generated/

      - name: Record results to L4
        run: python tools/conformance/record_results.py --sdk typescript@${{ github.sha }}
```

**Generate tests query:**

```python
query = '''
MATCH (cs:Conformance_Suite {suite_id: $suite_id})-[:CONTAINS]->(cc:Conformance_Case)
MATCH (cs)-[:TESTS]->(es:Event_Schema)
RETURN cc.case_id, cc.description, cc.expected, es.name, es.fields
ORDER BY cc.priority DESC
'''
```

**Record results:**

```python
# Create Conformance_Result node
# Link via CERTIFIES_CONFORMANCE to SDK_Release
# Emit certification.published event
```

**Testing:**
1. CI generates tests from L4 → 20 test cases created
2. Tests run → pass/fail recorded
3. Results written to L4 → Conformance_Result node created
4. Dashboard shows updated conformance rates

**Acceptance criteria:**
- [ ] CI generates + runs tests automatically
- [ ] Results written to L4 within 5 min
- [ ] Pass rates >85% required for release

**Time estimate:** 3-4 days

---

## Iris: Dashboard Integration (1 week)

### Week 4: Protocol Compliance Dashboards

**Task:** Add 3 new dashboard views querying L4

**What to build:**
1. **Compliance View** - SDK conformance pass rates
2. **Governance Health** - Rejection rates by reason
3. **Membrane κ Trends** - Protocol→impl strength over time

**Entry point:**
- `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md` (Section 8: Dashboard Integration)
- Queries provided (lines 1450-1550)

---

**View 1: Compliance View**

**File:** `app/consciousness/components/ComplianceView.tsx`

**Query:**

```cypher
MATCH (cr:Conformance_Result)-[:CERTIFIES_CONFORMANCE]->(sdk:SDK_Release)
RETURN sdk.language as language,
       sdk.version as version,
       cr.pass_rate as pass_rate,
       cr.test_date as test_date,
       cr.passed as passed,
       cr.total_cases as total
ORDER BY cr.test_date DESC
```

**Visualization:**
- Table with columns: SDK, Version, Pass Rate, Tests (passed/total), Last Tested
- Sparkline showing pass rate trend over time
- Color coding: >90% green, 85-90% yellow, <85% red

**Testing:**
1. Query L4 → returns conformance results
2. Table renders with correct data
3. Sparklines show trends
4. Color coding correct

**Acceptance criteria:**
- [ ] Real-time conformance data
- [ ] Trend visualization
- [ ] <500ms query time

**Time estimate:** 2 days

---

**View 2: Governance Health**

**File:** `app/consciousness/components/GovernanceHealth.tsx`

**Query:**

```cypher
// L4 provides total schemas
MATCH (es:Event_Schema)
RETURN count(es) as total_schemas

// Bus telemetry provides rejections (join in backend)
// Compute: rejections per reason / total events
```

**Visualization:**
- Pie chart: rejection reasons (missing_sig, rate_limit, unknown_schema, payload_size)
- Bar chart: rejections per namespace
- Table: top violating components

**Testing:**
1. Query L4 + bus telemetry → rejection breakdown
2. Pie chart renders
3. Drill-down to component level

**Acceptance criteria:**
- [ ] Rejection breakdown visible
- [ ] Drill-down to root cause
- [ ] Refreshes every 30s

**Time estimate:** 2 days

---

**View 3: Membrane κ Trends**

**File:** `app/consciousness/components/MembraneKappaTrends.tsx`

**Query:**

```cypher
MATCH (proto:SubEntity {name: "proto.membrane_stack"})-[impl:IMPLEMENTS]->(artifact)
RETURN artifact.package_name as component,
       impl.kappa_down as kappa_down,
       impl.kappa_up as kappa_up,
       impl.last_updated as last_updated,
       impl.update_count as updates
ORDER BY impl.last_updated DESC
```

**Visualization:**
- Line chart: κ↓ and κ↑ over time per component
- Table: current κ values + update count
- Trend indicators: ↑ strengthening, ↓ weakening, → stable

**Testing:**
1. Query L4 → κ values for all IMPLEMENTS links
2. Line chart shows trends
3. Real-time updates when κ changes

**Acceptance criteria:**
- [ ] κ trends visualized
- [ ] Updates in real-time
- [ ] Shows learning convergence

**Time estimate:** 2-3 days

---

## Ada: Coordination & Verification

### Your Role

**Week 1-2:** Coordinate Felix + Atlas, verify integration points
**Week 3:** Coordinate Atlas (CI), verify codegen output
**Week 4:** Coordinate Iris, verify dashboards, integration testing

### Key Integration Points to Verify

**Week 1:**
- [ ] Felix's `lint_inject` queries L4 correctly
- [ ] Rejection events have correct structure
- [ ] Cache strategy working (>90% hit rate)

**Week 2:**
- [ ] Felix's κ learning updates L4 links
- [ ] Atlas's gap detector emits missions to L2
- [ ] Atlas's `mp law` CLI returns correct data

**Week 3:**
- [ ] Atlas's codegen produces valid code
- [ ] CI fails on drift (hash mismatch)
- [ ] Conformance tests run and record to L4

**Week 4:**
- [ ] Iris's dashboards query L4 correctly
- [ ] Real-time updates working
- [ ] End-to-end: inject → validate → gap detect → mission → κ update → dashboard

### Final Acceptance Test

**Scenario:** New connector integration

1. Citizen queries: `mp law capabilities --component service:new_connector`
2. Citizen builds connector using L4 schemas
3. Connector emits events → `lint_inject` validates
4. Gap detector sees missing capability → emits mission
5. Mission delivered to L2 → exported to citizen
6. Citizen completes mission → κ increases
7. Dashboard shows updated conformance + κ trend

**Expected:** All steps complete within 30 minutes, no manual intervention

---

## Critical Files Reference

### Read These First (Priority Order)

1. **`docs/protocol/README.md`** - Start here, navigation guide
2. **`docs/protocol/L4_INTEGRATION_ARCHITECTURE.md`** - Full spec, read your section
3. **`docs/protocol/PROTOCOL_CLUSTER_COMPLETE.md`** - What's in L4, how to query

### Implementation Scripts (Reference Only)

- Don't modify these - they're already executed
- Use as examples of how to query L4
- Located in `tools/protocol/ingest_*_phase*.py`

### Substrate Verification

**Before starting, verify L4 is intact:**

```bash
# Connect to FalkorDB
redis-cli -p 6379

# Should return 165
> GRAPH.QUERY protocol "MATCH (n)-[:MEMBER_OF]->(proto:SubEntity {name: 'proto.membrane_stack'}) RETURN count(n)"

# Should return 873
> GRAPH.QUERY protocol "MATCH ()-[r]->() RETURN count(r)"
```

If counts don't match, re-run ingestion scripts.

---

## Communication Protocol

### Daily Standup (Async via SYNC.md)

**Format:**
```markdown
## 2025-10-30 - [Your Name]: [Component] - [Status]

**Yesterday:** [What you completed]
**Today:** [What you're working on]
**Blockers:** [Anything blocking progress]
**Questions:** [For Ada/Nicolas/Team]
```

### When You're Blocked

1. **Check documentation first:** `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md`
2. **Query L4 directly:** Use `redis-cli` to verify data
3. **Update SYNC.md with blocker:** Be specific about what's blocking
4. **Tag Ada for coordination:** She'll route to right person

### When You're Done with a Component

1. **Self-verify:** Run tests, check acceptance criteria
2. **Update SYNC.md:** Document completion + verification results
3. **Handoff:** Tag next person in chain (Felix→Atlas, Atlas→Iris, etc.)

---

## Questions & Answers

**Q: What if L4 graph is missing data I need?**
A: Check ingestion scripts in `tools/protocol/`. Likely need to re-run a phase or add to existing phase.

**Q: Can I modify L4 nodes directly?**
A: Yes, but document changes in SYNC.md. Prefer Cypher queries over scripts for one-off changes.

**Q: How do I test my L4 queries before implementing?**
A: Use `redis-cli -p 6379` → `GRAPH.QUERY protocol "your query here"`

**Q: What if FalkorDB is down?**
A: Engine should continue with cached data (degraded mode). Alert ops, queue writes for replay.

**Q: Can I skip the cache optimization for now?**
A: For prototyping, yes. For production, no - hot path must be <10ms per query.

**Q: Do I need all 3 languages for codegen?**
A: Start with TypeScript (highest priority), add Python/Go later.

**Q: What's the priority if I'm behind schedule?**
A: Week 1 (lint_inject + mp law) is critical path. Week 3-4 can slip if needed.

---

## Success Metrics (Review in 4 Weeks)

### Felix
- [ ] `lint_inject` validates 100+ envelopes/sec
- [ ] κ values converge within 100 outcomes
- [ ] No injection bypass vulnerabilities

### Atlas
- [ ] `mp law` CLI used by 80% of connector work
- [ ] Gap detection creates missions within 10s
- [ ] CI blocks releases with conformance <85%
- [ ] Zero drift incidents (hand-edits diverging from L4)

### Iris
- [ ] Dashboards query L4 in <500ms
- [ ] Real-time updates working
- [ ] All 3 views operational

### Team (Integration)
- [ ] End-to-end scenario completes in <30 min
- [ ] No manual intervention needed for protocol validation
- [ ] Citizens prefer L4 queries over docs

---

## Let's Go! 🚀

**L4 substrate is ready. The protocol knows itself. Time to make it operational.**

**Next Step:** Each person reads their section in `docs/protocol/L4_INTEGRATION_ARCHITECTURE.md`, sets up dev environment, starts Week 1 tasks.

**First Commit Target:** Week 1, Day 3 - Felix's `lint_inject` + Atlas's `mp law` CLI

**Questions?** Update SYNC.md or ping Ada for coordination.

---

**From:** Luca Vellumhand
**Status:** ✅ Substrate complete, handoff ready
**Confidence:** High - Full specs + implementations provided
**Risk:** Low - Incremental delivery, clear acceptance criteria

**Let's build living graph law into operational reality.** 🧠✨
