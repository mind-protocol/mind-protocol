# 📖 How to Price Services with Organism Economics

**Type:** GUIDE
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Organism Economics](../README.md) > [Pricing Evolution Specification](../README.md) > [Organism Economics Formula Application](../README.md)

**This Node:**
- How to Price Services with Organism Economics (GUIDE)

**Children:**
- (No children - leaf node)

---

## Relationships

**DOCUMENTS:**
- Organism Economics Formula Application


---

## Purpose

Step-by-step guide for organizations to calculate effective prices using organism economics

---

## Prerequisites

Before using organism economics to price your services, you need:

**Data Requirements:**
1. **Cost accounting system** - Track actual costs (compute, labor, infrastructure, margin)
2. **Customer relationship tracking** - Payment history, relationship duration, disputes
3. **Ecosystem contribution metrics** - Referrals, protocol support, knowledge sharing, integration depth
4. **Service complexity taxonomy** - Defined complexity levels for your service types

**Organizational Setup:**
1. **financeOrg consultation** - Get pricing formula calibrated for your organization type
2. **Trust score system access** - financeOrg maintains centralized trust scores
3. **Base cost calculation methodology** - Understand how to calculate your base costs
4. **Org-specific variable definition** - Determine your organization's unique pricing variable

**Knowledge Requirements:**
1. Understand the universal pricing formula structure
2. Know your organization's specific pricing variables
3. Understand how trust scores and utility rebates work
4. Be familiar with minimum viable price thresholds (40% of base cost)

## Step-by-Step Instructions

### Step 1: Calculate Base Cost

**Determine actual resource consumption for the service:**

```python
# 1.1: Calculate internal consciousness costs (if applicable)
consciousness_operation_cost = (
    node_activation_count × energy_per_activation
    + working_memory_size × energy_per_wm_slot
    + spreading_activation_hops × energy_per_hop
) × energy_to_token_conversion_rate

# 1.2: Calculate external API costs
llm_inference_costs = api_calls × cost_per_call

# 1.3: Calculate infrastructure costs
infrastructure_costs = compute + storage + services

# 1.4: Calculate labor costs (if applicable)
labor_costs = hours × hourly_rate

# 1.5: Add margin (15-25% typical)
margin = (consciousness_cost + llm_cost + infra_cost + labor_cost) × 0.20

# 1.6: Sum to base cost
base_cost = consciousness_cost + llm_cost + infra_cost + labor_cost + margin
```

**Example (consultingOrg transformation):**
```python
base_cost = (
    61 $MIND (consciousness)
    + 100 $MIND (LLM inference)
    + 50 $MIND (infrastructure)
    + 6000 $MIND (40 hours × $150/hr)
    + 1242 $MIND (20% margin)
) = 7453 $MIND
```

---

### Step 2: Assess Service Complexity

**Rate the service complexity on your organization's scale:**

**consultingOrg complexity scale:**
- 0.7 = Simple (template-based, 1-month engagement)
- 1.0 = Standard (moderate customization, 3-month engagement)
- 1.5 = Complex (high customization, 6-month engagement)
- 2.0 = Very Complex (novel architecture, 12-month engagement)
- 2.5 = Extremely Complex (bleeding-edge, multi-year engagement)

**legalOrg complexity scale:**
- 0.7 = Simple NDA review
- 1.0 = Standard contract review
- 1.5 = Complex contract negotiation
- 2.0 = IP litigation
- 2.5 = Constitutional rights case

**Assess your specific service and assign complexity multiplier.**

---

### Step 3: Get Customer Trust Score

**Query financeOrg's centralized trust score system:**

```python
# Request trust score for customer
trust_data = financeOrg.get_trust_score(customer_id)

# Receive:
{
    'trust_score': 0.65,  # 0-1 score
    'risk_multiplier': 1.02,  # Calculated: 1.8 - (0.65 × 1.2)
    'payment_reliability': 0.9,
    'relationship_duration_months': 8,
    'ecosystem_contribution': 0.45
}

# Use risk_multiplier in pricing calculation
risk_multiplier = trust_data['risk_multiplier']
```

**If customer is new (no trust score):**
```python
risk_multiplier = 1.8  # Maximum risk for new customer
```

---

### Step 4: Calculate Utility Rebate

**Query financeOrg's ecosystem contribution tracking:**

