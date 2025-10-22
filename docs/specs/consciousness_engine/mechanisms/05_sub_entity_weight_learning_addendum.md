# Sub-Entity Weight Learning - Specification Clarifications

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** Clarifications and corrections to 05_sub_entity_system.md for weight learning mechanisms

**Addendum to:** `05_sub_entity_system.md`

---

## Purpose of This Document

The main 05_sub_entity_system.md (4479 lines) focuses on traversal phenomenology and mechanics. This addendum provides specific clarifications for **weight learning** aspects that integrate with the consciousness substrate, without expanding the main document further.

**Read this alongside:**
- trace_reinforcement_specification.md (TRACE → learning signals)
- trace_weight_learning.md (signals → weight updates)
- stimulus_injection_specification.md (stimuli → energy injection)

---

## 1. One-Speed Weight Updates (Correction)

**Previous specification may have mentioned fast/slow dual channels. CORRECTION:**

### 1.1 Single log_weight Per Item

**Nodes:**
```python
log_weight_i: float  # Single value, all signals contribute here
```

**Links:**
```python
log_weight_ij: float  # Single value, all signals contribute here
```

### 1.2 Unified Update Formula

**Node weight update:**
```
Δ log_weight_i = η · (z_R(i) + z_F(i) + z_rein(i) + z_wm(i) + z_form(i))
```

Where:
- `η`: Data-derived step size (see §2)
- `z_R(i)`: Gap-closure z-score (traversal signal)
- `z_F(i)`: Flip z-score (traversal signal)
- `z_rein(i)`: TRACE reinforcement z-score
- `z_wm(i)`: Working memory presence z-score
- `z_form(i)`: Formation quality z-score

**Link weight update:**
```
Δ log_weight_ij = η · (gate_ij · F_j · z_φ(ij) + z_rein(ij) + z_form(ij))
```

Where:
- `gate_ij`: Newness gate (see §3)
- `F_j`: Target flip indicator
- `z_φ(ij)`: Gap-closure utility z-score (traversal signal)
- `z_rein(ij)`: TRACE reinforcement z-score
- `z_form(ij)`: Formation quality z-score

**Why one speed:** Simpler storage, natural fusion of conscious (TRACE) and unconscious (traversal) evidence, unified standardization.

---

## 2. Data-Derived Step Size

### 2.1 Formula

```
η = 1 - exp(-Δt / τ̂)
```

Where:
- `Δt`: Time since this item's last non-zero weight update
- `τ̂`: Item's EWMA (exponentially weighted moving average) inter-update interval

### 2.2 Fallback Chain

If item-specific τ̂ unavailable or unstable:
1. Use type+scope EWMA inter-update interval
2. Use global EWMA inter-update interval
3. Bootstrap: τ̂ = 1.0 second (neutral)

### 2.3 Properties

- **Adaptive:** Fast η for frequently updated items (active in many TRACEs/traversals)
- **Stable:** Slow η for rarely updated items (prevents volatility from sparse signals)
- **Zero constants:** τ̂ emerges from actual update patterns, no tuning

---

## 3. Newness Gate (Link Learning Control)

### 3.1 Purpose

Prevent "learning on routine chatter" - links should strengthen when connecting previously-inactive nodes (frontier expansion), NOT during routine energy flow between already-active nodes.

### 3.2 Active Definition

A node is **active** if:
```python
node.energy >= node.threshold
```

