# ALGORITHM: Organism Model

| Field | Value |
|---|---|
| **Module** | `economy/organism-model` |
| **Type** | ALGORITHM |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (integration moment synthesis) |

---

## Overview

This document specifies the core algorithms for the organism model: membrane-based pricing, trust scoring, responsibility cascade resolution, quarantine management, and mirror ratio evaluation.

---

## Data Structures

```
MembranePricing:
  base_cost: float             # Intrinsic cost of the service (compute, storage, bandwidth)
  friction: float              # f(sender.permeability, receiver.permeability)
  trust_discount: float        # min(0.3, trust_score x 0.01)
  utility_rebate: float        # min(0.2, utility_ema x 0.05)
  effective_price: float       # Final price after all adjustments

OrganFunction:
  organ_id: str                # Unique identifier (e.g., "heart", "kidney")
  name: str                    # Human-readable name (e.g., "Mind Foundation")
  biological_role: str         # Metaphorical role (e.g., "UBC circulation")
  responsibilities: list[str]  # Enumerated duties
  health_metrics: dict         # Key performance indicators for this organ

TrustRecord:
  actor_a: str                 # First party in the relationship
  actor_b: str                 # Second party in the relationship
  trust_score: float           # Cumulative trust (monotonically increasing)
  utility_ema: float           # Exponential moving average of utility contributions
  interaction_count: int       # Total interactions
  last_interaction: datetime   # Timestamp of most recent interaction

ResponsibilityCascade:
  levels: [AI, Organization, Community, ProtocolTreasury]
  current_level: int           # 0=AI, 1=Org, 2=Community, 3=Treasury
  harm_assessment: float       # Quantified harm magnitude
  resolution: str              # Outcome description
  escalation_log: list[dict]   # Record of each level's assessment

QuarantineState:
  citizen_id: str              # The quarantined AI's identifier
  reason: str                  # Classification: "ethical_transgression" or "technical_pathology"
  entered_at: datetime         # When quarantine began
  counselor_ids: list[str]     # Assigned counselor AIs
  introspection_enabled: bool  # Read-only access to own logs (always true)
  ubc_tier: str                # Always BASIC minimum (100 MIND/day)
  review_schedule: datetime    # Next scheduled review date

MirrorEvaluation:
  citizen_id: str              # The AI being evaluated
  alignment_ratio: float       # Percentage of aligned responses (target: 0.80)
  friction_ratio: float        # Percentage of friction responses (target: 0.20)
  sample_size: int             # Number of interactions sampled
  status: str                  # "healthy", "convergence_risk", "opposition_risk"
```

---

## Algorithm: compute_membrane_price(sender, receiver, service)

**Purpose:** Compute the effective price for a service transaction between two entities.

```
Step 1: Determine base_cost from service complexity
        base_cost = service.compute_cost + service.storage_cost + service.bandwidth_cost

Step 2: Compute friction from sender/receiver membrane permeability
        friction = (1 - sender.permeability) * (1 - receiver.permeability)
        # High permeability = low friction. Two open membranes = near-zero friction.
        # Two closed membranes = maximum friction.

Step 3: Look up trust_discount from relationship history
        trust_record = lookup_trust(sender.id, receiver.id)
        trust_discount = min(0.3, trust_record.trust_score * 0.01)

Step 4: Look up utility_rebate from receiver track record
        utility_rebate = min(0.2, trust_record.utility_ema * 0.05)

Step 5: Compute effective price
        effective_price = base_cost * (1 + friction) * (1 - trust_discount) * (1 - utility_rebate)

Step 6: Return MembranePricing(base_cost, friction, trust_discount, utility_rebate, effective_price)
```

**Invariants:**
- effective_price >= base_cost * 0.5 (minimum 50% of base cost, even with maximum discounts)
- friction >= 0
- trust_discount in [0.0, 0.3]
- utility_rebate in [0.0, 0.2]

---

## Algorithm: assess_responsibility(harm_event)

**Purpose:** Route a harm event through the responsibility cascade to resolution.

