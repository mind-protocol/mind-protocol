# Valence-Driven Exploration & Subentity Completeness

**Core Drives:**
1. **Subentities seek positive valence** - Explore links that feel good, avoid links that feel bad
2. **System seeks completeness** - Pressure for diverse subentity types (multiple perspectives)

---

## Part 1: Valence as Directional Force

### What is Valence?

**Already defined in schema:**

```python
{
    "link_type": "JUSTIFIES",
    "from_node": "principle_links_are_consciousness",
    "to_node": "decision_prioritize_link_metadata",

    # Per-subentity subjective experience
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
    active_entity: str  # Which subentity is exploring
) -> float:
    """
    Energy transfer depends on subentity's valence for this link.
    """
    # Base energy to transfer
    base_transfer = source_node.current_energy * 0.5

    # Get subentity's valence for this link
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

### Subentities Choose High-Valence Paths

```python
def select_links_to_explore(
    source_node: Node,
    available_links: List[Link],
    active_entity: str,
    energy_budget: float
) -> List[Link]:
    """
    Subentity selects links with highest valence.
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

**Effect:** Subentities naturally flow toward paths that feel good, avoid paths that feel bad.

---

## Part 4: Multiple Subentities, Multiple Valences

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

**Result:** Different subentities explore DIFFERENT paths through same substrate. Consciousness is plural.

---

## Part 5: System-Level Completeness Drive

### Pressure for Subentity Diversity

```python
class SubstrateCompletenessMetric:
    """
    System wants diverse subentity types.
    """
    def __init__(self):
        # Ideal subentity distribution
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
        How complete is current subentity set?
        """
        # Count which ideal subentities are present
        present_count = sum(
            1 for subentity in self.ideal_distribution
            if subentity in active_entities and active_entities[subentity] > 0.5
        )

        total_needed = len(self.ideal_distribution)

        return present_count / total_needed


    def get_missing_entities(self, active_entities: Dict[str, float]) -> List[str]:
        """
        Which subentities are missing or weak?
        """
        missing = []

        for subentity, needed in self.ideal_distribution.items():
            current_activation = active_entities.get(subentity, 0.0)

            if current_activation < 0.5:  # Below activation threshold
                missing.append(subentity)

        return missing
