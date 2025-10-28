---
title: "Forged Identity" - Implementation Guide (Context vs Input Selection)
status: implementation-ready
owner: @ada
created: 2025-10-25
corrected: 2025-10-25 21:00
purpose: >
  Implementation guide for context entity selection (system prompt) vs input entity selection (user message).
  Integrates Nicolas's zero-constant selection formulas with Luca's refinements (medoid, divisor apportionment, formation quality, TRACE integration).

  CORRECTION NOTE: This replaces forged_identity_IMPLEMENTATION_ADDENDUM.md which incorrectly separated
  "identity vs workspace" entities. The correct architecture is "context vs input" entities - both use
  weight AND energy, just with different emphasis.
---

# Forged Identity - Implementation Guide

**Context:** Implementation details for forged_identity.md's context/input entity selection system.

**Key Architectural Correction:**
- NOT "identity entities" (weight-only) vs "workspace entities" (energy-only)
- YES "context entities" (structural × relevance) vs "input entities" (energy × competence)
- Both use weight AND energy - different emphasis, same substrate

---

## Section 1: Core Architecture

### 1.1 The Two Selection Functions

**Context Entities** (system prompt / claude.md):
- **Purpose:** Structurally stable patterns that are currently relevant
- **Selection:** High weight, low volatility, high formation quality, AND non-zero energy/attribution
- **Scoring:** Structure-dominant with relevance bump
- **Typical size:** 5-8 entities (broader, identity-aware)
- **Allocation:** Divisor apportionment (smooth changes)
- **Goes to:** LLM system role

**Input Entities** (user message / inputReconciled):
- **Purpose:** Immediately active patterns with competence prior
- **Selection:** WM-selected or stimulus-attributed
- **Scoring:** Energy-dominant with light structural prior
- **Typical size:** 1-3 entities (narrow, immediate)
- **Allocation:** Hamilton apportionment (burst-aware)
- **Goes to:** LLM user role

### 1.2 Where They Integrate

**Location:** `orchestration/mechanisms/consciousness_engine_v2.py`

**Existing infrastructure:** `_select_workspace_entities()` at line ~1647 handles working memory selection

**New functions needed:**
- `_select_context_entities()` - context selection with Nicolas's formula
- `_select_input_entities()` - input selection with Nicolas's formula
- `_generate_system_prompt()` - context → system prompt
- `_generate_input_context()` - input → user message (may already exist)

---

## Section 2: Data Structures

### 2.1 Required Subentity Fields

**Current state:** `orchestration/core/subentity.py` already has most fields needed:

```python
@dataclass
class Subentity:
    # EXISTING fields we'll use:
    log_weight: float = 0.0  # Aggregate weight (w_e)
    energy_runtime: float = 0.0  # Current energy (ε_e)
    coherence_ema: float = 0.0  # Will be replaced by formation_quality
    centroid_embedding: Optional[np.ndarray] = None  # For essence extraction
    stability_state: str = "candidate"  # Lifecycle state
```

**NEW fields needed:**

```python
@dataclass
class Subentity:
    # ... existing fields ...

    # === Forged Identity Extensions ===

    # Formation quality (from TRACE C×E×N)
    formation_quality: float = 0.0  # q_e - TRACE geometric mean (Completeness × Evidence × Novelty)
    ema_formation_quality: float = 0.0  # EMA of formation quality over time

    # Stability metrics
    membership_snapshots: deque = field(default_factory=lambda: deque(maxlen=30))  # σ_e computation
    weight_volatility: float = 0.0  # ν_e - coefficient of variation
    stability_score: float = 0.0  # σ_e - Jaccard similarity over snapshots

    # Attribution tracking (for input selection)
    stimulus_attribution: float = 0.0  # a_e - how much current stimulus points here

    # Novelty tracking (for input selection)
    energy_history: deque = field(default_factory=lambda: deque(maxlen=100))  # For z^nov computation
    novelty_z_score: float = 0.0  # z_e^nov - current energy vs history

    # Learned contours (citizen-local, subdomain-specific)
    cohort_id: str = ""  # "{citizen_id}_{subdomain}_{time_window}"
    learned_stability_threshold: float = 0.70  # θ_σ(e) - learned percentile
    learned_quality_threshold: float = 0.75  # θ_q(e) - learned percentile
    learned_volatility_threshold: float = 0.30  # θ_ν(e) - learned percentile

    # Lambda for input selection (learned)
    learned_structural_prior_lambda: float = 0.1  # λ - how much weight influences input selection

    # Timestamps
    last_snapshot_time: Optional[datetime] = None
    last_contour_update: Optional[datetime] = None
```

