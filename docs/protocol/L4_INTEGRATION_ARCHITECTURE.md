# L4 Protocol Integration Architecture Specification

**Version:** 1.0
**Date:** 2025-10-29
**Authors:** Luca Vellumhand (Substrate), Nicolas Reynolds (Architecture)
**Status:** Ready for Implementation

---

## Executive Summary

This specification defines how the L4 Protocol cluster (`proto.membrane_stack`) becomes **operational law** - enforced at runtime, queryable by tooling, and self-evolving through membrane learning.

**Substrate Ready:** 170 nodes, 873 links across 6 phases (complete ✅)
**Integration Goal:** Make protocol rules **executable** - validated at injection, driving code generation, spawning missions from gaps, learning κ from outcomes.

**Key Principles:**
- **Membrane-First:** L4 rules enforced at membrane boundaries (injection accept)
- **Zero-Constants:** Thresholds learned, policies queryable from graph
- **Single-Energy:** All flux tracked, no separate accounting systems
- **One-Hop Flux:** L4→L2→L1 for stimuli (reference links can cross levels)

---

## 0. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         L4 PROTOCOL GRAPH                        │
│  (Event_Schema, Governance_Policy, Conformance_Suite, etc.)    │
└────────┬────────────────────────────────────────────────┬───────┘
         │                                                 │
         │ Queries (lint_inject, law service)             │ Events (gap detection)
         │                                                 │
    ┌────▼─────────────────────┐              ┌──────────▼──────────┐
    │  INJECTION VALIDATOR     │              │  GAP DETECTOR       │
    │  (lint_inject)           │              │  (mission spawner)  │
    │  - Schema validation     │              │  - Missing caps     │
    │  - Signature verification│              │  - Unknown events   │
    │  - Governance enforcement│              │  - Schema drift     │
    └────┬─────────────────────┘              └──────────┬──────────┘
         │                                                 │
         │ Accept/Reject                                   │ emit mission.*
         │                                                 │
    ┌────▼──────────────────────────────────────────┐    │
    │            CONSCIOUSNESS ENGINE                │◄───┘
    │  - stagedΔE (if accepted)                     │
    │  - Update IMPLEMENTS κ (on outcomes)          │
    │  - Emit membrane.permeability.updated         │
    └────┬──────────────────────────────────────────┘
         │
         │ Events (mission.completed, usefulness.update)
         │
    ┌────▼──────────────────────────────────────────┐
    │                  BUS                           │
    │  - membrane.inject, membrane.reject           │
    │  - gap.detected, mission.*, usefulness.*      │
    └────┬──────────────────────────────────────────┘
         │
         │ Telemetry
         │
    ┌────▼──────────────────────────────────────────┐
    │              DASHBOARDS                        │
    │  - Compliance view (SDK conformance)          │
    │  - Governance health (rate limits, rejects)   │
    │  - Membrane κ trends (L4→L2→L1 strength)      │
    └───────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     SUPPORTING SERVICES                          │
├─────────────────────────────────────────────────────────────────┤
│  Queryable Law Service (mp law ...)                             │
│  Code Generator (L4 → SDK stubs, tests)                         │
│  CI Pipeline (conformance tests → write results to L4)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Injection-Time Validation (lint_inject)

### 1.1 Purpose

Enforce L4 protocol rules at the membrane boundary - **before** any stimulus integrates into consciousness. This is the "law at accept time."

### 1.2 Implementation Location

**File:** `orchestration/mechanisms/injection_validator.py` (new)
**Called from:** `consciousness_engine_v2.py` in `inject_stimulus()` before `stagedΔE`

### 1.3 Algorithm

