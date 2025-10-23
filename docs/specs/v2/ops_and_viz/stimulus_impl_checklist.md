---
title: Stimulus Injection Implementation Checklist
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/STIMULUS_INJECTION_IMPLEMENTATION_CHECKLIST.md
depends_on:
  - entity_layer/stimulus_injection.md
  - foundations/diffusion.md
summary: >
  Implementation checklist for stimulus injection. Verifies all components are integrated:
  node/link retrieval, budget computation, health & source gates, peripheral amplification,
  link-matched split, (optional) subentity routing, events, and tests.
---

# 0) Scope & invariants

- **Single‑energy**: inject to **nodes** (and split across endpoints for link matches).  
- **No weight updates** here; TRACE/Traversal learning handle weights separately.  
- **Gap‑aware budget**: respect node’s activation **gap** to avoid overshoot.  
- **Observability**: emit `stimulus.injected.v1` and item‑level events.

# 1) Core — v0 (already in place)

- [x] Entropy‑coverage search (§2: adaptive retrieval)
- [x] Gap mass calculation (§3.2)
- [x] Gap‑capped budget distribution (§5.1)
- [x] Basic `InjectionMatch` / `InjectionResult`

# 2) Foundation features (v1)

## 2.1 Health modulation **f(ρ)** (spec §3.3)
- Compute `ρ` (or proxy) and frame quality signals (flip yield, activation entropy, overflow penalty).  
- Fit **isotonic regression** over a rolling window (increasing=false).  
- Until bootstrap N≥200, return 1.0.

**Acceptance:** budgets decrease monotonically with higher ρ in synthetic tests.

## 2.2 Source impact gate **g(source)** (spec §3.4)
- Track per‑source flip yield (flips/budget), **rank‑normalize** by cohort (this week).  
- Map to [0.5, 1.5]; bootstrap neutral until ≥50 samples.

**Acceptance:** `tool_result.error` sources get >1.0; low‑yield timers <1.0.

## 2.3 Direction‑aware **link injection** (spec §5.2)
- Search can yield **link** matches (id + src/dst).  
- Use precedence priors to split budget: `p_source`, `p_target` from Beta(α_fwd, β_fwd).  
- Inject `ΔE_source`, `ΔE_target`.

**Acceptance:** ENABLES links skew 70/30 as precedence accumulates.

## 2.4 Peripheral amplification (spec §6)
- Compare stimulus embedding against S5/S6 peripheral chunks; compute `max_alignment`.  
- Cohort rank‑z; amplify only for z>0: `B' = B * (1 + z)` (cap at policy max).

**Acceptance:** stimuli echoing peripheral awareness get 2–3× budget.

# 3) Subentity layer (v2, optional now)

- Compute **entity affinity** + **recent success** (flip share × gap‑closure share).  
- Softmax **π_e** over active entities; split B by π_e and route to members.  
- Keep neutral fallback until entity infrastructure is stable.

**Acceptance:** design‑related stimuli allocate more to “Architect” than “Validator”.

# 4) Budget & injection math

- Effective budget: `B_eff = B_base * f(ρ) * g(source) * (1 + peripheral_z⁺)`  
- **Node cap:** each node receives ≤ its **gap to threshold** (scaled), never overshoot.  
- **Sparsity:** honor K_eff; prefer diversity (cover different subgraphs).

# 5) Events (exact payloads)

### 5.1 `stimulus.injected.v1` (frame‑level)
```json
{
  "kind":"stimulus.injected.v1","frame_id":123457,"ts":"...",
  "source":"user_message","chunks":3,"matches_selected":12,
  "entropy":2.3,"coverage_target":0.90,
  "budget_base":18.5,"health_factor":0.92,"source_gate":1.15,"peripheral_amp":1.30,
  "budget_final":25.6,"energy_injected":24.2,"nodes_activated":8,"flips":5
}
````

### 5.2 `stimulus.item_injected.v1` (for debugging)

```json
{
  "kind":"stimulus.item_injected.v1","frame_id":123457,"ts":"...",
  "item_id":"n.X","item_type":"node","similarity":0.85,
  "delta_energy":3.2,"gap_before":4.5,"gap_after":1.3
}
```

# 6) Tests

## Unit

1. Entropy coverage adapts K.
2. Gap mass and caps respected (no overshoot).
3. f(ρ) monotone; g(source) cohort‑relative.
4. Direction prior splits per precedence.
5. Peripheral amplification on z>0 only.

## Integration

1. E2E stimulus → energy deltas → `node.flip` counts.
2. Multi‑stimulus batches adapt gates over 1000+ frames.
3. With subentity routing, π_e tracks **affinity×success**.

# 7) Config & flags

* `STIM_HEALTH_ENABLED=true`, `STIM_SOURCE_GATE_ENABLED=true`, `STIM_PERIPH_ENABLED=false` (start off), `STIM_LINK_INJECT_ENABLED=false` (enable after tests).
* Explicit caps: `STIM_BUDGET_MAX`, `STIM_PERIPH_MAX_X`.
* Sampling for item events: `STIM_ITEM_EVENT_RATE` (default 0.05).

# 8) Done =

* All features above implemented; events emitted; tests pass; dashboards wired to **Observability Events** contract.

```

**Changes made:**  
- Added precise **payloads**, **gates**, **caps**, and **tests**; clarified that injection is node‑level and link matches split across endpoints; added optional **subentity routing**; aligned with event contract. :contentReference[oaicite:5]{index=5}

**Compliance:** Single‑energy; no weight edits; observability aligned; optional subentity split guarded → **OK**.
