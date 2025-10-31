#!/usr/bin/env python3
"""
File Watcher - Membrane-Native Code Review Trigger

Monitors local file changes and emits membrane events for review pipeline.

Events emitted:
  - code.diff.emit (inject) - Contains file diffs
  - review.request (inject) - Triggers lint adapters

Design:
  - Debounces 250-400ms to batch rapid edits
  - Batches 2s to group related changes
  - Ignores vendor/build/node_modules
  - Emits failure.emit on errors (fail-loud)
  - Backpressure: exponential backoff on bus errors

Author: Atlas "Infrastructure Engineer"
Created: 2025-10-31
Spec: docs/L4-law/membrane_native_reviewer_and_lint_system.md § 5.1
"""

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
except ImportError:
    Observer = None
    FileSystemEventHandler = None
    FileSystemEvent = None

from orchestration.adapters.watchers.normalize_diff import (
    normalize_diff_batch,
    serialize_diff
)

logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Represents a file change event."""
    path: str
    event_type: str  # "created", "modified", "deleted"
    timestamp: float
    sha_before: Optional[str] = None
    sha_after: Optional[str] = None


@dataclass
class ChangeBuffer:
    """Buffers and batches file changes."""
    changes: Dict[str, FileChange] = field(default_factory=dict)
    last_activity: float = field(default_factory=time.time)
    debounce_ms: int = 300  # Debounce rapid edits
    batch_ms: int = 2000    # Batch related changes


# Directories to ignore
IGNORE_PATTERNS = [
    "__pycache__",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "build",
    "dist",
    ".next",
    "vendor",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".coverage",
    "*.egg-info",
]


def should_ignore(path: Path) -> bool:
    """Check if path should be ignored."""
    path_str = str(path)

    # Check ignore patterns
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True

    # Only watch Python and TypeScript/JavaScript files
    if not path.suffix in [".py", ".ts", ".tsx", ".js", ".jsx"]:
        return True

    return False


def compute_file_hash(file_path: Path) -> Optional[str]:
    """Compute SHA256 hash of file content."""
    try:
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]
    except Exception:
        return None


class FileWatcherHandler(FileSystemEventHandler):
    """Handles file system events and buffers changes."""

    def __init__(self, buffer: ChangeBuffer, root_path: Path):
        self.buffer = buffer
        self.root_path = root_path
        self.lock = asyncio.Lock()

    def on_any_event(self, event: FileSystemEvent):
        """Handle any file system event."""
        if event.is_directory:
            return

        path = Path(event.src_path)

        # Ignore patterns
        if should_ignore(path):
            return

        # Determine event type
        if event.event_type == "created":
            event_type = "created"
        elif event.event_type == "modified":
            event_type = "modified"
        elif event.event_type == "deleted":
            event_type = "deleted"
        else:
            return

        # Get relative path
        try:
            rel_path = str(path.relative_to(self.root_path))
        except ValueError:
            rel_path = str(path)

        # Compute hash (for non-deleted files)
        sha_after = None if event_type == "deleted" else compute_file_hash(path)

        # Buffer the change
        change = FileChange(
            path=rel_path,
            event_type=event_type,
            timestamp=time.time(),
            sha_after=sha_after
        )

        self.buffer.changes[rel_path] = change
        self.buffer.last_activity = time.time()

        logger.debug(f"[FileWatcher] Buffered {event_type}: {rel_path}")


class FileWatcher:
    """
    File watcher that emits membrane events for code review.

    Usage:
        watcher = FileWatcher(
            root_path=Path("/home/user/repo"),
            broadcaster=broadcaster,
            org_id="mind-protocol",
            ecosystem_id="prod"
        )
        await watcher.start()
    """

    def __init__(
        self,
        root_path: Path,
        broadcaster,
        org_id: str,
        ecosystem_id: str = "prod",
        debounce_ms: int = 300,
        batch_ms: int = 2000
    ):
        self.root_path = root_path
        self.broadcaster = broadcaster
        self.org_id = org_id
        self.ecosystem_id = ecosystem_id

        self.buffer = ChangeBuffer(debounce_ms=debounce_ms, batch_ms=batch_ms)
        self.observer = None
        self.handler = None
        self.running = False

        # Backpressure state
        self.emit_failures = 0
        self.backoff_until = 0.0

    async def start(self):
        """Start watching for file changes."""
        if Observer is None:
            logger.error("[FileWatcher] watchdog not installed, cannot watch files")
            await self._emit_failure(
                code_location="file_watcher.py:start",
                exception="ImportError: watchdog not installed",
                severity="error",
                suggestion="Install watchdog: pip install watchdog"
            )
            return

        if not self.root_path.exists():
            logger.error(f"[FileWatcher] Root path does not exist: {self.root_path}")
            await self._emit_failure(
                code_location="file_watcher.py:start",
                exception=f"FileNotFoundError: {self.root_path}",
                severity="error",
                suggestion="Check root_path configuration"
            )
            return

        self.running = True

        # Start watchdog observer
        self.handler = FileWatcherHandler(self.buffer, self.root_path)
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.root_path), recursive=True)
        self.observer.start()

        logger.info(f"[FileWatcher] Started watching {self.root_path}")

        # Start emission loop
        asyncio.create_task(self._emission_loop())

    async def stop(self):
        """Stop watching for file changes."""
        self.running = False

        if self.observer:
            self.observer.stop()
            self.observer.join()

        logger.info("[FileWatcher] Stopped")

    async def _emission_loop(self):
        """Main loop that emits batched changes."""
        while self.running:
            try:
                await asyncio.sleep(0.1)  # Check every 100ms

                # Check if we're in backoff
                if time.time() < self.backoff_until:
                    continue

                # Check if we have buffered changes
                if not self.buffer.changes:
                    continue

                # Check if debounce period has passed
                time_since_activity = time.time() - self.buffer.last_activity
                if time_since_activity < (self.buffer.debounce_ms / 1000.0):
                    continue

                # Emit batched changes
                await self._emit_batch()

            except Exception as exc:
                logger.error(f"[FileWatcher] Emission loop error: {exc}", exc_info=True)
                await self._emit_failure(
                    code_location="file_watcher.py:_emission_loop",
                    exception=str(exc),
                    severity="error"
                )

    async def _emit_batch(self):
        """Emit a batch of buffered changes."""
        if not self.buffer.changes:
            return

        # Take snapshot of current changes
        changes = list(self.buffer.changes.values())
        self.buffer.changes.clear()

        # Generate change_id
        change_id = f"local:{int(time.time())}"

        # Normalize changes into structured diffs with hunks
        # Convert FileChange objects to dicts for normalize_diff_batch
        change_dicts = [
            {
                "path": change.path,
                "event_type": change.event_type,
                "sha_after": change.sha_after
            }
            for change in changes
        ]

        # Generate diffs with hunks
        diffs = normalize_diff_batch(
            root_path=self.root_path,
            file_changes=change_dicts,
            store_old_content=False  # MVP: hash-only diffs for now
        )

        # Serialize diffs for event emission
        files = [serialize_diff(diff) for diff in diffs]

        logger.info(f"[FileWatcher] Emitting batch: {len(files)} files, change_id={change_id}")

        # Emit code.diff.emit
        try:
            await self.broadcaster.broadcast_event("code.diff.emit", {
                "change_id": change_id,
                "files": files,
                "org_id": self.org_id,
                "ecosystem_id": self.ecosystem_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            # Reset backoff on success
            self.emit_failures = 0

        except Exception as exc:
            logger.error(f"[FileWatcher] Failed to emit code.diff.emit: {exc}")
            await self._handle_emit_failure()
            await self._emit_failure(
                code_location="file_watcher.py:_emit_batch",
                exception=str(exc),
                severity="warn",
                change_id=change_id
            )
            return

        # Emit review.request
        try:
            await self.broadcaster.broadcast_event("review.request", {
                "change_id": change_id,
                "origin": "watcher",
                "org_id": self.org_id,
                "policies": "org:current",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        except Exception as exc:
            logger.error(f"[FileWatcher] Failed to emit review.request: {exc}")
            await self._handle_emit_failure()
            await self._emit_failure(
                code_location="file_watcher.py:_emit_batch",
                exception=str(exc),
                severity="warn",
                change_id=change_id
            )

    async def _handle_emit_failure(self):
        """Handle emission failure with exponential backoff."""
        self.emit_failures += 1

        # Exponential backoff: 1s, 2s, 4s, 8s, max 16s
        backoff_seconds = min(2 ** self.emit_failures, 16)
        self.backoff_until = time.time() + backoff_seconds

        logger.warning(f"[FileWatcher] Backoff {backoff_seconds}s after {self.emit_failures} failures")

    async def _emit_failure(
        self,
        code_location: str,
        exception: str,
        severity: str = "error",
        suggestion: str = "",
        change_id: Optional[str] = None
    ):
        """Emit failure.emit event (fail-loud requirement)."""
        try:
            await self.broadcaster.broadcast_event("failure.emit", {
                "code_location": code_location,
                "exception": exception,
                "severity": severity,
                "suggestion": suggestion,
                "change_id": change_id,
                "component": "file_watcher",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception as emit_exc:
            # Last resort: log to stderr
            logger.critical(
                f"[FileWatcher] CRITICAL: Failed to emit failure.emit: {emit_exc}",
                exc_info=True
            )


async def main():
    """Test file watcher."""
    from orchestration.libs.safe_broadcaster import SafeBroadcaster

    broadcaster = SafeBroadcaster()

    watcher = FileWatcher(
        root_path=Path.cwd(),
        broadcaster=broadcaster,
        org_id="mind-protocol",
        ecosystem_id="dev"
    )

    await watcher.start()

    try:
        # Run for 60 seconds
        await asyncio.sleep(60)
    finally:
        await watcher.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
