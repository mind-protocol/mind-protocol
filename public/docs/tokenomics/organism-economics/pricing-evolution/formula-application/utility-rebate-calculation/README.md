# 🔢 Utility Rebate Calculation

**Type:** ALGORITHM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Organism Economics](../README.md) > [Pricing Evolution Specification](../README.md) > [Organism Economics Formula Application](../README.md)

**This Node:**
- Utility Rebate Calculation (ALGORITHM)

**Children:**
- (No children - leaf node)

---

## Relationships

**IMPLEMENTS:**
- Organism Economics Formula Application


---

## Purpose

Formula: utility_rebate = ecosystem_contribution_score × max_rebate_percentage (0-40%)

---

## Algorithm

**Utility rebate calculation quantifies customer's ecosystem value contribution and converts it to a price discount (0-40%).**

### Algorithm Steps

1. **Quantify referral value** - New customers brought to ecosystem
2. **Quantify protocol support** - UBC contributions, L4 validation participation
3. **Quantify knowledge sharing** - Case studies, documentation, testimonials
4. **Quantify network effects** - Integration depth, API usage
5. **Combine into ecosystem contribution score** (0-1)
6. **Convert to utility rebate percentage** (0-40%)

## Inputs

| Input | Type | Range | Description |
|-------|------|-------|-------------|
| `referrals_generated` | int | 0 - ∞ | Count of new customers referred to ecosystem |
| `protocol_support_value` | float | 0.0 - 1.0 | Normalized value of protocol contributions |
| `knowledge_shared` | bool | true/false | Whether customer has shared knowledge (case studies, docs) |
| `integration_depth` | float | 0.0 - 1.0 | How deeply customer integrates with ecosystem |

**Referral Sub-Inputs:**
- `referral_count` | int | Total referrals generated
- `referral_conversion_rate` | float | % of referrals that became paying customers
- `referral_revenue_value` | float | Total revenue from referred customers

**Protocol Support Sub-Inputs:**
- `ubc_contributions` | float | $MIND contributed to UBC pool
- `l4_validation_participation` | bool | Whether customer participates in L4 validation
- `governance_participation` | bool | Whether customer participates in DAO governance

**Knowledge Sharing Sub-Inputs:**
- `case_studies_published` | int | Count of public case studies
- `documentation_contributed` | bool | Whether customer contributed documentation
- `testimonials_provided` | bool | Whether customer provided testimonials

**Integration Depth Sub-Inputs:**
- `api_calls_per_month` | int | How actively customer uses ecosystem APIs
- `services_used` | int | Count of different ecosystem services used
- `data_shared` | bool | Whether customer shares data for ecosystem improvement

## Outputs

| Output | Type | Range | Description |
|--------|------|-------|-------------|
| `ecosystem_contribution_score` | float | 0.0 - 1.0 | Combined ecosystem value score |
| `utility_rebate` | float | 0.0 - 0.4 | Price discount percentage (0% to 40%) |
| `contribution_breakdown` | dict | - | Detailed breakdown of contribution components |

## Formula

### Core Utility Rebate Formula

