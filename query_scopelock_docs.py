#!/usr/bin/env python3
"""
Query scopelock and graphcare_scopelock graphs for docs and implementations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from falkordb import FalkorDB

# Connect to local FalkorDB
db = FalkorDB(host='localhost', port=6379)

# Check both scopelock graphs
graphs_to_check = ['scopelock', 'graphcare_scopelock']

for graph_name in graphs_to_check:
    print("=" * 80)
    print(f"GRAPH: {graph_name}")
    print("=" * 80)

    try:
        graph = db.select_graph(graph_name)
    except Exception as e:
        print(f"Cannot access graph: {e}\n")
        continue

    # Query 1: Node type counts
    query_counts = """
    MATCH (n)
    RETURN labels(n)[0] AS node_type, count(n) AS count
    ORDER BY count DESC
    LIMIT 20
    """

    print("\nNode Types:")
    print("-" * 80)

    try:
        result = graph.query(query_counts)
        if result.result_set:
            for row in result.result_set:
                node_type = row[0]
                count = row[1]
                print(f"  {node_type:<50} {count:>6}")
        else:
            print("  No nodes found")
    except Exception as e:
        print(f"  Error: {e}")

    # Query 2: Relationship type counts
    query_rels = """
    MATCH ()-[r]->()
    RETURN type(r) AS rel_type, count(r) AS count
    ORDER BY count DESC
    LIMIT 20
    """

    print("\nRelationship Types:")
    print("-" * 80)

    try:
        result = graph.query(query_rels)
        if result.result_set:
            for row in result.result_set:
                rel_type = row[0]
                count = row[1]
                print(f"  {rel_type:<50} {count:>6}")
        else:
            print("  No relationships found")
    except Exception as e:
        print(f"  Error: {e}")

    # Query 3: Find docs with IMPLEMENTS/U4_IMPLEMENTS relationships
    query_implements = """
    MATCH (doc)-[r]->(target)
    WHERE type(r) IN ['IMPLEMENTS', 'U4_IMPLEMENTS', 'DOCUMENTS', 'U4_DOCUMENTS']
    RETURN doc.name AS doc_name,
           doc.ko_type AS doc_type,
           doc.path AS doc_path,
           type(r) AS rel_type,
           labels(target)[0] AS target_type,
           target.name AS target_name,
           target.path AS target_path
    ORDER BY doc.name
    LIMIT 50
    """

    print("\nDocs with IMPLEMENTS/DOCUMENTS relationships:")
    print("-" * 80)

    try:
        result = graph.query(query_implements)
        if not result.result_set:
            print("  No IMPLEMENTS/DOCUMENTS relationships found")
        else:
            print(f"  Found {len(result.result_set)} relationships:\n")

            for row in result.result_set:
                doc_name = row[0]
                doc_type = row[1]
                doc_path = row[2]
                rel_type = row[3]
                target_type = row[4]
                target_name = row[5]
                target_path = row[6]

                print(f"  📄 {doc_name} ({doc_type})")
                print(f"     Path: {doc_path}")
                print(f"     {rel_type} → {target_type}: {target_name}")
                print(f"     Target: {target_path}")
                print()

    except Exception as e:
        print(f"  Error: {e}")

    # Query 4: Sample some knowledge objects
    query_sample = """
    MATCH (ko)
    WHERE ko:KnowledgeObject OR ko:U4_Knowledge_Object
    RETURN ko.name AS name,
           ko.ko_type AS ko_type,
           ko.kind AS kind,
           ko.path AS path,
           labels(ko)[0] AS label
    ORDER BY ko.name
    LIMIT 10
    """

    print("\nSample Knowledge Objects:")
    print("-" * 80)

    try:
        result = graph.query(query_sample)
        if not result.result_set:
            print("  No knowledge objects found")
        else:
            for row in result.result_set:
                name = row[0]
                ko_type = row[1]
                kind = row[2]
                path = row[3]
                label = row[4]

                print(f"  📄 {name}")
                print(f"     Type: {ko_type or kind} ({label})")
                print(f"     Path: {path}")
                print()

    except Exception as e:
        print(f"  Error: {e}")

    print("\n")
