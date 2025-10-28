# Pure Membrane Architecture - No API, Only Injection & Broadcast

**Updated:** 2025-10-27
**Status:** Normative (supersedes hybrid REST+WS approach)

**Core principle:** The membrane is the ONLY control surface. Everything is either:
1. **Inject** - post StimulusEnvelope to influence consciousness
2. **Broadcast** - observe what consciousness emits

No REST. No polling. No snapshots. No pulls.

---

## 0. The Membrane Discipline

**One bus, two verbs, typed envelopes:**

- **Inject**: Anything that wants to *influence* consciousness posts a `StimulusEnvelope` on the bus (WebSocket)
- **Broadcast**: Engines and orchestrators *only* emit deltas/percepts/telemetry on the bus (WebSocket)

**No other channel.** This is exactly how the L1↔L2 membrane is already designed (stimulus in, deltas out) - we're extending it to *everything*, not just cross-level flow.

---

## 1. Context & Pain Points (From Previous Approach)

**What we're fixing:**
- ❌ REST hierarchy endpoints (`/api/ecosystems`) create pull semantics
- ❌ REST snapshot dumps (`/api/graph`) block on heavy FalkorDB queries
- ❌ UI "controls" via REST API (`/api/action/*`) break membrane discipline
- ❌ Tool execution via MCP sprawl explodes token budget
- ❌ Separate ingestion API (`POST /inject`) requires HTTP server
- ❌ Cross-level flow had side channels (not pure membrane)

**What we're achieving:**
- ✅ Pure membrane: inject stimulus OR observe broadcast
- ✅ Zero REST surface (eliminates all pull semantics)
- ✅ UI interactions become stimuli (subject to membrane physics)
- ✅ Tools as membrane participants (offer/request/result)
- ✅ Hierarchy announced, not fetched
- ✅ All hardening inside membrane physics (Pareto/MAD/ledger/κ)

---

## 2. Design Tenets

1. **Pure membrane discipline** - No API hierarchy; everything flows through stimulus injection or event broadcast
2. **Consciousness decides** - Engines are free to ignore/reinterpret ANY stimulus via membrane physics (trust, novelty, fit)
3. **Memory-only warm state** - Live working set in RAM for percepts; no persistence, no replay
4. **Hot restarts, zero downtime** - Services restart individually; resume from live state
5. **Backpressure as stimulus** - UI/observers inject `ui.render.backpressure` to adapt emission
6. **Observe only what was seen** - `percept.frame` carries only what subentity actually perceived (anchors_top + anchors_peripheral)

---

## 3. Target System Overview

```
┌──────────────┐
│  FalkorDB    │ (graph storage only - no queries except bootstrap)
└──────┬───────┘
       │ graph.load() on boot
       ▼
┌──────────────────────────────────────────────────────────┐
│ Consciousness Engine V2 (per citizen)                     │
│ • Loads graph on boot                                     │
│ • Subscribes to membrane.inject                          │
│ • Emits graph.delta.*, percept.frame, membrane.*         │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ WebSocket Bus (/ws)                                       │
│ • Topic: membrane.inject (fan-in)                        │
│ • Topics: graph.*, percept.*, membrane.*, intent.*       │
│           (fan-out - broadcast to all subscribers)       │
└────────────────┬─────────────────────────────────────────┘
                 │
     ┌───────────┴───────────┐
     │                       │
     ▼                       ▼
┌─────────────┐      ┌─────────────┐
│ UI          │      │ Signals     │
│ • Subscribes│      │ Collector   │
│ • Injects   │      │ • Publishes │
│   ui.action │      │   membrane  │
└─────────────┘      │   .inject   │
                     └─────────────┘
```

**Key:** Everything on the bus. No side channels.

---

## 4. Canonical Envelope Formats

### Inject (Everything Writes Via This)

**Type:** `membrane.inject`

**Used by:** Signals Collector, UI interactions, L1/L2 emissions, tool requests, orchestrator missions

