"""Fix duplicate subentities in citizen_felix by removing newer duplicates."""

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
print("Fixing duplicate subentities in citizen_felix")
print("="*60)

# Strategy: Keep older node (has member_count), delete newer node (has name field)
# Older nodes are from bootstrap, have richer metrics

duplicate_ids = [
    'entity_citizen_felix_translator',
    'entity_citizen_felix_validator',
    'entity_citizen_felix_pragmatist',
    'entity_citizen_felix_architect'
]

for dup_id in duplicate_ids:
    print(f"\nProcessing: {dup_id}")

    # Delete the node that has 'name' field (newer version)
    delete_query = f"""
    MATCH (n {{id: '{dup_id}'}})
    WHERE n.name IS NOT NULL
    DELETE n
    RETURN count(n) AS deleted
    """

    result = graph_store.query(delete_query)
    deleted = result[0][0] if result else 0

    print(f"  ✓ Deleted {deleted} newer duplicate(s)")

# Verify no duplicates remain
print("\n" + "="*60)
print("Verification")
print("="*60)

dup_check_query = """
MATCH (n)
WITH n.id AS id, count(n) AS count
WHERE count > 1
RETURN id, count
"""

result = graph_store.query(dup_check_query)

if not result or len(result) == 0:
    print("✅ No duplicate IDs remain")
else:
    print(f"❌ Still have {len(result)} duplicate IDs:")
    for row in result:
        print(f"  - {row[0]}: {row[1]} nodes")

print("\nDone!")
