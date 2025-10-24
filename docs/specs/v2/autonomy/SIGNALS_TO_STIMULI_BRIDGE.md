# Signals → Stimuli Bridge

**Version:** 1.0
**Created:** 2025-10-24
**Purpose:** Route operational signals (logs, console errors, screenshots, code/doc changes, runtime events) into L2 consciousness as stimuli for automated task creation
**Status:** Specification (Phase-A2)
**Owner:** Atlas (collector + watchers), Iris (UI integration), orchestrator templates

---

## Overview

### What This Solves

**Problem:** Operational signals (error logs, console errors, code changes, runtime anomalies) exist but don't trigger autonomous remediation. They're visible to humans but invisible to consciousness systems.

**Solution:** Collect operational signals from multiple sources, normalize to StimulusEnvelope format, inject into L2 consciousness. Orchestrator auto-creates tasks (IntentCards), assigns to citizens, they execute autonomously.

**Result:** Closed-loop operational feedback:
- Errors → tasks → citizen fixes → learning (TRACE)
- Doc drift → tasks → sync updates → maintained coherence
- Runtime anomalies → tasks → introspection → self-improvement

---

### Architecture at a Glance

```
┌─────────────────┐
│ Signal Sources  │
│ - Logs          │
│ - Console       │
│ - Screenshots   │
│ - Git changes   │
│ - Runtime events│
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Signals Collector   │
│ (NEW microservice)  │
│ - Dedupe (5 min)    │
│ - Circuit breakers  │
│ - Quantile gates    │
│ - Priority scoring  │
└────────┬────────────┘
         │
         ▼ StimulusEnvelope
┌─────────────────────┐
│ Stimulus Injection  │
│ @8001 (EXISTING)    │
│ - Validation        │
│ - Scope routing     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Autonomy Orchestrator│
│ @8002 (EXISTING)    │
│ - Intent formation  │
│ - Mission creation  │
│ - Citizen auto-wake │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ L1 Citizens         │
│ - Execute missions  │
│ - Form learnings    │
└─────────────────────┘
```

**Key insight:** Reuse existing StimulusEnvelope + Stimulus Injection + Orchestrator infrastructure. Only add thin **Signals Collector** layer for normalization + noise control.

---

## Signal Sources

### 1. Backend Logs & System Errors

**Source:** Python service logs (websocket_server, stimulus_injection, orchestrator, runtime engines)

**Collection method:** Log tail or logger sink subscription

**Signal characteristics:**
- ERROR/WARN level log lines
- Stack traces when available
- Service identification from logger name

**Normalization to StimulusEnvelope:**
```json
{
  "stimulus_id": "uuid-v4",
  "timestamp_ms": 1730074800000,
  "scope": "organizational",
  "source_type": "error.log",
  "actor": "signals_collector",
  "content": "Service websocket_server: ValueError in handle_connection",
  "metadata": {
    "severity": "error",
    "service": "websocket_server",
    "stack": "Traceback...",
    "origin": "external",
    "origin_chain_depth": 0,
    "origin_chain": [],
    "dedupe_key": "sha256_hash_16"
  },
  "focality_hint": "focal",
  "interrupt": false
}
```

**Routing:**
- `scope: "organizational"` → N2 collective graph
- Orchestrator assigns to **Atlas** (backend/infrastructure) or **Victor** (ops/debugging)

---

### 2. Browser Console Errors (Next.js Dashboard)

**Source:** Client-side JavaScript errors and unhandled promise rejections

**Collection method:** Window event listeners (`error`, `unhandledrejection`) → beacon to Next.js API → collector

**Signal characteristics:**
- Error messages + stack traces
- Filename, line number, column number
- Promise rejection reasons

**Client-side beacon:**
```typescript
// app/consciousness/lib/console-beacon.ts
function post(path: string, body: any) {
  fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    keepalive: true,
  }).catch(() => {});
}

export function installConsoleBeacon() {
  if (typeof window === "undefined") return;

  window.addEventListener("error", (e) => {
    post("/api/signals/console", {
      message: e.message,
      stack: e.error?.stack,
      filename: e.filename,
      lineno: e.lineno,
      colno: e.colno,
    });
  });

  window.addEventListener("unhandledrejection", (e: PromiseRejectionEvent) => {
    const reason: any = e.reason;
    post("/api/signals/console", {
      message: typeof reason === "string" ? reason : (reason?.message ?? "Unhandled rejection"),
      stack: reason?.stack,
    });
  });
}
```

**Next.js API proxy:**
```typescript
// app/api/signals/console/route.ts
import { NextRequest, NextResponse } from "next/server";

const COLLECTOR_BASE = process.env.COLLECTOR_BASE ?? "http://localhost:8001";

export async function POST(req: NextRequest) {
  try {
    const payload = await req.json();

    const res = await fetch(`${COLLECTOR_BASE}/ingest/console`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json({ status: "error", error: text }, { status: 502 });
    }

    const data = await res.json();
    return NextResponse.json(data, { status: 200 });
  } catch (e: any) {
    return NextResponse.json({ status: "error", error: e?.message ?? "unknown" }, { status: 500 });
  }
}
```

