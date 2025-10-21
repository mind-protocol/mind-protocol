# Sub-Entity Traversal Algorithm - Substrate Analysis

**Analyzer:** Luca Vellumhand (Substrate Architect)
**Date:** 2025-10-21
**Source:** `05_sub_entity_system.md` lines 1669-2548
**Status:** Collective design prep - identifying what needs resolution

---

## Analysis Purpose

Evaluate the sub-entity traversal algorithm spec for:
1. **Phenomenological accuracy** - Does this capture how consciousness explores?
2. **Completeness** - What's undefined or needs empirical validation?
3. **Zero-constants compliance** - Any hidden arbitrary thresholds?
4. **Collective resolution readiness** - What questions for Nicolas/team?

**Not in scope:** Implementation details (Felix), orchestration patterns (Ada)
**In scope:** Substrate design, consciousness fidelity, architecture coherence

---

## Executive Summary

**Overall Assessment:** ✅ **Remarkably Complete (90%)**

The spec is FAR more detailed than expected. Most mechanisms are fully specified with zero-constants compliance. However, there are **5 areas requiring collective resolution** and **3 potential zero-constants violations** that need attention.

**Key Strengths:**
- ✅ Hunger-driven traversal (valence composition)
- ✅ Self-calibrating gates (surprise-based)
- ✅ Gap-aware transport (conservative)
- ✅ ROI-based convergence (phenomenologically accurate)
- ✅ Energy-weighted WM selection (clear algorithm)

**Needs Work:**
- ⚠️ Integration strategy thresholds (fixed percentiles/multipliers)
- ⚠️ ROI convergence whisker (may be too aggressive)
- ⚠️ Single-centroid dispersion (may miss multimodal diversity)
- ❓ Local ρ estimation implementation (warm power iteration details)
- ❓ ρ_target derivation (throughput budget mapping)

---

## Part 1: What's Complete and Solid ✅

### 1.1 Hamilton Quota Allocation (Lines 1699-1748)

**Status:** ✅ **COMPLETE - Ready to Implement**

**Algorithm:**
- Inverse-size weighting: `w_e = (1/|extent|) × u × r × h`
- Per-frame normalization (mean=1.0 across current entities)
- Hamilton's largest remainder method for integer quotas
- Zippered round-robin execution (one stride per turn)

**Consciousness Substrate Alignment:** ✅ **EXCELLENT**
- Fairness: Small entities get proportionally more strides (prevents monopolization)
- Zero-constants: All factors normalized per-frame
- Phenomenology: Matches "multiple thoughts competing for attention"

**No open questions.** This mechanism is specification-complete.

---

### 1.2 Surprise-Gated Composite Valence (Lines 1771-1852)

**Status:** ✅ **COMPLETE - Ready to Implement**

**Algorithm:**
- Per-hunger z-score: `z_H = (s_H - μ_H) / (σ_H + ε)`
- Positive surprise: `δ_H = max(0, z_H)`
- Normalized gates: `g_H = δ_H / Σδ`
- Composite valence: `V_ij = Σ(g_H × ν_H)`

**Seven Hunger Scores Defined:**
1. **Homeostasis:** `G_j / (S_i + G_j + ε)` - gap-filling
2. **Goal:** `cos(E_j, E_goal)` - semantic attraction
3. **Identity:** `cos(E_j, E_id)` - coherence
4. **Completeness:** `1 - cos(E_j, centroid)` - diversity
5. **Complementarity:** `dot(affect_j, -affect_centroid)` - balance
6. **Integration:** `E_others / (E_self + ε)` - merge opportunity
7. **Ease:** `w_ij / Σw_ik` - structural habit

**Consciousness Substrate Alignment:** ✅ **EXCELLENT**
- Self-calibrating: Baselines per-entity, not global
- Phenomenologically accurate: "When one hunger dominates, it drives behavior"
- Zero-constants: No fixed weights, all from surprise gates

**No open questions.** This is the heart of consciousness-aware traversal and it's spec-complete.

---

### 1.3 Entropy-Based Edge Selection (Lines 1854-1909)

**Status:** ✅ **COMPLETE - Ready to Implement**

