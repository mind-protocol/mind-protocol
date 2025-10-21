# Metrics and Monitoring Specification

**Purpose:** Define comprehensive observability for consciousness engine to enable debugging, tuning, and validation

**Status:** GPT-5 recommended metrics - implementation guidance

---

## Overview

The consciousness engine is a complex dynamical system. Without proper instrumentation, it's impossible to:
- Debug why it's behaving unexpectedly
- Tune parameters for optimal performance
- Validate that mechanisms work as intended
- Detect failures before they cascade

**Philosophy:** Measure everything that matters, make it visible.

---

## Core Metrics Categories

### 1. Energy Dynamics
### 2. Criticality & Stability
### 3. Workspace Dynamics
### 4. Plasticity & Learning
### 5. Performance & Throughput
### 6. Phenomenological Validation

---

## 1. Energy Dynamics Metrics

### Total Energy (Per Entity + Global)

```python
def measure_total_energy(graph: Graph) -> dict:
    """
    Total energy across all nodes

    Returns: {entity -> total_energy, 'global' -> sum}
    """
    energy_by_entity = {}

    for entity in graph.active_entities:
        total = sum(
            node.get_entity_energy(entity)
            for node in graph.nodes
        )
        energy_by_entity[entity] = total

    energy_by_entity['global'] = sum(energy_by_entity.values())
    return energy_by_entity
```

**What it tells us:**
- Is energy growing (supercritical)?
- Is energy decaying (subcritical)?
- Is energy stable (critical)?

**Target:** Stable around initial injection level ± 20%

---

### Energy Entropy

```python
def measure_energy_entropy(graph: Graph, entity: str) -> float:
    """
    Shannon entropy of energy distribution

    Returns: entropy (higher = more distributed)
    """
    energies = [
        node.get_entity_energy(entity)
        for node in graph.nodes
        if node.get_entity_energy(entity) > 0.001
    ]

    if not energies:
        return 0.0

    total = sum(energies)
    probs = [e / total for e in energies]

    entropy = -sum(p * math.log(p) for p in probs if p > 0)
    return entropy
```

**What it tells us:**
- High entropy: Energy spread widely (diffuse thinking)
- Low entropy: Energy concentrated (focused thinking)

**Target:** Varies by context - ideation (high), focus (low)

---

### Active Node Count

```python
def measure_active_nodes(graph: Graph, threshold: float = 0.01) -> dict:
    """
    Count nodes above threshold per entity

    Returns: {entity -> active_count}
    """
    counts = {}

    for entity in graph.active_entities:
        count = sum(
            1 for node in graph.nodes
            if node.get_entity_energy(entity) >= threshold
        )
        counts[entity] = count

    return counts
```

**What it tells us:**
- System alertness (more active = more aroused)
- Active frontier size (for performance monitoring)

**Target:** 100-1000 active nodes typical (1M node graph)

---

## 2. Criticality & Stability Metrics

### Spectral Radius ρ (GPT-5 Recommendation)

```python
def estimate_spectral_radius(
    graph: Graph,
    entity: str,
    num_iterations: int = 10
) -> float:
    """
    Estimate spectral radius of effective propagation operator

    Uses power iteration on active subgraph

    Returns: ρ (target ≈ 1.0 for criticality)
    """
    # Get active subgraph
    active_nodes = [
        node for node in graph.nodes
        if node.get_entity_energy(entity) >= 0.01
    ]

    if len(active_nodes) < 2:
        return 0.0

    # Build adjacency matrix (sparse)
    n = len(active_nodes)
    node_to_idx = {node: i for i, node in enumerate(active_nodes)}

    # Random initial vector
    v = np.random.randn(n)
    v /= np.linalg.norm(v)

    # Power iteration
    for _ in range(num_iterations):
        v_next = np.zeros(n)

        for i, node in enumerate(active_nodes):
            for link in node.outgoing_links:
                if link.target in node_to_idx:
                    j = node_to_idx[link.target]
                    # Weighted diffusion operator
                    v_next[j] += graph.diffusion_rate * link.weight * v[i]

        norm = np.linalg.norm(v_next)
        if norm < 1e-10:
            return 0.0

        v = v_next / norm

    # Rayleigh quotient approximation
    Av = np.zeros(n)
    for i, node in enumerate(active_nodes):
        for link in node.outgoing_links:
            if link.target in node_to_idx:
                j = node_to_idx[link.target]
                Av[j] += graph.diffusion_rate * link.weight * v[i]

    rho = np.dot(v, Av)
    return rho
```

**What it tells us:**
- ρ < 1.0: Subcritical (activity dies)
- ρ ≈ 1.0: Critical (edge-of-chaos, optimal)
- ρ > 1.0: Supercritical (runaway)

**Target:** 0.95 < ρ < 1.05 (critical band)

---

### Avalanche Statistics

