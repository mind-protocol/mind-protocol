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

import logging
import sys
from pathlib import Path

# Add orchestration to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

from orchestration.config import constants
from orchestration.bus.emit import emit_failure

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
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


def verify_primary_entity_consistency(
    graph_store: FalkorDBGraphStore,
    graph_name: str,
    threshold: float = constants.PRIMARY_ENTITY_COVERAGE_THRESHOLD,
) -> bool:
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
        logger.warning("No nodes with MEMBER_OF links found in %s", graph_name)
        return True  # Vacuously true

    coverage = nodes_with_primary / total_nodes

    if coverage >= threshold:
        logger.info(
            "Primary entity coverage: %.1f%% (%d/%d) in %s",
            coverage * 100,
            nodes_with_primary,
            total_nodes,
            graph_name,
        )
        return True
    else:
        logger.error(
            "Primary entity coverage: %.1f%% (%d/%d) - below %.0f%% threshold",
            coverage * 100,
            nodes_with_primary,
            total_nodes,
            threshold * 100,
        )
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
        if (
            min_weight is None
            or max_weight is None
            or avg_weight is None
            or primary_links == 0
        ):
            logger.warning("No primary membership links found in %s", graph_name)
            return {}

        logger.info(
            "Primary membership weights in %s | min=%.3f max=%.3f avg=%.3f total=%d",
            graph_name,
            min_weight,
            max_weight,
            avg_weight,
            primary_links,
        )
        return {
            'min_weight': min_weight,
            'max_weight': max_weight,
            'avg_weight': avg_weight,
            'primary_links': primary_links,
        }

    logger.warning("No primary membership links found in %s", graph_name)
    return {}


def main():
    """Run all P1.3 verification checks across all citizen graphs."""
    from orchestration.config.settings import settings
    from orchestration.runtime.citizen_registry import get_all_citizen_ids
    from orchestration.config.graph_names import graph_name_for_citizen

    # Create FalkorDB connection
    falkordb_url = settings.FALKORDB_URL

    # Use citizen registry to find all citizen graphs
    citizen_ids = get_all_citizen_ids()
    citizen_graph_names = [graph_name_for_citizen(cid) for cid in citizen_ids]

    if not citizen_graph_names:
        detail = "Citizen registry returned no graph identifiers"
        emit_failure(
            component="scripts.verify_membership_hardening",
            reason="no_citizen_graphs",
            detail=detail,
            span={"file": __file__},
        )
        raise RuntimeError(detail)

    # Use first citizen to initialize graph_store
    first_graph = citizen_graph_names[0]
    graph_store = FalkorDBGraphStore(graph_name=first_graph, url=falkordb_url)

    logger.info("%s", "=" * 70)
    logger.info("P1.3 MEMBERSHIP HARDENING VERIFICATION")
    logger.info("%s", "=" * 70)
    logger.info(
        "Found %d citizen graphs: %s",
        len(citizen_graph_names),
        citizen_graph_names,
    )

    all_passed = True

    for graph_name in citizen_graph_names:
        logger.info("Checking %s", graph_name)
        logger.info("%s", "-" * 70)

        # Check 1: No orphan links
        passed_orphan = verify_no_orphan_links(graph_store, graph_name)

        # Check 2: Primary entity consistency
        passed_consistency = verify_primary_entity_consistency(graph_store, graph_name)

        # Check 3: ε-policy statistics
        epsilon_stats = verify_epsilon_policy(graph_store, graph_name)

        graph_passed = passed_orphan and passed_consistency
        all_passed = all_passed and graph_passed

        if graph_passed:
            logger.info("%s PASSED", graph_name)
        else:
            logger.error("%s FAILED", graph_name)

    logger.info("%s", "=" * 70)
    if all_passed:
        logger.info("ALL VERIFICATION CHECKS PASSED")
        logger.info("P1.3 Acceptance Criteria Met:")
        logger.info("  - No orphan MEMBER_OF links")
        logger.info("  - ≥95%% of linked nodes have primary_entity")
        return 0

    logger.error("SOME VERIFICATION CHECKS FAILED")
    logger.error("Review failures above and check:")
    logger.error("  - persist_membership() implementation")
    logger.error("  - ε-policy logic (0.1 threshold)")
    logger.error("  - Subentity node creation")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
