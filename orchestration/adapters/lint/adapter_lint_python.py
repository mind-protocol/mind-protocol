#!/usr/bin/env python3
"""
adapter.lint.python - Membrane-Native Python Linter

Wraps mp-lint (R-100/200/300/400) as a membrane adapter.

Events consumed:
  - code.diff.emit (inject) - File diffs to lint

Events emitted:
  - lint.findings.emit (broadcast) - Lint violations found
  - failure.emit (broadcast) - Internal adapter errors (fail-loud)

Design:
  - Runs mp-lint scanners (hardcoded, quality, fallback, fail-loud) on changed files
  - Converts violations to L4 event format
  - Emits findings as structured events
  - Fail-loud: All exceptions emit failure.emit and rethrow

Rules enforced:
  - R-100 series: Hardcoded values (magic numbers, strings, citizen arrays)
  - R-200 series: Quality degradation (TODO/HACK, disabled validation, print instead of logger)
  - R-300 series: Fallback antipatterns (silent except, silent defaults, fake availability)
  - R-400 series: Fail-loud contract (missing failure.emit, missing context fields)

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
Updated: 2025-10-31 (added R-400/401 fail-loud scanning)
Spec: docs/L4-law/membrane_native_reviewer_and_lint_system.md § 5.2
Milestone: A (task #2 complete, TICKET-001 complete)
"""

import asyncio
import logging
import sys
import traceback
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# mp-lint scanners
from tools.mp_lint.scanner_hardcoded import scan_file_for_hardcoded, HardcodedViolation
from tools.mp_lint.scanner_quality import scan_file_for_quality, QualityViolation
from tools.mp_lint.scanner_fallback import scan_file_for_fallback, FallbackViolation
from tools.mp_lint.scanner_fail_loud import scan_file_for_fail_loud, FailLoudViolation
from tools.mp_lint.rules import (
    convert_hardcoded_violation,
    convert_quality_violation,
    convert_fallback_violation,
    convert_fail_loud_violation,
    Violation
)

# Event emission
from orchestration.libs.safe_broadcaster import SafeBroadcaster

logger = logging.getLogger(__name__)


# Severity mapping (lint violations → event severity)
SEVERITY_MAP = {
    "R-100": "high",      # MAGIC_NUMBER
    "R-101": "critical",  # HARDCODED_STRING
    "R-102": "critical",  # CITIZEN_ARRAY
    "R-200": "medium",    # TODO_OR_HACK
    "R-201": "high",      # QUALITY_DEGRADE
    "R-202": "medium",    # OBSERVABILITY_CUT
    "R-300": "critical",  # BARE_EXCEPT_PASS
    "R-301": "high",      # SILENT_DEFAULT_RETURN
    "R-302": "critical",  # FAKE_AVAILABILITY
    "R-303": "medium",    # INFINITE_LOOP_NO_SLEEP
    "R-400": "critical",  # FAIL_LOUD_REQUIRED
    "R-401": "critical",  # MISSING_FAILURE_CONTEXT
}

# Policy mapping (rule → policy category)
POLICY_MAP = {
    "R-100": "hardcoded_anything",
    "R-101": "hardcoded_anything",
    "R-102": "hardcoded_anything",
    "R-200": "quality_degradation",
    "R-201": "quality_degradation",
    "R-202": "quality_degradation",
    "R-300": "fallback_antipattern",
    "R-301": "fallback_antipattern",
    "R-302": "fallback_antipattern",
    "R-303": "fallback_antipattern",
    "R-400": "fail_loud_contract",
    "R-401": "fail_loud_contract",
}


