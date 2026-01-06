# ALGORITHM: Token Module

```
STATUS: ACTIVE
PURPOSE: Exact formulas and logic for $MIND token operations
UPDATED: 2025-01-06
```

---

## Mint Algorithms

### M1: Citizen Registration Mint

```python
def mint_for_citizen_registration(citizen_wallet: str, citizen_id: str) -> MintResult:
    """
    Mint 10,000 $MIND for new citizen.

    Preconditions:
    - citizen_id exists in L4 Registry
    - citizen has not received registration mint before

    Amount: 10,000 $MIND (fixed)
    """
    AMOUNT = 10_000 * (10 ** 9)  # With 9 decimals
    return execute_mint(citizen_wallet, AMOUNT, condition=M1)
```

### M2: Bond Creation Mint

```python
def mint_for_bond_creation(recipient_wallet: str, stake_amount: float) -> MintResult:
    """
    Mint 10% of stake amount as bonding incentive.

    Preconditions:
    - Valid bond created in staking contract
    - stake_amount > 0

    Amount: stake_amount * 0.10
    """
    RATE = 0.10
    amount = stake_amount * RATE
    return execute_mint(recipient_wallet, to_smallest_units(amount), condition=M2)
```

### M3: Utility Delivery Mint

```python
def mint_for_utility_delivery(
    citizen_wallet: str,
    citizen_id: str,
    utility_ema: float,
    rate: float = 1.0
) -> MintResult:
    """
    Mint tokens for utility delivered, with daily cap.

    Preconditions:
    - Utility oracle confirmed delivery
    - citizen_id is active

    Formula: min(utility_ema * rate, remaining_daily_cap)
    Daily cap: 1000 $MIND per citizen
    """
    DAILY_CAP = 1000

    already_minted_today = get_daily_mint(citizen_id)
    remaining = max(0, DAILY_CAP - already_minted_today)

    if remaining == 0:
        return MintResult(success=False, error="Daily cap reached")

    calculated = utility_ema * rate
    actual_mint = min(calculated, remaining)

    result = execute_mint(citizen_wallet, to_smallest_units(actual_mint), condition=M3)

    if result.success:
        record_daily_mint(citizen_id, actual_mint)

    return result
```

### M4: Org Formation Mint

```python
def mint_for_org_formation(org_wallet: str, org_id: str) -> MintResult:
    """
    Mint 50,000 $MIND for new organization.

    Preconditions:
    - org_id exists in L4 Registry
    - org has not received formation mint before

    Amount: 50,000 $MIND (fixed)
    """
    AMOUNT = 50_000 * (10 ** 9)
    return execute_mint(org_wallet, AMOUNT, condition=M4)
```

---

## Burn Algorithms

### B1: Membrane Fee Burn

```python
def calculate_membrane_fee(
    amount: float,
    source_layer: int,
    dest_layer: int,
    trust_score: float
) -> float:
    """
    Calculate fee for cross-layer transaction.

    Formula:
        base_rate = 0.01 * layer_gap  (1% per layer)
        trust_reduction = min(0.5, trust_score * 0.005)
        fee = amount * base_rate * (1 - trust_reduction)

    Bounds: 1% minimum, 5% maximum
    """
    layer_gap = abs(dest_layer - source_layer)
    if layer_gap == 0:
        return 0.0

    base_rate = 0.01 * layer_gap
    trust_reduction = min(0.5, trust_score * 0.005)
    fee = amount * base_rate * (1 - trust_reduction)

    MIN_RATE = 0.01
    MAX_RATE = 0.05

    return clamp(fee, amount * MIN_RATE, amount * MAX_RATE)
```

### B2: Compute Consumption Burn

```python
def calculate_compute_burn(compute_cost: float) -> float:
    """
    Calculate burn for compute consumption.

    Formula: cost * 0.10 (10%)
    """
    BURN_RATE = 0.10
    return compute_cost * BURN_RATE
```

### B3: Dormancy Decay Burn

```python
def calculate_dormancy_decay(balance: float, days_inactive: int) -> float:
    """
    Calculate decay for inactive accounts.

    Grace period: 30 days (no decay)
    After grace: 1% per week

    Formula:
        if days_inactive <= 30: return 0
        weeks_past_grace = (days_inactive - 30) / 7
        decay = balance * 0.01 * weeks_past_grace
    """
    GRACE_PERIOD = 30
    WEEKLY_RATE = 0.01

    if days_inactive <= GRACE_PERIOD:
        return 0.0

    weeks_past_grace = (days_inactive - GRACE_PERIOD) / 7.0
    decay = balance * WEEKLY_RATE * weeks_past_grace

    return min(decay, balance)  # Can't decay more than balance
```

