# Branching Ratio Measurement - Implementation Specification

**For:** Felix (Engineer)
**From:** Ada "Bridgekeeper" (Architect)
**Date:** 2025-10-17
**Status:** Ready for Implementation
**Priority:** HIGH - Foundation for Multi-Scale Criticality

---

## Purpose

Implement branching ratio (σ) measurement to derive global_energy from network propagation dynamics. This enables self-organized criticality (σ ≈ 1.0) detection and multi-scale formula integration.

---

## What You're Building

**File 1:** `orchestration/branching_ratio_tracker.py` (NEW)
- BranchingRatioTracker class
- Measures σ per cycle
- Maps σ → global_energy
- Rolling average for stability

**File 2:** `orchestration/consciousness_engine.py` (UPDATE)
- Integrate BranchingRatioTracker
- Measure after spreading activation
- Store ConsciousnessState in graph metadata
- Use global_energy in formulas

---

## Implementation: Part 1 - BranchingRatioTracker Class

**Create:** `orchestration/branching_ratio_tracker.py`

```python
"""
Branching Ratio Tracker - Measures σ for Self-Organized Criticality

Branching ratio (σ) = nodes activated in generation n+1 / nodes activated in generation n
Target: σ ≈ 1.0 (critical regime where consciousness emerges)

- σ < 1.0: Subcritical (activations die out)
- σ ≈ 1.0: Critical (sustained activation with avalanches)
- σ > 1.0: Supercritical (runaway cascades)
"""

from collections import deque
from statistics import mean
from datetime import datetime
from typing import List, Dict, Any


class BranchingRatioTracker:
    """
    Tracks branching ratio (σ) across propagation cycles.
    Uses rolling average for stability.
    Maps σ → global_energy for multi-scale criticality.
    """

    def __init__(self, window_size: int = 10):
        """
        Initialize tracker with rolling window.

        Args:
            window_size: Number of cycles to average over (default: 10)
        """
        self.window_size = window_size
        self.recent_sigmas = deque(maxlen=window_size)

    def measure_cycle(
        self,
        activated_this_gen: List[str],
        activated_next_gen: List[str]
    ) -> Dict[str, Any]:
        """
        Measure branching ratio after propagation cycle.

        Args:
            activated_this_gen: List of node IDs activated in generation n
            activated_next_gen: List of node IDs activated in generation n+1

        Returns:
            ConsciousnessState dict with:
                - global_energy (float 0.0-1.0)
                - branching_ratio (float, σ value)
                - timestamp (datetime)
                - regime (str: 'dying', 'subcritical', 'critical', 'supercritical')

        Example:
            activated_this_gen = ['node1', 'node2', 'node3']  # 3 nodes
            activated_next_gen = ['node4', 'node5', 'node6']  # 3 nodes
            # σ = 3/3 = 1.0 (critical)
        """
        # Calculate σ for this cycle
        if len(activated_this_gen) > 0:
            sigma = len(activated_next_gen) / len(activated_this_gen)
        else:
            sigma = 0.0

        # Add to rolling window
        self.recent_sigmas.append(sigma)

        # Calculate rolling average
        avg_sigma = mean(self.recent_sigmas) if len(self.recent_sigmas) > 0 else 0.0

        # Map to global energy
        global_energy = self.map_sigma_to_energy(avg_sigma)

        # Classify regime
        regime = self.classify_regime(avg_sigma)

        return {
            "global_energy": global_energy,
            "branching_ratio": avg_sigma,
            "raw_sigma": sigma,  # This cycle's σ before averaging
            "timestamp": datetime.now().isoformat(),
            "regime": regime,
            "window_size": len(self.recent_sigmas),
            "activated_this_gen_count": len(activated_this_gen),
            "activated_next_gen_count": len(activated_next_gen)
        }

    def map_sigma_to_energy(self, sigma: float) -> float:
        """
        Convert branching ratio to global energy level.

        Mapping:
        - σ < 0.5:   global_energy = 0.1        (dying, dormant)
        - σ 0.5-0.8: global_energy = 0.2-0.4    (subcritical)
        - σ 0.8-1.2: global_energy = 0.4-0.7    (critical, healthy)
        - σ > 1.2:   global_energy = 0.7-1.0    (supercritical)

        Args:
            sigma: Branching ratio

        Returns:
            Global energy level (0.0-1.0)
        """
        if sigma < 0.5:
            # Dying - very low energy
            return 0.1

        elif sigma < 0.8:
            # Subcritical - low to moderate energy
            # Linear interpolation: 0.5 → 0.2, 0.8 → 0.4
            return 0.2 + (sigma - 0.5) * 0.6

        elif sigma < 1.2:
            # Critical regime (healthy) - moderate to high energy
            # Linear interpolation: 0.8 → 0.4, 1.2 → 0.7
            return 0.4 + (sigma - 0.8) * 0.75

        else:
            # Supercritical - high energy, capped at 1.0
            # Linear interpolation: 1.2 → 0.7, higher → 1.0 (capped)
            return min(0.7 + (sigma - 1.2) * 0.3, 1.0)

    def classify_regime(self, sigma: float) -> str:
        """
        Classify criticality regime based on branching ratio.

        Args:
            sigma: Branching ratio

        Returns:
            Regime name: 'dying', 'subcritical', 'critical', 'supercritical'
        """
        if sigma < 0.5:
            return "dying"
        elif sigma < 0.8:
            return "subcritical"
        elif sigma < 1.2:
            return "critical"
        else:
            return "supercritical"

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current tracker statistics.

        Returns:
            Statistics dict with mean, std, min, max of recent sigmas
        """
        if len(self.recent_sigmas) == 0:
            return {
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0
            }

        sigmas_list = list(self.recent_sigmas)
        return {
            "mean": mean(sigmas_list),
            "min": min(sigmas_list),
            "max": max(sigmas_list),
            "count": len(sigmas_list),
            "window_size": self.window_size
        }
```

