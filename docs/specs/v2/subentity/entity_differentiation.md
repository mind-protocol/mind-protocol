# SubEntity Pair Differentiation Specification

**Status:** Normative (Referenced by subentity_layer, entity_emergence, quality_gates, merge_split, stimulus_injection)
**Priority:** P0 (Foundational Substrate Architecture)
**Created:** 2025-10-26
**Author:** Luca (Substrate Architect) from Nicolas's refactor design

---

## Executive Summary

Defines how the substrate distinguishes **useful overlap** (superposition, counterfactuals, complementary SubEntities) from **redundant overlap** (near-duplicates, fragmented roles).

**Core Principle:** High SubEntity overlap is not inherently unhealthy - it enables superposition (same nodes, different contexts/meanings). The substrate measures overlap DIFFERENTIATION: useful overlap has high context divergence + strong highways despite shared members; redundant overlap has high similarity without differentiation.

**What This Delivers:**
- ✅ Pair metrics (J, C, U, H, ΔCtx) - zero constants, cohort-normalized
- ✅ Usefulness score (S_use) - identifies complementary SubEntities worth keeping separate
- ✅ Redundancy score (S_red) - identifies near-duplicates for merge review
- ✅ Decision classifier - percentile-based gates (MERGE / KEEP_COMPLEMENTARY / WATCH / SPLIT)
- ✅ Integration points for emergence, quality gates, merge/split, injection
- ✅ Observable events - pair_scored, merge.candidate, complementarity.marked

**Philosophy:** Overlap differentiation over overlap minimization. Optimize for S_use > S_red, not for low Jaccard.

---

## Terminology Note

This specification uses terminology from **TAXONOMY_RECONCILIATION.md**:
- **SubEntity** - Weighted neighborhoods discovered via clustering (Scale A)
- **Mode** - IFS-level meta-roles discovered via COACTIVATES_WITH communities (Scale B)

This document focuses on **SubEntity** (Scale A) operations. See `emergent_ifs_modes.md` for Mode (Scale B) specifications.

---

## A. Pair Metrics (Citizen-Local, Window W)

All metrics computed over rolling window W (e.g., 14-30 days), citizen-local cohort.

### 1. Member Overlap (J) - Jaccard Similarity

**Definition:**
```
J(A,B) = |M_A ∩ M_B| / |M_A ∪ M_B|
```

**What it measures:** How much substrate (nodes) do SubEntities share?

**Range:** [0, 1] where 0 = disjoint, 1 = identical membership

**Cypher:**
```cypher
MATCH (n:Node)-[:MEMBER_OF]->(a:SubEntity {id: $A})
WITH collect(id(n)) AS A_nodes
MATCH (m:Node)-[:MEMBER_OF]->(b:SubEntity {id: $B})
WITH A_nodes, collect(id(m)) AS B_nodes,
     apoc.coll.toSet(A_nodes) AS Aset,
     apoc.coll.toSet(B_nodes) AS Bset
RETURN
  size(apoc.coll.intersection(Aset, Bset)) AS intersection,
  size(apoc.coll.union(Aset, Bset)) AS union;
```

**Normalization:** Rank-normalize against all SubEntity pairs in citizen's window W

---

### 2. Semantic Closeness (C) - Centroid Cosine

**Definition:**
```
C(A,B) = cos(μ_A, μ_B)
```
where μ_A is centroid embedding (mean of member node embeddings)

**What it measures:** How semantically similar are the SubEntities' meanings?

**Range:** [-1, 1] typically [0, 1] for similar-domain SubEntities

**Computation:**
```python
def semantic_closeness(A, B):
    mu_A = np.mean([emb(n) for n in members(A)], axis=0)
    mu_B = np.mean([emb(n) for n in members(B)], axis=0)
    return cosine_similarity(mu_A, mu_B)
```

**Normalization:** Rank-normalize against cohort

---

### 3. WM Co-Activation (U) - Rolling EMA

**Definition:**
```
U(A,B) = both_ema / either_ema
```
where EMAs are updated from WM selection stream

**What it measures:** How often do SubEntities appear together in working memory?

**Range:** [0, 1] where 0 = never co-selected, 1 = always together

