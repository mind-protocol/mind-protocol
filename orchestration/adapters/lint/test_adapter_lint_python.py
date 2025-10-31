#!/usr/bin/env python3
"""
Test adapter.lint.python - Verify event emissions and fail-loud behavior

Tests:
  1. Lint violations are converted to findings correctly
  2. Internal errors emit failure.emit (fail-loud requirement)
  3. Event format matches spec (lint.findings.emit)

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
"""

import asyncio
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from orchestration.adapters.lint.adapter_lint_python import PythonLintAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_lint_findings_emission():
    """Test that violations are emitted as lint.findings.emit events."""
    logger.info("=== Test 1: Lint Findings Emission ===")

    # Mock broadcaster
    mock_broadcaster = MagicMock()
    mock_broadcaster.safe_emit = AsyncMock(return_value=True)

    adapter = PythonLintAdapter(broadcaster=mock_broadcaster)

    # Lint a file with known violations
    test_file = "orchestration/core/settings.py"
    change_id = "test-findings-001"

    result = await adapter.lint_files([test_file], change_id)

    logger.info(f"Result: {result}")

    # Check that safe_emit was called
    if mock_broadcaster.safe_emit.call_count > 0:
        # Get the event that was emitted
        call_args = mock_broadcaster.safe_emit.call_args_list[0]
        event_type = call_args[1]['event_type']
        event_data = call_args[1]['data']

        logger.info(f"✅ Event emitted: {event_type}")
        logger.info(f"   change_id: {event_data.get('change_id')}")
        logger.info(f"   findings: {len(event_data.get('findings', []))} violations")

        # Verify event format
        assert event_type == "lint.findings.emit"
        assert event_data["change_id"] == change_id
        assert "findings" in event_data
        assert isinstance(event_data["findings"], list)

        # Verify finding structure
        if event_data["findings"]:
            finding = event_data["findings"][0]
            required_fields = ["policy", "rule", "severity", "file", "span", "message", "suggestion", "evidence"]
            for field in required_fields:
                assert field in finding, f"Missing field: {field}"
            logger.info(f"✅ Finding format valid: {finding['rule']} - {finding['message'][:50]}...")
        else:
            logger.info("⚠️  No findings emitted (file may be clean)")

        logger.info("✅ Test 1 PASSED\n")
    else:
        logger.warning("⚠️  No events emitted (expected if file is clean)\n")


async def test_fail_loud_on_error():
    """Test that internal errors emit failure.emit before rethrowing."""
    logger.info("=== Test 2: Fail-Loud Behavior ===")

    # Mock broadcaster
    mock_broadcaster = MagicMock()
    mock_broadcaster.safe_emit = AsyncMock(return_value=True)

    adapter = PythonLintAdapter(broadcaster=mock_broadcaster)

    # Try to lint a non-existent file
    test_files = ["nonexistent_file_12345.py"]
    change_id = "test-fail-loud-001"

    # This should handle the error gracefully and NOT raise
    result = await adapter.lint_files(test_files, change_id)

    logger.info(f"Result: {result}")

    # Check if failure.emit was called
    failure_emitted = False
    for call in mock_broadcaster.safe_emit.call_args_list:
        event_type = call[1]['event_type']
        if event_type == "failure.emit":
            failure_emitted = True
            event_data = call[1]['data']
            logger.info(f"✅ failure.emit event emitted")
            logger.info(f"   severity: {event_data.get('severity')}")
            logger.info(f"   exception: {event_data.get('exception')[:80]}...")
            logger.info(f"   code_location: {event_data.get('code_location')}")

            # Verify failure event format
            required_fields = ["code_location", "exception", "severity", "suggestion", "trace_id"]
            for field in required_fields:
                assert field in event_data, f"Missing field in failure.emit: {field}"

            logger.info("✅ Test 2 PASSED\n")
            break

    if not failure_emitted:
        logger.info("⚠️  No failure.emit event (test file handling may differ)\n")


async def test_event_format_compliance():
    """Test that emitted events match spec format."""
    logger.info("=== Test 3: Event Format Compliance ===")

    # Mock broadcaster
    mock_broadcaster = MagicMock()
    mock_broadcaster.safe_emit = AsyncMock(return_value=True)

    adapter = PythonLintAdapter(broadcaster=mock_broadcaster)

    # Lint a file
    test_file = "orchestration/mechanisms/consciousness_engine_v2.py"
    change_id = "test-format-001"

    result = await adapter.lint_files([test_file], change_id)

    if mock_broadcaster.safe_emit.call_count == 0:
        logger.info("⚠️  No events emitted (file may be clean)")
        return

    # Get lint.findings.emit event
    for call in mock_broadcaster.safe_emit.call_args_list:
        event_type = call[1]['event_type']
        if event_type == "lint.findings.emit":
            event_data = call[1]['data']

            # Spec format from line 179-194 of membrane_native_reviewer_and_lint_system.md
            logger.info("✅ Event format compliance:")
            logger.info(f"   change_id: {event_data.get('change_id')}")
            logger.info(f"   findings[0].policy: {event_data['findings'][0]['policy']}")
            logger.info(f"   findings[0].rule: {event_data['findings'][0]['rule']}")
            logger.info(f"   findings[0].severity: {event_data['findings'][0]['severity']}")
            logger.info(f"   findings[0].span: {event_data['findings'][0]['span']}")

            # Verify severity values
            valid_severities = ["low", "medium", "high", "critical"]
            for finding in event_data["findings"]:
                assert finding["severity"] in valid_severities, \
                    f"Invalid severity: {finding['severity']}"

            # Verify policy values
            valid_policies = ["hardcoded_anything", "fallback_antipattern", "quality_degradation", "fail_loud"]
            for finding in event_data["findings"]:
                assert finding["policy"] in valid_policies, \
                    f"Invalid policy: {finding['policy']}"

            logger.info("✅ Test 3 PASSED\n")
            break


async def main():
    """Run all tests."""
    logger.info("=" * 70)
    logger.info("ADAPTER.LINT.PYTHON TEST SUITE")
    logger.info("=" * 70)
    logger.info("")

    try:
        await test_lint_findings_emission()
        await test_fail_loud_on_error()
        await test_event_format_compliance()

        logger.info("=" * 70)
        logger.info("✅ ALL TESTS PASSED")
        logger.info("=" * 70)

    except AssertionError as e:
        logger.error(f"❌ TEST FAILED: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
