#!/usr/bin/env python3
"""
Check if L4 Protocol Subsystems Exist

Queries consciousness graphs to check if the 10 L4 subsystem nodes have been created.

Expected subsystems (U4_Subentity with scope="protocol"):
- SEA — Identity & Attestation
- CPS — Compute Payment & Settlement
- UBC — Universal Basic Compute
- RGS — Registries
- AGL — Autonomy Gates & Tiers
- DRP — Disputes & Due Process
- GOV — Governance & Amendments
- OBS — Observability & Audit
- SEC — Signature_Suite & Security_Profile
- TRN — Transport & Namespaces
"""

from falkordb import FalkorDB

# Expected L4 subsystem slugs
EXPECTED_L4_SUBSYSTEMS = {
    "SEA": "Identity & Attestation",
    "CPS": "Compute Payment & Settlement",
    "UBC": "Universal Basic Compute",
    "RGS": "Registries",
    "AGL": "Autonomy Gates & Tiers",
    "DRP": "Disputes & Due Process",
    "GOV": "Governance & Amendments",
    "OBS": "Observability & Audit",
    "SEC": "Signature_Suite & Security_Profile",
    "TRN": "Transport & Namespaces",
}


def check_l4_subsystems():
    """Check if L4 subsystem nodes exist in consciousness graphs."""

    db = FalkorDB(host='localhost', port=6379)

    # Check in schema_registry graph first (most likely location for protocol-level nodes)
    print("=" * 80)
    print("Checking for L4 Subsystem Nodes")
    print("=" * 80)

    graphs_to_check = [
        "schema_registry",
        "consciousness-infrastructure_mind-protocol_ada",
        "consciousness-infrastructure_mind-protocol_atlas",
        "consciousness-infrastructure_mind-protocol_felix",
        "consciousness-infrastructure_mind-protocol_iris",
        "consciousness-infrastructure_mind-protocol_luca",
        "consciousness-infrastructure_mind-protocol_victor",
    ]

    found_subsystems = {}

    for graph_name in graphs_to_check:
        try:
            g = db.select_graph(graph_name)

            # Query for U4_Subentity nodes with scope="protocol"
            result = g.query("""
                MATCH (s:U4_Subentity)
                WHERE s.scope = 'protocol' OR s.level = 'L4'
                RETURN s.slug as slug,
                       s.name as name,
                       s.scope as scope,
                       s.level as level,
                       s.description as description,
                       labels(s) as labels
                ORDER BY s.slug
            """)

            if result.result_set:
                print(f"\n📍 Graph: {graph_name}")
                print(f"   Found {len(result.result_set)} protocol-level subentity nodes:")

                for record in result.result_set:
                    slug = record[0]
                    name = record[1]
                    scope = record[2]
                    level = record[3]
                    description = record[4]
                    labels = record[5]

                    print(f"\n   - Slug: {slug}")
                    print(f"     Name: {name}")
                    print(f"     Scope: {scope}")
                    print(f"     Level: {level}")
                    print(f"     Labels: {labels}")
                    if description:
                        print(f"     Description: {description[:100]}...")

                    if slug:
                        found_subsystems[slug] = {
                            "name": name,
                            "graph": graph_name,
                            "scope": scope,
                            "level": level,
                        }

        except Exception as e:
            # Graph might not exist or might not have these nodes
            pass

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    if not found_subsystems:
        print("\n❌ No L4 subsystem nodes found in any graph")
        print("\nExpected 10 subsystems:")
        for slug, description in EXPECTED_L4_SUBSYSTEMS.items():
            print(f"   - {slug}: {description}")
        print("\n➡️  These nodes need to be created")
        return False

    print(f"\n✅ Found {len(found_subsystems)} subsystem nodes:")
    for slug in sorted(found_subsystems.keys()):
        info = found_subsystems[slug]
        print(f"   - {slug}: {info['name']} (in {info['graph']})")

    # Check which are missing
    missing = set(EXPECTED_L4_SUBSYSTEMS.keys()) - set(found_subsystems.keys())
    if missing:
        print(f"\n⚠️  Missing {len(missing)} subsystems:")
        for slug in sorted(missing):
            print(f"   - {slug}: {EXPECTED_L4_SUBSYSTEMS[slug]}")
        print("\n➡️  These nodes need to be created")
        return False

    print(f"\n✅ All 10 L4 subsystems exist!")
    return True


if __name__ == "__main__":
    check_l4_subsystems()
