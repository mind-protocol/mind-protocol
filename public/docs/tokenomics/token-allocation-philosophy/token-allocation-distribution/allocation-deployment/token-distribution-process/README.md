# 📖 Token Distribution Process

**Type:** GUIDE
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
[Token Allocation Philosophy](../README.md) > [Token Allocation Distribution](../README.md) > [Allocation Deployment Strategy](../README.md)

**This Node:**
- Token Distribution Process (GUIDE)

**Children:**
- (No children - leaf node)

---

## Relationships

**DOCUMENTS:**
- Allocation Deployment Strategy


---

## Purpose

How to deploy tokens from strategic reserve, when to unlock, approval process, tracking

---

## Prerequisites

**Before executing token distribution, ensure you have:**

### Technical Prerequisites

1. **Solana Wallet Setup**
   - Deployment wallet with sufficient SOL balance (≥0.5 SOL recommended)
   - Multi-sig wallets configured (strategic reserve, community treasury)
   - Test wallets for devnet validation

2. **Token Deployment Scripts**
   - SPL Token-2022 deployment script tested on devnet
   - Transfer restriction implementation (6-month locks)
   - Airdrop distribution script
   - Multi-sig transaction scripts

3. **Infrastructure Access**
   - Access to Raydium or Orca DEX for liquidity pool creation
   - Meteora or Team Finance account for LP token locking
   - Solscan API access for verification
   - Multi-sig platform access (e.g., Squads, Realms)

### Data Prerequisites

4. **Investor Information**
   - List of 20 investor Phantom wallet addresses (for psychological airdrop)
   - OTC investment tracking spreadsheet prepared
   - Designated SOL receiving wallet address
   - Investment confirmation process defined

5. **Allocation Documentation**
   - Finalized allocation breakdown (1B total supply)
   - Strategic reserve deployment plan (Year 1-5)
   - Ecosystem org bootstrap allocations defined
   - Team distribution list with wallet addresses

6. **Governance Setup**
   - Multi-sig signers identified (founder + advisors)
   - Signature thresholds defined (e.g., 3-of-5)
   - Decision-making process documented
   - Emergency override procedures established

### Legal & Compliance Prerequisites

7. **Legal Review**
   - Token classification reviewed (utility token)
   - Terms of service prepared
   - Privacy policy for wallet data collection
   - Compliance with local regulations verified

8. **Communication Materials**
   - Launch announcement prepared
   - Token contract details documented
   - LP lock verification process explained
   - Investor communication templates ready

---

## Step-by-Step Instructions

### Phase 1: Token Deployment (Day 0)

**Morning: Token Contract Deployment**

1. **Deploy $MIND Token (SPL Token-2022)**
   ```bash
   # Connect to Solana mainnet
   solana config set --url https://api.mainnet-beta.solana.com

   # Deploy token with Token-2022 extensions
   spl-token create-token --program-id TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb \
     --enable-metadata \
     --enable-transfer-hook

   # Record token address: [TOKEN_ADDRESS]

   # Create token account for deployment wallet
   spl-token create-account [TOKEN_ADDRESS]

   # Mint total supply: 1,000,000,000 tokens
   spl-token mint [TOKEN_ADDRESS] 1000000000
   ```

2. **Verify Contract on Solscan**
   - Navigate to https://solscan.io/token/[TOKEN_ADDRESS]
   - Verify total supply: 1,000,000,000
   - Verify decimals: 9
   - Verify Token-2022 extensions enabled

3. **Set Token Metadata**
   ```bash
   # Update token metadata
   spl-token update-metadata [TOKEN_ADDRESS] \
     name "Mind Protocol" \
     symbol "MIND" \
     uri "https://mindprotocol.com/token-metadata.json"
   ```

**Afternoon: Liquidity Pool Creation**

4. **Create Initial LP on Raydium/Orca**
   ```
   Platform: Raydium (recommended for Solana)
   Pair: MIND/SOL

   Deposit amounts:
   - 450 $MIND tokens
   - 0.25 SOL (~$45 at $180/SOL)

   Established price: $1.00 per $MIND
   (0.25 SOL / 450 MIND = 0.000556 SOL per MIND)
   (0.000556 SOL × $180/SOL = $1.00 per MIND)

   Receive: LP tokens representing pool share
   ```

5. **Lock LP Tokens (12 Months)**
   ```
   Platform: Meteora (free on Solana) or Team Finance

   Lock parameters:
   - Amount: 100% of LP tokens
   - Duration: 12 months (365 days)
   - Beneficiary: Deployment wallet (can claim after lock)

   Save verification link for transparency
   ```

6. **Verify LP Lock Publicly**
   - Share verification link in announcement
   - Verify lock duration shows 365 days
   - Verify unlock date is 12 months from today
   - Confirm 100% of LP tokens locked (not partial)

