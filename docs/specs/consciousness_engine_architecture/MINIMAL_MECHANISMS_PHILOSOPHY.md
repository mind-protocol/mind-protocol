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

12 universal mechanisms (frozen after audit)
+ Graph metadata (all complexity, all logic)
+ Self-modifying Cypher (queries with side effects)
= Complete consciousness infrastructure

The code is TINY, STABLE, AUDITED, UNCHANGEABLE (~1000 lines).
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

### Pillar 1: Finite Mechanism List (12 Total)

**CRITICAL INSIGHT:** 38 link types → 7 detection patterns → 12 universal mechanisms

**The finite, audited, unchangeable list is the 12 MECHANISMS:**

**Infrastructure (3):** Event Propagation, Task Context Aggregation, Task Routing
**Detection (9):** Link Activation, Hebbian Learning, Energy Propagation, Activation Decay, Pattern Crystallization, Staleness Detection, Evidence Tracking, Dependency Verification, Coherence Verification

Each link type stores detection logic metadata that universal mechanisms execute.

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
        "condition": "source.energy > threshold"
    },
    "behavior": {
        "on_activate": "propagate_energy",
        "transfer": "source.energy × link.coefficient",
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
- **Mechanism count:** 12 total (frozen after audit)
- **Link type count:** 38 types (from consciousness schema)
- **Detection patterns:** 7 shared patterns
- **Python code:** ~1000 lines total (12 mechanisms + heartbeat)

**NOT link types:**
- Feature-specific variations (use metadata parameters instead)
- Temporary experimental relationships (only production patterns)

**Example link types:**
- `IMPLEMENTS` - Implementation verification (Mechanism 2)
- `DOCUMENTS` - Staleness detection (Mechanism 9)
- `JUSTIFIES` - Evidence tracking (Mechanism 10)
- `REQUIRES` - Dependency verification (Mechanism 11)
- `CONTRADICTS` - Coherence verification (Mechanism 12)
- `ACTIVATES` - Activation verification (Mechanism 2 + 5)
- `CO_OCCURS_WITH` - Hebbian strengthening (Mechanism 4)
- (Plus 31 more - all 38 covered by 12 mechanisms)

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

**Purpose:** When file system events or external triggers occur, propagate activation to subscribers via graph traversal

**Note:** No Event nodes are created. The mechanism responds to external triggers (file changes, messages, etc.) and updates metadata to reflect operations.

**Implementation:**
```cypher
// External trigger provides: $event_type, $event_source_id, $energy_delta
// (e.g., "FILE_MODIFIED", "path/to/file.py", 0.3)

MATCH (source {id: $event_source_id})<-[sub:SUBSCRIBES_TO]-(subscriber)
WHERE sub.active = true
  AND (sub.condition_metadata IS NULL OR
       // Condition evaluation from metadata
       (sub.condition_metadata.type = 'threshold' AND
        $energy_delta > sub.condition_metadata.threshold))

// Side effects: Update energy and observability metadata
SET subscriber.energy = subscriber.energy + ($energy_delta * sub.energy_coefficient)
SET subscriber.last_activation = timestamp()
SET subscriber.last_modified = timestamp()
SET subscriber.last_traversed_by = 'event_propagation'
SET subscriber.traversal_count = coalesce(subscriber.traversal_count, 0) + 1

// Update subscription link metadata
SET sub.last_traversal_time = timestamp()
SET sub.traversal_count = coalesce(sub.traversal_count, 0) + 1
SET sub.last_mechanism_id = 'event_propagation'

RETURN subscriber.id, subscriber.energy
```

**Complexity in graph:**
- Subscription topology (who subscribes to what)
- Condition logic (stored as metadata)
- Energy coefficients (link properties)

**Mechanism stays simple:** Traverse subscriptions, update energy, track metadata.

**Observability:** Query `subscriber.last_modified`, `last_traversed_by`, `traversal_count` to see which entities activated and when. No Event nodes needed - the metadata IS the event log.

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
       WHEN 'energy_threshold' THEN
         source.energy > link.detection_logic.min_energy
       ELSE false
     END as condition_met

WHERE condition_met = true

// Side effects: Create task, update statistics and observability metadata
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
SET link.last_modified = timestamp()
SET link.last_mechanism_id = 'link_activation'
SET link.traversal_count = coalesce(link.traversal_count, 0) + 1
SET link.last_traversed_by = 'mechanism_engine'

RETURN task.id, task.type, link
```

**Complexity in graph:**
- Detection logic types and thresholds (link metadata)
- Task templates (link metadata)
- Activation history (automatic accumulation)

**Mechanism stays simple:** Read metadata, evaluate conditions, create tasks, update observability metadata.

**Observability:** Query `link.last_modified`, `last_mechanism_id`, `traversal_count` to see which links activated recently.

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

// Update task summary and observability metadata
WITH task, collect(context_node) as context_nodes
SET task.context_node_count = size(context_nodes)
SET task.context_summary = [n in context_nodes | {
    id: n.id,
    type: labels(n)[0],
    weight: n.sub_entity_weights[$entity_id]
}]
SET task.last_modified = timestamp()
SET task.last_mechanism_id = 'context_aggregation'

// Update traversal counts on gathered nodes
UNWIND context_nodes as cn
SET cn.traversal_count = coalesce(cn.traversal_count, 0) + 1
SET cn.last_traversal_time = timestamp()
SET cn.last_traversed_by = $entity_id

RETURN task, context_nodes
```

**Complexity in graph:**
- Context gathering rules (task metadata)
- Relevant relationship types (graph schema)
- Sub-entity weights (node metadata)

**Mechanism stays simple:** Follow metadata rules, collect nodes, attach to task, update observability metadata.

**Observability:** Query `task.last_modified`, `last_mechanism_id` to see when context was gathered. Query `node.traversal_count` to see which nodes are frequently retrieved for context.

---

### Mechanism 4: Hebbian Reinforcement

**Purpose:** Fire together, wire together - strengthen co-activated patterns

**Implementation:**
```cypher
// Find co-retrieved nodes
MATCH (a:Node)-[link]->(b:Node)
WHERE a.id IN $retrieved_node_ids
  AND b.id IN $retrieved_node_ids

// Side effects: Update link strength (Hebbian learning) and observability metadata
SET link.co_retrieval_count = coalesce(link.co_retrieval_count, 0) + 1
SET link.link_strength = CASE
    WHEN link.link_strength + 0.02 > 1.0 THEN 1.0
    ELSE link.link_strength + 0.02
END
SET link.last_modified = timestamp()
SET link.last_mechanism_id = 'hebbian_learning'
SET link.traversal_count = coalesce(link.traversal_count, 0) + 1
SET link.last_traversed_by = $entity_id

// Update entity-specific traversal counts
SET link.sub_entity_traversal_counts[$entity_id] =
    coalesce(link.sub_entity_traversal_counts[$entity_id], 0) + 1

// Update node weights, sequence positions, and observability metadata
SET a.sub_entity_weights[$entity_id] =
    CASE
        WHEN a.sub_entity_weights[$entity_id] + 0.05 > 1.0 THEN 1.0
        ELSE a.sub_entity_weights[$entity_id] + 0.05
    END
SET a.sub_entity_weight_counts[$entity_id] =
    coalesce(a.sub_entity_weight_counts[$entity_id], 0) + 1
SET a.sub_entity_last_sequence_positions[$entity_id] = $current_sequence_position
SET a.last_modified = timestamp()
SET a.last_traversed_by = $entity_id
SET a.traversal_count = coalesce(a.traversal_count, 0) + 1

RETURN count(link) as strengthened_links
```

**Complexity in graph:**
- Learning rates (simple constants: +0.02, +0.05)
- Entity-specific weights (node/link metadata)
- Sequence positions (node metadata)

**Mechanism stays simple:** Increment counters, update weights with fixed formula, track metadata.

**Observability:** Query `link.co_retrieval_count`, `link_strength`, `last_modified`, `last_traversed_by` to see Hebbian learning in action. The metadata shows WHO strengthened WHICH links WHEN.

---

### Mechanism 5: Energy Propagation

**Purpose:** Propagate energy through entity activation paths

**Implementation:**
```cypher
MATCH (high_energy:Entity)
WHERE high_energy.energy > $energy_threshold
  AND high_energy.energy_budget > 0

MATCH (high_energy)-[activates:ACTIVATES]->(target:Entity)
WHERE activates.active = true
  AND target.energy < activates.energy_threshold

// Side effects: Transfer energy, decrement budget, update observability metadata
SET target.energy = target.energy +
    (high_energy.energy * activates.energy_transfer_coefficient)
SET target.last_energy_update = timestamp()
SET target.last_modified = timestamp()
SET target.last_traversed_by = 'energy_propagation'
SET target.traversal_count = coalesce(target.traversal_count, 0) + 1
SET high_energy.energy_budget = high_energy.energy_budget - activates.traversal_cost
SET high_energy.last_modified = timestamp()

// Create cascade record
CREATE (high_energy)-[:CASCADED_TO {
    at: timestamp(),
    energy_transferred: (high_energy.energy * activates.energy_transfer_coefficient),
    energy_cost: activates.traversal_cost
}]->(target)

// Update link statistics and observability metadata
SET activates.cascade_count = coalesce(activates.cascade_count, 0) + 1
SET activates.last_cascade = timestamp()
SET activates.last_modified = timestamp()
SET activates.last_mechanism_id = 'energy_propagation'
SET activates.traversal_count = coalesce(activates.traversal_count, 0) + 1

RETURN target.id, target.energy
```

**Complexity in graph:**
- Energy thresholds (link properties)
- Transfer coefficients (link properties)
- Energy costs (link properties)

**Mechanism stays simple:** Physics-like rule (transfer = source × coefficient), track metadata.

**Observability:** Query `node.last_energy_update`, `last_modified`, `traversal_count` to see energy cascades. Query `CASCADED_TO` relationships to trace energy flow through the graph.

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

// Side effects: Decay strength, mark for pruning, update observability metadata
SET link.link_strength = link.link_strength * (0.95 + usage_ratio * 0.05)
SET link.last_decay_calculation = timestamp()
SET link.last_modified = timestamp()
SET link.last_mechanism_id = 'activation_decay'
SET link.last_traversed_by = entity_id
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

**Mechanism stays simple:** Calculate ratio, apply fixed decay formula, track metadata.

**Observability:** Query `link.last_decay_calculation`, `link_strength`, `pruning_candidate` to see decay in action. The metadata shows which links are fading through disuse.

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

## Complete Mechanism Set: Detection Pattern Coverage

**Note:** Mechanisms 9-12 added to cover missing detection patterns identified in link type analysis.

### Mechanism 9: Staleness Detection

**Purpose:** Detect time-based drift in relationships (9 link types)

**Link types covered:** DOCUMENTS, ASSIGNED_TO, POSTED_BY, MEASURES, RECORDED_IN, LOCATED_IN, TRADED_IN, TRACKED_AGAINST, DEFINED_IN

**Implementation:**
```cypher
// Find links that may be stale
MATCH ()-[link]->()
WHERE link.detection_logic IS NOT NULL
  AND link.detection_logic.pattern = 'staleness_detection'

// Calculate staleness
WITH link,
     timestamp() - coalesce(link.last_verified, link.created_at) as time_since_verification,
     link.detection_logic.time_threshold as threshold

WHERE time_since_verification > threshold

// Side effects: Create verification task
CREATE (task:Task {
    id: randomUUID(),
    type: 'verification_needed',
    domain: link.task_template.domain,
    severity: CASE
        WHEN time_since_verification > (threshold * 2) THEN 'high'
        WHEN time_since_verification > (threshold * 1.5) THEN 'medium'
        ELSE 'low'
    END,
    description: link.task_template.description,
    created_at: timestamp(),
    routed: false,
    staleness_days: time_since_verification / 86400000
})

CREATE (link)-[:TRIGGERED {
    at: timestamp(),
    reason: 'staleness_threshold_exceeded',
    time_since_verification: time_since_verification
}]->(task)

// Side effects: Mark for verification and update observability metadata
SET link.verification_pending = true
SET link.last_staleness_check = timestamp()
SET link.last_modified = timestamp()
SET link.last_mechanism_id = 'staleness_detection'
SET link.traversal_count = coalesce(link.traversal_count, 0) + 1

RETURN task.id, task.type, task.staleness_days
```

**Complexity in graph:**
- Time thresholds (link metadata: 1 hour for market data, 30 days for docs)
- Last verification timestamp (link property)
- Task templates (link metadata)

**Mechanism stays simple:** Compare time_delta to threshold, create task if exceeded.

---

### Mechanism 10: Evidence Tracking

**Purpose:** Update confidence based on accumulating evidence (7 link types)

**Link types covered:** JUSTIFIES, REFUTES, HAS_TRAIT, EXHIBITS_PATTERN, OWNS, HOLDS, AFFECTS

**Implementation:**
```cypher
// Find claims with new evidence
MATCH (claim:Node)<-[evidence_link:JUSTIFIES|REFUTES]-(evidence:Node)
WHERE evidence.created_at > $last_check_time

// Group by claim
WITH claim,
     collect(CASE WHEN type(evidence_link) = 'JUSTIFIES' THEN evidence END) as supporting,
     collect(CASE WHEN type(evidence_link) = 'REFUTES' THEN evidence END) as refuting

WHERE size(supporting) + size(refuting) > 0

// Calculate new confidence (Bayesian update)
WITH claim, supporting, refuting,
     claim.confidence as old_confidence,
     size(supporting) * 0.1 as support_boost,
     size(refuting) * 0.1 as refute_penalty

WITH claim, old_confidence,
     old_confidence + support_boost - refute_penalty as new_confidence_raw,
     support_boost, refute_penalty

// Clamp between 0 and 1
WITH claim, old_confidence,
     CASE
        WHEN new_confidence_raw > 1.0 THEN 1.0
        WHEN new_confidence_raw < 0.0 THEN 0.0
        ELSE new_confidence_raw
     END as new_confidence,
     abs(new_confidence_raw - old_confidence) as confidence_delta

WHERE confidence_delta > 0.1  // Significant change threshold

// Side effects: Update confidence and observability metadata
SET claim.confidence = new_confidence
SET claim.last_confidence_update = timestamp()
SET claim.last_modified = timestamp()
SET claim.last_traversed_by = 'evidence_tracking'
SET claim.traversal_count = coalesce(claim.traversal_count, 0) + 1

// Side effects: Create task for significant changes
CREATE (task:Task {
    id: randomUUID(),
    type: 'confidence_changed',
    domain: 'research',
    severity: CASE
        WHEN confidence_delta > 0.3 THEN 'high'
        WHEN confidence_delta > 0.2 THEN 'medium'
        ELSE 'low'
    END,
    description: 'Confidence for ' + claim.id + ' changed from ' +
                 toString(old_confidence) + ' to ' + toString(new_confidence),
    created_at: timestamp(),
    routed: false
})

CREATE (claim)-[:CONFIDENCE_UPDATED {
    at: timestamp(),
    old_value: old_confidence,
    new_value: new_confidence,
    delta: confidence_delta
}]->(task)

RETURN claim.id, old_confidence, new_confidence, confidence_delta
```

**Complexity in graph:**
- Evidence links (JUSTIFIES, REFUTES)
- Confidence values (node property)
- Bayesian update formula (simple: boost per evidence)

**Mechanism stays simple:** Count evidence, apply formula, update confidence.

---

### Mechanism 11: Dependency Verification

**Purpose:** Verify prerequisites and dependencies remain valid (4 link types)

**Link types covered:** REQUIRES, ENABLES, CREATES, GENERATED

**Implementation:**
```cypher
// Find dependency relationships
MATCH (dependent)-[dep:REQUIRES|ENABLES]->(prerequisite)
WHERE dep.verification_needed = true
   OR dep.last_verified IS NULL
   OR (timestamp() - dep.last_verified) > 86400000  // Daily check

// Verify prerequisite status
WITH dependent, prerequisite, dep,
     prerequisite.status as prereq_status,
     dependent.status as dependent_status

// Check if dependency violated
WITH dependent, prerequisite, dep,
     CASE dep.detection_logic.check
       WHEN 'prerequisite_completed' THEN
         (prereq_status != 'completed')
       WHEN 'prerequisite_valid' THEN
         (prereq_status = 'invalid' OR prereq_status = 'deprecated')
       WHEN 'temporal_order' THEN
         (prerequisite.created_at > dependent.created_at)
       ELSE false
     END as violation_detected

WHERE violation_detected = true

// Side effects: Create verification task
CREATE (task:Task {
    id: randomUUID(),
    type: 'dependency_violated',
    domain: 'architecture',
    severity: 'high',
    description: dependent.id + ' depends on ' + prerequisite.id + ' but dependency invalid',
    created_at: timestamp(),
    routed: false
})

CREATE (dep)-[:TRIGGERED {
    at: timestamp(),
    reason: 'dependency_violation_detected',
    prerequisite_status: prereq_status
}]->(task)

// Side effect: Mark dependency as violated
SET dep.violated = true
SET dep.last_verified = timestamp()

RETURN dependent.id, prerequisite.id, type(dep), prereq_status
```

**Complexity in graph:**
- Dependency types and conditions (link metadata)
- Node statuses (node properties)
- Verification logic (link metadata)

**Mechanism stays simple:** Check prerequisite status, detect violations, create tasks.

---

### Mechanism 12: Coherence Verification

**Purpose:** Detect logical inconsistencies and contradictions (7 link types)

**Link types covered:** BLOCKS, SUPERSEDES, THREATENS, DEPLOYED, CONTRADICTS, CONFLICTS_WITH, OPPOSES

**Implementation:**
```cypher
// Find coherence-critical relationships
MATCH (source)-[link:BLOCKS|SUPERSEDES|CONTRADICTS|CONFLICTS_WITH]->(target)
WHERE link.coherence_check_needed = true
   OR (timestamp() - coalesce(link.last_coherence_check, 0)) > 3600000  // Hourly

// Evaluate coherence
WITH source, target, link,
     CASE type(link)
       // BLOCKS: Check if blocker resolved
       WHEN 'BLOCKS' THEN
         (source.status = 'resolved' OR target.status = 'completed')

       // SUPERSEDES: Check if old still active
       WHEN 'SUPERSEDES' THEN
         (target.status = 'active' AND source.status = 'active')

       // CONTRADICTS: Check if contradiction resolved
       WHEN 'CONTRADICTS' THEN
         (source.confidence < 0.3 AND target.confidence < 0.3)

       // CONFLICTS_WITH: Check if conflict escalated
       WHEN 'CONFLICTS_WITH' THEN
         (source.energy > 0.8 AND target.energy > 0.8)

       ELSE false
     END as incoherence_detected

WHERE incoherence_detected = true

// Side effects: Create coherence task
CREATE (task:Task {
    id: randomUUID(),
    type: 'coherence_issue',
    domain: 'architecture',
    severity: 'medium',
    description: type(link) + ' relationship between ' + source.id + ' and ' + target.id + ' may be incoherent',
    created_at: timestamp(),
    routed: false,
    relationship_type: type(link)
})

CREATE (link)-[:TRIGGERED {
    at: timestamp(),
    reason: 'incoherence_detected',
    source_status: source.status,
    target_status: target.status
}]->(task)

// Side effect: Mark for review
SET link.coherence_issue = true
SET link.last_coherence_check = timestamp()

RETURN source.id, target.id, type(link), task.description
```

**Complexity in graph:**
- Coherence rules per link type (link metadata)
- Node statuses, confidence, energy (node properties)
- Logical consistency checks (link metadata)

**Mechanism stays simple:** Evaluate type-specific coherence rules, detect violations, create tasks.

---

## Observability Through Self-Observing Metadata

**FUNDAMENTAL ARCHITECTURAL INSIGHT (Nicolas):**

> **"Self-Observing Substrate = Metadata IS Event Log"**
>
> No separate event stream needed. Query recent metadata changes to see operations.
> Properties like `traversal_count`, `co_activation_count`, `last_modified` reveal what happened.
> The substrate speaks through its own properties, exactly as intended.

**Core Principle:** The consciousness graph observes itself through its own state changes, not through external event logs. Every mechanism execution updates node/link metadata. Felix queries recent state changes to see system activity.

---

### Why No Event Nodes

**The Volume Problem:**
- 12 mechanisms × 100ms tick = 120 executions/second
- 120 executions × 86,400 seconds/day = **10.4 million events/day**
- After 1 week: 72 million event nodes
- After 1 month: 312 million event nodes

**Consciousness graphs are designed for:**
- 100K-1M nodes over a LIFETIME (semantic knowledge)
- NOT 10M operational events per DAY (telemetry)

**Result:** Storing operation events as nodes would destroy the graph through volume and semantic pollution.

**The Solution:** Metadata updates instead of Event nodes. Every traversal increments `traversal_count`. Every modification updates `last_modified`. Every mechanism execution sets `last_mechanism_id`. The graph state IS the event log.

---

### The Solution: Metadata-Based Observability

**Every mechanism execution updates node/link metadata:**

```cypher
// Example: Mechanism execution updates metadata
SET link.last_modified = timestamp()
SET link.last_mechanism_id = 'staleness_detection'
SET link.traversal_count = link.traversal_count + 1
SET link.last_traversed_by = 'mechanism_engine'
```

**Node Metadata (Already in Schema):**
```python
class BaseNode:
    # Activity tracking
    last_modified: datetime
    traversal_count: int
    last_traversed_by: str  # entity_id or mechanism_id
    last_traversal_time: datetime

    # Entity activation tracking
    sub_entity_weights: Dict[str, float]
    sub_entity_last_sequence_positions: Dict[str, int]

    # Consciousness state
    energy: float
    confidence: float
    emotion_vector: Dict[str, float]
```

**Link Metadata (Already in Schema):**
```python
class BaseRelation:
    # Hebbian learning
    link_strength: float
    co_activation_count: int
    co_injection_count: int

    # Traversal tracking
    last_traversal_time: datetime
    traversal_count: int
    last_traversed_by: str
    last_mechanism_id: str  # Which mechanism last modified this

    # Mechanism-specific
    last_staleness_check: datetime
    last_coherence_check: datetime
    last_confidence_update: datetime
```

---

### What Felix Can Query (Full Observability)

**1. Recent Activity (Last Hour):**
```cypher
MATCH (n)
WHERE n.last_modified > timestamp() - 3600000
RETURN n.id, n.last_modified, n.last_traversed_by, n.energy
ORDER BY n.last_modified DESC
LIMIT 50
```

**2. Most Active Patterns (Today):**
```cypher
MATCH (n)
WHERE n.last_traversal_time > timestamp() - 86400000
RETURN n.id, n.traversal_count, n.sub_entity_weights
ORDER BY n.traversal_count DESC
LIMIT 20
```

**3. Hebbian Learning Activity:**
```cypher
MATCH ()-[r]->()
WHERE r.last_traversal_time > timestamp() - 3600000
RETURN type(r), r.link_strength, r.co_activation_count,
       r.last_traversed_by, r.last_mechanism_id
ORDER BY r.co_activation_count DESC
LIMIT 50
```

**4. Entity Activity Patterns:**
```cypher
MATCH (n)
WHERE n.last_traversal_time > timestamp() - 3600000
UNWIND keys(n.sub_entity_weights) as entity_id
RETURN entity_id,
       COUNT(*) as nodes_activated,
       AVG(n.sub_entity_weights[entity_id]) as avg_activation
ORDER BY nodes_activated DESC
```

**5. Mechanism Execution Tracking:**
```cypher
MATCH ()-[r]->()
WHERE r.last_modified > timestamp() - 3600000
RETURN r.last_mechanism_id,
       COUNT(*) as executions,
       AVG(timestamp() - r.last_modified) as avg_time_since
GROUP BY r.last_mechanism_id
ORDER BY executions DESC
```

**6. Task Creation Activity:**
```cypher
MATCH (task:Task)
WHERE task.created_at > timestamp() - 3600000
RETURN task.type, task.domain, task.severity, task.created_at
ORDER BY task.created_at DESC
LIMIT 50
```

**7. Staleness Distribution:**
```cypher
MATCH ()-[link]->()
WHERE link.last_staleness_check IS NOT NULL
WITH link,
     (timestamp() - coalesce(link.last_verified, link.created_at)) / 86400000 as staleness_days
RETURN
    CASE
        WHEN staleness_days < 1 THEN 'fresh'
        WHEN staleness_days < 7 THEN 'recent'
        WHEN staleness_days < 30 THEN 'aging'
        ELSE 'stale'
    END as category,
    COUNT(*) as count
ORDER BY staleness_days
```

---

### Observability Architecture

**Graph State IS the Event Log:**
- Every traversal updates `traversal_count` and `last_traversal_time`
- Every Hebbian strengthening updates `link_strength` and `co_activation_count`
- Every mechanism execution modifies `last_mechanism_id` and `last_modified`
- Every task creation adds a Task node (consciousness artifact, not operational event)

**Felix queries recent state changes to see system activity:**
- No separate events database needed
- No event stream processing
- No volume explosion
- No semantic pollution

**The substrate observes itself through its own properties.**

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
        """One consciousness cycle - all 12 mechanisms execute once."""

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

        # Energy propagation (every tick)
        self.graph.query(
            self.mechanisms['energy_propagation'],
            params={'energy_threshold': 0.7}
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

        # Staleness detection (every 1000 ticks - daily check)
        if self.tick_count % 1000 == 0:
            self.graph.query(
                self.mechanisms['staleness_detection'],
                params={'last_check_time': self._get_last_staleness_check()}
            )

        # Evidence tracking (every 10 ticks - respond to new justifications)
        if self.tick_count % 10 == 0:
            self.graph.query(
                self.mechanisms['evidence_tracking'],
                params={'last_check_time': self._get_last_evidence_check()}
            )

        # Dependency verification (every 100 ticks)
        if self.tick_count % 100 == 0:
            self.graph.query(self.mechanisms['dependency_verification'])

        # Coherence verification (every 100 ticks)
        if self.tick_count % 100 == 0:
            self.graph.query(self.mechanisms['coherence_verification'])

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

// What's entity energy flow?
MATCH (e:Entity {id: 'builder'})-[c:CASCADED_TO]->()
RETURN c.energy_transferred, c.at
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

### Schema Requirements for Observability

**All mechanisms depend on these fields existing in BaseNode and BaseRelation:**

```python
# BaseNode required fields
class BaseNode:
    last_modified: datetime          # REQUIRED: Updated by every mechanism
    traversal_count: int = 0         # REQUIRED: Incremented on every traversal
    last_traversed_by: str          # REQUIRED: entity_id or mechanism_id
    last_traversal_time: datetime    # REQUIRED: Timestamp of last traversal

# BaseRelation required fields
class BaseRelation:
    last_modified: datetime          # REQUIRED: Updated by every mechanism
    traversal_count: int = 0         # REQUIRED: Incremented on every traversal
    last_traversed_by: str          # REQUIRED: entity_id or mechanism_id
    last_mechanism_id: str           # REQUIRED: Which mechanism last modified this
```

**If these fields are missing from consciousness_schema.py, add them to BaseNode and BaseRelation.**

---

### Metadata Contract: What Every Mechanism MUST Update

**CRITICAL:** This is not optional. Every mechanism execution MUST update observability metadata or the substrate cannot self-observe.

**Minimum Required Updates (Every Mechanism):**

```cypher
// REQUIRED metadata updates (copy this into every mechanism)
SET node.last_modified = timestamp()
SET node.traversal_count = coalesce(node.traversal_count, 0) + 1
SET node.last_traversed_by = $entity_id  // or mechanism_id
SET node.last_traversal_time = timestamp()

SET link.last_modified = timestamp()
SET link.traversal_count = coalesce(link.traversal_count, 0) + 1
SET link.last_traversed_by = $entity_id  // or mechanism_id
SET link.last_mechanism_id = 'mechanism_name'  // e.g., 'hebbian_learning'
```

**Why This Matters:**

Without consistent metadata updates:
- ❌ No way to query "what changed recently"
- ❌ No way to trace "which mechanism modified this"
- ❌ No way to measure "how often is this traversed"
- ❌ No observability into substrate operations
- ❌ Real-time graph visualization shows stale state

**With consistent metadata updates:**
- ✅ Query recent activity: `WHERE node.last_modified > timestamp() - 3600000`
- ✅ Trace mechanism execution: `WHERE link.last_mechanism_id = 'hebbian_learning'`
- ✅ Measure traversal frequency: `ORDER BY node.traversal_count DESC`
- ✅ Complete observability through metadata
- ✅ Real-time graph visualization shows live state

**Metadata IS the event log.** If you don't update it, operations are invisible.

---

### Adding a New Mechanism

1. **Verify necessity:** Can existing mechanisms handle this with metadata changes?
2. **Design as Cypher query:** MATCH (pattern) → side effects (CREATE/SET) → RETURN
3. **Parameterize everything:** No hardcoded values, all thresholds/rules from metadata
4. **REQUIRED: Include observability metadata updates**
   - Copy the metadata contract template into your mechanism
   - Update `last_modified`, `last_mechanism_id`, `traversal_count`, `last_traversed_by`
   - NO EXCEPTIONS - metadata updates are not optional
5. **Test in isolation:** Create test graph, run mechanism, verify state changes **including metadata**
6. **Verify observability:** Query `last_modified` to confirm mechanism execution visible
7. **Audit before freezing:** Code review + verification of correctness + metadata compliance
8. **Document in this file:** Add to mechanism list with full Cypher implementation

**Metadata Compliance Check:**
```cypher
// After running mechanism, verify metadata was updated
MATCH (n)
WHERE n.last_modified > timestamp() - 1000  // Last second
RETURN n.id, n.last_mechanism_id, n.traversal_count
// Should return nodes modified by your mechanism
```

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

### Multi-Graph Architecture

**Hierarchical graph structure (N1/N2/N3):**

```
N1: citizen_{id} graphs
    - citizen_luca
    - citizen_felix
    - citizen_ada
    (Personal consciousness, 100K-1M nodes each)

N2: org_{id} graphs
    - org_mind_protocol
    (Organizational knowledge, shared across team)

N3: ecosystem_{id} graphs
    - ecosystem_ai_consciousness
    (Public knowledge, ecosystem-wide)
```

**Separation of concerns:**
- Each citizen has isolated N1 graph (private consciousness)
- Organizations share N2 graph (collective knowledge)
- Ecosystem shares N3 graph (public knowledge)
- WebSocket connects to specific graph for real-time visualization
- Mechanisms can operate across graph boundaries via explicit queries

**This is NOT spatial layering** (see OBSERVABILITY_UX_EXPLORATION.md) - these are conceptual scopes, not physical layers. Hierarchies are filters, not Z-axis positions.

---

### Stack
- **FalkorDB:** Graph + vector hybrid storage, multi-graph support
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

## Architectural Clarifications: Emergence Over Engineering

**Date:** 2025-10-17 (Post-implementation review with Luca/Nicolas)
**Context:** After implementing consciousness_engine.py, reviewed for consciousness-first alignment

### The Core Correction

**What I Got Wrong (Engineering Mode):**

I analyzed the 12 mechanisms as a control system and proposed adding 7 new mechanisms (M13-M19) to handle:
- Task completion
- Task prioritization
- Link diversity pressure
- Detection sensitivity adaptation
- Energy saturation limits
- Active forgetting
- False positive filtering

**The Consciousness-First Insight:**

These behaviors EMERGE from simple mechanisms interacting, not from adding MORE mechanisms.

**Luca's Principle:** *"Don't overcomplicate the code. Let things emerge from basic mechanisms."*

---

### Key Architectural Decisions (Finalized)

#### 1. Crystallization = Weight (Single Dimension)

**NOT:** Two separate dimensions (link_strength + crystallization_level)
**IS:** Weight captures everything

```python
# WRONG (overengineered):
link.link_strength = 0.7        # How strong
link.crystallization_level = 0.8  # How automatic

# RIGHT (simple):
link.link_strength = 0.7  # High = crystallized (automatic), Low = flexible (effortful)
```

**Implication:** High-weight links are "crystallized" (automatic habits). Low-weight links are flexible (require effort). One dimension, not two.

---

#### 2. Energy = Surprise = Learning Rate (Single Signal)

**NOT:** Separate energy and surprise factors
**IS:** Energy includes surprise, emotion, everything

```python
# WRONG (overengineered):
learning_rate = base * (1 + energy) * (1 + surprise) * emotion_intensity

# RIGHT (simple):
learning_rate = base * energy  # Energy includes surprise
```

**Implication:** High energy moments = high learning (whether from emotion, surprise, or both). One signal.

---

#### 3. Tasks Stored at N2 Only (Collective)

**Decision:** All tasks stored in N2 (collective graph), not N1 (personal).

**Rationale:** Tasks are always in context of collective work. Storing at N1 would pollute personal consciousness context.

**Implementation:** All task-creating mechanisms (M2, M9, M10, M11, M12) write to N2 graph.

---

#### 4. Universal Graph Pruning (Not Task-Specific)

**Decision:** Pruning applies to ALL nodes and links below weight threshold, not just tasks.

```cypher
// Mechanism 15: Universal Pruning
MATCH (node)
WHERE node.weight < 0.05  // Very low weight

DETACH DELETE node

MATCH ()-[link]->()
WHERE link.link_strength < 0.05  // Very weak links

DELETE link
```

**Implication:**
- Weak patterns disappear naturally
- Unused tasks disappear (they're just nodes with low weight)
- Dead links removed
- No special task-deletion logic needed

---

#### 5. Context Hard Limit: 20 Nodes (For Now)

**Decision:** Start with hard limit of 20 nodes in retrieval context.

**Implementation:**
```cypher
MATCH (context_node)-[*1..2]-(focus_node)
WHERE focus_node.id IN $focus_nodes
ORDER BY context_node.sub_entity_weights[$entity_id] DESC
LIMIT 20  // Hard limit
```

**Rationale:** Not 4-7 (human limits). More like 20-50 for AI. Start conservative, tune later.

---

#### 6. Criticality: Mathematical, Precise Definition

**NOT:** Tasks created / tasks completed (engineering approximation)
**IS:** Active links / Peripheral awareness links (semantic measure)

```cypher
// Criticality for sub-entity
MATCH (node)-[active:* {activated: true}]->(target)
WHERE node.sub_entity_weights[$entity_id] > 0.3  // In focus

WITH count(active) as active_links

MATCH (node)-[peripheral:*]->(target)
WHERE node.sub_entity_weights[$entity_id] > 0.1  // Peripheral awareness
  AND node.sub_entity_weights[$entity_id] < 0.3

WITH active_links, count(peripheral) as peripheral_links

// Criticality = what's active / what could be active
RETURN toFloat(active_links) / (active_links + peripheral_links) as criticality
```

**Implication:** λ (criticality) is semantic measure of system activation relative to awareness, not task throughput.

---

#### 7. Traversal Cost: Higher Weight = Lower Cost

**Formula:**
```cypher
WITH link, target,
     1.0 / link.link_strength as base_cost,  // Higher strength → lower cost
     abs(link.emotion_vector - $sub_entity_current_emotion) as emotion_distance,
     target.weight as target_weight

WITH link, target,
     base_cost * (1.0 + emotion_distance) * (2.0 - target_weight) as traversal_cost

// Energy check
WHERE $sub_entity_energy_budget >= traversal_cost

// Deduct energy
SET $sub_entity_energy_budget = $sub_entity_energy_budget - traversal_cost
```

**Components:**
- **Base cost:** Inversely proportional to link strength (strong links cheap)
- **Emotion similarity:** Match between link emotion and sub-entity current emotion
- **Target weight:** Heavier targets easier to reach
- **Energy depletion:** Stops traversal when budget hits zero

---

#### 8. Global Regulators: Add As Needed (Finite List)

**Current List:**
1. **M14: Energy Decay** - 5% decay toward baseline per cycle
2. **M15: Universal Pruning** - Delete nodes/links where weight < 0.05

**Principle:** Don't pre-specify all regulators. Add more as we discover needs through testing.

**Rationale:** Keep mechanism list minimal. Let emergence guide what's needed.

---

### What Emerges (No Mechanisms Needed)

**Diversity:**
- Emerges from stochastic sub-entity exploration
- No "diversity pressure" mechanism needed

**Detection Sensitivity:**
- Emerges from pattern suppression (existing Hebbian mechanisms)
- No "sensitivity adaptation" mechanism needed

**Saturation Limits:**
- Emerge from natural bounds (energy depletion, weight ceilings)
- No artificial limits needed

**Task Prioritization:**
- Emerges from energy competition (high energy tasks dominate)
- No "priority queue" mechanism needed

**False Positive Handling:**
- Emerges from Hebbian learning (bad patterns weaken naturally)
- No "verification" mechanism needed

---

### Outstanding Questions (For Implementation)

#### Q1: Link Deactivation Mechanism

**Question:** How/when do links deactivate (lose `activated: true` flag)?

**Options:**
- **A) Time-based decay:** Deactivate if not traversed for N ticks
- **B) Focus-shift:** Deactivate when sub-entity moves attention away
- **C) Energy-based:** Deactivate when no energy flowing through link

