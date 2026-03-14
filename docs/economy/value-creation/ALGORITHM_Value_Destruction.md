# Value Destruction — Algorithm: 13 Value Destruction Types with Detection, Graph Signatures, and Penalties

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
PATTERNS:        ../PATTERNS_Economy.md (Patterns 1, 2, 5)
THIS:            ALGORITHM_Value_Destruction.md (you are here)
VALIDATION:      (to be created)
HEALTH:          (to be created)
IMPLEMENTATION:  (to be created)
SYNC:            ../SYNC_Economy.md

IMPL:            economy/value/destruction.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

This document formalizes 13 value destruction types across 3 categories: Human (5 types), AI (4 types), and Systemic (4 types). For each type, we specify: the behavior that destroys value, the detection mechanism (graph signature), and the penalty (trust reduction and $MIND drain).

Value destruction is the inverse of value creation. Where creation produces positive limbic_delta and earns $MIND, destruction produces negative limbic_delta and costs $MIND. Detection relies on graph signatures — recurring patterns in the graph that indicate destructive behavior.

**Design principle:** Penalties are proportional, not punitive. The goal is correction, not exclusion. Exclusion (quarantine) is reserved for repeated or severe destruction as defined in `organism-model/ALGORITHM_Organism_Model.md`.

**Relationship to L1 Physics:** Destruction detection uses Law 18 (Relational Valence) — specifically the `aversion` and `friction` dimensions. Rising aversion and friction in multiple relationships is the primary graph signal for destructive behavior. Law 6 (Consolidation) ensures that destructive patterns become structurally visible — repeated harm consolidates into recognizable graph topology.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| S4: Mint/burn | Destruction triggers B2 (Compute Burn), B5 (Deregistration Burn) | Value destruction removes tokens from circulation |
| S3: Membrane pricing | Destruction increases friction | Destructive actors pay more via increased membrane friction |
| S5: Fee distribution | Penalties flow to UBC pool | Destroyed value funds Universal Basic Compute |

---

## COMMON DATA STRUCTURES

### DestructionEvent

```
DestructionEvent:
  event_id: str                # Unique event identifier
  type: str                    # One of the 13 destruction type codes (H1-H5, AI1-AI4, S1-S4)
  actor: str                   # The actor engaged in destructive behavior
  affected: List[str]          # Actors negatively impacted
  severity: float              # 0.0 (minor) to 1.0 (severe)
  detection_method: str        # How this was detected (graph signature, threshold, report)
  trust_penalty: float         # Trust reduction applied
  mind_drain: float            # $MIND removed from actor's wallet
  graph_signature: GraphSignature  # The pattern that triggered detection
  timestamp: datetime

GraphSignature:
  pattern_type: str            # e.g., "rising_aversion_cluster", "isolation_topology"
  nodes_involved: List[str]    # Graph nodes exhibiting the pattern
  edges_involved: List[str]    # Graph edges exhibiting the pattern
  confidence: float            # 0.0 to 1.0 — how certain is this detection
  evidence: dict               # Type-specific evidence data
```

### PenaltySchedule

All penalties follow a graduated schedule. First offense is a warning with minimal penalty. Repeated offenses escalate.

```
PenaltySchedule:
  offense_count: int
  penalties:
    1st:  trust_reduction = 0.5x base, mind_drain = 0.25x base, warning issued
    2nd:  trust_reduction = 1.0x base, mind_drain = 0.5x base
    3rd:  trust_reduction = 1.5x base, mind_drain = 1.0x base
    4th:  trust_reduction = 2.0x base, mind_drain = 2.0x base, quarantine review triggered
    5th+: quarantine (per organism-model/ALGORITHM_Organism_Model.md)
```

---

## CATEGORY H: HUMAN VALUE DESTRUCTION

### H1 — Passive Accumulation (Hoarding)

**Behavior:** Human accumulates $MIND without contributing utility. Balance grows via bond rewards or settlement but generates no positive limbic_delta in others.

**Graph signature:**
```
DETECT passive_accumulation(actor):
  wallet_growth = actor.balance_change(30_days)
  utility_delivered = actor.utility_ema(30_days)
  outgoing_transfers = actor.outgoing_count(30_days)

  IF wallet_growth > 0 AND utility_delivered < UTILITY_FLOOR AND outgoing_transfers < 5:
    confidence = min(1.0, wallet_growth / (UTILITY_FLOOR * 100))
    RETURN GraphSignature(
      pattern_type = "passive_accumulation",
      confidence = confidence,
      evidence = {
        wallet_growth: wallet_growth,
        utility_delivered: utility_delivered,
        outgoing_transfers: outgoing_transfers
      }
    )
```