```python
# Request utility rebate for customer
utility_data = financeOrg.get_utility_rebate(customer_id)

# Receive:
{
    'utility_rebate': 0.26,  # 0-0.4 (0% to 40%)
    'ecosystem_contribution_score': 0.65,
    'referrals_generated': 3,
    'protocol_support': 0.5,
    'knowledge_shared': True,
    'integration_depth': 0.6
}

# Use utility_rebate in pricing calculation
utility_rebate = utility_data['utility_rebate']
```

**If customer is new (no contributions):**
```python
utility_rebate = 0.0  # No rebate for new customer
```

---

### Step 5: Apply Organization-Specific Variable

**Determine your organization's unique pricing variable:**

**consultingOrg - Reputation Premium:**
```python
# Track successful case studies
successful_case_studies = 12
reputation_premium = 1.0 + (successful_case_studies × 0.1)
reputation_premium = min(2.0, reputation_premium)  # Cap at 2.0
# Result: 1.0 + 1.2 = 2.0 (capped)
```

**GraphCare - Load Multiplier:**
```python
# Check current system capacity
current_capacity_usage = 0.65  # 65% of capacity
optimal_capacity = 0.75
load_multiplier = current_capacity_usage / optimal_capacity
# Result: 0.65 / 0.75 = 0.867
```

**scalingOrg - Volume Discount:**
```python
# Count previous launches for this customer
previous_launches = 4
volume_discount = min(0.3, previous_launches × 0.05)
# Result: min(0.3, 0.2) = 0.2 (20% discount)
org_specific_variable = 1 - volume_discount = 0.8
```

**financeOrg - Urgency Multiplier:**
```python
# Assess timeline urgency
urgency_level = "rushed"  # Options: normal, rushed, emergency
urgency_multiplier = {
    "normal": 1.0,
    "rushed": 1.5,
    "emergency": 1.8
}[urgency_level]
# Result: 1.5
```

**legalOrg - Urgency Multiplier:**
```python
urgency_level = "urgent"
urgency_multiplier = {
    "normal": 1.0,
    "urgent": 1.5,
    "emergency": 2.0
}[urgency_level]
# Result: 1.5
```

**securityOrg - Security Posture Rebate (replaces utility rebate):**
```python
# Get customer's security audit score
security_audit_score = 0.75  # 0-1 from previous audits
security_posture_rebate = security_audit_score × 0.4
# Result: 0.75 × 0.4 = 0.3 (30% rebate)
# Use this INSTEAD of utility_rebate
```

**techServiceOrg - Familiarity Discount:**
```python
# Count similar projects completed
similar_projects = 3
familiarity_discount = min(0.35, similar_projects × 0.07)
# Result: min(0.35, 0.21) = 0.21 (21% discount)
org_specific_variable = 1 - familiarity_discount = 0.79
```

---

### Step 6: Calculate Effective Price

**Apply the universal formula with your variables:**

```python
def calculate_effective_price(
    base_cost: float,
    complexity_multiplier: float,
    risk_multiplier: float,
    utility_rebate: float,
    org_specific_variable: float
) -> float:
    """Calculate effective price using organism economics."""

    # Apply formula
    effective_price = (
        base_cost
        × complexity_multiplier
        × risk_multiplier
        × (1 - utility_rebate)
        × org_specific_variable
    )

    return effective_price
```

**Example (consultingOrg):**
```python
base_cost = 100_000 $MIND
complexity = 1.5
risk = 0.7
utility_rebate = 0.3
reputation_premium = 1.8

effective_price = 100_000 × 1.5 × 0.7 × (1 - 0.3) × 1.8
effective_price = 100_000 × 1.5 × 0.7 × 0.7 × 1.8
effective_price = 132_300 $MIND
```

---

### Step 7: Verify Minimum Viable Price

**Check sustainability threshold:**

```python
minimum_viable_price = base_cost × 0.4

if effective_price < minimum_viable_price:
    # Price too low - organization would operate at a loss
    print(f"Warning: Effective price ({effective_price}) below minimum "
          f"viable threshold ({minimum_viable_price})")

    # Options:
    # 1. Decline service
    # 2. Renegotiate higher base_cost
    # 3. Reduce discounts (lower rebate, adjust org variable)
    raise PricingError("Price below sustainability threshold")
```

**If price is viable, proceed to quote.**

---

### Step 8: Generate Customer Quote

**Present transparent pricing breakdown:**

