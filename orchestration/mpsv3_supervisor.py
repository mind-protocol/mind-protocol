#!/usr/bin/env python3
"""
MPSv3 Supervisor - Centralized Process Management

Replaces guardian.py + launcher.py with single supervisor that:
- Acquires OS-level singleton lease (no stale locks)
- Manages all services via process groups
- Provides centralized file watching (no dual supervision)
- Implements exponential backoff with quarantine
- Handles clean shutdown on SIGTERM/SIGINT

Usage:
    python orchestration/mpsv3_supervisor.py [--config path/to/services.yaml]

Author: Atlas
Date: 2025-10-25
Phase: Phase 1 Implementation
"""

import argparse
import signal
import sys
import time
from pathlib import Path

# Add orchestration to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.services.mpsv3.singleton import SingletonLease
from orchestration.services.mpsv3.registry import ServiceRegistry
from orchestration.services.mpsv3.watcher import CentralizedFileWatcher
from orchestration.services.mpsv3.portguard import PortGuard, kill_port_owners_aggressive


class MPSv3Supervisor:
    """Main supervisor process."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.lease = None
        self.registry = None
        self.watcher = None
        self.running = False

    def start(self):
        """Start supervisor and all services."""
        print("[MPSv3] Starting Mind Protocol Supervisor v3...")

        # PRE-FLIGHT CLEANUP - Kill zombie services BEFORE attempting mutex
        # This resolves the catch-22: zombie processes from crashed supervisors
        # can hold ports/resources, blocking startup. By cleaning BEFORE mutex
        # acquisition, we ensure a clean slate even if previous supervisor crashed.
        print("[MPSv3] Phase 1: Pre-flight cleanup (killing zombie services)...")
        pg = PortGuard()
        ports = [3000, 8000, 8001, 8002, 8010, 6379]
        kill_port_owners_aggressive(ports, timeout_s=10, also_node=True)
        print("[MPSv3] Pre-flight cleanup complete.")

        # Acquire singleton lease
        self.lease = SingletonLease("MPSv3_Supervisor")
        if not self.lease.acquire():
            print("[MPSv3] Another supervisor is already running. Exiting.")
            sys.exit(1)

        # Load service registry
        print(f"[MPSv3] Loading services from {self.config_path}...")
        self.registry = ServiceRegistry(self.config_path)

        # RUNTIME CLEANUP - Additional verification after mutex acquired
        # This is redundant if pre-flight worked, but provides defense-in-depth
        print("[MPSv3] Phase 2: Runtime port verification...")
        ports = pg.ports_from_services_yaml(self.config_path) or [3000, 8000, 8001, 8002, 8010, 6379]
        kill_port_owners_aggressive(ports, timeout_s=5, also_node=False)
        print("[MPSv3] Runtime verification complete.")

        # Start all services
        print("[MPSv3] Starting all services...")
        self.registry.start_all()

        # Start file watcher
        print("[MPSv3] Starting file watcher...")
        self.watcher = CentralizedFileWatcher(self.registry)
        self.watcher.start()

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.running = True
        print("[MPSv3] Supervisor running. Press Ctrl+C to stop.")

        # Main loop (monitor services)
        try:
            while self.running:
                time.sleep(1)
                # TODO: Add health checks and service monitoring here
        except KeyboardInterrupt:
            pass

    def _signal_handler(self, signum, frame):
        """Handle SIGTERM/SIGINT gracefully."""
        print(f"\n[MPSv3] Received signal {signum}, shutting down...")
        self.running = False
        self.stop()

    def stop(self):
        """Stop all services and release lease."""
        print("[MPSv3] Stopping file watcher...")
        if self.watcher:
            self.watcher.stop()

        print("[MPSv3] Shutting down all services...")
        if self.registry:
            self.registry.shutdown_all()

        print("[MPSv3] Releasing singleton lease...")
        if self.lease:
            self.lease.release()

        print("[MPSv3] Supervisor stopped.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MPSv3 Supervisor - Mind Protocol Process Management")
    parser.add_argument(
        "--config",
        default="orchestration/services/mpsv3/services_simple.yaml",
        help="Path to services.yaml configuration file"
    )
    args = parser.parse_args()

    # Verify config exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[MPSv3] ERROR: Config file not found: {config_path}")
        sys.exit(1)

    # Start supervisor
    supervisor = MPSv3Supervisor(str(config_path))
    try:
        supervisor.start()
    except Exception as e:
        print(f"[MPSv3] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        supervisor.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
