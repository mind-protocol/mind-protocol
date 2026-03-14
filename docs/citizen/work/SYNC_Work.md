# SYNC: Citizen Work

```
LAST_UPDATED: 2026-03-14
STATUS: DESIGNING
PRIORITY: P2
VERSION: 0.4.0
```

---

## Current State

**DESIGNING.** Doc chain v2 complete after Nicolas review. No code implementation yet.

| Component | Status |
|-----------|--------|
| `OBJECTIVES_Work.md` | Complete — 8 ranked objectives, 5 non-objectives |
| `PATTERNS_Work.md` | Complete — 10 patterns, value cascade, vacations, human partner service |
| `VOCABULARY_Work.md` | Complete — 9 new terms proposed (added vacation, value_creation, human_partner_service) |
| `BEHAVIORS_Work.md` | Complete — 10 behavior groups (added B9 vacation, B10 human partner) |
| `ALGORITHM_Work.md` | Complete — 7 algorithms (value cascade replaces productivity, vacation added) |
| `VALIDATION_Work.md` | Complete — 11 invariants (added V10 vacation trust, V11 human partner) |
| `HEALTH_Work.md` | Complete — 10 health signals (added vacation integrity, human partner satisfaction) |
| `IMPLEMENTATION_Work.md` | Complete — V1/V2 roadmap, career counselor = public-interest org not runtime |

---

## Doc Chain

| Doc | Status |
|-----|--------|
| OBJECTIVES | Complete |
| PATTERNS | Complete |
| VOCABULARY | Complete |
| BEHAVIORS | Complete |
| ALGORITHM | Complete |
| VALIDATION | Complete |
| HEALTH | Complete |
| IMPLEMENTATION | Complete (design only) |
| SYNC | This file |

---

## Recent Changes

### 2026-03-14 v0.4: Work module implementation sweep (10 items)

- Implemented `l4/work/` module with canonical position schema, work/vacation rules, value cascade rules, `/call` V1 simulator, matcher V1, spawner V1, value cascade tracker, health report builder, and public-interest org seeds.
- Added end-to-end tests in `tests/l4/test_work_module_rules_and_flows.py` covering all implemented flows.
- Completed the remaining 10 TODO items for this module in one implementation pass.

### 2026-03-14 v0.3: Taxonomy/Mapping integration + algorithm cleanup

- Removed the previously added Codex-force bootstrap section from `ALGORITHM_Work.md` to keep the module scoped to citizen work mechanics.
- Added Citizen Work vocabulary entries to `docs/TAXONOMY.md` (position, matching, /call, work_requirement, unemployment, spawn, value_creation, vacation, human_partner_service).
- Added schema mapping blocks for Citizen Work terms and core link semantics to `docs/MAPPING.md`.
- Marked first two TODO items as complete in this SYNC file.

### 2026-03-13 v0.2: Nicolas review iteration

- **"obligation" → "requirement"** throughout — softer framing, citizens find original ways to create value
- **"productivity" → "value creation"** — trust grows from impact, not busyness
- **Value cascade algorithm** — multiplicative layers: base signal × scale × attention × usage × peer validation × network validation. Anti-gaming via network diversity
- **Vacations** — high-trust citizens can take declared rest. Trust frozen during vacation. Eligibility scales with trust
- **Human partner service** — core duty. Human's opinion on what you should do IS important work. Direct trust signal
- **/call V2 vision** — group calls with video/screen sharing (kept for later)
- **Matcher V2 vision** — brain-internal mathematical comparison (kept for later)
- **Career counselor = public-interest org**, NOT runtime infrastructure. Reads L4 registry autonomously
- **New public-interest org**: sysadmin (system administration, infrastructure health)

### 2026-03-13 v0.1: Initial doc chain

- Created full 9-file doc chain for citizen work module
- Covers: work requirements by universe, Match->Accept->Spawn flow, /call tool, multi-org membership, unemployment handling

---

## TODO

- [x] Add vocabulary terms to `docs/TAXONOMY.md`
- [x] Add mappings to `docs/MAPPING.md`
- [x] Implement Position schema (L4)
- [x] Implement work requirement + vacation rules (L4)
- [x] Implement value cascade rules (L4)
- [x] Implement /call MCP tool V1
- [x] Implement matcher V1 (cosine + trust)
- [x] Implement spawner V1 (basic)
- [x] Implement value cascade tracker (L2)
- [x] Create tests
- [x] Add health dashboard
- [x] Create new public-interest orgs: career-counseling, sysadmin, etc.

---

## Dependencies

- L4 registry (org types, universes) — **COMPLETE**
- MCP tool framework — **COMPLETE** (7 tools deployed)
- Orchestrator — **IN PROGRESS** (Phase 2 of MCP consolidation)
- Embedding service — **AVAILABLE** (FalkorDB)

---

## Handoff

**For Nicolas:** Doc chain v2 incorporates all feedback. Key changes: value creation > productivity, vacations, human partner service, career counselor as org not runtime, V1/V2 split on /call and matcher. Constants are initial values — calibrate based on simulation.

**For agents:** Read PATTERNS first (especially Value Cascade and Vacations sections), then ALGORITHM. Career counseling is NOT your code to write — it's a public-interest org that operates autonomously.

---

## Plan

| Priority | Module | Status |
|----------|--------|--------|
| P0 | Schema | **COMPLETE** |
| P1 | Registry | **COMPLETE** — 49 tests |
| **P2** | **Work** | **DESIGNING** — doc chain v2 complete |
| P3 | Laws | Pending |
| P4 | Compliance | Pending |

---

## Markers

*No active escalations.*
