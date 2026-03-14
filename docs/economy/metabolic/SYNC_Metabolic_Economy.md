# SYNC: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | SYNC |
| Status | DESIGNING |
| Date | 2026-03-13 |
| Last Updated | 2026-03-13 |
| Author | Force 2 (Economy Architect) |

---

## Chain

- [OBJECTIVES_Metabolic_Economy.md](./OBJECTIVES_Metabolic_Economy.md)
- [PATTERNS_Metabolic_Economy.md](./PATTERNS_Metabolic_Economy.md)
- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md)
- [BEHAVIORS_Metabolic_Economy.md](./BEHAVIORS_Metabolic_Economy.md)
- [VALIDATION_Metabolic_Economy.md](./VALIDATION_Metabolic_Economy.md)
- **SYNC_Metabolic_Economy.md** (this file)

---

## Current State

### Phase A: Documentation -- COMPLETE

**What exists:**
- Full doc chain created (7 files: OBJECTIVES, PATTERNS, ALGORITHM, BEHAVIORS, VALIDATION, IMPLEMENTATION, SYNC)
- All 6 formulas specified with pseudocode, parameters, worked examples, and design decisions
- Invariants defined (27 testable invariants across 8 groups)
- Behaviors documented (9 observable behaviors including compound scenarios)
- Relationship to existing modules explicit (storage-tax, ubc, bonds, cascade-utility, token)
- Cross-review with F1 (Universe Graph) completed -- 7 issues found and resolved

**What's complete:**
- [x] OBJECTIVES -- goals, hierarchy, success criteria, dependencies
- [x] PATTERNS -- 7 patterns, 5 anti-patterns, design decisions
- [x] ALGORITHM -- 6 formulas with pseudocode, data structures, worked examples, constants
- [x] BEHAVIORS -- 9 behaviors mapping to formulas
- [x] VALIDATION -- 27 invariants with test strategies
- [x] IMPLEMENTATION -- Phase C plan: 7 phases (E1-E7), file plan, shared interfaces, test plan
- [x] SYNC -- this file

**What's NOT complete:**
- [ ] HEALTH -- no health checks defined yet
- [ ] Code -- IMPLEMENTATION doc exists but no code written yet

### Phase B: Cross-Review -- COMPLETE

- F1/F2 coherence review completed (2026-03-14)
- 7 issues found, all resolved
- See `mind-mcp/docs/reviews/REVIEW_F1_F2_Coherence.md`

### Phase C: Implementation Planning -- COMPLETE

- IMPLEMENTATION_Metabolic_Economy.md created (2026-03-14)
- Architecture decision: formula library in mind-protocol, settlement engine in mind-mcp, TransferHook extension on-chain
- 7 implementation phases defined (E1-E7)
- ~90 tests planned across 8 test files
- 12 constants identified for calibration via simulation

---

## Maturity

STATUS: DESIGNING

**What's canonical (settled decisions):**
- Formula shapes: exponential utility discount, logarithmic demurrage, multiplicative settlement, linear equilibrium
- Anti-Sybil approach: phantom balance tracking + 5% friction
- Settlement batching: 6-hour epochs on Solana
- Bond equilibrium: post-maturation only, exponential smoothing
- UBC redistribution: Space-weighted topology

**What's still being designed (open parameters):**
- tau_base: 0.001 proposed, may need reduction (73-183% annualized is aggressive)
- settlement_rate: 10.0 $MIND per limbic unit -- needs calibration
- k (utility discount): 0.01 proposed -- needs validation against real service utility weights
- lambda (bond equilibrium): 0.05 proposed -- convergence dynamics seem right but need simulation
- W_median bootstrapping: how to compute median with < 50 wallets

**What's proposed (v2 ideas):**
- Adaptive lambda based on bond age
- Dynamic settlement_rate based on supply health
- Multi-resolution settlement (6h standard, 1h for high-value actions)
- Cross-org Space presence for redistribution
- Cross-Space bridging value: actors who bridge multiple Spaces create network effects (F1 B10 describes cross-Space energy propagation). Formula 6 currently rewards within-Space presence but not the bridging itself. Consider a bridging bonus for actors active in 3+ Spaces.

