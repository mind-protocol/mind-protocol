# SYNC: L4 Schema

```
LAST_UPDATED: 2024-12-29
STATUS: IMPLEMENTED
VERSION: 1.8.1
```

---

## Current State

Schema YAML defined and canonical. Full doc chain complete. **Pydantic implementation complete. P0 DONE.**

| Component | Status |
|-----------|--------|
| `schema.yaml` | **CANONICAL** |
| `node_type_enum_and_base_pydantic_models.py` | **IMPLEMENTED** — NodeType, NodeBase, MomentBase, specific types |
| `link_base_schema_with_semantic_axes.py` | **IMPLEMENTED** — LinkBase with all axes |
| `schema_version_tracker_and_compatibility.py` | **IMPLEMENTED** — Version tracking and compatibility |
| `node_and_link_schema_validators.py` | **IMPLEMENTED** — validate_node, validate_link, check_invariants |
| `tests/l4/test_schema_pydantic_models_and_validators.py` | **34 tests passing** |

---

## Doc Chain

| Doc | Status |
|-----|--------|
| OBJECTIVES | Complete |
| PATTERNS | Complete |
| BEHAVIORS | Complete |
| ALGORITHM | Complete |
| VALIDATION | Complete |
| IMPLEMENTATION | Complete |
| HEALTH | Complete |
| SYNC | This file |

---

## Recent Changes

### 2024-12-29: Files renamed to naming convention

Files renamed to 25-75 char explicit responsibility names:
- `node_types.py` → `node_type_enum_and_base_pydantic_models.py`
- `link_schema.py` → `link_base_schema_with_semantic_axes.py`
- `versions.py` → `schema_version_tracker_and_compatibility.py`
- `validation.py` → `node_and_link_schema_validators.py`
- `test_schema.py` → `test_schema_pydantic_models_and_validators.py`

### 2024-12-29: Pydantic implementation complete

- Implemented node types with NodeType enum, NodeBase, MomentBase, specific node types
- Implemented LinkBase with all semantic axes
- Implemented version tracking and compatibility checks
- Implemented validate_node, validate_link, check_invariants
- Added 34 passing tests

### 2024-12-28: Schema moved to mind-protocol

- Copied from `ngram/docs/schema/schema.yaml`
- Cleaned: removed pseudocode, kept definitions
- Added to `templates/mind/schema.yaml` for client distribution

---

## TODO

- [x] Implement `node_types.py` — Pydantic models for NodeBase, MomentBase
- [x] Implement `link_schema.py` — Pydantic model for LinkBase
- [x] Implement `versions.py` — Schema version tracking
- [x] Implement `validation.py` — Range and invariant validation
- [x] Add tests in `tests/l4/test_schema.py`

**P0 Complete.** Next: P1 (Registry)

---

## Handoff

**For agents:** Schema is complete. Next: P1 Registry.

**Key files:**
- `l4/schema/schema.yaml` — Canonical schema definition
- `l4/schema/node_type_enum_and_base_pydantic_models.py` — Node types
- `l4/schema/link_base_schema_with_semantic_axes.py` — Link schema

---

## Plan

| Priority | Module | Status |
|----------|--------|--------|
| **P0** | Schema | **COMPLETE** — 34 tests passing |
| P1 | Registry | Next — Pydantic models for Citizen, Org, Endpoint |
| P2 | Laws | Pending — Enforcement functions |
| P3 | Compliance | Pending — Test suite |

**Phasing decision pending:** When does graph become source of truth?

- Phase 1 (now): Docs are truth
- Phase 2: Graph is truth, seed data ready in `l4/seed/`
- Phase 3: Graph generates docs

---

## Markers

*No active escalations.*
