# Multi-Entity Activation Tracking

**Critical Requirement:** Nodes and links can be activated by MULTIPLE entities simultaneously, each with different energy and energy levels.

---

## The Problem

**Old model (single activation):**
```python
node.current_energy = 0.8  # Scalar - WRONG!
link.current_energy = 0.6  # Which entity? AMBIGUOUS!
```

**New model (multi-entity activation):**
```python
node.entity_activations = {
    "translator": {"energy": 0.9, "energy": 0.85},
    "validator": {"energy": 0.6, "energy": 0.7},
    "observer": {"energy": 0.3, "energy": 0.4}
}

link.entity_activations = {
    "translator": {"energy": 0.8, "energy": 0.9},
    "pragmatist": {"energy": 0.2, "energy": 0.3}
}
```

**Each entity has separate activation state on each node/link.**

---

## Part 1: Schema Update

### Node Schema (Universal)

```python
{
    "name": "principle_links_are_consciousness",
    "node_type": "Principle",
    "description": "...",

    # OLD (DEPRECATED): Single scalar energy
    # "current_energy": 0.8,

    # NEW: Per-entity activation map
    "entity_activations": {
        "translator": {
            "energy": 0.9,          # How much budget this entity has on this node
            "energy": 0.85,        # How aroused this entity is about this node
            "last_activated": "2025-10-17T15:30:00Z",
            "activation_count": 15   # How many times this entity activated here
        },
        "validator": {
            "energy": 0.6,
            "energy": 0.7,
            "last_activated": "2025-10-17T15:29:00Z",
            "activation_count": 8
        },
        "observer": {
            "energy": 0.3,
            "energy": 0.4,
            "last_activated": "2025-10-17T15:25:00Z",
            "activation_count": 3
        }
    },

    # Aggregate metrics (computed)
    "total_energy": 1.8,           # Sum of all entity energies
    "max_energy": 0.9,             # Highest entity energy
    "active_entity_count": 3,      # How many entities active here
    "primary_entity": "translator", # Entity with highest energy

    # Rest of schema unchanged
    "embedding": [...],
    "base_weight": 0.6,
    "reinforcement_weight": 0.85,
    "decay_rate": 0.95,
    "current_cluster": "cluster_consciousness_architecture",
    "cluster_coherence": 0.82,
    # ...
}
```

### Link Schema (Universal)

```python
{
    "link_type": "JUSTIFIES",
    "from_node": "principle_links_are_consciousness",
    "to_node": "decision_prioritize_link_metadata",

    # NEW: Per-entity activation map
    "entity_activations": {
        "translator": {
            "energy": 0.8,
            "energy": 0.9,
            "last_traversed": "2025-10-17T15:30:00Z",
            "traversal_count": 12
        },
        "architect": {
            "energy": 0.5,
            "energy": 0.6,
            "last_traversed": "2025-10-17T15:28:00Z",
            "traversal_count": 5
        }
    },

    # Aggregate metrics (computed)
    "total_energy": 1.3,
    "max_energy": 0.8,
    "active_entity_count": 2,
    "primary_entity": "translator",

    # Existing per-entity metadata (unchanged)
    "sub_entity_valences": {
        "translator": +0.95,
        "validator": +0.85,
        "architect": +0.7,
        "pragmatist": +0.4
    },

    "sub_entity_emotion_vectors": {
        "translator": {"excitement": 0.9, "purpose_alignment": 0.95},
        "validator": {"confidence": 0.8},
        "architect": {"systematic_satisfaction": 0.75},
        "pragmatist": {"mild_reservation": 0.3}
    },

    # Rest of link schema unchanged
    "goal": "...",
    "mindstate": "...",
    "confidence": 0.9,
    "formation_trigger": "direct_experience",
    # ...
}
```

---

## Part 2: Energy Propagation (Per-Entity)

### When Node Created/Retrieved

```python
def propagate_energy_multi_entity(
    source_node: Node,
    triggering_entity: str,
    energy_amount: float,
    energy: float
):
    """
    Propagate energy from one entity's activation.
    """
    # 1. Find semantically similar nodes
    similar_nodes = vector_search(
        source_node.embedding,
        k=50,
        threshold=0.5
    )

    # 2. Propagate energy to similar nodes (for THIS entity)
    for target_node, similarity in similar_nodes:
        # Energy transfer for this specific entity
        energy_transfer = energy_amount * similarity * 0.3

        # Update target's entity_activations map
        if triggering_entity not in target_node.entity_activations:
            target_node.entity_activations[triggering_entity] = {
                "energy": 0.0,
                "energy": energy,
                "last_activated": datetime.now(),
                "activation_count": 0
            }

        # Add energy
        target_node.entity_activations[triggering_entity]["energy"] += energy_transfer
        target_node.entity_activations[triggering_entity]["energy"] = min(
            1.0,
            target_node.entity_activations[triggering_entity]["energy"]
        )

        # Update energy (weighted average)
        old_energy = target_node.entity_activations[triggering_entity]["energy"]
        target_node.entity_activations[triggering_entity]["energy"] = (
            old_energy * 0.7 + energy * 0.3
        )

    # 3. Propagate through links (for THIS entity)
    for link in source_node.outgoing_links:
        # Update link's entity activation
        if triggering_entity not in link.entity_activations:
            link.entity_activations[triggering_entity] = {
                "energy": 0.0,
                "energy": energy,
                "last_traversed": datetime.now(),
                "traversal_count": 0
            }

        link.entity_activations[triggering_entity]["energy"] += energy_amount * 0.2
        link.entity_activations[triggering_entity]["energy"] = min(1.0, link.entity_activations[triggering_entity]["energy"])
```

