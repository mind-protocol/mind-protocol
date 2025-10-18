"""Check if vector indices exist in FalkorDB graphs."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

def check_indices(graph_name: str):
    """Check what indices exist in a graph."""
    print(f"\n{'='*60}")
    print(f"Checking indices for: {graph_name}")
    print(f"{'='*60}")

    try:
        gs = FalkorDBGraphStore(
            graph_name=graph_name,
            url="redis://localhost:6379"
        )

        # Query for all indices
        result = gs.query("CALL db.indexes()")

        if result:
            print(f"Found {len(result)} indices:")
            for idx in result:
                print(f"  - {idx}")
        else:
            print("  [NONE] No indices found")

    except Exception as e:
        print(f"  [ERROR] {e}")

# Check all three graphs
check_indices("citizen_Luca")
check_indices("collective_n2")
check_indices("ecosystem_n3")

print(f"\n{'='*60}")
print("Index Check Complete")
print(f"{'='*60}")
