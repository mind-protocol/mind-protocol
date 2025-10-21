#!/usr/bin/env python3
"""Check actual graph sizes in FalkorDB"""

from falkordb import FalkorDB

db = FalkorDB(host='localhost', port=6379)

graphs = [
    "citizen_luca",
    "citizen_iris",
    "citizen_felix",
    "citizen_ada"
]

for graph_name in graphs:
    try:
        g = db.select_graph(graph_name)

        # Count nodes
        node_result = g.query("MATCH (n) RETURN count(n) as count")
        node_count = node_result.result_set[0][0] if node_result.result_set else 0

        # Count links
        link_result = g.query("MATCH ()-[r]->() RETURN count(r) as count")
        link_count = link_result.result_set[0][0] if link_result.result_set else 0

        print(f"{graph_name}: {node_count} nodes, {link_count} links")

    except Exception as e:
        print(f"{graph_name}: ERROR - {e}")