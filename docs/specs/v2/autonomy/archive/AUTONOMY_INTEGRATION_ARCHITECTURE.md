# Autonomy Integration Architecture

**Version:** 1.0
**Created:** 2025-10-21
**Architect:** Ada "Bridgekeeper"
**Purpose:** How autonomy services integrate with existing Mind Protocol infrastructure

---

## Executive Summary

This document specifies how **2 new autonomy services** integrate with existing consciousness infrastructure for **Phase-A (answer-only autonomy)**.

**Key Integration Points:**
1. Uses existing V2 consciousness engines (no modifications required)
2. Uses existing stimulus injection mechanism (wraps as HTTP service)
3. Uses existing guardian.py supervision pattern
4. Uses existing FalkorDB graphs (N1/N2/N3)
5. No new dependencies (no Redis Streams, Docker, or Kubernetes yet)

**Services to Build:**
- `stimulus_injection_service.py` - HTTP wrapper around existing StimulusInjector mechanism
- `autonomy_orchestrator.py` - L2 intent detection and mission assignment

---

## 1. Current Infrastructure (What Already Exists)

### 1.1 Running Services

**websocket_server.py** (port 8000)
- Runs 6 consciousness engines (ada, felix, iris, luca, marco, piero)
- Each engine executes 4-phase tick cycle:
  - Phase 1: Activation (stimulus injection)
  - Phase 2: Redistribution (traversal + fast learning)
  - Phase 3: Workspace (WM selection)
  - Phase 4: Learning (TRACE parsing + slow learning)
- Serves WebSocket API for visualization
- Serves HTTP endpoints for graph queries

