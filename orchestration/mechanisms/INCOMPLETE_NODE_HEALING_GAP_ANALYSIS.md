# Incomplete Node Healing: Gap Analysis (V2)

**Spec:** `docs/specs/v2/learning_and_trace/incomplete_node_healing.md`
**Current:** No implementation exists
**Date:** 2025-10-22

## Executive Summary

Incomplete node healing **does not exist** in current codebase. Need to implement from scratch:
1. Schema validation and completeness checking
2. Eligibility predicate (read-time filter)
3. Task creation for incomplete nodes
4. Completion strategies
5. Integration with traversal/WM selection

## What Exists (Minimal)

### ✅ Pydantic Schema (`substrate/schemas/consciousness_schema.py`)
- **Purpose:** Schema definitions for substrate layer
- **Capabilities:**
  - BaseNode with required fields (name, description, formation_trigger, confidence)
  - Pydantic validation on instantiation
  - Bitemporal fields
  - Consciousness metadata

**Gap:** Substrate layer schema, not used by orchestration/core models

### ✅ Core Models (`orchestration/core/node.py`, `link.py`)
- **Purpose:** Runtime data structures
- **Current state:**
  - Dataclass-based (not Pydantic)
  - No validation logic
  - No completeness checking
  - No eligibility field

**Gap:** No validation, no completeness tracking

### ⚠️ Bitemporal Tracking (`orchestration/mechanisms/bitemporal.py`)
- **Purpose:** Temporal validity checking
- **Has:** `is_currently_valid()`, `is_currently_known()`

**Gap:** Checks temporal validity, NOT completeness

## What's Missing from V2 Spec

### ❌ MISSING: Schema Registry (Required Fields Per Type)

**Spec requirement:**
> "A node/link with missing required fields is marked incomplete"

**Gap:**
- No registry defining which fields are required for each NodeType
- No mapping like `{NodeType.CONCEPT: ['definition'], NodeType.MECHANISM: ['how_it_works', 'inputs', 'outputs']}`
- Cannot determine "what fields are missing?" without schema

**Impact:** Cannot validate completeness

**Fix:** Create schema registry:
```python
# schemas/required_fields.py
REQUIRED_NODE_FIELDS: Dict[NodeType, List[str]] = {
    NodeType.CONCEPT: ['name', 'description', 'definition'],
    NodeType.MECHANISM: ['name', 'description', 'how_it_works', 'inputs', 'outputs'],
    NodeType.MEMORY: ['name', 'description', 'timestamp', 'participants'],
    # ... all node types
}

REQUIRED_LINK_FIELDS: Dict[LinkType, List[str]] = {
    LinkType.ENABLES: ['source_id', 'target_id', 'enabling_type', 'degree_of_necessity'],
    LinkType.BLOCKS: ['source_id', 'target_id', 'blocking_condition', 'severity'],
    # ... all link types
}
```

### ❌ MISSING: Completeness Validation

**Spec requirement:**
> "`is_complete(i)`: all required fields per type present"

**Gap:**
- No `is_complete()` function
- No validation on node/link creation
- No way to check "does this node have all required fields?"

**Impact:** Cannot determine eligibility

**Fix:** Add validation functions:
```python
def is_node_complete(node: Node) -> bool:
    """Check if node has all required fields for its type."""
    required = REQUIRED_NODE_FIELDS.get(node.node_type, [])
    for field_name in required:
        # Check if field exists and is not None/empty
        value = getattr(node, field_name, None)
        if value is None or (isinstance(value, str) and value == ""):
            return False
    return True

def get_missing_fields(node: Node) -> List[str]:
    """Return list of missing required fields."""
    required = REQUIRED_NODE_FIELDS.get(node.node_type, [])
    missing = []
    for field_name in required:
        value = getattr(node, field_name, None)
        if value is None or (isinstance(value, str) and value == ""):
            missing.append(field_name)
    return missing
```

