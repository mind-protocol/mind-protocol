"""
Python AST Scanner - Find Event Emissions

Scans Python source files for event emission calls:
- broadcaster.broadcast_event(event_type, data)
- safe.safe_emit(event_type, data)
- await broadcaster.broadcast_event(...)
- await safe.safe_emit(...)

Extracts event_type (first argument) and location (file, line).

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-31
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class EventEmission:
    """
    Represents an event emission found in code.

    Attributes:
        event_type: Event name (e.g., "graph.delta.node.upsert")
        file_path: Path to file containing emission
        line_number: Line number of emission
        column: Column offset (0-indexed)
        code_snippet: Code snippet showing emission
        method_name: Method name ("broadcast_event" or "safe_emit")
    """
    event_type: str
    file_path: str
    line_number: int
    column: int
    code_snippet: str
    method_name: str


class PythonScanner(ast.NodeVisitor):
    """
    AST visitor to find event emission calls.

    Looks for:
    - obj.broadcast_event(event_type, ...)
    - obj.safe_emit(event_type, ...)

    Where event_type is a string literal.
    """

    def __init__(self, file_path: str, source_lines: List[str]):
        """
        Initialize scanner with file context.

        Args:
            file_path: Path to file being scanned
            source_lines: Source code lines (for extracting snippets)
        """
        self.file_path = file_path
        self.source_lines = source_lines
        self.emissions: List[EventEmission] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function call nodes to find event emissions."""
        # Check if this is a method call (obj.method(...))
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr

            # Check if method is broadcast_event or safe_emit
            if method_name in ("broadcast_event", "safe_emit"):
                # Extract event_type (first argument)
                if node.args and isinstance(node.args[0], ast.Constant):
                    event_type = node.args[0].value

                    # Only process string literals (skip variables)
                    if isinstance(event_type, str):
                        # Extract code snippet (with context)
                        code_snippet = self._extract_snippet(node.lineno)

                        # Create emission record
                        emission = EventEmission(
                            event_type=event_type,
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            code_snippet=code_snippet,
                            method_name=method_name
                        )
                        self.emissions.append(emission)

        # Continue visiting child nodes
        self.generic_visit(node)

    def _extract_snippet(self, line_number: int) -> str:
        """
        Extract code snippet showing emission.

        Args:
            line_number: Line number (1-indexed)

        Returns:
            Code snippet (single line or multi-line if call spans lines)
        """
        try:
            # Get line (1-indexed to 0-indexed)
            line_idx = line_number - 1

            if 0 <= line_idx < len(self.source_lines):
                line = self.source_lines[line_idx].rstrip()
                return line
            else:
                return ""
        except Exception:
            return ""


def scan_file(file_path: Path) -> List[EventEmission]:
    """
    Scan a Python file for event emissions.

    Args:
        file_path: Path to Python file

    Returns:
        List of EventEmission objects found in file
    """
    try:
        # Read source code
        with file_path.open("r", encoding="utf-8") as fh:
            source_code = fh.read()
            source_lines = source_code.splitlines()

        # Parse AST
        tree = ast.parse(source_code, filename=str(file_path))

        # Visit all nodes to find emissions
        scanner = PythonScanner(str(file_path), source_lines)
        scanner.visit(tree)

        return scanner.emissions

    except SyntaxError as exc:
        # Skip files with syntax errors (e.g., Python 2 code, broken files)
        print(f"Warning: Syntax error in {file_path}: {exc}")
        return []

    except Exception as exc:
        # Skip files that can't be read
        print(f"Warning: Failed to scan {file_path}: {exc}")
        return []


def scan_directory(
    directory: Path,
    pattern: str = "**/*.py",
    exclude_patterns: Optional[List[str]] = None
) -> List[EventEmission]:
    """
    Scan all Python files in a directory recursively.

    Args:
        directory: Root directory to scan
        pattern: Glob pattern for files (default: "**/*.py")
        exclude_patterns: Patterns to exclude (e.g., ["**/test_*.py", "**/venv/**"])

    Returns:
        List of EventEmission objects found across all files
    """
    if exclude_patterns is None:
        exclude_patterns = [
            "**/venv/**",
            "**/.venv/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.git/**",
        ]

    all_emissions = []

    # Find all Python files
    for file_path in directory.glob(pattern):
        # Skip if matches exclude pattern
        if any(file_path.match(pattern) for pattern in exclude_patterns):
            continue

        # Scan file
        emissions = scan_file(file_path)
        all_emissions.extend(emissions)

    return all_emissions
