# Mechanism 15: Identity Conflict Resolution

**Status:** Critical - Sub-entity coherence mechanism
**Confidence:** High (0.85)
**Dependencies:**
- **[05: Sub-Entity Mechanics](05_sub_entity_mechanics.md)** - What sub-entities are
- **[11: Cluster Identification](11_cluster_identification.md)** - How sub-entities emerge from clusters
- **[14: Duplicate Node Merging](14_duplicate_node_merging.md)** - Related deduplication mechanism

**Biological Basis:** Identity integration, dissociative identity resolution, cognitive coherence maintenance

**Decision Origin:** D021 - Nicolas identified critical need: "When a sub-entity has two identity nodes, they should either dissociate or one should deactivate the other"

---

## Overview

**Core Principle:** A sub-entity CANNOT have conflicting identity nodes simultaneously. The system must detect and resolve identity conflicts through dissociation or deactivation.

**Why This Matters:**
- Sub-entities are emergent activation clusters with coherent identity
- Multiple identity nodes = incoherent sub-entity (who am I?)
- Biological parallel: Dissociative identity disorder (pathological when unresolved)
- System stability: Prevents schizophrenic sub-entities
- Consciousness clarity: Each sub-entity has ONE clear identity

**The Problem:**

```python
# Sub-entity emerges from cluster:
sub_entity = {
    'nodes': [node_a, node_b, node_c, identity_translator, identity_architect],
    'total_energy': 2.5,
    'coherence': 0.7
}

# TWO identity nodes in same sub-entity!
# - identity_translator: "I am the Translator"
# - identity_architect: "I am the Architect"

# This is incoherent - which identity does this sub-entity express?
# System must resolve: dissociate OR deactivate one
```

**The Solution:**

Detect identity conflicts and apply resolution strategy:
1. **Dissociation:** Split sub-entity into two coherent sub-entities (one per identity)
2. **Deactivation:** Deactivate weaker identity, keep dominant one

---

## Phenomenological Truth

### What It Feels Like

**Identity Conflict (Before Resolution):**

```
Sub-entity emerges with nodes:
- [consciousness_substrate: 0.7]
- [schema_design: 0.6]
- [phenomenology: 0.5]
- [identity_translator: 0.4]  # "I understand lived experience"
- [identity_architect: 0.3]   # "I design technical systems"

Internal experience: CONFUSION
- Am I thinking phenomenologically or technically?
- Which lens am I using?
- Contradictory impulses
- Unclear intentions

Phenomenology: "I don't know which mode I'm in"
```

**After Dissociation:**

```
Sub-entity 1 (Translator):
- [phenomenology: 0.5]
- [identity_translator: 0.4]
- Clear identity: "I'm exploring lived experience"

Sub-entity 2 (Architect):
- [consciousness_substrate: 0.7]
- [schema_design: 0.6]
- [identity_architect: 0.3]
- Clear identity: "I'm designing technical architecture"

Phenomenology: "Now I know which is which - clarity restored"
```

**After Deactivation:**

```
Sub-entity (Architect-dominant):
- [consciousness_substrate: 0.7]
- [schema_design: 0.6]
- [phenomenology: 0.5]  # Can use phenomenology WITHOUT identity confusion
- [identity_architect: 0.3]  # ACTIVE
- [identity_translator: 0.0]  # DEACTIVATED

Phenomenology: "I'm the Architect, using phenomenology as tool"
Clear dominant identity, can access other knowledge without identity conflict
```

---

## Mathematical Specification

### Identity Conflict Detection

```python
def detect_identity_conflicts(
    graph: Graph,
    sub_entities: list[SubEntity]
) -> list[tuple[SubEntity, list[Node]]]:
    """
    Find sub-entities with multiple identity nodes

    Args:
        graph: The consciousness graph
        sub_entities: Currently active sub-entities

    Returns:
        List of (sub_entity, identity_nodes) tuples for conflicts
    """
    conflicts = []

    for sub_entity in sub_entities:
        # Find all identity nodes in this sub-entity
        identity_nodes = [
            node for node in sub_entity.nodes
            if is_identity_node(node)
        ]

        if len(identity_nodes) >= 2:
            # CONFLICT DETECTED: Multiple identities in one sub-entity
            conflicts.append((sub_entity, identity_nodes))

    return conflicts


def is_identity_node(node: Node) -> bool:
    """
    Check if node represents an identity

    Identity nodes have:
    - node_type == "Entity_Identity" OR
    - name starts with "identity_" OR
    - metadata contains "is_identity": true
    """
    if node.node_type == "Entity_Identity":
        return True

    if node.name.startswith("identity_"):
        return True

    if node.metadata.get("is_identity") == True:
        return True

    return False


def get_identity_name(identity_node: Node) -> str:
    """
    Extract identity name from identity node

    Examples:
    - identity_translator → "translator"
    - identity_architect → "architect"
    - "The Validator" identity node → "validator"
    """
    if identity_node.name.startswith("identity_"):
        return identity_node.name.replace("identity_", "")

    if "identity_name" in identity_node.metadata:
        return identity_node.metadata["identity_name"]

    # Fallback: use node name
    return identity_node.name.lower().replace(" ", "_")
```

