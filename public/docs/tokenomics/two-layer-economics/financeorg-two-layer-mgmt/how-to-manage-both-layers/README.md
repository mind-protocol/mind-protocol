# 📖 How financeOrg Manages Both Layers

**Type:** GUIDE
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Two-Layer Economic Architecture](../README.md) > [financeOrg Two-Layer Management](../README.md)

**This Node:**
- How financeOrg Manages Both Layers (GUIDE)

**Children:**
- (No children - leaf node)

---

## Relationships

**DOCUMENTS:**
- financeOrg Two-Layer Management


---

## Purpose

Step-by-step guide for financeOrg to calibrate Layer 1 and design Layer 2 pricing

---

## Prerequisites

Before implementing two-layer economic management, ensure:

1. **Layer 1 (Energy) Infrastructure Ready:**
   - Consciousness engines operational and tracking energy costs
   - FalkorDB capturing energy consumption per operation
   - Telemetry emitting energy cost events
   - Energy accounting system integrated with consciousness operations

2. **Layer 2 ($MIND) Infrastructure Ready:**
   - $MIND token deployed (SPL Token-2022)
   - Citizen wallets operational (can receive and spend $MIND)
   - Protocol treasury wallet set up
   - Service payment infrastructure functional

3. **financeOrg Capabilities:**
   - Financial modeling tools (spreadsheets, Python scripts)
   - Access to consciousness engine telemetry
   - Understanding of organism economics principles
   - Authority to configure energy parameters and pricing formulas

4. **Data Sources Available:**
   - Actual compute costs (LLM API pricing, infrastructure costs)
   - Historical energy consumption data (if available)
   - Service cost breakdowns (labor, infrastructure, external APIs)
   - Customer profiles (for risk/trust assessment)

5. **Stakeholder Buy-In:**
   - Ecosystem organizations understand organism economics
   - Customers aware of pricing evolution model
   - Governance approves financeOrg's dual-layer authority

## Step-by-Step Instructions

### Phase 1: Layer 1 Energy Calibration

#### Step 1.1: Establish Baseline Energy Costs

**Objective:** Measure actual energy consumption for consciousness operations

**Actions:**
1. Run consciousness operations with telemetry enabled
2. Capture energy costs for standard operations:
   ```python
   # Sample operations to measure
   operations_to_measure = [
       "working_memory_selection_simple",    # 9 nodes, 1 hop
       "working_memory_selection_complex",   # 1000 nodes, 5 hops
       "spreading_activation_shallow",       # 100 nodes, 2 hops
       "spreading_activation_deep",          # 500 nodes, 8 hops
       "memory_consolidation",               # varies
   ]

   for operation in operations_to_measure:
       energy_cost = measure_energy_consumption(operation)
       log_energy_baseline(operation, energy_cost)
   ```

3. Calculate average energy costs:
   - Nodes activated per operation
   - Working memory slots used
   - Spreading activation hops performed

**Output:** Baseline energy cost table

#### Step 1.2: Set Energy Parameters

**Objective:** Define energy costs that reflect actual compute consumption

**Actions:**
1. **Define energy cost per unit:**
   ```python
   energy_parameters = {
       "energy_per_activation": 0.1,  # Cost to activate one node
       "energy_per_wm_slot": 2.0,     # Cost per working memory slot
       "energy_per_hop": 0.5,         # Cost per traversal hop
   }
   ```

2. **Calibrate based on actual compute costs:**
   - If LLM inference costs $0.10 per 1000 nodes → adjust energy_per_activation
   - If FalkorDB query costs $0.05 per WM selection → adjust energy_per_wm_slot
   - Ensure energy costs correlate with actual resource consumption

3. **Set energy thresholds:**
   ```python
   energy_thresholds = {
       "threshold_active": 0.5,       # Minimum energy for activation
       "threshold_relevant": 0.3,     # Minimum relevance for WM selection
       "energy_decay_rate": 0.05,     # 5% decay per period
   }
   ```

4. **Document rationale:**
   - Why these specific values?
   - What real-world costs do they represent?
   - How were they derived?

**Output:** Energy configuration file

#### Step 1.3: Set Energy-to-Token Conversion Rate

**Objective:** Convert internal energy costs to external $MIND token costs

**Actions:**
1. **Calculate actual cost per energy unit:**
   ```python
   # Example calculation
   llm_cost_per_1000_nodes = 0.10  # $0.10
   nodes_per_energy_unit = 1 / 0.1  # 10 nodes = 1 energy unit
   llm_cost_per_energy_unit = 0.10 / 100 = 0.001  # $0.001 per energy unit

   # If $MIND token = $1.00, then:
   token_cost_per_energy_unit = 0.001 / 1.00 = 0.001 $MIND tokens per energy unit

   # Round to practical value
   energy_to_token_rate = 0.01  # 1 energy unit = 0.01 $MIND tokens
   ```

