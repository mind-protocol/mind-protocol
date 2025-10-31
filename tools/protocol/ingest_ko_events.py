#!/usr/bin/env python3
"""
L4 Protocol Ingestion: Knowledge Object Events

Adds KO ingestion event schemas to the protocol graph, enabling membrane-first doc ingestion.

Flow:
- docs.ingest.chunk → chunk from MarkdownChunker
- ko.cluster.proposed → KO extraction from map_and_link
- ko.cluster.applied → GraphWrapper confirmation
- ko.cluster.rejected → Linter rejection

Author: Ada Bridgekeeper
Date: 2025-10-30
Spec: KO-First Documentation Architecture
"""

import redis
import argparse
import sys
from typing import List, Tuple, Dict, Any


KO_EVENTS = [
    # Ingestion events (inject)
    ("docs.ingest.chunk", "inject", "ecosystem/{ecosystem_id}/org/{org_id}/ko/ingest",
     "MD chunk from MarkdownChunker for KO extraction"),
    ("ko.cluster.proposed", "inject", "ecosystem/{ecosystem_id}/org/{org_id}/ko/proposed",
     "KO cluster from map_and_link with candidate refs and placeholders"),
    ("ko.cluster.applied", "broadcast", "ecosystem/{ecosystem_id}/org/{org_id}/ko/applied",
     "KO cluster successfully written to L2 graph"),
    ("ko.cluster.rejected", "broadcast", "ecosystem/{ecosystem_id}/org/{org_id}/ko/rejected",
     "KO cluster rejected by linter with error details"),

    # Review events (for contradiction/duplicate resolution)
    ("ko.review.request", "inject", "ecosystem/{ecosystem_id}/org/{org_id}/ko/review",
     "System requests human/AI review for contradiction or duplicate"),
    ("ko.review.response", "inject", "ecosystem/{ecosystem_id}/org/{org_id}/ko/review",
     "Human/AI responds to review request with accept/reject/merge"),
]


def ingest_ko_events(r, graph_name: str = "protocol"):
    """
    Add KO ingestion event schemas to protocol graph.

    Creates:
    - 6 Event_Schema nodes
    - 1 Topic_Namespace for ecosystem/{ecosystem_id}/org/{org_id}/ko/*
    - 1 Governance_Policy with payload/rate/emitter constraints
    - Wiring: REQUIRES_ENVELOPE, REQUIRES_SIG, MAPS_TO_TOPIC, GOVERNS
    """

    print(f"📚 L4 Protocol: Knowledge Object Events")
    print(f"Graph: {graph_name}")
    print(f"Events to add: {len(KO_EVENTS)}")

    # Step 1: Get required references (Envelope_Schema, Signature_Suite)
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

    # Step 2: Create Topic_Namespace for KO events (3-level: L3→L2 boundary)
    namespace_id = "protocol/Topic_Namespace/ecosystem.org.ko"
    namespace_pattern = "ecosystem/{ecosystem_id}/org/{org_id}/ko/*"

    query_namespace = f"""
    MERGE (ns:ProtocolNode {{id: '{namespace_id}'}})
    ON CREATE SET
        ns.pattern = '{namespace_pattern}',
        ns.type_name = 'Topic_Namespace',
        ns.description = 'Knowledge Object ingestion events namespace'
    RETURN ns.id
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_namespace)
    print(f"✅ Created Topic_Namespace: {namespace_id} ({namespace_pattern})")

    # Step 3: Create Governance_Policy for KO namespace
    policy_id = "protocol/Governance_Policy/ko-namespace"

    # KO events can be larger (chunks + extraction results), but cap at 256KB
    # Rate limit higher (500/hour) since ingestion is batch operation
    query_policy = f"""
    MERGE (gp:ProtocolNode {{id: '{policy_id}'}})
    ON CREATE SET
        gp.type_name = 'Governance_Policy',
        gp.name = 'Knowledge Object Events Policy',
        gp.defaults = '{{"max_payload_kb": 256, "rate_limit": {{"per_tenant": 500, "window_seconds": 3600}}, "allowed_emitters": ["component:tool.ko.ingest", "component:tool.ko.applier", "component:orchestrator.l2"]}}'
    WITH gp
    MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
    MERGE (gp)-[:GOVERNS]->(ns)
    RETURN gp.id
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_policy)
    print(f"✅ Created Governance_Policy: {policy_id}")
    print(f"   - Max payload: 256KB (larger for chunk + extraction)")
    print(f"   - Rate limit: 500/hour per tenant (batch ingestion)")
    print(f"   - Allowed emitters: tool.ko.ingest, tool.ko.applier, orchestrator.l2")

    # Step 4: Create Event_Schema nodes and wire relationships
    events_created = 0

    for event_name, direction, topic_pattern, summary in KO_EVENTS:
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

    print(f"\n✅ KO Events Ingestion Complete: {events_created} events added")
    print(f"📊 Summary:")
    print(f"   - Events: {events_created} Event_Schema nodes")
    print(f"   - Namespace: 1 Topic_Namespace (ecosystem/org/ko/*)")
    print(f"   - Governance: 1 Governance_Policy (256KB, 500/h)")
    print(f"   - Links: ~{events_created * 3 + 1} relationships")

    return True


def verify_ko_events(r, graph_name: str = "protocol"):
    """
    Verify KO events are queryable from L4 protocol graph.
    """
    print("\n🔍 Verification:")

    # Count KO events
    query_count = """
    MATCH (es:ProtocolNode)
    WHERE es.type_name = 'Event_Schema' AND (es.name STARTS WITH 'ko.' OR es.name = 'docs.ingest.chunk')
    RETURN count(es) as ko_event_count
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_count)
    count = result[1][0][0]
    print(f"   - KO events: {count}")

    # Verify governance wiring
    query_governance = """
    MATCH (gp)-[:GOVERNS]->(ns)
    WHERE gp.type_name = 'Governance_Policy' AND ns.pattern CONTAINS 'ko'
    RETURN gp.id, ns.pattern
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_governance)
    if result[1]:
        policy_id = result[1][0][0].decode() if isinstance(result[1][0][0], bytes) else result[1][0][0]
        pattern = result[1][0][1].decode() if isinstance(result[1][0][1], bytes) else result[1][0][1]
        print(f"   - Governance: {policy_id} → {pattern}")

    # Sample query: What KO ingestion events exist?
    query_sample = """
    MATCH (es:ProtocolNode)
    WHERE es.type_name = 'Event_Schema' AND (es.name STARTS WITH 'ko.' OR es.name = 'docs.ingest.chunk')
    RETURN es.name, es.direction, es.topic_pattern
    ORDER BY es.name
    """
    result = r.execute_command('GRAPH.QUERY', graph_name, query_sample)

    print(f"\n   Sample Query: What KO ingestion events exist?")
    for row in result[1]:
        name = row[0].decode() if isinstance(row[0], bytes) else row[0]
        direction = row[1].decode() if isinstance(row[1], bytes) else row[1]
        topic = row[2].decode() if isinstance(row[2], bytes) else row[2]
        print(f"      - {name} ({direction}) → {topic}")

    print("\n✅ Verification complete: KO events are now queryable from L4")


def main():
    parser = argparse.ArgumentParser(description='Ingest KO event schemas into L4 protocol graph')
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

    # Ingest KO events
    success = ingest_ko_events(r, args.graph)

    if not success:
        print("\n❌ Ingestion failed")
        sys.exit(1)

    # Verify ingestion
    verify_ko_events(r, args.graph)

    print("\n✅ KO event schemas added - ready for membrane-pure ingestion")


if __name__ == "__main__":
    main()
