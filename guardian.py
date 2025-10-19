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
"""

import subprocess
import sys
import time
import logging
import os
from pathlib import Path

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


def main():
    """Forever loop that restarts launcher on crash."""

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
    logger.info("Press Ctrl+C to stop guardian (will restart on next boot)")
    logger.info("To permanently uninstall: python guardian.py --uninstall")
    logger.info("=" * 70)

    restart_count = 0

    while True:
        # Defensive: clean up stale launcher lock if present
        try:
            lock = MIND_PROTOCOL_ROOT / ".launcher.lock"
            if lock.exists():
                lock.unlink()
                logger.info("Removed stale .launcher.lock before launch")
        except Exception as e:
            logger.warning(f"Could not remove .launcher.lock: {e}")

        if restart_count == 0:
            logger.info("Starting Mind Protocol launcher...")
        else:
            logger.info(f"Restarting launcher (crash #{restart_count})...")

        try:
            # Start launcher with pinned WS_PORT for uvicorn
            env = os.environ.copy()
            env.setdefault("WS_PORT", "8000")  # Pin WS server port
            env.setdefault("DASHBOARD_PORT", "3000")  # Pin dashboard port

            process = subprocess.run(
                [sys.executable, str(LAUNCHER_SCRIPT)],
                check=False,  # Don't raise on non-zero exit
                env=env
            )

            exit_code = process.returncode

            if exit_code == 0:
                logger.info("Launcher exited cleanly (exit code 0)")
                logger.info("Guardian stopping (clean shutdown)")
                break  # Clean exit, don't restart
            else:
                logger.error(f"Launcher crashed (exit code {exit_code})")
                restart_count += 1

                # Exponential backoff to prevent rapid restart loops
                wait_time = min(30, 2 ** min(restart_count, 5))
                logger.warning(f"Waiting {wait_time}s before restart...")
                time.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info("")
            logger.info("Guardian shutdown requested (Ctrl+C)")
            logger.info("Note: Guardian will restart on next system boot")
            break

        except Exception as e:
            logger.error(f"Guardian error: {e}")
            time.sleep(10)

    logger.info("Guardian exiting")
    return 0


if __name__ == "__main__":
    # Handle --uninstall flag
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        logger.info("Uninstalling guardian from scheduled tasks...")
        uninstall_scheduled_task()
        sys.exit(0)

    sys.exit(main())
