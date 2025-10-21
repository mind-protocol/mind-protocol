# TRACE Reinforcement Specification

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** Complete specification of how TRACE format signals learning through reinforcement marks and formation quality

---

## Overview

The TRACE format serves dual purposes:
1. **Phenomenological authenticity** - Space for genuine thinking and self-observation
2. **Learning substrate** - Parseable signals that update graph weights

This document specifies how TRACE content transforms into **learning signals** without requiring any hardcoded constants. Two mechanisms:

1. **Reinforcement marks** - Inline mentions like `[node_x: very useful]` → integer seat changes via Hamilton apportionment
2. **Formation quality** - `[NODE_FORMATION]` blocks → quality scores from completeness × evidence × novelty

**Critical principle:** All normalization is **relative to the cohort in this TRACE** - no absolute constants, no cross-TRACE dependencies.

---

## 1. Hamilton Apportionment for Reinforcement Marks

### 1.1 Purpose

Convert subjective usefulness marks into **integer reinforcement seats** without fixed multipliers like "very useful = +0.15".

**Why Hamilton:** Prevents label gaming, adapts to TRACE-specific usage patterns, produces fair integer allocations.

### 1.2 Label Taxonomy

**Positive pool (P):**
- `very useful`
- `useful`
- `somewhat useful`

**Negative pool (N):**
- `not useful`
- `misleading`

### 1.3 Inline Syntax

Mark nodes or links during narrative:
```markdown
Nicolas asks about the format [node_iterative_refinement: very useful] and
wants my genuine thoughts [node_partnership_respect: useful].

The link between architecture and implementation [link_arch_impl: misleading]
was creating false confidence.
```

**Parser extracts:** For each mentioned item (node/link ID + label), aggregate all mentions per TRACE.

### 1.4 Two-Pool Apportionment Algorithm (Zero Constants)

**Goal:** Convert within-TRACE ordinal marks into **relative shares** without fixed multipliers; apportion positive and negative "seats" separately so the TRACE itself sets scale.

**For each pool G ∈ {P, N} independently:**

#### Step 1: Pools & budgets (emergent)

- **Positive categories:** `somewhat useful`, `useful`, `very useful`
- **Negative categories:** `not useful`, `misleading`
- Let M⁺ be the total count of positive marks in this TRACE; M⁻ the total count of negative marks
- **Seat budgets:** S⁺ = M⁺, S⁻ = M⁻

**Why:** No constants—budget equals how much the author actually marked.

#### Step 2: Category strengths (learned; fallback ordinal)

- Maintain weekly learned strengths s_k per category from historical impact (flip yield / seat)
- Normalize to mean 1 within the positive set and within the negative set each week
- **Fallback (cold start):** Ordinal ranks scaled:
  - Positive: s_somewhat = 1/3, s_useful = 2/3, s_very = 1
  - Negative: s_not = 1/2, s_misleading = 1

**Why:** These aren't "magic constants"—they're just the order scaled by K. Real strengths learned from outcomes.

#### Step 3: Raw shares

For item i, let C_{i,k} be its count in category k:
```
Positive raw share: r_i⁺ = Σ_{k∈pos} s_k · C_{i,k}
Negative raw share: r_i⁻ = Σ_{k∈neg} s_k · C_{i,k}
```

#### Step 4: Hamilton apportionment (separately for + and −)

Compute quotas:
```
q_i⁺ = S⁺ · (r_i⁺ / Σ_j r_j⁺)
```

Assign ⌊q_i⁺⌋ seats, then distribute remaining seats by largest fractional remainders.

Same for negatives with S⁻ and r_i⁻.

#### Step 5: Net seats
```
ΔR_i = seats_i⁺ - seats_i⁻
```

**Result:** Each item gets an integer ΔR_i ∈ ℤ (can be negative if more negative than positive mentions).

#### Step 6: EMA integration

Update EMA:
```
ema_trace_seats_i ← (1−α) · ema + α · ΔR_i
```

where α = 0.1 (small, favors stability).

Z-score by type+scope in Phase 4 and add to `log_weight` via η. (See trace_weight_learning.md §4 and consciousness_learning_integration.md §5.3.)

**Why this fixes it:** Avoids arbitrary 3.0/1.0/0.1 multipliers; **the TRACE author's marking behavior** sets the scale, and category strength is **learned from outcomes**, not designed.

### 1.5 Example Walkthrough