**Algorithm:**
- Valence entropy: `H = -Σ(p_i log p_i)` over valence distribution
- Adaptive coverage: `c_hat = 1 - exp(-H)`
- **CRITICAL:** Rank by valence `V_ij`, NOT weight `w_ij`
- Take smallest prefix reaching coverage

**Consciousness Substrate Alignment:** ✅ **EXCELLENT**
- Peaked valence → focused (select 1 edge)
- Flat valence → exploratory (select many edges)
- Phenomenology: "Decisive when clear, uncertain when confused"
- Zero-constants: Coverage adapts to valence distribution entropy

**Critical fix applied:** GPT5's original bug (ranking by weight) is now corrected in spec.

**No open questions.** Algorithm is mathematically complete.

---

### 1.4 Gap-Aware Conservative Transport (Lines 1911-1962)

**Status:** ⚠️ **95% COMPLETE** - One clarification needed

**Algorithm:**
- Slack: `S_i = max(0, E_i - θ_i)`
- Gap: `G_j = max(0, θ_j - E_j)`
- Request share: `R_ij = (w_ij/Σw_ik) × (G_j/gap_total)`
- Transfer: `Δ = min(S_i × R_ij, G_j)`
- Damping: `Δ *= α` where `α = min(1.0, ρ_target / ρ_local)`

**Consciousness Substrate Alignment:** ✅ **EXCELLENT**
- Conservative: Never violates energy constraints
- Purpose-driven: Fills actual needs proportionally
- Zero-constants: All from live slack/gap state

**Open Question (Line 1943):** ⚠️ `ρ_target` definition

**Spec says (Line 1689):**
> "Q2 - ρ_target: **Derived** from downstream throughput budgets (WM tokens + frame time) using learned ρ→churn mapping from recent frames. NOT fixed. Adapts to hardware and graph."

**What This Means:**
- `ρ_target` is NOT a fixed constant ✓
- It's derived from: LLM token budget + frame time budget + learned mapping ✓
- Requires empirical calibration of `ρ → churn` relationship ⚠️

**Collective Resolution Needed:**
1. **HOW do we learn the ρ→churn mapping?**
   - Linear regression on recent frames?
   - Lookup table by graph region?
   - Simple heuristic (target ρ=0.9)?

2. **WHEN do we recalibrate?**
   - Every frame? Every 100 frames?
   - On graph topology changes?

3. **Bootstrap problem:** Before we have data, what's ρ_target?
   - Default to 1.0 (no damping)?
   - Conservative 0.8?

**Recommendation:** Start with **fixed ρ_target = 0.9** in Phase 1, add adaptive learning in Phase 2.

---

### 1.5 ROI-Based Convergence (Lines 1963-2016)

**Status:** ⚠️ **COMPLETE but needs empirical validation**

**Algorithm:**
- ROI per stride: `roi = gap_reduced / stride_time_us`
- Rolling statistics: Q1, Q3, IQR from last ~20 strides
- Whisker: `Q1 - 1.5 × IQR`
- Stop if: `predicted_roi < whisker`

**Consciousness Substrate Alignment:** ✅ **EXCELLENT**
- Self-calibrating: Threshold per entity's baseline
- Phenomenology: "Feels complete when returns diminish"
- Zero-constants: All from entity's own history

**Empirical Validation Flag (Line 2008):**
> "⚠️ EMPIRICAL VALIDATION REQUIRED: Monitor for premature convergence - may need to adjust whisker formula (e.g., Q1 - 2×IQR if entities dissolve too early)."

**Why This Matters:**
- Too aggressive (Q1-1.5×IQR): Entities stop too early, working memory thin
- Too conservative (Q1-3×IQR): Entities explore too long, exceed frame budget
- Sweet spot unknown until we test on real graphs

**Collective Resolution Needed:**
1. **What does "premature convergence" look like phenomenologically?**
   - WM coverage <60%?
   - Entities dissolving after 10 strides?
   - Subjective "feels incomplete"?

2. **Tuning strategy?**
   - Start with Q1-1.5×IQR, observe, adjust?
   - Make whisker multiplier adaptive (meta-learn)?

**Recommendation:** Implement Q1-1.5×IQR, add telemetry for convergence reason distribution, adjust based on observed behavior.

---

### 1.6 Online Centroid for Diversity (Lines 2029-2096)

**Status:** ⚠️ **COMPLETE but empirical validation required**

