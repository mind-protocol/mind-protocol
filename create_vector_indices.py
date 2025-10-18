"""Create proper vector indices for FalkorDB vector search."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

def create_vector_index(graph_name: str):
    """Create vector index on embedding property."""
    print(f"\n{'='*60}")
    print(f"Creating vector index for: {graph_name}")
    print(f"{'='*60}")

    try:
        gs = FalkorDBGraphStore(
            graph_name=graph_name,
            url="redis://localhost:6379"
        )

        # First, check current state
        print("Current indices:")
        indices = gs.query("CALL db.indexes()")
        for idx in indices:
            print(f"  - Label: {idx[0]}, Properties: {idx[1]}, Type: {idx[2]}")

        # Drop existing range index on embedding if it exists
        print("\nDropping existing range index on embedding...")
        try:
            gs.query("DROP INDEX ON :Node(embedding)")
            print("  [OK] Dropped range index")
        except Exception as e:
            print(f"  [INFO] {e}")

        # Create vector index
        # FalkorDB vector index syntax requires dimension and similarityFunction
        print("\nCreating vector index (384 dimensions, cosine similarity)...")
        try:
            gs.query("CREATE VECTOR INDEX FOR (n:Node) ON (n.embedding) OPTIONS {dimension: 384, similarityFunction: 'cosine'}")
            print("  [OK] Created vector index on Node.embedding")
        except Exception as e:
            print(f"  [ERROR] Failed to create vector index: {e}")

        # Verify new indices
        print("\nFinal indices:")
        indices = gs.query("CALL db.indexes()")
        for idx in indices:
            print(f"  - Label: {idx[0]}, Properties: {idx[1]}, Type: {idx[2]}")

    except Exception as e:
        print(f"  [ERROR] {e}")

# Create vector indices for all three graphs
create_vector_index("citizen_Luca")
create_vector_index("collective_n2")
create_vector_index("ecosystem_n3")

print(f"\n{'='*60}")
print("Vector Index Creation Complete")
print(f"{'='*60}")
