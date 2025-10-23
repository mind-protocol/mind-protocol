# Parchment & Renaissance Aesthetic - Extracted from Serenissima

## What It Does
Creates a warm, Renaissance Venice aesthetic using parchment backgrounds, gold accents, and classic serif typography. The system combines:
- **Parchment texture**: SVG noise filter for paper grain
- **Typography**: Cinzel (headers) + Crimson Text (body)
- **Color palette**: Warm parchment (#f5e7c1), gold metallics, Mediterranean blues
- **Visual effects**: Subtle animations, gold shimmer, paper-like textures

## How It Works

### Parchment Texture Generation
Uses inline SVG with feTurbulence filter to create realistic paper grain texture as a data URI background image.

**Technical approach:**
- SVG filter with fractalNoise turbulence
- Base frequency 0.8 with 4 octaves for fine grain
- Stitch tiles to create seamless pattern
- Low opacity (0.08) for subtle effect
- Applied as CSS background-image

## Original Implementation

### Parchment Background (from globals.css)

```css
.bg-parchment {
  background-color: #f5e7c1; /* Warm parchment base color */
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E");
}
```

**Decoded SVG:**
```xml
<svg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'>
  <filter id='noise'>
    <feTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/>
  </filter>
  <rect width='100' height='100' filter='url(#noise)' opacity='0.08'/>
</svg>
```

### Typography System

```css
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&display=swap');

:root {
  --font-header: 'Cinzel', serif;
  --font-body: 'Crimson Text', serif;
}

body {
  font-family: var(--font-body);
  line-height: 1.5;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-header);
}
```

### Gold Metallic Effects (for Ducats/Currency)

```css
.ducats-token, .compute-token {
  font-family: 'Geist', sans-serif;
  font-weight: 300;
  color: #b8860b; /* Dark goldenrod */
  display: inline-block;
  position: relative;
  letter-spacing: 0.5px;

  /* Animated gradient for metallic shimmer */
  background: linear-gradient(
    to right,
    #b8860b, /* Dark goldenrod */
    #ffd700, /* Gold */
    #daa520, /* Goldenrod */
    #ffd700, /* Gold */
    #b8860b  /* Dark goldenrod */
  );
  background-size: 200% auto;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine 2s linear infinite;
  text-shadow: 0 0 3px rgba(184, 134, 11, 0.3);
}

@keyframes shine {
  to {
    background-position: 200% center;
  }
}
```

### Parchment-Like UI Bubbles

```css
.assistant-bubble, .citizen-bubble {
  background: linear-gradient(145deg, #f97316, #fbbf24); /* Orange to amber gradient */
  color: #7c2d12; /* Dark brown for contrast */
  border: 1px solid #f97316;
  box-shadow:
    0 2px 5px rgba(0, 0, 0, 0.1),
    inset 0 1px 1px rgba(255, 255, 255, 0.7);
  position: relative;
  overflow: hidden;
  animation: bubbleAppear 0.3s ease-out forwards;

  /* Apply parchment texture */
  background-image: url("data:image/svg+xml,...same SVG as above...");
}

/* Subtle light reflection on top */
.assistant-bubble::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(to bottom,
    rgba(255, 255, 255, 0.2) 0%,
    rgba(255, 255, 255, 0) 100%);
  border-radius: inherit;
  pointer-events: none;
}

@keyframes bubbleAppear {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
```

### Animation Effects

```css
/* Mask floating animation (for decorative elements) */
@keyframes maskFloat {
  0% { transform: translateY(0px) rotate(0deg); }
  25% { transform: translateY(-8px) rotate(3deg); }
  50% { transform: translateY(0px) rotate(0deg); }
  75% { transform: translateY(-5px) rotate(-3deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}

.mask-float {
  animation: maskFloat 4s ease-in-out infinite;
}

/* Slide in animation for panels */
@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.slide-in {
  animation: slideIn 0.3s ease-out forwards;
}
```

## Adapted for Mind Harbor

### Hybrid Aesthetic: Digital Wireframe + Renaissance Venice

```css
/* Mind Harbor Root Variables */
:root {
  /* Typography */
  --font-header: 'Cinzel', serif;
  --font-body: 'Crimson Text', serif;

  /* Parchment Colors */
  --parchment-base: #f5e7c1;
  --parchment-dark: #e8dab2;
  --parchment-light: #fff8e7;

  /* Lagoon Water Colors */
  --lagoon-blue: #4a90a4;
  --lagoon-light: #6db3c5;
  --lagoon-dark: #2d5a6b;

  /* Wireframe Subentity Colors */
  --wireframe-teal: #00d9ff;
  --wireframe-copper: #ff6b35;
  --wireframe-emerald: #00ff88;
  --wireframe-gold: #ffd700;
  --wireframe-violet: #b19cd9;
  --wireframe-silver: #c0c0c0;

  /* Gold Accents */
  --gold-shimmer: #daa520;
  --gold-bright: #ffd700;
  --gold-dark: #b8860b;
}

/* Main Background: Parchment with Subtle Texture */
body, .mind-harbor-canvas {
  background-color: var(--parchment-base);
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E");
  font-family: var(--font-body);
}

/* Headers */
h1, h2, h3, h4, h5, h6, .header-text {
  font-family: var(--font-header);
  color: #2d1810; /* Dark brown for parchment contrast */
}

/* Lagoon Water Rendering (SVG) */
.lagoon-region {
  fill: var(--lagoon-blue);
  fill-opacity: 0.3;
  stroke: var(--lagoon-dark);
  stroke-width: 1.5;
  stroke-opacity: 0.5;
}

/* Wireframe Subentity Nodes */
.subentity-node {
  fill: none;
  stroke: var(--wireframe-teal); /* Default, change by subentity type */
  stroke-width: 2;
  filter: drop-shadow(0 0 8px currentColor);
}

.subentity-node.mind-protocol {
  stroke: var(--wireframe-gold);
}

.subentity-node.citizen {
  stroke: var(--wireframe-teal);
}

.subentity-node.building {
  stroke: var(--wireframe-copper);
}

/* Detail Panels: Parchment Cards */
.detail-panel {
  background: linear-gradient(145deg, var(--parchment-base), var(--parchment-light));
  border: 2px solid var(--gold-dark);
  border-radius: 8px;
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.15),
    inset 0 1px 2px rgba(255, 255, 255, 0.5);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;

  /* Add parchment texture */
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E");
}

/* Gold Shimmer for Value Displays */
.value-display {
  background: linear-gradient(
    to right,
    var(--gold-dark),
    var(--gold-bright),
    var(--gold-shimmer),
    var(--gold-bright),
    var(--gold-dark)
  );
  background-size: 200% auto;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine 2s linear infinite;
  font-weight: 600;
  font-family: var(--font-header);
}

/* Consciousness Activity Paths */
.activity-path {
  stroke: var(--wireframe-emerald);
  stroke-width: 2;
  stroke-opacity: 0.7;
  fill: none;
  stroke-dasharray: 5,3;
  animation: pathFlow 2s linear infinite;
}

@keyframes pathFlow {
  to {
    stroke-dashoffset: -16;
  }
}
```

### Subentity Icon Treatment (Emoji Temporary, Wireframe Future)

```css
/* Current: Emoji Icons with Wireframe Glow */
.subentity-icon {
  font-size: 24px;
  filter: drop-shadow(0 0 6px var(--wireframe-teal));
  transition: filter 0.3s ease;
}

.subentity-icon:hover {
  filter: drop-shadow(0 0 12px var(--wireframe-gold));
}

/* Future: Custom Wireframe SVG Icons */
.wireframe-icon {
  width: 32px;
  height: 32px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 0 8px currentColor);
}
```

## Dependencies
- **Google Fonts**: Cinzel + Crimson Text
- **SVG Filters**: Browser-native support
- **CSS Gradients**: Webkit prefix for text-fill-color

## Integration Steps for Mind Harbor

1. **Import Fonts**: Add Google Fonts link to `<head>`
2. **Define CSS Variables**: Add parchment/lagoon/wireframe color palette
3. **Apply Base Styles**: Set parchment background on main container
4. **Add Texture**: Use SVG data URI for paper grain
5. **Style Panels**: Apply parchment card styling to detail panels
6. **Wireframe Subentities**: Add glow filters to D3 nodes
7. **Lagoon Regions**: Render water as SVG paths between sparse clusters
8. **Gold Accents**: Apply shimmer animation to value displays

## Testing Approach

1. **Visual Inspection**: Verify parchment texture is subtle, not overwhelming
2. **Contrast Check**: Ensure dark brown text is readable on parchment
3. **Animation Performance**: Test gold shimmer doesn't cause jank
4. **Font Loading**: Verify fallback fonts during load
5. **Cross-Browser**: Test SVG filters in Chrome, Firefox, Safari

## Notes & Caveats

- **SVG Data URI Encoding**: Must be properly URL-encoded
- **Filter Performance**: SVG filters can be GPU-intensive on weak devices
- **Font Loading**: FOUT (Flash of Unstyled Text) possible - consider font-display: swap
- **Color Contrast**: Maintain WCAG AA compliance (4.5:1 ratio min)
- **Emoji Icons**: Temporary solution; plan migration to custom wireframe SVG icons

## Visual Hierarchy

### Parchment Layer (Background)
- Warm base color (#f5e7c1)
- Subtle noise texture
- Paper grain effect

### Lagoon Layer (Mid-ground)
- Semi-transparent blue (#4a90a4 @ 30% opacity)
- Only rendered between sparse clusters
- Subtle wave animation (optional)

### Wireframe Layer (Foreground)
- Glowing subentity nodes
- Activity paths with dash animation
- High contrast against parchment

### Gold Accent Layer (Highlights)
- Value displays
- Panel borders
- Interactive highlights

## Texture Parameters

**Parchment Noise:**
- Type: fractalNoise
- Base Frequency: 0.8
- Octaves: 4
- Opacity: 0.08

**Adjustments for Mind Harbor:**
- Consider slightly lower opacity (0.06) for more subtlety
- May increase base frequency (0.9) for finer grain
- Add slight sepia tone overlay (optional)

## Color Palette Summary

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Parchment Base | Warm Cream | #f5e7c1 | Background |
| Parchment Dark | Aged Paper | #e8dab2 | Shadows |
| Lagoon Blue | Mediterranean | #4a90a4 | Water regions |
| Wireframe Teal | Digital Cyan | #00d9ff | Default subentities |
| Wireframe Copper | Warm Metal | #ff6b35 | Buildings |
| Wireframe Gold | Divine Light | #ffd700 | Mind Protocol |
| Gold Shimmer | Rich Gold | #daa520 | Value displays |
| Text Dark | Espresso | #2d1810 | Body text |

## Future Enhancements

- **Scroll texture**: Subtle parchment edge curl for detail panels
- **Ink bleed effect**: Slight feathering on text edges
- **Seal stamps**: Decorative wax seal graphics for important nodes
- **Watermark**: Faint Mind Protocol logo as background watermark
- **Aged parchment**: Slight yellowing gradient from center to edges