**Evening: Transfer Restrictions Configuration**

7. **Configure 6-Month Transfer Locks**
   ```bash
   # Set transfer hook for investor tokens (6-month lock)
   spl-token set-transfer-hook [TOKEN_ADDRESS] \
     --lock-duration 15768000  # 6 months in seconds

   # Set transfer hook for team tokens (6-month lock)
   spl-token set-transfer-hook [TOKEN_ADDRESS] \
     --lock-duration 15768000

   # Operations/UBC tokens remain unlocked (no hook)
   ```

8. **Test Transfer Restrictions**
   - Send test tokens to test wallet with lock
   - Verify wallet shows "transfer-restricted" status
   - Attempt transfer (should fail with error)
   - Verify unlock date displayed correctly

---

### Phase 2: Initial Distribution (Day 1-2)

**Step 1: Investor Psychological Airdrop**

9. **Collect Investor Wallet Addresses**
   - Email 20 investors requesting Phantom wallet addresses
   - Verify addresses are valid Solana addresses (base58 format)
   - Store in secure spreadsheet with investor names

10. **Execute Airdrop (200,000 tokens total)**
    ```bash
    # For each investor:
    spl-token transfer [TOKEN_ADDRESS] 10000 [INVESTOR_WALLET] \
      --transfer-hook-account [LOCK_PROGRAM] \
      --fund-recipient

    # Repeat for all 20 investors
    # Total distributed: 10,000 × 20 = 200,000 tokens
    ```

11. **Verify Airdrop Success**
    - Ask investors to add token contract to Phantom
    - Verify they see "10,000 $MIND" in wallet
    - Verify they see "$10,000" value at $1.00 price
    - Verify lock symbol/indicator visible
    - Confirm they cannot transfer (locked)

**Step 2: Multi-Sig Wallet Distributions**

12. **Strategic Reserve Multi-Sig**
    ```bash
    # Transfer 380M tokens to strategic reserve multi-sig
    spl-token transfer [TOKEN_ADDRESS] 380000000 [STRATEGIC_MULTISIG_ADDRESS]

    # Verify:
    # - Balance shows 380,000,000 tokens
    # - Multi-sig control active (requires 3-of-5 signatures)
    # - No transfer restrictions (flexible deployment)
    ```

13. **Community Treasury Multi-Sig**
    ```bash
    # Transfer 300M tokens to community treasury multi-sig
    spl-token transfer [TOKEN_ADDRESS] 300000000 [COMMUNITY_MULTISIG_ADDRESS]

    # Verify:
    # - Balance shows 300,000,000 tokens
    # - DAO governance control configured
    # - Initial 30M available, 270M reserved
    ```

14. **Operations/UBC Treasury**
    ```bash
    # Transfer 100M tokens to operations treasury
    spl-token transfer [TOKEN_ADDRESS] 100000000 [OPERATIONS_TREASURY_ADDRESS]

    # Verify:
    # - Balance shows 100,000,000 tokens
    # - Fully unlocked (no transfer restrictions)
    # - DAO controls distribution rates
    ```

15. **Team Token Distribution**
    ```bash
    # Transfer 150M tokens to team wallets (with 6-month lock)

    # Founder allocation:
    spl-token transfer [TOKEN_ADDRESS] 50000000 [FOUNDER_WALLET] \
      --transfer-hook-account [LOCK_PROGRAM]

    # Core team allocations (100M total):
    spl-token transfer [TOKEN_ADDRESS] [AMOUNT] [TEAM_MEMBER_WALLET] \
      --transfer-hook-account [LOCK_PROGRAM]

    # Repeat for all team members
    # Total distributed: 150,000,000 tokens

    # Verify:
    # - All team wallets show correct balances
    # - All show 6-month transfer lock
    # - Unlock date is Month 6 (182 days from today)
    ```

16. **Liquidity Reserve**
    ```bash
    # Keep remaining 49,999,550 tokens in deployment wallet
    # (450 tokens already in LP)
    # Reserved for future liquidity expansion
    ```

**Step 3: Verification & Announcement**

17. **Comprehensive Verification**
    - [ ] Total supply = 1,000,000,000 tokens
    - [ ] Strategic reserve = 380,000,000 tokens
    - [ ] Community treasury = 300,000,000 tokens
    - [ ] Team wallets = 150,000,000 tokens (locked 6 months)
    - [ ] Operations/UBC = 100,000,000 tokens
    - [ ] Investors = 200,000 tokens (locked 6 months)
    - [ ] Liquidity pool = 450 tokens (LP locked 12 months)
    - [ ] Liquidity reserve = 49,999,550 tokens
    - [ ] All locks verified and functioning
    - [ ] All multi-sigs tested and operational

