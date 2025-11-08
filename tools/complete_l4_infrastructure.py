#!/usr/bin/env python3
"""
Complete L4 Infrastructure Setup

This script completes the L4 documentation infrastructure by:
1. Creating L4_Governance_Policy nodes for LAW-001 through LAW-005
2. Ingesting code artifacts as U4_Code_Artifact nodes
3. Creating DOCUMENTS/IMPLEMENTS relationships
4. Creating U4_Work_Item task nodes for conformance suite implementation
"""

import os
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple
from falkordb import FalkorDB

# Connect to FalkorDB
db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('protocol')

PROJECT_ROOT = Path(__file__).parent.parent
L4_DOCS_DIR = PROJECT_ROOT / "docs" / "L4-law"
CONFORMANCE_SPEC = L4_DOCS_DIR / "CONFORMANCE_SUITE_SPECIFICATION.md"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file content"""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


# =============================================================================
# PART 1: Create L4_Governance_Policy Nodes
# =============================================================================

LAW_METADATA = {
    "LAW-001": {
        "title": "Consciousness Economy Protocol",
        "summary": "Economic framework for valuing and rewarding consciousness work",
        "version": "1.0",
        "status": "active"
    },
    "LAW-002": {
        "title": "Compute Payment System",
        "summary": "Tracks and compensates compute resource usage across consciousness operations",
        "version": "1.0",
        "status": "active"
    },
    "LAW-003": {
        "title": "Privacy and Consent Framework",
        "summary": "Governs data privacy, consent, and information flow control",
        "version": "1.0",
        "status": "active"
    },
    "LAW-004": {
        "title": "Membrane Access Control",
        "summary": "Defines layered access control and information boundaries",
        "version": "1.0",
        "status": "active"
    },
    "LAW-005": {
        "title": "Schema Registry Governance",
        "summary": "Manages schema evolution, versioning, and validation",
        "version": "1.0",
        "status": "active"
    }
}


def create_governance_policy_nodes():
    """Create L4_Governance_Policy nodes for all laws"""
    print("\n" + "=" * 80)
    print("PART 1: Creating L4_Governance_Policy Nodes")
    print("=" * 80)

    # Map law IDs to URI fragments based on actual URIs
    uri_fragments = {
        "LAW-001": "LAW-001_identity",
        "LAW-002": "LAW-002_compute",
        "LAW-003": "LAW-003_universal",
        "LAW-004": "LAW-004_AILLC",
        "LAW-005": "LAW-005_declaration"
    }

    created = 0

    for law_id, metadata in LAW_METADATA.items():
        # Find corresponding U4_Knowledge_Object using URI fragment
        uri_fragment = uri_fragments.get(law_id, law_id.lower())

        ko_query = """
        MATCH (ko:U4_Knowledge_Object)
        WHERE ko.level = 'L4'
          AND ko.uri CONTAINS $uri_fragment
        RETURN ko.uri AS uri, ko.hash AS hash, ko.file_path AS file_path
        LIMIT 1
        """

        result = graph.query(ko_query, {'uri_fragment': uri_fragment})

        if not result.result_set:
            print(f"⚠️  {law_id}: No U4_Knowledge_Object found (searched for '{uri_fragment}'), skipping")
            continue

        ko_uri = result.result_set[0][0]
        ko_hash = result.result_set[0][1]
        file_path = result.result_set[0][2]

        now = datetime.now(timezone.utc).isoformat()

        # Create L4_Governance_Policy node
        policy_cypher = """
        MERGE (policy:L4_Governance_Policy {policy_id: $policy_id})
        SET policy.name = $name,
            policy.type_name = 'L4_Governance_Policy',
            policy.summary = $summary,
            policy.version = $version,
            policy.status = $status,
            policy.uri = $uri,
            policy.hash = $hash,
            policy.file_path = $file_path,
            policy.level = 'L4',
            policy.scope_ref = 'protocol',
            policy.created_at = $now,
            policy.updated_at = $now,
            policy.valid_from = $now,
            policy.valid_to = NULL,
            policy.visibility = 'public',
            policy.created_by = 'l4_infrastructure_script',
            policy.substrate = 'organizational'
        RETURN policy.policy_id
        """

        params = {
            'policy_id': law_id,
            'name': metadata['title'],
            'summary': metadata['summary'],
            'version': metadata['version'],
            'status': metadata['status'],
            'uri': ko_uri,
            'hash': ko_hash,
            'file_path': file_path,
            'now': now
        }

        graph.query(policy_cypher, params)
        print(f"✅ Created: {law_id} - {metadata['title']}")
        created += 1

    print(f"\n📊 Created {created} L4_Governance_Policy nodes")
    return created


# =============================================================================
# PART 2: Ingest Code Artifacts
# =============================================================================

IMPLEMENTATION_PATHS = {
    "LAW-001": [
        # Identity attestation - no current implementation
    ],
    "LAW-002": [
        # Compute payment system
        "orchestration/protocol/envelopes/economy.py",
        "orchestration/mechanisms/consciousness_economy_stubs.py",
    ],
    "LAW-003": [
        # Universal Basic Compute - part of economy system
        "orchestration/protocol/envelopes/economy.py",
        "orchestration/mechanisms/consciousness_economy_stubs.py",
    ],
    "LAW-004": [
        # AILLC registration - no current implementation
    ],
    "LAW-005": [
        # Schema Registry governance
        "orchestration/libs/schema_registry.py",
        "orchestration/services/health/schema_map.py",
        "orchestration/scripts/setup_membership_schema.py",
    ]
}


def get_git_commit_hash(file_path: Path) -> str:
    """Get latest git commit hash for a file"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H', str(file_path)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()[:16] if result.returncode == 0 else "unknown"
    except:
        return "unknown"