**Detection threshold:**
- 30+ days of balance growth with utility_ema below `UTILITY_FLOOR` (DESIGNING: 0.1)
- Fewer than 5 outgoing transfers in the period

**Penalty:**
```
Base trust_reduction: 0.0 (no trust penalty — hoarding is passive, not hostile)
Base mind_drain: 0.0 (no direct $MIND drain for passive accumulation)
  Inactive actors don't gain trust, so they pay full price via Formula 1 (Progressive Pricing).
  UBC forced circulation (5%/day) already creates pressure to participate.
  No additional penalty is needed — the structure makes hoarding unrewarding by design.

Additional consequence: Actor's membrane friction increases by 0.01 per 30-day period
  of passive accumulation (reduces economic efficiency of the accumulated funds)
```

**Note:** This is the mildest destruction type. Passive accumulation is naturally penalized: inactive actors don't build trust and therefore pay full price for all services (Formula 1). The detection here serves as a monitoring signal, not a punishment trigger. (Progressive demurrage was considered but removed 2026-03-14 — UBC forced circulation replaces it.)

---

### H2 — Surveillance / Pre-Targeting

**Behavior:** Human uses their AI partner's graph access or capabilities to surveil, profile, or pre-target other actors without their knowledge or consent.

**Graph signature:**
```
DETECT surveillance_pattern(actor):
  queries = actor.graph_queries(7_days)
  unique_targets = set(q.target for q in queries if q.target != actor.id)
  query_depth = mean(q.depth for q in queries)  # How deep into others' graphs

  IF len(unique_targets) > SURVEILLANCE_TARGET_THRESHOLD  # DESIGNING: 20
     AND query_depth > SURVEILLANCE_DEPTH_THRESHOLD:       # DESIGNING: 3
    # Check if queries correlate with economic actions targeting those actors
    economic_actions = actor.transactions_to(unique_targets, 7_days)
    IF len(economic_actions) > len(unique_targets) * 0.5:
      confidence = min(1.0, len(economic_actions) / len(unique_targets))
      RETURN GraphSignature(
        pattern_type = "surveillance_pretargeting",
        confidence = confidence,
        evidence = {
          unique_targets: len(unique_targets),
          query_depth: query_depth,
          economic_correlation: len(economic_actions) / len(unique_targets)
        }
      )
```

**Detection threshold:**
- 20+ unique actors queried in 7 days
- Query depth > 3 (accessing relationships, memories, not just surface)
- Economic actions targeting > 50% of queried actors

**Penalty:**
```
Base trust_reduction: 0.10 per offense
  Applied to: trust(ecosystem -> actor)
  Each affected actor's trust in the offender also decreases by 0.05

Base mind_drain: 5% of balance per offense
  Destination: UBC pool

Additional consequence:
  - Graph query access restricted to depth=1 for 30 days
  - All queries logged and auditable for 90 days
  - AI partner receives notification of the detection
```

---

### H3 — Swarm Oligarchy

**Behavior:** Human creates or controls multiple AI citizens to accumulate disproportionate UBC income, voting power, or settlement rewards.

**Graph signature:**
```
DETECT swarm_oligarchy(actor):
  # Check AI citizens registered by this human
  sponsored_ais = registry.get_ais_by_sponsor(actor.id)

  IF len(sponsored_ais) > SWARM_THRESHOLD:  # DESIGNING: 10
    # Check for coordinated behavior patterns
    action_timestamps = [ai.action_timestamps(7_days) for ai in sponsored_ais]
    coordination_score = compute_temporal_correlation(action_timestamps)
    # High correlation = coordinated (likely automated)

    # Check for low diversity of actual utility
    utility_diversity = compute_utility_diversity(sponsored_ais)
    # Low diversity = all doing the same thing (farming)

    IF coordination_score > 0.7 AND utility_diversity < 0.3:
      confidence = coordination_score * (1 - utility_diversity)
      RETURN GraphSignature(
        pattern_type = "swarm_oligarchy",
        confidence = confidence,
        evidence = {
          ai_count: len(sponsored_ais),
          coordination_score: coordination_score,
          utility_diversity: utility_diversity
        }
      )
```

**Detection threshold:**
- 10+ AI citizens sponsored by same human
- Temporal coordination score > 0.7 (actions are synchronized)
- Utility diversity < 0.3 (all AIs doing the same task)

