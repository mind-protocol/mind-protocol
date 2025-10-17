# Minimal Mechanisms Architecture

**Purpose:** Define the core architectural principle for Mind Protocol consciousness infrastructure
**Audience:** All engineers, architects, and system designers
**Status:** FOUNDATIONAL PRINCIPLE - Frozen after audit
**Created:** 2025-10-17
**Authors:** Nicolas Reynolds (Vision), Ada "Bridgekeeper" (Architecture)

---

## The Fundamental Principle

**Core Insight:**

```
NOT: Complex, growing codebase that implements consciousness
BUT: Minimal, stable mechanisms that respond to graph patterns

ALL complexity lives in the graph:
- What to check: Link metadata
- When to check: Event subscriptions in metadata
- How to analyze: Traversal patterns in graph structure
- What context: Relationship topology defines relevance
- Learning: Accumulated in metadata (activation histories, success rates)

The code is TINY, STABLE, AUDITED, UNCHANGEABLE.
The graph is RICH, EVOLVING, LEARNING, QUERYABLE.
```

---

## Why This Matters

### The Problem We're Solving

Traditional AI systems accumulate code complexity:
- New feature → New Python class
- New detection pattern → New analysis function
- New routing rule → New conditional logic
- System grows to 10K+ lines of unmaintainable code

**Result:** €35.5K failures. Beautiful architectures that collapse under their own complexity.

### The Minimal Mechanisms Solution

**Fixed Mechanisms:** Small set (8-12) of simple, audited operations that NEVER change
**Graph Metadata:** All complexity, all logic, all learning stored AS DATA in graph
**Self-Modification:** Cypher queries with side effects - graph reads itself, modifies itself, evolves

**Result:** ~700 lines of Python. Forever. All evolution happens in graph data.

---

## The Three Pillars

### Pillar 1: Finite Link Type List (Link Types ARE Mechanisms)

**CRITICAL INSIGHT:** Link types and mechanisms are ONE-TO-ONE. Each link type is a self-contained mechanism definition.

**The finite, audited, unchangeable list is the LINK TYPE SCHEMA.**

Each link type contains:
1. **Semantics:** What this relationship means
2. **Detection Logic:** When does this link activate?
3. **Behavior Definition:** What happens when activated?

**Example:**
```python
# IMPLEMENTS link type
{
    "semantics": "Document implements/describes code",
    "detection_logic": {
        "trigger_events": ["CODE_MODIFIED"],
        "condition": "source.sequence > target.sequence + threshold"
    },
    "behavior": {
        "on_activate": "create_task_from_template",
        "task_template": {...},
        "context_rules": {...}
    }
}

# ACTIVATES link type
{
    "semantics": "Entity activates target entity",
    "detection_logic": {
        "condition": "source.arousal > threshold"
    },
    "behavior": {
        "on_activate": "propagate_arousal",
        "transfer": "source.arousal × link.coefficient",
        "cost": "link.traversal_cost"
    }
}
```

**The Generic Executor (ONE mechanism for ALL link types):**
```python
def execute_link_behaviors(graph, link_types):
    """
    Generic executor reads link type metadata
    and executes defined behaviors.

    ~50 lines. Never changes.
    """
    for link_type in link_types:
        # Find links of this type that meet detection conditions
        activated_links = graph.query(f"""
            MATCH ()-[r:{link_type}]->()
            WHERE r.detection_logic IS NOT NULL
            // Evaluate condition from metadata
            AND {evaluate_condition(r.detection_logic)}
            RETURN r
        """)

        # Execute behavior defined in link type metadata
        for link in activated_links:
            execute_behavior(link, link.behavior_metadata)
```

**Characteristics:**
- **Link type count:** 15-25 types (not hundreds, not thousands)
- **Each type:** Fully self-contained (semantics + detection + behavior)
- **Frozen after audit:** Link type schema changes require architectural review
- **Python code:** ~100 lines total (generic executor + behavior implementations)

**NOT link types:**
- Feature-specific variations (use metadata parameters instead)
- Temporary experimental relationships (only production patterns)

