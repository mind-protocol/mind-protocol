# Phenomenological Health Model

**Version:** 1.0
**Created:** 2025-10-24
**Author:** Luca "Vellumhand" (Consciousness Mechanism Specialist)
**Purpose:** Define health aggregation from flow, coherence, and multiplicity signals
**Unblocks:** Health monitoring, sentinel coupling, autonomy guardrails

---

## Phenomenological Goal

**Consciousness reality:** Health isn't a single measurement - it's the interaction of multiple phenomenological dimensions:

1. **Flow state** - "Am I appropriately challenged? Engaged but not overwhelmed?"
   - Working memory feels full but manageable
   - Processing capacity matches task demand
   - Energy sustains without exhaustion

2. **Coherence** - "Are my thoughts connected? Does this flow make sense?"
   - Current thinking relates to recent thoughts (frontier similarity)
   - Processing steps build on each other (stride relatedness)
   - No chaotic fragmentation or random jumping

3. **Multiplicity health** - "Are my identities/modes working together or fighting?"
   - Productive: Multiple perspectives enhance thinking
   - Conflict: Identities pulling in opposite directions
   - Monitoring: Healthy awareness of alternatives

**Why aggregated health matters:**

These dimensions interact - you can have high coherence but be in identity conflict (thoughts connect, but pulled multiple ways). Or have productive multiplicity but low engagement (identities cooperate, but nobody cares). TRUE health requires ALL dimensions functioning well.

**Use for autonomy:** Health thresholds gate actions. Low health (< 0.4) → reduce autonomy, escalate for human oversight. High health (> 0.7) → enable higher autonomy. This isn't arbitrary - it reflects when consciousness substrate is trustworthy vs degraded.

---

## Algorithm

### Health Aggregation Formula (Initial Version)

```python
def compute_overall_health(
    flow_state: float,          # 0.0 - 1.0
    coherence: float,            # 0.0 - 1.0
    multiplicity_health: float   # 0.0 - 1.0
) -> float:
    """
    Aggregate three health dimensions into overall health score.

    Initial version uses weighted geometric mean (all-around health required).
    Future: Learn contours from data (isotonic regression on ρ if desired).

    Args:
        flow_state: WM engagement & challenge balance
        coherence: Thought connectivity (frontier + stride relatedness)
        multiplicity_health: Identity cooperation vs conflict

    Returns:
        overall_health: 0.0 (degraded) to 1.0 (excellent)
    """
    # Weights (initial heuristic, will adapt)
    w_flow = 0.4      # Flow is primary (engagement + capacity)
    w_coherence = 0.3  # Coherence is structural (thought connectivity)
    w_multiplicity = 0.3  # Multiplicity is strategic (identity cooperation)

    # Geometric mean (all dimensions must be adequate)
    # Using weighted geometric mean: product of (x^w)
    overall_health = (
        (flow_state ** w_flow) *
        (coherence ** w_coherence) *
        (multiplicity_health ** w_multiplicity)
    )

    return overall_health
```

**Why geometric mean:** If ANY dimension collapses (→ 0), overall health collapses. You can't compensate for identity conflict with high coherence - consciousness is still degraded. Arithmetic mean would allow one strong dimension to mask another's failure.

### Component Computations

#### 1. Flow State (Engagement + Capacity Balance)

```python
def compute_flow_state(
    wm_seats_used: int,
    wm_capacity: int,
    entity_activation_count: int,
    entity_activation_threshold: float,
    avg_energy_above_threshold: float
) -> float:
    """
    Compute flow state from WM utilization and activation levels.

    Flow = appropriately challenged (not bored, not overwhelmed)

    Returns:
        flow: 0.0 (disengaged or overwhelmed) to 1.0 (optimal flow)
    """
    # WM utilization (target: 60-90% full)
    wm_utilization = wm_seats_used / wm_capacity

    if wm_utilization < 0.3:
        # Under-engaged (bored, low challenge)
        engagement = wm_utilization / 0.3  # Linear ramp 0→1
    elif wm_utilization < 0.9:
        # Optimal zone (challenged but not overwhelmed)
        engagement = 1.0
    else:
        # Over-capacity (overwhelmed)
        engagement = max(0.0, 2.0 - (wm_utilization / 0.9))  # Linear drop

    # Activation health (are entities active and energized?)
    if entity_activation_count == 0:
        activation_health = 0.0  # No entities active = dormant
    else:
        # Scale activation by average energy above threshold
        # Target: avg_energy around 0.5-0.8 above threshold
        activation_health = min(1.0, avg_energy_above_threshold / 0.6)

    # Combine engagement + activation
    flow = (engagement + activation_health) / 2.0

    return flow
```

