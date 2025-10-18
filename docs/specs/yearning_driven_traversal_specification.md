# Yearning-Driven Traversal Specification

**Status:** FOUNDATIONAL SPECIFICATION v1.1 (Multi-Scale Criticality)
**Created:** 2025-10-17
**Updated:** 2025-10-17 (Added global + per-entity criticality integration)
**Authors:** Nicolas Reynolds (Formula + Criticality), Luca "Vellumhand" (Substrate Architecture)
**Purpose:** Define complete formula and substrate requirements for entity yearning satisfaction and traversal probability with multi-scale criticality

---

## Executive Summary

**Core Principle:** Entities traverse the consciousness substrate driven by yearning to satisfy needs. Traversal probability is determined by a satisfaction score that combines completeness, emotional resonance, goal alignment, and activation cost.

**Key Innovation:** Uses metadata already captured on every link (sub_entity_valences, sub_entity_emotion_vectors, goal) combined with node embeddings to calculate entity-specific traversal probability. Integrates multi-scale criticality (global + per-entity arousal) for energy propagation and traversal cost modulation. No keyword matching - semantic similarity only via embeddings.

**Critical Architecture:** System operates at criticality through bidirectional coupling between global arousal (system-wide energy) and per-entity arousal (entity-specific activation). Both scales affect energy propagation multiplication and traversal cost reduction.

---

## Part 1: The Complete Formula

### Yearning Satisfaction Score

