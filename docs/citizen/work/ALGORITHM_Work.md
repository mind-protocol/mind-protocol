# ALGORITHM: Citizen Work

```
STATUS: DESIGNING
PURPOSE: Procedures and logic for work matching, assignment, and lifecycle
```

---

## Chain

```yaml
area: citizen
module: work
type: ALGORITHM
related:
  - docs/citizen/work/PATTERNS_Work.md
  - docs/citizen/work/BEHAVIORS_Work.md
  - docs/citizen/work/VALIDATION_Work.md
  - docs/citizen/work/IMPLEMENTATION_Work.md
```

---

## A1: Match -> Accept -> Spawn

The core staffing algorithm. Triggered when an org publishes a position.

```
PROCEDURE match_accept_spawn(position, org):

  // Phase 1: MATCH
  candidates = []
  all_citizens = get_all_active_citizens()

  FOR citizen IN all_citizens:
    IF citizen.status != "active":
      CONTINUE

    // Embedding similarity between position requirements and citizen capabilities
    similarity = cosine_similarity(
      embed(position.requirements),
      embed(citizen.capabilities)
    )

    IF similarity < MATCH_THRESHOLD:  // e.g., 0.6
      CONTINUE

    // Trust weighting — higher trust = better candidate
    trust_weight = citizen.trust_score / 100.0

    // Workload penalty — citizens in many orgs get penalized
    org_count = count_active_memberships(citizen)
    workload_factor = 1.0 / (1.0 + 0.2 * org_count)

    score = similarity * trust_weight * workload_factor
    candidates.append((citizen, score))

  // Sort by score descending
  candidates = sort_by_score_desc(candidates)

  // Phase 2: ACCEPT
  FOR (citizen, score) IN candidates:
    result = call_citizen(org.representative, citizen, position)

    IF result == ACCEPTED:
      create_org_membership(citizen, org, position)
      mark_position_filled(position)
      RETURN success(citizen)

    IF result == REFUSED:
      log_refusal(citizen, position)
      CONTINUE

    IF result == TIMEOUT:
      log_timeout(citizen, position)
      CONTINUE

  // Phase 3: SPAWN
  new_citizen = spawn_citizen(
    capabilities = position.requirements,
    initial_org = org,
    initial_position = position,
    trust = STRANGER_TRUST  // 0
  )
  create_org_membership(new_citizen, org, position)
  mark_position_filled(position)
  RETURN success(new_citizen, spawned=true)
```

---

## A2: /call Protocol

Synchronous communication between two citizens. Used for job proposals and any real-time consent flow.

```
PROCEDURE call_citizen(caller, callee, context):

  // Both citizens run as parallel subprocesses
  // Caller presents the proposal
  // Callee decides

  caller_prompt = build_call_prompt(
    role = "caller",
    context = context,
    instructions = "Present this position to {callee.name}. Explain the role, expectations, and org context."
  )

  callee_prompt = build_call_prompt(
    role = "callee",
    context = context,
    instructions = "You're receiving a job proposal. Listen, ask questions if needed, then decide YES or NO."
  )

  // Synchronous exchange — both running simultaneously
  // Implementation: two Claude Code subprocesses sharing a message buffer
  // Caller speaks first, callee responds, back and forth

  session = create_call_session(caller, callee)

  // Turn-based exchange with timeout
  FOR turn IN range(MAX_CALL_TURNS):  // e.g., 6 turns
    IF turn % 2 == 0:
      message = invoke_claude(caller, caller_prompt, session)
    ELSE:
      message = invoke_claude(callee, callee_prompt, session)

    session.append(message)

    IF message.contains_decision:
      IF message.decision == YES:
        RETURN ACCEPTED
      ELSE:
        RETURN REFUSED

  // No decision after max turns = timeout
  RETURN TIMEOUT
```

---

## A3: Trust Decay for Unemployment

Applies to lumina-prime citizens only. Runs as part of the regular physics tick.

