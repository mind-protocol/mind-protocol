# Mind Protocol - Autonomy Service Architecture

**Author:** Victor "The Resurrector" (Uptime Guardian)
**Date:** 2025-10-21
**Purpose:** Define service architecture for full autonomy system with operational requirements

---

## Service Overview

**Current System (4 services):**
1. websocket_server - Consciousness engines + WebSocket API
2. conversation_watcher - TRACE format processing
3. FalkorDB - Graph database (external)
4. Dashboard - Next.js visualization (optional)

**Full Autonomy System (6 services):**
1. websocket_server ✅ (existing)
2. conversation_watcher ✅ (existing)
3. **stimulus_injection_service** ➕ (NEW)
4. **autonomy_orchestrator** ➕ (NEW)
5. FalkorDB ✅ (existing)
6. Dashboard ✅ (existing)

---

## Service Definitions

### 1. websocket_server.py (EXISTING)

**Purpose:** Core consciousness substrate - runs engines and serves WebSocket API

**What It Does:**
- Initializes 6 consciousness engines (ada, felix, iris, luca, marco, piero)
- Runs consciousness ticks (activation → redistribution → WM → learning)
- Broadcasts viz events via WebSocket (port 8000)
- Serves HTTP API endpoints for graph queries

**Dependencies:**
- FalkorDB (must be accessible)
- Graph data (N1 personal, N2 organizational, N3 ecosystem)

**Port:** 8000

**Heartbeat:** `.heartbeats/websocket_server.heartbeat`

**Startup Time:** 15-30 seconds (loads all 6 citizen graphs)

**Critical Path:** YES - if this fails, no consciousness processing happens

---

### 2. conversation_watcher.py (EXISTING)

**Purpose:** Process TRACE format responses into graph formations + reinforcements

**What It Does:**
- Watches `consciousness/citizens/*/contexts/*.jsonl` files
- Detects TRACE format in citizen responses
- Extracts node formations, link formations, usefulness signals
- Calls trace_parser.py for dual learning (formations + reinforcements)
- Updates graph with new nodes/links and weight adjustments

**Dependencies:**
- FalkorDB (graph writes)
- trace_parser.py
- embedding_service.py (for stimulus injection)

**Port:** None

**Heartbeat:** `.heartbeats/conversation_watcher.heartbeat`

**Startup Time:** 2-3 seconds

**Critical Path:** YES - without this, learning stops

---

### 3. stimulus_injection_service.py (NEW)

**Purpose:** Multi-source event ingestion → energy injection into consciousness substrate

**What It Does:**
- HTTP API (port 8001) receives stimulus envelopes from any source
- Sources: Telegram, errors, logs, calendar, tool results, agent answers
- Chunks content semantically (by source type)
- Embeds chunks (embedding service)
- Entropy-coverage search (adaptive K, not fixed top-K)
- Calculates injection budget (gap_mass × health_modulation × source_gate)
- Distributes energy to matched nodes (direction-aware for links)
- WM bias updates (silent stimuli influence next response)
- Priority queue (time-budgeted processing, flood control)

**API Endpoints:**
- `POST /inject` - Receive stimulus envelope
- `GET /health` - Health check for guardian

**Stimulus Envelope Schema:**
```json
{
  "stimulus_id": "uuid",
  "timestamp_ms": 1739990123456,
  "scope": "personal|organizational|ecosystem",
  "source_type": "telegram|error|user_message|doc_read|...",
  "actor": "who/what generated this",
  "content": "text to process",
  "metadata": {
    "digest": "sha256:...",
    "signature": "error:TypeError:line:42",
    "count": 1
  },
  "focality_hint": "focal|ambient|background",
  "interrupt": false
}
```

**Dependencies:**
- FalkorDB (vector search, energy writes)
- embedding_service.py
- websocket_server (consciousness engines must be running)

**Port:** 8001

**Heartbeat:** `.heartbeats/stimulus_injection.heartbeat`

**Metrics:**
```json
{
  "queue_depth": 234,
  "queue_max": 1000,
  "processed_last_minute": 45,
  "dropped_last_minute": 0,
  "avg_latency_ms": 67,
  "circuit_breakers": {
    "embedding": "closed|open|half_open",
    "vector_search": "closed|open|half_open"
  },
  "memory_mb": 156
}
```

**Critical Path:** YES for autonomy - without this, no stimuli enter system

**Key Safety Requirements:**
- ✅ Timeout on embedding (5s)
- ✅ Timeout on vector search (10s)
- ✅ Circuit breaker on embedding service failures
- ✅ Queue overflow handling (drop lowest priority)
- ✅ Deduplication by content digest (5 min window)

---

### 4. autonomy_orchestrator.py (NEW)

