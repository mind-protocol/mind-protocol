"""
Create database indexes for entity membership queries.

Indexes created:
1. Subentity.name - Fast entity lookup by name
2. Node.primary_entity - Fast member queries by entity

Usage:
    python orchestration/scripts/create_membership_indexes.py

Author: Atlas
Date: 2025-10-25
"""

import redis
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_indexes_for_graph(graph_name: str, r: redis.Redis) -> None:
    """
    Create membership-related indexes for a single graph.

    Args:
        graph_name: Name of the graph
        r: Redis connection
    """
    logger.info(f"Creating indexes for {graph_name}...")

    indexes = [
        # Index on Subentity.name for fast entity lookup
        {
            'query': "CREATE INDEX FOR (e:Subentity) ON (e.name)",
            'description': "Subentity.name (entity lookup)"
        },
        # Index on Node.primary_entity for fast member queries
        {
            'query': "CREATE INDEX FOR (n:Node) ON (n.primary_entity)",
            'description': "Node.primary_entity (member queries)"
        },
        # Index on Subentity.id for ID-based lookup
        {
            'query': "CREATE INDEX FOR (e:Subentity) ON (e.id)",
            'description': "Subentity.id (ID lookup)"
        }
    ]

    for index in indexes:
        try:
            r.execute_command('GRAPH.QUERY', graph_name, index['query'])
            logger.info(f"  ✅ Created index: {index['description']}")
        except Exception as e:
            error_msg = str(e).lower()
            if 'already exists' in error_msg or 'index already exists' in error_msg:
                logger.debug(f"  ⏭️  Index already exists: {index['description']}")
            else:
                logger.warning(f"  ❌ Failed to create index {index['description']}: {e}")


def main():
    """Create membership indexes for all citizen graphs."""
    logger.info("=" * 80)
    logger.info("MEMBERSHIP INDEX CREATION")
    logger.info("=" * 80)

    # Connect to Redis/FalkorDB
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Get all graph names
    try:
        graphs = r.execute_command("GRAPH.LIST")
        logger.info(f"Found {len(graphs)} graphs")
    except Exception as e:
        logger.error(f"Failed to list graphs: {e}")
        return

    # Create indexes for each citizen graph (skip meta graphs like schema_registry)
    citizen_graphs = [g for g in graphs if g.startswith('citizen_') or g.startswith('org_')]

    for graph_name in citizen_graphs:
        create_indexes_for_graph(graph_name, r)

    logger.info("=" * 80)
    logger.info(f"✅ Index creation complete ({len(citizen_graphs)} graphs processed)")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
