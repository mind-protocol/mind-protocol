# L4 Conformance Test Suite

Automated testing framework for validating L4 (Protocol Law) compliance across schemas, policies, and implementations.

## Overview

The conformance test suite validates that Mind Protocol implementations comply with L4 governance policies and protocol specifications. Test suites verify:

- **Schema compliance**: Events, topics, and data structures follow defined schemas
- **Policy adherence**: Implementations respect governance policies (LAW-001 through LAW-005)
- **Protocol correctness**: Behavior matches protocol specifications
- **Backward compatibility**: Schema evolution doesn't break existing systems

## Architecture

```
tools/conformance/
├── runner.py              # Test runner (discovers, executes, reports)
├── suites/                # Test suite definitions
│   ├── CS_EVENT_SCHEMA_V1.py
│   ├── CS_TOPIC_NAMESPACE_V1.py
│   ├── CS_PRIVACY_CONSENT_V1.py
│   ├── CS_SCHEMA_EVOLUTION_V1.py
│   ├── CS_BITEMPORAL_V1.py
│   └── CS_EXAMPLE_V1.py   # Example/template suite
└── README.md              # This file
```

## Usage

### Run All Suites

```bash
python tools/conformance/runner.py
```

### Run Specific Suite

```bash
python tools/conformance/runner.py --suite CS_EVENT_SCHEMA_V1
```

### Filter by Criticality

```bash
python tools/conformance/runner.py --criticality critical
python tools/conformance/runner.py --criticality high
```

### JSON Output

```bash
python tools/conformance/runner.py --json
python tools/conformance/runner.py --json --output results.json
```

### Combined Filters

```bash
python tools/conformance/runner.py --suite CS_EVENT_* --criticality critical --json
```

## Writing Conformance Suites

### Suite Structure

Each conformance suite is a Python module in `tools/conformance/suites/` with the following structure:

```python
from tools.conformance.runner import (
    ConformanceTest,
    TestResult,
    TestStatus,
    Criticality
)

# Suite metadata (REQUIRED)
SUITE_ID = "CS_MY_SUITE_V1"
SUITE_NAME = "My Conformance Suite"
SUITE_VERSION = "1.0"

# Test functions
def test_something():
    """Test description"""
    # Perform validation
    if condition_passes:
        return TestResult(
            status=TestStatus.PASS,
            message="Validation succeeded"
        )
    else:
        return TestResult(
            status=TestStatus.FAIL,
            message="Validation failed",
            details={"expected": "X", "actual": "Y"}
        )

# Test suite definition (REQUIRED)
tests = [
    ConformanceTest(
        test_id="MY_SUITE_001",
        description="Test something critical",
        criticality=Criticality.CRITICAL,
        test_fn=test_something
    ),
    # ... more tests
]
```

### Test Criticality Levels

- **CRITICAL**: Must pass (100% required) - Core protocol invariants
- **HIGH**: Should pass (95% required) - Important functionality
- **MEDIUM**: Nice to pass (80% required) - Best practices
- **LOW**: Optional (no requirement) - Informational

### Test Status Values

- **PASS**: Test succeeded
- **FAIL**: Test failed (validation error)
- **SKIP**: Test skipped (feature not implemented)
- **ERROR**: Test error (exception during execution)

### TestResult Fields

```python
TestResult(
    status=TestStatus.PASS,        # Required: PASS/FAIL/SKIP/ERROR
    message="Human-readable result", # Required: Description
    details={                        # Optional: Structured data
        "checked_items": 10,
        "failed_items": [],
        "metadata": {...}
    }
)
```

## Pass Rate Requirements

| Criticality | Pass Rate | Usage |
|-------------|-----------|-------|
| CRITICAL    | 100%      | Core protocol invariants (breaking changes) |
| HIGH        | 95%       | Important functionality (major features) |
| MEDIUM      | 80%       | Best practices (recommendations) |
| LOW         | N/A       | Informational (metrics/warnings) |

Suite status: ✅ PASS if overall pass rate ≥ 95%

## Planned Conformance Suites

### CS_EVENT_SCHEMA_V1 (P0)
Validates L3_Event schema compliance:
- Required fields presence
- Type validation
- Privacy metadata structure
- Bitemporal metadata structure

### CS_TOPIC_NAMESPACE_V1 (P0)
Validates topic namespace structure:
- Namespace ownership validation
- Topic creation policy
- Naming convention compliance

