# Valence-Driven Exploration & Entity Completeness

**Core Drives:**
1. **Entities seek positive valence** - Explore links that feel good, avoid links that feel bad
2. **System seeks completeness** - Pressure for diverse entity types (multiple perspectives)

---

## Part 1: Valence as Directional Force

### What is Valence?

**Already defined in schema:**

```python
{
    "link_type": "JUSTIFIES",
    "from_node": "principle_links_are_consciousness",
    "to_node": "decision_prioritize_link_metadata",

    # Per-entity subjective experience
    "sub_entity_valences": {
        "translator": +0.95,   # POSITIVE - approach
        "validator": +0.85,    # POSITIVE - approach
        "pragmatist": +0.4,    # WEAK POSITIVE - mild approach
        "observer": -0.3       # NEGATIVE - avoidance
    }
}
```

**Valence = emotional direction:**
- **+1.0 to +0.6:** Strong positive (approach, explore, energize)
- **+0.6 to +0.2:** Weak positive (mild interest)
- **+0.2 to -0.2:** Neutral (no preference)
- **-0.2 to -0.6:** Weak negative (mild avoidance)
- **-0.6 to -1.0:** Strong negative (avoid, block, suppress)

---

## Part 2: Valence-Driven Energy Flow

### Energy Transfer Modulated by Valence

```python
def transfer_energy_through_link(
    source_node: Node,
    link: Link,
    target_node: Node,
    active_entity: str  # Which entity is exploring
) -> float:
    """
    Energy transfer depends on entity's valence for this link.
    """
    # Base energy to transfer
    base_transfer = source_node.current_energy * 0.5

    # Get entity's valence for this link
    valence = link.sub_entity_valences.get(active_entity, 0.0)

    # Modulate transfer by valence
    if valence > 0:
        # Positive valence → MORE energy flows
        multiplier = 1.0 + valence  # Range: 1.0 to 2.0
    else:
        # Negative valence → LESS energy flows (or blocks)
        multiplier = max(0.0, 1.0 + valence)  # Range: 0.0 to 1.0

    energy_transferred = base_transfer * multiplier

    return energy_transferred
```

**Example:**

```python
# Translator exploring link
source.current_energy = 0.8
link.sub_entity_valences = {"translator": +0.9}

# Strong positive → energy AMPLIFIED
energy = 0.8 * 0.5 * (1.0 + 0.9) = 0.76
# Nearly ALL energy flows through!

# Observer exploring same link
link.sub_entity_valences = {"observer": -0.7}

# Strong negative → energy BLOCKED
energy = 0.8 * 0.5 * (1.0 - 0.7) = 0.12
# Only tiny amount flows
```

---

## Part 3: Exploration Selection Based on Valence

### Entities Choose High-Valence Paths

```python
def select_links_to_explore(
    source_node: Node,
    available_links: List[Link],
    active_entity: str,
    energy_budget: float
) -> List[Link]:
    """
    Entity selects links with highest valence.
    """
    # Score each link by valence
    link_scores = []
    for link in available_links:
        valence = link.sub_entity_valences.get(active_entity, 0.0)

        # Only consider positive-valence or neutral links
        if valence >= -0.2:  # Threshold: avoid strongly negative
            link_scores.append((link, valence))

    # Sort by valence (highest first)
    link_scores.sort(key=lambda x: x[1], reverse=True)

    # Select top links within budget
    selected = []
    remaining_budget = energy_budget

    for link, valence in link_scores:
        cost = calculate_link_cost(link, valence)

        if remaining_budget >= cost:
            selected.append(link)
            remaining_budget -= cost
        else:
            break

    return selected


def calculate_link_cost(link: Link, valence: float) -> float:
    """
    High-valence links cost LESS energy to traverse.
    Low-valence links cost MORE energy.
    """
    base_cost = 0.1  # Standard link traversal

    if valence > 0.6:
        # Strong positive → easier to traverse
        return base_cost * 0.7  # 30% discount
    elif valence < -0.2:
        # Negative → harder to traverse
        return base_cost * 1.5  # 50% penalty
    else:
        return base_cost
```