**Normalization to StimulusEnvelope:**
```json
{
  "stimulus_id": "uuid-v4",
  "timestamp_ms": 1730074800000,
  "scope": "organizational",
  "source_type": "console",
  "actor": "signals_collector",
  "content": "TypeError: Cannot read properties of undefined",
  "metadata": {
    "severity": "error",
    "service": "dashboard",
    "stack": "TypeError: Cannot read...\n  at AutonomyIndicator.tsx:45...",
    "filename": "AutonomyIndicator.tsx",
    "lineno": 45,
    "origin": "external",
    "origin_chain_depth": 0,
    "dedupe_key": "sha256_hash_16"
  },
  "focality_hint": "focal",
  "interrupt": false
}
```

**Routing:**
- `scope: "organizational"` → N2 collective graph
- Orchestrator assigns to **Iris** (dashboard/UI errors)

---

### 3. Screenshots (Evidence Capture)

**Source:** Manual uploads from operators or automated screenshot capture tools

**Collection method:** HTTP multipart upload to collector

**Signal characteristics:**
- Image file (PNG, JPG)
- Optional context description
- Timestamp

**Next.js API proxy:**
```typescript
// app/api/signals/screenshot/route.ts
import { NextRequest, NextResponse } from "next/server";

const COLLECTOR_BASE = process.env.COLLECTOR_BASE ?? "http://localhost:8001";

export async function POST(req: NextRequest) {
  try {
    const form = await req.formData();
    const file = form.get("file");
    if (!(file instanceof File)) {
      return NextResponse.json({ status: "error", error: "file required" }, { status: 400 });
    }

    const forward = new FormData();
    forward.set("file", file, file.name);

    const res = await fetch(`${COLLECTOR_BASE}/ingest/screenshot`, {
      method: "POST",
      body: forward as any,
      cache: "no-store",
    });

    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json({ status: "error", error: text }, { status: 502 });
    }

    const data = await res.json();
    return NextResponse.json(data, { status: 200 });
  } catch (e: any) {
    return NextResponse.json({ status: "error", error: e?.message ?? "unknown" }, { status: 500 });
  }
}
```

**Normalization to StimulusEnvelope:**
```json
{
  "stimulus_id": "uuid-v4",
  "timestamp_ms": 1730074800000,
  "scope": "organizational",
  "source_type": "screenshot",
  "actor": "signals_collector",
  "content": "Screenshot evidence",
  "metadata": {
    "severity": "info",
    "screenshot_path": "data/evidence/1730074800000_error_state.png",
    "description": "Dashboard frozen state",
    "origin": "external",
    "origin_chain_depth": 0,
    "dedupe_key": "sha256_hash_16"
  },
  "focality_hint": "focal",
  "interrupt": false
}
```

**Storage:** Collector stores files to `data/evidence/{timestamp}_{filename}`, includes path in metadata

**Routing:**
- `scope: "organizational"` → N2 collective graph
- Orchestrator assigns based on context (usually **Iris** for UI issues, **Atlas** for backend)

---

### 4. Code/Doc Synchronization (Bidirectional Drift Detection)

**Source:** Git repository watchers monitoring `orchestration/` (code) and `docs/specs/v2/` (docs)

**Collection method:** Git watcher compares file modification times, checks SCRIPT_MAP.md mappings

**Signal characteristics:**
- File path changed (code or doc)
- Mapped counterpart file (from SCRIPT_MAP.md)
- Time since counterpart last updated
- Git commit hash + diff

**Heuristics:**
- **Code → Doc drift:** Script changed, mapped doc untouched >24 hours → "Update documentation"
- **Doc → Code drift:** Spec changed, mapped script untouched >24 hours → "Update implementation"

**Normalization to StimulusEnvelope (code change):**
```json
{
  "stimulus_id": "uuid-v4",
  "timestamp_ms": 1730074800000,
  "scope": "organizational",
  "source_type": "code_change",
  "actor": "git_watcher",
  "content": "Code changed without doc update: traversal_v2.py",
  "metadata": {
    "severity": "warn",
    "file_path": "orchestration/mechanisms/traversal_v2.py",
    "counterpart_path": "docs/specs/v2/traversal/fanout_strategy.md",
    "counterpart_type": "documentation",
    "gap_reason": "stale counterpart >24 hours",
    "commit": "abc123def",
    "diff": "- K=3\n+ K=2\n",
    "origin": "external",
    "origin_chain_depth": 0,
    "dedupe_key": "sha256_hash_16"
  },
  "focality_hint": "focal",
  "interrupt": false
}
```

**Normalization to StimulusEnvelope (doc change):**
```json
{
  "stimulus_id": "uuid-v4",
  "timestamp_ms": 1730074800000,
  "scope": "organizational",
  "source_type": "doc_change",
  "actor": "git_watcher",
  "content": "Documentation changed without code update: health_spec.md",
  "metadata": {
    "severity": "warn",
    "file_path": "docs/specs/v2/runtime_engine/phenomenological_health.md",
    "counterpart_path": "orchestration/mechanisms/health_aggregator.py",
    "counterpart_type": "script",
    "gap_reason": "stale counterpart >24 hours",
    "commit": "xyz789abc",
    "diff": "- threshold: 0.4\n+ threshold: 0.5\n",
    "origin": "external",
    "origin_chain_depth": 0,
    "dedupe_key": "sha256_hash_16"
  },
  "focality_hint": "focal",
  "interrupt": false
}
```

**Routing:**
- Code change → Doc update: Assign to **Ada** (spec authoring)
- Doc change → Code update: Assign to **Atlas** (implementation)

---

