"""
First-Hour Diagnostic Runbook (Automated)

When "nothing is working", run this script to systematically diagnose the system.

Per SCRIPT_MAP.md operational resilience requirements:
1. Health endpoints check
2. Event heartbeat verification
3. Conservation check
4. Frontier diagnostic
5. Entity boundary check
6. Learning freeze detection

Usage:
    python orchestration/scripts/diagnose_system.py

Returns:
    Exit code 0 if all checks pass
    Exit code 1 if any check fails

Author: Victor "The Resurrector"
Created: 2025-10-22
"""

import sys
import logging
import time
import requests
from typing import Dict, List, Tuple

# Add parent to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestration.services.health import (
    ServiceHealthChecker,
    StartupSelfTests,
    HealthStatus
)
from orchestration.core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DIAGNOSIS - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemDiagnostic:
    """Systematic system diagnosis per runbook."""

    def __init__(self):
        self.health_checker = ServiceHealthChecker(
            websocket_port=settings.WS_PORT,
            dashboard_port=3000,
            timeout_seconds=settings.HEALTH_CHECK_TIMEOUT_S
        )
        self.failures: List[str] = []
        self.warnings: List[str] = []

    def run_all_checks(self) -> bool:
        """
        Run all diagnostic checks in order.

        Returns:
            True if all checks pass, False if any critical failures
        """
        logger.info("=" * 70)
        logger.info("MIND PROTOCOL SYSTEM DIAGNOSTIC")
        logger.info("=" * 70)
        logger.info("")

        checks = [
            ("1. Startup Self-Tests", self.check_startup_tests),
            ("2. Service Health Endpoints", self.check_service_health),
            ("3. Event Heartbeat", self.check_event_heartbeat),
            ("4. FalkorDB Connectivity", self.check_falkordb),
            ("5. Safe Mode Status", self.check_safe_mode),
        ]

        for name, check_func in checks:
            logger.info(f"Running: {name}")
            try:
                result = check_func()
                if result:
                    logger.info(f"  ✅ PASS: {name}")
                else:
                    logger.error(f"  ❌ FAIL: {name}")
            except Exception as e:
                logger.error(f"  ❌ ERROR: {name} - {str(e)}")
                self.failures.append(f"{name}: {str(e)}")
            logger.info("")

        # Print summary
        logger.info("=" * 70)
        logger.info("DIAGNOSTIC SUMMARY")
        logger.info("=" * 70)

        if len(self.failures) == 0 and len(self.warnings) == 0:
            logger.info("✅ ALL CHECKS PASSED - System is healthy")
            return True
        else:
            if len(self.failures) > 0:
                logger.error(f"❌ {len(self.failures)} CRITICAL FAILURES:")
                for failure in self.failures:
                    logger.error(f"  - {failure}")

            if len(self.warnings) > 0:
                logger.warning(f"⚠️  {len(self.warnings)} WARNINGS:")
                for warning in self.warnings:
                    logger.warning(f"  - {warning}")

            return len(self.failures) == 0

    def check_startup_tests(self) -> bool:
        """Run startup self-tests."""
        all_passed, failures = StartupSelfTests.all_tests_pass()

        if not all_passed:
            for failure in failures:
                self.failures.append(f"Startup test failed: {failure}")
            return False

        return True

    def check_service_health(self) -> bool:
        """Check health endpoints for all services."""
        results = self.health_checker.check_all_services()

        has_failures = False
        for service_name, result in results.items():
            if result.status == HealthStatus.UNHEALTHY:
                self.failures.append(
                    f"{service_name}: {result.message}"
                )
                has_failures = True
            elif result.status == HealthStatus.DEGRADED:
                self.warnings.append(
                    f"{service_name}: {result.message}"
                )

        return not has_failures

    def check_event_heartbeat(self) -> bool:
        """
        Verify WebSocket server is emitting frame.end events.

        TODO: Connect to WebSocket and verify events flowing.
        For now, just checks if service responds.
        """
        try:
            response = requests.get(
                f"http://localhost:{settings.WS_PORT}/health",
                timeout=5
            )

            if response.status_code != 200:
                self.failures.append(
                    f"WebSocket /health returned {response.status_code}"
                )
                return False

            # TODO: Verify frame.end event cadence
            # For Phase 1: just verify service responds
            self.warnings.append(
                "Event heartbeat verification not yet implemented (checking /health only)"
            )

            return True

        except Exception as e:
            self.failures.append(f"Event heartbeat check failed: {str(e)}")
            return False

    def check_falkordb(self) -> bool:
        """Verify FalkorDB connectivity."""
        try:
            from falkordb import FalkorDB

            db = FalkorDB(host=settings.FALKORDB_HOST, port=settings.FALKORDB_PORT)
            # Try to access a test graph
            db.select_graph("_health_check_test")

            return True

        except Exception as e:
            self.failures.append(f"FalkorDB connection failed: {str(e)}")
            return False

    def check_safe_mode(self) -> bool:
        """Check if system is in Safe Mode."""
        try:
            # TODO: Query Safe Mode status from running engine
            # For Phase 1: just check if Safe Mode is enabled in settings
            if settings.SAFE_MODE_ENABLED:
                logger.info("  Safe Mode: ENABLED (monitoring active)")
            else:
                self.warnings.append("Safe Mode disabled in settings")

            return True

        except Exception as e:
            self.warnings.append(f"Could not check Safe Mode: {str(e)}")
            return True  # Not critical


def main():
    """Run diagnostic and exit with appropriate code."""
    diagnostic = SystemDiagnostic()
    success = diagnostic.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
