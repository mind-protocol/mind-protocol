"""
MPSv3 Service Registry - Service lifecycle management.

Coordinates:
- Service startup (start all, with dependency order in future)
- Service reload (graceful restart on file change)
- Service monitoring (track running state)
- Service shutdown (clean termination)

Author: Atlas
Date: 2025-10-25
"""

import yaml
from pathlib import Path
from typing import Dict

from .runner import ServiceRunner, ServiceSpec


class ServiceRegistry:
    """Service lifecycle management."""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.specs: Dict[str, ServiceSpec] = {}
        self.runners: Dict[str, ServiceRunner] = {}
        self._load_config()

    def _load_config(self):
        """Load service specifications from YAML."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        for service in config.get("services", []):
            spec = ServiceSpec(
                id=service["id"],
                cmd=service["cmd"],
                env=service.get("env", {}),
                cwd=service.get("cwd"),
                criticality=service.get("criticality", "CORE"),
                max_retries=service.get("max_retries", 3),
                watched_files=service.get("watched_files", [])
            )
            self.specs[spec.id] = spec
            self.runners[spec.id] = ServiceRunner(spec)

        print(f"[Registry] Loaded {len(self.specs)} service specifications")

    def start_all(self):
        """Start all services."""
        for service_id, runner in self.runners.items():
            print(f"[Registry] Starting {service_id}...")
            runner.start()

    def reload_service(self, service_id: str):
        """Gracefully reload a service (shutdown + restart)."""
        if service_id not in self.runners:
            print(f"[Registry] Unknown service: {service_id}")
            return

        runner = self.runners[service_id]
        print(f"[Registry] Reloading {service_id}...")
        runner.shutdown()
        runner.start()

    def shutdown_all(self):
        """Shutdown all services cleanly."""
        for service_id, runner in self.runners.items():
            print(f"[Registry] Shutting down {service_id}...")
            runner.shutdown()
