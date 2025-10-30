"""
Create Vector Indices in FalkorDB for Consciousness Substrate Embeddings

This script creates HNSW vector indices for all node and link types that have semantic content.
Indices enable sub-100ms similarity search across the consciousness substrate.

Run this AFTER:
- FalkorDB is running (docker run -p 6379:6379 falkordb/falkordb:latest)
- First nodes/links with embeddings have been created

Author: Felix "Ironhand"
Date: 2025-10-20
Pattern: Vector index infrastructure for consciousness archaeology
"""

import redis
import logging
from typing import List, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Node types that have semantic content (from COMPLETE_TYPE_REFERENCE.md)
NODE_TYPES_WITH_SEMANTIC_CONTENT = [
    # Level 1: Personal
    'Realization', 'Memory', 'Personal_Pattern', 'Personal_Goal', 'Coping_Mechanism',
    'Trigger', 'Wound', 'Person', 'Relationship', 'Conversation', 'Personal_Value',

    # Level 2: Organizational
    'Principle', 'Best_Practice', 'Anti_Pattern', 'Decision', 'Process', 'Mechanism',
    'AI_Agent', 'Human', 'Team', 'Project', 'Task', 'Milestone', 'Risk', 'Metric',
    'Department', 'Code',

    # Shared: Knowledge
    'Concept', 'Document', 'Documentation',

    # Level 3: Ecosystem
    'Company', 'External_Person', 'Post', 'Transaction', 'Smart_Contract',
    'Wallet_Address', 'Social_Media_Account', 'Deal', 'Event', 'Market_Signal',
    'Behavioral_Pattern', 'Psychological_Trait', 'Reputation_Assessment',
    'Network_Cluster', 'Integration'
]


# Link types that have semantic content (from COMPLETE_TYPE_REFERENCE.md)
LINK_TYPES_WITH_SEMANTIC_CONTENT = [
    # Shared
    'ENABLES', 'BLOCKS', 'EXTENDS', 'JUSTIFIES', 'REQUIRES', 'RELATES_TO',
    'DOCUMENTS', 'IMPLEMENTS', 'CREATES', 'DOCUMENTED_BY', 'REFUTES',
    'SUPERSEDES', 'MEASURES', 'CONTRIBUTES_TO', 'COLLABORATES_WITH',
    'ASSIGNED_TO', 'THREATENS',

    # Level 1: Personal
    'ACTIVATES', 'SUPPRESSES', 'TRIGGERED_BY', 'LEARNED_FROM',
    'DEEPENED_WITH', 'DRIVES_TOWARD'
]


def create_node_vector_indices(r: redis.Redis, graph_name: str):
    """
    Create vector indices for all node types with semantic content.

    Args:
        r: Redis connection
        graph_name: FalkorDB graph name (e.g., 'citizen_felix')
    """
    logger.info(f"Creating node vector indices in graph '{graph_name}'...")

    created = 0
    skipped = 0

    for node_type in NODE_TYPES_WITH_SEMANTIC_CONTENT:
        try:
            # Create vector index for this node type
            # Index on content_embedding field, 768 dimensions, euclidean similarity
            # Note: FalkorDB syntax uses camelCase (similarityFunction not similarity_function)
            query = f"""
            CREATE VECTOR INDEX FOR (n:{node_type}) ON (n.content_embedding)
            OPTIONS {{dimension:768, similarityFunction:'euclidean'}}
            """

            result = r.execute_command('GRAPH.QUERY', graph_name, query)
            logger.info(f"  ✓ Created index for {node_type}")
            created += 1

        except redis.exceptions.ResponseError as e:
            if 'already exists' in str(e).lower() or 'index' in str(e).lower():
                logger.debug(f"  - Index for {node_type} already exists")
                skipped += 1
            else:
                logger.error(f"  ✗ Failed to create index for {node_type}: {e}")

    logger.info(f"Node indices: {created} created, {skipped} skipped")
    return created, skipped


