#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest Concrete Telemetry Event Schemas

Maps concrete event names (mode.snapshot, wm.selected, etc.) to generic
telemetry schemas (telemetry.state@1.0.0, etc.) via namespace relationships.

This completes the Option C implementation by creating Event_Schema nodes
for each concrete event that the consciousness engines emit.

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-31
"""

import os
from datetime import datetime
from falkordb import FalkorDB


def ingest_concrete_events():
    """Ingest concrete telemetry event schemas."""

    print("=" * 80)
    print("CONCRETE TELEMETRY EVENT REGISTRATION")
    print("=" * 80)
    print()

    # Connect to FalkorDB
    db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=6379)
    protocol_graph = db.select_graph("protocol")

    # Define concrete events and their mappings
    # Format: (event_name, namespace_id, description)
    concrete_events = [
        # State events (STRICT) -> telemetry.state.*
        ("mode.snapshot", "protocol/Topic_Namespace/telemetry.state", "Mode state snapshot"),
        ("wm.selected", "protocol/Topic_Namespace/telemetry.state", "Working memory selection"),
        ("wm.emit", "protocol/Topic_Namespace/telemetry.state", "Working memory emission"),

        # Detection events (STRICT) -> telemetry.detection.*
        ("emergence.gap.detected", "protocol/Topic_Namespace/telemetry.detection", "Emergence gap detection"),
        ("emergence.coalition.formed", "protocol/Topic_Namespace/telemetry.detection", "Coalition formation detection"),
        ("emergence.reject", "protocol/Topic_Namespace/telemetry.detection", "Emergence rejection"),
        ("emergence.redirect", "protocol/Topic_Namespace/telemetry.detection", "Emergence redirection"),
        ("emergence.spawn.completed", "protocol/Topic_Namespace/telemetry.detection", "Emergence spawn completion"),
        ("emergence.weight.adjusted", "protocol/Topic_Namespace/telemetry.detection", "Emergence weight adjustment"),

        # Series events (FLEX) -> telemetry.series.*
        ("health.phenomenological", "protocol/Topic_Namespace/telemetry.series", "Phenomenological health metrics"),
        ("link.flow.summary", "protocol/Topic_Namespace/telemetry.series", "Link flow summary metrics"),
        ("se.boundary.summary", "protocol/Topic_Namespace/telemetry.series", "SubEntity boundary summary"),
        ("coherence.metric", "protocol/Topic_Namespace/telemetry.series", "Coherence metrics"),
        ("weights.updated", "protocol/Topic_Namespace/telemetry.series", "Weight update metrics"),
        ("phenomenology.mismatch", "protocol/Topic_Namespace/telemetry.series", "Phenomenology mismatch metrics"),
        ("integration_metrics.frame", "protocol/Topic_Namespace/telemetry.series", "Integration metrics"),

        # Lifecycle events (FLEX) -> telemetry.lifecycle.*
        ("subentity.lifecycle", "protocol/Topic_Namespace/telemetry.lifecycle", "SubEntity lifecycle transition"),
        ("subentity.flip", "protocol/Topic_Namespace/telemetry.lifecycle", "SubEntity state flip"),
        ("node.flip", "protocol/Topic_Namespace/telemetry.lifecycle", "Node state flip"),
        ("membership.updated", "protocol/Topic_Namespace/telemetry.lifecycle", "Membership update"),
        ("entity.multiplicity_assessment", "protocol/Topic_Namespace/telemetry.lifecycle", "Multiplicity assessment"),
        ("entity.productive_multiplicity", "protocol/Topic_Namespace/telemetry.lifecycle", "Productive multiplicity"),

        # Activation events (FLEX) -> telemetry.activation.*
        ("subentity.activation", "protocol/Topic_Namespace/telemetry.activation", "SubEntity activation level"),

        # Frame events (FLEX) -> telemetry.frame.*
        ("tick.update", "protocol/Topic_Namespace/telemetry.frame", "Tick update event"),
        ("frame.start", "protocol/Topic_Namespace/telemetry.frame", "Frame start event"),
        ("state_modulation.frame", "protocol/Topic_Namespace/telemetry.frame", "State modulation frame"),
        ("decay.tick", "protocol/Topic_Namespace/telemetry.frame", "Decay tick event"),
        ("tick_frame_v1", "protocol/Topic_Namespace/telemetry.frame", "Tick frame v1"),
        ("criticality.state", "protocol/Topic_Namespace/telemetry.frame", "Criticality state"),
        ("stimulus.injection.debug", "protocol/Topic_Namespace/telemetry.frame", "Stimulus injection debug"),
    ]

    print(f"[1/1] Creating {len(concrete_events)} concrete event schemas...")
    print()

    created_count = 0
    for event_name, namespace_id, description in concrete_events:
        event_id = f"protocol/Event_Schema/{event_name}"

        # Create Event_Schema node
        query = f"""
        MERGE (es:ProtocolNode {{id: '{event_id}'}})
        SET es.type_name = 'Event_Schema',
            es.name = '{event_name}',
            es.direction = 'broadcast',
            es.summary = '{description}',
            es.version = '1.0.0',
            es.updated_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(query)

        # MAPS_TO_TOPIC relationship to namespace
        maps_query = f"""
        MATCH (es:ProtocolNode {{id: '{event_id}'}}),
              (ns:ProtocolNode {{id: '{namespace_id}'}})
        MERGE (es)-[r:MAPS_TO_TOPIC]->(ns)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(maps_query)

        # REQUIRES_ENVELOPE relationship
        env_id = "protocol/Envelope_Schema/ENV_STANDARD_V1"
        env_query = f"""
        MATCH (es:ProtocolNode {{id: '{event_id}'}}),
              (env:ProtocolNode {{id: '{env_id}'}})
        MERGE (es)-[r:REQUIRES_ENVELOPE]->(env)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(env_query)

        # REQUIRES_SIG relationship
        sig_id = "protocol/Signature_Suite/SIG_ED25519_V1"
        sig_query = f"""
        MATCH (es:ProtocolNode {{id: '{event_id}'}}),
              (sig:ProtocolNode {{id: '{sig_id}'}})
        MERGE (es)-[r:REQUIRES_SIG]->(sig)
        SET r.created_at = '{datetime.utcnow().isoformat()}Z'
        """
        protocol_graph.query(sig_query)

        created_count += 1
        print(f"  - Created: {event_name:40s} -> {namespace_id.split('/')[-1]}")

    print()
    print("=" * 80)
    print("CONCRETE EVENT REGISTRATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Summary: Created {created_count} concrete event schemas")
    print()
    print("Next steps:")
    print("  1. Re-export L4 registry: python3 tools/protocol/export_l4_public.py")
    print("  2. Test mp-lint: python3 tools/mp-lint orchestration/")
    print()


if __name__ == "__main__":
    ingest_concrete_events()
