---
title: Traversal v2 (Frame Pipeline & Entry Points)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/v1_traversal_outline.md
depends_on:
  - foundations/diffusion.md
  - foundations/decay.md
  - foundations/criticality.md
  - runtime_engine/fanout_strategy.md
  - emotion/emotion_coloring.md
  - emotion/emotion_complementarity.md
  - emotion/emotion_weighted_traversal.md
  - ops_and_viz/observability_events.md
summary: >
  The per-frame orchestration: gather frontier, choose entity/edge(s), stage ΔE, apply, decay, ρ-control, WM emit, and events.
---

# Traversal v2 — Engine Entry Points

## 1) Context
v2 replaces matrix diffusion with **stride‑based** redistribution + **staged deltas**, integrates **emotion gates** as *cost* modulators, and formalizes **two‑scale traversal** (entity boundary → within‑entity atomic). Physics is **single‑energy**; links transport ΔE but store no activation. :contentReference[oaicite:9]{index=9}

## 2) Frame pipeline (overview)
````

run_frame(dt):

1. refresh_affect()                     # compute A for active entity (Phase 1: valence/arousal)
2. refresh_frontier()                   # active/shadow sets
3. choose_boundaries()                  # entity-scale exits (optional per mode)
4. within_entity_strides(dt)            # local fanout → candidate set → cost → top-1 or top-K
5. emit_stride_exec_samples()
6. apply_staged_deltas()                # atomic ΔE apply; conservation check
7. apply_activation_decay(dt)           # type-dependent multipliers
8. criticality_control()                # tune decay/α to keep ρ≈1
9. wm_select_and_emit()                 # entity-first WM output
10. frame_end_event()

```

## 3) Entry points & contracts

### 3.1 `run_frame(ctx, dt)`
Top‑level entry; invokes substeps; guarantees **no in‑place E mutation** before `apply_staged_deltas()`.

### 3.2 `refresh_frontier(ctx)`
- `active = {i | E_i ≥ Θ_i} ∪ {i | received ΔE this frame}`  
- `shadow = 1‑hop(active)`  
- May apply degree caps for huge neighborhoods.

### 3.3 `choose_boundaries(ctx)`
Optional between‑entity choice when entity mode is on: rank entity exits by boundary summaries (precedence, φ, dominance), mood gates, task term. Output is the **entity** to expand next; otherwise stay in current entity.

### 3.4 `within_entity_strides(ctx, dt)`
For each `src ∈ active ∩ members(entity)`:
1) **Strategy** ← `select_strategy(src, wm_state)` (fanout doc)  
2) `cands` ← `reduce_candidates(strategy, out_edges(src))`  
3) Score each cand with **cost** (`ease`, `goal`, emotion gates)  
4) **K=1**: pick min‑cost and stage `ΔE = Esrc * exp(logW) * α_tick * dt`  
   **K>1**: softmax‑split ΔE across top‑K  
5) Track `φ` (gap closure / usefulness), `ema_flow`, `res/comp` for events.

### 3.5 `apply_staged_deltas(ctx)`
Apply `delta_E` atomically; emit conservation diagnostics (`ΣΔE≈0` ignoring decay/stimuli). No weight changes here.

### 3.6 `apply_activation_decay(ctx, dt)`
Exponential decay with **type‑dependent multipliers**; weight decay happens on a slower cadence elsewhere.

### 3.7 `criticality_control(ctx)`
Estimate/proxy `ρ`; adjust decay (P or PID) and tiny α if needed; **do not** change wall‑clock schedule (see Tick Speed).

### 3.8 `wm_select_and_emit(ctx)`
Aggregate entity energy from members (`E_S = Σ m_{iS}·saturate(E_i)`), compute coherence/quality; select WM entities; emit.

## 4) Invariants
- **Single‑energy** at nodes; **no** per‑entity energy channels.  
- Traversal affects **ΔE** only; learning affects **log_weight** only.  
- All ΔE moves are **staged** then applied; emotion gates alter **cost**, not energy.

## 5) Observability — What to emit
- `stride.exec` samples with `{src,dst,dE,phi,ease,res...,comp...}`  
- `node.flip` & `tick_frame` frontier stats (`active`, `shadow`)  
- `se.boundary.summary` for entity exits  
- `frame.end` with conservation and timing

## 6) Failure modes & guards
| Risk | Guard |
|---|---|
| In‑place E writes | stage->apply discipline; test |
| Excess scoring load | frontier filter; fanout reduction |
| Conservation drift | tests; end‑frame checks |

## 7) Integration & settings
- **Code:** `mechanisms/consciousness_engine_v2.py` calls `run_frame(dt)`; fanout + gates live under `mechanisms/` per module.  
- **Settings:** `ALPHA_TICK`, `TOPK_SPLIT`, frontier caps, sample rates.  
- **Tests:** conservation; frontier boundedness; reconstruction parity; learning continuity.

## 8) Success criteria
- Throughput stable with **frontier**, not global N; ρ≈1; context reconstruction latency maintained or improved; events explain decisions.
