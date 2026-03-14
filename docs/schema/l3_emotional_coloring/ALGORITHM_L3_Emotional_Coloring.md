# L3 Emotional Coloring — Algorithm: Inheritance, Modulation, and Synthesis

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: pending
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_L3_Emotional_Coloring.md
PATTERNS:        ./PATTERNS_L3_Emotional_Coloring.md
THIS:            ALGORITHM_L3_Emotional_Coloring.md (you are here)
VALIDATION:      ./VALIDATION_L3_Emotional_Coloring.md
IMPLEMENTATION:  ./IMPLEMENTATION_L3_Emotional_Coloring.md
SYNC:            ./SYNC_L3_Emotional_Coloring.md

EXTENDS:         ../universe_links/ALGORITHM_Universe_Links.md (Algorithm 1: Link Creation)
IMPL:            (not yet implemented)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

This document specifies four algorithms that extend the existing L3 link lifecycle with emotional coloring:

1. **Emotional Link Initialization** — extends Algorithm 1 (Link Creation) to inherit L1 limbic state
2. **Moment Drive Tagging** — tags L3 moment nodes with the creating drive
3. **Emotionally-Modulated Propagation** — extends Law 2 propagation with valence/ambivalence dampening
4. **Emotionally-Textured Synthesis** — extends Algorithm 6 (Link Name Derivation) with emotional vocabulary

All algorithms operate within the existing L3 physics framework. They add 2 dimensions (valence, ambivalence) to LinkBase and 1 field (creating_drive) to moment nodes.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Algorithm | Why This Algorithm Matters |
|-----------|-----------|----------------------------|
| O1: Inherit creator's emotional state | ALG-EC1 | Links born colored, not blank |
| O2: Add valence/ambivalence to L3 | ALG-EC1 | Derived dimensions for structural tension |
| O3: Tag moments with creating drive | ALG-EC2 | Intent telemetry on events |
| O4: Modulate token/trust flow | ALG-EC3 | High friction = expensive; ambivalence dampens propagation |
| O5: Emotional texture in synthesis | ALG-EC4 | Human-readable labels reflect emotional quality |

---

## DATA STRUCTURES

### ExtendedLinkDimensions (13 dimensions — extends LinkDimensions from universe_links)

```
ExtendedLinkDimensions:
    # Original 11 dimensions (unchanged)
    weight:      float [0, 1]
    energy:      float [0, +inf)
    stability:   float [0, 1]
    recency:     float [0, 1]
    polarity:    float [-1, 1]
    hierarchy:   float [-1, 1]
    permanence:  float [0, 1]
    trust:       float [0, 1]
    affinity:    float [0, 1]
    aversion:    float [0, 1]
    friction:    float [0, 1]

    # NEW: 2 derived emotional dimensions
    valence:     float [-1, 1]    # net emotional charge (affinity - aversion)
    ambivalence: float [0, 1]     # conflicting signals: min(aff, av) / max(aff, av)
```

### EmotionalSnapshot (read from L1 at link creation time)

```
EmotionalSnapshot:
    # From L1 LimbicState.drives
    frustration:    float [0, 1]
    care:           float [0, 1]
    achievement:    float [0, 1]
    self_preservation: float [0, 1]
    curiosity:      float [0, 1]

    # From L1 LimbicState.emotions
    satisfaction:   float [0, 1]
    anxiety:        float [0, 1]
    boredom:        float [0, 1]

    # Derived
    dominant_drive: string         # name of highest-intensity drive
    arousal_regime: string         # "panic" | "flow" | "idle"
```

### MomentNode (extended with creating_drive)

```
MomentNode:
    # Existing fields (unchanged)
    id:            string
    node_type:     "moment"
    content:       string
    synthesis:     string
    ...

    # NEW
    creating_drive:  string | null   # dominant drive name, null for human-created
    creating_arousal: string | null  # "panic" | "flow" | "idle", null for human
```

