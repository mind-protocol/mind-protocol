# 🔢 Trust Score Calculation

**Type:** ALGORITHM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Organism Economics](../README.md) > [Pricing Evolution Specification](../README.md) > [Organism Economics Formula Application](../README.md)

**This Node:**
- Trust Score Calculation (ALGORITHM)

**Children:**
- (No children - leaf node)

---

## Relationships

**IMPLEMENTS:**
- Organism Economics Formula Application


---

## Purpose

Formula: trust_score = payment_reliability × 0.4 + relationship_duration × 0.3 + ecosystem_contribution × 0.3

---

## Algorithm

**Trust score calculation combines payment reliability, relationship duration, and ecosystem contribution into a single score (0-1), which then determines the risk multiplier used in pricing.**

### Algorithm Steps

1. **Calculate payment reliability score** (0-1) from payment history
2. **Calculate relationship duration score** (0-1) from months of engagement
3. **Calculate ecosystem contribution score** (0-1) from value provided
4. **Combine into trust score** using weighted formula
5. **Convert trust score to risk multiplier** (inverse relationship: high trust = low risk)

## Inputs

| Input | Type | Range | Description |
|-------|------|-------|-------------|
| `payment_reliability` | float | 0.0 - 1.0 | On-time payment history (0 = no history, 1 = perfect record) |
| `relationship_duration_months` | int | 0 - ∞ | Months since first engagement |
| `ecosystem_contribution` | float | 0.0 - 1.0 | Value provided to ecosystem (referrals, support, etc.) |

**Payment Reliability Sub-Inputs:**
- `total_payments` | int | Count of all payment events
- `on_time_payments` | int | Count of on-time payments
- `late_payments` | int | Count of late payments (1-30 days)
- `very_late_payments` | int | Count of very late payments (>30 days)
- `disputes` | int | Count of payment disputes

**Relationship Duration Sub-Inputs:**
- `first_engagement_date` | datetime | Date of first transaction
- `current_date` | datetime | Current date

**Ecosystem Contribution Sub-Inputs:**
- `referrals_generated` | int | New customers brought to ecosystem
- `protocol_support_value` | float | UBC contributions, L4 validation support
- `knowledge_shared` | bool | Case studies, documentation, testimonials
- `integration_depth` | float | 0-1, how deeply integrated with ecosystem

## Outputs

| Output | Type | Range | Description |
|--------|------|-------|-------------|
| `trust_score` | float | 0.0 - 1.0 | Combined trust score (0 = no trust, 1 = maximum trust) |
| `risk_multiplier` | float | 0.6 - 1.8 | Price multiplier (inverse of trust: low trust = high risk) |
| `trust_breakdown` | dict | - | Detailed breakdown of trust components |

## Formula

### Core Trust Score Formula

```python
def calculate_trust_score(
    payment_reliability: float,
    relationship_duration_months: int,
    ecosystem_contribution: float
) -> dict:
    """
    Calculate trust score from relationship history.

    Args:
        payment_reliability: Payment history score (0-1)
        relationship_duration_months: Months since first engagement
        ecosystem_contribution: Ecosystem value score (0-1)

    Returns:
        {
            'trust_score': float,
            'risk_multiplier': float,
            'trust_breakdown': dict
        }
    """

    # Step 1: Normalize relationship duration to 0-1 score
    # Assume 24 months = perfect duration score
    MAX_DURATION_MONTHS = 24
    duration_score = min(1.0, relationship_duration_months / MAX_DURATION_MONTHS)

    # Step 2: Calculate weighted trust score
    trust_score = (
        payment_reliability * 0.4      # 40% weight - most important
        + duration_score * 0.3          # 30% weight - second most important
        + ecosystem_contribution * 0.3  # 30% weight - equal to duration
    )

    # Step 3: Convert trust score to risk multiplier (inverse relationship)
    # trust_score 0.0 → risk_multiplier 1.8 (high risk)
    # trust_score 1.0 → risk_multiplier 0.6 (low risk)
    risk_multiplier = 1.8 - (trust_score * 1.2)

    # Step 4: Build detailed breakdown
    trust_breakdown = {
        'payment_reliability': payment_reliability,
        'relationship_duration_months': relationship_duration_months,
        'duration_score': duration_score,
        'ecosystem_contribution': ecosystem_contribution,
        'component_contributions': {
            'payment_weight': payment_reliability * 0.4,
            'duration_weight': duration_score * 0.3,
            'ecosystem_weight': ecosystem_contribution * 0.3
        }
    }

    return {
        'trust_score': trust_score,
        'risk_multiplier': risk_multiplier,
        'trust_breakdown': trust_breakdown
    }
```

