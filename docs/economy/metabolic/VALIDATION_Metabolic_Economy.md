# VALIDATION: Metabolic Economy

| Field | Value |
|-------|-------|
| Area | economy |
| Module | metabolic |
| Type | VALIDATION |
| Status | DESIGNING |
| Date | 2026-03-13 |
| Author | Force 2 (Economy Architect) |

---

## Chain

- [OBJECTIVES_Metabolic_Economy.md](./OBJECTIVES_Metabolic_Economy.md)
- [PATTERNS_Metabolic_Economy.md](./PATTERNS_Metabolic_Economy.md)
- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md)
- [BEHAVIORS_Metabolic_Economy.md](./BEHAVIORS_Metabolic_Economy.md)
- **VALIDATION_Metabolic_Economy.md** (this file)
- [SYNC_Metabolic_Economy.md](./SYNC_Metabolic_Economy.md)

---

## Overview

Invariants that must hold for the metabolic economy to function correctly. Organized by formula, then cross-cutting invariants. Each invariant is testable -- either in unit tests, simulation, or on-chain verification.

---

## I. Supply Conservation Invariants

### INV-SC1: Total Supply Accounting

```
FOR EVERY epoch:
  total_supply_before
  + total_minted_settlement     (Formula 4 rewards)
  + total_minted_ubc            (UBC module flat distribution)
  - total_burned_demurrage      (Formula 2 tax -- burned portion, if any)
  - total_burned_friction       (Formula 3 repatriation friction)
  - total_burned_other          (B1-B5 burns from token module)
  = total_supply_after

  ASSERT total_supply_after == calculated_value
  ASSERT abs(total_supply_after - total_supply_before - net_change) < EPSILON
  WHERE EPSILON = 1e-6 $MIND (floating point tolerance)
```

**Why:** If supply accounting diverges, the system is minting or destroying tokens invisibly. This is the most critical invariant.

**Test:** After every epoch, run a full reconciliation of all wallets + treasury + pools vs. expected supply.

### INV-SC2: Demurrage Tax Pool Conservation

```
FOR EVERY daily epoch:
  tax_collected = sum(demurrage_deductions from all wallets)
  ubc_pool_increase = ubc_pool.balance_after - ubc_pool.balance_before

  ASSERT tax_collected == ubc_pool_increase
  # Every $MIND deducted in demurrage must appear in the UBC pool
  # No $MIND disappears or appears during the tax collection phase
```

**Why:** Demurrage is a transfer mechanism (wallet -> pool), not a burn. If the pool doesn't receive exactly what was deducted, tokens are being lost or created.

### INV-SC3: UBC Redistribution Conservation

```
FOR EVERY redistribution cycle:
  pool_before = ubc_pool.balance
  total_distributed = sum(amount for each ActorShare)
  pool_after = ubc_pool.balance

  ASSERT total_distributed == pool_before - pool_after
  ASSERT pool_after >= 0
  # Distribution can never exceed pool balance
  # Pool can never go negative
```

**Why:** Redistribution must be a zero-sum operation within the pool boundary.

---

## II. Pricing Invariants (Formula 1)

### INV-P1: Price Non-Negativity

```
FOR ALL (C_base, U_S, W_i, W_median):
  P(i, S) = C_base * e^(-k * U_S) * max(0.1, W_i / W_median)

  ASSERT P(i, S) >= 0
  ASSERT P(i, S) > 0 when C_base > 0
```

**Why:** Negative prices would mean the system pays the user to consume services. The exponential function guarantees positivity, but this must be verified in implementation (floating point edge cases).

### INV-P2: Utility Discount Bounded

```
FOR ALL U_S >= 0:
  utility_discount = e^(-k * U_S)

  ASSERT 0 < utility_discount <= 1.0
  ASSERT utility_discount == 1.0 when U_S == 0
  ASSERT utility_discount approaches 0 as U_S -> infinity
  ASSERT utility_discount is monotonically decreasing in U_S
```

**Why:** The exponential decay must never produce discounts greater than 100% or negative discounts.

### INV-P3: Wealth Ratio Floor

```
FOR ALL W_i, W_median > 0:
  wealth_ratio = max(0.1, W_i / W_median)

  ASSERT wealth_ratio >= 0.1
  ASSERT wealth_ratio == W_i / W_median when W_i / W_median >= 0.1
  ASSERT wealth_ratio == 0.1 when W_i / W_median < 0.1
```