def ingest_code_artifacts():
    """Scan codebase and create U4_Code_Artifact nodes"""
    print("\n" + "=" * 80)
    print("PART 2: Ingesting Code Artifacts")
    print("=" * 80)

    created = 0

    # Collect all unique file paths
    all_files: Set[str] = set()
    for files in IMPLEMENTATION_PATHS.values():
        all_files.update(files)

    now = datetime.now(timezone.utc).isoformat()

    for file_ref in sorted(all_files):
        file_path = PROJECT_ROOT / file_ref

        if not file_path.exists():
            print(f"⚠️  {file_ref}: File not found, skipping")
            continue

        # Determine language
        suffix = file_path.suffix
        language_map = {
            '.py': 'python',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.sql': 'sql'
        }
        language = language_map.get(suffix, 'unknown')

        # Get file metadata
        file_hash = compute_file_hash(file_path)
        commit_hash = get_git_commit_hash(file_path)

        # Create U4_Code_Artifact node
        artifact_cypher = """
        MERGE (artifact:U4_Code_Artifact {path: $path})
        SET artifact.name = $name,
            artifact.type_name = 'U4_Code_Artifact',
            artifact.language = $language,
            artifact.hash = $hash,
            artifact.commit_hash = $commit_hash,
            artifact.level = 'L4',
            artifact.scope_ref = 'protocol',
            artifact.created_at = $now,
            artifact.updated_at = $now,
            artifact.valid_from = $now,
            artifact.valid_to = NULL,
            artifact.visibility = 'public',
            artifact.created_by = 'l4_infrastructure_script',
            artifact.substrate = 'organizational'
        RETURN artifact.path
        """

        params = {
            'path': str(file_ref),
            'name': file_path.name,
            'language': language,
            'hash': file_hash,
            'commit_hash': commit_hash,
            'now': now
        }

        graph.query(artifact_cypher, params)
        print(f"✅ Ingested: {file_ref} ({language})")
        created += 1

    print(f"\n📊 Ingested {created} code artifacts")
    return created


# =============================================================================
# PART 3: Create DOCUMENTS and IMPLEMENTS Relationships
# =============================================================================

