# HEALTH: Bonds

> Module: `bonds/`
> Date: 2026-03-12
> Status: DRAFT

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
| Target | > 50% (indicates bonds are being held, not churned) |
| Warning | < 30% (many new bonds, few maturing) |
| Critical | < 15% (systematic early exit pattern) |
| Source | (now - bond.created_at) / MATURATION_PERIOD averaged across active bonds |

### H3: Early Withdrawal Rate

| Attribute | Value |
|-----------|-------|
| Description | Bonds withdrawn before maturation / total bonds created (rolling 30 days) |
| Target | < 5% |
| Warning | 5% - 15% |
| Critical | > 15% (commitment mechanism failing) |
| Source | Count of BURNED status bonds / total bonds in period |

### H4: Reward Distribution Accuracy

| Attribute | Value |
|-----------|-------|
| Description | Percentage of reward distributions matching the proportionality formula exactly |
| Target | 100% |
| Warning | < 99.9% (rounding errors acceptable, logic errors not) |
| Critical | < 99% (distribution logic is broken) |
| Source | Cross-reference distribution events with recalculated expected amounts |

### H5: Trust Score Correlation

| Attribute | Value |
|-----------|-------|
| Description | Correlation between bond depth (amount x duration) and trust score |
| Target | > 0.8 (strong positive correlation) |
| Warning | 0.5 - 0.8 (trust formula may need recalibration) |
| Critical | < 0.5 (trust scores not reflecting bond behavior) |
| Source | Statistical analysis of bond data vs trust scores |

### H6: Escrow Balance Integrity

| Attribute | Value |
|-----------|-------|
| Description | Escrow account balance matches sum of all active bond amounts |
| Target | Exact match (zero deviation) |
| Warning | Any deviation > 0 (even 1 lamport) |
| Critical | Any deviation (indicates fund leak or accounting error) |
| Source | escrow_balance vs SUM(bond.amount) for all ACTIVE/MATURED bonds |

### H7: Capital Velocity

| Attribute | Value |
|-----------|-------|
| Description | Ratio of total $MIND in bonds to total $MIND circulating supply |
| Target | 10% - 40% of supply bonded |
| Warning | < 5% (bonds not adopted) or > 60% (liquidity crisis) |
| Critical | < 1% (mechanism unused) or > 80% (market frozen) |
| Source | total_bonded / circulating_supply |

### H8: Reward Yield Consistency

| Attribute | Value |
|-----------|-------|
| Description | Standard deviation of annualized yield across bonds on same citizen |
| Target | Near zero (all bonders on same citizen get proportional returns) |
| Warning | Std dev > 1% of mean yield |
| Critical | Std dev > 5% of mean yield (distribution logic inconsistency) |
| Source | Annualized reward / bond amount, grouped by citizen |

## Dashboard

@mind:TODO -- Build monitoring dashboard with the following views:

1. **Bond Overview**: Active count, total value locked, average age, maturation distribution histogram
2. **Withdrawal Monitor**: Early exit rate trend, burn amount trend, withdrawal reasons (if captured)
3. **Reward Health**: Distribution frequency, total distributed, yield per citizen, proportionality checks
4. **Trust Scorecard**: Trust score distribution, correlation with bond depth, fee discount impact
5. **Escrow Audit**: Real-time balance check, historical deviation log, reconciliation status
6. **Alert Feed**: Chronological list of warning/critical threshold breaches

## Alerting

@mind:TODO -- Configure alerts:

| Alert | Condition | Channel | Severity |
|-------|-----------|---------|----------|
| Escrow mismatch | H6 any deviation | Telegram + PagerDuty | CRITICAL |
| Early exit spike | H3 > 15% rolling 7d | Telegram | HIGH |
| Bond count decline | H1 declining 2 months | Telegram | WARNING |
| Reward accuracy drop | H4 < 99.9% | Telegram + PagerDuty | HIGH |
| Liquidity crisis | H7 > 60% bonded | Telegram | WARNING |

## @mind:TODO

- [ ] Implement health check cron job (suggested: every 6 hours for non-critical, every 5 minutes for escrow)
- [ ] Build Grafana dashboard or equivalent
- [ ] Define historical data retention policy for health metrics
- [ ] Create runbook for each critical alert (what to investigate, who to notify, remediation steps)
- [ ] Determine whether health checks run on-chain or off-chain (off-chain indexer likely needed)