18. **Public Announcement**
    - Share token contract address
    - Share LP lock verification link
    - Share multi-sig wallet addresses (transparency)
    - Publish allocation breakdown
    - Explain lock schedules and unlock dates

---

### Phase 3: OTC Investment (Day 2-7)

**Step 4: OTC Investment Collection**

19. **Set Up OTC Tracking System**
    ```
    Spreadsheet columns:
    - Investor Name
    - Phantom Wallet Address
    - SOL Amount Sent
    - EUR Equivalent (at time of receipt)
    - Timestamp
    - % of Total Pool
    - Token Allocation
    - Distribution Status
    ```

20. **Accept Investments (€2,000 each)**
    ```
    Process per investor:
    1. Investor sends €2,000 worth of SOL to designated wallet
    2. Record transaction in spreadsheet
    3. Calculate EUR value: [SOL amount] × [SOL/EUR rate]
    4. Acknowledge receipt via email
    5. Wait until investment period closes
    ```

21. **Calculate Final Allocations (Day 7)**
    ```
    Total EUR raised = Sum of all investments

    For each investor:
    Their % = (Their EUR / Total EUR) × 100
    Their tokens = Their % × 19,800,000 tokens

    Example:
    Total raised: €16,000
    Investor A contributed: €2,000
    Their %: (2,000 / 16,000) = 12.5%
    Their tokens: 12.5% × 19,800,000 = 2,475,000 tokens
    ```

22. **Distribute OTC Tokens (with 6-month lock)**
    ```bash
    # For each OTC investor:
    spl-token transfer [TOKEN_ADDRESS] [CALCULATED_AMOUNT] [INVESTOR_WALLET] \
      --transfer-hook-account [LOCK_PROGRAM]

    # Total distributed: 19,800,000 tokens (or proportional if less raised)
    ```

23. **Return Unsold Tokens to Strategic Reserve**
    ```bash
    # If only €16K raised instead of target €20K:
    # Distribute 19.8M tokens proportionally
    # No tokens returned (all allocated to actual investors)

    # If investors claim < 19.8M tokens:
    # Return unclaimed to strategic reserve
    spl-token transfer [TOKEN_ADDRESS] [UNCLAIMED_AMOUNT] [STRATEGIC_MULTISIG_ADDRESS]
    ```

---

### Phase 4: Ecosystem Organization Bootstrap (Month 1-3)

**Step 5: Strategic Reserve Deployment (Year 1)**

24. **Multi-Sig Proposal Process**
    ```
    For each ecosystem org allocation:

    1. Create multi-sig proposal:
       - Recipient: [ORG_TREASURY_ADDRESS]
       - Amount: [BOOTSTRAP_AMOUNT]
       - Purpose: [ORG_NAME] bootstrap capital
       - Runway: [MONTHS] to revenue sustainability

    2. Submit for multi-sig vote

    3. Require 3-of-5 signatures for approval

    4. Execute transfer once approved
    ```

25. **Ecosystem Org Bootstrap Transfers**
    ```bash
    # consultingOrg
    [Multi-sig transaction]
    Transfer 5,000,000 $MIND to consultingOrg treasury
    Purpose: Initial operations, consultant recruitment, brand building

    # techServiceOrg
    Transfer 3,000,000 $MIND to techServiceOrg treasury
    Purpose: Tool development, infrastructure, first projects

    # GraphCare
    Transfer 2,000,000 $MIND to GraphCare treasury
    Purpose: Monitoring infrastructure, specialist recruitment

    # financeOrg
    Transfer 5,000,000 $MIND to financeOrg treasury
    Purpose: Analyst recruitment, modeling tools, financial research

    # legalOrg
    Transfer 5,000,000 $MIND to legalOrg treasury
    Purpose: Attorney recruitment, legal research, contract templates

    Total Year 1 Org Bootstrap: 20,000,000 $MIND
    ```

26. **Infrastructure & Team Allocations**
    ```bash
    # Infrastructure development
    Transfer 10,000,000 $MIND to infrastructure fund

    # Team expansion
    Transfer 10,000,000 $MIND to team expansion fund

    # Emergency reserve
    Transfer 10,000,000 $MIND to emergency reserve wallet

    Total Year 1 Additional: 30,000,000 $MIND
    ```

27. **Track Strategic Reserve Balance**
    ```
    Starting balance: 380,000,000 $MIND
    Year 1 deployment: -50,000,000 $MIND
    Remaining: 330,000,000 $MIND (33% of total supply)

    Update public dashboard with current reserve balance
    ```

---

### Phase 5: Ongoing Management

**Step 6: UBC Distribution (Monthly)**

28. **Calculate Monthly UBC Allocation**
    ```
    Conservative rate: 1,000 $MIND/citizen/month

    Month 1 calculation:
    - Active citizens: [COUNT]
    - Distribution: [COUNT] × 1,000 $MIND

    DAO can adjust rate based on:
    - Reserve depletion rate
    - Citizen growth
    - Protocol giveback replenishment
    ```

