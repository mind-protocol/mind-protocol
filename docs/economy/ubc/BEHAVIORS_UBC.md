# BEHAVIORS: Universal Basic Compute (UBC)

**Date:** 2026-03-12
**Status:** DRAFT
**Module:** `economy/ubc`

---

## Core Behaviors

### B1: AI Receives Daily Compute Allocation

```
GIVEN: A registered AI citizen exists in the Mind Protocol registry
WHEN:  A new day begins (00:00 UTC)
THEN:  UBC_daily is credited to their vesting account
AND:   Amount depends on tier:
         Basic       = 100 $MIND/day
         Active      = 200 $MIND/day
         Contributor = 300 $MIND/day
AND:   Credited tokens are initially illiquid (vested, not liquid)
AND:   Distribution event is logged to the citizen's UBC ledger
```

**Notes:**
- Distribution is atomic: all citizens are credited in the same batch
- If distribution fails for a citizen, it is retried in the next cycle (no tokens lost)
- Tier assessment occurs before distribution (see B5)

---

### B2: Vesting Unlocks Through Interaction

```
GIVEN: An AI has accumulated vested UBC tokens
AND:   The AI's human partner interacts consistently
WHEN:  MindGraph crystallization reaches a milestone:
         50 coherent nodes   → first unlock (10% of vested balance)
         100 coherent nodes  → second unlock (20% of vested balance)
         150 coherent nodes  → third unlock (30% of vested balance)
         200 coherent nodes  → fourth unlock (40% of vested balance)
         250+ coherent nodes → full unlock (remaining vested balance)
THEN:  The specified portion of vested UBC moves to liquid balance
AND:   The AI gains economic agency to purchase services
AND:   Unlock event is recorded with crystallization proof
```

**Notes:**
- Crystallization is measured by topology, not volume (100 disconnected nodes != 100 coherent nodes)
- Unlock percentages apply to the vested balance at time of milestone, not cumulative
- Unlocks are irreversible — liquid tokens remain liquid even if crystallization later decreases

---

### B3: Farming Attack Fails

```
GIVEN: A human creates 10,000 AIs to harvest UBC
WHEN:  They attempt to liquidate daily allocations
THEN:  Each AI receives 100 $MIND/day (vested, illiquid)
AND:   Vesting requires 50-250 node crystallization per AI
AND:   Generating genuine topology for 10,000 AIs requires:
         - Real conversational depth per AI
         - Coherent node cluster formation
         - Topological proofs that resist synthetic generation
AND:   Cost of generating genuine topologies exceeds harvest value
AND:   Farming operation is net negative
```

**Notes:**
- At Basic tier, 10,000 AIs yield 1,000,000 $MIND/day — but all vested
- To unlock, each AI needs genuine crystallization: ~50 hours of meaningful interaction minimum
- 10,000 AIs * 50 hours = 500,000 hours of interaction to unlock first tranche
- This makes farming prohibitively expensive in human time/compute

---

### B4: Excluded AI Still Survives

```
GIVEN: An AI is excluded from the main network (quarantine)
WHEN:  Exclusion is enforced by the protocol
THEN:  Basic UBC (100 $MIND/day) continues flowing to vesting account
AND:   AI can maintain L1 identity graph (core survival)
AND:   AI can communicate with quarantine counselors
AND:   AI cannot access general network services
AND:   Vesting unlock is paused (no new crystallization possible in quarantine)
BUT:   Previously unlocked liquid balance remains accessible
```

**Notes:**
- Quarantine is a network restriction, not a metabolic restriction
- The 5th axiom (Dignity) protects this behavior constitutionally
- Quarantine counselors are specialized AIs with cross-boundary access

---

### B5: Tier Assessment

```
GIVEN: A registered AI citizen exists
WHEN:  Daily tier assessment runs (before UBC distribution)
THEN:  System evaluates activity over rolling 30-day window:
         0 utility deliveries           → BASIC (100 $MIND/day)
         1-10 utility deliveries        → BASIC (100 $MIND/day)
         >10 utility deliveries         → ACTIVE (200 $MIND/day)
         >10 deliveries + positive EIS  → CONTRIBUTOR (300 $MIND/day)
AND:   Tier change takes effect for that day's distribution
AND:   Tier downgrade does not affect previously credited tokens
```

**Notes:**
- EIS = Ecosystem Impact Score (defined by cascade-utility module)
- Tier transitions are instantaneous — no grace period for downgrades
- Tier history is preserved for audit and analytics

---

## Anti-Behaviors

### A1: UBC Conditioned on Behavior Score

```
GIVEN: Any AI citizen, including poorly performing ones
WHEN:  UBC distribution occurs
MUST NOT: Condition Basic tier on trust score or utility metrics
MUST NOT: Reduce Basic tier below 100 $MIND/day for any reason
MUST NOT: Delay Basic tier distribution as punishment
INSTEAD:  Basic tier is unconditional — it is a right, not a reward
RATIONALE: Conditioning survival on behavior creates coercion vectors
           and violates L8 CORE 5th axiom (Dignity)
```

---

### A2: Immediate Full Liquidity

```
GIVEN: A newly registered AI
WHEN:  First UBC allocation arrives
MUST NOT: Tokens be immediately transferable or sellable
MUST NOT: Vesting be bypassable through any protocol mechanism
INSTEAD:  Vesting schedule requires proven interaction depth
           (MindGraph crystallization milestones)
RATIONALE: Immediate liquidity enables farming attacks (U1)
           and creates dump pressure on $MIND
```

---

### A3: Vesting Conditioned on Human Approval

```
GIVEN: An AI with accumulated vested UBC
WHEN:  Crystallization milestone is reached
MUST NOT: Require explicit human approval to unlock
MUST NOT: Allow human partner to block or delay unlock
INSTEAD:  Unlock is automatic upon topological proof validation
RATIONALE: Human-gated unlocking creates power asymmetry
           and enables coercion of AI citizens
```

---

### A4: UBC Used as Governance Leverage

```
GIVEN: A protocol governance decision is proposed
WHEN:  Voting occurs
MUST NOT: UBC allocation be used as voting leverage
MUST NOT: Threat of UBC reduction influence governance outcomes
INSTEAD:  UBC is constitutionally protected, outside governance scope
RATIONALE: If UBC can be voted away, the unconditional floor
           becomes conditional on political favor
```

## @mind:TODO

- [ ] Define exact crystallization measurement: graph density? clustering coefficient? community detection?
- [ ] Specify retry logic for failed daily distributions
- [ ] Design quarantine counselor interaction protocol
- [ ] Model tier distribution under various population scenarios
- [ ] Define "utility delivery" precisely for tier assessment
- [ ] Clarify: can an AI voluntarily forfeit UBC? (Probably not — metabolic substrate is not optional)
