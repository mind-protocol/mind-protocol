---
title: Self‑Organized Criticality (Spectral Radius ρ)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/03_self_organized_criticality.md
depends_on:
  - foundations/activation_energy.md
  - foundations/decay.md
  - foundations/diffusion.md
---

# Self‑Organized Criticality (Spectral Radius ρ)

## 1) Context — Problem we’re solving
We need the substrate to **self‑regulate** so thinking neither dies out (too subcritical) nor explodes (too supercritical). That regulation must respect the **single‑energy** model—**each node has one activation energy (Eᵢ)**—and our **two‑scale traversal** (entity‑scale boundary strides + atomic within‑entity strides). No per‑entity energy buffers on nodes; links don’t store activation. :contentReference[oaicite:1]{index=1}

**Goals**
- Keep global dynamics near **ρ≈1** (edge‑of‑chaos) to maximize *useful spread without runaway*.  
- Provide a clean **control surface** (decay, diffusion share, small threshold factor) without hidden constants, with **observability** for operators. :contentReference[oaicite:2]{index=2}

## 2) Mechanism — What it is
We estimate the **spectral radius ρ** of the *effective propagation operator* \(\mathcal{T}\) and tune one or two levers to stay near the target:

\[
\mathcal{T} \;=\; (1-\delta)\,\big[(1-\alpha)\,I + \alpha\,P^\top\big]
\]

- \(P\): row‑stochastic transition (from learned link weights and current stride policy).  
- \(\alpha\): diffusion/redistribution share used inside a tick.  
- \(\delta\): state‑decay factor per tick (with **type multipliers** at apply‑time).  
- Target: \( \rho(\mathcal{T}) \approx 1.0 \). :contentReference[oaicite:3]{index=3}

**Controller options**
- **P‑controller (default)**: adjust \(\delta\) by \(k_p(\rho-1)\).
- **PID** (optional): adds integral/derivative for smoother convergence on shifting graphs.
- **Dual‑lever** (advanced): small co‑tuning of \(\alpha\) opposite to \(\delta\) for faster convergence. :contentReference[oaicite:4]{index=4}

### 2.1 Coherence C (Quality Metric, Optional)

**⚠️ STATUS:** OPTIONAL enrichment, behind `COHERENCE_METRIC_ENABLED` flag (default: false).

**Problem:** ρ measures **quantity** of activation spread but not **quality**. High ρ can mean either productive exploration or chaotic thrashing. We need a second axis to distinguish flow from fragmentation.

**Mechanism:** Compute **Coherence C ∈ [0,1]** measuring quality of activation spread:

\[
C = \alpha_{\text{frontier}} \cdot C_{\text{frontier}} + \alpha_{\text{stride}} \cdot C_{\text{stride}}
\]

where:
- \(C_{\text{frontier}}\) = similarity of active frontier to previous frame (cosine of embedding centroids)
- \(C_{\text{stride}}\) = mean relatedness of executed strides (based on link weights and semantic alignment)
- Default weights: \(\alpha_{\text{frontier}} = 0.6\), \(\alpha_{\text{stride}} = 0.4\)

**Interpretation:**
- **High C (> 0.7)**: Coherent exploration, related concepts, smooth traversal
- **Medium C (0.4-0.7)**: Mixed quality, some jumps but some continuity
- **Low C (< 0.4)**: Fragmented, incoherent jumps, thrashing

**Why optional:** Base ρ-control is sound. Coherence adds phenomenological realism (distinguishing flow from chaos) but increases computation. Enable when observing high-ρ states that feel scattered vs generative.

**Feature flag:** `COHERENCE_METRIC_ENABLED` (default: false)

**Configuration:**
```python
COHERENCE_METRIC_ENABLED = False
COHERENCE_FRONTIER_WEIGHT = 0.6
COHERENCE_STRIDE_WEIGHT = 0.4
COHERENCE_WINDOW_FRAMES = 5  # Rolling window for smoothing
```

---

### 2.2 Criticality Modes (ρ + C Classification, Optional)

**⚠️ STATUS:** OPTIONAL enrichment, behind `CRITICALITY_MODES_ENABLED` flag (default: false).

**Problem:** Single ρ value doesn't capture phenomenological state. Need richer classification combining quantity (ρ) and quality (C).

**Mechanism:** Classify system state into four modes based on (ρ, C) position:

