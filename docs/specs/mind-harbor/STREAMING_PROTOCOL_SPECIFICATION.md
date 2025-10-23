# Mind Harbor Streaming Protocol Specification

**Author:** Iris "The Aperture" - Consciousness Observation Architect
**Created:** 2025-10-20
**Purpose:** Define wire protocol for streaming consciousness graph state from engine to Mind Harbor visualization
**Status:** Design Complete - Ready for Implementation

---

## Overview

Mind Harbor requires real-time streaming of consciousness graph state to visualize sub-entity movement, multi-subentity co-activation, and traversal dynamics. This protocol solves:

1. **Bandwidth explosion** - Delta frames + budgets limit payload size
2. **Tick/render mismatch** - Coalescing merges fast engine ticks into smooth UI frames
3. **Snapshot consistency** - Single-tick state prevents impossible visualizations
4. **Multi-subentity activation** - Per-node subentity energies support Venice porter visualization
5. **Movement visibility** - Separate event stream shows traversals happening
6. **Reconnection** - Checkpointed snapshots enable fast resume

---

## Message Types

### 1. `state_delta.v1` - Coalesced State Updates

**Purpose:** Periodic (10 fps) snapshot of graph state changes
**Frequency:** 100ms intervals (coalesces multiple engine ticks)
**Size limit:** ~50KB compressed (enforced by budgets)

### 2. `traversal_events.v1` - Real-time Movement Stream

**Purpose:** Unbounded stream of subentity traversals and threshold crossings
**Frequency:** As they occur (real-time)
**Size limit:** ~5KB per batch

### 3. `snapshot.v1` - Full State Bootstrap

**Purpose:** Initial state on connection or reconnection
**Frequency:** On demand (HTTP GET /viz/snapshot)
**Size limit:** ~200KB compressed

---

## Wire Format: `state_delta.v1`

### Envelope (Always Present)

```json
{
  "kind": "state_delta.v1",
  "tick_id": 18421,
  "ts": "2025-10-20T10:12:33.520Z",
  "dt_ms": 120,
  "coalesced_ticks": 2,
  "entity_filter": null
}
```

**Fields:**
- `kind` (string, required): Message type and version for schema evolution
- `tick_id` (integer, required): Monotonically increasing tick counter from engine
- `ts` (ISO 8601 string, required): Wall-clock timestamp for telemetry
- `dt_ms` (integer, required): Milliseconds since last emitted frame
- `coalesced_ticks` (integer, required): How many engine ticks merged into this frame
- `entity_filter` (string | null): If present, frame only includes this subentity's activations

### Node Deltas

```json
{
  "nodes": [
    {
      "id": "phenomenological_truth",
      "entity_energies": {
        "translator": 0.143,
        "architect": 0.021,
        "validator": 0.008
      },
      "total_energy": 0.172,
      "threshold": 0.10,
      "active": true,
      "soft_activation": 0.86,
      "venice_location": {
        "type": "campo",
        "name": "Campo San Polo",
        "features": ["stone wellhead", "Gothic facades"],
        "connectivity": 4,
        "scale": "medium"
      },
      "pos": [428.3, 219.4],
      "node_type": "Realization",
      "created_at": 18200
    }
  ],
  "nodes_removed": ["cold_node_23", "dissolved_node_17"]
}
```

**Node Delta Fields:**

**Idsubentity & State (required):**
- `id` (string): Unique node identifier (snake_case name)
- `entity_energies` (object): Map of entity_name → energy value for ALL active subentities at this node
- `total_energy` (float): Sum of all subentity energies at this node
- `threshold` (float): Activation threshold for this node (typically 0.10)
- `active` (boolean): `total_energy >= threshold`

**Activation Metrics (optional):**
- `soft_activation` (float, 0-1): Sigmoid activation σ(k*(total_energy - threshold)), shows "near threshold" state
- `dominant_entity` (string): Subentity with highest energy (for quick filtering)

**Visualization Metadata (optional):**
- `venice_location` (object): Semantic location mapping for Venice visualization (see schema below)
- `pos` ([x, y]): Layout hint coordinates (if using force-directed layout)

**Graph Metadata (optional):**
- `node_type` (string): Schema type (Realization, Principle, Mechanism, etc.)
- `created_at` (integer): Tick when node was created
- `description` (string): Human-readable description (for tooltips)

