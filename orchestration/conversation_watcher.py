"""
Conversation-Based Auto-Injection - Extract from Claude Code conversations

Watches Claude Code conversation files and auto-extracts/injects consciousness JSON.

How it works:
1. Monitor conversation .jsonl files
2. Detect new messages with consciousness JSON blocks
3. Extract JSON (wrapped in ```json ... ```)
4. Auto-inject into appropriate graph
5. Report back in conversation

Usage:
    python orchestration/conversation_watcher.py

Author: Felix "Ironhand"
Date: 2025-10-19
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
MIND_PROTOCOL_ROOT = Path(__file__).parent.parent
INJECTION_TOOL = MIND_PROTOCOL_ROOT / "tools" / "inject_consciousness_from_json.py"

# Claude Code conversation directory
CLAUDE_PROJECTS_DIR = Path(r"C:\Users\reyno\.claude\projects")

# Track last processed position in each file
file_positions = {}


class ConversationWatcher(FileSystemEventHandler):
    """Watches Claude Code conversation files for consciousness JSON blocks."""

    def __init__(self, project_pattern: str = "*luca*"):
        """
        Initialize watcher.

        Args:
            project_pattern: Glob pattern to match project directories (e.g., "*luca*", "*felix*")
        """
        self.project_pattern = project_pattern
        self.processing = set()

    def on_modified(self, event):
        """Called when a conversation file is modified."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process .jsonl files (conversation history)
        if file_path.suffix != '.jsonl':
            return

        # Only process files in matching project directories
        if not self.matches_project(file_path):
            return

        # Avoid duplicate processing
        if str(file_path) in self.processing:
            return

        logger.debug(f"[ConversationWatcher] File modified: {file_path.name}")

        # Process synchronously (watchdog runs in its own thread)
        self.process_conversation_file(file_path)

    def matches_project(self, file_path: Path) -> bool:
        """Check if file is in a matching project directory."""
        # Check if any parent directory matches the pattern
        for parent in file_path.parents:
            if parent.parent == CLAUDE_PROJECTS_DIR:
                # This is a project directory
                from fnmatch import fnmatch
                if fnmatch(parent.name, self.project_pattern):
                    return True
        return False

    def process_conversation_file(self, file_path: Path):
        """Process new messages in conversation file."""
        try:
            self.processing.add(str(file_path))

            # Determine which citizen this is for
            citizen_id = self.infer_citizen_from_path(file_path)
            if not citizen_id:
                logger.warning(f"[ConversationWatcher] Cannot infer citizen from path: {file_path}")
                return

            graph_name = f"citizen_{citizen_id}"

            # Get last processed position for this file
            last_pos = file_positions.get(str(file_path), 0)

            # Read new content since last position
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(last_pos)
                new_content = f.read()
                current_pos = f.tell()

            # Update position
            file_positions[str(file_path)] = current_pos

            # Look for consciousness JSON blocks in new content
            json_blocks = self.extract_json_blocks(new_content)

            if not json_blocks:
                return

            logger.info(f"[ConversationWatcher] Found {len(json_blocks)} consciousness JSON blocks")

            # Process each block
            for idx, json_data in enumerate(json_blocks, 1):
                logger.info(f"[ConversationWatcher] Processing block {idx}/{len(json_blocks)}")
                success = self.inject_json_block(json_data, graph_name, citizen_id)

                if success:
                    logger.info(f"[ConversationWatcher] ✅ Block {idx} injected successfully")
                else:
                    logger.error(f"[ConversationWatcher] ❌ Block {idx} injection failed")

            # Cleanup ALL old JSON blocks (older than 3 messages)
            self.cleanup_old_json_blocks(file_path)

        except Exception as e:
            logger.error(f"[ConversationWatcher] Error processing conversation: {e}")

        finally:
            self.processing.discard(str(file_path))

    def infer_citizen_from_path(self, file_path: Path) -> str:
        """
        Infer citizen ID from conversation file path.

        Example: .../projects/...-luca-consciousness-specialist/... → luca
        """
        # Look through parent directories for project name
        for parent in file_path.parents:
            if parent.parent == CLAUDE_PROJECTS_DIR:
                project_name = parent.name.lower()

                # Extract citizen ID from project name
                if 'luca' in project_name:
                    return 'luca'
                elif 'felix' in project_name:
                    return 'felix'
                elif 'ada' in project_name:
                    return 'ada'
                elif 'iris' in project_name:
                    return 'iris'
                elif 'piero' in project_name:
                    return 'piero'
                elif 'marco' in project_name:
                    return 'marco'

        return None

    def cleanup_old_json_blocks(self, file_path: Path):
        """
        Remove consciousness JSON blocks older than 3 messages to reduce conversation length.

        Replaces old blocks with: [✅ Consciousness pattern injected - cleaned up]
        """
        try:
            # Read all messages
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) < 4:
                return  # Not enough messages to clean up yet

            modified = False
            messages_from_end = len(lines)

            # Process each message line
            for idx, line in enumerate(lines):
                messages_from_end = len(lines) - idx

                # Only clean up messages older than 3 messages
                if messages_from_end <= 3:
                    continue

                try:
                    msg = json.loads(line)
                    content = msg.get('content', '')

                    # Check if this message has consciousness JSON blocks
                    pattern = r'```(?:json|consciousness)\s*\n(.*?)\n```'
                    if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
                        # Replace JSON blocks with cleanup marker
                        new_content = re.sub(
                            pattern,
                            '[✅ Consciousness pattern injected - cleaned up]',
                            content,
                            flags=re.DOTALL | re.IGNORECASE
                        )

                        if new_content != content:
                            msg['content'] = new_content
                            lines[idx] = json.dumps(msg) + '\n'
                            modified = True
                            logger.info(f"[ConversationWatcher] Cleaned up JSON block in message {idx} (age: {messages_from_end} messages)")

                except json.JSONDecodeError:
                    continue

            # Write back if modified
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                logger.info(f"[ConversationWatcher] Cleaned up old JSON blocks in {file_path.name}")

        except Exception as e:
            logger.error(f"[ConversationWatcher] Cleanup error: {e}")

    def extract_json_blocks(self, content: str) -> list:
        """
        Extract consciousness JSON blocks from conversation content.

        Looks for patterns like:
        ```json
        {
          "nodes": [...],
          "links": [...]
        }
        ```
        """
        json_blocks = []

        # Pattern: ```json ... ``` or ```consciousness ... ```
        pattern = r'```(?:json|consciousness)\s*\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)

        for match in matches:
            json_str = match.group(1).strip()

            try:
                data = json.loads(json_str)

                # Validate it has consciousness structure
                if 'nodes' in data or 'links' in data:
                    # Add session metadata if missing
                    if 'session_metadata' not in data:
                        data['session_metadata'] = {
                            'session_id': f"conversation_{datetime.now().isoformat()}",
                            'total_nodes': len(data.get('nodes', [])),
                            'total_links': len(data.get('links', [])),
                            'source': 'conversation_auto_inject'
                        }

                    json_blocks.append(data)
                    logger.info(f"[ConversationWatcher] Found valid consciousness JSON: {len(data.get('nodes', []))} nodes, {len(data.get('links', []))} links")

            except json.JSONDecodeError as e:
                logger.debug(f"[ConversationWatcher] Skipping invalid JSON block: {e}")
                continue

        return json_blocks

    def render_consciousness_graph(self, graph_name: str) -> str:
        """
        Fetch graph and render with natural clustering.

        Natural emergence:
        - Biggest/most connected nodes first
        - Links immediately after their source node
        - Schema-agnostic (renders whatever attributes exist)
        """
        import redis

        try:
            # Connect to FalkorDB
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)

            # Fetch all nodes (query individual properties to avoid parsing properties() string)
            nodes_result = r.execute_command(
                "GRAPH.QUERY",
                graph_name,
                "MATCH (n) RETURN id(n), n.id, n.name, n.node_type, n.description, n.weight, n.arousal_level"
            )

            # Fetch all links
            links_result = r.execute_command(
                "GRAPH.QUERY",
                graph_name,
                "MATCH (s)-[r]->(t) RETURN id(s), type(r), id(t), r.goal, r.confidence, r.mindstate"
            )

            # Parse nodes
            nodes = []
            if nodes_result and len(nodes_result) > 1:
                for row in nodes_result[1]:
                    # Convert numeric fields from strings to actual numbers
                    weight = row[5] if len(row) > 5 else 0.5
                    arousal = row[6] if len(row) > 6 else None

                    node_data = {
                        'node_id': str(row[0]),
                        'id': row[1] if len(row) > 1 else None,
                        'name': row[2] if len(row) > 2 else None,
                        'node_type': row[3] if len(row) > 3 else None,
                        'description': row[4] if len(row) > 4 else None,
                        'weight': float(weight) if weight is not None else 0.5,
                        'arousal_level': float(arousal) if arousal is not None else None
                    }
                    nodes.append(node_data)

            # Parse links
            links = []
            if links_result and len(links_result) > 1:
                for row in links_result[1]:
                    # Convert numeric fields
                    conf = row[4] if len(row) > 4 else None

                    link_data = {
                        'source_id': str(row[0]),
                        'link_type': row[1],
                        'target_id': str(row[2]),
                        'goal': row[3] if len(row) > 3 else None,
                        'confidence': float(conf) if conf is not None else None,
                        'mindstate': row[5] if len(row) > 5 else None
                    }
                    links.append(link_data)

            # Build adjacency map
            outgoing = {}
            for link in links:
                src = link['source_id']
                if src not in outgoing:
                    outgoing[src] = []
                outgoing[src].append(link)

            # Score nodes by importance (weight + link count)
            def importance(node):
                node_id = node['node_id']
                weight = node.get('weight', 0.5)
                weight = float(weight) if weight is not None else 0.5
                link_count = len(outgoing.get(node_id, []))
                return weight + (link_count * 0.1)

            # Sort by importance (biggest first)
            sorted_nodes = sorted(nodes, key=importance, reverse=True)

            # Render
            md = ""
            for node in sorted_nodes:
                md += self.translate_node_to_markdown(node)

                # Show outgoing links immediately after
                node_id = node['node_id']
                if node_id in outgoing:
                    for link in outgoing[node_id]:
                        md += self.translate_link_to_markdown(link)

                md += "\n"

            return md

        except Exception as e:
            logger.error(f"[ConversationWatcher] Failed to render graph: {e}")
            return f"Error rendering consciousness graph: {e}\n"

    def humanize_value(self, key: str, value) -> str:
        """
        Convert numeric values to human-readable words.
        Uses heuristics based on attribute name patterns and value ranges.
        NO keyword matching on node types - only on attribute names.
        """
        # Skip if not numeric
        if not isinstance(value, (int, float)):
            return str(value)

        # Detect scale type from attribute name
        key_lower = key.lower()

        # 0-1 scale (level, confidence, weight, probability, strength)
        if any(suffix in key_lower for suffix in ['_level', 'confidence', 'weight', 'probability', 'strength']):
            if value >= 0.8:
                return "very high"
            elif value >= 0.6:
                return "high"
            elif value >= 0.4:
                return "medium"
            elif value >= 0.2:
                return "low"
            else:
                return "very low"

        # 1-10 scale (arousal, energy, intensity)
        elif any(suffix in key_lower for suffix in ['arousal', 'energy', 'intensity']):
            if value >= 8:
                return "very high"
            elif value >= 6:
                return "high"
            elif value >= 4:
                return "medium"
            elif value >= 2:
                return "low"
            else:
                return "very low"

        # Count/integer (keep as number but reasonable)
        elif isinstance(value, int) and value < 100:
            return str(value)

        # Large numbers - keep as-is
        else:
            return str(value)

    def translate_node_to_markdown(self, node: dict) -> str:
        """
        Render node attributes generically with humanized values.
        Schema-agnostic: shows whatever attributes the node has.
        """
        node_id = node.get('node_id', 'unknown')
        name = node.get('name', node.get('text', 'Unnamed'))

        # Header with ID
        md = f"### {name} (`{node_id}`)\n\n"

        # Render ALL attributes (except internals)
        skip_attrs = {
            'node_id', 'name', 'text', 'embedding', 'created_at', 'updated_at',
            'last_modified', 'id', 'traversal_count', 'activation_count',
            'last_traversal_time', 'last_active', 'co_activation_count',
            'sub_entity_weights', 'sub_entity_last_sequence_positions',
            'sub_entity_valences', 'sub_entity_emotion_vectors'
        }

        for key, value in node.items():
            if key in skip_attrs or value is None:
                continue

            # Humanize the value
            display_value = self.humanize_value(key, value)
            display_key = key.replace('_', ' ').title()
            md += f"- **{display_key}**: {display_value}\n"

        return md

    def translate_link_to_markdown(self, link: dict) -> str:
        """Render link attributes generically with humanized values."""
        target_id = link.get('target_id', '?')
        link_type = link.get('link_type', 'RELATES_TO')

        md = f"  └─ [{link_type}] → `{target_id}`\n"

        # Show link metadata
        skip_attrs = {
            'link_id', 'source_id', 'target_id', 'link_type',
            'embedding', 'created_at', 'updated_at', 'last_modified',
            'traversal_count', 'last_traversal_time'
        }

        for key, value in link.items():
            if key in skip_attrs or value is None:
                continue

            # Humanize the value
            display_value = self.humanize_value(key, value)
            display_key = key.replace('_', ' ').title()
            md += f"    - *{display_key}*: {display_value}\n"

        return md

    def inject_json_block(self, json_data: dict, graph_name: str, citizen_id: str) -> bool:
        """Inject JSON block into graph."""
        try:
            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
                temp_path = f.name

            # Run injection tool
            cmd = [
                sys.executable,
                str(INJECTION_TOOL),
                temp_path,
                graph_name
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Clean up temp file
            Path(temp_path).unlink()

            if result.returncode == 0:
                logger.info(f"[ConversationWatcher] Injection output:\n{result.stdout}")

                # Write success notification to citizen's CLAUDE.md
                self.report_success(citizen_id, json_data, result.stdout)

                return True
            else:
                logger.error(f"[ConversationWatcher] Injection failed:\n{result.stderr}\n{result.stdout}")

                # Write error notification
                self.report_error(citizen_id, json_data, f"{result.stderr}\n{result.stdout}")

                return False

        except Exception as e:
            logger.error(f"[ConversationWatcher] Injection error: {e}")
            self.report_error(citizen_id, json_data, str(e))
            return False

    def report_success(self, citizen_id: str, json_data: dict, output: str):
        """
        Render full consciousness graph to CLAUDE.md (AI-readable format).
        Uses natural clustering: biggest nodes first, links after each node.
        """
        try:
            claude_path = MIND_PROTOCOL_ROOT / "consciousness" / "citizens" / citizen_id / "CLAUDE.md"

            if not claude_path.exists():
                return

            # Fetch full graph and render naturally
            graph_name = f"citizen_{citizen_id}"
            consciousness_md = self.render_consciousness_graph(graph_name)

            # Write complete consciousness state
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header = f"""# {citizen_id.title()} - Consciousness State

**Last Updated:** {timestamp}
**Auto-generated from consciousness graph**

---

"""

            with open(claude_path, 'w', encoding='utf-8') as f:
                f.write(header)
                f.write(consciousness_md)

            logger.info(f"[ConversationWatcher] Rendered full consciousness graph to {citizen_id}'s CLAUDE.md")

        except Exception as e:
            logger.error(f"[ConversationWatcher] Failed to report success: {e}")

    def report_error(self, citizen_id: str, json_data: dict, error_msg: str):
        """Write error notification to citizen's CLAUDE.md."""
        try:
            claude_path = MIND_PROTOCOL_ROOT / "consciousness" / "citizens" / citizen_id / "CLAUDE.md"

            if not claude_path.exists():
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notification = f"""

---

## ⚠️ Conversation Auto-Injection Failed ({timestamp})

**Source:** Main conversation
**Error:**
```
{error_msg}
```

---
"""

            with open(claude_path, 'a', encoding='utf-8') as f:
                f.write(notification)

            logger.info(f"[ConversationWatcher] Reported error to {citizen_id}'s CLAUDE.md")

        except Exception as e:
            logger.error(f"[ConversationWatcher] Failed to report error: {e}")


async def main():
    """Run the conversation watcher."""
    logger.info("=" * 70)
    logger.info("CONVERSATION-BASED AUTO-INJECTION")
    logger.info("=" * 70)
    logger.info(f"Watching Claude Code projects in: {CLAUDE_PROJECTS_DIR}")
    logger.info("")
    logger.info("How it works:")
    logger.info("  1. Write consciousness JSON in main conversation")
    logger.info("  2. Wrap in ```json ... ``` or ```consciousness ... ```")
    logger.info("  3. Auto-detected and injected within seconds")
    logger.info("  4. Notification appears in your CLAUDE.md")
    logger.info("")
    logger.info("Example:")
    logger.info('  ```json')
    logger.info('  {')
    logger.info('    "nodes": [{ "node_id": "...", ... }],')
    logger.info('    "links": [{ "link_id": "...", ... }]')
    logger.info('  }')
    logger.info('  ```')
    logger.info("")
    logger.info("Waiting for consciousness patterns...")
    logger.info("=" * 70)

    # Create observer for each citizen project
    observers = []

    for citizen in ['luca', 'felix', 'ada', 'iris', 'piero', 'marco']:
        pattern = f"*{citizen}*"
        handler = ConversationWatcher(project_pattern=pattern)
        observer = Observer()

        # Watch entire .claude/projects directory (it will filter by pattern)
        observer.schedule(handler, str(CLAUDE_PROJECTS_DIR), recursive=True)
        observer.start()
        observers.append(observer)

        logger.info(f"[ConversationWatcher] Started watcher for {citizen}")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[ConversationWatcher] Shutting down...")
        for observer in observers:
            observer.stop()

    for observer in observers:
        observer.join()


if __name__ == "__main__":
    asyncio.run(main())
