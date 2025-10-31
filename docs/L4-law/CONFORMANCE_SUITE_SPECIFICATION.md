# L4 Conformance Suite Specification

**Status:** PROPOSED - Awaiting team review (Felix, Atlas, Ada)
**Author:** Luca Vellumhand (Consciousness Substrate Architect)
**Date:** 2025-10-31
**Version:** 1.0.0

---

## Executive Summary

**Conformance Suites = Executable test batteries that validate schemas, policies, and protocol implementations against L4 law.**

**Core Principle:** "Active" bundle status requires ≥95% conformance pass rate. Conformance results are stored as U4_Conformance_Result nodes with attestation evidence.

---

## What is a Conformance Suite?

**Definition:** A conformance suite is a versioned collection of test cases that validate whether a subject (schema, policy, implementation) conforms to its specification.

**Purpose:**
- **Quality Gate:** Prevent broken schemas from being marked "active"
- **Regression Detection:** Catch when implementations drift from spec
- **Public Proof:** Provide auditable evidence of conformance
- **Migration Safety:** Validate that breaking changes preserve semantics

**Scope:**
- Schema validation (Event_Schema, Envelope_Schema, Topic_Namespace)
- Policy compliance (Governance_Policy enforcement)
- Implementation conformance (consciousness engines, membrane validators)
- Type Index integrity (U3_/U4_ type definitions)

---

## Conformance Suite Structure

### U4_Conformance_Suite Node

```cypher
CREATE (cs:U4_Conformance_Suite {
  type_name: "U4_Conformance_Suite",
  universality: "U4",
  level: "L4",
  suite_id: "CS_EVENT_SCHEMA_V1",
  name: "Event Schema Validation Suite",
  version: "1.0.0",
  description: "Validates Event_Schema nodes for required fields, relationships, JSON Schema validity",
  test_case_count: 24,
  created_at: "2025-10-31T00:00:00Z",
  updated_at: "2025-10-31T00:00:00Z",
  maintainer: "protocol/Subentity/schema-registry",
  attestation_ref: "protocol/Attestation/suite-approval-CS_EVENT_SCHEMA_V1"
})
```

### Properties

- **suite_id** (string, unique) - Identifier (e.g., CS_EVENT_SCHEMA_V1)
- **name** (string) - Human-readable name
- **version** (string) - Semantic version of suite
- **description** (string) - What this suite validates
- **test_case_count** (int) - Number of test cases in suite
- **maintainer** (string) - Reference to maintaining subentity/team
- **attestation_ref** (string) - Link to approval attestation

### Relationships

```cypher
// Governance
(registry:U4_Subentity {role_or_topic:"schema-registry"})-[:GOVERNS]->(cs:U4_Conformance_Suite)

// Target specification
(cs:U4_Conformance_Suite)-[:CERTIFIES_CONFORMANCE]->(target:U4_Event_Schema|U4_Envelope_Schema|U4_Topic_Namespace|U4_Governance_Policy)

// Test cases
(cs:U4_Conformance_Suite)-[:CONTAINS_TEST]->(tc:U4_Test_Case)

// Results
(cs:U4_Conformance_Suite)<-[:EXECUTED_SUITE]-(result:U4_Conformance_Result)

// Evidence
(cs:U4_Conformance_Suite)-[:EVIDENCED_BY]->(att:Attestation)
```

---

## Test Case Structure

### U4_Test_Case Node

```cypher
CREATE (tc:U4_Test_Case {
  type_name: "U4_Test_Case",
  universality: "U4",
  level: "L4",
  test_id: "TC_EVENT_SCHEMA_001",
  name: "Event schema must have schema_uri property",
  description: "Validates that Event_Schema nodes have non-null schema_uri pointing to valid JSON Schema",
  category: "required_field",
  severity: "critical",
  test_type: "graph_query",
  query: "MATCH (es:Event_Schema) WHERE es.schema_uri IS NULL RETURN es.name",
  expected_result: "[]",
  timeout_ms: 5000,
  created_at: "2025-10-31T00:00:00Z"
})
```

