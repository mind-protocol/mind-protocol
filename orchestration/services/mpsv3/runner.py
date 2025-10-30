"""
MPSv3 Service Runner - Process lifecycle management with process groups.

Manages service start/stop/restart with:
- Process groups (Windows Job Objects / POSIX setsid) for clean termination
- Exit code semantics (0/99/78/other)
- Exponential backoff with quarantine
- Clean shutdown

Author: Atlas
Date: 2025-10-25
"""

import os
import platform
import signal
import subprocess
import time
from dataclasses import dataclass
from typing import Optional, Dict, List

from .backoff import BackoffState, QuarantineRequired


@dataclass
class ServiceSpec:
    """Service specification loaded from YAML."""
    id: str
    cmd: List[str]
    env: Dict[str, str]
    cwd: Optional[str]
    criticality: str  # CRITICAL | CORE | OPTIONAL
    max_retries: int
    watched_files: List[str]
    depends_on: List[str]


class ServiceRunner:
    """Manages lifecycle of a single service with backoff and quarantine."""

    def __init__(self, spec: ServiceSpec):
        self.spec = spec
        self.process: Optional[subprocess.Popen] = None
        self.pgid: Optional[int] = None  # POSIX process group ID
        self.job_handle = None  # Windows Job object
        self.backoff = BackoffState(max_retries=spec.max_retries)
        self.quarantined = False
        self.started_at: Optional[float] = None  # Timestamp when service started


    def _mark_started(self):
        """Record service start time for uptime tracking."""
        self.started_at = time.time()

    def uptime(self) -> float:
        """Return service uptime in seconds (0.0 if not started)."""
        return 0.0 if not self.started_at else (time.time() - self.started_at)

    def start(self):
        """Start service in new process group."""
        if self.quarantined:
            print(f"[{self.spec.id}] Service quarantined, refusing to start")
            return

        if platform.system() == "Windows":
            self._start_windows()
        else:
            self._start_posix()

    def _merged_env(self) -> Dict[str, str]:
        """Merge OS environment with service-specific overrides.

        Critical for Windows: Preserves PATH, SystemRoot, COMSPEC, etc.
        Without this, children get empty env -> npm not found, Winsock init fails.
        """
        env = os.environ.copy()
        if self.spec.env:
            env.update(self.spec.env)
        return env

    def _start_windows(self):
        """Windows: CREATE_NEW_PROCESS_GROUP + Job Object."""
        import ctypes
        from ctypes import wintypes

        # Create Job Object to manage process tree
        self.job_handle = ctypes.windll.kernel32.CreateJobObjectW(None, None)

        # Configure Job to kill all processes when closed
        JOBOBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
        job_info = (wintypes.DWORD * 9)()
        job_info[2] = JOBOBJECT_LIMIT_KILL_ON_JOB_CLOSE
        ctypes.windll.kernel32.SetInformationJobObject(
            self.job_handle, 2, ctypes.byref(job_info), ctypes.sizeof(job_info)
        )

        # Spawn process in new process group
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        self.process = subprocess.Popen(
            self.spec.cmd,
            env=self._merged_env(),
            cwd=self.spec.cwd,
            creationflags=CREATE_NEW_PROCESS_GROUP
        )

        # Assign process to Job
        ctypes.windll.kernel32.AssignProcessToJobObject(
            self.job_handle, int(self.process._handle)
        )

        self._mark_started()
        print(f"[{self.spec.id}] Started Windows process group (PID {self.process.pid})")

    def _start_posix(self):
        """POSIX: setsid() creates new process group."""
        def preexec_fn():
            os.setsid()  # Create new session (becomes process group leader)

        self.process = subprocess.Popen(
            self.spec.cmd,
            env=self._merged_env(),
            cwd=self.spec.cwd,
            preexec_fn=preexec_fn
        )
        self.pgid = self.process.pid  # Process group ID = session leader PID
        self._mark_started()
        print(f"[{self.spec.id}] Started POSIX process group (PGID {self.pgid})")

    def handle_exit(self, exit_code: int):
        """Handle service exit with backoff or quarantine."""
        print(f"[{self.spec.id}] Exited with code {exit_code}")

        if exit_code == 99:
            # Hot reload - no backoff, immediate restart
            print(f"[{self.spec.id}] Hot reload triggered")
            self.backoff.reset()
            self.start()

        elif exit_code == 78:
            # Quarantine - disable service, alert ops
            print(f"[{self.spec.id}] QUARANTINE - service disabled")
            self.quarantined = True
            self._alert_ops(f"Service {self.spec.id} quarantined (exit 78)")

        elif exit_code != 0:
            # Crash - apply backoff
            try:
                delay = self.backoff.next_delay()
                print(f"[{self.spec.id}] Crash detected, restarting in {delay:.1f}s "
                      f"(attempt {self.backoff.attempts}/{self.spec.max_retries})")
                time.sleep(delay)
                self.start()
            except QuarantineRequired:
                print(f"[{self.spec.id}] QUARANTINE - exceeded max retries")
                self.quarantined = True
                self._alert_ops(f"Service {self.spec.id} quarantined (max retries)")

        else:
            # Clean exit (code 0) - reset backoff, don't restart
            print(f"[{self.spec.id}] Clean exit, not restarting")
            self.backoff.reset()

    def shutdown(self):
        """Terminate entire process group cleanly."""
        if not self.process:
            return

        if platform.system() == "Windows":
            # Terminate Job (kills entire tree)
            import ctypes
            ctypes.windll.kernel32.TerminateJobObject(self.job_handle, 0)
            ctypes.windll.kernel32.CloseHandle(self.job_handle)
        else:
            # Kill process group
            try:
                os.killpg(self.pgid, signal.SIGTERM)
                time.sleep(2)
                os.killpg(self.pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Already dead

        print(f"[{self.spec.id}] Shutdown complete")

    def _alert_ops(self, message: str):
        """Alert operations team (stub - integrate with alerting)."""
        print(f"[ALERT] {message}")
        # TODO: Send to Slack, PagerDuty, etc.
