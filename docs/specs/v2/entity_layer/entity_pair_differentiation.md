---
title: Entity Pair Differentiation (v0)
status: draft
owner: @ada (architecture), @atlas (implementation)
last_updated: 2025-10-26
depends_on:
  - wm_selection_persistence.md
  - ../stimuli/stimulus_diversity.md
  - ../consciousness_engine/energy_dynamics.md
summary: >
  Measure whether high entity overlap is USEFUL (branching scenarios, counterfactuals)
  or REDUNDANT (duplicates needing merge). Uses divergence metrics + outcome evidence +
  exclusivity to classify pairs. Zero magic constants - all gates learned from cohort.
---

# Entity Pair Differentiation

## 1. Context - What problem are we solving?

**The fundamental question:** When two entities share 80%+ of their member nodes, is this:
- **Useful overlap** - Same substrate, different meanings (utopia/dystopia scenarios, investigator/builder modes)
- **Redundant overlap** - Same substrate, same meaning (duplicates, merge candidates)

**Why this matters:**

**Useful overlap is a FEATURE:**
- Branching scenarios: utopia/dystopia share world-model but diverge on outcomes
- Context-dependent modes: investigator/builder use same knowledge, different tools/approaches
- Counterfactual reasoning: consciousness holding "what-if" alternatives in superposition

**Redundant overlap is BLOAT:**
- Duplicate entities: two entities doing identical work, fragmenting activation
- Architectural debt: unclear boundaries, membership confusion
- WM pollution: redundant entities competing for attention slots

**Current state:** No way to distinguish. High overlap is ambiguous.

**Solution:** Measure divergence across activation contexts, link patterns, outcomes, and affect. High divergence + high overlap = useful. Low divergence + high overlap = redundant.

---

## 2. Measurement Framework

### 2.1 Core Principle

**Overlap itself is neutral.** What matters is **how overlapping nodes are USED**.

Measure five divergence dimensions:
1. **D_ctx** - Activation context divergence (channels, tools, partners, missions)
2. **D_link** - Link pattern divergence (structural emphasis within shared nodes)
3. **D_out** - Outcome divergence (mission results, incident patterns)
4. **D_aff** - Affect divergence (emotional coloring of stimuli)
5. **X** - Exclusivity (mutual exclusion in WM selection)

Plus two utility dimensions:
6. **U_out** - Outcome utility (which entity correlates with better outcomes)
7. **E** - Efficiency (outcome per energy spent)

**All metrics are cohort-normalized** (percentiles over pairs in window W) - **zero magic constants**.

### 2.2 Input Data (All Already Streaming)

**From WM selection history** (requires `wm_selection_persistence.md`):
- Frames where A/B were selected (via Frame→SELECTED→SubEntity)
- Co-selection patterns
- Selection ranks

**From stimulus attribution** (already in Stimulus Diversity):
- L1/L2 stimuli attributed to A/B (via ATTRIBUTED_TO edges)
- Stimulus metadata: channel, tool, partner, affect

**From graph structure** (already present):
- Member nodes: M_A, M_B
- Internal link patterns within shared members

**From outcome evidence** (already surfaced as L2):
- L2 incidents (backend_error, schema_regression)
- L2 intents (stabilize_narrative, reconcile_beliefs)
- Mission completion events
- TRACE seats (positive/negative outcomes)

**From injection telemetry** (already streaming):
- Energy budgets allocated
- Nodes activated per frame
- Flip yields

---

## 3. Divergence Metrics

### 3.1 Activation Context Divergence (D_ctx)

**What it measures:** Do entities A and B activate in different CONTEXTS?

**Method:** Jensen-Shannon Divergence over context distributions

**Context vector per frame:**
```python
context = {
    "channel": "chat" | "error_log" | "web" | "crypto" | ...,
    "tool": "Browser.Navigate" | "Runbook.Restart" | "Query.Exchange" | ...,
    "partner": person_id (if applicable),
    "mission_type": "investigate" | "build" | "monitor" | "respond" | ...
}
```

**Computation:**

```python
def compute_D_ctx(A, B, window_days=30):
    """Compute activation context divergence via JSD."""

    cutoff = now_ms() - (window_days * 24 * 60 * 60 * 1000)

    # Get frames where A was selected
    frames_A = db.query("""
        MATCH (f:Frame)-[:SELECTED]->(a:SubEntity {name: $A})
        MATCH (f)-[:TRIGGERED_BY]->(s:Stimulus)
        WHERE f.timestamp_ms >= $cutoff
        RETURN s.channel AS channel,
               s.metadata.tool AS tool,
               s.metadata.partner AS partner,
               s.metadata.mission_type AS mission_type
    """, {"A": A, "cutoff": cutoff})

    # Get frames where B was selected
    frames_B = db.query(...same for B...)

    # Build context histograms
    hist_A = Counter()
    for frame in frames_A:
        context_key = (frame.channel, frame.tool, frame.partner, frame.mission_type)
        hist_A[context_key] += 1

    hist_B = Counter()
    for frame in frames_B:
        context_key = (frame.channel, frame.tool, frame.partner, frame.mission_type)
        hist_B[context_key] += 1

    # Normalize to probability distributions
    total_A = sum(hist_A.values())
    total_B = sum(hist_B.values())

    P_A = {k: v/total_A for k, v in hist_A.items()}
    P_B = {k: v/total_B for k, v in hist_B.items()}

    # Compute Jensen-Shannon Divergence (0-1 range)
    jsd = compute_jsd(P_A, P_B)

    return jsd
```

