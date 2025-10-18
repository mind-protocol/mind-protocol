"""Check how embeddings are stored vs. how index expects them."""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

gs = FalkorDBGraphStore(
    graph_name="collective_n2",
    url="redis://localhost:6379"
)

# Get index details
print("Vector Index Details:")
indices = gs.query("CALL db.indexes()")
for idx in indices:
    if 'embedding' in str(idx[1]):
        print(f"  Label: {idx[0]}")
        print(f"  Property: {idx[1]}")
        print(f"  Type: {idx[2]}")
        print(f"  Full info: {idx}")
        print()

# Check how embeddings are stored
print("\nChecking embedding storage format...")
result = gs.query("""
    MATCH (n:Node)
    WHERE n.embedding IS NOT NULL
    RETURN n.name AS name, 
           TYPE(n.embedding) AS type,
           SIZE(n.embedding) AS size,
           n.embedding[0] AS first_value,
           n.embedding IS NOT NULL AS has_embedding
    LIMIT 3
""")

for row in result:
    print(f"Node: {row[0]}")
    print(f"  Type: {row[1]}")
    print(f"  Size: {row[2]}")
    print(f"  First value: {row[3]}")
    print(f"  Has embedding: {row[4]}")
    print()

# Try creating a test node with vecf32 format
print("Creating test node with vecf32 embedding...")
try:
    gs.query("""
        CREATE (t:TestNode {
            name: 'vector_test',
            embedding: vecf32([0.1, 0.2, 0.3, 0.4])
        })
    """)
    print("  [OK] Created test node")
    
    # Query it back
    test_result = gs.query("""
        MATCH (t:TestNode {name: 'vector_test'})
        RETURN TYPE(t.embedding) AS type, t.embedding AS embedding
    """)
    print(f"  Test node embedding type: {test_result[0][0]}")
    print(f"  Test node embedding: {test_result[0][1]}")
    
    # Clean up
    gs.query("MATCH (t:TestNode) DELETE t")
    print("  [OK] Cleaned up test node")
except Exception as e:
    print(f"  [ERROR] {e}")

# Check if there's a difference between regular array and vecf32 array
print("\nComparing array storage formats...")
result = gs.query("""
    MATCH (n:Node)
    WHERE n.embedding IS NOT NULL
    WITH n LIMIT 1
    RETURN n.embedding
""")
print(f"Embedding from database: {type(result[0][0])}")
print(f"First 3 values: {result[0][0][:3]}")
