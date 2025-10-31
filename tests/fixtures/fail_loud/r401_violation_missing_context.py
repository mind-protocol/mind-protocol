# -*- coding: utf-8 -*-
"""
Fixture: R-401 VIOLATION - failure.emit missing required context

These should be detected by scanner_fail_loud.py as violations.
failure.emit calls must include: code_location, exception, severity
"""


async def missing_all_fields():
    """VIOLATION: failure.emit with no payload"""
    try:
        risky_operation()
    except Exception:
        # VIOLATION: No payload dict
        await emit_failure()


async def missing_some_fields():
    """VIOLATION: failure.emit missing severity"""
    try:
        risky_operation()
    except Exception as e:
        # VIOLATION: Missing 'severity' field
        await emit_failure({
            "code_location": f"{__file__}:24",
            "exception": str(e)
        })


async def missing_exception_field():
    """VIOLATION: failure.emit missing exception"""
    try:
        risky_operation()
    except Exception:
        # VIOLATION: Missing 'exception' field
        broadcaster.emit("failure.emit", {
            "code_location": f"{__file__}:37",
            "severity": "error"
        })
