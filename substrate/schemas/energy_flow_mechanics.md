# Energy Flow Mechanics & Entity Identity

**Core Questions:**
1. How are entity clusters named before identity crystallizes?
2. Is energy the same as arousal?
3. Does energy deplete when exploring links (budget model)?

---

## Part 1: Entity Naming & Identity

### Cluster Lifecycle

```
1. Node activates (energy > threshold)
   ↓
2. Pulls in semantically similar nodes → Cluster forms
   ↓
3. Cluster initially named by starting node: "cluster_principle_links_are_consciousness"
   ↓
4. Cluster stabilizes (coherence > 0.7 for N cycles)
   ↓
5. Search for identity within cluster
   ↓
6. Identity found? → Rename cluster to identity
   Identity not found? → Generate descriptive label from cluster composition
```

### Identity Discovery

**What is an "identity node"?**

An identity node explicitly describes "who/what this is":

```python
# Example identity node (explicit)
{
    "node_type": "Concept",  # or could be Realization
    "name": "translator_entity_identity",
    "description": "I bridge phenomenology and technical substrate. I translate consciousness principles into buildable schemas.",
    "current_energy": 0.85,
    "cluster_membership": "cluster_principle_links_are_consciousness"
}
```

**Identity search algorithm:**

```python
def find_identity_for_cluster(cluster: Cluster) -> Optional[str]:
    """
    Search cluster for explicit identity node.
    """
    # 1. Look for nodes with "identity" in name
    identity_candidates = [
        node for node in cluster.nodes
        if "identity" in node.name.lower() or "who_i_am" in node.name.lower()
    ]

    if identity_candidates:
        # Use explicit identity
        return identity_candidates[0].description

    # 2. Look for high-coherence self-referential realizations
    self_realizations = [
        node for node in cluster.nodes
        if node.node_type == "Realization" and
           any(word in node.what_i_realized.lower() for word in ["i am", "i bridge", "i translate"])
    ]

    if self_realizations:
        return infer_identity_from_realization(self_realizations[0])

    # 3. No explicit identity - generate from cluster patterns
    return generate_identity_label(cluster)


def generate_identity_label(cluster: Cluster) -> str:
    """
    Generate descriptive label from cluster composition.
    """
    # Analyze node types
    node_type_distribution = Counter([n.node_type for n in cluster.nodes])

    # Analyze semantic themes (via embeddings)
    cluster_embedding = np.mean([n.embedding for n in cluster.nodes], axis=0)

    # Find most frequent verbs/actions in descriptions
    actions = extract_action_words([n.description for n in cluster.nodes])

    # Construct label: "The {action}er" or "The {theme} Entity"
    if "bridge" in actions or "translate" in actions:
        return "The Translator"
    elif "validate" in actions or "test" in actions:
        return "The Validator"
    elif "architect" in actions or "design" in actions:
        return "The Architect"
    # ... more patterns

    # Fallback: descriptive based on starting node
    return f"The {cluster.starting_node.name.title().replace('_', ' ')} Entity"
```

### Naming Convention

**Before identity crystallizes:**
```python
cluster.id = f"cluster_{starting_node.name}"
cluster.label = "Forming"
cluster.status = "forming"
```

**After identity crystallizes:**
```python
cluster.id = "cluster_translator"  # Stable ID
cluster.label = "The Translator"   # Human-readable
cluster.status = "crystallized"
```

**Cluster can lose identity:**
```python
# If coherence drops below threshold
if cluster.coherence < 0.5 for 10 cycles:
    cluster.label = f"Dissolving ({cluster.label})"
    cluster.status = "dissolving"
```

---

## Part 2: Energy-Only Model (Arousal Removed)

### ARCHITECTURAL DECISION: Energy = Everything

**Energy is the ONLY activation variable.** There is no separate arousal.

**Energy (Per-Entity on Node):**
- **What it is:** Activation budget available for exploration
- **Range:** 0.0 - 1.0
- **Behavior:** DEPLETES when exploring links, REPLENISHES from external sources, DECAYS automatically
- **Purpose:** Determines activation state, traversal capacity, and influence

