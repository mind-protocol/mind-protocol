#!/usr/bin/env python3
"""
Query for L4 (Protocol Law) level documentation and IMPLEMENTS/DOCUMENTS relationships
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from falkordb import FalkorDB

# Connect to local FalkorDB
db = FalkorDB(host='localhost', port=6379)
graphs = ['mind-protocol', 'protocol', 'schema_registry', 'ecosystem']

print("=" * 80)
print("L4 (Protocol Law) Documentation Query")
print("=" * 80)

for graph_name in graphs:
    try:
        graph = db.select_graph(graph_name)
    except Exception as e:
        continue

    print(f"\n📊 GRAPH: {graph_name}")
    print("-" * 80)

    # Query 1: L4 Knowledge Objects
    query_l4_ko = """
    MATCH (ko)
    WHERE (ko:KnowledgeObject OR ko:U4_Knowledge_Object)
      AND ko.level = 'L4'
    RETURN ko.name AS name,
           ko.ko_type AS ko_type,
           ko.kind AS kind,
           ko.path AS path,
           ko.uri AS uri,
           ko.scope_ref AS scope_ref,
           labels(ko)[0] AS label
    ORDER BY ko.name
    """

    try:
        result = graph.query(query_l4_ko)
        if result.result_set:
            print(f"\n  L4 Knowledge Objects: {len(result.result_set)}")
            for row in result.result_set:
                name = row[0] or "(unnamed)"
                ko_type = row[1]
                kind = row[2]
                path = row[3]
                uri = row[4]
                scope_ref = row[5]
                label = row[6]

                type_str = ko_type or kind or "?"
                print(f"\n  📄 {name} ({type_str})")
                print(f"     Scope: {scope_ref}")
                if path:
                    print(f"     Path: {path}")
                if uri:
                    print(f"     URI: {uri}")
        else:
            print("  No L4 knowledge objects found")
    except Exception as e:
        print(f"  Error querying L4 KOs: {e}")

    # Query 2: L4 DOCUMENTS relationships
    query_l4_docs = """
    MATCH (doc)-[r:DOCUMENTS|U4_DOCUMENTS]->(target)
    WHERE (doc:KnowledgeObject OR doc:U4_Knowledge_Object)
      AND doc.level = 'L4'
    RETURN doc.name AS doc_name,
           doc.ko_type AS doc_type,
           doc.path AS doc_path,
           type(r) AS rel_type,
           labels(target)[0] AS target_type,
           target.name AS target_name,
           target.type_name AS target_type_name
    ORDER BY doc.name
    """

    try:
        result = graph.query(query_l4_docs)
        if result.result_set:
            print(f"\n  L4 DOCUMENTS relationships: {len(result.result_set)}\n")
            for row in result.result_set:
                doc_name = row[0] or "(unnamed)"
                doc_type = row[1]
                doc_path = row[2]
                rel_type = row[3]
                target_type = row[4]
                target_name = row[5] or "(unnamed)"
                target_type_name = row[6]

                print(f"  📄 {doc_name} ({doc_type})")
                if doc_path:
                    print(f"     Path: {doc_path}")
                print(f"     {rel_type} → {target_type}: {target_name}")
                if target_type_name:
                    print(f"     Target type: {target_type_name}")
        else:
            print("  No L4 DOCUMENTS relationships found")
    except Exception as e:
        print(f"  Error querying L4 DOCUMENTS: {e}")

    # Query 3: L4 IMPLEMENTS relationships
    query_l4_impl = """
    MATCH (impl)-[r:IMPLEMENTS|U4_IMPLEMENTS]->(target)
    WHERE (impl:Code_Artifact OR impl:U4_Code_Artifact OR impl:KnowledgeObject)
      AND (impl.level = 'L4' OR target.level = 'L4')
    RETURN impl.name AS impl_name,
           labels(impl)[0] AS impl_type,
           impl.path AS impl_path,
           type(r) AS rel_type,
           labels(target)[0] AS target_type,
           target.name AS target_name,
           target.level AS target_level
    ORDER BY impl.name
    LIMIT 50
    """

    try:
        result = graph.query(query_l4_impl)
        if result.result_set:
            print(f"\n  L4-related IMPLEMENTS relationships: {len(result.result_set)}\n")
            for row in result.result_set:
                impl_name = row[0] or "(unnamed)"
                impl_type = row[1]
                impl_path = row[2]
                rel_type = row[3]
                target_type = row[4]
                target_name = row[5] or "(unnamed)"
                target_level = row[6]

                print(f"  💾 {impl_name} ({impl_type})")
                if impl_path:
                    print(f"     Path: {impl_path}")
                print(f"     {rel_type} → {target_type}: {target_name} [L{target_level}]")
        else:
            print("  No L4-related IMPLEMENTS relationships found")
    except Exception as e:
        print(f"  Error querying L4 IMPLEMENTS: {e}")

    # Query 4: All L4 node types
    query_l4_types = """
    MATCH (n)
    WHERE n.level = 'L4'
    RETURN labels(n)[0] AS node_type, count(n) AS count
    ORDER BY count DESC
    """

    try:
        result = graph.query(query_l4_types)
        if result.result_set:
            print(f"\n  L4 Node Type Distribution:")
            print(f"  {'-' * 40}")
            for row in result.result_set:
                node_type = row[0]
                count = row[1]
                print(f"  {node_type:<30} {count:>5}")
    except Exception as e:
        pass

print("\n" + "=" * 80)