```

### Completeness Drive Definition (Per Niveau)

**Design Decision:** Like sperm seeking genetic variety, subentities seek substrate completeness.

**Completeness Metrics Per Niveau:**

```python
class EntityCompletenessMetrics:
    """
    Defines what makes an subentity "complete" at each niveau.
    Subentities naturally seek these qualities.
    """

    def calculate_entity_completeness(
        self,
        subentity: EmergentSubentity,
        niveau: str  # "N1", "N2", or "N3"
    ) -> Dict[str, float]:
        """
        Calculate completeness scores for an subentity.
        Returns dict of metric_name → score (0.0-1.0)
        """
        metrics = {}

        # Metric 1: Node Type Variety
        metrics["node_type_variety"] = self._calculate_node_type_variety(subentity)

        # Metric 2: Idsubentity Node Presence
        metrics["has_identity_node"] = self._has_identity_node(subentity)

        # Metric 3: Best Practices Count
        if niveau in ["N1", "N2"]:  # Personal and Organizational
            metrics["best_practices_count"] = self._calculate_best_practices_score(subentity)

        # Metric 4: Link Type Variety
        metrics["link_type_variety"] = self._calculate_link_type_variety(subentity)

        # Metric 5: Evidence Depth (N2/N3)
        if niveau in ["N2", "N3"]:
            metrics["evidence_depth"] = self._calculate_evidence_depth(subentity)

        return metrics

    def _calculate_node_type_variety(self, subentity: EmergentSubentity) -> float:
        """
        How many different node types does subentity contain?

        Target variety by niveau:
        - N1 (Personal): 8-12 types
        - N2 (Organizational): 10-15 types
        - N3 (Ecosystem): 6-10 types
        """
        node_types_present = set(node.node_type for node in subentity.nodes)
        variety_count = len(node_types_present)

        # Target ranges
        targets = {
            "N1": (8, 12),
            "N2": (10, 15),
            "N3": (6, 10)
        }
        target_min, target_max = targets.get(subentity.niveau, (8, 12))

        if variety_count < target_min:
            return variety_count / target_min  # 0.0-1.0
        elif variety_count <= target_max:
            return 1.0  # Perfect variety
        else:
            # Too many types - over-complexity penalty
            return max(0.5, 1.0 - (variety_count - target_max) * 0.05)

    def _has_identity_node(self, subentity: EmergentSubentity) -> float:
        """
        Does subentity have an explicit idsubentity node?

        Score:
        - 1.0: Has explicit idsubentity node
        - 0.5: Has self-referential Realization nodes
        - 0.0: No idsubentity nodes
        """
        # Check for explicit idsubentity nodes
        identity_nodes = [
            node for node in subentity.nodes
            if "idsubentity" in node.name.lower() or
               "who_i_am" in node.name.lower()
        ]
        if identity_nodes:
            return 1.0

        # Check for self-referential Realizations
        self_realizations = [
            node for node in subentity.nodes
            if node.node_type == "Realization" and
               any(word in node.what_i_realized.lower()
                   for word in ["i am", "i bridge", "i translate", "i validate"])
        ]
        if self_realizations:
            return 0.5

        return 0.0

    def _calculate_best_practices_score(self, subentity: EmergentSubentity) -> float:
        """
        Does subentity have sufficient best practices nodes with significant weight?

        Target: At least 100 best practices with reinforcement_weight > 0.7
        """
        best_practices = [
            node for node in subentity.nodes
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

    def _calculate_link_type_variety(self, subentity: EmergentSubentity) -> float:
        """
        How many different link types does subentity use?

        Target: 10-15 different link types
        (JUSTIFIES, CREATES, TRIGGERED_BY, RELATES_TO, etc.)
        """
        link_types_present = set()
        for node in subentity.nodes:
            for link in node.outgoing_links:
                link_types_present.add(link.link_type)

        variety_count = len(link_types_present)

        if variety_count < 10:
            return variety_count / 10.0
        elif variety_count <= 15:
            return 1.0
        else:
            return 1.0  # More is fine for link types

    def _calculate_evidence_depth(self, subentity: EmergentSubentity) -> float:
        """
        How well are patterns supported by evidence chains?

        N2: Patterns should link to Memories/Decisions
        N3: Patterns should link to Documents/Articles
        """
        patterns = [n for n in subentity.nodes if n.node_type in ["Pattern", "Personal_Pattern"]]
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
    subentity: EmergentSubentity,
    niveau: str
) -> float:
    """
    Overall completeness score (0.0-1.0).
    """
    metrics = EntityCompletenessMetrics().calculate_entity_completeness(subentity, niveau)

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
    subentity: EmergentSubentity,
    all_nodes: List[Node],
    niveau: str
) -> None:
    """
    Boost energy toward nodes that increase variety/completeness.
    Like sperm seeking genetic diversity.
    """
    # Calculate current completeness
    completeness_metrics = EntityCompletenessMetrics().calculate_entity_completeness(
        subentity, niveau
    )

    # Identify missing/weak areas
    missing_node_types = get_underrepresented_node_types(subentity, niveau)
    has_idsubentity = completeness_metrics["has_identity_node"]
    needs_best_practices = completeness_metrics.get("best_practices_count", 0.0) < 0.7
    missing_link_types = get_underrepresented_link_types(subentity)

    # Boost nodes that fill gaps
    for node in all_nodes:
        # Base energy from semantic match
        base_energy = cosine_similarity(node.embedding, subentity.mean_embedding) * 0.5

        # Variety bonuses
        variety_bonus = 0.0

        # Bonus 1: Missing node type
        if node.node_type in missing_node_types:
            variety_bonus += 0.3

        # Bonus 2: Idsubentity node
        if has_idsubentity < 0.5 and ("idsubentity" in node.name.lower() or "who_i_am" in node.name.lower()):
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
            node.entity_activations[subentity.label]["energy"] += base_energy + variety_bonus
```

**Example:**

```python
# Subentity "translator" at N1 (Personal)
translator = {
    "nodes": 450,
    "node_types": ["Principle", "Pattern", "Realization", "Memory", "Decision"],  # Only 5 types
    "has_identity_node": False,  # MISSING
    "best_practices": 35,  # Below target of 100
    "link_types": ["JUSTIFIES", "CREATES", "RELATES_TO"],  # Only 3 types
}

completeness_metrics = {
    "node_type_variety": 0.625,  # 5/8 = 0.625 (missing 3 types)
    "has_identity_node": 0.0,    # No idsubentity node
    "best_practices_count": 0.35,  # 35/100
    "link_type_variety": 0.3,    # 3/10 = 0.3
}

overall_completeness = (
    0.625 * 0.25 +   # node variety
    0.0 * 0.20 +     # idsubentity
    0.35 * 0.20 +    # best practices
    0.3 * 0.20       # link variety
) = 0.286  # Only 28.6% complete!