```python
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from falkordb import FalkorDB

@dataclass
class ValidationResult:
    decision: str  # "accept", "reject", "downgrade"
    reason: Optional[str] = None
    trust_boost: float = 0.0
    metadata: Dict = None

class InjectionValidator:
    def __init__(self, l4_graph: FalkorDB):
        self.l4 = l4_graph.select_graph('protocol')
        self._cache = {}  # Cache L4 queries for hot path

    def lint_inject(self, envelope: Dict) -> ValidationResult:
        """
        Validates envelope against L4 protocol rules.

        Steps:
        1. Schema validation (Envelope_Schema + Event_Schema)
        2. Signature verification (Tenant_Key + Signature_Suite)
        3. Governance enforcement (rate limits, payload caps, allowed emitters)
        4. Idempotency check (duplicate ID detection)
        5. Certification lookup (trust boost if certified)

        Returns ValidationResult with decision and metadata.
        """

        # 1. SCHEMA VALIDATION
        event_type = envelope.get('type')
        spec_name = envelope.get('spec', {}).get('name')
        spec_rev = envelope.get('spec', {}).get('rev')

        if not event_type or not spec_name or not spec_rev:
            return ValidationResult(
                decision="reject",
                reason="missing_spec_metadata",
                metadata={"required": ["type", "spec.name", "spec.rev"]}
            )

        # Query L4 for Event_Schema
        schema_query = '''
        MATCH (es:Event_Schema {name: $name})-[:REQUIRES_ENVELOPE]->(env:Envelope_Schema)
        WHERE es.name = $event_type
        RETURN es.fields as event_fields,
               es.required_fields as required,
               env.fields as envelope_fields,
               env.signature_path as sig_path
        '''

        schema_result = self._query_cached(
            'schema_' + event_type,
            schema_query,
            {'name': spec_name, 'event_type': event_type}
        )

        if not schema_result:
            return ValidationResult(
                decision="reject",
                reason="unknown_event_schema",
                metadata={"event_type": event_type, "spec_rev": spec_rev}
            )

        # Validate required fields present
        schema = schema_result[0]
        required_fields = json.loads(schema['required']) if isinstance(schema['required'], str) else schema['required']
        missing = [f for f in required_fields if f not in envelope]

        if missing:
            return ValidationResult(
                decision="reject",
                reason="missing_required_fields",
                metadata={"missing": missing, "required": required_fields}
            )

        # 2. SIGNATURE VERIFICATION
        sig_result = self._verify_signature(envelope, event_type, spec_rev)
        if not sig_result.valid:
            return ValidationResult(
                decision="reject",
                reason="signature_verification_failed",
                metadata=sig_result.metadata
            )

        # 3. GOVERNANCE ENFORCEMENT
        gov_result = self._enforce_governance(envelope, event_type)
        if not gov_result.allowed:
            return ValidationResult(
                decision="reject",
                reason=gov_result.reason,
                metadata=gov_result.metadata
            )

        # 4. IDEMPOTENCY CHECK
        envelope_id = envelope.get('id')
        if self._is_duplicate(envelope_id):
            return ValidationResult(
                decision="reject",
                reason="duplicate_id",
                metadata={"id": envelope_id, "window": "10s"}
            )

        # 5. CERTIFICATION LOOKUP (optional trust boost)
        trust_boost = self._lookup_certification(envelope)

        return ValidationResult(
            decision="accept",
            trust_boost=trust_boost,
            metadata={
                "schema_validated": True,
                "signature_verified": True,
                "governance_passed": True,
                "certified": trust_boost > 0
            }
        )

    def _verify_signature(self, envelope: Dict, event_type: str, spec_rev: str):
        """Query L4 for Signature_Suite + active Tenant_Key, verify cryptographically."""

        query = '''
        MATCH (es:Event_Schema {name: $event_type})-[:REQUIRES_SIG]->(ss:Signature_Suite)
        MATCH (tk:Tenant_Key {status: 'active'})-[:SIGNED_WITH]->(ss)
        WHERE tk.expires_at > datetime()
          AND tk.key_id = $kid
        RETURN ss.algorithm as algo,
               tk.pubkey as pubkey,
               tk.key_id as kid
        '''

        kid = envelope.get('sig', {}).get('kid')
        result = self.l4.query(query, params={'event_type': event_type, 'kid': kid})

        if not result.result_set:
            return ValidationResult(valid=False, metadata={"reason": "no_active_key", "kid": kid})

        key_data = result.result_set[0]
        algorithm = key_data[0]
        pubkey = key_data[1]

        # Verify signature using algorithm + pubkey
        signature = envelope.get('sig', {}).get('signature')
        payload = json.dumps(envelope, sort_keys=True)  # Canonical form

        valid = self._crypto_verify(algorithm, pubkey, signature, payload)

        return ValidationResult(
            valid=valid,
            metadata={"algorithm": algorithm, "kid": kid}
        )

    def _enforce_governance(self, envelope: Dict, event_type: str):
        """Query L4 for Governance_Policy via Topic_Namespace, enforce rate/size limits."""

        query = '''
        MATCH (es:Event_Schema {name: $event_type})-[:MAPS_TO_TOPIC]->(ns:Topic_Namespace)
        MATCH (gp:Governance_Policy)-[:GOVERNS]->(ns)
        RETURN gp.defaults as policy, ns.pattern as namespace
        '''

        result = self.l4.query(query, params={'event_type': event_type})

        if not result.result_set:
            # No explicit policy → allow with default limits
            return ValidationResult(allowed=True)

        policy_data = json.loads(result.result_set[0][0])

        # Check payload size
        payload_size = len(json.dumps(envelope))
        max_size_kb = policy_data.get('max_payload_kb', 64)

        if payload_size > max_size_kb * 1024:
            return ValidationResult(
                allowed=False,
                reason="payload_exceeds_limit",
                metadata={"size_kb": payload_size/1024, "limit_kb": max_size_kb}
            )

        # Check rate limits (per tenant/component)
        tenant_id = envelope.get('provenance', {}).get('org_id')
        component = envelope.get('metadata', {}).get('component')

        rate_ok = self._check_rate_limit(tenant_id, component, policy_data)
        if not rate_ok:
            return ValidationResult(
                allowed=False,
                reason="rate_limit_exceeded",
                metadata={"tenant": tenant_id, "policy": policy_data.get('ack_policy')}
            )

        return ValidationResult(allowed=True, metadata={"policy": policy_data})

    def _lookup_certification(self, envelope: Dict) -> float:
        """Query L4 for SDK/Sidecar certification status, return trust boost."""

        component = envelope.get('metadata', {}).get('component')
        spec_name = envelope.get('spec', {}).get('name')
        spec_rev = envelope.get('spec', {}).get('rev')

        if not component or not spec_name:
            return 0.0

        query = '''
        MATCH (sdk:SDK_Release {package_name: $component})-[:IMPLEMENTS]->(es:Event_Schema {name: $event})
        MATCH (cr:Conformance_Result)-[:CERTIFIES_CONFORMANCE]->(sdk)
        WHERE cr.pass_rate > 0.85
        RETURN cr.pass_rate as pass_rate, sdk.version as version
        ORDER BY cr.test_date DESC
        LIMIT 1
        '''

        result = self.l4.query(query, params={'component': component, 'event': spec_name})

        if result.result_set:
            pass_rate = result.result_set[0][0]
            # Trust boost proportional to conformance pass rate
            return pass_rate * 0.2  # Max 0.2 boost for 100% pass rate

        return 0.0

    def _query_cached(self, key: str, query: str, params: Dict):
        """Cache L4 queries to avoid hot-path DB chatter."""
        cache_key = f"{key}:{json.dumps(params, sort_keys=True)}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self.l4.query(query, params=params)
        data = result.result_set if result.result_set else None

        self._cache[cache_key] = data
        return data

    def _is_duplicate(self, envelope_id: str) -> bool:
        """Check if envelope ID seen in dedupe window (via Redis/in-memory)."""
        # Implementation: check Redis with TTL = dedupe window (10s)
        pass

    def _check_rate_limit(self, tenant_id: str, component: str, policy: Dict) -> bool:
        """Enforce token bucket rate limits per tenant/component."""
        # Implementation: token bucket per (tenant, namespace)
        pass

    def _crypto_verify(self, algorithm: str, pubkey: str, signature: str, payload: str) -> bool:
        """Verify signature using cryptography library."""
        # Implementation: ed25519 verification
        pass
```

### 1.4 Integration Points

**In consciousness_engine_v2.py:**