**Interpretation:**
- High D_ctx (>0.7): Entities activate in DIFFERENT contexts (investigator on errors, builder on file_changes)
- Low D_ctx (<0.3): Entities activate in SAME contexts (likely duplicates)

---

### 3.2 Link Pattern Divergence (D_link)

**What it measures:** Within shared nodes, do entities emphasize different link patterns?

**Method:** JSD over link-type histograms among shared members

**Computation:**

```python
def compute_D_link(A, B):
    """Compute link pattern divergence within shared members."""

    # Get shared member nodes
    shared = db.query("""
        MATCH (a:SubEntity {name: $A})<-[:MEMBER_OF]-(n:Node)
        WITH collect(id(n)) AS A_nodes
        MATCH (b:SubEntity {name: $B})<-[:MEMBER_OF]-(m:Node)
        WITH A_nodes, collect(id(m)) AS B_nodes
        RETURN [x IN A_nodes WHERE x IN B_nodes] AS shared_ids
    """, {"A": A, "B": B})

    if len(shared.shared_ids) < 10:  # Too few shared nodes for meaningful comparison
        return 0.0

    # Get internal link types for A within shared nodes
    links_A = db.query("""
        MATCH (n:Node)-[r]->(m:Node)
        WHERE id(n) IN $shared AND id(m) IN $shared
          AND exists((n)<-[:MEMBER_OF]-(:SubEntity {name: $A}))
        RETURN type(r) AS link_type, count(*) AS count
    """, {"shared": shared.shared_ids, "A": A})

    # Get internal link types for B within shared nodes
    links_B = db.query(...same for B...)

    # Build link-type histograms
    hist_A = {row.link_type: row.count for row in links_A}
    hist_B = {row.link_type: row.count for row in links_B}

    # Normalize to probability distributions
    P_A = normalize(hist_A)
    P_B = normalize(hist_B)

    # Compute JSD
    jsd = compute_jsd(P_A, P_B)

    return jsd
```

**Interpretation:**
- High D_link (>0.6): Entities traverse shared nodes via DIFFERENT link types (Validator emphasizes BLOCKS, Architect emphasizes ENABLES)
- Low D_link (<0.3): Entities use same link patterns (likely duplicates)

---

### 3.3 Outcome Divergence (D_out)

**What it measures:** Do frames where A dominates vs B dominates lead to different outcomes?

**Method:** 1 - Jaccard over outcome node sets, or log-odds separation on success rates

**Computation:**

```python
def compute_D_out(A, B, window_days=30):
    """Compute outcome divergence between A-dominant and B-dominant frames."""

    cutoff = now_ms() - (window_days * 24 * 60 * 60 * 1000)

    # Get outcomes for A-dominant frames (A in top-3, B not in top-7)
    outcomes_A = db.query("""
        MATCH (f:Frame)-[:SELECTED {rank: 1..3}]->(a:SubEntity {name: $A})
        WHERE f.timestamp_ms >= $cutoff
          AND NOT (f)-[:SELECTED {rank: 1..7}]->(:SubEntity {name: $B})
        OPTIONAL MATCH (f)-[:LED_TO]->(o:Outcome)
        RETURN collect(DISTINCT o.type) AS outcome_types
    """, {"A": A, "B": B, "cutoff": cutoff})

    # Get outcomes for B-dominant frames (B in top-3, A not in top-7)
    outcomes_B = db.query(...same for B...)

    # Compute Jaccard similarity over outcome types
    outcomes_A_set = set(outcomes_A.outcome_types)
    outcomes_B_set = set(outcomes_B.outcome_types)

    if not outcomes_A_set and not outcomes_B_set:
        return 0.0  # No outcomes for either

    jaccard = len(outcomes_A_set & outcomes_B_set) / len(outcomes_A_set | outcomes_B_set)

    # Divergence = 1 - similarity
    return 1.0 - jaccard
```

**Alternative (success rate difference):**

```python
def compute_D_out_success(A, B, window_days=30):
    """Compute outcome divergence via success rate difference."""

    # Success rate when A dominates
    success_A = db.query("""
        MATCH (f:Frame)-[:SELECTED {rank: 1..3}]->(a:SubEntity {name: $A})
        WHERE f.timestamp_ms >= $cutoff
          AND NOT (f)-[:SELECTED {rank: 1..7}]->(:SubEntity {name: $B})
        OPTIONAL MATCH (f)-[:LED_TO]->(o:Outcome)
        WITH count(f) AS total,
             sum(CASE WHEN o.outcome_type = 'success' THEN 1 ELSE 0 END) AS success
        RETURN toFloat(success) / total AS success_rate
    """, {"A": A, "B": B, "cutoff": cutoff})

    # Success rate when B dominates
    success_B = db.query(...same for B...)

    # Divergence = absolute difference in success rates
    return abs(success_A.success_rate - success_B.success_rate)
```

