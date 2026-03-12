# IMPLEMENTATION: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Implementation status and code mapping     |

## Implementation Status

No implementation exists yet. This document describes the target architecture and tracks progress toward it.

## Target Code Structure

@mind:TODO Create the following directory structure in the mind-protocol repository:

```
src/economy/cascade/
  __init__.py
  pricing.py           # compute_price() -- Algorithm 1
  advantage.py         # compute_advantage() -- Algorithm 2
  topology.py          # validate_topology() -- Algorithm 3
  load_indicator.py    # LoadIndicator composition and normalization
  types.py             # PriceResult, TopologyProof, AdvantageResult, LoadIndicator
  constants.py         # TRUST_MAX, TRUST_MIN, DIVERSITY_THRESHOLD, etc.

src/economy/cascade/tests/
  __init__.py
  test_pricing.py      # Unit tests for pricing algorithm
  test_advantage.py    # Unit tests for propensity-weighted advantage
  test_topology.py     # Unit tests for topological validation
  test_invariants.py   # Validation rules V1-V7 as automated tests
  test_integration.py  # End-to-end cascade flow tests
```

## Module Mapping

| Algorithm               | Target File                        | Status      |
|-------------------------|------------------------------------|-------------|
| compute_price()         | src/economy/cascade/pricing.py     | @mind:TODO  |
| compute_advantage()     | src/economy/cascade/advantage.py   | @mind:TODO  |
| validate_topology()     | src/economy/cascade/topology.py    | @mind:TODO  |
| LoadIndicator           | src/economy/cascade/load_indicator.py | @mind:TODO |
| Data structures         | src/economy/cascade/types.py       | @mind:TODO  |
| Constants               | src/economy/cascade/constants.py   | @mind:TODO  |

## Dependencies

| Dependency                  | Purpose                                        | Status      |
|-----------------------------|------------------------------------------------|-------------|
| Bond trust system           | Provides sender.trust_score for f_risk         | @mind:TODO  |
| Task registry               | Provides baseline_success_rate for advantage   | @mind:TODO  |
| Infrastructure metrics      | Provides rho, backlog, latency, compute, drops | @mind:TODO  |
| `.cascade` storage backend  | Append-only contribution and usage records     | @mind:TODO  |
| $MIND ledger                | Provides Delta_E_allowed (clamping gate)       | @mind:TODO  |

## Implementation Phases

### Phase 1: Types and Constants

@mind:TODO Define all data structures (`LoadIndicator`, `PriceResult`, `TopologyProof`, `AdvantageResult`) as Python dataclasses or Pydantic models.

@mind:TODO Set initial constant values:
- TRUST_MAX, TRUST_MIN
- DIVERSITY_THRESHOLD (candidate: 0.5)
- MIN_CASCADE_DEPTH (candidate: 3)
- MAX_CASCADE_CHAIN (5)
- SCARCITY_MIN (1.0), SCARCITY_MAX (8.0)
- REBATE_CAP (0.9)

### Phase 2: Pricing Algorithm

@mind:TODO Implement `compute_price()` with the following sub-steps:
1. Load indicator composition (weighted sum of normalized signals)
2. Scarcity mapping (sigmoid with learned slope and threshold)
3. Risk computation (linear interpolation from trust score)
4. Cost estimation (initial: linear token model)
5. Base price multiplication
6. Rebate application (Utility_EMA / Harm_EMA)

@mind:TODO Implement Reserve-and-Settle flow:
1. Reserve: lock predicted cost before processing
2. Process: execute the request
3. Settle: compute actual cost, refund or charge difference

### Phase 3: Advantage Algorithm

@mind:TODO Implement `compute_advantage()`:
1. Baseline lookup from task registry
2. Advantage computation (outcome - baseline, clamped to >= 0)
3. Reward pool update

@mind:TODO Build or integrate with the task registry for baseline_success_rate tracking.

### Phase 4: Topological Validation

@mind:TODO Implement `validate_topology()`:
1. Downstream graph traversal
2. Coherent node counting (active + genuine usage)
3. Diversity scoring
4. Depth verification
5. Crystallization decision (50-250 node range)

@mind:TODO Design the graph storage and traversal infrastructure.

### Phase 5: Integration Tests

@mind:TODO Implement all validation rules (V1-V7) as automated tests.
@mind:TODO Create end-to-end test: stimulus injection -> pricing -> processing -> advantage -> topology validation.

## Notes

- All pricing computation must be deterministic given the same inputs. No randomness in price determination.
- The reserve-and-settle pattern requires a settlement ledger separate from the $MIND ledger.
- The topology validation may be computationally expensive for large graphs. Consider caching crystallization proofs with a TTL.