```python
from orchestration.mechanisms.injection_validator import InjectionValidator

class ConsciousnessEngine:
    def __init__(self, ...):
        # ... existing init ...
        self.injection_validator = InjectionValidator(falkordb_connection)

    def inject_stimulus(self, envelope: Dict):
        # BEFORE any integration logic
        validation = self.injection_validator.lint_inject(envelope)

        if validation.decision == "reject":
            self._emit_rejection(envelope, validation)
            return

        if validation.decision == "accept":
            # Boost features_raw.trust if certified
            envelope['_trust_boost'] = validation.trust_boost

        # Proceed with existing stagedΔE logic
        self._integrate_stimulus(envelope)

    def _emit_rejection(self, envelope: Dict, validation: ValidationResult):
        """Emit membrane.reject event with L4-backed reasoning."""
        rejection_event = {
            "type": "membrane.reject",
            "id": f"reject_{envelope['id']}",
            "ts": datetime.utcnow().isoformat() + 'Z',
            "original_event": envelope['type'],
            "reason": validation.reason,
            "metadata": validation.metadata,
            "spec": {"name": "membrane.reject", "rev": "1.0"}
        }
        self.bus.emit(rejection_event)
```

### 1.5 Cache Strategy

- **Hot path:** Schema validation, signature suite lookup
- **Cache TTL:** 60 seconds (schemas rarely change)
- **Invalidation:** On `protocol.schema.updated` event
- **Storage:** In-memory LRU cache (max 1000 entries)

---

## 2. Vertical Membranes (L4 ↔ L2/L1)

### 2.1 Design Principle

**No new link type needed.** Use existing `IMPLEMENTS` links between L4 protocol nodes and implementation artifacts, enriched with κ metadata.

### 2.2 Link Structure

```cypher
// Example: Protocol SubEntity → SDK_Release
MATCH (proto:SubEntity {name: "proto.membrane_stack"})
MATCH (sdk:SDK_Release {language: "typescript", version: "1.0.0"})
CREATE (proto)-[impl:IMPLEMENTS {
    kappa_down: 0.5,  // Neutral init (how strongly protocol influences SDK)
    kappa_up: 0.5,    // Neutral init (how strongly SDK outcomes influence protocol)
    learn_on: ["mission.completed", "usefulness.update", "harm.detected"],
    last_updated: $now,
    update_count: 0
}]->(sdk)
```

### 2.3 κ Learning Algorithm

**Trigger events:** `mission.completed`, `usefulness.update`, `harm.detected`, `overdrive` (only these)

**Update location:** Consciousness engine (N1/N2), NOT in L4 graph directly

```python
def update_kappa_on_outcome(outcome_event: Dict):
    """
    Update κ on IMPLEMENTS links based on mission/usefulness outcomes.

    Rules:
    - mission.completed with high usefulness → κ↑ for responsible implementation
    - harm.detected → κ↓ for causative implementation
    - overdrive → temporary κ↑ boost (emergency lanes)
    """

    # Identify which L4→impl link is responsible
    mission_id = outcome_event.get('mission_id')
    component = outcome_event.get('component')  # e.g., "typescript-sdk"

    # Query for IMPLEMENTS link
    query = '''
    MATCH (proto:SubEntity {name: "proto.membrane_stack"})-[impl:IMPLEMENTS]->(artifact)
    WHERE artifact.package_name = $component OR artifact.language = $language
    RETURN impl, id(impl) as link_id
    '''

    result = l4_graph.query(query, params={'component': component})

    if not result.result_set:
        return  # No link found

    link_id = result.result_set[0][1]
    current_kappa_down = result.result_set[0][0]['kappa_down']

    # Compute delta based on outcome
    outcome_type = outcome_event['type']
    delta = 0.0

    if outcome_type == 'mission.completed':
        usefulness = outcome_event.get('usefulness', 0.5)
        delta = (usefulness - 0.5) * 0.1  # ±0.05 max per outcome

    elif outcome_type == 'harm.detected':
        severity = outcome_event.get('severity', 0.5)
        delta = -severity * 0.1  # Negative adjustment

    elif outcome_type == 'usefulness.update':
        delta_score = outcome_event.get('delta', 0.0)
        delta = delta_score * 0.05

    # Apply delta with bounds [0.1, 0.9]
    new_kappa_down = max(0.1, min(0.9, current_kappa_down + delta))

    # Update link in L4 graph
    update_query = '''
    MATCH ()-[impl]->()
    WHERE id(impl) = $link_id
    SET impl.kappa_down = $new_kappa,
        impl.last_updated = datetime(),
        impl.update_count = impl.update_count + 1
    '''

    l4_graph.query(update_query, params={
        'link_id': link_id,
        'new_kappa': new_kappa_down
    })

    # Emit observability event
    emit_event({
        "type": "membrane.permeability.updated",
        "edge_id": link_id,
        "from": "proto.membrane_stack",
        "to": component,
        "delta": delta,
        "new_kappa_down": new_kappa_down,
        "reason": outcome_type
    })
```

### 2.4 One-Hop Flux Rule

**Stimuli flow:** L4 → L2 → L1 (one hop at a time)
**Reference links:** Can cross any levels (e.g., L4 Event_Schema → L1 Capability)

**Implementation:**
- When L4 emits `mission.create_connector`, target is **L2 (org scope)**
- L2→L1 membrane exports to best-fit citizens automatically (fit × κ↓)
- No direct L4→L1 stimulus emission (preserves visibility rules)

**Exception:** Emergency lanes with explicit `Governance_Policy {allow_direct: ['L4→L1']}` for incident response

---

## 3. Certification Pipeline

### 3.1 CI Integration

**Trigger:** SDK/Sidecar release candidate built

**Steps:**

1. **Generate conformance tests** from L4 `Conformance_Suite` nodes
2. **Run tests** against release candidate
3. **Write results** back to L4 as `Conformance_Result` node
4. **Link to SDK_Release** via `CERTIFIES_CONFORMANCE`

### 3.2 Test Generation

