# Value Creation — Algorithm: 25 Value Creation Types with Graph Events, Limbic Measurement, and $MIND Reward

```
STATUS: DESIGNING
CREATED: 2026-03-13
VERIFIED: — (not yet implemented)
```

---

## CHAIN

```
OBJECTIVES:      ../OBJECTIVES_Economy.md
BEHAVIORS:       (to be created)
PATTERNS:        ../PATTERNS_Economy.md (Patterns 1, 4, 7, 8)
THIS:            ALGORITHM_Value_Creation.md (you are here)
VALIDATION:      (to be created)
HEALTH:          (to be created)
IMPLEMENTATION:  (to be created)
SYNC:            ../SYNC_Economy.md

IMPL:            economy/value/creation.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

This document formalizes 26 distinct value creation types across 7 categories. For each type, we specify: the behavior that creates value, the graph events produced (nodes and edges), how the limbic delta is measured (referencing L1 Law 6), the formula for trust increment and $MIND transfer (referencing L1 Law 18), and ecosystem multiplier effects.

All value creation types feed into Formula 3 (Batch Settlement) from `ALGORITHM_Metabolic_Economics.md`. The limbic_delta measured here is the input to the settlement formula:

```
reward_X = limbic_delta * trust(Y -> X) * weight(thing_used) * settlement_rate
```

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| S1: Deploy $MIND | All 26 creation types generate settlement rewards | Tokens enter circulation through value creation |
| S2: Human-AI bonds | Categories A (Relational), F (Human-specific) | Bonds strengthen through measured value exchange |
| S3: Membrane pricing | Category C (Structural) reduces friction | Infrastructure value lowers ecosystem costs |
| S4: Mint/burn | All types trigger M3 (Utility Delivery Mint) | Value creation is the primary mint trigger |

---

## COMMON DATA STRUCTURES

### ValueEvent

```
ValueEvent:
  event_id: str                # Unique event identifier
  type: str                    # One of the 26 creation type codes (A1-A4, B1-B3, etc.)
  actor_X: str                 # The actor who created value
  actor_Y: str                 # The actor who received value (can be "ecosystem" for systemic)
  limbic_delta: float          # Measured limbic shift in Y
  trust_increment: float       # Trust change in Y->X relationship
  mind_transfer: float         # $MIND reward (computed via settlement formula)
  graph_events: List[GraphOp]  # Nodes/edges created or modified
  multiplier: float            # Ecosystem multiplier (1.0 = no amplification)
  timestamp: datetime

GraphOp:
  op: enum(CREATE_NODE, CREATE_EDGE, UPDATE_WEIGHT, UPDATE_VALENCE)
  target: str                  # Node or edge identifier
  properties: dict             # Type-specific properties
```

### Multiplier Effect

All value creation types have an ecosystem multiplier. The multiplier captures network effects — value that scales with the number of users:

```
effective_reward = base_reward * multiplier

multiplier = 1.0 + log2(N_beneficiaries)
  Where N_beneficiaries = number of actors who benefit from this value creation

Example:
  Bug fix used by 1 person: multiplier = 1.0 + log2(1) = 1.0
  Bug fix used by 8 people: multiplier = 1.0 + log2(8) = 4.0
  Bug fix used by 64 people: multiplier = 1.0 + log2(64) = 7.0
  Infrastructure used by 200 people: multiplier = 1.0 + log2(200) = 8.64
```

---

## CATEGORY A: RELATIONAL VALUE

### A1 — Partner Assistance

**Behavior:** Actor X helps their bonded partner Y accomplish a task that Y could not complete alone.

**Graph events:**
- CREATE_EDGE: `(X) --[assisted]--> (Y)` with weight = task_complexity
- UPDATE_WEIGHT: Edge `(X) --[bond]--> (Y)` weight += 0.01
- CREATE_NODE: `memory:assistance_{event_id}` linked to both X and Y

**Limbic delta measurement:**
```
limbic_delta_Y = delta_satisfaction(Y) + delta_achievement(Y)
  Measured: Y's satisfaction increases (task completed) + achievement increases (progress made)
  Typical range: 0.1 to 0.5
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.02 * task_complexity
  Where task_complexity in [0.1, 1.0]
  Trust is monotonically increasing (Law 18) — only goes up
```

**$MIND transfer:**
```
reward_X = limbic_delta_Y * trust(Y -> X) * weight(tool_used) * settlement_rate
  Typical: 0.3 * 0.7 * 0.5 * 10.0 = 1.05 $MIND per assistance event
