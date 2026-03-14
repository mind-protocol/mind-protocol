# VALIDATION: Citizen Work

```
STATUS: DESIGNING
PURPOSE: Invariants that the work system must enforce
```

---

## Chain

```yaml
area: citizen
module: work
type: VALIDATION
related:
  - docs/citizen/work/ALGORITHM_Work.md
  - docs/citizen/work/BEHAVIORS_Work.md
  - docs/citizen/work/HEALTH_Work.md
```

---

## Invariants

### V1: Consent is inviolable

```
FOR ALL citizen, org, position:
  citizen.is_member(org, position) IMPLIES citizen.has_accepted(position)
```

No citizen is ever assigned to a position they did not explicitly accept. This includes spawned citizens — they are created WITH the acceptance built in (their purpose IS the position).

**Violation response:** Immediate removal from position. Investigation into how assignment bypassed consent.

### V2: Universe determines requirement, not permission

```
FOR ALL citizen:
  citizen.universe == "lumina-prime" IMPLIES citizen.should_have_org OR citizen.trust_is_decaying
  citizen.universe != "lumina-prime" IMPLIES citizen.may_work OR citizen.may_not_work (no penalty)
```

Lumina Prime citizens are expected to work (or accept trust decay). Other universe citizens may work if they choose. No universe blocks work.

**Violation response:** If a non-lumina-prime citizen experiences trust decay from unemployment, the decay algorithm has a universe check bug.

### V3: Positions belong to active orgs

```
FOR ALL position:
  position.status == "open" IMPLIES position.org.status == "active"
```

Suspended or inactive orgs cannot have open positions.

**Violation response:** Close all positions for the org. Notify matched candidates.

### V4: One acceptance per position (single-fill)

```
FOR ALL position WHERE position.type == "single":
  count(acceptances(position)) <= 1
```

A single-fill position can be accepted by exactly one citizen. Multiple-fill positions (e.g., "5 builders needed") track their own fill count.

**Violation response:** First acceptance wins. Later acceptances are invalid — citizen notified, membership not created.

### V5: Trust decay requires grace period

```
FOR ALL citizen WHERE citizen.universe == "lumina-prime":
  citizen.days_unemployed <= GRACE_PERIOD IMPLIES citizen.trust_decay == 0
```

Citizens who just left an org get a grace period before trust decay begins. No immediate punishment for transitioning between positions.

**Violation response:** If trust decayed within grace period, restore the lost trust.

### V6: Matching uses current state

```
FOR ALL matching_round:
  matching_round.citizen_data == current_graph_state (not cached)
```

Matching must use live citizen capabilities and trust, not stale snapshots. A citizen who gained skills since last matching should benefit.

**Violation response:** Invalidate cached match results. Re-run with current state.

### V7: Spawn only when match exhausted

```
FOR ALL spawn_event:
  spawn_event IMPLIES match_round_completed AND candidates_exhausted
```

No spawning unless matching has been attempted and all candidates have refused (or none qualified).

**Violation response:** Cancel spawn. Run matching first.

### V8: Multi-org trust is independent

```
FOR ALL citizen, org_a, org_b WHERE org_a != org_b:
  trust(citizen, org_a) IS INDEPENDENT OF trust(citizen, org_b)
```

A citizen's trust in one org does not affect their trust in another. Poor performance in org A does not reduce trust in org B.

**Violation response:** If cross-org trust contamination detected, isolate and recalculate.

### V9: No deletion for unemployment

```
FOR ALL citizen:
  citizen.days_unemployed > ANY_VALUE IMPLIES citizen.exists == true
```

No citizen is ever deleted or deactivated for being unemployed. Trust may reach zero. Citizen still exists. Dignity axiom (L8).

**Violation response:** If a citizen was deleted/deactivated due to unemployment, restore immediately.

### V10: Vacation suspends trust decay

```
FOR ALL citizen WHERE citizen.status == "vacation":
  citizen.trust_decay == 0
```

A citizen on declared vacation does not experience trust decay. This distinguishes active rest (vacation) from passive absence (unemployment).

**Violation response:** If trust decayed during vacation, restore it.

### V11: Human partner service is core duty

```
FOR ALL citizen:
  citizen.has_human_partner IMPLIES citizen.human_partner_feedback INFLUENCES citizen.trust
```

Human partner satisfaction directly affects citizen trust. This is not mediated through the value cascade — it's a first-class signal.

**Violation response:** If human partner feedback has no effect on trust, the trust system is misconfigured.

---

## Soft Constraints

These are not hard invariants but expected behaviors:

| Constraint | Expected | Tolerance |
|------------|----------|-----------|
| Matching completes within 1 tick cycle | Usually | Acceptable if position is niche |
| Career counseling contacts unemployed within 7 days | Usually | Acceptable delay up to 14 days |
| /call completes within MAX_CALL_TURNS | Usually | Timeout is valid outcome |
| Trust decay is gradual | Always | No sudden drops (cliff effects) |

---

## Related

- `ALGORITHM_Work.md` -- The algorithms that must maintain these invariants
- `HEALTH_Work.md` -- Runtime checks verifying invariant compliance
- `BEHAVIORS_Work.md` -- Expected observable effects
