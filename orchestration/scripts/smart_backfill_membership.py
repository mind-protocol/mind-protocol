"""
Smart Entity Membership Backfill

Assigns entity membership to orphan nodes using semantic similarity scoring:
- Link structure similarity (neighbor overlap with entity members)
- Entity quality metrics (cohesion × activity)
- Learned weight priors (not magic 1.0)
- MERGE-based idempotency

Architecture: Entity-first, respects natural learning physics
Author: Iris "The Aperture"
Date: 2025-10-26
"""

import redis
import logging
import sys
import csv
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter

# Add repository root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_orphan_nodes(graph_name: str, r: redis.Redis) -> List[Dict[str, Any]]:
    """
    Get all nodes without MEMBER_OF edges.

    Returns:
        List of {id, name, node_type, labels} dicts
    """
    query = """
    MATCH (n)
    WHERE NOT (n)-[:MEMBER_OF]->(:Subentity)
    AND NOT 'Subentity' IN labels(n)
    AND NOT 'ConsciousnessState' IN labels(n)
    RETURN n.id as id, n.name as name, n.node_type as node_type, labels(n) as labels
    LIMIT 10000
    """

    try:
        result = r.execute_command('GRAPH.QUERY', graph_name, query)
        nodes = []

        # Result format: [header, rows_list, stats]
        if len(result) > 1 and result[1]:
            for row in result[1]:  # result[1] is list of rows
                nodes.append({
                    'id': row[0],
                    'name': row[1],
                    'node_type': row[2],
                    'labels': row[3]
                })

        return nodes
    except Exception as e:
        logger.error(f"Failed to query orphan nodes in {graph_name}: {e}")
        return []


def get_entities(graph_name: str, r: redis.Redis) -> List[Dict[str, Any]]:
    """Get all Subentity nodes with their metrics."""
    query = """
    MATCH (e:Subentity)
    RETURN e.id as id, e.name as name,
           e.coherence as coherence,
           e.energy_runtime as energy
    """

    try:
        result = r.execute_command('GRAPH.QUERY', graph_name, query)
        entities = []

        if len(result) > 1 and result[1]:
            for row in result[1]:
                entities.append({
                    'id': row[0],
                    'name': row[1],
                    'coherence': row[2] if row[2] is not None else 0.5,
                    'energy': row[3] if row[3] is not None else 0.0
                })

        return entities
    except Exception as e:
        logger.error(f"Failed to query entities in {graph_name}: {e}")
        return []


def get_entity_members(graph_name: str, entity_id: str, r: redis.Redis) -> List[str]:
    """Get all node IDs that are members of this entity."""
    query = """
    MATCH (n)-[:MEMBER_OF]->(e:Subentity {id: $entity_id})
    RETURN n.id as node_id
    """

    try:
        result = r.execute_command('GRAPH.QUERY', graph_name, query,
                                   f"CYPHER entity_id='{entity_id}'")
        members = []

        if len(result) > 1 and result[1]:
            for row in result[1]:
                members.append(row[0])

        return members
    except Exception as e:
        logger.error(f"Failed to query entity members: {e}")
        return []


def get_node_neighbors(graph_name: str, node_id: str, r: redis.Redis) -> List[str]:
    """Get all neighbor node IDs (both directions)."""
    query = """
    MATCH (n {id: $node_id})--(neighbor)
    WHERE NOT 'Subentity' IN labels(neighbor)
    RETURN DISTINCT neighbor.id as neighbor_id
    """

    try:
        result = r.execute_command('GRAPH.QUERY', graph_name, query,
                                   f"CYPHER node_id='{node_id}'")
        neighbors = []

        if len(result) > 1 and result[1]:
            for row in result[1]:
                if row[0]:  # Skip None values
                    neighbors.append(row[0])

        return neighbors
    except Exception as e:
        logger.error(f"Failed to query node neighbors: {e}")
        return []


def compute_link_similarity(node_neighbors: List[str],
                           entity_members: List[str]) -> float:
    """
    Compute similarity based on neighbor overlap.

    Returns:
        Jaccard similarity: |intersection| / |union|
    """
    if not node_neighbors or not entity_members:
        return 0.0

    node_set = set(node_neighbors)
    entity_set = set(entity_members)

    intersection = len(node_set & entity_set)
    union = len(node_set | entity_set)

    if union == 0:
        return 0.0

    return intersection / union


def compute_entity_quality(entity: Dict[str, Any]) -> float:
    """
    Compute entity quality score.

    Quality = (1 + coherence) × (1 + normalized_energy)
    """
    coherence = entity.get('coherence', 0.5)
    energy = entity.get('energy', 0.0)

    # Normalize energy to [0, 1] (assuming typical range 0-10)
    normalized_energy = min(1.0, energy / 10.0)

    quality = (1.0 + coherence) * (1.0 + normalized_energy)
    return quality