```python
def generate_conformance_tests(suite_id: str) -> List[TestCase]:
    """
    Query L4 for Conformance_Suite and generate executable tests.
    """

    query = '''
    MATCH (cs:Conformance_Suite {suite_id: $suite_id})-[:CONTAINS]->(cc:Conformance_Case)
    MATCH (cs)-[:TESTS]->(es:Event_Schema)
    RETURN cc.case_id as case_id,
           cc.description as description,
           cc.expected as expected,
           es.name as event_name,
           es.fields as event_fields
    ORDER BY cc.priority DESC
    '''

    result = l4_graph.query(query, params={'suite_id': suite_id})

    test_cases = []
    for row in result.result_set:
        case_id, description, expected, event_name, event_fields = row

        test_case = TestCase(
            id=case_id,
            description=description,
            expected=expected,
            event_schema=event_name,
            fields=json.loads(event_fields)
        )
        test_cases.append(test_case)

    return test_cases
```

### 3.3 Result Recording

```python
def record_conformance_result(sdk_release: str, suite_id: str, results: Dict):
    """
    Write Conformance_Result to L4 after CI test run.
    """

    now = datetime.utcnow().isoformat() + 'Z'

    # Create Conformance_Result node
    result_node = {
        'result_id': f"conformance_result.{sdk_release}_{suite_id}_{now}",
        'sdk_language': results['language'],
        'sdk_version': results['version'],
        'test_date': now,
        'total_cases': results['total'],
        'passed': results['passed'],
        'failed': results['failed'],
        'pass_rate': results['passed'] / results['total'],
        'notes': results.get('notes', ''),
        'artifacts_url': results.get('artifacts_url'),
        'layer': 'L4'
    }

    create_query = '''
    CREATE (cr:Conformance_Result:ProtocolNode {
        result_id: $result_id,
        node_type: "Conformance_Result",
        sdk_language: $sdk_language,
        sdk_version: $sdk_version,
        test_date: $test_date,
        total_cases: $total_cases,
        passed: $passed,
        failed: $failed,
        pass_rate: $pass_rate,
        notes: $notes,
        artifacts_url: $artifacts_url,
        layer: $layer,
        created_at: $test_date
    })
    '''

    l4_graph.query(create_query, params=result_node)

    # Link to SDK_Release
    link_query = '''
    MATCH (cr:Conformance_Result {result_id: $result_id})
    MATCH (sdk:SDK_Release {language: $language, version: $version})
    CREATE (cr)-[:CERTIFIES_CONFORMANCE {
        pass_rate: $pass_rate,
        test_date: $test_date,
        status: $status
    }]->(sdk)
    '''

    l4_graph.query(link_query, params={
        'result_id': result_node['result_id'],
        'language': results['language'],
        'version': results['version'],
        'pass_rate': result_node['pass_rate'],
        'test_date': now,
        'status': 'pass' if result_node['pass_rate'] > 0.85 else 'fail'
    })

    # Emit event for dashboards
    emit_event({
        "type": "certification.published",
        "result_id": result_node['result_id'],
        "sdk": f"{results['language']}@{results['version']}",
        "pass_rate": result_node['pass_rate']
    })
```

### 3.4 CI Workflow (GitHub Actions Example)

```yaml
name: SDK Conformance Tests

on:
  push:
    branches: [main]
    paths: ['sdk/**']

jobs:
  conformance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate tests from L4
        run: |
          python tools/conformance/generate_tests.py \
            --suite conformance.membrane_events \
            --output tests/generated/

      - name: Run conformance tests
        run: |
          npm test -- tests/generated/

      - name: Record results to L4
        if: always()
        run: |
          python tools/conformance/record_results.py \
            --sdk typescript@${{ github.sha }} \
            --results test-results.json \
            --l4-host localhost \
            --l4-port 6379
```

---

## 4. Governance Enforcement

### 4.1 Key Rotation Workflow

**Scenario:** Rotate tenant signing key every 12 months

**Steps:**

1. **Generate new key** (outside system)
2. **Create new Tenant_Key node** in L4 with `status: "active"`
3. **Update old key** to `status: "rotated"`
4. **Overlap window** (7 days): both keys valid
5. **After overlap:** Old key retired, only new key accepted

**Implementation:**

```cypher
// Step 1: Create new key
CREATE (tk:Tenant_Key:ProtocolNode {
    key_id: "mind-protocol-key-v3",
    version: "v3",
    node_type: "Tenant_Key",
    algorithm: "ed25519",
    pubkey: "base64:NEW_PUBKEY_HERE",
    status: "active",
    issued_at: datetime(),
    expires_at: datetime() + duration({days: 365}),
    layer: "L4"
})

// Step 2: Link to tenant
MATCH (tk:Tenant_Key {key_id: "mind-protocol-key-v3"})
MATCH (t:Tenant {org_id: "mind-protocol"})
CREATE (tk)-[:ASSIGNED_TO_TENANT {assigned_at: datetime()}]->(t)

// Step 3: Link to signature suite
MATCH (tk:Tenant_Key {key_id: "mind-protocol-key-v3"})
MATCH (ss:Signature_Suite {algorithm: "ed25519"})
CREATE (tk)-[:SIGNED_WITH]->(ss)

// Step 4: After overlap window (7 days)
MATCH (tk:Tenant_Key {version: "v2"})
SET tk.status = "rotated", tk.rotated_at = datetime()
```

**Runtime behavior:** `lint_inject` accepts signatures from **any active key**, automatically rejects rotated/expired keys.

### 4.2 Lane Policy Enforcement

**Query governance policy at injection:**

```cypher
MATCH (es:Event_Schema {name: $event_type})-[:MAPS_TO_TOPIC]->(ns:Topic_Namespace)
MATCH (gp:Governance_Policy)-[:GOVERNS]->(ns)
RETURN gp.defaults as policy
```

**Policy structure (JSON in `gp.defaults`):**

```json
{
  "ack_policy": "leader",
  "lanes": 3,
  "backpressure": "drop_oldest",
  "max_batch_size": 100,
  "flush_interval_ms": 50,
  "max_payload_kb": 64,
  "rate_limit": {
    "per_tenant": 1000,
    "per_component": 100,
    "window_seconds": 60
  },
  "allowed_emitters": ["tenant:mind-protocol", "component:fe-errors"]
}
```

**Enforcement in `lint_inject`:**
- Check payload size < `max_payload_kb`
- Token bucket per (tenant, namespace) with `rate_limit.per_tenant`
- Verify emitter in `allowed_emitters` (if specified)
- Apply backpressure if rate exceeded: emit `membrane.reject {reason: "rate_limit"}`