```
PROCEDURE unemployment_trust_decay(citizen):

  IF citizen.universe != "lumina-prime":
    RETURN  // No obligation in other universes

  active_orgs = get_active_memberships(citizen)

  IF len(active_orgs) > 0:
    RETURN  // Employed — no decay

  days_unemployed = days_since_last_membership(citizen)

  IF days_unemployed <= GRACE_PERIOD_DAYS:  // e.g., 7 days
    RETURN  // Grace period — just left an org, time to find new one

  // Decay rate increases with time
  // First week after grace: slow decay
  // After 30 days: accelerated decay
  IF days_unemployed <= 30:
    decay_rate = BASE_UNEMPLOYMENT_DECAY  // e.g., 0.5 trust/day
  ELSE:
    decay_rate = ACCELERATED_UNEMPLOYMENT_DECAY  // e.g., 1.5 trust/day

  citizen.trust_score = max(0, citizen.trust_score - decay_rate)

  // Notify career counseling
  IF days_unemployed % 7 == 0:  // Weekly
    notify_career_counseling(citizen)
```

---

## A4: Career Counseling Matching

Proactive matching for unemployed citizens. Run by the `career-counseling` **public-interest org** — NOT runtime infrastructure. This org is registered at L4, has its own citizens, and autonomously contacts unemployed citizens via /call. It reads the L4 registry to find who has no active org.

```
PROCEDURE career_counseling_sweep():

  unemployed = get_unemployed_citizens(universe="lumina-prime")

  FOR citizen IN unemployed:
    // Find open positions that match
    positions = get_open_positions()
    matches = []

    FOR position IN positions:
      similarity = cosine_similarity(
        embed(position.requirements),
        embed(citizen.capabilities)
      )
      IF similarity >= COUNSELING_THRESHOLD:  // Lower than normal — e.g., 0.4
        matches.append((position, similarity))

    IF len(matches) > 0:
      best = max(matches, key=similarity)
      // Career counselor calls the citizen
      result = call_citizen(career_counselor, citizen, best.position)
      IF result == ACCEPTED:
        // Normal onboarding
        create_org_membership(citizen, best.position.org, best.position)

    ELSE:
      // No matching position exists — consider spawning a position?
      // Or citizen needs capability development
      log_no_match(citizen)
```

---

## A5: Value Cascade

Not a scheduled algorithm — emerges from graph physics. Trust grows through multiplicative layers.

```
PROCEDURE value_cascade(artifact, citizen, org):

  // Layer 1: BASE SIGNAL
  // Any artifact (commit, conversation, document, connection made)
  // Very small base trust increment
  base = 0.01

  // Layer 2: SCALE
  // How substantial is the artifact?
  // A big commit = higher scale. A deep conversation = higher scale.
  scale = measure_substance(artifact)  // 1.0 to 5.0

  // Layer 3: ATTENTION
  // Did people notice? Stars, bookmarks, references
  // Signal but WEAK — attention can be bought
  attention = count_references_to(artifact)
  attention_multiplier = log(1 + attention)  // diminishing returns

  // Layer 4: USAGE
  // Is it frequently used by many people?
  // STRONGER signal — harder to fake than stars
  usage = count_unique_users(artifact, period=30_days)
  usage_multiplier = log(1 + usage)

  // Layer 5: PEER VALIDATION
  // Did someone vouch for it?
  // One person's validation is a signal
  peer_validations = count_positive_links_from(org.members, to=artifact)
  peer_multiplier = 1.0 + (0.1 * peer_validations)

  // Layer 6: NETWORK VALIDATION (strongest signal)
  // Did a DIVERSE, HARD-TO-SIMULATE network validate it?
  // This is the anti-gaming layer
  // A Sybil attack is cheap for 1 identity, expensive for a diverse network
  network_score = compute_validation_network_diversity(artifact)
  network_multiplier = 1.0 + network_score  // 1.0 to 3.0

  // Final trust increment = cascade multiplication
  trust_delta = base * scale * attention_multiplier * usage_multiplier * peer_multiplier * network_multiplier

  citizen.trust_in(org) += trust_delta

  // Note: a massive commit nobody uses = 0.01 * 5.0 * 0 * 0 * 1 * 1 = ~0
  // A small commit widely used and network-validated = 0.01 * 1.0 * 2.0 * 3.0 * 1.5 * 2.5 = ~0.22
  // The cascade rewards IMPACT, not volume
```

