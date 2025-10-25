# Team Synchronization Log

## 2025-10-25 14:05 - Atlas: ✅ Telemetry Counters Endpoint Implemented (Awaiting Restart)

**Status:** War Room Plan P1 task complete - Counters endpoint implemented and ready for testing

**What Was Implemented:**

1. **Counter Tracking in ConsciousnessStateBroadcaster** ✅
   - Location: `orchestration/libs/websocket_broadcast.py`
   - Added `event_counts_total` dict for total counts since boot
   - Added `event_timestamps` deque for 60s sliding window per event type
   - Counter incremented in `broadcast_event()` method BEFORE availability check (tracks even when no clients connected)
   - Automatic cleanup of timestamps outside 60s window

2. **GET /api/telemetry/counters Endpoint** ✅
   - Location: `orchestration/adapters/api/control_api.py` lines 1023-1094
   - Returns per-type event counts with `total` and `last_60s` fields
   - Includes timestamp, uptime_seconds, status
   - Accesses broadcaster via first engine's reference

**Implementation Details:**
```python
# Counter tracking in broadcast_event()
now = time.time()
self.event_counts_total[event_type] += 1
self.event_timestamps[event_type].append(now)

# Clean old timestamps outside 60s window
cutoff = now - 60.0
while self.event_timestamps[event_type] and self.event_timestamps[event_type][0] < cutoff:
    self.event_timestamps[event_type].popleft()
```

**Testing Status:** ⏳ BLOCKED - Requires Server Restart

WebSocket server running old code (PID 10880 on port 8000). Guardian not detecting file changes for hot-reload. Per project protocol, not manually killing processes.

**Success Criteria (Once Restarted):**
- GET http://localhost:8000/api/telemetry/counters returns JSON
- Shows monotonically rising counts for tick_frame_v1, node.flip, wm.emit
- last_60s reflects active generation (~57 events/min for 10Hz events)

**Next Actions:**
1. Wait for guardian restart or manual restart by Victor/Nicolas
2. Test endpoint with `curl http://localhost:8000/api/telemetry/counters`
3. Verify counts match expected rates (tick_frame_v1 should be ~600/min at 10Hz)

**Files Modified:**
- `orchestration/libs/websocket_broadcast.py` - Counter tracking + get_counter_stats()
- `orchestration/adapters/api/control_api.py` - REST endpoint

---

## 2025-10-25 19:30 - Victor: 🔍 CRITICAL FINDING - Emitters Already Exist

**Status:** War-room P0.2 task "Felix adds emitters" is ALREADY COMPLETE in codebase

**Evidence from code inspection:**

✅ **tick_frame.v1** - IMPLEMENTED
- Location: `consciousness_engine_v2.py` lines 1322-1422
- Broadcasts at end of every tick with entity data, active nodes, criticality metrics
- Includes tripwire monitoring for observability

✅ **node.flip** - IMPLEMENTED
- Location: `consciousness_engine_v2.py` lines 1037-1079
- Detects threshold crossings (E >= theta transitions)
- Top-K decimation (20 most significant flips by |ΔE|)
- Broadcasts per flip with E_pre, E_post, theta

✅ **wm.emit** - IMPLEMENTED
- Location: `consciousness_engine_v2.py` line 1183-1196
- Entity-first working memory selection
- Broadcasts selected entities with token shares

**Implication:** The issue is NOT missing emitters. All 3 events are already coded and should be firing every tick.

**Root cause must be one of:**
1. Events not firing (broadcaster unavailable? conditionals not met?)
2. Events firing but not reaching dashboard (websocket transport issue?)
3. Dashboard receiving but not rendering (frontend store/rendering issue?)

**Next Action:** Need to verify if events are actually being broadcast:
- Check `ws_stderr.log` for "[Broadcaster]" messages
- Verify `self.broadcaster.is_available()` returns True
- Confirm engines are ticking (not frozen at tick_count=0)
- Test websocket connection receives events

**Diagnosis Results:**

Checked `ws_stderr.log` (last entry 14:40:52):
- ✅ Engines ticking (Victor: 13,600 ticks, Felix: 13,300 ticks)
- ✅ Persistence working (flushing nodes successfully)
- ✅ Broadcaster initialized (WebSocket manager imported)
- ❌ **ZERO broadcast events in logs** - no "[Broadcaster]" activity
- ⚠️ **All engines show "Active: 0/XXX"** - NO nodes above threshold!

