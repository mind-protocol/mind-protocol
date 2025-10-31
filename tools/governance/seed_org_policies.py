#!/usr/bin/env python3
"""
Seed Org_Policy Nodes for Membrane-Native Reviewer System

Creates Org_Policy nodes for all organizations in the Mind Protocol ecosystem.
These policies define severity mappings, override rules, and pragma constraints
for mp-lint rule enforcement.

This script is part of Milestone A for the membrane-native reviewer system,
enabling reviewer aggregators to apply org-specific policies when issuing
verdicts on code changes.

Author: Ada Bridgekeeper (architect)
Date: 2025-10-31
Milestone: Reviewer System - Milestone A
Spec: docs/L4-law/membrane_native_reviewer_and_lint_system.md
"""

import sys
import redis
from typing import Dict, List

# ============================================================================
# Organization Registry
# ============================================================================

ORGANIZATIONS = [
    {
        "org_id": "mind-protocol",
        "org_name": "Mind Protocol Foundation",
        "description": "Core protocol organization",
        "level": "L2",
        "strictness": "high"  # high, medium, low
    },
    # Add more organizations as they join the ecosystem
]

# ============================================================================
# Policy Templates by Strictness Level
# ============================================================================

SEVERITY_MAPS = {
    "high": {
        # Protocol Compliance (R-001 through R-007)
        "R-001": "error",  # SCHEMA_EXISTS_ACTIVE
        "R-002": "error",  # TOPIC_MAPPED
        "R-003": "error",  # SIGNATURE_PROFILE
        "R-004": "error",  # CPS_COMPUTE_SETTLEMENT
        "R-005": "error",  # SEA_ATTESTATION
        "R-006": "error",  # NO_YANKED_VERSION
        "R-007": "warning",  # U3/U4_MATCH_LEVEL (warn during migration)

        # Membrane Discipline (R-100, R-101)
        "R-100": "error",  # BUS_ONLY
        "R-101": "error",  # PROJECTION_ONLY_UI

        # Quality Degradation (R-200 series)
        "R-200": "error",  # TODO_OR_HACK
        "R-201": "error",  # QUALITY_DEGRADE
        "R-202": "warning",  # OBSERVABILITY_CUT (print instead of logger)

        # Fallback Antipatterns (R-300 series)
        "R-300": "error",  # BARE_EXCEPT_PASS
        "R-301": "error",  # SILENT_DEFAULT_RETURN
        "R-302": "error",  # FAKE_AVAILABILITY
        "R-303": "warning",  # INFINITE_LOOP_NO_SLEEP

        # Fail-Loud Contract (R-400 series) - CRITICAL
        "R-400": "error",  # FAIL_LOUD_REQUIRED (no pragma allowed)
        "R-401": "error"   # MISSING_FAILURE_CONTEXT
    },
    "medium": {
        # Protocol Compliance
        "R-001": "error",
        "R-002": "error",
        "R-003": "error",
        "R-004": "warning",  # Relaxed for non-production orgs
        "R-005": "warning",  # Relaxed for non-production orgs
        "R-006": "error",
        "R-007": "warning",

        # Membrane Discipline
        "R-100": "error",
        "R-101": "warning",

        # Quality Degradation
        "R-200": "warning",
        "R-201": "warning",
        "R-202": "info",

        # Fallback Antipatterns
        "R-300": "warning",
        "R-301": "warning",
        "R-302": "warning",
        "R-303": "info",

        # Fail-Loud Contract (always error)
        "R-400": "error",  # Non-negotiable
        "R-401": "error"
    },
    "low": {
        # Protocol Compliance
        "R-001": "warning",
        "R-002": "warning",
        "R-003": "warning",
        "R-004": "info",
        "R-005": "info",
        "R-006": "warning",
        "R-007": "info",

        # Membrane Discipline
        "R-100": "warning",
        "R-101": "info",

        # Quality Degradation
        "R-200": "info",
        "R-201": "info",
        "R-202": "info",

        # Fallback Antipatterns
        "R-300": "info",
        "R-301": "info",
        "R-302": "info",
        "R-303": "info",

        # Fail-Loud Contract (always error)
        "R-400": "error",  # Non-negotiable
        "R-401": "error"
    }
}