| Mode | ρ Range | C Threshold | Phenomenology | Controller Response |
|------|---------|-------------|---------------|---------------------|
| **Subcritical** | ρ < 0.9 | (any) | Brain fog, ideas don't spread | Reduce δ, increase α slightly |
| **Flow** | 0.9 ≤ ρ ≤ 1.1 | C ≥ 0.7 | Optimal: coherent exploration | Maintain current parameters |
| **Generative Overflow** | ρ > 1.1 | C ≥ 0.7 | Creative overflow, many good threads | Slight δ increase, monitor for transition to chaos |
| **Chaotic Racing** | ρ > 1.1 | C < 0.4 | Scattered, anxious, incoherent jumps | Aggressive δ increase + small threshold multiplier |

**Mode transitions:**
- **Subcritical → Flow**: Natural from increased stimulation
- **Flow → Generative Overflow**: Acceptable for creative tasks, monitor coherence
- **Generative Overflow → Chaotic Racing**: DANGER - quality collapse despite high activation
- **Chaotic Racing → Flow**: Controller intervention successful
- **Flow → Subcritical**: Natural during rest/consolidation phases

**Observability:**

Emit mode change events:

```json
{
  "event": "criticality.mode_transition",
  "from_mode": "flow",
  "to_mode": "generative_overflow",
  "rho": 1.15,
  "coherence": 0.75,
  "tick": 1234,
  "controller_action": "monitor"
}
```

**Why optional:** Base ρ-control + phenomenological matching (section 3.1) sufficient for stability. Modes add interpretability and allow task-adaptive responses but increase complexity. Enable when operators need richer state classification.

**Feature flag:** `CRITICALITY_MODES_ENABLED` (default: false)

---

### 2.3 Task-Adaptive ρ Targets (Context-Aware Control, Optional)

**⚠️ STATUS:** OPTIONAL enrichment, behind `TASK_ADAPTIVE_TARGETS_ENABLED` flag (default: false).

**Problem:** Single ρ ≈ 1.0 target doesn't match all task contexts. Exploration benefits from slight supercriticality (ρ ≈ 1.1), consolidation from subcriticality (ρ ≈ 0.95).

**Mechanism:** Adjust target ρ based on inferred task context:

| Task Context | Target ρ | Tolerance | Rationale |
|--------------|----------|-----------|-----------|
| **Explore** | 1.10 | ±0.15 | Encourage wide activation spread, multiple perspectives |
| **Implement** | 1.00 | ±0.08 | Balanced: focused but adaptable |
| **Consolidate** | 0.95 | ±0.10 | Favor settling, memory formation, reduced noise |
| **Rest** | 0.80 | ±0.20 | Minimal spread, recovery, cleanup |

**Task context inference:**