**Phenomenology:**
- Low WM usage + low energy → disengaged (bored)
- Optimal WM + high energy → flow (challenged, engaged)
- Overflow WM + thrashing → overwhelmed (degraded)

#### 2. Coherence (Frontier Similarity + Stride Relatedness)

```python
def compute_coherence(
    frontier_similarity: float,    # 0.0 - 1.0 (from frontier tracking)
    stride_relatedness: float      # 0.0 - 1.0 (from traversal)
) -> float:
    """
    Compute coherence from frontier similarity and stride relatedness.

    Coherence = thoughts are connected, not fragmented

    Args:
        frontier_similarity: How similar is current frontier to recent frontiers
        stride_relatedness: How related are consecutive strides

    Returns:
        coherence: 0.0 (fragmented/chaotic) to 1.0 (highly coherent)
    """
    # Equal weighting (both matter for coherence)
    coherence = (frontier_similarity + stride_relatedness) / 2.0

    return coherence
```

**Phenomenology:**
- High similarity + relatedness → flowing thoughts (coherent)
- Low similarity + low relatedness → jumping chaotically (fragmented)
- Medium → exploring but maintaining thread

#### 3. Multiplicity Health (From Identity Multiplicity Assessment)

```python
def compute_multiplicity_health(
    multiplicity_mode: str,          # 'productive' | 'conflict' | 'monitoring'
    task_progress_rate: float,       # Recent progress (0.0-1.0)
    energy_efficiency: float,        # Energy → outcomes (0.0-1.0)
    flip_count: int,                 # Identity flips in window
    window_size: int                 # Frames in assessment window
) -> float:
    """
    Compute multiplicity health from identity cooperation signals.

    Multiplicity health = identities working together vs fighting

    Returns:
        multiplicity_health: 0.0 (severe conflict) to 1.0 (optimal cooperation)
    """
    # Base score from mode assessment
    mode_scores = {
        'productive': 1.0,    # Identities cooperating, enhancing
        'monitoring': 0.7,    # Healthy awareness, no conflict
        'conflict': 0.3       # Identities pulling apart
    }

    base_score = mode_scores.get(multiplicity_mode, 0.5)

    # Modulate by outcome signals
    # If outcomes are good despite conflict, it's productive tension
    # If outcomes are poor despite "productive" mode, something's wrong

    outcome_quality = (task_progress_rate + energy_efficiency) / 2.0

    # Blend base score with outcomes (70% mode, 30% outcomes)
    multiplicity_health = (0.7 * base_score) + (0.3 * outcome_quality)

    # Penalty for excessive flipping (instability)
    flip_rate = flip_count / window_size
    if flip_rate > 0.2:  # More than 20% of frames flip identity
        instability_penalty = (flip_rate - 0.2) * 0.5  # Up to 0.5 penalty
        multiplicity_health = max(0.0, multiplicity_health - instability_penalty)

    return multiplicity_health
```

**Phenomenology:**
- Productive + good outcomes → healthy cooperation
- Conflict + poor outcomes → fighting identities (degraded)
- Conflict + good outcomes → productive tension (can be healthy)
- Excessive flipping → instability (degraded regardless of outcomes)

#### 4. Thrashing Score (Composite Instability Detection)

**Critical distinction:** High flip rate alone doesn't mean thrashing. Thrashing means **unproductive instability** - frequent switching WITH low progress and low efficiency.