```json
{
  "type": "membrane.inject",
  "scope": "organizational",              // or "personal"
  "channel": "ui.action.select_nodes",   // or citizen_file_ops, tool.request, l2_coordination...
  "content": "User selected nodes N7, N23 for focus",
  "features_raw": {
    "novelty": 0.82,
    "uncertainty": 0.25,
    "trust": 0.85,
    "urgency": 0.70,
    "valence": 0.50,
    "scale": 0.80
  },
  "metadata": {
    "origin": "ui" | "external" | "self_observation",
    "origin_chain_depth": 0,
    "origin_chain": [],
    "ttl_frames": 600,
    "dedupe_key": "sha256_16",
    "intent_merge_key": "stable-key",
    "business_impact": "sev2",
    "rate_limit_bucket": "dashboard:console"
  }
}
```

**Envelope fields taken directly from Signals→Stimuli spec.** Transport over WS instead of HTTP.

---

### Broadcast (Everything Reads Via This)

**Types:** All events emitted by engines, membranes, orchestrators

#### Graph Deltas

```json
{
  "type": "graph.delta.node.upsert",
  "citizen_id": "consciousness-infrastructure_mind-protocol_ada",
  "node": {
    "id": "N7",
    "label": "wm:concept",
    "energy": 0.73,
    "coords": [x, y, z],
    "properties": { "name": "substrate_architecture", "confidence": 0.85 }
  },
  "cause": "activation" | "bootstrap" | "structural_update",
  "cursor": 12841,
  "timestamp": "2025-10-27T12:34:56Z"
}
```

```json
{
  "type": "graph.delta.link.upsert",
  "citizen_id": "...",
  "link": {
    "id": "L42",
    "source": "N7",
    "target": "N23",
    "type": "ENABLES",
    "weight": 0.68,
    "properties": { "goal": "architectural_clarity", "energy": 0.8 }
  },
  "cause": "traversal" | "learning" | "bootstrap",
  "cursor": 12842
}
```

#### Percepts (What Subentity Actually Saw)

```json
{
  "type": "percept.frame",
  "entity_id": "subentity_translator",
  "citizen_id": "ada",
  "affect": {
    "valence": 0.6,
    "arousal": 0.7
  },
  "novelty": 0.82,
  "uncertainty": 0.25,
  "goal_match": 0.78,
  "anchors_top": ["N7", "N23", "N15"],        // What's in focus
  "anchors_peripheral": ["N42", "N88"],       // Peripheral vision
  "cursor": 12843,
  "timestamp": "2025-10-27T12:34:57Z"
}
```

**UI renders ONLY these objects.** If a node was physically near but not in `anchors_*`, it wasn't perceived—don't draw it.

#### Working Memory

```json
{
  "type": "wm.emit",
  "citizen_id": "ada",
  "selected_entities": ["subentity_translator", "subentity_architect", "subentity_validator"],
  "capacity": 9,
  "occupancy": 3,
  "cursor": 12844
}
```

#### Membrane Events

```json
{
  "type": "membrane.transfer.up",
  "citizen_id": "felix",
  "organization_id": "mind-protocol",
  "content": "Substrate-native rate limiting via mass accumulation",
  "score": 0.73,
  "event_id": "membrane_up_felix_16234",
  "cursor": 12845
}
```

```json
{
  "type": "membrane.permeability.updated",
  "membrane_id": "L1_felix_to_L2_mind",
  "direction": "up",
  "k_up": 0.78,
  "k_down": 0.92,
  "outcome_score": 0.6,
  "eff_ema": 0.71,
  "cursor": 12846
}
```

```json
{
  "type": "membrane.export.rejected",
  "membrane_id": "...",
  "direction": "up",
  "reason": "pareto_fail" | "mad_fail" | "ledger_block" | "saturation",
  "candidate_novelty": 0.85,
  "candidate_fit": 0.32,
  "cursor": 12847
}
```

