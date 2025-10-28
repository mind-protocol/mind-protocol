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
from typing import List, Sequence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _fetch_existing_index_tokens(graph_name: str, r: redis.Redis) -> Sequence[str]:
    try:
        result = r.execute_command('GRAPH.QUERY', graph_name, "CALL db.indexes()")
    except Exception:
        return []

    if not isinstance(result, (list, tuple)) or len(result) < 2:
        return []

    rows = result[1] or []
    tokens: List[str] = []
    for row in rows:
        tokens.append(str(row).lower())
    return tokens


def _index_exists(existing_tokens: Sequence[str], label: str, prop: str) -> bool:
    target_label = label.lower()
    target_prop = prop.lower()
    for token in existing_tokens:
        if target_label in token and target_prop in token:
            return True
    return False


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
            'description': "Subentity.name (entity lookup)",
            'label': 'Subentity',
            'property': 'name'
        },
        # Index on Node.primary_entity for fast member queries
        {
            'query': "CREATE INDEX FOR (n:Node) ON (n.primary_entity)",
            'description': "Node.primary_entity (member queries)",
            'label': 'Node',
            'property': 'primary_entity'
        },
        # Index on Subentity.id for ID-based lookup
        {
            'query': "CREATE INDEX FOR (e:Subentity) ON (e.id)",
            'description': "Subentity.id (ID lookup)",
            'label': 'Subentity',
            'property': 'id'
        }
    ]

    existing_tokens = _fetch_existing_index_tokens(graph_name, r)

    for index in indexes:
        if index['label'] and index['property'] and _index_exists(existing_tokens, index['label'], index['property']):
            logger.debug(f"  ⏭️  Index already exists: {index['description']}")
            continue

        try:
            r.execute_command('GRAPH.QUERY', graph_name, index['query'])
            logger.info(f"  ✅ Created index: {index['description']}")
            existing_tokens = _fetch_existing_index_tokens(graph_name, r)
        except Exception as e:
            error_msg = str(e).lower()
            if (
                'already exists' in error_msg
                or 'index already exists' in error_msg
                or 'already indexed' in error_msg
            ):
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
