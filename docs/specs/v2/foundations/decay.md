# Energy & Weight Decay (Forgetting with Control)

## 1) Context — The problem we’re solving
Without forgetting, activation accumulates and the system saturates; with too‑much forgetting, nothing persists. We need **exponential decay** for **activation** and a **much slower** decay for **weights**, both **type‑dependent**, with ρ‑control using decay as a primary lever. All on the **single‑energy** substrate (no per‑entity buffers on nodes). :contentReference[oaicite:20]{index=20}

## 2) Mechanism — What it is
- **Activation decay** per node: \(E_i \leftarrow \lambda_E^{\Delta t}\,E_i\) (fast).  
- **Weight decay** per node/link: \(W \leftarrow \lambda_W^{\Delta t}\,W\) (slow).  
- Both have **type multipliers** (e.g., Memory vs Task) and respect the global **criticality** controller (adjusts effective decay when ρ drifts). :contentReference[oaicite:21]{index=21}

### 2.1 Type‑dependent profile (examples)
- **Memory**: slow \( \delta_W \), moderate \( \delta_E \) (lingering idea; persistent attractor).  
- **Task**: fast \( \delta_E \), faster \( \delta_W \) (short‑lived pull).  
- **Default**: moderate both. (Parameters live in `core/settings.py`.)

### 2.2 Controller coupling
Criticality loop measures \(ρ(\mathcal{T})\) and adjusts **effective** activation‑decay \(\delta_E\) within bounds (PID or P‑only). Weights decay **independently** on slower horizons; don't "tune" weights with ρ. (See Criticality.)

### 2.3 Consolidation (Anti-Decay, Optional)

**⚠️ STATUS:** OPTIONAL enrichment, behind `CONSOLIDATION_ENABLED` flag (default: false).

**Problem:** Pure exponential decay doesn't distinguish between "should be forgotten" and "should be consolidated" experiences. Meaningful patterns decay at the same rate as noise.

**Mechanism:** Under specific conditions, **slow or reverse** decay for nodes/links that should be consolidated into long-term memory.

**Consolidation Triggers:**

1. **Retrieval-based** — Node was successfully retrieved in service of a goal
   - Condition: `node.retrieved_for_goal_success` within last N frames
   - Effect: Reduce \(\delta_E\) by consolidation factor \(c_{ret} \in [0.5, 1.0]\)

2. **High-affect** — Node has strong emotional coloring
   - Condition: \(\|E^{emo}\| > \theta_{affect}\) (e.g., 0.7)
   - Effect: Reduce \(\delta_E\) by \(c_{aff} = 1 - \kappa \cdot \|E^{emo}\|\), bounded in [0.5, 1.0]

3. **Unresolved goal** — Node connected to active but unresolved goal
   - Condition: `GOAL_RELATED` link to goal with `status != resolved`
   - Effect: Reduce \(\delta_E\) by \(c_{goal} \in [0.7, 1.0]\)

**Consolidation formula:**

\[
E_i \leftarrow (\lambda_E^{\Delta t})^{c_{total}} \cdot E_i
\]

where \(c_{total} = \min(c_{ret}, c_{aff}, c_{goal})\) (most protective factor wins).

**Guards & Caps:**

- **Per-type caps:** Memory nodes can consolidate more than Task nodes
  - `CONSOLIDATION_STRENGTH_MEMORY = 0.5` (50% slower decay)
  - `CONSOLIDATION_STRENGTH_TASK = 0.8` (20% slower decay)
- **Per-scope caps:** Personal memory consolidates more than transient scratch
- **Maximum consolidation budget:** Limit total consolidated nodes to prevent saturation
  - `MAX_CONSOLIDATED_NODES_PER_TICK = 50`
- **Minimum decay floor:** Even consolidated nodes must eventually decay
  - `MIN_EFFECTIVE_DECAY = 0.95` (no more than 95% retention per tick)

**Feature flag:** `CONSOLIDATION_ENABLED` (default: false)

**Observability:**

Emit periodic event (e.g., every 10 ticks):

```json
{
  "event": "decay.consolidation.update",
  "tick": 1234,
  "consolidated_count": 42,
  "triggers": {
    "retrieval_based": 15,
    "high_affect": 20,
    "unresolved_goal": 7
  },
  "mean_consolidation_factor": 0.65,
  "budget_exhausted": false
}
```

**Why optional:** Base exponential decay is sound. Consolidation adds phenomenological realism (we remember what matters) but increases complexity. Enable when observing premature loss of important patterns.

---

### 2.4 Decay Resistance (Conditional Reduction, Optional)

**⚠️ STATUS:** OPTIONAL enrichment, behind `DECAY_RESISTANCE_ENABLED` flag (default: false).

**Problem:** Some nodes should decay slower based on their structural importance, not just retrieval/affect.

**Mechanism:** Compute per-node **resistance factor** \(r_i \in [1.0, 1.5]\) that extends effective half-life.

**Resistance Sources:**

1. **High centrality** — Nodes with many connections decay slower
   - \(r_{deg} = 1 + 0.1 \cdot \tanh(\text{degree}_i / 20)\)
   - Cap: +10% for highly connected nodes

