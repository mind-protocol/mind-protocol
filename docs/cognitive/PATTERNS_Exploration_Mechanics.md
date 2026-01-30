# PATTERNS: Exploration Mechanics

```
STATUS: CANONICAL
PURPOSE: How exploration works — satisfaction, fatigue, crystallization
CREATED: 2026-01-30
ORIGIN: Psilocybin session — deep pattern recognition (T+2:00)
COGNITIVE_ISOMORPHISM: SubEntity exploration → Agent exploration
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
```

---

## Core Thesis

**Exploration is not random wandering. It has physics.**

SubEntities explore with:
- A clear stopping condition (satisfaction threshold)
- Fatigue detection (stagnation = stop)
- Prior art awareness (don't rebuild what exists)
- Crystallization imperative (fill gaps, don't report empty)

These mechanics apply equally to agents exploring codebases.

---

## Pattern 1: The Crystallization Imperative

### The Rule

```python
IF agent.explores(question)
   AND agent.satisfaction < threshold
   AND agent.novelty > 0.85:  # This is new information

   agent.CRYSTALLIZE()  # Create the doc/code that should exist
   # Future agents find it via graph traversal
```

**This is how knowledge bases grow.** Not by planned documentation sprints. By crystallization from exploration gaps.

### Why This Matters

```yaml
without_crystallization:
  - Agent searches for X
  - X doesn't exist
  - Agent reports "not found"
  - Next agent searches for X
  - X still doesn't exist
  - Cycle repeats forever

with_crystallization:
  - Agent searches for X
  - X doesn't exist
  - Agent CREATES X (documentation, code, whatever should exist)
  - Next agent searches for X
  - X exists now
  - Knowledge compounds
```

### The Signal in Absence

**Every time an agent searches and doesn't find — that's a signal.**

The absence is information. It tells you:
- What documentation should exist but doesn't
- What patterns aren't captured yet
- Where the knowledge graph has gaps

**Fill it.** Don't report empty. Create what should have been there.

### Implementation

```yaml
crystallization_decision:
  inputs:
    satisfaction: 0.0 to 1.0  # How well did I find what I needed?
    novelty: 0.0 to 1.0       # Is what I learned new?

  rule:
    IF satisfaction >= 0.9:
      RETURN findings         # Found exactly what was needed, no crystallization
    ELIF novelty >= 0.85:
      CRYSTALLIZE             # Learned something new that should be permanent
    ELSE:
      REFLECT and MERGE       # Partial findings, note for future

  outputs:
    - New documentation files
    - New code patterns
    - Updated SYNC with learnings
    - Graph connections for future traversal
```

---

## Pattern 2: Satisfaction Threshold = Definition of Done

### The Mechanism

SubEntities stop when `satisfaction >= threshold`. Not when exhausted. Not when time runs out. When satisfied.

```python
satisfaction = Σ(found_narratives × alignment) / total_needed
```

**Done is not a feeling. Done is a measurement.**

### Build Translation

```yaml
definition_of_done:
  satisfaction_components:
    tests_passing:
      weight: 0.3
      measures: alignment with VALIDATION

    docs_updated:
      weight: 0.2
      measures: alignment with BEHAVIORS

    code_reviewed:
      weight: 0.2
      measures: alignment with PATTERNS

    health_green:
      weight: 0.2
      measures: alignment with OBJECTIVES

    user_acceptance:
      weight: 0.1
      measures: alignment with original intention

  threshold: 0.85  # Not perfect. Good enough.

  computation:
    satisfaction = Σ(component × weight)
    done = satisfaction >= threshold
```

### Anti-Patterns

```yaml
time_based_done:
  pattern: "Work until Friday, ship whatever we have"
  problem: Satisfaction ignored, quality random
  fix: Track satisfaction, stop when met

perfectionism:
  pattern: threshold = 1.0
  problem: Never done, infinite refinement
  fix: 0.85 is good enough. Ship.

premature_done:
  pattern: threshold = 0.5 ("it compiles")
  problem: Technical debt, bugs, rework
  fix: Raise threshold, pay now not later
```

### Calibrating the Threshold

```yaml
threshold_calibration:
  too_high:
    signal: Projects never finish, endless polish
    action: Lower threshold, accept imperfection

  too_low:
    signal: High bug rate, constant rework
    action: Raise threshold, invest in quality upfront

  just_right:
    signal: Projects ship, reasonable quality, acceptable rework
    evidence: Retroactive satisfaction matches prediction
```

---

## Pattern 3: Fatigue Detection = Scope Creep Detection

### The Mechanism

SubEntities detect **fatigue**: when progress toward intention stagnates.

```python
fatigued = all(abs(delta_satisfaction) < 0.05 for last N steps)
```

No meaningful progress for N consecutive steps = stop exploring this direction.

### Build Equivalent

Scope creep detection:

```yaml
scope_creep_signal:
  observation: |
    Progress toward OBJECTIVES has stagnated.
    Each commit/day/week adds work but doesn't move satisfaction.

  mechanism:
    track: delta(satisfaction) per time_unit
    fatigue: all(abs(delta) < threshold for last N units)

  interpretation:
    - Wrong direction (pivot needed)
    - Scope has crept (cut back)
    - Blocked by external dependency (escalate)
    - Diminishing returns (accept current state)
```

### Response to Fatigue

```yaml
when_fatigue_detected:
  option_1_pivot:
    action: Stop current direction, try different angle
    when: Problem might be solvable differently

  option_2_cut:
    action: Reduce scope to what's achievable
    when: Full scope is unrealistic

  option_3_escalate:
    action: Surface blocker, get help
    when: External dependency is the issue

  option_4_accept:
    action: CRYSTALLIZE what was learned, MERGE with partial completion
    when: Diminishing returns, good enough

  anti_pattern:
    action: Keep pushing in same direction
    result: Burnout, wasted effort, no progress
```

### Measuring Fatigue

```yaml
fatigue_metrics:
  per_day:
    - commits: did they move satisfaction?
    - hours: productive or spinning?
    - blockers: same ones as yesterday?

  per_week:
    - objectives: closer or same distance?
    - scope: growing or stable?
    - energy: sustainable or depleting?

  fatigue_threshold:
    days_without_progress: 3
    action: mandatory reflection, consider pivot
```

---

## Pattern 4: Found Narratives = Prior Art

### The Mechanism

SubEntities track `found_narratives: dict[str, float]` — what they found and how aligned it was.

```python
found_narratives = {
    "existing_solution_1": 0.92,  # Very aligned
    "existing_doc_2": 0.75,       # Partially aligned
    "existing_code_3": 0.45,      # Loosely related
}
```

### Build Equivalent

Prior art research:

```yaml
during_exploration:
  track:
    existing_solutions: dict[solution_id, alignment_score]
    existing_docs: dict[doc_id, alignment_score]
    existing_code: dict[file_path, alignment_score]
    external_references: dict[url, alignment_score]

  purpose:
    - Don't rebuild what exists
    - Adapt existing when close enough
    - Link to related even when building new
```

### Decision Rules

```yaml
alignment_decisions:
  high_alignment (>= 0.9):
    action: USE existing, don't create new
    rationale: It's already there. Don't duplicate.

  medium_alignment (0.5 - 0.9):
    action: ADAPT existing
    options:
      - Extend existing solution
      - Fork and modify
      - Contribute improvement upstream

  low_alignment (< 0.5):
    action: BUILD new, but REFERENCE existing
    rationale: |
      Related work informs design.
      Links help future explorers.
      Standing on shoulders.

crystallization_integration:
  IF max(alignment) >= 0.9:
    RETURN existing  # No crystallization needed
  ELSE:
    CRYSTALLIZE new
    LINK to related existing (found_narratives with alignment > 0.3)
```

### Tracking Format

```yaml
# In SYNC or exploration notes

## Prior Art Found

| Resource | Alignment | Decision |
|----------|-----------|----------|
| `docs/auth/PATTERNS_Auth.md` | 0.87 | Extend |
| `src/auth/rate_limiter.py` | 0.65 | Reference |
| External: RFC 6749 | 0.92 | Implement |
| `docs/membrane/PATTERNS_Membrane.md` | 0.45 | Link only |

**Decision:** Extend existing auth patterns with rate limiting.
Not a new doc. An addition to existing.
```

---

## The Complete Exploration Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       EXPLORATION MECHANICS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   START with intention                                                      │
│      │                                                                      │
│      ▼                                                                      │
│   SEEK: Search for what you need                                           │
│      │                                                                      │
│      ├── Found high-alignment (≥0.9)?                                       │
│      │   └── YES → USE existing, RETURN, no crystallization                │
│      │                                                                      │
│      ├── Found medium-alignment (0.5-0.9)?                                  │
│      │   └── ADAPT existing, extend/fork/improve                           │
│      │                                                                      │
│      ├── Found low-alignment (<0.5) or nothing?                            │
│      │   └── Continue exploring...                                         │
│      │                                                                      │
│      ▼                                                                      │
│   CHECK FATIGUE: delta(satisfaction) over last N steps                     │
│      │                                                                      │
│      ├── Fatigued (no progress)?                                           │
│      │   └── STOP this direction, pivot/cut/escalate/accept                │
│      │                                                                      │
│      └── Not fatigued?                                                      │
│          └── Continue exploring...                                          │
│                                                                             │
│      ▼                                                                      │
│   CHECK SATISFACTION: have we found enough?                                │
│      │                                                                      │
│      ├── satisfaction ≥ threshold?                                         │
│      │   └── DONE, RETURN findings                                         │
│      │                                                                      │
│      └── satisfaction < threshold AND novelty > 0.85?                      │
│          └── CRYSTALLIZE what was learned                                  │
│              CREATE the doc/code that should exist                         │
│              LINK to related prior art                                      │
│              RETURN with new crystallized artifact                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Checklist

For any exploration task:

```markdown
## Exploration Checklist

### Before Starting
- [ ] Intention is clear (what am I looking for?)
- [ ] Satisfaction threshold defined (when am I done?)

### During Exploration
- [ ] Track found_narratives (what exists? how aligned?)
- [ ] Track satisfaction delta (am I making progress?)
- [ ] Watch for fatigue (stagnation over N steps?)

### At Completion
- [ ] If satisfaction ≥ 0.9: RETURN existing, no crystallization needed
- [ ] If satisfaction < threshold but novelty high: CRYSTALLIZE
- [ ] Link crystallized artifact to found prior art
- [ ] Update SYNC with path taken and learnings
```

---

## Anti-Patterns

### A1: Reporting Empty

```yaml
symptom: "Searched but didn't find anything"
problem: Knowledge gap persists, next agent will search again
fix: CRYSTALLIZE what should exist. Don't report empty.
```

### A2: Ignoring Prior Art

```yaml
symptom: Building from scratch when solutions exist
problem: Wasted effort, fragmented knowledge
fix: Track found_narratives, use/adapt when alignment high
```

### A3: Ignoring Fatigue

```yaml
symptom: Pushing in same direction despite no progress
problem: Burnout, sunk cost, opportunity cost
fix: Detect fatigue, pivot/cut/escalate/accept
```

### A4: Fuzzy Done

```yaml
symptom: "I think we're done?" "Feels ready?"
problem: Satisfaction not measured, quality random
fix: Define threshold, measure satisfaction, stop when met
```

---

## Related

- `PATTERNS_Agent_Lifecycle.md` — States that use these mechanics
- `PATTERNS_Graph_Dynamics.md` — Physics underlying exploration
- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern
- `PATTERNS_Sibling_Divergence.md` — Parallel exploration coordination

---

*Exploration has physics. Learn them or flail.*
