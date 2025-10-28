# Signals → Stimuli Bridge

**Version:** 1.1
**Created:** 2025-10-24
**Updated:** 2025-10-24 (Production hardening - added 10 resilience mitigations)
**Purpose:** Route operational signals (logs, console errors, screenshots, code/doc changes, runtime events) into L2 consciousness as stimuli for automated task creation
**Status:** Specification (Phase-A2)
**Owner:** Atlas (collector + watchers), Iris (UI integration), orchestrator templates

---

## Changelog

**v1.1 (2025-10-24):**
- Added Production Resilience Mitigations section (10 mitigations addressing adversarial analysis risks)
- Added extended StimulusEnvelope metadata fields (cooldown, merge keys, impact scoring, PII flags)
- Added Orchestrator Policy Configuration (ACK policies, lanes, capacity limits, trust tracking)
- Added 6 new acceptance tests (fanout cap, priority inversion, metric gaming, self-awareness guard, outage resilience, PII handling)
- Updated architecture diagram to reflect production features (backlog, fanout caps, capacity-aware routing)
- Updated telemetry requirements (Prometheus metrics, SLO targets, alerting thresholds)

**v1.0 (2025-10-24):**
- Initial specification
- 5 signal sources (logs, console, screenshots, code/doc drift, runtime events)
- Signals Collector service (FastAPI @8003)
- Intent templates (fix_incident, sync_docs_scripts)
- Self-awareness loop guards (origin tagging, depth limits, TTL)
- 4 base acceptance tests

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
 [Logs/Console/Screenshots/CodeDiffs/RuntimeEvents]
                 │
                 ▼
        ┌───────────────────────┐
        │  Signals Collector    │  FastAPI @8003
        │  - dedupe/rate/quant  │  backlog on outage
        │  - cooldown/merge     │  circuit breakers
        └─────────┬─────────────┘
                  │ StimulusEnvelope (N2)
                  ▼
        ┌───────────────────────┐
        │  Stimulus Injection   │ @8001
        │  - Validation         │ at-least-once
        └─────────┬─────────────┘
                  │
                  ▼
        ┌───────────────────────┐
        │   N2 Graph (Org)      │  evidence + routing
        └─────────┬─────────────┘
                  │
                  ▼
        ┌───────────────────────┐
        │ Autonomy Orchestrator │ @8002
        │ - Intent templates    │ fanout cap/lanes/ACK
        │ - Priority + impact   │ capacity-aware routing
        └─────────┬─────────────┘
                  │ Mission
                  ▼
        ┌───────────────────────┐
        │   L1 Citizen Engines  │  auto-wake with backpressure
        └─────────┬─────────────┘
                  │ Actions/TRACE
                  ▼
        ┌───────────────────────┐
        │   Runtime Events WS   │ @8000
        └──────┬────────────────┘
               │ (guarded reinjection)
               ▼
        ┌───────────────────────┐
        │  Self-awareness path  │ origin/TTL/depth/cooldown
        └───────────────────────┘
```

**Key insights:**
- Reuse existing StimulusEnvelope + Stimulus Injection + Orchestrator infrastructure
- Add thin **Signals Collector** layer for normalization + noise control + production resilience
- **Production hardening:** Backlog on outage, fanout caps, capacity-aware routing, impact-based trust
- **Self-awareness guards:** Origin tagging, depth limits, cooldown, hysteresis prevent runaway loops

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
- `scope: "organizational"` → N2 organization graph
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
- `scope: "organizational"` → N2 organization graph
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
- `scope: "organizational"` → N2 organization graph
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
- `scope: "organizational"` → N2 organization graph
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

### Orchestrator Policy Configuration

**Location:** `orchestration/services/orchestrator/orchestrator_config.yaml`

**Purpose:** Production resilience policies for intent routing, capacity management, and autonomy governance.

```yaml
version: 1