class PythonLintAdapter:
    """
    Membrane adapter wrapping mp-lint for Python files.

    Accepts code.diff.emit events and emits lint.findings.emit.
    """

    def __init__(
        self,
        citizen_id: str = "adapter.lint.python",
        broadcaster: Optional[SafeBroadcaster] = None
    ):
        """
        Initialize lint adapter.

        Args:
            citizen_id: Adapter identity for event provenance
            broadcaster: SafeBroadcaster for event emission
        """
        self.citizen_id = citizen_id
        self.broadcaster = broadcaster or SafeBroadcaster(citizen_id=citizen_id)

        logger.info(f"[{self.citizen_id}] Initialized Python lint adapter")

    async def lint_files(
        self,
        file_paths: List[str],
        change_id: str
    ) -> Dict[str, Any]:
        """
        Lint multiple Python files and emit findings.

        Args:
            file_paths: List of file paths to lint
            change_id: Change ID from code.diff.emit event

        Returns:
            Dict with summary: {files_scanned, violations_found, findings_emitted}

        Raises:
            Exception: On internal errors (after emitting failure.emit)
        """
        all_violations: List[Violation] = []
        files_scanned = 0

        try:
            for file_path_str in file_paths:
                file_path = Path(file_path_str)

                # Skip non-Python files
                if file_path.suffix != '.py':
                    continue

                # Skip if file doesn't exist
                if not file_path.exists():
                    logger.warning(f"[{self.citizen_id}] File not found: {file_path}")
                    continue

                try:
                    # Run all scanners on file
                    violations = await self._scan_file(file_path)
                    all_violations.extend(violations)
                    files_scanned += 1

                except Exception as e:
                    # Emit failure for this specific file
                    await self._emit_failure(
                        change_id=change_id,
                        code_location=f"{file_path}:0",
                        exception=str(e),
                        severity="error",
                        suggestion=f"Failed to scan {file_path}: {e}"
                    )
                    # Continue with other files
                    logger.error(f"[{self.citizen_id}] Error scanning {file_path}: {e}")

            # Emit findings if any violations found
            if all_violations:
                await self._emit_findings(change_id, all_violations)

            return {
                "files_scanned": files_scanned,
                "violations_found": len(all_violations),
                "findings_emitted": len(all_violations)
            }

        except Exception as e:
            # Critical adapter error - emit failure and rethrow
            await self._emit_failure(
                change_id=change_id,
                code_location=f"{__file__}:{self.lint_files.__code__.co_firstlineno}",
                exception=str(e),
                severity="fatal",
                suggestion="Internal adapter error - check logs"
            )
            raise

    async def _scan_file(self, file_path: Path) -> List[Violation]:
        """
        Run all mp-lint scanners on a single file.

        Args:
            file_path: Path to Python file

        Returns:
            List of Violation objects
        """
        violations = []

        # R-100 series: Hardcoded values
        hardcoded_violations = scan_file_for_hardcoded(file_path)
        for hv in hardcoded_violations:
            violations.append(convert_hardcoded_violation(hv))

        # R-200 series: Quality degradation
        quality_violations = scan_file_for_quality(file_path)
        for qv in quality_violations:
            violations.append(convert_quality_violation(qv))

        # R-300 series: Fallback antipatterns
        fallback_violations = scan_file_for_fallback(file_path)
        for fv in fallback_violations:
            violations.append(convert_fallback_violation(fv))

        # R-400 series: Fail-loud contract
        fail_loud_violations = scan_file_for_fail_loud(file_path)
        for flv in fail_loud_violations:
            violations.append(convert_fail_loud_violation(flv))

        return violations

    async def _emit_findings(
        self,
        change_id: str,
        violations: List[Violation]
    ) -> None:
        """
        Emit lint.findings.emit event with violations.

        Args:
            change_id: Change ID from original code.diff.emit
            violations: List of violations found
        """
        # Convert violations to event format
        findings = []

        for v in violations:
            finding = {
                "policy": POLICY_MAP.get(v.rule_code, "unknown"),
                "rule": v.rule_code,
                "severity": SEVERITY_MAP.get(v.rule_code, "medium"),
                "file": v.file_path,
                "span": {
                    "start_line": v.line_number,
                    "end_line": v.line_number  # Single line for now
                },
                "message": v.message,
                "suggestion": self._get_suggestion(v),
                "evidence": v.context or v.event_type
            }
            findings.append(finding)

        # Emit event
        event_data = {
            "change_id": change_id,
            "findings": findings
        }

        success = await self.broadcaster.safe_emit(
            event_type="lint.findings.emit",
            data=event_data
        )

        if success:
            logger.info(
                f"[{self.citizen_id}] Emitted {len(findings)} findings "
                f"for change_id={change_id}"
            )
        else:
            logger.error(
                f"[{self.citizen_id}] Failed to emit findings for "
                f"change_id={change_id}"
            )

    async def _emit_failure(
        self,
        change_id: Optional[str],
        code_location: str,
        exception: str,
        severity: str,
        suggestion: str
    ) -> None:
        """
        Emit failure.emit event (fail-loud requirement).

        Args:
            change_id: Optional change ID
            code_location: File:line where error occurred
            exception: Exception message
            severity: warn|error|fatal
            suggestion: How to fix
        """
        trace_id = str(uuid.uuid4())

        event_data = {
            "change_id": change_id,
            "code_location": code_location,
            "exception": exception,
            "severity": severity,
            "suggestion": suggestion,
            "trace_id": trace_id,
            "stack_trace": traceback.format_exc()
        }

        await self.broadcaster.safe_emit(
            event_type="failure.emit",
            data=event_data
        )

        logger.error(
            f"[{self.citizen_id}] Emitted failure.emit: "
            f"trace_id={trace_id}, severity={severity}"
        )

    def _get_suggestion(self, violation: Violation) -> str:
        """
        Generate suggestion for fixing violation.

        Args:
            violation: Violation object

        Returns:
            Human-readable suggestion
        """
        rule_code = violation.rule_code

        suggestions = {
            "R-100": "Extract magic number to named constant",
            "R-101": "Move hardcoded value to settings/config",
            "R-102": "Use graph query or discovery service instead of hardcoded array",
            "R-200": "Remove TODO/HACK or add pragma with expiry",
            "R-201": "Re-enable validation or use pragma with reason",
            "R-202": "Replace print() with logger.info/warning/error",
            "R-300": "Add error handling or emit failure.emit event",
            "R-301": "Emit failure.emit before returning default",
            "R-302": "Implement actual availability check",
            "R-303": "Add sleep/backoff to prevent CPU spin"
        }

        return suggestions.get(rule_code, "See mp-lint documentation")


async def main():
    """
    Test adapter with sample files.
    """
    adapter = PythonLintAdapter()

    # Test with some orchestration files
    test_files = [
        "orchestration/core/settings.py",
        "orchestration/mechanisms/consciousness_engine_v2.py"
    ]

    change_id = f"test-{uuid.uuid4().hex[:8]}"

    logger.info(f"Testing lint adapter with change_id={change_id}")
    result = await adapter.lint_files(test_files, change_id)

    logger.info(f"Lint results: {result}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
