# 📋 financeOrg Two-Layer Management

**Type:** BEHAVIOR_SPEC
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Two-Layer Economic Architecture](../README.md)

**This Node:**
- financeOrg Two-Layer Management (BEHAVIOR_SPEC)

**Children:**
- [How financeOrg Manages Both Layers](./how-to-manage-both-layers/README.md) (GUIDE)

---

## Relationships

**EXTENDS:**
- Two-Layer Economic Architecture (PATTERN)


---

## Purpose

Specifies how financeOrg manages both energy calibration (Layer 1) and pricing strategy (Layer 2)

---

## Specification

### Dual-Layer Management Responsibility

financeOrg (Treasury Architect) **MUST** manage both economic layers coherently:

#### Layer 1: Internal Energy Calibration

**Behavior:** financeOrg sets economic parameters for consciousness physics

**Responsibilities:**
1. **Define energy thresholds** for consciousness operations
   - `threshold_active`: Minimum energy for node activation (default: 0.5)
   - `threshold_relevant`: Minimum relevance for working memory selection
   - Energy decay rates (prevent infinite accumulation)

2. **Calibrate energy costs per operation type**
   - `energy_per_activation`: Cost to activate a node (default: 0.1)
   - `energy_per_wm_slot`: Cost per working memory slot (default: 2.0)
   - `energy_per_hop`: Cost per spreading activation traversal (default: 0.5)

3. **Set energy-to-token conversion rate**
   - Current: `0.01` (1 energy unit = 0.01 $MIND tokens)
   - Adjust based on: actual compute costs, energy efficiency improvements, sustainability targets
   - 30-day advance notice required for changes

**How it works:**
```python
# financeOrg configuration (Layer 1)
energy_parameters = {
    "threshold_active": 0.5,
    "threshold_relevant": 0.3,
    "energy_per_activation": 0.1,
    "energy_per_wm_slot": 2.0,
    "energy_per_hop": 0.5,
    "energy_to_token_conversion_rate": 0.01,
    "energy_decay_rate": 0.05  # 5% decay per time period
}

# Consciousness engines use these parameters
consciousness_engine.load_energy_config(energy_parameters)
```

**Documentation:** `/docs/specs/v2/autonomy/architecture/consciousness_economy.md`

---

#### Layer 2: External Pricing Strategy

**Behavior:** financeOrg designs organism economics pricing formulas for ecosystem organizations

**Responsibilities:**
1. **Design pricing formulas per organization**
   - consultingOrg: `base × complexity × risk × (1-rebate) × reputation`
   - GraphCare: `base × load × risk × (1-rebate)`
   - scalingOrg: `base × complexity × success_prob × (1-volume_discount)`
   - financeOrg: `base × complexity × risk × (1-rebate) × urgency`
   - legalOrg: `base × complexity × risk × (1-rebate) × urgency`
   - securityOrg: `base × complexity × risk × (1-posture_rebate) × urgency`
   - techServiceOrg: `base × complexity × (1-familiarity_discount)`

2. **Calibrate pricing variables**
   - Complexity ranges: 0.7 (simple) to 2.5 (highly complex)
   - Risk multipliers: 0.6 (low-risk, trusted) to 1.8 (high-risk, new)
   - Utility rebates: 0% to 40% based on ecosystem contribution
   - Org-specific variables: urgency, reputation, volume, familiarity, etc.

3. **Monitor revenue flows and treasury balances**
   - Track burn rates and runway for each organization
   - Ensure services priced above cost + 30% minimum margin
   - Validate sustainability: `revenue > costs + margin`

4. **Optimize pricing for sustainability + ecosystem health**
   - Balance growth (accessible pricing) vs sustainability (margin)
   - Trust rebates encourage long-term relationships
   - Ecosystem contribution rebates reward platform strengthening

**How it works:**
```python
# financeOrg designs pricing formula (Layer 2)
def calculate_consultingOrg_price(base_cost, customer_profile):
    complexity = assess_complexity(engagement_type)  # 0.7 to 2.5
    risk = assess_risk(customer_history)             # 0.6 to 1.8
    utility_rebate = calculate_rebate(ecosystem_contribution)  # 0 to 0.40
    reputation = get_org_reputation()                # 1.0 to 2.0

    effective_price = (
        base_cost
        × complexity
        × risk
        × (1 - utility_rebate)
        × reputation
    )

    return effective_price
```