### ❌ MISSING: Eligibility Predicate

**Spec requirement:**
> "eligible(i) := is_complete(i) ∧ status∈{active} ∧ E_i ≥ Θ_i"

**Gap:**
- No `eligible()` function
- No status field on nodes (active/deleted/archived)
- Eligibility not checked in traversal or WM selection

**Impact:** Incomplete nodes can contaminate traversal/WM

**Fix:** Add eligibility checking:
```python
def is_eligible(node: Node) -> bool:
    """
    Check if node is eligible for traversal/WM selection.

    Eligibility = completeness ∧ status ∧ activation
    """
    # 1. Completeness check
    if not is_node_complete(node):
        return False

    # 2. Status check (not deleted/archived)
    status = node.properties.get('status', 'active')
    if status not in ['active']:
        return False

    # 3. Activation check (standard energy threshold)
    if node.E < node.theta:
        return False

    return True
```

### ❌ MISSING: Incompleteness Tracking on Node/Link

**Spec requirement:**
> "marked incomplete and ineligible"

**Gap:**
- No `is_incomplete` field on Node/Link
- No `missing_fields` field
- No `completion_task_id` field

**Impact:** Cannot track which nodes need completion

**Fix:** Add fields to Node/Link:
```python
# Add to Node dataclass
is_incomplete: bool = False
missing_fields: List[str] = field(default_factory=list)
completion_task_id: Optional[str] = None
```

### ❌ MISSING: Task Creation for Incomplete Nodes

**Spec requirement:**
> "emit `task.create{type=complete_node, missing[], target_id}`"

**Gap:**
- No task creation logic
- No task data structure
- No task queue/registry

**Impact:** Incomplete nodes never get completed

**Fix:** Add task system:
```python
@dataclass
class CompletionTask:
    """Task to complete an incomplete node/link."""
    id: str
    task_type: str = "complete_node"  # or "complete_link"
    target_id: str  # Node/link ID to complete
    target_type: str  # NodeType or LinkType
    missing_fields: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending/in_progress/completed/failed
    completion_strategy: Optional[str] = None
    completion_source: Optional[str] = None
    confidence: float = 0.0

def create_completion_task(
    obj: Union[Node, Link],
    missing_fields: List[str]
) -> CompletionTask:
    """Create task to complete incomplete object."""
    task = CompletionTask(
        id=f"task_{uuid.uuid4().hex[:8]}",
        target_id=obj.id,
        target_type=str(obj.node_type if isinstance(obj, Node) else obj.link_type),
        missing_fields=missing_fields
    )
    return task
```

### ❌ MISSING: Completion Strategies

**Spec requirement:**
> "Context inference (neighbors, type exemplars), LLM fill with guardrails, Defaults from schema"

**Gap:**
- No completion strategy implementations
- No context-based inference
- No LLM integration for completion
- No default value registry

**Impact:** Tasks created but never completed

**Fix:** Add completion strategies:
```python
class CompletionStrategy(Enum):
    """Strategies for completing missing fields."""
    CONTEXT_INFERENCE = "context_inference"  # Infer from neighbors
    LLM_FILL = "llm_fill"  # Ask LLM to fill
    SCHEMA_DEFAULT = "schema_default"  # Use schema default
    MANUAL = "manual"  # Human intervention required

def complete_node_from_context(
    graph: Graph,
    node: Node,
    missing_fields: List[str]
) -> Dict[str, Any]:
    """
    Infer missing fields from neighboring nodes.

    Strategy: Look at neighbors of same type, find common patterns.
    """
    completions = {}
    # TODO: Implement context-based inference
    return completions

def complete_node_with_defaults(
    node: Node,
    missing_fields: List[str]
) -> Dict[str, Any]:
    """Fill missing fields with schema defaults."""
    defaults = {
        'description': f"Auto-generated description for {node.name}",
        'confidence': 0.5,  # Low confidence for auto-filled
        # ... more defaults
    }
    completions = {
        field: defaults.get(field, "")
        for field in missing_fields
        if field in defaults
    }
    return completions
```