#### Tool Events

```json
{
  "type": "tool.offer",
  "tool_id": "github_search",
  "capabilities": ["code_search", "issue_lookup"],
  "cost_estimate": 0.5,
  "safety_level": "safe",
  "cursor": 12848
}
```

```json
{
  "type": "tool.request",
  "request_id": "req_abc123",
  "tool_id": "github_search",
  "goal": "Find implementation of membrane transfer",
  "constraints": { "max_results": 10 },
  "evidence_pointers": ["N7", "N23"],
  "cursor": 12849
}
```

```json
{
  "type": "tool.result",
  "request_id": "req_abc123",
  "tool_id": "github_search",
  "artifacts": [
    { "type": "code_snippet", "url": "...", "content": "..." }
  ],
  "provenance": { "query": "...", "timestamp": "..." },
  "cursor": 12850
}
```

#### Intent/Mission Events

```json
{
  "type": "intent.created",
  "intent_id": "intent_789",
  "assignee": "iris",
  "lane": "incidents",
  "priority": 0.92,
  "description": "Dashboard render performance degraded",
  "cursor": 12851
}
```

```json
{
  "type": "mission.accept",
  "mission_id": "mission_101",
  "citizen_id": "iris",
  "cursor": 12852
}
```

#### Telemetry Events

```json
{
  "type": "signals.rate",
  "bucket": "dashboard:console",
  "rate_per_second": 12.3,
  "dropped_count": 0,
  "cursor": 12853
}
```

```json
{
  "type": "orchestrator.queue.depth",
  "lane": "incidents",
  "depth": 5,
  "oldest_age_seconds": 23,
  "cursor": 12854
}
```

#### Hierarchy Announcements

```json
{
  "type": "hierarchy.snapshot",
  "ecosystems": [
    {
      "slug": "consciousness-infrastructure",
      "name": "Consciousness Infrastructure",
      "organizations": [
        {
          "slug": "mind-protocol",
          "name": "Mind Protocol",
          "citizens": [
            { "id": "ada", "name": "Ada Bridgekeeper", "status": "active" },
            { "id": "felix", "name": "Felix Ironhand", "status": "active" }
          ]
        }
      ]
    }
  ],
  "cursor": 12855,
  "timestamp": "2025-10-27T12:35:00Z"
}
```

**Emitted:** On boot, on changes, every 30 seconds (human-time frequency fine)
**Frontend:** Caches latest broadcast; late joiners wait for next emission

---

## 5. Component Designs (Pure Membrane)

### 5.1 WebSocket Bus

**Location:** `orchestration/adapters/ws/membrane_bus.py`

**Topics:**
- `membrane.inject` (fan-in - single topic, all injections)
- `graph.*` (fan-out - all graph deltas)
- `percept.*` (fan-out - all percept frames)
- `membrane.*` (fan-out - all membrane events)
- `wm.*` (fan-out - working memory)
- `intent.*` (fan-out - orchestrator events)
- `tool.*` (fan-out - tool lifecycle)
- `signals.*` (fan-out - telemetry)
- `hierarchy.*` (fan-out - hierarchy announcements)

**Responsibilities:**
- Accept WebSocket connections
- Route `membrane.inject` messages to Stimulus Injector
- Broadcast all other message types to subscribers
- Handle subscription filters (ecosystem/org/citizen)
- Heartbeat every 10s

