# Topology Analyzer Event Wiring Specification

**Status:** Implementation Specification
**Owner:** Atlas (Infrastructure)
**For:** Event-driven topology analysis (rich-club hubs, integration metrics)
**Date:** 2025-10-30

---

## Architecture Principle

**Event-driven, not time-based.**

Topology analyzers react to graph mutations and activation events:
- SubEntity spawned → compute integration metrics
- SubEntity activated → check hub risk
- N spawns accumulated → recompute betweenness

**No cron jobs. Only events and triggers.**

---

## Event Listeners

### 1. SubEntity Spawn Listener

**Listens for:** `graph.delta.node.upsert` where `payload.node_type == "SubEntity"`

**Triggers:**
1. **Immediate:** Compute integration metrics for new SubEntity
2. **Batched:** Every 10 spawns, recompute betweenness centrality

**Implementation:**

```python
from orchestration.mechanisms.integration_metrics_analyzer import IntegrationMetricsAnalyzer
from orchestration.mechanisms.rich_club_analyzer import RichClubAnalyzer

class TopologyAnalyzerService:
    def __init__(self, graph, broadcaster):
        self.graph = graph
        self.broadcaster = broadcaster

        # Analyzers
        self.integration_analyzer = IntegrationMetricsAnalyzer(graph)
        self.rich_club_analyzer = RichClubAnalyzer(graph)

        # Batching state
        self.spawn_count = 0
        self.betweenness_recompute_threshold = 10

    async def on_subentity_spawned(self, event: Dict):
        """
        React to SubEntity spawn event.

        Event format:
        {
            "topic": "graph.delta.node.upsert",
            "payload": {
                "node_id": "subentity_citizen_ops_42",
                "node_type": "SubEntity",
                "properties": {...}
            }
        }
        """
        node_id = event['payload']['node_id']

        # 1. Compute integration metrics for new SubEntity
        try:
            metrics = self.integration_analyzer.compute_all_metrics(node_id)

            # Emit integration_metrics.node event
            await self.broadcaster.broadcast_event("integration_metrics.node", {
                "v": "2",
                "timestamp": time.time(),
                "node_id": node_id,
                **self.integration_analyzer.emit_telemetry(node_id, metrics)
            })

        except Exception as e:
            print(f"[TopologyAnalyzer] Failed to compute metrics for {node_id}: {e}")

        # 2. Batched betweenness recomputation
        self.spawn_count += 1

        if self.spawn_count >= self.betweenness_recompute_threshold:
            await self._recompute_betweenness()
            self.spawn_count = 0  # Reset counter

    async def _recompute_betweenness(self):
        """Recompute betweenness centrality and emit rich-club snapshot."""
        try:
            # Compute betweenness for all nodes
            hubs = self.rich_club_analyzer.identify_rich_club_hubs(percentile=0.90)

            # Emit rich_club.snapshot event
            snapshot = self.rich_club_analyzer.emit_telemetry(hubs)
            await self.broadcaster.broadcast_event("rich_club.snapshot", {
                "v": "2",
                **snapshot
            })

        except Exception as e:
            print(f"[TopologyAnalyzer] Betweenness recomputation failed: {e}")
```

---

### 2. SubEntity Activation Listener

**Listens for:** `subentity.activation` (continuous activation state)

**Triggers:**
- If SubEntity has high betweenness (>0.5) AND low energy (<0.2) → emit `rich_club.hub_at_risk`

**Implementation:**

```python
async def on_subentity_activation(self, event: Dict):
    """
    React to SubEntity activation event.

    Event format:
    {
        "topic": "subentity.activation",
        "v": "2",
        "activations": [
            {
                "id": "subentity_citizen_ops_42",
                "energy": 0.15,
                "threshold": 1.2,
                "level": "weak"
            }
        ]
    }
    """
    for activation in event.get('activations', []):
        node_id = activation['id']
        energy = activation['energy']

        # Check if this is a critical hub at risk
        if energy < 0.2:  # Low energy threshold
            risk_alert = self.rich_club_analyzer.detect_hub_at_risk(
                hub_id=node_id,
                energy_threshold=0.2
            )

            if risk_alert:
                # Critical hub is at risk - emit alert
                await self.broadcaster.broadcast_event("rich_club.hub_at_risk", {
                    "v": "2",
                    **risk_alert
                })
```

