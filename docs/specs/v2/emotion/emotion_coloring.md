---
title: Emotion Coloring
status: draft
owner: @owner
last_updated: 2025-10-22
supersedes: []
depends_on:
  - foundations/activation_energy.md
  - foundations/decay.md
  - runtime_engine/traversal_v2.md
---

# Emotion Coloring

## 1) Context — The problem we’re solving

The runtime needs a way to **retain and read out the emotional context** of recent thinking without violating the single‑energy substrate. We want traversal to “remember” that a region felt calm, tense, joyful, etc., so later choices can use that information to regulate or sustain mood—**without** injecting activation or silently altering weights. Earlier mechanism notes captured this as “coloring” during traversal; here we make it explicit, measurable, and safe. :contentReference[oaicite:1]{index=1}

**Constraints**
- **Single‑energy model:** one activation scalar per node; entities derive energy from members; **links store no activation**. Emotion must be **metadata only**, with its own decay. 
- **Two‑scale traversal:** between‑entity jumps + within‑entity atomic strides. Emotion should inform **cost/valence**, not energy. 
- **No magic constants:** All gains and caps are tunable, telemetry‑driven.

**Target outcome**
- An emotionally informed substrate where traversal can **sense** (not **be driven by**) prior affect, enabling **regulation** (seek balance) and **coherence** (stay aligned), which are realized by separate cost modulators (Complementarity and Resonance). 


## 2) Mechanism — What it is (short description)

As the system traverses nodes/links, it writes the active entity’s affect vector to those elements as **emotion metadata** (bounded, normalized, decaying). This **does not change activation energy or weights**. Later, traversal reads this metadata to modulate **cost** (not energy) via:
- **Complementarity**: opposite affect reduces cost (regulatory pull). :contentReference[oaicite:3]{index=3}  
- **Resonance**: similar affect reduces cost (coherence pull). :contentReference[oaicite:4]{index=4}

Coloring is **additive‑with‑caps + decay**, producing a durable yet fading emotional memory. :contentReference[oaicite:5]{index=5}


## 3) Why this makes sense

### 3.1 Sub‑entity phenomenology
- When we’ve worked in an anxious patch of ideas, nearby thoughts **feel** tense later; calm areas feel soothing. Coloring externalizes that felt tone on the graph, letting subsequent sub‑entities read it back.
- It matches the subjective report that “**context keeps a mood**” and “returning to a place **brings back a feeling**,” without conflating feeling with **salience/activation**.

### 3.2 Human bio‑inspiration
- **Affective context tagging** resembles limbic modulation of cortical traces: affect binds with memory, yet **doesn’t equal arousal**; arousal (activation) and valence (feeling) are separable signals.
- **Persistence with forgetting**: emotions linger longer than attention but decay with time—captured via slower decay than activation. :contentReference[oaicite:6]{index=6}

### 3.3 Systems‑dynamics rationale
- Keeping emotion as a **separate, bounded state** avoids unstable feedback loops (e.g., positive feedback from “feeling → more activation → more feeling”). 
- Using emotion only in **cost modulators** (Complementarity/Resonance) yields **stable, tunable pressures** that do not alter conservation of activation or the decision thresholds. 


## 4) Expected resulting behaviors

- **Emotional memory**: traversed regions accrue a characteristic affect signature that fades slowly. :contentReference[oaicite:8]{index=8}
- **Momentum vs regulation**: depending on context, traversal either maintains mood (Resonance) or seeks balance (Complementarity). 
- **Better disambiguation**: when content is semantically similar, the emotional layer breaks ties based on recent needs (e.g., “safe vs exciting” next steps).
- **UI interpretability**: viz can tint nodes/links by emotion to communicate “why” a path was chosen without exposing sensitive content.


## 5) Algorithm — Detailed

### 5.1 Inputs
- Active entity’s **affect vector** \(A \in \mathbb{R}^d\), \(\|A\|\in[0,1]\).
- Node/link’s stored **emotion vector** \(E^{emo}\) (metadata).
- Tick duration \(\Delta t\) and **decay** parameters (type‑dependent).

### 5.2 Coloring update (on visit/stride)
- **Rule (EMA‑style with cap & hysteresis)**  
  \(E^{emo} \leftarrow \text{clip}_{\|.\|\le M}\Big(\alpha\,E^{emo} + \beta \cdot g \cdot A\Big)\)  
  where:
  - \(\alpha \in (0,1]\): retention factor (near 1; slow forgetting).
  - \(\beta \in (0,1]\): coloring rate (telemetry‑tuned).
  - \(g \in [0,1]\): gating from dwell time, attention, current entity energy (as a **multiplier**, not energy transfer), and \(\|A\|\).  
  - \(M\): max magnitude cap; small **hysteresis** around \(M\) to avoid flicker.  
  - Optional **per‑type caps** (e.g., Memory nodes retain more).

