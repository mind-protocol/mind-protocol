#!/usr/bin/env python3
"""
Simple Graph Migration: Drop consciousness-infrastructure prefix

Just renames graphs from:
  consciousness-infrastructure_mind-protocol_{citizen} → mind-protocol_{citizen}
  collective_n2 → mind-protocol_collective

Deletes empty/false graphs.
"""

import redis
import sys

# Simple migration map
RENAMES = {
    "consciousness-infrastructure_mind-protocol_felix": "mind-protocol_felix",
    "consciousness-infrastructure_mind-protocol_luca": "mind-protocol_luca",
    "consciousness-infrastructure_mind-protocol_atlas": "mind-protocol_atlas",
    "consciousness-infrastructure_mind-protocol_ada": "mind-protocol_ada",
    "consciousness-infrastructure_mind-protocol_iris": "mind-protocol_iris",
    "consciousness-infrastructure_mind-protocol_victor": "mind-protocol_victor",
    "consciousness-infrastructure_mind-protocol": "mind-protocol",  # Org base graph
    "consciousness-infrastructure": "ecosystem",  # L3 ecosystem graph
    # protocol and schema_registry stay as-is
}

DELETE = [
    "collective_n2",  # Delete L2 org graph
    "falkor",  # Empty
    "",  # Empty
]

def main():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    print("🔄 Simple Graph Migration")
    print("=" * 70)

    # Get current graphs
    graphs = r.execute_command('GRAPH.LIST')
    print(f"\nCurrent graphs: {len(graphs)}")

    # Renames
    print("\n1️⃣  Renaming graphs...")
    for old_name, new_name in RENAMES.items():
        if old_name in graphs:
            # FalkorDB stores graphs as Redis keys without prefix
            try:
                r.rename(old_name, new_name)
                print(f"   ✓ {old_name} → {new_name}")
            except Exception as e:
                print(f"   ✗ Failed: {old_name} → {e}")
        else:
            print(f"   ⊘ Skip: {old_name} (not found)")

    # Deletes
    print("\n2️⃣  Deleting empty/false graphs...")
    for graph_name in DELETE:
        if graph_name in graphs:
            try:
                r.execute_command('GRAPH.DELETE', graph_name)
                print(f"   ✓ Deleted: {graph_name}")
            except Exception as e:
                print(f"   ✗ Failed: {graph_name} → {e}")
        else:
            print(f"   ⊘ Skip: {graph_name} (not found)")

    # Verify
    print("\n3️⃣  Verification...")
    new_graphs = r.execute_command('GRAPH.LIST')
    print(f"   New graph count: {len(new_graphs)}")

    # Check for old names
    old_patterns = [g for g in new_graphs if 'consciousness-infrastructure' in g or g == 'collective_n2']
    if old_patterns:
        print(f"   ⚠️  Old names still present: {old_patterns}")
    else:
        print(f"   ✅ No old names found")

    print("\n" + "=" * 70)
    print("✅ Migration complete")
    print("\nNew graphs:")
    for g in sorted(new_graphs):
        print(f"   - {g}")

if __name__ == "__main__":
    confirm = input("This will rename graphs in FalkorDB. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        main()
    else:
        print("Aborted.")
        sys.exit(1)
