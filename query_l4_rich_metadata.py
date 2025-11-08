#!/usr/bin/env python3
"""
Query L4 docs with rich metadata and implementation status
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from falkordb import FalkorDB

db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('protocol')

print("=" * 80)
print("L4 DOCUMENTATION - RICH METADATA & IMPLEMENTATION STATUS")
print("=" * 80)

# Query with full metadata
query = """
MATCH (ko:U4_Knowledge_Object)
WHERE ko.level = 'L4'
RETURN ko.name AS name,
       ko.ko_type AS ko_type,
       ko.version AS version,
       ko.status AS status,
       ko.owner AS owner,
       ko.implementation_status AS impl_status,
       ko.implementation_notes AS impl_notes,
       ko.file_path AS file_path,
       ko.uri AS uri,
       ko.hash AS hash
ORDER BY ko.name
"""

result = graph.query(query)

if not result.result_set:
    print("\nNo L4 documentation found")
    sys.exit(0)

print(f"\nTotal L4 Documents: {len(result.result_set)}\n")

# Group by implementation status
by_impl_status = {}
for row in result.result_set:
    impl_status = row[5] or 'unknown'
    if impl_status not in by_impl_status:
        by_impl_status[impl_status] = []
    by_impl_status[impl_status].append(row)

# Show stats
print("IMPLEMENTATION STATUS SUMMARY:")
print("-" * 80)
for status in ['implemented', 'partially_implemented', 'not_implemented', 'unknown']:
    count = len(by_impl_status.get(status, []))
    icon = {'implemented': '✅', 'partially_implemented': '🟡', 'not_implemented': '⭕', 'unknown': '❓'}[status]
    print(f"{icon} {status.replace('_', ' ').title()}: {count}")

print("\n" + "=" * 80)
print("DETAILED LISTING")
print("=" * 80)

for row in result.result_set:
    name = row[0]
    ko_type = row[1]
    version = row[2]
    status = row[3]
    owner = row[4]
    impl_status = row[5] or 'unknown'
    impl_notes = row[6] or "No implementation info"
    file_path = row[7]
    uri = row[8]
    hash_val = row[9]

    # Icon based on impl_status
    icon = {'implemented': '✅', 'partially_implemented': '🟡', 'not_implemented': '⭕', 'unknown': '❓'}.get(impl_status, '❓')

    print(f"\n{icon} {name}")
    print(f"{'─' * 80}")
    print(f"  Type: {ko_type} | Version: {version} | Status: {status}")
    print(f"  Owner: {owner}")
    print(f"  File: {file_path}")
    print(f"  URI: {uri}")
    print(f"  Hash: {hash_val[:16]}...")
    print(f"  Implementation: {impl_status}")
    print(f"  Notes: {impl_notes}")

print("\n" + "=" * 80)

# Query for DOCUMENTS relationships
print("\nDOCUMENTS RELATIONSHIPS")
print("=" * 80)

docs_query = """
MATCH (ko:U4_Knowledge_Object)-[r:U4_DOCUMENTS]->(target)
WHERE ko.level = 'L4'
RETURN ko.name AS doc_name,
       labels(target)[0] AS target_type,
       target.name AS target_name
ORDER BY ko.name
"""

result = graph.query(docs_query)
if result.result_set:
    for row in result.result_set:
        print(f"  📄 {row[0]}")
        print(f"     → {row[1]}: {row[2]}\n")
else:
    print("  No DOCUMENTS relationships found\n")

# Query for IMPLEMENTS relationships
print("IMPLEMENTS RELATIONSHIPS")
print("=" * 80)

impl_query = """
MATCH (code)-[r:U4_IMPLEMENTS]->(ko:U4_Knowledge_Object)
WHERE ko.level = 'L4'
RETURN ko.name AS spec_name,
       labels(code)[0] AS code_type,
       code.name AS code_name,
       code.path AS code_path
ORDER BY ko.name
"""

result = graph.query(impl_query)
if result.result_set:
    for row in result.result_set:
        print(f"  📄 {row[0]}")
        print(f"     ← {row[1]}: {row[2]}")
        print(f"     Path: {row[3]}\n")
else:
    print("  No IMPLEMENTS relationships found\n")

print("=" * 80)
