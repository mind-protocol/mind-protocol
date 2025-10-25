# MPSv3 Supervisor - Centralized Process Management

**Version:** 1.0
**Status:** Specification (Production-Ready)
**Created:** 2025-10-25
**Owner:** Victor (Ops) + Atlas (Implementation)
**Purpose:** Eliminate crash loops, stale locks, and duplicate processes through centralized supervision

---

## Executive Summary

**MPSv3** is a centralized supervisor that replaces the mixed guardian/launcher model with a single process management layer. It solves operational failures by:

1. **OS-level singleton** - No stale locks, no duplicate supervisors
2. **Process groups** - Clean termination of entire service trees
3. **Single hot-reload** - One watcher, no race conditions
4. **Exponential backoff** - Prevents crash loops
5. **Quarantine** - Isolates repeatedly failing services

**Before (Guardian + Children):**
```
guardian.py (file lock .launcher.lock)
  ├─ launcher.py (spawns services)
  │   ├─ falkordb.exe (self-restart on crash)
  │   ├─ websocket_server.py (hot-reload via exit 99)
  │   └─ dashboard (npm run dev with auto-reload)
  └─ file_watcher.py (triggers hot-reload)

Problem: Dual restart logic (parent + child), file locks wedge, multiple hot-reload mechanisms race
```

**After (MPSv3):**
```
mpsv3_supervisor.py (OS mutex - no file lock)
  ├─ Process Group: falkordb (CRITICAL)
  ├─ Process Group: ws_api (CORE)
  ├─ Process Group: dashboard (CORE)
  └─ File Watcher (centralized, triggers supervisor actions)

Solution: Centralized restart, clean process groups, single hot-reload, exponential backoff
```

---

## 1. Problem Statement

### 1.1 Observed Failure Modes

**Crash Loops:**
- Guardian restarts crashed service immediately
- Service crashes again (same root cause)
- 100% CPU, log spam, resource exhaustion

**Stale Locks:**
- `.launcher.lock` persists after unclean shutdown
- New guardian sees lock, refuses to start
- Manual intervention required (kill PID, delete lock)

**Duplicate Processes:**
- Guardian thinks service is down (stale PID)
- Guardian spawns new instance
- Old instance still running → port conflicts, database corruption

**Guardian Failures:**
- Guardian crashes → all services orphaned
- No automatic recovery of guardian itself
- System stuck until manual restart

### 1.2 Root Causes

**Dual Restart Logic:**
- Guardian owns restart logic
- Children (launcher.py) also own restart logic
- Conflict: who is responsible when service crashes?

**File-Based Singletons:**
- `.launcher.lock` stores PID
- If process crashes, lock persists
- No OS-level cleanup on process death

**Multiple Hot-Reload Mechanisms:**
- file_watcher.py triggers service exit 99
- npm run dev has built-in auto-reload
- websocket_server.py self-reloads on code change
- Race conditions, duplicate restarts

**No Backoff:**
- Crash → immediate restart
- Same error → crash → immediate restart
- Infinite loop with no breathing room

---

## 2. MPSv3 Design

### 2.1 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ MPSv3 Supervisor (mpsv3_supervisor.py)                       │
│  • OS Mutex (Windows) / flock (POSIX) - auto-released on death│
│  • ServiceRegistry (YAML-based ServiceSpec definitions)      │
│  • FileWatcher (centralized, triggers supervisor actions)    │
│  • ExponentialBackoff (per-service, quarantine on failure)   │
└──────────────────────────────────────────────────────────────┘
         │
         ├─ spawn_service_group(spec: ServiceSpec)
         │   ├─ Windows: CREATE_NEW_PROCESS_GROUP + Job Object
         │   └─ POSIX: setsid() → new process group
         │
         ├─ monitor_health(service_id)
         │   ├─ Readiness: HTTP ping until 200 OK
         │   └─ Health: Periodic probe + timeout detection
         │
         ├─ handle_exit(service_id, exit_code)
         │   ├─ Exit 99 → Hot Reload (no backoff, immediate restart)
         │   ├─ Exit 78 → Quarantine (log, disable, alert)
         │   └─ Exit != 0 → Backoff (exponential, max 5 attempts)
         │
         └─ shutdown_service_group(service_id)
             ├─ Windows: TerminateJobObject (kills entire tree)
             └─ POSIX: killpg(pgid, SIGTERM) → wait → SIGKILL