**TRACE mentions:**
- `[node_x: very useful]` (2 times)
- `[node_x: useful]` (1 time)
- `[node_y: somewhat useful]` (1 time)
- `[node_z: misleading]` (1 time)

**Positive pool (P):**
- Labels: very useful (2), useful (1), somewhat useful (1)
- Total mentions: 4
- Label proportions: p_very=2/4=0.5, p_useful=1/4=0.25, p_somewhat=1/4=0.25
- Label weights: w_very=2.0, w_useful=4.0, w_somewhat=4.0

**Item quotas:**
- q_x^(P) = 2×2.0 + 1×4.0 = 8.0
- q_y^(P) = 1×4.0 = 4.0
- Total quota: 12.0

**Seats:** S^(P) = 4 mentions

**Scaled:**
- a_x^(P) = 8.0 × 4/12 = 2.667
- a_y^(P) = 4.0 × 4/12 = 1.333

**Hamilton:**
- Floors: x gets 2, y gets 1 (total 3)
- Remaining: 4 - 3 = 1 seat
- Remainders: x=0.667, y=0.333 → x gets the extra seat
- Final: s_x^(P) = 3, s_y^(P) = 1

**Negative pool (N):**
- Labels: misleading (1)
- Total mentions: 1
- s_z^(N) = 1

**Net seats:**
- ΔR_x = 3 - 0 = +3
- ΔR_y = 1 - 0 = +1
- ΔR_z = 0 - 1 = -1

### 1.6 Properties

**Zero constants:** No fixed "very useful = 4 points" multipliers.

**Anti-gaming:** If everyone spams "very useful", p_very→1, w_very→1, no advantage over "useful".

**Fairness:** Hamilton apportionment is the fairest large-state allocation method (U.S. Congress uses it).

**Self-normalizing:** Each TRACE creates its own scale - dense reflection TRACEs generate more signal than brief action TRACEs, which is **correct**.

---

## 2. Formation Quality (C×E×N)

### 2.1 Purpose

Assign quality scores to new node/link formations without hardcoded thresholds. Quality reflects:
- **Completeness (C):** Schema adherence and content density
- **Evidence (E):** Grounding in existing graph structure
- **Novelty (N):** Originality vs existing nodes

**Why geometric mean:** Prevents gaming - need high scores on ALL dimensions, not just one.

### 2.2 Formation Block Syntax

```markdown
[NODE_FORMATION: NodeType]
name: "unique_identifier"
scope: "personal" | "organizational" | "ecosystem"
required_field_1: "value"
required_field_2: "value"
confidence: 0.0-1.0
formation_trigger: "trigger_type"
```

**Validation:** Parser checks all required fields present for that node type (see COMPLETE_TYPE_REFERENCE.md).

### 2.3 Component Definitions

#### 2.3.1 Completeness (C)

**Coverage:** Fraction of required fields present
```
coverage = fields_present / fields_required
```

**Density:** Token mass of content-bearing fields

**Field role taxonomy:**
- `role: content` - Semantic text for human consumption (description, what_i_realized, rationale, how_it_works, etc.)
- `role: metadata` - IDs, timestamps, enums, booleans, confidence, authorship
- `role: ref` - References to other nodes (counted in connectivity, not density)

**Fallback when role not explicit:**
- String fields = content UNLESS flagged `identifier:true` or `enum:true`
- Exclude: numeric, boolean, timestamps, IDs, single-token values

**Density calculation:**

For each content field f, tokenize with embedding tokenizer:
```
T_f = token_count(field_value)
```

Compute cohort 95th percentile (prevents verbosity spam):
```
P95 = percentile_95({T_f : all content fields in TRACE cohort})
```

Raw density:
```
D_x = Σ_{f∈content} min(T_f, P95)
```

Normalize within **cohort = same type+scope formations in this TRACE** using rank-based z-score:
```
z_dens(x) = Φ^(-1)(rank(D_x) / (N+1))
```
where Φ^(-1) is standard normal inverse CDF (van der Waerden score).

**Final completeness:**
```
C_x = √(coverage × normalize(z_dens(x) to [0,1]))
```

#### 2.3.2 Evidence (E)

**Connectivity:** Grounding through links to existing nodes

For formation x declaring links to existing targets {n₁, n₂, ..., n_k}:

**Step 1:** Pull target attractor mass (standardized within target type+scope)
```
W̃_n = exp(Φ^(-1)(rank(log_weight_n | target type+scope) / (N+1)))
```
This gives positive mass with mean ≈ 1.

