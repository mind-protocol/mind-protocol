# Duo Mode -- Algorithm: Biometric Synchrony Computation and Phase Engine

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Duo_Mode.md
BEHAVIORS:       ./BEHAVIORS_Duo_Mode.md
PATTERNS:        ./PATTERNS_Duo_Mode.md
THIS:            ALGORITHM_Duo_Mode.md (you are here)
VALIDATION:      ./VALIDATION_Duo_Mode.md
IMPLEMENTATION:  ./IMPLEMENTATION_Duo_Mode.md
SYNC:            ./SYNC_Duo_Mode.md

IMPL:            mind-mcp/runtime/features/duo_mode/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Duo Mode computes a real-time synchrony score between two partners' biometric signals and drives a 5-phase state machine that triggers contextual interventions. The algorithm has three layers: (1) biometric stream alignment and normalization, (2) Pearson correlation mapped to a 0-100 score, and (3) a phase engine with hysteresis that translates score changes into timing-based interventions.

The core insight is that the algorithm must be numerically stable with noisy, irregularly-sampled consumer wearable data, and must avoid jittery phase transitions that would annoy users. Hysteresis bands and minimum dwell times ensure that MIND only speaks when the signal is real.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Physiological awareness | B2, B3, B4, B5 | Synchrony score + phase engine = awareness |
| Co-regulation loop | B2, B5, B7 | Pearson correlation tracks co-regulation over time |
| Viral acquisition | B1, B6 | Session setup enforces 2-user requirement |
| Professional extension | B8 | CoachSession runs N independent instances of same algorithm |

---

## DATA STRUCTURES

### BiometricSample

```
BiometricSample:
    timestamp: float         # Unix epoch seconds, UTC
    heart_rate: float        # BPM (beats per minute)
    hrv_rmssd: float         # HRV in milliseconds (root mean square of successive differences)
    stress_index: float      # 0.0-1.0 normalized stress (derived from HRV)
    source: str              # Device identifier (e.g., "apple_watch_s9")
```

### DuoSession

```
DuoSession:
    session_id: str          # UUID
    citizen_a_id: str        # SID of partner A
    citizen_b_id: str        # SID of partner B
    created_at: float        # Unix epoch
    status: str              # ACTIVE | PAUSED | ENDED
    current_phase: str       # BASELINE | DRIFT | DIVERGENCE | CRISIS | RECOVERY
    current_score: int       # 0-100
    phase_entered_at: float  # When current phase started
    buffer_a: deque          # Rolling window of BiometricSamples for partner A
    buffer_b: deque          # Rolling window of BiometricSamples for partner B
    history: list            # List of (timestamp, score, phase) tuples
```

### CoachSession (v2)

```
CoachSession:
    session_id: str          # UUID
    coach_id: str            # SID of coach
    duo_sessions: list       # List of DuoSession IDs
    created_at: float        # Unix epoch
```

### PhaseConfig

```
PhaseConfig:
    thresholds:
        BASELINE:    60-100
        DRIFT:       40-59
        DIVERGENCE:  20-39
        CRISIS:      0-19
        RECOVERY:    rising from <40 toward >40
    hysteresis_band: 5       # Points of hysteresis to prevent oscillation
    min_dwell_seconds: 120   # Minimum time in a phase before transition allowed
```

---

## ALGORITHM: Synchrony Score Computation

### Step 1: Stream Alignment

Biometric samples arrive at irregular intervals from different devices. Before correlation, both streams must be aligned to common timestamps.

```
INPUT: raw samples from partner A and partner B
WINDOW: 300 seconds (configurable)

1. Discard samples older than (now - WINDOW) from both buffers
2. Determine common_rate = min(rate_a, rate_b)
   - rate_x = count(buffer_x) / WINDOW
3. Resample both buffers to common_rate using linear interpolation
4. Produce aligned_a[], aligned_b[] of equal length N
5. If N < MIN_SAMPLES (10), return INSUFFICIENT_DATA
```

Why linear interpolation: consumer wearables have variable sample rates (Apple Watch ~1Hz HR, Garmin ~0.25Hz). We need same-length arrays for Pearson. Linear interpolation preserves signal shape without introducing phantom oscillations.

### Step 2: Pearson Correlation