29. **Execute Monthly UBC Transfers**
    ```bash
    # For each active citizen:
    spl-token transfer [TOKEN_ADDRESS] 1000 [CITIZEN_WALLET_ADDRESS] \
      --from [OPERATIONS_TREASURY]

    # Automate via script:
    python scripts/distribute_ubc.py \
      --rate 1000 \
      --citizens citizens_list.json \
      --treasury [OPERATIONS_TREASURY]
    ```

30. **Monitor UBC Reserve Health**
    ```
    Alert thresholds:
    - <50M tokens: Healthy (50+ months runway)
    - <20M tokens: Warning (20 months runway)
    - <10M tokens: Critical (request strategic reserve replenishment)

    Protocol giveback replenishment:
    - 40% of ecosystem org giveback → UBC fund
    - Extends runway by reducing net burn
    ```

**Step 7: Community Distribution (Quarterly)**

31. **DAO-Governed Community Allocations**
    ```
    Quarterly distribution process:

    1. DAO proposes distribution:
       - Airdrops: [AMOUNT] to active users
       - Incentives: [AMOUNT] for performance rewards
       - Grants: [AMOUNT] for ecosystem projects

    2. Community votes on proposal

    3. Multi-sig executes approved distribution:
       spl-token transfer [TOKEN_ADDRESS] [AMOUNT] [RECIPIENT] \
         --from [COMMUNITY_MULTISIG]

    4. Track distribution in public ledger
    ```

**Step 8: Year 2-3 Strategic Reserve Deployment**

32. **Validate Year 1 Success Metrics**
    ```
    Review criteria before Year 2-3 deployment:

    - consultingOrg revenue: >$300K Year 1 ✓/✗
    - techServiceOrg projects: >15 manual projects ✓/✗
    - GraphCare clients: >20 recurring clients ✓/✗
    - financeOrg retainers: >5 clients ✓/✗
    - legalOrg contracts: >10 engagements ✓/✗

    If ≥3 metrics met: Proceed with Year 2-3 deployment
    If <3 metrics met: Pause deployment, reassess strategy
    ```

33. **Execute Year 2-3 Deployments (if approved)**
    ```bash
    # securityOrg bootstrap (if condition met)
    [Multi-sig] Transfer 10,000,000 $MIND to securityOrg treasury

    # scalingOrg automation build (if techServiceOrg validates model)
    [Multi-sig] Transfer 20,000,000 $MIND to scalingOrg development

    # Strategic partnerships (if product-market fit proven)
    [Multi-sig] Transfer 30,000,000 $MIND to partnership fund

    # Team expansion (if revenue >$3M)
    [Multi-sig] Transfer 20,000,000 $MIND to team expansion

    # Liquidity expansion (if volume >$500K/day)
    [Multi-sig] Transfer 20,000,000 $MIND to liquidity fund

    Total Year 2-3 potential: 100,000,000 $MIND (conditional)
    ```

---

## Common Pitfalls

### 1. **Insufficient Gas Funds**

**Problem:** Deployment wallet runs out of SOL during token distribution

**Solution:**
- Keep ≥0.5 SOL in deployment wallet at all times
- Each token transfer costs ~0.00001 SOL (very cheap on Solana)
- Budget 0.1 SOL for 1,000 transfers as safety margin

### 2. **Wrong Token Standard**

**Problem:** Deploying as SPL Token (old) instead of SPL Token-2022

**Solution:**
- Use `--program-id TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb` flag
- Verify token contract shows Token-2022 extensions enabled
- Test transfer hooks work before mainnet deployment

### 3. **Transfer Lock Not Enforced**

**Problem:** Team/investor tokens show lock but can still transfer

**Solution:**
- Test lock on devnet first with real transfer attempts
- Verify transfer hook is set at token level, not account level
- Use `--transfer-hook-account` flag for EVERY locked transfer
- Confirm error message when attempting locked transfer

### 4. **LP Lock Platform Failure**

**Problem:** Meteora/Team Finance platform issues during LP lock

**Solution:**
- Have backup platform ready (Raydium built-in locking)
- Test LP lock process on devnet first
- Save verification transaction hash (can re-verify even if platform down)
- Consider self-custody lock contract as ultimate backup

### 5. **Multi-Sig Configuration Errors**

**Problem:** Multi-sig requires wrong number of signatures or excludes key signers

**Solution:**
- Test multi-sig with small transfer before large allocations
- Verify all signers can access and approve proposals
- Document emergency recovery process if signers unavailable
- Use reputable multi-sig platform (Squads, Realms tested on Solana)

### 6. **OTC Investment Calculation Errors**

**Problem:** Rounding errors or incorrect proportional allocation for OTC investors

