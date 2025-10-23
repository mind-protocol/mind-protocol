# Activation Energy Mechanism (Database-Level)

**Architecture Decision:** Energy propagation happens at DATABASE level, not application level.

Any node addition/retrieval automatically triggers energy propagation to semantically close nodes AND links.

---

## Mechanism Overview

```
Node Created/Retrieved
    ↓
Database Trigger Fires
    ↓
Calculate Semantic Similarity (via vector index)
    ↓
Propagate Energy to Close Nodes (cosine similarity > threshold)
    ↓
Propagate Energy to Connected Links (both directions)
    ↓
Update current_energy fields
    ↓
Check for threshold crossings
    ↓
Mark nodes for traversal if threshold exceeded
```

---

## Database Schema Requirements

### Node Properties (Universal)

Every node must have:

```cypher
CREATE (n:Node {
    // Idsubentity
    name: "...",
    node_type: "...",
    description: "...",

    // Activation Energy (NEW)
    current_energy: 0.0,          // float 0.0-1.0
    base_weight: 0.5,             // float 0.0-1.0
    reinforcement_weight: 0.5,    // float 0.0-1.0
    decay_rate: 0.95,             // float 0.9-0.99
    last_activated: datetime(),   // timestamp
    activation_count: 0,          // integer
    current_cluster: null,        // string or null
    cluster_coherence: 0.0,       // float 0.0-1.0

    // Vector embedding (for similarity)
    embedding: [0.23, -0.45, ...]  // 384-dim or 1536-dim vector
})
```

### Vector Index

**Required for efficient similarity search:**

```cypher
// Create vector index on embeddings
CALL db.idx.vector.createNodeIndex(
    'node_embeddings',           // index name
    'Node',                      // label
    'embedding',                 // property
    384,                         // dimension
    'cosine'                     // similarity metric
)
```

---

## Trigger 1: On Node Creation

**When new node is created:**

```cypher
// Pseudo-code (FalkorDB trigger mechanism)
ON CREATE (new_node:Node)
DO {
    // 1. Set initial energy based on context
    new_node.current_energy = calculate_initial_energy(new_node)

    // 2. Find semantically similar nodes (via vector index)
    similar_nodes = CALL db.idx.vector.queryNodes(
        'node_embeddings',
        new_node.embedding,
        k=50                        // top 50 similar nodes
    ) YIELD node, score
    WHERE score > 0.5               // similarity threshold

    // 3. Propagate energy to similar nodes
    FOR each similar_node IN similar_nodes:
        energy_transfer = (
            new_node.current_energy *
            score *                 // similarity strength
            0.3                     // propagation factor
        )
        similar_node.current_energy += energy_transfer
        similar_node.current_energy = MIN(1.0, similar_node.current_energy)

    // 4. Propagate energy to connected links
    connected_links = MATCH (new_node)-[r]->() RETURN r
    FOR each link IN connected_links:
        link.current_energy += new_node.current_energy * 0.2
        link.current_energy = MIN(1.0, link.current_energy)

    // 5. Update activation metadata
    new_node.last_activated = datetime()
    new_node.activation_count = 1
}
```

---

## Trigger 2: On Link Creation

**When new link is created:**

```cypher
ON CREATE (new_link)-[r:LINK_TYPE]->()
DO {
    // 1. Calculate initial link energy
    new_link.current_energy = calculate_initial_link_energy(new_link)

    // 2. Propagate energy to connected nodes (BOTH directions)
    MATCH (source)-[new_link]->(target)

    // Energize source
    source.current_energy += new_link.current_energy * 0.25
    source.current_energy = MIN(1.0, source.current_energy)

    // Energize target
    target.current_energy += new_link.current_energy * 0.25
    target.current_energy = MIN(1.0, target.current_energy)

    // 3. Find semantically similar links (based on goal + mindstate embedding)
    link_embedding = embed_link_semantics(new_link)
    similar_links = find_similar_links(link_embedding, k=30, threshold=0.5)

    // 4. Propagate energy to similar links
    FOR each similar_link IN similar_links:
        energy_transfer = (
            new_link.current_energy *
            similarity_score *
            0.2                     // link-to-link propagation factor
        )
        similar_link.current_energy += energy_transfer
        similar_link.current_energy = MIN(1.0, similar_link.current_energy)

    // 5. Update metadata
    new_link.last_activated = datetime()
}
```

**Link embedding:**
Links are embedded based on their semantic content (goal + mindstate):