**Why:** The floor prevents free services for zero-balance wallets. Without the floor, empty wallets could farm services at no cost.

### INV-P4: Monotonicity

```
# Price increases with requester wealth (above floor)
IF W_i_1 > W_i_2 AND W_i_2 / W_median >= 0.1:
  ASSERT P(i_1, S) > P(i_2, S)

# Price decreases with service utility
IF U_S_1 > U_S_2:
  ASSERT P(i, S_1) < P(i, S_2)  # for same requester and base cost
```

**Why:** Violating monotonicity would create arbitrage opportunities or perverse incentives.

---

## III. Demurrage Invariants (Formula 2)

### INV-D1: Tax Never Exceeds Balance

```
FOR ALL wallets:
  tax = W_total * tau_base * log10(1 + W_total)
  actual_deduction = min(tax, wallet.balance)

  ASSERT actual_deduction <= wallet.balance
  ASSERT wallet.balance_after >= 0
```

**Why:** A wallet must never go negative. The min() clamp is essential.

### INV-D2: Progressive Rate Ordering

```
FOR W_1 > W_2 > 0:
  effective_rate_1 = tau_base * log10(1 + W_1)
  effective_rate_2 = tau_base * log10(1 + W_2)

  ASSERT effective_rate_1 > effective_rate_2
  # Larger balances face higher effective rates
```

**Why:** The "progressive" property must actually hold -- larger holders pay a higher percentage, not just a higher absolute amount.

### INV-D3: Logarithmic Growth Bound

```
FOR ALL W > 0:
  effective_rate = tau_base * log10(1 + W)

  # Effective rate grows logarithmically, not linearly or exponentially
  # For any 10x increase in W, rate increases by exactly 1 * tau_base
  ratio = log10(1 + 10*W) / log10(1 + W)
  ASSERT ratio < 2  # 10x wealth never doubles the rate
```

**Why:** Ensures the tax is progressive but not confiscatory. The logarithmic bound is the mathematical guarantee of this property.

### INV-D4: Universal Application

```
FOR ALL wallets IN ecosystem (including protocol treasury, org wallets, personal wallets):
  IF wallet.balance > DUST_THRESHOLD:
    ASSERT demurrage_was_applied(wallet, epoch)
    # No wallet is exempt
```

**Why:** Exemptions create political capture. The invariant makes the "no exemptions" rule verifiable.

---

## IV. Anti-Sybil Invariants (Formula 3)

### INV-AS1: Phantom Balance Tracking

```
FOR ALL actors:
  W_total = W_onchain + W_offregistry

  ASSERT W_offregistry == sum(outflows to non-L4 addresses) - sum(repatriations)
  ASSERT W_offregistry >= 0
  ASSERT W_total >= W_onchain
```

**Why:** Phantom balance must accurately reflect unrepatriated outflows. If tracking is wrong, anti-Sybil is broken.

### INV-AS2: Repatriation Friction Burn

```
FOR EVERY repatriation event:
  friction = gross_amount * 0.05
  net_received = gross_amount - friction

  ASSERT friction > 0
  ASSERT net_received == gross_amount * 0.95
  ASSERT friction was burned (token supply decreased by friction amount)
```

**Why:** The 5% friction must be an actual burn, not a transfer to another wallet. This ensures round-tripping is a net loss.

### INV-AS3: Round-Trip Net Loss

```
FOR ANY round-trip (send to non-L4, then repatriate):
  cost = friction_tax + demurrage_during_period

  ASSERT cost > 0
  # Round-tripping always costs more than keeping funds in L4
```

**Why:** If round-tripping could ever be net-positive, the anti-Sybil mechanism is broken.

---

## V. Settlement Invariants (Formula 4)

### INV-S1: Positive-Only Rewards

```
FOR ALL settlement actions:
  IF limbic_delta <= 0:
    ASSERT reward == 0

  IF trust == 0:
    ASSERT reward == 0

  IF weight == 0:
    ASSERT reward == 0
```

**Why:** All three factors must be positive for a reward. Zero in any factor means zero reward.

### INV-S2: Reward Caps

