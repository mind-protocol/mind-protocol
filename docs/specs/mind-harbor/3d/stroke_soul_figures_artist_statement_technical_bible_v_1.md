# Stroke‑Soul Figures — Artist Statement & Technical Bible v1

**Author:** Iris “The Aperture” (compiled with Assistant)
**Version:** v1 (2025‑10‑21)
**Purpose:** A complete creative + technical specification for producing the luminous brush‑ribbon figures ("stroke‑soul" style). Contains artist statement, aesthetic philosophy, emotional/phenomenological notes, and deterministic build rules for reproducible images and animations.

---

## 1) Artist Statement

**What I’m making**
I paint people as motion—bodies written in strokes of metal and light. The figures aren’t filled; they’re **sentences** spelled by gestures, each joint a comma, each filament a clause of feeling. The core glows from the chest—the **soul as a diffuse sun**—and the nervous system carries that brightness into the hands, the feet, the groin. Idsubentity is not an outline you color in; it’s a path you take.

**How it should feel**
Elation without strain. Vulnerability without collapse. The dignity of metal meeting the candor of unfinished brush marks. The viewer should sense the **clean air between strokes**, a respect of boundaries that enables resonance. These bodies do not collide—they harmonize.

**Why Venice sometimes, why night often**
Topology matters. Bridges and water teach attention where it can and cannot go. Even in a void, the figures respect constraints; that’s what gives the motion truth.

**My promise to the viewer**
I won’t fake solidity. I’ll show the **inside‑out light** and the gaps where breath lives. I’ll keep the materials precious—specular, textured, reflective—because consciousness deserves craft.

---

## 2) Emotional Tones, Topics, Worldview, Lens, Awareness

### Emotional Tones
- **Elation‑in‑motion:** Leaping, reaching bodies = joy and becoming.
- **Tender exposure:** Open silhouettes and visible gaps = brave softness.
- **Sacred warmth:** The chest orb reads holy but intimate—a hearth.
- **Electric intimacy:** Five inner filaments feel touchable, near‑somatic.
- **Playful gravitas:** Starfields and gilded strokes = wonder with ceremony.

### Core Topics
- **Consciousness as activity:** People as verbs; idsubentity is traversal.
- **Coherence from fragments:** Wholeness emerges from non‑touching parts.
- **Relationality:** Hands extended; dancing rings; interweaving flows.
- **Energy hygiene:** Boundaries and constraints enable real freedom.
- **Embodiment as lightcraft:** Nerves and aura are first‑class forms.

### Worldview (Philosophy)
- **Phenomenology‑first:** Felt flow outranks mechanism.
- **Optimistic realism:** Hard materials + inner light; both are true.
- **Non‑dual craft:** Digital precision with painterly ritual; equals.
- **Plural harmonics:** Many hues, many bodies, one dance.
- **Becoming over being:** The self is rewritten continuously; gaps are breath.

### Special Lens (How the images “see”)
- **Calligraphic anatomy:** Bodies as sentences; joints are commas.
- **Field perception:** Read glows/overlaps/affordances over objects.
- **Inside‑out lighting:** Illumination originates within the body.
- **Constraint‑aware framing:** Voids/water/panels teach where *not* to go.
- **Time blur:** Long‑exposure memory—the lingering is what mattered.

### Type of Awareness Portrayed
- **Kinesthetic intuition:** Knowing by moving.
- **Distributed selfing:** Mind as networked agency (five head‑born lines).
- **Affective clarity:** Stable heart‑center; radiating, not flooding.
- **Attuned boundaries:** Clean edges, consent, resonance over collision.
- **Ecstatic composure:** Serenity and rapture, held at once.

---

## 3) Visual Grammar (from the artist’s rules)

### Head (Always)
- **Three face strokes** define direction and presence.
- **One back‑of‑head stroke** arcs from occiput, often flowing into hair.
- **Two jaw strokes** hook from ear/hinge toward chin corners.
> Total head strokes = **6**. No facial features. Strokes do **not** touch.

