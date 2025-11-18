# 🔢 Giveback Allocation Formula

**Type:** ALGORITHM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Ecosystem as Organism](../README.md) > [Protocol Giveback Specification](../README.md) > [Protocol Giveback Distribution](../README.md)

**This Node:**
- Giveback Allocation Formula (ALGORITHM)

**Children:**
- (No children - leaf node)

---

## Relationships

**IMPLEMENTS:**
- Protocol Giveback Distribution


---

## Purpose

Formula: monthly_giveback = sum(org_revenue × org_giveback_percentage) distributed 40/20/20/20 (UBC/L4/Dev/Gov)

---

## Algorithm

**High-Level Algorithm:**

1. Collect monthly revenue from all ecosystem organizations
2. Calculate giveback per organization (revenue × org_giveback_percentage)
3. Sum total monthly giveback across all orgs
4. Distribute total giveback to four allocation pools (40/20/20/20 split)
5. Return allocation breakdown for transparency and auditing

**Detailed Steps:**

```
FUNCTION calculate_monthly_giveback_allocation(org_revenues):
    // Step 1: Initialize collections
    total_giveback = 0
    org_contributions = {}

    // Step 2: Calculate giveback per organization
    FOR EACH org IN ecosystem_organizations:
        IF org.monthly_revenue > 0:
            org_giveback = org.monthly_revenue × org.giveback_percentage
            org_contributions[org.name] = org_giveback
            total_giveback += org_giveback
        END IF
    END FOR

    // Step 3: Distribute to allocation pools (40/20/20/20)
    allocation = {
        "ubc_reserve": total_giveback × 0.40,
        "l4_validation": total_giveback × 0.20,
        "protocol_dev": total_giveback × 0.20,
        "governance": total_giveback × 0.20
    }

    // Step 4: Verify allocation sums to total (sanity check)
    ASSERT sum(allocation.values()) == total_giveback

    // Step 5: Return detailed breakdown
    RETURN {
        "total_giveback": total_giveback,
        "org_contributions": org_contributions,
        "allocation": allocation,
        "timestamp": current_timestamp()
    }
END FUNCTION
```

## Inputs

**Required Inputs:**

1. **org_revenues**: Dictionary mapping organization names to monthly revenue amounts
   - Type: `Dict[str, float]` (organization_name → revenue in $MIND tokens)
   - Example: `{"consultingOrg": 230000, "GraphCare": 10500, "scalingOrg": 0}`
   - Note: Organizations with zero or negative revenue (still burning bootstrap capital) contribute zero giveback

2. **org_giveback_percentages**: Configuration mapping organization to giveback percentage
   - Type: `Dict[str, float]` (organization_name → percentage as decimal)
   - Values:
     - `consultingOrg: 0.15` (15%)
     - `techServiceOrg: 0.20` (20%)
     - `GraphCare: 0.20` (20%)
     - `scalingOrg: 0.20` (20%)
     - `financeOrg: 0.15` (15%)
     - `legalOrg: 0.15` (15%)
     - `securityOrg: 0.15` (15%)

3. **allocation_split**: Distribution percentages for giveback pools
   - Type: `Dict[str, float]` (pool_name → percentage as decimal)
   - Default: `{"ubc_reserve": 0.40, "l4_validation": 0.20, "protocol_dev": 0.20, "governance": 0.20}`
   - Constraint: `sum(allocation_split.values()) == 1.0` (must sum to 100%)

## Outputs

**Return Value:**

```python
{
    "total_giveback": float,              # Total $MIND tokens collected as giveback
    "org_contributions": {
        "consultingOrg": float,           # Each org's contribution amount
        "techServiceOrg": float,
        "GraphCare": float,
        # ... etc
    },
    "allocation": {
        "ubc_reserve": float,             # Amount allocated to each pool
        "l4_validation": float,
        "protocol_dev": float,
        "governance": float
    },
    "timestamp": datetime,                # When calculation was performed
    "month": str,                         # Month identifier (e.g., "2025-02")
}
```

## Formula

**Core Formula:**