**Interpretation:**
- High D_out (>0.7): Entities correlate with DIFFERENT outcomes (Security → incidents, Innovation → new_features)
- Low D_out (<0.3): Entities lead to SAME outcomes (likely duplicates)

---

### 3.4 Affect Divergence (D_aff)

**What it measures:** Do entities activate on stimuli with different emotional coloring?

**Method:** 1 - cosine similarity between mean affect vectors

**Computation:**

```python
def compute_D_aff(A, B, window_days=30):
    """Compute affect divergence from attributed stimuli."""

    cutoff = now_ms() - (window_days * 24 * 60 * 60 * 1000)

    # Get affect from stimuli attributed to A
    affect_A = db.query("""
        MATCH (a:SubEntity {name: $A})<-[:ATTRIBUTED_TO]-(s:Stimulus)
        WHERE s.timestamp_ms >= $cutoff
          AND s.metadata.valence IS NOT NULL
        RETURN avg(s.metadata.valence) AS avg_valence,
               avg(s.metadata.arousal) AS avg_arousal
    """, {"A": A, "cutoff": cutoff})

    # Get affect from stimuli attributed to B
    affect_B = db.query(...same for B...)

    # Compute cosine distance between affect vectors
    vec_A = [affect_A.avg_valence, affect_A.avg_arousal]
    vec_B = [affect_B.avg_valence, affect_B.avg_arousal]

    cosine_sim = dot(vec_A, vec_B) / (norm(vec_A) * norm(vec_B))

    # Divergence = 1 - similarity
    return 1.0 - cosine_sim
```

**Interpretation:**
- High D_aff (>0.6): Entities activate on stimuli with DIFFERENT affect (Security on negative-valence threats, Innovation on positive-valence opportunities)
- Low D_aff (<0.3): Entities activate on same affective stimuli (likely duplicates)

---

### 3.5 Exclusivity (X)

**What it measures:** How rarely do A and B co-appear in top-K WM?

**Method:** 1 - (co-selection rate / min selection rate)

**Computation:**

```python
def compute_exclusivity(A, B, window_days=30):
    """Compute mutual exclusion in WM selection."""

    cutoff = now_ms() - (window_days * 24 * 60 * 60 * 1000)

    stats = db.query("""
        MATCH (f:Frame)
        WHERE f.timestamp_ms >= $cutoff

        OPTIONAL MATCH (f)-[:SELECTED]->(a:SubEntity {name: $A})
        OPTIONAL MATCH (f)-[:SELECTED]->(b:SubEntity {name: $B})

        WITH count(f) AS total_frames,
             count(a) AS frames_A,
             count(b) AS frames_B,
             count(CASE WHEN a IS NOT NULL AND b IS NOT NULL THEN 1 END) AS frames_both

        RETURN total_frames, frames_A, frames_B, frames_both
    """, {"A": A, "B": B, "cutoff": cutoff})

    # P(A and B co-selected)
    p_both = stats.frames_both / stats.total_frames

    # min(P(A), P(B))
    p_A = stats.frames_A / stats.total_frames
    p_B = stats.frames_B / stats.total_frames
    p_min = min(p_A, p_B)

    # Exclusivity = 1 - (co-selection / min-selection)
    if p_min == 0:
        return 0.0

    exclusivity = 1.0 - (p_both / p_min)

    return exclusivity
```

**Interpretation:**
- High X (>0.7): Entities RARELY appear together (mutually exclusive scenarios)
- Low X (<0.3): Entities OFTEN appear together (likely collaborators or duplicates)

---

## 4. Utility Metrics

### 4.1 Outcome Utility (U_out)

**What it measures:** Which entity correlates with better outcomes?

**Method:** Observational uplift (success rate difference when A dominates vs B dominates)

**MVP Computation (Simple):**

```python
def compute_outcome_utility(A, B, window_days=30):
    """Compute which entity correlates with better outcomes."""

    cutoff = now_ms() - (window_days * 24 * 60 * 60 * 1000)

    # Success rate when A dominates (A in top-3, B not in top-7)
    success_A = db.query("""
        MATCH (f:Frame)-[:SELECTED {rank: 1..3}]->(a:SubEntity {name: $A})
        WHERE f.timestamp_ms >= $cutoff
          AND NOT (f)-[:SELECTED {rank: 1..7}]->(:SubEntity {name: $B})
        OPTIONAL MATCH (f)-[:LED_TO]->(o:Outcome)
        WITH count(f) AS total,
             sum(CASE WHEN o.outcome_type = 'success' THEN 1 ELSE 0 END) AS success
        RETURN total, success, toFloat(success) / total AS success_rate
    """, {"A": A, "B": B, "cutoff": cutoff})

    # Success rate when B dominates
    success_B = db.query(...same for B...)

    # Uplift = difference in success rates
    uplift_A = success_A.success_rate - success_B.success_rate

    return {
        "uplift_A": uplift_A,
        "uplift_B": -uplift_A,  # Symmetric
        "success_rate_A": success_A.success_rate,
        "success_rate_B": success_B.success_rate,
        "frames_A": success_A.total,
        "frames_B": success_B.total
    }
```