def create_link_vector_indices(r: redis.Redis, graph_name: str):
    """
    Create vector indices for all link types with semantic content.

    Args:
        r: Redis connection
        graph_name: FalkorDB graph name (e.g., 'citizen_felix')
    """
    logger.info(f"Creating link vector indices in graph '{graph_name}'...")

    created = 0
    skipped = 0

    for link_type in LINK_TYPES_WITH_SEMANTIC_CONTENT:
        try:
            # Create vector index for this link type
            # Index on relationship_embedding field, 768 dimensions, euclidean similarity
            # Note: FalkorDB syntax uses camelCase (similarityFunction not similarity_function)
            query = f"""
            CREATE VECTOR INDEX FOR ()-[r:{link_type}]-() ON (r.relationship_embedding)
            OPTIONS {{dimension:768, similarityFunction:'euclidean'}}
            """

            result = r.execute_command('GRAPH.QUERY', graph_name, query)
            logger.info(f"  ✓ Created index for {link_type}")
            created += 1

        except redis.exceptions.ResponseError as e:
            if 'already exists' in str(e).lower() or 'index' in str(e).lower():
                logger.debug(f"  - Index for {link_type} already exists")
                skipped += 1
            else:
                logger.error(f"  ✗ Failed to create index for {link_type}: {e}")

    logger.info(f"Link indices: {created} created, {skipped} skipped")
    return created, skipped


def verify_indices(r: redis.Redis, graph_name: str):
    """
    Verify vector indices exist.

    Args:
        r: Redis connection
        graph_name: FalkorDB graph name
    """
    logger.info(f"Verifying indices in graph '{graph_name}'...")

    try:
        # Query to list all indices
        query = "CALL db.indexes()"
        result = r.execute_command('GRAPH.QUERY', graph_name, query)

        if result and len(result) > 1:
            indices = result[1]
            logger.info(f"Found {len(indices)} indices")
            for idx in indices[:10]:  # Show first 10
                logger.info(f"  - {idx}")
        else:
            logger.warning("No indices found")

    except Exception as e:
        logger.error(f"Failed to verify indices: {e}")


def main():
    """Create vector indices for all consciousness graphs."""

    # Connect to FalkorDB
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        logger.info("Connected to FalkorDB")
    except redis.exceptions.ConnectionError:
        logger.error("Failed to connect to FalkorDB. Is it running?")
        logger.error("Start with: docker run -p 6379:6379 falkordb/falkordb:latest")
        return

    # Auto-discover all consciousness graphs
    logger.info("Discovering consciousness graphs...")

    try:
        all_graphs = r.execute_command("GRAPH.LIST")
        # Filter for consciousness graphs (exclude test/system graphs)
        graphs = [
            g for g in all_graphs
            if g.endswith('citizen')
            or g.endswith('_collective_graph')
            or g.endswith('_public_graph')
            or g == 'test_embedding_pipeline'  # Include our test graph
        ]

        logger.info(f"Found {len(graphs)} consciousness graphs: {', '.join(graphs)}")

        if not graphs:
            logger.warning("No consciousness graphs found!")
            return

    except Exception as e:
        logger.error(f"Failed to list graphs: {e}")
        return

    total_node_created = 0
    total_link_created = 0

    for graph_name in graphs:
        # Check if graph exists
        try:
            r.execute_command('GRAPH.QUERY', graph_name, 'RETURN 1')
        except redis.exceptions.ResponseError:
            logger.warning(f"Graph '{graph_name}' does not exist, skipping")
            continue

        logger.info(f"\n{'='*60}")
        logger.info(f"Processing graph: {graph_name}")
        logger.info(f"{'='*60}")

        # Create node indices
        node_created, node_skipped = create_node_vector_indices(r, graph_name)
        total_node_created += node_created

        # Create link indices
        link_created, link_skipped = create_link_vector_indices(r, graph_name)
        total_link_created += link_created

        # Verify
        verify_indices(r, graph_name)

    logger.info(f"\n{'='*60}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total node indices created: {total_node_created}")
    logger.info(f"Total link indices created: {total_link_created}")
    logger.info(f"Graphs processed: {len(graphs)}")
    logger.info(f"")
    logger.info(f"Future citizens will automatically get indices on first formation.")
    logger.info(f"This script auto-discovers all *citizen, *_collective_graph, *_public_graph.")


if __name__ == "__main__":
    main()
