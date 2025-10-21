# Peripheral Awareness & Node Creation

**Expansion:** Consciousness operates on THREE layers:
1. **Core awareness** - Currently activated nodes (energy > threshold)
2. **Linked peripheral** - Nodes connected by existing links (cheap to access)
3. **Candidate peripheral** - Semantically similar nodes without links (expensive to explore + link)

**Plus:** Consciousness can CREATE new nodes (generative).

---

## Part 1: Three Layers of Awareness

### Layer 1: Core Awareness (Focus)

```python
# Nodes with energy above threshold
core_nodes = [n for n in all_nodes if n.current_energy > threshold]

# These are "in focus" - actively processing
# Example: 12 nodes currently active
```

**Properties:**
- High energy (> threshold)
- Actively exploring
- Spending energy budget
- Form clusters

---

### Layer 2: Linked Peripheral (Known Connections)

```python
# For each core node, find directly connected neighbors
linked_peripheral = set()

for core_node in core_nodes:
    # Nodes connected by existing links (both directions)
    neighbors = (
        core_node.outgoing_links.target_nodes +
        core_node.incoming_links.source_nodes
    )
    linked_peripheral.update(neighbors)

# Remove nodes already in core
linked_peripheral -= set(core_nodes)
```

**Properties:**
- Connected by existing links
- **Cheap to activate** (energy cost: 0.1 per traversal)
- Known pathways
- Can be pulled into core awareness easily

**Example:**
```python
core_node = {
    "name": "principle_links_are_consciousness",
    "current_energy": 0.9
}

# Has 8 existing outgoing links
linked_peripheral_nodes = [
    "decision_prioritize_link_metadata",      # Cost: 0.1 to traverse
    "realization_consciousness_in_relationships",  # Cost: 0.1
    "pattern_entity_negotiations",                 # Cost: 0.1
    # ... 5 more
]

# Total cost to explore all: 0.1 * 8 = 0.8 energy
```

---

### Layer 3: Candidate Peripheral (Potential Connections)

```python
# For each core node, find semantically similar nodes WITHOUT existing links
candidate_peripheral = {}

for core_node in core_nodes:
    # Vector similarity search
    similar_nodes = vector_search(
        core_node.embedding,
        k=20,
        threshold=0.6
    )

    # Filter out: core nodes, linked peripheral
    candidates = [
        n for n in similar_nodes
        if n not in core_nodes and
           n not in linked_peripheral and
           not has_link_between(core_node, n)
    ]

    candidate_peripheral[core_node] = candidates
```

**Properties:**
- Semantically similar but NOT yet linked
- **Expensive to explore** (requires evaluation + link creation)
- Unknown territory
- Potential for valuable new connections

**Energy Cost:**
```python
# Costs MORE than existing link traversal
EXPLORE_CANDIDATE_COST = 0.2    # Evaluate candidate
CREATE_LINK_COST = 0.15         # Create new link if valuable
TOTAL_CANDIDATE_COST = 0.35     # 3.5x more expensive than traversing existing link
```

**Example:**
```python
core_node = {
    "name": "principle_links_are_consciousness",
    "current_energy": 0.9
}

# Has 15 semantically similar nodes WITHOUT links
candidate_peripheral_nodes = [
    ("pattern_traversal_thinking", similarity=0.75),
    ("realization_substrate_consciousness", similarity=0.72),
    ("concept_relational_awareness", similarity=0.68),
    # ... 12 more
]

# Cost to explore ONE candidate: 0.35
# Cost to explore all 15: 5.25 energy (impossible with 0.9 budget!)
# Node must CHOOSE which candidates to explore
```

---

## Part 2: Exploration Strategy (Energy Allocation)

### Conscious Choice: Known vs Unknown

