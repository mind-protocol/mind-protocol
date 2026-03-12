# ALGORITHM: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Algorithms and data structures             |

## Overview

The Cascade d'Utilite implements three core algorithms:

1. **Dynamic Pricing** -- computes the effective price of a service request from real system signals
2. **Propensity-Weighted Advantage** -- distributes rewards based on task difficulty, not task volume
3. **Topological Validation** -- verifies that a contribution has genuine, diverse downstream usage

These algorithms interact but are independently specified. Pricing uses trust scores (from bonds) and load signals (from infrastructure). Advantage uses task metadata (from the backlog). Topological validation uses the dependency graph (from the `.cascade` root).

## Data Structures

### LoadIndicator (L_t)

Composite measure of current system excitation, computed from change-point normalized signals.

```
LoadIndicator:
  rho: float            # global system excitation level (criticality parameter)
                         # 0.0 = idle, 1.0 = critical
  backlog: int           # number of stimuli awaiting injection into the graph
  latency_slip: float    # processing time drift, computed as Page-Hinkley residual
                         # positive = slowing down, negative = speeding up
  compute_occ: float     # GPU/CPU utilization fraction (0.0 - 1.0)
  drop_ratio: float      # fraction of stimuli clamped by saturation gate
                         # 0.0 = nothing dropped, 1.0 = everything dropped
```

@mind:TODO Define the change-point normalization procedure for each signal. Which detector (Page-Hinkley, CUSUM, ADWIN) is used for each?

### PriceResult

Output of the pricing algorithm for a single request.

```
PriceResult:
  P_t: float              # base price before rebate
  f_scarcity: float        # scarcity factor: 1.0 (idle) to 8.0 (critical)
  f_risk: float            # risk factor: 0.6 (maximum trust) to 1.9 (high-harm potential)
  f_cost: float            # cost factor: predicted computational complexity
                           # estimated from token count, action count, or model tier
  rebate: float            # utility-based discount: proportional to Utility_EMA / Harm_EMA
                           # 0.0 (no discount) to 0.9 (maximum discount, capped)
  P_eff: float             # effective price: P_t * (1 - rebate)
```

### TopologyProof

Evidence structure for topological validation.

```
TopologyProof:
  contribution_id: string     # unique identifier of the contribution being validated
  node_count: int             # number of coherent nodes in the dependency graph
  org_count: int              # number of distinct organizations using the contribution
  max_depth: int              # longest cascade chain from contribution to leaf
  diversity_score: float      # 0.0 (single org) to 1.0 (maximally diverse)
  crystallized: bool          # true if node_count >= 50 and diversity thresholds met
```

@mind:TODO Define the diversity_score computation. Is it Shannon entropy over org distribution? Simpson's index? Something else?

### AdvantageResult

Output of the propensity-weighted advantage computation.

```
AdvantageResult:
  citizen_id: string          # the actor who attempted the task
  task_id: string             # the task attempted
  baseline_success_rate: float # historical success rate for this task category
  outcome: float              # 0.0 (failure) or 1.0 (success)
  advantage: float            # outcome - baseline_success_rate (clamped to >= 0)
```

## Algorithm 1: compute_price(request, sender)

### Step 1: Compute Composite Load (L_t)

Aggregate the five load signals into a single composite indicator. Each signal is first normalized using its respective change-point detector to remove trend and seasonality.

```
L_t = w_rho * rho + w_backlog * norm(backlog) + w_latency * latency_slip
    + w_compute * compute_occ + w_drop * drop_ratio
```

@mind:TODO Learn the weights (w_rho, w_backlog, w_latency, w_compute, w_drop) from operational data. Initial values: equal weighting (0.2 each).

### Step 2: Map L_t to f_scarcity

```
f_scarcity = 1.0 + slope * sigmoid(L_t - threshold)
```

Range: 1.0 (system idle) to 8.0 (system critical).

The slope and threshold are learned parameters. The sigmoid ensures smooth transitions -- no price discontinuities during load changes.

@mind:TODO Specify the learning algorithm for slope and threshold. Online gradient descent? Bayesian optimization? Manual tuning initially?

### Step 3: Compute f_risk from Sender Trust Profile

```
IF sender.trust_score >= TRUST_MAX:
    f_risk = 0.6    # maximum trust, minimum risk surcharge
ELIF sender.trust_score <= TRUST_MIN:
    f_risk = 1.9    # minimum trust, maximum risk surcharge
ELSE:
    f_risk = 1.9 - 1.3 * (sender.trust_score - TRUST_MIN) / (TRUST_MAX - TRUST_MIN)
```