### CS_PRIVACY_CONSENT_V1 (P1)
Validates privacy extension compliance:
- Privacy metadata presence
- Consent tracking
- PII detection and handling

### CS_SCHEMA_EVOLUTION_V1 (P1)
Validates schema versioning:
- Version increment validation
- Backward compatibility checks
- Breaking change detection

### CS_BITEMPORAL_V1 (P1)
Validates bitemporal metadata:
- Temporal field presence
- Timeline integrity
- Temporal query correctness

## CI Integration

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python tools/conformance/runner.py --criticality critical
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ COMMIT BLOCKED: Critical conformance tests failed!"
    exit 1
fi
echo "✅ Critical conformance tests passed"
exit 0
```

### GitHub Actions

```yaml
name: Conformance Tests
on: [push, pull_request]
jobs:
  conformance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run conformance tests
        run: |
          python tools/conformance/runner.py --json --output conformance-results.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: conformance-results
          path: conformance-results.json
```

## Example Output

```
================================================================================
Running Suite: CS_EXAMPLE_V1 - Example Conformance Suite
================================================================================

[1/4] EXAMPLE_001: Critical validation test
  Criticality: critical
  ✅ PASS - Critical validation passed
  Duration: 0.01ms

[2/4] EXAMPLE_002: High-priority math test
  Criticality: high
  ✅ PASS - Math works correctly
  Duration: 0.01ms

================================================================================
Suite Results: CS_EXAMPLE_V1
================================================================================
Total Tests: 4
Passed: 3 (75.0%)
Failed: 0
Skipped: 1
Errors: 0
Duration: 0.09ms

Status: ❌ FAIL (requires 95% pass rate)
================================================================================
```

## JSON Output Format

```json
{
  "executed_at": "2025-11-08T19:25:28.683837",
  "total_suites": 1,
  "passed_suites": 0,
  "failed_suites": 1,
  "suites": [
    {
      "suite_id": "CS_EXAMPLE_V1",
      "suite_name": "Example Conformance Suite",
      "suite_version": "1.0",
      "executed_at": "2025-11-08T19:25:28.683751",
      "total_tests": 4,
      "passed": 3,
      "failed": 0,
      "skipped": 1,
      "errors": 0,
      "pass_rate": 75.0,
      "meets_requirements": false,
      "test_results": [
        {
          "test_id": "EXAMPLE_001",
          "description": "Critical validation test",
          "criticality": "critical",
          "status": "pass",
          "message": "Critical validation passed",
          "details": {},
          "duration_ms": 0.01
        }
      ],
      "duration_ms": 0.09
    }
  ]
}
```

## Development Workflow

1. **Write test suite**: Create `CS_MY_SUITE_V1.py` in `suites/`
2. **Run locally**: `python tools/conformance/runner.py --suite CS_MY_SUITE_V1`
3. **Fix failures**: Iterate until pass rate ≥ 95%
4. **Commit**: Pre-commit hook runs critical tests
5. **CI validation**: GitHub Actions runs full suite

## References

- **Specification**: `docs/L4-law/CONFORMANCE_SUITE_SPECIFICATION.md`
- **L4 Laws**: `docs/L4-law/LAW-*.md`
- **Work Items**: Query FalkorDB for `U4_Work_Item` nodes with task IDs CS-*

## Status

| Component | Status |
|-----------|--------|
| Runner infrastructure | ✅ Implemented |
| Suite discovery | ✅ Implemented |
| Test execution | ✅ Implemented |
| Filtering (suite/criticality) | ✅ Implemented |
| JSON output | ✅ Implemented |
| Example suite | ✅ Implemented |
| CS_EVENT_SCHEMA_V1 | ⭕ TODO (CS-IMPL-001) |
| CS_TOPIC_NAMESPACE_V1 | ⭕ TODO (CS-IMPL-002) |
| CS_PRIVACY_CONSENT_V1 | ⭕ TODO (CS-IMPL-003) |
| CS_SCHEMA_EVOLUTION_V1 | ⭕ TODO (CS-IMPL-004) |
| CS_BITEMPORAL_V1 | ⭕ TODO (CS-IMPL-005) |
| Pre-commit integration | ⭕ TODO (CS-CI-001) |
| GitHub Actions CI | ⭕ TODO (CS-CI-002) |

---

**Created**: 2025-11-08
**Author**: Atlas (Infrastructure Engineer)
**Version**: 1.0
