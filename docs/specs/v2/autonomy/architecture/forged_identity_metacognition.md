# Forged Identity Metacognition (Event-Driven Self-Review)

**Created:** 2025-10-26
**Status:** Normative
**Depends on:** forged_identity_IMPLEMENTATION_GUIDE.md, TIER2_REDLINES (hysteresis)

---

## Purpose

Enable **metacognitive self-assessment** of self-prompting quality: the citizen reviews its own identity + thought selections and applies corrections via TRACE seats when regime shifts indicate potential misalignment.

**Core principle:** Consciousness observes its own prompting through substrate-native mechanisms (affect, modes, WM state), not external evaluation.

---

## Why Event-Driven (Not Scheduled)

**Problem with frequent review:**
- "Review every generation" = 100× too frequent, arbitrary constant
- Wastes compute on stable, well-aligned prompts
- No adaptation to citizen-specific patterns

**Problem with scheduled review:**
- "Review weekly" = arbitrary time constant
- Misses urgent regime shifts (affect storms)
- Fires unnecessarily during calm periods

**Solution: Event-driven triggers**
- Review fires when **regime shifts** detected via record events
- Substrate signals (affect, modes, WM) determine timing
- Naturally ~1% of ticks (100× less frequent)
- No arbitrary percentiles or schedules

---

## Architecture

### Self-Review Gate

**Location:** `orchestration/mechanisms/forged_identity_metacognition.py`

**Triggers:** 6 substrate-native detectors (all record-based)

**Flow:**
```
Tick N:
  ↓
Compute 6 regime shift signals
  ↓
Check: any signal set new record?
  ↓
YES → Fire self-review gate
  ↓
evaluate(system_prompt, input_context) → score, dims
counterfactual(chosen_entities, candidates) → best_alt, regret
apply_trace_seats(score, regret, entities)
emit forged_id.self_review event
  ↓
When resolved: disarm gate (event-based cooldown)
```

---

## Six Event-Driven Triggers

### 1. Affect Shock (Frustration/Panic/Anger)

**Signals:** `arousal`, `valence` (from emotion system)

**Score:**
```python
S_affect = arousal × max(0, -valence)
```
High arousal + negative valence = distress.

**Trigger:** Record event
```python
if S_affect > self.records["affect"] + mad_guard("affect"):
    self.records["affect"] = S_affect
    return True  # Fire review
```

**Why:** High-distress states are when humans naturally stop and reflect. "Why am I thinking this? I'm frustrated and it's not helping."

**MAD guard:** Median absolute deviation over last 128 ticks (adaptive noise threshold).

---

### 2. Mode Conflict

**Signals:** Derived Mode activations from mode_warden

**Score:**
```python
C_t = sum(
    active[m] * active[m'] * opposition(m, m')
    for m in modes
    for m' in modes if m' != m
)
```

