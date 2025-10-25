"""Diagnose duplicate IDs in citizen_felix."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

graph_store = FalkorDBGraphStore(
    database='citizen_felix',
    url='redis://localhost:6379'
)

print("="*60)
print("Diagnosing duplicate IDs in citizen_felix")
print("="*60)

# Find duplicate IDs
dup_query = """
MATCH (n)
WITH n.id AS id, collect(n) AS nodes, count(n) AS count
WHERE count > 1
RETURN id, count
ORDER BY count DESC
"""

result = graph_store.query(dup_query)

if not result:
    print("No duplicates found")
    sys.exit(0)

print(f"\nFound {len(result)} duplicate IDs\n")

for row in result:
    dup_id = row[0]
    dup_count = row[1]

    print(f"\n{'='*60}")
    print(f"ID: {dup_id} ({dup_count} nodes)")
    print(f"{'='*60}")

    # Get all nodes with this ID
    node_query = f"""
    MATCH (n {{id: '{dup_id}'}})
    RETURN labels(n) AS labels, keys(n) AS props, properties(n) AS all_props
    """

    nodes = graph_store.query(node_query)

    for i, node in enumerate(nodes):
        labels = node[0]
        props_keys = node[1]
        all_props = node[2]

        print(f"\nNode {i+1}:")
        print(f"  Labels: {labels}")
        print(f"  Properties:")
        for key in sorted(props_keys):
            value = all_props.get(key, '<missing>')
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"    {key}: {value}")
