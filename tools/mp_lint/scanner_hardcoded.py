# -*- coding: utf-8 -*-
"""
Hardcoded Value Scanner - AST-based detection of hardcoded strings, magic numbers, and domain arrays.

Blocks:
  - Strings that look like IDs/URLs/paths/secrets/DSNs
  - Magic numbers (outside tiny allowlist) in non-constant contexts
  - Arrays of known domain entities (citizens, etc.)

Allowed:
  - docs/, tests/, __fixtures__/, constants modules
  - Per-line pragma: # lint: allow-hardcoded

Author: Atlas "Infrastructure Engineer"
Created: 2025-10-31
Purpose: Prevent hardcoded configuration in application code
"""

import ast
import re
from pathlib import Path
from typing import List, Set, Optional
from dataclasses import dataclass


@dataclass
class HardcodedViolation:
    """Represents a hardcoded value violation found in code."""
    violation_type: str  # MAGIC_NUMBER, HARDCODED_STRING, CITIZEN_ARRAY, etc.
    file_path: str
    line_number: int
    code_snippet: str
    value: str
    message: str


# Directories/files where hardcoded values are allowed
ALLOWED_DIRS = (
    "docs/",
    "tests/",
    "__tests__/",
    "__fixtures__/",
    ".storybook/",
    "tools/",
    "scripts/",
)

ALLOWED_FILES = (
    "orchestration/config/constants.py",
    "orchestration/config/graph_names.py",
    "orchestration/config/settings.py",
)

# Pragma to suppress warnings on specific lines
PRAGMA = "lint: allow-hardcoded"

# Known citizen names (expand as needed)
CITIZENS = ["felix", "ada", "atlas", "iris", "luca", "victor"]

# Numbers that are trivially allowed (common loop/array patterns)
ALLOWED_NUMBERS = {-1, 0, 1, 2}

# Heuristic patterns for detecting hardcoded strings
HARDCODED_PATTERNS = [
    # URLs and DSNs
    (re.compile(r"\b(?:http|https|ws|wss|amqp|mqtt|redis|postgres|mysql|s3|file)://", re.I), "Hardcoded URL/DSN"),

    # Domain names
    (re.compile(r"\b(?:[a-z0-9-]+\.)+[a-z]{2,}\b", re.I), "Hardcoded domain name"),

    # IPv4 addresses
    (re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"), "Hardcoded IP address"),

    # Port numbers in host:port format
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b"), "Hardcoded host:port"),

    # Long hex strings (likely IDs, hashes, tokens)
    (re.compile(r"\b[A-Fa-f0-9]{32,}\b"), "Hardcoded hex ID/token"),

    # JWT-like tokens
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), "Hardcoded JWT token"),

    # AWS-style keys
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "Hardcoded AWS key"),

    # Base64-ish long strings
    (re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b"), "Hardcoded base64 token"),

    # Secret-like key=value patterns
    (re.compile(r"(?i)\b(api|secret|token|key|password|auth)\b.*?[=:]\s*['\"][^'\"]{8,}"), "Hardcoded secret/key"),

    # File paths (Unix and Windows)
    (re.compile(r"(?:^|['\"\\s])(?:/(?:home|Users|var|etc|tmp|opt|srv|mnt|app|data|usr)/[^\s'\"]+|[A-Z]:\\[^\s'\"]+)", re.I), "Hardcoded file path"),

    # Graph/resource names (consciousness-infrastructure pattern)
    (re.compile(r"\b(?:consciousness-infrastructure|mind-protocol)_[a-z0-9_-]+\b"), "Hardcoded graph/resource name"),

    # FalkorDB graph names
    (re.compile(r"\bconsciousness-infrastructure_mind-protocol_[a-z]+\b"), "Hardcoded FalkorDB graph name"),
]

# Pattern for citizen arrays
CITIZEN_ARRAY_PATTERN = re.compile(
    r"\[\s*(?:['\"](?:" + "|".join(map(re.escape, CITIZENS)) + r")['\"]\s*,?\s*)+\]",
    re.I
)


def is_allowed_path(file_path: Path, file_content: str) -> bool:
    """Check if file is in allowed directories."""
    path_str = str(file_path).replace("\\", "/")

    # Check allowed directories
    if any(path_str.startswith(d) for d in ALLOWED_DIRS):
        return True

    # Check allowed specific files
    if path_str in ALLOWED_FILES:
        return True

    # Note: Pragma is checked per-line, not file-wide
    return False


def has_line_pragma(source_lines: List[str], line_number: int) -> bool:
    """Check if specific line has pragma comment."""
    if line_number <= 0 or line_number > len(source_lines):
        return False

    line = source_lines[line_number - 1]
    return PRAGMA in line


