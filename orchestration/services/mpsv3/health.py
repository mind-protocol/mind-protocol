"""
MPSv3 Health Checks - Service health monitoring.

Implements:
- TCP port checks (is service listening?)
- HTTP GET checks (does endpoint respond?)
- Script checks (custom validation)
- Readiness checks (initial startup verification)
- Liveness checks (ongoing health monitoring)

Author: Victor "The Resurrector"
Date: 2025-10-29
"""

import socket
import subprocess
import time
from dataclasses import dataclass
from typing import Optional, Dict, Any
from urllib.request import urlopen
from urllib.error import URLError


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    passed: bool
    message: str
    latency_ms: float


class HealthChecker:
    """Executes health checks for services."""

    def check_tcp(self, host: str, port: int, timeout_s: float = 3.0) -> HealthCheckResult:
        """Check if TCP port is accepting connections."""
        start = time.time()
        try:
            with socket.create_connection((host, port), timeout=timeout_s):
                latency = (time.time() - start) * 1000
                return HealthCheckResult(
                    passed=True,
                    message=f"TCP {host}:{port} accepting connections",
                    latency_ms=latency
                )
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            latency = (time.time() - start) * 1000
            return HealthCheckResult(
                passed=False,
                message=f"TCP {host}:{port} failed: {type(e).__name__}",
                latency_ms=latency
            )

    def check_http(self, url: str, timeout_s: float = 3.0) -> HealthCheckResult:
        """Check if HTTP endpoint responds with 2xx status."""
        start = time.time()
        try:
            response = urlopen(url, timeout=timeout_s)
            latency = (time.time() - start) * 1000
            status_code = response.getcode()

            if 200 <= status_code < 300:
                return HealthCheckResult(
                    passed=True,
                    message=f"HTTP {url} returned {status_code}",
                    latency_ms=latency
                )
            else:
                return HealthCheckResult(
                    passed=False,
                    message=f"HTTP {url} returned {status_code} (expected 2xx)",
                    latency_ms=latency
                )
        except (URLError, socket.timeout) as e:
            latency = (time.time() - start) * 1000
            return HealthCheckResult(
                passed=False,
                message=f"HTTP {url} failed: {e}",
                latency_ms=latency
            )

    def check_script(self, cmd: str, timeout_s: float = 3.0) -> HealthCheckResult:
        """Run script and check exit code (0 = healthy)."""
        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                timeout=timeout_s,
                capture_output=True,
                text=True
            )
            latency = (time.time() - start) * 1000

            if result.returncode == 0:
                return HealthCheckResult(
                    passed=True,
                    message=f"Script '{cmd}' passed (exit 0)",
                    latency_ms=latency
                )
            else:
                return HealthCheckResult(
                    passed=False,
                    message=f"Script '{cmd}' failed (exit {result.returncode}): {result.stderr[:100]}",
                    latency_ms=latency
                )
        except subprocess.TimeoutExpired:
            latency = (time.time() - start) * 1000
            return HealthCheckResult(
                passed=False,
                message=f"Script '{cmd}' timed out after {timeout_s}s",
                latency_ms=latency
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return HealthCheckResult(
                passed=False,
                message=f"Script '{cmd}' error: {e}",
                latency_ms=latency
            )

    def execute_check(self, check_config: Dict[str, Any]) -> HealthCheckResult:
        """Execute health check from YAML config."""
        # TCP check
        if "tcp" in check_config:
            tcp = check_config["tcp"]
            return self.check_tcp(
                host=tcp.get("host", "127.0.0.1"),
                port=tcp["port"],
                timeout_s=tcp.get("timeout_s", 3.0)
            )

        # HTTP check
        elif "http_get" in check_config:
            http = check_config["http_get"]
            return self.check_http(
                url=http["url"],
                timeout_s=http.get("timeout_s", 3.0)
            )

        # Script check
        elif "script" in check_config:
            script = check_config["script"]
            return self.check_script(
                cmd=script["cmd"],
                timeout_s=script.get("timeout_s", 3.0)
            )

        else:
            return HealthCheckResult(
                passed=False,
                message=f"Unknown check type: {list(check_config.keys())}",
                latency_ms=0.0
            )


class ServiceHealthMonitor:
    """Monitors health of a single service."""

    def __init__(self, service_id: str, readiness_check: Optional[Dict], liveness_check: Optional[Dict]):
        self.service_id = service_id
        self.readiness_check = readiness_check
        self.liveness_check = liveness_check
        self.checker = HealthChecker()

        # State tracking
        self.is_ready = False  # Has service passed readiness check?
        self.consecutive_failures = 0  # Count liveness failures
        self.last_check_time = 0.0
        self.last_result: Optional[HealthCheckResult] = None

    def check_readiness(self, max_attempts: int = 30, interval_s: float = 1.0) -> bool:
        """
        Wait for service to pass readiness check.

        Returns True if service becomes ready, False if max_attempts exhausted.
        """
        if not self.readiness_check:
            # No readiness check defined - assume ready immediately
            self.is_ready = True
            return True

        print(f"[{self.service_id}] Waiting for readiness check...")

        for attempt in range(1, max_attempts + 1):
            result = self.checker.execute_check(self.readiness_check)
            self.last_result = result
            self.last_check_time = time.time()

            if result.passed:
                print(f"[{self.service_id}] ✅ Ready after {attempt} attempt(s) ({result.latency_ms:.0f}ms)")
                self.is_ready = True
                return True

            if attempt < max_attempts:
                time.sleep(interval_s)

        print(f"[{self.service_id}] ❌ Failed readiness after {max_attempts} attempts: {result.message}")
        return False

    def check_liveness(self) -> bool:
        """
        Check if service is alive (ongoing monitoring).

        Returns True if healthy, False if failed.
        Tracks consecutive failures for alerting.
        """
        if not self.liveness_check:
            # No liveness check - can't determine health
            return True  # Assume healthy

        result = self.checker.execute_check(self.liveness_check)
        self.last_result = result
        self.last_check_time = time.time()

        if result.passed:
            if self.consecutive_failures > 0:
                print(f"[{self.service_id}] ✅ Recovered after {self.consecutive_failures} failures")
            self.consecutive_failures = 0
            return True
        else:
            self.consecutive_failures += 1
            print(f"[{self.service_id}] ❌ Liveness check failed ({self.consecutive_failures}x): {result.message}")
            return False

    def should_restart(self, failure_threshold: int = 3) -> bool:
        """Should service be restarted due to health failures?"""
        return self.consecutive_failures >= failure_threshold
