# Fanout Strategy - Gap Analysis

**Date:** 2025-10-22
**Analyst:** Felix (Engineer)
**Spec:** `docs/specs/v2/runtime_engine/fanout_strategy.md`
**Current Implementation:** `orchestration/mechanisms/diffusion_runtime.py` (lines 389-424: `_select_best_outgoing_link`)

---

## Executive Summary

**Status:** ~30% complete - cost-based selection exists, fanout pre-pruning missing

**Verdict:** EXTEND existing selection logic with fanout strategy pre-pruning. Current code:
- ✓ Cost computation (ease, goal, emotion gates)
- ✓ Argmin selection (best link)
- ❌ No fanout-based pruning (evaluates ALL outgoing links)
- ❌ No WM pressure adaptation
- ❌ No top-K split option
- ❌ No strategy selection (Selective/Balanced/Exhaustive)

**Recommendation:** Create `fanout_strategy.py` module with strategy selection and candidate pruning, integrate into `diffusion_runtime.py` link selection.

---

## What Exists (Current Code)

### diffusion_runtime.py: _select_best_outgoing_link()

**Lines 389-424:**
```python
def _select_best_outgoing_link(
    node,
    goal_embedding: Optional[np.ndarray] = None,
    emotion_context: Optional[Dict] = None
) -> Optional['Link']:
    if not node.outgoing_links:
        return None

    # Compute cost for each outgoing link
    link_costs = [
        (_compute_link_cost(link, goal_embedding, emotion_context), link)
        for link in node.outgoing_links  # <-- NO PRUNING
    ]

    # Select link with minimum cost
    best_cost, best_link = min(link_costs, key=lambda x: x[0])

    return best_link
```

**What it does:**
- Evaluates **all** outgoing links
- Computes cost per link (ease + goal + emotion)
- Picks minimum cost (K=1)

**What it doesn't do:**
- Pre-prune based on outdegree
- Adapt to WM pressure
- Support top-K split
- Select strategy (Selective/Balanced/Exhaustive)

**Complexity:** O(d) where d = outdegree
- For hub node with d=1000 outgoing links: computes 1000 costs every time
- Spec wants: prune to top_k=5-10 first, then compute costs on subset

---

## Gap Analysis by Spec Section

### §1 Context - PARTIALLY ADDRESSED

**Spec requirement:**
"Traversal at a node with many outgoing links can explode the candidate set; at a sparse node we risk missing the only good route."

**Current state:**
- High fanout nodes: compute costs for all links (expensive)
- Low fanout nodes: works fine (exhaustive is correct)

**Gap:** No adaptive strategy based on fanout.

**Impact:** Performance degradation at hubs (O(d) → should be O(k) where k << d).

---

### §2.1 Strategy Selection - NOT IMPLEMENTED

**Spec requirement:**
```python
# Based on outdegree d:
if d > τ_high:          # High fanout
    strategy = Selective(top_k = k_high)
elif d >= τ_low:        # Medium
    strategy = Balanced(top_k = round(d/2))
else:                   # Low fanout
    strategy = Exhaustive()

# WM pressure modulation:
if wm_nearly_full:
    top_k *= 0.6  # Reduce by 20-40%
```

**Current code:**
Always exhaustive (all links evaluated).

**Missing components:**

1. **Strategy enum**
   ```python
   class FanoutStrategy(Enum):
       SELECTIVE = "selective"
       BALANCED = "balanced"
       EXHAUSTIVE = "exhaustive"
   ```

2. **Thresholds in settings**
   - `FANOUT_LOW` (default: 3)
   - `FANOUT_HIGH` (default: 10)
   - `SELECTIVE_TOPK` (default: 5)

3. **select_strategy() function**
   ```python
   def select_strategy(node, wm_state) -> FanoutStrategy:
       d = len(node.outgoing_links)
       # ... threshold logic ...
       return strategy
   ```

4. **WM state tracking**
   - Need current WM capacity usage
   - Headroom calculation

**Impact:** Critical - this is the core adaptive behavior.

---

### §2.1 Candidate Pruning - NOT IMPLEMENTED

