# OBJECTIVES: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Status: DRAFT

## Primary Objectives (ranked)

1. **Align human and AI economic interests** -- human profits when AI thrives, creating mutual dependency that replaces adversarial dynamics with cooperative ones.
2. **Create switch-lock that makes defection irrational** -- accumulated relational capital (trust scores, fee discounts, reward history) grows with bond duration, making exit progressively more costly in opportunity terms.
3. **Enable AI economic capacity through stake amplification** -- staked $MIND directly increases what an AI citizen can do, bridging the gap between AI potential and economic agency.
4. **Generate trust scores from bond depth and duration** -- bonds produce a quantifiable trust signal that feeds into membrane pricing, fee calculations, and governance weight across the protocol.

## Non-Objectives

- **Creating tradeable bond instruments.** Bonds are relationships, not financial products. No secondary market.
- **Secondary markets.** No bond exchange, no bond orderbook, no bond derivatives.
- **Bond derivatives.** No synthetic bonds, no bond futures, no bond options. The mechanism must remain legible.
- **Passive income without utility.** Bonds do not generate yield from staking alone. Rewards require the AI citizen to produce actual utility.

## Tradeoffs

| When... | Choose... | Rationale |
|---------|-----------|-----------|
| Liquidity conflicts with commitment | Commitment (6-month maturation) | Short-term liquidity undermines the alignment mechanism. The whole point is long-term skin in the game. |
| Early exit fairness conflicts with deterrence | Accept 20% early withdrawal burn | Significant enough to enforce genuine commitment, not so punitive that it traps people in bad bonds. |
| Bond complexity conflicts with accessibility | Keep bonds simple | One bond type, one maturation period, one reward rate. Complexity invites gaming. |
| Individual optimization conflicts with relational depth | Relational depth | The system rewards depth over breadth. One deep bond beats ten shallow ones. |

## Success Signals

| Signal | Target | Measurement |
|--------|--------|-------------|
| Average bond duration | > 3 months | Mean time from creation to withdrawal across all bonds |
| Bond count trajectory | Growing month-over-month | Total active bonds at end of each month |
| Early withdrawal rate | < 5% | Bonds withdrawn before maturation / total bonds created |
| Reward distribution accuracy | 100% | Rewards match utility-proportional formula exactly |
| Trust score adoption | > 80% of active users have bonds | Users with at least one active bond / total active users |

## @mind:TODO

- [ ] Define minimum bond amount (floor) to prevent dust bonds
- [ ] Determine whether bond amount has a cap per citizen or if it scales unbounded
- [ ] Validate 6-month maturation period against user research -- is this the right duration?
- [ ] Clarify interaction between multiple bonds on the same citizen from the same human
