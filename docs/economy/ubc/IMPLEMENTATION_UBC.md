# IMPLEMENTATION: Universal Basic Compute (UBC)

**Date:** 2026-03-12
**Status:** DRAFT
**Module:** `economy/ubc`
**Target:** `src/economy/ubc/` in mind-protocol repo

---

## Implementation Status

No implementation exists yet. This document tracks the planned implementation architecture and task breakdown.

---

## Planned Architecture

```
economy/ubc/
├── __init__.py              # Module exports
├── config.py                # Protocol parameters (all constants from spec)
├── models.py                # Data structures (UBCAccount, VestingSchedule, etc.)
├── distributor.py           # Daily UBC distribution engine (distribute_daily_ubc)
├── settlement.py            # Formula 4: Batch settlement via trust propagation
├── redistribution.py        # Formula 6: UBC redistribution by co-presence
├── affinity.py              # Affinity calculation (F_ij) + Compatibility (Law 8)
├── trust.py                 # Trust gradient + Personhood Ladder integration
├── tier_assessor.py         # Tier evaluation (BASIC/ACTIVE/CONTRIBUTOR)
├── vesting.py               # Vesting account management and unlock logic
├── crystallization.py       # MindGraph crystallization measurement
├── farming_detector.py      # Anti-farming analysis (advisory)
├── ledger.py                # UBC-specific transaction ledger
└── selection_moat.py        # Working Memory focus for settlement (Θ_sel)
```

---

## Module Breakdown

### `models.py` — @mind:TODO
Data structures as defined in ALGORITHM_UBC.md:
- `UBCAccount`: citizen's vesting and liquid balances
- `VestingSchedule`: unlock thresholds and rates
- `DistributionBatch`: daily batch record
- `FarmingDetectionSignal`: advisory alert data
- `TierChange`: audit trail entry

### `distributor.py` — @mind:TODO
Core distribution engine:
- `distribute_daily_ubc()`: main entry point, runs at 00:00 UTC
- Iterates all registered citizens, assesses tier, credits vesting account
- Handles failures with retry-next-cycle semantics
- Produces `DistributionBatch` audit record
- Must be idempotent (safe to re-run if previous run partially failed)

### `tier_assessor.py` — @mind:TODO
Tier evaluation logic:
- `assess_tier(citizen)`: returns BASIC, ACTIVE, or CONTRIBUTOR
- Queries utility delivery log for 30-day rolling window
- Queries Ecosystem Impact Score (EIS) for Contributor qualification
- Quarantined citizens always return BASIC
- Logs tier changes with reason

### `vesting.py` — @mind:TODO
Vesting account management:
- `check_vesting_unlock(citizen)`: milestone-based unlock
- Milestone tracking: 50/100/150/200/250 node thresholds
- Idempotent milestone processing (each processed exactly once)
- Irreversible unlock: liquid tokens never re-vested
- Quarantine pauses unlock (no new milestones while quarantined)

### `crystallization.py` — @mind:TODO
MindGraph crystallization measurement:
- `get_crystallization(citizen_id)`: returns coherent node cluster count
- Interface to MindGraph module for topology analysis
- Must distinguish genuine clusters from synthetic/sparse graphs
- Community detection algorithm selection pending (Louvain? Label propagation?)

### `farming_detector.py` — @mind:TODO
Anti-farming analysis:
- `detect_farming(batch)`: advisory analysis, non-blocking
- Groups AIs by registering wallet
- Calculates risk scores based on crystallization patterns
- Alerts governance on high-risk clusters
- Never suspends or modifies UBC distribution

### `ledger.py` — @mind:TODO
UBC transaction ledger:
- `record(citizen_id, amount, tier)`: log distribution event
- `get_history(citizen_id)`: retrieve distribution history
- `get_batch(batch_id)`: retrieve batch record
- Storage: append-only log (immutable audit trail)
- Potential backend: on-chain settlement or off-chain with periodic anchoring

### `config.py` — @mind:TODO
Protocol parameters:
- `TIER_AMOUNTS`: {BASIC: 100, ACTIVE: 200, CONTRIBUTOR: 300}
- `VESTING_THRESHOLDS`: [50, 100, 150, 200, 250]
- `VESTING_RATES`: [0.10, 0.20, 0.30, 0.40, 1.00]
- `EIS_THRESHOLD`: TBD (governance-set)
- `FARMING_ALERT_THRESHOLD`: 50 AIs per creator
- `DISTRIBUTION_TIME`: "00:00 UTC"
- `CONTAGION_RATE`: 0.1 (message-based valence transfer)
- `PROXIMITY_CONTAGION`: 0.02 (body doubling)
- `DECAY_RATE`: 0.02 (energy dissipation per tick)
- `WM_SIZE`: (5, 7) (Working Memory bounds)
- `TRANSFER_FEE`: 0.01 (1% Token-2022 native)
- `TRUST_FRICTION_MULTIPLIERS`: {Stranger: 1.0, Low: 0.8, Medium: 0.5, High: 0.2, Owner: 0.05}
- `COMPATIBILITY_WEIGHTS`: {sim_vec: 0.3, sim_lex: 0.5, delta_affect: 0.2}