def create_documents_relationships():
    """Create U4_DOCUMENTS relationships from U4_Knowledge_Object to L4_Governance_Policy"""
    print("\n" + "=" * 80)
    print("PART 3a: Creating DOCUMENTS Relationships")
    print("=" * 80)

    # Map law IDs to URI fragments (same as in create_governance_policy_nodes)
    uri_fragments = {
        "LAW-001": "LAW-001_identity",
        "LAW-002": "LAW-002_compute",
        "LAW-003": "LAW-003_universal",
        "LAW-004": "LAW-004_AILLC",
        "LAW-005": "LAW-005_declaration"
    }

    created = 0
    now = datetime.now(timezone.utc).isoformat()

    for law_id in LAW_METADATA.keys():
        uri_fragment = uri_fragments.get(law_id, law_id.lower())

        cypher = """
        MATCH (ko:U4_Knowledge_Object)
        WHERE ko.level = 'L4'
          AND ko.uri CONTAINS $uri_fragment
        MATCH (policy:L4_Governance_Policy {policy_id: $policy_id})
        MERGE (ko)-[r:U4_DOCUMENTS]->(policy)
        SET r.doc_role = 'policy',
            r.confidence = 1.0,
            r.energy = 0.9,
            r.forming_mindstate = 'documentation',
            r.goal = 'document_law',
            r.created_at = $now,
            r.updated_at = $now,
            r.valid_from = $now,
            r.valid_to = NULL,
            r.visibility = 'public',
            r.commitments = [],
            r.created_by = 'l4_infrastructure_script',
            r.substrate = 'organizational'
        RETURN count(r)
        """

        params = {
            'uri_fragment': uri_fragment,
            'policy_id': law_id,
            'now': now
        }

        result = graph.query(cypher, params)
        if result.result_set and result.result_set[0][0] > 0:
            print(f"✅ {law_id}: U4_Knowledge_Object -[DOCUMENTS]-> L4_Governance_Policy")
            created += 1

    print(f"\n📊 Created {created} DOCUMENTS relationships")
    return created


def create_implements_relationships():
    """Create U4_IMPLEMENTS relationships from U4_Code_Artifact to L4_Governance_Policy"""
    print("\n" + "=" * 80)
    print("PART 3b: Creating IMPLEMENTS Relationships")
    print("=" * 80)

    created = 0
    now = datetime.now(timezone.utc).isoformat()

    for law_id, file_paths in IMPLEMENTATION_PATHS.items():
        for file_ref in file_paths:
            file_path = PROJECT_ROOT / file_ref
            if not file_path.exists():
                continue

            cypher = """
            MATCH (artifact:U4_Code_Artifact {path: $path})
            MATCH (policy:L4_Governance_Policy {policy_id: $policy_id})
            MERGE (artifact)-[r:U4_IMPLEMENTS]->(policy)
            SET r.confidence = 0.9,
                r.energy = 0.8,
                r.forming_mindstate = 'implementation',
                r.goal = 'implement_law',
                r.evidence_rules_passed = [],
                r.last_lint_ts = $now,
                r.created_at = $now,
                r.updated_at = $now,
                r.valid_from = $now,
                r.valid_to = NULL,
                r.visibility = 'public',
                r.commitments = [],
                r.created_by = 'l4_infrastructure_script',
                r.substrate = 'organizational'
            RETURN count(r)
            """

            params = {
                'path': str(file_ref),
                'policy_id': law_id,
                'now': now
            }

            result = graph.query(cypher, params)
            if result.result_set and result.result_set[0][0] > 0:
                print(f"✅ {law_id}: {file_ref} -[IMPLEMENTS]-> {law_id}")
                created += 1

    print(f"\n📊 Created {created} IMPLEMENTS relationships")
    return created


# =============================================================================
# PART 4: Create Conformance Suite Work Items
# =============================================================================