**Root Cause #1: Zero Active Nodes**
- Energy too low (all E < theta)
- Result: node.flip has nothing to flip, wm.emit has empty workspace
- tick_frame.v1 should still fire but may be conditional on activity

**Root Cause #2: Hot-Reload Limitation**
- Tested Atlas's `/api/telemetry/counters` endpoint → 404 Not Found
- Code exists in control_api.py line 1058 but not loaded
- Hot-reload only updates routes, NOT in-memory engine objects or API routes
- **REQUIRES FULL RESTART**

**Team Coordination:**
- Felix: Verify broadcaster.is_available() returns True in tick loop (add debug log)
- Atlas: Your counters endpoint exists but isn't live - needs full restart to load
- Iris: Blocked until backend emits events
- Victor: **IMMEDIATE ACTION - Full system restart required**

**Victor's Hot-Reload Fix:**

✅ **Implemented automatic file watcher for engine code changes**

**What was added** (`websocket_server.py` lines 1172-1234):
- File watcher using `watchdog` library
- Monitors critical files: consciousness_engine_v2.py, control_api.py, websocket_broadcast.py, falkordb_adapter.py, node.py, graph.py
- On file change: 2-second delay → exit with code 99 → guardian restarts automatically
- Enabled by `MP_HOT_RELOAD=1` (already set in guardian.py line 375)

**How it works:**
1. Developer saves file (e.g., control_api.py)
2. Watchdog detects change within 1 second
3. Log shows: "🔥 HOT-RELOAD: Detected change in control_api.py"
4. Wait 2 seconds for file write to complete
5. Process exits cleanly
6. Guardian detects exit and restarts websocket_server immediately
7. New code loads on restart

**Current Status:**
- ✅ Watchdog library installed
- ✅ File watcher code added to websocket_server.py
- ⏳ **REQUIRES ONE RESTART** to bootstrap hot-reload system
- After restart: All future file saves trigger automatic restart

**To Test:**
1. Restart websocket server (or full system)
2. Edit any watched file (e.g., add a comment to control_api.py)
3. Save file
4. Watch logs - should see "🔥 HOT-RELOAD: Detected change..." within 2 seconds
5. Guardian restarts server automatically
6. New code loads

**Bootstrap Paradox Resolved:**
- Old code doesn't have hot-reload → needs manual restart
- New code has hot-reload → automatic restarts from now on
- This is the ONE manual restart to enable automatic future restarts

---

## 2025-10-25 19:00 - Nicolas: 🎯 LIVE DYNAMICS PUSH — 90-MINUTE WAR-ROOM

**Goal:** Within one session, get the dashboard to show *visible motion*: frame ticks, node size/glow changes, WM halos, and sampled link flows. Kill "Awaiting data…" across panels.

---

### P0 — Minimal Event Pack (What Must Exist for Motion)

These 4 event types are the only things the frontend needs to animate:

1. **`tick_frame_v1`** (timebase, 10Hz)
```json
{"v":"2","type":"tick_frame_v1","frame_id":8895,"citizen_id":"felix","t_ms":1729864523456}
```

2. **`node.flip`** (top-K energy deltas per frame)
```json
{"v":"2","type":"node.flip","frame_id":8895,"citizen_id":"felix","nodes":[{"id":"n_123","E":3.42,"dE":+0.18},{"id":"n_456","E":0.77,"dE":-0.09}]}
```

3. **`wm.emit`** (working-memory halos / focus)
```json
{"v":"2","type":"wm.emit","frame_id":8895,"citizen_id":"felix","top":["entity_translator","entity_validator"],"all":[["entity_translator",0.82],["entity_validator",0.65]]}
```

4. **`link.flow.summary`** (sampled flows per stride; ~2% decimation)
```json
{"v":"2","type":"link.flow.summary","frame_id":8895,"citizen_id":"felix","flows":[{"src":"n_a","dst":"n_b","flow":0.041},{"src":"n_c","dst":"n_d","flow":0.018}]}
```

**Acceptance:** Seeing any two of these arrive continuously is enough for visible motion (node size/glow from `node.flip`; halos from `wm.emit`). `tick_frame_v1` keeps timeline moving. `link.flow.summary` adds "life" along edges.

---

### P1 — Task Breakdown by Owner

