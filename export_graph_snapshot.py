#!/usr/bin/env python3
"""
Export graph snapshot as JSON for static visualization
Workaround for WebSocket server crashes
"""

from falkordb import FalkorDB
import json
import sys

def export_graph(graph_name: str, output_file: str, node_limit: int = 200, link_limit: int = 300):
    """Export graph data as JSON"""

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph(graph_name)

    print(f"Exporting {graph_name}...")

    # Query nodes with properties
    nodes_query = f"""
    MATCH (n)
    RETURN n.node_id as id,
           labels(n)[0] as type,
           n.name as name,
           n.energy as energy,
           n.confidence as confidence
    LIMIT {node_limit}
    """
    nodes_result = g.query(nodes_query)

    nodes = []
    for row in nodes_result.result_set:
        node = {
            'id': row[0] or f'node_{len(nodes)}',
            'type': row[1] or 'Unknown',
            'name': row[2] or row[0],
            'energy': row[3] or 0.0,
            'confidence': row[4] or 0.5
        }
        nodes.append(node)

    print(f"  ✓ Exported {len(nodes)} nodes")

    # Query links
    links_query = f"""
    MATCH (s)-[r]->(t)
    RETURN s.node_id as source,
           type(r) as type,
           t.node_id as target,
           r.weight as weight
    LIMIT {link_limit}
    """
    links_result = g.query(links_query)

    links = []
    for row in links_result.result_set:
        if row[0] and row[2]:  # Valid source and target
            link = {
                'source': row[0],
                'type': row[1] or 'RELATES_TO',
                'target': row[2],
                'weight': row[3] or 0.5
            }
            links.append(link)

    print(f"  ✓ Exported {len(links)} links")

    # Create snapshot
    snapshot = {
        'graph_id': graph_name,
        'nodes': nodes,
        'links': links,
        'metadata': {
            'exported_at': str(nodes_result.result_set),  # Timestamp would go here
            'node_count': len(nodes),
            'link_count': len(links)
        }
    }

    # Write to file
    with open(output_file, 'w') as f:
        json.dump(snapshot, f, indent=2)

    print(f"✅ Snapshot saved to {output_file}")
    print(f"   Nodes: {len(nodes)}, Links: {len(links)}")

    return snapshot

if __name__ == '__main__':
    # Export Iris's graph (has most data)
    export_graph('mind-protocol_iris', 'iris_graph_snapshot.json', node_limit=500, link_limit=1000)

    # Export Felix's demo graph
    export_graph('consciousness-infrastructure_mind-protocol_felix', 'felix_graph_snapshot.json')

    print("\n🎯 To visualize:")
    print("   1. Open iris_graph_snapshot.json or felix_graph_snapshot.json")
    print("   2. Use any D3.js force-directed graph viewer")
    print("   3. Or copy to public/ folder and load in dashboard")
