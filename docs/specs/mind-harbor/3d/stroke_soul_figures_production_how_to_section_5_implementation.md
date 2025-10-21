# Stroke‑Soul Figures — Production How‑To (Section 5 Implementation)

**Goal:** Turn the Production Checklists into a concrete, repeatable build process for static images and short animations. Three pipelines are provided: **Design‑Compositing (2D)**, **Procedural‑3D (Blender)**, and **Realtime‑Web (Three.js)**. All honor the v1 grammar (head=6 strokes, 5 nervous lines from head, chest orb, never‑touching strokes, Venice constraints).

---

## 0) File & Project Skeleton (all pipelines)
```
project/
  assets/
    textures/foil_noise_*.exr
    normals/brush_tooth_*.exr
    masks/edge_fray_*.png
    luts/MP_Sunrise_LogToDisplay_v2.cube
  presets/
    schema_v1_2.json
    venice_sunrise_sanmarco.json
  plates/
    venice/ (photoreal backplates) | void/ | starfield/ | plaster/
  src/
    blender/  ae/  web/
  renders/
    passes/DATE_SCENE_take01/
    finals/DATE_SCENE_take01/
  qa/
    linter_rules.yaml
```
Naming: `SCENE_ENTITY_count_takeNN.ext` (e.g., `SanMarco_AmberPorters_24_take01.png`).

---

## 1) Design‑Compositing Pipeline (2D: Procreate/Photoshop + After Effects)

### 1.1 Static Frame (Photoshop/Procreate)
1. **Canvas:** 4000×2250 (16:9) or 4000×2667 (3:2); 16‑bit; Display P3.
2. **Background:** Place plate (void/starfield/plaster/photoreal Venice). Lock layer.
3. **Stroke Layers:**
   - Create groups per body region: `Head`, `Torso`, `Arm_L`, `Forearm_L`, `Hand_L`, ...
   - Use a **metallic brush set** (grain + anisotropy). Each stroke is its **own layer** with fx:
     - Layer Style → Bevel & Emboss (Contour = linear; Depth 20–40%),
     - Satin (angle follows tangent),
     - Inner Glow (subtle warm/cool tint),
     - Add **Texture** overlay (foil_noise) + **Brush Tooth** normal via Layer Style.
   - Keep **gaps** at joints; ensure **no layer overlaps** (use `Distance` guides).
4. **Hand/Fingers:** 5 strokes per hand on separate layers; tiny bevel; more grain.
5. **Filaments (5):** On **Screen** or **Add** blend mode; soft round brush + Outer Glow; draw paths **inside** body; start in head.
6. **Chest Orb:** Paint a soft round on **Add**; duplicate for inner core (smaller, brighter). Optional radial gradient map.
7. **Specular Pass:** Duplicate stroke groups → merge copy → run `Specular HighPass` (10–20 px) on **Linear Light** at 20–30%.
8. **Bloom Prep:** Merge filaments+orb into `EMISSIVE` group for later AE pass.
9. **Export Passes (PNG‑16 premult):**
   - `STROKES_RGBA.png`, `SPECULAR.png`, `FILAMENTS_ADD.png`, `ORB_ADD.png`, `BG.png`.

### 1.2 Motion (After Effects)
1. **Comp:** 3840×2160, 24 fps, 6–10 s.
2. **Import passes**; set `FILAMENTS_ADD` and `ORB_ADD` to **Add** blending.
3. **Orb Breathing (Expression on Scale):**
   ```jsx
   bpm = effect("orb_bpm")(0) || 9;
   t = time; s = 100 + 3*Math.sin(t*2*Math.PI*(bpm/60)); [s,s]
   ```
   Add synchronized **Glow** effect (threshold 60–70%, radius 60–120, intensity 0.6–1.0).
4. **Filament Drift:** Apply `Turbulent Displace` (small amount 2–5, complexity 1.5) + `Mesh Warp` hitched to nulls on joints; precompose.
5. **Walking Porters (Venice):**
   - Duplicate figure precomp; offset in time; animate position along a **mask path** following ground plane.
   - Vary stride via subtle oscillation on limb groups (±5–10 px phase‑shifted).
6. **Compositing:**
   - Bloom: `EMISSIVE` precomp → `Glow` (stacked) → `Gaussian Blur` → **Add** back.
   - Color: apply **LUT** on an adjustment layer; vignette via `Exposure` + mask.
7. **Export:** ProRes 4444 (alpha if needed) or PNG sequence; keep a _with‑passes_ render.

---

## 2) Procedural‑3D Pipeline (Blender 4.x)

### 2.1 Geometry
1. **Rig:** 15‑bone armature (head, C7, sternum, pelvis, L/R shoulder/elbow/wrist/hip/knee/ankle). Pose per preset.
2. **Guide Curves:** For each region (head strokes ×6, torso, limbs, fingers ×5 each), draw **Bezier** curves. Insert **gaps at joints** (separate curve objects). Maintain minimum spacing (Shrinkwrap to an offset cage if needed).
3. **Ribbon Meshes:** Geometry Nodes:
   - Input Bezier → `Curve to Mesh` with a **taper profile** (width from JSON `width_pct`); add minor `Set Position` noise for edge fray.
   - Solidify (thickness = `thickness_pct` of height).