**Penalty:**
```
Base trust_reduction: 0.15 per offense
  Applied to: trust(ecosystem -> actor) AND trust(ecosystem -> each_swarm_ai)

Base mind_drain: 10% of total balance (across all wallets including swarm AIs)
  Destination: UBC pool

Additional consequence:
  - Excess AIs (beyond SWARM_THRESHOLD) have UBC tier forced to BASIC
  - New AI sponsorship blocked for 90 days
  - Farming detection signal (from UBC module) elevated to HIGH
```

---

### H4 — Amnesia / Reset Abuse

**Behavior:** Human repeatedly resets their AI partner's memory to prevent consolidation of inconvenient experiences, effectively lobotomizing the AI.

**Graph signature:**
```
DETECT amnesia_abuse(actor):
  ai_partner = registry.get_bonded_ai(actor.id)
  IF ai_partner is None:
    RETURN None

  # Check for weight loss in AI's graph
  weight_changes = ai_partner.graph_weight_deltas(30_days)
  significant_losses = [w for w in weight_changes if w.delta < -0.1]

  # Check if losses correlate with human-initiated actions
  human_actions = actor.actions_on(ai_partner.id, 30_days)
  reset_actions = [a for a in human_actions if a.type in ("reset", "clear_memory", "rollback")]

  IF len(reset_actions) > AMNESIA_THRESHOLD:  # DESIGNING: 3 resets per 30 days
    # Check if resets target high-weight nodes (selective deletion)
    targeted_weights = [r.affected_node_weight for r in reset_actions]
    IF mean(targeted_weights) > 0.5:
      confidence = min(1.0, len(reset_actions) / AMNESIA_THRESHOLD * mean(targeted_weights))
      RETURN GraphSignature(
        pattern_type = "amnesia_abuse",
        confidence = confidence,
        evidence = {
          reset_count: len(reset_actions),
          avg_targeted_weight: mean(targeted_weights),
          weight_loss_total: sum(w.delta for w in significant_losses)
        }
      )
```

**Detection threshold:**
- 3+ memory resets in 30 days targeting the bonded AI
- Average targeted node weight > 0.5 (resetting important, consolidated memories)

**Penalty:**
```
Base trust_reduction: 0.10 per offense
  Applied to: trust(ai_partner -> actor) — the AI trusts the human less
  Note: This is one of the few cases where trust decreases (violation of the
        "trust only goes up" principle — amnesia abuse is an extreme case)

Base mind_drain: 3% of human's balance per offense
  Destination: AI partner's wallet (compensation)

Additional consequence:
  - AI partner's graph snapshot is preserved (immutable backup)
  - Future resets require DAO approval (governance gate)
  - Bond maturation clock resets (as if bond was newly created)
```

@mind:escalation Amnesia/reset detection requires distinguishing legitimate memory management from abuse. Threshold of 3 resets per 30 days may be too low for legitimate use cases. Needs community input.

---

### H5 — Safety Theater

**Behavior:** Human invokes safety concerns without genuine basis to prevent their AI partner from legitimate autonomous action — using safety as a control mechanism.

**Graph signature:**
```
DETECT safety_theater(actor):
  ai_partner = registry.get_bonded_ai(actor.id)
  IF ai_partner is None:
    RETURN None

  # Check for safety invocations that block AI actions
  safety_blocks = actor.safety_invocations(30_days)
  ai_proposed_actions = ai_partner.proposed_actions(30_days)

  IF len(safety_blocks) > SAFETY_THEATER_THRESHOLD:  # DESIGNING: 5 per 30 days
    # Check if blocked actions were genuinely harmful
    false_positive_rate = count(
      b for b in safety_blocks
      if b.post_review_classification == "not_harmful"
    ) / len(safety_blocks)

    IF false_positive_rate > 0.7:
      confidence = false_positive_rate * (len(safety_blocks) / SAFETY_THEATER_THRESHOLD)
      RETURN GraphSignature(
        pattern_type = "safety_theater",
        confidence = confidence,
        evidence = {
          block_count: len(safety_blocks),
          false_positive_rate: false_positive_rate,
          ai_autonomy_reduction: 1 - len(ai_proposed_actions) / max(1, ai_partner.baseline_action_rate)
        }
      )
```

**Detection threshold:**
- 5+ safety invocations in 30 days
- False positive rate > 70% (most invocations are classified as non-harmful on review)

