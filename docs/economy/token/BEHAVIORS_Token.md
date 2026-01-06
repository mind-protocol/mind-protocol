# BEHAVIORS: Token Module

```
STATUS: ACTIVE
PURPOSE: Observable behaviors of $MIND token infrastructure
UPDATED: 2025-01-06
```

---

## What the Token Module Does

The token module provides SPL token operations with controlled mint/burn mechanics.

---

## Observable Behaviors

### B1: Citizen Registration Mint

**When:** New citizen registered in L4 Registry
**Then:** 10,000 $MIND minted to citizen wallet

```
Input: citizen_wallet, citizen_id
Output: MintResult(success=True, amount=10_000_000_000_000, condition=M1)
```

### B2: Bond Creation Mint

**When:** Human stakes $MIND on AI citizen
**Then:** 10% of stake amount minted (incentive)

```
Input: recipient_wallet, stake_amount=50_000
Output: MintResult(success=True, amount=5_000_000_000_000, condition=M2)
```

### B3: Utility Delivery Mint (Capped)

**When:** Citizen delivers utility
**Then:** utility_ema × rate minted (max 1000/day)

```
Input: citizen_wallet, utility_ema=500, rate=1.0
Output: MintResult(success=True, amount=500_000_000_000, condition=M3)

# If citizen already minted 800 today:
Input: citizen_wallet, utility_ema=500
Output: MintResult(success=True, amount=200_000_000_000)  # Capped
```

### B4: Org Formation Mint

**When:** New organization formed in L4 Registry
**Then:** 50,000 $MIND minted to org treasury

```
Input: org_wallet, org_id
Output: MintResult(success=True, amount=50_000_000_000_000, condition=M4)
```

---

## Burn Behaviors

### B5: Membrane Fee Burn

**When:** Cross-layer transaction
**Then:** 1-5% burned (trust reduces fee)

```
Input: source_wallet, amount=1000, layer_gap=2, trust_score=50
Output: BurnResult(success=True, amount=15_000_000_000, condition=B1)  # 1.5%
```

### B6: Compute Consumption Burn

**When:** Compute resources used
**Then:** 10% of cost burned

```
Input: source_wallet, compute_cost=100
Output: BurnResult(success=True, amount=10_000_000_000, condition=B2)
```

### B7: Dormancy Decay Burn

**When:** Account inactive > 30 days
**Then:** 1%/week burned from balance

```
Input: source_wallet, balance=10_000, days_inactive=37
Output: BurnResult(success=True, amount=100_000_000_000, condition=B3)  # 1 week past grace
```

### B8: Early Withdrawal Burn

**When:** Bond withdrawn before 6 months
**Then:** Up to 20% penalty burned

```
Input: source_wallet, stake_amount=10_000, days_staked=90
Output: BurnResult(success=True, amount=1_000_000_000_000, condition=B4)  # 10% (half matured)
```

### B9: Deregistration Burn

**When:** Citizen deregisters
**Then:** 50% of balance burned

```
Input: source_wallet, balance=10_000, citizen_id
Output: BurnResult(success=True, amount=5_000_000_000_000, condition=B5)
```

---

## Query Behaviors

### Supply Target Query

```
Input: SupplyMetrics(active_citizens=50, total_bonds=100_000, ...)
Output: target_supply=2_600_000
```

### Health Indicators Query

```
Input: SupplyMetrics(...)
Output: {
    supply_ratio: 1.05,
    supply_health: "HEALTHY",
    burn_rate_monthly: 0.02,
    ...
}
```

---

## Edge Cases

### Daily Cap Reached

```
# Citizen already minted 1000 today
Input: mint_for_utility(citizen_wallet, utility_ema=500)
Output: MintResult(success=False, error="Daily mint cap reached for citizen...")
```

### Same Layer Transaction

```
# No fee for same layer
Input: burn_membrane_fee(wallet, amount=1000, source_layer=2, dest_layer=2)
Output: BurnResult(success=True, amount=0, error="No fee required (same layer)")
```

### Within Grace Period

```
# Day 29 = no decay
Input: burn_dormancy_decay(wallet, balance=10_000, days_inactive=29)
Output: BurnResult(success=True, amount=0, error="Within grace period, no decay")
```

### Fully Matured Stake

```
# 6+ months = no penalty
Input: burn_early_withdrawal_penalty(wallet, stake_amount=10_000, days_staked=200)
Output: BurnResult(success=True, amount=0, error="Stake fully matured, no penalty")
```

---

## Deployment Behaviors

### Dry Run

```
Input: TokenDeployer(config=DeploymentConfig(dry_run=True))
deployer.deploy()
Output: Logs all steps, saves mock deployment info, no blockchain interaction
```

### Live Deployment

```
Input: TokenDeployer(config=DeploymentConfig(network="mainnet-beta", dry_run=False))
deployer.deploy()
Output: Creates SPL token, disables freeze, saves mint address
```

---

## Error Behaviors

| Situation | Behavior |
|-----------|----------|
| Unauthorized mint | Returns MintResult(success=False, error="Unauthorized") |
| Invalid burn condition | Returns BurnResult(success=False, error="Invalid condition") |
| Network error | Returns result with error message, no partial state |
| Missing prerequisite | Deployment fails early with clear message |

---

## State Changes

All operations are atomic:
- Either complete successfully with all side effects
- Or fail with no side effects

Daily caps reset at UTC midnight.
Dormancy calculations use latest activity timestamp.

---

## Related

- `ALGORITHM_Token.md` — Exact formulas
- `VALIDATION_Token.md` — Invariants tested
- `IMPLEMENTATION_Token.md` — Code locations