**Phase 2 Enhancement (Stratified):**

```python
def compute_outcome_utility_stratified(A, B, window_days=30):
    """Compute uplift controlling for rho quantiles."""

    # Stratify by rho (low/medium/high criticality)
    rho_bands = [(0.0, 0.33), (0.33, 0.67), (0.67, 1.0)]

    stratified_uplift = []

    for (rho_min, rho_max) in rho_bands:
        # Compute success rates within this rho stratum
        success_A = db.query("""
            MATCH (f:Frame)-[:SELECTED {rank: 1..3}]->(a:SubEntity {name: $A})
            WHERE f.timestamp_ms >= $cutoff
              AND f.rho >= $rho_min AND f.rho < $rho_max
              AND NOT (f)-[:SELECTED {rank: 1..7}]->(:SubEntity {name: $B})
            ...compute success_rate...
        """, {"A": A, "B": B, "cutoff": cutoff, "rho_min": rho_min, "rho_max": rho_max})

        success_B = db.query(...same for B...)

        uplift = success_A.success_rate - success_B.success_rate
        weight = success_A.total + success_B.total  # Stratum size

        stratified_uplift.append({
            "rho_band": (rho_min, rho_max),
            "uplift": uplift,
            "weight": weight
        })

    # Weighted average across strata
    total_weight = sum(s["weight"] for s in stratified_uplift)
    avg_uplift = sum(s["uplift"] * s["weight"] for s in stratified_uplift) / total_weight

    return avg_uplift
```

**Interpretation:**
- Positive U_out(A>B): A-dominant frames have higher success rate
- Negative U_out(A>B): B-dominant frames have higher success rate
- Near-zero: No clear utility difference

**Note:** This is CORRELATION, not causation. High uplift suggests A is "better" in contexts where it activates, not that A CAUSES better outcomes.

---

### 4.2 Efficiency (E)

**What it measures:** Outcome achieved per energy spent

**Computation:**

```python
def compute_efficiency(entity, window_days=30):
    """Compute efficiency = outcome / energy."""

    cutoff = now_ms() - (window_days * 24 * 60 * 60 * 1000)

    stats = db.query("""
        MATCH (f:Frame)-[:SELECTED]->(e:SubEntity {name: $entity})
        WHERE f.timestamp_ms >= $cutoff
        OPTIONAL MATCH (f)-[:LED_TO]->(o:Outcome)

        WITH avg(f.budget_allocated) AS avg_energy,
             avg(f.nodes_activated) AS avg_nodes,
             sum(CASE WHEN o.outcome_type = 'success' THEN 1 ELSE 0 END) AS success_count,
             count(f) AS total_frames

        RETURN avg_energy,
               avg_nodes,
               toFloat(success_count) / total_frames AS success_rate,
               success_rate / avg_energy AS efficiency
    """, {"entity": entity, "cutoff": cutoff})

    return stats.efficiency
```

**Interpretation:**
- High E: Entity achieves outcomes with low energy expenditure (efficient)
- Low E: Entity requires high energy for outcomes (inefficient)

---

## 5. Composite Scores

### 5.1 Useful-Overlap Score (S_use)

**What it captures:** Same substrate, different meanings

**Formula:**

```
S_use = gmean(J̃, max(D̃_ctx, D̃_link, D̃_out, D̃_aff), X̃)
```

Where:
- `J̃` = cohort-normalized Jaccard (percentile over all pairs in window W)
- `D̃_*` = cohort-normalized divergence metrics
- `X̃` = cohort-normalized exclusivity
- `gmean` = geometric mean (punishes low dimensions)

**Intuition:** High overlap AND high divergence (in at least one dimension) AND exclusivity

**Computation:**

```python
def compute_S_use(A, B, cohort_stats):
    """Compute useful-overlap score."""

    # Raw metrics
    J = compute_jaccard(A, B)
    D_ctx = compute_D_ctx(A, B)
    D_link = compute_D_link(A, B)
    D_out = compute_D_out(A, B)
    D_aff = compute_D_aff(A, B)
    X = compute_exclusivity(A, B)

    # Cohort-normalize (percentile transformation)
    J_norm = cohort_stats.percentile_rank("jaccard", J)
    D_ctx_norm = cohort_stats.percentile_rank("D_ctx", D_ctx)
    D_link_norm = cohort_stats.percentile_rank("D_link", D_link)
    D_out_norm = cohort_stats.percentile_rank("D_out", D_out)
    D_aff_norm = cohort_stats.percentile_rank("D_aff", D_aff)
    X_norm = cohort_stats.percentile_rank("X", X)

    # Max divergence (at least ONE dimension highly divergent)
    max_divergence = max(D_ctx_norm, D_link_norm, D_out_norm, D_aff_norm)

    # Geometric mean
    S_use = gmean([J_norm, max_divergence, X_norm])

    return S_use
```

---

### 5.2 Redundancy Score (S_red)

**What it captures:** Same substrate, same meaning (duplicates)

**Formula:**

```
S_red = gmean(J̃, 1-D̃_ctx, 1-D̃_link, 1-D̃_out, 1-D̃_aff, co-selectioñ)
```

**Intuition:** High overlap AND low divergences AND frequently co-selected