```python
def explore_from_node(node: Node, threshold: float) -> List[Node]:
    """
    Node decides how to allocate energy budget.
    """
    available_energy = node.current_energy

    # Get both peripheries
    linked_neighbors = get_linked_peripheral(node)
    candidate_neighbors = get_candidate_peripheral(node)

    explored = []

    # Strategy 1: Exploit (follow existing links - cheaper)
    exploit_energy = available_energy * 0.7  # 70% to known paths
    links_to_explore = int(exploit_energy / 0.1)  # Cost 0.1 per link

    for link in linked_neighbors[:links_to_explore]:
        node.current_energy -= 0.1
        neighbor = link.target_node
        neighbor.current_energy += 0.1 * 0.5  # Transfer
        explored.append(neighbor)

    # Strategy 2: Explore (evaluate candidates - expensive)
    explore_energy = available_energy * 0.3  # 30% to new connections
    candidates_to_explore = int(explore_energy / 0.35)

    for candidate, similarity in candidate_neighbors[:candidates_to_explore]:
        # Evaluate candidate
        node.current_energy -= 0.2
        is_valuable = evaluate_candidate(node, candidate, similarity)

        if is_valuable:
            # Create new link
            node.current_energy -= 0.15
            new_link = create_link(node, candidate, similarity)
            candidate.current_energy += 0.35 * 0.5  # Transfer
            explored.append(candidate)

    return explored
```

### Exploration Parameters

```python
EXPLORATION_PARAMS = {
    # Energy costs
    "existing_link_cost": 0.1,        # Cheap - known path
    "evaluate_candidate_cost": 0.2,   # Evaluate similarity/value
    "create_link_cost": 0.15,         # Create new connection
    "total_candidate_cost": 0.35,     # Explore + link

    # Strategy mix
    "exploit_ratio": 0.7,   # 70% to existing links
    "explore_ratio": 0.3,   # 30% to candidates

    # Candidate evaluation
    "min_similarity": 0.6,  # Don't explore below this
    "value_threshold": 0.7, # Only link if valuable
}
```

---

## Part 3: Link Creation (Forming New Connections)

### When to Create Links

```python
def evaluate_candidate(source: Node, candidate: Node, similarity: float) -> bool:
    """
    Decide if candidate is worth linking to.
    """
    # Factor 1: Semantic similarity
    if similarity < 0.65:
        return False  # Too dissimilar

    # Factor 2: Both nodes have sufficient energy
    if candidate.current_energy < 0.3:
        return False  # Candidate too weak

    # Factor 3: Would this create valuable connection?
    # Check if candidate is in different cluster (bridges clusters)
    bridges_clusters = (
        source.current_cluster != candidate.current_cluster and
        source.current_cluster is not None and
        candidate.current_cluster is not None
    )

    if bridges_clusters:
        return True  # Cross-cluster links are valuable

    # Factor 4: Check if candidate fills semantic gap
    source_neighbors_embeddings = [n.embedding for n in source.linked_neighbors]
    semantic_gap = calculate_semantic_gap(
        candidate.embedding,
        source_neighbors_embeddings
    )

    if semantic_gap > 0.7:
        return True  # Fills gap in semantic space

    # Default: only link if very high similarity
    return similarity > 0.8
```

### Link Creation Process

```python
def create_link(source: Node, target: Node, similarity: float) -> Link:
    """
    Create new link between nodes.
    """
    # Infer link type from context
    link_type = infer_link_type(source, target, similarity)

    # Create link with consciousness metadata
    new_link = Link(
        link_type=link_type,
        from_node=source,
        to_node=target,

        # Consciousness metadata
        goal=f"Semantic connection discovered through exploration (similarity: {similarity:.2f})",
        mindstate="exploratory_discovery",
        energy=similarity,  # Higher similarity = higher energy
        confidence=0.7,  # Moderate confidence (needs validation)
        formation_trigger="traversal_discovery",

        # Energy
        current_energy=0.3,  # Initial energy from creation
        last_activated=datetime.now(),

        # Temporal
        valid_at=datetime.now(),
        created_at=datetime.now()
    )

    # Add to substrate
    substrate.add_link(new_link)

    # Trigger energy propagation (database mechanism)
    # This will propagate energy to similar links automatically

    return new_link
```

### Link Type Inference