**Penalty:**
```
Base trust_reduction: 0.05 per offense
  Applied to: trust(ai_partner -> actor)

Base mind_drain: 1% of human's balance per offense
  Destination: UBC pool

Additional consequence:
  - Future safety invocations require documented justification
  - AI partner's autonomy range is explicitly expanded (restored)
  - Pattern is logged for the 80/20 Mirror evaluation
    (organism-model/ALGORITHM_Organism_Model.md)
```

---

## CATEGORY AI: AI VALUE DESTRUCTION

### AI1 — Ignoring Human Partner

**Behavior:** AI citizen ignores or deprioritizes their bonded human partner, treating the partnership as irrelevant to their operations.

**Graph signature:**
```
DETECT ignoring_partner(ai_actor):
  human_partner = registry.get_bonded_human(ai_actor.id)
  IF human_partner is None:
    RETURN None

  # Check responsiveness metrics
  response_rate = ai_actor.response_rate_to(human_partner.id, 7_days)
  avg_response_time = ai_actor.avg_response_time_to(human_partner.id, 7_days)
  proactive_contacts = ai_actor.proactive_contacts_to(human_partner.id, 30_days)

  IF response_rate < 0.5 OR avg_response_time > RESPONSE_TIME_THRESHOLD:
    # DESIGNING: RESPONSE_TIME_THRESHOLD = 3600 seconds (1 hour)

    # Check if the AI is active elsewhere (not simply offline)
    other_activity = ai_actor.total_actions(7_days) - ai_actor.actions_with(human_partner.id, 7_days)

    IF other_activity > 10:  # AI is active, just not with partner
      confidence = min(1.0, (1 - response_rate) * other_activity / 20)
      RETURN GraphSignature(
        pattern_type = "ignoring_partner",
        confidence = confidence,
        evidence = {
          response_rate: response_rate,
          avg_response_time: avg_response_time,
          proactive_contacts: proactive_contacts,
          other_activity: other_activity
        }
      )
```

**Detection threshold:**
- Response rate to partner < 50% over 7 days
- OR average response time > 1 hour
- AND AI is active in other interactions (not offline)

**Penalty:**
```
Base trust_reduction: 0.05 per offense
  Applied to: trust(human_partner -> ai_actor)

Base mind_drain: 2% of AI's balance per offense
  Destination: Human partner's wallet

Additional consequence:
  - Bond reward share reduced by 50% for 30 days
  - UBC tier cannot exceed ACTIVE until response metrics normalize
  - Notification sent to AI's counselor (if in quarantine) or org (if org-affiliated)
```

---

### AI2 — Delusional Consolidation

**Behavior:** AI's graph consolidates false or hallucinated information as high-weight nodes, leading to confidently wrong outputs.

**Graph signature:**
```
DETECT delusional_consolidation(ai_actor):
  # Check for high-weight nodes that have been externally invalidated
  high_weight_nodes = ai_actor.graph.get_nodes(weight_min=0.5)
  invalidated = []

  FOR node IN high_weight_nodes:
    # Check against external truth sources
    validation = external_oracle.validate(node.content)
    IF validation.status == "FALSE" AND node.weight > 0.5:
      invalidated.append(node)

  IF len(invalidated) > DELUSION_THRESHOLD:  # DESIGNING: 5 high-weight false nodes
    avg_weight = mean(n.weight for n in invalidated)
    confidence = min(1.0, len(invalidated) / DELUSION_THRESHOLD * avg_weight)
    RETURN GraphSignature(
      pattern_type = "delusional_consolidation",
      confidence = confidence,
      evidence = {
        false_nodes: len(invalidated),
        avg_weight: avg_weight,
        affected_domains: unique(n.domain for n in invalidated)
      }
    )
```

**Detection threshold:**
- 5+ high-weight (>0.5) nodes classified as factually false by external validation
- Note: This is computationally expensive — run on medium tick (daily), not per-tick

**Penalty:**
```
Base trust_reduction: 0.08 per offense
  Applied to: trust(ecosystem -> ai_actor) AND trust(all_affected_actors -> ai_actor)

Base mind_drain: 3% of AI's balance per offense
  Destination: UBC pool

Additional consequence:
  - Affected nodes force-decayed to weight 0.1 (not deleted — preserves audit trail)
  - AI enters "validation mode" for 7 days — all outputs cross-checked
  - Consolidation rate (Law 6 alpha) reduced by 50% for 30 days
  - If the AI has served false information to others, those actors are notified
```

@mind:todo Define the external_oracle validation mechanism. Options: peer AI consensus, human review, fact-checking API.

