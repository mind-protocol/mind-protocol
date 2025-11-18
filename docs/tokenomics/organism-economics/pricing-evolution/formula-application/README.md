# ⚙️ Organism Economics Formula Application

**Type:** MECHANISM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Organism Economics](../README.md) > [Pricing Evolution Specification](../README.md)

**This Node:**
- Organism Economics Formula Application (MECHANISM)

**Children:**
- [Effective Price Calculation](./effective-price-calculation/README.md) (ALGORITHM)
- [Trust Score Calculation](./trust-score-calculation/README.md) (ALGORITHM)
- [Utility Rebate Calculation](./utility-rebate-calculation/README.md) (ALGORITHM)
- [How to Price Services with Organism Economics](./how-to-price-services/README.md) (GUIDE)

---

## Relationships

**IMPLEMENTS:**
- Pricing Evolution Specification


---

## Purpose

How to apply the universal pricing formula to calculate effective prices

---

## How It Works

**The organism economics formula application transforms relationship state into effective prices through a 4-step calculation:**

### Step 1: Determine Base Cost

Calculate actual cost to provide the service:

```python
base_cost = (
    consciousness_operation_cost    # Internal energy costs (Layer 1)
    + llm_inference_costs           # External API costs (Claude, GPT-4)
    + infrastructure_costs          # FalkorDB, compute, storage
    + labor_costs                   # Human specialists if needed
    + margin                        # Profit/reserves (typically 15-25%)
)
```

**Base cost is NOT negotiable** - it represents real resource consumption.

### Step 2: Apply Universal Multipliers

Apply complexity, risk, and utility rebate (common to all organizations):

```python
price_after_universal = (
    base_cost
    × complexity_multiplier         # 0.7 (simple) to 2.5 (complex)
    × risk_multiplier               # 0.6 (trusted) to 1.8 (risky)
    × (1 - utility_rebate)          # 0% to 40% rebate
)
```

**These three variables drive most of the pricing evolution over time.**

### Step 3: Apply Organization-Specific Variables

Each organization adds its own context-specific multipliers:

```python
effective_price = (
    price_after_universal
    × [org_specific_variable]       # Varies by organization type
)
```

**Organization-specific variables:**
- **consultingOrg:** `reputation_premium` (1.0 to 2.0)
- **GraphCare:** `load_multiplier` (0.7 to 1.5)
- **scalingOrg:** `(1 - volume_discount)` (0% to 30%)
- **financeOrg:** `urgency_multiplier` (1.0 to 1.8)
- **legalOrg:** `urgency_multiplier` (1.0 to 2.0)
- **securityOrg:** `urgency_multiplier` (1.0 to 1.5)
- **techServiceOrg:** `(1 - familiarity_discount)` (0% to 35%)

### Step 4: Verify Minimum Viable Price

Ensure price doesn't drop below sustainability threshold:

```python
if effective_price < base_cost × 0.4:
    # Price too low - either:
    # 1. Decline service
    # 2. Renegotiate base_cost
    # 3. Reduce discounts
    raise PricingError("Price below minimum viable threshold")
```

**This prevents ecosystem orgs from operating at a loss.**

## Components

### 1. Base Cost Calculator

**Purpose:** Determine real resource consumption

**Inputs:**
- Internal energy costs (from Layer 1 consciousness economy)
- External API costs (LLM providers)
- Infrastructure costs (FalkorDB, hosting)
- Labor costs (human specialists)
- Target margin (15-25%)

**Output:** Base cost in $MIND tokens

**Owner:** financeOrg (calibrates conversion rates and margins)

---

### 2. Complexity Assessor

**Purpose:** Quantify service complexity

**Inputs:**
- Service type (contract review vs complex litigation)
- Customization level (template vs custom)
- Technical difficulty (simple graph vs multi-layer architecture)
- Time required (hours or weeks)

**Output:** Complexity multiplier (0.7 to 2.5)

**Owner:** Service organization (consultingOrg, legalOrg, etc.)

**Examples:**
- Simple NDA review: 0.7
- Standard transformation: 1.2
- Complex IP litigation: 2.5

---

### 3. Trust Score Engine

**Purpose:** Calculate risk multiplier based on relationship history

**Inputs:**
- Payment reliability score (0-1)
- Relationship duration (months)
- Ecosystem contribution score (0-1)

**Output:** Risk multiplier (0.6 to 1.8)

**Owner:** financeOrg (maintains trust scores across ecosystem)

**Formula:**
```python
trust_score = (
    payment_reliability × 0.4
    + relationship_duration × 0.3
    + ecosystem_contribution × 0.3
)

risk_multiplier = 1.8 - (trust_score × 1.2)
# New customer (trust_score=0): risk=1.8
# Trusted customer (trust_score=1): risk=0.6
```

---

### 4. Utility Rebate Calculator

**Purpose:** Quantify ecosystem value contribution

**Inputs:**
- Customer referrals generated
- Protocol contributions (UBC support, L4 validation)
- Knowledge sharing (case studies, documentation)
- Network effects (integration depth)

**Output:** Utility rebate percentage (0% to 40%)

**Owner:** financeOrg (tracks ecosystem contributions)

**Formula:**
```python
ecosystem_contribution_score = (
    referral_value × 0.4          # New customers brought to ecosystem
    + protocol_support × 0.3      # UBC, L4, infrastructure contributions
    + knowledge_sharing × 0.2     # Documentation, case studies
    + network_effects × 0.1       # Integration depth, API usage
)

utility_rebate = ecosystem_contribution_score × 0.4
# No contribution: 0% rebate
# Maximum contribution: 40% rebate
```