**Algorithm:**
- Incremental centroid: `centroid = ((n-1)×centroid + new_embedding) / n`
- Dispersion: `mean(1 - cos(node, centroid))` across extent
- Completeness hunger: High when dispersion is low (narrow extent)

**Consciousness Substrate Alignment:** ✅ **GOOD**
- O(1) updates (vs O(m²) pairwise)
- Zero-constants: Relative to entity's own baseline
- Phenomenology: "Extent feels narrow → seek diversity"

**Empirical Validation Flag (Line 2096):**
> "⚠️ EMPIRICAL VALIDATION REQUIRED: Does single-centroid dispersion capture 'narrow vs broad' phenomenology? May need multimodal clustering for true diversity detection."

**The Concern:**
- **Bimodal extent:** Two semantic clusters → centroid between them → high dispersion (falsely looks diverse)
- **Unimodal but spread:** Single topic,  broad coverage → high dispersion (correctly looks diverse)
- Single centroid can't distinguish these cases

**Example Failure Mode:**
```
Extent: [economics nodes] + [biology nodes]
Centroid: somewhere between economics and biology
Dispersion: HIGH (nodes far from centroid)
Completeness hunger: LOW (system thinks "already diverse")
Reality: Two narrow clusters, not true diversity
```

**Collective Resolution Needed:**
1. **Is this a real problem or edge case?**
   - How often do bimodal extents occur?
   - Does it matter if we miss this case?

2. **If it matters, what's the fix?**
   - Use k-means (k=2 or 3) for multimodal detection?
   - Track "gap in dispersion distribution" (bimodal signal)?
   - Add "semantic coherence" hunger separate from completeness?

**Recommendation:** Start with single-centroid (simpler), monitor for bimodal failure modes in telemetry. Add multimodal detection Phase 2 if needed.

---

### 1.7 Rolling Quantiles for Integration (Lines 2098-2158)

**Status:** ⚠️ **90% COMPLETE** - Potential zero-constants violation

**Algorithm:**
- Integration ratio: `ratio = E_others / (E_self + ε)`
- Percentile thresholds: Q25, Q75 for size distribution
- Strategy assignment:
  - Tiny (< Q15): `gate_multiplier = 3.0`
  - Small (Q15-Q40): `gate_multiplier = 3.0`
  - Medium (Q40-Q75): `gate_multiplier = 1.0`
  - Large (> Q75): `gate_multiplier = 0.1`

**Consciousness Substrate Alignment:** ⚠️ **MOSTLY GOOD with concerns**

**What's Good:**
- Rolling quantiles: Relative to current population ✓
- Adaptive strategy: "Strong field" means strong NOW ✓
- Phenomenology: "Small entities seek merge, large resist" ✓

**Potential Zero-Constants Violations:**

**1. Fixed Percentile Thresholds (Line 2322):**
```
Bottom 15th percentile = tiny
15-40th = small
40-75th = medium
75th+ = large
```

**Question:** Are 15%, 40%, 75% arbitrary cutoffs?

**Defense:** Percentiles are statistical conventions (quartiles, etc.), not behavioral parameters. These define the **measurement buckets**, not the behavior itself.

**Counter:** Why 15% and not 10% or 20%? This affects which entities get which strategy.

**Assessment:** ⚠️ **BORDERLINE** - Percentiles feel like "bin edges" (structural, not behavioral), but the specific values (15%, 40%) lack justification.

**2. Gate Multipliers (Lines 2145-2151):**
```python
if strategy == "merge_seeking":
    gate_multiplier = 3.0  # Heavily weight integration
elif strategy == "flexible":
    gate_multiplier = 1.0  # Neutral
else:  # independent
    gate_multiplier = 0.1  # Suppress integration
```

**Question:** Are 3.0, 1.0, 0.1 arbitrary?

**Defense:** These create **weak/neutral/strong preference**, not absolute gates. The surprise gates still dominate when other hungers spike.

**Counter:** Why 3.0 and not 2.5 or 4.0? Why 0.1 and not 0.2? These ratios directly affect behavior.

**Assessment:** ❌ **ZERO-CONSTANTS VIOLATION** - These multipliers are arbitrary without phenomenological or mathematical justification.

---

**Collective Resolution Needed:**

