"""
Backfill SubEntity Membership for Existing Nodes

Assigns primary_subentity and MEMBER_OF links for all nodes missing membership.

For nodes without subentity attribution:
1. Query node creation context if available
2. Default to 'translator' subentity (most common consciousness work entity)
3. Set primary_subentity property
4. Create MEMBER_OF link with weight=1.0, role='primary'

Usage:
    python orchestration/scripts/backfill_membership.py [--graph GRAPH_NAME] [--dry-run]

Author: Felix
Date: 2025-10-25
"""

import redis
import logging
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add repository root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_all_citizen_graphs(r: redis.Redis) -> List[str]:
    """Get list of all citizen consciousness graphs using discovery service."""
    try:
        from orchestration.adapters.ws.websocket_server import discover_graphs

        # Use discovery service to find N1 (citizen) graphs
        graphs_dict = discover_graphs(host='localhost', port=6379)
        citizen_graphs = graphs_dict.get('n1_graphs', [])
        return citizen_graphs
    except Exception as e:
        logger.error(f"Failed to list graphs: {e}")
        return []


def get_unattributed_nodes(graph_name: str, r: redis.Redis) -> List[Dict[str, Any]]:
    """
    Get all nodes without primary_subsubentity attribution.

    Returns:
        List of {id, name, node_type} dicts
    """
    query = """
    MATCH (n:Node)
    WHERE n.primary_subentity IS NULL OR n.primary_subentity = ''
    RETURN id(n) as node_id, n.name as name, n.node_type as node_type
    LIMIT 10000
    """

    try:
        result = r.execute_command('GRAPH.QUERY', graph_name, query)
        nodes = []

        # Result format: [header, [row1], [row2], ..., stats]
        if len(result) > 1:
            for row in result[1:-1]:  # Skip header and stats
                nodes.append({
                    'node_id': row[0],
                    'name': row[1],
                    'node_type': row[2]
                })

        return nodes
    except Exception as e:
        logger.error(f"Failed to query unattributed nodes in {graph_name}: {e}")
        return []


def get_default_subentity_id(graph_name: str) -> str:
    """
    Get default subentity ID for a citizen graph.

    Defaults to 'translator' as the most common consciousness work entity.

    Args:
        graph_name: e.g., resolver.citizen("felix")

    Returns:
        Full entity ID: 'SubEntity:translator'
    """
    # The SubEntity ID format is 'SubEntity:{name}' not tied to citizen
    # We default to 'translator' as the most common entity
    return 'SubEntity:translator'


def assign_membership(
    graph_name: str,
    node_name: str,
    subentity_id: str,
    r: redis.Redis,
    dry_run: bool = False
) -> bool:
    """
    Assign node to subentity (set property + create link).

    Args:
        graph_name: Graph to operate on
        node_name: Node.name to assign
        subentity_id: Full entity ID (e.g., 'subentity_citizen_felix_translator')
        r: Redis connection
        dry_run: If True, don't actually write to DB

    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        logger.info(f"  [DRY RUN] Would assign {node_name} → {subentity_id}")
        return True

    query = """
    MATCH (n:Node {name: $node_name})
    MATCH (e:SubEntity {id: $subentity_id})
    SET n.primary_subentity = $subentity_id
    MERGE (n)-[r:MEMBER_OF]->(e)
    SET r.weight = 1.0, r.role = 'primary'
    RETURN n.name, e.id
    """

    try:
        result = r.execute_command(
            'GRAPH.QUERY',
            graph_name,
            query,
            '--params',
            f'{{"node_name": "{node_name}", "subentity_id": "{subentity_id}"}}'
        )

        # Check if update succeeded
        if len(result) > 1 and len(result[1]) > 0:
            return True
        else:
            logger.warning(f"  ⚠️  No match for node={node_name} or entity={entity_id}")
            return False

    except Exception as e:
        logger.error(f"  ✗ Failed to assign {node_name}: {e}")
        return False


def backfill_graph(graph_name: str, r: redis.Redis, dry_run: bool = False) -> int:
    """
    Backfill entity membership for all unattributed nodes in a graph.

    Args:
        graph_name: Graph to process
        r: Redis connection
        dry_run: If True, don't actually write to DB

    Returns:
        Number of nodes successfully attributed
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Processing: {graph_name}")
    logger.info(f"{'='*80}")

    # Get unattributed nodes
    nodes = get_unattributed_nodes(graph_name, r)
    logger.info(f"Found {len(nodes)} unattributed nodes")

    if not nodes:
        logger.info("  ✅ All nodes already have subentity attribution")
        return 0

    # Get default entity for this citizen
    default_subentity_id = get_default_subentity_id(graph_name)
    logger.info(f"Default entity: {default_subentity_id}")

    # Verify entity exists
    subentity_check_query = f"MATCH (e:SubEntity {{id: '{default_subentity_id}'}}) RETURN e.id"
    subentity_result = r.execute_command('GRAPH.QUERY', graph_name, subentity_check_query)
    if len(subentity_result) <= 1 or len(subentity_result[1]) == 0:
        logger.error(f"  ✗ Entity {default_subentity_id} does not exist in {graph_name}")
        logger.error(f"  ✗ Run subentity bootstrap first!")
        return 0

    # Assign membership for each node
    success_count = 0
    for i, node in enumerate(nodes, 1):
        node_name = node['name']
        node_type = node['node_type']

        if (i-1) % 100 == 0 and i > 1:
            logger.info(f"  Progress: {i}/{len(nodes)} nodes processed")

        if assign_membership(graph_name, node_name, default_subentity_id, r, dry_run):
            success_count += 1

    logger.info(f"✅ Assigned {success_count}/{len(nodes)} nodes to {default_subentity_id}")
    return success_count


def main():
    """Main backfill orchestration."""
    parser = argparse.ArgumentParser(description='Backfill entity membership for existing nodes')
    parser.add_argument('--graph', type=str, help='Process specific graph only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without writing to DB')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("SUBENTITY MEMBERSHIP BACKFILL")
    logger.info("=" * 80)

    if args.dry_run:
        logger.warning("⚠️  DRY RUN MODE - No changes will be written to database")

    # Connect to Redis/FalkorDB
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Determine which graphs to process
    if args.graph:
        graphs_to_process = [args.graph]
        logger.info(f"Processing single graph: {args.graph}")
    else:
        graphs_to_process = get_all_citizen_graphs(r)
        logger.info(f"Found {len(graphs_to_process)} citizen graphs")

    # Backfill each graph
    total_attributed = 0
    for graph_name in graphs_to_process:
        attributed = backfill_graph(graph_name, r, args.dry_run)
        total_attributed += attributed

    logger.info("=" * 80)
    logger.info(f"✅ BACKFILL COMPLETE")
    logger.info(f"   Total nodes attributed: {total_attributed}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
