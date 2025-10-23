# Graph → Living Venice — Step‑by‑Step Scaling & Look/Feel Plan

**Goal:** Transform the current laggy node‑link view into a performant, legible, and beautiful **Venice‑topology** experience with Stroke‑Soul porters. Each step is shippable and improves both **speed** and **aesthetics**.

---

## Phase 0 — Profiling & Budget (1 day)
- **Measure:** FPS, CPU/GPU time per layer, node/link counts, draw calls.
- **Set budgets:** target 60 fps on mid laptop → **≤ 4 ms CPU**, **≤ 12 ms GPU** per frame.
- **Quick wins:** turn off expensive shadows/filters; flatten DOM if using SVG; prefer Canvas/WebGL.

**Tools:** Chrome Perf (Performance + Web Vitals), Spector.js (WebGL), stats.js.

---

## Phase 1 — Rendering Back‑End Swap (2–3 days)
- Move from DOM/SVG to **WebGL** (Pixi/Three/Babylon). Reason: thousands of nodes + lines choke layout/painting.
- **Instancing:** draw all nodes with **one instanced mesh**; links as batched lines (mesh or SDF quads).
- **Hit‑testing:** do in screen‑space grid or color‑picking buffer (no DOM listeners per node).

**Milestone:** Same scene, 5–10× faster, identical visuals.

---

## Phase 2 — Topology Shift (3–5 days)
- Replace abstract force layout with **Venice topology**: islands = nodes, bridges = edges, water = constraint.
- Load **tile** for the current viewport only (sestiere chunks).
- Links become **bridges** (thickened arcs with crowns); water rendered as inert blue (no shaders needed yet).

**Milestone:** The map reads like Venice; scrolling loads tiles; lag reduced via spatial culling.

---

## Phase 3 — Visual Language Upgrade (2–4 days)
- Node glyph → **porter orb + small stroke silhouette** preview; color by subentity.
- Link glyph → **bridge highlights**; active traversal = bright trail.
- Tooltip → **Parchment card** (Cinzel/Crimson Text) with meaningful metrics only.
- Add **Style Lock:** night or sunrise palette; Mind Protocol typography.

**Milestone:** First pass of the hybrid aesthetic (futuristic explorer × realistic world).

---

## Phase 4 — LOD & Culling (5–7 days)
- **Spatial index** (R‑tree or grid) for nodes/bridges; render only within frustum.
- **LOD tiers** for everything:
  - Nodes: text/emoji → dot → hidden.
  - Bridges: full geometry → thin line → hidden.
  - Porters (when added): A/B/C/D tiers (see Scaling Plan).
- **Label decluttering:** screen‑space binning; one label per bin.

**Milestone:** 10–50k primitives at 60 fps.

---

## Phase 5 — Data‑Bound Motion (3–5 days)
- Add **walking porters** on bridges/islands using instancing and path arrays.
- Bind motion to metrics: `activation → count`, `energy → orb BPM`, `link.strength → bridge glow`.
- **No meaningless animation**: each movement must reflect state.

**Milestone:** The map feels alive; still performant.

---

## Phase 6 — Compositing & Bloom (2–3 days)
- Post chain: FXAA → **Unreal Bloom** (emissive only) → LUT (sunrise/night) → vignette.
- Ensure bloom is applied to **orb/filaments** passes, not the whole scene (half‑res buffer).

**Milestone:** Premium look without a perf hit.

---

## Phase 7 — Interaction & Story (3–5 days)
- **Hover focus** reduces global clutter: dim non‑neighbors; highlight route.
- **Time scrubber** for historical playback; stroke‑trail echoes.
- **Camera presets:** Campo, Bridge, Bacino; smooth jumps.

**Milestone:** It tells stories; users can follow traversal.

---

## Phase 8 — City‑Scale Crowds (2–3 weeks)
- Integrate **tile streaming** and multi‑tier LOD porters from the Scaling Plan.
- Perf HUD; QA overlays for constraint violations; telemetry dashboard.

**Milestone:** “Full Venice full of people” at stable FPS.

---

## Visual Coherence Checklist (every phase)
- Water is a **hard boundary**; no illegal crossings.
- Porters **walk by default**; every porter **carries an orb**.
- Aesthetics as architecture: digital explorer + realistic content.
- No motion without meaning; everything bound to data.

---

## Perf Cookbook (copy/paste)
- Batch draws; **avoid per‑node DOM**.  
- Use **instanced buffers** for attributes (color, size, state).  
- Offload layout to workers.  
- Cull off‑screen.  
- Half‑res post; downsampled bloom.  
- Avoid expensive text; use SDF fonts; cache glyph quads.

---

## Acceptance Criteria per Phase
- **0:** Baseline perf report captured.
- **1:** WebGL renderer parity; draw calls < 10.
- **2:** Venice tiles load; panning cost ≤ 3 ms/frame.
- **3:** New glyphs + parchment cards live.
- **4:** 60 fps with 5× current node/link counts.
- **5:** Porter count scales with activation; no idle animation.
- **6:** Bloom applied only to emissive; FPS drop < 10%.
- **7:** Hover focus & scrubber live.
- **8:** City‑wide LOD crowds; perf HUD green.

---

**Mantra:** Profile first, then replace the slowest layer; one shippable step at a time until Venice is alive.