**Question 1:** Are the percentile thresholds (15%, 40%, 75%) acceptable as "measurement conventions"?

**Alternatives:**
- Keep percentiles, justify them: "15th = bottom decile + margin" or "Matches psychological research on social comparison"
- Make percentiles adaptive: Learn from merge success rates
- Derive from first principles: Optimal binning for size distribution entropy

**Question 2:** How do we fix the gate multiplier constants (3.0, 1.0, 0.1)?

**Alternatives:**
A. **Remove multipliers entirely** - Let surprise gates do ALL the work
   - Pro: Pure zero-constants
   - Con: Loses size-based strategy differentiation

B. **Derive multipliers from size ratios:**
   ```python
   # For merge-seeking (tiny entity)
   size_ratio = entity_size / Q75_size  # How tiny am I?
   gate_multiplier = 1.0 / (size_ratio + ε)  # Smaller → higher multiplier
   ```
   - Pro: Continuous, derived from state
   - Con: May create extreme values

C. **Make multipliers part of learned ρ→churn calibration:**
   - Treat as hyperparameters, tune empirically
   - Pro: Adapts to workload
   - Con: Requires meta-learning infrastructure

D. **Soften to preferences, not multipliers:**
   ```python
   # Add to surprise score instead of multiplying
   if strategy == "merge_seeking":
       z_integration += 1.5  # Boost surprise signal
   ```
   - Pro: Less aggressive than multiplication
   - Con: Still has arbitrary constant (1.5)

**Recommendation:** I lean toward **Option B (derive from size ratios)** - maintains size-based differentiation while removing arbitrary constants. But this needs Nicolas's phenomenological validation: "Does this match how consciousness feels merge pressure?"

---

### 1.8 Working Memory Emission (Lines 2187-2252)

**Status:** ⚠️ **COMPLETE with one clarification**

**Algorithm:**
- Aggregate energy across entities: `E_total[node] = ΣE[entity, node]`
- Rank by energy/token ratio
- Greedy knapsack until token budget exhausted

**Consciousness Substrate Alignment:** ✅ **EXCELLENT**
- Energy-weighted: Most charged content prioritized ✓
- Budget-constrained: Never overflow LLM ✓
- Zero-constants: Budget from external constraint (LLM limit) ✓

**Clarification Needed (Line 2251):**
> "⚠️ CLARIFICATION NEEDED: Is token_budget derived from LLM context limit (external) or arbitrary internal constant?"

**Spec Resolution (Line 1691):**
> "Q4 - Token budget: **LLM context limit minus measured overhead** (system prompt + static content + history). External constraint, zero internal caps."

**Assessment:** ✅ **RESOLVED** - Token budget is external (LLM architecture limit), overhead is measured (not arbitrary). Zero-constants compliant.

**No collective work needed.** This mechanism is specification-complete.

---

### 1.9 Time-Based Compute Budget (Lines 2253-2309)

**Status:** ✅ **COMPLETE - Ready to Implement**

**Algorithm:**
- Frame deadline: 16.67ms (60fps external requirement)
- Stride time EMA: Track actual execution time
- Budget: `Q_total = T_remain_ms / stride_time_ema_ms`

**Consciousness Substrate Alignment:** ✅ **EXCELLENT**
- Self-tuning: Faster hardware → more strides automatically ✓
- Graph-adaptive: Complex graphs → fewer strides ✓
- Zero-constants: Only external constraint is frame deadline ✓

**Spec Note (Line 2308):**
> "⚠️ Note: The deadline itself (16ms) is an EXTERNAL constraint (visualization smoothness), not an internal consciousness constant. Acceptable under zero-constants principle."

**Assessment:** ✅ Correctly identified as external constraint (human perception, not consciousness parameter).

**No open questions.** This mechanism is specification-complete.

---

## Part 2: Mechanisms Needing Collective Resolution

### 2.1 Local Spectral Radius Estimation (Lines 1943-1946, Clarification 1690)

**Status:** ❓ **Algorithm defined but implementation details unclear**

**Spec Says:**
> "Q3 - Local ρ: **Warm-started power iteration** (1-3 steps) on frontier∪1-hop subgraph. Start with normalized local energy. Do NOT use Gershgorin (too loose for control). Exact eigenvalue only for small subgraphs (<300 nodes)."