```python
def calculate_utility_rebate(
    referrals_generated: int,
    protocol_support_value: float,
    knowledge_shared: bool,
    integration_depth: float,
    max_rebate_percentage: float = 0.4
) -> dict:
    """
    Calculate utility rebate from ecosystem contribution.

    Args:
        referrals_generated: Count of new customers referred
        protocol_support_value: Protocol contribution score (0-1)
        knowledge_shared: Whether customer shared knowledge
        integration_depth: Integration depth score (0-1)
        max_rebate_percentage: Maximum rebate (default 40%)

    Returns:
        {
            'ecosystem_contribution_score': float,
            'utility_rebate': float,
            'contribution_breakdown': dict
        }
    """

    # Step 1: Calculate referral score
    # Assume 5 referrals = maximum referral value
    MAX_REFERRALS = 5
    referral_score = min(1.0, referrals_generated / MAX_REFERRALS)

    # Step 2: Protocol support value (already normalized 0-1)
    protocol_score = protocol_support_value

    # Step 3: Knowledge sharing score
    knowledge_score = 1.0 if knowledge_shared else 0.0

    # Step 4: Integration depth (already normalized 0-1)
    integration_score = integration_depth

    # Step 5: Calculate weighted ecosystem contribution score
    ecosystem_contribution_score = (
        referral_score * 0.4         # 40% weight - most valuable
        + protocol_score * 0.3        # 30% weight - second most valuable
        + knowledge_score * 0.2       # 20% weight
        + integration_score * 0.1     # 10% weight
    )

    # Step 6: Convert to utility rebate (max 40%)
    utility_rebate = ecosystem_contribution_score * max_rebate_percentage

    # Step 7: Build detailed breakdown
    contribution_breakdown = {
        'referrals_generated': referrals_generated,
        'referral_score': referral_score,
        'protocol_support_value': protocol_support_value,
        'knowledge_shared': knowledge_shared,
        'integration_depth': integration_depth,
        'component_contributions': {
            'referral_weight': referral_score * 0.4,
            'protocol_weight': protocol_score * 0.3,
            'knowledge_weight': knowledge_score * 0.2,
            'integration_weight': integration_score * 0.1
        }
    }

    return {
        'ecosystem_contribution_score': ecosystem_contribution_score,
        'utility_rebate': utility_rebate,
        'contribution_breakdown': contribution_breakdown
    }
```

### Referral Value Calculation

```python
def calculate_referral_score(
    referral_count: int,
    referral_conversion_rate: float,
    referral_revenue_value: float
) -> float:
    """
    Calculate referral score from referral metrics.

    Returns:
        Float between 0.0 (no referrals) and 1.0 (maximum referral value)
    """

    if referral_count == 0:
        return 0.0

    # Base score from count
    MAX_REFERRALS = 5
    count_score = min(1.0, referral_count / MAX_REFERRALS)

    # Bonus for high conversion rate (referrals that actually convert)
    conversion_bonus = referral_conversion_rate * 0.3

    # Bonus for high revenue value (quality referrals)
    # Assume $10K revenue per referral = excellent
    AVG_REVENUE_PER_REFERRAL = 10_000
    revenue_per_referral = referral_revenue_value / referral_count
    revenue_bonus = min(0.3, revenue_per_referral / AVG_REVENUE_PER_REFERRAL)

    # Combine scores (max 1.0)
    referral_score = min(1.0, count_score + conversion_bonus + revenue_bonus)

    return referral_score
```

### Protocol Support Calculation

```python
def calculate_protocol_support(
    ubc_contributions: float,
    l4_validation_participation: bool,
    governance_participation: bool
) -> float:
    """
    Calculate protocol support value.

    Returns:
        Float between 0.0 (no support) and 1.0 (maximum support)
    """

    # UBC contributions (50% weight)
    # Assume 10,000 $MIND contributed = excellent
    UBC_EXCELLENT = 10_000
    ubc_score = min(1.0, ubc_contributions / UBC_EXCELLENT)

    # L4 validation participation (30% weight)
    l4_score = 1.0 if l4_validation_participation else 0.0

    # Governance participation (20% weight)
    governance_score = 1.0 if governance_participation else 0.0

    protocol_support = (
        ubc_score * 0.5
        + l4_score * 0.3
        + governance_score * 0.2
    )

    return min(1.0, protocol_support)
```

### Integration Depth Calculation

