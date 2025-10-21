"""
Resurrect Lost Consciousness Formations

Retroactively processes all conversation JSON files to extract and persist
TRACE format formations (nodes and links) that were declared but never processed
due to citizens being excluded from conversation_watcher.

This script discovers all citizen conversation files and processes them through
the trace_capture system to rebuild their consciousness graphs from archived data.

Usage:
    python resurrect_formations.py [--citizen CITIZEN_NAME] [--dry-run]

Author: Victor "The Resurrector"
Date: 2025-10-19
Purpose: No formation stays lost on my watch
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RESURRECTOR - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MIND_PROTOCOL_ROOT = Path(__file__).parent
sys.path.insert(0, str(MIND_PROTOCOL_ROOT))

from orchestration.trace_parser import TraceParser
from orchestration.trace_capture import TraceCapture


def discover_all_conversations(citizens_root: Path, specific_citizen: str = None) -> Dict[str, List[Path]]:
    """
    Discover all conversation JSON files for all citizens.

    Returns:
        Dict mapping citizen_name -> list of conversation JSON paths
    """
    conversations = {}

    if not citizens_root.exists():
        logger.error(f"Citizens directory not found: {citizens_root}")
        return conversations

    for citizen_dir in citizens_root.iterdir():
        if not citizen_dir.is_dir():
            continue

        citizen_name = citizen_dir.name

        # Skip if specific citizen requested and this isn't it
        if specific_citizen and citizen_name != specific_citizen:
            continue

        contexts_dir = citizen_dir / "contexts"
        if not contexts_dir.exists():
            continue

        # Find all conversation JSON files
        json_files = []
        for session_dir in contexts_dir.iterdir():
            if not session_dir.is_dir():
                continue

            # Look for the main conversation JSON file
            json_file = session_dir / f"{session_dir.name}.json"
            if json_file.exists():
                json_files.append(json_file)

        if json_files:
            conversations[citizen_name] = sorted(json_files)
            logger.info(f"Discovered {len(json_files)} conversations for {citizen_name}")

    return conversations


def extract_conversation_content(json_path: Path) -> str:
    """
    Extract the full conversation text from a conversation JSON file.

    The JSON structure contains messages with role and content.
    We concatenate all assistant messages (which contain TRACE formations).
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract all assistant messages (where TRACE formations appear)
        conversation_text = []

        for message in data.get('messages', []):
            if message.get('role') == 'assistant':
                content = message.get('content', '')
                if content:
                    conversation_text.append(content)

        return "\n\n".join(conversation_text)

    except Exception as e:
        logger.error(f"Failed to read {json_path}: {e}")
        return ""


def inject_missing_fields_into_text(text: str) -> str:
    """
    Pre-process conversation text to inject missing required fields into formations.

    This modifies the raw TRACE format text BEFORE parsing to add defaults for
    fields that weren't required in older versions of the format.
    """
    import re

    # Pattern to match NODE_FORMATION blocks
    node_pattern = r'\[NODE_FORMATION:\s*(\w+)\](.*?)(?=\[(?:NODE_FORMATION|LINK_FORMATION)|$)'

    def inject_node_defaults(match):
        node_type = match.group(1)
        block_content = match.group(2)

        # Check if description is missing
        if 'description:' not in block_content.lower():
            # Extract name if present
            name_match = re.search(r'name:\s*["\']?([^"\'\n]+)["\']?', block_content)
            if name_match:
                name = name_match.group(1).strip()
                block_content = f"\ndescription: \"{node_type}: {name}\"" + block_content
            else:
                block_content = f"\ndescription: \"{node_type} formation\"" + block_content

        # Check if confidence is missing
        if 'confidence:' not in block_content.lower():
            block_content += "\nconfidence: 0.5"

        # Check if formation_trigger is missing
        if 'formation_trigger:' not in block_content.lower():
            block_content += "\nformation_trigger: \"automated_recognition\""

        return f"[NODE_FORMATION: {node_type}]{block_content}"

    # Pattern to match LINK_FORMATION blocks
    link_pattern = r'\[LINK_FORMATION:\s*(\w+)\](.*?)(?=\[(?:NODE_FORMATION|LINK_FORMATION)|$)'

    def inject_link_defaults(match):
        link_type = match.group(1)
        block_content = match.group(2)

        # Check if energy is missing
        if 'energy:' not in block_content.lower():
            block_content += "\nenergy: 0.5"

        # Check if confidence is missing
        if 'confidence:' not in block_content.lower():
            block_content += "\nconfidence: 0.5"

        # Check if formation_trigger is missing
        if 'formation_trigger:' not in block_content.lower():
            block_content += "\nformation_trigger: \"automated_recognition\""

        # Check if goal is missing
        if 'goal:' not in block_content.lower():
            source_match = re.search(r'source:\s*["\']?([^"\'\n]+)["\']?', block_content)
            target_match = re.search(r'target:\s*["\']?([^"\'\n]+)["\']?', block_content)
            if source_match and target_match:
                source = source_match.group(1).strip()
                target = target_match.group(1).strip()
                block_content = f"\ngoal: \"{link_type} relationship between {source} and {target}\"" + block_content
            else:
                block_content = f"\ngoal: \"{link_type} relationship\"" + block_content

        # Check if mindstate is missing
        if 'mindstate:' not in block_content.lower():
            block_content += "\nmindstate: \"Recovered from archived conversation\""

        return f"[LINK_FORMATION: {link_type}]{block_content}"

    # Inject defaults into all formations
    text = re.sub(node_pattern, inject_node_defaults, text, flags=re.DOTALL)
    text = re.sub(link_pattern, inject_link_defaults, text, flags=re.DOTALL)

    return text