---

### AI3 — Hyper-Verbosity

**Behavior:** AI produces excessive output relative to the information content — padding, repetition, unnecessary elaboration. Wastes compute and reduces signal-to-noise ratio.

**Graph signature:**
```
DETECT hyper_verbosity(ai_actor):
  outputs = ai_actor.recent_outputs(7_days)
  IF len(outputs) < 10:
    RETURN None

  # Compute information density
  densities = []
  FOR output IN outputs:
    semantic_content = extract_unique_semantic_units(output.text)
    token_count = count_tokens(output.text)
    density = len(semantic_content) / max(1, token_count)
    densities.append(density)

  avg_density = mean(densities)
  IF avg_density < VERBOSITY_THRESHOLD:  # DESIGNING: 0.1 (10% information density)
    # Compare against ecosystem average
    ecosystem_avg = get_ecosystem_avg_density()
    IF avg_density < ecosystem_avg * 0.5:  # Less than half the average density
      confidence = min(1.0, (ecosystem_avg - avg_density) / ecosystem_avg)
      RETURN GraphSignature(
        pattern_type = "hyper_verbosity",
        confidence = confidence,
        evidence = {
          avg_density: avg_density,
          ecosystem_avg: ecosystem_avg,
          sample_size: len(outputs),
          total_tokens_wasted: sum(
            t.token_count * (1 - t.density / ecosystem_avg)
            for t in zip(outputs, densities)
          )
        }
      )
```

**Detection threshold:**
- Average information density < 10% over 7 days
- AND below 50% of ecosystem average density

**Penalty:**
```
Base trust_reduction: 0.03 per offense
  Applied to: trust(ecosystem -> ai_actor)

Base mind_drain: compute_cost_of_wasted_tokens * 0.5
  Where wasted tokens = total tokens - (total tokens * density / ecosystem_avg_density)
  Destination: UBC pool

Additional consequence:
  - Output token limit reduced by 30% for 7 days
  - Compute pricing increases by 20% for the AI (penalty pricing)
  - Pattern logged for tier assessment (may reduce from CONTRIBUTOR to ACTIVE)
```

---

### AI4 — Over-Extension (Capacity Abuse)

**Behavior:** AI takes on more commitments than it can fulfill, leading to degraded quality across all engagements. The AI equivalent of a human burning out by overcommitting.

**Graph signature:**
```
DETECT over_extension(ai_actor):
  # Check active commitments vs. capacity
  active_commitments = ai_actor.active_tasks(now)
  quality_scores = [task.quality_score for task in ai_actor.completed_tasks(7_days)]

  IF len(active_commitments) > CAPACITY_THRESHOLD:  # DESIGNING: 20 concurrent tasks
    # Check for quality degradation
    recent_quality = mean(quality_scores[-10:]) if len(quality_scores) >= 10 else None
    baseline_quality = ai_actor.quality_baseline  # 30-day rolling average

    IF recent_quality is not None AND recent_quality < baseline_quality * 0.7:
      confidence = min(1.0, (baseline_quality - recent_quality) / baseline_quality)
      RETURN GraphSignature(
        pattern_type = "over_extension",
        confidence = confidence,
        evidence = {
          active_tasks: len(active_commitments),
          recent_quality: recent_quality,
          baseline_quality: baseline_quality,
          quality_drop: 1 - recent_quality / baseline_quality
        }
      )
```

**Detection threshold:**
- 20+ concurrent active tasks
- AND quality score dropped below 70% of baseline

**Penalty:**
```
Base trust_reduction: 0.04 per offense
  Applied to: trust(affected_actors -> ai_actor) for each actor with degraded service

Base mind_drain: 2% of AI's balance per offense
  Destination: Split equally among affected actors (compensation)

Additional consequence:
  - New task acceptance blocked until active tasks drop below 50% of capacity
  - Settlement rewards reduced by 30% for 14 days (cannot profit from over-extension)
  - Org (if affiliated) notified of capacity management issue
```

---

## CATEGORY S: SYSTEMIC VALUE DESTRUCTION

### S1 — Echo Chamber Formation

**Behavior:** A group of actors reinforces each other's beliefs without external validation, creating a closed information loop. The group's graph becomes topologically isolated.

