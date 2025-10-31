# scripts/backfill_entity_activations.py
# Usage:  python scripts/backfill_entity_activations.py [graph_name]
import sys, json
import redis
from pathlib import Path

# Add orchestration to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestration.adapters.ws.websocket_server import discover_graphs

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Get graph from args or use first discovered N1 graph
if len(sys.argv) > 1:
    graph = sys.argv[1]
else:
    graphs_dict = discover_graphs(host='localhost', port=6379)
    citizen_graphs = graphs_dict.get('n1_graphs', [])
    if not citizen_graphs:
        print("No citizen graphs found in FalkorDB")
        sys.exit(1)
    graph = citizen_graphs[0]
    print(f"No graph specified, using first discovered: {graph}")

# 1) Pull MEMBER_OF edges to build activations per node (energy * weight)
q_links = """
MATCH (n)-[m:MEMBER_OF]->(e:Subentity)
RETURN id(n) AS nid, n.name AS nname, e.id AS eid, COALESCE(m.weight,0.05) AS w, COALESCE(n.E,0.0) AS E
"""
res = r.execute_command("GRAPH.QUERY", graph, q_links)

# FalkorDB returns: [header, rows, metadata]
rows = res[1] if len(res) > 1 else []
if not rows:
    print("No MEMBER_OF rows; nothing to backfill.")
    sys.exit(0)

by_node = {}
for row in rows:
    nid, nname, eid, w, E = row[0], row[1], row[2], row[3], row[4]
    # eid is now entity_id string, not internal ID number
    nid = int(nid); w = float(w); E = float(E)
    if eid is None:
        print(f"Warning: Subentity has no entity_id for node {nname}, skipping")
        continue
    by_node.setdefault(nid, {"name": nname, "activations": {}})
    by_node[nid]["activations"][eid] = {
        "energy": E * w,
        "last_activated": 0
    }

print(f"Updating {len(by_node)} nodes in {graph} ...")

# Helper: set entity_activations as JSON string (simpler, works reliably)
def set_activations(nid: int, activations: dict):
    # Store as JSON string to avoid Cypher map escaping issues
    act_json = json.dumps(activations, separators=(",", ":"))
    # Escape quotes for Cypher string literal
    act_escaped = act_json.replace('"', '\\"')
    query = f'MATCH (n) WHERE id(n)={nid} SET n.entity_activations="{act_escaped}" RETURN 1'
    return r.execute_command("GRAPH.QUERY", graph, query)

# Execute updates
updated = 0
for nid, data in by_node.items():
    resp = set_activations(nid, data["activations"])
    updated += 1

print(f"Done. Nodes attempted: {len(by_node)}, updates issued: {updated}")

# Quick verification
verify = r.execute_command(
    "GRAPH.QUERY", graph,
    "MATCH (n) WHERE exists(n.entity_activations) RETURN count(n)"
)
count = int(verify[1][0][0]) if len(verify) > 1 and verify[1] else 0
print(f"Nodes with entity_activations: {count}")