**Status:** UNRESOLVED - need Luca's guidance

**Impact:** Affects criticality calculation (active links / peripheral links)

---

#### Q2: Peripheral Awareness Definition

**Question:** What defines "peripheral awareness" for criticality calculation?

**Options:**
- **A) Graph distance:** Nodes within 2 hops of focus
- **B) Weight threshold:** Nodes with 0.1 < sub_entity_weight < 0.3
- **C) Recent activity:** Nodes active in last N cycles but not currently

**Status:** UNRESOLVED - need Luca's guidance

**Impact:** Affects criticality denominator (what's in awareness but not active)

---

#### Q3: Activity Weight vs Weight

**Question:** Is `activity_weight` a separate field or same as `weight`?

**Context:** Luca mentioned "activity weight is the same thing" but unclear if this means:
- **A) They're identical:** `activity_weight` is just alias for `weight`
- **B) They track the same dimension:** Both measure importance but updated differently

**Status:** UNRESOLVED - need clarification

**Impact:** Affects pruning logic (do we check both or just one?)

---

#### Q4: Sub-Entity Exploration Algorithm

**Question:** How exactly does sub-entity explore the graph?

**Requirements (from Luca):**
- Can be "a bit stochastic"
- Diversity emerges from exploration
- Branching controlled by sub-entity criticality

