# -*- coding: utf-8 -*-
"""
Quality Degradation Scanner - Detect patterns that reduce system quality.

Blocks:
  - TODO/HACK/FIXME/TEMP comments that affect logic
  - Disabled validation/enforcement flags
  - Observability cuts (logging disabled, print() instead of logger)
  - Absurd timeouts/zero retries/zero backoff
  - Spec/version downgrades

Allowed:
  - docs/, tests/, __fixtures__/
  - Per-line pragma: # lint: allow-degrade(reason="...")

Author: Atlas "Infrastructure Engineer"
Created: 2025-10-31
Purpose: Prevent quality degradation in production code
"""

import ast
import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class QualityViolation:
    """Represents a quality degradation violation."""
    violation_type: str
    file_path: str
    line_number: int
    code_snippet: str
    pattern: str
    message: str


# Directories where quality degradation is allowed
ALLOWED_DIRS = (
    "docs/",
    "tests/",
    "__tests__/",
    "__fixtures__/",
    ".storybook/",
)

# Pragma to suppress warnings
PRAGMA = "lint: allow-degrade"

# TODO/HACK/FIXME/TEMP pattern
RE_TODO = re.compile(r'\b(TODO|TEMP|HACK|FIXME)\b', re.I)

# Quality degradation patterns
QUALITY_PATTERNS = [
    # Disabled validation
    (re.compile(r'\bvalidate\s*=\s*False\b'), "Validation disabled"),
    (re.compile(r'\benforce\s*=\s*False\b'), "Enforcement disabled"),
    (re.compile(r'\bskip_validation\s*=\s*True\b'), "Validation skipped"),
    (re.compile(r'\blint\s*=\s*False\b'), "Linting disabled"),

    # Observability cuts
    (re.compile(r'\blogging\.disable\('), "Logging globally disabled"),
    (re.compile(r'\blogger\.disabled\s*=\s*True\b'), "Logger disabled"),

    # Absurd timeouts (>100000ms = 100+ seconds)
    (re.compile(r'\btimeout\s*=\s*[1-9]\d{5,}\b'), "Absurdly large timeout"),
    (re.compile(r'\btimeout_ms\s*=\s*[1-9]\d{5,}\b'), "Absurdly large timeout"),

    # Zero retries/backoff (reduces resilience)
    (re.compile(r'\bretries\s*=\s*0\b'), "Zero retries disables resilience"),
    (re.compile(r'\bmax_retries\s*=\s*0\b'), "Zero retries disables resilience"),
    (re.compile(r'\bbackoff\s*=\s*0\b'), "Zero backoff disables rate limiting"),

    # Spec downgrades
    (re.compile(r'spec\.rev\s*=\s*["\']current["\']'), "Spec rev downgraded to string 'current'"),
    (re.compile(r'spec\s*=\s*None'), "Spec set to None"),
    (re.compile(r'schema_version\s*=\s*None'), "Schema version set to None"),
]


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


class QualityScanner(ast.NodeVisitor):
    """AST visitor that detects quality degradation patterns."""

    def __init__(self, file_path: Path, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.violations: List[QualityViolation] = []

    def _get_line_snippet(self, line_number: int) -> str:
        """Get source code line at given line number."""
        if 0 < line_number <= len(self.source_lines):
            return self.source_lines[line_number - 1].strip()
        return ""

    def visit_Call(self, node: ast.Call):
        """Visit function calls to detect print() usage."""
        line_number = node.lineno
        line_snippet = self._get_line_snippet(line_number)

        # Skip if line has pragma
        if has_line_pragma(self.source_lines, line_number):
            self.generic_visit(node)
            return

        # Check for print() usage (possible observability cut)
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            # Check if logger exists in file (heuristic)
            if "logger" in self.source_code or "logging.getLogger" in self.source_code:
                self.violations.append(QualityViolation(
                    violation_type="OBSERVABILITY_CUT",
                    file_path=str(self.file_path),
                    line_number=line_number,
                    code_snippet=line_snippet,
                    pattern="print() instead of logger",
                    message="Using print() instead of logger reduces observability"
                ))

        self.generic_visit(node)

    def scan_text_patterns(self):
        """Scan source text for regex-based quality patterns."""
        for line_number, line in enumerate(self.source_lines, start=1):
            # Skip if line has pragma
            if has_line_pragma(self.source_lines, line_number):
                continue

            # Check TODO/HACK/FIXME
            if RE_TODO.search(line):
                # Skip pure comments in docstrings (allowed for planning)
                # But flag if it's in actual code logic
                stripped = line.strip()
                if not stripped.startswith('#') or '=' in stripped or 'return' in stripped:
                    self.violations.append(QualityViolation(
                        violation_type="TODO_OR_HACK",
                        file_path=str(self.file_path),
                        line_number=line_number,
                        code_snippet=line.strip(),
                        pattern=RE_TODO.search(line).group(0),
                        message="TODO/HACK/FIXME in code logic reduces quality"
                    ))

            # Check other quality patterns
            for pattern, description in QUALITY_PATTERNS:
                match = pattern.search(line)
                if match:
                    self.violations.append(QualityViolation(
                        violation_type="QUALITY_DEGRADE",
                        file_path=str(self.file_path),
                        line_number=line_number,
                        code_snippet=line.strip(),
                        pattern=match.group(0),
                        message=description
                    ))


def scan_file_for_quality(file_path: Path) -> List[QualityViolation]:
    """
    Scan a Python file for quality degradation patterns.

    Args:
        file_path: Path to Python file

    Returns:
        List of QualityViolation objects
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
    scanner = QualityScanner(file_path, source_code)
    scanner.visit(tree)
    scanner.scan_text_patterns()

    return scanner.violations


def scan_directory_for_quality(directory: Path, exclude_patterns: Optional[List[str]] = None) -> List[QualityViolation]:
    """
    Scan a directory recursively for quality degradation patterns.

    Args:
        directory: Directory to scan
        exclude_patterns: Glob patterns to exclude

    Returns:
        List of all QualityViolation objects found
    """
    exclude_patterns = exclude_patterns or []
    all_violations = []

    for py_file in directory.rglob("*.py"):
        # Check exclusions
        if any(py_file.match(pattern) for pattern in exclude_patterns):
            continue

        violations = scan_file_for_quality(py_file)
        all_violations.extend(violations)

    return all_violations
