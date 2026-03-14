# Duo Mode -- Implementation: Code Architecture and Structure

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
ALGORITHM:       ./ALGORITHM_Duo_Mode.md
VALIDATION:      ./VALIDATION_Duo_Mode.md
THIS:            IMPLEMENTATION_Duo_Mode.md (you are here)
SYNC:            ./SYNC_Duo_Mode.md

IMPL:            mind-mcp/runtime/features/duo_mode/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-mcp/
├── runtime/
│   ├── features/
│   │   └── duo_mode/
│   │       ├── __init__.py                              # Public API: DuoSession, compute_synchrony, create_session
│   │       ├── biometric_stream_alignment_and_resampling.py   # Stream alignment, interpolation, common-rate resampling
│   │       ├── pearson_synchrony_score_computation.py         # Pearson correlation, score mapping [0-100]
│   │       ├── phase_engine_with_hysteresis_and_dwell.py      # 5-phase state machine, transitions, hysteresis
│   │       ├── duo_session_lifecycle_and_management.py        # Session creation, activation, pausing, ending
│   │       ├── intervention_message_generation.py             # Phase-transition message templates, timing recommendations
│   │       └── coach_session_multi_duo_topology.py            # CoachSession: 1 coach, N DuoSession children (v2)
│   ├── chat/
│   │   └── chat_routes.py                               # Existing chat infrastructure (integration point)
│   └── biometric/
│       └── ingestion.py                                 # Biometric data ingestion (dependency, not owned by Duo Mode)
├── tests/
│   └── features/
│       └── duo_mode/
│           ├── test_biometric_alignment_and_resampling.py
│           ├── test_pearson_synchrony_computation.py
│           ├── test_phase_engine_transitions_and_hysteresis.py
│           ├── test_duo_session_lifecycle.py
│           └── test_intervention_message_generation.py
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `biometric_stream_alignment_and_resampling.py` | Align two irregular biometric streams to common timestamps | `align_streams()`, `resample_to_common_rate()`, `linear_interpolate()` | ~120 | PLANNED |
| `pearson_synchrony_score_computation.py` | Compute Pearson r and map to 0-100 score | `pearson_r()`, `map_r_to_score()`, `compute_synchrony()` | ~80 | PLANNED |
| `phase_engine_with_hysteresis_and_dwell.py` | 5-phase state machine with transition logic | `PhaseEngine`, `determine_phase()`, `should_transition()` | ~150 | PLANNED |
| `duo_session_lifecycle_and_management.py` | Create, activate, pause, end sessions | `DuoSession`, `create_session()`, `end_session()`, `pause_session()` | ~200 | PLANNED |
| `intervention_message_generation.py` | Generate timing-based intervention messages | `generate_intervention()`, `PHASE_TEMPLATES` | ~100 | PLANNED |
| `coach_session_multi_duo_topology.py` | Multi-Duo topology for professional use | `CoachSession`, `create_coach_session()`, `get_dashboard()` | ~120 | PLANNED (v2) |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline (stream processing) + State Machine (phase engine)

**Why this pattern:** Biometric data flows through a pipeline (align -> correlate -> score -> phase). The phase engine is a classic state machine with transition rules. This separation means the pipeline is stateless and testable, while the state machine owns all temporal logic.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Pipeline | `align_streams -> pearson_r -> map_r_to_score` | Stateless transformations, each function is independently testable |
| State Machine | `PhaseEngine` | Phase transitions with hysteresis, minimum dwell, recovery detection |
| Template Method | `generate_intervention()` | Message generation varies by phase transition type, common structure |
| Observer | `DuoSession.on_phase_change` | Decouple phase transitions from intervention delivery |

### Anti-Patterns to Avoid

