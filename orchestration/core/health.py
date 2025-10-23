"""
Health check utilities for Mind Protocol services.

Provides standardized health check endpoints and probes.

Author: Ada (Architect)
Created: 2025-10-22
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class HealthStatus(Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    status: HealthStatus
    service_name: str
    timestamp: str
    uptime_seconds: float
    checks: Dict[str, bool]
    metrics: Dict[str, Any]
    message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["status"] = self.status.value
        return result


class HealthProbe:
    """Health probe for a service."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.start_time = time.time()
        self.checks: Dict[str, Callable[[], bool]] = {}
        self.metrics: Dict[str, Callable[[], Any]] = {}
        self.last_heartbeat: Optional[datetime] = None

    def add_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """
        Add a health check.

        Args:
            name: Name of the check
            check_func: Function that returns True if healthy, False otherwise
        """
        self.checks[name] = check_func

    def add_metric(self, name: str, metric_func: Callable[[], Any]) -> None:
        """
        Add a metric to include in health reports.

        Args:
            name: Metric name
            metric_func: Function that returns metric value
        """
        self.metrics[name] = metric_func

    def heartbeat(self) -> None:
        """Record a heartbeat."""
        self.last_heartbeat = datetime.utcnow()

    def check(self) -> HealthCheckResult:
        """
        Run all health checks.

        Returns:
            HealthCheckResult with status and details
        """
        # Run all checks
        check_results = {}
        for name, check_func in self.checks.items():
            try:
                check_results[name] = check_func()
            except Exception as e:
                check_results[name] = False

        # Gather metrics
        metric_values = {}
        for name, metric_func in self.metrics.items():
            try:
                metric_values[name] = metric_func()
            except Exception:
                metric_values[name] = None

        # Determine overall status
        all_passing = all(check_results.values()) if check_results else True

        if all_passing:
            # Check heartbeat if we're tracking it
            if self.last_heartbeat:
                age = datetime.utcnow() - self.last_heartbeat
                if age > timedelta(seconds=30):
                    status = HealthStatus.DEGRADED
                    message = f"No heartbeat for {age.total_seconds():.0f}s"
                else:
                    status = HealthStatus.HEALTHY
                    message = None
            else:
                status = HealthStatus.HEALTHY
                message = None
        else:
            failed_checks = [name for name, passed in check_results.items() if not passed]
            status = HealthStatus.UNHEALTHY
            message = f"Failed checks: {', '.join(failed_checks)}"

        return HealthCheckResult(
            status=status,
            service_name=self.service_name,
            timestamp=datetime.utcnow().isoformat() + "Z",
            uptime_seconds=time.time() - self.start_time,
            checks=check_results,
            metrics=metric_values,
            message=message,
        )


async def run_health_server(probe: HealthProbe, port: int = 8789) -> None:
    """
    Run a simple HTTP server for health checks.

    Args:
        probe: HealthProbe instance
        port: Port to listen on
    """
    from aiohttp import web

    async def health_handler(request):
        """Handle /healthz requests."""
        result = probe.check()

        if result.status == HealthStatus.HEALTHY:
            status_code = 200
        elif result.status == HealthStatus.DEGRADED:
            status_code = 200  # Still accepting traffic
        else:
            status_code = 503  # Service unavailable

        return web.json_response(result.to_dict(), status=status_code)

    app = web.Application()
    app.router.add_get("/healthz", health_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Keep running
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
