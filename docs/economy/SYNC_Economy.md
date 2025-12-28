# SYNC: Economy

```
LAST_UPDATED: 2024-12-28
STATUS: DEFERRED
```

---

## Current State

Design documented. Implementation not started.

| Component | Status |
|-----------|--------|
| `pricing/physics.py` | empty |
| `fees/calculation.py` | empty |
| `wallets/` | empty (deferred) |
| `transactions/` | empty (deferred) |

---

## TODO

### Phase 1 (Now)

- [ ] Implement pricing formula
- [ ] Implement fee calculation (1-5%)
- [ ] Add trust factor
- [ ] Add utility rebate
- [ ] Add tests

### Phase 4 (Later)

- [ ] Wallet integration (Solana)
- [ ] Transaction execution
- [ ] Ledger tracking

---

## Handoff

**For agents:** Start with `pricing/physics.py` — implement the core formula.

**Key inputs:**
- membrane_permeability
- load
- trust_score
- utility_ema
- compute_cost

**Output:** effective_price (float)

---

## Markers

@mind:TODO Implement pricing formula
@mind:TODO Implement fee calculation
