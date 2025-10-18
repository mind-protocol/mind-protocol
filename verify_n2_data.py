"""
Verify N2 collective graph has data.
"""

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

# Connect to collective_n2 graph
graph_store = FalkorDBGraphStore(
    graph_name="collective_n2",
    url="redis://localhost:6379"
)

print("=" * 60)
print("VERIFYING N2 COLLECTIVE GRAPH DATA")
print("=" * 60)

# Query nodes
print("\n[NODES]")
try:
    node_result = graph_store.query("MATCH (n) RETURN n.name AS name, labels(n)[0] AS type")
    print(f"Total nodes: {len(node_result)}")
    # FalkorDB returns list of lists, not list of dicts
    for record in node_result:
        if isinstance(record, (list, tuple)) and len(record) >= 2:
            print(f"  - {record[0]} ({record[1]})")
        else:
            print(f"  - {record}")
except Exception as e:
    print(f"Error querying nodes: {e}")

# Query relations
print("\n[RELATIONS]")
try:
    rel_result = graph_store.query("""
        MATCH (s)-[r]->(t)
        RETURN s.name AS source, type(r) AS rel_type, t.name AS target
    """)
    print(f"Total relations: {len(rel_result)}")
    # FalkorDB returns list of lists
    for record in rel_result:
        if isinstance(record, (list, tuple)) and len(record) >= 3:
            print(f"  - {record[0]} -[{record[1]}]-> {record[2]}")
        else:
            print(f"  - {record}")
except Exception as e:
    print(f"Error querying relations: {e}")

print("\n" + "=" * 60)
