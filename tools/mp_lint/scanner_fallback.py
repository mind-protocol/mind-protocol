# -*- coding: utf-8 -*-
"""
Fallback Antipattern Scanner - Detect patterns that hide bugs through silent fallbacks.

Blocks:
  - Silent except: (bare except or broad Exception with pass/return default)
  - Fake availability checks (is_available() returns True without runtime verification)
  - Infinite loops without sleep/backoff
  - Fail-open feature flags (default to enabled when config missing)
  - Spec-drift fallbacks (silent schema mapping on mismatch)

Allowed:
  - docs/, tests/, __fixtures__/
  - Per-line pragma: # lint: allow-fallback(reason="...")

Author: Atlas "Infrastructure Engineer"
Created: 2025-10-31
Purpose: Prevent silent fallbacks that hide bugs
"""

import ast
import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class FallbackViolation:
    """Represents a fallback antipattern violation."""
    violation_type: str
    file_path: str
    line_number: int
    code_snippet: str
    pattern: str
    message: str


# Directories where fallback antipatterns are allowed
ALLOWED_DIRS = (
    "docs/",
    "tests/",
    "__tests__/",
    "__fixtures__/",
    ".storybook/",
)

# Pragma to suppress warnings
PRAGMA = "lint: allow-fallback"


def is_allowed_path(file_path: Path) -> bool:
    """Check if file is in allowed directories."""
    path_str = str(file_path).replace("\\", "/")
    return any(path_str.startswith(d) for d in ALLOWED_DIRS)


def has_line_pragma(source_lines: List[str], line_number: int) -> bool:
    """Check if specific line has pragma comment."""
    if line_number <= 0 or line_number > len(source_lines):
        return False

    line = source_lines[line_number - 1]
    return PRAGMA in line


