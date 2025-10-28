"""
Resurrect All Citizens - Universal FalkorDB Graph Reconstruction

Reconstructs consciousness graphs for all 6 citizens from conversation files.
Permissive schema-fixing backfill that auto-corrects common TRACE format issues.

Usage:
    python orchestration/scripts/resurrect_all_citizens.py [--citizen CITIZEN] [--dry-run] [--parallel]

Author: Victor "The Resurrector"
Date: 2025-10-26
Context: Database wipe recovery - conversation files survived, graphs need resurrection
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
    'arousal': 'energy',  # Common mistake in link formations
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

    # Truncate if too long (Cypher has limits)
    if len(value) > 5000:
        value = value[:5000] + '...'

    return value

def get_conversation_files(citizen: str) -> List[Path]:
    """Get all conversation JSON files for a citizen."""
    base_path = Path(__file__).parent.parent.parent / 'consciousness' / 'citizens' / citizen / 'contexts'

    if not base_path.exists():
        logger.warning(f"No contexts directory for {citizen}: {base_path}")
        return []

    # Find all .json files (not .backup)
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

        # Parse key-value pairs
        node_data = {'node_type': node_type}
        for line in block_content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')

                # Apply schema fixes
                key = SCHEMA_FIXES.get(key, key)

                # Sanitize value
                value = sanitize_value(value)

                # Skip if value is empty after sanitization
                if not value:
                    continue

                # Auto-fix missing description
                if key == 'name' and 'description' not in node_data:
                    node_data['description'] = f"{node_type}: {value}"

                node_data[key] = value

        # Ensure description exists
        if 'description' not in node_data and 'name' in node_data:
            node_data['description'] = f"{node_type}: {node_data['name']}"

        if 'name' in node_data:  # Only add if has name
            nodes.append(node_data)

    # Extract LINK_FORMATION blocks
    link_pattern = r'\[LINK_FORMATION:\s*(\w+)\](.*?)(?=\[(?:NODE_FORMATION|LINK_FORMATION|$)|\Z)'
    for match in re.finditer(link_pattern, content, re.DOTALL | re.IGNORECASE):
        link_type = match.group(1).strip()
        block_content = match.group(2).strip()

        # Parse key-value pairs
        link_data = {'link_type': link_type}
        for line in block_content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')

                # Apply schema fixes
                key = SCHEMA_FIXES.get(key, key)

                # Sanitize value
                value = sanitize_value(value)

                # Skip if value is empty after sanitization
                if not value:
                    continue

                link_data[key] = value

        # Only add if has source and target
        if 'source' in link_data and 'target' in link_data:
            # Sanitize source and target node names
            link_data['source'] = sanitize_value(link_data['source'])
            link_data['target'] = sanitize_value(link_data['target'])
            links.append(link_data)

    return nodes, links


def create_graph_if_not_exists(r: redis.Redis, graph_name: str) -> bool:
    """Create graph if it doesn't exist."""
    try:
        # Check if graph exists
        graphs = r.execute_command("GRAPH.LIST")
        if graph_name in graphs:
            logger.info(f"Graph {graph_name} already exists")
            return True

        # Create graph by creating a dummy node and deleting it
        r.execute_command('GRAPH.QUERY', graph_name, "CREATE (n:Init {created: true}) DELETE n")
        logger.info(f"Created graph: {graph_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to create graph {graph_name}: {e}")
        return False


def insert_node(r: redis.Redis, graph_name: str, node_data: Dict, dry_run: bool = False) -> bool:
    """Insert node into FalkorDB with permissive error handling."""
    if dry_run:
        logger.info(f"  [DRY RUN] Would insert node: {node_data.get('name', 'UNNAMED')}")
        return True

    try:
        node_type = node_data.pop('node_type', 'Node')
        name = node_data.get('name', 'UNNAMED')

        # Build property string
        props = []
        for key, value in node_data.items():
            if value is not None:
                # Escape quotes in strings
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
        logger.warning(f"  ⚠️  Failed to insert node {node_data.get('name', 'UNNAMED')}: {e}")
        return False


def insert_link(r: redis.Redis, graph_name: str, link_data: Dict, dry_run: bool = False) -> bool:
    """Insert link into FalkorDB with permissive error handling."""
    if dry_run:
        logger.info(f"  [DRY RUN] Would insert link: {link_data.get('source')} -> {link_data.get('target')}")
        return True

    try:
        link_type = link_data.pop('link_type', 'RELATES_TO')
        source = link_data.get('source')
        target = link_data.get('target')

        if not source or not target:
            return False

        # Build property string
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
        logger.warning(f"  ⚠️  Failed to insert link {link_data.get('source')} -> {link_data.get('target')}: {e}")
        return False