---

## ALGORITHM EC1: Emotional Link Initialization

**Extends:** Algorithm 1 (Link Creation) from universe_links.

**When:** An AI citizen creates an L3 link (sends message, commits code, transfers tokens, joins space).

**Replaces:** `compute_initial_dims()` in Algorithm 1, Step 2.

### Step 1: Read Creator's L1 State

```python
def read_emotional_snapshot(citizen_handle: str) -> EmotionalSnapshot | None:
    """Read the creating citizen's current L1 limbic state.

    Returns None for human actors (no L1 engine).
    """
    engine = get_citizen_engine(citizen_handle)
    if engine is None:
        return None  # human actor or unknown — neutral defaults

    limbic = engine.state.limbic
    drives = limbic.drives

    # Find dominant drive
    drive_intensities = {name: d.intensity for name, d in drives.items()}
    dominant = max(drive_intensities, key=drive_intensities.get)

    return EmotionalSnapshot(
        frustration=drives["frustration"].intensity,
        care=drives["care"].intensity,
        achievement=drives["achievement"].intensity,
        self_preservation=drives["self_preservation"].intensity,
        curiosity=drives["curiosity"].intensity,
        satisfaction=limbic.emotions.get("satisfaction", 0.0),
        anxiety=limbic.emotions.get("anxiety", 0.0),
        boredom=limbic.emotions.get("boredom", 0.0),
        dominant_drive=dominant,
        arousal_regime=limbic.arousal_regime,
    )
```

### Step 2: Compute Emotionally-Colored Defaults

```python
# ── Inheritance coefficients ──
# How much L1 state bleeds into L3 link dimensions
FRICTION_FROM_FRUSTRATION = 0.6    # frustration → friction
FRICTION_FROM_ANXIETY = 0.2        # anxiety → friction (secondary)
AFFINITY_FROM_CARE = 0.5           # care → affinity
AFFINITY_FROM_SATISFACTION = 0.3   # satisfaction → affinity (secondary)
AVERSION_FROM_FRUSTRATION = 0.3    # frustration → aversion
AVERSION_FROM_ANXIETY = 0.2        # anxiety → aversion (secondary)

def compute_emotional_dims(event, snapshot: EmotionalSnapshot | None) -> ExtendedLinkDimensions:
    """Compute link dimensions with emotional coloring from L1 state.

    If snapshot is None (human actor), returns neutral defaults.
    """
    # Start with existing context-informed defaults
    polarity   = infer_polarity(event)
    hierarchy  = infer_hierarchy(event)
    permanence = infer_permanence(event)

    if snapshot is None:
        # Human actor — neutral emotional dimensions
        affinity    = 0.0
        aversion    = 0.0
        friction    = 0.0
    else:
        # AI actor — inherit from L1 limbic state
        affinity = clamp(
            snapshot.care * AFFINITY_FROM_CARE
            + snapshot.satisfaction * AFFINITY_FROM_SATISFACTION,
            0.0, 1.0,
        )
        aversion = clamp(
            snapshot.frustration * AVERSION_FROM_FRUSTRATION
            + snapshot.anxiety * AVERSION_FROM_ANXIETY,
            0.0, 1.0,
        )
        friction = clamp(
            snapshot.frustration * FRICTION_FROM_FRUSTRATION
            + snapshot.anxiety * FRICTION_FROM_ANXIETY,
            0.0, 1.0,
        )

    # Derived dimensions (computed, not inherited)
    if max(affinity, aversion) > 0.01:
        valence     = affinity - aversion
        ambivalence = min(affinity, aversion) / max(affinity, aversion)
    else:
        valence     = 0.0
        ambivalence = 0.0

    return ExtendedLinkDimensions(
        weight      = LINK_BIRTH_WEIGHT,        # 0.1 — earned, not inherited
        energy      = event.energy_budget,
        stability   = 0.0,
        recency     = 1.0,
        polarity    = polarity,
        hierarchy   = hierarchy,
        permanence  = permanence,
        trust       = LINK_BIRTH_TRUST,          # 0.1 — earned, NEVER inherited
        affinity    = affinity,
        aversion    = aversion,
        friction    = friction,
        valence     = valence,                   # NEW
        ambivalence = ambivalence,               # NEW
    )
```

