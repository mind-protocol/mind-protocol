#!/usr/bin/env python3
"""
Health Protocol L4 Schema Ingestion

Adds health.* event schemas to L4 protocol graph for membrane-native health monitoring.

Usage:
    python3 tools/protocol/ingest_health_protocol.py
"""

import sys
import redis
from pathlib import Path


def ingest_health_schemas():
    """Add health.* event schemas and governance to L4 protocol graph"""

    # Connect to FalkorDB via Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    graph_name = "protocol"

    # Health event schemas
    schemas = [
        {
            "name": "health.link.ping",
            "direction": "inject",
            "description": "Request echo across specific topic/route for synthetic link health",
            "content_schema": {
                "probe_id": "string (uuid)",
                "target_topic": "string (topic pattern to test)",
                "headers": "object? (optional test headers)",
                "sample_payload": "object? (optional test payload)",
                "ttl_ms": "integer (timeout for response)"
            }
        },
        {
            "name": "health.link.pong",
            "direction": "broadcast",
            "description": "Echo response from health echo tool",
            "content_schema": {
                "probe_id": "string (matches ping)",
                "target_topic": "string (requested topic)",
                "received_topic": "string (actual topic received on)",
                "rtt_ms": "integer (round-trip time)",
                "hops": "integer (relay count)",
                "responder": "string (echo tool id)"
            }
        },
        {
            "name": "health.link.snapshot",
            "direction": "broadcast",
            "description": "Rolling window metrics per {emitter, topic}",
            "content_schema": {
                "window_s": "integer (measurement window)",
                "emitter": "string (component id)",
                "topic": "string (topic pattern)",
                "ack_rate": "float (0-1, successful pongs)",
                "rtt_p50": "float (median latency ms)",
                "rtt_p95": "float (95th percentile latency ms)",
                "jitter_ms": "float (latency std dev)",
                "loss_rate": "float (0-1, missing pongs)",
                "ordering_errors": "integer (out-of-order count)",
                "route_mismatch": "integer (wrong topic deliveries)",
                "last_ok_ts": "string (ISO timestamp of last success)"
            }
        },
        {
            "name": "health.link.alert",
            "direction": "broadcast",
            "description": "Change-point detected on link metrics (learned, not constants)",
            "content_schema": {
                "probe_id": "string? (optional probe that triggered)",
                "emitter": "string (component id)",
                "topic": "string (affected topic)",
                "signal": "enum (ack_rate_drop|latency_spike|loss_spike|route_error)",
                "evidence": "object (metric values + change point data)",
                "severity": "enum (low|medium|high|critical)"
            }
        },
        {
            "name": "health.compliance.snapshot",
            "direction": "broadcast",
            "description": "Validator outcomes per {emitter, topic} from membrane.reject analysis",
            "content_schema": {
                "window_s": "integer (measurement window)",
                "emitter": "string (component id)",
                "topic": "string (topic pattern)",
                "accept_rate": "float (0-1, accepted events)",
                "reject_rate": "float (0-1, rejected events)",
                "top_rejects": "array<{reason: string, count: integer}> (top 5 rejection reasons)",
                "spec_rev_mismatch": "integer (outdated spec.rev count)",
                "payload_cap_hits": "integer (oversized payload count)",
                "idempotent_replays": "integer (duplicate id count)"
            }
        },
        {
            "name": "health.compliance.alert",
            "direction": "broadcast",
            "description": "Change-point on rejection mix / spec drift (learned thresholds)",
            "content_schema": {
                "emitter": "string (component id)",
                "topic": "string (affected topic)",
                "signal": "enum (reject_spike|spec_drift|governance_hits|signature_failures)",
                "evidence": "object (reject stats + change point data)",
                "severity": "enum (low|medium|high|critical)"
            }
        }
    ]

    # Create namespace and governance
    namespace_query = """
    MERGE (ns:Topic_Namespace {pattern: 'ecosystem/{ecosystem_id}/org/{org_id}/health/*'})
    ON CREATE SET
        ns.description = 'Membrane-native health monitoring'

    MERGE (gp:Governance_Policy {name: 'health.namespace'})
    ON CREATE SET
        gp.max_payload_kb = 16,
        gp.rate_limit_per_component = 120,
        gp.rate_limit_window_seconds = 60,
        gp.allowed_emitters = ['component:tool.health.*']

    MERGE (gp)-[:GOVERNS]->(ns)

    RETURN ns.pattern AS namespace
    """

    result = r.execute_command("GRAPH.QUERY", graph_name, namespace_query)
    print(f"✅ Created namespace: ecosystem/{{ecosystem_id}}/org/{{org_id}}/health/*")

    # Create event schemas
    for schema_def in schemas:
        schema_query = f"""
        MERGE (ns:Topic_Namespace {{pattern: 'ecosystem/{{ecosystem_id}}/org/{{org_id}}/health/*'}})

        MERGE (es:Event_Schema {{name: $name}})
        ON CREATE SET
            es.direction = $direction,
            es.description = $description,
            es.content_schema = $content_schema

        MERGE (es)-[:MAPS_TO_TOPIC]->(ns)

        MERGE (env:Envelope_Schema {{name: 'membrane.envelope.v1'}})
        MERGE (es)-[:REQUIRES_ENVELOPE]->(env)

        MERGE (sig:Signature_Suite {{algorithm: 'ed25519'}})
        MERGE (es)-[:REQUIRES_SIG]->(sig)

        RETURN es.name AS schema_name
        """

        # Build parameterized query - escape quotes in schema
        schema_json = str(schema_def['content_schema']).replace("'", "\\'")

        params_query = schema_query.replace("$name", f"'{schema_def['name']}'")
        params_query = params_query.replace("$direction", f"'{schema_def['direction']}'")
        params_query = params_query.replace("$description", f"'{schema_def['description']}'")
        params_query = params_query.replace("$content_schema", f"'{schema_json}'")

        result = r.execute_command("GRAPH.QUERY", graph_name, params_query)
        schema_name = schema_def["name"]
        direction_emoji = "📥" if schema_def["direction"] == "inject" else "📤"
        print(f"  {direction_emoji} {schema_name}")

    print(f"\n✅ Ingested {len(schemas)} health event schemas into L4 protocol graph")
    print(f"   Namespace: ecosystem/{{ecosystem_id}}/org/{{org_id}}/health/*")
    print(f"   Governance: 16KB payload cap, 120 events/min per component")


if __name__ == "__main__":
    try:
        ingest_health_schemas()
    except Exception as e:
        print(f"❌ Error ingesting health schemas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