# ============================================================================
# Override Rules by Strictness
# ============================================================================

OVERRIDE_RULES = {
    "high": {
        "allow_degrade_max_days": 7,   # Strict: max 7 days for quality degradation
        "allow_fallback_max_days": 3,  # Very strict: max 3 days for fallback antipatterns
        "requires_ticket": True,
        "requires_approval": True,  # High-strictness orgs require human approval for overrides
        "max_overrides_per_change": 3  # Limit overrides per change
    },
    "medium": {
        "allow_degrade_max_days": 14,  # Default: 14 days
        "allow_fallback_max_days": 7,  # Default: 7 days
        "requires_ticket": True,
        "requires_approval": False,  # Auto-granted if reason/expiry valid
        "max_overrides_per_change": 5
    },
    "low": {
        "allow_degrade_max_days": 30,  # Relaxed: 30 days
        "allow_fallback_max_days": 14,  # Relaxed: 14 days
        "requires_ticket": False,  # Reason only
        "requires_approval": False,
        "max_overrides_per_change": 10
    }
}

# ============================================================================
# Verdict Thresholds by Strictness
# ============================================================================

VERDICT_THRESHOLDS = {
    "high": {
        "pass_max_errors": 0,  # Zero errors for pass
        "pass_max_warnings": 3,  # Max 3 warnings for pass
        "soft_fail_max_errors": 2,  # 1-2 errors = soft fail (override allowed)
        "hard_fail_min_errors": 3  # 3+ errors = hard fail (no override)
    },
    "medium": {
        "pass_max_errors": 0,
        "pass_max_warnings": 5,
        "soft_fail_max_errors": 5,
        "hard_fail_min_errors": 6
    },
    "low": {
        "pass_max_errors": 2,  # Allow 2 errors for pass
        "pass_max_warnings": 10,
        "soft_fail_max_errors": 10,
        "hard_fail_min_errors": 11
    }
}


def create_org_policy_node(org: Dict, r: redis.Redis, graph_name: str) -> str:
    """Create an Org_Policy node for a given organization."""
    policy_id = f"ORG_POLICY_{org['org_id'].upper().replace('-', '_')}_V1"
    org_ref = f"org:{org['org_id']}"
    strictness = org.get("strictness", "medium")

    # Get policy configuration based on strictness
    severity_map = SEVERITY_MAPS[strictness]
    override_rules = OVERRIDE_RULES[strictness]
    verdict_thresholds = VERDICT_THRESHOLDS[strictness]

    # Build Cypher query
    query = f"""
    // Find or create Organization node
    MERGE (o:Organization {{org_id: '{org['org_id']}'}})
    ON CREATE SET
        o.name = '{org['org_name']}',
        o.description = '{org['description']}',
        o.level = '{org['level']}',
        o.type_name = 'Organization'

    // Create Org_Policy node
    CREATE (p:Org_Policy {{
        policy_id: '{policy_id}',
        org_ref: '{org_ref}',
        name: '{org['org_name']} Reviewer Policy v1',
        description: 'Membrane reviewer policy for {org['org_name']} ({strictness} strictness)',
        strictness: '{strictness}',
        level: '{org['level']}',
        scope_ref: '{org_ref}',
        type_name: 'Org_Policy',

        // Severity mappings (JSON-like string for now, structured in implementation)
        severity_r001: '{severity_map["R-001"]}',
        severity_r002: '{severity_map["R-002"]}',
        severity_r003: '{severity_map["R-003"]}',
        severity_r004: '{severity_map["R-004"]}',
        severity_r005: '{severity_map["R-005"]}',
        severity_r006: '{severity_map["R-006"]}',
        severity_r007: '{severity_map["R-007"]}',
        severity_r100: '{severity_map["R-100"]}',
        severity_r101: '{severity_map["R-101"]}',
        severity_r200: '{severity_map["R-200"]}',
        severity_r201: '{severity_map["R-201"]}',
        severity_r202: '{severity_map["R-202"]}',
        severity_r300: '{severity_map["R-300"]}',
        severity_r301: '{severity_map["R-301"]}',
        severity_r302: '{severity_map["R-302"]}',
        severity_r303: '{severity_map["R-303"]}',
        severity_r400: '{severity_map["R-400"]}',
        severity_r401: '{severity_map["R-401"]}',

        // Override rules
        allow_degrade_max_days: {override_rules['allow_degrade_max_days']},
        allow_fallback_max_days: {override_rules['allow_fallback_max_days']},
        requires_ticket: {str(override_rules['requires_ticket']).lower()},
        requires_approval: {str(override_rules['requires_approval']).lower()},
        max_overrides_per_change: {override_rules['max_overrides_per_change']},

        // Verdict thresholds
        pass_max_errors: {verdict_thresholds['pass_max_errors']},
        pass_max_warnings: {verdict_thresholds['pass_max_warnings']},
        soft_fail_max_errors: {verdict_thresholds['soft_fail_max_errors']},
        hard_fail_min_errors: {verdict_thresholds['hard_fail_min_errors']},

        // Metadata
        created_at: datetime(),
        version: '1.0.0',
        status: 'active'
    }})

    // Link policy to organization
    WITH o, p
    MERGE (o)-[:GOVERNED_BY]->(p)

    RETURN p.policy_id as policy_id
    """

    result = r.execute_command("GRAPH.QUERY", graph_name, query)
    return policy_id


