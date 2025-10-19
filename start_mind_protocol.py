"""
Mind Protocol Unified Launcher

Starts and monitors all consciousness infrastructure components:
- FalkorDB (database backend)
- Conversation Watcher (TRACE format capture)
- Consciousness Engine (optional - substrate heartbeat)
- Dashboard (optional - Next.js frontend)

Handles automatic restarts on crashes and graceful shutdown.

Usage:
    python start_mind_protocol.py [--full]  # Full system with consciousness engine
    python start_mind_protocol.py           # Core only (DB + watchers)

Author: Felix "Ironhand"
Date: 2025-10-19
"""

import asyncio
import logging
import subprocess
import sys
import signal
import time
import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MIND_PROTOCOL_ROOT = Path(__file__).parent
LOCK_FILE = MIND_PROTOCOL_ROOT / ".launcher.lock"


def acquire_launcher_lock():
    """
    Ensure only ONE launcher instance runs.

    Creates lock file with current PID. If lock exists and process is alive,
    refuses to start. If lock exists but process is dead, takes over.

    Returns:
        File handle to lock file (keep open while running)
    """
    try:
        if LOCK_FILE.exists():
            # Check if existing process is still alive
            try:
                existing_pid = int(LOCK_FILE.read_text().strip())

                # Check if process exists (Windows-specific)
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {existing_pid}"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if str(existing_pid) in result.stdout:
                    logger.error(f"[Guardian] Another launcher already running (PID {existing_pid})")
                    logger.error("Kill the other launcher first or wait for it to exit")
                    sys.exit(1)
                else:
                    logger.warning(f"[Guardian] Stale lock file found (dead PID {existing_pid}), taking over")
                    LOCK_FILE.unlink()

            except Exception:
                # Corrupt lock file, remove it
                logger.warning("[Guardian] Corrupt lock file, removing")
                LOCK_FILE.unlink()

        # Create new lock file
        lock_fd = open(LOCK_FILE, 'w')
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()

        logger.info(f"[Guardian] Lock acquired (PID {os.getpid()}) - I am the guardian")
        return lock_fd

    except Exception as e:
        logger.error(f"[Guardian] Lock acquisition failed: {e}")
        sys.exit(1)