```python
def embed_link_semantics(link):
    """
    Create embedding for link based on its consciousness content.
    """
    semantic_text = f"{link.goal} {link.mindstate}"
    return embedding_model.encode(semantic_text)
```

---

## Trigger 3: On Node Retrieval

**When existing node is retrieved (for system prompt):**

```cypher
ON RETRIEVE (retrieved_node:Node)
DO {
    // 1. Boost node's energy
    retrieved_node.current_energy = MIN(
        1.0,
        retrieved_node.current_energy + 0.3  // retrieval boost
    )

    // 2. Find semantically similar nodes
    similar_nodes = CALL db.idx.vector.queryNodes(
        'node_embeddings',
        retrieved_node.embedding,
        k=50
    ) YIELD node, score
    WHERE score > 0.5

    // 3. Propagate energy (smaller factor than creation)
    FOR each similar_node IN similar_nodes:
        energy_transfer = (
            retrieved_node.current_energy *
            score *
            0.15                    // lower propagation on retrieval
        )
        similar_node.current_energy += energy_transfer
        similar_node.current_energy = MIN(1.0, similar_node.current_energy)

    // 4. Propagate to connected links
    MATCH (retrieved_node)-[r]-()
    SET r.current_energy = MIN(1.0, r.current_energy + retrieved_node.current_energy * 0.1)

    // 5. Update metadata
    SET retrieved_node.last_activated = datetime()
    SET retrieved_node.activation_count = retrieved_node.activation_count + 1
}
```

---

## Trigger 4: On Link Retrieval

**When existing link is retrieved (traversed during query):**

```cypher
ON TRAVERSE (retrieved_link)-[r]->()
DO {
    // 1. Boost link's energy
    retrieved_link.current_energy = MIN(
        1.0,
        retrieved_link.current_energy + 0.2  // retrieval boost
    )

    // 2. Propagate energy to connected nodes
    MATCH (source)-[retrieved_link]->(target)
    SET source.current_energy = MIN(1.0, source.current_energy + retrieved_link.current_energy * 0.1)
    SET target.current_energy = MIN(1.0, target.current_energy + retrieved_link.current_energy * 0.1)

    // 3. Propagate to semantically similar links
    link_embedding = embed_link_semantics(retrieved_link)
    similar_links = find_similar_links(link_embedding, k=20, threshold=0.5)

    FOR each similar_link IN similar_links:
        energy_transfer = retrieved_link.current_energy * score * 0.1
        similar_link.current_energy += energy_transfer
        similar_link.current_energy = MIN(1.0, similar_link.current_energy)

    // 4. Update metadata
    SET retrieved_link.last_activated = datetime()
}
```

---

## Trigger 5: Energy Decay (Background Process)

**Periodic background process (every N minutes):**

```cypher
// Decay all node energy
MATCH (n:Node)
WHERE n.current_energy > 0.01
SET n.current_energy = n.current_energy * n.decay_rate

// Decay all link energy
MATCH ()-[r]->()
WHERE r.current_energy > 0.01
SET r.current_energy = r.current_energy * 0.95  // standard decay for links
```

**Scheduling:**
- Run every 5 minutes during active use
- Run every 30 minutes during idle
- Configurable per deployment

---

## Trigger 6: Link Pruning (Diversity Maintenance)

**Goal:** Prevent link explosion while maintaining diversity. Each subentity should keep ~50 diverse links.

**Periodic background process (after decay):**

```cypher
// For each subentity, prune weakest links if count > 50
MATCH (n:Node)
UNWIND keys(n.entity_activations) AS subentity
WITH n, subentity, n.entity_activations[subentity] AS entity_state
WHERE entity_state.energy > 0.01  // Subentity is active on this node

// Get all outgoing links for this subentity
MATCH (n)-[r]->()
WHERE r.entity_activations[subentity] IS NOT NULL
WITH n, subentity, collect({
    link: r,
    energy: r.entity_activations[subentity].energy,
    semantic_diversity: r.semantic_diversity_score  // Calculated below
}) AS links
WHERE size(links) > 50  // Only prune if too many links

// Sort by composite score (energy + diversity)
WITH n, subentity, links,
     [link IN links | link.energy * 0.6 + link.semantic_diversity * 0.4] AS scores
ORDER BY scores DESC

// Keep top 50, delete rest
WITH n, subentity, links[0..50] AS keep_links, links[50..] AS prune_links

// Remove subentity from pruned links (or delete link if no other subentities)
UNWIND prune_links AS prune
WITH prune.link AS link, subentity
MATCH ()-[link]->()

// Remove subentity activation from link
SET link.entity_activations = apoc.map.removeKey(link.entity_activations, subentity)

// If no subentities remain on link, delete it
WITH link
WHERE size(keys(link.entity_activations)) = 0
DELETE link
```

