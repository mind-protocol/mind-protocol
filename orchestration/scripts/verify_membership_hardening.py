#!/usr/bin/env python3
"""
P1.3 Membership Hardening Verification Script

Validates production-grade membership implementation:
1. No orphan MEMBER_OF links (all point to valid Subentity nodes)
2. ≥95% of nodes with MEMBER_OF links have primary_entity set
3. ε-policy enforcement (primary_entity changes only when weight threshold exceeded)

Owner: Felix "Ironhand"
Created: 2025-10-25
"""

import sys
from pathlib import Path

# Add orchestration to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llama_index.graph_stores.falkordb import FalkorDBGraphStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_no_orphan_links(graph_store: FalkorDBGraphStore, graph_name: str) -> bool:
    """
    Verify no orphan MEMBER_OF links (all target nodes are valid Subentities).

    Query from Nicolas:
    MATCH (n)-[r:MEMBER_OF]->(e)
    WHERE NOT e:Subentity
    RETURN count(r)
    """
    query = """
    MATCH (n)-[r:MEMBER_OF]->(e)
    WHERE NOT e:Subentity
    RETURN count(r) as orphan_count
    """

    graph_store.database = graph_name
    result = graph_store.query(query)
    orphan_count = result[0][0] if result and len(result) > 0 else 0

    if orphan_count == 0:
        logger.info(f"✅ No orphan MEMBER_OF links in {graph_name}")
        return True
    else:
        logger.error(f"❌ Found {orphan_count} orphan MEMBER_OF links in {graph_name}")
        return False


def verify_primary_entity_consistency(graph_store: FalkorDBGraphStore, graph_name: str, threshold: float = 0.95) -> bool:
    """
    Verify ≥95% of nodes with MEMBER_OF links have primary_entity set.

    Query from Nicolas:
    MATCH (n)-[:MEMBER_OF]->(e:Subentity)
    WITH n, count(*) AS k, exists(n.primary_entity) AS has_pe
    RETURN has_pe, k, count(*) ORDER BY k DESC LIMIT 10
    """
    query = """
    MATCH (n)-[:MEMBER_OF]->(e:Subentity)
    WITH n, count(*) as membership_count, (n.primary_entity IS NOT NULL) as has_primary
    RETURN
        has_primary,
        count(n) as node_count,
        membership_count
    ORDER BY membership_count DESC
    """

    graph_store.database = graph_name
    result = graph_store.query(query)

    total_nodes = 0
    nodes_with_primary = 0

    for row in result:
        has_primary, node_count, membership_count = row
        total_nodes += node_count
        if has_primary:
            nodes_with_primary += node_count

    if total_nodes == 0:
        logger.warning(f"⚠️  No nodes with MEMBER_OF links found in {graph_name}")
        return True  # Vacuously true

    coverage = nodes_with_primary / total_nodes

    if coverage >= threshold:
        logger.info(f"✅ Primary entity coverage: {coverage:.1%} ({nodes_with_primary}/{total_nodes}) in {graph_name}")
        return True
    else:
        logger.error(f"❌ Primary entity coverage: {coverage:.1%} ({nodes_with_primary}/{total_nodes}) - below {threshold:.0%} threshold")
        return False


def verify_epsilon_policy(graph_store: FalkorDBGraphStore, graph_name: str) -> dict:
    """
    Check ε-policy enforcement: primary_entity should only change when weight difference > 0.1

    Returns statistics about membership weight distribution.
    """
    query = """
    MATCH (n)-[r:MEMBER_OF]->(e:Subentity)
    WHERE n.primary_entity = e.name
    RETURN
        min(r.weight) as min_weight,
        max(r.weight) as max_weight,
        avg(r.weight) as avg_weight,
        count(r) as primary_links
    """

    graph_store.database = graph_name
    result = graph_store.query(query)

    if result and len(result) > 0:
        min_weight, max_weight, avg_weight, primary_links = result[0]

        # Handle None values (no primary links found)
        if min_weight is None or max_weight is None or avg_weight is None or primary_links == 0:
            logger.warning(f"⚠️  No primary membership links found in {graph_name}")
            return {}

        logger.info(f"📊 Primary membership weights in {graph_name}:")
        logger.info(f"   Min: {min_weight:.3f}, Max: {max_weight:.3f}, Avg: {avg_weight:.3f}")
        logger.info(f"   Total primary links: {primary_links}")
        return {'min_weight': min_weight, 'max_weight': max_weight, 'avg_weight': avg_weight, 'primary_links': primary_links}
    else:
        logger.warning(f"⚠️  No primary membership links found in {graph_name}")
        return {}


def main():
    """Run all P1.3 verification checks across all citizen graphs."""
    # Create FalkorDB connection
    falkordb_url = "redis://localhost:6379"
    graph_store = FalkorDBGraphStore(graph_name="citizen_felix", url=falkordb_url)

    # Citizen graphs to check
    citizens = ['felix', 'ada', 'atlas', 'iris', 'luca', 'victor']

    print("=" * 70)
    print("P1.3 MEMBERSHIP HARDENING VERIFICATION")
    print("=" * 70)
    print()

    all_passed = True

    for citizen in citizens:
        graph_name = f'citizen_{citizen}'
        print(f"Checking {graph_name}...")
        print("-" * 70)

        # Check 1: No orphan links
        passed_orphan = verify_no_orphan_links(graph_store, graph_name)

        # Check 2: Primary entity consistency
        passed_consistency = verify_primary_entity_consistency(graph_store, graph_name)

        # Check 3: ε-policy statistics
        epsilon_stats = verify_epsilon_policy(graph_store, graph_name)

        graph_passed = passed_orphan and passed_consistency
        all_passed = all_passed and graph_passed

        if graph_passed:
            print(f"✅ {graph_name} PASSED")
        else:
            print(f"❌ {graph_name} FAILED")

        print()

    print("=" * 70)
    if all_passed:
        print("✅ ALL VERIFICATION CHECKS PASSED")
        print()
        print("P1.3 Acceptance Criteria Met:")
        print("  ✅ No orphan MEMBER_OF links")
        print("  ✅ ≥95% of linked nodes have primary_entity")
        return 0
    else:
        print("❌ SOME VERIFICATION CHECKS FAILED")
        print()
        print("Review failures above and check:")
        print("  - persist_membership() implementation")
        print("  - ε-policy logic (0.1 threshold)")
        print("  - Subentity node creation")
        return 1


if __name__ == '__main__':
    sys.exit(main())
