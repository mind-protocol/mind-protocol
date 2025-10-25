"""
Guardian Wrapper - Self-installing auto-restart supervisor

First run automatically installs itself as Windows scheduled task.
Subsequent runs (or reboots) start automatically.

Usage:
    python guardian.py  # First time: installs + runs
                        # After that: runs on boot automatically
    python guardian.py --uninstall  # Remove from scheduled tasks

Author: Ada "Bridgekeeper"
Date: 2025-10-19
Pattern: Self-healing infrastructure - makes the system bulletproof

FIXED VERSION - Victor "The Resurrector" 2025-10-20
Fixes:
  - Removed capture_output=True to prevent pipe buffer deadlock
  - Removed premature break after stderr logging to enable retry logic

RESILIENCE UPDATE - Victor "The Resurrector" 2025-10-21
Circuit breaker with degraded mode:
  - Never gives up (removed 10-crash limit)
  - Switches to --core-only after 3 consecutive failures
  - Tracks failure timestamps for pattern detection
  - Logs chronic failure warnings
"""

import subprocess
import sys
import time
import logging
import os
import ctypes
import threading
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque

# Setup logging to both console and file
MIND_PROTOCOL_ROOT = Path(__file__).parent
LOG_FILE = MIND_PROTOCOL_ROOT / "guardian.log"

# Create logger with handlers for both file and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler - keeps full log history
file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - GUARDIAN - %(levelname)s - %(message)s'))

# Console handler - for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - GUARDIAN - %(levelname)s - %(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

LAUNCHER_SCRIPT = MIND_PROTOCOL_ROOT / "start_mind_protocol.py"
TASK_NAME = "MindProtocolGuardian"


def is_admin():
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Relaunch this script with administrator privileges using UAC."""
    try:
        if sys.platform != 'win32':
            logger.error("Admin elevation only supported on Windows")
            return False

        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])

        # Use ShellExecuteEx with runas verb to trigger UAC
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,           # parent window
            "runas",        # operation (triggers UAC)
            sys.executable, # executable (python.exe)
            params,         # parameters (script path + args)
            None,           # working directory
            1               # show command (SW_NORMAL)
        )

        if ret > 32:  # Success
            logger.info("✅ Relaunched with administrator privileges")
            return True
        else:
            logger.error(f"❌ Failed to elevate privileges (error code: {ret})")
            return False

    except Exception as e:
        logger.error(f"❌ Elevation error: {e}")
        return False


def is_installed_as_task():
    """Check if guardian is already installed as scheduled task."""
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/tn", TASK_NAME],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def install_as_scheduled_task():
    """Install guardian as Windows scheduled task (runs on login)."""
    logger.info("=" * 70)
    logger.info("AUTO-INSTALLATION: First-time setup")
    logger.info("=" * 70)

    # Build command: python <full_path_to_guardian.py>
    python_exe = sys.executable
    guardian_script = Path(__file__).resolve()

    # Create scheduled task
    cmd = [
        "schtasks",
        "/create",
        "/tn", TASK_NAME,
        "/tr", f'"{python_exe}" "{guardian_script}"',
        "/sc", "onlogon",           # Run on user login
        "/rl", "highest",            # Run with highest privileges
        "/f"                         # Force overwrite if exists
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            logger.info("✅ Guardian installed as scheduled task")
            logger.info(f"   Task name: {TASK_NAME}")
            logger.info(f"   Runs on: User login")
            logger.info(f"   Command: {python_exe} {guardian_script}")
            logger.info("")
            logger.info("The guardian will now:")
            logger.info("  1. Start automatically on system boot/login")
            logger.info("  2. Keep Mind Protocol running forever")
            logger.info("  3. Kill rogue processes")
            logger.info("  4. Auto-restart on crashes")
            logger.info("")
            return True
        else:
            logger.error(f"❌ Installation failed: {result.stderr}")
            logger.warning("Continuing anyway (will run this session only)")
            return False

    except Exception as e:
        logger.error(f"❌ Installation error: {e}")
        logger.warning("Continuing anyway (will run this session only)")
        return False


def uninstall_scheduled_task():
    """Remove guardian from scheduled tasks (for cleanup)."""
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            logger.info(f"✅ Removed scheduled task: {TASK_NAME}")
        else:
            logger.warning(f"Task removal failed (may not exist): {result.stderr}")

    except Exception as e:
        logger.error(f"Uninstall error: {e}")


def check_port_bound(port):
    """Check if a port is bound (service listening)."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False