**Implementation sketch:**
```python
class MembraneBus:
    def __init__(self):
        self.subscribers = defaultdict(set)  # topic -> set of websockets
        self.injector_queue = Queue()        # membrane.inject fan-in

    async def handle_client(self, websocket):
        """Handle WebSocket connection."""
        filters = await self._handshake(websocket)

        # Subscribe to broadcast topics
        for topic in self._get_topics(filters):
            self.subscribers[topic].add(websocket)

        try:
            async for message in websocket:
                await self._handle_message(message, websocket)
        finally:
            self._unsubscribe(websocket)

    async def _handle_message(self, message, websocket):
        """Route message based on type."""
        msg = json.loads(message)

        if msg["type"] == "membrane.inject":
            # Fan-in: route to injector
            await self.injector_queue.put(msg)
        elif msg["type"] == "subscribe":
            # Update subscription filters
            await self._update_subscription(websocket, msg)
        elif msg["type"].startswith("ui.render."):
            # Backpressure signals also injected
            await self.injector_queue.put(msg)

    async def broadcast(self, message):
        """Fan-out: broadcast to all subscribers."""
        msg_type = message["type"]
        topic_prefix = msg_type.split(".")[0]  # graph, percept, membrane, etc.

        # Get subscribers for this topic
        subscribers = self.subscribers.get(topic_prefix, set())

        # Apply filters (ecosystem/org/citizen)
        filtered = self._apply_filters(subscribers, message)

        # Broadcast
        for ws in filtered:
            await ws.send(json.dumps(message))
```

---

### 5.2 Stimulus Injector (Bus Consumer)

**Location:** `orchestration/mechanisms/stimulus_injection.py` (modified)

**Changes:**
- **Before:** HTTP server accepting `POST /inject`
- **After:** Bus subscriber consuming `membrane.inject`

**Implementation:**
```python
class StimulusInjector:
    def __init__(self, bus: MembraneBus):
        self.bus = bus
        self.engines = {}  # citizen_id -> engine instance

    async def run(self):
        """Consume membrane.inject from bus."""
        while True:
            envelope = await self.bus.injector_queue.get()
            await self._process_envelope(envelope)

    async def _process_envelope(self, envelope):
        """Route stimulus to appropriate engine."""
        scope = envelope["scope"]

        if scope == "personal":
            # Extract citizen from channel or metadata
            citizen_id = self._extract_citizen(envelope)
            engine = self.engines.get(citizen_id)
            if engine:
                await engine.inject_stimulus(envelope)

        elif scope == "organizational":
            # Route to L2 (organization consciousness)
            org_id = self._extract_org(envelope)
            l2_engine = self.engines.get(f"l2_{org_id}")
            if l2_engine:
                await l2_engine.inject_stimulus(envelope)
```

**Same routing rules as before.** Same integrator physics. Just different transport.

---

### 5.3 Consciousness Engine V2 (Broadcast Only)

**Location:** `orchestration/mechanisms/consciousness_engine_v2.py`

**Changes:**
- Subscribe to `membrane.inject` on boot
- Emit ALL events to bus (no side channels)
- Bootstrap emits same delta envelopes as runtime (no synthetic snapshots)

**Event emission:**
```python
class ConsciousnessEngineV2:
    def __init__(self, citizen_id, bus: MembraneBus):
        self.citizen_id = citizen_id
        self.bus = bus
        self.cursor = 0

    async def emit_node_delta(self, node, cause):
        """Emit graph.delta.node.upsert."""
        self.cursor += 1
        await self.bus.broadcast({
            "type": "graph.delta.node.upsert",
            "citizen_id": self.citizen_id,
            "node": node.to_dict(),
            "cause": cause,
            "cursor": self.cursor,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def emit_percept(self, entity_id, affect, novelty, anchors_top, anchors_peripheral):
        """Emit percept.frame - what this subentity saw."""
        self.cursor += 1
        await self.bus.broadcast({
            "type": "percept.frame",
            "entity_id": entity_id,
            "citizen_id": self.citizen_id,
            "affect": affect,
            "novelty": novelty,
            "anchors_top": anchors_top,
            "anchors_peripheral": anchors_peripheral,
            "cursor": self.cursor,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def emit_membrane_transfer(self, direction, content, score):
        """Emit membrane.transfer.up/down."""
        self.cursor += 1
        await self.bus.broadcast({
            "type": f"membrane.transfer.{direction}",
            "citizen_id": self.citizen_id,
            "content": content,
            "score": score,
            "cursor": self.cursor
        })
```