```python
# Step 1: Calculate per-org giveback
monthly_giveback = sum(
    org_revenue × org_giveback_percentage
    for org in ecosystem_organizations
    if org_revenue > 0
)

# Step 2: Distribute to pools
allocation = {
    "ubc_reserve": monthly_giveback × 0.40,
    "l4_validation": monthly_giveback × 0.20,
    "protocol_dev": monthly_giveback × 0.20,
    "governance": monthly_giveback × 0.20
}

# Verification constraint
assert sum(allocation.values()) == monthly_giveback
```

**Per-Organization Contribution Formula:**

```python
org_contribution = max(0, org_monthly_revenue) × org_giveback_percentage

# Where:
#   org_monthly_revenue: Total revenue for month (in $MIND tokens)
#   org_giveback_percentage: 0.15 or 0.20 depending on org type
#   max(0, ...) ensures negative revenue (losses) contributes zero giveback
```

## Examples

**Example 1: Single Organization (consultingOrg)**

```python
# Input
org_revenues = {
    "consultingOrg": 230_000  # $230K revenue in February
}
org_giveback_percentage = 0.15  # 15% for consultingOrg

# Calculation
org_contribution = 230_000 × 0.15 = 34_500 $MIND
total_giveback = 34_500

# Allocation (40/20/20/20 split)
allocation = {
    "ubc_reserve": 34_500 × 0.40 = 13_800,
    "l4_validation": 34_500 × 0.20 = 6_900,
    "protocol_dev": 34_500 × 0.20 = 6_900,
    "governance": 34_500 × 0.20 = 6_900
}

# Verification: 13,800 + 6,900 + 6,900 + 6,900 = 34,500 ✓

# Output
{
    "total_giveback": 34_500,
    "org_contributions": {"consultingOrg": 34_500},
    "allocation": {
        "ubc_reserve": 13_800,
        "l4_validation": 6_900,
        "protocol_dev": 6_900,
        "governance": 6_900
    },
    "timestamp": "2025-02-28T23:59:59Z",
    "month": "2025-02"
}
```

**Example 2: Multiple Organizations (Ecosystem-Wide, Year 2)**

```python
# Input (Year 2 monthly average)
org_revenues = {
    "consultingOrg": 125_000,    # $1.5M annual / 12 months
    "techServiceOrg": 30_000,    # $360K annual / 12 months
    "GraphCare": 10_000,         # $120K annual / 12 months
    "scalingOrg": 66_667,        # $800K annual / 12 months
    "financeOrg": 72_500,        # $870K annual / 12 months
    "legalOrg": 90_417,          # $1.085M annual / 12 months
    "securityOrg": 130_000,      # $1.56M annual / 12 months
}

org_giveback_percentages = {
    "consultingOrg": 0.15,
    "techServiceOrg": 0.20,
    "GraphCare": 0.20,
    "scalingOrg": 0.20,
    "financeOrg": 0.15,
    "legalOrg": 0.15,
    "securityOrg": 0.15,
}

# Calculation per org
org_contributions = {
    "consultingOrg": 125_000 × 0.15 = 18_750,
    "techServiceOrg": 30_000 × 0.20 = 6_000,
    "GraphCare": 10_000 × 0.20 = 2_000,
    "scalingOrg": 66_667 × 0.20 = 13_333,
    "financeOrg": 72_500 × 0.15 = 10_875,
    "legalOrg": 90_417 × 0.15 = 13_563,
    "securityOrg": 130_000 × 0.15 = 19_500,
}

# Total giveback
total_giveback = sum(org_contributions.values()) = 84_021

# Allocation (40/20/20/20 split)
allocation = {
    "ubc_reserve": 84_021 × 0.40 = 33_608,
    "l4_validation": 84_021 × 0.20 = 16_804,
    "protocol_dev": 84_021 × 0.20 = 16_804,
    "governance": 84_021 × 0.20 = 16_804
}

# Verification: 33,608 + 16,804 + 16,804 + 16,804 = 84,020 ✓ (rounding)

# Annual projection: 84,021 × 12 = 1,008,252 $MIND/year giveback
```

