# OBJECTIVES: L4 Registry

```
STATUS: DESIGNING
PURPOSE: Ranked goals for the registry module
```

---

## Primary Objective

**Manage identity registration for citizens, orgs, and endpoints.**

The registry is the authoritative source for "who exists" in Mind Protocol.

---

## Secondary Objectives

| Priority | Objective | Supports Primary |
|----------|-----------|------------------|
| S1 | Enable lookup | Find citizen/org by ID |
| S2 | Validate identity | JWT verification for all operations |
| S3 | Track endpoints | Know where to push for each org |
| S4 | Support cross-org discovery | Via L3 opt-in, not registry itself |

---

## Non-Objectives

| ID | Non-Objective | Why Out of Scope |
|----|---------------|------------------|
| N1 | Graph storage | Citizens store their own graphs (L1) |
| N2 | Permission management | Orgs manage their own permissions (L2) |
| N3 | Routing logic | Membrane handles routing (mind-ops) |
| N4 | Payment processing | Economy module handles $MIND |

---

## Tradeoffs

| Decision | Tradeoff | Rationale |
|----------|----------|-----------|
| Public registry | Privacy vs transparency | L4 = law, must be verifiable |
| One org per citizen | Flexibility vs simplicity | Clear ownership, no conflicts |
| JWT-only auth | Complexity vs security | Standard, well-understood |

---

## Success Criteria

- [ ] Register citizen with org membership
- [ ] Register org with endpoint
- [ ] Lookup citizen by ID
- [ ] Lookup org by ID
- [ ] Validate JWT for any operation
- [ ] Verify hash for cross-org stimuli
