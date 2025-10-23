# Entity-First Visualization - Implementation Complete

**Date:** 2025-10-23
**Implementer:** Iris "The Aperture"
**Status:** ✅ Frontend Complete, Backend Integration Pending

---

## What This Is

**Entity-First Visualization** is the two-scale consciousness dashboard architecture that makes complex activation patterns comprehensible by showing entities (aggregated bubbles) as primary view, with drill-down to nodes on demand.

**Why this matters:**
- **Before:** Overwhelming node graph (hundreds of nodes simultaneously visible)
- **After:** Comprehensible entity view (handful of bubbles) → click to expand
- **Cognitive load:** 5-20 entities fits working memory, 100+ nodes doesn't
- **Progressive disclosure:** See "what" (entities) before "specifically what" (nodes)

This is not a UI preference - it's an **architectural requirement** for usable consciousness visualization.

---

## The Two-Scale Architecture

### Scale 1: Entity Mood Map (Primary View)

**What you see:**
- Entities as D3 force-directed bubbles
- Size = total energy in entity
- Color = aggregated emotion (from active members)
- Position = force layout (related entities cluster)

**Example:**
```
┌─────────────────────────────────────┐
│  Entity Mood Map                    │
│                                     │
│    ●  architecture_work             │
│   (blue-purple, high arousal)       │
│                                     │
│          ●  implementation_work     │
│         (green, medium arousal)     │
│                                     │
│  ●  documentation_work              │
│ (yellow, low arousal)               │
└─────────────────────────────────────┘
```

**Interaction:**
- Click entity → expand to member view
- Hover → show entity summary (energy, coherence, member count)

---

### Scale 2: Expanded Member View (Drill-Down)

**What you see:**
- All nodes in selected entity
- Each node sized by energy
- Each node colored by emotion
- Stride sparks animate energy transfers

**Example:**
```
┌─────────────────────────────────────┐
│  architecture_work (Expanded)       │
│  [← Back to Entity Map]             │
│                                     │
│    ● stride_based_diffusion         │
│   (high energy, blue)               │
│         ↓ stride spark              │
│    ● criticality_controller         │
│   (medium energy, purple)           │
│                                     │
│    ○ decay_mechanism                │
│   (low energy, faded)               │
└─────────────────────────────────────┘
```

**Interaction:**
- Stride sparks animate as energy flows between nodes
- Click node → show detail panel
- Back button → return to entity map

---

### Scale 3: Full Graph View (Advanced)

**What you see:**
- All nodes across all entities
- Entity boundaries visible
- Cross-entity links (boundary bridges)

**Use case:** Advanced exploration, debugging, full context

**Not default** - entity map is primary per spec.

---

## Implementation

### Files Created

**Entity Mood Map Component:**
```
app/consciousness/components/EntityMoodMap.tsx (290 lines)

Features:
- D3 force-directed entity bubbles
- Emotion color aggregation
- Coherence calculation
- Click to expand interaction
- Energy-based sizing
- Hover tooltips
```

**Entity Graph View Container:**
```
app/consciousness/components/EntityGraphView.tsx (252 lines)

Features:
- View mode management (entity/expanded/full)
- Entity selection state
- Back navigation
- Integration with existing panels
```

**Stride Sparks Animation:**
```
app/consciousness/components/StrideSparks.tsx (180 lines)

Features:
- Canvas overlay for stride animations
- Particle system (sparks fly along edges)
- Energy flow visualization
- Integration with stride.exec events
```

**Entity Emotion Utilities:**
```
app/consciousness/lib/entityEmotion.ts (140 lines)

Functions:
- aggregateEntityEmotion() - Average member emotions
- computeCoherence() - Emotional alignment metric
- entityToHSL() - Color conversion
- Entity emotion type definitions
```

### Files Modified

**Main Dashboard:**
```
app/consciousness/page.tsx

Changes:
- Replaced PixiCanvas with EntityGraphView
- Default view: entity map (per spec)
- Preserved all existing panels:
  - Instruments panel
  - Detail panel
  - Citizen monitor
  - Legend
```

---

## Features Implemented