**Example 3: Edge Case - New Org With No Revenue**

```python
# Input (Month 1 of new org)
org_revenues = {
    "consultingOrg": 150_000,     # Established org with revenue
    "newOrg": -5_000,             # New org burning bootstrap capital (negative revenue)
}

org_giveback_percentages = {
    "consultingOrg": 0.15,
    "newOrg": 0.20,
}

# Calculation
org_contributions = {
    "consultingOrg": 150_000 × 0.15 = 22_500,
    "newOrg": max(0, -5_000) × 0.20 = 0,  # No giveback when revenue ≤ 0
}

total_giveback = 22_500

# Allocation
allocation = {
    "ubc_reserve": 22_500 × 0.40 = 9_000,
    "l4_validation": 22_500 × 0.20 = 4_500,
    "protocol_dev": 22_500 × 0.20 = 4_500,
    "governance": 22_500 × 0.20 = 4_500
}

# Output shows newOrg contributed zero (not penalized for bootstrap phase)
{
    "total_giveback": 22_500,
    "org_contributions": {
        "consultingOrg": 22_500,
        "newOrg": 0
    },
    # ... allocation
}
```

## Edge Cases

**Edge Case 1: Zero Revenue Month**
- **Situation**: All orgs have zero revenue (rare, but possible in early bootstrap)
- **Handling**: `total_giveback = 0`, all allocation pools receive zero
- **Output**: Valid output with zero values (no error, just empty month)

**Edge Case 2: Single Org Dominates Revenue**
- **Situation**: consultingOrg earns $500K, all other orgs earn $10K total
- **Handling**: Algorithm handles normally, consultingOrg contributes $75K (15%), others contribute $2K total
- **Impact**: UBC reserve replenishment concentrated from single org (acceptable)

**Edge Case 3: Allocation Split Change (DAO Vote)**
- **Situation**: DAO votes to increase UBC allocation from 40% → 60% (crisis mode)
- **Handling**: Update `allocation_split` parameter: `{"ubc_reserve": 0.60, "l4_validation": 0.15, "protocol_dev": 0.15, "governance": 0.10}`
- **Verification**: Algorithm checks `sum(allocation_split.values()) == 1.0` before execution

**Edge Case 4: Rounding Errors**
- **Situation**: Decimal calculations create rounding errors (e.g., total = 84,020.99 vs 84,021.00)
- **Handling**: Accept rounding errors up to 0.01 $MIND (negligible for token economics)
- **Verification**: `assert abs(sum(allocation.values()) - total_giveback) < 0.01`

**Edge Case 5: New Org Added Mid-Month**
- **Situation**: New org launches on 15th, earns revenue for half month
- **Handling**: Calculate giveback on actual revenue earned (pro-rated automatically)
- **Example**: If org earns $5K in half month, contributes 5,000 × 0.20 = 1,000 $MIND

## Complexity

**Time Complexity:** O(N)
- Where N = number of ecosystem organizations
- Single pass through organizations to calculate contributions
- Constant time allocation distribution (4 pools)
- Linear scaling with ecosystem growth

**Space Complexity:** O(N)
- Store org_contributions dictionary (N entries)
- Store allocation dictionary (4 entries, constant)
- Total space: O(N + 4) = O(N)

**Performance Characteristics:**
- **Monthly execution**: Runs once per month (not performance-critical)
- **Current scale**: ~7 organizations → <1ms execution time
- **Future scale**: Even at 100 organizations → <10ms execution time
- **Bottleneck**: Not computation (trivial math), but on-chain transaction costs for transfers

**Optimization Opportunities:**
- **Batch transfers**: Collect all org contributions in single transaction block (reduce gas fees)
- **Pre-calculation**: Cache allocation percentages (avoid repeated lookups)
- **Parallel execution**: Calculate org contributions in parallel (if needed at scale)

**Current Implementation Priority:** Correctness and transparency over performance (monthly frequency makes performance non-critical)


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Protocol Giveback Distribution](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