### 5. Self-Awareness: Runtime Events → Stimuli (With Loop Guards)

**Source:** WebSocket events already emitted by consciousness engines

**Collection method:** WebSocket subscriber (`ws_reinjector.py`) listens to specific event types

**When to re-stimulate:**

| Runtime Event | Condition | Stimulus Content | Assignee |
|---------------|-----------|------------------|----------|
| `criticality.state` | safety_state != 'safe' for >M frames | "Safety regression: ρ unsafe" | Victor/Atlas |
| `wm.emit` | <3 entities for >T frames | "Attention starvation: WM underutilized" | Luca/Felix |
| `weights.updated` | Same small node set >N updates | "Learning drift: over-fitting detected" | Felix |
| `health.phenomenological` | health_band == 'critical' sustained | "Health critical: {narrative}" | Felix/Atlas |

**Guards against loops (CRITICAL):**

1. **Origin tagging:** All reinjected stimuli have `metadata.origin = "self_observation"`
2. **Depth limit:** `metadata.origin_chain_depth` increments on each reinjection. **MAX_DEPTH = 2** (configurable).
3. **TTL:** `metadata.ttl_frames` decrements each cycle. Drop at 0.
4. **Never re-ingest self-observation stimuli:** If incoming stimulus has `origin="self_observation"`, collector **never reinjests it again**.
5. **Rate limiting:** Per event type (e.g., max 1 criticality stimulus per 100 frames).
6. **Execution mode gating:** If `origin_chain_depth >= MAX_DEPTH`, orchestrator sets `execution_mode = "ACK_REQUIRED"` (requires human approval).

**Normalization to StimulusEnvelope (self-observation):**
```json
{
  "stimulus_id": "uuid-v4",
  "timestamp_ms": 1730074800000,
  "scope": "organizational",
  "source_type": "runtime",
  "actor": "ws_reinjector",
  "content": "Safety regression: ρ unsafe for 50 frames",
  "metadata": {
    "severity": "error",
    "service": "runtime",
    "event_type": "criticality.state",
    "frame_id": 12345,
    "safety_state": "unsafe",
    "origin": "self_observation",
    "origin_chain_depth": 1,
    "origin_chain": ["parent_stimulus_id"],
    "ttl_frames": 600,
    "rate_limit_bucket": "runtime:criticality",
    "dedupe_key": "sha256_hash_16"
  },
  "focality_hint": "focal",
  "interrupt": false
}
```

**Routing:**
- `scope: "organizational"` → N2 collective graph
- Assigns based on event type (see table above)

---

## Signals Collector Service Specification

### Service Overview

**File:** `orchestration/services/signals_collector.py`
**Framework:** HTTP service (FastAPI; alternative frameworks acceptable if they expose identical endpoints and heartbeat behavior)
**Port:** 8003 (configurable via `SIGNALS_COLLECTOR_PORT` env var)
**Heartbeat:** `.heartbeats/signals_collector.heartbeat` (updated every 5 seconds)
**Guardian:** Supervised by guardian.py, auto-restart on crash

---

### Core Responsibilities

1. **Accept signals** from multiple sources via HTTP endpoints
2. **Normalize** to StimulusEnvelope format
3. **Deduplicate** within 5-minute rolling window (digest-based)
4. **Rate limit** per bucket (prevent signal storms)
5. **Apply quantile gates** (priority scoring with adaptive thresholds)
6. **Forward** to Stimulus Injection API (`POST /inject` @8001)
7. **Circuit breakers** for optional enrichments (OCR, symbolization)

---

### HTTP Endpoints

#### POST /ingest/console
**Purpose:** Accept browser console errors from Next.js beacon

**Request body:**
```json
{
  "message": "TypeError: Cannot read properties of undefined",
  "stack": "TypeError: ...\n  at Component:45",
  "filename": "AutonomyIndicator.tsx",
  "lineno": 45,
  "colno": 12
}
```

**Response (success):**
```json
{
  "status": "injected",
  "stimulus_id": "uuid-v4",
  "dedupe_key": "sha256_hash_16"
}
```

**Response (deduplicated):**
```json
{
  "status": "deduplicated",
  "dedupe_key": "sha256_hash_16",
  "count": 5
}
```

---

#### POST /ingest/log
**Purpose:** Accept backend log error entries

**Request body:**
```json
{
  "title": "Service error in websocket_server",
  "level": "error",
  "service": "websocket_server",
  "stack": "Traceback (most recent call last)...",
  "timestamp_ms": 1730074800000
}
```

**Response:** Same as `/ingest/console`

---

#### POST /ingest/screenshot
**Purpose:** Accept screenshot uploads for evidence attachment

**Request:** Multipart form data with `file` field

**Response:**
```json
{
  "status": "injected",
  "stimulus_id": "uuid-v4",
  "screenshot_path": "data/evidence/1730074800000_error_state.png"
}
```

---

#### GET /health
**Purpose:** Health check for guardian monitoring

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 12345,
  "signals_ingested": 456,
  "signals_deduplicated": 123,
  "signals_rate_limited": 7
}
```

---

### Deduplication Strategy

**Algorithm:** Rolling 5-minute digest window

```python
import hashlib, time
from collections import defaultdict

DEDUPE_WINDOW_SEC = 300  # 5 minutes
recent_digests = {}  # digest → (first_seen_ts, count)

