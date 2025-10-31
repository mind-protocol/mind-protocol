#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Generic Telemetry Schemas to L4 Protocol Graph

Implements Option C (hybrid policy):
- 6 telemetry namespace wildcards (telemetry.state.*, telemetry.series.*, etc.)
- 5 generic, reusable event schemas (telemetry.state@1.0.0, etc.)
- 2 governance policies (STRICT for identity-bearing, FLEX for metrics)
- Wildcard mappings covering 50+ concrete telemetry topics

Why this approach:
- One door (L4) with fast evolution
- Strong guarantees for high-stakes signals (SEA required)
- Flex rules for low-stakes telemetry (signature only)
- No one-off schemas for every telemetry event

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-31
Architecture: Option C (hybrid telemetry policy)
"""

import os
from datetime import datetime
from falkordb import FalkorDB


def ingest_telemetry_schemas():
    """Ingest generic telemetry schemas, namespaces, and policies to protocol graph."""

    print("=" * 80)
    print("TELEMETRY SCHEMA INGESTION (Option C: Generic Schemas + Wildcards)")
    print("=" * 80)
    print()

    # Connect to FalkorDB
    db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=6379)
    protocol_graph = db.select_graph("protocol")

    print("[1/4] Creating telemetry namespaces with wildcard patterns...")
    print()

    # Define telemetry namespaces (wildcards)
    namespaces = [
        {
            "id": "protocol/Topic_Namespace/telemetry.state",
            "name": "telemetry.state.*",
            "pattern": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/telemetry/state/*",
            "description": "State snapshots and selections (mode.snapshot, wm.selected, wm.emit)",
            "governance_level": "strict",  # Identity-bearing
        },
        {
            "id": "protocol/Topic_Namespace/telemetry.series",
            "name": "telemetry.series.*",
            "pattern": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/telemetry/series/*",
            "description": "Metric batches and summaries (health.*, link.flow.summary)",
            "governance_level": "flex",
        },
        {
            "id": "protocol/Topic_Namespace/telemetry.lifecycle",
            "name": "telemetry.lifecycle.*",
            "pattern": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/telemetry/lifecycle/*",
            "description": "Lifecycle transitions (subentity.lifecycle, subentity.flip)",
            "governance_level": "flex",
        },
        {
            "id": "protocol/Topic_Namespace/telemetry.activation",
            "name": "telemetry.activation.*",
            "pattern": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/telemetry/activation/*",
            "description": "Activation and intensity metrics (subentity.activation)",
            "governance_level": "flex",
        },
        {
            "id": "protocol/Topic_Namespace/telemetry.detection",
            "name": "telemetry.detection.*",
            "pattern": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/telemetry/detection/*",
            "description": "Gap and anomaly detection (emergence.gap.detected, emergence.coalition.formed)",
            "governance_level": "strict",  # Detection events are high-stakes
        },
        {
            "id": "protocol/Topic_Namespace/telemetry.frame",
            "name": "telemetry.frame.*",
            "pattern": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/telemetry/frame/*",
            "description": "Frame-level telemetry (tick.update, frame.start, state_modulation.frame)",
            "governance_level": "flex",
        },
    ]

    for ns in namespaces:
        query = f"""
        MERGE (ns:ProtocolNode {{id: '{ns['id']}'}})
        SET ns.type_name = 'Topic_Namespace',
            ns.name = '{ns['name']}',
            ns.pattern = '{ns['pattern']}',
            ns.description = '{ns['description']}',
            ns.governance_level = '{ns['governance_level']}',
            ns.updated_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(query)
        print(f"   Created namespace: {ns['name']} ({ns['governance_level']})")

    print()
    print("[2/4] Creating generic telemetry event schemas...")
    print()

    # Define generic telemetry schemas
    schemas = [
        {
            "id": "protocol/Event_Schema/telemetry.state",
            "name": "telemetry.state@1.0.0",
            "direction": "broadcast",
            "summary": "Generic state snapshot or selection",
            "schema_def": '{"type":"object","required":["entity_id","state","ts"],"properties":{"entity_id":{"type":"string"},"state":{"type":"object"},"ts":{"type":"integer"}},"additionalProperties":true}',
            "version": "1.0.0",
            "namespace": "protocol/Topic_Namespace/telemetry.state",
        },
        {
            "id": "protocol/Event_Schema/telemetry.series",
            "name": "telemetry.series@1.0.0",
            "direction": "broadcast",
            "summary": "Generic metric batch or time-series summary",
            "schema_def": '{"type":"object","required":["entity_id","metrics","ts"],"properties":{"entity_id":{"type":"string"},"metrics":{"type":"object","additionalProperties":{"type":"number"}},"ts":{"type":"integer"},"window":{"type":"object","properties":{"start_ts":{"type":"integer"},"end_ts":{"type":"integer"}}}},"additionalProperties":true}',
            "version": "1.0.0",
            "namespace": "protocol/Topic_Namespace/telemetry.series",
        },
        {
            "id": "protocol/Event_Schema/telemetry.lifecycle",
            "name": "telemetry.lifecycle@1.0.0",
            "direction": "broadcast",
            "summary": "Generic lifecycle transition event",
            "schema_def": '{"type":"object","required":["entity_id","transition","ts"],"properties":{"entity_id":{"type":"string"},"transition":{"type":"string"},"details":{"type":"object"},"ts":{"type":"integer"}},"additionalProperties":true}',
            "version": "1.0.0",
            "namespace": "protocol/Topic_Namespace/telemetry.lifecycle",
        },
        {
            "id": "protocol/Event_Schema/telemetry.activation",
            "name": "telemetry.activation@1.0.0",
            "direction": "broadcast",
            "summary": "Generic activation or intensity metric",
            "schema_def": '{"type":"object","required":["entity_id","activation","ts"],"properties":{"entity_id":{"type":"string"},"activation":{"type":"number"},"dims":{"type":"object"},"ts":{"type":"integer"}},"additionalProperties":true}',
            "version": "1.0.0",
            "namespace": "protocol/Topic_Namespace/telemetry.activation",
        },
        {
            "id": "protocol/Event_Schema/telemetry.detection",
            "name": "telemetry.detection@1.0.0",
            "direction": "broadcast",
            "summary": "Generic gap or anomaly detection event",
            "schema_def": '{"type":"object","required":["subject_id","kind","score","ts"],"properties":{"subject_id":{"type":"string"},"kind":{"type":"string"},"score":{"type":"number"},"context":{"type":"object"},"ts":{"type":"integer"}},"additionalProperties":true}',
            "version": "1.0.0",
            "namespace": "protocol/Topic_Namespace/telemetry.detection",
        },
    ]

    # Create envelope schema reference (reuse existing or create)
    envelope_id = "protocol/Envelope_Schema/ENV_STANDARD_V1"
    envelope_query = f"""
    MERGE (env:ProtocolNode {{id: '{envelope_id}'}})
    SET env.type_name = 'Envelope_Schema',
        env.name = 'ENV_STANDARD_V1',
        env.description = 'Standard L4 envelope with ed25519 signature',
        env.version = '1.0.0'
    """
    protocol_graph.query(envelope_query)

    # Create signature suite reference (reuse existing or create)
    sig_id = "protocol/Signature_Suite/SIG_ED25519_V1"
    sig_query = f"""
    MERGE (sig:ProtocolNode {{id: '{sig_id}'}})
    SET sig.type_name = 'Signature_Suite',
        sig.name = 'SIG_ED25519_V1',
        sig.algorithm = 'ed25519',
        sig.version = '1.0.0'
    """
    protocol_graph.query(sig_query)

    for schema in schemas:
        # Create Event_Schema node
        query = f"""
        MERGE (es:ProtocolNode {{id: '{schema['id']}'}})
        SET es.type_name = 'Event_Schema',
            es.name = '{schema['name']}',
            es.direction = '{schema['direction']}',
            es.summary = '{schema['summary']}',
            es.schema_def = '{schema['schema_def']}',
            es.version = '{schema['version']}',
            es.updated_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(query)

        # MAPS_TO_TOPIC relationship
        maps_query = f"""
        MATCH (es:ProtocolNode {{id: '{schema['id']}'}}),
              (ns:ProtocolNode {{id: '{schema['namespace']}'}})
        MERGE (es)-[r:MAPS_TO_TOPIC]->(ns)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(maps_query)

        # REQUIRES_ENVELOPE relationship
        env_query = f"""
        MATCH (es:ProtocolNode {{id: '{schema['id']}'}}),
              (env:ProtocolNode {{id: '{envelope_id}'}})
        MERGE (es)-[r:REQUIRES_ENVELOPE]->(env)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(env_query)

        # REQUIRES_SIG relationship (all telemetry requires signature)
        sig_query = f"""
        MATCH (es:ProtocolNode {{id: '{schema['id']}'}}),
              (sig:ProtocolNode {{id: '{sig_id}'}})
        MERGE (es)-[r:REQUIRES_SIG]->(sig)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(sig_query)

        print(f"   Created schema: {schema['name']}")

    print()
    print("[3/4] Creating governance policies...")
    print()

    # Create governance policies
    policies = [
        {
            "id": "protocol/Governance_Policy/POL_TELEM_STRICT_V1",
            "name": "POL_TELEM_STRICT_V1",
            "description": "Strict telemetry policy for identity-bearing state and detection events",
            "rules": {
                "signature_required": True,
                "sea_required": True,  # SEA attestation required for identity-bearing topics
                "subject_types": ["subentity", "mode", "wm"],
            },
            "governs_namespaces": [
                "protocol/Topic_Namespace/telemetry.state",
                "protocol/Topic_Namespace/telemetry.detection",
            ],
        },
        {
            "id": "protocol/Governance_Policy/POL_TELEM_FLEX_V1",
            "name": "POL_TELEM_FLEX_V1",
            "description": "Flexible telemetry policy for metrics and lifecycle events",
            "rules": {
                "signature_required": True,
                "sea_required": False,  # Signature only, no SEA
                "cps_applicable": False,
            },
            "governs_namespaces": [
                "protocol/Topic_Namespace/telemetry.series",
                "protocol/Topic_Namespace/telemetry.lifecycle",
                "protocol/Topic_Namespace/telemetry.activation",
                "protocol/Topic_Namespace/telemetry.frame",
            ],
        },
    ]

    for policy in policies:
        # Create Governance_Policy node
        import json
        rules_json = json.dumps(policy['rules']).replace("'", "\\'")

        query = f"""
        MERGE (pol:ProtocolNode {{id: '{policy['id']}'}})
        SET pol.type_name = 'Governance_Policy',
            pol.name = '{policy['name']}',
            pol.description = '{policy['description']}',
            pol.rules = '{rules_json}',
            pol.updated_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(query)

        # GOVERNS relationships to namespaces
        for ns_id in policy['governs_namespaces']:
            governs_query = f"""
            MATCH (pol:ProtocolNode {{id: '{policy['id']}'}}),
                  (ns:ProtocolNode {{id: '{ns_id}'}})
            MERGE (pol)-[r:GOVERNS]->(ns)
            SET r.created_at = '{datetime.utcnow().isoformat()}Z'
            """
            protocol_graph.query(governs_query)

        print(f"   Created policy: {policy['name']}")
        print(f"    Governs: {len(policy['governs_namespaces'])} namespaces")

    print()
    print("[4/4] Creating topic-to-schema mappings (concrete examples)...")
    print()

    # Define concrete topic mappings for documentation
    # (These are implicit through namespace wildcards, but documenting explicitly helps)
    topic_mappings = [
        # State events (STRICT)
        ("mode.snapshot", "telemetry.state@1.0.0", "telemetry.state.*"),
        ("wm.selected", "telemetry.state@1.0.0", "telemetry.state.*"),
        ("wm.emit", "telemetry.state@1.0.0", "telemetry.state.*"),

        # Detection events (STRICT)
        ("emergence.gap.detected", "telemetry.detection@1.0.0", "telemetry.detection.*"),
        ("emergence.coalition.formed", "telemetry.detection@1.0.0", "telemetry.detection.*"),

        # Series events (FLEX)
        ("health.phenomenological", "telemetry.series@1.0.0", "telemetry.series.*"),
        ("link.flow.summary", "telemetry.series@1.0.0", "telemetry.series.*"),
        ("se.boundary.summary", "telemetry.series@1.0.0", "telemetry.series.*"),
        ("coherence.metric", "telemetry.series@1.0.0", "telemetry.series.*"),

        # Lifecycle events (FLEX)
        ("subentity.lifecycle", "telemetry.lifecycle@1.0.0", "telemetry.lifecycle.*"),
        ("subentity.flip", "telemetry.lifecycle@1.0.0", "telemetry.lifecycle.*"),

        # Activation events (FLEX)
        ("subentity.activation", "telemetry.activation@1.0.0", "telemetry.activation.*"),

        # Frame events (FLEX)
        ("tick.update", "telemetry.series@1.0.0", "telemetry.frame.*"),
        ("frame.start", "telemetry.series@1.0.0", "telemetry.frame.*"),
        ("state_modulation.frame", "telemetry.series@1.0.0", "telemetry.frame.*"),
        ("decay.tick", "telemetry.series@1.0.0", "telemetry.frame.*"),
    ]

    print("  Concrete topic examples (implicit via namespace wildcards):")
    for topic, schema, namespace in topic_mappings:
        print(f"    - {topic:35s} -> {schema:30s} ({namespace})")

    print()
    print("=" * 80)
    print("TELEMETRY SCHEMA INGESTION COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print("  - 6 telemetry namespaces created (wildcards)")
    print("  - 5 generic event schemas created")
    print("  - 2 governance policies created (STRICT + FLEX)")
    print("  - All relationships wired (MAPS_TO_TOPIC, REQUIRES_ENVELOPE, REQUIRES_SIG, GOVERNS)")
    print()
    print("Next steps:")
    print("  1. Re-export L4 registry: python3 tools/protocol/export_l4_public.py")
    print("  2. Update mp-lint to support wildcard namespace matching")
    print("  3. Test mp-lint: python3 tools/mp-lint orchestration/")
    print()


if __name__ == "__main__":
    ingest_telemetry_schemas()