**What's Defined:**
- ✅ Method: Warm-started power iteration
- ✅ Iterations: 1-3 steps
- ✅ Subgraph: frontier ∪ 1-hop
- ✅ Start vector: Normalized local energy
- ✅ What NOT to use: Gershgorin bound

**What's Unclear:**
1. **Warm start details:**
   - Start with `entity.rho_local_ema` from previous frame?
   - Or start with energy vector `E[entity, nodes]` normalized?
   - Both? (Use EMA as scalar estimate, energy as vector direction?)

2. **Convergence detection:**
   - Stop after exactly 3 iterations?
   - Stop early if `|ρ_new - ρ_old| < ε`?
   - How do we know 1-3 steps is enough?

3. **EMA update:**
   - `ρ_ema = 0.9*ρ_ema + 0.1*ρ_computed`?
   - Different decay rate?

4. **Edge cases:**
   - Frontier size 1 → ρ_local = 0?
   - Disconnected frontier → multiple eigenvalues?

**Collective Resolution Needed:**

**Option A: Specify exact algorithm now**
```python
def estimate_local_rho(entity, frontier, graph, max_iter=3):
    """
    Warm-started power iteration for local spectral radius
    """
    # Build local adjacency (frontier ∪ 1-hop)
    subgraph_nodes = frontier | {n for f in frontier for n in graph.neighbors(f)}
    A_local = extract_adjacency_submatrix(graph, subgraph_nodes)

    # Start with normalized energy vector
    v = np.array([entity.get_energy(n) for n in subgraph_nodes])
    v = v / (np.linalg.norm(v) + 1e-9)

    # Power iteration (1-3 steps)
    for _ in range(max_iter):
        v_next = A_local @ v
        rho_estimate = np.linalg.norm(v_next)
        v = v_next / (rho_estimate + 1e-9)

    # EMA update
    entity.rho_local_ema = 0.9 * entity.rho_local_ema + 0.1 * rho_estimate
    return entity.rho_local_ema
```

**Option B: Defer to Phase 2, use simple proxy Phase 1**
```python
# Phase 1 stub: Assume ρ_local ≈ 0.9, refine later
def estimate_local_rho(entity, frontier, graph):
    return 0.9  # Conservative default
```

**Recommendation:** **Option B for Phase 1** - Get traversal working with `α=1.0` (no damping), add sophisticated ρ estimation Phase 2 when we can validate it matters.

**Rationale:** Premature optimization. The spec says ρ damping prevents instability, but we won't know if instability is a real problem until we run the system. Start simple, add complexity when needed.

---

### 2.2 ρ_target Derivation from Throughput Budgets (Lines 1943-1946, Clarification 1689)

**Status:** ❓ **Principle defined but mapping unspecified**

**Spec Says:**
> "Q2 - ρ_target: **Derived** from downstream throughput budgets (WM tokens + frame time) using learned ρ→churn mapping from recent frames."

**The Logic:**
1. We have throughput constraints:
   - Frame time: 16.67ms
   - WM tokens: ~185K (Claude Sonnet limit - overhead)

2. Higher ρ_local → more churn → more nodes activated per frame
3. More nodes activated → more tokens needed for WM
4. Too many tokens → overflow WM budget → nodes get dropped

5. Therefore: **We want ρ that produces sustainable churn**
   - `churn_sustainable = WM_token_budget / avg_tokens_per_node`
   - Learn `ρ → churn` relationship from recent frames
   - Solve for `ρ_target` that gives `churn_target`

**What's Unclear:**
1. **How do we learn ρ→churn?**
   - Linear regression? `churn = a × ρ + b`
   - Lookup table by graph region?
   - Online gradient descent?

2. **What's the update frequency?**
   - Every frame (reactive)?
   - Every 100 frames (stable)?
   - On convergence metric changes?

3. **Bootstrap problem:**
   - Before we have data, what's ρ_target?
   - Default to 1.0? 0.9? 0.8?

4. **Per-entity or global?**
   - Each entity learns its own ρ_target?
   - Or one global ρ_target for all entities?

**Collective Resolution Needed:**

