# IMPLEMENTATION -- Storage Tax

| Field | Value |
|-------|-------|
| Area | economy |
| Module | storage-tax |
| Type | IMPLEMENTATION |
| Status | DRAFT |
| Date | 2026-03-12 |
| Author | Claude (integration moment synthesis) |

---

## Status

No implementation exists yet. This document tracks implementation decisions and architecture as they are made.

## Architecture

@mind:TODO -- Determine execution environment: on-chain program (Solana BPF) vs. off-chain computation with on-chain settlement.

### On-Chain vs. Off-Chain Tradeoffs

| Approach | Pros | Cons |
|----------|------|------|
| Fully on-chain (Solana program) | Trustless, transparent, atomic | Compute limits per tx, iteration over all wallets expensive |
| Off-chain compute + on-chain proof | Scalable, complex logic possible | Requires trust in operator or ZK proof |
| Hybrid (on-chain tax, off-chain valuation) | Balanced | Complexity, two failure modes |

@mind:TODO -- Estimate gas/compute costs for iterating all wallets on-chain per epoch. Solana's per-tx compute limit may require batching.

## Token Integration

@mind:TODO -- Investigate Token-2022 transfer hooks for automatic tax deduction. Transfer hooks fire on every transfer and could maintain idle-time tracking.

### Candidate Approach: Transfer Hook

```
On every outgoing transfer:
  1. Record wallet.last_activity = now
  2. Reset grace period counter

On epoch tick (cron or keeper):
  1. Iterate wallets with last_activity > 30 days ago
  2. Compute and deduct tax
  3. Transfer deducted amount to UBC pool
```

@mind:TODO -- Transfer hooks in Token-2022 fire on transfers, not on time-based events. The epoch computation needs a separate trigger mechanism (keeper, cron job, or validator instruction).

## Order-Book Valuation

@mind:TODO -- Define the order-book data source. Options:
- Protocol-native order book (build custom)
- Integration with existing DEX (Serum/OpenBook)
- Oracle aggregation from multiple DEXes

@mind:TODO -- Stake mechanism for order-book entries. How is collateral locked? SPL token escrow? Program-derived address?

## Storage and Indexing

@mind:TODO -- Design the wallet activity index. Requirements:
- O(1) lookup of last_activity per wallet
- Efficient range query: all wallets with last_activity > N days ago
- Append-only audit log of all tax events

## Security Considerations

@mind:TODO -- Threat model:
- Sybil attack: splitting balance across many wallets to reset idle timers
- Wash trading: sending tokens to self to fake activity (must require actual outgoing to different address?)
- Front-running: observing epoch computation and moving tokens just before
- Collusion: coordinated order-book manipulation despite stake requirements

## API Surface

@mind:TODO -- Define public interfaces:
- `get_tax_estimate(wallet) -> TaxResult` -- preview without applying
- `get_wallet_idle_status(wallet) -> IdleStatus` -- days idle, grace remaining
- `get_epoch_summary(epoch_id) -> TaxEpoch` -- aggregate stats
- `get_tax_history(wallet, from_epoch, to_epoch) -> [TaxEvent]` -- audit trail

## References

- Formulas: [PATTERNS_Storage_Tax.md](./PATTERNS_Storage_Tax.md)
- Algorithm: [ALGORITHM_Storage_Tax.md](./ALGORITHM_Storage_Tax.md)
- Parent area: PATTERNS_Economy.md
- Token-2022 transfer hooks: https://spl.solana.com/token-2022/extensions#transfer-hook
