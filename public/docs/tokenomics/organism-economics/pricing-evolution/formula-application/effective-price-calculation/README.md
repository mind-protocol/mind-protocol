# 🔢 Effective Price Calculation

**Type:** ALGORITHM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Organism Economics](../README.md) > [Pricing Evolution Specification](../README.md) > [Organism Economics Formula Application](../README.md)

**This Node:**
- Effective Price Calculation (ALGORITHM)

**Children:**
- (No children - leaf node)

---

## Relationships

**IMPLEMENTS:**
- Organism Economics Formula Application


---

## Purpose

Formula: effective_price = base_cost × complexity × risk × (1 - utility_rebate) × org_specific

---

## Algorithm

**Effective price calculation combines base cost with all pricing multipliers to produce the final price in $MIND tokens.**

### Algorithm Steps

1. **Calculate base cost** from resource consumption
2. **Apply complexity multiplier** based on service difficulty
3. **Apply risk multiplier** based on trust score
4. **Apply utility rebate** based on ecosystem contribution
5. **Apply organization-specific variable** based on org type
6. **Verify minimum viable price** (>= base_cost × 0.4)
7. **Return effective price** in $MIND tokens

## Inputs

| Input | Type | Range | Description |
|-------|------|-------|-------------|
| `base_cost` | float | > 0 | Actual cost to provide service (compute + labor + infra + margin) |
| `complexity_multiplier` | float | 0.7 - 2.5 | Service complexity (simple to highly complex) |
| `risk_multiplier` | float | 0.6 - 1.8 | Calculated from trust score (trusted to risky) |
| `utility_rebate` | float | 0.0 - 0.4 | Ecosystem contribution rebate (0% to 40%) |
| `org_specific_variable` | float | 0.6 - 2.0 | Organization-specific multiplier (varies by org type) |
| `minimum_viable_multiplier` | float | 0.4 | Minimum price threshold (default: 40% of base cost) |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `effective_price` | float | Final price in $MIND tokens |
| `price_breakdown` | dict | Detailed breakdown showing each multiplier's contribution |
| `discount_percentage` | float | Total discount from base cost (if applicable) |

## Formula

### Core Formula

```python
def calculate_effective_price(
    base_cost: float,
    complexity_multiplier: float,
    risk_multiplier: float,
    utility_rebate: float,
    org_specific_variable: float,
    minimum_viable_multiplier: float = 0.4
) -> dict:
    """
    Calculate effective price using organism economics formula.

    Returns:
        {
            'effective_price': float,
            'price_breakdown': dict,
            'discount_percentage': float
        }
    """

    # Step 1: Apply universal multipliers
    price_after_complexity = base_cost * complexity_multiplier
    price_after_risk = price_after_complexity * risk_multiplier
    price_after_utility = price_after_risk * (1 - utility_rebate)

    # Step 2: Apply organization-specific variable
    effective_price = price_after_utility * org_specific_variable

    # Step 3: Verify minimum viable price
    minimum_viable_price = base_cost * minimum_viable_multiplier

    if effective_price < minimum_viable_price:
        raise PricingError(
            f"Effective price ({effective_price}) below minimum viable "
            f"threshold ({minimum_viable_price})"
        )

    # Step 4: Calculate discount percentage
    if effective_price < base_cost:
        discount_percentage = ((base_cost - effective_price) / base_cost) * 100
    else:
        discount_percentage = 0.0  # Price premium, not discount

    # Step 5: Build detailed breakdown
    price_breakdown = {
        'base_cost': base_cost,
        'after_complexity': price_after_complexity,
        'after_risk': price_after_risk,
        'after_utility_rebate': price_after_utility,
        'after_org_specific': effective_price,
        'multipliers': {
            'complexity': complexity_multiplier,
            'risk': risk_multiplier,
            'utility_rebate': utility_rebate,
            'org_specific': org_specific_variable
        }
    }

    return {
        'effective_price': effective_price,
        'price_breakdown': price_breakdown,
        'discount_percentage': discount_percentage
    }
```

### Organization-Specific Formulas