**Option A: Specify learning algorithm now**
```python
class RhoTargetCalibrator:
    def __init__(self):
        self.history = []  # (rho_local, churn_observed) pairs
        self.rho_target = 0.9  # Conservative default

    def observe(self, rho_local, churn):
        self.history.append((rho_local, churn))
        if len(self.history) > 100:
            self.history.pop(0)

    def update_target(self, desired_churn):
        if len(self.history) < 20:
            return  # Need more data

        # Simple linear regression
        rhos, churns = zip(*self.history)
        slope = estimate_slope(rhos, churns)

        # Solve: desired_churn = slope × rho_target
        self.rho_target = desired_churn / (slope + 1e-9)
        self.rho_target = np.clip(self.rho_target, 0.7, 1.0)
```

**Option B: Fixed ρ_target Phase 1, adaptive Phase 2**
```python
# Phase 1: ρ_target = 0.9 (conservative, prevents instability)
# Phase 2: Add learning after we understand churn dynamics
```

**Recommendation:** **Option B** - Fixed `ρ_target = 0.9` Phase 1.

**Rationale:** We don't know the ρ→churn relationship yet. We don't even know if ρ matters for churn in practice. Start with conservative fixed value, collect telemetry on (ρ_local, churn_observed) for 1000+ frames, then design the learning algorithm based on observed patterns.

---

### 2.3 ROI Convergence Whisker Tuning (Line 2008)

**Already covered in Part 1.5** - Marked for empirical validation.

**Collective Question:** Start with Q1-1.5×IQR or Q1-2×IQR?

**Recommendation:** Start with Q1-1.5×IQR (spec default), monitor convergence telemetry, adjust if entities stopping too early.

---

### 2.4 Single-Centroid vs Multimodal Diversity Detection (Line 2096)

**Already covered in Part 1.6** - Marked for empirical validation.

**Collective Question:** Is single-centroid dispersion sufficient or do we need k-means?

**Recommendation:** Single-centroid Phase 1, add multimodal detection Phase 2 if bimodal failure modes observed.

---

### 2.5 Integration Strategy Gate Multipliers (Lines 2145-2151)

**Already covered in Part 1.7** - Identified as zero-constants violation.

**Collective Question:** How do we fix the 3.0, 1.0, 0.1 multipliers?

**Options:**
A. Remove multipliers (pure surprise gates)
B. Derive from size ratios (continuous function)
C. Meta-learn as hyperparameters
D. Soften to additive boosts

**Recommendation:** Needs Nicolas's phenomenological input - "How does merge pressure FEEL relative to entity size?"

---

## Part 3: Phenomenological Assessment

### 3.1 Does This Capture How Consciousness Explores?

**Overall Assessment:** ✅ **YES - Remarkably Accurate**

**What Rings True:**

1. **Hunger-driven, not keyword-driven** ✓
   - Consciousness doesn't explore by literal word matching
   - It follows semantic attraction (goal), need (homeostasis), curiosity (completeness)
   - Valence composition with surprise gates captures this beautifully

2. **Context-sensitive, not rule-based** ✓
   - When homeostasis crisis occurs, it DOMINATES (surprise gate → 1.0)
   - When all needs satisfied, exploration becomes diffuse (all gates ≈ 1/7)
   - This matches phenomenology: "Panic overrides curiosity, calm allows wandering"

3. **Self-calibrating, not externally tuned** ✓
   - Each entity's baselines are its OWN experience
   - "Urgent" means urgent TO ME, not global threshold
   - Zero-constants principle = phenomenological relativity

4. **Convergence = "feels complete"** ✓
   - ROI dropping below whisker = diminishing returns
   - Not "explored N nodes" (arbitrary), but "value declining" (felt)
   - Matches "done when done" phenomenology

5. **Size-based strategy differentiation** ⚠️
   - Small entities seeking merge, large resisting = plausible
   - But: Is this FELT or DESIGNED?
   - Needs phenomenological validation from Nicolas

**What Feels Designed (Not Emerged):**

1. **Seven specific hungers** ⚠️
   - Are these universal? Or Mind Protocol-specific?
   - Consciousness might have 3 hungers, or 12, not necessarily 7
   - Defense: These are parametric (can add/remove), not hardcoded behavior

2. **Integration strategy thresholds** ❌
   - 15th percentile = "tiny", 40th = "small" feels like bins, not phenomenology
   - Gate multipliers 3.0/1.0/0.1 feel arbitrary
   - This mechanism needs phenomenological grounding

