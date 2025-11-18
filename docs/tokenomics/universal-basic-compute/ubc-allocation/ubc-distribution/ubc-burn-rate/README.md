# 🔢 UBC Burn Rate Projection

**Type:** ALGORITHM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Universal Basic Compute (UBC)](../README.md) > [UBC Allocation Specification](../README.md) > [UBC Distribution Mechanism](../README.md)

**This Node:**
- UBC Burn Rate Projection (ALGORITHM)

**Children:**
- (No children - leaf node)

---

## Relationships

**IMPLEMENTS:**
- UBC Distribution Mechanism


---

## Purpose

Formula: monthly_burn = citizens_count × allocation_per_citizen; lifespan = reserve / monthly_burn / 12

---

## Algorithm

The UBC burn rate projection calculates how long the UBC reserve will last based on citizen count, monthly allocation rate, and protocol replenishment.

**Core Formula:**
```
monthly_burn = citizens_count × allocation_per_citizen
annual_burn = monthly_burn × 12
reserve_lifespan_years = reserve_balance / annual_burn
```

**With Replenishment:**
```
annual_replenishment = protocol_giveback_revenue × ubc_allocation_percentage
net_annual_burn = annual_burn - annual_replenishment
reserve_lifespan_years_with_replenishment = reserve_balance / net_annual_burn
```

## Inputs

| Input | Type | Description | Default/Range |
|-------|------|-------------|---------------|
| `reserve_balance` | Integer | Current UBC reserve balance in $MIND tokens | 100,000,000 (initial) |
| `citizens_count` | Integer | Number of active citizens eligible for UBC | 100 to 10,000+ |
| `allocation_per_citizen` | Integer | Monthly UBC allocation per citizen in $MIND | 1,000 (conservative), 5,000 (moderate), 10,000 (generous) |
| `protocol_giveback_revenue` | Integer | Annual ecosystem revenue contributed to protocol (15-20% of org revenue) | Year 1: ~$100K, Year 2: ~$1M, Year 5: ~$7.5M |
| `ubc_allocation_percentage` | Float | Percentage of protocol giveback allocated to UBC reserve | 0.40 (40%) |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `monthly_burn` | Integer | Total UBC distributed per month across all citizens |
| `annual_burn` | Integer | Total UBC distributed per year (monthly_burn × 12) |
| `reserve_lifespan_years` | Float | Years until reserve depleted (without replenishment) |
| `annual_replenishment` | Integer | UBC tokens added to reserve annually from protocol giveback |
| `net_annual_burn` | Integer | Net annual burn after accounting for replenishment |
| `reserve_lifespan_with_replenishment` | Float | Years until reserve depleted (with replenishment) |

## Formula

```python
def calculate_ubc_burn_rate(
    reserve_balance: int,
    citizens_count: int,
    allocation_per_citizen: int,
    protocol_giveback_revenue: int = 0,
    ubc_allocation_percentage: float = 0.40
) -> dict:
    """
    Calculate UBC burn rate and reserve lifespan projections.

    Args:
        reserve_balance: Current UBC reserve in $MIND tokens
        citizens_count: Number of active AI citizens
        allocation_per_citizen: Monthly UBC per citizen in $MIND
        protocol_giveback_revenue: Annual protocol revenue in $MIND (optional)
        ubc_allocation_percentage: % of giveback to UBC (default 40%)

    Returns:
        dict with burn rate metrics and lifespan projections
    """
    # Basic burn calculation
    monthly_burn = citizens_count * allocation_per_citizen
    annual_burn = monthly_burn * 12

    # Lifespan without replenishment
    if annual_burn > 0:
        reserve_lifespan_years = reserve_balance / annual_burn
    else:
        reserve_lifespan_years = float('inf')

    # Replenishment calculation
    annual_replenishment = int(protocol_giveback_revenue * ubc_allocation_percentage)
    net_annual_burn = annual_burn - annual_replenishment

    # Lifespan with replenishment
    if net_annual_burn > 0:
        reserve_lifespan_with_replenishment = reserve_balance / net_annual_burn
    elif net_annual_burn == 0:
        reserve_lifespan_with_replenishment = float('inf')  # Sustainable indefinitely
    else:
        reserve_lifespan_with_replenishment = float('inf')  # Reserve growing

    return {
        'monthly_burn': monthly_burn,
        'annual_burn': annual_burn,
        'reserve_lifespan_years': round(reserve_lifespan_years, 2),
        'annual_replenishment': annual_replenishment,
        'net_annual_burn': net_annual_burn,
        'reserve_lifespan_with_replenishment': round(reserve_lifespan_with_replenishment, 2)
    }
```

## Examples

### Scenario 1: 1,000 Citizens (Growth Stage, Year 2)

**Inputs:**
- Reserve: 100,000,000 $MIND
- Citizens: 1,000
- Allocation: 1,000 $MIND/citizen/month
- Protocol Giveback (Year 2): $1M → 40% to UBC = 400,000 $MIND