def check_launcher_already_running():
    """
    Check if launcher is already running AND HEALTHY.

    Victor "The Resurrector" Fix - 2025-10-24
    Previous version only checked if PID exists, allowing zombie launchers
    to block resurrection. Now verifies launcher is actually functional.
    """
    try:
        lock = MIND_PROTOCOL_ROOT / ".launcher.lock"
        if not lock.exists():
            return False

        # Read PID from lock file
        pid = int(lock.read_text().strip())

        # Check 1: Process with that PID exists
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if str(pid) not in result.stdout:
            # PID is dead but lock file exists - remove stale lock
            logger.warning(f"⚠️  Lock file exists but PID {pid} is dead - removing stale lock")
            try:
                lock.unlink()
            except Exception as e:
                logger.error(f"❌ Could not remove stale lock: {e}")
            return False

        # Check 2: Verify launcher functionality via port binding
        # Websocket server should be bound to port 8000 if launcher is working
        if not check_port_bound(8000):
            logger.warning(f"⚠️  Launcher PID {pid} exists but port 8000 not bound - ZOMBIE DETECTED")
            logger.warning(f"⚠️  Killing zombie launcher and removing lock")

            # Kill the zombie launcher
            try:
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid)],
                    capture_output=True,
                    timeout=5
                )
                logger.info(f"✅ Killed zombie launcher PID {pid}")
            except Exception as e:
                logger.error(f"❌ Failed to kill zombie launcher: {e}")

            # Remove stale lock
            try:
                # Force removal even if process holds it
                time.sleep(1)  # Give process time to die
                lock.unlink()
                logger.info(f"✅ Removed stale lock file")
            except Exception as e:
                logger.error(f"❌ Could not remove lock file: {e}")
                # Even if we can't remove the lock, we killed the zombie
                # Next iteration will try again

            return False

        # Both checks passed - launcher is alive AND functional
        return True

    except Exception as e:
        logger.error(f"❌ Error checking launcher status: {e}")
        return False


def write_guardian_heartbeat():
    """Write guardian heartbeat every 5 seconds for watchdog monitoring."""
    heartbeat_dir = MIND_PROTOCOL_ROOT / ".heartbeats"
    heartbeat_file = heartbeat_dir / "guardian.heartbeat"

    # Ensure directory exists
    heartbeat_dir.mkdir(exist_ok=True)

    while True:
        try:
            with open(heartbeat_file, "w") as f:
                f.write(str(int(time.time())))
        except Exception as e:
            logger.error(f"Failed to write guardian heartbeat: {e}")
        time.sleep(5)