- **Neutral handling**: If \(A=\vec{0}\), skip write; if \(E^{emo}\) absent, initialize to \(\vec{0}\).

- **No activation or weight changes here**; this is **metadata only**. :contentReference[oaicite:10]{index=10}

### 5.3 Decay (per tick)
- \(E^{emo} \leftarrow \lambda^{\Delta t} \cdot E^{emo}\), with \(\lambda = \exp(-\eta_{emo})\), \(\eta_{emo} \ll \eta_{act}\) (emotions linger longer than activation). Type‑dependent overrides may apply. :contentReference[oaicite:11]{index=11}

### 5.4 How traversal consumes emotion (separate mechanisms)
- **Complementarity (regulation)** lowers cost for **opposites**; intensity & context gate the effect. :contentReference[oaicite:12]{index=12}
- **Resonance (coherence)** lowers cost for **similarity**; clamps prevent getting stuck. :contentReference[oaicite:13]{index=13}

### 5.5 Parameterization & defaults (telemetry‑tuned, not constants)
- \(\beta\) initial 0.05–0.15, \(\alpha\approx 0.98\) per tick (example), \(M\in[0.6,1.0]\) depending on node type.
- Dwell threshold to prevent micro‑staining (e.g., ≥ one micro‑tick).
- All defaults backed by **data‑driven** tuning loops (SDT targets on downstream selection effects).


## 6) Affective Coupling (Bounded, Optional)

**⚠️ ARCHITECTURE INVARIANT: NO ENERGY INJECTION**

The base mechanism (§5) treats emotion as **metadata only** — it does not affect activation or weights. This section defines **optional** couplings that modulate thresholds and weight updates via **bounded functions**. All coupling is:
- **Behind feature flags** (opt-in; can disable if ρ unstable)
- **Bounded by tanh gates** (no runaway feedback)
- **Small default parameters** (conservative tuning)
- **Observable** (all affective contributions tracked in events)

**Affect does NOT inject activation energy.** It only MODULATES thresholds and weight learning. ρ-control (criticality regulation) remains the primary stability lever.

---

### 6.1 Bounded Affect→Activation (Threshold Modulation)

**Mechanism:**
Current threshold: \(\Theta_i = \mu + z\cdot\sigma + f(\rho) - b\cdot\log(W_i)\)

**With affective coupling (OPTIONAL):**
\(\Theta_i = \mu + z\cdot\sigma + f(\rho) - b\cdot\log(W_i) - h(A, E^{emo})\)

Where \(h(A, E^{emo})\) is **bounded affective threshold reduction:**

