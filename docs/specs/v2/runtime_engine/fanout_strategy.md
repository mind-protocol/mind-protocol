---
title: Local Fanout Strategy (Bottom‑Up Topology Adaptation)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/17_local_fanout_strategy.md
depends_on:
  - foundations/diffusion.md
  - runtime_engine/traversal_v2.md
  - emotion/emotion_coloring.md
  - emotion/emotion_complementarity.md
  - emotion/emotion_weighted_traversal.md
---

# Local Fanout Strategy

## 1) Context — Problem we're solving
Traversal at a node with many outgoing links can explode the candidate set; at a sparse node we risk missing the only good route. We need a **local, bottom‑up** strategy (no global topology) that **adapts to out‑degree** and **working‑memory pressure**, while keeping physics intact (single‑energy Eᵢ; links carry no activation). :contentReference[oaicite:1]{index=1}

## 2) Mechanism — What it is
At each visited node, pick a **strategy** from {**Selective**, **Balanced**, **Exhaustive**} using **local fanout**, **WM headroom**, and optionally **task mode**; then compute **cost** on that reduced candidate set and pick the next edge (or distribute across top‑K) for **ΔE** transfer (stride diffusion).

### 2.1 Strategy selection (local + task-mode-aware)
Let `d = outdegree(node)`. Thresholds live in settings and may be nudged by WM capacity (fewer free WM slots → more selective) AND by **task mode** (overrides structure/WM heuristics when enabled).

**Base selection (structure-driven):**
- **High fanout (d > τ_high):** `Selective(top_k = k_high)`
- **Medium (τ_low ≤ d ≤ τ_high):** `Balanced(top_k = round(d/2))`
- **Low (d < τ_low):** `Exhaustive()`
- **WM pressure:** if WM nearly full, reduce `top_k` by ~20–40%.

**Task mode override (optional, feature-flagged):**

When `FANOUT_TASK_MODE_ENABLED=true`, task mode can override the structure-driven heuristic:

| Task Mode | Override Behavior | Rationale |
|-----------|-------------------|-----------|
| **FOCUSED** | Always Selective (top-1 or top-2, even at low fanout) | Narrow attention, ignore distractions |
| **BALANCED** | Use structure-driven heuristics (default behavior) | Let structure guide exploration |
| **DIVERGENT** | Wider selection despite high fanout/WM pressure (top_k × 1.5) | Creative exploration, multiple perspectives |
| **METHODICAL** | Always Exhaustive (check ALL edges, even at hubs) | Thoroughness over efficiency |

**Mode inference:**

Task mode can be:
1. **Explicit:** Set by active goal/task annotation (e.g., `task.mode = "focused"`)
2. **Inferred:** From goal type and entity state:
   - **FOCUSED:** High-urgency goals + single active entity
   - **DIVERGENT:** Exploration goals + multiple active entities
   - **METHODICAL:** Validation/audit goals
   - **BALANCED:** Default (no strong signal)

**Example:**

```python
def select_strategy(node, wm_state, task_mode=None):
    """
    Select fanout strategy based on structure, WM, and optional task mode

    Args:
        node: Current node
        wm_state: Working memory state (capacity, headroom)
        task_mode: Optional task mode override (FOCUSED | BALANCED | DIVERGENT | METHODICAL)

    Returns:
        Strategy enum (SELECTIVE | BALANCED | EXHAUSTIVE) and top_k
    """
    d = len(node.outgoing_links)

    # Task mode override (if enabled and provided)
    if settings.FANOUT_TASK_MODE_ENABLED and task_mode:
        if task_mode == "FOCUSED":
            return (SELECTIVE, min(2, d))  # Top-1 or top-2
        elif task_mode == "DIVERGENT":
            # Wider than structure would suggest
            k = compute_structure_topk(d)
            return (BALANCED, int(k * 1.5))
        elif task_mode == "METHODICAL":
            return (EXHAUSTIVE, d)  # Check everything
        # BALANCED falls through to structure-driven

    # Structure-driven heuristics (default)
    if d > settings.FANOUT_HIGH:
        top_k = settings.SELECTIVE_TOPK
        strategy = SELECTIVE
    elif d >= settings.FANOUT_LOW:
        top_k = round(d / 2)
        strategy = BALANCED
    else:
        top_k = d
        strategy = EXHAUSTIVE

    # WM pressure modulation
    if wm_state.headroom < 0.2:  # Nearly full
        top_k = max(1, int(top_k * 0.6))  # Reduce by 40%

    return (strategy, top_k)
```

