#!/usr/bin/env python3
"""
Import Mind Protocol graph data to production FalkorDB via admin API

This script imports data using the admin API, avoiding the need for Render shell access.

Usage:
    python tools/import_via_admin_api.py <path_to_export.json.gz> <admin_api_key>
"""
import sys
import json
import gzip
import time
import requests
from typing import Dict, List, Any

ADMIN_API_URL = "https://engine.mindprotocol.ai/admin/query"

def escape_cypher_string(value: str) -> str:
    """Escape string values for Cypher queries"""
    return value.replace('\\', '\\\\').replace("'", "\\'")

def execute_query(api_key: str, graph_name: str, query: str) -> Dict[str, Any]:
    """Execute a Cypher query via admin API"""
    response = requests.post(
        ADMIN_API_URL,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key
        },
        json={
            "graph_name": graph_name,
            "query": query
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def build_node_query(node: Dict[str, Any]) -> str:
    """Build CREATE query for a single node"""
    labels = ':'.join(node['labels']) if node['labels'] else 'Node'
    props = node['properties']

    # Build property string
    props_parts = []
    for key, value in props.items():
        # Skip embeddings (too large for single query)
        if key == 'content_embedding':
            continue

        if isinstance(value, str):
            escaped = escape_cypher_string(value)
            # Truncate very long strings to avoid query size limits
            if len(escaped) > 1000:
                escaped = escaped[:1000] + "..."
            props_parts.append(f"{key}: '{escaped}'")
        elif isinstance(value, (int, float)):
            props_parts.append(f"{key}: {value}")
        elif isinstance(value, bool):
            props_parts.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, list) and key != 'content_embedding':
            # Arrays (skip if too large)
            if len(value) > 10:
                continue
            arr_str = '[' + ', '.join(
                f"'{escape_cypher_string(str(v))}'" if isinstance(v, str) else str(v)
                for v in value
            ) + ']'
            props_parts.append(f"{key}: {arr_str}")

    props_str = ', '.join(props_parts) if props_parts else ''

    if props_str:
        return f"CREATE (:{labels} {{{props_str}}})"
    else:
        return f"CREATE (:{labels})"

def build_relationship_query(rel: Dict[str, Any]) -> str:
    """Build CREATE query for a single relationship"""
    rel_type = rel['type']
    source_name = rel.get('source', {}).get('properties', {}).get('name')
    target_name = rel.get('target', {}).get('properties', {}).get('name')

    if not source_name or not target_name:
        return None

    props = rel.get('properties', {})

    # Build property string
    props_parts = []
    for key, value in props.items():
        if isinstance(value, str):
            escaped = escape_cypher_string(value)
            if len(escaped) > 500:
                escaped = escaped[:500] + "..."
            props_parts.append(f"{key}: '{escaped}'")
        elif isinstance(value, bool):
            props_parts.append(f"{key}: {str(value).lower()}")
        elif value is None:
            props_parts.append(f"{key}: null")
        elif isinstance(value, (int, float)):
            props_parts.append(f"{key}: {value}")

    props_str = '{' + ', '.join(props_parts) + '}' if props_parts else ''

    # Create relationship query
    query = f"""
    MATCH (a {{name: '{escape_cypher_string(source_name)}'}})
    MATCH (b {{name: '{escape_cypher_string(target_name)}'}})
    CREATE (a)-[r:{rel_type} {props_str}]->(b)
    """.strip()

    return query

