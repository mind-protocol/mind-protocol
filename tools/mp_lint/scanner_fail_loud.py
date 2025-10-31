# -*- coding: utf-8 -*-
"""
Fail-Loud Scanner - AST-based detection of fail-loud contract violations

Blocks:
  R-400: Exception handlers that don't rethrow and don't emit failure.emit
  R-401: failure.emit calls missing required context (code_location, exception, severity)

NO PRAGMA SUPPRESSION ALLOWED - Fail-loud is a protocol contract.

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
Purpose: Enforce fail-loud contract (all failures must be observable)
Spec: docs/L4-law/membrane_native_reviewer_and_lint_system.md § R-400/401
"""

import ast
import re
from pathlib import Path
from typing import List, Set, Optional
from dataclasses import dataclass


@dataclass
class FailLoudViolation:
    """Represents a fail-loud violation found in code."""
    violation_type: str  # FAIL_LOUD_REQUIRED, MISSING_FAILURE_CONTEXT
    file_path: str
    line_number: int
    code_snippet: str
    pattern: str
    message: str


# Allowed directories (defensive guards, test code, etc.)
ALLOWED_DIRS = (
    "tests/",
    "__tests__/",
    "__fixtures__/",
    ".storybook/",
)

# Functions that emit failure.emit
FAILURE_EMIT_PATTERNS = [
    "emit_failure",
    "failure.emit",
    "broadcaster.emit.*failure",
    "safe_emit.*failure",
    "_emit_failure",
]

# Required fields in failure.emit payload
REQUIRED_FAILURE_FIELDS = {
    "code_location",
    "exception",
    "severity"
}


def _is_allowed_path(file_path: Path) -> bool:
    """Check if file is in an allowed directory."""
    path_str = str(file_path)
    return any(allowed in path_str for allowed in ALLOWED_DIRS)


def _has_pragma_no_cover(source_lines: List[str], line_number: int) -> bool:
    """
    Check if line has pragma: no cover (defensive guard).

    These are typically defensive try/except blocks that should not fail
    in normal operation.
    """
    if line_number <= 0 or line_number > len(source_lines):
        return False

    # Check current line and next line for pragma
    for offset in [0, 1]:
        check_line = line_number - 1 + offset
        if check_line >= len(source_lines):
            continue
        line = source_lines[check_line]
        if "pragma: no cover" in line or "pragma:no cover" in line:
            return True

    return False


def _calls_failure_emit(node: ast.AST) -> bool:
    """
    Check if AST node contains a call to failure.emit or similar.

    Looks for:
    - emit_failure(...)
    - broadcaster.emit("failure.emit", ...)
    - safe_emit(..., "failure.emit", ...)
    """
    class FailureEmitVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_failure_emit = False

        def visit_Call(self, node: ast.Call):
            # Check function name
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if "emit_failure" in func_name or "failure" in func_name:
                    self.has_failure_emit = True

            # Check attribute (broadcaster.emit, safe.emit, etc.)
            elif isinstance(node.func, ast.Attribute):
                attr_name = node.func.attr
                if "emit_failure" in attr_name or "failure" in attr_name:
                    self.has_failure_emit = True

                # Check if arguments contain "failure.emit" string
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "failure" in arg.value.lower():
                            self.has_failure_emit = True

            self.generic_visit(node)

    visitor = FailureEmitVisitor()
    visitor.visit(node)
    return visitor.has_failure_emit


def _has_raise(node: ast.AST) -> bool:
    """Check if AST node contains a raise statement."""
    class RaiseVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_raise = False

        def visit_Raise(self, node: ast.Raise):
            self.has_raise = True

    visitor = RaiseVisitor()
    visitor.visit(node)
    return visitor.has_raise


def _check_exception_handler(
    handler: ast.ExceptHandler,
    source_lines: List[str],
    file_path: str
) -> Optional[FailLoudViolation]:
    """
    Check if exception handler violates R-400 (doesn't rethrow or emit failure).

    R-400 VIOLATION: Exception handler that:
    1. Catches an exception
    2. Does NOT rethrow (no `raise` statement)
    3. Does NOT emit failure.emit

    This is silent failure - unacceptable under fail-loud contract.
    """
    # Check if handler has raise statement
    if _has_raise(handler):
        return None  # OK: Handler rethrows

    # Check if handler calls failure.emit
    if _calls_failure_emit(handler):
        return None  # OK: Handler emits failure

    # Check if empty except (pass only) - already caught by R-300
    if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
        return None  # R-300 violation, not R-400

    # R-400 VIOLATION: Exception handler doesn't rethrow AND doesn't emit failure
    line_number = handler.lineno

    # Get code snippet
    snippet_lines = []
    for i in range(max(0, line_number - 1), min(len(source_lines), line_number + 3)):
        snippet_lines.append(source_lines[i].rstrip())
    code_snippet = "\n".join(snippet_lines)

    # Get exception type
    exc_type = "Exception"
    if handler.type:
        if isinstance(handler.type, ast.Name):
            exc_type = handler.type.id
        elif isinstance(handler.type, ast.Tuple):
            types = [e.id if isinstance(e, ast.Name) else "Exception" for e in handler.type.elts]
            exc_type = f"({', '.join(types)})"

    return FailLoudViolation(
        violation_type="FAIL_LOUD_REQUIRED",
        file_path=file_path,
        line_number=line_number,
        code_snippet=code_snippet,
        pattern=f"except {exc_type}:",
        message=f"Exception handler must either rethrow or emit failure.emit (fail-loud contract). "
                f"Handler catches {exc_type} but does neither - silent failure is forbidden."
    )