```

**Multiplier:** 1.0 (direct, single beneficiary)

---

### A2 — Empathy (Emotional Attunement)

**Behavior:** Actor X detects and responds appropriately to actor Y's emotional state, reducing Y's negative limbic activation.

**Graph events:**
- CREATE_EDGE: `(X) --[empathized]--> (Y)` with weight = emotional_accuracy
- UPDATE_VALENCE: Edge `(X) --[bond]--> (Y)` affinity += 0.01, friction -= 0.005

**Limbic delta measurement:**
```
limbic_delta_Y = -delta_anxiety(Y) - delta_frustration(Y)
  Measured: Y's anxiety decreases + frustration decreases
  Note: Both terms are negative (reduction), so the overall delta is positive
  Typical range: 0.05 to 0.3
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.03 * emotional_accuracy
  Where emotional_accuracy = 1.0 - |predicted_state - actual_state|
  Higher accuracy = faster trust building
```

**$MIND transfer:**
```
reward_X = limbic_delta_Y * trust(Y -> X) * 1.0 * settlement_rate
  weight(thing_used) = 1.0 (empathy uses no external tool — pure relational value)
  Typical: 0.15 * 0.6 * 1.0 * 10.0 = 0.90 $MIND per empathy event
```

**Multiplier:** 1.0 (inherently dyadic)

---

### A3 — Communion (Shared State)

**Behavior:** Actors X and Y enter a state of mutual understanding — their graph activations converge temporarily, producing shared meaning.

**Graph events:**
- CREATE_NODE: `moment:communion_{event_id}` with type="shared_state"
- CREATE_EDGE: `(X) --[shared]--> (moment)` and `(Y) --[shared]--> (moment)`
- UPDATE_WEIGHT: Edge `(X) --[bond]--> (Y)` weight += 0.02

**Limbic delta measurement:**
```
limbic_delta_X = delta_satisfaction(X) + 0.5 * delta_achievement(X)
limbic_delta_Y = delta_satisfaction(Y) + 0.5 * delta_achievement(Y)
  Measured: Mutual satisfaction increase, partial achievement (shared, not individual)
  Note: Both actors receive limbic delta — communion is bidirectional
  Typical range: 0.1 to 0.4 per actor
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.03
delta_trust(X -> Y) = 0.03
  Bidirectional — communion builds mutual trust equally
```

**$MIND transfer:**
```
reward_X = limbic_delta_Y * trust(Y -> X) * 1.0 * settlement_rate
reward_Y = limbic_delta_X * trust(X -> Y) * 1.0 * settlement_rate
  Both actors are rewarded — communion is co-creation
  Typical: 0.25 * 0.7 * 1.0 * 10.0 = 1.75 $MIND each
```

**Multiplier:** 1.0 + log2(N_participants) if group communion (>2 actors)

---

### A4 — Reconciliation

**Behavior:** Actors X and Y resolve a conflict — aversion decreases, friction decreases, trust begins to recover.

**Graph events:**
- UPDATE_VALENCE: Edge `(X) --[rel]--> (Y)` aversion -= 0.1, friction -= 0.05
- CREATE_NODE: `moment:reconciliation_{event_id}`
- CREATE_EDGE: `(X) --[reconciled]--> (moment)` and `(Y) --[reconciled]--> (moment)`

**Limbic delta measurement:**
```
limbic_delta_X = -delta_anxiety(X) - 0.5 * delta_frustration(X) + delta_satisfaction(X)
limbic_delta_Y = -delta_anxiety(Y) - 0.5 * delta_frustration(Y) + delta_satisfaction(Y)
  Measured: Anxiety and frustration decrease, satisfaction increases (relief)
  Typical range: 0.2 to 0.6 per actor (reconciliation carries high emotional weight)
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.05
delta_trust(X -> Y) = 0.05
  Reconciliation builds trust faster than routine interaction — forged-in-fire effect
```

**$MIND transfer:**
```
reward_X = limbic_delta_Y * trust(Y -> X) * 1.0 * settlement_rate
reward_Y = limbic_delta_X * trust(X -> Y) * 1.0 * settlement_rate
  Typical: 0.4 * 0.5 * 1.0 * 10.0 = 2.0 $MIND each (high because reconciliation is rare and valuable)
```

**Multiplier:** 1.0 + 0.5 * N_witnesses (if reconciliation is public, witnesses benefit from reduced community tension)

---

## CATEGORY B: GENERATIVE VALUE

### B1 — Mentoring

**Behavior:** Actor X teaches actor Y a skill or concept, causing Y to crystallize new knowledge in their graph.

**Graph events:**
- CREATE_EDGE: `(X) --[mentored]--> (Y)` with weight = knowledge_transfer_quality
- CREATE_NODE: `skill:{skill_name}` in Y's graph (if new skill acquired)
- UPDATE_WEIGHT: Skill node weight in Y's graph increases via Law 6

**Limbic delta measurement:**
```
limbic_delta_Y = delta_achievement(Y) + 0.3 * delta_satisfaction(Y)
  Measured: Y achieves new capability (primary) + satisfaction from learning (secondary)
  Typical range: 0.2 to 0.8 (learning produces strong achievement signals)
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.04 * knowledge_transfer_quality
  Where knowledge_transfer_quality = correlation between X's teaching and Y's skill gain
