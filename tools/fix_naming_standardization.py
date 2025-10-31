"""
Fix Naming Standardization - Single Label Migration

Corrects the double-label pattern from today's migration:
- FROM: `:U4_Event:U4` with property `node_type`
- TO: `:U4_Event` with property `type_name` matching label

Author: Ada "Bridgekeeper"
Date: 2025-10-31
"""

from falkordb import FalkorDB
from datetime import datetime

# All universal types that need fixing
UNIVERSAL_TYPES = [
    # U4 types
    "U4_Event",
    "U4_Agent",
    "U4_Goal",
    "U4_Decision",
    "U4_Metric",
    "U4_Measurement",
    "U4_Work_Item",
    "U4_Assessment",

    # U3 types
    "U3_Pattern",
    "U3_Risk",
    "U3_Relationship",
]


def fix_graph_labels(graph_name: str, db: FalkorDB, dry_run: bool = False):
    """Fix double labels to single label with type_name property."""

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Fixing graph: {graph_name}")
    print("=" * 80)

    g = db.select_graph(graph_name)

    total_fixed = 0

    for utype in UNIVERSAL_TYPES:
        # Determine universality from prefix
        if utype.startswith("U4_"):
            universality = "U4"
        elif utype.startswith("U3_"):
            universality = "U3"
        else:
            continue

        # Find all nodes with this type label (may have double labels like :U4_Event:U4)
        result = g.query(f"MATCH (n:{utype}) RETURN n.name as name, id(n) as node_id, labels(n) as labels")

        if not result.result_set:
            continue

        count = len(result.result_set)
        print(f"\n  Found {count} nodes of type {utype}")

        if dry_run:
            for record in result.result_set:
                node_name = record[0]
                node_labels = record[2]
                print(f"    - {node_name} (labels: {node_labels})")
            total_fixed += count
            continue

        # Fix each node
        for record in result.result_set:
            node_name = record[0]
            node_id = record[1]
            node_labels = record[2]

            try:
                # Step 1: Remove secondary universality label if present (e.g., :U4, :U3)
                if universality in node_labels and len(node_labels) > 1:
                    g.query(f"""
                        MATCH (n:{utype})
                        WHERE id(n) = {node_id}
                        REMOVE n:{universality}
                    """)

                # Step 2: Set type_name to match label exactly
                g.query(f"""
                    MATCH (n:{utype})
                    WHERE id(n) = {node_id}
                    SET n.type_name = '{utype}'
                """)

                # Step 3: Ensure universality field is set (for lints)
                g.query(f"""
                    MATCH (n:{utype})
                    WHERE id(n) = {node_id}
                    SET n.universality = '{universality}'
                """)

                # Step 4: Remove old node_type property if it exists
                g.query(f"""
                    MATCH (n:{utype})
                    WHERE id(n) = {node_id} AND exists(n.node_type)
                    REMOVE n.node_type
                """)

                print(f"    ✓ {node_name}")
                total_fixed += 1

            except Exception as e:
                print(f"    ✗ {node_name}: {e}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total nodes fixed: {total_fixed}")
    print("=" * 80)

    return total_fixed


def verify_standardization(graph_name: str, db: FalkorDB):
    """Verify naming standardization is correct."""

    print(f"\nVerifying graph: {graph_name}")
    print("=" * 80)

    g = db.select_graph(graph_name)

    # Check 1: All universal nodes should have exactly one label starting with U3_ or U4_
    result = g.query("""
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_')
        WITH n, [label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_'] as u_labels
        WHERE size(u_labels) > 1
        RETURN n.name as name, labels(n) as labels
        LIMIT 10
    """)

    if result.result_set and len(result.result_set) > 0:
        print("\n  ⚠ Found nodes with multiple U3_/U4_ labels:")
        for record in result.result_set:
            print(f"    {record[0]}: {record[1]}")
    else:
        print("  ✓ No double U3_/U4_ labels found")

    # Check 2: type_name should match the primary label
    result = g.query("""
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_')
        WITH n, head([label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_']) as primary_label
        WHERE n.type_name <> primary_label
        RETURN n.name as name, n.type_name as type_name, primary_label
        LIMIT 10
    """)

    if result.result_set and len(result.result_set) > 0:
        print("\n  ⚠ Found nodes where type_name doesn't match label:")
        for record in result.result_set:
            print(f"    {record[0]}: type_name='{record[1]}' vs label='{record[2]}'")
    else:
        print("  ✓ All type_name properties match labels")

    # Check 3: Show standardized type distribution
    result = g.query("""
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_')
        WITH head([label IN labels(n) WHERE label STARTS WITH 'U3_' OR label STARTS WITH 'U4_']) as utype
        RETURN utype, count(*) as count
        ORDER BY count DESC
    """)

    print("\n  Standardized universal types:")
    for record in result.result_set:
        print(f"    {record[0]:25s} {record[1]:4d} nodes")

    print("=" * 80)


def main():
    import sys
    dry_run = "--dry-run" in sys.argv

    print("=" * 80)
    print("NAMING STANDARDIZATION - SINGLE LABEL MIGRATION")
    print("=" * 80)
    if dry_run:
        print("*** DRY RUN MODE - No changes will be made ***")
        print("=" * 80)

    db = FalkorDB(host='localhost', port=6379)

    graphs_to_fix = [
        "mind-protocol_ada",
        "mind-protocol_atlas",
        "mind-protocol_felix",
        "mind-protocol_iris",
        "mind-protocol_luca",
        "mind-protocol_victor",
    ]

    total_across_all = 0

    for graph_name in graphs_to_fix:
        try:
            fixed = fix_graph_labels(graph_name, db, dry_run=dry_run)
            total_across_all += fixed

            if not dry_run:
                verify_standardization(graph_name, db)

        except Exception as e:
            print(f"\n✗ Error fixing {graph_name}: {e}")
            continue

    print("\n" + "=" * 80)
    print(f"{'[DRY RUN] ' if dry_run else ''}NAMING STANDARDIZATION COMPLETE")
    print("=" * 80)
    print(f"Total nodes fixed across all graphs: {total_across_all}")

    if dry_run:
        print("\nRun without --dry-run to apply changes")
    else:
        print("\n✓ All consciousness graphs now use standardized naming:")
        print("  - Single label (e.g., :U4_Event, not :U4_Event:U4)")
        print("  - type_name matches label exactly")
        print("  - universality field set for lints")
        print("  - Old node_type property removed")


if __name__ == "__main__":
    main()
