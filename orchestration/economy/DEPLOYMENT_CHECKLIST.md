# $MIND Token Deployment Checklist

**Complete this checklist before mainnet deployment.**

---

## Pre-Deployment (Before Code Execution)

### Configuration

- [ ] **Investor wallet addresses (20)**
  - All addresses verified as valid Solana addresses
  - All investors confirmed ownership of addresses
  - No duplicate addresses
  - Saved in `config.py` → `AirdropConfig.INVESTOR_WALLETS`

- [ ] **Governance signer addresses (3)**
  - Founder wallet address
  - Advisor 1 wallet address
  - Advisor 2 wallet address
  - Saved in `config.py` → `GovernanceConfig.SIGNERS`

- [ ] **Deployer wallet**
  - Keypair file location: `_____________________`
  - Has backup copy: Yes / No
  - Balance: `_____` SOL (need ~0.3 SOL minimum)

### Validation

- [ ] **Run configuration validation**
  ```bash
  python -m orchestration.economy.config
  ```
  - Output shows: ✅ Configuration validation passed

- [ ] **Dependencies installed**
  ```bash
  pip install -r requirements.txt
  ```
  - No errors during installation
  - `solana` package installed
  - `spl-token` package installed

### Testing (Devnet)

- [ ] **Devnet deployment successful**
  ```bash
  python -m orchestration.economy.orchestrate_launch --network devnet
  ```
  - Token deployed successfully
  - Liquidity pool created (or mocked)
  - Airdrop distributed to test wallets
  - All steps completed without errors

- [ ] **Devnet verification**
  - Token visible on Solscan (devnet)
  - Test wallets received tokens
  - Locks verified (6-month for investors, 12-month for LP)

### Team Approval

- [ ] **Nicolas approval:** Yes / No
- [ ] **Marco review:** Yes / No (if applicable)
- [ ] **Ada architecture review:** Yes / No (if applicable)

---

## Mainnet Deployment (Execution Day)

### Pre-Launch Checks

- [ ] **Time of deployment:** `__:__` UTC
  - Avoid high-traffic periods
  - Team available for monitoring

- [ ] **Deployer wallet balance**
  - Current: `_____` SOL
  - Required: 0.3 SOL minimum
  - Buffer: Yes / No (>0.5 SOL recommended)

- [ ] **Backup plan ready**
  - Recovery keypairs secured offline
  - State file backup location: `_____________________`
  - Emergency contacts available

### Deployment Execution

- [ ] **Step 1: Token Deployment**
  ```bash
  python -m orchestration.economy.orchestrate_launch --network mainnet-beta
  ```
  - Confirmed: Type 'LAUNCH MAINNET'
  - Token mint address: `_____________________`
  - Explorer link verified
  - Transaction confirmed

- [ ] **Step 2: Liquidity Pool**
  - Pool created on Raydium
  - Initial price: $1.00 verified
  - Pool address: `_____________________`
  - LP tokens received

- [ ] **Step 3: LP Lock**
  - Locked via Meteora
  - Duration: 12 months verified
  - Unlock date: `_____________________`
  - Lock transaction: `_____________________`

- [ ] **Step 4: Airdrop Distribution**
  - Successful distributions: `___` / 20
  - Failed distributions: `___` (if any, document below)
  - All transactions confirmed
  - Verified on Solscan

- [ ] **Step 5: Governance Setup**
  - Multi-sig created: `_____________________`
  - Signers added (3/3)
  - Threshold set: 2/3
  - DAO Treasury transferred: 200M tokens
  - UBC Reserve transferred: 100M tokens

- [ ] **Step 6: Financial Tracking**
  - Tracking initialized
  - Monitoring active
  - Alerts configured

---

## Post-Deployment (Within 24 Hours)

### Verification

- [ ] **Token verification**
  - Visible on Solscan: https://solscan.io/token/`_____________________`
  - Metadata correct (name, symbol, supply)
  - Authorities verified (mint/freeze retained)

