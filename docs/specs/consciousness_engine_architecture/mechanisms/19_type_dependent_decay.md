# Mechanism 19: Type-Dependent Decay Rates

**Type:** Energy Dynamics
**Phase:** 3 (Core consciousness mechanisms)
**Status:** Specified
**Source:** Discussion D014 - Separate Energy vs Weight Decay
**Author:** Nicolas (architectural guidance), Luca (specification)

---

## Purpose

Different node and link types have different decay rates. Memory nodes decay slowly ("sticks"), Task nodes decay fast (temporary). This creates type-specific persistence characteristics without manual tuning per-instance.

---

## Architectural Principle

**Decay varies by TYPE, not globally:**

- Memory nodes: very slow decay (knowledge persists)
- Task nodes: fast decay (temporary structures)
- Realization nodes: slow decay (insights persist)
- Trigger nodes: moderate decay (contextual)

**Plus: Separate energy decay vs weight decay**

**Nicolas's guidance:**
> "Energy decay and weight decay should NOT decay at same rate. It should depend on the node or link type. Memory should decay slower than tasks. Memory sticks."

---

## Core Mechanism

### Dual Decay System

**Every node has TWO decay rates:**
1. **δ_state** - How fast energy fades (working memory)
2. **δ_weight** - How fast link weights decay (long-term memory)

```python
class Node:
    def __init__(self, node_type):
        self.type = node_type

        # Get type-specific decay rates from schema
        decay_config = get_decay_config(node_type)

        self.energy_decay_rate = decay_config.delta_state
        self.weight_decay_rate = decay_config.delta_weight

    def apply_decay(self, dt):
        """
        Apply both energy and weight decay

        Energy decays at delta_state rate
        Outgoing link weights decay at delta_weight rate
        """

        # Energy decay (fast)
        for entity in self.energy:
            self.energy[entity] *= (1 - self.energy_decay_rate * dt)

        # Weight decay (slow)
        for link in self.outgoing_links:
            link.weight *= (1 - self.weight_decay_rate * dt)
```

---

## Type-Specific Decay Configuration

**Decay rates by node type:**

```python
NODE_TYPE_DECAY_RATES = {
    # PERSISTENT TYPES (slow decay)
    "Memory": {
        "delta_state": 0.05 / 3600,   # Energy: 5% per hour
        "delta_weight": 0.0001 / 3600, # Weights: 0.01% per hour (very slow)
        "rationale": "Memories stick - persist for weeks"
    },

    "Realization": {
        "delta_state": 0.1 / 3600,     # Energy: 10% per hour
        "delta_weight": 0.0005 / 3600, # Weights: 0.05% per hour
        "rationale": "Realizations fade from attention but connections persist"
    },

    "Principle": {
        "delta_state": 0.1 / 3600,
        "delta_weight": 0.0002 / 3600,
        "rationale": "Principles are foundational - very persistent"
    },

    # TEMPORARY TYPES (fast decay)
    "Task": {
        "delta_state": 0.5 / 3600,     # Energy: 50% per hour
        "delta_weight": 0.01 / 3600,   # Weights: 1% per hour
        "rationale": "Tasks are temporary - fade quickly when not active"
    },

    "Question": {
        "delta_state": 0.3 / 3600,
        "delta_weight": 0.005 / 3600,
        "rationale": "Questions urgent but temporary"
    },

    # MODERATE TYPES
    "Trigger": {
        "delta_state": 0.2 / 3600,
        "delta_weight": 0.001 / 3600,
        "rationale": "Triggers are contextual - moderate persistence"
    },

    "Concept": {
        "delta_state": 0.1 / 3600,
        "delta_weight": 0.0003 / 3600,
        "rationale": "Concepts persist but fade without reinforcement"
    },

    # DEFAULT for unknown types
    "default": {
        "delta_state": 0.1 / 3600,
        "delta_weight": 0.001 / 3600,
        "rationale": "Generic moderate decay"
    }
}
```

**Typical ratios:**
- Memory: `delta_weight = 0.002 × delta_state` (500x slower)
- Task: `delta_weight = 0.02 × delta_state` (50x slower)
- Realization: `delta_weight = 0.005 × delta_state` (200x slower)

---

## Link Type Decay

**Links also have type-dependent decay:**

```python
LINK_TYPE_DECAY_RATES = {
    "ENABLES": {
        "delta_weight": 0.0005 / 3600,
        "rationale": "Enabling relationships persist"
    },

    "BLOCKS": {
        "delta_weight": 0.002 / 3600,
        "rationale": "Blocking relationships decay faster (temporary obstacles)"
    },

    "TRIGGERED_BY": {
        "delta_weight": 0.001 / 3600,
        "rationale": "Trigger relationships moderate persistence"
    },

    "RELATES_TO": {
        "delta_weight": 0.0003 / 3600,
        "rationale": "Semantic relationships very persistent"
    },

    # etc. for all link types
}
```

