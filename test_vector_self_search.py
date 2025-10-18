"""Test vector search by searching for a node's own embedding."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

gs = FalkorDBGraphStore(
    graph_name="collective_n2",
    url="redis://localhost:6379"
)

# Get a node and its embedding
print("Fetching a sample node...")
node_result = gs.query("""
    MATCH (n:Node)
    WHERE n.embedding IS NOT NULL
    RETURN n.name AS name, n.embedding AS embedding
    LIMIT 1
""")

if node_result:
    node_name = node_result[0][0]
    node_embedding = node_result[0][1]
    
    print(f"Node: {node_name}")
    print(f"Embedding type: {type(node_embedding)}")
    print(f"Embedding length: {len(node_embedding) if hasattr(node_embedding, '__len__') else 'N/A'}")
    print(f"First 5 values: {node_embedding[:5] if hasattr(node_embedding, '__getitem__') else node_embedding}")
    
    # Try to search using this exact embedding
    print("\nSearching for this node using its own embedding...")
    
    # Test with different embedding formats
    # Format 1: Direct list
    try:
        result = gs.query(f"""
            CALL db.idx.vector.queryNodes(
                'Node',
                'embedding',
                5,
                {node_embedding}
            ) YIELD node, score
            RETURN node.name AS name, score
            LIMIT 5
        """)
        print(f"[Test 1] Direct embedding: {len(result)} results")
        for r in result:
            print(f"  - {r[0]}: {r[1]}")
    except Exception as e:
        print(f"[Test 1] Direct embedding FAILED: {e}")
    
    # Format 2: With vecf32()
    try:
        embedding_str = str(node_embedding).replace("'", "")  # Remove quotes if any
        result = gs.query(f"""
            CALL db.idx.vector.queryNodes(
                'Node',
                'embedding',
                5,
                vecf32({embedding_str})
            ) YIELD node, score
            RETURN node.name AS name, score
            LIMIT 5
        """)
        print(f"\n[Test 2] vecf32(embedding): {len(result)} results")
        for r in result:
            print(f"  - {r[0]}: {r[1]}")
    except Exception as e:
        print(f"\n[Test 2] vecf32(embedding) FAILED: {e}")
else:
    print("No nodes found!")