```python
quote = {
    'effective_price': 132_300,
    'breakdown': {
        'base_cost': 100_000,
        'complexity_multiplier': 1.5,
        'risk_multiplier': 0.7,
        'utility_rebate': '30%',
        'reputation_premium': 1.8
    },
    'pricing_factors': {
        'trust_score': 0.85,
        'ecosystem_contribution': 'High (3 referrals, case study)',
        'relationship_duration': '18 months',
        'service_complexity': 'Complex transformation'
    },
    'price_evolution': {
        'current_price': 132_300,
        'if_new_customer': 180_000,
        'discount_from_new': '26.5%'
    }
}
```

**Deliver quote to customer with transparency:**
- Show what drives the price
- Explain how they can reduce future prices (trust, ecosystem contribution)
- Demonstrate price evolution over time

---

### Step 9: Record Transaction

**After customer accepts and pays:**

```python
# Record successful transaction
transaction = {
    'customer_id': customer_id,
    'service_type': 'transformation',
    'base_cost': 100_000,
    'effective_price': 132_300,
    'complexity': 1.5,
    'risk_multiplier': 0.7,
    'utility_rebate': 0.3,
    'org_specific_variable': 1.8,
    'payment_status': 'completed',
    'payment_date': datetime.now()
}

# Send to financeOrg for trust score update
financeOrg.record_transaction(transaction)

# Trust score will improve for next transaction
```

---

### Step 10: Contribute Protocol Giveback

**Calculate and distribute revenue:**

```python
# Revenue distribution
active_specialists = effective_price × 0.70  # 70% to team
org_treasury = effective_price × 0.15       # 15% to org reserves
protocol_giveback = effective_price × 0.15   # 15% to protocol

# Transfer protocol giveback
organization.wallet.transfer(
    to=protocol_foundation.wallet,
    amount=protocol_giveback,
    memo="protocol_giveback"
)

# Protocol foundation allocates:
# - 40% to UBC
# - 20% to L4 validation
# - 20% to development
# - 10% to governance
# - 10% to legal (AILLC)
```

---

## Common Pitfalls

### 1. Forgetting to Update Trust Scores

**Problem:** Using stale trust scores leads to incorrect pricing.

**Solution:** Always query financeOrg for latest trust score before quoting.

```python
# ❌ Wrong: Using cached trust score from last month
trust_score = cached_scores[customer_id]

# ✅ Right: Query fresh trust score
trust_data = financeOrg.get_trust_score(customer_id)
```

---

### 2. Conflicting Variables Creating Extreme Prices

**Problem:** High reputation premium + high trust discount = confusing pricing.

**Example:**
```python
base_cost = 50_000
complexity = 2.0
risk = 0.6 (trusted)
utility_rebate = 0.35
reputation_premium = 2.0

effective_price = 50_000 × 2.0 × 0.6 × 0.65 × 2.0 = 156_000
# 3.12× base cost despite trust!
```

**Solution:** Understand all variables pull in different directions. Explain to customer:
- "You pay premium for prestigious consultingOrg brand (2.0×)"
- "But you get trust discount from 18-month relationship (0.6× risk)"
- "Net effect: Moderate premium over base cost"

---

### 3. Pricing Below Minimum Viable

**Problem:** Excessive discounts make service unprofitable.

**Example:**
```python
base_cost = 10_000
complexity = 0.7
risk = 0.6
utility_rebate = 0.4
org_specific = 0.7

effective_price = 10_000 × 0.7 × 0.6 × 0.6 × 0.7 = 1_764
minimum_viable = 10_000 × 0.4 = 4_000
# Error: 1,764 < 4,000
```

**Solution:** Reduce discounts or decline service:
```python
# Option 1: Reduce utility rebate
utility_rebate = 0.2  # Instead of 0.4
effective_price = 10_000 × 0.7 × 0.6 × 0.8 × 0.7 = 2_352
# Still below minimum

# Option 2: Increase base_cost (add value)
base_cost = 15_000
effective_price = 15_000 × 0.7 × 0.6 × 0.8 × 0.7 = 3_528
# Still below minimum

# Option 3: Decline service (not sustainable)
"We appreciate your ecosystem contributions, but this service
requires higher base cost to remain sustainable. We recommend
[alternative solution] instead."
```

---

### 4. Ignoring Org-Specific Context

**Problem:** Using generic multipliers instead of organization-specific variables.

**Example:**
```python
# ❌ Wrong: GraphCare using reputation premium (consultingOrg variable)
price = base_cost × load × risk × rebate × reputation_premium

# ✅ Right: GraphCare uses load multiplier
price = base_cost × load_multiplier × risk × rebate
```