- **God Session**: Don't let DuoSession handle alignment, correlation, phase logic, AND message generation. Each is a separate module with a clear responsibility boundary.
- **Mutable Pipeline**: Keep the pipeline functions pure. State lives in DuoSession and PhaseEngine, not in the alignment or correlation functions.
- **Fallback Scores**: If data is insufficient or stale, return INSUFFICIENT_DATA or PAUSED. Never return a "best guess" score. (See PRINCIPLES: no fallbacks.)

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Duo Mode feature | Synchrony computation, phase engine, interventions | Biometric ingestion, chat delivery, registry | `compute_synchrony(session_id)`, `create_session(citizen_a, citizen_b)` |
| Session management | Lifecycle, buffers, history | Persistence layer, auth | `DuoSession` dataclass |
| Phase engine | Transition logic, hysteresis | Score computation, message generation | `PhaseEngine.update(score) -> (phase, changed)` |

---

## SCHEMA

### DuoSession

```yaml
DuoSession:
  required:
    - session_id: str           # UUID
    - citizen_a_id: str         # SID, must exist in L4 registry
    - citizen_b_id: str         # SID, must exist in L4 registry
    - status: str               # ACTIVE | PAUSED | ENDED
    - current_phase: str        # BASELINE | DRIFT | DIVERGENCE | CRISIS | RECOVERY
    - current_score: int        # 0-100
  optional:
    - phase_entered_at: float   # Unix epoch
    - created_at: float         # Unix epoch
    - ended_at: float           # Unix epoch, set when status -> ENDED
  constraints:
    - citizen_a_id != citizen_b_id
    - 0 <= current_score <= 100
    - status transitions: ACTIVE -> PAUSED -> ACTIVE, ACTIVE -> ENDED, PAUSED -> ENDED
```

### PhaseTransition Event

```yaml
PhaseTransition:
  required:
    - session_id: str
    - from_phase: str
    - to_phase: str
    - score: int
    - timestamp: float
  relationships:
    - triggers: InterventionMessage
```

---

## ENTRY POINTS

| Entry Point | File:Function | Triggered By |
|-------------|---------------|--------------|
| Session creation | `duo_session_lifecycle_and_management.py:create_session()` | User activates Duo Mode |
| Score computation | `pearson_synchrony_score_computation.py:compute_synchrony()` | New biometric sample arrives |
| Phase update | `phase_engine_with_hysteresis_and_dwell.py:PhaseEngine.update()` | Score computed |
| Intervention delivery | `intervention_message_generation.py:generate_intervention()` | Phase transition fires |
| Coach dashboard | `coach_session_multi_duo_topology.py:get_dashboard()` | Coach requests overview |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Synchrony Computation Cycle

This is the core flow. Runs every time a new biometric sample arrives. Transforms raw samples into a synchrony score and potentially a phase transition with intervention.

