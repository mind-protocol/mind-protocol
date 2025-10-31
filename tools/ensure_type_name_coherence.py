#!/usr/bin/env python3
"""
Ensure type_name ↔ Label Coherence

Write-helper and validation utility to enforce:
- Nodes have exactly one U3_/U4_/type-specific label
- type_name property matches that label exactly
- CI can run this to catch drift

Usage:
    # Validate existing nodes
    python tools/ensure_type_name_coherence.py --validate --graph protocol

    # Fix mismatches (add missing labels or update type_name)
    python tools/ensure_type_name_coherence.py --fix --graph protocol
"""

from falkordb import FalkorDB
from typing import Tuple, List


def validate_type_name_coherence(graph_name: str) -> Tuple[bool, List[str]]:
    """
    Validate that type_name matches primary label.

    Returns:
        (passed: bool, violations: List[str])
    """
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph(graph_name)

    violations = []

    # Check 1: type_name doesn't match primary label
    result = g.query("""
        MATCH (n)
        WHERE n.type_name IS NOT NULL
        WITH n,
             [label IN labels(n)
              WHERE label <> 'ProtocolNode'
                AND (label STARTS WITH 'U3_'
                     OR label STARTS WITH 'U4_'
                     OR label STARTS WITH 'L1_'
                     OR label STARTS WITH 'L2_'
                     OR label STARTS WITH 'L3_'
                     OR label STARTS WITH 'L4_'
                     OR label IN ['Event_Schema', 'Governance_Policy', 'Signature_Suite',
                                  'Topic_Namespace', 'Capability', 'Tool_Contract',
                                  'Mechanism', 'Principle', 'Process', 'Interface',
                                  'Metric', 'SubEntity', 'Envelope_Schema', 'Schema_Bundle',
                                  'Protocol_Version', 'Conformance_Case', 'Conformance_Suite',
                                  'Conformance_Result', 'Security_Profile', 'Transport_Spec',
                                  'Topic_Route', 'Bus_Instance', 'Tenant', 'Tenant_Key',
                                  'SDK_Release', 'Adapter_Release', 'Sidecar_Release',
                                  'Retention_Policy', 'Compatibility_Matrix', 'Deprecation_Notice',
                                  'Event', 'Task'])
             ] as type_labels
        WHERE size(type_labels) > 0
          AND head(type_labels) <> n.type_name
        RETURN n.name as name,
               n.type_name as type_name,
               head(type_labels) as primary_label,
               type_labels as all_type_labels
        LIMIT 50
    """)

    for record in result.result_set:
        name = record[0] or "(unnamed)"
        type_name = record[1]
        primary_label = record[2]
        all_labels = record[3]
        violations.append(
            f"Node '{name}': type_name='{type_name}' doesn't match label '{primary_label}' (labels: {all_labels})"
        )

    # Check 2: Multiple type-specific labels
    result = g.query("""
        MATCH (n)
        WITH n,
             [label IN labels(n)
              WHERE label STARTS WITH 'U3_'
                 OR label STARTS WITH 'U4_'
             ] as universal_labels
        WHERE size(universal_labels) > 1
        RETURN n.name as name,
               n.type_name as type_name,
               universal_labels as labels
        LIMIT 50
    """)

    for record in result.result_set:
        name = record[0] or "(unnamed)"
        type_name = record[1]
        labels = record[2]
        violations.append(
            f"Node '{name}' has multiple U3_/U4_ labels: {labels} (type_name: {type_name})"
        )

    # Check 3: Has type_name but no matching label
    result = g.query("""
        MATCH (n)
        WHERE n.type_name IS NOT NULL
        WITH n,
             [label IN labels(n) WHERE label = n.type_name] as matching_labels
        WHERE size(matching_labels) = 0
        RETURN n.name as name,
               n.type_name as type_name,
               labels(n) as labels
        LIMIT 50
    """)

    for record in result.result_set:
        name = record[0] or "(unnamed)"
        type_name = record[1]
        labels = record[2]
        violations.append(
            f"Node '{name}': type_name='{type_name}' but no matching label in {labels}"
        )

    return (len(violations) == 0, violations)


