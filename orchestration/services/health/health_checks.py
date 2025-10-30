"""
Health Check System - Fail-Loud Observability

Implements startup self-tests and runtime health verification per SCRIPT_MAP.md
operational resilience requirements.

Author: Victor "The Resurrector"
Created: 2025-10-22
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import requests

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check result status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    service: str
    status: HealthStatus
    message: str
    latency_ms: float
    details: Optional[Dict] = None


class ServiceHealthChecker:
    """
    Comprehensive health checking for Mind Protocol services.

    Checks both infrastructure (port binding) AND functionality (endpoints respond).
    """

    def __init__(
        self,
        websocket_port: int = 8000,
        dashboard_port: int = 3000,
        api_port: int = 8788,
        timeout_seconds: float = 5.0
    ):
        self.websocket_port = websocket_port
        self.dashboard_port = dashboard_port
        self.api_port = api_port
        self.timeout = timeout_seconds

    def check_websocket_server(self) -> HealthCheckResult:
        """
        Check WebSocket server health.

        Verifies:
        1. Port bound
        2. HTTP endpoint responds
        3. Returns valid status
        """
        start_time = time.time()

        try:
            # Check if service responds (not just port bound)
            response = requests.get(
                f"http://localhost:{self.websocket_port}/health",
                timeout=self.timeout
            )

            latency_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()

                # Verify expected fields present
                if "status" in data and "engines" in data:
                    return HealthCheckResult(
                        service="websocket_server",
                        status=HealthStatus.HEALTHY,
                        message=f"Responding ({len(data.get('engines', []))} engines)",
                        latency_ms=latency_ms,
                        details=data
                    )
                else:
                    return HealthCheckResult(
                        service="websocket_server",
                        status=HealthStatus.DEGRADED,
                        message="Missing expected fields in response",
                        latency_ms=latency_ms,
                        details=data
                    )
            else:
                return HealthCheckResult(
                    service="websocket_server",
                    status=HealthStatus.UNHEALTHY,
                    message=f"HTTP {response.status_code}",
                    latency_ms=latency_ms
                )

        except requests.exceptions.ConnectionError:
            return HealthCheckResult(
                service="websocket_server",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection refused on port {self.websocket_port}",
                latency_ms=(time.time() - start_time) * 1000
            )
        except requests.exceptions.Timeout:
            return HealthCheckResult(
                service="websocket_server",
                status=HealthStatus.DEGRADED,
                message=f"Timeout after {self.timeout}s",
                latency_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return HealthCheckResult(
                service="websocket_server",
                status=HealthStatus.UNKNOWN,
                message=f"Error: {str(e)}",
                latency_ms=(time.time() - start_time) * 1000
            )

    def check_dashboard(self) -> HealthCheckResult:
        """
        Check Next.js dashboard health.

        Verifies:
        1. Port bound
        2. Returns HTML (not error page)
        3. Reasonable response time
        """
        start_time = time.time()

        try:
            response = requests.get(
                f"http://localhost:{self.dashboard_port}",
                timeout=self.timeout
            )

            latency_ms = (time.time() - start_time) * 1000

            # Check if we got HTML back (not just an error)
            content_type = response.headers.get('content-type', '')

            if response.status_code == 200 and 'html' in content_type:
                # Verify it's not the Next.js error page
                if "Internal Server Error" in response.text:
                    return HealthCheckResult(
                        service="dashboard",
                        status=HealthStatus.UNHEALTHY,
                        message="Returning Internal Server Error",
                        latency_ms=latency_ms
                    )

                return HealthCheckResult(
                    service="dashboard",
                    status=HealthStatus.HEALTHY,
                    message=f"Serving pages ({latency_ms:.0f}ms)",
                    latency_ms=latency_ms
                )
            else:
                return HealthCheckResult(
                    service="dashboard",
                    status=HealthStatus.DEGRADED,
                    message=f"HTTP {response.status_code}, {content_type}",
                    latency_ms=latency_ms
                )

        except requests.exceptions.ConnectionError:
            return HealthCheckResult(
                service="dashboard",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection refused on port {self.dashboard_port}",
                latency_ms=(time.time() - start_time) * 1000
            )
        except requests.exceptions.Timeout:
            return HealthCheckResult(
                service="dashboard",
                status=HealthStatus.DEGRADED,
                message=f"Timeout after {self.timeout}s",
                latency_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return HealthCheckResult(
                service="dashboard",
                status=HealthStatus.UNKNOWN,
                message=f"Error: {str(e)}",
                latency_ms=(time.time() - start_time) * 1000
            )

    def check_all_services(self) -> Dict[str, HealthCheckResult]:
        """Run health checks for all services."""
        return {
            "websocket_server": self.check_websocket_server(),
            "dashboard": self.check_dashboard(),
        }

    def get_overall_health(self) -> Tuple[HealthStatus, str]:
        """
        Get overall system health status.

        Returns:
            (status, summary_message)
        """
        results = self.check_all_services()

        # Count status types
        healthy = sum(1 for r in results.values() if r.status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in results.values() if r.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for r in results.values() if r.status == HealthStatus.UNHEALTHY)
        total = len(results)

        if unhealthy > 0:
            return (
                HealthStatus.UNHEALTHY,
                f"{unhealthy}/{total} services unhealthy"
            )
        elif degraded > 0:
            return (
                HealthStatus.DEGRADED,
                f"{degraded}/{total} services degraded"
            )
        elif healthy == total:
            return (
                HealthStatus.HEALTHY,
                f"All {total} services healthy"
            )
        else:
            return (
                HealthStatus.UNKNOWN,
                "Unable to determine health"
            )


class StartupSelfTests:
    """
    Fast (<2s) deterministic tests run before serving.

    Per SCRIPT_MAP.md requirements:
    - Conservation micrograph
    - Hub fan-out
    - Two-scale sanity
    - Decay half-life check

    TODO: Implement actual consciousness tests once Ada provides test scenarios.
    For now, implements infrastructure smoke tests.
    """

    @staticmethod
    def test_falkordb_connection() -> HealthCheckResult:
        """Verify FalkorDB is accessible."""
        start_time = time.time()

        try:
            from falkordb import FalkorDB

            db = FalkorDB(host='localhost', port=6379)
            # Try to access a graph (will fail if FalkorDB not running)
            db.select_graph("_test_health_check")

            latency_ms = (time.time() - start_time) * 1000

            return HealthCheckResult(
                service="falkordb",
                status=HealthStatus.HEALTHY,
                message=f"Connected ({latency_ms:.0f}ms)",
                latency_ms=latency_ms
            )

        except Exception as e:
            return HealthCheckResult(
                service="falkordb",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection failed: {str(e)}",
                latency_ms=(time.time() - start_time) * 1000
            )

    @staticmethod
    def test_settings_loaded() -> HealthCheckResult:
        """Verify core settings are loaded and valid."""
        start_time = time.time()

        try:
            from orchestration.core.settings import settings

            # Verify critical settings present
            assert settings.WS_PORT > 0, "WS_PORT not set"
            assert settings.API_PORT > 0, "API_PORT not set"
            assert settings.FALKORDB_HOST, "FALKORDB_HOST not set"

            latency_ms = (time.time() - start_time) * 1000

            return HealthCheckResult(
                service="settings",
                status=HealthStatus.HEALTHY,
                message="Core settings valid",
                latency_ms=latency_ms,
                details={
                    "ws_port": settings.WS_PORT,
                    "api_port": settings.API_PORT,
                    "falkordb_host": settings.FALKORDB_HOST
                }
            )

        except Exception as e:
            return HealthCheckResult(
                service="settings",
                status=HealthStatus.UNHEALTHY,
                message=f"Settings validation failed: {str(e)}",
                latency_ms=(time.time() - start_time) * 1000
            )

    @classmethod
    def run_all_tests(cls) -> Dict[str, HealthCheckResult]:
        """Run all startup self-tests."""
        return {
            "falkordb": cls.test_falkordb_connection(),
            "settings": cls.test_settings_loaded(),
        }

    @classmethod
    def all_tests_pass(cls) -> Tuple[bool, List[str]]:
        """
        Run all tests and return pass/fail with failures.

        Returns:
            (all_passed, failure_messages)
        """
        results = cls.run_all_tests()

        failures = []
        for name, result in results.items():
            if result.status != HealthStatus.HEALTHY:
                failures.append(f"{name}: {result.message}")

        return (len(failures) == 0, failures)


def create_health_check_summary() -> Dict:
    """
    Create comprehensive health check summary for monitoring.

    Returns dict suitable for JSON serialization.
    """
    checker = ServiceHealthChecker()
    service_results = checker.check_all_services()
    overall_status, overall_message = checker.get_overall_health()

    return {
        "timestamp": time.time(),
        "overall_status": overall_status.value,
        "overall_message": overall_message,
        "services": {
            name: {
                "status": result.status.value,
                "message": result.message,
                "latency_ms": result.latency_ms,
                "details": result.details
            }
            for name, result in service_results.items()
        }
    }
