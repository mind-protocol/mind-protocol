---
title: Diffusion v2 — Stride-based, Active-Frontier (Single-Energy Substrate)
status: ready
owner: @felix
last_updated: 2025-10-22
supersedes:
  - mechanisms/diffusion.py (matrix diffusion)
depends_on:
  - subentity_layer/subentity_layer.md
  - runtime_engine/traversal_v2.md
  - runtime_engine/fanout_strategy.md
  - foundations/decay.md
  - runtime_engine/tick_speed.md
  - ops_and_viz/observability_events.md
---
```

## 1) Intent & Why we’re changing it

**Problem with current code:** full‑graph, per‑subentity channels + matrix diffusion (O(N²)/tick) conflicts with the final substrate design (one activation energy per node; entities are soft aggregations) and scales poorly. **Spec direction:** single‑energy substrate, **selective, stride‑based transfer** along edges chosen by traversal; maintain an **active frontier** instead of touching the whole graph. This matches the entity model (entities aggregate from member nodes) and the runtime traversal architecture (two‑scale selection, then atomic strides).  

**Design alignment highlights**

* **Single energy Eᵢ per node**; entities aggregate via membership weights (no per‑entity energy buffers on nodes). 
* **Diffusion happens via executed strides**, not a global multiply; breadth is kept sane with **local fan‑out strategy**. 
* **Tick duration Δt** is variable (tick‑speed regulation) and must factor into energy transfer/decay. 
* **Per‑type decay** remains independent (state vs weight) and runs after transfers. 

---

## 2) Core rule (what replaces matrix diffusion)

For each executed stride ( i \to j ) this tick:

[
\Delta E_{i \to j}
=\underbrace{E_i^{\text{pre}}}*{\text{source}} \cdot
\underbrace{f!\left(\widetilde{W}*j\right)}*{\text{monotone of standardized target weight}} \cdot
\underbrace{\alpha*{\text{tick}}}*{\text{global step}} \cdot
\underbrace{\Delta t}*{\text{tick duration}}
]

* **( \widetilde{W}_j )** is the **read‑time standardized attractor mass** of target (j):
  (\widetilde{W}_j = \exp!\big((\log W_j - \mu_T)/(\sigma_T+\varepsilon)\big)) (per‑type baseline). Set ( f(x)=x ) for v1. This uses the weight‑reading invariant from weight learning so we never hard‑center stored values. 
* **( \alpha_{\text{tick}} )** is a small global step (start with 0.02) that caps how much of a source can move per tick. It multiplies with **Δt** (seconds) so faster ticks don’t move absurd mass (tick speed is stimulus‑driven). 

**No energy on links.** Links only gate selection and parameterize transfer; all activation energy lives on nodes. 

---

## 3) Data structures & contracts

**New runtime accumulators (per tick):**

```python
# mechanisms/sub_entity_traversal.py (module-scope or class)
delta_E: Dict[NodeID, float]           # staged energy deltas for this tick
stride_log: List[StrideExec]            # for events & learning
active_frontier: Set[NodeID]            # E_i >= Θ_i at frame start
shadow_frontier: Set[NodeID]            # one-hop neighbors of active_frontier
```

* **active_frontier**: nodes above threshold at **frame start**.
* **shadow_frontier**: 1‑hop neighbors (candidate targets).
* Maintain these sets in traversal; update them incrementally as flips occur. 

**API hooks to (re)use**

* **Traversal entry points** (call sites for per‑stride transfer + staging): `traversal_v2` (engine loop; TODO file documents the entry points we wire). 
* **Local fanout selector** (limits candidate edges before scoring): `fanout_strategy`. 
* **Decay module** (type‑dependent): apply after we commit deltas. 
* **Tick speed controller** (provides Δt): used by the loop to scale transfers & decays. 

---

## 4) Algorithm (one tick, high‑level)

1. **Snapshot pre‑state**
   Compute thresholds, **active_frontier** (= {nodes with (E_i \ge \Theta_i)}), **shadow_frontier** (= out‑neighbors). Clear `delta_E`. 

2. **For each source node** in active_frontier (and any newly flipped this tick):

   * Select candidate edges using **fanout strategy** (local, no global topology). 
   * Score candidates (valence stack, emotions if enabled) → pick **K** targets (see §6/Q5).
   * For each chosen edge (i\to j): compute (\Delta E_{i\to j}) via core rule; stage it: `delta_E[j] += ΔE; delta_E[i] -= ΔE`.
   * Log `stride.exec` record (includes ΔE, utility φ, z_flow, etc.). 

3. **Commit staged deltas atomically**
   For all nodes: `E_i_post = max(0, E_i_pre + delta_E[i])`. Emit flips. **Then** apply **type‑dependent decay** with the same Δt. 

4. **Emit frame events**

   * `frame.start`, then per‑stride `stride.exec`, `node.flip`, `subentity.boundary.summary` beams, `frame.end` (2‑frame reorder buffer). 
   * Maintain energy‑conservation diagnostics (below).

5. **Update active/shadow sets**

   * Add newly flipped nodes to active; update shadow from new actives.
   * Remove nodes that fell below threshold and got no inbound ΔE.

---

## 5) Exact answers & decisions (Q1–Q6)

**Q1 — Single‑Energy migration path**

* **Decision:** Remove node‑level per‑entity channels. Introduce one stored field `node.energy: float`.
* **Differentiation for entities** happens by **aggregation** at read‑time (subentity energy = weighted sum of member nodes above threshold); no node stores “per‑entity energy.” Keep an *ephemeral* **attribution buffer** (in‑tick only) if you need to break down ΔE by subentity for events, but **do not persist** it on nodes. This follows the entity spec (entities are soft neighborhoods over one substrate). 

**Q2 — Active‑frontier tracking (placement & updates)**

* **Placement:** traversal runtime (e.g., `SubEntityTraversalCtx`), not on the schema.
* **Seeds:** start from **stimulus‑activated** and any above‑threshold nodes.
* **Updates:** mutate sets **after commit** each tick; frontier is defined on pre‑tick state plus new flips staged this tick (additions) and nodes that fell sub‑threshold (removals). 

**Q3 — Staged deltas**

* **Decision:** `Dict[node_id, float]` accumulator; **apply once** per tick after all strides; then run **decay**. Add a **conservation check**:
  (\sum_i \Delta E_i^{\text{staged}} + \Delta E_{\text{stim}} - \Delta E_{\text{decay}} \stackrel{?}{=} \Delta E_{\text{total}}).
  On >1% discrepancy, emit a diagnostic. Events should carry per‑tick totals to the viz stream. 

**Q4 — Backward compatibility**

* **Feature flag in settings:** `DIFFUSION_IMPL = "stride" | "matrix"` (default “stride” in dev).
* Keep `mechanisms/diffusion.py` **only for A/B in tests**; remove calls from engine. **Production path** goes through traversal strides. Update the engine entrypoints in `traversal_v2` to orchestrate “stage → commit → decay → events.” 

**Q5 — Top‑K split**

* **Phase 1:** `K=1` (single best edge per source visit) — simpler and already validated by selection logic.
* **Phase 2:** enable `K∈{2..4}`; split (\Delta E_i) across targets using **softmax over scores** (valence + weight), then apply each target’s share via the same core rule; controlled by `DIFFUSION_TOPK`. Documented in fanout strategy as a natural extension. 

**Q6 — ( f(w) ) transform**

* **Decision:** Use the standardized weight reader from learning (**don't** use raw weight):
  ( f(\widetilde{W}_j) = \widetilde{W}_j = \exp((\log W_j - \mu_T)/(\sigma_T+\varepsilon)) ).
  This is exactly how weights are meant to be consumed across the stack.

**Q7 — Stickiness (Target-Side Retention, Optional)**

* **Problem:** Some nodes should retain incoming energy more strongly (consolidation points), while others should let energy pass through (relay nodes). Without this, all nodes treat incoming ΔE equally.
* **Decision (OPTIONAL, feature-flagged):** Add **target-side retention factor** `s_j ∈ [0,1]` that modulates how much inbound ΔE is **retained** vs **passed along** in subsequent transfers.
* **Mechanism:**
  ```python
  # When staging energy transfer i → j
  retained_ΔE = s_j * ΔE_{i→j}
  delta_E[j] += retained_ΔE
  delta_E[i] -= ΔE_{i→j}  # Source loses full amount

  # Stickiness affects FUTURE transfers FROM j
  # (j's effective available energy for outbound strides is reduced by retention)
  ```

* **Stickiness sources (read-time computation, NOT stored):**
  1. **Type-based:** Memory nodes sticky (s=0.9), Task nodes flow-through (s=0.3)
  2. **Consolidation-based:** Nodes being consolidated are stickier (s+=0.2)
  3. **Centrality-based:** Hub nodes slightly stickier (s+=0.1 * tanh(degree/20))
  4. **Combined:** `s_j = clip(s_type * s_consolidation * s_centrality, 0.1, 1.0)`

* **Properties:**
  - **Bounded:** s_j ∈ [0.1, 1.0] (minimum 10% retention, maximum 100%)
  - **Read-time param:** Computed on-demand, NOT stored on nodes (keeps schema clean)
  - **No link energy:** Links still don't store energy; stickiness is a node property
  - **Conservation:** Total energy conserved (source loses full ΔE, target gains s_j * ΔE, difference dissipates as "flow-through loss")

* **Effect:**
  - **Consolidation points** (Memory, Principle nodes) accumulate energy more readily
  - **Relay nodes** (Task, transient nodes) let energy flow through to deeper targets
  - **Hub nodes** act as energy attractors without requiring manual configuration

* **Feature flag:** `STICKINESS_ENABLED` (default: false)

* **Observability:**
  ```json
  {
    "event": "stride.exec",
    "src": "node_i",
    "tgt": "node_j",
    "delta_E_gross": 0.5,
    "delta_E_retained": 0.45,
    "stickiness": 0.9,
    "flow_through_loss": 0.05
  }
  ```

* **Why optional:** Base diffusion (full retention, s=1.0) is sound. Stickiness adds flow dynamics that can help with consolidation but may interact unexpectedly with decay. Enable when observing energy pooling issues or wanting to bias toward hub/memory accumulation.

* **Guards:**
  - **Conservation accounting:** Track flow-through loss separately; include in energy conservation check
  - **Minimum stickiness floor:** s_j ≥ 0.1 (always retain at least 10%)
  - **Type override:** Ensure type-specific stickiness doesn't conflict with decay resistance

---

## 6) Scoring, utility & learning hooks (what happens on each stride)

When a candidate edge (i\to j) is considered:

* **Score** with your existing valence stack (emotion resonance, complementarity, goal, novelty, weight term ( \widetilde{W}_j )). Fanout strategy prunes the set before scoring to control branching. 
* **Compute utility** ( \phi_{ij} = \min(\Delta E_{i\to j}, G_j^{\text{pre}})/(G_j^{\text{pre}}+\varepsilon) ) for z‑norm cohorts; log into `stride.exec`. This feeds weight learning (link utility z_φ) as specced. 
* **Learning signals:** keep **newness gate** (only strengthen edges that recruit a dormant target and both endpoints were sub‑threshold pre‑stride), and use rank‑z cohorts per the spec. (No changes here—diffusion v2 just provides the ΔE and φ inputs.) 

---

## 7) Observability (what to emit & how to read it)

**Per stride** (`stride.exec`):

* `src`, `tgt`, `ΔE`, `E_src_pre`, `E_tgt_pre`, `E_tgt_post`, `phi`, `z_flow`, `score`, `selected_reason(top_k/fanout)`. This attaches cleanly to the current WS contract (deltas + a 2‑frame reorder buffer; redraw at `frame.end`). 

**Per frame diagnostics (new counters):**

* `energy_in`: sum of stimulus injections this frame
* `energy_transferred`: ( \sum |\Delta E_{i\to j}| )
* `energy_decay`: total loss to decay (state) with per‑type breakdown
* `conservation_error`: absolute & %
* `frontier_size_active`, `frontier_size_shadow`, `mean_degree_active`, `diffusion_radius_from_seeds`

**Subentity boundary summaries:** aggregate cross‑entity beams (count, ( \sum \Delta E ), max φ, typical hunger). This matches the “boundary summary” visualization needs. 

**Why these matter (interpretation guide for Iris):**

* A rising `frontier_size_active` with stable `energy_in` ⇒ system relying more on internal attractors (expect growth in high‑weight regions).
* High `conservation_error` ⇒ bug (order‑of‑ops or double‑apply).
* Increasing `diffusion_radius` ⇒ exploration; falling radius with high φ ⇒ exploitation around good attractors.

---

## 8) Failure modes & guards

1. **Energy explosion** (ΔE pulls too hard on a single tick at high Hz)

   * **Guard:** cap per‑source **transfer ratio**: (\sum_j \Delta E_{i\to j} \le \beta \cdot E_i^{\text{pre}}) (β ∈ [0.05, 0.2]). Combine with Δt.

2. **Frontier collapse** (too strict thresholds starve traversal)

   * **Guard:** keep a **shadow retry**: a small budget can be aimed at top shadow nodes even if actives are few; this prevents deadlocks near threshold.

3. **Oscillation with quick ticks** (over‑responsive stimulus bursts)

   * **Guard:** use the **smoothed** tick controller variant (EMA on interval); still pass raw Δt for physics after applying a **max_tick_duration** cap. 

4. **Type coupling error** (decay applied before commit)

   * **Guard:** invariant: **commit deltas → then decay**. Unit test enforces order.

5. **Learning on chatter**

   * **Guard:** keep **newness gate** for link strengthening and require target flip for positive updates. 

---

## 9) Integration points (exact files & changes)

* **Remove** engine call: `diffusion.diffusion_tick(...)` (matrix).

* **Add** to `mechanisms/sub_entity_traversal.py`:

  * `select_candidates()` uses **fanout strategy**. 
  * `execute_stride(i, j, ctx)` computes/stages **ΔE** via core rule; appends `stride.exec`.
  * Maintain **active/shadow** sets.

* **Update** `runtime_engine/traversal_v2.py` (engine loop): **stage → commit → decay → events**; accept **Δt** from tick controller; publish viz events as per contract. (The file is TODO; this spec defines the orchestration that belongs there.) 

* **Decay**: call **type‑dependent decay** after commit using the same Δt (state) and the regular slow path for weights (if you decay weights continuously). 

* **Tick**: source Δt from **tick speed regulation** (time since last stimulus, with bounds/cap). 

* **Events**: ensure `stride.exec`, `node.flip`, `subentity.boundary.summary`, `weights.updated` are emitted with schemas from the viz contract. 

---

## 10) Backward compatibility & rollout

* **`core/settings.py`**:
  `DIFFUSION_IMPL="stride"` (default), `"matrix"` (legacy), and `DIFFUSION_TOPK=1`.
* **Two‑week dual path in CI only**: run A/B tests comparing steady‑state totals and conservation error on a fixed seed. No dual runtime in prod.
* **Remove** legacy once parity tests pass.

---

## 11) Tests & success criteria

**Unit**

* **Conservation**: staged sums + stimuli − decay == total ΔE within 1%.
* **Ordering**: commit‑before‑decay invariant.
* **Frontier maintenance**: flips add to active; sub‑threshold nodes leave.

**Integration**

* **Star vs chain topologies** show selective vs exhaustive behavior (fanout). 
* **Tick adaptation**: faster stimulus ⇒ more (but smaller) ΔE steps; slow periods ⇒ fewer (larger Δt) steps with cap. 
* **Type decay**: memory vs task persistence curves match config. 

**Observability acceptance**

* `stride.exec` events carry ΔE, φ, z_flow; `frame` counters show ~0 conservation error at steady state; boundary summaries appear on cross‑entity beams. 

**Success looks like**

* CPU drops ~10–30× on large graphs (we only touch frontier).
* Visuals: expanding “beams” instead of uniform glow; boundary summaries reflect focused cross‑entity flow. 

---

## 12) Open questions / future work

* **Phase‑2 Top‑K splitting** default values (K, temperature) — start with K=1, T=1.5; tune from TRACE.
* **Per‑edge step size** (learn a small α by type/scope) — keep global α until we have data.
* **Entity‑aware redistribution** — when between‑subentity jumps are explicitly chosen, summarize as **boundary beams** (already in events spec). 

---

### Minimal code sketch (illustrative only)

```python
# traversal_v2.py (engine loop)  -- orchestrates one tick
def tick(ctx: EngineCtx, dt: float):
    frontier = ctx.frontier.active
    delta_E = defaultdict(float)
    stride_log = []

    for i in frontier:
        cand_edges = fanout.select(i)                    # bottom-up pruning
        j = pick_best(cand_edges, ctx)                   # or top-K softmax
        if not j: continue
        dE = compute_delta_E(i, j, dt, ctx)              # core rule
        delta_E[i] -= dE; delta_E[j] += dE
        stride_log.append(make_stride_event(i, j, dE, ctx))

    commit_deltas(ctx.graph, delta_E)                    # atomic apply
    apply_type_dependent_decay(ctx.graph, dt)            # then decay
    emit_frame_events(stride_log, ctx)                   # WS events
```

This puts diffusion **inside traversal** (as per spec intent), keeps deltas staged, and makes Δt a first‑class parameter.
