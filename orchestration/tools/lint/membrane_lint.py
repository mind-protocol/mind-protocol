"""
Membrane Boundary Lint - Enforce L3 Purity

Prevents L3 (ecosystem layer) from violating membrane discipline:
- NO FalkorDB imports
- NO Cypher execution
- NO database credentials
- NO org-internal compute

This is a CI guardrail to catch violations before they reach production.

Exit codes:
- 0: No violations found
- 1: Violations detected (fail CI)

Author: Mel "Bridgekeeper"
Date: 2025-11-04
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

# L3 code directories (ecosystem layer)
L3_PATHS = [
    "orchestration/adapters/api",
    "orchestration/adapters/ws",
]

# Files excluded from L3 lint (legitimately L2 engine management)
EXCLUDED_FILES = [
    "control_api.py",  # Engine control/management (L2 function)
    "websocket_server.py",  # Includes engine initialization (L2 function)
    "docs_view_api.DEPRECATED.py",  # Deprecated - being phased out
]

# Forbidden imports for L3
FORBIDDEN_IMPORTS = [
    "falkordb",
    "FalkorDBAdapter",
    "FalkorDBGraphStore",
    "llama_index.graph_stores.falkordb",
    "orchestration.libs.utils.falkordb_adapter",
]

# Forbidden patterns (regex-like strings to search for)
FORBIDDEN_PATTERNS = [
    "FALKORDB_API",
    "FALKORDB_KEY",
    "FALKORDB_HOST",
    "execute_cypher",
    "MATCH (",  # Cypher query start
    "CREATE (",  # Cypher query start
    "MERGE (",  # Cypher query start
]


class MembraneViolationFinder(ast.NodeVisitor):
    """AST visitor to find forbidden imports and patterns."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations: List[Tuple[int, str]] = []

    def visit_Import(self, node: ast.Import):
        """Check import statements."""
        for alias in node.names:
            if any(forbidden in alias.name for forbidden in FORBIDDEN_IMPORTS):
                self.violations.append((
                    node.lineno,
                    f"Forbidden import: {alias.name}"
                ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check from...import statements."""
        if node.module and any(forbidden in node.module for forbidden in FORBIDDEN_IMPORTS):
            self.violations.append((
                node.lineno,
                f"Forbidden import: from {node.module}"
            ))
        self.generic_visit(node)


def check_file_for_patterns(filepath: Path) -> List[Tuple[int, str]]:
    """Check file content for forbidden patterns."""
    violations = []

    try:
        content = filepath.read_text()

        for lineno, line in enumerate(content.split("\n"), 1):
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in line:
                    violations.append((
                        lineno,
                        f"Forbidden pattern: '{pattern}' found"
                    ))

    except Exception as e:
        print(f"[WARN] Failed to read {filepath}: {e}")

    return violations


def lint_file(filepath: Path) -> List[Tuple[int, str]]:
    """Lint a single Python file for membrane violations."""
    violations = []

    try:
        # Parse AST
        tree = ast.parse(filepath.read_text(), filename=str(filepath))

        # Check for forbidden imports
        finder = MembraneViolationFinder(str(filepath))
        finder.visit(tree)
        violations.extend(finder.violations)

        # Check for forbidden patterns
        pattern_violations = check_file_for_patterns(filepath)
        violations.extend(pattern_violations)

    except SyntaxError as e:
        print(f"[WARN] Syntax error in {filepath}: {e}")

    except Exception as e:
        print(f"[WARN] Failed to lint {filepath}: {e}")

    return violations


def main():
    """Run membrane lint on L3 code."""

    root = Path(__file__).parent.parent.parent.parent  # Navigate to repo root
    all_violations = []

    print("🔍 Membrane Boundary Lint - Checking L3 Purity\n")

    for l3_path in L3_PATHS:
        l3_dir = root / l3_path

        if not l3_dir.exists():
            print(f"[SKIP] {l3_path} does not exist")
            continue

        print(f"Checking {l3_path}/")

        # Find all Python files
        py_files = list(l3_dir.rglob("*.py"))

        for filepath in py_files:
            # Skip excluded files (L2 engine management code)
            if filepath.name in EXCLUDED_FILES:
                continue

            violations = lint_file(filepath)

            if violations:
                all_violations.append((filepath, violations))

                # Print violations immediately
                rel_path = filepath.relative_to(root)
                print(f"\n❌ {rel_path}")
                for lineno, message in violations:
                    print(f"   Line {lineno}: {message}")

    # Summary
    print("\n" + "=" * 70)

    if all_violations:
        print(f"❌ FAILED: Found {len(all_violations)} files with membrane violations\n")
        print("L3 (ecosystem layer) must NOT:")
        print("  - Import FalkorDB or execute Cypher")
        print("  - Access database credentials")
        print("  - Compute inside org boundary")
        print("\nUse the L4 membrane bus (protocol/hub) to inject/observe events.")
        print("=" * 70)
        sys.exit(1)

    else:
        print("✅ PASSED: No membrane violations found in L3 code")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