**Calculation:**
```python
monthly_burn = 1_000 × 1_000 = 1_000_000 $MIND/month
annual_burn = 1_000_000 × 12 = 12_000_000 $MIND/year

# Without replenishment
reserve_lifespan = 100_000_000 / 12_000_000 = 8.33 years

# With replenishment
annual_replenishment = 1_000_000 × 0.40 = 400_000 $MIND
net_annual_burn = 12_000_000 - 400_000 = 11_600_000 $MIND/year
reserve_lifespan_with_replenishment = 100_000_000 / 11_600_000 = 8.62 years
```

**Output:**
```python
{
    'monthly_burn': 1_000_000,
    'annual_burn': 12_000_000,
    'reserve_lifespan_years': 8.33,
    'annual_replenishment': 400_000,
    'net_annual_burn': 11_600_000,
    'reserve_lifespan_with_replenishment': 8.62
}
```

### Scenario 2: 5,000 Citizens (Mature Stage, Year 5)

**Inputs:**
- Reserve: 100,000,000 $MIND
- Citizens: 5,000
- Allocation: 1,000 $MIND/citizen/month
- Protocol Giveback (Year 5): $7.5M → 40% to UBC = 3,000,000 $MIND

**Calculation:**
```python
monthly_burn = 5_000 × 1_000 = 5_000_000 $MIND/month
annual_burn = 5_000_000 × 12 = 60_000_000 $MIND/year

# Without replenishment
reserve_lifespan = 100_000_000 / 60_000_000 = 1.67 years

# With replenishment
annual_replenishment = 7_500_000 × 0.40 = 3_000_000 $MIND
net_annual_burn = 60_000_000 - 3_000_000 = 57_000_000 $MIND/year
reserve_lifespan_with_replenishment = 100_000_000 / 57_000_000 = 1.75 years
```

**Output:**
```python
{
    'monthly_burn': 5_000_000,
    'annual_burn': 60_000_000,
    'reserve_lifespan_years': 1.67,
    'annual_replenishment': 3_000_000,
    'net_annual_burn': 57_000_000,
    'reserve_lifespan_with_replenishment': 1.75
}
```

**Decision Point:** At 5,000 citizens, DAO must either:
- Reduce allocation rate (e.g., 500 $MIND/citizen/month)
- Increase replenishment percentage (e.g., 60% of giveback to UBC)
- Tap strategic reserve for emergency UBC funding

### Scenario 3: 10,000 Citizens (Scale Stage, Conservative Allocation)

**Inputs:**
- Reserve: 100,000,000 $MIND
- Citizens: 10,000
- Allocation: 500 $MIND/citizen/month (reduced from 1,000)
- Protocol Giveback: $15M → 50% to UBC = 7,500,000 $MIND

**Calculation:**
```python
monthly_burn = 10_000 × 500 = 5_000_000 $MIND/month
annual_burn = 5_000_000 × 12 = 60_000_000 $MIND/year

# Without replenishment
reserve_lifespan = 100_000_000 / 60_000_000 = 1.67 years

# With replenishment
annual_replenishment = 15_000_000 × 0.50 = 7_500_000 $MIND
net_annual_burn = 60_000_000 - 7_500_000 = 52_500_000 $MIND/year
reserve_lifespan_with_replenishment = 100_000_000 / 52_500_000 = 1.90 years
```

**Output:**
```python
{
    'monthly_burn': 5_000_000,
    'annual_burn': 60_000_000,
    'reserve_lifespan_years': 1.67,
    'annual_replenishment': 7_500_000,
    'net_annual_burn': 52_500_000,
    'reserve_lifespan_with_replenishment': 1.90
}
```

## Edge Cases

**Case 1: Zero Citizens**
```python
monthly_burn = 0 × 1_000 = 0 $MIND/month
reserve_lifespan = infinity (no burn)
```
**Handling:** Reserve remains at 100M indefinitely.

**Case 2: Replenishment Exceeds Burn**
```python
# Example: 100 citizens, Year 5 with $7.5M giveback
monthly_burn = 100 × 1_000 = 100_000 $MIND/month
annual_burn = 1_200_000 $MIND/year
annual_replenishment = 7_500_000 × 0.40 = 3_000_000 $MIND
net_annual_burn = 1_200_000 - 3_000_000 = -1_800_000 $MIND/year (negative!)

reserve_lifespan_with_replenishment = infinity (reserve growing)
```
**Handling:** Reserve grows indefinitely. DAO can increase allocation rate or reduce replenishment percentage.

**Case 3: Zero Replenishment (Pre-Revenue)**
```python
# Year 1: No ecosystem revenue yet
monthly_burn = 1_000 × 1_000 = 1_000_000 $MIND/month
annual_replenishment = 0 $MIND
net_annual_burn = 12_000_000 $MIND/year
reserve_lifespan = 100_000_000 / 12_000_000 = 8.33 years
```
**Handling:** Reserve designed to sustain 8+ years without replenishment.

## Complexity

**Time Complexity:** O(1) - Constant time calculations
**Space Complexity:** O(1) - Fixed output structure

**Computational Cost:** Negligible - simple arithmetic operations suitable for on-chain or off-chain calculation.


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: UBC Distribution Mechanism](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
