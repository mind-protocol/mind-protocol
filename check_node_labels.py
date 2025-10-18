"""Check what labels nodes actually have in FalkorDB."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

def check_labels(graph_name: str):
    print(f"\n{'='*60}")
    print(f"Graph: {graph_name}")
    print(f"{'='*60}")

    gs = FalkorDBGraphStore(
        graph_name=graph_name,
        url="redis://localhost:6379"
    )

    # Get all distinct labels
    labels_result = gs.query("""
        MATCH (n)
        RETURN DISTINCT labels(n) AS labels, COUNT(n) AS count
        ORDER BY count DESC
    """)

    print(f"Node labels found:")
    for row in labels_result:
        print(f"  {row[0]}: {row[1]} nodes")

    # Check if any nodes have embedding property
    embedding_result = gs.query("""
        MATCH (n)
        WHERE n.embedding IS NOT NULL
        RETURN labels(n) AS labels, COUNT(n) AS count
        ORDER BY count DESC
    """)

    print(f"\nNodes WITH embeddings:")
    for row in embedding_result:
        print(f"  {row[0]}: {row[1]} nodes")

    # Sample a few nodes
    sample_result = gs.query("""
        MATCH (n)
        WHERE n.embedding IS NOT NULL
        RETURN labels(n) AS labels, n.name AS name, SIZE(n.embedding) AS embedding_size
        LIMIT 5
    """)

    print(f"\nSample nodes:")
    for row in sample_result:
        print(f"  Labels: {row[0]}, Name: {row[1]}, Embedding size: {row[2]}")

check_labels("citizen_Luca")
check_labels("collective_n2")
check_labels("ecosystem_n3")
