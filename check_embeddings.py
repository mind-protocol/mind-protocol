"""Check if ingested nodes have embeddings."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

for graph_name in ["citizen_Luca", "collective_n2", "ecosystem_n3"]:
    print(f"\n[{graph_name}]")

    try:
        gs = FalkorDBGraphStore(
            graph_name=graph_name,
            url="redis://localhost:6379"
        )

        # Check for embedding property
        result = gs.query("MATCH (n) RETURN n.name AS name, n.embedding IS NOT NULL AS has_embedding LIMIT 5")

        print(f"  Nodes checked: {len(result)}")
        for row in result:
            name, has_emb = row[0], row[1]
            status = "HAS" if has_emb else "MISSING"
            print(f"    {name}: {status} embedding")

    except Exception as e:
        print(f"  Error: {e}")
