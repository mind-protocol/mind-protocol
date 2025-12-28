# SYNC: L4 Registry

```
LAST_UPDATED: 2024-12-28
STATUS: DESIGNING
```

---

## Current State

Design documented. Implementation not started.

| Component | Status |
|-----------|--------|
| `citizens.py` | empty |
| `orgs.py` | empty |
| `endpoints.py` | empty |
| `validation.py` | empty |

---

## TODO

- [ ] Define Citizen Pydantic model
- [ ] Define Org Pydantic model
- [ ] Define Endpoint Pydantic model
- [ ] Implement JWT validation
- [ ] Implement hash verification for cross-org
- [ ] Add GraphQL resolvers for lookup
- [ ] Add tests

---

## Dependencies

- `l4/schema/` — Uses NodeBase for citizen/org nodes
- `api/graphql/` — Exposes registry via GraphQL
- `graph/` — Stores registry in Neo4j

---

## Handoff

**For agents:** Start with Pydantic models for Citizen, Org, Endpoint.

**Key decisions:**
- Citizen belongs to exactly one org
- Org has exactly one endpoint
- All operations require JWT validation

---

## Markers

@mind:TODO Implement registry Pydantic models
@mind:TODO Implement JWT validation
