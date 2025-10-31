#!/usr/bin/env python3
"""
Cleanup Duplicate/Empty FalkorDB Graphs

Removes duplicate and empty consciousness graphs that are polluting the database
and causing engine initialization issues.

Author: Felix
Date: 2025-10-30
"""

import logging
from falkordb import FalkorDB

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def cleanup_duplicate_graphs(dry_run: bool = True):
    """
    Delete empty duplicate graphs from FalkorDB.

    Keeps only the primary graphs with data:
    - mind-protocol_felix
    - mind-protocol_atlas
    - etc.

    Deletes:
    - citizen_lucia, citizen_luca, citizen_victor (legacy empty)
    - citizen_ecosystem_mind-protocol_* (duplicate empty)

    Args:
        dry_run: If True, only show what would be deleted (don't actually delete)
    """
    logger.info("=" * 70)
    logger.info("DUPLICATE GRAPH CLEANUP")
    logger.info("=" * 70)
    logger.info(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will delete!)'}")
    logger.info("")

    db = FalkorDB(host='localhost', port=6379)

    # Get all graphs
    all_graphs = db.list_graphs()
    logger.info(f"Found {len(all_graphs)} total graphs in FalkorDB")
    logger.info("")

    # Categorize graphs
    primary_graphs = []  # ecosystem_mind-protocol_*
    legacy_empty = []    # citizen_lucia, citizen_luca, etc. (old format)
    duplicate_empty = [] # citizen_ecosystem_mind-protocol_* (wrongly prefixed)
    other_graphs = []

    for graph_name in all_graphs:
        # Check node count
        try:
            g = db.select_graph(graph_name)
            result = g.query("MATCH (n) RETURN count(n) as node_count")
            node_count = result.result_set[0][0] if result.result_set else 0
        except Exception as e:
            logger.warning(f"Failed to query {graph_name}: {e}")
            node_count = -1

        # Categorize
        if graph_name.startswith("ecosystem_mind-protocol_"):
            primary_graphs.append((graph_name, node_count))
        elif graph_name.startswith("citizen_ecosystem_mind-protocol_"):
            duplicate_empty.append((graph_name, node_count))
        elif graph_name in ["citizen_lucia", "citizen_luca", "citizen_victor", "citizen_felix",
                            "citizen_ada", "citizen_atlas", "citizen_iris"]:
            legacy_empty.append((graph_name, node_count))
        else:
            other_graphs.append((graph_name, node_count))

    # Report findings
    logger.info("PRIMARY GRAPHS (keep these):")
    for name, count in primary_graphs:
        logger.info(f"  ✅ {name}: {count} nodes")
    logger.info("")

    logger.info("LEGACY EMPTY GRAPHS (will delete):")
    for name, count in legacy_empty:
        logger.info(f"  ❌ {name}: {count} nodes")
    logger.info("")

    logger.info("DUPLICATE EMPTY GRAPHS (will delete):")
    for name, count in duplicate_empty:
        logger.info(f"  ❌ {name}: {count} nodes")
    logger.info("")

    if other_graphs:
        logger.info("OTHER GRAPHS (review manually):")
        for name, count in other_graphs:
            logger.info(f"  ⚠️  {name}: {count} nodes")
        logger.info("")

    # Deletion
    to_delete = legacy_empty + duplicate_empty

    if not to_delete:
        logger.info("✅ No graphs to delete!")
        return

    logger.info("=" * 70)
    logger.info(f"WILL DELETE {len(to_delete)} GRAPHS:")
    for name, count in to_delete:
        logger.info(f"  - {name} ({count} nodes)")
    logger.info("=" * 70)
    logger.info("")

    if dry_run:
        logger.info("DRY RUN: No changes made. Run with --live to actually delete.")
        return

    # Confirm deletion
    confirmation = input("Type 'DELETE' to confirm deletion: ")
    if confirmation != "DELETE":
        logger.info("Cancelled.")
        return

    # Delete graphs
    deleted = 0
    failed = 0
    for name, count in to_delete:
        try:
            db.delete_graph(name)
            logger.info(f"  ✅ Deleted {name}")
            deleted += 1
        except Exception as e:
            logger.error(f"  ❌ Failed to delete {name}: {e}")
            failed += 1

    logger.info("")
    logger.info("=" * 70)
    logger.info(f"CLEANUP COMPLETE: {deleted} deleted, {failed} failed")
    logger.info("=" * 70)


if __name__ == "__main__":
    import sys

    dry_run = "--live" not in sys.argv

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")
        print("Run with --live to actually delete graphs\n")

    cleanup_duplicate_graphs(dry_run=dry_run)
