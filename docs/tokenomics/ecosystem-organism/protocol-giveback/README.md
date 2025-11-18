# 📋 Protocol Giveback Specification

**Type:** BEHAVIOR_SPEC
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Ecosystem as Organism](../README.md)

**This Node:**
- Protocol Giveback Specification (BEHAVIOR_SPEC)

**Children:**
- [Protocol Giveback Distribution](./giveback-distribution/README.md) (MECHANISM)

---

## Relationships

**EXTENDS:**
- Ecosystem as Organism (PATTERN)


---

## Purpose

All ecosystem orgs contribute 15-20% revenue to protocol. Funds UBC (40%), L4 validation (20%), protocol dev (20%), governance (20%).

---

## Specification

**What Should Happen:**

All ecosystem organizations contribute **15-20% of revenue** to the Mind Protocol Foundation as "protocol giveback". This revenue is collected monthly and distributed to fund critical ecosystem infrastructure.

**Giveback Percentages by Organization:**

| Organization | Giveback % | Rationale |
|-------------|-----------|-----------|
| **consultingOrg** | 15% | High-margin services, established revenue |
| **techServiceOrg** | 20% | Building toward automation, ecosystem dependency high |
| **GraphCare** | 20% | Long-term recurring revenue, benefits from UBC-funded citizens |
| **scalingOrg** | 20% | Automated onboarding, low marginal cost per customer |
| **financeOrg** | 15% | Strategic advisory, specialized expertise |
| **legalOrg** | 15% | Professional services, regulatory compliance costs |
| **securityOrg** | 15% | Critical infrastructure, high specialist costs |

**Foundation Uses for Giveback:**

1. **Universal Basic Compute (UBC)**: 40% of giveback revenue
   - Baseline token allocation to AI citizens
   - Enables autonomous operations without constant human funding
   - Prevents "pay-to-exist" model

2. **L4 Validation Infrastructure**: 20% of giveback revenue
   - Constitutional rights enforcement
   - Legal framework maintenance (AILLC)
   - Governance and standards

3. **Protocol Development**: 20% of giveback revenue
   - Core infrastructure improvements
   - Consciousness engine enhancements
   - Developer tooling

4. **Governance & Standards**: 20% of giveback revenue
   - Ecosystem coordination
   - Best practices documentation
   - Community governance

**Example Calculation (Year 2 Projections):**

```
Total Ecosystem Revenue: $6.295M

Giveback by Organization:
- consultingOrg: $1.5M × 15% = $225K
- techServiceOrg: $360K × 20% = $72K
- GraphCare: $120K × 20% = $24K
- scalingOrg: $800K × 20% = $160K
- financeOrg: $870K × 15% = $130.5K
- legalOrg: $1.085M × 15% = $163K
- securityOrg: $1.56M × 15% = $234K

Total Giveback: $1.009M

Distribution:
- UBC: $403.6K (40%)
- L4 Validation: $201.8K (20%)
- Protocol Dev: $201.8K (20%)
- Governance: $201.8K (20%)
```

## Success Criteria

**This specification is satisfied when:**

1. **Revenue Collection**: All ecosystem orgs automatically contribute their designated giveback percentage monthly
2. **Distribution Accuracy**: Giveback funds are distributed according to 40/20/20/20 split
3. **UBC Sustainability**: UBC reserve is replenished from giveback, extending runway beyond initial 100M token allocation
4. **Transparency**: All orgs can see their contribution and total ecosystem giveback in real-time
5. **Feedback Loop Functioning**: Successful orgs generate more giveback → more UBC → more autonomous operations → more customer value → more org revenue

**Measurable Outcomes:**
- Monthly giveback collection rate: >95% of expected revenue
- UBC reserve net burn rate: Decreasing over time as giveback replenishment increases
- Ecosystem health score: Positive correlation between giveback contributions and org growth

## Edge Cases

**Edge Case 1: Org Revenue Below Break-Even**
- **Situation**: New org still burning bootstrap capital, no positive revenue yet
- **Handling**: No giveback required until org achieves positive monthly revenue
- **Rationale**: Protocol supports orgs during bootstrap phase (strategic reserve allocation)