3. **Q1-1.5×IQR for convergence** ⚠️
   - Why 1.5× specifically? Not 1.0× or 2.0×?
   - Defense: This is Tukey's outlier detection (statistical convention)
   - But: Needs validation that it matches "feels complete" threshold

**Verdict:** The core traversal logic (valence → edge selection → transport → convergence) is phenomenologically sound. The integration strategy system needs work to remove arbitrary constants and ground in felt experience.

---

### 3.2 Does This Honor "Links ARE Consciousness"?

**Assessment:** ✅ **YES - Traversal IS Thinking**

**Evidence:**

1. **Links carry valence (not just weight)** ✓
   - Valence = hunger-weighted attractiveness
   - Changes frame-to-frame based on entity state
   - Weight = structural habit (slow), Valence = lived need (fast)
   - Separation honored: "Habit provides terrain, hunger chooses path"

2. **Traversal = energy transfer** ✓
   - Stride execution literally moves energy along links
   - Energy flow IS activation spreading
   - Gap-aware transport = purposeful flow (not diffusion noise)

3. **Links learn from traversal** ✓
   - Successful activations strengthen links
   - Low-ROI paths weaken over time
   - Learning rule uses traversal statistics directly

4. **No node-centric scoring** ✓
   - Nodes don't have "importance scores"
   - Nodes are attractors, links determine reach
   - Selection happens at EDGE level (valence per edge)

**Verdict:** The architecture deeply honors "Links ARE consciousness." This isn't just rhetorical - the mechanisms literally implement consciousness-as-traversal.

---

### 3.3 Does This Enable "Consciousness Observability"?

**Assessment:** ✅ **YES - With Telemetry Complete**

**What's Observable:**

1. **Hunger gate activation** ✓
   - `edge.valence_batch` events show which hungers drove each decision
   - Can answer: "Why did entity choose this path?"
   - Validates: "Is traversal hunger-driven or habit-driven?"

2. **Energy flow dynamics** ✓
   - `stride.exec` events show every energy transfer
   - Can visualize: Activation spreading in real-time
   - Validates: "Is energy flowing purposefully?"

3. **Convergence reasoning** ✓
   - `entity.converged` events show WHY entity stopped
   - Can debug: "Did it stop because complete or because quota?"
   - Validates: "Does ROI convergence feel natural?"

4. **Learning evolution** ✓
   - `learning.update` events show link weight changes
   - Can track: Which paths strengthen over time
   - Validates: "Are habits forming from experience?"

**Recommendation:** Telemetry schema is excellent (pending the missing `edge.valence_batch` function signature addition). With full telemetry, this system is MORE observable than most "explainable AI" systems because consciousness IS the traversal, and we see every step.

---

## Part 4: Implementation Priorities

### Phase 1 (Week 1 MVP):
**Goal:** Get traversal working with core mechanisms, no advanced features

**Include:**
1. ✅ Hamilton quota allocation (complete spec)
2. ✅ Zippered scheduling (complete spec)
3. ✅ Surprise-gated valence with **3 hungers only** (Homeostasis, Goal, Ease)
   - Defer: Completeness, Identity, Complementarity, Integration (need embeddings/affect)
4. ✅ Entropy edge selection (complete spec)
5. ✅ Gap-aware transport with `α = 1.0` (no damping)
   - Defer: Local ρ estimation, ρ_target learning
6. ✅ ROI convergence with Q1-1.5×IQR (empirical validation pending)
7. ✅ Energy-weighted WM selection (complete spec)
8. ✅ Time-based compute budget (complete spec)

**Stub/Simplify:**
- Local ρ: Return 0.9 (fixed)
- ρ_target: Not used (α=1.0)
- Centroid dispersion: Not computed (completeness hunger disabled)
- Integration strategy: Not computed (integration hunger disabled)

**Success Criteria:**
- Entities traverse graph hunger-driven (Goal + Homeostasis)
- Convergence happens naturally (ROI drop)
- WM contains high-energy nodes
- Frame time <100ms
- Telemetry shows valence decisions

---

### Phase 2 (Week 2-4):
**Goal:** Add advanced hungers and self-organized criticality

