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

---

### B6: Settlement Flows Through Trust Links

```
GIVEN: Agent i has surplus energy (E_i > Θ_i)
AND:   Agent i has trust links to neighbors j₁, j₂, ..., jₙ
WHEN:  Batch settlement runs
THEN:  Surplus_i = max(0, E_i - Θ_i) is distributed to neighbors
AND:   Each neighbor j receives proportional to affinity F_ij:
         F_ij = weight_ij × gain_ij × (1 - friction_ij) × Compatibility(i, link, j)
AND:   Higher trust → lower friction → more surplus propagated
AND:   Personhood Ladder mastery acts as multiplier on gain_ij
```

**Notes:**
- Trust gradient is monotone (Stranger → Low → Medium → High → Owner)
- High/Owner trust requires T1 (Foundation Mastery) — no shortcuts
- Compatibility uses Sim_lex at 0.5 weight to prevent false positive financial flows

---

### B7: Topological Activity Triggers Redistribution

```
GIVEN: A space has ≥3 active actors
AND:   An actor creates moment nodes in that space (messages, actions, contributions)
WHEN:  Daily redistribution runs
THEN:  Actor's activity score = log10(1 + Σ(weight of their moments in that space))
AND:   Multiplied by community density: score × (actors_in_space - 1)
AND:   Actor receives their proportion of the transfer fee pool
AND:   Actors who created 0 moments or only 0-weight moments receive 0%
```

**Notes:**
- Weight is earned via Law 6 (Consolidation) — only genuinely useful moments gain weight
- Logarithmic envelope prevents hyperactive actors from dominating
- Same formula applies to physical spaces (GPS), Telegram chats, GitHub repos
- Eligible spaces require ≥3 actors (minimum community threshold)

### B7b: Presence Without Action = Zero

```
GIVEN: An actor has 15 browser tabs open in various spaces
AND:   The actor creates 0 moment nodes (no messages, no interactions)
WHEN:  Daily redistribution runs
THEN:  Σ(weight of moments) = 0
AND:   log10(1 + 0) = 0
AND:   Share = 0%
AND:   Actor receives nothing from the redistribution pool
```

**Notes:**
- This is the anti-farming mechanism for Formula 6
- Hours present is NEVER counted — only topological proof matters
- Identical to how Law 7 (Oubli) dissolves inactive nodes

---

### B8: Energy Conservation Holds

```
GIVEN: The protocol operates with a global budget B
WHEN:  Any energy injection occurs (Law 1)
THEN:  Total injected energy across all nodes ≤ B
AND:   max_share per node = clamp(1/√N_targeted, 0.01, 0.5)
AND:   This holds whether N = 100 or N = 100,000
```

---

### B9: Natural Decay Prevents Inflation

```
GIVEN: Any node with energy E > 0
WHEN:  A tick passes without reinforcing activity
THEN:  Energy decays by DECAY_RATE (0.02) per tick
AND:   Only real activity maintains influence
AND:   Dormant capital naturally returns to the pool
```

---

## Anti-Behaviors (continued)

### A5: Settlement Bypasses Trust

```
GIVEN: Any settlement operation
MUST NOT: Route funds to agents without trust links
MUST NOT: Allow settlement at Stranger level without full friction cost
MUST NOT: Bypass Personhood Ladder requirements for High/Owner trust
INSTEAD:  Trust gradient modulates all settlement flows
RATIONALE: Structurally making cooperation profitable requires
           that trust reduces cost — bypassing this breaks the incentive
```

### A6: Magic Number Constraints

```
GIVEN: Any economic constraint in the system
MUST NOT: Use absolute caps (e.g., "max 10 tokens per node")
MUST NOT: Use hardcoded limits that fail at different scales
INSTEAD:  max_share = clamp(1/√N_targeted, 0.01, 0.5)
RATIONALE: I2 invariant — topology agnostic, scales from 100 to 100k nodes
```