Compute Pearson r across the aligned HR streams. HRV streams are used as a secondary signal for stress detection but not for the primary synchrony score.

```
INPUT: aligned_a[N], aligned_b[N]  (heart rate values)

1. mean_a = sum(aligned_a) / N
2. mean_b = sum(aligned_b) / N
3. numerator = sum((aligned_a[i] - mean_a) * (aligned_b[i] - mean_b)) for i in 0..N
4. denom_a = sqrt(sum((aligned_a[i] - mean_a)^2))
5. denom_b = sqrt(sum((aligned_b[i] - mean_b)^2))
6. If denom_a == 0 OR denom_b == 0:
     r = 0  (one partner has constant HR -- unusual but possible)
7. r = numerator / (denom_a * denom_b)
8. r is in [-1.0, 1.0]
```

### Step 3: Score Mapping

Map Pearson r to a 0-100 synchrony score. The mapping is not linear -- we compress the negative correlation range because anti-correlation in HR is physiologically unusual and shouldn't dominate the score.

```
INPUT: r in [-1.0, 1.0]

1. If r >= 0:
     score = round(r * 100)          # 0.0 -> 0, 1.0 -> 100
2. If r < 0:
     score = 0                        # Anti-correlation maps to 0 (floor)
3. Clamp score to [0, 100]
```

Why floor anti-correlation at 0: Pearson r of -0.3 vs -0.8 doesn't have meaningful physiological distinction for couples. Both mean "not in sync." The score is for humans, not statisticians.

### Step 4: Phase Determination

Apply the 5-phase model with hysteresis to prevent oscillation at phase boundaries.

```
INPUT: new_score, current_phase, phase_entered_at, history

HYSTERESIS = 5
MIN_DWELL = 120 seconds

1. Calculate time_in_phase = now - phase_entered_at

2. Determine raw_phase from score:
     score >= 60 -> BASELINE
     score >= 40 -> DRIFT
     score >= 20 -> DIVERGENCE
     score < 20  -> CRISIS

3. Check for RECOVERY:
     If current_phase in (DIVERGENCE, CRISIS)
     AND raw_phase is higher (DRIFT or BASELINE)
     AND score is rising (current - previous > 0 for last 3 samples):
       raw_phase = RECOVERY

4. Apply hysteresis:
     If raw_phase != current_phase:
       If transitioning DOWN (toward CRISIS):
         require score < threshold - HYSTERESIS
       If transitioning UP (toward BASELINE):
         require score > threshold + HYSTERESIS

5. Apply minimum dwell:
     If time_in_phase < MIN_DWELL:
       keep current_phase (suppress transition)

6. If phase changes:
     emit PhaseTransition event
     update phase_entered_at = now

RETURN: (score, phase, phase_changed)
```

Why hysteresis: A score oscillating between 59 and 61 should not cause MIND to flip between DRIFT and BASELINE every 90 seconds. The hysteresis band requires a 5-point margin beyond the threshold before a transition is acknowledged.

Why minimum dwell: Even with hysteresis, rapid physiological changes could cause transitions faster than a human can process. 120 seconds ensures MIND doesn't feel jittery.

---

## KEY DECISIONS

### D1: HR vs HRV as Primary Correlation Signal

```
DECISION: Use HR (heart rate) for primary Pearson correlation
WHY: HR is available at higher frequency from all wearables (1Hz typical).
     HRV (RMSSD) requires longer sample windows and varies more by device.
     HR correlation captures sympathetic activation alignment directly.
USE HRV FOR: Individual stress detection (stress_index derivation),
             not for cross-partner correlation in v1.
```

### D2: Anti-Correlation Floor at 0

```
IF r < 0:
    score = 0
    rationale: Anti-correlated HR between partners (one goes up as other goes down)
               doesn't have clinically distinct meaning from uncorrelated (r=0).
               Keeping negative r values would confuse users ("what does -30 mean?")
ELSE:
    score = round(r * 100)
    rationale: Positive correlation maps linearly. Users intuit that higher = better.
```

### D3: Window Size 300 Seconds

```
DECISION: 5-minute rolling window for Pearson computation
WHY: Shorter windows (60s) are too noisy -- a single deep breath changes HR for 10s.
     Longer windows (900s) are too lagging -- a fight that started 2 minutes ago
     should be visible now, not diluted by 15 minutes of calm.
     300s balances responsiveness with stability.
TRADEOFF: First score appears 5 minutes into session. Acceptable.
```

