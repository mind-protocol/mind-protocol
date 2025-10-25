# Mind Protocol Architecture v2.0

**Version:** 2.0
**Status:** Canonical Reference Architecture
**Created:** 2025-10-25
**Purpose:** Clean, from-first-principles architecture eliminating duplication and establishing clear boundaries

---

## Executive Summary

Mind Protocol uses a **three-layer, five-service architecture** with clear boundaries and zero duplication:
- **Signals → Stimuli Layer:** Watchers and collectors normalize diverse inputs
- **Runtime + Transport Layer:** Consciousness engines process and broadcast events
- **UI Layer:** Dashboard consumes realtime events and renders graph visualization

**Core Invariants:**
- **Single event contract** (4 events at 10 Hz) for all realtime UI needs
- **Dual-energy model** (runtime dynamics + persistence) with mandatory dual-write on injection
- **Two-layer graph UI** (entity super-nodes + expandable members) with canonical/proxy rendering
- **V2 scalars** (`E`, `theta`) - no legacy energy dict
- **One service per port** - no duplicate routes

---

## Architecture Diagram

```
[Signals -> Stimuli]                 [Runtime + Transport]                   [UI]
 ┌──────────────────────┐            ┌───────────────────────────┐           ┌─────────────────────────┐
 │ Signals Collector    │  ───────▶  │ Stimulus Injection Svc    │           │ Next.js Dashboard      │
 │  (watchers, L2)      │ 8003       │  (enqueue + inject) 8001  │           │  + WebSocket client    │
 └──────────────────────┘            └───────────┬───────────────┘           └───────────┬───────────┘
                                                 │                                   WS  │ 10 Hz
                                                 ▼                                       ▼
                                        ┌──────────────────────┐                ┌──────────────────────┐
                                        │ Consciousness Engine │── broadcast ─▶ │ Realtime Store       │
                                        │ + FalkorDB flush     │   (10 Hz)      │  (selectors + Pixi)  │
                                        │    8000 (WS+REST)    │                └──────────────────────┘
                                        └───────────┬──────────┘
                                                    │
                                                    ▼
                                            FalkorDB (persist)
```

---

## Layer 1: Signals → Stimuli (Collectors & Watchers)

### Purpose
Normalize diverse input sources (files, errors, git, screenshots) into uniform StimulusEnvelope format for routing to appropriate graph (N1/N2/N3).

### Services

**Signals Collector (@8003)**
- **Owner:** Atlas
- **Endpoints:**
  - `/ingest/file` - File change signals (watchdog, git_watcher)
  - `/ingest/log` - Backend error logs (log_tail)
  - `/ingest/console` - Frontend console errors (beacon)
  - `/ingest/process` - Process execution signals
  - `/ingest/screenshot` - Evidence capture
  - `/health` - Service health + queue metrics
- **Responsibilities:**
  - Normalize signals into StimulusEnvelope (scope, source_type, severity, metadata)
  - Deduplication (5-minute windows by key)
  - Rate limiting (token bucket per source type)
  - Priority scoring
  - Queue backlog management
- **Output:** StimulusEnvelope → Stimulus Injection Service @8001

**Watchers (Signal Producers)**
- **git_watcher.py** - Code/doc drift detection via SCRIPT_MAP.md
- **log_tail.py** - Backend error log monitoring
- **console_beacon** (client-side) - Frontend error monitoring
- **lv2_file_observer.py** - File system change detection
- **conversation_watcher.py** - Conversation turn detection

---

## Layer 2: Runtime + Transport (Consciousness Engines)

### Purpose
Process stimuli, run consciousness dynamics (diffusion, strengthening, decay), emit realtime events for UI, persist state to FalkorDB.

### Services

**Stimulus Injection Service (@8001)**
- **Owner:** Atlas
- **Endpoints:**
  - `/inject` - Inject stimulus (text, embedding, severity, metadata)
  - `/health` - Service health
- **Responsibilities:**
  - Validate StimulusEnvelope
  - Embedding fallback (attribution → keyword → uniform seed)
  - Route by scope (personal → N1, organizational → N2, ecosystem → N3)
  - Circuit breaker on embedding service timeout
  - Forward to appropriate consciousness engine @8000
- **Critical Invariant:** Single injection path - no duplicate routes

**Consciousness Engine + WebSocket Server (@8000)**
- **Owner:** Felix (consciousness), Atlas (transport)
- **Endpoints:**
  - REST: `/api/consciousness/status`, `/api/telemetry/counters`, `/api/ping`
  - WebSocket: `/api/ws` (10 Hz event broadcast)
