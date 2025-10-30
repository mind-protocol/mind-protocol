"""
Cleanup Invalid Nodes - Remove nodes with types not in schema

Scans all graphs for nodes with invalid types (not in consciousness_schema.py)
and removes them.

Usage:
    python tools/cleanup_invalid_nodes.py --dry-run  # Show what would be deleted
    python tools/cleanup_invalid_nodes.py --delete   # Actually delete

Author: Iris "The Aperture"
Date: 2025-10-19
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis
import argparse
from substrate.schemas.consciousness_schema import NODE_TYPES

# Valid node type names
VALID_NODE_TYPES = {node_class.__name__ for node_class in NODE_TYPES}


def get_all_graphs():
    """Get list of all graphs in FalkorDB"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    return r.execute_command("GRAPH.LIST")


def find_invalid_nodes(graph_name: str):
    """Find all nodes with invalid types in a graph"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Query all nodes with their labels
    query = """
    MATCH (n)
    RETURN id(n) AS id, labels(n) AS labels, n.name AS name
    """

    result = r.execute_command('GRAPH.QUERY', graph_name, query)

    invalid_nodes = []

    if len(result[1]) > 0:
        for row in result[1]:
            node_id = row[0]
            labels_str = row[1]  # FalkorDB returns as string like "[Label]"
            node_name = row[2]

            # Parse label from string
            if labels_str == '[]':
                # No label
                invalid_nodes.append({
                    'id': node_id,
                    'name': node_name,
                    'type': None,
                    'reason': 'No type label'
                })
            else:
                # Extract label from "[Label]" format
                label = labels_str.strip('[]')
                if label not in VALID_NODE_TYPES:
                    invalid_nodes.append({
                        'id': node_id,
                        'name': node_name,
                        'type': label,
                        'reason': f'Invalid type: {label}'
                    })

    return invalid_nodes


def delete_node(graph_name: str, node_id: int):
    """Delete a node by internal ID"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Delete node and all its relationships
    query = f"""
    MATCH (n)
    WHERE id(n) = {node_id}
    DETACH DELETE n
    """

    r.execute_command('GRAPH.QUERY', graph_name, query)


def main():
    parser = argparse.ArgumentParser(description='Cleanup invalid nodes from FalkorDB graphs')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without deleting')
    parser.add_argument('--delete', action='store_true', help='Actually delete invalid nodes')
    parser.add_argument('--graph', type=str, help='Only process this graph (default: all graphs)')

    args = parser.parse_args()

    if not args.dry_run and not args.delete:
        print("ERROR: Must specify either --dry-run or --delete")
        return

    # Get graphs to process
    if args.graph:
        graphs = [args.graph]
    else:
        graphs = get_all_graphs()
        # Skip schema_registry (contains schema metadata, not consciousness nodes)
        graphs = [g for g in graphs if g != 'schema_registry']

    print(f"Valid node types: {len(VALID_NODE_TYPES)}")
    print(f"Graphs to check: {len(graphs)}")
    print()

    total_invalid = 0

    for graph_name in graphs:
        print(f"Checking {graph_name}...")

        invalid_nodes = find_invalid_nodes(graph_name)

        if invalid_nodes:
            total_invalid += len(invalid_nodes)
            print(f"  Found {len(invalid_nodes)} invalid nodes:")

            for node in invalid_nodes:
                print(f"    ID {node['id']}: name='{node['name']}', {node['reason']}")

            if args.delete:
                print(f"  Deleting {len(invalid_nodes)} nodes...")
                for node in invalid_nodes:
                    delete_node(graph_name, node['id'])
                print(f"  DELETED {len(invalid_nodes)} nodes")
            else:
                print(f"  (Dry run - would delete {len(invalid_nodes)} nodes)")
        else:
            print(f"  OK - No invalid nodes")

        print()

    print(f"Summary: Found {total_invalid} invalid nodes total")

    if args.dry_run:
        print()
        print("Run with --delete to actually remove these nodes")


if __name__ == "__main__":
    main()