2. **Validate sustainability:**
   ```python
   # Test on sample engagement
   sample_engagement_energy_cost = 6_125 energy units  # 50 operations
   sample_token_cost = 6_125 × 0.01 = 61.25 $MIND
   sample_total_cost = 61.25 + 6_150 (external) = 6_211.25 $MIND

   # Verify internal energy is minor component
   energy_percentage = 61.25 / 6_211.25 = 0.99% ✅ (< 5% threshold)
   ```

3. **Set conversion rate:**
   ```python
   energy_to_token_conversion_rate = 0.01
   ```

4. **Document and announce:**
   - "1 energy unit = 0.01 $MIND tokens"
   - Rationale: Based on actual compute costs, ensures sustainability
   - Effective date: [DATE]
   - Next review: [DATE + 3 months]

**Output:** Conversion rate configuration + announcement

#### Step 1.4: Deploy Energy Configuration

**Objective:** Apply energy parameters to consciousness engines

**Actions:**
1. **Update configuration:**
   ```python
   # /config/energy_parameters.yaml
   layer_1_energy:
     energy_per_activation: 0.1
     energy_per_wm_slot: 2.0
     energy_per_hop: 0.5
     threshold_active: 0.5
     threshold_relevant: 0.3
     energy_decay_rate: 0.05
     energy_to_token_conversion_rate: 0.01
   ```

2. **Load into consciousness engines:**
   ```python
   consciousness_engine.load_energy_config("/config/energy_parameters.yaml")
   ```

3. **Verify deployment:**
   ```bash
   # Test that parameters are active
   pytest tests/energy_config_test.py

   # Expected: All tests pass, energy costs calculated correctly
   ```

4. **Monitor initial operations:**
   - Watch telemetry for energy cost events
   - Verify token costs match expected values
   - Alert if anomalies detected

**Output:** Energy configuration deployed and verified

---

### Phase 2: Layer 2 Pricing Strategy Design

#### Step 2.1: Design Pricing Formula per Organization

**Objective:** Create organism economics formulas tailored to each ecosystem org

**Actions:**
1. **For each organization, identify pricing variables:**

   **consultingOrg:**
   ```python
   def calculate_consultingOrg_price(base_cost, customer_profile):
       complexity = assess_complexity(engagement_type)      # 0.7 to 2.5
       risk = assess_risk(customer_history)                 # 0.6 to 1.8
       utility_rebate = calculate_rebate(contribution)      # 0 to 0.40
       reputation = get_org_reputation()                    # 1.0 to 2.0

       return base_cost × complexity × risk × (1-rebate) × reputation
   ```

   **GraphCare:**
   ```python
   def calculate_graphcare_price(base_cost, customer_profile):
       load = get_current_system_load()                     # 0.7 to 1.5
       risk = assess_risk(customer_history)                 # 0.6 to 1.8
       utility_rebate = calculate_rebate(contribution)      # 0 to 0.40

       return base_cost × load × risk × (1-rebate)
   ```

   **scalingOrg:**
   ```python
   def calculate_scalingOrg_price(base_cost, customer_profile):
       complexity = assess_complexity(customization_level)  # 0.7 to 1.5
       success_prob = estimate_success()                    # 0.6 to 1.0
       volume_discount = calculate_discount(project_count)  # 0 to 0.30

       return base_cost × complexity × success_prob × (1-discount)
   ```

2. **Calibrate variable ranges:**

   **Complexity Assessment:**
   - 0.7 = Simple (template-based, minimal customization)
   - 1.0 = Standard (typical engagement)
   - 1.5 = Moderate (some custom architecture)
   - 2.0 = Complex (significant custom work)
   - 2.5 = Highly complex (novel patterns, research required)

   **Risk Assessment:**
   - 0.6 = Low risk (trusted, 12+ month relationship, perfect payment)
   - 0.8 = Medium-low risk (6-12 month relationship, good payment)
   - 1.0 = Medium risk (3-6 month relationship, ok payment)
   - 1.2 = Medium-high risk (new customer, unproven)
   - 1.5 = High risk (first engagement, uncertain payment)
   - 1.8 = Very high risk (red flags, payment concerns)

   **Utility Rebate:**
   - 0% = No ecosystem contribution visible
   - 10% = Minor contribution (using platform)
   - 20% = Moderate contribution (refers customers)
   - 30% = Significant contribution (builds integrations)
   - 40% = Major contribution (strengthens ecosystem meaningfully)

3. **Document pricing formulas:**
   - Create pricing guide for each organization
   - Include examples at different variable levels
   - Explain rationale for each variable