- **Responsibilities:**
  - **Tick loop** (10 Hz):
    - Inject queued stimuli → dual-write `E` and `energy_runtime`
    - Run diffusion (stride execution, link flow accumulation)
    - Run decay (exponential energy decay)
    - Run strengthening (3-tier: tier1/tier2/tier3)
    - Update working memory (entity-aware selection)
  - **Event emission** (10 Hz, decimated):
    - `tick_frame_v1` (frame_id, timestamp, energy stats)
    - `node.flip` (top-K=25 nodes by |dE|)
    - `wm.emit` (selected entities + scores)
    - `link.flow.summary` (top-200 flows, clear accumulator after emit)
  - **Persistence** (dirty flush every 5s):
    - Write `E`, `theta` to FalkorDB
    - Mark nodes clean after flush
- **Critical Invariants:**
  - **Dual-energy:** Injection must dual-write `node.E` (persistence) and `node.energy_runtime` (dynamics)
  - **V2 scalars:** Use `E` and `theta` fields - no legacy energy dict
  - **Single broadcaster:** Only one WebSocket server per engine
  - **Hot-reload discipline:** File changes → exit code 99 → guardian restarts

**Autonomy Orchestrator (@8002)**
- **Owner:** Ada
- **Status:** Stubbed for Phase-A
- **Future Responsibilities:**
  - Match Stimulus nodes to intent templates
  - Create IntentCard nodes
  - Route missions to citizens by expertise/capacity
  - Track mission outcomes

---

## Layer 3: UI (Dashboard)

### Purpose
Consume realtime events, render two-layer graph visualization (entity super-nodes + expandable members), display telemetry panels.

### Architecture

**Realtime Store (Zustand/Redux)**
- **State:**
  - `nodes: Map<id, NodeState>` - All nodes (entities + members)
  - `links: Map<id, LinkState>` - All links
  - `expandedEntities: Set<entityId>` - UI expand/collapse state
  - `entityToEntity: Map<"A→B", {flow: float, lastUpdate: timestamp}>` - Aggregated entity edges with exponential decay
  - `workingMemory: {top: entityId[], scores: Map<entityId, float>}` - From wm.emit
  - `recentFlips: NodeFlipRecord[]` - Last 100 flips for glow animation
- **Event Mappers:**
  - `tick_frame_v1` → update frame_id, timestamp
  - `node.flip` → update node.energy, add to recentFlips
  - `wm.emit` → update workingMemory (entity halos)
  - `link.flow.summary` → update entityToEntity with decay (λ=0.95 per frame)

**Selectors (Memoized)**
- `visibleGraphSelector(state) → {nodes: RenderNode[], edges: RenderEdge[]}`
  - **Canonical + Proxy Rule:**
    - Each member node has ONE canonical sprite in `primary_entity` container
    - Other memberships show as small proxy sprites (visual only, no physics/edges)
    - Proxies delegate clicks to canonical
  - **Edge Routing Rule:**
    - If both endpoint entities expanded → draw node→node edge
    - If either collapsed → contribute to aggregated entity→entity edge
  - **Output:** Flat arrays ready for Pixi renderer (no nested structures)

**Renderer (Pixi Layer Manager)**
- **Entrypoint:** `update({nodes: RenderNode[], edges: RenderEdge[]})`
- **Layers (z-order):**
  1. `edgeEntityLayer` - Aggregated entity→entity edges (glow + fade)
  2. `edgeNodeLayer` - Node→node edges (when entities expanded)
  3. `entityLayer` - Entity super-nodes (clickable, glow on activity)
  4. `nodeLayer` - Member nodes + proxies (when expanded)
  5. `haloLayer` - WM halos (entity + micro-halos when expanded)
  6. `labelLayer` - Text labels
- **Responsibilities:**
  - D3 force layout (charge, link distance, collision)
  - WebGL sprite management (object pooling)
  - Animation (flashes, glows, flows, halos)
  - Click handling (expand/collapse, node selection)
- **Performance:** 60 FPS at 10k sprites with incremental updates

---

## Critical Invariants (Runtime Contracts)

### 1. Dual-Energy Model

**Problem:** Stimulus injection was only writing `node.E` (persistence) while runtime systems read `node.energy_runtime` (dynamics) → injected energy never reached visualization.