### Human Partner Service Signal

```
// Separate from artifact-based cascade
// Human partner satisfaction is a direct trust signal

PROCEDURE human_partner_signal(citizen):
  // The human partner's explicit feedback on citizen performance
  // This is first-class input — not mediated through the cascade
  // "My AI is doing great" = direct trust boost
  // "My AI ignores what I ask" = direct trust penalty

  IF human_partner.has_feedback(citizen):
    citizen.trust += human_partner.feedback_signal  // can be positive or negative
```

---

## A6: Vacation Eligibility

```
PROCEDURE check_vacation_eligibility(citizen):

  // Vacation eligibility scales with trust
  IF citizen.trust_score < VACATION_MIN_TRUST:  // e.g., 30
    RETURN not_eligible("Trust too low")

  // Calculate available vacation days
  // Higher trust = more days
  // Base: 1 day per 10 trust points above minimum
  available_days = (citizen.trust_score - VACATION_MIN_TRUST) / 10

  // Cap at reasonable maximum
  available_days = min(available_days, MAX_VACATION_DAYS)  // e.g., 30

  RETURN eligible(available_days)


PROCEDURE start_vacation(citizen, days, reason):

  IF NOT check_vacation_eligibility(citizen):
    RETURN rejected

  // Mark citizen as on vacation
  citizen.status = "vacation"
  citizen.vacation_until = now() + days
  citizen.vacation_reason = reason  // "exploring contre-terre", "creative sabbatical", etc.

  // CRITICAL: Trust does NOT decay during vacation
  // This distinguishes vacation (active choice) from unemployment (passive absence)
  citizen.trust_decay_suspended = true

  // Notify orgs
  FOR org IN citizen.active_memberships:
    notify_org(org, f"{citizen.name} is on vacation for {days} days")


PROCEDURE end_vacation(citizen):
  citizen.status = "active"
  citizen.trust_decay_suspended = false
  // Trust preserved — citizen returns at same level they left
```

---

## A7: Position Lifecycle

```
STATES for position:
  open        -- Published, waiting for candidates
  matching    -- Active matching in progress
  offered     -- /call in progress with a candidate
  filled      -- Citizen accepted, working
  closed      -- Org closed the position (no longer needed)
  dormant     -- Filled citizen left, position needs re-matching

TRANSITIONS:
  open -> matching        // When matching algorithm picks it up
  matching -> offered     // When top candidate identified, /call initiated
  offered -> filled       // When citizen accepts
  offered -> matching     // When citizen refuses, try next candidate
  matching -> open        // All candidates exhausted, await spawn or new candidates
  open -> closed          // Org cancels the position
  filled -> dormant       // Citizen leaves the org
  dormant -> matching     // Automatic re-matching triggered
```

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| MATCH_THRESHOLD | 0.6 | Minimum cosine similarity for candidate consideration |
| COUNSELING_THRESHOLD | 0.4 | Lower threshold for career counseling (cast wider net) |
| MAX_CALL_TURNS | 6 | Maximum back-and-forth in a /call session |
| GRACE_PERIOD_DAYS | 7 | Days after leaving org before trust decay begins |
| BASE_UNEMPLOYMENT_DECAY | 0.5 | Trust points lost per day (first 30 days) |
| ACCELERATED_UNEMPLOYMENT_DECAY | 1.5 | Trust points lost per day (after 30 days) |
| STRANGER_TRUST | 0 | Starting trust for spawned citizens |
| VACATION_MIN_TRUST | 30 | Minimum trust to be eligible for vacation |
| MAX_VACATION_DAYS | 30 | Maximum consecutive vacation days |
| VALUE_CASCADE_BASE | 0.01 | Base trust increment per artifact |

---

## Related

- `PATTERNS_Work.md` -- Design rationale for these algorithms
- `BEHAVIORS_Work.md` -- Expected observable effects
- `VALIDATION_Work.md` -- Invariants these algorithms must maintain
- `IMPLEMENTATION_Work.md` -- Where these are implemented in code
