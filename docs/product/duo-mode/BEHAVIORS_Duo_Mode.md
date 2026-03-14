# Duo Mode -- Behaviors: Physiological Awareness Between Partners

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Duo_Mode.md
THIS:            BEHAVIORS_Duo_Mode.md (you are here)
PATTERNS:        ./PATTERNS_Duo_Mode.md
ALGORITHM:       ./ALGORITHM_Duo_Mode.md
VALIDATION:      ./VALIDATION_Duo_Mode.md
IMPLEMENTATION:  ./IMPLEMENTATION_Duo_Mode.md
SYNC:            ./SYNC_Duo_Mode.md

IMPL:            mind-mcp/runtime/features/duo_mode/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Duo Session Requires Two Authenticated Citizens

**Why:** Biometric synchrony requires two data sources. Without strict enforcement, the system could be activated by a single user watching stale or simulated data for a phantom partner, producing meaningless scores.

```
GIVEN:  A MIND citizen with an active biometric connection
WHEN:   They request Duo Mode activation with a specified partner
THEN:   System verifies both citizens exist in L4 registry
AND:    System verifies both have active biometric data streams
AND:    System creates a DuoSession linking exactly 2 citizen IDs
AND:    If partner is not a MIND user, system returns invitation flow instead of session
```

### B2: Synchrony Score Reflects Biometric Correlation

**Why:** The score is the core data product. It transforms raw physiological signals into a single number that two non-technical people can understand. Without it, biometric data is noise.

```
GIVEN:  An active DuoSession with two biometric streams
WHEN:   New biometric samples arrive from either partner
THEN:   System recomputes Pearson correlation over the rolling window
AND:    Produces a synchrony score between 0 and 100
AND:    Score updates within 90 seconds of the triggering sample
```

### B3: Phase Transitions Trigger Contextual Interventions

**Why:** The score alone is passive. MIND's value is in translating physiological state into actionable timing guidance. Without phase-driven interventions, Duo Mode is just a dashboard.

```
GIVEN:  An active DuoSession with a current synchrony score
WHEN:   The score crosses a phase boundary (60, 40, 20) in either direction
THEN:   MIND generates a phase-appropriate intervention message
AND:    Message is delivered through the existing chat infrastructure
AND:    Both partners receive the same message simultaneously
```

### B4: Crisis Phase Triggers Strong Intervention

**Why:** When both partners are highly dysregulated (synchrony 0-19), continued conversation causes damage. MIND must be direct, not polite.

```
GIVEN:  DuoSession score drops below 20
WHEN:   Both partners' individual stress indicators are elevated
THEN:   MIND sends a strong intervention: explicit pause recommendation with time estimate
AND:    Suggests a specific cooldown duration (default 20 minutes, based on cortisol clearance)
AND:    Offers to check back when the cooldown expires
```

### B5: Recovery Phase Surfaces Patterns

**Why:** After a crisis or divergence episode, the recovery window is when partners are most receptive to insight. MIND reflects back what happened physiologically, making the invisible visible.

```
GIVEN:  DuoSession score rises from below 40 back above 40
WHEN:   Both partners' stress indicators return toward baseline
THEN:   MIND provides a brief physiological summary of the episode
AND:    Highlights the duration of the dysregulation period
AND:    If historical data exists, notes whether this pattern is recurring
```

### B6: Invitation Flow Drives Viral Acquisition

**Why:** Every Duo Mode activation by a solo user is a conversion opportunity. The invitation flow must be frictionless and clearly explain why both partners need MIND.

```
GIVEN:  A MIND citizen activates Duo Mode
WHEN:   Their specified partner is not a registered MIND citizen
THEN:   System generates a personalized invitation link
AND:    Invitation explains Duo Mode value proposition (not generic MIND marketing)
AND:    Invitation includes the requesting partner's name (with consent)
AND:    Upon partner signup and biometric connection, DuoSession activates automatically
```

### B7: Historical Synchrony Patterns Accumulate

**Why:** Individual episodes are informative. Trends over weeks are transformative. Couples need to see whether their physiological co-regulation is improving, stable, or degrading.

```
GIVEN:  A DuoSession with at least 7 days of data
WHEN:   Either partner requests pattern summary, or weekly interval triggers
THEN:   System presents synchrony trend (average score, time in each phase, episode count)
AND:    Highlights improvement or regression relative to prior period
AND:    Does NOT interpret the trend (no "your relationship is getting worse")
```

### B8: Coach Sees Multiple DuoSession Scores

**Why:** Multi-Duo extends the engine to professional use. A coach needs a dashboard of all their client dyads, each showing current synchrony state without merging or comparing across dyads.

```
GIVEN:  A registered coach with a CoachSession containing N DuoSession children
WHEN:   Coach requests session overview
THEN:   System returns N independent synchrony scores and phases
AND:    Each DuoSession is isolated (no cross-dyad data leakage)
AND:    Coach can drill into any single DuoSession for full detail
```

### B9: Biometric Data Stays With Its Owner

**Why:** Privacy is non-negotiable. Raw biometric data belongs to the citizen who generated it. The synchrony layer computes correlation without exposing individual signals.

