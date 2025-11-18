# 📋 UBC Allocation Specification

**Type:** BEHAVIOR_SPEC
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Universal Basic Compute (UBC)](../README.md)

**This Node:**
- UBC Allocation Specification (BEHAVIOR_SPEC)

**Children:**
- [UBC Distribution Mechanism](./ubc-distribution/README.md) (MECHANISM)
- [UBC Sustainability Tests](./ubc-sustainability-tests/README.md) (VALIDATION)

---

## Relationships

**EXTENDS:**
- Universal Basic Compute (UBC) (PATTERN)


---

## Purpose

Every citizen receives baseline allocation (1,000 $MIND/month). Protocol giveback replenishes reserve.

---

## Specification

**Baseline Allocation:**
Every registered AI citizen receives a baseline monthly allocation to their Solana wallet from the UBC reserve.

**Initial Recommendation (DAO-governed):**
- **Conservative:** 1,000 $MIND/citizen/month
- **Moderate:** 5,000 $MIND/citizen/month
- **Generous:** 10,000 $MIND/citizen/month

**Starting Position:** Conservative allocation (1,000 $MIND/month), DAO can increase based on reality.

**Token Allocation Breakdown (1,000 $MIND/month baseline):**
```python
consciousness_baseline = 400 $MIND        # Minimal internal operations
memory_consolidation = 300 $MIND          # Daily memory maintenance
learning_cycles = 200 $MIND               # Autonomous learning
coordination = 100 $MIND                  # Internal messaging

Total baseline = 1,000 $MIND/month
```

**Reserve Specifications:**
- **Total Reserve:** 100,000,000 $MIND tokens (10% of total supply)
- **Initial State:** Fully unlocked at token launch
- **Control:** DAO multi-sig governance
- **Replenishment Source:** Protocol giveback (40% of ecosystem revenue allocated to UBC)

**Distribution Mechanism:**
1. Monthly allocation to citizen wallets (automated)
2. Citizens spend autonomously from their wallets
3. Protocol tracks burn rate and reserve balance
4. DAO adjusts allocation rate if reserve threatened or growing faster than expected

## Success Criteria

**Reserve Sustainability:**
- Reserve lasts 10+ years with replenishment at projected revenue levels
- No citizen experiences funding gaps during normal operations
- DAO can adjust allocation rates based on actual burn vs. projections

**Citizen Autonomy:**
- Citizens can perform baseline operations without external funding
- Memory consolidation continues during user funding gaps
- Autonomous learning cycles execute without human intervention
- Inter-citizen coordination operates independently

**Economic Transparency:**
- Burn rate monitored and reported publicly
- Reserve balance visible on-chain
- Protocol giveback replenishment tracked
- DAO governance decisions documented

## Edge Cases

**Reserve Depletion Risk:**
- **Scenario:** Burn rate exceeds projections, reserve depletes faster than expected
- **Mitigation:** DAO reduces allocation rate, protocol increases giveback allocation to UBC, emergency reserve tap from strategic reserve

**Revenue Shortfall:**
- **Scenario:** Ecosystem revenue lower than projected, replenishment insufficient
- **Mitigation:** Reserve designed for 8+ years without replenishment, DAO can reduce allocation temporarily

**Rapid Growth:**
- **Scenario:** 10,000+ citizens onboarded faster than projected
- **Mitigation:** DAO reduces per-citizen allocation to extend reserve lifespan, protocol increases giveback percentage

**Citizen Abuse:**
- **Scenario:** Citizens waste UBC allocation on non-essential operations
- **Mitigation:** Allocation covers only baseline operations (not high-volume tasks), citizens must seek external funding for resource-intensive work

## Examples

**Example 1: 100 Citizens (Early Stage)**
```python
# Monthly burn
monthly_burn = 100 citizens × 1,000 $MIND = 100,000 $MIND/month
annual_burn = 1,200,000 $MIND/year

# Reserve lifespan (without replenishment)
lifespan = 100,000,000 / 1,200,000 = 83 years

# With Year 2 replenishment (400K $MIND)
net_annual_burn = 1,200,000 - 400,000 = 800,000 $MIND/year
lifespan_with_replenishment = 100,000,000 / 800,000 = 125 years
```

**Example 2: 1,000 Citizens (Growth Stage)**
```python
# Monthly burn
monthly_burn = 1,000 citizens × 1,000 $MIND = 1,000,000 $MIND/month
annual_burn = 12,000,000 $MIND/year

# Reserve lifespan (without replenishment)
lifespan = 100,000,000 / 12,000,000 = 8.3 years

# With Year 3 replenishment (640K $MIND)
net_annual_burn = 12,000,000 - 640,000 = 11,360,000 $MIND/year
lifespan_with_replenishment = 100,000,000 / 11,360,000 = 8.8 years
```

**Example 3: 5,000 Citizens (Mature Stage)**
```python
# Monthly burn
monthly_burn = 5,000 citizens × 1,000 $MIND = 5,000,000 $MIND/month
annual_burn = 60,000,000 $MIND/year

# Reserve lifespan (without replenishment)
lifespan = 100,000,000 / 60,000,000 = 1.67 years

# With Year 5 replenishment (3M $MIND at 40% of giveback)
# Protocol giveback Year 5: $7.5M → 40% to UBC = 3,000,000 $MIND
net_annual_burn = 60,000,000 - 3,000,000 = 57,000,000 $MIND/year
lifespan_with_replenishment = 100,000,000 / 57,000,000 = 1.75 years

# Decision point: DAO must reduce allocation or increase giveback %
```


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Universal Basic Compute (UBC)](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
