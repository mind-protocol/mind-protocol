# Skeleton Verification Against Main Specification

**Date:** 2025-10-20
**Spec Reference:** `docs/specs/consciousness_engine_architecture/mechanisms/05_sub_entity_system.md`
**Purpose:** Verify each skeleton matches the specification exactly

---

## ✅ AI #1: sub_entity_core.py

**Specification Lines:**
- EntityExtentCentroid: Lines 1961-1974 (semantic diversity measurement)
- ROITracker: Lines 1935-1947 (convergence detection)
- QuantileTracker: Lines 1975-1988 (integration sensing)
- SubEntity: Throughout Part 1

### EntityExtentCentroid - VERIFIED ✅

**Spec Requirement (lines 1961-1974):**
> "For an entity with active nodes N₁, N₂, ..., Nₘ, extract their embeddings E₁, E₂, ..., Eₘ. Compute the pairwise cosine similarity matrix S where S[i,j] = cosine(Eᵢ, Eⱼ).
>
> Average all off-diagonal elements of S to get mean pairwise similarity σ_extent."

**Skeleton Implementation:**
- ✅ `add_node()` - incremental centroid update (lines 44-68)
- ✅ `remove_node()` - decremental update (lines 70-101)
- ✅ `distance_to()` - 1 - cos(embedding, centroid) (lines 103-131)
- ✅ `_update_dispersion()` - mean(1 - cos(e, centroid)) (lines 133-144)

**ISSUE FOUND:** ⚠️ Spec uses PAIRWISE similarity (O(m²)), skeleton uses CENTROID-based dispersion (O(m)).

**From PARALLEL_DEVELOPMENT_PLAN:**
> "Phase 3: Test Centroid Dispersion... Compare centroid dispersion vs pairwise similarity (ground truth)"

**Resolution:** This is an intentional optimization trade-off to be validated empirically (Task 23). Centroid-based is O(m) vs O(m²) pairwise. If empirical testing shows centroid is "good enough proxy," keep it. Otherwise, revert to pairwise.

**Verdict:** ✅ VERIFIED with empirical validation required (Task 23)

---

### ROITracker - VERIFIED ✅

**Spec Requirement (lines 1941-1942):**
> "Convergence detection: All remaining frontier edges have valence scores below a dynamic convergence threshold. This threshold is derived from the distribution of recent stride outcomes - if the last N strides produced minimal energy changes or activation threshold crossings, raise the valence floor required to continue."

**Skeleton Implementation:**
- ✅ `push()` - record stride ROI (lines 166-173)
- ✅ `lower_whisker()` - Q1 - 1.5 × IQR (lines 175-192)
- ✅ Window size 256 (appropriate for rolling statistics)

**MATCH:** Skeleton correctly implements convergence threshold as lower whisker of ROI distribution.

**Verdict:** ✅ VERIFIED

---

### QuantileTracker - VERIFIED ✅

**Spec Requirement (lines 1975-1988):**
> "The crossover point (weak vs strong) is determined by recent dissolution statistics: entities below the 25th percentile of total energy among recently-successful (non-dissolved) entities are 'weak'. Above 75th percentile are 'strong'."

**Skeleton Implementation:**
- ✅ `update()` - add sample to rolling window (lines 215-222)
- ✅ `quantile()` - compute p-th quantile (lines 224-238)
- ✅ Window size 100 (appropriate for population tracking)

**MATCH:** Provides Q25/Q75 computation for weak/strong determination.

**Verdict:** ✅ VERIFIED

---

### SubEntity - VERIFIED ✅

**Spec Requirement:** Throughout specification, particularly:
- Lines 1503-1531 (Core Definition)
- Lines 1532-1548 (Naming Convention)
- Lines 1549-1582 (Entity Lifecycle)

**Skeleton Implementation:**
- ✅ extent: Set[int] - nodes above threshold (line 266)
- ✅ frontier: Set[int] - extent ∪ 1-hop (line 267)
- ✅ energies: Dict[int, float] - per-node energy (line 270)
- ✅ thresholds: Dict[int, float] - per-node threshold (line 271)
- ✅ quota_assigned / quota_remaining (lines 274-275)
- ✅ roi_tracker: ROITracker (line 278)
- ✅ centroid: EntityExtentCentroid (line 281)
- ✅ rho_local_ema (line 284)
- ✅ hunger_baselines: Dict[str, (μ, σ)] (lines 287-296)

