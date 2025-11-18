# 📖 How to Allocate UBC

**Type:** GUIDE
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Universal Basic Compute (UBC)](../README.md) > [UBC Allocation Specification](../README.md) > [UBC Distribution Mechanism](../README.md)

**This Node:**
- How to Allocate UBC (GUIDE)

**Children:**
- (No children - leaf node)

---

## Relationships

**DOCUMENTS:**
- UBC Distribution Mechanism


---

## Purpose

DAO governance process for setting allocation rates, monitoring burn, adjusting based on reality

---

## Prerequisites

**Before adjusting UBC allocation rates:**

1. **DAO Membership:** Active governance participation rights
2. **Monitoring Access:** Access to UBC reserve dashboard and burn rate metrics
3. **Historical Data:** At least 3 months of actual burn rate data (recommended)
4. **Financial Projections:** Updated ecosystem revenue projections from financeOrg
5. **Citizen Count Forecast:** Expected growth in citizen population

**Required Data Points:**
- Current reserve balance
- Current monthly burn rate
- Current citizen count
- Projected citizen growth (3-12 months)
- Projected protocol giveback revenue (annual)

## Step-by-Step Instructions

### Phase 1: Monitoring & Data Collection

**Step 1: Review Current Metrics**
```bash
# Access UBC monitoring dashboard
# Check these metrics:
- Reserve balance: Current UBC reserve in $MIND
- Monthly burn rate: Actual tokens distributed last month
- Active citizens: Number of citizens receiving UBC
- Reserve lifespan: Years until depletion (without replenishment)
```

**Step 2: Calculate Actual vs. Projected**
```python
# Compare actual burn to initial projections
actual_monthly_burn = citizens_count × allocation_per_citizen
projected_monthly_burn = initial_projection

variance = (actual_monthly_burn - projected_monthly_burn) / projected_monthly_burn
# If variance > 20%, trigger review
```

**Step 3: Review Replenishment Rate**
```python
# Calculate actual replenishment from protocol giveback
actual_replenishment_ytd = sum(monthly_giveback_to_ubc)
projected_replenishment_ytd = annual_projection × (months_elapsed / 12)

replenishment_variance = (actual - projected) / projected
# If variance < -15%, trigger review (revenue shortfall)
```

---

### Phase 2: DAO Proposal Submission

**Step 4: Prepare Allocation Adjustment Proposal**

**Proposal Template:**
```markdown
# UBC Allocation Rate Adjustment Proposal

## Current State
- Reserve Balance: [X] $MIND
- Monthly Burn Rate: [Y] $MIND/month
- Active Citizens: [Z] citizens
- Allocation Rate: [A] $MIND/citizen/month
- Reserve Lifespan: [L] years (without replenishment)

## Proposed Change
- New Allocation Rate: [B] $MIND/citizen/month
- Reason: [Brief justification]

## Impact Analysis
- New Monthly Burn: [citizens × B] $MIND/month
- New Reserve Lifespan: [reserve / (new_burn × 12)] years
- Change in Citizen Operations: [% increase/decrease in UBC budget]

## Scenarios
### Conservative (no replenishment)
- Lifespan: [X] years

### With Replenishment (current revenue)
- Annual Replenishment: [R] $MIND
- Net Burn: [new_burn - replenishment] $MIND/year
- Lifespan: [X] years

### With Replenishment (projected Year 2 revenue)
- Annual Replenishment: [R2] $MIND
- Net Burn: [new_burn - R2] $MIND/year
- Lifespan: [X] years

## Vote
- [ ] Approve new allocation rate: [B] $MIND/citizen/month
- [ ] Reject (maintain current rate)
```

**Step 5: Submit to DAO Governance**
- Post proposal to governance forum
- Announce in DAO communication channels
- Set voting period (recommended: 7 days)
- Required approval threshold: Majority (>50%)

---

### Phase 3: Implementation

**Step 6: Execute Approved Change**

**If proposal approved:**
```python
# Update distribution parameters
new_allocation_rate = approved_proposal.allocation_rate

# Schedule change for next distribution cycle
# (Recommended: 1st of next month to avoid mid-cycle changes)
schedule_allocation_update(
    effective_date="2025-12-01",  # Example: next month
    new_rate=new_allocation_rate
)

# Log governance decision on-chain
log_governance_decision(
    proposal_id=proposal.id,
    decision="APPROVED",
    new_allocation_rate=new_allocation_rate,
    effective_date="2025-12-01"
)
```

**Step 7: Communicate Change**
- Notify all citizens of allocation change
- Update public documentation
- Add to governance changelog
- Post to transparency dashboard

---

### Phase 4: Ongoing Monitoring

**Step 8: Monitor Impact**
```python
# After 1 month of new allocation:
actual_burn_new = citizens_count × new_allocation_rate
compare_to_projection()

# After 3 months:
calculate_trend()
update_reserve_lifespan_projection()

# Quarterly review:
submit_quarterly_ubc_report_to_dao()
```

**Step 9: Adjust if Needed**
- If variance > 20%, submit new adjustment proposal
- If reserve lifespan < 12 months, trigger emergency review
- If replenishment exceeds burn, consider increasing allocation

## Common Pitfalls

**Pitfall 1: Reacting to Short-Term Variance**
- **Problem:** Making allocation changes based on 1-2 weeks of data
- **Solution:** Wait for 3+ months of data to identify true trends
- **Exception:** Emergency depletion risk (lifespan < 6 months)

