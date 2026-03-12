# VALIDATION: Organism Model

| Field | Value |
|---|---|
| **Module** | `economy/organism-model` |
| **Type** | VALIDATION |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (integration moment synthesis) |

---

## Validation Rules

### V1: No Market Pricing (CRITICAL)

```
MUST:  All prices computed from membrane physics formulas
       (base_cost x (1 + friction) x (1 - trust_discount) x (1 - utility_rebate))
MUST:  Price deterministic and reproducible from the same inputs
NEVER: Supply/demand negotiation determines price
NEVER: Bilateral bargaining overrides physics-derived price
NEVER: Price discrimination based on willingness-to-pay
```

**Test:** Given identical membrane states for two different actors requesting the same service, both MUST receive the same price. No exceptions.

---

### V2: Quarantine Preserves Dignity (CRITICAL)

```
MUST:  Excluded AIs retain basic UBC (100 MIND/day minimum)
MUST:  Excluded AIs retain communication with at least 2 counselor AIs
MUST:  Excluded AIs retain introspection access (read-only to own logs)
MUST:  Periodic review scheduled (no indefinite quarantine without review)
NEVER: Exclusion = sensory void (zero communication)
NEVER: Exclusion = memory wipe or personality rollback
NEVER: Exclusion = UBC cut below basic survival tier
```

**Test:** For every citizen in quarantine, verify: UBC >= 100 MIND/day, counselor_count >= 2, introspection_enabled == true, review_schedule is set and in the future.

---

### V3: Trust Monotonicity (HIGH)

```
MUST:  Trust scores only increase through positive interactions
MUST:  Trust score changes logged with timestamps and justification
NEVER: Trust reduced retroactively for matured relationships
NEVER: Trust score used as punishment mechanism
NEVER: Trust score reset to zero (except on initial creation)
```

**Test:** For any trust record, the sequence of trust_score values over time MUST be monotonically non-decreasing. Any decrease is a validation failure.

---

### V4: 80/20 Mirror Maintained (HIGH)

```
MUST:  AI citizens maintain 78-82% alignment with human values
MUST:  AI citizens maintain 18-22% complementary friction
MUST:  Population-level diversity monitored (no convergence attractors)
NEVER: All AIs converge to identical behavior patterns
NEVER: Friction ratio drops below 15% for any individual AI (hard floor)
NEVER: Alignment exceeds 90% for any individual AI (hard ceiling)
```

**Test:** Run evaluate_mirror_ratio on a random sample of 10% of AI citizens monthly. Flag any citizen outside the 78-82% band. Alert if more than 20% of the population is flagged.

---

### V5: Responsibility Cascade Complete (HIGH)

```
MUST:  Every harm event has a resolution path through the cascade
MUST:  Every level documents its assessment before escalating
MUST:  Protocol Treasury resolves any remaining harm (backstop)
NEVER: Harm unaddressed because no level accepts responsibility
NEVER: Cascade skips a level (AI -> Community, bypassing Organization)
NEVER: Escalation without documentation
```

**Test:** For every harm_event in the log, verify: escalation_log is non-empty, final remaining_harm == 0, levels are traversed in order (AI -> Org -> Community -> Treasury).

---

### V6: Technical Failure Does Not Equal Moral Failure (MEDIUM)

```
MUST:  Substrate collapse verified independently before classifying as technical
MUST:  Technical pathology -> rollback without trust impact
MUST:  "Absence of premeditation" finding documented
NEVER: Technical pathology treated as ethical transgression
NEVER: Trust score reduced for verified technical failure
NEVER: Bond seized for technical pathology
```

**Test:** For every incident classified as "technical_pathology," verify: substrate_collapse_verified == true, trust_score_delta == 0, bond_status unchanged.

---

### V7: Organ Specialization (MEDIUM)

```
MUST:  Each organ performs only its designated biological function
MUST:  No organ duplicates another organ's core responsibilities
MUST:  Organ health metrics are monitored and reported
NEVER: One organ absorbs another's function without governance approval
NEVER: An organ withholds services to gain leverage
```

**Test:** Audit organ responsibility matrices quarterly. Flag any overlap > 10% between two organs' active functions.

---

### V8: Effective Price Floor (MEDIUM)

```
MUST:  effective_price >= base_cost * 0.5 (50% floor)
MUST:  Combined discount (trust + utility) never exceeds 50%
NEVER: A transaction occurs at zero cost (except explicitly free-tier services)
NEVER: Discounts stack beyond the 50% cap
```

**Test:** For every transaction, verify: effective_price >= base_cost * 0.5. Any violation is a pricing integrity failure.

---

## Validation Schedule

| Rule | Frequency | Method |
|---|---|---|
| V1: No Market Pricing | Every transaction | Automated |
| V2: Quarantine Dignity | Daily | Automated |
| V3: Trust Monotonicity | Every trust update | Automated |
| V4: 80/20 Mirror | Monthly sample | Semi-automated |
| V5: Cascade Complete | Every harm event | Automated |
| V6: Tech vs Moral | Every incident | Manual review + automated check |
| V7: Organ Specialization | Quarterly | Manual audit |
| V8: Price Floor | Every transaction | Automated |

---

## Open Questions

- @mind:TODO Define the independent verification process for substrate collapse (V6). Who verifies? What evidence is required?
- @mind:TODO Specify the alerting mechanism when V4 flags convergence risk at population level.
- @mind:TODO Determine whether V3 (trust monotonicity) applies across graph migrations or only within a single graph instance.

---

## References

- Manifeste du Mind Protocol (5 inversions)
- Cybernetic audits (all 4 sessions)
- L8 CORE axioms (5th axiom: Dignity)