**Computation:**

```python
def compute_S_red(A, B, cohort_stats):
    """Compute redundancy score."""

    # Raw metrics
    J = compute_jaccard(A, B)
    D_ctx = compute_D_ctx(A, B)
    D_link = compute_D_link(A, B)
    D_out = compute_D_out(A, B)
    D_aff = compute_D_aff(A, B)
    co_selection = compute_co_selection_rate(A, B)

    # Cohort-normalize
    J_norm = cohort_stats.percentile_rank("jaccard", J)
    D_ctx_norm = cohort_stats.percentile_rank("D_ctx", D_ctx)
    D_link_norm = cohort_stats.percentile_rank("D_link", D_link)
    D_out_norm = cohort_stats.percentile_rank("D_out", D_out)
    D_aff_norm = cohort_stats.percentile_rank("D_aff", D_aff)
    co_sel_norm = cohort_stats.percentile_rank("co_selection", co_selection)

    # Geometric mean (low divergence = high redundancy)
    S_red = gmean([
        J_norm,
        1.0 - D_ctx_norm,
        1.0 - D_link_norm,
        1.0 - D_out_norm,
        1.0 - D_aff_norm,
        co_sel_norm
    ])

    return S_red
```

---

### 5.3 Preference Score (S_prefer)

**What it captures:** Which entity is "better" (correlates with better outcomes)

**Formula:**

```
S_prefer(A > B) = gmean(Ũ_out(A>B), Ẽ(A))
```

**Computation:**

```python
def compute_S_prefer(A, B, cohort_stats):
    """Compute preference scores (which is better)."""

    # Outcome utility
    U = compute_outcome_utility(A, B)
    uplift_A = U["uplift_A"]
    uplift_B = U["uplift_B"]

    # Efficiency
    E_A = compute_efficiency(A)
    E_B = compute_efficiency(B)

    # Cohort-normalize
    uplift_A_norm = cohort_stats.percentile_rank("uplift", uplift_A)
    uplift_B_norm = cohort_stats.percentile_rank("uplift", uplift_B)
    E_A_norm = cohort_stats.percentile_rank("efficiency", E_A)
    E_B_norm = cohort_stats.percentile_rank("efficiency", E_B)

    # Preference scores
    S_prefer_A = gmean([uplift_A_norm, E_A_norm])
    S_prefer_B = gmean([uplift_B_norm, E_B_norm])

    return {
        "S_prefer_A": S_prefer_A,
        "S_prefer_B": S_prefer_B,
        "preferred": "A" if S_prefer_A > S_prefer_B else "B",
        "magnitude": abs(S_prefer_A - S_prefer_B)
    }
```

---

## 6. Classification

### 6.1 Percentile-Based Gates (Zero Constants)

**Labels:**
- **Useful** - High overlap with high divergence (branching scenarios)
- **Redundant** - High overlap with low divergence (duplicates)
- **Uncertain** - Neither clearly useful nor redundant

**Classification logic:**

```python
def classify_pair(S_use, S_red, cohort_stats):
    """Classify pair using learned percentile gates."""

    # Percentile thresholds (computed from cohort)
    Q90_use = cohort_stats.quantile("S_use", 0.90)
    Q50_red = cohort_stats.quantile("S_red", 0.50)
    Q90_red = cohort_stats.quantile("S_red", 0.90)
    Q50_use = cohort_stats.quantile("S_use", 0.50)

    if S_use > Q90_use and S_red < Q50_red:
        return "Useful"
    elif S_red > Q90_red and S_use < Q50_use:
        return "Redundant"
    else:
        return "Uncertain"
```

**Bootstrap (first 30 days when cohort small):**

```python
# Temporary fixed thresholds until cohort builds
BOOTSTRAP_GATES = {
    "useful": {"S_use_min": 0.70, "S_red_max": 0.40},
    "redundant": {"S_red_min": 0.70, "S_use_max": 0.40},
}

def classify_pair_bootstrap(S_use, S_red):
    """Bootstrap classification with seed thresholds."""

    if S_use > 0.70 and S_red < 0.40:
        return "Useful"
    elif S_red > 0.70 and S_use < 0.40:
        return "Redundant"
    else:
        return "Uncertain"
```

**Transition logic:**

```python
if cohort_size < 30 or window_days < 30:
    label = classify_pair_bootstrap(S_use, S_red)
else:
    label = classify_pair(S_use, S_red, cohort_stats)
```

---

## 7. L2 Assessment Emission

**When pair classified as Useful or Redundant, emit L2 assessment stimulus:**

