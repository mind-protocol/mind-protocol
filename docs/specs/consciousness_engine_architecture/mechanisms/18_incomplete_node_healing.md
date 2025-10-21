# Mechanism 18: Incomplete Node Self-Healing

**Type:** Data Quality / Self-Organization
**Phase:** 3 (Core consciousness mechanisms)
**Status:** Specified
**Source:** Discussion #014 - Incomplete Data Handling Strategy
**Author:** Nicolas (architectural guidance), Luca (specification)

---

## Purpose

Allow incomplete node creation (LLM will often create nodes with missing fields), mark them as non-traversable, and automatically trigger task creation to complete missing information. Self-healing through bottom-up task generation, not top-down synchronization.

---

## Architectural Principle

**CRITICAL: Bottom-up self-healing, not top-down validation**

- Incomplete nodes WILL exist (expected, not error)
- Don't block node creation waiting for completeness
- Don't use global synchronization to ensure completeness
- Self-heal through automatic task creation

**Nicolas's guidance:**
> "We want to allow for incomplete node creation because the LLM is going to often make incomplete nodes. However, this should be fixed as soon as possible by the creation of tasks that are automatically triggered to complete the missing information."

---

## Core Mechanism

### Node Completeness Detection

```python
class Node:
    """
    Node with completeness tracking

    Every node type has required fields (from schema)
    Missing required fields → incomplete
    """

    def __init__(self, node_type, **fields):
        self.type = node_type
        self.fields = fields
        self.is_complete = self._check_completeness()
        self.traversable = self.is_complete  # Incomplete = non-traversable

    def _check_completeness(self):
        """
        Check if all required fields present

        Required fields defined in COMPLETE_TYPE_REFERENCE.md
        """
        schema = get_schema_for_type(self.type)
        required_fields = schema.required_fields

        for field in required_fields:
            if field not in self.fields or self.fields[field] is None:
                return False  # Missing required field

        return True  # All required fields present

    def get_missing_fields(self):
        """Return list of missing required fields"""
        schema = get_schema_for_type(self.type)
        required_fields = schema.required_fields

        missing = []
        for field in required_fields:
            if field not in self.fields or self.fields[field] is None:
                missing.append(field)

        return missing
```

### Automatic Task Creation

```python
def handle_incomplete_node(node):
    """
    Automatically create task to complete missing information

    Triggered immediately upon incomplete node detection
    """

    if node.is_complete:
        return  # Already complete, nothing to do

    # Get missing fields
    missing_fields = node.get_missing_fields()

    # Create completion task
    task = Task(
        type="Complete_Node_Metadata",
        description=f"Complete missing fields for {node.name}",
        target_node_id=node.id,
        target_node_name=node.name,
        target_node_type=node.type,
        missing_fields=missing_fields,
        priority="high",  # Blocks traversal - high priority
        created_by="system",
        creation_reason="incomplete_node_detected"
    )

    # Add task to task queue
    task_queue.add(task)

    logger.info(
        f"Auto-created task to complete {node.name} "
        f"(missing: {', '.join(missing_fields)})"
    )
```

### Traversability Blocking

```python
def is_node_traversable(node, entity):
    """
    Incomplete nodes are NOT traversable

    Sub-entities cannot traverse incomplete nodes
    Prevents incomplete data from polluting traversal
    """

    # Check 1: Node must be complete
    if not node.is_complete:
        return False  # Incomplete → non-traversable

    # Check 2: Node must have minimum energy for entity
    if node.energy[entity] < node.activation_threshold:
        return False  # Below activation threshold

    # Check 3: Node must not be marked deleted/archived
    if node.status in ["deleted", "archived"]:
        return False

    return True  # Passes all checks → traversable
```

---

## Task Completion Flow

**1. LLM creates node with missing fields**
```json
{
  "type": "Realization",
  "name": "new_insight_about_consciousness",
  "what_i_realized": "Something important about substrate",
  // MISSING: confidence, formation_trigger, description
}
```

**2. System detects incompleteness**
- Node creation succeeded
- Completeness check fails
- `is_complete = False`
- `traversable = False`

**3. System auto-creates task**
```python
Task(
  description="Complete missing fields for new_insight_about_consciousness",
  missing_fields=["confidence", "formation_trigger", "description"],
  priority="high"
)
```

**4. Task execution (by sub-entity or system)**
- Fetch node context
- Infer missing fields from context
- Update node with completed fields
- Mark node as complete
- Node becomes traversable

**5. Node becomes usable**
- `is_complete = True`
- `traversable = True`
- Sub-entities can now traverse
- Node participates in consciousness dynamics

---