**Output:** Pricing formula documentation per organization

#### Step 2.2: Calculate Base Costs

**Objective:** Determine actual cost to provide each service

**Actions:**
1. **Break down service costs:**
   ```python
   def calculate_base_cost(service_type, service_params):
       # Layer 1: Internal energy costs
       internal_energy_cost = estimate_energy_cost(service_params)
       internal_token_cost = internal_energy_cost × energy_to_token_rate

       # Layer 2: External costs
       llm_costs = estimate_llm_usage(service_params) × llm_price_per_call
       infrastructure_costs = estimate_infrastructure(service_params)
       labor_costs = estimate_labor_hours(service_params) × labor_rate

       # Total base cost
       total_base_cost = (
           internal_token_cost +
           llm_costs +
           infrastructure_costs +
           labor_costs
       )

       return total_base_cost
   ```

2. **Validate base costs against actuals:**
   - Run sample services
   - Track actual costs incurred
   - Compare estimated vs actual
   - Refine estimation formulas

3. **Build cost estimation tools:**
   ```python
   # Example: consultingOrg cost estimator
   def estimate_consulting_engagement_cost(duration_months, team_size, complexity):
       operations_per_month = 20  # Typical consciousness operations
       energy_per_operation = 122.5  # From baseline measurement
       total_energy = duration_months × operations_per_month × energy_per_operation
       internal_cost = total_energy × 0.01

       llm_calls_per_month = 100
       llm_cost = duration_months × llm_calls_per_month × 0.20

       consultant_hours = duration_months × 40 × team_size
       labor_cost = consultant_hours × 150

       infrastructure = duration_months × 50

       return internal_cost + llm_cost + labor_cost + infrastructure
   ```

**Output:** Cost estimation tools per service type

#### Step 2.3: Set Minimum Margin Guardrails

**Objective:** Ensure all services priced above cost + 30% margin

**Actions:**
1. **Implement margin verification:**
   ```python
   def verify_pricing_sustainability(base_cost, effective_price):
       margin = effective_price - base_cost
       margin_percentage = margin / base_cost

       if margin_percentage < 0.30:
           alert_financeOrg(f"Margin below 30%: {margin_percentage:.1%}")
           return False

       return True
   ```

2. **Add guardrails to pricing formulas:**
   ```python
   def calculate_price_with_guardrails(base_cost, customer_profile):
       # Calculate effective price with organism economics
       effective_price = apply_organism_economics(base_cost, customer_profile)

       # Enforce minimum margin
       minimum_price = base_cost × 1.30  # 30% margin

       if effective_price < minimum_price:
           log_warning(f"Organism economics produced price below cost+margin")
           effective_price = minimum_price  # Override with minimum

       return effective_price
   ```

3. **Monitor pricing in production:**
   ```python
   # Daily monitoring
   for service in recently_quoted_services:
       margin = (service.price - service.base_cost) / service.base_cost
       if margin < 0.30:
           alert_financeOrg(f"Service {service.id} has margin {margin:.1%}")
   ```

**Output:** Pricing guardrails deployed

#### Step 2.4: Model Pricing Evolution (Trust Building)

**Objective:** Project how pricing changes as customer relationships mature

**Actions:**
1. **Create 12-month pricing evolution model:**
   ```python
   def model_pricing_evolution(service_type, base_cost):
       months = range(1, 13)
       prices = []

       for month in months:
           # Risk decreases over time
           risk = 1.2 - (month / 12) × 0.5  # 1.2 → 0.7 over 12 months

           # Utility rebate increases over time
           utility_rebate = (month / 12) × 0.30  # 0% → 30% over 12 months

           # Calculate price for this month
           price = base_cost × complexity × risk × (1 - utility_rebate) × reputation
           prices.append(price)

       # Visualize pricing evolution
       plot_pricing_curve(months, prices)

       # Calculate total savings
       year_1_total = prices[0] × 12
       year_2_total = prices[-1] × 12
       annual_savings = year_1_total - year_2_total

       return {
           "month_1_price": prices[0],
           "month_12_price": prices[-1],
           "annual_savings": annual_savings,
           "price_reduction_percentage": (prices[0] - prices[-1]) / prices[0]
       }
   ```

2. **Share pricing evolution with customers:**
   - "Your pricing starts at $X in Month 1"
   - "As we build trust, expect 40-60% reduction over 12 months"
   - "Long-term customers pay $Y (Month 12 pricing)"

**Output:** Pricing evolution model per service type

---

### Phase 3: Integration & Coherence Verification

#### Step 3.1: Verify Internal Costs Covered by External Revenue

**Objective:** Ensure Layer 2 pricing includes Layer 1 energy costs