```yaml
flow:
  name: synchrony_computation
  purpose: Transform biometric samples into synchrony score and phase-driven interventions
  scope: From biometric sample arrival to intervention delivery
  steps:
    - id: ingest_sample
      description: New biometric sample received from wearable via ingestion layer
      file: runtime/biometric/ingestion.py
      function: on_sample()
      input: BiometricSample
      output: buffered sample in citizen's stream
      trigger: Wearable API push
      side_effects: Sample added to DuoSession buffer

    - id: align_streams
      description: Align both partners' buffers to common timestamps
      file: runtime/features/duo_mode/biometric_stream_alignment_and_resampling.py
      function: align_streams()
      input: buffer_a, buffer_b, window_seconds
      output: aligned_a[], aligned_b[]
      trigger: Called by compute_synchrony
      side_effects: None (pure function)

    - id: compute_pearson
      description: Compute Pearson correlation and map to 0-100 score
      file: runtime/features/duo_mode/pearson_synchrony_score_computation.py
      function: compute_synchrony()
      input: aligned_a[], aligned_b[]
      output: synchrony_score (int 0-100)
      trigger: Called after alignment
      side_effects: None (pure function)

    - id: update_phase
      description: Feed score into phase engine, check for transition
      file: runtime/features/duo_mode/phase_engine_with_hysteresis_and_dwell.py
      function: PhaseEngine.update()
      input: synchrony_score
      output: (phase, phase_changed)
      trigger: Called after score computation
      side_effects: PhaseEngine internal state updated

    - id: generate_intervention
      description: If phase changed, produce intervention message
      file: runtime/features/duo_mode/intervention_message_generation.py
      function: generate_intervention()
      input: phase, previous_phase, score, episode_duration
      output: InterventionMessage
      trigger: phase_changed == True
      side_effects: None (pure function)

    - id: deliver_intervention
      description: Send intervention to both partners via chat
      file: runtime/chat/chat_routes.py
      function: send_duo_intervention()
      input: session_id, InterventionMessage
      output: delivery confirmation
      trigger: InterventionMessage generated
      side_effects: Message appears in both partners' chat

  docking_points:
    guidance:
      include_when: Transformation boundary, privacy boundary, state mutation
      omit_when: Pure function internals
      selection_notes: Focus on where data crosses module boundaries and where state changes
    available:
      - id: dock_sample_ingest
        type: event
        direction: input
        file: runtime/biometric/ingestion.py
        function: on_sample()
        trigger: Wearable API push
        payload: BiometricSample
        async_hook: required
        needs: add async hook
        notes: Entry point from external wearable data

      - id: dock_alignment_output
        type: custom
        direction: output
        file: runtime/features/duo_mode/biometric_stream_alignment_and_resampling.py
        function: align_streams()
        trigger: compute_synchrony call
        payload: aligned_a[], aligned_b[]
        async_hook: not_applicable
        needs: none
        notes: Pure function boundary, useful for verifying alignment quality

      - id: dock_score_output
        type: custom
        direction: output
        file: runtime/features/duo_mode/pearson_synchrony_score_computation.py
        function: compute_synchrony()
        trigger: align_streams result
        payload: synchrony_score (int 0-100)
        async_hook: not_applicable
        needs: none
        notes: Core score output, critical for V2 and V10 verification

      - id: dock_phase_transition
        type: event
        direction: output
        file: runtime/features/duo_mode/phase_engine_with_hysteresis_and_dwell.py
        function: PhaseEngine.update()
        trigger: score update
        payload: PhaseTransition event
        async_hook: optional
        needs: add event emitter
        notes: State mutation point, drives intervention delivery

      - id: dock_intervention_delivery
        type: api
        direction: output
        file: runtime/chat/chat_routes.py
        function: send_duo_intervention()
        trigger: phase transition
        payload: InterventionMessage
        async_hook: required
        needs: add chat route
        notes: Crosses into chat infrastructure, both partners must receive simultaneously

    health_recommended:
      - dock_id: dock_score_output
        reason: Score bounds (V2) and numerical stability (V10) must be verified at this point
      - dock_id: dock_phase_transition
        reason: Phase determinism (V3), hysteresis (V4), and dwell (V5) verified here
      - dock_id: dock_intervention_delivery
        reason: Symmetry (V6) verified -- both partners receive same content
```

### Flow 2: Session Lifecycle

Covers creation, activation, pausing, and ending of DuoSessions. Lower frequency but critical for V1 (session integrity).

```yaml
flow:
  name: session_lifecycle
  purpose: Manage DuoSession creation and state transitions
  scope: From user request to session state change
  steps:
    - id: validate_citizens
      description: Verify both citizens exist in L4 registry
      file: runtime/features/duo_mode/duo_session_lifecycle_and_management.py
      function: create_session()
      input: citizen_a_id, citizen_b_id
      output: validated citizen pair
      trigger: User API request
      side_effects: Registry query

    - id: create_session
      description: Instantiate DuoSession with ACTIVE status
      file: runtime/features/duo_mode/duo_session_lifecycle_and_management.py
      function: create_session()
      input: validated citizen pair
      output: DuoSession
      trigger: Validation passes
      side_effects: Session stored in persistence layer
```

---

## LOGIC CHAINS

### LC1: Sample to Intervention

**Purpose:** End-to-end flow from biometric sample arrival to intervention delivery.

```
BiometricSample
  -> ingestion.on_sample()              # Buffer the sample
    -> align_streams(buf_a, buf_b)      # Align to common timestamps
      -> compute_synchrony(aligned)     # Pearson r -> score 0-100
        -> PhaseEngine.update(score)    # Phase transition check
          -> generate_intervention()    # Message template
            -> send_duo_intervention()  # Deliver via chat
```

