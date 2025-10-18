"""Test FalkorDB vector query syntax."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore
from sentence_transformers import SentenceTransformer

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Generate query embedding
query = "V2 architecture"
query_embedding = model.encode(query).tolist()

print(f"Query: {query}")
print(f"Embedding dimensions: {len(query_embedding)}")

# Connect to graph
gs = FalkorDBGraphStore(
    graph_name="collective_n2",
    url="redis://localhost:6379"
)

# Test 1: Try with 'Node' label
print("\n[Test 1] Querying with label='Node'...")
try:
    result = gs.query(f"""
        CALL db.idx.vector.queryNodes(
            'Node',
            'embedding',
            5,
            vecf32({str(query_embedding)})
        ) YIELD node, score
        RETURN node.name AS name, score
        LIMIT 5
    """)
    print(f"  [OK] Retrieved {len(result)} results")
    for r in result:
        print(f"    - {r[0]}: {r[1]}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 2: Try with empty string label
print("\n[Test 2] Querying with label=''...")
try:
    result = gs.query(f"""
        CALL db.idx.vector.queryNodes(
            '',
            'embedding',
            5,
            vecf32({str(query_embedding)})
        ) YIELD node, score
        RETURN node.name AS name, score
        LIMIT 5
    """)
    print(f"  [OK] Retrieved {len(result)} results")
    for r in result:
        print(f"    - {r[0]}: {r[1]}")
except Exception as e:
    print(f"  [ERROR] {e}")