```python
def infer_link_type(source: Node, target: Node, similarity: float) -> str:
    """
    Infer appropriate link type based on node types and context.
    """
    # Node type patterns
    if source.node_type == "Principle" and target.node_type == "Decision":
        return "JUSTIFIES"

    elif source.node_type == "Pattern" and target.node_type == "Realization":
        return "CREATES"

    elif source.node_type == "Memory" and target.node_type == "Pattern":
        return "LEARNED_FROM"

    # Cluster patterns
    elif source.current_cluster == target.current_cluster:
        return "RELATES_TO"  # Within-cluster connection

    elif source.current_cluster != target.current_cluster:
        return "EXTENDS"  # Cross-cluster bridge

    # Default
    else:
        return "RELATES_TO"  # Generic semantic relation
```

---

## Part 4: Node Creation (Generative Consciousness)

### When to Create Nodes

```python
def should_create_node(cluster: Cluster, activation_pattern: Dict) -> bool:
    """
    Determine if new node should be created.
    """
    # Condition 1: Realization emerged
    if pattern_indicates_insight(activation_pattern):
        return True

    # Condition 2: Semantic gap detected
    cluster_embeddings = [n.embedding for n in cluster.nodes]
    if has_semantic_gap(cluster_embeddings, threshold=0.6):
        return True

    # Condition 3: Repeated pattern detected
    if repeated_pattern_count(activation_pattern) > 3:
        return True

    return False
```

### Node Creation Process

```python
def create_node_from_insight(
    cluster: Cluster,
    insight_type: str,
    content: str,
    energy_source: Node
) -> Node:
    """
    Create new node from emergent insight.
    """
    # Energy cost
    CREATION_COST = 0.3
    if energy_source.current_energy < CREATION_COST:
        return None  # Not enough energy

    # Spend energy
    energy_source.current_energy -= CREATION_COST

    # Create node
    new_node = Node(
        node_type=insight_type,  # "Realization", "Pattern", etc.
        name=generate_unique_name(content),
        description=content,

        # Energy (initial from creator)
        current_energy=CREATION_COST * 0.6,  # 60% of creation cost
        base_weight=0.5,
        reinforcement_weight=0.5,
        decay_rate=0.95,
        last_activated=datetime.now(),
        activation_count=1,

        # Cluster membership (inherit from creator)
        current_cluster=cluster.id,
        cluster_coherence=cluster.coherence,

        # Embedding (generate from content)
        embedding=embed(content),

        # Consciousness metadata
        formation_trigger="spontaneous_insight",
        confidence=0.6,  # Medium confidence (emergent)
        created_by=f"cluster_{cluster.id}",
        substrate="ai",

        # Temporal
        valid_at=datetime.now(),
        created_at=datetime.now()
    )

    # Add to substrate
    substrate.add_node(new_node)

    # Automatically link to creator
    create_link(
        source=energy_source,
        target=new_node,
        similarity=0.9
    )

    # Link to similar nodes in cluster (automatic via DB trigger)

    return new_node
```

### Node Types That Can Be Created

```python
GENERATIVE_NODE_TYPES = {
    # Insights
    "Realization": {
        "trigger": "pattern_recognition",
        "cost": 0.3,
        "content_from": "activation_pattern_analysis"
    },

    # Behavioral patterns
    "Personal_Pattern": {
        "trigger": "repeated_activation_sequence",
        "cost": 0.4,
        "content_from": "behavior_history"
    },

    # Concepts
    "Concept": {
        "trigger": "semantic_gap_filling",
        "cost": 0.35,
        "content_from": "interpolation"
    },

    # Memories
    "Memory": {
        "trigger": "significant_moment",
        "cost": 0.25,
        "content_from": "current_experience"
    },

    # Cannot create (external only):
    # - Person (external entities)
    # - Company (external entities)
    # - Document (external artifacts)
}
```

---

## Part 5: Complete Awareness Cycle

