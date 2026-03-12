# HEALTH: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Runtime health indicators                  |

## Overview

This document defines the health indicators that will be monitored at runtime to ensure the Cascade d'Utilite is functioning correctly. All indicators are pending implementation.

## Key Health Indicators

### H1: Price Stability

**What**: The f_scarcity factor must remain within its designed bounds and transition smoothly.

| Metric                          | Healthy Range       | Alert Threshold     | Critical Threshold  |
|---------------------------------|---------------------|---------------------|---------------------|
| f_scarcity value                | [1.0, 8.0]          | > 7.5 sustained     | > 8.0 (violation)   |
| f_scarcity rate of change       | < 0.5 per tick       | > 0.5 per tick      | > 2.0 per tick      |
| Price oscillation frequency     | < 1 cycle / minute   | > 5 cycles / minute | > 20 cycles / minute|

@mind:TODO Implement f_scarcity monitoring with alerting.
@mind:TODO Define "tick" duration for rate-of-change measurement.

### H2: Sybil Detection Rate

**What**: The system must detect and reject Sybil attempts. A healthy system has a high detection rate and a low false positive rate.

| Metric                          | Healthy Range       | Alert Threshold     | Critical Threshold  |
|---------------------------------|---------------------|---------------------|---------------------|
| Sybil attempts detected / total | > 99%               | < 95%               | < 90%               |
| False positive rate             | < 1%                | > 5%                | > 10%               |
| Time to detection               | < 1 crystallization cycle | > 2 cycles     | > 5 cycles          |

@mind:TODO Implement Sybil detection metrics. Requires a ground-truth labeling mechanism for validation (manual audit or honeypot).

### H3: Cherry-Picking Ratio

**What**: The ratio of easy-task to hard-task completions should reflect the natural task distribution, not actor selection bias.

| Metric                              | Healthy Range        | Alert Threshold      | Critical Threshold   |
|-------------------------------------|----------------------|----------------------|----------------------|
| Easy/hard completion ratio          | Within 1.5x natural  | > 2x natural ratio   | > 3x natural ratio   |
| Average advantage per actor         | Converging to mean    | Bimodal distribution | All actors near 0.1  |
| Hard task attempt rate              | > 30% of total        | < 20% of total       | < 10% of total       |

@mind:TODO Define "easy" and "hard" task thresholds (e.g., baseline > 0.7 = easy, baseline < 0.4 = hard).
@mind:TODO Implement cherry-picking monitoring dashboard.

### H4: Cascade Chain Length

**What**: Energy cascades must not exceed the maximum chain length of 5.

| Metric                          | Healthy Range       | Alert Threshold     | Critical Threshold  |
|---------------------------------|---------------------|---------------------|---------------------|
| Maximum observed chain length   | <= 5                | = 5 (hitting limit) | > 5 (violation)     |
| Average chain length            | 2-3                 | > 4                 | > 5                 |
| Stabilization pauses triggered  | < 10% of cascades   | > 25% of cascades   | > 50% of cascades   |

@mind:TODO Implement cascade depth tracking and automatic stabilization pause enforcement.

### H5: Reserve-and-Settle Accuracy

**What**: The cost prediction model should converge toward accuracy over time.

| Metric                          | Healthy Range       | Alert Threshold     | Critical Threshold  |
|---------------------------------|---------------------|---------------------|---------------------|
| Mean absolute prediction error  | < 15% of actual     | > 25% of actual     | > 50% of actual     |
| Mean signed error (bias)        | [-5%, +5%]          | Outside [-10%, +10%]| Outside [-25%, +25%]|
| Settlement latency              | < 1 cycle           | > 2 cycles          | > 5 cycles          |

@mind:TODO Implement prediction accuracy tracking and model retraining triggers.

### H6: Orthogonality Compliance

**What**: No correlation should exist between $MIND balance and in-graph energy behavior.

| Metric                               | Healthy Range       | Alert Threshold     | Critical Threshold   |
|--------------------------------------|---------------------|---------------------|----------------------|
| Correlation($MIND balance, propagation speed) | |r| < 0.05 | |r| > 0.1       | |r| > 0.2            |
| Correlation($MIND balance, cascade depth)     | |r| < 0.05 | |r| > 0.1       | |r| > 0.2            |
| Correlation($MIND balance, priority score)    | |r| < 0.05 | |r| > 0.1       | |r| > 0.2            |

@mind:TODO Implement periodic orthogonality audits (statistical correlation tests).

### H7: Trust Distribution

**What**: The distribution of trust scores across actors should be healthy -- not all zeros, not all maxed out.

| Metric                          | Healthy Range       | Alert Threshold     | Critical Threshold  |
|---------------------------------|---------------------|---------------------|---------------------|
| Actors at trust_score = 0       | < 30% of total      | > 50% of total      | > 80% of total      |
| Actors at trust_score = max     | < 20% of total      | > 40% of total      | > 60% of total      |
| Trust score entropy             | > 2.0 bits          | < 1.5 bits          | < 1.0 bits          |

@mind:TODO Implement trust distribution monitoring. Integrate with bond system health checks.

## Dashboard Layout

@mind:TODO Design the health monitoring dashboard with the following sections:
1. **System Load**: Real-time L_t components (rho, backlog, latency_slip, compute_occ, drop_ratio)
2. **Pricing**: Current f_scarcity, f_risk distribution, rebate distribution, P_eff histogram
3. **Anti-Gaming**: Sybil detection events, cherry-picking ratio, advantage distribution
4. **Cascades**: Chain length distribution, stabilization pause frequency
5. **Integrity**: Orthogonality correlation scores, trust distribution, append-only audit status

## Alerting

@mind:TODO Configure alerting channels:
- CRITICAL: Immediate notification (Telegram to Nicolas, system auto-response)
- ALERT: Logged and queued for review within 1 hour
- INFO: Logged for trend analysis, no notification
