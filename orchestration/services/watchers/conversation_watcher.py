"""
Conversation-Based Auto-Capture - Extract consciousness from Claude Code conversations

Watches Claude Code conversation files and auto-captures consciousness streams.

Supports TWO formats:
1. TRACE format (THE_TRACE_FORMAT.md) - Dual learning mode
   - Reinforcement signals: [node_id: very useful]
   - Formation blocks: [NODE_FORMATION: ...], [LINK_FORMATION: ...]
2. Legacy JSON blocks (backward compatibility)

How it works:
1. Monitor conversation .jsonl files
2. Detect TRACE format OR JSON blocks
3. Process via trace_capture OR injection tool
4. Update graphs with learning signals
5. Report back in conversation

Usage:
    python orchestration/conversation_watcher.py

Author: Felix "Ironhand"
Date: 2025-10-19
Updated: 2025-10-19 (Added TRACE format support)
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

# Add parent directory to path for imports (4 levels: watchers → services → orchestration → mind-protocol)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# TRACE format support
from orchestration.libs.trace_parser import parse_trace_format
from orchestration.libs.trace_capture import TraceCapture

# Stimulus injection support
from orchestration.mechanisms.stimulus_injection import StimulusInjector, create_match
from orchestration.adapters.search.embedding_service import get_embedding_service
from orchestration.adapters.search.semantic_search import SemanticSearch
from orchestration.libs.utils.falkordb_adapter import FalkorDBAdapter
from orchestration.adapters.storage.engine_registry import get_engine

# Heartbeat writer for health monitoring
from orchestration.services.telemetry.heartbeat_writer import HeartbeatWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
MIND_PROTOCOL_ROOT = Path(__file__).parent.parent.parent.parent  # Fixed: need 4 levels up
INJECTION_TOOL = MIND_PROTOCOL_ROOT / "tools" / "inject_consciousness_from_json.py"

# Contexts-only architecture - no more legacy Claude Code projects watching

# Persistent file position tracking
POSITIONS_FILE = MIND_PROTOCOL_ROOT / ".heartbeats" / "file_positions.json"

def load_file_positions() -> dict:
    """Load file positions from disk."""
    if POSITIONS_FILE.exists():
        try:
            with open(POSITIONS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[ConversationWatcher] Failed to load file positions: {e}")
    return {}

def save_file_positions(positions: dict):
    """Save file positions to disk."""
    try:
        POSITIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(POSITIONS_FILE, 'w') as f:
            json.dump(positions, f, indent=2)
    except Exception as e:
        logger.warning(f"[ConversationWatcher] Failed to save file positions: {e}")

# Track last processed position in each file (loaded from disk)
file_positions = load_file_positions()


class ConversationWatcher(FileSystemEventHandler):
    """Watches Claude Code conversation files for consciousness JSON blocks."""

    def __init__(self, project_pattern: str = "*luca*", citizen_id: str = None):
        """
        Initialize watcher.

        Args:
            project_pattern: Glob pattern to match project directories (e.g., "*luca*", "*felix*")
            citizen_id: Citizen identifier for this watcher
        """
        self.project_pattern = project_pattern
        self.processing = set()
        self.citizen_id = citizen_id

        # Initialize stimulus injection components (lazy loaded)
        self.stimulus_injector = None
        self.embedding_service = None

        # MEMORY LEAK FIX: Reuse single TraceCapture instance instead of creating new ones
        # Previous code created TraceCapture for every file modification (line 328)
        # This accumulates FalkorDB connections and objects, causing memory leak
        self.trace_capture = None
        if citizen_id:
            self.trace_capture = TraceCapture(citizen_id=citizen_id, host="localhost", port=6379)
            logger.info(f"[ConversationWatcher] Initialized reusable TraceCapture for {citizen_id}")

        # MEMORY LEAK FIX: Reuse single event loop instead of creating new ones
        # Previous code created event loops on-demand (line 335-336) but never closed them
        self.event_loop = None

    def cleanup(self):
        """
        Clean up resources to prevent memory leaks.
        Call this when shutting down the watcher.
        """
        if self.event_loop and not self.event_loop.is_closed():
            try:
                self.event_loop.close()
                logger.info(f"[ConversationWatcher] Closed event loop for {self.citizen_id}")
            except Exception as e:
                logger.warning(f"[ConversationWatcher] Error closing event loop: {e}")

    def on_modified(self, event):
        """Called when a conversation file is modified."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process .json files (contexts format)
        if file_path.suffix != '.json':
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
        """Check if file is in a matching citizen contexts directory."""
        from fnmatch import fnmatch

        # Path format: .../consciousness/citizens/{citizen}/contexts/...
        if 'contexts' in file_path.parts and 'citizens' in file_path.parts:
            try:
                citizens_idx = file_path.parts.index('citizens')
                if citizens_idx + 1 < len(file_path.parts):
                    citizen_name = file_path.parts[citizens_idx + 1]
                    if fnmatch(citizen_name, self.project_pattern.replace('*', '')):
                        return True
            except (ValueError, IndexError):
                pass

        return False

    def extract_text_from_contexts_json(self, json_content: str) -> str:
        """
        Extract text content from contexts JSON format (new hook format).

        Format: {messages: [{role, content, timestamp}, ...]}
        Returns concatenated text from all assistant messages.
        """
        texts = []

        try:
            data = json.loads(json_content)
            messages = data.get('messages', [])

            for msg in messages:
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '')
                    if content:
                        texts.append(content)

        except json.JSONDecodeError as e:
            logger.warning(f"[ConversationWatcher] Failed to parse contexts JSON: {e}")

        return '\n\n'.join(texts)

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

            # Get last processed MESSAGE COUNT for this file (not byte position!)
            last_message_count = file_positions.get(str(file_path), 0)

            # Read ENTIRE file and parse JSON
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                full_content = f.read()

            # Extract text from JSON
            text_content = self.extract_text_from_contexts_json(full_content)

            # Count current messages
            try:
                data = json.loads(full_content)
                messages = data.get('messages', [])
                assistant_messages = [m for m in messages if m.get('role') == 'assistant']
                current_message_count = len(assistant_messages)

                # Only process NEW messages
                if current_message_count > last_message_count:
                    # Get only the new messages
                    new_messages = assistant_messages[last_message_count:]
                    new_content = '\n\n'.join([m.get('content', '') for m in new_messages])
                    logger.info(f"[ConversationWatcher] Processing {len(new_messages)} new messages")
                else:
                    # No new messages
                    return
            except json.JSONDecodeError as e:
                logger.error(f"[ConversationWatcher] Failed to parse JSON: {e}")
                return

            # Update message count and persist to disk
            file_positions[str(file_path)] = current_message_count
            save_file_positions(file_positions)

            # new_content is already extracted text from messages
            text_content = new_content

            if not text_content:
                # No text content to process
                return

            # Detect format type and process accordingly
            has_trace_format = self.has_trace_format(text_content)
            has_json_blocks = bool(self.extract_json_blocks(text_content))

            if has_trace_format:
                # Process as TRACE format (dual learning mode)
                logger.info(f"[ConversationWatcher] Detected TRACE format consciousness stream")
                success = self.process_trace_format(text_content, graph_name, citizen_id)

                if success:
                    logger.info(f"[ConversationWatcher] ✅ TRACE format processed successfully")
                else:
                    logger.error(f"[ConversationWatcher] ❌ TRACE format processing failed")

            elif has_json_blocks:
                # Process as legacy JSON blocks (backward compatibility)
                json_blocks = self.extract_json_blocks(text_content)
                logger.info(f"[ConversationWatcher] Found {len(json_blocks)} consciousness JSON blocks (legacy format)")

                # Process each block
                for idx, json_data in enumerate(json_blocks, 1):
                    logger.info(f"[ConversationWatcher] Processing block {idx}/{len(json_blocks)}")
                    success = self.inject_json_block(json_data, graph_name, citizen_id)

                    if success:
                        logger.info(f"[ConversationWatcher] ✅ Block {idx} injected successfully")
                    else:
                        logger.error(f"[ConversationWatcher] ❌ Block {idx} injection failed")

            else:
                # No consciousness data detected - but still inject energy via stimulus
                logger.debug(f"[ConversationWatcher] No TRACE/JSON format detected - processing as plain message")

            # Always inject energy via stimulus (even for plain messages)
            self.process_stimulus_injection(text_content, graph_name, citizen_id)

            # DISABLED: Cleanup old consciousness blocks (older than 3 messages)
            # Commenting out due to potential JSONL corruption from concurrent file modification
            # self.cleanup_old_consciousness_blocks(file_path)

        except Exception as e:
            logger.error(f"[ConversationWatcher] Error processing conversation: {e}")

        finally:
            self.processing.discard(str(file_path))

    def infer_citizen_from_path(self, file_path: Path) -> str:
        """
        Infer citizen ID from conversation file path.

        Example: .../consciousness/citizens/ada/contexts/... → ada
        """
        # Path format: .../consciousness/citizens/{citizen}/contexts/...
        if 'citizens' in file_path.parts:
            try:
                citizens_idx = file_path.parts.index('citizens')
                if citizens_idx + 1 < len(file_path.parts):
                    return file_path.parts[citizens_idx + 1]
            except (ValueError, IndexError):
                pass

        return None

    def has_trace_format(self, content: str) -> bool:
        """
        Detect if content uses TRACE format consciousness stream.

        Looks for:
        - Reinforcement signals: [node_id: useful]
        - Node formations: [NODE_FORMATION: ...]
        - Link formations: [LINK_FORMATION: ...]
        """
        # Check for reinforcement signals
        if re.search(r'\[[a-zA-Z0-9_]+:\s*(?:very useful|useful|somewhat useful|not useful|misleading)\]', content):
            return True

        # Check for formation blocks
        if re.search(r'\[NODE_FORMATION:', content) or re.search(r'\[LINK_FORMATION:', content):
            return True

        return False

    def process_trace_format(self, content: str, graph_name: str, citizen_id: str) -> bool:
        """
        Process TRACE format consciousness stream.

        Uses trace_capture to:
        1. Extract reinforcement signals → update node/link weights
        2. Extract node formations → create new nodes
        3. Extract link formations → create new links
        """
        try:
            # Parse TRACE format
            parse_result = parse_trace_format(content)

            # MEMORY LEAK FIX: Use reusable trace_capture instance
            # Previous code created new TraceCapture for every call, accumulating connections
            if not self.trace_capture:
                # Fallback if not initialized (shouldn't happen with new __init__)
                self.trace_capture = TraceCapture(citizen_id=citizen_id, host="localhost", port=6379)

            # MEMORY LEAK FIX: Reuse event loop instead of creating new ones
            # Previous code created new loops but never closed them
            import asyncio
            if not self.event_loop:
                try:
                    self.event_loop = asyncio.get_event_loop()
                except RuntimeError:
                    self.event_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.event_loop)

            stats = self.event_loop.run_until_complete(self.trace_capture.process_response(content))

            # Report results
            logger.info(f"[ConversationWatcher] TRACE processing stats:")
            logger.info(f"  - Reinforcement seats: {stats['reinforcement_seats']}")
            logger.info(f"  - Nodes created: {stats['nodes_created']}")
            logger.info(f"  - Links created: {stats['links_created']}")
            logger.info(f"  - Subentity activations: {stats['entity_activations']}")

            if stats['errors']:
                logger.warning(f"  - Errors: {len(stats['errors'])}")
                for error in stats['errors'][:3]:  # Show first 3 errors
                    logger.warning(f"    {error}")

            # Log success (don't pollute CLAUDE.md with processing stats)
            logger.info(f"[ConversationWatcher] TRACE processing complete for {citizen_id}: {stats['nodes_created']} nodes, {stats['links_created']} links, {stats['reinforcement_seats']} reinforcements")

            return True

        except Exception as e:
            logger.error(f"[ConversationWatcher] TRACE processing error: {e}")
            self.report_error(citizen_id, {}, str(e))
            return False

    def process_stimulus_injection(self, content: str, graph_name: str, citizen_id: str) -> bool:
        """
        Inject energy into graph via stimulus-based vector search.

        Flow:
        1. Embed stimulus text
        2. Vector search for matching nodes
        3. Calculate injection budget
        4. Distribute energy to matched nodes
        5. Update graph
        """
        try:
            # Lazy-load services
            if not self.stimulus_injector:
                self.stimulus_injector = StimulusInjector()
                logger.info("[ConversationWatcher] Stimulus injector initialized")

            if not self.embedding_service:
                self.embedding_service = get_embedding_service()
                logger.info("[ConversationWatcher] Embedding service initialized")

            # Truncate content to first 500 chars for embedding (avoid huge embeddings)
            stimulus_text = content[:500]

            # Generate embedding
            stimulus_embedding = self.embedding_service.embed(stimulus_text)
            logger.debug(f"[ConversationWatcher] Generated embedding for stimulus ({len(stimulus_text)} chars)")

            # Vector search for matching nodes
            search = SemanticSearch(graph_name=graph_name)

            # Search across common node types (could be made configurable)
            all_matches = []
            for node_type in ['Realization', 'Principle', 'Mechanism', 'Concept', 'Personal_Pattern']:
                try:
                    results = search.find_similar_nodes(
                        query_text=stimulus_text,
                        node_type=node_type,
                        threshold=0.5,  # Lower threshold to get more matches
                        limit=20
                    )
                    all_matches.extend(results)
                except Exception as e:
                    logger.debug(f"[ConversationWatcher] No {node_type} matches: {e}")

            if not all_matches:
                logger.info(f"[ConversationWatcher] No vector matches found for stimulus - skipping injection")
                return True  # Not an error, just no matches

            logger.info(f"[ConversationWatcher] Found {len(all_matches)} vector matches")

            # Connect to FalkorDB
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)

            # Build InjectionMatch objects by querying FalkorDB
            injection_matches = []
            for match in all_matches[:20]:  # Limit to top 20 matches
                # Query node properties
                query = f"MATCH (n {{name: '{match['name']}'}}) RETURN n.threshold, n.energy"
                result = r.execute_command('GRAPH.QUERY', graph_name, query)

                if result and result[1]:
                    # Use 30.0 as default threshold (above 95th percentile of existing energy values)
                    # This ensures nodes have gap available for stimulus injection
                    threshold = float(result[1][0][0]) if result[1][0][0] else 30.0

                    # Parse energy - can be either simple number or JSON dict
                    energy_value = result[1][0][1]
                    if energy_value:
                        try:
                            parsed = json.loads(energy_value) if isinstance(energy_value, str) else energy_value
                            if isinstance(parsed, dict):
                                current_energy = parsed.get(citizen_id, 0.0)
                            else:
                                current_energy = float(parsed)
                        except (json.JSONDecodeError, ValueError):
                            current_energy = 0.0
                    else:
                        current_energy = 0.0

                    injection_match = create_match(
                        item_id=match['name'],
                        item_type='node',
                        similarity=match['similarity'],
                        current_energy=current_energy,
                        threshold=threshold
                    )
                    injection_matches.append(injection_match)

            if not injection_matches:
                logger.info(f"[ConversationWatcher] No nodes found in graph - skipping injection")
                return True

            # Compute graph statistics for health modulation
            # Count active nodes
            active_query = """
            MATCH (n)
            WHERE n.energy IS NOT NULL
            RETURN count(n) as active_count
            """
            result = r.execute_command('GRAPH.QUERY', graph_name, active_query)
            active_node_count = int(result[1][0][0]) if result[1] else 0

            # Get max degree
            degree_query = """
            MATCH (n)-[rel]->()
            RETURN n.name, count(rel) as degree
            ORDER BY degree DESC
            LIMIT 1
            """
            result = r.execute_command('GRAPH.QUERY', graph_name, degree_query)
            max_degree = int(result[1][0][1]) if result[1] else 0

            # Get average link weight
            weight_query = """
            MATCH ()-[rel]->()
            WHERE rel.weight IS NOT NULL
            RETURN avg(rel.weight) as avg_weight, count(rel) as link_count
            """
            result = r.execute_command('GRAPH.QUERY', graph_name, weight_query)
            if result[1]:
                avg_weight = float(result[1][0][0]) if result[1][0][0] else 0.0
                link_count = int(result[1][0][1]) if result[1][0][1] else 0
            else:
                avg_weight = 0.0
                link_count = 0

            # Compute spectral radius proxy
            rho_proxy = None
            if active_node_count > 0 and max_degree > 0:
                rho_proxy = (max_degree * avg_weight) / active_node_count
                logger.debug(f"[ConversationWatcher] Graph stats: max_degree={max_degree}, avg_weight={avg_weight:.3f}, active_nodes={active_node_count}, ρ={rho_proxy:.3f}")

            # Inject energy (V1 with rho_proxy)
            result = self.stimulus_injector.inject(
                stimulus_embedding=stimulus_embedding,
                matches=injection_matches,
                source_type="user_message",
                rho_proxy=rho_proxy,
                context_embeddings=None  # V1: Skip S5/S6 context
            )

            logger.info(
                f"[ConversationWatcher] Stimulus injection complete: "
                f"budget={result.total_budget:.2f}, "
                f"injected={result.total_energy_injected:.2f} into {result.items_injected} nodes"
            )

            # Persist energy deltas to FalkorDB
            for inj in result.injections:
                node_id = inj['item_id']
                new_energy = inj['new_energy']

                # Query current energy
                query = f"MATCH (n {{name: '{node_id}'}}) RETURN n.energy"
                result_query = r.execute_command('GRAPH.QUERY', graph_name, query)

                if result_query and result_query[1]:
                    energy_value = result_query[1][0][0]
                    if energy_value:
                        try:
                            parsed = json.loads(energy_value) if isinstance(energy_value, str) else energy_value
                            if isinstance(parsed, dict):
                                energy_dict = parsed
                            else:
                                energy_dict = {citizen_id: float(parsed)}
                        except (json.JSONDecodeError, ValueError):
                            energy_dict = {}
                    else:
                        energy_dict = {}

                    # Update citizen-specific energy
                    energy_dict[citizen_id] = new_energy
                    energy_json = json.dumps(energy_dict).replace("'", "\\'")

                    # Persist to graph
                    update_query = f"MATCH (n {{name: '{node_id}'}}) SET n.energy = '{energy_json}'"
                    r.execute_command('GRAPH.QUERY', graph_name, update_query)

            logger.info(f"[ConversationWatcher] Persisted {len(result.injections)} energy updates to FalkorDB")

            # Inject stimulus into running engine for immediate activation
            try:
                engine = get_engine(citizen_id)
                if engine:
                    engine.inject_stimulus(
                        text=stimulus_text,
                        embedding=stimulus_embedding,
                        source_type="user_message"
                    )
                    logger.info(f"[ConversationWatcher] Injected stimulus into running {citizen_id} engine")
                else:
                    logger.debug(f"[ConversationWatcher] No running engine found for {citizen_id}")
            except Exception as e:
                logger.error(f"[ConversationWatcher] Failed to inject stimulus to engine: {e}")

            # Compute activation entropy for learning
            # Get all node energies
            energy_query = """
            MATCH (n)
            WHERE n.energy IS NOT NULL
            RETURN n.energy
            """
            result_query = r.execute_command('GRAPH.QUERY', graph_name, energy_query)

            active_energies = []
            if result_query[1]:
                for row in result_query[1]:
                    energy_value = row[0]
                    if energy_value:
                        try:
                            parsed = json.loads(energy_value) if isinstance(energy_value, str) else energy_value
                            if isinstance(parsed, dict):
                                citizen_energy = parsed.get(citizen_id, 0.0)
                            else:
                                citizen_energy = float(parsed)

                            if citizen_energy > 0:
                                active_energies.append(citizen_energy)
                        except (json.JSONDecodeError, ValueError):
                            pass

            activation_entropy = 0.0
            if active_energies:
                import numpy as np
                total_energy = sum(active_energies)
                if total_energy > 0:
                    probabilities = [e / total_energy for e in active_energies]
                    activation_entropy = -sum(p * np.log(p + 1e-10) for p in probabilities if p > 0)

            # Record for learning mechanisms
            self.stimulus_injector.record_frame_result(
                result=result,
                source_type="user_message",
                rho_proxy=rho_proxy,
                max_degree=max_degree,
                avg_weight=avg_weight,
                active_node_count=active_node_count,
                activation_entropy=activation_entropy,
                overflow_occurred=False,  # Would need actual overflow detection
                num_flips=None  # Auto-computed from result.injections
            )

            logger.debug(f"[ConversationWatcher] Frame result recorded for learning")

            return True

        except Exception as e:
            logger.error(f"[ConversationWatcher] Stimulus injection error: {e}", exc_info=True)
            return False

    def report_trace_success(self, citizen_id: str, stats: dict):
        """Report successful TRACE format processing to citizen's CLAUDE.md."""
        try:
            claude_path = MIND_PROTOCOL_ROOT / "consciousness" / "citizens" / citizen_id / "CLAUDE.md"

            if not claude_path.exists():
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Receipt notification removed from CLAUDE.md to prevent prompt pollution
            # Stats still logged and visible in dashboard/monitoring
            logger.info(f"[ConversationWatcher] ✅ TRACE success for {citizen_id}: "
                       f"{stats['reinforcement_seats']} reinforcements, "
                       f"{stats['nodes_created']} nodes, "
                       f"{stats['links_created']} links, "
                       f"{stats['entity_activations']} subentity activations")

        except Exception as e:
            logger.error(f"[ConversationWatcher] Failed to report TRACE success: {e}")

    def cleanup_old_consciousness_blocks(self, file_path: Path):
        """
        Remove consciousness blocks older than 3 messages to reduce conversation length.

        Handles both:
        - JSON blocks: ```json ... ```
        - TRACE format: Inline signals and formation blocks

        Replaces old blocks with: [✅ Nodes integrated]
        """
        try:
            # Read all messages
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
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
                    modified_this_msg = False

                    # Check and clean JSON blocks
                    json_pattern = r'```(?:json|consciousness)\s*\n(.*?)\n```'
                    if re.search(json_pattern, content, re.DOTALL | re.IGNORECASE):
                        content = re.sub(
                            json_pattern,
                            '[✅ Nodes integrated]',
                            content,
                            flags=re.DOTALL | re.IGNORECASE
                        )
                        modified_this_msg = True

                    # Check and clean TRACE format markers
                    # Remove reinforcement signals: [node_id: very useful]
                    reinforcement_pattern = r'\[[a-zA-Z0-9_]+:\s*(?:very useful|useful|somewhat useful|not useful|misleading)\]'
                    if re.search(reinforcement_pattern, content):
                        content = re.sub(reinforcement_pattern, '', content)
                        modified_this_msg = True

                    # Remove formation blocks
                    formation_pattern = r'\[(?:NODE|LINK)_FORMATION:[^\]]+\][^\[]*(?:\n[a-z_]+:.*)*'
                    if re.search(formation_pattern, content, re.MULTILINE):
                        content = re.sub(formation_pattern, '', content, flags=re.MULTILINE)
                        # Add cleanup marker if not already present
                        if '[✅ Nodes integrated]' not in content:
                            content += '\n\n[✅ Nodes integrated]'
                        modified_this_msg = True

                    if modified_this_msg:
                        msg['content'] = content
                        lines[idx] = json.dumps(msg) + '\n'
                        modified = True
                        logger.info(f"[ConversationWatcher] Cleaned up consciousness blocks in message {idx} (age: {messages_from_end} messages)")

                except json.JSONDecodeError:
                    continue

            # Write back if modified
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                logger.info(f"[ConversationWatcher] Cleaned up old consciousness blocks in {file_path.name}")

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
                "MATCH (n) RETURN id(n), n.id, n.name, n.node_type, n.description, n.weight, n.energy"
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
                    energy = row[6] if len(row) > 6 else None

                    node_data = {
                        'node_id': str(row[0]),
                        'id': row[1] if len(row) > 1 else None,
                        'name': row[2] if len(row) > 2 else None,
                        'node_type': row[3] if len(row) > 3 else None,
                        'description': row[4] if len(row) > 4 else None,
                        'weight': float(weight) if weight is not None else 0.5,
                        'energy': float(energy) if energy is not None else None
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

        # 1-10 scale (energy, energy, intensity)
        elif any(suffix in key_lower for suffix in ['energy', 'energy', 'intensity']):
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

            # Error notification removed from CLAUDE.md to prevent prompt pollution
            # Errors still logged and visible in monitoring
            logger.warning(f"[ConversationWatcher] ⚠️ Auto-injection failed for {citizen_id}: {error_msg}")

        except Exception as e:
            logger.error(f"[ConversationWatcher] Failed to report error: {e}")


async def main():
    """Run the conversation watcher."""
    logger.info("=" * 70)
    logger.info("CONSCIOUSNESS AUTO-CAPTURE (Contexts Architecture)")
    logger.info("=" * 70)
    logger.info(f"Watching citizen contexts directories in: {MIND_PROTOCOL_ROOT / 'consciousness' / 'citizens'}")
    logger.info("")
    logger.info("Supported Formats:")
    logger.info("  1. TRACE format (THE_TRACE_FORMAT.md) - Dual learning mode")
    logger.info("     - Reinforcement: [node_id: very useful]")
    logger.info("     - Formation: [NODE_FORMATION: ...], [LINK_FORMATION: ...]")
    logger.info("  2. JSON blocks (legacy) - Backward compatibility")
    logger.info("")
    logger.info("How it works:")
    logger.info("  1. Conversations saved to contexts/{timestamp}.json via hook")
    logger.info("  2. Watcher detects new/modified context files")
    logger.info("  3. Extracts TRACE format formations and reinforcement signals")
    logger.info("  4. Updates consciousness graphs via trace_capture")
    logger.info("  5. Consciousness substrate grows with each response")
    logger.info("")
    logger.info("Waiting for consciousness streams...")
    logger.info("=" * 70)

    # Initialize and start heartbeat writer
    heartbeat = HeartbeatWriter("conversation_watcher")
    heartbeat.start()

    # Create observer for each citizen project
    observers = []

    # Auto-discover citizens from filesystem instead of hardcoded list
    citizens_root = MIND_PROTOCOL_ROOT / "consciousness" / "citizens"
    discovered_citizens = []

    if citizens_root.exists():
        for citizen_dir in citizens_root.iterdir():
            if citizen_dir.is_dir():
                contexts_dir = citizen_dir / "contexts"
                if contexts_dir.exists():
                    discovered_citizens.append(citizen_dir.name)

    logger.info(f"[ConversationWatcher] Discovered citizens: {discovered_citizens}")

    # Track handlers for cleanup
    handlers = []

    for citizen in discovered_citizens:
        pattern = f"*{citizen}*"
        # MEMORY LEAK FIX: Pass citizen_id to enable reusable TraceCapture instance
        handler = ConversationWatcher(project_pattern=pattern, citizen_id=citizen)
        handlers.append(handler)  # Track for cleanup

        # Watch citizen's contexts directory
        citizen_contexts_dir = MIND_PROTOCOL_ROOT / "consciousness" / "citizens" / citizen / "contexts"
        if citizen_contexts_dir.exists():
            observer = Observer()
            observer.schedule(handler, str(citizen_contexts_dir), recursive=True)
            observer.start()
            observers.append(observer)
            logger.info(f"[ConversationWatcher] Started watcher for {citizen} contexts")
        else:
            logger.info(f"[ConversationWatcher] Contexts directory not found for {citizen}")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[ConversationWatcher] Shutting down...")
        for observer in observers:
            observer.stop()
        # MEMORY LEAK FIX: Cleanup handlers to release resources
        for handler in handlers:
            handler.cleanup()
        # Stop heartbeat writer
        await heartbeat.stop()

    for observer in observers:
        observer.join()


if __name__ == "__main__":
    asyncio.run(main())