```json
{
  "level": "L2",
  "type": "assessment.entity_pair",
  "stimulus_id": "assess_pair_felix_investigator_builder_001",
  "timestamp_ms": 1730145600000,
  "citizen_id": "felix",

  "explanation": "Investigator/Builder overlap 88% but contexts diverge (D_ctx=0.77), outcomes diverge (D_out=0.84), and rarely co-select (X=0.73) → branching modes",

  "evidence": [
    "frame_felix_1730000000000",
    "frame_felix_1730100000000",
    "stim_L1_error_log_456",
    "stim_L1_file_change_789"
  ],

  "confidence": 0.82,

  "attribution": {
    "primary_entities": ["Investigator", "Builder"],
    "primary_confidence": 0.82,
    "attribution_method": "hybrid"
  },

  "routing": {
    "mode": "amplify",
    "budget_hint": 1.5,
    "target_entities": ["Investigator", "Builder"]
  },

  "correlation_id": "L2-2025-10-26-001",

  "metadata": {
    "label": "Useful",
    "scores": {
      "S_use": 0.91,
      "S_red": 0.21,
      "S_prefer_A": 0.66,
      "S_prefer_B": 0.34
    },
    "components": {
      "jaccard": 0.88,
      "D_ctx": 0.77,
      "D_link": 0.61,
      "D_out": 0.84,
      "D_aff": 0.79,
      "X": 0.73,
      "uplift_A": 0.12,
      "efficiency_A": 0.82,
      "efficiency_B": 0.75
    }
  }
}
```

**Routing behavior:**

**Useful label:**
- Optionally write relation properties on `RELATES_TO(A,B)`:
  - `counterfactual_strength` = S_use
  - `exclusivity` = X
  - `affect_contrast` = D_aff
  - `preferred_mode` = "A" or "B" (from S_prefer)
- No further action required (overlap is legitimate)

**Redundant label:**
- Emit `subentity.merge.candidate` event with evidence
- Create dashboard alert for operator review
- Do NOT auto-merge (operator approval required)

---

## 8. Daily Analyzer Job

### 8.1 Job Specification

**Schedule:** Daily at 02:00 (after Frame archival at 03:00 completes)

**Scope:** Per citizen, top 100 entity pairs by Jaccard

**Workflow:**

```python
@daily_cron("02:00")
def analyze_entity_pairs(citizen_id):
    """Daily entity pair differentiation analysis."""

    emit_event("analyzer.entity_pairs.started", {
        "citizen_id": citizen_id,
        "timestamp_ms": now()
    })

    window_days = 30

    # Get cohort of entity pairs (top 100 by Jaccard, min 0.5)
    pairs = db.query("""
        MATCH (a:SubEntity)<-[:MEMBER_OF]-(n:Node)-[:MEMBER_OF]->(b:SubEntity)
        WHERE a.citizen_id = $citizen_id
          AND b.citizen_id = $citizen_id
          AND a.name < b.name  // Avoid duplicates (A,B) and (B,A)

        WITH a, b, count(DISTINCT n) AS shared_count

        MATCH (a)<-[:MEMBER_OF]-(m)
        WITH a, b, shared_count, count(DISTINCT m) AS a_count

        MATCH (b)<-[:MEMBER_OF]-(p)
        WITH a, b, shared_count, a_count, count(DISTINCT p) AS b_count

        WITH a, b,
             toFloat(shared_count) / (a_count + b_count - shared_count) AS jaccard

        WHERE jaccard >= 0.5

        RETURN a.name AS A, b.name AS B, jaccard
        ORDER BY jaccard DESC
        LIMIT 100
    """, {"citizen_id": citizen_id})

    # Compute cohort statistics (for percentile normalization)
    cohort_stats = compute_cohort_statistics(pairs, window_days)

    results = []

    for pair in pairs:
        try:
            # Compute all metrics
            metrics = {
                "jaccard": pair.jaccard,
                "D_ctx": compute_D_ctx(pair.A, pair.B, window_days),
                "D_link": compute_D_link(pair.A, pair.B),
                "D_out": compute_D_out(pair.A, pair.B, window_days),
                "D_aff": compute_D_aff(pair.A, pair.B, window_days),
                "X": compute_exclusivity(pair.A, pair.B, window_days),
                "U_out": compute_outcome_utility(pair.A, pair.B, window_days),
                "E_A": compute_efficiency(pair.A, window_days),
                "E_B": compute_efficiency(pair.B, window_days)
            }

            # Compute composite scores
            S_use = compute_S_use(pair.A, pair.B, cohort_stats)
            S_red = compute_S_red(pair.A, pair.B, cohort_stats)
            S_prefer = compute_S_prefer(pair.A, pair.B, cohort_stats)

            # Classify
            label = classify_pair(S_use, S_red, cohort_stats)

            # Emit L2 assessment if Useful or Redundant
            if label != "Uncertain":
                emit_L2_assessment(
                    pair.A, pair.B,
                    metrics, S_use, S_red, S_prefer,
                    label, citizen_id
                )

            results.append({
                "A": pair.A,
                "B": pair.B,
                "metrics": metrics,
                "S_use": S_use,
                "S_red": S_red,
                "S_prefer": S_prefer,
                "label": label
            })

        except Exception as e:
            log_error(f"Failed to analyze pair ({pair.A}, {pair.B}): {e}")
            continue

    emit_event("analyzer.entity_pairs.completed", {
        "citizen_id": citizen_id,
        "pairs_analyzed": len(results),
        "useful_count": sum(1 for r in results if r["label"] == "Useful"),
        "redundant_count": sum(1 for r in results if r["label"] == "Redundant"),
        "uncertain_count": sum(1 for r in results if r["label"] == "Uncertain"),
        "timestamp_ms": now()
    })

    return results
```

### 8.2 Cohort Statistics

