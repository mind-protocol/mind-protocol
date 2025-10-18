"""Add generic :Node label to all nodes for vector search."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

def add_node_label(graph_name: str):
    print(f"\n{'='*60}")
    print(f"Graph: {graph_name}")
    print(f"{'='*60}")

    gs = FalkorDBGraphStore(
        graph_name=graph_name,
        url="redis://localhost:6379"
    )

    # Count nodes before
    before_result = gs.query("MATCH (n) RETURN COUNT(n) AS count")
    total_nodes = before_result[0][0]
    print(f"Total nodes: {total_nodes}")

    # Add :Node label to all nodes that don't have it
    print("Adding :Node label to all nodes...")
    result = gs.query("""
        MATCH (n)
        WHERE NOT 'Node' IN labels(n)
        SET n:Node
        RETURN COUNT(n) AS updated_count
    """)
    updated_count = result[0][0]
    print(f"  [OK] Added :Node label to {updated_count} nodes")

    # Verify
    verify_result = gs.query("""
        MATCH (n:Node)
        RETURN labels(n) AS labels, COUNT(n) AS count
    """)
    print(f"\nNodes with :Node label:")
    for row in verify_result:
        print(f"  {row[0]}: {row[1]} nodes")

add_node_label("citizen_Luca")
add_node_label("collective_n2")
add_node_label("ecosystem_n3")

print(f"\n{'='*60}")
print("Node Label Addition Complete")
print(f"{'='*60}")