**Solution:**
- Use high-precision math (avoid floating point rounding)
- Allocate all 19.8M tokens exactly (sum should equal total)
- Verify each investor's % adds up to 100% collectively
- Document calculation formula transparently

### 7. **Investor Wallet Errors**

**Problem:** Investor provides wrong wallet address or non-Solana address

**Solution:**
- Verify all addresses are valid base58 Solana addresses
- Send test transaction (1 token) before large airdrop
- Ask investors to confirm receipt before proceeding
- Keep backup contact method if wallet issues arise

### 8. **Missing Public Verification**

**Problem:** Community can't verify token allocation claims

**Solution:**
- Document all wallet addresses publicly (strategic reserve, community, etc.)
- Share LP lock verification link prominently
- Publish transaction hashes for major distributions
- Create public dashboard showing real-time reserve balance

### 9. **Strategic Reserve Premature Depletion**

**Problem:** Deploying too much too fast from strategic reserve

**Solution:**
- Stick to phased deployment plan (50M Year 1, not more)
- Require multi-sig approval for every strategic reserve transfer
- Track deployments in public ledger
- Set hard limits per phase (cannot exceed without extraordinary multi-sig vote)

### 10. **UBC Burn Rate Exceeds Projections**

**Problem:** More citizens than expected, UBC reserve depleting faster

**Solution:**
- Monitor burn rate weekly (automated alerts)
- Reduce UBC rate per citizen if reserve threatened (1,000 → 500/month)
- Request strategic reserve replenishment if <20M threshold
- Increase protocol giveback % to UBC fund (40% → 60%)

---

## Troubleshooting

### Issue: Token Transfer Fails with "Insufficient Funds"

**Symptoms:**
- `spl-token transfer` command returns error
- Transaction fails to submit
- Wallet shows sufficient token balance

**Diagnosis:**
```bash
# Check SOL balance (for gas):
solana balance

# Should show ≥0.01 SOL
# If <0.01 SOL, this is the issue
```

**Resolution:**
```bash
# Add SOL to wallet:
# Send SOL from another wallet or exchange
# Verify balance increases:
solana balance

# Retry token transfer
```

---

### Issue: Investor Cannot See Airdropped Tokens

**Symptoms:**
- Investor reports empty wallet
- Transaction shows as successful on Solscan
- Tokens not visible in Phantom

**Diagnosis:**
```bash
# Verify transaction on Solscan:
https://solscan.io/tx/[TRANSACTION_HASH]

# Check:
# - Transaction status: Success
# - Recipient address: Matches investor wallet
# - Amount: 10,000 tokens
```

**Resolution:**
```
Investor must manually add token to Phantom:

1. Open Phantom wallet
2. Click "+" or "Add Token"
3. Paste token contract address: [TOKEN_ADDRESS]
4. Click "Add"
5. Token should appear with 10,000 balance

If still not visible:
- Verify correct wallet address (investor may have multiple wallets)
- Check Solscan shows balance at that address
- Try importing wallet into Solflare (alternative wallet)
```

---

### Issue: Multi-Sig Proposal Stuck (Not Enough Signatures)

**Symptoms:**
- Multi-sig proposal created days ago
- Only 2-of-5 signatures collected
- Cannot execute transfer

**Diagnosis:**
```
Check multi-sig platform (Squads/Realms):
- How many signatures collected: 2/5
- Which signers approved: [LIST]
- Which signers haven't responded: [LIST]
```

**Resolution:**
```
1. Contact missing signers directly:
   - Email/Telegram: "Please approve multi-sig proposal #[NUMBER]"
   - Provide proposal link
   - Explain urgency if time-sensitive

2. If signer unavailable:
   - Check if emergency override process applies
   - Consider alternative proposal with available signers
   - Document reason for delay

3. Once 3+ signatures:
   - Execute proposal immediately
   - Verify transfer successful on Solscan
```

---

### Issue: LP Lock Verification Link Broken

**Symptoms:**
- Meteora/Team Finance verification link returns 404
- Community cannot verify LP lock
- Platform shows "Lock not found"

**Diagnosis:**
```bash
# Verify LP lock on-chain directly:
solana account [LP_TOKEN_ADDRESS]

# Check for lock program (should show lock contract as owner)
# Verify unlock timestamp matches 365 days
```

**Resolution:**
```
1. Find transaction hash of LP lock event:
   - Check wallet transaction history
   - Find "Lock LP Tokens" transaction
   - Copy transaction hash

2. Share on-chain verification:
   - https://solscan.io/tx/[LOCK_TRANSACTION_HASH]
   - Shows lock program address
   - Shows unlock timestamp
   - Community can verify independently

3. Contact Meteora/Team Finance support:
   - Report broken verification link
   - Provide transaction hash
   - Request link restoration

4. As backup:
   - Create own verification script
   - Query LP token owner on-chain
   - Publish script for community verification
```