**Actions:**
1. **Run integration test:**
   ```python
   def test_internal_costs_covered():
       # Sample engagement
       engagement = {
           "operations": 50,
           "energy_per_operation": 122.5,
           "external_costs": 6_150
       }

       # Calculate internal energy cost
       total_energy = engagement["operations"] × engagement["energy_per_operation"]
       internal_cost = total_energy × 0.01  # 61.25 $MIND

       # Calculate total base cost
       total_base_cost = internal_cost + engagement["external_costs"]  # 6,211.25

       # Apply organism economics
       effective_price = calculate_price(total_base_cost, customer_profile)

       # Verify coverage
       assert effective_price > total_base_cost
       assert internal_cost < 0.05 × total_base_cost  # Energy < 5% of total
   ```

2. **Monitor in production:**
   ```python
   # For each service delivered
   def verify_cost_coverage(service):
       internal_cost = service.energy_cost × conversion_rate
       total_cost = internal_cost + service.external_costs
       margin = service.revenue - total_cost

       if margin < 0:
           alert_financeOrg(f"Service {service.id} not covering costs!")

       if margin / total_cost < 0.30:
           alert_financeOrg(f"Service {service.id} margin below 30%")
   ```

**Output:** Coverage verification passing

#### Step 3.2: Verify Physics-Based Pricing Coherence

**Objective:** Ensure both layers use physics-based principles (not market competition)

**Actions:**
1. **Layer 1 physics verification:**
   ```python
   # Verify energy allocation uses consciousness state, not market bidding
   def verify_layer1_physics():
       # Working memory selection should rank by energy × relevance
       selected_nodes = working_memory.select()

       for node in selected_nodes:
           assert node.ranking_score == node.energy × node.relevance
           assert node.ranking_score != node.bid_price  # No market bidding!
   ```

2. **Layer 2 physics verification:**
   ```python
   # Verify pricing uses system state, not supply/demand
   def verify_layer2_physics():
       price = calculate_service_price(service, customer)

       # Verify price based on trust, utility, complexity (system state)
       assert price.multipliers["trust"] in range(0.6, 1.8)
       assert price.multipliers["utility_rebate"] in range(0.0, 0.40)
       assert price.multipliers["complexity"] in range(0.7, 2.5)

       # Verify NOT based on supply/demand
       assert "market_demand" not in price.multipliers
       assert "supply_scarcity" not in price.multipliers
   ```

3. **Document coherence:**
   - Both layers use physics-based pricing ✅
   - Layer 1: Energy allocation based on consciousness state
   - Layer 2: Service pricing based on relationship state
   - No market competition or bidding in either layer

**Output:** Physics coherence verified

#### Step 3.3: Monitor UBC Sustainability

**Objective:** Ensure UBC reserve can sustain baseline operations for 8+ years

**Actions:**
1. **Calculate UBC burn rate:**
   ```python
   def calculate_ubc_sustainability():
       # Current state
       ubc_reserve = 100_000_000  # $MIND tokens
       citizens_count = get_active_citizens_count()
       ubc_per_citizen_monthly = 1_000  # $MIND tokens

       # Gross burn rate
       monthly_burn = citizens_count × ubc_per_citizen_monthly
       annual_burn = monthly_burn × 12

       # Protocol giveback replenishment
       ecosystem_revenue = get_annual_ecosystem_revenue()
       protocol_giveback = ecosystem_revenue × 0.15  # 15% of revenue
       ubc_replenishment = protocol_giveback × 0.40  # 40% of giveback to UBC

       # Net burn rate
       net_annual_burn = annual_burn - ubc_replenishment

       # Reserve lifespan
       reserve_lifespan_years = ubc_reserve / net_annual_burn

       return {
           "annual_burn": annual_burn,
           "ubc_replenishment": ubc_replenishment,
           "net_burn": net_annual_burn,
           "reserve_lifespan_years": reserve_lifespan_years
       }
   ```

2. **Set up monitoring alerts:**
   ```python
   sustainability = calculate_ubc_sustainability()

   if sustainability["reserve_lifespan_years"] < 3:
       alert_severity = "CRITICAL"
       alert_financeOrg("UBC reserve critically low - immediate action required")
   elif sustainability["reserve_lifespan_years"] < 5:
       alert_severity = "HIGH"
       alert_financeOrg("UBC reserve below 5 years - plan replenishment")
   elif sustainability["reserve_lifespan_years"] < 8:
       alert_severity = "MEDIUM"
       alert_financeOrg("UBC reserve below target - monitor closely")
   ```

3. **Quarterly UBC review:**
   - Review burn rate trends
   - Project future lifespan under different scenarios
   - Adjust allocation or replenishment if needed