orchestrator:
  # ACK policies (Mitigation #10)
  ack_policies:
    max_origin_depth: 2
    business_impact_ack: ["sev1", "sev2"]
    whitelist_patterns:
      - "intent.sync_docs_scripts"  # safe auto-execute
      - "intent.fix_incident" where service != "sentinel"

  # Priority lanes (Mitigation #3)
  lanes:
    safety: 0.30      # 30% capacity for sev1/sev2
    incidents: 0.40   # 40% capacity for operational errors
    sync: 0.30        # 30% capacity for doc/code drift

  # Priority computation (Mitigation #3)
  priority:
    formula: "P * impact(sev) * service_criticality"
    aging_sec: 900  # boost priority after 15 min wait
    impact_weights:
      sev1: 10.0
      sev2: 5.0
      sev3: 1.0
      sev4: 0.5

  # Fan-out controls (Mitigation #1)
  fanout:
    max_intents_per_stimulus: 3
    merge_window_sec: 600
    merge_strategy: "highest_priority"  # keep top 3 by priority

  # Capacity management (Mitigation #7)
  capacity:
    per_assignee_max_in_flight:
      atlas: 8
      iris: 8
      felix: 6
      victor: 6
      ada: 12
    backpressure_threshold: 0.8  # queue assignment when 80% capacity
    overflow_strategy: "reassign"  # or "queue"

  # Reassignment policies (Mitigation #7)
  reassignment:
    timeout_sec: 1800  # 30 min stall timeout
    escalation_chain:
      iris: ["ada", "victor"]
      atlas: ["victor", "ada"]
      felix: ["ada"]
      victor: ["ada"]

  # Source trust tracking (Mitigation #2)
  trust:
    initial_trust: 0.8
    decay_rate: 0.95  # multiply by 0.95 per failed outcome
    recovery_rate: 1.05  # multiply by 1.05 per successful outcome
    min_trust: 0.1
    verification_required_below: 0.5  # ACK if source_trust < 0.5

  # Telemetry (Mitigation #9)
  telemetry:
    metrics_port: 9090
    export_format: "prometheus"
    slo_targets:
      intent_creation_latency_p99_ms: 500
      mission_completion_rate: 0.85
```

**Orchestrator behavior:**
1. **Load policies on startup** from orchestrator_config.yaml
2. **Evaluate ACK policies** before mission execution
3. **Enforce lane capacity** when assigning missions
4. **Apply fanout cap** when multiple intents match
5. **Check citizen capacity** before assignment
6. **Track source trust** after mission completion
7. **Export telemetry** to Prometheus on port 9090

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

## Production Resilience Mitigations

### Overview

The following 10 mitigations address production risks identified through adversarial analysis. Each mitigation extends the base architecture with defenses against specific failure modes.

---

### 1. Fan-out Explosion → Intent Merge + Cap

**Risk:** Single high-recurrence signal (e.g., same error 100×) creates 100 intents, overwhelming citizens.

**Defense:** Intent merging with fanout cap
- `max_intents_per_stimulus = 3` (configurable)
- `intent_merge_key` for coalescing related intents
- `intent_merge_window_sec = 600` (10 minutes)

**Extended Metadata:**
```yaml
metadata:
  intent_merge_key: "<stable key for coalescing>"
  max_intents_per_stimulus: 3
  intent_merge_window_sec: 600
```

**Orchestrator behavior:** If N>3 matches fire for same stimulus, merge into ≤3 intents with highest priority.

---

### 2. Metric Gaming → Impact-Based Trust

**Risk:** Citizens optimize for task count over real fixes. Completing low-impact tasks inflates metrics without improving system health.

**Defense:** Source trust scoring based on realized impact
- Track `Δhealth`, `Δerror_rate` after mission execution
- Update `source_trust` (0-1) based on outcomes
- Downweight signals from low-trust sources

**Extended Metadata:**
```yaml
metadata:
  source_trust: 0.0-1.0               # learned from outcomes
  expected_outcome: "error rate drops by 50%"
  verification_query: "check error count in last 10 mins"
