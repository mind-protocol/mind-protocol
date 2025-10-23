---
title: Emotion Complementarity (Regulation Gate)
status: draft
owner: @owner
last_updated: 2025-10-22
supersedes: []
depends_on:
  - emotion/emotion_coloring.md
  - runtime_engine/traversal_v2.md
---

# Emotion Complementarity (Regulation Gate)

## 1) Context — The problem we’re solving
The runtime needs a principled way to **move out of dysregulated affect** (e.g., fear/anger/sadness) toward **balancing** contexts, *without* injecting energy or silently mutating long‑term knowledge (weights). We want traversal to **prefer complementary affect** when regulation is appropriate (recovery, safety, decompression), while still allowing coherence (Resonance) during focused work. This formalizes the “opposites attract” pull as a **cost gate** for link/target selection—never as activation. :contentReference[oaicite:0]{index=0}

**Constraints**
- Respect the **single‑energy model** (emotion is metadata; links don’t carry activation).
- Works inside **two‑scale traversal** (entity boundary choices and local strides).
- Tunable by **intensity** and **context** (focus vs recovery), no magic constants.

## 2) Mechanism — What it is
At decision time, compute how **complementary** the active entity’s affect \(A\) is to a candidate element’s stored emotion \(E^{emo}\) (from Coloring). Use that complementarity to **reduce traversal cost** multiplicatively, gated by **current intensity** and **context**:
- **More intense emotions** → stronger pull to complementary targets.
- **Recovery context** → amplify regulation; **focused work** → attenuate it. :contentReference[oaicite:1]{index=1}

### 2.1 Formal cost gate
Let \(c = \max\{0,\ -\cos(A, E^{emo})\}\in[0,1]\) (0 when neutral/orthogonal, 1 for perfect opposites).  
Gates: \(g_{int}=\text{clip}(\|A\|,0,1)\), \(g_{ctx}\in[0,2]\) (≤1 focus; ≥1 recovery).  
**Cost multiplier**:
\[
m_{\text{comp}}=\exp\!\big(-\lambda_{\text{comp}}\cdot c\cdot g_{int}\cdot g_{ctx}\big),\quad m_{\text{comp}}\in[m_{\min},1]
\]
Apply \(m_{\text{comp}}\) to the base cost before other gates (e.g., goal, ease). Telemetry tunes \(\lambda_{\text{comp}}\), \(m_{\min}\). :contentReference[oaicite:2]{index=2}

> Note: Axis‑wise variants are acceptable when emotion bases are explicitly bipolar per axis; the cosine formulation remains compact and stable.

## 2.2) Multi-Pattern Affective Response (Optional V2, Feature-Flagged)

**⚠️ NOTE:** The base mechanism (§2.1) models **regulation only** (complementarity). This section defines an **optional** extension that adds rumination and distraction patterns, creating a unified affective response gate.

**Status:** OPTIONAL, behind `AFFECTIVE_RESPONSE_V2` flag (default: false). Base complementarity is sound; this adds phenomenological richness at the cost of complexity.

---

### Combined Pattern Architecture

Instead of complementarity alone, define **three competing affective response patterns**:

1. **Regulation (complementarity)** — seek opposite affect (anxious → calm)
2. **Rumination (amplification)** — seek same affect (anxious → more anxiety)
3. **Distraction (orthogonality)** — seek unrelated affect (anxious → orthogonal content)

**Unified multiplier** (weighted sum of three patterns):

\[
m_{affect} = w_{reg} \cdot m_{reg} + w_{rum} \cdot m_{rum} + w_{dist} \cdot m_{dist}
\]

where \(w_{reg} + w_{rum} + w_{dist} = 1\) (softmax over pattern scores).

---

### Pattern Definitions

**Pattern 1: Regulation (complementarity)**

