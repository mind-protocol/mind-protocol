---
title: Identity Conflict Resolution
status: draft
owner: @owner
last_updated: 2025-10-22
supersedes: []
depends_on:
  - entity_layer/entity_layer.md
  - runtime_engine/traversal_v2.md
---

# Identity Conflict Resolution

## 1) Context — The problem we’re solving
An **active entity** should present a **single coherent identity** (role/lens). When multiple **identity‑labeled nodes** simultaneously dominate within the same active entity, phenomenology becomes “who am I?” muddled; traversal quality degrades, and global dynamics can oscillate. We need a **safe, spec‑compliant** way to **detect** and **resolve** such conflicts—*without* per‑entity energy on nodes—using only scoring and threshold modulation that our architecture already permits. :contentReference[oaicite:14]{index=14}

## 2) Mechanism — What it is
Detect concurrent activation of multiple identity nodes inside one active entity; decide between:
- **Dissociation**: split into separate entities when identities are **separable**.
- **Coherence enforcement**: keep one entity but **discourage** simultaneous identities via **WM scoring penalty** + temporary **threshold multipliers** on weaker identity nodes (no zeroing energies). :contentReference[oaicite:15]{index=15}

### 2.1 Detection (Two Approaches)

**Approach A: Structural Detection (Original)**

Among active members \(E_i\ge \Theta_i\), collect identity‑tagged nodes. If ≥2, compute:
- **Dominance ratio** \(D=\frac{E_{(1)}}{E_{(2)}}\) (top vs second).
- **Separation** \(S\): embedding distance + neighborhood overlap (Jaccard) + divergence of boundary flows (EMA).
- **Stability**: windowed persistence to avoid reacting to flukes.

**Approach B: Outcome-Based Detection (RECOMMENDED)**

Instead of detecting conflict structurally, assess **whether multiplicity is productive or pathological** via outcome metrics:

**Multiplicity Assessment Metrics (rolling window, e.g., last 20 frames):**

```python
task_progress_rate = Δ(goals_achieved) / frames
energy_efficiency = work_output / total_energy_spent
identity_flip_count = number of dominant identity changes
coherence_score = 1 - (identity_flip_count / frames)
```

**Multiplicity Modes:**

1. **Productive Multiplicity** — Multiple identities active, but outcomes are good:
   - `task_progress_rate` above baseline
   - `energy_efficiency` stable or improving
   - `identity_flip_count` moderate (healthy switching, not thrash)

2. **Conflict Multiplicity** — Multiple identities active, outcomes degrading:
   - `task_progress_rate` below baseline
   - `energy_efficiency` declining
   - `identity_flip_count` high (thrashing)

3. **Monitoring** — Single dominant identity, no action needed.

**Detection rule:**

```python
if num_active_identities >= 2:
    if task_progress_rate < PROGRESS_THRESHOLD and
       energy_efficiency < EFFICIENCY_THRESHOLD and
       identity_flip_count > FLIP_THRESHOLD:
        mode = "conflict"  # Pathological multiplicity
    else:
        mode = "productive"  # Healthy multiplicity, no intervention
else:
    mode = "monitoring"  # Single identity, stable
```

**Why outcome-based is better:** Avoids false positives on healthy multi-perspective thinking. Only intervenes when multiplicity is **actually harming** task performance, not when it's structurally present.

---

### 2.2 Resolution policy
- **Dissociate** if **mode = "conflict"** AND identities are **separable** (high \(S\)) and budget allows. Seed new entities around the competing identities; reassign nearby members by affinity; emit `entity.dissociate`.
- **Coherence enforcement** if **mode = "conflict"** but dissociation not appropriate:
  - Add **identity‑conflict penalty** to WM score proportional to number of competing identities and inefficiency.
  - Apply a small **temporary multiplier** \(\gamma>1\) to thresholds \(\Theta\) of the weaker identity nodes (falls away over T ticks) to let dominance settle **without deleting energy**.
  - Emit `entity.identity_cohere`.
- **No intervention** if **mode = "productive"** — productive multiplicity is valid; don't interfere.
- **No intervention** if **mode = "monitoring"** — single identity, stable.

> No per‑entity energy maps are used; we respect single‑energy and do not edit weights. :contentReference[oaicite:16]{index=16}

## 3) Why this makes sense

### 3.1 Sub‑entity phenomenology
Conflicted modes feel like talking over one another; **dissociation** restores clarity when roles are truly distinct; **coherence** penalty nudges the entity to **pick a lens** when a split would be artificial. :contentReference[oaicite:17]{index=17}

### 3.2 Human bio‑inspiration
Identity coherence echoes **task‑set maintenance**; **dissociation** parallels mode switching across cortical ensembles when goals differ; **gentle inhibition** (threshold multiplier) reflects top‑down control rather than suppressive erasure.