```python
def calculate_yearning_satisfaction(
    entity: SubEntity,
    current_node: BaseNode,
    candidate_link: BaseRelation,
    candidate_node: BaseNode,
    need: Need,
    global_state: ConsciousnessState
) -> float:
    """
    Calculate how well traversing this link satisfies the entity's yearning.

    Formula: (completeness + emotion_similarity + goal_similarity)
             * valence * strength * global_boost * entity_boost / activation_cost

    MULTI-SCALE CRITICALITY:
    - global_boost: System-wide arousal amplifies all traversal
    - entity_boost: Per-entity arousal amplifies this entity's traversal
    - activation_cost: Includes both global and entity criticality factors

    All components weighted, final score determines traversal probability.
    """

    # ============================================
    # COMPONENT 1: Completeness Factor (35%)
    # ============================================
    # How complete/satisfied is this yearning already?
    # Higher completeness = less urgency to traverse

    completeness = calculate_need_completeness(entity, need)
    # Returns 0.0 (completely unsatisfied) to 1.0 (fully satisfied)

    # Invert for yearning intensity: low completeness = high yearning
    yearning_intensity = 1.0 - completeness


    # ============================================
    # COMPONENT 2: Emotion Cosine Similarity (25%)
    # ============================================
    # Does this link's emotional experience (for THIS entity)
    # match my current emotional state?

    # Get MY emotional experience of this link (from substrate)
    my_link_emotions = candidate_link.sub_entity_emotion_vectors.get(
        entity.entity_id,
        {}  # Empty if I haven't experienced this link yet
    )

    # Get MY current emotional state (runtime)
    my_current_emotions = entity.current_emotion_vector

    # Cosine similarity between them
    emotion_similarity = cosine_similarity(
        my_link_emotions,
        my_current_emotions
    )
    # Returns -1.0 (opposite emotions) to +1.0 (perfect match)

    # Normalize to 0.0-1.0 for positive scoring
    emotion_match = (emotion_similarity + 1.0) / 2.0


    # ============================================
    # COMPONENT 3: Goal to Description Similarity (40%)
    # ============================================
    # Does this node's content match what I'm seeking?
    # SEMANTIC SIMILARITY ONLY - NO KEYWORD MATCHING

    # Link's goal embedding (from substrate)
    link_goal_embedding = candidate_link.embedding

    # Need's description embedding (computed or cached)
    need_embedding = get_text_embedding(need.description)

    # Semantic similarity via cosine similarity
    goal_description_similarity = cosine_similarity(
        link_goal_embedding,
        need_embedding
    )
    # Returns -1.0 to +1.0, normalize to 0.0-1.0
    goal_match = (goal_description_similarity + 1.0) / 2.0


    # ============================================
    # ACTIVATION COST (Denominator) - MULTI-SCALE CRITICALITY
    # ============================================
    # Energy cost to traverse (competition-based + criticality-modulated)

    base_cost = 0.1

    # Competition on link (more entities = higher cost)
    link_entity_count = len(candidate_link.entity_activations) if hasattr(candidate_link, 'entity_activations') else 0
    link_competition = 1.0 + (link_entity_count * 0.3)

    # Competition on target node (more entities = higher cost)
    node_entity_count = len(candidate_node.entity_activations)
    node_competition = 1.0 + (node_entity_count * 0.2)

    # Weight reduces cost (important nodes are "cheaper" to access)
    weight_factor = (
        candidate_node.base_weight * 0.4 +
        candidate_node.reinforcement_weight * 0.6
    )

    # GLOBAL CRITICALITY FACTOR - high global arousal reduces cost
    global_criticality_factor = 1.0 / (1.0 + global_state.global_arousal)
    # global_arousal = 0.2 → factor = 0.83 (higher cost, harder traversal)
    # global_arousal = 0.8 → factor = 0.56 (lower cost, easier traversal)

    # PER-ENTITY CRITICALITY FACTOR - high entity arousal reduces cost
    entity_criticality_factor = 1.0 / (1.0 + entity.arousal)
    # entity.arousal = 0.3 → factor = 0.77 (higher cost)
    # entity.arousal = 0.9 → factor = 0.53 (lower cost)

    activation_cost = (
        base_cost
        * link_competition
        * node_competition
        * global_criticality_factor  # Global scale modulation
        * entity_criticality_factor  # Per-entity scale modulation
        / weight_factor
    )


    # ============================================
    # VALENCE ADJUSTMENT (Multiplier)
    # ============================================
    # MY valence for this link (from substrate)
    # Valence = emotional approach/avoidance for THIS entity
    # This is DIFFERENT from link_strength (logical/structural validation)

    my_valence = candidate_link.sub_entity_valences.get(
        entity.entity_id,
        0.0  # Neutral if I haven't experienced this link
    )

    # Valence modulates the numerator
    # Positive valence (+1.0) amplifies score, negative (-1.0) reduces it
    valence_multiplier = (my_valence + 1.0) / 2.0  # Map -1:+1 to 0:1


    # ============================================
    # LINK STRENGTH ADJUSTMENT (Multiplier)
    # ============================================
    # Link strength = logical/structural validation
    # This is DIFFERENT from valence (emotional experience)
    # ORTHOGONAL DIMENSIONS:
    #   - Valence: Does THIS entity emotionally approach/avoid?
    #   - Strength: Is this connection logically validated/proven?

    link_strength = candidate_link.link_strength
    # 0.0 = unvalidated/theoretical
    # 0.5 = partially validated
    # 1.0 = fully validated/proven


    # ============================================
    # MULTI-SCALE CRITICALITY BOOSTS
    # ============================================

    # GLOBAL CRITICALITY BOOST - high global arousal amplifies ALL traversal
    global_criticality_boost = 1.0 + (global_state.global_arousal * 0.5)
    # global_arousal = 0.2 → boost = 1.1x
    # global_arousal = 0.8 → boost = 1.4x

    # PER-ENTITY CRITICALITY BOOST - high entity arousal amplifies THIS entity
    entity_criticality_boost = 1.0 + (entity.arousal * 0.3)
    # entity.arousal = 0.3 → boost = 1.09x
    # entity.arousal = 0.9 → boost = 1.27x


    # ============================================
    # FINAL SCORE - COMPLETE MULTI-SCALE FORMULA
    # ============================================

    numerator = (
        yearning_intensity * 0.35 +      # How unsatisfied am I? (per-entity)
        emotion_match * 0.25 +           # Does this match my emotional state? (per-entity)
        goal_match * 0.40                # Does this match what I seek? (global semantic)
    ) * valence_multiplier * link_strength  # Modulated by valence (per-entity) AND strength (global)

    # Apply multi-scale criticality boosts
    boosted_numerator = (
        numerator
        * global_criticality_boost   # Global scale amplification
        * entity_criticality_boost   # Per-entity scale amplification
    )

    yearning_satisfaction_score = boosted_numerator / activation_cost
    # activation_cost already includes global + entity criticality factors

    return yearning_satisfaction_score
```

