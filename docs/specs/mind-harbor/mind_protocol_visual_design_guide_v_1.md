# Mind Protocol — Visual Design Guide (v1.0)

A pragmatic, opinionated system for making Mind Protocol feel coherent across products, protocol surfaces, and brand media.

---

## 0) Brand Essence → Visual Consequences

- **Explorer vs World**: The _Explorer_ (consciousness) is luminous and abstract; the _World_ (evidence) is realistic and textured. Use emissive light and ribbons for Explorer layers; use photographic/scan‑like textures for evidence surfaces.
- **Membrane‑first**: Frames, rings, and gates recur. Visual membranes are soft‑edged rings and glassy panes separating spaces. Emissions cross membranes visibly.
- **Law at L4**: Law is legible, not mystical. Render registries and receipts as precise documents with typographic hierarchy and official seals.

---

## 1) Color System

### 1.1 Primaries (Dark‑first)
- **Void Black** `#040507` — background canvas (Explorer).  
- **Membrane Teal** `#37D6DF` — primary accent for membranes, rings.  
- **Core Gold** `#EAD15A` — energy core, highlights, orbs.  
- **Graph Cyan** `#5FE3F1` — graph links, hover accents.  
- **Field Slate** `#121418` — elevated surfaces (cards/panels).  
- **Warm Paper** `#F8F2E3` — evidence backgrounds (receipts, docs, scans).

**Usage ratio (dark theme):** 70% Void Black, 15% Field Slate, 10% Neutral Greys, 5% Accents (Teal/Cyan/Gold).

### 1.2 Neutral Greys
- **N0** `#0A0C10`  
- **N1** `#151922`  
- **N2** `#1F2630`  
- **N3** `#2B3542`  
- **N4** `#3B495A`  
- **N5** `#53657A`  
- **N6** `#93A1B1`  
- **N7** `#C9D1DB`  
- **N8** `#E6EBF0`

### 1.3 Status & Feedback
- **Success / Alignment** `#3ED598`  
- **Warning / Scarcity** `#F5A623`  
- **Danger / Rejection** `#FF5A6E`  
- **Info / Telemetry** `#4DA3FF`

### 1.4 Emissive Spectrum (Energy → Hue)
Use for activation gradients, entity orbs, and data‑viz heatmaps:
- **Low** `#2AF6D0` → **Mid** `#40A1FF` → **High** `#AA5BFF` → **Peak** `#F3E560`

**Gradient recipes:**
- **Membrane Ring:** `linear-gradient(180deg, #37D6DF 0%, #5FE3F1 60%, #EAD15A 100%)`
- **Entity Orb:** radial `#EAD15A 0% → #AA5BFF 35% → transparent 70%`

### 1.5 Accessibility
Maintain **4.5:1** contrast for body text and **3:1** for large text. On dark backgrounds, do not use pure white; prefer **N8 `#E6EBF0`** for text.

---

## 2) Typography

**Primary UI:** _Inter_ (sans, UI)  
**Secondary / Editorial:** _IBM Plex Serif_ (long‑form docs)  
**Monospace / Code:** _JetBrains Mono_

**Scale (Major Third):**  
- Display `64/72`  
- H1 `48/56`  
- H2 `36/44`  
- H3 `28/36`  
- H4 `22/28`  
- Body‑L `18/28`  
- Body `16/24`  
- Caption `13/18`  
- Micro `11/16`

**Weights:** 400 regular, 600 semibold, 700 bold.  
**Tracking:** −1% for Display/H1; default for others.  
**Link style:** Graph Cyan text with 1px bottom border `rgba(95,227,241,.5)`; hover increases opacity.

---

## 3) Layout, Spacing, and Grid

**Grid:** 12‑column; 72px gutters desktop, 24px mobile; max width 1280px content.  
**Spacing scale (8‑pt):** 4, 8, 12, 16, 24, 32, 40, 48, 64, 96, 128.  
**Radii:** 12, 16, 24 (cards 16, modals 24, badges 12).  
**Strokes:** 1px hairline on N3; 2px keylines for membranes.