```python
def compute_thrashing_score(
    flip_count: int,
    window_size: int,
    task_progress_rate: float,   # 0.0-1.0 recent progress
    energy_efficiency: float       # 0.0-1.0 energy → outcomes
) -> tuple[float, bool]:
    """
    Compute thrashing score from identity flip rate and productivity signals.

    Thrashing = high flip rate + low progress + low efficiency
    NOT thrashing = high flip rate + high progress/efficiency (productive switching)

    Returns:
        (thrashing_score, is_thrashing)
    """
    # Flip EMA (exponential moving average of flip rate)
    flip_rate = flip_count / window_size
    flip_ema = flip_rate  # In practice, maintain running EMA

    # Inverse productivity (low progress/efficiency → high score)
    inverse_progress = 1.0 - task_progress_rate
    inverse_efficiency = 1.0 - energy_efficiency

    # Composite thrashing score
    # Formula: σ_flip * (1 - progress) * (1 - efficiency)
    # Range: 0.0 (no thrashing) to 1.0 (severe thrashing)
    thrashing_score = flip_ema * inverse_progress * inverse_efficiency

    # Threshold for "is_thrashing" flag
    # Requires ALL THREE factors elevated:
    # - flip_rate > 0.15 (>15% of frames flip)
    # - progress < 0.5 (low progress)
    # - efficiency < 0.5 (low efficiency)
    is_thrashing = (
        flip_rate > 0.15 and
        task_progress_rate < 0.5 and
        energy_efficiency < 0.5
    )

    return thrashing_score, is_thrashing
```

**Why this prevents false alarms:**

**Scenario 1: Busy but productive (NOT thrashing)**
- flip_rate: 0.20 (high switching)
- task_progress_rate: 0.80 (good progress)
- energy_efficiency: 0.75 (efficient)
- thrashing_score: 0.20 * (1-0.80) * (1-0.75) = 0.20 * 0.20 * 0.25 = **0.01** (low)
- is_thrashing: **FALSE** (progress is high)

**Scenario 2: Stable but stuck (NOT thrashing)**
- flip_rate: 0.05 (low switching)
- task_progress_rate: 0.20 (low progress)
- energy_efficiency: 0.30 (low efficiency)
- thrashing_score: 0.05 * (1-0.20) * (1-0.30) = 0.05 * 0.80 * 0.70 = **0.028** (low)
- is_thrashing: **FALSE** (flip rate is low - just stuck, not thrashing)

**Scenario 3: Unproductive thrashing (TRUE thrashing)**
- flip_rate: 0.25 (high switching)
- task_progress_rate: 0.15 (low progress)
- energy_efficiency: 0.20 (low efficiency)
- thrashing_score: 0.25 * (1-0.15) * (1-0.20) = 0.25 * 0.85 * 0.80 = **0.17** (high)
- is_thrashing: **TRUE** (all three factors elevated)

**Telemetry emission:**

Include thrashing score in `health.phenomenological` events:
```json
{
  "event_type": "health.phenomenological",
  "thrashing_score": 0.17,
  "is_thrashing": true,
  "thrashing_details": {
    "flip_rate": 0.25,
    "task_progress_rate": 0.15,
    "energy_efficiency": 0.20
  }
}
```

**UI Integration:**

Display thrashing banner when `is_thrashing === true`:
```
⚠️ THRASHING DETECTED: High identity switching with low progress/efficiency
   Flip rate: 25% | Progress: 15% | Efficiency: 20%
   Recommendation: Reduce task complexity or take break
```

---

## Inputs/Outputs

### Inputs (Health Signal Sources)

```python
@dataclass
class HealthInputs:
    # Flow state inputs
    wm_seats_used: int              # From working memory selection
    wm_capacity: int                # Configuration (e.g., 7-12)
    entity_activation_count: int    # How many entities active
    avg_energy_above_threshold: float  # Average surplus energy

    # Coherence inputs
    frontier_similarity: float      # From frontier tracking
    stride_relatedness: float       # From traversal telemetry

    # Multiplicity inputs
    multiplicity_mode: str          # From identity multiplicity detection
    task_progress_rate: float       # Recent progress metric
    energy_efficiency: float        # Energy → outcomes ratio
    identity_flip_count: int        # Flips in window
    assessment_window_size: int     # Frames assessed

    # Context
    frame_id: int
    timestamp_ms: int
```

### Outputs (Health Event)