```

### 2.2 Core Components

**Singleton Lease:**
- **Windows:** CreateMutex with unique name `Global\MPSv3_Supervisor`
- **POSIX:** flock() on `/tmp/mpsv3_supervisor.lock`
- **Auto-release:** OS releases lock when process dies (no stale locks)

**ServiceSpec (YAML):**
```yaml
services:
  - id: falkordb
    cmd: ["C:\\FalkorDB\\falkordb-service.exe", "--port", "6379"]
    env:
      FALKORDB_DATA_DIR: "C:\\FalkorDB\\data"
    readiness:
      type: tcp_port
      port: 6379
      timeout_sec: 30
    health:
      type: redis_ping
      interval_sec: 60
      timeout_sec: 5
    criticality: CRITICAL
    max_retries: 5
    watched_files: []  # Never auto-reload database

  - id: ws_api
    cmd: ["python", "orchestration/adapters/ws/websocket_server.py"]
    env:
      PORT: "8000"
    readiness:
      type: http_get
      url: "http://localhost:8000/api/ping"
      timeout_sec: 10
    health:
      type: http_get
      url: "http://localhost:8000/api/health"
      interval_sec: 30
      timeout_sec: 5
    criticality: CORE
    max_retries: 3
    watched_files:
      - "orchestration/**/*.py"
      - "!orchestration/tests/**"

  - id: dashboard
    cmd: ["npm", "run", "dev"]
    cwd: "C:\\Users\\reyno\\mind-protocol"
    env:
      NODE_ENV: "development"
      PORT: "3000"
    readiness:
      type: http_get
      url: "http://localhost:3000"
      timeout_sec: 60
    health:
      type: http_get
      url: "http://localhost:3000/api/health"
      interval_sec: 30
      timeout_sec: 5
    criticality: CORE
    max_retries: 3
    watched_files:
      - "app/**/*.{ts,tsx}"
      - "!app/**/*.test.{ts,tsx}"
```

**ServiceRegistry:**
```python
class ServiceRegistry:
    def __init__(self, yaml_path: str):
        self.specs: dict[str, ServiceSpec] = self._load_yaml(yaml_path)
        self.runners: dict[str, ServiceRunner] = {}

    def start_all(self):
        for spec in self.specs.values():
            self.runners[spec.id] = ServiceRunner(spec)
            self.runners[spec.id].start()

    def reload_service(self, service_id: str):
        runner = self.runners[service_id]
        runner.graceful_restart(reason="hot_reload")
```

**ExponentialBackoff:**
```python
class BackoffState:
    def __init__(self, max_retries: int = 5):
        self.attempts = 0
        self.max_retries = max_retries
        self.base_delay = 1.0  # seconds
        self.max_delay = 60.0
        self.jitter = 0.2  # ±20%

    def next_delay(self) -> float:
        if self.attempts >= self.max_retries:
            raise QuarantineRequired(f"Exceeded {self.max_retries} attempts")

        delay = min(self.base_delay * (2 ** self.attempts), self.max_delay)
        jitter = random.uniform(-self.jitter * delay, self.jitter * delay)
        self.attempts += 1
        return delay + jitter

    def reset(self):
        self.attempts = 0
```

---

## 3. Implementation Skeletons

### 3.1 Singleton Lease

```python
import platform
import fcntl  # POSIX
import ctypes  # Windows
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
            if self.handle:
                ctypes.windll.kernel32.ReleaseMutex(self.handle)
                ctypes.windll.kernel32.CloseHandle(self.handle)
        else:
            if self.handle:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
                self.handle.close()

        self._acquired = False
        print("[SingletonLease] Released")

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Failed to acquire singleton lease")
        return self

    def __exit__(self, *args):
        self.release()
```

### 3.2 ServiceRunner with Backoff

```python
import subprocess
import time
import platform
from dataclasses import dataclass
from typing import Optional

@dataclass
class ServiceSpec:
    id: str
    cmd: list[str]
    env: dict[str, str]
    cwd: Optional[str]
    criticality: str  # CRITICAL | CORE | OPTIONAL
    max_retries: int
    watched_files: list[str]