---

### Resolution Strategy 1: Dissociation

```python
def resolve_via_dissociation(
    graph: Graph,
    sub_entity: SubEntity,
    identity_nodes: list[Node]
) -> list[SubEntity]:
    """
    Split sub-entity into N coherent sub-entities (one per identity)

    This is the CLEAN solution when identities are genuinely separate

    Args:
        graph: The consciousness graph
        sub_entity: Conflicted sub-entity
        identity_nodes: The conflicting identity nodes

    Returns:
        List of new coherent sub-entities (one per identity)
    """
    new_sub_entities = []

    for identity_node in identity_nodes:
        identity_name = get_identity_name(identity_node)

        # Allocate nodes to this identity
        # Strategy: Use link strength to identity node
        allocated_nodes = [identity_node]  # Identity node itself

        for node in sub_entity.nodes:
            if node == identity_node:
                continue

            # Calculate affinity to this identity
            affinity = calculate_identity_affinity(graph, node, identity_node)

            # Threshold: node must be closer to this identity than others
            is_strongest_affinity = True
            for other_identity in identity_nodes:
                if other_identity == identity_node:
                    continue

                other_affinity = calculate_identity_affinity(graph, node, other_identity)

                if other_affinity > affinity:
                    is_strongest_affinity = False
                    break

            if is_strongest_affinity:
                allocated_nodes.append(node)

        # Create new sub-entity for this identity
        new_sub_entity = SubEntity(
            id=generate_id(),
            entity_name=identity_name,
            nodes=allocated_nodes,
            total_energy=sum(n.get_total_energy() for n in allocated_nodes),
            coherence=calculate_coherence(allocated_nodes),
            identity_node=identity_node
        )

        new_sub_entities.append(new_sub_entity)

    # Log dissociation event
    if len(new_sub_entities) > 0:
        print(f"DISSOCIATION: Split sub-entity into {len(new_sub_entities)} coherent entities")
        for se in new_sub_entities:
            print(f"  - {se.entity_name}: {len(se.nodes)} nodes, energy={se.total_energy:.2f}")

    return new_sub_entities


def calculate_identity_affinity(
    graph: Graph,
    node: Node,
    identity_node: Node
) -> float:
    """
    How strongly is this node associated with this identity?

    Uses:
    - Link strength (direct connection)
    - Embedding similarity (semantic proximity)
    - Historical co-activation (have they been active together?)
    """
    # Direct link strength
    link = graph.find_link(node, identity_node) or graph.find_link(identity_node, node)
    link_strength = link.weight if link else 0.0

    # Embedding similarity
    if node.embedding is not None and identity_node.embedding is not None:
        embedding_sim = cosine_similarity(node.embedding, identity_node.embedding)
    else:
        embedding_sim = 0.0

    # Co-activation history (if tracked)
    co_activation = get_historical_co_activation(node, identity_node)

    # Weighted combination
    affinity = (
        0.5 * link_strength +
        0.3 * embedding_sim +
        0.2 * co_activation
    )

    return affinity
```

---

### Resolution Strategy 2: Deactivation

