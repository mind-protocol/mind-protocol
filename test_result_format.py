"""Test what format FalkorDB returns."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
query_embedding = model.encode("V2 architecture").tolist()

gs = FalkorDBGraphStore(
    graph_name="collective_n2",
    url="redis://localhost:6379"
)

result = gs.query(f"""
    CALL db.idx.vector.queryNodes(
        'Node',
        'embedding',
        3,
        vecf32({str(query_embedding)})
    ) YIELD node, score
    RETURN
        id(node) AS node_id,
        node.name AS name,
        node.description AS description,
        score
    LIMIT 3
""")

print(f"Result type: {type(result)}")
print(f"Result length: {len(result)}")
print(f"\nFirst result:")
print(f"  Type: {type(result[0])}")
print(f"  Content: {result[0]}")
print(f"\nHow to access fields:")
print(f"  result[0][0] (node_id): {result[0][0]}")
print(f"  result[0][1] (name): {result[0][1]}")
print(f"  result[0][2] (description): {result[0][2]}")
print(f"  result[0][3] (score): {result[0][3]}")