def import_graph(api_key: str, graph_data: Dict[str, Any]) -> bool:
    """Import a single graph via admin API"""
    graph_name = graph_data['graph_name']
    nodes = graph_data['nodes']
    relationships = graph_data['relationships']

    print(f"\n{'='*60}")
    print(f"Importing: {graph_name}")
    print(f"{'='*60}")
    print(f"  Nodes to import: {len(nodes)}")
    print(f"  Relationships to import: {len(relationships)}")

    # Clear existing data first
    print(f"\n  Clearing existing data...")
    try:
        result = execute_query(api_key, graph_name, "MATCH (n) DETACH DELETE n")
        print(f"  ✅ Graph cleared")
    except Exception as e:
        print(f"  ⚠️  Clear failed (graph may be empty): {e}")

    # Import nodes in batches
    print(f"\n  Importing nodes...")
    batch_size = 20  # Bulk CREATE per query
    imported_nodes = 0
    failed_nodes = 0

    for i in range(0, len(nodes), batch_size):
        batch = nodes[i:i+batch_size]

        # Build bulk CREATE query
        node_parts = []
        for idx, node in enumerate(batch):
            labels = ':'.join(node['labels']) if node['labels'] else 'Node'
            props = node['properties']

            # Build minimal properties (skip embeddings, truncate long strings)
            props_parts = []
            for key, value in props.items():
                if key in ['content_embedding', 'embeddable_text']:
                    continue
                if isinstance(value, str):
                    escaped = escape_cypher_string(value[:200])  # Truncate to 200 chars
                    props_parts.append(f"{key}: '{escaped}'")
                elif isinstance(value, (int, float)):
                    props_parts.append(f"{key}: {value}")
                elif isinstance(value, bool):
                    props_parts.append(f"{key}: {'true' if value else 'false'}")

            props_str = ', '.join(props_parts) if props_parts else ''
            if props_str:
                node_parts.append(f"(n{idx}:{labels} {{{props_str}}})")
            else:
                node_parts.append(f"(n{idx}:{labels})")

        bulk_query = "CREATE " + ",\n  ".join(node_parts)

        try:
            execute_query(api_key, graph_name, bulk_query)
            imported_nodes += len(batch)
        except Exception as e:
            print(f"    ⚠️  Batch failed: {str(e)[:100]}")
            failed_nodes += len(batch)

        if (i + batch_size) % 200 == 0 or i + batch_size >= len(nodes):
            print(f"    {min(i + batch_size, len(nodes))}/{len(nodes)} nodes imported")

    print(f"  ✅ Imported {imported_nodes}/{len(nodes)} nodes ({failed_nodes} failed)")

    # Import relationships
    if relationships:
        print(f"\n  Importing relationships...")
        imported_rels = 0
        failed_rels = 0

        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i+batch_size]

            for rel in batch:
                try:
                    query = build_relationship_query(rel)
                    if query:
                        execute_query(api_key, graph_name, query)
                        imported_rels += 1
                except Exception as e:
                    failed_rels += 1

            if (i + batch_size) % 500 == 0 or i + batch_size >= len(relationships):
                print(f"    {min(i + batch_size, len(relationships))}/{len(relationships)} relationships imported")

        print(f"  ✅ Imported {imported_rels}/{len(relationships)} relationships ({failed_rels} failed)")

    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/import_via_admin_api.py <path_to_export.json.gz> <admin_api_key>")
        sys.exit(1)

    export_file = sys.argv[1]
    api_key = sys.argv[2]

    print("="*60)
    print("Mind Protocol - Import via Admin API")
    print("="*60)

    # Load JSON
    print(f"\n⏳ Loading {export_file}...")
    try:
        if export_file.endswith('.gz'):
            with gzip.open(export_file, 'rt') as f:
                graph_exports = json.load(f)
        else:
            with open(export_file, 'r') as f:
                graph_exports = json.load(f)
        print(f"  ✅ Loaded {len(graph_exports)} graphs")
    except Exception as e:
        print(f"  ❌ Failed to load: {e}")
        sys.exit(1)

    # Import each graph
    success_count = 0
    start_time = time.time()

    for graph_data in graph_exports:
        try:
            if import_graph(api_key, graph_data):
                success_count += 1
        except Exception as e:
            print(f"\n  ❌ Graph import failed: {e}")

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
        print(f"  1. Wait 30 seconds for engines to detect new data")
        print(f"  2. Check dashboard at https://www.mindprotocol.ai/consciousness")
        print(f"  3. Verify WebSocket events show graph data")

if __name__ == "__main__":
    main()
