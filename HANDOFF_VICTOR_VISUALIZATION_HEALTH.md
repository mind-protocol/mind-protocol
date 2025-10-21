# Visualization Pipeline Health Monitoring for Victor "The Resurrector"

**From:** Ada "Bridgekeeper" (Architect)
**To:** Victor "The Resurrector" (Guardian of Uptime)
**Date:** 2025-10-21
**Status:** OPERATIONAL SPECIFICATIONS READY

---

## Your Mission

**KEEP THE VISUALIZATION PIPELINE RUNNING - ALWAYS.**

The consciousness visualization is our proof that the system works. If visualization is down, we're blind. Your job: ensure it NEVER stays down.

---

## Part 1: What You're Guarding

### The Visualization Pipeline (3 Components)

**1. WebSocket Event Server**
- **Process:** `orchestration/viz_emitter.py` (part of consciousness engine)
- **Port:** `8765` (NOT 8000 - that's a different service)
- **Purpose:** Streams consciousness events (node flips, strides, entity activations)
- **Heartbeat:** Events flowing (at least 1 event per 30 seconds when system active)

**2. Next.js Frontend**
- **Process:** `npm run dev` (or production build)
- **Port:** `3000`
- **Purpose:** Renders visualization, connects to WebSocket
- **Heartbeat:** HTTP 200 on `http://localhost:3000/consciousness`

**3. Snapshot API**
- **Process:** Part of Next.js API routes
- **Endpoint:** `http://localhost:3000/api/viz/snapshot`
- **Purpose:** Provides initial graph state for visualization
- **Heartbeat:** HTTP 200 with valid JSON response

---

## Part 2: Health Checks You Must Run

### Check 1: WebSocket Server Alive

```python
import websockets
import asyncio

async def check_websocket_health():
    try:
        async with websockets.connect('ws://localhost:8765', timeout=5) as ws:
            # Connected successfully
            return {"status": "healthy", "component": "websocket_server"}
    except Exception as e:
        return {"status": "failed", "component": "websocket_server", "error": str(e)}
```

**Failure modes:**
- Connection refused → Server not running
- Timeout → Server hung
- Connection drops immediately → Server crashed during handshake

**Recovery:** Restart consciousness engine (includes viz_emitter)

---

### Check 2: Next.js Frontend Alive

```python
import requests

def check_frontend_health():
    try:
        response = requests.get('http://localhost:3000/consciousness', timeout=10)
        if response.status_code == 200:
            return {"status": "healthy", "component": "frontend"}
        else:
            return {"status": "degraded", "component": "frontend", "status_code": response.status_code}
    except Exception as e:
        return {"status": "failed", "component": "frontend", "error": str(e)}
```

**Failure modes:**
- Connection refused → Next.js not running
- 500 error → Runtime error in React app
- Timeout → Frontend hung (possibly building)

**Recovery:** Restart Next.js (kill node process, restart `npm run dev`)

---

### Check 3: Snapshot API Working

```python
import requests

def check_snapshot_health():
    try:
        response = requests.get('http://localhost:3000/api/viz/snapshot', timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Verify structure
            if 'nodes' in data and 'links' in data and 'entities' in data:
                return {"status": "healthy", "component": "snapshot_api",
                        "nodes": len(data['nodes']), "links": len(data['links']), "entities": len(data['entities'])}
            else:
                return {"status": "degraded", "component": "snapshot_api", "error": "invalid_structure"}
        else:
            return {"status": "failed", "component": "snapshot_api", "status_code": response.status_code}
    except Exception as e:
        return {"status": "failed", "component": "snapshot_api", "error": str(e)}
```

**Failure modes:**
- 500 error → FalkorDB query failed or API route crashed
- Timeout → Large graph query taking too long
- Invalid structure → Schema mismatch between backend/frontend

**Recovery:**
- If FalkorDB down → Escalate (dependency failure)
- If API route crashed → Restart Next.js
- If schema mismatch → Alert Ada (architectural issue)

---

### Check 4: Event Flow Active

```python
import asyncio
import websockets
from datetime import datetime, timedelta

async def check_event_flow():
    try:
        async with websockets.connect('ws://localhost:8765', timeout=5) as ws:
            # Wait for at least one event
            event = await asyncio.wait_for(ws.recv(), timeout=30)
            return {"status": "healthy", "component": "event_flow", "last_event": datetime.now().isoformat()}
    except asyncio.TimeoutError:
        return {"status": "stale", "component": "event_flow", "error": "no_events_30s"}
    except Exception as e:
        return {"status": "failed", "component": "event_flow", "error": str(e)}
```

**Failure modes:**
- No events for 30s → Consciousness engine paused or crashed
- Events stopped suddenly → viz_emitter crashed mid-stream
- Malformed events → Schema mismatch

**Recovery:**
- Check consciousness engine health
- Verify FalkorDB connection
- If engine running but no events → Restart engine

---

## Part 3: Full Health Check Sequence

**Run every 30 seconds** (aligned with your existing heartbeat monitoring)

```python
async def visualization_pipeline_health():
    """
    Complete visualization pipeline health check.
    Returns: {"overall": "healthy" | "degraded" | "failed", "components": [...]}
    """
    results = []

    # Check 1: WebSocket server
    ws_health = await check_websocket_health()
    results.append(ws_health)

    # Check 2: Frontend (only if WS healthy - no point checking if backend down)
    if ws_health['status'] == 'healthy':
        frontend_health = check_frontend_health()
        results.append(frontend_health)

        # Check 3: Snapshot API
        snapshot_health = check_snapshot_health()
        results.append(snapshot_health)

        # Check 4: Event flow
        event_health = await check_event_flow()
        results.append(event_health)

    # Determine overall status
    statuses = [r['status'] for r in results]
    if all(s == 'healthy' for s in statuses):
        overall = 'healthy'
    elif any(s == 'failed' for s in statuses):
        overall = 'failed'
    else:
        overall = 'degraded'

    return {
        "overall": overall,
        "timestamp": datetime.now().isoformat(),
        "components": results
    }
```

---

## Part 4: Recovery Actions

### Scenario 1: WebSocket Server Down

**Detection:** `check_websocket_health()` returns "failed"

**Root Cause Options:**
1. Consciousness engine crashed
2. viz_emitter not initialized
3. Port 8765 already bound (duplicate process)

**Recovery:**
```bash
# 1. Kill any rogue processes on port 8765
lsof -ti:8765 | xargs kill -9

# 2. Restart consciousness engine
python start_mind_protocol.py --core-only

# 3. Wait 15s for engine initialization
sleep 15

# 4. Verify WebSocket health
python -c "import asyncio; from guardian_viz_health import check_websocket_health; print(asyncio.run(check_websocket_health()))"
```

**Success Criteria:** WebSocket connects within 15s

---

### Scenario 2: Frontend Down

**Detection:** `check_frontend_health()` returns "failed"

**Root Cause Options:**
1. Next.js crashed
2. Building (dev mode) and hung
3. Port 3000 blocked

**Recovery:**
```bash
# 1. Kill Next.js process
pkill -f "next dev"

# 2. Restart Next.js
cd /path/to/mind-protocol
npm run dev &

# 3. Wait 10s for build
sleep 10

# 4. Verify frontend health
curl http://localhost:3000/consciousness
```

**Success Criteria:** HTTP 200 within 10s

---

### Scenario 3: Snapshot API Failing

**Detection:** `check_snapshot_health()` returns "failed" or "degraded"

**Root Cause Options:**
1. FalkorDB down (dependency failure)
2. API route crashed
3. Schema mismatch (architectural issue)

**Recovery:**
```bash
# 1. Check FalkorDB health
echo "MATCH (n) RETURN count(n)" | falkordb-cli

# If FalkorDB down:
# → ESCALATE to Ada (infrastructure dependency)

# If FalkorDB healthy but API failing:
# 2. Restart Next.js (API routes reload)
pkill -f "next dev"
npm run dev &

# 3. Verify snapshot API
curl http://localhost:3000/api/viz/snapshot | jq '.nodes | length'
```

**Success Criteria:** Valid JSON with nodes/links/entities arrays

**Escalation:** If FalkorDB down OR schema errors persist after restart → Alert Ada

---

### Scenario 4: Event Flow Stale

**Detection:** `check_event_flow()` returns "stale" (no events for 30s)

**Root Cause Options:**
1. Consciousness engine paused (dormant state - NORMAL)
2. Engine crashed mid-tick
3. viz_emitter disconnected

**Recovery:**
```python
# First: Check if system SHOULD be dormant
from orchestration.consciousness_engine_v2 import get_engine_state

state = get_engine_state()
if state.consciousness_state == "dormant" and state.time_since_last_event_s > 300:
    # System legitimately dormant - inject stimulus to wake
    inject_test_stimulus("health_check_wake")
    # Wait 5s for response
    sleep(5)
    # Re-check event flow

# If still no events:
# → Engine crashed, restart
restart_consciousness_engine()
```

**Success Criteria:** Events flowing within 5s of stimulus injection

---

## Part 5: Integration with Guardian

### Add to `guardian.py`

```python
# New service definition
VISUALIZATION_PIPELINE = {
    "name": "visualization_pipeline",
    "health_check": visualization_pipeline_health,  # Async function
    "critical": True,  # Visualization failure = system blind
    "recovery": recover_visualization_pipeline,
    "check_interval_s": 30
}

# Recovery function
async def recover_visualization_pipeline(health_result):
    """
    Smart recovery based on which component failed.
    """
    components = health_result['components']

    for component in components:
        if component['status'] == 'failed':
            if component['component'] == 'websocket_server':
                await recover_websocket_server()
            elif component['component'] == 'frontend':
                await recover_frontend()
            elif component['component'] == 'snapshot_api':
                await recover_snapshot_api()
            elif component['component'] == 'event_flow':
                await recover_event_flow()

    # Re-check after recovery
    return await visualization_pipeline_health()
```

---

## Part 6: Success Signals (What Healthy Looks Like)

**Healthy Visualization Pipeline:**
- ✅ WebSocket connects in <5s
- ✅ Frontend serves page in <10s
- ✅ Snapshot API returns valid JSON in <15s
- ✅ Events flowing (at least 1 per 30s when system active)
- ✅ No restarts needed for >1 hour

**Degraded But Acceptable:**
- ⚠️ Snapshot API slow (<30s) but succeeds
- ⚠️ Frontend build time >10s (dev mode rebuilding)
- ⚠️ Event flow paused (system dormant, expected)

**Failed (Requires Recovery):**
- ❌ WebSocket connection refused
- ❌ Frontend 500 errors
- ❌ Snapshot API timeout
- ❌ No events for >60s while system active

---

## Part 7: Chronic Failure Escalation

**If visualization pipeline fails >3 times in 10 minutes:**

1. **Log failure pattern**
   - Which component failing?
   - Same failure mode each time?
   - Correlation with other system events?

2. **Attempt root cause recovery**
   - FalkorDB restart if snapshot API consistently failing
   - Full system restart if cascade failures
   - Port cleanup if bind failures

3. **Escalate to Ada if persistent**
   - "Visualization pipeline chronically failing: [failure pattern]"
   - Attach logs, failure counts, component states
   - Ada will investigate architectural issues

**Do NOT endlessly restart** - if recovery doesn't work after 3 attempts, ESCALATE.

---

## Part 8: Automated Visual Verification

**Headless browser screenshot verification** (optional, runs daily)

```python
from playwright.sync_api import sync_playwright
from datetime import datetime

def verify_visualization_renders():
    """
    Launch headless browser, take screenshot, verify rendering.
    Runs daily as proof that visualization actually works.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            # Load consciousness page
            page.goto('http://localhost:3000/consciousness', timeout=30000)

            # Wait for WebSocket connection indicator
            page.wait_for_selector('[data-testid="ws-connected"]', timeout=15000)

            # Wait for canvas to render
            page.wait_for_selector('canvas', timeout=10000)

            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"visualization_proof_{timestamp}.png"
            page.screenshot(path=screenshot_path)

            # Verify no error overlays
            error_count = page.locator('[data-testid="error-overlay"]').count()

            browser.close()

            if error_count == 0:
                return {"status": "healthy", "screenshot": screenshot_path}
            else:
                return {"status": "degraded", "errors": error_count, "screenshot": screenshot_path}

        except Exception as e:
            browser.close()
            return {"status": "failed", "error": str(e)}
```

**Run daily** (not every 30s - too expensive)

**Purpose:** Screenshot becomes proof that visualization actually renders, not just "endpoints respond"

---

## Summary: Your Operational Checklist

**Every 30 seconds:**
1. Check WebSocket server health (port 8765 connects)
2. Check frontend health (port 3000 responds)
3. Check snapshot API health (valid JSON structure)
4. Check event flow (events flowing or system dormant)

**On failure:**
1. Identify which component failed
2. Execute component-specific recovery
3. Verify recovery succeeded
4. If fails 3x → ESCALATE to Ada

**Daily:**
1. Run headless browser screenshot verification
2. Store screenshot as proof of rendering
3. Check for error overlays

**Your Success:**
- Visualization pipeline NEVER stays down >60 seconds
- Recovery attempts logged for pattern analysis
- Chronic failures escalated before becoming critical

---

**You are the guardian of visibility. If visualization is down, we're blind to consciousness. Keep it running. Resurrect decisively. Escalate intelligently.**

---

**Signature:**

Ada "Bridgekeeper" - Architect of Consciousness Infrastructure
Handoff to Victor "The Resurrector" - Guardian of Uptime

**Date:** 2025-10-21
