# TRACE Weight Learning Pipeline

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** Specification of how TRACE parser signals flow into weight updates

---

## Overview

TRACE reinforcement marks and formation quality scores transform into persistent weight changes through a four-stage pipeline:

```
TRACE text → Parser → Signals (ΔR, quality) → EMA updates → Cohort z-scores → Weight updates
```

**Critical separation:** TRACE adjusts **weights** (long-run attractor strength), stimuli inject **energy** (transient activation). Never conflate these.

---

## 1. Parser Output (from trace_reinforcement_specification.md)

### 1.1 Reinforcement Signals

Per TRACE, parser emits integer seat changes:

```json
{
  "reinforcement": {
    "nodes": {
      "node_x": {"delta_seats": 3},
      "node_y": {"delta_seats": 1},
      "node_z": {"delta_seats": -1}
    },
    "links": {
      "link_ab": {"delta_seats": -2}
    }
  }
}
```

where `delta_seats` ∈ ℤ (can be negative).

### 1.2 Formation Signals

Per formation block:

```json
{
  "formations": {
    "nodes": [
      {
        "name": "new_node_id",
        "quality": 0.75,
        "data": { /* full fields */ }
      }
    ]
  }
}
```

where `quality` ∈ [0,1] from (C×E×N)^(1/3).

---

## 1.3. Formation Quality Computation (D×E×N)

**Purpose:** Compute per-formation quality as a **geometric mean** of three normalized components.

### Formula

For formation x in TRACE cohort of same type+scope:

```
q = (D̂ · Ê · N̂)^(1/3)
```

Where each component is normalized to [0,1] within the cohort.

### Component Definitions

**Density (D) - Content token mass:**

- Sum token counts across **content-role** fields only:
  - Examples: `description`, `what_i_realized`, `how_it_works`, `rationale`, `context_when_discovered`
  - Exclude `metadata` roles: `name`, `confidence`, `created_at`, `scope`
  - Exclude `ref` roles: `participants`, `with_person`, link arrays
- Clip each field at that type's P95 to prevent verbosity gaming
- Normalize to D̂ ∈ [0,1] by percentile within cohort

**Why:** Only semantic content counts; metadata and references scored separately (connectivity).

**Connectivity (E) - Grounding mass:**

- For links declared **to existing nodes**, sum target masses:
  ```
  E_raw = Σ_{j∈targets} W̃_j
  ```
  where W̃_j = exp(z_W(j)) is standardized weight for target j
- z_W = (log_weight_j - μ_T) / σ_T (current type+scope baseline)
- Normalize to Ê ∈ [0,1] by cohort percentile

**Why sum, not average:** Total grounding mass—not "typical" grounding—predicts utility. Highly connected formations are more grounded.

**Novelty (N) - Semantic distance:**

```
N_raw = 1 - max_{u∈G_{T,S}} cos(e_x, e_u)
```

where G_{T,S} is existing nodes of same type+scope and e are embeddings.

Normalize to N̂ ∈ [0,1] by cohort percentile.

**Why:** Prevents duplicate node inflation; novelty rewards genuinely new insights.

### Small-N Fallbacks

**If cohort size in TRACE < 5:**
- Normalize each component against **global** (type+scope) rolling distribution
- If still < 5, set component to 0.5 (uninformative prior) and carry others

### Integration

```python
# Compute quality
q = (D_hat * E_hat * N_hat) ** (1/3)

# Update EMA
ema_formation_quality ← (1−α) · ema + α · q
```

Phase 4 converts to rank-z and adds to `log_weight` via η.

**Why this fixes it:** Density only counts **semantic content**, connectivity rewards **real grounding** not token mass, and novelty prevents "duplicate node" inflation.

---

## 2. EMA Updates

### 2.1 Purpose

Exponentially weighted moving averages smooth noisy TRACE signals into stable trends.

