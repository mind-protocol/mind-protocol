"""
One-time migration: node.subsubentity_activations JSON → MEMBER_OF edge properties.

Converts denormalized cache (node.subentity_activations) to canonical edge truth (MEMBER_OF edges).
After migration, node.subentity_activations becomes derived cache rebuilt from edges.

Migration Process:
1. Query all nodes with subentity_activations cache
2. Parse JSON cache
3. Create/update MEMBER_OF edges with activation stats
4. Rebuild caches from edges to ensure consistency
5. Mark migration complete

Usage:
    python orchestration/scripts/migrate_entity_activations_to_edges.py [graph_id]

    # Dry run (preview without executing)
    python orchestration/scripts/migrate_entity_activations_to_edges.py --dry-run

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-25
Integration: MEMBER_OF_EDGE_PERSISTENCE_INTEGRATION.md Integration 6
"""

import sys
import os
import redis
import json
import logging
from typing import Dict, Any, Optional
from falkordb import FalkorDB

# Add orchestration to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def get_falkordb_graph(graph_name: str):
    """
    Get FalkorDB graph object for executing queries.
    Uses FalkorDB Python client's graph.query(query, params) API.
    """
    db = FalkorDB(host='localhost', port=6379)
    return db.select_graph(graph_name)


def migrate_entity_activations_to_edges(
    graph_id: str = "citizen_felix",
    dry_run: bool = False,
    batch_size: int = 1000
) -> int:
    """
    Migrate node.subsubentity_activations cache to MEMBER_OF edge properties.

    For each node with entity_activations:
    1. Parse JSON cache
    2. Create/update MEMBER_OF edges with activation stats
    3. Mark migration complete

    Args:
        graph_id: Target graph to migrate (default: citizen_felix)
        dry_run: If True, preview migration without executing (default: False)
        batch_size: Number of nodes to process per batch (default: 1000)

    Returns:
        Number of subentity activations migrated to edges

    Raises:
        redis.exceptions.ConnectionError: If FalkorDB not accessible
    """
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Starting migration for graph: {graph_id}")

    # Get FalkorDB graph connection
    try:
        graph = get_falkordb_graph(graph_id)
        logger.info("✓ FalkorDB connection established")
    except Exception as e:
        logger.error(f"✗ FalkorDB not accessible: {e}")
        raise

    # Query all nodes with subentity_activations cache
    query = f"""
    MATCH (n:Node)
    WHERE n.subentity_activations IS NOT NULL
    RETURN n.id AS node_id, n.subentity_activations AS cache
    LIMIT {batch_size}
    """

    logger.info(f"Querying nodes with entity_activations (limit: {batch_size})...")
    result = graph.query(query)

    if not result or not result.result_set:
        logger.info("No nodes with subentity_activations found - migration not needed")
        return 0

    logger.info(f"Found {len(result.result_set)} nodes with subentity_activations cache")

    if dry_run:
        logger.info("[DRY RUN] Preview of migration:")

    migrated = 0
    failed = 0

    for row in result.result_set:
        node_id = row[0]
        cache_str = row[1]

        try:
            # Parse JSON cache
            cache = json.loads(cache_str) if isinstance(cache_str, str) else cache_str
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse cache for {node_id}: {e}")
            failed += 1
            continue

        # Migrate each cached subentity activation as MEMBER_OF edge
        for entity_id, stats in cache.items():
            if dry_run:
                logger.info(f"  [DRY RUN] Would migrate: {node_id} -[MEMBER_OF]-> {entity_id}")
                logger.info(f"            Stats: weight={stats.get('weight')}, "
                           f"activation_ema={stats.get('activation_ema')}, "
                           f"last_ts={stats.get('last_ts')}")
                migrated += 1
                continue

            # Execute actual migration (not dry run)
            migrate_query = """
            MATCH (n:Node {id: $node_id})
            MERGE (e:SubEntity {id: $entity_id})
            MERGE (n)-[r:MEMBER_OF]->(e)
            SET r.activation_ema = coalesce($activation_ema, r.activation_ema, 0.0),
                r.last_activated_ts = coalesce($last_ts, r.last_activated_ts),
                r.weight = coalesce($weight, r.weight, 0.0),
                r.updated_at = timestamp(),
                r.migrated_from_cache = true
            """

            params = {
                "node_id": node_id,
                "entity_id": entity_id,
                "activation_ema": stats.get("activation_ema"),
                "last_ts": stats.get("last_ts"),
                "weight": stats.get("weight")
            }

            try:
                graph.query(migrate_query, params)
                migrated += 1
            except Exception as e:
                logger.error(f"Failed to migrate {node_id} → {entity_id}: {e}")
                failed += 1

    # Summary
    logger.info("")
    logger.info("=" * 70)
    if dry_run:
        logger.info(f"[DRY RUN] Migration preview complete")
        logger.info(f"  Would migrate: {migrated} subentity activations")
        logger.info(f"  Would fail: {failed} subentity activations")
    else:
        logger.info(f"✅ Migrated {migrated} subentity activations to MEMBER_OF edges")
        if failed > 0:
            logger.warning(f"⚠️  Failed to migrate {failed} subentity activations")

        # After migration, rebuild caches from edges to ensure consistency
        logger.info("")
        logger.info("Rebuilding caches from canonical edge truth...")
        rebuild_all_caches(graph_id)

    logger.info("=" * 70)

    return migrated