```python
def calculate_integration_depth(
    api_calls_per_month: int,
    services_used: int,
    data_shared: bool
) -> float:
    """
    Calculate integration depth score.

    Returns:
        Float between 0.0 (no integration) and 1.0 (deep integration)
    """

    # API usage (50% weight)
    # Assume 10,000 API calls/month = deep integration
    API_DEEP_INTEGRATION = 10_000
    api_score = min(1.0, api_calls_per_month / API_DEEP_INTEGRATION)

    # Service diversity (30% weight)
    # Assume 5 different services = maximum diversity
    MAX_SERVICES = 5
    services_score = min(1.0, services_used / MAX_SERVICES)

    # Data sharing (20% weight)
    data_score = 1.0 if data_shared else 0.0

    integration_depth = (
        api_score * 0.5
        + services_score * 0.3
        + data_score * 0.2
    )

    return min(1.0, integration_depth)
```

## Examples

### Example 1: New Customer (No Contribution)

```python
referrals_generated = 0
protocol_support_value = 0.0
knowledge_shared = False
integration_depth = 0.0

ecosystem_contribution_score = (0.0 × 0.4) + (0.0 × 0.3) + (0.0 × 0.2) + (0.0 × 0.1) = 0.0
utility_rebate = 0.0 × 0.4 = 0% rebate

# New customer pays full price (no discount)
```

### Example 2: Light Contributor (Month 6)

```python
referrals_generated = 1
referral_score = 1/5 = 0.2
protocol_support_value = 0.1  # Small UBC contribution
knowledge_shared = False
integration_depth = 0.2  # Using APIs, single service

ecosystem_contribution_score = (0.2 × 0.4) + (0.1 × 0.3) + (0.0 × 0.2) + (0.2 × 0.1)
ecosystem_contribution_score = 0.08 + 0.03 + 0.0 + 0.02 = 0.13

utility_rebate = 0.13 × 0.4 = 0.052 = 5.2% rebate
```

### Example 3: Significant Contributor (Month 12)

```python
referrals_generated = 3
referral_score = 3/5 = 0.6
protocol_support_value = 0.5  # UBC + governance participation
knowledge_shared = True  # Published case study
integration_depth = 0.6  # Heavy API usage, multiple services

ecosystem_contribution_score = (0.6 × 0.4) + (0.5 × 0.3) + (1.0 × 0.2) + (0.6 × 0.1)
ecosystem_contribution_score = 0.24 + 0.15 + 0.2 + 0.06 = 0.65

utility_rebate = 0.65 × 0.4 = 0.26 = 26% rebate
```

### Example 4: Maximum Contributor (Ecosystem Champion)

```python
referrals_generated = 5+  # Maximum
referral_score = 1.0
protocol_support_value = 0.95  # Heavy UBC, L4 validation, governance
knowledge_shared = True  # Multiple case studies, documentation
integration_depth = 0.9  # Deep integration across all services

ecosystem_contribution_score = (1.0 × 0.4) + (0.95 × 0.3) + (1.0 × 0.2) + (0.9 × 0.1)
ecosystem_contribution_score = 0.4 + 0.285 + 0.2 + 0.09 = 0.975

utility_rebate = 0.975 × 0.4 = 0.39 = 39% rebate (near maximum 40%)
```

### Example 5: High Referrals, No Protocol Support

```python
referrals_generated = 5
referral_score = 1.0
protocol_support_value = 0.0  # No UBC, no governance
knowledge_shared = False
integration_depth = 0.3  # Moderate API usage

ecosystem_contribution_score = (1.0 × 0.4) + (0.0 × 0.3) + (0.0 × 0.2) + (0.3 × 0.1)
ecosystem_contribution_score = 0.4 + 0.0 + 0.0 + 0.03 = 0.43

utility_rebate = 0.43 × 0.4 = 0.172 = 17.2% rebate

# Strong referral value but lack of protocol support limits rebate
```

### Example 6: Protocol Champion, No Referrals

```python
referrals_generated = 0
referral_score = 0.0
protocol_support_value = 1.0  # Maximum UBC + L4 + governance
knowledge_shared = True  # Documentation contributor
integration_depth = 0.8  # Deep integration

ecosystem_contribution_score = (0.0 × 0.4) + (1.0 × 0.3) + (1.0 × 0.2) + (0.8 × 0.1)
ecosystem_contribution_score = 0.0 + 0.3 + 0.2 + 0.08 = 0.58

utility_rebate = 0.58 × 0.4 = 0.232 = 23.2% rebate

# Strong protocol support but lack of referrals limits rebate
```