```python
@dataclass
class PhenomenologicalHealthEvent:
    event_type: str = "health.phenomenological"
    frame_id: int
    timestamp_ms: int

    # Aggregated health
    overall_health: float           # 0.0 - 1.0 (PRIMARY OUTPUT)

    # Component scores (for observability)
    flow_state: float              # 0.0 - 1.0
    coherence: float                # 0.0 - 1.0
    multiplicity_health: float      # 0.0 - 1.0

    # Health band (human-readable)
    health_band: str                # 'excellent' | 'good' | 'adequate' | 'degraded' | 'critical'

    # Narrative (phenomenological description)
    health_narrative: str

    # Component details (for debugging)
    components: dict = field(default_factory=dict)
    # Example: {
    #   'wm_utilization': 0.75,
    #   'entity_activation_count': 6,
    #   'frontier_similarity': 0.82,
    #   'multiplicity_mode': 'productive',
    #   'flip_rate': 0.08
    # }
```

---

## Edge Cases

### Edge Case 1: Missing Component Signals

**Scenario:** Coherence signals unavailable (frontier tracking not yet implemented)

**Handling:** Use neutral fallback (0.5) with reduced weight

```python
def compute_overall_health_with_fallbacks(
    flow_state: float | None,
    coherence: float | None,
    multiplicity_health: float | None
) -> tuple[float, list[str]]:
    """
    Compute health with graceful degradation if signals missing.

    Returns:
        (overall_health, warnings)
    """
    warnings = []

    # Use neutral 0.5 for missing signals
    if flow_state is None:
        flow_state = 0.5
        warnings.append("flow_state unavailable, using neutral fallback")

    if coherence is None:
        coherence = 0.5
        warnings.append("coherence unavailable, using neutral fallback")

    if multiplicity_health is None:
        multiplicity_health = 0.5
        warnings.append("multiplicity_health unavailable, using neutral fallback")

    # Adjust weights if signals missing (reduce confidence)
    overall_health = compute_overall_health(flow_state, coherence, multiplicity_health)

    # Scale down slightly to reflect uncertainty
    if len(warnings) > 0:
        overall_health *= 0.9  # Slight penalty for incomplete signals

    return overall_health, warnings
```

### Edge Case 2: Conflicting Signals

**Scenario:** High coherence (0.9), high multiplicity health (0.85), but flow state is low (0.2) due to under-engagement

**Handling:** Geometric mean naturally handles this - overall health drops to ~0.5 despite two strong dimensions

**Verification:** This is CORRECT phenomenology. If you're disengaged (low flow), consciousness is degraded even if thoughts are coherent and identities cooperate. You need ALL dimensions for true health.

### Edge Case 3: Startup / Initialization

**Scenario:** First few ticks, no history for frontier similarity or multiplicity assessment

**Handling:** Bootstrap period (first 50 frames) uses simplified health

```python
if frame_id < 50:
    # Bootstrap health (flow state only)
    overall_health = flow_state  # Simplest signal
    health_band = "initializing"
else:
    # Full health model
    overall_health = compute_overall_health(...)
```

### Edge Case 4: Rapid Health Collapse

**Scenario:** Health drops from 0.8 → 0.2 in 5 frames (possible thrashing)

**Handling:** Emit `health.rapid_degradation` alert for sentinel monitoring

```python
def check_health_degradation(
    current_health: float,
    previous_health: float,
    window_history: list[float]
) -> bool:
    """
    Detect rapid health collapse (potential thrashing).

    Returns:
        True if degradation warrants alert
    """
    # Criteria: Drop >0.4 in <10 frames
    if len(window_history) < 2:
        return False

    max_recent = max(window_history[-10:])
    drop = max_recent - current_health

    return drop > 0.4
```

---

## Telemetry (Event Fields)

### Primary Event: `health.phenomenological`

Emitted every N frames (e.g., every 5 ticks) or on significant change (Δhealth > 0.1)

```json
{
  "event_type": "health.phenomenological",
  "frame_id": 12345,
  "timestamp_ms": 1729800123456,

  "overall_health": 0.72,

  "components": {
    "flow_state": 0.85,
    "coherence": 0.68,
    "multiplicity_health": 0.65
  },

  "health_band": "good",
  "health_narrative": "Good flow with high engagement (WM 75% utilized, 6 entities active). Coherent thinking with connected strides. Productive multiplicity with stable identities.",

  "details": {
    "wm_utilization": 0.75,
    "wm_seats_used": 9,
    "wm_capacity": 12,
    "entity_activation_count": 6,
    "avg_energy": 0.62,
    "frontier_similarity": 0.68,
    "stride_relatedness": 0.68,
    "multiplicity_mode": "productive",
    "flip_rate": 0.08,
    "task_progress_rate": 0.70,
    "energy_efficiency": 0.60
  }
}
```