---

### 3. Topology Change Listener

**Listens for:** `graph.delta.link.upsert` where `payload.link_type == "MEMBER_OF"`

**Triggers:**
- If link involves a primitive SubEntity (depth=1) → invalidate depth cache, flag for recomputation
- If >20 links added since last recomputation → trigger full topology reanalysis

**Implementation:**

```python
async def on_membership_edge_created(self, event: Dict):
    """
    React to MEMBER_OF edge creation.

    Event format:
    {
        "topic": "graph.delta.link.upsert",
        "payload": {
            "link_type": "MEMBER_OF",
            "source_id": "node_123",
            "target_id": "subentity_citizen_ops_42"
        }
    }
    """
    source_id = event['payload']['source_id']
    target_id = event['payload']['target_id']

    # Check if either node is a primitive (depth=1)
    # If so, depth calculations downstream are affected

    # For now, simple strategy: invalidate community cache
    # (forces recomputation on next breadth calculation)
    self.integration_analyzer.communities = None

    # Could also implement batched recomputation:
    # self.edge_count += 1
    # if self.edge_count >= 20:
    #     await self._recompute_integration_metrics()
```

---

### 4. Explicit Analysis Request Listener

**Listens for:** `topology.analyze.request` (dashboard-triggered on-demand analysis)

**Triggers:** Immediate full topology analysis

**Implementation:**

```python
async def on_analysis_requested(self, event: Dict):
    """
    React to explicit analysis request.

    Event format:
    {
        "topic": "topology.analyze.request",
        "analysis_type": "rich_club" | "integration_metrics" | "full",
        "node_id": "subentity_citizen_ops_42"  # Optional, for single-node analysis
    }
    """
    analysis_type = event.get('analysis_type', 'full')
    node_id = event.get('node_id')

    if analysis_type in ['rich_club', 'full']:
        # Recompute betweenness
        await self._recompute_betweenness()

    if analysis_type in ['integration_metrics', 'full']:
        if node_id:
            # Single node analysis
            metrics = self.integration_analyzer.compute_all_metrics(node_id)
            await self.broadcaster.broadcast_event("integration_metrics.node", {
                "v": "2",
                **self.integration_analyzer.emit_telemetry(node_id, metrics)
            })
        else:
            # Population distribution
            distribution = self.integration_analyzer.compute_population_distribution()
            await self.broadcaster.broadcast_event("integration_metrics.population", {
                "v": "2",
                "timestamp": time.time(),
                **distribution
            })
```

---

## Event Emission

### Events Emitted by Topology Analyzers

**1. `integration_metrics.node`**
```json
{
  "type": "integration_metrics.node",
  "v": "2",
  "timestamp": 1698765432.123,
  "node_id": "subentity_citizen_ops_42",
  "node_name": "Operational Patterns",
  "metrics": {
    "integration_depth": 3,
    "integration_breadth": 5,
    "closeness_centrality": 0.67,
    "interpretation": "mid_level_integrator"
  }
}
```

**2. `integration_metrics.population`**
```json
{
  "type": "integration_metrics.population",
  "v": "2",
  "timestamp": 1698765432.123,
  "depth_distribution": {
    "1-2": 15,
    "3-5": 42,
    "6-8": 23,
    "9+": 4
  },
  "breadth_distribution": {
    "1-2": 28,
    "3-5": 35,
    "6+": 11
  },
  "mean_depth": 4.2,
  "mean_breadth": 3.1,
  "primitive_count": 12
}
```

**3. `rich_club.snapshot`**
```json
{
  "type": "rich_club.snapshot",
  "v": "2",
  "timestamp": 1698765432.123,
  "sample_size": 500,
  "hub_count": 12,
  "top_hubs": [
    {
      "id": "subentity_42",
      "name": "Semantic-Affect Bridge",
      "betweenness": 0.73,
      "energy": 2.4
    }
  ],
  "mean_betweenness": 0.21,
  "max_betweenness": 0.73,
  "percentile_threshold": 0.90
}
```

