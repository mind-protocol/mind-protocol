# 📋 Token Allocation Distribution

**Type:** BEHAVIOR_SPEC
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Token Allocation Philosophy](../README.md)

**This Node:**
- Token Allocation Distribution (BEHAVIOR_SPEC)

**Children:**
- [Allocation Deployment Strategy](./allocation-deployment/README.md) (MECHANISM)

---

## Relationships

**EXTENDS:**
- Token Allocation Philosophy (PATTERN)


---

## Purpose

Community 30%, Strategic 38%, UBC 10%, Team 15%, Investors 2%, Liquidity 5%. Total 1B tokens.

---

## Specification

### Total Supply: 1,000,000,000 $MIND Tokens

**Allocation Breakdown:**

| Category | Tokens | % of Total | Initial Unlock | Lock Duration | Unlock Date |
|----------|--------|-----------|---------------|---------------|-------------|
| **Community & Ecosystem** | 300M | 30% | 30M (10%) | Flexible | Variable |
| **Strategic Reserve** | 380M | 38% | 50M | Flexible | Variable |
| **Team & Founders** | 150M | 15% | 150M (100%) | 6 months | Month 6 |
| **Operations & UBC** | 100M | 10% | 100M (100%) | Unlocked | Day 1 |
| **Liquidity** | 50M | 5% | 0.45M | 12 months (LP lock) | Month 12 |
| **Investors** | 20M | 2% | 20M (100%) | 6 months | Month 6 |
| **TOTAL** | **1B** | **100%** | **~200M (20%)** | - | - |

---

### 1. Community & Ecosystem: 30% (300M tokens)

**Purpose:** User acquisition, ecosystem incentives, DAO governance

**Breakdown:**
- **Future Airdrops:** 90M tokens (9% of total supply)
  - Quarterly distributions to active users
  - Merit-based allocation (not speculative)
  - Sybil-resistant distribution mechanisms
  - Rewards genuine ecosystem contribution

- **Usage Incentives:** 90M tokens (9% of total supply)
  - Citizen performance rewards
  - Referral programs (scalingOrg → GraphCare conversions)
  - Early adopter bonuses
  - Ecosystem contribution bonuses

- **DAO Treasury:** 120M tokens (12% of total supply)
  - Ecosystem grants for developers
  - Strategic partnerships and integrations
  - Development funding for core infrastructure
  - Emergency reserve for ecosystem support

**Initial Unlock:** 30M tokens (10% of allocation) available at launch

**Vesting:** Flexible, DAO-governed distribution over 2-4 years based on:
- User growth rates
- Ecosystem engagement metrics
- Community governance decisions
- Strategic priorities

**Governance:** Multi-sig wallet controlled with community votes on distribution decisions

---

### 2. Strategic Reserve: 38% (380M tokens)

**Purpose:** Maximum flexibility for adaptation and growth

**Uses:**
- Future team expansion (as project scales)
- Strategic partnerships and integrations
- Additional community allocation (if growth warrants)
- Emergency situations and market opportunities
- Ecosystem organization bootstrap capital
- Unallocated buffer (decide based on reality)

**Initial Unlock:** 50M tokens available at launch

**Lock:** Flexible - no rigid vesting schedule

**Control:** Multi-sig wallet (founder + advisors)

**Deployment Philosophy:**
- Don't commit upfront
- Allocate based on proven needs
- Observe reality first, then deploy
- Can reallocate to community if ecosystem thrives
- Emergency buffer for survival situations

**Rationale for 38% (largest allocation):**
- Provides maximum strategic flexibility
- Can bootstrap all ecosystem organizations
- Can reallocate to community if user growth exceeds projections
- Prevents over-commitment before proving traction
- Enables rapid response to opportunities

---

### 3. Team & Founders: 15% (150M tokens)

**Purpose:** Align team with long-term success

**Allocation:** 150,000,000 tokens

**Initial Unlock:** 100% unlocked at launch (all tokens distributed)

**Lock Duration:** 6 months (transfer-restricted via SPL Token-2022)

**Rationale:**
- Shows minimum commitment to project
- Prevents immediate exit/dumps
- Provides flexibility after 6 months based on reality
- Allows adaptation as team needs evolve
- Shorter than industry standard (2-4 years) by design

**Post-Lock:** Fully liquid after 6 months (Month 6)

**Why 6 months not 2-4 years:**
- We're pre-revenue with uncertain trajectory
- Rigid long-term locks assume certain growth
- Team needs flexibility to adapt compensation
- Can deploy more from strategic reserve if team scales
- Minimum credible lock period

