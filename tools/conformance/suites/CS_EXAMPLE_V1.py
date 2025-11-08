"""
Example Conformance Suite

Demonstrates the structure and API for writing conformance test suites.
This is a template - copy and modify for actual test suites.

Author: Atlas
Date: 2025-11-08
"""

import sys
from pathlib import Path

# Add project root to path for importing runner types
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.conformance.runner import (
    ConformanceTest,
    TestResult,
    TestStatus,
    Criticality
)

# =============================================================================
# Suite Metadata (REQUIRED)
# =============================================================================

SUITE_ID = "CS_EXAMPLE_V1"
SUITE_NAME = "Example Conformance Suite"
SUITE_VERSION = "1.0"

# =============================================================================
# Test Definitions
# =============================================================================

def test_example_critical():
    """Example critical test - must pass"""
    # Perform validation
    condition = True  # Replace with actual test logic

    if condition:
        return TestResult(
            status=TestStatus.PASS,
            message="Critical validation passed"
        )
    else:
        return TestResult(
            status=TestStatus.FAIL,
            message="Critical validation failed",
            details={"expected": "X", "actual": "Y"}
        )


def test_example_high():
    """Example high-priority test"""
    try:
        # Test logic here
        result = 2 + 2

        if result == 4:
            return TestResult(
                status=TestStatus.PASS,
                message="Math works correctly"
            )
        else:
            return TestResult(
                status=TestStatus.FAIL,
                message=f"Math broken: 2+2={result}"
            )

    except Exception as e:
        return TestResult(
            status=TestStatus.ERROR,
            message=f"Exception during test: {e}"
        )


def test_example_skip():
    """Example skipped test"""
    return TestResult(
        status=TestStatus.SKIP,
        message="Test skipped - feature not implemented"
    )


def test_example_with_details():
    """Example test with detailed results"""
    return TestResult(
        status=TestStatus.PASS,
        message="Validation passed with details",
        details={
            "checked_items": 10,
            "passed_items": 10,
            "warnings": [],
            "metadata": {
                "version": "1.0",
                "validator": "example_validator"
            }
        }
    )


# =============================================================================
# Test Suite Definition (REQUIRED)
# =============================================================================

tests = [
    ConformanceTest(
        test_id="EXAMPLE_001",
        description="Critical validation test",
        criticality=Criticality.CRITICAL,
        test_fn=test_example_critical
    ),
    ConformanceTest(
        test_id="EXAMPLE_002",
        description="High-priority math test",
        criticality=Criticality.HIGH,
        test_fn=test_example_high
    ),
    ConformanceTest(
        test_id="EXAMPLE_003",
        description="Skipped test example",
        criticality=Criticality.MEDIUM,
        test_fn=test_example_skip
    ),
    ConformanceTest(
        test_id="EXAMPLE_004",
        description="Test with detailed results",
        criticality=Criticality.LOW,
        test_fn=test_example_with_details
    ),
]