class ServiceRunner:
    """Manages lifecycle of a single service with backoff and quarantine."""

    def __init__(self, spec: ServiceSpec):
        self.spec = spec
        self.process: Optional[subprocess.Popen] = None
        self.pgid: Optional[int] = None  # POSIX process group ID
        self.job_handle = None  # Windows Job object
        self.backoff = BackoffState(max_retries=spec.max_retries)
        self.quarantined = False

    def start(self):
        """Start service in new process group."""
        if self.quarantined:
            print(f"[{self.spec.id}] Service quarantined, refusing to start")
            return

        if platform.system() == "Windows":
            self._start_windows()
        else:
            self._start_posix()

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
            env=self.spec.env,
            cwd=self.spec.cwd,
            creationflags=CREATE_NEW_PROCESS_GROUP
        )

        # Assign process to Job
        ctypes.windll.kernel32.AssignProcessToJobObject(
            self.job_handle, int(self.process._handle)
        )

        print(f"[{self.spec.id}] Started Windows process group (PID {self.process.pid})")

    def _start_posix(self):
        """POSIX: setsid() creates new process group."""
        def preexec_fn():
            os.setsid()  # Create new session (becomes process group leader)

        self.process = subprocess.Popen(
            self.spec.cmd,
            env=self.spec.env,
            cwd=self.spec.cwd,
            preexec_fn=preexec_fn
        )
        self.pgid = self.process.pid  # Process group ID = session leader PID
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
```

### 3.3 File Watcher (Centralized)

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import fnmatch

class ServiceFileHandler(FileSystemEventHandler):
    """Watches files for a specific service and triggers reload."""

    def __init__(self, service_id: str, patterns: list[str], callback):
        self.service_id = service_id
        self.patterns = patterns
        self.callback = callback
        self.debounce_time = 2.0  # seconds
        self.last_trigger = 0

    def on_modified(self, event):
        if event.is_directory:
            return

        # Check if file matches watched patterns
        if not any(fnmatch.fnmatch(event.src_path, p) for p in self.patterns):
            return

        # Debounce rapid changes
        now = time.time()
        if now - self.last_trigger < self.debounce_time:
            return

        self.last_trigger = now
        print(f"[FileWatcher] {self.service_id}: {event.src_path} changed")
        self.callback(self.service_id, reason="file_change")

class CentralizedFileWatcher:
    """Single file watcher for all services."""

    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.observer = Observer()

    def start(self):
        """Watch all service file patterns."""
        for spec in self.registry.specs.values():
            if not spec.watched_files:
                continue

            handler = ServiceFileHandler(
                service_id=spec.id,
                patterns=spec.watched_files,
                callback=self._handle_file_change
            )

            # Watch workspace root
            self.observer.schedule(handler, path=".", recursive=True)

        self.observer.start()
        print("[FileWatcher] Started centralized watcher")

    def _handle_file_change(self, service_id: str, reason: str):
        """Trigger graceful reload of service."""
        print(f"[FileWatcher] Triggering reload: {service_id} ({reason})")
        self.registry.reload_service(service_id)

    def stop(self):
        self.observer.stop()
        self.observer.join()
```

---

## 4. Exit Code Semantics

MPSv3 uses exit codes to control restart behavior:

| Exit Code | Meaning | Supervisor Action |
|-----------|---------|-------------------|
| **0** | Clean exit | No restart, reset backoff counter |
| **99** | Hot reload request | Immediate restart (no backoff) |
| **78** | Self-quarantine | Disable service, alert ops, no restart |
| **1-255** | Crash/error | Exponential backoff → restart (max retries) |

**Usage in Service Code:**

```python
# websocket_server.py - request hot reload
def signal_handler(sig, frame):
    print("[WebSocket] SIGHUP received, requesting hot reload")
    sys.exit(99)

# consciousness_engine_v2.py - self-quarantine on corruption
def detect_corruption():
    if graph.node_count() == 0 and expected_bootstrap:
        print("[Engine] FATAL: Graph corruption detected, quarantining")
        sys.exit(78)

# normal crash - let supervisor handle backoff
def main():
    try:
        run_engine()
    except Exception as e:
        print(f"[Engine] Unhandled exception: {e}")
        sys.exit(1)  # Supervisor applies backoff
```