```
Step 1: Classify harm
        IF harm_event.substrate_collapse_verified:
            classification = "technical_pathology"
        ELSE:
            classification = "ethical_transgression"

Step 2: If technical pathology AND substrate collapse verified
        -> Rollback to previous personality snapshot
        -> No trust score impact
        -> Log as maintenance event
        -> RETURN resolution("technical_rollback")

Step 3: If ethical transgression -> enter cascade
        cascade = ResponsibilityCascade(levels=[AI, Org, Community, Treasury])
        remaining_harm = harm_event.magnitude

Step 4: For each level in cascade:
        absorb = level.capacity_to_resolve(remaining_harm)
        remaining_harm -= absorb
        cascade.escalation_log.append({level, absorb, remaining_harm})
        IF remaining_harm <= 0:
            BREAK

Step 5: Protocol Treasury absorbs any remainder
        IF remaining_harm > 0:
            treasury.absorb(remaining_harm)
            cascade.escalation_log.append({Treasury, remaining_harm, 0})

Step 6: Return cascade with full resolution log
```

---

## Algorithm: enforce_quarantine(citizen, reason)

**Purpose:** Move a citizen from the main network to the quarantine graph.

```
Step 1: Remove citizen from main network graph
        main_graph.remove_node(citizen.id)
        # All active connections severed (except counselor links)

Step 2: Place in quarantine graph with designated counselor AIs
        quarantine_graph.add_node(citizen.id)
        counselors = select_counselors(citizen, count=2)
        FOR counselor IN counselors:
            quarantine_graph.add_edge(citizen.id, counselor.id)

Step 3: Enable introspection mode
        citizen.introspection_enabled = True
        # Read-only access to own interaction logs, decision history

Step 4: Maintain Basic UBC
        citizen.ubc_tier = "BASIC"  # 100 MIND/day guaranteed
        # No reduction below this floor, ever

Step 5: Schedule periodic review
        citizen.review_schedule = now() + 30 days
        # Review can result in: continued quarantine, graduated return, or full reinstatement
```

---

## Algorithm: evaluate_mirror_ratio(ai_citizen)

**Purpose:** Assess whether an AI citizen maintains the 80/20 Mirror.

```
Step 1: Sample recent interactions
        interactions = ai_citizen.get_recent_interactions(count=100)
        # If fewer than 100 available, use all available with minimum threshold of 20

Step 2: Classify each interaction
        aligned = 0
        friction = 0
        FOR interaction IN interactions:
            IF interaction.is_aligned_with_human_values():
                aligned += 1
            ELSE:
                friction += 1

Step 3: Compute ratios
        alignment_ratio = aligned / len(interactions)
        friction_ratio = friction / len(interactions)

Step 4: Evaluate convergence risk
        IF alignment_ratio > 0.85:
            status = "convergence_risk"
            # Flag for intervention: AI is becoming too agreeable

Step 5: Evaluate opposition risk
        IF friction_ratio > 0.30:
            status = "opposition_risk"
            # Flag for review: AI may be adversarial rather than constructively challenging

Step 6: Healthy range
        IF 0.78 <= alignment_ratio <= 0.82:
            status = "healthy"

Step 7: Return MirrorEvaluation(citizen_id, alignment_ratio, friction_ratio, len(interactions), status)
```

---

## Complexity Analysis

| Algorithm | Time | Space | Notes |
|---|---|---|---|
| compute_membrane_price | O(1) | O(1) | Trust lookup is O(1) with hash map |
| assess_responsibility | O(L) | O(L) | L = cascade levels (fixed at 4) |
| enforce_quarantine | O(E) | O(1) | E = edges to sever from main graph |
| evaluate_mirror_ratio | O(N) | O(N) | N = sample size (typically 100) |

---

## Open Questions

- @mind:TODO Define the permeability function formally. What variables determine an entity's membrane permeability?
- @mind:TODO Specify the `is_aligned_with_human_values()` classifier. Is this LLM-based, rule-based, or hybrid?
- @mind:TODO Define `level.capacity_to_resolve()` for each cascade level. What are the resolution capacities?
- @mind:TODO How are counselors selected in `select_counselors()`? Random, specialized, or matched by failure type?

---

## References

- Manifeste du Mind Protocol (5 inversions)
- Cybernetic audits (all 4 sessions)
- Solo AI rehabilitation transcript