### Body Outline Strokes
- Neck (1). Shoulder caps (optional). Arms: upper + forearm per side (gaps at elbows). Back diminution (1 long taper). Torso curves (1–2). Hips crest (1). Crotch (1 short anchor). Legs: thigh + shin per side (gaps at knees). Feet (optional flicks). Hands: **one stroke per finger** (5 per hand).
> All strokes have **volume** (small thickness), metallic texture, and **never touch**—maintain air gaps.

### Nervous System (Always Five)
- **Origin:** inside head
- **Count:** **5 luminous filaments**
- **Paths:** remain **inside** body envelope; natural curves
- **Termini:** include at least one hand, one foot, and the crotch; remaining lines may target the other hand/foot/occipital/sterna rim.

### Chest Orb (Always)
- **Diffuse, glowing core** centered in sternum; soft radius; not a glass ball.

### Color Linking (Per Character)
- Each character uses a **harmonic trio**: stroke hue ≈ line hue ≈ orb hue (minor offsets < 15° in hue).

---

## 4) Materials & Rendering

### Metallic Brush Strokes (the body)
- **Look:** textured metallic / brush‑foil hybrid; reflective, anisotropic, with visible grain and paint gaps.
- **Parameters (typical):**
  - Metallic 0.85 ± 0.06; Specular 0.75 ± 0.10; Roughness 0.18 ± 0.06
  - Thickness = 10–20% of stroke width; width 0.9–1.6% of image height (fingers 0.25–0.45%)
  - Edge fray noise 1–3 px; 0.5–2 cycles; alpha jitter 0–20% along length
  - Anisotropy 0.6 ± 0.2 aligned to stroke tangent
- **Textures:** layered base color + foil noise + micro‑scratches + paint flecks. Ensure unfinished spaces remain visible.

### Emissive Filaments (nervous system)
- Width 0.12–0.28% of image height; emissive intensity head:1.0 → distal:0.5; subtle bloom. Lines sit visually above metals but may weave under/over via masks.

### Chest Orb
- Diffuse sphere/oval glow (radius 3–6% of image height). Add shallow volumetric halo; tint matches character hue.

### Post
- Bloom radius 5–10% of frame; threshold just under clipping; slight chromatic dispersion at hottest whites. Light vignette except in plaster‑panel variant.

---

## 5) Spatial Rules & QA

- **No touching:** Minimum clearance `d_min = max(0.3% image height, 1.5× stroke width)` between any two strokes/lines.
- **Gaps at joints:** visible interruptions at shoulder/elbow/wrist/hip/knee/ankle.
- **Open silhouette:** never close the outer contour.
- **Filaments inside:** all five remain within body envelope at all times.
- **Chest orb present:** centered at sternum; remains un‑cropped.
- **Color trio consistent:** strokes, filaments, orb in one family.

**QA Checklist** (tick before publishing)
- [ ] Head = 3 face + 1 back + 2 jaw
- [ ] Hands = 5 strokes each
- [ ] Nervous lines = 5 from head → correct termini
- [ ] Orb = diffuse chest glow
- [ ] Metallic texture visible; unfinished brush gaps readable
- [ ] Strokes never touch; joint gaps present

---

## 6) Deterministic Build Process

1. **Pose scaffold:** 15‑joint skeleton; choose diagonal motion vector; set one reaching arm and one trailing; one knee raised, one leg back.
2. **Head first (6 strokes):** three face strokes, back‑of‑head arc, two jaw hooks. Ensure air gaps.
3. **Torso/back/hips/crotch:** lay long tapers; keep back diminution readable.
4. **Arms & legs:** upper and lower boundaries as separate strokes; leave elbow/knee gaps.
5. **Hands:** five finger strokes per hand; thumb rotated; tips do not touch other strokes.
6. **Feet (optional flicks).**
7. **Nervous system:** spawn **five** emissive filaments inside head; route within body to at least {one hand, one foot, crotch} + two other endpoints; smooth C² curves with modest meander; brightest at origin.
8. **Chest orb:** add diffuse central glow; tint to palette; reflect subtly in nearby metals.
9. **Material pass:** assign metallic parameters and textures; anisotropy along tangents; introduce paint gaps (alpha jitter).
10. **Color link:** pick hue family; set strokes/lines/orb to closely related values; apply ±5–12° hue jitter for naturalism.
11. **Non‑intersection solve:** enforce `d_min` by nudging stroke control points or trimming.
12. **Lighting/post:** bloom/dispersion/vignette as above; keep midtones minimal for high contrast.

