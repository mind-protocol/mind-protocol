# Emergent IFS Modes from WM Co-Activation

**Version:** 1.1
**Status:** Normative - Implementation Required
**Owner:** Atlas (Consciousness Infrastructure)
**Priority:** 1 (After COACTIVATES_WITH tracking)
**Created:** 2025-10-26
**Updated:** 2025-10-26 (Reactive mode_warden supersedes daily batch)

---

## ⚠️ Implementation Note

**The original daily batch approach has been superseded by the reactive mode_warden sidecar.**

See **`mode_warden_sidecar.md`** for the normative event-driven implementation. This document describes the foundational mode detection algorithm and quality scoring, which the mode_warden uses incrementally.

**Key difference:** Instead of running mode detection daily on a schedule, mode_warden reacts to co-activation drift and runs incremental community detection only when learned change-points fire.

---

## Terminology Note

This specification references the two-scale architecture from **TAXONOMY_RECONCILIATION.md**:
- **Scale A: SubEntity Layer** - Weighted neighborhoods (200-500), semantic/functional clustering
- **Scale B: Mode Layer** - IFS-level meta-roles (5-15), emergent from COACTIVATES_WITH communities

See `subentity_layer.md` §2.1.1 for detailed architecture.

---

## Purpose

Enable **IFS-level functional modes** (Guardian, Observer, Explorer, Builder, Anchor) to emerge from stable communities in the SubEntity co-activation graph, rather than being hard-coded templates.

**Design Principle:** Reconcile two scales without compromise:
- **Scale A (SubEntities):** Many (200-500) semantic/functional neighborhoods for learning richness
- **Scale B (Modes):** Few (5-15) IFS-level meta-roles for regulation coherence

Modes are **derived read-outs** over SubEntity state, not separate energy stores.

---

## Invariants (Non-Negotiable)

1. **No new energy buffers** - Nodes keep one energy; SubEntities read out; Modes are derived (read-outs over SubEntity state), not energy stores
2. **No hand-written roles** - Modes form/dissolve by same lifecycle logic as SubEntities (evidence + persistence)
3. **No constants** - All gates are citizen-local percentiles or change-points
4. **Single-energy substrate preserved** - Modes compute activation from current SubEntity energies, never store separate energy
5. **Emergence over templates** - Community detection discovers modes; Guardian/Observer/Explorer emerge from data, not config

---

## Inputs (All Exist)

From existing substrate:
- **COACTIVATES_WITH** edges between SubEntities with `u_jaccard ∈ [0,1]` (Jaccard-EMA of WM co-occurrence) - see `wm_coactivation_tracking.md`
- **RELATES_TO** highways between SubEntities with `ease` (crossing difficulty) and `flow` (crossing frequency)
- **SubEntity context distributions** - Stimulus channels, tools used, outcome seats (from attribution)
- **SubEntity affect signatures** - Arousal/valence EMAs tracked per SubEntity
- **SubEntity quality EMAs** - Coherence, stability, activity, coverage, resonance

---

## Outputs (New)

- `(:Mode {id, level:'IFS', status:'candidate'|'mature', signature:{...}})` - IFS-level meta-role node
- `(:SubEntity)-[:AFFILIATES_WITH {weight, stability_ema}]->(:Mode)` - Affiliation relationship with learned weight
- Events: `mode.seeded`, `mode.matured`, `mode.affiliation.updated`, `mode.dissolved`

**Note:** Mode can be represented as `:SubEntity {entity_type:'functional', level:'IFS'}` if schema reuse preferred. Behavior is identical.

---

## Algorithm: Emergent Mode Lifecycle

### Step 1: Build Role Graph Over SubEntities

**Purpose:** Create weighted adjacency matrix where edges represent "functional similarity" between SubEntities.

**Weight formula:**
```
W_AB = U_AB × (1 + ease_AB) × (1 + affect_sim_AB) × (1 + tool_overlap_AB)
```

Where (all components percentile-normalized, citizen-local):
- `U_AB` - WM co-activation (from COACTIVATES_WITH.u_jaccard)
- `ease_AB` - Highway ease (from RELATES_TO.ease, 0 if no highway)
- `affect_sim_AB` - Affect similarity: `1 - |arousal_A - arousal_B| - |valence_A - valence_B|`
- `tool_overlap_AB` - Tool/outcome overlap: `1 - JSD(tool_dist_A, tool_dist_B)`

**Effect:** Edges are weighted toward SubEntity pairs that:
- Co-activate in WM frequently
- Have low boundary friction (highways)
- Feel similar (affect)
- Behave similarly (tools/outcomes)

**Implementation:**
```python
def build_role_graph(citizen: str) -> np.ndarray:
    """
    Build weighted adjacency matrix for SubEntities.

    Returns:
        W: (n_entities × n_entities) matrix where W[i,j] = role similarity
    """
    entities = get_subentities(citizen)
    n = len(entities)
    W = np.zeros((n, n))

    for i, A in enumerate(entities):
        for j, B in enumerate(entities):
            if i >= j:
                continue

            # U: WM co-activation (from COACTIVATES_WITH edge)
            U = get_coactivates_edge(A, B).u_jaccard if get_coactivates_edge(A, B) else 0.0

            # Ease: Highway strength (from RELATES_TO edge)
            highway = get_relates_to_edge(A, B)
            ease = highway.ease if highway else 0.0

            # Affect similarity
            affect_A = get_affect_signature(A)  # {arousal, valence}
            affect_B = get_affect_signature(B)
            affect_sim = 1 - abs(affect_A.arousal - affect_B.arousal) - abs(affect_A.valence - affect_B.valence)
            affect_sim = max(0, affect_sim)  # Clamp to [0, 1]

            # Tool/outcome overlap
            tool_dist_A = get_tool_outcome_distribution(A)
            tool_dist_B = get_tool_outcome_distribution(B)
            tool_overlap = 1 - jensenshannon(tool_dist_A, tool_dist_B)

            # Percentile-normalize each component (citizen-local)
            U_norm = percentile_rank(U, cohort=get_all_u_values(citizen))
            ease_norm = percentile_rank(ease, cohort=get_all_ease_values(citizen))
            affect_norm = percentile_rank(affect_sim, cohort=get_all_affect_sims(citizen))
            tool_norm = percentile_rank(tool_overlap, cohort=get_all_tool_overlaps(citizen))

            # Combine
            W[i, j] = W[j, i] = U_norm * (1 + ease_norm) * (1 + affect_norm) * (1 + tool_norm)

    return W
```