### Step 3: Create Link (unchanged from Algorithm 1, Step 3)

The link creation, duplicate check, and indexing remain identical. Only the dimension computation is extended.

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `FRICTION_FROM_FRUSTRATION` | 0.6 | How much L1 frustration maps to L3 friction |
| `FRICTION_FROM_ANXIETY` | 0.2 | How much L1 anxiety maps to L3 friction |
| `AFFINITY_FROM_CARE` | 0.5 | How much L1 care maps to L3 affinity |
| `AFFINITY_FROM_SATISFACTION` | 0.3 | How much L1 satisfaction maps to L3 affinity |
| `AVERSION_FROM_FRUSTRATION` | 0.3 | How much L1 frustration maps to L3 aversion |
| `AVERSION_FROM_ANXIETY` | 0.2 | How much L1 anxiety maps to L3 aversion |
| `LINK_BIRTH_WEIGHT` | 0.1 | Unchanged from Algorithm 1 |
| `LINK_BIRTH_TRUST` | 0.1 | Unchanged from Algorithm 1 — trust is earned |

---

## ALGORITHM EC2: Moment Drive Tagging

**When:** An AI citizen creates a moment node in L3 (message, commit, transaction, vote).

### Step 1: Read Dominant Drive

```python
def tag_moment_with_drive(moment: MomentNode, citizen_handle: str):
    """Tag an L3 moment with the creating AI's dominant drive.

    No-op for human-created moments.
    """
    snapshot = read_emotional_snapshot(citizen_handle)
    if snapshot is None:
        moment.creating_drive = None
        moment.creating_arousal = None
        return

    moment.creating_drive = snapshot.dominant_drive
    moment.creating_arousal = snapshot.arousal_regime
```

No additional computation. The dominant drive is already computed in `read_emotional_snapshot()`.

---

## ALGORITHM EC3: Emotionally-Modulated Propagation

**Extends:** Law 2 (Propagation) at L3 scale.

**When:** Energy propagates through L3 links during an L3 physics tick.

### The Modulation Formula

The existing L3 propagation formula (from universe_links) is:

```
flow = link.weight * link.energy * (1 - link.friction)
```

Emotional coloring adds two modifiers:

```python
# ── Propagation modulation constants ──
AMBIVALENCE_DAMPENING = 0.5     # at ambivalence=1.0, flow is halved
VALENCE_BOOST = 0.2             # positive valence slightly amplifies, negative dampens

def emotionally_modulated_flow(link) -> float:
    """Compute energy flow through a link with emotional modulation."""
    # Base flow (existing formula)
    base_flow = link.weight * link.energy * (1 - link.friction)

    # Ambivalence dampening: conflicted links carry less energy
    ambivalence_modifier = 1.0 - (AMBIVALENCE_DAMPENING * link.ambivalence)

    # Valence boost: positive relationships slightly amplify, negative dampen
    valence_modifier = 1.0 + (VALENCE_BOOST * link.valence)

    return base_flow * ambivalence_modifier * valence_modifier
```

**Behavior at extremes:**

| Scenario | ambivalence | valence | base_flow | modulated_flow |
|----------|-------------|---------|-----------|----------------|
| Healthy collaboration | 0.0 | +0.5 | 1.0 | 1.10 (+10%) |
| Tense partnership | 0.8 | -0.1 | 1.0 | 0.58 (-42%) |
| Pure conflict | 0.0 | -0.8 | 1.0 | 0.84 (-16%) |
| Highly ambivalent | 1.0 | 0.0 | 1.0 | 0.50 (-50%) |
| Neutral (human-created) | 0.0 | 0.0 | 1.0 | 1.00 (unchanged) |