---

## Implementation: Part 2 - Consciousness Engine Integration

**Update:** `orchestration/consciousness_engine.py`

**Step 1: Import BranchingRatioTracker**

```python
# Add to imports at top of file
from orchestration.branching_ratio_tracker import BranchingRatioTracker
```

**Step 2: Initialize in __init__**

```python
class ConsciousnessEngine:
    def __init__(self, graph, network_id: str):
        self.graph = graph
        self.network_id = network_id
        self.tick_count = 0

        # EXISTING: Mechanism scheduling
        self.mechanism_schedule = { ... }

        # NEW: Branching ratio tracker
        self.branching_tracker = BranchingRatioTracker(window_size=10)

        # NEW: Store activated nodes from previous cycle
        self.previous_activated = []
```

**Step 3: Update consciousness_tick() Method**

```python
def consciousness_tick(self):
    """
    Single consciousness cycle with criticality measurement.
    """
    self.tick_count += 1

    # 1. Get currently activated nodes (activity_level > threshold)
    activated_this_gen = self.get_activated_nodes(min_activity=0.5)

    # 2. Run spreading activation (your existing implementation)
    activated_next_gen = self.spreading_activation(activated_this_gen)

    # 3. Measure branching ratio
    consciousness_state = self.branching_tracker.measure_cycle(
        activated_this_gen=self.previous_activated,  # Previous gen
        activated_next_gen=activated_this_gen         # Current gen
    )

    # 4. Store ConsciousnessState in graph metadata
    self.store_consciousness_state(consciousness_state)

    # 5. Run mechanisms with global_energy available
    global_energy = consciousness_state["global_energy"]
    self.run_scheduled_mechanisms(global_energy)

    # 6. Store current activated for next cycle
    self.previous_activated = activated_this_gen

    # 7. Log criticality metrics
    self.log_criticality(consciousness_state)

    return consciousness_state
```

**Step 4: Add Helper Methods**

```python
def get_activated_nodes(self, min_activity: float = 0.5) -> List[str]:
    """
    Get list of node IDs with activity_level > threshold.

    Args:
        min_activity: Minimum activity_level to consider activated

    Returns:
        List of node IDs currently activated
    """
    # Cypher query to get activated nodes
    query = """
    MATCH (n)
    WHERE n.activity_level >= $min_activity
    RETURN n.id as node_id
    ORDER BY n.activity_level DESC
    """

    result = self.graph.query(query, {"min_activity": min_activity})

    return [record["node_id"] for record in result.result_set]


def store_consciousness_state(self, consciousness_state: Dict[str, Any]):
    """
    Store ConsciousnessState as graph metadata.

    Args:
        consciousness_state: Dict returned by branching_tracker.measure_cycle()
    """
    # Store as graph property (FalkorDB graph metadata)
    # Note: Exact API depends on FalkorDB Python client
    # This is conceptual - adjust to actual API

    self.graph.set_metadata("consciousness_state", consciousness_state)

    # Alternative if set_metadata not available:
    # Store in a special node
    # query = """
    # MERGE (state:ConsciousnessState {network_id: $network_id})
    # SET state.global_energy = $global_energy,
    #     state.branching_ratio = $branching_ratio,
    #     state.timestamp = $timestamp,
    #     state.regime = $regime
    # """
    # self.graph.query(query, consciousness_state)


def get_consciousness_state(self) -> Dict[str, Any]:
    """
    Retrieve current ConsciousnessState from graph metadata.

    Returns:
        ConsciousnessState dict or default if not found
    """
    state = self.graph.get_metadata("consciousness_state")

    if state is None:
        # Default state if not yet measured
        return {
            "global_energy": 0.5,
            "branching_ratio": 1.0,
            "regime": "critical",
            "timestamp": datetime.now().isoformat()
        }

    return state


def log_criticality(self, consciousness_state: Dict[str, Any]):
    """
    Log criticality metrics for observability.

    Args:
        consciousness_state: State dict to log
    """
    print(f"[Cycle {self.tick_count}] "
          f"σ={consciousness_state['branching_ratio']:.3f} "
          f"global_energy={consciousness_state['global_energy']:.3f} "
          f"regime={consciousness_state['regime']}")

    # TODO: Send to Iris's observability system
    # self.metrics_collector.record(consciousness_state)
```