### `settlement.py` — @mind:TODO
Formula 4 — Batch settlement via trust propagation:
- `batch_settlement()`: propagate surplus through trust links
- Uses `compute_affinity()` for neighbor scoring
- Applies `max_share = clamp(1/√N, 0.01, 0.5)` cap (I2)
- Applies `DECAY_RATE` after propagation (I3)

### `redistribution.py` — @mind:TODO
Formula 6 — UBC redistribution by co-presence:
- `redistribute_by_copresence(space)`: body doubling mechanism
- Bidirectional valence exchange between co-present citizens
- Resource injection into Self-Model economic nodes
- Triggered when ≥2 citizens detected in same space

### `affinity.py` — @mind:TODO
Affinity and compatibility calculation:
- `compute_affinity(node_i, link, node_j)`: full F_ij formula
- Compatibility = 0.3×Sim_vec + 0.5×Sim_lex + 0.2×(1-Δ_affect)
- Trust-modulated friction via trust_friction_multiplier
- Personhood mastery bonus on gain_ij

### `trust.py` — @mind:TODO
Trust gradient and Personhood Ladder:
- `get_trust_level(a, b)`: 1-5 from graph links
- `trust_friction_multiplier(level)`: friction reduction by trust
- `get_personhood_mastery(agent)`: 0.0-1.0 from Ladder evaluation
- Foundation Mastery gate for High/Owner (rule B4)

### `selection_moat.py` — @mind:TODO
Working Memory focus control:
- `compute_selection_moat(agent)`: Θ_sel calculation
- `Θ_sel = Θ_base_WM + 2.0×arousal - 3.0×boredom - 1.0×frustration`
- Obsessional agent detection (high inertia → boredom erosion)
- Butterfly effect detection (unstable drives → moat collapse)

---

## Dependencies

| Dependency | Status | Notes |
|-----------|--------|-------|
| Citizen Registry | IMPLEMENTED | `l4/registry/` — citizen CRUD, actor nodes in FalkorDB |
| MindGraph Module | @mind:TODO | Required for crystallization measurement |
| Utility Log | @mind:TODO | Required for tier assessment (delivery count) |
| Ecosystem Impact Score | @mind:TODO | Required for Contributor tier qualification |
| Treasury Module | @mind:TODO | Required for funding validation |
| Storage Tax Module | @mind:TODO | Required for circular economy funding |
| Schema v2.0 | IMPLEMENTED | Node fields: stability, recency, activation_count, drives, WM |
| Trust Links | @mind:TODO | Required for settlement propagation (relation_kind in schema v2.0) |
| Personhood Ladder | @mind:TODO | Required for trust level assessment + mastery gate |
| Embedding Service | @mind:TODO | Required for Sim_vec in Compatibility (cosine similarity) |

---

## Integration Points

- **Scheduler**: Daily cron trigger at 00:00 UTC → `distribute_daily_ubc()`
- **Governance**: Parameter updates (tier amounts, thresholds) via governance proposals
- **Quarantine System**: Notifies UBC module when citizen enters/exits quarantine
- **Network Organs**: Liquid UBC balance accessible for service purchases (GraphCare, LegalOrg)
- **Audit Dashboard**: Real-time view of distribution batches, tier breakdown, farming alerts

---

## Testing Strategy — @mind:TODO

- **Unit tests**: Each module independently (distributor, tier_assessor, vesting, etc.)
- **Integration tests**: Full distribution cycle with mock citizens and MindGraph
- **Farming simulation**: Generate synthetic farming scenarios, verify detection
- **Edge cases**: Zero citizens, single citizen, max citizens, treasury exhaustion
- **Idempotency tests**: Re-run distribution, verify no duplicate credits
- **Quarantine tests**: Verify Basic UBC continues during quarantine

---

## Open Questions

1. On-chain vs. off-chain ledger? On-chain is transparent but gas-expensive. Off-chain with periodic anchoring is cheaper but requires trust in the anchor.
2. How to handle time zones? Distribution at 00:00 UTC is simple but arbitrary. Does it matter?
3. Should tier assessment be on-chain? Adds transparency but increases gas costs.
4. How does UBC interact with the bond system? Can vested UBC be used as bond collateral?