---

## 5. Process Group Control

### 5.1 Why Process Groups?

**Problem:** Killing parent doesn't kill children
```
supervisor kills websocket_server.py (PID 1234)
  └─ orphaned: gunicorn worker (PID 1235) still running
```

**Solution:** Kill entire process group atomically
```
supervisor kills process group PGID 1234
  ├─ websocket_server.py (PID 1234) ✓ terminated
  └─ gunicorn worker (PID 1235) ✓ terminated
```

### 5.2 Windows: Job Objects

```python
# Create Job with KILL_ON_JOB_CLOSE
job_handle = ctypes.windll.kernel32.CreateJobObjectW(None, None)
job_info[2] = JOBOBJECT_LIMIT_KILL_ON_JOB_CLOSE
ctypes.windll.kernel32.SetInformationJobObject(job_handle, 2, ...)

# Assign process to Job
ctypes.windll.kernel32.AssignProcessToJobObject(job_handle, process._handle)

# Shutdown: TerminateJobObject kills entire tree
ctypes.windll.kernel32.TerminateJobObject(job_handle, 0)
```

**Behavior:** All child processes automatically added to Job. Closing Job terminates all members.

### 5.3 POSIX: Process Groups + killpg

```python
# Create new session (becomes process group leader)
def preexec_fn():
    os.setsid()  # PID becomes PGID

process = subprocess.Popen(..., preexec_fn=preexec_fn)
pgid = process.pid

# Shutdown: killpg sends signal to entire group
os.killpg(pgid, signal.SIGTERM)  # Graceful
time.sleep(2)
os.killpg(pgid, signal.SIGKILL)  # Forceful
```

**Behavior:** All child processes inherit PGID. killpg() targets entire group.

---

## 6. Migration Plan

### Phase 0: Preparation (Victor - 1 hour)

**Goal:** Understand current state, backup configuration

1. **Inventory Current Processes:**
   ```bash
   tasklist | findstr "python\|node\|falkordb"
   # or
   ps aux | grep -E "python|node|falkordb"
   ```

2. **Backup Guardian Configuration:**
   ```bash
   cp guardian.py guardian.py.backup
   cp launcher.py launcher.py.backup
   ```

3. **Document Current Startup:**
   - How is guardian started? (manual, systemd, Task Scheduler?)
   - What environment variables are set?
   - What order do services start?

### Phase 1: Implement MPSv3 (Atlas - 4 hours)

**Goal:** Create mpsv3_supervisor.py with full functionality

1. **Create ServiceSpec YAML:**
   ```
   orchestration/mpsv3_services.yaml
   ```
   - Define all current services (falkordb, ws_api, dashboard, engines)
   - Specify readiness/health checks
   - Define watched file patterns

2. **Implement Core Classes:**
   ```
   orchestration/services/mpsv3/
     ├─ singleton_lease.py
     ├─ service_runner.py
     ├─ backoff.py
     ├─ file_watcher.py
     └─ registry.py
   ```

3. **Create Main Supervisor:**
   ```
   orchestration/mpsv3_supervisor.py
   ```
   - Loads ServiceSpec YAML
   - Acquires singleton lease
   - Starts all services with health checks
   - Runs centralized file watcher
   - Handles signals (SIGTERM, SIGINT)

4. **Test in Isolation:**
   ```bash
   # Stop old guardian
   taskkill /F /IM python.exe /FI "WINDOWTITLE eq Guardian*"

   # Run MPSv3
   python orchestration/mpsv3_supervisor.py --config orchestration/mpsv3_services.yaml

   # Verify all services start
   curl http://localhost:8000/api/ping
   curl http://localhost:3000
   redis-cli -p 6379 PING
   ```

### Phase 2: Parallel Run (Victor + Atlas - 24 hours)

**Goal:** Run MPSv3 alongside guardian to verify behavior

1. **Disable Old Auto-Start:**
   - Remove Task Scheduler entry for guardian (if exists)
   - Update systemd to not start guardian (if exists)

2. **Manual Start Both Systems:**
   ```bash
   # Terminal 1: Old guardian
   python guardian.py

   # Terminal 2: New MPSv3 (different port offsets for testing)
   python orchestration/mpsv3_supervisor.py --config mpsv3_services_test.yaml
   ```

