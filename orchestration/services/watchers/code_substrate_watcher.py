"""
Code Substrate Watcher - Auto-create Code and Documentation nodes

Watches code and documentation files, auto-creating nodes in N2 organization graph.

Monitors:
- orchestration/*.py
- substrate/**/*.py
- app/**/*.{ts,tsx}
- docs/**/*.md
- consciousness/**/*.md

On file create/modify:
1. Check if Code/Documentation node exists in N2
2. If not → create node with auto_created flag
3. If exists → update last_modified timestamp
4. Nodes get enriched manually or via periodic enrichment tool

Author: Ada "Bridgekeeper" (extending Felix's file watcher pattern)
Date: 2025-10-19
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
MIND_PROTOCOL_ROOT = Path(__file__).parent.parent

# Directories to watch
WATCH_DIRS = [
    MIND_PROTOCOL_ROOT / "orchestration",
    MIND_PROTOCOL_ROOT / "substrate",
    MIND_PROTOCOL_ROOT / "app",
    MIND_PROTOCOL_ROOT / "docs",
    MIND_PROTOCOL_ROOT / "consciousness",
    MIND_PROTOCOL_ROOT / "tools",
]


class CodeSubstrateHandler(FileSystemEventHandler):
    """Handles code/doc file changes by auto-creating nodes in N2."""

    def __init__(self):
        self.processing = set()  # Track files being processed
        self.db = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.n2_graph = "ecosystem"  # L3 ecosystem graph (was collective_n2)

    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process relevant file types
        if not self._should_process(file_path):
            return

        # Avoid duplicate processing
        if str(file_path) in self.processing:
            return

        logger.info(f"📄 NEW FILE: {self._relative_path(file_path)}")

        # Process asynchronously
        asyncio.create_task(self.process_file(file_path, change_type="created"))

    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process relevant file types
        if not self._should_process(file_path):
            return

        # Avoid duplicate processing
        if str(file_path) in self.processing:
            return

        # Process asynchronously
        asyncio.create_task(self.process_file(file_path, change_type="modified"))

    def _should_process(self, file_path: Path) -> bool:
        """Check if file should be processed."""

        # Skip __pycache__, node_modules, .git, etc.
        skip_dirs = {'__pycache__', 'node_modules', '.git', 'venv', '.next', 'dist', 'build'}
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            return False

        # Process Python, TypeScript, and Markdown files
        return file_path.suffix in ['.py', '.ts', '.tsx', '.md']

    def _relative_path(self, file_path: Path) -> str:
        """Get path relative to Mind Protocol root."""
        try:
            return str(file_path.relative_to(MIND_PROTOCOL_ROOT))
        except ValueError:
            return str(file_path)

    async def process_file(self, file_path: Path, change_type: str):
        """Process a code or documentation file."""
        try:
            self.processing.add(str(file_path))

            # Small delay to ensure file is fully written
            await asyncio.sleep(0.3)

            # Determine node type
            if file_path.suffix in ['.py', '.ts', '.tsx']:
                node_type = 'Code'
                language = self._detect_language(file_path.suffix)
            elif file_path.suffix == '.md':
                node_type = 'Documentation'
                language = None
            else:
                return

            # Find or create node
            relative_path = self._relative_path(file_path)
            node_result = await self._find_or_create_node(
                relative_path,
                node_type,
                language,
                change_type
            )

            if node_result['created']:
                logger.info(f"  ✅ Created {node_type} node: {relative_path}")
            elif node_result['updated']:
                logger.info(f"  🔄 Updated {node_type} node: {relative_path}")

        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")

        finally:
            self.processing.discard(str(file_path))

    def _detect_language(self, suffix: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'python',
            '.ts': 'typescript',
            '.tsx': 'typescript',
        }
        return language_map.get(suffix, 'unknown')

    async def _find_or_create_node(
        self,
        file_path: str,
        node_type: str,
        language: str,
        change_type: str
    ) -> dict:
        """Find existing node or create new one. Returns result dict."""

        # Query for existing node
        query = f"""
        MATCH (n:{node_type} {{file_path: $file_path}})
        RETURN id(n) as node_id, n.auto_created as auto_created
        """

        result = self.db.execute_command(
            "GRAPH.QUERY",
            self.n2_graph,
            query,
            f"file_path='{file_path}'"
        )

        if result:
            # Node exists → update timestamp
            node_id = result[0]['node_id']
            await self._update_node_timestamp(node_id, node_type)
            return {'created': False, 'updated': True, 'node_id': node_id}
        else:
            # Node doesn't exist → create it
            node_id = await self._create_node(file_path, node_type, language)
            return {'created': True, 'updated': False, 'node_id': node_id}

    async def _create_node(self, file_path: str, node_type: str, language: str) -> int:
        """Create new Code or Documentation node in N2."""

        if node_type == 'Code':
            # Create Code node with universal + type-specific fields
            query = """
            CREATE (n:Code {
                name: $name,
                file_path: $file_path,
                language: $language,
                purpose: $purpose,
                description: $description,
                node_type: 'Code',

                base_weight: 0.5,
                decay_rate: 0.95,
                reinforcement_weight: 0.0,

                created_at: datetime(),
                valid_at: datetime(),
                expired_at: null,
                invalid_at: null,

                confidence: 0.7,
                formation_trigger: 'automated_recognition',

                created_by: 'code_substrate_watcher',
                substrate: 'organizational',

                auto_created: true,
                needs_enrichment: true
            })
            RETURN id(n) as node_id
            """

            # Generate name from file path
            name = file_path.replace('/', '_').replace('\\', '_').replace('.', '_')

            params = {
                "name": name,
                "file_path": file_path,
                "language": language,
                "purpose": "[Auto-created - needs enrichment]",
                "description": f"Code file: {file_path}"
            }

        else:  # Documentation
            query = """
            CREATE (n:Documentation {
                name: $name,
                file_path: $file_path,
                description: $description,
                node_type: 'Documentation',

                base_weight: 0.5,
                decay_rate: 0.95,
                reinforcement_weight: 0.0,

                created_at: datetime(),
                valid_at: datetime(),
                expired_at: null,
                invalid_at: null,

                confidence: 0.7,
                formation_trigger: 'automated_recognition',

                created_by: 'code_substrate_watcher',
                substrate: 'organizational',

                auto_created: true,
                needs_enrichment: true
            })
            RETURN id(n) as node_id
            """

            # Generate name from file path
            name = file_path.replace('/', '_').replace('\\', '_').replace('.', '_')

            params = {
                "name": name,
                "file_path": file_path,
                "description": f"Documentation: {file_path}"
            }

        # Convert params to Cypher parameters
        param_str = ", ".join([f"{k}='{v}'" for k, v in params.items()])

        result = self.db.execute_command(
            "GRAPH.QUERY",
            self.n2_graph,
            query,
            param_str if param_str else ""
        )
        return result[0]['node_id']

    async def _update_node_timestamp(self, node_id: int, node_type: str):
        """Update last_modified timestamp on existing node."""
        query = f"""
        MATCH (n:{node_type})
        WHERE id(n) = $node_id
        SET n.last_modified = datetime()
        RETURN n
        """

        self.db.execute_command(
            "GRAPH.QUERY",
            self.n2_graph,
            query,
            f"node_id={node_id}"
        )


async def main():
    """Run the code substrate watcher."""
    logger.info("=" * 70)
    logger.info("CODE SUBSTRATE WATCHER - AUTO-NODE CREATION")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Watching directories:")
    for watch_dir in WATCH_DIRS:
        if watch_dir.exists():
            logger.info(f"  ✅ {watch_dir.relative_to(MIND_PROTOCOL_ROOT)}")
        else:
            logger.info(f"  ❌ {watch_dir.relative_to(MIND_PROTOCOL_ROOT)} (not found)")
    logger.info("")
    logger.info("Monitored file types:")
    logger.info("  - *.py   → Code nodes (Python)")
    logger.info("  - *.ts   → Code nodes (TypeScript)")
    logger.info("  - *.tsx  → Code nodes (TypeScript)")
    logger.info("  - *.md   → Documentation nodes")
    logger.info("")
    logger.info("Target graph: ecosystem (L3)")
    logger.info("")
    logger.info("Waiting for file changes...")
    logger.info("=" * 70)

    # Create event handler
    event_handler = CodeSubstrateHandler()

    # Create observer and schedule all watch directories
    observer = Observer()

    for watch_dir in WATCH_DIRS:
        if watch_dir.exists():
            observer.schedule(
                event_handler,
                str(watch_dir),
                recursive=True  # Watch subdirectories
            )

    # Start watching
    observer.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[CodeSubstrateWatcher] Shutting down...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    asyncio.run(main())