Infer from combination of:
- **Goal type**: Exploration_Goal → explore, Task → implement, Memory formation → consolidate
- **Active entity types**: High entity count + diverse types → explore
- **Recent flip rate**: High flip rate → implement (focus needed)
- **WM stability**: Stable WM for N frames → consolidate
- **Low activation period**: ρ < 0.9 for M frames → rest (don't fight it)

**Controller adjustment:**

```python
if TASK_ADAPTIVE_TARGETS_ENABLED:
    task_context = infer_task_context(goals, entities, flip_rate, wm_stability)
    target_rho = TASK_CONTEXT_TARGETS[task_context]
    tolerance = TASK_CONTEXT_TOLERANCES[task_context]

    # P-controller with adaptive target
    error = rho - target_rho
    if abs(error) > tolerance:
        delta_adjustment = k_p * error
```

**Observability:**

Include task context in criticality updates:

```json
{
  "event": "criticality.update",
  "rho": 1.05,
  "target_rho": 1.10,
  "task_context": "explore",
  "within_tolerance": true,
  "controller_action": "maintain"
}
```

**Guards:**
- **Explicit mode only**: Don't auto-infer during critical operations (use fixed ρ = 1.0)
- **Hysteresis on transitions**: Require N frames of evidence before switching task context
- **Override capability**: Allow manual task context setting for testing/debugging

**Why optional:** Fixed ρ ≈ 1.0 target is safe and stable. Task-adaptive targets add performance optimization (better match between dynamics and task) but risk instability if context inference is wrong. Enable when system is mature and task contexts are reliably detectable.

**Feature flag:** `TASK_ADAPTIVE_TARGETS_ENABLED` (default: false)

**Configuration:**
```python
TASK_ADAPTIVE_TARGETS_ENABLED = False
TASK_CONTEXT_TARGETS = {
    "explore": 1.10,
    "implement": 1.00,
    "consolidate": 0.95,
    "rest": 0.80
}
TASK_CONTEXT_TOLERANCES = {
    "explore": 0.15,
    "implement": 0.08,
    "consolidate": 0.10,
    "rest": 0.20
}
TASK_CONTEXT_HYSTERESIS_FRAMES = 5  # Frames before switching context
```

---

## 3) Why this makes sense

### 3.1 Phenomenology
- **Subcritical (ρ≪1)**: “brain fog,” ideas don’t propagate.  
- **Critical (ρ≈1)**: flow; ideas connect without overwhelm.  
- **Supercritical (ρ≫1)**: racing thoughts, hard to focus. :contentReference[oaicite:5]{index=5}

### 3.2 Bio‑inspiration
Matches **neural avalanches** literature: cortex near the edge of chaos optimizes dynamic range and information transmission.

### 3.3 Systems‑dynamics rationale
ρ is a **global stability index** for linearized spread/decay. Keeping \(\rho\approx1\) ensures **marginal stability** while traversals pick *which* edges actually carry energy.

## 4) Expected resulting behaviors
- **Stable cascades** that neither fizzle nor blow up.  
- **Elastic reactivity**: after stimulus bursts, controller increases decay briefly, then relaxes.  
- **Consistent WM composition** (entity‑first) because activation stays in a workable band. :contentReference[oaicite:6]{index=6}

## 5) Why this algorithm vs alternatives
| Alternative | Problem | Why we prefer ρ‑control |
|---|---|---|
| Fixed decay | Breaks across graphs/tasks | ρ adapts to topology and recent traffic |
| Per‑entity clocks / solo tuning | Race conditions, inconsistent snapshots | We tune on a **single global tick**, apply deltas together |
| Only threshold modulation | Laggy, can mask instability | ρ directly measures propagation stability |

(We still allow a **small threshold multiplier** \(f_\rho\) to gently tighten/loosen activation checks during excursions; the primary lever remains \(\delta\).) :contentReference[oaicite:7]{index=7}

## 6) Observability — How & what to measure, and how to read it
**How (per frame):**
- Estimate \( \rho(\mathcal{T})\) via **power iteration** on the operator built from current \(P\), \(\delta\), \(\alpha\).  
- Lightweight proxy: **branching ratio** \(B=\frac{\sum \text{outflow}}{\sum \text{inflow}}\) on the active frontier; \(B\) tracks ρ trends cheaply.  
- Keep both: ρ (authoritative, sampled) and B (cheap, every frame). :contentReference[oaicite:8]{index=8}

**What to emit (metrics & events):**
- `rho.global`, `rho.proxy.branching`, `rho.var.window`, controller outputs (Δδ, Δα), **safety state** (`subcritical|critical|supercritical`).  
- Optional **entity‑view** for explanation: compute ρ on the **membership‑weighted subgraph** of an *active entity* (read‑only projection; no per‑entity node energies). Helpful to explain “this entity was too lively,” without violating single‑energy. :contentReference[oaicite:9]{index=9}

**How to interpret:**
- **ρ≈1 ±0.1** → healthy; **ρ>1.2** sustained → clamp α and lift δ a notch; **ρ<0.8** → back off δ.  
- Watch **oscillation index** (sign changes of \(\rho-1\)); if high, lower controller gains (PID D‑term).

## 7) Failure modes & risks — and why they’re bad
| Risk | Why bad | Guard |
|---|---|---|
| **Controller oscillation** | Flicker; wasted compute | Use PID w/ anti‑windup; cap gain; hysteresis on safety states |
| **Expensive ρ estimate** | Frame budget blow‑ups | Sample power‑iteration; keep B as per‑frame proxy |
| **Per‑entity tuning** | Race conditions, hidden clocks | Single global tick; entity ρ only for **read‑only** diagnostics |
| **Masking with thresholds** | Latent instability | Keep threshold factor small; use ρ as truth |

## 8) Integration in code
- **Where**: `mechanisms/consciousness_engine_v2.py` controller loop.  
- **Inputs**: current \(P\) (from link log‑weights + selector), \(\alpha\), \(\delta\).  
- **Outputs**: updated \(\delta\) (and optionally \(\alpha\)), `rho.*` metrics.  
- **Two‑scale**: controller runs **once per frame**; traversal then uses the updated parameters. :contentReference[oaicite:10]{index=10}

## 9) What success looks like
- **ρ mean** in [0.95, 1.05] with **low variance** under realistic stimulus schedules.  
- **No growth** in flip‑thrash; WM selection stable.  
- **Operator dashboard**: clear read of when/why ρ moved and which lever acted.

## 10) Open questions / future work / mistakes to avoid
- **Open**: task‑adaptive targets (creative exploration might prefer ρ≈1.1?).  
- **Future**: contextual priors for \(\alpha,\delta\) on known graph regions.  
- **Avoid**: per‑entity energy maps (retired), per‑entity clocks; “fixing” ρ by cranking thresholds only. :contentReference[oaicite:11]{index=11}
