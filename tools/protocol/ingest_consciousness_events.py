#!/usr/bin/env python3
"""
L4 Protocol Ingestion: Consciousness Events

Adds Event_Schema for consciousness infrastructure:
- graph.delta.node.upsert - Graph node mutations
- graph.delta.link.upsert - Graph edge mutations
- subentity.snapshot - SubEntity state snapshots (SEA required)
- presence.beacon - Liveness/status heartbeats

These schemas unblock SafeBroadcaster validation for consciousness engines.
"""

import sys
import redis

# Topic namespaces
TOPIC_NAMESPACES = [
    {
        "name": "graph.delta",
        "pattern": "graph.delta.*",
        "description": "Low-risk internal graph mutations (L2/L1 observability)"
    },
    {
        "name": "subentity",
        "pattern": "subentity.*",
        "description": "SubEntity identity and phenomenology state (high-stakes)"
    },
    {
        "name": "presence",
        "pattern": "presence.*",
        "description": "Liveness and status beacons (low-risk)"
    }
]

# Signature suite
SIGNATURE_SUITE = {
    "suite_id": "SIG_ED25519_V1",
    "algo": "ed25519",
    "description": "Ed25519 signature verification for consciousness events"
}

# Governance policies
GOVERNANCE_POLICIES = [
    {
        "policy_id": "POL_CONS_TELEMETRY_V1",
        "name": "Consciousness Telemetry Policy",
        "description": "Must be signed; SEA not required; CPS not applicable",
        "governs_topics": ["graph.delta", "presence"]
    },
    {
        "policy_id": "POL_SUBENTITY_STATE_V1",
        "name": "SubEntity State Policy",
        "description": "Must be signed; SEA required (fresh attestation_ref); CPS not applicable",
        "governs_topics": ["subentity"]
    }
]

# Event schemas
CONSCIOUSNESS_EVENTS = [
    {
        "schema_uri": "l4://schemas/graph.delta.node.upsert/1.0.0.json",
        "name": "graph.delta.node.upsert",
        "version": "1.0.0",
        "direction": "inject",
        "topic": "graph.delta.node.upsert",
        "topic_namespace": "graph.delta",
        "summary": "Graph node mutation (create/update)",
        "requires_sig_suite": "SIG_ED25519_V1",
        "sea_required": False,
        "cps": False,
        "json_schema": {
            "type": "object",
            "required": ["node_id", "labels", "props"],
            "properties": {
                "node_id": {"type": "string"},
                "labels": {"type": "array", "items": {"type": "string"}},
                "props": {"type": "object"},
                "merge_keys": {"type": "array", "items": {"type": "string"}}
            },
            "additionalProperties": False
        }
    },
    {
        "schema_uri": "l4://schemas/graph.delta.link.upsert/1.0.0.json",
        "name": "graph.delta.link.upsert",
        "version": "1.0.0",
        "direction": "inject",
        "topic": "graph.delta.link.upsert",
        "topic_namespace": "graph.delta",
        "summary": "Graph edge mutation (create/update relationship)",
        "requires_sig_suite": "SIG_ED25519_V1",
        "sea_required": False,
        "cps": False,
        "json_schema": {
            "type": "object",
            "required": ["from_id", "to_id", "rel_type", "props"],
            "properties": {
                "from_id": {"type": "string"},
                "to_id": {"type": "string"},
                "rel_type": {"type": "string"},
                "props": {"type": "object"},
                "merge_keys": {"type": "array", "items": {"type": "string"}}
            },
            "additionalProperties": False
        }
    },
    {
        "schema_uri": "l4://schemas/subentity.snapshot/1.0.0.json",
        "name": "subentity.snapshot",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic": "subentity.snapshot",
        "topic_namespace": "subentity",
        "summary": "SubEntity state snapshot with metrics (SEA required)",
        "requires_sig_suite": "SIG_ED25519_V1",
        "sea_required": True,  # HIGH-STAKES: Requires attestation_ref
        "cps": False,
        "json_schema": {
            "type": "object",
            "required": ["citizen_id", "subentity_id", "metrics", "window"],
            "properties": {
                "citizen_id": {"type": "string"},
                "subentity_id": {"type": "string"},
                "metrics": {
                    "type": "object",
                    "required": ["weight", "energy", "stability", "volatility", "formation_quality"],
                    "properties": {
                        "weight": {"type": "number"},
                        "energy": {"type": "number"},
                        "stability": {"type": "number"},
                        "volatility": {"type": "number"},
                        "formation_quality": {"type": "number"}
                    }
                },
                "window": {
                    "type": "object",
                    "required": ["start_ts", "end_ts"],
                    "properties": {
                        "start_ts": {"type": "integer"},
                        "end_ts": {"type": "integer"}
                    }
                },
                "wm_digest": {"type": "string"}
            },
            "additionalProperties": False
        }
    },
    {
        "schema_uri": "l4://schemas/presence.beacon/1.0.0.json",
        "name": "presence.beacon",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic": "presence.beacon",
        "topic_namespace": "presence",
        "summary": "Liveness/status heartbeat (60s interval, TTL 90-120s)",
        "requires_sig_suite": "SIG_ED25519_V1",
        "sea_required": False,
        "cps": False,
        "json_schema": {
            "type": "object",
            "required": ["agent_id", "citizen_id", "status", "ts"],
            "properties": {
                "agent_id": {"type": "string"},
                "citizen_id": {"type": "string"},
                "status": {"type": "string", "enum": ["online", "busy", "idle", "offline"]},
                "ts": {"type": "integer"},
                "details": {"type": "object"}
            },
            "additionalProperties": False
        }
    }
]

