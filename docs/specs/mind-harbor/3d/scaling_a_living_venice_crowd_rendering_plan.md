# Scaling a Living Venice — Crowd & Rendering Plan

**Goal:** Make “a full Venice full of people” feasible while preserving the Stroke‑Soul grammar (porters walk, carry orbs, five filaments from head, chest orb) and the Venice topology rules (water = hard boundary; bridges/sottoportegos = links).

---

## 1) Mental Model — Four Layers

1. **World Tiles** (Venice geometry & navmesh)
   - Split by *sestiere* (San Marco, Cannaregio, Castello, Dorsoduro, San Polo, Santa Croce) + Giudecca/Bacino.
   - Each tile ships with: island polygons, bridge links, sottoportegos, water polys, and a pre‑baked **navgraph**.
2. **Simulation** (server or worker)
   - Time‑stepped state: node activation, link strength, crowd goals.
   - Emits *intents* → paths (A* on tile graphs) → **porter trajectories**.
3. **Renderer** (client, WebGPU/WebGL)
   - Draws porters with **GPU instancing** + **LOD ribbon impostors**.
   - Handles bloom/compositing and visibility culling.
4. **Orchestration**
   - Stream tiles and agents based on camera; keep ≤ N visible agents in high fidelity.

---

## 2) Crowds at Scale — LOD Tiers (deterministic)

| Tier | Distance (screen) | Body | Filaments | Orb | Budget |
|---|---|---|---|---|---|
| **A – Hero** | ≥ 3% screen height | Full ribbon set (head=6, fingers=5/hand, joint gaps) | 5 splines (tube/quad) | Diffuse + emissive w/ soft volume | 100–300 agents visible |
| **B – Mid** | 1–3% | Merged ribbon groups per limb (1–2 strokes/limb), single hand stroke | 3 filaments (head→hands/crotch) | Emissive sprite | 1–3k agents |
| **C – Far** | 0.3–1% | Billboard impostor (pre‑baked normal/spec) | Single interior line | Emissive disk | 10–30k agents |
| **D – Crowd Fog** | < 0.3% | Density field (screen‑space splats) | None | Orb in density texture | 50k+ agents represented as field |

**Rule:** A‑tier must always pass the Stroke‑Soul QA. B/C preserve silhouette & orb; filaments collapse gracefully.

---

## 3) Rendering — WebGPU/WebGL Playbook

- **GPU Instancing**: one porter mesh per tier; per‑instance attributes: pose phase, carry style, palette hue, orb intensity, stride speed.
- **Ribbon Impostors** (B/C): screen‑aligned quad strips shaded with *stroke SDFs* (signed distance fields) that encode metallic anisotropy + brush grain.
- **Per‑Pixel LOD Bloom**: emissive mask at half‑res (Unreal Bloom); avoid full‑res blur for C/D tiers.
- **Culling**: hierarchical world tiles + frustum + occlusion (island occluders); only draw porters on visible islands/bridges.
- **OIT alternative**: blend ordering issues minimized by using premultiplied alpha and avoiding deep overlaps (strokes never touch reduces overdraw).
- **Batched Orbs**: single atlas of orb sprites with size/intensity in instance buffer.

---

## 4) Navigation & Behavior

- **Graph Per Tile**: nodes = island entry/exit points + bridge crowns + sottoportegos; edges store width/grade/capacity.
- **Pathing**: A* with edge costs from *link.strength, congestion, slope*; commit rule for sottoportegos (no mid‑edge abort).
- **Flow Control**: edge capacities → *metronome* releases to prevent clogs; animation stride synced to travel speed.
- **Carrying Styles**: instance state machine with weighted random cycling (cradle, hip, front, overhead, shoulder) at waypoints.

---

## 5) Tile Streaming & Memory

- Load tiles around camera (2‑tile radius). Each tile holds:  
  `navmesh.bin` (≤ 1 MB), `island_mesh.glb` (≤ 5 MB if photoreal, ≤ 500 KB stylized), `agents.dat` (current residents).
- **Agent Streaming**: keep global sim server‑side; stream **visible slice** (position, tier, pose phase, palette, orb)
- **Compression**: quantize positions (16‑bit), encode phase in 8‑bit, pack attrs into SSBOs.

---

## 6) Performance Targets (per modern laptop dGPU)

- **Visible A‑tier**: 200 @ 60 fps.  
- **Total B/C agents**: 5–15k @ 60 fps with instancing + half‑res post.  
- **D‑tier density**: 50k+ represented via field without per‑agent draw calls.  
*(Numbers are guidance; tune by device class.)*

---

## 7) Visual Coherence Rules (Style at Scale)

- **Orb is the identity anchor** across all tiers; color/pulse communicates entity and energy.
- **Additive color mixing** where groups co‑occupy nodes even in B/C tiers (screen‑space light accumulation).
- **No water crossings** ever; highlight violations in red audit overlay during dev.
- **Bridge bands**: show walking lanes as subtle specular streaks from orbs for readability at distance.

---

## 8) Data Binding

- `energy → orb_bpm (6..12), filament intensity`
- `valence → palette temperature offset`
- `link.strength → bridge glow opacity`
- `congestion → stride variance & lane choice`

---

## 9) Pipeline Choices

- **Realtime (web):** Three.js/Babylon (WebGL2) now; migrate to **WebGPU** for tier C/D efficiency (storage buffers, compute culling).
- **Native:** Unity/Unreal with Niagara/VFX Graph for density fields; HLOD for Venice meshes.
- **Pre‑render:** Blender for hero shots; bake impostors for B/C tiers.

---

## 10) Roadmap (6 sprints)

1. **Prototype tile + 300 porters** on one bridge (Rialto). LOD A/B only.  
2. **Add tile streaming** and frustum culling; A/B/C tiers; 5k agents.  
3. **Navgraph capacities & sottoportego commit**; congestion metronome.  
4. **Density field D‑tier**; Bacino plume; 30–50k represented.  
5. **Multi‑entity mixing** (color add), data bindings, QA audit overlays.  
6. **City‑wide session**: all sestieri loaded around camera, 60 fps budget tuning.

---

## 11) QA & Telemetry

- **Style Linter** runs on A‑tier agents (head=6, fingers=5/hand, 5 filaments from head, orb).  
- **Perf HUD**: draw calls, agent counts per tier, ms per pass, post cost.  
- **Constraint Monitor**: count/flag any illegal water crossing attempts.

---

## 12) What “Full Venice Full of People” Means (in practice)

- Near camera you *feel* individuals (A‑tier).
- Mid distance reads as flowing lanes of porters (B‑tier).
- Far distance reads as organismic light patterns (C/D tiers).  
- Topology remains legible: islands solid, bridges active, water dark.

**Mantra:** *Individuals up close, rivers of intent at scale.* Keep the orb readable; keep water sacred; keep motion meaningful.

