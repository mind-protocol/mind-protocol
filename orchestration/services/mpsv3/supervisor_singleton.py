"""
MPSv3 PID File Singleton - Atomic PID-based singleton enforcement.

Replaces Windows mutex with more reliable PID file approach:
- Atomic file creation (O_CREAT|O_EXCL) prevents race conditions
- Process liveness verification prevents stale locks
- Cmdline verification prevents PID reuse false positives
- Automatic cleanup on exit via atexit

Author: Victor "The Resurrector" (based on Nicolas's implementation plan)
Date: 2025-10-26
Phase: Cascade Prevention Implementation
"""

import os
import json
import uuid
import time
import atexit
import sys
from pathlib import Path


# Lock file path
LOCK_DIR = Path(".locks")
LOCK_DIR.mkdir(parents=True, exist_ok=True)
PID_PATH = LOCK_DIR / "mpsv3_supervisor.pid"


def _proc_alive_matches(pid: int, expect: str | None = None) -> bool:
    """
    Check if process is alive and matches expected command line.

    Uses psutil for robust process checking with cmdline verification
    to avoid PID reuse false positives.
    """
    try:
        import psutil
        p = psutil.Process(pid)

        # Zombie processes are effectively dead
        if p.status() == psutil.STATUS_ZOMBIE:
            return False

        # Verify cmdline contains expected string (prevents PID reuse)
        if expect:
            cmdline_str = " ".join(p.cmdline())
            if expect not in cmdline_str:
                return False

        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
        # If we can't verify, assume dead (safe default)
        return False


def acquire_singleton() -> bool:
    """
    Acquire singleton lease via atomic PID file creation.

    Returns:
        True if lease acquired successfully
        False if another instance is already running

    Exits with code 0 if another instance is confirmed running.
    """
    # Try atomic create
    try:
        fd = os.open(str(PID_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        # PID file exists - check if it's stale or valid
        try:
            with open(PID_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)

            pid = int(meta.get("pid", -1))
            cmdline_hint = meta.get("cmdline", "")

            # Check if that PID is still alive and running supervisor
            if pid > 0 and _proc_alive_matches(pid, expect="mpsv3_supervisor"):
                print(f"[PIDSingleton] Another supervisor already running (PID {pid}). Exiting.",
                      file=sys.stderr)
                sys.exit(0)  # Clean exit - this is expected behavior
            else:
                print(f"[PIDSingleton] Stale PID file detected (PID {pid} not running). Reclaiming lock.")
                try:
                    os.remove(PID_PATH)
                except Exception as e:
                    print(f"[PIDSingleton] Warning: Could not remove stale lock: {e}", file=sys.stderr)
        except (json.JSONDecodeError, ValueError, Exception) as e:
            # Corrupt lock file - reclaim
            print(f"[PIDSingleton] Corrupt PID file detected: {e}. Reclaiming lock.")
            try:
                os.remove(PID_PATH)
            except Exception:
                pass

        # Retry atomic create after cleanup
        try:
            fd = os.open(str(PID_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            # Race condition - another process won
            print("[PIDSingleton] Another supervisor acquired lock during reclaim. Exiting.",
                  file=sys.stderr)
            sys.exit(0)

    # Write PID file metadata
    instance_uuid = str(uuid.uuid4())
    metadata = {
        "pid": os.getpid(),
        "start_ts": time.time(),
        "cmdline": " ".join(sys.argv),
        "instance_uuid": instance_uuid,
        "hostname": os.environ.get("COMPUTERNAME", os.environ.get("HOSTNAME", "unknown"))
    }

    metadata_json = json.dumps(metadata, indent=2)
    os.write(fd, metadata_json.encode("utf-8"))
    os.close(fd)

    print(f"[PIDSingleton] Acquired lock (PID {os.getpid()}, UUID {instance_uuid[:8]}...)")

    # Register cleanup on exit
    def _cleanup():
        """Remove PID file only if it still points to this instance."""
        try:
            if not PID_PATH.exists():
                return

            with open(PID_PATH, "r", encoding="utf-8") as f:
                current_meta = json.load(f)

            # Only remove if it's still our PID (prevents removing successor's lock)
            if int(current_meta.get("pid", -1)) == os.getpid():
                os.remove(PID_PATH)
                print(f"[PIDSingleton] Released lock (PID {os.getpid()})")
        except Exception as e:
            print(f"[PIDSingleton] Warning: Cleanup failed: {e}", file=sys.stderr)

    atexit.register(_cleanup)

    return True


def check_singleton_health() -> dict:
    """
    Check singleton lock status (for monitoring/debugging).

    Returns dict with:
        - locked: bool (is lock file present)
        - pid: int | None (locked process PID)
        - alive: bool (is that process still running)
        - stale: bool (lock exists but process dead)
    """
    if not PID_PATH.exists():
        return {"locked": False, "pid": None, "alive": False, "stale": False}

    try:
        with open(PID_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)

        pid = int(meta.get("pid", -1))
        alive = _proc_alive_matches(pid, expect="mpsv3_supervisor")

        return {
            "locked": True,
            "pid": pid,
            "alive": alive,
            "stale": not alive,
            "metadata": meta
        }
    except Exception as e:
        return {
            "locked": True,
            "pid": None,
            "alive": False,
            "stale": True,
            "error": str(e)
        }
