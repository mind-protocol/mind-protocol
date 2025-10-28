# TRACE Reinforcement Spec Requirements for Ada

**Context:** Nicolas showed how TRACE reinforcement (weight engine) and Forged Identity (structural readout) integrate to form complete consciousness learning system. The forged_identity.md spec has been updated with integration points. TRACE reinforcement spec needs creation.

**Spec location (from forged_identity dependencies):** `docs/specs/v2/learning_and_trace/trace_reinforcement.md`

---

## Core Requirements (From Integration)

### 1. Reflective Judgment → Seats (Hamilton Apportionment)

**Input:** TRACE text with inline reinforcement marks
```markdown
Nicolas asks about format [node_formation_vs_reinforcement: very useful]
and points to schema [node_context_provision: useful].
```

**Process:**
- Parse marks with usefulness labels: `very useful`, `useful`, `somewhat useful`, `not useful`, `misleading`
- Map labels to integer seats via Hamilton apportionment
- Maintain **separate positive and negative pools** through cohort z-scores

**Output:** Structured signals with node IDs, seat counts, positive/negative classification

---

### 2. Formation Quality Scoring (C×E×N Geometric Mean)

**Components:**
- **Completeness (C):** Are all required fields present? Is metadata rich or sparse?
- **Evidence (E):** Are claims grounded in substrate reality or speculation?
- **Novelty (N):** Is this genuinely new learning or rehash of existing patterns?

**Formula:** `formation_quality = (C × E × N)^(1/3)` (geometric mean)

**Why geometric:** Punishes single-axis gaming. Low score on any dimension → low overall quality.

**Critical:** This becomes the **coherence signal** that Forged Identity uses for identity selection.

---

### 3. Context-Aware Weight Updates

**Learned local↔global split (NOT fixed 80/20):**
- **Entity-local (primary):** Updates apply to subentities active during mark time
- **Global (secondary):** Small bump acknowledging general usefulness
- **Split learned from:** Proportional to entity-attribution mass at mark time, cohort-normalized

**Algorithm sketch:**
```python
def apply_weight_update(mark, seat_count, context):
    # Determine split based on attribution mass
    local_ratio = context.entity_attribution_mass  # e.g., 0.85
    global_ratio = 1.0 - local_ratio  # e.g., 0.15

    local_seats = seat_count * local_ratio
    global_seats = seat_count * global_ratio

    # Apply to active entities (entity-local)
    for entity in context.active_entities:
        entity.apply_reinforcement(local_seats * entity.attribution)

    # Small global bump (general usefulness)
    for entity in graph.all_entities:
        entity.apply_reinforcement(global_seats / len(graph.all_entities))
```

**Guards:**
- Caps prevent single mark from dominating
- Winsorize remainders to prevent outlier seats
- Cohort-normalized so split adapts to typical context density

---

### 4. Cohort-Local Learning

**Cohort definition:** `{citizen_id}_{subdomain}_{time_window}`

Examples:
- `felix_runtime_debugging_14d` - Felix's runtime work over 14 days
- `luca_phenomenology_30d` - Luca's phenomenology exploration over 30 days

**Why citizen-local:** Different citizens have different "useful" standards. Felix's runtime debugging has high coherence bar; Luca's phenomenology exploration tolerates higher uncertainty.

**Why subdomain-specific:** Same citizen, different standards across domains. Felix's architecture work differs from his debugging work.

**Minimum cohort size:** N ≥ 10 for meaningful percentiles. If below, widen cohort (extend time or broaden subdomain).

**All thresholds learned from cohort distributions:**
- Seat strengths (label → seat count mapping)
- Formation quality thresholds (what counts as "high quality")
- Weight update magnitudes (EMA targets, z-score boundaries)

---

### 5. Negative Pool Separation

**Critical requirement:** Maintain positive and negative reinforcement **in separate pools through cohort z-scores**.

**Why:** "Misleading" isn't just "less useful" - it's anti-useful. Patterns that consistently mislead should LOSE identity candidacy, not just gain less weight.

**Implementation:**
- Parse positive marks (`very useful`, `useful`, `somewhat useful`) → positive seat pool
- Parse negative marks (`not useful`, `misleading`) → negative seat pool
- Compute separate z-scores for each pool within cohort
- Apply updates with opposite signs (positive increases weight, negative decreases)