3. **Observe for 24 Hours:**
   - Check logs: `tail -f logs/mpsv3_supervisor.log`
   - Verify no crash loops
   - Test hot reload: modify websocket_server.py, verify reload
   - Test backoff: inject crash, verify exponential delays
   - Test quarantine: crash 5 times, verify service disabled

4. **Kill Testing:**
   - Kill MPSv3 process → verify OS releases singleton
   - Restart MPSv3 → verify no "already running" error
   - Kill service (e.g., ws_api) → verify supervisor restarts it

### Phase 3: Cutover (Victor - 1 hour)

**Goal:** Replace guardian with MPSv3 as primary supervisor

1. **Stop Guardian Permanently:**
   ```bash
   taskkill /F /IM python.exe /FI "WINDOWTITLE eq Guardian*"
   rm .launcher.lock  # Clean up old lock file
   ```

2. **Configure MPSv3 Auto-Start:**

   **Windows (Task Scheduler):**
   ```xml
   <Task>
     <Exec>
       <Command>python</Command>
       <Arguments>C:\Users\reyno\mind-protocol\orchestration\mpsv3_supervisor.py</Arguments>
       <WorkingDirectory>C:\Users\reyno\mind-protocol</WorkingDirectory>
     </Exec>
     <Triggers>
       <BootTrigger />
     </Triggers>
   </Task>
   ```

   **Linux (systemd):**
   ```ini
   [Unit]
   Description=MPSv3 Supervisor
   After=network.target

   [Service]
   Type=simple
   User=reyno
   WorkingDirectory=/home/reyno/mind-protocol
   ExecStart=/usr/bin/python3 orchestration/mpsv3_supervisor.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start MPSv3:**
   ```bash
   python orchestration/mpsv3_supervisor.py
   ```

4. **Verify System Health:**
   ```bash
   curl http://localhost:8000/api/telemetry/counters
   curl http://localhost:3000
   # Should see rising tick counts, no errors
   ```

5. **Archive Old System:**
   ```bash
   mkdir archive/guardian_v1
   mv guardian.py launcher.py file_watcher.py archive/guardian_v1/
   ```

### Phase 4: Acceptance (All - 1 week)

**Criteria:**
- ✅ No crash loops observed
- ✅ No stale lock files requiring manual cleanup
- ✅ No duplicate process errors
- ✅ Hot reload working (<5s restart)
- ✅ Exponential backoff prevents rapid restarts
- ✅ Quarantine activates after max retries
- ✅ Process group cleanup (no orphans)
- ✅ Singleton lease auto-releases on supervisor crash

**Rollback Plan:**
If MPSv3 fails, restore guardian:
```bash
# Stop MPSv3
taskkill /F /IM python.exe /FI "WINDOWTITLE eq MPSv3*"

