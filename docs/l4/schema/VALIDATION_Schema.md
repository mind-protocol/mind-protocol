# VALIDATION: L4 Schema

```
STATUS: DESIGNING
PURPOSE: Invariants that must always hold for schema compliance
```

---

## Critical Invariants

These MUST be true at all times. Violation = protocol breach.

| ID | Invariant | Verification |
|----|-----------|--------------|
| V1 | **5 node types only** | `node.node_type in ["actor", "moment", "narrative", "space", "thing"]` |
| V2 | **Single link type** | `link.type == "link"` |
| V3 | **Non-negative weight** | `node.weight >= 0` |
| V4 | **Non-negative energy** | `node.energy >= 0` |
| V5 | **Polarity bounded** | `-1 <= link.polarity <= 1` |
| V6 | **Hierarchy bounded** | `-1 <= link.hierarchy <= 1` |
| V7 | **Permanence bounded** | `0 <= link.permanence <= 1` |
| V8 | **Valid references** | Links point to existing nodes |

---

## Derived Invariants

These follow from physics formulas in schema.yaml.

| ID | Invariant | Formula |
|----|-----------|---------|
| D1 | Forward coloration by permanence | `fc_weight = 1 - permanence` |
| D2 | Branching only on Moments | `spawn_subentity() only valid for node_type == "moment"` |

---

## Soft Constraints

These SHOULD be true but won't break the protocol if violated.

| ID | Constraint | Reason |
|----|------------|--------|
| S1 | Embedding present | Required for semantic search |
| S2 | Synthesis regenerated | Human-readable representation |
| S3 | Timestamps accurate | Auditing and decay |

---

## Verification Procedures

```python
def verify_schema_compliance(graph):
    """Check all nodes and links against schema invariants."""
    violations = []

    for node in graph.nodes:
        if node.node_type not in VALID_TYPES:
            violations.append(f"V1: Invalid node_type {node.node_type}")
        if node.weight < 0:
            violations.append(f"V3: Negative weight on {node.id}")
        if node.energy < 0:
            violations.append(f"V4: Negative energy on {node.id}")

    for link in graph.links:
        if link.type != "link":
            violations.append(f"V2: Invalid link type {link.type}")
        if not (-1 <= link.polarity <= 1):
            violations.append(f"V5: Polarity out of range on {link.id}")
        # ... etc

    return violations
```

---

## When Validation Runs

| Trigger | What's Checked |
|---------|----------------|
| Node creation | V1, V3, V4 |
| Link creation | V2, V5, V6, V7, V8 |
| Stimulus receipt | Full graph validation |
| Schema upgrade | Migration compatibility |

---

## Related

- `ALGORITHM_Schema.md` — How validation works
- `HEALTH_Schema.md` — Runtime verification
- `l4/schema/schema.yaml` — Authoritative ranges