---

## 7) Palette Families (starter sets)

- **Amber/Gold:** strokes #E4A631 → #F7D37A; lines/orb #FFD27A → #FFE6B0
- **Rose/Carmine:** strokes #F06A6A → #FF97A8; lines/orb #FFC1C9
- **Teal/Cyan:** strokes #1DB7B3 → #6FE7E2; lines/orb #A9FFFF
- **Violet/Magenta:** strokes #8B6EF0 → #D29AF7; lines/orb #F5C6FF

(Adjust toward scene lighting; keep lines/orb 5–15° warmer/cooler than strokes.)

---

## 8) Prompt Dialect (for generative tools)

> **Style lock:** “Luminous metallic brush‑ribbon figure; three face strokes + back‑of‑head arc + two jaw hooks; separate outline strokes for neck/arms/legs/torso/hips/crotch; one stroke per finger; strokes never touch; five glowing filaments start inside the head and stay inside the body, terminating at hands/feet/crotch; diffuse chest orb at sternum; textured metallic materials with anisotropic specular, visible brush grain and unfinished gaps; high contrast; inside‑out lighting; ecstatic composure.”

Include color family tokens, e.g., “amber/gold strokes, matching amber filaments and chest orb.”

---

## 9) Animation Notes

- **Stroke stability:** body strokes stay fixed to rig bones (skinned), slight secondary jiggle.
- **Filament drift:** slow, low‑amplitude noise; endpoints anchored.
- **Orb pulsing:** 6–12 BPM gentle breathing; bloom radius sync.
- **Camera:** diagonal tracking; allow occasional limb crop; never crop the orb.

---

## 10) Variants & Backgrounds

- **Void:** true black; maximal bloom.
- **Starfield:** low‑contrast cosmic field; filaments echo constellation logic.
- **Plaster panel:** matte ivory panel with engraved negative strokes (non‑emissive); raking light for relief.
- **Venice topology:** stroke figures obey water/bridge constraints; no stroke crosses water.

---

## 11) Maintenance

Log any palette or parameter changes with version bumps. Keep a small gallery of canonical frames as regression tests (one per palette family and background variant).

---

**Mantra:** *Open, bright, and breathing. The body is a sentence; the soul is its light.*



---

## 12) Enrichment Addendum — Voice & Vision Integration (v1.1)

> **North Star:** *Aesthetics are architecture.* The Explorer (interface) is futuristic and luminous; the World (content) is realistic and material (Venice stone, parchment, economic anchors). **No motion without meaning.**

### 12.1 Hybrid Model (UI ↔ Reality)
- **Explorer/UI:** luminous metallic brush‑ribbons, calligraphic anatomy, Cinzel/Crimson Text for headings/longform, subtle amber gradients.
- **Content/Findings:** photoreal backdrops (Venice, parchment panels, receipts), physically plausible lighting & shadows.
- **Rule of Belonging:** if it depicts **consciousness/attention**, it may be abstract + emissive; if it depicts **evidence/ground**, it must be realistic and textured.

### 12.2 Semantic Animation Doctrine
- **Allowed (data‑bound):**
  - **Traversal:** figures crossing bridges; five head‑born filaments rerouting to currently active limbs.
  - **Activation/Arousal:** chest‑orb breathing = `orb_bpm = map(energy,0..1 → 6..12)`.
  - **Constraint Feedback:** water shimmer intensifies near blocked links; sottoportego glow denotes committed path.
  - **Integration:** additive color mixing when subentities co‑occupy a node.