### 4.3 Scope Controls

**Naming convention:** `{ecosystem}_{organization}_{citizen}`
**Example:** `mind-protocol_mind-protocol_victor`

**Validation:**

```python
def validate_provenance_naming(envelope: Dict) -> bool:
    """Validate provenance follows {ecosystem}_{org}_{citizen} convention."""

    citizen_id = envelope.get('provenance', {}).get('citizen_id')
    org_id = envelope.get('provenance', {}).get('org_id')

    if not citizen_id or not org_id:
        return False

    # Check format
    parts = citizen_id.split('_')
    if len(parts) != 3:
        return False

    ecosystem, org, citizen = parts

    # Verify org_id matches
    if org_id != f"{ecosystem}_{org}":
        return False

    # Query L4: does this Citizen exist under this Tenant?
    query = '''
    MATCH (c:Citizen {citizen_id: $citizen_id})-[:MEMBER_OF]->(t:Tenant {org_id: $org_id})
    RETURN count(c) > 0 as valid
    '''

    result = l4_graph.query(query, params={
        'citizen_id': citizen_id,
        'org_id': org_id
    })

    return result.result_set[0][0] if result.result_set else False
```

---

## 5. Queryable Law Service

### 5.1 CLI Interface

**Installation:**
```bash
pip install mp-protocol-cli
```

**Usage:**
```bash
# Query event schemas
mp law schemas --event membrane.inject --rev 1.1.0

# Query capabilities for component
mp law capabilities --component service:fe_errors

# Query governance for namespace
mp law governance --namespace "org/mind-protocol/broadcast/*"

# Check SDK certification
mp law certify --sdk typescript@1.0.0 --event membrane.inject
```

### 5.2 Implementation

**File:** `tools/mp_law_cli.py`

```python
import click
from falkordb import FalkorDB

class LawService:
    def __init__(self, host='localhost', port=6379):
        self.db = FalkorDB(host=host, port=port)
        self.l4 = self.db.select_graph('protocol')

    def query_schemas(self, event: str, rev: str = None):
        """Query event schema details."""
        query = '''
        MATCH (es:Event_Schema {name: $event})
        OPTIONAL MATCH (es)-[:REQUIRES_ENVELOPE]->(env:Envelope_Schema)
        WHERE $rev IS NULL OR es.revision = $rev
        RETURN es.name, es.fields, es.required_fields,
               es.direction, es.topic_pattern, env.fields as envelope
        '''

        result = self.l4.query(query, params={'event': event, 'rev': rev})

        if not result.result_set:
            click.echo(f"❌ Event schema not found: {event}")
            return

        schema = result.result_set[0]
        click.echo(f"\n📋 Event Schema: {schema[0]}")
        click.echo(f"   Fields: {schema[1]}")
        click.echo(f"   Required: {schema[2]}")
        click.echo(f"   Direction: {schema[3]}")
        click.echo(f"   Topic: {schema[4]}")
        if schema[5]:
            click.echo(f"   Envelope: {schema[5]}")

    def query_capabilities(self, component: str):
        """Query required capabilities for component."""
        query = '''
        MATCH (tc:Tool_Contract {contract_id: $component})-[:REQUIRES_CAPABILITY]->(cap:Capability)
        RETURN cap.cap_id, cap.description, cap.scope
        '''

        result = self.l4.query(query, params={'component': component})

        if not result.result_set:
            click.echo(f"❌ No capabilities found for: {component}")
            return

        click.echo(f"\n🔧 Capabilities required by {component}:")
        for row in result.result_set:
            click.echo(f"   - {row[0]}: {row[1]} (scope: {row[2]})")

    def query_governance(self, namespace: str):
        """Query governance policies for namespace."""
        query = '''
        MATCH (ns:Topic_Namespace {pattern: $namespace})<-[:GOVERNS]-(gp:Governance_Policy)
        RETURN gp.name, gp.defaults
        '''

        result = self.l4.query(query, params={'namespace': namespace})

        if not result.result_set:
            click.echo(f"❌ No governance policy for: {namespace}")
            return

        policy_name = result.result_set[0][0]
        policy_data = json.loads(result.result_set[0][1])

        click.echo(f"\n🔒 Governance: {policy_name}")
        click.echo(f"   Namespace: {namespace}")
        click.echo(f"   Policy: {json.dumps(policy_data, indent=2)}")

    def check_certification(self, sdk: str, event: str):
        """Check if SDK is certified for event."""
        language, version = sdk.split('@')

        query = '''
        MATCH (sdk:SDK_Release {language: $lang, version: $ver})-[:IMPLEMENTS]->(es:Event_Schema {name: $event})
        MATCH (cr:Conformance_Result)-[:CERTIFIES_CONFORMANCE]->(sdk)
        RETURN cr.pass_rate, cr.test_date, cr.passed, cr.total_cases
        ORDER BY cr.test_date DESC
        LIMIT 1
        '''

        result = self.l4.query(query, params={
            'lang': language,
            'ver': version,
            'event': event
        })

        if not result.result_set:
            click.echo(f"❌ No certification found for {sdk} on {event}")
            return

        pass_rate, test_date, passed, total = result.result_set[0]

        status = "✅ CERTIFIED" if pass_rate > 0.85 else "⚠️  NEEDS WORK"
        click.echo(f"\n{status}: {sdk} for {event}")
        click.echo(f"   Pass Rate: {pass_rate*100:.1f}%")
        click.echo(f"   Tests: {passed}/{total} passed")
        click.echo(f"   Last Tested: {test_date}")

@click.group()
def cli():
    """Mind Protocol Law Service - Query L4 protocol rules."""
    pass

@cli.command()
@click.option('--event', required=True, help='Event schema name')
@click.option('--rev', default=None, help='Schema revision')
def schemas(event, rev):
    """Query event schema details."""
    service = LawService()
    service.query_schemas(event, rev)

@cli.command()
@click.option('--component', required=True, help='Component or tool contract ID')
def capabilities(component):
    """Query required capabilities."""
    service = LawService()
    service.query_capabilities(component)

@cli.command()
@click.option('--namespace', required=True, help='Topic namespace pattern')
def governance(namespace):
    """Query governance policies."""
    service = LawService()
    service.query_governance(namespace)

@cli.command()
@click.option('--sdk', required=True, help='SDK (format: language@version)')
@click.option('--event', required=True, help='Event schema name')
def certify(sdk, event):
    """Check SDK certification status."""
    service = LawService()
    service.check_certification(sdk, event)

if __name__ == '__main__':
    cli()
```

