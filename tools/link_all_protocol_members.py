#!/usr/bin/env python3
"""
Link ALL Protocol Graph Nodes to L4 Subentities (Complete)

Maps ALL 217 protocol nodes to their governing L4 subentities.
Previous script only handled 60 nodes - this handles everything.
"""

from falkordb import FalkorDB
from datetime import datetime, timezone

# Complete mapping of node types to L4 subentities
NODE_TYPE_MAPPING = {
    # SEA - Identity & Attestation
    "SEA": {
        "node_types": [],  # Event patterns handled separately
        "description": "Identity, attestations, membership"
    },

    # CPS - Compute Payment & Settlement
    "CPS": {
        "node_types": [],  # Will have economy/budget events when added
        "description": "Economic settlement, compute payment"
    },

    # UBC - Universal Basic Compute
    "UBC": {
        "node_types": [],  # Will have ubc.* events when added
        "description": "Universal basic compute distribution"
    },

    # RGS - Registries
    "RGS": {
        "node_types": [
            "SDK_Release",
            "Adapter_Release",
            "Sidecar_Release",
            "Tool_Contract",
            "Tenant",
            "Tenant_Key",
            "Capability",  # Capability registry
        ],
        "description": "Registry of releases, tools, tenants, capabilities"
    },

    # AGL - Autonomy Gates & Tiers
    "AGL": {
        "node_types": [],  # Tool events already mapped
        "description": "Capability unlock, tier progression"
    },

    # DRP - Disputes & Due Process
    "DRP": {
        "node_types": [],  # Will have dispute/suspension events when added
        "description": "Disputes, suspensions, appeals"
    },

    # GOV - Governance & Amendments
    "GOV": {
        "node_types": [
            "Governance_Policy",  # Already partially mapped, but need all
            "Schema_Bundle",
            "Protocol_Version",
            "Deprecation_Notice",
            "Retention_Policy",
            "Compatibility_Matrix",
            "Principle",
            "Process",
            "Mechanism",
            "Interface",
            "SubEntity",  # Protocol spec for SubEntity concept
        ],
        "description": "Governance, protocol versioning, principles, specs"
    },

    # OBS - Observability & Audit
    "OBS": {
        "node_types": [
            "Conformance_Case",
            "Conformance_Suite",
            "Conformance_Result",
            "Metric",
        ],
        "description": "Conformance testing, metrics, observability"
    },

    # SEC - Signature Suites & Security
    "SEC": {
        "node_types": [
            "Signature_Suite",  # Already partially mapped
            "Security_Profile",
        ],
        "description": "Security profiles, signature suites, cryptography"
    },

    # TRN - Transport & Namespaces
    "TRN": {
        "node_types": [
            "Envelope_Schema",  # Already partially mapped
            "Topic_Namespace",  # Should have been mapped but wasn't
            "Topic_Route",
            "Bus_Instance",
            "Transport_Spec",
        ],
        "description": "Transport, routing, namespaces, bus topology"
    },
}

# Event name patterns (from previous script)
EVENT_PATTERNS = {
    "SEA": ["governance.keys.", "membership.updated"],
    "OBS": ["health.", "presence.beacon", "status.activity", "graph.delta.", "wm.emit", "percept.frame", "emergence.", "gap.detected", "candidate.redirected"],
    "GOV": ["policy.", "governance.", "intent.", "mission."],
    "TRN": ["membrane.", "message.", "bridge.", "handoff."],
    "AGL": ["tool."],
}