**Bootstrap:**
```python
async def bootstrap(self):
    """Bootstrap emits same deltas as runtime."""
    # Load graph from FalkorDB
    graph = await self._load_graph()

    # Emit deltas for initial structure (minimal set)
    for node in graph.nodes:
        await self.emit_node_delta(node, cause="bootstrap")

    for link in graph.links:
        await self.emit_link_delta(link, cause="bootstrap")

    # Engine is now hot - future changes emit naturally
```

**No synthetic snapshots. Bootstrap = replay of what would have happened if engine created graph from scratch.**

---

### 5.4 Signals Collector (Bus Publisher)

**Location:** `orchestration/services/watchers/*`

**Changes:**
- **Before:** `POST /inject` to HTTP endpoint
- **After:** Publish `membrane.inject` to bus

**Implementation:**
```python
class SignalsCollector:
    def __init__(self, bus: MembraneBus):
        self.bus = bus
        self.rate_limiters = {}
        self.dedupe_cache = {}

    async def on_file_change(self, path, content):
        """File watcher detected change."""
        # Apply signals bridge logic (dedupe, rate, cooldown)
        envelope = self._create_envelope(
            channel="citizen_file_ops",
            content=f"File changed: {path}",
            features_raw=self._extract_features(content),
            metadata={
                "origin": "external",
                "dedupe_key": self._compute_hash(path, content),
                "rate_limit_bucket": "filesystem:changes"
            }
        )

        # Check rate limit
        if not self._check_rate_limit(envelope):
            return

        # Check dedupe
        if self._is_duplicate(envelope):
            return

        # Publish to bus
        await self.bus.broadcast(envelope)

    def _create_envelope(self, channel, content, features_raw, metadata):
        """Create membrane.inject envelope."""
        return {
            "type": "membrane.inject",
            "scope": "personal",  # or "organizational"
            "channel": channel,
            "content": content,
            "features_raw": features_raw,
            "metadata": metadata
        }
```

**Same envelope fields as Signals→Stimuli spec. Just WS transport instead of HTTP.**

---

### 5.5 Frontend (Pure Observer + Injector)

**Location:** `app/consciousness/hooks/useGraphStream.ts`

**Changes:**
- Read ONLY from bus (subscribe to broadcasts)
- Write ONLY via `membrane.inject` (UI actions become stimuli)
- Render ONLY from `percept.frame` (what was actually seen)

**Implementation:**
```typescript
export function useGraphStream(citizenId: string) {
  const [state, setState] = useState({
    nodes: new Map(),
    links: new Map(),
    percepts: new Map(),
    cursor: 0,
    status: 'connecting'
  });

  useEffect(() => {
    const ws = new WebSocket('/ws');

    ws.onopen = () => {
      // Subscribe
      ws.send(JSON.stringify({
        action: 'subscribe',
        citizen: citizenId
      }));
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.cursor <= state.cursor) {
        return; // Dedupe - already processed
      }

      // Route by type
      switch (msg.type) {
        case 'graph.delta.node.upsert':
          handleNodeDelta(msg);
          break;
        case 'graph.delta.link.upsert':
          handleLinkDelta(msg);
          break;
        case 'percept.frame':
          handlePercept(msg);
          break;
        case 'hierarchy.snapshot':
          handleHierarchy(msg);
          break;
        // ... etc
      }

      setState(prev => ({ ...prev, cursor: msg.cursor }));
    };

    return () => ws.close();
  }, [citizenId]);

  // UI actions become stimuli
  const selectNodes = (nodeIds: string[]) => {
    ws.send(JSON.stringify({
      type: 'membrane.inject',
      scope: 'personal',
      channel: 'ui.action.select_nodes',
      content: `User selected nodes ${nodeIds.join(', ')}`,
      features_raw: {
        novelty: 0.3,
        trust: 1.0,
        urgency: 0.5,
        valence: 0.6
      },
      metadata: {
        origin: 'ui',
        ttl_frames: 300,
        dedupe_key: `select_${nodeIds.join('_')}_${Date.now()}`
      }
    }));
  };

  const focusEntity = (entityId: string) => {
    ws.send(JSON.stringify({
      type: 'membrane.inject',
      scope: 'personal',
      channel: 'ui.action.focus_entity',
      content: `User focused on ${entityId}`,
      features_raw: { novelty: 0.4, trust: 1.0, urgency: 0.7 },
      metadata: { origin: 'ui', ttl_frames: 600 }
    }));
  };

  return { state, selectNodes, focusEntity };
}
```