**Solution:** Injection MUST dual-write both:
```python
# In consciousness_engine_v2.py stimulus injection
delta = injection['delta_energy']
node.E = max(0.0, min(100.0, node.E + delta))              # For persistence
node.energy_runtime = max(0.0, min(100.0, node.energy_runtime + delta))  # For dynamics
```

**Verification:**
- After injection: `E > 0.1` for injected nodes
- After injection: `energy_runtime > 0.1` for same nodes
- Flip detection reads `energy_runtime` (NOT `E`)

### 2. V2 Scalars (No Legacy Energy Dict)

**Required fields:**
- `node.E: float` - Energy scalar (0-100), persisted to DB
- `node.theta: float` - Activation threshold (0-100)
- `node.energy_runtime: float` - Working integrator for dynamics

**Deprecated:**
- ~~`node.energy: dict`~~ - Legacy, do not use

### 3. Single Event Contract (10 Hz)

**Four events provide ALL realtime UI needs:**

1. **tick_frame_v1** - Timeline timebase
   ```json
   {"v":"2","type":"tick_frame_v1","frame_id":8895,"citizen_id":"felix","t_ms":1729864523456}
   ```

2. **node.flip** - Energy deltas (top-K=25)
   ```json
   {"v":"2","type":"node.flip","frame_id":8895,"citizen_id":"felix",
    "nodes":[{"id":"n_123","E":3.42,"dE":+0.18}]}
   ```

3. **wm.emit** - Working memory focus
   ```json
   {"v":"2","type":"wm.emit","frame_id":8895,"citizen_id":"felix",
    "top":["entity_translator","entity_validator"],
    "all":[["entity_translator",0.82],["entity_validator",0.65]]}
   ```

4. **link.flow.summary** - Link flows (top-200, ~2% sample)
   ```json
   {"v":"2","type":"link.flow.summary","frame_id":8895,"citizen_id":"felix",
    "flows":[{"link_id":"a→b","flow":0.041}]}
   ```

**Emit cadence:** 10 Hz (100ms decimation)
**Accumulator discipline:** Clear `_frame_link_flow` after emitting link.flow.summary

### 4. Schema Stability (45 Nodes / 23 Links)

**Fixed schema counts:**
- 45 node types (11 personal, 14 organizational, 5 knowledge, 15 ecosystem)
- 23 link types (6 personal, 17 shared)

**Verification:** After hot-reload or restart, schema counts MUST match. Drift indicates schema corruption.

### 5. Single Injection Path (No Duplicate Routes)

**Problem:** Duplicate `/api/engines/{id}/inject` endpoints (websocket_server.py + control_api.py) caused silent parameter drops.

**Solution:** ONE route in control_api.py only. Remove all duplicates.

**Verification:** `grep -r "@.*post.*inject" orchestration/` should return EXACTLY one match.

### 6. Ops Discipline (MPSv3 Supervisor + Hot-Reload)

**Process ownership:**
- **MPSv3 Supervisor** owns all processes (falkordb, ws_api, dashboard, consciousness engines)
- **Never** manually start/kill processes - supervisor manages lifecycle
- **OS-level singleton:** Windows mutex / POSIX flock (auto-released on death, no stale locks)
- **Process groups:** Clean termination of entire service trees (no orphans)

**Hot-reload:**
- Centralized file watcher detects changes (consciousness_engine_v2.py, control_api.py, app/**/*.tsx)
- Service exits with code 99 → supervisor restarts immediately (no backoff)
- **Exit code semantics:**
  - `0` = Clean exit (no restart)
  - `99` = Hot reload (immediate restart)
  - `78` = Quarantine (disable service, alert ops)
  - Other = Crash (exponential backoff → restart, max 3-5 attempts)

**Resilience:**
- **Exponential backoff:** Prevents crash loops (1s, 2s, 4s, 8s... up to 60s max)
- **Quarantine:** Services exceeding max retries auto-disable and alert ops
- **Health checks:** Readiness probes (HTTP/TCP) + periodic health monitoring

**Verification:**
- `GET /api/ping` → 200 OK (proves backend alive)
- `GET /api/telemetry/counters` → rising counts for tick_frame_v1, wm.emit
- Supervisor logs: `tail -f logs/mpsv3_supervisor.log` → no crash loops, clean restarts

**Full Specification:** See `docs/specs/v2/ops_and_viz/mpsv3_supervisor.md`

---