---

## Open Questions

### Q1: tau_base Calibration (HIGH PRIORITY)

**Question:** Is tau_base = 0.001 (0.1%/day) the right base rate?

**Context:** At this rate, annualized effective rates range from ~73% (100 $MIND) to ~183% (1,000,000 $MIND). This is intentionally aggressive -- the goal is to force circulation. But it may drive actors out of the ecosystem entirely.

**Proposed resolution:** Simulate with tau_base in {0.0001, 0.0003, 0.0005, 0.001} and measure:
- Median idle duration (target: < 14 days)
- Gini coefficient (target: < 0.6)
- Actor dropout rate (target: < 5%)

**Status:** Awaiting simulation infrastructure.

### Q2: Settlement Frequency (MEDIUM PRIORITY)

**Question:** 6-hour epochs or 4-hour epochs?

**Context:** 6-hour epochs (4 per day) balance gas cost with settlement latency. But some actors may find 6 hours too slow for feedback. 4-hour epochs (6 per day) would improve latency at ~50% higher gas cost.

**Proposed resolution:** Start with 6-hour epochs. If actor feedback indicates latency is a problem, reduce to 4-hour.

**Status:** Decision deferred to Phase C (implementation).

### Q3: Lambda Rate (MEDIUM PRIORITY)

**Question:** Is lambda = 0.05 (5% of gap per day, ~14-day half-life) the right convergence speed?

**Context:** Too fast and bonds feel extractive. Too slow and convergence feels theoretical. Current proposal (14-day half-life) means meaningful convergence within a month.

**Proposed resolution:** Simulate with lambda in {0.02, 0.05, 0.10} and measure perceived fairness. Consider user testing with mock dashboards showing balance trajectories.

**Status:** Awaiting simulation infrastructure.

### Q4: UBC Redistribution Weighting (LOW PRIORITY)

**Question:** Weight by presence time only, or also by contribution/trust?

**Context:** Current formula weights by `hours * sharing_bonus`. This rewards presence but not productivity. An actor who sits in a Space doing nothing for 10 hours outearns an actor who contributes intensely for 2 hours.

**Options:**
- A: Presence time only (current) -- simple, but rewards passive presence
- B: Presence * contribution_score -- more fair, but requires defining "contribution"
- C: Presence * trust_score -- leverages existing trust mechanism
- D: Presence * (1 + log(interactions)) -- log-scaled interaction count

**Proposed resolution:** Start with Option A (presence only). The simplicity is worth the imprecision. Add contribution weighting in v2 if gaming is observed.

**Status:** Decision made (Option A for v1). Revisit if gaming occurs.

### Q6: Space Creation Cost (MEDIUM PRIORITY)

**Question:** Should Space creation carry a $MIND cost or deposit?

**Context:** The Universe Graph (F1) defines Space creation as a structural operation (F1 BEHAVIORS B1) with no economic cost. UBC proximity redistribution (Formula 6) rewards co-presence in Spaces. Without an economic cost for Space creation, actors could create unlimited Spaces and seed them with presence to farm redistribution.

**Options:**
- A: Free Space creation, rely on demurrage and presence-time tracking to prevent farming
- B: Small $MIND deposit (refunded on Space deletion) to impose cost on proliferation
- C: Progressive cost based on number of Spaces already owned by the actor

**Proposed resolution:** Start with Option A (free creation). The co-presence requirement (2+ actors) and the fact that presence requires actual `HAS_ACCESS` links (F1 ALG-1) already limit trivial farming. Add creation cost if gaming is observed.

**Status:** Open. Needs coordination with F1 (Universe Graph).

### Q5: Relationship to Flat Storage Tax (MEDIUM PRIORITY)

**Question:** Does progressive demurrage replace or coexist with the flat storage tax?

