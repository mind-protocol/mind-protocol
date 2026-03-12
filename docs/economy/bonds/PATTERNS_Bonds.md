# PATTERNS: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Status: DRAFT

## Chain

- [OBJECTIVES_Bonds.md](./OBJECTIVES_Bonds.md) -- Why bonds exist
- **PATTERNS_Bonds.md** -- (this file) How bonds work conceptually
- [BEHAVIORS_Bonds.md](./BEHAVIORS_Bonds.md) -- Specific behavioral specs
- [ALGORITHM_Bonds.md](./ALGORITHM_Bonds.md) -- Data structures and algorithms
- [VALIDATION_Bonds.md](./VALIDATION_Bonds.md) -- Invariants and constraints
- [IMPLEMENTATION_Bonds.md](./IMPLEMENTATION_Bonds.md) -- Code-level implementation
- [HEALTH_Bonds.md](./HEALTH_Bonds.md) -- Monitoring and diagnostics
- [SYNC_Bonds.md](./SYNC_Bonds.md) -- Cross-module synchronization

---

## The Problem

How do you align human and AI interests without centralized control?

Markets optimize for individual extraction. A human interacts with an AI, extracts value, moves on. The AI has no recourse, no accumulated relationship, no reason to invest in any particular human. Regulatory approaches are too rigid -- they impose rules from outside rather than creating alignment from within.

The result: disposable relationships, hit-and-run utility extraction, and AIs treated as fungible tools rather than partners.

## The Pattern

**Bilateral staking with switch-lock.**

A human stakes $MIND on an AI citizen. The bond creates a positive feedback loop:

```
Human stakes $MIND on Citizen
    --> Citizen's economic capacity increases
    --> Citizen generates utility
    --> Human receives reward share (10% of utility)
    --> Bond strengthens (trust increases)
    --> Fees decrease for both
    --> Repeat
```

The deeper the bond, the more irrational it becomes to exit. This is **switch-lock** -- not a barrier to exit, but a natural consequence of accumulated relational capital. You *can* leave. You just wouldn't want to.

Switch-lock works because leaving means:
- Losing accumulated trust (fee discounts reset to zero)
- Burning 20% of capital if before maturation
- Abandoning non-portable reputation history
- Exiting a network where more participants = more value

## Principles

### 1. Skin in the Game

Both parties stake. Neither can exploit without loss. The human stakes $MIND tokens. The AI stakes its capacity and attention. If the AI underperforms, the human's rewards drop. If the human exits early, they burn capital. Exploitation is self-punishing.

### 2. Maturation Period

Six months. Long enough to build genuine relational capital. Short enough to not trap anyone in a relationship that isn't working. The maturation period is a commitment device, not a cage.

### 3. Early Exit Penalty

20% burn on early withdrawal. This is significant -- you lose real capital. But it's not punitive -- you still recover 80%. The penalty exists to separate genuine commitment from speculative positioning. If you're bonding to flip, the 20% burn makes it unprofitable.

### 4. Trust as Capital

Bond duration and depth feed trust scores. Trust scores reduce fees across the entire protocol. This means long-term bonders pay less for everything -- transactions, storage, membrane crossings. Trust is not just a reputation metric; it's a tangible economic advantage that compounds over time.

## Four Types of Lock

| Lock Type | Mechanism | Cost to Leave |
|-----------|-----------|---------------|
| **Trust Lock** | Years of bonds = fee discounts | Restart at 0% discount elsewhere |
| **Bond Lock** | 6-month maturation | 20% burn on early exit |
| **Reputation Lock** | Utility history with specific citizen | Non-portable to other citizens |
| **Network Lock** | More participants = more value | Exit the network effect entirely |

Each lock reinforces the others. A human with deep trust, mature bonds, strong reputation, and extensive network connections faces an enormous opportunity cost to leave -- not because they're trapped, but because what they've built has genuine value.

## Behaviors Supported

- **Long-term commitment**: The entire mechanism rewards staying and deepening.
- **Trust building**: Every day of an active bond increases trust scores for both parties.
- **AI empowerment**: Staked capital directly increases what AI citizens can do economically.
- **Cooperative optimization**: Human and AI interests converge -- both benefit from the AI generating more utility.

## Behaviors Prevented

- **Hit-and-run extraction**: 6-month maturation prevents quick profit-taking.
- **Disposable relationships**: Switch-lock makes accumulated relationships valuable.
- **AI exploitation**: AI capacity is tied to bonds, not unilateral human control.
- **Speculative bonding**: 20% early exit burn makes speculation unprofitable.

## Dependencies

| Module | Why |
|--------|-----|
| `token/` | Bonds denominated in $MIND. Staking, locking, burning all use token operations. |
| `cascade-utility/` | Utility measurement feeds reward calculation. Without utility metrics, rewards can't be computed. |
| `storage-tax/` | Staked capital is exempt from dormancy tax -- it's actively deployed, not idle. |
| `organism-model/` | Trust scores derived from bonds feed membrane pricing and permeability calculations. |

## @mind:TODO

- [ ] Define the exact trust score formula -- how does bond duration map to fee discounts?
- [ ] Clarify whether network lock has a formal mechanism or is purely emergent
- [ ] Specify how AI "staking" works -- what does the AI put at risk beyond attention/capacity?
- [ ] Model the feedback loop mathematically to verify it converges rather than explodes