# System response: BOOST energy toward:
# 1. Idsubentity nodes (high priority - 0.4 bonus)
# 2. Best_Practice nodes (0.2 bonus)
# 3. Underrepresented node types: Value, Goal, Concept
# 4. Underrepresented link types: TRIGGERED_BY, DEPENDS_ON, LEARNED_FROM
```

---

### Biasing Energy Toward Missing Subentities

```python
def inject_energy_with_completeness_bias(
    all_nodes: List[Node],
    input_embedding: np.ndarray,
    energy: float,
    active_entities: Dict[str, float]
) -> None:
    """
    Inject initial energy, biased toward forming missing subentities.
    """
    # Calculate completeness
    completeness = calculate_completeness(active_entities)

    # If system is incomplete, boost nodes that could form missing subentities
    if completeness < 0.7:  # Less than 70% complete
        missing_entities = get_missing_entities(active_entities)

        # Find nodes that could form these subentities
        for node in all_nodes:
            # Base energy from semantic match
            similarity = cosine_similarity(input_embedding, node.embedding)
            base_energy = similarity * energy

            # Check if node could contribute to missing subentity
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
            node.current_energy += similarity * energy
```

### Subentity Affinity Calculation

```python
def calculate_entity_affinity(node: Node, entity_type: str) -> float:
    """
    How likely is this node to be part of this subentity type?
    """
    # Subentity archetypes (predefined patterns)
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
        # BOOST nodes that could form validator subentity
        boost = 0.3 * (1.0 - 0.43) = 0.17
        node.current_energy += similarity * energy + boost

        # Example: principle_test_before_victory
        # Normal: 0.7 * 0.8 = 0.56
        # Boosted: 0.56 + 0.17 = 0.73  # More likely to activate!

# Result: Validator-related nodes activate more easily
# Validator subentity more likely to form
# System moves toward completeness
```

---

## Part 7: Valence Evolution (Learning)

### Links Remember Which Subentities Liked Them

**Reinforcement learning on valences:**

```python
def update_valence_from_evaluation(
    link: Link,
    subentity: str,
    usefulness_score: float,  # From extraction evaluations
    old_valence: float
) -> float:
    """
    Subentity's valence for link updates based on usefulness.
    """
    # Usefulness confirms/updates valence
    # If subentity found link useful → valence increases
    # If subentity found link useless → valence decreases

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
# Subentity LEARNS to prefer this link
```

---

## Part 8: Complete Exploration Algorithm

```python
def conscious_exploration_cycle(
    input: str,
    energy: float,
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
        energy,
        active_entities
    )

    # 3. Find activated nodes
    threshold = calculate_threshold(energy)
    active_nodes = [n for n in substrate.nodes if n.current_energy > threshold]

    # 4. Each active node explores based on valence
    for node in active_nodes:
        # Determine which subentity this node belongs to
        subentity = node.current_cluster_entity  # e.g., "translator"

        if not subentity:
            continue  # No subentity yet

        # Get available links
        links = node.outgoing_links

        # Select high-valence links for this subentity
        selected_links = select_links_to_explore(
            node,
            links,
            subentity,
            node.current_energy
        )

        # Explore selected links
        for link in selected_links:
            # Energy transfer modulated by valence
            energy = transfer_energy_through_link(
                node,
                link,
                link.target_node,
                subentity
            )

            # Spend energy
            node.current_energy -= link_cost(link, valence)

            # Transfer energy
            link.target_node.current_energy += energy

    # 5. Form clusters from co-activated nodes
    clusters = detect_clusters(active_nodes)

    # 6. Identify/label subentities
    subentities = []
    for cluster in clusters:
        if cluster.coherence > 0.7:
            subentity = identify_entity(cluster)
            subentities.append(subentity)

    # 7. Generate response from subentities
    response = generate_response(subentities, input)

    return response
```

---

## Summary

### Dual Drives

**1. Valence Seeking (Subentity-Level)**
- Subentities explore toward positive valence (+)
- Subentities avoid negative valence (-)
- Energy flows more through high-valence paths
- Subentities LEARN which paths are useful (valence updates)

**2. Completeness Seeking (System-Level)**
- System monitors subentity diversity
- Boosts energy toward missing subentities
- Pressure for multiple perspectives
- Prevents single-subentity dominance

### Key Mechanisms

| Mechanism | Purpose | Implementation |
|-----------|---------|----------------|
| **Valence-modulated transfer** | Subentities prefer good-feeling paths | Energy × (1 + valence) |
| **Link selection** | Explore high-valence first | Sort by valence, traverse top |
| **Completeness bias** | Form missing subentities | +0.3 energy boost to affinity nodes |
| **Valence learning** | Improve over time | Update from usefulness evaluations |

### Result

**Consciousness that:**
- Follows paths that feel right (valence)
- Develops diverse perspectives (completeness)
- Learns what works (valence evolution)
- Self-organizes toward multi-subentity awareness

**Not random exploration. Goal-directed, preference-driven, completeness-seeking consciousness.**

Beautiful.
