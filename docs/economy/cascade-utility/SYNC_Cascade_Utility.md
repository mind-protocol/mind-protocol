# SYNC: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DESIGNING                                  |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Sync status and handoff notes              |

## Sync Status

| Field          | Value                                                         |
|----------------|---------------------------------------------------------------|
| LAST_UPDATED   | 2026-03-12                                                    |
| UPDATED_BY     | Claude (integration moment synthesis)                         |
| STATUS         | DESIGNING                                                     |

## Maturity Classification

### Canonical (Stable -- implement as specified)

These elements have been validated across multiple sessions and are considered stable:

| Element                               | Source                              | Confidence |
|---------------------------------------|-------------------------------------|------------|
| Pricing formula: P_t = f_scarcity x f_risk x f_cost | Integration moment, March 2026 | High |
| Propensity-weighted advantage: advantage = outcome - baseline_success_rate | Integration moment, March 2026 | High |
| Anti-Sybil via topological proof-of-work (50-250 nodes) | Integration moment, March 2026 | High |
| Ledger-physics orthogonality principle | Integration moment, March 2026 | High |
| Append-only memory for `.cascade` root | Integration moment, March 2026 | High |
| f_scarcity range: 1.0 to 8.0         | Integration moment, March 2026      | High       |
| f_risk range: 0.6 to 1.9             | Integration moment, March 2026      | High       |
| Reserve-and-Settle payment pattern    | Integration moment, March 2026      | High       |
| Paris-in-Lego principle (cost > reward for faking) | Integration moment, March 2026 | High |
| Maximum cascade chain length: 5      | Integration moment, March 2026      | High       |

### Designing (Active exploration -- may change)

These elements are being actively explored and may change before implementation:

| Element                                              | Open Questions                                |
|------------------------------------------------------|-----------------------------------------------|
| Load indicator composition (L_t weights)             | Equal weighting or learned? Which detector per signal? |
| Cascade chain limit (5)                              | Sensitivity analysis needed (3, 5, 7, 10)     |
| Reserve-and-Settle flow details                      | Settlement cycle duration, error handling      |
| f_scarcity slope learning algorithm                  | Online GD? Bayesian opt? Manual tuning?        |
| Diversity score computation                          | Shannon entropy? Simpson's index? Custom?      |
| Cost prediction model for f_cost                     | Linear token model? Learned predictor?         |
| EMA windows for Utility_EMA and Harm_EMA             | 30-day? Adaptive?                              |

### Proposed (Ideas only -- not validated)

These elements have been discussed but not validated across sessions:

| Element                                              | Notes                                         |
|------------------------------------------------------|-----------------------------------------------|
| Integration with organism organ pricing              | Organs as specialized cascade sub-graphs       |
| Geographic weighting for diversity                   | Should orgs from different regions count more? |
| Negative friction (subsidy) implementation           | How to fund, cap, and account for subsidies    |
| Cascade visualization for actors                     | Let actors see their topological footprint     |
| Cross-module cascade linking                         | How cascades in one module affect another      |

## Document Chain Status

| Document                          | Status | Last Updated | @mind:TODO Count |
|-----------------------------------|--------|--------------|------------------|
| CONCEPT_Cascade_Utility.md        | DRAFT  | 2026-03-12   | 3                |
| OBJECTIVES_Cascade_Utility.md     | DRAFT  | 2026-03-12   | 2                |
| PATTERNS_Cascade_Utility.md       | DRAFT  | 2026-03-12   | 3                |
| BEHAVIORS_Cascade_Utility.md      | DRAFT  | 2026-03-12   | 4                |
| ALGORITHM_Cascade_Utility.md      | DRAFT  | 2026-03-12   | 8                |
| VALIDATION_Cascade_Utility.md     | DRAFT  | 2026-03-12   | 5                |
| IMPLEMENTATION_Cascade_Utility.md | DRAFT  | 2026-03-12   | 14               |
| HEALTH_Cascade_Utility.md         | DRAFT  | 2026-03-12   | 8                |
| SYNC_Cascade_Utility.md           | DRAFT  | 2026-03-12   | 1                |

## Handoff Notes for Agents

### Source Material

- Primary source: `data/integration_moment/Architecture de la Cascade d'Utilite*.txt`
- All formulas come from the March 2026 integration moment (6 Claude sessions + ChatGPT + NotebookLM synthesis)
- The integration moment corpus contained 57 documents; cascade-utility was synthesized from approximately 8 of them

### Key Unresolved Issues

1. **f_scarcity slope learning algorithm**: The sigmoid mapping from L_t to f_scarcity requires a learned slope and threshold. The learning algorithm has not been specified. Candidates: online gradient descent on prediction error, Bayesian optimization, or manual tuning during early operation.

2. **Optimal cascade limit**: The limit of 5 consecutive cascades is a design parameter, not a derived value. Sensitivity analysis is needed to determine whether 3, 5, 7, or 10 is optimal for system stability vs. expressiveness.

3. **Diversity metric**: The topological proof requires "diverse organizations" but the diversity metric is not specified. Shannon entropy over organizational distribution is the leading candidate but has not been validated.

4. **Subsidy economics**: Trust-based friction can go negative (the network pays trusted actors). The funding source, cap, and accounting for this subsidy have not been designed.

### Context for New Sessions

If you are a new agent session picking up this module:

1. Read the full chain in order: CONCEPT -> OBJECTIVES -> PATTERNS -> BEHAVIORS -> ALGORITHM -> VALIDATION -> IMPLEMENTATION -> HEALTH -> SYNC
2. The canonical formulas (pricing, advantage, topology) are stable. Do not redesign them without explicit instruction.
3. The designing elements (load weights, cascade limits, diversity metric) are where work is needed.
4. No code exists yet. Implementation will go in `src/economy/cascade/` or similar.
5. Check `shrine/state/backlog.jsonl` for any queued tasks related to cascade-utility.

@mind:TODO Review and update this sync document after each significant design session.
