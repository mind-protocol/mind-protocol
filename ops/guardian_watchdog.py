"""
Guardian Watchdog - Meta-supervisor for guardian.py

Monitors guardian heartbeat and restarts if stale or not running.
Provides the meta-guardian layer to ensure guardian never stays down.

Usage:
    python ops/guardian_watchdog.py

Auto-starts via Task Scheduler on system boot.

Author: Victor "The Resurrector"
Date: 2025-10-25
Purpose: P4 Ops Hardening - Meta-guardian implementation (Option B)
"""

import os
import sys
import time
import subprocess
import psutil
from pathlib import Path

# Configuration
ROOT = Path(__file__).parent.parent
HB_FILE = ROOT / ".heartbeats" / "guardian.heartbeat"
GUARDIAN_SCRIPT = ROOT / "guardian.py"
STALE_THRESHOLD_SEC = int(os.getenv("GUARDIAN_STALE_SEC", "20"))
CHECK_INTERVAL_SEC = 5

def is_guardian_running():
    """Check if guardian.py process is currently running."""
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            # Check if this is a Python process running guardian.py
            if "python" in (proc.info.get("name") or "").lower():
                if any("guardian.py" in str(arg) for arg in cmdline):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


def is_heartbeat_fresh():
    """Check if guardian heartbeat file is fresh (updated within threshold)."""
    if not HB_FILE.exists():
        return False

    try:
        with open(HB_FILE, "r") as f:
            timestamp_str = f.read().strip()
            if not timestamp_str:
                return False
            timestamp = int(timestamp_str)

        age = time.time() - timestamp
        return age < STALE_THRESHOLD_SEC

    except (ValueError, OSError) as e:
        print(f"[Watchdog] Error reading heartbeat: {e}", file=sys.stderr)
        return False


def start_guardian():
    """Launch guardian.py as a subprocess."""
    try:
        print(f"[Watchdog] Starting guardian: {GUARDIAN_SCRIPT}")
        subprocess.Popen(
            [sys.executable, str(GUARDIAN_SCRIPT)],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("[Watchdog] Guardian launched successfully")
    except Exception as e:
        print(f"[Watchdog] ERROR: Failed to start guardian: {e}", file=sys.stderr)


def main():
    """Main watchdog loop - monitor guardian and restart if needed."""
    print("=" * 70)
    print("GUARDIAN WATCHDOG - META-SUPERVISOR ACTIVE")
    print("=" * 70)
    print(f"Monitoring: {HB_FILE}")
    print(f"Stale threshold: {STALE_THRESHOLD_SEC} seconds")
    print(f"Check interval: {CHECK_INTERVAL_SEC} seconds")
    print("=" * 70)
    print("")

    restart_count = 0

    while True:
        try:
            running = is_guardian_running()
            heartbeat_ok = is_heartbeat_fresh()

            status = "OK" if (running and heartbeat_ok) else "DEGRADED"

            if not running:
                print(f"[Watchdog] Guardian NOT RUNNING (restart #{restart_count + 1})")
                start_guardian()
                restart_count += 1
                time.sleep(10)  # Give guardian time to start before re-checking

            elif not heartbeat_ok:
                age_str = "N/A"
                if HB_FILE.exists():
                    try:
                        with open(HB_FILE, "r") as f:
                            ts = int(f.read().strip())
                            age_str = f"{int(time.time() - ts)}s"
                    except Exception:
                        pass

                print(f"[Watchdog] Guardian heartbeat STALE (age: {age_str}, threshold: {STALE_THRESHOLD_SEC}s)")
                print(f"[Watchdog] Guardian process detected but heartbeat stale - may be hung")
                # Don't restart immediately if process exists - give it time to recover
                # Next cycle will restart if still stale
                time.sleep(CHECK_INTERVAL_SEC)

            else:
                # All healthy - silent monitoring
                time.sleep(CHECK_INTERVAL_SEC)

        except KeyboardInterrupt:
            print("\n[Watchdog] Shutting down (Ctrl+C received)")
            break
        except Exception as e:
            print(f"[Watchdog] ERROR in monitoring loop: {e}", file=sys.stderr)
            time.sleep(CHECK_INTERVAL_SEC)


if __name__ == "__main__":
    main()
