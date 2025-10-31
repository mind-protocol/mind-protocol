#!/usr/bin/env python3
"""
Link Protocol Graph Nodes to L4 Subentities

Creates MEMBER_OF relationships between Event_Schema, Governance_Policy,
Topic_Namespace, and Signature_Suite nodes and their governing L4 subentities.

Based on L4 subsystems spec and node name patterns.
"""

from falkordb import FalkorDB
from datetime import datetime, timezone

# Mapping of event/policy/topic patterns to L4 subentities
MEMBERSHIP_MAPPING = {
    # SEA - Identity & Attestation
    "SEA": {
        "event_patterns": ["governance.keys.", "membership.updated"],
        "topic_patterns": ["identity.*"],
        "description": "Identity, keys, membership, attestations"
    },

    # CPS - Compute Payment & Settlement
    "CPS": {
        "event_patterns": ["economy.quote.", "budget.", "compute."],
        "topic_patterns": ["economy.*", "budget.*"],
        "description": "Economic settlement, compute payment"
    },

    # UBC - Universal Basic Compute
    "UBC": {
        "event_patterns": ["ubc."],
        "topic_patterns": ["ubc.*"],
        "description": "Universal basic compute distribution"
    },

    # RGS - Registries
    "RGS": {
        "event_patterns": ["registry.", "legal_entity."],
        "topic_patterns": ["registry.*", "legal.*"],
        "description": "Registry operations, legal entities"
    },

    # AGL - Autonomy Gates & Tiers
    "AGL": {
        "event_patterns": ["tier.", "capability."],
        "topic_patterns": ["capability.*", "tier.*"],
        "description": "Capability unlock, tier progression"
    },

    # DRP - Disputes & Due Process
    "DRP": {
        "event_patterns": ["governance.suspension.", "dispute.", "appeal."],
        "topic_patterns": ["dispute.*", "suspension.*"],
        "description": "Disputes, suspensions, appeals"
    },

    # GOV - Governance & Amendments
    "GOV": {
        "event_patterns": ["policy.", "governance."],
        "topic_patterns": ["governance.*", "policy.*"],
        "description": "Governance policies, amendments"
    },

    # OBS - Observability & Audit
    "OBS": {
        "event_patterns": [
            "presence.beacon",
            "health.",
            "status.activity",
            "graph.delta.",
            "wm.emit",
            "percept.frame"
        ],
        "topic_patterns": ["health.*", "presence.*", "status.*"],
        "description": "Health monitoring, telemetry, consciousness observability"
    },

    # SEC - Signature Suites & Security
    "SEC": {
        "event_patterns": ["security.", "signature.", "keys."],
        "topic_patterns": ["security.*", "keys.*"],
        "description": "Security profiles, signature suites"
    },

    # TRN - Transport & Namespaces
    "TRN": {
        "event_patterns": [
            "membrane.inject",
            "membrane.transfer.",
            "membrane.permeability",
            "message.",
            "bridge.",
            "handoff."
        ],
        "topic_patterns": [
            "membrane.*",
            "org/*/inject/*",
            "org/*/broadcast/*",
            "citizen/*/broadcast/*",
            "ecosystem/*"
        ],
        "description": "Transport, routing, message delivery, handoffs"
    },
}

# Special handling for nodes that don't fit clear patterns
SPECIAL_MAPPINGS = {
    # Consciousness/infrastructure events → OBS
    "emergence.spawn": "OBS",
    "emergence.candidate": "OBS",
    "candidate.redirected": "OBS",
    "gap.detected": "OBS",
    "subentity.snapshot": "OBS",

    # Mission/intent events → GOV (organizational governance)
    "intent.created": "GOV",
    "intent.assigned": "GOV",
    "mission.completed": "GOV",
    "mission.done": "GOV",

    # Tool events → AGL (capability management)
    "tool.offer": "AGL",
    "tool.request": "AGL",
    "tool.result": "AGL",

    # Documentation events → GOV (documentation governance)
    "docs.request.generate": "GOV",
    "docs.draft.created": "GOV",
    "docs.page.upsert": "GOV",
    "docs.publish": "GOV",
    "docs.catalog.emit": "GOV",
    "docs.page.updated": "GOV",
    "docs.slice.emit": "GOV",

    # Knowledge object events → GOV (knowledge governance)
    "docs.ingest.chunk": "GOV",
    "ko.cluster.proposed": "GOV",
    "ko.cluster.applied": "GOV",
    "ko.cluster.rejected": "GOV",
    "ko.review.request": "GOV",
    "ko.review.response": "GOV",
}