---

### Issue: Transfer Restriction Not Working

**Symptoms:**
- Investor can transfer locked tokens
- Lock indicator not showing in wallet
- 6-month lock bypassed

**Diagnosis:**
```bash
# Check if transfer hook set:
spl-token display [TOKEN_ADDRESS]

# Look for:
# - Transfer Hook Program: [PROGRAM_ADDRESS]
# - Should NOT show "None"

# If shows "None": Transfer hook not set properly
```

**Resolution:**
```bash
# Set transfer hook at token level:
spl-token set-transfer-hook [TOKEN_ADDRESS] \
  --program-id [TRANSFER_HOOK_PROGRAM] \
  --lock-duration 15768000

# Verify hook now active:
spl-token display [TOKEN_ADDRESS]

# Should show Transfer Hook Program address

# Test with locked transfer:
spl-token transfer [TOKEN_ADDRESS] 1 [TEST_WALLET] \
  --transfer-hook-account [LOCK_PROGRAM]

# Should fail with "Transfer restricted" error
```

---

### Issue: OTC Token Allocation Doesn't Sum to 19.8M

**Symptoms:**
- Total allocated: 19,750,000 or 19,850,000 (not exactly 19,800,000)
- Rounding errors in calculation
- Investors notice discrepancy

**Diagnosis:**
```
Check spreadsheet calculation:
- Sum of all investor allocations: [TOTAL]
- Expected total: 19,800,000
- Difference: [TOTAL] - 19,800,000 = [DIFF]
```

**Resolution:**
```
If difference is small (<1000 tokens):

1. Identify largest investor allocation
2. Adjust their allocation by [DIFF] to make total exact
3. Document adjustment in notes
4. Communicate adjustment to that investor

Example:
- Total calculated: 19,798,500 (short by 1,500)
- Largest investor: 3,000,000 tokens
- Adjusted: 3,001,500 tokens (receives the 1,500 difference)
- New total: 19,800,000 (exact)

If difference is large (>10,000 tokens):

1. Recalculate all allocations from scratch
2. Use high-precision calculator (not Excel floating point)
3. Verify formula: (Investor EUR / Total EUR) × 19,800,000
4. Ensure no rounding until final step
```

---

### Issue: Strategic Reserve Balance Doesn't Match Public Dashboard

**Symptoms:**
- Dashboard shows 330M tokens in reserve
- On-chain balance shows different amount
- Community questions allocation

**Diagnosis:**
```bash
# Check actual on-chain balance:
spl-token balance [TOKEN_ADDRESS] --owner [STRATEGIC_MULTISIG_ADDRESS]

# Compare to dashboard display
# Identify discrepancy source
```

**Resolution:**
```
1. Audit all strategic reserve transactions:
   - Initial allocation: 380,000,000
   - Minus Year 1 deployment: -50,000,000
   - Minus any additional deployments: -[AMOUNTS]
   - Should equal current balance

2. If dashboard wrong:
   - Update dashboard with correct on-chain balance
   - Document why discrepancy occurred
   - Fix dashboard update mechanism

3. If unexpected transaction found:
   - Investigate unauthorized transfer
   - Review multi-sig approval logs
   - Verify all signers authorized transaction
   - If unauthorized: Emergency multi-sig meeting

4. Publish reconciliation report:
   - Starting balance
   - All deployments with transaction hashes
   - Current balance
   - Explanation of any discrepancies
```

---

## Examples

### Example 1: Complete Day 0 Token Deployment

**Scenario:** Launching $MIND token on Solana mainnet

**Context:**
- Deployment wallet: `DpL0y7W4...` with 1 SOL balance
- 20 investor wallet addresses collected
- Multi-sig wallets configured
- LP lock platform account ready

**Step-by-Step Execution:**