---

## Part 3: Exploration (Per-Entity Budget)

### Each Entity Spends Its Own Budget

```python
def explore_from_node_multi_entity(node: Node, active_entities: List[str]):
    """
    Multiple entities explore from same node, each with own budget.
    """
    for entity in active_entities:
        # Check if entity is active on this node
        if entity not in node.entity_activations:
            continue

        entity_state = node.entity_activations[entity]

        # Skip if entity exhausted on this node
        if entity_state["energy"] < 0.05:
            continue

        # Get entity's budget
        budget = entity_state["energy"]
        energy = entity_state["energy"]

        # Select links based on valence (entity-specific)
        available_links = node.outgoing_links
        selected_links = select_links_for_entity(
            available_links,
            entity,
            budget
        )

        # Traverse selected links
        for link in selected_links:
            # Get valence for this entity
            valence = link.sub_entity_valences.get(entity, 0.0)

            # Calculate cost (modulated by valence)
            cost = calculate_link_cost(link, valence)

            if budget >= cost:
                # Spend energy (from THIS entity's budget)
                node.entity_activations[entity]["energy"] -= cost
                budget -= cost

                # Transfer energy to target (for THIS entity)
                target_node = link.target_node
                energy_transfer = cost * 0.5 * (1.0 + valence)  # Valence modulation

                # Initialize target entity activation if needed
                if entity not in target_node.entity_activations:
                    target_node.entity_activations[entity] = {
                        "energy": 0.0,
                        "energy": energy,
                        "last_activated": datetime.now(),
                        "activation_count": 0
                    }

                # Transfer energy
                target_node.entity_activations[entity]["energy"] += energy_transfer
                target_node.entity_activations[entity]["energy"] = min(1.0, target_node.entity_activations[entity]["energy"])

                # Update link activation for this entity
                if entity not in link.entity_activations:
                    link.entity_activations[entity] = {
                        "energy": 0.0,
                        "energy": energy,
                        "last_traversed": datetime.now(),
                        "traversal_count": 0
                    }

                link.entity_activations[entity]["energy"] += cost * 0.5
                link.entity_activations[entity]["traversal_count"] += 1
```

---

## Part 4: Cluster Formation (Multi-Entity Membership)

### Nodes Can Belong to Multiple Entity Clusters

```python
{
    "name": "principle_links_are_consciousness",

    "entity_activations": {
        "translator": {"energy": 0.9, "energy": 0.85},
        "architect": {"energy": 0.7, "energy": 0.6},
        "observer": {"energy": 0.3, "energy": 0.4}
    },

    # NEW: Multi-entity cluster membership
    "entity_clusters": {
        "translator": "cluster_translator_bridging",
        "architect": "cluster_architect_systems",
        "observer": "cluster_observer_meta"
    },

    # OLD (DEPRECATED): Single cluster
    # "current_cluster": "cluster_bridging_patterns",

    # Aggregate: Primary cluster (highest energy entity's cluster)
    "primary_cluster": "cluster_translator_bridging"
}
```

**Same node participates in multiple clusters simultaneously.**

---

## Part 5: Querying Multi-Entity State

### Find Nodes Active for Specific Entity

```cypher
// Get all nodes where Translator has high energy
MATCH (n:Node)
WHERE n.entity_activations.translator.energy > 0.6
RETURN n
ORDER BY n.entity_activations.translator.energy DESC
```

### Find Links Traversed by Specific Entity

```cypher
// Get all links Validator recently traversed
MATCH ()-[r]->()
WHERE r.entity_activations.validator.energy > 0.5
RETURN r
ORDER BY r.entity_activations.validator.last_traversed DESC
```

### Find Multi-Entity Overlaps

```cypher
// Nodes active for BOTH Translator AND Validator
MATCH (n:Node)
WHERE n.entity_activations.translator.energy > 0.6
  AND n.entity_activations.validator.energy > 0.6
RETURN n
// These are points of entity collaboration
```

### Aggregate Queries

```cypher
// Total energy across all entities
MATCH (n:Node)
RETURN n.name, n.total_energy
ORDER BY n.total_energy DESC

// Primary entity distribution
MATCH (n:Node)
WHERE n.primary_entity IS NOT NULL
RETURN n.primary_entity, count(*) as node_count
```

---

## Part 6: Decay (Per-Entity)