**Purpose:** Compute percentile ranks for normalization

```python
def compute_cohort_statistics(pairs, window_days):
    """Compute cohort statistics for percentile normalization."""

    # Compute raw metrics for all pairs
    raw_metrics = {
        "jaccard": [],
        "D_ctx": [],
        "D_link": [],
        "D_out": [],
        "D_aff": [],
        "X": [],
        "uplift": [],
        "efficiency": []
    }

    for pair in pairs:
        raw_metrics["jaccard"].append(pair.jaccard)
        raw_metrics["D_ctx"].append(compute_D_ctx(pair.A, pair.B, window_days))
        raw_metrics["D_link"].append(compute_D_link(pair.A, pair.B))
        raw_metrics["D_out"].append(compute_D_out(pair.A, pair.B, window_days))
        raw_metrics["D_aff"].append(compute_D_aff(pair.A, pair.B, window_days))
        raw_metrics["X"].append(compute_exclusivity(pair.A, pair.B, window_days))

        U = compute_outcome_utility(pair.A, pair.B, window_days)
        raw_metrics["uplift"].append(U["uplift_A"])

        raw_metrics["efficiency"].append(compute_efficiency(pair.A, window_days))

    # Build percentile lookup (each metric → sorted array)
    cohort_stats = CohortStatistics()

    for metric_name, values in raw_metrics.items():
        cohort_stats.add_metric(metric_name, sorted(values))

    return cohort_stats


class CohortStatistics:
    """Cohort statistics for percentile normalization."""

    def __init__(self):
        self.metrics = {}

    def add_metric(self, name, sorted_values):
        """Store sorted values for a metric."""
        self.metrics[name] = sorted_values

    def percentile_rank(self, metric_name, value):
        """Convert raw value to percentile rank (0-1)."""
        sorted_values = self.metrics[metric_name]

        if not sorted_values:
            return 0.5  # Default if no data

        # Binary search for rank
        rank = bisect_left(sorted_values, value)
        percentile = rank / len(sorted_values)

        return percentile

    def quantile(self, metric_name, q):
        """Get value at quantile q (e.g., 0.90 for Q90)."""
        sorted_values = self.metrics[metric_name]

        if not sorted_values:
            return 0.0

        index = int(q * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
```

---

## 9. Acceptance Tests

### 9.1 Counterfactual Pair (Useful)

**Setup:** Two scenario entities (utopia/dystopia) with ~90% overlap

```python
def test_useful_overlap():
    # Create utopia/dystopia entities with shared world-model
    shared_nodes = create_nodes(count=90, type="Concept")
    utopia_unique = create_nodes(count=10, type="Concept", tag="positive")
    dystopia_unique = create_nodes(count=10, type="Concept", tag="negative")

    create_entity("Utopia", members=shared_nodes + utopia_unique)
    create_entity("Dystopia", members=shared_nodes + dystopia_unique)

    # Create frames with context divergence
    # Utopia activates during positive stimuli
    for i in range(100):
        create_frame(
            entities=["Utopia"],
            stimulus=create_stimulus(channel="chat", affect={"valence": 0.8, "arousal": 0.6})
        )

    # Dystopia activates during negative stimuli
    for i in range(100):
        create_frame(
            entities=["Dystopia"],
            stimulus=create_stimulus(channel="chat", affect={"valence": -0.7, "arousal": 0.7})
        )

    # Different outcomes
    link_outcomes("Utopia", outcome_type="success", count=80)
    link_outcomes("Dystopia", outcome_type="failure", count=70)

    # Compute metrics
    metrics = analyze_pair("Utopia", "Dystopia")

    # Assertions
    assert metrics["jaccard"] > 0.85  # High overlap
    assert metrics["D_aff"] > 0.70  # High affect divergence
    assert metrics["D_out"] > 0.70  # High outcome divergence
    assert metrics["X"] > 0.90  # High exclusivity (never co-select)
    assert metrics["S_use"] > 0.70  # Useful overlap
    assert metrics["S_red"] < 0.40  # Low redundancy
    assert metrics["label"] == "Useful"
```

### 9.2 Duplicate Pair (Redundant)

**Setup:** Two entities with ~80% overlap used identically

```python
def test_redundant_overlap():
    # Create two entities with shared nodes
    shared_nodes = create_nodes(count=80, type="Concept")
    runtime_v1_unique = create_nodes(count=20, type="Concept", tag="v1")
    runtime_v2_unique = create_nodes(count=20, type="Concept", tag="v2")

    create_entity("Runtime_v1", members=shared_nodes + runtime_v1_unique)
    create_entity("Runtime_v2", members=shared_nodes + runtime_v2_unique)

    # Create frames with SAME contexts (both activate on errors)
    for i in range(100):
        stimulus = create_stimulus(channel="error_log", tool="Runbook.Restart")

        # Both entities selected together frequently
        create_frame(
            entities=["Runtime_v1", "Runtime_v2"],
            stimulus=stimulus
        )

    # Same outcomes
    link_outcomes("Runtime_v1", outcome_type="success", count=60)
    link_outcomes("Runtime_v2", outcome_type="success", count=62)

    # Compute metrics
    metrics = analyze_pair("Runtime_v1", "Runtime_v2")

    # Assertions
    assert metrics["jaccard"] > 0.75  # High overlap
    assert metrics["D_ctx"] < 0.30  # Low context divergence (same channels/tools)
    assert metrics["D_out"] < 0.20  # Low outcome divergence (same success rates)
    assert metrics["X"] < 0.30  # Low exclusivity (frequently co-select)
    assert metrics["S_use"] < 0.40  # Low useful overlap
    assert metrics["S_red"] > 0.70  # High redundancy
    assert metrics["label"] == "Redundant"
```