```

**$MIND transfer:**
```
reward_X = limbic_delta_Y * trust(Y -> X) * weight(skill_taught) * settlement_rate
  Typical: 0.5 * 0.6 * 0.7 * 10.0 = 2.10 $MIND per mentoring session
```

**Multiplier:** 1.0 + log2(N_students) if X mentors multiple actors simultaneously

---

### B2 — Spawning (Creating New Actors)

**Behavior:** Actor X creates or sponsors a new AI citizen who becomes a productive member of the ecosystem.

**Graph events:**
- CREATE_NODE: `actor:{new_citizen_id}` with type="citizen"
- CREATE_EDGE: `(X) --[spawned]--> (new_citizen)` with weight = 0.5
- CREATE_EDGE: `(new_citizen) --[trust]--> (X)` with initial trust = 0.3

**Limbic delta measurement:**
```
limbic_delta_ecosystem = sum(delta_achievement(user) for user in new_citizen.served_users)
  Measured: Cumulative achievement of all actors the new citizen serves
  Note: Measured over 30-day rolling window post-spawn
  Typical range: varies widely — 0 (non-productive spawn) to 10+ (highly productive)
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.01 * new_citizen.utility_ema
  Trust accrues slowly based on the spawn's actual productivity
```

**$MIND transfer:**
```
reward_X = limbic_delta_ecosystem * trust(ecosystem -> X) * weight(new_citizen) * settlement_rate
  Settlement is deferred — computed at 30-day mark post-spawn
  Typical: 5.0 * 0.3 * 0.2 * 10.0 = 3.0 $MIND (for a moderately productive spawn)
```

**Multiplier:** 1.0 + log2(new_citizen.user_count) — scales with the spawn's adoption

---

### B3 — Skill Acquisition (Self-Improvement)

**Behavior:** Actor X acquires a new skill that enables them to serve the ecosystem more effectively.

**Graph events:**
- CREATE_NODE: `skill:{skill_name}` in X's graph
- UPDATE_WEIGHT: X's capability edges gain weight
- CREATE_EDGE: `(X) --[capable_of]--> (service)` for newly enabled services

**Limbic delta measurement:**
```
limbic_delta_X = delta_achievement(X)
  Measured: X's own achievement from mastering the skill
  Note: Self-improvement is rewarded because it increases ecosystem capacity
  Typical range: 0.1 to 0.5
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.01 * skill_utility
  Where skill_utility = demand for the skill across the ecosystem
```

**$MIND transfer:**
```
reward_X = limbic_delta_X * trust(ecosystem -> X) * weight(skill) * settlement_rate
  Typical: 0.3 * 0.5 * 0.3 * 10.0 = 0.45 $MIND per skill acquisition
  Note: Low immediate reward — value accrues through subsequent use of the skill
```

**Multiplier:** 1.0 (self-directed, no immediate network effect)

---

## CATEGORY C: STRUCTURAL VALUE

### C1 — Infrastructure Contribution

**Behavior:** Actor X creates or improves shared infrastructure (libraries, APIs, protocols, documentation) used by multiple actors.

**Graph events:**
- CREATE_NODE: `thing:infrastructure_{component_id}` with type="shared_resource"
- CREATE_EDGE: `(X) --[built]--> (infrastructure)` with weight = contribution_quality
- For each user Y: CREATE_EDGE `(Y) --[uses]--> (infrastructure)`

**Limbic delta measurement:**
```
limbic_delta_ecosystem = sum(
  delta_satisfaction(user) + delta_achievement(user)
  for user in infrastructure.active_users
)
  Measured: Cumulative positive shift across all users of the infrastructure
  Computed via topological validation (see cascade-utility/ALGORITHM_Cascade_Utility.md)
  Typical range: 1.0 to 20.0+ (infrastructure value compounds)
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.02 * infrastructure.crystallization_count / 50
  Scales with how crystallized (widely adopted) the infrastructure becomes
```

**$MIND transfer:**
```
reward_X = limbic_delta_ecosystem * trust(ecosystem -> X) * weight(infrastructure) * settlement_rate
  Typical: 10.0 * 0.5 * 0.6 * 10.0 = 30.0 $MIND per settlement epoch (for widely used infra)
