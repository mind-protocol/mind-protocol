"""
Setup MEMBER_OF edge schema - constraints and indexes.

One-time migration script to create constraints and indexes for entity membership edges.
Run once during deployment or as part of migration pipeline.

Usage:
    python orchestration/scripts/setup_membership_schema.py [graph_id]

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-25
Spec: orchestration/MEMBER_OF_EDGE_PERSISTENCE_INTEGRATION.md Integration 1
"""

import sys
import redis
import logging
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Schema constraints and indexes for MEMBER_OF edge-based membership
CONSTRAINTS_AND_INDEXES = [
    # Node & SubEntity unique constraints
    """
    CREATE CONSTRAINT node_id IF NOT EXISTS
    FOR (n:Node) REQUIRE n.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT subentity_id IF NOT EXISTS
    FOR (e:SubEntity) REQUIRE e.id IS UNIQUE
    """,

    # MEMBER_OF edge indexes for query performance
    """
    CREATE INDEX member_of_weight IF NOT EXISTS
    FOR ()-[r:MEMBER_OF]-() ON (r.weight)
    """,
    """
    CREATE INDEX member_of_last_ts IF NOT EXISTS
    FOR ()-[r:MEMBER_OF]-() ON (r.last_activated_ts)
    """,
    """
    CREATE INDEX member_of_activation IF NOT EXISTS
    FOR ()-[r:MEMBER_OF]-() ON (r.activation_ema)
    """
]


def get_falkordb_client():
    """Get Redis client connected to FalkorDB."""
    return redis.Redis(host='localhost', port=6379, decode_responses=False)


def setup_membership_schema(graph_id: str = "citizen_felix") -> int:
    """
    Create constraints and indexes for MEMBER_OF edge schema.

    Args:
        graph_id: FalkorDB graph ID (default: citizen_felix)

    Returns:
        Number of schema operations successfully executed

    Raises:
        redis.exceptions.ConnectionError: If FalkorDB not accessible
        Exception: If schema creation fails unexpectedly
    """
    logger.info(f"Setting up MEMBER_OF schema for graph: {graph_id}")

    client = get_falkordb_client()

    # Verify FalkorDB connectivity
    try:
        client.ping()
        logger.info("✓ FalkorDB connection established")
    except redis.exceptions.ConnectionError as e:
        logger.error(f"✗ FalkorDB not accessible: {e}")
        raise

    successful = 0
    failed = 0

    for i, query in enumerate(CONSTRAINTS_AND_INDEXES, 1):
        query_short = query.strip().split('\n')[1].strip()[:60]  # First meaningful line

        try:
            result = client.execute_command("GRAPH.QUERY", graph_id, query)
            logger.info(f"[{i}/{len(CONSTRAINTS_AND_INDEXES)}] ✓ {query_short}...")
            successful += 1

        except Exception as e:
            error_str = str(e).lower()

            # Idempotent - already exists is OK
            if "already exists" in error_str or "constraint already exists" in error_str:
                logger.info(f"[{i}/{len(CONSTRAINTS_AND_INDEXES)}] ⊘ Already exists: {query_short}...")
                successful += 1
            else:
                logger.error(f"[{i}/{len(CONSTRAINTS_AND_INDEXES)}] ✗ Error: {e}")
                logger.error(f"   Query: {query.strip()}")
                failed += 1

                # Decide whether to continue or abort
                if "syntax error" in error_str or "unknown command" in error_str:
                    logger.error("   Critical error - aborting schema setup")
                    raise

    logger.info("")
    logger.info("=" * 70)
    if failed == 0:
        logger.info(f"✅ Schema setup complete for graph: {graph_id}")
        logger.info(f"   Successfully executed: {successful}/{len(CONSTRAINTS_AND_INDEXES)} operations")
    else:
        logger.warning(f"⚠️  Schema setup completed with errors for graph: {graph_id}")
        logger.warning(f"   Successful: {successful}/{len(CONSTRAINTS_AND_INDEXES)}")
        logger.warning(f"   Failed: {failed}/{len(CONSTRAINTS_AND_INDEXES)}")
    logger.info("=" * 70)

    return successful


if __name__ == "__main__":
    # Allow graph_id override from command line
    graph_id = sys.argv[1] if len(sys.argv) > 1 else "citizen_felix"

    try:
        setup_membership_schema(graph_id)
        sys.exit(0)
    except redis.exceptions.ConnectionError:
        logger.error("Cannot connect to FalkorDB (port 6379). Ensure service is running.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Schema setup failed: {e}")
        sys.exit(1)