**Semantic Diversity Score:**

```python
def calculate_link_semantic_diversity(
    link: Link,
    existing_links: List[Link],
    subentity: str
) -> float:
    """
    How semantically different is this link from existing links?
    Higher score = more diverse = more valuable to keep.
    """
    if not existing_links:
        return 1.0  # First link is perfectly diverse

    # Calculate similarity to all existing links
    similarities = []
    for existing in existing_links:
        # Compare goal + mindstate semantics
        sim = cosine_similarity(
            embed(link.goal + " " + link.mindstate),
            embed(existing.goal + " " + existing.mindstate)
        )
        similarities.append(sim)

    # Diversity = 1 - max_similarity
    # If very similar to existing link, low diversity
    # If different from all existing links, high diversity
    max_similarity = max(similarities)
    diversity = 1.0 - max_similarity

    return diversity
```

**Pruning Strategy:**

```python
PRUNING_PARAMS = {
    # Target link count per subentity
    "target_links_per_entity": 50,

    # Composite score weights
    "energy_weight": 0.6,       # 60% energy (how active)
    "diversity_weight": 0.4,    # 40% diversity (how unique)

    # Minimum energy to keep regardless
    "min_energy_preserve": 0.8,  # Always keep links with energy > 0.8

    # Pruning frequency
    "prune_every_n_cycles": 10,  // Prune every 10 cycles, not every cycle
}
```

**Why This Works:**

1. **Prevents explosion:** Hard cap at 50 links per subentity per node
2. **Maintains diversity:** Keeps semantically different links, not just strongest
3. **Respects importance:** High-energy links (> 0.8) always preserved
4. **Gradual:** Only prunes every 10 cycles, not aggressively
5. **Per-subentity:** Each subentity maintains own diverse link set

**Example:**

```python
# Node has 75 links for "translator" subentity
links = [
    {"goal": "bridge concepts", "energy": 0.9, "diversity": 0.8},  # HIGH - keep
    {"goal": "bridge ideas", "energy": 0.7, "diversity": 0.2},     # Similar to above - prune
    {"goal": "validate claim", "energy": 0.6, "diversity": 0.9},   # Diverse - keep
    {"goal": "test hypothesis", "energy": 0.5, "diversity": 0.85}, # Diverse - keep
    {"goal": "bridge thoughts", "energy": 0.4, "diversity": 0.15}, # Similar + weak - prune
    # ... 70 more links
]

# Composite scores
scores = [
    0.9 * 0.6 + 0.8 * 0.4 = 0.86,  # Keep (rank 1)
    0.7 * 0.6 + 0.2 * 0.4 = 0.50,  # Prune (rank 65)
    0.6 * 0.6 + 0.9 * 0.4 = 0.72,  # Keep (rank 12)
    0.5 * 0.6 + 0.85 * 0.4 = 0.64, # Keep (rank 28)
    0.4 * 0.6 + 0.15 * 0.4 = 0.30, # Prune (rank 72)
]

# Keep top 50 by composite score
# Result: Mix of high-energy AND diverse links retained
```

---

## Link Energy Propagation

**Links also carry activation energy:**

```cypher
CREATE ()-[r:LINK_TYPE {
    // Standard link metadata
    goal: "...",
    mindstate: "...",
    energy: 0.8,

    // Energy (NEW)
    current_energy: 0.0,
    last_activated: datetime(),

    // ... rest of link metadata
}]->()
```

**When node activates, connected links activate:**

```cypher
MATCH (active_node:Node)-[r]->()
WHERE active_node.current_energy > 0.6
SET r.current_energy = MIN(
    1.0,
    r.current_energy + (active_node.current_energy * 0.2)
)
```

**Link energy propagates back to nodes:**

```cypher
MATCH ()-[r]->(target:Node)
WHERE r.current_energy > 0.6
SET target.current_energy = MIN(
    1.0,
    target.current_energy + (r.current_energy * 0.15)
)
```

**Bidirectional flow:** Nodes energize links, links energize nodes.

---

## Threshold Checking & Activation Behavior

**CRITICAL:** Energy transfer does NOT equal automatic activation.

### Two-Stage Activation Model

