---
title: Emotion‑Weighted Traversal (Resonance Gate)
status: draft
owner: @owner
last_updated: 2025-10-22
supersedes: []
depends_on:
  - emotion/emotion_coloring.md
  - runtime_engine/traversal_v2.md
---

# Emotion‑Weighted Traversal (Resonance Gate)

## 1) Context — The problem we’re solving
The system needs a way to **maintain coherent emotional context** during focused work: when we’re in a productive, appropriate state, traversal should **prefer emotionally aligned paths** so attention doesn’t scatter. We want this momentum **without** coupling emotion to activation or weights—purely as a **cost gate** that favors **resonance**. :contentReference[oaicite:8]{index=8}

## 2) Mechanism — What it is
Compute **resonance** between current affect \(A\) and a candidate’s stored \(E^{emo}\) (from Coloring). Use resonance to **reduce traversal cost** (make aligned paths cheaper) and **increase cost** for clashes—bounded, tunable, and composed with other gates. :contentReference[oaicite:9]{index=9}

### 2.1 Formal cost gate
Resonance \(r=\cos(A,E^{emo})\in[-1,1]\).  
**Multiplier**:
\[
m_{\text{res}}=\exp\!\big(-\lambda_{\text{res}}\cdot r\big),\quad m_{\text{res}}\in[m_{\min},m_{\max}]
\]
- \(r>0\) (aligned) → \(m_{\text{res}}<1\) (easier).  
- \(r<0\) (clash) → \(m_{\text{res}}>1\) (harder).  
Gate becomes neutral when \(A=\vec 0\) or \(E^{emo}=\vec 0\). Clamp to keep composition stable. :contentReference[oaicite:10]{index=10}

> Combine with Complementarity: order doesn’t matter if you multiply cost multipliers; measure effect sizes separately in telemetry.

## 3) Why this makes sense

### 3.1 Sub‑entity phenomenology
**Emotional momentum**: while confidently designing or joyfully exploring, nearby aligned material feels **easier** to move through, and clashing material feels **costly** to approach. The gate captures that pull. :contentReference[oaicite:11]{index=11}

### 3.2 Human bio‑inspiration
Cortical processing shows **state‑dependent facilitation**: when networks are tuned to a state, **aligned** inputs pass more easily; clashing ones require more control effort. Resonance approximates this **facilitation** as a soft bias.

### 3.3 Systems‑dynamics rationale
As a **bounded cost** modulation, resonance **preserves stability** and avoids self‑amplifying activation loops. Clamps and diminishing‑returns guards prevent “stuck mood” pathologies.

## 4) Expected resulting behaviors
- **Coherent trajectories** through emotionally uniform regions during focus.  
- **Inertia**: short‑term resistance to abrupt affect flips unless other gates (goal/complementarity) overcome it.  
- **Predictable detours**: clashing regions require more evidence/cost reductions to enter.

## 5) Why this algorithm vs alternatives
| Alternative | Why we don’t use it |
|---|---|
| Add activation to aligned nodes | Breaks single‑energy; creates runaway positive feedback. |
| Weight edits for coherence | Bleeds transient affect into long‑term memory; hard to unwind. |
| Hard filters (“only aligned”) | Brittle; ignores goals and regulation; harms exploration. |
| Linear, unbounded scaling | Instability when gates stack; exponent + clamps is safer. |

The proposed gate is **minimal, composable, bounded**, and yields interpretable telemetry. :contentReference[oaicite:12]{index=12}

## 6) Observability — How & what to measure, and how to interpret

### 6.1 Events/metrics
- **Per‑stride** (sampled): `stride.exec` add `{resonance: r, res_mult: m_res}`.  
- **Coherence Index**: fraction of selections with \(r>0\) weighted by magnitude.  
- **Stickiness**: probability of **same‑sign** affect across K frames vs baseline.  
- **Tradeoff plot**: share of selections explained by resonance vs complementarity vs goal.

