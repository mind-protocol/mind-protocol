"""
MPSv3 Centralized File Watcher - Single file watcher for all services.

Eliminates dual supervision race by having ONE file watcher in supervisor.
Uses watchdog library with debouncing to prevent rapid restarts.

Author: Atlas
Date: 2025-10-25
"""

import time
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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

        # Check if file matches watched patterns
        if not any(fnmatch.fnmatch(event.src_path, p) for p in self.patterns):
            return

        # Debounce rapid changes
        now = time.time()
        if now - self.last_trigger < self.debounce_time:
            return

        self.last_trigger = now
        print(f"[FileWatcher] {self.service_id}: {event.src_path} changed")
        self.callback(self.service_id, reason="file_change")


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

        self.observer.start()
        print("[FileWatcher] Started centralized watcher")

    def _handle_file_change(self, service_id: str, reason: str):
        """Trigger graceful reload of service."""
        print(f"[FileWatcher] Triggering reload: {service_id} ({reason})")
        self.registry.reload_service(service_id)

    def stop(self):
        self.observer.stop()
        self.observer.join()