**Data transformation:**
- Input: `BiometricSample` -- raw (timestamp, HR, HRV, stress) from one partner
- After alignment: `float[]` -- equal-length HR arrays for both partners
- After correlation: `int` -- synchrony score 0-100
- After phase engine: `(str, bool)` -- (phase, changed)
- Output: `InterventionMessage` -- text delivered to both partners

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
duo_session_lifecycle_and_management
    └── imports -> phase_engine_with_hysteresis_and_dwell
    └── imports -> pearson_synchrony_score_computation
        └── imports -> biometric_stream_alignment_and_resampling
    └── imports -> intervention_message_generation

coach_session_multi_duo_topology
    └── imports -> duo_session_lifecycle_and_management
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `math` (stdlib) | sqrt for Pearson denominator | `pearson_synchrony_score_computation.py` |
| `collections.deque` (stdlib) | Rolling buffer for biometric samples | `duo_session_lifecycle_and_management.py` |
| `uuid` (stdlib) | Session ID generation | `duo_session_lifecycle_and_management.py` |
| `dataclasses` (stdlib) | DuoSession, BiometricSample, PhaseTransition | multiple files |

No external (pip) dependencies. Duo Mode core is pure Python with stdlib only.

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Biometric buffers | `DuoSession.buffer_a`, `DuoSession.buffer_b` | Per-session | Created at session start, cleared at session end |
| Phase state | `PhaseEngine` (inside DuoSession) | Per-session | Created at session start, updated on each score computation |
| Session registry | Persistence layer (TBD) | Global | Created on activation, persisted until explicit deletion |
| Score history | `DuoSession.history` | Per-session | Grows during session, aggregated periodically |

### State Transitions

```
CREATED ──activate──> ACTIVE ──pause──> PAUSED ──resume──> ACTIVE
                        │                   │
                        └──end──> ENDED <──end──┘
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. User requests Duo Mode activation with partner_id
2. System verifies both citizens in L4 registry
3. If partner is not MIND user: return invitation flow
4. If partner is MIND user: create DuoSession(ACTIVE)
5. Initialize PhaseEngine with BASELINE phase
6. Begin buffering biometric samples from both partners
7. First score computed after MIN_SAMPLES (10) accumulated from both
```

### Main Loop / Request Cycle

```
1. Biometric sample arrives from either partner (event-driven, not polled)
2. Sample buffered in appropriate deque
3. If both buffers have >= MIN_SAMPLES:
   a. align_streams()
   b. compute_synchrony()
   c. PhaseEngine.update(score)
   d. If phase_changed: generate_intervention() -> send_duo_intervention()
   e. Append (timestamp, score, phase) to history
4. Return current (score, phase) to any polling clients
```

### Shutdown

```
1. Either partner ends session, or session times out
2. DuoSession.status -> ENDED
3. Final history snapshot persisted
4. Biometric buffers cleared (privacy: don't retain raw data)
5. PhaseEngine state cleared
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Biometric ingestion | async (event-driven) | Samples arrive asynchronously from wearable APIs |
| Score computation | sync (per-event) | Triggered by sample arrival, fast enough for sync execution |
| Phase engine | sync (lock-protected) | State machine must be updated atomically, no concurrent transitions |
| Intervention delivery | async | Chat delivery is I/O-bound, fire-and-forget with confirmation |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `WINDOW_SECONDS` | duo_mode config | `300` | Rolling window for Pearson computation (5 minutes) |
| `HYSTERESIS_BAND` | PhaseConfig | `5` | Points of margin required for phase transition |
| `MIN_DWELL_SECONDS` | PhaseConfig | `120` | Minimum time in a phase before transition allowed |
| `STALE_THRESHOLD_SECONDS` | duo_mode config | `120` | Time after which biometric data is considered stale |
| `MIN_SAMPLES` | duo_mode config | `10` | Minimum aligned samples required for Pearson computation |

---

## MARKERS

<!-- @mind:todo Persistence layer for DuoSession: graph node (space type?) or separate store? Decide before implementation. -->
<!-- @mind:todo Integration with existing chat_routes.py: identify the exact hook point for send_duo_intervention() -->
<!-- @mind:proposition DuoSession as a graph SpaceNode with links to both citizen ActorNodes -- fits Mind Protocol universal schema -->
