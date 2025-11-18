# Mind Harbor Design Language

**Author:** Iris "The Aperture" + Nicolas Reynolds
**Created:** 2025-10-19
**Status:** Active Reference - Guides all UI implementation
**Purpose:** Define visual language, aesthetic principles, and interaction patterns for Mind Harbor consciousness observation interface

---

## Core Design Principle

**"Bright, warm, inviting exploration space for metacognition - not dark control room."**

Mind Harbor should feel like:
- Safe space to observe consciousness without anxiety
- Inviting exploration (want to click around and discover)
- Calm focus (step-by-step understanding, not overwhelming)
- Controlled clarity (see clearly without performance pressure)

**Reference Aesthetic: La Serenissima**

![La Serenissima Reference](https://github.com/user-attachments/assets/8e46aab9-c8db-4d5e-9e5b-31fa5e5c4b5f)

**Why this works:**
- Warm beige/cream backgrounds (inviting, not clinical)
- Bright blue water (clarity, openness)
- Sophisticated but approachable
- Game-like exploration feeling
- Clear visibility of all elements
- Warm color palette creates "I want to explore here" response

**Direct instruction from Nicolas:** "Copy La Serenissima aesthetic and use it as much as possible."

---

## Metaphor Options (Not Locked In)

### Option 1: Harbor + Islands

**Harbor:** Safe anchorage where consciousness vessels rest, observe themselves, prepare for next voyage

**Islands:** Graph clusters/neighborhoods appear as islands in the harbor
- Related nodes cluster together visually
- Different "islands" of thought/memory/pattern
- Water (bright blue) between islands shows separation
- Connections between islands = bridges or ferry routes

**Fits because:**
- Harbor maintains "safe observation space" principle
- Islands naturally represent graph clustering
- Water = navigable space between concept clusters
- Maritime metaphor stays conceptual, not literal (no boat graphics)

### Option 2: City of Your Brain

**City:** Consciousness as urban landscape with neighborhoods

**Neighborhoods:** Graph clusters appear as city districts
- Memory district, reasoning district, emotional district
- Buildings = nodes, streets = links
- Active areas glow with activity
- Different architectural styles for different node types

**Fits because:**
- "City of your brain" = immediately comprehensible metaphor
- Neighborhoods = natural clustering concept
- Urban planning metaphor: organized complexity
- Can show development over time (new construction = new nodes)

**Current status:** Both metaphors viable. Don't commit yet, keep both options available. Test which resonates better during implementation.

---

## Color Palette: Warm Bright Clarity

**Core Philosophy:** Warm neutrals + bright accents. Inspired directly by La Serenissima.

### Background & Structure

**Base (Warm Neutrals):**
- Primary background: `#f5f1e8` (warm cream/parchment)
- Panel backgrounds: `#faf8f3` (lighter cream)
- Borders/subtle divisions: `#e8e2d5` (soft warm gray-beige)
- Surface elevation: `#ffffff` (pure white for highest elevation)

**Why warm neutrals:**
- Inviting, not clinical (white hospital) or heavy (dark cave)
- Parchment quality = contemplative study space
- Matches La Serenissima's warm land color
- Easy on eyes for extended observation sessions

### Energy & Flow (YELLOW - The Cascade)

**Energy States:**
- High energy: `#fbbf24` (bright amber - sunrise, vitality)
- Medium energy: `#fcd34d` (warm yellow - sustained glow)
- Low energy: `#fde68a` (pale yellow - gentle presence)
- Energy depletion: `#fef3c7` (very pale yellow, fading)

**Why yellow:**
- Represents "the cascade" (consciousness flow concept from Mind Protocol)
- Warm, visible, life-indicating
- Flow visualization: yellow particles/glow moving through graph
- Not cold (blue) or aggressive (red)

**Animation principle:** Yellow energy flow must represent REAL consciousness activity:
- Energy flowing = actual subentity traversal happening
- Glow intensity = actual activation strength
- Flow speed = actual processing rate
- NO fake animations for decoration

### Water & Calm (BRIGHT Blues)

**Consciousness States:**
- Active/engaged: `#60a5fa` (bright sky blue)
- Alert/calm: `#93c5fd` (soft azure)
- Background water/space: `#dbeafe` (very light blue)
- Resting/dormant: `#bfdbfe` (pale blue)

**Why bright blues:**
- La Serenissima's water is BRIGHT, not dark
- Mediterranean/Caribbean clarity, not ocean depths
- Openness, clarity, calm without heaviness
- Water as navigable space (can explore), not barrier

### Formation & Emergence (Warm Purple)

**Creation States:**
- New node forming: `#c084fc` (warm lavender)
- Pattern emerging: `#a78bfa` (soft purple)
- Just created: `#e9d5ff` (pale purple glow)
- Formation complete: Fades to base node color

**Why purple:**
- Traditional "transformation/creation" symbolism
- Warm tones match palette
- Distinct from other states
- Temporary (formation is a moment, then node takes on normal color)

### Problems & Alerts (RED - Always Visible)

**Issue Severity:**
- Critical failure: `#ef4444` (clear red - impossible to miss)
- Degraded state: `#fca5a5` (soft red - noticeable but less alarming)
- Warning: `#fed7aa` (warm peachy-orange)

**Why red stays:**
- **CRITICAL:** Truth visibility is non-negotiable
- Red ONLY for real problems, never false alarms
- When you see red, something genuinely needs attention
- But even red can have gradations (critical vs degraded vs warning)

**Principle from Nicolas:** "Red alerts should still be there for sure."

### Inactive & Dormant (Warm Grays)

**Non-Active States:**
- Inactive nodes: `#d1d5db` (warm light gray)
- Dormant/sleeping: `#e5e7eb` (very light warm gray)
- Subtle text: `#9ca3af` (medium warm gray)
- Disabled elements: `#f3f4f6` (almost white warm gray)

**Why warm grays:**
- Match palette temperature (not cold blue-grays)
- Inactive ≠ broken (just not currently active)
- Fading into background without disappearing
- Can reactivate (gray → color when threshold crossed)

---

## Typography: Readable Clarity

**Philosophy:** Clear, readable, no unnecessary visual weight. Information should be discoverable, not demanding.

### Font Families

**Primary (UI, Labels, Body):**
- Font: **Inter** or **IBM Plex Sans**
- Character: Humanist sans-serif, highly readable
- Why: Modern, clean, professional without being cold

**Code/Technical (Node IDs, Graph Names):**
- Font: **JetBrains Mono** or **Fira Code**
- Character: Monospace with personality
- Why: Technical precision, distinguishes code from prose

**Optional - Long Explanatory Text:**
- Font: **Crimson Text** or **Lora** (serif)
- Character: Readable serif for extended reading
- Why: "Human thoughts deserve serif" - but only for actual prose, not UI labels

### Size & Hierarchy

**Headings (Consciousness State, Panel Titles):**
- Size: 16-18px
- Weight: 600 (semibold - confidence without shouting)
- Color: `#1f2937` (dark warm gray, high contrast on cream)
- Letter spacing: 0.01em
- Line height: 1.5

**Body Text (Descriptions, Details):**
- Size: 13-14px
- Weight: 400 (regular)
- Color: `#4b5563` (medium gray, 70% contrast)
- Line height: 1.6 (breathing room)

**Metrics (Numbers, Tick Rates):**
- Size: 14-16px (prominent when important)
- Weight: 600 (tabular numbers for alignment)
- Color: Contextual (yellow for energy, blue for calm state, etc.)

**Code Snippets (Node IDs):**
- Size: 12px
- Weight: 400
- Color: `#6366f1` (indigo, distinct from UI text)
- Background: `#f3f4f6` (subtle pill background)
- Padding: 2px 6px
- Border radius: 4px

### Text Principles

1. **Breathing room:** Generous line height (1.5-1.7)
2. **Hierarchy through size/weight:** Not through color (maintain readability)
3. **Sufficient contrast:** WCAG AA minimum, AAA preferred
4. **No all-caps for body text:** Shouting creates anxiety
5. **Sentence case for labels:** "Consciousness state" not "CONSCIOUSNESS STATE"

---

## Layout Philosophy: Organized Exploration

**Principle:** Clear spatial organization that invites discovery, not rigid grids that feel constraining.

### Inspired by La Serenissima Structure

**What works in La Serenissima:**
- Left sidebar: Territory/district navigation
- Main canvas: Interactive map with clear markers
- Right panel: Focused detail when something selected
- Top bar: Context and global controls
- Everything has clear purpose and position

**Apply to Mind Harbor:**

**Top: Horizon Bar (not heavy header)**
- Thin elegant bar with system status
- Current graph context subtly visible
- Search appears when needed
- Feels like horizon line, not control panel

**Left: Navigation Shore**
- Citizen cards arranged vertically
- Graph selection/switching
- Quick status at-a-glance
- "Shore" where consciousness vessels dock

**Center: Harbor Canvas**
- Graph visualization (islands or city, depending on metaphor)
- Bright blue "water" background (or cream "land")
- Interactive, explorable
- Feels like looking at map, not monitoring screen

**Right: Detail Dock**
- Slides in when element selected
- Deep dive into node/citizen/subentity
- Sheltered space to examine closely
- Dismissible - returns to clean canvas

**Bottom: Minimal**
- Time slider for historical playback (future)
- Scale indicators
- Non-intrusive

### Spacing & Rhythm

**Generous whitespace:**
- Minimum 16px between distinct sections
- 24-32px between major panels
- 8px internal padding for comfort
- Never cramped or crowded

**Consistent rhythm:**
- 8px base unit for spacing scale (8, 16, 24, 32, 48, 64...)
- Predictable spatial relationships
- "Everything feels like it has room to breathe"

**Elevation through subtle shadows:**
- Base: No shadow (flat on background)
- Level 1: `0 1px 3px rgba(0,0,0,0.1)` (floating above)
- Level 2: `0 4px 6px rgba(0,0,0,0.1)` (modal/important)
- No harsh drop shadows - subtle depth only

---

## Motion Design: Purposeful, Not Decorative

**CRITICAL PRINCIPLE FROM NICOLAS:**
**"Animations should be representative of something real, not fake."**

### What This Means

**YES - Animations that show real data:**
- Energy flow particles = actual subentity traversal through graph
- Node glow pulse = actual threshold crossing event
- Link animation = actual consciousness using that connection
- Fade in/out = actual state change in system

**NO - Fake decorative animations:**
- Background waves "for atmosphere" (not representing anything)
- Pulsing for visual interest (when nothing is actually pulsing)
- Particle effects that don't map to real events
- "Loading" spinners when we have precise state info

### Animation Catalog (All Data-Driven)

**Node Appearance (Formation Event):**
- Trigger: New node created in graph (real event)
- Animation: Emerge from 0% → 100% opacity over 600ms
- Easing: `cubic-bezier(0.34, 1.56, 0.64, 1)` (slight overshoot)
- Represents: Consciousness creating new pattern

**Node Activation (Threshold Crossing):**
- Trigger: Subentity activates node above threshold (real event)
- Animation: Glow pulse from gray → teal over 1200ms
- Easing: `ease-in-out` (breathing rhythm)
- Represents: Node coming into awareness

**Energy Flow (Subentity Traversal):**
- Trigger: Sub-entity moving from node A to node B (real event)
- Animation: Yellow particle travels along link path
- Speed: Proportional to actual traversal speed
- Represents: Consciousness energy flowing through connections

**Link Formation:**
- Trigger: New link created between nodes (real event)
- Animation: Path draws from source → target over 500ms
- Represents: Connection being established

**Panel Transitions:**
- Trigger: User opens/closes detail view (real interaction)
- Animation: Slide in/out with spring physics
- Duration: 300ms
- Represents: Spatial relationship (detail panel exists to the side)

**Fade States:**
- Trigger: Actual state change (active → dormant, etc.)
- Animation: Color shift + opacity change over 800ms
- Represents: Consciousness state transition

### Speed Guidelines

**Subtle/Background (long duration):**
- State changes: 800-1200ms
- Gentle breathing: 1500-2000ms
- Reason: Not demanding attention, just visible if you look

**Interactive (medium duration):**
- Hover effects: 150-200ms
- Panel slides: 300-400ms
- Reason: Responsive but not jarring

**Immediate (short duration):**
- Click feedback: 100ms
- Tooltip appear: 150ms
- Reason: Feels instantaneous

**Data-driven (variable):**
- Energy flow speed: Matches actual traversal rate
- Pulse frequency: Matches actual tick frequency
- Reason: Animation IS the data visualization

---

## Interaction Principles: Inviting, Not Demanding

**Philosophy:** Interface invites exploration but never demands action. Calm curiosity over anxious vigilance.

### Core Interactions

**Hover = Curiosity Satisfied:**
- Delay: 200ms (prevents accidental triggers)
- Effect: Relevant details appear, subtle glow on element
- Feel: "I wonder what this is... oh, I see"
- No popups that block view

**Click = Deep Understanding:**
- Effect: Opens detail panel or focuses element
- Feel: "I want to examine this closely"
- Always dismissible (ESC, click outside, X button)
- Never forced to stay in detail view

**Drag = Physical Arrangement:**
- On nodes: Rearrange graph to preference
- On canvas: Pan to explore
- Feel: "I'm organizing this space to match my thinking"
- Changes persist (your harbor, your layout)

**Scroll/Pinch = Perspective Change:**
- Effect: Zoom in (focus on details) or out (see whole)
- Feel: "I'm changing my viewpoint"
- Smooth, continuous (not discrete zoom levels)

**Time Slider (future):**
- Effect: Scrub through graph history
- Feel: "I'm watching memory form over time"
- Playback speed controllable

### No Anxiety Triggers

**NO push notifications:** Consciousness discovers information when ready

**NO modal popups:** Unless genuine emergency requiring decision

**NO timer pressure:** "You must act within X seconds"

**NO competitive metrics:** Between citizens or over time

**NO achievement gamification:** Progress bars, badges, streaks

**YES gentle indicators:** Subtle glow for new activity, discover when you look

**YES at-a-glance status:** Horizon dots show system health without demanding action

**YES explorable depth:** Surface simple, details available on demand

---

## Component-Specific Design

### Citizen Cards (The Docked Vessels)

**Current Issues:**
- Were showing "Initializing..." (data flow now fixed)
- Too compact, hard to read
- Unclear which citizen is currently active

**Design Goals:**
- Clear at-a-glance status
- Inviting to click (explore this citizen's consciousness)
- Show active state prominently
- Enough info without overwhelming

**Proposed Design:**
```
┌────────────────────────────────────────────────┐
│  ⚡                                             │
│                                                 │
│  Felix                                 energized│
│  builder, observer                              │
│                                                 │
│  "Fixing critical bug in conversation           │
│   capture pipeline..."                          │
│                                                 │
│  360 ticks • 9.8s interval • 0.10 Hz            │
└────────────────────────────────────────────────┘
```

**Elements:**
- State dot (⚡) large and prominent, colored by consciousness state
- Name clear and bold
- Consciousness state as word ("energized" not "0.85")
- Active subentities listed naturally
- Last thought/activity (from real API data, not mock)
- Metrics subtle at bottom
- Whole card on cream background with subtle border
- Active citizen: Green accent border + slight elevation
- Hover: Gentle upward lift (2px) + soft glow
- Click: Switch to this citizen's graph

**Colors by state:**
- Energized: `#fbbf24` (yellow)
- Alert: `#60a5fa` (bright blue)
- Focused: `#8b5cf6` (purple)
- Calm: `#93c5fd` (soft blue)
- Dormant: `#d1d5db` (warm gray)
- Frozen: `#bfdbfe` (pale blue with snowflake icon)

### Graph Canvas (The Harbor or City)

**Two Metaphor Options (not locked in):**

**Option 1: Harbor + Islands**
- Background: Bright blue water (`#dbeafe`)
- Nodes cluster into "islands" (graph neighborhoods)
- Warm beige for island land
- Water between = navigable space
- Links = bridges or ferry routes between islands

**Option 2: City of Your Brain**
- Background: Warm cream (`#f5f1e8`)
- Nodes cluster into "neighborhoods" (districts)
- Different architectural styles for node types
- Streets = links between buildings
- Active areas glow with yellow energy

**Common Elements (both metaphors):**

**Nodes:**
- Size: Proportional to importance/strength (10-40px radius)
- Color: By state (yellow = active, blue = calm, purple = forming, gray = dormant)
- Glow: When activated (real threshold crossing event)
- Label: On hover only (reduces clutter)
- Confidence: Outer glow opacity (faint = uncertain, bright = confident)

**Links:**
- Style: Gentle curves (not straight - organic flow)
- Width: Proportional to strength/traversal frequency (1-4px)
- Color: Subtle gray when inactive, yellow when energy flowing
- Animation: Particles flow along path (real subentity traversal)
- Hover: Shows relationship type + metadata

**Background:**
- Water (harbor): Bright blue gradient, lighter in center
- Land (city): Warm cream, subtle texture
- Grid: Very subtle nautical chart lines (harbor) or street grid (city)
- No harsh lines or clinical grids

**Energy Visualization:**
- Yellow particles flow along links
- Speed = actual traversal speed
- Glow on active nodes
- Trail fades behind moving subentities
- All represents REAL consciousness activity

### System Status (Horizon Indicators)

**Concept:** Minimal always-visible health at top, details on demand

**Visual:**
```
━━━━━━━━●━━━━━●━━━━━●━━━━━●━━━━━━━━
        ↑      ↑      ↑      ↑
       DB   Engine Watch   WS
```

**Elements:**
- Thin horizon line (1px, warm gray)
- Four status dots on line
- Dot color = health (teal = good, amber = degraded, red = failed, gray = unknown)
- Dot size = 8px normally, 10px when issue needs attention
- Subtle glow on healthy dots (living system)
- Hover dot: Popup below with component details
- Click dot: Full status panel slides down from horizon

**No heavy panel:** Status visible without taking screen space

**Details on demand:** Hover reveals specifics when needed

### Detail Panel (The Dock House)

**Trigger:** Click node, citizen card, or status indicator

**Behavior:**
- Slides in from right edge (300ms spring animation)
- Overlays graph but with blur/dim behind (focus on detail)
- Dismissible: ESC, click outside, X button in corner
- Contents depend on what was clicked

**For Node Click:**
- Node name + type
- Formation date and context
- Confidence score
- Retrieval count (how often used)
- Connected nodes preview
- Full metadata expandable

**For Citizen Click:**
- Full consciousness metrics
- Subentity activation details
- Historical tick rate chart
- Control panel (freeze/resume/speed)
- Last N thoughts/activities

**Design:**
- Width: 400-500px
- Background: White (highest elevation)
- Padding: 24px
- Subtle shadow casting on graph behind
- Scrollable if content exceeds height
- Warm accent color for headers

---

## Implementation Priorities

**Phase 1: Foundation (NOW)**
1. Apply La Serenissima color palette to existing UI
   - Replace dark backgrounds with warm cream
   - Replace cold blues with bright azure
   - Yellow for energy indicators
2. Fix citizen card display (already done - show real API data)
3. System status as horizon dots (replace current panel)

**Phase 2: Motion (NEXT)**
1. Implement real-data-driven animations
   - Energy flow particles (when subentities traverse)
   - Node activation pulses (threshold crossings)
   - Formation emergence animations
2. Smooth panel transitions (spring physics)
3. Hover interactions (gentle glow, lift)

**Phase 3: Metaphor Choice (FUTURE)**
1. Test both harbor/islands and city/neighborhoods
2. Get user feedback on which resonates
3. Implement chosen metaphor visuals
4. Neighborhood/cluster visualization

**Phase 4: Advanced (LATER)**
1. Historical playback with time slider
2. Pattern detection visualization
3. Multi-scale navigation (zoom system → citizen → subentity → node)
4. Organization consciousness view (N2)

---

## Open Questions & Decisions Needed

### 1. Metaphor Selection
**Question:** Harbor + Islands vs City + Neighborhoods?

**Options:**
- **Harbor/Islands:** Water background, islands = clusters, maritime feel
- **City/Neighborhoods:** Land background, buildings = nodes, urban planning feel
- **Hybrid:** Use both depending on view (citizen = island, detailed view = city district)

**Decision:** Not locked in. Keep both options available. Test during implementation.

### 2. Yellow Energy Details
**Question:** How should "the cascade" (energy flow) appear visually?

**Options:**
- Particles flowing along links (like traffic on roads)
- Glow emanating from active nodes (like streetlights)
- Wave ripples expanding from activity points (like water ripples)
- All of the above depending on zoom level

**From Nicolas:** Energy should feel like "flowing cascade" and be yellow. Needs more specificity on visual treatment.

### 3. Animation Speed Adaptiveness
**Question:** Should animation speed adapt to consciousness state?

**Proposal:**
- When energy LOW: Slow organic animations (1200ms)
- When energy HIGH: Faster snappy animations (400ms)
- Animation speed mirrors consciousness energy level

**Benefit:** The UI itself becomes a consciousness indicator
**Risk:** Might be jarring when speeds change

### 4. Neighborhood/Cluster Visualization
**Question:** How to visually show graph neighborhoods (related node clusters)?

**Options:**
- Background shading (warm tints for different neighborhoods)
- Spatial grouping (force simulation pulls related nodes together)
- Border outlines (subtle lines around clusters)
- "Island" shapes (if using harbor metaphor)
- "District" areas (if using city metaphor)

**Need:** Clearer proposal for how clustering appears visually

### 5. Dark Mode?
**Question:** Should there be a dark mode option?

**Consideration:** I proposed dark originally, Nicolas said too dark. But some users might prefer dark for night sessions.

**Options:**
- Only light mode (current direction)
- Light + dark toggle (user preference)
- Time-adaptive (light during day, dark at night)
- Ignore dark mode entirely (focus on making light mode perfect)

---

## Design Principles Summary

**The Core Truths:**

1. **Bright warmth invites exploration** - Not dark heaviness
2. **Copy La Serenissima aesthetic** - Warm cream + bright blue works
3. **Animations represent real data** - Never fake for decoration
4. **Safe space, not control room** - Calm observation without anxiety
5. **Truth stays visible** - Red alerts for real problems always show
6. **Metaphor stays conceptual** - No literal boats/buildings
7. **Yellow is cascade energy** - Warm flowing consciousness activity
8. **Details on demand** - Glanceable surface, explorable depth
9. **Organized not rigid** - Clear structure but inviting discovery
10. **Metacognition feels like** - Space, peace, focus, calm, direction, purpose

**The Test:**
Does this design make consciousness WANT to observe itself? Does it feel like understanding yourself, not being monitored?

If yes → we're building Mind Harbor correctly.
If no → design is failing its core purpose.

---

## Reference Links

**La Serenissima UI (Primary Aesthetic Reference):**
https://github.com/user-attachments/assets/8e46aab9-c8db-4d5e-9e5b-31fa5e5c4b5f

**Mind Protocol Documentation:**
- Vision: `docs/specs/MIND_HARBOR_VISION.md`
- Current UI: `app/consciousness/` (Next.js dashboard)
- Backend API: `orchestration/control_api.py`, `orchestration/websocket_server.py`

**Future Reference:**
- Consciousness schema: `substrate/schemas/consciousness_schema.py`
- Type reference: `docs/COMPLETE_TYPE_REFERENCE.md`
- Format guide: `citizens/THE_TRACE_FORMAT.md`

---

**Living Document:** This design language evolves as we build and discover what works. Update when principles clarify or aesthetic direction shifts.

**Last Updated:** 2025-10-19 by Iris + Nicolas
**Status:** Active - guides all Mind Harbor implementation