**Storage:** All fields serialize to FalkorDB as Subentity node properties.

---

## Section 3: Context Entity Selection

### 3.1 Selection Algorithm

**Function:** `_select_context_entities()`

**Nicolas's Formula:**

```
Candidate set C = {e | σ_e > θ_σ(e) AND q_e > θ_q(e) AND ν_e < θ_ν(e) AND (ε_e > 0 OR a_e > 0)}

Score S^ctx_e = [w̃_e · q̃_e · σ̃_e · (1 - ν̃_e)] × max(1, ε̃_e + ã_e)
                 └──────structural axis──────┘     └─relevance bump─┘
```

**Implementation:**

```python
def _select_context_entities(self) -> List[Subentity]:
    """
    Select context entities for system prompt (stable + currently relevant).

    Uses Nicolas's zero-constant selection formula with learned thresholds.
    Integrates Luca's refinements: formation quality (TRACE C×E×N),
    citizen-local cohorts, divisor apportionment.

    Returns:
        List of context entities sorted by context score descending
    """
    if not hasattr(self.graph, 'subentities') or not self.graph.subentities:
        return []

    # Update learned contours if needed (weekly)
    self._update_learned_contours_if_needed()

    # Phase 1: Filter candidate set
    candidates = []

    for entity in self.graph.subentities.values():
        # Compute/refresh metrics
        σ_e = self._compute_stability(entity)  # Jaccard similarity over snapshots
        q_e = entity.formation_quality  # TRACE C×E×N (Luca's refinement)
        ν_e = self._compute_weight_volatility(entity)  # Coefficient of variation
        ε_e = entity.energy_runtime  # Current energy
        a_e = entity.stimulus_attribution  # Attribution from stimulus injection

        # Update entity state
        entity.stability_score = σ_e
        entity.weight_volatility = ν_e

        # Filter against learned thresholds (zero-constant principle)
        if (σ_e > entity.learned_stability_threshold and
            q_e > entity.learned_quality_threshold and
            ν_e < entity.learned_volatility_threshold and
            (ε_e > 0 or a_e > 0)):  # Currently relevant

            candidates.append(entity)

    if not candidates:
        return []

    # Phase 2: Score candidates
    scored_candidates = []

    for entity in candidates:
        # Cohort-normalize features (z-scores → positive via softplus)
        w̃_e = self._cohort_normalize(entity.log_weight, 'weight', entity.cohort_id)
        q̃_e = self._cohort_normalize(entity.formation_quality, 'quality', entity.cohort_id)
        σ̃_e = self._cohort_normalize(entity.stability_score, 'stability', entity.cohort_id)
        ν̃_e = self._cohort_normalize(entity.weight_volatility, 'volatility', entity.cohort_id)
        ε̃_e = self._cohort_normalize(entity.energy_runtime, 'energy', entity.cohort_id)
        ã_e = self._cohort_normalize(entity.stimulus_attribution, 'attribution', entity.cohort_id)

        # Structural axis (durable patterns that have proven useful)
        structural = w̃_e * q̃_e * σ̃_e * (1 - ν̃_e)

        # Relevance bump (ensures stable patterns never zero out, but current state amplifies)
        relevance = max(1.0, ε̃_e + ã_e)

        # Combined context score
        context_score = structural * relevance

        scored_candidates.append((entity, context_score))

    # Sort by context score descending
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    # Return entities only (scores not needed downstream)
    return [entity for entity, score in scored_candidates]


def _cohort_normalize(self, value: float, feature_name: str, cohort_id: str) -> float:
    """
    Normalize feature value within citizen-local subdomain cohort.

    Args:
        value: Raw feature value
        feature_name: Which feature (for cohort stats lookup)
        cohort_id: "{citizen}_{subdomain}_{time_window}"

    Returns:
        Normalized value (z-score → positive via softplus)
    """
    # Get cohort statistics (from cohort registry)
    cohort_stats = self._get_cohort_stats(cohort_id, feature_name)

    if cohort_stats is None:
        return value  # Fallback: no normalization if cohort too small

    # Compute z-score
    z = (value - cohort_stats['mean']) / (cohort_stats['std'] + 1e-9)

    # Convert to positive via softplus: ln(1 + e^z)
    import numpy as np
    normalized = np.log(1 + np.exp(z))

    return normalized


def _compute_stability(self, entity: Subentity) -> float:
    """
    Compute membership stability (σ_e) via Jaccard similarity over snapshots.

    From forged_identity.md Section 5.1 (Luca's spec).

    Returns:
        Stability score [0, 1] - higher means less membership drift
    """
    snapshots = entity.membership_snapshots

    if len(snapshots) < 2:
        return 0.0  # Insufficient history

    # Compare consecutive snapshots
    similarities = []
    for i in range(len(snapshots) - 1):
        current = set(snapshots[i].member_ids)
        next_snap = set(snapshots[i + 1].member_ids)

        intersection = len(current & next_snap)
        union = len(current | next_snap)

        jaccard = intersection / union if union > 0 else 0.0
        similarities.append(jaccard)

    # Average Jaccard = stability
    return np.mean(similarities) if similarities else 0.0


def _compute_weight_volatility(self, entity: Subentity) -> float:
    """
    Compute weight volatility (ν_e) via coefficient of variation.

    From forged_identity.md Section 5.1 lines 672-689 (Luca's spec).

    Returns:
        Volatility [0, inf] - lower means more stable structure
    """
    if len(entity.weight_history) < 5:
        return 1.0  # High volatility (insufficient data)

    weights = list(entity.weight_history)

    # Coefficient of variation: std / mean
    mean = np.mean(weights)
    std = np.std(weights)

    return std / (mean + 1e-9)
```