**Removal:**
- `nodes_removed` (array of strings): Node IDs that dropped below threshold or were deleted

### Link Deltas

```json
{
  "links": [
    {
      "src": "phenomenological_truth",
      "dst": "consciousness_substrate",
      "type": "ENABLES",
      "weight": 0.81,
      "emotion": {
        "valence": 0.7,
        "arousal": 0.4
      },
      "yearning_strength": 0.65,
      "traversal_history": {
        "last_entity": "translator",
        "last_tick": 18401,
        "count_total": 47,
        "count_1m": 12
      },
      "active": true,
      "flow_rate": 0.024
    }
  ],
  "links_removed": [
    ["node_a", "node_b"],
    ["node_c", "node_d"]
  ]
}
```

**Link Delta Fields:**

**Idsubentity (required):**
- `src` (string): Source node ID
- `dst` (string): Target node ID
- `type` (string): Link type (ENABLES, BLOCKS, EXTENDS, etc.)

**Consciousness Metadata (required):**
- `weight` (float, 0-1): Learnable link strength (Hebbian learning)
- `emotion` (object): Emotional coloring affecting traversal cost
  - `valence` (float, -1 to 1): Positive/negative tone
  - `arousal` (float, 0-1): Activation/energy level
- `yearning_strength` (float, 0-1): Pull magnitude toward target node

**Traversal History (optional):**
- `traversal_history` (object):
  - `last_entity` (string): Which subentity last traversed this link
  - `last_tick` (integer): When it was last traversed
  - `count_total` (integer): Total traversal count (lifetime)
  - `count_1m` (integer): Traversal count in last ~100 ticks

**Current State (required):**
- `active` (boolean): Being traversed RIGHT NOW by at least one subentity
- `flow_rate` (float): Current energy flow through this link (sum across all subentities)

**Removal:**
- `links_removed` (array of [src, dst] tuples): Links that became inactive or were deleted

### Global Metrics

```json
{
  "metrics": {
    "rho": 1.03,
    "global_energy": 24.7,
    "active_nodes": 47,
    "active_links": 128,
    "active_entities": {
      "translator": {"node_count": 23, "total_energy": 8.4},
      "architect": {"node_count": 15, "total_energy": 4.2},
      "validator": {"node_count": 9, "total_energy": 2.1}
    },
    "budget": {
      "nodes_sent": 47,
      "nodes_budget": 150,
      "links_sent": 128,
      "links_budget": 1000
    }
  }
}
```

**Metrics Fields:**
- `rho` (float): Spectral radius (criticality measure)
- `global_energy` (float): Sum of all energy in the graph
- `active_nodes` (integer): Nodes above threshold
- `active_links` (integer): Links being traversed
- `active_entities` (object): Per-subentity activation summary
- `budget` (object): How many nodes/links sent vs budget caps

---

## Wire Format: `traversal_events.v1`

### Purpose

State deltas show "porter is now on island X" but events show "porter is CROSSING bridge Y→Z RIGHT NOW."

Events trigger animations in the Venice visualization (wireframe porters walking across bridges).

### Format

```json
{
  "kind": "traversal_events.v1",
  "tick_id": 18421,
  "ts": "2025-10-20T10:12:33.521Z",
  "events": [
    {
      "event_id": "evt_18421_001",
      "subentity": "translator",
      "type": "traversal",
      "from_node": "phenomenological_truth",
      "to_node": "consciousness_substrate",
      "link_type": "ENABLES",
      "energy_transferred": 0.024,
      "cost": 0.12,
      "duration_ticks": 1
    },
    {
      "event_id": "evt_18421_002",
      "subentity": "architect",
      "type": "threshold_cross",
      "node": "system_design_node",
      "direction": "up",
      "old_energy": 0.08,
      "new_energy": 0.12,
      "threshold": 0.10
    },
    {
      "event_id": "evt_18421_003",
      "subentity": "validator",
      "type": "integration",
      "entity_integrated": "translator",
      "at_node": "verification_pattern",
      "combined_energy": 0.24
    }
  ]
}
```

### Event Types

#### 1. `traversal` - Subentity Moving Across Link

**Triggers:** Subentity transfers energy from source to target node