**Spec requirement:**
"reduce_candidates(strategy, edges) → subset"

After selecting strategy, prune candidate set BEFORE computing costs:

**Selective strategy:**
- Prune to top_k candidates based on **quick heuristic** (e.g., link weight)
- Then compute full cost on subset

**Balanced strategy:**
- Prune to ~50% of edges (round(d/2))

**Exhaustive strategy:**
- Keep all edges

**Current code:**
No pruning - always evaluates all edges.

**Missing:**
```python
def reduce_candidates(
    strategy: FanoutStrategy,
    edges: List[Link],
    top_k: int
) -> List[Link]:
    if strategy == FanoutStrategy.EXHAUSTIVE:
        return edges
    elif strategy == FanoutStrategy.SELECTIVE:
        # Quick pre-filter on weight
        sorted_by_weight = sorted(edges, key=lambda e: e.log_weight, reverse=True)
        return sorted_by_weight[:top_k]
    elif strategy == FanoutStrategy.BALANCED:
        k = max(1, len(edges) // 2)
        sorted_by_weight = sorted(edges, key=lambda e: e.log_weight, reverse=True)
        return sorted_by_weight[:k]
```

**Impact:** High - performance optimization at hubs.

---

### §2.2 Candidate Scoring - COMPLETE

**Spec requirement:**
```python
ease = exp(log_weight_ij)
c0 = -log(ease)
m_res = exp(-λ_res * cos(A, Eemo_j))
m_comp = exp(-λ_comp * max(0, -cos(A, Eemo_j)) * g_int * g_ctx)
c = (c0 + c_goal) * m_res * m_comp
```

**Current code:**
Already implemented in `_compute_link_cost()`.

**No gap - this works.**

---

### §2.3 Top-K Split - NOT IMPLEMENTED

**Spec requirement:**
```python
# When TOPK_SPLIT.enabled=true:
π_k = softmax(-c_k / T)
ΔE_k = E_src * α_tick * dt * π_k
```

Distribute energy across K best links instead of sending all to best link.

**Current code:**
Only supports K=1 (single best link).

**Missing:**

1. **Setting:** `TOPK_SPLIT_ENABLED` (default: False)
2. **K parameter:** `TOPK_SPLIT_K` (default: 3)
3. **Temperature:** `TOPK_SPLIT_TEMPERATURE` (default: 1.0)

4. **top_k_split() function:**
   ```python
   def compute_top_k_split(
       links: List[Link],
       costs: List[float],
       k: int,
       temperature: float
   ) -> List[Tuple[Link, float]]:
       """
       Returns: [(link, energy_fraction), ...]
       where sum(fractions) = 1.0
       """
       top_k_items = sorted(zip(costs, links), key=lambda x: x[0])[:k]
       # Softmax over -cost/T
       logits = [-c / temperature for c, _ in top_k_items]
       probs = softmax(logits)
       return [(link, prob) for (_, link), prob in zip(top_k_items, probs)]
   ```

**Impact:** Medium - nice-to-have for exploration, not critical for core function.

---

### §3-5 Justification - N/A

Philosophy and alternatives - no implementation required.

---

### §6 Observability - PARTIALLY IMPLEMENTED

**Spec requirement:**
- `stride.exec` carries per-edge costs and multipliers
- `tick_frame` includes `{fanout: d, top_k}` for sampled nodes
- Metrics: prune rate, K usage distribution, selection entropy

**Current state:**
- Some event emission exists (TODO comments)
- No fanout-specific metrics

**Missing:**
- Prune rate tracking
- K usage histogram
- Selection entropy at hubs

**Impact:** Low - affects debugging/visualization, not core function.

---

### §7 Failure Modes & Guards - NOT IMPLEMENTED

**Missing guards:**

1. **Over-pruning at hubs**
   - Guard: Floor on `top_k` (min=2)
   - Not implemented

2. **WM pressure too aggressive**
   - Guard: Bound reduction (max 40% reduction)
   - Not implemented

3. **Tie storms**
   - Guard: Stable tie-breakers
   - Partially implemented (deterministic min, but no secondary criteria)

**Impact:** Low - system likely stable without guards, but may have edge cases.