### 6.2 Dashboards
- **Momentum dial**: moving average of Coherence Index.  
- **Cost landscape**: heatmap of \(m_{\text{res}}\) across recent frontier candidates.  
- **A/B panels**: task success when resonance is high vs low.

## 7) Failure Modes & Guards — Risks and why they're bad
| Risk | Why bad | Guard |
|---|---|---|
| Getting "stuck" in a mood | Reduces adaptability, harms regulation | Keep \(\lambda_{\text{res}}\) below \(\lambda_{\text{comp}}\) in recovery; **coherence persistence tracking + diminishing returns** (§7.1) |
| Over‑penalizing clashes | Blocks necessary corrective moves | Clamp \(m_{\max}\); allow goal or comp to override |
| Noisy/zero vectors | Unstable or spurious bias | Treat zero as neutral \(r=0\); require min magnitude |

### 7.1 Coherence Persistence Tracking & Lock-In Prevention (OPTIONAL)

**Problem:** Resonance has no memory of "how long have I been in this state?" — can maintain coherent affect indefinitely, which is productive for flow but pathological when stuck in unproductive states (rumination, anxiety spirals).

**Solution (OPTIONAL, feature-flagged):** Track consecutive frames in similar affective state; apply **diminishing returns** to \(\lambda_{\text{res}}\) after persistence threshold.

**Mechanism:**

```python
# Track consecutive frames in similar affective state
if cos(A_curr, A_prev) > COHERENCE_SIMILARITY_THRESHOLD:  # default: 0.85
    entity.coherence_persistence += 1
else:
    entity.coherence_persistence = 0

# Diminishing returns after P frames
P = COHERENCE_PERSISTENCE_THRESHOLD  # default: 20 frames
γ = COHERENCE_DECAY_RATE             # default: 0.05

if entity.coherence_persistence > P:
    excess = entity.coherence_persistence - P
    λ_res_effective = λ_res * exp(-γ * excess)
else:
    λ_res_effective = λ_res
```

**Effect:**
- First P frames (20) of coherence: full resonance strength → **productive focus/flow**
- After P frames: resonance weakens exponentially at rate γ (0.05) → **forced exploration**
- Prevents permanent lock-in while allowing productive coherence

**Feature flag:** `RES_DIMINISH_ENABLED` (default: false)

**Observability:**

```json
{
  "event": "affective_response.resonance",
  "entity_id": "...",
  "alignment": 0.85,
  "coherence_persistence": 12,
  "lambda_res_effective": 0.8,  // Diminishing returns applied
  "lock_in_risk": false
}
```

**Lock-in detection (alerts only, no automatic intervention):**

When `coherence_persistence > P` AND `affect_magnitude` staying high → emit `coherence.lock_in_detected` event for higher-level control to consider intervention.

**Why optional:** Base resonance mechanism is sound. This enrichment prevents pathological persistence but adds complexity. Enable when observing excessive state lock-in in telemetry.

## 8) Integration in code
- **Where**: `orchestration/mechanisms/sub_entity_traversal.py` in `rank_links()` / `choose_next_link()`.  
- **How**: compute \(r\) from \(A\) and \(E^{emo}\); apply \(m_{\text{res}}\) to cost; multiply with other gates.  
- **Config**: `RES_LAMBDA`, `RES_MIN_MULT`, `RES_MAX_MULT`.  
- **Events**: enrich `stride.exec`; Iris renders attribution alongside comp.

## 9) What success looks like
- **Behavioral**: higher **task throughput** during focus windows; fewer context breaks.  
- **Dynamics**: no increase in flip‑thrash; bounded effect sizes; healthy tradeoff with complementarity.  
- **UX**: attribution cards show resonance terms explaining link choice.

## 10) Open questions / future improvements / mistakes
- **Open**: Should resonance be per‑axis or full‑vector cosine only?  
- **Future**: learn \(\lambda_{\text{res}}\) per task type; schedule‑aware policies (focus vs recovery).  
- **Avoid**: using resonance to change **activation** or **weights**—keep it a cost gate.

**References**: Original Emotion‑Weighted Traversal cost spec. :contentReference[oaicite:13]{index=13}