```

**Orchestrator behavior:** Missions include verification queries. Post-execution, compare expected vs actual outcome. Update source_trust accordingly.

---

### 3. Priority Inversion → Lanes + Aging

**Risk:** Flood of low-priority signals (sev3/sev4) starves critical safety incidents (sev1).

**Defense:** Priority lanes with capacity allocation
- **Safety lane:** 30% capacity reserved for sev1/sev2
- **Incidents lane:** 40% capacity for operational errors
- **Sync lane:** 30% capacity for doc/code drift

**Extended Metadata:**
```yaml
metadata:
  business_impact: "sev1" | "sev2" | "sev3" | "sev4"
  service_criticality: 0.0-1.0
```

**Orchestrator policy:**
```yaml
orchestrator:
  lanes:
    safety: 0.30
    incidents: 0.40
    sync: 0.30
  priority:
    formula: "P * impact(sev) * service_criticality"
    aging_sec: 900  # boost priority after 15 min wait
```

---

### 4. Stimuli Flood → Enhanced Rate Limiting + Cooldown

**Risk:** Burst of 1000 similar signals (e.g., network partition) exceeds rate limits, but signals keep arriving.

**Defense:** Cooldown period after burst detection
- After rate limit hit, enter `cooldown_sec` period
- During cooldown, signals deduplicated but not injected
- Cooldown ends when signal rate drops below threshold

**Extended Metadata:**
```yaml
metadata:
  cooldown_sec: 300  # 5 min cooldown after burst
  rate_limit_bucket: "<service>:<pattern>"
```

**Collector behavior:** Track burst events. If rate limit exceeded 3× in 60 seconds, enter cooldown. Queue signals, inject summary after cooldown expires.

---

### 5. Cascading Loops → Cooldown + Hysteresis

**Risk:** Fix attempt triggers new anomaly → new stimulus → new fix attempt → cascade.

**Defense:** Anomaly cooldown with hysteresis
- After mission triggered by anomaly, enter `anomaly_cooldown_sec` period
- Suppress similar anomalies during cooldown
- Require `anomaly_hysteresis_frames` of healthy state before re-enabling

**Extended Metadata:**
```yaml
metadata:
  anomaly_cooldown_sec: 300
  anomaly_hysteresis_frames: 50  # must be healthy 50 frames before re-escalating
```

**WS reinjector behavior:** Track last anomaly escalation timestamp. Suppress reinjection during cooldown. Require sustained health before next escalation.

---

### 6. Orchestrator Outage → Backlog + Idempotency

**Risk:** Orchestrator down for 10 minutes. Collector queues 500 signals. On restart, all injected at once, overwhelming orchestrator.

**Defense:** Durable backlog with at-least-once delivery
- Collector writes stimuli to persistent queue (disk or Redis)
- Injection retries with exponential backoff
- Orchestrator handles duplicates via `stimulus_id` deduplication

**Extended Metadata:**
```yaml
metadata:
  backlog_id: "<persistent queue ID>"
  retry_count: 0
  retry_backoff_ms: 1000
```

**Collector behavior:** If injector unreachable, append to backlog file. Background task retries with backoff. Delete from backlog after successful injection.

**Orchestrator behavior:** Deduplicate by `stimulus_id` before creating IntentCard.

---

### 7. Citizen Overload → Capacity-Aware Routing

**Risk:** All incidents route to Atlas. He gets 50 concurrent missions, can't complete any.

**Defense:** Per-citizen capacity limits with backpressure
- `max_in_flight` missions per citizen (configurable per role)
- If citizen at capacity, queue or reassign to alternate
- Reassignment timeout if mission stalled

**Extended Metadata:**
```yaml
metadata:
  assignee_capacity:
    max_in_flight: 5
  reassign_after_sec: 1800  # 30 min timeout
```

**Orchestrator policy:**
```yaml
orchestrator:
  capacity:
    per_assignee_max_in_flight:
      atlas: 8
      iris: 8
      felix: 6
      victor: 6
      ada: 12
  reassignment:
    timeout_sec: 1800