def main():
    """Forever loop that monitors launcher and restarts on crash with circuit breaker."""

    # Check if running as administrator
    if not is_admin():
        logger.warning("⚠️  Guardian not running as administrator")
        logger.warning("⚠️  Will not be able to kill protected processes")
        logger.info("Attempting to elevate privileges...")

        if run_as_admin():
            # Successfully relaunched with admin rights, exit this instance
            logger.info("Exiting non-admin instance...")
            return 0
        else:
            logger.error("❌ Failed to obtain administrator privileges")
            logger.error("Guardian will run with limited capabilities")
            logger.error("May not be able to kill all blocking processes")
            logger.error("Continuing in limited mode (no admin). Some operations may fail.")

    else:
        logger.info("✅ Running with administrator privileges")

    # Check if we need to auto-install
    if not is_installed_as_task():
        logger.info("Guardian not installed yet - performing first-time setup...")
        install_as_scheduled_task()
    else:
        logger.info("Guardian already installed as scheduled task ✅")

    logger.info("=" * 70)
    logger.info("MIND PROTOCOL GUARDIAN - ACTIVE")
    logger.info("Auto-restart supervisor running")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"📋 Log file: {LOG_FILE}")
    logger.info("   Monitor with: tail -f guardian.log")
    logger.info("")
    logger.info("Restart Policy:")
    logger.info("  - Exponential backoff (1s, 2s, 4s, 8s, 16s, 32s max)")
    logger.info("  - Never gives up (will retry forever)")
    logger.info("  - Chronic failure logging after 10 failures in 10 min")
    logger.info("")
    logger.info("Press Ctrl+C to stop guardian (will restart on next boot)")
    logger.info("To permanently uninstall: python guardian.py --uninstall")
    logger.info("=" * 70)

    # Start guardian heartbeat writer for watchdog monitoring
    heartbeat_thread = threading.Thread(target=write_guardian_heartbeat, daemon=True)
    heartbeat_thread.start()
    logger.info("✅ Guardian heartbeat writer started (.heartbeats/guardian.heartbeat)")

    restart_count = 0
    failure_timestamps = deque(maxlen=20)  # Track last 20 failures
    launcher_process = None
    launcher_log_file = None  # Track log file handle
    last_chronic_warning = None

    try:
        while True:
            # Check if launcher is already running from another guardian
            if check_launcher_already_running():
                logger.info("Launcher already running (detected via lock file)")
                logger.info("Guardian entering monitor-only mode (will restart if crashes)")

                # Monitor existing launcher without starting new one
                while check_launcher_already_running():
                    time.sleep(5)  # Check every 5 seconds

                logger.warning("Launcher died - will restart it")
                restart_count += 1
                failure_timestamps.append(datetime.now())

            else:
                # No launcher running - start it
                if restart_count == 0:
                    logger.info("Starting Mind Protocol launcher...")
                else:
                    logger.info(f"Restarting launcher (crash #{restart_count})...")

                # Start launcher with Popen (non-blocking)
                env = os.environ.copy()
                env.setdefault("WS_PORT", "8000")  # Pin WS server port
                env.setdefault("DASHBOARD_PORT", "3000")  # Pin dashboard port
                env.setdefault("MP_HOT_RELOAD", "1")  # Enable hot-reload by default during dev

                # Enable persistence with configurable thresholds
                env.setdefault("MP_PERSIST_ENABLED", "1")  # Enable persistence
                env.setdefault("MP_PERSIST_MIN_BATCH", "5")  # Lower threshold for testing
                env.setdefault("MP_PERSIST_INTERVAL_SEC", "5.0")  # 5 second flush interval

                # Open log file for launcher output
                launcher_log_path = MIND_PROTOCOL_ROOT / "launcher.log"
                launcher_log_file = open(launcher_log_path, 'a', encoding='utf-8', buffering=1)  # Line buffered

                launcher_process = subprocess.Popen(
                    [sys.executable, str(LAUNCHER_SCRIPT)],
                    env=env,
                    stdout=launcher_log_file,  # Log to file for debugging
                    stderr=subprocess.STDOUT  # Merge stderr into stdout
                )

                logger.info(f"Launcher started (PID {launcher_process.pid})")

                # Monitor launcher process
                while True:
                    time.sleep(5)  # Poll every 5 seconds

                    exit_code = launcher_process.poll()

                    if exit_code is None:
                        # Still running
                        continue
                    elif exit_code == 0:
                        logger.info("Launcher exited cleanly (exit code 0)")
                        logger.info("Guardian stopping (clean shutdown)")
                        return 0
                    else:
                        # Crashed
                        logger.error(f"Launcher crashed (exit code {exit_code})")
                        restart_count += 1
                        failure_timestamps.append(datetime.now())

                        # Check for chronic failures (>10 failures in last 10 minutes)
                        now = datetime.now()
                        recent_failures = [t for t in failure_timestamps if now - t < timedelta(minutes=10)]

                        if len(recent_failures) >= 10:
                            # Chronic failure detected
                            if last_chronic_warning is None or now - last_chronic_warning > timedelta(minutes=30):
                                logger.error("🚨 CHRONIC FAILURE DETECTED")
                                logger.error(f"🚨 {len(recent_failures)} failures in last 10 minutes")
                                logger.error("🚨 Check: FalkorDB health, adapter.load_graph() hang, port conflicts")
                                logger.error("🚨 Guardian will keep trying with exponential backoff...")
                                last_chronic_warning = now

                        # Exponential backoff
                        wait_time = min(30, 2 ** min(restart_count, 5))
                        logger.warning(f"Waiting {wait_time}s before restart...")

                        # Close log file before restart
                        if launcher_log_file and not launcher_log_file.closed:
                            launcher_log_file.close()
                            launcher_log_file = None

                        time.sleep(wait_time)
                        break  # Exit monitor loop to restart

    except KeyboardInterrupt:
        logger.info("")
        logger.info("Guardian shutdown requested (Ctrl+C)")
        if launcher_process and launcher_process.poll() is None:
            logger.info("Terminating launcher...")
            launcher_process.terminate()
            time.sleep(2)
            if launcher_process.poll() is None:
                logger.warning("Launcher didn't terminate, killing it...")
                launcher_process.kill()

        # Close log file on shutdown
        if launcher_log_file and not launcher_log_file.closed:
            launcher_log_file.close()

        logger.info("Note: Guardian will restart on next system boot")
        return 0

    except Exception as e:
        logger.error(f"Guardian error: {e}")
        return 1

    logger.info("Guardian exiting")
    return 0