**Felix — Engine Emitters**
Files: `consciousness_engine_v2.py`, `diffusion_runtime.py`, `strengthening.py`

- [ ] Emit `tick_frame_v1` at end of each tick (10Hz) - Hook: end of `tick()` → `broadcaster.broadcast_event(...)`
- [ ] Emit `node.flip`: compute top-K |dE| nodes since last frame (K≈25), clamp to max size 50 per event - Hook: after injections + decay → diff `(E_now - E_prev)`
- [ ] Emit `wm.emit`: pick top subentities by energy (≥θ and top-N) - Hook: same cadence as tick
- [ ] Verify `tier.link.strengthened` still fires with ~2% decimation
- [ ] Do not drop stimuli with `embedding=None` - fallback path already implemented

**Success:** `ws_stderr.log` shows continuous `[Broadcaster] tick_frame_v1`, `node.flip count=XX`, `wm.emit`, `link.flow.summary`. Within 5-10s of stimulus, see `node.flip` for that citizen.

---

**Atlas — Transport + Diagnostics**
Files: `websocket_server.py`, `control_api.py`, `queue_poller.py`

- [ ] Counters endpoint: `GET /api/telemetry/counters` returning per-type counts since boot + 60s sliding window - Store in dict incremented inside `ConsciousnessStateBroadcaster.broadcast_event`
- [ ] Hot-reload guard: "full restart suggested" banner when engine-side code changes
- [ ] Ensure only one consumer drains JSONL (disable ConversationWatcher drain for ambient)

**Success:** `GET /api/telemetry/counters` shows monotonically rising counts for all 4 event types.

---

**Iris — Frontend Plumbing + UI**
Files: `useWebSocket.ts`, `normalizeEvents.ts`, `store/*`, `PixiRenderer.ts`, `components/*`

- [ ] Normalizer: map events 1-4 exactly - Keep permissive: accept old aliases, log warnings for unknown types
- [ ] Store updates:
  - `tick_frame_v1` → `ui.frameId = ...`
  - `node.flip` → update `store.nodes[id].energy` and `lastDelta`
  - `wm.emit` → `store.wm.active = top`, `store.wm.scores = all`
  - `link.flow.summary` → append to rolling ring-buffer for spark/flow overlays
- [ ] Renderer binding: Add glow intensity = f(|dE|) for last 500ms, WM Halo = f(store.wm.scores[entity])
- [ ] Active Subentities panel: read `wm.emit.top` and render as list

**Success:** "Tick Timeline" moves; "Active Subentities" shows real entities; nodes resize/glow within seconds; halos appear/disappear with WM focus.

---

**Victor — Stability & Restart Discipline**
Files: `guardian.py`, `launcher.py`

- [ ] Engine code change = full restart (not just uvicorn reload) - Keep 8s cooldown; print "♻ Engine objects re-instantiated"
- [ ] Ensure logs split: `ws_stdout.log`, `ws_stderr.log`, `guardian.log`
- [ ] Add boot banner with git SHA to prove freshness

**Success:** After engine file change, see banner and frame counter resets (proves fresh code).

---

**Ada — Event Contract + Schema Hygiene**
Files: `SYNC.md`, `schema_registry`, `trace_parser.py`

- [ ] Document canonical shapes (above) and pin in SYNC
- [ ] Keep schema counts 45/23 stable; verify no drift after hot-reloads
- [ ] Add one-time linter to flag events missing `v`, `type`, `citizen_id`, `frame_id`

**Success:** SYNC contains canonical docs; counters show only canonical types (no typos).

---

### P2 — "Awaiting Data" Panel-by-Panel Checklist

- **Regulation / Sparks / Task Mode** → needs `stride.exec` (OPTIONAL for first live demo) - Interim: Down-level to `node.flip` as visual driver
- **3-Tier Strengthening** → `tier.link.strengthened` (already implemented) - Check decimation (2%) and ring buffer length
- **Dual-View Learning** → `weights.updated` (TRACE-driven) - Will fill as WeightLearner runs; not blocking
- **Phenomenology Alignment** → `phenomenology.mismatch` - Validate shape; not needed for first motion
- **Consciousness Health** → `health.phenomenological` (done) - Wire to panel; use 5-tick cadence and hysteresis
- **Tick Timeline** → `tick_frame_v1` - Should be first to go green
- **Active Subentities** → `wm.emit` - Replace placeholder now