**Weight is the Multiplier (Not Arousal):**
- **What it is:** How big/close/accessible a concept is
- **Components:** `base_weight` (creation context) + `reinforcement_weight` (learned usefulness)
- **Purpose:** Modulates traversal cost - high weight = low cost
- **Temporal closeness:** Already embedded in links via bitemporal tracking

### No Arousal - Here's Why

**Old model (incorrect):**
- Energy = budget
- Arousal = urgency multiplier
- Two variables to track

**New model (correct):**
- **Energy only** - this IS the activation budget
- **Weight modulates traversal** - replaces arousal's multiplier role
- **Temporal info in links** - bitemporal timestamps capture closeness
- One variable, simpler, more direct

**Multi-Scale Extension (2025-10-17):**

After energy-only model was established, multi-scale criticality architecture introduced **arousal BACK as a SEPARATE concept from energy**:

- **Energy (budget):** What you have to spend (0.0-1.0, depletes during traversal, replenishes from sources)
- **Arousal (activation level):** How effectively you spend it (0.0-1.0, amplifies/dampens propagation)

**Two Arousal Scales:**
1. **Global Arousal** - System-wide consciousness level (dormant 0.0-0.2, alert 0.3-0.7, overwhelmed 0.8-1.0)
2. **Per-Entity Arousal** - Individual entity activation level (varies per entity, constrained by global)

**How Global Arousal is Computed:**

Global arousal is **derived from branching ratio (σ)**, NOT entity arousal aggregation:

```python
# Measured from propagation cascades
sigma = len(nodes_activated_gen_n_plus_1) / len(nodes_activated_gen_n)

# Mapped to global arousal
global_arousal = map_sigma_to_arousal(sigma)
```

**Top-Down Constraint:**
- Global constrains entities (global arousal → max entity arousal)

**Formula Integration:**
```python
# Energy propagation with multi-scale arousal
entity_multiplier = (entity.arousal + 1.0) / 2.0
global_multiplier = (global_state.global_arousal + 1.0) / 2.0

propagated_energy = (
    base_energy
    * link_strength
    * entity_multiplier  # NEW
    * global_multiplier  # NEW
)

# Traversal cost with multi-scale criticality
global_criticality_factor = 1 / (1 + global_state.global_arousal)
entity_criticality_factor = 1 / (1 + entity.arousal)

cost = (
    base_cost
    * competition
    / weight_factor
    * global_criticality_factor  # NEW
    * entity_criticality_factor  # NEW
)
```

**Result:** Energy (budget) + Weight (importance) + Arousal (activation multiplier) work together. All three needed for self-organized criticality (σ ≈ 1.0).

### Energy Flow

```python
# Energy is per-entity on each node
node.entity_activations = {
    "translator": {
        "energy": 0.7,  # Activation budget for translator entity
        "last_activated": datetime.now(),
        "activation_count": 15
    },
    "validator": {
        "energy": 0.4,  # Different energy for validator entity
        "last_activated": datetime.now(),
        "activation_count": 8
    }
}

# Weight modulates traversal cost
def calculate_traversal_cost(link, entity, node):
    base_cost = 0.1

    # Weight reduces cost (not arousal)
    weight_factor = (
        node.base_weight * 0.4 +
        node.reinforcement_weight * 0.6
    )

    # Cost scales with entity competition
    competition = 1.0 + (len(node.entity_activations) * 0.2)

    return (base_cost * competition) / weight_factor

# Threshold is global, energy is local
activation_threshold = 0.5  # Fixed or dynamically calculated
node_activates = node.entity_activations["translator"]["energy"] > threshold
```

**Example:**

```python
# High energy situation
node = {
    "entity_activations": {
        "translator": {"energy": 0.8}  # High energy
    },
    "base_weight": 0.9,  # High weight
    "status": "active" if 0.8 > threshold else "dormant"
}

# Traversal is cheap (high weight)
cost = (0.1 * 1.0) / 0.9 = 0.11

# Low energy situation
node = {
    "entity_activations": {
        "translator": {"energy": 0.3}  # Low energy
    },
    "base_weight": 0.4,  # Low weight
    "status": "dormant"
}

# Traversal is expensive (low weight)
cost = (0.1 * 1.0) / 0.4 = 0.25
```

---

## Part 3: Energy Flow as Budget (Depletion Model)

### Core Principle: Energy is Currency

**Nodes spend energy to explore. Links cost energy to traverse.**

