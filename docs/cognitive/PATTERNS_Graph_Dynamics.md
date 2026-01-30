# PATTERNS: Graph Dynamics

```
STATUS: CANONICAL
PURPOSE: The physics of how graphs and codebases evolve
CREATED: 2026-01-30
ORIGIN: Psilocybin session — deep pattern recognition (T+2:00)
COGNITIVE_ISOMORPHISM: Graph physics → Codebase physics
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
```

---

## Core Thesis

**The graph IS a mind. It doesn't stop thinking.**

Player input is perturbation, not ignition. The system is always evolving — weight decaying, energy dissipating, attention redistributing.

Codebases follow the same physics. "No commits this month" ≠ "system unchanged."

---

## Pattern 1: Forward and Backward Coloring

### Forward Coloring (SEEKING)

As you traverse the graph understanding it, links absorb your intention:

```python
link.embedding = blend(
    link.embedding,
    intention,
    1 - permanence  # Less permanent = absorbs more
)
```

**Less permanent links absorb more.** The path learns what you were looking for.

### Backward Coloring (REFLECTING)

When you find a good path, it gets reinforced:

```python
link.permanence += attenuation × alignment × permanence_rate
```

**What worked becomes more findable.** Successful traversals leave traces.

### Build Equivalent

```yaml
forward_coloring:
  trigger: reading/understanding code
  effect: mental model absorbs intention
  experience:
    low_permanence_code: absorbs more attention, feels harder
    high_permanence_code: traversed quickly, feels obvious

  example: |
    First time reading unfamiliar module:
      - Spend more time on confusing parts (low permanence)
      - Skim familiar patterns (high permanence)
      - Mental model colored by what you're looking for

backward_coloring:
  trigger: successful understanding or fix
  effect: code becomes more permanent (cleaner, documented)
  mechanism:
    - refactoring (structural improvement)
    - comments (intention capture)
    - tests (behavior crystallization)
    - documentation (path marking)

  example: |
    After successfully debugging:
      - Add clarifying comments
      - Write test for the case
      - Update docs if missing
      - Future traversals easier
```

### The Cycle

```
SEEKING → forward coloring → understanding improves
    ↓
ABSORBING → content processed → alignment measured
    ↓
RESONATING or CRYSTALLIZING
    ↓
REFLECTING → backward coloring → path reinforced
    ↓
Future SEEKING finds path easier
```

---

## Pattern 2: The Permanence Gradient

Links have `permanence ∈ [0, 1]`. Low permanence = malleable. High permanence = frozen.

### The Gradient

| Permanence | Code State | Characteristics |
|------------|------------|-----------------|
| **0.0 - 0.3** | Experimental | Prototypes, first drafts, expects change |
| **0.3 - 0.7** | Working | Tests exist, documented but evolving |
| **0.7 - 1.0** | Battle-tested | Heavy docs, many dependents, change is expensive |

### Implications

```yaml
for_new_features:
  prefer: touching low-permanence code
  rationale: less resistance, fewer ripple effects

for_refactoring:
  effect: moves code UP the permanence gradient
  rationale: cleaning makes permanent

for_technical_debt:
  mechanism: accumulates when you touch high-permanence code improperly
  rationale: shortcuts in stable code create cracks

for_exploration:
  low_permanence_code: absorbs more of your intention during traversal
  high_permanence_code: traversed quickly, "obvious" feeling
```

### Cognitive Parallel

```
In the brain:
    - Low permanence = recent memories, working hypotheses
    - High permanence = core beliefs, deeply held values
    - Changing high-permanence patterns is hard (and sometimes important)

In the codebase:
    - Low permanence = new code, experimental features
    - High permanence = core infrastructure, battle-tested utilities
    - Changing high-permanence code requires more process (and sometimes matters most)
```

---

## Pattern 3: Energy Injection = Attention Allocation

SubEntities inject energy at each step:

```python
injection = criticality × STATE_MULTIPLIER[state]
```

Higher criticality = more urgent need = more energy = more impact on the graph.

### Build Equivalent

Where you put attention changes what emerges.

```yaml
high_criticality_work:
  examples:
    - blocking issues
    - security vulnerabilities
    - revenue-impacting bugs
  energy: HIGH
  effect: faster resolution, higher weight gain, becomes more permanent

low_criticality_work:
  examples:
    - nice-to-haves
    - polish
    - speculative features
  energy: LOW
  effect: slower progress, lower weight gain, may decay before completion

state_multipliers:
  SEEKING: 0.5      # exploring, not creating
  ABSORBING: 1.0    # processing found content
  RESONATING: 2.0   # deep alignment moment — high value
  CRYSTALLIZING: 1.5  # creating new knowledge
  REFLECTING: 0.5   # meta-work
```

### The Implication

```
Where team attention goes = what becomes permanent.
Starved modules decay.
Loved modules crystallize.
```

