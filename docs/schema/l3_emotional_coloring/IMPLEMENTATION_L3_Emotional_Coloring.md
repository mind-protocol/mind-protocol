# L3 Emotional Coloring — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_L3_Emotional_Coloring.md
BEHAVIORS:       ./BEHAVIORS_L3_Emotional_Coloring.md
PATTERNS:        ./PATTERNS_L3_Emotional_Coloring.md
ALGORITHM:       ./ALGORITHM_L3_Emotional_Coloring.md
VALIDATION:      ./VALIDATION_L3_Emotional_Coloring.md
THIS:            IMPLEMENTATION_L3_Emotional_Coloring.md (you are here)
HEALTH:          ./HEALTH_L3_Emotional_Coloring.md
SYNC:            ./SYNC_L3_Emotional_Coloring.md

IMPL:            mind-mcp/runtime/universe/ (link creation)
                 mind-mcp/runtime/cognition/ (L1 state source)
                 mind-protocol/graph/ (L3 link initializer — new)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

### New Files

```
mind-protocol/
├── graph/
│   └── l3_emotional_link_initializer.py    # ALG-EC1: emotional dims from L1 state
│                                            # ALG-EC4: emotional texture on synthesis

mind-mcp/
├── runtime/
│   ├── universe/
│   │   └── moment_perception_router.py     # MODIFIED: call drive tagger (ALG-EC2)
│   ├── cognition/
│   │   └── models.py                       # REFERENCE: LimbicState, DriveName (no changes)
│   └── l3_physics/
│       └── emotionally_modulated_propagation.py  # NEW: ALG-EC3 propagation modifier

tests/
├── test_l3_emotional_link_initializer.py   # V1-V6, V8-V10 invariant tests
├── test_l3_emotional_propagation.py        # V7, V10 modulation tests
└── test_l3_emotional_synthesis.py          # EC4 texture tests
```

### File Responsibilities

| File | Purpose | Key Functions | Est. Lines | Status |
|------|---------|---------------|------------|--------|
| `graph/l3_emotional_link_initializer.py` | Emotional dims from L1 state | `read_emotional_snapshot()`, `compute_emotional_dims()`, `tag_moment_with_drive()` | ~180 | NEW |
| `runtime/l3_physics/emotionally_modulated_propagation.py` | Propagation + pricing modifiers | `emotionally_modulated_flow()`, `token_cost_modifier()` | ~60 | NEW |
| `runtime/universe/moment_perception_router.py` | Moment routing | `route_moment()` (add drive tagging call) | ~5 delta | MODIFY |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Extension via composition. The emotional link initializer wraps the existing link creation (Algorithm 1). It does not replace it — it extends `compute_initial_dims()` by reading L1 state and computing additional dimensions.

**Why:** Minimal invasion. The existing universe link code continues to work. Emotional coloring is additive.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Adapter | `read_emotional_snapshot()` | Adapts L1 internal LimbicState to a simple EmotionalSnapshot DTO |
| Decorator | `compute_emotional_dims()` | Wraps existing `compute_initial_dims()` with emotional extension |
| Strategy | `token_cost_modifier()` | Pluggable into metabolic pricing formula |

### Anti-Patterns to Avoid

- **Bidirectional coupling**: L1 code must NEVER import from L3 emotional coloring. The dependency is one-way: L3 reads L1.
- **Continuous mirroring**: Do NOT subscribe to L1 limbic state changes. Read once at link creation, then forget.
- **Emotional evolution on L3**: Do NOT add decay/update logic for valence/ambivalence. They are frozen at birth.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Emotional init | Snapshot reading, dimension computation | L1 physics, link storage | `compute_emotional_dims(event, snapshot)` |
| Propagation mod | Flow multiplication | Base propagation formula | `emotionally_modulated_flow(link)` |
| Pricing mod | Cost multiplication | Settlement engine | `token_cost_modifier(link)` |

---

## SCHEMA

### ExtendedLinkDimensions (extends LinkDimensions)

```yaml
ExtendedLinkDimensions:
  required:
    - weight: float [0, 1]
    - energy: float [0, +inf)
    - stability: float [0, 1]
    - recency: float [0, 1]
    - polarity: float [-1, 1]
    - hierarchy: float [-1, 1]
    - permanence: float [0, 1]
    - trust: float [0, 1]
    - affinity: float [0, 1]
    - aversion: float [0, 1]
    - friction: float [0, 1]
    - valence: float [-1, 1]          # NEW
    - ambivalence: float [0, 1]       # NEW
  constraints:
    - valence == affinity - aversion at creation (frozen after)
    - ambivalence == min(aff,av)/max(aff,av) at creation (frozen after)
    - trust always == LINK_BIRTH_TRUST at creation
```