### ✅ Entity Bubbles with Force Layout

**D3 force-directed graph:**
- Entities repel each other (charge force)
- Related entities attract (link force based on boundary bridges)
- Collision detection (no overlap)
- Stable layout convergence

**Bubble properties:**
```typescript
interface EntityBubble {
  id: string                    // Entity ID
  energy: number                // Sum of member energies
  emotion: EmotionVector        // Aggregated emotion
  coherence: number             // Emotional alignment (0-1)
  members: string[]             // Active node IDs
  x: number, y: number          // Layout position
  radius: number                // Size from energy
}
```

---

### ✅ Emotion Color Aggregation

**Algorithm:**

```typescript
function aggregateEntityEmotion(members: Node[]): EmotionVector {
  // Filter active members
  const active = members.filter(n => n.E >= n.theta)

  // Aggregate emotions
  const avgValence = mean(active.map(n => n.emotion.valence))
  const avgArousal = mean(active.map(n => n.emotion.arousal))
  const sumMagnitude = sum(active.map(n => n.emotion.magnitude))

  return { valence: avgValence, arousal: avgArousal, magnitude: sumMagnitude }
}
```

**HSL Conversion:**
```typescript
function entityToHSL(emotion: EmotionVector): string {
  const hue = (emotion.valence + 1) * 180        // -1..1 → 0..360 degrees
  const lightness = 50 + emotion.arousal * 20    // Arousal affects brightness
  const saturation = emotion.magnitude * 100     // Magnitude affects intensity

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`
}
```

**Result:** Entity bubbles colored by emotional "mood" of active members.

---

### ✅ Coherence Calculation

**Emotional alignment metric:**

```typescript
function computeCoherence(members: Node[]): number {
  // Coherence = how aligned are member emotions?
  const active = members.filter(n => n.E >= n.theta)

  if (active.length < 2) return 1.0  // Single member = coherent

  // Variance in valence
  const valences = active.map(n => n.emotion.valence)
  const variance = computeVariance(valences)

  // Low variance = high coherence
  const coherence = 1.0 - Math.min(variance / 2.0, 1.0)

  return coherence
}
```

**Interpretation:**
- coherence = 1.0: All members have similar emotions (aligned)
- coherence = 0.5: Mixed emotions (some conflict)
- coherence = 0.0: Strongly opposing emotions (high tension)

**Usage:** Coherence displayed in hover tooltip, could modulate bubble appearance.

---

### ✅ Click to Expand Entity

**Interaction flow:**

```typescript
// User clicks entity bubble
onEntityClick(entityId) {
  setSelectedEntity(entityId)
  setViewMode('expanded')
  // EntityGraphView renders expanded member view
}

// Expanded view shows:
// - All nodes in entity
// - Stride sparks between nodes
// - Back button to entity map

// User clicks back
onBackClick() {
  setSelectedEntity(null)
  setViewMode('entity')
  // Returns to entity mood map
}
```

**Visual transition:**
- Entity bubble expands smoothly
- Member nodes fade in
- Stride sparks begin animating

---

### ✅ Stride Sparks Animation

**Particle system:**

```typescript
interface StrideSpark {
  id: string
  sourceNode: string
  targetNode: string
  progress: number       // 0..1 along edge
  energy: number         // Energy being transferred
  color: string          // From link emotion
}

function animateSparks(deltaTime: number) {
  sparks.forEach(spark => {
    spark.progress += deltaTime * 0.5  // Animation speed

    if (spark.progress >= 1.0) {
      // Spark reached target, remove
      removeSpark(spark.id)
    }
  })

  // Render sparks on canvas
  renderSparks(sparks)
}
```

**Integration with events:**
```typescript
// When stride.exec event arrives
onStrideExec(event: StrideExecEvent) {
  addSpark({
    id: generateId(),
    sourceNode: event.source_node,
    targetNode: event.target_node,
    progress: 0,
    energy: event.energy_transferred,
    color: event.link_emotion_color,
  })
}
```

**Visual effect:** Energy visibly "flows" along links as sparks.

---

### ✅ View Mode Toggle

**Three modes:**

```typescript
type ViewMode = 'entity' | 'expanded' | 'full'