### Test Categories

**1. required_field** - Validates presence of required node properties
**2. required_relationship** - Validates existence of required edges
**3. semantic_validity** - Validates field values make semantic sense
**4. schema_validity** - Validates JSON Schema is well-formed and reachable
**5. policy_compliance** - Validates adherence to governance policies
**6. implementation_behavior** - Validates runtime behavior matches spec

### Test Types

**graph_query** - Cypher query that returns violations (empty = pass)
**json_schema** - JSON Schema validation against document
**api_endpoint** - HTTP request/response validation
**event_emission** - Validate event structure and metadata
**script** - Custom validation script (Python, Bash)

### Severity Levels

**critical** - Must pass for ≥95% threshold
**high** - Should pass, degrades quality score
**medium** - Nice to have, informational
**low** - Advisory only

---

## Conformance Result Structure

### U4_Conformance_Result Node

```cypher
CREATE (cr:U4_Conformance_Result {
  type_name: "U4_Conformance_Result",
  universality: "U4",
  level: "L4",
  result_id: "CR_20251031_EVENT_SCHEMA_V1",
  suite_ref: "protocol/U4_Conformance_Suite/CS_EVENT_SCHEMA_V1",
  subject_ref: "protocol/Schema_Bundle/v1.2.0",
  test_case_count: 24,
  passed: 23,
  failed: 1,
  skipped: 0,
  pass_rate: 0.9583,
  critical_failures: 0,
  execution_time_ms: 1247,
  timestamp: "2025-10-31T05:00:00Z",
  executor: "ci-runner-prod-01",
  attestation_ref: "protocol/Attestation/conformance-result-20251031",
  proof_uri: "l4://conformance/results/CR_20251031_EVENT_SCHEMA_V1.json",
  commit_hash: "abc123def456"
})
```

### Properties

- **result_id** (string, unique) - Identifier for this test run
- **suite_ref** (string) - Which suite was executed
- **subject_ref** (string) - What was tested (bundle, schema, implementation)
- **test_case_count** (int) - Total tests in suite
- **passed** (int) - Number of passed tests
- **failed** (int) - Number of failed tests
- **skipped** (int) - Number of skipped tests
- **pass_rate** (float, 0.0-1.0) - passed / (passed + failed)
- **critical_failures** (int) - Number of failed critical-severity tests
- **execution_time_ms** (int) - Total execution time
- **timestamp** (datetime) - When test ran
- **executor** (string) - CI runner or manual executor ID
- **attestation_ref** (string) - Evidence attestation
- **proof_uri** (string) - Link to detailed results JSON
- **commit_hash** (string) - Git commit that was tested

### Pass/Fail Criteria

**PASS (subject can be marked "active"):**
- pass_rate ≥ 0.95 (95%)
- critical_failures = 0

**FAIL (subject remains "draft" or moves to "yanked"):**
- pass_rate < 0.95
- critical_failures > 0

### Relationships

```cypher
// Suite execution
(cr:U4_Conformance_Result)-[:EXECUTED_SUITE]->(cs:U4_Conformance_Suite)

// Test subject
(cr:U4_Conformance_Result)-[:TESTED_SUBJECT]->(subject:U4_Schema_Bundle|U4_Event_Schema|...)

// Individual test results
(cr:U4_Conformance_Result)-[:HAS_TEST_RESULT]->(tr:U4_Test_Result)

// Evidence
(cr:U4_Conformance_Result)-[:EVIDENCED_BY]->(att:Attestation)

// Previous runs (for trend analysis)
(cr_new:U4_Conformance_Result)-[:SUPERSEDES]->(cr_old:U4_Conformance_Result)
```

---

## Conformance Suite Catalog

### CS_EVENT_SCHEMA_V1 - Event Schema Validation

**Validates:** Event_Schema nodes