class HardcodedScanner(ast.NodeVisitor):
    """AST visitor that detects hardcoded values in Python code."""

    def __init__(self, file_path: Path, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.violations: List[HardcodedViolation] = []

    def _get_line_snippet(self, line_number: int) -> str:
        """Get source code line at given line number."""
        if 0 < line_number <= len(self.source_lines):
            return self.source_lines[line_number - 1].strip()
        return ""

    def _is_constant_assignment(self, node: ast.Constant) -> bool:
        """Check if constant is being assigned to UPPER_CASE variable (likely a constant)."""
        # Walk up to find parent assignment
        parent = getattr(node, "_parent", None)
        if isinstance(parent, ast.Assign):
            # Check if any target is an uppercase name
            for target in parent.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    return True
        return False

    def visit_Constant(self, node: ast.Constant):
        """Visit constant literals (strings, numbers)."""
        line_number = node.lineno
        line_snippet = self._get_line_snippet(line_number)

        # Skip if line has pragma
        if has_line_pragma(self.source_lines, line_number):
            self.generic_visit(node)
            return

        # Check magic numbers
        if isinstance(node.value, (int, float)):
            if node.value not in ALLOWED_NUMBERS:
                # Allow if it's a constant assignment (UPPER_CASE = value)
                if not self._is_constant_assignment(node):
                    self.violations.append(HardcodedViolation(
                        violation_type="MAGIC_NUMBER",
                        file_path=str(self.file_path),
                        line_number=line_number,
                        code_snippet=line_snippet,
                        value=str(node.value),
                        message=f"Magic number '{node.value}' should be a named constant"
                    ))

        # Check hardcoded strings
        if isinstance(node.value, str):
            value = node.value.strip()

            # Skip very short strings (likely not configuration)
            if len(value) <= 2:
                self.generic_visit(node)
                return

            # Check against patterns
            for pattern, description in HARDCODED_PATTERNS:
                if pattern.search(value):
                    self.violations.append(HardcodedViolation(
                        violation_type="HARDCODED_STRING",
                        file_path=str(self.file_path),
                        line_number=line_number,
                        code_snippet=line_snippet,
                        value=value[:50] + "..." if len(value) > 50 else value,
                        message=f"{description}: '{value[:50]}...'"
                    ))
                    break

        self.generic_visit(node)

    def visit_List(self, node: ast.List):
        """Visit list literals (check for citizen arrays)."""
        line_number = node.lineno
        line_snippet = self._get_line_snippet(line_number)

        # Skip if line has pragma
        if has_line_pragma(self.source_lines, line_number):
            self.generic_visit(node)
            return

        # Get source segment for this list
        try:
            list_text = ast.get_source_segment(self.source_code, node) or ""
        except (AttributeError, TypeError):
            list_text = ""

        # Check if it's a citizen array
        if CITIZEN_ARRAY_PATTERN.search(list_text):
            self.violations.append(HardcodedViolation(
                violation_type="CITIZEN_ARRAY",
                file_path=str(self.file_path),
                line_number=line_number,
                code_snippet=line_snippet,
                value=list_text[:50] + "..." if len(list_text) > 50 else list_text,
                message="Hardcoded citizen array - use graph query or settings"
            ))

        self.generic_visit(node)


def walk_with_parents(node: ast.AST, parent: Optional[ast.AST] = None):
    """Walk AST and attach parent references."""
    node._parent = parent
    for child in ast.iter_child_nodes(node):
        walk_with_parents(child, node)


def scan_file_for_hardcoded(file_path: Path) -> List[HardcodedViolation]:
    """
    Scan a Python file for hardcoded values.

    Args:
        file_path: Path to Python file

    Returns:
        List of HardcodedViolation objects
    """
    try:
        source_code = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    # Skip allowed paths
    if is_allowed_path(file_path, source_code):
        return []

    # Parse AST
    try:
        tree = ast.parse(source_code, filename=str(file_path))
    except SyntaxError:
        return []

    # Attach parent references
    walk_with_parents(tree)

    # Scan for violations
    scanner = HardcodedScanner(file_path, source_code)
    scanner.visit(tree)

    return scanner.violations


def scan_directory_for_hardcoded(directory: Path, exclude_patterns: Optional[List[str]] = None) -> List[HardcodedViolation]:
    """
    Scan a directory recursively for hardcoded values.

    Args:
        directory: Directory to scan
        exclude_patterns: Glob patterns to exclude

    Returns:
        List of all HardcodedViolation objects found
    """
    exclude_patterns = exclude_patterns or []
    all_violations = []

    for py_file in directory.rglob("*.py"):
        # Check exclusions
        if any(py_file.match(pattern) for pattern in exclude_patterns):
            continue

        violations = scan_file_for_hardcoded(py_file)
        all_violations.extend(violations)

    return all_violations