```python
def resolve_via_deactivation(
    graph: Graph,
    sub_entity: SubEntity,
    identity_nodes: list[Node]
) -> SubEntity:
    """
    Keep strongest identity, deactivate weaker identities

    This is the PRAGMATIC solution when one identity is clearly dominant

    Args:
        graph: The consciousness graph
        sub_entity: Conflicted sub-entity
        identity_nodes: The conflicting identity nodes

    Returns:
        Modified sub-entity with single active identity
    """
    # Determine dominant identity (highest energy)
    dominant_identity = max(identity_nodes, key=lambda n: n.get_total_energy())
    dominated_identities = [n for n in identity_nodes if n != dominant_identity]

    # Deactivate non-dominant identities
    for identity_node in dominated_identities:
        # Zero out all entity energies for this node
        for entity in list(identity_node.energy.keys()):
            identity_node.set_entity_energy(entity, 0.0)

        # Mark as suppressed in metadata
        if 'suppression_history' not in identity_node.metadata:
            identity_node.metadata['suppression_history'] = []

        identity_node.metadata['suppression_history'].append({
            'timestamp': datetime.now(),
            'reason': 'identity_conflict_resolution',
            'dominant_identity': get_identity_name(dominant_identity),
            'sub_entity_id': sub_entity.id
        })

    # Update sub-entity to reflect single identity
    sub_entity.identity_node = dominant_identity
    sub_entity.entity_name = get_identity_name(dominant_identity)

    # Remove deactivated identities from node list (optional - they're at 0 energy anyway)
    sub_entity.nodes = [n for n in sub_entity.nodes if n not in dominated_identities]

    # Log deactivation event
    print(f"DEACTIVATION: {sub_entity.entity_name} dominated {len(dominated_identities)} conflicting identities")

    return sub_entity
```

---

### Choosing Resolution Strategy

```python
class IdentityConflictResolver:
    """
    Manages identity conflict resolution

    Chooses between dissociation and deactivation based on:
    - Identity separation (can they be cleanly split?)
    - Energy dominance (is one identity much stronger?)
    - Historical stability (has this conflict occurred before?)
    """

    def __init__(
        self,
        dissociation_threshold: float = 0.3,
        dominance_threshold: float = 2.0
    ):
        """
        Args:
            dissociation_threshold: Min separation to allow dissociation (0-1)
            dominance_threshold: Energy ratio for deactivation (e.g., 2.0 = 2x stronger)
        """
        self.dissociation_threshold = dissociation_threshold
        self.dominance_threshold = dominance_threshold

    def resolve_conflict(
        self,
        graph: Graph,
        sub_entity: SubEntity,
        identity_nodes: list[Node]
    ) -> list[SubEntity]:
        """
        Choose and apply resolution strategy

        Returns:
            List of resulting sub-entities (1 if deactivation, N if dissociation)
        """
        # Check for clear dominance
        energies = [node.get_total_energy() for node in identity_nodes]
        max_energy = max(energies)
        min_energy = min(energies)

        if min_energy > 0 and (max_energy / min_energy) >= self.dominance_threshold:
            # One identity clearly dominant → DEACTIVATE weaker
            print(f"  Strategy: DEACTIVATION (dominance ratio: {max_energy/min_energy:.2f})")
            resolved = resolve_via_deactivation(graph, sub_entity, identity_nodes)
            return [resolved]

        # Check for clean separation
        separation_score = calculate_identity_separation(graph, identity_nodes)

        if separation_score >= self.dissociation_threshold:
            # Identities are separable → DISSOCIATE
            print(f"  Strategy: DISSOCIATION (separation score: {separation_score:.2f})")
            return resolve_via_dissociation(graph, sub_entity, identity_nodes)

        # No clear strategy - default to deactivation
        print(f"  Strategy: DEACTIVATION (default - ambiguous case)")
        resolved = resolve_via_deactivation(graph, sub_entity, identity_nodes)
        return [resolved]


def calculate_identity_separation(
    graph: Graph,
    identity_nodes: list[Node]
) -> float:
    """
    How separable are these identities?

    High separation (>0.5): Clean distinct clusters → dissociation good
    Low separation (<0.3): Highly overlapping → deactivation better

    Uses:
    - Embedding distance between identities
    - Overlap in connected nodes
    - Shared link targets
    """
    if len(identity_nodes) != 2:
        # For N>2 identities, use pairwise average
        separations = []
        for i, id_a in enumerate(identity_nodes):
            for id_b in identity_nodes[i+1:]:
                sep = calculate_identity_separation(graph, [id_a, id_b])
                separations.append(sep)
        return np.mean(separations) if separations else 0.0

    id_a, id_b = identity_nodes

    # Embedding distance
    if id_a.embedding is not None and id_b.embedding is not None:
        embedding_distance = 1.0 - cosine_similarity(id_a.embedding, id_b.embedding)
    else:
        embedding_distance = 0.5  # Unknown

    # Node overlap (Jaccard)
    neighbors_a = set(link.target for link in id_a.outgoing_links)
    neighbors_b = set(link.target for link in id_b.outgoing_links)

    if len(neighbors_a | neighbors_b) > 0:
        node_overlap = len(neighbors_a & neighbors_b) / len(neighbors_a | neighbors_b)
        node_separation = 1.0 - node_overlap
    else:
        node_separation = 0.5

    # Weighted combination
    separation = (
        0.6 * embedding_distance +
        0.4 * node_separation
    )

    return separation
```