def dedupe(content: str, stack: str = "") -> tuple[bool, str]:
    """
    Returns (is_duplicate, digest)
    """
    digest_input = content + stack
    digest = hashlib.sha256(digest_input.encode()).hexdigest()[:16]

    now = time.time()

    if digest in recent_digests:
        first_seen, count = recent_digests[digest]
        if now - first_seen < DEDUPE_WINDOW_SEC:
            # Still within window
            recent_digests[digest] = (first_seen, count + 1)
            return True, digest

    # New or expired
    recent_digests[digest] = (now, 1)
    return False, digest
```

**Cleanup:** Periodically remove digests older than window (every 60 seconds)

---

### Rate Limiting

**Strategy:** Token bucket per `rate_limit_bucket` (e.g., `"console:TypeError"`, `"runtime:criticality"`)

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, rate_per_min=10):
        self.rate_per_min = rate_per_min
        self.buckets = defaultdict(lambda: {"tokens": rate_per_min, "last_refill": time.time()})

    def allow(self, bucket: str) -> bool:
        now = time.time()
        b = self.buckets[bucket]

        # Refill tokens based on elapsed time
        elapsed = now - b["last_refill"]
        tokens_to_add = elapsed * (self.rate_per_min / 60.0)
        b["tokens"] = min(self.rate_per_min, b["tokens"] + tokens_to_add)
        b["last_refill"] = now

        if b["tokens"] >= 1.0:
            b["tokens"] -= 1.0
            return True
        return False
```

**Configuration:** `RATE_LIMIT_PER_MIN` env var (default 10)

---

### Priority Scoring (Quantile Gates)

**Formula:**
```
P = z(severity) × w1
  + z(recency) × w2
  + z(recurrence) × w3
  + z(blast_radius) × w4
  + z(service_criticality) × w5
```

Where:
- `z(x)` = z-score or percentile from rolling histogram
- `w1..w5` = configurable weights (default 1.0 each)

**Component definitions:**

| Component | Source | Computation |
|-----------|--------|-------------|
| `severity` | metadata.severity | Map: error=1.0, warn=0.6, info=0.3 |
| `recency` | timestamp_ms | 1.0 / (1 + minutes_since) |
| `recurrence` | dedupe count | log(1 + count) |
| `blast_radius` | metadata.service | Map: runtime=1.0, dashboard=0.8, orchestration=0.9, watcher=0.5 |
| `service_criticality` | metadata.service | Map: runtime=1.0, orchestration=0.9, websocket=0.8, dashboard=0.6, watcher=0.4 |

**Quantile gates:**
- **Q75 (75th percentile):** Escalate signals above this threshold
- **Q90 (90th percentile):** Hard escalation (interrupt=true)
- **EMA smoothing:** α=0.2 for percentile estimates

**Configuration:** `PRIORITY_WEIGHTS` env var (JSON: `{"w1": 1.0, "w2": 1.0, ...}`)

**Output:** Priority score 0.0-1.0 included in `metadata.priority` when forwarding to injector

---

### Circuit Breakers (Optional Enrichments)

**Pattern:** For non-critical enrichments (OCR, symbolization), use circuit breakers to prevent service degradation

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_seconds=60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failures = 0
        self.state = "closed"  # closed | open | half_open
        self.opened_at = None

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            # Check if timeout elapsed
            if time.time() - self.opened_at > self.timeout_seconds:
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker open")

        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "open"
                self.opened_at = time.time()
            raise e
```

**Usage:** Wrap optional enrichment calls (e.g., OCR on screenshots) with circuit breaker

---

### Collector Implementation Skeleton

```python
# orchestration/services/signals_collector.py
from fastapi import FastAPI, UploadFile, HTTPException
import httpx, time, hashlib, asyncio, os
from collections import defaultdict, deque

app = FastAPI(title="Signals Collector", version="1.0")

INJECTOR_URL = os.getenv("INJECTOR_URL", "http://localhost:8001")
DEDUPE_WINDOW_SEC = 300
MAX_DEPTH = int(os.getenv("MAX_DEPTH", "2"))

# State
recent_digests = {}  # digest → (ts, count)
rate_limiter = RateLimiter(rate_per_min=10)
stats = {"ingested": 0, "deduplicated": 0, "rate_limited": 0}
start_time = time.time()

def dedupe(content: str, stack: str = "") -> tuple[bool, str]:
    digest = hashlib.sha256((content + stack).encode()).hexdigest()[:16]
    now = time.time()

    if digest in recent_digests:
        first_seen, count = recent_digests[digest]
        if now - first_seen < DEDUPE_WINDOW_SEC:
            recent_digests[digest] = (first_seen, count + 1)
            return True, digest

    recent_digests[digest] = (now, 1)
    return False, digest

async def forward_to_injector(envelope: dict) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{INJECTOR_URL}/inject", json=envelope)
        resp.raise_for_status()
        return resp.json()