**Elevation (shadows):**  
- E1: `0 1px 2px rgba(0,0,0,.4)`  
- E2: `0 8px 24px rgba(0,0,0,.45)`  
- E3: `0 24px 60px rgba(0,0,0,.55)` (Explorer surfaces)

---

## 4) Logo & Mark

- **Primary lockup:** Cyan ring stack icon + wordmark “Mind Protocol”. Prefer horizontal.  
- **Monochrome:** full white on dark, full black on light.  
- **Clear space:** `1×` the outer ring thickness on all sides.  
- **Minimum size:** 24px icon, 120px lockup.

**Do not:** skew, add drop shadows, recolor ring segments, or place on busy photographic backgrounds without a 12% black scrim.

---

## 5) Iconography

- **Style:** geometric line icons, rounded joins, **1.75px** stroke @1×.  
- **Corners:** 8% corner rounding to echo radii.  
- **Metaphors:** membranes as rings, emissions as tapered arcs, entities as orbs with 5 filaments.  
- **States:** outline (default), filled (active), strikethrough (disabled).

---

## 6) Illustration & Imagery

### 6.1 Stroke‑Soul Figures (Explorer)
- **Head:** 6 vertical brush strokes, evenly spaced, never touching.  
- **Filaments:** 5 emissive filaments emerging from head; chest orb lit.  
- **Texture:** brushed metal with micro‑scratches.  
- **Background:** pure void; no extra particles.  
- **Color:** emissive spectrum; gold near core; cyan/indigo limbs.  
- **Framing:** three‑quarter or profile; leave negative space for UI overlays.

**Quality checklist:** strokes unmerged, joints gapped, singular light source, no visual noise.

### 6.2 Partner Portraits
- Wireframe body (neon grid) + **one** hyperreal anchor (eye, cheekbone, hand, or earring).  
- Dark background; rim light in cyan or magenta; speculars in gold.  
- Reserved for identity, collectibles, or launch campaigns.

### 6.3 Evidence Photography (World)
- **Textures:** parchment, stamped paper, stone, metal plates, receipts.  
- **Lighting:** soft top‑down, 20° angle; real shadows.  
- **Color:** desaturated; keep warmth from paper; avoid neon.  
- **Treatment:** subtle vignette; 3% film grain.

---

## 7) Motion & Interaction

**Principles:** purpose‑bound, membrane‑aware, energy‑linked. No decorative loops.

**Durations:**  
- Micro (buttons, chips): 120–160ms  
- Panels, dialogs, ring openings: 180–220ms  
- Traversal highlights: 260–340ms  
- Scene transitions: 360–420ms

**Easing (cubic‑bezier):**  
- Standard: `0.2, 0.8, 0.2, 1`  
- Emissive spring: `0.16, 1, 0.3, 1`  
- Law/Docs (formal): `0.3, 0.0, 0.2, 1`

**Bindings:**  
- Orb pulse amplitude ↔ entity energy (log‑scaled).  
- Ring permeability ↔ opacity/width.  
- Ribbon thickness ↔ bandwidth; color shift ↔ utility.

**Reduce motion:** honor OS setting; swap to crossfades ≤120ms.

---

## 8) Components

### 8.1 Buttons
- **Primary:** Membrane Teal bg, N0 text; focus ring 2px Graph Cyan outer.  
- **Secondary:** Field Slate bg, N8 text; 1px N3 border.  
- **Tertiary:** text only, Cyan link with bottom border.

States: hover = +4% luminosity; active = pressed E2; disabled = 40% opacity + no shadow.

### 8.2 Cards & Panels
- Field Slate, 16px radius, E2 shadow, 1px N3 keyline; header uses Body‑L 600.  
- Optional _membrane top bar_ (2px gradient) to indicate compartment.

### 8.3 Badges & Chips
- Pill 12px radius; filled uses status colors; outline uses 1px with 16% fill.

