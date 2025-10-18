"""Rebuild vector indices after adding :Node labels."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

def rebuild_index(graph_name: str):
    print(f"\n{'='*60}")
    print(f"Graph: {graph_name}")
    print(f"{'='*60}")

    gs = FalkorDBGraphStore(
        graph_name=graph_name,
        url="redis://localhost:6379"
    )

    # Drop existing vector index
    print("Dropping vector index...")
    try:
        gs.query("DROP INDEX ON :Node(embedding)")
        print("  [OK] Dropped vector index")
    except Exception as e:
        print(f"  [INFO] {e}")

    # Recreate vector index
    print("Creating vector index...")
    try:
        gs.query("CREATE VECTOR INDEX FOR (n:Node) ON (n.embedding) OPTIONS {dimension: 384, similarityFunction: 'cosine'}")
        print("  [OK] Created vector index")
    except Exception as e:
        print(f"  [ERROR] {e}")

    # Verify index
    indices = gs.query("CALL db.indexes()")
    print("Final indices:")
    for idx in indices:
        if idx[1] == ['embedding']:
            print(f"  - Label: {idx[0]}, Properties: {idx[1]}, Type: {idx[2]}")

rebuild_index("citizen_Luca")
rebuild_index("collective_n2")
rebuild_index("ecosystem_n3")

print(f"\n{'='*60}")
print("Index Rebuild Complete")
print(f"{'='*60}")