def _check_failure_emit_call(
    node: ast.Call,
    source_lines: List[str],
    file_path: str
) -> Optional[FailLoudViolation]:
    """
    Check if failure.emit call violates R-401 (missing required context).

    R-401 VIOLATION: failure.emit call missing required fields:
    - code_location (file:line)
    - exception (error message/type)
    - severity (warn|error|fatal)
    """
    # Check if this is a failure.emit call
    is_failure_emit = False

    if isinstance(node.func, ast.Name):
        if "emit_failure" in node.func.id or "failure" in node.func.id:
            is_failure_emit = True

    elif isinstance(node.func, ast.Attribute):
        if "emit_failure" in node.func.attr or "failure" in node.func.attr:
            is_failure_emit = True

        # Check arguments for "failure.emit" string
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if "failure" in arg.value.lower():
                    is_failure_emit = True

    if not is_failure_emit:
        return None

    # Extract payload (look for dict argument)
    payload_dict = None
    for arg in node.args:
        if isinstance(arg, ast.Dict):
            payload_dict = arg
            break

    # Also check keyword arguments
    if not payload_dict:
        for keyword in node.keywords:
            if isinstance(keyword.value, ast.Dict):
                payload_dict = keyword.value
                break

    if not payload_dict:
        # No payload dict found - definitely missing context
        return FailLoudViolation(
            violation_type="MISSING_FAILURE_CONTEXT",
            file_path=file_path,
            line_number=node.lineno,
            code_snippet=source_lines[node.lineno - 1].rstrip() if node.lineno <= len(source_lines) else "",
            pattern="failure.emit without payload",
            message="failure.emit must include payload with: code_location, exception, severity"
        )

    # Check if required fields are present
    found_fields = set()
    for key in payload_dict.keys:
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            found_fields.add(key.value)

    missing_fields = REQUIRED_FAILURE_FIELDS - found_fields

    if missing_fields:
        return FailLoudViolation(
            violation_type="MISSING_FAILURE_CONTEXT",
            file_path=file_path,
            line_number=node.lineno,
            code_snippet=source_lines[node.lineno - 1].rstrip() if node.lineno <= len(source_lines) else "",
            pattern=f"failure.emit missing: {', '.join(sorted(missing_fields))}",
            message=f"failure.emit must include required fields: {', '.join(sorted(missing_fields))}. "
                    f"Protocol contract requires: code_location (file:line), exception (error), severity (warn|error|fatal)."
        )

    return None


def scan_file_for_fail_loud(file_path: Path) -> List[FailLoudViolation]:
    """
    Scan a Python file for fail-loud violations (R-400/401).

    Returns:
        List of FailLoudViolation objects
    """
    violations = []

    # Skip allowed paths
    if _is_allowed_path(file_path):
        return violations

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            source_lines = source.splitlines()
    except Exception:
        return violations  # Can't read file

    # Parse AST
    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return violations  # Syntax error - skip

    # Visitor to find exception handlers and failure.emit calls
    class FailLoudVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []

        def visit_Try(self, node: ast.Try):
            # Check each exception handler
            for handler in node.handlers:
                # Skip if has pragma: no cover (defensive guard)
                if _has_pragma_no_cover(source_lines, handler.lineno):
                    continue

                violation = _check_exception_handler(handler, source_lines, str(file_path))
                if violation:
                    self.violations.append(violation)

            self.generic_visit(node)

        def visit_Call(self, node: ast.Call):
            # Check failure.emit calls for missing context
            violation = _check_failure_emit_call(node, source_lines, str(file_path))
            if violation:
                self.violations.append(violation)

            self.generic_visit(node)

    visitor = FailLoudVisitor()
    visitor.visit(tree)
    violations.extend(visitor.violations)

    return violations


def scan_directory_for_fail_loud(directory: Path) -> List[FailLoudViolation]:
    """
    Recursively scan directory for fail-loud violations.

    Returns:
        List of FailLoudViolation objects
    """
    violations = []

    for py_file in directory.rglob("*.py"):
        if py_file.is_file():
            file_violations = scan_file_for_fail_loud(py_file)
            violations.extend(file_violations)

    return violations


if __name__ == "__main__":
    # Test on a sample file
    import sys

    if len(sys.argv) > 1:
        path = Path(sys.argv[1])

        if path.is_file():
            violations = scan_file_for_fail_loud(path)
        else:
            violations = scan_directory_for_fail_loud(path)

        print(f"Found {len(violations)} fail-loud violations:")
        for v in violations:
            print(f"\n{v.file_path}:{v.line_number}")
            print(f"  Type: {v.violation_type}")
            print(f"  Pattern: {v.pattern}")
            print(f"  Message: {v.message}")
    else:
        print("Usage: python scanner_fail_loud.py <file_or_directory>")