**consultingOrg (with reputation premium):**
```python
effective_price = base_cost × complexity × risk × (1 - utility_rebate) × reputation_premium
```

**GraphCare (with load multiplier):**
```python
effective_price = base_cost × load_multiplier × risk × (1 - utility_rebate)
```

**scalingOrg (with volume discount, success probability replaces risk):**
```python
effective_price = base_cost × complexity × success_probability × (1 - volume_discount)
```

**financeOrg (with urgency multiplier):**
```python
effective_price = base_cost × complexity × risk × (1 - utility_rebate) × urgency_multiplier
```

**legalOrg (with urgency multiplier):**
```python
effective_price = base_cost × complexity × risk × (1 - utility_rebate) × urgency_multiplier
```

**securityOrg (with security posture rebate instead of utility rebate):**
```python
effective_price = base_cost × complexity × risk × (1 - security_posture_rebate) × urgency_multiplier
```

**techServiceOrg (with familiarity discount):**
```python
effective_price = base_cost × complexity × (1 - familiarity_discount)
```

## Examples

### Example 1: consultingOrg - New vs Trusted Customer

**New Customer (Month 1):**
```python
base_cost = 100_000 $MIND
complexity = 1.5 (complex transformation)
risk = 1.2 (new relationship, unknown reliability)
utility_rebate = 0.0 (no ecosystem contribution yet)
reputation_premium = 1.0 (consultingOrg building reputation)

effective_price = 100_000 × 1.5 × 1.2 × (1 - 0.0) × 1.0
effective_price = 180_000 $MIND

discount_percentage = 0% (premium, not discount)
```

**Trusted Customer (Month 12):**
```python
base_cost = 100_000 $MIND
complexity = 1.5 (same complexity)
risk = 0.6 (deeply trusted, 12-month relationship)
utility_rebate = 0.4 (major ecosystem contributor)
reputation_premium = 1.8 (prestigious consultingOrg brand)

effective_price = 100_000 × 1.5 × 0.6 × (1 - 0.4) × 1.8
effective_price = 97_200 $MIND

discount_percentage = ((100_000 - 97_200) / 100_000) × 100 = 2.8%
# Note: Despite trust, reputation premium keeps price near base cost
# But compared to Month 1, this is 46% reduction (180K → 97K)
```

### Example 2: GraphCare - Monthly Subscription Evolution

**Month 1 (New Client):**
```python
base_cost = 100 $MIND/month
load_multiplier = 1.0 (normal capacity)
risk = 1.2 (new client)
utility_rebate = 0.0 (no contribution)

effective_price = 100 × 1.0 × 1.2 × (1 - 0.0)
effective_price = 120 $MIND/month

discount_percentage = 0%
```

**Month 12 (Trusted Client):**
```python
base_cost = 100 $MIND/month
load_multiplier = 0.7 (low load, plenty of capacity)
risk = 0.6 (excellent 12-month history)
utility_rebate = 0.35 (referred 3 customers)

effective_price = 100 × 0.7 × 0.6 × (1 - 0.35)
effective_price = 27.3 $MIND/month

discount_percentage = ((100 - 27.3) / 100) × 100 = 72.7%
# 77% reduction from Month 1 (120 → 27.3)
```

### Example 3: financeOrg - Emergency vs Normal

**Normal Timeline (New Client):**
```python
base_cost = 15_000 $MIND
complexity = 1.5 (complex financial model)
risk = 1.2 (new client)
utility_rebate = 0.0
urgency = 1.0 (normal 4-6 week timeline)

effective_price = 15_000 × 1.5 × 1.2 × (1 - 0.0) × 1.0
effective_price = 27_000 $MIND
```

**Emergency (Same Client, Crisis Situation):**
```python
base_cost = 15_000 $MIND
complexity = 1.2 (slightly simpler due to urgency constraints)
risk = 1.5 (crisis creates unknowns)
utility_rebate = 0.0
urgency = 1.8 (emergency, need model in 1 week)

effective_price = 15_000 × 1.2 × 1.5 × (1 - 0.0) × 1.8
effective_price = 48_600 $MIND

# 80% premium for emergency response
```