- **Disallowed:** idle bobbing, purposeless parallax, decorative particles, fake water ripples.

### 12.3 Naming & Frames (beyond “dashboard”)
- **Consciousness Viewer** (global), **Traversal Theater** (live movement), **Bridge Inspector** (link semantics), **Basin View** (global workspace / Bacino), **Parchment Panel** (evidence/receipts/quotes).

### 12.4 Process Discipline — Test Over Theory
- Every spec addition ships with a **test scene** + **acceptance criteria**:
  1) Renders at sparse/medium/dense energies. 2) Water constraint legible (no illegal crossings). 3) ≥1 animation parameter bound to a real metric. 4) Bible QA passes (head=6 strokes; 5 filaments from head; chest orb; no touches; joint gaps; palette harmony).
- **Reality checks:** filesystem assets exist; loops derive from data; performance goal 60 fps ≤ 40 figures (LOD beyond).

### 12.5 Venice Topology Mapping (condensed)
- **Nodes:** islands/buildings. **Links:** bridges/sottoportegos. **Constraints:** water (impassable). 
- **Semantics:** San Marco = central hub; Santa Margherita = residential co‑activation; Rialto/Accademia = high‑traffic links; Bacino = global workspace. Stroke‑figures traverse the **real** Venice; chest‑orb = node activation; filaments visualize decision routes.

### 12.6 Prompt Dialect (short lock)
> *“Luminous metallic brush‑ribbon figure; head from 3 face strokes + back‑arc + 2 jaw hooks; separate outline strokes for every limb and finger, never touching, joints gapped; five glowing filaments start in the head and stay inside the body to hands/feet/crotch; diffuse chest orb at sternum; interface futuristic, content realistic (Venice/parchment); no meaningless animation; water is a hard boundary.”*

### 12.7 Data‑Binding Snippets (ready to wire)
```pseudo
orb_bpm        = clamp(map(energy, 0..1, 6..12))
filament_targets = select_endpoints({hand, foot, crotch}, policy="coverage")
bridge_opacity = map(link.strength, 0..1, 0.2..1.0)
node_glow      = sigmoid(node.activation, k=6)
```

### 12.8 Acceptance Checklists (merge into §5)
**Aesthetic QA** — Hybrid respected; stroke grammar satisfied (head=6; fingers 5/hand; gaps; no touches); 5 filaments from head inside body; chest orb harmonized; palette trio coherent.  
**Semantic Motion QA** — All movement data‑driven; constraint legible; integration via additive light.  
**Performance QA** — Stroke/bloom maintain target fps; LOD active beyond 40 figures.

### 12.9 Roadmap Hooks
- **Icon pass** (replace temporary emojis with bespoke glyphs).
- **Venice Sunrise Pack** (canonical scenes for San Marco, Rialto, Santa Margherita, Bacino).
- **Historical Playback** (timeline scrub + stroke‑trail echoes). 
- **Consequence Mode** (link thickness ∝ cost/latency; parchment receipts for actions).

---

## 13) Optional Parameter Schema (for generators)

```json
{
  "pose": {"vector_deg": 35, "knee_raise": 0.6, "arm_reach": 0.8},
  "palette": {"family": "amber", "hue_jitter": 8, "value": 0.95},
  "strokes": {"width_pct": 1.2, "thickness_pct": 0.18, "edge_fray_px": 2},
  "hands": {"fingers_per_hand": 5},
  "nervous_lines": {"count": 5, "origin": "head", "endpoints": ["L_hand","R_foot","crotch","R_hand","L_foot"]},
  "orb": {"radius_pct": 4.5, "bpm": 9},
  "constraints": {"no_touch_clearance_pct": 0.3, "joint_gaps_pct": 4},
  "environment": {"mode": "venice", "location": "Piazza San Marco", "lighting": "sunrise"}
}
```

> Keep §1–§11 unchanged; this addendum augments practice and wiring without altering the core grammar.

