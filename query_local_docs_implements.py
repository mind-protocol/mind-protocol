#!/usr/bin/env python3
"""
Query local FalkorDB for docs and IMPLEMENTS relationships
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from falkordb import FalkorDB

# Connect to local FalkorDB
db = FalkorDB(host='localhost', port=6379)

# List available graphs
print("Available graphs:")
graphs = db.list_graphs()
for g in graphs:
    print(f"  - {g}")

if not graphs:
    print("\nNo graphs found in local FalkorDB")
    sys.exit(0)

# Use the first graph (or specify 'mindprotocol' or 'scopelock')
graph_name = 'mindprotocol' if 'mindprotocol' in graphs else graphs[0]
print(f"\nQuerying graph: {graph_name}\n")

graph = db.select_graph(graph_name)

# Query 1: Find all docs and what they IMPLEMENT
query1 = """
MATCH (ko)-[r:IMPLEMENTS]->(target)
WHERE ko:KnowledgeObject OR ko:U4_Knowledge_Object
RETURN ko.name AS doc_name,
       ko.ko_type AS doc_type,
       ko.kind AS doc_kind,
       ko.path AS doc_path,
       type(r) AS rel_type,
       labels(target)[0] AS target_type,
       target.name AS target_name,
       target.path AS target_path
ORDER BY ko.name
LIMIT 100
"""

print("=" * 80)
print("QUERY 1: Docs that IMPLEMENT something")
print("=" * 80)

try:
    result = graph.query(query1)

    if not result.result_set:
        print("No IMPLEMENTS relationships found")
    else:
        print(f"Found {len(result.result_set)} relationships:\n")

        for row in result.result_set:
            doc_name = row[0]
            doc_type = row[1]
            doc_kind = row[2]
            doc_path = row[3]
            rel_type = row[4]
            target_type = row[5]
            target_name = row[6]
            target_path = row[7]

            print(f"📄 {doc_name}")
            print(f"   Type: {doc_type or doc_kind}")
            print(f"   Path: {doc_path}")
            print(f"   {rel_type} → {target_type}: {target_name}")
            print(f"   Target path: {target_path}")
            print()

except Exception as e:
    print(f"Query 1 error: {e}")

# Query 2: Find all docs and what DOCUMENTS them
query2 = """
MATCH (ko)-[r:DOCUMENTS]->(target)
WHERE ko:KnowledgeObject OR ko:U4_Knowledge_Object
RETURN ko.name AS doc_name,
       ko.ko_type AS doc_type,
       ko.kind AS doc_kind,
       ko.path AS doc_path,
       type(r) AS rel_type,
       labels(target)[0] AS target_type,
       target.name AS target_name,
       target.path AS target_path
ORDER BY ko.name
LIMIT 100
"""

print("\n" + "=" * 80)
print("QUERY 2: Docs that DOCUMENT something")
print("=" * 80)

try:
    result = graph.query(query2)

    if not result.result_set:
        print("No DOCUMENTS relationships found")
    else:
        print(f"Found {len(result.result_set)} relationships:\n")

        for row in result.result_set:
            doc_name = row[0]
            doc_type = row[1]
            doc_kind = row[2]
            doc_path = row[3]
            rel_type = row[4]
            target_type = row[5]
            target_name = row[6]
            target_path = row[7]

            print(f"📄 {doc_name}")
            print(f"   Type: {doc_type or doc_kind}")
            print(f"   Path: {doc_path}")
            print(f"   {rel_type} → {target_type}: {target_name}")
            print(f"   Target path: {target_path}")
            print()

except Exception as e:
    print(f"Query 2 error: {e}")

# Query 3: Get counts by node type
query3 = """
MATCH (n)
RETURN labels(n)[0] AS node_type, count(n) AS count
ORDER BY count DESC
"""

print("\n" + "=" * 80)
print("QUERY 3: Node type statistics")
print("=" * 80)

try:
    result = graph.query(query3)

    if result.result_set:
        print(f"{'Node Type':<40} {'Count':>10}")
        print("-" * 52)
        for row in result.result_set:
            node_type = row[0]
            count = row[1]
            print(f"{node_type:<40} {count:>10}")

except Exception as e:
    print(f"Query 3 error: {e}")