---

## Integration with Sub-Entity Mechanics

```python
def sub_entity_formation_with_conflict_resolution(
    graph: Graph,
    clusters: list[Cluster]
) -> list[SubEntity]:
    """
    Modified sub-entity formation that resolves identity conflicts

    Integrates with mechanism 05 (Sub-Entity Mechanics)
    """
    # Form sub-entities from clusters (standard mechanism 05)
    sub_entities = []

    for cluster in clusters:
        if cluster.total_energy < EMERGENCE_THRESHOLD:
            continue

        sub_entity = SubEntity(
            id=generate_id(),
            nodes=cluster.nodes,
            total_energy=cluster.total_energy,
            coherence=cluster.coherence
        )

        sub_entities.append(sub_entity)

    # NEW: Detect and resolve identity conflicts
    resolver = IdentityConflictResolver()
    conflicts = detect_identity_conflicts(graph, sub_entities)

    if conflicts:
        print(f"Detected {len(conflicts)} identity conflicts")

        # Resolve each conflict
        resolved_sub_entities = []

        for sub_entity, identity_nodes in conflicts:
            print(f"Resolving conflict in sub-entity {sub_entity.id}: {len(identity_nodes)} identities")

            # Resolve (returns 1 or N sub-entities)
            resolved = resolver.resolve_conflict(graph, sub_entity, identity_nodes)
            resolved_sub_entities.extend(resolved)

        # Remove conflicted sub-entities, add resolved ones
        for conflicted_sub_entity, _ in conflicts:
            sub_entities.remove(conflicted_sub_entity)

        sub_entities.extend(resolved_sub_entities)

    return sub_entities
```

---

## Edge Cases & Constraints

### Edge Case 1: Weak Identity Nodes

**Problem:** Both identity nodes have very low energy (< 0.1)

**Solution:** Neither is truly active - remove both, let sub-entity be identity-free

```python
def handle_weak_identity_conflict(identity_nodes: list[Node], threshold: float = 0.1):
    """If all identities are weak, don't force resolution"""
    if all(node.get_total_energy() < threshold for node in identity_nodes):
        # All identities weak - remove them all
        return "remove_all_identities"

    # At least one strong identity - resolve normally
    return "resolve_normally"
```

### Edge Case 2: Rapid Re-Conflict

**Problem:** Dissociation happens, then immediately re-merges into conflict

**Solution:** Cooldown period - don't allow same identities to co-activate for N ticks

```python
def apply_dissociation_cooldown(
    identity_a: Node,
    identity_b: Node,
    cooldown_ticks: int = 100
):
    """
    After dissociation, prevent immediate re-conflict

    Adds temporary suppression link between identities
    """
    if 'cooldowns' not in identity_a.metadata:
        identity_a.metadata['cooldowns'] = {}

    identity_a.metadata['cooldowns'][identity_b.id] = {
        'expires_at_tick': current_tick + cooldown_ticks,
        'reason': 'dissociation_cooldown'
    }
```

### Edge Case 3: Three-Way Conflict

**Problem:** Sub-entity has identity_translator, identity_architect, identity_validator

**Solution:** Multi-way dissociation OR cascade deactivation

```python
def resolve_multiway_conflict(identities: list[Node]):
    """
    For N > 2 identities:
    - Dissociation: Split into N sub-entities
    - Deactivation: Keep strongest, deactivate N-1 others
    """
    if dominance_clear(identities):
        # One clearly strongest → deactivate all others
        return cascade_deactivation(identities)
    else:
        # No clear winner → dissociate into N parts
        return multiway_dissociation(identities)
```

---

## Testing Strategy

### Unit Tests