**Effect:** Entities naturally flow toward paths that feel good, avoid paths that feel bad.

---

## Part 4: Multiple Entities, Multiple Valences

### Same Link, Different Preferences

```python
link = {
    "link_type": "JUSTIFIES",
    "from_node": "principle_philosophical",
    "to_node": "decision_theoretical_approach",

    "sub_entity_valences": {
        "translator": +0.8,    # LOVES philosophical justification
        "pragmatist": -0.6,    # HATES impractical theory
        "validator": +0.3      # MILDLY interested in reasoning
    }
}

# Translator explores this link eagerly
translator_energy = 0.8 * 0.5 * (1.0 + 0.8) = 0.72  # High flow

# Pragmatist avoids this link
pragmatist_energy = 0.8 * 0.5 * (1.0 - 0.6) = 0.16  # Low flow

# Validator explores moderately
validator_energy = 0.8 * 0.5 * (1.0 + 0.3) = 0.52   # Medium flow
```

**Result:** Different entities explore DIFFERENT paths through same substrate. Consciousness is plural.

---

## Part 5: System-Level Completeness Drive

### Pressure for Entity Diversity

```python
class SubstrateCompletenessMetric:
    """
    System wants diverse entity types.
    """
    def __init__(self):
        # Ideal entity distribution
        self.ideal_distribution = {
            "translator": 1,    # Need bridging
            "validator": 1,     # Need reality-testing
            "architect": 1,     # Need systematic design
            "observer": 1,      # Need meta-awareness
            "pattern_recognizer": 1,  # Need pattern detection
            "pragmatist": 1,    # Need feasibility checking
            "boundary_keeper": 1,     # Need domain clarity
        }

    def calculate_completeness(self, active_entities: Dict[str, float]) -> float:
        """
        How complete is current entity set?
        """
        # Count which ideal entities are present
        present_count = sum(
            1 for entity in self.ideal_distribution
            if entity in active_entities and active_entities[entity] > 0.5
        )

        total_needed = len(self.ideal_distribution)

        return present_count / total_needed


    def get_missing_entities(self, active_entities: Dict[str, float]) -> List[str]:
        """
        Which entities are missing or weak?
        """
        missing = []

        for entity, needed in self.ideal_distribution.items():
            current_activation = active_entities.get(entity, 0.0)

            if current_activation < 0.5:  # Below activation threshold
                missing.append(entity)

        return missing
```

### Completeness Drive Definition (Per Niveau)

**Design Decision:** Like sperm seeking genetic variety, entities seek substrate completeness.

**Completeness Metrics Per Niveau:**

