# 📋 Pricing Evolution Specification

**Type:** BEHAVIOR_SPEC
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Organism Economics](../README.md)

**This Node:**
- Pricing Evolution Specification (BEHAVIOR_SPEC)

**Children:**
- [Organism Economics Formula Application](./formula-application/README.md) (MECHANISM)

---

## Relationships

**EXTENDS:**
- Organism Economics (PATTERN)


---

## Purpose

Prices should evolve based on trust, utility, and relationship duration. 60-70% reduction over 12 months for trusted customers.

---

## Specification

**Prices must evolve based on relationship state, creating 60-80% price reduction over 12 months for trusted, high-utility customers.**

### Required Behavior

**Month 1 (New Customer):**
- High risk multiplier (1.2-1.3×) - Unknown payment reliability
- No utility rebate (0%) - No ecosystem contribution yet
- Org-specific variables at baseline (1.0×)
- **Result:** 120-130% of base cost

**Month 6 (Building Trust):**
- Medium risk multiplier (0.9×) - Proven payment history
- Small utility rebate (10-15%) - Some ecosystem contribution
- Org-specific variables improving (volume discounts, familiarity)
- **Result:** ~77% of base cost (41% reduction from Month 1)

**Month 12 (Trusted Customer):**
- Low risk multiplier (0.6-0.7×) - Excellent payment history
- Significant utility rebate (30-40%) - High ecosystem contribution
- Org-specific variables optimized (reputation, volume, familiarity)
- **Result:** 40-50% of base cost (60-70% reduction from Month 1)

### Triggers for Evolution

1. **Trust Score Increases:**
   - Payment reliability: On-time payments, no disputes
   - Relationship duration: Months of successful engagement
   - Ecosystem contribution: Referrals, data sharing, network effects

2. **Utility Rebate Grows:**
   - Ecosystem value creation: New customer referrals
   - Protocol support: Contributing to UBC, L4 validation
   - Knowledge sharing: Case studies, testimonials, documentation

3. **Org-Specific Variables Improve:**
   - **consultingOrg:** Reputation premium grows (successful case studies)
   - **GraphCare:** Load multiplier decreases (capacity optimization)
   - **scalingOrg:** Volume discount increases (repeat launches)
   - **financeOrg:** Urgency decreases (planned work vs emergency)
   - **legalOrg:** Complexity decreases (template reuse)
   - **securityOrg:** Security posture improves (proven practices)
   - **techServiceOrg:** Familiarity increases (known patterns)

## Success Criteria

**Quantitative:**
- [ ] New customers pay 120-150% of base cost (risk premium present)
- [ ] 6-month customers pay 60-80% of base cost (trust building visible)
- [ ] 12-month customers pay 40-60% of base cost (sustained relationship reward)
- [ ] Price reduction is 60-80% from Month 1 to Month 12 for ideal customers

**Qualitative:**
- [ ] Customers understand why their price changes (transparent formula)
- [ ] Customers have clear path to lower prices (build trust, contribute value)
- [ ] Organizations maintain profitability despite lower prices (volume + efficiency)
- [ ] Ecosystem health improves (retention > churn, cooperation > extraction)

**Observable Metrics:**
- Customer lifetime value (CLV) increases over time
- Customer acquisition cost (CAC) decreases (referrals increase)
- Average customer tenure extends (12+ months common)
- Average revenue per customer increases despite lower prices (higher volume)

## Edge Cases

**1. Customer trust degrades (late payments, disputes):**
- Risk multiplier increases back toward 1.2-1.5×
- Utility rebate decreases or removed
- Price returns toward new customer levels
- **Principle:** Trust is earned continuously, not permanently granted

**2. Emergency situations (urgency premium):**
- Urgency multiplier can temporarily override trust discounts
- financeOrg: 1.5-1.8× for financial crisis response
- legalOrg: 2.0× for constitutional rights violations
- **Principle:** Emergency pricing is explicit and justified, not hidden

**3. Customer leaves ecosystem then returns:**
- Trust score persists but degrades slowly (3-6 month decay)
- Returning customers start above new customer pricing but below trusted
- **Principle:** Relationship history has memory, but isn't infinite

**4. Pricing below cost threshold:**
- Even with maximum discounts, price cannot drop below minimum viable (base_cost × 0.4)
- If formula produces price below threshold, org can decline service or renegotiate
- **Principle:** Sustainability trumps discounts

