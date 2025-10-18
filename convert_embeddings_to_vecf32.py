"""Convert all embeddings from list format to vecf32 format."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

def convert_embeddings(graph_name: str):
    print(f"\n{'='*60}")
    print(f"Graph: {graph_name}")
    print(f"{'='*60}")

    gs = FalkorDBGraphStore(
        graph_name=graph_name,
        url="redis://localhost:6379"
    )

    # Get all nodes with embeddings
    nodes_result = gs.query("""
        MATCH (n:Node)
        WHERE n.embedding IS NOT NULL
        RETURN id(n) AS node_id, n.name AS name, n.embedding AS embedding
    """)

    print(f"Found {len(nodes_result)} nodes with embeddings")

    # Convert each embedding to vecf32 format
    converted_count = 0
    for row in nodes_result:
        node_id = row[0]
        name = row[1]
        embedding = row[2]  # This is a Python list

        # Convert list to vecf32 format by updating the node
        # We need to build the Cypher query with the vecf32 call directly
        embedding_str = str(embedding)
        
        try:
            gs.query(f"""
                MATCH (n) WHERE id(n) = {node_id}
                SET n.embedding = vecf32({embedding_str})
            """)
            converted_count += 1
            if converted_count % 5 == 0:
                print(f"  Converted {converted_count} embeddings...")
        except Exception as e:
            print(f"  [ERROR] Failed to convert {name}: {e}")

    print(f"[OK] Converted {converted_count} embeddings to vecf32 format")

    # Check index stats after conversion
    print("\nChecking index stats...")
    indices = gs.query("CALL db.indexes()")
    for idx in indices:
        if 'embedding' in str(idx[1]):
            stats = idx[8]  # Index stats are in position 8
            print(f"  numDocuments: {stats.get('numDocuments', 'N/A')}")

convert_embeddings("citizen_Luca")
convert_embeddings("collective_n2")
convert_embeddings("ecosystem_n3")

print(f"\n{'='*60}")
print("Embedding Conversion Complete")
print(f"{'='*60}")