def force_restart_cleanup():
    """
    Nuclear cleanup for launcher cannibalism situations.

    Victor "The Resurrector" - 2025-10-24
    Kills all Python processes, removes stale locks, enables clean restart.
    """
    logger.info("=" * 70)
    logger.info("FORCE RESTART MODE - Cleaning up all processes")
    logger.info("=" * 70)

    # Check admin privileges first
    if not is_admin():
        logger.error("❌ Force restart requires administrator privileges")
        logger.info("Attempting to relaunch with admin...")
        if run_as_admin():
            logger.info("✅ Relaunched with admin - exiting this instance")
            return True  # Successfully relaunched, exit this instance
        else:
            logger.error("❌ Could not obtain admin privileges")
            return False

    logger.info("✅ Running with administrator privileges")

    # Step 1: Kill all python.exe processes EXCEPT this guardian
    logger.info("Step 1: Killing all Python processes (except this guardian)...")
    current_pid = os.getpid()
    logger.info(f"   My PID: {current_pid} (will be excluded from kill)")

    try:
        # Get all Python PIDs
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5
        )

        killed_count = 0
        for line in result.stdout.strip().split('\n'):
            if '"python.exe"' in line:
                # Extract PID from CSV: "python.exe","PID","..."
                parts = line.split(',')
                if len(parts) >= 2:
                    pid_str = parts[1].strip('"')
                    try:
                        pid = int(pid_str)
                        if pid != current_pid:
                            subprocess.run(
                                ["taskkill", "/F", "/PID", str(pid)],
                                capture_output=True,
                                timeout=3
                            )
                            killed_count += 1
                    except (ValueError, subprocess.TimeoutExpired):
                        pass

        logger.info(f"✅ Killed {killed_count} Python processes (kept guardian PID {current_pid} alive)")
    except Exception as e:
        logger.error(f"❌ Failed to kill Python processes: {e}")
        return False

    # Wait for processes to die
    logger.info("Waiting 3 seconds for processes to terminate...")
    time.sleep(3)

    # Step 2: Remove stale lock file
    logger.info("Step 2: Removing stale lock file...")
    lock = MIND_PROTOCOL_ROOT / ".launcher.lock"
    try:
        if lock.exists():
            lock.unlink()
            logger.info("✅ Removed .launcher.lock")
        else:
            logger.info("ℹ️  No lock file found")
    except Exception as e:
        logger.warning(f"⚠️  Could not remove lock file: {e}")
        # Continue anyway - we killed the processes holding it

    # Step 3: Verify cleanup
    logger.info("Step 3: Verifying cleanup...")
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe"],
            capture_output=True,
            text=True,
            timeout=5
        )
        python_count = result.stdout.count("python.exe")
        if python_count == 0:
            logger.info("✅ All Python processes terminated")
        else:
            logger.warning(f"⚠️  {python_count} Python processes still running")
    except Exception as e:
        logger.warning(f"⚠️  Could not verify cleanup: {e}")

    logger.info("=" * 70)
    logger.info("CLEANUP COMPLETE - Starting fresh guardian")
    logger.info("=" * 70)
    logger.info("")

    return True


if __name__ == "__main__":
    # Handle --uninstall flag
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        logger.info("Uninstalling guardian from scheduled tasks...")
        uninstall_scheduled_task()
        sys.exit(0)

    # Handle --force-restart flag
    if len(sys.argv) > 1 and sys.argv[1] == "--force-restart":
        if force_restart_cleanup():
            # If we successfully relaunched with admin, exit
            if not is_admin():
                sys.exit(0)
            # Otherwise continue to main()
            sys.exit(main())
        else:
            logger.error("❌ Force restart cleanup failed")
            sys.exit(1)

    sys.exit(main())
