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

import copy
import re
import threading
import time
import yaml
from pathlib import Path
from typing import Dict, Any

from .runner import ServiceRunner, ServiceSpec
from .health import ServiceHealthMonitor

# Quiescence window: refuse reload until service stable
DEFAULT_MIN_UPTIME = 25  # seconds - allows engines to initialize


class ServiceRegistry:
    """Service lifecycle management."""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.specs: Dict[str, ServiceSpec] = {}
        self.runners: Dict[str, ServiceRunner] = {}
        self.health_monitors: Dict[str, ServiceHealthMonitor] = {}  # Health monitoring
        self._timers: Dict[str, threading.Timer] = {}  # Deferred reload timers
        self._load_config()

    def _expand_vars(self, value: Any, env_vars: Dict[str, str]) -> Any:
        """Recursively expand ${VAR} references in config values."""
        if isinstance(value, str):
            def replacer(match):
                var_name = match.group(1)
                return env_vars.get(var_name, match.group(0))
            return re.sub(r'\$\{([^}]+)\}', replacer, value)
        elif isinstance(value, dict):
            return {k: self._expand_vars(v, env_vars) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._expand_vars(item, env_vars) for item in value]
        else:
            return value

    def _apply_template(self, value: Any, params: Dict[str, Any]) -> Any:
        """Recursively substitute {{placeholder}} tokens using params."""
        if isinstance(value, str):
            pattern = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")

            def replacer(match):
                key = match.group(1)
                if key not in params:
                    raise KeyError(f"Missing template variable '{key}' for service template")
                return str(params[key])

            return pattern.sub(replacer, value)
        elif isinstance(value, dict):
            return {
                (self._apply_template(k, params) if isinstance(k, str) else k): self._apply_template(v, params)
                for k, v in value.items()
            }
        elif isinstance(value, list):
            return [self._apply_template(item, params) for item in value]
        else:
            return value

    def _expand_templated_services(self, config: Dict[str, Any]) -> list:
        """Expand service groups defined via template/items pattern."""
        expanded = []
        for group_name, group_cfg in config.items():
            if group_name in {"env", "services"}:
                continue

            if not isinstance(group_cfg, dict):
                continue

            template = group_cfg.get("template")
            items = group_cfg.get("items")
            if template is None or items is None:
                continue

            for index, item in enumerate(items or []):
                if not isinstance(item, dict):
                    raise ValueError(f"Invalid item in '{group_name}' template list: {item!r}")

                context = {**item, "group": group_name, "index": index}
                template_copy = copy.deepcopy(template)
                service_spec = self._apply_template(template_copy, context)

                if "id" not in service_spec or not service_spec["id"]:
                    base = context.get("id") or f"{group_name}_{index}"
                    service_spec["id"] = str(base)

                expanded.append(service_spec)

        return expanded

    def _load_config(self):
        """Load service specifications from YAML."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        # Load top-level environment variables for expansion
        global_env = config.get("env", {})

        all_services = list(config.get("services", []))
        all_services.extend(self._expand_templated_services(config))

        for service in all_services:
            # Parse watch configuration (paths to watch for file changes)
            watch_config = service.get("watch", {})
            watched_files = watch_config.get("paths", [])

            spec = ServiceSpec(
                id=service["id"],
                cmd=service["cmd"],
                env=self._expand_vars(service.get("env", {}), global_env),
                cwd=service.get("cwd"),
                criticality=service.get("criticality", "CORE"),
                max_retries=service.get("max_retries", 3),
                watched_files=watched_files,
                depends_on=service.get("depends_on", [])
            )
            self.specs[spec.id] = spec
            self.runners[spec.id] = ServiceRunner(spec)

            # Create health monitor if readiness/liveness checks defined
            readiness_check = self._expand_vars(service.get("readiness"), global_env)
            liveness_check = self._expand_vars(service.get("liveness"), global_env)
            if readiness_check or liveness_check:
                self.health_monitors[spec.id] = ServiceHealthMonitor(
                    service_id=spec.id,
                    readiness_check=readiness_check,
                    liveness_check=liveness_check
                )

        print(f"[Registry] Loaded {len(self.specs)} service specifications")

    def start_all(self):
        """Start all services."""
        for service_id, runner in self.runners.items():
            print(f"[Registry] Starting {service_id}...")
            runner.start()

    def reload_service(self, service_id: str):
        """Gracefully reload a service with quiescence window.
        
        Defers reload if service is within min_uptime window to prevent
        restart loops during initialization (e.g., engines loading).
        """
        runner = self.runners.get(service_id)
        if not runner:
            print(f"[Registry] Unknown service: {service_id}")
            return

        # Get quiescence window (default 25s for engine initialization)
        min_uptime = getattr(runner.spec, 'min_uptime_before_reload', DEFAULT_MIN_UPTIME)
        uptime = runner.uptime()

        # Check if service is within quiescence window
        if uptime < min_uptime:
            delay = max(1, int(min_uptime - uptime))
            print(f"[Registry] {service_id}: deferring reload {delay}s "
                  f"(uptime {uptime:.1f}s < {min_uptime}s quiescence)")
            
            # Coalesce multiple triggers by using single timer per service
            timer_key = f"{service_id}::reload_timer"
            
            # Cancel existing timer if present
            if timer_key in self._timers and self._timers[timer_key] is not None:
                self._timers[timer_key].cancel()
            
            # Schedule deferred reload
            def deferred_reload():
                print(f"[Registry] Quiescence complete, reloading {service_id}...")
                runner.shutdown()
                runner.start()
                self._timers[timer_key] = None
            
            self._timers[timer_key] = threading.Timer(delay, deferred_reload)
            self._timers[timer_key].start()
            return

        # Service past quiescence window - reload immediately
        print(f"[Registry] Reloading {service_id} (uptime {uptime:.1f}s)...")
        runner.shutdown()
        runner.start()

    def wait_for_readiness(self, overall_timeout_s: float = 60.0):
        """
        Wait for all services with readiness checks to become ready.

        Args:
            overall_timeout_s: Maximum time to wait for ALL services (default 60s)
        """
        import time
        print("[Registry] Waiting for services to become ready...")
        start_time = time.time()

        for service_id, monitor in self.health_monitors.items():
            # Check overall timeout
            elapsed = time.time() - start_time
            if elapsed >= overall_timeout_s:
                print(f"[Registry] ⚠️ Overall readiness timeout ({overall_timeout_s}s) exceeded - proceeding anyway")
                break

            if not monitor.readiness_check:
                continue  # No readiness check defined

            # Check if process is still alive before waiting
            runner = self.runners.get(service_id)
            if runner and runner.process and runner.process.poll() is not None:
                print(f"[Registry] ⚠️ {service_id} process died - skipping readiness check")
                continue

            remaining = overall_timeout_s - elapsed
            max_attempts = min(30, int(remaining))  # Don't exceed remaining time

            ready = monitor.check_readiness(max_attempts=max_attempts, interval_s=1.0)
            if not ready:
                print(f"[Registry] WARNING: {service_id} failed readiness check")

    def check_all_health(self) -> Dict[str, bool]:
        """
        Check health of all monitored services.

        Returns dict mapping service_id -> is_healthy.
        """
        health_status = {}
        for service_id, monitor in self.health_monitors.items():
            runner = self.runners.get(service_id)

            # Check if process is dead - RESURRECT IMMEDIATELY
            if not runner or not runner.process or runner.process.poll() is not None:
                print(f"[Registry] {service_id} process died - resurrecting...")
                health_status[service_id] = False

                # Restart dead process
                if runner:
                    runner.shutdown()  # Clean up any remnants
                    runner.start()

                    # Wait for readiness after resurrection
                    if monitor.readiness_check:
                        monitor.is_ready = False
                        monitor.consecutive_failures = 0
                        ready = monitor.check_readiness(max_attempts=30, interval_s=1.0)
                        health_status[service_id] = ready
                    else:
                        health_status[service_id] = True  # Assume healthy if no readiness check
                continue

            # Check liveness for running processes
            is_healthy = monitor.check_liveness()
            health_status[service_id] = is_healthy

            # Restart if exceeded failure threshold (3 consecutive liveness failures)
            if monitor.should_restart(failure_threshold=3):
                print(f"[Registry] {service_id} exceeded health failure threshold, restarting...")
                runner.shutdown()
                runner.start()

                # Wait for readiness after restart
                if monitor.readiness_check:
                    monitor.is_ready = False
                    monitor.consecutive_failures = 0
                    ready = monitor.check_readiness(max_attempts=30, interval_s=1.0)
                    health_status[service_id] = ready

        return health_status

    def shutdown_all(self):
        """Shutdown all services cleanly."""
        for service_id, runner in self.runners.items():
            print(f"[Registry] Shutting down {service_id}...")
            runner.shutdown()
