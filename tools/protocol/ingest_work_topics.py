#!/usr/bin/env python3
"""
Ingest Work Item Topic Namespaces (L4)

Seeds the protocol graph with work.* topic namespaces and governance policy
for ticket/bug/mission lifecycle events.

Maps work.* topics to existing generic telemetry schemas:
- work.*.opened/closed → telemetry.lifecycle@1.0.0
- work.*.updated → telemetry.state@1.0.0
- work.*.evidence → telemetry.lifecycle@1.0.0

Governance: POL_WORK_TICKETS_V1 (signature required, SEA not required)

Usage:
    python tools/protocol/ingest_work_topics.py

Author: Luca (Consciousness Architect) + Ada (Coordinator)
Date: 2025-10-31
Architecture: L4 Protocol Registry
"""

import os
import sys
from falkordb import FalkorDB

# Topic namespaces for work item lifecycle
WORK_NAMESPACES = [
    {
        "name": "work.ticket",
        "pattern": "work.ticket.*",
        "description": "Standard work item lifecycle (ticket creation, updates, completion)"
    },
    {
        "name": "work.bug",
        "pattern": "work.bug.*",
        "description": "Bug tracking lifecycle (bug reports, fixes, verification)"
    },
    {
        "name": "work.mission",
        "pattern": "work.mission.*",
        "description": "Mission/milestone tracking (multi-part objectives with dependencies)"
    }
]

# Concrete event topics that map to generic telemetry schemas
# We reuse telemetry.lifecycle@1.0.0 and telemetry.state@1.0.0
WORK_EVENT_MAPPINGS = {
    "work.ticket.opened": {
        "schema": "telemetry.lifecycle@1.0.0",
        "namespace": "work.ticket",
        "description": "Ticket created and enters todo state"
    },
    "work.ticket.updated": {
        "schema": "telemetry.state@1.0.0",
        "namespace": "work.ticket",
        "description": "Ticket metadata or state changed"
    },
    "work.ticket.closed": {
        "schema": "telemetry.lifecycle@1.0.0",
        "namespace": "work.ticket",
        "description": "Ticket completed (done) or abandoned (canceled)"
    },
    "work.ticket.evidence": {
        "schema": "telemetry.lifecycle@1.0.0",
        "namespace": "work.ticket",
        "description": "Evidence link added to ticket (PR merged, doc updated, test added)"
    },
    "work.bug.opened": {
        "schema": "telemetry.lifecycle@1.0.0",
        "namespace": "work.bug",
        "description": "Bug reported and enters todo state"
    },
    "work.bug.updated": {
        "schema": "telemetry.state@1.0.0",
        "namespace": "work.bug",
        "description": "Bug metadata or state changed"
    },
    "work.bug.closed": {
        "schema": "telemetry.lifecycle@1.0.0",
        "namespace": "work.bug",
        "description": "Bug fixed and verified"
    },
    "work.mission.opened": {
        "schema": "telemetry.lifecycle@1.0.0",
        "namespace": "work.mission",
        "description": "Mission created with milestones"
    },
    "work.mission.updated": {
        "schema": "telemetry.state@1.0.0",
        "namespace": "work.mission",
        "description": "Mission progress updated"
    },
    "work.mission.closed": {
        "schema": "telemetry.lifecycle@1.0.0",
        "namespace": "work.mission",
        "description": "Mission completed"
    }
}

