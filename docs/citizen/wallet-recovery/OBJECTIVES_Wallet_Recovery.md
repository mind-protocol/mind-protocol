# OBJECTIVES — Wallet Recovery

```
STATUS: STABLE
CREATED: 2026-03-14
```

## PRIMARY OBJECTIVES (ranked)
1. **Citizen never permanently loses funds** — Key loss is an operational incident, not a financial catastrophe. $MIND is not for accumulation; recovery must be fast and simple.
2. **Identity verification is the only gate** — The citizen proves who they are. That's it. No complex escrow, no multi-sig ceremony, no waiting period beyond verification.
3. **Sovereignty preserved** — The citizen controls their new wallet. The protocol facilitates transfer, not custody.

## NON-OBJECTIVES
- Complex key backup or rotation infrastructure
- Multi-sig recovery schemes
- Hardware wallet integration (v2+)
- Preventing key loss (that's operational, not protocol)

## TRADEOFFS (canonical decisions)
- When speed conflicts with ceremony, choose speed. $MIND isn't meant to be hoarded.
- We accept the risk of a compromised identity hash in exchange for a simple, fast recovery flow. If identity itself is compromised, that's a separate, larger problem (citizen deregistration territory).

## SUCCESS SIGNALS (observable)
- A citizen who loses their key recovers funds within minutes, not days
- Zero manual intervention from protocol operators for standard recoveries
- No funds permanently lost due to key loss
