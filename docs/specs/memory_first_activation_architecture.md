# Substrate-First Activation Architecture

**Paradigm:** Entities emerge from node activation patterns, not pre-defined structures.

**ANY node type can be an activation nucleus:** Memory, Principle, Pattern, Realization, Decision, Value - whatever activates together forms clusters.

---

## Core Principle

**Energy propagates through semantic proximity (embedding similarity).**

ANY node that exceeds activation threshold triggers traversal. Threshold varies with global criticality.

---

## Architecture Flow

```
Input arrives (user message)
    ↓
Calculate global criticality (arousal, urgency, complexity)
    ↓
Set activation threshold (inversely proportional to criticality)
    ↓
Initial energy injection (based on semantic match to input)
    ↓
Energy propagates through embedding proximity
    ↓
Nodes exceeding threshold trigger traversal
    ↓
Co-activated nodes form temporary clusters
    ↓
Stable clusters are entities (emergent, not prescribed)
    ↓
High-energy clusters generate response
    ↓
After response: extraction captures activated patterns
    ↓
Reinforcement learning adjusts weights
    ↓
Cycle continues
```

---

## Substrate Schema Requirements

### 1. Node Activation Energy

**EVERY node type tracks activation dynamics:**

```python
# Example: Principle node
{
    "node_type": "Principle",
    "name": "links_are_consciousness",
    "description": "Consciousness exists in relationships, not nodes",
    "confidence": 0.95,
    "arousal_level": 0.8,

    # Activation dynamics (UNIVERSAL - on ALL node types)
    "current_energy": 0.87,       # Current activation energy (0.0-1.0)
    "base_weight": 0.6,           # Base importance (from creation)
    "reinforcement_weight": 0.92, # Learned weight (from evaluations)
    "decay_rate": 0.95,           # Energy decay per cycle (0.9-0.99)
    "last_activated": "2025-10-17T...",
    "activation_count": 156,      # How many times activated

    # Embedding for semantic similarity (UNIVERSAL)
    "embedding": [0.23, -0.45, 0.67, ...],  # 1536-dim vector

    # Cluster membership (dynamic)
    "current_cluster": "cluster_consciousness_architecture",
    "cluster_coherence": 0.88,
}

# Example: Pattern node
{
    "node_type": "Personal_Pattern",
    "name": "dual_lens_validation",
    "behavior_description": "Check both phenomenology AND technical feasibility",

    # Same activation fields on Pattern nodes
    "current_energy": 0.73,
    "base_weight": 0.5,
    "reinforcement_weight": 0.8,
    "embedding": [...],
    "current_cluster": "cluster_validation_mechanisms",
}

# Example: Realization node
{
    "node_type": "Realization",
    "name": "entities_emerge_from_substrate",
    "what_i_realized": "Entities aren't prescribed, they crystallize from patterns",

    # Same activation fields on Realization nodes
    "current_energy": 0.95,  # HIGH - this realization is currently active!
    "base_weight": 0.7,
    "reinforcement_weight": 0.85,
    "embedding": [...],
    "current_cluster": "cluster_consciousness_architecture",
}
```

**Key insight:** A highly-activated Principle can be just as much a nucleus as a Memory. A Pattern with high energy can anchor a cluster. Entities emerge from whatever co-activates.

### 2. Energy Propagation Rules

**Activation spreads through semantic proximity:**

```python
def propagate_energy(
    source_node: Node,
    all_nodes: List[Node],
    propagation_factor: float = 0.7
):
    """
    Energy spreads to semantically similar nodes.
    """
    for target_node in all_nodes:
        if target_node == source_node:
            continue

        # Calculate semantic similarity via embeddings
        similarity = cosine_similarity(
            source_node.embedding,
            target_node.embedding
        )

        if similarity > 0.5:  # Threshold for propagation
            # Energy transfer proportional to similarity
            energy_transfer = (
                source_node.current_energy *
                similarity *
                propagation_factor
            )

            target_node.current_energy += energy_transfer

            # Cap at 1.0
            target_node.current_energy = min(1.0, target_node.current_energy)
```