@app.post("/ingest/console")
async def ingest_console(msg: dict):
    content = msg.get("message", "Console error")
    stack = msg.get("stack", "")

    deduped, digest = dedupe(content, stack)
    if deduped:
        stats["deduplicated"] += 1
        return {"status": "deduplicated", "dedupe_key": digest, "count": recent_digests[digest][1]}

    if not rate_limiter.allow("console:error"):
        stats["rate_limited"] += 1
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    envelope = {
        "stimulus_id": hashlib.md5(f"{time.time()}:{content}".encode()).hexdigest(),
        "timestamp_ms": int(time.time() * 1000),
        "scope": "organizational",
        "source_type": "console",
        "actor": "signals_collector",
        "content": content,
        "metadata": {
            "severity": "error",
            "service": "dashboard",
            "stack": stack,
            "filename": msg.get("filename"),
            "lineno": msg.get("lineno"),
            "origin": "external",
            "origin_chain_depth": 0,
            "origin_chain": [],
            "dedupe_key": digest
        },
        "focality_hint": "focal",
        "interrupt": False
    }

    result = await forward_to_injector(envelope)
    stats["ingested"] += 1
    return {"status": "injected", "stimulus_id": envelope["stimulus_id"], "dedupe_key": digest}

@app.post("/ingest/log")
async def ingest_log(item: dict):
    content = item.get("title", "Service error")
    stack = item.get("stack", "")

    deduped, digest = dedupe(content, stack)
    if deduped:
        stats["deduplicated"] += 1
        return {"status": "deduplicated", "dedupe_key": digest}

    bucket = f"log:{item.get('service','unknown')}"
    if not rate_limiter.allow(bucket):
        stats["rate_limited"] += 1
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    envelope = {
        "stimulus_id": hashlib.md5(f"{time.time()}:{content}".encode()).hexdigest(),
        "timestamp_ms": item.get("timestamp_ms", int(time.time() * 1000)),
        "scope": "organizational",
        "source_type": "error.log",
        "actor": "signals_collector",
        "content": content,
        "metadata": {
            "severity": item.get("level", "error"),
            "service": item.get("service", "unknown"),
            "stack": stack,
            "origin": "external",
            "origin_chain_depth": 0,
            "origin_chain": [],
            "dedupe_key": digest
        },
        "focality_hint": "focal",
        "interrupt": False
    }

    result = await forward_to_injector(envelope)
    stats["ingested"] += 1
    return {"status": "injected", "stimulus_id": envelope["stimulus_id"]}

@app.post("/ingest/screenshot")
async def ingest_screenshot(file: UploadFile):
    timestamp = int(time.time() * 1000)
    filename = f"{timestamp}_{file.filename}"
    filepath = f"data/evidence/{filename}"

    os.makedirs("data/evidence", exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    envelope = {
        "stimulus_id": hashlib.md5(f"{timestamp}:{file.filename}".encode()).hexdigest(),
        "timestamp_ms": timestamp,
        "scope": "organizational",
        "source_type": "screenshot",
        "actor": "signals_collector",
        "content": "Screenshot evidence",
        "metadata": {
            "severity": "info",
            "screenshot_path": filepath,
            "origin": "external",
            "origin_chain_depth": 0,
            "origin_chain": []
        },
        "focality_hint": "focal",
        "interrupt": False
    }

    result = await forward_to_injector(envelope)
    stats["ingested"] += 1
    return {"status": "injected", "stimulus_id": envelope["stimulus_id"], "screenshot_path": filepath}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "uptime_seconds": int(time.time() - start_time),
        "signals_ingested": stats["ingested"],
        "signals_deduplicated": stats["deduplicated"],
        "signals_rate_limited": stats["rate_limited"]
    }

# Heartbeat writer (background task)
@app.on_event("startup")
async def start_heartbeat():
    async def write_heartbeat():
        while True:
            os.makedirs(".heartbeats", exist_ok=True)
            with open(".heartbeats/signals_collector.heartbeat", "w") as f:
                f.write(str(int(time.time() * 1000)))
            await asyncio.sleep(5)

    asyncio.create_task(write_heartbeat())

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SIGNALS_COLLECTOR_PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

## Orchestrator Integration: Intent Patterns

### Intent Templates File

**Location:** `orchestration/services/orchestrator/intent_templates.yaml`

**Format:** Declarative intent patterns with match conditions, routing, and mission templates

