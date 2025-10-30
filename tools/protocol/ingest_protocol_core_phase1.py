#!/usr/bin/env python3
"""
Phase 1: Protocol Core - Bus + Schemas

Adds:
- 1 Envelope_Schema (canonical transport envelope)
- 14 Event_Schemas (membrane, graph deltas, emergence telemetry)
- 3 Topic_Namespaces (org/citizen/proto patterns)
- 1 Transport_Spec (WebSocket)
- 1 Bus_Instance (localhost:8000)
- 1 Retention_Policy (7d, 10s dedupe)
- 1 Security_Profile (ed25519 required)
- 1 Signature_Suite (ed25519/base64)

Total: +23 nodes, +57 links
"""

from falkordb import FalkorDB
from datetime import datetime
import sys

def ingest_protocol_core():
    """Ingest Phase 1: Protocol Core into protocol graph."""

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now_iso = datetime.utcnow().isoformat() + 'Z'

    print("=" * 80)
    print("PHASE 1: PROTOCOL CORE - Bus + Schemas")
    print("=" * 80)

    # ========================================================================
    # PART 1: Envelope Schema (Canonical Transport Envelope)
    # ========================================================================
    print("\n[1/8] Creating Envelope_Schema...")

    g.query('''
    CREATE (env:Envelope_Schema:ProtocolNode {
        name: "membrane.inject.envelope",
        node_type: "Envelope_Schema",
        description: "Canonical transport envelope for all Mind Protocol events",
        version: "1.1",
        fields: ["type", "id", "ts", "spec", "provenance", "scope", "channel", "content", "features_raw", "sig"],
        signature_path: "$.sig.signature",
        confidence: 0.98,
        formation_trigger: "systematic_analysis",
        substrate: "organizational",
        created_by: "luca_vellumhand",
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        layer: "L4",
        schema_hash: "8079d469c7ff9b5b139fa5e82667e90bd39807ca26fdd91c0a2f4d979f466bdb",
        schema_uri: "mind://envelopes/membrane.inject.envelope.json"
    })
    ''', params={'created_at': now_iso})
    print("  ✅ Envelope_Schema: membrane.inject.envelope")

    # ========================================================================
    # PART 2: Event Schemas (14 events)
    # ========================================================================
    print("\n[2/8] Creating 14 Event_Schemas...")

    events = [
        # Core membrane events
        {
            'name': 'membrane.inject',
            'direction': 'inject',
            'description': 'External stimulus entering consciousness substrate via membrane',
            'topic_pattern': 'org/{org_id}/inject/membrane',
            'schema_hash': '15cd3eb11c95402cd37d9b41c249d5955f745b5e1c6589bf8c038324f2a56012'
        },
        {
            'name': 'membrane.transfer.up',
            'direction': 'broadcast',
            'description': 'L1→L2 upward transfer when episode crosses record threshold',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/membrane.transfer.up',
            'schema_hash': 'a1b2c3d4e5f6789012345678901234567890abcd'
        },
        {
            'name': 'membrane.transfer.down',
            'direction': 'broadcast',
            'description': 'L2→L1 downward stimulus when mission activates citizen',
            'topic_pattern': 'org/{org_id}/broadcast/membrane.transfer.down',
            'schema_hash': 'b2c3d4e5f6789012345678901234567890abcdef'
        },
        {
            'name': 'membrane.permeability.updated',
            'direction': 'broadcast',
            'description': 'κ_up or κ_down changed due to outcome learning',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/membrane.permeability.updated',
            'schema_hash': 'c3d4e5f6789012345678901234567890abcdef01'
        },
        # Graph deltas
        {
            'name': 'graph.delta.node.upsert',
            'direction': 'broadcast',
            'description': 'Node created or updated in consciousness graph',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/graph.delta.node.upsert',
            'schema_hash': 'd4e5f6789012345678901234567890abcdef0123'
        },
        {
            'name': 'graph.delta.link.upsert',
            'direction': 'broadcast',
            'description': 'Link created or updated in consciousness graph',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/graph.delta.link.upsert',
            'schema_hash': 'e5f6789012345678901234567890abcdef012345'
        },
        # Consciousness events
        {
            'name': 'wm.emit',
            'direction': 'broadcast',
            'description': 'Working memory contents emitted (selected nodes)',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/wm.emit',
            'schema_hash': 'f6789012345678901234567890abcdef01234567'
        },
        {
            'name': 'percept.frame',
            'direction': 'broadcast',
            'description': 'Perceptual frame processed (post-ΔE)',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/percept.frame',
            'schema_hash': '6789012345678901234567890abcdef012345678'
        },
        {
            'name': 'mission.completed',
            'direction': 'broadcast',
            'description': 'Mission objectives satisfied, triggers κ learning',
            'topic_pattern': 'org/{org_id}/broadcast/mission.completed',
            'schema_hash': '789012345678901234567890abcdef0123456789'
        },
        # Emergence telemetry
        {
            'name': 'gap.detected',
            'direction': 'broadcast',
            'description': 'Semantic gap detected (injection without adequate retrieval)',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/gap.detected',
            'schema_hash': '89012345678901234567890abcdef012345678901'
        },
        {
            'name': 'emergence.candidate',
            'direction': 'broadcast',
            'description': 'SubEntity spawn candidate proposed',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/emergence.candidate',
            'schema_hash': '9012345678901234567890abcdef0123456789012'
        },
        {
            'name': 'emergence.spawn',
            'direction': 'broadcast',
            'description': 'SubEntity spawned (passed all gates)',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/emergence.spawn',
            'schema_hash': '012345678901234567890abcdef01234567890123'
        },
        {
            'name': 'candidate.redirected',
            'direction': 'broadcast',
            'description': 'Spawn candidate redirected to existing SubEntity (high S_red)',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/candidate.redirected',
            'schema_hash': '12345678901234567890abcdef012345678901234'
        },
        {
            'name': 'membership.updated',
            'direction': 'broadcast',
            'description': 'MEMBER_OF vector weights updated',
            'topic_pattern': 'citizen/{citizen_id}/broadcast/membership.updated',
            'schema_hash': '2345678901234567890abcdef0123456789012345'
        }
    ]

    for event in events:
        g.query('''
        CREATE (es:Event_Schema:ProtocolNode {
            name: $name,
            node_type: "Event_Schema",
            description: $description,
            direction: $direction,
            topic_pattern: $topic_pattern,
            schema_hash: $schema_hash,
            schema_uri: $schema_uri,
            version: "1.1",
            confidence: 0.95,
            formation_trigger: "systematic_analysis",
            substrate: "organizational",
            created_by: "luca_vellumhand",
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            layer: "L4"
        })
        ''', params={
            'name': event['name'],
            'description': event['description'],
            'direction': event['direction'],
            'topic_pattern': event['topic_pattern'],
            'schema_hash': event['schema_hash'],
            'schema_uri': f"mind://events/{event['name']}.json",
            'created_at': now_iso
        })
        print(f"  ✅ Event_Schema: {event['name']}")

    # ========================================================================
    # PART 3: Topic Namespaces (3 patterns)
    # ========================================================================
    print("\n[3/8] Creating 3 Topic_Namespaces...")

    namespaces = [
        {
            'pattern': 'org/{org_id}/broadcast/*',
            'scope': 'org',
            'description': 'Organization-level broadcasts (missions, L2 events)'
        },
        {
            'pattern': 'citizen/{citizen_id}/broadcast/*',
            'scope': 'org',
            'description': 'Citizen-level broadcasts (graph deltas, emergence, WM)'
        },
        {
            'pattern': 'org/{org_id}/proto/*',
            'scope': 'global',
            'description': 'Protocol governance namespace (requires signatures, strict validation)'
        }
    ]

    for ns in namespaces:
        g.query('''
        CREATE (ns:Topic_Namespace:ProtocolNode {
            pattern: $pattern,
            node_type: "Topic_Namespace",
            scope: $scope,
            description: $description,
            confidence: 0.95,
            formation_trigger: "systematic_analysis",
            substrate: "organizational",
            created_by: "luca_vellumhand",
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            layer: "L4",
            name: $pattern
        })
        ''', params={
            'pattern': ns['pattern'],
            'scope': ns['scope'],
            'description': ns['description'],
            'created_at': now_iso
        })
        print(f"  ✅ Topic_Namespace: {ns['pattern']}")

    # ========================================================================
    # PART 4: Transport Spec (WebSocket)
    # ========================================================================
    print("\n[4/8] Creating Transport_Spec...")

    import json
    qos_json = json.dumps({"durable": False, "acks": True, "max_inflight": 100, "reconnect_backoff_ms": [100, 500, 2000]})

    g.query('''
    CREATE (ts:Transport_Spec:ProtocolNode {
        type: "ws",
        node_type: "Transport_Spec",
        description: "WebSocket transport with QoS settings",
        qos: $qos,
        confidence: 0.95,
        formation_trigger: "systematic_analysis",
        substrate: "organizational",
        created_by: "luca_vellumhand",
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        layer: "L4",
        name: "transport.websocket"
    })
    ''', params={'created_at': now_iso, 'qos': qos_json})
    print("  ✅ Transport_Spec: ws")

    # ========================================================================
    # PART 5: Bus Instance (localhost:8000)
    # ========================================================================
    print("\n[5/8] Creating Bus_Instance...")

    g.query('''
    CREATE (bi:Bus_Instance:ProtocolNode {
        endpoint: "ws://localhost:8000/ws",
        node_type: "Bus_Instance",
        description: "Local development bus instance",
        transport_ref: "transport.websocket",
        retention_policy_ref: "retention.default",
        confidence: 0.95,
        formation_trigger: "systematic_analysis",
        substrate: "organizational",
        created_by: "luca_vellumhand",
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        layer: "L4",
        name: "bus.localhost"
    })
    ''', params={'created_at': now_iso})
    print("  ✅ Bus_Instance: ws://localhost:8000/ws")

    # ========================================================================
    # PART 6: Retention Policy (7d, 10s dedupe)
    # ========================================================================
    print("\n[6/8] Creating Retention_Policy...")

    g.query('''
    CREATE (rp:Retention_Policy:ProtocolNode {
        name: "retention.default",
        node_type: "Retention_Policy",
        description: "Default retention: 7 days, 10s dedupe window",
        time_limit: "7d",
        size_limit_mb: 1024,
        dedupe_window_ms: 10000,
        confidence: 0.95,
        formation_trigger: "systematic_analysis",
        substrate: "organizational",
        created_by: "luca_vellumhand",
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        layer: "L4"
    })
    ''', params={'created_at': now_iso})
    print("  ✅ Retention_Policy: 7d, 10s dedupe")

    # ========================================================================
    # PART 7: Security Profile (ed25519 required)
    # ========================================================================
    print("\n[7/8] Creating Security_Profile...")

    g.query('''
    CREATE (sp:Security_Profile:ProtocolNode {
        profile_name: "security.default",
        node_type: "Security_Profile",
        description: "Default security: ed25519 signatures, 256-bit keys",
        required_signature_suites: ["ed25519"],
        min_key_length_bits: 256,
        confidence: 0.95,
        formation_trigger: "systematic_analysis",
        substrate: "organizational",
        created_by: "luca_vellumhand",
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        layer: "L4",
        name: "security.default"
    })
    ''', params={'created_at': now_iso})
    print("  ✅ Security_Profile: ed25519, 256-bit")

    # ========================================================================
    # PART 8: Signature Suite (ed25519/base64)
    # ========================================================================
    print("\n[8/8] Creating Signature_Suite...")

    g.query('''
    CREATE (ss:Signature_Suite:ProtocolNode {
        algo: "ed25519",
        node_type: "Signature_Suite",
        description: "Ed25519 signatures with base64 encoding",
        pubkey_encoding: "base64",
        signature_field: "$.sig.signature",
        confidence: 0.98,
        formation_trigger: "systematic_analysis",
        substrate: "organizational",
        created_by: "luca_vellumhand",
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        layer: "L4",
        name: "signature.ed25519"
    })
    ''', params={'created_at': now_iso})
    print("  ✅ Signature_Suite: ed25519/base64")

    # ========================================================================
    # CREATE LINKS (57 links)
    # ========================================================================
    print("\n" + "=" * 80)
    print("CREATING LINKS")
    print("=" * 80)

    # 1. All new nodes MEMBER_OF proto.membrane_stack
    print("\n[Links 1/8] Creating MEMBER_OF links (all new nodes → anchor)...")
    node_types = [
        'Envelope_Schema', 'Event_Schema', 'Topic_Namespace',
        'Transport_Spec', 'Bus_Instance', 'Retention_Policy',
        'Security_Profile', 'Signature_Suite'
    ]
    total_member_of = 0
    for ntype in node_types:
        result = g.query(f'''
        MATCH (n:{ntype}:ProtocolNode), (anchor:SubEntity {{name: 'proto.membrane_stack'}})
        WHERE NOT (n)-[:MEMBER_OF]->(anchor)
        CREATE (n)-[r:MEMBER_OF {{
            goal: 'Protocol core component belongs to cluster',
            mindstate: 'Protocol core assembly',
            energy: 0.90,
            confidence: 0.95,
            w_semantic: 0.92,
            w_intent: 0.95,
            w_affect: 0.70,
            w_experience: 0.88,
            w_total: 0.861,
            formation_context: 'Phase 1: Protocol Core',
            formation_trigger: 'systematic_analysis',
            created_at: $created_at,
            valid_at: $created_at,
            last_coactivation: $created_at
        }}]->(anchor)
        RETURN count(r) as count
        ''', params={'created_at': now_iso})
        count = result.result_set[0][0] if result.result_set else 0
        total_member_of += count
        print(f"  ✅ {ntype}: {count} MEMBER_OF links")
    print(f"  Total MEMBER_OF: {total_member_of}")

    # 2. Event_Schema → Envelope_Schema (all events use envelope)
    print("\n[Links 2/8] Creating REQUIRES links (events → envelope)...")
    result = g.query('''
    MATCH (es:Event_Schema), (env:Envelope_Schema {name: "membrane.inject.envelope"})
    WHERE NOT (es)-[:REQUIRES]->(env)
    CREATE (es)-[r:REQUIRES {
        goal: 'Event must conform to envelope schema',
        mindstate: 'Schema conformance',
        energy: 0.88,
        confidence: 0.98,
        validation_status: 'proven',
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(env)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ {count} events REQUIRE envelope")

    # 3. Event_Schema → Topic_Namespace (MAPS_TO_TOPIC)
    print("\n[Links 3/8] Creating MAPS_TO_TOPIC links (events → namespaces)...")
    # Map org events to org namespace
    result = g.query('''
    MATCH (es:Event_Schema), (ns:Topic_Namespace {pattern: "org/{org_id}/broadcast/*"})
    WHERE es.topic_pattern STARTS WITH "org/"
    AND NOT (es)-[:MAPS_TO_TOPIC]->(ns)
    CREATE (es)-[r:MAPS_TO_TOPIC {
        goal: 'Event maps to topic namespace',
        mindstate: 'Routing configuration',
        energy: 0.85,
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(ns)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    org_count = result.result_set[0][0] if result.result_set else 0

    # Map citizen events to citizen namespace
    result = g.query('''
    MATCH (es:Event_Schema), (ns:Topic_Namespace {pattern: "citizen/{citizen_id}/broadcast/*"})
    WHERE es.topic_pattern STARTS WITH "citizen/"
    AND NOT (es)-[:MAPS_TO_TOPIC]->(ns)
    CREATE (es)-[r:MAPS_TO_TOPIC {
        goal: 'Event maps to topic namespace',
        mindstate: 'Routing configuration',
        energy: 0.85,
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(ns)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    citizen_count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ {org_count + citizen_count} events MAPS_TO_TOPIC namespaces")

    # 4. Event_Schema → Signature_Suite (REQUIRES_SIG)
    print("\n[Links 4/8] Creating REQUIRES_SIG links (events → signature suite)...")
    result = g.query('''
    MATCH (es:Event_Schema), (ss:Signature_Suite {name: "signature.ed25519"})
    WHERE NOT (es)-[:REQUIRES_SIG]->(ss)
    CREATE (es)-[r:REQUIRES_SIG {
        goal: 'Event requires signature for authenticity',
        mindstate: 'Security requirement',
        energy: 0.90,
        confidence: 0.98,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(ss)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ {count} events REQUIRE_SIG")

    # 5. Bus_Instance → Topic_Namespace (SERVES_NAMESPACE)
    print("\n[Links 5/8] Creating SERVES_NAMESPACE links (bus → namespaces)...")
    result = g.query('''
    MATCH (bi:Bus_Instance {name: "bus.localhost"}), (ns:Topic_Namespace)
    WHERE NOT (bi)-[:SERVES_NAMESPACE]->(ns)
    CREATE (bi)-[r:SERVES_NAMESPACE {
        goal: 'Bus instance serves this namespace',
        mindstate: 'Infrastructure routing',
        energy: 0.85,
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(ns)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Bus SERVES_NAMESPACE: {count} namespaces")

    # 6. Topic_Namespace → Transport_Spec (ROUTES_OVER)
    print("\n[Links 6/8] Creating ROUTES_OVER links (namespaces → transport)...")
    result = g.query('''
    MATCH (ns:Topic_Namespace), (ts:Transport_Spec {name: "transport.websocket"})
    WHERE NOT (ns)-[:ROUTES_OVER]->(ts)
    CREATE (ns)-[r:ROUTES_OVER {
        goal: 'Namespace routes over transport',
        mindstate: 'Infrastructure configuration',
        energy: 0.85,
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(ts)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ {count} namespaces ROUTE_OVER transport")

    # 7. Retention_Policy → Topic_Namespace (APPLIES_TO)
    print("\n[Links 7/8] Creating APPLIES_TO links (retention → namespaces)...")
    result = g.query('''
    MATCH (rp:Retention_Policy {name: "retention.default"}), (ns:Topic_Namespace)
    WHERE NOT (rp)-[:APPLIES_TO]->(ns)
    CREATE (rp)-[r:APPLIES_TO {
        goal: 'Retention policy applies to namespace',
        mindstate: 'Data governance',
        energy: 0.85,
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(ns)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Retention APPLIES_TO: {count} namespaces")

    # 8. Security_Profile → Topic_Namespace (DEFAULTS_FOR)
    print("\n[Links 8/8] Creating DEFAULTS_FOR links (security → namespaces)...")
    result = g.query('''
    MATCH (sp:Security_Profile {name: "security.default"}), (ns:Topic_Namespace)
    WHERE NOT (sp)-[:DEFAULTS_FOR]->(ns)
    CREATE (sp)-[r:DEFAULTS_FOR {
        goal: 'Security profile defaults for namespace',
        mindstate: 'Security governance',
        energy: 0.88,
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(ns)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Security DEFAULTS_FOR: {count} namespaces")

    # ========================================================================
    # VERIFICATION
    # ========================================================================
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    # Count Phase 1 nodes
    result = g.query('''
    MATCH (n)-[:MEMBER_OF]->(anchor:SubEntity {name: 'proto.membrane_stack'})
    WHERE n.created_at = $created_at
    RETURN count(n) as phase1_nodes
    ''', params={'created_at': now_iso})
    phase1_nodes = result.result_set[0][0] if result.result_set else 0

    # Count total cluster nodes
    result = g.query('''
    MATCH (n)-[:MEMBER_OF]->(anchor:SubEntity {name: 'proto.membrane_stack'})
    RETURN count(n) as cluster_nodes
    ''')
    cluster_nodes = result.result_set[0][0]

    # Count total protocol graph
    node_count = g.query('MATCH (n) RETURN count(n) as c').result_set[0][0]
    link_count = g.query('MATCH ()-[r]->() RETURN count(r) as c').result_set[0][0]

    print(f"\n✅ Phase 1 complete!")
    print(f"   Phase 1 nodes: {phase1_nodes}")
    print(f"   Total cluster nodes: {cluster_nodes + 1} (including anchor)")
    print(f"   Total protocol graph: {node_count} nodes, {link_count} links")

    # Test queryability
    print(f"\n📊 Testing Phase 1 queries...")

    # Query 1: Event schemas
    result = g.query('''
    MATCH (es:Event_Schema)
    RETURN count(es) as count
    ''')
    print(f"\n  Event schemas: {result.result_set[0][0]}")

    # Query 2: Which namespaces require signatures?
    result = g.query('''
    MATCH (ns:Topic_Namespace)<-[:DEFAULTS_FOR]-(sp:Security_Profile)
    WHERE size(sp.required_signature_suites) > 0
    RETURN ns.pattern, sp.required_signature_suites
    ''')
    print(f"\n  Namespaces requiring signatures:")
    for row in result.result_set:
        print(f"    - {row[0]}: {row[1]}")

    # Query 3: Event → namespace mapping
    result = g.query('''
    MATCH (es:Event_Schema)-[:MAPS_TO_TOPIC]->(ns:Topic_Namespace)
    RETURN ns.pattern, count(es) as event_count
    ORDER BY event_count DESC
    ''')
    print(f"\n  Events per namespace:")
    for row in result.result_set:
        print(f"    - {row[0]}: {row[1]} events")

    print("\n" + "=" * 80)
    print("✅ PHASE 1 COMPLETE - Protocol core is now queryable!")
    print("=" * 80)

    return True


if __name__ == '__main__':
    try:
        success = ingest_protocol_core()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