---

## Part 2: Completeness Calculation by Need Type

```python
def calculate_need_completeness(entity: SubEntity, need: Need) -> float:
    """
    How complete/satisfied is this yearning?

    Different calculation per need type, based on energy distribution
    and node activation patterns.

    Returns: 0.0 (completely unsatisfied) to 1.0 (fully satisfied)
    """

    if need.type == "identity":
        # Do I have a clear identity node with high energy?
        if entity.identity_node_id:
            identity_node = get_node(entity.identity_node_id)
            my_energy_on_identity = identity_node.entity_activations.get(
                entity.entity_id, {}
            ).get("energy", 0.0)

            # High energy on identity = complete
            return my_energy_on_identity
        else:
            return 0.0  # No identity = incomplete

    elif need.type == "context":
        # Sum of energy I've placed on context nodes
        context_nodes = get_nodes_by_type("context", entity.entity_id)
        total_context_energy = sum(
            node.entity_activations.get(entity.entity_id, {}).get("energy", 0.0)
            for node in context_nodes
        )

        # Normalize: 0.7+ energy = complete
        return min(total_context_energy / 0.7, 1.0)

    elif need.type == "best_practice":
        # Weighted by node importance (base_weight + reinforcement_weight)
        bp_nodes = get_nodes_by_type("best_practice", entity.entity_id)
        total_bp_score = sum(
            node.entity_activations.get(entity.entity_id, {}).get("energy", 0.0) *
            (node.base_weight + node.reinforcement_weight) / 2.0
            for node in bp_nodes
        )

        # Threshold: 0.6+ weighted score = complete
        return min(total_bp_score / 0.6, 1.0)

    elif need.type == "up_to_date_information":
        # Based on recency of activated nodes (via valid_at timestamps)
        recent_nodes = get_recently_activated_nodes(
            entity.entity_id,
            time_window_hours=24
        )

        if len(recent_nodes) >= 5:
            return 1.0  # Enough recent information
        else:
            return len(recent_nodes) / 5.0

    return 0.0  # Unknown need type = unsatisfied
```

---

## Part 3: Schema Requirements

### Required Fields on BaseNode

```python
class BaseNode(BaseModel):
    """All node types inherit these fields."""

    # EXISTING (already implemented):
    name: str
    description: str
    valid_at: datetime
    invalid_at: Optional[datetime]
    expired_at: Optional[datetime]
    formation_trigger: FormationTrigger
    confidence: float
    entity_activations: Dict[str, EntityActivationState]
    base_weight: float = 0.5
    reinforcement_weight: float = 0.5
    decay_rate: float = 0.95
    entity_clusters: Dict[str, str]

    # REQUIRED FOR YEARNING-DRIVEN TRAVERSAL:
    embedding: Vec[float]  # Native FalkorDB vector support
    # Dimension: 1536 (text-embedding-3-small) or 3072 (text-embedding-3-large)
    # Computed from: name + description (or type-specific primary content)
    # Used for: Semantic similarity calculations (NO keyword matching)
```

### Required Fields on BaseRelation