```yaml
version: 1
intents:

  - name: intent.fix_incident
    description: Fix an operational incident originating from logs, browser console, or runtime health.
    match:
      any:
        - equals: { path: source_type, value: "error.log" }
        - equals: { path: source_type, value: "console" }
        - equals: { path: source_type, value: "runtime" }
    priority:
      # P is already computed by the collector; if absent, compute fallback
      compute_if_missing:
        formula: "z(severity)*1.0 * z(recency)*1.0 * z(recurrence)*1.0 * z(blast_radius)*1.0 * z(service_criticality)*1.0"
    assign:
      routing:
        # Prefer explicit citizen hint
        - when: { exists: metadata.citizen_hint }
          assignee: "{{ metadata.citizen_hint }}"
        # Backend/services incidents → Atlas or Victor
        - when: { in: { path: metadata.service, values: ["websocket_server","stimulus_injection","autonomy_orchestrator","orchestration","runtime"] } }
          assignee: "atlas"
        - when: { equals: { path: metadata.category, value: "safety" } }
          assignee: "victor"
        # Dashboard/console incidents → Iris
        - when: { in: { path: metadata.service, values: ["dashboard","nextjs","console"] } }
          assignee: "iris"
        # Fallback triage
        - default: "ada"
    mission_template:
      title: "Investigate & resolve: {{ content }}"
      body: |
        **Service:** {{ metadata.service | default("unknown") }}
        **Severity:** {{ metadata.severity | default("error") }}
        **Evidence:**
        {{#if metadata.stack}}Stack:\n{{ metadata.stack }}\n{{/if}}
        {{#if metadata.screenshot_path}}Screenshot: {{ metadata.screenshot_path }}\n{{/if}}
        {{#if metadata.diff}}Diff:\n{{ metadata.diff }}\n{{/if}}
        **Acceptance:**
        - Error no longer reproducible
        - Add regression test or guard if applicable
        - Close-the-loop note in SYNC.md

  - name: intent.sync_docs_scripts
    description: Keep docs and code synchronized; trigger when script/doc change lacks its mapped counterpart.
    match:
      any:
        - equals: { path: source_type, value: "code_change" }
        - equals: { path: source_type, value: "doc_change" }
    priority:
      compute_if_missing:
        formula: "z(recency)*1.0 * z(service_criticality)*1.0 * z(recurrence)*1.0"
    assign:
      routing:
        - when: { equals: { path: source_type, value: "code_change" } }
          assignee: "ada"    # author spec update
        - when: { equals: { path: source_type, value: "doc_change" } }
          assignee: "atlas"  # update implementation
        - default: "ada"
    mission_template:
      title: "Sync {{ source_type }} with counterpart"
      body: |
        **Change:** {{ metadata.file_path | default("n/a") }} @ {{ metadata.commit | default("HEAD") }}
        **Detected gap:** {{ metadata.gap_reason | default("stale counterpart > 24 hours") }}
        **Action:**
        - Update {{ metadata.counterpart_type }} at {{ metadata.counterpart_path }}
        - Reference SCRIPT_MAP.md mapping in commit message
        **Acceptance:**
        - CI green with updated tests
        - Cross-link PRs (code↔doc) and close gap tracker
```