\[
h(A, E^{emo}) = \lambda_{aff} \cdot \tanh\big(\|A\| \cdot \cos(A, E^{emo})\big) \cdot \text{clip}(\|E^{emo}\|, 0, 1)
\]
\[
\text{where } \lambda_{aff} = 0.08 \cdot \sigma(\text{node.type}) \quad \text{// ~8\% of type's energy std dev}
\]

**Properties:**
- **Bounded:** tanh ensures \(-\lambda_{aff} \le h \le \lambda_{aff}\) (no runaway)
- **Congruence-gated:** \(\cos(A, E^{emo})\) means only affect-aligned nodes get threshold reduction
- **Intensity-scaled:** \(\|A\|\) means stronger entity affect → stronger effect
- **Coloring-magnitude aware:** \(\|E^{emo}\|\) means freshly/strongly colored nodes affected more
- **Type-relative:** \(\lambda_{aff}\) scales with type's typical energy variation

**Effect:**
- Affect-congruent nodes activate more easily (lower threshold)
- Creates **mood-congruent recall** and **intrusive thoughts** when affect intense
- Bounded by tanh and type-relative \(\lambda_{aff}\)

**Feature flag:** `AFFECTIVE_THRESHOLD_ENABLED` (default: false)

**Safety:**
- Default \(\lambda_{aff} = 0.08\cdot\sigma(\text{type})\) is conservative
- Monitor ρ (criticality); if unstable, disable flag
- Observability tracks affective contribution separately in `theta_components.affective_reduction`

---

### 6.2 Bounded Affect→Weight (Memory Enhancement)

**Mechanism:**
Current weight learning: \(\Delta\log W_i = \eta \cdot (\alpha_{flip}\cdot z_{flip} + \alpha_{gap}\cdot z_{gap} + \alpha_{wm}\cdot z_{wm} + \alpha_{trace}\cdot z_{trace})\)

**With affective coupling (OPTIONAL):**
\[
\Delta\log W_i = \eta \cdot m_{affect} \cdot (\alpha_{flip}\cdot z_{flip} + \alpha_{gap}\cdot z_{gap} + \alpha_{wm}\cdot z_{wm} + \alpha_{trace}\cdot z_{trace})
\]

Where:
\[
m_{affect} = \max(m_{min}, 1 + \kappa \cdot \tanh(\|E^{emo}\|))
\]
\[
\text{// Default parameters: } \kappa = 0.3, \quad m_{min} = 0.6
\]

**Properties:**
- **Multiplicative boost:** high-affect experiences get amplified weight updates
- **Bounded:** \(\tanh(\|E^{emo}\|) \in [0,1]\), so \(m_{affect} \in [m_{min}, 1+\kappa] = [0.6, 1.3]\)
- **Neutral-safe:** when \(E^{emo} = 0\), \(m_{affect} = 1\) (no effect)
- **Asymmetric:** only amplifies, never weakens (negative affect still strengthens memory)
- **Floor-protected:** \(m_{min}\) prevents pathological dampening

**Effect:**
- Emotionally intense experiences form stronger memories (up to 30% boost)
- High-affect nodes have higher long-run weights → surface more in future retrieval
- Matches phenomenology: we remember what made us feel

**Feature flag:** `AFFECTIVE_MEMORY_ENABLED` (default: false)

**Safety:**
- Conservative \(\kappa = 0.3\) (max 30% boost)
- Floor \(m_{min} = 0.6\) prevents over-dampening
- Monitor weight distributions; if saturation, reduce \(\kappa\)
- Mean-centering per type/scope (existing mechanism) prevents runaway

---

### 6.3 Configuration Parameters

**Add to** `orchestration/core/settings.py`:

```python
# === AFFECTIVE COUPLING (OPTIONAL) ===
# Feature flags (all default: false)
AFFECTIVE_THRESHOLD_ENABLED = False  # Enable affect→threshold modulation
AFFECTIVE_MEMORY_ENABLED = False     # Enable affect→weight amplification

# Affective threshold modulation (λ_aff is type-relative, computed at runtime)
AFFECTIVE_THRESHOLD_LAMBDA_FACTOR = 0.08  # Multiplier of σ(type), ~8%

# Affective memory enhancement
AFFECTIVE_MEMORY_KAPPA = 0.3  # Max boost factor (1.3x at saturation)
AFFECTIVE_MEMORY_MIN = 0.6    # Floor to prevent over-dampening
```

---

### 6.4 Observability Enrichments

**Enrich existing events:**

```json
{
  "event": "node.activation.computed",
  "node_id": "...",
  "E": 0.7,
  "theta": 0.5,
  "theta_components": {
    "base": 0.45,
    "criticality_penalty": 0.05,
    "weight_anchoring": -0.05,
    "affective_reduction": 0.05  // NEW
  },
  "affective_alignment": 0.8,  // NEW
  "activated": true
}
```

```json
{
  "event": "weights.updated.flip",  // or .gap, .wm, .trace
  "node_id": "...",
  "delta_log_w": 0.15,
  "affective_multiplier": 1.3,  // NEW
  "emotion_magnitude": 0.7      // NEW
}
```

---

## 8) Why this algorithm vs alternatives

| Alternative | Why we reject it |
|---|---|
| **Store emotion as activation** (inject E) | Violates single‑energy model; couples mood to thresholds; risks runaway feedback. |
| **Edit weights on coloring** | Conflates long‑run knowledge with transient affect; hard to undo; biases retrieval globally. |
| **Entity‑only emotion (no per‑node/link metadata)** | Loses spatial granularity; can’t capture that *this* edge felt safe while the other felt thrilling. |
| **Scalar “mood id” per element** | Too coarse; can’t support complementarity/resonance along multiple axes simultaneously. |
| **Unbounded additive coloring** | Saturates; destroys discriminability; hard to recover without harsh resets. |

This design keeps emotion **decoupled** from activation & weights, **bounded**, **decaying**, and **useful** to traversal through **separate, inspectable cost gates**.


## 9) Observability — How & what we measure, and how to make it meaningful

### 9.1 What to capture (events/metrics)
- **Events** (deltas):  
  - `node.emotion.update` / `link.emotion.update` with `{id, ||Eemo||, top_axes, dmag}` for sampled touches.  
  - `stride.exec` enriched with `{resonance, comp_score, res_mult, comp_mult}` to attribute decisions to emotion gates. 
- **Metrics** (per frame, per entity, and global):  
  - Mean/median **emotion magnitude** over frontier and WM.  
  - **Skew** of emotion axes (e.g., fear→security balance) in the active region.  
  - **Coloring throughput**: number of elements updated per tick; average **Δmag**.  
  - **Half‑life estimates** for emotion decay per type (fit EWMA).
  - **Effect sizes**: Δ selection probability vs baseline when resonance/complementarity active (A/B gated).

### 9.2 Translating to meaningful info (dashboards)
- **“Mood map”**: entity bubbles tinted by centroid affect with **hysteresis**, edges showing top complementary vs resonant routes (stacked bars of comp/res multipliers).  
- **Regulation vs coherence index**: ratio of comp‑driven to res‑driven selections last N frames.  
- **Staining watch**: histogram of \(\|E^{emo}\|\) by type; red‑flag tails (saturation).  
- **Attribution cards**: for a chosen stride, show raw \(A\), local \(E^{emo}\), and final cost after gates.

These surfaces keep emotion **explanatory**, not occult. :contentReference[oaicite:16]{index=16}


## 10) Failure Modes & Guards — Risks and why they're bad

| Risk | Why it’s bad | Guards |
|---|---|---|
| **Saturation / over‑coloring** | Flattens discrimination; everything looks the same | Magnitude cap \(M\); per‑type caps; decay; dwell threshold; per‑tick color budget |
| **Micro‑staining from fly‑bys** | Spurious signals pollute edges | Minimum dwell time / attention gate; lower β at high velocity |
| **Emotion drift from noise** | Mood “creeps” without cause | EMA retention with small β; require consistent touches to move centroid |
| **Self‑reinforcing loops via gates** | Unstable dynamics | Keep emotion in **cost only**; clamp resonance/complementarity multipliers; monitor rho/flip rates |
| **Privacy/interpretation risk** | Over‑reading private affect | Only vectors + magnitudes; no raw prompts; UI shows **ranges**, not labels |

Guards keep the emotional layer **bounded, legible, and safe**. :contentReference[oaicite:17]{index=17}


## 11) Integration in the codebase (where and how)

- **Write phase (on traversal):**  
  `orchestration/mechanisms/sub_entity_traversal.py`  
  - In `process_node()` and `choose_next_link()` hooks, call `color_element(element, A, gates)` which implements §5.2.  
- **Decay phase (per tick):**  
  `orchestration/mechanisms/consciousness_engine_v2.py`  
  - Tick loop calls `emotion_decay(graph, dt)` implementing §5.3.  
- **Consumption (cost gates):**  
  `orchestration/mechanisms/sub_entity_traversal.py`  
  - Complementarity and Resonance gates read `E^{emo}` to adjust **cost** only.   
- **Events & UI:**  
  `orchestration/adapters/ws/traversal_event_emitter.py` emits `node.emotion.update`, enriched `stride.exec`; Iris renders tint with hysteresis.

**Config:** default caps/β/α in `core/settings.py`; structured logs via `core/logging.py`.


## 12) What success looks like

- **Behavioral**:  
  - Regions previously traversed in a mood are measurably more/less attractive via comp/res multipliers (stat‑sig effect sizes).  
  - Agents **recover** from high‑arousal regions faster with complementarity enabled vs disabled (lower time‑to‑calm).  
- **Systems**:  
  - No increase in flip thrash or spectral radius spikes from turning on coloring.  
  - Saturation rate stays below threshold (e.g., ≤5% of nodes exceeding 0.9 magnitude).
- **UX**:  
  - Attribution cards explain "why this edge" in terms of comp/res + emotion magnitudes.


## 13) Open questions, future improvements, and common mistakes

**Open questions**
- Emotion basis: fixed axes vs learned latent factors? How many dimensions are enough?  
- Context gates: Should recovery/focused modes be entity‑local or global control?  
- Type‑dependent half‑lives: which classes deserve longer affect memory?

**Future improvements**
- **Counter‑coloring**: on regulation completion, gently neutralize extreme traces.  
- **Contrastive tuning**: learn β/α per type to hit target SDT curves automatically.  
- **Path‑level summaries**: maintain short‑horizon rolling affect for sequences (not only per element).

**Common mistakes to avoid**
- Treating emotion as **activation** (breaks thresholds; destabilizes).  
- Writing color on **every micro‑touch** (noise).  
- Using color to **edit weights** (couples transient affect to long‑term knowledge).  

---

**References**
- Original “Emotion Coloring During Traversal” notes (mechanism intent, persistence/decay, use in later traversal). :contentReference[oaicite:19]{index=19}  
- Complementarity (opposites reduce cost; regulation gate). :contentReference[oaicite:20]{index=20}  
- Emotion‑weighted traversal / Resonance (similarity reduces cost; coherence gate). :contentReference[oaicite:21]{index=21}
```