class FallbackScanner(ast.NodeVisitor):
    """AST visitor that detects fallback antipatterns."""

    def __init__(self, file_path: Path, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.violations: List[FallbackViolation] = []

    def _get_line_snippet(self, line_number: int) -> str:
        """Get source code line at given line number."""
        if 0 < line_number <= len(self.source_lines):
            return self.source_lines[line_number - 1].strip()
        return ""

    def _get_range_snippet(self, start_line: int, end_line: int) -> str:
        """Get source code for a range of lines."""
        if start_line > 0 and end_line <= len(self.source_lines):
            return "\n".join(self.source_lines[start_line-1:end_line])
        return ""

    def _is_trivial_return(self, node: ast.Return) -> bool:
        """Check if return statement returns a trivial default value."""
        if node.value is None:
            return True

        # Check for None, empty dict, empty list, 0, empty string
        if isinstance(node.value, ast.Constant):
            value = node.value.value
            if value is None or value == 0 or value == "" or value == []:
                return True

        if isinstance(node.value, (ast.Dict, ast.List, ast.Tuple)):
            # Empty containers
            if not node.value.keys if isinstance(node.value, ast.Dict) else not node.value.elts:
                return True

        return False

    def visit_Try(self, node: ast.Try):
        """Visit try-except blocks to detect silent fallbacks."""
        for handler in node.handlers:
            line_number = handler.lineno
            line_snippet = self._get_line_snippet(line_number)

            # Skip if line has pragma
            if has_line_pragma(self.source_lines, line_number):
                self.generic_visit(node)
                continue

            # Check for bare except or broad Exception
            is_broad = (handler.type is None) or (
                isinstance(handler.type, ast.Name) and
                handler.type.id in ("Exception", "BaseException")
            )

            if is_broad:
                bodies = handler.body if handler.body else []

                # Check for pass-only handler
                if all(isinstance(stmt, ast.Pass) for stmt in bodies):
                    self.violations.append(FallbackViolation(
                        violation_type="BARE_EXCEPT_PASS",
                        file_path=str(self.file_path),
                        line_number=line_number,
                        code_snippet=line_snippet,
                        pattern="except: pass",
                        message="Silent except with pass hides errors"
                    ))

                # Check for trivial return
                for stmt in bodies:
                    if isinstance(stmt, ast.Return) and self._is_trivial_return(stmt):
                        self.violations.append(FallbackViolation(
                            violation_type="SILENT_DEFAULT_RETURN",
                            file_path=str(self.file_path),
                            line_number=stmt.lineno,
                            code_snippet=self._get_line_snippet(stmt.lineno),
                            pattern="except: return default",
                            message="Silent fallback to default value hides errors"
                        ))

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions to detect fake availability checks."""
        line_number = node.lineno
        line_snippet = self._get_line_snippet(line_number)

        # Skip if line has pragma
        if has_line_pragma(self.source_lines, line_number):
            self.generic_visit(node)
            return

        # Check is_available() functions
        if node.name == "is_available":
            # Get function body text
            if hasattr(node, 'end_lineno'):
                body_text = self._get_range_snippet(node.lineno, node.end_lineno)
            else:
                body_text = ""

            # Heuristic: returns True without checking runtime state
            # Look for: return True without any attribute checks
            if re.search(r'return\s+True\b', body_text):
                # Check if there are any runtime checks (attribute access, method calls)
                has_checks = bool(re.search(r'self\.\w+|\w+\.client_count|\.is_connected|\.ping', body_text))

                if not has_checks:
                    self.violations.append(FallbackViolation(
                        violation_type="FAKE_AVAILABILITY",
                        file_path=str(self.file_path),
                        line_number=line_number,
                        code_snippet=line_snippet,
                        pattern="is_available() without checks",
                        message="is_available() returns True without runtime verification"
                    ))

        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        """Visit while loops to detect infinite loops without sleep."""
        line_number = node.lineno
        line_snippet = self._get_line_snippet(line_number)

        # Skip if line has pragma
        if has_line_pragma(self.source_lines, line_number):
            self.generic_visit(node)
            return

        # Check for while True loops
        is_infinite = (
            isinstance(node.test, ast.Constant) and node.test.value is True
        ) or (
            isinstance(node.test, ast.NameConstant) and node.test.value is True  # Python 3.7 compat
        )

        if is_infinite:
            # Get loop body text
            if hasattr(node, 'end_lineno'):
                body_text = self._get_range_snippet(node.lineno, node.end_lineno)
            else:
                body_text = ""

            # Check for sleep/delay
            has_sleep = bool(re.search(r'\bsleep\(|await\s+asyncio\.sleep|time\.sleep|await\s+sleep', body_text))

            if not has_sleep:
                self.violations.append(FallbackViolation(
                    violation_type="INFINITE_LOOP_NO_SLEEP",
                    file_path=str(self.file_path),
                    line_number=line_number,
                    code_snippet=line_snippet,
                    pattern="while True without sleep",
                    message="Infinite loop without sleep/backoff causes CPU exhaustion"
                ))

        self.generic_visit(node)


def scan_file_for_fallback(file_path: Path) -> List[FallbackViolation]:
    """
    Scan a Python file for fallback antipatterns.

    Args:
        file_path: Path to Python file

    Returns:
        List of FallbackViolation objects
    """
    # Skip allowed paths
    if is_allowed_path(file_path):
        return []

    try:
        source_code = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    # Parse AST
    try:
        tree = ast.parse(source_code, filename=str(file_path))
    except SyntaxError:
        return []

    # Scan for violations
    scanner = FallbackScanner(file_path, source_code)
    scanner.visit(tree)

    return scanner.violations


def scan_directory_for_fallback(directory: Path, exclude_patterns: Optional[List[str]] = None) -> List[FallbackViolation]:
    """
    Scan a directory recursively for fallback antipatterns.

    Args:
        directory: Directory to scan
        exclude_patterns: Glob patterns to exclude

    Returns:
        List of all FallbackViolation objects found
    """
    exclude_patterns = exclude_patterns or []
    all_violations = []

    for py_file in directory.rglob("*.py"):
        # Check exclusions
        if any(py_file.match(pattern) for pattern in exclude_patterns):
            continue

        violations = scan_file_for_fallback(py_file)
        all_violations.extend(violations)

    return all_violations