class ProcessManager:
    """Manages lifecycle of all Mind Protocol processes."""

    def __init__(self, full_system: bool = True):  # Changed default to True
        """
        Initialize process manager.

        Args:
            full_system: If True, start consciousness engine + dashboard (DEFAULT)
        """
        self.full_system = full_system
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = True
        self.lock_fd = None  # Lock file handle for single-instance enforcement
        self.file_mtimes: Dict[str, float] = {}  # Track file modification times for auto-restart

    async def cleanup_existing_processes(self):
        """Kill any existing Mind Protocol processes before starting."""
        logger.info("[0/4] Cleaning up existing processes...")

        try:
            # Kill existing conversation watchers
            result = subprocess.run(
                ["pkill", "-f", "conversation_watcher"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("  Killed existing conversation watchers")

            # Kill existing Node.js processes on port 3000
            # First find the PID using port 3000
            port_check = subprocess.run(
                ["cmd.exe", "/c", "netstat -ano | findstr :3000 | findstr LISTENING"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if port_check.stdout:
                # Extract PID from netstat output (last column)
                for line in port_check.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                subprocess.run(
                                    ["cmd.exe", "/c", f"taskkill /PID {pid} /F"],
                                    capture_output=True,
                                    timeout=5
                                )
                                logger.info(f"  Killed process on port 3000 (PID: {pid})")
                            except Exception as e:
                                logger.debug(f"  Could not kill PID {pid}: {e}")

            logger.info("  ✅ Cleanup complete")

        except Exception as e:
            logger.debug(f"  Cleanup encountered errors (non-fatal): {e}")

    async def start_all(self):
        """Start all components in order."""
        # Acquire guardian lock FIRST (single instance enforcement)
        self.lock_fd = acquire_launcher_lock()

        logger.info("=" * 70)
        logger.info("MIND PROTOCOL UNIFIED LAUNCHER (GUARDIAN MODE)")
        logger.info("=" * 70)

        # 0. Kill any blocking processes first
        logger.info("[0/5] Cleaning up existing processes...")
        await self._cleanup_existing_processes()

        # 1. Check FalkorDB
        if not await self.check_falkordb():
            logger.error("FalkorDB not running. Start it first:")
            logger.error("  docker-compose up -d")
            return False

        # 2. Start WebSocket server (dashboard API)
        if not await self.start_websocket_server():
            return False

        # 3. Start conversation watcher (TRACE format capture)
        if not await self.start_conversation_watcher():
            return False

        # 4. Optionally start consciousness engine
        if self.full_system:
            if not await self.start_consciousness_engine():
                return False

            # 5. Optionally start dashboard
            if not await self.start_dashboard():
                return False

        logger.info("")
        logger.info("=" * 70)
        logger.info("ALL SYSTEMS OPERATIONAL")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Running components:")
        for name in self.processes.keys():
            logger.info(f"  ✅ {name}")

        logger.info("")
        logger.info("Guardian features:")
        logger.info("  🛡️  Single instance enforcement (PID lock)")
        logger.info("  🔍 Rogue process monitoring (kills manual starts)")
        logger.info("  🔄 Auto-restart on crash (via guardian.py)")
        logger.info("  🔥 Hot-reload on code changes (2s detection)")
        logger.info("")
        logger.info("Press Ctrl+C to shutdown gracefully")
        logger.info("=" * 70)

        # Start guardian monitoring tasks
        asyncio.create_task(self.monitor_and_kill_rogues())
        asyncio.create_task(self.monitor_code_changes())

        return True

    async def check_falkordb(self) -> bool:
        """Check if FalkorDB is running."""
        logger.info("[1/5] Checking FalkorDB...")

        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=falkordb", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if "falkordb" in result.stdout:
                logger.info("  ✅ FalkorDB running")
                return True
            else:
                logger.error("  ❌ FalkorDB not running")
                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to check FalkorDB: {e}")
            return False

    async def start_websocket_server(self) -> bool:
        """Start WebSocket server (dashboard API)."""
        logger.info("[2/5] Starting WebSocket Server...")

        # Enforce port 8000 (aggressive cleanup)
        logger.info("  Enforcing port 8000 (aggressive cleanup)...")

        # Kill any processes on port 8000 until none remain
        for attempt in range(5):
            killed = await self._kill_port(8000)
            if killed > 0:
                logger.info(f"    Attempt {attempt + 1}/5: Killed {killed} process(es), checking again...")
                await asyncio.sleep(1)
            else:
                logger.info(f"    Attempt {attempt + 1}/5: Port 8000 clear")
                break

        # Wait for OS to fully release port
        await asyncio.sleep(2)

        # Verify port is actually free
        if not await self._verify_port_free(8000):
            logger.error("  ❌ Port 8000 still occupied after aggressive cleanup!")
            return False

        logger.info("  ✅ Port 8000 verified free")

        try:
            server_script = MIND_PROTOCOL_ROOT / "orchestration" / "websocket_server.py"

            if not server_script.exists():
                logger.error(f"  ❌ Script not found: {server_script}")
                return False

            logger.info("  Starting uvicorn server on port 8000...")
            process = subprocess.Popen(
                [sys.executable, str(server_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            self.processes['websocket_server'] = process

            # Give it time to start and bind to port (uvicorn can take 5-7 seconds)
            await asyncio.sleep(7)

            if process.poll() is None:
                # Verify it actually bound to 8000
                if await self._verify_port_in_use(8000):
                    logger.info("  ✅ WebSocket Server started on port 8000")
                    return True
                else:
                    logger.error("  ❌ WebSocket Server started but NOT on port 8000")
                    process.terminate()
                    return False
            else:
                logger.error("  ❌ WebSocket Server failed to start")
                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start WebSocket Server: {e}")
            return False

    async def start_conversation_watcher(self) -> bool:
        """Start conversation watcher."""
        logger.info("[3/5] Starting Conversation Watcher...")

        try:
            watcher_script = MIND_PROTOCOL_ROOT / "orchestration" / "conversation_watcher.py"

            if not watcher_script.exists():
                logger.error(f"  ❌ Script not found: {watcher_script}")
                return False

            process = subprocess.Popen(
                [sys.executable, str(watcher_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            self.processes['conversation_watcher'] = process

            # Give it a moment to start
            await asyncio.sleep(2)

            if process.poll() is None:
                logger.info("  ✅ Conversation Watcher started")
                return True
            else:
                logger.error("  ❌ Conversation Watcher failed to start")
                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start Conversation Watcher: {e}")
            return False

    async def start_consciousness_engine(self) -> bool:
        """Start consciousness engine (substrate heartbeat)."""
        logger.info("[4/5] Starting Consciousness Engine...")

        try:
            engine_script = MIND_PROTOCOL_ROOT / "start_consciousness_system.py"

            if not engine_script.exists():
                logger.warning(f"  ⚠️  Script not found: {engine_script}")
                logger.info("  ⏭️  Skipping consciousness engine")
                return True

            process = subprocess.Popen(
                [sys.executable, str(engine_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            self.processes['consciousness_engine'] = process

            # Give it a moment to start
            await asyncio.sleep(3)

            if process.poll() is None:
                logger.info("  ✅ Consciousness Engine started")
                return True
            else:
                logger.error("  ❌ Consciousness Engine failed to start")
                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start Consciousness Engine: {e}")
            return False

    async def start_dashboard(self) -> bool:
        """Start Next.js dashboard with AGGRESSIVE port 3000 enforcement."""
        logger.info("[5/5] Starting Dashboard...")

        try:
            dashboard_dir = MIND_PROTOCOL_ROOT

            # Check if Next.js is configured
            if not (dashboard_dir / "package.json").exists():
                logger.warning("  ⚠️  No package.json found")
                logger.info("  ⏭️  Skipping dashboard")
                return True

            # AGGRESSIVE PORT 3000 ENFORCEMENT
            logger.info("  Enforcing port 3000 (aggressive cleanup)...")

            # Step 1: Kill ALL processes on port 3000 until none remain
            max_attempts = 5
            for attempt in range(max_attempts):
                killed = await self._kill_port_3000()
                if not killed:
                    logger.info(f"    Attempt {attempt + 1}/{max_attempts}: Port 3000 clear")
                    break
                else:
                    logger.info(f"    Attempt {attempt + 1}/{max_attempts}: Killed {killed} process(es), checking again...")
                    await asyncio.sleep(1)

            # Step 2: Wait for OS to fully release port
            logger.info("  Waiting for port 3000 to fully release...")
            await asyncio.sleep(2)

            # Step 3: Verify port is actually free
            if not await self._verify_port_free(3000):
                logger.error("  ❌ Port 3000 still occupied after aggressive cleanup!")
                logger.error("  Cannot start dashboard - port enforcement failed")
                return False

            logger.info("  ✅ Port 3000 verified free")

            # Step 4: Start dashboard with FORCED port 3000 (hardcoded in package.json)
            logger.info("  Starting Next.js on port 3000 (forced via package.json dev script)...")

            # Port 3000 is hardcoded in package.json: "dev": "next dev -p 3000"
            process = subprocess.Popen(
                "npm run dev",
                cwd=str(dashboard_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                shell=True
            )

            self.processes['dashboard'] = process

            # Step 5: Monitor startup for port drift
            logger.info("  Monitoring startup for port drift...")
            port_detected = None
            startup_timeout = 10  # seconds
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < startup_timeout:
                if process.poll() is not None:
                    logger.error("  ❌ Dashboard crashed during startup")
                    return False

                # Check process output for port messages
                # (This is best-effort - Next.js might not have output yet)
                await asyncio.sleep(0.5)

                # If process still running after timeout, assume success
                if (asyncio.get_event_loop().time() - start_time) >= startup_timeout:
                    break

            # Step 6: Verify dashboard bound to port 3000 (not drifted)
            await asyncio.sleep(2)  # Give it moment to bind

            if await self._verify_port_in_use(3000):
                logger.info("  ✅ Dashboard started on port 3000 (http://localhost:3000)")
                return True
            else:
                # Port drift detected - dashboard running but not on 3000
                logger.error("  ❌ PORT DRIFT DETECTED!")
                logger.error("  Dashboard started but NOT on port 3000")
                logger.error("  This indicates port enforcement failed")

                # Kill the drifted process
                logger.error("  Killing drifted dashboard process...")
                try:
                    process.terminate()
                    await asyncio.sleep(1)
                    if process.poll() is None:
                        process.kill()
                except Exception:
                    pass

                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start Dashboard: {e}")
            return False

    async def _cleanup_existing_processes(self):
        """Kill any existing Mind Protocol processes and clear ports."""
        killed_count = 0

        try:
            # Kill port 3000 (Next.js dashboard)
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                if ':3000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if parts:
                        pid = parts[-1]
                        try:
                            subprocess.run(
                                ["taskkill", "/PID", pid, "/F"],
                                capture_output=True,
                                timeout=5
                            )
                            logger.info(f"  Killed process {pid} blocking port 3000")
                            killed_count += 1
                        except Exception:
                            pass

            # Kill any existing conversation_watcher processes
            try:
                result = subprocess.run(
                    ["tasklist"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                for line in result.stdout.split('\n'):
                    if 'python' in line.lower() and 'conversation_watcher' in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            pid = parts[1]
                            try:
                                subprocess.run(
                                    ["taskkill", "/PID", pid, "/F"],
                                    capture_output=True,
                                    timeout=5
                                )
                                logger.info(f"  Killed existing conversation_watcher process {pid}")
                                killed_count += 1
                            except Exception:
                                pass
            except Exception:
                pass

            if killed_count == 0:
                logger.info("  ✅ No conflicting processes found")
            else:
                logger.info(f"  ✅ Cleaned up {killed_count} existing process(es)")
                await asyncio.sleep(2)  # Give OS time to release resources

        except Exception as e:
            logger.debug(f"  Cleanup check: {e}")

    async def _kill_port(self, port: int) -> int:
        """
        Kill any process using the specified port.

        Args:
            port: Port number to clear

        Returns:
            Number of processes killed
        """
        killed_count = 0

        try:
            # Windows: Find process using port
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    # Extract PID (last column)
                    parts = line.split()
                    if parts:
                        pid = parts[-1]
                        try:
                            subprocess.run(
                                ["taskkill", "/PID", pid, "/F"],
                                capture_output=True,
                                timeout=5
                            )
                            logger.debug(f"  Killed process {pid} on port {port}")
                            killed_count += 1
                        except Exception:
                            pass

        except Exception as e:
            logger.debug(f"  Port cleanup error: {e}")

        return killed_count

    async def _kill_port_3000(self) -> int:
        """Kill any process using port 3000."""
        return await self._kill_port(3000)

    async def _verify_port_free(self, port: int) -> bool:
        """
        Verify that a port is not in use.

        Args:
            port: Port number to check

        Returns:
            True if port is free, False if occupied
        """
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Check if port appears in LISTENING state
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    return False  # Port is occupied

            return True  # Port is free

        except Exception as e:
            logger.debug(f"  Port verification error: {e}")
            return False  # Assume occupied on error

    async def _verify_port_in_use(self, port: int) -> bool:
        """
        Verify that a port IS in use (opposite of _verify_port_free).

        Args:
            port: Port number to check

        Returns:
            True if port is in use, False if free
        """
        return not await self._verify_port_free(port)

    def _check_file_changes(self) -> List[str]:
        """
        Check if monitored directories have changed since last check.

        Uses simple directory-based detection:
        - orchestration/*.py changed → restart all Python services
        - app/**/* changed → restart dashboard

        Returns:
            List of service names that need restart
        """
        services_to_restart = set()

        # Check orchestration directory for Python file changes
        orchestration_dir = MIND_PROTOCOL_ROOT / "orchestration"
        if orchestration_dir.exists():
            for py_file in orchestration_dir.glob("*.py"):
                try:
                    current_mtime = py_file.stat().st_mtime
                    file_key = str(py_file)

                    # First time - record mtime, don't trigger
                    if file_key not in self.file_mtimes:
                        self.file_mtimes[file_key] = current_mtime
                        continue

                    # File changed - restart all Python services
                    if current_mtime > self.file_mtimes[file_key]:
                        logger.info(f"[Guardian] 📝 Code changed: {py_file.name}")
                        self.file_mtimes[file_key] = current_mtime

                        # Restart all Python services (aggressive but safe)
                        services_to_restart.add("websocket_server")
                        services_to_restart.add("conversation_watcher")

                except Exception as e:
                    logger.debug(f"[Guardian] Error checking {py_file}: {e}")

        # Check app directory for frontend changes
        app_dir = MIND_PROTOCOL_ROOT / "app"
        if app_dir.exists():
            # Check all .tsx, .ts, .jsx, .js files recursively
            for pattern in ["**/*.tsx", "**/*.ts", "**/*.jsx", "**/*.js"]:
                for frontend_file in app_dir.glob(pattern):
                    try:
                        current_mtime = frontend_file.stat().st_mtime
                        file_key = str(frontend_file)

                        # First time - record mtime, don't trigger
                        if file_key not in self.file_mtimes:
                            self.file_mtimes[file_key] = current_mtime
                            continue

                        # File changed - restart dashboard
                        if current_mtime > self.file_mtimes[file_key]:
                            logger.info(f"[Guardian] 📝 Frontend changed: {frontend_file.relative_to(MIND_PROTOCOL_ROOT)}")
                            self.file_mtimes[file_key] = current_mtime
                            services_to_restart.add("dashboard")

                    except Exception as e:
                        logger.debug(f"[Guardian] Error checking {frontend_file}: {e}")

        return list(services_to_restart)

    async def monitor_code_changes(self):
        """
        Monitor code files for changes and auto-restart affected services.

        This provides hot-reload functionality for developers:
        - Edit orchestration/*.py → auto-restart Python services
        - Edit app/**/*.tsx → auto-restart dashboard
        - Changes detected within 2 seconds
        - No manual restarts needed
        """
        logger.info("[Guardian] Starting code change monitor (hot-reload enabled)")

        while self.running:
            await asyncio.sleep(2)  # Check every 2 seconds

            services_to_restart = self._check_file_changes()

            for service_name in services_to_restart:
                # Only restart if service is actually running
                if service_name not in self.processes:
                    logger.debug(f"[Guardian] Service {service_name} not running, skipping")
                    continue

                process = self.processes[service_name]
                if process.poll() is not None:
                    # Already dead, monitor_processes() will restart it
                    logger.debug(f"[Guardian] Service {service_name} already dead, monitor will restart")
                    continue

                logger.info(f"[Guardian] 🔄 Auto-restarting: {service_name}")

                try:
                    # Kill process - monitor_processes() will restart it automatically
                    process.terminate()
                    await asyncio.sleep(0.5)

                    # Force kill if still alive
                    if process.poll() is None:
                        process.kill()

                    logger.info(f"[Guardian] ✅ {service_name} killed (will restart in ~2s)")

                except Exception as e:
                    logger.error(f"[Guardian] Failed to kill {service_name}: {e}")

    def _get_mind_protocol_processes(self) -> List[Tuple[str, str]]:
        """
        Find all Mind Protocol python processes running on system.

        Returns:
            List of (PID, process_info) tuples
        """
        processes = []

        try:
            result = subprocess.run(
                ["tasklist", "/V", "/FO", "CSV"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                if 'python' in line.lower():
                    # Check if it's one of our scripts
                    if any(script in line.lower() for script in [
                        'conversation_watcher',
                        'websocket_server',
                        'trace_capture',
                        'consciousness_engine'
                    ]):
                        # Parse PID from CSV (second column)
                        parts = line.split(',')
                        if len(parts) >= 2:
                            pid = parts[1].strip('"')
                            processes.append((pid, line))

        except Exception as e:
            logger.debug(f"[Guardian] Process scan error: {e}")

        return processes

    async def monitor_and_kill_rogues(self):
        """
        Guardian loop - continuously monitor for and kill rogue processes.

        A rogue process is any Mind Protocol script running without being
        managed by this launcher. This prevents fragmented startups.
        """
        logger.info("[Guardian] Starting rogue process monitor")

        while self.running:
            await asyncio.sleep(5)  # Check every 5 seconds

            # Get all Mind Protocol processes
            all_processes = self._get_mind_protocol_processes()

            # Get PIDs we manage
            managed_pids = {str(p.pid) for p in self.processes.values() if p.poll() is None}

            # Find rogues (running but not managed by us)
            for pid, process_info in all_processes:
                if pid not in managed_pids:
                    logger.warning(f"[Guardian] ROGUE PROCESS DETECTED: PID {pid}")
                    logger.warning(f"  Process: {process_info[:100]}")

                    try:
                        subprocess.run(
                            ["taskkill", "/PID", pid, "/F"],
                            capture_output=True,
                            timeout=5
                        )
                        logger.info(f"[Guardian] ✅ Killed rogue process {pid}")

                    except Exception as e:
                        logger.error(f"[Guardian] Failed to kill rogue {pid}: {e}")

    async def monitor_processes(self):
        """Monitor processes and restart on crash."""
        while self.running:
            await asyncio.sleep(5)

            for name, process in list(self.processes.items()):
                if process.poll() is not None:
                    logger.error(f"❌ {name} crashed! Exit code: {process.returncode}")

                    # Auto-restart
                    logger.info(f"🔄 Restarting {name}...")

                    if name == 'websocket_server':
                        await self.start_websocket_server()
                    elif name == 'conversation_watcher':
                        await self.start_conversation_watcher()
                    elif name == 'consciousness_engine':
                        await self.start_consciousness_engine()
                    elif name == 'dashboard':
                        await self.start_dashboard()

    async def shutdown(self):
        """Gracefully shutdown all processes."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("SHUTTING DOWN")
        logger.info("=" * 70)

        self.running = False

        for name, process in self.processes.items():
            logger.info(f"Stopping {name}...")
            try:
                process.terminate()
                await asyncio.sleep(2)

                if process.poll() is None:
                    logger.warning(f"  Force killing {name}")
                    process.kill()

                logger.info(f"  ✅ {name} stopped")

            except Exception as e:
                logger.error(f"  ❌ Failed to stop {name}: {e}")

        # Release guardian lock
        if self.lock_fd:
            logger.info("Releasing guardian lock...")
            try:
                self.lock_fd.close()
                LOCK_FILE.unlink(missing_ok=True)
                logger.info("  ✅ Lock released")
            except Exception as e:
                logger.error(f"  ❌ Lock cleanup failed: {e}")

        logger.info("=" * 70)
        logger.info("SHUTDOWN COMPLETE")
        logger.info("=" * 70)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Mind Protocol Unified Launcher")
    parser.add_argument(
        "--core-only",
        action="store_true",
        help="Start core only (DB + watchers, no dashboard)"
    )
    args = parser.parse_args()

    # Default is full system (with dashboard), --core-only disables it
    manager = ProcessManager(full_system=not args.core_only)

    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("\nReceived shutdown signal...")
        asyncio.create_task(manager.shutdown())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start all systems
    if not await manager.start_all():
        logger.error("Failed to start all systems")
        return 1

    # Monitor and keep alive
    try:
        await manager.monitor_processes()
    except KeyboardInterrupt:
        pass
    finally:
        await manager.shutdown()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
