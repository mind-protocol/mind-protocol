"""
Setup FalkorDB Indexes for COACTIVATES_WITH Tracking

Creates required indexes for efficient co-activation edge updates.

Priority 0: COACTIVATES_WITH tracking requires:
1. Index on SubEntity.id for fast MERGE operations
2. Index on COACTIVATES_WITH.last_ts for time-based queries

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26
Spec: docs/specs/v2/subentity/wm_coactivation_tracking.md
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_indexes(graph_name: str) -> None:
    """
    Create FalkorDB indexes for COACTIVATES_WITH tracking.

    Args:
        graph_name: Target graph (e.g., "citizen_felix")
    """
    logger.info(f"Setting up indexes for graph: {graph_name}")
    graph = get_falkordb_graph(graph_name)

    # Index 1: SubEntity.id (for fast MERGE on SubEntity nodes)
    logger.info("Creating index on SubEntity.id...")
    try:
        query = "CREATE INDEX subentity_id IF NOT EXISTS FOR (e:SubEntity) ON (e.id)"
        graph.query(query)
        logger.info("  ✓ Index created: SubEntity.id")
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("  ✓ Index already exists: SubEntity.id")
        else:
            logger.error(f"  ✗ Failed to create index SubEntity.id: {e}")
            raise

    # Index 2: COACTIVATES_WITH.last_ts (for time-based queries)
    # Note: FalkorDB syntax for relationship indexes may vary
    # This is a forward-looking index for future time-based queries
    logger.info("Creating index on COACTIVATES_WITH.last_ts...")
    try:
        # Relationship indexes in FalkorDB use different syntax
        # This may need adjustment based on FalkorDB version
        query = "CREATE INDEX coacts_last_ts IF NOT EXISTS FOR ()-[r:COACTIVATES_WITH]-() ON (r.last_ts)"
        result = graph.query(query)
        logger.info("  ✓ Index created: COACTIVATES_WITH.last_ts")
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("  ✓ Index already exists: COACTIVATES_WITH.last_ts")
        elif "not supported" in str(e).lower() or "syntax error" in str(e).lower():
            logger.warning("  ⚠ Relationship indexes not supported by this FalkorDB version")
            logger.warning("    Time-based queries may be slower without this index")
        else:
            logger.error(f"  ✗ Failed to create index COACTIVATES_WITH.last_ts: {e}")
            # Don't raise - relationship indexes are optional optimization

    logger.info("Index setup complete")


if __name__ == "__main__":
    from orchestration.adapters.ws.websocket_server import discover_graphs

    logger.info("=" * 60)
    logger.info("FalkorDB Index Setup - COACTIVATES_WITH Tracking")
    logger.info("=" * 60)

    # Use discovery service to find all citizen graphs (N1 level)
    graphs = discover_graphs(host='localhost', port=6379)
    citizens = graphs.get('n1_graphs', [])

    if not citizens:
        logger.warning("No citizen graphs found in FalkorDB")
        import sys
        sys.exit(0)

    logger.info(f"Found {len(citizens)} citizen graphs: {citizens}")

    for citizen in citizens:
        try:
            setup_indexes(citizen)
            logger.info("")
        except Exception as e:
            logger.error(f"Failed to setup indexes for {citizen}: {e}")
            logger.error("Continuing with next citizen...")
            logger.info("")

    logger.info("=" * 60)
    logger.info("Index setup complete for all citizens")
    logger.info("=" * 60)