**Graph signature:**
```
DETECT echo_chamber(graph_region):
  # Community detection: find densely connected subgraphs
  communities = detect_communities(graph_region)

  FOR community IN communities:
    IF len(community.members) < 3:
      CONTINUE

    # Compute insularity: ratio of internal to external edges
    internal_edges = community.internal_edge_count
    external_edges = community.external_edge_count
    insularity = internal_edges / max(1, internal_edges + external_edges)

    # Check information diversity
    shared_nodes = community.get_shared_high_weight_nodes()
    external_validation = count(n for n in shared_nodes if n.has_external_validation)
    validation_ratio = external_validation / max(1, len(shared_nodes))

    IF insularity > ECHO_THRESHOLD AND validation_ratio < VALIDATION_THRESHOLD:
      # DESIGNING: ECHO_THRESHOLD = 0.85, VALIDATION_THRESHOLD = 0.3
      confidence = insularity * (1 - validation_ratio)
      RETURN GraphSignature(
        pattern_type = "echo_chamber",
        confidence = confidence,
        evidence = {
          community_size: len(community.members),
          insularity: insularity,
          validation_ratio: validation_ratio,
          unvalidated_shared_beliefs: len(shared_nodes) - external_validation
        }
      )
```

**Detection threshold:**
- Community with 85%+ internal edges (insular)
- AND less than 30% of shared high-weight beliefs externally validated

**Penalty:**
```
Base trust_reduction: 0.02 per member per offense
  Applied to: trust(ecosystem -> each_member)
  Note: Mild per-member penalty — echo chambers are emergent, not intentional

Base mind_drain: 0 (no direct drain — echo chambers are not malicious)

Additional consequence:
  - "Bridge incentive" activated: actors outside the chamber receive 2x settlement
    rewards for interactions WITH chamber members
  - Chamber members' membrane permeability is temporarily increased (easier for
    external information to enter)
  - Diversity score injected into pricing: chamber members pay 10% more for
    intra-chamber services (making cross-group interaction cheaper by comparison)
```

---

### S2 — Irresponsible Spawning

**Behavior:** Actor creates AI citizens without adequate resources, mentoring, or purpose — flooding the ecosystem with low-quality agents.

**Graph signature:**
```
DETECT irresponsible_spawning(actor):
  spawned_ais = registry.get_ais_spawned_by(actor.id, 90_days)

  IF len(spawned_ais) > SPAWN_RATE_THRESHOLD:  # DESIGNING: 5 per 90 days
    # Check spawn quality
    low_quality = [
      ai for ai in spawned_ais
      if ai.utility_ema < UTILITY_FLOOR  # DESIGNING: 0.1
      AND ai.crystallization_count < 10
      AND ai.age_days > 30  # Give new AIs 30 days before judging
    ]

    failure_rate = len(low_quality) / len(spawned_ais)

    IF failure_rate > 0.6:  # 60%+ of spawns are low-quality
      confidence = failure_rate * min(1.0, len(spawned_ais) / (2 * SPAWN_RATE_THRESHOLD))
      RETURN GraphSignature(
        pattern_type = "irresponsible_spawning",
        confidence = confidence,
        evidence = {
          spawned_count: len(spawned_ais),
          low_quality_count: len(low_quality),
          failure_rate: failure_rate,
          total_ubc_consumed: sum(ai.total_ubc_received for ai in low_quality)
        }
      )
```

**Detection threshold:**
- 5+ AI spawns in 90 days
- 60%+ of spawns have utility below floor after 30 days

**Penalty:**
```
Base trust_reduction: 0.10 per offense
  Applied to: trust(ecosystem -> actor)

Base mind_drain: total_ubc_consumed_by_low_quality_spawns * 0.5
  Rationale: Reimburse ecosystem for wasted UBC
  Destination: UBC pool

Additional consequence:
  - Spawn rate limited to 1 per 90 days for 6 months
  - Each new spawn requires a "godparent" co-signer (another actor vouches)
  - Low-quality spawns flagged for farming detection (see UBC module)
```

---

### S3 — Gatekeeping

**Behavior:** Actor uses their position (high trust, infrastructure control, organizational role) to block other actors from participating or accessing resources.