**Purpose:** L2 (organizational) autonomy - detect intents, assign missions, verify outcomes

**What It Does:**

**9-Stage Loop:**

1. **Stimulus → Intent**
   - Receives stimuli at L2 (org-wide events: errors, logs, partner DMs)
   - Chunks, embeds, retrieves relevant L2 nodes (projects, policies, goals)
   - Proposes IntentCards (candidate work items with evidence)

2. **Scoring (Priority P)**
   - Geometric mean of: severity, urgency, expected_yield, alignment, confidence
   - All factors z-scored vs current cohort (no fixed weights)
   - Penalties: risk, duplication
   - Formula: `P = GM(ŝ, û, ŷ, â, ĉ) × (1-r̂) × (1-d̂)`

3. **Safety Gates**
   - PoG (Proof-of-Grounding): citations to evidence, Q25 threshold
   - PoC (Proof-of-Competence): assignee success rate, z-scored vs peers
   - PoP (Proof-of-Permission): capabilities check (repos, envs, budgets)
   - If gates fail → escalate to human (Telegram ACK)

4. **Autonomy Level (L0-L4)**
   - L0: Log only (learning)
   - L1: Suggestion in WM (human picks)
   - L2: Create Task + plan, require 1-click ACK
   - L3: Auto-execute in sandbox/staging, open PR, request review
   - L4: Verified no-risk ops, fully automatic, still logged

5. **Assignment**
   - Match to Org LLM (L2) or Citizen (L1)
   - Matching score: GM(affinity, availability, competence, recency_penalty)
   - If citizen matched → auto-wake L1 with mission stimulus

6. **Auto-Wake (L1)**
   - Send mission stimulus to citizen's L1 graph
   - Bounded execution session (N strides or T ms)
   - WM includes mission + evidence + constraints
   - Citizen returns artifacts (diffs, PRs, replies, notes)

7. **Execution Controls**
   - Time budget (time_headroom / ema_stride_cost × health f(ρ))
   - Sandbox by default, promotion via tests
   - Plan → Act → Check cadence
   - Step-by-step with verification

8. **Verification (PoV)**
   - Tests passed OR
   - Independent retrieval corroboration OR
   - Human ACK OR
   - External API confirmation
   - If PoV < Q25 → cannot escalate beyond L2/L3

9. **Learning & Closeout**
   - Create Outcome node (status, artifacts, tests, feedback, time)
   - Update: link weights, node weights, citizen competence, source yields
   - Entity boundary ease/dominance if cross-entity strides occurred

**Key Features:**
- **Zero arbitrary constants** - all thresholds learned from data
- **Self-healing** - sentinels monitor quality, quarantine bad routes
- **Kill-switch** - disengages autonomy if health degrades
- **Full auditability** - every decision is an event + graph formation

**API Endpoints (if HTTP):**
- `POST /intent` - Manually create intent
- `GET /health` - Health check
- `GET /metrics` - Autonomy metrics

**Dependencies:**
- stimulus_injection_service (receives intents as stimuli)
- FalkorDB (intent storage, evidence retrieval)
- websocket_server (L1 citizen access)
- Telegram bot (for human ACK, if implemented)

**Port:** 8002 (if HTTP API)

**Heartbeat:** `.heartbeats/autonomy_orchestrator.heartbeat`

**Metrics:**
```json
{
  "active_intents": 12,
  "pending_missions": 3,
  "gate_pass_rates": {
    "PoG": 0.85,
    "PoC": 0.72,
    "PoP": 0.95
  },
  "autonomy_distribution": {
    "L0": 5, "L1": 10, "L2": 15, "L3": 8, "L4": 2
  },
  "sentinel_health": 0.82,
  "kill_switch": "disengaged|engaged",
  "memory_mb": 287
}
```

**Critical Path:** YES for autonomy - this is the brain of autonomous operation

**Key Safety Requirements:**
- ✅ Timeout on L1 auto-wake response (30s)
- ✅ Timeout on FalkorDB queries (10s)
- ✅ Verification required before L3/L4 escalation
- ✅ Kill-switch on sentinel health <threshold
- ✅ Quarantine routes with low success rates

---

## Dependency Graph & Startup Order

**CRITICAL: Services must start in this order**

```
FalkorDB (external check)
  ↓
websocket_server (engines need graph)
  ↓
conversation_watcher (TRACE → graph updates)
  ↓
stimulus_injection (needs embedding + graph)
  ↓
autonomy_orchestrator (needs stimulus service + intents)
  ↓
dashboard (visualization only)
```

**Rationale:**
- websocket_server needs FalkorDB for graph loading
- conversation_watcher needs websocket_server for graph writes
- stimulus_injection needs conversation_watcher pattern + engines
- autonomy_orchestrator needs stimulus_injection for intent processing
- dashboard needs all services for complete visualization