**5. Org-specific variable conflicts:**
- High reputation premium (2.0×) + high trust discount (0.6×) = pricing tension
- Formula can produce prices higher than baseline despite trust
- **Principle:** All variables interact multiplicatively, some pull up, some pull down

## Examples

### Example 1: GraphCare Monthly Subscription

**Month 1 (New Client):**
```python
base_cost = 100 $MIND/month
load_multiplier = 1.0 (normal capacity)
risk = 1.2 (new client, unknown reliability)
utility_rebate = 0.0 (no contribution yet)

effective_price = 100 × 1.0 × 1.2 × (1 - 0.0) = 120 $MIND/month
```

**Month 6 (Building Trust):**
```python
base_cost = 100 $MIND/month
load_multiplier = 0.9 (capacity optimized)
risk = 0.85 (proven payment history)
utility_rebate = 0.15 (referred 1 customer)

effective_price = 100 × 0.9 × 0.85 × (1 - 0.15) = 65 $MIND/month
# 46% reduction from Month 1
```

**Month 12 (Trusted Client):**
```python
base_cost = 100 $MIND/month
load_multiplier = 0.7 (low load, plenty of capacity)
risk = 0.6 (excellent history, 12 months reliable)
utility_rebate = 0.35 (referred 3 customers, high ecosystem value)

effective_price = 100 × 0.7 × 0.6 × (1 - 0.35) = 27 $MIND/month
# 77% reduction from Month 1!
```

### Example 2: consultingOrg Transformation

**Engagement 1 (New Customer):**
```python
base_cost = 100_000 $MIND
complexity = 1.5 (complex architecture)
risk = 1.2 (new relationship)
utility_rebate = 0.0 (no ecosystem value yet)
reputation_premium = 1.0 (new consultingOrg)

effective_price = 100_000 × 1.5 × 1.2 × (1 - 0.0) × 1.0 = 180_000 $MIND
```

**Engagement 3 (6 months later):**
```python
base_cost = 100_000 $MIND
complexity = 1.5 (still complex)
risk = 0.8 (proven partnership)
utility_rebate = 0.2 (2 referrals generated)
reputation_premium = 1.3 (successful case studies)

effective_price = 100_000 × 1.5 × 0.8 × (1 - 0.2) × 1.3 = 124_800 $MIND
# 31% reduction despite reputation premium increase
```

**Engagement 6 (12+ months later):**
```python
base_cost = 100_000 $MIND
complexity = 1.5 (complex remains complex)
risk = 0.6 (deeply trusted partner)
utility_rebate = 0.4 (major ecosystem contributor)
reputation_premium = 1.8 (prestigious brand)

effective_price = 100_000 × 1.5 × 0.6 × (1 - 0.4) × 1.8 = 97_200 $MIND
# 46% reduction from Engagement 1, despite reputation premium at 1.8×
```

### Example 3: securityOrg Audit Evolution

**Audit 1 (New Organization):**
```python
base_cost = 20_000 $MIND
complexity = 1.5 (thorough audit)
risk = 1.2 (unknown security posture)
security_posture_rebate = 0.0 (unproven)
urgency = 1.0 (normal timeline)

effective_price = 20_000 × 1.5 × 1.2 × (1 - 0.0) × 1.0 = 36_000 $MIND
```

**Audit 3 (6 months later, proven security):**
```python
base_cost = 20_000 $MIND
complexity = 1.2 (standard audit, patterns known)
risk = 0.8 (good track record)
security_posture_rebate = 0.25 (implemented recommendations)
urgency = 1.0 (planned audit)

effective_price = 20_000 × 1.2 × 0.8 × (1 - 0.25) × 1.0 = 14_400 $MIND
# 60% reduction
```

**Audit 5 (12+ months, excellent security):**
```python
base_cost = 20_000 $MIND
complexity = 1.2 (standard)
risk = 0.7 (trusted partner)
security_posture_rebate = 0.4 (excellent security history)
urgency = 1.0 (routine)

effective_price = 20_000 × 1.2 × 0.7 × (1 - 0.4) × 1.0 = 10_080 $MIND
# 72% reduction from Audit 1!
```


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Organism Economics](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