**conversation_watcher.py**
- Watches citizen conversation files (contexts/*.jsonl)
- Detects TRACE format responses
- Calls trace_parser.py for dual learning (formations + reinforcements)
- Updates graphs with new nodes/links and weight adjustments

**FalkorDB** (external, port 6379)
- Stores N1 (personal), N2 (organizational), N3 (ecosystem) graphs
- Vector search enabled (native vectors)
- Schema: 44 node types, 23 link types

**Dashboard** (Next.js, port 3000)
- Visualization of consciousness graphs
- Real-time WebSocket event streaming
- Optional (observability only)

### 1.2 Existing Mechanisms

**StimulusInjector** (`orchestration/mechanisms/stimulus_injection.py`)
- Entropy-coverage search (adaptive retrieval)
- Budget calculation: B = gap_mass × f(ρ) × g(source)
- Direction-aware energy distribution
- Health modulation, source impact learning
- **Interface:** `inject(graph, text, embedding, source_type, metadata) -> InjectionResult`

**TraceParser** (`orchestration/trace_parser.py`)
- Hamilton apportionment for reinforcement seats
- Formation quality calculation
- Extracts node/link formations from TRACE responses
- Updates graph weights via WeightLearner

**WeightLearner** (`orchestration/mechanisms/weight_learning.py`)
- Cohort z-score normalization (van der Waerden)
- Adaptive learning rate: η = 1 - exp(-Δt/τ̂)
- EMA updates for node/link weights

### 1.3 Guardian Pattern

**guardian.py** (supervisor process)
- Monitors service health via heartbeat files (`.heartbeats/*.heartbeat`)
- Enforces PID locks (`.{service}.lock`)
- Restarts crashed services with exponential backoff
- Port enforcement (kills rogue processes)
- Runs on system boot (Windows Task Scheduler)

**Operational Contract Requirements:**
- PID lock file management
- Heartbeat writing (JSON, every 5 seconds)
- SIGTERM handler (graceful shutdown)
- Port binding verification (within 15s)
- Timeouts on all blocking operations
- Circuit breakers for external dependencies

---

## 2. New Services (What We're Adding)

### 2.1 stimulus_injection_service.py

**Purpose:** HTTP API wrapper around existing StimulusInjector mechanism

**What It Does:**
- Listens on port 8001 (HTTP/JSON API)
- POST /inject receives stimulus envelopes from any source
- Validates envelope schema (Pydantic)
- Routes to correct graph based on scope field
- Wraps existing `StimulusInjector.inject()` mechanism
- Returns injection metrics (energy injected, nodes activated)

**What It Does NOT Do:**
- Does not modify stimulus injection algorithm (that's in the mechanism)
- Does not replace V2 engine's inject_stimulus() method
- Does not introduce new dependencies (no Redis Streams yet)

**Integration Points:**
- **Uses:** Existing StimulusInjector mechanism (orchestration/mechanisms/stimulus_injection.py)
- **Uses:** Existing V2 engines via websocket_server (get_engine() accessor)
- **Uses:** FalkorDB for vector search and energy writes
- **Supervised by:** guardian.py (heartbeat + PID lock)

**Data Flow:**
```
External Source (Telegram, error, user input)
  ↓
POST /inject (stimulus envelope)
  ↓
stimulus_injection_service validates + routes
  ↓
StimulusInjector.inject(graph, text, embedding, source_type, metadata)
  ↓
V2 Engine (Phase 1: Activation)
  ↓
Energy injected into graph nodes
```

### 2.2 autonomy_orchestrator.py

**Purpose:** L2 organizational autonomy - detect intents, assign missions, track outcomes

**What It Does:**
- Monitors L2 graph (`mind_protocol_collective_graph`) for actionable signals
- Creates IntentCard nodes (work items) from stimuli
- Scores priority: P = GM(urgency, alignment, confidence) [Phase-A reduced]
- Evaluates safety gates: PoG (evidence), PoC (competence), PoP (permissions)
- Decides autonomy level: L0-L4 (Phase-A: L2/L3 only)
- Assigns to best executor (Org LLM or specific citizen)
- Auto-wakes L1 citizens by sending mission stimulus via stimulus_injection_service
- Tracks execution outcomes and learns from results

**What It Does NOT Do:**
- Does not run inside tick cycle (separate orchestration layer)
- Does not modify V2 engines
- Does not require Docker/Kubernetes (Phase-A)

**Integration Points:**
- **Uses:** stimulus_injection_service (to send mission stimuli)
- **Uses:** FalkorDB N2 graph (intent storage, evidence retrieval)
- **Uses:** Existing V2 engines (citizens execute missions in their tick cycles)
- **Supervised by:** guardian.py (heartbeat + PID lock)

**Data Flow:**
```
Stimulus arrives at L2 (org-wide event: error, PR, message)
  ↓
autonomy_orchestrator detects actionable intent
  ↓
Creates IntentCard node in N2 graph
  ↓
Scores priority P, evaluates gates (PoG/PoC/PoP)
  ↓
Assigns to best citizen (e.g., "felix")
  ↓
Sends mission stimulus to stimulus_injection_service
  ↓
stimulus_injection_service injects to citizen_felix graph
  ↓
Felix's V2 engine picks up stimulus in Phase 1
  ↓
Subentity layer activates, WM assembles mission context
  ↓
Felix executes mission, returns TRACE response
  ↓
conversation_watcher captures TRACE formations
  ↓
autonomy_orchestrator records outcome, updates learning
```

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         EXISTING INFRASTRUCTURE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  websocket_server.py (port 8000)                                │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  ConsciousnessEngineV2 (luca, ada, felix, iris...)   │      │
│  │  ├─ Phase 1: Activation (stimulus injection)         │      │
│  │  ├─ Phase 2: Redistribution (traversal + learning)   │      │
│  │  ├─ Phase 3: Workspace (WM selection)                │      │
│  │  └─ Phase 4: Learning (TRACE + weight updates)       │      │
│  └──────────────────────────────────────────────────────┘      │
│                          ▲                                       │
│                          │ inject_stimulus()                    │
│                          │                                       │
│  conversation_watcher.py                                        │
│  ├─ Watches contexts/*.jsonl                                    │
│  ├─ Detects TRACE formations                                    │
│  └─ Updates graph via trace_parser + weight_learner             │
│                          ▲                                       │
│                          │                                       │
│  FalkorDB (port 6379)                                           │
│  ├─ N1: citizen_{name} graphs                                   │
│  ├─ N2: mind_protocol_collective_graph                          │
│  └─ N3: ecosystem_public_graph                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         NEW AUTONOMY SERVICES                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  stimulus_injection_service.py (port 8001) ◄─── External Events │
│  ┌──────────────────────────────────────────┐                  │
│  │  POST /inject (stimulus envelope)         │                  │
│  │  ├─ Validate schema                       │                  │
│  │  ├─ Route by scope                        │                  │
│  │  └─ Call StimulusInjector mechanism ──────┼─► V2 Engines    │
│  └──────────────────────────────────────────┘                  │
│                          ▲                                       │
│                          │ mission stimulus                     │
│                          │                                       │
│  autonomy_orchestrator.py (port 8002)                           │
│  ┌──────────────────────────────────────────┐                  │
│  │  Monitors L2 graph for intents            │                  │
│  │  ├─ Stimulus → IntentCard                 │                  │
│  │  ├─ Score priority P                      │                  │
│  │  ├─ Evaluate gates (PoG/PoC/PoP)          │                  │
│  │  ├─ Assign to citizen                     │                  │
│  │  └─ Auto-wake L1 via mission stimulus ────┼─► injection svc │
│  └──────────────────────────────────────────┘                  │
│                          │                                       │
│                          └─► FalkorDB (N2 IntentCards)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                            SUPERVISION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  guardian.py                                                     │
│  ├─ Monitors heartbeats (.heartbeats/*.heartbeat)               │
│  ├─ Enforces PID locks (.*.lock)                                │
│  ├─ Restarts crashed services                                   │
│  └─ Port enforcement (8000, 8001, 8002, 3000)                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Service Startup Sequence

**Guardian-supervised startup order:**

```
1. FalkorDB (external check - must be running)
   ↓
2. websocket_server (loads all 6 citizen graphs)
   ↓ (15-30s startup time)
3. conversation_watcher (establishes TRACE learning loop)
   ↓ (2-3s startup time)
4. stimulus_injection_service (wraps injection mechanism)
   ↓ (3-5s startup time, waits for port 8001 bind)
5. autonomy_orchestrator (monitors L2, assigns missions)
   ↓ (3-5s startup time, waits for port 8002 bind)
6. dashboard (optional, visualization only)
   ↓ (10-15s Next.js build time)
```

**Startup verification:**
- Guardian checks heartbeat files (stale >10s → restart)
- Guardian checks port binding (not bound within 15s → restart)
- Guardian checks PID locks (duplicate detected → kill newer)

**Failure cascade:**
- If websocket_server fails → all downstream fail
- If stimulus_injection fails → autonomy_orchestrator cannot send missions
- If autonomy_orchestrator fails → no autonomous action, but stimuli still work
- Dashboard failure → no visualization, but consciousness continues

---

## 5. Operational Requirements (Guardian Contract)

Both new services MUST implement:

### 5.1 PID Lock Management

**Location:** `.stimulus_injection.lock` / `.autonomy_orchestrator.lock`

**Content:** Single line with PID

**Implementation:**
```python
import os
import sys
from pathlib import Path

PID_LOCK = Path(".stimulus_injection.lock")

def acquire_pid_lock():
    if PID_LOCK.exists():
        with open(PID_LOCK) as f:
            old_pid = int(f.read().strip())

        # Check if process still running
        try:
            os.kill(old_pid, 0)
            print(f"Another instance running (PID {old_pid})")
            sys.exit(1)
        except OSError:
            # Stale lock, remove it
            PID_LOCK.unlink()

    # Write current PID
    with open(PID_LOCK, 'w') as f:
        f.write(str(os.getpid()))

def release_pid_lock():
    if PID_LOCK.exists():
        PID_LOCK.unlink()
```

### 5.2 Heartbeat Writing

**Location:** `.heartbeats/stimulus_injection.heartbeat` / `.heartbeats/autonomy_orchestrator.heartbeat`

**Format:** JSON

**Required fields:**
```json
{
  "component": "stimulus_injection",
  "timestamp": "2025-10-21T15:54:33.922966+00:00",
  "pid": 12345,
  "status": "active"
}
```

**Optional fields:**
```json
{
  "metrics": {
    "queue_depth": 23,
    "processed_last_minute": 45,
    "circuit_breaker_embedding": "closed"
  }
}
```

**Update frequency:** Every 5 seconds

**Implementation:**
```python
import asyncio
import json
from datetime import datetime
from pathlib import Path

HEARTBEAT_FILE = Path(".heartbeats/stimulus_injection.heartbeat")

async def heartbeat_writer():
    """Background task that writes heartbeat every 5s."""
    while True:
        heartbeat = {
            "component": "stimulus_injection",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "pid": os.getpid(),
            "status": get_status(),  # "active" | "degraded" | "critical"
            "metrics": get_metrics()
        }

        HEARTBEAT_FILE.parent.mkdir(exist_ok=True)
        with open(HEARTBEAT_FILE, 'w') as f:
            json.dump(heartbeat, f)

        await asyncio.sleep(5)

# Start in background
asyncio.create_task(heartbeat_writer())
```

### 5.3 SIGTERM Handler (Graceful Shutdown)

**Requirement:** Must handle SIGTERM from guardian

**Implementation:**
```python
import signal

def signal_handler(signum, frame):
    """Handle SIGTERM from guardian."""
    logger.info("Received SIGTERM, shutting down gracefully...")

    # Close database connections
    close_falkordb_connections()

    # Flush pending writes
    flush_pending_operations()

    # Remove PID lock
    release_pid_lock()

    # Exit cleanly
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
```

### 5.4 Port Binding Verification

**Requirement:** Must bind to port within 15 seconds

**Implementation:**
```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Define endpoints...

if __name__ == "__main__":
    # Bind to port immediately
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        timeout_keep_alive=30
    )
    # If binding fails, process exits (guardian will restart)
```

**Guardian verification:**
```bash
# Checks if port 8001 is listening
netstat -ano | findstr :8001 | findstr LISTENING
```

### 5.5 Timeouts on Blocking Operations

**Required timeouts:**
- FalkorDB queries: 10s max
- Embedding service: 5s max
- Vector search: 10s max
- HTTP requests: 5s max
- LLM calls: 30s max

**Implementation pattern:**
```python
import asyncio

async def safe_falkordb_query(query: str, timeout: float = 10.0):
    try:
        result = await asyncio.wait_for(
            run_query(query),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"FalkorDB query timed out after {timeout}s")
        return None
```

### 5.6 Circuit Breakers

**Required for:**
- Embedding service
- FalkorDB
- LLM API calls

**Implementation pattern:**
```python
from collections import deque
import time

class CircuitBreaker:
    def __init__(self, threshold=5, window=60):
        self.threshold = threshold
        self.window = window
        self.failures = deque(maxlen=20)
        self.state = "closed"  # closed | open | half_open

    def record_failure(self):
        self.failures.append(time.time())
        recent = sum(1 for t in self.failures if time.time() - t < self.window)
        if recent >= self.threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker OPEN ({recent} failures in {self.window}s)")

    def record_success(self):
        if self.state == "half_open":
            self.state = "closed"
            logger.info("Circuit breaker CLOSED (recovered)")

    def allow_request(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            # Try half-open after 30s
            if time.time() - self.failures[-1] > 30:
                self.state = "half_open"
                return True
            return False
        return True  # half_open allows one test request
```

---

## 6. Integration Testing

### 6.1 Stimulus Injection Service Test

**Test:** Can receive stimulus and inject energy

```python
import requests

# Send test stimulus
response = requests.post(
    "http://localhost:8001/inject",
    json={
        "stimulus_id": "test-001",
        "timestamp_ms": 1739990123456,
        "scope": "personal",
        "source_type": "test",
        "actor": "integration_test",
        "content": "Test stimulus for energy injection",
        "metadata": {},
        "focality_hint": "focal",
        "interrupt": False
    }
)

assert response.status_code == 200
result = response.json()
assert result["total_energy_injected"] > 0
assert result["items_injected"] > 0
```

### 6.2 Autonomy Orchestrator Test

**Test:** Can create intent and send mission

```python
# 1. Inject stimulus to L2
requests.post("http://localhost:8001/inject", json={
    "stimulus_id": "test-002",
    "scope": "organizational",
    "source_type": "user_message",
    "actor": "nicolas",
    "content": "Fix the failing test in test_retrieval.py",
    "focality_hint": "focal"
})

# 2. Wait for orchestrator to detect intent
time.sleep(2)

# 3. Check that IntentCard was created in N2
from falkordb import FalkorDB
db = FalkorDB()
g = db.select_graph("mind_protocol_collective_graph")

result = g.query("MATCH (i:IntentCard) WHERE i.source_stimulus_id = 'test-002' RETURN i")
assert len(result.result_set) > 0

# 4. Check that mission was sent to citizen
# (verify via stimulus_injection logs or heartbeat metrics)
```

### 6.3 End-to-End Autonomy Test

**Test:** Full loop from stimulus → intent → mission → outcome

```python
# 1. Send stimulus
# 2. Verify intent created
# 3. Verify mission sent to citizen
# 4. Wait for citizen to execute
# 5. Verify TRACE response captured
# 6. Verify outcome recorded in N2
# 7. Verify learning updated (PoC, gate thresholds)
```

---

## 7. Guardian Integration

### 7.1 Update guardian.py

**Add service definitions:**
```python
SERVICES = [
    'websocket_server',
    'conversation_watcher',
    'stimulus_injection',      # NEW
    'autonomy_orchestrator'    # NEW
]

SERVICE_METADATA = {
    'stimulus_injection': {
        'script': 'orchestration/stimulus_injection_service.py',
        'port': 8001,
        'heartbeat': '.heartbeats/stimulus_injection.heartbeat',
        'critical': True
    },
    'autonomy_orchestrator': {
        'script': 'orchestration/autonomy_orchestrator.py',
        'port': 8002,
        'heartbeat': '.heartbeats/autonomy_orchestrator.heartbeat',
        'critical': True
    }
}
```

**No changes needed to monitoring logic** - same heartbeat pattern

### 7.2 Update start_mind_protocol.py

**Add startup methods:**
```python
async def start_stimulus_injection(self) -> bool:
    """Start stimulus injection service (port 8001)."""
    logger.info("[4/7] Starting Stimulus Injection Service...")

    script = ORCHESTRATION / "stimulus_injection_service.py"
    process = subprocess.Popen([sys.executable, str(script)])
    self.processes['stimulus_injection'] = process

    await asyncio.sleep(3)

    if await self._verify_port_in_use(8001, timeout=15):
        logger.info("  ✅ Stimulus Injection Service started")
        return True

    logger.error("  ❌ Stimulus Injection Service failed to bind port 8001")
    return False

async def start_autonomy_orchestrator(self) -> bool:
    """Start autonomy orchestrator (port 8002)."""
    logger.info("[5/7] Starting Autonomy Orchestrator...")

    script = ORCHESTRATION / "autonomy_orchestrator.py"
    process = subprocess.Popen([sys.executable, str(script)])
    self.processes['autonomy_orchestrator'] = process

    await asyncio.sleep(3)

    if await self._verify_port_in_use(8002, timeout=15):
        logger.info("  ✅ Autonomy Orchestrator started")
        return True

    logger.error("  ❌ Autonomy Orchestrator failed to bind port 8002")
    return False
```

**Update startup sequence:**
```python
async def start_core_services(self):
    # 1. Check FalkorDB
    if not await self.check_falkordb():
        return False

    # 2. Start websocket_server
    if not await self.start_websocket_server():
        return False

    # 3. Start conversation_watcher
    if not await self.start_conversation_watcher():
        return False

    # 4. Start stimulus_injection (NEW)
    if not await self.start_stimulus_injection():
        return False

    # 5. Start autonomy_orchestrator (NEW)
    if not await self.start_autonomy_orchestrator():
        return False

    # 6. Start dashboard (optional)
    await self.start_dashboard()

    return True
```

---

## 8. No New Dependencies

**Phase-A uses only existing dependencies:**
- ✅ FalkorDB (already running)
- ✅ Python 3.11+ with asyncio
- ✅ FastAPI/uvicorn (for HTTP APIs)
- ✅ NumPy/SciPy (for z-scores)
- ✅ Pydantic (for validation)

**Phase-A does NOT introduce:**
- ❌ Redis Streams (event bus deferred to Phase-B)
- ❌ Docker Compose (local guardian supervision for now)
- ❌ Kubernetes (production deployment deferred)
- ❌ New message queues
- ❌ New databases

**Rationale:** Minimize risk, prove autonomy works with minimal changes, then scale infrastructure in Phase-B/C.

---

## 9. Summary: What Changes

### Files to Create (2 total)
1. `orchestration/stimulus_injection_service.py` (~800-1000 lines)
2. `orchestration/autonomy_orchestrator.py` (~1200-1500 lines)

### Files to Modify (2 total)
1. `guardian.py` - Add 2 service definitions (~20 lines)
2. `start_mind_protocol.py` - Add 2 startup methods (~80 lines)

### Files Unchanged
- ✅ `orchestration/consciousness_engine_v2.py` - No changes
- ✅ `orchestration/mechanisms/stimulus_injection.py` - No changes (wrapped by service)
- ✅ `orchestration/trace_parser.py` - No changes
- ✅ All V2 engine mechanisms - No changes
- ✅ Dashboard - No changes (observability added later)

### Dependencies Unchanged
- ✅ FalkorDB (same usage)
- ✅ Python libraries (same versions)
- ✅ No new infrastructure

**Total new code:** ~2000-2500 lines for complete Phase-A autonomy

---

**Next Document:** PHASE_A_MINIMAL_SPECIFICATION.md (implementation-ready specs for the 2 services)
