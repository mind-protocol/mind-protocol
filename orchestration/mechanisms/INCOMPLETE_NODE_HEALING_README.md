# Incomplete Node Healing - Implementation Guide

**Spec:** `docs/specs/v2/learning_and_trace/incomplete_node_healing.md`
**Implementation:** `orchestration/mechanisms/incomplete_node_healing.py`
**Tests:** `orchestration/mechanisms/test_incomplete_node_healing.py`
**Author:** Felix (Engineer)
**Date:** 2025-10-22

---

## Overview

Prevents schema-incomplete nodes/links from contaminating traversal/WM while **allowing creation** (don't block thinking). Bottom-up approach: **detect → task → complete → admit**.

**Key principle:** Eligibility is a **READ-TIME FILTER**, not a second energy channel. Single-energy E_i remains the physics; eligibility gates **SELECTION**.

**Eligibility predicate:**
```
eligible(i) := is_complete(i) ∧ status∈{active} ∧ E_i ≥ Θ_i
```

---

## Core Functions

### 1. Completeness Validation

```python
from orchestration.mechanisms import incomplete_node_healing as heal

# Check if node has all required fields
complete = heal.is_node_complete(node)

# Get list of missing fields
missing = heal.get_missing_fields(node)
# Output: ["definition", "confidence"]

# Check link completeness
complete = heal.is_link_complete(link)
```

**Required fields defined per type:**
- CONCEPT: name, description, definition
- MEMORY: name, description, timestamp, participants
- MECHANISM: name, description, how_it_works, inputs, outputs
- ENABLES: source_id, target_id, subentity, enabling_type, degree_of_necessity
- (See REQUIRED_NODE_FIELDS / REQUIRED_LINK_FIELDS in code)

### 2. Eligibility Checking

```python
# Check if node/link is eligible for selection
if heal.is_eligible(node):
    candidates.append(node)  # Can be selected for traversal/WM
else:
    # Skip incomplete/ineligible node (visible but greyed)
    pass
```

**Eligibility requires ALL of:**
1. **Completeness:** All required fields present
2. **Status:** status = "active" (not deleted/archived)
3. **Activation:** E ≥ theta (for nodes only)

### 3. Task Creation

```python
# Detect incompleteness and create task
missing = heal.validate_and_mark_incomplete(node)

if missing:
    # Create completion task
    task = heal.create_completion_task(node, missing)

    # Task contains:
    # - task.target_id = node.id
    # - task.missing_fields = ["definition", ...]
    # - task.status = PENDING

    # Store task for processing
    task_registry.append(task)
```

### 4. Completion Strategies

```python
# Execute task with schema defaults
success = heal.complete_task(
    task,
    graph,
    strategy=heal.CompletionStrategy.SCHEMA_DEFAULT
)

# Or try context inference
success = heal.complete_task(
    task,
    graph,
    strategy=heal.CompletionStrategy.CONTEXT_INFERENCE
)

if success:
    # Node now complete and eligible
    assert heal.is_node_complete(node)
    assert heal.is_eligible(node)
```

**Available strategies:**
- `SCHEMA_DEFAULT`: Fill with sensible defaults
- `CONTEXT_INFERENCE`: Infer from neighboring nodes (basic implementation)
- `LLM_FILL`: Ask LLM to complete (future)
- `MANUAL`: Human intervention required

---

## Integration with Selectors

### Traversal Integration

```python
# In sub_entity_traversal.py or similar
def select_traversal_candidates(graph, source_node, goal):
    """Select candidates with eligibility filtering."""
    candidates = []

    for link in source_node.outgoing_links:
        target = link.target

        # NEW: Check eligibility (read-time filter)
        if not heal.is_eligible(target):
            continue  # Skip incomplete nodes

        # ... rest of candidate selection logic

    return candidates
```

### Working Memory Integration

```python
# In wm_pack.py or similar
def select_working_memory(graph, top_n=10):
    """Select WM nodes with eligibility filtering."""
    # Filter to eligible nodes only
    eligible_nodes = [
        node for node in graph.nodes.values()
        if heal.is_eligible(node)
    ]

    # Sort by energy and take top-N
    sorted_nodes = sorted(eligible_nodes, key=lambda n: n.E, reverse=True)
    return sorted_nodes[:top_n]
```

---

## Workflow Example

**Complete workflow: detect → task → complete → eligible**

```python
import incomplete_node_healing as heal

# 1. Create potentially incomplete node
node = Node(
    id="c1",
    name="Mind Protocol",
    node_type=NodeType.CONCEPT,
    description="The consciousness framework",
    E=2.0,  # Energized
    theta=1.0
)
node.properties['status'] = "active"
graph.add_node(node)

# 2. Validate on creation
missing = heal.validate_and_mark_incomplete(node)
# missing = ["definition"]

# Check eligibility
assert not heal.is_eligible(node)  # Ineligible due to incompleteness

# 3. Create completion task
task = heal.create_completion_task(node, missing)

# 4. Execute task (auto or manual)
success = heal.complete_task(task, graph, heal.CompletionStrategy.SCHEMA_DEFAULT)

# 5. Verify completion
assert heal.is_node_complete(node)  # Now complete
assert heal.is_eligible(node)  # Now eligible for selection
```

---

## Test Coverage

**24 comprehensive tests covering:**

### Completeness Validation (7 tests)
- Complete CONCEPT node passes
- Incomplete CONCEPT fails
- Complete MEMORY node passes
- Incomplete MEMORY fails
- Complete ENABLES link passes
- Incomplete ENABLES link fails
- Empty strings count as missing

### Eligibility Predicate (5 tests)
- Complete+active+energized node is eligible
- Incomplete node is ineligible
- Deleted node is ineligible
- Below-threshold node is ineligible
- Eligibility requires ALL conditions

### Task Management (3 tests)
- Create task for incomplete node
- Create task for incomplete link
- Task serialization to dict

### Completion Strategies (4 tests)
- Schema defaults for CONCEPT
- Schema defaults for MEMORY
- Execute task with schema defaults
- Task fails if target not found

### Validation on Creation (2 tests)
- Complete node validation returns None
- Incomplete node marked and missing returned

### Integration (1 test)
- End-to-end: detect → task → complete → eligible

### Registry (4 tests)
- CONCEPT requires 'definition'
- MEMORY requires 'timestamp' and 'participants'
- ENABLES requires specific fields
- Default fallback exists

**Run tests:**
```bash
python orchestration/mechanisms/test_incomplete_node_healing.py
```

---

## Configuration

### Required Fields Registry

Edit `incomplete_node_healing.py` to add/modify required fields:

```python
REQUIRED_NODE_FIELDS = {
    "Concept": ["name", "description", "definition"],
    "Memory": ["name", "description", "timestamp", "participants"],
    # ... add more types
}

REQUIRED_LINK_FIELDS = {
    "ENABLES": ["source_id", "target_id", "subentity", "enabling_type", "degree_of_necessity"],
    # ... add more types
}
```

### Completion Defaults

Customize default values in `complete_with_defaults()`:

```python
def complete_with_defaults(obj, missing_fields):
    defaults = {}

    for field_name in missing_fields:
        if field_name == "definition":
            defaults[field_name] = f"Auto-generated definition for {obj.name}"
        elif field_name == "confidence":
            defaults[field_name] = 0.5  # Medium confidence
        # ... add more defaults
```

---

## Observability (Future Integration)

### Events to Emit

```python
# When node/link created incomplete
await broadcaster.broadcast_event("node.incomplete", {
    "v": "2",
    "node_id": node.id,
    "node_type": str(node.node_type),
    "missing_fields": missing,
    "created_at": node.created_at.isoformat()
})

# When task created
await broadcaster.broadcast_event("task.create", {
    "v": "2",
    "task_id": task.id,
    "task_type": task.task_type,
    "target_id": task.target_id,
    "missing_fields": task.missing_fields
})

# When task completed
await broadcaster.broadcast_event("task.resolve", {
    "v": "2",
    "task_id": task.id,
    "strategy": task.completion_strategy.value,
    "confidence": task.confidence,
    "time_to_complete_ms": elapsed_ms
})

# When eligibility changes
await broadcaster.broadcast_event("eligibility.update", {
    "v": "2",
    "node_id": node.id,
    "was_eligible": was_eligible,
    "now_eligible": is_eligible(node)
})
```

### Metrics to Track

```python
metrics = heal.IncompletenessMetrics(
    incomplete_nodes_by_type={"Concept": 5, "Memory": 2},
    incomplete_links_by_type={"ENABLES": 3},
    tasks_pending=7,
    tasks_completed=15,
    tasks_failed=1,
    median_time_to_complete_ms=1850.0,
    completion_by_strategy={"schema_default": 12, "context_inference": 3},
    eligibility_hits=150,  # Eligible nodes selected
    eligibility_misses=7   # Ineligible nodes filtered
)
```

---

## Performance Considerations

### Validation Cost

**Completeness checking:** O(F) where F = number of required fields (typically 2-5)
- Very fast: just check field existence
- No expensive computation

**Eligibility checking:** O(1)
- Three simple checks: completeness + status + energy
- Negligible overhead

### Memory Overhead

**Per incomplete node:**
- `properties['is_incomplete']`: 1 boolean
- `properties['missing_fields']`: 1 list (typically 1-3 items)
- Total: ~50 bytes

**Task storage:**
- CompletionTask: ~200 bytes per task
- For 100 incomplete nodes: ~20KB total
- Negligible compared to graph size

### Integration Impact

**Traversal filtering:**
- Adds one `is_eligible()` check per candidate
- O(1) per check
- Negligible impact on traversal performance

**WM selection:**
- Adds filtering step before sorting
- O(N) where N = total nodes
- Minimal since N typically < 10K

---

## Future Enhancements

### Phase 2: LLM Completion Strategy

```python
async def complete_with_llm(node, missing_fields):
    """Ask LLM to fill missing fields."""
    prompt = f"Complete the following {node.node_type} node:\n"
    prompt += f"Name: {node.name}\n"
    prompt += f"Description: {node.description}\n"
    prompt += f"Missing fields: {missing_fields}\n"

    response = await llm_client.complete(prompt)
    completions = parse_llm_response(response)

    return completions
```

### Phase 3: Context-Based Inference (Enhanced)

```python
def complete_from_context_enhanced(graph, node, missing_fields):
    """
    Infer missing fields from:
    - Neighbors of same type
    - Type exemplars (high-quality examples)
    - Temporal neighbors (±5 min created_at)
    """
    # Find similar nodes
    similar = find_similar_nodes(graph, node)

    # Extract patterns
    patterns = extract_field_patterns(similar, missing_fields)

    # Apply patterns
    completions = apply_patterns(node, patterns)

    return completions
```

### Phase 4: Collaborative Completion

```python
# Store tasks in N2 organizational graph
# Other citizens can see and complete tasks
task_node = create_task_node_in_n2(task)

# Emit for other citizens
await broadcast_to_n2("task.needs_completion", task.to_dict())
```

---

## Troubleshooting

### Problem: Node marked incomplete incorrectly

**Cause:** Required fields registry missing node type

**Fix:** Add node type to `REQUIRED_NODE_FIELDS`:
```python
REQUIRED_NODE_FIELDS["MyNodeType"] = ["name", "description", "my_field"]
```

### Problem: Too many incomplete nodes

**Cause:** LLM/importer creating stubs without required fields

**Fix:**
1. Update importer to fill required fields
2. Add schema validation before creation
3. Set up automated completion tasks

### Problem: Defaults too generic

**Cause:** `complete_with_defaults()` using placeholder values

**Fix:** Customize defaults for your domain:
```python
if field_name == "definition" and "technical" in node.name.lower():
    defaults[field_name] = "Technical definition to be specified"
```

---

## Summary

Incomplete node healing provides:

✓ **Schema validation** - Check completeness per node/link type
✓ **Eligibility filtering** - Read-time gate (not second energy channel)
✓ **Task creation** - Automatic task for missing fields
✓ **Completion strategies** - Schema defaults, context inference, future LLM
✓ **24 comprehensive tests** - All passing

**Key principle:** Allow creation, prevent contamination, fix bottom-up.

**Phenomenology:** Stubs visible but greyed; "click into place" when completed.

**Integration:** Filter in traversal/WM selectors via `is_eligible()`.

**Testing:** `python orchestration/mechanisms/test_incomplete_node_healing.py`

**Documentation:** This file + `docs/specs/v2/learning_and_trace/incomplete_node_healing.md`