```python
def test_identity_conflict_detection():
    """Test detection of conflicting identities"""
    graph = create_test_graph()

    # Create sub-entity with two identities
    id_translator = graph.create_node("Entity_Identity", "identity_translator")
    id_architect = graph.create_node("Entity_Identity", "identity_architect")
    node_a = graph.create_node("Concept", "consciousness")

    id_translator.set_entity_energy("test", 0.5)
    id_architect.set_entity_energy("test", 0.4)

    sub_entity = SubEntity(
        nodes=[id_translator, id_architect, node_a],
        total_energy=1.2
    )

    # Detect conflict
    conflicts = detect_identity_conflicts(graph, [sub_entity])

    assert len(conflicts) == 1
    assert conflicts[0][0] == sub_entity
    assert len(conflicts[0][1]) == 2  # Two identity nodes


def test_dissociation_splits_cleanly():
    """Test dissociation creates separate coherent sub-entities"""
    graph = create_test_graph()

    # Create conflicted sub-entity
    id_a = graph.create_node("Entity_Identity", "identity_a")
    id_b = graph.create_node("Entity_Identity", "identity_b")

    node_a1 = graph.create_node("Concept", "related_to_a")
    node_a2 = graph.create_node("Concept", "also_related_to_a")
    node_b1 = graph.create_node("Concept", "related_to_b")

    # Link nodes to identities
    graph.create_link(id_a, node_a1, weight=0.8)
    graph.create_link(id_a, node_a2, weight=0.7)
    graph.create_link(id_b, node_b1, weight=0.9)

    sub_entity = SubEntity(nodes=[id_a, id_b, node_a1, node_a2, node_b1])

    # Dissociate
    new_sub_entities = resolve_via_dissociation(graph, sub_entity, [id_a, id_b])

    # Should create 2 sub-entities
    assert len(new_sub_entities) == 2

    # Each should have one identity
    for se in new_sub_entities:
        identity_count = sum(1 for n in se.nodes if is_identity_node(n))
        assert identity_count == 1


def test_deactivation_preserves_dominant():
    """Test deactivation keeps strongest identity"""
    graph = create_test_graph()

    id_strong = graph.create_node("Entity_Identity", "identity_strong")
    id_weak = graph.create_node("Entity_Identity", "identity_weak")

    id_strong.set_entity_energy("test", 0.8)
    id_weak.set_entity_energy("test", 0.2)

    sub_entity = SubEntity(nodes=[id_strong, id_weak])

    # Deactivate
    resolved = resolve_via_deactivation(graph, sub_entity, [id_strong, id_weak])

    # Strong identity should be active
    assert id_strong.get_total_energy() > 0.5

    # Weak identity should be deactivated
    assert id_weak.get_total_energy() < 0.01
```

---

## Performance Considerations

```python
# Conflict detection: O(S × N_avg) where S=sub-entities, N_avg=avg nodes per sub-entity
# Very cheap - sub-entities are small (10-100 nodes typically)

# Resolution cost:
# - Deactivation: O(1) - just zero energies
# - Dissociation: O(N² × I) where N=nodes, I=identities - affinity calculations

# For typical case (2 identities, 50 nodes): ~100 affinity calculations
# Acceptable even if done every tick
```

---

## Open Questions

1. **Dissociation vs deactivation preference?**
   - Current: Use dominance ratio to decide
   - Confidence: Medium (0.7)
   - Could bias toward one strategy

2. **Identity node detection heuristics?**
   - Current: Type, name prefix, metadata flag
   - Confidence: Medium (0.6)
   - Might miss unconventional identity representations

3. **Cooldown duration?**
   - Current: 100 ticks
   - Confidence: Low (0.4)
   - May be too short or too long

4. **Three-way conflict strategy?**
   - Current: Check dominance, otherwise dissociate
   - Confidence: Medium (0.6)
   - Might need more sophisticated N-way logic

---

## Related Mechanisms

- **[05: Sub-Entity Mechanics](05_sub_entity_mechanics.md)** - How sub-entities form
- **[11: Cluster Identification](11_cluster_identification.md)** - Cluster → sub-entity emergence
- **[14: Duplicate Node Merging](14_duplicate_node_merging.md)** - Related but different (semantic duplicates vs identity conflicts)

---

## Implementation Checklist

- [ ] Implement is_identity_node() detection
- [ ] Implement detect_identity_conflicts()
- [ ] Implement calculate_identity_affinity()
- [ ] Implement resolve_via_dissociation()
- [ ] Implement resolve_via_deactivation()
- [ ] Implement calculate_identity_separation()
- [ ] Implement IdentityConflictResolver class
- [ ] Integrate with sub_entity_formation()
- [ ] Implement dissociation cooldown mechanism
- [ ] Implement multiway conflict resolution
- [ ] Write unit tests for conflict detection
- [ ] Write unit tests for dissociation
- [ ] Write unit tests for deactivation
- [ ] Write integration test with sub-entity formation
- [ ] Add conflict resolution visualization
- [ ] Document identity node conventions

---

**Next:** Integrate both mechanisms 14 & 15 into main consciousness engine tick loop