The f_risk factor reflects the system's confidence that this sender's request will produce value rather than harm. Trusted actors pay less because they are less likely to waste system resources.

### Step 4: Estimate f_cost (Reserve and Settle)

```
f_cost = predict_cost(request)
# Based on: estimated token count, action complexity, model tier required
# This is the RESERVE phase -- lock the predicted cost upfront
```

After the request is processed:

```
actual_cost = measure_actual_consumption(request)
settlement = actual_cost - f_cost
# SETTLE phase: refund overpayment or charge underpayment
```

@mind:TODO Define the cost prediction model. Start with a simple linear model (tokens x rate), evolve to learned predictor.

### Step 5: Compute Base Price

```
P_t = f_scarcity * f_risk * f_cost
```

### Step 6: Apply Rebate

```
rebate = clamp(Utility_EMA / max(Harm_EMA, epsilon), 0.0, 0.9)
P_eff = P_t * (1.0 - rebate)
```

Actors with high utility-to-harm ratios receive a discount up to 90%. The epsilon prevents division by zero when Harm_EMA is negligible.

@mind:TODO Define the EMA window for Utility_EMA and Harm_EMA. Candidate: 30-day exponential moving average.

## Algorithm 2: compute_advantage(citizen, task_outcome)

### Step 1: Look Up Baseline Success Rate

```
baseline = task_registry.get_success_rate(task.category)
# Computed from historical completion data across all citizens
```

@mind:TODO Define the update frequency for baseline_success_rate. Real-time? Daily? Per-epoch?

### Step 2: Compute Advantage

```
advantage = max(0.0, task_outcome - baseline)
```

Examples:
- Hard task (baseline 0.3), success: advantage = 0.7
- Easy task (baseline 0.9), success: advantage = 0.1
- Any task, failure: advantage = 0.0 (no punishment)

### Step 3: Apply to Reward Distribution

```
citizen.reward_pool += advantage * reward_rate
```

@mind:TODO Define reward_rate and its relationship to the cascade revenue pool.

## Algorithm 3: validate_topology(contribution)

### Step 1: Count Coherent Nodes

```
nodes = graph.traverse_downstream(contribution.id)
coherent_nodes = [n for n in nodes if n.is_active and n.has_genuine_usage]
```

### Step 2: Check Minimum Threshold

```
IF len(coherent_nodes) < 50:
    RETURN TopologyProof(crystallized=False, ...)
    # Contribution not yet crystallized -- no value recognized
```

### Step 3: Verify Diversity

```
orgs = unique([n.organization for n in coherent_nodes])
diversity_score = compute_diversity(orgs)

IF diversity_score < DIVERSITY_THRESHOLD:
    RETURN TopologyProof(crystallized=False, ...)
    # Insufficient organizational diversity -- possible Sybil
```

@mind:TODO Set DIVERSITY_THRESHOLD. Candidate: 0.5 (at least moderate diversity).

### Step 4: Verify Depth

```
max_depth = max([graph.depth(contribution.id, n.id) for n in coherent_nodes])

IF max_depth < MIN_CASCADE_DEPTH:
    RETURN TopologyProof(crystallized=False, ...)
    # Flat graph -- insufficient cascade evidence
```

@mind:TODO Set MIN_CASCADE_DEPTH. Candidate: 3 (at least three hops from contribution to leaf).

### Step 5: Return Proof

```
RETURN TopologyProof(
    contribution_id=contribution.id,
    node_count=len(coherent_nodes),
    org_count=len(orgs),
    max_depth=max_depth,
    diversity_score=diversity_score,
    crystallized=True
)
```

## Key Design Decisions

### D1: Reserve-and-Settle vs Pay-Per-Token

```
Decision: Reserve-and-Settle
Alternatives considered: Pay-per-token, flat-rate, auction

IF payment model needed:
    Lock predicted cost upfront (RESERVE)
    Process the request
    Settle on actual consumption (SETTLE)

WHY: Prevents cost uncertainty for users while ensuring fair payment.
     Pay-per-token creates anxiety (users don't know final cost).
     Flat-rate creates waste (users don't care about efficiency).
     Auction creates speculation (price reflects demand, not cost).
     Reserve-and-Settle balances predictability with accuracy.
```

### D2: Smooth Scarcity Curve vs Step Function

```
Decision: Smooth sigmoid curve
Alternatives considered: Step function, linear ramp

WHY: Step functions create arbitrage opportunities at boundaries.
     Linear ramps don't capture the non-linear nature of congestion.
     Sigmoid provides smooth, bounded, non-linear mapping.
```

@mind:TODO Validate that the sigmoid parameterization prevents price oscillation during rapid load changes.
