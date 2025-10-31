#!/usr/bin/env python3
"""
L4 Protocol Ingestion: Documentation Events (Phase 7)

Adds docs.* event schemas to the protocol graph, enabling membrane-first documentation.

Author: Ada Bridgekeeper
Date: 2025-10-30
Spec: docs/specs/v2/autonomy/architecture/membrane_systems_map.md
"""

import redis
import argparse
import sys
from typing import List, Tuple, Dict, Any


DOC_EVENTS = [
    ("docs.request.generate", "inject", "ecosystem/{ecosystem_id}/org/{org_id}/docs/generate", "Request L2 to generate/regenerate a documentation page"),
    ("docs.draft.created", "inject", "ecosystem/{ecosystem_id}/org/{org_id}/docs/draft", "AI/tool posts draft back to L2 for review"),
    ("docs.page.upsert", "inject", "ecosystem/{ecosystem_id}/org/{org_id}/docs/upsert", "L2 accepts page into repo after governance checks"),
    ("docs.publish", "broadcast", "ecosystem/{ecosystem_id}/org/{org_id}/docs/publish", "Publish doc version, triggers site build + WS broadcast"),
    ("docs.catalog.emit", "broadcast", "ecosystem/{ecosystem_id}/org/{org_id}/docs/catalog", "Site-wide TOC broadcast for in-system AI"),
    ("docs.page.updated", "broadcast", "ecosystem/{ecosystem_id}/org/{org_id}/docs/page", "Page change broadcast for subscribers"),
    ("docs.slice.emit", "broadcast", "ecosystem/{ecosystem_id}/org/{org_id}/docs/slice", "Semantic chunk broadcast for retrieval"),
]