def seed_org_policies():
    """Seed Org_Policy nodes for all organizations."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    graph_name = "collective_n2"  # Organizational graph (L2)

    print("🏛️  Org_Policy Seed Script - Membrane-Native Reviewer System")
    print("=" * 70)
    print()
    print(f"Target Graph: {graph_name} (L2 organizational consciousness)")
    print(f"Organizations: {len(ORGANIZATIONS)}")
    print()

    created_policies = []

    for org in ORGANIZATIONS:
        print(f"📋 Creating policy for: {org['org_name']}")
        print(f"   Org ID: {org['org_id']}")
        print(f"   Strictness: {org.get('strictness', 'medium')}")

        try:
            policy_id = create_org_policy_node(org, r, graph_name)
            created_policies.append(policy_id)

            strictness = org.get("strictness", "medium")
            severity_map = SEVERITY_MAPS[strictness]
            override_rules = OVERRIDE_RULES[strictness]

            print(f"   ✅ Policy created: {policy_id}")
            print(f"      R-400 (Fail-Loud): {severity_map['R-400']} (CRITICAL - no pragma)")
            print(f"      R-300 series: {severity_map['R-300']} (Fallback antipatterns)")
            print(f"      Override max days: degrade={override_rules['allow_degrade_max_days']}, fallback={override_rules['allow_fallback_max_days']}")
            print()

        except Exception as e:
            print(f"   ❌ Error creating policy: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 70)
    print(f"✅ Org policy seed complete")
    print()
    print("Summary:")
    print(f"  - Created {len(created_policies)} Org_Policy nodes")
    print(f"  - Target graph: {graph_name}")
    print()
    print("Policy Structure:")
    print("  - Severity mappings for 17 rules (R-001 through R-401)")
    print("  - Override rules (pragma max days, ticket requirements)")
    print("  - Verdict thresholds (pass/soft_fail/hard_fail)")
    print()
    print("Strictness Levels:")
    print("  🔴 high: Zero tolerance (7-day degrade, 3-day fallback, approval required)")
    print("  🟡 medium: Balanced (14-day degrade, 7-day fallback, auto-granted)")
    print("  🟢 low: Permissive (30-day degrade, 14-day fallback, reason only)")
    print()
    print("Critical Rules (always error):")
    print("  - R-400 (Fail-Loud): No pragma allowed - violations must be fixed")
    print("  - R-401 (Missing failure context): Required fields enforced")
    print()
    print("Next Steps:")
    print("  1. Reviewer aggregator reads Org_Policy nodes via Cypher query")
    print("  2. Apply severity overrides per org (e.g., R-200 = warning for org A, error for org B)")
    print("  3. Validate override requests against policy constraints")
    print("  4. Issue verdicts (pass/soft_fail/hard_fail) based on thresholds")
    print()
    print("Query to verify:")
    print(f"  MATCH (o:Organization)-[:GOVERNED_BY]->(p:Org_Policy)")
    print(f"  RETURN o.org_id, p.policy_id, p.strictness, p.severity_r400")


if __name__ == "__main__":
    try:
        seed_org_policies()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