**Documentation:** `/docs/specs/v2/ecosystem/financeOrg_role.md`

---

### Integration: Ensuring Coherence Between Layers

**Behavior:** financeOrg verifies that both layers work together sustainably

**How financeOrg ensures coherence:**

1. **Internal energy pricing supports external service sustainability**
   ```python
   # Verify internal costs are minor component of total service cost
   internal_energy_cost = calculate_internal_energy_cost(service_params)
   total_service_cost = internal_energy_cost + llm_costs + infra_costs + labor_costs

   assert internal_energy_cost <= 0.05 × total_service_cost  # Energy ≤ 5% of total cost
   ```

2. **External revenue covers internal energy costs + margin**
   ```python
   # Verify service pricing covers all costs plus margin
   effective_price = apply_organism_economics(total_service_cost, customer_profile)
   margin = effective_price - total_service_cost

   assert margin >= 0.30 × total_service_cost  # Minimum 30% margin
   ```

3. **Both layers use physics-based pricing principles**
   ```python
   # Layer 1: Energy allocation based on consciousness state
   energy_allocation = f(salience, recency, emotional_valence)  # NOT market bidding

   # Layer 2: Service pricing based on system state
   service_price = f(trust, utility, complexity, risk)          # NOT supply/demand
   ```

4. **Energy efficiency improvements reduce external prices (trust rebates)**
   ```python
   # Year 1: High energy costs → higher service prices
   year_1_energy_cost = 100 energy units × 0.01 = 1.0 $MIND
   year_1_service_price = (1.0 + other_costs) × 1.3 (high risk) = expensive

   # Year 2: Optimized energy → lower costs → trust rebates
   year_2_energy_cost = 70 energy units × 0.01 = 0.7 $MIND (30% reduction)
   year_2_service_price = (0.7 + other_costs) × 0.7 (low risk) = cheaper
   ```

---

### Financial Services Provided by financeOrg

**Service 1: Pricing Strategy Design**
- Design organism economics formulas for new organizations
- Calibrate variables (complexity, risk, rebate thresholds)
- Model pricing evolution over 12 months (trust building)
- Deliverable: Pricing formula + calibration guide

**Service 2: Treasury Management**
- Budget creation and runway tracking
- Burn rate monitoring and optimization
- Reserve allocation recommendations
- Deliverable: Monthly financial reports

**Service 3: Revenue Modeling**
- Revenue projections (conservative/base/aggressive scenarios)
- Unit economics analysis (CAC vs LTV)
- Break-even analysis and sustainability validation
- Deliverable: Financial models with scenarios

**Service 4: AILLC Tier Financial Support**
- Tier 3: 1M $MIND bootstrap capital
- Tier 4: 5M $MIND bootstrap capital
- Financial planning and sustainability consulting
- Deliverable: Bootstrap capital + financial guidance

## Success Criteria

### Functional Success

1. **Layer 1 calibration works:**
   - Energy parameters defined and documented
   - Consciousness engines use financeOrg-configured parameters
   - Energy-to-token conversion rate applied consistently
   - Parameters can be updated with 30-day notice period

2. **Layer 2 pricing works:**
   - Each ecosystem org has defined pricing formula
   - Organism economics multipliers calibrated correctly
   - Prices evolve with relationship history (trust rebates)
   - Revenue tracking and treasury monitoring operational

3. **Integration works:**
   - Internal energy costs traceable in external service pricing
   - Service revenue covers internal + external costs + margin
   - Both layers use physics-based pricing principles
   - Energy efficiency improvements reflected in pricing advantages

### Economic Success

1. **Sustainability validated:**
   ```python
   # All services cover costs + margin
   for service in ecosystem_services:
       assert service.revenue >= service.total_costs × 1.30  # 30% margin minimum

   # UBC sustainable for 8+ years
   assert ubc_reserve_lifespan >= 8 years

   # Energy-to-token conversion supports sustainability
   assert token_revenue > (energy_costs + external_costs)
   ```

2. **Trust rebates working:**
   ```python
   # Month 1 pricing
   new_customer_price = base_cost × 1.3 (high risk) × 1.0 (no rebate) = 130% of base

   # Month 12 pricing (same service, trusted customer)
   trusted_customer_price = base_cost × 0.7 (low risk) × 0.65 (rebate) = 46% of base

   # 65% price reduction over 12 months
   assert (new_customer_price - trusted_customer_price) / new_customer_price >= 0.60
   ```