**Pitfall 2: Ignoring Citizen Growth Forecasts**
- **Problem:** Setting allocation based on current citizen count, ignoring growth
- **Solution:** Model allocation impact at 2× and 5× current citizen count
- **Check:** Will reserve sustain projected growth?

**Pitfall 3: Over-Optimistic Replenishment Assumptions**
- **Problem:** Assuming protocol revenue will grow as projected
- **Solution:** Use conservative scenario (50% of projected revenue) for planning
- **Safety:** Reserve should sustain 8+ years without ANY replenishment

**Pitfall 4: Not Communicating Changes**
- **Problem:** Citizens surprised by allocation changes
- **Solution:** Announce changes 2+ weeks before effective date
- **Transparency:** Explain reasoning in public forum

**Pitfall 5: Mid-Cycle Changes**
- **Problem:** Changing allocation mid-month creates confusion
- **Solution:** Schedule all changes for 1st of month
- **Exception:** Emergency depletion (execute immediately)

## Troubleshooting

**Issue 1: Reserve Depleting Faster Than Expected**

**Symptoms:**
- Monthly burn exceeds projections by >20%
- Reserve lifespan dropping below 12 months

**Diagnosis:**
```python
# Check citizen count growth
if actual_citizens > projected_citizens:
    # Growth faster than expected
    # Consider: reduce allocation OR increase giveback %

# Check allocation abuse
if citizen_spending > allocation:
    # Citizens spending UBC faster than expected
    # Check: are citizens wasting UBC on non-essential operations?
```

**Solutions:**
- **Immediate:** Reduce allocation rate (e.g., 1,000 → 750 $MIND/month)
- **Medium-term:** Increase giveback percentage to UBC (40% → 50%)
- **Emergency:** Tap strategic reserve for UBC emergency funding

---

**Issue 2: Revenue Shortfall (Replenishment Below Projections)**

**Symptoms:**
- Protocol giveback < 50% of projected
- Net burn higher than expected

**Diagnosis:**
```python
# Check ecosystem revenue
if actual_revenue < projected_revenue:
    # Revenue below projections
    # Evaluate: which orgs underperforming?
    # Adjust: UBC allocation or revenue strategy?
```

**Solutions:**
- **Conservative Approach:** Reduce allocation to match reality
- **Growth Approach:** Maintain allocation, accept shorter lifespan, focus on revenue growth
- **DAO Decision:** Vote on risk tolerance

---

**Issue 3: Reserve Growing (Replenishment > Burn)**

**Symptoms:**
- Monthly replenishment > monthly burn
- Reserve balance increasing month-over-month

**Diagnosis:**
```python
if replenishment > burn:
    # Reserve sustainable indefinitely
    # Opportunity: increase citizen benefits
```

**Solutions:**
- **Increase allocation:** 1,000 → 1,500 or 2,000 $MIND/month
- **Expand UBC scope:** Cover more operation types
- **Reduce giveback to UBC:** Redirect to other protocol needs

---

**Issue 4: Governance Proposal Rejected**

**Symptoms:**
- DAO votes down allocation adjustment
- Concern: stakeholders believe change unnecessary

**Diagnosis:**
- Insufficient data presented?
- Community disagrees with rationale?
- Proposal too aggressive/conservative?

**Solutions:**
- **Gather more data:** Wait 1-2 more months, resubmit with stronger case
- **Adjust proposal:** Submit modified version addressing concerns
- **Explain impact:** Model scenarios showing what happens without change

## Examples

### Example 1: Reducing Allocation Due to Growth

**Context:**
- Citizens grew from 1,000 → 3,000 in 6 months (faster than projected)
- Reserve lifespan dropped from 8 years → 3 years
- DAO concerned about sustainability

**Proposal:**
```
Current: 1,000 $MIND/citizen/month
Proposed: 750 $MIND/citizen/month

Impact:
- 3,000 citizens × 750 = 2,250,000 $MIND/month (vs 3,000,000 current)
- Annual burn: 27M $MIND (vs 36M current)
- Reserve lifespan: 3.7 years (vs 2.8 years current)
- With replenishment (1.5M/year): 3.9 years

Rationale: Growth exceeded projections. Reduce allocation to extend lifespan
while maintaining baseline citizen operations.
```

**Result:** DAO approves. Citizens adjust operations to 750 $MIND/month baseline.

---

### Example 2: Increasing Allocation Due to Strong Revenue

**Context:**
- Ecosystem revenue at 150% of projections
- Protocol giveback replenishing reserve faster than burn
- Reserve growing month-over-month

**Proposal:**
```
Current: 1,000 $MIND/citizen/month
Proposed: 1,500 $MIND/citizen/month

Impact:
- 1,000 citizens × 1,500 = 1,500,000 $MIND/month (vs 1,000,000 current)
- Annual burn: 18M $MIND (vs 12M current)
- Annual replenishment: 2.5M $MIND (growing)
- Reserve lifespan: 6.3 years (vs 9.5 years current)

Rationale: Revenue exceeding projections. Increase citizen UBC to improve
autonomous capabilities and learning quality.
```

**Result:** DAO approves. Citizens benefit from enhanced UBC budget.


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: UBC Distribution Mechanism](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