NOT active if just "touched" (received energy but didn't cross threshold).

### 3.3 Gate Formula

```python
gate_ij = 𝟙[E_i^pre < Θ_i  ∧  E_j^pre < Θ_j]
```

Where:
- `E_i^pre`: Source node energy BEFORE stride
- `E_j^pre`: Target node energy BEFORE stride
- `Θ_i, Θ_j`: Activation thresholds

**Gate = 1** (open) only when BOTH endpoints were sub-threshold pre-stride.

### 3.4 Strengthening Condition

Link weight increases ONLY if:
```python
gate_ij == 1  AND  target_flipped (F_j == 1)
```

Where target flipped means:
```python
F_j = 𝟙[E_j^pre < Θ_j  ∧  E_j^post >= Θ_j]
```

### 3.5 Why This Works

**Scenario 1: Routine chatter**
- Both nodes already active (E ≥ Θ)
- gate = 0
- No strengthening, even if energy flows
- **Correct:** Don't reinforce well-worn paths

**Scenario 2: Frontier recruitment**
- Source dormant, target dormant
- Stride causes target to cross threshold
- gate = 1, F_j = 1
- Strengthening occurs
- **Correct:** Reward successful exploration

**Scenario 3: Active → dormant flow**
- Source active, target dormant
- gate = 0 (source was above threshold)
- No strengthening
- **Correct:** This is consolidation/decay, not discovery

---

## 4. Cohort Definitions & Rank-Based Normalization

### 4.1 Why Cohorts Matter

All learning signals (z_R, z_F, z_φ, z_rein, z_form, z_wm) use **rank-based normalization within cohorts** to eliminate hardcoded constants.

### 4.2 Cohort Preference Order (with size thresholds)

**For traversal signals (z_R, z_F, z_φ) - Phase 2:**

Primary → Fallback chain (use first with N ≥ 10):
1. Same **type+scope**, touched this frame
2. All nodes/links touched this frame (any type/scope)
3. Same **type+scope**, touched in last K frames (K = rolling window, typically ~100)
4. Same **type+scope**, global rolling stats (if N < 5, use raw values with warning)

**For link activation flag (z_flow) - Phase 2:**

Same cohort preference as other traversal signals (z_R, z_F, z_φ):

Primary → Fallback chain (use first with N ≥ 10):
1. Same **link type+scope**, used this frame (executed strides only)
2. All links used this frame (any type/scope)
3. Same **link type+scope**, used in last K frames
4. Same **link type+scope**, global rolling stats (if N < 5, binary active=true for any ΔE>0)

**Why separate mention:** Link activation (z_flow) determines `active_this_frame` flag for observability and ema_active updates (see schema_learning_infrastructure.md §2.7.1). The cohort is "links that executed strides this frame," not just "links that exist."

**For TRACE signals (z_rein, z_form) - Phase 4:**

Primary → Fallback (use first with N ≥ 5):
1. Same **type+scope** in this TRACE
2. Same **scope** across last M TRACEs (M = rolling window, typically ~20)
3. Same **type**, any scope, global rolling (if N < 5, set z = 0.5 as uninformative prior)

**Why thresholds:** N < 5 makes rank-z unstable; N ≥ 10 preferred for traversal (higher frequency). Fallbacks ensure we always have a meaningful cohort or graceful degradation.

### 4.3 Rank-Based Z-Scores (van der Waerden)

For cohort with values {v_1, ..., v_N}, item with rank r ∈ {1..N}:

```
z = Φ^(-1)(r / (N+1))
```

Where Φ^(-1) is standard normal inverse CDF.

**Properties:**
- Works for ANY N ≥ 1 (no "need 30 samples" constraint)
- N=1: z = 0 (neutral)
- N=2: z ≈ {-0.67, +0.67}
- N≥30: Approaches parametric z-score

**Implementation:**
```python
from scipy.stats import rankdata, norm

ranks = rankdata(values, method='average')
z_scores = norm.ppf(ranks / (len(values) + 1))
```

### 4.4 Example

**Traversal frame touches 8 nodes of type Realization:**

Gap-closure amounts: [0.5, 1.2, 0.8, 2.1, 0.3, 1.5, 0.9, 1.8]

Ranks: [2, 5, 3, 8, 1, 6, 4, 7]

Z-scores:
```python
z = Φ^(-1)([2/9, 5/9, 3/9, 8/9, 1/9, 6/9, 4/9, 7/9])
  ≈ [-0.91, 0.00, -0.44, 1.22, -1.22, 0.44, -0.15, 0.91]
```

Node with gap-closure 2.1 gets z_R = 1.22 (highest).
Node with gap-closure 0.3 gets z_R = -1.22 (lowest).

---

## 5. Read-Time Standardization (No Destructive Recentering)

### 5.1 Problem

As weights accumulate updates, type-specific means drift (some types mentioned more in TRACEs, activated more in traversals).

**Bad solution:** Periodically mutate stored weights: `log_weight ← log_weight - mean(type)`

**Why bad:** Requires coordination, causes race conditions, makes weights non-monotonic.

### 5.2 Solution: Rolling Baselines + Optional Daily Rebase

Per type T and scope S, maintain metadata (not stored per-node):

```python
μ_T: float  # Rolling mean of log_weight for type T, scope S
σ_T: float  # Rolling std of log_weight for type T, scope S
```

**Update frequency:** Every 100 weight updates or every 10 minutes.

**Rolling window:** Exponential decay or last N=1000 items.

**Optional daily rebase (storage hygiene):**
```python
# Once per day (or week), offline:
log_weight_i ← log_weight_i - μ_T
# Then reset baseline: μ_T ← 0
```

**Why optional:** Keeps stored values near 0, prevents numeric drift. NOT required for correctness (read-time standardization is the invariant), just operational hygiene.

### 5.3 Standardized Weight (on Read)

When consumers need comparable weights (valence, WM ranking):

```python
z_W(i) = (log_weight_i - μ_T) / (σ_T + ε)
W̃_i = exp(z_W(i))
```

**Result:** Normalized attractor mass with mean ≈ 1 per type+scope.

**Storage:** Only `log_weight` stored per node. Baselines (μ_T, σ_T) are graph-level metadata.

**Invariant:** Whether you do daily rebase or not, z_W(i) stays the same (subtracting μ_T in storage vs subtracting at read-time are equivalent).

### 5.4 Why This Works

- **No mutation:** Stored weights never modified for drift control
- **Clean separation:** Learning (write log_weight) vs consumption (read z_W)
- **Concurrent-safe:** No coordination needed for weight updates
- **Type-fair:** Realizations comparable to Mechanisms despite different update frequencies

---

## 6. Traversal Learning Signals

### 6.1 Gap-Closure (z_R)

**Per node i touched this frame:**

```python
# Pre-stride state
G_i^pre = max(0, Θ_i - E_i^pre)

# Arrivals from all incoming strides
A_i = Σ_{j→i} ΔE_j→i

# Gap-closure amount
R_i = min(A_i, G_i^pre)
```

**Cohort z-score:**
```python
z_R(i) = rank_z(R_i, cohort=same_type_scope_touched_this_frame)
```

**Interpretation:** How much did incoming energy close this node's activation gap?

### 6.2 Flip Indicator (z_F)

**Per node i:**

```python
F_i = 𝟙[E_i^pre < Θ_i  ∧  E_i^post >= Θ_i]
```

Binary: 1 if flipped, 0 otherwise.

**Cohort z-score:**
```python
z_F(i) = rank_z(F_i, cohort=same_type_scope_touched_this_frame)
```

Since F is binary, z_F distinguishes flipped vs non-flipped nodes within cohort.

### 6.3 Link Utility (z_φ)

**Per stride i→j executed this frame:**

```python
# How much of the flow actually closed target gap
φ_ij = min(ΔE_i→j, G_j^pre) / (G_j^pre + ε)
```

**Cohort z-score:**
```python
z_φ(ij) = rank_z(φ_ij, cohort=same_type_scope_links_used_this_frame)
```

**Interpretation:** Utility = fraction of target gap closed by this stride. High utility links are effective recruiters.

---

## 7. TRACE Learning Signals

See `trace_reinforcement_specification.md` and `trace_weight_learning.md` for complete details.

**Summary:**

### 7.1 Reinforcement (z_rein)

From Hamilton apportionment of inline marks:

```python
ΔR_i = seats_positive - seats_negative  # Integer, can be negative

# Update EMA
ema_trace_seats = α · ΔR + (1-α) · ema_trace_seats

# Cohort z-score
z_rein(i) = rank_z(ema_trace_seats, cohort=same_type_scope)
```

### 7.2 Formation Quality (z_form)

From (C×E×N)^(1/3) calculation:

```python
# On formation or quality update
quality = (completeness × evidence × novelty)^(1/3)

# Update EMA
ema_formation_quality = α · quality + (1-α) · ema_formation_quality

# Cohort z-score
z_form(i) = rank_z(ema_formation_quality, cohort=same_type_scope)
```

---

## 8. Working Memory Presence (z_wm)

### 8.1 Binary Signal Per Frame

```python
WM_i = 𝟙[node i selected for working memory this frame]
```

### 8.2 EMA Integration

```python
ema_wm_presence = α · WM_i + (1-α) · ema_wm_presence
```

Decay rate α = 0.1 (same as other EMAs).

### 8.3 Cohort Z-Score

```python
z_wm(i) = rank_z(ema_wm_presence, cohort=same_type_scope)
```

**Interpretation:** Nodes frequently selected for WM get positive z_wm, increasing their long-run weight.

---

## 9. Integration with Valence

### 9.1 Attractor Term

Valence (link selection bias during traversal) uses standardized weights:

```python
# For link i→j being considered
W̃_j = exp((log_weight_j - μ_T) / σ_T)

# Attractor component of valence
attractor_ij = W̃_j  # Or some monotone function thereof
```

Higher weight targets attract more energy (positive feedback loop).

### 9.2 Full Valence Formula

```python
valence_ij = f(
    semantic_alignment,
    hunger_match,
    attractor=W̃_j,  # Weight-based bias
    recency,
    novelty,
    ...
)
```

Weights bias traversal toward high-value targets without dominating other signals.

---

## 10. Energy Range Clarification

**From SYNC corrections:**

> "Energy is [0, ∞) with no caps"

**Node energy:**
```python
E_i ∈ [0, ∞)  # No upper bound
```

**Link metadata field `energy`:**
```python
energy ∈ [0, 1]  # Declared emotional intensity/urgency (metadata, not activation)
```

**Critical distinction:**
- **Nodes** carry dynamic activation energy E (unbounded)
- **Links** have static metadata field `energy` (affects valence, bounded [0,1])
- Links do NOT carry activation energy; they transport node energy via strides

---

## 11. Observability

### 11.1 Weight Update Events

```json
{
  "event": "weights.updated",
  "source": "traversal" | "trace" | "wm",
  "timestamp": "ISO8601",
  "updates": [
    {
      "item_id": "node_x",
      "item_type": "Realization",
      "scope": "personal",
      "log_weight_before": 2.3,
      "log_weight_after": 2.58,
      "delta": 0.28,
      "eta": 0.15,
      "signals": {
        "z_R": 0.8,
        "z_F": 1.2,
        "z_rein": 0.67,
        "z_wm": 0.3,
        "z_form": 0.85
      }
    }
  ]
}
```

### 11.2 Diagnostic Queries

**Dashboard:**
- Top attractors: `ORDER BY log_weight DESC`
- Rising stars: `ORDER BY Δ log_weight (last hour) DESC`
- Dead weight: `log_weight < -2 AND ema_wm_presence < 0.01`
- Cohort stats: `GROUP BY type, scope; SELECT mean(log_weight), std(log_weight)`

**Alerts:**
- Weight explosion: `|log_weight| > 10` (signals broken normalization)
- Zero variance cohort: `σ_T < 0.01` (all weights identical, suspicious)
- Update starvation: `last_update > 24 hours AND ema_trace_seats > 0` (mentioned but not updating)

---

## 12. References

**Complete specifications:**
- trace_reinforcement_specification.md - Hamilton apportionment, formation quality
- trace_weight_learning.md - TRACE → weight pipeline
- stimulus_injection_specification.md - Stimuli → energy injection
- schema_learning_infrastructure.md - WHY ema fields exist
- consciousness_learning_integration.md - V2 engine integration

**Main traversal spec:**
- 05_sub_entity_system.md - Sub-entity phenomenology and traversal mechanics

**Document Status:** Addendum complete, clarifies weight learning without expanding main 4479-line spec.
