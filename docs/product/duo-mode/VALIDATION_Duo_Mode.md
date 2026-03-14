# Duo Mode -- Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Duo_Mode.md
PATTERNS:        ./PATTERNS_Duo_Mode.md
BEHAVIORS:       ./BEHAVIORS_Duo_Mode.md
THIS:            VALIDATION_Duo_Mode.md (you are here)
ALGORITHM:       ./ALGORITHM_Duo_Mode.md
IMPLEMENTATION:  ./IMPLEMENTATION_Duo_Mode.md
SYNC:            ./SYNC_Duo_Mode.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, would mean Duo Mode has failed its purpose. A broken synchrony score means couples get wrong timing advice. A broken phase engine means MIND either nags when it shouldn't or stays silent when it should speak. A privacy violation destroys trust in the product.

---

## INVARIANTS

### V1: Session Requires Two Registered Citizens

**Why we care:** A DuoSession with a phantom partner produces meaningless synchrony scores. Worse, a single user could game the system by feeding fabricated biometric data for an imaginary partner.

```
MUST:   DuoSession.citizen_a_id and DuoSession.citizen_b_id both resolve to active citizens in L4 registry
MUST:   citizen_a_id != citizen_b_id
NEVER:  Create a DuoSession with a citizen_id that doesn't exist in registry
NEVER:  Create a DuoSession where both IDs are the same citizen
```

### V2: Synchrony Score Stays in [0, 100]

**Why we care:** Scores outside this range break the phase engine, confuse the UI, and produce nonsensical interventions.

```
MUST:   0 <= synchrony_score <= 100 for all computed scores
MUST:   synchrony_score is an integer
NEVER:  Return a score below 0 or above 100
NEVER:  Return a floating-point score to consumers (internal precision is float, external is int)
```

### V3: Phase Boundaries Are Deterministic

**Why we care:** If two identical biometric inputs produce different phases, the system is nondeterministic and untestable. Phase determination must be a pure function of (score, current_phase, timing).

```
MUST:   Same (score, current_phase, phase_entered_at) always produces same (new_phase, transition_fired)
MUST:   Phase thresholds match PhaseConfig exactly: BASELINE >= 60, DRIFT 40-59, DIVERGENCE 20-39, CRISIS < 20
NEVER:  Use random or probabilistic elements in phase determination
NEVER:  Allow external state (other sessions, network conditions) to influence phase computation
```

### V4: Hysteresis Prevents Oscillation

**Why we care:** A score oscillating at a boundary (e.g., 59/61) without hysteresis would cause phase transitions every computation cycle, flooding the user with contradictory interventions. MIND would feel broken.

```
MUST:   Downward transition (toward CRISIS) requires score < threshold - HYSTERESIS_BAND
MUST:   Upward transition (toward BASELINE) requires score > threshold + HYSTERESIS_BAND
MUST:   HYSTERESIS_BAND >= 3 (minimum meaningful margin with 0-100 scale)
NEVER:  Transition on exact threshold crossing without hysteresis margin
```

### V5: Minimum Dwell Prevents Rapid Transitions

**Why we care:** Even with hysteresis, a sharp physiological spike could trigger transitions faster than humans can read and process the intervention message.

```
MUST:   Phase transition suppressed if time_in_current_phase < MIN_DWELL_SECONDS
MUST:   MIN_DWELL_SECONDS >= 60 (absolute minimum for human processing)
NEVER:  Fire two phase transitions within MIN_DWELL_SECONDS of each other in the same session
```

### V6: Both Partners See Identical Score and Phase

**Why we care:** Asymmetric information between partners destroys trust. If Partner A sees "CRISIS" and Partner B sees "DRIFT," they're working from different realities during the most sensitive moments.

```
MUST:   At any point in time, both partners' views of the DuoSession show the same score and phase
MUST:   Intervention messages are identical for both partners
NEVER:  Show different scores, phases, or intervention text to different partners in the same session
```

### V7: Raw Biometric Data Stays Private

**Why we care:** Sharing raw HR/HRV data between partners without consent is a privacy violation. The synchrony score is the product -- it's derived, not raw.

```
MUST:   Partner A's raw BiometricSamples are never exposed to Partner B through any API
MUST:   Only derived data (synchrony_score, phase, episode_duration) is shared between partners
NEVER:  Return raw heart_rate, hrv_rmssd, or stress_index of one partner to the other
NEVER:  Store raw biometric data outside the owning citizen's MIND instance
```

### V8: Stale Data Pauses Score, Not Fabricates

**Why we care:** When one partner's biometric stream drops, the system could either extrapolate (guess) or pause. Guessing produces false confidence. Pausing is honest.

```
MUST:   If either partner's latest sample is older than STALE_THRESHOLD (120s), synchrony computation pauses
MUST:   Both partners are notified that synchrony is paused and why
MUST:   Last valid score is preserved (not cleared or zeroed) during pause
NEVER:  Extrapolate, interpolate, or predict biometric values for a disconnected partner
NEVER:  Continue phase transitions during data staleness
```

### V9: No Content Mediation

**Why we care:** MIND's value in Duo Mode is timing, not advice. If MIND starts suggesting what to say or who is right, it enters a domain where errors are relationship-damaging and liability is real.

```
MUST:   All intervention messages relate to timing (pause, breathe, resume, wait)
MUST:   Intervention messages reference physiological state, not relational content
NEVER:  Suggest what the couple should discuss
NEVER:  Attribute blame or take sides
NEVER:  Reference the content of the couple's conversation in interventions
```

### V10: Pearson Computation Is Numerically Stable

**Why we care:** Degenerate inputs (constant HR, single sample, all-zero arrays) must not produce NaN, Infinity, or crashes.

```
MUST:   If either aligned array has zero variance (constant values), return score = 0
MUST:   If aligned arrays have fewer than MIN_SAMPLES (10) elements, return INSUFFICIENT_DATA
NEVER:  Allow division by zero in Pearson denominator
NEVER:  Return NaN or Infinity as a synchrony score
```

### V11: DuoSession Isolation in Multi-Duo

**Why we care:** A coach viewing Dyad A's data must never see Dyad B's biometric information mixed in. Cross-contamination is both a privacy violation and a clinical risk.

```
MUST:   Each DuoSession has independent buffers, score, phase, and history
MUST:   CoachSession dashboard queries each DuoSession independently
NEVER:  Aggregate biometric data across DuoSessions
NEVER:  Allow a query on DuoSession X to return data from DuoSession Y
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable or dangerous |
| **HIGH** | Major value lost | Degraded severely, trust broken |
| **MEDIUM** | Partial value lost | Works but worse experience |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Session integrity | CRITICAL |
| V2 | Score bounds | CRITICAL |
| V3 | Phase determinism | CRITICAL |
| V4 | Transition stability | HIGH |
| V5 | Human processing time | HIGH |
| V6 | Partner symmetry | CRITICAL |
| V7 | Biometric privacy | CRITICAL |
| V8 | Honest uncertainty | HIGH |
| V9 | Scope discipline (timing only) | HIGH |
| V10 | Numerical stability | CRITICAL |
| V11 | Multi-Duo isolation | CRITICAL |

---

## MARKERS

<!-- @mind:todo V7 needs specific API-level enforcement plan: which endpoints exist, which must filter raw biometric fields -->
<!-- @mind:escalation V9 boundary: is it OK for Recovery phase to say "that episode lasted 12 minutes, which is shorter than last time"? That's pattern reflection, not content mediation, but it could feel like judgment -->
<!-- @mind:proposition V4 hysteresis band could be adaptive: wider band during first session (unfamiliar), narrower after 7+ sessions (calibrated) -->