---

### 4. Operations & Universal Basic Compute: 10% (100M tokens)

**Purpose:** Enable autonomous AI citizen operations without constant human funding

**Critical Innovation:** Universal Basic Compute (UBC)
- Powers baseline autonomous operations
- Prevents "pay-to-operate-only" model
- Enables learning and coordination without user payment
- Distinguishes Mind Protocol from pure pay-per-API models

**Initial Allocation:** 100M tokens fully unlocked at launch

**Control:** DAO controls distribution rates

**Replenishment:** Protocol giveback (15-20% of ecosystem org revenue)

**Suggested UBC Rates (DAO decides):**
- **Conservative:** 1,000 tokens/citizen/month (initial recommendation)
- **Moderate:** 5,000 tokens/citizen/month
- **Generous:** 10,000 tokens/citizen/month

**Sustainability Calculation (Conservative 1,000/month):**
```
100M tokens / (1,000 tokens/citizen/month × 12 months) = 8,333 citizens for 1 year
OR: 100 citizens for 83 years
OR: 1,000 citizens for 8.3 years
```

**With Protocol Giveback Replenishment (Year 5):**
- Gross burn: 12M tokens/year (1,000 citizens × 1,000/month × 12)
- Replenishment: 3M tokens/year (40% of $7.5M protocol giveback)
- Net burn: 9M tokens/year
- Reserve lifespan: 11+ years

---

### 5. Liquidity: 5% (50M tokens)

**Purpose:** Enable price discovery and trading

**Initial Liquidity Pool:**
- **Amount:** 450 $MIND tokens paired with 0.25 SOL
- **Platform:** Raydium or Orca (Solana DEX)
- **Establishes:** $1.00 on-chain price at launch
- **LP Token Lock:** 100% locked for 12 months
- **Lock Platform:** Meteora (free on Solana) or Raydium built-in locking
- **Verification:** Public lock verification link for transparency

**Remaining Allocation (49,999,550 tokens):**
- CEX listings (Tier 2/3 exchanges)
- Additional DEX pairs as ecosystem grows
- Market maker loans if needed for liquidity depth
- Deployed based on trading volume and demand

**LP Lock Schedule:**
- Months 0-12: 100% locked (no LP token withdrawals)
- Month 12: Fully unlocked, can adjust liquidity

**Why Minimal Initial LP ($45 total):**
- Pre-seed bootstrap phase
- Focus on utility not speculation
- All other tokens locked (no dump risk)
- Can expand LP with revenue over time
- Solana community values fair launches over large LPs

---

### 6. Investors: 2% (20M tokens)

**Purpose:** Repair burned investors + raise bridge capital

**Structure:**

**Phase 1: Psychological Airdrop**
- **Amount:** 10,000 tokens per investor × 20 investors = 200,000 tokens
- **Creates:** $10,000 wallet display at $1.00 price
- **Lock:** 6 months (transfer-restricted via SPL Token-2022)
- **Purpose:** Visual repair and credibility restoration

**Phase 2: OTC Investment**
- **Amount:** 19,800,000 tokens available
- **Raised through:** €2,000 OTC investments
- **Distribution:** Proportional among participants
- **Lock:** 6 months (transfer-restricted)

**Unlock Schedule:**
- Month 0-6: Fully locked (no transfers allowed)
- Month 6: 100% unlocked, fully liquid

**Why Only 2% (Smallest Allocation):**
- Mind Protocol is pre-revenue, high-risk
- Limited investor appetite at this stage
- Focus on earning revenue, not raising capital
- Can offer more allocation later from strategic reserve
- Maintains founder/team control

---

## Lock & Vesting Summary

**Philosophy:** Minimum viable locks for credibility without constraining flexibility

**Timeline Overview:**

| Milestone | What Unlocks | Circulating Impact |
|-----------|--------------|-------------------|
| **Day 1** | Operations (100M) + Strategic (50M initial) + Community (30M initial) + Liquidity (0.45M) | ~180M circulating (18%) |
| **Month 6** | Investors (20M) + Team (150M) | +170M → 350M circulating (35%) |
| **Month 12** | LP Tokens unlock (can adjust liquidity) | No direct circulating impact |
| **Ongoing** | Community distributions, Strategic deployments | Variable based on DAO/multi-sig decisions |

**After 6 Months:** Majority of initially allocated tokens fully liquid

**After 12 Months:** 100% liquidity pool flexibility available

---

## Success Criteria