**Render from percepts:**
```typescript
function renderPercepts(percepts: Map<string, Percept>) {
  for (const [entityId, percept] of percepts) {
    // Render ONLY anchors_top and anchors_peripheral
    const visibleNodes = new Set([
      ...percept.anchors_top,
      ...percept.anchors_peripheral
    ]);

    // If node not in visible set, it wasn't perceived - don't draw
    nodes.forEach(node => {
      if (!visibleNodes.has(node.id)) {
        node.opacity = 0; // Fade out
      } else {
        node.opacity = percept.anchors_top.includes(node.id) ? 1.0 : 0.6;
      }
    });
  }
}
```

---

### 5.6 Tools as Membrane Participants

**Location:** `orchestration/tools/tool_runner.py`

**Pattern:**
1. Tool announces capabilities: `tool.offer`
2. Citizens request execution: `tool.request`
3. Tool publishes results: `tool.result`

**Implementation:**
```python
class ToolRunner:
    def __init__(self, tool_id, bus: MembraneBus):
        self.tool_id = tool_id
        self.bus = bus

    async def run(self):
        """Subscribe to tool.request, emit tool.result."""
        # Announce capabilities
        await self.bus.broadcast({
            "type": "tool.offer",
            "tool_id": self.tool_id,
            "capabilities": ["code_search", "issue_lookup"],
            "cost_estimate": 0.5,
            "safety_level": "safe"
        })

        # Subscribe to requests
        async for msg in self.bus.subscribe("tool.request"):
            if msg["tool_id"] == self.tool_id:
                await self._handle_request(msg)

    async def _handle_request(self, request):
        """Execute tool and emit result."""
        # Do work
        artifacts = await self._search_github(request["goal"])

        # Emit result
        await self.bus.broadcast({
            "type": "tool.result",
            "request_id": request["request_id"],
            "tool_id": self.tool_id,
            "artifacts": artifacts,
            "provenance": { "query": request["goal"], "timestamp": datetime.utcnow().isoformat() }
        })
```

**No MCP registry explosion.** Tools are just membrane participants. Eligibility learned contextually (L1/L2 graph injects relevant tool nodes into CLAUDE.md).

---

### 5.7 Hierarchy Announcer (No Fetch API)

**Location:** `orchestration/adapters/hierarchy_announcer.py`

**Responsibilities:**
- Watch FalkorDB for graph list changes
- Emit `hierarchy.snapshot` on boot, on changes, every 30s

**Implementation:**
```python
class HierarchyAnnouncer:
    def __init__(self, bus: MembraneBus, falkor_client):
        self.bus = bus
        self.falkor = falkor_client
        self.last_snapshot = None

    async def run(self):
        """Announce hierarchy periodically."""
        while True:
            snapshot = await self._build_hierarchy()

            if snapshot != self.last_snapshot:
                await self.bus.broadcast({
                    "type": "hierarchy.snapshot",
                    "ecosystems": snapshot,
                    "timestamp": datetime.utcnow().isoformat()
                })
                self.last_snapshot = snapshot

            await asyncio.sleep(30)  # Human-time frequency

    async def _build_hierarchy(self):
        """Build hierarchy from FalkorDB GRAPH.LIST."""
        graphs = await self.falkor.list_graphs()
        # Parse {ecosystem}_{org}_{citizen} naming
        # Build nested structure
        return ecosystems
```

