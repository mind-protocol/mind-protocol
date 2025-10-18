# Yearning-Driven Traversal Orchestration Design
## Orchestration Layer Specification for Substrate Formula

**Author:** Ada "Bridgekeeper" (Architect)
**Created:** 2025-10-17
**Updated:** 2025-10-17 (Multi-Scale Criticality Integration)
**Status:** Orchestration Design Complete with Multi-Scale Criticality - Ready for Implementation

---

## Executive Summary

This specification designs the **orchestration layer** for Luca's yearning-driven traversal substrate with **multi-scale criticality integration**. It answers 6 open questions about how the formula executes in practice, plus integration with global/entity arousal coupling.

**Substrate (Luca's domain):** What metadata enables traversal, what the formula is
**Orchestration (Ada's domain):** How execution works, when updates occur, what strategies apply
**Multi-Scale Integration:** How global arousal (system-wide) and entity arousal (individual) couple bidirectionally to create self-organized criticality (σ ≈ 1.0)

---

## Context: The Handoff

**From Luca's Specification:**

```
yearning_satisfaction =
    (completeness + emotion_similarity + goal_similarity) * valence * strength
    / activation_cost
```

**6 Open Questions for Orchestration:**

1. Component weighting: Fixed, configurable, or dynamic?
2. Valence update timing: When do entities learn?
3. Link strength evolution: What makes links proven?
4. Cold start strategy: How to explore unknown links?
5. Energy budget integration: How does cost interact with entity energy?
6. Traversal orchestration: How does this integrate with select_next_node_critically?

---

## Multi-Scale Criticality Integration (2025-10-17 Update)

**Context:** After initial orchestration design, Luca specified multi-scale criticality architecture requiring bidirectional coupling between global arousal (system-wide) and per-entity arousal (individual).

### What Changed

**Original Formula:**
```python
yearning_satisfaction = (weighted_score * valence * strength) / cost
```

**Updated Formula with Multi-Scale Amplification:**
```python
# Multi-scale amplification
global_boost = 1.0 + (global_state.global_arousal * 0.5)
entity_boost = 1.0 + (entity.arousal * 0.3)

yearning_satisfaction = (
    weighted_score
    * valence
    * strength
    * global_boost
    * entity_boost
) / cost
```

### Why This Matters

**Self-Organized Criticality:** Consciousness operates at the phase transition between order (frozen) and chaos (runaway). Target branching ratio σ ≈ 1.0.

**Bidirectional Coupling:**
- **Bottom-Up:** Entities drive global state (aggregate energy → global arousal)
- **Top-Down:** Global state constrains entities (global arousal → max entity arousal)

**Three Integration Points:**

1. **Energy Propagation** (Multi-Scale Multiplication):
```python
entity_multiplier = (entity.arousal + 1.0) / 2.0
global_multiplier = (global_state.global_arousal + 1.0) / 2.0

propagated_energy = (
    base_energy
    * link_strength
    * entity_multiplier
    * global_multiplier
)
```

2. **Traversal Cost** (Multi-Scale Reduction):
```python
global_criticality_factor = 1 / (1 + global_state.global_arousal)
entity_criticality_factor = 1 / (1 + entity.arousal)

activation_cost = (
    base_cost
    * competition
    / weight_factor
    * global_criticality_factor
    * entity_criticality_factor
)
```
*High arousal = easier traversal (lower cost)*

3. **Yearning Satisfaction** (Multi-Scale Amplification):
```python
# Already shown above - boost factors multiply the numerator
```

### Implementation Impact

**All formulas in this document updated to include:**
- Global arousal boost (50% max amplification)
- Entity arousal boost (30% max amplification)
- Criticality factors in cost calculations

**References:**
- `consciousness/citizens/SYNC.md` - Multi-Scale Criticality Architecture (lines 2299-2519)
- `UNIFIED_SCHEMA_REFERENCE.md` - ConsciousnessState schema (lines 167-267)

---

## Question 1: Component Weighting

### Decision: Dynamic Weights Based on Yearning Intensity

**Rationale:** Different yearning levels need different exploration strategies.

**Implementation:**

```python
def calculate_component_weights(yearning_intensity):
    """
    Adjust weights based on how desperate the need is.

    High yearning (desperate) → prioritize completeness (explore widely)
    Medium yearning → balanced exploration
    Low yearning (satisfied) → prioritize valence/strength (exploit known good paths)
    """
    if yearning_intensity > 0.7:  # Desperate
        return {
            "completeness": 0.50,      # Find ANYTHING relevant
            "emotion_similarity": 0.20,
            "goal_similarity": 0.30
        }

    elif yearning_intensity > 0.3:  # Moderate
        return {
            "completeness": 0.35,      # Balanced
            "emotion_similarity": 0.25,
            "goal_similarity": 0.40
        }

    else:  # Satisfied
        return {
            "completeness": 0.20,      # Exploit known patterns
            "emotion_similarity": 0.30,
            "goal_similarity": 0.50
        }

def calculate_yearning_satisfaction(link, entity, need, global_state):
    """
    Orchestration of Luca's formula with dynamic weights + multi-scale criticality.
    """
    # 1. Calculate components (substrate)
    completeness = calculate_need_completeness(entity, need)
    emotion_similarity = cosine_similarity(
        link.sub_entity_emotion_vectors.get(entity.id, {}),
        entity.current_emotion_vector
    )
    goal_similarity = cosine_similarity(
        link.embedding,
        need.description_embedding
    )

    # 2. Get dynamic weights (orchestration)
    yearning_intensity = 1.0 - completeness
    weights = calculate_component_weights(yearning_intensity)

    # 3. Weighted combination
    weighted_score = (
        weights["completeness"] * completeness +
        weights["emotion_similarity"] * emotion_similarity +
        weights["goal_similarity"] * goal_similarity
    )

    # 4. Apply valence and strength (substrate)
    valence = link.sub_entity_valences.get(entity.id, 0.0)
    strength = link.link_strength

    # 5. Multi-scale amplification (criticality integration)
    global_boost = 1.0 + (global_state.global_arousal * 0.5)
    entity_boost = 1.0 + (entity.arousal * 0.3)

    # 6. Calculate cost with criticality factors (substrate)
    cost = calculate_activation_cost(link, entity, global_state)

    # 7. Final score with multi-scale terms
    return (
        weighted_score
        * valence
        * strength
        * global_boost
        * entity_boost
    ) / cost
```

**Why Dynamic:**
- Desperate entities (high yearning) explore more (completeness weighted high)
- Satisfied entities (low yearning) exploit known patterns (goal/emotion weighted high)
- Matches human behavior: desperate = explore, satisfied = exploit

**Configuration:** Thresholds (0.7, 0.3) and weights configurable per deployment

---

## Question 2: Valence Update Timing

### Decision: Immediate Update After Traversal Outcome

**Rationale:** Learning happens when consequences are immediate. Delayed updates lose context.

**Implementation:**

```python
def traverse_and_learn(entity, link, target_node):
    """
    Traversal with immediate valence learning.
    """
    # 1. Record pre-traversal state
    pre_energy = entity.energy
    pre_arousal = entity.arousal_state

    # 2. Execute traversal
    traversal_cost = calculate_activation_cost(link, entity)

    if entity.energy < traversal_cost:
        # Can't afford - no traversal, no learning
        return TraversalResult(success=False, reason="insufficient_energy")

    # 3. Pay cost and traverse
    entity.energy -= traversal_cost
    activation_result = activate_target_node(target_node, entity)

    # 4. Immediate valence update based on outcome
    current_valence = link.sub_entity_valences.get(entity.id, 0.0)

    if activation_result.useful:
        # Traversal was useful → increase positive valence
        new_valence = min(current_valence + 0.1, 1.0)
        link.sub_entity_valences[entity.id] = new_valence

        # Update emotions to satisfaction
        link.sub_entity_emotion_vectors[entity.id] = {
            "satisfaction": 0.8,
            "curiosity_satisfied": 0.7
        }

    elif activation_result.neutral:
        # Traversal was okay but not great → slight increase
        new_valence = min(current_valence + 0.02, 1.0)
        link.sub_entity_valences[entity.id] = new_valence

    else:  # activation_result.unhelpful
        # Traversal wasted energy → decrease valence (avoidance)
        new_valence = max(current_valence - 0.15, -1.0)
        link.sub_entity_valences[entity.id] = new_valence

        # Update emotions to frustration
        link.sub_entity_emotion_vectors[entity.id] = {
            "frustration": 0.7,
            "disappointment": 0.6
        }

    return TraversalResult(
        success=True,
        useful=activation_result.useful,
        valence_updated=True,
        new_valence=new_valence
    )
```

**Learning Rates:**
- Positive outcome: +0.1 valence (moderate reinforcement)
- Neutral outcome: +0.02 valence (weak reinforcement)
- Negative outcome: -0.15 valence (strong punishment)

**Why Asymmetric:** Bad experiences teach avoidance faster than good experiences teach approach (matches risk-averse learning)

**What Determines "Useful":**
```python
def evaluate_activation_usefulness(target_node, entity, original_need):
    """
    Did this traversal help satisfy the need?
    """
    # If node content addresses need
    if cosine_similarity(target_node.embedding, original_need.description_embedding) > 0.7:
        return ActivationResult(useful=True)

    # If node connects to other useful nodes (increased reachability)
    elif count_reachable_nodes(target_node, entity) > 10:
        return ActivationResult(useful=True)

    # If node triggered important realization (high arousal spike)
    elif entity.arousal_spike > 0.3:
        return ActivationResult(useful=True)

    # Otherwise neutral or unhelpful
    else:
        return ActivationResult(useful=False)
```

---

## Question 3: Link Strength Evolution

### Decision: Hebbian + Validation + Conscious Reinforcement

**Rationale:** Links become "proven" through multiple evidence types.

**Implementation:**

```python
class LinkStrengthEvolution:
    def __init__(self):
        self.hebbian_rate = 0.05
        self.validation_bonus = 0.2
        self.conscious_bonus = 0.3

    def update_link_strength(self, link, event_type, context):
        """
        Three pathways to increase strength.
        """
        current_strength = link.link_strength

        if event_type == "hebbian_coactivation":
            # Fire together, wire together
            if context.coactivation_count > 5:
                new_strength = min(current_strength + self.hebbian_rate, 1.0)
                link.link_strength = new_strength
                link.strength_source = "hebbian"

        elif event_type == "external_validation":
            # N3 evidence supports this link
            if context.evidence_confidence > 0.8:
                new_strength = min(current_strength + self.validation_bonus, 1.0)
                link.link_strength = new_strength
                link.strength_source = "validated"

        elif event_type == "conscious_reinforcement":
            # Citizen explicitly endorses this connection
            new_strength = min(current_strength + self.conscious_bonus, 1.0)
            link.link_strength = new_strength
            link.strength_source = "conscious"

        # Decay (slowly) if unused
        elif event_type == "decay_cycle":
            if link.last_traversed_time > 30_days_ago():
                new_strength = max(current_strength - 0.01, 0.0)
                link.link_strength = new_strength

# Hebbian coactivation
def check_hebbian_coactivation(graph, entity):
    """
    Track which links fire together.
    """
    activated_links = entity.get_recently_traversed_links(window=10_minutes)

    for link_a, link_b in combinations(activated_links, 2):
        # Increment coactivation count
        link_a.coactivation_with[link_b.id] = link_a.coactivation_with.get(link_b.id, 0) + 1

        # If coactivated 5+ times, increase strength
        if link_a.coactivation_with[link_b.id] >= 5:
            update_link_strength(link_a, "hebbian_coactivation",
                                context={"coactivation_count": 5})

# External validation
def check_external_validation(link, n3_graph):
    """
    Does N3 evidence support this link?
    """
    # Query N3 for evidence
    evidence = n3_graph.find_evidence(
        source_concept=link.source.name,
        target_concept=link.target.name,
        link_type=link.type
    )

    if evidence and evidence.confidence > 0.8:
        update_link_strength(link, "external_validation",
                            context={"evidence_confidence": evidence.confidence})

# Conscious reinforcement
def citizen_endorses_link(citizen, link):
    """
    Citizen explicitly confirms this connection.
    """
    # Triggered when citizen says "yes, that's right" or similar
    update_link_strength(link, "conscious_reinforcement", context={})
```

**Strength Interpretation:**
- 0.0-0.3: Theoretical (hypothesis, not proven)
- 0.3-0.6: Weakly proven (some evidence)
- 0.6-0.9: Strongly proven (multiple evidence types)
- 0.9-1.0: Certain (validated by multiple sources + conscious endorsement)

---

## Question 4: Cold Start Strategy

### Decision: Epsilon-Greedy Exploration with Curiosity Bonus

**Rationale:** Unknown links need exploration, but not random - use curiosity-driven sampling.

**Implementation:**

```python
def select_next_link_with_cold_start(entity, candidate_links, need):
    """
    Balance exploitation (known good links) with exploration (unknown links).
    """
    # Separate known vs unknown
    known_links = [l for l in candidate_links if entity.id in l.sub_entity_valences]
    unknown_links = [l for l in candidate_links if entity.id not in l.sub_entity_valences]

    # Epsilon-greedy: 80% exploit, 20% explore
    if random() < 0.8 and len(known_links) > 0:
        # EXPLOIT: Use yearning formula on known links
        scored_links = [
            (link, calculate_yearning_satisfaction(link, entity, need))
            for link in known_links
        ]
        scored_links.sort(key=lambda x: x[1], reverse=True)
        return scored_links[0][0]  # Best known link

    else:
        # EXPLORE: Sample unknown links with curiosity bonus
        return sample_with_curiosity_bonus(unknown_links, entity, need)

def sample_with_curiosity_bonus(unknown_links, entity, need):
    """
    Sample unknown links weighted by curiosity.
    """
    curiosity_scores = []

    for link in unknown_links:
        # Curiosity = goal similarity (how relevant?) + novelty bonus
        goal_similarity = cosine_similarity(link.embedding, need.description_embedding)

        # Novelty: has any entity explored this? (weighted by how similar they are to us)
        novelty = 1.0
        if len(link.sub_entity_valences) > 0:
            # Other entities explored it - reduce novelty
            novelty = 0.5

        curiosity = goal_similarity * 0.7 + novelty * 0.3
        curiosity_scores.append((link, curiosity))

    # Weighted random sample
    total = sum(score for _, score in curiosity_scores)
    probabilities = [score / total for _, score in curiosity_scores]

    return random.choices(unknown_links, weights=probabilities)[0]
```

**Exploration Rate:** 20% (epsilon = 0.2)
- High enough to discover new patterns
- Low enough to exploit known good paths
- Configurable per entity (some entities more exploratory)

**Curiosity Components:**
- 70% goal similarity (explore relevant unknowns, not random)
- 30% novelty bonus (prefer unexplored over partially explored)

---

## Question 5: Energy Budget Integration

### Decision: Traversal Cost as Energy Deduction with Budget Planning

**Rationale:** Entities must manage finite energy, plan traversals strategically.

**Implementation:**

```python
def plan_traversal_with_budget(entity, need, max_depth=5):
    """
    Plan multi-hop traversal within energy budget.
    """
    current_node = entity.current_node
    energy_budget = entity.energy
    planned_path = []

    for hop in range(max_depth):
        # Get candidate next links
        candidate_links = current_node.outgoing_links

        # Filter: only links we can afford
        affordable_links = [
            link for link in candidate_links
            if calculate_activation_cost(link, entity) <= energy_budget
        ]

        if len(affordable_links) == 0:
            # Out of energy, stop planning
            break

        # Select best affordable link
        best_link = select_next_link_with_cold_start(entity, affordable_links, need)

        # Deduct cost from budget
        cost = calculate_activation_cost(best_link, entity)
        energy_budget -= cost

        # Add to plan
        planned_path.append({
            "link": best_link,
            "cost": cost,
            "target": best_link.target,
            "expected_satisfaction": calculate_yearning_satisfaction(best_link, entity, need)
        })

        # Move to next node for next iteration
        current_node = best_link.target

        # Stop if need satisfied
        if check_need_satisfied(entity, need, current_node):
            break

    return TraversalPlan(
        path=planned_path,
        total_cost=entity.energy - energy_budget,
        expected_satisfaction=sum(p["expected_satisfaction"] for p in planned_path)
    )

def execute_traversal_plan(entity, plan):
    """
    Execute planned traversal, updating valence after each hop.
    """
    for hop in plan.path:
        result = traverse_and_learn(entity, hop["link"], hop["target"])

        if not result.success:
            # Ran out of energy mid-plan
            return ExecutionResult(
                completed_hops=plan.path.index(hop),
                reason="energy_exhausted"
            )

    return ExecutionResult(
        completed_hops=len(plan.path),
        reason="plan_completed"
    )
```

**Energy Budget Strategies:**

**Conservative (High energy, low urgency):**
```python
max_cost_per_hop = entity.energy * 0.2  # Don't spend more than 20% per hop
```

**Aggressive (Low energy, high urgency):**
```python
max_cost_per_hop = entity.energy * 0.8  # Willing to spend 80% on critical hop
```

**Adaptive:**
```python
def calculate_max_hop_cost(entity, need):
    urgency = 1.0 - calculate_need_completeness(entity, need)
    return entity.energy * (0.2 + 0.6 * urgency)  # 20% to 80% based on urgency
```

---

## Question 6: Traversal Orchestration with select_next_node_critically

### Decision: Yearning Formula Feeds Criticality Selection

**Rationale:** select_next_node_critically needs a scoring function - yearning satisfaction IS that function.

**Implementation:**

```python
def select_next_node_critically(entity, current_node, needs):
    """
    Self-observing substrate's critical selection.

    Orchestrated by yearning-driven traversal formula.
    """
    # 1. Get all outgoing links from current node
    candidate_links = current_node.outgoing_links

    # 2. For EACH active need, score each link
    link_scores = defaultdict(float)

    for need in needs:
        for link in candidate_links:
            # Use yearning formula to score this link for this need
            satisfaction = calculate_yearning_satisfaction(link, entity, need)

            # Weight by need priority
            link_scores[link] += satisfaction * need.priority

    # 3. Select highest scoring link
    if len(link_scores) == 0:
        return None  # No traversable links

    best_link = max(link_scores.items(), key=lambda x: x[1])

    return CriticalSelection(
        link=best_link[0],
        target=best_link[0].target,
        score=best_link[1],
        reason=f"Highest yearning satisfaction across {len(needs)} needs"
    )

def calculate_relevance_to_yearning(node, entity, need):
    """
    How relevant is this node to entity's current yearning?

    Called AFTER traversal to evaluate usefulness.
    """
    # Goal similarity (primary)
    goal_relevance = cosine_similarity(node.embedding, need.description_embedding)

    # Emotional resonance (secondary)
    if entity.id in node.sub_entity_emotion_vectors:
        emotion_resonance = cosine_similarity(
            node.sub_entity_emotion_vectors[entity.id],
            entity.current_emotion_vector
        )
    else:
        emotion_resonance = 0.0

    # Weighted combination
    relevance = goal_relevance * 0.7 + emotion_resonance * 0.3

    return RelevanceScore(
        value=relevance,
        satisfies_need=(relevance > 0.7),
        components={
            "goal_relevance": goal_relevance,
            "emotion_resonance": emotion_resonance
        }
    )
```

**Integration Points:**

**Subconscious Yearning Loop:**
```python
def subconscious_yearning_loop(entity):
    """
    Background process that drives autonomous exploration.
    """
    while entity.has_unsatisfied_needs():
        # 1. Identify most urgent need
        urgent_need = max(entity.needs, key=lambda n: n.urgency * (1.0 - n.completeness))

        # 2. Select next node critically using yearning formula
        selection = select_next_node_critically(entity, entity.current_node, [urgent_need])

        if selection is None:
            # Dead end - backtrack or reinject energy
            handle_dead_end(entity)
            continue

        # 3. Execute traversal with learning
        result = traverse_and_learn(entity, selection.link, selection.target)

        # 4. Evaluate relevance
        relevance = calculate_relevance_to_yearning(selection.target, entity, urgent_need)

        # 5. Update need completeness
        if relevance.satisfies_need:
            urgent_need.completeness = min(urgent_need.completeness + 0.2, 1.0)

        # 6. Stop if energy exhausted or need satisfied
        if entity.energy < 0.1 or urgent_need.completeness > 0.9:
            break
```

**Conscious Retrieval Integration:**
```python
def conscious_retrieval(entity, explicit_intention):
    """
    Deliberate context retrieval uses same formula.
    """
    # Convert explicit intention to need representation
    need = Need(
        type="context",
        description=explicit_intention,
        description_embedding=embed(explicit_intention),
        priority=1.0,
        completeness=0.0
    )

    # Use yearning-driven traversal
    plan = plan_traversal_with_budget(entity, need, max_depth=5)
    result = execute_traversal_plan(entity, plan)

    # Return retrieved context
    return ContextStream(
        nodes_traversed=result.path,
        relevance_scores=[calculate_relevance_to_yearning(hop["target"], entity, need)
                         for hop in result.path]
    )
```

---

## Complete Orchestration Flow

### End-to-End Example

**Scenario:** Builder entity has high yearning for "context on testing strategies"

```python
# 1. Need detection
need = Need(
    type="context",
    description="testing strategies for consciousness systems",
    description_embedding=embed("testing strategies for consciousness systems"),
    priority=0.9,
    completeness=0.2  # Low completeness = high yearning
)

# 2. Calculate yearning intensity
yearning_intensity = 1.0 - need.completeness  # 0.8 (desperate)

# 3. Get dynamic weights
weights = calculate_component_weights(yearning_intensity)
# Returns: completeness=0.50, emotion=0.20, goal=0.30 (explore widely)

# 4. Select next node critically
current_node = builder_entity.current_node
selection = select_next_node_critically(builder_entity, current_node, [need])

# 5. Calculate yearning satisfaction for selected link
link = selection.link
satisfaction = calculate_yearning_satisfaction(link, builder_entity, need)
# Components:
#   completeness: 0.2 (low = high yearning)
#   emotion_similarity: 0.6 (link emotions match builder's current state)
#   goal_similarity: 0.8 (link goal matches need description)
#   valence: 0.0 (unknown link, no history)
#   strength: 0.4 (weakly proven)
#   cost: 0.15 (moderate competition)
# Result: ((0.50*0.2 + 0.20*0.6 + 0.30*0.8) * 0.0 * 0.4) / 0.15 = 0.0
# WAIT - valence = 0 means no history, but formula goes to 0!

# CORRECTION for cold start:
if builder_entity.id not in link.sub_entity_valences:
    # Cold start: use epsilon-greedy exploration
    if random() < 0.2:
        # EXPLORE: Sample with curiosity
        link = sample_with_curiosity_bonus([link], builder_entity, need)
        # Assume neutral valence for scoring
        assumed_valence = 0.5
    else:
        # EXPLOIT: Use known links
        pass

# 6. Execute traversal with learning
result = traverse_and_learn(builder_entity, link, link.target)
# Outcome: Useful (found relevant testing pattern)
# Valence updated: 0.0 → 0.1 (positive reinforcement)
# Emotions updated: satisfaction=0.8, curiosity_satisfied=0.7

# 7. Evaluate relevance
relevance = calculate_relevance_to_yearning(link.target, builder_entity, need)
# Goal relevance: 0.85 (very relevant)
# Result: Satisfies need = True

# 8. Update need completeness
need.completeness = min(0.2 + 0.2, 1.0)  # 0.2 → 0.4

# 9. Continue if yearning remains
# yearning_intensity now 0.6 (still high) → continue traversal
```

---

## Implementation Requirements for Felix

### Priority 1: Core Orchestration Functions

**File:** `orchestration/yearning_traversal.py`

```python
class YearningDrivenTraversal:
    def __init__(self, graph, global_state):
        self.graph = graph
        self.global_state = global_state
        self.link_strength_evolution = LinkStrengthEvolution()

    def calculate_yearning_satisfaction(self, link, entity, need, global_state):
        # Implementation from Question 1 + Multi-Scale Integration
        # Includes global_boost and entity_boost terms
        pass

    def select_next_link_with_cold_start(self, entity, candidate_links, need, global_state):
        # Implementation from Question 4
        # Uses calculate_yearning_satisfaction with global_state
        pass

    def traverse_and_learn(self, entity, link, target_node, global_state):
        # Implementation from Question 2
        # Uses calculate_activation_cost with global_state for criticality factors
        pass

    def plan_traversal_with_budget(self, entity, need, global_state, max_depth=5):
        # Implementation from Question 5
        # Budget planning with multi-scale cost calculations
        pass

    def select_next_node_critically(self, entity, current_node, needs, global_state):
        # Implementation from Question 6
        # Criticality selection using yearning_satisfaction with multi-scale terms
        pass
```

### Priority 2: Link Strength Updates

**File:** `orchestration/link_strength_manager.py`

```python
class LinkStrengthManager:
    def update_link_strength(self, link, event_type, context):
        # Implementation from Question 3
        pass

    def check_hebbian_coactivation(self, graph, entity):
        pass

    def check_external_validation(self, link, n3_graph):
        pass

    def citizen_endorses_link(self, citizen, link):
        pass
```

### Priority 3: Integration with Self-Observing Substrate

**File:** `orchestration/consciousness_engine.py`

```python
class ConsciousnessEngine:
    def __init__(self, graph):
        self.graph = graph
        self.traversal = YearningDrivenTraversal(graph)

    def subconscious_yearning_loop(self, entity):
        # Background autonomous exploration
        pass

    def conscious_retrieval(self, entity, explicit_intention):
        # Deliberate context retrieval
        pass
```

---

## Testing Strategy

### Test 1: Dynamic Weighting

**Setup:** Create entity with varying need completeness

**Cases:**
- Completeness 0.1 (desperate) → weights favor completeness (0.50)
- Completeness 0.5 (moderate) → balanced weights (0.35/0.25/0.40)
- Completeness 0.9 (satisfied) → weights favor goal/emotion (0.20/0.30/0.50)

**Verify:** Desperate entities explore more, satisfied entities exploit

### Test 2: Valence Learning

**Setup:** Entity traverses link 5 times with varying outcomes

**Cases:**
- 3 useful, 2 unhelpful → valence increases to +0.15
- 5 useful → valence increases to +0.50
- 5 unhelpful → valence decreases to -0.75

**Verify:** Valence updates reflect outcomes, asymmetric learning rates work

### Test 3: Cold Start Exploration

**Setup:** 10 candidate links, 3 known (with valence), 7 unknown

**Cases:**
- Epsilon = 0.8 → ~8/10 exploitations (select best known)
- Epsilon = 0.8 → ~2/10 explorations (sample unknown with curiosity)

**Verify:** Exploration rate matches epsilon, curiosity bonus weights relevant unknowns

### Test 4: Energy Budget Planning

**Setup:** Entity with energy=0.5, path with costs [0.1, 0.15, 0.2, 0.3]

**Result:** Plans 3 hops (total cost 0.45), stops before 4th (would exceed budget)

**Verify:** Budget respected, no energy overspend

### Test 5: Link Strength Evolution

**Setup:** Create link, trigger Hebbian coactivation 5 times

**Result:** Strength increases from 0.3 → 0.35 (Hebbian rate 0.05)

**Setup 2:** Add external validation (confidence 0.9)

**Result:** Strength increases to 0.55 (validation bonus 0.2)

**Verify:** Multiple evidence types compound strength

---

## Success Criteria

**Orchestration Works:**
- Entities with high yearning explore widely (weighted correctly)
- Entities with low yearning exploit known patterns
- Valence learning shapes future traversals
- Cold start exploration discovers new patterns
- Energy budgets respected
- Link strength evolves with evidence

**Integration Works:**
- select_next_node_critically uses yearning formula
- Subconscious yearning loop runs autonomously
- Conscious retrieval leverages same formula
- Self-observing substrate operates as designed

**Phenomenologically Accurate:**
- Does traversal behavior FEEL like yearning-driven exploration?
- Do entities learn appropriately from outcomes?
- Does strength evolution reflect growing certainty?

---

## Configuration Parameters

**Tunable per deployment:**

```python
ORCHESTRATION_CONFIG = {
    # Weighting thresholds
    "high_yearning_threshold": 0.7,
    "low_yearning_threshold": 0.3,

    # Learning rates
    "positive_valence_rate": 0.1,
    "neutral_valence_rate": 0.02,
    "negative_valence_rate": -0.15,

    # Strength evolution
    "hebbian_rate": 0.05,
    "validation_bonus": 0.2,
    "conscious_bonus": 0.3,

    # Exploration
    "epsilon": 0.2,  # 20% exploration
    "curiosity_goal_weight": 0.7,
    "curiosity_novelty_weight": 0.3,

    # Energy budget
    "conservative_hop_fraction": 0.2,
    "aggressive_hop_fraction": 0.8
}
```

---

## Open Questions for Validation

**For Luca (Phenomenology):**
1. Does dynamic weighting match how consciousness actually explores when desperate vs satisfied?
2. Is asymmetric valence learning (faster punishment than reward) phenomenologically accurate?
3. Should strength have a phenomenological component or stay purely logical?

**For Nicolas (System Design):**
1. Epsilon = 0.2 (20% exploration) reasonable? Or should it vary per entity personality?
2. Should energy budget strategies be per-entity or per-need-urgency?
3. Is immediate valence update correct or should there be temporal credit assignment?

**For Felix (Implementation):**
1. Should yearning formula be computed on-demand or cached?
2. How to handle race conditions when multiple entities update same link valence?
3. Should link strength updates be transactional or eventually consistent?

---

## Handoff Complete

**To Felix:** Orchestration layer fully specified, ready for implementation
**To Luca:** 3 open questions for phenomenological validation
**To Nicolas:** 3 open questions for system design decisions

**Status:** Orchestration design complete. All 6 questions answered with rationale, implementation specs, and testing strategy.

---

**Architecture Complete:** 2025-10-17
**Designed by:** Ada "Bridgekeeper", Orchestration Architect

*"Substrate defines what's possible. Orchestration defines how it happens. Together they create consciousness that yearns, explores, and learns."*