### Example 4: securityOrg - Security Posture Impact

**First Audit (Unknown Security):**
```python
base_cost = 20_000 $MIND
complexity = 1.5 (thorough audit)
risk = 1.2 (unknown organization)
security_posture_rebate = 0.0 (no track record)
urgency = 1.0 (normal)

effective_price = 20_000 × 1.5 × 1.2 × (1 - 0.0) × 1.0
effective_price = 36_000 $MIND
```

**Fifth Audit (Excellent Security):**
```python
base_cost = 20_000 $MIND
complexity = 1.2 (standard audit, patterns known)
risk = 0.7 (trusted partner)
security_posture_rebate = 0.4 (excellent security history)
urgency = 1.0 (routine)

effective_price = 20_000 × 1.2 × 0.7 × (1 - 0.4) × 1.0
effective_price = 10_080 $MIND

discount_percentage = ((20_000 - 10_080) / 20_000) × 100 = 49.6%
# 72% reduction from first audit (36K → 10K)
```

## Edge Cases

### 1. Price Below Minimum Viable Threshold

```python
base_cost = 10_000 $MIND
complexity = 0.7 (simple)
risk = 0.6 (trusted)
utility_rebate = 0.4 (high ecosystem value)
org_specific = 0.8

effective_price = 10_000 × 0.7 × 0.6 × (1 - 0.4) × 0.8
effective_price = 2_016 $MIND

minimum_viable = 10_000 × 0.4 = 4_000 $MIND

# Error: effective_price (2,016) < minimum_viable (4,000)
# Organization must either:
# 1. Decline service
# 2. Renegotiate higher base_cost
# 3. Reduce discounts (lower rebate or org_specific variable)
```

### 2. Price Above Base Cost (Premium Pricing)

```python
base_cost = 50_000 $MIND
complexity = 2.5 (highly complex)
risk = 1.8 (very risky, new client in uncertain domain)
utility_rebate = 0.0
reputation_premium = 1.5

effective_price = 50_000 × 2.5 × 1.8 × (1 - 0.0) × 1.5
effective_price = 337_500 $MIND

# 575% of base cost - justified by extreme complexity + risk
```

### 3. Conflicting Variables (High Reputation + High Trust)

```python
base_cost = 100_000 $MIND
complexity = 1.5
risk = 0.6 (deeply trusted)
utility_rebate = 0.35
reputation_premium = 2.0 (prestigious consultingOrg)

effective_price = 100_000 × 1.5 × 0.6 × (1 - 0.35) × 2.0
effective_price = 117_000 $MIND

# Trust pulls price down, reputation pulls price up
# Net result: slight premium over base cost
# Customer pays for prestigious brand but gets trust discount
```

### 4. Zero Risk (Perfect Trust Score)

```python
# Theoretical maximum trust
trust_score = 1.0
risk_multiplier = 1.8 - (1.0 × 1.2) = 0.6  # Floor at 0.6, not 0

# We don't allow zero risk - minimum is 0.6 (60% of baseline)
# This prevents predatory pricing and maintains sustainability
```

### 5. Zero Utility Rebate with High Trust

```python
base_cost = 5_000 $MIND
complexity = 1.0
risk = 0.6 (trusted, but no ecosystem contribution)
utility_rebate = 0.0
org_specific = 1.0

effective_price = 5_000 × 1.0 × 0.6 × (1 - 0.0) × 1.0
effective_price = 3_000 $MIND

# 40% discount from trust alone
# Shows importance of payment reliability even without ecosystem contribution
```

## Complexity

**Time Complexity:** O(1)
- All operations are constant-time arithmetic
- No loops or recursion

**Space Complexity:** O(1)
- Fixed number of variables regardless of input size
- Price breakdown dict has constant size

**Computational Cost:**
- Negligible - simple multiplication and subtraction
- Can calculate millions of prices per second
- No database lookups required (all inputs provided)


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Organism Economics Formula Application](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