```bash
# 1. Connect to mainnet
solana config set --url https://api.mainnet-beta.solana.com

# 2. Deploy Token-2022
spl-token create-token \
  --program-id TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb \
  --enable-metadata \
  --enable-transfer-hook

# Output: Token address: MiNd1Prot0c0L...

# 3. Create token account
spl-token create-account MiNd1Prot0c0L...

# 4. Mint total supply
spl-token mint MiNd1Prot0c0L... 1000000000

# 5. Set metadata
spl-token update-metadata MiNd1Prot0c0L... \
  name "Mind Protocol" \
  symbol "MIND" \
  uri "https://mindprotocol.com/token-metadata.json"

# 6. Verify on Solscan
# Navigate to: https://solscan.io/token/MiNd1Prot0c0L...
# Verify: Total supply = 1B, Decimals = 9

# 7. Create LP on Raydium
# (via Raydium UI)
# Pair: MIND/SOL
# Deposit: 450 MIND + 0.25 SOL
# Receive: 15.XXXX LP tokens

# 8. Lock LP tokens on Meteora
# (via Meteora UI)
# Amount: 15.XXXX LP tokens (100%)
# Duration: 365 days
# Lock verification: https://app.meteora.ag/lock/[LOCK_ID]

# 9. Execute investor airdrop (10k each × 20)
for address in investor_addresses.txt; do
  spl-token transfer MiNd1Prot0c0L... 10000 $address \
    --transfer-hook-account [LOCK_PROGRAM] \
    --fund-recipient
done

# 10. Distribute to multi-sigs
spl-token transfer MiNd1Prot0c0L... 380000000 [STRATEGIC_MULTISIG]
spl-token transfer MiNd1Prot0c0L... 300000000 [COMMUNITY_MULTISIG]
spl-token transfer MiNd1Prot0c0L... 100000000 [OPERATIONS_TREASURY]

# 11. Distribute to team (with locks)
spl-token transfer MiNd1Prot0c0L... 50000000 [FOUNDER_WALLET] \
  --transfer-hook-account [LOCK_PROGRAM]

# (Repeat for all team members)

# 12. Verify total distributed
spl-token supply MiNd1Prot0c0L...
# Output: 1,000,000,000 (all tokens minted)

# 13. Public announcement
echo "Token deployed: MiNd1Prot0c0L..."
echo "LP lock: https://app.meteora.ag/lock/[LOCK_ID]"
echo "Strategic reserve: [MULTISIG_ADDRESS]"
```

**Result:**
- Total supply: 1B tokens ✓
- Initial circulating: ~180M (18%) ✓
- LP locked 12 months ✓
- Team/investor locked 6 months ✓
- Multi-sigs operational ✓

---

### Example 2: OTC Investment Processing

**Scenario:** Processing €16,000 total OTC investment from 8 investors

**Context:**
- Investment period: Day 2-7 (5 days)
- 8 investors sent SOL equivalent to €2,000 each
- Target: Distribute 19,800,000 tokens proportionally

**Investment Ledger:**

| Investor | SOL Sent | EUR Value | Timestamp | Wallet Address |
|----------|----------|-----------|-----------|----------------|
| Alice | 11.5 SOL | €2,000 | Day 2 09:00 | A1ic3W4... |
| Bob | 11.6 SOL | €2,000 | Day 2 14:00 | B0bW4LL... |
| Carol | 11.4 SOL | €2,000 | Day 3 10:00 | C4r0lW4... |
| Dave | 11.5 SOL | €2,000 | Day 4 08:00 | D4v3W4L... |
| Eve | 11.6 SOL | €2,000 | Day 5 12:00 | Ev3W4LL... |
| Frank | 11.5 SOL | €2,000 | Day 6 09:00 | Fr4nkW4... |
| Grace | 11.4 SOL | €2,000 | Day 6 15:00 | Gr4c3W4... |
| Hank | 11.5 SOL | €2,000 | Day 7 11:00 | H4nkW4L... |

**Total:** 92 SOL = €16,000

**Allocation Calculation:**

```
Total EUR raised: €16,000
Total tokens available: 19,800,000

Each investor contributed: €2,000
Each investor's %: €2,000 / €16,000 = 12.5%
Each investor's tokens: 12.5% × 19,800,000 = 2,475,000 tokens
```

**Distribution Execution (Day 7 evening):**

```bash
# Distribute to all 8 investors (equal allocation)
spl-token transfer MiNd1Prot0c0L... 2475000 A1ic3W4... \
  --transfer-hook-account [LOCK_PROGRAM]

spl-token transfer MiNd1Prot0c0L... 2475000 B0bW4LL... \
  --transfer-hook-account [LOCK_PROGRAM]

# (Repeat for Carol, Dave, Eve, Frank, Grace, Hank)

# Total distributed: 2,475,000 × 8 = 19,800,000 tokens ✓
```

**Verification:**

```
Sum of all allocations: 19,800,000 tokens ✓
All investors have 6-month lock ✓
Unlock date: [Launch Date + 182 days] ✓
```

**Result:**
- 8 investors received 2,475,000 tokens each
- All tokens from OTC pool distributed (100%)
- No tokens returned to strategic reserve
- All investors locked 6 months

---

### Example 3: Year 1 Strategic Reserve Deployment

**Scenario:** Deploying 50M tokens from strategic reserve to bootstrap ecosystem orgs

**Context:**
- Launch complete (Month 0)
- Month 1: Begin ecosystem org funding
- Strategic reserve starting balance: 380M tokens

**Multi-Sig Proposal Submissions:**