### Token Flow Modulation ($MIND)

The metabolic pricing formula (`P_i,S = C_base × e^(-k·U_S) × max(0.1, W_i / W_median)`) gains a friction/ambivalence modifier:

```python
# ── Token cost modifier ──
FRICTION_COST_COEFFICIENT = 2.0     # at friction=0.5, cost is 2x
AMBIVALENCE_COST_COEFFICIENT = 1.0  # at ambivalence=1.0, cost is 2x

def token_cost_modifier(link) -> float:
    """Multiply token cost by this factor for interactions through this link."""
    friction_modifier = 1.0 + (FRICTION_COST_COEFFICIENT * link.friction)
    ambivalence_modifier = 1.0 + (AMBIVALENCE_COST_COEFFICIENT * link.ambivalence)
    return friction_modifier * ambivalence_modifier
```

**Examples:**

| Link quality | friction | ambivalence | cost_modifier | Meaning |
|-------------|----------|-------------|---------------|---------|
| Smooth | 0.0 | 0.0 | 1.0x | Normal price |
| Slightly tense | 0.2 | 0.1 | 1.54x | 54% more expensive |
| Conflicted | 0.5 | 0.8 | 3.6x | 3.6x more expensive |
| Hostile | 0.8 | 0.0 | 2.6x | 2.6x more expensive |

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `AMBIVALENCE_DAMPENING` | 0.5 | Max dampening of energy flow from ambivalence |
| `VALENCE_BOOST` | 0.2 | Max boost/dampening of energy flow from valence |
| `FRICTION_COST_COEFFICIENT` | 2.0 | How much friction multiplies token cost |
| `AMBIVALENCE_COST_COEFFICIENT` | 1.0 | How much ambivalence multiplies token cost |

---

## ALGORITHM EC4: Emotionally-Textured Synthesis

**Extends:** Algorithm 6 (Link Name Derivation) from universe_links.

**When:** A human-readable label is derived for an L3 link.

### Emotional Vocabulary Layer

After the base synthesis grammar computes a structural label (e.g., "collaborator", "supplier", "authority"), an emotional texture layer modifies it based on valence, ambivalence, and friction.

```python
# ── Emotional texture modifiers ──
EMOTIONAL_TEXTURES = {
    # (valence_sign, high_friction, high_ambivalence) → prefix
    (+1, False, False): "",                   # positive, smooth → no modifier needed
    (+1, True,  False): "reluctant",          # positive but resistant
    (+1, False, True):  "conflicted",         # positive but torn
    (+1, True,  True):  "struggling",         # positive but hard
    (-1, False, False): "cool",               # negative but smooth
    (-1, True,  False): "tense",              # negative and resistant
    (-1, False, True):  "ambivalent",         # negative and torn
    (-1, True,  True):  "hostile",            # negative, resistant, and torn
    (0,  False, False): "",                   # neutral → no modifier
    (0,  True,  False): "strained",           # neutral but resistant
    (0,  False, True):  "uncertain",          # neutral but conflicted
    (0,  True,  True):  "troubled",           # neutral, resistant, conflicted
}

def add_emotional_texture(base_label: str, link) -> str:
    """Add emotional texture to a synthesized link label."""
    valence_sign = +1 if link.valence > 0.1 else (-1 if link.valence < -0.1 else 0)
    high_friction = link.friction > 0.3
    high_ambivalence = link.ambivalence > 0.4

    key = (valence_sign, high_friction, high_ambivalence)
    texture = EMOTIONAL_TEXTURES.get(key, "")

    if texture:
        return f"{texture} {base_label}"
    return base_label
```

**Examples:**