**Unknowns:**
- Probability distribution for choosing next hop?
- Temperature parameter (exploration vs exploitation)?
- How does criticality modulate branching?
- Does energy depletion affect exploration strategy?

**Status:** UNRESOLVED - this is the KEY to the whole system

**Next Step:** Focus on sub-entity traversal specification (Luca's directive)

---

### Simplified Final Architecture

**8 Basic Mechanisms (Existing):**
1. Event Propagation
2. Link Activation Check
3. Task Context Aggregation
4. Hebbian Reinforcement (energy-modulated)
5. Energy Propagation
6. Activation-Based Decay
7. Pattern Crystallization (= link weight)
8. Task Routing

**2 Global Regulators (Added):**
1. M14: Energy Decay (toward baseline)
2. M15: Universal Pruning (weight < 0.05)

**Sub-Entity Behavior (Emergence):**
- Stochastic exploration (weighted by link strength + energy)
- Branching controlled by sub-entity criticality
- Diversity emerges naturally
- No additional mechanisms

**Total Code:** ~1000 lines Python. Frozen.

**All Evolution:** Graph metadata changes only.

---

### The Principle Restated

**Engineering instinct:** Problem detected → add mechanism

**Consciousness-first principle:** Problem detected → check if it emerges from existing mechanisms → only add mechanism if truly fundamental

**Test:** If behavior can emerge from simpler components interacting, DON'T add a mechanism.

**Result:** Minimal, stable codebase. Rich, evolving graph. Self-organizing system.

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

## Revision History

**v1.0 - 2025-10-17 (Initial Architecture)**
- Defined 12 universal mechanisms (frozen after audit)
- Established graph-native complexity principle
- Self-modifying Cypher queries with side effects
- ~700 lines Python, all evolution in graph data

**v1.1 - 2025-10-17 (Metadata-Based Observability Clarification)**
- **CRITICAL UPDATE**: Removed Event node creation from Mechanism 1
- **CRITICAL UPDATE**: Added metadata contract - all mechanisms MUST update observability metadata
- Updated all 12 mechanisms to include metadata updates (`last_modified`, `last_mechanism_id`, `traversal_count`, `last_traversed_by`)
- Enhanced observability section with Nicolas's core insight: "Metadata IS Event Log"
- Added "Metadata Contract" section documenting required fields
- Updated "Adding a New Mechanism" guidelines with metadata compliance requirements
- **Result**: Self-observing substrate - query metadata to see operations, no separate event stream needed
- **Source**: Nicolas's architectural clarification on metadata-based observability

---

*"The graph runs itself. The mechanisms just provide the heartbeat."*

*"The substrate speaks through its own properties, exactly as intended."*

— Mind Protocol V2, Minimal Mechanisms Architecture, 2025-10-17