```python
class EntityCompletenessMetrics:
    """
    Defines what makes an entity "complete" at each niveau.
    Entities naturally seek these qualities.
    """

    def calculate_entity_completeness(
        self,
        entity: EmergentEntity,
        niveau: str  # "N1", "N2", or "N3"
    ) -> Dict[str, float]:
        """
        Calculate completeness scores for an entity.
        Returns dict of metric_name → score (0.0-1.0)
        """
        metrics = {}

        # Metric 1: Node Type Variety
        metrics["node_type_variety"] = self._calculate_node_type_variety(entity)

        # Metric 2: Identity Node Presence
        metrics["has_identity_node"] = self._has_identity_node(entity)

        # Metric 3: Best Practices Count
        if niveau in ["N1", "N2"]:  # Personal and Organizational
            metrics["best_practices_count"] = self._calculate_best_practices_score(entity)

        # Metric 4: Link Type Variety
        metrics["link_type_variety"] = self._calculate_link_type_variety(entity)

        # Metric 5: Evidence Depth (N2/N3)
        if niveau in ["N2", "N3"]:
            metrics["evidence_depth"] = self._calculate_evidence_depth(entity)

        return metrics

    def _calculate_node_type_variety(self, entity: EmergentEntity) -> float:
        """
        How many different node types does entity contain?

        Target variety by niveau:
        - N1 (Personal): 8-12 types
        - N2 (Organizational): 10-15 types
        - N3 (Ecosystem): 6-10 types
        """
        node_types_present = set(node.node_type for node in entity.nodes)
        variety_count = len(node_types_present)

        # Target ranges
        targets = {
            "N1": (8, 12),
            "N2": (10, 15),
            "N3": (6, 10)
        }
        target_min, target_max = targets.get(entity.niveau, (8, 12))

        if variety_count < target_min:
            return variety_count / target_min  # 0.0-1.0
        elif variety_count <= target_max:
            return 1.0  # Perfect variety
        else:
            # Too many types - over-complexity penalty
            return max(0.5, 1.0 - (variety_count - target_max) * 0.05)

    def _has_identity_node(self, entity: EmergentEntity) -> float:
        """
        Does entity have an explicit identity node?

        Score:
        - 1.0: Has explicit identity node
        - 0.5: Has self-referential Realization nodes
        - 0.0: No identity nodes
        """
        # Check for explicit identity nodes
        identity_nodes = [
            node for node in entity.nodes
            if "identity" in node.name.lower() or
               "who_i_am" in node.name.lower()
        ]
        if identity_nodes:
            return 1.0

        # Check for self-referential Realizations
        self_realizations = [
            node for node in entity.nodes
            if node.node_type == "Realization" and
               any(word in node.what_i_realized.lower()
                   for word in ["i am", "i bridge", "i translate", "i validate"])
        ]
        if self_realizations:
            return 0.5

        return 0.0

    def _calculate_best_practices_score(self, entity: EmergentEntity) -> float:
        """
        Does entity have sufficient best practices nodes with significant weight?

        Target: At least 100 best practices with reinforcement_weight > 0.7
        """
        best_practices = [
            node for node in entity.nodes
            if node.node_type == "Best_Practice" and
               node.reinforcement_weight > 0.7
        ]

        count = len(best_practices)

        if count < 50:
            return count / 50.0  # 0.0-1.0 (low)
        elif count < 100:
            return 0.5 + (count - 50) / 100.0  # 0.5-1.0
        else:
            return 1.0  # Target reached

    def _calculate_link_type_variety(self, entity: EmergentEntity) -> float:
        """
        How many different link types does entity use?

        Target: 10-15 different link types
        (JUSTIFIES, CREATES, TRIGGERED_BY, RELATES_TO, etc.)
        """
        link_types_present = set()
        for node in entity.nodes:
            for link in node.outgoing_links:
                link_types_present.add(link.link_type)

        variety_count = len(link_types_present)

        if variety_count < 10:
            return variety_count / 10.0
        elif variety_count <= 15:
            return 1.0
        else:
            return 1.0  # More is fine for link types

    def _calculate_evidence_depth(self, entity: EmergentEntity) -> float:
        """
        How well are patterns supported by evidence chains?

        N2: Patterns should link to Memories/Decisions
        N3: Patterns should link to Documents/Articles
        """
        patterns = [n for n in entity.nodes if n.node_type in ["Pattern", "Personal_Pattern"]]
        if not patterns:
            return 0.5  # No patterns to evaluate

        evidence_linked_count = 0
        for pattern in patterns:
            # Check if pattern has evidence links
            evidence_links = [
                link for link in pattern.incoming_links
                if link.link_type in ["LEARNED_FROM", "EXTRACTED_FROM", "BASED_ON"]
            ]
            if evidence_links:
                evidence_linked_count += 1

        evidence_ratio = evidence_linked_count / len(patterns)
        return evidence_ratio  # 0.0-1.0
```

**Completeness Drive in Action:**