def match_node_to_subentity(node_name: str, node_type: str) -> str:
    """
    Determine which L4 subentity a node should be a member of.

    Args:
        node_name: Name of the node (e.g., "health.link.ping")
        node_type: Type of node (Event_Schema, Governance_Policy, etc.)

    Returns:
        Subentity slug (SEA, CPS, etc.) or None if no match
    """

    # Check special mappings first
    if node_name in SPECIAL_MAPPINGS:
        return SPECIAL_MAPPINGS[node_name]

    # Check pattern matching
    for subentity_slug, config in MEMBERSHIP_MAPPING.items():
        patterns = config.get("event_patterns", [])

        for pattern in patterns:
            if pattern.endswith("."):
                # Prefix match (e.g., "health." matches "health.link.ping")
                if node_name.startswith(pattern):
                    return subentity_slug
            else:
                # Exact match or substring match
                if pattern in node_name:
                    return subentity_slug

    return None


def create_member_of_relationships(dry_run: bool = False):
    """Create MEMBER_OF relationships between nodes and L4 subentities."""

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now = datetime.now(timezone.utc).isoformat()

    print("=" * 80)
    print("Linking Protocol Graph Nodes to L4 Subentities")
    print("=" * 80)

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")

    # Get all Event_Schema nodes
    result = g.query("""
        MATCH (e:Event_Schema)
        RETURN e.name as name, id(e) as node_id
        ORDER BY e.name
    """)

    event_schemas = [(r[0], r[1]) for r in result.result_set]
    print(f"\nFound {len(event_schemas)} Event_Schema nodes")

    # Map events to subentities
    membership_counts = {slug: [] for slug in MEMBERSHIP_MAPPING.keys()}
    unmapped_events = []

    for event_name, node_id in event_schemas:
        subentity = match_node_to_subentity(event_name, "Event_Schema")

        if subentity:
            membership_counts[subentity].append(event_name)

            # Create MEMBER_OF relationship
            query = f"""
                MATCH (e:Event_Schema), (s:U4_Subentity {{slug: '{subentity}'}})
                WHERE id(e) = {node_id}
                MERGE (e)-[r:MEMBER_OF]->(s)
                ON CREATE SET r.joined_at = '{now}', r.membership_type = 'governed'
                RETURN id(r)
            """

            if dry_run:
                print(f"  [DRY RUN] Would link: {event_name} → {subentity}")
            else:
                try:
                    g.query(query)
                    print(f"  ✓ Linked: {event_name} → {subentity}")
                except Exception as e:
                    print(f"  ✗ Error linking {event_name}: {e}")
        else:
            unmapped_events.append(event_name)

    # Handle Topic_Namespace nodes → all go to TRN
    result = g.query("""
        MATCH (t:Topic_Namespace)
        RETURN t.namespace as namespace, id(t) as node_id
    """)

    topic_namespaces = [(r[0], r[1]) for r in result.result_set if r[0]]
    print(f"\nFound {len(topic_namespaces)} Topic_Namespace nodes")

    for namespace, node_id in topic_namespaces:
        query = f"""
            MATCH (t:Topic_Namespace), (s:U4_Subentity {{slug: 'TRN'}})
            WHERE id(t) = {node_id}
            MERGE (t)-[r:MEMBER_OF]->(s)
            ON CREATE SET r.joined_at = '{now}', r.membership_type = 'governed'
            RETURN id(r)
        """

        if dry_run:
            print(f"  [DRY RUN] Would link: Topic '{namespace}' → TRN")
        else:
            try:
                g.query(query)
                print(f"  ✓ Linked: Topic '{namespace}' → TRN")
                membership_counts["TRN"].append(f"Topic: {namespace}")
            except Exception as e:
                print(f"  ✗ Error linking topic {namespace}: {e}")

    # Handle Signature_Suite nodes → all go to SEC
    result = g.query("""
        MATCH (sig:Signature_Suite)
        RETURN sig.name as name, id(sig) as node_id
    """)

    signature_suites = [(r[0] or "Unknown", r[1]) for r in result.result_set]
    print(f"\nFound {len(signature_suites)} Signature_Suite nodes")

    for suite_name, node_id in signature_suites:
        query = f"""
            MATCH (sig:Signature_Suite), (s:U4_Subentity {{slug: 'SEC'}})
            WHERE id(sig) = {node_id}
            MERGE (sig)-[r:MEMBER_OF]->(s)
            ON CREATE SET r.joined_at = '{now}', r.membership_type = 'governed'
            RETURN id(r)
        """

        if dry_run:
            print(f"  [DRY RUN] Would link: Signature_Suite '{suite_name}' → SEC")
        else:
            try:
                g.query(query)
                print(f"  ✓ Linked: Signature_Suite '{suite_name}' → SEC")
                membership_counts["SEC"].append(f"Suite: {suite_name}")
            except Exception as e:
                print(f"  ✗ Error linking signature suite: {e}")

    # Handle Governance_Policy nodes - map by name pattern
    result = g.query("""
        MATCH (p:Governance_Policy)
        RETURN p.name as name, id(p) as node_id
    """)

    policies = [(r[0] or "Unknown", r[1]) for r in result.result_set]
    print(f"\nFound {len(policies)} Governance_Policy nodes")

    for policy_name, node_id in policies:
        # Most governance policies → GOV, unless they match other patterns
        subentity = match_node_to_subentity(policy_name, "Governance_Policy") or "GOV"

        query = f"""
            MATCH (p:Governance_Policy), (s:U4_Subentity {{slug: '{subentity}'}})
            WHERE id(p) = {node_id}
            MERGE (p)-[r:MEMBER_OF]->(s)
            ON CREATE SET r.joined_at = '{now}', r.membership_type = 'governed'
            RETURN id(r)
        """

        if dry_run:
            print(f"  [DRY RUN] Would link: Policy '{policy_name}' → {subentity}")
        else:
            try:
                g.query(query)
                print(f"  ✓ Linked: Policy '{policy_name}' → {subentity}")
                membership_counts[subentity].append(f"Policy: {policy_name}")
            except Exception as e:
                print(f"  ✗ Error linking policy {policy_name}: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    print("\n### Membership by Subentity:")
    for subentity, members in sorted(membership_counts.items()):
        if members:
            print(f"\n{subentity} ({len(members)} members):")
            for member in members[:10]:  # Show first 10
                print(f"  - {member}")
            if len(members) > 10:
                print(f"  ... and {len(members) - 10} more")

    if unmapped_events:
        print(f"\n⚠️  Unmapped events ({len(unmapped_events)}):")
        for event in unmapped_events[:20]:
            print(f"  - {event}")
        if len(unmapped_events) > 20:
            print(f"  ... and {len(unmapped_events) - 20} more")

    # Verify member_count on subentities
    if not dry_run:
        print("\n### Updating member_count on subentities:")
        for subentity_slug in MEMBERSHIP_MAPPING.keys():
            query = f"""
                MATCH (s:U4_Subentity {{slug: '{subentity_slug}'}})
                OPTIONAL MATCH (m)-[:MEMBER_OF]->(s)
                WITH s, count(m) as member_count
                SET s.member_count = member_count
                RETURN s.slug, member_count
            """
            result = g.query(query)
            if result.result_set:
                slug, count = result.result_set[0]
                print(f"  {slug}: {count} members")


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    create_member_of_relationships(dry_run=dry_run)
