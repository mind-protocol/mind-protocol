# -*- coding: utf-8 -*-
"""
Fixture: R-400 VIOLATION - Silent exception handler

This should be detected by scanner_fail_loud.py as a violation.
Exception handler doesn't rethrow AND doesn't emit failure.emit.
"""


def process_data(data):
    """Process data with silent exception handling - VIOLATION"""
    try:
        result = risky_operation(data)
        return result
    except ValueError:
        # VIOLATION: Silent failure - no rethrow, no failure.emit
        logger.error("Failed to process data")
        return None


def another_violation():
    """Another violation - catches and logs only"""
    try:
        dangerous_call()
    except (IOError, OSError):
        # VIOLATION: Multiple exception types, still silent
        print("Something went wrong")
        return False