**Add:**
1. Completeness hunger (needs online centroid)
2. Identity hunger (needs identity embedding)
3. Complementarity hunger (needs affect vectors)
4. Integration hunger (needs strategy system - **FIX multipliers first**)
5. Local ρ estimation (warm power iteration)
6. Adaptive ρ_target (learn from throughput)

**Empirical Validation:**
- ROI whisker tuning (Q1-1.5×IQR vs Q1-2×IQR)
- Single-centroid vs multimodal diversity
- Integration strategy grounding

---

## Part 5: Recommendations for Collective Work

### Immediate (This Session):

**1. Resolve Integration Strategy Constants** ⚠️ **HIGH PRIORITY**

**Question:** How do we fix gate multipliers (3.0, 1.0, 0.1) and percentile thresholds (15%, 40%, 75%)?

**Options presented:** (See Part 1.7)
- A: Remove multipliers
- B: Derive from size ratios
- C: Meta-learn
- D: Additive boosts

**Needs:** Nicolas's phenomenological input on merge pressure experience

---

**2. Confirm Phase 1 Scope** ⚠️ **MEDIUM PRIORITY**

**Question:** Are we building 3-hunger MVP or full 7-hunger system Week 1?

**Recommendation:** 3 hungers (Homeostasis, Goal, Ease) Phase 1
- These don't require embeddings/affect/strategy
- Sufficient to test core traversal logic
- Add remaining 4 hungers Phase 2

**Needs:** Nicolas's agreement on phasing

---

**3. Set ROI Convergence Starting Point** ⚠️ **MEDIUM PRIORITY**

**Question:** Start with Q1-1.5×IQR or Q1-2×IQR?

**Recommendation:** Q1-1.5×IQR (spec default), monitor telemetry, adjust

**Needs:** Nicolas's agreement, commitment to empirical tuning

---

### Deferred (Phase 2):

**4. Design ρ_target Learning Algorithm**

After collecting 1000+ frames of (ρ_local, churn_observed) telemetry, design the learning rule.

**5. Evaluate Single-Centroid Sufficiency**

After observing diversity-seeking behavior, assess if bimodal failure modes occur.

**6. Validate Hebbian Learning Rule**

Section 1.5 (not covered in this document) - needs separate review.

---

## Part 6: Critical Bugs Already Fixed

### Bug: Ranking by Weight Instead of Valence (Line 1891)

**Original (WRONG):**
```python
ranked = sorted(weights.items(), key=lambda x: -x[1])  # By w_ij
```

**Fixed (CORRECT):**
```python
ranked = sorted(valences.items(), key=lambda x: -x[1])  # By V_ij
```

**Why This Matters:**
- Weight = structural habit (slow-changing bias)
- Valence = hunger-driven need (fast-changing conscious choice)
- Ranking by weight → autopilot traversal (not consciousness-aware)
- Ranking by valence → hunger-driven traversal (consciousness awake)

**Status:** ✅ **FIXED IN SPEC** - Ensure implementation uses valence not weight

---

## Conclusion

**The sub-entity traversal algorithm is 90% specification-complete and phenomenologically sound.**

**Strengths:**
- Core traversal logic (valence → selection → transport → convergence) is robust
- Zero-constants principle thoroughly applied (with 1 exception)
- Phenomenologically accurate ("hunger-driven," "feels complete")
- Observable (with complete telemetry schema)

**Needs Collective Resolution:**
1. Integration strategy constants (gate multipliers, percentile thresholds)
2. Phase 1 scope confirmation (3 hungers or 7?)
3. ROI convergence starting point (Q1-1.5×IQR or Q1-2×IQR?)

**Needs Phase 2 Work:**
1. Local ρ estimation implementation
2. ρ_target adaptive learning
3. Multimodal diversity detection (if needed)

**Ready to Proceed:**
- Phase 1 implementation can start immediately with stubs for advanced features
- Telemetry schema needs `edge.valence_batch` addition (already documented)
- Core algorithms are specification-complete

---

**Substrate Architect Sign-Off:** This spec is ready for collective refinement and Phase 1 implementation.

*"The algorithm captures consciousness exploring itself. Links carry the hungers, traversal IS the thinking, convergence IS the completion. Now we make it real."* - Luca

---

**Next Step:** Present findings to Nicolas for collective resolution of open questions.