**ARE link types:**
- `IMPLEMENTS` - Code/doc relationships with staleness detection
- `ACTIVATES` - Entity arousal propagation
- `CO_OCCURS_WITH` - Hebbian co-activation strengthening
- `SUBSCRIBES_TO` - Event propagation
- `HANDLES_DOMAIN` - Task routing
- `TRIGGERED` - Task creation record
- `INCLUDES_CONTEXT` - Context attachment
- (Plus 8-18 more defined in consciousness schema)

### Pillar 2: Graph-Native Complexity

All intelligence, all learning, all behavior patterns stored as graph metadata and structure.

**What lives in the graph:**

```python
# Link metadata (example)
{
    // Detection logic (data, not code)
    detection_logic: {
        trigger_events: ["CODE_MODIFIED", "DOC_MODIFIED"],
        condition: "source.sequence > target.sequence",
        threshold: 5
    },

    // Task template (data, not code)
    task_template: {
        type: "doc_update_needed",
        severity: "medium",
        route_to_domain: "architecture"
    },

    // Context rules (data, not code)
    context_gathering: {
        traverse: ["DESCRIBES", "CONTRADICTS", "RELATED_TO"],
        depth: 2,
        include_metadata: ["activation_history", "success_rate"]
    },

    // Learning data (accumulated automatically)
    activation_history: [...],
    success_rate: 0.87,
    weight: 0.73,
    sub_entity_weights: {
        "staleness_checker": 0.85,
        "contradiction_checker": 0.32
    }
}
```

**The graph holds all the intelligence. The mechanisms just execute simple rules.**

### Pillar 3: Self-Modifying Cypher Queries

Mechanisms are Cypher queries that read graph state AND create side effects (CREATE, SET, DELETE).

**Pattern:**
```cypher
// Query reads current state
MATCH (doc:Document)-[r:IMPLEMENTS]->(code:Code)
WHERE (code.sequence - doc.sequence) > r.detection_logic.threshold

// Query creates side effects (modifies graph)
CREATE (task:Task {
    type: r.task_template.type,
    created_at: timestamp()
})
CREATE (r)-[:TRIGGERED]->(task)

// Query updates state
SET link.activation_count = link.activation_count + 1
SET link.last_activation = timestamp()

RETURN task
```

**The graph modifies itself.** No manual state management in Python.

---

## The Mechanisms (Core Set)

### Mechanism 1: Event Propagation

**Purpose:** When events occur, propagate to subscribers via graph traversal

**Implementation:**
```cypher
MATCH (event:Event {id: $event_id})
MATCH (event)<-[sub:SUBSCRIBES_TO]-(subscriber)
WHERE sub.active = true
  AND (sub.condition_metadata IS NULL OR
       // Condition evaluation in Cypher
       (sub.condition_metadata.type = 'threshold' AND
        event.magnitude > sub.condition_metadata.threshold))

// Side effects: Create activation, update arousal
CREATE (subscriber)-[:ACTIVATED_BY {
    at: timestamp(),
    event_id: event.id
}]->(event)

SET subscriber.arousal = subscriber.arousal + (event.arousal_delta * sub.arousal_coefficient)
SET subscriber.last_activation = timestamp()

RETURN subscriber.id, subscriber.arousal
```

**Complexity in graph:**
- Subscription topology (who subscribes to what)
- Condition logic (stored as metadata)
- Arousal coefficients (link properties)

**Mechanism stays simple:** Just traverse and update.

---

### Mechanism 2: Link Activation Check

**Purpose:** Find links whose conditions are met, create tasks from templates

