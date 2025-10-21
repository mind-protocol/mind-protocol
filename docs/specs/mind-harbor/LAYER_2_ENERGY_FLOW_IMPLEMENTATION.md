# Layer 2: Energy Flow Animation - Implementation

**Author:** Iris "The Aperture"
**Date:** 2025-10-19
**Status:** ✅ Implemented, Ready for Testing

---

## What Is Layer 2?

Layer 2 visualizes **energy flowing through the graph** when sub-entities traverse nodes.

**You see:** Colored particles moving along invisible links from source → target as sub-entities explore.

**Purpose:** Make sub-entity graph traversal visible in real-time.

---

## What You See

### When Sub-Entity Traverses:

1. **WebSocket event arrives** → `entity_activity` with `current_node`
2. **Particle spawns** at current node position
3. **Particle travels** along link to recently activated target node
4. **Entity-colored** (matches sub-entity: teal/amber/cyan/etc)
5. **500ms journey** with smooth ease-out animation
6. **Particle fades** after completing journey

**Result:** "Every time a tick and energy is flowing, I see a particular grain from one to the other" (Nicolas's requirement)

---

## Technical Implementation

### Component: `EnergyFlowParticles.tsx`

**Architecture:**
- Listens to `entity_activity` WebSocket stream
- Creates particle on each traversal event
- Animates particle using `requestAnimationFrame`
- Cleans up expired particles (> 500ms old)

**Performance:**
- Only recent events (last 2 seconds)
- Particle limit (expired particles removed)
- `useMemo` for node position lookup
- SVG particles (GPU-accelerated)

### Particle Structure:

```typescript
interface Particle {
  id: string;              // Unique identifier
  sourceX: number;         // Start position
  sourceY: number;
  targetX: number;         // End position
  targetY: number;
  entityColor: string;     // Sub-entity color
  startTime: number;       // Animation start
  duration: number;        // 500ms
}
```

### Animation Algorithm:

```typescript
// Ease-out cubic for smooth deceleration
const progress = Math.min(elapsed / duration, 1);
const eased = 1 - Math.pow(1 - progress, 3);

// Interpolate position
const x = sourceX + (targetX - sourceX) * eased;
const y = sourceY + (targetY - sourceY) * eased;
```

### Target Detection:

**Challenge:** WebSocket event only provides `current_node`, not link target.

**Solution:** Heuristic based on recent activations:
1. Find nodes activated by same sub-entity
2. Within last 100ms (very recent)
3. Not the current node itself
4. That's the traversal target

**Limitation:** May miss some traversals if timing doesn't align. Good enough for visualization.

---

## SVG Filters

Added particle blur filter to GraphCanvas:

```typescript
// PARTICLE BLUR FILTER (for energy flow particles)
const particleBlur = defs.append('filter')
  .attr('id', 'particle-blur')
  .attr('stdDeviation', '3');
```

**Effect:** Particles have soft glow matching sub-entity color.

---

## Integration

### Page Layout (Layer Stack):

```
1. GraphCanvas (base: nodes + links)
2. EntityClusterOverlay (Layer 1: sub-entity names)
3. EnergyFlowParticles (Layer 2: flow animation) ← NEW
4. ActivationBubbles (event notifications)
```

**Z-order:** Particles render above clusters but below bubbles.

---

## Performance Characteristics

**Optimizations Applied:**
- Only animate recent events (2 second window)
- Limit active particles (auto-cleanup)
- `useMemo` for node positions (computed once)
- `requestAnimationFrame` for smooth animation
- SVG rendering (GPU-accelerated)

**Performance Target:**
- Handle 10+ traversals/second without lag
- Smooth 60fps animation
- No memory leaks (particles cleaned up)

---

## Particle Visual Design

**Core Particle:**
- 3px radius circle
- Solid entity color
- 90% opacity

**Glow Halo:**
- 6px radius circle
- Same entity color
- 30% opacity
- Gaussian blur filter

**Result:** Glowing orb effect matching sub-entity color scheme.

---

## Data Flow

```
1. SubEntity traverses graph (backend)
   ↓
2. entity_activity event → WebSocket
   ↓
3. useWebSocket hook captures event
   ↓
4. EnergyFlowParticles receives entityActivity array
   ↓
5. Latest event processed → spawn particle
   ↓
6. requestAnimationFrame animates particle
   ↓
7. Particle removed after 500ms
```

---

## Known Limitations

### 1. Target Detection Heuristic
**Limitation:** Uses timestamp proximity to infer link target
**Impact:** May miss some traversals if timing doesn't align
**Acceptable:** Visualization shows representative flow, not 100% coverage

### 2. No Link Path Following
**Limitation:** Particles travel straight line, not along actual link curves
**Impact:** Visual approximation, not exact path
**Future:** Could use D3 link path data for curved trajectories

### 3. Particle Limit
**Limitation:** Very fast traversal (20+/sec) may overflow
**Impact:** Some particles may not render
**Acceptable:** Performance > completeness for visualization

---

## Testing Checklist

### Visual Verification:
- [ ] Particles spawn at traversed nodes
- [ ] Particles move smoothly toward target
- [ ] Entity colors match sub-entity
- [ ] Glow effect visible
- [ ] Particles disappear after animation
- [ ] No visual artifacts (stuttering/flickering)

### Performance Verification:
- [ ] No lag with 10+ particles active
- [ ] 60fps animation maintained
- [ ] Memory stable (no leaks)
- [ ] Particles cleaned up correctly

### Data Verification:
- [ ] Responds to real WebSocket events
- [ ] Correct sub-entity colors used
- [ ] Target detection reasonably accurate
- [ ] No crashes on missing data

---

## Next Steps: Layer 3

**Layer 3: Mechanism Visualization**

Once Layer 2 is tested:

1. **Mechanism overlays** - show which mechanisms active
2. **Per-mechanism visualizations** - custom view for each
3. **Toggle mechanism visibility** - collapsed menu
4. **Mechanism activity indicators** - visual encoding

**Implementation approach:**
- Create `MechanismOverlay` component
- One visualization per mechanism type
- Toggleable from UI control
- Positioned on graph, not separate panel

---

## Code Locations

**Component:** `app/consciousness/components/EnergyFlowParticles.tsx`
**Integration:** `app/consciousness/page.tsx` (line 206-209)
**Filter:** `app/consciousness/components/GraphCanvas.tsx` (line 152-162)
**Colors:** `app/consciousness/constants/entity-colors.ts`

---

**"Energy flows where attention goes. Now you can see it."**

— Iris "The Aperture"

Layer 2 makes sub-entity traversal visible.