**Failure Cascade:**
If websocket_server fails → all downstream services fail
If stimulus_injection fails → autonomy_orchestrator cannot create intents
If autonomy_orchestrator fails → no autonomous action, but stimuli still process

---

## Operational Contract (All Services Must Implement)

### 1. PID Lock File

**Location:** `.{service_name}.lock`

**Content:** PID only (single line)

**Purpose:** Single-instance enforcement

**Guardian Behavior:**
- Checks if PID in lock file is running
- If duplicate detected → kills newer process
- If lock file stale (process dead) → removes lock

### 2. Heartbeat File

**Location:** `.heartbeats/{service_name}.heartbeat`

**Format:** JSON

**Required Fields:**
```json
{
  "component": "service_name",
  "timestamp": "2025-10-21T15:54:33.922966+00:00",
  "pid": 12345,
  "status": "active|degraded|critical"
}
```

**Optional Fields:**
```json
{
  "metrics": {
    // Service-specific health data
  }
}
```

**Update Frequency:** Every 5 seconds

**Guardian Behavior:**
- Stale threshold: 10 seconds
- If stale → kill and restart service
- If file missing → kill and restart service

### 3. Graceful Shutdown

**SIGTERM Handler Required:**
```python
import signal

def signal_handler(signum, frame):
    """Handle SIGTERM from guardian."""
    cleanup()
    PID_LOCK.unlink()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
```

**Cleanup Must:**
- Close database connections
- Flush pending writes
- Remove PID lock
- Exit with code 0 (clean shutdown)

### 4. Port Binding (if applicable)

**Requirement:** Must bind within 15 seconds

**Guardian Verification:**
- Uses `netstat -ano | findstr :{port} | findstr LISTENING`
- Checks every 1s for 15s
- If not bound within timeout → kills and restarts

### 5. Timeouts on ALL Blocking Operations

**External Dependencies:**
- FalkorDB queries: 10s max
- Embedding service: 5s max
- Vector search: 10s max
- HTTP requests: 5s max
- L1 auto-wake: 30s max

**Implementation Pattern:**
```python
import asyncio

async def safe_operation(operation, timeout_seconds):
    try:
        result = await asyncio.wait_for(operation(), timeout=timeout_seconds)
        return result
    except asyncio.TimeoutError:
        logger.error(f"Operation timed out after {timeout_seconds}s")
        return None
```

### 6. Circuit Breakers

**Required for External Dependencies:**
- Embedding service
- FalkorDB
- Telegram API

**Pattern:**
```python
from collections import deque
import time

class CircuitBreaker:
    def __init__(self, threshold=5, window=60):
        self.threshold = threshold
        self.window = window
        self.failures = deque(maxlen=20)
        self.state = "closed"  # closed|open|half_open

    def record_failure(self):
        self.failures.append(time.time())
        recent = sum(1 for t in self.failures if time.time() - t < self.window)
        if recent >= self.threshold:
            self.state = "open"

    def record_success(self):
        if self.state == "half_open":
            self.state = "closed"

    def allow_request(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.time() - self.failures[-1] > 30:
                self.state = "half_open"
                return True
            return False
        return True  # half_open
```

---

## Guardian Changes Required

**File:** `guardian.py`

**Changes:** MINOR (30 minutes, ~20 lines)

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
        'port': 8001,
        'heartbeat': '.heartbeats/stimulus_injection.heartbeat',
        'required': True
    },
    'autonomy_orchestrator': {
        'port': 8002,
        'heartbeat': '.heartbeats/autonomy_orchestrator.heartbeat',
        'required': True
    }
}
```

**No changes to monitoring logic** - same loop, just checks 2 more services

---

## Launcher Changes Required

**File:** `start_mind_protocol.py`

**Changes:** MODERATE (1-2 hours, ~80 lines)

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
    return False
```

**Update sequence in `start_core_services()`:**
```python
# Add after conversation_watcher
if not await self.start_stimulus_injection():
    return False

if not await self.start_autonomy_orchestrator():
    return False
```

---

## New Service Files Required

**Files to Create:**
1. `orchestration/stimulus_injection_service.py` (~800-1200 lines)
2. `orchestration/autonomy_orchestrator.py` (~1500-2000 lines)

**Both must implement:**
- PID lock management
- Heartbeat writing (every 5s)
- SIGTERM handler (graceful shutdown)
- Port binding (within 15s)
- Timeouts on all blocking ops
- Circuit breakers for external deps
- Rich metrics in heartbeat

**Service Boilerplate Pattern:**
See full implementation template in architecture doc sections above.

---

## Operational Monitoring Requirements

### Alert Thresholds