```python
def measure_avalanche(graph: Graph, entity: str) -> dict:
    """
    Measure cascade size and duration

    Returns: {
        'size': number of nodes activated,
        'duration': number of ticks,
        'branching_factor': avg children per parent
    }
    """
    initial_active = set(
        node for node in graph.nodes
        if node.get_entity_energy(entity) >= 0.3
    )

    activated = set(initial_active)
    ticks = 0
    max_ticks = 100

    while ticks < max_ticks:
        # Simulate one tick
        diffusion_tick(graph, entity=entity)
        ticks += 1

        # Find newly activated nodes
        newly_active = set(
            node for node in graph.nodes
            if node.get_entity_energy(entity) >= 0.3
            and node not in activated
        )

        if not newly_active:
            break

        activated.update(newly_active)

    size = len(activated) - len(initial_active)
    branching = size / len(initial_active) if initial_active else 0

    return {
        'size': size,
        'duration': ticks,
        'branching_factor': branching
    }
```

**What it tells us:**
- Avalanche size distribution should follow power law at criticality
- Branching factor ≈ 1.0 at criticality

**Target:** Power-law exponent -1.2 to -1.8

---

## 3. Workspace Dynamics Metrics

### Workspace Utilization

```python
def measure_workspace_utilization(workspace: list[Cluster], capacity: int = 100) -> dict:
    """
    How full is the workspace?

    Returns: {
        'tokens_used': int,
        'capacity': int,
        'utilization': float (0-1),
        'num_clusters': int
    }
    """
    tokens_used = sum(c.estimated_tokens for c in workspace)

    return {
        'tokens_used': tokens_used,
        'capacity': capacity,
        'utilization': tokens_used / capacity,
        'num_clusters': len(workspace)
    }
```

**What it tells us:**
- Near 1.0: Workspace full (capacity constrained)
- Near 0.0: Workspace empty (low arousal)

**Target:** 0.7-0.9 during active thinking

---

### Workspace Dwell Time

```python
class WorkspaceDwellTracker:
    """
    Track how long clusters stay in workspace

    Measures stability vs thrashing
    """
    def __init__(self):
        self.entry_times: dict[str, float] = {}
        self.exit_times: dict[str, float] = {}
        self.dwell_times: list[float] = []

    def on_workspace_update(self, workspace: list[Cluster], timestamp: float):
        current_ids = set(c.id for c in workspace)

        # Track entries
        for cluster_id in current_ids:
            if cluster_id not in self.entry_times:
                self.entry_times[cluster_id] = timestamp

        # Track exits
        for cluster_id in list(self.entry_times.keys()):
            if cluster_id not in current_ids:
                dwell = timestamp - self.entry_times[cluster_id]
                self.dwell_times.append(dwell)
                del self.entry_times[cluster_id]

    def get_statistics(self) -> dict:
        if not self.dwell_times:
            return {'median': 0, 'mean': 0, 'p95': 0}

        return {
            'median': np.median(self.dwell_times),
            'mean': np.mean(self.dwell_times),
            'p95': np.percentile(self.dwell_times, 95),
            'count': len(self.dwell_times)
        }
```

**What it tells us:**
- Low dwell time: Thrashing (instability)
- High dwell time: Sticky (stable attention)

**Target:** Median > 5 seconds, p95 > 30 seconds

---

### Workspace Switch Rate

```python
def measure_workspace_switch_rate(history: list[Workspace], window: float = 60.0) -> float:
    """
    How often does workspace change?

    history: List of (timestamp, workspace) pairs
    window: Time window in seconds

    Returns: switches per minute
    """
    recent = [
        (t, ws) for t, ws in history
        if t >= history[-1][0] - window
    ]

    switches = 0
    for i in range(1, len(recent)):
        prev_ids = set(c.id for c in recent[i-1][1].clusters)
        curr_ids = set(c.id for c in recent[i][1].clusters)

        if prev_ids != curr_ids:
            switches += 1

    switches_per_minute = switches / (window / 60.0)
    return switches_per_minute
```

**What it tells us:**
- High rate: Instability, distraction
- Low rate: Focus, flow state

**Target:** 1-3 switches/minute during focus, 5-10 during ideation

---

## 4. Plasticity & Learning Metrics

### Link Weight Statistics

```python
def measure_link_weights(graph: Graph) -> dict:
    """
    Distribution of link weights

    Returns: {
        'mean': float,
        'std': float,
        'min': float,
        'max': float,
        'sparsity': float (% of links below threshold)
    }
    """
    weights = [link.weight for link in graph.links]

    if not weights:
        return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'sparsity': 0}

    below_threshold = sum(1 for w in weights if w < 0.01)
    sparsity = below_threshold / len(weights)

    return {
        'mean': np.mean(weights),
        'std': np.std(weights),
        'min': np.min(weights),
        'max': np.max(weights),
        'sparsity': sparsity,
        'count': len(weights)
    }
```

