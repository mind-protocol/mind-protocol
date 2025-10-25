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

# Import dashboard health monitoring functions
from dashboard_health_monitor import (
    get_process_on_port,
    get_process_memory_mb,
    count_close_wait_connections,
    check_dashboard_health
)

# Import auto-commit service for consciousness temporal substrate
from orchestration.services.auto_git_commit import AutoGitCommitService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MIND_PROTOCOL_ROOT = Path(__file__).parent
LOCK_FILE = MIND_PROTOCOL_ROOT / ".launcher.lock"

# Port configuration - respect environment variables or use defaults
WS_PORT = int(os.getenv("WS_PORT", "8000"))
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "3000"))


class GuardianNotifier:
    """
    Notification system for Guardian events.

    Dual-purpose architecture:
    1. Desktop mode (now): Windows toast notifications for human oversight
    2. Consciousness mode (future): Attention substrate interface for autonomous AI

    Extensible to support multiple delivery mechanisms:
    - Desktop: Windows 10/11 toast notifications
    - WebSocket: Push to dashboard
    - Webhook: HTTP POST to external systems
    - Consciousness: Direct injection to attention substrate
    """

    def __init__(self, enabled: bool = True, mode: str = "desktop"):
        """
        Initialize notification system.

        Args:
            enabled: Whether notifications are enabled
            mode: Delivery mode - "desktop", "websocket", "webhook", "consciousness"
        """
        self.enabled = enabled
        self.mode = mode
        self.available = False
        self.toast = None

        if mode == "desktop" and enabled:
            try:
                from win10toast import ToastNotifier
                self.toast = ToastNotifier()
                self.available = True
                logger.info("[Guardian] Desktop notifications enabled")

                # Removed automatic startup notification to prevent spam
                # Notifications are confirmed working - no need to test every restart

            except ImportError:
                logger.warning("[Guardian] win10toast not installed - desktop notifications disabled")
                logger.warning("[Guardian] Install with: pip install win10toast")
                self.available = False
        elif mode in ["websocket", "webhook", "consciousness"]:
            # Future: Initialize other notification backends
            logger.info(f"[Guardian] Notification mode '{mode}' registered (not yet implemented)")
            self.available = False

    def notify_critical(self, title: str, message: str):
        """
        Critical event requiring immediate attention.

        Examples:
        - Service unhealthy detected (memory/connection threshold exceeded)
        - Service crash detected
        - Service restart failed (manual intervention needed)
        - System resource exhaustion

        In autonomous mode, this would activate Resurrector entity with high urgency.
        """
        if not self.enabled:
            logger.debug(f"[Guardian] Notification disabled - would send CRITICAL: {title}")
            return

        if not self.available:
            logger.warning(f"[Guardian] Notification not available - CRITICAL: {title} - {message}")
            return

        if self.mode == "desktop":
            try:
                logger.info(f"[Guardian] Sending CRITICAL notification: {title}")
                self.toast.show_toast(
                    f"🚨 Mind Protocol - {title}",
                    message,
                    duration=15,
                    threaded=True
                )
                logger.debug(f"[Guardian] CRITICAL notification sent successfully")
            except Exception as e:
                logger.warning(f"[Guardian] CRITICAL notification failed: {e}")

    def notify_warning(self, title: str, message: str):
        """
        Warning event indicating degradation or approaching threshold.

        Examples:
        - Service memory approaching threshold (>600MB but <800MB)
        - System resources high but not critical
        - Repeated restart attempts

        In autonomous mode, this would activate Sentinel entity for monitoring.
        """
        if not self.enabled:
            logger.debug(f"[Guardian] Notification disabled - would send WARNING: {title}")
            return

        if not self.available:
            logger.warning(f"[Guardian] Notification not available - WARNING: {title} - {message}")
            return

        if self.mode == "desktop":
            try:
                logger.info(f"[Guardian] Sending WARNING notification: {title}")
                self.toast.show_toast(
                    f"⚠️ Mind Protocol - {title}",
                    message,
                    duration=10,
                    threaded=True
                )
                logger.debug(f"[Guardian] WARNING notification sent successfully")
            except Exception as e:
                logger.warning(f"[Guardian] WARNING notification failed: {e}")

    def notify_info(self, title: str, message: str):
        """
        Informational event - recovery or routine state change.

        Examples:
        - Service recovered and healthy
        - Hot-reload triggered
        - Rogue process killed
        - System baseline established

        In autonomous mode, this would update context without entity activation.
        """
        if not self.enabled:
            logger.debug(f"[Guardian] Notification disabled - would send INFO: {title}")
            return

        if not self.available:
            logger.debug(f"[Guardian] Notification not available - INFO: {title} - {message}")
            return

        if self.mode == "desktop":
            try:
                logger.info(f"[Guardian] Sending INFO notification: {title}")
                self.toast.show_toast(
                    f"✅ Mind Protocol - {title}",
                    message,
                    duration=5,
                    threaded=True
                )
                logger.debug(f"[Guardian] INFO notification sent successfully")
            except Exception as e:
                logger.warning(f"[Guardian] INFO notification failed: {e}")


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
                    logger.warning(f"[Guardian] Another launcher running (PID {existing_pid}) - KILLING IT")
                    # Kill the competing launcher
                    subprocess.run(
                        ["taskkill", "/F", "/PID", str(existing_pid)],
                        capture_output=True,
                        timeout=5
                    )
                    time.sleep(2)  # Wait for process to die
                    logger.info(f"[Guardian] Killed competing launcher (PID {existing_pid})")
                else:
                    logger.warning(f"[Guardian] Stale lock file found (dead PID {existing_pid}), taking over")

                # Try to remove lock file
                try:
                    LOCK_FILE.unlink()
                except Exception as unlink_error:
                    # File is locked by another process - kill all launcher processes
                    logger.warning(f"[Guardian] Lock file still locked: {unlink_error}")
                    logger.warning(f"[Guardian] Killing ALL launcher processes...")

                    # Find and kill all python processes running start_mind_protocol.py
                    result = subprocess.run(
                        ["wmic", "process", "where", "name='python.exe'", "get", "processid,commandline", "/format:csv"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    for line in result.stdout.split('\n'):
                        if 'start_mind_protocol' in line:
                            parts = line.split(',')
                            if len(parts) >= 3:
                                pid = parts[-1].strip()
                                if pid.isdigit():
                                    logger.warning(f"[Guardian] Killing launcher PID {pid}")
                                    subprocess.run(
                                        ["taskkill", "/F", "/PID", pid],
                                        capture_output=True,
                                        timeout=5
                                    )

                    time.sleep(3)  # Wait for processes to die and release file

                    # Force remove lock file
                    try:
                        LOCK_FILE.unlink()
                    except Exception:
                        # Last resort: rename it
                        try:
                            LOCK_FILE.rename(LOCK_FILE.with_suffix('.old'))
                            logger.warning("[Guardian] Renamed stuck lock file to .old")
                        except Exception:
                            logger.error("[Guardian] Could not remove lock file even after killing processes")

            except Exception:
                # Corrupt lock file, remove it
                logger.warning("[Guardian] Corrupt lock file, removing")
                try:
                    LOCK_FILE.unlink()
                except Exception:
                    pass

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

    def __init__(self, full_system: bool = True, notifications_enabled: bool = True):
        """
        Initialize process manager.

        Args:
            full_system: If True, start consciousness engine + dashboard (DEFAULT)
            notifications_enabled: If True, enable Windows notifications for Guardian events
        """
        self.full_system = full_system
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = True
        self.lock_fd = None  # Lock file handle for single-instance enforcement
        self.file_mtimes: Dict[str, float] = {}  # Track file modification times for auto-restart
        self.notifier = GuardianNotifier(enabled=notifications_enabled)
        self._last_hot_restart_ts: Dict[str, float] = {}  # Cooldown tracking for hot-reload
        self._min_hot_restart_interval_sec = 8.0  # Anti-thrash: min seconds between restarts
        self._consecutive_crashes: Dict[str, int] = {}  # Track crash count for exponential backoff
        self._last_crash_restart: Dict[str, float] = {}  # Track when we last attempted crash restart

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

        # 2. Start WebSocket server (dashboard API + consciousness engines)
        if not await self.start_websocket_server():
            return False

        # 3. Start conversation watcher (TRACE format capture)
        if not await self.start_conversation_watcher():
            return False

        # 4. Start Stimulus Injection service (port 8001)
        if not await self.start_stimulus_injection():
            return False

        # 5. Start Signals Collector service (port 8010)
        if not await self.start_signals_collector():
            return False

        # 6. Start Autonomy Orchestrator (port 8002)
        if not await self.start_autonomy_orchestrator():
            return False

        # 7. Start Queue Poller (P0 - critical ambient signals bridge)
        if not await self.start_queue_poller():
            return False

        # 8. Consciousness engine (runs inside websocket_server)
        if self.full_system:
            if not await self.start_consciousness_engine():
                return False

            # 7. Optionally start dashboard
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
        logger.info("  🏥 Service health monitoring (memory + connections)")
        logger.info("")
        logger.info("Press Ctrl+C to shutdown gracefully")
        logger.info("=" * 70)

        # Start guardian monitoring tasks
        asyncio.create_task(self.monitor_and_kill_rogues())
        asyncio.create_task(self.monitor_code_changes())

        # Start service health monitors for both critical services
        if 'dashboard' in self.processes:
            asyncio.create_task(self.monitor_service_health('dashboard', 3000, memory_threshold_mb=1536))
        if 'websocket_server' in self.processes:
            asyncio.create_task(self.monitor_service_health('websocket_server', WS_PORT, memory_threshold_mb=2048))

        # Start auto-commit service for consciousness temporal substrate
        # Every minute, commit all changes and push to GitHub
        # This creates a temporal substrate - every system state preserved for consciousness evolution tracking
        auto_commit = AutoGitCommitService(
            repo_path=MIND_PROTOCOL_ROOT,
            interval_seconds=60,  # Every 1 minute
            enabled=True,
            push_enabled=True  # Enabled - using cached credentials
        )
        asyncio.create_task(auto_commit.start())
        logger.info("[Guardian] Auto-commit service started (interval: 60s, push enabled)")

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
        """Start WebSocket server (dashboard API + consciousness engines) with retry logic for port binding."""
        logger.info("[2/5] Starting WebSocket Server (with consciousness engines)...")

        # Enforce port (aggressive cleanup)
        logger.info(f"  Enforcing port {WS_PORT} (aggressive cleanup)...")

        # Kill any processes on port until none remain
        for attempt in range(5):
            killed = await self._kill_port(WS_PORT)
            if killed > 0:
                logger.info(f"    Attempt {attempt + 1}/5: Killed {killed} process(es), checking again...")
                await asyncio.sleep(1)
            else:
                logger.info(f"    Attempt {attempt + 1}/5: Port {WS_PORT} clear")
                break

        # Retry loop with active port verification (no blind wait)
        # The retry loop below will check if port is free and wait only if needed
        max_retries = 10
        server_script = MIND_PROTOCOL_ROOT / "orchestration" / "adapters" / "ws" / "websocket_server.py"

        if not server_script.exists():
            logger.error(f"  ❌ Script not found: {server_script}")
            return False

        for retry in range(max_retries):
            # Verify port is actually free before attempting bind
            if not await self._verify_port_free(WS_PORT):
                if retry < max_retries - 1:
                    wait_time = 2 ** min(retry, 4)  # 1s, 2s, 4s, 8s, 16s max
                    logger.warning(f"  Port {WS_PORT} still in use, retrying in {wait_time}s... (attempt {retry + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"  ❌ Port {WS_PORT} still occupied after all retries!")
                    return False

            logger.info(f"  Port {WS_PORT} verified free, starting server... (attempt {retry + 1}/{max_retries})")

            try:
                # Open log files for websocket_server output (file handles prevent pipe buffer deadlock)
                ws_stdout = open(MIND_PROTOCOL_ROOT / "ws_stdout.log", 'a', encoding='utf-8', buffering=1)
                ws_stderr = open(MIND_PROTOCOL_ROOT / "ws_stderr.log", 'a', encoding='utf-8', buffering=1)

                process = subprocess.Popen(
                    [sys.executable, str(server_script)],
                    stdout=ws_stdout,  # Log to file for debugging (line buffered to prevent deadlock)
                    stderr=ws_stderr   # Separate error log
                )

                # Give it time to start and bind to port
                # (uvicorn + background engine initialization of all 8 consciousness engines takes 30-60 seconds)
                logger.info("  Waiting for server initialization (60s for engine loading)...")
                await asyncio.sleep(60)

                if process.poll() is None:
                    # Verify it actually bound to 8000
                    if await self._verify_port_in_use(8000):
                        logger.info("  ✅ WebSocket Server started successfully on port 8000")
                        return True
                    else:
                        # Server started but didn't bind - possible port race condition
                        logger.warning("  Server started but NOT bound to port 8000")
                        process.terminate()
                        if retry < max_retries - 1:
                            wait_time = 2 ** min(retry, 4)
                            logger.info(f"  Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.error("  ❌ WebSocket Server failed to bind after all retries")
                            return False
                else:
                    # Process crashed during startup
                    logger.warning("  Server process crashed during startup")
                    if retry < max_retries - 1:
                        wait_time = 2 ** min(retry, 4)
                        logger.info(f"  Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("  ❌ WebSocket Server failed to start after all retries")
                        return False

            except Exception as e:
                logger.warning(f"  Error starting server: {e}")
                if retry < max_retries - 1:
                    wait_time = 2 ** min(retry, 4)
                    logger.info(f"  Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"  ❌ Failed to start WebSocket Server after all retries: {e}")
                    return False

        # If we exhausted all retries via continue statements
        logger.error("  ❌ WebSocket Server failed to start after all retries")
        return False

    async def start_conversation_watcher(self) -> bool:
        """Start conversation watcher."""
        logger.info("[3/5] Starting Conversation Watcher...")

        try:
            watcher_script = MIND_PROTOCOL_ROOT / "orchestration" / "services" / "watchers" / "conversation_watcher.py"

            if not watcher_script.exists():
                logger.error(f"  ❌ Script not found: {watcher_script}")
                return False

            process = subprocess.Popen(
                [sys.executable, str(watcher_script)]
                # Don't capture stdout - let it go to parent to avoid pipe buffer deadlock
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

    async def start_stimulus_injection(self) -> bool:
        """Start Stimulus Injection service (port 8001)."""
        logger.info("[4/7] Starting Stimulus Injection Service...")

        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "orchestration.services.stimulus_injection_service"],
                cwd=MIND_PROTOCOL_ROOT
            )

            self.processes['stimulus_injection'] = process

            # Give it a moment to start and bind port
            await asyncio.sleep(2)

            if process.poll() is None:
                logger.info("  ✅ Stimulus Injection Service started (port 8001)")
                return True
            else:
                logger.error("  ❌ Stimulus Injection Service failed to start")
                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start Stimulus Injection: {e}")
            return False

    async def start_signals_collector(self) -> bool:
        """Start Signals Collector service (port 8010)."""
        logger.info("[5/7] Starting Signals Collector Service...")

        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "orchestration.services.signals_collector"],
                cwd=MIND_PROTOCOL_ROOT
            )

            self.processes['signals_collector'] = process

            # Give it a moment to start and bind port
            await asyncio.sleep(2)

            if process.poll() is None:
                logger.info("  ✅ Signals Collector started (port 8010)")
                return True
            else:
                logger.error("  ❌ Signals Collector failed to start")
                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start Signals Collector: {e}")
            return False

    async def start_autonomy_orchestrator(self) -> bool:
        """Start Autonomy Orchestrator service (port 8002)."""
        logger.info("[5/7] Starting Autonomy Orchestrator...")

        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "orchestration.services.autonomy_orchestrator"],
                cwd=MIND_PROTOCOL_ROOT
            )

            self.processes['autonomy_orchestrator'] = process

            # Give it a moment to start and bind port
            await asyncio.sleep(2)

            if process.poll() is None:
                logger.info("  ✅ Autonomy Orchestrator started (port 8002)")
                return True
            else:
                logger.error("  ❌ Autonomy Orchestrator failed to start")
                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start Autonomy Orchestrator: {e}")
            return False

    async def start_queue_poller(self) -> bool:
        """
        Start Queue Poller service (no port - file-based).

        Priority: P0 - Critical path to autonomy
        Drains .stimuli/queue.jsonl and injects into consciousness engines.
        """
        logger.info("[6/8] Starting Queue Poller (P0 - Ambient Signals Bridge)...")

        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "orchestration.services.queue_poller"],
                cwd=MIND_PROTOCOL_ROOT
            )

            self.processes['queue_poller'] = process

            # Give it a moment to start and write heartbeat
            await asyncio.sleep(2)

            if process.poll() is None:
                logger.info("  ✅ Queue Poller started (draining queue → engines)")
                return True
            else:
                logger.error("  ❌ Queue Poller failed to start")
                return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start Queue Poller: {e}")
            return False

    async def start_consciousness_engine(self) -> bool:
        """
        Start consciousness engine (OBSOLETE - now handled by websocket_server.py).

        Consciousness engines are now created and registered INSIDE the websocket server
        process on startup, ensuring the control API can see them.
        """
        logger.info("[4/5] Consciousness Engine...")
        logger.info("  ⏭️  Skipped (engines load inside websocket server)")
        return True

    async def start_dashboard(self) -> bool:
        """Start Next.js dashboard with retry logic for port binding."""
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

            # Retry loop with active port verification (no blind wait)
            # The retry loop below will check if port is free and wait only if needed
            max_retries = 10
            for retry in range(max_retries):
                # Step 3: Verify port is actually free before attempting bind
                if not await self._verify_port_free(3000):
                    if retry < max_retries - 1:
                        wait_time = 2 ** min(retry, 4)  # 1s, 2s, 4s, 8s, 16s max
                        logger.warning(f"  Port 3000 still in use, retrying in {wait_time}s... (attempt {retry + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("  ❌ Port 3000 still occupied after all retries!")
                        return False

                logger.info(f"  Port 3000 verified free, starting dashboard... (attempt {retry + 1}/{max_retries})")

                # Step 4: Start dashboard with FORCED port 3000 (hardcoded in package.json)
                # Port 3000 is hardcoded in package.json: "dev": "next dev -p 3000"
                process = subprocess.Popen(
                    "npm run dev",
                    cwd=str(dashboard_dir),
                    shell=True
                    # Don't capture stdout - let it go to parent to avoid pipe buffer deadlock
                )

                self.processes['dashboard'] = process

                # Step 5: Monitor startup for port drift
                logger.info("  Monitoring startup (allowing for Next.js build time)...")
                startup_timeout = 45  # seconds - Next.js builds can take 30-60s
                start_time = asyncio.get_event_loop().time()

                while (asyncio.get_event_loop().time() - start_time) < startup_timeout:
                    if process.poll() is not None:
                        # Dashboard crashed during startup
                        logger.warning("  Dashboard crashed during startup")
                        if retry < max_retries - 1:
                            wait_time = 2 ** min(retry, 4)
                            logger.info(f"  Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            break
                        else:
                            logger.error("  ❌ Dashboard failed to start after all retries")
                            return False

                    await asyncio.sleep(0.5)

                    # If process still running after timeout, check port binding
                    if (asyncio.get_event_loop().time() - start_time) >= startup_timeout:
                        break

                # If process crashed, continue to next retry
                if process.poll() is not None:
                    continue

                # Step 6: Verify dashboard bound to port 3000 (not drifted)
                await asyncio.sleep(2)  # Give it moment to bind

                if await self._verify_port_in_use(3000):
                    logger.info("  ✅ Dashboard started successfully on port 3000 (http://localhost:3000)")
                    return True
                else:
                    # Port drift detected or binding failed
                    logger.warning("  Dashboard started but NOT bound to port 3000")

                    # Kill the process
                    try:
                        process.terminate()
                        await asyncio.sleep(1)
                        if process.poll() is None:
                            process.kill()
                    except Exception:
                        pass

                    if retry < max_retries - 1:
                        wait_time = 2 ** min(retry, 4)
                        logger.info(f"  Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("  ❌ Dashboard failed to bind to port 3000 after all retries")
                        return False

            # If we exhausted all retries via continue/break statements
            logger.error("  ❌ Dashboard failed to start after all retries")
            return False

        except Exception as e:
            logger.error(f"  ❌ Failed to start Dashboard: {e}")
            return False

    async def _cleanup_existing_processes(self):
        """Kill any existing Mind Protocol processes by clearing ALL critical ports."""
        # Critical ports that MUST be cleared before startup
        critical_ports = {
            8000: 'WebSocket Server',
            8001: 'Stimulus Injection',
            8002: 'Autonomy Orchestrator',
            8010: 'Signals Collector',
            3000: 'Next.js Dashboard'
        }

        killed_count = 0

        logger.info("  Clearing critical ports...")
        for port, service in critical_ports.items():
            killed = await self._kill_port(port)
            if killed > 0:
                logger.info(f"  Killed {killed} process(es) on port {port} ({service})")
                killed_count += killed

        if killed_count == 0:
            logger.info("  ✅ All critical ports already clear")
        else:
            logger.info(f"  ✅ Cleared {killed_count} process(es) from critical ports")
            await asyncio.sleep(2)  # Give OS time to release resources

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
            # Use asyncio.create_subprocess_exec instead of subprocess.run to avoid blocking event loop
            process = await asyncio.create_subprocess_exec(
                "netstat", "-ano",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)
            result_stdout = stdout.decode("utf-8", errors="ignore")

            # Check if port appears in LISTENING state
            for line in result_stdout.split('\n'):
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
            for py_file in orchestration_dir.rglob("*.py"):
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

        Can be disabled via MP_HOT_RELOAD=0 environment variable (default: disabled for stability).
        """
        # Feature flag: disable hot-reload by default for stability (spawn loop prevention)
        hot_reload_enabled = os.getenv("MP_HOT_RELOAD", "0") == "1"

        if not hot_reload_enabled:
            logger.info("[Guardian] Hot-reload DISABLED (set MP_HOT_RELOAD=1 to enable)")
            return  # Exit monitoring entirely when disabled

        logger.info("[Guardian] Starting code change monitor (hot-reload ENABLED)")

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

                # Cooldown check - prevent restart thrashing
                now = time.time()
                last = self._last_hot_restart_ts.get(service_name, 0.0)
                if now - last < self._min_hot_restart_interval_sec:
                    logger.info(f"[Guardian] ⏳ Skipping {service_name} restart (cooldown: {now - last:.1f}s < {self._min_hot_restart_interval_sec}s)")
                    continue
                self._last_hot_restart_ts[service_name] = now

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

    async def monitor_service_health(self, service_name: str, port: int,
                                     memory_threshold_mb: int = 800,
                                     connection_threshold: int = 20,
                                     check_interval_sec: int = 30):
        """
        Monitor service health and auto-restart if unhealthy.

        Generic health monitor for any Mind Protocol service. Detects:
        - Memory usage exceeding threshold (memory leaks)
        - Connection leaks (CLOSE_WAIT accumulation)
        - Service hangs requiring manual intervention

        On unhealthy status, kills process and lets monitor_processes() restart.

        Args:
            service_name: Name of service in self.processes (e.g., 'dashboard', 'websocket_server')
            port: Port the service binds to
            memory_threshold_mb: Memory limit in MB before restart (default: 800)
            connection_threshold: Max CLOSE_WAIT connections before restart (default: 20)
            check_interval_sec: Seconds between health checks (default: 30)
        """
        logger.info(f"[Guardian] Starting health monitor for {service_name}")
        logger.info(f"[Guardian]   Port: {port}")
        logger.info(f"[Guardian]   Thresholds: Memory >{memory_threshold_mb}MB, Connections >{connection_threshold} CLOSE_WAIT")
        logger.info(f"[Guardian]   Check interval: {check_interval_sec}s")

        # Wait for service to fully start before monitoring
        await asyncio.sleep(60)

        while self.running:
            await asyncio.sleep(check_interval_sec)

            # Only monitor if service is running
            if service_name not in self.processes:
                continue

            process = self.processes[service_name]
            if process.poll() is not None:
                # Service already dead, monitor_processes() will handle it
                continue

            try:
                # Check service health
                is_healthy, status = check_dashboard_health(port=port)

                if is_healthy:
                    logger.debug(f"[Guardian] {service_name} health: {status}")
                else:
                    # Service unhealthy - trigger restart
                    logger.warning(f"[Guardian] 🏥 {service_name.upper()} UNHEALTHY: {status}")
                    logger.warning(f"[Guardian] Triggering auto-restart...")

                    # Send notification about unhealthy service
                    self.notifier.notify_critical(
                        f"{service_name.upper()} Unhealthy",
                        f"{status}\nAuto-restarting service..."
                    )

                    # Kill the service process
                    pid = get_process_on_port(port)
                    if pid:
                        try:
                            subprocess.run(
                                ["taskkill", "/F", "/PID", str(pid)],
                                capture_output=True,
                                timeout=5
                            )
                            logger.info(f"[Guardian] ✅ Killed unhealthy {service_name} (PID {pid})")
                            logger.info(f"[Guardian] Monitor will restart {service_name} in ~5s")

                            # Send notification about successful kill and pending restart
                            self.notifier.notify_info(
                                f"{service_name.capitalize()} Restarting",
                                f"Service killed (PID {pid}). Restarting automatically..."
                            )

                            # Wait longer after restart to allow clean startup
                            await asyncio.sleep(60)

                        except Exception as e:
                            logger.error(f"[Guardian] Failed to kill {service_name}: {e}")
                    else:
                        logger.warning(f"[Guardian] Could not find {service_name} PID on port {port}")

            except Exception as e:
                logger.error(f"[Guardian] {service_name} health check error: {e}")

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
                        'stimulus_injection',
                        'signals_collector',
                        'autonomy_orchestrator',
                        'queue_poller',
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

                        # Send notification about rogue process kill
                        self.notifier.notify_info(
                            "Rogue Process Killed",
                            f"PID {pid} was running outside launcher control and has been terminated"
                        )

                    except Exception as e:
                        logger.error(f"[Guardian] Failed to kill rogue {pid}: {e}")

    def _check_service_health(self, name: str, process) -> tuple[bool, str]:
        """
        Check if service is healthy (process alive + functional).

        Victor "The Resurrector" Fix - 2025-10-24
        Returns (is_healthy, reason_if_unhealthy)
        """
        # Check 1: Process alive
        if process.poll() is not None:
            return (False, f"Process terminated (exit code: {process.returncode})")

        # Check 2: Functional verification (port binding)
        import socket
        port_checks = {
            'websocket_server': 8000,
            'dashboard': 3000,
            'stimulus_injection': 8001,
            'signals_collector': 8010,
            'autonomy_orchestrator': 8002
        }

        if name in port_checks:
            port = port_checks[name]
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result != 0:
                    return (False, f"Port {port} not bound (process alive but service degraded)")
            except Exception as e:
                return (False, f"Port check failed: {e}")

        return (True, "")

    async def monitor_processes(self):
        """Monitor processes and restart on crash or degradation with exponential backoff."""
        while self.running:
            await asyncio.sleep(5)

            for name, process in list(self.processes.items()):
                # Check both process death AND service degradation
                is_healthy, failure_reason = self._check_service_health(name, process)

                if is_healthy:
                    # Service healthy - reset crash counter
                    if name in self._consecutive_crashes and self._consecutive_crashes[name] > 0:
                        logger.info(f"[Guardian] ✅ {name} recovered - resetting crash counter")
                        self._consecutive_crashes[name] = 0
                    continue

                # Service unhealthy - apply exponential backoff
                logger.error(f"❌ {name} unhealthy: {failure_reason}")

                # Calculate backoff delay based on consecutive crashes
                crash_count = self._consecutive_crashes.get(name, 0)
                backoff_delay = 2 ** min(crash_count, 5)  # Max 32 seconds

                # Check if enough time has passed since last crash restart
                now = time.time()
                last_restart = self._last_crash_restart.get(name, 0)
                time_since_restart = now - last_restart

                if time_since_restart < backoff_delay:
                    wait_remaining = backoff_delay - time_since_restart
                    logger.info(f"[Guardian] ⏳ {name} backoff: waiting {wait_remaining:.0f}s (attempt #{crash_count + 1})")
                    continue

                # Enough time passed - attempt restart
                self._consecutive_crashes[name] = crash_count + 1
                self._last_crash_restart[name] = now

                # Send notification about failure
                self.notifier.notify_critical(
                    f"{name.capitalize()} Unhealthy",
                    f"{failure_reason}\nAttempting restart (attempt #{crash_count + 1})..."
                )

                # Auto-restart
                logger.info(f"🔄 Restarting {name} (crash #{crash_count + 1}, backoff was {backoff_delay}s)...")

                success = False
                if name == 'websocket_server':
                    success = await self.start_websocket_server()
                elif name == 'conversation_watcher':
                    success = await self.start_conversation_watcher()
                elif name == 'stimulus_injection':
                    success = await self.start_stimulus_injection()
                elif name == 'signals_collector':
                    success = await self.start_signals_collector()
                elif name == 'autonomy_orchestrator':
                    success = await self.start_autonomy_orchestrator()
                elif name == 'queue_poller':
                    success = await self.start_queue_poller()
                elif name == 'consciousness_engine':
                    success = await self.start_consciousness_engine()
                elif name == 'dashboard':
                    success = await self.start_dashboard()

                if not success:
                    logger.error(f"❌ Failed to restart {name} - will retry with backoff")
                    # Send warning about failed restart
                    self.notifier.notify_warning(
                        f"{name.capitalize()} Restart Failed",
                        f"Will retry with exponential backoff (next: {2 ** min(crash_count + 1, 5)}s)"
                    )
                    # Leave failed process in dict - next cycle will detect it's still dead and retry with backoff
                else:
                    logger.info(f"✅ Successfully restarted {name}")
                    # Reset crash counter on successful restart
                    self._consecutive_crashes[name] = 0
                    # Send info about successful restart
                    self.notifier.notify_info(
                        f"{name.capitalize()} Recovered",
                        f"Service successfully restarted and operational"
                    )

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
    parser.add_argument(
        "--disable-notifications",
        action="store_true",
        help="Disable Windows notifications for Guardian events"
    )
    args = parser.parse_args()

    # Default is full system (with dashboard), --core-only disables it
    # Notifications enabled by default, --disable-notifications turns them off
    manager = ProcessManager(
        full_system=not args.core_only,
        notifications_enabled=not args.disable_notifications
    )

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
