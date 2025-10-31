"""
Report Generator - Format Linter Violations

Formats mp-lint violations for display:
- Human-readable terminal output with colors
- JSON output for CI integration
- Summary statistics

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-31
"""

import json
from collections import defaultdict
from typing import Any, Dict, List

from .rules import Violation


class ReportGenerator:
    """
    Formats linter violations for display.

    Supports multiple output formats:
    - "terminal": Human-readable colored output
    - "json": Structured JSON for CI integration
    - "summary": Brief statistics only
    """

    def __init__(self, violations: List[Violation]):
        """
        Initialize report generator with violations.

        Args:
            violations: List of violations to report
        """
        self.violations = violations
        self.violations_by_file: Dict[str, List[Violation]] = defaultdict(list)
        self.violations_by_rule: Dict[str, int] = defaultdict(int)

        # Group violations
        for v in violations:
            self.violations_by_file[v.file_path].append(v)
            self.violations_by_rule[v.rule_code] += 1

    def generate_terminal_report(self) -> str:
        """
        Generate human-readable terminal report.

        Returns:
            Formatted report string
        """
        lines = []

        # Header
        lines.append("")
        lines.append("=" * 80)
        lines.append("mp-lint: L4 Membrane Linter Results")
        lines.append("=" * 80)
        lines.append("")

        # Violations by file
        if self.violations:
            for file_path, file_violations in sorted(self.violations_by_file.items()):
                lines.append(f"File: {file_path}")
                lines.append("")

                for v in sorted(file_violations, key=lambda x: x.line_number):
                    # Format: Line X: [RULE-CODE] Message
                    severity_icon = "[ERROR]" if v.severity == "error" else "[WARN]"
                    lines.append(f"  {severity_icon} Line {v.line_number}: [{v.rule_code}] {v.message}")

                    # Show code snippet if available
                    if v.context:
                        lines.append(f"    > {v.context.strip()}")

                    lines.append("")

        # Summary
        lines.append("=" * 80)
        lines.append("Summary")
        lines.append("=" * 80)

        if self.violations:
            lines.append(f"Total violations: {len(self.violations)}")
            lines.append("")
            lines.append("Violations by rule:")
            for rule_code, count in sorted(self.violations_by_rule.items()):
                lines.append(f"  {rule_code}: {count}")
            lines.append("")
            lines.append("[FAIL] Linting FAILED")
        else:
            lines.append("[PASS] No violations found - all events comply with L4 protocol")

        lines.append("")

        return "\n".join(lines)

    def generate_json_report(self) -> str:
        """
        Generate JSON report for CI integration.

        Returns:
            JSON string
        """
        report = {
            "total_violations": len(self.violations),
            "violations_by_rule": dict(self.violations_by_rule),
            "violations": [
                {
                    "rule_code": v.rule_code,
                    "severity": v.severity,
                    "message": v.message,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "event_type": v.event_type,
                    "context": v.context
                }
                for v in self.violations
            ],
            "passed": len(self.violations) == 0
        }

        return json.dumps(report, indent=2)

    def generate_summary(self) -> str:
        """
        Generate brief summary.

        Returns:
            Summary string
        """
        if self.violations:
            return (
                f"[FAIL] mp-lint: {len(self.violations)} violations found "
                f"({', '.join(f'{code}: {count}' for code, count in sorted(self.violations_by_rule.items()))})"
            )
        else:
            return "[PASS] mp-lint: No violations found"

    def should_fail_ci(self) -> bool:
        """
        Check if violations should fail CI.

        Returns:
            True if any violations have severity="error"
        """
        return any(v.severity == "error" for v in self.violations)