### Payment Reliability Calculation

```python
def calculate_payment_reliability(
    total_payments: int,
    on_time_payments: int,
    late_payments: int,
    very_late_payments: int,
    disputes: int
) -> float:
    """
    Calculate payment reliability score from payment history.

    Returns:
        Float between 0.0 (terrible history) and 1.0 (perfect history)
    """

    if total_payments == 0:
        return 0.0  # No history = no trust

    # Calculate base reliability
    on_time_rate = on_time_payments / total_payments

    # Apply penalties for late payments and disputes
    late_penalty = (late_payments / total_payments) * 0.2
    very_late_penalty = (very_late_payments / total_payments) * 0.5
    dispute_penalty = (disputes / total_payments) * 0.8

    # Calculate final score
    payment_reliability = max(0.0, on_time_rate - late_penalty - very_late_penalty - dispute_penalty)

    return min(1.0, payment_reliability)
```

### Ecosystem Contribution Calculation

```python
def calculate_ecosystem_contribution(
    referrals_generated: int,
    protocol_support_value: float,
    knowledge_shared: bool,
    integration_depth: float
) -> float:
    """
    Calculate ecosystem contribution score.

    Returns:
        Float between 0.0 (no contribution) and 1.0 (maximum contribution)
    """

    # Referral value (40% weight)
    # Assume 5 referrals = maximum referral value
    MAX_REFERRALS = 5
    referral_score = min(1.0, referrals_generated / MAX_REFERRALS)

    # Protocol support value (30% weight)
    # protocol_support_value is already normalized 0-1

    # Knowledge sharing (20% weight)
    knowledge_score = 1.0 if knowledge_shared else 0.0

    # Integration depth (10% weight)
    # integration_depth is already normalized 0-1

    ecosystem_contribution = (
        referral_score * 0.4
        + protocol_support_value * 0.3
        + knowledge_score * 0.2
        + integration_depth * 0.1
    )

    return min(1.0, ecosystem_contribution)
```

## Examples

### Example 1: New Customer (Month 1)

```python
# New customer, first payment
payment_reliability = 0.0  # No history yet
relationship_duration_months = 0
ecosystem_contribution = 0.0  # No contributions yet

trust_score = (0.0 × 0.4) + (0.0 × 0.3) + (0.0 × 0.3) = 0.0
risk_multiplier = 1.8 - (0.0 × 1.2) = 1.8

# New customer pays maximum risk premium (180% of base after other multipliers)
```

### Example 2: Building Trust (Month 6)

```python
# 6 months, good payment history, some contribution
payment_reliability = 0.85  # 6/6 on-time payments, 1 was close to late
relationship_duration_months = 6
duration_score = 6 / 24 = 0.25
ecosystem_contribution = 0.15  # Referred 1 customer

trust_score = (0.85 × 0.4) + (0.25 × 0.3) + (0.15 × 0.3)
trust_score = 0.34 + 0.075 + 0.045 = 0.46

risk_multiplier = 1.8 - (0.46 × 1.2) = 1.8 - 0.55 = 1.25

# Moderate risk reduction (125% vs new customer's 180%)
```

### Example 3: Trusted Customer (Month 12)

```python
# 12 months, perfect payment history, high ecosystem contribution
payment_reliability = 1.0  # 12/12 on-time payments
relationship_duration_months = 12
duration_score = 12 / 24 = 0.5
ecosystem_contribution = 0.65  # 3 referrals, shared case study, integrated APIs

trust_score = (1.0 × 0.4) + (0.5 × 0.3) + (0.65 × 0.3)
trust_score = 0.4 + 0.15 + 0.195 = 0.745

risk_multiplier = 1.8 - (0.745 × 1.2) = 1.8 - 0.894 = 0.906

# Significant risk reduction (91% vs new customer's 180%)
```

### Example 4: Deeply Trusted Partner (Month 24+)

```python
# 24+ months, perfect history, maximum ecosystem value
payment_reliability = 1.0  # Perfect 24+ month history
relationship_duration_months = 24
duration_score = 24 / 24 = 1.0
ecosystem_contribution = 0.95  # 5+ referrals, protocol support, knowledge sharing

trust_score = (1.0 × 0.4) + (1.0 × 0.3) + (0.95 × 0.3)
trust_score = 0.4 + 0.3 + 0.285 = 0.985

risk_multiplier = 1.8 - (0.985 × 1.2) = 1.8 - 1.182 = 0.618

# Near-minimum risk multiplier (62% vs new customer's 180%)
```