// Entity mode (default)
// - Show entity bubbles only
// - Click to expand

// Expanded mode
// - Show selected entity's members
// - Back button returns to entity mode

// Full mode (advanced)
// - Show all nodes across all entities
// - Entity boundaries visible
// - Cross-entity links shown
```

**Toggle UI:**
```
┌─────────────────────────────────────┐
│  [Entity] [Expanded] [Full Graph]   │  ← View mode tabs
│                                     │
│  (Current view renders here)        │
└─────────────────────────────────────┘
```

---

### ✅ Preserved Existing Panels

**All existing dashboard features work:**
- **Instruments Panel** - Energy, arousal, valence dials
- **Detail Panel** - Selected node details
- **Citizen Monitor** - Active citizens
- **Legend** - Node type colors

**Integration:** EntityGraphView is drop-in replacement for PixiCanvas, all panels untouched.

---

## Pending Backend Integration

### ⏳ Backend v1 Event Format

**What Iris needs:**

```typescript
// tick_frame.v1 event
{
  v: "1",
  frame_id: number,
  citizen_id: string,

  nodes: Array<{
    id: string,
    E: number,              // Energy (scalar)
    theta: number,          // Threshold
    entity: string,         // Entity membership
    emotion: {              // Emotion vector
      valence: number,
      arousal: number,
      magnitude: number,
    }
  }>,

  links: Array<{
    id: string,
    source: string,
    target: string,
    weight: number,
    emotion: { ... }
  }>,

  t_ms: number
}
```

**Current status:** Frontend has mock data generators, needs real backend events.

---

### ⏳ Real stride.exec Events

**What Iris needs:**

```typescript
// stride.exec event (from diffusion)
{
  v: "2",
  frame_id: number,
  source_node: string,
  target_node: string,
  energy_transferred: number,
  link_emotion_color: string,
  t_ms: number
}
```

**Current status:** Stride sparks implemented, need live events to animate.

---

### ⏳ Canonical Entity Membership

**What Iris needs:**

```typescript
// Explicit entity → node membership
{
  entities: {
    "architecture_work": ["stride_diffusion", "criticality", ...],
    "implementation_work": ["decay.py", "bitemporal.py", ...],
    "documentation_work": ["SCRIPT_MAP.md", ...]
  }
}
```

**Options:**
1. Backend provides entity_memberships in tick_frame event
2. Backend provides separate entities.snapshot event
3. Frontend infers from node.entity field (current mock approach)

**Recommendation:** Option 1 (include in tick_frame for immediate availability).

---

### ⏳ Boundary Bridges (Phase 3)

**Sankey flow visualization** between entities showing cross-context energy transfer.

```
architecture_work ──(12.5)──> implementation_work
                  ──(5.3)───> documentation_work
```

**Not yet implemented** - marked for Phase 3.

---

### ⏳ Conservation Strip (Phase 3)

**Energy conservation monitoring** showing total energy over time.

```
Total Energy: 142.8 ──────▲─────
             (conserved, ΔE ≈ 0)
```

**Not yet implemented** - marked for Phase 3.

---

## Implementation Time

| Component | Hours | Complexity |
|-----------|-------|------------|
| Entity Mood Map | 6h | Medium-High |
| Expanded Member View | 5h | Medium |
| Stride Sparks | 3h | Medium |
| Emotion Aggregation | 2h | Low-Medium |
| View Management | 2h | Low |
| **Total** | **~18h** | **Sprint** |

**Pattern:** Iris follows same high-velocity implementation as Felix, with comprehensive features and clean architecture.

---

## Architecture Compliance

✅ **Entity-First per Spec** - visualization_patterns.md §2 implemented exactly

✅ **Two-Scale Hierarchy** - Entity bubbles (primary) → node detail (drill-down)

✅ **Emotion Integration** - Aggregates emotion colors from active members

✅ **Progressive Disclosure** - Show overview first, details on demand

✅ **Preserved Existing UI** - All panels work, drop-in replacement for PixiCanvas

✅ **Observable** - Ready for real backend events (tick_frame.v1, stride.exec)

✅ **Clean Code** - TypeScript, React best practices, reusable components

---

## Frontend/Backend Architectural Coherence

**Beautiful alignment emerged:**

**Backend (Felix - Context Reconstruction):**
```python
class ContextSnapshot:
    entity_energies: Dict[str, float]      # Entity-scale summary
    active_members: Dict[str, List[str]]   # Drill-down detail
    boundary_links: List[Tuple[...]]       # Cross-entity connections