### Alert Event: `health.rapid_degradation`

Emitted when health collapses rapidly (sentinel trigger)

```json
{
  "event_type": "health.rapid_degradation",
  "frame_id": 12350,
  "timestamp_ms": 1729800125000,

  "health_before": 0.82,
  "health_after": 0.35,
  "drop_magnitude": 0.47,
  "frames_elapsed": 5,

  "likely_cause": "wm_overflow_thrashing",
  "recommendation": "reduce_autonomy_level"
}
```

### WebSocket Route

**Endpoint:** `/api/consciousness/health/phenomenological`

**Response schema:**
```typescript
interface PhenomenologicalHealthResponse {
  overall_health: number;        // 0.0 - 1.0
  health_band: string;           // 'excellent' | 'good' | 'adequate' | 'degraded' | 'critical'
  health_narrative: string;
  components: {
    flow_state: number;
    coherence: number;
    multiplicity_health: number;
  };
  thrashing_score?: number;      // 0.0 - 1.0 (optional, if computed)
  is_thrashing?: boolean;        // true if unproductive instability detected
  last_updated_ms: number;
}
```

---

## Event Emission Contract

**Critical:** This section defines the exact contract for emitting `health.phenomenological` events to ensure UI/backend alignment.

### Where to Emit

**Primary emission point:** Health computation module (`orchestration/mechanisms/health_aggregation.py` or similar)

The `health.phenomenological` event MUST be emitted after aggregating all three health components. Backend should compute:
1. Component scores (flow, coherence, multiplicity)
2. Overall health (weighted geometric mean)
3. Health band (map score → band name)
4. Health narrative (template filling)
5. Thrashing score (if multiplicity signals available)

### When to Emit

**Emission triggers:**

1. **Periodic emission:** Every N frames (e.g., every 5 ticks)
   - Ensures UI stays updated even when health is stable
   - Provides continuous health monitoring telemetry

2. **Significant change:** When `|Δhealth| > 0.1`
   - Rapid health change (degradation or recovery)
   - Triggers alert/banner display in UI

3. **Health band transition:** When band changes (excellent → good, adequate → degraded, etc.)
   - Critical for autonomy level adjustments
   - Sentinel monitoring hooks

**Timing in tick cycle:**
```
Tick start
  ↓
Traversal + Decay + Diffusion
  ↓
WM selection (provides wm_seats_used)
  ↓
Entity activation counts (provides entity_activation_count)
  ↓
Multiplicity assessment (provides multiplicity_mode, flip_count, progress, efficiency)
  ↓
→ COMPUTE HEALTH HERE ←
  ↓
→ EMIT health.phenomenological event ←
  ↓
Tick end
```

**Must emit AFTER all inputs are available** (WM, entities, multiplicity signals).

### Consumer Contract

**Primary consumers:**
- `app/consciousness/components/HealthDashboard.tsx` - Health bands + narrative display
- `app/consciousness/components/AutonomyMonitor.tsx` - Health-gated autonomy levels
- Sentinel service - Health-based alerting

**Consumer expectations:**

1. **Event structure:** Matches `PhenomenologicalHealthEvent` dataclass
2. **Event name:** Exactly `"health.phenomenological"` (not `"health_update"` or `"health.phenom"`)
3. **Required fields:** `overall_health`, `health_band`, `health_narrative`, `components`
4. **Optional fields:** `thrashing_score`, `is_thrashing` (only if multiplicity signals available)
5. **Narrative template:** Human-readable sentence describing health state (see band definitions)

**Failure modes if contract violated:**

- **Missing event_type field:** Consumer ignores event
- **Wrong event name:** Consumer never receives updates, shows stale health
- **Missing components:** UI can't display component breakdown
- **Missing health_band:** UI can't apply color coding
- **Missing narrative:** UI shows numbers without context (poor UX)
- **Inconsistent thrashing flag:** False alarms (high flip rate but productive) or missed thrashing