```

**Orchestrator behavior:** Check citizen capacity before assignment. If at max, queue mission or route to alternate. Monitor mission staleness, reassign if timeout exceeded.

---

### 8. Screenshots & PII → Sensitivity Metadata

**Risk:** Screenshot contains credentials, PII, or sensitive data. Routing to N3 exposes it publicly.

**Defense:** Sensitivity classification with routing restrictions
- `sensitivity` field: `public` | `internal` | `restricted`
- `pii_redacted` flag if redaction applied
- Screenshots default to `internal`, never route to N3

**Extended Metadata:**
```yaml
metadata:
  sensitivity: "public" | "internal" | "restricted"
  pii_redacted: true
  storage_uri: "s3://evidence/redacted_screenshot.png"
```

**Collector behavior:**
- Tag all screenshots as `sensitivity: internal`
- Optional: Run PII redaction with circuit breaker
- Store original + redacted version, include `storage_uri`

**Orchestrator behavior:** Never route `restricted` stimuli to N3 graph. Limit N2 access to authorized citizens.

---

### 9. Observability Gaps → Telemetry Requirements

**Risk:** Can't distinguish "system working" from "signals not flowing". Silent failures invisible.

**Defense:** Required telemetry for all components
- Collector exposes `/metrics` (Prometheus format)
- SLO counters: ingestion latency, deduplication rate, injection success rate
- Orchestrator tracks: intent creation rate, mission completion rate, citizen utilization

**Telemetry Requirements:**

**Collector metrics:**
```python
signals_ingested_total          # counter
signals_deduplicated_total      # counter
signals_rate_limited_total      # counter
injection_latency_seconds       # histogram
injection_failures_total        # counter
```

**Orchestrator metrics:**
```python
intents_created_total           # counter, labels: intent_type
missions_assigned_total         # counter, labels: assignee
missions_completed_total        # counter, labels: assignee, outcome
citizen_queue_depth             # gauge, labels: citizen
```

**Alerting thresholds:**
- Injection latency p99 >10 seconds → alert
- Injection failure rate >5% → alert
- Citizen queue depth >10 for >30 min → alert

---

### 10. Autonomy Breaker → Enhanced ACK Policies

**Risk:** Self-awareness loops accidentally create missions that break autonomy (e.g., "disable sentinel").

**Defense:** Enhanced ACK policies for high-risk operations
- `origin_chain_depth >= 2` → ACK_REQUIRED
- `business_impact = sev1` or `sev2` → ACK_REQUIRED
- Orchestrator whitelist for auto-execute patterns

**Extended Metadata:**
```yaml
metadata:
  requires_ack_reason: "self_observation_depth_2" | "business_critical" | "manual_review"
```

**Orchestrator policy:**
```yaml
orchestrator:
  ack_policies:
    max_origin_depth: 2
    business_impact_ack: ["sev1", "sev2"]
    whitelist_patterns:
      - "intent.sync_docs_scripts"  # safe auto-execute
      - "intent.fix_incident" where service != "sentinel"
```

**Orchestrator behavior:** Evaluate mission against ACK policies. If match, set `execution_mode = ACK_REQUIRED`. Citizen awaits human approval.

---

### Extended StimulusEnvelope Metadata (Complete)

All StimulusEnvelope instances SHOULD include these extended fields for production resilience:

```yaml
metadata:
  # Core loop prevention (existing)
  origin: "external" | "self_observation"
  origin_chain_depth: 0
  origin_chain: []
  ttl_frames: 600
  dedupe_key: "<hash>"
  rate_limit_bucket: "<service>:<pattern>"

  # Production mitigations (NEW)
  cooldown_sec: 300
  q_gate_config:
    q_escalate: 0.75
    q_hard: 0.90
    ema_alpha: 0.2

  # Fan-out & merging
  intent_merge_key: "<stable key>"
  max_intents_per_stimulus: 3
  intent_merge_window_sec: 600

  # Priority & impact
  business_impact: "sev1" | "sev2" | "sev3" | "sev4"
  service_criticality: 0.0-1.0
  source_trust: 0.0-1.0
  expected_outcome: "error rate drops by 50%"
  verification_query: "check error count in last 10 mins"

  # Capacity & routing
  assignee_capacity:
    max_in_flight: 5
  reassign_after_sec: 1800

  # Safety & PII
  sensitivity: "public" | "internal" | "restricted"
  pii_redacted: true
  storage_uri: "s3://evidence/screenshot.png"

  # Self-awareness
  anomaly_cooldown_sec: 300
  anomaly_hysteresis_frames: 50
  requires_ack_reason: "self_observation_depth_2" | "business_critical"