**Critical Test Cases:**
1. TC_EVENT_SCHEMA_001: Must have schema_uri property
2. TC_EVENT_SCHEMA_002: Must have version property (semver format)
3. TC_EVENT_SCHEMA_003: Must have exactly one MAPS_TO_TOPIC edge
4. TC_EVENT_SCHEMA_004: Must have exactly one REQUIRES_SIG edge
5. TC_EVENT_SCHEMA_005: Must have governance_strictness (STRICT|FLEX)
6. TC_EVENT_SCHEMA_006: schema_uri must be reachable (HTTP 200 or l4:// resolvable)
7. TC_EVENT_SCHEMA_007: JSON Schema must parse without errors
8. TC_EVENT_SCHEMA_008: Must have direction (inject|broadcast|request|response)

**High Priority Test Cases:**
9. TC_EVENT_SCHEMA_009: Should have summary/description
10. TC_EVENT_SCHEMA_010: MAPS_TO_TOPIC target must exist and be active
11. TC_EVENT_SCHEMA_011: REQUIRES_SIG target must exist
12. TC_EVENT_SCHEMA_012: JSON Schema should include required fields list

**Total:** 24 test cases (8 critical, 16 high/medium)

---

### CS_TOPIC_NAMESPACE_V1 - Topic Namespace Validation

**Validates:** Topic_Namespace nodes

**Critical Test Cases:**
1. TC_TOPIC_NS_001: Must have namespace property (topic pattern)
2. TC_TOPIC_NS_002: Must have name property
3. TC_TOPIC_NS_003: namespace must be valid topic pattern (no wildcards in ID)
4. TC_TOPIC_NS_004: Must have at least one MEMBER_OF edge to U4_Subentity

**High Priority Test Cases:**
5. TC_TOPIC_NS_005: Should have description
6. TC_TOPIC_NS_006: Should have version
7. TC_TOPIC_NS_007: Namespace pattern should not overlap with existing namespaces (conflict detection)

**Total:** 12 test cases (4 critical, 8 high/medium)

---

### CS_GOVERNANCE_POLICY_V1 - Governance Policy Validation

**Validates:** Governance_Policy nodes

**Critical Test Cases:**
1. TC_GOV_POLICY_001: Must have policy_id property
2. TC_GOV_POLICY_002: Must have uri property (policy document location)
3. TC_GOV_POLICY_003: Must have hash property (policy content hash)
4. TC_GOV_POLICY_004: Must have at least one GOVERNS edge
5. TC_GOV_POLICY_005: hash must match document content (integrity check)

**High Priority Test Cases:**
6. TC_GOV_POLICY_006: Should have version
7. TC_GOV_POLICY_007: Should have description/summary
8. TC_GOV_POLICY_008: GOVERNS targets should be valid nodes
9. TC_GOV_POLICY_009: Policy document should be reachable

**Total:** 15 test cases (5 critical, 10 high/medium)

---

### CS_SIGNATURE_SUITE_V1 - Signature Suite Validation

**Validates:** Signature_Suite nodes

**Critical Test Cases:**
1. TC_SIG_SUITE_001: Must have suite_id property
2. TC_SIG_SUITE_002: Must have algo property (signature algorithm)
3. TC_SIG_SUITE_003: algo must be supported (ed25519, secp256k1, etc.)
4. TC_SIG_SUITE_004: Must have hash_algos array

**High Priority Test Cases:**
5. TC_SIG_SUITE_005: Should have description
6. TC_SIG_SUITE_006: Should have example verification code
7. TC_SIG_SUITE_007: hash_algos should be non-empty

**Total:** 10 test cases (4 critical, 6 high/medium)

---

### CS_TYPE_INDEX_V1 - Type Index Validation

**Validates:** Type Index integrity

**Critical Test Cases:**
1. TC_TYPE_INDEX_001: Every U4_Type_Index node must have type_name
2. TC_TYPE_INDEX_002: Every U4_Type_Index node must have schema_ref
3. TC_TYPE_INDEX_003: Every U4_Type_Index node must have exactly one PUBLISHES_SCHEMA edge
4. TC_TYPE_INDEX_004: No duplicate type_name for active types
5. TC_TYPE_INDEX_005: All ALIASES edges must be symmetric (bidirectional)
6. TC_TYPE_INDEX_006: schema_ref must be reachable
7. TC_TYPE_INDEX_007: Every type must have attestation_ref evidence

**High Priority Test Cases:**
8. TC_TYPE_INDEX_008: Should have version
9. TC_TYPE_INDEX_009: Should have description
10. TC_TYPE_INDEX_010: Should have universality (U3 or U4)
11. TC_TYPE_INDEX_011: universality should match type_name prefix

**Total:** 18 test cases (7 critical, 11 high/medium)

---

### CS_SCHEMA_BUNDLE_V1 - Schema Bundle Validation

**Validates:** Schema_Bundle nodes

**Critical Test Cases:**
1. TC_BUNDLE_001: Must have semver property (semantic version)
2. TC_BUNDLE_002: Must have hash property (bundle content hash)
3. TC_BUNDLE_003: Must have status (draft|active|deprecated|yanked)
4. TC_BUNDLE_004: Must have at least one PUBLISHES_SCHEMA edge
5. TC_BUNDLE_005: hash must match bundle content
6. TC_BUNDLE_006: If status=active, pass_rate must be ≥0.95

**High Priority Test Cases:**
7. TC_BUNDLE_007: Should have description
8. TC_BUNDLE_008: PUBLISHES_SCHEMA targets should be valid schemas
9. TC_BUNDLE_009: If status=deprecated, should have SUPERSEDES edge
10. TC_BUNDLE_010: semver should be monotonically increasing

**Total:** 16 test cases (6 critical, 10 high/medium)

---

## Implementation Architecture

### Conformance Runner (CI Service)

**Location:** `tools/conformance/runner.py`

**Responsibilities:**
1. Load conformance suite definitions from protocol graph
2. Execute test cases (graph queries, JSON Schema validation, API tests)
3. Record pass/fail results with timing
4. Calculate pass_rate and critical_failures
5. Create U4_Conformance_Result nodes
6. Generate detailed proof JSON
7. Create attestation evidence
8. Broadcast `conformance.result.recorded` event

**Execution Modes:**
- **Pre-commit:** Run on changed schemas before git commit
- **PR Check:** Run full suite on pull request
- **Scheduled:** Run nightly on all active bundles
- **Manual:** On-demand execution for debugging

---

### Test Case Executor

**Responsibilities:**
1. Parse test case definition (query, expected_result, timeout)
2. Execute test based on test_type
3. Compare actual vs expected results
4. Record pass/fail with error message if failed
5. Capture execution time

**Test Type Handlers:**

**graph_query:**
```python
def execute_graph_query(test_case):
    result = graph.query(test_case.query)
    actual = result.result_set
    expected = json.loads(test_case.expected_result)
    return actual == expected
```

**json_schema:**
```python
def execute_json_schema(test_case):
    schema = load_json_schema(test_case.schema_uri)
    document = load_document(test_case.document_uri)
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(document))
    return len(errors) == 0
```

**api_endpoint:**
```python
def execute_api_endpoint(test_case):
    response = requests.request(
        method=test_case.method,
        url=test_case.endpoint,
        json=test_case.request_body
    )
    return (response.status_code == test_case.expected_status
            and response.json() == test_case.expected_body)
```

---

### Result Storage

**Graph Storage:**
```cypher
// Create result node
CREATE (cr:U4_Conformance_Result {
  result_id: 'CR_20251031_EVENT_SCHEMA_V1',
  // ... properties
})

// Link to suite
MATCH (cs:U4_Conformance_Suite {suite_id: 'CS_EVENT_SCHEMA_V1'})
CREATE (cr)-[:EXECUTED_SUITE]->(cs)

// Link to subject
MATCH (bundle:U4_Schema_Bundle {semver: '1.2.0'})
CREATE (cr)-[:TESTED_SUBJECT]->(bundle)

// Link to attestation
MATCH (att:Attestation {attestation_id: 'protocol/Attestation/...'})
CREATE (cr)-[:EVIDENCED_BY]->(att)
```

**JSON Proof Document:**
```json
{
  "result_id": "CR_20251031_EVENT_SCHEMA_V1",
  "suite": {
    "suite_id": "CS_EVENT_SCHEMA_V1",
    "version": "1.0.0",
    "name": "Event Schema Validation Suite"
  },
  "subject": {
    "type": "U4_Schema_Bundle",
    "ref": "protocol/Schema_Bundle/v1.2.0",
    "semver": "1.2.0"
  },
  "summary": {
    "total": 24,
    "passed": 23,
    "failed": 1,
    "skipped": 0,
    "pass_rate": 0.9583,
    "critical_failures": 0
  },
  "test_results": [
    {
      "test_id": "TC_EVENT_SCHEMA_001",
      "name": "Event schema must have schema_uri property",
      "status": "passed",
      "execution_time_ms": 45
    },
    {
      "test_id": "TC_EVENT_SCHEMA_009",
      "name": "Should have summary/description",
      "status": "failed",
      "error": "3 Event_Schema nodes missing summary property",
      "failed_subjects": [
        "protocol/Event_Schema/example.event.1",
        "protocol/Event_Schema/example.event.2",
        "protocol/Event_Schema/example.event.3"
      ],
      "execution_time_ms": 52
    }
  ],
  "timestamp": "2025-10-31T05:00:00Z",
  "executor": "ci-runner-prod-01",
  "commit_hash": "abc123def456",
  "attestation_ref": "protocol/Attestation/conformance-result-20251031"
}
```

---

## CI Integration

### Pre-commit Hook

**Location:** `.claude/hooks/pre-commit-conformance.sh`

```bash
#!/bin/bash
# Run conformance tests on modified schemas before commit

# Detect modified schemas
CHANGED_SCHEMAS=$(git diff --cached --name-only | grep 'tools/protocol/.*\.py')

if [ -n "$CHANGED_SCHEMAS" ]; then
    echo "🔍 Running conformance tests on modified schemas..."

    python3 tools/conformance/runner.py \
        --suite CS_EVENT_SCHEMA_V1 \
        --changed-only \
        --fail-on-critical

    if [ $? -ne 0 ]; then
        echo "❌ Conformance tests failed - fix violations before committing"
        exit 1
    fi
fi
```

---

### GitHub Actions

**Location:** `.github/workflows/conformance-checks.yml`

```yaml
name: L4 Conformance Checks

on:
  pull_request:
    paths:
      - 'tools/protocol/**'
      - 'orchestration/**'
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  conformance-tests:
    runs-on: ubuntu-latest

    services:
      falkordb:
        image: falkordb/falkordb:latest
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install falkordb jsonschema requests

      - name: Load protocol graph
        run: |
          python3 tools/protocol/seed_protocol_graph.py

      - name: Run Event Schema conformance
        run: |
          python3 tools/conformance/runner.py \
            --suite CS_EVENT_SCHEMA_V1 \
            --output results/event_schema.json

      - name: Run Topic Namespace conformance
        run: |
          python3 tools/conformance/runner.py \
            --suite CS_TOPIC_NAMESPACE_V1 \
            --output results/topic_namespace.json

      - name: Run Type Index conformance
        run: |
          python3 tools/conformance/runner.py \
            --suite CS_TYPE_INDEX_V1 \
            --output results/type_index.json

      - name: Check pass rates
        run: |
          python3 tools/conformance/check_pass_rates.py \
            --threshold 0.95 \
            --results results/*.json

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: conformance-results
          path: results/

      - name: Record results in graph
        if: github.ref == 'refs/heads/main'
        run: |
          python3 tools/conformance/record_results.py \
            --results results/*.json \
            --commit ${{ github.sha }}
```

---

## Dashboard Integration

### Conformance Badge

**Display on schema registry page:**

```
✅ Conformance: 98.5% (95/96 passed)
   Last run: 2025-10-31 05:00 UTC
   Commit: abc123d
```

**Color coding:**
- Green (✅): pass_rate ≥ 0.95, critical_failures = 0
- Yellow (⚠️): pass_rate ≥ 0.90, critical_failures = 0
- Red (❌): pass_rate < 0.90 or critical_failures > 0

---

### Conformance Trend Chart

**Show pass_rate over time:**
- X-axis: timestamp (last 30 days)
- Y-axis: pass_rate (0.0 - 1.0)
- Threshold line at 0.95
- Color: Green above threshold, red below

---

### Test Case Drill-down

**Click on conformance badge to see:**
- List of all test cases in suite
- Pass/fail status for each
- Error messages for failures
- Execution time per test
- Link to detailed proof JSON

---

## Migration Path

### Phase 1: Core Suite Implementation (Week 1)
1. Create CS_EVENT_SCHEMA_V1 suite with 8 critical tests
2. Implement conformance runner (graph_query type only)
3. Test on protocol graph, verify 100% pass rate
4. Create first U4_Conformance_Result node

### Phase 2: CI Integration (Week 1)
5. Wire runner into pre-commit hook
6. Add GitHub Actions workflow
7. Test on PR with intentional violations
8. Verify CI fails correctly

### Phase 3: Additional Suites (Week 2)
9. Create CS_TOPIC_NAMESPACE_V1
10. Create CS_GOVERNANCE_POLICY_V1
11. Create CS_TYPE_INDEX_V1
12. Run all suites in CI

### Phase 4: Dashboard (Week 2)
13. Add conformance badge to schema registry page
14. Create trend chart
15. Add test case drill-down

### Phase 5: Advanced Features (Week 3+)
16. Add json_schema test type support
17. Add api_endpoint test type support
18. Implement auto-fix suggestions
19. Add conformance notifications (Slack, email)

---

## Success Criteria

- [ ] All 5 core conformance suites defined (Event_Schema, Topic_Namespace, Governance_Policy, Signature_Suite, Type_Index)
- [ ] Conformance runner executes suites and stores results in protocol graph
- [ ] CI fails PRs that reduce pass_rate below 95%
- [ ] Dashboard displays conformance badge with current pass_rate
- [ ] Schema bundles cannot be marked "active" without ≥95% pass_rate
- [ ] Conformance results include attestation evidence
- [ ] Nightly conformance runs detect regressions

---

## Open Questions for Team

### For Felix (Implementation):
1. Should conformance runner be part of consciousness engines or separate service?
2. Preferred test isolation strategy (separate graph, rollback transactions)?
3. Performance target for full suite execution? (suggested: <5 minutes)

### For Atlas (Infrastructure):
1. Where to store proof JSON documents? (S3, GitHub artifacts, L4 storage?)
2. How long to retain conformance result history? (suggested: 90 days)
3. Should conformance failures trigger alerts? (suggested: yes for production)

### For Ada (Architecture):
1. Should conformance be required for schema_registry only, or all L4 subentities?
2. How to handle conformance for external protocol integrations?
3. Should ≥95% threshold be configurable per suite, or protocol-wide constant?

---

## Next Steps

1. **Team Review:** Felix + Atlas + Ada review this specification
2. **Approval:** Nicolas approves conformance as L4 quality gate
3. **Implementation Sprint Planning:** Break into tickets with estimates
4. **Phase 1 Kickoff:** Felix implements core runner, Atlas sets up CI
5. **Testing:** Validate on protocol graph with real schemas
6. **Rollout:** Enable in CI for all PRs touching protocol graph