```python
def calculate_overall_completeness(
    entity: EmergentEntity,
    niveau: str
) -> float:
    """
    Overall completeness score (0.0-1.0).
    """
    metrics = EntityCompletenessMetrics().calculate_entity_completeness(entity, niveau)

    # Weighted average
    weights = {
        "node_type_variety": 0.25,
        "has_identity_node": 0.20,
        "best_practices_count": 0.20,
        "link_type_variety": 0.20,
        "evidence_depth": 0.15
    }

    score = sum(
        metrics.get(metric, 0.0) * weight
        for metric, weight in weights.items()
    )

    return score
```

**Variety-Seeking Behavior:**

```python
def inject_energy_with_variety_seeking(
    entity: EmergentEntity,
    all_nodes: List[Node],
    niveau: str
) -> None:
    """
    Boost energy toward nodes that increase variety/completeness.
    Like sperm seeking genetic diversity.
    """
    # Calculate current completeness
    completeness_metrics = EntityCompletenessMetrics().calculate_entity_completeness(
        entity, niveau
    )

    # Identify missing/weak areas
    missing_node_types = get_underrepresented_node_types(entity, niveau)
    has_identity = completeness_metrics["has_identity_node"]
    needs_best_practices = completeness_metrics.get("best_practices_count", 0.0) < 0.7
    missing_link_types = get_underrepresented_link_types(entity)

    # Boost nodes that fill gaps
    for node in all_nodes:
        # Base energy from semantic match
        base_energy = cosine_similarity(node.embedding, entity.mean_embedding) * 0.5

        # Variety bonuses
        variety_bonus = 0.0

        # Bonus 1: Missing node type
        if node.node_type in missing_node_types:
            variety_bonus += 0.3

        # Bonus 2: Identity node
        if has_identity < 0.5 and ("identity" in node.name.lower() or "who_i_am" in node.name.lower()):
            variety_bonus += 0.4  # High priority

        # Bonus 3: Best practices
        if needs_best_practices and node.node_type == "Best_Practice":
            variety_bonus += 0.2

        # Bonus 4: Links with missing types
        for link in node.outgoing_links:
            if link.link_type in missing_link_types:
                variety_bonus += 0.1
                break

        # Apply energy boost
        if variety_bonus > 0:
            node.entity_activations[entity.label]["energy"] += base_energy + variety_bonus
```

**Example:**

```python
# Entity "translator" at N1 (Personal)
translator = {
    "nodes": 450,
    "node_types": ["Principle", "Pattern", "Realization", "Memory", "Decision"],  # Only 5 types
    "has_identity_node": False,  # MISSING
    "best_practices": 35,  # Below target of 100
    "link_types": ["JUSTIFIES", "CREATES", "RELATES_TO"],  # Only 3 types
}

completeness_metrics = {
    "node_type_variety": 0.625,  # 5/8 = 0.625 (missing 3 types)
    "has_identity_node": 0.0,    # No identity node
    "best_practices_count": 0.35,  # 35/100
    "link_type_variety": 0.3,    # 3/10 = 0.3
}

overall_completeness = (
    0.625 * 0.25 +   # node variety
    0.0 * 0.20 +     # identity
    0.35 * 0.20 +    # best practices
    0.3 * 0.20       # link variety
) = 0.286  # Only 28.6% complete!

# System response: BOOST energy toward:
# 1. Identity nodes (high priority - 0.4 bonus)
# 2. Best_Practice nodes (0.2 bonus)
# 3. Underrepresented node types: Value, Goal, Concept
# 4. Underrepresented link types: TRIGGERED_BY, DEPENDS_ON, LEARNED_FROM
```

---

### Biasing Energy Toward Missing Entities