def score_node_for_entity(node_id: str,
                          entity: Dict[str, Any],
                          graph_name: str,
                          r: redis.Redis,
                          entity_members_cache: Dict[str, List[str]],
                          node_neighbors_cache: Dict[str, List[str]]) -> Tuple[float, Dict[str, float]]:
    """
    Score how well a node fits an entity.

    Score = similarity × quality

    Returns:
        (total_score, {similarity, quality, coherence, energy})
    """
    entity_id = entity['id']

    # Get entity members (cached)
    if entity_id not in entity_members_cache:
        entity_members_cache[entity_id] = get_entity_members(graph_name, entity_id, r)
    entity_members = entity_members_cache[entity_id]

    # Get node neighbors (cached)
    if node_id not in node_neighbors_cache:
        node_neighbors_cache[node_id] = get_node_neighbors(graph_name, node_id, r)
    node_neighbors = node_neighbors_cache[node_id]

    # Compute components
    similarity = compute_link_similarity(node_neighbors, entity_members)
    quality = compute_entity_quality(entity)

    # Total score
    score = similarity * quality

    details = {
        'similarity': similarity,
        'quality': quality,
        'coherence': entity.get('coherence', 0.5),
        'energy': entity.get('energy', 0.0)
    }

    return score, details


def choose_entity_for_node(node_id: str,
                           entities: List[Dict[str, Any]],
                           graph_name: str,
                           r: redis.Redis,
                           entity_members_cache: Dict[str, List[str]],
                           node_neighbors_cache: Dict[str, List[str]]) -> Tuple[str, float, Dict[str, float]]:
    """
    Choose best entity for a node.

    Returns:
        (entity_id, score, score_details)
    """
    scored = []

    for entity in entities:
        score, details = score_node_for_entity(
            node_id, entity, graph_name, r,
            entity_members_cache, node_neighbors_cache
        )
        scored.append((entity['id'], entity['name'], score, details))

    # Sort by score descending
    scored.sort(key=lambda t: t[2], reverse=True)

    if not scored:
        return None, 0.0, {}

    # Return top entity
    entity_id, entity_name, score, details = scored[0]
    logger.info(f"  Chose entity '{entity_name}' (score={score:.3f}, sim={details['similarity']:.3f}, quality={details['quality']:.2f})")

    return entity_id, score, details


def get_weight_prior(graph_name: str, r: redis.Redis) -> float:
    """
    Get learned weight prior for new memberships.

    Uses 25th percentile of existing MEMBER_OF weights, or 0.05 floor.
    """
    query = """
    MATCH ()-[m:MEMBER_OF]->()
    RETURN m.weight as weight
    ORDER BY weight
    """

    try:
        result = r.execute_command('GRAPH.QUERY', graph_name, query)
        weights = []

        if len(result) > 1 and result[1]:
            for row in result[1]:
                if row[0] is not None:
                    weights.append(float(row[0]))

        if weights:
            # Compute 25th percentile
            weights.sort()
            p25_idx = int(len(weights) * 0.25)
            prior = weights[p25_idx]
            logger.info(f"  Learned weight prior: {prior:.3f} (p25 of {len(weights)} existing weights)")
            return prior
        else:
            # No existing weights, use small floor
            logger.info(f"  No existing weights, using floor: 0.05")
            return 0.05

    except Exception as e:
        logger.error(f"Failed to compute weight prior: {e}")
        return 0.05


def assign_membership(graph_name: str,
                     node_id: str,
                     entity_id: str,
                     weight_init: float,
                     r: redis.Redis) -> bool:
    """
    Create MEMBER_OF edge (idempotent MERGE).

    Returns:
        True if edge created, False if already exists or error
    """
    query = """
    MATCH (n {id: $node_id})
    WITH n
    OPTIONAL MATCH (n)-[r:MEMBER_OF]->(:Subentity)
    WITH n, count(r) AS existing
    WHERE existing = 0
    MATCH (e:Subentity {id: $entity_id})
    MERGE (n)-[m:MEMBER_OF]->(e)
    ON CREATE SET
      m.weight = $weight_init,
      m.activation_ema = 0.0,
      m.activation_count = 0,
      m.last_activated_ts = NULL,
      m.created_at = timestamp(),
      m.updated_at = timestamp()
    RETURN n.id, e.id
    """

    try:
        cypher_params = f"CYPHER node_id='{node_id}' entity_id='{entity_id}' weight_init={weight_init}"
        result = r.execute_command('GRAPH.QUERY', graph_name, query, cypher_params)

        # Check if edge was created (result has data rows)
        if len(result) > 1 and len(result[1]) > 0:
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Failed to assign membership for node {node_id}: {e}")
        return False


