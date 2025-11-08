#!/usr/bin/env python3
"""
Conformance Test Runner

Discovers and executes L4 conformance test suites defined in tools/conformance/suites/.
Validates schema compliance, policy adherence, and protocol correctness.

Usage:
    python tools/conformance/runner.py                          # Run all suites
    python tools/conformance/runner.py --suite CS_EVENT_SCHEMA  # Run specific suite
    python tools/conformance/runner.py --criticality critical   # Run only critical tests
    python tools/conformance/runner.py --json                   # Output JSON results

Suite Structure:
    tools/conformance/suites/
        CS_EVENT_SCHEMA_V1.py
        CS_TOPIC_NAMESPACE_V1.py
        ...

Each suite module must define:
    - SUITE_ID: str (e.g., "CS_EVENT_SCHEMA_V1")
    - SUITE_NAME: str (e.g., "Event Schema Conformance")
    - SUITE_VERSION: str (e.g., "1.0")
    - tests: List[ConformanceTest]

ConformanceTest:
    - test_id: str
    - description: str
    - criticality: "critical" | "high" | "medium" | "low"
    - test_fn: Callable[[], TestResult]

Author: Atlas
Date: 2025-11-08
"""

import sys
import json
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# Type Definitions
# =============================================================================

class Criticality(Enum):
    """Test criticality levels"""
    CRITICAL = "critical"  # Must pass (100% required)
    HIGH = "high"          # Should pass (95% required)
    MEDIUM = "medium"      # Nice to pass (80% required)
    LOW = "low"            # Optional (no requirement)


class TestStatus(Enum):
    """Test execution status"""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class TestResult:
    """Result from a single test execution"""
    status: TestStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    duration_ms: float = 0.0


@dataclass
class ConformanceTest:
    """Definition of a conformance test"""
    test_id: str
    description: str
    criticality: Criticality
    test_fn: Callable[[], TestResult]


@dataclass
class ConformanceSuite:
    """Collection of related conformance tests"""
    suite_id: str
    suite_name: str
    suite_version: str
    tests: List[ConformanceTest]


@dataclass
class SuiteExecutionResult:
    """Results from executing a suite"""
    suite_id: str
    suite_name: str
    suite_version: str
    executed_at: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    pass_rate: float
    meets_requirements: bool
    test_results: List[Dict[str, Any]]
    duration_ms: float


# =============================================================================
# Suite Discovery
# =============================================================================

SUITES_DIR = Path(__file__).parent / "suites"


def discover_suites() -> List[Path]:
    """Discover all conformance suite modules in suites/ directory"""
    if not SUITES_DIR.exists():
        print(f"⚠️  Suites directory not found: {SUITES_DIR}")
        return []

    suite_files = sorted(SUITES_DIR.glob("CS_*.py"))
    print(f"📂 Discovered {len(suite_files)} suite(s) in {SUITES_DIR}")

    return suite_files


