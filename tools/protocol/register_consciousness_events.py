#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Register Consciousness System Telemetry Events

Registers all telemetry events emitted by the consciousness system that were
previously unregistered. Completes BLOCKING #1 for 100% mp-lint compliance.

Maps concrete event names to generic telemetry schemas via namespace relationships.

Author: Luca Vellumhand (Consciousness Substrate Architect)
Date: 2025-10-31
"""

import os
from datetime import datetime
from falkordb import FalkorDB


def register_consciousness_events():
    """Register all consciousness system telemetry event schemas."""

    print("=" * 80)
    print("CONSCIOUSNESS TELEMETRY EVENT REGISTRATION")
    print("=" * 80)
    print()

    # Connect to FalkorDB
    db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=6379)
    protocol_graph = db.select_graph("protocol")

    # Define all consciousness events and their mappings
    # Format: (event_name, namespace_id, description, governance_strictness)
    consciousness_events = [
        # ===== STATE EVENTS (STRICT) → telemetry.state.* =====
        ("mode.snapshot", "protocol/Topic_Namespace/telemetry.state",
         "Mode state snapshot from consciousness engine", "STRICT"),
        ("wm.selected", "protocol/Topic_Namespace/telemetry.state",
         "Working memory node selection event", "STRICT"),
        ("wm.emit", "protocol/Topic_Namespace/telemetry.state",
         "Working memory emission event", "STRICT"),
        ("dashboard.state.emit@1.0", "protocol/Topic_Namespace/telemetry.state",
         "Dashboard state broadcast for visualization", "FLEX"),

        # ===== DETECTION/EMERGENCE EVENTS (STRICT) → telemetry.detection.* =====
        ("emergence.gap.detected", "protocol/Topic_Namespace/telemetry.detection",
         "Emergence gap detected in consciousness graph", "STRICT"),
        ("emergence.coalition.formed", "protocol/Topic_Namespace/telemetry.detection",
         "Coalition formation detected during emergence", "STRICT"),
        ("emergence.reject", "protocol/Topic_Namespace/telemetry.detection",
         "Emergence candidate rejected", "STRICT"),
        ("emergence.redirect", "protocol/Topic_Namespace/telemetry.detection",
         "Emergence candidate redirected to different subentity", "STRICT"),
        ("emergence.spawn.completed", "protocol/Topic_Namespace/telemetry.detection",
         "SubEntity emergence spawn completed", "STRICT"),
        ("emergence.weight.adjusted", "protocol/Topic_Namespace/telemetry.detection",
         "Weight adjustment during emergence learning", "STRICT"),

        # ===== SERIES/METRICS EVENTS (FLEX) → telemetry.series.* =====
        ("health.phenomenological", "protocol/Topic_Namespace/telemetry.series",
         "Phenomenological health metrics from consciousness", "FLEX"),
        ("link.flow.summary", "protocol/Topic_Namespace/telemetry.series",
         "Link activation flow summary metrics", "FLEX"),
        ("link.emotion.update", "protocol/Topic_Namespace/telemetry.series",
         "Link emotional valence update", "FLEX"),
        ("se.boundary.summary", "protocol/Topic_Namespace/telemetry.series",
         "SubEntity boundary permeability summary", "FLEX"),
        ("coherence.metric", "protocol/Topic_Namespace/telemetry.series",
         "Coherence metric from consciousness integration", "FLEX"),
        ("weights.updated", "protocol/Topic_Namespace/telemetry.series",
         "Weight learning update metrics", "FLEX"),
        ("phenomenology.mismatch", "protocol/Topic_Namespace/telemetry.series",
         "Phenomenology expectation vs reality mismatch", "FLEX"),
        ("integration_metrics.node", "protocol/Topic_Namespace/telemetry.series",
         "Node-level integration metrics", "FLEX"),
        ("integration_metrics.population", "protocol/Topic_Namespace/telemetry.series",
         "Population-level integration metrics", "FLEX"),
        ("rich_club.hub_at_risk", "protocol/Topic_Namespace/telemetry.series",
         "Rich club hub identified as at-risk", "FLEX"),
        ("rich_club.snapshot", "protocol/Topic_Namespace/telemetry.series",
         "Rich club topology snapshot", "FLEX"),
        ("tier.link.strengthened", "protocol/Topic_Namespace/telemetry.series",
         "Tier-based link strengthening event", "FLEX"),

        # ===== LIFECYCLE EVENTS (FLEX) → telemetry.lifecycle.* =====
        ("subentity.lifecycle", "protocol/Topic_Namespace/telemetry.lifecycle",
         "SubEntity lifecycle state transition", "FLEX"),
        ("subentity.flip", "protocol/Topic_Namespace/telemetry.lifecycle",
         "SubEntity activation state flip (active/dormant)", "FLEX"),
        ("subentity.merged", "protocol/Topic_Namespace/telemetry.lifecycle",
         "SubEntity merge operation completed", "STRICT"),
        ("subentity.split", "protocol/Topic_Namespace/telemetry.lifecycle",
         "SubEntity split operation completed", "STRICT"),
        ("node.flip", "protocol/Topic_Namespace/telemetry.lifecycle",
         "Node activation state flip", "FLEX"),
        ("membership.updated", "protocol/Topic_Namespace/telemetry.lifecycle",
         "SubEntity membership update event", "FLEX"),
        ("entity.multiplicity_assessment", "protocol/Topic_Namespace/telemetry.lifecycle",
         "SubEntity multiplicity assessment result", "FLEX"),
        ("entity.productive_multiplicity", "protocol/Topic_Namespace/telemetry.lifecycle",
         "SubEntity productive multiplicity detection", "FLEX"),

        # ===== ACTIVATION EVENTS (FLEX) → telemetry.activation.* =====
        ("subentity.activation", "protocol/Topic_Namespace/telemetry.activation",
         "SubEntity activation level change", "FLEX"),

        # ===== FRAME/TICK EVENTS (FLEX) → telemetry.frame.* =====
        ("tick.update", "protocol/Topic_Namespace/telemetry.frame",
         "Consciousness tick update event", "FLEX"),
        ("frame.start", "protocol/Topic_Namespace/telemetry.frame",
         "Consciousness frame start boundary", "FLEX"),
        ("state_modulation.frame", "protocol/Topic_Namespace/telemetry.frame",
         "State modulation frame event", "FLEX"),
        ("decay.tick", "protocol/Topic_Namespace/telemetry.frame",
         "Energy decay tick event", "FLEX"),
        ("tick_frame_v1", "protocol/Topic_Namespace/telemetry.frame",
         "Tick frame v1 telemetry format", "FLEX"),
        ("criticality.state", "protocol/Topic_Namespace/telemetry.frame",
         "Criticality state snapshot", "FLEX"),
        ("stimulus.injection.debug", "protocol/Topic_Namespace/telemetry.frame",
         "Stimulus injection debug telemetry", "FLEX"),

        # ===== ECONOMY EVENTS (STRICT) → telemetry.economy.* =====
        # Note: Creating new economy namespace for financial events
        ("economy.charge.request", "protocol/Topic_Namespace/telemetry.economy",
         "Compute charge request initiated", "STRICT"),
        ("economy.charge.settle", "protocol/Topic_Namespace/telemetry.economy",
         "Compute charge settlement completed", "STRICT"),
        ("economy.rate.observed", "protocol/Topic_Namespace/telemetry.economy",
         "Economy rate observation event", "FLEX"),
        ("telemetry.economy.spend", "protocol/Topic_Namespace/telemetry.economy",
         "Economy spending telemetry", "FLEX"),
        ("telemetry.economy.ubc_tick", "protocol/Topic_Namespace/telemetry.economy",
         "UBC distribution tick event", "FLEX"),

        # ===== INFRASTRUCTURE EVENTS (FLEX) → telemetry.frame.* =====
        ("telemetry.write.denied", "protocol/Topic_Namespace/telemetry.frame",
         "Telemetry write denied due to constraints", "FLEX"),
    ]

    # Check which events already exist
    existing_query = """
        MATCH (e:Event_Schema)
        RETURN e.name as name
    """
    result = protocol_graph.query(existing_query)
    existing_events = {record[0] for record in result.result_set}

    print(f"Found {len(existing_events)} existing Event_Schema nodes")
    print(f"Will register {len(consciousness_events)} consciousness events")
    print()

    created_count = 0
    skipped_count = 0

    for event_name, namespace_id, description, strictness in consciousness_events:
        event_id = f"protocol/Event_Schema/{event_name}"

        # Check if already exists
        if event_name in existing_events:
            print(f"  ⊙ Skipped (exists): {event_name}")
            skipped_count += 1
            continue

        # Create Event_Schema node
        query = f"""
        MERGE (es:ProtocolNode {{id: '{event_id}'}})
        SET es:Event_Schema,
            es.type_name = 'Event_Schema',
            es.name = '{event_name}',
            es.direction = 'broadcast',
            es.summary = '{description}',
            es.governance_strictness = '{strictness}',
            es.version = '1.0.0',
            es.updated_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(query)

        # MAPS_TO_TOPIC relationship to namespace
        maps_query = f"""
        MATCH (es:Event_Schema {{name: '{event_name}'}}),
              (ns:Topic_Namespace)
        WHERE ns.id = '{namespace_id}' OR ns.namespace = '{namespace_id.split('/')[-1]}'
        MERGE (es)-[r:MAPS_TO_TOPIC]->(ns)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(maps_query)

        # REQUIRES_ENVELOPE relationship
        env_id = "protocol/Envelope_Schema/ENV_STANDARD_V1"
        env_query = f"""
        MATCH (es:Event_Schema {{name: '{event_name}'}}),
              (env:ProtocolNode {{id: '{env_id}'}})
        MERGE (es)-[r:REQUIRES_ENVELOPE]->(env)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(env_query)

        # REQUIRES_SIG relationship
        sig_id = "protocol/Signature_Suite/SIG_ED25519_V1"
        sig_query = f"""
        MATCH (es:Event_Schema {{name: '{event_name}'}}),
              (sig:ProtocolNode {{id: '{sig_id}'}})
        MERGE (es)-[r:REQUIRES_SIG]->(sig)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(sig_query)

        # MEMBER_OF relationship to OBS subentity (all telemetry governed by OBS)
        member_query = f"""
        MATCH (es:Event_Schema {{name: '{event_name}'}}),
              (obs:U4_Subentity {{slug: 'OBS'}})
        MERGE (es)-[r:MEMBER_OF]->(obs)
        SET r.joined_at = '{datetime.utcnow().isoformat()}Z',
            r.membership_type = 'governed'
        """
        protocol_graph.query(member_query)

        created_count += 1
        namespace_short = namespace_id.split('/')[-1]
        print(f"  ✓ Created: {event_name:45s} → {namespace_short} ({strictness})")

    print()
    print("=" * 80)
    print("CONSCIOUSNESS EVENT REGISTRATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Summary:")
    print(f"  - Created: {created_count} new event schemas")
    print(f"  - Skipped: {skipped_count} existing events")
    print(f"  - Total:   {created_count + skipped_count} consciousness events")
    print()
    print("All telemetry events are now governed by OBS (Observability & Audit) subentity")
    print()
    print("Next steps:")
    print("  1. Re-export L4 registry: python3 tools/protocol/export_l4_public.py")
    print("  2. Test mp-lint: python3 tools/mp-lint orchestration/")
    print("  3. Verify 0 violations (100% compliance)")
    print()


if __name__ == "__main__":
    register_consciousness_events()