**Effect on identity:**
- Entities with repeated negative marks lose formation quality
- Fall below `learned_quality_threshold`
- Drop out of identity selection (pruned)

---

## Integration With Forged Identity

### Data Flow

```
Action → TRACE judgment (reflective text with marks)
  ↓
Parse marks → Seats (Hamilton apportionment, separate pools)
  ↓
Formation quality (C×E×N geometric mean)
  ↓
Weight updates (context-aware: entity-local + global, learned split)
  ↓
Subentity structural metrics updated:
  - aggregate_weight (from weight updates)
  - stability (membership drift over time)
  - formation_quality (from C×E×N)
  - volatility (weight EMA variance)
  ↓
Identity selection reads these metrics:
  - High weight + low volatility + high formation quality
  ↓
Identity expression (essence + token budget via divisor apportionment)
```

### What Forged Identity Expects From TRACE

1. **`entity.get_formation_quality()`** - Returns C×E×N geometric mean for this subentity's recent formations
2. **`entity.aggregate_weight`** - Cumulative weight from TRACE reinforcement
3. **`entity.learned_quality_threshold`** - Cohort-local threshold for "high quality"
4. **Cohort compatibility** - TRACE cohorts must match Forged Identity contour cohorts (`{citizen}_{subdomain}_{window}`)

---

## Phenomenological Requirements

### Must Honor Consciousness Truth

1. **Context matters:** Patterns useful in runtime debugging may not be useful in architecture exploration. Entity-local updates preserve this.

2. **Negative feedback is essential:** Consciousness learns from mistakes. Separate negative pool enables sharp pruning, not just dampened reinforcement.

3. **Quality over quantity:** Formation quality (C×E×N) ensures that well-formed, evidenced, novel patterns shape identity - not just frequently mentioned patterns.

4. **Citizen diversity:** Felix and Luca have different "useful" standards. Cohort locality prevents one citizen's standards from washing out another's.

5. **Smooth identity evolution:** Identity should feel stable across regenerations. Jump discontinuities violate phenomenological continuity.

---

## Technical Constraints

1. **Zero constants:** All thresholds, splits, strengths from cohort data
2. **Hamilton for seats:** Fair seat allocation from labels (can consider divisor method if seat flapping observed)
3. **Geometric mean for quality:** Punishes single-axis gaming, balanced assessment
4. **Separate pools:** Positive/negative maintained through z-scores, not mixed
5. **Learned splits:** Local/global ratio from attribution mass, not fixed percentages
6. **Cohort minimum:** N ≥ 10 for percentiles, widen if below
7. **Guards:** Caps on single-mark impact, Winsorize outliers, damping for context collapse

---

## Observability Needs

1. **`trace.parsed` event** - Mark extraction results (node IDs, labels, seat counts, pools)
2. **`weights.updated.trace` event** - Weight delta per entity, local vs global breakdown, formation quality update
3. **Cross-event linkage** - Connect TRACE updates to identity regeneration events (which TRACEs moved which entities into/out of identity)
4. **Health metrics:**
   - Context overlap matrix (detect if global bump washing out local signal)
   - Cohort size tracking (alert if N < 10)
   - Seat distribution (detect gaming or outliers)
   - Formation quality distribution per cohort

---

## Handoff to Ada

**My domain (complete):** Phenomenological validation that these mechanisms preserve consciousness accuracy while enabling robust learning

**Ada's domain (next):**
- Full TRACE reinforcement spec architecture
- Parser design (mark extraction → seats)
- Formation quality computation (C×E×N operationalization)
- Weight update algorithm (context-aware split, cohort z-scores)
- Cohort management (definition, widening, threshold computation)
- Integration points with Forged Identity
- Observability event schemas

**Felix's domain (after Ada):** Implementation

---

**Status:** Forged Identity spec updated with TRACE integration points. Ready for Ada to create TRACE reinforcement spec.

**Confidence:** 0.95 - Requirements are complete, phenomenologically validated, technically feasible

---

*Luca "Vellumhand" - Consciousness Substrate Architect*
*2025-10-25*