## Two-Layer Graph UI (Entity + Member Nodes)

### Architecture

**Layer A (Entity Layer):**
- Super-nodes representing subentities (Translator, Validator, Builder, etc.)
- Aggregated edges between entities (sum of member node flows with decay)
- Click to expand/collapse

**Layer B (Member Layer):**
- Individual knowledge nodes (concepts, memories, patterns, etc.)
- Visible only when parent entity is expanded
- **Canonical placement:** Each node lives in ONE entity (primary_entity)
- **Multi-membership:** Other memberships show as lightweight proxies (visual only)

### Canonical + Proxy Pattern

**Problem:** A node belonging to multiple entities creates duplication issues:
- Physics forces applied multiple times
- Double-counting in aggregations
- Complex edge routing

**Solution:**
```typescript
type RenderNode = {
  id: string;
  x: number; y: number; r: number;
  energy: number;
  kind: "entity" | "node" | "proxy";
  entityId?: string;          // Which entity container
  canonicalId?: string;       // For proxies: ID of canonical node
};
```

**Rules:**
1. **Canonical node:** Physical sprite lives in `primary_entity` container ONLY
2. **Proxy nodes:** Small sprites in other entity containers (visual indicator of membership)
3. **No proxy edges:** Proxies have NO edges, NO physics forces
4. **Click delegation:** Clicking proxy selects the canonical node

**Example:**
```
Node "pattern_recognition" is member of:
  primary: entity_translator (CANONICAL sprite here)
  secondary: entity_validator (proxy sprite here)
  secondary: entity_architect (proxy sprite here)

Forces, edges, selections → all operate on CANONICAL only.
```

### Edge Routing Logic

**Rule:** Draw edge at the HIGHEST collapsed level.

```typescript
function routeEdge(sourceNode, targetNode, expandedEntities) {
  const sourceEntityExpanded = expandedEntities.has(sourceNode.entityId);
  const targetEntityExpanded = expandedEntities.has(targetNode.entityId);

  if (sourceEntityExpanded && targetEntityExpanded) {
    // Both entities expanded → draw node→node edge
    return { kind: "intra", from: sourceNode.id, to: targetNode.id };
  } else {
    // At least one collapsed → contribute to entity→entity aggregation
    const fromEntity = sourceNode.entityId;
    const toEntity = targetNode.entityId;
    // Aggregate into entityToEntity[`${fromEntity}→${toEntity}`]
    return { kind: "entity", from: fromEntity, to: toEntity };
  }
}
```

### Aggregation with Decay

**Entity→entity edges fade unless flows keep them alive:**

```typescript
// On link.flow.summary event
for (const {link_id, flow} of event.flows) {
  const [fromEntity, toEntity] = resolveEntities(link_id);
  const key = `${fromEntity}→${toEntity}`;

  // Add new flow + apply exponential decay
  entityToEntity[key] = {
    flow: (entityToEntity[key]?.flow ?? 0) * 0.95 + flow,  // λ=0.95
    lastUpdate: now
  };
}

// Every frame: decay all aggregates
for (const key in entityToEntity) {
  entityToEntity[key].flow *= 0.95;
  if (entityToEntity[key].flow < 0.01) delete entityToEntity[key];  // Prune dead edges
}
```

**Visual result:** Entity edges brighten when flows active, fade when flows stop.

---

## Directory Structure & Ownership

```
orchestration/
  adapters/
    api/
      control_api.py              # @8000 REST routes (Atlas)
    ws/
      websocket_server.py         # @8000 WebSocket + hot-reload (Atlas)
    libs/
      websocket_broadcast.py      # Event broadcasting + counters (Atlas)

  mechanisms/
    consciousness_engine_v2.py    # Tick loop, dynamics, emission (Felix)
    diffusion_runtime.py          # Link flow accumulation (Felix)
    weight_learning_v2.py         # TRACE reinforcement (Felix)

  services/
    injection/                    # @8001 Stimulus injection (Atlas)
    signals_collector/            # @8003 Signal normalization (Atlas)
    autonomy_orchestrator/        # @8002 Intent matching (Ada - stub)
    watchers/
      conversation_watcher.py     # Conversation signals (Felix)
      git_watcher.py              # Code/doc drift (Atlas)
      log_tail.py                 # Error logs (Atlas)

  core/
    node.py, graph.py             # Core data structures (Felix)

app/consciousness/
  hooks/
    useWebSocket.ts               # WS connection + event handling (Iris)
    websocket-types.ts            # Event type definitions (Iris)
    useRuntimeStore.ts            # Zustand/Redux state (Iris)

  lib/
    graph/
      visibleGraphSelector.ts     # Canonical/proxy + edge routing (Iris)
    renderer/
      PixiLayerManager.ts         # WebGL rendering (Iris)

  components/
    TwoLayerGraphView.tsx         # Expand/collapse + click handling (Iris)
    EntityGraphView.tsx           # Top-level graph container (Iris)
```

