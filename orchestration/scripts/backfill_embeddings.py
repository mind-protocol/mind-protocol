"""
Backfill Embeddings for All Existing Nodes

Generates embeddings for all nodes in consciousness graphs so vector search works.

For each node:
1. Generate embeddable_text from semantic fields
2. Create 768-dim embedding vector
3. Update node with both fields
4. Create vector indices for fast search

Author: Felix "Ironhand"
Date: 2025-10-21 (updated from 2025-10-17 version)
"""

import redis
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add repository root to path (go up two levels from scripts/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestration.adapters.search.embedding_service import get_embedding_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_all_graphs() -> List[str]:
    """Get list of all consciousness graphs."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    try:
        graphs = r.execute_command("GRAPH.LIST")
        # Filter for citizen graphs
        citizen_graphs = [g for g in graphs if g.startswith('citizen_')]
        return citizen_graphs
    except Exception as e:
        logger.error(f"Failed to list graphs: {e}")
        return []


def generate_embeddable_text(node_type: str, props: Dict[str, Any]) -> str:
    """
    Generate embeddable text from node properties.

    Uses similar logic to EmbeddingService.create_node_embeddable_text
    but works from raw FalkorDB properties instead of formation fields.
    """

    # Fallback: description field if it exists
    description = props.get('description', '')

    # Try type-specific semantic fields
    if node_type == 'Realization':
        what = props.get('what_i_realized', '')
        context = props.get('context_when_discovered', '')
        if what:
            return f"{what}. Context: {context}" if context else what

    elif node_type == 'Principle':
        statement = props.get('principle_statement', '')
        why = props.get('why_it_matters', '')
        if statement:
            return f"{statement}. Why: {why}" if why else statement

    elif node_type == 'Mechanism':
        how = props.get('how_it_works', '')
        inputs = props.get('inputs', '')
        outputs = props.get('outputs', '')
        if how:
            return f"{how}. Inputs: {inputs}. Outputs: {outputs}"

    elif node_type == 'Concept':
        definition = props.get('definition', '')
        if definition:
            return definition

    elif node_type == 'Personal_Pattern':
        behavior = props.get('behavior_description', '')
        if behavior:
            return behavior

    elif node_type == 'Personal_Goal':
        goal = props.get('goal_description', '')
        why = props.get('why_it_matters', '')
        if goal:
            return f"{goal}. Why: {why}" if why else goal

    elif node_type == 'Best_Practice':
        desc = props.get('description', '')
        how_to = props.get('how_to_apply', '')
        if desc:
            return f"{desc}. How: {how_to}" if how_to else desc

    elif node_type == 'Anti_Pattern':
        desc = props.get('description', '')
        if desc:
            return desc

    elif node_type == 'Decision':
        rationale = props.get('rationale', '')
        if rationale:
            return rationale

    # Fallback to description or name
    if description:
        return description

    return props.get('name', 'Unknown')


def backfill_graph_embeddings(graph_name: str, embedding_service) -> Dict[str, int]:
    """
    Backfill embeddings for all nodes in a graph.

    Returns:
        Stats dict with counts
    """
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    stats = {
        'nodes_total': 0,
        'nodes_embedded': 0,
        'nodes_skipped': 0,
        'errors': 0
    }

    logger.info(f"[{graph_name}] Fetching all nodes...")

    # Query all nodes with common properties
    # Query specific fields instead of using properties() which returns complex format
    query = """
    MATCH (n)
    WHERE n.name IS NOT NULL
    RETURN
        n.name as name,
        labels(n) as labels,
        n.description as description,
        n.what_i_realized as what_i_realized,
        n.context_when_discovered as context_when_discovered,
        n.principle_statement as principle_statement,
        n.why_it_matters as why_it_matters,
        n.how_it_works as how_it_works,
        n.inputs as inputs,
        n.outputs as outputs,
        n.definition as definition,
        n.behavior_description as behavior_description,
        n.goal_description as goal_description,
        n.how_to_apply as how_to_apply,
        n.rationale as rationale
    """

    try:
        result = r.execute_command('GRAPH.QUERY', graph_name, query)
    except Exception as e:
        logger.error(f"[{graph_name}] Query failed: {e}")
        return stats

    if len(result) < 2:
        logger.warning(f"[{graph_name}] No nodes found")
        return stats

    # Column names from query
    columns = ['name', 'labels', 'description', 'what_i_realized', 'context_when_discovered',
               'principle_statement', 'why_it_matters', 'how_it_works', 'inputs', 'outputs',
               'definition', 'behavior_description', 'goal_description', 'how_to_apply', 'rationale']

    # Parse results
    nodes = []
    for row in result[1]:
        # Build props dict from row
        props = {}
        for idx, col in enumerate(columns):
            if idx < len(row):
                val = row[idx]
                if val is not None:
                    if isinstance(val, bytes):
                        val = val.decode('utf-8')
                    # Handle labels special case
                    if col == 'labels' and isinstance(val, list):
                        props[col] = [l.decode() if isinstance(l, bytes) else l for l in val]
                    else:
                        props[col] = val

        name = props.get('name', 'unknown')
        labels = props.get('labels', [])
        node_type = labels[0] if labels else 'Unknown'

        nodes.append({
            'name': name,
            'type': node_type,
            'props': props
        })

    stats['nodes_total'] = len(nodes)
    logger.info(f"[{graph_name}] Processing {len(nodes)} nodes...")

    # Process each node
    for idx, node in enumerate(nodes, 1):
        try:
            # Generate embeddable text
            embeddable_text = generate_embeddable_text(node['type'], node['props'])

            if not embeddable_text or len(embeddable_text.strip()) == 0:
                logger.warning(f"[{graph_name}] {node['name']}: No embeddable text, skipping")
                stats['nodes_skipped'] += 1
                continue

            # Generate embedding
            embedding = embedding_service.embed(embeddable_text)

            # Format as FalkorDB vector
            embedding_str = str(embedding)

            # Escape single quotes in embeddable_text
            embeddable_text_escaped = embeddable_text.replace("'", "\\'").replace('"', '\\"')

            # Update node with embeddable_text and content_embedding
            update_query = f"""
            MATCH (n {{name: '{node['name']}'}})
            SET
                n.embeddable_text = '{embeddable_text_escaped}',
                n.content_embedding = vecf32({embedding_str})
            RETURN n.name
            """

            r.execute_command('GRAPH.QUERY', graph_name, update_query)

            stats['nodes_embedded'] += 1

            if idx % 10 == 0:
                logger.info(f"[{graph_name}] Progress: {idx}/{len(nodes)} nodes embedded")

        except Exception as e:
            logger.error(f"[{graph_name}] Failed to embed {node['name']}: {e}")
            stats['errors'] += 1

    logger.info(f"[{graph_name}] Complete: {stats['nodes_embedded']}/{stats['nodes_total']} nodes embedded")

    return stats


def create_vector_indices(graph_name: str) -> bool:
    """
    Create vector indices for fast similarity search.

    Creates indices on content_embedding for all common node types.
    """
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Common node types to index
    node_types = [
        'Realization', 'Principle', 'Mechanism', 'Concept',
        'Personal_Pattern', 'Personal_Goal', 'Best_Practice', 'Anti_Pattern',
        'Decision', 'Memory', 'Coping_Mechanism', 'Trigger'
    ]

    logger.info(f"[{graph_name}] Creating vector indices...")

    for node_type in node_types:
        try:
            # Create vector index: db.idx.vector.createNodeIndex
            # Signature: (label, attribute, dimensions, similarity_function)
            index_query = f"""
            CALL db.idx.vector.createNodeIndex(
                '{node_type}',
                'content_embedding',
                768,
                'cosine'
            )
            """

            r.execute_command('GRAPH.QUERY', graph_name, index_query)
            logger.info(f"[{graph_name}] ✅ Created vector index for {node_type}")

        except Exception as e:
            # Index might already exist, that's ok
            if 'already exists' in str(e).lower():
                logger.debug(f"[{graph_name}] Vector index for {node_type} already exists")
            else:
                logger.warning(f"[{graph_name}] Failed to create index for {node_type}: {e}")

    return True


def main():
    """Backfill embeddings for all graphs."""
    logger.info("=" * 80)
    logger.info("EMBEDDING BACKFILL - Starting")
    logger.info("=" * 80)

    # Initialize embedding service
    logger.info("Initializing embedding service...")
    embedding_service = get_embedding_service()
    logger.info("✅ Embedding service ready")

    # Get all graphs
    graphs = get_all_graphs()
    logger.info(f"Found {len(graphs)} citizen graphs: {graphs}")

    if not graphs:
        logger.error("No graphs found!")
        return

    # Process each graph
    total_stats = {
        'graphs_processed': 0,
        'total_nodes': 0,
        'total_embedded': 0,
        'total_errors': 0
    }

    for graph_name in graphs:
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"Processing {graph_name}")
        logger.info("=" * 80)

        # Backfill embeddings
        stats = backfill_graph_embeddings(graph_name, embedding_service)

        # Create vector indices
        create_vector_indices(graph_name)

        # Update totals
        total_stats['graphs_processed'] += 1
        total_stats['total_nodes'] += stats['nodes_total']
        total_stats['total_embedded'] += stats['nodes_embedded']
        total_stats['total_errors'] += stats['errors']

    # Final summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("EMBEDDING BACKFILL - Complete")
    logger.info("=" * 80)
    logger.info(f"Graphs processed: {total_stats['graphs_processed']}")
    logger.info(f"Total nodes: {total_stats['total_nodes']}")
    logger.info(f"Nodes embedded: {total_stats['total_embedded']}")
    logger.info(f"Errors: {total_stats['total_errors']}")
    logger.info("")
    logger.info("✅ All graphs now have embeddings and vector indices!")
    logger.info("Stimulus injection vector search is now operational.")


if __name__ == "__main__":
    main()
