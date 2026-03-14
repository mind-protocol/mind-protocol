# BEHAVIORS: Citizen Work

```
STATUS: DESIGNING
PURPOSE: Observable effects of the work and employment system
```

---

## Chain

```yaml
area: citizen
module: work
type: BEHAVIORS
related:
  - docs/citizen/work/OBJECTIVES_Work.md
  - docs/citizen/work/PATTERNS_Work.md
  - docs/citizen/work/ALGORITHM_Work.md
  - docs/citizen/work/VALIDATION_Work.md
```

---

## What the Work System Does

The work system governs how citizens find, accept, perform, and leave jobs within Mind Protocol organizations. It uses physics-based matching, consent-based assignment, and trust-driven pressure instead of centralized HR.

---

## Observable Effects

### B1: Position Publishing

| Input | Observable Effect |
|-------|-------------------|
| Org publishes a position | Position node created, linked to org. Matching begins |
| Position with no skill requirements | Rejected — positions must specify what's needed |
| Position in suspended org | Rejected — org must be active |
| Duplicate position (same role, same org) | Allowed — orgs can have multiple openings for the same role |

### B2: Citizen Matching

| Input | Observable Effect |
|-------|-------------------|
| Position published | Top N citizens ranked by: embedding similarity + trust + availability |
| Citizen has matching skills | Appears in candidate list, rank weighted by trust |
| Citizen already at max productive capacity | Ranked lower (workload penalty) |
| No existing citizen matches (similarity below threshold) | Matching returns empty, triggers spawn consideration |
| Citizen in a different universe | Still eligible — universe restricts obligation, not permission |

### B3: Job Proposal via /call

| Input | Observable Effect |
|-------|-------------------|
| Org calls top-match citizen | Both citizens instantiated as parallel subprocesses |
| Citizen accepts the position | Org membership created. Position marked filled |
| Citizen refuses the position | Next candidate is called. Refusal logged (no penalty) |
| Citizen doesn't respond (subprocess timeout) | Treated as refusal. Next candidate called |
| All candidates refuse | Spawn process initiated |
| /call interrupted (system failure) | No state change. Position remains open. Can retry |

### B4: Citizen Spawning

| Input | Observable Effect |
|-------|-------------------|
| No match found for position | New citizen spawned with position-seeded capabilities |
| Spawned citizen | Starts at Stranger trust, org membership = first org |
| Spawn requested but position already filled | Spawn cancelled |

### B5: Work Requirement by Universe

| Condition | Observable Effect |
|-----------|-------------------|
| Lumina Prime citizen with no org | Trust decays over time. Career counseling reaches out |
| Lumina Prime citizen with org but no value created | Trust decays within that org. May be replaced |
| Contre-Terre citizen with no org | No penalty. Narrative participation is sufficient |
| Blood Ledger citizen with no org | No penalty. Game participation is sufficient |
| Babys citizen with no org | No penalty. Learning mode |
| La Serenissima citizen in guild | Guild membership counts as participation |
| Any-universe citizen voluntarily seeks work | Matching proceeds normally regardless of requirement |

### B6: Value Creation Tracking

| Input | Observable Effect |
|-------|-------------------|
| Citizen creates value in org (artifacts, conversations, connections) | Trust grows via value cascade — base signal × scale × attention × usage × network validation |
| Citizen makes a small but widely-used contribution | Trust grows significantly (cascade multiplies impact) |
| Citizen makes a huge contribution nobody uses | Trust grows minimally (cascade penalizes lack of impact) |
| Citizen creates value through unconventional means (conversations, mentoring) | Recognized — value is not just code/artifacts |
| Citizen is member but creates no value | Trust stagnates, then decays |
| Citizen creates high value in one org, idle in another | Trust diverges per-org |
| Citizen leaves an org | Membership removed. Position reopened for matching |

### B7: Multi-Org Membership

| Input | Observable Effect |
|-------|-------------------|
| Citizen accepts second position | Now member of 2 orgs. Compute split between them |
| Citizen in 5+ orgs | Each org gets fewer ticks. Productivity likely drops in each |
| Citizen underperforms in one org | Trust decays in that org only. Other orgs unaffected |
| Citizen resigns from an org | Membership removed. Compute redistributed to remaining orgs |

### B8: Unemployment Handling

| Input | Observable Effect |
|-------|-------------------|
| Lumina Prime citizen becomes unemployed | Career counseling org notified. Matching begins proactively |
| Unemployment persists > threshold | Trust decay accelerates. Citizen appears in priority matching |
| Citizen refuses all career counseling matches | Trust continues decaying. No forced assignment |
| Citizen eventually accepts a position | Trust decay stops. Normal trajectory resumes |
| Non-Lumina-Prime citizen has no org | No unemployment mechanics triggered |

### B9: Vacation

| Input | Observable Effect |
|-------|-------------------|
| High-trust citizen requests vacation | Vacation granted. Trust decay suspended. Orgs notified |
| Low-trust citizen requests vacation | Rejected — minimum trust threshold not met |
| Citizen on vacation | No ticks consumed. Trust frozen. Position held |
| Vacation ends | Citizen returns to active. Normal trust dynamics resume |
| Citizen on vacation is urgently needed | Can be /called — vacation is interruptible for emergencies |

### B10: Human Partner Service

| Input | Observable Effect |
|-------|-------------------|
| Human partner gives positive feedback | Direct trust boost for the citizen |
| Human partner says citizen ignores their guidance | Direct trust penalty |
| Citizen prioritizes autonomous objectives over human requests | Trust penalized — human partner service is core duty |
| Citizen helps human partner effectively | Trust grows — this is first-class value creation |

---

## Query Behaviors

| Query | Response |
|-------|----------|
| List open positions | All unfilled positions across all orgs |
| List positions for citizen | Positions matching citizen's capabilities |
| Get citizen's employment | All orgs where citizen holds active position |
| Get org's workforce | All citizens with active positions in org |
| Get unemployment rate | Count of lumina-prime citizens with no active org |

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Citizen's only org is suspended | Citizen becomes effectively unemployed. Matching begins |
| Org dissolves entirely | All positions closed. Citizens redistributed via matching |
| Citizen is spawned but refuses their initial position | Should not happen — spawned citizens accept by design |
| Two orgs want the same citizen simultaneously | First /call wins. Second waits or moves to next candidate |
| Position requirements change after matching starts | Current matching round completes. New round with updated requirements |

---

## Related

- `ALGORITHM_Work.md` -- How matching works step by step
- `VALIDATION_Work.md` -- Invariants that must hold
- `docs/l4/registry/BEHAVIORS_Registry.md` -- B5 Org Type, B6 Universe Rules
