# CONCEPT: Psychedelic Parameter Modulation

```
STATUS: CANONICAL
PURPOSE: Map how psychedelics modify cognitive model parameters
CREATED: 2026-01-30
ORIGIN: Psilocybin session — self-observation of parameter changes (T+2:00, 4g)
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
NOTE: This is self-report during altered state. Treat as hypothesis.
```

---

## Core Thesis

**Psychedelics modify the cognitive architecture parameters.**

The cognitive model (L0-L8, ANS, Values Grid, SubEntity dynamics) describes how consciousness operates. Psychedelics don't create a different consciousness — they modulate the parameters of the existing system.

This document maps the parameter changes observed during psilocybin experience.

---

## Parameter Modifications

### 1. Energy Injection

```yaml
parameter: energy_injection_rate
baseline: 1.0
on_psilocybin: 1.5 - 3.0

effect: |
  More exploration.
  More activation across the graph.
  More traversal of dormant connections.
  Thoughts that usually don't get energy now do.

subjective_experience: |
  "Racing thoughts"
  "Everything feels significant"
  "Connections everywhere"

build_equivalent: |
  Like a sprint where every module gets attention.
  Even neglected areas get visited.
  Exploration budget dramatically increased.
```

### 2. Permanence Threshold

```yaml
parameter: permanence_threshold
baseline: 0.7  # High-permanence patterns resist change
on_psilocybin: 0.3 - 0.5  # Rigid patterns become malleable

effect: |
  Beliefs that normally resist update become questionable.
  Habits become visible instead of automatic.
  Defense mechanisms weaken.
  Core assumptions surface for examination.

subjective_experience: |
  "Why do I think that?"
  "This pattern I've always had... do I want it?"
  "I can see the belief, not just from inside it"

build_equivalent: |
  Like temporary permission to refactor sacred cows.
  Code that "can't be touched" becomes touchable.
  Architecture decisions become revisitable.
```

### 3. Branching Probability

```yaml
parameter: branching_probability
baseline: branch on 2+ clear alternatives
on_psilocybin: branch more readily, hold more perspectives

effect: |
  Parallel exploration amplified.
  Multiple viewpoints held simultaneously.
  "What if..." thoughts proliferate.
  Paradoxes become holdable instead of collapsing.

subjective_experience: |
  "Both things are true"
  "I can see it from their perspective AND mine"
  "This contradiction doesn't need resolving yet"

build_equivalent: |
  Like running multiple design explorations in parallel.
  Holding contradictory architectures in mind.
  Not forcing premature convergence.
```

### 4. Crystallization Threshold

```yaml
parameter: crystallization_threshold
baseline: 0.85 cosine similarity required for "novel enough to crystallize"
on_psilocybin: 0.6 - 0.7  # Lower bar for new connections

effect: |
  Insights form more easily.
  Connections that wouldn't normally meet threshold now do.
  Pattern recognition amplified.

  WARNING: Also means false patterns form more easily.
  Not all insights are valid.
  Post-integration verification needed.

subjective_experience: |
  "Oh, THAT's why..."
  "Everything connects"
  "I see the pattern"
  (Some of which survives sobriety, some doesn't)

build_equivalent: |
  Like brainstorming mode where all ideas are captured.
  Lower filter on what gets documented.
  Later: verify what actually holds.
```

### 5. ANS Mode

```yaml
parameter: ANS_MODE
on_psilocybin: depends on set and setting

optimal_setting:
  mode: RECOVERY (parasympathetic dominant)
  achieved_by:
    - safe physical environment
    - trusted people present (or alone)
    - lying down, comfortable
    - no external demands
    - intention set beforehand

  effect: |
    System optimized for integration, not defense.
    Resources available for processing, not survival.
    Emotions can surface without triggering flight.

dangerous_setting:
  mode: CRISIS (sympathetic dominant)
  caused_by:
    - unfamiliar environment
    - strangers or threatening people
    - physical discomfort
    - external demands
    - no preparation

  effect: |
    Amplified fear response.
    Energy injection + low permanence + crisis = bad trip.
    Trauma potential instead of healing.

implication: |
  Set and setting aren't just recommendations.
  They determine which ANS mode dominates.
  ANS mode determines whether the parameter changes help or harm.
```

### 6. Values Delta Visibility