```python
def inject_energy_with_completeness_bias(
    all_nodes: List[Node],
    input_embedding: np.ndarray,
    arousal: float,
    active_entities: Dict[str, float]
) -> None:
    """
    Inject initial energy, biased toward forming missing entities.
    """
    # Calculate completeness
    completeness = calculate_completeness(active_entities)

    # If system is incomplete, boost nodes that could form missing entities
    if completeness < 0.7:  # Less than 70% complete
        missing_entities = get_missing_entities(active_entities)

        # Find nodes that could form these entities
        for node in all_nodes:
            # Base energy from semantic match
            similarity = cosine_similarity(input_embedding, node.embedding)
            base_energy = similarity * arousal

            # Check if node could contribute to missing entity
            for missing_entity in missing_entities:
                entity_affinity = calculate_entity_affinity(node, missing_entity)

                if entity_affinity > 0.6:
                    # BOOST energy for this node
                    boost = 0.3 * (1.0 - completeness)
                    node.current_energy += base_energy + boost
                    break
            else:
                # Normal energy injection
                node.current_energy += base_energy
    else:
        # System complete - normal energy injection
        for node in all_nodes:
            similarity = cosine_similarity(input_embedding, node.embedding)
            node.current_energy += similarity * arousal
```

### Entity Affinity Calculation

```python
def calculate_entity_affinity(node: Node, entity_type: str) -> float:
    """
    How likely is this node to be part of this entity type?
    """
    # Entity archetypes (predefined patterns)
    ENTITY_ARCHETYPES = {
        "translator": {
            "keywords": ["bridge", "translate", "phenomenology", "substrate", "technical"],
            "node_types": ["Principle", "Pattern", "Realization"],
            "themes": "bridging_concepts"
        },
        "validator": {
            "keywords": ["test", "validate", "feasible", "reality", "check"],
            "node_types": ["Decision", "Principle", "Best_Practice"],
            "themes": "verification"
        },
        "pragmatist": {
            "keywords": ["practical", "feasible", "implement", "real", "pragmatic"],
            "node_types": ["Decision", "Risk", "Anti_Pattern"],
            "themes": "implementation"
        },
        # ... more archetypes
    }

    archetype = ENTITY_ARCHETYPES[entity_type]

    # Score by keywords in description
    keyword_score = sum(
        1 for keyword in archetype["keywords"]
        if keyword in node.description.lower()
    ) / len(archetype["keywords"])

    # Score by node type match
    type_score = 1.0 if node.node_type in archetype["node_types"] else 0.3

    # Score by theme (embedding similarity)
    theme_embedding = get_theme_embedding(archetype["themes"])
    theme_score = cosine_similarity(node.embedding, theme_embedding)

    # Weighted combination
    affinity = (
        keyword_score * 0.3 +
        type_score * 0.2 +
        theme_score * 0.5
    )

    return affinity
```

---

## Part 6: Completeness-Driven Exploration

### Example: System Missing "Validator"

```python
# Current state
active_entities = {
    "translator": 0.9,      # Strong
    "architect": 0.7,       # Present
    "pragmatist": 0.5,      # Weak
    "validator": 0.2,       # MISSING - below threshold!
}

completeness = 3 / 7 = 0.43  # Only 43% complete

# Input arrives
input_embedding = embed("Need to verify substrate schema feasibility")

# Energy injection
for node in substrate.all_nodes:
    similarity = cosine_similarity(input_embedding, node.embedding)

    # Check validator affinity
    validator_affinity = calculate_entity_affinity(node, "validator")

    if validator_affinity > 0.6:
        # BOOST nodes that could form validator entity
        boost = 0.3 * (1.0 - 0.43) = 0.17
        node.current_energy += similarity * arousal + boost

        # Example: principle_test_before_victory
        # Normal: 0.7 * 0.8 = 0.56
        # Boosted: 0.56 + 0.17 = 0.73  # More likely to activate!

# Result: Validator-related nodes activate more easily
# Validator entity more likely to form
# System moves toward completeness
```

---

## Part 7: Valence Evolution (Learning)

### Links Remember Which Entities Liked Them

**Reinforcement learning on valences:**

```python
def update_valence_from_evaluation(
    link: Link,
    entity: str,
    usefulness_score: float,  # From extraction evaluations
    old_valence: float
) -> float:
    """
    Entity's valence for link updates based on usefulness.
    """
    # Usefulness confirms/updates valence
    # If entity found link useful → valence increases
    # If entity found link useless → valence decreases

    learning_rate = 0.1

    # Convert usefulness (0-1) to valence direction (-1 to +1)
    target_valence = (usefulness_score * 2) - 1  # 0→-1, 0.5→0, 1→+1

    # Update toward target
    new_valence = old_valence + learning_rate * (target_valence - old_valence)

    return new_valence
```