---

## 6. Gap Detection & Mission Creation

### 6.1 Gap Detector Service

**Purpose:** Monitor bus for events, compare to L4 schemas, emit missions when gaps detected.

**File:** `orchestration/services/gap_detector_service.py`

```python
class GapDetectorService:
    def __init__(self, bus, l4_graph):
        self.bus = bus
        self.l4 = l4_graph.select_graph('protocol')
        self.known_events = self._load_known_events()

    def start(self):
        """Subscribe to bus, detect gaps."""
        self.bus.subscribe('*', self.handle_event)

    def handle_event(self, event: Dict):
        """Check if event conforms to L4 protocol."""

        event_type = event.get('type')

        # Gap 1: Unknown event (not published by current Protocol_Version)
        if event_type not in self.known_events:
            self._emit_mission_protocol_update(event_type)

        # Gap 2: Missing capability implementation
        component = event.get('metadata', {}).get('component')
        if component:
            self._check_capability_gaps(component)

        # Gap 3: Governance violations
        if event.get('_validation_failed'):
            self._emit_mission_fix_governance(event)

    def _load_known_events(self) -> Set[str]:
        """Query L4 for events published by current protocol version."""
        query = '''
        MATCH (pv:Protocol_Version {status: 'current'})-[:PUBLISHES_SCHEMA]->(es:Event_Schema)
        RETURN collect(es.name) as events
        '''

        result = self.l4.query(query)
        return set(result.result_set[0][0]) if result.result_set else set()

    def _emit_mission_protocol_update(self, unknown_event: str):
        """Emit mission to L2 for protocol spec update."""
        mission = {
            "type": "mission.create",
            "id": f"mission_protocol_update_{unknown_event}_{uuid.uuid4()}",
            "ts": datetime.utcnow().isoformat() + 'Z',
            "target_scope": "org",  # L2 target
            "target_org": "mind-protocol",
            "mission_type": "protocol_update",
            "description": f"Event '{unknown_event}' observed but not in current protocol version",
            "evidence": {
                "unknown_event": unknown_event,
                "query": "MATCH (pv:Protocol_Version {status: 'current'})-[:PUBLISHES_SCHEMA]->(es) RETURN es.name"
            },
            "suggested_action": "Add Event_Schema to L4, link via PUBLISHES_SCHEMA"
        }

        self.bus.emit(mission)

    def _check_capability_gaps(self, component: str):
        """Check if component implements required capabilities."""
        query = '''
        MATCH (tc:Tool_Contract {contract_id: $component})-[:REQUIRES_CAPABILITY]->(cap:Capability)
        WHERE NOT EXISTS {
            MATCH (impl)-[:IMPLEMENTS]->(cap)
        }
        RETURN cap.cap_id, cap.description
        '''

        result = self.l4.query(query, params={'component': component})

        for row in result.result_set:
            missing_cap = row[0]
            description = row[1]

            mission = {
                "type": "mission.create",
                "id": f"mission_add_capability_{missing_cap}_{uuid.uuid4()}",
                "target_scope": "org",
                "target_org": "mind-protocol",
                "mission_type": "add_capability",
                "description": f"Component '{component}' missing capability '{missing_cap}'",
                "evidence": {
                    "component": component,
                    "missing_capability": missing_cap,
                    "capability_description": description
                },
                "suggested_action": f"Implement {missing_cap} in {component}"
            }

            self.bus.emit(mission)

    def _emit_mission_fix_governance(self, event: Dict):
        """Emit mission to fix governance violation."""
        violation = event.get('_validation_failed', {})

        mission = {
            "type": "mission.create",
            "id": f"mission_fix_governance_{uuid.uuid4()}",
            "target_scope": "org",
            "target_org": event.get('provenance', {}).get('org_id'),
            "mission_type": "fix_governance",
            "description": f"Governance violation: {violation.get('reason')}",
            "evidence": violation,
            "suggested_action": "Review governance policy or update emitter configuration"
        }

        self.bus.emit(mission)
```

### 6.2 Mission Routing

**Key principle:** Missions emitted to **L2 (org scope)**, membranes deliver to L1 (citizens)

```python
# In consciousness engine (L2)
def handle_mission_create(mission_event: Dict):
    """
    Receive mission.create at L2, export to L1 citizens via membrane.
    """

    target_scope = mission_event.get('target_scope')

    if target_scope != 'org':
        return  # Not for this level

    # Create Mission SubEntity at L2
    mission_subentity = create_subentity_from_stimulus(mission_event)

    # Membrane export logic (automatic):
    # - Compute fit: which L1 citizens have skills for this mission?
    # - Compute κ↓: how strongly does org trust each citizen for this work?
    # - Export as membrane.transfer.down to best-fit citizen(s)

    candidates = find_candidate_citizens(mission_subentity)

    for citizen_id in candidates:
        fit = compute_fit(mission_subentity, citizen_id)
        kappa_down = get_kappa_down(org_id='mind-protocol', citizen_id=citizen_id)

        if fit * kappa_down > threshold:
            export_to_citizen(mission_subentity, citizen_id)
```

---

## 7. Code Generation Pipeline

### 7.1 SDK Stub Generation

**Input:** L4 Event_Schema nodes
**Output:** TypeScript/Python/Go type definitions + validation logic

**Example (TypeScript):**