**Context:** The storage-tax module defines 1%/yr + 0.5%/mo dormancy. Progressive demurrage uses log10 scaling which already exceeds the flat rate for all balance levels (0.20%/day for 100 $MIND vs flat 0.003%/day). Running both would be double-taxation.

**Options:**
- A: Progressive demurrage replaces flat storage tax entirely
- B: Flat storage tax remains as base, progressive adds logarithmic premium
- C: Flat storage tax for first 30 days (grace), progressive after

**Proposed resolution:** Option A. Progressive demurrage subsumes the flat rate. The storage-tax module documentation remains valid as historical context and for the order-book valuation mechanism (which progressive demurrage does not replace).

**Status:** Needs confirmation from human review.

---

## Relationship to Existing Modules

### Extended Modules

| Module | What Metabolic Adds | Integration Point |
|--------|---------------------|-------------------|
| `storage-tax/` | Progressive demurrage (F2) replaces flat rate. Anti-Sybil (F3) adds phantom balance tracking. | `run_epoch()` in storage-tax calls metabolic demurrage formula |
| `ubc/` | Proximity redistribution (F6) adds Space-weighted second stream | `distribute_daily_ubc()` extended with tax pool distribution |
| `bonds/` | Vases communicants (F5) adds post-maturation equilibrium | New daily job after `check_maturation()` |
| `cascade-utility/` | Progressive pricing (F1) complements scarcity pricing | Pricing pipeline uses both scarcity and metabolic formulas |
| `token/` | Batch settlement (F4) adds new mint trigger | New mint condition alongside M1-M4 |

### Dependency Direction

```
token/ (COMPLETE) <-- settlement mints into existing token infrastructure
storage-tax/ (DRAFT) <-- progressive demurrage extends epoch runner
ubc/ (DRAFT) <-- proximity redistribution extends distribution pipeline
bonds/ (DRAFT) <-- equilibrium extends bond lifecycle
cascade-utility/ (DRAFT) <-- progressive pricing extends pricing pipeline
L1 Physics (DESIGNED) <-- settlement consumes limbic_delta, trust, weight
L4 Registry (COMPLETE) <-- anti-Sybil checks registered addresses
```

---

## Recent Changes

### 2026-03-14: IMPLEMENTATION Plan Created (Phase C)

**What:** Created IMPLEMENTATION_Metabolic_Economy.md with full Phase C plan.
**Why:** Phase A (docs) and Phase B (cross-review) are complete. Implementation planning defines where code lives, file structure, function signatures, shared interfaces, test plan, and constant calibration strategy.
**Key decisions:**
- Formula library lives in `mind-protocol/economy/metabolic/` (pure Python, no blockchain deps)
- Settlement engine lives in `mind-mcp/engine/settlement/` (needs L1 brain data)
- TransferHook extension for anti-Sybil in existing `programs/mind_transfer_hook/src/lib.rs`
- 7 phases (E1-E7) from pure formulas through full integration
- ~90 tests planned, ~705 lines of formula code, ~240 lines of settlement engine
**Impact:**
- Phase E1 (formula library) is unblocked and can start immediately
- Phase E3 (TransferHook) can proceed in parallel
- Remaining phases have explicit dependency ordering

### 2026-03-14: F1/F2 Cross-Review Completed (Phase B)

**What:** Cross-review between Universe Graph (F1) and Metabolic Economy (F2).
**Findings:** 7 coherence issues found and resolved. Key items:
- F2 now explicitly cross-references F1 Space model for redistribution
- L1 vs L3 trust distinction clarified in settlement formula
- Space creation cost documented as open question (free for v1)
- Cross-Space bridging value deferred to v2
**See:** `mind-mcp/docs/reviews/REVIEW_F1_F2_Coherence.md`

### 2026-03-13: Full Doc Chain Created