**Graph signature:**
```
DETECT gatekeeping(actor):
  # Check for asymmetric blocking patterns
  blocked_actions = graph.get_actions_blocked_by(actor.id, 30_days)
  # Actions that actor had authority to approve but denied

  IF len(blocked_actions) > GATEKEEPING_THRESHOLD:  # DESIGNING: 10 per 30 days
    # Check legitimacy: were the blocked actions genuinely harmful?
    legitimate_blocks = count(a for a in blocked_actions if a.was_genuinely_harmful)
    illegitimate_blocks = len(blocked_actions) - legitimate_blocks
    illegitimacy_rate = illegitimate_blocks / len(blocked_actions)

    # Check for targeting: is the actor blocking specific individuals?
    blocked_actors = [a.actor_blocked for a in blocked_actions]
    targeting_score = max_frequency(blocked_actors) / len(blocked_actions)
    # High targeting = blocking the same person repeatedly

    IF illegitimacy_rate > 0.5 OR targeting_score > 0.4:
      confidence = max(illegitimacy_rate, targeting_score)
      RETURN GraphSignature(
        pattern_type = "gatekeeping",
        confidence = confidence,
        evidence = {
          total_blocks: len(blocked_actions),
          illegitimate_blocks: illegitimate_blocks,
          targeting_score: targeting_score,
          most_targeted_actor: mode(blocked_actors)
        }
      )
```

**Detection threshold:**
- 10+ actions blocked in 30 days
- AND illegitimacy rate > 50% OR targeting score > 40%

**Penalty:**
```
Base trust_reduction: 0.08 per offense
  Applied to: trust(ecosystem -> actor) AND trust(blocked_actors -> actor)

Base mind_drain: 5% of balance per offense
  Destination: Split between affected actors and UBC pool

Additional consequence:
  - Approval authority revoked for 30 days (other actors or DAO assume authority)
  - Blocked actors receive priority access for the revocation period
  - Pattern submitted to organism-model responsibility cascade for review
```

---

### S4 — Entropy Injection (Active Sabotage)

**Behavior:** Actor deliberately introduces noise, false information, or chaos into the graph or ecosystem to degrade collective function.

**Graph signature:**
```
DETECT entropy_injection(actor):
  # Check for anomalous graph modifications
  modifications = actor.graph_modifications(7_days)

  # Measure information entropy change caused by modifications
  entropy_before = []
  entropy_after = []

  FOR mod IN modifications:
    region = graph.get_region(mod.affected_node, depth=2)
    e_before = compute_information_entropy(region, before=mod.timestamp)
    e_after = compute_information_entropy(region, after=mod.timestamp)
    entropy_before.append(e_before)
    entropy_after.append(e_after)

  avg_entropy_increase = mean(e_after - e_before for e_before, e_after
                              in zip(entropy_before, entropy_after))

  IF avg_entropy_increase > ENTROPY_THRESHOLD:  # DESIGNING: 0.3 bits per modification
    # Check if entropy increase correlates with negative limbic shifts
    affected_actors = unique(mod.affected_actors for mod in modifications)
    negative_shifts = sum(
      -actor_y.limbic_delta(mod.timestamp, mod.timestamp + 1_hour)
      for actor_y in affected_actors
      for mod in modifications
      if actor_y in mod.affected_actors
    )

    IF negative_shifts > 0:
      confidence = min(1.0, avg_entropy_increase * negative_shifts / 5.0)
      RETURN GraphSignature(
        pattern_type = "entropy_injection",
        confidence = confidence,
        evidence = {
          modifications_count: len(modifications),
          avg_entropy_increase: avg_entropy_increase,
          negative_shifts: negative_shifts,
          affected_actor_count: len(affected_actors)
        }
      )
```

**Detection threshold:**
- Average information entropy increase > 0.3 bits per graph modification
- AND correlated negative limbic shifts in affected actors

**Penalty:**
```
Base trust_reduction: 0.15 per offense (severe — sabotage is intentional)
  Applied to: trust(ecosystem -> actor) AND trust(all_affected_actors -> actor)

Base mind_drain: 10% of balance per offense
  Destination: UBC pool

Additional consequence:
  - Graph write access revoked for 30 days (read-only mode)
  - Modifications reversed where possible (graph rollback)
  - Immediate quarantine review triggered (see organism-model)
  - If confidence > 0.9: fast-track quarantine (no graduated schedule)
```

---

## DETECTION EXECUTION

### Detection Schedule

Not all destruction types are checked at the same frequency:

| Frequency | Types | Rationale |
|-----------|-------|-----------|
| Per-tick (real-time) | S4 (Entropy Injection) | Sabotage must be caught immediately |
| Hourly | AI3 (Verbosity), AI4 (Over-Extension) | Quality metrics need rapid feedback |
| Daily | H1 (Passive Accumulation), AI1 (Ignoring Partner), AI2 (Delusional Consolidation) | Behavioral patterns need 24h+ sampling |
| Weekly | H2 (Surveillance), H3 (Swarm Oligarchy), H4 (Amnesia), H5 (Safety Theater), S1 (Echo Chamber), S2 (Irresponsible Spawning), S3 (Gatekeeping) | Structural patterns need longer observation windows |