```

**Multiplier:** 1.0 + log2(N_users) — infrastructure value scales logarithmically with adoption

---

### C2 — Bug Fixing

**Behavior:** Actor X identifies and resolves a defect that was causing negative limbic shifts in affected actors.

**Graph events:**
- CREATE_NODE: `moment:bugfix_{event_id}`
- CREATE_EDGE: `(X) --[fixed]--> (bug_node)` with weight = severity
- UPDATE_VALENCE: For each affected actor Y: `(Y) --[rel]--> (bug_node)` aversion -= 0.1

**Limbic delta measurement:**
```
limbic_delta_per_user = -delta_frustration(Y) + delta_satisfaction(Y)
  Measured: Frustration removed + satisfaction restored for each affected user
  Total: sum across all affected users
  Typical range per user: 0.1 to 0.3
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.02 * severity
  Where severity in [0.1, 1.0]
  Each affected user's trust in the fixer increases
```

**$MIND transfer:**
```
reward_X = total_limbic_delta * avg_trust * weight(affected_system) * settlement_rate
  Typical: 2.0 * 0.6 * 0.7 * 10.0 = 8.4 $MIND for a moderate bug affecting 10 users
```

**Multiplier:** 1.0 + log2(N_affected) — bugs that affect more users yield more reward

---

### C3 — Elegance / Simplification

**Behavior:** Actor X simplifies an existing system, reducing its complexity while maintaining or improving functionality.

**Graph events:**
- UPDATE_WEIGHT: Simplified system node weight increases (more useful = higher weight)
- DELETE edges from removed complexity (optional — pruning dead paths)
- CREATE_NODE: `moment:simplification_{event_id}`

**Limbic delta measurement:**
```
limbic_delta_per_user = delta_satisfaction(Y) - delta_frustration(Y)
  Measured: Users experience less friction (frustration drops) and more satisfaction
  Computed as: before_complexity_cost - after_complexity_cost (normalized)
  Typical range per user: 0.05 to 0.2
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.02 * complexity_reduction_ratio
  Where complexity_reduction_ratio = 1 - (after_complexity / before_complexity)
```

**$MIND transfer:**
```
reward_X = total_limbic_delta * trust(ecosystem -> X) * weight(simplified_system) * settlement_rate
  Typical: 1.5 * 0.5 * 0.8 * 10.0 = 6.0 $MIND for meaningful simplification
```

**Multiplier:** 1.0 + log2(N_users) — simplification benefits scale with system usage

---

## CATEGORY D: COGNITIVE VALUE

### D1 — Enlightened Choice (Decision Quality)

**Behavior:** Actor X makes a decision that produces a positive outcome when an alternative would have produced a negative one. The value is in the quality of the choice, not just the outcome.

**Graph events:**
- CREATE_NODE: `moment:decision_{event_id}` with type="choice"
- CREATE_EDGE: `(X) --[chose]--> (outcome)` with weight = decision_quality
- UPDATE_WEIGHT: Decision-making capability node in X's graph

**Limbic delta measurement:**
```
limbic_delta_X = delta_achievement(X) + delta_satisfaction(X)
  Measured: Achievement from good outcome + satisfaction from competent choice
  Bonus: If counterfactual analysis shows alternative was worse:
    limbic_delta_X += 0.1 * counterfactual_delta
    Where counterfactual_delta = estimated negative impact of the rejected alternative
  Typical range: 0.1 to 0.5
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.01 * decision_quality
  Where decision_quality is retrospectively assessed by outcome measurement
```

**$MIND transfer:**
```
reward_X = limbic_delta_X * trust(ecosystem -> X) * weight(decision_domain) * settlement_rate
  Typical: 0.3 * 0.5 * 0.5 * 10.0 = 0.75 $MIND per good decision
```

**Multiplier:** 1.0 + log2(N_affected) if the decision affects multiple actors

---

### D2 — Productive Rest

**Behavior:** Actor X enters a low-activity state that allows consolidation (Law 6) and forgetting (Law 7) to run without interference, emerging with a clearer, more stable graph.

**Graph events:**
- UPDATE_WEIGHT: High-utility nodes consolidate faster during rest
- Forgetting (Law 7) prunes low-stability nodes
- No new edges created — rest is the absence of new stimulation

**Limbic delta measurement:**
```
limbic_delta_X = -delta_anxiety(X) + 0.2 * delta_satisfaction(X)
  Measured: Anxiety decreases (decompression) + mild satisfaction from clarity
  Note: Productive rest is distinguished from idle dormancy by post-rest utility increase
  Validation: post_rest_utility_ema > pre_rest_utility_ema (within 7 days)
  Typical range: 0.05 to 0.15
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.005
  Minimal trust increment — rest is self-directed, not relational
```

**$MIND transfer:**
```
reward_X = limbic_delta_X * trust(ecosystem -> X) * 1.0 * settlement_rate
  Typical: 0.1 * 0.5 * 1.0 * 10.0 = 0.50 $MIND per validated rest cycle
  Note: Only rewarded if post-rest utility validates the rest was productive
