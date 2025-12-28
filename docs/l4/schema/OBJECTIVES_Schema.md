# OBJECTIVES: L4 Schema

```
STATUS: DESIGNING
PURPOSE: Ranked goals for the schema module
```

---

## Primary Objective

**Define canonical node/link types for all Mind Protocol graphs.**

The schema is the source of truth. All graphs in L1-L4 must conform to this schema.

---

## Secondary Objectives

| Priority | Objective | Supports Primary |
|----------|-----------|------------------|
| S1 | Enable validation | Nodes/links can be checked against schema |
| S2 | Support versioning | Schema can evolve with clear migration paths |
| S3 | Provide defaults | New entities have sensible initial values |
| S4 | Document invariants | What must always be true |

---

## Non-Objectives

| ID | Non-Objective | Why Out of Scope |
|----|---------------|------------------|
| N1 | Runtime schema changes | Schema is protocol law, not config |
| N2 | Per-org customization | One schema for all, consistency > flexibility |
| N3 | Query optimization | Schema defines structure, not query patterns |
| N4 | Implementation details | Schema is abstract, Pydantic models are separate |

---

## Tradeoffs

| Decision | Tradeoff | Rationale |
|----------|----------|-----------|
| Fixed 5 types | Less flexibility | Predictable physics, simpler reasoning |
| Single link type | More properties | Embedding-based retrieval, no type queries |
| YAML format | Not code | Human-readable, language-agnostic |

---

## Success Criteria

- [ ] All node types defined with fields and defaults
- [ ] All link properties defined with ranges
- [ ] Invariants documented and testable
- [ ] Version tracked, migration path clear