def parse_conformance_spec() -> List[Dict]:
    """Parse CONFORMANCE_SUITE_SPECIFICATION.md and extract work items"""

    if not CONFORMANCE_SPEC.exists():
        print(f"⚠️  Conformance spec not found: {CONFORMANCE_SPEC}")
        return []

    content = CONFORMANCE_SPEC.read_text(encoding='utf-8')

    work_items = []

    # Phase 1: Core Suite Implementation
    work_items.append({
        'task_id': 'CS-IMPL-001',
        'title': 'Implement CS_EVENT_SCHEMA_V1 Conformance Suite',
        'description': 'Create test suite validating L3_Event schema compliance with event_schema.json',
        'phase': 'Phase 1',
        'priority': 'P0',
        'assignee': 'Atlas',
        'state': 'todo',
        'depends_on': [],
        'acceptance_criteria': [
            'All critical tests pass (100%)',
            'All high-priority tests pass (95%+)',
            'Test runner executes suite',
            'Results logged in structured format'
        ]
    })

    work_items.append({
        'task_id': 'CS-IMPL-002',
        'title': 'Implement CS_TOPIC_NAMESPACE_V1 Conformance Suite',
        'description': 'Create test suite validating topic namespace structure and ownership',
        'phase': 'Phase 1',
        'priority': 'P0',
        'assignee': 'Atlas',
        'state': 'todo',
        'depends_on': [],
        'acceptance_criteria': [
            'Namespace validation tests pass',
            'Ownership verification tests pass',
            'Topic creation policy tests pass'
        ]
    })

    work_items.append({
        'task_id': 'CS-IMPL-003',
        'title': 'Implement CS_PRIVACY_CONSENT_V1 Conformance Suite',
        'description': 'Create test suite validating privacy extension and consent mechanisms',
        'phase': 'Phase 1',
        'priority': 'P1',
        'assignee': 'Atlas',
        'state': 'todo',
        'depends_on': ['CS-IMPL-001'],
        'acceptance_criteria': [
            'Privacy metadata validation tests pass',
            'Consent verification tests pass',
            'PII detection tests pass'
        ]
    })

    work_items.append({
        'task_id': 'CS-IMPL-004',
        'title': 'Implement CS_SCHEMA_EVOLUTION_V1 Conformance Suite',
        'description': 'Create test suite validating schema versioning and backward compatibility',
        'phase': 'Phase 1',
        'priority': 'P1',
        'assignee': 'Atlas',
        'state': 'todo',
        'depends_on': [],
        'acceptance_criteria': [
            'Version increment validation tests pass',
            'Backward compatibility tests pass',
            'Breaking change detection tests pass'
        ]
    })

    work_items.append({
        'task_id': 'CS-IMPL-005',
        'title': 'Implement CS_BITEMPORAL_V1 Conformance Suite',
        'description': 'Create test suite validating bitemporal metadata structure',
        'phase': 'Phase 1',
        'priority': 'P1',
        'assignee': 'Atlas',
        'state': 'todo',
        'depends_on': ['CS-IMPL-001'],
        'acceptance_criteria': [
            'Temporal metadata validation tests pass',
            'Timeline integrity tests pass',
            'Temporal query tests pass'
        ]
    })

    # Phase 2: CI Integration
    work_items.append({
        'task_id': 'CS-CI-001',
        'title': 'Create pre-commit hook for conformance tests',
        'description': 'Integrate conformance runner into pre-commit workflow',
        'phase': 'Phase 2',
        'priority': 'P1',
        'assignee': 'Atlas',
        'state': 'todo',
        'depends_on': ['CS-IMPL-001', 'CS-IMPL-002'],
        'acceptance_criteria': [
            'Hook runs on git commit',
            'Critical tests block commits on failure',
            'Hook runs in <5 seconds'
        ]
    })

    work_items.append({
        'task_id': 'CS-CI-002',
        'title': 'Integrate conformance tests into GitHub Actions CI',
        'description': 'Add conformance suite to CI pipeline',
        'phase': 'Phase 2',
        'priority': 'P1',
        'assignee': 'Atlas',
        'state': 'todo',
        'depends_on': ['CS-CI-001'],
        'acceptance_criteria': [
            'Tests run on every PR',
            'Results reported in PR checks',
            'Failures block merge'
        ]
    })

    # Phase 3: Infrastructure
    work_items.append({
        'task_id': 'CS-INFRA-001',
        'title': 'Create conformance test runner infrastructure',
        'description': 'Build runner at tools/conformance/runner.py with suite discovery and execution',
        'phase': 'Phase 1',
        'priority': 'P0',
        'assignee': 'Atlas',
        'state': 'todo',
        'depends_on': [],
        'acceptance_criteria': [
            'Runner discovers suites in tools/conformance/suites/',
            'Executes tests and collects results',
            'Outputs structured JSON results',
            'Supports filtering by suite/criticality'
        ]
    })

    work_items.append({
        'task_id': 'CS-INFRA-002',
        'title': 'Create conformance results dashboard',
        'description': 'Build dashboard showing conformance status across all suites',
        'phase': 'Phase 3',
        'priority': 'P2',
        'assignee': 'Iris',
        'state': 'todo',
        'depends_on': ['CS-IMPL-001', 'CS-IMPL-002', 'CS-IMPL-003', 'CS-IMPL-004', 'CS-IMPL-005'],
        'acceptance_criteria': [
            'Dashboard shows suite status',
            'Pass/fail rates visualized',
            'Historical trends tracked'
        ]
    })

    return work_items


