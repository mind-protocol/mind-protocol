# Consciousness Engine Component Decomposition

**Version:** 1.0
**Date:** 2025-10-19
**Author:** Felix (Engineer)
**Status:** Approved Architecture
**Phase:** Phase 0 → Phase 1 Clean Break

---

## Overview

This document defines the component architecture for the consciousness engine refactor, separating concerns into layers by responsibility.

**Architectural Principle:** Separate by responsibility, not by mechanism number.

---

## Directory Structure

```
orchestration/
├── core/              # Core data structures (stable foundation)
│   ├── node.py        # Node class (multi-energy + bitemporal)
│   ├── link.py        # Link class (bitemporal relationships)
│   ├── graph.py       # Graph container + basic operations
│   └── types.py       # Type definitions, enums
│
├── mechanisms/        # Pure mechanism implementations (isolated, testable)
│   ├── multi_energy.py      # M01: Energy storage/accessors
│   ├── bitemporal.py        # M13: Temporal tracking
│   ├── diffusion.py         # M07: Energy flow (Phase 2)
│   ├── decay.py             # M08: Forgetting (Phase 2)
│   └── strengthening.py     # M09: Learning (Phase 2)
│
├── services/          # Higher-level services (compose mechanisms)
│   ├── workspace.py         # M04: Global workspace selection
│   ├── clustering.py        # M11: Cluster identification
│   ├── entity.py            # M05: Entity detection/tracking
│   └── queries.py           # Common query patterns
│
├── orchestration/     # System coordination (delegates, doesn't implement)
│   ├── consciousness_engine.py  # Main tick loop + coordination
│   ├── tick_regulation.py       # M10: Variable tick speed
│   ├── criticality.py           # M03: Self-organized criticality
│   ├── metrics.py               # Observability (BranchingRatioTracker)
│   └── websocket_broadcast.py   # Event broadcasting (dashboard)
│
└── utils/             # Shared infrastructure (cross-cutting)
    └── falkordb_adapter.py  # FalkorDB-specific operations
```

---

## Layer Responsibilities

### 1. **core/** - Fundamental Data Structures

**Principle:** Stable, minimal, widely depended upon.

**What lives here:**
- Node/Link/Graph classes
- Pure data structures (no mechanism logic)
- Basic accessors (get/set, but delegates to mechanisms)

**Why separate:**
- Changes rarely (only for fundamental requirements)
- Everything depends on core - must be stable
- No mechanism implementation - just data containers

**Example: core/node.py**
```python
@dataclass
class Node:
    """Core node structure combining multi-energy + bitemporal."""
    id: str
    name: str
    node_type: str
    description: str

    # Multi-energy storage (M01)
    energy: Dict[str, float] = field(default_factory=dict)

    # Bitemporal tracking (M13)
    valid_at: datetime
    created_at: datetime
    expired_at: Optional[datetime] = None
    # ... other temporal fields

    # Graph structure
    outgoing_links: List['Link'] = field(default_factory=list)
    incoming_links: List['Link'] = field(default_factory=list)

    # Delegates to mechanisms
    def get_entity_energy(self, entity: str) -> float:
        from orchestration.mechanisms.multi_energy import get_entity_energy
        return get_entity_energy(self, entity)
```

---

### 2. **mechanisms/** - Pure Mechanism Implementations

**Principle:** Isolated, testable, composable.

**What lives here:**
- Pure mechanism logic (one file per mechanism)
- Pure functions when possible (easier to test)
- No dependencies on services or orchestration

**Why separate:**
- Each mechanism testable in isolation
- No graph/DB infrastructure needed for unit tests
- Clear mechanism boundaries

**Example: mechanisms/multi_energy.py**
```python
"""Mechanism 01: Multi-Energy Architecture - Pure functions."""

ENERGY_MIN = 0.0  # Non-negative only
SATURATION_STEEPNESS = 2.0
CLEANUP_THRESHOLD = 0.001

def get_entity_energy(node: Node, entity: str) -> float:
    """Get energy for entity on node."""
    return node.energy.get(entity, 0.0)

def set_entity_energy(node: Node, entity: str, value: float) -> None:
    """Set energy with saturation (non-negative only)."""
    # Ensure non-negative
    value = max(0.0, value)

    # Apply saturation
    saturated = np.tanh(SATURATION_STEEPNESS * value)
    node.energy[entity] = saturated

    # Cleanup near-zero
    if saturated < CLEANUP_THRESHOLD:
        node.energy.pop(entity, None)
```