def load_suite(suite_path: Path) -> Optional[ConformanceSuite]:
    """Load a conformance suite module and extract suite definition"""

    try:
        # Import module dynamically
        spec = importlib.util.spec_from_file_location(suite_path.stem, suite_path)
        if not spec or not spec.loader:
            print(f"⚠️  Could not load spec for {suite_path.name}")
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract required attributes
        suite_id = getattr(module, "SUITE_ID", None)
        suite_name = getattr(module, "SUITE_NAME", None)
        suite_version = getattr(module, "SUITE_VERSION", "1.0")
        tests = getattr(module, "tests", [])

        if not suite_id or not suite_name:
            print(f"⚠️  Suite {suite_path.name} missing SUITE_ID or SUITE_NAME")
            return None

        if not tests:
            print(f"⚠️  Suite {suite_path.name} has no tests defined")
            return None

        print(f"✅ Loaded suite: {suite_id} ({len(tests)} tests)")

        return ConformanceSuite(
            suite_id=suite_id,
            suite_name=suite_name,
            suite_version=suite_version,
            tests=tests
        )

    except Exception as e:
        print(f"❌ Error loading suite {suite_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# Test Execution
# =============================================================================

def execute_test(test: ConformanceTest) -> Dict[str, Any]:
    """Execute a single conformance test and capture result"""

    start_time = datetime.now()

    try:
        # Run test function
        result = test.test_fn()

        # Check if result has required attributes (duck typing)
        if not (hasattr(result, 'status') and hasattr(result, 'message')):
            result = TestResult(
                status=TestStatus.ERROR,
                message=f"Test returned invalid type: {type(result)}",
                details={"returned_value": str(result)}
            )

    except Exception as e:
        # Catch any exceptions during test execution
        result = TestResult(
            status=TestStatus.ERROR,
            message=f"Test raised exception: {str(e)}",
            details={"exception_type": type(e).__name__}
        )
        import traceback
        result.details["traceback"] = traceback.format_exc()

    end_time = datetime.now()
    duration_ms = (end_time - start_time).total_seconds() * 1000

    # Extract status value (handle both enum and string)
    status_value = result.status.value if hasattr(result.status, 'value') else str(result.status)

    return {
        "test_id": test.test_id,
        "description": test.description,
        "criticality": test.criticality.value,
        "status": status_value,
        "message": result.message,
        "details": result.details or {} if hasattr(result, 'details') else {},
        "duration_ms": duration_ms
    }


def execute_suite(
    suite: ConformanceSuite,
    criticality_filter: Optional[Criticality] = None
) -> SuiteExecutionResult:
    """Execute all tests in a suite (optionally filtered by criticality)"""

    print(f"\n{'=' * 80}")
    print(f"Running Suite: {suite.suite_id} - {suite.suite_name}")
    print(f"{'=' * 80}")

    start_time = datetime.now()

    # Filter tests by criticality if specified
    tests_to_run = suite.tests
    if criticality_filter:
        # Use value comparison to handle different enum instances
        filter_value = criticality_filter.value
        tests_to_run = [
            t for t in suite.tests
            if (t.criticality.value if hasattr(t.criticality, 'value') else str(t.criticality)) == filter_value
        ]
        print(f"Filtering: {len(tests_to_run)} {criticality_filter.value} tests")

    test_results = []
    passed = 0
    failed = 0
    skipped = 0
    errors = 0

    for i, test in enumerate(tests_to_run, 1):
        print(f"\n[{i}/{len(tests_to_run)}] {test.test_id}: {test.description}")
        print(f"  Criticality: {test.criticality.value}")

        result = execute_test(test)
        test_results.append(result)

        status = TestStatus(result["status"])

        if status == TestStatus.PASS:
            passed += 1
            print(f"  ✅ PASS - {result['message']}")
        elif status == TestStatus.FAIL:
            failed += 1
            print(f"  ❌ FAIL - {result['message']}")
        elif status == TestStatus.SKIP:
            skipped += 1
            print(f"  ⭕ SKIP - {result['message']}")
        elif status == TestStatus.ERROR:
            errors += 1
            print(f"  💥 ERROR - {result['message']}")

        print(f"  Duration: {result['duration_ms']:.2f}ms")

    end_time = datetime.now()
    total_duration_ms = (end_time - start_time).total_seconds() * 1000

    # Calculate pass rate
    total_tests = len(tests_to_run)
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0.0

    # Determine if suite meets requirements (95% pass rate)
    meets_requirements = pass_rate >= 95.0

    print(f"\n{'=' * 80}")
    print(f"Suite Results: {suite.suite_id}")
    print(f"{'=' * 80}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed} ({pass_rate:.1f}%)")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"Duration: {total_duration_ms:.2f}ms")
    print(f"\nStatus: {'✅ PASS' if meets_requirements else '❌ FAIL'} (requires 95% pass rate)")
    print(f"{'=' * 80}")

    return SuiteExecutionResult(
        suite_id=suite.suite_id,
        suite_name=suite.suite_name,
        suite_version=suite.suite_version,
        executed_at=start_time.isoformat(),
        total_tests=total_tests,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        pass_rate=pass_rate,
        meets_requirements=meets_requirements,
        test_results=test_results,
        duration_ms=total_duration_ms
    )


# =============================================================================
# CLI Interface
# =============================================================================

def parse_args():
    """Parse command-line arguments"""
    import argparse

    parser = argparse.ArgumentParser(
        description="L4 Conformance Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Run all suites
  %(prog)s --suite CS_EVENT_SCHEMA_V1   # Run specific suite
  %(prog)s --criticality critical       # Run only critical tests
  %(prog)s --json                       # Output JSON results
  %(prog)s --suite CS_* --criticality high --json  # Combined filters
        """
    )

    parser.add_argument(
        "--suite",
        type=str,
        help="Suite ID pattern to run (supports wildcards, e.g., 'CS_EVENT_*')"
    )

    parser.add_argument(
        "--criticality",
        type=str,
        choices=["critical", "high", "medium", "low"],
        help="Only run tests with this criticality level"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Write JSON results to file"
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Discover suites
    suite_files = discover_suites()

    if not suite_files:
        print("❌ No conformance suites found")
        return 1

    # Filter by suite pattern if specified
    if args.suite:
        import fnmatch
        pattern = args.suite if args.suite.endswith("*") else f"{args.suite}*"
        suite_files = [f for f in suite_files if fnmatch.fnmatch(f.stem, pattern)]

        if not suite_files:
            print(f"❌ No suites match pattern: {args.suite}")
            return 1

    # Load suites
    suites = []
    for suite_file in suite_files:
        suite = load_suite(suite_file)
        if suite:
            suites.append(suite)

    if not suites:
        print("❌ No valid suites loaded")
        return 1

    # Parse criticality filter
    criticality_filter = None
    if args.criticality:
        criticality_filter = Criticality(args.criticality)

    # Execute suites
    results = []
    for suite in suites:
        result = execute_suite(suite, criticality_filter)
        results.append(result)

    # Summary
    total_suites = len(results)
    passed_suites = sum(1 for r in results if r.meets_requirements)

    print(f"\n{'=' * 80}")
    print("OVERALL SUMMARY")
    print(f"{'=' * 80}")
    print(f"Suites Executed: {total_suites}")
    print(f"Suites Passed: {passed_suites}")
    print(f"Suites Failed: {total_suites - passed_suites}")
    print(f"{'=' * 80}\n")

    # Output JSON if requested
    if args.json or args.output:
        output_data = {
            "executed_at": datetime.now().isoformat(),
            "total_suites": total_suites,
            "passed_suites": passed_suites,
            "failed_suites": total_suites - passed_suites,
            "suites": [asdict(r) for r in results]
        }

        json_output = json.dumps(output_data, indent=2)

        if args.output:
            Path(args.output).write_text(json_output)
            print(f"✅ Results written to {args.output}")
        else:
            print(json_output)

    # Exit code: 0 if all suites pass, 1 otherwise
    return 0 if passed_suites == total_suites else 1


if __name__ == "__main__":
    sys.exit(main())
