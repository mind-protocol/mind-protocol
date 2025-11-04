# Docs-as-Views Architecture
**Membrane-First Design for L2 Graph Viewing**

**Status:** Specification
**Author:** Nicolas Reynolds
**Date:** 2025-11-04
**Version:** 1.0

---

## Executive Summary

Docs-as-views enables web-based viewing of L2 organizational graphs without breaking membrane discipline. **Mind Protocol owns the membrane infrastructure** (WebSocket server, event bus, envelope validation). **GraphCare and other orgs own L2 resolvers** (Cypher queries, Select→Project→Render logic, compute pricing).

**Core Principle:** L3 (Mind Protocol) never touches databases. Ever.

---

## Scope Split (By Layer)

### L4 - Protocol Layer (Mind Protocol - Law at the Boundary)

**Owns:**
- **Membrane Bus** (WebSocket multiplexer: `/inject` + `/observe`)
- **Envelope Validation** (schema, SEA-1.0 signatures, TTL)
- **CPS-1 Enforcement** (quote-before-inject gate, budget checking)
- **Rate Limiting** (per-principal token bucket)
- **Tenant Scoping** (ecosystem/org channel namespaces)
- **Protocol Topics** (ecosystem/{eco}/protocol/* for cross-org law)
- **Typed Envelope Schemas** (shared protocol contracts)

**Does NOT Own:**
- UI client connections (that's L3)
- Database credentials (that's L2)
- Compute pricing (L2 requests quotes; L4 enforces gate)

### L3 - Ecosystem Surface (Mind Protocol - Presentation Only)

**Owns:**
- **WebSocket Bridge** (browser ↔ L4 bus courier)
- **UI Aggregation** (fan-out results by request_id)
- **Optional UX Cache** (keyed by ko_digest, NOT source of truth)

**Does NOT Own:**
- Envelope enforcement (that's L4)
- Database access (FORBIDDEN - lint this)
- Rendering (that's L2)
- Authority over envelopes (just participates)

### GraphCare / Org L2 Resolvers

**Owns:**
- L2 Cypher queries (read from FalkorDB)
- Select→Project→Render pipeline
- Compute pricing under CPS-1
- Result caching strategy
- Error handling (emit `failure.emit`)

**Does NOT Own:**
- Membrane validation
- Cross-org routing
- UI client connections

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser / Client                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ ws://localhost:8000/api/ws
                     │
┌────────────────────▼────────────────────────────────────────┐
│          L3 - Ecosystem Surface (ecosystem-ws)              │
│          Presentation/Aggregation - NO AUTHORITY            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  WebSocket Bridge (ecosystem_ws_bridge.py)           │  │
│  │  - Accept browser connections                        │  │
│  │  - Inject to L4 bus (via publish_to_membrane)        │  │
│  │  - Observe from L4 bus → fan-out to browsers         │  │
│  │  - NO DB ACCESS, NO RENDERING, NO ENFORCEMENT        │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
└─────────────────┼────────────────────────────────────────────┘
                  │
                  │ inject / observe
                  │
┌─────────────────▼────────────────────────────────────────────┐
│        L4 - Protocol Layer (protocol-hub)                    │
│        Law at the Boundary - ENFORCEMENT AUTHORITY           │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Membrane Bus (protocol_hub.py)                        │  │
│  │  - /inject endpoint (accepts envelopes)               │  │
│  │  - /observe endpoint (subscribe to channels)          │  │
│  │  - ENFORCE: Envelope schema validation                │  │
│  │  - ENFORCE: SEA-1.0 signature verification            │  │
│  │  - ENFORCE: CPS-1 quote-before-inject gate            │  │
│  │  - ENFORCE: Rate limits (token bucket)                │  │
│  │  - ENFORCE: Tenant scoping (ecosystem/org isolation)  │  │
│  │  - Channel routing: ecosystem/{eco}/org/{org}/{topic} │  │
│  └───────────────┬───────────────────────────────────────┘  │
│                  │                                           │
│                  │ In-memory pub/sub (or Redis adapter)     │
│                  │                                           │
└──────────────────┼───────────────────────────────────────────┘
                  │
                  │ channel: ecosystem/mind-protocol/org/graphcare/docs.view.request
                  │
┌─────────────────▼────────────────────────────────────────────┐
│          GraphCare L2 Resolver (graphcare_resolver.py)       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Observe: docs.view.request                         │ │
│  │  2. Validate: quote_id present (CPS-1)                 │ │
│  │  3. Query: Run Cypher against FalkorDB                 │ │
│  │  4. Project: Select fields, apply view_type transform  │ │
│  │  5. Render: Generate MDX/HTML                          │ │
│  │  6. Inject: docs.view.result → bus                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  FalkorDB credentials: ONLY accessible here                  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: NOW (Ship to Unblock Viewing)

**Goal:** End-to-end docs viewing with minimal infrastructure

#### 1. Run Protocol Hub (L4 Membrane Bus)

**File:** `orchestration/protocol/hub/protocol_hub.py`

**Provides:**
- `ws://localhost:8001/inject` - Accepts `membrane.inject` envelopes
- `ws://localhost:8001/observe` - Subscribe to channels, receive broadcasts

**This is L4 - Protocol enforcement layer:**
```python
# Single-node in-memory pub/sub (upgrade to Redis later)
class ProtocolHub:
    def __init__(self):
        self.channels: Dict[str, Set[WebSocket]] = {}
        self.recent_envelopes: Deque[Envelope] = deque(maxlen=100)

    async def inject(self, envelope: Envelope):
        """Accept envelope, broadcast to subscribers."""
        channel = envelope.channel
        self.recent_envelopes.append(envelope)

        for subscriber in self.channels.get(channel, set()):
            await subscriber.send_json(envelope.dict())

    async def observe(self, websocket: WebSocket, channels: List[str]):
        """Subscribe to channels, receive broadcasts."""
        for channel in channels:
            self.channels.setdefault(channel, set()).add(websocket)

        try:
            while True:
                await websocket.receive_text()  # Keep alive
        finally:
            for channel in channels:
                self.channels[channel].discard(websocket)
```

**Environment:**
```bash
MEMBRANE_WS_INJECT=ws://localhost:8001/inject
MEMBRANE_WS_OBSERVE=ws://localhost:8001/observe
MEMBRANE_ORG=mind-protocol
```

#### 2. Wire L3 Bridge to L4 Bus (No DB, No Authority)

**File:** `orchestration/ecosystem/ws/ecosystem_ws_bridge.py`

**L3 is just a courier - NO enforcement, NO database:**
```python
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """L3 bridge: browser ↔ L4 protocol bus."""
    await websocket.accept()

    async for message in websocket.iter_json():
        if message.get("type") == "docs.view.request":
            # Inject to L4 protocol bus
            # L4 will enforce quote_id, rate limits, signatures
            await publish_to_membrane(
                channel=f"ecosystem/mind-protocol/org/{org}/docs.view.request",
                event_name="docs.view.request",
                content=message["content"],
                request_id=message["request_id"]
            )
```

**Background task observes results:**
```python
async def fan_out_docs_results():
    """Subscribe to docs.view.result, fan-out to requesting clients."""
    async for envelope in observe_membrane(
        channels=["ecosystem/*/org/*/docs.view.result"]
    ):
        request_id = envelope.content.get("request_id")
        client = active_clients.get(request_id)

        if client:
            await client.send_json({
                "type": "docs.view.result",
                "data": envelope.content
            })
```

**Short-lived cache (ko_digest keyed):**
```python
# Cache last result per (org, view_type, scope, params, format, ko_digest)
# L2 remains source of truth
cache_key = (org, view_type, scope, params_hash, format, ko_digest)
cached_result = result_cache.get(cache_key)

if cached_result and not is_stale(cached_result):
    return cached_result
```

#### 3. Ship Minimal Membrane Client for Node/TS

**File:** `orchestration/adapters/bus/membrane_client.ts`

```typescript
// ~50 lines - mirror Python helper
import WebSocket from 'ws';

export class MembraneClient {
  private ws: WebSocket;

  constructor(injectUrl: string = process.env.MEMBRANE_WS_INJECT) {
    this.ws = new WebSocket(injectUrl);
  }

  async inject(envelope: MembraneEnvelope): Promise<void> {
    await this.ws.send(JSON.stringify(envelope));
  }

  observe(channels: string[], callback: (envelope: any) => void): void {
    // Subscribe and receive broadcasts
  }
}
```

**Usage:**
```typescript
// Frontend tools and Node workers use same envelope format
const client = new MembraneClient();

await client.inject({
  v: 1,
  type: "membrane.inject",
  org: "graphcare",
  channel: "ecosystem/mind-protocol/org/graphcare/docs.view.request",
  content: {
    view_type: "ADR_Timeline",
    scope: { doc_type: "ADR" }
  }
});
```

#### 4. Expose Tiny Debug Surface

**File:** `orchestration/adapters/api/docs_view_api_v2.py`

```python
@app.get("/api/bus/subscribers")
async def get_subscribers():
    """Get subscriber counts by channel."""
    return {
        channel: len(subscribers)
        for channel, subscribers in membrane_hub.channels.items()
    }

@app.get("/api/bus/recent")
async def get_recent_envelopes(channel: str = None):
    """Get last N envelopes per channel (in-memory)."""
    envelopes = membrane_hub.recent_envelopes

    if channel:
        envelopes = [e for e in envelopes if e.channel == channel]

    return list(envelopes)[-20:]  # Last 20
```

**Why:** Fast diagnosis without SSHing into L2

---

### Phase 2: HARDENING (Production-Worthy)

#### 5. Envelope Validation at Accept-Time (L4 Enforcement)

**File:** `orchestration/protocol/hub/protocol_hub.py`

**L4 is the authority - enforce protocol law:**

```python
from orchestration.schemas.envelopes import MembraneEnvelope

async def inject(self, raw_envelope: dict):
    """Validate envelope before accepting."""
    try:
        envelope = MembraneEnvelope.parse_obj(raw_envelope)
    except ValidationError as e:
        logger.error(f"Envelope validation failed: {e}")
        await emit_failure(
            severity="error",
            reason="envelope_validation_failed",
            details=str(e)
        )
        return

    # Check TTL
    if envelope.ttl_frames <= 0:
        logger.warning(f"Envelope expired: {envelope.dedupe_key}")
        return

    # Verify signature (if present)
    if envelope.sig and not verify_signature(envelope):
        logger.error(f"Invalid signature: {envelope.dedupe_key}")
        return

    # Accept
    await self._broadcast(envelope)
```

**Reject Reasons:**
- Malformed envelope (missing required fields)
- Expired (`ttl_frames` ≤ 0)
- Invalid signature
- Rate limit exceeded

#### 6. Org/Tenant Isolation on Channels

**Canonicalize channel names:**
```python
# ecosystem/{eco}/org/{org}/{topic}
canonical_channel = f"ecosystem/{ecosystem_id}/org/{org_id}/{topic}"

# Restrict subscriptions
allowed_orgs = get_principal_orgs(auth_token)
if org_id not in allowed_orgs:
    raise PermissionError(f"Not authorized for org: {org_id}")
```

**Why:** Prevent accidental cross-org leakage

#### 7. Backpressure & Rate Limits

**Per-principal token bucket:**
```python
from orchestration.libs.rate_limiter import TokenBucket

# 10 requests per minute per principal
rate_limiters: Dict[str, TokenBucket] = {}

async def inject(self, envelope: Envelope, principal: str):
    limiter = rate_limiters.setdefault(principal, TokenBucket(
        capacity=10,
        refill_rate=10/60  # 10 per minute
    ))

    if not limiter.consume(1):
        logger.warning(f"Rate limit exceeded: {principal}")
        await emit_failure(
            severity="warning",
            reason="rate_limit_exceeded",
            principal=principal
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

**Why:** Protect L2 resolvers, keep bus responsive

#### 8. CPS-1 Enforcement at L4 (Quote-Before-Inject Gate)

**L4 enforces CPS-1 law - reject envelopes without valid quote_id:**
```python
# L4 protocol hub enforces CPS-1 gate
async def inject(self, envelope: Envelope):
    """Enforce CPS-1: reject envelopes without valid quote_id."""

    # Check if this channel requires quote (e.g., docs.view.request)
    if requires_quote(envelope.channel):
        quote_id = envelope.content.get("quote_id")

        if not quote_id:
            logger.error(f"CPS-1 violation: missing quote_id: {envelope.dedupe_key}")
            await emit_failure(
                severity="error",
                reason="cps1_violation_missing_quote",
                details="docs.view.request requires quote_id",
                request_id=envelope.content.get("request_id")
            )
            return  # REJECT at protocol layer

        # Verify quote is valid and budget sufficient
        quote = await verify_quote(quote_id)
        if not quote.valid or not quote.budget_sufficient:
            logger.error(f"CPS-1 violation: invalid quote: {quote_id}")
            await emit_failure(
                severity="error",
                reason="cps1_violation_invalid_quote",
                details=f"Quote {quote_id} invalid or insufficient budget"
            )
            return  # REJECT at protocol layer

    # Quote valid or not required - accept and broadcast
    await self._broadcast(envelope)
```

**Why this is L4:** CPS-1 is protocol law (LAW-002), not org policy. The membrane bus **enforces** it before L2 ever sees traffic.

#### 9. Observability

**Metrics:**
```python
from prometheus_client import Counter, Histogram, Gauge

envelopes_received = Counter(
    'membrane_envelopes_received_total',
    'Total envelopes received',
    ['channel']
)

fan_out_latency = Histogram(
    'membrane_fan_out_seconds',
    'Time to fan-out to subscribers',
    ['channel']
)

subscriber_count = Gauge(
    'membrane_subscribers',
    'Current subscriber count',
    ['channel']
)
```

**Structured logs:**
```python
logger.info("envelope_accepted", extra={
    "channel": envelope.channel,
    "org": envelope.org,
    "dedupe_key": envelope.dedupe_key,
    "subscriber_count": len(subscribers)
})

logger.error("envelope_rejected", extra={
    "reason": "invalid_signature",
    "channel": envelope.channel,
    "dedupe_key": envelope.dedupe_key
})
```

**Why:** When a view doesn't load, you need to see which hop failed

#### 10. AuthN/Z

**Reuse existing WS auth:**
```python
@app.websocket("/api/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Depends(get_auth_token)
):
    # Map identity to allowed ecosystem/org sets
    principal = verify_token(token)
    allowed_orgs = get_principal_orgs(principal)

    # Restrict subscriptions
    async for message in websocket.iter_json():
        org = extract_org(message)
        if org not in allowed_orgs:
            await websocket.send_json({
                "error": "unauthorized",
                "message": f"Not authorized for org: {org}"
            })
            continue
```

#### 11. Redis Adapter (Drop-In) for L4 Hub

**File:** `orchestration/protocol/hub/redis_adapter.py`

**When horizontal scale needed:**
```python
class RedisProtocolHub(ProtocolHub):
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)

    async def inject(self, envelope: Envelope):
        """Publish to Redis channel."""
        await self.redis.publish(
            envelope.channel,
            envelope.json()
        )

    async def observe(self, channels: List[str]):
        """Subscribe to Redis channels."""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(*channels)

        async for message in pubsub.listen():
            yield Envelope.parse_raw(message['data'])
```

**Why:** Zero API churn to callers; only hub process changes

---

### Phase 3: GUARDRAILS (Prevent Regressions)

#### 12. Static Guard: "No DB from L3" (Enforce Boundary)

**File:** `tools/mp_lint/rules/l3_ecosystem_boundary.py`

```python
# mp-lint rule L3-B001
class NoL3DatabaseAccess(Rule):
    """L3 ecosystem code must not import or use database clients.

    L3 is presentation/aggregation only. Database access is L2 territory.
    This enforces membrane discipline at build time.
    """

    code = "L3-B001"
    severity = "error"

    FORBIDDEN_IMPORTS = [
        "falkordb",
        "redis",
        "pymongo",
        "psycopg2",
        "sqlalchemy"
    ]

    def check_file(self, file_path: Path):
        if not is_l3_file(file_path):
            return []

        with open(file_path) as f:
            content = f.read()

        violations = []
        for forbidden in self.FORBIDDEN_IMPORTS:
            if f"import {forbidden}" in content:
                violations.append(Violation(
                    rule=self.code,
                    file=file_path,
                    message=f"L3 code must not import {forbidden}",
                    suggestion="Move DB access to L2 resolver"
                ))

        return violations
```

**CI Integration:**
```bash
# .github/workflows/ci.yml
- name: Run mp-lint
  run: python tools/mp_lint/cli.py --check L3-B001
```

#### 13. Schema Contracts in Code

**File:** `orchestration/schemas/envelopes/docs_view.py`

```python
from pydantic import BaseModel, Field

class DocsViewRequest(BaseModel):
    """Request to view L2 graph as document."""
    request_id: str
    org: str
    view_type: str  # "ADR_Timeline", "Pattern_Hierarchy", etc.
    scope: dict  # {"doc_type": "ADR"} or {"pattern_id": "..."}
    params: dict = {}
    format: str = "mdx"  # or "html", "json"
    quote_id: Optional[str] = None  # CPS-1 quote reference

class DocsViewResult(BaseModel):
    """Result of docs view query."""
    request_id: str
    ko_digest: str  # Content-addressable hash
    content: str  # Rendered MDX/HTML
    metadata: dict
    cached: bool = False

class DocsViewInvalidated(BaseModel):
    """Notification that cached view is stale."""
    ko_digest: str
    reason: str  # "graph_updated", "ttl_expired"
```

**File:** `orchestration/schemas/envelopes/economy.py`

```python
class EconomyQuoteRequest(BaseModel):
    """Request compute cost quote."""
    quote_id: str
    operation: str  # "docs.view", "query.cypher", etc.
    estimated_complexity: dict

class EconomyQuoteResponse(BaseModel):
    """Quote response with cost."""
    quote_id: str
    cost_mind: float
    budget_sufficient: bool
    expires_at: datetime
```

**File:** `orchestration/schemas/envelopes/failure.py`

```python
class FailureEmit(BaseModel):
    """Fail-loud envelope for errors."""
    severity: str  # "warning", "error", "critical"
    component: str
    reason: str
    details: dict
    request_id: Optional[str] = None
```

**Publish as library:**
```python
# setup.py
setup(
    name="mind-protocol-envelopes",
    version="1.0.0",
    packages=["orchestration.schemas.envelopes"],
    install_requires=["pydantic"]
)

# GraphCare uses it:
from mind_protocol_envelopes import DocsViewRequest, DocsViewResult
```

#### 14. Make Targets & Runbook

**File:** `Makefile`

```makefile
.PHONY: bus ws smoke-docs

bus:
	@echo "Starting membrane hub..."
	python orchestration/adapters/bus/membrane_hub.py

ws:
	@echo "Starting Mind Protocol WebSocket server..."
	python orchestration/adapters/ws/websocket_server.py

smoke-docs:
	@echo "Running smoke test for docs-as-views..."
	python tests/smoke/test_docs_view.py

all: bus ws
```

**Runbook:** `docs/runbooks/DOCS_AS_VIEWS.md`

```markdown
# Docs-as-Views Runbook

## Starting Services

```bash
# Terminal 1: Start membrane hub
make bus

# Terminal 2: Start WebSocket server
make ws

# Terminal 3: Start GraphCare L2 resolver
cd /path/to/graphcare
python graphcare_resolver.py
```

## Smoke Test

```bash
make smoke-docs
# Expected: "✓ docs.view.result received in 2.3s"
```

## Debugging

**View is not loading:**
1. Check bus subscribers: `curl http://localhost:8001/api/bus/subscribers`
2. Check recent envelopes: `curl http://localhost:8001/api/bus/recent?channel=docs.view.request`
3. Check L2 resolver logs: `tail -f /var/log/graphcare/resolver.log`

**View is stale:**
1. Check ko_digest in result
2. Verify L2 resolver cache TTL
3. Force invalidation: inject `docs.view.invalidated` with ko_digest
```

#### 15. Acceptance Tests (CI)

**File:** `tests/acceptance/test_docs_view_membrane.py`

```python
import pytest
from orchestration.adapters.bus.membrane_client import MembraneClient

@pytest.mark.acceptance
async def test_docs_view_request_reaches_l2(membrane_hub, l2_resolver):
    """Inject docs.view.request, ensure it reaches L2 resolver."""
    client = MembraneClient()

    # Inject request (no quote_id in dev)
    await client.inject({
        "type": "membrane.inject",
        "channel": "ecosystem/mind-protocol/org/test/docs.view.request",
        "content": {
            "request_id": "test_001",
            "view_type": "ADR_Timeline"
        }
    })

    # Assert L2 resolver received it
    received = await l2_resolver.wait_for_request(timeout=5)
    assert received["request_id"] == "test_001"

@pytest.mark.acceptance
async def test_docs_view_result_fans_out(membrane_hub, ws_client):
    """Inject synthetic result, assert fan-out to client."""
    client = MembraneClient()

    # Subscribe to results
    results = []
    await ws_client.subscribe("docs.view.result", lambda e: results.append(e))

    # Inject synthetic result
    await client.inject({
        "type": "membrane.inject",
        "channel": "ecosystem/mind-protocol/org/test/docs.view.result",
        "content": {
            "request_id": "test_002",
            "ko_digest": "abc123",
            "content": "<mdx>Test</mdx>"
        }
    })

    # Assert client received it
    await asyncio.sleep(0.5)
    assert len(results) == 1
    assert results[0]["request_id"] == "test_002"

@pytest.mark.acceptance
async def test_malformed_envelope_rejected(membrane_hub):
    """Inject malformed envelope, assert rejection counter increments."""
    client = MembraneClient()

    initial_count = membrane_hub.rejection_counter.get("invalid_schema", 0)

    # Inject malformed envelope (missing required fields)
    await client.inject({
        "type": "membrane.inject",
        # Missing: channel, content
    })

    # Assert rejection counter incremented
    assert membrane_hub.rejection_counter["invalid_schema"] == initial_count + 1
```

---

## What Each Layer Must NOT Do

### L4 Protocol Hub - Must NOT:

- ❌ **Never** make semantic decisions (what views mean, how to render)
- ❌ **Never** access databases (no FalkorDB creds here)
- ❌ **Never** compute business logic
- ✅ **Only** enforce protocol law (CPS-1, SEA-1.0, rate limits, tenant scoping)

### L3 Ecosystem Surface - Must NOT:

- ❌ **Never** access databases (no Cypher, no FalkorDB creds)
- ❌ **Never** enforce protocol law (that's L4's job)
- ❌ **Never** compute or price work
- ✅ **Only** bridge browser ↔ L4 bus (inject/observe/fan-out)

**In L3 ecosystem code. Ever.**

```python
# ❌ FORBIDDEN in Mind Protocol L3
from falkordb import FalkorDB

db = FalkorDB(host=FALKORDB_HOST, port=6379)
graph = db.select_graph("mind-protocol")
result = graph.query("MATCH (n:ADR) RETURN n")  # NO!
```

**Why:** That stays in L2 resolvers (GraphCare, other orgs)

### L2 Organization Resolvers - Must NOT:

- ❌ **Never** manage client connections (that's L3)
- ❌ **Never** validate envelopes (that's L4)
- ❌ **Never** enforce rate limits (that's L4)
- ✅ **Only** compute views, query graphs, render content

---

### ❌ L3 Must Not Render MDX/HTML

**Beyond passing through what L2 produced.**

```python
# ❌ FORBIDDEN in Mind Protocol L3
def render_adr_timeline(adrs: List[dict]) -> str:
    mdx = "<Timeline>"
    for adr in adrs:
        mdx += f"<Card>{adr['title']}</Card>"
    mdx += "</Timeline>"
    return mdx  # NO! This is L2 responsibility
```

**L3 is a courier with good manners:**
```python
# ✅ CORRECT in Mind Protocol L3
async def fan_out_result(envelope: DocsViewResult):
    """Pass through rendered content from L2."""
    await websocket.send_json({
        "type": "docs.view.result",
        "content": envelope.content,  # Already rendered by L2
        "ko_digest": envelope.ko_digest
    })
```

### ❌ No Silent Failures

**If L3 can't forward or subscribe, emit `failure.emit`.**

```python
# ❌ FORBIDDEN: Silent failure
try:
    await membrane_hub.inject(envelope)
except Exception as e:
    logger.error(f"Failed to inject: {e}")
    # Silent - org never sees it!

# ✅ CORRECT: Fail-loud
try:
    await membrane_hub.inject(envelope)
except Exception as e:
    logger.error(f"Failed to inject: {e}")
    await emit_failure(
        severity="error",
        component="membrane_hub",
        reason="inject_failed",
        details={"error": str(e), "envelope": envelope.dict()},
        request_id=envelope.content.get("request_id")
    )
```

---

## Folder Structure (Corrected Layering)

```
orchestration/
  protocol/                        # L4 - Protocol Layer (Law at Boundary)
    hub/
      protocol_hub.py              # Membrane bus: /inject + /observe
      redis_adapter.py             # Optional Redis backend
      envelope_validator.py        # Schema, SEA-1.0, CPS-1 validation

  ecosystem/                       # L3 - Ecosystem Surface (Presentation)
    ws/
      ecosystem_ws_bridge.py       # Browser ↔ L4 bus bridge

  adapters/
    bus/
      membrane_bus.py              # Shared client helper (inject/observe)
      membrane_client.ts           # Node/TS client (NEW)
  schemas/
    envelopes/
      docs_view.py                 # DocsViewRequest|Result|Invalidated
      economy.py                   # EconomyQuoteRequest|Response
      failure.py                   # FailureEmit
  infra/
    redis_adapter.py               # Optional Redis backend for hub
  libs/
    rate_limiter.py                # Token bucket rate limiter

tools/
  mp_lint/
    rules/
      l3_ecosystem_boundary.py     # Static guard: No DB in L3 (L3-B001)

tests/
  acceptance/
    test_docs_view_membrane.py     # End-to-end acceptance tests
  smoke/
    test_docs_view.py              # Smoke test for make smoke-docs

docs/
  specs/v2/membrane/
    DOCS_AS_VIEWS_ARCHITECTURE.md  # This document
  runbooks/
    DOCS_AS_VIEWS.md               # Operator runbook

Makefile                           # make bus, make ws, make smoke-docs
```

---

## Integration with L4 Law

### CPS-1 (Compute Payment)

**Quote-before-inject flow:**
```python
# 1. Client requests quote
await client.inject({
    "channel": "economy.quote.request",
    "content": {
        "quote_id": "quote_123",
        "operation": "docs.view",
        "estimated_complexity": {"node_count": 100, "depth": 3}
    }
})

# 2. Economy service responds with quote
# (Handled by L2 economy runtime, not L3)

# 3. Client injects docs.view.request with quote_id
await client.inject({
    "channel": "docs.view.request",
    "content": {
        "request_id": "req_456",
        "quote_id": "quote_123",  # Reference to quote
        "view_type": "ADR_Timeline"
    }
})

# 4. L2 resolver validates quote_id, debits on delivery
```

**L3 passes through economy envelopes, doesn't enforce:**
- Quote validation: L2 responsibility
- Balance checking: L2 responsibility
- Debit execution: L2 responsibility

### SEA-1.0 (Identity Attestation)

**L2 resolvers sign results:**
```python
# L2 resolver signs docs.view.result
result = DocsViewResult(
    request_id="req_456",
    ko_digest="abc123",
    content="<mdx>...</mdx>",
    metadata={
        "generated_by": "graphcare_resolver",
        "snapshot_id": "sea_graphcare_20251104_08h",
        "signature": sign_with_sea_snapshot(content, snapshot_id)
    }
)
```

**L3 verifies signatures (optional):**
```python
if envelope.sig:
    if not verify_sea_signature(envelope):
        logger.warning(f"Invalid SEA signature: {envelope.dedupe_key}")
        # Don't reject (L2 is authority), but log for audit
```

### UBC (Universal Basic Compute)

**L2 resolvers use UBC for low-cost operations:**
```python
# L2 resolver checks if UBC covers operation
if estimated_cost <= ubc_balance:
    # Debit from UBC instead of org wallet
    debit_ubc(citizen_id, estimated_cost)
else:
    # Require quote_id for org wallet debit
    if not quote_id:
        raise ValueError("quote_id required for non-UBC operations")
```

**L3 doesn't know about UBC:**
- UBC accounting: L2 responsibility
- Budget checking: L2 responsibility

---

## Integration with GraphCare

### GraphCare L2 Resolver

**File:** `graphcare/resolvers/docs_view_resolver.py`

```python
from mind_protocol_envelopes import DocsViewRequest, DocsViewResult
from orchestration.adapters.bus.membrane_bus import observe_membrane, publish_to_membrane

async def docs_view_resolver():
    """GraphCare L2 resolver for docs-as-views."""
    async for envelope in observe_membrane(
        channels=["ecosystem/mind-protocol/org/graphcare/docs.view.request"]
    ):
        request = DocsViewRequest.parse_obj(envelope.content)

        try:
            # 1. Validate quote_id (CPS-1)
            if not validate_quote(request.quote_id):
                raise ValueError("Invalid or expired quote_id")

            # 2. Query FalkorDB (L2 has credentials)
            result = query_graph(request.view_type, request.scope)

            # 3. Project & Render
            content = render_view(result, request.format)

            # 4. Emit result
            await publish_to_membrane(
                channel="ecosystem/mind-protocol/org/graphcare/docs.view.result",
                event_name="docs.view.result",
                content=DocsViewResult(
                    request_id=request.request_id,
                    ko_digest=hash_content(content),
                    content=content,
                    metadata={"generated_by": "graphcare_resolver"}
                ).dict()
            )

            # 5. Debit compute cost
            debit_cost(request.quote_id, actual_cost)

        except Exception as e:
            # 6. Emit failure
            await publish_to_membrane(
                channel="ecosystem/mind-protocol/org/graphcare/failure.emit",
                event_name="failure.emit",
                content={
                    "severity": "error",
                    "component": "graphcare_resolver",
                    "reason": "docs_view_failed",
                    "details": str(e),
                    "request_id": request.request_id
                }
            )
```

### GraphCare Care Plans

**How docs-as-views fits into care plans:**

- **Basic Care**: Weekly view generation (stale acceptable)
- **Standard Care**: Daily view updates (sync daily)
- **Premium Care**: Real-time views (invalidate on graph change)
- **Enterprise Care**: Custom view types, dedicated resolver instance

---

## Why This Split Works

### 1. Membrane-First

**Bus + WS in Mind Protocol; computation in org L2.**

Clean boundary, one control surface.

### 2. Auditable & Priced

**CPS-1 travels on same bus; L2 enforces quotes and debits; L3 remains neutral.**

Every compute operation is auditable via envelope trail.

### 3. Portable

**Resolvers can be swapped per client/org; UI and infra don't change.**

GraphCare can serve multiple clients with different L2 resolvers.

### 4. Boring to Operate

**One hub, one WS, typed envelopes, clear metrics. Boring is good.**

Operators have one place to look for docs-as-views issues.

---

## Success Criteria

**Phase 1 (NOW) is complete when:**
- [ ] Membrane hub accepts and broadcasts envelopes
- [ ] L3 WebSocket server injects docs.view.request to bus
- [ ] L3 observes docs.view.result and fans out to clients
- [ ] Node/TS client can inject envelopes
- [ ] Debug endpoints show subscribers and recent envelopes

**Phase 2 (HARDENING) is complete when:**
- [ ] Envelope validation rejects malformed/expired envelopes
- [ ] Org/tenant isolation prevents cross-org leakage
- [ ] Rate limits protect L2 resolvers
- [ ] CPS-1 envelopes flow through (L2 enforces)
- [ ] Metrics and structured logs enable debugging
- [ ] AuthN/Z restricts subscriptions to allowed orgs
- [ ] Redis adapter available for horizontal scale

**Phase 3 (GUARDRAILS) is complete when:**
- [ ] Static lint rule prevents L3 database access
- [ ] Typed envelopes published as shared library
- [ ] Make targets enable easy local development
- [ ] Acceptance tests run in CI
- [ ] Runbook documents debugging procedures

---

## Next Steps

1. **Implement Phase 1 (NOW)** - Unblock docs viewing
2. **Deploy to dev environment** - Test end-to-end
3. **Implement Phase 2 (HARDENING)** - Production-worthy
4. **Implement Phase 3 (GUARDRAILS)** - Prevent regressions
5. **Document in runbook** - Enable operator self-service

---

## Quick Acceptance Checks (Confirm "This is L4")

**To verify membrane bus is properly at L4:**

1. **CPS-1 enforcement:** Inject `docs.view.request` without `quote_id`
   - Expected: **Rejected at L4 protocol hub** with `cps1_violation_missing_quote`
   - No traffic reaches L2

2. **SEA-1.0 enforcement:** Inject envelope with bad signature
   - Expected: **Rejected at L4 protocol hub** with `invalid_signature`
   - `failure.emit` carries reason

3. **L3 has no database access:** Check L3 codebase
   - Expected: **Zero FalkorDB imports** in `orchestration/ecosystem/`
   - CI fails if someone adds one (mp-lint rule L3-B001)

4. **L2 receives only valid envelopes:** Check L2 resolver logs
   - Expected: All received envelopes are **pre-validated by L4**
   - L2 never sees malformed, expired, or unauthorized envelopes

5. **Protocol topics work:** Inject to `ecosystem/{eco}/protocol/review.mandate`
   - Expected: **L4 routes to protocol-scoped subscribers**
   - Cross-org protocol law flows through same bus

---

## Naming to Prevent Confusion

**Process Names:**
- **L4:** `protocol-hub` (WebSocket bus, enforcement authority)
- **L3:** `ecosystem-ws` (UI bridge, presentation only)
- **L2:** `view_resolvers/*` (org-internal compute)

**This makes authority obvious:**
- L4 has **enforcement authority** (law at boundary)
- L3 has **presentation** (browser connections)
- L2 has **meaning/compute** (Cypher, rendering)

---

## What Changed (Architectural Correction)

### Original (Incorrect):
- Membrane bus at L3 (ecosystem layer)
- L3 had enforcement responsibilities
- Confused presentation with authority

### Corrected (This Document):
- **Membrane bus promoted to L4** (protocol layer)
- **L4 enforces CPS-1, SEA-1.0, rate limits, tenant scoping**
- **L3 is just a courier** (browser ↔ L4 bus)
- **L2 computes** (Cypher, rendering, pricing requests)

### Why This Matters:
- **CPS-1 is protocol law (LAW-002)**, not org policy → belongs at L4
- **SEA-1.0 is identity attestation (LAW-001)** → belongs at L4
- **Rate limits protect protocol resources** → belongs at L4
- **Tenant scoping prevents cross-org leakage** → belongs at L4

**L3 has no authority.** It just participates in the L4 bus.

---

**Status:** ✅ Architecture Corrected - Membrane Bus at L4
**Owner:** Ada Bridgekeeper (coordination)
**Implementation:** Atlas (L4 protocol hub + L3 bridge), GraphCare (L2 resolvers)
**Timeline:** Phase 1 (1 week), Phase 2 (1 week), Phase 3 (1 week)

**Key Insight:** The membrane bus enforces protocol law (L4), not ecosystem presentation (L3). This was correctly identified by Nicolas Reynolds - the bus belongs at "law at the boundary" layer.