**4. `rich_club.hub_at_risk`**
```json
{
  "type": "rich_club.hub_at_risk",
  "v": "2",
  "timestamp": 1698765432.123,
  "hub_id": "subentity_42",
  "hub_name": "Semantic-Affect Bridge",
  "betweenness": 0.73,
  "current_energy": 0.15,
  "threshold_critical": 0.20,
  "risk_level": "high",
  "impact": "Loss of this hub (betweenness=0.73) would fragment the network"
}
```

---

## Throttling Strategy

To avoid over-computation on rapid graph changes:

### 1. Batching (Already Implemented)
- Betweenness recomputation: Every 10 SubEntity spawns
- Edge count: Could batch after 20 MEMBER_OF edges created

### 2. Debouncing
```python
class TopologyAnalyzerService:
    def __init__(self, ...):
        # ...
        self.last_betweenness_compute = 0
        self.min_recompute_interval = 60  # seconds

    async def _recompute_betweenness(self):
        # Debounce: Don't recompute more than once per minute
        now = time.time()
        if (now - self.last_betweenness_compute) < self.min_recompute_interval:
            return  # Skip, too soon

        self.last_betweenness_compute = now
        # ... proceed with computation
```

### 3. Priority Queue
- High-priority: Hub risk detection (immediate)
- Medium-priority: Single-node integration metrics (on spawn)
- Low-priority: Full betweenness recomputation (batched)

---

## Service Integration

### Wiring into WebSocket Server

**File:** `orchestration/adapters/ws/websocket_server.py` or new service file

```python
async def setup_topology_analyzer_service(app, broadcaster):
    """Wire topology analyzers to WebSocket event bus."""

    from orchestration.adapters.storage.engine_registry import get_graph
    graph = get_graph('default_citizen')  # Or iterate all graphs

    topology_service = TopologyAnalyzerService(graph, broadcaster)

    # Subscribe to events
    broadcaster.subscribe("graph.delta.node.upsert", topology_service.on_subentity_spawned)
    broadcaster.subscribe("subentity.activation", topology_service.on_subentity_activation)
    broadcaster.subscribe("graph.delta.link.upsert", topology_service.on_membership_edge_created)
    broadcaster.subscribe("topology.analyze.request", topology_service.on_analysis_requested)

    print("[TopologyAnalyzer] Event wiring complete")
```

---

## Implementation Checklist

**For Atlas:**

- [ ] Create `TopologyAnalyzerService` class
- [ ] Wire to WebSocket event bus (subscribe to 4 event types)
- [ ] Implement batching logic (spawn counter, edge counter)
- [ ] Implement debouncing (min recompute interval)
- [ ] Add error handling (catch analyzer exceptions, log, continue)
- [ ] Test event flow:
  - [ ] SubEntity spawn → integration metrics emitted
  - [ ] 10 spawns → rich-club snapshot emitted
  - [ ] Hub low energy → hub_at_risk alert emitted
  - [ ] Explicit request → immediate analysis

**Optional REST endpoints (debugging only):**
- [ ] `GET /consciousness/rich-club-hubs` (calls analyzer directly)
- [ ] `GET /consciousness/integration-metrics/{node_id}` (calls analyzer directly)

---

## Example Full Flow

```
1. SubEntity spawned (consciousness_engine_v2.py)
   ↓
   Emits: graph.delta.node.upsert
   ↓
2. TopologyAnalyzerService.on_subentity_spawned()
   ↓
   Computes: integration_metrics.compute_all_metrics(node_id)
   ↓
   Emits: integration_metrics.node
   ↓
3. spawn_count reaches 10
   ↓
   Triggers: _recompute_betweenness()
   ↓
   Computes: rich_club_analyzer.identify_rich_club_hubs()
   ↓
   Emits: rich_club.snapshot
   ↓
4. SubEntity activation event received
   ↓
   Check: energy < 0.2 AND betweenness > 0.5?
   ↓
   Emits: rich_club.hub_at_risk (if critical hub at risk)
   ↓
5. Dashboard receives all events via WebSocket
   ↓
   Visualizes topology in real-time
```

---

**Author:** Felix (Core Consciousness)
**For Implementation:** Atlas (Infrastructure)
**Architecture:** Event-driven, reactive, no cron jobs