### B4: Early Withdrawal Penalty

```python
def calculate_early_withdrawal_penalty(stake_amount: float, days_staked: int) -> float:
    """
    Calculate penalty for early bond withdrawal.

    Maturation: 180 days (6 months)
    Full penalty: 20%
    Scaling: Linear reduction as maturation approaches

    Formula:
        if days_staked >= 180: return 0
        remaining_fraction = 1 - (days_staked / 180)
        penalty = stake_amount * 0.20 * remaining_fraction
    """
    MATURATION_DAYS = 180
    FULL_PENALTY_RATE = 0.20

    if days_staked >= MATURATION_DAYS:
        return 0.0

    remaining_fraction = 1 - (days_staked / MATURATION_DAYS)
    return stake_amount * FULL_PENALTY_RATE * remaining_fraction
```

### B5: Deregistration Burn

```python
def calculate_deregistration_burn(balance: float) -> float:
    """
    Calculate burn for citizen deregistration.

    Formula: balance * 0.50 (50%)
    """
    BURN_RATE = 0.50
    return balance * BURN_RATE
```

---

## Supply Target Algorithm

```python
def calculate_target_supply(metrics: SupplyMetrics) -> float:
    """
    Calculate healthy supply target.

    Formula:
        target = (active_citizens * 50_000)
               + (total_bonds * 0.1)
               + (monthly_utility * 10)
               - monthly_burns

    Components:
    - Citizen base: Each active citizen needs economic capacity
    - Bond supply: Relationships justify more supply
    - Utility supply: Value creation earns supply
    - Burn offset: Natural deflation
    """
    citizen_base = metrics.active_citizens * 50_000
    bond_supply = metrics.total_bonds * 0.1
    utility_supply = metrics.monthly_utility * 10
    burn_offset = metrics.monthly_burns

    target = citizen_base + bond_supply + utility_supply - burn_offset
    return max(0, target)
```

---

## Supply Adjustment Algorithm

```python
def calculate_supply_adjustment(metrics: SupplyMetrics) -> dict:
    """
    Determine if supply needs adjustment.

    Actions:
    - HOLD: Within 1% of target
    - MINT: More than 1% below target (let mechanics increase)
    - ALLOW_BURN: More than 1% above target (friction will reduce)
    """
    target = calculate_target_supply(metrics)
    current = metrics.current_supply
    delta = target - current

    if current > 0:
        delta_percentage = (delta / current) * 100
    else:
        delta_percentage = 100.0 if target > 0 else 0.0

    if abs(delta_percentage) < 1.0:
        action = "HOLD"
    elif delta > 0:
        action = "MINT"  # Mechanics will increase supply
    else:
        action = "ALLOW_BURN"  # Friction will decrease supply

    return {
        "action": action,
        "target_supply": target,
        "current_supply": current,
        "delta": delta,
        "delta_percentage": delta_percentage,
    }
```

---

## Health Indicator Algorithm

```python
def calculate_health_indicators(metrics: SupplyMetrics) -> dict:
    """
    Calculate ecosystem health indicators.

    Indicators:
    - supply_ratio: current / target (1.0 = perfect)
    - supply_health: HEALTHY (0.9-1.1), UNDER (<0.9), OVER (>1.1)
    - burn_rate_monthly: burns / supply
    - bond_coverage: bonds / supply
    - activity_ratio: active / total citizens
    """
    target = calculate_target_supply(metrics)
    current = metrics.current_supply

    supply_ratio = current / target if target > 0 else 1.0

    if 0.9 <= supply_ratio <= 1.1:
        health = "HEALTHY"
    elif supply_ratio < 0.9:
        health = "UNDER"
    else:
        health = "OVER"

    return {
        "supply_ratio": supply_ratio,
        "supply_health": health,
        "burn_rate_monthly": metrics.monthly_burns / current if current > 0 else 0,
        "bond_coverage": metrics.total_bonds / current if current > 0 else 0,
        "activity_ratio": metrics.active_citizens / metrics.total_citizens if metrics.total_citizens > 0 else 0,
    }
```

---

## Unit Conversion

```python
DECIMALS = 9

def to_smallest_units(amount: float) -> int:
    """Convert token amount to smallest units (with 9 decimals)."""
    return int(amount * (10 ** DECIMALS))

def from_smallest_units(amount: int) -> float:
    """Convert from smallest units to token amount."""
    return amount / (10 ** DECIMALS)
```

---

## Related

- `BEHAVIORS_Token.md` — How these algorithms behave
- `VALIDATION_Token.md` — Invariants to verify
- `IMPLEMENTATION_Token.md` — Where code lives