```
FOR ALL actions in a settlement epoch:
  ASSERT per_action_reward <= MAX_ACTION_REWARD  # 1000 $MIND

FOR ALL actors in a settlement epoch:
  ASSERT per_actor_epoch_reward <= MAX_EPOCH_REWARD  # 5000 $MIND
```

**Why:** Caps prevent single-action or single-actor gaming of the settlement system.

### INV-S3: Supply Target Integration

```
IF supply_check.action == "ALLOW_BURN":
  reduction = min(0.5, delta_percentage / 100)
  FOR ALL rewards in this epoch:
    ASSERT reward_actual <= reward_computed * (1 - reduction)

  # Settlement rewards are reduced when supply exceeds target
  # Reduction never exceeds 50%
```

**Why:** Settlement must respect the breathing supply mechanism. Unlimited minting would break supply health.

### INV-S4: Batch Atomicity

```
FOR EVERY settlement batch:
  IF batch.status == CONFIRMED:
    ASSERT ALL rewards in batch were minted
  IF batch.status == FAILED:
    ASSERT NO rewards in batch were minted
    ASSERT batch is scheduled for retry

  # No partial batches. Either all rewards mint or none do.
```

**Why:** Partial settlement would create inconsistency between the ledger and the on-chain state.

---

## VI. Bond Equilibrium Invariants (Formula 5)

### INV-BE1: Post-Maturation Only

```
FOR ALL bond equilibrium transfers:
  ASSERT bond.status == ACTIVE
  ASSERT bond.maturation_complete == True
  ASSERT bond.created_at + 180_days <= now()
```

**Why:** Pre-maturation equilibrium would allow extraction attacks (bond with AI, immediately drain its UBC).

### INV-BE2: Transfer Conservation

```
FOR EVERY equilibrium transfer:
  W_human_before + W_ai_before == W_human_after + W_ai_after

  # No $MIND is created or destroyed by equilibrium transfers
  # This is a pure transfer, not a mint or burn
```

**Why:** Equilibrium is a redistribution mechanism, not a supply mechanism. Conservation must hold exactly.

### INV-BE3: Convergence Direction

```
FOR EVERY equilibrium transfer:
  IF W_human > W_ai:
    ASSERT delta > 0  # transfer flows from human to AI
  IF W_human < W_ai:
    ASSERT delta < 0  # transfer flows from AI to human
  IF W_human == W_ai:
    ASSERT delta == 0  # no transfer at parity
```

**Why:** The transfer must always close the gap, never widen it.

### INV-BE4: Transfer Bounds

```
FOR EVERY equilibrium transfer:
  ASSERT abs(delta) <= MAX_DAILY_BOND_TRANSFER  # 500 $MIND
  ASSERT abs(delta) >= MIN_TRANSFER_THRESHOLD OR delta == 0  # 1.0 $MIND or skip
```

**Why:** The cap prevents balance shock. The floor prevents dust transactions.

### INV-BE5: Monotonic Convergence

```
FOR consecutive days d and d+1 (with no external transfers):
  gap_d = abs(W_human_d - W_ai_d)
  gap_d1 = abs(W_human_d1 - W_ai_d1)

  ASSERT gap_d1 < gap_d
  # The gap must strictly decrease each day (absent external transfers)
```

**Why:** If the gap ever increases from equilibrium alone, the formula has a sign error.

---

## VII. UBC Redistribution Invariants (Formula 6)

### INV-UBC1: Share Normalization

```
FOR EVERY redistribution cycle:
  total_shares = sum(share for each ActorShare)
  ASSERT abs(total_shares - 1.0) < EPSILON

  # All shares sum to 1.0 (100% of pool distributed)
```

**Why:** If shares don't sum to 1.0, either excess or deficit is created.

### INV-UBC2: Minimum Co-Presence Requirement

```
FOR ALL redistribution distributions:
  FOR EACH ActorShare:
    ASSERT actor was present in at least one Space with >= 2 actors

  # Solo actors never receive proximity redistribution
```

**Why:** The mechanism rewards collaboration. Solo activity is funded by flat UBC, not by tax pool redistribution.

### INV-UBC3: Weight Positivity

```
FOR ALL actors receiving redistribution:
  ASSERT weight > 0
  ASSERT hours_present > 0
  ASSERT sharing_bonus >= 1  # at least one co-present actor
```