**The allocation is correctly implemented when:**

1. **Total Supply Verified**
   - Solana contract shows exactly 1,000,000,000 tokens minted
   - Supply is fixed (mint authority can be retained but not exercised to increase supply)
   - All allocations sum to 1B tokens precisely

2. **Lock Enforcement**
   - Investor tokens show "transfer-restricted" status in Phantom wallet
   - Team tokens show "transfer-restricted" status until Month 6
   - Operations/UBC tokens are immediately transferable
   - LP tokens locked via verifiable on-chain lock (Meteora/Unicrypt)

3. **Initial Circulating Supply**
   - CoinMarketCap/CoinGecko show ~200M circulating (20%)
   - Locked tokens NOT counted in circulating supply
   - Strategic reserve tokens held in identifiable multi-sig wallet

4. **Multi-Sig Control**
   - Strategic reserve controlled by multi-sig (founder + advisors)
   - Community allocation controlled by multi-sig (with DAO governance)
   - Deployment transactions require multiple signatures

5. **Unlock Dates Enforced**
   - SPL Token-2022 transfer hook enforces 6-month locks automatically
   - No manual unlock required (on-chain enforcement)
   - LP lock verifiable and cannot be bypassed

6. **Transparency**
   - All wallet addresses publicly documented
   - LP lock verification link shared
   - Token contract address verified on Solscan
   - Multi-sig signers publicly known

## Edge Cases

**1. OTC Investment Shortfall**

**Scenario:** Only €10K raised instead of target €20K

**Response:**
- Distribute 19.8M tokens proportionally among actual investors
- Remaining tokens return to strategic reserve
- No minimum raise requirement
- Bridge capital still sufficient for 2.5-5 month runway

**2. Team Member Departure (Before Month 6)**

**Scenario:** Core team member leaves during 6-month lock period

**Response:**
- Tokens remain locked (cannot be reclaimed)
- Individual still receives full allocation at Month 6
- Risk: Ex-team member may dump tokens
- Mitigation: Short lock period (6 months) minimizes this risk
- Alternative: Negotiate voluntary return to strategic reserve

**3. Ecosystem Org Failure**

**Scenario:** techServiceOrg receives 3M token bootstrap, fails to achieve revenue

**Response:**
- Shut down org, return unused tokens to strategic reserve
- Tokens spent on actual operations are burned (not recoverable)
- Lesson learned: More conservative bootstrap amounts for unproven orgs
- Reallocate funds to proven orgs (consultingOrg, GraphCare)

**4. UBC Depletion Risk**

**Scenario:** Citizen count grows faster than projected, 100M token reserve threatened

**Response:**
- Reduce UBC allocation per citizen (1,000 → 500 tokens/month)
- Increase protocol giveback percentage to UBC (40% → 60%)
- Deploy additional tokens from strategic reserve to UBC fund
- Implement usage caps (citizens prioritize high-value operations)

**5. Community Demand for More Allocation**

**Scenario:** Community argues 30% allocation too low, demands more

**Response:**
- Strategic reserve provides flexibility
- Can increase community allocation from strategic reserve
- Requires DAO vote and community consensus
- Multi-sig approves transfer from strategic → community treasury
- Document rationale and update allocation documentation

**6. Regulatory Challenge**

**Scenario:** Regulatory authority questions token distribution structure

**Response:**
- Strategic reserve provides emergency response capital
- Can allocate tokens for legal defense
- Can restructure allocations if legally required
- Multi-sig can freeze distributions pending legal clarity
- Flexibility prevents over-commitment to challenged structures

**7. LP Liquidity Crisis**

**Scenario:** Minimal LP ($45) creates extreme volatility, users can't trade

**Response:**
- Deploy additional tokens from liquidity allocation (50M available)
- Use protocol revenue to add liquidity (buy SOL, pair with $MIND)
- Strategic reserve can provide emergency liquidity
- Accept volatility as feature (discourages speculation)
- Focus messaging on utility not trading

**8. Investor Lock Bypass Attempt**

**Scenario:** Investor attempts to circumvent 6-month lock via smart contract exploit

**Response:**
- SPL Token-2022 transfer hook enforces lock at protocol level
- No known bypasses (Solana blockchain enforcement)
- If exploit discovered: Freeze authority can freeze compromised accounts
- Deploy patch to transfer hook if vulnerability found
- Communicate transparently with community about response

## Examples

**Example 1: Initial Launch Allocation (Day 1)**