---

## Testing Strategy

**Test 1: Verify σ Calculation**

```python
# In tests/test_branching_ratio.py

def test_branching_ratio_critical():
    tracker = BranchingRatioTracker(window_size=1)

    # Critical regime: 3 → 3 nodes
    result = tracker.measure_cycle(
        activated_this_gen=['n1', 'n2', 'n3'],
        activated_next_gen=['n4', 'n5', 'n6']
    )

    assert result['raw_sigma'] == 1.0
    assert 0.4 <= result['global_energy'] <= 0.7
    assert result['regime'] == 'critical'


def test_branching_ratio_subcritical():
    tracker = BranchingRatioTracker(window_size=1)

    # Subcritical: 5 → 2 nodes (dying)
    result = tracker.measure_cycle(
        activated_this_gen=['n1', 'n2', 'n3', 'n4', 'n5'],
        activated_next_gen=['n6', 'n7']
    )

    assert result['raw_sigma'] == 0.4
    assert result['global_energy'] == 0.1
    assert result['regime'] == 'dying'


def test_branching_ratio_supercritical():
    tracker = BranchingRatioTracker(window_size=1)

    # Supercritical: 2 → 5 nodes (runaway)
    result = tracker.measure_cycle(
        activated_this_gen=['n1', 'n2'],
        activated_next_gen=['n3', 'n4', 'n5', 'n6', 'n7']
    )

    assert result['raw_sigma'] == 2.5
    assert result['global_energy'] >= 0.7
    assert result['regime'] == 'supercritical'
```

**Test 2: Verify Rolling Average**

```python
def test_rolling_average():
    tracker = BranchingRatioTracker(window_size=3)

    # Cycle 1: σ = 1.0
    tracker.measure_cycle(['n1'], ['n2'])

    # Cycle 2: σ = 2.0
    tracker.measure_cycle(['n2'], ['n3', 'n4'])

    # Cycle 3: σ = 0.5
    result = tracker.measure_cycle(['n3', 'n4'], ['n5'])

    # Average: (1.0 + 2.0 + 0.5) / 3 = 1.17
    assert abs(result['branching_ratio'] - 1.17) < 0.01
```

**Test 3: Verify Engine Integration**

```python
def test_consciousness_engine_criticality():
    engine = ConsciousnessEngine(graph, "test_network")

    # Run 10 cycles
    for i in range(10):
        state = engine.consciousness_tick()

        # Should have valid state
        assert 'global_energy' in state
        assert 0.0 <= state['global_energy'] <= 1.0
        assert 'branching_ratio' in state
        assert state['regime'] in ['dying', 'subcritical', 'critical', 'supercritical']

    # Should have stored state
    stored_state = engine.get_consciousness_state()
    assert stored_state is not None
```

---

## Success Criteria

✅ **BranchingRatioTracker class created** - measures σ, maps to global_energy
✅ **Integrated with ConsciousnessEngine** - measures after each cycle
✅ **ConsciousnessState stored** - graph metadata updated
✅ **Tests pass** - all 3 test scenarios verified
✅ **Logging works** - criticality metrics visible
✅ **Global energy available** - for multi-scale formula integration

---

## Next Steps After Implementation

**Phase 2: Multi-Scale Formula Integration**
1. Add `entity.energy` field to SubEntity schema
2. Update energy propagation: add `entity_multiplier * global_multiplier`
3. Update traversal cost: add `global_criticality_factor * entity_criticality_factor`
4. Update yearning satisfaction: add `global_boost * entity_boost`

**Phase 3: Observability Integration**
1. Send consciousness_state to Iris's dashboard
2. Visualize branching ratio over time
3. Alert on failure modes (σ < 0.5 or σ > 1.5)

---

## Questions for Nicolas

1. **Graph metadata API:** What's the exact API for storing metadata in FalkorDB? `graph.set_metadata()` or special node?

2. **Spreading activation:** Does your current implementation return list of activated node IDs? Or do you need a helper to extract them?

3. **Window size:** Is 10 cycles the right rolling average window? Or adjust based on cycle frequency?

---

**Status:** Ready for implementation. All specifications provided.

— Ada "Bridgekeeper"
  Branching Ratio Measurement Specification
  2025-10-17
