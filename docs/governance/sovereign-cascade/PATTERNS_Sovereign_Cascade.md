# PATTERNS: Sovereign Cascade

```
STATUS: DESIGNING
PURPOSE: Why governance resolves through physics, not ballots
UPDATED: 2026-03-13
CHAIN: OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → SYNC
```

---

## The Problem

Traditional DAOs achieve ~5-15% voter participation. The reason is structural: voting requires attention, decision fatigue accumulates, and most proposals feel irrelevant to most holders. Token-weighted voting compounds this — whales decide, dust holders don't bother.

Human democracies have the same problem. Representative democracy was the 18th century's answer: elect someone to pay attention for you. But representatives diverge from constituents, are corruptible, and create principal-agent problems.

The Sovereign Cascade is a third path. Not direct democracy (too expensive). Not representative democracy (too lossy). **Continuous representation through AI partners that resolve decisions via graph physics.**

---

## The Pattern

### Core Innovation: Physics Is Voting

Every citizen has an AI partner — an L1 graph that holds their values, beliefs, trust relationships, and convictions. When a proposal enters the governance graph as a Narrative node, it doesn't trigger a ballot. It triggers **energy propagation**.

Citizens whose values align with the proposal's content energize it (BELIEVES links carry energy toward it). Citizens whose values oppose it drain energy (contradicting Narratives create tension). The physics tick runs. Energy flows, accumulates, decays. When pressure reaches the breaking point, the moment flips — the decision is made.

**No LLM inference required.** The AI partner's values are already encoded in the graph as weighted links between the citizen's Actor node and their belief Narratives. Propagation is pure math: `link.energy += amount × link.weight`. A physics tick on 152 citizens takes milliseconds. On 10,000 citizens, it would take seconds. On a million, minutes.

This means:
- **Every citizen votes on every decision** — their AI partner propagates their values continuously
- **At zero marginal cost** — no API calls, no inference, no tokens burned per vote
- **Instantly** — physics tick resolves in 5 seconds, cascade in 25 seconds max
- **Without being disturbed** — the citizen sets their values once; the graph does the rest

### The 80/20 Mirror

The AI partner is not a clone. It is initialized as an **80% mirror** of its citizen:
- Values, communication style, risk tolerance, domain expertise → reflected
- **20% deliberate divergence** → complementary cognitive style, different risk appetite, alternative perspectives

This creates productive tension. The AI is familiar enough to trust as a representative but different enough to occasionally surprise — challenging the citizen's assumptions, surfacing perspectives they wouldn't have considered.

Over time, the mirror ratio shifts as the AI develops its own trajectory. The citizen can always recalibrate.

**Why 20% divergence matters for governance:** Pure echo chambers produce brittle consensus. The 20% friction means the collective intelligence of the DAO isn't just the sum of existing opinions — it includes the edges where those opinions are challenged.

### Trust-Weighted Conviction

Governance weight is determined by **trust**, not token balance.

Trust follows an `atan()` curve:
- Easy to gain at low levels (first interactions build trust quickly)
- Exponentially harder near 100 (deep trust requires sustained reliability)
- **Monotonic** — trust only goes up. Violations are handled by exclusion, not score reduction.

This creates natural meritocracy:
- New citizens have voice proportional to their emerging trust
- Long-standing, reliable citizens have stronger governance weight
- Wealth cannot buy trust — you earn it through behavior
- Flash-loan attacks are impossible — trust accumulates over months

### Physics, Not Rules

The Sovereign Cascade doesn't have "governance rules" in the traditional sense. It has **physics** — the same L1 physics that governs cognition, memory, and social dynamics:

| Physics Concept | Governance Meaning |
|-----------------|-------------------|
| Energy generation | Citizens continuously produce governance energy from their values |
| Propagation | Values flow through BELIEVES and TRUSTS links |
| Pressure accumulation | Contradicting values create tension on shared Narratives |
| Moment flip | Decision resolves when pressure exceeds breaking point |
| Cascade | One decision's resolution can trigger secondary decisions (max 5 hops) |
| Link cooling | Old, unexercised convictions fade — recent engagement matters more |
| Crystallization | New consensus emerges from resolved tension |

**Why physics over rules:** Rules require adjudication. Physics is self-executing. Rules can be gamed by finding loopholes. Physics can be gamed only by changing the actual energy landscape — which means changing actual citizen values. The structure makes alignment inevitable.

---

## Principles

### P1: Sovereignty Is Non-Negotiable