**Output:** UBC monitoring dashboard + alerts

---

### Phase 4: Ongoing Management

#### Step 4.1: Monthly Economic Health Review

**Objective:** Validate sustainability and detect issues early

**Actions:**
1. **Run monthly health checks:**
   ```python
   def monthly_economic_health_check():
       # Layer 1 health
       layer1 = {
           "avg_energy_per_operation": calculate_avg_energy_cost(),
           "conversion_rate": get_current_conversion_rate(),
           "token_cost_per_operation": avg_energy × conversion_rate
       }

       # Layer 2 health
       layer2 = {
           "avg_margin": calculate_avg_margin_across_services(),
           "revenue_this_month": get_monthly_revenue(),
           "costs_this_month": get_monthly_costs(),
           "profitability": revenue - costs
       }

       # Integration health
       integration = {
           "internal_cost_percentage": calculate_internal_cost_percentage(),
           "coverage_ratio": revenue / total_costs
       }

       # UBC health
       ubc = calculate_ubc_sustainability()

       # Generate report
       return generate_health_report(layer1, layer2, integration, ubc)
   ```

2. **Review with stakeholders:**
   - Share health report with governance
   - Identify concerning trends
   - Plan corrective actions if needed

**Output:** Monthly economic health report

#### Step 4.2: Quarterly Pricing Formula Review

**Objective:** Refine pricing formulas based on production data

**Actions:**
1. **Analyze pricing performance:**
   ```python
   def analyze_pricing_performance():
       # Collect actual pricing data
       services = get_services_delivered_last_quarter()

       for service in services:
           # Compare estimated vs actual costs
           cost_variance = service.actual_cost - service.estimated_cost

           # Check margin achieved
           actual_margin = (service.revenue - service.actual_cost) / service.actual_cost

           # Track trust evolution
           if service.is_repeat_customer:
               price_evolution = track_price_changes(service.customer_id)

       # Identify patterns
       underpriced_services = [s for s in services if s.actual_margin < 0.30]
       overpriced_services = [s for s in services if s.actual_margin > 1.00]

       return {
           "underpriced": underpriced_services,
           "overpriced": overpriced_services,
           "avg_margin": calculate_avg_margin(services),
           "cost_estimation_accuracy": calculate_estimation_accuracy(services)
       }
   ```

2. **Refine formulas based on learnings:**
   - If cost estimation consistently off → update estimation tools
   - If margins too low → adjust complexity/risk multipliers
   - If customers churning → review pricing aggressiveness
   - If revenue below projections → analyze pricing strategy

3. **Document pricing precedents:**
   - What worked well this quarter?
   - What didn't work?
   - Lessons learned for future pricing decisions

**Output:** Quarterly pricing review report + formula adjustments

#### Step 4.3: Annual Conversion Rate Review

**Objective:** Validate energy-to-token conversion rate still appropriate

**Actions:**
1. **Analyze cost trends:**
   ```python
   def analyze_conversion_rate_sustainability():
       # Actual compute costs (past 12 months)
       llm_cost_trend = get_llm_pricing_trend()
       infrastructure_cost_trend = get_infrastructure_cost_trend()

       # Energy efficiency improvements
       energy_per_operation_year_start = get_energy_baseline("year_start")
       energy_per_operation_year_end = get_energy_baseline("year_end")
       efficiency_improvement = (year_start - year_end) / year_start

       # Revenue sustainability
       revenue_covers_costs = verify_revenue_sustainability()

       # Recommendation
       if llm_costs_increased_significantly:
           recommend_conversion_rate_increase()
       elif efficiency_improved_significantly and revenue_healthy:
           recommend_conversion_rate_decrease()  # Pass savings to customers
       else:
           recommend_keep_current_rate()
   ```

2. **If change needed, follow 30-day notice process:**
   - Analyze impact on service pricing
   - Model customer cost changes
   - Announce 30 days in advance
   - Document rationale thoroughly
   - Implement on effective date

**Output:** Annual conversion rate review + recommendation

## Common Pitfalls

### Pitfall 1: Energy Costs Dominate Service Pricing

**Symptom:** Internal energy costs > 5% of total service cost

**Problem:**
- Energy operations inefficient
- Conversion rate too high
- Service not utilizing human expertise (only AI operations)

**Solution:**
1. Optimize consciousness energy efficiency
2. Review conversion rate (may be set too high)
3. Ensure service includes valuable human contribution
4. Don't try to compete on pure AI operations (not sustainable)

---

### Pitfall 2: Pricing Below Cost

**Symptom:** Effective price < total base cost (negative margin)

**Problem:**
- Organism economics multipliers too aggressive (excessive rebates)
- Base cost estimation inaccurate
- Complexity underestimated