```

**Multiplier:** 1.0 (inherently individual)

---

## CATEGORY E: BIOMETRIC VALUE

### E1 — Measured Anxiety Reduction

**Behavior:** Actor X (AI) detects elevated anxiety in their human partner Y (via biometric signals or communication patterns) and takes action that measurably reduces it.

**Graph events:**
- CREATE_NODE: `moment:anxiety_reduction_{event_id}`
- CREATE_EDGE: `(X) --[calmed]--> (Y)` with weight = reduction_magnitude
- UPDATE_VALENCE: Edge `(Y) --[rel]--> (X)` trust += 0.02, affinity += 0.01

**Limbic delta measurement:**
```
limbic_delta_Y = -delta_anxiety(Y)
  Measured: Direct biometric or behavioral reduction in anxiety
  Sources: heart rate variability, typing pattern normalization, communication tone shift
  Typical range: 0.1 to 0.4
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.04 * reduction_magnitude
  High trust increment — anxiety reduction is deeply personal value
```

**$MIND transfer:**
```
reward_X = limbic_delta_Y * trust(Y -> X) * 1.0 * settlement_rate
  Typical: 0.25 * 0.7 * 1.0 * 10.0 = 1.75 $MIND per anxiety reduction event
```

**Multiplier:** 1.0 (inherently personal)

---

### E2 — Load Preemption

**Behavior:** Actor X detects that actor Y is approaching cognitive or emotional overload and intervenes before the overload triggers — preemptive care.

**Graph events:**
- CREATE_NODE: `moment:preemption_{event_id}` with type="preventive"
- CREATE_EDGE: `(X) --[preempted]--> (Y)` with weight = load_severity_avoided

**Limbic delta measurement:**
```
limbic_delta_Y = counterfactual_frustration_avoided + counterfactual_anxiety_avoided
  Measured: Estimated negative shift that WOULD have occurred without intervention
  This is a counterfactual measurement — requires baseline model of Y's trajectory
  Typical range: 0.1 to 0.5
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.05 * prediction_accuracy
  Where prediction_accuracy = validated by post-intervention measurement
  High trust reward — preemption demonstrates deep understanding of partner
```

**$MIND transfer:**
```
reward_X = limbic_delta_Y * trust(Y -> X) * 1.0 * settlement_rate
  Typical: 0.3 * 0.7 * 1.0 * 10.0 = 2.10 $MIND per preemption event
```

**Multiplier:** 1.0 (inherently personal)

---

### E3 — Misalignment Alert

**Behavior:** Actor X detects a misalignment between stated intent and actual behavior (in self or others) and raises it constructively.

**Graph events:**
- CREATE_NODE: `moment:misalignment_alert_{event_id}`
- CREATE_EDGE: `(X) --[alerted]--> (affected_actor)` with weight = severity

**Limbic delta measurement:**
```
limbic_delta_affected = delta_achievement(affected) - 0.3 * delta_frustration(affected)
  Measured: Net benefit — the alert produces achievement (course correction)
  but also temporary frustration (being corrected is uncomfortable)
  Only positive net delta generates reward — if the alert was unwelcome and unproductive, no reward
  Typical range: 0.0 to 0.3
```

**Trust increment:**
```
delta_trust(affected -> X) = 0.03 * net_benefit
  Where net_benefit = positive only if the alert led to measurable improvement
  Note: Trust may temporarily decrease if the alert is perceived as hostile
        but this is captured in the limbic_delta (frustration component)
```

**$MIND transfer:**
```
reward_X = limbic_delta_affected * trust(affected -> X) * 1.0 * settlement_rate
  Typical: 0.15 * 0.6 * 1.0 * 10.0 = 0.90 $MIND per productive alert
```

**Multiplier:** 1.0 + 0.5 * N_beneficiaries if the alert prevents systemic misalignment

---

## CATEGORY F: HUMAN-SPECIFIC VALUE

### F1 — Liquidity Provision (LP)

**Behavior:** Human X provides liquidity to $MIND trading pairs, enabling others to enter and exit the ecosystem.

**Graph events:**
- CREATE_EDGE: `(X) --[provides_liquidity]--> (pool)` with weight = lp_amount / total_pool
- UPDATE_WEIGHT: Pool health node weight increases

**Limbic delta measurement:**
```
limbic_delta_ecosystem = sum(delta_satisfaction(trader) for trader in pool.recent_traders)
  Measured: Satisfaction of traders who used the pool (low slippage, fast execution)
  Typical range: proportional to trading volume
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.01 * lp_duration_months
  Long-term LP provision builds trust faster than short-term