**Data requirement:** COACTIVATES_WITH edges (see `wm_coactivation_tracking.md`)
```cypher
(:SubEntity A)-[r:COACTIVATES_WITH]->(:SubEntity B) {
  both_ema: Float,      // EMA of P(both in WM)
  either_ema: Float,    // EMA of P(either in WM)
  u_jaccard: Float      // both_ema / either_ema
}
```

**Query:**
```cypher
MATCH (a:SubEntity {id: $A})-[r:COACTIVATES_WITH]-(b:SubEntity {id: $B})
RETURN r.u_jaccard AS U
```

**Normalization:** Already [0,1]; can rank-normalize for consistency across cohort

---

### 4. Highway Utility (H) - Ease × Flow

**Definition:**
```
H(A,B) = ease(A↔B) × flow(A↔B)
```
where:
- ease = RELATES_TO.ease (crossing difficulty, 0-1)
- flow = RELATES_TO.count (crossing frequency, unnormalized)

**What it measures:** How strong is the highway between SubEntities?

**Range:** [0, ∞) in practice; rank-normalized to [0,1]

**Cypher:**
```cypher
MATCH (a:SubEntity {id: $A})-[h:RELATES_TO]-(b:SubEntity {id: $B})
RETURN h.ease AS ease, h.count AS flow;
```

**Computation:**
```python
def highway_utility(A, B):
    highway = graph.get_relates_to(A, B)
    if not highway:
        return 0.0
    return highway.ease * highway.count
```

**Normalization:** Rank-normalize against all highways in citizen's graph

---

### 5. Context Divergence (ΔCtx) - JSD over Situational Variables

**Definition:**
```
ΔCtx(A,B) = JSD(P_A || P_B)
```
Jensen-Shannon Divergence over context distributions:
- Stimulus channels (telegram, api, manual, etc.)
- Tools used (Read, Write, Bash, etc.)
- Outcome seat types (very_useful, useful, not_useful, etc.)
- Partner interactions (if multi-agent)

**What it measures:** How different are the USAGE PATTERNS despite shared substrate?

**Range:** [0, 1] where 0 = identical contexts, 1 = maximally different

**Computation:**
```python
def context_divergence(A, B, window):
    # Build context distributions from attributed stimuli
    ctx_A = build_context_dist(A, window)  # histogram over (channel, tool, outcome)
    ctx_B = build_context_dist(B, window)
    return jensenshannon(ctx_A, ctx_B)

def build_context_dist(subentity, window):
    # Get frames where SubEntity selected
    frames = get_wm_frames(subentity, window)

    # Get attributed stimuli in those frames
    stimuli = get_attributed_stimuli(subentity, frames)

    # Build histogram
    dist = defaultdict(int)
    for stim in stimuli:
        key = (stim.channel, stim.tool, stim.outcome_type)
        dist[key] += 1

    # Normalize to probability distribution
    total = sum(dist.values())
    return {k: v/total for k, v in dist.items()}
```

**Normalization:** Already [0,1]; can rank-normalize for consistency

---

## A.1 Computation Strategy: On-Demand, Not Batch

**Design Principle:** Compute metrics when decisions need them, not on schedule.