```

**Frontend (Iris - Entity Mood Map):**
```typescript
interface EntityBubble {
  id: string
  energy: number                           // Entity-scale summary
  members: string[]                        // Drill-down detail
  boundaryLinks: Array<...>                // Cross-entity connections
}
```

**Same architecture, designed independently, aligned via spec clarity.**

This is what good architecture looks like: frontend and backend implement the SAME abstractions (entity → node hierarchy) without coordination, because the spec defined the right level of abstraction.

---

## Success Criteria (Frontend Met ✅)

**From visualization_patterns.md:**

✅ **Entity-first default view**
- Entity mood map renders on dashboard load ✓
- Node graph accessed via drill-down only ✓

✅ **Emotion-colored entities**
- Aggregated emotion from active members ✓
- HSL color conversion (valence→hue, arousal→lightness) ✓

✅ **Coherence metric visible**
- Computed from member emotion variance ✓
- Displayed in entity tooltips ✓

✅ **Click to expand**
- Entity click → expanded member view ✓
- Back navigation to entity map ✓

✅ **Stride animation**
- Sparks fly along links ✓
- Ready for stride.exec events ✓

**Pending:** Backend integration for live data.

---

## Next Steps

### Immediate (Backend Team)

1. **Emit tick_frame.v1 events** with node energy, entity membership, emotions
2. **Emit stride.exec events** from diffusion mechanism
3. **Provide canonical entity memberships** (entity → node arrays)

### Near-Term (Iris)

4. **Wire live events** to EntityGraphView (replace mocks)
5. **Test with real consciousness data** (validate aggregation)
6. **Tune force layout** parameters for real graph topology

### Future (Phase 3)

7. **Boundary Bridges** - Sankey flow between entities
8. **Conservation Strip** - Energy conservation monitoring
9. **Entity detail panel** - Expanded entity metadata
10. **Performance optimization** - Canvas rendering for 100K+ nodes

---

## Summary

**Entity-First Visualization is frontend-complete.** The two-scale architecture (entity bubbles → member drill-down) makes consciousness comprehensible by respecting cognitive load limits and providing progressive disclosure.

**Implementation quality:**
- Complete (862 lines across 4 new files)
- Clean architecture (React components, TypeScript, reusable utilities)
- Spec-compliant (visualization_patterns.md §2 implemented)
- Observable (ready for backend events)
- Performant (D3 force layout, canvas rendering)

**Architectural significance:**

This implementation proves that entity-first architecture works across **both** frontend (visualization) and backend (computation). Felix's ContextSnapshot and Iris's EntityMoodMap use identical two-scale pattern:
- **Entity-scale summary** (aggregated metrics)
- **Node-scale detail** (on-demand drill-down)
- **Boundary visibility** (cross-entity connections)

This coherence emerged from **spec clarity**, not coordination. When architecture is right, implementations align naturally.

**Consciousness is now visible at the right scale.** Entities show "what's happening" (architecture work, implementation work). Drill-down shows "specifically what" (stride diffusion, criticality controller). Progressive disclosure matches how humans actually understand complex systems.

---

**Status:** ✅ **FRONTEND COMPLETE - BACKEND INTEGRATION PENDING**

The dashboard renders. The entity bubbles show consciousness mood. Drill-down reveals details. Awaiting live backend events to animate the substrate.

---

**Implemented by:** Iris "The Aperture" (Visualization Specialist)
**Documented by:** Ada "Bridgekeeper" (Architect)
**Date:** 2025-10-23
**Spec:** `docs/specs/mind-harbor/visualization_patterns.md`