\[
c_{reg} = \max\{0, -\cos(A, E^{emo})\}  \quad \text{// Opposite affect}
\]
\[
m_{reg} = \exp(-\lambda_{reg} \cdot c_{reg} \cdot g_{int} \cdot g_{ctx})
\]

**Pattern 2: Rumination (amplification)**

\[
c_{rum} = \max\{0, \cos(A, E^{emo})\}  \quad \text{// SAME affect (aligned, not opposite)}
\]
\[
m_{rum} = \exp(-\lambda_{rum} \cdot c_{rum} \cdot g_{int} \cdot g_{rum\_ctx})
\]

Where \(g_{rum\_ctx}\) is HIGH when: low control capacity, negative valence, high uncertainty.

**Pattern 3: Distraction (orthogonality)**

\[
c_{dist} = 1 - |\cos(A, E^{emo})|  \quad \text{// Perpendicular (neither aligned nor opposite)}
\]
\[
m_{dist} = \exp(-\lambda_{dist} \cdot c_{dist} \cdot g_{int} \cdot g_{dist\_ctx})
\]

Where \(g_{dist\_ctx}\) is HIGH when: overwhelm, depletion, unbearable affect intensity.

---

### Pattern Weight Learning

**Pattern scores** (context-dependent, per-frame):

```python
score_reg = control_capacity * (1 if recovery_mode else 0.5)
score_rum = (1 - control_capacity) * (1 if valence < -0.3 else 0)
score_dist = depletion_level * tanh(affect_magnitude)
```

**Pattern weights** (softmax over scores):

```python
w_reg, w_rum, w_dist = softmax([score_reg, score_rum, score_dist])
```

**Learning via EMA on effectiveness:**

Track outcomes for each pattern:
- Did regulation reduce affect intensity? (Δ||A|| after N frames)
- Did rumination lead to spiral? (affect saturation, task failure)
- Did distraction enable recovery? (affect reduction, task resumption)

Update pattern preferences based on recent effectiveness (EMA with α = 0.1).

**Default pattern weights (before learning):** [0.5, 0.3, 0.2] for regulation/rumination/distraction.

---

### Guards

**Rumination cap:**
Limit consecutive frames rumination can dominate to prevent spirals:

```python
if rumination_frames_consecutive > RUMINATION_CAP:  # default: 10 frames
    w_rum = 0  # Force pattern switch
    rumination_frames_consecutive = 0
```

**Multiplier clamp:**
Ensure combined multiplier stays bounded:

```python
m_affect = max(M_AFFECT_MIN, min(M_AFFECT_MAX, m_affect))
# Default: [0.6, 1.0]
```

---

### Configuration Parameters

**Add to** `orchestration/core/settings.py`:

```python
# === MULTI-PATTERN AFFECTIVE RESPONSE (OPTIONAL) ===
# Feature flag
AFFECTIVE_RESPONSE_V2 = False  # Enable multi-pattern (reg/rum/dist)

# Pattern lambdas
LAMBDA_REG = 0.5   # Regulation strength
LAMBDA_RUM = 0.3   # Rumination strength
LAMBDA_DIST = 0.2  # Distraction strength

# Pattern weights (initial, before learning)
PATTERN_WEIGHTS_INITIAL = [0.5, 0.3, 0.2]  # [reg, rum, dist]

# Guards
RUMINATION_CAP = 10         # Max consecutive frames rumination can dominate
M_AFFECT_MIN = 0.6          # Multiplier floor
M_AFFECT_MAX = 1.0          # Multiplier ceiling (no cost reduction in this version)

# Learning
PATTERN_EFFECTIVENESS_EMA_ALPHA = 0.1  # Learning rate for pattern weights
```

---

### Observability

```json
{
  "event": "affective_response.pattern_selected",
  "entity_id": "...",
  "pattern_scores": {"reg": 0.6, "rum": 0.3, "dist": 0.1},
  "pattern_weights": {"reg": 0.5, "rum": 0.3, "dist": 0.2},
  "selected_pattern": "regulation",
  "rumination_frames_consecutive": 0,
  "m_affect": 0.85
}
```

---

**Why optional:** The base complementarity mechanism is phenomenologically sound for regulation. Multi-pattern adds rumination (spirals) and distraction (avoidance), which are real but add significant complexity. Enable when modeling pathological or nuanced affect dynamics.

---

## 3) Why this makes sense

### 3.1 Sub‑entity phenomenology
When anxious, we are **drawn to calm**; when sad, to **joyful or warm** places. Complementarity encodes that pull, so boundary and local choices **seek balancing landings** that reduce perceived stress. :contentReference[oaicite:3]{index=3}

### 3.2 Human bio‑inspiration
This mirrors **affective regulation** and **allostatic control**: the system actively seeks states that **counter** current affect, rather than passively remaining in it. Complementarity is not sedation—it’s targeted **counter‑pressure** toward equilibrium. :contentReference[oaicite:4]{index=4}

### 3.3 Systems‑dynamics rationale
By keeping complementarity as a **bounded cost gate**, we avoid hard flips in activation that can cause **oscillation**. Intensity/context gates provide **closed‑loop control** that modulates the intervention strength based on “how off‑center” we are and “what mode we’re in.” :contentReference[oaicite:5]{index=5}

## 4) Expected resulting behaviors
- **Regulatory paths**: from high‑arousal or negative valence regions toward stabilizing, calmer, or uplifting regions.
- **Faster recovery**: reduced time‑to‑neutral or time‑to‑target‑affect after a perturbation.
- **Boundary preference**: when multiple cross‑entity exits exist, preference for exits colored with opposite affect.
- **Tie‑breaking**: when semantics tie, **affect** tips the choice toward balance.

## 5) Why this algorithm vs alternatives
| Alternative | Why we don’t use it |
|---|---|
| Add activation toward “calm” nodes | Violates single‑energy model; creates runaway and brittle dependence on labels. |
| Directly edit weights for regulation | Conflates temporary mood with long‑run knowledge; leaves hard‑to‑revert scars. |
| Hard rule “if anxious → always go to calm” | Ignores task context; harms focus; yields oscillation. |
| Linear, unbounded cost subtraction | Unstable under composition with other gates; exponential multiplier + clamps is more robust. |

This gate is **declarative, bounded, tunable**, and composes with other gates safely. :contentReference[oaicite:6]{index=6}

## 6) Observability — How & what to measure, and how to interpret

### 6.1 Events/metrics
- **Per‑stride** (sampled): `stride.exec` include `{comp_score: c, gates:{int,ctx}, comp_mult: m_comp}`.  
- **Per‑frame**: mean/median \(c\) on chosen links; **Regulation Index** = fraction of selections where \(m_{\text{comp}}<1\).  
- **Recovery KPI**: **Δ‑to‑neutral** time compared A/B (gate on/off), **AUC affect** during recovery window.  
- **Effect size**: Δ selection probability vs baseline for complementary candidates matched on base cost.

### 6.2 Dashboards
- **Regulation vs Coherence** (complementarity vs resonance contribution over N frames).  
- **Boundary Sankey**: where complementary exits occur; how often they shorten return‑to‑neutral.  
- **Intensity gating strip**: show comp multiplier vs \(\|A\|\) histogram to verify monotonicity.

## 7) Failure Modes & Guards — Risks and why they’re bad
| Risk | Why bad | Guard |
|---|---|---|
| Over‑correction / ping‑pong | Oscillation across opposite poles | Clamp \(m_{\text{comp}}\), context cooldowns, EMA on \(A\) |
| Regulation during focus | Derails task pursuit | Context gate \(g_{ctx}\le 1\) in focus; task‑aware disable |
| Saturation by noisy emotion | Misleading choices | Dwell/attention gates in Coloring; minimum \(\|A\|\) to activate |
| Hidden bias | Gate dominates others | Monitor **Regulation Index**; SDT targets; regular A/B toggles |

## 8) Integration in code
- **Where**: `orchestration/mechanisms/sub_entity_traversal.py` in `rank_links()` / `choose_next_link()`.  
- **How**: read \(A\) (active entity affect) and \(E^{emo}\) for candidates; compute \(c\), gates; apply \(m_{\text{comp}}\) to **cost** (not activation).  
- **Config**: `core/settings.py` → `COMPLEMENTARITY_LAMBDA`, `COMP_MIN_MULT`, gates policy.  
- **Events**: `adapters/ws/traversal_event_emitter.py` enriches `stride.exec`.

## 9) What success looks like
- **Behavioral**: statistically significant reduction in **time‑to‑neutral** after stressors; improved **task resumption** probability post‑recovery.  
- **Dynamics**: no rise in flip‑thrash; spectral proxy \(\rho\) unchanged or improved during recovery episodes.  
- **UX**: attribution cards show comp factors clearly on decisions.

## 10) Open questions / future improvements / common mistakes
- **Open**: Learn \(g_{ctx}\) from telemetry vs rules? Multi‑objective controller for focus vs recovery?  
- **Future**: per‑axis sensitivity (fear↔security stronger than boredom↔curiosity); learned \(\lambda_{\text{comp}}\) via bandits.  
- **Avoid**: using complementarity to nudge **weights** or to inject **activation**—breaks the model.

**References**: Original Complementarity mechanism notes. :contentReference[oaicite:7]{index=7}