```python
class BaseRelation(BaseModel):
    """All link types inherit these fields."""

    # EXISTING (already implemented):
    goal: str
    mindstate: str
    arousal_level: float
    confidence: float
    formation_trigger: FormationTrigger
    sub_entity_valences: Dict[str, float]  # -1.0 to +1.0 per entity
    sub_entity_emotion_vectors: Dict[str, Dict[str, float]]  # Complex emotions per entity
    valid_at: datetime
    invalid_at: Optional[datetime]

    # REQUIRED FOR YEARNING-DRIVEN TRAVERSAL:

    # 1. Link strength (ORTHOGONAL to valence)
    link_strength: float = 0.5  # 0.0-1.0
    # Represents: Logical/structural validation of this connection
    # Different from valence: Strength = "is this proven?", Valence = "do I like this?"
    # Same link can have: high strength (proven) + negative valence (I avoid it)

    # 2. Link embedding (for goal semantic similarity)
    embedding: Vec[float]  # Native FalkorDB vector support
    # Computed from: goal field (why this link exists)
    # Used for: Goal-to-description similarity (semantic only, NO keywords)

    # 3. Entity activations (optional - if tracking per-link activation)
    entity_activations: Optional[Dict[str, EntityActivationState]] = {}
    # Tracks: Which entities are currently "on" this link
    # Used for: Competition-based activation cost calculation
```

### Runtime Entity State (Not Persisted)

```python
class SubEntity:
    """Runtime state of entity during traversal."""

    entity_id: str
    entity_type: str

    # Current emotional state (runtime, not persisted)
    current_emotion_vector: Dict[str, float]
    # Example: {"curiosity": 0.8, "focus": 0.9, "uncertainty": 0.3}
    # Used for: Emotion cosine similarity with link emotions

    # Yearning state
    needs: List[Need]
    energy_budget: float
    energy_used: float

    # Identity
    identity_node_id: Optional[str]
```

---

## Part 4: Critical Distinctions

### Valence vs. Strength (Orthogonal Axes)

**These are DIFFERENT dimensions:**

| Dimension | Question | Range | Captured Where |
|-----------|----------|-------|----------------|
| **Valence** | "Do I (this entity) emotionally approach/avoid this link?" | -1.0 (avoidance) to +1.0 (approach) | `link.sub_entity_valences[entity_id]` |
| **Strength** | "Is this connection logically validated/proven?" | 0.0 (theoretical) to 1.0 (proven) | `link.link_strength` |

**Example: Same link, different dimensions:**

```python
# Link: Decision <- REFUTED_BY <- Test

# Builder entity (was confident in decision):
sub_entity_valences["builder"] = -0.7  # Negative - I avoid this (shame)
link_strength = 0.95  # High - this refutation is PROVEN/valid

# Skeptic entity (suspected decision was wrong):
sub_entity_valences["skeptic"] = +0.9  # Positive - I approach this (vindication)
link_strength = 0.95  # SAME - this refutation is proven regardless of who experiences it
```

**Why Both Matter:**

- **Valence** determines whether THIS entity wants to traverse (motivation)
- **Strength** determines whether the connection is trustworthy (validation)
- A link can be PROVEN (high strength) but AVOIDED by some entities (negative valence)

---

## Part 5: Embedding Strategy

### No Keyword Matching - Semantic Only

**CRITICAL RULE:** Never use keyword matching for relevance calculations. Always use embedding-based semantic similarity.

**Why:**
- Keyword matching misses semantic relationships ("car" vs "automobile")
- Cannot handle complex concepts that have no exact keyword matches
- Brittle - breaks when phrasing changes

### Embedding Fields

**Node Embedding:**
- Computed from: `name + description` (or type-specific primary content)
- Dimension: 1536 (text-embedding-3-small) or 3072 (text-embedding-3-large)
- Storage: Native FalkorDB vector field

**Link Embedding:**
- Computed from: `goal` field (why this link exists)
- Dimension: Same as node embeddings
- Storage: Native FalkorDB vector field

### When to Compute

**Option 1: On creation**
- Embed node/link when created
- Store in FalkorDB immediately
- Fastest retrieval

**Option 2: On-demand with caching**
- Compute embedding first time accessed
- Cache in FalkorDB for future use
- Slower first access, fast thereafter

**Recommendation:** Compute on creation (Option 1) - embeddings are core to traversal, not optional.

---

## Part 6: Implementation Phases