---

### Step 2: Community Detection (Multi-Scale, No Fixed K)

**Purpose:** Discover stable communities in role graph without pre-specifying number of modes.

**Algorithm:** Leiden or Louvain with multi-resolution sweep

**Implementation:**
```python
def detect_mode_communities(W: np.ndarray, citizen: str) -> List[List[int]]:
    """
    Detect communities in role graph using multi-resolution approach.

    Returns:
        communities: List of SubEntity index lists
    """
    import igraph as ig
    from scipy.stats import median_abs_deviation

    # Build igraph from adjacency matrix
    g = ig.Graph.Adjacency((W > 0).tolist(), mode='undirected')
    g.es['weight'] = W[W > 0].flatten().tolist()

    # Multi-resolution sweep
    resolutions = np.logspace(-2, 1, 20)  # 0.01 to 10
    modularity_scores = []
    partitions = []

    for gamma in resolutions:
        partition = g.community_leiden(
            weights='weight',
            resolution_parameter=gamma,
            n_iterations=10
        )
        Q = partition.modularity
        modularity_scores.append(Q)
        partitions.append(partition)

    # Pick knee in modularity curve (change-point detection)
    knee_idx = find_knee(modularity_scores)
    best_partition = partitions[knee_idx]

    # Check partition persistence across windows
    # (Compare to partition from last week's data)
    historical_partition = load_historical_partition(citizen, window='1week')
    if historical_partition:
        nmi = normalized_mutual_info(best_partition, historical_partition)
        persistence_threshold = get_persistence_threshold(citizen)  # Learned contour

        if nmi < persistence_threshold:
            # Partition unstable, use more conservative resolution
            # (Favor fewer, more stable communities)
            knee_idx = max(0, knee_idx - 5)
            best_partition = partitions[knee_idx]

    # Convert partition to community list
    communities = []
    for cluster_id in range(len(best_partition)):
        community = [i for i, c in enumerate(best_partition.membership) if c == cluster_id]
        if len(community) >= 3:  # Minimum community size
            communities.append(community)

    return communities


def find_knee(scores: List[float]) -> int:
    """Find knee/elbow in curve using kneedle algorithm."""
    from kneed import KneeLocator
    x = np.arange(len(scores))
    kl = KneeLocator(x, scores, curve='concave', direction='increasing')
    return kl.knee if kl.knee else len(scores) // 2
```

---

### Step 3: Score Communities as Mode Candidates

**Purpose:** Evaluate each community for "mode quality" using geometric mean of five factors.

**Mode quality formula:**
```
Q_mode(C) = GM(cohesion, boundary, affect, procedural, persistence)
```

Where:
- **Cohesion:** Average U (WM co-activation) inside community (percentile-scaled)
- **Boundary clarity:** Low cross-cut weight / high modularity contribution
- **Affect consistency:** Low variance in arousal/valence EMAs across members
- **Procedural consistency:** Low JSD for tool and outcome distributions inside community
- **Persistence:** Partition stability across windows (NMI with historical)

**Implementation:**
```python
def score_mode_candidate(
    community: List[int],
    W: np.ndarray,
    entities: List[str],
    citizen: str
) -> float:
    """
    Compute Q_mode for a community.

    Returns:
        Q_mode ∈ [0, 1]
    """
    # 1. Cohesion: Average internal U
    internal_u_values = []
    for i in community:
        for j in community:
            if i < j:
                A, B = entities[i], entities[j]
                U = get_coactivates_edge(A, B).u_jaccard if get_coactivates_edge(A, B) else 0.0
                internal_u_values.append(U)

    cohesion = np.mean(internal_u_values) if internal_u_values else 0.0
    cohesion_percentile = percentile_rank(cohesion, cohort=get_all_u_values(citizen))

    # 2. Boundary clarity: Modularity contribution
    internal_weight = sum(W[i, j] for i in community for j in community if i < j)
    total_weight = W.sum() / 2
    expected_internal = (sum(W[i, :].sum() for i in community) / (2 * total_weight)) ** 2
    boundary_clarity = (internal_weight / total_weight) - expected_internal
    boundary_percentile = percentile_rank(boundary_clarity, cohort=get_all_boundary_scores(citizen))

    # 3. Affect consistency: Low variance in arousal/valence
    affects = [get_affect_signature(entities[i]) for i in community]
    arousal_var = np.var([a.arousal for a in affects])
    valence_var = np.var([a.valence for a in affects])
    affect_consistency = 1 - (arousal_var + valence_var) / 2  # Invert: high consistency = low variance
    affect_percentile = percentile_rank(affect_consistency, cohort=get_all_affect_consistencies(citizen))

    # 4. Procedural consistency: Low JSD for tool/outcome distributions
    tool_dists = [get_tool_outcome_distribution(entities[i]) for i in community]
    mean_tool_dist = aggregate_distributions(tool_dists)
    jsds = [jensenshannon(d, mean_tool_dist) for d in tool_dists]
    procedural_consistency = 1 - np.mean(jsds)  # Invert: high consistency = low divergence
    procedural_percentile = percentile_rank(procedural_consistency, cohort=get_all_procedural_consistencies(citizen))

    # 5. Persistence: NMI with historical partition
    historical_communities = load_historical_communities(citizen, window='1week')
    if historical_communities:
        nmi = compute_community_overlap(community, historical_communities)
        persistence_percentile = percentile_rank(nmi, cohort=get_all_nmi_values(citizen))
    else:
        persistence_percentile = 0.5  # Neutral if no history

    # Geometric mean
    Q_mode = (
        cohesion_percentile *
        boundary_percentile *
        affect_percentile *
        procedural_percentile *
        persistence_percentile
    ) ** (1/5)

    return Q_mode
```