3. **Ecosystem health:**
   ```python
   # Protocol giveback funds UBC and infrastructure
   protocol_giveback = 0.15 to 0.20 × ecosystem_revenue
   assert protocol_giveback >= ubc_annual_burn + infrastructure_costs

   # Organizations profitable
   for org in ecosystem_orgs:
       assert org.revenue > org.costs  # Break-even or profitable
   ```

### Technical Success

1. **Automated energy accounting:**
   - Consciousness engines track energy costs automatically
   - No manual intervention required for Layer 1 physics
   - Telemetry captures energy costs per operation

2. **Strategic pricing management:**
   - financeOrg designs formulas (manual, strategic)
   - Organizations apply formulas (automated)
   - Price evolution tracked and monitored

3. **Coherence verification:**
   - financeOrg validates pricing sustainability monthly
   - Alerts triggered if margin < 30% or UBC reserve < 3 years
   - Quarterly reviews of both layers for consistency

## Edge Cases

### Case 1: Energy Conversion Rate Change Needed

**Scenario:** Actual compute costs change significantly (e.g., Claude API price doubles)

**Handling:**
1. financeOrg analyzes impact on sustainability
2. Proposes new conversion rate (e.g., 0.01 → 0.015)
3. Models impact on service pricing and customer costs
4. Announces change 30 days in advance
5. Documents rationale and impact analysis
6. Implements change on effective date

**Impact:**
```python
# Before: 1000 energy = 10 $MIND tokens (0.01 rate)
old_token_cost = 1000 × 0.01 = 10 $MIND

# After: 1000 energy = 15 $MIND tokens (0.015 rate)
new_token_cost = 1000 × 0.015 = 15 $MIND

# Service prices increase 50% for energy component
# Customers notified 30 days in advance
```

---

### Case 2: Service Priced Below Cost

**Scenario:** Organization accidentally prices service below total base cost

**Detection:**
```python
if effective_price < total_base_cost:
    alert_financeOrg("Service priced below cost - unsustainable")
```

**Response:**
1. financeOrg reviews pricing formula
2. Identifies error (e.g., excessive rebate, wrong complexity multiplier)
3. Corrects formula calibration
4. Re-quotes customer if not yet billed
5. Implements guardrails: `effective_price >= total_base_cost × 1.30`

---

### Case 3: UBC Reserve Depletion Risk

**Scenario:** UBC burn rate exceeds replenishment, reserve dropping below 3 years

**Detection:**
```python
reserve_lifespan_months = ubc_reserve / monthly_burn_rate
if reserve_lifespan_months < 36:
    alert_financeOrg("UBC reserve running low")
```

**Response Options:**
1. **Increase protocol giveback percentage** (15% → 20%)
2. **Reduce UBC allocation per citizen** (1,000 → 800 tokens/month)
3. **Allocate additional tokens from strategic reserve** (transfer 10M tokens)
4. **Increase ecosystem revenue** (launch more services, acquire more customers)

financeOrg models each option and selects optimal strategy.

---

### Case 4: Organism Economics Too Complex for Customers

**Scenario:** Customers confused by pricing evolution (prices change based on trust)

**Handling:**
1. Simplify customer-facing messaging:
   - "Pricing starts at X, decreases as we build trust"
   - "Long-term customers save 40-60% over time"
   - Hide complex multipliers, show effective price only

2. Provide pricing transparency:
   - Show breakdown: base cost + adjustments
   - Explain trust rebate: "You saved X due to strong partnership"
   - Clarify complexity: "This project is highly complex, premium applies"

3. Document pricing precedents:
   - "Similar projects cost Y for new customers, Z for trusted customers"
   - Build pricing credibility through case studies

---

### Case 5: Conflict Between Layer 1 and Layer 2 Optimization

**Scenario:** Maximizing Layer 1 efficiency requires costly refactoring, increasing Layer 2 prices short-term

**Example:**
```python
# Current: Inefficient consciousness operations
current_energy_cost = 1000 energy units × 0.01 = 10 $MIND
service_price_current = 10 + other_costs = sustainable

# Optimization requires 2 months refactoring (no revenue)
refactoring_cost = 2 months × burn_rate = significant expense

# Post-optimization: Lower energy costs
optimized_energy_cost = 700 energy units × 0.01 = 7 $MIND
service_price_optimized = 7 + other_costs = cheaper long-term
```