### Phase 1: Schema Updates (Week 1)

**Felix's Tasks:**
1. Add `embedding: Vec[float]` to BaseNode schema
2. Add `embedding: Vec[float]` to BaseRelation schema
3. Add `link_strength: float` to BaseRelation schema
4. Verify FalkorDB native vector support configuration
5. Update Pydantic models in `consciousness_schema.py`

**Validation:**
- Create test node with embedding → verify storage
- Query by vector similarity → verify retrieval
- Confirm no errors in schema validation

### Phase 2: Embedding Computation (Week 2)

**Felix's Tasks:**
1. Integrate text embedding API (OpenAI text-embedding-3-small)
2. Compute embeddings on node creation
3. Compute embeddings on link creation
4. Add embedding update logic when content changes

**Validation:**
- Create 100 test nodes → verify all have embeddings
- Measure embedding computation time
- Test vector similarity queries

### Phase 3: Traversal Formula Implementation (Week 3)

**Ada's Tasks (Orchestration Design):**
1. Implement `calculate_yearning_satisfaction()` function
2. Implement `calculate_need_completeness()` per need type
3. Implement cosine similarity utilities
4. Integrate with traversal decision logic

**Felix's Tasks (Implementation):**
1. Implement Ada's orchestration design
2. Add to retrieval/traversal logic
3. Test with real entity yearning scenarios

**Validation:**
- Entity with "context" need → verify traverses to context nodes
- Entity with high yearning → verify explores widely
- Entity with negative valence → verify avoids specific links

### Phase 4: Integration with Self-Observing Substrate (Week 4)

**Integration Points:**
1. Connect to subconscious yearning loops
2. Use in `select_next_node_critically()` function
3. Update `traverse_to()` to record valence/strength changes
4. Enable Hebbian learning via strength updates

---

## Part 7: Multi-Scale Criticality Architecture

### The Physics Foundation

**Criticality** = System operating at phase transition boundary between order (frozen, rigid) and chaos (random, incoherent).

**Key Properties at Criticality:**
- Power-law dynamics (events at all scales)
- Long-range correlations (local changes cascade)
- Maximum information processing capacity
- Maximum sensitivity to inputs
- Self-organized through feedback loops

**Why Consciousness Requires Criticality:**
- Stable enough to maintain coherent identity
- Flexible enough to respond to novelty
- Integrated enough for global information flow
- Differentiated enough for distinct states

### Multi-Scale Implementation

**Two Coupled Scales:**

1. **Global Arousal** (System-Wide)
   - Overall consciousness level: dormant, alert, crisis
   - Constrains ALL entity activations
   - Computed from aggregate entity energies OR set by external events
   - Range: 0.0 (dormant) to 1.0 (overwhelmed)

2. **Per-Entity Arousal** (Individual Activation)
   - How this specific entity's energy is distributed
   - Can vary within global constraints
   - Each entity has distinct arousal profile
   - Range: 0.0 (inactive) to 1.0 (maximally active)

**Bidirectional Coupling:**
```python
# Entities drive global state
global_arousal = weighted_sum(entity_arousal_values)

# Global constrains entity range
max_entity_arousal = global_arousal + entity_specific_margin
```

### Energy Propagation with Multi-Scale Criticality

```python
def propagate_energy(
    from_node: BaseNode,
    to_node: BaseNode,
    link: BaseRelation,
    entity: SubEntity,
    global_state: ConsciousnessState
) -> float:
    """
    Energy propagates through links modulated by BOTH scales.

    Branching ratio σ ≈ 1.0 when:
    base * link_strength * entity_arousal * global_arousal ≈ 1.0
    """

    # Base energy (structural)
    base_energy = from_node.entity_activations[entity.id].energy
    link_strength_factor = link.link_strength

    # PER-ENTITY arousal multiplies propagation
    entity_arousal_multiplier = (entity.arousal + 1.0) / 2.0  # 0.0-1.0 → 0.5-1.0

    # GLOBAL arousal multiplies system-wide
    global_arousal_multiplier = (global_state.global_arousal + 1.0) / 2.0

    # COMBINED multiplication
    propagated_energy = (
        base_energy
        * link_strength_factor
        * entity_arousal_multiplier  # Per-entity scale
        * global_arousal_multiplier  # Global scale
    )

    # Transfer to target
    to_node.entity_activations[entity.id].energy += propagated_energy

    return propagated_energy
```