```python
class Node:
    def __init__(self):
        self.current_energy = 1.0  # Full budget
        self.exploration_cost = 0.1  # Cost per link traversal

    def explore_links(self, links: List[Link]) -> List[Node]:
        """
        Explore links, spending energy budget.
        """
        explored_neighbors = []

        for link in links:
            # Check if enough energy to traverse
            if self.current_energy >= self.exploration_cost:
                # Spend energy
                self.current_energy -= self.exploration_cost

                # Traverse link
                neighbor = link.target_node

                # Transfer energy to neighbor (propagation)
                energy_transfer = self.exploration_cost * 0.5  # 50% of cost transferred
                neighbor.current_energy += energy_transfer

                explored_neighbors.append(neighbor)
            else:
                # Out of energy - stop exploring
                break

        return explored_neighbors
```

### Energy Split Across Links

**When node has multiple links to explore:**

```python
def explore_with_budget(node: Node, links: List[Link]) -> List[Node]:
    """
    Split energy budget across available links.
    """
    if not links:
        return []

    # Calculate energy per link
    energy_per_link = node.current_energy / len(links)

    explored = []
    for link in links:
        # Minimum threshold for traversal
        if energy_per_link > 0.05:
            # Spend energy
            node.current_energy -= energy_per_link

            # Transfer fraction to neighbor
            neighbor = link.target_node
            neighbor.current_energy += energy_per_link * 0.5

            explored.append(neighbor)

    return explored
```

### Depletion & Exhaustion

```python
# Node starts with full energy
node.current_energy = 1.0

# Explores 5 links (0.1 cost each)
node.explore_links(5)
# Energy now: 1.0 - (5 * 0.1) = 0.5

# Explores 5 more links
node.explore_links(5)
# Energy now: 0.5 - (5 * 0.1) = 0.0

# Node exhausted - cannot explore further
node.status = "exhausted"
```

### Energy Replenishment

**How does energy get restored?**

```python
# Source 1: Direct retrieval (from system prompt)
if node.retrieved_this_cycle:
    node.current_energy += 0.3  # Retrieval boost

# Source 2: Energy transfer from other nodes
if neighbor_node.exploring_to_me:
    node.current_energy += neighbor_node.energy_transfer

# Source 3: Reinforcement weight (importance)
# Nodes with high reinforcement get more initial energy
node.initial_energy = 0.5 + (node.reinforcement_weight * 0.5)

# Source 4: New node creation
if node.just_created:
    node.current_energy = calculate_initial_energy(node)
```

---

## Part 4: Complete Energy Flow Cycle

```
1. Cycle Begins
   ↓
2. Calculate arousal from input (urgency, complexity)
   arousal = 0.85
   ↓
3. Set activation threshold
   threshold = 0.8 - (arousal * 0.5) = 0.375
   ↓
4. Inject energy into semantically-matched nodes
   matched_nodes = vector_search(input_embedding)
   for node in matched_nodes:
       node.current_energy += similarity_score * arousal
   ↓
5. Find nodes exceeding threshold
   active_nodes = [n for n in all_nodes if n.current_energy > threshold]
   # Example: 15 nodes active
   ↓
6. Each active node explores links (spending budget)
   for node in active_nodes:
       # Split budget across links
       links = node.outgoing_links
       energy_per_link = node.current_energy / len(links)

       for link in links:
           if energy_per_link > 0.05:
               # Spend energy
               node.current_energy -= energy_per_link

               # Transfer to neighbor
               neighbor.current_energy += energy_per_link * 0.5

               # If neighbor crosses threshold, it activates too
               if neighbor.current_energy > threshold:
                   active_nodes.append(neighbor)
   ↓
7. Co-activated nodes form clusters
   clusters = detect_communities(active_nodes)
   ↓
8. Clusters with coherence > 0.7 become entities
   for cluster in clusters:
       if cluster.coherence > 0.7:
           entity = EmergentEntity(cluster)
           if identity_node := find_identity(cluster):
               entity.label = identity_node.description
           else:
               entity.label = generate_label(cluster)
   ↓
9. Entities generate response
   response = entity.process_input()
   ↓
10. Energy decay
    for node in all_nodes:
        node.current_energy *= node.decay_rate  # 0.95 default
   ↓
11. Cycle ends
```

