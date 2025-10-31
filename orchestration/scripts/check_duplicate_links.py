"""
Check for duplicate links in FalkorDB graphs.

Author: Felix - 2025-10-23
Purpose: Diagnostic tool to find duplicate links causing startup failures
"""

import redis
from llama_index.graph_stores.falkordb import FalkorDBGraphStore


def check_duplicates_in_graph(graph_name: str, host: str = "localhost", port: int = 6379):
    """
    Check for duplicate links in a FalkorDB graph.

    Args:
        graph_name: Name of the graph to check
        host: Redis host
        port: Redis port
    """
    print(f"\n{'='*70}")
    print(f"Checking graph: {graph_name}")
    print(f"{'='*70}\n")

    try:
        graph_store = FalkorDBGraphStore(
            database=graph_name,
            url=f"redis://{host}:{port}"
        )

        # Query to find duplicate links
        query = """
        MATCH (a)-[r]->(b)
        WITH a.id as src, b.id as dst, type(r) as rel_type, count(*) as link_count
        WHERE link_count > 1
        RETURN src, dst, rel_type, link_count
        ORDER BY link_count DESC
        LIMIT 20
        """

        result = graph_store.query(query)

        if not result or len(result) == 0:
            print(f"✅ No duplicate links found in {graph_name}")
            return []

        print(f"⚠️  Found {len(result)} sets of duplicate links:\n")

        duplicates = []
        for row in result:
            src = row[0]
            dst = row[1]
            rel_type = row[2]
            count = row[3]

            print(f"  Source: {src}")
            print(f"  Target: {dst}")
            print(f"  Type: {rel_type}")
            print(f"  Count: {count}")
            print(f"  " + "-"*60)

            duplicates.append({
                'src': src,
                'dst': dst,
                'rel_type': rel_type,
                'count': count
            })

        return duplicates

    except Exception as e:
        print(f"❌ Error checking {graph_name}: {e}")
        import traceback
        traceback.print_exc()
        return []


def remove_duplicate_links(graph_name: str, src: str, dst: str, rel_type: str, host: str = "localhost", port: int = 6379):
    """
    Remove duplicate links from a graph, keeping only the first instance.

    Args:
        graph_name: Name of the graph
        src: Source node ID
        dst: Target node ID
        rel_type: Relationship type
        host: Redis host
        port: Redis port
    """
    print(f"\n{'='*70}")
    print(f"Removing duplicates: {src} -[{rel_type}]-> {dst}")
    print(f"{'='*70}\n")

    try:
        graph_store = FalkorDBGraphStore(
            database=graph_name,
            url=f"redis://{host}:{port}"
        )

        # First, count how many exist
        count_query = f"""
        MATCH (a {{id: '{src}'}})-[r:{rel_type}]->(b {{id: '{dst}'}})
        RETURN count(r) as total
        """

        result = graph_store.query(count_query)
        total = result[0][0] if result else 0

        print(f"Found {total} instances of this link")

        if total <= 1:
            print("No duplicates to remove")
            return

        # Delete all but first
        delete_query = f"""
        MATCH (a {{id: '{src}'}})-[r:{rel_type}]->(b {{id: '{dst}'}})
        WITH a, b, collect(r) as rels
        FOREACH (rel in tail(rels) | DELETE rel)
        RETURN count(rels) as deleted
        """

        result = graph_store.query(delete_query)
        deleted = total - 1  # We keep the first one

        print(f"✅ Deleted {deleted} duplicate link(s), kept 1")

    except Exception as e:
        print(f"❌ Error removing duplicates: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add orchestration to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from orchestration.adapters.ws.websocket_server import discover_graphs

    # Use discovery service to find all graphs
    graphs_dict = discover_graphs(host='localhost', port=6379)
    graphs_to_check = graphs_dict.get('n1_graphs', []) + graphs_dict.get('n2_graphs', [])

    print("\n" + "="*70)
    print("FALKORDB DUPLICATE LINK CHECKER")
    print("="*70)
    print(f"Found {len(graphs_to_check)} graphs: {graphs_to_check}\n")

    all_duplicates = {}

    for graph_name in graphs_to_check:
        duplicates = check_duplicates_in_graph(graph_name)
        if duplicates:
            all_duplicates[graph_name] = duplicates

    if all_duplicates:
        print("\n" + "="*70)
        print("SUMMARY - Graphs with duplicates:")
        print("="*70)

        for graph_name, duplicates in all_duplicates.items():
            print(f"\n{graph_name}: {len(duplicates)} sets of duplicates")
            for dup in duplicates:
                print(f"  - {dup['src']} -[{dup['rel_type']}]-> {dup['dst']} (x{dup['count']})")

        print("\n" + "="*70)
        print("CLEANUP RECOMMENDED")
        print("="*70)
        print("\nTo remove duplicates, run:")
        print("  python orchestration/scripts/remove_duplicate_links.py")

    else:
        print("\n" + "="*70)
        print("✅ ALL GRAPHS CLEAN - No duplicates found")
        print("="*70)