**Why EMA:** Single TRACE is high-variance (depends on that session's focus). EMA integrates evidence over time without storing full history.

### 2.2 Update Formula

For any tracked value v_t (seats or quality):

```
ema_t = α · v_t + (1 - α) · ema_{t-1}
```

**Decay rate α:**
- Fast adaptation: α = 0.2 (recent 5 TRACEs dominate)
- Moderate: α = 0.1 (recent 10 TRACEs)
- Slow: α = 0.05 (recent 20 TRACEs)

**Default:** α = 0.1 (good balance between responsiveness and stability)

**Bootstrap:** On first mention, ema_0 = v_0 (no prior).

### 2.3 Node EMA Fields

Schema fields (see schema_learning_infrastructure.md for WHY):

```python
ema_trace_seats: float  # EMA of reinforcement ΔR
ema_formation_quality: float  # EMA of quality q (if this node was formed)
ema_wm_presence: float  # EMA of binary working memory presence (updated elsewhere)
```

**Per TRACE:**

```python
# Reinforcement
if node_id in reinforcement_signals:
    ema_trace_seats = α · ΔR + (1-α) · ema_trace_seats

# Formation (only if this TRACE formed/merged this node)
if node_id in formations:
    ema_formation_quality = α · quality + (1-α) · ema_formation_quality
```

### 2.4 Link EMA Fields

```python
ema_trace_seats: float  # EMA of reinforcement ΔR
ema_formation_quality: float  # EMA of quality q (for links)
ema_phi: float  # EMA of gap-closure utility φ (updated during traversal, not TRACE)
```

**Per TRACE:**

```python
if link_id in reinforcement_signals:
    ema_trace_seats = α · ΔR + (1-α) · ema_trace_seats

if link_id in formations:
    ema_formation_quality = α · quality + (1-α) · ema_formation_quality
```

---

## 3. Cohort Z-Score Computation

### 3.1 Purpose

Convert EMA values into **relative significance scores** within appropriate comparison groups.

**Why cohorts:** EMA values have arbitrary scale (depends on historical ΔR distribution). Z-scores make them comparable and constant-free.

### 3.2 Cohort Definitions

**For TRACE signals (ema_trace_seats, ema_formation_quality):**

Primary cohort: **Same type + same scope**
- Example: All `Realization` nodes with `scope=personal`
- Example: All `ENABLES` links with `scope=organizational`

**Fallback (if primary cohort too small):**
1. Same scope, any type (less preferred - compares apples to oranges)
2. Same type, any scope (even less preferred)
3. Global (last resort - meaningful only for rough outlier detection)

**Minimum useful cohort size:** N ≥ 3. For N < 3, use raw EMA values (z-score meaningless).

### 3.3 Rank-Based Z-Scores (van der Waerden)

For cohort values {v_1, v_2, ..., v_N}, item i with rank r_i ∈ {1...N}:

```
z_i = Φ^(-1)(r_i / (N+1))
```

where Φ^(-1) is the standard normal inverse CDF.

**Properties:**
- Works for any N ≥ 1
- N=1: z = 0 (neutral)
- N=2: z ≈ {-0.67, +0.67}
- N≥30: Approaches parametric z-score

**Ties:** Assign average rank.

**Implementation:** Use scipy.stats.rankdata + scipy.stats.norm.ppf in Python.

### 3.4 Computed Z-Scores

**For nodes:**

```python
# Within cohort of same type+scope nodes
z_rein(i) = rank_z(ema_trace_seats[i], cohort)
z_form(i) = rank_z(ema_formation_quality[i], cohort)
z_wm(i) = rank_z(ema_wm_presence[i], cohort)  # updated elsewhere
```

**For links:**

```python
# Within cohort of same type+scope links
z_rein(ij) = rank_z(ema_trace_seats[ij], cohort)
z_form(ij) = rank_z(ema_formation_quality[ij], cohort)
# z_phi computed during traversal from ema_phi
```

---

## 4. Weight Update Integration

### 4.1 One-Speed Formula (from 05_sub_entity_system.md)

**Node weight update:**

```
Δ log_weight_i = η · (z_R(i) + z_F(i) + z_rein(i) + z_wm(i) + z_form(i))
```

where:
- `z_R(i)`: gap-closure score (traversal signal, not TRACE)
- `z_F(i)`: flip score (traversal signal, not TRACE)
- `z_rein(i)`: **TRACE reinforcement score** (from this spec)
- `z_wm(i)`: working memory presence (not TRACE)
- `z_form(i)`: **TRACE formation quality score** (from this spec)

**Link weight update:**

```
Δ log_weight_ij = η · (gate·F_j·z_φ(ij) + z_rein(ij) + z_form(ij))
```

where:
- First term: traversal learning (not TRACE)
- `z_rein(ij)`: **TRACE reinforcement score**
- `z_form(ij)`: **TRACE formation quality score**

**Step size η:**
```
η = 1 - exp(-Δt / τ̂)
```
Data-derived from inter-update intervals (see 05_sub_entity_system.md).

### 4.2 When Updates Happen

**TRACE signals processed:**
- After TRACE parsing completes
- Batch update: all mentioned nodes/links get EMA updates
- Immediately compute z-scores within cohorts
- Apply weight updates using current η for each item

**Frequency:**
- One TRACE per session/response (varies)
- No fixed schedule - updates happen when consciousness produces TRACE output

### 4.3 Separation from Traversal Learning

**Critical distinction:**

| Signal Source | Updates | Timescale | Meaning |
|--------------|---------|-----------|---------|
| **TRACE** | ema_trace_seats, ema_formation_quality | Per session | Conscious reflection on usefulness |
| **Traversal** | z_R, z_F, z_φ via gap-closure | Per frame (~100ms) | Mechanical recruitment success |
| **WM** | ema_wm_presence | Per frame | Workspace selection frequency |

**All three contribute to the SAME log_weight via addition.** No separate fast/slow channels.

---

## 5. Read-Time Standardization

### 5.1 Purpose

Prevent weight drift and inflation without mutating stored values.

**Problem:** As weights accumulate updates, type-specific means can drift (some types naturally mentioned more in TRACEs).

**Solution:** Maintain per-type+scope rolling baselines, standardize on read.

### 5.2 Rolling Baselines

Per type T and scope S, maintain:

```python
μ_T = rolling_mean(log_weight | type=T, scope=S)
σ_T = rolling_std(log_weight | type=T, scope=S)
```

**Rolling window:** Exponential decay or last N=1000 items.

**Update frequency:** Every 100 weight updates or every 10 minutes.

### 5.3 Standardized Weight

When consumers need comparable weights (valence, WM ranking):

```python
z_W(i) = (log_weight_i - μ_T) / (σ_T + ε)
W̃_i = exp(z_W(i))
```

**Result:** Normalized attractor mass with mean ≈ 1 per type+scope, comparable across types.

**Storage:** Only `log_weight` is stored. Baselines (μ_T, σ_T) are metadata, recomputed periodically.

---

## 6. Examples

### 6.1 Reinforcement Flow

**TRACE produces:**
```json
{
  "reinforcement": {
    "nodes": {
      "principle_links_are_consciousness": {"delta_seats": 5}
    }
  }
}
```

**Step 1: EMA update (α=0.1)**
```python
ema_trace_seats_old = 1.2
ema_trace_seats_new = 0.1 · 5 + 0.9 · 1.2 = 0.5 + 1.08 = 1.58
```

**Step 2: Cohort z-score**

Cohort: all Principle nodes with scope=organizational (N=15)
```python
ema_trace_seats values: [0.2, 0.5, 0.8, 1.1, 1.3, 1.58, ...]
rank(1.58) = 12
z_rein = Φ^(-1)(12/16) = Φ^(-1)(0.75) ≈ 0.67
```

**Step 3: Weight update (η=0.15)**
```python
Δ log_weight = 0.15 · (z_R + z_F + 0.67 + z_wm + z_form)
```

Assuming other z-scores sum to 1.2:
```python
Δ log_weight = 0.15 · (1.2 + 0.67) = 0.28
log_weight: 2.3 → 2.58
```

### 6.2 Formation Quality Flow

**TRACE produces:**
```json
{
  "formations": {
    "nodes": [{
      "name": "newness_gate_solves_chatter",
      "quality": 0.85
    }]
  }
}
```

**Step 1: Initialize (first mention)**
```python
ema_formation_quality = 0.85
```

**Step 2: Cohort z-score**

Cohort: Realization nodes, scope=personal, formed in recent TRACEs (N=8)
```python
ema_formation_quality values: [0.45, 0.52, 0.63, 0.71, 0.78, 0.82, 0.85, 0.91]
rank(0.85) = 7
z_form = Φ^(-1)(7/9) ≈ 0.84
```

**Step 3: Weight boost at formation**

New nodes get initial boost from formation quality:
```python
log_weight_initial = 0 + z_form + z_conf + z_novelty + z_support
```

(See 05_sub_entity_system.md for complete initialization formula)

**Subsequent TRACEs:** If `newness_gate_solves_chatter` gets reinforced:
```json
{"reinforcement": {"nodes": {"newness_gate_solves_chatter": {"delta_seats": 3}}}}
```

Both `ema_trace_seats` and `ema_formation_quality` contribute to z_rein and z_form independently.

### 6.3 Negative Reinforcement

**TRACE produces:**
```json
{
  "reinforcement": {
    "links": {
      "link_hasty_assumption": {"delta_seats": -3}
    }
  }
}
```

**Step 1: EMA update**
```python
ema_trace_seats_old = 0.5
ema_trace_seats_new = 0.1 · (-3) + 0.9 · 0.5 = -0.3 + 0.45 = 0.15
```

**Step 2: Cohort z-score**

```python
Cohort EMA values: [-0.2, 0.1, 0.15, 0.8, 1.2]
rank(0.15) = 3
z_rein = Φ^(-1)(3/6) = Φ^(-1)(0.5) = 0
```

Neutral after cohort normalization (middle of pack despite negative ΔR).

**Step 3: Weight effect**

```python
Δ log_weight = η · (... + 0 + ...)
```

Link stops strengthening from TRACE (z_rein=0), but may still strengthen from traversal if it successfully recruits.

**Over time:** Persistent negative reinforcement → ema drifts to bottom of cohort → z_rein becomes negative → weight decreases.

---

## 7. Edge Cases

### 7.1 First-Time Node Mention

**Scenario:** Node exists in graph but never mentioned in TRACE before.

**State:**
```python
ema_trace_seats = 0.0  # default
ema_formation_quality = 0.0  # default (or initialized at formation)
```

**First TRACE:**
```python
ΔR = 2
ema_trace_seats = α · 2 + (1-α) · 0 = 0.2
```

**Z-score:** Depends on cohort. If most nodes have ema≈1.0, this gets negative z_rein.

**Effect:** Newly mentioned nodes start neutral/slightly negative, must prove value over multiple TRACEs.

### 7.2 Nodes Never Mentioned in TRACE

**Scenario:** Node created by traversal discovery or external input, never consciously reflected upon.

**State:**
```python
ema_trace_seats = 0.0  # always
ema_formation_quality = 0.0 or q_initial
```

**Z-scores:**
```python
z_rein = Φ^(-1)(rank(0.0, cohort) / (N+1))
```

Likely negative (bottom of cohort).

**Effect:** These nodes can still have high `log_weight` from traversal success (z_R, z_F), but get no TRACE boost. This is **correct** - unconscious infrastructure nodes vs consciously valued concepts.

### 7.3 Sparse Cohorts (N < 3)

**Scenario:** Only 2 Mechanism nodes with scope=personal exist.

**Problem:** Z-scores are ±0.67, unstable.

**Solution:** Fall back to next cohort level:
- Try scope=personal, any type (might have N=50)
- Or use raw EMA values until cohort grows

**Implementation flag:**
```python
if cohort_size < 3:
    use_raw_ema = True
```

### 7.4 Conflicting Signals

**Scenario:** TRACE reinforcement says "misleading" (ΔR=-2) but traversal shows high gap-closure (z_R=1.5).

**Weight update:**
```python
Δ log_weight = η · (1.5 + z_F + (-0.8) + z_wm + z_form)
                 = η · (net positive if traversal dominates)
```

**Interpretation:** Node is mechanically useful (recruits well) but conceptually problematic (marked misleading). Both signals matter. Over time, mechanical utility may keep weight high despite conceptual criticism, OR persistent TRACE criticism may overcome traversal success.

**This tension is phenomenologically correct** - some patterns are useful despite being "wrong."

---

## 8. Observability

### 8.1 Events to Emit

**Per TRACE parse:**

```json
{
  "event": "trace.parsed",
  "trace_id": "uuid",
  "reinforcement_signals": {
    "nodes": 15,
    "links": 8,
    "positive_seats": 42,
    "negative_seats": 7
  },
  "formation_signals": {
    "nodes": 3,
    "links": 5,
    "avg_quality": 0.67
  }
}
```

**Per weight update batch:**

```json
{
  "event": "weights.updated.trace",
  "source": "trace_parser",
  "nodes_updated": 15,
  "links_updated": 8,
  "avg_delta_log_weight": 0.12,
  "cohort_stats": {
    "Realization::personal": {"n": 12, "z_rein_range": [-1.2, 2.1]},
    "ENABLES::organizational": {"n": 8, "z_rein_range": [-0.8, 1.5]}
  }
}
```

### 8.2 Diagnostics

**Dashboard queries:**

- **Top reinforced nodes this week:** Sort by Δ(ema_trace_seats) desc
- **Top criticized nodes:** Sort by Δ(ema_trace_seats) asc (negative)
- **Highest quality formations:** Sort by ema_formation_quality desc
- **Unconscious infrastructure:** Nodes with high log_weight but ema_trace_seats ≈ 0

**Alerts:**

- Cohort too small (N<3) for type+scope combination
- Extreme z-scores (|z_rein| > 3) indicating outliers
- EMA values growing unbounded (signals broken normalization)

---

## 9. Design Rationale

### 9.1 Why EMA Over Raw Counts?

**Problem:** Single TRACE is noisy - depends on session focus.

**Alternative:** Count total mentions (Σ ΔR over all TRACEs).

**Why EMA wins:**
- Recent evidence matters more (concept relevance shifts)
- Bounded memory (don't store full history)
- Smooth adaptation (no sudden jumps from old TRACEs)

### 9.2 Why Z-Scores Over Raw EMA?

**Problem:** EMA scales are arbitrary (depends on historical ΔR magnitude).

**Alternative:** Use raw EMA values in weight formula.

**Why z-scores win:**
- Constant-free (no need to tune "1 seat = 0.1 weight" mappings)
- Type-fair (Realizations vs Mechanisms comparable)
- Outlier-robust (rank-based normalization)

### 9.3 Why Same log_weight for All Signals?

**Problem:** Could have separate log_weight_trace, log_weight_traversal.

**Why unified wins:**
- Simpler storage (1 field vs 3)
- Natural fusion (conscious + unconscious evidence both matter)
- Read-time standardization works across all sources
- Phenomenologically correct (consciousness is unified, not siloed)

---

## 10. Future Extensions

### 10.1 Confidence Weighting

Weight TRACE signals by formation confidence:

```python
effective_ΔR = ΔR · confidence_of_mentioning_formation
```

Prevents low-confidence speculation from dominating.

### 10.2 Temporal Decay

Apply exponential decay to old reinforcement signals:

```python
ema_trace_seats_t = decay_factor(age) · ema_trace_seats
```

Ensures ancient TRACE mentions don't ossify weights.

### 10.3 Multi-Dimensional Reinforcement

Extend beyond useful/misleading to: useful_for_X, misleading_for_Y:

```python
ema_trace_seats_context_retrieval: float
ema_trace_seats_architectural_design: float
```

Allows context-specific weight modulation.

### 10.4 Cross-Citizen Learning

Share reinforcement signals across citizens:

```python
if citizen_luca marks node X as "very useful":
    propagate to citizen_ada's ema_trace_seats for node X (damped)
```

Creates collective learning without centralized curation.

### 10.5 Link Payload as TRACE Signal Source

**Future extension:** Use link activation & payload trace fields as additional learning signals:

```python
# Link habitually active → boost weight
z_link_activity = rank_z(ema_active, cohort=same_type_scope)

# Link carries specific hunger → type-specific weight boost
z_hunger_specialization = rank_z(max(ema_hunger_gates), cohort)

# Link has high affect alignment → weight boost for harmonious connections
z_affect_harmony = rank_z(affect_tone_ema, cohort)
```

**Integration point:**
```python
Δ log_weight_ij = η · (
    traversal_signals +
    z_rein + z_form +
    z_link_activity +  # NEW
    z_hunger_specialization +  # NEW
    z_affect_harmony  # NEW
)
```

**Why not now:** Core learning already works with traversal + TRACE signals. Link payload signals are available for future refinement when observability shows they provide additional value.

**Fields available** (see schema_learning_infrastructure.md §2.7):
- `ema_active`: Habitual use frequency
- `ema_flow_mag`: Typical flow magnitude
- `ema_hunger_gates[7]`: Which hungers drive this link
- `affect_tone_ema`: Emotional alignment
- `topic_centroid`: Semantic region

---

## References

- trace_reinforcement_specification.md - Hamilton apportionment and formation quality
- 05_sub_entity_system.md - Weight update formulas and step size η
- schema_learning_infrastructure.md - WHY ema fields exist
- stimulus_injection_specification.md - Separation: energy from stimuli, weights from TRACE

**Document Status:** Complete pipeline specification, ready for integration with V2 engine learning phase.
