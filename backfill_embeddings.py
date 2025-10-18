"""
Backfill Embeddings for Existing Nodes

This script generates embeddings for all nodes that were written by Phase 1
but lack semantic embeddings. This is the missing piece that blocks vector search.

Root Cause: Phase 1 Write Flux wrote nodes but didn't generate embeddings.
Fix: Generate embeddings for all existing nodes, then update Write Flux to
     generate embeddings going forward.

Designer: Felix (Engineer)
Date: 2025-10-17
Principle: Test Over Trust revealed this gap
"""

import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
from llama_index.graph_stores.falkordb import FalkorDBGraphStore

sys.path.insert(0, str(Path(__file__).parent))

# Configure LOCAL embedding model (no API key required)
# Using sentence-transformers directly for full control and zero dependencies
print("Loading local embedding model...")
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print(f"  Model loaded: all-MiniLM-L6-v2 ({embedding_model.get_sentence_embedding_dimension()} dimensions)")

GRAPHS = {
    "N1": "citizen_Luca",
    "N2": "collective_n2",
    "N3": "ecosystem_n3"
}

print("=" * 70)
print("BACKFILL EMBEDDINGS - Semantic Layer Completion")
print("=" * 70)
print("\nThis adds the missing semantic meaning to existing nodes.")
print("Phase 1 wrote facts. Now we add understanding.\n")

total_processed = 0
total_updated = 0

for level, graph_name in GRAPHS.items():
    print(f"\n[{level}] Processing graph: {graph_name}")
    print("-" * 70)

    try:
        # Connect to graph
        graph_store = FalkorDBGraphStore(
            graph_name=graph_name,
            url="redis://localhost:6379"
        )

        # Get all nodes without embeddings
        query = """
        MATCH (n)
        WHERE n.embedding IS NULL
        RETURN id(n) AS node_id, n.name AS name, n.description AS description
        """

        nodes = graph_store.query(query)
        print(f"  Nodes without embeddings: {len(nodes)}")

        if not nodes:
            print(f"  [OK] All nodes already have embeddings")
            continue

        # Generate embeddings for each node
        for node in nodes:
            node_id, name, description = node[0], node[1], node[2]

            try:
                # Create text for embedding: name + description
                text_to_embed = f"{name}: {description}" if description else name

                # Generate embedding using local model
                embedding = embedding_model.encode(text_to_embed).tolist()

                # Update node with embedding
                update_query = """
                MATCH (n)
                WHERE id(n) = $node_id
                SET n.embedding = $embedding
                """

                graph_store.query(update_query, params={
                    "node_id": node_id,
                    "embedding": embedding
                })

                total_updated += 1
                print(f"    [OK] {name} - embedding generated ({len(embedding)} dims)")

            except Exception as e:
                print(f"    [ERROR] {name} - failed: {e}")

            total_processed += 1

        print(f"  [{level}] Complete: {total_updated}/{total_processed} nodes updated")

    except Exception as e:
        print(f"  [ERROR] Failed to process {graph_name}: {e}")

print("\n" + "=" * 70)
print("BACKFILL COMPLETE")
print(f"  Total nodes processed: {total_processed}")
print(f"  Total embeddings generated: {total_updated}")
print("=" * 70)

if total_updated > 0:
    print("\n[SUCCESS] Semantic layer now complete.")
    print("Vector search should now work in Phase 3 retrieval.")
    print("\nNext steps:")
    print("  1. Re-run Phase 3 retrieval test")
    print("  2. Update Write Flux to generate embeddings for new nodes")
else:
    print("\n[INFO] No embeddings needed - all nodes already have semantic meaning.")