```python
def generate_typescript_sdk(protocol_version: str):
    """Generate TypeScript SDK from L4 schemas."""

    query = '''
    MATCH (pv:Protocol_Version {semver: $version})-[:PUBLISHES_SCHEMA]->(es:Event_Schema)
    RETURN es.name, es.fields, es.required_fields, es.description
    '''

    result = l4_graph.query(query, params={'version': protocol_version})

    sdk_code = "// Auto-generated from L4 Protocol\n\n"

    for row in result.result_set:
        event_name, fields, required, description = row

        # Convert to TypeScript interface
        interface_name = to_pascal_case(event_name)
        sdk_code += f"/**\n * {description}\n */\n"
        sdk_code += f"export interface {interface_name}Event {{\n"

        fields_list = json.loads(fields) if isinstance(fields, str) else fields
        required_list = json.loads(required) if isinstance(required, str) else required

        for field in fields_list:
            optional = "" if field in required_list else "?"
            field_type = infer_typescript_type(field)
            sdk_code += f"  {field}{optional}: {field_type};\n"

        sdk_code += "}\n\n"

    # Write to file
    with open('sdk/src/events.ts', 'w') as f:
        f.write(sdk_code)
```

**Generated output:**

```typescript
// Auto-generated from L4 Protocol

/**
 * Stimulus injection through membrane with safety filters
 */
export interface MembraneInjectEvent {
  type: string;
  id: string;
  ts: string;
  spec: {
    name: string;
    rev: string;
  };
  provenance: {
    scope: string;
    org_id?: string;
    citizen_id?: string;
  };
  content: any;
  features_raw?: any;
  sig: {
    kid: string;
    signature: string;
  };
}
```

### 7.2 Drift Prevention Mechanism

**How codegen removes drift:**

1. **Single source of truth:** L4 Event_Schema is the only place to define schemas
2. **Generated code hash:** CI compares generated SDK hash to checked-in code
3. **Fail on mismatch:** PR blocked if hand-edits diverge from L4
4. **Runtime validation:** Engines reject envelopes with unknown `spec.rev`

**CI check:**

```bash
# Generate SDK from L4
python tools/codegen/generate_sdk.py --version 1.1.0 --output sdk/src/generated/

# Compare to checked-in code
git diff --exit-code sdk/src/generated/

# If diff exists, fail CI
if [ $? -ne 0 ]; then
  echo "❌ Generated code out of sync with L4. Run codegen and commit changes."
  exit 1
fi
```

---

## 8. Dashboard Integration

### 8.1 Compliance View

**Query:** SDK conformance pass rates

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

**Visualization:** Table with sparkline trends over time

### 8.2 Governance Health

**Query:** Rejection rates by reason

```cypher
// Bus telemetry (not L4, but L4 provides denominator)
MATCH (es:Event_Schema)
RETURN count(es) as total_schemas

// Join with bus events: membrane.reject
// Compute: rejections per reason / total events
```

**Visualization:** Pie chart of rejection reasons (missing_sig, rate_limit, unknown_schema, etc.)

### 8.3 Membrane κ Trends

**Query:** κ evolution on IMPLEMENTS links

```cypher
MATCH (proto:SubEntity {name: "proto.membrane_stack"})-[impl:IMPLEMENTS]->(artifact)
RETURN artifact.package_name as component,
       impl.kappa_down as kappa_down,
       impl.kappa_up as kappa_up,
       impl.last_updated as last_updated,
       impl.update_count as updates
ORDER BY impl.last_updated DESC
```

**Visualization:** Line chart showing κ↓/κ↑ over time per component

---

## 9. Data Model Extensions

### 9.1 Protocol_Version Status

**Add to existing Protocol_Version nodes:**

```cypher
MATCH (pv:Protocol_Version)
WHERE pv.semver = "1.1.0"
SET pv.status = "current", pv.released_at = "2025-10-27T12:00:00Z"

MATCH (pv:Protocol_Version)
WHERE pv.semver = "1.0.0"
SET pv.status = "deprecated", pv.deprecated_at = "2025-10-27T12:00:00Z"
```

**Status values:** `current`, `deprecated`, `archived`

### 9.2 IMPLEMENTS Link κ Metadata

**When creating IMPLEMENTS links between protocol and artifacts:**

```cypher
MATCH (proto:SubEntity {name: "proto.membrane_stack"})
MATCH (sdk:SDK_Release {language: "typescript", version: "1.0.0"})
CREATE (proto)-[impl:IMPLEMENTS {
    kappa_down: 0.5,
    kappa_up: 0.5,
    learn_on: ["mission.completed", "usefulness.update", "harm.detected"],
    last_updated: datetime(),
    update_count: 0
}]->(sdk)
```

### 9.3 Conformance_Result Temporal

**Allow multiple results per SDK for trend tracking:**

```cypher
// Query recent conformance trends
MATCH (cr:Conformance_Result)-[:CERTIFIES_CONFORMANCE]->(sdk:SDK_Release {language: "typescript"})
WHERE cr.test_date > datetime() - duration({days: 30})
RETURN avg(cr.pass_rate) as avg_pass_rate,
       min(cr.pass_rate) as min_pass_rate,
       max(cr.pass_rate) as max_pass_rate,
       count(cr) as test_runs
```

---

## 10. Implementation Sequence

### Week 1: Foundation
1. ✅ **Day 1-2:** Implement `lint_inject` (injection validator)
   - File: `orchestration/mechanisms/injection_validator.py`
   - Integration: `consciousness_engine_v2.py`
   - Tests: Validate against L4 schemas, signature verification, governance

2. ✅ **Day 3:** Add Protocol_Version.status field to existing nodes
   - Update Phase 2 script: `tools/protocol/ingest_versioning_phase2.py`
   - Re-run to add status field

3. ✅ **Day 4:** Implement `mp law` CLI
   - File: `tools/mp_law_cli.py`
   - Commands: schemas, capabilities, governance, certify

### Week 2: Membranes & Missions
4. ✅ **Day 5-6:** Wire vertical membranes (L4↔L2↔L1)
   - Add IMPLEMENTS links with κ metadata
   - Implement κ learning on outcomes
   - Emit `membrane.permeability.updated` events

5. ✅ **Day 7-8:** Implement Gap Detector Service
   - File: `orchestration/services/gap_detector_service.py`
   - Detect unknown events, missing capabilities, governance violations
   - Emit mission.create to L2

### Week 3: CI & Codegen
6. ✅ **Day 9-10:** Build code generation pipeline
   - File: `tools/codegen/generate_sdk.py`
   - Generate TypeScript/Python stubs from L4
   - CI check for drift