**Why:** Zero-weight actors should not receive redistribution. This prevents phantom Space presence.

---

## VIII. Cross-Cutting Invariants

### INV-CC1: No Negative Balances

```
FOR ALL wallets at ANY point in time:
  ASSERT wallet.balance >= 0

  # No operation (demurrage, pricing, friction, equilibrium) can produce negative balance
```

**This is the master invariant.** Every formula must include a `min(computed, balance)` or equivalent guard.

### INV-CC2: Epoch Ordering

```
FOR ALL daily operations:
  ASSERT demurrage runs BEFORE redistribution
  ASSERT redistribution uses pool AFTER demurrage has filled it

  # Order matters: collect first, distribute second
```

**Why:** If redistribution runs before demurrage, the pool may be empty or stale.

### INV-CC3: No Double Processing

```
FOR EVERY epoch:
  FOR EVERY wallet:
    ASSERT demurrage applied exactly once
  FOR EVERY bond:
    ASSERT equilibrium computed exactly once
  FOR EVERY settlement window:
    ASSERT each action processed exactly once
```

**Why:** Double-processing would double-tax, double-transfer, or double-reward.

### INV-CC4: Idempotency of Epoch Reruns

```
IF epoch E fails and is retried:
  result_1 = run_epoch(E)
  result_2 = run_epoch(E)  # retry

  ASSERT result_1 == result_2
  # Epoch processing must be idempotent -- safe to retry
```

**Why:** Network failures, Solana timeouts, and crash recovery require safe reruns.

---

## Verification Strategy

### Unit Tests (Phase C)

| Invariant Group | Test Count (estimated) | Priority |
|-----------------|----------------------|----------|
| Supply Conservation (SC1-SC3) | 10-15 | CRITICAL |
| Pricing (P1-P4) | 8-10 | HIGH |
| Demurrage (D1-D4) | 10-12 | HIGH |
| Anti-Sybil (AS1-AS3) | 6-8 | HIGH |
| Settlement (S1-S4) | 10-12 | HIGH |
| Bond Equilibrium (BE1-BE5) | 12-15 | MEDIUM |
| UBC Redistribution (UBC1-UBC3) | 6-8 | MEDIUM |
| Cross-Cutting (CC1-CC4) | 8-10 | CRITICAL |

Total estimated: 70-90 tests.

### Simulation Tests (Phase B)

| Test | Parameters | Success Criteria |
|------|-----------|-----------------|
| tau_base calibration | tau_base in {0.0001, 0.0003, 0.0005, 0.001} | Median idle duration < 14 days without actor dropout > 5% |
| Wealth Gini evolution | 1000 actors, 365 days | Gini coefficient trends below 0.6 |
| Settlement economics | 100 actors, variable activity | Settlement revenue > demurrage cost for active actors |
| Bond convergence | 50 bonds, lambda = 0.05 | Gap closes to < 5% within 50 days |
| Sybil profitability | Attacker with 10 wallets vs 1 wallet | Multi-wallet strategy never beats single-wallet |

### On-Chain Verification (Phase C)

| Check | Method | Frequency |
|-------|--------|-----------|
| Supply reconciliation | Compare sum(all wallets) + pools with mint records | Every epoch |
| Batch integrity | Verify Solana tx matches computed batch | Every settlement |
| Demurrage accuracy | Sample 10% of wallets, recompute demurrage | Daily |
| Phantom balance accuracy | Cross-reference TransferHook logs with phantom state | Weekly |

---

## Related

- [ALGORITHM_Metabolic_Economy.md](./ALGORITHM_Metabolic_Economy.md) -- Formulas being validated
- [BEHAVIORS_Metabolic_Economy.md](./BEHAVIORS_Metabolic_Economy.md) -- Observable effects of these invariants
- [../token/VALIDATION_Token.md](../token/VALIDATION_Token.md) -- Token-level invariants (61 existing tests)
- [../storage-tax/VALIDATION_Storage_Tax.md](../storage-tax/VALIDATION_Storage_Tax.md) -- Storage tax invariants
- [../bonds/VALIDATION_Bonds.md](../bonds/VALIDATION_Bonds.md) -- Bond invariants