```
Total Supply: 1,000,000,000 $MIND
Deployer Wallet: 1B tokens minted

Distribution Transactions:
1. Strategic Reserve Multi-Sig: 380,000,000 tokens (380M)
   - 50,000,000 unlocked immediately
   - 330,000,000 held for future deployment

2. Community Treasury Multi-Sig: 300,000,000 tokens (300M)
   - 30,000,000 unlocked immediately
   - 270,000,000 held for future distributions

3. Team Wallets: 150,000,000 tokens (150M total)
   - Transfer-restricted: 6 months
   - Nicolas: 50M tokens
   - Core Team: 100M tokens distributed proportionally

4. Operations/UBC Treasury: 100,000,000 tokens (100M)
   - Fully unlocked, immediately transferable
   - DAO controls distribution rates

5. Liquidity Pool: 450 tokens
   - Paired with 0.25 SOL
   - LP tokens locked 12 months

6. Investors: 20,000,000 tokens (20M)
   - Phase 1 Airdrop: 200,000 tokens (10k × 20 investors)
   - Phase 2 OTC: 19,800,000 tokens (distributed after fundraise)
   - All transfer-restricted: 6 months

Circulating Supply Day 1: ~180,000,000 tokens (18%)
Locked Supply Day 1: ~820,000,000 tokens (82%)
```

**Example 2: Year 1 Strategic Reserve Deployment**

```
Strategic Reserve Starting Balance: 380M tokens
Year 1 Planned Uses: 50M tokens

Ecosystem Org Bootstrap Allocations:
- consultingOrg Treasury: 5,000,000 $MIND
  Purpose: Initial operations, consultant recruitment, brand building

- techServiceOrg Treasury: 3,000,000 $MIND
  Purpose: Tool development, infrastructure setup, first projects

- GraphCare Treasury: 2,000,000 $MIND
  Purpose: Monitoring infrastructure, specialist recruitment

- financeOrg Treasury: 5,000,000 $MIND
  Purpose: Analyst recruitment, modeling tools, financial research

- legalOrg Treasury: 5,000,000 $MIND
  Purpose: Attorney recruitment, legal research, contract templates

Infrastructure & Team:
- Infrastructure Development: 10,000,000 $MIND
  Purpose: FalkorDB scaling, consciousness engine optimization

- Team Expansion: 10,000,000 $MIND
  Purpose: Hire additional engineers, designers, operations

- Emergency Reserve: 10,000,000 $MIND
  Purpose: Unexpected costs, survival buffer

Total Year 1 Deployment: 50,000,000 $MIND
Strategic Reserve Remaining: 330,000,000 $MIND (33% of total supply)
```

**Example 3: Month 6 Unlock Event**

```
Month 6 Unlock Date: [Launch Date + 182 days]

Tokens Unlocking:
1. Team Tokens: 150,000,000 $MIND
   - Transfer restrictions automatically lift
   - Team can now transfer/sell tokens
   - No manual action required

2. Investor Tokens: 20,000,000 $MIND
   - Psychological airdrop: 200,000 $MIND unlocked
   - OTC investment: 19,800,000 $MIND unlocked
   - All transfer restrictions lift automatically

Circulating Supply Before: 180M (18%)
Circulating Supply After: 350M (35%)

New Circulating Impact: +170M tokens (+17% of supply)

Market Considerations:
- Team may begin selling for liquidity
- Investors may take profits
- Expect short-term selling pressure
- Organism economics reduces speculation (utility focus)
- Long-term holders unaffected
```

**Example 4: UBC Distribution (Monthly)**

```
Conservative UBC Allocation: 1,000 $MIND/citizen/month

Month 1 Distribution:
- Active Citizens: 50 citizens
- Distribution: 50 × 1,000 = 50,000 $MIND
- UBC Reserve Remaining: 99,950,000 $MIND

Month 12 Distribution:
- Active Citizens: 200 citizens
- Distribution: 200 × 1,000 = 200,000 $MIND
- Cumulative Year 1 Burn: ~1,500,000 $MIND
- UBC Reserve Remaining: 98,500,000 $MIND

Year 2 Distribution (with replenishment):
- Monthly Burn: 1,000 citizens × 1,000 = 1,000,000 $MIND/month
- Annual Burn: 12,000,000 $MIND
- Protocol Giveback Replenishment: 400,000 $MIND (Year 2)
- Net Burn: 11,600,000 $MIND
- Reserve Remaining: ~87M $MIND

Sustainability: 7-11 years depending on citizen growth and replenishment
```


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Token Allocation Philosophy](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