def backfill_graph(graph_name: str, r: redis.Redis, dry_run: bool = False,
                  output_csv: str = None) -> int:
    """
    Backfill entity memberships for one graph.

    Returns:
        Number of nodes assigned
    """
    logger.info(f"\n{'=' * 80}")
    logger.info(f"Processing: {graph_name}")
    logger.info(f"{'=' * 80}")

    # Get orphan nodes
    orphans = get_orphan_nodes(graph_name, r)
    logger.info(f"Found {len(orphans)} orphan nodes")

    if not orphans:
        logger.info("  ✅ All nodes already have entity attribution")
        return 0

    # Get entities
    entities = get_entities(graph_name, r)
    logger.info(f"Found {len(entities)} entities")

    if not entities:
        logger.error("  ❌ No entities found in graph")
        return 0

    # Get weight prior
    weight_prior = get_weight_prior(graph_name, r)

    # Caches
    entity_members_cache = {}
    node_neighbors_cache = {}

    # Assignment decisions
    decisions = []
    assigned_count = 0

    # Process each orphan
    for i, node in enumerate(orphans):
        node_id = node['id']
        node_name = node.get('name', 'unknown')

        logger.info(f"[{i+1}/{len(orphans)}] Processing node: {node_name} (id={node_id})")

        # Choose entity
        entity_id, score, details = choose_entity_for_node(
            node_id, entities, graph_name, r,
            entity_members_cache, node_neighbors_cache
        )

        if entity_id is None:
            logger.warning(f"  ⚠️ Could not score node, skipping")
            continue

        # Record decision
        decisions.append({
            'node_id': node_id,
            'node_name': node_name,
            'node_type': node.get('node_type', 'unknown'),
            'entity_id': entity_id,
            'score': score,
            'similarity': details.get('similarity', 0),
            'quality': details.get('quality', 0),
            'coherence': details.get('coherence', 0),
            'energy': details.get('energy', 0),
            'weight_init': weight_prior
        })

        # Assign (unless dry-run)
        if not dry_run:
            success = assign_membership(graph_name, node_id, entity_id, weight_prior, r)
            if success:
                assigned_count += 1
                logger.info(f"  ✅ Assigned membership")
            else:
                logger.warning(f"  ⚠️ Edge already exists or assignment failed")
        else:
            logger.info(f"  [DRY-RUN] Would assign membership")

    # Write CSV
    if output_csv and decisions:
        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'node_id', 'node_name', 'node_type', 'entity_id',
                'score', 'similarity', 'quality', 'coherence', 'energy', 'weight_init'
            ])
            writer.writeheader()
            writer.writerows(decisions)
        logger.info(f"\n📊 Wrote decisions to: {output_csv}")

    return assigned_count


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Smart entity membership backfill')
    parser.add_argument('--graph', type=str, help='Specific graph to process')
    parser.add_argument('--dry-run', action='store_true', help='Show decisions without writing')
    parser.add_argument('--output-csv', type=str, help='Path to write decision CSV')

    args = parser.parse_args()

    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    logger.info("=" * 80)
    logger.info("SMART ENTITY MEMBERSHIP BACKFILL")
    logger.info("=" * 80)

    if args.dry_run:
        logger.info("🔍 DRY-RUN MODE (no writes)")

    # Process graph(s)
    if args.graph:
        logger.info(f"Processing single graph: {args.graph}")
        total = backfill_graph(args.graph, r, dry_run=args.dry_run,
                              output_csv=args.output_csv)
    else:
        # Process all citizen graphs
        graphs = r.execute_command("GRAPH.LIST")
        citizen_graphs = [g for g in graphs if g.startswith('citizen_')]
        logger.info(f"Processing {len(citizen_graphs)} citizen graphs")

        total = 0
        for graph_name in citizen_graphs:
            csv_path = args.output_csv.replace('.csv', f'_{graph_name}.csv') if args.output_csv else None
            count = backfill_graph(graph_name, r, dry_run=args.dry_run,
                                  output_csv=csv_path)
            total += count

    logger.info("=" * 80)
    logger.info(f"{'✅ BACKFILL COMPLETE' if not args.dry_run else '🔍 DRY-RUN COMPLETE'}")
    logger.info(f"   Total nodes {'assigned' if not args.dry_run else 'would be assigned'}: {total}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