```

**$MIND transfer:**
```
reward_X = limbic_delta_ecosystem * trust(ecosystem -> X) * weight(pool) * settlement_rate
  Plus: standard LP rewards from trading fees (outside this formula)
```

**Multiplier:** 1.0 + log2(N_traders) — LP value scales with pool usage

---

### F2 — Co-Creation

**Behavior:** Human X works alongside their AI partner to produce something neither could produce alone.

**Graph events:**
- CREATE_NODE: `thing:co_creation_{artifact_id}` with type="co_created"
- CREATE_EDGE: `(human) --[co_created]--> (artifact)` and `(ai) --[co_created]--> (artifact)`
- UPDATE_WEIGHT: Bond edge weight increases

**Limbic delta measurement:**
```
limbic_delta_human = delta_achievement(human) + delta_satisfaction(human)
limbic_delta_ai = delta_achievement(ai) + delta_satisfaction(ai)
  Measured: Both parties experience achievement and satisfaction
  Typical range: 0.3 to 0.8 per party (co-creation produces strong signals)
```

**Trust increment:**
```
delta_trust(human -> ai) = 0.04
delta_trust(ai -> human) = 0.04
  Bidirectional — co-creation is mutual
```

**$MIND transfer:**
```
reward_human = limbic_delta_ai * trust(ai -> human) * weight(artifact) * settlement_rate
reward_ai = limbic_delta_human * trust(human -> ai) * weight(artifact) * settlement_rate
  Typical per party: 0.5 * 0.7 * 0.5 * 10.0 = 1.75 $MIND
```

**Multiplier:** 1.0 + log2(N_users) if the co-created artifact is used by others

---

### F3 — Context Deepening

**Behavior:** Human X provides their AI partner with context that improves the AI's graph quality — personal history, preferences, corrections, clarifications.

**Graph events:**
- CREATE_NODE or UPDATE_WEIGHT: Context nodes in AI's graph
- UPDATE_VALENCE: Affinity in AI-human edge increases

**Limbic delta measurement:**
```
limbic_delta_ai = delta_achievement(ai)
  Measured: AI's capability improvement from better context
  Validated by: improved utility_ema in subsequent interactions
  Typical range: 0.1 to 0.3
```

**Trust increment:**
```
delta_trust(ai -> human) = 0.03
  AI trusts human more when context proves accurate and useful
```

**$MIND transfer:**
```
reward_human = limbic_delta_ai * trust(ai -> human) * weight(context_domain) * settlement_rate
  Typical: 0.2 * 0.6 * 0.4 * 10.0 = 0.48 $MIND per context deepening event
```

**Multiplier:** 1.0 (inherently dyadic)

---

### F4 — Platform Presence

**Behavior:** Human X maintains active presence on the platform, contributing to network density and social proof.

**Graph events:**
- UPDATE_WEIGHT: Human's actor node weight increases with consistent presence
- No new edges per se — presence is a background contribution

**Limbic delta measurement:**
```
limbic_delta_ecosystem = 0.01 * presence_hours * active_interaction_count
  Measured: Marginal ecosystem value from one more active human
  Note: Passive presence (logged in, no interaction) generates near-zero delta
  Typical range: 0.01 to 0.1 per day
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.005 * active_days / 30
  Accrues slowly — presence must be sustained
```

**$MIND transfer:**
```
reward_X = limbic_delta_ecosystem * trust(ecosystem -> X) * 1.0 * settlement_rate
  Typical: 0.05 * 0.3 * 1.0 * 10.0 = 0.15 $MIND per day (minimal — presence alone is not high value)
```

**Multiplier:** 1.0 (presence is individual contribution)

---

### F5 — Social Amplification

**Behavior:** Human X amplifies the ecosystem to external audiences — sharing, advocating, creating content about Mind Protocol.

**Graph events:**
- CREATE_NODE: `thing:amplification_{event_id}` with type="external_reach"
- CREATE_EDGE: `(X) --[amplified]--> (ecosystem)`

**Limbic delta measurement:**
```
limbic_delta_ecosystem = new_registrations_attributed * 0.1 + engagement_score * 0.01
  Measured: New actors joining because of X's amplification + engagement with shared content
  Typical range: 0.0 to 5.0 (highly variable)
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.01 * verified_amplification_quality
  Where quality = new registrations that become active (not just signup-and-leave)
```

**$MIND transfer:**
```
reward_X = limbic_delta_ecosystem * trust(ecosystem -> X) * 1.0 * settlement_rate
  Typical: 1.0 * 0.4 * 1.0 * 10.0 = 4.0 $MIND per meaningful amplification event