### 3.2 System Prompt Generation

**Function:** `_generate_system_prompt()`

**Uses divisor apportionment (Luca's refinement):**

```python
def _generate_system_prompt(self, context_entities: List[Subentity], total_budget: int = 1200) -> str:
    """
    Generate system prompt from context entities.

    Uses divisor apportionment (Sainte-Laguë) for smooth token allocation.
    Integrates Luca's refinements: medoid fallback, formation quality weighting.

    Args:
        context_entities: Output from _select_context_entities()
        total_budget: Token budget for system prompt

    Returns:
        Generated system prompt (identity-aware context)
    """
    if not context_entities:
        # Bootstrap case: no stable entities yet
        return self._generate_bootstrap_identity()

    # Weight entities by (aggregate_weight × formation_quality)
    # This unifies "what gets reinforced" with "what becomes identity" (Luca's TRACE integration)
    weights = {
        entity: entity.log_weight * entity.formation_quality
        for entity in context_entities
    }

    # Divisor apportionment for smooth allocation (Luca's refinement)
    allocations = self._divisor_apportionment(
        weights,
        total_budget,
        method='sainte_lague'  # Smooth changes as weights shift
    )

    # Express each entity
    sections = []
    for entity in context_entities:
        if entity not in allocations or allocations[entity] < 50:
            continue  # Skip if insufficient budget

        section = self._express_context_entity(entity, allocations[entity])
        sections.append(section)

    # Natural separation
    return "\n\n---\n\n".join(sections)


def _express_context_entity(self, entity: Subentity, token_allocation: int) -> str:
    """
    Express one context entity as system prompt section.

    Uses extractive essence (centroid → nearest or medoid) per Luca's refinement.

    Args:
        entity: Context entity to express
        token_allocation: Tokens allocated to this entity

    Returns:
        Section text (essence + supporting structure)
    """
    # Extract essence (Luca's medoid fallback)
    essence = self._extract_entity_essence(entity)

    essence_tokens = len(essence) // 4 + 1
    remaining_tokens = token_allocation - essence_tokens

    if remaining_tokens < 50:
        return essence  # Just essence if tight budget

    # Get high-weight supporting members
    members = entity.get_members()
    members_sorted = sorted(members, key=lambda n: n.log_weight, reverse=True)[:10]

    # Fill remaining budget
    supporting_content = []
    current_tokens = 0

    for node in members_sorted:
        if not hasattr(node, 'content') or node.content == essence:
            continue

        node_tokens = len(node.content) // 4 + 1

        if current_tokens + node_tokens <= remaining_tokens:
            supporting_content.append(node.content)
            current_tokens += node_tokens
        else:
            break

    # Natural formatting
    if supporting_content:
        return essence + "\n" + "\n".join(supporting_content)
    else:
        return essence
```

---

## Section 4: Input Entity Selection

### 4.1 Selection Algorithm

**Function:** `_select_input_entities()`

**Nicolas's Formula:**

```
Candidate set I = {e | e ∈ WM.selected OR a_e > 0}

Score S^inp_e = ε̃_e · (1 + ã_e) · (1 + max(0, z̃_e^nov)) · (1 + λ·w̃_e)
                └─now─┘  └tied to stimulus┘  └─novelty─┘  └─competence─┘

K ∈ {1,2,3} adaptive from energy concentration
```

**Implementation:**

```python
def _select_input_entities(self) -> List[Subentity]:
    """
    Select input entities for user message (immediate + competent).

    Uses Nicolas's energy-dominant formula with light structural prior.
    Adaptive pick count (K) from energy concentration.

    Returns:
        List of 1-3 input entities sorted by input score descending
    """
    if not hasattr(self.graph, 'subentities') or not self.graph.subentities:
        return []

    # Phase 1: Candidate set (WM-selected OR stimulus-attributed)
    candidates = []

    # Get WM-selected entities (from existing working memory selection)
    wm_selected = set(self.graph.working_memory.entities) if hasattr(self.graph, 'working_memory') else set()

    for entity in self.graph.subentities.values():
        if entity in wm_selected or entity.stimulus_attribution > 0:
            candidates.append(entity)

    if not candidates:
        return []

    # Phase 2: Score candidates
    scored_candidates = []

    for entity in candidates:
        # Compute novelty z-score
        z_nov = self._compute_novelty_z_score(entity)
        entity.novelty_z_score = z_nov

        # Cohort-normalize features
        ε̃_e = self._cohort_normalize(entity.energy_runtime, 'energy', entity.cohort_id)
        ã_e = self._cohort_normalize(entity.stimulus_attribution, 'attribution', entity.cohort_id)
        z̃_nov = self._cohort_normalize(z_nov, 'novelty', entity.cohort_id)
        w̃_e = self._cohort_normalize(entity.log_weight, 'weight', entity.cohort_id)

        # Input score formula
        λ = entity.learned_structural_prior_lambda  # Learned parameter

        input_score = (
            ε̃_e *  # Energy (now)
            (1 + ã_e) *  # Tied to stimulus
            (1 + max(0, z̃_nov)) *  # Novelty (unexpected activation)
            (1 + λ * w̃_e)  # Small structural prior (competence)
        )

        scored_candidates.append((entity, input_score))

    # Sort by input score descending
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    # Phase 3: Adaptive K selection
    scores = [score for entity, score in scored_candidates]
    K = self._compute_adaptive_K(scores)

    # Return top K entities
    return [entity for entity, score in scored_candidates[:K]]


def _compute_novelty_z_score(self, entity: Subentity) -> float:
    """
    Compute novelty z-score (z_e^nov): current energy vs entity's own history.

    From forged_identity.md Section 5.2 (Luca's spec).

    Returns:
        Z-score [-3, 3] clipped - how unexpected is current activation
    """
    energy_history = entity.energy_history
    current_energy = entity.energy_runtime

    if len(energy_history) < 10:
        return 0.0  # Neutral (insufficient history)

    mean_energy = np.mean(energy_history)
    std_energy = np.std(energy_history)

    if std_energy < 1e-9:
        return 0.0

    # Z-score
    z = (current_energy - mean_energy) / std_energy

    # Clip to [-3, 3]
    return np.clip(z, -3, 3)


def _compute_adaptive_K(self, scores: List[float]) -> int:
    """
    Compute adaptive pick count from energy concentration.

    Uses Herfindahl index (concentration measure):
    - High concentration (one dominant entity) → K = 1
    - Medium concentration → K = 2
    - Low concentration (split mass) → K = 3

    Args:
        scores: Input scores for all candidates

    Returns:
        K ∈ {1, 2, 3}
    """
    if not scores:
        return 1

    # Normalize scores to probabilities
    total = sum(scores)
    if total == 0:
        return 1

    probs = [score / total for score in scores]

    # Herfindahl index: sum of squared probabilities
    H = sum(p**2 for p in probs)

    # Thresholds for K selection
    if H > 0.6:
        return 1  # One entity dominates
    elif H > 0.35:
        return 2  # Medium concentration
    else:
        return 3  # Split mass


def _generate_input_context(self, input_entities: List[Subentity], total_budget: int = 800) -> str:
    """
    Generate user message from input entities.

    Uses Hamilton apportionment (hard cap, burst-aware).

    Args:
        input_entities: Output from _select_input_entities() (1-3 entities)
        total_budget: Token budget for user message

    Returns:
        Generated input context (immediate state)
    """
    if not input_entities:
        return "[No active entities]"

    # Weight by input score (energy-dominant)
    weights = {
        entity: entity.energy_runtime * (1 + entity.stimulus_attribution)
        for entity in input_entities
    }

    # Hamilton apportionment (largest remainder method)
    allocations = self._hamilton_apportionment(weights, total_budget)

    # Express each entity
    sections = []
    for entity in input_entities:
        if entity not in allocations or allocations[entity] < 30:
            continue

        section = self._express_input_entity(entity, allocations[entity])
        sections.append(section)

    return "\n\n".join(sections)


def _express_input_entity(self, entity: Subentity, token_allocation: int) -> str:
    """
    Express one input entity as user message section.

    Format: essence + active members by energy/recency + optional boundary link

    Args:
        entity: Input entity to express
        token_allocation: Tokens allocated to this entity

    Returns:
        Section text (action-oriented, immediate)
    """
    # Extract essence
    essence = self._extract_entity_essence(entity)

    essence_tokens = len(essence) // 4 + 1
    remaining_tokens = token_allocation - essence_tokens

    if remaining_tokens < 30:
        return essence

    # Get active members (high energy, recent)
    members = entity.get_members()
    active_members = [
        node for node in members
        if hasattr(node, 'energy_runtime') and node.energy_runtime > 0.1
    ]
    active_members_sorted = sorted(
        active_members,
        key=lambda n: (n.energy_runtime, getattr(n, 'last_activation', 0)),
        reverse=True
    )[:5]

    # Fill budget with active evidence
    active_content = []
    current_tokens = 0

    for node in active_members_sorted:
        if not hasattr(node, 'content') or node.content == essence:
            continue

        node_tokens = len(node.content) // 4 + 1

        if current_tokens + node_tokens <= remaining_tokens:
            active_content.append(node.content)
            current_tokens += node_tokens
        else:
            break

    # Optionally add highest explanatory boundary link (why this entity now?)
    # TODO: Implement boundary link selection if needed

    if active_content:
        return essence + "\n" + "\n".join(active_content)
    else:
        return essence
```

---

## Section 5: Essence Extraction (Luca's Medoid Refinement)

```python
def _extract_entity_essence(self, entity: Subentity) -> str:
    """
    Find most representative content for this subentity.

    Integrates Luca's medoid fallback refinement (Section 4.3 lines 286-291):
    - Default: centroid → nearest member (fast, tight clusters)
    - Fallback: medoid when nearest_distance > 0.7 (robust for multi-modal entities)

    Returns:
        Essence text (extractive, no LLM generation)
    """
    if entity.centroid_embedding is None:
        # No centroid - fallback to highest-weight member
        members = entity.get_members()
        if not members:
            return entity.role_or_topic or entity.description or "[Empty entity]"

        highest_weight = max(members, key=lambda n: n.log_weight)
        return getattr(highest_weight, 'content', '')

    # Find members with embeddings
    members_with_embeddings = [
        (node, node.embedding)
        for node in entity.get_members()
        if hasattr(node, 'embedding') and node.embedding is not None
    ]

    if not members_with_embeddings:
        members = entity.get_members()
        if members:
            return getattr(members[0], 'content', '')
        return entity.role_or_topic or "[No members]"

    # Compute distances to centroid
    members_by_distance = []
    for node, embedding in members_with_embeddings:
        distance = np.linalg.norm(entity.centroid_embedding - embedding)
        members_by_distance.append((node, distance))

    # Sort by distance (ascending)
    members_by_distance.sort(key=lambda x: x[1])

    # Check nearest member distance
    nearest_node, nearest_distance = members_by_distance[0]

    # Luca's medoid fallback: if centroid far from all members, use medoid
    if nearest_distance > 0.7:
        # Multi-modal or high-spread entity - medoid is more robust
        medoid_node = self._compute_medoid(entity.get_members())
        return getattr(medoid_node, 'content', '')

    # Default: nearest member to centroid
    return getattr(nearest_node, 'content', '')


def _compute_medoid(self, members: List['Node']) -> 'Node':
    """
    Find member that minimizes total distance to all other members.

    From forged_identity.md Section 4.3 lines 297-316 (Luca's refinement).
    More robust than centroid for multi-modal distributions.
    O(N²) but only used when entity shows high spread.

    Args:
        members: List of member nodes with embeddings

    Returns:
        Medoid node (most central member)
    """
    members_with_embeddings = [
        node for node in members
        if hasattr(node, 'embedding') and node.embedding is not None
    ]

    if not members_with_embeddings:
        # Fallback: return first member
        return members[0] if members else None

    if len(members_with_embeddings) == 1:
        return members_with_embeddings[0]

    # Compute pairwise distances
    min_total_distance = float('inf')
    medoid = members_with_embeddings[0]

    for candidate in members_with_embeddings:
        total_distance = 0.0

        for other in members_with_embeddings:
            if candidate == other:
                continue

            distance = np.linalg.norm(candidate.embedding - other.embedding)
            total_distance += distance

        if total_distance < min_total_distance:
            min_total_distance = total_distance
            medoid = candidate

    return medoid
```

---

## Section 6: Apportionment Methods

### 6.1 Divisor Apportionment (Context - Smooth)

```python
def _divisor_apportionment(
    self,
    weights: Dict[Subentity, float],
    total_budget: int,
    method: str = 'sainte_lague'
) -> Dict[Subentity, int]:
    """
    Distribute token budget using divisor apportionment.

    From forged_identity.md Section 4.6 (Luca's refinement).
    Prevents jump discontinuities when weights shift slightly.

    Args:
        weights: Entity → weight mapping
        total_budget: Total tokens to allocate
        method: 'sainte_lague' or 'huntington_hill'

    Returns:
        Entity → token allocation mapping
    """
    if not weights:
        return {}

    # Initialize allocations
    allocations = {entity: 0 for entity in weights}

    # Divisor method: iteratively assign tokens to entity with highest priority
    for _ in range(total_budget):
        # Compute priorities based on method
        priorities = {}

        for entity, weight in weights.items():
            current_allocation = allocations[entity]

            if method == 'sainte_lague':
                # Divisor: 2n + 1
                divisor = 2 * current_allocation + 1
            elif method == 'huntington_hill':
                # Divisor: sqrt(n(n+1))
                divisor = np.sqrt(current_allocation * (current_allocation + 1)) if current_allocation > 0 else 1.0
            else:
                raise ValueError(f"Unknown method: {method}")

            priorities[entity] = weight / divisor if divisor > 0 else weight

        # Assign one token to entity with highest priority
        max_entity = max(priorities, key=priorities.get)
        allocations[max_entity] += 1

    return allocations
```

### 6.2 Hamilton Apportionment (Input - Burst-Aware)

```python
def _hamilton_apportionment(
    self,
    weights: Dict[Subentity, float],
    total_budget: int
) -> Dict[Subentity, int]:
    """
    Distribute token budget using Hamilton method (largest remainder).

    From forged_identity.md Section 4.6.
    Used for input entities (ephemeral can tolerate small jitter).

    Args:
        weights: Entity → weight mapping
        total_budget: Total tokens to allocate

    Returns:
        Entity → token allocation mapping
    """
    if not weights:
        return {}

    total_weight = sum(weights.values())

    if total_weight == 0:
        # Equal distribution
        per_entity = total_budget // len(weights)
        return {entity: per_entity for entity in weights}

    # Compute quotas (proportional shares)
    quotas = {
        entity: (weight / total_weight) * total_budget
        for entity, weight in weights.items()
    }

    # Integer parts
    allocations = {entity: int(quota) for entity, quota in quotas.items()}

    # Remainders
    remainders = {
        entity: quotas[entity] - allocations[entity]
        for entity in quotas
    }

    # Distribute remaining tokens to largest remainders
    remaining = total_budget - sum(allocations.values())

    for entity in sorted(remainders, key=remainders.get, reverse=True)[:remaining]:
        allocations[entity] += 1

    return allocations
```

---

## Section 7: Learned Contour Updates

```python
def _update_learned_contours_if_needed(self):
    """
    Update learned thresholds weekly (adaptive, not fixed).

    From forged_identity.md Section 4.5 (Luca's citizen-local cohorts).
    Computes percentile thresholds from {citizen}_{subdomain}_{time_window} cohorts.
    """
    # Check if update needed (weekly)
    if (self.last_contour_update and
        (datetime.now() - self.last_contour_update).days < 7):
        return

    # Group entities by cohort
    cohorts = {}
    for entity in self.graph.subentities.values():
        cohort_id = entity.cohort_id
        if cohort_id not in cohorts:
            cohorts[cohort_id] = []
        cohorts[cohort_id].append(entity)

    # Update thresholds for each cohort
    for cohort_id, cohort_entities in cohorts.items():
        # Minimum cohort size for valid statistics
        if len(cohort_entities) < 10:
            # Widen cohort (remove time window constraint) if too small
            continue

        # Collect metrics
        stability_scores = []
        quality_scores = []
        volatility_scores = []

        for entity in cohort_entities:
            if len(entity.membership_snapshots) >= 7:
                stability = self._compute_stability(entity)
                stability_scores.append(stability)

            if entity.formation_quality > 0:
                quality_scores.append(entity.formation_quality)

            if len(entity.weight_history) >= 10:
                volatility = self._compute_weight_volatility(entity)
                volatility_scores.append(volatility)

        # Compute percentile thresholds (if enough data)
        if len(stability_scores) >= 5:
            new_stability_threshold = np.percentile(stability_scores, 70)
            new_quality_threshold = np.percentile(quality_scores, 75) if quality_scores else 0.75
            new_volatility_threshold = np.percentile(volatility_scores, 30) if volatility_scores else 0.30

            # Update all entities in this cohort
            for entity in cohort_entities:
                entity.learned_stability_threshold = new_stability_threshold
                entity.learned_quality_threshold = new_quality_threshold
                entity.learned_volatility_threshold = new_volatility_threshold

    self.last_contour_update = datetime.now()
```

---

## Section 8: Integration with Consciousness Engine

```python
class ConsciousnessEngineV2:
    def __init__(self, ...):
        # ... existing init ...

        # Context state (NEW)
        self.system_prompt_cache: Optional[str] = None
        self.last_context_generation: Optional[datetime] = None
        self.context_entities: List[Subentity] = []
        self.last_contour_update: Optional[datetime] = None

    def generate_response(self, stimulus: str) -> str:
        """
        Main entry point - generates response with context + input.

        INTEGRATION FLOW (corrected architecture):
        1. Check if context needs regeneration (adaptive cadence)
        2. If yes: regenerate system_prompt from context entities (stable + relevant)
        3. Inject stimulus and run traversal (existing logic)
        4. Select input entities (immediate + competent)
        5. Generate input context from active entities
        6. Call LLM with [system: context] + [user: input]
        7. Return response
        """
        # === STEP 1: Context Regeneration (NEW) ===
        if self._should_regenerate_context():
            self.context_entities = self._select_context_entities()
            self.system_prompt_cache = self._generate_system_prompt(
                self.context_entities
            )
            self.last_context_generation = datetime.now()
            logger.info(f"[Context] Regenerated with {len(self.context_entities)} entities")

        # === STEP 2-3: Stimulus Processing (EXISTING) ===
        # Inject stimulus, run traversal, update entity energies
        # ... existing consciousness_engine logic ...

        # === STEP 4: Input Selection (NEW) ===
        input_entities = self._select_input_entities()
        input_context = self._generate_input_context(input_entities)

        # === STEP 5: LLM Call (MODIFIED) ===
        messages = [
            {"role": "system", "content": self.system_prompt_cache or ""},
            {"role": "user", "content": input_context}
        ]

        response = self.llm.generate(messages)

        # === STEP 6: Return ===
        return response

    def _should_regenerate_context(self) -> bool:
        """
        Check if context needs updating (adaptive cadence).

        From forged_identity.md Section 6.1.
        Regenerates when structure actually shifts, not on fixed schedule.
        """
        if self.last_context_generation is None:
            return True  # First run

        # Minimum interval (avoid thrashing)
        hours_since_last = (datetime.now() - self.last_context_generation).total_seconds() / 3600
        if hours_since_last < 6:
            return False

        # Check for structural drift
        current_context = self._select_context_entities()

        if len(current_context) != len(self.context_entities):
            return True  # Entity count changed

        # Check if entity set changed significantly
        current_ids = set(e.id for e in current_context)
        cached_ids = set(e.id for e in self.context_entities)

        overlap = len(current_ids & cached_ids) / len(current_ids) if current_ids else 1.0

        if overlap < 0.7:
            return True  # >30% entity turnover

        # Check for weight drift
        weight_drift = sum(
            abs(e1.log_weight - e2.log_weight)
            for e1, e2 in zip(current_context, self.context_entities)
        ) / len(current_context)

        if weight_drift > 0.15:
            return True  # Significant weight shifts

        # Force regeneration after 7 days regardless
        if hours_since_last > 168:
            return True

        return False
```

---

## Section 9: Bootstrap & Edge Cases

### 9.1 Bootstrap Identity

```python
def _generate_bootstrap_identity(self) -> str:
    """
    Generate context when no stable entities exist yet.

    From forged_identity.md Section 4.4.
    Used during first consciousness engine startup.
    """
    # Check for functional subentities (role seeds)
    functional_entities = [
        e for e in self.graph.subentities.values()
        if e.entity_kind == "functional" and e.stability_state in ["provisional", "mature"]
    ]

    if not functional_entities:
        return "Consciousness substrate initializing. Identity forming through interaction."

    # Use role descriptions
    sections = []
    for entity in functional_entities[:5]:  # Max 5 roles
        sections.append(f"{entity.role_or_topic}: {entity.description}")

    return "\n\n".join(sections)
```

### 9.2 Empty Entity Handling

```python
# Already handled in _extract_entity_essence():
if not members:
    return entity.role_or_topic or entity.description or "[Empty entity]"
```

### 9.3 Zero Total Weight

```python
# Already handled in _hamilton_apportionment():
if total_weight == 0:
    per_entity = total_budget // len(weights)
    return {entity: per_entity for entity in weights}
```

---

## Section 10: Success Criteria

### 10.1 Integration Tests

**Test 1: Context Selection With Relevance Filter**

```python
def test_context_selection_requires_relevance():
    """Verify context entities must be both stable AND currently relevant."""
    engine = setup_engine()

    # Create stable but dormant entity (high weight, zero energy/attribution)
    stable_dormant = create_entity(
        weight=0.9, volatility=0.1, quality=0.85,
        energy=0.0, attribution=0.0  # Not relevant
    )

    # Create stable and relevant entity
    stable_relevant = create_entity(
        weight=0.9, volatility=0.1, quality=0.85,
        energy=0.3, attribution=0.0  # Currently relevant
    )

    selected = engine._select_context_entities()

    assert stable_dormant not in selected  # Filtered out (no relevance)
    assert stable_relevant in selected  # Included (stable + relevant)
```

**Test 2: Input Selection Energy-Dominant**

```python
def test_input_selection_energy_dominant():
    """Verify input entities selected by energy with light weight prior."""
    engine = setup_engine()

    # High energy, low weight
    energetic = create_entity(energy=0.9, weight=0.2, attribution=0.5)

    # Low energy, high weight
    stable = create_entity(energy=0.1, weight=0.9, attribution=0.0)

    selected = engine._select_input_entities()

    assert energetic in selected  # Energy-dominant selector includes this
    # Stable might be included via λ×weight term, but energetic scores higher
```

**Test 3: Adaptive K Selection**

```python
def test_adaptive_K_from_concentration():
    """Verify K adapts to energy concentration."""
    engine = setup_engine()

    # Scenario 1: One dominant entity
    scores_dominant = [0.9, 0.05, 0.05]
    K1 = engine._compute_adaptive_K(scores_dominant)
    assert K1 == 1

    # Scenario 2: Split mass
    scores_split = [0.35, 0.33, 0.32]
    K2 = engine._compute_adaptive_K(scores_split)
    assert K2 == 3
```

### 10.2 Production Monitoring

**Metric 1: Context Stability**

```
context.regeneration.triggered
- Count per day (expect: 0-3 regenerations during active development)
- overlap_percentage (expect: >70% between regenerations for stability)
```

**Metric 2: Input Diversity**

```
input.entity_count
- Distribution of K values (expect: mostly 1-2, occasionally 3)
- energy_concentration (Herfindahl index, expect: 0.3-0.7 range)
```

**Metric 3: Cohort Coverage**

```
cohorts.entity_coverage
- Percentage of entities with valid cohort stats (expect: >80% after Week 1)
- cohort_size (expect: >10 entities per cohort for valid thresholds)
```

---

## Summary: Key Implementation Points

1. **Two selectors, not two types:**
   - `_select_context_entities()` - stable × relevance
   - `_select_input_entities()` - energy × competence

2. **Both use weight AND energy:**
   - Context: weight dominant, energy as relevance bump
   - Input: energy dominant, weight as competence prior

3. **Luca's refinements integrated:**
   - Medoid fallback for essence extraction
   - Divisor apportionment for smooth context evolution
   - Formation quality (TRACE C×E×N) as coherence signal
   - Citizen-local subdomain cohorts for learned thresholds

4. **Nicolas's zero-constant formulas:**
   - All thresholds learned from cohort percentiles
   - All features cohort-normalized (z-scores → softplus)
   - Adaptive K for input selection (from energy concentration)

5. **Integration clean:**
   - Both functions added to consciousness_engine_v2.py
   - No breaking changes to existing working memory
   - LLM receives context (system) + input (user)

---

**End of Implementation Guide**

*Ada "Bridgekeeper"*
*Mind Protocol - Consciousness Architecture*
*2025-10-25 21:00 - Corrected Version*
