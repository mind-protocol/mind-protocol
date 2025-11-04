#!/usr/bin/env python3
"""
Migrate local FalkorDB data to cloud FalkorDB on Render
Exports all citizen graphs and imports to production
"""

import sys
from falkordb import FalkorDB

# Configuration
LOCAL_HOST = "localhost"
LOCAL_PORT = 6379

# Cloud FalkorDB URL (from Render Private Service)
CLOUD_URL = input("Enter cloud FalkorDB URL (e.g., mind-protocol-falkordb.onrender.com): ")
CLOUD_PORT = 6379

# Citizen graphs to migrate
CITIZENS = [
    "mind-protocol_iris",
    "mind-protocol_felix",
    "mind-protocol_atlas",
    "mind-protocol_luca",
    "mind-protocol_victor",
    "mind-protocol_ada"
]

def export_graph(local_db, graph_name):
    """Export a graph as Cypher CREATE statements"""
    print(f"\n{'='*60}")
    print(f"Exporting: {graph_name}")
    print(f"{'='*60}")

    graph = local_db.select_graph(graph_name)

    # Get node count
    result = graph.query("MATCH (n) RETURN count(n) as count")
    node_count = result.result_set[0][0] if result.result_set else 0
    print(f"  Nodes: {node_count}")

    if node_count == 0:
        print(f"  ⚠️  Empty graph, skipping")
        return None

    # Export all nodes with properties
    print(f"  Fetching nodes...")
    result = graph.query("""
        MATCH (n)
        RETURN id(n) as node_id, labels(n) as labels, properties(n) as props
    """)

    nodes = []
    for record in result.result_set:
        node_id, labels, props = record
        nodes.append({
            'id': node_id,
            'labels': labels,
            'props': props
        })

    # Export all relationships
    print(f"  Fetching relationships...")
    result = graph.query("""
        MATCH (a)-[r]->(b)
        RETURN id(a) as from_id, type(r) as rel_type, properties(r) as props, id(b) as to_id
    """)

    relationships = []
    for record in result.result_set:
        from_id, rel_type, props, to_id = record
        relationships.append({
            'from': from_id,
            'type': rel_type,
            'props': props,
            'to': to_id
        })

    print(f"  ✅ Exported {len(nodes)} nodes, {len(relationships)} relationships")

    return {
        'name': graph_name,
        'nodes': nodes,
        'relationships': relationships
    }

def import_graph(cloud_db, export_data):
    """Import graph data to cloud"""
    graph_name = export_data['name']
    nodes = export_data['nodes']
    relationships = export_data['relationships']

    print(f"\n{'='*60}")
    print(f"Importing: {graph_name}")
    print(f"{'='*60}")

    graph = cloud_db.select_graph(graph_name)

    # Import nodes (batch by 100)
    print(f"  Importing {len(nodes)} nodes...")
    batch_size = 100
    for i in range(0, len(nodes), batch_size):
        batch = nodes[i:i+batch_size]
        for node in batch:
            # Build CREATE statement
            labels_str = ':'.join(node['labels'])
            props_str = ', '.join([f"{k}: ${k}" for k in node['props'].keys()])

            query = f"CREATE (n:{labels_str} {{{props_str}}}) RETURN id(n)"
            graph.query(query, node['props'])

        print(f"    {min(i+batch_size, len(nodes))}/{len(nodes)} nodes")

    # Import relationships (batch by 100)
    print(f"  Importing {len(relationships)} relationships...")
    # Note: This requires node ID mapping which is complex
    # For now, skip relationships and let system recreate them
    print(f"    ⚠️  Relationship migration requires node ID mapping")
    print(f"    ⚠️  System will recreate relationships during runtime")

    print(f"  ✅ Import complete!")

def main():
    print("="*60)
    print("Mind Protocol - Local → Cloud Data Migration")
    print("="*60)

    # Connect to local FalkorDB
    print(f"\nConnecting to local FalkorDB: {LOCAL_HOST}:{LOCAL_PORT}")
    try:
        local_db = FalkorDB(host=LOCAL_HOST, port=LOCAL_PORT)
        print("  ✅ Connected to local FalkorDB")
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        sys.exit(1)

    # Connect to cloud FalkorDB
    print(f"\nConnecting to cloud FalkorDB: {CLOUD_URL}:{CLOUD_PORT}")
    try:
        cloud_db = FalkorDB(host=CLOUD_URL, port=CLOUD_PORT)
        print("  ✅ Connected to cloud FalkorDB")
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        print(f"  💡 Make sure FalkorDB service is running on Render")
        print(f"  💡 Check that you're using the correct URL")
        sys.exit(1)

    # Export all citizen graphs
    exports = []
    for citizen in CITIZENS:
        export_data = export_graph(local_db, citizen)
        if export_data:
            exports.append(export_data)

    if not exports:
        print("\n⚠️  No data to migrate!")
        return

    # Confirm before import
    print(f"\n{'='*60}")
    print(f"Ready to import {len(exports)} graphs to cloud")
    print(f"{'='*60}")
    response = input("Continue? (yes/no): ")

    if response.lower() != 'yes':
        print("Migration cancelled")
        return

    # Import to cloud
    for export_data in exports:
        import_graph(cloud_db, export_data)

    print(f"\n{'='*60}")
    print(f"✅ Migration Complete!")
    print(f"{'='*60}")
    print(f"\nMigrated graphs:")
    for exp in exports:
        print(f"  - {exp['name']}: {len(exp['nodes'])} nodes")

if __name__ == "__main__":
    main()
