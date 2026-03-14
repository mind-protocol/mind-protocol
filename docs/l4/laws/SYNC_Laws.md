# SYNC: L4 Laws

```
LAST_UPDATED: 2026-03-14
STATUS: COMPLETE
PRIORITY: P2
```

---

## Current State

8 laws documented. Implementation complete. 53 tests passing.

| Component | Status |
|-----------|--------|
| `l4/laws/constants.py` | **COMPLETE** — Law definitions, fee constraints |
| `l4/laws/compliance.py` | **COMPLETE** — Stimulus + ComplianceResult + check_stimulus_compliance |
| `l4/laws/audit.py` | **COMPLETE** — AuditReport + audit_org |
| `l4/laws/__init__.py` | **COMPLETE** — Public API exports |
| `tests/l4/test_laws_compliance_and_audit.py` | **53 tests passing** |
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

| ID | Law | Enforcement |
|----|-----|-------------|
| L1 | Respect schema | Runtime (compliance checker) |
| L2 | Register to exist | Runtime (compliance checker) |
| L3 | No direct DB access | Architecture (no code) |
| L4 | Cross-org via membrane | Architecture (no code) |
| L5 | Hash-based identity | Runtime (JWT detection + hash verification) |
| L6 | Receiver validates | Architecture (receiver's code) |
| L7 | Membrane fees | Runtime (compliance checker) |
| L8 | WebSocket only | Architecture (API design) |

---

## Architecture Decisions

- **Callables for registry integration:** `check_stimulus_compliance` takes `sender_exists` and `verify_identity` callables instead of importing registry directly. This keeps the laws module decoupled from graph infrastructure. The membrane provides these callables at runtime.
- **JWT detection via regex:** `_looks_like_jwt` uses a compiled regex to detect `eyJ...eyJ...` patterns embedded anywhere in text, catching JWTs in node content/synthesis and link synthesis fields.
- **Dataclasses, not Pydantic:** Matches existing patterns in `l4/work/`.
- **Removed empty placeholder:** `ecosystem_law_definitions_and_enforcement.py` deleted in favor of the three focused files (constants, compliance, audit).

---

## TODO

- [x] Implement law enforcement functions
- [x] Add tests for each law (53 tests, all 9 validation invariants covered)
- [x] Document violation error codes (violations use "L{n}: description" format)

---

## Handoff

**For agents:** Laws module is complete. Compliance checker validates stimuli against L1/L2/L5/L7. L3/L4/L6/L8 are enforced by architecture. Integration point: membrane calls `check_stimulus_compliance` with graph-backed callables for sender lookup and hash verification.

**Key insight:** Laws define what you MUST do to participate. Everything else is your choice.

---

## Plan

| Priority | Module | Status |
|----------|--------|--------|
| P0 | Schema | **COMPLETE** |
| P1 | Registry | **COMPLETE** |
| **P2** | Laws | **COMPLETE** |
| P3 | Compliance | Pending (P3 = broader compliance beyond laws) |

**Phasing:** Seed data ready. Runtime enforcement goes to mind-ops via callables.