def fix_type_name_coherence(graph_name: str, dry_run: bool = False) -> int:
    """
    Fix type_name/label mismatches.

    Strategy:
    1. If node has type_name but no matching label → add label
    2. If node has label but no/wrong type_name → set type_name

    Returns:
        Number of nodes fixed
    """
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph(graph_name)

    print(f"{'[DRY RUN] ' if dry_run else ''}Fixing type_name coherence in {graph_name}...\n")

    fixed_count = 0

    # Fix 1: Add missing labels
    result = g.query("""
        MATCH (n)
        WHERE n.type_name IS NOT NULL
        WITH n,
             [label IN labels(n) WHERE label = n.type_name] as matching_labels
        WHERE size(matching_labels) = 0
        RETURN id(n) as node_id,
               n.name as name,
               n.type_name as type_name,
               labels(n) as current_labels
    """)

    for record in result.result_set:
        node_id = record[0]
        name = record[1] or "(unnamed)"
        type_name = record[2]
        current_labels = record[3]

        if dry_run:
            print(f"  [DRY RUN] Would add label '{type_name}' to node '{name}'")
        else:
            query = f"""
                MATCH (n) WHERE id(n) = {node_id}
                SET n:{type_name}
                RETURN labels(n)
            """
            g.query(query)
            print(f"  ✓ Added label '{type_name}' to node '{name}'")
            fixed_count += 1

    # Fix 2: Set missing/wrong type_name
    result = g.query("""
        MATCH (n)
        WITH n,
             [label IN labels(n)
              WHERE label <> 'ProtocolNode'
                AND (label STARTS WITH 'U3_' OR label STARTS WITH 'U4_')
             ] as type_labels
        WHERE size(type_labels) > 0
          AND (n.type_name IS NULL OR n.type_name <> head(type_labels))
        RETURN id(n) as node_id,
               n.name as name,
               n.type_name as old_type_name,
               head(type_labels) as new_type_name
    """)

    for record in result.result_set:
        node_id = record[0]
        name = record[1] or "(unnamed)"
        old_type_name = record[2]
        new_type_name = record[3]

        if dry_run:
            print(f"  [DRY RUN] Would set type_name='{new_type_name}' on node '{name}' (was: {old_type_name})")
        else:
            query = f"""
                MATCH (n) WHERE id(n) = {node_id}
                SET n.type_name = '{new_type_name}'
                RETURN n.type_name
            """
            g.query(query)
            print(f"  ✓ Set type_name='{new_type_name}' on node '{name}'")
            fixed_count += 1

    return fixed_count


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Ensure type_name ↔ Label Coherence"
    )
    parser.add_argument(
        '--graph',
        required=True,
        help='Graph name to check (e.g., "protocol", "mind-protocol_ada")'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate coherence (exit 1 if violations found)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Fix mismatches automatically'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without making changes'
    )

    args = parser.parse_args()

    if args.validate:
        print(f"Validating type_name coherence in {args.graph}...\n")
        passed, violations = validate_type_name_coherence(args.graph)

        if passed:
            print(f"✅ All nodes in {args.graph} have coherent type_name/labels")
            return 0
        else:
            print(f"❌ Found {len(violations)} violations in {args.graph}:\n")
            for v in violations[:20]:
                print(f"  - {v}")
            if len(violations) > 20:
                print(f"  ... and {len(violations) - 20} more")
            return 1

    elif args.fix or args.dry_run:
        fixed = fix_type_name_coherence(args.graph, dry_run=args.dry_run)

        if args.dry_run:
            print(f"\n[DRY RUN] Would fix {fixed} nodes")
        else:
            print(f"\n✅ Fixed {fixed} nodes")

        # Re-validate
        print("\nRe-validating...")
        passed, violations = validate_type_name_coherence(args.graph)

        if passed:
            print(f"✅ All nodes now have coherent type_name/labels")
            return 0
        else:
            print(f"⚠️  Still have {len(violations)} violations (may require manual review)")
            return 1

    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    import sys
    sys.exit(main())