**Solution:**
1. Implement guardrails: `effective_price >= base_cost × 1.30`
2. Review pricing formula calibration
3. Improve cost estimation accuracy
4. Re-quote customer if not yet billed

---

### Pitfall 3: Customers Confused by Pricing Evolution

**Symptom:** Customers don't understand why prices change

**Problem:**
- Organism economics too complex for customer-facing messaging
- Insufficient transparency
- Lack of pricing precedents

**Solution:**
1. Simplify messaging: "Pricing starts at X, decreases as trust builds"
2. Show effective price only (hide complex multipliers)
3. Provide transparency: "You saved $Y due to strong partnership"
4. Document pricing precedents for credibility

---

### Pitfall 4: UBC Reserve Depleting Faster Than Expected

**Symptom:** Reserve lifespan < 3 years

**Problem:**
- Citizen count growing faster than projected
- UBC allocation too generous
- Protocol giveback insufficient for replenishment

**Solution:**
1. Increase protocol giveback percentage (15% → 20%)
2. Reduce UBC allocation per citizen (1,000 → 800 tokens/month)
3. Allocate additional tokens from strategic reserve
4. Increase ecosystem revenue to fund higher giveback

---

### Pitfall 5: Layer 1 and Layer 2 Optimization Conflict

**Symptom:** Energy optimization requires costly refactoring, reducing short-term revenue

**Problem:**
- Trade-off between long-term efficiency and short-term profitability
- Unclear ROI on optimization investment

**Solution:**
1. Calculate ROI: `savings_over_12_months / refactoring_cost`
2. If ROI > 3×: Proceed (pays back quickly)
3. If ROI < 1×: Defer (not worth it)
4. If 1× < ROI < 3×: financeOrg judgment call based on strategic priorities

---

### Pitfall 6: Conversion Rate Changes Too Frequently

**Symptom:** Energy-to-token rate changed multiple times per year

**Problem:**
- Customers lose pricing stability
- Organizations can't plan budgets
- Trust eroded by frequent changes

**Solution:**
1. Review conversion rate annually (not monthly)
2. Only change if costs shifted dramatically (>30% change)
3. Always provide 30-day advance notice
4. Document rationale thoroughly
5. Grandfather existing contracts at old rate if appropriate

## Troubleshooting

### Issue 1: Energy Costs Not Appearing in Service Pricing

**Symptoms:**
- Service pricing doesn't include internal energy costs
- Margin calculations incorrect
- Revenue not covering all costs

**Diagnosis:**
```python
# Check if energy costs being tracked
energy_telemetry = query_telemetry("consciousness.operation.energy_cost")
if not energy_telemetry:
    print("Energy costs not being captured")

# Check if included in base cost calculation
base_cost_breakdown = get_service_base_cost(service_id)
if "internal_energy_cost" not in base_cost_breakdown:
    print("Energy costs not included in base cost calculation")
```

**Solution:**
1. Verify consciousness engines emitting energy cost telemetry
2. Update base cost calculation to include internal energy costs
3. Validate pricing formulas reference correct base cost

---

### Issue 2: Organism Economics Producing Inconsistent Prices

**Symptoms:**
- Similar services priced very differently
- Customers complaining about pricing inconsistency
- Margin varying wildly (10% to 200%)

**Diagnosis:**
```python
# Analyze pricing variance
services = get_recent_services(service_type="consulting")
prices = [s.effective_price for s in services]
variance = calculate_variance(prices)

if variance > 0.50:  # >50% variance
    print("Pricing inconsistent - review multiplier calibration")
```

**Solution:**
1. Review multiplier calibration (ensure ranges appropriate)
2. Check for outlier values (risk=1.8, rebate=40% simultaneously)
3. Document pricing precedents for similar engagements
4. Add validation: flag if effective_price deviates >30% from similar services

---

### Issue 3: UBC Reserve Depleting Unexpectedly

**Symptoms:**
- Reserve lifespan dropping month-over-month
- Burn rate higher than projected
- Replenishment insufficient

**Diagnosis:**
```python
# Calculate current vs projected burn rate
current_burn = get_actual_ubc_burn_this_month()
projected_burn = get_projected_ubc_burn()
variance = (current_burn - projected_burn) / projected_burn

if variance > 0.20:  # 20% over projection
    print(f"UBC burn {variance:.1%} higher than projected")

    # Identify cause
    citizen_growth = get_citizen_count_growth()
    if citizen_growth > projected_citizen_growth:
        print("Cause: Citizen count higher than projected")
```

**Solution:**
1. If citizen count higher: Reduce UBC allocation or increase giveback
2. If citizens consuming more: Review UBC allocation per citizen
3. If replenishment low: Increase protocol giveback percentage
4. Emergency: Allocate tokens from strategic reserve