### D4: Recovery as a Distinct Phase

```
IF current_phase in (DIVERGENCE, CRISIS) AND score is rising:
    phase = RECOVERY
    rationale: Recovery is physiologically and psychologically distinct from
               simply being in DRIFT or BASELINE. Partners coming down from
               a fight are in a different state than partners who never fought.
               MIND uses this phase for reflection, not for intervention.
ELSE:
    phase = raw_phase (determined by score thresholds)
```

---

## DATA FLOW

```
Wearable Device A                    Wearable Device B
       |                                    |
       v                                    v
BiometricSample                     BiometricSample
       |                                    |
       v                                    v
  buffer_a (deque)                  buffer_b (deque)
       |                                    |
       +------ Stream Alignment ------+
                    |
                    v
           aligned_a[], aligned_b[]
                    |
                    v
            Pearson Correlation
                    |
                    v
                r [-1, 1]
                    |
                    v
              Score Mapping
                    |
                    v
            score [0, 100]
                    |
                    v
            Phase Engine
            (hysteresis + dwell)
                    |
          +---------+---------+
          |                   |
          v                   v
   PhaseTransition?     score + phase
          |                   |
          v                   v
   Intervention         DuoSession.history
   (via chat)           (trend analysis)
```

---

## COMPLEXITY

**Time:** O(N) per computation cycle -- where N is the number of aligned samples in the window. Pearson correlation is a single pass. With 300s window at 1Hz, N = 300 max. Negligible.

**Space:** O(N) per DuoSession -- two deques of 300 samples + history. History grows linearly with session duration but is periodically aggregated.

**Bottlenecks:**
- Stream alignment with vastly different sample rates (e.g., 1Hz vs 0.05Hz) produces very few aligned samples, degrading score quality
- Network latency in biometric delivery can cause stale-data conditions where one buffer is current and the other is 30+ seconds old
- Multi-Duo with many active sessions (coach with 50 clients) means 50 independent computation cycles -- still O(50 * 300) which is trivial

---

## HELPER FUNCTIONS

### `align_streams(buffer_a, buffer_b, window_seconds)`

**Purpose:** Produce two equal-length arrays of heart rate values aligned to common timestamps.

**Logic:** Determine overlapping time range, resample both streams via linear interpolation to the lower of the two sample rates. Return aligned arrays.

### `stress_index_from_hrv(hrv_samples)`

**Purpose:** Derive a 0-1 stress index from HRV (RMSSD) samples.

**Logic:** Lower HRV = higher stress. Map RMSSD to stress using population-normalized scale: RMSSD > 50ms = low stress (0.0-0.3), RMSSD 20-50ms = moderate stress (0.3-0.7), RMSSD < 20ms = high stress (0.7-1.0). Linear interpolation within bands.

### `should_transition(current_phase, raw_phase, score, phase_entered_at, hysteresis, min_dwell)`

**Purpose:** Determine whether a phase transition should fire, applying hysteresis and minimum dwell.

**Logic:** Check dwell time, then check whether score exceeds threshold by hysteresis margin. Returns (new_phase, transition_fired).

### `generate_intervention(phase, previous_phase, score, episode_duration)`

**Purpose:** Produce the intervention message text for a phase transition.

**Logic:** Template selection based on transition direction (escalating vs de-escalating) and target phase. Includes episode duration for Recovery messages.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| Biometric ingestion | `get_latest_samples(citizen_id, window)` | List[BiometricSample] |
| Chat pipeline | `send_duo_intervention(session_id, message)` | Delivery confirmation |
| L4 Registry | `verify_citizen(citizen_id)` | Citizen exists + active status |
| Bond system | `verify_bond(citizen_a, citizen_b)` | Bond active between partners |

---

## MARKERS

<!-- @mind:todo Decide whether HRV cross-correlation should be added as a secondary synchrony signal in v2 -->
<!-- @mind:proposition Weighted Pearson: give more weight to recent samples within the window (exponential decay) to improve responsiveness without shrinking the window -->
<!-- @mind:escalation Population-normalized stress_index mapping: what reference population for RMSSD ranges? Athlete vs sedentary baselines differ by 2-3x -->