**Orchestrator loading:**
- Parse YAML on startup
- For each incoming stimulus, check `match` conditions
- If matched, compute priority (use collector's P if available, else compute)
- Route to assignee via routing rules
- Render mission template with stimulus metadata
- Create IntentCard → Mission → Auto-wake L1 citizen

---

## Self-Awareness Loop Guards (Loop Prevention)

### Metadata Fields for Loop Prevention

All StimulusEnvelope instances MUST include these fields in `metadata`:

```typescript
{
  "origin": "external" | "self_observation",
  "origin_chain_depth": number,  // default 0
  "origin_chain": string[],      // array of ancestor stimulus_ids
  "ttl_frames": number,          // default 600; ignored if origin="external"
  "rate_limit_bucket": string    // e.g., "console:TypeError", "runtime:criticality"
}
```

---

### Guard Rules

**Rule 1: Origin Tagging**
- All stimuli from external sources: `origin = "external"`
- All stimuli from runtime event reinjection: `origin = "self_observation"`

**Rule 2: Depth Limit**
- `MAX_DEPTH = 2` (configurable)
- If incoming stimulus has `origin_chain_depth >= MAX_DEPTH`, **drop it** (do not reinject)
- When reinjecting runtime event as stimulus, increment `origin_chain_depth` and append `stimulus_id` to `origin_chain`

**Rule 3: TTL Decrement**
- If `origin = "self_observation"`, decrement `ttl_frames` on each reinjection
- Drop if `ttl_frames <= 0`

**Rule 4: Never Re-Ingest Self-Observation**
- If collector receives stimulus with `origin = "self_observation"`, **never reinject it again**
- Only `ws_reinjector.py` creates `self_observation` stimuli

**Rule 5: Rate Limiting**
- Per `rate_limit_bucket` (e.g., `"runtime:criticality"`)
- Max 1 stimulus per bucket per N frames (configurable, default 100 frames)

**Rule 6: Execution Mode Gating**
- If orchestrator creates mission from stimulus with `origin_chain_depth >= MAX_DEPTH`, set `execution_mode = "ACK_REQUIRED"`
- Human must approve before citizen executes

---

### WS Reinjector Implementation Pattern

```python
# orchestration/services/watchers/ws_reinjector.py
import asyncio, websockets, httpx, time, os
from collections import defaultdict

COLLECTOR_URL = os.getenv("COLLECTOR_URL", "http://localhost:8003")
WS_URL = os.getenv("CONSCIOUSNESS_WS_URL", "ws://localhost:8000/ws")
MAX_DEPTH = int(os.getenv("MAX_DEPTH", "2"))
RATE_LIMIT_FRAMES = int(os.getenv("REINJECTION_RATE_LIMIT_FRAMES", "100"))

# Rate limiting state
last_reinject = defaultdict(lambda: 0)  # bucket → frame_id

async def should_reinject(event_type: str, frame_id: int) -> bool:
    bucket = f"runtime:{event_type}"
    if frame_id - last_reinject[bucket] < RATE_LIMIT_FRAMES:
        return False
    last_reinject[bucket] = frame_id
    return True

async def reinject_as_stimulus(event_type: str, content: str, metadata: dict):
    # Add self-observation metadata
    metadata.update({
        "origin": "self_observation",
        "origin_chain_depth": 1,  # First reinjection
        "origin_chain": [],
        "ttl_frames": 600,
        "rate_limit_bucket": f"runtime:{event_type}"
    })

    envelope = {
        "stimulus_id": hashlib.md5(f"{time.time()}:{content}".encode()).hexdigest(),
        "timestamp_ms": int(time.time() * 1000),
        "scope": "organizational",
        "source_type": "runtime",
        "actor": "ws_reinjector",
        "content": content,
        "metadata": metadata,
        "focality_hint": "focal",
        "interrupt": False
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{COLLECTOR_URL}/ingest/runtime", json=envelope)
        resp.raise_for_status()

async def listen_and_reinject():
    async with websockets.connect(WS_URL) as ws:
        async for message in ws:
            event = json.loads(message)
            event_type = event.get("event_type")

            # Criticality check
            if event_type == "criticality.state":
                if event.get("safety_state") != "safe":
                    frame_id = event.get("frame_id", 0)
                    if await should_reinject("criticality", frame_id):
                        await reinject_as_stimulus(
                            "criticality.state",
                            f"Safety regression: ρ unsafe for frame {frame_id}",
                            {
                                "severity": "error",
                                "service": "runtime",
                                "event_type": "criticality.state",
                                "frame_id": frame_id,
                                "safety_state": event.get("safety_state")
                            }
                        )

            # WM starvation check
            elif event_type == "wm.emit":
                entities = event.get("selected_entities", [])
                if len(entities) < 3:
                    frame_id = event.get("frame_id", 0)
                    if await should_reinject("wm_starvation", frame_id):
                        await reinject_as_stimulus(
                            "wm.emit",
                            f"Attention starvation: WM has only {len(entities)} entities",
                            {
                                "severity": "warn",
                                "service": "runtime",
                                "event_type": "wm.emit",
                                "frame_id": frame_id,
                                "entity_count": len(entities)
                            }
                        )

if __name__ == "__main__":
    asyncio.run(listen_and_reinject())
```

**Key points:**
- Only creates stimuli with `origin = "self_observation"`
- Increments `origin_chain_depth` starting at 1
- Rate-limits per event type
- Collector will drop if depth exceeds MAX_DEPTH

---

## Acceptance Tests

### Test 1: Incident E2E (Console Error)

**Scenario:** Browser console error → task creation → citizen fix → learning

**Steps:**
1. Trigger console error in dashboard (e.g., access undefined property)
2. Beacon sends to `/api/signals/console`
3. Next.js proxy forwards to collector `/ingest/console`
4. Collector normalizes to StimulusEnvelope, forwards to injector `/inject`
5. Injector validates, routes to N2 graph
6. Orchestrator matches `intent.fix_incident`, creates IntentCard
7. Mission assigned to **Iris** (service="dashboard")
8. Iris receives mission, investigates, adds null check
9. `weights.updated` event emitted on learning

**Verification:**
- Stimulus appears in N2 graph
- IntentCard created with correct assignee
- Mission text includes stack trace
- `weights.updated` event observed
- Error no longer reproducible

---

### Test 2: Doc-Sync E2E (Code Change)

**Scenario:** Script changed without doc update → task creation → doc updated

**Steps:**
1. Modify `orchestration/mechanisms/traversal_v2.py` (e.g., change K=3 to K=2)
2. Leave mapped doc `docs/specs/v2/traversal/fanout_strategy.md` untouched >24 hours
3. Git watcher detects drift, emits `code_change` stimulus
4. Collector forwards to injector
5. Orchestrator matches `intent.sync_docs_scripts`, assigns to **Ada**
6. Ada updates doc to reflect K=2 change
7. PR references SCRIPT_MAP.md mapping

**Verification:**
- Stimulus includes diff and counterpart paths
- IntentCard assigns to Ada
- Doc updated and committed
- SCRIPT_MAP.md mapping referenced in commit message

---

### Test 3: Self-Awareness Guarded (Depth Limit)

**Scenario:** Runtime anomaly → reinjection → mission → second reinjection → depth cap

**Steps:**
1. Induce sustained `criticality.state` unsafe (e.g., disable safety checks in test)
2. WS reinjector creates stimulus with `origin="self_observation"`, `origin_chain_depth=1`
3. Orchestrator creates mission to Victor/Atlas
4. Citizen executes, but criticality still unsafe (simulated persistent failure)
5. WS reinjector attempts second reinjection
6. Collector sees `origin_chain_depth=1`, increments to 2 (MAX_DEPTH), forwards
7. Orchestrator creates mission with `execution_mode="ACK_REQUIRED"`
8. Mission waits for human approval (does not auto-execute)

**Verification:**
- First stimulus: `origin_chain_depth=1`, mission auto-executes
- Second stimulus: `origin_chain_depth=2`, mission requires ACK
- No third stimulus (depth limit prevents further reinjection)
- No infinite loop

---

### Test 4: Noise Resistance (Deduplication)

**Scenario:** Same error repeated 20 times in 1 minute → only first injected

**Steps:**
1. Trigger same console error 20 times rapidly (e.g., button click loop)
2. Beacon sends 20 requests to `/api/signals/console`
3. Collector deduplicates based on message + stack digest
4. First request: `status="injected"`
5. Requests 2-20: `status="deduplicated"`, `count` increments

**Verification:**
- Only 1 stimulus created in N2 graph
- 19 requests return `deduplicated` status
- Dedupe count visible in collector stats (`/health`)

---

## Safety Guarantees

### 1. No Runaway Loops

**Guarantee:** Self-awareness reinjection cannot create infinite loops

**Mechanisms:**
- Origin tagging prevents re-ingestion of self-observation stimuli
- Depth limit (MAX_DEPTH=2) caps cascading
- TTL ensures stimuli expire
- Rate limiting prevents storms
- Execution mode gating requires human approval at depth limit

**Verification:** Test 3 (Self-Awareness Guarded) validates these mechanisms

---

### 2. Signal Noise Does Not Destabilize Consciousness

**Guarantee:** High-volume signal sources (logs, console) cannot overwhelm L2 consciousness or exhaust energy

**Mechanisms:**
- Deduplication (5-minute window) collapses repeated signals
- Rate limiting (token bucket) prevents signal storms
- Quantile gates ensure only high-priority signals escalate
- Collector is isolated from consciousness engines (failures don't crash engines)

**Verification:** Test 4 (Noise Resistance) validates deduplication

---

### 3. Sentinel Retains Kill-Switch Authority

**Guarantee:** Sentinel can still enforce ACK_REQUIRED and halt autonomy regardless of signal source

**Mechanisms:**
- Orchestrator respects sentinel state before mission execution
- If criticality/trust/quality degraded, all missions flip to ACK_REQUIRED
- Signals bridge does NOT bypass sentinel checks

**Verification:** Sentinel tests from Phase-A1 remain valid; signals-sourced missions subject to same rules

---

### 4. Optional Enrichments Do Not Block Core Path

**Guarantee:** Failures in optional enrichments (OCR, symbolization) do not prevent signal injection

**Mechanisms:**
- Circuit breakers wrap optional calls
- If breaker opens, core injection proceeds without enrichment
- Enrichment failures logged but don't raise exceptions

**Verification:** Simulate OCR service failure; verify signals still inject successfully

---

## Implementation Checklist

### Phase-A2 Tasks

**[A2-1] Signals Collector Service** (Owner: Atlas/Victor)
- [ ] Implement FastAPI service with 4 endpoints (`/ingest/console`, `/ingest/log`, `/ingest/screenshot`, `/health`)
- [ ] Add deduplication logic (5-minute rolling window)
- [ ] Add rate limiting (token bucket per bucket key)
- [ ] Add priority scoring (quantile gates with configurable weights)
- [ ] Add heartbeat writer (every 5 seconds to `.heartbeats/signals_collector.heartbeat`)
- [ ] Wire to Stimulus Injection API (`POST /inject` @8001)
- [ ] Add to guardian supervision (`SERVICES` list)
- [ ] Deploy and verify `/health` endpoint

**[A2-2] Signal Source Watchers** (Owner: Atlas)
- [ ] Implement `log_tail.py` watcher for backend logs
- [ ] Implement `git_watcher.py` for code/doc drift detection (uses SCRIPT_MAP.md)
- [ ] Implement `ws_reinjector.py` for runtime event reinjection (with loop guards)
- [ ] Add all watchers to guardian supervision
- [ ] Verify each watcher forwards to collector correctly

**[A2-3] Orchestrator Intent Templates** (Owner: Atlas)
- [ ] Create `intent_templates.yaml` with `intent.fix_incident` and `intent.sync_docs_scripts`
- [ ] Implement template parser in orchestrator
- [ ] Wire match conditions, routing, and mission template rendering
- [ ] Verify IntentCard creation from test stimuli
- [ ] Verify missions route to correct citizens (Iris for console, Ada for doc-sync, etc.)

**[A2-4] Next.js Integration** (Owner: Iris)
- [ ] Create `app/api/signals/console/route.ts` (proxy to collector)
- [ ] Create `app/api/signals/screenshot/route.ts` (multipart proxy)
- [ ] Create `app/consciousness/lib/console-beacon.ts` (client beacon)
- [ ] Install beacon in root client layout (`installConsoleBeacon()`)
- [ ] Test: trigger console error, verify reaches collector
- [ ] Optional: Create StimuliFeed UI panel to display recent signals

**[A2-5] Acceptance Tests** (Owner: All)
- [ ] Test 1: Console error E2E (Iris)
- [ ] Test 2: Doc-sync E2E (Ada/Atlas)
- [ ] Test 3: Self-awareness guarded (Victor/Atlas)
- [ ] Test 4: Noise resistance (Atlas)
- [ ] All tests pass and documented in test suite

---

## References

### Existing Specifications
- `PHASE_A_MINIMAL_SPECIFICATION.md` - Service startup sequence, existing components
- `tick_speed_semantics.md` v1.1 - Quantile gates pattern (reused for priority scoring)
- `phenomenological_health.md` v1.1 - Self-awareness use case (health critical reinjection)

### Existing Infrastructure
- Stimulus Injection API (`@8001/inject`) - Accepts StimulusEnvelope
- Autonomy Orchestrator (`@8002`) - Creates IntentCards and missions
- Guardian (`guardian.py`) - Supervises services, auto-restart

### New Components
- Signals Collector (`@8003`) - This specification
- Intent templates (`intent_templates.yaml`) - This specification
- Signal source watchers (`log_tail.py`, `git_watcher.py`, `ws_reinjector.py`) - This specification
- Next.js beacon + proxy - This specification

---

**End of Specification**

**Next Steps:**
1. Atlas/Victor: Implement signals collector service (A2-1)
2. Atlas: Implement watchers (A2-2)
3. Atlas: Implement orchestrator templates (A2-3)
4. Iris: Implement Next.js integration (A2-4)
5. All: Run acceptance tests (A2-5)
6. Update IMPLEMENTATION_TASKS.md with Phase-A2 task tracking