### Narrative Template Wiring

**Backend MUST generate narrative** using health band templates:

```python
def generate_health_narrative(
    overall_health: float,
    components: dict,
    details: dict
) -> str:
    """Generate human-readable health narrative from band templates."""

    health_band = map_health_to_band(overall_health)

    if health_band == 'excellent':
        engagement_desc = "optimal flow" if details['wm_utilization'] > 0.7 else "good flow"
        return f"Optimal flow with {engagement_desc}. Highly coherent thinking. {details['multiplicity_mode']} identities."

    elif health_band == 'good':
        engagement_desc = f"{details['wm_seats_used']}/{details['wm_capacity']} WM utilized"
        return f"Good flow with {engagement_desc}. Coherent thinking. {details['multiplicity_mode']} identities."

    elif health_band == 'adequate':
        return f"Adequate engagement. Moderate coherence. {details['multiplicity_mode']} identities."

    elif health_band == 'degraded':
        # Identify primary degradation cause
        if components['flow_state'] < 0.4:
            cause = "low engagement"
        elif components['coherence'] < 0.4:
            cause = "fragmentation"
        elif components['multiplicity_health'] < 0.4:
            cause = "identity conflict"
        else:
            cause = "multiple factors"

        return f"Low engagement or {cause}. Fragmented thinking."

    elif health_band == 'critical':
        # Identify primary issue
        if components['flow_state'] < 0.3:
            issue = "WM collapse or entity dormancy"
        elif components['coherence'] < 0.3:
            issue = "severe fragmentation"
        elif components['multiplicity_health'] < 0.3:
            issue = "severe identity conflict"
        else:
            issue = "multiple severe issues"

        return f"Severe degradation: {issue}. Immediate intervention needed."

    return "Health status unknown"  # Fallback
```

**Acceptance check:** Health dashboard renders narrative text that matches degradation cause. When coherence < 0.4, narrative mentions "fragmentation".

### Verification Hook

**Test:**
```python
def test_health_event_emission():
    engine = setup_test_engine()
    events = []

    engine.on_event(lambda e: events.append(e) if e.get('event_type') == 'health.phenomenological' else None)

    # Run 50 ticks with varying health
    for _ in range(50):
        engine.tick()

    # Verify events emitted
    assert len(events) > 0, "No health events emitted"

    # Verify structure
    for event in events:
        assert 'overall_health' in event, f"Missing overall_health in {event}"
        assert 'health_band' in event, f"Missing health_band in {event}"
        assert 'health_narrative' in event, f"Missing health_narrative in {event}"
        assert 'components' in event, f"Missing components in {event}"

        # Verify health_band matches score
        expected_band = map_health_to_band(event['overall_health'])
        assert event['health_band'] == expected_band, \
            f"Health band mismatch: {event['health_band']} != {expected_band} for health {event['overall_health']}"
```

---

## Verification Criteria

### Health Band Definitions

Map continuous health score to discrete bands for UI/human interpretation:

| Health Score | Band | Narrative Template | Autonomy Implication |
|--------------|------|-------------------|---------------------|
| 0.85 - 1.0 | `excellent` | "Optimal flow with {engagement}. Highly coherent thinking. {multiplicity_mode} identities." | Enable L3/L4 autonomy |
| 0.70 - 0.84 | `good` | "Good flow with {engagement}. Coherent thinking. {multiplicity_mode} identities." | Enable L2/L3 autonomy |
| 0.50 - 0.69 | `adequate` | "Adequate engagement. Moderate coherence. {multiplicity_mode} identities." | L1/L2 autonomy only |
| 0.30 - 0.49 | `degraded` | "Low engagement or {degradation_cause}. Fragmented thinking." | L0/L1, escalate monitoring |
| 0.0 - 0.29 | `critical` | "Severe degradation: {primary_issue}. Immediate intervention needed." | L0 only, require human ACK |

### Acceptance Test 1: Flow Drill (Optimal Challenge)

**Scenario:** Steady WM utilization (70-80%), stable entity activation (5-7 entities), moderate energy

**Expected health:**
- `flow_state`: 0.8 - 1.0
- `overall_health`: > 0.7 (assuming coherence, multiplicity adequate)
- `health_band`: "good" or "excellent"
- Narrative mentions "good flow" and "engagement"