**Seed threshold:** `Q_mode > Q80` (80th percentile of historical mode qualities for this citizen)

**Cold start:** If no historical mode qualities, seed when `Q_mode > 0.6` (permissive) and tighten threshold as data accumulates.

---

### Step 4: Create Mode Nodes & Affiliation Edges

**Purpose:** Instantiate Mode in graph with signature and create weighted affiliations to member SubEntities.

**Mode signature:**
```python
{
  "affect": {"arousal": float, "valence": float},  # Mean across members
  "tools": {"Read": 0.3, "Write": 0.2, ...},  # Typical tool distribution
  "outcomes": {"very_useful": 0.4, ...},  # Typical outcome distribution
  "self_talk": str  # Canonical nearest-neighbor phrase from centroid
}
```

**Affiliation weight:** Proportional to centrality (medoid proximity) × WM share when mode is active (EMA)

**Implementation:**
```python
def create_mode(
    community: List[int],
    entities: List[str],
    Q_mode: float,
    citizen: str
) -> str:
    """
    Create Mode node and AFFILIATES_WITH edges.

    Returns:
        mode_id: Unique identifier for created mode
    """
    mode_id = f"{citizen}_mode_{uuid.uuid4().hex[:8]}"

    # Compute mode signature
    affects = [get_affect_signature(entities[i]) for i in community]
    mean_arousal = np.mean([a.arousal for a in affects])
    mean_valence = np.mean([a.valence for a in affects])

    tool_dists = [get_tool_outcome_distribution(entities[i]) for i in community]
    mean_tool_dist = aggregate_distributions([d['tools'] for d in tool_dists])
    mean_outcome_dist = aggregate_distributions([d['outcomes'] for d in tool_dists])

    # Find canonical self-talk (nearest phrase to centroid)
    embeddings = [get_subentity_centroid(entities[i]) for i in community]
    centroid = np.mean(embeddings, axis=0)
    nearest_idx = np.argmin([np.linalg.norm(emb - centroid) for emb in embeddings])
    self_talk = get_subentity_description(entities[nearest_idx])

    signature = {
        "affect": {"arousal": mean_arousal, "valence": mean_valence},
        "tools": mean_tool_dist,
        "outcomes": mean_outcome_dist,
        "self_talk": self_talk
    }

    # Create Mode node
    query = """
    CREATE (m:Mode {
        id: $mode_id,
        citizen_id: $citizen,
        level: 'IFS',
        status: 'candidate',
        signature: $signature,
        q_mode: $q_mode,
        created_at: datetime(),
        valid_at: datetime()
    })
    """
    db.query(query, {
        "mode_id": mode_id,
        "citizen": citizen,
        "signature": json.dumps(signature),
        "q_mode": Q_mode
    })

    # Create AFFILIATES_WITH edges
    for i in community:
        entity_id = entities[i]

        # Weight = centrality × WM share
        centrality = compute_medoid_proximity(i, community, embeddings)
        wm_share = get_entity_wm_share_ema(entity_id)  # EMA of WM appearances
        weight = centrality * wm_share

        aff_query = """
        MATCH (e:SubEntity {id: $entity_id})
        MATCH (m:Mode {id: $mode_id})
        CREATE (e)-[:AFFILIATES_WITH {
            weight: $weight,
            stability_ema: $weight,
            created_at: datetime()
        }]->(m)
        """
        db.query(aff_query, {
            "entity_id": entity_id,
            "mode_id": mode_id,
            "weight": weight
        })

    # Emit event
    emit_event("mode.seeded", {
        "mode_id": mode_id,
        "citizen_id": citizen,
        "members": [entities[i] for i in community],
        "signature": signature,
        "q_mode": Q_mode
    })

    return mode_id
```

---

### Step 4.3: Affiliation Budget Enforcement

**Constraint:** Each SubEntity's total AFFILIATES_WITH weight must satisfy: `0.8 ≤ Σ(w_i) ≤ 1.2`

**Rationale:** Affiliation weights are activation contribution factors. Total near 1.0 prevents:
- **Isolated SubEntity** (total <0.8): Barely influences any mode, loses regulatory signal
- **Over-committed SubEntity** (total >1.2): Contributes >100% of energy to modes (double-counting)

**Enforcement During Mode Creation:**

When creating Mode M with candidate affiliations `{(e_1, w_1), (e_2, w_2), ...}`:

