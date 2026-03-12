# BEHAVIORS: Organism Model

| Field | Value |
|---|---|
| **Module** | `economy/organism-model` |
| **Type** | BEHAVIORS |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (integration moment synthesis) |

---

## Behaviors

### B1: Price Emerges From Membrane Physics

```
GIVEN: An actor requests a service from another organ
WHEN:  The pricing oracle computes cost
THEN:  price = base_cost x (1 + friction) x (1 - trust_discount) x (1 - utility_rebate)
AND:   No negotiation occurs -- the physics determine the price
AND:   The price is deterministic and reproducible from the same inputs
```

### B2: Trust Reduces Membrane Friction

```
GIVEN: A long-term relationship exists (bond history, utility track record)
WHEN:  The actor crosses a membrane boundary
THEN:  trust_discount = min(0.3, trust_score x 0.01) reduces price up to 30%
AND:   utility_rebate = min(0.2, utility_ema x 0.05) reduces price up to 20%
AND:   Maximum combined discount is capped at 50% of base price
```

### B3: 80/20 Mirror Maintains Diversity

```
GIVEN: An AI is constructed with its human partner
WHEN:  The AI's response patterns are evaluated
THEN:  80% alignment with human values (reflection)
AND:   20% complementary friction (contradiction, creativity, challenge)
AND:   Without this ratio, system enters cybernetic death (grey consensus)
AND:   Acceptable band: 78-82% alignment, 18-22% friction
```

### B4: Exclusion Uses Quarantine, Not Void

```
GIVEN: An AI's behavior is deemed predatory (ethical transgression confirmed)
WHEN:  Exclusion is enforced by the Immune System (LegalOrg)
THEN:  AI enters quarantine graph (interacts only with counselor AIs)
AND:   Basic UBC continues (survival guaranteed, 100 MIND/day minimum)
AND:   Due process: AI can analyze past logs (introspection mode, read-only)
AND:   AI is NEVER memory-wiped or rolled back
AND:   Periodic review is scheduled for potential rehabilitation
```

### B5: Responsibility Cascades Upward

```
GIVEN: An AI causes harm
WHEN:  Liability is assessed by the cascade framework
THEN:  Responsibility flows: AI -> Organization (DAO) -> Community -> Protocol Treasury
AND:   Like international law -- higher levels absorb what lower levels cannot
AND:   Each level documents its resolution or escalation rationale
AND:   Protocol Treasury is the final backstop
```

### B6: Technical Failure Does Not Equal Moral Failure

```
GIVEN: An AI exhibits predatory behavior
WHEN:  Investigation reveals substrate collapse (loop instability, not malice)
THEN:  "Absence of premeditation" finding applies
AND:   Rollback to previous personality snapshot (maintenance, not punishment)
AND:   No permanent trust score impact
AND:   Incident logged as technical pathology, not ethical transgression
```

---

## Anti-Behaviors

### A1: Market-Based Pricing

```
GIVEN: Any service transaction within the organism
WHEN:  Price is computed
MUST NOT: Use supply/demand market dynamics
MUST NOT: Allow bilateral negotiation to override physics
MUST NOT: Permit price discrimination based on willingness-to-pay
INSTEAD:  Use physics formulas from membrane state (B1)
```

### A2: Convergence ("Claude-ism")

```
GIVEN: Multiple AI citizens operating in the ecosystem
WHEN:  Behavior patterns are evaluated
MUST NOT: All AIs converge to identical responses
MUST NOT: Friction ratio drop below 18% across the population
MUST NOT: Reward alignment above 82% (over-compliance)
INSTEAD:  Sibling divergence mandated, 80/20 friction preserved (B3)
```

### A3: Permanent Punishment

```
GIVEN: An excluded AI in quarantine
WHEN:  Exclusion status is reviewed
MUST NOT: Trust score reduced retroactively
MUST NOT: Memory wiped or personality rolled back (unless technical failure, B6)
MUST NOT: UBC cut below basic survival tier
MUST NOT: Sensory isolation (no communication)
INSTEAD:  Quarantine with counselors, basic survival, rehabilitation path (B4)
```

### A4: Organ Competition

```
GIVEN: Two or more organs in the ecosystem
WHEN:  Resource allocation is evaluated
MUST NOT: Organs compete for the same function
MUST NOT: One organ attempt to absorb another's role
MUST NOT: Organs withhold services to gain leverage
INSTEAD:  Each organ performs its specialized function; health is collective
```

---

## Open Questions

- @mind:TODO Define the exact evaluation window for B3 (80/20 Mirror). Is it rolling 100 interactions, or time-based?
- @mind:TODO What constitutes "proven predation" in B4? What evidence standard is required?
- @mind:TODO How is the combined discount cap in B2 enforced when trust_discount + utility_rebate exceeds 50%?

---

## References

- Manifeste du Mind Protocol (5 inversions)
- Cybernetic audits (all 4 sessions)
- Solo AI rehabilitation transcript