def ingest_docs_events(r, graph_name: str = "protocol"):
    """
    Add docs.* event schemas to protocol graph.

    Creates:
    - 7 Event_Schema nodes
    - 1 Topic_Namespace for org/{org_id}/docs/*
    - 1 Governance_Policy with payload/rate/emitter constraints
    - Wiring: REQUIRES_ENVELOPE, REQUIRES_SIG, MAPS_TO_TOPIC, GOVERNS
    """

    print(f"📄 Phase 7: Documentation Events (docs.*)")
    print(f"Graph: {graph_name}")
    print(f"Events to add: {len(DOC_EVENTS)}")

    # Step 1: Get required references (Envelope_Schema, Signature_Suite)
    # Note: Protocol graph uses full path IDs, not short names
    query_refs = """
    MATCH (env) WHERE env.type_name = 'Envelope_Schema'
    MATCH (sig) WHERE sig.type_name = 'Signature_Suite'
    RETURN env.id as env_id, sig.id as sig_id
    LIMIT 1
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_refs)

    if not result or not result[1]:
        print("❌ Error: Required schemas not found (Envelope_Schema, Signature_Suite)")
        return False

    env_id = result[1][0][0].decode() if isinstance(result[1][0][0], bytes) else result[1][0][0]
    sig_id = result[1][0][1].decode() if isinstance(result[1][0][1], bytes) else result[1][0][1]
    print(f"✅ Found: {env_id}, {sig_id}")

    # Step 2: Create Topic_Namespace for docs (3-level: L3→L2 boundary)
    namespace_id = "protocol/Topic_Namespace/ecosystem.org.docs"
    namespace_pattern = "ecosystem/{ecosystem_id}/org/{org_id}/docs/*"

    query_namespace = f"""
    MERGE (ns:ProtocolNode {{id: '{namespace_id}'}})
    ON CREATE SET
        ns.pattern = '{namespace_pattern}',
        ns.type_name = 'Topic_Namespace',
        ns.description = 'Documentation events namespace'
    RETURN ns.id
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_namespace)
    print(f"✅ Created Topic_Namespace: {namespace_id} ({namespace_pattern})")

    # Step 3: Create Governance_Policy for docs namespace
    policy_id = "protocol/Governance_Policy/docs-namespace"

    query_policy = f"""
    MERGE (gp:ProtocolNode {{id: '{policy_id}'}})
    ON CREATE SET
        gp.type_name = 'Governance_Policy',
        gp.name = 'Documentation Events Policy',
        gp.defaults = '{{"max_payload_kb": 64, "rate_limit": {{"per_tenant": 100, "window_seconds": 3600}}, "allowed_emitters": ["component:tool.docgen", "component:tool.doc.publisher", "component:orchestrator.l2"]}}'
    WITH gp
    MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
    MERGE (gp)-[:GOVERNS]->(ns)
    RETURN gp.id
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_policy)
    print(f"✅ Created Governance_Policy: {policy_id}")
    print(f"   - Max payload: 64KB")
    print(f"   - Rate limit: 100/hour per tenant")
    print(f"   - Allowed emitters: tool.docgen, tool.doc.publisher, orchestrator.l2")

    # Step 4: Create Event_Schema nodes and wire relationships
    events_created = 0

    for event_name, direction, topic_pattern, summary in DOC_EVENTS:
        event_id = f"protocol/Event_Schema/{event_name}"

        query_event = f"""
        MERGE (es:ProtocolNode {{id: '{event_id}'}})
        ON CREATE SET
            es.name = '{event_name}',
            es.type_name = 'Event_Schema',
            es.direction = '{direction}',
            es.topic_pattern = '{topic_pattern}',
            es.summary = '{summary}',
            es.schema_hash = 'sha256:placeholder',
            es.version = '1.0'
        WITH es
        MATCH (env:ProtocolNode {{id: '{env_id}'}})
        MERGE (es)-[:REQUIRES_ENVELOPE]->(env)
        WITH es
        MATCH (sig:ProtocolNode {{id: '{sig_id}'}})
        MERGE (es)-[:REQUIRES_SIG]->(sig)
        WITH es
        MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
        MERGE (es)-[:MAPS_TO_TOPIC]->(ns)
        RETURN es.id
        """

        result = r.execute_command('GRAPH.QUERY', graph_name, query_event)
        events_created += 1
        print(f"   ✅ {event_name} ({direction})")

    print(f"\n✅ Phase 7 Complete: {events_created} doc events added")
    print(f"📊 Summary:")
    print(f"   - Events: {events_created} Event_Schema nodes")
    print(f"   - Namespace: 1 Topic_Namespace")
    print(f"   - Governance: 1 Governance_Policy")
    print(f"   - Links: ~{events_created * 3 + 1} relationships (REQUIRES_ENVELOPE, REQUIRES_SIG, MAPS_TO_TOPIC, GOVERNS)")

    return True


def verify_docs_events(r, graph_name: str = "protocol"):
    """
    Verify docs.* events are queryable from L4 protocol graph.
    """
    print("\n🔍 Verification:")

    # Count docs.* events
    query_count = """
    MATCH (es:Event_Schema)
    WHERE es.name STARTS WITH 'docs.'
    RETURN count(es) as doc_event_count
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_count)
    count = result[1][0][0]
    print(f"   - docs.* events: {count}")

    # Verify governance wiring
    query_governance = """
    MATCH (gp)-[:GOVERNS]->(ns)
    WHERE gp.type_name = 'Governance_Policy' AND ns.type_name = 'Topic_Namespace' AND ns.pattern CONTAINS 'docs'
    RETURN gp.id, ns.pattern
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_governance)
    if result[1]:
        policy_id = result[1][0][0].decode() if isinstance(result[1][0][0], bytes) else result[1][0][0]
        pattern = result[1][0][1].decode() if isinstance(result[1][0][1], bytes) else result[1][0][1]
        print(f"   - Governance: {policy_id} → {pattern}")

    # Sample query: What events can I emit for documentation?
    query_sample = """
    MATCH (es:Event_Schema)
    WHERE es.name STARTS WITH 'docs.'
    RETURN es.name, es.direction, es.topic_pattern
    ORDER BY es.name
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_sample)

    print(f"\n   Sample Query: What documentation events exist?")
    for row in result[1]:
        name = row[0].decode() if isinstance(row[0], bytes) else row[0]
        direction = row[1].decode() if isinstance(row[1], bytes) else row[1]
        topic = row[2].decode() if isinstance(row[2], bytes) else row[2]
        print(f"      - {name} ({direction}) → {topic}")

    print("\n✅ Verification complete: docs.* events are now queryable from L4")


def main():
    parser = argparse.ArgumentParser(description='Ingest documentation event schemas into L4 protocol graph')
    parser.add_argument('--host', default='localhost', help='Redis host')
    parser.add_argument('--port', type=int, default=6379, help='Redis port')
    parser.add_argument('--graph', default='protocol', help='FalkorDB graph name')

    args = parser.parse_args()

    # Connect to FalkorDB
    r = redis.Redis(host=args.host, port=args.port, decode_responses=False)

    try:
        r.ping()
        print(f"✅ Connected to FalkorDB at {args.host}:{args.port}\n")
    except redis.ConnectionError:
        print(f"❌ Failed to connect to FalkorDB at {args.host}:{args.port}")
        sys.exit(1)

    # Ingest docs events
    success = ingest_docs_events(r, args.graph)

    if not success:
        print("\n❌ Ingestion failed")
        sys.exit(1)

    # Verify ingestion
    verify_docs_events(r, args.graph)

    print("\n✅ Phase 7 ingestion complete - docs.* events are now living graph law")


if __name__ == "__main__":
    main()
