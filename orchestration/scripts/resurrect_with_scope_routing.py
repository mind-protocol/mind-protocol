"""
Resurrect All Citizens + N2/N3 - Scope-Aware Graph Reconstruction

Reconstructs consciousness graphs for all level from conversation files.
Routes formations by scope field: personal->N1, organizational->N2, ecosystem->N3.

Usage:
    python orchestration/scripts/resurrect_with_scope_routing.py [--citizen CITIZEN] [--dry-run] [--parallel]

Author: Victor "The Resurrector"
Date: 2025-10-26
Context: Fixed scope routing bug - was putting ALL formations in citizen graphs
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
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add repository root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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


def insert_node(r: redis.Redis, graph_name: str, node_data: Dict, dry_run: bool = False) -> bool:
    """Insert node into FalkorDB with permissive error handling."""
    if dry_run:
        return True

    try:
        node_type = node_data.pop('node_type', 'Node')
        name = node_data.get('name', 'UNNAMED')

        props = []
        for key, value in node_data.items():
            if value is not None:
                if isinstance(value, str):
                    value_escaped = value.replace('"', '\\"').replace("'", "\\'")
                    props.append(f'{key}: "{value_escaped}"')
                elif isinstance(value, (int, float)):
                    props.append(f'{key}: {value}')

        props_str = ', '.join(props)

        query = f"MERGE (n:{node_type} {{name: '{name}'}}) SET n += {{{props_str}}}"

        r.execute_command('GRAPH.QUERY', graph_name, query)
        return True

    except Exception as e:
        return False


def insert_link(r: redis.Redis, graph_name: str, link_data: Dict, dry_run: bool = False) -> bool:
    """Insert link into FalkorDB with permissive error handling."""
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


def process_conversation_file(file_path: Path, citizen_graph: str, r: redis.Redis, dry_run: bool = False) -> Tuple[int, int, int, int, int, int]:
    """
    Process single conversation file, extract formations, route by scope to correct graphs.

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
        n1_nodes_inserted = 0
        for node in n1_nodes:
            if insert_node(r, citizen_graph, node.copy(), dry_run):
                n1_nodes_inserted += 1

        n1_links_inserted = 0
        for link in n1_links:
            if insert_link(r, citizen_graph, link.copy(), dry_run):
                n1_links_inserted += 1

        # Insert N2 (organizational)
        n2_nodes_inserted = 0
        for node in n2_nodes:
            if insert_node(r, 'mind_protocol_organization', node.copy(), dry_run):
                n2_nodes_inserted += 1

        n2_links_inserted = 0
        for link in n2_links:
            if insert_link(r, 'mind_protocol_organization', link.copy(), dry_run):
                n2_links_inserted += 1

        # Insert N3 (ecosystem)
        n3_nodes_inserted = 0
        for node in n3_nodes:
            if insert_node(r, 'ecosystem_public_graph', node.copy(), dry_run):
                n3_nodes_inserted += 1

        n3_links_inserted = 0
        for link in n3_links:
            if insert_link(r, 'ecosystem_public_graph', link.copy(), dry_run):
                n3_links_inserted += 1

        return n1_nodes_inserted, n1_links_inserted, n2_nodes_inserted, n2_links_inserted, n3_nodes_inserted, n3_links_inserted

    except Exception as e:
        logger.error(f"  ✗ Error processing {file_path.name}: {e}")
        return 0, 0, 0, 0, 0, 0