def rebuild_all_caches(graph_id: str, k: int = 10):
    """
    Rebuild all node.subsubentity_activations caches from MEMBER_OF edges.

    Uses APOC-free batch rebuild. If APOC is available, this could be optimized,
    but current implementation works on any FalkorDB installation.

    Args:
        graph_id: Target graph
        k: Number of top entities to cache per node (default: 10)
    """
    logger.info(f"Rebuilding caches for graph {graph_id} (top-{k} entities per node)...")

    # Get FalkorDB graph connection
    graph = get_falkordb_graph(graph_id)

    # Query all nodes that have MEMBER_OF edges
    query = """
    MATCH (n:Node)-[r:MEMBER_OF]->(:SubEntity)
    RETURN DISTINCT n.id AS node_id
    """

    result = graph.query(query)

    if not result or not result.result_set:
        logger.info("No nodes with MEMBER_OF edges found")
        return

    node_ids = [row[0] for row in result.result_set]

    logger.info(f"Rebuilding caches for {len(node_ids)} nodes...")

    rebuilt = 0
    for node_id in node_ids:
        try:
            # Use APOC-free cache rebuild function from falkordb_adapter
            from orchestration.libs.utils.falkordb_adapter import rebuild_node_entity_activations_cache
            rebuild_node_entity_activations_cache(graph_id, node_id, k=k)
            rebuilt += 1
        except Exception as e:
            logger.error(f"Failed to rebuild cache for {node_id}: {e}")

    logger.info(f"✅ Rebuilt {rebuilt}/{len(node_ids)} caches from edges")


if __name__ == "__main__":
    from orchestration.adapters.ws.websocket_server import discover_graphs

    # Parse command line arguments
    dry_run = False
    specific_graph = None

    for arg in sys.argv[1:]:
        if arg == "--dry-run":
            dry_run = True
        elif not arg.startswith("--"):
            specific_graph = arg

    try:
        # Use discovery service to find all citizen graphs
        graphs = discover_graphs(host='localhost', port=6379)
        citizens = graphs.get('n1_graphs', [])

        # If specific graph provided, migrate only that one
        if specific_graph:
            citizens = [specific_graph]
            logger.info(f"Migrating specific graph: {specific_graph}")
        else:
            logger.info(f"Found {len(citizens)} citizen graphs: {citizens}")

        if not citizens:
            logger.warning("No citizen graphs found in FalkorDB")
            sys.exit(0)

        total_migrated = 0
        failed_graphs = []

        for graph_id in citizens:
            try:
                migrated = migrate_entity_activations_to_edges(graph_id, dry_run=dry_run)
                total_migrated += migrated
            except Exception as e:
                logger.error(f"Failed to migrate {graph_id}: {e}")
                failed_graphs.append(graph_id)

        logger.info("")
        logger.info("=" * 70)
        if dry_run:
            logger.info(f"[DRY RUN] Preview complete. Run without --dry-run to execute migration.")
        else:
            logger.info(f"✅ Migration complete: {total_migrated} total subentity activations migrated")
            if failed_graphs:
                logger.warning(f"⚠️  Failed graphs: {failed_graphs}")
        logger.info("=" * 70)

        sys.exit(0 if not failed_graphs else 1)

    except redis.exceptions.ConnectionError:
        logger.error("Cannot connect to FalkorDB (port 6379). Ensure service is running.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