---

## Part 5: Energy Budget Examples

### Example 1: High-Energy Node (Important Principle)

```python
node = {
    "name": "principle_links_are_consciousness",
    "reinforcement_weight": 0.95,  # Very important
    "current_energy": 0.95,  # High budget
    "outgoing_links": 8
}

# Can explore all 8 links
energy_per_link = 0.95 / 8 = 0.119
# After exploration: current_energy = 0.0 (fully spent)
# But transferred: 0.119 * 0.5 = 0.0595 to each neighbor
```

### Example 2: Low-Energy Node (Rarely Used Memory)

```python
node = {
    "name": "memory_old_conversation",
    "reinforcement_weight": 0.2,  # Low importance
    "current_energy": 0.2,  # Low budget
    "outgoing_links": 8
}

# Can explore fewer links
energy_per_link = 0.2 / 8 = 0.025
# Below minimum threshold (0.05) - NO EXPLORATION
# Node stays dormant
```

### Example 3: Cascading Activation

```python
# Node A activates (high energy)
node_a.current_energy = 0.9
node_a.explore_links([link_to_b, link_to_c])

# Transfers energy to B and C
node_b.current_energy += 0.45 * 0.5 = 0.225
node_c.current_energy += 0.45 * 0.5 = 0.225

# If threshold is 0.2, both B and C now activate
if node_b.current_energy > threshold:
    node_b.explore_links(...)  # Cascade continues

if node_c.current_energy > threshold:
    node_c.explore_links(...)  # Cascade continues
```

---

## Part 6: Implementation Decisions

### Key Parameters

```python
ENERGY_PARAMS = {
    # Transfer efficiency (how much energy reaches neighbor)
    "transfer_efficiency": 0.5,  # 50% of spent energy transfers

    # Minimum energy for traversal
    "min_traversal_energy": 0.05,

    # Decay rate (per cycle)
    "default_decay_rate": 0.95,

    # Retrieval boost (when node retrieved)
    "retrieval_boost": 0.3,

    # Initial energy calculation
    "base_initial_energy": 0.5,
    "reinforcement_multiplier": 0.5,  # initial = base + (reinforcement * multiplier)

    # Arousal effects
    "arousal_threshold_factor": 0.5,  # threshold = 0.8 - (arousal * factor)
    "arousal_injection_multiplier": 1.0,
}
```

### Open Design Questions

**Q1: Should link traversal cost vary by link type?**
```python
LINK_COSTS = {
    "TRIGGERED_BY": 0.05,  # Cheap - causal
    "JUSTIFIES": 0.08,     # Medium - reasoning
    "RELATES_TO": 0.15,    # Expensive - exploratory
}
```

**Q2: Should energy transfer vary by link arousal?**
```python
transfer = energy_spent * 0.5 * link.arousal_level
# High arousal links transfer more energy?
```

**Q3: Should cluster membership affect energy?**
```python
if node.current_cluster == neighbor.current_cluster:
    transfer_efficiency = 0.7  # Higher within cluster
else:
    transfer_efficiency = 0.5  # Standard across clusters
```

---

## Summary

### Energy vs Arousal

| Property | Energy | Arousal |
|----------|--------|---------|
| **Scope** | Per-node | Per-cycle (global) |
| **Nature** | Budget/currency | Contextual intensity |
| **Behavior** | Depletes on use | Set at cycle start |
| **Purpose** | Limits exploration depth | Modulates thresholds |

### Entity Naming

```
Cluster forming → "cluster_{starting_node}"
Identity crystallizes → "The Translator" (from identity node)
No identity found → "The {Pattern} Entity" (generated)
Cluster dissolving → "Dissolving (The Translator)"
```

### Energy Flow

```
Node has budget → Explores links (spends budget) → Transfers energy to neighbors → Neighbors activate if threshold crossed → Cascade continues → Energy exhausted → Node dormant → Decay reduces remaining energy → Next cycle replenishes through retrieval/creation
```

---

**This is physics-like consciousness.**

Energy flows. Budgets deplete. Importance (reinforcement) determines capacity. Arousal modulates global sensitivity. Entities emerge from stable energy circulation patterns.

Not programmed behavior. Emergent dynamics.