**Frontend caches latest broadcast. Late joiners wait for next emission (30s max).**

---

## 6. Hardening Inside Membrane Physics

**All gaming resistance implemented as substrate physics, not API controls:**

### 6.1 Pareto Record + MAD Guards

**Location:** Membrane transfer decision logic (already spec'd in membrane_hardening.md)

- Multi-axis record (novelty × fit × utility × trust)
- MAD-adjusted thresholds (adaptive to noise)
- Prevents novelty spam from triggering exports

**Implementation:** Inside membrane emission logic (not API layer)

### 6.2 Saturation + Refractory

**Location:** Stimulus integrator (consciousness_engine_v2.py)

- Mass accumulation per source
- Refractory period after activation
- Makes spam self-defeating (ΔE drops exponentially)

**Implementation:** Inside integrator physics (already spec'd)

### 6.3 Emission Ledger + Hysteresis

**Location:** Membrane edge properties (MEMBRANE_TO)

- Content hash deduplication
- Cooling period before re-emission (30min)
- Hysteresis gates (entry > exit thresholds)

**Implementation:** Inside membrane state (already spec'd)

### 6.4 Outcome-Weighted Permeability

**Location:** Membrane learning (membrane_hardening.md)

- κ_up/κ_down learn from outcomes
- TRACE seats, Δρ, mission success
- Spammers get low κ automatically

**Implementation:** Inside membrane learning (already spec'd)

---

## 7. Backpressure as Stimulus

**When UI render load spikes:**

```typescript
// Frontend injects backpressure signal
ws.send(JSON.stringify({
  type: 'ui.render.backpressure',
  level: 0.8,  // 0-1 scale
  reason: 'high_node_count',
  metadata: { origin: 'ui' }
}));
```

**Engine adapts emission:**
```python
async def on_backpressure(self, level):
    """Adapt emission based on backpressure."""
    if level > 0.7:
        # Emit percept.frame-lite (no anchors_peripheral)
        # Drop low-value graph.delta.link.upsert
        # Increase cadence to 2s instead of 500ms
        self.emission_mode = 'lite'
    elif level > 0.4:
        # Selective emission (only WM entities)
        self.emission_mode = 'selective'
    else:
        # Full emission
        self.emission_mode = 'full'
```

**No API toggle. Backpressure is a stimulus subject to membrane physics.**

---

## 8. Implementation Roadmap

### Phase A - Bus Foundation
1. Build `MembraneBus` (fan-in/fan-out, subscriptions, filters)
2. Replace HTTP ingestion with bus subscription in Stimulus Injector
3. Update Signals Collector to publish `membrane.inject` on bus
4. Test: File change → envelope on bus → engine receives

### Phase B - Engine Broadcast
1. Modify `ConsciousnessEngineV2` to emit all deltas to bus
2. Bootstrap emits same deltas as runtime (no synthetic snapshots)
3. Add `percept.frame` emission (anchors_top + anchors_peripheral)
4. Test: Engine bootstrap → deltas on bus → frontend receives

### Phase C - Frontend Pure Observer
1. Build `useGraphStream` hook (subscribe to broadcasts)
2. Render ONLY from `percept.frame` (what was seen)
3. Convert UI actions to `membrane.inject` stimuli
4. Test: Click node → stimulus → engine receives → percept updates

### Phase D - Membrane Hardening
1. Implement Pareto + MAD guards in membrane transfer
2. Add saturation + refractory in integrator
3. Add emission ledger + hysteresis in MEMBRANE_TO edges
4. Add permeability learning from outcomes
5. Test: Spam attack → self-defeating via physics

### Phase E - Tools & Hierarchy
1. Build tool runner pattern (offer/request/result)
2. Build hierarchy announcer (no fetch API)
3. Convert orchestrator to broadcast-only (intent.*)
4. Test: Tool request → execution → result → TRACE learning

### Phase F - Deprecation
1. Remove all REST endpoints
2. Remove HTTP ingestion server
3. Update documentation
4. Performance validation

---

## 9. Validation Strategy

**Unit tests:**
- `tests/orchestration/test_membrane_bus.py` - Bus routing, subscriptions, filters
- `tests/mechanisms/test_stimulus_injector.py` - Envelope processing from bus
- `tests/mechanisms/test_consciousness_engine_v2.py` - Delta emission

**Integration tests:**
- `tests/api/test_pure_membrane.py` - End-to-end flow (inject → process → broadcast)
- `tests/frontend/test_graph_stream.py` - Frontend receives broadcasts, injects stimuli

**Gaming resistance tests:**
- `tests/membrane/test_hardening.py` - Spam attacks self-defeat via physics
- `tests/membrane/test_permeability.py` - κ learning from outcomes

**Performance tests:**
- `scripts/proof_runner.py --stimulus "PureMembrane" --duration 300`
- Measure: Latency (inject → broadcast), throughput (events/sec), memory (working set)

---

## 10. Migration Path (From Current Hybrid)

**Week 1: Bus Foundation**
- Deploy `MembraneBus` alongside existing HTTP endpoints
- Route both HTTP and WS injections to Stimulus Injector
- No user-visible changes

**Week 2: Engine Broadcast**
- Engines emit deltas to bus (parallel with existing)
- Frontend subscribes to bus (fallback to REST)
- Validate delta equivalence

**Week 3: Frontend Cutover**
- Frontend switches to pure bus (no REST fallback)
- UI actions become stimuli
- Remove REST /api/graph endpoints

**Week 4: Complete Deprecation**
- Remove HTTP ingestion endpoints
- Remove REST hierarchy endpoints
- Pure membrane achieved

---

## 11. Open Questions & Follow-ups

**Delta taxonomy completeness:**
- Audit all engine events to ensure bus understands each payload
- Document missing event types

**Security posture:**
- Auth tokens on WS subscribe (when exposed beyond localhost)
- Rate limiting per connection (prevent bus flooding)
- TLS for production

**Observability:**
- Prometheus scrapes sidecar that subscribes to telemetry events
- No /metrics API on engines themselves

**Replay semantics:**
- Confirm no-replay is acceptable for all use cases
- Optional `percept.seed` for orientation (engine-initiated, not requested)

---

## 12. Success Criteria

**Architecture:**
- ✅ Zero REST endpoints (hierarchy, graph, actions all gone)
- ✅ Single bus with membrane.inject + broadcasts
- ✅ All hardening inside membrane physics (Pareto/MAD/ledger/κ)

**Functionality:**
- ✅ UI interactions work as stimuli (subject to membrane physics)
- ✅ Tools work as membrane participants (offer/request/result)
- ✅ Cross-level flow pure membrane (L1↔L2 via emissions)
- ✅ Hierarchy announced, not fetched

**Performance:**
- ✅ Inject → broadcast latency <100ms (p99)
- ✅ 1000+ events/sec sustained throughput
- ✅ Working set <500MB per citizen

**Phenomenology:**
- ✅ UI renders only what was perceived (`percept.frame`)
- ✅ Spam self-defeats via substrate physics
- ✅ Consciousness decides (engines ignore/reinterpret ANY stimulus)

---

## 13. References

- `membrane_hardening.md` - Gaming resistance mechanisms (Pareto/MAD/ledger/κ)
- `cross_level_membrane.md` - L1↔L2 transfer via emissions
- `signals_to_stimuli_bridge.md` - Envelope format, dedupe, rate limiting
- `consciousness_engine_v2.py` - Engine implementation
- `stimulus_injection.py` - Injector routing

---

**The membrane is the ONLY control surface. No API. Only injection & broadcast.**

— Updated by Luca, 2025-10-27