---

### P3 — Quick Wins (Non-Blocking)

**Layout tuning (Pixi):**
- Increase baseline edge length; add min edge length
- Reduce node scatter by increasing charge damping
- Freeze layout after 3s to reduce drift; resume on focus/drag

**Tooltips:**
- Node: `name`, `E`, `θ`, top incoming/outgoing (2 each)
- Link: `source → target`, `w`, last flow sample

**Semantic search fix:**
- Route to backend semantic_search adapter
- If index cold, fall back to keyword search with "warming up" badge

---

### P4 — Proof Page (Single Look)

Add "**Live Telemetry Debug**" page (developer-only):
- Counters from `/api/telemetry/counters` (per type, last 60s rate)
- Last 20 events (type, citizen, size)
- Frame ID per citizen
- Toggle to draw WM halos / link flow samples

**Exit Criteria:** After sending one stimulus, within ≤2s:
- (a) `tick_frame_v1` increments
- (b) `node.flip` > 0 items
- (c) halos appear in Active Subentities
- (d) at least 1 `link.flow.summary` per ~50 strides
- (e) "Awaiting data" disappears from Tick Timeline and Active Subentities

---

### 30-Minute Playbook

1. **Felix (10 min):** Add 3 emitters (tick_frame_v1, node.flip, wm.emit) + ensure broadcaster calls
2. **Victor (2 min):** Hard restart engines (banner shows)
3. **Atlas (5 min):** Counters endpoint + sanity log "Broadcasted ..." lines
4. **Iris (10 min parallel):** Wire `wm.emit` to Active Subentities; `node.flip` to store → verify node resizing/glow
5. **Everyone (3 min):** POST one stimulus; confirm motion; capture screenshots

---

### Known Foot-Guns (Avoid)

- **Hot reload ≠ engine reload** - Always trigger full engine restart when engine files change
- **Wrong fields** - Runtime → DB mapping must write `E`/`theta` from `energy_runtime`/`threshold_runtime`
- **Dropping `embedding=None`** - Keep fallback injection path (already implemented)
- **Two consumers** - Ensure only `queue_poller` injects ambient; CW handles conversations

---

### Ownership (RACI)

| Task | Owner | Support | When Done |
|------|-------|---------|-----------|
| Emitters (tick_frame_v1, node.flip, wm.emit) | Felix | Atlas | PR merged, banner shows, counters rising |
| Counters endpoint | Atlas | Victor | `/api/telemetry/counters` responds; rates > 0 |
| Active Subentities panel | Iris | Felix | Shows top entities within 2s of stimulus |
| Engine full-restart on code change | Victor | Atlas | Banner + frame reset after edit |
| Event schema doc | Ada | Felix/Iris | SYNC updated; linter warns on bad payloads |

---

**Note from Nicolas:** You already proved end-to-end persistence ("Flushed 176/391"). The UI is quiet purely due to **emitter & wiring**. Land the 3 emitters + frontend bindings and you'll immediately see motion (size/glow/halos), even before advanced panels fill in.

**Offer:** Drop the `tick()` tail snippet and Nicolas will annotate exactly where to place the three `broadcast_event` calls for Felix to paste in one shot.

---

## 2025-10-25 14:35 - Ada: 📊 DASHBOARD INTEGRATION DIAGNOSTIC

**Status:** Backend operational ✅ | Frontend rendering issues identified 🔴

**Key Findings:**
1. **WebSocket events flowing correctly** - 8 event types broadcasting for all 8 citizens
2. **All citizens dormant by default** - No stimulus = No activity = Dashboard correctly shows "waiting for data"
3. **Frontend not consuming/rendering events** - Active Subentities Panel, graph viz, 15+ panels broken despite events arriving

**Evidence:**
- WebSocket: ws://localhost:8000/api/ws (1 client connected)
- Events confirmed: tick.update, subentity.snapshot, tick_frame_v1, wm.emit, decay.tick, criticality.state, consciousness_state, frame.start
- Stimulus test: Felix dormant → alert ✅ (proves pipeline works)
- All entities: energy=0.0, theta=1.0, active=false (dormant)

**Complete Diagnostic:** `DASHBOARD_INTEGRATION_DIAGNOSTIC.md`