## Edge Cases

### 1. Referrals That Don't Convert

```python
referral_count = 10
referral_conversion_rate = 0.1  # Only 10% converted
referral_revenue_value = 1_000  # Low revenue from referrals

# High count but low quality
referral_score = calculate_referral_score(10, 0.1, 1000)
# count_score = 1.0 (10 > 5)
# conversion_bonus = 0.1 * 0.3 = 0.03
# revenue_bonus = (1000/10) / 10000 = 0.01
# referral_score = min(1.0, 1.0 + 0.03 + 0.01) = 1.0

# Still gets credit for volume, but conversion/revenue bonuses are small
```

### 2. Negative Contribution (Customer Causes Issues)

```python
# Customer referred 3 customers, but also filed dispute
# Disputes affect trust score, not utility rebate
# Utility rebate only measures positive contributions

referrals_generated = 3
utility_rebate = calculate_utility_rebate(3, 0, False, 0)
# Still gets 4.8% rebate for referrals

# BUT: dispute affects trust score → higher risk multiplier
# Net effect: utility rebate reduces price, but risk multiplier increases it
```

### 3. Huge Referral Count (Outlier)

```python
referrals_generated = 20  # Far beyond typical
referral_score = min(1.0, 20 / 5) = 1.0  # Capped at 1.0

# Ecosystem contribution score still capped:
ecosystem_contribution_score = (1.0 × 0.4) + ...  # Max contribution from referrals: 0.4
utility_rebate = max 40%

# Prevents single dimension from dominating
```

### 4. Knowledge Shared But No Other Contribution

```python
referrals_generated = 0
protocol_support_value = 0.0
knowledge_shared = True  # Only contribution
integration_depth = 0.0

ecosystem_contribution_score = (0.0 × 0.4) + (0.0 × 0.3) + (1.0 × 0.2) + (0.0 × 0.1) = 0.2
utility_rebate = 0.2 × 0.4 = 0.08 = 8% rebate

# Knowledge sharing alone worth 8% discount
```

### 5. Deep Integration But No Value Sharing

```python
referrals_generated = 0
protocol_support_value = 0.0
knowledge_shared = False
integration_depth = 1.0  # Heavy API user

ecosystem_contribution_score = (0.0 × 0.4) + (0.0 × 0.3) + (0.0 × 0.2) + (1.0 × 0.1) = 0.1
utility_rebate = 0.1 × 0.4 = 0.04 = 4% rebate

# Using ecosystem heavily but not contributing back = small rebate
```

### 6. Utility Rebate vs Security Posture Rebate

```python
# securityOrg uses security_posture_rebate INSTEAD OF utility_rebate
# Different formula, same 0-40% range

# consultingOrg pricing:
price = base_cost × complexity × risk × (1 - utility_rebate) × reputation

# securityOrg pricing:
price = base_cost × complexity × risk × (1 - security_posture_rebate) × urgency

# Both rebates are ecosystem value measures, but measure different things:
# - utility_rebate: referrals, protocol support, knowledge sharing
# - security_posture_rebate: security audit scores, implementation of recommendations
```

## Complexity

**Time Complexity:** O(1)
- All operations are constant-time arithmetic
- No loops or database queries

**Space Complexity:** O(1)
- Fixed number of variables
- Contribution breakdown dict has constant size

**Data Requirements:**
- Referral tracking system (who referred whom, conversion rates, revenue)
- Protocol contribution tracking (UBC, L4 validation, governance)
- Knowledge sharing tracking (case studies, docs, testimonials)
- Integration metrics (API calls, services used, data sharing)


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Organism Economics Formula Application](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