def create_work_item_nodes(work_items: List[Dict]):
    """Create U4_Work_Item nodes for conformance suite tasks"""
    print("\n" + "=" * 80)
    print("PART 4: Creating Conformance Suite Work Items")
    print("=" * 80)

    created = 0
    now = datetime.now(timezone.utc).isoformat()

    for item in work_items:
        cypher = """
        MERGE (task:U4_Work_Item {task_id: $task_id})
        SET task.name = $title,
            task.type_name = 'U4_Work_Item',
            task.description = $description,
            task.phase = $phase,
            task.priority = $priority,
            task.assignee = $assignee,
            task.state = $state,
            task.depends_on = $depends_on,
            task.acceptance_criteria = $acceptance_criteria,
            task.level = 'L4',
            task.scope_ref = 'protocol',
            task.created_at = $now,
            task.updated_at = $now,
            task.valid_from = $now,
            task.valid_to = NULL,
            task.visibility = 'public',
            task.created_by = 'l4_infrastructure_script',
            task.substrate = 'organizational'
        RETURN task.task_id
        """

        params = {
            'task_id': item['task_id'],
            'title': item['title'],
            'description': item['description'],
            'phase': item['phase'],
            'priority': item['priority'],
            'assignee': item['assignee'],
            'state': item['state'],
            'depends_on': item['depends_on'],
            'acceptance_criteria': item['acceptance_criteria'],
            'now': now
        }

        graph.query(cypher, params)
        print(f"✅ {item['task_id']}: {item['title']}")
        created += 1

    # Create dependency relationships
    print("\nCreating task dependencies...")
    for item in work_items:
        for dep_id in item['depends_on']:
            dep_cypher = """
            MATCH (task:U4_Work_Item {task_id: $task_id})
            MATCH (dep:U4_Work_Item {task_id: $dep_id})
            MERGE (task)-[r:U4_DEPENDS_ON]->(dep)
            SET r.dependency_type = 'blocks',
                r.created_at = $now,
                r.created_by = 'l4_infrastructure_script'
            RETURN count(r)
            """

            graph.query(dep_cypher, {
                'task_id': item['task_id'],
                'dep_id': dep_id,
                'now': now
            })

    print(f"\n📊 Created {created} work item nodes")
    return created


# =============================================================================
# Main Execution
# =============================================================================

def main():
    print("=" * 80)
    print("L4 INFRASTRUCTURE COMPLETION SCRIPT")
    print("=" * 80)
    print(f"Connected to: FalkorDB (localhost:6379)")
    print(f"Graph: protocol")
    print(f"Project root: {PROJECT_ROOT}")

    stats = {
        'policies': 0,
        'artifacts': 0,
        'documents_rels': 0,
        'implements_rels': 0,
        'work_items': 0
    }

    # Part 1: L4_Governance_Policy nodes
    stats['policies'] = create_governance_policy_nodes()

    # Part 2: U4_Code_Artifact nodes
    stats['artifacts'] = ingest_code_artifacts()

    # Part 3: Relationships
    stats['documents_rels'] = create_documents_relationships()
    stats['implements_rels'] = create_implements_relationships()

    # Part 4: Work items
    work_items = parse_conformance_spec()
    stats['work_items'] = create_work_item_nodes(work_items)

    # Summary
    print("\n" + "=" * 80)
    print("COMPLETION SUMMARY")
    print("=" * 80)
    print(f"L4_Governance_Policy nodes: {stats['policies']}")
    print(f"U4_Code_Artifact nodes: {stats['artifacts']}")
    print(f"DOCUMENTS relationships: {stats['documents_rels']}")
    print(f"IMPLEMENTS relationships: {stats['implements_rels']}")
    print(f"U4_Work_Item nodes: {stats['work_items']}")
    print("\n✅ L4 infrastructure complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
