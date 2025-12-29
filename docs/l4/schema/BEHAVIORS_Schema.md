# BEHAVIORS: L4 Schema

```
STATUS: DESIGNING
PURPOSE: Observable effects of the schema system
```

---

## What the Schema Does

The schema defines the **structure** of all graphs in Mind Protocol. It doesn't run — it constrains.

---

## Observable Effects

### B1: Node Creation Constrained

| Input | Observable Effect |
|-------|-------------------|
| Create node with `node_type: "custom"` | Rejected — must be one of 5 types |
| Create node with `node_type: "actor"` | Accepted — valid type |
| Create node without `weight` | Rejected — required field |

### B2: Link Creation Constrained

| Input | Observable Effect |
|-------|-------------------|
| Create link type `KNOWS` | Rejected — only `link` allowed |
| Create link with `polarity: 2.0` | Rejected — must be in [-1, 1] |
| Create link with all required fields | Accepted |

### B3: Range Enforcement

| Field | Range | Effect of Violation |
|-------|-------|---------------------|
| weight | [0, ∞) | Clamp or reject |
| energy | [0, ∞) | Clamp or reject |
| polarity | [-1, 1] | Clamp or reject |
| permanence | [0, 1] | Clamp or reject |

### B4: Subtype Behavior

| Input | Observable Effect |
|-------|-------------------|
| `node_type: "actor", type: "npc"` | Accepted — subtype is freeform string |
| `node_type: "actor", type: null` | Accepted — subtype optional |
| `node_type: "custom_actor"` | Rejected — not a valid node_type |

---

## Behavior by Node Type

| Node Type | Specific Behaviors |
|-----------|-------------------|
| Actor | Can have `budget`, emits stimuli |
| Moment | Only type that can branch (spawn subentities) |
| Narrative | High-weight attractor, destination node |
| Space | Container, allows bidirectional flow |
| Thing | Passthrough, tends toward weight=0 |

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty content field | Allowed — synthesis regenerates |
| Missing embedding | Warning — embedding required for retrieval |
| Circular references | Allowed — graph can have cycles |
| Orphan nodes | Allowed — node can exist without links |

---

## Related

- `l4/schema/schema.yaml` — Canonical definition
- `VALIDATION_Schema.md` — Invariants to enforce
- `ALGORITHM_Schema.md` — How validation works