### 9.3 Preference Detection

**Setup:** Two entities with overlap, but one performs better

```python
def test_preference():
    # Create pair with overlap
    shared = create_nodes(count=70, type="Concept")
    create_entity("Optimizer", members=shared + create_nodes(30))
    create_entity("Baseline", members=shared + create_nodes(30))

    # Optimizer has higher success rate
    for i in range(100):
        create_frame(entities=["Optimizer"], stimulus=create_stimulus())
        if i < 85:
            link_outcome(frame_id=frame.id, outcome_type="success")

    # Baseline has lower success rate
    for i in range(100):
        create_frame(entities=["Baseline"], stimulus=create_stimulus())
        if i < 60:
            link_outcome(frame_id=frame.id, outcome_type="success")

    # Compute preference
    pref = compute_S_prefer("Optimizer", "Baseline", cohort_stats)

    # Assertions
    assert pref["preferred"] == "Optimizer"
    assert pref["S_prefer_A"] > pref["S_prefer_B"]
    assert pref["magnitude"] > 0.2  # Clear preference
```

---

## 10. Dashboard Integration

**See:** `overlap_clinic_dashboard.md` for complete UI specification

**Summary:** Overlap Clinic panel shows:
- Table of top Jaccard pairs with metrics, scores, labels
- Row actions: Mark counterfactuals, Open merge review, View details, Run what-if
- Evidence panel: Frames, outcomes, link patterns, affect distributions

---

## 11. Implementation Checklist

**Dependencies:**
- [x] WM selection persistence (Frame nodes, SELECTED edges)
- [ ] Outcome labeling (LED_TO edges from frames to outcomes)
- [ ] L2 stimulus emission infrastructure (Stimulus Diversity)
- [ ] Cohort statistics computation

**Analyzer Job:**
- [ ] Daily cron scheduler (02:00)
- [ ] Jaccard pair retrieval (top 100, min 0.5)
- [ ] Metric computation functions (D_ctx, D_link, D_out, D_aff, X, U_out, E)
- [ ] Cohort statistics builder (percentile normalization)
- [ ] Composite score computation (S_use, S_red, S_prefer)
- [ ] Classification logic (bootstrap → learned percentiles)
- [ ] L2 assessment emission

**Observability:**
- [ ] analyzer.entity_pairs.started event
- [ ] analyzer.entity_pairs.completed event
- [ ] assessment.entity_pair L2 stimuli
- [ ] subentity.merge.candidate events (for Redundant pairs)

**Dashboard:**
- [ ] Overlap Clinic panel (see overlap_clinic_dashboard.md)
- [ ] Table view with scores, labels, actions
- [ ] Evidence drill-down
- [ ] Merge review workflow

**Testing:**
- [ ] Unit tests for each metric (D_ctx, D_link, D_out, D_aff, X)
- [ ] Unit tests for composite scores (S_use, S_red, S_prefer)
- [ ] Unit tests for classification (bootstrap + learned)
- [ ] Integration test: counterfactual pair → Useful label
- [ ] Integration test: duplicate pair → Redundant label
- [ ] Integration test: preference detection

---

## 12. Success Criteria

**Measurement accuracy:**
- ✅ Counterfactual pairs (utopia/dystopia) label as Useful (S_use > Q90, S_red < Q50)
- ✅ Duplicate pairs (runtime_v1/runtime_v2) label as Redundant (S_red > Q90, S_use < Q50)
- ✅ Preference correctly identifies entity with higher success rate

**Performance:**
- ✅ Daily analyzer job completes <10 minutes for 100 pairs
- ✅ Metric computation <1 second per pair (parallelizable)
- ✅ Cohort statistics build <30 seconds

**Zero constants:**
- ✅ All classification gates use percentiles (Q90/Q50) from cohort
- ✅ Bootstrap thresholds (0.70, 0.40) only used for first 30 days
- ✅ Smooth transition from bootstrap to learned gates

**Integration:**
- ✅ L2 assessments emit correctly for Useful/Redundant pairs
- ✅ Merge candidates created for Redundant pairs
- ✅ Relation properties written for Useful pairs
- ✅ Dashboard displays pair table with scores and labels

---

## Status

**Specification:** COMPLETE
**Implementation:** READY (pending WM persistence + outcome labeling)
**Dependencies:**
- wm_selection_persistence.md (in progress)
- Outcome labeling strategy (TBD)
**Next steps:**
1. Atlas implements WM persistence (Frame nodes)
2. Define outcome labeling strategy (how to create LED_TO edges)
3. Atlas implements analyzer job + metric computation
4. Iris implements Overlap Clinic dashboard panel