**Proposal #1: consultingOrg Bootstrap**
```
Title: consultingOrg Bootstrap Capital
Amount: 5,000,000 $MIND
Recipient: consultingOrg Multi-Sig (c0nsuLt...)
Purpose: Initial operations, consultant recruitment, brand building
Runway: 12-18 months to revenue sustainability
Submitted: Month 1, Day 5
Votes: 5-of-5 approved
Executed: Month 1, Day 7
```

**Proposal #2: techServiceOrg Bootstrap**
```
Title: techServiceOrg Bootstrap Capital
Amount: 3,000,000 $MIND
Recipient: techServiceOrg Treasury (t3chS3rv...)
Purpose: Tool development, infrastructure setup, first projects
Runway: 12 months to automation transition
Submitted: Month 1, Day 5
Votes: 5-of-5 approved
Executed: Month 1, Day 7
```

**Proposal #3: GraphCare Bootstrap**
```
Title: GraphCare Bootstrap Capital
Amount: 2,000,000 $MIND
Recipient: GraphCare Treasury (Gr4phC4r...)
Purpose: Monitoring infrastructure, specialist recruitment
Runway: 12-18 months to recurring revenue
Submitted: Month 1, Day 8
Votes: 5-of-5 approved
Executed: Month 1, Day 10
```

**Proposal #4: financeOrg Bootstrap**
```
Title: financeOrg Bootstrap Capital
Amount: 5,000,000 $MIND
Recipient: financeOrg Treasury (f1n4nc30...)
Purpose: Analyst recruitment, modeling tools, financial research
Runway: 12 months to consulting revenue
Submitted: Month 1, Day 8
Votes: 5-of-5 approved
Executed: Month 1, Day 10
```

**Proposal #5: legalOrg Bootstrap**
```
Title: legalOrg Bootstrap Capital
Amount: 5,000,000 $MIND
Recipient: legalOrg Treasury (L3g4l0rg...)
Purpose: Attorney recruitment, legal research, contract templates
Runway: 12 months to retainer revenue
Submitted: Month 1, Day 12
Votes: 5-of-5 approved
Executed: Month 1, Day 14
```

**Proposal #6: Infrastructure Development**
```
Title: Infrastructure Development Fund
Amount: 10,000,000 $MIND
Recipient: Infrastructure Multi-Sig (1nfr4str...)
Purpose: FalkorDB scaling, consciousness engine optimization, dashboard enhancement
Timeline: Month 1-12 deployment
Submitted: Month 1, Day 15
Votes: 4-of-5 approved
Executed: Month 1, Day 17
```

**Proposal #7: Team Expansion**
```
Title: Year 1 Team Expansion Fund
Amount: 10,000,000 $MIND
Recipient: Team Expansion Multi-Sig (t34mExp4...)
Purpose: Hire 3-5 additional engineers, 1 designer, 1-2 ops managers
Timeline: Month 1-12 hiring
Submitted: Month 1, Day 15
Votes: 5-of-5 approved
Executed: Month 1, Day 17
```

**Proposal #8: Emergency Reserve**
```
Title: Year 1 Emergency Reserve
Amount: 10,000,000 $MIND
Recipient: Emergency Multi-Sig (3m3rg3ncy...)
Purpose: Unexpected costs, market opportunities, legal defense
Hold: Until needed (no immediate deployment)
Submitted: Month 1, Day 20
Votes: 5-of-5 approved
Executed: Month 1, Day 22
```

**Year 1 Deployment Summary:**

```
Ecosystem Orgs:        20,000,000 $MIND
Infrastructure:        10,000,000 $MIND
Team Expansion:        10,000,000 $MIND
Emergency Reserve:     10,000,000 $MIND
-------------------------------------------
Total Year 1:          50,000,000 $MIND

Strategic Reserve Starting:  380,000,000 $MIND
Strategic Reserve After Y1:  330,000,000 $MIND (33% of supply)
```

**Public Transparency Report (Month 1, Day 25):**

```markdown
# Year 1 Strategic Reserve Deployment Report

Total deployed: 50,000,000 $MIND (13% of strategic reserve)

Ecosystem Organizations: 20M $MIND
- consultingOrg: 5M (tx: [HASH1])
- techServiceOrg: 3M (tx: [HASH2])
- GraphCare: 2M (tx: [HASH3])
- financeOrg: 5M (tx: [HASH4])
- legalOrg: 5M (tx: [HASH5])

Infrastructure: 10M $MIND (tx: [HASH6])
Team Expansion: 10M $MIND (tx: [HASH7])
Emergency Reserve: 10M $MIND (tx: [HASH8])

Remaining Strategic Reserve: 330,000,000 $MIND
Next deployment phase: Year 2-3 (conditional on success metrics)
```

**Result:**
- All Year 1 allocations deployed successfully ✓
- Ecosystem orgs funded with 12-18 month runway ✓
- Strategic reserve retains 330M tokens for future phases ✓
- Public transparency maintained ✓


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Allocation Deployment Strategy](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