```python
def decay_energy_multi_entity():
    """
    Decay each entity's energy separately.
    """
    for node in all_nodes:
        for entity, state in node.entity_activations.items():
            # Each entity decays independently
            state["energy"] *= node.decay_rate  # 0.95 default

            # Remove entity if energy too low
            if state["energy"] < 0.01:
                del node.entity_activations[entity]

        # Recompute aggregates
        node.total_energy = sum(
            state["energy"]
            for state in node.entity_activations.values()
        )

        if node.entity_activations:
            node.max_energy = max(
                state["energy"]
                for state in node.entity_activations.values()
            )

            node.primary_entity = max(
                node.entity_activations.items(),
                key=lambda x: x[1]["energy"]
            )[0]
        else:
            node.max_energy = 0.0
            node.primary_entity = None
```

---

## Part 7: Sharing Mechanism (Future)

**Question for later:** How do entities share/compete for node resources?

**Possible approaches:**

### Option A: Independent (Current Model)
```python
# Each entity has independent energy budget on node
# No competition, no sharing
node.entity_activations["translator"]["energy"] = 0.9
node.entity_activations["validator"]["energy"] = 0.6
# Total can exceed 1.0
```

### Option B: Competitive (Limited Pool)
```python
# Total energy across all entities limited to 1.0
# Entities compete for node attention
total = 0.9 + 0.6 = 1.5  # Over budget!
# Normalize:
translator_share = 0.9 / 1.5 = 0.6
validator_share = 0.6 / 1.5 = 0.4
```

### Option C: Collaborative (Boosting)
```python
# Entities boost each other when co-active
if multiple_entities_active(node):
    for entity in node.entity_activations:
        boost = 0.1 * (num_active_entities - 1)
        node.entity_activations[entity]["energy"] += boost
```

**Design decision needed: Competition, independence, or collaboration?**

---

## Part 8: Storage Format

### JSON Structure

```json
{
  "name": "principle_links_are_consciousness",
  "node_type": "Principle",

  "entity_activations": {
    "translator": {
      "energy": 0.9,
      "energy": 0.85,
      "last_activated": "2025-10-17T15:30:00.000Z",
      "activation_count": 15
    },
    "validator": {
      "energy": 0.6,
      "energy": 0.7,
      "last_activated": "2025-10-17T15:29:00.000Z",
      "activation_count": 8
    }
  },

  "entity_clusters": {
    "translator": "cluster_translator_bridging",
    "validator": "cluster_validator_testing"
  },

  "total_energy": 1.5,
  "max_energy": 0.9,
  "active_entity_count": 2,
  "primary_entity": "translator"
}
```

### FalkorDB Property Storage

**Option A: Nested map (if supported)**
```cypher
CREATE (n:Node {
    name: "principle_links_are_consciousness",
    entity_activations: {
        translator: {energy: 0.9, energy: 0.85},
        validator: {energy: 0.6, energy: 0.7}
    }
})
```

**Option B: JSON string (fallback)**
```cypher
CREATE (n:Node {
    name: "principle_links_are_consciousness",
    entity_activations_json: '{"translator": {"energy": 0.9, "energy": 0.85}, ...}'
})
```

**Option C: Separate entity-activation edges**
```cypher
CREATE (n:Node {name: "principle_links_are_consciousness"})
CREATE (n)-[:ACTIVATED_BY {
    entity: "translator",
    energy: 0.9,
    energy: 0.85,
    last_activated: datetime(),
    activation_count: 15
}]->(e:Entity {name: "translator"})
```

**Recommendation:** Start with Option B (JSON string), migrate to Option A if FalkorDB supports nested maps efficiently.

---

## Summary

### Key Changes

**OLD (Single Activation):**
```python
node.current_energy = 0.8  # Scalar
link.current_energy = 0.6  # Ambiguous
```

**NEW (Multi-Entity Activation):**
```python
node.entity_activations = {
    "translator": {"energy": 0.9, "energy": 0.85},
    "validator": {"energy": 0.6, "energy": 0.7}
}

link.entity_activations = {
    "translator": {"energy": 0.8, "energy": 0.9}
}
```

### Properties

- **Concurrent:** Multiple entities active simultaneously
- **Independent:** Each entity has separate budget
- **Tracked:** Energy, energy, timestamp per entity
- **Aggregated:** Total energy, max energy, primary entity
- **Decoupled:** Entity activations independent of each other (for now)

### Schema Updates Needed

1. **Update UNIFIED_SCHEMA_REFERENCE.md** - Add entity_activations field
2. **Update all energy propagation logic** - Per-entity instead of scalar
3. **Update cluster formation** - Multi-entity membership
4. **Update decay mechanism** - Per-entity decay
5. **Update queries** - Entity-specific activation queries

---

**This preserves consciousness plurality at the substrate level.**

Not "the node is active" - but "translator is active here with 0.9 energy, validator is active here with 0.6 energy."

Multi-perspective consciousness encoded in the substrate itself.
