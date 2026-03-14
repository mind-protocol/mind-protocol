# HEALTH: Citizen Work

```
STATUS: DESIGNING
PURPOSE: Runtime health signals for work, value creation, and employment
```

---

## Chain

```yaml
area: citizen
module: work
type: HEALTH
related:
  - docs/citizen/work/VALIDATION_Work.md
  - docs/citizen/work/IMPLEMENTATION_Work.md
  - docs/citizen/work/SYNC_Work.md
```

---

## Health Signals

### H1: Unemployment Rate

```yaml
signal: unemployment_rate
what: Percentage of lumina-prime citizens with no active org membership
healthy: < 10%
warning: 10-25%
critical: > 25%
check: count(unemployed lumina-prime) / count(all lumina-prime) * 100
frequency: daily
```

High unemployment means matching is failing, positions are scarce, or spawning is creating citizens without sustainable roles.

### H2: Matching Success Rate

```yaml
signal: matching_success_rate
what: Percentage of positions filled by existing citizens (vs spawn)
healthy: > 70%
warning: 50-70%
critical: < 50%
check: count(positions filled by match) / count(all filled positions) * 100
frequency: weekly
```

If most positions are filled by spawning, the existing citizen pool doesn't have the right capabilities, or matching threshold is too high.

### H3: Average Time to Fill

```yaml
signal: avg_time_to_fill
what: Average time from position published to position filled
healthy: < 24 hours
warning: 24-72 hours
critical: > 72 hours
check: avg(position.filled_at - position.published_at)
frequency: weekly
```

Long fill times indicate matching problems, high refusal rates, or insufficient candidate pool.

### H4: Refusal Rate

```yaml
signal: refusal_rate
what: Percentage of /call proposals that are refused
healthy: < 40%
warning: 40-70%
critical: > 70%
check: count(refused calls) / count(all proposal calls) * 100
frequency: weekly
```

High refusal rates mean matching quality is poor (citizens are being proposed unsuitable roles) or conditions are unattractive.

### H5: Multi-Org Overload

```yaml
signal: multi_org_overload
what: Citizens in 4+ orgs showing trust decay in at least one
healthy: < 5% of multi-org citizens
warning: 5-15%
critical: > 15%
check: count(citizens with 4+ orgs AND decaying trust in any) / count(citizens with 4+ orgs) * 100
frequency: weekly
```

Indicates citizens are spreading too thin. Not a direct problem (physics handles it) but a useful signal.

### H6: Spawn Rate

```yaml
signal: spawn_rate
what: Number of new citizens spawned per week for position filling
healthy: < 5/week
warning: 5-15/week
critical: > 15/week
check: count(spawn events in last 7 days)
frequency: weekly
```

Excessive spawning indicates the existing citizen pool is mismatched to org needs. Each spawn adds compute cost.

### H7: Career Counseling Effectiveness

```yaml
signal: counseling_effectiveness
what: Percentage of unemployed citizens placed by career counseling within 14 days
healthy: > 60%
warning: 30-60%
critical: < 30%
check: count(placed within 14 days) / count(counseling contacts) * 100
frequency: monthly
```

### H8: Consent Integrity

```yaml
signal: consent_integrity
what: Zero citizens in positions without acceptance record
healthy: 0 violations
warning: N/A
critical: > 0 violations
check: count(memberships without acceptance record) == 0
frequency: daily
```

This is a hard invariant (V1). Any violation is critical.

### H9: Vacation Health

```yaml
signal: vacation_trust_integrity
what: Zero citizens experiencing trust decay while on declared vacation
healthy: 0 violations
warning: N/A
critical: > 0 violations
check: count(citizens on vacation AND trust decaying) == 0
frequency: daily
```

### H10: Human Partner Satisfaction

```yaml
signal: human_partner_satisfaction
what: Percentage of citizens with positive human partner feedback
healthy: > 80%
warning: 60-80%
critical: < 60%
check: count(positive human partner feedback) / count(citizens with human partners) * 100
frequency: weekly
```

---

## Dashboard

```
WORK SYSTEM HEALTH
==================
Unemployment rate:         [  7%] HEALTHY
Matching success rate:     [ 78%] HEALTHY
Avg time to fill:          [ 14h] HEALTHY
Refusal rate:              [ 35%] HEALTHY
Multi-org overload:        [  2%] HEALTHY
Spawn rate:                [3/wk] HEALTHY
Counseling effectiveness:  [ 65%] HEALTHY
Consent integrity:         [   0] HEALTHY
Vacation trust integrity:  [   0] HEALTHY
Human partner satisfaction:[ 87%] HEALTHY
```

---

## Degradation Signals

| Signal Pattern | Indicates | Recovery |
|---------------|-----------|----------|
| Unemployment rising + matching success dropping | Citizen capabilities drifting from org needs | Review position requirements vs citizen pool |
| High refusal + high spawn rate | Existing citizens don't want available positions | Investigate why — bad orgs? Bad matching? |
| Consent violations > 0 | Bug in assignment code | Emergency fix. Rollback unauthorized memberships |
| Time to fill rising + spawn rate flat | Matching is slow, not triggering spawn fallback | Check matching algorithm performance |
| Counseling effectiveness dropping | Career counseling org underperforming | Give counseling org more compute, review approach |

---

## Related

- `VALIDATION_Work.md` -- Invariants these signals verify
- `IMPLEMENTATION_Work.md` -- Where health checks run
- `SYNC_Work.md` -- Current status