def map_node_to_subentity(node_labels: list, node_name: str, type_name: str = None) -> str:
    """Determine which L4 subentity a node belongs to."""

    # Get primary label (non-ProtocolNode), or use type_name as fallback
    primary_label = next((l for l in node_labels if l != "ProtocolNode"), type_name)

    if not primary_label:
        return None

    # Check node type mapping
    for subentity, config in NODE_TYPE_MAPPING.items():
        if primary_label in config["node_types"]:
            return subentity

    # For Event_Schema, check name patterns
    if primary_label == "Event_Schema" and node_name:
        for subentity, patterns in EVENT_PATTERNS.items():
            for pattern in patterns:
                if pattern.endswith("."):
                    if node_name.startswith(pattern):
                        return subentity
                else:
                    if pattern in node_name:
                        return subentity

    # Default for remaining Event_Schema → TRN
    if primary_label == "Event_Schema":
        return "TRN"

    # Event, Task → GOV (organizational governance)
    if primary_label in ["Event", "Task"]:
        return "GOV"

    return None


def link_all_protocol_members(dry_run: bool = False):
    """Link ALL protocol nodes to L4 subentities."""

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now = datetime.now(timezone.utc).isoformat()

    print("=" * 80)
    print("Linking ALL Protocol Graph Nodes to L4 Subentities")
    print("=" * 80)

    if dry_run:
        print("\n⚠️  DRY RUN MODE\n")

    # Get ALL nodes (except U4_Subentity)
    result = g.query("""
        MATCH (n)
        WHERE NOT 'U4_Subentity' IN labels(n)
        RETURN labels(n) as labels,
               n.name as name,
               n.type_name as type_name,
               id(n) as node_id
    """)

    all_nodes = result.result_set
    print(f"Found {len(all_nodes)} nodes to process\n")

    # Map nodes to subentities
    membership_counts = {slug: [] for slug in NODE_TYPE_MAPPING.keys()}
    unmapped = []

    for labels, name, type_name, node_id in all_nodes:
        primary_label = next((l for l in labels if l != "ProtocolNode"), type_name or "Unknown")
        display_name = f"{primary_label}:{name}" if name else primary_label

        subentity = map_node_to_subentity(labels, name, type_name)

        if subentity:
            membership_counts[subentity].append(display_name)

            # Check if already has MEMBER_OF
            check_query = f"""
                MATCH (n)-[r:MEMBER_OF]->(s:U4_Subentity)
                WHERE id(n) = {node_id}
                RETURN count(r)
            """
            check_result = g.query(check_query)
            has_member_of = check_result.result_set[0][0] > 0

            if has_member_of:
                if dry_run:
                    print(f"  [SKIP] Already linked: {display_name}")
                continue

            # Create MEMBER_OF
            query = f"""
                MATCH (n), (s:U4_Subentity {{slug: '{subentity}'}})
                WHERE id(n) = {node_id}
                MERGE (n)-[r:MEMBER_OF]->(s)
                ON CREATE SET r.joined_at = '{now}', r.membership_type = 'governed'
                RETURN id(r)
            """

            if dry_run:
                print(f"  [DRY RUN] Would link: {display_name} → {subentity}")
            else:
                try:
                    g.query(query)
                    print(f"  ✓ Linked: {display_name} → {subentity}")
                except Exception as e:
                    print(f"  ✗ Error linking {display_name}: {e}")
        else:
            unmapped.append(display_name)

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    print("\n### Membership by Subentity:")
    total_mapped = 0
    for subentity, members in sorted(membership_counts.items()):
        if members:
            print(f"\n{subentity} ({len(members)} members):")
            for member in members[:10]:
                print(f"  - {member}")
            if len(members) > 10:
                print(f"  ... and {len(members) - 10} more")
            total_mapped += len(members)

    print(f"\n### Total mapped: {total_mapped}")
    print(f"### Unmapped: {len(unmapped)}")

    if unmapped:
        print("\nUnmapped nodes:")
        for node in unmapped[:20]:
            print(f"  - {node}")
        if len(unmapped) > 20:
            print(f"  ... and {len(unmapped) - 20} more")

    # Update member_count on subentities
    if not dry_run:
        print("\n### Updating member_count on subentities:")
        for subentity_slug in NODE_TYPE_MAPPING.keys():
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
    link_all_protocol_members(dry_run=dry_run)
