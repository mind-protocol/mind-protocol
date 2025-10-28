"""
MPSv3 Centralized File Watcher - Single file watcher for all services.

Eliminates dual supervision race by having ONE file watcher in supervisor.
Uses watchdog library with debouncing to prevent rapid restarts.

Author: Atlas
Date: 2025-10-25
"""

import time
import sys
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# File patterns to ignore (reduce noise from editors, bytecode, temps)
IGNORE_PATHS = ('__pycache__', '.git', '.idea', '.vscode', 'node_modules', '.next')
IGNORE_EXTENSIONS = ('.pyc', '.pyo', '.swp', '.tmp', '~', '.log')


class ServiceFileHandler(FileSystemEventHandler):
    """Watches files for a specific service and triggers reload."""

    def __init__(self, service_id: str, patterns: list, callback):
        self.service_id = service_id
        self.patterns = patterns
        self.callback = callback
        self.debounce_time = 2.0  # seconds
        self.last_trigger = 0

    def on_modified(self, event):
        if event.is_directory:
            return

        # Ignore noisy files (editor temps, bytecode, logs)
        if any(p in event.src_path for p in IGNORE_PATHS):
            return
        if event.src_path.lower().endswith(IGNORE_EXTENSIONS):
            return

        # Normalize path separators for consistent matching
        normalized_path = event.src_path.replace('', '/')

        # Check if file matches watched patterns
        # Support both glob patterns AND directory prefixes
        def matches_pattern(path, pattern):
            # Try fnmatch first (for glob patterns like *.py)
            if fnmatch.fnmatch(path, pattern):
                return True
            # Fallback to startswith for directory patterns
            if path.startswith(pattern):
                return True
            # Also try with trailing slash for directory patterns
            if path.startswith(pattern + '/'):
                return True
            return False

        if not any(matches_pattern(normalized_path, p) for p in self.patterns):
            return

        # Debounce rapid changes
        now = time.time()
        if now - self.last_trigger < self.debounce_time:
            return

        self.last_trigger = now
        print(f'[FileWatcher] {self.service_id}: matched {event.src_path}')
        self.callback(self.service_id, reason='file_change')


class CentralizedFileWatcher:
    """Single file watcher for all services."""

    def __init__(self, registry):
        self.registry = registry
        self.observer = Observer()

    def start(self):
        """Watch all service file patterns."""
        for spec in self.registry.specs.values():
            if not spec.watched_files:
                continue

            handler = ServiceFileHandler(
                service_id=spec.id,
                patterns=spec.watched_files,
                callback=self._handle_file_change
            )

            # Watch workspace root
            self.observer.schedule(handler, path=".", recursive=True)
            # DIAGNOSTIC: show what patterns this service watches
            print(f"[FileWatcher] Watching {spec.id}: {spec.watched_files}")

        self.observer.start()
        print("[FileWatcher] Started centralized watcher")

    def _handle_file_change(self, service_id: str, reason: str):
        """Trigger graceful reload of service."""
        print(f"[FileWatcher] Triggering reload: {service_id} ({reason})")
        self.registry.reload_service(service_id)

    def stop(self):
        self.observer.stop()
        self.observer.join()