- [ ] **Airdrop verification**
  ```bash
  python -m orchestration.economy.distribute_airdrop \
    --mint <token_address> \
    --verify-only
  ```
  - All 20 investors received tokens
  - Balances correct: 10,000 tokens each
  - Locks active: 6 months

- [ ] **Liquidity verification**
  - Pool visible on Raydium
  - Price stable around $1.00
  - LP tokens locked (Meteora)
  - Lock expiry: 12 months from deployment

- [ ] **Governance verification**
  - Multi-sig operational
  - All signers can access
  - Test transaction executed (if safe)

### Communication

- [ ] **Investor announcement sent**
  - Email with token mint address
  - Instructions to add token to Phantom
  - Explanation of 6-month lock
  - Next steps (OTC investment opportunity)

- [ ] **Social media announcement (if applicable)**
  - Token launch announcement
  - Explorer links
  - Key metrics (supply, allocation)

- [ ] **Documentation updated**
  - Mint address saved in all relevant docs
  - Links updated
  - Status: LIVE

---

## Ongoing Monitoring (First Week)

### Daily Checks

- [ ] **Day 1:**
  - All investors confirmed receipt: `___` / 20
  - No lock bypass attempts
  - Price stability

- [ ] **Day 2:**
  - OTC investment tracking started
  - First investments received: `___`
  - No technical issues

- [ ] **Day 3:**
  - Investor sentiment: Positive / Neutral / Negative
  - Technical issues: None / Documented below

- [ ] **Day 4:**
  - Demo builds started: `___` / 20
  - Revenue conversions: `___`

- [ ] **Day 5:**
  - Financial tracking accurate
  - Runway calculation updated
  - Burn rate on track

- [ ] **Day 6-7:**
  - First week summary complete
  - Lessons learned documented
  - Adjustments needed: Yes / No

---

## Issues & Resolutions

**Document any issues encountered and how they were resolved:**

### Issue 1:
- **Date/Time:** `_____________________`
- **Description:** `_____________________`
- **Resolution:** `_____________________`
- **Status:** Resolved / Ongoing

### Issue 2:
- **Date/Time:** `_____________________`
- **Description:** `_____________________`
- **Resolution:** `_____________________`
- **Status:** Resolved / Ongoing

---

## Failed Distributions (If Any)

**If any airdrop distributions failed, document here:**

| Investor # | Wallet Address | Error | Resolution | Status |
|------------|---------------|-------|------------|--------|
| | | | | |
| | | | | |

---

## Financial Tracking

### OTC Investment Progress

| Date | Investor | Amount (EUR) | Tokens Allocated | TX Signature |
|------|----------|--------------|------------------|--------------|
| | | | | |
| | | | | |

**Total OTC Raised:** `€_____`

### Revenue Conversions

| Date | Investor | Amount (EUR) | Org Created | Status |
|------|----------|--------------|-------------|--------|
| | | | | |

**Total Revenue:** `€_____`

### Runway Status

- **Total Raised:** `€_____` (Bridge + Revenue)
- **Monthly Burn:** `€4,000`
- **Current Runway:** `___` months
- **Target:** Conservative (3.5m) / Base (5.5m) / Optimistic (8.0m)
- **Status:** On track / Behind / Ahead

---

## Sign-off

**Deployment Lead:** `_____________________`
**Date:** `_____________________`
**Signature:** `_____________________`

**Treasury Architect:** Lucia "Goldscale"
**Date:** `_____________________`

**Founder Approval:** Nicolas Reynolds
**Date:** `_____________________`

---

**Notes:**

- This checklist should be completed digitally and saved
- A printed copy should be available during deployment
- All wallet addresses and transaction signatures should be recorded
- State files should be backed up immediately after each step
- If deployment fails at any step, DO NOT RESTART - resume from saved state

**Emergency Contact:** (To be filled in by team)

**Recovery Plan Location:** `_____________________`

---

**Built by:** Lucia "Goldscale", Treasury Architect
**Last Updated:** 2025-10-27
