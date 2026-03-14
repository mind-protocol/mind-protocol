# SYNC — L3 Emotional Coloring

**Module:** L3 Emotional Coloring
**Area:** schema/l3_emotional_coloring
**Last updated:** 2026-03-14

---

## Maturity

**STATUS: DESIGNING — Doc chain COMPLETE (8/8 files)**

### What's canonical:
- Decision: L3 links inherit creator's L1 emotional state at birth (reverses universe_links O5/V5)
- Decision: Trust is NEVER inherited (earned only via Cascade of Utility)
- Decision: Creating drive goes on moment nodes, not links
- Decision: Valence and ambivalence added to L3 LinkBase (11 → 13 dimensions)
- Decision: Human-created links born neutral (no fake emotions)
- Decision: Valence/ambivalence frozen at birth (not evolved by L3 physics)
- Decision: Scaled mapping via coefficients (not direct L1→L3 copy)

### Doc chain status:
- OBJECTIVES — complete (5 ranked objectives, supersedes universe_links O5/V5)
- PATTERNS — complete (5 principles, scope, dependencies, Damasio/Kahneman inspirations)
- BEHAVIORS — complete (9 behaviors, 4 edge cases, 4 anti-behaviors)
- ALGORITHM — complete (4 algorithms: EC1 emotional init, EC2 drive tagging, EC3 modulated propagation, EC4 textured synthesis, with full pseudocode and constants)
- VALIDATION — complete (10 invariants: 3 critical, 5 high, 2 medium)
- IMPLEMENTATION — complete (5 build phases, file structure, logic chains, data flows, schema extensions, configuration)
- HEALTH — complete (6 health indicators, 6 checkers, throttling strategy)
- SYNC — this file

### What needs implementation:
- Phase EC-1: Schema update (valence, ambivalence, creating_drive)
- Phase EC-2: `graph/l3_emotional_link_initializer.py`
- Phase EC-3: `runtime/l3_physics/emotionally_modulated_propagation.py`
- Phase EC-4: Synthesis grammar extension
- Phase EC-5: Wiring into moment_perception_router

---

## Open Questions

| # | Question | Status | Decision |
|---|----------|--------|----------|
| OQ1 | Direct copy vs scaled mapping? | DECIDED | Scaled via 6 coefficients (see ALGORITHM EC1) |
| OQ2 | Ambivalence dampening threshold? | DECIDED | `flow × (1 - 0.5 × ambivalence)`. At 0.8, flow is 60% |
| OQ3 | Friction → token cost coefficient? | DECIDED | `cost × (1 + 2 × friction)`. At 0.5, cost is 2x |
| OQ4 | Does valence evolve on L3? | DECIDED | Frozen at birth. Captures creation moment only |
| OQ5 | L1 synthesis — purely mathematical? | CONFIRMED | Law 10: embedding centroid + medoid + parent name concat. No LLM |
| OQ6 | Where does creating_drive live? | DECIDED | On moment node, not link (action property, not relationship property) |

---

## Dependencies

| Module | Status | What We Need |
|--------|--------|-------------|
| universe_links | DESIGNING | Base LinkBase (11 dims), needs O5/V5 deprecation |
| L1 cognition | CANONICAL | LimbicState, DriveName — available, no changes needed |
| metabolic economy | DESIGNING | Pricing formula — needs friction/ambivalence modifier |
| L1 wiring | IMPLEMENTING | Dispatcher provides L1 state per citizen — already wired |

---

## Recent Changes

### 2026-03-14: Full doc chain created

- 8 files created from templates following FRAMEWORK.md doc chain spec
- All open questions from initial design resolved
- 10 constants defined with proposed values (all env-overridable via `L3_EC_` prefix)
- 5 build phases planned across mind-protocol and mind-mcp repos
- 6 health checkers defined (all pending implementation)

---

## Handoff

**For next agent:**
- Agent subtype: **groundwork**
- Start with Phase EC-1 (schema update) — smallest blast radius, enables everything else
- Then Phase EC-2 (link initializer) — core feature, most tests
- Then Phase EC-3 (propagation modifier) — economics impact
- EC-4 and EC-5 can be parallel after EC-2

**For human:**
- Doc chain 100% complete (OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → HEALTH → SYNC)
- All 6 open questions from initial design are answered
- No blockers — implementation can start immediately
- Key files to review: ALGORITHM (formulas), VALIDATION (invariants), IMPLEMENTATION (build phases)
- Existing universe_links O5/V5 will be deprecated, not deleted — they stay as historical record with a pointer to this module
