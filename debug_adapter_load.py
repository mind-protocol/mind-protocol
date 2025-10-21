"""
Debug script to test FalkorDBAdapter.load_graph()

Tests why the adapter returns 0 nodes when the graph has 58 nodes.
"""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore
from orchestration.utils.falkordb_adapter import FalkorDBAdapter

# Connect to FalkorDB
print("Connecting to FalkorDB...")
graph_store = FalkorDBGraphStore(url="redis://localhost:6379")
adapter = FalkorDBAdapter(graph_store)

print("\nSwitching to citizen_felix database...")
graph_store.database = "citizen_felix"

# Try direct query
print("\nDirect query test:")
query = "MATCH (n) RETURN n LIMIT 5"
print(f"Query: {query}")
result = graph_store.query(query)

print(f"\nResult type: {type(result)}")
print(f"Result: {result}")

if result:
    print(f"Has result_set: {hasattr(result, 'result_set')}")

    # Inspect first node
    if len(result) > 0:
        first_row = result[0]
        first_node = first_row[0]
        print(f"\nFirst node type: {type(first_node)}")
        print(f"First node dir: {[x for x in dir(first_node) if not x.startswith('_')]}")
        print(f"First node properties: {first_node.properties if hasattr(first_node, 'properties') else 'NO PROPERTIES'}")
        print(f"First node id: {first_node.id if hasattr(first_node, 'id') else 'NO ID'}")
        print(f"First node alias: {first_node.alias if hasattr(first_node, 'alias') else 'NO ALIAS'}")
        print(f"First node labels: {first_node.labels if hasattr(first_node, 'labels') else 'NO LABELS'}")

# Try count query
print("\n\nCount query test:")
count_query = "MATCH (n) RETURN COUNT(n) as count"
print(f"Query: {count_query}")
count_result = graph_store.query(count_query)
print(f"Count result: {count_result}")
if count_result and hasattr(count_result, 'result_set'):
    print(f"Count from result_set: {count_result.result_set}")

# Now test the adapter
print("\n\nTesting adapter.load_graph():")
graph = adapter.load_graph("citizen_felix")
print(f"Loaded nodes: {len(graph.nodes)}")
print(f"Loaded links: {len(graph.links)}")