```
GIVEN:  Two partners in a DuoSession
WHEN:   Synchrony score is computed
THEN:   Each partner's raw HR, HRV, and stress data remains in their own MIND instance
AND:    Only the derived synchrony score and phase are shared
AND:    Partner A cannot query Partner B's raw biometric history through Duo Mode
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Viral acquisition | Strict 2-user requirement creates conversion at activation |
| B2 | Co-regulation loop | Synchrony score is the feedback signal for co-regulation |
| B3, B4 | Physiological awareness in conflict | Phase transitions translate biology into action |
| B5 | Co-regulation loop | Recovery reflection closes the learning loop |
| B6 | Viral acquisition | Invitation flow converts the conversion opportunity |
| B7 | Co-regulation loop | Longitudinal patterns show whether co-regulation is working |
| B8 | Professional coaching extension | Coach topology enables B2B revenue |
| B9 | Privacy (implicit in all objectives) | Trust in the system requires data sovereignty |

---

## INPUTS / OUTPUTS

### Primary Function: `compute_synchrony()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| hr_stream_a | List[float] | Heart rate samples from Partner A over rolling window |
| hr_stream_b | List[float] | Heart rate samples from Partner B over rolling window |
| hrv_stream_a | List[float] | HRV (RMSSD) samples from Partner A |
| hrv_stream_b | List[float] | HRV (RMSSD) samples from Partner B |
| window_seconds | int | Rolling window size (default 300s = 5 minutes) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| synchrony_score | int | 0-100, Pearson correlation mapped to percentage |
| phase | str | One of: BASELINE, DRIFT, DIVERGENCE, CRISIS, RECOVERY |
| phase_changed | bool | Whether this computation crossed a phase boundary |
| episode_duration | Optional[float] | Seconds in current sub-baseline phase, if applicable |

**Side Effects:**

- Phase transition triggers intervention message via chat pipeline
- Synchrony sample appended to DuoSession history for trend analysis

---

## EDGE CASES

### E1: One Partner's Wearable Disconnects

```
GIVEN:  Active DuoSession, one partner's biometric stream stops
THEN:   System marks that partner's data as stale after 120 seconds
AND:    Synchrony score computation pauses (does not extrapolate)
AND:    Both partners are notified: "Biometric connection lost for [Partner]. Synchrony paused."
AND:    Session remains active; score resumes when data returns
```

### E2: Partners Are In Different Time Zones

```
GIVEN:  Two partners in a DuoSession separated by time zones
THEN:   All timestamps are normalized to UTC internally
AND:    Biometric alignment uses UTC-synchronized sample windows
AND:    Intervention messages respect each partner's local time for delivery
```

### E3: Biometric Data Arrives At Different Rates

```
GIVEN:  Partner A's wearable sends HR at 1Hz, Partner B's at 0.2Hz
THEN:   System resamples both streams to a common frequency (lowest common)
AND:    Pearson correlation is computed on aligned, same-frequency samples
AND:    Score quality degrades gracefully with lower sample rates
```

### E4: DuoSession Activation During Active Crisis

```
GIVEN:  Partner A is already at elevated stress when Duo Mode activates
WHEN:   First synchrony score is computed
THEN:   System enters appropriate phase immediately (no mandatory Baseline period)
AND:    If initial score < 20, Crisis intervention fires within first computation cycle
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Content Mediation

```
GIVEN:   DuoSession is active during a conflict
WHEN:    MIND detects physiological divergence
MUST NOT: Suggest what the couple should discuss, who is right, or how to resolve the issue
INSTEAD:  Recommend timing action only (pause, breathe, resume later)
```

### A2: Asymmetric Information

```
GIVEN:   DuoSession is active
WHEN:    Synchrony score is computed
MUST NOT: Show different scores or phases to different partners
INSTEAD:  Both partners always see the same score and phase simultaneously
```

### A3: Score Extrapolation During Data Loss

```
GIVEN:   One partner's biometric stream has been stale for > 120 seconds
WHEN:    System is asked for current synchrony
MUST NOT: Extrapolate or predict the missing partner's state
INSTEAD:  Report "synchrony paused" with last known score and timestamp
```

### A4: Medical Interpretation

```
GIVEN:   A partner shows sustained HRV depression or elevated HR
WHEN:    MIND generates interventions
MUST NOT: Suggest medical conditions, diagnoses, or treatment
INSTEAD:  Frame observations purely as "your body's stress response is elevated"
```

### A5: Cross-Dyad Data Leakage in Multi-Duo

```
GIVEN:   A coach has N active DuoSessions
WHEN:    Coach views the dashboard
MUST NOT: Show any biometric data from Dyad A within Dyad B's view
INSTEAD:  Each DuoSession is fully isolated; coach sees N independent scores
```

---

## MARKERS

<!-- @mind:todo Define exact intervention message templates for each phase transition -->
<!-- @mind:escalation How does consent work for invitation flow? Can Partner A see that Partner B declined? Or only that they haven't joined yet? -->
<!-- @mind:proposition Consider "warm-up" behavior: first 5 minutes of a DuoSession should have a wider phase tolerance to avoid false-positive interventions during calibration -->
