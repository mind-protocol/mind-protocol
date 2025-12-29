# SYNC: L4 Laws

```
LAST_UPDATED: 2024-12-29
STATUS: DESIGNING
PRIORITY: P2
```

---

## Current State

8 laws documented. Full doc chain complete. Implementation not started.

| Component | Status |
|-----------|--------|
| `ecosystem_law_definitions_and_enforcement.py` | empty |
| `l4/seed/l4_protocol_seed_nodes_laws_and_schema.py` | **READY** — Seed data for when graph becomes truth |

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

## Laws Summary

| ID | Law |
|----|-----|
| L1 | Respect schema |
| L2 | Register to exist |
| L3 | No direct DB access |
| L4 | Cross-org via membrane |
| L5 | Hash-based identity |
| L6 | Receiver validates |
| L7 | Membrane fees |
| L8 | WebSocket only |

---

## TODO

- [ ] Implement law enforcement functions
- [ ] Add tests for each law
- [ ] Document violation error codes

---

## Handoff

**For agents:** Laws are ecosystem obligations, not graph internals.

**Key insight:** Laws define what you MUST do to participate. Everything else is your choice.

---

## Plan

| Priority | Module | Status |
|----------|--------|--------|
| P0 | Schema | **COMPLETE** |
| P1 | Registry | Next |
| **P2** | Laws | **THIS MODULE** — After Registry |
| P3 | Compliance | Pending |

**Phasing:** Seed data ready. Enforcement goes to mind-ops.

---

## Markers

@mind:TODO Implement law enforcement (mind-ops)