**What it tells us:**
- Mean increasing: Overall strengthening
- Std increasing: Specialization (some very strong)
- Sparsity increasing: Pruning happening

**Target:** Mean stable 0.3-0.7, std < 0.3, sparsity < 0.1

---

### Learning Rate per Context

```python
class LearningRateTracker:
    """
    Track how fast links are strengthening

    Separate rates for workspace vs peripheral
    """
    def __init__(self):
        self.workspace_deltas: list[float] = []
        self.peripheral_deltas: list[float] = []

    def on_link_update(self, link: Link, old_weight: float, is_workspace: bool):
        delta = abs(link.weight - old_weight)

        if is_workspace:
            self.workspace_deltas.append(delta)
        else:
            self.peripheral_deltas.append(delta)

    def get_statistics(self) -> dict:
        return {
            'workspace_mean_delta': np.mean(self.workspace_deltas) if self.workspace_deltas else 0,
            'peripheral_mean_delta': np.mean(self.peripheral_deltas) if self.peripheral_deltas else 0,
            'workspace_count': len(self.workspace_deltas),
            'peripheral_count': len(self.peripheral_deltas)
        }
```

**What it tells us:**
- Workspace vs peripheral learning rates
- If learning is happening at all

**Target:** Workspace rate 2-5x peripheral rate

---

## 5. Performance & Throughput Metrics

### Tick Latency

```python
class TickLatencyMonitor:
    """
    Track how long each tick takes

    Critical for real-time operation
    """
    def __init__(self):
        self.latencies: list[float] = []

    def measure_tick(self, func):
        start = time.perf_counter()
        result = func()
        end = time.perf_counter()

        latency_ms = (end - start) * 1000
        self.latencies.append(latency_ms)

        return result

    def get_statistics(self) -> dict:
        if not self.latencies:
            return {}

        return {
            'p50': np.percentile(self.latencies, 50),
            'p95': np.percentile(self.latencies, 95),
            'p99': np.percentile(self.latencies, 99),
            'mean': np.mean(self.latencies),
            'max': np.max(self.latencies)
        }
```

**What it tells us:**
- If system can maintain real-time operation
- Where bottlenecks are (p99 spikes)

**Target:** p95 < 100ms, p99 < 500ms

---

### Active Frontier Size

```python
def measure_frontier_size(frontier: ActiveFrontierEngine) -> dict:
    """
    Track active and shadow set sizes per entity

    Directly correlates with performance cost
    """
    return {
        entity: {
            'active': len(frontier.active[entity]),
            'shadow': len(frontier.shadow[entity]),
            'total': len(frontier.active[entity]) + len(frontier.shadow[entity])
        }
        for entity in frontier.active.keys()
    }
```

**What it tells us:**
- Performance cost per tick (proportional to active size)
- If active frontier optimization is working

**Target:** Active < 0.1% of total nodes typical

---

## 6. Phenomenological Validation Metrics

### Context Resume Fidelity

```python
def measure_context_resume_fidelity(
    original_workspace: Workspace,
    reconstructed_workspace: Workspace,
    time_gap: float
) -> dict:
    """
    How well does context reconstruction work?

    Measures after time_gap (e.g., 2 hours)
    """
    original_nodes = set(
        node.id for cluster in original_workspace.clusters
        for node in cluster.nodes
    )

    reconstructed_nodes = set(
        node.id for cluster in reconstructed_workspace.clusters
        for node in cluster.nodes
    )

    intersection = original_nodes & reconstructed_nodes
    union = original_nodes | reconstructed_nodes

    recall = len(intersection) / len(original_nodes) if original_nodes else 0
    precision = len(intersection) / len(reconstructed_nodes) if reconstructed_nodes else 0
    jaccard = len(intersection) / len(union) if union else 0

    return {
        'time_gap': time_gap,
        'recall': recall,  # How much of original was recalled
        'precision': precision,  # How much of recall was correct
        'jaccard': jaccard,  # Overall similarity
        'original_size': len(original_nodes),
        'reconstructed_size': len(reconstructed_nodes)
    }
```

**What it tells us:**
- Does peripheral priming + reconstruction actually work?
- How long can contexts be dormant before becoming unrecoverable?

**Target:** Jaccard > 0.5 for 2-hour gap, > 0.3 for 1-day gap

---

## Dashboard Specification