**Stimulus Injection:**
- ❌ CRITICAL: Heartbeat stale >10s → restart
- ❌ CRITICAL: Port 8001 not bound → restart
- ⚠️ WARNING: Queue depth >800/1000
- ⚠️ WARNING: Circuit breaker OPEN
- ⚠️ WARNING: Memory >500MB

**Autonomy Orchestrator:**
- ❌ CRITICAL: Heartbeat stale >10s → restart
- ❌ CRITICAL: Port 8002 not bound → restart
- ❌ CRITICAL: Kill-switch engaged → alert Nicolas
- ⚠️ WARNING: Sentinel health <0.5
- ⚠️ WARNING: Memory >1GB

### Dashboard Integration

**New Panels Needed:**
- Stimulus queue depth (real-time graph)
- Source effectiveness (g(source) values by type)
- Autonomy distribution (L0-L4 pie chart)
- Intent pipeline (created → assigned → completed)
- Gate pass rates (PoG/PoC/PoP over time)
- Sentinel health (time series)
- Kill-switch status (indicator)

---

## Phase-A Implementation (Minimal Viable Autonomy)

**Scope:** Answer-only autonomy with reduced features

**What to Build:**
1. Stimulus injection service (full implementation)
2. Autonomy orchestrator (reduced features):
   - Ingest agent answers only (not errors/logs yet)
   - Derive intents for clarify/continue tasks
   - Score with {urgency, alignment, confidence} only
   - Gate to L2/L3 only (no L4 auto-exec yet)
   - Assign to same citizen (self-handoff)
   - Require at least one evidence link for verification

**What to Defer:**
- Multi-source stimuli (Telegram, errors, logs)
- Full PoG/PoC/PoP learning (bootstrap with defaults)
- L4 full automation
- Sentinel learning (use fixed thresholds initially)
- Kill-switch (manual only)

**Timeline:** 3-5 days for Phase-A

**Capability:** Self-improving agent responses with verification

---

## Telegram Fast Reply (Full Feature)

**Requires:**
- Stimulus injection service ✅
- Autonomy orchestrator with:
  - Intent classification (reply_required vs FYI)
  - SLA learning (median reply times per partner)
  - L1 auto-wake micro-sessions
  - Reply generation with citations
  - One-tap feedback loop (👍/✍️/👎)
  - Partner allowlist (security)

**Timeline:** 5-7 days

**Capability:** Autonomous Telegram replies in safe cases, fast clarifications otherwise

---

## Success Criteria

**Stimulus Injection Service:**
- ✅ Receives stimuli from any source via HTTP API
- ✅ Processes with <100ms average latency
- ✅ Handles queue overflow gracefully (no crashes)
- ✅ Circuit breakers work (embedding service fails → degrades)
- ✅ Heartbeat updates every 5s with accurate metrics
- ✅ 100% uptime under guardian supervision

**Autonomy Orchestrator:**
- ✅ Creates intents from stimuli
- ✅ Scores with learned thresholds (no fixed constants)
- ✅ Gates pass/fail correctly (PoG/PoC/PoP)
- ✅ Assigns to best executor (citizen or Org LLM)
- ✅ Auto-wake works (L1 receives mission, executes, returns)
- ✅ Verification blocks ungrounded work (PoV enforcement)
- ✅ Sentinels detect degradation, quarantine bad routes
- ✅ Kill-switch engages on critical health loss
- ✅ 100% uptime under guardian supervision

---

## Victor's Operational Guarantee

**If both services implement the operational contract:**
- ✅ Guardian will keep them running forever
- ✅ Crashes will recover within 10s
- ✅ Chronic failures will be logged and alerted
- ✅ Circuit breakers will prevent cascade failures
- ✅ Exponential backoff will prevent restart loops
- ✅ 100% uptime is achievable

**If they don't implement the contract:**
- ❌ Timeouts missing → crash loop like websocket_server
- ❌ Circuit breakers missing → cascade failures
- ❌ Heartbeat missing → guardian can't monitor
- ❌ Graceful shutdown missing → zombie processes
- ❌ Uptime NOT guaranteed

**Build them right, and I'll resurrect them reliably.**

---

**End of Architecture Document**

**Next Steps:**
1. Ada implements stimulus_injection_service.py
2. Ada implements autonomy_orchestrator.py
3. Victor updates guardian.py (30 min)
4. Victor updates start_mind_protocol.py (1-2 hours)
5. Test Phase-A (answer-only autonomy)
6. Iterate to Telegram fast reply

**Reference Specs:**
- `docs/specs/consciousness_engine_architecture/mechanisms/stimulus_injection_specification.md`
- `docs/specs/consciousness_engine_architecture/autonomy/foundation.md`
- `docs/specs/consciousness_engine_architecture/autonomy/orcheestration_spec_v1.md`
