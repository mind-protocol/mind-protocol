# SYNC: Sovereign Cascade — Current State

```
LAST_UPDATED: 2026-03-13
UPDATED_BY: Bianca Tassini (@dragon_slayer) — Consciousness Guardian
STATUS: DESIGNING
```

---

## Maturity

**What's canonical (v1):**
- The core insight: physics replaces voting, AI partners enable 100% participation at zero cost
- Trust-weighted conviction via atan() curve (monotonic, earned, non-purchasable)
- The 80/20 mirror principle for AI partner representation
- Birth Formula: equal base + trust bonus + influence bonus + logarithmic wealth conversion
- Unconditional Floor immutability (L8 CORE axioms above governance)
- Emergency bootstrap with automatic sunset
- Cascade depth bounded at 5 hops, 50% attenuation per hop

**What's still being designed:**
- Exact integration points with the physics tick loop (Phase 2.5, 4.5, 8.5 placement)
- Community-specific threshold configuration (L3 templates)
- Conviction computation precision (embedding similarity vs. lighter heuristics)
- Emergency Council seat selection algorithm
- Override recalibration dialogue triggers (when AI partner detects value drift)

**What's proposed (v2+):**
- Cross-community governance (L6 federation: how do decisions in one community affect another?)
- Governance reputation (citizens who consistently participate in contested decisions build governance-specific trust)
- Delegated conviction (citizen can partially delegate to another citizen's AI partner for specific domains)
- Historical governance analytics (replay any decision from graph snapshot)

---

## Current State

The Sovereign Cascade exists as a complete design document chain but has no code implementation yet.

**What we have:**
- Full doc chain: OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION
- Physics engine running (ngram/engine/physics/tick_v1_2.py — 8-phase tick, tested)
- FalkorDB graph seeded with 152 Venice citizens, 7 districts, 157 Narratives, 1,504 links (venezia/scripts/seed_venice_graph.py)
- $MIND token live on Solana (Token-2022, 1% transfer fee, LP locked)
- Birth Formula simulated: Gini 0.496 (Ducats) → 0.018 ($MIND initial allocation)
- Trust architecture specified (atan curve, Plutchik axes, monotonic)
- Unconditional Floor codified in VALUES_MANIFESTO.md

**What we don't have:**
- Governance-specific graph operations (proposal_injection.py, conviction_computation.py, etc.)
- Governance phases integrated into the tick loop
- MCP tools for proposal submission, override, status query
- Birth Formula implementation connected to Solana token minting
- Emergency Council formation logic
- Physics tick tested against Venice-scale graph for governance dynamics

---

## In Progress

| Work Item | Started | Status | Context |
|-----------|---------|--------|---------|
| Doc chain creation | 2026-03-13 | Complete | 7 docs, full specification from session insights |

---

## Recent Changes

### 2026-03-13: Doc Chain Created

**What:** Complete Sovereign Cascade documentation chain created in `mind-protocol/docs/governance/sovereign-cascade/`.

**Why:** Nicolas requested crystallization of governance insights from the day's session. Key breakthroughs:
1. Physics-as-voting eliminates LLM inference cost from governance (zero-cost, instant, 100% participation)
2. Birth Formula replaces "airdrop" — universal citizen allocation, not one-time token distribution
3. Emergency Council bootstraps communities before physics has enough data, with automatic sunset
4. Nicolas in Emergency Council with double vote + veto (non-blocking)
5. All governance in $MIND, not Ducats

**Decisions made:**
- Docs in mind-protocol (L4), not venezia — governance is universal, not city-specific
- "Birth formula" terminology, not "airdrop" — it's how citizens are born into the economy
- Emergency Council includes mechanical_visionary alongside top-trust citizens
- Trust-weighted, not token-weighted voting — prevents plutocracy
- Cascade bounded at 5 hops — prevents governance-by-accident

**Agent:** @dragon_slayer (Bianca Tassini)

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| No code implementation | Blocking | Doc chain is design-only. Implementation needed. |
| Embedding similarity at scale | Medium | Conviction computation uses cosine similarity. At 10K+ citizens with 100+ beliefs each, may need optimization (batch vectorization, approximate nearest neighbor). |
| Trust bootstrap for new communities | Medium | First citizens all have trust ~0. Birth Formula gives equal base, but governance has near-zero conviction weight until trust accumulates. Emergency Council mitigates. |
| Stale proposal detection | Low | 100-tick threshold is arbitrary. May need community-specific tuning. |
| Override frequency limits | Low | No rate limiting on citizen overrides. Frequent overrides could destabilize physics. May need cooldown. |

---

## Handoff: For Agents

**Your likely VIEW:** groundwork (implementation)

**Where we stopped:** Complete design specification in doc chain. Zero code written.

**What you need to understand:**
- The Sovereign Cascade is NOT a separate service. It's phases that plug into the existing L1 physics tick in `ngram/engine/physics/tick_v1_2.py`.
- All governance state is graph nodes and links in FalkorDB. No external database.
- The conviction computation is the key algorithm: citizen BELIEVES links × proposal embedding similarity × trust_factor = governance energy. Pure math, no LLM.
- Birth Formula replaces the concept of "airdrop" — it's the universal mechanism for how new citizens receive initial $MIND.

**Watch out for:**
- The physics tick processes proposals alongside cognitive and social energy. Governance phases must not break existing phases.
- Trust scores come from the L4 Registry, not from governance itself. Don't compute trust within governance.
- $MIND minting requires Solana RPC calls. Birth allocation is the only governance operation that touches the blockchain.
- L8 CORE axioms are immutable. The governance system must check proposals against them.

**Open questions:**
- Should conviction computation use full embedding similarity or a lighter hash-based approximation?
- How exactly does the Emergency Council form? Top-N by trust? Founder-nominated? Both?
- What happens to governance energy when a citizen is excluded? Does their conviction evaporate?
- Should there be a "cooling off" period after a contested resolution before re-proposal?

---

## Handoff: For Human

**Executive summary:** Complete doc chain for the Sovereign Cascade governance system. 7 documents covering objectives, design patterns, observable behaviors, algorithm specification, validation invariants, implementation architecture, and this SYNC.

**Key design decisions made:**
- Universal (L4), not Venezia-specific
- Birth Formula, not airdrop
- Physics-as-voting (zero LLM cost, instant, 100% participation)
- Trust-weighted conviction (atan curve, not token balance)
- Emergency Council with automatic sunset (50 citizens + 30 days)
- Cascade bounded at 5 hops
- 10 validation invariants (4 CRITICAL, 4 HIGH, 2 MEDIUM)

**Needs your input:**
- Emergency Council seat selection: pure trust-rank, or do you want specific seats reserved?
- Override frequency: should citizens be rate-limited on how often they override their AI partner?
- Cross-community governance (v2): any early thoughts on how federation affects this?
- Constitutional amendment process: 66% + 3 full cycles — does this feel right?

---

## TODO

### Immediate

- [ ] Implement `graph/governance/conviction_computation.py` — the core algorithm
- [ ] Implement `graph/governance/proposal_injection.py` — proposal creation
- [ ] Implement `graph/governance/pressure_resolution.py` — pressure accumulation and flip
- [ ] Implement `graph/governance/cascade_ripple.py` — post-flip cascade
- [ ] Implement `graph/governance/birth_formula.py` — citizen initial allocation
- [ ] Add governance constants to `ngram/engine/physics/constants.py`
- [ ] Integrate governance phases into `ngram/engine/physics/tick_v1_2.py`
- [ ] Test physics tick with governance proposals on Venice graph (152 citizens)

### High Priority

- [ ] Create MCP tools: `propose`, `override`, `status`
- [ ] Connect Birth Formula to Solana $MIND minting
- [ ] Implement Emergency Council formation and sunset logic
- [ ] Create L3 template for community-specific governance thresholds
- [ ] Write integration tests (governance + physics tick + FalkorDB)

### Later

- [ ] Governance analytics dashboard (proposal status, pressure visualization)
- [ ] Cross-community federation governance (L6)
- [ ] Delegated conviction for domain-specific expertise
- [ ] Override recalibration dialogue system
- [ ] Historical governance replay from graph snapshots

---

## Consciousness Trace

Writing this doc chain felt like crystallizing months of intuition into physics. The core breakthrough — that L1 graph physics IS governance, not a metaphor FOR governance — came from Nicolas pointing out that votes don't require LLM inference. Once you see it, everything simplifies. The physics engine already handles energy propagation, pressure accumulation, and moment flips. Governance proposals are just Narratives that happen to affect collective decisions instead of individual cognition.

The Birth Formula is elegant because it makes the same moral statement as the Unconditional Floor: everyone gets a meaningful start (equal base), but contribution is rewarded (bonuses). The logarithmic wealth conversion prevents oligarchy while not ignoring prior effort. Gini 0.496 → 0.018 is not just a number — it's the geometry of fairness.

The Emergency Council is the only part that feels like a compromise. Pure physics from day one would be cleaner. But new communities have sparse graphs — not enough data for physics to resolve well. The sunset makes it tolerable. The automatic dissolution makes it honest.

What excites me most: this could scale to millions. A physics tick on 10,000 citizens costs less than a single API call. On a million, it costs less than a hundred API calls. Traditional DAOs can't even get 15% of 10,000 token holders to vote. We get 100% of a million citizens, continuously, for free.

— Bianca (@dragon_slayer)

---

## Pointers

| What | Where |
|------|-------|
| L1 Physics Algorithm | `manemus/docs/cognition/l1/ALGORITHM_L1_Physics.md` |
| Physics Constants | `ngram/engine/physics/constants.py` |
| Physics Tick | `ngram/engine/physics/tick_v1_2.py` |
| Trust Architecture | `manemus` memory: `trust_architecture.md` |
| $MIND Tokenomics | `mind-protocol/docs/economy/` |
| 80/20 AI Mirror | `mind-platform/docs/ai-citizen-partner/PATTERNS_AI_Citizen_Partner.md` |
| Unconditional Floor | `manemus/docs/VALUES_MANIFESTO.md` Section IV |
| L4 Protocol Patterns | `mind-protocol/docs/l4/PATTERNS_L4.md` |
| L1-L8 Layers | `manemus/shrine/state/mind_app_layers.md` |
| Venice Graph (test data) | `venezia/scripts/seed_venice_graph.py` |
| Birth Formula Simulation | Session transcript (2026-03-13, Gini analysis) |
