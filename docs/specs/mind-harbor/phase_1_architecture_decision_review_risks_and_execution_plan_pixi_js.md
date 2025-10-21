# Phase 1 Architecture Decision — Review, Risks, and Execution Plan

**Decision Under Review:** Adopt **PixiJS** for the graph → Venice transition renderer (Phase 1).

---

## 1) Position
**Approve with guardrails.** PixiJS is the right first move for a 2D‑dominant scene graph with thousands of sprites, provided we lock in a few patterns up front so we don’t corner ourselves when crowds/LOD/post‑fx arrive.

**Why yes:**
- Excellent batching for sprites/meshes; easy to reach 50k+ quads with instancing.
- Text solved (BitmapFont/SDF via `@pixi/text-bitmap`).
- Simple filter chain; dev velocity high; bundle small.

**Guardrails:**
- Use **custom Mesh + Geometry** (instanced attributes) over `ParticleContainer` for portability and per‑instance styling.
- Build a **post‑processing stage** now (RenderTexture → half‑res bloom → LUT). Don’t defer.
- Keep an **escape hatch**: package scene graph so we can later port to Three/WebGPU if we outgrow Pixi.

---

## 2) Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Heavy post‑fx (bloom/LUT) hurts fps | Medium | Half‑res ping‑pong buffers; only emissive layer is bloomed; cache LUT in a single filter pass. |
| Need 3D (camera tilt/aerial) later | Low‑Med | Limit to 2.5D parallax; if true 3D needed, wrap Pixi layer inside a Three compositor (keep data+systems engine‑agnostic). |
| `ParticleContainer` limitations (no per‑sprite tint/alpha/uv) | Medium | Avoid it; use `Mesh` with instanced attributes (`aInstance`, `uAtlas`), or Pixi v8 `BatchGeometry`. |
| Text perf | Medium | Prebake labels to BitmapFont or SDF; bin labels screen‑space. |
| CPU hit‑testing on thousands | Medium | Use color‑picking FBO or spatial hash grid; avoid DOM pointer events per node. |
| Future WebGPU | Opportunity | Abstract renderer via `RendererAdapter` interface so scenes can swap backend. |

---

## 3) Architecture (Pixi v7/8)

**Layers (top → bottom):**
1. **UI/HUD** (HTML/CSS or Pixi): search, panels.
2. **Effects**: full‑screen filters (FXAA → UnrealBloom → LUT → Vignette).
3. **Emissive Layer**: porters’ orbs + filaments only (to drive bloom). Render to RT.
4. **Stroke Layer**: node glyphs/bridges/porters (non‑emissive metals).
5. **Background**: water, islands, parchment cards.

**Core classes:**
- `SceneController` — loads tiles, manages camera & culling.
- `InstancedSpriteLayer` — nodes, porters (per‑instance attributes: position, scale, palette hue, state, stride phase).
- `BridgeLayer` — batched quads with SDF caps; state tint for strength.
- `TextManager` — BitmapFont cache + screen‑binning.
- `PostChain` — render textures for emissive bloom + color grading.

**Data flow:**
`graphState → ViewModel (tile slice) → instance buffers (Float32Array/Uint8Array) → Pixi Mesh`.

---

## 4) Execution Plan (5–7 days)

### Day 1 — Boot & Parity POC
- Install Pixi, set up renderer, camera pan/zoom, high‑DPI.
- Render **2,500 node sprites** (atlas) + **1,000 links** (batched) at 60 fps. 
- Hit‑testing via color‑picking buffer.

**Acceptance:** < 10 draw calls; 60 fps on mid‑laptop.

### Day 2 — Instancing & Text
- Replace sprites with **Instanced Mesh** (position, size, tint, state). 
- Add **BitmapFont** labels with screen‑binning (≤ one label per 128×128 cell).

**Acceptance:** 5,000 nodes + 2,000 labels at 60 fps.

### Day 3 — Emissive/Bloom & LUT
- Split **emissive layer**; implement half‑res **UnrealBloom** filter (only emissive RT). 
- Add LUT grading + vignette.

**Acceptance:** Bloom FPS drop < 10%; visual parity with comps.

### Day 4 — Venice Tile Loader
- Replace force layout with **tile JSON** (islands, bridges, water). 
- Spatial culling; frustum only; smooth panning; bridge hit targets.

**Acceptance:** Single sestiere renders with panning @ 60 fps.

### Day 5 — Porters (Proto)
- Add **porter instanced layer**: default **walk**; each instance carries an **orb** (emissive sprite) and has **stride phase**. 
- Bind count to `activation`; BPM to `energy`. 

**Acceptance:** 300 walking porters on one tile (Rialto) @ 60 fps.

*(Day 6–7 buffer for polish or to push to two tiles.)*

---

## 5) Code Sketches

**Instanced nodes:**
```ts
const mesh = new PIXI.Mesh(new PIXI.Geometry()
  .addAttribute('aVertexPosition', quadVerts, 2)
  .addAttribute('aInstancePos', instancePos, 2, true)
  .addAttribute('aInstanceScale', instanceScale, 1, true)
  .addAttribute('aInstanceHue', instanceHue, 1, true)
  .addIndex(indices), shader);
```

**Half‑res emissive bloom:**
```ts
// render emissive to RT_E at 0.5 scale
renderer.render(emissiveLayer, { renderTexture: rtE });
applyBloom(rtE, rtE_blurred);
// composite: strokes + (rtE_blurred add)
```

**BitmapFont labels:** pre‑rasterize glyphs; bin by screen cell; only update when camera crosses bin boundaries.

---

## 6) Acceptance Criteria (Phase 1 done)
- WebGL/Pixi renderer parity, **< 10 draw calls** base scene.
- 5k nodes + 2k labels @ **60 fps**.
- Emissive‑only bloom + LUT; **< 10%** perf hit.
- Venice tile loader with culling.
- 300 walking porters on one bridge; orbs bloom correctly.

---

## 7) Exit Strategy
- Keep rendering behind `RendererAdapter` so we can move to **Three/WebGPU** if we need 3D or compute‑based culling later.
- Asset & data layers remain engine‑agnostic.

---

**Verdict:** Proceed with PixiJS now; build with instancing, emissive split, and a renderer abstraction so we’re future‑proof. Ship in ~5–7 dev‑days with clear perf gates.