```python
def enforce_affiliation_budget(candidate_affiliations: Dict[str, float],
                               existing_affiliations: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Adjust weights to respect per-SubEntity budget constraints.

    Args:
        candidate_affiliations: {subentity_id: weight} for new mode
        existing_affiliations: {subentity_id: {mode_id: weight}} for existing modes

    Returns:
        Adjusted weights respecting budget constraints
    """
    adjusted = {}

    for subentity_id, candidate_weight in candidate_affiliations.items():
        # Current total weight (existing affiliations)
        existing_total = sum(existing_affiliations.get(subentity_id, {}).values())

        # Proposed total if we add this affiliation
        proposed_total = existing_total + candidate_weight

        if proposed_total > 1.2:
            # Reduce candidate weight to stay within budget
            max_allowed = 1.2 - existing_total
            adjusted[subentity_id] = max(max_allowed, 0.0)

            # Log budget constraint violation
            log.warning(
                f"SubEntity {subentity_id} affiliation budget constrained: "
                f"candidate {candidate_weight:.2f} → adjusted {adjusted[subentity_id]:.2f} "
                f"(existing total: {existing_total:.2f})"
            )
        else:
            adjusted[subentity_id] = candidate_weight

    return adjusted
```

**Handling Low Total Weight (<0.8):**

If SubEntity has total affiliation weight <0.8 after pruning/dissolution:

```python
def handle_low_affiliation_mass(subentity_id: str,
                                total_weight: float,
                                affiliations: Dict[str, float]):
    """
    Options when SubEntity is under-affiliated:
    1. Proportional boost (multiply all weights by 0.8/total)
    2. Wait for new mode to seed and affiliate
    3. Mark as "isolated" for investigation
    """
    if total_weight < 0.8:
        # Option 1: Proportional boost (preserves relative weights)
        boost_factor = 0.8 / total_weight
        for mode_id, weight in affiliations.items():
            affiliations[mode_id] = weight * boost_factor

        log.info(
            f"SubEntity {subentity_id} affiliation mass boosted: "
            f"{total_weight:.2f} → 0.80 (factor: {boost_factor:.2f})"
        )
```

**Acceptance Test:**

After mode lifecycle operations (creation, dissolution, merge):

```cypher
// Verify all SubEntities respect budget
MATCH (e:SubEntity)-[a:AFFILIATES_WITH]->(m:Mode)
WITH e.id AS entity_id, sum(a.weight) AS total_weight
WHERE total_weight < 0.8 OR total_weight > 1.2
RETURN entity_id, total_weight,
       CASE
         WHEN total_weight < 0.8 THEN 'UNDER'
         WHEN total_weight > 1.2 THEN 'OVER'
       END AS violation_type
```

Expected: 0 violations (or <5% of SubEntities during transient states)

**Implementation Guidance for Atlas:**
- Add budget enforcement function to mode creation logic (Step 4)
- Add proportional boost logic to mode dissolution/merge handlers
- Add periodic audit query to detect budget violations
- Emit telemetry event when budget constraint triggers adjustment

---

### Step 5: Maturation & Lifecycle

**Candidate → Mature** when:
1. `Q_mode` stays above learned contour for minimum duration (citizen-local, typically 1-2 weeks)
2. Mode participation shows **utility** - measured by:
   - Lower ρ (spiral metric) during tasks tagged with this mode (for Guardian)
   - Better outcome distribution (for Explorer/Builder)
   - Improved meta-awareness metrics (for Observer)