---

### §8 Integration - PARTIALLY WIRED

**Spec requirements:**

1. **Where:** `mechanisms/sub_entity_traversal.py`
   - Current: Logic is in `diffusion_runtime.py` instead
   - Works but location mismatch

2. **Functions:**
   - `select_strategy(node, wm_state) → strategy` - **NOT IMPLEMENTED**
   - `reduce_candidates(strategy, edges) → subset` - **NOT IMPLEMENTED**
   - `score_and_choose(subset) → best | topK` - **PARTIALLY IMPLEMENTED** (best only, no topK)

3. **Settings:** FANOUT_{LOW, HIGH}, SELECTIVE_TOPK, TOPK_SPLIT
   - **NOT IN SETTINGS**

**Impact:** High - integration requires new module and settings.

---

### §9 Success Criteria - CANNOT VERIFY

**Spec criteria:**
- CPU per tick scales with frontier, not global E
- Prune rate rises with fanout
- Task throughput improves at hubs

**Current state:**
No pruning → CPU scales with sum of outdegrees across active nodes.

**Gap:** Success criteria unachievable without fanout pruning.

---

## Priority Gaps (What to fix)

### P0 - Core Fanout Strategy (blocks performance at scale)

1. **Strategy selection logic**
   ```python
   def select_strategy(outdegree: int, wm_headroom: float) -> tuple[FanoutStrategy, int]:
       """Returns (strategy, top_k)"""
       # Threshold logic + WM modulation
   ```

2. **Candidate pruning**
   ```python
   def reduce_candidates(edges: List[Link], strategy: FanoutStrategy, top_k: int) -> List[Link]:
       """Pre-filter edges before cost computation"""
   ```

3. **Settings integration**
   - Add FANOUT_LOW, FANOUT_HIGH, SELECTIVE_TOPK to config

### P1 - WM Pressure Adaptation

4. **WM state tracking**
   - Need current WM usage
   - Compute headroom percentage

5. **top_k reduction**
   ```python
   if wm_headroom < 0.2:  # Less than 20% free
       top_k = int(top_k * 0.6)  # Reduce by 40%
   ```

### P2 - Top-K Split (optional exploration enhancement)

6. **Softmax energy distribution**
   ```python
   def compute_top_k_split(costs, links, k, T) -> List[Tuple[Link, float]]:
       # Softmax over -cost/T
   ```

7. **Multi-target energy staging**
   - Modify `execute_stride_step()` to handle multiple targets

### P3 - Observability & Guards

8. **Prune rate metric**
9. **Floor on top_k**
10. **Tie-breaking improvements**

---

## Recommended Implementation

### New File: fanout_strategy.py

```python
from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FanoutConfig:
    """Configuration for fanout strategy selection."""
    fanout_low: int = 3          # Low fanout threshold
    fanout_high: int = 10         # High fanout threshold
    selective_topk: int = 5       # K for selective strategy
    topk_split_enabled: bool = False  # Enable top-K energy split
    topk_split_k: int = 3        # K for splitting
    topk_split_temperature: float = 1.0  # Softmax temperature
    wm_pressure_enabled: bool = True     # Enable WM modulation
    wm_pressure_threshold: float = 0.2   # Headroom threshold
    wm_pressure_reduction: float = 0.6   # Reduction factor

class FanoutStrategy(Enum):
    SELECTIVE = "selective"
    BALANCED = "balanced"
    EXHAUSTIVE = "exhaustive"

def select_strategy(
    outdegree: int,
    wm_headroom: Optional[float] = None,
    config: Optional[FanoutConfig] = None
) -> Tuple[FanoutStrategy, int]:
    """
    Select fanout strategy based on outdegree and WM pressure.

    Returns:
        (strategy, top_k)
    """
    if config is None:
        config = FanoutConfig()

    # Base strategy from outdegree
    if outdegree > config.fanout_high:
        strategy = FanoutStrategy.SELECTIVE
        top_k = config.selective_topk
    elif outdegree >= config.fanout_low:
        strategy = FanoutStrategy.BALANCED
        top_k = max(1, outdegree // 2)
    else:
        strategy = FanoutStrategy.EXHAUSTIVE
        top_k = outdegree

    # WM pressure modulation
    if config.wm_pressure_enabled and wm_headroom is not None:
        if wm_headroom < config.wm_pressure_threshold:
            top_k = int(top_k * config.wm_pressure_reduction)
            top_k = max(2, top_k)  # Floor at 2

    return strategy, top_k

def reduce_candidates(
    edges: List['Link'],
    strategy: FanoutStrategy,
    top_k: int
) -> List['Link']:
    """
    Prune edges based on strategy.

    Uses quick heuristic (link weight) for pre-filtering.
    Full cost computation happens on reduced set.
    """
    if strategy == FanoutStrategy.EXHAUSTIVE:
        return edges

    # Sort by log_weight (quick heuristic, not full cost)
    sorted_edges = sorted(edges, key=lambda e: e.log_weight, reverse=True)

    # Take top_k
    return sorted_edges[:top_k]
```