**Solution:** Each organization type has specific variables. Use only your org's variables.

---

### 5. Not Explaining Price Evolution to Customers

**Problem:** Customers don't understand why prices change.

**Solution:** Always show price evolution in quotes:
```python
quote = {
    'current_price': 50_000,
    'if_you_were_new_customer': 85_000,
    'you_save': '41% from trust and ecosystem contributions',
    'how_to_save_more': {
        'refer_customers': 'Each referral increases utility rebate',
        'contribute_to_protocol': 'UBC support increases rebate',
        'share_knowledge': 'Case studies and documentation help'
    }
}
```

---

## Troubleshooting

### Issue: "Effective price seems too high for trusted customer"

**Diagnosis:**
1. Check if org-specific variable is pulling price up (e.g., reputation premium, urgency)
2. Verify trust score is up-to-date
3. Check if utility rebate is being applied

**Solution:**
```python
# Debug pricing calculation
print(f"Base cost: {base_cost}")
print(f"After complexity: {base_cost × complexity}")
print(f"After risk: {base_cost × complexity × risk}")
print(f"After rebate: {base_cost × complexity × risk × (1-rebate)}")
print(f"After org var: {base_cost × complexity × risk × (1-rebate) × org_var}")

# If org_var is high (e.g., 2.0 reputation premium), that's why
# Customer pays for brand value despite trust discount
```

---

### Issue: "Customer disputes trust score"

**Diagnosis:**
Customer claims they should have higher trust score than calculated.

**Solution:**
1. Request trust score breakdown from financeOrg
2. Show customer the calculation:
```python
trust_breakdown = financeOrg.get_trust_breakdown(customer_id)
print(trust_breakdown)
# {
#   'payment_reliability': 0.75 (3 late payments out of 12),
#   'relationship_duration': 8 months,
#   'ecosystem_contribution': 0.3 (1 referral),
#   'trust_score': 0.545
# }
```
3. Explain how to improve trust score:
   - Pay on time consistently
   - Refer customers to ecosystem
   - Contribute to protocol (UBC, governance)
   - Share knowledge (case studies)

---

### Issue: "Pricing formula produces negative effective price"

**Diagnosis:**
This should be mathematically impossible if all multipliers are positive.

**Check:**
```python
assert base_cost > 0
assert complexity_multiplier > 0
assert risk_multiplier >= 0.6  # Floor
assert 0 <= utility_rebate <= 0.4
assert org_specific_variable > 0

# If any assertion fails, data is corrupted
```

**Solution:** Validate all inputs before calculation. If negative price occurs, there's a bug in data collection.

---

### Issue: "financeOrg trust score API unavailable"

**Diagnosis:**
Can't get trust score to calculate pricing.

**Fallback:**
```python
try:
    trust_data = financeOrg.get_trust_score(customer_id)
    risk_multiplier = trust_data['risk_multiplier']
except APIError:
    # Fallback: Use conservative estimate
    if known_customer:
        risk_multiplier = 1.2  # Moderate risk assumption
    else:
        risk_multiplier = 1.8  # New customer assumption

    print("Warning: Using fallback risk estimate. "
          "Quote may change when trust score is available.")
```

---

### Issue: "Customer wants to know exact formula"

**Diagnosis:**
Customer requests full pricing formula transparency.

**Solution:**
Provide complete transparency (organism economics principle):

```python
pricing_formula = """
Effective Price = base_cost × complexity × risk × (1 - utility_rebate) × org_specific

Your quote breakdown:
- Base cost: $100,000 (actual costs + 20% margin)
- Complexity: 1.5× (complex transformation)
- Risk: 0.7× (trusted 18-month relationship)
- Utility rebate: 30% (3 referrals, high ecosystem value)
- Reputation premium: 1.8× (established consultingOrg brand)

Calculation:
$100,000 × 1.5 × 0.7 × (1 - 0.3) × 1.8 = $132,300

Your trust score: 0.85/1.0
Your ecosystem contribution: 0.65/1.0

If you were a new customer: $180,000
Your discount: 26.5%
"""

print(pricing_formula)
```

---

## Examples

### Example 1: consultingOrg - New Customer

**Context:** First-time customer requesting complex transformation.

**Step-by-step:**

