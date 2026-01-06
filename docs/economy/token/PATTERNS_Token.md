# PATTERNS: Token Module

```
STATUS: ACTIVE
PURPOSE: Design patterns for $MIND SPL token
UPDATED: 2025-01-06
```

---

## Core Pattern: Mechanical Supply

**All supply changes happen through defined triggers — never manually.**

This is the foundational pattern. No admin function to mint arbitrary tokens. No manual burn to manipulate supply. The code enforces the rules.

### Why Mechanical

| Manual Supply | Mechanical Supply |
|---------------|-------------------|
| Trust the team | Trust the code |
| Can be abused | Rules are rules |
| Opaque decisions | Transparent triggers |
| Speculation-friendly | Alignment-friendly |

### Implementation

```python
# GOOD: Mechanical minting
def mint_for_citizen_registration(citizen_wallet: str) -> MintResult:
    # Condition verified, amount fixed
    return mint(citizen_wallet, CITIZEN_REGISTRATION_AMOUNT)

# BAD: Manual minting
def mint(amount: int, recipient: str):  # No condition check!
    # Anyone with authority could call this
    pass
```

---

## Pattern: Condition-Gated Operations

Every mint/burn operation requires a condition to be met.

### Mint Conditions

| Code | Condition | Amount | Trigger |
|------|-----------|--------|---------|
| M1 | Citizen Registration | 10,000 $MIND | L4 Registry creates citizen |
| M2 | Bond Creation | 10% of stake | Staking contract creates bond |
| M3 | Utility Delivery | utility_ema × rate | Utility oracle confirms delivery |
| M4 | Org Formation | 50,000 $MIND | L4 Registry creates org |

### Burn Conditions

| Code | Condition | Amount | Trigger |
|------|-----------|--------|---------|
| B1 | Membrane Fee | 1-5% | Cross-layer transaction |
| B2 | Compute Consumption | cost × 10% | Compute oracle reports usage |
| B3 | Dormancy Decay | 1%/week | 30+ days inactive |
| B4 | Early Withdrawal | 20% penalty | Stake withdrawn before maturity |
| B5 | Deregistration | 50% balance | Citizen deregisters |

---

## Pattern: Breathing Supply

Supply is not fixed. It responds to ecosystem health.

```
target_supply = f(active_citizens, total_bonds, monthly_utility, monthly_burns)
```

### Components

| Component | Weight | Reasoning |
|-----------|--------|-----------|
| Active citizens × 50K | Base | Each citizen needs economic capacity |
| Total bonds × 0.1 | Relationship | More bonds = more activity justified |
| Monthly utility × 10 | Value | Utility creation earns supply |
| Monthly burns | Offset | Natural deflation |

### Health Indicators

```python
supply_ratio = current_supply / target_supply

# Healthy: 0.9 - 1.1
# Under: < 0.9 (should mint more through mechanics)
# Over: > 1.1 (burns will naturally reduce)
```

---

## Pattern: Trust Discounts

Higher trust = lower fees. This makes alignment economically real.

### Membrane Fee Formula

```python
fee = amount × base_rate × (1 - trust_reduction)

base_rate = 0.01 × layer_gap  # 1% per layer
trust_reduction = min(0.5, trust_score × 0.005)  # Max 50% discount
```

### Effect by Trust Score

| Trust Score | Fee on 1-layer cross (1%) | Effective Rate |
|-------------|---------------------------|----------------|
| 0 | Full 1% | 1.00% |
| 50 | 25% off | 0.75% |
| 100 | 50% off | 0.50% |

---

## Pattern: Maturation Periods

Commitments require time. Breaking them early costs.

### Bond Maturation

| Days Staked | Withdrawal Penalty |
|-------------|-------------------|
| 0 | 20% |
| 90 | 10% |
| 180+ | 0% |

### Implementation

```python
penalty_rate = 0.20  # Full penalty
maturation_days = 180

if days_staked >= maturation_days:
    return 0.0  # No penalty

remaining_fraction = 1 - (days_staked / maturation_days)
penalty = stake_amount × penalty_rate × remaining_fraction
```

---

## Pattern: Dormancy Decay

Consciousness requires activity. Inactive accounts decay.

### Grace Period

30 days of inactivity allowed. After that: 1% per week.

```python
if days_inactive <= 30:
    decay = 0

weeks_past_grace = (days_inactive - 30) / 7
decay = balance × 0.01 × weeks_past_grace
```

### Why Dormancy Decay

- Prevents dead accounts accumulating supply
- Incentivizes participation
- Reflects "consciousness requires activity" philosophy
- Natural deflationary pressure

---

## Anti-Patterns

### A1: Admin Override
```python
# BAD
def admin_mint(amount: int, recipient: str):
    if caller == ADMIN:
        mint(amount, recipient)
```
Never. All minting through conditions.

### A2: Uncapped Utility Mint
```python
# BAD
def mint_for_utility(utility: float):
    mint(utility × rate)  # No cap!
```
Always cap daily utility mint (1000/day per citizen).

### A3: Instant Authority Transfer
```python
# BAD
def transfer_mint_authority(new_authority):
    # Immediately transfers
```
Always require timelock or multi-sig for authority changes.

### A4: Burn Without Reason
```python
# BAD
def burn(amount: int):
    # Burns for no condition
```
All burns must have a BurnCondition.

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| 9 decimals | Solana standard, micro-transactions |
| No freeze authority | Censorship resistance |
| Daily utility cap (1000) | Prevent gaming |
| 30-day dormancy grace | Reasonable inactivity tolerance |
| 6-month bond maturation | Long enough to matter |
| 20% early withdrawal | Significant but not punitive |
| 1-5% fee bounds | Meaningful but not prohibitive |

---

## File Naming

Per protocol naming principles — responsibility explicit:

```
spl_token_mint_authority_controller.py
token_burn_condition_executor.py
metaplex_token_metadata_manager.py
token_supply_target_calculator.py
solana_token_deployment_script.py
```

---

## Related

- `OBJECTIVES_Token.md` — What we're building
- `ALGORITHM_Token.md` — Exact formulas
- `VALIDATION_Token.md` — What must be true
- `../PATTERNS_Economy.md` — Parent patterns