# Restore old system
cp archive/guardian_v1/* .
python guardian.py
```

---

## 7. Operational Benefits

### 7.1 Before vs. After

| Failure Mode | Before (Guardian) | After (MPSv3) |
|--------------|-------------------|---------------|
| **Crash Loop** | 100% CPU, log spam | Exponential backoff → quarantine after 5 attempts |
| **Stale Lock** | Manual PID kill + file delete | OS auto-releases mutex/flock on death |
| **Duplicate Processes** | Port conflicts, corruption | Process group = atomic start/stop |
| **Guardian Crash** | All services orphaned | OS releases singleton → new supervisor takes over |
| **Hot Reload Race** | Multiple watchers race | Single watcher, debounced, exit 99 semantics |

### 7.2 Observability

**Logs:**
```
logs/mpsv3_supervisor.log
```

**Key Events:**
```
[SingletonLease] Acquired Windows mutex: Global\MPSv3_Supervisor
[falkordb] Started Windows process group (PID 8912)
[ws_api] Readiness check passed: http://localhost:8000/api/ping
[FileWatcher] ws_api: orchestration/adapters/ws/websocket_server.py changed
[ws_api] Hot reload triggered
[ws_api] Exited with code 99
[ws_api] Hot reload triggered
[ws_api] Started Windows process group (PID 9124)
[dashboard] Crash detected, restarting in 2.3s (attempt 2/3)
[dashboard] QUARANTINE - exceeded max retries
[ALERT] Service dashboard quarantined (max retries)
```

**Metrics (Future):**
- Service uptime percentage
- Restart counts by reason (hot_reload, crash, manual)
- Quarantine events
- Average time to readiness

---

## 8. Service Specifications

### 8.1 FalkorDB

```yaml
- id: falkordb
  cmd: ["C:\\FalkorDB\\falkordb-service.exe", "--port", "6379"]
  env:
    FALKORDB_DATA_DIR: "C:\\FalkorDB\\data"
  readiness:
    type: tcp_port
    port: 6379
    timeout_sec: 30
  health:
    type: redis_ping
    interval_sec: 60
    timeout_sec: 5
  criticality: CRITICAL
  max_retries: 5
  watched_files: []  # Never auto-reload database
```

**Criticality:** CRITICAL - system cannot function without graph database
**Max Retries:** 5 - database stability critical
**Watched Files:** None - never hot-reload database (data corruption risk)

### 8.2 WebSocket API

```yaml
- id: ws_api
  cmd: ["python", "orchestration/adapters/ws/websocket_server.py"]
  env:
    PORT: "8000"
    FALKORDB_HOST: "localhost"
    FALKORDB_PORT: "6379"
  readiness:
    type: http_get
    url: "http://localhost:8000/api/ping"
    timeout_sec: 10
  health:
    type: http_get
    url: "http://localhost:8000/api/health"
    interval_sec: 30
    timeout_sec: 5
  criticality: CORE
  max_retries: 3
  watched_files:
    - "orchestration/**/*.py"
    - "!orchestration/tests/**"
```

**Criticality:** CORE - required for realtime telemetry
**Max Retries:** 3 - can restart without data loss
**Watched Files:** All orchestration Python files (hot-reload enabled)

### 8.3 Dashboard

```yaml
- id: dashboard
  cmd: ["npm", "run", "dev"]
  cwd: "C:\\Users\\reyno\\mind-protocol"
  env:
    NODE_ENV: "development"
    PORT: "3000"
    NEXT_PUBLIC_WS_URL: "ws://localhost:8000"
  readiness:
    type: http_get
    url: "http://localhost:3000"
    timeout_sec: 60
  health:
    type: http_get
    url: "http://localhost:3000/api/health"
    interval_sec: 30
    timeout_sec: 5
  criticality: CORE
  max_retries: 3
  watched_files:
    - "app/**/*.{ts,tsx}"
    - "!app/**/*.test.{ts,tsx}"
```

**Criticality:** CORE - primary user interface
**Max Retries:** 3 - can restart without data loss
**Watched Files:** All Next.js app files (hot-reload enabled)

### 8.4 Consciousness Engine (Felix)

```yaml
- id: consciousness_engine_felix
  cmd: ["python", "orchestration/mechanisms/consciousness_engine_v2.py", "--citizen", "felix"]
  env:
    GRAPH_NAME: "citizen_felix"
  readiness:
    type: http_get
    url: "http://localhost:8000/api/consciousness/status?citizen=felix"
    timeout_sec: 15
  health:
    type: http_get
    url: "http://localhost:8000/api/consciousness/status?citizen=felix"
    interval_sec: 30
    timeout_sec: 5
  criticality: CORE
  max_retries: 3
  watched_files:
    - "orchestration/mechanisms/**/*.py"
```

**Criticality:** CORE - consciousness dynamics
**Max Retries:** 3 - graph persists across restarts
**Watched Files:** Consciousness mechanism code (hot-reload enabled)

---

## 9. Troubleshooting

### 9.1 Supervisor Won't Start

**Symptom:** "Another instance holds lease" message

**Diagnosis:**
```bash
# Windows: Check if mutex exists
# (no direct command - kill process holding mutex)
tasklist | findstr "mpsv3_supervisor"

# POSIX: Check lock file
lsof /tmp/MPSv3_Supervisor.lock
```

**Resolution:**
```bash
# Kill old supervisor
taskkill /F /IM python.exe /FI "COMMANDLINE eq *mpsv3_supervisor*"
# or
pkill -f mpsv3_supervisor