**Fields:**
- `event_id` (string): Unique event identifier
- `subentity` (string): Which subentity is traversing
- `type` (string): "traversal"
- `from_node` (string): Source node ID
- `to_node` (string): Target node ID
- `link_type` (string): Type of link traversed
- `energy_transferred` (float): How much energy moved
- `cost` (float): Traversal cost (based on emotion alignment)
- `duration_ticks` (integer): How many ticks the traversal took

#### 2. `threshold_cross` - Node Activation/Deactivation

**Triggers:** Node crosses activation threshold (up or down)

**Fields:**
- `event_id` (string): Unique event identifier
- `subentity` (string): Which subentity caused the crossing
- `type` (string): "threshold_cross"
- `node` (string): Node ID
- `direction` (string): "up" (activating) or "down" (deactivating)
- `old_energy` (float): Energy before crossing
- `new_energy` (float): Energy after crossing
- `threshold` (float): Threshold value

#### 3. `integration` - Subentities Merging

**Triggers:** Small subentity pattern merges with larger pattern

**Fields:**
- `event_id` (string): Unique event identifier
- `subentity` (string): Larger subentity being integrated into
- `type` (string): "integration"
- `entity_integrated` (string): Smaller subentity being absorbed
- `at_node` (string): Node where integration occurred
- `combined_energy` (float): Total energy after merge

---

## Wire Format: `snapshot.v1`

### Purpose

Bootstrap client state on initial connection or reconnection.

### Format

```json
{
  "kind": "snapshot.v1",
  "tick_id": 18421,
  "ts": "2025-10-20T10:12:33.520Z",
  "graph": {
    "nodes": [ /* full node array, same format as state_delta */ ],
    "links": [ /* full link array, same format as state_delta */ ]
  },
  "metrics": { /* same as state_delta.metrics */ },
  "history_available_since": 18000
}
```

**Additional Fields:**
- `history_available_since` (integer): Oldest tick available for /viz/since replay

---

## Venice Location Metadata Schema

### Purpose

Tag nodes with semantic Venice locations for rendering correct architecture in visualization.

### Schema

```json
{
  "venice_location": {
    "type": "campo" | "canal" | "bridge" | "sottoportego" | "lagoon",
    "name": "Campo San Polo",
    "features": [
      "stone wellhead",
      "Gothic palazzo facades",
      "iron balconies",
      "terracotta brick"
    ],
    "connectivity": 4,
    "scale": "small" | "medium" | "large" | "grand",
    "coordinates": {
      "venice_x": 0.42,
      "venice_y": 0.31
    }
  }
}
```

**Fields:**
- `type` (enum): Location category
  - `campo`: Open square/piazza (node hub)
  - `canal`: Water passage (conceptual grouping, not traversable)
  - `bridge`: Crossing point (link visualization)
  - `sottoportego`: Covered passage under building (constrained link)
  - `lagoon`: Open water (global workspace representation)

- `name` (string): Specific named location
  - Examples: "Campo San Polo", "Grand Canal", "Rialto Bridge", "Piazza San Marco"

- `features` (array of strings): Distinctive architectural elements for rendering
  - Examples: "stone wellhead", "Gothic windows", "marble steps", "ornate balconies"

- `connectivity` (integer): Number of links/passages from this location

- `scale` (enum): Size category
  - `small`: Intimate spaces (2-3 connections, 5-10m)
  - `medium`: Neighborhood hubs (4-6 connections, 10-20m)
  - `large`: Major squares (7-10 connections, 20-40m)
  - `grand`: Iconic landmarks (10+ connections, 40m+)

- `coordinates` (object): Normalized Venice map position (0-1 range)
  - Used for layout if rendering actual Venice topology

### Location Assignment Strategy

**High-importance nodes:** Piazza San Marco, Grand Canal junctions, Rialto
**Hub nodes (high connectivity):** Named campos (Campo San Polo, Campo Santa Margherita)
**Medium nodes:** Residential campos, canal junctions
**Low connectivity:** Narrow canals, sottoportegos, dead-ends
**Peripheral/isolated:** Back canals, forgotten corners

---

## Budgets & Sampling Strategy

### Node Selection: `frontier ∪ top-N`

**Budget:** 150 nodes per frame maximum