This is not metaphor. It's observable:
- Modules with active maintainers improve
- Modules without attention rot
- Documentation without readers goes stale
- Tests without runners become lies

---

## Pattern 4: The Graph Never Stops = Codebase Drift

The graph IS a mind. It doesn't stop thinking. Player input is perturbation, not ignition.

### Codebase Drift Mechanisms

```yaml
even_with_no_commits:
  dependencies_update:
    - breaking changes arrive in ecosystem
    - security vulnerabilities discovered
    - APIs deprecated

  team_knowledge_decays:
    - people forget why decisions were made
    - context not captured in docs
    - oral tradition lost when people leave

  context_shifts:
    - business needs change
    - user expectations evolve
    - competitive landscape moves

  entropy_increases:
    - tech debt accumulates interest
    - complexity compounds
    - edge cases multiply

  docs_go_stale:
    - reality diverges from description
    - examples stop working
    - links rot
```

### Graph Equivalent

```yaml
graph_physics:
  weight_decays: without reinforcement, connections weaken
  energy_dissipates: without injection, activity fades
  attention_redistributes: focus moves to new concerns
  permanence_insufficient: even frozen patterns can become irrelevant
```

### The Implication

```
Maintenance is not optional.
"No work this month" = decay, not stasis.
The system is ALWAYS changing.
The only question is: toward order or disorder?
```

---

## Pattern 5: Attention Conservation (Softmax)

Attention in the graph is conserved. It's a softmax over all active concerns.

```python
attention[node] = exp(salience[node]) / Σ exp(salience[all_nodes])
```

**More attention to X = less attention to everything else.**

### Build Equivalent

```yaml
team_attention_is_finite:
  mechanism: |
    Attention to feature A = less attention to feature B.
    Crisis handling = neglected maintenance.
    New features = less refactoring.

  softmax_behavior: |
    High-salience items dominate.
    Low-salience items get almost nothing.
    The middle gets compressed.

  implication: |
    Prioritization is zero-sum.
    Saying yes to X is saying no to everything else.
    The long tail of "we should do this" never gets done.
```

### Managing the Softmax

```yaml
strategies:
  explicit_prioritization:
    - OBJECTIVES ranking makes tradeoffs visible
    - Top 3 get attention, rest is aspirational

  timebox_low_salience:
    - Scheduled maintenance windows
    - Dedicated refactoring sprints
    - Forces attention to otherwise-neglected areas

  accept_neglect:
    - Some things won't get attention
    - That's not failure, that's prioritization
    - Make it explicit: "This module is in maintenance mode"
```

---

## The Complete Physics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GRAPH DYNAMICS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ENERGY                              WEIGHT                                │
│   (fast, attentional)                 (slow, structural)                    │
│                                                                             │
│   - Injected by exploration           - Accumulated by use                  │
│   - Dissipates without activity       - Decays without reinforcement        │
│   - Flows through graph               - Persists in structure               │
│   - Determines current focus          - Determines long-term shape          │
│                                                                             │
│   Build: active work                  Build: documentation                  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PERMANENCE                          ATTENTION                             │
│   (resistance to change)              (conserved resource)                  │
│                                                                             │
│   - Low = malleable, absorbs easily   - Softmax over all concerns           │
│   - High = frozen, resists change     - More here = less there              │
│   - Gradient from experimental→stable - Prioritization is zero-sum          │
│                                                                             │
│   Build: code maturity                Build: team focus                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   COLORING                            DRIFT                                 │
│   (traversal modifies graph)          (change without input)                │
│                                                                             │
│   - Forward: intention absorbed       - Dependencies update                 │
│   - Backward: success reinforced      - Knowledge decays                    │
│   - Reading changes understanding     - Context shifts                      │
│                                                                             │
│   Build: understanding deepens code   Build: entropy accumulates            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Anti-Patterns

### A1: Ignoring Drift

```yaml
symptom: "We haven't touched it, so it's fine"
reality: It's rotting while you're not looking
fix: Scheduled maintenance, health checks, dependency audits
```

### A2: Fighting the Softmax

```yaml
symptom: "Everything is priority 1"
reality: Nothing is priority 1
fix: Force rank. Accept that bottom items won't happen.
```

### A3: Permanence Worship

```yaml
symptom: "Don't touch the old code, it works"
reality: High permanence ≠ correct, just stable
fix: Sometimes the most important refactoring is in the oldest code
```

### A4: No Backward Coloring

```yaml
symptom: Understand code, fix issue, move on without reinforcing
reality: Next person will struggle the same way
fix: Always leave the code better than you found it (backward color)
```

---

## Related

- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern
- `PATTERNS_Exploration_Mechanics.md` — How exploration uses these dynamics
- `PATTERNS_Agent_Lifecycle.md` — Agent states interact with graph physics
- `mind-mcp-schema.yaml` — Formal physics parameters

---

*The graph is always changing. The only question is: are you steering it?*