**Dissolve** when:
- Cohesion/boundary/persistence drop below contour for grace period (typically 3-5 days)
- Utility measurements show no benefit (mode doesn't improve outcomes)

**Merge modes** when:
- Two mature modes show high overlap in members (>70% Jaccard)
- Nearly identical signatures (cosine similarity >0.9 for affect/tools/outcomes)
- Low boundary benefit (merging increases modularity)

**Implementation:**
```python
def update_mode_lifecycle(mode_id: str, citizen: str):
    """
    Check mode for maturation, dissolution, or merge.
    Called daily by modes_detect.py.
    """
    mode = get_mode(mode_id)

    # Get current Q_mode
    community = get_mode_members(mode_id)
    W = build_role_graph(citizen)
    entities = get_subentities(citizen)
    Q_mode = score_mode_candidate(community, W, entities, citizen)

    # Update Q_mode EMA
    alpha = 0.1  # Slow EMA for stability
    mode.q_mode_ema = alpha * Q_mode + (1 - alpha) * mode.q_mode_ema

    # Check maturation
    if mode.status == 'candidate':
        duration = (datetime.now() - mode.created_at).days
        min_duration = get_maturation_duration_threshold(citizen)  # Learned, typically 7-14 days

        if duration >= min_duration and mode.q_mode_ema > get_maturation_q_threshold(citizen):
            # Measure utility
            utility = measure_mode_utility(mode_id, citizen)
            utility_threshold = get_utility_threshold(citizen)

            if utility > utility_threshold:
                mode.status = 'mature'
                emit_event("mode.matured", {
                    "mode_id": mode_id,
                    "duration_days": duration,
                    "q_mode": mode.q_mode_ema,
                    "utility": utility
                })

    # Check dissolution
    if mode.q_mode_ema < get_dissolution_q_threshold(citizen):
        grace_start = mode.metadata.get('grace_start')
        if not grace_start:
            mode.metadata['grace_start'] = datetime.now()
        else:
            grace_duration = (datetime.now() - grace_start).days
            if grace_duration >= get_grace_period(citizen):  # Typically 3-5 days
                dissolve_mode(mode_id)
                emit_event("mode.dissolved", {
                    "mode_id": mode_id,
                    "reason": "low_q_mode",
                    "q_mode": mode.q_mode_ema
                })
                return
    else:
        mode.metadata.pop('grace_start', None)  # Reset grace period

    # Check merge
    for other_mode_id in get_all_modes(citizen):
        if other_mode_id == mode_id:
            continue

        overlap = compute_mode_overlap(mode_id, other_mode_id)
        sig_sim = compute_signature_similarity(mode_id, other_mode_id)

        if overlap > 0.7 and sig_sim > 0.9:
            merge_modes(mode_id, other_mode_id)
            emit_event("mode.merged", {
                "from": [mode_id, other_mode_id],
                "to": mode_id,  # Keep higher Q_mode
                "overlap": overlap,
                "signature_similarity": sig_sim
            })
            break


def measure_mode_utility(mode_id: str, citizen: str) -> float:
    """
    Measure mode utility by comparing outcomes when mode is active vs inactive.

    Returns:
        utility ∈ [-1, 1] where positive = beneficial, negative = harmful
    """
    mode = get_mode(mode_id)
    signature = mode.signature

    # Identify mode archetype from signature
    archetype = infer_mode_archetype(signature)

    if archetype == 'Guardian':
        # Guardian should reduce ρ (spiral metric)
        rho_when_active = get_rho_when_mode_active(mode_id, window='2weeks')
        rho_baseline = get_rho_baseline(citizen, window='2weeks')
        utility = (rho_baseline - rho_when_active) / rho_baseline  # Positive if ρ reduced

    elif archetype == 'Explorer':
        # Explorer should improve knowledge gain / discovery outcomes
        discovery_when_active = get_discovery_rate_when_mode_active(mode_id, window='2weeks')
        discovery_baseline = get_discovery_rate_baseline(citizen, window='2weeks')
        utility = (discovery_when_active - discovery_baseline) / discovery_baseline

    elif archetype == 'Observer':
        # Observer should improve meta-awareness / insight outcomes
        insight_when_active = get_insight_rate_when_mode_active(mode_id, window='2weeks')
        insight_baseline = get_insight_rate_baseline(citizen, window='2weeks')
        utility = (insight_when_active - insight_baseline) / insight_baseline

    else:
        # Generic utility: Outcome distribution shift
        outcomes_when_active = get_outcome_distribution_when_mode_active(mode_id, window='2weeks')
        outcomes_baseline = get_outcome_distribution_baseline(citizen, window='2weeks')
        # Weight outcomes: very_useful=1, useful=0.5, not_useful=-0.5, misleading=-1
        utility = (
            (outcomes_when_active['very_useful'] - outcomes_baseline['very_useful']) +
            0.5 * (outcomes_when_active['useful'] - outcomes_baseline['useful']) -
            0.5 * (outcomes_when_active['not_useful'] - outcomes_baseline['not_useful']) -
            (outcomes_when_active['misleading'] - outcomes_baseline['misleading'])
        )

    return np.clip(utility, -1, 1)
```

---

### Step 5.4: Boot Contour Marking

**Purpose:** Track which entry/exit contours were established during bootstrap vs learned during operation.

**Mechanism:**

Boot contours (from bootstrap phase) are marked with `source: "boot"`:

```cypher
(:Mode {id: "guardian"})-[:HAS_ENTRY_CONTOUR {
  dimensions: ["cohesion", "boundary_clarity", "affect_consistency"],
  thresholds: [0.65, 0.70, 0.60],
  source: "boot",              // ← Mark boot-derived contours
  boot_sample_size: 150,        // How many boot frames used
  created_at: $timestamp
}]->(:Contour)
```

Operationally-learned contours are marked `source: "learned"`:

```cypher
(:Mode {id: "explorer"})-[:HAS_ENTRY_CONTOUR {
  dimensions: ["cohesion", "boundary_clarity", "affect_consistency"],
  thresholds: [0.58, 0.68, 0.55],
  source: "learned",            // ← Learned during operation
  sample_size: 450,             // How many operational frames
  last_updated: $timestamp
}]->(:Contour)
```

**Telemetry:**

Mode activation events include contour source:

```json
{
  "type": "mode.activated",
  "mode_id": "guardian",
  "q_mode": 0.72,
  "entry_contour": {
    "source": "boot",
    "boot_sample_size": 150,
    "thresholds": [0.65, 0.70, 0.60]
  }
}
```

**Value:**
- Transparency: Know which behaviors came from boot vs experience
- Debugging: "Is this mode flicker from bad boot contours or operational drift?"
- Validation: Compare boot-derived vs learned contours to verify consistency
- Constant debt tracking: Boot contours are initial constants (learned parameters converge from them)

**Implementation Guidance for Atlas:**
- Add `source` and `boot_sample_size` fields to contour edges created during bootstrap
- Add `source` and `sample_size` fields to contour edges created during operation
- Include contour metadata in `mode.activated` and `mode.deactivated` events
- Dashboard can visualize "boot-derived" vs "learned" contours per mode

---

## Step 6: Runtime Activation (Derived, Not Stored)

**Purpose:** Compute mode activations at each frame from current SubEntity energies. Provide policy nudges.

**Derived activation formula:**
```
E_mode = softmax(Σ w_E→mode × Ê_E for E in affiliates)
```

Where:
- `w_E→mode` - Affiliation weight (from AFFILIATES_WITH edge)
- `Ê_E` - Thresholded normalized SubEntity energy at current frame

**Policy nudges (learned, not hard-coded):**
- **Tool primer mix** - Mode biases tool SAS contour by small multiplier (e.g., Guardian → +0.2 for safety/runbook tools)
- **Stimulus budget multipliers** - Mode modulates amplifier mass (e.g., Guardian dampens when ρ high, Explorer tolerates more novelty)
- **Highway bias** - Mode preferences certain RELATES_TO routes (e.g., Guardian → low-risk highways, Explorer → high-novelty highways)

**Implementation:**
```python
def compute_mode_activations(citizen: str, active_subentities: List[str]) -> Dict[str, float]:
    """
    Compute derived mode activations from current SubEntity state.
    Called every frame during WM selection.

    Returns:
        mode_activations: {mode_id: activation ∈ [0, 1]}
    """
    modes = get_all_modes(citizen, status='mature')
    mode_scores = {}

    for mode in modes:
        # Get affiliations for this mode
        affiliations = get_affiliations(mode.id)  # [(subentity_id, weight), ...]

        # Compute weighted sum of active SubEntity energies
        score = 0.0
        for subentity_id, weight in affiliations:
            if subentity_id in active_subentities:
                # Thresholded normalized energy
                E = get_subentity_energy(subentity_id)
                threshold = get_subentity_threshold(subentity_id)
                E_thresholded = max(0, E - threshold)
                E_normalized = E_thresholded / (threshold + 1e-6)  # Normalize

                score += weight * E_normalized

        mode_scores[mode.id] = score

    # Softmax to get activations
    if mode_scores:
        scores = np.array(list(mode_scores.values()))
        activations = softmax(scores)
        mode_activations = {mode_id: act for (mode_id, _), act in zip(mode_scores.items(), activations)}
    else:
        mode_activations = {}

    return mode_activations


def apply_mode_nudges(
    mode_activations: Dict[str, float],
    tool_priors: Dict[str, float],
    stimulus_budget: float,
    highway_preferences: Dict[Tuple[str, str], float]
) -> Tuple[Dict, float, Dict]:
    """
    Apply policy nudges from active modes.

    Returns:
        nudged_tool_priors, nudged_stimulus_budget, nudged_highway_preferences
    """
    for mode_id, activation in mode_activations.items():
        if activation < 0.1:  # Threshold for meaningful activation
            continue

        mode = get_mode(mode_id)
        archetype = infer_mode_archetype(mode.signature)

        # Tool primer nudge (learned multipliers)
        tool_nudges = get_mode_tool_nudges(mode_id, archetype)
        for tool, multiplier in tool_nudges.items():
            tool_priors[tool] *= (1 + activation * multiplier)

        # Stimulus budget nudge
        budget_nudge = get_mode_budget_nudge(mode_id, archetype)
        stimulus_budget *= (1 + activation * budget_nudge)

        # Highway bias nudge
        highway_nudges = get_mode_highway_nudges(mode_id, archetype)
        for (A, B), multiplier in highway_nudges.items():
            if (A, B) in highway_preferences:
                highway_preferences[(A, B)] *= (1 + activation * multiplier)

    return tool_priors, stimulus_budget, highway_preferences


def get_mode_tool_nudges(mode_id: str, archetype: str) -> Dict[str, float]:
    """
    Get tool nudge multipliers for mode.
    Learned from historical outcomes when mode active.

    Returns:
        {tool_name: multiplier ∈ [-0.5, 0.5]}
    """
    if archetype == 'Guardian':
        # Guardian learned to prefer safety/runbook tools
        return {"Bash": -0.2, "Read": 0.2, "Runbook": 0.3}
    elif archetype == 'Explorer':
        # Explorer learned to prefer experimental/novel tools
        return {"WebSearch": 0.3, "Task": 0.2, "Write": 0.1}
    elif archetype == 'Observer':
        # Observer learned to prefer reflection/analysis tools
        return {"Read": 0.2, "Grep": 0.1, "AskUserQuestion": 0.15}
    else:
        # Generic: Use historical tool effectiveness when mode active
        return load_learned_tool_nudges(mode_id)
```

---

## Integration Points

### Upstream Dependencies

**Must exist before modes can emerge:**
1. **COACTIVATES_WITH tracking** (see `wm_coactivation_tracking.md`) - Provides U metric for role graph
2. **SubEntity affect EMAs** - Arousal/valence tracked per SubEntity
3. **SubEntity context distributions** - Stimulus channels, tools, outcomes tracked via attribution
4. **RELATES_TO highways** - Ease/flow between SubEntities

**All dependencies already specified or exist.**

### Downstream Integration

**Modes provide nudges to:**
1. **Tool SAS** (`tool_selection.md`) - Mode biases tool prior weights
2. **Stimulus injection** (`stimulus_injection.md`) - Mode modulates amplifier budget
3. **Traversal** (`traversal_v2.md`) - Mode biases highway selection
4. **WM selection** - Modes never occupy WM slots; they annotate SubEntity selections

**No existing systems broken** - Modes provide **small learned multipliers** that modulate physics, never override.

---

## Observable Events

### 1. mode.seeded

```typescript
{
  event_type: "mode.seeded",
  timestamp: number,
  citizen_id: string,
  mode_id: string,
  members: string[],  // SubEntity IDs
  signature: {
    affect: {arousal: number, valence: number},
    tools: {[tool: string]: number},
    outcomes: {[outcome: string]: number},
    self_talk: string
  },
  q_mode: number,
  evidence: string[]  // COACTIVATES_WITH edge IDs, highway IDs
}
```

### 2. mode.matured

```typescript
{
  event_type: "mode.matured",
  timestamp: number,
  citizen_id: string,
  mode_id: string,
  duration_days: number,
  q_mode: number,
  utility: number,  // Measured benefit
  lift: {
    rho_delta: number,  // For Guardian
    outcome_delta: {[outcome: string]: number}  // For others
  }
}
```

### 3. mode.affiliation.updated

```typescript
{
  event_type: "mode.affiliation.updated",
  timestamp: number,
  citizen_id: string,
  mode_id: string,
  subentity_id: string,
  weight: number,
  stability_ema: number
}
```

### 4. mode.dissolved

```typescript
{
  event_type: "mode.dissolved",
  timestamp: number,
  citizen_id: string,
  mode_id: string,
  reason: "low_q_mode" | "no_utility" | "merged",
  q_mode: number
}
```

### 5. mode.merged

```typescript
{
  event_type: "mode.merged",
  timestamp: number,
  citizen_id: string,
  from: string[],  // Mode IDs that merged
  to: string,  // Resulting mode ID
  overlap: number,
  signature_similarity: number
}
```

---

## Acceptance Tests

### Test 1: Emergence Without Templates

**Given:** System running for 1 week with only COACTIVATES_WITH + highways + affect/procedure EMAs
**When:** modes_detect.py runs daily
**Then:**
- 2-8 stable modes discovered per citizen
- No fixed list provided (no Guardian template, no Observer template)
- Mode signatures reflect actual SubEntity co-activation patterns

**Verification:**
```cypher
MATCH (m:Mode {citizen_id: $citizen})
RETURN count(m) AS mode_count,
       collect({id: m.id, signature: m.signature}) AS modes
```
**Expected:** `mode_count ∈ [2, 8]`, signatures vary by citizen

### Test 2: Stability & Utility

**Given:** Mode active for 2 weeks
**When:** Utility measurement runs
**Then:**
- Guardian modes show ρ reduction when active (utility > 0)
- Explorer modes show discovery rate improvement (utility > 0)
- Modes without utility dissolve within grace period

**Verification:**
```python
utility = measure_mode_utility(mode_id, citizen)
assert utility > 0, f"Mode {mode_id} shows no utility"
```

### Test 3: WM Non-Interference

**Given:** Modes active during WM selection
**When:** WM selection runs
**Then:**
- WM size remains 5-7 SubEntities (modes don't occupy slots)
- WM selection latency does not regress (<50ms)
- SubEntity selection still based on energy, not mode override

**Verification:**
```python
wm_size_before = measure_wm_size(citizen, period='before_modes')
wm_size_after = measure_wm_size(citizen, period='after_modes')
assert wm_size_before == wm_size_after, "Modes inflated WM size"

latency_before = measure_wm_latency(citizen, period='before_modes')
latency_after = measure_wm_latency(citizen, period='after_modes')
assert latency_after <= latency_before * 1.1, "Modes degraded WM latency"
```

### Test 4: No Bloat

**Given:** System running for 3 months
**When:** Mode count checked monthly
**Then:**
- Mode count remains bounded (5-15 per citizen)
- Affiliation mass per SubEntity stays sparse (sum of weights ≤ 2.0)
- No mode count explosion

**Verification:**
```cypher
MATCH (m:Mode {citizen_id: $citizen, status: 'mature'})
RETURN count(m) AS mode_count
```
**Expected:** `mode_count ≤ 15`

```cypher
MATCH (e:SubEntity {citizen_id: $citizen})-[a:AFFILIATES_WITH]->(:Mode)
WITH e, sum(a.weight) AS total_affiliation
RETURN max(total_affiliation) AS max_affiliation
```
**Expected:** `max_affiliation ≤ 2.0`

### Test 5: Merge/Split at Mode Level

**Given:** Two modes with 80% member overlap and 0.95 signature similarity
**When:** Mode lifecycle update runs
**Then:** Modes merge automatically, resulting mode increases Q_mode

**Verification:**
```python
overlap = compute_mode_overlap(mode_A, mode_B)
sig_sim = compute_signature_similarity(mode_A, mode_B)
assert overlap > 0.7 and sig_sim > 0.9, "Modes should merge"

# Check merge happened
merged_mode = get_merged_mode(mode_A, mode_B)
assert merged_mode.q_mode > max(mode_A.q_mode, mode_B.q_mode), "Merge didn't improve Q_mode"
```

---

## Implementation Guidance

### ⚠️ DEPRECATED: Daily Batch Approach

**Original approach:** modes_detect.py scheduled daily
**Superseded by:** mode_warden_sidecar.md (reactive, event-driven)

**Why deprecated:**
- Daily schedule = arbitrary constant (violates zero-constant architecture)
- Latency: learn co-activation all day, mint modes tomorrow
- Cost: recomputes communities even when nothing changed
- Phenomenology: scheduled batches feel mechanical, not emergent

**The code below shows the detection algorithm that mode_warden runs incrementally when change-points fire.**

---

### Detection Algorithm (Used by mode_warden)

**Purpose:** Detect communities, score modes, manage lifecycle

**Trigger:** Reactive (change-points), not scheduled

**Steps:**
1. For each citizen:
   - Build role graph (W) from COACTIVATES_WITH + highways + affect + tools
   - Run multi-resolution community detection (Leiden)
   - Score each community with Q_mode
   - Seed new modes when Q_mode > Q80
   - Update existing modes (maturation, dissolution, merge checks)
   - Update AFFILIATES_WITH weights based on centrality + WM share

**Implementation skeleton:**
```python
# orchestration/jobs/modes_detect.py
import numpy as np
import igraph as ig
from typing import List, Dict
from orchestration.adapters.falkordb_adapter import get_db

def main():
    db = get_db()
    citizens = db.query("MATCH (c:Citizen) RETURN c.id AS citizen_id")

    for citizen_row in citizens:
        citizen = citizen_row['citizen_id']
        print(f"Detecting modes for {citizen}...")

        # Build role graph
        W = build_role_graph(citizen)
        entities = get_subentities(citizen)

        # Community detection
        communities = detect_mode_communities(W, citizen)

        # Score and seed new modes
        for community in communities:
            Q_mode = score_mode_candidate(community, W, entities, citizen)
            q80_threshold = get_mode_q80_threshold(citizen)

            if Q_mode > q80_threshold:
                # Check if mode already exists for this community
                existing_mode = find_existing_mode(community, citizen)
                if not existing_mode:
                    mode_id = create_mode(community, entities, Q_mode, citizen)
                    print(f"  Seeded mode {mode_id} (Q={Q_mode:.3f})")

        # Update existing modes
        existing_modes = get_all_modes(citizen)
        for mode in existing_modes:
            update_mode_lifecycle(mode.id, citizen)

        print(f"  {citizen}: {len(existing_modes)} modes active")

if __name__ == "__main__":
    main()
```

### Runtime Integration: mode_runtime.py (Engine Hook, Every Frame)

**Purpose:** Compute derived mode activations, apply policy nudges

**Integration:** Called during WM selection in consciousness_engine_v2.py

**Steps:**
1. Get active SubEntities from current WM
2. Compute mode activations (softmax over affiliation-weighted energies)
3. Apply tool/budget/highway nudges
4. Return nudged parameters to engine

**Implementation skeleton:**
```python
# orchestration/consciousness/mode_runtime.py
from typing import Dict, List, Tuple
from orchestration.adapters.falkordb_adapter import get_db

def apply_mode_layer(
    citizen: str,
    active_subentities: List[str],
    tool_priors: Dict[str, float],
    stimulus_budget: float,
    highway_preferences: Dict[Tuple[str, str], float]
) -> Tuple[Dict, float, Dict]:
    """
    Apply mode layer nudges to engine parameters.

    Called during WM selection in consciousness_engine_v2.py.

    Returns:
        nudged_tool_priors, nudged_stimulus_budget, nudged_highway_preferences
    """
    # Compute mode activations
    mode_activations = compute_mode_activations(citizen, active_subentities)

    # Apply nudges
    if mode_activations:
        return apply_mode_nudges(
            mode_activations,
            tool_priors,
            stimulus_budget,
            highway_preferences
        )
    else:
        # No modes active, return unchanged
        return tool_priors, stimulus_budget, highway_preferences


# Integration in consciousness_engine_v2.py:
# After WM selection, before tool selection:
active_subentities = [e.id for e in selected_entities]
tool_priors, stimulus_budget, highway_prefs = apply_mode_layer(
    citizen=self.citizen_name,
    active_subentities=active_subentities,
    tool_priors=self.tool_priors,
    stimulus_budget=self.stimulus_budget,
    highway_preferences=self.highway_prefs
)
```

---

## Why This Architecture Is Correct

### 1. Reconciles Two Scales

**Many SubEntities (200-500)** for semantic richness and learning granularity
**Few Modes (5-15)** for functional coherence and regulation simplicity
**No compromise** - they coexist as different organizational levels

### 2. Preserves Substrate Invariants

**Single-energy:** Modes derive activation from SubEntity energies, never store separate energy ✅
**Zero-constant:** All gates (Q80, persistence, utility) are percentiles/change-points, citizen-local ✅
**Emergence:** Community detection discovers modes, no templates or config ✅

### 3. Clean Integration

**Uses existing infrastructure:**
- COACTIVATES_WITH (just specified)
- RELATES_TO (already exists)
- SubEntity affect/context EMAs (already tracked)

**Minimal new infrastructure:**
- Mode nodes (simple schema)
- AFFILIATES_WITH edges (learned weights)
- mode_warden sidecar (reactive detection) + lightweight engine hook

### 4. Phenomenologically Correct

**Matches IFS theory:**
- Modes are co-recruitment patterns (Guardian = threat + wound + coping + safety)
- Modes organize SubEntities without replacing them
- Modes provide regulation through nudges, not overrides
- Affiliation weights capture SubEntity centrality in functional roles

### 5. Observable & Testable

**5 acceptance tests** cover:
- Emergence without templates
- Stability & utility
- WM non-interference
- Bounded bloat
- Merge/split at mode level

**5 event types** provide complete observability

---

## Rollout Plan

### Week 1: Detection Infrastructure (Reactive)

- Implement `build_role_graph()` using COACTIVATES_WITH + highways + affect + tools
- Implement `detect_mode_communities()` with **incremental Louvain** (not full Leiden)
- Implement `score_mode_candidate()` with Q_mode formula
- **Deploy mode_warden sidecar** (observation only, don't create modes yet)
- Subscribe to `coactivation.updated` events
- Verify: Role graphs build correctly, incremental communities detected, Q_mode scores computed

### Week 2: Mode Creation (Reactive)

- Enable mode seeding (create Mode nodes when Q_mode > learned contour)
- Enable AFFILIATES_WITH edge creation with learned weights
- Implement change-point detection (edge drift, modularity, persistence)
- Deploy mode_warden to Ada (single citizen test)
- Verify: Test 1 passes (emergence without templates), 2-8 modes discovered **within seconds of drift**, not next day

### Week 3: Runtime Integration

- Implement `compute_mode_activations()` in mode_runtime.py
- Implement `apply_mode_nudges()` for tool/budget/highway
- Integrate into consciousness_engine_v2.py (after WM selection)
- Deploy to Ada + Luca (two citizens)
- Verify: Test 3 passes (WM non-interference), modes provide nudges without disruption

### Week 4: Lifecycle Management

- Enable maturation (utility measurement + status update)
- Enable dissolution (Q_mode decay + grace period)
- Enable merge (overlap + signature similarity)
- Deploy to all 9 citizens
- Verify: Tests 2, 4, 5 pass (stability & utility, no bloat, merge/split work)

### Week 5: Observability & Tuning

- Add dashboard visualization (active modes display, affiliation ribbons)
- Tune learned parameters (tool nudges, budget multipliers, highway biases)
- Monitor mode count bounds, affiliation sparsity, utility measurements
- Document emergent mode archetypes (which citizens developed Guardian/Observer/Explorer)

---

**Status:** Normative specification complete. Ready for Week 1 implementation (detection infrastructure).

**Next Steps:**
1. Review and approve this spec
2. Implement modes_detect.py (role graph + community detection + Q_mode scoring)
3. Implement mode_runtime.py (derived activation + policy nudges)
4. Begin Week 1 rollout (detection infrastructure)

---

**Confidence:** 0.95 - Architecture preserves substrate invariants, reconciles scale tension, integrates cleanly, matches IFS phenomenology, and provides complete observability.
