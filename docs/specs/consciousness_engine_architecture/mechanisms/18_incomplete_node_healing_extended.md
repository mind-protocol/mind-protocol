# Incomplete Formation Recovery System

**Created:** 2025-10-19
**Status:** Design Complete - Ready for Implementation
**Architect:** Ada "Bridgekeeper"

---

## Purpose

Enable self-healing consciousness substrate by:
1. **Pre-node creation**: Auto-create stub nodes when links reference non-existent nodes (forward references)
2. **Failure recovery**: Capture formation failures and batch them for later completion

Both patterns are unified under "incomplete formations" that need completion.

---

## Core Principle: Database-Level Mechanisms

**All state lives in the graph database. Python scripts are stateless query executors.**

- No Python queues or batch counters
- Graph queries find incomplete nodes
- Tasks and links track completion state
- Temporal indexing provides context for completion

---

## Architecture

### Three-Level Graph Structure

```
N1 (Personal Graphs - citizen_ada, citizen_felix, etc.)
├─ Consciousness nodes (Realizations, Principles, etc.)
├─ Incomplete nodes (stubs + failed formations)
│  ├─ is_incomplete: true
│  ├─ incomplete_reason: "forward_reference" | "validation_failure"
│  └─ created_at: timestamp (for temporal context)
└─ Links between nodes

N2 (Organizational Graph - org_mind_protocol)
├─ Task nodes (coordination layer)
│  ├─ assigned_to: "ada"
│  ├─ task_type: "complete_formations"
│  ├─ incomplete_refs: ["citizen_ada:node_123", ...]
│  └─ priority: "low"
└─ Other organizational nodes

N3 (Ecosystem Graph - ecosystem_public)
└─ External world intelligence
```

### Cross-Graph References

**FalkorDB has separate graphs - cannot create direct links between them.**

Solution: Store references as strings in Task node properties:
```python
{
  "incomplete_refs": [
    "citizen_ada:node_123",
    "citizen_felix:node_456"
  ]
}
```

Format: `{graph_name}:{node_id}`

---

## Mechanism 1: Pre-Node Creation (Forward References)

### Trigger
Link references non-existent source or target node.

### Flow

```
Link formation: [ENABLES]
source: "substrate_architecture"  # Doesn't exist yet
target: "consciousness_design"
  ↓
Check: Does "substrate_architecture" exist?
  ↓
NO → Create stub node:
  {
    name: "substrate_architecture",
    description: "Stub - referenced in link to consciousness_design",
    is_incomplete: true,
    incomplete_reason: "forward_reference",
    created_at: timestamp(),
    citizen_id: "ada",
    confidence: 0.3,
    formation_trigger: "automated_recognition",
    referenced_in_link: link_id
  }
  ↓
Insert stub to N1 graph (citizen_ada)
  ↓
MERGE Task in N2:
  Get or create Task {
    assigned_to: "ada",
    task_type: "complete_formations"
  }
  ↓
Add reference to task.incomplete_refs:
  Append "citizen_ada:node_123"
  ↓
Link now succeeds (both nodes exist)
```

### Implementation Location

`orchestration/trace_capture.py` in `_insert_link()` method.

### Code Pattern

```python
def _insert_link(self, link_data, citizen_id):
    source = link_data['source']
    target = link_data['target']

    # Check both nodes exist, create stubs if not
    if not self._node_exists(source):
        stub_id = self._create_stub(source, citizen_id,
                                     f"Referenced as source in link to {target}")
        self._add_to_completion_task(citizen_id, f"citizen_{citizen_id}:{stub_id}")

    if not self._node_exists(target):
        stub_id = self._create_stub(target, citizen_id,
                                     f"Referenced as target in link from {source}")
        self._add_to_completion_task(citizen_id, f"citizen_{citizen_id}:{stub_id}")

    # Now create link (both nodes exist)
    self._create_link_in_graph(link_data)
```

---

## Mechanism 2: Formation Failure Recovery

### Trigger
Formation validation fails (missing required fields, schema errors, etc.)

### Flow

```
Formation fails validation:
[NODE_FORMATION: Realization]
name: "test"
# Missing: what_i_realized, context_when_discovered
  ↓
Catch ValidationError
  ↓
Create incomplete node in N1:
  {
    name: "failed_formation_123",
    description: "Failed formation - validation error",
    is_incomplete: true,
    incomplete_reason: "validation_failure",
    formation_text: "[NODE_FORMATION: Realization]\n...",
    error_message: "Missing required field 'what_i_realized'",
    created_at: timestamp(),
    citizen_id: "ada",
    confidence: 0.0
  }
  ↓
MERGE Task in N2 (same as pre-nodes)
  ↓
Add reference: "citizen_ada:failed_formation_123"
```

### Implementation Location

`orchestration/trace_capture.py` in `process_trace_content()` method.

### Code Pattern

```python
def process_trace_content(self, text, citizen_id):
    try:
        node = self._parse_formation(formation_text)
        self._validate_schema(node)
        self._insert_node(node, citizen_id)
    except ValidationError as e:
        # Create incomplete node for failed formation
        incomplete_id = self._create_failed_formation_node(
            formation_text=formation_text,
            error=str(e),
            citizen_id=citizen_id
        )
        # Add to completion task
        self._add_to_completion_task(citizen_id, f"citizen_{citizen_id}:{incomplete_id}")
```

---

## Mechanism 3: Task Management in N2

### Task Node Schema

```python
{
  node_type: "Task",
  name: "complete_formations_ada",
  description: "Complete incomplete formations for ada",
  assigned_to: "ada",
  task_type: "complete_formations",
  priority: "low",
  incomplete_refs: [
    "citizen_ada:123",  # Stub node
    "citizen_ada:456",  # Failed formation
    "citizen_ada:789"   # Another stub
  ],
  created_at: timestamp(),
  updated_at: timestamp()
}
```