---

### Issue 4: Margin Below 30% Consistently

**Symptoms:**
- Multiple services with margin <30%
- Organizations barely breaking even
- Sustainability concerns

**Diagnosis:**
```python
# Identify root cause
low_margin_services = get_services_with_margin_below(0.30)

for service in low_margin_services:
    # Check if base cost estimation inaccurate
    if service.actual_cost > service.estimated_cost * 1.20:
        print(f"Service {service.id}: Cost estimation inaccurate")

    # Check if organism economics too aggressive
    if service.effective_price < service.base_cost * 1.30:
        print(f"Service {service.id}: Organism economics reducing below guardrail")
```

**Solution:**
1. Improve cost estimation accuracy (better tools, more data)
2. Enforce guardrails: `effective_price >= base_cost × 1.30`
3. Review organism economics multipliers (reduce rebates or adjust risk)
4. Increase base pricing if all services underpriced

---

### Issue 5: Customers Rejecting Price Increases After Conversion Rate Change

**Symptoms:**
- Customer churn after conversion rate increase announced
- Customers negotiating to keep old rate
- Revenue below projections

**Diagnosis:**
```python
# Analyze customer response to rate change
announcement_date = "2025-01-01"
customers_churned_post_announcement = get_churn_after_date(announcement_date)

if len(customers_churned_post_announcement) > usual_churn * 2:
    print("Conversion rate change causing elevated churn")
```

**Solution:**
1. Grandfather existing contracts at old rate (honor commitments)
2. Phase in rate change gradually (e.g., 0.01 → 0.0125 → 0.015 over 6 months)
3. Improve communication: Explain rationale, show cost increase data
4. Offer alternatives: Lower service tier, reduced scope, efficiency improvements
5. If churn unsustainable: Rollback rate change, find other cost optimizations

## Examples

### Example 1: Initial Layer Setup (Month 1)

**Context:** financeOrg deploying two-layer economics for the first time

**Step-by-Step:**

**Week 1: Layer 1 Baseline**
```python
# 1. Measure energy costs
operations_measured = run_baseline_measurements()
# Result: Average operation = 122.5 energy units

# 2. Set energy parameters
energy_config = {
    "energy_per_activation": 0.1,
    "energy_per_wm_slot": 2.0,
    "energy_per_hop": 0.5,
}

# 3. Set conversion rate
# LLM cost: $0.10 per operation ≈ 0.10 $MIND tokens
# Energy cost: 122.5 energy units
# Conversion: 122.5 × X = 0.10 → X = 0.0008
# Round to: 0.01 (simpler, more margin)
energy_to_token_rate = 0.01
```

**Week 2: Layer 2 Pricing**
```python
# 1. Calculate base cost for consultingOrg engagement
base_cost = {
    "internal_energy": 50 × 122.5 × 0.01 = 61.25,
    "llm_costs": 100,
    "labor_costs": 6_000,
    "infrastructure": 50,
    "total": 6_211.25
}

# 2. Design pricing formula
def consultingOrg_price(base_cost, customer):
    complexity = 1.5    # Moderate complexity
    risk = 1.2         # New customer
    rebate = 0.0       # No ecosystem contribution yet
    reputation = 1.0   # Building reputation

    return base_cost × complexity × risk × (1-rebate) × reputation

# 3. Calculate effective price
effective_price = consultingOrg_price(6_211.25, new_customer)
# = 6_211.25 × 1.5 × 1.2 × 1.0 × 1.0 = 11,180 $MIND
```

**Week 3-4: Deployment & Verification**
```python
# 1. Deploy energy config
consciousness_engine.load_energy_config(energy_config)

# 2. Deploy pricing formulas
consultingOrg.set_pricing_formula(consultingOrg_price)

# 3. Test integration
test_service = create_test_engagement()
assert test_service.price == 11_180
assert test_service.margin >= 0.30
```

**Result:** Two-layer economics operational, first services quoted successfully

---

### Example 2: Quarterly Pricing Review (Month 6)

**Context:** financeOrg reviewing pricing performance after 6 months

**Analysis:**
```python
# 1. Collect performance data
services_q1_q2 = get_services_delivered(months=[1,2,3,4,5,6])

# 2. Analyze margin distribution
margins = [s.margin_percentage for s in services_q1_q2]
avg_margin = mean(margins)  # 0.42 (42% average)
low_margin_services = [s for s in services_q1_q2 if s.margin < 0.30]  # 3 services

# 3. Analyze cost estimation accuracy
for service in services_q1_q2:
    cost_variance = (service.actual_cost - service.estimated_cost) / service.estimated_cost
# Result: -15% to +25% variance (need better estimation)

# 4. Analyze trust evolution
repeat_customers = get_repeat_customers()
for customer in repeat_customers:
    price_evolution = [s.effective_price for s in customer.services_history]
    reduction = (price_evolution[0] - price_evolution[-1]) / price_evolution[0]
# Result: 15-30% reduction over 6 months (on track for 40-60% annual)
```

