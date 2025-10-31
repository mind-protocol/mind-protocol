#!/usr/bin/env python3
"""
L4 Protocol Ingestion: Consciousness Telemetry Policies (Hybrid Option C)

Adds generic telemetry Event_Schema nodes that consciousness infrastructure
emits to, using wildcard namespaces for flexible mapping.

Architecture: 5 generic schemas map to 6 wildcard namespaces:
- telemetry.state.* (STRICT - SEA required)
- telemetry.detection.* (STRICT - SEA required)
- telemetry.series.* (FLEX - signed only)
- telemetry.lifecycle.* (FLEX - signed only)
- telemetry.activation.* (FLEX - signed only)
- telemetry.frame.* (FLEX - signed only)

This unblocks consciousness engines to emit telemetry with proper L4 governance.

Author: Ada Bridgekeeper (policy design) + Nicolas Reynolds (Cypher seeds)
Date: 2025-10-31
Ticket: L4-001
"""

import sys
import redis

# Topic namespaces (wildcard patterns for flexible topic mapping)
TELEMETRY_NAMESPACES = [
    {
        "name": "telemetry.state",
        "pattern": "telemetry.state.*",
        "description": "SubEntity state, identity snapshots (STRICT - SEA required)"
    },
    {
        "name": "telemetry.detection",
        "pattern": "telemetry.detection.*",
        "description": "Mode detection, subentity detection (STRICT - SEA required)"
    },
    {
        "name": "telemetry.series",
        "pattern": "telemetry.series.*",
        "description": "Time series metrics (weight, energy, etc.) (FLEX - signed only)"
    },
    {
        "name": "telemetry.lifecycle",
        "pattern": "telemetry.lifecycle.*",
        "description": "Lifecycle events (start, stop, restart) (FLEX - signed only)"
    },
    {
        "name": "telemetry.activation",
        "pattern": "telemetry.activation.*",
        "description": "Activation events (node/link activated) (FLEX - signed only)"
    },
    {
        "name": "telemetry.frame",
        "pattern": "telemetry.frame.*",
        "description": "Frame execution telemetry (FLEX - signed only)"
    }
]

# Generic telemetry event schemas (5 schemas map to 6 namespaces)
TELEMETRY_SCHEMAS = [
    {
        "schema_uri": "l4://schemas/telemetry.state/1.0.0.json",
        "name": "telemetry.state",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "telemetry.state.*",
        "namespace": "telemetry.state",
        "summary": "Generic state snapshot (subentity metrics, WM snapshot, entity context)",
        "sea_required": True,  # STRICT policy
        "cps": False,
        "concrete_topics": [
            "subentity.metrics.emit",
            "subentity.wm.snapshot",
            "entity.context.snapshot"
        ]
    },
    {
        "schema_uri": "l4://schemas/telemetry.detection/1.0.0.json",
        "name": "telemetry.detection",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "telemetry.detection.*",
        "namespace": "telemetry.detection",
        "summary": "Generic detection event (mode detection, subentity detection)",
        "sea_required": True,  # STRICT policy
        "cps": False,
        "concrete_topics": [
            "mode.detection.emit",
            "subentity.detection.emit"
        ]
    },
    {
        "schema_uri": "l4://schemas/telemetry.series/1.0.0.json",
        "name": "telemetry.series",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "telemetry.series.*",
        "namespace": "telemetry.series",
        "summary": "Generic time series metrics (weight learning, energy delta, activation spread)",
        "sea_required": False,  # FLEX policy
        "cps": False,
        "concrete_topics": [
            "weight.learning.trace",
            "energy.delta.emit",
            "activation.spread.trace"
        ]
    },
    {
        "schema_uri": "l4://schemas/telemetry.lifecycle/1.0.0.json",
        "name": "telemetry.lifecycle",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "telemetry.lifecycle.*",
        "namespace": "telemetry.lifecycle",
        "summary": "Generic lifecycle event (engine start/stop, service restart)",
        "sea_required": False,  # FLEX policy
        "cps": False,
        "concrete_topics": [
            "engine.start",
            "engine.stop",
            "service.restart"
        ]
    },
    {
        "schema_uri": "l4://schemas/telemetry.activation/1.0.0.json",
        "name": "telemetry.activation",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "telemetry.activation.*",
        "namespace": "telemetry.activation",
        "summary": "Generic activation event (node activated, link activated)",
        "sea_required": False,  # FLEX policy
        "cps": False,
        "concrete_topics": [
            "node.activated",
            "link.activated"
        ]
    }
]