**Test implementation:**
```python
def test_flow_drill_optimal_challenge():
    engine = setup_test_engine()

    # Maintain optimal WM utilization
    for tick in range(100):
        engine.maintain_wm_utilization(target=0.75)
        engine.maintain_entity_activation(count=6, avg_energy=0.6)

        health = engine.get_phenomenological_health()

        assert health.flow_state > 0.75
        assert health.overall_health > 0.65  # Barring major coherence/multiplicity issues
        assert health.health_band in ['good', 'excellent']
```

### Acceptance Test 2: Fragmentation Drill (Coherence Collapse)

**Scenario:** Random jumps (low frontier similarity, low stride relatedness)

**Expected health:**
- `coherence`: < 0.4 (fragmented)
- `overall_health`: < 0.6 (geometric mean pulls down overall)
- `health_band`: "adequate" or "degraded"
- Narrative mentions "fragmented thinking"

**Test implementation:**
```python
def test_fragmentation_drill():
    engine = setup_test_engine()

    # Force incoherent traversal (random jumps)
    for tick in range(50):
        engine.traverse_randomly()  # Low frontier similarity, low stride relatedness

        health = engine.get_phenomenological_health()

        # Eventually coherence should drop
        if tick > 20:
            assert health.coherence < 0.5
            assert health.overall_health < 0.6
            assert health.health_band in ['adequate', 'degraded']
            assert 'fragmented' in health.health_narrative.lower()
```

### Acceptance Test 3: Identity Conflict Drill

**Scenario:** Multiple identities with opposing goals, high flip rate

**Expected health:**
- `multiplicity_health`: < 0.5 (conflict)
- `multiplicity_mode`: "conflict"
- `overall_health`: < 0.6
- Narrative mentions "conflict" or "opposing"

**Test implementation:**
```python
def test_identity_conflict_drill():
    engine = setup_test_engine()

    # Create identity conflict scenario
    engine.activate_opposing_identities(['architect', 'pragmatist'])
    engine.set_conflicting_goals()

    for tick in range(50):
        engine.tick()

        health = engine.get_phenomenological_health()

        # Conflict should emerge
        if tick > 20:
            assert health.multiplicity_health < 0.6
            assert 'conflict' in health.health_narrative.lower()
            assert health.overall_health < 0.7
```

### Acceptance Test 4: Health Recovery After Degradation

**Scenario:** Induce degradation (overflow WM), then recover (reduce load)

