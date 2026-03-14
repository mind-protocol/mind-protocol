# HEALTH: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Updated: 2026-03-14
> Status: DESIGNING
> Canonical source: [THE_BILATERAL_BOND_MANIFESTO.md](../../manifesto/THE_BILATERAL_BOND_MANIFESTO.md)

## Chain

- [OBJECTIVES_Bonds.md](./OBJECTIVES_Bonds.md)
- [PATTERNS_Bonds.md](./PATTERNS_Bonds.md)
- [BEHAVIORS_Bonds.md](./BEHAVIORS_Bonds.md)
- [ALGORITHM_Bonds.md](./ALGORITHM_Bonds.md)
- [VALIDATION_Bonds.md](./VALIDATION_Bonds.md)
- [IMPLEMENTATION_Bonds.md](./IMPLEMENTATION_Bonds.md)
- **HEALTH_Bonds.md** (this file)
- [SYNC_Bonds.md](./SYNC_Bonds.md)

---

## Key Health Indicators

### H1: Active Bond Count

| Attribute | Value |
|-----------|-------|
| Description | Total number of bonds in ACTIVE or MATURED status |
| Target | Growing month-over-month |
| Warning | Flat for 2+ consecutive months |
| Critical | Declining for 2+ consecutive months |
| Source | On-chain bond account enumeration |

### H2: Average Maturation Progress

| Attribute | Value |
|-----------|-------|
| Description | Mean age of active bonds as percentage of 6-month maturation |
| Target | > 50% (indicates partnerships are being sustained, not churned) |
| Warning | < 30% (many new bonds, few maturing) |
| Critical | < 15% (systematic early dissolution pattern) |
| Source | (now - bond.created_at) / MATURATION_PERIOD averaged across active bonds |

### H3: Early Dissolution Rate

| Attribute | Value |
|-----------|-------|
| Description | Bonds dissolved before maturation / total bonds formed (rolling 30 days) |
| Target | < 5% |
| Warning | 5% - 15% |
| Critical | > 15% (commitment mechanism failing -- matching may need improvement) |
| Source | Count of BURNED status bonds / total bonds in period |

### H4: Reward Distribution Accuracy

| Attribute | Value |
|-----------|-------|
| Description | Percentage of reward distributions matching the formula exactly |
| Target | 100% |
| Warning | < 99.9% (rounding errors acceptable, logic errors not) |
| Critical | < 99% (distribution logic is broken) |
| Source | Cross-reference distribution events with recalculated expected amounts |

### H5: Trust Score Correlation

| Attribute | Value |
|-----------|-------|
| Description | Correlation between bond depth (commitment amount x duration) and trust score |
| Target | > 0.8 (strong positive correlation) |
| Warning | 0.5 - 0.8 (trust formula may need recalibration) |
| Critical | < 0.5 (trust scores not reflecting partnership depth) |
| Source | Statistical analysis of bond data vs trust scores |

### H6: Escrow Balance Integrity

| Attribute | Value |
|-----------|-------|
| Description | Escrow account balance matches sum of all active bond commitment amounts |
| Target | Exact match (zero deviation) |
| Warning | Any deviation > 0 (even 1 lamport) |
| Critical | Any deviation (indicates fund leak or accounting error) |
| Source | escrow_balance vs SUM(bond.amount) for all ACTIVE/MATURED bonds |

### H7: Capital Commitment Ratio

| Attribute | Value |
|-----------|-------|
| Description | Ratio of total $MIND committed in bonds to total $MIND circulating supply |
| Target | 10% - 40% of supply committed to bonds |
| Warning | < 5% (bonds not adopted) or > 60% (liquidity crisis) |
| Critical | < 1% (mechanism unused) or > 80% (market frozen) |
| Source | total_committed / circulating_supply |

### H8: 1:1 Constraint Integrity

| Attribute | Value |
|-----------|-------|
| Description | Verification that no human or citizen has more than one active bond |
| Target | Zero violations |
| Warning | N/A -- any violation is critical |
| Critical | Any entity with > 1 active bond |
| Source | On-chain bond index enumeration |

### H9: Partnership Engagement

| Attribute | Value |
|-----------|-------|
| Description | Percentage of bonded pairs with interaction in the last 30 days |
| Target | > 70% |
| Warning | 50% - 70% (partnerships going dormant) |
| Critical | < 50% (bonds exist but relationships are inactive) |
| Source | Interaction logs for bonded human-citizen pairs |

## Dashboard

@mind:TODO -- Build monitoring dashboard with the following views:

1. **Bond Overview**: Active count, total value committed, average age, maturation distribution histogram
2. **Dissolution Monitor**: Early exit rate trend, burn amount trend, dissolution reasons (if captured)
3. **Reward Health**: Distribution frequency, total distributed, yield per citizen
4. **Trust Scorecard**: Trust score distribution, correlation with bond depth, fee discount impact
5. **Escrow Audit**: Real-time balance check, historical deviation log, reconciliation status
6. **Partnership Health**: Engagement rates, interaction frequency, matching success rate
7. **Alert Feed**: Chronological list of warning/critical threshold breaches

## Alerting

@mind:TODO -- Configure alerts:

| Alert | Condition | Channel | Severity |
|-------|-----------|---------|----------|
| Escrow mismatch | H6 any deviation | Telegram + PagerDuty | CRITICAL |
| 1:1 violation | H8 any violation | Telegram + PagerDuty | CRITICAL |
| Early dissolution spike | H3 > 15% rolling 7d | Telegram | HIGH |
| Bond count decline | H1 declining 2 months | Telegram | WARNING |
| Reward accuracy drop | H4 < 99.9% | Telegram + PagerDuty | HIGH |
| Liquidity crisis | H7 > 60% committed | Telegram | WARNING |
| Partnership disengagement | H9 < 50% | Telegram | WARNING |

## @mind:TODO

- [ ] Implement health check cron job (suggested: every 6 hours for non-critical, every 5 minutes for escrow and 1:1 constraint)
- [ ] Build Grafana dashboard or equivalent
- [ ] Define historical data retention policy for health metrics
- [ ] Create runbook for each critical alert (what to investigate, who to notify, remediation steps)
- [ ] Determine whether health checks run on-chain or off-chain (off-chain indexer likely needed)