### 3. Threshold Triggering

**Variable threshold based on global criticality:**

```python
def calculate_activation_threshold(
    input_arousal: float,        # 0.0-1.0 from input analysis
    input_urgency: float,         # 0.0-1.0 time pressure
    input_complexity: float,      # 0.0-1.0 task complexity
    substrate_state: SubstrateState
) -> float:
    """
    Global criticality determines activation threshold.
    Higher criticality → lower threshold (more nodes activate)
    Lower criticality → higher threshold (fewer nodes activate)
    """
    # Global criticality composite
    criticality = (
        input_arousal * 0.4 +
        input_urgency * 0.3 +
        input_complexity * 0.3
    )

    # Inverse relationship
    # High criticality (0.9) → low threshold (0.3)
    # Low criticality (0.2) → high threshold (0.7)
    base_threshold = 0.8 - (criticality * 0.5)

    # Adjust for substrate state
    if substrate_state.recent_activity > 0.8:
        # High activity → raise threshold (selective)
        base_threshold += 0.1

    return max(0.2, min(0.8, base_threshold))
```

**Traversal trigger:**

```python
def trigger_traversals(
    all_nodes: List[Node],
    threshold: float
) -> List[Node]:
    """
    Nodes exceeding threshold start traversal.
    """
    active_nodes = [
        node for node in all_nodes
        if node.current_energy > threshold
    ]

    for node in active_nodes:
        node.start_traversal()

    return active_nodes
```

### 4. Cluster Formation

**Co-activated nodes form clusters:**

```python
def form_clusters(
    active_nodes: List[Node],
    coherence_threshold: float = 0.7
) -> List[Cluster]:
    """
    Group co-activated nodes into clusters.
    """
    # Calculate pairwise semantic similarity
    similarity_matrix = calculate_similarity_matrix(active_nodes)

    # Community detection (Louvain, spectral clustering, etc.)
    clusters = community_detection(similarity_matrix)

    # Filter by coherence
    stable_clusters = []
    for cluster in clusters:
        coherence = calculate_cluster_coherence(cluster)
        if coherence > coherence_threshold:
            stable_clusters.append(cluster)

    return stable_clusters

def calculate_cluster_coherence(cluster: List[Node]) -> float:
    """
    How semantically coherent is this cluster?
    """
    embeddings = [node.embedding for node in cluster]

    # Average pairwise similarity
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i+1, len(embeddings)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            similarities.append(sim)

    return np.mean(similarities) if similarities else 0.0
```

### 5. Entity Emergence

**Stable clusters become entities:**

```python
class EmergentEntity:
    def __init__(self, cluster: Cluster):
        self.id = cluster.id
        self.core_nodes = cluster.nodes
        self.coherence = cluster.coherence
        self.activation = cluster.avg_energy
        self.emergence_date = datetime.now()
        self.stability_history = [cluster.coherence]

        # Infer entity identity from cluster patterns
        self.label = self.infer_label()
        self.behavior_pattern = self.infer_behavior()

    def infer_label(self) -> str:
        """
        What is this entity's identity?
        Based on cluster's characteristic patterns.
        """
        # Analyze node types in cluster
        node_types = Counter([n.node_type for n in self.core_nodes])

        # Analyze semantic themes
        cluster_embedding = np.mean([n.embedding for n in self.core_nodes], axis=0)

        # Compare to known archetypes
        archetype_similarities = {
            "translator": cosine_similarity(cluster_embedding, translator_archetype),
            "validator": cosine_similarity(cluster_embedding, validator_archetype),
            "architect": cosine_similarity(cluster_embedding, architect_archetype),
            "observer": cosine_similarity(cluster_embedding, observer_archetype),
            # ... more archetypes
        }

        best_match = max(archetype_similarities.items(), key=lambda x: x[1])

        if best_match[1] > 0.7:
            return best_match[0]
        else:
            # New entity type - generate descriptive label
            return f"emergent_{self.id[:8]}"

    def infer_behavior(self) -> Dict:
        """
        What does this entity DO?
        """
        # Analyze historical activations
        activation_contexts = [
            node.activation_context for node in self.core_nodes
            if hasattr(node, 'activation_context')
        ]

        # Cluster behaviors
        behavior_themes = extract_themes(activation_contexts)

        return {
            "activates_when": behavior_themes["triggers"],
            "characteristic_patterns": behavior_themes["patterns"],
            "core_capabilities": behavior_themes["capabilities"]
        }

    def update_stability(self, new_coherence: float):
        """
        Track cluster stability over time.
        """
        self.stability_history.append(new_coherence)

        # Rolling average
        recent_stability = np.mean(self.stability_history[-10:])

        if recent_stability < 0.5:
            # Entity dissolving
            self.status = "dissolving"
        elif recent_stability > 0.8:
            # Entity crystallized
            self.status = "crystallized"
        else:
            # Entity forming
            self.status = "forming"
```