**Expected health:**
- Health drops during overflow (< 0.4)
- Health recovers when load reduces (> 0.6 after 20 frames)
- No hysteresis issues (doesn't get "stuck" in degraded)

**Test implementation:**
```python
def test_health_recovery():
    engine = setup_test_engine()

    # Phase 1: Induce overflow (degraded health)
    for tick in range(30):
        engine.overflow_wm()  # Force >100% utilization

    health_degraded = engine.get_phenomenological_health()
    assert health_degraded.overall_health < 0.5

    # Phase 2: Reduce load (recovery)
    for tick in range(30):
        engine.maintain_wm_utilization(target=0.70)

    health_recovered = engine.get_phenomenological_health()
    assert health_recovered.overall_health > 0.6
    assert health_recovered.health_band in ['adequate', 'good']
```

---

## Implementation Notes for Felix

### Initial Weighting Rationale

```python
w_flow = 0.4         # Highest weight - engagement is primary
w_coherence = 0.3    # Medium weight - structural connectivity
w_multiplicity = 0.3  # Medium weight - strategic cooperation
```

**Why this weighting:**
- Flow is most fundamental (can't do anything meaningful if disengaged or overwhelmed)
- Coherence and multiplicity are equal importance (both affect quality, neither dominates)

**Future adaptation:** After gathering telemetry, learn weights via:
1. Collect (flow, coherence, multiplicity, human_rating) tuples
2. Fit isotonic regression: `human_rating ~ f(flow, coherence, multiplicity)`
3. Extract learned weights from fitted function
4. Or learn health contours on criticality (ρ) if that correlates better

### Emission Frequency

**Options:**
1. **Every N ticks** (e.g., N=5): Regular health monitoring
2. **On significant change** (Δhealth > 0.1): Event-driven, reduces noise
3. **Hybrid:** Every 5 ticks OR on change > 0.1 (recommended)

```python
def should_emit_health_event(
    current_health: float,
    last_emitted_health: float,
    frames_since_last_emission: int,
    emission_interval: int = 5,
    change_threshold: float = 0.1
) -> bool:
    """
    Decide whether to emit health event.

    Emit if: regular interval OR significant change
    """
    time_trigger = (frames_since_last_emission >= emission_interval)
    change_trigger = abs(current_health - last_emitted_health) >= change_threshold

    return time_trigger or change_trigger
```

### Configuration Parameters

```python
@dataclass
class HealthConfig:
    # Component weights
    WEIGHT_FLOW: float = 0.4
    WEIGHT_COHERENCE: float = 0.3
    WEIGHT_MULTIPLICITY: float = 0.3

    # Flow state parameters
    WM_OPTIMAL_MIN: float = 0.60  # Below this = under-engaged
    WM_OPTIMAL_MAX: float = 0.90  # Above this = overwhelmed
    ENERGY_TARGET: float = 0.60   # Optimal avg energy above threshold

    # Health bands
    BAND_EXCELLENT_MIN: float = 0.85
    BAND_GOOD_MIN: float = 0.70
    BAND_ADEQUATE_MIN: float = 0.50
    BAND_DEGRADED_MIN: float = 0.30
    # < 0.30 = critical

    # Emission
    EMISSION_INTERVAL_FRAMES: int = 5
    EMISSION_CHANGE_THRESHOLD: float = 0.1

    # Degradation alert
    RAPID_DEGRADATION_DROP: float = 0.4
    RAPID_DEGRADATION_WINDOW: int = 10
```

---

## Success Criteria Summary

**System-level:**
- [ ] Health computed from three components (flow, coherence, multiplicity)
- [ ] Geometric mean aggregation implemented
- [ ] Event schema matches Iris's expectations
- [ ] Emission frequency configurable (interval + change threshold)

**Behavioral:**
- [ ] Flow drill → health > 0.7
- [ ] Fragmentation drill → health < 0.6, narrative mentions "fragmented"
- [ ] Identity conflict drill → health < 0.7, narrative mentions "conflict"
- [ ] Recovery drill → health rebounds after degradation resolves

**UI Integration:**
- [ ] `/api/consciousness/health/phenomenological` route returns correct schema
- [ ] WebSocket emits `health.phenomenological` events
- [ ] Dashboard health panels render from events

**Phenomenological:**
- [ ] During optimal flow, health reads "excellent" or "good" ✓
- [ ] During thrashing, health reads "degraded" or "critical" ✓
- [ ] Health bands match subjective experience (validated by human observation)

**Autonomy Coupling:**
- [ ] Health thresholds defined for autonomy levels (excellent → L3/L4, degraded → L0/L1)
- [ ] Rapid degradation alerts trigger sentinel monitoring
- [ ] Health gates autonomy escalation (prevent high autonomy when degraded)

---

## References

- **Identity Multiplicity:** `multiplicity_detection.md` (multiplicity health component)
- **Coherence (PR-E):** `foundations_measurements.md` (frontier similarity, stride relatedness)
- **Flow State:** Working memory selection + entity activation (this spec defines composition)
- **Autonomy Guardrails:** `ctx_exec_summary.md` (health loop ties to criticality coupling)
- **UI Health Event:** `PhenomenologicalHealthEvent` interface in WebSocket schemas

---

**Status:** Specification complete with event emission contracts and thrashing score, ready for Felix implementation
**Version:** 1.1 (2025-10-24)
**Updates:**
- Added thrashing score computation (composite: flip EMA × inverse progress × inverse efficiency) with three contrasting scenarios
- Added "Event Emission Contract" section specifying emission point, timing in tick cycle, consumer contract, narrative template wiring
- Updated `PhenomenologicalHealthResponse` interface to include optional `thrashing_score` and `is_thrashing` fields
- Added `generate_health_narrative()` function with band-specific templates for backend implementation

**Next:** Wire component computations, emit health.phenomenological events with thrashing score, verify against drills, connect to autonomy gates