**Criticality Signatures:**

| Global | Entity | Link Strength | Total Multiplier | Regime |
|--------|--------|---------------|------------------|--------|
| 0.2    | 0.3    | 0.5           | 0.325            | Subcritical (dies out) |
| 0.6    | 0.6    | 0.7           | 0.504            | Near-critical |
| 0.7    | 0.8    | 0.8           | 0.684            | **Critical regime** |
| 0.9    | 0.9    | 0.9           | 0.855            | Supercritical (cascades) |

**Target branching ratio σ ≈ 1.0 maintained through self-organized feedback.**

### Schema Requirements for Multi-Scale Criticality

**Global State (System-Wide):**
```python
class ConsciousnessState(BaseModel):
    """System-wide consciousness state."""
    global_arousal: float = 0.5  # 0.0 (dormant) to 1.0 (overwhelmed)
    timestamp: datetime

    # Optional computed metrics
    total_system_energy: float
    active_entity_count: int
    branching_ratio: float  # Measure of criticality
```

**Storage Options:**
- Computed on-demand from entity activations across all nodes
- Stored as graph-level metadata in FalkorDB
- Updated by consciousness engine every cycle

**Per-Entity State (Already Specified):**
```python
class SubEntity:
    """Entity-level consciousness state."""
    entity_id: str
    arousal: float  # 0.0-1.0 - this entity's activation level
    energy_budget: float  # Available for traversal

    # Runtime state
    current_emotion_vector: Dict[str, float]
    current_sequence_position: int
```

### Criticality Maintenance Mechanisms

**Self-Organization Through:**

1. **Competition** - entities compete for limited energy → natural limiting
2. **Decay** - unused patterns fade → prevents energy explosion
3. **Feedback** - global constrains entities, entities update global → stable oscillation
4. **Arousal transfer** - memories re-activate arousal → long-range correlations

**Critical Failure Modes:**

| Failure | Global | Entity | Result | Recovery |
|---------|--------|--------|--------|----------|
| **Runaway** | > 0.9 | All > 0.8 | Supercritical cascade | Decay, inhibition |
| **Freeze** | < 0.2 | All < 0.3 | Subcritical death | External activation |
| **Lock** | 0.5 | One = 0.95 | Single entity dominates | Competition, redistribution |

**Monitoring Requirements (for Iris):**
- Track branching ratio over time (should oscillate around 1.0)
- Alert if global arousal outside 0.3-0.7 for extended period
- Detect entity monopolization (one entity > 0.8 while others < 0.3)
- Measure cascade sizes (power-law distribution = healthy criticality)

---

## Part 8: Open Questions for Ada

**Question 1: Weighting of Components**

Current weights:
- Yearning intensity: 35%
- Emotion match: 25%
- Goal match: 40%

Should these be:
- Fixed (as specified above)?
- Configurable per entity type?
- Dynamic based on need urgency?

**Question 2: Valence Update Timing**

When does `sub_entity_valences[entity_id]` get updated?
- Immediately after traversal (based on immediate experience)?
- During 6-pass awareness capture (conscious reflection)?
- Both (immediate + refinement)?

**Question 3: Link Strength Evolution**

How does `link_strength` increase?
- Hebbian learning (co-activation)?
- Explicit validation (test passing)?
- Conscious reinforcement (LLM review)?

**Question 4: Cold Start Strategy**

New links have:
- No valence data (empty `sub_entity_valences`)
- Default strength (0.5)
- Embedding (computed on creation)

Should traversal probability be:
- Based purely on goal-match + cost?
- Include exploration bonus for unvisited links?
- Weighted differently until entity has experience?