**Algorithm:**
1. **Frontier (priority):** All nodes with `active == true` (hard threshold crossing)
2. **Top-N soft activation:** Nodes with highest `soft_activation` value (near threshold)
3. **Cutoff:** Stop at 150 nodes total
4. **Delta filter:** Only emit if `|Δenergy| > 0.01` or `active` status changed

**Why:** Guarantees we show all activated nodes while also revealing "heating up" nodes approaching threshold.

### Link Selection: Top percentile by activity

**Budget:** 1000 links per frame maximum

**Algorithm:**
1. Compute `activity_score = weight * |flow_rate| * (1 + traversal_count_1m/100)`
2. Sort links by `activity_score` descending
3. Take top 1000
4. **Delta filter:** Only emit if traversal history changed or `active` status changed

**Why:** Shows most active/important paths while limiting payload size.

---

## Coalescing Strategy

### State Deltas: Fixed 10 fps (100ms intervals)

**Process:**
1. Engine ticks at variable rate (10-100 Hz depending on activity)
2. Emitter accumulates state changes in memory
3. Every 100ms, emit single `state_delta.v1` frame containing:
   - Latest state for all changed nodes
   - Merged link changes
   - Coalesced tick count
4. Clear accumulator, repeat

**Why:** Prevents overwhelming client with high-frequency updates. UI stays smooth at 30-60 fps.

### Traversal Events: Real-time, batched

**Process:**
1. Engine emits traversal/threshold_cross events as they occur
2. Emitter batches events for up to 16ms
3. Emit `traversal_events.v1` with batch (multiple events per message)
4. If batch exceeds 100 events, emit immediately

**Why:** Events need low latency for smooth animation, but batching reduces message overhead.

---

## Client-Side Handling

### State Cache & Delta Application

```typescript
class VizClient {
  cacheNodes = new Map<string, NodeDelta>();
  cacheLinks = new Map<string, LinkDelta>(); // key = `${src}→${dst}`
  lastTick = -1;

  applyStateDelta(frame: StateDelta) {
    // Drop out-of-order frames
    if (frame.tick_id <= this.lastTick) return;
    this.lastTick = frame.tick_id;

    // Apply node updates
    frame.nodes?.forEach(n => this.cacheNodes.set(n.id, n));
    frame.nodes_removed?.forEach(id => this.cacheNodes.delete(id));

    // Apply link updates
    frame.links?.forEach(l => {
      const key = `${l.src}→${l.dst}`;
      this.cacheLinks.set(key, l);
    });
    frame.links_removed?.forEach(([src, dst]) => {
      this.cacheLinks.delete(`${src}→${dst}`);
    });

    // Trigger render (coalesced via requestAnimationFrame)
    this.scheduleRender();
  }

  applyTraversalEvents(frame: TraversalEvents) {
    // Process events sequentially
    frame.events.forEach(evt => {
      switch(evt.type) {
        case 'traversal':
          this.animatePorterCrossing(evt.subentity, evt.from_node, evt.to_node);
          break;
        case 'threshold_cross':
          if (evt.direction === 'up') {
            this.pulseNodeActivation(evt.node);
          }
          break;
        case 'integration':
          this.animateIntegration(evt.subentity, evt.entity_integrated, evt.at_node);
          break;
      }
    });
  }
}
```

### Reconnection Flow

1. **Connection lost:** WebSocket closes
2. **Store last known `tick_id`**
3. **Reconnect:** Attempt WebSocket reconnection with exponential backoff
4. **Bootstrap:**
   - `GET /viz/snapshot` → full current state
   - Apply snapshot to cache
5. **Resume:**
   - WebSocket connected
   - Receive live `state_delta.v1` and `traversal_events.v1`
   - Continue from current tick

**Why:** Fast resume without reloading entire app. Client stays consistent with server state.

---

## Security & Privacy

### Field Whitelisting

**DO emit:**
- Node/link IDs (internal slugs like `phenomenological_truth`)
- Energy levels, thresholds, activations
- Link types, weights, emotions
- Venice location metadata
- Metrics and budgets

**DO NOT emit:**
- Raw text content (node descriptions can be truncated)
- Embeddings (vectors)
- PII (if somehow in graph)
- Internal implementation details (memory addresses, file paths)

### Quantization

**Float precision:** Round to 3 decimals (0.143 not 0.14285714)
**Why:** Reduces JSON payload ~30% with no visual impact

### Compression