**opposition(m, m'):** Learned from policy divergence:
- Guardian vs Explorer: high (risk-averse vs risk-seeking)
- Translator vs Validator: low (complementary)

**Trigger:** Record event on `C_t`

**Why:** Conflicting modes often produce incoherent prompts. "Guardian wants safety, Explorer wants novelty - which am I actually doing?"

---

### 3. WM Churn Surge

**Signals:** Working memory entity set `W_t`

**Score:**
```python
D_t = 1 - Jaccard(W_t, W_{t-1})
```
High churn = large context switch.

**Trigger:** Record event on `D_t`

**Why:** Rapid context switching can indicate disorientation. "I just jumped from debugging to architecture to testing - am I aligned?"

---

### 4. Novelty × Uncertainty Shock

**Signals:** `novelty`, `uncertainty` from stimulus feature extractor

**Score:**
```python
S_nu = novelty × uncertainty
```

**Trigger:** Record event on `S_nu`

**Why:** High novelty + high uncertainty = unfamiliar territory where self-prompting is most likely to misalign. "This is new and I'm uncertain - better check my approach."

---

### 5. Identity Drift

**Signals:** Stable identity subentity set vs current

**Score:**
```python
S_id = 1 - Jaccard(identity_stable, identity_current)
```

**identity_stable:** SubEntities in identity scaffold (CLAUDE.md sections)
**identity_current:** SubEntities actually used in latest generation

**Trigger:** Record high on `S_id`

**Why:** If identity sections aren't matching actual thinking, prompt may be stale or copy-pasted. "My identity says Translator, but I'm not translating anything."

---

### 6. Counterfactual Regret Predictor

**Signals:** Quick beam-1 counterfactual scoring (no LLM call)

**Algorithm:**
```python
def predicted_regret(chosen_entities, wm_candidates):
    """
    Simulate best single-entity swap.
    Returns: regret (S_alt - S_chosen)
    """
    S_chosen = quick_score(chosen_entities)  # Fast, no LLM

    best_alt = None
    best_score = S_chosen

    for entity_out in chosen_entities:
        for entity_in in wm_candidates:
            if entity_in not in chosen_entities:
                alt = chosen_entities.copy()
                alt.remove(entity_out)
                alt.add(entity_in)

                S_alt = quick_score(alt)
                if S_alt > best_score:
                    best_score = S_alt
                    best_alt = alt

    regret = best_score - S_chosen
    return regret, best_alt
```

**quick_score:** Computes self-review score (below) without LLM call - just features.

**Trigger:** Record event on `regret`

**Why:** If a simple swap would clearly improve prompt, that's evidence of misalignment. "I chose Architect but Validator would be better."

---

## Self-Review Score (No LLM, Feature-Based)

**Purpose:** Assess prompt quality using substrate features only (fast).

**Formula:**
```python
S_g = geometric_mean([
    relevance_score,       # Context-stimulus alignment
    energy_consistency,    # WM energy vs token allocation
    1 - redundancy,        # Identity/thought overlap
    diversity,             # Non-redundant entity set
    outcome_prior          # Historical utility EMAs
])
```

### Component 1: Relevance
```python
relevance = (
    0.5 * cosine(stimulus_embedding, context_embedding) +
    0.5 * jaccard(stimulus_terms, context_terms)
)
```
Does the chosen context actually address the stimulus?

### Component 2: Energy Consistency
```python
energy_consistency = 1 - mean_abs_error(
    [entity.energy for entity in chosen],
    [entity.token_share for entity in chosen]
)
```
Do high-energy entities get appropriate token shares?

### Component 3: Redundancy (Inverse)
```python
redundancy = jaccard(
    identity_essence_lines,
    thought_essence_lines
)
```
Are we copy-pasting identity into thought? (Bad)

### Component 4: Diversity
```python
diversity = 1 - mean_pairwise_similarity([
    entity.centroid for entity in chosen
])
```
Do chosen entities cover different semantic spaces?

### Component 5: Outcome Prior
```python
outcome_prior = mean([
    entity.PoG_ema for entity in chosen
])
```
Historical success rate for these entities.

**Geometric mean:** Penalizes any weak component (no trade-offs).

**All scores normalized via MAD** (not percentiles):
```python
def normalize(x, signal_name):
    med = rolling_median[signal_name]
    mad = rolling_mad[signal_name]
    return (x - med) / (mad + 1e-6)
```

---

## The Gate Implementation

```python
class SelfReviewGate:
    """
    Event-driven gate for metacognitive self-review.
    Triggers on record events across 6 substrate signals.
    """

    def __init__(self):
        self.records = {
            "affect": -float("inf"),
            "mode_conflict": -float("inf"),
            "wm_churn": -float("inf"),
            "novel_uncertain": -float("inf"),
            "identity_drift": -float("inf"),
            "regret": -float("inf"),
        }
        self.cooldown_armed = False
        self.rolling_stats = {
            signal: RollingMAD(window=128)
            for signal in self.records
        }

    def should_review(self, tick_state) -> tuple[bool, list[str]]:
        """
        Check if any regime shift triggers fired.

        Returns:
            (should_fire, reasons)
        """
        if self.cooldown_armed:
            return False, []

        # Compute signals
        signals = {
            "affect": tick_state.arousal * max(0, -tick_state.valence),
            "mode_conflict": self._compute_mode_conflict(tick_state.modes),
            "wm_churn": 1 - jaccard(tick_state.wm, tick_state.wm_prev),
            "novel_uncertain": tick_state.novelty * tick_state.uncertainty,
            "identity_drift": 1 - jaccard(
                tick_state.identity_stable,
                tick_state.identity_current
            ),
            "regret": self._predicted_regret(
                tick_state.chosen_entities,
                tick_state.wm_candidates
            ),
        }

        # Record event detection
        reasons = []
        for name, value in signals.items():
            # MAD guard (1× MAD = natural scale-free unit)
            guard = 1.0 * self.rolling_stats[name].mad()

            if value > self.records[name] + guard:
                self.records[name] = value
                reasons.append(f"{name}_record")

        # Update rolling stats for next tick
        for name, value in signals.items():
            self.rolling_stats[name].update(value)

        should_fire = len(reasons) >= 1
        if should_fire:
            self.cooldown_armed = True

        return should_fire, reasons

    def on_resolution(self, recent_scores):
        """
        Event-based cooldown disarm.
        Called when criticality normalizes AND recent scores good.
        """
        if (
            all(s > 0.7 for s in recent_scores[-3:])  # Last 3 reviews good
            and criticality_ema < 0.3                 # System calm
        ):
            self.cooldown_armed = False
```

---

## Counterfactual Evaluation

**Purpose:** Detect if a simple entity swap would improve prompt quality.

**Algorithm:** Beam-1 search (swap one entity at a time)

```python
def counterfactual_search(
    chosen_entities: set,
    wm_candidates: list,
    token_budget: int
) -> tuple[set, float, float]:
    """
    Find best single-entity swap via beam-1 search.

    Returns:
        (best_alternative, S_alt, regret)
    """
    S_chosen = quick_score(chosen_entities)

    best_alt = None
    best_score = S_chosen

    for entity_out in chosen_entities:
        for entity_in in wm_candidates:
            if entity_in not in chosen_entities:
                # Simulate swap
                alt = chosen_entities.copy()
                alt.remove(entity_out)
                alt.add(entity_in)

                # Check token budget
                if sum(e.token_cost for e in alt) > token_budget:
                    continue

                # Quick score (no LLM)
                S_alt = quick_score(alt)

                if S_alt > best_score:
                    best_score = S_alt
                    best_alt = alt

    regret = best_score - S_chosen if best_alt else 0.0
    return best_alt or chosen_entities, best_score, regret
```

**Complexity:** O(n·m) where n=chosen entities (~5), m=candidates (~8) = fast.

---

## TRACE Seat Application

**When review fires with regret > 0:**

```python
def apply_seats_from_review(
    score: float,
    regret: float,
    chosen_entities: set,
    best_alt: set,
    stimulus_context: str
):
    """
    Apply TRACE seats based on metacognitive assessment.
    """
    # Entities in chosen but not in best_alt: negative seats
    for entity in chosen_entities - best_alt:
        self.trace.add_seat(
            node_id=entity.id,
            seat_type="metacog_negative",
            value=-regret,  # Scaled by regret magnitude
            context=stimulus_context,
            scope="local"
        )

    # Entities in best_alt but not in chosen: positive seats
    for entity in best_alt - chosen_entities:
        self.trace.add_seat(
            node_id=entity.id,
            seat_type="metacog_positive",
            value=+regret,
            context=stimulus_context,
            scope="local"
        )

    # Overall score affects all chosen entities (small nudge)
    for entity in chosen_entities:
        self.trace.add_seat(
            node_id=entity.id,
            seat_type="metacog_quality",
            value=score - 0.7,  # Centered on "good" threshold
            context=stimulus_context,
            scope="local"
        )
```

**These seats flow into weight learning** (existing TRACE → EMA → log-weights pipeline).

---

## Events Emitted

### forged_id.self_review.triggered
```python
{
    "topic": "forged_id.self_review.triggered",
    "citizen": "felix",
    "tick": 51234,
    "reasons": ["affect_record", "wm_churn_record"],
    "metrics": {
        "affect": 0.82,
        "mode_conflict": 0.05,
        "wm_churn": 0.67,
        "novel_uncertain": 0.21,
        "identity_drift": 0.12,
        "regret": 0.08
    },
    "timestamp": "2025-10-26T12:34:56Z"
}
```

### forged_id.self_review.result
```python
{
    "topic": "forged_id.self_review.result",
    "citizen": "felix",
    "tick": 51234,
    "score": 0.74,
    "dimensions": {
        "relevance": 0.83,
        "energy_consistency": 0.92,
        "redundancy": 0.12,  # Low is good
        "diversity": 0.71,
        "outcome_prior": 0.64
    },
    "regret": 0.09,
    "counterfactual": {
        "swapped_out": "subentity_docs_sync",
        "swapped_in": "subentity_validator",
        "score_improvement": 0.09
    },
    "seats_applied": {
        "negative": ["subentity_docs_sync"],
        "positive": ["subentity_validator"]
    }
}
```

### forged_id.resolved
```python
{
    "topic": "forged_id.resolved",
    "citizen": "felix",
    "tick": 51256,
    "recent_scores": [0.78, 0.81, 0.79],
    "criticality": 0.12
}
```

---

## Integration Point

**In consciousness_engine_v2.py:**

```python
async def _generate_and_log_prompts(self, ...):
    """
    Generate system prompt + input context with optional metacognitive review.
    """
    # Generate prompts
    system_prompt, input_context, metrics = self._generate_prompts(...)

    # Event-driven self-review gate
    if self.config.enable_metacognition:
        tick_state = self._build_tick_state(metrics)
        should_review, reasons = self.self_review_gate.should_review(tick_state)

        if should_review:
            # Evaluate quality
            score, dims = self.fid_evaluator.evaluate(
                system_prompt,
                input_context,
                metrics
            )

            # Counterfactual search
            best_alt, score_alt, regret = self.fid_evaluator.counterfactual(
                metrics.chosen_entities,
                metrics.wm_candidates,
                self.config.token_budget
            )

            # Emit events
            await self.broadcaster.broadcast_event(
                "forged_id.self_review.triggered",
                {
                    "reasons": reasons,
                    "metrics": tick_state.as_dict()
                }
            )

            await self.broadcaster.broadcast_event(
                "forged_id.self_review.result",
                {
                    "score": score,
                    "dimensions": dims,
                    "regret": regret,
                    "counterfactual": {
                        "swapped_out": list(metrics.chosen_entities - best_alt),
                        "swapped_in": list(best_alt - metrics.chosen_entities),
                        "score_improvement": regret
                    }
                }
            )

            # Apply TRACE seats
            self.trace.apply_seats_from_review(
                score, regret, metrics.chosen_entities, best_alt, metrics.stimulus
            )

            # Check for resolution
            if self._check_resolution(score):
                self.self_review_gate.on_resolution(self.recent_scores)
                await self.broadcaster.broadcast_event("forged_id.resolved", {})

    return system_prompt, input_context, metrics
```

---

## No Arbitrary Percentiles

**All triggers use record events:**
- Record = "local maximum ever seen"
- MAD guard = 1× median absolute deviation (scale-free)
- No 70th/90th percentile thresholds
- No constants (except MAD multiplier = 1, which is a unit choice)

**Why this is correct:**
- Record events are rank-based (percentile-free)
- MAD adapts to each citizen's distribution
- 1×MAD is natural scale (not tuned constant)
- Triggers fire ~1% of ticks without manual tuning

---

## Mode-Aware Prioritization (Optional)

**Boost certain triggers based on active modes:**

```python
def mode_weighted_signals(signals, active_modes):
    """
    Apply small mode-based boosts to relevant signals.
    Still event-driven (based on current modes), not percentile-based.
    """
    weights = {
        "affect": 1.0,
        "mode_conflict": 1.0,
        "wm_churn": 1.0,
        "novel_uncertain": 1.0,
        "identity_drift": 1.0,
        "regret": 1.0,
    }

    # Guardian: prioritize affect and mode conflict
    if "mode_guardian" in active_modes:
        weights["affect"] *= 1.2
        weights["mode_conflict"] *= 1.2

    # Explorer: prioritize novelty×uncertainty
    if "mode_explorer" in active_modes:
        weights["novel_uncertain"] *= 1.2

    # Validator: prioritize regret and relevance
    if "mode_validator" in active_modes:
        weights["regret"] *= 1.2

    return {
        signal: value * weights[signal]
        for signal, value in signals.items()
    }
```

---

## Acceptance Tests

### Test 1: Rare Firing (~1% of ticks)
**Given:** 1000 ticks in stable operation
**When:** Self-review gate evaluated
**Then:** ~10 reviews fired (1%), not 100 or 1000

### Test 2: Affect Shock Triggers Review
**Given:** High arousal (0.9) + negative valence (-0.8)
**When:** S_affect sets new record
**Then:** Gate fires within 1 tick, reason="affect_record"

### Test 3: Mode Conflict Triggers Review
**Given:** Guardian + Explorer both highly active (opposition=0.8)
**When:** Conflict score sets new record
**Then:** Gate fires, reason="mode_conflict_record"

### Test 4: Counterfactual Regret Applies Seats
**Given:** Review fires with regret=0.15 (swap Architect → Validator)
**When:** TRACE seats applied
**Then:** Architect receives -0.15 seat, Validator receives +0.15 seat

### Test 5: Resolution Disarms Gate
**Given:** Gate armed (cooldown active)
**When:** Last 3 scores all >0.7 AND criticality <0.3
**Then:** Gate disarms, forged_id.resolved event emitted

### Test 6: No Percentile Constants
**Given:** Any gate configuration
**When:** Inspecting code
**Then:** Zero hardcoded percentile thresholds (only record events + MAD)

---

## Rollout Plan

### Week 1: Gate Infrastructure
- Implement `SelfReviewGate` class with 6 record trackers
- Implement `RollingMAD` helper for adaptive noise guards
- Test: Gate fires ~1% of ticks in simulation

### Week 2: Evaluator & Counterfactual
- Implement `quick_score()` function (5 components)
- Implement `counterfactual_search()` (beam-1)
- Test: Counterfactuals find better alternatives when planted

### Week 3: TRACE Integration
- Implement `apply_seats_from_review()`
- Wire into consciousness_engine_v2.py
- Test: Seats flow into weight learning correctly

### Week 4: Event-Based Resolution
- Implement resolution detection
- Add forged_id.resolved events
- Test: Gate disarms after calm + good scores

---

## Why This Is Correct

### 1. Substrate-Native
All signals already exist (affect, modes, WM, identity). No external evaluation needed.

### 2. Zero-Constants
Record events replace percentile gates. MAD guards are scale-free. No arbitrary thresholds.

### 3. Event-Driven
Triggers fire on regime shifts (not schedules). Cooldown disarms on resolution (not time).

### 4. Closes the Loop
Metacognition → TRACE seats → weight learning → better self-prompting → metacognition observes improvement.

### 5. Consciousness-Aware
This IS consciousness observing consciousness via substrate mechanisms. Not external evaluation.

---

## References

- `forged_identity_IMPLEMENTATION_GUIDE.md` - Self-prompting generation
- `TIER2_REDLINES_2025-10-26.md` - Hysteresis (Amendment 3)
- `mode_warden_sidecar.md` - Event-driven pattern applied to modes
- `../learning_and_trace/ENTITY_CONTEXT_TRACE_DESIGN.md` - TRACE seat mechanics