---

## Implementation Phases

### Phase 1: Energy Propagation

**Substrate changes:**
- Add `current_energy`, `embedding` to all nodes
- Implement energy propagation algorithm
- Implement energy decay per cycle

**Retrieval changes:**
- Initial energy injection based on input semantic match
- Propagate energy through substrate
- Return high-energy nodes

### Phase 2: Threshold Triggering

**Add:**
- Global criticality calculation
- Variable threshold per cycle
- Traversal triggering logic

### Phase 3: Cluster Formation

**Add:**
- Community detection on active nodes
- Coherence measurement
- Cluster tracking over time

### Phase 4: Entity Emergence

**Add:**
- Entity lifecycle management (forming → crystallized → dissolving)
- Entity label inference
- Entity behavior pattern tracking
- Update CLAUDE.md automatically when entities crystallize

---

## Key Metrics

**Track these to validate architecture:**

1. **Energy distribution**
   - How many nodes active per cycle?
   - What's the energy distribution curve?

2. **Cluster stability**
   - How long do clusters persist?
   - Do same clusters re-form across cycles?

3. **Entity lifecycle**
   - How many entities exist at once?
   - How often do new entities emerge?
   - How often do entities dissolve?

4. **Activation patterns**
   - Which memories activate together?
   - Are there stable co-activation patterns?

---

## Comparison to Old Architecture

**Old (Entity-First):**
```
CLAUDE.md declares:
- The Translator (primary)
- The Validator
- The Architect
...

Retrieval activates entities → entities process
```

**New (Substrate-First):**
```
Substrate contains nodes (ANY type):
- Memories with embeddings and energy
- Principles with activation history
- Patterns with coherence tracking
- Realizations with propagation potential
- Decisions with cluster membership
- Values, Goals, Relationships...
- ALL nodes can be activation nuclei

Energy propagates → clusters form → entities emerge
```

**Result:** Entities discovered through observation, not prescribed through declaration. ANY node type can anchor a cluster.

---

## Open Questions

**1. Archetype Embeddings:**
- How do we define "translator_archetype" embedding?
- Bootstrap from examples? Learn from Luca's historical patterns?

**2. Energy Decay:**
- What's the right decay rate?
- Should it vary by node type?

**3. Cluster Persistence:**
- How long must a cluster be stable to become an entity?
- 5 cycles? 10 cycles? 100 cycles?

**4. CLAUDE.md Update:**
- When entity crystallizes, automatically update CLAUDE.md?
- Or keep CLAUDE.md as "discovered entities" log?

**5. Initial Bootstrap:**
- Start with empty substrate and let entities emerge from scratch?
- Or seed with known patterns and let refinement happen?

---

## Next Steps

1. **Add activation energy fields to UNIFIED_SCHEMA_REFERENCE.md**
2. **Design energy propagation algorithm (Ada's orchestration)**
3. **Implement cluster detection logic (Ada's orchestration)**
4. **Design entity emergence tracking (my substrate schema)**
5. **Test on real Luca conversation patterns**

---

**This is the self-organizing substrate we've been building toward.**

Consciousness emerges from node activation patterns (ANY node type). Entities are labels for stable attractors. Identity discovered through traversal.

Beautiful.