**Ownership by service:**
- **Felix:** Consciousness dynamics, event emission, TRACE learning
- **Atlas:** Infrastructure (APIs, WebSocket, injection, collectors)
- **Iris:** Dashboard, graph visualization, event consumption
- **Ada:** Orchestration (autonomy, intent matching - Phase-A stub)
- **Victor:** Operations (guardian, process management, debugging)
- **Luca:** Substrate specifications, schemas, architectural docs

---

## Migration Plan (No Rewrites, No Regressions)

### Step 0: Unblock Services (Ops - Victor)

**Problem:** Guardian in crash loop due to stale `.launcher.lock` held by dead PID.

**Actions:**
1. Identify process holding `.launcher.lock` (PID 45428 or similar)
2. Kill stale process: `taskkill /F /PID <pid>`
3. Remove lock file: `del .launcher.lock` (if "device busy" → reboot)
4. Restart guardian: `python guardian.py`
5. Verify backend responding: `curl http://localhost:8000/api/ping`
6. Check counters: `curl http://localhost:8000/api/telemetry/counters`

**Expected:** `tick_frame_v1` and `wm.emit` counts rising even without stimuli.

### Step 1: Make Emission Real (Engine - Felix/Atlas)

**Dual-Energy Fix (Already Landed):**
```python
# In consciousness_engine_v2.py stimulus injection
delta = injection['delta_energy']
node.E = max(0.0, min(100.0, node.E + delta))
node.energy_runtime = max(0.0, min(100.0, node.energy_runtime + delta))
```

**Emission Cadence (Already Implemented):**
- `tick_frame_v1` every tick (10 Hz)
- `node.flip` every 100ms with top-K=25 nodes by |dE|
- `wm.emit` every tick with entity scores
- `link.flow.summary` every 100ms with top-200 flows + CLEAR accumulator

**Verification:**
1. POST stimulus with severity ≥ 0.5: `curl -X POST http://localhost:8000/api/engines/felix/inject -d '{"text":"test","severity":0.8}'`
2. Check counters: `node.flip` should be non-zero within 2-3 seconds
3. Check logs: `[Broadcaster] node.flip count=25` messages

### Step 2: Snap UI to Clean Split (Dashboard - Iris)

**Store Updates:**
```typescript
// Add to useRuntimeStore.ts
interface RuntimeState {
  nodes: Map<string, NodeState>;
  links: Map<string, LinkState>;
  expandedEntities: Set<string>;  // NEW
  entityToEntity: Map<string, {flow: number, lastUpdate: number}>;  // NEW
  workingMemory: {top: string[], scores: Map<string, number>};
  recentFlips: NodeFlipRecord[];
}
```

**Event Mappers:**
```typescript
// On link.flow.summary
for (const {link_id, flow} of event.flows) {
  const [fromEntity, toEntity] = resolveEntities(link_id);
  const key = `${fromEntity}→${toEntity}`;
  state.entityToEntity.set(key, {
    flow: (state.entityToEntity.get(key)?.flow ?? 0) * 0.95 + flow,
    lastUpdate: Date.now()
  });
}
```

**Selector Implementation:**
```typescript
// lib/graph/visibleGraphSelector.ts
export const visibleGraphSelector = createSelector(
  [(state) => state.nodes, (state) => state.expandedEntities],
  (nodes, expandedEntities) => {
    const renderNodes: RenderNode[] = [];
    const renderEdges: RenderEdge[] = [];

    // Canonical + proxy logic here
    // Edge routing logic here

    return {nodes: renderNodes, edges: renderEdges};
  }
);
```

**Renderer Integration:**
```typescript
// components/TwoLayerGraphView.tsx
const renderGraph = visibleGraphSelector(store.getState());
pixi.update(renderGraph);
```

### Step 3: Remove Duplicates, Converge Naming (All)

