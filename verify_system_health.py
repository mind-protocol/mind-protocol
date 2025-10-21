"""
Mind Protocol System Health Verification

Comprehensive test script that verifies all infrastructure components.

Usage:
    python verify_system_health.py

Returns exit code 0 if all systems operational, 1 if any failures.

Author: Victor "The Resurrector"
Created: 2025-10-20
Purpose: Automated verification of complete infrastructure health
"""

import sys
import time
import socket
import requests
from pathlib import Path
from datetime import datetime, timedelta
import psutil
from falkordb import FalkorDB

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

MIND_PROTOCOL_ROOT = Path(__file__).parent

class HealthCheck:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def test(self, name, check_func):
        """Run a test and track result."""
        print(f"\n{BLUE}[TEST]{RESET} {name}...", end=" ")
        try:
            result = check_func()
            if result is True:
                print(f"{GREEN}[PASS]{RESET}")
                self.passed.append(name)
                return True
            elif result is False:
                print(f"{RED}[FAIL]{RESET}")
                self.failed.append(name)
                return False
            else:
                # Tuple (passed, message)
                passed, message = result
                if passed:
                    print(f"{GREEN}[PASS]{RESET} {message}")
                    self.passed.append(name)
                else:
                    print(f"{RED}[FAIL]{RESET} {message}")
                    self.failed.append(name)
                return passed
        except Exception as e:
            print(f"{RED}[ERROR]{RESET} {str(e)}")
            self.failed.append(name)
            return False

    def warn(self, message):
        """Log a warning."""
        print(f"{YELLOW}⚠ WARNING{RESET} {message}")
        self.warnings.append(message)

    def summary(self):
        """Print final summary and return exit code."""
        print("\n" + "="*70)
        print("SYSTEM HEALTH SUMMARY")
        print("="*70)

        print(f"\n{GREEN}PASSED:{RESET} {len(self.passed)}")
        for test in self.passed:
            print(f"  [OK] {test}")

        if self.warnings:
            print(f"\n{YELLOW}WARNINGS:{RESET} {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  [WARN] {warning}")

        if self.failed:
            print(f"\n{RED}FAILED:{RESET} {len(self.failed)}")
            for test in self.failed:
                print(f"  [FAIL] {test}")
            print(f"\n{RED}SYSTEM NOT FULLY OPERATIONAL{RESET}")
            return 1
        else:
            print(f"\n{GREEN}[OK] ALL SYSTEMS OPERATIONAL{RESET}")
            return 0


def check_port_open(port, host='localhost'):
    """Check if port is open and accepting connections."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def test_falkordb():
    """Test FalkorDB connectivity."""
    try:
        db = FalkorDB(host='localhost', port=6379)
        # Try to connect and run simple query
        g = db.select_graph('schema_registry')
        result = g.query("RETURN 1 as test")
        return result is not None
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def test_websocket_server():
    """Test WebSocket server HTTP endpoint."""
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False, "Server not responding"
    except Exception as e:
        return False, str(e)


def test_dashboard():
    """Test Next.js dashboard."""
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False, "Dashboard not responding"
    except Exception as e:
        return False, str(e)


def test_heartbeat_fresh():
    """Check if heartbeat files are fresh (< 10 seconds old)."""
    heartbeat_dir = MIND_PROTOCOL_ROOT / '.heartbeats'

    if not heartbeat_dir.exists():
        return False, "Heartbeat directory doesn't exist"

    heartbeat_files = list(heartbeat_dir.glob('*.heartbeat'))

    if not heartbeat_files:
        return False, "No heartbeat files found"

    stale_files = []
    fresh_files = []
    now = datetime.now()

    for hb_file in heartbeat_files:
        try:
            mtime = datetime.fromtimestamp(hb_file.stat().st_mtime)
            age = (now - mtime).total_seconds()

            if age > 10:
                stale_files.append(f"{hb_file.name} ({age:.1f}s old)")
            else:
                fresh_files.append(hb_file.name)
        except Exception as e:
            stale_files.append(f"{hb_file.name} (error: {str(e)})")

    if stale_files:
        return False, f"Stale heartbeats: {', '.join(stale_files)}"
    else:
        return True, f"{len(fresh_files)} heartbeat(s) fresh"


def test_guardian_running():
    """Check if guardian process is running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'guardian.py' in ' '.join(cmdline):
                return True, f"PID {proc.info['pid']}"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False, "Guardian process not found"


def test_launcher_running():
    """Check if launcher process is running."""
    lock_file = MIND_PROTOCOL_ROOT / '.launcher.lock'

    if not lock_file.exists():
        return False, "No launcher lock file"

    try:
        pid = int(lock_file.read_text().strip())
        if psutil.pid_exists(pid):
            return True, f"PID {pid}"
        else:
            return False, f"Stale lock (PID {pid} not running)"
    except Exception as e:
        return False, str(e)


def test_consciousness_engines():
    """Check if consciousness engines initialized."""
    try:
        db = FalkorDB(host='localhost', port=6379)

        # Check for N1 citizen graphs
        expected_citizens = ['felix', 'luca', 'ada', 'iris', 'piero', 'marco', 'victor']
        found_graphs = []

        for citizen in expected_citizens:
            graph_name = f"{citizen}citizen"
            try:
                g = db.select_graph(graph_name)
                result = g.query("MATCH (n) RETURN count(n) as count LIMIT 1")
                if result:
                    found_graphs.append(citizen)
            except:
                pass

        if len(found_graphs) == len(expected_citizens):
            return True, f"All {len(found_graphs)} citizen graphs accessible"
        else:
            missing = set(expected_citizens) - set(found_graphs)
            return False, f"Missing graphs: {', '.join(missing)}"

    except Exception as e:
        return False, str(e)


def test_port_conflicts():
    """Check for unexpected processes on critical ports."""
    critical_ports = {
        8000: 'WebSocket Server',
        3000: 'Next.js Dashboard',
        6379: 'FalkorDB'
    }

    conflicts = []

    for port, service in critical_ports.items():
        if not check_port_open(port):
            conflicts.append(f"Port {port} ({service}) not bound")

    if conflicts:
        return False, '; '.join(conflicts)
    else:
        return True, "All critical ports bound correctly"


def main():
    """Run all health checks."""
    print("="*70)
    print("MIND PROTOCOL SYSTEM HEALTH CHECK")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    health = HealthCheck()

    # Core Infrastructure
    print(f"\n{BLUE}>>> CORE INFRASTRUCTURE{RESET}")
    health.test("FalkorDB connectivity", test_falkordb)
    health.test("Port configuration", test_port_conflicts)

    # Process Health
    print(f"\n{BLUE}>>> PROCESS HEALTH{RESET}")
    health.test("Guardian running", test_guardian_running)
    health.test("Launcher running", test_launcher_running)
    health.test("Heartbeats fresh", test_heartbeat_fresh)

    # Service Endpoints
    print(f"\n{BLUE}>>> SERVICE ENDPOINTS{RESET}")
    health.test("WebSocket server responding", test_websocket_server)
    health.test("Dashboard accessible", test_dashboard)

    # Consciousness Infrastructure
    print(f"\n{BLUE}>>> CONSCIOUSNESS INFRASTRUCTURE{RESET}")
    health.test("Consciousness engines initialized", test_consciousness_engines)

    # Final summary
    return health.summary()


if __name__ == "__main__":
    sys.exit(main())