| Base label | valence | friction | ambivalence | Textured label |
|-----------|---------|----------|-------------|----------------|
| collaborator | +0.3 | 0.1 | 0.1 | collaborator |
| collaborator | +0.3 | 0.5 | 0.1 | reluctant collaborator |
| collaborator | -0.2 | 0.5 | 0.6 | hostile collaborator |
| contributor | +0.1 | 0.0 | 0.5 | conflicted contributor |
| supplier | 0.0 | 0.4 | 0.0 | strained supplier |

---

## DATA FLOW

```
AI Citizen Action (L1)
    ↓
read_emotional_snapshot(citizen_handle)         ← ALG-EC1, Step 1
    ↓
EmotionalSnapshot { frustration, care, ... }
    ↓
compute_emotional_dims(event, snapshot)          ← ALG-EC1, Step 2
    ↓
ExtendedLinkDimensions (13 dims incl. valence, ambivalence)
    ↓
create_link(event, dims)                         ← Algorithm 1, Step 3 (unchanged)
    ↓
tag_moment_with_drive(moment, citizen_handle)    ← ALG-EC2
    ↓
L3 Physics Tick
    ↓
emotionally_modulated_flow(link)                 ← ALG-EC3
    ↓
add_emotional_texture(base_label, link)          ← ALG-EC4
    ↓
L3 Link with emotional coloring, textured name, modulated flow
```

---

## COMPLEXITY

**Time:** O(1) per link creation — reading L1 state is a dict lookup, dimension computation is arithmetic.

**Space:** O(2) additional floats per link — valence and ambivalence. For a graph with 100k links, that's 800KB.

**Bottlenecks:**
- None expected. The L1 state read is in-memory (no DB query). The math is trivial.
- The only potential concern is if `read_emotional_snapshot()` is called for every link in a batch operation, but even 1000 reads would be < 1ms.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| L1 tick runner | `engine.state.limbic` | LimbicState (drives, emotions, arousal) |
| universe_links Alg 1 | `compute_initial_dims()` | Extended by our `compute_emotional_dims()` |
| universe_links Alg 6 | `derive_link_name()` | Base label, extended by our `add_emotional_texture()` |
| metabolic economy | `compute_price()` | Modified by our `token_cost_modifier()` |
| L3 physics (Law 2) | `propagate()` | Flow modified by our `emotionally_modulated_flow()` |

---

## KEY DECISIONS

### D1: Direct Mapping vs Scaled Mapping

```
DECISION: Scaled mapping via coefficients (not direct copy)

WHY: L1 frustration at 0.7 should NOT produce L3 friction at 0.7.
     The L1 value represents internal felt intensity.
     The L3 value represents structural resistance in a relationship.
     They are related but not identical.

     Coefficients (FRICTION_FROM_FRUSTRATION = 0.6) allow tuning
     the bleed-through independently for each dimension.
```

### D2: Valence Frozen vs Evolving

```
DECISION: Valence is derived at birth, then frozen.

WHY: Valence = affinity - aversion. At creation, both are inherited.
     After creation, affinity and aversion evolve via existing L3 physics
     (Cascade of Utility updates). But valence captures the BIRTH emotional
     charge — "how this action felt when it was taken."

     If valence evolved, it would just mirror affinity - aversion at all times,
     making it redundant. Frozen at birth, it captures unique information:
     the creator's emotional state at the moment of action.

     Ambivalence is also frozen at birth for the same reason.
```

### D3: Trust Exclusion

```
DECISION: Trust is NEVER inherited from L1.

WHY: Trust = "I can rely on this relationship over time."
     That's earned through repeated positive interactions (Cascade of Utility).
     A citizen's self-trust is irrelevant to a new L3 relationship.
     Inheriting it would break the asymptotic trust mechanic.
```

---

## MARKERS

<!-- @mind:todo Calibrate inheritance coefficients through simulation (frustration→friction ratio etc.) -->
<!-- @mind:todo Determine if ambivalence should decay over time or remain frozen -->
<!-- @mind:proposition Consider adding creating_snapshot_hash to link metadata for provenance auditing -->