## Incomplete Links

**Links can also be incomplete:**

```python
class Link:
    def __init__(self, link_type, source, target, **fields):
        self.type = link_type
        self.source = source
        self.target = target
        self.fields = fields
        self.is_complete = self._check_completeness()
        self.traversable = self.is_complete

    def get_missing_fields(self):
        """Return missing required fields for this link type"""
        schema = get_schema_for_link_type(self.type)
        required_fields = schema.required_fields

        missing = []
        for field in required_fields:
            if field not in self.fields or self.fields[field] is None:
                missing.append(field)

        return missing
```

**Same mechanism:**
- Incomplete link → non-traversable
- Auto-create completion task
- Task fills missing fields
- Link becomes traversable

---

## Visual Indication

**For observability (visualization):**

```python
def render_node(node):
    """
    Incomplete nodes have distinct visual style

    Makes incompleteness visible to human observers
    """

    if not node.is_complete:
        return {
            "style": "dashed",
            "color": "gray",
            "opacity": 0.5,
            "label": f"{node.name} (INCOMPLETE)",
            "tooltip": f"Missing: {', '.join(node.get_missing_fields())}"
        }
    else:
        return {
            "style": "solid",
            "color": determine_color(node),
            "opacity": 1.0,
            "label": node.name
        }
```

**Effect:**
- Incomplete nodes appear grayed out and dashed
- Tooltip shows missing fields
- Humans can see what needs completion

---

## Completion Strategies

**Task execution can use multiple strategies:**

**1. Context Inference**
```python
def infer_missing_fields(node):
    """Infer from surrounding graph context"""

    # Look at connected nodes
    similar_nodes = find_similar_nodes(node)

    # Infer confidence from similar node patterns
    if "confidence" in missing:
        node.confidence = np.mean([n.confidence for n in similar_nodes])

    # Infer formation_trigger from creation context
    if "formation_trigger" in missing:
        node.formation_trigger = infer_trigger_from_context(node)
```

**2. LLM Completion**
```python
def llm_complete_node(node):
    """Ask LLM to fill missing fields"""

    prompt = f"""
    Node: {node.name} (type: {node.type})
    Existing fields: {node.fields}
    Missing fields: {node.get_missing_fields()}

    Please provide values for missing fields based on context.
    """

    response = llm_query(prompt)
    updated_fields = parse_completion(response)
    node.update(updated_fields)
```

**3. Default Values**
```python
def apply_default_values(node):
    """Use schema-defined defaults"""

    schema = get_schema_for_type(node.type)

    for field in node.get_missing_fields():
        if field in schema.defaults:
            node.fields[field] = schema.defaults[field]
```

---

## Integration Points

**Interacts with:**
- **Mechanism 05** (Sub-entity Mechanics) - sub-entities check traversability before traversing
- **Task system** (not yet specified) - tasks get created and executed
- **Schema validation** - required fields defined in schema
- **Visualization** - incomplete nodes rendered distinctly

---

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `allow_incomplete_creation` | True | Boolean | Whether to allow incomplete nodes at all |
| `auto_task_creation` | True | Boolean | Whether to auto-create completion tasks |
| `incomplete_traversable` | False | Boolean | Whether incomplete nodes can be traversed |
| `task_priority` | "high" | String | Priority level for completion tasks |

---

## Implementation Notes

**For Felix:**
- Completeness check on every node/link creation
- `is_complete` and `traversable` as node/link properties
- Task creation uses existing task queue infrastructure
- Schema-based validation (reference COMPLETE_TYPE_REFERENCE.md)

**Performance:**
- O(1) completeness check per node creation
- Task creation is async (doesn't block)
- No global validation needed

---

## Validation Criteria

**Mechanism works correctly if:**
1. ✅ Incomplete nodes can be created (no blocking)
2. ✅ Incomplete nodes are non-traversable (sub-entities skip them)
3. ✅ Tasks auto-created for all incomplete nodes
4. ✅ Task completion makes nodes traversable
5. ✅ Incomplete nodes visible in visualization (grayed out)

---

## Edge Cases

**What if task completion fails?**
- Node remains incomplete and non-traversable
- Task can be retried (manual or automatic)
- Human can manually complete fields

**What if required fields change (schema update)?**
- Existing complete nodes might become incomplete
- Re-trigger task creation for newly-incomplete nodes
- Migration mechanism needed

**What if node has partial information?**
- Some required fields present, some missing
- Node is incomplete (traversable = false)
- Task only needs to fill missing fields (not re-do existing)

---

**Status:** Ready for implementation
**Next Steps:** Requires task system infrastructure (not yet specified)