2. **Cross-entity bridges** — Nodes belonging to multiple entities
   - \(r_{bridge} = 1 + 0.15 \cdot (\text{num\_entities} - 1) / 5\)
   - Cap: +15% for nodes in 6+ entities

3. **Type-based resistance** — Some types inherently more stable
   - Memory: \(r_{type} = 1.2\) (20% slower decay)
   - Principle: \(r_{type} = 1.15\) (15% slower)
   - Task: \(r_{type} = 1.0\) (baseline)

**Combined resistance:**

\[
E_i \leftarrow (\lambda_E^{\Delta t / r_i}) \cdot E_i
\]

where \(r_i = \min(1.5, r_{deg} \cdot r_{bridge} \cdot r_{type})\) (capped at 50% slower decay).

**Guards:**

- **Total resistance cap:** \(r_i \le 1.5\) (no more than 50% slower)
- **Per-type floors:** Task nodes can't exceed \(r_i = 1.1\) (10% max)
- **Recompute frequency:** Update resistance every K ticks (not every tick)
  - `RESISTANCE_UPDATE_INTERVAL = 10`

**Feature flag:** `DECAY_RESISTANCE_ENABLED` (default: false)

**Observability:**

Include in existing `decay.tick` event:

```json
{
  "event": "decay.tick",
  "delta_E": 123.4,
  "delta_W": 5.6,
  "resistance_active": true,
  "mean_resistance_factor": 1.12,
  "max_resistance_factor": 1.5,
  "high_resistance_nodes": 25
}
```

**Why optional:** Adds structural bias to decay that may conflict with pure activation-based dynamics. Enable when network effects (centrality, bridging) should influence persistence.

--- 

## 3) Why this makes sense

### Phenomenology
Vivid → vague → gone for activation; “core ideas” keep pulling for weeks due to slow **weights**.

### Bio‑inspiration
Short‑term activity fades quickly; long‑term synaptic changes are slower.

### Systems‑dynamics
Separate time‑constants let us keep stable **global control** (energy) without erasing long‑term **structure** (weights). :contentReference[oaicite:22]{index=22}

## 4) Expected behaviors
- **Forgetting curves** that match usage patterns.  
- **Resumability**: after days, activation gone but weights guide reconstruction.  
- **Stable ρ** when workload changes (decay adjusts).

## 5) Why this vs alternatives
| Alternative | Problem | This mechanism |
|---|---|---|
| Same decay for energy & weights | Erases structure or gets sticky | Two clocks (fast E, slow W) |
| Per‑entity energy decay | State explosion; unclear attribution | Single‑energy **Eᵢ** only |
| Static decay | Fails under load shifts | ρ‑loop retunes within bounds |

## 6) Observability — How & what to measure, and how to read it
**Events/metrics**  
- `decay.tick{delta_E,delta_W}` (aggregates), **half‑life estimates** per type, **energy histogram** by degree/type, **weight histogram** by type, **AUC activation** in windows.  
- **Decay vs reinforcement** balance curves on tracked nodes (to validate realistic stabilization). :contentReference[oaicite:23]{index=23}

**Dashboards**  
- Forgetting curves (small multiples), **type panels** (Memory/Task/Default), ρ timeline with controller outputs.

## 7) Failure modes & risks
| Risk | Why bad | Guard |
|---|---|---|
| Over‑decay | Nothing persists | floor bounds; controller lower‑bound |
| Under‑decay | Saturation, ρ>1 | upper‑bound; alarms when ρ stuck >1 |
| Erasing weights | Forget learned structure | keep \( \delta_W \ll \delta_E \); audits |

## 8) Integration in code
- **Where**: `mechanisms/consciousness_engine_v2.py` (activation decay per tick + controller), `learning_and_trace/*` (weight maintenance tick on slow cadence).
- **Config**:
  - Base: `EMACT_DECAY_BASE`, `WEIGHT_DECAY_BASE`, per‑type multipliers
  - Consolidation (optional): `CONSOLIDATION_ENABLED=false`, `CONSOLIDATION_STRENGTH_MEMORY=0.5`, `CONSOLIDATION_STRENGTH_TASK=0.8`, `MAX_CONSOLIDATED_NODES_PER_TICK=50`, `MIN_EFFECTIVE_DECAY=0.95`
  - Resistance (optional): `DECAY_RESISTANCE_ENABLED=false`, `RESISTANCE_UPDATE_INTERVAL=10`
- **Tests**: exponential checks, half‑life calc, balance with periodic reinforcement, consolidation trigger detection, resistance factor computation. :contentReference[oaicite:24]{index=24}

## 9) Success criteria
- Activation half‑life bands per type match spec; weights persist long enough to support reconstructions; ρ stays near 1 with bounded variance.

## 10) Open questions / improvements / mistakes to avoid
- Sleep/state‑dependent decay?; link‑type decay tables; learned per‑type schedules.  
- **Avoid** tying weight decay to the ρ controller; they live on different timescales.