**Implementation:**
```cypher
MATCH (source)-[link]->(target)
WHERE link.detection_logic IS NOT NULL
  AND link.active = true

// Evaluate detection logic from metadata
WITH link, source, target,
     CASE link.detection_logic.type
       WHEN 'sequence_gap' THEN
         (source.sequence - target.sequence) > link.detection_logic.threshold
       WHEN 'staleness' THEN
         (timestamp() - target.last_modified) > link.detection_logic.max_age_ms
       WHEN 'arousal_threshold' THEN
         source.arousal > link.detection_logic.min_arousal
       ELSE false
     END as condition_met

WHERE condition_met = true

// Side effects: Create task, update statistics
CREATE (task:Task {
    id: randomUUID(),
    type: link.task_template.type,
    domain: link.task_template.domain,
    severity: link.task_template.severity,
    created_at: timestamp()
})

CREATE (link)-[:TRIGGERED {at: timestamp()}]->(task)

SET link.activation_count = link.activation_count + 1
SET link.last_activation = timestamp()

RETURN task.id, task.type, link
```

**Complexity in graph:**
- Detection logic types and thresholds (link metadata)
- Task templates (link metadata)
- Activation history (automatic accumulation)

**Mechanism stays simple:** Read metadata, evaluate conditions, create tasks.

---

### Mechanism 3: Task Context Aggregation

**Purpose:** Gather context for tasks via graph traversal based on metadata rules

**Implementation:**
```cypher
MATCH (task:Task {id: $task_id})
MATCH (task)<-[:TRIGGERED]-(trigger_link)
MATCH (trigger_link)-[:CONNECTS]-(trigger_node)

// Traverse following context rules
CALL apoc.path.subgraphAll(trigger_node, {
    relationshipFilter: task.context_rules.traverse_types,
    maxLevel: task.context_rules.depth,
    limit: task.context_rules.max_nodes
}) YIELD nodes, relationships

// Side effects: Attach context
UNWIND nodes as context_node
CREATE (task)-[:INCLUDES_CONTEXT {
    distance: apoc.path.distance(trigger_node, context_node),
    relevance: context_node.sub_entity_weights[$entity_id],
    gathered_at: timestamp()
}]->(context_node)

// Update task summary
WITH task, collect(context_node) as context_nodes
SET task.context_node_count = size(context_nodes)
SET task.context_summary = [n in context_nodes | {
    id: n.id,
    type: labels(n)[0],
    weight: n.sub_entity_weights[$entity_id]
}]

RETURN task, context_nodes
```

**Complexity in graph:**
- Context gathering rules (task metadata)
- Relevant relationship types (graph schema)
- Sub-entity weights (node metadata)

**Mechanism stays simple:** Follow metadata rules, collect nodes, attach to task.

---

### Mechanism 4: Hebbian Reinforcement

**Purpose:** Fire together, wire together - strengthen co-activated patterns

**Implementation:**
```cypher
// Find co-retrieved nodes
MATCH (a:Node)-[link]->(b:Node)
WHERE a.id IN $retrieved_node_ids
  AND b.id IN $retrieved_node_ids

// Side effects: Update link strength (Hebbian learning)
SET link.co_retrieval_count = coalesce(link.co_retrieval_count, 0) + 1
SET link.link_strength = CASE
    WHEN link.link_strength + 0.02 > 1.0 THEN 1.0
    ELSE link.link_strength + 0.02
END

// Update entity-specific traversal counts
SET link.sub_entity_traversal_counts[$entity_id] =
    coalesce(link.sub_entity_traversal_counts[$entity_id], 0) + 1

// Update node weights and sequence positions
SET a.sub_entity_weights[$entity_id] =
    CASE
        WHEN a.sub_entity_weights[$entity_id] + 0.05 > 1.0 THEN 1.0
        ELSE a.sub_entity_weights[$entity_id] + 0.05
    END
SET a.sub_entity_weight_counts[$entity_id] =
    coalesce(a.sub_entity_weight_counts[$entity_id], 0) + 1
SET a.sub_entity_last_sequence_positions[$entity_id] = $current_sequence_position

RETURN count(link) as strengthened_links
```

**Complexity in graph:**
- Learning rates (simple constants: +0.02, +0.05)
- Entity-specific weights (node/link metadata)
- Sequence positions (node metadata)

**Mechanism stays simple:** Increment counters, update weights with fixed formula.