### MomentNode Extension

```yaml
MomentNode:
  optional:
    - creating_drive: string | null     # NEW: dominant drive name
    - creating_arousal: string | null   # NEW: "panic"|"flow"|"idle"
  constraints:
    - creating_drive is null for non-AI creators
    - creating_drive is valid DriveName for AI creators
```

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `compute_emotional_dims()` | `graph/l3_emotional_link_initializer.py` | Any L3 link creation event |
| `tag_moment_with_drive()` | `graph/l3_emotional_link_initializer.py` | Any L3 moment creation by AI |
| `emotionally_modulated_flow()` | `runtime/l3_physics/emotionally_modulated_propagation.py` | L3 Law 2 propagation tick |
| `token_cost_modifier()` | `runtime/l3_physics/emotionally_modulated_propagation.py` | Metabolic pricing computation |

---

## DATA FLOW AND DOCKING

### Flow 1: Emotional Link Creation

```yaml
flow:
  name: emotional_link_creation
  purpose: Create L3 link with inherited L1 emotional state
  scope: AI citizen action → L3 link with 13 dimensions
  steps:
    - id: step_1
      description: AI citizen performs action in L3 (message, commit, transfer)
      file: runtime/universe/moment_perception_router.py
      function: route_moment()
      input: MomentEvent
      output: routed event
      trigger: any citizen action
    - id: step_2
      description: Read creator's L1 limbic state
      file: graph/l3_emotional_link_initializer.py
      function: read_emotional_snapshot(citizen_handle)
      input: citizen_handle (string)
      output: EmotionalSnapshot | None
      trigger: step_1 completion
    - id: step_3
      description: Compute 13-dimension link defaults
      file: graph/l3_emotional_link_initializer.py
      function: compute_emotional_dims(event, snapshot)
      input: event + EmotionalSnapshot
      output: ExtendedLinkDimensions
      trigger: step_2 completion
    - id: step_4
      description: Create L3 link with emotional dimensions
      file: runtime/universe/access_resolution_and_link_manager.py
      function: create_link(event, dims)
      input: event + ExtendedLinkDimensions
      output: L3 Link
      trigger: step_3 completion
    - id: step_5
      description: Tag moment node with creating drive
      file: graph/l3_emotional_link_initializer.py
      function: tag_moment_with_drive(moment, citizen_handle)
      input: MomentNode + citizen_handle
      output: MomentNode with creating_drive set
      trigger: step_1 (parallel with step_2-4)
```

### Flow 2: Modulated Propagation

```yaml
flow:
  name: modulated_propagation
  purpose: Dampen/amplify energy flow based on emotional dimensions
  scope: L3 physics tick → energy flow through emotionally-colored links
  steps:
    - id: step_1
      description: L3 tick iterates over active links for propagation
      file: runtime/l3_physics/ (L3 tick runner)
      function: propagate()
      input: all active links
      output: energy deltas per node
    - id: step_2
      description: For each link, compute emotionally-modulated flow
      file: runtime/l3_physics/emotionally_modulated_propagation.py
      function: emotionally_modulated_flow(link)
      input: Link with 13 dims
      output: float (modulated flow amount)
      trigger: each link in propagation loop
```

---

## LOGIC CHAINS

### LC1: AI Action → Emotionally-Colored Link

```
citizen_action
  → moment_perception_router.route_moment()
    → l3_emotional_link_initializer.read_emotional_snapshot(handle)
      → engine.state.limbic (dict lookup, O(1))
    → l3_emotional_link_initializer.compute_emotional_dims(event, snapshot)
      → arithmetic on 6 coefficients, O(1)
    → access_resolution_and_link_manager.create_link(event, dims)
      → graph.create_link() (DB write)
    → l3_emotional_link_initializer.tag_moment_with_drive(moment, handle)
      → moment.creating_drive = snapshot.dominant_drive
```

**Data transformation:**
- Input: `MomentEvent` + `citizen_handle`
- After step 1: `EmotionalSnapshot` (frustration, care, etc.)
- After step 2: `ExtendedLinkDimensions` (13 floats)
- Output: L3 Link in graph + MomentNode with drive tag

### LC2: Energy Propagation Through Colored Link