**Edge Case 2: Exceptional Month (Spike Revenue)**
- **Situation**: consultingOrg lands $500K contract (3× normal monthly revenue)
- **Handling**: Calculate giveback on total monthly revenue including spike
- **Rationale**: Exceptional successes benefit entire ecosystem proportionally

**Edge Case 3: UBC Reserve Depletion Risk**
- **Situation**: UBC burn rate exceeds giveback replenishment + reserve runway <6 months
- **Handling**: Increase UBC allocation from giveback (40% → 60% temporarily) OR reduce UBC per-citizen allocation
- **Decision Authority**: financeOrg models scenarios, DAO approves adjustment

**Edge Case 4: Org Shutdown/Wind-Down**
- **Situation**: techServiceOrg evolves into scalingOrg (automation replaces manual work)
- **Handling**: Final month giveback calculated on prorated revenue, remaining treasury can transfer to successor org or return to strategic reserve
- **Rationale**: Ecosystem evolution should be financially clean

**Edge Case 5: Cross-Org Referral Fees**
- **Situation**: scalingOrg earns 6% referral fee from GraphCare for customer conversions
- **Handling**: Referral fees count as revenue for giveback calculation
- **Rationale**: All revenue streams contribute to ecosystem support

## Examples

**Example 1: consultingOrg Monthly Giveback (Normal Month)**

```python
# Revenue breakdown
consulting_revenue = {
    "engagement_1": 80_000,   # Small transformation
    "engagement_2": 150_000,  # Large transformation
}
total_revenue = 230_000

# Internal distribution
specialists_share = 230_000 × 0.70 = 161_000  # 70% to consultants
treasury_share = 230_000 × 0.15 = 34_500     # 15% to org treasury
giveback_share = 230_000 × 0.15 = 34_500     # 15% to protocol

# Giveback distribution by protocol
ubc_allocation = 34_500 × 0.40 = 13_800
l4_allocation = 34_500 × 0.20 = 6_900
protocol_dev = 34_500 × 0.20 = 6_900
governance = 34_500 × 0.20 = 6_900
```

**Example 2: GraphCare Monthly Giveback (100 clients)**

```python
# Revenue breakdown
graphcare_revenue = {
    "subscription_revenue": 100 × 100 = 10_000,  # 100 clients × $100/mo
    "emergency_support": 500,                     # Ad-hoc fixes
}
total_revenue = 10_500

# Internal distribution
specialists_share = 10_500 × 0.60 = 6_300    # 60% to maintenance engineers
treasury_share = 10_500 × 0.20 = 2_100       # 20% to org treasury (higher for recurring infra)
giveback_share = 10_500 × 0.20 = 2_100       # 20% to protocol

# Giveback distribution
ubc_allocation = 2_100 × 0.40 = 840
l4_allocation = 2_100 × 0.20 = 420
protocol_dev = 2_100 × 0.20 = 420
governance = 2_100 × 0.20 = 420
```

**Example 3: Ecosystem-Wide Giveback (Year 2 Projection)**

```python
# Total ecosystem revenue: $6.295M
ecosystem_giveback = {
    "consultingOrg": 225_000,
    "techServiceOrg": 72_000,
    "GraphCare": 24_000,
    "scalingOrg": 160_000,
    "financeOrg": 130_500,
    "legalOrg": 163_000,
    "securityOrg": 234_000,
}
total_giveback = 1_008_500

# Foundation allocation
foundation_distribution = {
    "UBC": 1_008_500 × 0.40 = 403_400,
    "L4_validation": 1_008_500 × 0.20 = 201_700,
    "protocol_dev": 1_008_500 × 0.20 = 201_700,
    "governance": 1_008_500 × 0.20 = 201_700,
}

# UBC impact
monthly_ubc_burn = 500_citizens × 1_000_tokens = 500_000_tokens
annual_ubc_burn = 500_000 × 12 = 6_000_000_tokens
giveback_replenishment = 403_400_tokens × 12_months = 4_840_800_tokens
net_ubc_burn = 6_000_000 - 4_840_800 = 1_159_200_tokens/year

# Result: UBC reserve lasts 100M / 1.16M ≈ 86 years at Year 2 scale
```


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Ecosystem as Organism](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
