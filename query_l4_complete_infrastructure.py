#!/usr/bin/env python3
"""
Query Complete L4 Infrastructure

Shows the full L4 documentation and implementation graph including:
- L4_Governance_Policy nodes (laws)
- U4_Knowledge_Object nodes (documentation)
- U4_Code_Artifact nodes (implementing code)
- U4_Work_Item nodes (tasks)
- DOCUMENTS relationships (docs → policies)
- IMPLEMENTS relationships (code → policies)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from falkordb import FalkorDB

db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('protocol')

print("=" * 80)
print("L4 INFRASTRUCTURE - COMPLETE VIEW")
print("=" * 80)

# 1. L4_Governance_Policy nodes
print("\n📜 L4 GOVERNANCE POLICIES")
print("-" * 80)

policy_query = """
MATCH (policy:L4_Governance_Policy)
RETURN policy.policy_id AS policy_id,
       policy.name AS name,
       policy.summary AS summary,
       policy.version AS version,
       policy.status AS status,
       policy.uri AS uri
ORDER BY policy.policy_id
"""

result = graph.query(policy_query)
if result.result_set:
    for row in result.result_set:
        print(f"\n  {row[0]}: {row[1]}")
        print(f"    Summary: {row[2]}")
        print(f"    Version: {row[3]} | Status: {row[4]}")
        print(f"    URI: {row[5]}")
else:
    print("  No policies found")

# 2. U4_Code_Artifact nodes
print("\n\n💾 CODE ARTIFACTS (Implementations)")
print("-" * 80)

artifact_query = """
MATCH (artifact:U4_Code_Artifact)
WHERE artifact.level = 'L4'
RETURN artifact.path AS path,
       artifact.language AS language,
       artifact.commit_hash AS commit_hash
ORDER BY artifact.path
"""

result = graph.query(artifact_query)
if result.result_set:
    for row in result.result_set:
        print(f"\n  📄 {row[0]}")
        print(f"     Language: {row[1]} | Commit: {row[2]}")
else:
    print("  No code artifacts found")

# 3. DOCUMENTS relationships
print("\n\n📚 DOCUMENTS RELATIONSHIPS (Docs → Policies)")
print("-" * 80)

docs_query = """
MATCH (ko:U4_Knowledge_Object)-[r:U4_DOCUMENTS]->(policy:L4_Governance_Policy)
WHERE ko.level = 'L4'
RETURN ko.name AS doc_name,
       policy.policy_id AS policy_id,
       policy.name AS policy_name,
       r.doc_role AS doc_role,
       r.confidence AS confidence
ORDER BY policy.policy_id
"""

result = graph.query(docs_query)
if result.result_set:
    for row in result.result_set:
        print(f"\n  📄 {row[0]}")
        print(f"     DOCUMENTS → {row[1]}: {row[2]}")
        print(f"     Role: {row[3]} | Confidence: {row[4]}")
else:
    print("  No DOCUMENTS relationships found")

# 4. IMPLEMENTS relationships
print("\n\n🔧 IMPLEMENTS RELATIONSHIPS (Code → Policies)")
print("-" * 80)

impl_query = """
MATCH (artifact:U4_Code_Artifact)-[r:U4_IMPLEMENTS]->(policy:L4_Governance_Policy)
RETURN artifact.path AS code_path,
       policy.policy_id AS policy_id,
       policy.name AS policy_name,
       r.confidence AS confidence
ORDER BY policy.policy_id, artifact.path
"""

result = graph.query(impl_query)
if result.result_set:
    current_policy = None
    for row in result.result_set:
        policy_id = row[1]
        if policy_id != current_policy:
            print(f"\n  {policy_id}: {row[2]}")
            current_policy = policy_id
        print(f"     ← 💾 {row[0]} (confidence: {row[3]})")
else:
    print("  No IMPLEMENTS relationships found")

# 5. U4_Work_Item nodes (Conformance Suite tasks)
print("\n\n✅ WORK ITEMS (Conformance Suite Tasks)")
print("-" * 80)

work_item_query = """
MATCH (task:U4_Work_Item)
WHERE task.level = 'L4'
RETURN task.task_id AS task_id,
       task.name AS name,
       task.phase AS phase,
       task.priority AS priority,
       task.assignee AS assignee,
       task.state AS state,
       task.depends_on AS depends_on
ORDER BY task.task_id
"""

result = graph.query(work_item_query)
if result.result_set:
    phase_groups = {}
    for row in result.result_set:
        phase = row[2]
        if phase not in phase_groups:
            phase_groups[phase] = []
        phase_groups[phase].append(row)

    for phase in sorted(phase_groups.keys()):
        print(f"\n  {phase}:")
        for row in phase_groups[phase]:
            task_id = row[0]
            name = row[1]
            priority = row[3]
            assignee = row[4]
            state = row[5]
            depends_on = row[6]

            status_icon = {'todo': '⭕', 'in_progress': '🔄', 'done': '✅'}.get(state, '❓')

            print(f"\n    {status_icon} {task_id}: {name}")
            print(f"       Priority: {priority} | Assignee: {assignee} | State: {state}")
            if depends_on:
                print(f"       Depends on: {', '.join(depends_on)}")
else:
    print("  No work items found")

# 6. Summary statistics
print("\n\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

stats_query = """
MATCH (policy:L4_Governance_Policy)
OPTIONAL MATCH (policy)<-[:U4_DOCUMENTS]-(ko:U4_Knowledge_Object)
OPTIONAL MATCH (policy)<-[:U4_IMPLEMENTS]-(artifact:U4_Code_Artifact)
RETURN policy.policy_id AS policy_id,
       count(DISTINCT ko) AS doc_count,
       count(DISTINCT artifact) AS impl_count
ORDER BY policy.policy_id
"""

result = graph.query(stats_query)
if result.result_set:
    print("\nPolicy Implementation Status:")
    print(f"{'Policy':<10} {'Docs':<8} {'Impls':<8} {'Status':<15}")
    print("-" * 45)

    for row in result.result_set:
        policy_id = row[0]
        doc_count = row[1]
        impl_count = row[2]

        if impl_count > 0:
            status = f"✅ {impl_count} file(s)"
        else:
            status = "⭕ Not implemented"

        print(f"{policy_id:<10} {doc_count:<8} {impl_count:<8} {status:<15}")

# Count work items by phase
work_item_stats = """
MATCH (task:U4_Work_Item)
WHERE task.level = 'L4'
RETURN task.phase AS phase, count(task) AS count
ORDER BY phase
"""

result = graph.query(work_item_stats)
if result.result_set:
    print("\n\nConformance Suite Tasks by Phase:")
    total_tasks = 0
    for row in result.result_set:
        phase = row[0]
        count = row[1]
        total_tasks += count
        print(f"  {phase}: {count} task(s)")
    print(f"  Total: {total_tasks} task(s)")

print("\n" + "=" * 80)