7. ✅ **Day 11-12:** Implement certification pipeline
   - File: `tools/conformance/generate_tests.py`
   - File: `tools/conformance/record_results.py`
   - GitHub Actions workflow

### Week 4: Dashboards & Polish
8. ✅ **Day 13-14:** Wire dashboard queries
   - Compliance view (SDK conformance)
   - Governance health (rejection rates)
   - Membrane κ trends

9. ✅ **Day 15:** Integration testing
   - End-to-end: inject stimulus → lint_inject validates → gap detector sees unknown event → mission created → κ updated
   - Load testing: L4 query performance under load

10. ✅ **Day 16:** Documentation & handoff
    - Update SYNC.md with operational status
    - Write runbook for ops team
    - Training session for citizens

---

## 11. Acceptance Criteria

### ✅ Injection Validation
- [ ] `lint_inject` validates 100+ envelopes/sec without degradation
- [ ] Rejection events include machine-parsable L4 node references
- [ ] Cache hit rate >90% for schema/signature lookups

### ✅ Vertical Membranes
- [ ] IMPLEMENTS links exist between proto.membrane_stack and all SDK_Releases
- [ ] κ values update on mission.completed (±0.05 per outcome)
- [ ] membrane.permeability.updated events emitted with reason

### ✅ Certification
- [ ] CI generates conformance tests from L4
- [ ] Test runs write Conformance_Result back to L4
- [ ] Dashboards show pass rate trends per SDK

### ✅ Governance
- [ ] Key rotation completes without downtime
- [ ] Rate limits enforce per-tenant/per-component
- [ ] Governance violations emit actionable mission.create

### ✅ Queryable Law
- [ ] `mp law` CLI returns results in <200ms
- [ ] Citizens use law service to build integrations
- [ ] 100% of connector work starts from L4 queries

### ✅ Gap Detection
- [ ] Unknown events trigger mission.protocol_update
- [ ] Missing capabilities trigger mission.add_capability
- [ ] Missions delivered to L2, exported to L1 via membranes

### ✅ Code Generation
- [ ] SDK stubs regenerate on L4 schema changes
- [ ] CI fails on drift (hand-edits diverging from L4)
- [ ] Runtime rejects envelopes with unknown spec.rev

### ✅ Dashboards
- [ ] Compliance view shows SDK conformance (real-time)
- [ ] Governance health shows rejection breakdown
- [ ] Membrane κ trends visualize L4→impl strength

---

## 12. Risk Mitigation

### Performance Risk: L4 Query Overhead
**Mitigation:**
- Cache schema/policy lookups (60s TTL)
- Pre-load hot path queries at engine init
- Async query for non-critical validations

### Availability Risk: L4 Graph Down
**Mitigation:**
- Engine continues with cached policies (degraded mode)
- Emit `l4.unavailable` alert
- Queue conformance writes for replay

### Evolution Risk: Schema Breaking Changes
**Mitigation:**
- Require SUPERSEDES link for breaking changes
- Enforce overlap window (7 days minimum)
- Automated rollback if conformance drops below threshold

---

## 13. Success Metrics (3 Months)

1. **Injection Accept Rate:** >95% of valid envelopes accepted on first attempt
2. **Conformance Pass Rate:** All SDKs >90% conformance
3. **Gap Detection Latency:** Missions created within 10s of gap appearance
4. **κ Learning Convergence:** IMPLEMENTS κ values stabilize within 100 outcomes
5. **Drift Incidents:** Zero instances of hand-edited code diverging from L4
6. **Law Service Adoption:** 80% of connector work starts from `mp law` queries

---

## Appendix A: Example Queries

### Query: Complete injection validation chain
```cypher
MATCH (es:Event_Schema {name: "membrane.inject"})-[:REQUIRES_ENVELOPE]->(env:Envelope_Schema)
MATCH (es)-[:REQUIRES_SIG]->(ss:Signature_Suite)
MATCH (es)-[:MAPS_TO_TOPIC]->(ns:Topic_Namespace)<-[:GOVERNS]-(gp:Governance_Policy)
MATCH (tk:Tenant_Key {status: "active"})-[:SIGNED_WITH]->(ss)
RETURN env.fields as envelope_schema,
       es.fields as event_schema,
       ss.algorithm as sig_algorithm,
       gp.defaults as governance_policy,
       tk.pubkey as active_key
```

### Query: SDK implementation coverage
```cypher
MATCH (sdk:SDK_Release {language: "typescript"})-[impl:IMPLEMENTS]->(es:Event_Schema)
MATCH (cr:Conformance_Result)-[:CERTIFIES_CONFORMANCE]->(sdk)
RETURN sdk.version,
       count(DISTINCT es) as events_implemented,
       avg(cr.pass_rate) as avg_conformance,
       max(cr.test_date) as last_tested
```

### Query: Governance violation hotspots
```cypher
// Requires bus telemetry joined with L4
MATCH (es:Event_Schema)-[:MAPS_TO_TOPIC]->(ns:Topic_Namespace)
MATCH (gp:Governance_Policy)-[:GOVERNS]->(ns)
// JOIN with membrane.reject events (count by es.name)
RETURN es.name,
       gp.name as policy,
       count(*) as rejection_count
ORDER BY rejection_count DESC
LIMIT 10
```

---

## Appendix B: Glossary

- **L4 (Level 4):** Protocol layer containing normative rules, schemas, versions
- **L2 (Level 2):** Organizational layer (tenants, teams, projects)
- **L1 (Level 1):** Citizen layer (individual AI agents)
- **lint_inject:** Injection-time validator consulting L4 rules
- **κ (kappa):** Membrane permeability coefficient (learned strength)
- **IMPLEMENTS:** Link type connecting protocol specs to implementations
- **Conformance_Result:** CI test output recorded in L4
- **Gap Detection:** Service monitoring for protocol deviations
- **Queryable Law:** CLI/API exposing L4 rules for citizen consumption

---

**End of Specification**

**Status:** Ready for Implementation
**Next Steps:** Felix (lint_inject), Atlas (gap detector), Iris (dashboard queries)
**Review:** Ada (orchestration integration), Nicolas (architecture validation)