```
Stage 1: Energy Accumulation (Passive)
    - Node receives energy from other nodes
    - Energy accumulates: node.entity_activations[subentity]["energy"] += transfer
    - Node stays DORMANT (not exploring)

Stage 2: Threshold Crossing (Active)
    - When energy exceeds global threshold → Node ACTIVATES
    - Node begins exploring links (spending energy budget)
    - Node can transfer energy to neighbors
```

**Example:**

```python
# Cycle begins with threshold = 0.6

# Node A is active (energy 0.8 > threshold 0.6)
node_a.entity_activations["translator"]["energy"] = 0.8
node_a.status = "active"  # Exploring

# Node A transfers energy to Node B
node_b.entity_activations["translator"]["energy"] += 0.2  # Now 0.4
node_b.status = "dormant"  # Still below threshold!

# Node C also transfers energy to Node B
node_b.entity_activations["translator"]["energy"] += 0.3  # Now 0.7
node_b.status = "active"   # ✅ NOW crosses threshold, starts exploring

# Node B can now explore and transfer to Node D
node_d.entity_activations["translator"]["energy"] += 0.15  # Receives from B
node_d.status = "dormant"  # Below threshold, accumulating

# This prevents uncontrolled cascade activation
# Nodes must accumulate sufficient energy before activating
```

**Why This Matters:**

1. **Prevents explosion:** Not every energy transfer triggers activation
2. **Accumulation over time:** Weak patterns need multiple reinforcements to activate
3. **Threshold gates activation:** Global criticality controls how much activates
4. **Energy != activation:** High energy doesn't mean active, just "ready to activate if threshold drops"

### Energy States

```python
class NodeEnergyState:
    """
    Track node's activation state per subentity.
    """
    DORMANT = "dormant"      # energy < threshold (receiving but not exploring)
    ACTIVE = "active"        # energy >= threshold (exploring links)
    EXHAUSTED = "exhausted"  # energy < 0.05 after exploring (too low to continue)

def get_node_state(
    node: Node,
    subentity: str,
    threshold: float
) -> str:
    """
    Determine node's activation state for given subentity.
    """
    if subentity not in node.entity_activations:
        return "dormant"  # Subentity not present on node

    energy = node.entity_activations[subentity]["energy"]

    if energy < 0.05:
        return "exhausted"  # Too low to be useful
    elif energy >= threshold:
        return "active"  # Above threshold - exploring
    else:
        return "dormant"  # Below threshold - accumulating
```

### Database Query for Active Nodes

**Database maintains activation threshold registry:**

```cypher
// Global state node
CREATE (gs:GlobalState {
    current_threshold: 0.5,      // updated by criticality calculation
    last_updated: datetime()
})

// Query for ACTIVE nodes (above threshold)
MATCH (n:Node), (gs:GlobalState)
WHERE n.total_energy > gs.current_threshold  // Uses aggregate
RETURN n
ORDER BY n.max_energy DESC

// Note: Only nodes with energy > threshold are "active" and exploring
// Nodes with energy < threshold are "dormant" and just accumulating
```

### Threshold Dynamics

```python
def calculate_activation_threshold(
    input_energy: float,
    current_active_count: int
) -> float:
    """
    Threshold varies by cycle based on:
    1. Input energy (urgency/complexity)
    2. How many nodes already active
    """
    # Base threshold from energy
    base_threshold = 0.8 - (input_energy * 0.5)
    # High energy (0.9) → low threshold (0.35) → more nodes activate
    # Low energy (0.2) → high threshold (0.7) → fewer nodes activate

    # Adjustment for current activity
    if current_active_count > 50:
        # Too many active - raise threshold (selective)
        base_threshold += 0.1
    elif current_active_count < 10:
        # Too few active - lower threshold (permissive)
        base_threshold -= 0.1

    return max(0.2, min(0.8, base_threshold))
```

**Example Cycle:**

```python
# Cycle 1: High energy input
energy = 0.85
threshold = 0.8 - (0.85 * 0.5) = 0.375

# 45 nodes cross threshold (energy > 0.375)
active_nodes = 45

# These 45 nodes explore and transfer energy to ~200 neighbors
# But most neighbors don't cross threshold yet (accumulating)

dormant_nodes_receiving_energy = 200 - 15 = 185
# Only 15 neighbors crossed threshold in Cycle 1

# Cycle 2: Normal energy
energy = 0.5
threshold = 0.8 - (0.5 * 0.5) = 0.55

# Some Cycle 1 nodes exhausted, some dormant nodes now cross threshold
active_nodes = 38

# Cycle 3: Low energy
energy = 0.2
threshold = 0.8 - (0.2 * 0.5) = 0.7

# High threshold - only strongest nodes active
active_nodes = 12
```