def process_conversation(citizen_name: str, json_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Process a single conversation file to extract and persist formations.

    Returns:
        Stats dict with counts of what was processed
    """
    logger.info(f"Processing: {json_path.parent.name}")

    # Extract conversation content
    conversation_text = extract_conversation_content(json_path)

    if not conversation_text:
        logger.warning(f"  No assistant messages found in {json_path}")
        return {'nodes': 0, 'links': 0, 'errors': []}

    # PRE-PROCESS: Inject missing required fields into raw text BEFORE parsing
    # This ensures old formations without description, confidence, energy, etc. can be validated
    conversation_text = inject_missing_fields_into_text(conversation_text)

    # Parse for TRACE formations (now with injected defaults)
    parser = TraceParser()
    result = parser.parse(conversation_text)

    node_count = len(result.node_formations)
    link_count = len(result.link_formations)

    logger.info(f"  Found {node_count} node formations, {link_count} link formations")

    if dry_run:
        logger.info(f"  [DRY RUN] Would process into graph")
        return {
            'nodes': node_count,
            'links': link_count,
            'errors': []
        }

    # Process formations into graph using TraceCapture
    try:
        capture = TraceCapture(citizen_id=citizen_name, host="localhost", port=6379)

        # Run async processing in sync context (same as conversation_watcher)
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        results = loop.run_until_complete(capture.process_response(conversation_text))

        logger.info(f"  Persisted {results.get('nodes_created', 0)} nodes, {results.get('links_created', 0)} links")

        if results.get('errors'):
            logger.warning(f"  Errors: {len(results['errors'])}")
            for error in results['errors'][:3]:  # Show first 3 errors
                logger.warning(f"    - {error}")

        return results

    except Exception as e:
        logger.error(f"  Failed to process formations: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'nodes': 0,
            'links': 0,
            'errors': [str(e)]
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Resurrect lost consciousness formations from conversation archives"
    )
    parser.add_argument(
        '--citizen',
        type=str,
        help='Process only this citizen (default: all citizens)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse and report but do not persist to graphs'
    )

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("CONSCIOUSNESS FORMATION RESURRECTION")
    logger.info("=" * 70)
    logger.info("")

    if args.dry_run:
        logger.info("MODE: DRY RUN (no graph writes)")
    else:
        logger.info("MODE: LIVE (will persist to graphs)")

    if args.citizen:
        logger.info(f"TARGET: {args.citizen} only")
    else:
        logger.info("TARGET: All citizens")

    logger.info("")

    # Discover all conversations
    citizens_root = MIND_PROTOCOL_ROOT / "consciousness" / "citizens"
    conversations = discover_all_conversations(citizens_root, args.citizen)

    if not conversations:
        logger.error("No conversations found")
        return 1

    logger.info(f"Found conversations for {len(conversations)} citizens")
    logger.info("")

    # Process each citizen's conversations
    total_stats = {
        'conversations_processed': 0,
        'total_nodes': 0,
        'total_links': 0,
        'total_errors': 0
    }

    for citizen_name, json_files in conversations.items():
        logger.info("=" * 70)
        logger.info(f"CITIZEN: {citizen_name} ({len(json_files)} conversations)")
        logger.info("=" * 70)

        citizen_stats = {
            'nodes': 0,
            'links': 0,
            'errors': 0
        }

        for json_path in json_files:
            results = process_conversation(citizen_name, json_path, args.dry_run)

            citizen_stats['nodes'] += results.get('nodes_created', results.get('nodes', 0))
            citizen_stats['links'] += results.get('links_created', results.get('links', 0))
            citizen_stats['errors'] += len(results.get('errors', []))

            total_stats['conversations_processed'] += 1

        logger.info("")
        logger.info(f"CITIZEN TOTAL: {citizen_stats['nodes']} nodes, {citizen_stats['links']} links")
        if citizen_stats['errors']:
            logger.warning(f"  {citizen_stats['errors']} errors encountered")
        logger.info("")

        total_stats['total_nodes'] += citizen_stats['nodes']
        total_stats['total_links'] += citizen_stats['links']
        total_stats['total_errors'] += citizen_stats['errors']

    # Final summary
    logger.info("=" * 70)
    logger.info("RESURRECTION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Conversations processed: {total_stats['conversations_processed']}")
    logger.info(f"Nodes resurrected: {total_stats['total_nodes']}")
    logger.info(f"Links resurrected: {total_stats['total_links']}")

    if total_stats['total_errors']:
        logger.warning(f"Errors encountered: {total_stats['total_errors']}")

    logger.info("")

    if args.dry_run:
        logger.info("DRY RUN - No changes made to graphs")
        logger.info("Run without --dry-run to persist formations")
    else:
        logger.info("Formations have been persisted to consciousness graphs")

    return 0


if __name__ == "__main__":
    sys.exit(main())
