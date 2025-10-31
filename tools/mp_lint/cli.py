#!/usr/bin/env python3
"""
Membrane Linter CLI - L4 Protocol Law Enforcement

Usage:
    python tools/mp_lint/cli.py                    # Lint all consciousness graphs
    python tools/mp_lint/cli.py --graph luca      # Lint specific graph
    python tools/mp_lint/cli.py --export          # Export L4 registry first
    python tools/mp_lint/cli.py --check-code      # Check code/registry drift

Exit codes:
    0 = All rules passed
    1 = Lint violations found
    2 = Error running linter

Author: Ada "Bridgekeeper"
Date: 2025-10-31
"""

import sys
import argparse
from typing import List
from falkordb import FalkorDB

from lint_rules import (
    lint_label_property_coherence,
    lint_universality_level_coherence,
    lint_no_double_labels,
    lint_schema_code_drift,
)
from registry_export import export_registry


def lint_graph(graph_name: str, db: FalkorDB) -> bool:
    """Run all lint rules on a graph. Returns True if all pass."""

    print(f"\n{'='*80}")
    print(f"Linting graph: {graph_name}")
    print('='*80)

    all_passed = True

    # Rule 1: Label/property coherence
    print("\n[1/3] Checking label/property coherence...")
    passed, violations = lint_label_property_coherence(db, graph_name)
    if passed:
        print("  ✓ All nodes have coherent type_name/label")
    else:
        print(f"  ✗ Found {len(violations)} violations:")
        for v in violations[:10]:  # Show first 10
            print(f"    - {v}")
        if len(violations) > 10:
            print(f"    ... and {len(violations) - 10} more")
        all_passed = False

    # Rule 2: Universality/level coherence
    print("\n[2/3] Checking universality/level coherence...")
    passed, violations = lint_universality_level_coherence(db, graph_name)
    if passed:
        print("  ✓ All U3/U4 nodes have valid levels")
    else:
        print(f"  ✗ Found {len(violations)} violations:")
        for v in violations[:10]:
            print(f"    - {v}")
        if len(violations) > 10:
            print(f"    ... and {len(violations) - 10} more")
        all_passed = False

    # Rule 3: No double labels
    print("\n[3/3] Checking for double U3_/U4_ labels...")
    passed, violations = lint_no_double_labels(db, graph_name)
    if passed:
        print("  ✓ No nodes with multiple universal labels")
    else:
        print(f"  ✗ Found {len(violations)} violations:")
        for v in violations[:10]:
            print(f"    - {v}")
        if len(violations) > 10:
            print(f"    ... and {len(violations) - 10} more")
        all_passed = False

    return all_passed


def lint_code_schemas() -> bool:
    """Check if code schemas match L4 registry."""

    print(f"\n{'='*80}")
    print("Checking code/registry drift")
    print('='*80)

    # Export registry
    print("\n[1/2] Exporting L4 registry...")
    registry = export_registry("build/l4_registry.json")

    # Load code schemas
    print("\n[2/2] Checking against complete_schema_data.py...")
    try:
        # Import the schema data
        import sys
        sys.path.insert(0, '/home/mind-protocol/mindprotocol/tools')
        from complete_schema_data import NODE_TYPE_SCHEMAS

        # Filter to universal types only
        code_schemas = {
            name: schema for name, schema in NODE_TYPE_SCHEMAS.items()
            if name.startswith('U3_') or name.startswith('U4_')
        }

        passed, violations = lint_schema_code_drift(registry, code_schemas)

        if passed:
            print(f"  ✓ Code schemas match L4 registry ({len(code_schemas)} types)")
        else:
            print(f"  ✗ Found {len(violations)} drift issues:")
            for v in violations:
                print(f"    - {v}")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Error checking code schemas: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Membrane Linter - L4 Protocol Law Enforcement"
    )
    parser.add_argument(
        '--graph',
        help='Lint specific graph (e.g., "luca", "ada"). Default: all graphs'
    )
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export L4 registry before linting'
    )
    parser.add_argument(
        '--check-code',
        action='store_true',
        help='Check code/registry drift only'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("MEMBRANE LINTER - L4 Protocol Law Enforcement")
    print("=" * 80)

    # Export registry if requested
    if args.export:
        print("\nExporting L4 registry...")
        export_registry("build/l4_registry.json")
        if not args.check_code and not args.graph:
            print("\n✓ Registry exported successfully")
            return 0

    # Check code/registry drift if requested
    if args.check_code:
        passed = lint_code_schemas()
        if not passed:
            print("\n" + "=" * 80)
            print("LINT FAILED: Code/registry drift detected")
            print("=" * 80)
            return 1

        if not args.graph:
            print("\n" + "=" * 80)
            print("✓ All lint checks passed")
            print("=" * 80)
            return 0

    # Lint consciousness graphs
    db = FalkorDB(host='localhost', port=6379)

    if args.graph:
        # Lint specific graph
        graph_name = f"consciousness-infrastructure_mind-protocol_{args.graph}"
        passed = lint_graph(graph_name, db)

        if not passed:
            print("\n" + "=" * 80)
            print(f"LINT FAILED: {graph_name}")
            print("=" * 80)
            return 1
    else:
        # Lint all graphs
        graphs = [
            "consciousness-infrastructure_mind-protocol_ada",
            "consciousness-infrastructure_mind-protocol_atlas",
            "consciousness-infrastructure_mind-protocol_felix",
            "consciousness-infrastructure_mind-protocol_iris",
            "consciousness-infrastructure_mind-protocol_luca",
            "consciousness-infrastructure_mind-protocol_victor",
        ]

        all_passed = True
        for graph in graphs:
            passed = lint_graph(graph, db)
            if not passed:
                all_passed = False

        if not all_passed:
            print("\n" + "=" * 80)
            print("LINT FAILED: Some graphs have violations")
            print("=" * 80)
            return 1

    print("\n" + "=" * 80)
    print("✓ All lint checks passed")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