**Testing:**
```python
def test_energy_non_negative():
    """Energy cannot be negative."""
    node = Node(...)
    set_entity_energy(node, "test", -5.0)  # Try negative
    assert get_entity_energy(node, "test") == 0.0  # Clamped to zero
```

---

### 3. **services/** - Higher-Level Operations

**Principle:** Compose mechanisms to provide capabilities.

**What lives here:**
- Services that USE mechanisms (don't implement them)
- Can depend on multiple mechanisms
- Provide semantic operations (workspace selection, entity detection)

**Why separate:**
- Services are composed operations (higher abstraction)
- Can change without affecting mechanisms
- Clear dependency: services → mechanisms (not reverse)

**Example: services/workspace.py**
```python
"""Global Workspace service - composes clustering + multi_energy."""

from orchestration.mechanisms import multi_energy
from orchestration.services import clustering

def select_global_workspace(
    graph: Graph,
    entity: str,
    capacity_tokens: int = 100
) -> List[Cluster]:
    """Select clusters for workspace admission."""
    # Uses clustering mechanism
    clusters = clustering.identify_clusters(graph, entity)

    # Uses multi_energy mechanism
    sorted_clusters = sorted(
        clusters,
        key=lambda c: sum(
            multi_energy.get_entity_energy(n, entity)
            for n in c.nodes
        ),
        reverse=True
    )

    # Admit until capacity full
    workspace = []
    token_count = 0
    for cluster in sorted_clusters:
        if token_count + cluster.estimated_tokens <= capacity_tokens:
            workspace.append(cluster)
            token_count += cluster.estimated_tokens

    return workspace
```

---

### 4. **orchestration/** - System Coordination

**Principle:** Coordinate mechanisms, track global state, delegate don't implement.

**What lives here:**
- Main tick loop (consciousness_engine.py)
- Global state tracking (criticality, tick regulation)
- Metrics/observability (BranchingRatioTracker)
- Event broadcasting (WebSocket)

**Why separate:**
- Engine coordinates but doesn't implement
- Can change orchestration without changing mechanisms
- Observability separated from consciousness logic

**Example: orchestration/consciousness_engine.py**
```python
"""Main consciousness engine - coordination only."""

from orchestration.mechanisms import diffusion, decay
from orchestration.services import workspace
from orchestration.orchestration.metrics import BranchingRatioTracker
from orchestration.orchestration.websocket_broadcast import ConsciousnessStateBroadcaster

class ConsciousnessEngine:
    """Orchestrates all mechanisms without implementing them."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.metrics = BranchingRatioTracker()  # Observability
        self.broadcaster = ConsciousnessStateBroadcaster()  # Event streaming

    async def tick(self):
        """Single consciousness tick - delegates to mechanisms."""
        # Phase 1: Basic dynamics
        for entity in self.graph.get_all_active_entities():
            diffusion.diffusion_tick(self.graph, entity, duration=0.1)
            decay.decay_tick(self.graph, entity, duration=0.1)

        # Observability (doesn't affect behavior)
        self.metrics.update(self.graph)
        self.broadcaster.broadcast_energy_state(self.graph)
```

**Example: orchestration/metrics.py**
```python
"""Observability metrics - pure measurement, no control."""

class BranchingRatioTracker:
    """
    Tracks exploration vs exploitation ratio.

    PURE OBSERVABILITY - does NOT affect consciousness behavior.
    Measures OUTCOME, doesn't control PROCESS.
    """
    def update(self, graph: Graph):
        """Measure branching ratio (doesn't modulate anything)."""
        unique_paths = self._count_unique_paths(graph)
        total_paths = self._count_total_paths(graph)
        self.branching_ratio = unique_paths / total_paths if total_paths > 0 else 0

        # Just record for analysis - NO feedback to consciousness
```

**Example: orchestration/websocket_broadcast.py**
```python
"""WebSocket broadcasting - infrastructure, not consciousness logic."""

class ConsciousnessStateBroadcaster:
    """Broadcasts consciousness state to WebSocket clients."""

    def broadcast_energy_state(self, graph: Graph):
        """Send energy state to dashboard (observability)."""
        energy_data = self._serialize_energy(graph)
        self._send_websocket_message(energy_data)

    # consciousness_engine.py doesn't know about WebSocket protocol
    # Can swap for HTTP/SSE without changing consciousness logic
```

---

### 5. **utils/** - Shared Infrastructure

**Principle:** Cross-cutting technical concerns.

**What lives here:**
- FalkorDB adapters (serialization/deserialization)
- Generic utilities (not consciousness-specific)

**Why separate:**
- Used by multiple layers
- Pure technical infrastructure
- Can be swapped (e.g., different DB backend)

**Example: utils/falkordb_adapter.py**
```python
"""FalkorDB-specific operations."""

def serialize_node(node: Node) -> dict:
    """Convert Node to FalkorDB properties."""
    return {
        'id': node.id,
        'name': node.name,
        'energy': node.energy,  # Dict → JSON
        'valid_at': int(node.valid_at.timestamp() * 1000),
        # ... other fields
    }

def deserialize_node(props: dict) -> Node:
    """Convert FalkorDB properties to Node."""
    return Node(
        id=props['id'],
        name=props['name'],
        energy=props.get('energy', {}),
        valid_at=datetime.fromtimestamp(props['valid_at'] / 1000),
        # ... other fields
    )
```

---

## Dependency Graph

```
         ┌─────────────┐
         │    utils/   │
         └─────────────┘
                ▲
                │ (DB adapter)
                │
         ┌─────────────┐
         │    core/    │ ◄──────────┐
         │ (Node/Graph)│            │
         └─────────────┘            │
                ▲                   │
                │ (data)            │
                │                   │
         ┌─────────────┐            │
         │ mechanisms/ │            │ (uses)
         │  (M01-M13)  │            │
         └─────────────┘            │
                ▲                   │
                │ (compose)         │
                │                   │
         ┌─────────────┐            │
         │  services/  │ ───────────┘
         │ (workspace) │
         └─────────────┘
                ▲
                │ (orchestrate)
                │
         ┌─────────────┐
         │orchestration│
         │  (engine)   │
         └─────────────┘
```

**Dependency rules:**
- ✅ mechanisms → core (pure functions operate on data)
- ✅ services → mechanisms + core (compose mechanisms)
- ✅ orchestration → services + mechanisms + core (coordinate everything)
- ❌ core → mechanisms (NO - data doesn't know about logic)
- ❌ mechanisms → services (NO - mechanisms are lower level)

---

## Migration Strategy

**Phase 1 (Weeks 1-2):**

1. Create core/ (Node, Link, Graph with multi-energy + bitemporal)
2. Create mechanisms/ (multi_energy.py, bitemporal.py as pure functions)
3. Create utils/falkordb_adapter.py (serialization)
4. Unit tests for all above (no integration yet)

**Phase 2 (Week 2):**

5. Refactor consciousness_engine.py to use new components
6. Extract metrics.py (BranchingRatioTracker)
7. Extract websocket_broadcast.py
8. Integration tests

**Phase 3 (Week 2+):**

9. Validate against Phase 1 criteria
10. Phase 2 mechanisms (diffusion, decay, strengthening)

---

## Placement Decisions (From Ada/Nicolas)

**BranchingRatioTracker:**
- ✅ Location: orchestration/metrics.py
- ✅ Rationale: Pure observability, measures outcome not control
- ✅ Does NOT affect consciousness behavior

**WebSocket Broadcasting:**
- ✅ Location: orchestration/websocket_broadcast.py
- ✅ Rationale: Infrastructure/observability, not consciousness logic
- ✅ Dependency injection pattern (engine uses broadcaster, doesn't implement)

**SubEntity:**
- ✅ Status: Completely dynamic (per Nicolas)
- ✅ Location: TBD (likely services/entity.py for entity detection)

---

## Key Architectural Insights

### 1. Separation of Concerns

**core/** = Data (what IS)
**mechanisms/** = Logic (what HAPPENS)
**services/** = Capabilities (what we CAN DO)
**orchestration/** = Coordination (what we DECIDE to do)

### 2. Testing Strategy

**Unit tests:** mechanisms/ (pure functions, no DB)
**Integration tests:** services/ (mechanisms compose correctly)
**System tests:** orchestration/ (full tick loop behavior)

### 3. Stability Gradient

**Most stable:** core/ (changes rarely)
**Stable:** mechanisms/ (changes when understanding improves)
**Moderate:** services/ (changes as capabilities evolve)
**Flexible:** orchestration/ (changes frequently for tuning)

---

## Clean Break: Phase 0 → Phase 1

**This is NOT gradual migration.**

Phase 0 (consciousness_engine.py original) will be replaced entirely.

**Approach:**
1. Build Phase 1 components clean
2. Test Phase 1 in isolation
3. Switch when Phase 1 validated
4. Archive Phase 0 (don't maintain both)

---

**Document Status:** Approved by Ada/Nicolas (2025-10-19)
**Implementation Start:** Phase 1.1.1 (core/node.py)