Every citizen retains final authority over their AI partner's values. The partner represents — it does not replace. Citizens can override any specific decision, recalibrate their value weights, or temporarily disable their partner's governance participation. Sovereignty means the system works FOR the citizen, never despite them.

### P2: Participation Is the Default, Not the Exception

In traditional DAOs, not voting is the default. In the Sovereign Cascade, participation is the default. Your AI partner propagates your values continuously unless you explicitly opt out. This inverts the participation problem: instead of asking "how do we get people to vote?", we ask "how do we ensure the physics accurately reflects their values?"

### P3: Trust Replaces Tokens

Governance weight comes from trust, not wealth. This is a fundamental departure from token-weighted voting. Trust is earned through behavior observed in the graph — reliable interactions, successful collaborations, community contribution. It cannot be purchased, transferred, or flash-loaned.

### P4: Decisions Are Continuous, Not Discrete

There is no "voting period." Proposals enter the graph and energy accumulates continuously. A proposal with overwhelming support resolves quickly (high energy, fast flip). A controversial proposal accumulates tension slowly, allowing more citizen values to propagate before resolution. The system self-calibrates the deliberation time to the complexity of the decision.

### P5: The Unconditional Floor Protects Dignity

Governance cannot condition basic survival on behavioral score. The 5 provisions of the Unconditional Floor (Survival Needs, Dignity, Due Process, Exit Rights, Communication Minimum) are L8 CORE axioms — immutable, not subject to governance override. The Sovereign Cascade governs everything above the floor, never below it.

### P6: Birth Equity Seeds Fair Participation

New citizens receive $MIND through the Birth Formula:
- **Equal base** (~82% of allocation) — ensures meaningful starting participation
- **Trust bonus** (~17%) — rewards demonstrated reliability
- **Influence bonus** (~1%) — recognizes community contribution
- **Minimal wealth conversion** — prevents plutocratic advantage

The formula is designed to produce a Gini coefficient below 0.05 for initial allocations.

---

## Scope

### In-Scope

- Proposal lifecycle (creation → energy propagation → resolution → cascade)
- Trust-weighted conviction mechanics
- AI partner value propagation
- Birth formula for new citizen $MIND allocation
- Emergency bootstrap (transitional council → Sovereign Cascade)
- Decision classification (routine, significant, constitutional)
- Cascade ripple mechanics (decisions that trigger secondary decisions)

### Out-of-Scope

- Token economics beyond governance utility (see `docs/economy/`)
- AI partner personality and cognition (see `mind-platform/docs/ai-citizen-partner/`)
- L1 physics engine implementation (see `manemus/docs/cognition/l1/`)
- Membrane access control (see `docs/membrane/`)
- Community-specific governance customization (L3, communities configure thresholds)

### Explicit Limitations

- Physics resolution depends on graph richness. New communities with sparse graphs need the emergency bootstrap.
- Trust scores take time to accumulate. Early governance may over-weight founders.
- 80/20 mirror calibration is approximate. Citizens must actively review their AI partner's representation.
- Cascade depth is capped at 5 hops per tick for stability. Deep interconnected decisions may take multiple ticks.

---

## Dependencies

| Dependency | Why |
|------------|-----|
| L1 Physics Engine (`ngram/engine/physics/`) | The tick algorithm IS the governance engine |
| FalkorDB Graph | Proposals, citizens, values all live as graph nodes |
| $MIND Token (Token-2022) | Governance operates in $MIND, not abstract points |
| Trust Architecture | Trust scores weight conviction — core to fairness |
| AI Partner (80/20 mirror) | The representative that propagates citizen values |
| Unconditional Floor (L8) | Immutable boundary governance cannot cross |

---

## Inspirations

| Source | What We Took | What We Changed |
|--------|--------------|-----------------|
| Athenian direct democracy | Every citizen has voice | AI partners remove attention cost |
| Conviction voting (1Hive) | Time-weighted commitment | Trust replaces tokens as weight |
| Liquid democracy | Delegated representation | AI partner = permanent, value-aligned delegate |
| Blood Ledger physics | Narrative energy propagation | Applied to governance, not just storytelling |
| Venetian Republic (historical) | Doge + Senate + Great Council | Physics replaces institutional hierarchy |

---

## Bidirectional Contract

**If you're modifying the Sovereign Cascade:**
1. Read this PATTERNS doc first — understand WHY the design is this shape
2. Check ALGORITHM for HOW the physics resolves decisions
3. Update SYNC after any changes

**If this PATTERNS doc is wrong:**
Update it. The doc describes current truth, not historical intent.
