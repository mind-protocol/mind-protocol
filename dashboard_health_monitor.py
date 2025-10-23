"""
Dashboard Health Monitor - Detects and fixes Next.js HMR accumulation

Monitors Next.js dashboard process for:
- Memory usage >800MB (HMR accumulation)
- HTTP responsiveness
- Connection leaks (CLOSE_WAIT states)

Auto-restarts dashboard when unhealthy.

Usage:
    python dashboard_health_monitor.py  # Run standalone
    # Or: Called periodically from launcher's monitoring loop

Author: Victor "The Resurrector"
Date: 2025-10-21
Purpose: Solve chronic Next.js HMR memory leak requiring manual intervention
"""

import subprocess
import logging
import time
import sys
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def get_process_on_port(port: int) -> Optional[int]:
    """
    Get PID of process listening on port.

    Args:
        port: Port number

    Returns:
        PID if found, None otherwise
    """
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )

        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        return int(pid)

        return None

    except Exception as e:
        logger.error(f"Failed to get PID on port {port}: {e}")
        return None


def get_process_memory_mb(pid: int) -> Optional[float]:
    """
    Get process memory usage in MB.

    Args:
        pid: Process ID

    Returns:
        Memory in MB, None if failed
    """
    try:
        # Use tasklist to get memory
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Parse CSV output: "Image Name","PID","Session Name","Session#","Mem Usage"
        # Example: "node.exe","16688","Console","1","1,459,088 K"
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = [p.strip('"') for p in line.split('","')]
                if len(parts) >= 5:
                    mem_str = parts[4].replace(',', '').replace(' K', '')
                    if mem_str.isdigit():
                        mem_kb = int(mem_str)
                        mem_mb = mem_kb / 1024.0
                        return mem_mb

        return None

    except Exception as e:
        logger.error(f"Failed to get memory for PID {pid}: {e}")
        return None


def count_close_wait_connections(port: int) -> int:
    """
    Count CLOSE_WAIT connections on port (connection leak indicator).

    Args:
        port: Port number

    Returns:
        Count of CLOSE_WAIT connections
    """
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )

        count = 0
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'CLOSE_WAIT' in line:
                count += 1

        return count

    except Exception as e:
        logger.error(f"Failed to count CLOSE_WAIT: {e}")
        return 0


def check_http_responsive(port: int, timeout: int = 5) -> bool:
    """
    Check if HTTP server on port responds.

    Args:
        port: Port number
        timeout: Request timeout in seconds

    Returns:
        True if responsive, False otherwise
    """
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "nul", "-w", "%{http_code}",
             f"http://localhost:{port}/consciousness"],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # Any HTTP response code indicates responsiveness
        return result.stdout.strip().isdigit()

    except Exception:
        return False


def check_dashboard_health(port: int = 3000) -> Tuple[bool, str]:
    """
    Check dashboard health.

    Args:
        port: Dashboard port (default 3000)

    Returns:
        Tuple (is_healthy, reason_if_unhealthy)
    """
    pid = get_process_on_port(port)

    if pid is None:
        return False, "No process on port 3000"

    # Check memory
    memory_mb = get_process_memory_mb(pid)
    if memory_mb is None:
        return False, "Could not read process memory"

    if memory_mb > 800:
        return False, f"Memory exceeded threshold: {memory_mb:.0f}MB > 800MB"

    # Check connection leaks
    close_wait_count = count_close_wait_connections(port)
    if close_wait_count > 20:
        return False, f"Connection leak detected: {close_wait_count} CLOSE_WAIT connections"

    # Check HTTP responsiveness (optional - can be slow)
    # Disabled by default to avoid slowing health checks
    # if not check_http_responsive(port):
    #     return False, "HTTP server not responsive"

    return True, f"Healthy (Memory: {memory_mb:.0f}MB, PID: {pid})"


def restart_dashboard(port: int = 3000) -> bool:
    """
    Restart dashboard by killing and letting launcher restart it.

    Args:
        port: Dashboard port

    Returns:
        True if killed successfully, False otherwise
    """
    logger.info(f"Restarting dashboard on port {port}...")

    pid = get_process_on_port(port)
    if pid is None:
        logger.warning("No process found to restart")
        return False

    try:
        # Kill the process
        subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True,
            timeout=5
        )

        logger.info(f"Killed dashboard process (PID {pid})")
        return True

    except Exception as e:
        logger.error(f"Failed to restart dashboard: {e}")
        return False


def monitor_loop(check_interval: int = 30, port: int = 3000):
    """
    Continuous monitoring loop.

    Args:
        check_interval: Seconds between health checks
        port: Dashboard port
    """
    logger.info("Dashboard health monitor starting...")
    logger.info(f"Checking every {check_interval}s for memory >800MB or connection leaks")

    while True:
        try:
            is_healthy, status = check_dashboard_health(port)

            if is_healthy:
                logger.debug(f"Dashboard health: {status}")
            else:
                logger.warning(f"Dashboard unhealthy: {status}")
                logger.warning("Triggering auto-restart...")

                if restart_dashboard(port):
                    logger.info("Dashboard restart triggered - launcher will restart it")
                    # Wait longer after restart to allow clean startup
                    time.sleep(60)
                else:
                    logger.error("Failed to restart dashboard")

            time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("Health monitor stopped (Ctrl+C)")
            break

        except Exception as e:
            logger.error(f"Health monitor error: {e}")
            time.sleep(check_interval)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - DASHBOARD_HEALTH - %(levelname)s - %(message)s'
    )

    logger.info("=" * 70)
    logger.info("DASHBOARD HEALTH MONITOR - ACTIVE")
    logger.info("Monitoring Next.js for HMR accumulation")
    logger.info("Will auto-restart if memory >800MB or connection leaks detected")
    logger.info("=" * 70)

    monitor_loop(check_interval=30, port=3000)
