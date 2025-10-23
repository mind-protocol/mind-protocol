---
title: Context Reconstruction (Stimulus → Traversal → Emergent Pattern)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/02_context_reconstruction.md
depends_on:
  - foundations/activation_energy.md
  - runtime_engine/traversal_v2.md
  - learning_and_trace/link_strengthening.md
  - entity_layer/stimulus_injection.md
---

# Context Reconstruction

## 1) Context — The problem we’re solving
We routinely **resume** old threads after minutes/hours/days. Nothing stores a “context snapshot”; instead, **stimuli** reactivate entry nodes and **traversal** rebuilds a **pattern** similar to the past one. We need a crisp, stable mechanism that does this on the single‑energy substrate (no per‑entity buffers on nodes), with **two‑scale traversal** and **bounded costs**. :contentReference[oaicite:13]{index=13}

## 2) Mechanism — What it is
A **context** is an **emergent activation pattern** over nodes, summarized at the **entity** scale (entities aggregate member activations). Reconstruction = **stimulus injection** + **budgeted, weighted traversal** (diffusion via chosen strides) under criticality control. No stored snapshots. :contentReference[oaicite:14]{index=14}

### 2.1 Steps
1) **Identify entry nodes** from stimulus (semantic match + explicit refs).
2) **Inject activation** to **nodes** only (entity aggregation happens implicitly).
3) Run **two‑scale traversal** for K ticks (between‑entity choices then within‑entity strides).
4) **Summarize**: entity energies (derived), active members, boundary links, WM selection.
5) Optionally compute **similarity** to a prior observed pattern for analytics.

### 2.2 Affective Priming (Budget Bias, Optional)

**⚠️ STATUS:** OPTIONAL enrichment, behind `AFFECTIVE_PRIMING_ENABLED` flag (default: false).

**Problem:** Pure semantic matching for stimulus injection ignores recent affective context. If the system just experienced anxiety about a topic, semantically-related but affect-congruent seeds should be slightly preferred over neutral matches.

**Mechanism:** Bias injection budget toward **affect-congruent entry nodes** by reading their `E^emo` (emotion coloring) and comparing to recent active entity affect.

**Affective priming formula:**

When selecting entry nodes for stimulus injection, compute match score:

\[
\text{score}_i = \underbrace{s_{\text{semantic}}}_{\text{baseline match}} \cdot \underbrace{(1 + p \cdot r_{\text{affect}})}_{\text{affective boost}}
\]

where:
- \(s_{\text{semantic}}\) is standard semantic/embedding similarity ∈ [0,1]
- \(p\) is **priming strength** (small, e.g., 0.15 = max 15% boost)
- \(r_{\text{affect}} = \cos(A_{\text{recent}}, E^{emo}_i)\) ∈ [-1,1] is affect alignment
  - \(A_{\text{recent}}\) = EMA of recent active entity affects (last N frames)
  - \(E^{emo}_i\) = emotion coloring on candidate entry node

**Properties:**
- **Small bounded boost:** Max 15% advantage for perfectly aligned affect
- **Reuses coloring vectors:** No new affect infrastructure needed
- **Neutral-safe:** When \(A_{\text{recent}} = \vec{0}\) or \(E^{emo}_i = \vec{0}\), boost = 0
- **Budget redistribution:** Doesn't inject more total energy, just **biases** which seeds get it

**Effect:**
- **Mood-congruent reconstruction:** Anxious system more likely to start from anxiety-related seeds
- **Affective continuity:** Reconstruction picks up where the previous affective state left off
- **Subtle bias:** Doesn't override strong semantic matches, just tips ties

**Example:**

```python
# Recent active entities had A_recent = [0.8 anxiety, 0.2 urgency, ...]
# Stimulus: "check schema validation"

# Candidate entry nodes:
# - node_A: "schema validation" (semantic=0.9, E_emo=[0.7 confidence, ...])
#   → score = 0.9 * (1 + 0.15 * cos([anxiety], [confidence]))
#           ≈ 0.9 * (1 - 0.10) = 0.81

# - node_B: "schema errors" (semantic=0.85, E_emo=[0.8 anxiety, ...])
#   → score = 0.85 * (1 + 0.15 * cos([anxiety], [anxiety]))
#           ≈ 0.85 * (1 + 0.15) = 0.98

# node_B gets slight priority despite lower semantic match
```

**Feature flag:** `AFFECTIVE_PRIMING_ENABLED` (default: false)

**Configuration:**
```python
AFFECTIVE_PRIMING_ENABLED = False
AFFECTIVE_PRIMING_STRENGTH = 0.15  # p: max 15% boost
AFFECTIVE_PRIMING_WINDOW = 20      # frames for A_recent EMA
AFFECTIVE_PRIMING_MIN_MAGNITUDE = 0.3  # ignore weak affects
```

**Observability:**

Enrich `stimulus.inject` event:

```json
{
  "event": "stimulus.inject",
  "targets": ["node_A", "node_B", "node_C"],
  "budget": 1.0,
  "affective_priming_active": true,
  "recent_affect_magnitude": 0.75,
  "primed_nodes": ["node_B"],
  "priming_boost": {"node_B": 0.13}
}
```

