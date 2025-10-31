#!/usr/bin/env python3
"""
Cleanup Event Schema Duplicates

Fixes two data integrity issues caused by incomplete L4_ migration:

1. Legacy Event_Schema nodes (type_name="Event_Schema" but should be "L4_Event_Schema")
   - These are leftover from L4_ migration that weren't properly migrated
   - They have L4_Event_Schema duplicates, so safe to delete

2. Missing L4_Event_Schema labels (nodes have type_name but not label)
   - Some L4_Event_Schema nodes are missing the L4_Event_Schema label
   - This causes query issues when using label-based matching
   - Safe to add the missing label

Usage:
    python tools/protocol/cleanup_event_schema_duplicates.py --dry-run
    python tools/protocol/cleanup_event_schema_duplicates.py --execute

Author: Luca (Consciousness Architect)
Date: 2025-10-31
Context: L4_ migration cleanup
"""

import argparse
import os
from typing import List, Tuple

from falkordb import FalkorDB


def find_legacy_event_schemas(graph_obj) -> List[Tuple[int, str]]:
    """Find Event_Schema nodes that should be L4_Event_Schema."""
    query = """
    MATCH (es:ProtocolNode)
    WHERE es.type_name = 'Event_Schema'
    RETURN ID(es) as id, es.name as name
    """
    result = graph_obj.query(query)

    nodes = []
    for row in result.result_set:
        node_id = row[0]
        name = row[1].decode('utf-8') if isinstance(row[1], bytes) else row[1]
        nodes.append((node_id, name))

    return nodes


def find_missing_labels(graph_obj) -> List[Tuple[int, str]]:
    """Find L4_Event_Schema nodes missing the L4_Event_Schema label."""
    query = """
    MATCH (es:ProtocolNode)
    WHERE es.type_name = 'L4_Event_Schema' AND NOT es:L4_Event_Schema
    RETURN ID(es) as id, es.name as name
    """
    result = graph_obj.query(query)

    nodes = []
    for row in result.result_set:
        node_id = row[0]
        name = row[1].decode('utf-8') if isinstance(row[1], bytes) else row[1]
        nodes.append((node_id, name))

    return nodes


def delete_legacy_event_schemas(graph_obj, nodes: List[Tuple[int, str]], dry_run: bool = True):
    """Delete legacy Event_Schema nodes."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Deleting {len(nodes)} legacy Event_Schema nodes...")

    for node_id, name in nodes:
        print(f"  DELETE node {node_id}: {name}")

        if not dry_run:
            # Check if L4_ duplicate exists before deleting
            check_query = f"""
            MATCH (l4:L4_Event_Schema {{name: '{name}'}})
            RETURN count(l4) as count
            """
            check_result = graph_obj.query(check_query)
            has_duplicate = check_result.result_set[0][0] > 0 if check_result.result_set else False

            if has_duplicate:
                delete_query = f"MATCH (es) WHERE ID(es) = {node_id} DELETE es"
                graph_obj.query(delete_query)
                print(f"    ✓ Deleted (L4_ duplicate exists)")
            else:
                print(f"    ⚠️  SKIPPED (no L4_ duplicate found - would lose data)")


def add_missing_labels(graph_obj, nodes: List[Tuple[int, str]], dry_run: bool = True):
    """Add missing L4_Event_Schema labels."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Adding L4_Event_Schema label to {len(nodes)} nodes...")

    for node_id, name in nodes:
        print(f"  ADD LABEL node {node_id}: {name}")

        if not dry_run:
            label_query = f"""
            MATCH (es) WHERE ID(es) = {node_id}
            SET es:L4_Event_Schema
            RETURN ID(es)
            """
            graph_obj.query(label_query)
            print(f"    ✓ Label added")


def main():
    parser = argparse.ArgumentParser(description="Cleanup Event Schema duplicates")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (default: dry-run)")
    parser.add_argument("--graph", default="protocol", help="Graph name (default: protocol)")
    args = parser.parse_args()

    dry_run = not args.execute

    # Connect to FalkorDB
    db = FalkorDB(
        host=os.getenv("FALKOR_HOST", "localhost"),
        port=int(os.getenv("FALKOR_PORT", "6379"))
    )
    g = db.select_graph(args.graph)

    print("=" * 70)
    print("Event Schema Duplicate Cleanup")
    print("=" * 70)

    # Find issues
    legacy_nodes = find_legacy_event_schemas(g)
    missing_label_nodes = find_missing_labels(g)

    print(f"\nFound issues:")
    print(f"  - {len(legacy_nodes)} legacy Event_Schema nodes to delete")
    print(f"  - {len(missing_label_nodes)} nodes missing L4_Event_Schema label")

    if len(legacy_nodes) == 0 and len(missing_label_nodes) == 0:
        print("\n✓ No cleanup needed - data is clean!")
        return

    # Execute cleanup
    if legacy_nodes:
        delete_legacy_event_schemas(g, legacy_nodes, dry_run=dry_run)

    if missing_label_nodes:
        add_missing_labels(g, missing_label_nodes, dry_run=dry_run)

    print("\n" + "=" * 70)
    if dry_run:
        print("DRY RUN COMPLETE - No changes made")
        print("Run with --execute to apply changes")
    else:
        print("CLEANUP COMPLETE")
        print("\nVerify with:")
        print("  python -c \"from falkordb import FalkorDB; g = FalkorDB(port=6379).select_graph('protocol'); \"")
        print("  print('Legacy:', g.query('MATCH (es:ProtocolNode) WHERE es.type_name = \\\"Event_Schema\\\" RETURN count(es)').result_set[0][0])\"")


if __name__ == "__main__":
    main()