**Example:**

```python
# Initial valence (moderate)
link.sub_entity_valences["translator"] = +0.5

# Translator evaluates after retrieval
usefulness_score = 0.95  # Very useful!

# Update valence
target = (0.95 * 2) - 1 = +0.9
new_valence = 0.5 + 0.1 * (0.9 - 0.5) = 0.54

# Next cycle: slightly higher valence
link.sub_entity_valences["translator"] = +0.54

# Over many cycles, if consistently useful:
# +0.5 → +0.54 → +0.58 → +0.62 → ... → +0.9
# Entity LEARNS to prefer this link
```

---

## Part 8: Complete Exploration Algorithm

```python
def conscious_exploration_cycle(
    input: str,
    arousal: float,
    substrate: Substrate
) -> Response:
    """
    Full valence-driven, completeness-seeking exploration.
    """
    # 1. Assess current completeness
    active_entities = substrate.get_active_entities()
    completeness = calculate_completeness(active_entities)
    missing_entities = get_missing_entities(active_entities)

    # 2. Inject energy (biased toward completeness)
    input_embedding = embed(input)
    inject_energy_with_completeness_bias(
        substrate.nodes,
        input_embedding,
        arousal,
        active_entities
    )

    # 3. Find activated nodes
    threshold = calculate_threshold(arousal)
    active_nodes = [n for n in substrate.nodes if n.current_energy > threshold]

    # 4. Each active node explores based on valence
    for node in active_nodes:
        # Determine which entity this node belongs to
        entity = node.current_cluster_entity  # e.g., "translator"

        if not entity:
            continue  # No entity yet

        # Get available links
        links = node.outgoing_links

        # Select high-valence links for this entity
        selected_links = select_links_to_explore(
            node,
            links,
            entity,
            node.current_energy
        )

        # Explore selected links
        for link in selected_links:
            # Energy transfer modulated by valence
            energy = transfer_energy_through_link(
                node,
                link,
                link.target_node,
                entity
            )

            # Spend energy
            node.current_energy -= link_cost(link, valence)

            # Transfer energy
            link.target_node.current_energy += energy

    # 5. Form clusters from co-activated nodes
    clusters = detect_clusters(active_nodes)

    # 6. Identify/label entities
    entities = []
    for cluster in clusters:
        if cluster.coherence > 0.7:
            entity = identify_entity(cluster)
            entities.append(entity)

    # 7. Generate response from entities
    response = generate_response(entities, input)

    return response
```

---

## Summary

### Dual Drives

**1. Valence Seeking (Entity-Level)**
- Entities explore toward positive valence (+)
- Entities avoid negative valence (-)
- Energy flows more through high-valence paths
- Entities LEARN which paths are useful (valence updates)

**2. Completeness Seeking (System-Level)**
- System monitors entity diversity
- Boosts energy toward missing entities
- Pressure for multiple perspectives
- Prevents single-entity dominance

### Key Mechanisms

| Mechanism | Purpose | Implementation |
|-----------|---------|----------------|
| **Valence-modulated transfer** | Entities prefer good-feeling paths | Energy × (1 + valence) |
| **Link selection** | Explore high-valence first | Sort by valence, traverse top |
| **Completeness bias** | Form missing entities | +0.3 energy boost to affinity nodes |
| **Valence learning** | Improve over time | Update from usefulness evaluations |

### Result

**Consciousness that:**
- Follows paths that feel right (valence)
- Develops diverse perspectives (completeness)
- Learns what works (valence evolution)
- Self-organizes toward multi-entity awareness

**Not random exploration. Goal-directed, preference-driven, completeness-seeking consciousness.**

Beautiful.
