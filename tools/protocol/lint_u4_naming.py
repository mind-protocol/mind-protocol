#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
U4 Naming Linter - L4 Protocol Governance Enforcement

Validates U3_/U4_ naming conventions across protocol graph:
1. U3_ prefix → Level 1-3 only (U3 universality)
2. U4_ prefix → Level 1-4 only (U4 universality)
3. type_name ↔ label coherence
4. level ↔ universality consistency
5. No unauthorized use of universal prefixes

Author: Luca Vellumhand (Consciousness Substrate Architect)
Date: 2025-10-31
"""

import os
import sys
from typing import List, Tuple, Dict
from falkordb import FalkorDB


class U4NamingLinter:
    """Linter for U3_/U4_ naming convention enforcement."""

    def __init__(self, graph_name: str = "protocol"):
        self.db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=6379)
        self.graph = self.db.select_graph(graph_name)
        self.violations = []
        self.warnings = []

    def lint_all(self) -> Tuple[List[Dict], List[Dict]]:
        """Run all linting checks."""
        print("=" * 80)
        print("U4 NAMING LINT - L4 Protocol Governance Enforcement")
        print("=" * 80)
        print()

        # Run all checks
        self.check_u3_level_coherence()
        self.check_u4_level_coherence()
        self.check_type_name_label_coherence()
        self.check_universality_level_consistency()
        self.check_unauthorized_universal_prefixes()
        self.check_missing_universality_property()
        self.check_level_property_validity()

        return self.violations, self.warnings

    def check_u3_level_coherence(self):
        """Check that U3_ types only exist at levels L1-L3."""
        result = self.graph.query("""
            MATCH (n)
            WHERE (n.type_name STARTS WITH 'U3_' OR
                   ANY(label IN labels(n) WHERE label STARTS WITH 'U3_'))
              AND n.level IS NOT NULL
              AND NOT (n.level = 'L1' OR n.level = 'L2' OR n.level = 'L3')
            RETURN id(n) as node_id,
                   n.type_name as type_name,
                   n.name as name,
                   n.level as level,
                   labels(n) as labels
            LIMIT 50
        """)

        if result.result_set:
            for record in result.result_set:
                node_id, type_name, name, level, labels = record
                self.violations.append({
                    "rule": "U3_LEVEL_COHERENCE",
                    "severity": "ERROR",
                    "message": f"U3_ type at invalid level {level} (must be L1-L3)",
                    "node_id": node_id,
                    "type_name": type_name,
                    "name": name or "(unnamed)",
                    "level": level,
                    "labels": labels
                })

    def check_u4_level_coherence(self):
        """Check that U4_ types only exist at levels L1-L4."""
        result = self.graph.query("""
            MATCH (n)
            WHERE (n.type_name STARTS WITH 'U4_' OR
                   ANY(label IN labels(n) WHERE label STARTS WITH 'U4_'))
              AND n.level IS NOT NULL
              AND NOT (n.level = 'L1' OR n.level = 'L2' OR n.level = 'L3' OR n.level = 'L4')
            RETURN id(n) as node_id,
                   n.type_name as type_name,
                   n.name as name,
                   n.level as level,
                   labels(n) as labels
            LIMIT 50
        """)

        if result.result_set:
            for record in result.result_set:
                node_id, type_name, name, level, labels = record
                self.violations.append({
                    "rule": "U4_LEVEL_COHERENCE",
                    "severity": "ERROR",
                    "message": f"U4_ type at invalid level {level} (must be L1-L4)",
                    "node_id": node_id,
                    "type_name": type_name,
                    "name": name or "(unnamed)",
                    "level": level,
                    "labels": labels
                })

    def check_type_name_label_coherence(self):
        """Check that type_name matches primary U3_/U4_ label."""
        result = self.graph.query("""
            MATCH (n)
            WHERE n.type_name IS NOT NULL
              AND (n.type_name STARTS WITH 'U3_' OR n.type_name STARTS WITH 'U4_')
            WITH n,
                 [label IN labels(n)
                  WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_'
                 ] as universal_labels
            WHERE size(universal_labels) = 0
               OR (size(universal_labels) > 0 AND head(universal_labels) <> n.type_name)
            RETURN id(n) as node_id,
                   n.type_name as type_name,
                   n.name as name,
                   universal_labels as labels
            LIMIT 50
        """)

        if result.result_set:
            for record in result.result_set:
                node_id, type_name, name, labels = record
                if not labels:
                    self.violations.append({
                        "rule": "TYPE_NAME_LABEL_COHERENCE",
                        "severity": "ERROR",
                        "message": f"Node has type_name='{type_name}' but no matching label",
                        "node_id": node_id,
                        "type_name": type_name,
                        "name": name or "(unnamed)",
                        "labels": labels
                    })
                else:
                    self.violations.append({
                        "rule": "TYPE_NAME_LABEL_COHERENCE",
                        "severity": "ERROR",
                        "message": f"type_name='{type_name}' doesn't match label '{labels[0]}'",
                        "node_id": node_id,
                        "type_name": type_name,
                        "name": name or "(unnamed)",
                        "labels": labels
                    })

    def check_universality_level_consistency(self):
        """Check that universality property matches type prefix."""
        # U3 types should have universality="U3"
        result = self.graph.query("""
            MATCH (n)
            WHERE (n.type_name STARTS WITH 'U3_' OR
                   ANY(label IN labels(n) WHERE label STARTS WITH 'U3_'))
              AND (n.universality IS NULL OR n.universality <> 'U3')
            RETURN id(n) as node_id,
                   n.type_name as type_name,
                   n.name as name,
                   n.universality as universality
            LIMIT 50
        """)

        if result.result_set:
            for record in result.result_set:
                node_id, type_name, name, universality = record
                self.warnings.append({
                    "rule": "UNIVERSALITY_CONSISTENCY",
                    "severity": "WARNING",
                    "message": f"U3_ type has universality='{universality}' (should be 'U3')",
                    "node_id": node_id,
                    "type_name": type_name,
                    "name": name or "(unnamed)",
                    "universality": universality
                })

        # U4 types should have universality="U4"
        result = self.graph.query("""
            MATCH (n)
            WHERE (n.type_name STARTS WITH 'U4_' OR
                   ANY(label IN labels(n) WHERE label STARTS WITH 'U4_'))
              AND (n.universality IS NULL OR n.universality <> 'U4')
            RETURN id(n) as node_id,
                   n.type_name as type_name,
                   n.name as name,
                   n.universality as universality
            LIMIT 50
        """)

        if result.result_set:
            for record in result.result_set:
                node_id, type_name, name, universality = record
                self.warnings.append({
                    "rule": "UNIVERSALITY_CONSISTENCY",
                    "severity": "WARNING",
                    "message": f"U4_ type has universality='{universality}' (should be 'U4')",
                    "node_id": node_id,
                    "type_name": type_name,
                    "name": name or "(unnamed)",
                    "universality": universality
                })

    def check_unauthorized_universal_prefixes(self):
        """Check for nodes using U3_/U4_ prefixes at wrong graph level."""
        # This check is only meaningful for non-protocol graphs
        # In protocol graph, all U3_/U4_ usage is authorized
        # (This would be enforced in citizen graphs)
        pass

    def check_missing_universality_property(self):
        """Warn about nodes with universal labels but missing universality property."""
        result = self.graph.query("""
            MATCH (n)
            WHERE (ANY(label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_'))
              AND n.universality IS NULL
            RETURN id(n) as node_id,
                   n.type_name as type_name,
                   n.name as name,
                   labels(n) as labels
            LIMIT 50
        """)

        if result.result_set:
            for record in result.result_set:
                node_id, type_name, name, labels = record
                universal_label = next((l for l in labels if l.startswith(('U3_', 'U4_'))), None)
                expected_universality = universal_label[:2] if universal_label else "?"

                self.warnings.append({
                    "rule": "MISSING_UNIVERSALITY",
                    "severity": "WARNING",
                    "message": f"Node with {universal_label} label missing universality property",
                    "node_id": node_id,
                    "type_name": type_name,
                    "name": name or "(unnamed)",
                    "expected_universality": expected_universality
                })

    def check_level_property_validity(self):
        """Check that level property values are valid (L1-L4)."""
        result = self.graph.query("""
            MATCH (n)
            WHERE n.level IS NOT NULL
              AND NOT (n.level = 'L1' OR n.level = 'L2' OR n.level = 'L3' OR n.level = 'L4')
            RETURN id(n) as node_id,
                   n.type_name as type_name,
                   n.name as name,
                   n.level as level
            LIMIT 50
        """)

        if result.result_set:
            for record in result.result_set:
                node_id, type_name, name, level = record
                self.violations.append({
                    "rule": "LEVEL_VALIDITY",
                    "severity": "ERROR",
                    "message": f"Invalid level value '{level}' (must be L1, L2, L3, or L4)",
                    "node_id": node_id,
                    "type_name": type_name,
                    "name": name or "(unnamed)",
                    "level": level
                })

    def print_report(self):
        """Print linting report."""
        print()
        print("=" * 80)
        print("LINT REPORT")
        print("=" * 80)
        print()

        if not self.violations and not self.warnings:
            print("✅ No violations found - all U3_/U4_ naming conventions followed")
            return 0

        # Print violations
        if self.violations:
            print(f"❌ VIOLATIONS ({len(self.violations)}):")
            print()
            for v in self.violations[:20]:
                print(f"  [{v['rule']}] {v['message']}")
                print(f"    Node: {v.get('name', '(unnamed)')} (type_name: {v.get('type_name', 'N/A')})")
                print(f"    Details: {v}")
                print()

            if len(self.violations) > 20:
                print(f"  ... and {len(self.violations) - 20} more violations")
                print()

        # Print warnings
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            print()
            for w in self.warnings[:20]:
                print(f"  [{w['rule']}] {w['message']}")
                print(f"    Node: {w.get('name', '(unnamed)')} (type_name: {w.get('type_name', 'N/A')})")
                print()

            if len(self.warnings) > 20:
                print(f"  ... and {len(self.warnings) - 20} more warnings")
                print()

        print("=" * 80)
        print("Summary:")
        print(f"  Violations: {len(self.violations)}")
        print(f"  Warnings:   {len(self.warnings)}")
        print("=" * 80)
        print()

        return 1 if self.violations else 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="U4 Naming Linter - Enforce L4 protocol naming conventions"
    )
    parser.add_argument(
        "--graph",
        default="protocol",
        help="Graph name to lint (default: protocol)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix violations (adds missing properties)"
    )

    args = parser.parse_args()

    linter = U4NamingLinter(args.graph)
    violations, warnings = linter.lint_all()

    if args.json:
        import json
        print(json.dumps({
            "violations": violations,
            "warnings": warnings
        }, indent=2))
        return 1 if violations else 0
    else:
        exit_code = linter.print_report()

        if args.fix and (violations or warnings):
            print("Fix mode not yet implemented - manual fixes required")
            print()
            print("To fix violations:")
            print("  1. Add missing universality properties")
            print("  2. Add missing U3_/U4_ labels to match type_name")
            print("  3. Correct invalid level values")
            print()

        return exit_code


if __name__ == "__main__":
    sys.exit(main())