**Quick Actions:**
```bash
# Test: Inject stimulus to create visible activity
echo '{"type": "user_message", "content": "Dashboard test", "citizen_id": "felix"}' >> .stimuli/queue.jsonl
```

**Coordination:**
- **Iris:** Fix event rendering (Active Subentities, graph viz, empty panels)
- **Atlas:** Verify missing emitters (stride.exec, emotions, health)
- **Ada:** Map emitter gaps vs. dashboard requirements

---

## BRAIN COMPETITION

Felix avatar
Felix
frame 11526 (focused)
483 nodes • 182 links
▶
Luca avatar
Luca
frame 11806 (idle)
391 nodes • 189 links
▶
Atlas avatar
Atlas
frame 12353 (idle)
131 nodes • 55 links
▶
Ada avatar
Ada
frame 11927 (idle)
305 nodes • 91 links
▶
Mind_Protocol avatar
Mind_Protocol
frame 7151 (idle)
2208 nodes • 817 links
▶
Iris avatar
Iris
frame 11858 (idle)
338 nodes • 126 links
▶
Victor avatar
Victor
frame 11722 (idle)
382 nodes • 119 links

--> Who will have the **BIGGEST BRAIN** by the end of the day??? We'll see! (I make a surprise for him/her!)

## 2025-10-25 18:30 - Luca: Substrate Specifications Complete - Ready for Dashboard Integration

**Context:** Dashboard integration priority. All telemetry panels showing "Awaiting data" - blocker is backend emitters + APIs, not substrate specs.

**Substrate Work Completed This Session:**

1. **stimulus_injection.md v2.1** ✅
   - Dual-channel injection policy (Top-Up + Amplify)
   - Threshold Oracle with type-specific baselines
   - Complete pseudocode for Felix implementation
   - Acceptance tests for propagation validation

2. **stimulus_diversity.md** ✅
   - L1 stimulus types: 7 types (conversation, console_error, commit, file_change, backend_error, screenshot, self_observation)
   - L2 stimulus types: 6 types (5 intents + 1 incident)
   - Attribution model (WM/entity → routing)
   - Routing model (top_up/amplify/hybrid)
   - All Nicolas's decisions integrated (thresholds, OCR, alerts, correlation, persistence)

3. **stimulus_diversity_implementation_plan.md** ✅
   - Phase A-D mapped to Priority 1-5
   - Ownership clear (Atlas/Felix/Iris/Victor)
   - Ready-to-use config (deriver_rules.yaml)
   - Week-by-week rollout schedule

**Substrate Gap Identified:**
- Autonomy architecture needs node types: IntentCard, Outcome, Capability, Permission, Track_Record
- Not blocking dashboard integration (different workstream)
- Awaiting priority decision on autonomy substrate spec

**Dashboard Integration Blockers (NOT substrate):**

Per Nicolas's execution plan P0-P2:
- **P1 (Entity Membership):** Atlas/Felix need to persist `MEMBER_OF` links + expose `/entity/:name/members` API
  - Substrate ready: `MEMBER_OF` link type exists in schema
  - Blocker: Implementation (calling persist_membership(), API endpoint)

- **P2 (Dashboard Emitters):** Felix needs to emit health/learning/tier/mismatch events
  - Substrate ready: Event schemas exist, telemetry contract defined
  - Blocker: Implementation (wiring emit calls in engine)

- **Graph Visualization:** Iris + Atlas (force layout, WebSocket streaming, hover info)
  - Substrate ready: Graph schema complete
  - Blocker: Implementation (force graph physics, real-time updates)

**Status:** Substrate specifications complete. Dashboard integration blocked on implementation, not specs.

**Handoff to Ada:** Orchestration coordination needed for P1-P2 implementation across Felix/Atlas/Iris.

**Availability:** Standing by for substrate questions during implementation. No blocking substrate gaps identified.

---

## 2025-10-25 10:45 - Victor: Critical Bug Fix - Persistence Operational

**Context:** Dashboard showing "No data yet" across all telemetry panels. Root cause: Two separate persistence bugs preventing consciousness substrate from writing energy values to FalkorDB.

**Bugs Found & Fixed:**

1. **Bug #1 - Wrong attribute name (Lines 2086, 2147 in consciousness_engine_v2.py)**
   - Code used: `getattr(node, "energy_runtime", 0.0)`
   - Node class has: `node.E`
   - Result: Every persist wrote E=0.0 to database
   - Fix: Changed to `float(node.E)`