def main():
    print("📋 Work Item Topic Namespaces Ingestion")
    print("="*70)

    # Connect to FalkorDB
    try:
        db = FalkorDB(
            host=os.getenv("FALKOR_HOST", "localhost"),
            port=int(os.getenv("FALKOR_PORT", "6379"))
        )
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to FalkorDB: {e}")
        sys.exit(1)

    graph_name = 'protocol'
    graph = db.select_graph(graph_name)

    # 0️⃣ Ensure SIG_ED25519_V1 and ENV_STANDARD_V1 exist
    print("\n0️⃣  Ensuring Signature Suite and Envelope Schema exist...")

    # Check if SIG_ED25519_V1 exists
    query_sig = """
    MATCH (sig:ProtocolNode)
    WHERE sig.type_name = 'L4_Signature_Suite' AND sig.suite_id = 'SIG_ED25519_V1'
    RETURN count(sig) as cnt
    """
    result_sig = graph.query(query_sig)
    sig_exists = len(result_sig.result_set) > 0 and result_sig.result_set[0][0] > 0

    if not sig_exists:
        create_sig = """
        CREATE (sig:ProtocolNode:L4_Signature_Suite {
            suite_id: 'SIG_ED25519_V1',
            type_name: 'L4_Signature_Suite',
            name: 'Ed25519 Signature Suite',
            algo: 'ed25519',
            hash_algos: ['sha256'],
            level: 'L4',
            scope_ref: 'protocol',
            description: 'Ed25519 signature suite for event validation',
            created_at: timestamp(),
            updated_at: timestamp()
        })
        """
        graph.query(create_sig)
        print("  ✓ Created SIG_ED25519_V1")
    else:
        print("  ✓ SIG_ED25519_V1 (ed25519)")

    # Check if ENV_STANDARD_V1 exists
    query_env = """
    MATCH (env:ProtocolNode)
    WHERE env.type_name = 'L4_Envelope_Schema' AND env.name = 'ENV_STANDARD_V1'
    RETURN count(env) as cnt
    """
    result_env = graph.query(query_env)
    env_exists = len(result_env.result_set) > 0 and result_env.result_set[0][0] > 0

    if not env_exists:
        create_env = """
        CREATE (env:ProtocolNode:L4_Envelope_Schema {
            name: 'ENV_STANDARD_V1',
            type_name: 'L4_Envelope_Schema',
            schema_uri: 'l4://schemas/envelope/standard/1.0.json',
            version: '1.0',
            level: 'L4',
            scope_ref: 'protocol',
            description: 'Standard envelope schema for event wrapping',
            created_at: timestamp(),
            updated_at: timestamp()
        })
        """
        graph.query(create_env)
        print("  ✓ Created ENV_STANDARD_V1")
    else:
        print("  ✓ ENV_STANDARD_V1")

    # 1️⃣ Create Topic Namespaces
    print("\n1️⃣  Creating Topic Namespaces (wildcard patterns)...")

    for ns in WORK_NAMESPACES:
        # MERGE to avoid duplicates
        # Note: id format is protocol/L4_Topic_Namespace/<name>
        ns_id = f"protocol/L4_Topic_Namespace/{ns['name']}"
        query = f"""
        MERGE (ns:ProtocolNode:L4_Topic_Namespace {{name: '{ns['name']}'}})
        ON CREATE SET
            ns.id = '{ns_id}',
            ns.type_name = 'L4_Topic_Namespace',
            ns.pattern = '{ns['pattern']}',
            ns.description = '{ns['description']}',
            ns.level = 'L4',
            ns.scope_ref = 'protocol',
            ns.created_at = timestamp(),
            ns.updated_at = timestamp()
        ON MATCH SET
            ns.id = '{ns_id}',
            ns.updated_at = timestamp()
        """
        graph.query(query)

        # Determine policy type
        policy_type = "FLEX"  # Work items don't require SEA
        print(f"  📝 {policy_type:6s} {ns['name']:30s} - {ns['description'][:50]}")

    # 2️⃣ Create Schema Bundle
    print("\n2️⃣  Creating Schema Bundle...")

    bundle_query = """
    MERGE (b:ProtocolNode:L4_Schema_Bundle {name: 'BUNDLE_WORK_ITEMS_1_0_0'})
    ON CREATE SET
        b.type_name = 'L4_Schema_Bundle',
        b.semver = '1.0.0',
        b.status = 'active',
        b.hash = 'sha256:work_items_1_0_0_placeholder',
        b.level = 'L4',
        b.scope_ref = 'protocol',
        b.description = 'Work item lifecycle schemas (tickets, bugs, missions)',
        b.created_at = timestamp(),
        b.updated_at = timestamp()
    ON MATCH SET
        b.updated_at = timestamp()
    """
    graph.query(bundle_query)
    print("  ✓ BUNDLE_WORK_ITEMS_1_0_0 (active)")

    # 3️⃣ Link concrete topics to existing telemetry schemas
    print("\n3️⃣  Linking Work Topics to Generic Telemetry Schemas...")

    for topic, mapping in WORK_EVENT_MAPPINGS.items():
        # Find the telemetry schema (already exists from telemetry ingestion)
        schema_name = mapping["schema"]
        namespace_name = mapping["namespace"]

        # Create relationships
        link_query = f"""
        MATCH (schema:L4_Event_Schema {{name: '{schema_name}'}})
        MATCH (ns:L4_Topic_Namespace {{name: '{namespace_name}'}})
        MATCH (bundle:L4_Schema_Bundle {{name: 'BUNDLE_WORK_ITEMS_1_0_0'}})
        MATCH (sig:L4_Signature_Suite {{suite_id: 'SIG_ED25519_V1'}})

        // Link bundle to schema (if not already linked)
        MERGE (bundle)-[:U4_PUBLISHES_SCHEMA]->(schema)

        // Link schema to namespace
        MERGE (schema)-[:U4_MAPS_TO_TOPIC]->(ns)

        // Link schema to signature suite
        MERGE (schema)-[:U4_REQUIRES_SIG]->(sig)
        """
        graph.query(link_query)

        print(f"  ✓ {topic:35s} → {schema_name}")

    # 4️⃣ Create Governance Policies
    print("\n4️⃣  Creating Governance Policy...")

    pol_query = """
    MERGE (gp:ProtocolNode:L4_Governance_Policy {policy_id: 'POL_WORK_TICKETS_V1'})
    ON CREATE SET
        gp.type_name = 'L4_Governance_Policy',
        gp.name = 'Work Item Lifecycle Policy',
        gp.hash = 'sha256:pol_work_tickets_v1_placeholder',
        gp.uri = 'l4://law/POL_WORK_TICKETS_V1.md',
        gp.status = 'active',
        gp.level = 'L4',
        gp.scope_ref = 'protocol',
        gp.summary = 'Governance for work.* topic namespaces (signature required, SEA not required)',
        gp.description = 'Governs all work item lifecycle events: tickets, bugs, missions. Requires signature but not SEA (operational telemetry).',
        gp.created_at = timestamp(),
        gp.updated_at = timestamp()
    ON MATCH SET
        gp.updated_at = timestamp()
    """
    graph.query(pol_query)

    # Link governance policy to namespaces
    for ns in WORK_NAMESPACES:
        link_pol = f"""
        MATCH (gp:L4_Governance_Policy {{policy_id: 'POL_WORK_TICKETS_V1'}})
        MATCH (ns:L4_Topic_Namespace {{name: '{ns['name']}'}})
        MERGE (gp)-[:U4_GOVERNS]->(ns)
        """
        graph.query(link_pol)

    print("  ✓ POL_WORK_TICKETS_V1            - FLEX (signature required, 3 namespaces)")

    # Summary
    print("\n" + "="*70)
    print("✅ Ingested work item topic namespaces\n")
    print("Summary:")
    print(f"  - {len(WORK_NAMESPACES)} Topic_Namespace nodes (wildcard patterns)")
    print(f"  - {len(WORK_EVENT_MAPPINGS)} concrete topic mappings to generic telemetry schemas")
    print(f"  - 1 Governance_Policy node (POL_WORK_TICKETS_V1)")
    print(f"  - 1 Schema_Bundle (BUNDLE_WORK_ITEMS_1_0_0, active)")

    print("\nPolicy Breakdown:")
    print(f"  📝 FLEX (signed only): work.ticket.*, work.bug.*, work.mission.*")
    print("     (reuses telemetry.lifecycle@1.0.0 and telemetry.state@1.0.0)")

    print("\nConcrete Topic Mappings:")
    for topic, mapping in list(WORK_EVENT_MAPPINGS.items())[:5]:
        print(f"  - {topic:35s} → {mapping['schema']}")
    print(f"  ... and {len(WORK_EVENT_MAPPINGS) - 5} more")

    print("\nNext Steps:")
    print("  1. Re-export L4 registry: python tools/protocol/export_l4_public.py")
    print("  2. Run mp-lint: python tools/mp_lint/cli.py")
    print("  3. Expected: R-001 = 0 (schemas exist)")
    print("  4. Create GitHub webhook: services/ingestors/github_webhook.py")
    print("  5. SafeBroadcaster should emit work.* topics cleanly")


if __name__ == "__main__":
    main()