### 3.3 Systems‑dynamics rationale
Hard deactivation or energy zeroing can cause rebounds and instability. A **scoring penalty** + **temporary threshold bias** provides **smooth control** that decays, preventing oscillations and preserving state learning signals.

## 4) Expected resulting behaviors
- **Clear modes**: entities present a single dominant identity during active windows.  
- **Correct splits**: separable identities become distinct entities with proper RELATES_TO links.  
- **Fewer stalls**: less indecision at boundaries when identities clash.

## 5) Why this algorithm vs alternatives
| Alternative | Why we don’t use it |
|---|---|
| Zero out non‑dominant identity energies | Violates single‑energy design; creates abrupt rebounds. |
| Merge identities into one composite permanently | Hides real multimodality; harms interpretability. |
| Always split on any conflict | Over‑fragmentation; thrash when evidence is weak. |
| Weight surgery to “prefer” an identity | Entangles transient mode with long‑term knowledge. |

This design uses **soft control** (scores/thresholds), reversible and stable under load. :contentReference[oaicite:18]{index=18}

## 6) Observability — How & what to measure, and interpretation

### 6.1 Events/metrics

**Structural Detection (Approach A):**
- **Detection**: `entity.identity_conflict.detected` with `{entity_id, identities, D, S, persistence}`.
- **Resolution**: `entity.dissociate` or `entity.identity_cohere` with rationale and parameters.

**Outcome-Based Detection (Approach B - RECOMMENDED):**

```json
{
  "event": "entity.multiplicity_assessment",
  "entity_id": "...",
  "num_active_identities": 2,
  "identities": ["architect", "translator"],
  "task_progress_rate": 0.45,
  "energy_efficiency": 0.72,
  "identity_flip_count": 3,
  "coherence_score": 0.85,
  "mode": "productive",  // "productive" | "conflict" | "monitoring"
  "intervention": "none"  // "none" | "dissociate" | "coherence_enforcement"
}
```

```json
{
  "event": "entity.productive_multiplicity",
  "entity_id": "...",
  "identities": ["architect", "translator"],
  "task_progress_rate": 0.65,
  "energy_efficiency": 0.80,
  "message": "Multiple identities active but outcomes positive - no intervention"
}
```

**Common events (both approaches):**
- **Rates**: conflict frequency, mean time‑to‑resolution, post‑resolution stability (re‑conflict rate).
- **Quality**: task success / throughput before vs after resolution; user‑visible clarity metrics if applicable.

### 6.2 Dashboards
- **Conflict matrix**: top identity pairs by frequency \(S\) and outcomes.  
- **Resolution outcomes**: share of dissociation vs coherence; re‑merge rates.  
- **Penalty view**: WM scoring penalty magnitudes over time.

## 7) Failure Modes & Guards — Risks and why they’re bad
| Risk | Why bad | Guard |
|---|---|---|
| Split thrash | Rapid split/merge wastes budget, confuses WM | **Cooldown** on re‑association; hysteresis on \(S,\ D\) |
| False positives | Penalize healthy multimodality | Require persistence window; minimum activation; human‑in‑the‑loop override for critical identities |
| Over‑penalizing minority | Lose creative perspectives | Cap penalty; decay it; allow goal‑based overrides |
| Under‑splitting | Mixed modes remain incoherent | Lower \( \tau_{sep} \) when repeated conflicts; log for review |

## 8) Integration in code
- **Where**:  
  - Detection in `orchestration/mechanisms/entity_layer.py` during entity update.  
  - Resolution policy in `orchestration/mechanisms/consciousness_engine_v2.py` (per‑tick controller) with helpers in `entity_layer.py`.  
  - WM scoring penalty injected in `sub_entity_traversal.py` WM selection/packing.  
- **How**: read identity‑tagged nodes among active members; compute \(D,S\); apply policy; emit events.  
- **Config**: `IDENTITY_SEP_THRESH`, `IDENTITY_DOM_THRESH`, penalty coefficients, cooldown durations.

## 9) What success looks like
- **Behavioral**: fewer ambiguous decisions; faster boundary selection; improved task completion rates.  
- **Dynamics**: reduced conflict duration; low re‑conflict within cooldown; no spikes in \(\rho\) during resolution.  
- **UX**: clear “Architect” vs “Translator” modes, easy to explain in logs/Viz.

## 10) Open questions / future improvements / mistakes
- **Open**: better \(S\) estimators (boundary flow topology, causal influence); multi‑way (N>2) policies.  
- **Future**: learned penalty schedules; identity‑aware WM anchoring heuristics.  
- **Avoid**: per‑entity energy maps, hard zeroing, or weight edits to “pick winners”.

**References**: Original identity/sub‑entity conflict notes and resolution strategies. :contentReference[oaicite:19]{index=19}