**Observability:**

```json
{
    "event": "stride.selection",
    "node_id": "schema_validation",
    "fanout": 12,
    "strategy": "selective",
    "top_k": 2,
    "task_mode": "focused",
    "task_mode_override": true,
    "structure_would_suggest": "balanced",
    "wm_headroom": 0.45
}
```

**No global measures** (clustering, betweenness, …) are used—only **local** fanout, WM headroom, and task mode. :contentReference[oaicite:2]{index=2}

### 2.2 Candidate scoring → cost (on reduced set)
For each candidate edge i→j:
- **Ease from weight:** `ease = exp(log_weight_ij)`
- **Base cost:** `c0 = -log(ease)` (monotone, stable)
- **Emotion gates (cost‑only):**
  - **Resonance:** `m_res = exp(-λ_res * cos(A, Eemo_j))`
  - **Complementarity:** `m_comp = exp(-λ_comp * max(0, -cos(A, Eemo_j)) * g_int * g_ctx)`
- **Goal/task term:** `c_goal` from task fit / φ prior (optional)
- **Final cost:** `c = (c0 + c_goal) * m_res * m_comp`

Pick **min‑cost** edge (K=1) or the **top‑K** (softmax split) if `TOPK_SPLIT.enabled=true`.

> **Important:** do **not** read per‑entity node energy; use only **node.E** (single‑energy) and **metadata** (emotion vector at node/link). This replaces the draft's `link.target.energy[subentity]`. :contentReference[oaicite:3]{index=3}

### 2.3 Optional top‑K split (within‑entity)
When enabled, distribute ΔE over K choices:
```

π_k = softmax( -c_k / T )     # T temperature
ΔE_k = Esrc * α_tick * dt * π_k

```
Else, send all ΔE along the min‑cost edge.

## 3) Why this makes sense
- **Phenomenology:** many options → selective attention; few options → thoroughness.
- **Bio‑inspiration:** cortical competition & sparsity; attention narrows under overload.
- **Systems‑dynamics:** local pruning keeps cost O(d log d) worst case and preserves the **active‑frontier** budget.

## 4) Expected behaviors
- Hubs favor **few** strong exits; chains explore **all** links; mixed graphs show **emergent** bottom‑up adaptation.
- With WM pressure, fanout tightens; when WM frees up, exploration broadens.

## 5) Why this vs alternatives
| Alternative | Issue | This mechanism |
|---|---|---|
| Global topology heuristics | Expensive; brittle; needs full graph | Purely local; robust |
| Fixed K everywhere | Misses structure differences | Adapts to fanout & WM |
| Use per‑entity energies in scoring | Violates single‑energy substrate | Node `E` + metadata only |

## 6) Observability — How & what
- **Events:** `stride.exec` carries per‑edge costs and comp/res multipliers; `tick_frame` can include `{fanout: d, top_k}` for sampled nodes.
- **Metrics:** **Prune rate** (fraction removed by strategy), **K usage** distribution, **selection entropy** at hubs.
- **Dashboards:** a "fanout dial" overlay on nodes; histogram of top‑K sizes vs WM headroom.

## 7) Failure modes & guards
| Risk | Why bad | Guard |
|---|---|---|
| Over‑pruning at hubs | Miss good paths | Floor on `top_k`; ε‑explore |
| WM pressure too aggressive | Starves exploration | Bound reduction; min `top_k` |
| Tie storms | Indecision | Stable tie‑breakers (φ, recency)

## 8) Integration in code
- **Where:** `mechanisms/sub_entity_traversal.py`
  - `select_strategy(node, wm_state) → strategy`
  - `reduce_candidates(strategy, edges) → subset`
  - `score_and_choose(subset) → best | topK`
  - Stage ΔE; emit `stride.exec`
- **Settings:** `FANOUT_{LOW, HIGH}`, `SELECTIVE_TOPK`, `TOPK_SPLIT`.

## 9) Success criteria
- CPU per tick scales with **frontier**, not global E; **prune rate** rises with fanout; task throughput improves at hubs without harming recall.

## 10) Open questions / future
- Learn `top_k(d, WM)` from telemetry; per‑type thresholds (e.g., Task nodes stricter).