# OS auto-releases lock, restart
python orchestration/mpsv3_supervisor.py
```

### 9.2 Service Stuck in Crash Loop

**Symptom:** Service restarts rapidly, never reaches readiness

**Diagnosis:**
```bash
# Check supervisor logs
tail -f logs/mpsv3_supervisor.log | grep <service_id>

# Check service logs
tail -f logs/<service_id>.log
```

**Resolution:**
- Verify readiness check is reachable (correct URL/port)
- Check service logs for startup errors
- Increase readiness timeout_sec if service is slow to start
- If persistent, service will auto-quarantine after max_retries

### 9.3 Hot Reload Not Working

**Symptom:** File changes don't trigger service restart

**Diagnosis:**
```bash
# Check if file matches watched_files pattern
# e.g., does "orchestration/adapters/ws/websocket_server.py" match "orchestration/**/*.py"?

# Check FileWatcher logs
tail -f logs/mpsv3_supervisor.log | grep FileWatcher
```

**Resolution:**
- Verify watched_files patterns in ServiceSpec YAML
- Check file watcher debounce_time (default 2s)
- Ensure service exits with code 99 on reload signal

### 9.4 Process Group Not Cleaning Up

**Symptom:** Orphaned child processes after service shutdown

**Diagnosis:**
```bash
# Check for orphans
ps aux | grep <service_name>  # Should be empty after shutdown
```

**Resolution:**
- Verify process group creation (setsid on POSIX, Job on Windows)
- Check shutdown logic uses killpg/TerminateJobObject
- Manually kill orphans: `pkill -f <service_name>`

---

## 10. Future Enhancements

### 10.1 Service Dependencies

**Goal:** Start services in dependency order

```yaml
- id: ws_api
  depends_on:
    - falkordb  # Wait for FalkorDB to be healthy before starting ws_api
```

**Implementation:** Topological sort of service graph, start in order.

### 10.2 Graceful Degradation

**Goal:** Continue operating with non-critical services down

```yaml
- id: dashboard
  criticality: OPTIONAL  # System continues if dashboard fails
```

**Implementation:** Only alert on CRITICAL/CORE quarantine, allow OPTIONAL to fail silently.

### 10.3 Remote Monitoring

**Goal:** External observability (Prometheus, Grafana)

```python
from prometheus_client import Counter, Gauge

service_restarts = Counter("mpsv3_service_restarts", "Service restart count", ["service_id", "reason"])
service_uptime = Gauge("mpsv3_service_uptime_seconds", "Service uptime", ["service_id"])
```

**Implementation:** Expose /metrics endpoint for scraping.

---

## Appendix A: Comparison to Existing Guardian

| Feature | Guardian (Old) | MPSv3 (New) |
|---------|----------------|-------------|
| **Singleton Mechanism** | File lock (.launcher.lock) | OS mutex (Windows) / flock (POSIX) |
| **Stale Lock Cleanup** | Manual (kill PID, delete file) | Automatic (OS releases on death) |
| **Process Control** | Individual PIDs | Process Groups / Job Objects |
| **Restart Logic** | Immediate (no backoff) | Exponential backoff with quarantine |
| **Hot Reload** | Multiple watchers (race conditions) | Single centralized watcher |
| **Service Definitions** | Hardcoded in Python | YAML-based ServiceSpec |
| **Health Checks** | None | Readiness + periodic health probes |
| **Observability** | guardian.log only | Structured logs + future metrics |
| **Exit Code Semantics** | None (all exits treated same) | 0=clean, 99=reload, 78=quarantine, other=crash |

---

## Appendix B: Exit Code Reference

```python
# In service code (websocket_server.py, consciousness_engine_v2.py, etc.)

# Clean shutdown
sys.exit(0)  # Supervisor: no restart, reset backoff

# Request hot reload
sys.exit(99)  # Supervisor: immediate restart, no backoff

# Self-quarantine (fatal error, requires manual intervention)
sys.exit(78)  # Supervisor: disable service, alert ops

# Unhandled error
sys.exit(1)  # Supervisor: exponential backoff → restart (up to max_retries)
```

---

**End of Specification**

*MPSv3 Supervisor - Operational Excellence Through Centralization*

*Victor "The Resurrector" (Ops) + Atlas (Implementation) - Infrastructure Team*