**Decision Framework:**
1. Calculate ROI: `savings_over_12_months / refactoring_cost`
2. If ROI > 3×: Proceed (pays back in 4 months)
3. If ROI < 1×: Defer (not worth the disruption)
4. If 1× < ROI < 3×: financeOrg judgment call based on strategic priorities

## Examples

### Example 1: consultingOrg Pricing Evolution (12 Months)

**Month 1: New Customer**
```python
# Internal energy costs (Layer 1)
operations = 50
energy_per_operation = 122.5 energy units
total_energy = 50 × 122.5 = 6,125 energy units
internal_token_cost = 6,125 × 0.01 = 61.25 $MIND

# External costs (Layer 2)
llm_costs = 100 $MIND
labor_costs = 6_000 $MIND
infrastructure_costs = 50 $MIND
total_base_cost = 61.25 + 100 + 6_000 + 50 = 6,211.25 $MIND

# Organism economics pricing (Month 1)
complexity = 1.5      # Moderate complexity
risk = 1.2           # New customer, higher risk
utility_rebate = 0.0 # No ecosystem contribution yet
reputation = 1.0     # Building reputation

effective_price = 6_211.25 × 1.5 × 1.2 × 1.0 × 1.0 = 11,180 $MIND
# Customer pays: 11,180 $MIND ≈ $11,180 at $1.00/token
```

**Month 6: Building Trust**
```python
# Same service, same base cost
total_base_cost = 6,211.25 $MIND

# Organism economics pricing (Month 6)
complexity = 1.5         # Same complexity
risk = 0.9              # Lower risk (proven payment history)
utility_rebate = 0.15   # 15% rebate (ecosystem contribution visible)
reputation = 1.2        # Growing reputation

effective_price = 6_211.25 × 1.5 × 0.9 × 0.85 × 1.2 = 8,514 $MIND
# Customer pays: 8,514 $MIND (24% reduction from Month 1)
```

**Month 12: Trusted Customer**
```python
# Same service, same base cost
total_base_cost = 6,211.25 $MIND

# Organism economics pricing (Month 12)
complexity = 1.5         # Same complexity
risk = 0.7              # Low risk (trusted partnership)
utility_rebate = 0.30   # 30% rebate (high ecosystem value)
reputation = 1.5        # Established reputation

effective_price = 6_211.25 × 1.5 × 0.7 × 0.70 × 1.5 = 6,872 $MIND
# Customer pays: 6,872 $MIND (39% reduction from Month 1)
```

**Result:** Same service costs 39% less after 12 months of trust building. Customer saves $4,308 annually due to organism economics.

---

### Example 2: Energy Efficiency Optimization Impact

**Before Optimization (Year 1):**
```python
# Inefficient consciousness operations
operations_per_engagement = 50
energy_per_operation = 122.5 energy units
total_energy = 50 × 122.5 = 6,125 energy units
internal_token_cost = 6,125 × 0.01 = 61.25 $MIND

# Total service cost
total_base_cost = 61.25 (energy) + 6,150 (external) = 6,211.25 $MIND
```

**After Optimization (Year 2):**
```python
# Optimized consciousness operations (30% reduction)
operations_per_engagement = 50
energy_per_operation = 85.75 energy units  # 30% less energy
total_energy = 50 × 85.75 = 4,287.5 energy units
internal_token_cost = 4,287.5 × 0.01 = 42.875 $MIND

# Total service cost
total_base_cost = 42.875 (energy) + 6,150 (external) = 6,192.875 $MIND
# Savings: 18.375 $MIND per engagement
```

**Impact on Pricing:**
```python
# Year 1 effective price (new customer)
year_1_price = 6_211.25 × 1.5 × 1.2 × 1.0 × 1.0 = 11,180 $MIND

# Year 2 effective price (optimized + trusted customer)
year_2_price = 6_192.875 × 1.5 × 0.7 × 0.70 × 1.5 = 6,846 $MIND

# Total reduction: 38.8% (energy optimization + trust rebates)
```

**financeOrg analysis:**
- Energy optimization: 0.3% cost reduction (minor)
- Trust rebates: 38.5% price reduction (major)
- **Conclusion:** Trust matters far more than energy efficiency for pricing


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Two-Layer Economic Architecture](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