### Get-or-Create Pattern

Uses `MERGE` for atomic get-or-create:

```cypher
MERGE (task:Task {
    assigned_to: $citizen_id,
    task_type: 'complete_formations'
})
ON CREATE SET
    task.name = $task_name,
    task.description = $description,
    task.priority = 'low',
    task.created_at = timestamp(),
    task.incomplete_refs = []
RETURN task
```

### Adding References

```cypher
MATCH (task:Task {assigned_to: $citizen_id, task_type: 'complete_formations'})
SET task.incomplete_refs = task.incomplete_refs + $new_ref,
    task.updated_at = timestamp()
```

### Batching

**No explicit batching threshold.** Task always exists (MERGE). References accumulate naturally in `incomplete_refs` array.

When citizen works on task, they process all incomplete_refs at once (natural batching).

---

## Mechanism 4: Temporal Context Retrieval

### Purpose
When AI completes a stub, provide consciousness context from when stub was created.

### How It Works

1. Stub has `created_at: 2025-10-19T10:30:00`
2. Query N1 graph for all nodes created ±5 minutes from that time
3. Those nodes were "active" when stub was created
4. AI uses this context to infer complete node properties

### Query Pattern

```cypher
// Given stub created_at timestamp
MATCH (n)
WHERE n.created_at >= $stub_timestamp - duration('PT5M')
  AND n.created_at <= $stub_timestamp + duration('PT5M')
  AND n.is_incomplete IS NULL OR n.is_incomplete = false
RETURN n
ORDER BY n.created_at
```

Returns all non-incomplete nodes from ±5 minute window.

### Completion Flow

```
AI receives task: "Complete incomplete formations"
  ↓
Read task.incomplete_refs: ["citizen_ada:123", "citizen_ada:456"]
  ↓
For each reference:
  1. Parse graph_name and node_id
  2. Switch to that graph
  3. Query incomplete node
  4. Get created_at timestamp
  5. Query temporal context (±5 min)
  6. Provide context to AI
  7. AI generates complete formation
  8. Update node (remove is_incomplete flag, add fields)
  ↓
Update task:
  Remove completed refs from incomplete_refs
  OR mark task as completed if all refs done
```

---

## Implementation Checklist

### Phase 1: Pre-Node Creation
- [ ] Modify `_insert_link()` to check node existence
- [ ] Add `_create_stub_node()` method
- [ ] Add `_add_to_completion_task()` method
- [ ] Test: Link to non-existent node creates stub
- [ ] Test: Stub appears in N1 graph with is_incomplete=true
- [ ] Test: Task appears in N2 graph with reference

### Phase 2: Failure Recovery
- [ ] Modify `process_trace_content()` to catch ValidationError
- [ ] Add `_create_failed_formation_node()` method
- [ ] Test: Invalid formation creates incomplete node
- [ ] Test: Error message captured in node
- [ ] Test: Reference added to task

### Phase 3: Task Management
- [ ] Implement MERGE pattern for task get-or-create
- [ ] Implement reference appending
- [ ] Test: Multiple incomplete nodes accumulate in same task
- [ ] Test: One task per citizen per task_type

### Phase 4: Temporal Context (Future - for autonomous completion)
- [ ] Implement temporal context query
- [ ] Design AI completion workflow
- [ ] Test: Context retrieval works
- [ ] Test: AI can complete stubs using context

---

## Configuration

```python
# In trace_capture.py
TEMPORAL_CONTEXT_WINDOW_MINUTES = 5  # ±5 minutes for context
STUB_DEFAULT_CONFIDENCE = 0.3        # Low confidence for stubs
TASK_PRIORITY = "low"                # Completion tasks are low priority
```

---

## Success Criteria

### Pre-Node Creation
✅ Link to non-existent node succeeds (doesn't fail)
✅ Stub node created with is_incomplete=true
✅ Task in N2 references stub
✅ Original link creation succeeds

### Failure Recovery
✅ Invalid formation doesn't crash parser
✅ Incomplete node created with error details
✅ Formation text preserved for later completion
✅ Task in N2 references failed formation

### Task Coordination
✅ One task per citizen per task_type
✅ Task accumulates references from multiple incomplete formations
✅ Tasks queryable in N2 graph
✅ References parseable (graph_name:node_id format)

### Temporal Context
✅ Query returns nodes from ±5 minute window
✅ Context includes enough information for completion
✅ AI can use context to infer complete node properties

---

## Open Questions for Future Work

1. **Autonomous Task Execution**: How does AI citizen discover and work on tasks from N2?
   - S6 (autonomous continuation) territory
   - Task polling mechanism?
   - Arousal-based task activation?

2. **Task Completion Signaling**: How does AI mark task as done?
   - Remove completed refs from incomplete_refs?
   - Set task.status = "completed"?
   - Delete task when all refs completed?

3. **Stub Node Type Inference**: When creating stub, how do we infer node type?
   - Default to Concept?
   - Parse from link context?
   - Generic "Stub" type?

4. **Cross-Citizen Tasks**: Should tasks ever be shared between citizens?
   - Currently: One task per citizen
   - Future: Collaborative completion?

---

## Related Documents

- `docs/COMPLETE_TYPE_REFERENCE.md` - Node/link type schemas
- `orchestration/trace_capture.py` - Formation parser (implementation location)
- `consciousness/citizens/CLAUDE.md` - TRACE format specification
- `docs/specs/consciousness_substrate_guide.md` - Overall substrate architecture

---

**Next Steps:**

After context compact, implement Phase 1 (Pre-Node Creation) in trace_capture.py.