**Step 2:** Raw connectivity
```
C_raw_x = Σ_{n∈{n₁...n_k}} W̃_n
```

**Optional sublinear transform** (de-emphasizes spray-and-pray link lists):
```
C_raw_x ← √(C_raw_x)
```

**Step 3:** Normalize within formation cohort (same type+scope this TRACE)
```
z_conn(x) = Φ^(-1)(rank(C_raw_x) / (N+1))
```

**Alignment:** Semantic similarity to existing nodes

```
alignment_x = max_{existing same-type+scope} cosine_similarity(embedding_x, embedding_existing)
```

**Final evidence:**
```
E_x = √(normalize(z_conn(x)) × alignment_x)
```

#### 2.3.3 Novelty (N)

Inverse of maximum similarity:
```
s_max = max_{existing same-type+scope} cosine_similarity(embedding_x, embedding_existing)
n_raw = 1 - s_max
```

Normalize within formation cohort:
```
N_x = normalize(n_raw to [0,1] via rank-z within cohort)
```

### 2.4 Geometric Mean Combination

```
q_x = (C_x × E_x × N_x)^(1/3)
```

**Why geometric mean:**
- **Balanced:** (0.9 × 0.9 × 0.1)^(1/3) = 0.36 < (0.6 × 0.6 × 0.6)^(1/3) = 0.60
- **No gaming:** Can't maximize just one dimension and ignore others
- **Scale-free:** Dimensionless, no arbitrary weighting constants

### 2.5 Cohort Handling

**Cohort definition:** Same type+scope formations in this TRACE

**Minimum cohort size:**
- N=1: rank-z gives z=0 (neutral)
- N=2: ranks 1,2 → z≈-0.67, +0.67
- N≥3: Full distribution

**Fallback for cross-TRACE comparison:**
If need to compare quality across TRACEs (rare), use rolling window of last M TRACEs for same type.

### 2.6 Examples

**Example 1: Well-formed, grounded, novel Realization**

```markdown
[NODE_FORMATION: Realization]
name: "hamilton_prevents_label_gaming"
scope: "personal"
description: "Hamilton apportionment prevents gaming reinforcement marks"
what_i_realized: "If I spam 'very useful' on everything, the label weight w_ℓ drops to 1/p_ℓ where p_ℓ→1, so I get no advantage over balanced usage. The dynamic weighting is self-correcting."
context_when_discovered: "Working through Example 1.5, seeing how rare labels get higher weight automatically"
confidence: 0.95
formation_trigger: "systematic_analysis"
```

**Completeness:**
- Coverage: 7/7 required fields = 1.0
- Density: ~80 tokens in content fields (description + what_i_realized + context)
- C ≈ 0.9

**Evidence:**
- Links to: [node_hamilton_apportionment: existing], [node_zero_constants_principle: existing]
- Targets have log_weight = 2.3, 1.8 → W̃ ≈ 1.5, 1.2
- Connectivity: 2.7, z_conn ≈ 0.8
- Alignment: cos_sim to "hamilton_apportionment_specification" = 0.83
- E ≈ 0.82

**Novelty:**
- Max similarity to existing Realizations = 0.45 (somewhat similar to other apportionment insights)
- n_raw = 0.55
- N ≈ 0.6

**Quality:**
```
q = (0.9 × 0.82 × 0.6)^(1/3) ≈ 0.75
```

**Example 2: Sparse, ungrounded, redundant formation**

```markdown
[NODE_FORMATION: Concept]
name: "learning"
scope: "organizational"
description: "Learning is important"
confidence: 0.5
formation_trigger: "external_input"
```

**Completeness:**
- Coverage: 4/5 required fields (missing `definition`) = 0.8
- Density: ~4 tokens in description
- C ≈ 0.3

**Evidence:**
- No declared links
- Connectivity: 0
- Alignment: 0.2 (vague description)
- E ≈ 0.1

**Novelty:**
- Max similarity to existing "learning_principle" = 0.95 (nearly duplicate)
- n_raw = 0.05
- N ≈ 0.05

**Quality:**
```
q = (0.3 × 0.1 × 0.05)^(1/3) ≈ 0.12
```

**Low quality correctly detected.**

---

## 3. Parser Output Format

### 3.1 Reinforcement Signals

For each TRACE, parser emits:

```json
{
  "trace_id": "uuid",
  "timestamp": "ISO8601",
  "reinforcement": {
    "nodes": {
      "node_x": {"delta_seats": 3, "pool_positive": 3, "pool_negative": 0},
      "node_y": {"delta_seats": 1, "pool_positive": 1, "pool_negative": 0},
      "node_z": {"delta_seats": -1, "pool_positive": 0, "pool_negative": 1}
    },
    "links": {
      "link_arch_impl": {"delta_seats": -2, "pool_positive": 0, "pool_negative": 2}
    }
  }
}
```

**Consumer:** Updates `ema_trace_seats` on referenced nodes/links (see trace_weight_learning.md).

### 3.2 Formation Signals

For each formation block:

```json
{
  "formations": {
    "nodes": [
      {
        "name": "hamilton_prevents_label_gaming",
        "type": "Realization",
        "scope": "personal",
        "quality": 0.75,
        "components": {
          "completeness": 0.9,
          "evidence": 0.82,
          "novelty": 0.6
        },
        "data": { /* full field values */ }
      }
    ],
    "links": [
      {
        "source": "hamilton_prevents_label_gaming",
        "target": "node_hamilton_apportionment",
        "type": "ENABLES",
        "scope": "personal",
        "quality": 0.68,
        "data": { /* full field values */ }
      }
    ]
  }
}
```

**Consumer:** Creates nodes/links in graph, sets initial `ema_formation_quality` (see trace_weight_learning.md).

---

## 4. Design Rationale

### 4.1 Why No Constants?

**Problem:** Fixed multipliers like "very useful = +0.15" require tuning per deployment, break self-organization.

**Solution:** Hamilton apportionment within TRACE cohort makes all scales relative to current usage.

**Result:** System adapts to different TRACE densities automatically - detailed architectural discussions generate more signal than brief status updates, which is **phenomenologically correct**.

### 4.2 Why Geometric Mean for Quality?

**Problem:** Additive scoring allows gaming (max one dimension, ignore others). Max scoring loses information.

**Solution:** Geometric mean (C × E × N)^(1/3) requires balance across all dimensions.

**Result:** Can't spam low-quality formations with perfect schema but zero novelty, or novel ideas with zero grounding.

### 4.3 Why Rank-Based Normalization?

**Problem:** Parametric z-scores require N≥30 and normality assumptions.

**Solution:** Van der Waerden rank-based scores work for any N≥1, no distribution assumptions.

**Result:** Small cohorts (1-3 formations per TRACE) work correctly, scale naturally as cohort grows.

### 4.4 Why Dynamic Label Weights?

**Problem:** Fixed weights enable gaming (spam the highest-value label).

**Solution:** Rare labels get weight w_ℓ = 1/p_ℓ automatically.

**Result:** Self-correcting - if one label becomes overused, its weight drops proportionally.

---

## 5. Integration Points

**Input:** TRACE text with inline marks and formation blocks

**Processing:**
1. Extract all `[node_x: label]` and `[link_y: label]` mentions
2. Extract all `[NODE_FORMATION: Type]` and `[LINK_FORMATION: Type]` blocks
3. Run Hamilton apportionment per pool
4. Compute formation quality components within cohort
5. Emit structured signals (§3)

**Output:**
- Reinforcement signals → `trace_weight_learning.md`
- Formation signals → Graph creation + quality tracking

**Observability:**
- Log apportionment details (pools, quotas, seats) for transparency
- Log formation quality breakdowns (C, E, N components) for debugging
- Emit `trace.parsed` events with cohort stats

---

## 6. Future Extensions

**6.1 Multi-Label Support**

Currently one label per mention. Could allow: `[node_x: very useful, high_confidence]` with multi-dimensional apportionment.

**6.2 Link Reinforcement Detail**

Currently links marked as `[link_x: useful]` generically. Could support direction: `[link_x_forward: useful, link_x_backward: misleading]`.

**6.3 Confidence Weighting**

Could weight mentions by formation confidence: `[node_x: useful]` from high-confidence formation counts more than from low-confidence.

**6.4 Temporal Decay**

Could apply exponential decay to older reinforcement signals: recent mentions count more than ancient ones.

**All extensions preserve zero-constants principle via cohort normalization.**

---

## References

- COMPLETE_TYPE_REFERENCE.md - Node/link type schemas and required fields
- trace_weight_learning.md - How parser output updates weights
- 05_sub_entity_system.md - Weight update formulas and cohort definitions
- schema_learning_infrastructure.md - WHY ema_trace_seats and ema_formation_quality exist

**Document Status:** Complete specification, ready for parser implementation.