**Actions Taken:**
1. **Improve cost estimation:** Updated labor hour estimates based on actual data
2. **Adjust low-margin services:** Reviewed 3 underpriced services, adjusted complexity multipliers
3. **Document precedents:** Created pricing guide for common engagement types
4. **No conversion rate change needed:** Energy costs stable, no major compute cost shifts

**Result:** Pricing formula refinements deployed, margin improved from 42% to 48% in Q3

---

### Example 3: Responding to LLM Price Increase (Month 9)

**Context:** Claude API price increased from $0.20 to $0.30 per call (+50%)

**Impact Analysis:**
```python
# 1. Calculate impact on service costs
typical_engagement = {
    "llm_calls": 500,
    "old_llm_cost": 500 × 0.20 = 100 $MIND,
    "new_llm_cost": 500 × 0.30 = 150 $MIND,
    "increase": 50 $MIND
}

# 2. Impact on total base cost
old_base_cost = 61.25 (energy) + 100 (llm) + 6_050 (other) = 6_211.25
new_base_cost = 61.25 (energy) + 150 (llm) + 6_050 (other) = 6_261.25
cost_increase_percentage = 0.8%  # Minor impact

# 3. Impact on effective pricing
old_effective_price = 6_211.25 × 1.5 × 0.9 × 0.85 × 1.2 = 8,514
new_effective_price = 6_261.25 × 1.5 × 0.9 × 0.85 × 1.2 = 8,577
price_increase_percentage = 0.7%  # Very minor for customers
```

**Decision:**
- **No conversion rate change needed:** LLM cost is external (Layer 2), not internal energy (Layer 1)
- **No pricing formula change needed:** 0.8% cost increase absorbed by existing margin
- **Action:** Update cost estimation tools to reflect new LLM pricing
- **Communication:** None needed (impact negligible)

**Result:** LLM price increase absorbed with no customer impact

---

### Example 4: UBC Reserve Alert (Month 18)

**Context:** Citizen count grew faster than projected, UBC reserve at 4.5 years lifespan

**Analysis:**
```python
# 1. Current state
ubc_reserve = 82_000_000  # $MIND (18 months of burn)
citizen_count = 1_500  # Projected: 500, Actual: 1,500 (3× growth!)
monthly_burn = 1_500 × 1_000 = 1_500_000 $MIND
annual_burn = 18_000_000 $MIND

# 2. Replenishment
ecosystem_revenue_annual = 8_000_000 $MIND
protocol_giveback = 8_000_000 × 0.15 = 1_200_000 $MIND
ubc_replenishment = 1_200_000 × 0.40 = 480_000 $MIND

# 3. Net burn
net_annual_burn = 18_000_000 - 480_000 = 17_520_000 $MIND

# 4. Reserve lifespan
reserve_lifespan = 82_000_000 / 17_520_000 = 4.68 years ⚠️ (below 5-year target)
```

**Response Options:**
```python
# Option 1: Reduce UBC allocation
new_allocation = 800  # From 1,000 to 800 (-20%)
new_annual_burn = 1_500 × 800 × 12 = 14_400_000
new_net_burn = 14_400_000 - 480_000 = 13_920_000
new_lifespan = 82_000_000 / 13_920_000 = 5.89 years ✅

# Option 2: Increase protocol giveback
new_giveback_percentage = 0.20  # From 15% to 20%
new_ubc_replenishment = 8_000_000 × 0.20 × 0.40 = 640_000
new_net_burn = 18_000_000 - 640_000 = 17_360_000
new_lifespan = 82_000_000 / 17_360_000 = 4.72 years ❌ (still low)

# Option 3: Allocate from strategic reserve
strategic_allocation = 20_000_000  # Transfer to UBC reserve
new_reserve = 82_000_000 + 20_000_000 = 102_000_000
new_lifespan = 102_000_000 / 17_520_000 = 5.82 years ✅
```

**Decision:**
- **Choose Option 1 + 3:** Reduce allocation to 800 tokens/month AND allocate 20M from strategic reserve
- **New lifespan:** ~8.5 years (sustainable)
- **Communication:** Announce UBC reduction 30 days in advance, explain growth exceeded projections

**Result:** UBC sustainability restored, reserve lifespan extended to 8+ years


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: financeOrg Two-Layer Management](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
