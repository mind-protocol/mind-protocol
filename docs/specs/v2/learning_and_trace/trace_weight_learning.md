---
title: TRACE Weight Learning (EMAs → Cohort z → log_weight)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - learning_and_trace/trace_weight_learning.md
depends_on:
  - learning_and_trace/trace_reinforcement.md
---

# TRACE Weight Learning (EMAs → Cohort z → log_weight)

## 1) Context
Convert parser signals from TRACE (reinforcement seats ΔR; **C×E×N** formation quality) into **stable, comparable** updates of `log_weight` for nodes/links—distinct from traversal learning. :contentReference[oaicite:24]{index=24}

## 2) Mechanism — What it is
1) **EMA smoothing** of ΔR and q per item (`ema_trace_seats`, `ema_formation_quality`).  
2) **Cohort rank‑z** within **type+scope** (fallback widening on small N).  
3) **Apply** to `log_weight` with small step size η; **read‑time standardization** prevents drift.

### 2.1 EMA
`ema_t = α·v_t + (1−α)·ema_{t−1}`; defaults α=0.1; bootstrap on first mention.

### 2.2 Cohort z
`z = Φ^{-1}(rank/(N+1))`; cohorts: type+scope → scope → type → global (only if needed). For N<3, use raw EMA and flag low confidence.

### 2.3 Update
Nodes: `Δ logW_i = η · (z_rein(i) + z_form(i) + z_R(i) + z_F(i) + z_wm(i))`  
Links: `Δ logW_ij = η · (z_rein + z_form + z_φ(ij))` (traversal channel adds to same `logW`).  

### 2.4 Read‑time standardization
Maintain rolling `(μ_T,σ_T)` per type+scope; consumers read `W̃=exp((logW−μ_T)/σ_T)` for comparability.

## 3) Why this makes sense
EMAs tame variance; cohort rank‑z eliminates magic constants; read‑time standardization prevents global drift while preserving raw `log_weight`. :contentReference[oaicite:25]{index=25}

## 4) Expected behaviors
- Recently reinforced items rise relative to cohort; weak ones sink; effects are **auditable** by seat and quality histories.

## 5) Why this vs alternatives
| Alternative | Issue | This |
|---|---|---|
| Raw counts | Session bias | EMA |
| Global z only | Domain shift | Cohorts w/ fallbacks |
| Store standardized | Loss of raw | Standardize on read |

## 6) Observability
**Events:** `weights.updated.trace` with cohort stats; seat and quality panels per item.  
**Metrics:** z distributions by type; update deltas; cohort size alerts. :contentReference[oaicite:26]{index=26}

## 7) Failure modes & guards
| Risk | Guard |
|---|---|
| Tiny cohorts | widen fallback; confidence flags |
| Weight inflation | read‑time z; η caps |
| Conflicting signals | show decomposed terms; don’t mask traversal channel |

## 8) Integration
- **Inputs:** signals from `trace_reinforcement.md`;  
- **Store:** `log_weight` only; EMAs and baselines kept in side‑stores;  
- **Schedule:** after TRACE parse; batch apply; emit events.

## 9) Success criteria
- Stable distributions; explainable movements; improved retrieval/WM selection correlated with positive z. 

## 10) Open questions
- Confidence‑weighted seats; per‑author sharing; temporal decay of stale EMAs.
