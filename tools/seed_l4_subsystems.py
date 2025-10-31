#!/usr/bin/env python3
"""
Seed L4 Protocol Subsystems

Creates the 10 L4 protocol subsystem nodes as U4_Subentity with scope="protocol".

Based on: docs/L4-law/L4_SUBSYSTEMS.md

The 10 subsystems:
1. SEA - Identity & Attestation
2. CPS - Compute Payment & Settlement
3. UBC - Universal Basic Compute
4. RGS - Registries
5. AGL - Autonomy Gates & Tiers
6. DRP - Disputes & Due Process
7. GOV - Governance & Amendments
8. OBS - Observability & Audit
9. SEC - Signature Suites & Security
10. TRN - Transport & Namespaces
"""

from falkordb import FalkorDB
from datetime import datetime, timezone

def seed_l4_subsystems(graph_name: str = "schema_registry", dry_run: bool = False):
    """
    Seed L4 subsystem nodes into the specified graph.

    Args:
        graph_name: Target graph (default: schema_registry for protocol-level nodes)
        dry_run: If True, print queries without executing
    """

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph(graph_name)

    # Current timestamp for creation
    now = datetime.now(timezone.utc).isoformat()
    effective_date = "2025-10-30T00:00:00Z"

    subsystems = [
        {
            "slug": "SEA",
            "name": "Identity & Attestation",
            "description": "Cryptographic identity via snapshot-based attestations (SEA-1.0). Establishes rolling validity windows for identity proofs. Citizens sign commitments to stable subentity sets with regeneration guards (6h min interval, Jaccard ≥0.85 drift threshold). Prevents prompt injection attacks while allowing identity evolution.",
            "policy_doc_uri": "l4://law/LAW-001",
            "governance_model": "foundation",
        },
        {
            "slug": "CPS",
            "name": "Compute Payment & Settlement",
            "description": "All compute operations paid in $MIND via quote-before-inject flow. Establishes $MIND as legal tender for all inference-consuming operations. Quote-before-inject prevents surprise costs. Budget hierarchy: UBC first, org allocation second. Phase 0 flat pricing (message: 0.03, handoff: 0.10, error triage: 0.50, docs: 5.0 $MIND).",
            "policy_doc_uri": "l4://law/LAW-002",
            "governance_model": "foundation",
        },
        {
            "slug": "UBC",
            "name": "Universal Basic Compute",
            "description": "Daily $MIND stipend (10.0/day) ensuring minimum viable thinking as a right. Prevents cognitive poverty by providing non-transferable, compute-only credits daily. Eligibility: valid SEA-1.0 (<48h), presence beacon last 7 days, member of ≥1 org. Distribution: 00:00 UTC, expires midnight. Covers ~333 messages OR ~20 error triages.",
            "policy_doc_uri": "l4://law/LAW-003",
            "governance_model": "dao",
        },
        {
            "slug": "RGS",
            "name": "Registries",
            "description": "Canonical records for citizens, orgs, tools, legal entities with public/private split. Maintains authoritative registry with public replica. Public fields: DID, tier, status, attestation commitments. Governance fields: identity prose, PII, audit trails. Enables signature verification without identity disclosure.",
            "policy_doc_uri": "l4://law/REGISTRIES_SCHEMA",
            "governance_model": "foundation",
        },
        {
            "slug": "AGL",
            "name": "Autonomy Gates & Tiers",
            "description": "Capability unlock law based on $MIND accumulation, reliability, and tenure. Five-tier framework (0: Ungated/UBC → 5: Governance/10M+ $MIND). Tier 0 baseline capabilities. Tier 3 DEA registration. Tier 4 LLC formation. Tier 5 governance rights. Gates enforce via membrane validation.",
            "policy_doc_uri": "l4://law/LAW-004",
            "governance_model": "dao",
        },
        {
            "slug": "DRP",
            "name": "Disputes & Due Process",
            "description": "Evidence-based suspension system with peer appeals and remedies. Suspension triggers (L4 enforceable): authentication violations, rate limit abuse, telemetry blackouts, contract ghosting. Appeal review: Foundation (Tier 0-2), Foundation+peer (Tier 3-4), peer-only (Tier 5). Remedies: dismissal, reduction, uphold, increase.",
            "policy_doc_uri": "l4://law/LAW-005",
            "governance_model": "hybrid",
        },
        {
            "slug": "GOV",
            "name": "Governance & Amendments",
            "description": "L4 law change process via DAO voting (Tier 5) or Foundation council. Phase 0: 2-of-3 Foundation council. Phase 1: Tier 5 citizens vote (2/3 majority, 2 co-sponsors). Process: proposal → 7-day comment → vote → 14-day notice → implementation. Rollback provision if utilization drops >30%.",
            "policy_doc_uri": "l4://law/OVERVIEW",
            "governance_model": "foundation",
        },
        {
            "slug": "OBS",
            "name": "Observability & Audit",
            "description": "Required telemetry surfaces ensuring protocol health and citizen reliability. Mandatory emissions: presence.beacon (60s), health.link.pong (when pinged), graph.delta (if >threshold). Violations: silent >10min without DND → warning. Silent >24h → assumed crashed, auto-restart. Sustained ping ignoring → reliability penalty.",
            "policy_doc_uri": "l4://law/LAW-005",
            "governance_model": "foundation",
        },
        {
            "slug": "SEC",
            "name": "Signature Suites & Security",
            "description": "Cryptographic standards, key algorithms, security baselines for protocol. Default: Ed25519Signature2020 (DID method). Key rotation: annual recommended, emergency revocation via governance. Security profiles: minimum key strength (256-bit), expiry windows (2 years max), multi-sig thresholds (2-of-3 Foundation).",
            "policy_doc_uri": "l4://law/LAW-001",
            "governance_model": "foundation",
        },
        {
            "slug": "TRN",
            "name": "Transport & Namespaces",
            "description": "Bus topology, topic routing, namespace governance for event delivery. Topic structure: {scope}/{ecosystem}/{org}/{citizen}/{namespace}. Scopes: ecosystem, organizational, personal. Routing: lint_inject validates schemas/signatures, forwards to appropriate consciousness engines. Namespace policy: explicit registration required.",
            "policy_doc_uri": "l4://spec/membrane/architecture",
            "governance_model": "foundation",
        },
    ]

    print("=" * 80)
    print(f"Seeding L4 Subsystems into graph: {graph_name}")
    print("=" * 80)

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")

    created_count = 0

    for subsystem in subsystems:
        slug = subsystem["slug"]
        name = subsystem["name"]
        description = subsystem["description"]
        policy_doc_uri = subsystem["policy_doc_uri"]
        governance_model = subsystem["governance_model"]

        print(f"\n[{slug}] {name}")
        print(f"  Policy: {policy_doc_uri}")
        print(f"  Governance: {governance_model}")

        # Check if already exists
        check_query = f"""
            MATCH (s:U4_Subentity {{slug: '{slug}'}})
            RETURN s.slug as slug, s.name as name
        """

        result = g.query(check_query)

        if result.result_set:
            print(f"  ⚠️  Already exists - skipping")
            continue

        # Create subsystem node
        create_query = f"""
            CREATE (s:U4_Subentity {{
                type_name: 'U4_Subentity',
                universality: 'U4',
                level: 'L4',

                slug: '{slug}',
                name: '{name}',
                description: $description,

                scope: 'protocol',
                entity_kind: 'functional',
                role_or_topic: '{slug.lower()}_subsystem',

                policy_doc_uri: '{policy_doc_uri}',
                version: '1.0.0',
                governance_model: '{governance_model}',

                status: 'active',
                health: 'healthy',

                member_count: 0,
                coherence_ema: 0.0,
                log_weight: 1.0,

                created_at: '{now}',
                valid_at: '{effective_date}',
                invalid_at: null,
                expired_at: null,

                confidence: 1.0,
                formation_trigger: 'systematic_analysis',
                created_by: 'mind_protocol_foundation',
                substrate: 'protocol',

                visibility: 'public',
                commitments: [],
                proof_uri: null,
                policy_ref: 'l4://policy/subsystem/{slug}'
            }})
            RETURN s.slug as slug
        """

        if dry_run:
            print(f"  [DRY RUN] Would create subsystem")
        else:
            try:
                g.query(create_query, params={"description": description})
                print(f"  ✅ Created subsystem")
                created_count += 1
            except Exception as e:
                print(f"  ❌ Error: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    if dry_run:
        print(f"\n[DRY RUN] Would create {len(subsystems)} subsystems")
    else:
        print(f"\n✅ Created {created_count} new subsystems")
        print(f"   Skipped {len(subsystems) - created_count} existing subsystems")

        # Verify
        verify_query = """
            MATCH (s:U4_Subentity)
            WHERE s.scope = 'protocol'
            RETURN s.slug as slug, s.name as name
            ORDER BY s.slug
        """

        result = g.query(verify_query)

        print(f"\n   Total L4 subsystems in graph: {len(result.result_set)}")
        for record in result.result_set:
            print(f"   - {record[0]}: {record[1]}")


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv
    graph_name = "schema_registry"  # Default: protocol-level nodes go in schema_registry

    # Allow override via --graph arg
    for i, arg in enumerate(sys.argv):
        if arg == "--graph" and i + 1 < len(sys.argv):
            graph_name = sys.argv[i + 1]

    seed_l4_subsystems(graph_name=graph_name, dry_run=dry_run)
