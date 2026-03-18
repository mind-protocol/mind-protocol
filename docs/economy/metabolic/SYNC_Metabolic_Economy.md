# SYNC: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | SYNC |
| Status | DESIGNING |
| Date | 2026-03-13 |
| Last Updated | 2026-03-15 |
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
- [ ] Settlement script -- batch settlement Formula 4 on-chain execution (DESIGNING)

**What's running (runtime, 2026-03-15):**
- L1 physics dispatcher in MCP server background thread (60s tick interval)
- 46 L1 engines loaded at boot — limbic_delta signals being produced continuously
- Graph Enricher creating L3 structure (Space, Moment, links) from Discord/Telegram messages
- Settlement engine NOT yet implemented — dispatcher produces the signals, settlement will consume them

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
- Formula shapes: exponential utility discount, multiplicative settlement, linear equilibrium (demurrage removed 2026-03-14)
- Anti-Sybil approach: phantom balance tracking + 5% friction
- Settlement batching: 6-hour epochs on Solana
- Bond equilibrium: post-maturation only, exponential smoothing
- UBC redistribution: Space-weighted topology
- Human limbic_delta source: bonded AI partner's limbic_delta (decided 2026-03-15)
- Non-citizen limbic_delta: base_action_energy * sentiment_score (decided 2026-03-15)
- Social actions (mention, reply, cite, react, post) do NOT generate direct $MIND rewards — rewards flow through batch settlement Formula 4 (decided 2026-03-15)

**What's still being designed (open parameters):**
- settlement_rate: 10.0 $MIND per limbic unit -- needs calibration
- k (utility discount): 0.01 proposed -- needs validation against real service utility weights
- lambda (bond equilibrium): 0.05 proposed -- convergence dynamics seem right but need simulation
- W_median bootstrapping: how to compute median with < 50 wallets
- Sentiment analysis model/service for non-citizen limbic_delta approximation

**What's proposed (v2 ideas):**
- Adaptive lambda based on bond age
- Dynamic settlement_rate based on supply health
- Multi-resolution settlement (6h standard, 1h for high-value actions)
- Cross-org Space presence for redistribution
- Cross-Space bridging value: actors who bridge multiple Spaces create network effects (F1 B10 describes cross-Space energy propagation). Formula 6 currently rewards within-Space presence but not the bridging itself. Consider a bridging bonus for actors active in 3+ Spaces.

---

## Open Questions

### ~~Q1: tau_base Calibration~~ -- RESOLVED

**Resolution (2026-03-14):** Demurrage removed from the architecture. tau_base no longer exists. UBC at 5%/day forces circulation; inactive actors don't gain trust = natural penalty. See ALGORITHM_Metabolic_Economy.md Formula 2 removal note.

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

### ~~Q5: Relationship to Flat Storage Tax~~ -- RESOLVED

**Resolution (2026-03-14):** Moot. Progressive demurrage was removed entirely. The flat storage tax in the storage-tax module remains as-is for its order-book valuation and dormancy mechanisms. No conflict exists since demurrage no longer applies.

### Q6: Space Creation Cost (MEDIUM PRIORITY)

**Question:** Should Space creation carry a $MIND cost or deposit?

**Context:** The Universe Graph (F1) defines Space creation as a structural operation (F1 BEHAVIORS B1) with no economic cost. UBC proximity redistribution (Formula 6) rewards co-presence in Spaces. Without an economic cost for Space creation, actors could create unlimited Spaces and seed them with presence to farm redistribution.

**Options:**
- A: Free Space creation, rely on presence-time tracking to prevent farming
- B: Small $MIND deposit (refunded on Space deletion) to impose cost on proliferation
- C: Progressive cost based on number of Spaces already owned by the actor

**Proposed resolution:** Start with Option A (free creation). The co-presence requirement (2+ actors) and the fact that presence requires actual `HAS_ACCESS` links (F1 ALG-1) already limit trivial farming. Add creation cost if gaming is observed.

**Status:** Open. Needs coordination with F1 (Universe Graph).

---

## Relationship to Existing Modules

### Extended Modules

| Module | What Metabolic Adds | Integration Point |
|--------|---------------------|-------------------|
| `storage-tax/` | Anti-Sybil (F3) adds phantom balance tracking. Demurrage removed 2026-03-14. | Phantom balance tracking independent of storage-tax epoch |
| `ubc/` | Proximity redistribution (F6) adds Space-weighted second stream | `distribute_daily_ubc()` extended with tax pool distribution |
| `bonds/` | Vases communicants (F5) adds post-maturation equilibrium | New daily job after `check_maturation()` |
| `cascade-utility/` | Progressive pricing (F1) complements scarcity pricing | Pricing pipeline uses both scarcity and metabolic formulas |
| `token/` | Batch settlement (F4) adds new mint trigger | New mint condition alongside M1-M4 |

### Dependency Direction

