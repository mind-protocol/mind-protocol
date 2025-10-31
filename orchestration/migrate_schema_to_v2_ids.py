"""
Schema migration: Add proper 'id' field to all nodes using Label:Name scheme.

Migrates from V1 schema (name-only) to V2 schema (proper id field).

Follows Nicolas's migration strategy:
1. Backfill id using "Label:Name" scheme
2. Verify all nodes have unique IDs
3. Create index on id field

Author: Atlas
Created: 2025-10-25
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llama_index.graph_stores.falkordb import FalkorDBGraphStore


def migrate_citizen_graph(graph_id: str):
    """Migrate one citizen graph to V2 schema with proper id fields."""

    print(f"\n{'='*60}")
    print(f"Migrating graph: {graph_id}")
    print(f"{'='*60}")

    # Connect
    graph_store = FalkorDBGraphStore(
        database=graph_id,
        url='redis://localhost:6379'
    )

    # Step 1: Count nodes before migration
    print("\n[Step 1] Pre-migration assessment...")

    count_query = "MATCH (n) RETURN count(n) AS total"
    result = graph_store.query(count_query)
    total_nodes = result[0][0] if result else 0

    print(f"✓ Total nodes: {total_nodes}")

    # Check how many already have id
    has_id_query = "MATCH (n) WHERE n.id IS NOT NULL RETURN count(n) AS with_id"
    result = graph_store.query(has_id_query)
    nodes_with_id = result[0][0] if result else 0

    print(f"✓ Nodes with id field: {nodes_with_id}")
    print(f"✓ Nodes needing migration: {total_nodes - nodes_with_id}")

    # Step 2a: Migrate standard nodes (have name field)
    print("\n[Step 2a] Migrating standard nodes (Label:Name scheme)...")

    migration_query = """
    MATCH (n)
    WHERE n.id IS NULL AND n.name IS NOT NULL
    SET n.id = labels(n)[0] + ':' + n.name
    RETURN count(n) AS migrated
    """

    result = graph_store.query(migration_query)
    migrated_count = result[0][0] if result else 0

    print(f"✓ Migrated {migrated_count} standard nodes")

    # Step 2b: Migrate ConsciousnessState nodes (use citizen_id)
    print("\n[Step 2b] Migrating ConsciousnessState nodes...")

    cs_migration_query = """
    MATCH (n:ConsciousnessState)
    WHERE n.id IS NULL AND n.citizen_id IS NOT NULL
    SET n.id = 'ConsciousnessState:' + n.citizen_id
    RETURN count(n) AS migrated
    """

    result = graph_store.query(cs_migration_query)
    cs_migrated = result[0][0] if result else 0

    print(f"✓ Migrated {cs_migrated} ConsciousnessState nodes")

    # Step 2c: Migrate TestNode (assign unique id)
    print("\n[Step 2c] Migrating TestNode nodes...")

    test_migration_query = """
    MATCH (n:TestNode)
    WHERE n.id IS NULL
    SET n.id = 'TestNode:' + toString(id(n))
    RETURN count(n) AS migrated
    """

    result = graph_store.query(test_migration_query)
    test_migrated = result[0][0] if result else 0

    if test_migrated > 0:
        print(f"✓ Migrated {test_migrated} TestNode nodes")

    total_migrated = migrated_count + cs_migrated + test_migrated
    print(f"\nTotal migrated: {total_migrated}")

    if total_migrated != (total_nodes - nodes_with_id):
        print(f"⚠ Warning: Expected to migrate {total_nodes - nodes_with_id}, actually migrated {total_migrated}")

    # Step 3: Verify all nodes now have id
    print("\n[Step 3] Post-migration verification...")

    result = graph_store.query("MATCH (n) WHERE n.id IS NULL RETURN count(n)")
    nodes_without_id = result[0][0] if result else 0

    if nodes_without_id > 0:
        print(f"❌ FAIL: {nodes_without_id} nodes still missing id field")
        return False

    print("✓ All nodes have id field")

    # Step 4: Check for duplicate IDs
    print("\n[Step 4] Checking for duplicate IDs...")

    dup_query = """
    MATCH (n)
    WITH n.id AS id, count(n) AS count
    WHERE count > 1
    RETURN id, count
    ORDER BY count DESC
    LIMIT 10
    """

    result = graph_store.query(dup_query)

    if result and len(result) > 0:
        print(f"❌ FAIL: Found {len(result)} duplicate IDs:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} nodes")
        return False

    print("✓ All IDs are unique")

    # Step 5: Sample migrated nodes
    print("\n[Step 5] Sample of migrated nodes...")

    sample_query = """
    MATCH (n)
    RETURN labels(n)[0] AS label, n.name AS name, n.id AS id
    LIMIT 5
    """

    result = graph_store.query(sample_query)

    if result:
        for row in result:
            label = row[0]
            name = row[1]
            node_id = row[2]
            print(f"  - {label}:{name} → id={node_id}")

    # Step 6: Create index on id field
    print("\n[Step 6] Creating index on id field...")

    try:
        index_query = "CREATE INDEX FOR (n:Node) ON (n.id)"
        graph_store.query(index_query)
        print("✓ Index created successfully")
    except Exception as e:
        if "already indexed" in str(e).lower():
            print("✓ Index already exists")
        else:
            print(f"⚠ Index creation warning: {e}")

    print(f"\n{'='*60}")
    print(f"✅ Migration complete for {graph_id}")
    print(f"{'='*60}")

    return True


def main():
    """Migrate all citizen graphs using discovery service."""

    # Add orchestration to path for imports
    import os
    sys.path.insert(0, str(Path(__file__).parent))

    from orchestration.adapters.ws.websocket_server import discover_graphs

    # Use discovery service to find all citizen graphs
    graphs = discover_graphs(host='localhost', port=6379)
    citizens = graphs.get('n1_graphs', [])

    print("=" * 60)
    print("Schema Migration: V1 → V2 (Proper ID Fields)")
    print("=" * 60)

    if not citizens:
        print("\n⚠️  No citizen graphs found in FalkorDB")
        return True

    print(f"\nFound {len(citizens)} citizen graphs: {citizens}")
    print(f"Migrating {len(citizens)} citizen graphs...\n")

    results = {}

    for citizen_id in citizens:
        try:
            success = migrate_citizen_graph(citizen_id)
            results[citizen_id] = success
        except Exception as e:
            print(f"\n❌ Error migrating {citizen_id}: {e}")
            import traceback
            traceback.print_exc()
            results[citizen_id] = False

    # Final summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)

    for citizen_id, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{citizen_id}: {status}")

    total_success = sum(1 for s in results.values() if s)
    print(f"\n{total_success}/{len(citizens)} graphs migrated successfully")

    return all(results.values())


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