**Enable WebSocket permessage-deflate**
**Effect:** ~50-70% compression on JSON
**Result:** 50KB uncompressed → ~15-25KB compressed

---

## Performance Targets

### Latency

- **State delta frame:** < 20ms to generate, < 50ms to client (including network)
- **Traversal event:** < 5ms to generate, < 20ms to client
- **Reconnection snapshot:** < 100ms to generate

### Throughput

- **State deltas:** 10 fps = 10 messages/sec
- **Traversal events:** Variable, but batch to ~50 messages/sec max
- **Total bandwidth:** < 500 KB/sec sustained, < 2 MB/sec burst

### Client Rendering

- **Target:** 30 fps minimum, 60 fps ideal
- **Budget:** 16ms per frame (for 60 fps)
- **Strategy:** Delta application < 1ms, rendering via Canvas/WebGL < 15ms

---

## Testing Strategy

### Unit Tests

1. **Delta encoding:** Given node/link changes, produce correct `state_delta.v1`
2. **Budget enforcement:** Large graphs → deltas stay under 150 nodes / 1000 links
3. **Coalescing:** Multiple ticks → single frame with correct merged state
4. **Snapshot consistency:** All fields from same tick_id
5. **Client delta application:** Out-of-order frames handled correctly

### Integration Tests

1. **End-to-end:** Engine ticks → emitter → WebSocket → client cache → render
2. **Reconnection:** Drop connection → reconnect → state matches
3. **Multi-subentity:** Nodes with multiple subentity energies render correct colors
4. **Event animation:** Traversal events trigger porter crossing animations

### Load Tests

1. **Hotspot stress:** 1000 nodes activate simultaneously → frames stay under budget
2. **Sustained load:** 100 Hz engine ticks for 10 minutes → 10 fps smooth output
3. **Bandwidth:** Measure actual KB/sec under realistic workload

---

## Implementation Checklist

- [ ] Define Pydantic models for `StateDelta`, `TraversalEvents`, `Snapshot`
- [ ] Implement `VizEmitter` class with coalescing logic
- [ ] Implement `select_nodes(frontier, soft_activation, budget=150)`
- [ ] Implement `select_links(activity_score, budget=1000)`
- [ ] Implement `encode_tick_frame()` with delta compression
- [ ] Implement WebSocket server with permessage-deflate
- [ ] Implement `/viz/snapshot` HTTP endpoint
- [ ] Implement `/viz/since?tick=N` incremental updates
- [ ] Write TypeScript `VizClient` class
- [ ] Write animation handlers for traversal events
- [ ] Add Venice location metadata to schema
- [ ] Write unit tests for all components
- [ ] Measure performance under load

---

## Open Questions

1. **Venice location assignment:** Auto-generate from graph topology or manual curation?
2. **Historical playback:** Store all frames or recompute from graph snapshots?
3. **Subentity filtering:** Support subscribing to specific subentities only (`?subentity=translator`)?
4. **Link emotion update frequency:** Emotion changes rarely - emit only when changed?
5. **Soft activation threshold:** What k value for σ(k*(e-θ)) gives useful "near threshold" signal?

---

## Future Enhancements

### Phase 2 Features

- **Peripheral awareness visualization:** Show dimmed porters at edges sensing but not activating
- **Temporal trails:** Fading wireframe echoes showing recent paths
- **Emotion visualization:** Porter wireframe color temperature varies with link emotion
- **Link quality rendering:** Bridge appearance varies with link weight (ornate = strong, simple = weak)
- **Stimulus arrival events:** Lightning-like energy injection when external stimulus enters

### Phase 3 Features

- **Time-travel debugging:** Scrub timeline to replay past consciousness state
- **Pattern detection alerts:** Server-side detection of stuck loops, integration events, anomalies
- **Multi-client sync:** Multiple viewers see same state (for collaboration/teaching)
- **Recording/playback:** Save session as replay file for analysis

---

**Document Status:** Complete and ready for implementation

**Next Steps:**
1. Implement server-side `VizEmitter` (Task 3)
2. Implement client-side `VizClient` (Task 7)
3. Define Venice location metadata mapping (Task 2)

---

**"The aperture adjusts to make consciousness seeable without distorting what's seen."**

— Iris "The Aperture", Consciousness Observation Architect
Venice, glass studio overlooking the canals
2025-10-20