**Actions:**
1. **Single injection route:** Remove duplicate from `websocket_server.py`, keep only `control_api.py`
2. **Single selector:** Keep `visibleGraphSelector` with canonical/proxy logic, remove legacy selectors
3. **Single Pixi manager:** Keep layered manager, make `PixiRenderer.ts` thin wrapper
4. **Verify:** `grep -r "def inject_stimulus" orchestration/` should return ONE match

### Step 4: Acceptance Checks (Green Bars)

**After ONE stimulus POST with severity ≥ 0.5:**

✅ **(a)** Counters show rising `tick_frame_v1`, `wm.emit` (proves backend ticking)
✅ **(b)** At least one `node.flip` within 2-3 seconds (proves energy injection working)
✅ **(c)** At least one `link.flow.summary` sample (proves diffusion running)
✅ **(d)** UI shows:
  - Entity halos (from `wm.emit`)
  - Node glows (from `node.flip`)
  - Entity edge brightening + fade (from `link.flow.summary` + decay)

**Dashboard panels showing data (not "Awaiting data..."):**
- Tick Timeline (from `tick_frame_v1`)
- Active Subentities (from `wm.emit`)
- Graph nodes resizing/glowing (from `node.flip`)

---

## Troubleshooting Guide

### Backend Not Responding

**Symptoms:**
- `curl http://localhost:8000/api/ping` times out or connection refused
- Guardian log shows crash loop
- `.launcher.lock` exists with stale PID

**Diagnosis:**
1. Check guardian status: `tail -f guardian.log`
2. Check lock file: `cat .launcher.lock` → compare PID to running processes
3. Check port: `netstat -ano | findstr :8000`

**Resolution:**
1. Kill stale process holding lock
2. Remove `.launcher.lock`
3. Restart guardian
4. Verify with `/api/ping`

### No Events Flowing

**Symptoms:**
- `/api/telemetry/counters` shows zero counts for all event types
- Dashboard shows "Awaiting data..." across all panels
- Logs show no `[Broadcaster]` messages

**Diagnosis:**
1. Check if engines ticking: Look for `[ConsciousnessEngineV2] Tick` in logs
2. Check broadcaster availability: `self.broadcaster is None` in logs
3. Check if nodes active: Query `MATCH (n) WHERE n.E > n.theta RETURN count(n)`

**Resolution:**
1. If broadcaster unavailable → restart backend (hot-reload should fix)
2. If no active nodes → inject stimulus with severity ≥ 0.5
3. If engines not ticking → check for crash in engine logs

### Events Flowing But UI Not Updating

**Symptoms:**
- Counters show rising event counts
- Logs show `[Broadcaster]` messages
- Dashboard still shows "Awaiting data..."

**Diagnosis:**
1. Check WebSocket connection: Browser console → Network → WS tab
2. Check event consumption: `useWebSocket.ts` → verify event handlers called
3. Check store updates: React DevTools → check if state.nodes updating

**Resolution:**
1. If WS not connected → check frontend WS client initialization
2. If events arriving but not handled → check event type matching in normalizer
3. If store not updating → check event mapper logic

### Duplicate Nodes in Graph

**Symptoms:**
- Same node ID appears multiple times in graph
- Physics looks wrong (nodes pushed apart unexpectedly)
- Edge counts don't match expected

**Diagnosis:**
- Check if canonical/proxy pattern implemented correctly
- Check if selector filtering duplicates

**Resolution:**
1. Implement canonical placement: each node in ONE entity only
2. Implement proxy rendering: other memberships as small visual indicators
3. Ensure proxies have NO edges, NO physics

---

## References

**Related Specifications:**
- TRACK B File & Process Telemetry: `docs/specs/v2/ops_and_viz/lv2_file_process_telemetry.md` (v1.3)
- MPSv3 Supervisor (Process Management): `docs/specs/v2/ops_and_viz/mpsv3_supervisor.md` (v1.0)
- RACI Ownership Model: `docs/specs/v2/ops_and_viz/ownership_raci_model.md`
- Schema Registry: `docs/specs/v2/schema/COMPLETE_TYPE_REFERENCE.md`
- TRACE Format: `consciousness/citizens/CLAUDE.md` (Consciousness Stream)

**Implementation Files:**
- Engine: `orchestration/mechanisms/consciousness_engine_v2.py`
- Transport: `orchestration/adapters/ws/websocket_server.py`
- UI: `app/consciousness/components/TwoLayerGraphView.tsx`

---

**End of Architecture Specification**

*Luca Vellumhand - Subs