**Guards:**
- **Small cap:** p ≤ 0.20 (never more than 20% boost)
- **Magnitude threshold:** Only apply when \(\|A_{\text{recent}}\| > 0.3\) (ignore weak affects)
- **Budget conservation:** Total injected energy unchanged, only distribution shifts
- **Fallback:** If no affect-aligned seeds found, proceed with pure semantic matching

**Why optional:** Base semantic matching is sound. Affective priming adds phenomenological continuity (mood persists across reconstructions) but may bias toward rumination if not guarded. Enable when observing jarring affective discontinuities in context switches.

---

## 3) Why this makes sense

### Phenomenology
Seeing the Telegram badge triggers Alice‑related nodes; flows re‑activate related concepts until a familiar **chunk** emerges (“Ah, Alice’s schema question”). The reconstructed pattern is **similar, not identical**—drift is expected. :contentReference[oaicite:15]{index=15}

### Bio‑inspiration
Hippocampal pattern completion: partial cues re‑instantiate a distributed pattern; no perfect replay.

### Systems‑dynamics
Keeping reconstruction as **activation + traversal** avoids state duplication and integrates with **criticality** and **decay** cleanly.

## 4) Expected behaviors
- **Non‑linear resumption**: jump to a task from hours ago with no stack unwind.  
- **Partial reconstruction** under decay: enough to act, not necessarily full detail.  
- **Goal/affect modulation** (complementarity/resonance) adjusts the chosen route, not the physics.

## 5) Why this vs alternatives
| Alternative | Problem | This mechanism |
|---|---|---|
| Storing context snapshots | Heavy, goes stale | Always fresh; graph is the memory |
| Per‑entity buffers on nodes | State explosion; unstable | Single‑energy + entity aggregation |
| Uniform diffusion | Expensive, noisy | Budgeted strides guided by weights |

## 6) Observability — How & what to measure, and how to read it
**Events**  
- `stimulus.inject{targets, budget, K_eff}`, `stride.exec{src,dst,ΔE,φ}`, `wm.emit{entities,members}`, `se.boundary.summary{S→T}`.

**Metrics**  
- **Reconstruction similarity** (vs reference pattern) using set or embedding overlap; **time‑to‑reconstruct**; **energy radius** growth; **AUC of entity energies** during reconstruction window. Use these to tune K ticks and budgets. :contentReference[oaicite:16]{index=16}

**Dashboards**  
- Animated **frontier** + emergent **entity bubbles**; attribution overlays (goal, comp/res multipliers).

## 7) Failure modes & risks
| Risk | Why bad | Guard |
|---|---|---|
| Over‑ or under‑reconstruction | Miss memory vs waste compute | Adaptive ticks & budget by urgency |
| Drift too strong | Wrong recall | Anchors (few high‑weight nodes) in critical contexts |
| Ambiguous entry | Wrong branch | Use immediately‑prior active set as disambiguation prior |

## 8) Integration in code
- **Where**: `entity_layer/stimulus_injection.py` (targets + injection), `mechanisms/sub_entity_traversal.py` (two‑scale), `mechanisms/consciousness_engine_v2.py` (tick loop & ρ‑control).  
- **Similarity**: analytics helper `context_similarity(snapshot_a, snapshot_b)`; *snapshots are ephemeral* (not persisted). :contentReference[oaicite:17]{index=17}

## 9) Success criteria
- 100–300 ms typical reconstructions; similarity **0.6–0.8** on scenarios like Telegram/Alice (empirical).  
- Stable ρ during bursts; WM picks coherent entities; operators can *see* why.

## 10) Open questions / improvements / mistakes to avoid
- Learn **urgency→ticks** mapping; richer priors for disambiguation.  
- **Avoid** storing contexts as objects; treat them as measurements only.

````

### B. Changes made

* Removed per‑subentity energy math; **inject to nodes**, aggregate to entities.
* Replaced “diffuse everything” with **budgeted strides** + two‑scale traversal.
* Added **observability** and **success metrics**; clarified similarity as analytics only. 

### C. Compliance matrix

| Spec point                                       | Status |
| ------------------------------------------------ | ------ |
| Single‑energy per node; links hold no activation | **OK** |
| Entities = neighborhoods; WM entity‑first        | **OK** |
| Stimuli inject activation only                   | **OK** |
| Two‑scale traversal                              | **OK** |
| Observability & deltas                           | **OK** |

---

## 3) `foundations/decay.md` — **Energy & Weight Decay (Forgetting with Control)**

> Refactors the draft from per‑subentity energy maps to **single‑energy** `Eᵢ`, separates **energy** decay vs **weight** decay, and positions decay as a **lever** in criticality control. Source: uploaded “Energy Decay.” 

```markdown
---
title: Energy & Weight Decay (Forgetting with Control)
status: stable
owner: @felix
last_updated: 2025-10-22
supersedes:
  - ../consciousness_engine/mechanisms/08_energy_decay.md
depends_on:
  - foundations/activation_energy.md
  - foundations/criticality.md
  - learning_and_trace/trace_weight_learning.md