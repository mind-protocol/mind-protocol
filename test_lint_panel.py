#!/usr/bin/env python3
"""
Quick test to emit a lint.findings.emit event to verify LintPanel receives it.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from orchestration.libs.safe_broadcaster import SafeBroadcaster


async def test_lint_panel():
    """Emit a test lint finding to verify LintPanel receives it."""

    print("🧪 Testing LintPanel event reception...")

    broadcaster = SafeBroadcaster(citizen_id="test_iris")

    # Test finding matching spec format (§ 6.2)
    test_event = {
        "change_id": "test:iris-panel-001",
        "findings": [
            {
                "policy": "hardcoded_anything",
                "rule": "R-102",
                "severity": "critical",
                "file": "app/consciousness/test_file.tsx",
                "span": {"start_line": 42, "end_line": 42},
                "message": "Hardcoded citizen array",
                "suggestion": "Use discover_graphs() service",
                "evidence": "['felix', 'ada', 'atlas', 'iris']"
            },
            {
                "policy": "quality_degradation",
                "rule": "R-201",
                "severity": "high",
                "file": "app/consciousness/test_file.tsx",
                "span": {"start_line": 88, "end_line": 92},
                "message": "TODO in logic path",
                "suggestion": "Implement validation logic"
            },
            {
                "policy": "fallback_antipattern",
                "rule": "R-300",
                "severity": "high",
                "file": "orchestration/test_service.py",
                "span": {"start_line": 156, "end_line": 159},
                "message": "Silent exception handler (BARE_EXCEPT_PASS)",
                "suggestion": "Emit failure.emit or re-raise exception"
            }
        ]
    }

    print(f"📤 Emitting lint.findings.emit with {len(test_event['findings'])} findings...")

    await broadcaster.broadcast_event(
        "lint.findings.emit",
        test_event
    )

    print("✅ Event emitted successfully!")
    print("\n📊 Check dashboard at http://localhost:3000/consciousness")
    print("   LintPanel (bottom-right) should show:")
    print("   - 🔴 3 findings badge")
    print("   - 2 files with violations")
    print("   - Severity colors: red (critical), orange (high)")
    print("\n⏱️  Event should appear within 1 second")

    # Also emit a verdict
    verdict_event = {
        "change_id": "test:iris-panel-001",
        "result": "soft_fail",
        "scores": {
            "hardcoded_anything": 1,
            "quality_degradation": 1,
            "fallback_antipattern": 1
        },
        "required": {
            "override": False,
            "fields": []
        }
    }

    print("\n📤 Emitting review.verdict (soft_fail)...")
    await broadcaster.broadcast_event("review.verdict", verdict_event)
    print("✅ Verdict emitted!")

    # Keep alive for a moment to ensure delivery
    await asyncio.sleep(0.5)

    print("\n✅ Test complete! Check the dashboard.")


if __name__ == "__main__":
    asyncio.run(test_lint_panel())
