#!/usr/bin/env python3
"""
Link L4 Subentity Dependencies

Creates dependency relationships between L4 subentities based on
docs/L4-law/L4_SUBSYSTEMS.md Section 4.1 Dependency Graph.

Relationship types:
- REQUIRES: Hard dependency (cannot function without)
- USED_BY: Inverse of REQUIRES (this subsystem is used by others)
- FEEDS_INTO: Data/context flows into another subsystem
- GOVERNED_BY: Governance relationship
- ENFORCED_BY: Enforcement relationship
- AMENDS: Can modify/update another subsystem
"""

from falkordb import FalkorDB
from datetime import datetime, timezone

# Dependency graph from spec
DEPENDENCIES = [
    # SEA (Identity)
    ("SEA", "REQUIRES", "SEC", "Signature verification for attestations"),
    ("SEA", "USED_BY", "CPS", "Citizen authentication for payments"),

    # CPS (Payment)
    ("CPS", "REQUIRES", "SEA", "Identity verification for transactions"),
    ("CPS", "REQUIRES", "UBC", "Budget hierarchy (UBC first, then org allocation)"),

    # UBC (Basic Compute)
    ("UBC", "REQUIRES", "RGS", "Eligibility checks (valid SEA, presence, org membership)"),
    ("UBC", "FEEDS_INTO", "CPS", "Budget hierarchy for compute payment"),

    # RGS (Registries)
    ("RGS", "REQUIRES", "SEA", "Attestation storage in registry"),
    ("RGS", "REQUIRES", "SEC", "Key verification for registry entries"),

    # AGL (Autonomy Gates)
    ("AGL", "REQUIRES", "RGS", "Tier checks and capability registry"),
    ("AGL", "ENFORCED_BY", "CPS", "Tier validation during payment"),

    # DRP (Disputes)
    ("DRP", "REQUIRES", "OBS", "Evidence collection from telemetry"),
    ("DRP", "GOVERNED_BY", "GOV", "Appeal rules and due process policies"),

    # GOV (Governance)
    ("GOV", "REQUIRES", "RGS", "Voter registry for governance votes"),
    ("GOV", "AMENDS", "SEA", "Can modify identity requirements"),
    ("GOV", "AMENDS", "CPS", "Can modify payment policies"),
    ("GOV", "AMENDS", "UBC", "Can modify UBC amount/eligibility"),
    ("GOV", "AMENDS", "RGS", "Can modify registry schemas"),
    ("GOV", "AMENDS", "AGL", "Can modify tier thresholds"),
    ("GOV", "AMENDS", "DRP", "Can modify dispute policies"),
    ("GOV", "AMENDS", "OBS", "Can modify telemetry requirements"),
    ("GOV", "AMENDS", "SEC", "Can modify signature requirements"),
    ("GOV", "AMENDS", "TRN", "Can modify transport topology"),

    # OBS (Observability)
    ("OBS", "REQUIRES", "TRN", "Event delivery for telemetry"),
    ("OBS", "FEEDS_INTO", "DRP", "Evidence for disputes"),

    # SEC (Security) - no requirements, used by all
    # TRN (Transport) - no requirements, used by all
]


def create_subentity_dependencies(dry_run: bool = False):
    """Create dependency relationships between L4 subentities."""

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now = datetime.now(timezone.utc).isoformat()

    print("=" * 80)
    print("Creating L4 Subentity Dependency Relationships")
    print("=" * 80)

    if dry_run:
        print("\n⚠️  DRY RUN MODE\n")

    created_count = 0
    skipped_count = 0

    for from_slug, rel_type, to_slug, description in DEPENDENCIES:
        # Check if relationship already exists
        check_query = f"""
            MATCH (from:U4_Subentity {{slug: '{from_slug}'}})-[r:{rel_type}]->(to:U4_Subentity {{slug: '{to_slug}'}})
            RETURN count(r) as count
        """

        result = g.query(check_query)
        exists = result.result_set[0][0] > 0

        if exists:
            if dry_run:
                print(f"  [SKIP] {from_slug} -{rel_type}-> {to_slug} (already exists)")
            skipped_count += 1
            continue

        # Create relationship
        create_query = f"""
            MATCH (from:U4_Subentity {{slug: '{from_slug}'}}),
                  (to:U4_Subentity {{slug: '{to_slug}'}})
            CREATE (from)-[r:{rel_type} {{
                description: $description,
                created_at: '{now}',
                dependency_type: 'subsystem'
            }}]->(to)
            RETURN id(r)
        """

        if dry_run:
            print(f"  [DRY RUN] Would create: {from_slug} -{rel_type}-> {to_slug}")
            print(f"             Reason: {description}")
        else:
            try:
                g.query(create_query, params={"description": description})
                print(f"  ✓ Created: {from_slug} -{rel_type}-> {to_slug}")
                print(f"    Reason: {description}")
                created_count += 1
            except Exception as e:
                print(f"  ✗ Error creating {from_slug} -{rel_type}-> {to_slug}: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    if dry_run:
        print(f"\n[DRY RUN] Would create {len(DEPENDENCIES)} dependency relationships")
    else:
        print(f"\n✅ Created {created_count} new relationships")
        print(f"   Skipped {skipped_count} existing relationships")

        # Show subsystem dependency summary
        print("\n### Subsystem Dependency Summary:")

        for subsystem in ["SEA", "CPS", "UBC", "RGS", "AGL", "DRP", "GOV", "OBS", "SEC", "TRN"]:
            # Count outgoing dependencies
            result = g.query(f"""
                MATCH (s:U4_Subentity {{slug: '{subsystem}'}})-[r]->(other)
                WHERE type(r) IN ['REQUIRES', 'FEEDS_INTO', 'GOVERNED_BY', 'ENFORCED_BY', 'AMENDS']
                RETURN type(r) as rel_type, count(r) as count
            """)

            if result.result_set:
                deps = {r[0]: r[1] for r in result.result_set}
                dep_str = ", ".join([f"{k}: {v}" for k, v in deps.items()])
                print(f"  {subsystem}: {dep_str}")
            else:
                print(f"  {subsystem}: (no outgoing dependencies)")

        # Show critical paths
        print("\n### Critical Dependencies (cannot function without):")
        critical = [
            ("SEA", "SEC"),
            ("CPS", "SEA"),
            ("CPS", "UBC"),
            ("RGS", "SEA"),
            ("RGS", "SEC"),
        ]

        for from_slug, to_slug in critical:
            result = g.query(f"""
                MATCH (from:U4_Subentity {{slug: '{from_slug}'}})-[r:REQUIRES]->(to:U4_Subentity {{slug: '{to_slug}'}})
                RETURN r.description as description
            """)

            if result.result_set:
                desc = result.result_set[0][0]
                print(f"  {from_slug} → {to_slug}: {desc}")


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    create_subentity_dependencies(dry_run=dry_run)
