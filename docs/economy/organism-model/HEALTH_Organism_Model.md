# HEALTH: Organism Model

| Field | Value |
|---|---|
| **Module** | `economy/organism-model` |
| **Type** | HEALTH |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (integration moment synthesis) |

---

## Overview

Health indicators for the organism model. These metrics determine whether the economy is functioning as a healthy organism or drifting toward pathological states (market dynamics, convergence, or organ failure).

@mind:TODO All indicators below are design targets. No collection infrastructure exists yet.

---

## Key Health Indicators

### H1: Pricing Formula Convergence

**What it measures:** Whether prices across the ecosystem are determined by membrane physics or by emergent market-like dynamics.

| Metric | Target | Warning | Critical |
|---|---|---|---|
| % transactions priced by formula | 100% | < 99% | < 95% |
| Price variance for identical inputs | 0 | > 0.01 | > 0.05 |
| Average friction coefficient | 0.1 - 0.5 | < 0.05 or > 0.7 | < 0.01 or > 0.9 |

@mind:TODO Define how to detect "market-like" pricing behavior (bilateral negotiation bypassing the formula).

---

### H2: Mirror Ratio Distribution

**What it measures:** Whether the AI population maintains healthy cognitive diversity (80/20 Mirror).

| Metric | Target | Warning | Critical |
|---|---|---|---|
| Population mean alignment | 78-82% | 75-85% | < 70% or > 90% |
| Population mean friction | 18-22% | 15-25% | < 10% or > 30% |
| Standard deviation of alignment | > 3% | < 2% | < 1% (convergence) |
| Citizens flagged for convergence risk | < 5% | 5-15% | > 15% |
| Citizens flagged for opposition risk | < 3% | 3-10% | > 10% |

@mind:TODO Define the sampling cadence. Monthly evaluation of 10% sample is proposed; validate whether this catches convergence early enough.

---

### H3: Quarantine Population

**What it measures:** Whether the quarantine system is functioning as rehabilitation (low steady-state population) or as a dumping ground (growing population).

| Metric | Target | Warning | Critical |
|---|---|---|---|
| Quarantine population (% of total) | < 1% | 1-3% | > 3% |
| Average quarantine duration | < 60 days | 60-120 days | > 120 days |
| Rehabilitation success rate | > 80% | 50-80% | < 50% |
| Citizens in quarantine > 180 days | 0 | 1-3 | > 3 |
| Counselor-to-quarantined ratio | >= 2:1 | 1.5:1 | < 1:1 |

@mind:TODO Define "rehabilitation success rate." Is it measured by time to reinstatement, recidivism rate, or both?

---

### H4: Responsibility Cascade Resolution

**What it measures:** Whether harm events are resolved efficiently through the cascade without bottlenecks.

| Metric | Target | Warning | Critical |
|---|---|---|---|
| % harm events resolved at Level 1 (AI) | > 60% | 40-60% | < 40% |
| % harm events reaching Treasury (L4) | < 5% | 5-15% | > 15% |
| Average resolution time | < 48h | 48h-7d | > 7d |
| Unresolved harm events | 0 | 1-3 | > 3 |
| Escalation documentation completeness | 100% | < 100% | < 90% |

@mind:TODO Define what constitutes "resolution" at each level. Is monetary compensation sufficient, or is behavioral change required?

---

### H5: Organ Health Metrics

**What it measures:** The functional health of each of the 5 organs.

#### Heart (Mind Foundation)
| Metric | Target | Warning | Critical |
|---|---|---|---|
| UBC circulation rate | Stable | -10% deviation | -25% deviation |
| L4 validation uptime | > 99.9% | < 99.9% | < 99% |
| Governance proposal throughput | > 1/week | < 1/month | Stalled |

#### Kidney (GraphCare)
| Metric | Target | Warning | Critical |
|---|---|---|---|
| Graph integrity score | > 99% | 95-99% | < 95% |
| Cleanup backlog | < 100 items | 100-500 | > 500 |
| Filtration latency | < 1s | 1-5s | > 5s |

#### Brain (HRI)
| Metric | Target | Warning | Critical |
|---|---|---|---|
| Evidence synthesis throughput | > 10/day | 5-10/day | < 5/day |
| Insight quality score (peer review) | > 4/5 | 3-4/5 | < 3/5 |
| Research pipeline depth | > 5 active | 2-5 active | < 2 active |

#### Digestive System (DataPipe)
| Metric | Target | Warning | Critical |
|---|---|---|---|
| Data transformation throughput | Stable | -20% deviation | -50% deviation |
| Error rate | < 0.1% | 0.1-1% | > 1% |
| Pipeline latency (p99) | < 5s | 5-30s | > 30s |

#### Immune System (LegalOrg)
| Metric | Target | Warning | Critical |
|---|---|---|---|
| Predator detection rate | > 95% | 80-95% | < 80% |
| False positive rate | < 5% | 5-15% | > 15% |
| Compliance audit pass rate | > 98% | 90-98% | < 90% |

@mind:TODO These organ metrics are placeholders. Each organ's team must validate and refine their own health indicators.

---

### H6: Trust Economy Health

**What it measures:** Whether trust is functioning as the primary economic signal.

| Metric | Target | Warning | Critical |
|---|---|---|---|
| Average trust_discount applied | 5-15% | < 3% or > 20% | < 1% or > 25% |
| Average utility_rebate applied | 3-10% | < 1% or > 15% | < 0.5% or > 18% |
| Trust score growth rate (ecosystem-wide) | Positive | Flat | Negative |
| Trust monotonicity violations | 0 | > 0 | > 3 |

---

## Dashboard Design

@mind:TODO Design and implement a real-time health dashboard showing:
- Overall organism health (composite score)
- Per-organ health status (green/yellow/red)
- Mirror ratio distribution chart
- Quarantine population trend
- Cascade resolution funnel
- Trust economy trends

---

## Alerting Thresholds

@mind:TODO Configure alerting for all Critical thresholds. Warning thresholds should generate daily digest reports. Critical thresholds should page on-call.

---

## References

- VALIDATION_Organism_Model.md (validation rules V1-V8)
- ALGORITHM_Organism_Model.md (algorithm specifications)
- Manifeste du Mind Protocol (5 inversions)
