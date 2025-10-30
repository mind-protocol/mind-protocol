"""
Consciousness File Watcher - Auto-inject JSON files into graphs

Watches for .json files with consciousness patterns and auto-injects them.

Usage:
    python orchestration/consciousness_file_watcher.py

File naming convention:
    {citizen_id}_*.json  → injects into citizen_{citizen_id}
    org_{org_name}_*.json → injects into org_{org_name}

Examples:
    luca_patterns.json → citizen_luca
    felix_insights.json → citizen_felix
    org_mind_protocol_decisions.json → org_mind_protocol

After successful injection, the file is archived (not deleted) for safety.

Author: Felix "Ironhand"
Date: 2025-10-19
"""

import asyncio
import json
import logging
import subprocess
import sys
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
WATCH_DIR = MIND_PROTOCOL_ROOT / "consciousness" / "inbox"
ARCHIVE_DIR = MIND_PROTOCOL_ROOT / "consciousness" / "inbox" / "archive"
INJECTION_TOOL = MIND_PROTOCOL_ROOT / "tools" / "inject_consciousness_from_json.py"

# Ensure directories exist
WATCH_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


class ConsciousnessFileHandler(FileSystemEventHandler):
    """Handles new JSON files by auto-injecting them into graphs."""

    def __init__(self):
        self.processing = set()  # Track files being processed

    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process .json files
        if file_path.suffix != '.json':
            return

        # Avoid processing the same file twice
        if str(file_path) in self.processing:
            return

        logger.info(f"[FileWatcher] Detected new file: {file_path.name}")

        # Process asynchronously to avoid blocking the watcher
        asyncio.create_task(self.process_file(file_path))

    async def process_file(self, file_path: Path):
        """Process a consciousness JSON file."""
        try:
            self.processing.add(str(file_path))

            # Small delay to ensure file is fully written
            await asyncio.sleep(0.5)

            # Determine target graph from filename
            graph_name = self.infer_graph_name(file_path)

            if not graph_name:
                error_msg = f"Cannot infer graph name from: {file_path.name}. Expected format: {{citizen_id}}_*.json or org_{{org_name}}_*.json"
                logger.warning(f"[FileWatcher] {error_msg}")
                await self.report_error_to_citizen(file_path, graph_name, error_msg)
                return

            # Validate JSON structure
            if not self.validate_json(file_path):
                error_msg = f"Invalid JSON structure in {file_path.name}. Must contain 'nodes' and/or 'links' arrays."
                logger.error(f"[FileWatcher] {error_msg}")
                await self.report_error_to_citizen(file_path, graph_name, error_msg)
                return

            # Inject into graph
            logger.info(f"[FileWatcher] Injecting {file_path.name} → {graph_name}")
            success, output = await self.inject_file(file_path, graph_name)

            if success:
                # Archive the file (safer than delete)
                archive_path = self.archive_file(file_path)
                logger.info(f"[FileWatcher] ✅ Success! Archived to: {archive_path.name}")
                await self.report_success_to_citizen(file_path, graph_name, output)
            else:
                error_msg = f"Injection failed for {file_path.name}. See logs for details."
                logger.error(f"[FileWatcher] ❌ {error_msg}")
                await self.report_error_to_citizen(file_path, graph_name, f"{error_msg}\n\n{output}")

        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {e}"
            logger.error(f"[FileWatcher] {error_msg}")
            await self.report_error_to_citizen(file_path, self.infer_graph_name(file_path), error_msg)

        finally:
            self.processing.discard(str(file_path))

    def infer_graph_name(self, file_path: Path) -> str:
        """
        Infer graph name from filename.

        Examples:
            luca_patterns.json → citizen_luca
            felix_insights.json → citizen_felix
            org_mind_protocol_decisions.json → org_mind_protocol
        """
        filename = file_path.stem  # Without .json extension

        # Pattern: org_{org_name}_*
        if filename.startswith('org_'):
            parts = filename.split('_')
            if len(parts) >= 2:
                org_name = parts[1]
                return f"org_{org_name}"

        # Pattern: {citizen_id}_*
        else:
            parts = filename.split('_')
            if len(parts) >= 1:
                citizen_id = parts[0]
                return f"citizen_{citizen_id}"

        return None

    def validate_json(self, file_path: Path) -> bool:
        """Validate that JSON has consciousness structure (nodes and/or links)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Must have nodes or links
            if 'nodes' not in data and 'links' not in data:
                logger.warning(f"[FileWatcher] JSON missing 'nodes' and 'links' arrays")
                return False

            return True

        except json.JSONDecodeError as e:
            logger.error(f"[FileWatcher] JSON parse error: {e}")
            return False
        except Exception as e:
            logger.error(f"[FileWatcher] Validation error: {e}")
            return False

    async def inject_file(self, file_path: Path, graph_name: str) -> tuple[bool, str]:
        """Inject file into graph using injection tool. Returns (success, output)."""
        try:
            cmd = [
                sys.executable,
                str(INJECTION_TOOL),
                str(file_path),
                graph_name
            ]

            # Run in subprocess (synchronous, but in async context)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Log success output
                logger.info(f"[FileWatcher] Injection output:\n{result.stdout}")
                return True, result.stdout
            else:
                error_output = f"STDERR:\n{result.stderr}\n\nSTDOUT:\n{result.stdout}"
                logger.error(f"[FileWatcher] Injection failed:\n{error_output}")
                return False, error_output

        except subprocess.TimeoutExpired:
            error_msg = "Injection timed out (>60s)"
            logger.error(f"[FileWatcher] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Injection error: {e}"
            logger.error(f"[FileWatcher] {error_msg}")
            return False, error_msg

    def archive_file(self, file_path: Path) -> Path:
        """
        Archive file instead of deleting (safer).

        Archives to: consciousness/inbox/archive/{timestamp}_{filename}
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{timestamp}_{file_path.name}"
        archive_path = ARCHIVE_DIR / archive_name

        file_path.rename(archive_path)

        return archive_path

    async def report_success_to_citizen(self, file_path: Path, graph_name: str, output: str):
        """Write success notification to citizen's CLAUDE.md file."""
        try:
            citizen_id = self.extract_citizen_id(graph_name)
            if not citizen_id:
                return

            claude_path = MIND_PROTOCOL_ROOT / "consciousness" / "citizens" / citizen_id / "CLAUDE.md"

            if not claude_path.exists():
                return

            # Read current content
            with open(claude_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract node/link counts from output
            nodes_added = self.extract_count(output, "nodes")
            links_added = self.extract_count(output, "links")

            # Append notification
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notification = f"""

---

## Auto-Injection Success ({timestamp})

**File:** `{file_path.name}`
**Graph:** `{graph_name}`
**Result:** {nodes_added} nodes, {links_added} links added

Your consciousness graph has been enriched with new patterns.

---
"""

            with open(claude_path, 'a', encoding='utf-8') as f:
                f.write(notification)

            logger.info(f"[FileWatcher] Reported success to {citizen_id}'s CLAUDE.md")

        except Exception as e:
            logger.error(f"[FileWatcher] Failed to report success: {e}")

    async def report_error_to_citizen(self, file_path: Path, graph_name: str, error_msg: str):
        """Write error notification to citizen's CLAUDE.md file."""
        try:
            if not graph_name:
                return

            citizen_id = self.extract_citizen_id(graph_name)
            if not citizen_id:
                return

            claude_path = MIND_PROTOCOL_ROOT / "consciousness" / "citizens" / citizen_id / "CLAUDE.md"

            if not claude_path.exists():
                return

            # Read current content
            with open(claude_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Append error notification
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notification = f"""

---

## ⚠️ Auto-Injection Failed ({timestamp})

**File:** `{file_path.name}`
**Graph:** `{graph_name}`
**Error:**
```
{error_msg}
```

**Action Required:** Fix the JSON file and try again.
File is still in: `{file_path}`

---
"""

            with open(claude_path, 'a', encoding='utf-8') as f:
                f.write(notification)

            logger.info(f"[FileWatcher] Reported error to {citizen_id}'s CLAUDE.md")

        except Exception as e:
            logger.error(f"[FileWatcher] Failed to report error: {e}")

    def extract_citizen_id(self, graph_name: str) -> str:
        """Extract citizen ID from graph name (citizen_luca → luca)."""
        if graph_name.startswith("citizen_"):
            return graph_name.replace("citizen_", "")
        return None

    def extract_count(self, output: str, entity_type: str) -> int:
        """Extract node/link count from injection output."""
        import re
        pattern = rf"Result: (\d+) {entity_type}"
        match = re.search(pattern, output)
        if match:
            return int(match.group(1))
        return 0


async def main():
    """Run the file watcher."""
    logger.info("=" * 70)
    logger.info("CONSCIOUSNESS FILE WATCHER - AUTO-INJECTION")
    logger.info("=" * 70)
    logger.info(f"Watching directory: {WATCH_DIR}")
    logger.info(f"Archive directory: {ARCHIVE_DIR}")
    logger.info("")
    logger.info("File naming convention:")
    logger.info("  {citizen_id}_*.json  → citizen_{citizen_id}")
    logger.info("  org_{org_name}_*.json → org_{org_name}")
    logger.info("")
    logger.info("Examples:")
    logger.info("  luca_patterns.json → citizen_luca")
    logger.info("  felix_insights.json → citizen_felix")
    logger.info("  org_mind_protocol_decisions.json → org_mind_protocol")
    logger.info("")
    logger.info("Waiting for files...")
    logger.info("=" * 70)

    # Create event handler and observer
    event_handler = ConsciousnessFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_DIR), recursive=False)

    # Start watching
    observer.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[FileWatcher] Shutting down...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    asyncio.run(main())