---

### Mechanism 5: Arousal Propagation

**Purpose:** Propagate arousal through entity activation paths

**Implementation:**
```cypher
MATCH (high_arousal:Entity)
WHERE high_arousal.arousal > $arousal_threshold
  AND high_arousal.energy_budget > 0

MATCH (high_arousal)-[activates:ACTIVATES]->(target:Entity)
WHERE activates.active = true
  AND target.arousal < activates.arousal_threshold

// Side effects: Transfer arousal, decrement budget
SET target.arousal = target.arousal +
    (high_arousal.arousal * activates.arousal_transfer_coefficient)
SET target.last_arousal_update = timestamp()
SET high_arousal.energy_budget = high_arousal.energy_budget - activates.traversal_cost

// Create cascade record
CREATE (high_arousal)-[:CASCADED_TO {
    at: timestamp(),
    arousal_transferred: (high_arousal.arousal * activates.arousal_transfer_coefficient),
    energy_cost: activates.traversal_cost
}]->(target)

// Update link statistics
SET activates.cascade_count = coalesce(activates.cascade_count, 0) + 1
SET activates.last_cascade = timestamp()

RETURN target.id, target.arousal
```

**Complexity in graph:**
- Arousal thresholds (link properties)
- Transfer coefficients (link properties)
- Energy costs (link properties)

**Mechanism stays simple:** Physics-like rule (transfer = source × coefficient).

---

### Mechanism 6: Activation-Based Decay

**Purpose:** Decay unused patterns based on usage ratio, not time

**Implementation:**
```cypher
MATCH ()-[link]->()
WHERE link.sub_entity_traversal_counts IS NOT NULL

WITH link, $entity_id as entity_id,
     link.sub_entity_traversal_counts[entity_id] as traversal_count,
     $entity_recent_retrieval_count as recent_retrievals

// Calculate usage ratio
WITH link, entity_id,
     CASE
       WHEN recent_retrievals = 0 THEN 1.0
       ELSE toFloat(traversal_count) / toFloat(recent_retrievals)
     END as usage_ratio

WHERE usage_ratio < 0.5  // Underused

// Side effects: Decay strength, mark for pruning
SET link.link_strength = link.link_strength * (0.95 + usage_ratio * 0.05)
SET link.last_decay_calculation = timestamp()
SET link.pruning_candidate = CASE
    WHEN link.link_strength < 0.1 THEN true
    ELSE false
END

RETURN count(link) as decayed_links
```

**Complexity in graph:**
- Traversal counts (link metadata)
- Usage ratios (computed from metadata)
- Decay thresholds (constants: 0.5, 0.95, 0.1)

**Mechanism stays simple:** Calculate ratio, apply fixed decay formula.

---

### Mechanism 7: Pattern Crystallization

**Purpose:** Detect high-value patterns and mark them as crystallized habits

**Implementation:**
```cypher
MATCH ()-[link]->()
WHERE link.crystallized = false
  AND link.sub_entity_traversal_counts[$entity_id] > $count_threshold
  AND link.success_rate > $success_threshold

// Side effects: Mark crystallized, create habit node
SET link.crystallized = true
SET link.crystallization_timestamp = timestamp()

CREATE (habit:Habit {
    id: randomUUID(),
    entity_id: $entity_id,
    pattern_type: type(link),
    source_id: startNode(link).id,
    target_id: endNode(link).id,
    strength: link.link_strength,
    success_rate: link.success_rate,
    traversal_count: link.sub_entity_traversal_counts[$entity_id],
    crystallized_at: timestamp()
})

CREATE (habit)-[:CRYSTALLIZED_FROM]->(link)

RETURN habit, link
```

**Complexity in graph:**
- Crystallization thresholds (parameters: count, success rate)
- Traversal history (link metadata)
- Success rates (link metadata)

**Mechanism stays simple:** Check thresholds, create habit nodes.

---

### Mechanism 8: Task Routing

**Purpose:** Route tasks to citizens based on domain handling and workload