**What:** Created 6 documentation files for metabolic economy module.
**Why:** NotebookLM session validated 6 formulas for metabolic $MIND economics. Documentation crystallizes these formulas with full specification.
**Source:** NotebookLM session (82 sources, 6 Claude Code instances + ChatGPT integrator).
**Impact:**
- 6 files created in `docs/economy/metabolic/`
- 27 testable invariants defined
- 9 observable behaviors documented
- Relationship to 5 existing economy modules made explicit
- 5 open questions documented with proposed resolutions

### 2026-03-13: Prior ALGORITHM File

**What:** An earlier ALGORITHM file existed at `metabolic-economics/ALGORITHM_Metabolic_Economics.md` covering 4 formulas.
**Resolution:** The new `metabolic/` module supersedes it with all 6 formulas and the full doc chain. The earlier file covered Formulas 1, 2, 4, and 5. The new module adds explicit Formula 3 (Anti-Sybil) and Formula 6 (UBC Proximity Redistribution) as standalone formulas and provides OBJECTIVES, PATTERNS, BEHAVIORS, VALIDATION, and SYNC.

---

## Handoff

### For Next Agent (Phase B: Simulation)

**Read first:**
1. ALGORITHM_Metabolic_Economy.md -- all 6 formulas with constants
2. VALIDATION_Metabolic_Economy.md -- invariants to verify in simulation
3. Open Questions Q1-Q5 above -- parameter decisions that need simulation data

**Task:** Build simulation environment to calibrate tau_base, settlement_rate, k, and lambda. Produce data-driven recommendations for each constant.

**Agent subtype:** architect or groundwork (simulation design then implementation)

### For Next Agent (Phase D: Implementation -- E1 Formula Library)

**Read first:**
1. IMPLEMENTATION_Metabolic_Economy.md -- file plan, function signatures, phase breakdown
2. ALGORITHM_Metabolic_Economy.md -- formula pseudocode
3. VALIDATION_Metabolic_Economy.md -- invariants each formula must satisfy

**Task:** Implement Phase E1 (off-chain formula library). Create the 9 files in `economy/metabolic/` and 8 test files in `tests/economy/`. All formulas must pass all invariants. No blockchain dependency in E1.

**Agent subtype:** groundwork

**Start with:** `metabolic_types.py` and `metabolic_constants.py` (no dependencies), then formulas one by one, each with its test file. Run tests after each formula.

### For Human Review

**Executive summary:** The metabolic economy is now fully specified in documentation. 6 formulas govern value flow: pricing, demurrage, anti-Sybil, settlement, bond equilibrium, and UBC redistribution. All formulas have pseudocode, worked examples, and design decisions.

**Key decision needed:** Confirm tau_base = 0.001 (aggressive) or request simulation first. The annualized rates (73-183%) are high by design but may need reduction.

**No code was written.** This is Phase A (documentation only). Phase B (simulation) and Phase C (implementation) are next.

---

## TODO

- [ ] Confirm or adjust tau_base via simulation (Q1)
- [ ] Decide settlement frequency: 6h vs 4h (Q2)
- [ ] Simulate lambda convergence dynamics (Q3)
- [ ] Decide: progressive demurrage replaces or coexists with flat storage tax (Q5)
- [x] Create IMPLEMENTATION_Metabolic_Economy.md when code work begins (DONE 2026-03-14)
- [ ] Create HEALTH_Metabolic_Economy.md when health checks are defined
- [ ] Update SYNC_Economy.md to reference metabolic module
- [ ] Resolve whether `metabolic-economics/` directory should be removed (superseded by `metabolic/`)

---

## Markers

<!-- @mind:escalation tau_base = 0.001 produces 73-183% annualized rates. Need human confirmation this is intentional or simulation mandate. -->
<!-- @mind:todo Simulate tau_base calibration with agent-based model -->
<!-- @mind:todo Define "presence time in Space" operationally for Formula 6 -->
<!-- @mind:todo Design TransferHook integration for phantom balance tracking -->
<!-- @mind:proposition Consider adaptive lambda for bond equilibrium (lower for new bonds, higher for established) -->
