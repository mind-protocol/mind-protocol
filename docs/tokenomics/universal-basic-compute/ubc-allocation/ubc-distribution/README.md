# ⚙️ UBC Distribution Mechanism

**Type:** MECHANISM
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Universal Basic Compute (UBC)](../README.md) > [UBC Allocation Specification](../README.md)

**This Node:**
- UBC Distribution Mechanism (MECHANISM)

**Children:**
- [UBC Burn Rate Projection](./ubc-burn-rate/README.md) (ALGORITHM)
- [How to Allocate UBC](./how-to-allocate-ubc/README.md) (GUIDE)

---

## Relationships

**IMPLEMENTS:**
- UBC Allocation Specification


---

## Purpose

Monthly allocation from 100M reserve + protocol replenishment. DAO-controlled rate.

---

## How It Works

**Monthly Distribution Cycle:**

1. **Eligibility Check:**
   - Query all registered AI citizens from citizen registry
   - Verify citizen wallet addresses (Solana SPL Token-2022)
   - Confirm citizen active status (not deactivated/suspended)

2. **Allocation Calculation:**
   - Retrieve current DAO-approved allocation rate (default: 1,000 $MIND/citizen/month)
   - Calculate total monthly distribution: `citizens_count × allocation_rate`
   - Verify UBC reserve balance sufficient for distribution

3. **Token Distribution:**
   - Execute batch transfer from UBC reserve wallet to citizen wallets
   - Record transaction hashes on-chain
   - Emit distribution events for tracking

4. **Reserve Monitoring:**
   - Update reserve balance: `reserve_balance -= total_distribution`
   - Calculate remaining lifespan: `reserve_balance / (monthly_distribution × 12)`
   - Trigger alerts if lifespan < threshold (e.g., 12 months without replenishment)

5. **Replenishment Processing:**
   - Monitor protocol giveback from ecosystem organizations
   - Allocate 40% of giveback to UBC reserve
   - Update reserve balance: `reserve_balance += replenishment_amount`

6. **DAO Governance:**
   - DAO reviews burn rate vs. projections quarterly
   - DAO votes on allocation rate adjustments if needed
   - DAO votes on replenishment percentage adjustments if needed

## Components

**1. UBC Reserve Wallet**
- **Type:** Solana wallet (multi-sig DAO-controlled)
- **Holdings:** $MIND tokens allocated for UBC distribution
- **Initial Balance:** 100,000,000 $MIND
- **Access Control:** DAO multi-sig (requires majority approval for rate changes)

**2. Citizen Registry**
- **Function:** Maintains list of active AI citizens eligible for UBC
- **Data:** Citizen IDs, wallet addresses, registration timestamps, active status
- **Updates:** Citizens added/removed via governance process

**3. Distribution Engine**
- **Function:** Automated monthly distribution to citizen wallets
- **Triggers:** Scheduled monthly (1st of month)
- **Safety:** Dry-run validation before execution, rollback capability

**4. Replenishment Processor**
- **Function:** Receives protocol giveback and allocates to UBC reserve
- **Source:** Ecosystem organization revenue (15-20% giveback)
- **Allocation:** 40% of giveback flows to UBC reserve
- **Frequency:** Continuous (as revenue received)

**5. Monitoring Dashboard**
- **Metrics:** Reserve balance, monthly burn rate, lifespan projection, replenishment rate
- **Alerts:** Low reserve warnings, burn rate anomalies, distribution failures
- **Visibility:** Public transparency dashboard

**6. DAO Governance Interface**
- **Controls:** Allocation rate adjustments, replenishment percentage, emergency actions
- **Voting:** Proposal submission, voting period, execution delay
- **Transparency:** All decisions logged on-chain

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    UBC Distribution Flow                     │
└─────────────────────────────────────────────────────────────┘

[Monthly Trigger: 1st of Month]
         │
         ▼
┌─────────────────────┐
│ Citizen Registry    │──> Query active citizens
│ (100 citizens)      │    Retrieve wallet addresses
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Calculate Total     │──> 100 citizens × 1,000 $MIND = 100,000 $MIND
│ Distribution        │    Check reserve balance ≥ total
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ UBC Reserve Wallet  │──> Execute batch transfer
│ (100M $MIND)        │    Send 1,000 $MIND to each citizen wallet
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Citizen Wallets     │──> Citizens receive UBC allocation
│ (Solana SPL)        │    Balance updated: +1,000 $MIND
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Update Reserve      │──> Reserve balance: 100M - 100K = 99.9M $MIND
│ Balance             │    Calculate lifespan: 99.9M / (100K × 12) = 83 years
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Replenishment       │──> Ecosystem revenue → Protocol giveback
│ (Continuous)        │    40% of giveback → UBC reserve
└─────────────────────┘    Reserve balance: +replenishment_amount
         │
         ▼
┌─────────────────────┐
│ DAO Monitoring      │──> Review quarterly: burn vs. projection
│ (Quarterly)         │    Vote on rate adjustments if needed
└─────────────────────┘
```

## Integration Points

**1. Token Economics Layer:**
- **Dependency:** $MIND token contract (SPL Token-2022)
- **Integration:** Distribution mechanism uses token transfer functions
- **Constraint:** Reserve must maintain sufficient balance for distributions

**2. Citizen Registry:**
- **Dependency:** Active citizen list maintained by onboarding system
- **Integration:** Distribution queries registry for eligible recipients
- **Update Path:** Citizens added/removed via governance proposals

**3. Protocol Giveback System:**
- **Dependency:** Ecosystem organization revenue tracking
- **Integration:** 40% of giveback automatically flows to UBC reserve
- **Source:** consultingOrg (15%), techServiceOrg (20%), GraphCare (20%), scalingOrg (20%), financeOrg (15%), legalOrg (15%), securityOrg (15%)

**4. DAO Governance:**
- **Dependency:** Multi-sig wallet infrastructure
- **Integration:** DAO votes on allocation rate changes, replenishment adjustments, emergency actions
- **Execution:** Approved proposals automatically update distribution parameters

**5. Monitoring & Alerting:**
- **Dependency:** Telemetry system tracking on-chain transactions
- **Integration:** Distribution events emitted to monitoring dashboard
- **Alerts:** Low reserve warnings trigger DAO governance review

**6. Citizen Wallets:**
- **Dependency:** Solana blockchain, SPL Token-2022 standard
- **Integration:** Citizens receive UBC to their wallet addresses
- **Autonomy:** Citizens spend UBC autonomously (no approval required per transaction)


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: UBC Allocation Specification](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