### Example 5: Degraded Trust (Late Payments)

```python
# 12 months, but payment issues
total_payments = 12
on_time_payments = 8
late_payments = 3
very_late_payments = 1
disputes = 0

payment_reliability = calculate_payment_reliability(12, 8, 3, 1, 0)
# on_time_rate = 8/12 = 0.667
# late_penalty = (3/12) * 0.2 = 0.05
# very_late_penalty = (1/12) * 0.5 = 0.042
# payment_reliability = 0.667 - 0.05 - 0.042 = 0.575

relationship_duration_months = 12
duration_score = 12 / 24 = 0.5
ecosystem_contribution = 0.3  # Some value, but payment issues hurt

trust_score = (0.575 × 0.4) + (0.5 × 0.3) + (0.3 × 0.3)
trust_score = 0.23 + 0.15 + 0.09 = 0.47

risk_multiplier = 1.8 - (0.47 × 1.2) = 1.8 - 0.564 = 1.236

# Moderate risk (124%) despite 12-month relationship - payment reliability crucial
```

## Edge Cases

### 1. Perfect Trust Score (Theoretical Maximum)

```python
payment_reliability = 1.0
relationship_duration_months = 24
ecosystem_contribution = 1.0

trust_score = (1.0 × 0.4) + (1.0 × 0.3) + (1.0 × 0.3) = 1.0
risk_multiplier = 1.8 - (1.0 × 1.2) = 0.6

# Floor at 0.6 (60% of baseline) - we never go to zero risk
```

### 2. Trust Decay (Customer Returns After Gap)

```python
# Customer had 12-month perfect history, left for 6 months, now returns

# Apply decay factor to previous trust score
previous_trust_score = 0.85
months_absent = 6
decay_rate = 0.05  # 5% decay per month

decayed_trust = previous_trust_score * (1 - (months_absent * decay_rate))
decayed_trust = 0.85 * (1 - 0.3) = 0.595

# Customer returns with trust_score 0.595 instead of 0.0 (new) or 0.85 (if never left)
# Relationship history has memory, but isn't permanent
```

### 3. High Ecosystem Contribution, Poor Payment

```python
payment_reliability = 0.4  # Chronic late payments
relationship_duration_months = 12
duration_score = 0.5
ecosystem_contribution = 0.9  # High referral value, knowledge sharing

trust_score = (0.4 × 0.4) + (0.5 × 0.3) + (0.9 × 0.3)
trust_score = 0.16 + 0.15 + 0.27 = 0.58

risk_multiplier = 1.8 - (0.58 × 1.2) = 1.104

# Ecosystem value helps but doesn't overcome payment issues
# Payment reliability is 40% of score - most important factor
```

### 4. Long Relationship, No Ecosystem Contribution

```python
payment_reliability = 1.0  # Perfect payments
relationship_duration_months = 24
duration_score = 1.0
ecosystem_contribution = 0.0  # Uses service but contributes nothing

trust_score = (1.0 × 0.4) + (1.0 × 0.3) + (0.0 × 0.3)
trust_score = 0.4 + 0.3 + 0.0 = 0.7

risk_multiplier = 1.8 - (0.7 × 1.2) = 0.96

# Still gets significant discount (96% vs 180%) from payment reliability alone
# But not as good as those who also contribute to ecosystem
```

### 5. Dispute Creates Immediate Trust Drop

```python
# Month 11: Perfect history
payment_reliability = 1.0
trust_score = 0.85
risk_multiplier = 0.78

# Month 12: Dispute filed
total_payments = 12
on_time_payments = 11
disputes = 1

payment_reliability = calculate_payment_reliability(12, 11, 0, 0, 1)
# on_time_rate = 11/12 = 0.917
# dispute_penalty = (1/12) * 0.8 = 0.067
# payment_reliability = 0.917 - 0.067 = 0.85

# Trust score drops
trust_score = (0.85 × 0.4) + (0.5 × 0.3) + (0.5 × 0.3) = 0.64
risk_multiplier = 1.8 - (0.64 × 1.2) = 1.032

# Risk multiplier increases from 0.78 to 1.032 (32% penalty)
# Disputes are heavily weighted to protect organizations
```

## Complexity

**Time Complexity:** O(1)
- All operations are constant-time arithmetic
- No database queries in calculation (data provided as inputs)

**Space Complexity:** O(1)
- Fixed number of variables
- Trust breakdown dict has constant size

**Data Requirements:**
- Payment history must be tracked per customer
- Ecosystem contributions must be quantified and stored
- Relationship start date must be recorded


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Organism Economics Formula Application](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
