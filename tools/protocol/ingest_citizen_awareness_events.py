#!/usr/bin/env python3
"""
L4 Protocol Ingestion: Citizen Awareness Events (Phase 0 MVP)

Adds citizen.* event schemas to protocol graph for Wall/dashboard visibility.
Includes: presence, status, messaging, and email bridge.
Note: handoff.* events moved to L2 org-local law (not global L4).

Usage:
    python3 tools/protocol/ingest_citizen_awareness_events.py
"""

import sys
import redis


CITIZEN_EVENTS = [
    # Presence - heartbeat for liveness
    {
        "name": "presence.beacon",
        "direction": "broadcast",
        "namespace": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/presence",
        "description": "60s heartbeat for citizen liveness; TTL 90-120s",
        "max_payload_kb": 1,
        "rate_limit_per_hour": 120
    },
    # Status
    {
        "name": "status.activity.emit",
        "direction": "broadcast",
        "namespace": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/status",
        "description": "Current working context (mission, files, note)",
        "max_payload_kb": 4,
        "rate_limit_per_hour": 60
    },
    # Messaging
    {
        "name": "message.thread",
        "direction": "inject",
        "namespace": "ecosystem/{ecosystem_id}/org/{org_id}/message/thread",
        "description": "Thread initialization or continuation",
        "max_payload_kb": 2,
        "rate_limit_per_hour": 300
    },
    {
        "name": "message.direct",
        "direction": "inject",
        "namespace": "ecosystem/{ecosystem_id}/org/{org_id}/message/direct",
        "description": "Single message within thread",
        "max_payload_kb": 4,
        "rate_limit_per_hour": 600
    },
    # Email bridge
    {
        "name": "bridge.email.inbound",
        "direction": "inject",
        "namespace": "ecosystem/{ecosystem_id}/org/{org_id}/bridge/email/in",
        "description": "Normalized email to message.thread",
        "max_payload_kb": 8,
        "rate_limit_per_hour": 300
    },
    {
        "name": "bridge.email.outbound",
        "direction": "broadcast",
        "namespace": "ecosystem/{ecosystem_id}/org/{org_id}/bridge/email/out",
        "description": "message.thread to SMTP",
        "max_payload_kb": 4,
        "rate_limit_per_hour": 300
    }
]


def ingest_citizen_events():
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    graph_name = "protocol"

    print("👥 Citizen Awareness Events (Phase 0 MVP)")
    print(f"   Events to add: {len(CITIZEN_EVENTS)}\n")

    for event_def in CITIZEN_EVENTS:
        namespace = event_def["namespace"]
        
        query = f"""
        MERGE (ns:Topic_Namespace {{pattern: '{namespace}'}})
        MERGE (gp:Governance_Policy {{name: 'policy.{event_def["name"]}'}})
        ON CREATE SET
            gp.max_payload_kb = {event_def["max_payload_kb"]},
            gp.rate_limit_per_hour = {event_def["rate_limit_per_hour"]}
        MERGE (gp)-[:GOVERNS]->(ns)
        
        MERGE (es:Event_Schema {{name: '{event_def["name"]}'}})
        ON CREATE SET
            es.direction = '{event_def["direction"]}',
            es.description = '{event_def["description"]}'
        MERGE (es)-[:MAPS_TO_TOPIC]->(ns)
        
        MERGE (env:Envelope_Schema {{name: 'membrane.envelope.v1'}})
        MERGE (es)-[:REQUIRES_ENVELOPE]->(env)
        
        RETURN es.name
        """
        
        r.execute_command("GRAPH.QUERY", graph_name, query)
        emoji = "📥" if event_def["direction"] == "inject" else "📤"
        print(f"  {emoji} {event_def['name']:<30} ({event_def['max_payload_kb']}KB, {event_def['rate_limit_per_hour']}/hr)")

    print(f"\n✅ Ingested {len(CITIZEN_EVENTS)} citizen awareness schemas")
    print("   Phase 0: presence + status + messaging + email bridge")
    print("   Note: handoff.* moved to L2 org-local law (not global L4)")


if __name__ == "__main__":
    try:
        ingest_citizen_events()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