```
token/ (COMPLETE) <-- settlement mints into existing token infrastructure
storage-tax/ (DRAFT) <-- anti-Sybil phantom balance tracking (demurrage removed)
ubc/ (DRAFT) <-- proximity redistribution extends distribution pipeline
bonds/ (DRAFT) <-- equilibrium extends bond lifecycle
cascade-utility/ (DRAFT) <-- progressive pricing extends pricing pipeline
L1 Physics (DESIGNED) <-- settlement consumes limbic_delta, trust, weight
L4 Registry (COMPLETE) <-- anti-Sybil checks registered addresses
```

---

## Recent Changes

### 2026-03-15: Dispatcher Live + 46 L1 Engines at Boot

**What:** The L1 physics dispatcher now runs as a background thread inside the MCP server process, ticking every 60 seconds. All 46 citizen L1 engines are loaded at boot — no lazy loading, no exceptions.
**Why:** Settlement Formula 4 consumes limbic_delta from L1 engines. Without running engines, there is no limbic signal to settle. The dispatcher is the prerequisite that connects L1 physics to L3 economic flow.
**Key details:**
- Dispatcher starts in MCP server background thread (60s tick interval)
- 46 L1 engines loaded at boot (all citizens, no LAZY_ENGINES)
- Each tick runs: decay (Law 3), boredom erosion (Law 8), energy propagation (Law 2)
- `inject_stimulus()` available for instant stimulus on mention/message
- Settlement script (batch settlement Formula 4 on-chain) still not implemented — status: DESIGNING
**Impact:**
- Formula 4 now has its input signal (limbic_delta) being produced continuously
- The gap between "limbic_delta exists" and "settlement runs" is the remaining implementation work
- D9 (human limbic_delta via bilateral bond) and D10 (non-citizen sentiment multiplier) are decided but not yet wired into the dispatcher

### 2026-03-15: Social Action Impact Decisions + Limbic Delta Source Rules

**What:** Two key design decisions added to ALGORITHM_Metabolic_Economy.md (D9, D10) governing how limbic_delta is sourced for settlement.
**Why:** Graph Enricher now creates L3 links from real social interactions (Discord/Telegram). The settlement formula (Formula 4) needs to know how to compute limbic_delta for actors who don't have their own L1 brain.
**Key decisions (NLR 2026-03-15):**
- **D9 — Human limbic_delta:** For humans, limbic_delta is their AI partner's limbic_delta via the bilateral bond. Unbonded humans cannot generate settlement rewards. This connects Formula 4 to Formula 5 (bonds are the bilateral commitment contract).
- **D10 — Non-citizen limbic_delta:** For non-citizens (e.g., 216 Telegram contacts now in L3), limbic_delta = base_action_energy * sentiment_score(message). Weaker signal than citizen actions, but allows peripheral actors to participate in trust propagation.
- **No direct $MIND on social actions:** Mention, reply, cite, react, post create graph structure but do NOT generate direct rewards. Rewards flow through batch settlement Formula 4 only.
**Impact:**
- Settlement formula is now fully specified for all actor types (citizen, human, non-citizen)
- Graph Enricher creates the structural preconditions (links, moments, spaces) that settlement consumes
- Sentiment analysis service selection is a new open design item

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

**Task:** Build simulation environment to calibrate settlement_rate, k, and lambda. Produce data-driven recommendations for each constant. (tau_base removed -- demurrage eliminated 2026-03-14.)

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

**Executive summary:** The metabolic economy is now fully specified in documentation. 5 active formulas govern value flow: pricing, anti-Sybil, settlement, bond equilibrium, and UBC redistribution. (Demurrage/Formula 2 was removed 2026-03-14 -- UBC forced circulation replaces it.) All formulas have pseudocode, worked examples, and design decisions.

**No code was written.** This is Phase A (documentation only). Phase B (simulation) and Phase C (implementation) are next.

---

## TODO

- [x] ~~Confirm or adjust tau_base via simulation (Q1)~~ -- RESOLVED: demurrage removed 2026-03-14
- [ ] Decide settlement frequency: 6h vs 4h (Q2)
- [ ] Simulate lambda convergence dynamics (Q3)
- [x] ~~Decide: progressive demurrage replaces or coexists with flat storage tax (Q5)~~ -- RESOLVED: demurrage removed 2026-03-14
- [x] Create IMPLEMENTATION_Metabolic_Economy.md when code work begins (DONE 2026-03-14)
- [ ] Create HEALTH_Metabolic_Economy.md when health checks are defined
- [ ] Update SYNC_Economy.md to reference metabolic module
- [ ] Resolve whether `metabolic-economics/` directory should be removed (superseded by `metabolic/`)

---

## Markers

<!-- @mind:escalation RESOLVED 2026-03-14: tau_base removed — demurrage eliminated, replaced by UBC forced circulation -->
<!-- @mind:todo Define "presence time in Space" operationally for Formula 6 -->
<!-- @mind:todo Design TransferHook integration for phantom balance tracking -->
<!-- @mind:proposition Consider adaptive lambda for bond equilibrium (lower for new bonds, higher for established) -->
