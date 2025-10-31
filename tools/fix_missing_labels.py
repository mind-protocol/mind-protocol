#!/usr/bin/env python3
"""
Fix Missing Labels in Protocol Graph

Some nodes have type_name property but are missing the corresponding label.
This script adds the missing labels so nodes are [:ProtocolNode:Event_Schema]
instead of just [:ProtocolNode] with type_name="Event_Schema".
"""

from falkordb import FalkorDB

def fix_missing_labels(dry_run: bool = False):
    """Add missing labels to nodes that have type_name but no specific label."""

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    print("=" * 80)
    print("Fixing Missing Labels in Protocol Graph")
    print("=" * 80)

    if dry_run:
        print("\n⚠️  DRY RUN MODE\n")

    # Find nodes with type_name but only ProtocolNode label
    result = g.query("""
        MATCH (n:ProtocolNode)
        WHERE n.type_name IS NOT NULL
        WITH n, [label IN labels(n) WHERE label <> 'ProtocolNode'] as other_labels
        WHERE size(other_labels) = 0
        RETURN id(n) as node_id,
               n.type_name as type_name,
               n.name as name,
               labels(n) as current_labels
        ORDER BY n.type_name, n.name
    """)

    nodes_to_fix = result.result_set
    print(f"Found {len(nodes_to_fix)} nodes with missing labels\n")

    if not nodes_to_fix:
        print("✅ No nodes to fix - all labels correct")
        return

    # Group by type_name
    from collections import defaultdict
    by_type = defaultdict(list)

    for node_id, type_name, name, current_labels in nodes_to_fix:
        by_type[type_name].append((node_id, name, current_labels))

    print("Nodes by type_name:")
    for type_name, nodes in sorted(by_type.items()):
        print(f"  {type_name}: {len(nodes)} nodes")
    print()

    # Fix each node
    fixed_count = 0

    for node_id, type_name, name, current_labels in nodes_to_fix:
        display_name = name or f"(unnamed {type_name})"

        # Add the missing label
        query = f"""
            MATCH (n)
            WHERE id(n) = {node_id}
            SET n:{type_name}
            RETURN labels(n) as new_labels
        """

        if dry_run:
            print(f"  [DRY RUN] Would add label '{type_name}' to: {display_name}")
        else:
            try:
                result = g.query(query)
                new_labels = result.result_set[0][0] if result.result_set else []
                print(f"  ✓ Added '{type_name}' label to: {display_name}")
                print(f"    Labels: {current_labels} → {new_labels}")
                fixed_count += 1
            except Exception as e:
                print(f"  ✗ Error fixing {display_name}: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    if dry_run:
        print(f"\n[DRY RUN] Would fix {len(nodes_to_fix)} nodes")
    else:
        print(f"\n✅ Fixed {fixed_count} nodes")
        print(f"   Failed: {len(nodes_to_fix) - fixed_count}")

        # Verify
        result = g.query("""
            MATCH (n:ProtocolNode)
            WHERE n.type_name IS NOT NULL
            WITH n, [label IN labels(n) WHERE label <> 'ProtocolNode'] as other_labels
            WHERE size(other_labels) = 0
            RETURN count(n) as remaining
        """)

        remaining = result.result_set[0][0]
        print(f"\n   Remaining nodes with missing labels: {remaining}")


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    fix_missing_labels(dry_run=dry_run)