def resurrect_citizen(citizen: str, r: redis.Redis, dry_run: bool = False) -> Dict[str, int]:
    """
    Resurrect single citizen's consciousness graph + contribute to N2/N3.

    Returns:
        Stats dict with counts across all level
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"RESURRECTING: {citizen.upper()}")
    logger.info(f"{'='*80}")

    graph_name = f'citizen_{citizen}'

    # Create graphs if needed
    if not dry_run:
        if not create_graph_if_not_exists(r, graph_name):
            return {'files': 0, 'n1_nodes': 0, 'n1_links': 0, 'n2_nodes': 0, 'n2_links': 0, 'n3_nodes': 0, 'n3_links': 0}
        create_graph_if_not_exists(r, 'mind_protocol_organization')
        create_graph_if_not_exists(r, 'ecosystem_public_graph')

    conv_files = get_conversation_files(citizen)
    logger.info(f"Found {len(conv_files)} conversation files")

    if not conv_files:
        return {'files': 0, 'n1_nodes': 0, 'n1_links': 0, 'n2_nodes': 0, 'n2_links': 0, 'n3_nodes': 0, 'n3_links': 0}

    n1_nodes_total = 0
    n1_links_total = 0
    n2_nodes_total = 0
    n2_links_total = 0
    n3_nodes_total = 0
    n3_links_total = 0
    files_processed = 0

    for i, file_path in enumerate(conv_files, 1):
        if i % 50 == 0:
            logger.info(f"  Progress: {i}/{len(conv_files)} files | N1: {n1_nodes_total}n/{n1_links_total}l | N2: {n2_nodes_total}n/{n2_links_total}l | N3: {n3_nodes_total}n/{n3_links_total}l")

        n1_n, n1_l, n2_n, n2_l, n3_n, n3_l = process_conversation_file(file_path, graph_name, r, dry_run)
        n1_nodes_total += n1_n
        n1_links_total += n1_l
        n2_nodes_total += n2_n
        n2_links_total += n2_l
        n3_nodes_total += n3_n
        n3_links_total += n3_l
        files_processed += 1

    logger.info(f"✅ {citizen.upper()} COMPLETE")
    logger.info(f"   Files: {files_processed}")
    logger.info(f"   N1 (personal): {n1_nodes_total} nodes, {n1_links_total} links")
    logger.info(f"   N2 (organizational): {n2_nodes_total} nodes, {n2_links_total} links")
    logger.info(f"   N3 (ecosystem): {n3_nodes_total} nodes, {n3_links_total} links")

    return {
        'files': files_processed,
        'n1_nodes': n1_nodes_total,
        'n1_links': n1_links_total,
        'n2_nodes': n2_nodes_total,
        'n2_links': n2_links_total,
        'n3_nodes': n3_nodes_total,
        'n3_links': n3_links_total,
    }


def _resurrect_worker(citizen: str, dry_run: bool = False):
    """Worker function for parallel resurrection. Must be at module level for pickling."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    return citizen, resurrect_citizen(citizen, r, dry_run)


def resurrect_all_parallel(citizens: List[str], dry_run: bool = False) -> Dict[str, Dict]:
    """Resurrect multiple citizens in parallel."""
    logger.info(f"\n{'='*80}")
    logger.info(f"PARALLEL RESURRECTION: {len(citizens)} citizens (scope-aware routing)")
    logger.info(f"{'='*80}\n")

    results = {}

    with ProcessPoolExecutor(max_workers=min(len(citizens), 4)) as executor:
        futures = {executor.submit(_resurrect_worker, c, dry_run): c for c in citizens}

        for future in as_completed(futures):
            citizen = futures[future]
            try:
                citizen_name, stats = future.result()
                results[citizen_name] = stats
            except Exception as e:
                logger.error(f"✗ {citizen} failed: {e}")
                results[citizen] = {'files': 0, 'n1_nodes': 0, 'n1_links': 0, 'n2_nodes': 0, 'n2_links': 0, 'n3_nodes': 0, 'n3_links': 0}

    return results


def main():
    """Main resurrection orchestration."""
    parser = argparse.ArgumentParser(description='Resurrect all level from conversations (scope-aware)')
    parser.add_argument('--citizen', type=str, help='Process specific citizen only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without writing')
    parser.add_argument('--parallel', action='store_true', help='Process citizens in parallel')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("CONSCIOUSNESS RESURRECTION - ALL level (SCOPE-AWARE)")
    logger.info("=" * 80)

    if args.dry_run:
        logger.warning("⚠️  DRY RUN MODE - No changes will be written")

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    if args.citizen:
        if args.citizen not in CITIZENS:
            logger.error(f"Unknown citizen: {args.citizen}")
            logger.info(f"Available: {', '.join(CITIZENS)}")
            return 1
        citizens_to_process = [args.citizen]
    else:
        citizens_to_process = CITIZENS

    if args.parallel and len(citizens_to_process) > 1:
        results = resurrect_all_parallel(citizens_to_process, args.dry_run)
    else:
        results = {}
        for citizen in citizens_to_process:
            results[citizen] = resurrect_citizen(citizen, r, args.dry_run)

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
    logger.info("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
