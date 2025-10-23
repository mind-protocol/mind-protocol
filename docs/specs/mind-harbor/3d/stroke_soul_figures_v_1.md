# Stroke‑Soul Figures — v1.2 Additions (Schema, Presets, Compositing, Materials, Checklists)

**Scope:** Implements the selected upgrades: **Parameter JSON Schema**, **Canonical Presets Library** (Venice porters walk by default), **Compositing Pipeline**, **Expanded Material Library**, and **Production Checklists**. This extends the v1 Bible without changing its core grammar.

---

## 1) Parameter JSON Schema (Authoritative)
Use this as the single source of truth for generation. Values shown are examples.

```json
{
  "version": "1.2",
  "scene": {
    "background": "void|starfield|plaster|venice",
    "location": "Piazza San Marco|Rialto|Campo Santa Margherita|Bacino di San Marco|Custom",
    "time_of_day": "night|sunrise|golden_hour|blue_hour",
    "camera": { "lens_mm": 35, "elevation_deg": 5, "tilt_deg": -3, "azimuth_deg": 35 },
    "aspect_ratio": "16:9|3:2|4:3|21:9"
  },
  "character": {
    "palette_family": "amber|rose|teal|violet|custom",
    "stroke_color": "#E4A631",
    "line_color": "#FFD27A",
    "orb_color": "#FFE6B0",
    "hue_jitter_deg": 8,
    "value": 0.95
  },
  "pose": {
    "vector_deg": 35,
    "arm_reach": 0.8,
    "knee_raise": 0.6,
    "diagonal_bias": 0.7,
    "gesture": "reach|leap|spiral|fold|bow"
  },
  "strokes": {
    "width_pct": 1.2,
    "thickness_pct": 0.18,
    "edge_fray_px": 2,
    "alpha_jitter": 0.15,
    "anisotropy": 0.6,
    "metallic": 0.88,
    "roughness": 0.2
  },
  "hands": { "fingers_per_hand": 5, "draw_thumbs": true },
  "nervous_lines": {
    "count": 5,
    "origin": "head",
    "endpoints": ["L_hand", "R_foot", "crotch", "R_hand", "L_foot"],
    "stay_inside_body": true,
    "intensity_head": 1.0,
    "intensity_distal": 0.5
  },
  "orb": { "radius_pct": 4.5, "bpm": 9, "diffuse_only": true },
  "constraints": {
    "no_touch_clearance_pct": 0.3,
    "joint_gaps_pct": 4,
    "water_is_hard_boundary": true
  },
  "crowd": {
    "count": 1,
    "role": "porter",
    "default_motion": "walk",
    "speed": 1.0,
    "spacing_min_pct": 2.0
  },
  "post": {
    "bloom_radius_pct": 7,
    "bloom_threshold": 0.85,
    "chromatic_dispersion_px": 1.5,
    "vignette_strength": 0.15,
    "lut": "MP_Sunrise_LogToDisplay_v2.cube"
  },
  "export": { "bit_depth": 16, "color_space": "DisplayP3", "png_premultiplied": true }
}
```

**Validation rules:**
- Head strokes = 6 (3 face + 1 back + 2 jaw).  
- Fingers = 5 per hand.  
- Nervous lines = 5, start in head, endpoints include ≥1 hand, ≥1 foot, and crotch.  
- No-touch clearance and joint gaps enforced.  
- Chest orb present and un‑cropped.

---

## 2) Canonical Presets Library (Venice Porters Walk by Default)
All Venice presets assume **role: porter**, **default_motion: walk**, each porter **carries a glowing orb**. Use palette variants per subentity.

### 2.1 Solo Figure (Non‑Venice)
- **Void Minimal:** lens 50 mm, aspect 3:2, background void, palette any, gesture reach.  
- **Starfield Drift:** lens 35 mm, aspect 16:9, low‑contrast stars, bloom +10%.  
- **Plaster Panel:** lens 50 mm, matte ivory panel, raking light, no emissive bleed outside figure.

### 2.2 Venice Sunrise Pack (Walking Porters)
- **San Marco Hub — Sunrise:** lens 50 mm, elevation 3°, azimuth 20°. Crowd 18–30 porters walking in loose lanes across the piazza. Waterfront visible; **water is not traversed**. Chest‑orb BPM maps to energy.
- **Rialto Major Link — Blue Hour→Sunrise:** lens 35 mm, slight telephoto compression; **on‑bridge cap 24** walking porters mid‑step; ascent/descent visible; no stopping.
- **Campo Santa Margherita — Waking Residential:** lens 28 mm, elongated composition; tri‑subentity co‑presence (amber/blue/green) all **walking**; café chairs unoccupied; wellhead central.
- **Bacino di San Marco — Global Workspace:** lens 24 mm aerial; walking streams along fondamenta; density ramps toward basin edge; additive color where groups mingle.

