#!/usr/bin/env python3
"""
Search all graphs for knowledge objects and IMPLEMENTS/DOCUMENTS relationships
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from falkordb import FalkorDB

# Connect to local FalkorDB
db = FalkorDB(host='localhost', port=6379)
graphs = db.list_graphs()

print(f"Searching {len(graphs)} graphs for docs with IMPLEMENTS/DOCUMENTS relationships...\n")
print("=" * 80)

found_any = False

for graph_name in graphs:
    try:
        graph = db.select_graph(graph_name)
    except Exception as e:
        continue

    # Quick check: count knowledge objects
    count_query = """
    MATCH (ko)
    WHERE ko:KnowledgeObject OR ko:U4_Knowledge_Object OR ko:Document
    RETURN count(ko) AS count
    """

    try:
        result = graph.query(count_query)
        if result.result_set and result.result_set[0][0] > 0:
            ko_count = result.result_set[0][0]
            print(f"\n📊 GRAPH: {graph_name} ({ko_count} knowledge objects)")
            print("-" * 80)

            # Get docs with relationships
            docs_query = """
            MATCH (doc)-[r]->(target)
            WHERE (doc:KnowledgeObject OR doc:U4_Knowledge_Object OR doc:Document)
              AND type(r) IN ['IMPLEMENTS', 'U4_IMPLEMENTS', 'DOCUMENTS', 'U4_DOCUMENTS',
                              'DOCUMENTED_BY', 'implements', 'documents']
            RETURN doc.name AS doc_name,
                   doc.ko_type AS doc_type,
                   doc.kind AS doc_kind,
                   doc.path AS doc_path,
                   doc.file_path AS file_path,
                   type(r) AS rel_type,
                   labels(target)[0] AS target_type,
                   target.name AS target_name,
                   target.path AS target_path
            ORDER BY doc.name
            LIMIT 100
            """

            result = graph.query(docs_query)
            if result.result_set:
                found_any = True
                print(f"Found {len(result.result_set)} relationships:\n")

                for row in result.result_set:
                    doc_name = row[0] or "(unnamed)"
                    doc_type = row[1]
                    doc_kind = row[2]
                    doc_path = row[3]
                    file_path = row[4]
                    rel_type = row[5]
                    target_type = row[6]
                    target_name = row[7] or "(unnamed)"
                    target_path = row[8]

                    doc_type_str = doc_type or doc_kind or "?"
                    path_str = file_path or doc_path or ""

                    print(f"📄 {doc_name} ({doc_type_str})")
                    if path_str:
                        print(f"   Path: {path_str}")
                    print(f"   {rel_type} → {target_type}: {target_name}")
                    if target_path:
                        print(f"   Target: {target_path}")
                    print()
            else:
                # Show sample docs even without relationships
                sample_query = """
                MATCH (doc)
                WHERE doc:KnowledgeObject OR doc:U4_Knowledge_Object OR doc:Document
                RETURN doc.name AS name,
                       doc.ko_type AS ko_type,
                       doc.kind AS kind,
                       doc.path AS path,
                       labels(doc)[0] AS label
                ORDER BY doc.name
                LIMIT 5
                """

                result = graph.query(sample_query)
                if result.result_set:
                    print(f"No IMPLEMENTS/DOCUMENTS relationships, but found these docs:\n")
                    for row in result.result_set:
                        name = row[0] or "(unnamed)"
                        ko_type = row[1]
                        kind = row[2]
                        path = row[3]
                        label = row[4]

                        print(f"  📄 {name} ({ko_type or kind}) [{label}]")
                        if path:
                            print(f"     Path: {path}")

    except Exception as e:
        continue

if not found_any:
    print("\n❌ No IMPLEMENTS/DOCUMENTS relationships found in any graph")
    print("\nThis could mean:")
    print("  1. The graphs haven't been populated with documentation yet")
    print("  2. The relationship types use different names")
    print("  3. The docs are in a remote graph (not synced locally)")

print("\n" + "=" * 80)