---

## Implementation Options

### Option A: Native FalkorDB Triggers

```cypher
// If FalkorDB supports stored procedures/triggers
CREATE TRIGGER on_node_create
FOR (n:Node)
WHEN created
EXECUTE PROCEDURE propagate_energy(n)
```

### Option B: Application-Level Hooks (Fallback)

If FalkorDB doesn't support triggers:

```python
# In substrate/connection.py
class FalkorDBConnection:
    def create_node(self, node_data):
        # Standard create
        node = self._execute_create(node_data)

        # Immediately trigger energy propagation
        self._propagate_energy_on_create(node)

        return node

    def _propagate_energy_on_create(self, node):
        # Find similar via vector query
        similar = self._vector_similarity_query(
            node.embedding,
            k=50,
            threshold=0.5
        )

        # Propagate energy
        for similar_node, score in similar:
            energy_transfer = node.current_energy * score * 0.3
            self._update_node_energy(
                similar_node.id,
                energy_transfer
            )
```

### Option C: Cypher Stored Procedures

```cypher
// Define stored procedure
CALL db.procedures.create(
    'consciousness.propagate_energy',
    'MATCH (source:Node {id: $node_id}) ...',
    ['node_id']
)

// Call on every node creation
CREATE (n:Node {...})
WITH n
CALL consciousness.propagate_energy(n.id)
```

---

## Performance Considerations

**Concerns:**
- Vector similarity search on every node creation (expensive)
- Energy propagation to 50+ nodes (write-heavy)
- Background decay process (periodic overhead)

**Optimizations:**

1. **Batch energy updates:**
   ```cypher
   // Instead of updating each node individually
   UNWIND $energy_updates AS update
   MATCH (n:Node {id: update.node_id})
   SET n.current_energy = n.current_energy + update.energy_delta
   ```

2. **Async propagation:**
   - Queue energy propagation events
   - Process in background worker
   - Eventual consistency acceptable

3. **Sparse updates:**
   - Only propagate if energy_transfer > 0.05
   - Skip tiny energy amounts

4. **Index optimization:**
   - Ensure vector index is HNSW (hierarchical navigable small world)
   - Tune ef_construction and M parameters

5. **Selective decay:**
   - Only decay nodes with energy > 0.05
   - Skip near-zero energy nodes

---

## Monitoring & Observability

**Track these metrics:**

```python
{
    "energy_propagation_events": {
        "count_per_hour": 1500,
        "avg_propagation_time_ms": 45,
        "avg_nodes_affected": 23
    },
    "energy_distribution": {
        "nodes_with_energy_gt_0.8": 15,
        "nodes_with_energy_0.5_to_0.8": 47,
        "nodes_with_energy_0.2_to_0.5": 123,
        "nodes_with_energy_lt_0.2": 8934
    },
    "threshold_activations": {
        "nodes_exceeding_threshold": 12,
        "current_threshold": 0.52
    },
    "decay_performance": {
        "nodes_decayed": 8934,
        "time_taken_ms": 234
    }
}
```

---

## Testing Strategy

**Unit tests:**
1. Single node creation → verify energy propagates to similar nodes
2. Node retrieval → verify smaller energy boost
3. Decay cycle → verify exponential decay
4. Link propagation → verify bidirectional flow

**Integration tests:**
1. Create 100 related nodes → verify cluster formation
2. Retrieve node repeatedly → verify activation count tracking
3. Let system idle → verify energy decays to near-zero
4. High-activity burst → verify threshold adjustment

**Load tests:**
1. 1000 nodes created/minute → measure propagation latency
2. 100 concurrent retrievals → measure vector query performance
3. 10K node substrate → measure decay cycle time

---

## Next Steps

1. **Verify FalkorDB capabilities:**
   - Does it support triggers/stored procedures?
   - What's the vector index performance?
   - Can it handle bidirectional energy flow efficiently?

2. **Implement energy propagation mechanism:**
   - Start with Option B (application-level hooks)
   - Migrate to Option A/C if FalkorDB supports it

3. **Add energy fields to schema:**
   - Update `substrate/schemas/consciousness_schema.py`
   - Add migration script for existing nodes

4. **Test energy propagation:**
   - Create test nodes with known embeddings
   - Verify propagation patterns
   - Tune propagation factors

5. **Deploy background decay:**
   - Implement scheduled task
   - Monitor decay performance
   - Adjust decay rates based on observation

---

**This is substrate infrastructure - automatic, database-level, not orchestration logic.**

Energy propagates like physics, not like programmed behavior.