### 8.4 Inputs
- 1px N4 border; focus ring 2px Cyan outside. Error border `#FF5A6E`; helper text Caption in N6.

### 8.5 Navigation
- Left rail 72px; icon + label on hover/expanded. Active item: ring glow underlay (blur 12px).

### 8.6 Data Surfaces
- **Traversal Theater:** dark canvas with entity orbs, 1px trails; WM pinned top‑right.  
- **Bridge Inspector:** stacked rings with animated permeability; transfer counters.

---

## 9) Data Visualization

- **Palettes:** Use Emissive Spectrum for energy, Neutral Greys for structure, Core Gold for highlights.  
- **Chart types:**
  - Activation over time → line with glow at peaks.  
  - Entity overlap → chord/ribbon with tapered ends.  
  - Permeability learning → dual‑axis (k and utility) with capped error bars.  
  - Quote accuracy → dot plot with 95% band.  
- **Do not** stack more than 5 hues; encode secondary values with thickness, opacity, or dash.

**Accessibility:** separate hues by ΔE ≥ 35; provide shape markers; ensure 3:1 contrast for strokes against canvas.

---

## 10) Theming & Modes

**Dark (default):** as specified.  
**Light:** background `#FCFDFE`, text `#111726`, accents keep same hues; shadows lighten:  
- E1 `0 1px 2px rgba(0,0,0,.08)`  
- E2 `0 8px 24px rgba(0,0,0,.12)`

**High‑contrast:** swap Neutral palette for N1/N8 extremes; outline buttons only; disable shadows.

---

## 11) Accessibility & Inclusive Design

- Minimum 44×44 touch targets; 24px min row height for dense tables.  
- Focus visible: 2px Cyan outer ring + 1px inner N0 knock‑out on dark.  
- All motion bound to Reduced Motion.  
- Alt text convention: `[surface]: [state] — [data focus]`.

---

## 12) Asset Production

**Export rules:**
- Icons: SVG, 24/20/16px artboards, stroke‑based no outlines.  
- Illustrations: 2× PNG on dark with transparent margins; keep glow in asset, not CSS.  
- Photos: 2400px wide JPEG, 85% quality, sRGB.

**Figma tokens (example):**
```json
{
  "color.brand.teal": "#37D6DF",
  "color.brand.gold": "#EAD15A",
  "color.canvas.dark": "#040507",
  "radius.card": 16,
  "elevation.e2": "0 8px 24px rgba(0,0,0,.45)"
}
```

**CSS variables (starter):**
```css
:root{--c-void:#040507;--c-slate:#121418;--c-teal:#37D6DF;--c-gold:#EAD15A;--c-cyan:#5FE3F1;--c-n3:#2B3542;--c-n8:#E6EBF0;--r-card:16px}
```

---

## 13) Do / Don’t Quickboard

**Do**
- Use emissive gradients sparingly to signal energy or membranes.  
- Keep Explorer scenes minimal; let orbs and ribbons carry meaning.  
- Render evidence with honest materials.

**Don’t**
- Mix neon emissives into document surfaces.  
- Animate without data linkage.  
- Over‑stack hues; favor thickness/opacity encodings instead.

---

## 14) Reference Layouts

- **Citizen Wall:** avatar (Stroke‑Soul or portrait), presence, WM entities, capabilities, economy strip.  
- **Traversal Theater:** full‑bleed dark canvas, WM dock, membrane overlays.  
- **Bridge Inspector:** concentric rings, transfer tickers, alignment fits.  
- **Docs / Evidence:** Warm Paper background, Plex Serif headings, stamped seals.

---

## 15) Governance of the Guide

- Changes propose via design RFC; snapshots tagged `design/v1.x`.  
- Visual lint: contrast tests, token diff, motion limits; CI blocks on failures.

> This guide is the single visual source of truth. If a new need isn’t addressed, extend the token set first, then components, then layouts—always keeping Explorer versus World separation intact.