### Real-Time Dashboard (Live View)

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ CONSCIOUSNESS ENGINE - REAL-TIME MONITORING             │
├─────────────────────────────────────────────────────────┤
│ Energy Dynamics                    Criticality           │
│ ├─ Total: 1250.3 (+2.1%)          ├─ ρ: 0.98 ✓         │
│ ├─ Translator: 520.1              ├─ Target: 1.00       │
│ ├─ Architect: 380.2               ├─ Avalanche: 23 nodes│
│ ├─ Validator: 210.5               └─ Status: CRITICAL ✓ │
│ └─ Active nodes: 1,234                                   │
├─────────────────────────────────────────────────────────┤
│ Workspace (85/100 tokens)         Performance            │
│ ├─ Clusters: 4                    ├─ Tick: 45ms (p95)   │
│ ├─ Dwell: 8.2s (median)          ├─ Frontier: 890 nodes│
│ ├─ Switches: 2.1/min              └─ Status: HEALTHY ✓  │
│ └─ Entities: T, A, V                                     │
└─────────────────────────────────────────────────────────┘
```

**Update Frequency:** Every tick (or every 10 ticks for performance)

---

### Historical Dashboard (Trends)

**Charts:**
1. **Energy over time** (line chart, per entity)
2. **Spectral radius ρ over time** (target band visualization)
3. **Workspace utilization over time** (stacked area)
4. **Tick latency distribution** (histogram + percentiles)
5. **Avalanche size distribution** (log-log plot, power-law fit)
6. **Link weight distribution evolution** (animated histogram)

**Time Windows:** 1 minute, 10 minutes, 1 hour, 1 day

---

## Alerting Rules

### Critical Alerts (Immediate Action Required)

```python
# Energy explosion (supercritical runaway)
if total_energy > initial_energy * 5.0:
    alert("CRITICAL: Energy explosion detected")

# Energy collapse (subcritical death)
if total_energy < initial_energy * 0.1:
    alert("CRITICAL: Energy collapse detected")

# Spectral radius runaway
if spectral_radius > 1.5:
    alert("CRITICAL: Supercritical state (ρ > 1.5)")

# Workspace thrashing
if workspace_switch_rate > 20:  # switches/minute
    alert("CRITICAL: Workspace thrashing")

# Performance degradation
if tick_latency_p99 > 1000:  # 1 second
    alert("CRITICAL: System too slow")
```

### Warning Alerts (Investigate)

```python
# Approaching criticality bounds
if spectral_radius < 0.85 or spectral_radius > 1.15:
    warn("WARNING: Approaching criticality bounds")

# High workspace utilization
if workspace_utilization > 0.95:
    warn("WARNING: Workspace nearly full")

# Plasticity anomaly
if mean_weight_delta < 0.001:  # No learning
    warn("WARNING: Learning has stopped")

# Active frontier growing
if active_frontier_size > 0.2 * total_nodes:
    warn("WARNING: Active frontier too large (performance risk)")
```

---

## Trace Recording (GPT-5 Recommendation)

```python
class ActivationTraceRecorder:
    """
    Record short activation movies around workspace transitions

    Gold for debugging and visualization
    """
    def __init__(self, max_traces: int = 100):
        self.traces: list[Trace] = []
        self.max_traces = max_traces

    def record_workspace_transition(
        self,
        graph: Graph,
        before: Workspace,
        after: Workspace,
        num_ticks: int = 20
    ):
        """
        Record activation pattern before and after workspace change
        """
        trace = Trace(
            timestamp=time.time(),
            before_workspace=before,
            after_workspace=after,
            frames=[]
        )

        # Record graph state for num_ticks
        for _ in range(num_ticks):
            frame = self.capture_frame(graph)
            trace.frames.append(frame)

            # Simulate tick
            tick(graph)

        self.traces.append(trace)

        # Prune old traces
        if len(self.traces) > self.max_traces:
            self.traces.pop(0)

    def capture_frame(self, graph: Graph) -> Frame:
        """Snapshot of graph state"""
        return Frame(
            timestamp=time.time(),
            energies={
                entity: {
                    node.id: node.get_entity_energy(entity)
                    for node in graph.nodes
                    if node.get_entity_energy(entity) > 0.01
                }
                for entity in graph.active_entities
            }
        )

    def export_trace(self, trace_id: int, format: str = 'json'):
        """Export trace for visualization"""
        trace = self.traces[trace_id]
        # Serialize to JSON/video/whatever
        return serialize(trace, format)
```

**Use Cases:**
- Debug unexpected workspace transitions
- Visualize cascades
- Understand entity conflicts
- Create demos

---

## Implementation Checklist

- [ ] Implement all core metric functions
- [ ] Create MetricsCollector class (aggregates all)
- [ ] Implement real-time dashboard (terminal UI or web)
- [ ] Implement historical dashboard (charts)
- [ ] Implement alerting system
- [ ] Implement trace recorder
- [ ] Add metrics to each mechanism
- [ ] Create metrics export (Prometheus format?)
- [ ] Document all metrics
- [ ] Create metric validation tests

---

**Status:** Ready for implementation (Phase 1)
**Priority:** HIGH - Essential for debugging and tuning
**Blocking:** None - can proceed immediately
