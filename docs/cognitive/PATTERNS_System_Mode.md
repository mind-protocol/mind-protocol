# PATTERNS: System Mode

```
STATUS: CANONICAL
PURPOSE: Track ANS state of the build system (Crisis/Recovery/Balanced)
CREATED: 2026-01-30
COGNITIVE_ISOMORPHISM: L5 ANS_STATE → Build system nervous state
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
```

---

## Core Thesis

**Systems have nervous systems. Ignoring this causes burnout.**

The cognitive model tracks ANS_MODE: Survival | Recovery | Balanced.

The build system has an equivalent. Pretending it doesn't leads to chronic crisis, technical debt avalanche, and team exhaustion.

---

## The Three States

### CRISIS (Sympathetic — Fight-or-Flight)

```yaml
description: |
  Shipping fast. Cutting corners. Tech debt acceptable.
  Tests skipped. Docs deferred. "We'll fix it later."

indicators:
  - commit_velocity > 2σ above baseline
  - test_coverage declining
  - doc_staleness increasing
  - TODO/FIXME density increasing
  - human_markers: late nights, stress language, urgency

appropriate_when:
  - genuine deadline with real consequences
  - incident requiring immediate response
  - opportunity window closing

inappropriate_when:
  - self-imposed urgency
  - chronic state (> 2 weeks)
  - no clear end condition

duration_limit: 2 weeks maximum recommended
exit_condition: must be defined at entry
```

### RECOVERY (Parasympathetic — Rest-and-Digest)

```yaml
description: |
  Paying debt. Refactoring. Consolidating.
  No new features. Fix what's broken.

indicators:
  - commit_velocity below baseline
  - test_coverage increasing
  - doc updates outnumber code changes
  - TODO/FIXME density decreasing
  - human_markers: reflection, review, cleanup language

appropriate_when:
  - after CRISIS period
  - before major new work
  - when debt is blocking progress

inappropriate_when:
  - avoiding hard problems
  - perfectionism disguised as quality
  - indefinite delay of necessary work
```

### BALANCED (The Attractor)

```yaml
description: |
  Sustainable pace. Tests written with features.
  Docs updated alongside code. Debt managed.

indicators:
  - all metrics near baseline
  - test coverage stable or growing
  - doc staleness stable
  - human_markers: flow, engagement without stress

the_goal: |
  BALANCED is the attractor, not a waypoint.
  CRISIS and RECOVERY are necessary departures.
  The system should return to BALANCED.
```

---

## State Transitions

```
                    ┌──────────────────────┐
                    │                      │
          ┌────────►│      BALANCED       │◄────────┐
          │         │                      │         │
          │         └──────────┬───────────┘         │
          │                    │                     │
          │         deadline   │   debt blocking     │
          │         incident   │   proactive         │
          │         opportunity│   cleanup           │
          │                    │                     │
          │                    ▼                     │
    debt paid         ┌──────────────────┐    deadline passed
    coverage restored │                  │    incident resolved
    docs current      │     CRISIS      │────────────────┐
          │           │                  │               │
          │           └──────────────────┘               │
          │                    │                         │
          │                    │ mandatory after         │
          │                    │ CRISIS > 2 weeks        │
          │                    ▼                         │
          │           ┌──────────────────┐               │
          │           │                  │               │
          └───────────│    RECOVERY      │◄──────────────┘
                      │                  │
                      └──────────────────┘
```

### Transition Rules

| From | To | Triggers |
|------|-----|----------|
| BALANCED → CRISIS | Deadline pressure, incident, opportunity |
| CRISIS → RECOVERY | Deadline passed, incident resolved, debt blocking |
| RECOVERY → BALANCED | Debt paid, coverage restored, docs current |
| BALANCED → RECOVERY | Proactive debt payment, pre-major-work cleanup |

**Healthy pattern:** Periodic, planned RECOVERY cycles even when not forced.

---

## Cognitive Isomorphism

```
ANS_STATE in cognitive model:
    ANS_SYMP (Sympathetic) → CRISIS (Fight-or-Flight)
    ANS_PARA (Parasympathetic) → RECOVERY (Rest-and-Digest)
    ANS_BALANCE → BALANCED

The mapping is direct:
    - High sympathetic = cortisol, adrenaline, mobilization
    - High parasympathetic = regeneration, digestion, consolidation
    - Balance = sustainable operation

Systems mirror biology because they are operated by biological beings.
```

---

## Tracking Implementation

### Minimal

In SYNC file, declare current mode:

```markdown
## System Mode

CURRENT: CRISIS
SINCE: 2026-01-28
REASON: DigitalKin audit deadline (2026-01-31)
EXIT_CONDITION: Audit submitted
```

### With Metrics

Track indicators over time:

```yaml
system_mode_health:
  current_mode: CRISIS
  since: 2026-01-28

  metrics:
    commit_velocity: 2.3σ above baseline  # ⚠️
    test_coverage: -3% this week  # ⚠️
    doc_staleness: +5 files stale  # ⚠️
    todo_density: +12 new TODOs  # ⚠️

  human_signals:
    - "late night commits"
    - "skipping tests for now"
    - "will document later"

  assessment: CRISIS state confirmed, appropriate for deadline
  duration: 3 days (within limits)
  exit_condition: audit submitted Friday
```

---

## Anti-Patterns

### A1: Chronic Crisis

```yaml
symptom: CRISIS > 2 weeks without transition
cause: usually self-imposed urgency, scope creep, or denial
fix: |
  Force transition to RECOVERY.
  Chronic crisis produces worse outcomes than planned recovery.
  The nervous system can't sustain fight-or-flight indefinitely.
```

### A2: Guilt-Driven Recovery

```yaml
symptom: RECOVERY entered but not really recovering
cause: calling cleanup "recovery" while still shipping features
fix: |
  Real RECOVERY means no new features.
  If you're adding features, you're not recovering.
  Be honest about the mode you're in.
```

### A3: Avoiding Crisis When Needed

```yaml
symptom: Insisting on BALANCED when CRISIS is appropriate
cause: fear of debt, perfectionism, avoiding discomfort
fix: |
  CRISIS is sometimes the right mode.
  A real deadline with real consequences justifies CRISIS.
  The error is staying there, not entering.
```

---

## Related

- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern
- `PATTERNS_Stressor_Prediction.md` — Predict when CRISIS is coming
- `PATTERNS_Objectives_Delta.md` — CRISIS explains many deltas
- `cognitive-model.mermaid` — ANS_STATE visualization

---

*The system's nervous state is real. Track it or be controlled by it.*