---

## Phenomenological Justification

**Why Memory sticks:**

Real-world scenario: "I think about consciousness substrate architecture for 2 hours, then don't touch it for 3 days."

**With single decay rate (broken):**
- If `decay_rate = 0.1/hour`: Energy gone in hours ✓, weights gone in days ✗
  - Problem: Can't resume context after 3 days - connections decayed
- If `decay_rate = 0.001/hour`: Energy lingers for days ✗, weights persist ✓
  - Problem: Can't let go of thoughts - activation persists too long

**With type-dependent dual decay (correct):**
- Memory nodes:
  - `delta_state = 0.05/hour`: Energy clears in ~20 hours ✓
  - `delta_weight = 0.0001/hour`: Weights preserve for weeks ✓
- Task nodes:
  - `delta_state = 0.5/hour`: Energy clears in ~2 hours ✓
  - `delta_weight = 0.01/hour`: Weights fade in days ✓

**Result:** Can let go of active thinking (energy clears) but remember the knowledge (weights persist).

---

## Working Memory Span

**CRITICAL: Working memory span is NOT determined by energy decay alone**

**Nicolas's guidance:**
> "Working memory span depends on the algorithm of the sub-entity traversal."

**Decay sets the SUBSTRATE:**
- Energy decay creates time window for potential traversal
- Sub-entity traversal algorithm determines ACTUAL working memory

**Example:**
- Energy decays to 10% baseline in 2 hours
- But sub-entity might:
  - Revisit nodes within 10 minutes (keeps them "in working memory")
  - Or not revisit for 3 hours (falls out of working memory despite some residual energy)

**Working memory = traversal pattern, not just decay rate** [node_traversal_determines_memory_span: very useful]

---

## Timescale Examples

**Scenario: Deep work session (3 hours), then 3-day break**

**Memory node:**
- Hour 0: `energy = 1.0`, `weight = 1.0`
- Hour 3: `energy = 0.86` (still warm), `weight = 0.9997` (barely decayed)
- Hour 75 (3 days): `energy = 0.02` (cold), `weight = 0.993` (still strong)
- **Result:** Can resume context after break ✓

**Task node:**
- Hour 0: `energy = 1.0`, `weight = 1.0`
- Hour 3: `energy = 0.22` (cooling fast), `weight = 0.97` (decaying)
- Hour 75: `energy ≈ 0.0` (gone), `weight = 0.48` (half strength)
- **Result:** Task fades appropriately for temporary structure ✓

---

## Integration Points

**Interacts with:**
- **Mechanism 08** (Energy Decay) - extends with type-dependence
- **Mechanism 09** (Link Strengthening) - weights that strengthen also decay at type-specific rates
- **Mechanism 05** (Sub-entity Mechanics) - traversal patterns determine actual working memory span
- **Mechanism 18** (Incomplete Node Healing) - incomplete nodes might have different decay

---

## Parameters

**Global:**
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `decay_rate_multiplier` | 1.0 | [0.5, 2.0] | Global multiplier for all decay rates |
| `energy_weight_ratio_default` | 100 | [10, 1000] | Default ratio `delta_state / delta_weight` |

**Per-type:** See `NODE_TYPE_DECAY_RATES` and `LINK_TYPE_DECAY_RATES` above

---

## Implementation Notes

**For Felix:**
- Store `energy_decay_rate` and `weight_decay_rate` per node/link
- Load from type-based config on creation
- Apply in decay tick loop (already exists for global decay)
- Type config stored in separate JSON file for easy tuning

**Performance:**
- No additional overhead (same decay loop, just different rates per element)
- Type lookup on node creation only (not every tick)

---

## Validation Criteria

**Mechanism works correctly if:**
1. ✅ Memory nodes retain weights for weeks (observable in tests)
2. ✅ Task nodes decay within days
3. ✅ Energy decays faster than weights for all types
4. ✅ Type-specific decay follows configured rates
5. ✅ Can resume context after 3-day break (Memory nodes) but not Tasks

---

## Tuning Guide

**How to adjust decay rates:**

1. **Test scenario:** "Work 3 hours, break 3 days, return"
2. **Measure:** Can I resume context? Do temporary structures clear?
3. **Adjust:**
   - If can't resume → reduce `delta_weight` for Memory
   - If temporary structures persist → increase `delta_weight` for Task
   - If thoughts linger too long → increase `delta_state`
   - If thoughts fade too fast → reduce `delta_state`

**Start with defaults, tune based on phenomenology.**

---

**Status:** Ready for implementation
**Next Steps:** Modify Mechanism 08 (Energy Decay) to support type-dependent rates