### ❌ MISSING: Integration with Traversal/WM Selection

**Spec requirement:**
> "selectors in `mechanisms/sub_entity_traversal.py` read `eligible(i)`"

**Gap:**
- `sub_entity_traversal.py` doesn't check eligibility
- `wm_pack.py` (working memory) doesn't filter incomplete nodes
- Incomplete nodes can be selected

**Impact:** Incomplete nodes contaminate results

**Fix:** Add eligibility filtering:
```python
# In sub_entity_traversal.py
def select_traversal_candidates(
    graph: Graph,
    source_node: Node,
    goal: SubEntityGoal
) -> List[TraversalCandidate]:
    """Select candidate links for traversal (eligibility-aware)."""
    candidates = []

    for link in source_node.outgoing_links:
        target = link.target

        # NEW: Check eligibility
        if not is_eligible(target):
            continue  # Skip incomplete/ineligible nodes

        # ... existing candidate selection logic

    return candidates
```

### ❌ MISSING: Observability Events

**Spec requirement:**
> "Events: `node.incomplete`, `link.incomplete`, `task.create`, `task.resolve`, `eligibility.update`"

**Gap:**
- No events emitted for incompleteness
- No metrics tracking completion rate
- No visibility into backlog

**Impact:** Cannot monitor completion system health

**Fix:** Add event emission:
```python
# When creating incomplete node
await broadcaster.broadcast_event("node.incomplete", {
    "v": "2",
    "node_id": node.id,
    "node_type": str(node.node_type),
    "missing_fields": missing_fields,
    "created_at": node.created_at.isoformat()
})

# When creating task
await broadcaster.broadcast_event("task.create", {
    "v": "2",
    "task_id": task.id,
    "task_type": task.task_type,
    "target_id": task.target_id,
    "missing_fields": task.missing_fields
})

# When completing task
await broadcaster.broadcast_event("task.resolve", {
    "v": "2",
    "task_id": task.id,
    "strategy": task.completion_strategy,
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

### ❌ MISSING: Metrics and Dashboards

**Spec requirement:**
> "Metrics: backlog (#incomplete by type/scope), median time-to-complete, %auto-completed by strategy, eligibility hit/miss rate"

**Gap:**
- No backlog tracking
- No completion time metrics
- No strategy success rates
- No eligibility statistics

**Impact:** Cannot tune completion system

**Fix:** Add metrics:
```python
@dataclass
class CompletionMetrics:
    """Metrics for incomplete node healing."""
    incomplete_nodes_by_type: Dict[NodeType, int]
    incomplete_links_by_type: Dict[LinkType, int]
    tasks_pending: int
    tasks_completed: int
    tasks_failed: int
    median_time_to_complete_ms: float
    completion_by_strategy: Dict[str, int]  # {strategy: count}
    eligibility_hits: int  # Eligible nodes selected
    eligibility_misses: int  # Ineligible nodes filtered out