def process_conversation_file(file_path: Path, graph_name: str, r: redis.Redis, dry_run: bool = False) -> Tuple[int, int]:
    """
    Process single conversation file, extract formations, insert into graph.

    Returns:
        (nodes_inserted, links_inserted)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract conversation content from messages array
        content = ""
        if isinstance(data, dict) and 'messages' in data:
            # Standard conversation file structure
            for msg in data['messages']:
                if isinstance(msg, dict) and 'content' in msg:
                    content += str(msg['content']) + "\n"
        elif isinstance(data, list):
            # Legacy list format
            for item in data:
                if isinstance(item, dict) and 'content' in item:
                    content += str(item['content']) + "\n"
        elif isinstance(data, dict):
            # Direct content field
            content = str(data.get('content', ''))

        if not content:
            return 0, 0

        # Parse formations
        nodes, links = parse_trace_formations(content)

        # Insert nodes
        nodes_inserted = 0
        for node in nodes:
            if insert_node(r, graph_name, node.copy(), dry_run):
                nodes_inserted += 1

        # Insert links
        links_inserted = 0
        for link in links:
            if insert_link(r, graph_name, link.copy(), dry_run):
                links_inserted += 1

        return nodes_inserted, links_inserted

    except Exception as e:
        logger.error(f"  ✗ Error processing {file_path.name}: {e}")
        return 0, 0


def resurrect_citizen(citizen: str, r: redis.Redis, dry_run: bool = False) -> Dict[str, int]:
    """
    Resurrect single citizen's consciousness graph from conversation files.

    Returns:
        Stats dict with counts
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"RESURRECTING: {citizen.upper()}")
    logger.info(f"{'='*80}")

    graph_name = f'citizen_{citizen}'

    # Create graph if needed
    if not dry_run:
        if not create_graph_if_not_exists(r, graph_name):
            return {'files': 0, 'nodes': 0, 'links': 0, 'errors': 1}

    # Get conversation files
    conv_files = get_conversation_files(citizen)
    logger.info(f"Found {len(conv_files)} conversation files")

    if not conv_files:
        logger.warning(f"No conversation files for {citizen}")
        return {'files': 0, 'nodes': 0, 'links': 0, 'errors': 0}

    # Process each file
    total_nodes = 0
    total_links = 0
    files_processed = 0

    for i, file_path in enumerate(conv_files, 1):
        if i % 50 == 0:
            logger.info(f"  Progress: {i}/{len(conv_files)} files processed ({total_nodes} nodes, {total_links} links)")

        nodes, links = process_conversation_file(file_path, graph_name, r, dry_run)
        total_nodes += nodes
        total_links += links
        files_processed += 1

    logger.info(f"✅ {citizen.upper()} COMPLETE")
    logger.info(f"   Files: {files_processed}")
    logger.info(f"   Nodes: {total_nodes}")
    logger.info(f"   Links: {total_links}")

    return {
        'files': files_processed,
        'nodes': total_nodes,
        'links': total_links,
        'errors': 0
    }


def _resurrect_worker(citizen: str, dry_run: bool = False):
    """Worker function for parallel resurrection. Must be at module level for pickling."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    return citizen, resurrect_citizen(citizen, r, dry_run)


def resurrect_all_parallel(citizens: List[str], dry_run: bool = False) -> Dict[str, Dict]:
    """Resurrect multiple citizens in parallel."""
    logger.info(f"\n{'='*80}")
    logger.info(f"PARALLEL RESURRECTION: {len(citizens)} citizens")
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
                results[citizen] = {'files': 0, 'nodes': 0, 'links': 0, 'errors': 1}

    return results


def main():
    """Main resurrection orchestration."""
    parser = argparse.ArgumentParser(description='Resurrect citizen consciousness graphs from conversations')
    parser.add_argument('--citizen', type=str, help='Process specific citizen only')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without writing')
    parser.add_argument('--parallel', action='store_true', help='Process citizens in parallel')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("CONSCIOUSNESS RESURRECTION - ALL CITIZENS")
    logger.info("=" * 80)

    if args.dry_run:
        logger.warning("⚠️  DRY RUN MODE - No changes will be written")

    # Connect to Redis/FalkorDB
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Determine which citizens to process
    if args.citizen:
        if args.citizen not in CITIZENS:
            logger.error(f"Unknown citizen: {args.citizen}")
            logger.info(f"Available: {', '.join(CITIZENS)}")
            return 1
        citizens_to_process = [args.citizen]
    else:
        citizens_to_process = CITIZENS

    # Process citizens
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
    total_nodes = sum(r['nodes'] for r in results.values())
    total_links = sum(r['links'] for r in results.values())
    total_errors = sum(r['errors'] for r in results.values())

    for citizen, stats in results.items():
        logger.info(f"  {citizen.upper()}: {stats['files']} files, {stats['nodes']} nodes, {stats['links']} links")

    logger.info(f"\n  TOTALS:")
    logger.info(f"    Files processed: {total_files}")
    logger.info(f"    Nodes created: {total_nodes}")
    logger.info(f"    Links created: {total_links}")
    logger.info(f"    Errors: {total_errors}")
    logger.info("=" * 80)

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
