"""
MPSv3 Singleton Lease - OS-level singleton that auto-releases on process death.

Eliminates stale lock files by using OS primitives:
- Windows: CreateMutex (auto-released on process exit)
- POSIX: flock (auto-released on process exit)

Author: Atlas
Date: 2025-10-25
"""

import os
import platform
from pathlib import Path


class SingletonLease:
    """OS-level singleton that auto-releases on process death."""

    def __init__(self, name: str = "MPSv3_Supervisor"):
        self.name = name
        self.handle = None
        self._acquired = False

    def acquire(self) -> bool:
        """Acquire singleton lease. Returns True if acquired, False if already held."""
        if platform.system() == "Windows":
            return self._acquire_windows()
        else:
            return self._acquire_posix()

    def _acquire_windows(self) -> bool:
        """Windows: CreateMutex (auto-released on process exit)."""
        import ctypes

        kernel32 = ctypes.windll.kernel32
        mutex_name = f"Global\\{self.name}"

        # CreateMutexW(lpMutexAttributes, bInitialOwner, lpName)
        self.handle = kernel32.CreateMutexW(None, True, mutex_name)
        error = kernel32.GetLastError()

        if error == 183:  # ERROR_ALREADY_EXISTS
            print(f"[SingletonLease] Another instance holds lease: {mutex_name}")
            return False

        self._acquired = True
        print(f"[SingletonLease] Acquired Windows mutex: {mutex_name}")
        return True

    def _acquire_posix(self) -> bool:
        """POSIX: flock (auto-released on process exit)."""
        import fcntl

        lock_path = Path(f"/tmp/{self.name}.lock")
        self.handle = open(lock_path, "w")

        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._acquired = True
            self.handle.write(str(os.getpid()))
            self.handle.flush()
            print(f"[SingletonLease] Acquired POSIX flock: {lock_path}")
            return True
        except BlockingIOError:
            print(f"[SingletonLease] Another instance holds lease: {lock_path}")
            return False

    def release(self):
        """Explicitly release lease (optional - OS auto-releases on death)."""
        if not self._acquired:
            return

        if platform.system() == "Windows":
            import ctypes
            if self.handle:
                ctypes.windll.kernel32.ReleaseMutex(self.handle)
                ctypes.windll.kernel32.CloseHandle(self.handle)
        else:
            import fcntl
            if self.handle:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
                self.handle.close()

        self._acquired = False
        print("[SingletonLease] Released")

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Failed to acquire singleton lease - another MPSv3 instance is running")
        return self

    def __exit__(self, *args):
        self.release()