---

### 5. Org-Specific Variable Handlers

**Purpose:** Apply context-specific multipliers per organization

**Each organization implements its own handler:**

**consultingOrg - Reputation Premium:**
```python
reputation_premium = 1.0 + (successful_case_studies × 0.1)
# Range: 1.0 (new) to 2.0 (10+ successful transformations)
```

**GraphCare - Load Multiplier:**
```python
load_multiplier = current_capacity_usage / optimal_capacity
# Range: 0.7 (low load) to 1.5 (high demand)
```

**scalingOrg - Volume Discount:**
```python
volume_discount = min(0.3, previous_launches × 0.05)
# Range: 0% (first launch) to 30% (6+ launches)
```

**financeOrg - Urgency Multiplier:**
```python
urgency_multiplier = {
    "normal": 1.0,      # 4-6 weeks
    "rushed": 1.5,      # 2 weeks
    "emergency": 1.8    # Financial crisis, 1 week
}[urgency_level]
```

**legalOrg - Urgency Multiplier:**
```python
urgency_multiplier = {
    "normal": 1.0,           # Standard timeline
    "urgent": 1.5,           # Contract deadline
    "emergency": 2.0         # Rights violation, immediate response
}[urgency_level]
```

**securityOrg - Security Posture Rebate:**
```python
security_posture_rebate = security_audit_score × 0.4
# Range: 0% (unknown) to 40% (excellent history)
```

**techServiceOrg - Familiarity Discount:**
```python
familiarity_discount = min(0.35, similar_projects × 0.07)
# Range: 0% (new pattern) to 35% (5+ similar builds)
```

## Flow Diagram

```
Customer Request
    ↓
[1] Calculate Base Cost
    ├─ Internal energy costs (Layer 1)
    ├─ External API costs
    ├─ Infrastructure costs
    ├─ Labor costs
    └─ Margin (15-25%)
    ↓
[2] Apply Universal Multipliers
    ├─ Complexity (0.7-2.5×)
    ├─ Risk (0.6-1.8×)
    └─ Utility Rebate (0-40%)
    ↓
[3] Apply Org-Specific Variables
    └─ Organization type determines variable
       (reputation, load, volume, urgency, etc.)
    ↓
[4] Verify Minimum Viable Price
    └─ Check: effective_price >= base_cost × 0.4
    ↓
Effective Price (in $MIND tokens)
    ↓
Customer Decision (accept/negotiate/decline)
```

## Integration Points

### With Layer 1 (Internal Consciousness Economy)

**Base cost calculation depends on internal energy costs:**

```python
# Layer 1: Consciousness energy consumption
consciousness_operation_energy = (
    node_activation_count × energy_per_activation
    + working_memory_size × energy_per_wm_slot
    + spreading_activation_hops × energy_per_hop
)

# Convert to $MIND tokens
consciousness_token_cost = (
    consciousness_operation_energy
    × energy_to_token_conversion_rate
)

# Include in base cost
base_cost = consciousness_token_cost + other_costs
```

**financeOrg calibrates energy-to-token conversion rate** to ensure Layer 1 and Layer 2 economic coherence.

### With Trust Score System

**Trust score evolves with each transaction:**

```python
# After successful payment
payment_reliability_score += 0.05
relationship_duration += 1 month
if referral_generated:
    ecosystem_contribution_score += 0.1

# Recalculate trust score
new_trust_score = calculate_trust_score(
    payment_reliability_score,
    relationship_duration,
    ecosystem_contribution_score
)

# Trust score affects next transaction's pricing
next_risk_multiplier = 1.8 - (new_trust_score × 1.2)
```

### With Ecosystem Organizations

**Each org maintains its own pricing variables but uses universal formula:**

```python
# consultingOrg pricing
price = base_cost × complexity × risk × (1 - rebate) × reputation_premium

# GraphCare pricing
price = base_cost × load × risk × (1 - rebate)

# scalingOrg pricing
price = base_cost × complexity × success_prob × (1 - volume_discount)

# All use same trust score and utility rebate systems
# All contribute to protocol giveback (15-20%)
```

### With Protocol Giveback

**Every transaction generates protocol support:**

```python
# Calculate effective price
effective_price = apply_organism_economics_formula(...)

# Customer pays organization
customer → organization: effective_price

# Organization distributes revenue
organization → active_specialists: effective_price × 0.60-0.70
organization → org_treasury: effective_price × 0.15-0.25
organization → protocol_foundation: effective_price × 0.15-0.20

# Protocol foundation allocates giveback
protocol_foundation → UBC: 40% of giveback
protocol_foundation → L4_validation: 20% of giveback
protocol_foundation → development: 20% of giveback
protocol_foundation → governance: 10% of giveback
protocol_foundation → legal_AILLC: 10% of giveback
```

### With Customer Wallets

**Customers hold $MIND tokens and approve transactions:**

```python
# Customer receives quote
quote = organization.calculate_price(service_request)

# Customer approves transaction
customer_wallet.approve(
    spender=organization.wallet,
    amount=quote
)

# Organization charges customer
organization.charge(
    customer=customer_wallet,
    amount=quote,
    service=service_request
)

# Trust score updates automatically after successful charge
trust_system.record_successful_payment(customer)
```


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Pricing Evolution Specification](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