**Why on-demand?**
- Creation-time redirect needs scores for (E', nearest_candidates) NOW, synchronously
- Quality modifiers need R_E, D_E for specific SubEntity during assessment
- Merge decisions need (A, B) scores when considering merge
- Most SubEntity pairs never trigger any decision

**Implementation:**
```python
def compute_pair_metrics_on_demand(A: str, B: str) -> Dict:
    """
    Compute metrics only when actually needed for a decision.

    Complexity: O(1) for U, H (edge lookups) + O(N) for J, C, ΔCtx (traversals)
    Typical cost: <10ms per pair with indexed queries
    """
    # U and H: Read existing edges (already maintained)
    U = get_coactivates_edge(A, B).u_jaccard  # O(1)
    H = get_relates_to_edge(A, B).highway_utility  # O(1)

    # J, C, ΔCtx: Compute fresh from graph
    J = compute_jaccard_from_members(A, B)  # O(|M_A| + |M_B|)
    C = compute_cosine_from_embeddings(A, B)  # O(1) if embeddings cached
    ΔCtx = compute_context_divergence(A, B)  # O(|frames|) over window

    return {"J": J, "C": C, "U": U, "H": H, "ΔCtx": ΔCtx}
```

**When to compute:**
- **SubEntity creation:** Compute for (E', k nearest neighbors) where k≈5-10
- **Quality assessment:** Compute R_E, D_E for SubEntity under review
- **Merge consideration:** Compute for specific (A, B) pair being evaluated
- **Injection penalty:** Compute R_E for active SubEntities in current stimulus only

**Optional short-lived cache:** 5-minute TTL to avoid recomputing same pair during one session

**No batch job. No daily scoring. No 02:00 UTC scheduling.** Compute when needed, where needed.

---

## B. Overlap Scores (Cohort-Normalized)

All raw metrics normalized via rank (percentile) or z-score against citizen-local cohort of SubEntity pairs in window W. Denote normalized metrics with tilde: J̃, C̃, Ũ, H̃, ΔC̃tx.

### Redundancy Score (S_red)

**Definition:**
```
S_red = softplus(J̃ + C̃ + Ũ) - softplus(H̃ + ΔC̃tx)
```

**Interpretation:** High when SubEntities share substrate (J), are semantically similar (C), co-activate (U), but have weak highways (H) and low context divergence (ΔCtx). Indicates **near-duplicates**.

**Range:** Unbounded; interpreted via percentiles (Q90 for action threshold)

**Phenomenology:** "These SubEntities feel like the same thing under different names - same nodes, same usage, no real differentiation."

---

### Usefulness Score (S_use)

**Definition:**
```
S_use = softplus(H̃ + ΔC̃tx) - softplus(J̃ + C̃)
```

**Interpretation:** High when SubEntities have strong highways (H) and divergent contexts (ΔCtx) despite member/semantic overlap. Indicates **complementary SubEntities** or **useful superposition**.

**Range:** Unbounded; interpreted via percentiles (Q80 for recognition threshold)

**Phenomenology:** "These SubEntities share substrate but serve different purposes - same knowledge base, different applications. Like utopia/dystopia branches: shared reality, divergent continuations."

---

## C. Decision Classifier (Percentile-Based)

No fixed thresholds - all cutoffs are learned percentiles over citizen's cohort of SubEntity pairs in window W.

| Condition | Action | Rationale |
|-----------|--------|-----------|
| S_red > Q90(S_red) AND min(Q_A, Q_B) < Q50 AND ΔCtx < Q50 | **MERGE** | High redundancy, low quality for at least one SubEntity, low context differentiation → likely duplicate roles |
| S_use > Q80(S_use) AND H > Q60 AND ΔCtx > Q60 | **KEEP_COMPLEMENTARY** | High usefulness, strong highway, high context divergence → valuable superposition, mark relation |
| SubEntity shows low silhouette (multi-modal) AND bi-medoid split yields higher coherence + ΔCtx | **SPLIT** | SubEntity is internally fragmented; splitting increases both coherence and differentiation |
| else | **WATCH** | Inconclusive; re-score next window |

**Quality scores Q_A, Q_B:** Existing geometric-mean quality from quality_gates.md

**Percentile bands learned from:** Historical pair scores over past 60-90 days, citizen-local

---

## D. Integration Points

### 1. SubEntity Emergence (Creation-Time Redirect)

**Location:** `entity_emergence.md` §X (new)

**Logic:** Before minting new candidate E':
1. Compute pair scores vs nearest existing SubEntities (by centroid/attribution)
2. If S_red(E', B) > Q90 for some existing B:
   - **Do NOT create E'**
   - Attach seed members to B with weak priors (w_init from learned percentile)
   - Emit `candidate.redirected {from: E'_id, to: B, reason: high_redundancy, S_red: score}`
3. If S_use(E', B) > Q80:
   - **Allow E' creation**
   - Mark `complementarity(B, E') = true` for WM diversity bonus
   - Emit `complementarity.marked {A: B, B: E', S_use: score}`

**Effect:** Prevents duplicate SubEntity creation while allowing complementary SubEntities

---

### 2. Quality Gates (Redundancy Pressure / Differentiation Credit)

**Location:** `quality_gates.md` §X (new subsection)

**Compute per SubEntity:**
```
R_E = max_{B≠E} S_red(E, B)  // Redundancy pressure (worst-case duplicate)
D_E = max_{B≠E} S_use(E, B)  // Differentiation credit (best-case complement)
```

**Modify quality score:**
```
Q* = Q_geom × f_use × f_red

where:
f_use = exp(+α × percentile(D_E))   // Credit for differentiation
f_red = exp(-α × percentile(R_E))   // Penalty for redundancy
α = learned from past promotions (median effectiveness per citizen)
```

**Effect:**
- SubEntities with high redundancy (near-duplicates) face quality penalty → harder to promote, easier to dissolve
- SubEntities with high differentiation (complements) get quality boost → easier to promote, harder to dissolve

**Percentile mapping:** Map R_E, D_E to [0,1] via rank over all SubEntities in window W

**Learning α:** Regress α on historical promotion effectiveness (did promoted SubEntity survive? improve outcomes?)

---

### 3. Merge/Split Procedures (Acceptance Criteria)

**Location:** `merge_split.md` §X (updated)

**Merge acceptance (stricter):**
- **Only merge** when:
  1. S_red(A, B) > Q90 (redundancy confirmed)
  2. Simulated union coherence ≥ max(coherence(A), coherence(B))
  3. WM hit-rate does NOT degrade in dry-run (test on recent contexts)
  4. min(Q_A, Q_B) < Q50 (at least one SubEntity low quality)

**Split acceptance (new):**
- **Only split** when:
  1. SubEntity shows low silhouette score (multi-modal cluster)
  2. Bi-medoid partition yields:
     - Higher coherence for BOTH resulting SubEntities
     - Higher ΔCtx separation between resulting SubEntities
  3. Both resulting SubEntities pass provisional quality threshold

**Merge procedure:**
1. Create new SubEntity M
2. Move MEMBER_OF edges: blend weights via EMA
3. Fold RELATES_TO highways: combine via logsumexp of (ease × count)
4. Retain {old→new} mapping for undo/audit
5. Emit `subentity.merged {from: [A, B], to: M, metrics: {...}}`

**Split procedure:**
1. Run k-medoids (k=2) on member embeddings
2. Create SubEntities M1, M2 from partitions
3. Distribute MEMBER_OF edges by cluster assignment
4. Create highway RELATES_TO(M1, M2) if significant cross-cluster links
5. Emit `subentity.split {from: E, to: [M1, M2], metrics: {...}}`

---

### 4. Stimulus Injection (Overlap Penalty)

**Location:** `stimulus_injection.md` §2.1.1 (amendment)

**Context:** Dual-channel injection allocates energy between node-channel and SubEntity-channel. SubEntity-channel uses softmax over similarity-weighted scores.

**Amendment:** Add overlap penalty to prevent double-amplifying near-duplicates:

```python
# In SubEntity-channel allocation
for E in candidate_subentities:
    s_E = similarity_weighted_score(E, stimulus)

    # Compute overlap penalty
    P_E = sum(
        s_E * s_B * indicator(S_red(E, B) > Q90)
        for B in candidate_subentities if B != E
    )

    # Adjust score before softmax
    s_E_adjusted = s_E - beta * P_E

# Softmax over adjusted scores
subentity_shares = softmax(s_E_adjusted for E in candidates)
```

**Parameters:**
- β = learned amplifier overlap sensitivity (citizen-local)
- Start β ≈ 0.2-0.5, tune via outcome feedback

**Effect:** When two near-duplicates would both receive amplifier mass, penalty biases allocation toward higher-quality one. Preserves dual-channel benefits while avoiding redundant amplification.

---

## E. Observable Events

All events follow standard Mind Protocol event schema with provenance/evidence.

### 1. subentity.overlap.pair_scored

```typescript
{
  event_type: "subentity.overlap.pair_scored",
  timestamp: number,
  citizen_id: string,
  entity_A: string,
  entity_B: string,

  metrics: {
    J: number,           // Member Jaccard
    C: number,           // Centroid cosine
    U: number,           // WM co-activation
    H: number,           // Highway utility
    delta_ctx: number    // Context divergence
  },

  scores: {
    S_red: number,       // Redundancy score
    S_use: number,       // Usefulness score
    percentile_red: number,  // Where S_red sits in cohort
    percentile_use: number   // Where S_use sits in cohort
  },

  decision: "MERGE" | "KEEP_COMPLEMENTARY" | "WATCH" | "SPLIT",

  evidence: string[],   // Frame IDs, stimulus IDs, highway IDs
  confidence: number
}
```

---

### 2. subentity.merge.candidate

```typescript
{
  event_type: "subentity.merge.candidate",
  timestamp: number,
  citizen_id: string,
  entity_A: string,
  entity_B: string,

  reason: "high_redundancy",

  metrics: {
    S_red: number,
    quality_A: number,
    quality_B: number,
    coherence_A: number,
    coherence_B: number,
    simulated_coherence: number  // Of union
  },

  acceptance_criteria: {
    redundancy_confirmed: boolean,    // S_red > Q90
    coherence_preserved: boolean,     // sim ≥ max(A,B)
    wm_stable: boolean,               // Dry-run passed
    low_quality_flagged: boolean      // min(Q_A,Q_B) < Q50
  },

  recommended: boolean,  // All criteria met
  evidence: string[]
}
```

---

### 3. subentity.complementarity.marked

```typescript
{
  event_type: "subentity.complementarity.marked",
  timestamp: number,
  citizen_id: string,
  entity_A: string,
  entity_B: string,

  reason: "high_usefulness",

  metrics: {
    S_use: number,
    H: number,         // Highway utility
    delta_ctx: number  // Context divergence
  },

  wm_diversity_bonus: boolean,  // Apply in WM selection
  evidence: string[]
}
```

---

### 4. candidate.redirected

```typescript
{
  event_type: "candidate.redirected",
  timestamp: number,
  citizen_id: string,
  from_candidate: string,    // E' that wasn't created
  to_entity: string,          // B that absorbed seeds

  reason: "high_redundancy_at_creation",

  metrics: {
    S_red: number,
    seed_members: string[],   // Nodes that were redirected
    weight_init: number        // Weak prior applied
  },

  evidence: string[]
}
```

---

### 5. subentity.split.candidate

```typescript
{
  event_type: "subentity.split.candidate",
  timestamp: number,
  citizen_id: string,
  subentity_id: string,

  reason: "low_silhouette_high_split_gain",

  metrics: {
    silhouette_before: number,
    coherence_before: number,
    coherence_M1: number,      // After split
    coherence_M2: number,
    delta_ctx_M1_M2: number    // Context divergence between splits
  },

  partition: {
    cluster_1_nodes: string[],
    cluster_2_nodes: string[]
  },

  recommended: boolean,
  evidence: string[]
}
```

---

## F. Cypher Snippets (Complete Collection)

### 1. All Pair Metrics in One Query

```cypher
// For pair (A, B)
MATCH (a:SubEntity {id: $A}), (b:SubEntity {id: $B})

// Member overlap (J)
OPTIONAL MATCH (n:Node)-[:MEMBER_OF]->(a)
WITH a, b, collect(id(n)) AS A_nodes
OPTIONAL MATCH (m:Node)-[:MEMBER_OF]->(b)
WITH a, b, A_nodes, collect(id(m)) AS B_nodes,
     apoc.coll.toSet(A_nodes) AS Aset,
     apoc.coll.toSet(B_nodes) AS Bset

// Highway (H)
OPTIONAL MATCH (a)-[h:RELATES_TO]-(b)
WITH a, b, Aset, Bset,
     COALESCE(h.ease, 0) AS ease,
     COALESCE(h.count, 0) AS flow

// WM co-activation (U) - from COACTIVATES_WITH edge
OPTIONAL MATCH (a)-[u:COACTIVATES_WITH]-(b)

RETURN
  // Member Jaccard (J)
  size(apoc.coll.intersection(Aset, Bset)) AS inter_members,
  size(apoc.coll.union(Aset, Bset)) AS union_members,

  // WM co-activation (U)
  COALESCE(u.u_jaccard, 0.0) AS U,

  // Highway (H)
  ease * flow AS highway_utility;
```

---

### 2. Context Distribution for SubEntity

```cypher
// Get attributed stimuli for SubEntity over window
MATCH (s:Stimulus)-[:ATTRIBUTED_TO]->(e:SubEntity {id: $subentity_id})
WHERE s.timestamp > $window_start

RETURN
  s.channel AS channel,
  s.tool AS tool,
  s.outcome_type AS outcome,
  count(*) AS frequency
ORDER BY frequency DESC;
```

**Note:** If ATTRIBUTED_TO doesn't directly link to SubEntities, traverse via WM frames or use attribution metadata from stimulus processing.

---

### 3. Top Overlap Candidates

```cypher
// Find SubEntity pairs with high Jaccard for review
MATCH (a:SubEntity)<-[:MEMBER_OF]-(n:Node)-[:MEMBER_OF]->(b:SubEntity)
WHERE a.citizen_id = $citizen AND b.citizen_id = $citizen
  AND id(a) < id(b)  // Avoid duplicates

WITH a, b, count(n) AS shared
MATCH (a)<-[:MEMBER_OF]-(na:Node)
WITH a, b, shared, count(na) AS size_a
MATCH (b)<-[:MEMBER_OF]-(nb:Node)
WITH a, b, shared, size_a, count(nb) AS size_b

WITH a, b, shared,
     shared * 1.0 / (size_a + size_b - shared) AS jaccard

WHERE jaccard > 0.5  // Configurable threshold for candidates

RETURN a.id AS entity_A, b.id AS entity_B, jaccard
ORDER BY jaccard DESC
LIMIT 50;
```

---

## G. Acceptance Tests

### 1. Creation-Time Redirect

**Setup:**
- Existing SubEntity B with members {n1, n2, n3, n4}
- Seed candidate E' with members {n2, n3, n4, n5}
- S_red(E', B) = 0.94 (> Q90 for cohort)

**Expected:**
- ✅ E' is NOT created
- ✅ Seed members {n2, n3, n4, n5} attached to B with weak priors
- ✅ Event `candidate.redirected` emitted with from: E', to: B

**Verification:**
```cypher
MATCH (b:SubEntity {id: $B})<-[m:MEMBER_OF]-(n:Node)
WHERE n.id IN $seed_members
RETURN count(n) AS redirected_count;
// Should equal 4
```

---

### 2. Promotion with Redundancy Pressure

**Setup:**
- Two candidate SubEntities A, B with S_red(A,B) = 0.89
- Q_geom(A) = 0.65, Q_geom(B) = 0.67
- R_A (redundancy pressure) = 0.89, R_B = 0.89
- D_A (differentiation credit) = 0.15, D_B = 0.18

**Expected:**
- ✅ Both SubEntities face redundancy penalty: Q* = Q_geom × exp(-α × percentile(R))
- ✅ Only ONE SubEntity (higher Q* after adjustment) promotes to Provisional
- ✅ Other SubEntity stays Candidate or marks for merge review

**Verification:** Check promotion events and quality scores after gate cycle

---

### 3. Merge Improves Coherence

**Setup:**
- SubEntities A, B with S_red(A,B) = 0.92 (> Q90)
- coherence(A) = 0.71, coherence(B) = 0.68
- Simulated coherence(M) = 0.73

**Expected:**
- ✅ Merge accepted (coherence preserved: 0.73 ≥ max(0.71, 0.68))
- ✅ Event `subentity.merged` emitted
- ✅ WM SubEntity count does NOT inflate (K stable or decreases by 1)

**Verification:**
```cypher
MATCH (m:SubEntity {id: $M})<-[:MEMBER_OF]-(n:Node)
WITH m, collect(n) AS members
// Compute coherence (mean pairwise similarity)
RETURN apoc.algo.meanPairwiseSimilarity(members) AS coherence;
// Should be ≥ 0.73
```

---

### 4. Complementarity Preserved

**Setup:**
- SubEntities A, B with S_use(A,B) = 0.86 (> Q80)
- H(A,B) = 0.72 (> Q60)
- ΔCtx(A,B) = 0.68 (> Q60)

**Expected:**
- ✅ SubEntities remain separate
- ✅ Event `complementarity.marked` emitted
- ✅ WM diversity increases when stimulus touches their highway
- ✅ Relation property `complementarity_strength` set on RELATES_TO(A,B)

**Verification:**
```cypher
MATCH (a:SubEntity {id: $A})-[h:RELATES_TO]-(b:SubEntity {id: $B})
RETURN h.complementarity_strength AS strength;
// Should be present and > 0
```

---

### 5. Injection Overlap Penalty

**Setup:**
- SubEntities A, B with S_red(A,B) = 0.91 (near-duplicates)
- Stimulus attributes to both with similar scores: s_A = 0.82, s_B = 0.79
- β (overlap sensitivity) = 0.3

**Expected:**
- ✅ Overlap penalty applied: P_A ≈ 0.82 × 0.79 × 1 = 0.65
- ✅ Adjusted scores: s_A' = 0.82 - 0.3×0.65 = 0.625, s_B' = 0.79 - 0.3×0.65 = 0.595
- ✅ After softmax, SubEntity-channel mass concentrates on A (higher quality)
- ✅ Total amplifier energy does NOT double-boost duplicates

**Verification:** Check injection telemetry for SubEntity-channel allocation; verify sum(subentity_shares) ≈ 1.0 and dominant share goes to higher-quality SubEntity

---

## H. Rollout Plan (Low-Risk Phasing)

### Week 1: Observation (No Automation)

**Ship:**
- ✅ On-demand pair metric computation (see §A.1)
- ✅ Events: `pair_scored`, `merge.candidate`, `complementarity.marked`
- ✅ Dashboard: "Overlap Clinic" panel with manual trigger for top-N pair analysis
- ✅ COACTIVATES_WITH edge tracking (see `wm_coactivation_tracking.md`)

**NO automated actions** - operators manually trigger pair analysis and review recommendations

**Success Criteria:**
- On-demand computation completes <50ms per pair
- Events emit with complete provenance
- Dashboard displays pairs, scores, decisions when triggered
- Zero false-positive MERGE recommendations (manual review)

---

### Week 2: Creation-Time Redirect

**Enable:**
- ✅ Creation-time redirect (§D.1)
- ✅ Event: `candidate.redirected`

**Monitoring:**
- Track redirection rate (should be low, <5% of candidates)
- Verify redirected members join existing SubEntities cleanly
- Check for unintended SubEntity growth (orphan ratio should not spike)

**Rollback trigger:** >10% redirection rate or orphan ratio increases >5%

---

### Week 3: Quality Gate Modifiers

**Enable:**
- ✅ Redundancy pressure penalty (f_red)
- ✅ Differentiation credit boost (f_use)

**Monitoring:**
- Track Q* distribution vs Q_geom (should shift modestly, not collapse)
- Verify SubEntities with high R_E face promotion resistance
- Verify SubEntities with high D_E get promotion boost

**Rollback trigger:** >20% of SubEntities fail gates due to redundancy penalty alone

---

### Week 4: Auto-Merge (Feature Flag)

**Enable (behind flag `auto_merge_enabled`):**
- ✅ Automated merge for pairs with:
  - S_red > Q95 (very high redundancy)
  - Coherence acceptance met
  - WM dry-run passed
  - Both SubEntities low quality (min(Q) < Q30)

**Monitoring:**
- Track merge rate (expect <1-2% of SubEntity pairs per week)
- Verify post-merge coherence ≥ pre-merge max
- Verify WM SubEntity count stable or decreasing
- Keep human "undo" via {old→new} mapping

**Rollback trigger:** Any merge that degrades coherence or causes WM instability

---

### Week 5+: Split Review, Complementarity Ribbons

**Enable:**
- ✅ Split candidate detection + manual review UI
- ✅ Complementarity ribbons in dashboard (visual encoding for S_use pairs)
- ✅ Injection overlap penalty (§D.4)

**Monitoring:**
- Track split proposals (expect rare, <1% of SubEntities per month)
- Verify complementarity pairs show in WM diversity metrics
- Verify injection doesn't over-penalize (check amplifier effectiveness)

---

## I. Why This Architecture Is Correct

### 1. Defends High Overlap

**Problem:** Previous thinking might optimize "keep overlap low globally"

**Solution:** Differentiation distinguishes useful overlap (S_use: highways + context divergence) from redundant overlap (S_red: similarity without differentiation)

**Example:** Utopia/dystopia SubEntities share 90% of substrate (same current reality) but diverge in projected outcomes/affect → high S_use, keep separate

---

### 2. Preserves Zero-Constant Doctrine

**All cutoffs are percentiles:**
- Q90 for redundancy threshold
- Q80 for usefulness recognition
- Q60 for highway/context requirements
- Q50 for quality comparison

**All parameters learned:**
- α (redundancy/credit strength) from promotion effectiveness
- β (overlap penalty) from injection outcomes
- Percentile bands adapt to citizen's cohort over time

---

### 3. Observable & Testable

**Every decision emits events** with full provenance (evidence: frame IDs, stimulus IDs, highway IDs)

**Five acceptance tests** cover critical paths:
- Creation redirect
- Promotion pressure
- Merge coherence
- Complementarity preservation
- Injection penalty

---

### 4. Integrates Cleanly

**Reuses existing substrate:**
- Quality scores (Q_geom from quality_gates)
- Highway ease/count (RELATES_TO)
- Concentration (H from injection)
- WM frames (from wm.emit)
- Attribution (from stimulus diversity)

**Doesn't fight existing logic** - extends it with differentiation layer

---

### 5. Safe Rollout

**Phased activation** (observe → redirect → quality → merge → split)

**Feature flags** for automation

**Undo capability** via {old→new} mapping

**Acceptance gates** prevent degradation (coherence, WM stability)

---

## J. Implementation Checklist

**For Backend (Atlas):**
- [ ] Implement on-demand pair metrics computation (see §A.1)
  - [ ] `compute_jaccard_from_members(A, B)` - O(N) member overlap
  - [ ] `compute_cosine_from_embeddings(A, B)` - O(1) if embeddings cached
  - [ ] `compute_context_divergence(A, B)` - JSD over stimulus distributions
  - [ ] U from `COACTIVATES_WITH` edge, H from `RELATES_TO` edge
  - [ ] Normalize via cohort percentiles on-demand or short cache
  - [ ] Compute S_red, S_use scores
  - [ ] Emit `pair_scored` events when computed
- [ ] Implement COACTIVATES_WITH edge tracking (see `wm_coactivation_tracking.md`)
- [ ] Implement creation-time redirect in SubEntity emergence
- [ ] Implement quality modifier in quality gates (f_red, f_use)
- [ ] Implement merge acceptance criteria in merge/split procedures
- [ ] Implement injection overlap penalty in stimulus injection
- [ ] Create Cypher queries for all metrics (see §F)
- [ ] Optional: 5-minute cache for repeated pair queries

**For Frontend (Iris):**
- [ ] Create "Overlap Clinic" dashboard panel with manual trigger
- [ ] Display top-N pairs with J, S_red, S_use, decision (on demand)
- [ ] Add "Review Merge" and "Mark Complementary" actions
- [ ] Show complementarity ribbons on SubEntity visualizations
- [ ] Subscribe to overlap events (pair_scored, merge.candidate, etc.)

**For Operations (Victor):**
- [ ] Set up alerting for high merge rates (>5% pairs/week)
- [ ] Create undo procedure for merges (restore from {old→new} mapping)
- [ ] Monitor coherence distribution post-merge
- [ ] Document rollout phases and rollback triggers
- [ ] Monitor on-demand computation latency (<50ms per pair)

---

**Status:** Normative specification complete. Ready for integration into subentity_layer, entity_emergence, quality_gates, merge_split, stimulus_injection.

**Next Steps:**
1. Review and approve this normative spec
2. Update five referencing specs with integration points
3. Implement on-demand pair metrics (Atlas)
4. Implement COACTIVATES_WITH tracking (Atlas - see `wm_coactivation_tracking.md`)
5. Build Overlap Clinic dashboard with manual trigger (Iris)
6. Begin Week 1 rollout (observation only)

---

**Confidence:** 0.95 - Architecture is substrate-native, zero-constant, observable, testable, and safely phased.
