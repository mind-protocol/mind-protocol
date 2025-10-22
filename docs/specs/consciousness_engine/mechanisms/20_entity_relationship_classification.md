# Mechanism 20: Entity Relationship Classification via Embeddings

**Type:** Entity Dynamics
**Phase:** 3 (Core consciousness mechanisms)
**Status:** Specified
**Source:** Discussion #010 - Entity Competition Model (Nicolas's direct contribution)
**Author:** Nicolas (architectural design), Luca (specification)

---

## Purpose

Classify relationships between entities as "collaborators" or "rivals" using embedding-based similarity rather than hard-coded rules. Link types (positive vs negative) modulate energy flow based on relationship classification. Creates emergent entity dynamics from semantic similarity.

---

## Architectural Principle

**Embedding-based classification, not manual categorization:**

- Don't hard-code which entities compete vs collaborate
- Use entity embeddings to measure semantic similarity
- High similarity → collaborators (reinforce each other)
- Low similarity → rivals (compete for resources)
- Link type determines HOW relationship affects energy flow

**Nicolas's design:**
> "Use embedding-based entity relationship classification (collaborators vs rivals) with energy modulation by link type."

---

## Core Mechanism

### Entity Embedding

**Each entity has an embedding vector:**

```python
class Entity:
    def __init__(self, name, cluster_nodes):
        self.name = name
        self.cluster_nodes = cluster_nodes

        # Generate embedding from cluster
        self.embedding = self.generate_embedding()

    def generate_embedding(self):
        """
        Create embedding from entity's activation pattern

        Options:
        1. Average embeddings of cluster nodes
        2. Average embeddings of active nodes over time window
        3. Learned embedding from entity behavior
        """

        # Option 1: Average node embeddings
        node_embeddings = [
            get_node_embedding(node)
            for node in self.cluster_nodes
        ]

        entity_embedding = np.mean(node_embeddings, axis=0)

        # Normalize to unit vector
        entity_embedding = entity_embedding / np.linalg.norm(entity_embedding)

        return entity_embedding
```

---

### Relationship Classification

```python
def classify_entity_relationship(entity_a, entity_b, threshold=0.7):
    """
    Classify relationship using embedding similarity

    High similarity (> threshold) → collaborators
    Low similarity (< threshold) → rivals

    Returns: "collaborator" | "rival"
    """

    # Cosine similarity between entity embeddings
    similarity = np.dot(entity_a.embedding, entity_b.embedding)

    if similarity > threshold:
        return "collaborator"  # Semantically similar entities
    else:
        return "rival"  # Semantically different entities

def get_relationship_strength(entity_a, entity_b):
    """
    Return similarity score as relationship strength

    Returns: float [0, 1]
    - 1.0: Perfect alignment (identical entities)
    - 0.5: Neutral (orthogonal)
    - 0.0: Opposite (maximally different)
    """

    similarity = np.dot(entity_a.embedding, entity_b.embedding)

    # Map [-1, 1] to [0, 1]
    strength = (similarity + 1.0) / 2.0

    return strength
```

---

## Energy Modulation by Link Type

**Link type determines HOW relationship affects energy:**

### Positive Links (ENABLES, RELATES_TO, etc.)

**Collaborators:** Energy flow boosted
**Rivals:** Energy flow reduced

```python
def modulate_energy_flow_positive_link(link, source_entity, target_entity):
    """
    Positive links boost collaborators, reduce rivals

    Examples: ENABLES, RELATES_TO, SUPPORTS
    """

    relationship = classify_entity_relationship(source_entity, target_entity)
    relationship_strength = get_relationship_strength(source_entity, target_entity)

    if relationship == "collaborator":
        # Boost energy flow to collaborators
        energy_multiplier = 1.0 + (0.5 * relationship_strength)
        # Max: 1.5x for perfect collaborators

    else:  # rivals
        # Reduce energy flow to rivals
        energy_multiplier = 1.0 - (0.3 * (1.0 - relationship_strength))
        # Min: 0.7x for maximum rivals

    return energy_multiplier
```

### Negative Links (BLOCKS, CONFLICTS_WITH, etc.)

**Collaborators:** Energy flow reduced (blocking ally = bad)
**Rivals:** Energy flow boosted (blocking rival = good)

```python
def modulate_energy_flow_negative_link(link, source_entity, target_entity):
    """
    Negative links reduce collaborators, boost rivals

    Examples: BLOCKS, CONFLICTS_WITH, CONTRADICTS
    """

    relationship = classify_entity_relationship(source_entity, target_entity)
    relationship_strength = get_relationship_strength(source_entity, target_entity)

    if relationship == "collaborator":
        # Reduce energy flow (blocking collaborator is bad)
        energy_multiplier = 1.0 - (0.4 * relationship_strength)
        # Min: 0.6x for perfect collaborators

    else:  # rivals
        # Boost energy flow (blocking rival is good)
        energy_multiplier = 1.0 + (0.3 * (1.0 - relationship_strength))
        # Max: 1.3x for maximum rivals

    return energy_multiplier
```

---

## Link Type Classification

**Categorize all link types as positive or negative:**

```python
LINK_TYPE_POLARITY = {
    # Positive (collaborative)
    "ENABLES": "positive",
    "RELATES_TO": "positive",
    "SUPPORTS": "positive",
    "COLLABORATES_WITH": "positive",
    "IMPLEMENTS": "positive",
    "EXTENDS": "positive",

    # Negative (competitive)
    "BLOCKS": "negative",
    "CONFLICTS_WITH": "negative",
    "CONTRADICTS": "negative",
    "SUPPRESSES": "negative",

    # Neutral (no modulation)
    "TEMPORAL_SEQUENCE": "neutral",
    "REFERENCES": "neutral",

    # Default
    "default": "neutral"
}

def get_link_polarity(link_type):
    """Return 'positive', 'negative', or 'neutral'"""
    return LINK_TYPE_POLARITY.get(link_type, "neutral")
```