```

### ❌ MISSING: Configuration

**Spec requirement:**
> "`INCOMPLETE_TRAVERSABLE=False` in `core/settings.py`"

**Gap:**
- No configuration for incomplete node behavior
- No flag to enable/disable strict eligibility

**Impact:** Cannot toggle behavior

**Fix:** Add settings:
```python
# In core/settings.py
INCOMPLETE_TRAVERSABLE: bool = False  # Strict: incomplete nodes ineligible
INCOMPLETE_VISUALIZATION: str = "dashed_grey"  # How to render incomplete nodes
COMPLETION_STRATEGY_ORDER: List[str] = [
    "context_inference",
    "schema_default",
    "llm_fill"  # Try in this order
]
COMPLETION_SLA_MS: int = 3600000  # 1 hour to complete
```

## Implementation Plan

### Phase 1: Schema Registry & Validation (CRITICAL)

1. Create `schemas/required_fields.py`:
   - `REQUIRED_NODE_FIELDS` dictionary
   - `REQUIRED_LINK_FIELDS` dictionary
   - Map all NodeType/LinkType to required fields

2. Add validation functions:
   - `is_node_complete(node) -> bool`
   - `is_link_complete(link) -> bool`
   - `get_missing_fields(obj) -> List[str]`

3. Add fields to Node/Link dataclasses:
   - `is_incomplete: bool`
   - `missing_fields: List[str]`
   - `completion_task_id: Optional[str]`

### Phase 2: Eligibility Predicate

1. Add `is_eligible(node) -> bool` function
2. Add `is_eligible(link) -> bool` function
3. Add status field to node properties
4. Integrate with existing activation check (E >= theta)

### Phase 3: Task System

1. Create `CompletionTask` dataclass
2. Add `create_completion_task()` function
3. Create task registry (in-memory or N2 graph)
4. Add task lifecycle management (create/assign/complete/fail)

### Phase 4: Completion Strategies

1. Implement `complete_node_from_context()`
2. Implement `complete_node_with_defaults()`
3. Add LLM completion strategy (optional/future)
4. Add confidence tracking to completions

### Phase 5: Integration with Selectors

1. Update `sub_entity_traversal.py`:
   - Filter candidates by eligibility
   - Emit eligibility miss events

2. Update working memory selection:
   - Filter WM candidates by eligibility
   - Track eligibility statistics

3. Update graph visualization:
   - Render incomplete nodes as dashed/grey
   - Show missing fields in tooltips

### Phase 6: Observability & Metrics

1. Emit incompleteness events
2. Emit task lifecycle events
3. Emit eligibility change events
4. Track completion metrics
5. Add dashboard components

## Minimal Viable Implementation

To satisfy spec with minimal effort:

1. **Create required fields registry:**
   - Basic mapping for core node/link types
   - Start with CONCEPT, MEMORY, TASK, MECHANISM

2. **Add validation functions:**
   - `is_node_complete()`
   - `get_missing_fields()`

3. **Add eligibility check:**
   - `is_eligible() = is_complete() and E >= theta`
   - Integrate into traversal selector

4. **Create completion tasks:**
   - Simple task dataclass
   - Basic schema default strategy

5. **Emit events:**
   - `node.incomplete`
   - `task.create`

This gives 80% of spec value with 20% of effort.

## Open Questions

1. **Schema source:** Where do required fields come from?
   - Option A: Hardcoded registry (simple, static)
   - Option B: Load from COMPLETE_TYPE_REFERENCE.md (dynamic)
   - Option C: Pydantic schemas (substrate layer integration)

2. **Task storage:** Where are tasks stored?
   - Option A: In-memory list (ephemeral)
   - Option B: N2 organizational graph (persistent)
   - Option C: Separate task database

3. **LLM integration:** How to call LLM for completion?
   - Requires API integration
   - Needs prompt templates
   - Guardrails for validation

4. **Temporal context:** How to get ±Δt neighbors for context inference?
   - Use bitemporal `created_at` for proximity
   - Query nodes within ±5 minutes
   - Helpful for completion strategies

5. **Status field:** Where does `status` live?
   - Option A: New field on Node/Link
   - Option B: `node.properties['status']`
   - Option C: Separate status registry

## Recommendation

**Implement Phase 1 + 2 + 3 + 5 (Schema + Eligibility + Tasks + Integration):**

1. Create required fields registry (hardcoded for core types)
2. Add validation and eligibility functions
3. Create basic task system with schema defaults
4. Integrate eligibility into traversal/WM selectors
5. Emit basic observability events

Skip LLM completion and advanced metrics for now (future enhancement).

This satisfies core spec requirements and enables the key behavior: **incomplete nodes are visible but ineligible for selection**.
