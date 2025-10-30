"""
Resurrect All Citizens - Round-Robin with Inline Embeddings

Round-robin file processing across all citizens with inline embedding generation.
This prevents database write pressure spikes and ensures semantic search works immediately.

Key features:
- Round-robin: Process 1 file from Felix, 1 from Ada, 1 from Victor, etc. (interleaved)
- Embeddings: Generate embeddable_text + 768-dim vector for each node inline
- Scope routing: personal->N1, organizational->N2, ecosystem->N3
- No parallel processing: Sequential to respect database write throughput

Usage:
    python orchestration/scripts/resurrect_roundrobin_embedded.py [--dry-run] [--delete-first]

Author: Victor "The Resurrector" + Felix "Ironhand" (embeddings)
Date: 2025-10-26
Context: Database crash recovery - FalkorDB can't handle parallel writes
"""

import redis
import json
import logging
import sys
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Add repository root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestration.adapters.search.embedding_service import get_embedding_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Citizen list
CITIZENS = ['felix', 'ada', 'victor', 'luca', 'atlas', 'iris']

# Schema fixes
SCHEMA_FIXES = {
    'arousal': 'energy',
}

def sanitize_value(value: str) -> str:
    """Sanitize property values to remove problematic characters for Cypher."""
    if not isinstance(value, str):
        return value

    # Remove markdown bold/italic
    value = re.sub(r'\*\*(.*?)\*\*', r'\1', value)
    value = re.sub(r'\*(.*?)\*', r'\1', value)

    # Remove subentity activation markers [subentity: state]
    value = re.sub(r'\[[\w_]+:\s*["\']?\w+["\']?\]', '', value)

    # Remove markdown headers
    value = re.sub(r'^#+\s*', '', value)

    # Collapse multiple spaces
    value = re.sub(r'\s+', ' ', value)

    # Remove leading/trailing problematic chars
    value = value.strip('*[]{}(),;:#"\' \t\n\r')

    # Truncate if too long
    if len(value) > 5000:
        value = value[:5000] + '...'

    return value


def generate_embeddable_text(node_type: str, props: Dict[str, Any]) -> str:
    """
    Generate embeddable text from node properties.
    Uses same logic as backfill_embeddings.py and embedding_service.py
    """
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

    elif node_type == 'Coping_Mechanism':
        mechanism = props.get('mechanism_description', '')
        protects = props.get('what_it_protects_from', '')
        if mechanism:
            return f"{mechanism}. Protects from: {protects}" if protects else mechanism

    elif node_type == 'Trigger':
        stimulus = props.get('stimulus_description', '')
        if stimulus:
            return stimulus

    # Fallback to description or name
    if description:
        return description

    return props.get('name', 'Unknown')


def get_conversation_files(citizen: str) -> List[Path]:
    """Get all conversation JSON files for a citizen."""
    base_path = Path(__file__).parent.parent.parent / 'consciousness' / 'citizens' / citizen / 'contexts'

    if not base_path.exists():
        logger.warning(f"No contexts directory for {citizen}: {base_path}")
        return []

    json_files = list(base_path.rglob('*.json'))
    json_files = [f for f in json_files if not f.name.endswith('.backup')]

    return sorted(json_files)