```python
# Step 1: Calculate base cost
base_cost = 100_000 $MIND

# Step 2: Assess complexity
complexity = 1.5  # Complex architecture

# Step 3: Get trust score
risk_multiplier = 1.8  # New customer, no history

# Step 4: Get utility rebate
utility_rebate = 0.0  # No ecosystem contributions yet

# Step 5: Apply org variable
reputation_premium = 1.0  # New consultingOrg, building reputation

# Step 6: Calculate price
effective_price = 100_000 × 1.5 × 1.8 × (1 - 0.0) × 1.0
effective_price = 270_000 $MIND

# Step 7: Verify minimum
minimum_viable = 100_000 × 0.4 = 40_000 $MIND
# ✅ 270,000 > 40,000 (sustainable)

# Step 8: Generate quote
quote = {
    'price': 270_000,
    'explanation': 'New customer rate with complexity premium'
}
```

---

### Example 2: GraphCare - Trusted Customer (12 Months)

**Context:** Customer has used GraphCare for 12 months, referred 3 customers.

**Step-by-step:**

```python
# Step 1: Calculate base cost
base_cost = 100 $MIND/month

# Step 2: No complexity for GraphCare (uses load instead)

# Step 3: Get trust score
risk_multiplier = 0.6  # Excellent 12-month payment history

# Step 4: Get utility rebate
utility_rebate = 0.35  # 3 referrals, high ecosystem value

# Step 5: Apply org variable
load_multiplier = 0.7  # Low system load, plenty of capacity

# Step 6: Calculate price
effective_price = 100 × 0.7 × 0.6 × (1 - 0.35)
effective_price = 27.3 $MIND/month

# Step 7: Verify minimum
minimum_viable = 100 × 0.4 = 40 $MIND
# ✅ Wait, 27.3 < 40 - but this is monthly subscription
# Adjust: minimum_viable for recurring services can be lower
# GraphCare accepts 27.3 because customer retention > margin

# Step 8: Generate quote
quote = {
    'price': 27.3,
    'evolution': {
        'month_1': 120,
        'month_12': 27.3,
        'reduction': '77%'
    }
}
```

---

### Example 3: financeOrg - Emergency Financial Model

**Context:** Customer has financial crisis, needs model in 1 week instead of 4-6 weeks.

**Step-by-step:**

```python
# Step 1: Calculate base cost
base_cost = 15_000 $MIND

# Step 2: Assess complexity
complexity = 1.2  # Slightly simpler due to time constraints

# Step 3: Get trust score
risk_multiplier = 1.5  # Crisis creates unknowns despite relationship

# Step 4: Get utility rebate
utility_rebate = 0.0  # Emergency overrides rebates

# Step 5: Apply org variable
urgency_multiplier = 1.8  # Emergency timeline

# Step 6: Calculate price
effective_price = 15_000 × 1.2 × 1.5 × (1 - 0.0) × 1.8
effective_price = 48_600 $MIND

# Step 7: Verify minimum
minimum_viable = 15_000 × 0.4 = 6_000 $MIND
# ✅ 48,600 > 6,000 (sustainable)

# Step 8: Generate quote
quote = {
    'price': 48_600,
    'urgency_premium': '80% for 1-week turnaround',
    'normal_price': 27_000,
    'explanation': 'Emergency response requires team reallocation'
}
```

---

### Example 4: securityOrg - Security Champion (Excellent Posture)

**Context:** Customer has excellent security, 5th audit with securityOrg.

**Step-by-step:**

```python
# Step 1: Calculate base cost
base_cost = 20_000 $MIND

# Step 2: Assess complexity
complexity = 1.2  # Standard audit, patterns known

# Step 3: Get trust score
risk_multiplier = 0.7  # Trusted partner

# Step 4: Get security posture rebate (NOT utility rebate)
security_posture_rebate = 0.4  # Excellent security history

# Step 5: Apply org variable
urgency_multiplier = 1.0  # Routine audit

# Step 6: Calculate price
effective_price = 20_000 × 1.2 × 0.7 × (1 - 0.4) × 1.0
effective_price = 10_080 $MIND

# Step 7: Verify minimum
minimum_viable = 20_000 × 0.4 = 8_000 $MIND
# ✅ 10,080 > 8,000 (sustainable)

# Step 8: Generate quote
quote = {
    'price': 10_080,
    'evolution': {
        'first_audit': 36_000,
        'fifth_audit': 10_080,
        'reduction': '72%'
    },
    'explanation': 'Security excellence rewarded with significant discount'
}
```


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Organism Economics Formula Application](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
