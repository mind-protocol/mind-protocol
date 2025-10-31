# -*- coding: utf-8 -*-
"""
Fixture: R-400 CORRECT PATTERNS

These should NOT trigger violations - they follow fail-loud contract.
"""


async def correct_with_emit(data):
    """Correct: Exception handler emits failure.emit"""
    try:
        result = risky_operation(data)
        return result
    except ValueError as e:
        # CORRECT: Emits failure before returning default
        await emit_failure(
            code_location=f"{__file__}:14",
            exception=str(e),
            severity="error"
        )
        return None


def correct_with_rethrow(data):
    """Correct: Exception handler rethrows"""
    try:
        result = risky_operation(data)
        return result
    except ValueError:
        # CORRECT: Rethrows exception
        logger.error("Failed to process data")
        raise


def correct_defensive_guard():
    """Correct: Defensive guard with pragma"""
    try:
        optional_feature()
    except Exception:  # pragma: no cover
        # CORRECT: Pragma marks this as defensive guard
        pass


def correct_with_broadcaster():
    """Correct: Uses broadcaster.emit with failure event"""
    try:
        result = risky_operation()
        return result
    except Exception as e:
        # CORRECT: broadcaster.emit counts as failure emission
        broadcaster.emit("failure.emit", {
            "code_location": f"{__file__}:53",
            "exception": str(e),
            "severity": "warn"
        })
        return None
