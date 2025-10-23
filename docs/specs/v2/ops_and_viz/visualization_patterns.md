---
title: Visualization Patterns (Entity‑First, Frontier‑Aware)
status: stable
owner: @iris
last_updated: 2025-10-22
depends_on:
  - ops_and_viz/observability_events.md
  - emotion/emotion_coloring.md
  - runtime_engine/traversal_v2.md
summary: >
  Patterns for rendering the entity layer first, with frontier-aware node/edge detail on demand.
  Includes color/tint rules (valence/arousal), hysteresis, sampling, and attribution UX.
---

# 1) Goals & constraints
- **Tell the story at the right scale:** Entity bubbles first, atomic details on demand.
- **Stable mental map:** Positions should drift slowly; big jumps only at explicit user actions.
- **Bounded work:** Render ≤ 10 fps; degrade gracefully via sampling & level of detail (LOD).

# 2) Core compositions

## 2.1 Entity Mood Map (default)
- **Nodes:** entities as bubbles; size ∝ `energy` (derived), border weight ∝ `coherence`.
- **Color (HSL or OKLCH):**
  - axes: `"valence"`, `"arousal"` (from emotion events);
  - hue ← valence (negative→magenta/red 320°, positive→green 120°);
  - **lightness ← valence × arousal** (product mapping):
    - **Excited** (high valence × high arousal → positive product) → **brighter** (L ≈ 70-85)
    - **Anxious** (low valence × high arousal → negative product) → **darker** (L ≈ 25-40)
    - **Content** (high valence × low arousal → small positive) → **medium-light** (L ≈ 55-65)
    - **Depressed** (low valence × low arousal → small negative) → **medium-dark** (L ≈ 45-55)
    - Formula: `L = 50 + 35 * tanh(valence * arousal)` (maps [-1,1]×[0,1] → [25,85] lightness)
  - saturation ← |valence|.
- **Urgency encoding (independent of color):**
  - **Data source:** `se.state.v1.urgency` field (0-1) from entity state events
  - **Border pulse:** When `urgency > 0.7`, animate border with 1.5s pulse cycle (opacity 0.4 → 1.0)
  - **Glow:** When `urgency > 0.5`, add subtle radial glow (size ∝ urgency, white/yellow tint)
  - **No color override:** Urgency affects border/glow only, not the valence×arousal color mapping
  - **Active goal chip:** Display `active_goal` label when present, with intensity ∝ `goal_strength`
- **Hysteresis:** update bubble color only if Δhue>12° **or** Δmag>0.08.
- **Labels:** name + KPI chips (energy, coherence, urgency if >0.5).
- **Interaction:** click to **expand** into member view.

## 2.2 Expanded Member View (within an entity)
- **Nodes:** Active members (from `tick_frame.nodes` intersected with membership); grey non‑active members optional.  
- **Edges:** Show **active** links only (`flow>0` this frame or positive `z_flow`).  
- **Texture:** tiny “spark” along edges for sampled `stride.exec`.  
- **WM glow:** WM‑selected members get a faint rim.

## 2.3 Boundary Bridges (entity↔entity)
- **Sankey / ribbon** between bubbles; width ∝ `se.boundary.summary.dE_sum`, color mixes source & target tints.  
- **Tooltips:** precedence, dominance, φ_max.

# 3) Diagnostics overlays

- **Regulation vs Coherence Index:** small dial or stacked bars computed from `comp_mult<1` vs `res_mult<1`.  
- **Staining Watch:** histogram of `node.emotion.update.mag`, per type; alert when tail > threshold.  
- **Conservation strip:** tiny display of `deltaE_total` and `rho` over last N frames.

# 4) Layout & stability

- **Entity layout:** incremental force with **pinning**; only allow small offsets per frame (≤1–2 px).  
- **Member layout:** seeded around entity centroid; sort by degree and place radial rings; reuse last positions for stability.  
- **LOD:** if members > 400, collapse to “top‑K” by `energy` and show summary counts.

# 5) Performance & sampling budgets

- **Frame budget:** target ≤ 16 ms render time; if exceeded, drop least important deltas: (1) node emotion deltas, (2) link deltas, (3) hide minor labels.  
- **Stride sampling:** respect `notes` in `tick_frame` (e.g., “stride sampling: 0.1”).  
- **Quantization:** pre‑quantized numeric fields; avoid re‑quantizing on client.

# 6) Attribution Cards (why this edge?)
- **Inputs:** last `stride.exec` for the edge; show `phi`, `ease=exp(log_weight)`, `resonance/res_mult`, `comp_score/comp_mult`.  
- **Explain:** “Chosen because φ high and resonance favored; comp was weak; effective cost X.”  
- **Links to:** weight evolution sparkline; entity mood chips.

# 7) Error/empty states
- **No emotion data:** fallback neutral palette; hide affect chips.  
- **Backpressure note:** surface `tick_frame.notes` prominently (“reduced stride sampling”).  
- **Reconnect:** use `snapshot.v1` to bootstrap, then consume deltas.

# 8) Accessibility
- Provide **colorblind-safe** alternative palette (vary lightness more than hue).  
- Tooltips readable at 200% zoom; keyboard focus order moves entities first, then members, then edges.