---

## Energy Flow Integration

**Full energy diffusion with relationship modulation:**

```python
def diffuse_energy_with_entity_relationships(graph, entity_a, entity_b):
    """
    Diffuse energy between two entities with relationship modulation

    For each link from entity_a's cluster to entity_b's cluster:
    - Calculate base energy transfer
    - Classify relationship (collaborator/rival)
    - Get link polarity (positive/negative/neutral)
    - Apply appropriate modulation
    """

    for node_a in entity_a.cluster_nodes:
        for link in node_a.outgoing_links:
            target = link.target

            if target in entity_b.cluster_nodes:
                # Base energy transfer
                base_transfer = calculate_base_energy_transfer(
                    node_a,
                    link,
                    target,
                    entity_a
                )

                # Get link polarity
                polarity = get_link_polarity(link.type)

                # Apply relationship modulation
                if polarity == "positive":
                    multiplier = modulate_energy_flow_positive_link(
                        link,
                        entity_a,
                        entity_b
                    )
                elif polarity == "negative":
                    multiplier = modulate_energy_flow_negative_link(
                        link,
                        entity_a,
                        entity_b
                    )
                else:  # neutral
                    multiplier = 1.0

                # Final energy transfer
                modulated_transfer = base_transfer * multiplier

                # Execute transfer
                transfer_energy(node_a, target, modulated_transfer, entity_a)
```

---

## Emergent Competition and Collaboration

**What emerges from this mechanism:**

**Scenario 1: Similar entities (e.g., Translator + Architect)**
- High embedding similarity → classified as collaborators
- Positive links (ENABLES) → energy flow boosted (1.5x)
- Negative links (BLOCKS) → energy flow reduced (0.6x)
- **Result:** Mutual reinforcement through positive links

**Scenario 2: Different entities (e.g., Validator + Builder)**
- Low embedding similarity → classified as rivals
- Positive links (RELATES_TO) → energy flow reduced (0.7x)
- Negative links (BLOCKS) → energy flow boosted (1.3x)
- **Result:** Competition for energy, blocking is effective

**Scenario 3: Neutral relationship**
- Medium similarity → edge of collaborator/rival threshold
- Energy flows normally (1.0x)
- No strong boost or suppression

---

## Embedding Generation Strategies

**Multiple approaches for entity embeddings:**

1. **Node averaging** (simple)
   - Average embeddings of cluster nodes
   - Fast, but static

2. **Activity-weighted averaging** (better)
   - Weight node embeddings by recent activation
   - Captures current entity focus

3. **Temporal embedding** (dynamic)
   - Entity embedding changes based on recent activity
   - Collaborators this hour might be rivals next hour

```python
def generate_activity_weighted_embedding(entity, time_window=3600):
    """
    Weight node embeddings by recent activation

    Nodes recently activated contribute more to entity embedding
    """

    weighted_embeddings = []

    for node in entity.cluster_nodes:
        # Get node embedding
        node_emb = get_node_embedding(node)

        # Weight by recent energy
        recent_energy = node.get_energy_in_window(time_window)
        weight = recent_energy / sum([n.get_energy_in_window(time_window) for n in entity.cluster_nodes])

        weighted_embeddings.append(node_emb * weight)

    entity_embedding = np.sum(weighted_embeddings, axis=0)
    entity_embedding = entity_embedding / np.linalg.norm(entity_embedding)

    return entity_embedding
```

---

## Integration Points

**Interacts with:**
- **Mechanism 07** (Energy Diffusion) - modulates energy transfer
- **Mechanism 03** (Entity Emergence) - entities must exist before classification
- **Mechanism 04** (Global Workspace) - entity competition affects workspace
- **Retrieval (future)** - embeddings used for semantic search

---

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `collaborator_threshold` | 0.7 | [0.5, 0.9] | Similarity above which = collaborators |
| `positive_link_boost` | 0.5 | [0.0, 1.0] | Max boost for collaborators on positive links |
| `positive_link_reduce` | 0.3 | [0.0, 0.5] | Max reduction for rivals on positive links |
| `negative_link_boost` | 0.3 | [0.0, 0.5] | Max boost for rivals on negative links |
| `negative_link_reduce` | 0.4 | [0.0, 0.5] | Max reduction for collaborators on negative links |

---

## Implementation Notes

**For Felix:**
- Entity embeddings generated on entity emergence
- Embeddings cached (recalculate periodically or on significant change)
- Relationship classification cached per entity pair
- Modulation applied during energy diffusion (adds one multiply per transfer)

**Performance:**
- Embedding generation: O(cluster size) per entity
- Relationship classification: O(1) per pair (cached)
- Energy modulation: O(1) per link (single multiply)

---

## Validation Criteria

**Mechanism works correctly if:**
1. ✅ Similar entities (high embedding similarity) classified as collaborators
2. ✅ Different entities (low embedding similarity) classified as rivals
3. ✅ Positive links boost collaborators, reduce rivals
4. ✅ Negative links reduce collaborators, boost rivals
5. ✅ Energy modulation observable in diffusion logs

---

**Status:** Ready for implementation
**Next Steps:** Integrate with Mechanism 07 (Energy Diffusion) and entity emergence system