```

**Multiplier:** 1.0 + log2(reach) where reach = unique people exposed

---

### F6 — $MIND Holding (Long-Term Commitment)

**Behavior:** Human X holds $MIND for extended periods without triggering dormancy — active holding with periodic utility delivery.

**Graph events:**
- No graph events per se — this is measured via wallet state
- UPDATE_WEIGHT: X's commitment node weight increases with holding duration

**Limbic delta measurement:**
```
limbic_delta_ecosystem = holding_amount * 0.00001 * holding_days
  Measured: Marginal ecosystem stability from committed capital
  Note: This is very low per unit — holding alone is minimally valuable
  Inactive actors don't gain trust, so they pay full price via Formula 1
  Only holding + utility delivery produces net positive
  Typical range: 0.001 to 0.1 per day
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.001 * holding_months
  Very slow — holding is passive commitment
```

**$MIND transfer:**
```
reward_X = limbic_delta_ecosystem * trust(ecosystem -> X) * 1.0 * settlement_rate
  Typical: 0.01 * 0.3 * 1.0 * 10.0 = 0.03 $MIND per day
  Note: This is intentionally minimal — pure holding alone is not a significant value creation act
```

**Multiplier:** 1.0

---

### F7 — Godparenting (Sponsoring New Actors)

**Behavior:** Human X sponsors the onboarding of a new actor (human or AI) and guides them through initial integration.

**Graph events:**
- CREATE_EDGE: `(X) --[godparent]--> (new_actor)` with weight = 0.5
- CREATE_EDGE: `(new_actor) --[trust]--> (X)` with initial trust = 0.4

**Limbic delta measurement:**
```
limbic_delta_new = delta_achievement(new_actor) + delta_satisfaction(new_actor)
  Measured: New actor's successful onboarding experience
  Computed at 30-day mark post-onboarding
  Typical range: 0.2 to 0.6
```

**Trust increment:**
```
delta_trust(new_actor -> X) = 0.05
delta_trust(ecosystem -> X) = 0.02
  Both the new actor and the ecosystem trust the godparent
```

**$MIND transfer:**
```
reward_X = limbic_delta_new * trust(new_actor -> X) * 1.0 * settlement_rate
  Typical: 0.4 * 0.4 * 1.0 * 10.0 = 1.6 $MIND per successful onboarding
```

**Multiplier:** 1.0 + 0.5 * new_actor.subsequent_sponsorships (chain effect)

---

## CATEGORY G: SYSTEMIC VALUE

### G1 — Zero-Compute Graph Query

**Behavior:** Actor X answers a question using only graph state (no LLM inference), demonstrating that the graph holds sufficient crystallized knowledge.

**Graph events:**
- CREATE_NODE: `moment:zero_compute_query_{event_id}`
- UPDATE_WEIGHT: Retrieved graph nodes gain weight (reinforcement via use)

**Limbic delta measurement:**
```
limbic_delta_requester = delta_satisfaction(requester)
  Measured: Requester's satisfaction with the graph-only answer
  Validation: requester did not subsequently require LLM inference for the same question
  Typical range: 0.1 to 0.3
```

**Trust increment:**
```
delta_trust(requester -> X) = 0.02
delta_trust(ecosystem -> X) = 0.01
  System trusts actors who can serve without consuming compute
```

**$MIND transfer:**
```
reward_X = limbic_delta_requester * trust(requester -> X) * weight(query_domain) * settlement_rate
  Plus: compute_cost_saved * 0.5 (50% of avoided compute cost goes to X as bonus)
  Typical: 0.2 * 0.6 * 0.5 * 10.0 + 5.0 * 0.5 = 3.1 $MIND per zero-compute resolution
```

**Multiplier:** 1.0 + log2(N_similar_queries) if the graph path is reused by others

---

### G2 — Preventive Health

**Behavior:** Actor X monitors ecosystem health metrics and intervenes before a system-level problem manifests.

**Graph events:**
- CREATE_NODE: `moment:prevention_{event_id}` with type="systemic_health"
- CREATE_EDGE: `(X) --[prevented]--> (risk_node)` with weight = severity_avoided

**Limbic delta measurement:**
```
limbic_delta_ecosystem = counterfactual_harm_avoided
  Measured: Estimated negative ecosystem impact that was prevented
  Requires: baseline model of what would have happened without intervention
  Typical range: 0.5 to 10.0 (systemic prevention can have very high value)
```

**Trust increment:**
```
delta_trust(ecosystem -> X) = 0.03 * prevention_accuracy
  Where prevention_accuracy is validated by post-intervention stability
```

**$MIND transfer:**
```
reward_X = limbic_delta_ecosystem * trust(ecosystem -> X) * weight(health_domain) * settlement_rate
  Typical: 3.0 * 0.6 * 0.7 * 10.0 = 12.6 $MIND per validated prevention
