#!/usr/bin/env python3
"""
Migrate all nodes to have id property based on their name.

For nodes with id=None or missing id, sets:
  id = "{lowercase_label}:{name}"

Example: Best_Practice node with name "foo" gets id "best_practice:foo"
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from falkordb import FalkorDB
from typing import List, Tuple


def get_all_graphs(db: FalkorDB) -> List[str]:
    """Get list of all graph names."""
    result = db.list_graphs()
    return result if result else []


def migrate_graph_node_ids(db: FalkorDB, graph_name: str) -> Tuple[int, int]:
    """
    Migrate all nodes in a graph to have id property.

    Returns: (nodes_updated, nodes_failed)
    """
    graph = db.select_graph(graph_name)

    # Get all node labels
    labels_result = graph.query("CALL db.labels()")
    labels = [row[0].decode('utf-8') if isinstance(row[0], bytes) else str(row[0])
              for row in labels_result.result_set]

    print(f"\n[{graph_name}] Found {len(labels)} node types")

    nodes_updated = 0
    nodes_failed = 0

    for label in labels:
        print(f"  Processing {label}...")

        # Find nodes with missing/null id
        query = f"""
        MATCH (n:{label})
        WHERE n.id IS NULL OR n.id = ''
        RETURN n.name AS name, id(n) AS internal_id
        """

        try:
            result = graph.query(query)

            if not result.result_set:
                print(f"    ✓ All {label} nodes have IDs")
                continue

            # Update each node
            for row in result.result_set:
                name = row[0]
                internal_id = row[1]

                if not name:
                    print(f"    ⚠ Skipping node {internal_id} - no name")
                    nodes_failed += 1
                    continue

                # Decode bytes if needed
                if isinstance(name, bytes):
                    name = name.decode('utf-8')

                # Construct ID: lowercase_label:name
                # Convert "Best_Practice" -> "best_practice"
                label_lower = label.lower()
                node_id = f"{label_lower}:{name}"

                # Update node
                update_query = f"""
                MATCH (n:{label})
                WHERE id(n) = {internal_id}
                SET n.id = '{node_id}'
                RETURN n.id
                """

                try:
                    update_result = graph.query(update_query)
                    if update_result.result_set:
                        nodes_updated += 1
                        if nodes_updated % 100 == 0:
                            print(f"    Updated {nodes_updated} nodes...")
                    else:
                        print(f"    ✗ Failed to update node {internal_id}")
                        nodes_failed += 1
                except Exception as e:
                    print(f"    ✗ Error updating node {internal_id}: {e}")
                    nodes_failed += 1

            print(f"    ✓ Updated {len(result.result_set)} {label} nodes")

        except Exception as e:
            print(f"    ✗ Error querying {label}: {e}")
            nodes_failed += 1

    return nodes_updated, nodes_failed


def main():
    """Run migration across all graphs."""
    print("=" * 60)
    print("Node ID Migration: name -> id for all graphs")
    print("=" * 60)

    # Connect to FalkorDB
    try:
        db = FalkorDB(host='localhost', port=6379)
        print("✓ Connected to FalkorDB")
    except Exception as e:
        print(f"✗ Failed to connect to FalkorDB: {e}")
        sys.exit(1)

    # Get all graphs
    graphs = get_all_graphs(db)
    print(f"\nFound {len(graphs)} graphs:")
    for g in graphs:
        print(f"  - {g}")

    # Migrate each graph
    total_updated = 0
    total_failed = 0

    for graph_name in graphs:
        try:
            updated, failed = migrate_graph_node_ids(db, graph_name)
            total_updated += updated
            total_failed += failed
            print(f"[{graph_name}] ✓ Updated: {updated}, Failed: {failed}")
        except Exception as e:
            print(f"[{graph_name}] ✗ Migration failed: {e}")
            total_failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Migration Complete!")
    print(f"  Total nodes updated: {total_updated}")
    print(f"  Total failures: {total_failed}")
    print("=" * 60)

    if total_failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