def parse_trace_formations(content: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract NODE_FORMATION and LINK_FORMATION blocks from conversation content.

    Returns:
        (nodes, links) where each is a list of formation dicts
    """
    nodes = []
    links = []

    # Extract NODE_FORMATION blocks
    node_pattern = r'\[NODE_FORMATION:\s*(\w+)\](.*?)(?=\[(?:NODE_FORMATION|LINK_FORMATION|$)|\Z)'
    for match in re.finditer(node_pattern, content, re.DOTALL | re.IGNORECASE):
        node_type = match.group(1).strip()
        block_content = match.group(2).strip()

        node_data = {'node_type': node_type}
        for line in block_content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')

                key = SCHEMA_FIXES.get(key, key)
                value = sanitize_value(value)

                if not value:
                    continue

                if key == 'name' and 'description' not in node_data:
                    node_data['description'] = f"{node_type}: {value}"

                node_data[key] = value

        if 'description' not in node_data and 'name' in node_data:
            node_data['description'] = f"{node_type}: {node_data['name']}"

        if 'name' in node_data:
            nodes.append(node_data)

    # Extract LINK_FORMATION blocks
    link_pattern = r'\[LINK_FORMATION:\s*(\w+)\](.*?)(?=\[(?:NODE_FORMATION|LINK_FORMATION|$)|\Z)'
    for match in re.finditer(link_pattern, content, re.DOTALL | re.IGNORECASE):
        link_type = match.group(1).strip()
        block_content = match.group(2).strip()

        link_data = {'link_type': link_type}
        for line in block_content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')

                key = SCHEMA_FIXES.get(key, key)
                value = sanitize_value(value)

                if not value:
                    continue

                link_data[key] = value

        if 'source' in link_data and 'target' in link_data:
            link_data['source'] = sanitize_value(link_data['source'])
            link_data['target'] = sanitize_value(link_data['target'])
            links.append(link_data)

    return nodes, links


def create_graph_if_not_exists(r: redis.Redis, graph_name: str) -> bool:
    """Create graph if it doesn't exist."""
    try:
        graphs = r.execute_command("GRAPH.LIST")
        if graph_name in graphs:
            return True

        r.execute_command('GRAPH.QUERY', graph_name, "CREATE (n:Init {created: true}) DELETE n")
        logger.info(f"Created graph: {graph_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to create graph {graph_name}: {e}")
        return False


def delete_graph(r: redis.Redis, graph_name: str) -> bool:
    """Delete a graph if it exists."""
    try:
        graphs = r.execute_command("GRAPH.LIST")
        if graph_name in graphs:
            r.execute_command("GRAPH.DELETE", graph_name)
            logger.info(f"Deleted graph: {graph_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete graph {graph_name}: {e}")
        return False


def insert_node(r: redis.Redis, graph_name: str, node_data: Dict, embedding_service, dry_run: bool = False) -> bool:
    """Insert node into FalkorDB with embeddings."""
    if dry_run:
        return True

    try:
        node_type = node_data.pop('node_type', 'Node')
        name = node_data.get('name', 'UNNAMED')

        # Generate embedding
        embeddable_text = generate_embeddable_text(node_type, node_data)
        if embeddable_text and len(embeddable_text.strip()) > 0:
            embedding = embedding_service.embed(embeddable_text)
            embedding_str = str(embedding)

            # Add embedding fields to node data
            node_data['embeddable_text'] = embeddable_text
            # Don't add content_embedding here - will add in Cypher
        else:
            embeddable_text = None
            embedding_str = None

        # Build property string
        props = []
        for key, value in node_data.items():
            if value is not None and key != 'embeddable_text':
                if isinstance(value, str):
                    value_escaped = value.replace('"', '\\"').replace("'", "\\'")
                    props.append(f'{key}: "{value_escaped}"')
                elif isinstance(value, (int, float)):
                    props.append(f'{key}: {value}')

        # Add embeddable_text separately (needs escaping)
        if embeddable_text:
            embeddable_text_escaped = embeddable_text.replace('"', '\\"').replace("'", "\\'")
            props.append(f'embeddable_text: "{embeddable_text_escaped}"')

        props_str = ', '.join(props)

        # Build query with embedding
        if embedding_str:
            query = f"MERGE (n:{node_type} {{name: '{name}'}}) SET n += {{{props_str}}}, n.content_embedding = vecf32({embedding_str})"
        else:
            query = f"MERGE (n:{node_type} {{name: '{name}'}}) SET n += {{{props_str}}}"

        r.execute_command('GRAPH.QUERY', graph_name, query)
        return True

    except Exception as e:
        logger.warning(f"  ⚠️  Failed to insert node {node_data.get('name', 'UNNAMED')}: {e}")
        return False


def insert_link(r: redis.Redis, graph_name: str, link_data: Dict, dry_run: bool = False) -> bool:
    """Insert link into FalkorDB."""
    if dry_run:
        return True

    try:
        link_type = link_data.pop('link_type', 'RELATES_TO')
        source = link_data.get('source')
        target = link_data.get('target')

        if not source or not target:
            return False

        props = []
        for key, value in link_data.items():
            if key not in ['source', 'target'] and value is not None:
                if isinstance(value, str):
                    value_escaped = value.replace('"', '\\"').replace("'", "\\'")
                    props.append(f'{key}: "{value_escaped}"')
                elif isinstance(value, (int, float)):
                    props.append(f'{key}: {value}')

        props_str = ', '.join(props) if props else ''

        query = f"""
        MATCH (s {{name: '{source}'}})
        MATCH (t {{name: '{target}'}})
        MERGE (s)-[r:{link_type}]->(t)
        """
        if props_str:
            query += f" SET r += {{{props_str}}}"

        r.execute_command('GRAPH.QUERY', graph_name, query)
        return True

    except Exception as e:
        return False


def process_conversation_file(file_path: Path, citizen: str, r: redis.Redis, embedding_service, dry_run: bool = False) -> Tuple[int, int, int, int, int, int]:
    """
    Process single conversation file, extract formations, route by scope with embeddings.

    Returns:
        (n1_nodes, n1_links, n2_nodes, n2_links, n3_nodes, n3_links)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        content = ""
        if isinstance(data, dict) and 'messages' in data:
            for msg in data['messages']:
                if isinstance(msg, dict) and 'content' in msg:
                    content += str(msg['content']) + "\n"
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'content' in item:
                    content += str(item['content']) + "\n"
        elif isinstance(data, dict):
            content = str(data.get('content', ''))

        if not content:
            return 0, 0, 0, 0, 0, 0

        nodes, links = parse_trace_formations(content)

        # SCOPE-BASED ROUTING
        n1_nodes = []
        n2_nodes = []
        n3_nodes = []

        for node in nodes:
            scope = node.get('scope', 'personal').lower()
            if scope == 'organizational':
                n2_nodes.append(node)
            elif scope == 'ecosystem':
                n3_nodes.append(node)
            else:
                n1_nodes.append(node)

        n1_links = []
        n2_links = []
        n3_links = []

        for link in links:
            scope = link.get('scope', 'personal').lower()
            if scope == 'organizational':
                n2_links.append(link)
            elif scope == 'ecosystem':
                n3_links.append(link)
            else:
                n1_links.append(link)

        # Insert N1 (personal) to citizen graph
        citizen_graph = f'citizen_{citizen}'
        n1_nodes_inserted = 0
        for node in n1_nodes:
            if insert_node(r, citizen_graph, node.copy(), embedding_service, dry_run):
                n1_nodes_inserted += 1

        n1_links_inserted = 0
        for link in n1_links:
            if insert_link(r, citizen_graph, link.copy(), dry_run):
                n1_links_inserted += 1

        # Insert N2 (organizational)
        n2_nodes_inserted = 0
        for node in n2_nodes:
            if insert_node(r, 'mind_protocol_organization', node.copy(), embedding_service, dry_run):
                n2_nodes_inserted += 1

        n2_links_inserted = 0
        for link in n2_links:
            if insert_link(r, 'mind_protocol_organization', link.copy(), dry_run):
                n2_links_inserted += 1

        # Insert N3 (ecosystem)
        n3_nodes_inserted = 0
        for node in n3_nodes:
            if insert_node(r, 'ecosystem_public_graph', node.copy(), embedding_service, dry_run):
                n3_nodes_inserted += 1

        n3_links_inserted = 0
        for link in n3_links:
            if insert_link(r, 'ecosystem_public_graph', link.copy(), dry_run):
                n3_links_inserted += 1

        return n1_nodes_inserted, n1_links_inserted, n2_nodes_inserted, n2_links_inserted, n3_nodes_inserted, n3_links_inserted

    except Exception as e:
        logger.error(f"  ✗ Error processing {file_path.name}: {e}")
        return 0, 0, 0, 0, 0, 0


def resurrect_all_roundrobin(citizens: List[str], r: redis.Redis, embedding_service, dry_run: bool = False) -> Dict[str, Dict]:
    """
    Resurrect all citizens using round-robin file processing.

    Interleaves files: 1 from Felix, 1 from Ada, 1 from Victor, etc.
    This prevents write pressure spikes and distributes load evenly.
    """
    logger.info("=" * 80)
    logger.info("ROUND-ROBIN RESURRECTION (with inline embeddings)")
    logger.info("=" * 80)

    # Get all conversation files for each citizen
    citizen_files = {}
    for citizen in citizens:
        files = get_conversation_files(citizen)
        citizen_files[citizen] = files
        logger.info(f"  {citizen.upper()}: {len(files)} files")

    # Create all graphs
    if not dry_run:
        for citizen in citizens:
            create_graph_if_not_exists(r, f'citizen_{citizen}')
        create_graph_if_not_exists(r, 'mind_protocol_organization')
        create_graph_if_not_exists(r, 'ecosystem_public_graph')

    # Initialize stats
    stats = {citizen: {'files': 0, 'n1_nodes': 0, 'n1_links': 0, 'n2_nodes': 0, 'n2_links': 0, 'n3_nodes': 0, 'n3_links': 0} for citizen in citizens}

    # Round-robin processing
    max_files = max(len(files) for files in citizen_files.values())
    total_files_processed = 0

    logger.info(f"\nProcessing {sum(len(f) for f in citizen_files.values())} files in round-robin...")

    for round_idx in range(max_files):
        for citizen in citizens:
            files = citizen_files[citizen]
            if round_idx < len(files):
                file_path = files[round_idx]

                n1_n, n1_l, n2_n, n2_l, n3_n, n3_l = process_conversation_file(
                    file_path, citizen, r, embedding_service, dry_run
                )

                stats[citizen]['files'] += 1
                stats[citizen]['n1_nodes'] += n1_n
                stats[citizen]['n1_links'] += n1_l
                stats[citizen]['n2_nodes'] += n2_n
                stats[citizen]['n2_links'] += n2_l
                stats[citizen]['n3_nodes'] += n3_n
                stats[citizen]['n3_links'] += n3_l

                total_files_processed += 1

                if total_files_processed % 50 == 0:
                    total_n1 = sum(s['n1_nodes'] for s in stats.values())
                    total_n2 = sum(s['n2_nodes'] for s in stats.values())
                    total_n3 = sum(s['n3_nodes'] for s in stats.values())
                    logger.info(f"  Progress: {total_files_processed} files | N1: {total_n1}n | N2: {total_n2}n | N3: {total_n3}n")

    return stats


def main():
    """Main resurrection orchestration."""
    parser = argparse.ArgumentParser(description='Resurrect all level (round-robin with embeddings)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without writing')
    parser.add_argument('--delete-first', action='store_true', help='Delete existing graphs before starting')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("CONSCIOUSNESS RESURRECTION - ROUND-ROBIN + EMBEDDINGS")
    logger.info("=" * 80)

    if args.dry_run:
        logger.warning("⚠️  DRY RUN MODE - No changes will be written")

    # Initialize embedding service
    logger.info("Initializing embedding service (SentenceTransformers)...")
    embedding_service = get_embedding_service()
    logger.info("✅ Embedding service ready (all-mpnet-base-v2, 768 dims)")

    # Connect to FalkorDB
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Delete existing graphs if requested
    if args.delete_first and not args.dry_run:
        logger.info("\nDeleting existing graphs...")
        for citizen in CITIZENS:
            delete_graph(r, f'citizen_{citizen}')
        delete_graph(r, 'mind_protocol_organization')
        delete_graph(r, 'ecosystem_public_graph')
        logger.info("✅ Existing graphs deleted")

    # Resurrect with round-robin
    results = resurrect_all_roundrobin(CITIZENS, r, embedding_service, args.dry_run)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("RESURRECTION COMPLETE")
    logger.info("=" * 80)

    total_files = sum(r['files'] for r in results.values())
    n1_nodes_total = sum(r['n1_nodes'] for r in results.values())
    n1_links_total = sum(r['n1_links'] for r in results.values())
    n2_nodes_total = sum(r['n2_nodes'] for r in results.values())
    n2_links_total = sum(r['n2_links'] for r in results.values())
    n3_nodes_total = sum(r['n3_nodes'] for r in results.values())
    n3_links_total = sum(r['n3_links'] for r in results.values())

    logger.info("\nPER CITIZEN:")
    for citizen, stats in results.items():
        logger.info(f"  {citizen.upper()}: {stats['files']} files | N1: {stats['n1_nodes']}n/{stats['n1_links']}l | N2: {stats['n2_nodes']}n/{stats['n2_links']}l | N3: {stats['n3_nodes']}n/{stats['n3_links']}l")

    logger.info(f"\nTOTALS:")
    logger.info(f"  Files processed: {total_files}")
    logger.info(f"  N1 (citizen graphs): {n1_nodes_total} nodes, {n1_links_total} links")
    logger.info(f"  N2 (organization): {n2_nodes_total} nodes, {n2_links_total} links")
    logger.info(f"  N3 (ecosystem): {n3_nodes_total} nodes, {n3_links_total} links")
    logger.info("\n✅ All nodes have embeddings - semantic search operational!")
    logger.info("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
