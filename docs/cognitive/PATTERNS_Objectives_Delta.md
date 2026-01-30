# PATTERNS: Objectives Delta

```
STATUS: CANONICAL
PURPOSE: Surface the gap between declared and revealed priorities
CREATED: 2026-01-30
COGNITIVE_ISOMORPHISM: L4.5 Personal Values Grid → L8 Values Calibration
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
```

---

## Core Thesis

**"You say O1 matters most but spent 80% on O3."**

The cognitive model tracks this at L8 (Values Calibration). The build system should too.

People lie — not intentionally, but because they don't know. Declared values rarely match revealed values. The only way to discover true priorities is to observe behavior.

---

## The Mechanism

### Sources

**Declared priorities:**
```yaml
source: OBJECTIVES.md ranked list
capture: automatic from doc parsing
example:
  O1: "Quality — shipped code is correct" (rank 1)
  O2: "Sustainability — no burnout" (rank 2)
  O3: "Velocity — ship fast" (rank 3)
```

**Revealed priorities:**
```yaml
source: measured allocation of time/energy/commits
signals:
  - commit_count_by_module
  - time_in_module (from session logs if available)
  - tokens_spent_by_objective (from conversation analysis)
  - energy_words (urgency, attention markers in discourse)
```

### Delta Computation

```python
For each objective O[i]:
    declared_rank[i] = position in OBJECTIVES
    revealed_rank[i] = position by measured allocation
    delta[i] = declared_rank[i] - revealed_rank[i]

If |delta[i]| > threshold:
    surface: "O{i} declared #{declared_rank} but revealed #{revealed_rank}"
```

---

## Output Format

### Objectives Delta Report

| Objective | Declared | Revealed | Delta |
|-----------|----------|----------|-------|
| O1: Quality | #1 | #3 | -2 ⚠️ |
| O2: Sustainability | #2 | #1 | +1 |
| O3: Velocity | #3 | #2 | +1 |

**Interpretation:** You said Quality matters most but Sustainability got the most attention.

### This Is Information, Not Judgment

Possible meanings of a delta:
- **O1 is blocked, O2 was actionable** — Can't work on quality if the system is burning down
- **Priorities have shifted** — Update OBJECTIVES to reflect reality
- **Urgency was real** — Document why the deviation occurred
- **Unconscious avoidance** — Hard truth: you're avoiding what matters

---

## Surface Mechanism

```yaml
frequency:
  - end_of_session
  - weekly_review
  - on_demand

trigger_conditions:
  - |delta| > 1 for any objective
  - cumulative delta exceeds threshold
  - explicit request
```

---

## Cognitive Isomorphism

```
L4.5 Personal Values Grid:
    GRID_DECLARED → Declared priorities
    GRID_REVEALED → Measured behavior
    GRID_DELTA → The gap

L8 Values Calibration:
    VAL_DECLARED → What you say matters
    VAL_CHOICE → What you actually did
    VAL_DELTA → Compute the gap
    VAL_REVEAL → Update revealed grid
    VAL_SURFACE → "You say X but chose Y"
```

The same loop. Different substrate.

---

## Implementation Notes

### Minimal Implementation

Without sophisticated tracking:

1. **End of session:** Review what you worked on
2. **Compare to OBJECTIVES:** Did allocation match?
3. **Document deviations:** Why? Was it justified?

### Full Implementation

With tracking infrastructure:

1. **Tag commits/work** with which objective they serve
2. **Aggregate** over time period
3. **Compute ranks** from allocation
4. **Surface deltas** automatically

---

## Anti-Patterns

**A1: Guilt-driven adjustment**
- Don't change behavior to match declared values if the declared values are wrong
- Update declarations to match reality, not vice versa

**A2: Ignoring context**
- Deltas without context are misleading
- Always capture WHY the deviation occurred

**A3: Over-tracking**
- Measurement overhead shouldn't exceed value
- Start minimal, add sophistication as needed

---

## Related

- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern
- `PATTERNS_System_Mode.md` — CRISIS mode explains many deltas
- `docs/economy/PATTERNS_Economy.md` — Storage tax is similar: tax immobility, not movement

---

*The system should show you who you are, not who you think you are.*