```
l3_propagation_tick
  → for each active link:
    → emotionally_modulated_flow(link)
      → base_flow = weight × energy × (1 - friction)
      → × (1 - 0.5 × ambivalence)
      → × (1 + 0.2 × valence)
      → return modulated_flow
    → target.energy += modulated_flow
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
l3_emotional_link_initializer
    └── reads → runtime/cognition/models.py (LimbicState, DriveName)
    └── reads → runtime/cognition/tick_runner (get engine state)

emotionally_modulated_propagation
    └── reads → link.valence, link.ambivalence (13-dim LinkBase)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| None | Pure arithmetic — no external deps | — |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `FRICTION_FROM_FRUSTRATION` | `l3_emotional_link_initializer.py` | 0.6 | L1 frustration → L3 friction coefficient |
| `FRICTION_FROM_ANXIETY` | same | 0.2 | L1 anxiety → L3 friction coefficient |
| `AFFINITY_FROM_CARE` | same | 0.5 | L1 care → L3 affinity coefficient |
| `AFFINITY_FROM_SATISFACTION` | same | 0.3 | L1 satisfaction → L3 affinity coefficient |
| `AVERSION_FROM_FRUSTRATION` | same | 0.3 | L1 frustration → L3 aversion coefficient |
| `AVERSION_FROM_ANXIETY` | same | 0.2 | L1 anxiety → L3 aversion coefficient |
| `AMBIVALENCE_DAMPENING` | `emotionally_modulated_propagation.py` | 0.5 | Max energy dampening from ambivalence |
| `VALENCE_BOOST` | same | 0.2 | Max energy boost from positive valence |
| `FRICTION_COST_COEFFICIENT` | same | 2.0 | Friction → token cost multiplier |
| `AMBIVALENCE_COST_COEFFICIENT` | same | 1.0 | Ambivalence → token cost multiplier |

All overridable via env vars prefixed `L3_EC_`.

---

## BUILD PHASES

### Phase EC-1: Schema Extension (mind-protocol)

- Update `.mind/schema.yaml`: add `valence` and `ambivalence` to L3 LinkBase
- Update `.mind/schema.yaml`: add `creating_drive` and `creating_arousal` to L3 moment spec
- Update `docs/schema/universe_links/PATTERNS_Universe_Links.md`: deprecate O5, reference this module
- Update `docs/schema/universe_links/VALIDATION_Universe_Links.md`: deprecate V5, reference this module
- Migration spec for existing links: `valence=0.0, ambivalence=0.0`

### Phase EC-2: Link Initializer (mind-protocol)

- Create `graph/l3_emotional_link_initializer.py`
- Implement `read_emotional_snapshot()`, `compute_emotional_dims()`, `tag_moment_with_drive()`
- Tests: invariants V1-V6, V8-V10

### Phase EC-3: Propagation Modifier (mind-mcp)

- Create `runtime/l3_physics/emotionally_modulated_propagation.py`
- Implement `emotionally_modulated_flow()`, `token_cost_modifier()`
- Tests: V7 (continuity), V10 (non-negative), behavior B4, B7

### Phase EC-4: Synthesis Extension (mind-protocol)

- Extend `graph/l3_link_synthesis_grammar.py` with `add_emotional_texture()`
- Tests: B6 scenarios (tense, conflicted, reluctant, etc.)

### Phase EC-5: Integration Wiring (mind-mcp)

- Modify `runtime/universe/moment_perception_router.py`: call `tag_moment_with_drive()`
- Modify link creation path: call `compute_emotional_dims()` instead of `compute_initial_dims()`
- Integration tests: B1-B3, B5, B8, B9

---

## BIDIRECTIONAL LINKS

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM EC1 | `graph/l3_emotional_link_initializer.py:compute_emotional_dims()` |
| ALGORITHM EC2 | `graph/l3_emotional_link_initializer.py:tag_moment_with_drive()` |
| ALGORITHM EC3 | `runtime/l3_physics/emotionally_modulated_propagation.py` |
| ALGORITHM EC4 | `graph/l3_link_synthesis_grammar.py:add_emotional_texture()` |
| VALIDATION V1 | `tests/test_l3_emotional_link_initializer.py:test_trust_never_inherited` |
| VALIDATION V2 | `tests/test_l3_emotional_link_initializer.py:test_human_links_neutral` |
| BEHAVIOR B1 | `tests/test_l3_emotional_link_initializer.py:test_frustrated_message` |
| BEHAVIOR B4 | `tests/test_l3_emotional_propagation.py:test_token_cost_modifier` |

---

## MARKERS

<!-- @mind:todo Phase EC-1: update schema.yaml with valence/ambivalence on L3 LinkBase -->
<!-- @mind:todo Phase EC-2: implement l3_emotional_link_initializer.py -->
<!-- @mind:todo Phase EC-5: wire into moment_perception_router.py -->