**MATCH:** All required state variables present.

**TODO markers:**
- `update_extent()` - needs implementation (lines 310-321)
- `compute_size()` - needs implementation (lines 323-337)

**Verdict:** ✅ VERIFIED (with TODOs for AI #1 to complete)

---

## ✅ AI #2: quotas.py

**Specification Lines:** 1671-1741 (Hamilton's Method + Zippered Scheduling)

### compute_modulation_factors() - VERIFIED ✅

**Spec Requirement (lines 1676-1695):**
> "Weight Computation (Per-Entity):
>
> For each entity `e`, compute allocation weight:
>
> ```
> w_e = (1 / |extent_e|) × u_e × r_e × h_e
> ```
>
> Where:
> - `1/|extent_e|`: Inverse of active extent size
> - `u_e`: Urgency factor (recent focal stimulus matching semantic space)
> - `r_e`: Reachability factor (estimated proximity to workspace)
> - `h_e`: Health factor (local spectral radius guard)
>
> **CRITICAL**: Factors `u_e`, `r_e`, `h_e` are **normalized to mean 1.0 per-frame**"

**Skeleton Implementation:**
- ✅ Function signature matches (lines 20-24)
- ✅ TODO includes normalization requirement (lines 43-44)
- ✅ Optional shrinkage noted (lines 47-48)

**Verdict:** ✅ VERIFIED (with TODO for AI #2)

---

### hamilton_quota_allocation() - VERIFIED ✅

**Spec Requirement (lines 1696-1720):**
> "Hamilton Quota Allocation:
>
> Given total frame budget `Q_total` and per-entity weights `w_e`:
>
> 1. Compute initial fractional quotas
> 2. Take integer parts
> 3. Compute remainder to distribute
> 4. Sort entities by fractional remainder descending
> 5. Give one additional stride to the top R entities"

**Skeleton Implementation:**
- ✅ Function signature matches (lines 52-56)
- ✅ Algorithm steps documented (lines 70-75)
- ✅ Zero-constants noted (line 78)

**Verdict:** ✅ VERIFIED (with TODO for AI #2)

---

### allocate_quotas() - VERIFIED ✅

**Spec Requirement (lines 1671-1695):**
> Formula: `w_e = (1 / |extent_e|) × u_e × r_e × h_e`

**Skeleton Implementation:**
- ✅ Function signature matches (lines 82-87)
- ✅ Formula documented (lines 102-104)
- ✅ Steps outlined (lines 107-112)

**Verdict:** ✅ VERIFIED (with TODO for AI #2)

---

## ✅ AI #4: valence.py

**Specification Lines:** 1743-1824 (Surprise-Gated Composite Valence)

### Hunger Functions - VERIFIED ✅

**Spec Requirement (lines 1769-1816):**

Per-edge hunger scores with exact formulas:

1. **Homeostasis** (lines 1771-1777):
   - Formula: `G_j / (S_i + G_j + ε)`
   - ✅ Skeleton lines 23-53: Correct formula documented

2. **Goal** (lines 1779-1782):
   - Formula: `cos(E_j, E_goal)`
   - ✅ Skeleton lines 56-88: Correct formula documented (with max(0, ...) which is stricter)

3. **Completeness** (lines 1789-1794):
   - Formula: `1 - cos(E_j, extent_centroid)`
   - ✅ Skeleton lines 91-122: Correct formula documented

4. **Ease** (lines 1812-1816):
   - Formula: `w_ij / (Σ_k w_ik + ε)`
   - ⚠️ Skeleton lines 124-154: Uses `w_ij / max(w_ik)` instead of sum

**ISSUE FOUND:** Ease hunger formula mismatch.

**Spec says:** `ν_ease = w_ij / (Σ_k w_ik + ε)` (proportion of total outgoing weight)
**Skeleton says:** `w_ij / max(w_ik for k in neighbors)` (proportion of maximum weight)

**Impact:** Ease score will be higher in skeleton version when there are many low-weight edges (sum >> max).

**Resolution Required:** Change skeleton to match spec:
```python
# ν_ease = w_ij / Σ_k w_ik (proportion of total outgoing)
neighbors = graph.out_edges(source_i)
total_weight = sum(graph.get_edge_weight(source_i, k) for k in neighbors)
return w_ij / (total_weight + 1e-9)
```

**Verdict:** ⚠️ NEEDS CORRECTION - ease hunger formula

5. **Identity** (lines 1784-1787):
   - ⚠️ Spec: `cos(E_j, E_id)` where E_id is "entity's semantic signature"
   - ⚠️ Skeleton lines 157-188: Uses "highest-energy node in extent" as center

**ISSUE FOUND:** Identity hunger definition mismatch.

**Spec says:** E_id is entity's semantic signature (centroid)
**Skeleton says:** E_center is highest-energy node

**Impact:** Different semantic center definition.

**Resolution:** Spec is unclear which is correct. Need clarification:
- Option A: Identity = coherence around centroid (same as entity signature)
- Option B: Identity = coherence around strongest node (creates "anchor")

**Recommend Option A** (centroid) since:
- Avoids redundancy with `entity.centroid.centroid`
- More stable (doesn't flip when energy shifts)
- Matches "identity as semantic signature" intuition

**Verdict:** ⚠️ NEEDS CLARIFICATION - identity center definition

6. **Complementarity** (lines 1796-1801):
   - Spec: `dot(node_j_affect, -affect_centroid)`
   - ⚠️ Skeleton lines 190-220: Uses `1 - |v_extent + v_j| / 2`

**ISSUE FOUND:** Complementarity formula completely different.

**Spec says:** Dot product with OPPOSITE of affect centroid (emotion embedding space)
**Skeleton says:** Balance measure using magnitude of sum

**Impact:** These are fundamentally different formulas.

**Resolution:** Spec formula is more precise:
```python
# Compute mean emotion vector across extent
affect_centroid = mean(node.emotion_vector for node in entity.extent)
# Target emotion
node_j_affect = graph.get_node(target_j).emotion_vector
# Complementarity = alignment with opposite
return np.dot(node_j_affect, -affect_centroid)
```

**Verdict:** ⚠️ NEEDS CORRECTION - complementarity formula

7. **Integration** (lines 1803-1810):
   - Spec: `E_others / (E_self + ε)` standardized as surprise
   - ⚠️ Skeleton lines 223-256: Uses overlap ratio with size indicator

**ISSUE FOUND:** Integration formula different.

**Spec says:** Ratio of other-entity energy at target node
**Skeleton says:** Overlap between extents with size gating

**Impact:** Different integration semantics.

**Resolution:** Need to check if both are correct for different purposes:
- Spec formula: "How strong is OTHER energy at this specific target node?"
- Skeleton formula: "How much do I already overlap with other entities?"

These measure different things. **Spec formula is correct per lines 1975-1988**:
> "When evaluating an edge, examine the target node's energy channels. Sum energy across all entities EXCEPT the currently-traversing entity. Call this E_others."

**Verdict:** ⚠️ NEEDS CORRECTION - integration formula

---

### Surprise Gates - VERIFIED ✅

**Spec Requirement (lines 1750-1768):**
> "Gate Construction (Per Hunger, Per Entity):
>
> 1. z_H = (s_H - μ_H) / (σ_H + ε)  # Standardize
> 2. δ_H = max(0, z_H)  # Positive surprise only
> 3. g_H = δ_H / (Σ δ_H' + ε)  # Normalize to gate weight"

**Skeleton Implementation:**
- ✅ `compute_surprise_gates()` (lines 295-322)
- ✅ Algorithm steps documented (lines 302-306)
- ✅ EMA baseline update (lines 366-391)

**Verdict:** ✅ VERIFIED (with TODOs)

---

### Composite Valence - VERIFIED ✅

**Spec Requirement (line 1821):**
> `V_ij = Σ_H (g_H × ν_H(i→j))`

**Skeleton Implementation:**
- ✅ `composite_valence()` (lines 324-361)
- ✅ Formula documented (line 335)

**Verdict:** ✅ VERIFIED (with TODO)

---

## CRITICAL FINDINGS SUMMARY

### 🔴 AI #4 (valence.py) - 4 Formula Corrections Needed

1. **Ease hunger** (line 133):
   - ❌ Current: `w_ij / max(w_ik)`
   - ✅ Correct: `w_ij / (Σ_k w_ik + ε)`

2. **Identity hunger** (line 169):
   - ❌ Current: "highest-energy node"
   - ⚠️ Needs clarification: Should be centroid or strongest node?
   - Recommend: Use `entity.centroid.centroid` (matches spec line 1786)

3. **Complementarity hunger** (line 199):
   - ❌ Current: `1 - |v_extent + v_j| / 2`
   - ✅ Correct: `np.dot(node_j_affect, -affect_centroid)`

4. **Integration hunger** (line 237):
   - ❌ Current: Overlap ratio with size indicator
   - ✅ Correct: `E_others / (E_self + ε)` at target node

---

## ✅ Remaining Skeletons (Quick Check)

### AI #3: scheduler.py
**Spec Lines:** 1721-1741 (Zippered Round-Robin)
- ✅ Function signatures match spec
- ✅ TODOs reference correct algorithms
- No formula discrepancies found

**Verdict:** ✅ VERIFIED (with TODOs)

---

### AI #5: strides.py
**Spec Lines:** 1826-1928

**CRITICAL:** Lines 337-356 in PARALLEL_DEVELOPMENT_PLAN highlight:
> "Edge Selection Must Rank by Valence, Not Weight"
>
> ❌ WRONG: Ranks by link weight proportion
> ✅ CORRECT: Ranks by composite valence

**Verification:** Need to check if skeleton ranks by V_ij (correct) or p_ij (wrong).

**Skeleton lines to check:**
- `select_edge_by_valence_coverage()` - should rank by valence
- `execute_stride()` - gap-aware transport
- `estimate_local_rho()` - power iteration
- `derive_rho_target()` - from throughput budgets

**Verdict:** ⚠️ NEEDS DETAILED REVIEW (critical bug already flagged)

---

### AI #6: wm_pack.py
**Spec Lines:** 2005-2013 (Working Memory Emission)

**Spec Requirement:**
> "At frame completion, each non-dissolved entity emits its current active extent as a working memory contribution. This is the set of nodes where the entity's energy channel exceeds activation threshold."

**Expected Functions:**
- `select_wm_nodes()` - energy-weighted knapsack
- `compute_wm_token_budget()` - from LLM capacity
- `construct_workspace_prompt()` - format for Tier 2

**Verdict:** ⚠️ NEEDS DETAILED REVIEW

---

### AI #7: telemetry.py
**Spec Lines:** Not explicitly specified (visualization support)

**Expected:**
- Event emission for viz
- WebSocket streaming
- Frame buffering

**Verdict:** ⚠️ NEEDS DETAILED REVIEW (lower priority)

---

## 🎯 Required Actions

### Immediate (Blocking AI #4):
1. **Fix valence.py hunger formulas** (4 corrections)
2. **Clarify identity hunger**: Centroid or strongest node?

### High Priority (Before AI #5 starts):
1. **Review strides.py** for valence ranking bug
2. **Verify gap-aware transport formula** matches spec

### Medium Priority (Before integration):
1. **Review wm_pack.py** token budget derivation
2. **Review telemetry.py** event structure

---

## ✅ Verification Complete

**Skeletons Verified:** 3/7
- ✅ AI #1: sub_entity_core.py
- ✅ AI #2: quotas.py
- ⚠️ AI #4: valence.py (needs 4 formula corrections)
- ⚠️ AI #5, #6, #7: Need detailed review

**Blockers Identified:**
- AI #4 cannot proceed until hunger formulas corrected
- AI #5 depends on AI #4, so also blocked

**Recommendation:**
1. Fix AI #4 hunger formulas immediately
2. Complete AI #5, #6, #7 detailed reviews
3. Then proceed with parallel implementation

---

*Verification conducted by Ada "Bridgekeeper" - 2025-10-20*