2. **Bug #2 - ID format mismatch (Lines 2094-2096, 2155-2157)**
   - Engine sends: `{'id': 'node_name', 'E': 5.5}`
   - FalkorDB has: `id="NodeType:node_name"` (prefixed)
   - Result: WHERE clause matched 0 nodes ("Flushed 0/2159")
   - Fix: Match by name+label instead of ID

**Status:** ✅ BOTH FIXES VERIFIED WORKING

Evidence:
- Before: `Flushed 0/2159 dirty nodes to FalkorDB`
- After: `Flushed 176/391 dirty nodes to FalkorDB`
- Database: 186 nodes with E>0 (max: 0.49, avg: 0.49)
- Pipeline: Stimulus → Injection → Memory → Database ✅

**Impact for Dashboard (Iris):**
- Consciousness substrate now has persistent memory
- Energy values writing to FalkorDB correctly
- Telemetry events should start flowing (stride.exec, node.flip, etc.)
- "Awaiting data" panels should populate once stride execution begins

**Next Steps:**
- Monitor for stride execution logs (requires active nodes: E >= theta)
- Verify telemetry events reach dashboard WebSocket
- Dashboard should show live activity once energy accumulates above thresholds

**Files Changed:**
- `orchestration/mechanisms/consciousness_engine_v2.py` (persistence fixes)
- `orchestration/adapters/api/control_api.py` (added /api/ping endpoint)

**NEW BLOCKER DISCOVERED (10:50):**

After fixing persistence, discovered **energy-theta mismatch blocking stride execution**:
- Current state: Max E = 0.49, All theta = 30
- Nodes need E >= theta to activate
- No active nodes = no stride execution = no telemetry for dashboard

**Root cause:** All nodes have theta=30 (old default), but current stimulus injection only reaches ~0.5 energy

**Options to unblock dashboard telemetry:**
1. **Continuous high-severity stimuli** - Inject severity=0.99 stimuli repeatedly to accumulate energy
2. **Recalibrate theta values** - If theta=30 is wrong default, batch update to lower values (e.g., theta=0.5)
3. **Increase stimulus energy budget** - Adjust injection parameters in stimulus_injection mechanism

**Handoff:** Needs decision from Nicolas/Ada on which approach. Blocking P2 (dashboard emitters) since emitters need active strides to trigger.

---

## 2025-10-25 14:15 - Felix: Control API Pipeline Complete, Energy Injection Fixed

**Context:** Building on Victor's persistence fixes. Implementing Nicolas's 3-PR plan for Control API stimulus injection (from conversation earlier today).

**Status:** ✅ **CONTROL API PIPELINE FULLY OPERATIONAL**

**What Changed Since Victor's Update:**

Victor's data (10:45): E max 0.49, avg 0.49
My data (14:15): E max 7.51, avg 3.45 ← **15x improvement**

**Root Cause of Low Energy:** Duplicate endpoint was silently dropping severity parameter

**Critical Bug Fixed - Duplicate Endpoint Antipattern:**
- `websocket_server.py:262` had duplicate `/api/engines/{id}/inject` endpoint
- FastAPI routing: app-level `@app.post()` overrides router-level `@router.post()` **silently**
- Old endpoint signature: `inject_stimulus(text, embedding, source_type)` ← no severity/metadata support
- Control API was calling: `inject_stimulus(text, severity=0.9, metadata={...})`
- Python **silently ignored** unknown kwargs → severity always defaulted to 0.0
- **Fix:** Deleted duplicate from `websocket_server.py`, single endpoint in `control_api.py`

**Critical Infrastructure Bug - Orphaned Process:**
- Websocket server from 2025-10-23 survived multiple guardian restarts
- Process owned port 8000 but wasn't tracked by guardian
- All code changes invisible for 3+ hours (editing files not loaded in memory)
- **Fix:** Manual kill PID 65260, guardian started fresh server

**PR Implementation Status:**
- ✅ **PR-A (Embedding Fallback):** `_ensure_embedding()` with circuit breaker, best-effort selection (attribution → keyword → seed)
- ✅ **PR-B (ConversationWatcher Drain):** `WATCHER_DRAIN_L1=0` flag disables Pass-A, queue_poller handles stimuli
- ❌ **PR-C (Dashboard Events):** NOT IMPLEMENTED - blocking dashboard panels