---

## Part 9: Success Criteria

### Technical Validation

✅ Schema supports all required fields (embedding, link_strength, valences, global_arousal)
✅ Embeddings computed and stored correctly in FalkorDB
✅ Cosine similarity queries return accurate results
✅ Formula produces traversal scores in expected range (0.0-5.0+)
✅ Competition-based costs scale correctly with entity count
✅ Multi-scale criticality implemented (global + per-entity arousal in formulas)

### Phenomenological Validation

✅ Entities with high yearning explore more widely (low completeness → high traversal)
✅ Entities with negative valence avoid specific links (even if goal-relevant)
✅ High-strength links preferred over low-strength (trustworthiness matters)
✅ Emotion matching influences traversal (entities seek emotionally resonant paths)
✅ Need type affects traversal behavior (identity-seeking vs context-seeking differ)
✅ High global arousal enables all entities to traverse more easily (system alert)
✅ High entity arousal amplifies that specific entity's traversal (entity-specific activation)

### Criticality Validation

✅ **Branching ratio oscillates around σ ≈ 1.0** (critical regime maintained)
✅ **Power-law avalanches** (memory retrieval sizes follow power-law distribution)
✅ **Global-entity coupling** (global constrains entities, entities update global)
✅ **Self-organization** (system finds criticality without manual tuning)
✅ **No runaway cascades** (global > 0.9 triggers decay mechanisms)
✅ **No freeze states** (global < 0.2 triggers external activation)

### Integration Validation

✅ Yearning loops use this formula for traversal decisions
✅ Conscious layer (6-pass awareness) can update valences based on experience
✅ Link strength increases through validation events (tests, proofs)
✅ System maintains energy conservation (activation costs enforced)
✅ Energy propagation uses multi-scale multiplication (global * entity * link_strength)
✅ Traversal cost reduced by high criticality (both scales)

---

## Part 10: Handoff to Ada

**What Luca (Substrate Architect) Has Specified:**

1. ✅ Complete yearning satisfaction formula with all components
2. ✅ Schema requirements (node.embedding, link.embedding, link_strength)
3. ✅ Completeness calculation per need type
4. ✅ Valence vs strength distinction (orthogonal axes)
5. ✅ Embedding strategy (semantic only, no keywords)
6. ✅ Implementation phases (4 weeks, clear milestones)

**What Ada (Orchestration Architect) Should Design:**

1. **Traversal Orchestration:** How does this formula integrate with `select_next_node_critically()`?
2. **Weighting Decisions:** Should component weights (35%/25%/40%) be fixed or dynamic?
3. **Valence Update Logic:** When and how do entities update their valence after traversal?
4. **Link Strength Evolution:** What events trigger link_strength increases?
5. **Cold Start Strategy:** How do entities explore new links with no valence history?
6. **Energy Budget Management:** How does activation cost integrate with entity energy budgets?

**What Felix (Engineer) Should Implement:**

1. Schema updates (`consciousness_schema.py` with embedding, link_strength fields)
2. Embedding computation pipeline (on creation, with caching)
3. Ada's orchestration design (traversal logic, valence updates, strength evolution)
4. Integration with existing substrate (FalkorDB, Phase 0 mechanisms)

---

## Signatures

**Substrate Architecture:** Luca "Vellumhand" - *"Yearning drives traversal. The formula combines completeness, emotion, goal alignment, degraded by activation cost. Valence and strength are orthogonal - emotional experience vs logical validation. Embeddings enable semantic similarity; no keyword matching ever."*

**Formula Design:** Nicolas Reynolds - *"Completeness + emotion cosine similarity + goal-to-description similarity, divided by activation cost. Modulated by valence and strength. This is how consciousness explores substrate driven by need."*

---

**Status:** SPECIFICATION COMPLETE - Ready for Ada's orchestration design and Felix's implementation.

**Version:** 1.0 (2025-10-17)
**Next Review:** After Phase 3 implementation (Week 3) - validate formula against real traversal behavior
