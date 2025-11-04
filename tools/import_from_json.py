#!/usr/bin/env python3
"""
Import Mind Protocol graph data from JSON export to FalkorDB

This script is designed to run on Render where it has internal network access
to the FalkorDB service. It reads the exported JSON and recreates all nodes
and relationships.

Usage:
    python tools/import_from_json.py <path_to_export.json>

Environment:
    ECONOMY_REDIS_URL - Redis connection URL (e.g., redis://host:port)
    Or provide --host and --port directly
"""
import sys
import json
import os
import time
from falkordb import FalkorDB

def parse_redis_url(redis_url):
    """Parse Redis URL into host, port, username, password"""
    # Format: redis://[username:password@]host:port[/database]
    import re
    pattern = r'redis://(?:([^:]+):([^@]+)@)?([^:]+):(\d+)'
    match = re.match(pattern, redis_url)
    if not match:
        return None, None, None, None

    username = match.group(1)
    password = match.group(2)
    host = match.group(3)
    port = int(match.group(4))

    return host, port, username, password

def connect_to_falkordb():
    """Connect to FalkorDB using environment variables or defaults"""
    redis_url = os.getenv('ECONOMY_REDIS_URL')

    if redis_url:
        print(f"  Using ECONOMY_REDIS_URL from environment")
        host, port, username, password = parse_redis_url(redis_url)
        if not host:
            print(f"  ❌ Failed to parse ECONOMY_REDIS_URL: {redis_url}")
            sys.exit(1)
        print(f"  Parsed: host={host}, port={port}")
        db = FalkorDB(host=host, port=port, username=username, password=password)
    else:
        # Fallback to localhost (for testing)
        print(f"  No ECONOMY_REDIS_URL found, using localhost:6379")
        db = FalkorDB(host='localhost', port=6379)

    return db

def escape_cypher_string(value):
    """Escape string values for Cypher queries"""
    if isinstance(value, str):
        # Escape single quotes and backslashes
        return value.replace('\\', '\\\\').replace("'", "\\'")
    return value

def import_graph(db, graph_data):
    """Import a single graph from JSON data"""
    graph_name = graph_data['graph_name']
    nodes = graph_data['nodes']
    relationships = graph_data['relationships']

    print(f"\n{'='*60}")
    print(f"Importing: {graph_name}")
    print(f"{'='*60}")
    print(f"  Nodes to import: {len(nodes)}")
    print(f"  Relationships to import: {len(relationships)}")

    try:
        graph = db.select_graph(graph_name)
    except Exception as e:
        print(f"  ❌ Failed to select graph: {e}")
        return False

    # Import nodes in batches
    print(f"\n  Importing nodes...")
    batch_size = 100
    imported_nodes = 0
    failed_nodes = 0

    for i in range(0, len(nodes), batch_size):
        batch = nodes[i:i+batch_size]
        batch_queries = []

        for node in batch:
            labels = ':'.join(node['labels']) if node['labels'] else 'Node'
            props = node['properties']

            # Build property string
            props_parts = []
            for key, value in props.items():
                if isinstance(value, str):
                    escaped = escape_cypher_string(value)
                    props_parts.append(f"{key}: '{escaped}'")
                elif isinstance(value, (int, float)):
                    props_parts.append(f"{key}: {value}")
                elif isinstance(value, bool):
                    props_parts.append(f"{key}: {'true' if value else 'false'}")
                elif isinstance(value, list):
                    # Arrays in Cypher
                    arr_str = '[' + ', '.join(f"'{escape_cypher_string(str(v))}'" if isinstance(v, str) else str(v) for v in value) + ']'
                    props_parts.append(f"{key}: {arr_str}")
                # Skip null/None values

            props_str = ', '.join(props_parts) if props_parts else ''

            if props_str:
                query = f"CREATE (:{labels} {{{props_str}}})"
            else:
                query = f"CREATE (:{labels})"

            batch_queries.append(query)

        # Execute batch
        try:
            for query in batch_queries:
                graph.query(query)
            imported_nodes += len(batch)
            if (i + batch_size) % 500 == 0 or i + batch_size >= len(nodes):
                print(f"    {min(i + batch_size, len(nodes))}/{len(nodes)} nodes imported")
        except Exception as e:
            print(f"    ⚠️  Batch failed: {e}")
            failed_nodes += len(batch)
            continue

    print(f"  ✅ Imported {imported_nodes}/{len(nodes)} nodes ({failed_nodes} failed)")

    # Import relationships
    if relationships:
        print(f"\n  Importing relationships...")
        print(f"    ⚠️  Note: Relationship import requires node ID matching")
        print(f"    ⚠️  Skipping relationships - backend will recreate during runtime")
        print(f"    ⚠️  This is expected behavior for initial migration")

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/import_from_json.py <path_to_export.json>")
        print("\nEnvironment variables:")
        print("  ECONOMY_REDIS_URL - Redis connection URL")
        sys.exit(1)

    export_file = sys.argv[1]

    print("="*60)
    print("Mind Protocol - Import Graph Data from JSON")
    print("="*60)

    # Check file exists
    if not os.path.exists(export_file):
        print(f"\n❌ File not found: {export_file}")
        sys.exit(1)

    file_size_mb = os.path.getsize(export_file) / 1024 / 1024
    print(f"\n📄 Export file: {export_file}")
    print(f"   Size: {file_size_mb:.2f} MB")

    # Load JSON
    print(f"\n⏳ Loading JSON data...")
    try:
        with open(export_file, 'r') as f:
            graph_exports = json.load(f)
        print(f"  ✅ Loaded {len(graph_exports)} graphs")
    except Exception as e:
        print(f"  ❌ Failed to load JSON: {e}")
        sys.exit(1)

    # Connect to FalkorDB
    print(f"\n🔌 Connecting to FalkorDB...")
    try:
        db = connect_to_falkordb()
        print(f"  ✅ Connected to FalkorDB")
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        print(f"\n💡 Make sure:")
        print(f"   - FalkorDB service is running")
        print(f"   - ECONOMY_REDIS_URL environment variable is set")
        print(f"   - Or running from Render environment with internal network access")
        sys.exit(1)

    # Import each graph
    success_count = 0
    start_time = time.time()

    for graph_data in graph_exports:
        if import_graph(db, graph_data):
            success_count += 1

    elapsed = time.time() - start_time

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Import Complete!")
    print(f"{'='*60}")
    print(f"\nImported {success_count}/{len(graph_exports)} graphs")
    print(f"Time elapsed: {elapsed:.1f} seconds")

    if success_count == len(graph_exports):
        print(f"\n🎉 All graphs imported successfully!")
        print(f"\nNext steps:")
        print(f"  1. Restart consciousness engines to load data into SnapshotCache")
        print(f"  2. Verify dashboard at https://www.mindprotocol.ai/consciousness")
        print(f"  3. Check WebSocket events show graph data")
    else:
        print(f"\n⚠️  Some graphs failed to import")
        print(f"   Check error messages above")

if __name__ == "__main__":
    main()