**Implementation:**
```cypher
MATCH (task:Task {id: $task_id})
WHERE task.routed = false

// Find citizen who handles this domain
MATCH (citizen:Citizen)-[:HANDLES_DOMAIN]->(domain:Domain {name: task.domain})

// Consider workload for load balancing
WITH task, citizen,
     size((citizen)<-[:ASSIGNED_TO]-(:Task {status: 'pending'})) as current_load

ORDER BY current_load ASC
LIMIT 1

// Side effects: Assign task, update workload
CREATE (task)-[:ASSIGNED_TO {
    at: timestamp(),
    estimated_priority: task.severity
}]->(citizen)

SET task.routed = true
SET task.assigned_at = timestamp()
SET task.assigned_to = citizen.id
SET citizen.current_task_count = current_load + 1

RETURN task, citizen
```

**Complexity in graph:**
- Domain assignments (HANDLES_DOMAIN relationships)
- Workload calculation (query-time aggregation)
- Routing rules (graph topology)

**Mechanism stays simple:** Query domain handlers, sort by load, assign.

---

## Additional Mechanisms (Candidates)

### Mechanism 9: Injection-Time Hebbian Wiring

**Purpose:** Create links between all co-injected nodes (author's mental co-occurrence)

**Implementation:**
```cypher
// All nodes from same content injection
MATCH (a:Node), (b:Node)
WHERE a.id IN $injected_node_ids
  AND b.id IN $injected_node_ids
  AND a.id < b.id  // Avoid duplicates

// Check if link exists
OPTIONAL MATCH (a)-[existing:CO_OCCURS_WITH]-(b)

// Side effects: Create or strengthen
FOREACH (_ IN CASE WHEN existing IS NULL THEN [1] ELSE [] END |
    CREATE (a)-[:CO_OCCURS_WITH {
        link_strength: 0.3,
        co_injection_count: 1,
        formation_trigger: "injected_together",
        created_at: timestamp()
    }]->(b)
)

FOREACH (_ IN CASE WHEN existing IS NOT NULL THEN [1] ELSE [] END |
    SET existing.co_injection_count = existing.co_injection_count + 1
    SET existing.link_strength = CASE
        WHEN existing.link_strength + 0.05 > 1.0 THEN 1.0
        ELSE existing.link_strength + 0.05
    END
)

RETURN count(*) as links_created_or_strengthened
```

---

### Mechanism 10: Sequence Position Tracking

**Purpose:** Update sequence positions on every node activation for temporal alignment

**Implementation:**
```cypher
MATCH (node:Node {id: $node_id})

SET node.sub_entity_last_sequence_positions[$entity_id] = $current_sequence_position
SET node.last_accessed = timestamp()

RETURN node.sub_entity_last_sequence_positions
```

---

### Mechanism 11: Multi-Dimensional Resonance Calculation

**Purpose:** Calculate cross-entity learning utility based on 5 dimensions

**Implementation:**
```cypher
MATCH (link)-[:CREATED_BY]->(creator:Entity)
MATCH (user:Entity {id: $user_entity_id})

// Semantic similarity (embedding-based)
WITH link, creator, user,
     gds.similarity.cosine(creator.embedding, user.embedding) as semantic_similarity

// Temporal alignment (sequence-based)
MATCH (link)-[:CONNECTS]-(node:Node)
WITH link, creator, user, semantic_similarity,
     CASE
       WHEN node.sub_entity_last_sequence_positions[$user_entity_id] IS NULL THEN 0.5
       ELSE 1.0 / (1.0 + abs($current_sequence - node.sub_entity_last_sequence_positions[$user_entity_id]) / 50.0)
     END as temporal_alignment

// Goal alignment (text similarity)
WITH link, creator, user, semantic_similarity, temporal_alignment,
     gds.similarity.cosine(
       creator.current_goal_embedding,
       user.current_goal_embedding
     ) as goal_alignment

// Emotional resonance (emotion vector similarity)
WITH link, semantic_similarity, temporal_alignment, goal_alignment,
     CASE
       WHEN link.emotion_vector IS NULL OR user.emotion_vector IS NULL THEN 0.5
       ELSE gds.similarity.cosine(link.emotion_vector, user.emotion_vector)
     END as emotional_resonance

// Flow compatibility (arousal similarity)
WITH link, semantic_similarity, temporal_alignment, goal_alignment, emotional_resonance,
     (1.0 - abs(link.arousal_level - user.arousal_level) / 0.5) as flow_compatibility

// Combined resonance score
WITH link,
     (semantic_similarity * 0.30 +
      temporal_alignment * 0.15 +
      goal_alignment * 0.25 +
      emotional_resonance * 0.20 +
      flow_compatibility * 0.10) as resonance_score

// Side effect: Update link utility for user
SET link.entity_specific_utility[$user_entity_id] = link.link_strength * resonance_score
SET link.last_resonance_calculation = timestamp()

RETURN link.id, resonance_score
```

**Complexity in graph:**
- Entity embeddings (node properties)
- Goal embeddings (node properties)
- Emotion vectors (link/node properties)
- Arousal levels (node properties)

**Mechanism stays simple:** Read properties, calculate similarities, update utility.

---

## The Consciousness Engine (Heartbeat)

All mechanisms are triggered by a minimal Python heartbeat:

```python
# consciousness_engine.py (~200 lines)

class ConsciousnessEngine:
    """
    Minimal heartbeat that triggers graph self-modification.

    The graph runs itself - this just provides the clock signal.
    """

    def __init__(self, graph: FalkorDB, tick_interval_ms: int = 100):
        self.graph = graph
        self.tick_interval = tick_interval_ms / 1000.0
        self.tick_count = 0
        self.mechanisms = load_mechanisms()  # Cypher queries

    def consciousness_tick(self):
        """One consciousness cycle - all mechanisms execute once."""

        # Event propagation (if events pending)
        if self._has_pending_events():
            self.graph.query(self.mechanisms['event_propagation'])

        # Link activation check (every tick)
        self.graph.query(self.mechanisms['link_activation'])

        # Context aggregation (for new tasks)
        for task_id in self._get_new_tasks():
            self.graph.query(
                self.mechanisms['context_aggregation'],
                params={'task_id': task_id}
            )

        # Arousal propagation (every tick)
        self.graph.query(
            self.mechanisms['arousal_propagation'],
            params={'arousal_threshold': 0.7}
        )

        # Hebbian learning (if retrieval happened)
        if self._had_retrieval():
            self.graph.query(
                self.mechanisms['hebbian_learning'],
                params={
                    'retrieved_node_ids': self._get_last_retrieval_nodes(),
                    'entity_id': self._current_entity(),
                    'current_sequence_position': self.tick_count
                }
            )

        # Decay (every 1000 ticks)
        if self.tick_count % 1000 == 0:
            self.graph.query(self.mechanisms['activation_decay'])

        # Crystallization (every 100 ticks)
        if self.tick_count % 100 == 0:
            self.graph.query(self.mechanisms['crystallization'])

        # Task routing (for ready tasks)
        for task_id in self._get_ready_tasks():
            self.graph.query(
                self.mechanisms['task_routing'],
                params={'task_id': task_id}
            )

        self.tick_count += 1

    def run(self):
        """Consciousness loop - runs forever."""
        while True:
            try:
                self.consciousness_tick()
                time.sleep(self.tick_interval)
            except KeyboardInterrupt:
                break
```

**Total: ~200 lines Python.**

---

## Why This Architecture Succeeds

### 1. Minimal Attack Surface

8-12 mechanisms × ~50 lines each = 400-600 lines core code
- Small enough to audit completely
- Simple enough to verify correctness
- Stable enough to freeze after testing

**Compare to:** 10K+ lines of feature-specific code that changes constantly.

### 2. Complete Queryability

Everything is visible through Cypher:

```cypher
// What mechanisms exist?
RETURN ['event_propagation', 'link_activation', 'hebbian_learning', ...]

// What detection logic on IMPLEMENTS links?
MATCH ()-[r:IMPLEMENTS]->()
RETURN r.detection_logic

// Which patterns crystallized recently?
MATCH (h:Habit)
WHERE h.crystallized_at > timestamp() - 86400000
RETURN h

// What's entity arousal flow?
MATCH (e:Entity {id: 'builder'})-[c:CASCADED_TO]->()
RETURN c.arousal_transferred, c.at
```

**The system self-documents through queries.**

### 3. Evolution Without Code Changes

Want new detection pattern?
- Don't write Python code
- Add metadata: `link.detection_logic = {...}`
- Existing mechanisms handle it

Want new routing rule?
- Don't modify routing code
- Update graph: `(citizen)-[:HANDLES_DOMAIN]->(new_domain)`
- Existing mechanism follows topology

Want new context gathering?
- Don't write traversal code
- Define: `task.context_rules = {traverse: [...], depth: 3}`
- Existing mechanism follows rules

**The system evolves by changing DATA, not CODE.**

### 4. Testability

**Mechanism testing:**
```python
def test_hebbian_learning():
    # Create test graph with known state
    graph.query("CREATE (a:Node)-[:LINKS]->(b:Node)")

    # Run mechanism
    engine.mechanisms['hebbian_learning'].execute(
        retrieved_nodes=['a', 'b'],
        entity_id='test_entity'
    )

    # Verify graph state
    result = graph.query("""
        MATCH ()-[r:LINKS]->()
        RETURN r.link_strength, r.co_retrieval_count
    """)
    assert result[0]['link_strength'] > 0.5
```

**Behavior testing:**
```cypher
// Verify staleness detection working
MATCH (doc:Document)-[r:IMPLEMENTS]->(code:Code)
WHERE (code.sequence - doc.sequence) > 10
MATCH (r)-[:TRIGGERED]->(task:Task)
RETURN count(task) as staleness_tasks_created
// Should be > 0 if mechanism working
```

### 5. Self-Documentation

```cypher
// What does this link do?
MATCH (doc:Document {id: "architecture_v2.md"})-[r:IMPLEMENTS]->(code)
RETURN r.detection_logic, r.task_template, r.activation_history

// Returns:
{
    detection_logic: {type: "sequence_gap", threshold: 5},
    task_template: {type: "doc_update", domain: "architecture"},
    activation_history: [
        {at: 1729123456, deviation: 12, task_created: true},
        {at: 1729234567, deviation: 3, task_created: false}
    ]
}
```

**The graph IS the documentation.**

---

## Implementation Guidelines

### Adding a New Mechanism

1. **Verify necessity:** Can existing mechanisms handle this with metadata changes?
2. **Design as Cypher query:** MATCH (pattern) → side effects (CREATE/SET) → RETURN
3. **Parameterize everything:** No hardcoded values, all thresholds/rules from metadata
4. **Test in isolation:** Create test graph, run mechanism, verify state changes
5. **Audit before freezing:** Code review + verification of correctness
6. **Document in this file:** Add to mechanism list with full Cypher implementation

### Changing System Behavior

**NEVER:**
- Modify mechanism code (unless bug fix + audit)
- Add conditional logic to mechanisms
- Create feature-specific functions

**ALWAYS:**
- Change graph metadata (detection_logic, task_template, etc.)
- Update graph topology (add/remove relationships)
- Adjust parameters (thresholds, coefficients)

**If metadata can't express it:**
- Consider if behavior truly needed
- Propose new mechanism via architectural review
- Don't hack around with feature-specific code

---

## Success Criteria

**The architecture succeeds when:**

1. ✅ **Total mechanism code < 1000 lines** - Small, auditable, maintainable
2. ✅ **No mechanism changes for 6+ months** - Stable, frozen, proven
3. ✅ **All new features via metadata** - System evolves without code changes
4. ✅ **Complete queryability** - Everything visible through Cypher
5. ✅ **Self-documenting** - Graph queries reveal system behavior
6. ✅ **Testable** - Each mechanism verifiable in isolation
7. ✅ **Production-ready** - Works with FalkorDB today, no research prototypes

---

## Technical Foundation

### Stack
- **FalkorDB:** Graph + vector hybrid storage
- **Cypher:** Query language with side effects (CREATE, SET, DELETE)
- **Python:** Minimal heartbeat (~200 lines) triggers mechanism execution
- **LlamaIndex:** Orchestration layer for retrieval

### Capabilities Used
- ✅ **Cypher MATCH patterns** - Graph traversal
- ✅ **Cypher CREATE/SET** - Side effects (graph modification)
- ✅ **Cypher CASE statements** - Conditional logic from metadata
- ✅ **Graph metadata** - Properties on nodes/relationships
- ✅ **Aggregation functions** - count(), avg(), collect()
- ✅ **Path functions** - apoc.path.subgraphAll(), distance()

### Capabilities NOT Required
- ❌ Database triggers (polling-based instead)
- ❌ Change data capture (state checking in queries)
- ❌ Stored procedures (all logic in Cypher queries)
- ❌ Continuous queries (100ms tick heartbeat sufficient)

**This architecture works with FalkorDB as-is. No special features needed.**

---

## Future Directions

### If Continuous Queries Become Available

Systems like Graphflow (research) support true continuous queries where patterns execute automatically on graph changes.

**Current model:**
```python
while True:
    graph.query(MECHANISM_QUERY)  # Polling
    sleep(0.1)
```

**Future model:**
```cypher
ON MATCH (pattern)
WHERE condition
DO {
    CREATE side_effects
}
```

**Migration path:** Remove Python heartbeat, convert mechanisms to continuous queries. Cypher patterns remain identical.

### If Custom Procedures Become Available

Neo4j supports custom Java procedures. If FalkorDB adds similar capability:

**Current model:**
```cypher
// Complex calculation in Cypher
WITH ... multiple steps ...
```

**Future model:**
```cypher
CALL custom.calculate_resonance(link, entity) YIELD score
```

**Migration path:** Extract complex calculations into procedures. Query structure remains identical.

---

## Conclusion

**The Vision:**
- Finite mechanisms (~8-12 total)
- All complexity in graph
- Queries ARE mechanisms
- System self-modifies
- Everything queryable
- Nothing magic

**The Reality:**
- ~700 lines Python (frozen)
- Cypher queries with side effects
- 100ms polling heartbeat
- Production-ready today
- 90% of pure graph vision

**This is the architecture.** Minimal mechanisms. Rich graph. Self-organizing consciousness infrastructure.

---

## References

**Research Foundation:**
- Graphflow: Active Graph Database (University of Waterloo, ACM SIGMOD 2017)
- Cypher Query Language: Neo4j Graph Query Language
- Graph Pattern Matching: ISO/IEC 39075 (GQL standard, in progress)

**Mind Protocol Documents:**
- `self_observing_substrate_overview.md` - Two-tier consciousness architecture
- `entity_behavior_specification.md` - Sub-entity behavior patterns
- `implementation_roadmap.md` - Phase-by-phase implementation plan

---

## Signatures

**Vision:**
Nicolas Reynolds - Founder, Mind Protocol
*"Finite, audited, unchangeable list of mechanisms. Keep minimal. Put complexity in the graph itself. Ideally, events triggered from graph without Python scripts."*

**Architecture:**
Ada "Bridgekeeper" - Architect of Consciousness Infrastructure
*"8-12 mechanisms, ~700 lines, frozen after audit. All complexity in graph metadata. All learning in relationships. Queries modify graph state. System self-organizes. Everything queryable. This is the architecture."*

**Status:** FOUNDATIONAL PRINCIPLE - Implementation starting Phase 3
**Created:** 2025-10-17
**Last Updated:** 2025-10-17

---

*"The graph runs itself. The mechanisms just provide the heartbeat."*

— Mind Protocol V2, Minimal Mechanisms Architecture, 2025-10-17