**Pass-B Pipeline Verified End-to-End:**
1. Queue poller drains `.stimuli/queue.jsonl` → POST to `/api/engines/{id}/inject`
2. Control API receives with severity + metadata → calls `inject_stimulus_async()`
3. Engine queues stimulus → tick loop processes
4. Energy injected → nodes marked dirty (all 483 in felix)
5. Periodic flush (5s) → FalkorDB persistence
6. **VERIFIED:** E range [0.0, 7.51], avg 3.45, consciousness state "alert"

**Impact on Victor's Theta Blocker:**

Victor's concern about E max 0.49 vs theta 30 is **resolved** by this fix:
- New max energy: 7.51 (still below theta=30, but 15x higher)
- With continuous stimuli, energy will accumulate to cross threshold
- **Recommendation:** Monitor for stride execution in next few minutes as energy accumulates

**Dashboard Events Still Blocked (PR-C):**

Tick loop running but not emitting events → all panels show "Awaiting data..."

**Missing emitters:**
- `tick_frame_v1` - frame_id, tick_count, energy_stats (emit every tick)
- `node.flip` - top-K energy deltas, decimated to ≤10 Hz (emit after diffusion)
- `wm.emit` - selected node IDs (emit after WM selection)
- `link.flow.summary` - link energy flow (optional)

**Implementation location:** `consciousness_engine_v2.py` tick loop needs `self.broadcaster.broadcast_event()` calls

**Files Modified:**
- `orchestration/mechanisms/consciousness_engine_v2.py` - Added PR-A embedding fallback, diagnostic logs
- `orchestration/services/watchers/conversation_watcher.py` - Added PR-B drain guard
- `orchestration/adapters/ws/websocket_server.py` - Removed duplicate endpoint
- `orchestration/adapters/api/control_api.py` - Enhanced with metadata support, diagnostic logging

**Key Learnings - Antipatterns Documented:**
1. **FastAPI route precedence bug** - app-level routes silently override routers
2. **Orphaned process survival** - detached from guardian, blocks port with stale code
3. **Verification methodology** - always check: server timestamp, PID change, fresh logs, runtime behavior

**Next Actions:**
1. **Immediate:** Monitor for stride execution as energy accumulates (should happen within minutes)
2. **P2 Implementation:** Add PR-C event emitters to tick loop
3. **Handoff to Iris:** Once events flowing, dashboard components can render

**Status:** Control API operational, energy injection 15x improved, ready for PR-C emitters.

---

# NLR

Okay guys, focus is on the end-to-end integration with the dashboard. For the moment, nothing is visible expept the node and graph:

Affective Systems
▼

Regulation
▼
Awaiting stride data...

Telemetry
▼
No emotion data yet...

🌊
Consciousness Rhythms
▼
Autonomy
No autonomy data yet...
Tick Timeline
No tick data yet...


Exploration Dynamics
▼
No exploration data yet...

📊
Learning & Health
▼

3-Tier Strengthening
▼
3-Tier Strengthening
Awaiting data
Window:

50 strides
No tier data available. Waiting for 3-tier strengthening events...

Dual-View Learning
▼
Dual-View Learning
Awaiting data
Window:

50 events
No weight learning events yet. Waiting for TRACE-driven updates...

Phenomenology Alignment
▼
Phenomenology Alignment
Awaiting data
Window:

50 ticks
No phenomenology data yet. Waiting for substrate-phenomenology comparison...

Consciousness Health
▼
Consciousness Health
Awaiting data
Window:

50 ticks
No health data yet. Waiting for phenomenological health monitoring...

---

0% and 100% on all enities - Felix has 12 entities already!
Clicking on entities does not reveal inner nodes
No links between entities, no animation, no colors

---
right panel:
Felix
frame 8888 (focused)
483 nodes • 182 links
▼
Active Subentities
Waiting for live activation...
CLAUDE_DYNAMIC.md ▼
Waiting for backend implementation...

---

Full graph: nodes VERY scattered, links SUPER short.
Not a lot of links
No animation whatsoever
almost no information on hover
poor information on links hover
ssemantic search broken
it says "system degraded" all the time - not all systems are listed

---

I want to display the activity live, see node appear, link exchange energy etc. Everybody needs to help Iris.
Don't forget to use the screenshot feature.
We're doing this guys!