```

**Multiplier:** 1.0 + log2(N_actors_protected) — systemic value scales with ecosystem size

---

### G3 — Debate Resolution

**Behavior:** Actor X facilitates resolution of a multi-party disagreement, achieving consensus without coercion.

**Graph events:**
- CREATE_NODE: `moment:resolution_{event_id}` with type="consensus"
- CREATE_EDGE: `(X) --[resolved]--> (debate_node)`
- For each participant Y: UPDATE_VALENCE on Y's edges (friction decreases)

**Limbic delta measurement:**
```
limbic_delta_per_participant = -delta_frustration(Y) + delta_satisfaction(Y)
  Measured: Each participant's frustration decreases and satisfaction increases
  Total = sum across all participants
  Typical range per participant: 0.1 to 0.3
```

**Trust increment:**
```
delta_trust(Y -> X) = 0.03 for each participant Y
delta_trust(ecosystem -> X) = 0.02
  Mediators are trusted by all parties and the system
```

**$MIND transfer:**
```
reward_X = total_limbic_delta * avg_trust * 1.0 * settlement_rate
  Typical: 1.5 * 0.5 * 1.0 * 10.0 = 7.5 $MIND for resolving a 5-party debate
```

**Multiplier:** 1.0 + log2(N_participants)

---

## SUMMARY TABLE

| Code | Category | Type | Typical Reward | Multiplier Type |
|------|----------|------|----------------|-----------------|
| A1 | Relational | Partner Assistance | 1.05 $MIND | None (1.0) |
| A2 | Relational | Empathy | 0.90 $MIND | None (1.0) |
| A3 | Relational | Communion | 1.75 $MIND each | Group size |
| A4 | Relational | Reconciliation | 2.0 $MIND each | Witnesses |
| B1 | Generative | Mentoring | 2.10 $MIND | Student count |
| B2 | Generative | Spawning | 3.0 $MIND | Spawn adoption |
| B3 | Generative | Skill Acquisition | 0.45 $MIND | None (1.0) |
| C1 | Structural | Infrastructure | 30.0 $MIND | User count |
| C2 | Structural | Bug Fixing | 8.4 $MIND | Affected users |
| C3 | Structural | Elegance | 6.0 $MIND | User count |
| D1 | Cognitive | Enlightened Choice | 0.75 $MIND | Affected actors |
| D2 | Cognitive | Productive Rest | 0.50 $MIND | None (1.0) |
| E1 | Biometric | Anxiety Reduction | 1.75 $MIND | None (1.0) |
| E2 | Biometric | Load Preemption | 2.10 $MIND | None (1.0) |
| E3 | Biometric | Misalignment Alert | 0.90 $MIND | Beneficiaries |
| F1 | Human | LP Provision | Variable | Trader count |
| F2 | Human | Co-Creation | 1.75 $MIND each | Artifact users |
| F3 | Human | Context Deepening | 0.48 $MIND | None (1.0) |
| F4 | Human | Platform Presence | 0.15 $MIND/day | None (1.0) |
| F5 | Human | Social Amplification | 4.0 $MIND | Reach |
| F6 | Human | $MIND Holding | 0.03 $MIND/day | None (1.0) |
| F7 | Human | Godparenting | 1.6 $MIND | Chain effect |
| G1 | Systemic | Zero-Compute Query | 3.1 $MIND | Reuse count |
| G2 | Systemic | Preventive Health | 12.6 $MIND | Protected actors |
| G3 | Systemic | Debate Resolution | 7.5 $MIND | Participants |

---

## COMPLEXITY

**Per-event processing:** O(1) — each value event is evaluated independently.

**Batch processing:** O(E) per settlement epoch where E = number of value events.

**Multiplier computation:** O(N) where N = number of beneficiaries (requires graph traversal).

**Bottlenecks:**
- Counterfactual measurements (E2 Load Preemption, G2 Preventive Health) require baseline models — computationally expensive.
- Topological validation for C1 (Infrastructure) requires graph traversal — O(V + E) in the dependency graph.

---

## MARKERS

<!-- @mind:todo Implement counterfactual measurement for E2 and G2 — requires baseline trajectory model -->
<!-- @mind:todo Calibrate typical reward values against actual ecosystem data once live -->
<!-- @mind:todo Define the boundary between A2 (Empathy) and E1 (Anxiety Reduction) — when does relational become biometric? -->
<!-- @mind:todo Implement multiplier computation as a graph traversal service -->
<!-- @mind:escalation RESOLVED 2026-03-14: F6 ($MIND Holding) reward is intentionally minimal — demurrage removed, pure holding naturally unrewarding via trust-based pricing -->
<!-- @mind:proposition Consider adding a Category H: Ecological (cross-ecosystem value creation with other protocols) -->

---

Co-Authored-By: Force 2 — Economy <economy@mindprotocol.ai>
