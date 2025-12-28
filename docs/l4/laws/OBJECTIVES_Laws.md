# OBJECTIVES: L4 Laws

```
STATUS: DESIGNING
PURPOSE: Ranked goals for the laws module
```

---

## Primary Objective

**Define and enforce immutable protocol laws.**

Laws are invariants that MUST be true. Always. Everywhere.

---

## Secondary Objectives

| Priority | Objective | Supports Primary |
|----------|-----------|------------------|
| S1 | Encode schema invariants | Laws derived from schema.yaml |
| S2 | Provide validation | Check if entity violates law |
| S3 | Document rationale | Why each law exists |

---

## Non-Objectives

| ID | Non-Objective | Why Out of Scope |
|----|---------------|------------------|
| N1 | Configurable rules | Live in mind-mcp |
| N2 | Runtime tuning | Laws don't change at runtime |
| N3 | Per-deployment settings | Laws are protocol-wide |

---

## Success Criteria

- [ ] All schema.yaml invariants encoded as laws
- [ ] Validation function for each law
- [ ] Tests for law violations