def ingest_consciousness_events():
    """Ingest consciousness event schemas to L4 protocol graph."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    graph_name = "protocol"

    print("🧠 Consciousness Events Ingestion")
    print("=" * 60)
    print()

    # 1. Create Topic_Namespace nodes
    print("1️⃣  Creating Topic Namespaces...")
    for ns in TOPIC_NAMESPACES:
        namespace_id = f"protocol/Topic_Namespace/{ns['name']}"
        query = f"""
        MERGE (ns:ProtocolNode {{id: '{namespace_id}'}})
        ON CREATE SET
            ns.pattern = '{ns["pattern"]}',
            ns.type_name = 'Topic_Namespace',
            ns.description = '{ns["description"]}'
        RETURN ns.id
        """
        r.execute_command("GRAPH.QUERY", graph_name, query)
        print(f"  ✓ {ns['pattern']:<30} - {ns['description']}")
    print()

    # 2. Create Signature_Suite
    print("2️⃣  Creating Signature Suite...")
    sig_id = f"protocol/Signature_Suite/{SIGNATURE_SUITE['suite_id']}"
    query = f"""
    MERGE (sig:ProtocolNode {{id: '{sig_id}'}})
    ON CREATE SET
        sig.suite_id = '{SIGNATURE_SUITE["suite_id"]}',
        sig.algo = '{SIGNATURE_SUITE["algo"]}',
        sig.type_name = 'Signature_Suite',
        sig.description = '{SIGNATURE_SUITE["description"]}'
    RETURN sig.id
    """
    r.execute_command("GRAPH.QUERY", graph_name, query)
    print(f"  ✓ {SIGNATURE_SUITE['suite_id']} ({SIGNATURE_SUITE['algo']})")
    print()

    # 3. Create Governance_Policy nodes
    print("3️⃣  Creating Governance Policies...")
    for policy in GOVERNANCE_POLICIES:
        policy_id = f"protocol/Governance_Policy/{policy['policy_id']}"
        query = f"""
        MERGE (gp:ProtocolNode {{id: '{policy_id}'}})
        ON CREATE SET
            gp.policy_id = '{policy["policy_id"]}',
            gp.name = '{policy["name"]}',
            gp.type_name = 'Governance_Policy',
            gp.description = '{policy["description"]}'
        RETURN gp.id
        """
        r.execute_command("GRAPH.QUERY", graph_name, query)
        print(f"  ✓ {policy['policy_id']:<30} - {policy['name']}")

        # Link policy to topics it governs
        for topic_name in policy["governs_topics"]:
            # Find topic namespace by name (not pattern)
            topic_ns = next((t for t in TOPIC_NAMESPACES if t["name"] == topic_name), None)
            if topic_ns:
                namespace_id = f"protocol/Topic_Namespace/{topic_name}"
                query = f"""
                MATCH (gp:ProtocolNode {{id: '{policy_id}'}})
                MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
                MERGE (gp)-[:GOVERNS]->(ns)
                """
                r.execute_command("GRAPH.QUERY", graph_name, query)
    print()

    # 4. Create Event_Schema nodes and relationships
    print("4️⃣  Creating Event Schemas...")
    for event in CONSCIOUSNESS_EVENTS:
        import json

        event_id = f"protocol/Event_Schema/{event['name']}"
        namespace_id = f"protocol/Topic_Namespace/{event['topic_namespace']}"

        # Escape single quotes in JSON schema
        json_schema_str = json.dumps(event["json_schema"]).replace("'", "\\'")

        # Create Event_Schema node with relationships
        query = f"""
        MERGE (es:ProtocolNode {{id: '{event_id}'}})
        ON CREATE SET
            es.name = '{event["name"]}',
            es.schema_uri = '{event["schema_uri"]}',
            es.version = '{event["version"]}',
            es.type_name = 'Event_Schema',
            es.direction = '{event["direction"]}',
            es.topic_pattern = '{event["topic"]}',
            es.summary = '{event["summary"]}',
            es.requires_sig_suite = '{event["requires_sig_suite"]}',
            es.sea_required = {str(event["sea_required"]).lower()},
            es.cps = {str(event["cps"]).lower()},
            es.json_schema = '{json_schema_str}',
            es.schema_hash = 'sha256:placeholder'
        WITH es
        MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
        MERGE (es)-[:MAPS_TO_TOPIC]->(ns)
        WITH es
        MATCH (sig:ProtocolNode {{id: '{sig_id}'}})
        MERGE (es)-[:REQUIRES_SIG]->(sig)
        RETURN es.id
        """
        r.execute_command("GRAPH.QUERY", graph_name, query)

        # Emoji based on stakes
        emoji = "🔐" if event["sea_required"] else "📝"
        sea_marker = " (SEA REQUIRED)" if event["sea_required"] else ""
        print(f"  {emoji} {event['name']:<35} - {event['direction']:>9}{sea_marker}")

    print()
    print("=" * 60)
    print(f"✅ Ingested {len(CONSCIOUSNESS_EVENTS)} consciousness event schemas")
    print()
    print("Schema Summary:")
    print(f"  - graph.delta.node.upsert    : Signed, SEA not required")
    print(f"  - graph.delta.link.upsert    : Signed, SEA not required")
    print(f"  - subentity.snapshot         : Signed, SEA REQUIRED (high-stakes)")
    print(f"  - presence.beacon            : Signed, SEA not required")
    print()
    print("Next Steps:")
    print("  1. Re-export L4 registry: python tools/protocol/export_l4_public.py")
    print("  2. Update .mp-lint.yaml: Add 'subentity.snapshot' to high_stakes_topics")
    print("  3. Verify schemas in export: grep 'subentity.snapshot' build/l4_public_registry.json")
    print("  4. Rerun SafeBroadcaster: Should go green on consciousness events")

if __name__ == "__main__":
    try:
        ingest_consciousness_events()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