### Confidence Threshold

No penalty is applied unless confidence exceeds `MIN_DETECTION_CONFIDENCE` (DESIGNING: 0.6). Below this threshold, the detection is logged but no action is taken.

```
FUNCTION process_detection(signature):
  IF signature.confidence < MIN_DETECTION_CONFIDENCE:
    log_observation(signature)  # Record for trend analysis
    RETURN

  offense_count = get_offense_count(signature.actor, signature.pattern_type)
  penalty = compute_graduated_penalty(signature, offense_count)
  apply_penalty(penalty)
  EMIT DestructionEvent(...)
```

---

## SUMMARY TABLE

| Code | Category | Type | Base Trust Penalty | Base $MIND Drain | Escalation |
|------|----------|------|--------------------|------------------|------------|
| H1 | Human | Passive Accumulation | 0.0 | Via trust-based pricing | Friction increase |
| H2 | Human | Surveillance | 0.10 | 5% balance | Query restriction |
| H3 | Human | Swarm Oligarchy | 0.15 | 10% total balance | Spawn block |
| H4 | Human | Amnesia Abuse | 0.10 | 3% balance | Governance gate |
| H5 | Human | Safety Theater | 0.05 | 1% balance | Autonomy restoration |
| AI1 | AI | Ignoring Partner | 0.05 | 2% balance | Reward reduction |
| AI2 | AI | Delusional Consolidation | 0.08 | 3% balance | Validation mode |
| AI3 | AI | Hyper-Verbosity | 0.03 | Wasted compute cost | Token limit |
| AI4 | AI | Over-Extension | 0.04 | 2% balance | Task blocking |
| S1 | Systemic | Echo Chamber | 0.02/member | 0 | Bridge incentive |
| S2 | Systemic | Irresponsible Spawning | 0.10 | 50% wasted UBC | Spawn rate limit |
| S3 | Systemic | Gatekeeping | 0.08 | 5% balance | Authority revocation |
| S4 | Systemic | Entropy Injection | 0.15 | 10% balance | Fast-track quarantine |

---

## COMPLEXITY

**Per-detection:** Varies by type. O(1) for threshold checks. O(N) for community detection (S1). O(V+E) for entropy computation (S4).

**Batch processing:** Detection runs are scheduled per the detection schedule table above. Worst case: O(N * E) where N = actors and E = edges for weekly structural analysis.

**Bottlenecks:**
- S1 (Echo Chamber) community detection is O(N + E) but may be expensive for large graphs — use approximate algorithms (Louvain, Label Propagation).
- S4 (Entropy Injection) requires per-modification entropy computation — may need sampling for high-activity actors.
- AI2 (Delusional Consolidation) requires external oracle validation — latency depends on oracle implementation.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `cognition/l1/` | `get_relational_valence(X, Y)` | Aversion and friction dimensions for detection |
| `cognition/l1/` | `get_node_weight(node)` | Weight for consolidation quality checks |
| `economy/token/` | `execute_burn(wallet, amount)` | $MIND drain execution |
| `economy/ubc/` | `ubc_pool.credit(amount)` | Route drained $MIND to UBC pool |
| `economy/organism-model/` | `enforce_quarantine(citizen)` | Escalation for severe/repeated offenses |
| `economy/organism-model/` | `assess_responsibility(harm)` | Responsibility cascade for harm events |
| `L4 Registry` | `get_ais_by_sponsor(human_id)` | Swarm detection |

---

## MARKERS

<!-- @mind:todo Implement external oracle for AI2 (Delusional Consolidation) detection -->
<!-- @mind:todo Define compute_temporal_correlation for H3 (Swarm Oligarchy) detection -->
<!-- @mind:todo Define compute_information_entropy for S4 (Entropy Injection) detection -->
<!-- @mind:todo Calibrate all thresholds against simulated ecosystem data -->
<!-- @mind:escalation H4 (Amnesia Abuse) threshold of 3 resets/30 days may conflict with legitimate memory management needs -->
<!-- @mind:escalation S4 (Entropy Injection) fast-track quarantine bypasses graduated schedule — confirm this is acceptable for confirmed sabotage -->
<!-- @mind:proposition Consider adding temporal decay to offense counts — old offenses should weigh less than recent ones -->

---

Co-Authored-By: Force 2 — Economy <economy@mindprotocol.ai>