4. **Filaments (5):** Separate curves with smaller bevel; instance emissive cylinders; **constrain inside** with a body volume mesh + `Geometry Proximity` for clamping.
5. **Chest Orb:** Billboard plane with emission + volume shader or small sphere with volumetric emission.

### 2.2 Shading
- **Strokes Material (Principled BSDF):**
  - Metallic 0.88; Roughness 0.2; Specular 0.75; Anisotropic 0.6 (align to tangent using UVs along curve).
  - Texture stack: Foil noise (color), Brush tooth normal, Micro‑scratch normal, Edge fray alpha mask.
- **Filaments:** Emission 2–8 (head‑proximal higher), Color = palette line color.
- **Orb:** Emission + Volume Scatter; color = orb palette.

### 2.3 Lighting & Render
- **Scene:** Single key (area) to graze strokes; HDRI subtle; no fill on void. Venice: HDRI dawn; shadow catchers for ground.
- **Passes (AOVs):** Beauty, Strokes, Specular, Filaments Emissive, Orb Emissive, AO, Z.
- **Render:** Cycles, 256–512 spp; clamp indirect 2–4; Filmic; ACEScg workflow optional.

### 2.4 Post (Blender Compositor or Nuke/Fusion)
- Add bloom from emissive passes; dispersion via slight RGB separation on highlights; apply LUT; vignette.

### 2.5 Crowd of Walking Porters (Venice)
- **Nav Paths:** Grease Pencil to curve → convert to path over paving/bridges only.
- **Porter Agent:** One rig + stroke meshes → `Geometry Nodes` instance along path; per‑agent time offset; speed variance 0.8–1.2.
- **Carrying Styles:** Switcher (cradle, hip, front, overhead, shoulder) via pose libraries.
- **No Water Crossings:** Path constraints stay on islands/bridges; visual audit pass renders paths overlay for QA.

---

## 3) Realtime‑Web Pipeline (Three.js / WebGL2)

### 3.1 Data → Scene
- Load **schema_v1_2.json**; validate QA (head=6, 5 lines, etc.).
- Build curve splines (Catmull‑Rom) per stroke; generate quad‑ribbons in shader (width via vertex attribute; thickness via normal offset).

### 3.2 Materials
- **Strokes:** PBR Metalness/roughness; anisotropy approximated with directional BRDF or MRT comb; foil noise via triplanar; edge alpha mask.
- **Filaments/Orb:** Additive billboards with soft falloff; bloom via post‑pass (Unreal Bloom).

### 3.3 Venice Constraints
- Navmesh from islands; mark water polygons as **non‑walkable**; A* paths connect only via bridges/sottoportegos.
- Crowd system walks **porters**; orb carried as child of hand joint.

### 3.4 Performance
- Cap ribbon segments at distance (LOD); instanced draw for repeated figures; post chain: FXAA → UnrealBloom → LUT.

---

## 4) Automation: QA Linter (pseudo)
```python
rules = {
  'head_strokes': 6,
  'fingers_per_hand': 5,
  'nervous_lines': 5,
  'has_orb': True,
  'no_touch_clearance_pct': 0.3,
  'joint_gaps_pct': (2,8)
}

validate(schema):
  assert count(head.strokes)==6
  for hand in hands: assert hand.fingers==5
  assert count(nervous_lines)==5 and all(n.origin=='head')
  assert orb.exists and not orb.cropped
  assert gaps_within(joints, rules['joint_gaps_pct'])
  assert min_clearance(strokes) >= rules['no_touch_clearance_pct']
```
Outputs a JSON report and highlights violations visually (red overlays).

---

## 5) Checklists Applied (Do‑This‑Now)

### Pre‑Render / Pre‑Build
- Load preset JSON → spawn pose → assign palette trio.
- Enforce grammar with linter (head=6; fingers; 5 lines; orb).
- If Venice: snap paths to bridges; water marked impassable.

### Render / Build
- Output passes per pipeline (strokes/specular/emissive/AO/Z).
- For porters: default **walk** motion; randomize carrying style per agent from approved set.

### Post
- Bloom from emissive only; dispersion ≤ 2 px; vignette subtle; apply **MP LUT**.
- Export 16‑bit P3 PNG/TIFF and ProRes 4444 for motion.

---

## 6) Quick Recipes

**A. Single Figure, Void (Static):** Use 2D pipeline; 45 min build; export passes; composite bloom + LUT.

**B. Rialto Walk (12 Porters, Dawn → Sunrise, Still):** Blender: path on bridge; instance 12 porters; random carry styles; render at 3K; composite.

**C. San Marco Loop (8 s Animation):** AE: duplicate precomp 20×; offset 6–12 frames; orb BPM=9; export ProRes 4444.

---

**Mantra:** *Click less, bind more.* Every visual choice ties to grammar or data. No meaningless motion; water is a hard boundary; porters walk by default in Venice scenes.