### Modified: diffusion_runtime.py

```python
from orchestration.mechanisms.fanout_strategy import select_strategy, reduce_candidates, FanoutConfig

def _select_best_outgoing_link(
    node,
    goal_embedding: Optional[np.ndarray] = None,
    emotion_context: Optional[Dict] = None,
    wm_headroom: Optional[float] = None,
    fanout_config: Optional[FanoutConfig] = None
) -> Optional['Link']:
    """Select best outgoing link with fanout strategy pruning."""

    if not node.outgoing_links:
        return None

    # NEW: Fanout strategy selection
    outdegree = len(node.outgoing_links)
    strategy, top_k = select_strategy(outdegree, wm_headroom, fanout_config)

    # NEW: Prune candidates
    candidates = reduce_candidates(node.outgoing_links, strategy, top_k)

    # Compute cost on REDUCED set
    link_costs = [
        (_compute_link_cost(link, goal_embedding, emotion_context), link)
        for link in candidates  # <-- Now pruned
    ]

    # Select minimum cost
    best_cost, best_link = min(link_costs, key=lambda x: x[0])

    return best_link
```

---

## Estimated Effort

**New code:** ~300 lines

**Breakdown:**
- fanout_strategy.py: ~180 lines (strategy selection, pruning, top-K split)
- diffusion_runtime.py modifications: ~40 lines
- Settings integration: ~20 lines
- Tests: ~120 lines
- Documentation: ~60 lines

**Time estimate:** 4-5 hours

**Blockers:** None - can implement immediately

---

## Test Plan

### Unit Tests (test_fanout_strategy.py)

1. **test_strategy_selection_by_outdegree**
   - d=2 → EXHAUSTIVE, top_k=2
   - d=5 → BALANCED, top_k=2-3
   - d=20 → SELECTIVE, top_k=5

2. **test_wm_pressure_reduction**
   - wm_headroom=0.5 → no reduction
   - wm_headroom=0.1 → 40% reduction

3. **test_candidate_pruning**
   - 100 edges, SELECTIVE → 5 edges (top by weight)
   - 100 edges, BALANCED → 50 edges
   - 5 edges, EXHAUSTIVE → 5 edges

4. **test_top_k_split**
   - Softmax over costs
   - Sum of fractions = 1.0

### Integration Tests

5. **test_hub_performance**
   - Node with 1000 edges
   - Verify only ~5 cost computations (not 1000)

6. **test_chain_thoroughness**
   - Node with 2 edges
   - Verify both evaluated (EXHAUSTIVE)

---

## Summary

Fanout strategy is ~30% implemented:
- ✓ Cost-based selection exists
- ✓ Argmin picking works
- ❌ No fanout-based pruning
- ❌ No strategy selection
- ❌ No WM pressure adaptation
- ❌ No top-K split

**Recommendation:**
Create `fanout_strategy.py` with strategy selection and candidate pruning logic, integrate into `diffusion_runtime.py`. This provides O(k) instead of O(d) performance at hubs while maintaining thoroughness at sparse nodes.

**Priority:** MEDIUM-HIGH - performance optimization that's important at scale but not blocking for basic function. Diffusion v2 can work without it (just slower at hubs).
