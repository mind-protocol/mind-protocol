# VALIDATION: Token Module

```
STATUS: ACTIVE
PURPOSE: Invariants and validation rules for $MIND token
UPDATED: 2025-01-06
```

---

## Critical Invariants

These MUST be true. Test them.

### V1: Mint Authority Control

```
INVARIANT: Only authorized addresses can mint
TEST: Unauthorized mint attempt returns MintResult(success=False)
SEVERITY: CRITICAL — violation enables inflation attack
```

### V2: Burn Condition Requirement

```
INVARIANT: Burns only on defined conditions (B1-B5)
TEST: Manual burn without condition fails
SEVERITY: CRITICAL — violation enables supply manipulation
```

### V3: Supply Accuracy

```
INVARIANT: Tracked supply equals actual on-chain supply
TEST: Sum of mints - sum of burns == current supply
SEVERITY: HIGH — inaccuracy breaks health calculations
```

### V4: Fee Bounds

```
INVARIANT: Membrane fees between 1% and 5%
TEST: calculate_membrane_fee always returns fee in [0.01*amount, 0.05*amount]
SEVERITY: MEDIUM — violation affects economic model
```

### V5: Dormancy Grace Period

```
INVARIANT: No decay for first 30 days of inactivity
TEST: calculate_dormancy_decay(balance, 29) == 0
SEVERITY: MEDIUM — violation punishes legitimate inactivity
```

### V6: Bond Maturation

```
INVARIANT: Full withdrawal after 180 days has no penalty
TEST: calculate_early_withdrawal_penalty(amount, 180) == 0
SEVERITY: MEDIUM — violation breaks trust in commitments
```

---

## Verification Procedures

### VP1: Mint Authority Test

```python
def test_unauthorized_mint_fails():
    controller = MintAuthorityController(
        mint_address="test_mint",
        authority_keypair=None,  # No authority
        dry_run=False,
    )
    result = controller.mint_for_citizen_registration(
        citizen_wallet="unauthorized_wallet",
        citizen_id="test_citizen",
    )
    assert result.success == False
    assert "not yet implemented" in result.error or "unauthorized" in result.error.lower()
```

### VP2: Daily Cap Test

```python
def test_utility_daily_cap():
    controller = MintAuthorityController(mint_address="test", dry_run=True)

    # First mint: 800
    result1 = controller.mint_for_utility_delivery(
        citizen_wallet="wallet",
        citizen_id="citizen_1",
        utility_ema=800,
    )
    assert result1.success
    assert result1.amount == 800 * (10**9)

    # Second mint: should cap at 200
    result2 = controller.mint_for_utility_delivery(
        citizen_wallet="wallet",
        citizen_id="citizen_1",
        utility_ema=500,
    )
    assert result2.success
    assert result2.amount == 200 * (10**9)  # Capped

    # Third mint: should fail
    result3 = controller.mint_for_utility_delivery(
        citizen_wallet="wallet",
        citizen_id="citizen_1",
        utility_ema=100,
    )
    assert result3.success == False
    assert "cap reached" in result3.error.lower()
```

### VP3: Fee Bounds Test

```python
def test_membrane_fee_bounds():
    executor = BurnConditionExecutor(mint_address="test", dry_run=True)

    # Test various layer gaps and trust scores
    test_cases = [
        (1000, 1, 2, 0),    # 1% base
        (1000, 1, 4, 0),    # 3% base (but capped at 5%)
        (1000, 1, 2, 100),  # With max trust discount
    ]

    for amount, src, dst, trust in test_cases:
        fee = executor.calculate_membrane_fee(amount, src, dst, trust)
        assert fee >= amount * 0.01, f"Fee below 1%: {fee}"
        assert fee <= amount * 0.05, f"Fee above 5%: {fee}"
```

### VP4: Dormancy Grace Test

```python
def test_dormancy_grace_period():
    executor = BurnConditionExecutor(mint_address="test", dry_run=True)

    # Day 29: no decay
    decay_29 = executor.calculate_dormancy_decay(10_000, 29)
    assert decay_29 == 0

    # Day 30: no decay (boundary)
    decay_30 = executor.calculate_dormancy_decay(10_000, 30)
    assert decay_30 == 0

    # Day 31: decay starts
    decay_31 = executor.calculate_dormancy_decay(10_000, 31)
    assert decay_31 > 0
```

### VP5: Maturation Test

```python
def test_bond_maturation():
    executor = BurnConditionExecutor(mint_address="test", dry_run=True)

    # Day 179: still penalty
    penalty_179 = executor.calculate_early_withdrawal_penalty(10_000, 179)
    assert penalty_179 > 0

    # Day 180: no penalty
    penalty_180 = executor.calculate_early_withdrawal_penalty(10_000, 180)
    assert penalty_180 == 0

    # Day 200: no penalty
    penalty_200 = executor.calculate_early_withdrawal_penalty(10_000, 200)
    assert penalty_200 == 0
```

### VP6: Supply Calculation Test

```python
def test_supply_target_calculation():
    from economy.token import SupplyMetrics, calculate_target_supply

    metrics = SupplyMetrics(
        active_citizens=50,
        total_bonds=100_000,
        monthly_utility=10_000,
        monthly_burns=1_000,
    )

    target = calculate_target_supply(metrics)

    # Manual calculation:
    # 50 * 50_000 = 2_500_000
    # 100_000 * 0.1 = 10_000
    # 10_000 * 10 = 100_000
    # - 1_000
    # = 2_609_000

    assert target == 2_609_000
```

---

## Soft Constraints

These SHOULD be true. Warn if violated.

| Constraint | Threshold | Warning |
|------------|-----------|---------|
| Supply ratio | 0.8 - 1.2 | "Supply significantly off target" |
| Daily cap usage | < 90% | "Citizen approaching daily cap" |
| Dormancy warning | > 20 days | "Citizen approaching dormancy decay" |
| Bond maturation | > 150 days | "Bond approaching full maturation" |

---

## Runtime Validation

```python
def validate_mint_result(result: MintResult) -> list[str]:
    """Validate a mint result for consistency."""
    issues = []

    if result.success and result.amount <= 0:
        issues.append("Successful mint with zero/negative amount")

    if not result.success and result.tx_signature:
        issues.append("Failed mint has transaction signature")

    if result.success and not result.tx_signature:
        issues.append("Successful mint missing transaction signature")

    return issues


def validate_burn_result(result: BurnResult) -> list[str]:
    """Validate a burn result for consistency."""
    issues = []

    if result.success and result.amount < 0:
        issues.append("Successful burn with negative amount")

    if not result.success and result.tx_signature:
        issues.append("Failed burn has transaction signature")

    return issues
```

---

## Test Coverage Requirements

| Area | Required Tests | Status |
|------|---------------|--------|
| Mint conditions (M1-M4) | 4 minimum | Pending |
| Burn conditions (B1-B5) | 5 minimum | Pending |
| Daily cap | 3 minimum | Pending |
| Fee calculation | 5 minimum | Pending |
| Supply calculation | 3 minimum | Pending |
| Health indicators | 3 minimum | Pending |
| Edge cases | 10 minimum | Pending |

**Target: 35+ tests for token module**

---

## Related

- `ALGORITHM_Token.md` — Formulas being validated
- `BEHAVIORS_Token.md` — Expected behaviors
- `tests/economy/test_token_*.py` — Actual test implementations