```

**Note:** Fields marked (NEW) are optional extensions. Core fields (origin, origin_chain_depth, dedupe_key) remain REQUIRED.

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

### Test 5: Fanout Cap (Intent Merge)

**Scenario:** Same error 20× in logs → only ≤3 intents created

**Steps:**
1. Generate 20 identical backend errors (same message + stack)
2. Collector deduplicates, but sets `recurrence = 20` in metadata
3. Forward single stimulus with high recurrence to orchestrator
4. Orchestrator matches `intent.fix_incident`, evaluates fanout cap
5. Creates ≤3 intents (merged by `intent_merge_key`)

**Verification:**
- Only 1 stimulus created (deduplication works)
- ≤3 IntentCards created despite high recurrence
- Intent merge visible in orchestrator logs

---

### Test 6: Priority Inversion (Lane Protection)

**Scenario:** Flood of sev3 signals doesn't starve sev1 safety incident

**Steps:**
1. Generate 100 sev3 incidents (low priority)
2. Generate 1 sev1 safety incident (high priority)
3. Orchestrator receives all 101 stimuli
4. Safety lane (30% capacity) reserves slots for sev1
5. Sev1 mission assigned immediately despite queue depth

**Verification:**
- Sev1 mission created within <5 seconds
- Sev3 missions queued but don't block sev1
- Lane allocation visible in orchestrator metrics

---

### Test 7: Metric Gaming (Source Trust)

**Scenario:** Citizen completes low-impact tasks, source_trust degrades

**Steps:**
1. Generate 10 signals from `test_source` with expected outcomes
2. Citizen completes missions but outcomes don't match expectations
3. Orchestrator measures Δhealth / Δerror_rate post-execution
4. `source_trust` for `test_source` drops from 1.0 → 0.3
5. Future signals from `test_source` downweighted

**Verification:**
- `source_trust` degrades after low-impact completions
- Future signals from source have lower priority
- Trust score visible in metadata

---

### Test 8: Self-Awareness Guard (Depth Cap)

**Scenario:** Cascade attempt hits depth=2 limit, requires ACK

**Steps:**
1. Induce runtime anomaly (criticality unsafe)
2. WS reinjector creates stimulus depth=1
3. Mission executes, but anomaly persists
4. Second reinjection creates stimulus depth=2
5. Orchestrator sets `execution_mode = ACK_REQUIRED`
6. Mission waits for human approval

**Verification:**
- First mission auto-executes (depth=1)
- Second mission requires ACK (depth=2)
- No third stimulus created (depth limit prevents)

---

### Test 9: Outage Resilience (Backlog)

**Scenario:** Injector down, signals queued, replayed on recovery

**Steps:**
1. Stop stimulus injection service
2. Generate 50 signals while injector down
3. Collector writes to backlog file
4. Restart injector
5. Collector replays backlog with exponential backoff
6. All 50 stimuli injected, deduplicated by `stimulus_id`

**Verification:**
- Backlog file created during outage
- All signals eventually injected
- No duplicates (idempotency works)
- Backlog file cleared after replay

---

### Test 10: PII Handling (Sensitivity Routing)

**Scenario:** Screenshot with PII never routes to N3

**Steps:**
1. Upload screenshot with visible credentials
2. Collector tags as `sensitivity: restricted`
3. Optional: PII redaction runs (or circuit breaker trips)
4. Orchestrator creates mission, checks sensitivity
5. Mission routes to N2 only, never N3
6. Citizen receives mission with redacted version

**Verification:**
- Screenshot tagged `restricted`
- Never appears in N3 graph
- Redacted version (if applicable) used in mission
- Original stored securely with access controls

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
