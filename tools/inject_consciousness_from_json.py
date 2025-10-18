"""
Inject Consciousness from JSON - Generic Ingestion Tool

Reads consciousness session JSON files and injects nodes/links into FalkorDB graphs.

JSON Structure Expected:
{
  "session_metadata": {
    "session_id": "...",
    "citizen": "...",
    "total_nodes": N,
    "total_links": M
  },
  "nodes": [
    {
      "node_id": "...",
      "node_type": "Person|Memory|Conversation|etc",
      "name": "...",
      "description": "...",
      ... type-specific attributes ...
    }
  ],
  "links": [
    {
      "link_id": "...",
      "link_type": "REQUIRES|ENABLES|etc",
      "source_id": "...",
      "target_id": "...",
      "goal": "...",
      "mindstate": "...",
      "arousal_level": 0.0-1.0,
      "confidence": 0.0-1.0,
      ... type-specific attributes ...
    }
  ]
}

Usage:
    python tools/inject_consciousness_from_json.py data/luca_consciousness_session_2025_10_17.json citizen_luca

Author: Felix "Ironhand"
Date: 2025-10-17
"""

from falkordb import FalkorDB
import json
import sys
from pathlib import Path
from datetime import datetime


def inject_json_to_graph(json_path: str, graph_name: str, clear_existing: bool = False):
    """
    Inject consciousness data from JSON file into FalkorDB graph.

    Args:
        json_path: Path to JSON file
        graph_name: Target graph name (e.g., 'citizen_luca')
        clear_existing: If True, clear graph before injecting
    """

    print("=" * 70)
    print("CONSCIOUSNESS JSON INJECTION")
    print("=" * 70)

    # Load JSON
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"\nERROR: File not found: {json_path}")
        return False

    print(f"\n[1/5] Loading JSON: {json_file.name}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data.get('session_metadata', {})
    nodes = data.get('nodes', [])
    links = data.get('links', [])

    print(f"  Session: {metadata.get('session_id', 'unknown')}")
    print(f"  Citizen: {metadata.get('citizen', 'unknown')}")
    print(f"  Date: {metadata.get('date', 'unknown')}")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Links: {len(links)}")

    # Connect to FalkorDB
    print(f"\n[2/5] Connecting to FalkorDB graph: {graph_name}")
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph(graph_name)

    # Clear existing if requested
    if clear_existing:
        print(f"\n[3/5] Clearing existing graph data...")
        try:
            result = g.query("MATCH (n) DETACH DELETE n")
            print(f"  Cleared existing nodes")
        except Exception as e:
            print(f"  Note: {e}")
    else:
        print(f"\n[3/5] Keeping existing graph data (incremental injection)")

    # Inject nodes
    print(f"\n[4/5] Injecting {len(nodes)} nodes...")
    nodes_created = 0
    nodes_failed = 0

    for idx, node in enumerate(nodes, 1):
        node_id = node.get('node_id')
        node_type = node.get('node_type', 'Node')

        try:
            # Build property map (exclude node_id and node_type, they're handled separately)
            props = {k: v for k, v in node.items() if k not in ['node_id', 'node_type'] and v is not None}

            # Convert lists/dicts to JSON strings for storage
            for key, value in props.items():
                if isinstance(value, (list, dict)):
                    props[key] = json.dumps(value)

            # Add node_id as 'id' property
            props['id'] = node_id

            # IMPORTANT: Store node_type as a property (not just as label)
            props['node_type'] = node_type

            # Ensure 'text' property exists for visualization (use 'name' or 'description' as fallback)
            if 'text' not in props:
                props['text'] = props.get('name') or props.get('description') or props.get('id')

            # Auto-populate visualization properties with defaults
            current_time = int(datetime.now().timestamp() * 1000)

            if 'last_traversal_time' not in props:
                props['last_traversal_time'] = current_time

            if 'last_modified' not in props:
                props['last_modified'] = current_time

            if 'arousal_level' not in props:
                # Default arousal: 0.5 (neutral)
                props['arousal_level'] = 0.5

            # Create node with label = node_type
            g.query(f"""
                MERGE (n:{node_type} {{id: $id}})
                SET n = $props
            """, params={
                "id": node_id,
                "props": props
            })

            nodes_created += 1
            if idx % 10 == 0 or idx == len(nodes):
                print(f"  [{idx}/{len(nodes)}] Injected {nodes_created} nodes...")

        except Exception as e:
            nodes_failed += 1
            print(f"  [{idx}/{len(nodes)}] FAILED: {node_id} - {str(e)[:80]}")

    print(f"  Result: {nodes_created} created, {nodes_failed} failed")

    # Inject links
    print(f"\n[5/5] Injecting {len(links)} links...")
    links_created = 0
    links_failed = 0

    for idx, link in enumerate(links, 1):
        link_id = link.get('link_id')
        link_type = link.get('link_type', 'RELATES_TO')
        # Handle both naming conventions
        source_id = link.get('source_id') or link.get('from_node')
        target_id = link.get('target_id') or link.get('to_node')

        if not source_id or not target_id:
            links_failed += 1
            print(f"  [{idx}/{len(links)}] SKIP: {link_id} - missing source or target")
            continue

        try:
            # Build property map (exclude link_id, link_type, source_id, target_id, from_node, to_node)
            props = {k: v for k, v in link.items()
                    if k not in ['link_id', 'link_type', 'source_id', 'target_id', 'from_node', 'to_node']
                    and v is not None}

            # Convert lists/dicts to JSON strings
            for key, value in props.items():
                if isinstance(value, (list, dict)):
                    props[key] = json.dumps(value)

            # Add link_id as property
            if link_id:
                props['link_id'] = link_id

            # IMPORTANT: Store link_type as a property (not just as relationship type)
            props['link_type'] = link_type

            # Auto-populate visualization properties with defaults
            current_time = int(datetime.now().timestamp() * 1000)

            if 'link_strength' not in props:
                props['link_strength'] = 0.5

            if 'last_traversal_time' not in props:
                props['last_traversal_time'] = current_time

            if 'last_modified' not in props:
                props['last_modified'] = current_time

            # Create link
            g.query(f"""
                MATCH (source {{id: $source_id}})
                MATCH (target {{id: $target_id}})
                MERGE (source)-[r:{link_type}]->(target)
                SET r = $props
            """, params={
                "source_id": source_id,
                "target_id": target_id,
                "props": props
            })

            links_created += 1
            if idx % 10 == 0 or idx == len(links):
                print(f"  [{idx}/{len(links)}] Injected {links_created} links...")

        except Exception as e:
            links_failed += 1
            print(f"  [{idx}/{len(links)}] FAILED: {link_id} ({link_type}) - {str(e)[:80]}")

    print(f"  Result: {links_created} created, {links_failed} failed")

    # Verify
    print(f"\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    try:
        node_count = g.query("MATCH (n) RETURN count(n) as count").result_set[0][0]
        link_count = g.query("MATCH ()-[r]->() RETURN count(r) as count").result_set[0][0]

        print(f"\nGraph: {graph_name}")
        print(f"  Nodes: {node_count}")
        print(f"  Links: {link_count}")

        # Show node type distribution
        type_result = g.query("""
            MATCH (n)
            RETURN labels(n)[0] as type, count(n) as count
            ORDER BY count DESC
            LIMIT 10
        """)

        print(f"\nNode type distribution:")
        for row in type_result.result_set:
            print(f"  {row[0]:20s} : {row[1]}")

        # Show link type distribution
        link_type_result = g.query("""
            MATCH ()-[r]->()
            RETURN type(r) as link_type, count(r) as count
            ORDER BY count DESC
            LIMIT 10
        """)

        print(f"\nLink type distribution:")
        for row in link_type_result.result_set:
            print(f"  {row[0]:20s} : {row[1]}")

    except Exception as e:
        print(f"\nVerification error: {e}")

    print(f"\n" + "=" * 70)
    print("INJECTION COMPLETE")
    print("=" * 70)
    print(f"\nVisualize at: http://localhost:8000")
    print(f"  Graph Type: {'citizen' if 'citizen_' in graph_name else 'organization'}")
    print(f"  Graph ID: {graph_name.replace('citizen_', '').replace('org_', '')}")

    return True


def main():
    """CLI entry point."""

    if len(sys.argv) < 3:
        print("Usage: python tools/inject_consciousness_from_json.py <json_path> <graph_name> [--clear]")
        print("\nExamples:")
        print("  python tools/inject_consciousness_from_json.py data/luca_session.json citizen_luca")
        print("  python tools/inject_consciousness_from_json.py data/org_session.json org_mind_protocol --clear")
        sys.exit(1)

    json_path = sys.argv[1]
    graph_name = sys.argv[2]
    clear_existing = '--clear' in sys.argv

    inject_json_to_graph(json_path, graph_name, clear_existing)


if __name__ == "__main__":
    main()