**Defaults applied:** `crowd.role = porter`, `crowd.default_motion = walk`, `crowd.speed = 1.0`, orbs carried in varied styles (cradle/hip/front/overhead/shoulder), **no stacking**.

---

## 3) Compositing Pipeline (Authoritative)

### 3.1 Layer Order (top → bottom)
1. **Grade FX:** LUT, film grain, vignette.  
2. **Bloom/Glow:** from emissive AOV only (filaments + chest orb).  
3. **Specular Highlights:** metallic ribbons’ spec pass.  
4. **Body Strokes:** alpha, premultiplied.  
5. **Filaments:** additive; mask to remain inside body envelope except for subtle edge light.  
6. **Shadows/Contact:** soft AO where strokes approach ground/architecture (Venice scenes).  
7. **Background Plate:** void/starfield/plaster/photoreal Venice.

### 3.2 Blending & Color Management
- **Premultiplied alpha** for strokes; **additive** for emissive passes.  
- Color space: work in **ACEScg or Linear sRGB**; display to **P3/Rec.709** with provided LUT.  
- Clamp bloom pre‑display; avoid clipping body metals.

### 3.3 AOVs / Passes
- Beauty, Strokes (RGBA), Filaments (emissive), Orb (emissive), Specular, AO/Contact, Z‑depth (for selective bloom falloff).

### 3.4 Post Recipes
- **Bloom:** radius 5–10% frame; threshold 0.85–0.9.  
- **Dispersion:** 1–2 px at hottest whites only.  
- **Vignette:** 0.1–0.2, disabled for plaster panel.

---

## 4) Expanded Material Library

### 4.1 Metallic Brush Strokes (PBR tables)
| Material | Metallic | Roughness | Anisotropy | Specular | Notes |
|---|---:|---:|---:|---:|---|
| Polished Gold | 0.95 | 0.14 | 0.55 | 0.78 | Warm tint; strong edge glints |
| Rose Gold | 0.92 | 0.18 | 0.60 | 0.76 | Pink undertone; great with violet lines |
| Brushed Copper | 0.9 | 0.22 | 0.65 | 0.74 | Orange warmth; visible grain |
| Oxidized Copper | 0.88 | 0.28 | 0.50 | 0.72 | Teal speckle mask; richer cool accents |
| Brushed Steel | 0.85 | 0.20 | 0.70 | 0.75 | Neutral; pairs with any palette |
| Hematite | 0.9 | 0.16 | 0.45 | 0.8 | Dark mirror; dramatic highlights |

**Texture stack (per stroke):** base color → foil noise → brush tooth normals → edge fray mask → paint flecks (magenta‑blue) → micro‑scratches. **Alpha jitter** 0–20% along length to preserve unfinished gaps.

### 4.2 Emissive Filaments
- **Core types:** single‑core (sharp), double‑core (softer center), spectral tip (slight hue shift at ends).  
- Width 0.12–0.28% H; intensity head:1.0 → distal:0.5.

### 4.3 Chest Orb
- Pure diffuse + emissive; soft volumetric halo; tint from palette; optional specular kiss on nearby metals.

---

## 5) Production Checklists

### 5.1 Pre‑Render
- [ ] **Grammar:** head=6 strokes, fingers=5/hand, joint gaps, no touches.  
- [ ] **Nervous system:** 5 lines start inside head; endpoints include ≥1 hand, ≥1 foot, and crotch; lines stay inside body.  
- [ ] **Orb:** diffuse chest glow present and un‑cropped.  
- [ ] **Palette:** strokes/lines/orb harmonized (hue offsets < 15°).  
- [ ] **Venice constraints (if any):** water impassable; bridges/sottoportegos only.  
- [ ] **Crowd (porters):** role=porter; default motion=walk; every porter visibly carries an orb; no stacking.

### 5.2 Render Settings
- [ ] Linear workflow; ACEScg or Linear sRGB; LUT set.  
- [ ] AOVs enabled (Strokes, Filaments, Orb, Specular, AO, Z).  
- [ ] Bloom threshold and radius per spec.

### 5.3 Post‑Render
- [ ] Bloom within bounds; dispersion ≤ 2 px; vignette subtle.  
- [ ] No illegal stroke intersections; filaments fully inside body.  
- [ ] Export 16‑bit, Display P3 + Rec.709; premultiplied PNG; CMYK proof if printing.

---

**Mantra (unchanged):** Keep the grammar sacred; scale the system. Motion is meaning. Constraints create coherence.