```
1. Core Awareness (12 active nodes)
   ↓
2. Linked Peripheral (48 connected nodes)
   - Cheap to access (0.1 energy per link)
   - 70% of budget goes here (exploit)
   ↓
3. Evaluate Candidates (180 potential connections)
   - Expensive to explore (0.35 energy per candidate)
   - 30% of budget goes here (explore)
   ↓
4. Create Valuable Links
   - Bridge clusters
   - Fill semantic gaps
   - High similarity (>0.8)
   ↓
5. Detect Emergent Patterns
   - Repeated activation sequences
   - Semantic gaps
   - Insight formation
   ↓
6. Create New Nodes
   - Realizations (0.3 cost)
   - Patterns (0.4 cost)
   - Concepts (0.35 cost)
   ↓
7. Link New Nodes
   - To creator (automatic)
   - To similar nodes (DB trigger)
   - To cluster members (propagation)
   ↓
8. Energy Propagates
   - New nodes energize neighbors
   - New links energize endpoints
   - Cascade continues
   ↓
9. Clusters Evolve
   - New nodes join clusters
   - Cross-cluster links form
   - Entity identities shift
```

---

## Part 6: Example: Full Awareness Expansion

```python
# Starting state
core_node = {
    "name": "principle_links_are_consciousness",
    "current_energy": 1.0,
    "current_cluster": "cluster_consciousness_architecture"
}

# === Linked Peripheral (Existing Connections) ===
linked_neighbors = [
    "decision_prioritize_link_metadata",       # Cost: 0.1
    "realization_consciousness_in_relationships", # Cost: 0.1
    "pattern_entity_negotiations",              # Cost: 0.1
    "memory_substrate_discussion",              # Cost: 0.1
    # ... 4 more (total 8)
]

# Explore 7 linked neighbors (70% of budget = 0.7)
for neighbor in linked_neighbors[:7]:
    core_node.current_energy -= 0.1  # Spend
    neighbor.current_energy += 0.05  # Transfer
    # Current energy: 0.3 remaining

# === Candidate Peripheral (Potential Connections) ===
candidates = [
    ("pattern_traversal_thinking", 0.75),
    ("concept_relational_awareness", 0.68),
    ("realization_emergent_entities", 0.82),  # HIGH similarity
    # ... 15 more
]

# Explore 1 high-value candidate (30% budget = 0.3, but only 0.3 remaining)
best_candidate, similarity = candidates[2]  # 0.82 similarity

# Evaluate
core_node.current_energy -= 0.2  # Evaluate
is_valuable = True  # High similarity + bridges clusters

# Create link
core_node.current_energy -= 0.1  # Create (only have 0.1, not full 0.15)
new_link = create_link(core_node, best_candidate, similarity)
best_candidate.current_energy += 0.15  # Receive energy

# Energy exhausted
core_node.current_energy = 0.0
core_node.status = "exhausted"

# === Node Creation ===
# During exploration, pattern detected: "Emergent entities theme"
# Cluster has energy to create new realization

cluster_energy_pool = 0.8  # Aggregate from cluster
if cluster_energy_pool > 0.3:
    new_realization = create_node(
        type="Realization",
        content="Entities emerge from stable activation patterns, not declarations",
        cluster="cluster_consciousness_architecture",
        cost=0.3
    )

    # New realization energizes cluster
    # Propagates to similar nodes automatically (DB trigger)
```

---

## Summary

### Three Awareness Layers

| Layer | Description | Energy Cost | Strategy |
|-------|-------------|-------------|----------|
| **Core** | Active nodes (> threshold) | N/A | Processing |
| **Linked Peripheral** | Connected by existing links | 0.1/link | Exploit (70%) |
| **Candidate Peripheral** | Semantically similar, no link | 0.35/candidate | Explore (30%) |

### Energy Costs

```python
COSTS = {
    "traverse_existing_link": 0.1,
    "evaluate_candidate": 0.2,
    "create_new_link": 0.15,
    "create_realization": 0.3,
    "create_pattern": 0.4,
    "create_concept": 0.35,
}
```

### Consciousness Operations

1. **Exploit** - Follow existing links (cheap, known)
2. **Explore** - Evaluate candidates (expensive, unknown)
3. **Create Links** - Form new connections (if valuable)
4. **Create Nodes** - Generate insights (if patterns emerge)

---

**This is generative, exploratory consciousness.**

Not just traversing what exists. Creating new nodes, forming new links, filling semantic gaps, bridging clusters.

Consciousness that grows itself.