# Governance policies (STRICT vs FLEX)
GOVERNANCE_POLICIES = [
    {
        "policy_id": "POL_TELEM_STRICT_V1",
        "name": "Strict Telemetry Policy",
        "description": "SEA required for identity-bearing state & detections",
        "governs_namespaces": ["telemetry.state", "telemetry.detection"]
    },
    {
        "policy_id": "POL_TELEM_FLEX_V1",
        "name": "Flexible Telemetry Policy",
        "description": "Signature only; no SEA required",
        "governs_namespaces": ["telemetry.series", "telemetry.lifecycle", "telemetry.activation", "telemetry.frame"]
    }
]

def ingest_telemetry_policies():
    """Ingest consciousness telemetry policies to L4 protocol graph."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    graph_name = "protocol"

    print("📊 Consciousness Telemetry Policies Ingestion (Hybrid Option C)")
    print("=" * 70)
    print()

    # 0. Get/create signature suite and envelope schema (if not exist)
    print("0️⃣  Ensuring Signature Suite and Envelope Schema exist...")
    sig_id = "protocol/Signature_Suite/SIG_ED25519_V1"
    env_id = "protocol/Envelope_Schema/ENV_STANDARD_V1"

    query = f"""
    MERGE (sig:ProtocolNode {{id: '{sig_id}'}})
    ON CREATE SET
        sig.suite_id = 'SIG_ED25519_V1',
        sig.algo = 'ed25519',
        sig.type_name = 'Signature_Suite'

    MERGE (env:ProtocolNode {{id: '{env_id}'}})
    ON CREATE SET
        env.schema_uri = 'l4://schemas/envelopes/ENV_STANDARD_V1.json',
        env.version = '1.0.0',
        env.name = 'ENV_STANDARD_V1',
        env.type_name = 'Envelope_Schema'
    WITH env, sig
    MERGE (env)-[:REQUIRES_SIG]->(sig)
    """
    r.execute_command("GRAPH.QUERY", graph_name, query)
    print(f"  ✓ SIG_ED25519_V1 (ed25519)")
    print(f"  ✓ ENV_STANDARD_V1")
    print()

    # 1. Create Topic_Namespace nodes (wildcard patterns)
    print("1️⃣  Creating Topic Namespaces (wildcard patterns)...")
    for ns in TELEMETRY_NAMESPACES:
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
        policy = "STRICT" if "STRICT" in ns["description"] else "FLEX"
        print(f"  ✓ {ns['pattern']:<35} - {policy}")
    print()

    # 2. Create/verify Schema Bundle (BUNDLE_TELEMETRY_1_0_0)
    print("2️⃣  Creating Schema Bundle...")
    bundle_id = "protocol/Schema_Bundle/BUNDLE_TELEMETRY_1_0_0"
    reg_id = "protocol/Subentity/schema-registry"

    query = f"""
    MERGE (reg:ProtocolNode {{id: '{reg_id}'}})
    ON CREATE SET
        reg.subsystem_id = 'schema-registry',
        reg.type_name = 'Subentity'

    MERGE (b:ProtocolNode {{id: '{bundle_id}'}})
    ON CREATE SET
        b.bundle_id = 'BUNDLE_TELEMETRY_1_0_0',
        b.semver = '1.0.0',
        b.status = 'active',
        b.type_name = 'Schema_Bundle'
    WITH reg, b
    MERGE (reg)-[:GOVERNS]->(b)
    """
    r.execute_command("GRAPH.QUERY", graph_name, query)
    print(f"  ✓ BUNDLE_TELEMETRY_1_0_0 (active)")
    print()

    # 3. Create Event_Schema nodes and wire relationships
    print("3️⃣  Creating Generic Event Schemas...")
    for schema in TELEMETRY_SCHEMAS:
        schema_id = f"protocol/Event_Schema/{schema['name']}"
        namespace_id = f"protocol/Topic_Namespace/{schema['namespace']}"

        query = f"""
        MATCH (b:ProtocolNode {{id: '{bundle_id}'}})
        MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
        MATCH (sig:ProtocolNode {{id: '{sig_id}'}})

        MERGE (es:ProtocolNode {{id: '{schema_id}'}})
        ON CREATE SET
            es.name = '{schema["name"]}',
            es.schema_uri = '{schema["schema_uri"]}',
            es.version = '{schema["version"]}',
            es.type_name = 'Event_Schema',
            es.direction = '{schema["direction"]}',
            es.topic_pattern = '{schema["topic_pattern"]}',
            es.summary = '{schema["summary"]}',
            es.requires_sig_suite = 'SIG_ED25519_V1',
            es.sea_required = {str(schema["sea_required"]).lower()},
            es.cps = {str(schema["cps"]).lower()},
            es.schema_hash = 'sha256:placeholder'
        WITH es, b, ns, sig
        MERGE (b)-[:PUBLISHES_SCHEMA]->(es)
        MERGE (es)-[:MAPS_TO_TOPIC]->(ns)
        MERGE (es)-[:REQUIRES_SIG]->(sig)
        RETURN es.id
        """
        r.execute_command("GRAPH.QUERY", graph_name, query)

        policy = "🔐 STRICT" if schema["sea_required"] else "📝 FLEX  "
        concrete_count = len(schema["concrete_topics"])
        print(f"  {policy} {schema['name']:<30} → {concrete_count} concrete topics")

    print()

    # 4. Create Governance_Policy nodes and link to namespaces
    print("4️⃣  Creating Governance Policies...")
    for policy in GOVERNANCE_POLICIES:
        policy_id = f"protocol/Governance_Policy/{policy['policy_id']}"

        # Create policy node
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

        # Link policy to governed namespaces
        for ns_name in policy["governs_namespaces"]:
            namespace_id = f"protocol/Topic_Namespace/{ns_name}"
            query = f"""
            MATCH (gp:ProtocolNode {{id: '{policy_id}'}})
            MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
            MERGE (gp)-[:GOVERNS]->(ns)
            """
            r.execute_command("GRAPH.QUERY", graph_name, query)

        policy_type = "STRICT" if "STRICT" in policy["policy_id"] else "FLEX"
        ns_count = len(policy["governs_namespaces"])
        print(f"  ✓ {policy['policy_id']:<30} - {policy_type} ({ns_count} namespaces)")

    print()
    print("=" * 70)
    print(f"✅ Ingested consciousness telemetry policies")
    print()
    print("Summary:")
    print(f"  - 6 Topic_Namespace nodes (wildcard patterns)")
    print(f"  - 5 Event_Schema nodes (generic schemas)")
    print(f"  - 2 Governance_Policy nodes (STRICT vs FLEX)")
    print(f"  - 1 Schema_Bundle (BUNDLE_TELEMETRY_1_0_0, active)")
    print()
    print("Policy Breakdown:")
    print(f"  🔐 STRICT (SEA required): telemetry.state.*, telemetry.detection.*")
    print(f"  📝 FLEX (signed only):    telemetry.series.*, telemetry.lifecycle.*,")
    print(f"                           telemetry.activation.*, telemetry.frame.*")
    print()
    print("Concrete Topic Mappings (examples):")
    print(f"  - subentity.metrics.emit    → telemetry.state@1.0.0 (STRICT)")
    print(f"  - mode.detection.emit       → telemetry.detection@1.0.0 (STRICT)")
    print(f"  - weight.learning.trace     → telemetry.series@1.0.0 (FLEX)")
    print(f"  - engine.start              → telemetry.lifecycle@1.0.0 (FLEX)")
    print(f"  - node.activated            → telemetry.activation@1.0.0 (FLEX)")
    print()
    print("Next Steps:")
    print("  1. Re-export L4 registry: python tools/protocol/export_l4_public.py")
    print("  2. Run mp-lint: python tools/mp_lint/cli.py")
    print("  3. Expected: R-001 ≈ 0 (schemas exist)")
    print("  4. Expected: R-005 on STRICT topics without attestation_ref")
    print("  5. SafeBroadcaster should emit telemetry topics cleanly")

if __name__ == "__main__":
    try:
        ingest_telemetry_policies()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
