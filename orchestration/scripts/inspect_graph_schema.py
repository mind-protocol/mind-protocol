"""
Inspect FalkorDB graph schema to understand node property names.

Author: Felix - 2025-10-23
Purpose: Determine actual property names used in nodes
"""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore


def inspect_graph_schema(graph_name: str, host: str = "localhost", port: int = 6379):
    """
    Inspect a graph to see actual node and link properties.

    Args:
        graph_name: Name of the graph to inspect
        host: Redis host
        port: Redis port
    """
    print(f"\n{'='*70}")
    print(f"Inspecting graph: {graph_name}")
    print(f"{'='*70}\n")

    try:
        graph_store = FalkorDBGraphStore(
            database=graph_name,
            url=f"redis://{host}:{port}"
        )

        # Get sample nodes
        query = "MATCH (n) RETURN n LIMIT 5"
        result = graph_store.query(query)

        if result:
            print(f"Sample Nodes ({len(result)} shown):\n")
            for i, row in enumerate(result[:5]):
                node = row[0]
                print(f"Node {i+1}:")
                if hasattr(node, 'properties'):
                    print(f"  Properties: {node.properties}")
                if hasattr(node, 'labels'):
                    print(f"  Labels: {node.labels}")
                if hasattr(node, 'id'):
                    print(f"  Internal ID: {node.id}")
                print()

        # Get sample links with endpoints
        query = "MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 5"
        result = graph_store.query(query)

        if result:
            print(f"\nSample Links ({len(result)} shown):\n")
            for i, row in enumerate(result[:5]):
                src_node = row[0]
                link = row[1]
                tgt_node = row[2]

                print(f"Link {i+1}:")
                print(f"  Source properties: {src_node.properties if hasattr(src_node, 'properties') else 'N/A'}")
                print(f"  Link type: {link.relationship if hasattr(link, 'relationship') else 'N/A'}")
                print(f"  Link properties: {link.properties if hasattr(link, 'properties') else 'N/A'}")
                print(f"  Target properties: {tgt_node.properties if hasattr(tgt_node, 'properties') else 'N/A'}")
                print()

        # Get all node labels
        query = "MATCH (n) RETURN DISTINCT labels(n) LIMIT 20"
        result = graph_store.query(query)

        if result:
            print(f"\nNode Labels in Graph:\n")
            for row in result:
                print(f"  {row[0]}")

        # Get all relationship types
        query = "MATCH ()-[r]->() RETURN DISTINCT type(r) LIMIT 20"
        result = graph_store.query(query)

        if result:
            print(f"\nRelationship Types in Graph:\n")
            for row in result:
                print(f"  {row[0]}")

    except Exception as e:
        print(f"❌ Error inspecting {graph_name}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add orchestration to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from orchestration.adapters.ws.websocket_server import discover_graphs

    # Get graph from args or use first discovered N1 graph
    if len(sys.argv) > 1:
        graph = sys.argv[1]
    else:
        graphs_dict = discover_graphs(host='localhost', port=6379)
        citizen_graphs = graphs_dict.get('n1_graphs', [])
        if not citizen_graphs:
            print("No citizen graphs found in FalkorDB")
            sys.exit(1)
        graph = citizen_graphs[0]
        print(f"No graph specified, using first discovered: {graph}\n")

    # Inspect the selected graph
    inspect_graph_schema(graph)
