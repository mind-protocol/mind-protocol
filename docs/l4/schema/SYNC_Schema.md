# SYNC: L4 Schema

```
LAST_UPDATED: 2024-12-28
STATUS: DESIGNING
VERSION: 1.8.1
```

---

## Current State

Schema YAML defined and canonical. Pydantic implementation not started.

| Component | Status |
|-----------|--------|
| `schema.yaml` | **CANONICAL** |
| `node_types.py` | empty |
| `link_schema.py` | empty |
| `versions.py` | empty |
| `validation.py` | empty |

---

## Recent Changes

### 2024-12-28: Schema moved to mind-protocol

- Copied from `ngram/docs/schema/schema.yaml`
- Cleaned: removed pseudocode, kept definitions
- Added to `templates/mind/schema.yaml` for client distribution

---

## TODO

- [ ] Implement `node_types.py` — Pydantic models for NodeBase, MomentBase
- [ ] Implement `link_schema.py` — Pydantic model for LinkBase
- [ ] Implement `versions.py` — Schema version tracking
- [ ] Implement `validation.py` — Range and invariant validation
- [ ] Add tests in `tests/l4/test_schema.py`

---

## Handoff

**For agents:** Start with `node_types.py` — it's the foundation.

**Key files:**
- `l4/schema/schema.yaml` — Read this first
- `l4/schema/node_types.py` — Implement NodeType enum, NodeBase, MomentBase

**Watch out:**
- Match field names exactly to schema.yaml
- Include all ranges and defaults
- Use Pydantic v2

---

## Markers

@mind:TODO Implement Pydantic models matching schema.yaml