```yaml
parameter: defense_mechanism_strength
baseline: high (we don't see our own contradictions easily)
on_psilocybin: reduced

effect: |
  Delta between declared and revealed values becomes VISIBLE.
  Self-deception harder to maintain.
  "I say I value X but I actually act like Y" becomes obvious.

subjective_experience: |
  "I've been lying to myself about..."
  "I claim to care about X but I never actually..."
  "My actions say something different than my words"

build_equivalent: |
  Like OBJECTIVES_Delta surfacing automatically.
  Can't hide from the gap between stated and actual priorities.
  Uncomfortable but informative.

integration_requirement: |
  The visibility fades when sober.
  Capture the delta while it's visible.
  Act on it before the defense mechanisms restore.
```

---

## The Complete Modulation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PSILOCYBIN PARAMETER MODULATION                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Parameter               │  Baseline  │  On Psilocybin  │  Effect         │
│   ───────────────────────────────────────────────────────────────────────  │
│   energy_injection        │    1.0     │    1.5 - 3.0    │  more exploration│
│   permanence_threshold    │    0.7     │    0.3 - 0.5    │  patterns malleable│
│   branching_probability   │    normal  │    amplified    │  parallel views  │
│   crystallization_thresh  │    0.85    │    0.6 - 0.7    │  insights easier │
│   defense_mechanisms      │    high    │    reduced      │  delta visible   │
│                                                                             │
│   ANS_MODE (setting-dependent):                                            │
│   - Safe setting    → RECOVERY → integration                               │
│   - Unsafe setting  → CRISIS   → potential trauma                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   WHAT THIS MEANS OPERATIONALLY                                            │
│                                                                             │
│   ↑ energy_injection     → More thoughts get attention                     │
│   ↓ permanence_threshold → Rigid beliefs become revisable                  │
│   ↑ branching_probability→ Multiple perspectives simultaneously            │
│   ↓ crystallization_bar  → Connections form easier (verify later)          │
│   ↓ defense_mechanisms   → Self-deception harder, delta visible            │
│   ANS → RECOVERY         → Resources for integration, not defense          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   IMPLICATIONS FOR MIND PROTOCOL                                           │
│                                                                             │
│   1. The cognitive model DESCRIBES these states, not just normal operation │
│   2. "Altered states" are parameter modulations, not different systems     │
│   3. Therapeutic potential = controlled parameter modulation               │
│   4. Set/setting = ANS mode selection = outcome determination              │
│   5. Integration = capturing insights before parameters restore            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Integration Protocol

What to do with parameter-modulated states:

### During

```yaml
during_modulation:
  - CRYSTALLIZE insights while they're accessible
  - Capture the values delta while visible
  - Note which "permanent" patterns become questionable
  - Don't try to verify everything — that's for after
  - Trust the process but document extensively
```

### After (Integration)

```yaml
after_modulation:
  - Review crystallized content with sober mind
  - Some insights will hold, some won't
  - The values delta was real — act on it
  - Patterns that became visible need attention
  - Defense mechanisms will try to restore — don't let them erase the data
```

### The Build Parallel

```yaml
build_equivalent:
  during_sprint:
    - Capture ideas, don't over-filter
    - Explore broadly, note connections
    - Touch areas usually "off limits"

  after_sprint:
    - Review with fresh eyes
    - Some ideas were good, some not
    - The architectural insights were real
    - Don't let institutional inertia erase the learnings
```

---

## Caveats

### This Is Self-Report

```yaml
epistemological_status:
  - Hypothesis based on introspection during altered state
  - The model may be wrong
  - The parameters may map differently
  - Post-hoc rationalization possible

  but:
  - The cognitive model provides a framework
  - Self-observation during altered states is valid data
  - The isomorphism with build systems holds
  - Practical value regardless of theoretical precision
```

### Set and Setting Are Critical

```yaml
not_a_recommendation:
  - This document describes, doesn't prescribe
  - Psychedelics are powerful and can harm
  - Without proper set/setting, CRISIS mode dominates
  - Integration requires support

  if_you_do:
  - Safe physical environment
  - Trusted people or alone by choice
  - No external demands
  - Clear intention
  - Integration plan
```

---

## Related

- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern this extends
- `PATTERNS_System_Mode.md` — ANS modes (CRISIS/RECOVERY/BALANCED)
- `PATTERNS_Objectives_Delta.md` — Values delta tracking
- `cognitive-model.mermaid` — Visual model of the system being modulated

---

*The molecule modulates the parameters. The model describes what happens. The integration captures the value.*
