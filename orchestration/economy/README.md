# Token Economy Automation

**Automated deployment and management of $MIND token economy.**

Based on `docs/economy/MIND_TOKEN_ECONOMICS.md` specification.

---

## 🎯 What This Does

This automation handles the complete $MIND token launch sequence:

1. **Deploy SPL Token-2022** on Solana with metadata and authorities
2. **Create liquidity pool** on Raydium (0.25 SOL + 450 $MIND)
3. **Lock LP tokens** via Meteora (12 months)
4. **Distribute airdrop** to 20 investors (10k tokens each, locked 6 months)
5. **Set up governance** with 2/3 multi-sig wallet
6. **Initialize tracking** for runway, revenue, and financial health

**Single command execution:**
```bash
python -m orchestration.economy.orchestrate_launch --network devnet
```

---

## 🚀 Quick Start

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Solana wallet:**
   ```bash
   solana-keygen new  # If you don't have a wallet
   solana config set --url https://api.devnet.solana.com  # For testing
   ```

3. **Fund wallet with SOL:**
   - Devnet: Use faucet at https://faucet.solana.com
   - Mainnet: Ensure ~0.3 SOL (~$54) available

4. **Configure investor wallets:**

   Edit `orchestration/economy/config.py`:
   ```python
   class AirdropConfig:
       INVESTOR_WALLETS = [
           "wallet1_address_here",
           "wallet2_address_here",
           # ... 20 total
       ]
   ```

5. **Configure governance signers:**

   Edit `orchestration/economy/config.py`:
   ```python
   class GovernanceConfig:
       SIGNERS = [
           "founder_wallet_address",
           "advisor1_wallet_address",
           "advisor2_wallet_address"
       ]
   ```

### Test Deployment (Devnet)

```bash
# Validate configuration
python -m orchestration.economy.config

# Deploy to devnet
python -m orchestration.economy.orchestrate_launch --network devnet
```

### Production Deployment (Mainnet)

```bash
# CRITICAL: Verify everything on devnet first!

# Deploy to mainnet
python -m orchestration.economy.orchestrate_launch --network mainnet-beta

# You will be prompted to type 'LAUNCH MAINNET' to confirm
```

---

## 📚 Module Documentation

### `config.py`

**Token economy configuration constants.**

- `TokenConfig` - Token parameters (name, supply, decimals)
- `AllocationConfig` - Token allocation (30% community, 38% strategic, etc.)
- `AirdropConfig` - Investor airdrop (10k tokens × 20 investors)
- `OTCConfig` - Off-exchange investment tracking
- `LiquidityConfig` - Raydium pool parameters
- `GovernanceConfig` - Multi-sig configuration
- `BurnConfig` - Financial projections and runway
- `NetworkConfig` - Solana network settings

**Validate configuration:**
```bash
python -m orchestration.economy.config
```

### `deploy_token.py`

**Deploy SPL Token-2022 to Solana.**

Features:
- Token-2022 standard with transfer restrictions
- Rich metadata
- Retained mint/freeze authorities
- Initial emission (20% of total supply)

**Usage:**
```bash
# Dry run (no deployment)
python -m orchestration.economy.deploy_token --dry-run

# Deploy to devnet
python -m orchestration.economy.deploy_token --network devnet

# Deploy to mainnet
python -m orchestration.economy.deploy_token --network mainnet-beta
```

### `distribute_airdrop.py`

**Distribute locked tokens to investors.**

Features:
- 10,000 tokens per investor × 20 investors
- 6-month transfer lock via Token-2022
- Batch processing with error handling
- Verification mode

**Usage:**
```bash
# Distribute airdrop
python -m orchestration.economy.distribute_airdrop \
  --mint <token_mint_address> \
  --network devnet

# Verify existing distribution
python -m orchestration.economy.distribute_airdrop \
  --mint <token_mint_address> \
  --verify-only

# Dry run
python -m orchestration.economy.distribute_airdrop \
  --mint <token_mint_address> \
  --dry-run
```

### `orchestrate_launch.py`

**Main orchestration script - executes complete launch.**

Features:
- Sequential step execution
- State persistence (resume on failure)
- Automatic validation
- Comprehensive error handling

**Usage:**
```bash
# Full launch (devnet)
python -m orchestration.economy.orchestrate_launch --network devnet

# Resume from previous state
python -m orchestration.economy.orchestrate_launch \
  --network devnet \
  --resume orchestration/economy/deployments/launch_state_devnet.json

# Production launch (mainnet)
python -m orchestration.economy.orchestrate_launch --network mainnet-beta
```

---

## 🔧 Configuration Reference

### Token Parameters

```python
TOKEN_NAME = "MIND"
TOKEN_SYMBOL = "$MIND"
TOTAL_SUPPLY = 1_000_000_000  # 1 billion
INITIAL_EMISSION = 200_000_000  # 20%
```

### Allocation

| Category | Tokens | % | Lock |
|----------|--------|---|------|
| Community & Ecosystem | 300M | 30% | Flexible |
| Strategic Reserve | 380M | 38% | Flexible |
| Team & Founders | 150M | 15% | 6 months |
| Operations & UBC | 100M | 10% | Unlocked |
| Liquidity | 50M | 5% | 12 months (LP) |
| Investors | 20M | 2% | 6 months |

### Airdrop Structure

**Phase 1: Psychological Airdrop**
- 10,000 tokens × 20 investors = 200,000 tokens
- Creates $10,000 wallet display at $1.00 price
- 6-month lock

**Phase 2: OTC Investment**
- Remaining 19,800,000 tokens
- €2,000 per investor
- Proportional distribution
- 6-month lock

### Financial Projections

| Scenario | Bridge Capital | Revenue | Total | Runway |
|----------|---------------|---------|-------|--------|
| Conservative | €10,000 | €4,000 | €14,000 | 3.5 months |
| Base | €16,000 | €6,000 | €22,000 | 5.5 months |
| Optimistic | €20,000 | €12,000 | €32,000 | 8.0 months |

---

## 🛡️ Safety Features

### State Persistence

If deployment fails at any step, state is saved to:
```
orchestration/economy/deployments/launch_state_{network}.json
```

Resume with:
```bash
python -m orchestration.economy.orchestrate_launch \
  --resume orchestration/economy/deployments/launch_state_devnet.json
```

### Validation Checks

1. **Pre-deployment:**
   - Configuration consistency (allocation adds to 100%)
   - Wallet address formats
   - Sufficient SOL balance

2. **During deployment:**
   - Transaction confirmations
   - Balance verifications
   - Lock validations

3. **Post-deployment:**
   - Airdrop verification mode
   - Token balance checks
   - Lock expiry validation

### Confirmation Prompts

**Mainnet deployments require explicit confirmation:**
- Token deployment: Type `DEPLOY` to confirm
- Airdrop distribution: Type `DISTRIBUTE` to confirm
- Full launch: Type `LAUNCH MAINNET` to confirm

**Skip confirmations (dangerous):**
```bash
python -m orchestration.economy.orchestrate_launch \
  --network mainnet-beta \
  --skip-confirmations
```

---

## 📁 Directory Structure

```
orchestration/economy/
├── __init__.py                 # Module initialization
├── config.py                   # Token economy configuration
├── deploy_token.py             # Token deployment script
├── distribute_airdrop.py       # Airdrop distribution
├── orchestrate_launch.py       # Main orchestration
├── README.md                   # This file
├── deployments/                # Deployment records
│   ├── mind_token_devnet_*.json
│   ├── mind_token_mainnet_*.json
│   └── launch_state_*.json
└── distributions/              # Airdrop records
    ├── airdrop_devnet_*.json
    └── airdrop_mainnet_*.json
```

---

## 🧪 Testing Strategy

### Phase 1: Devnet Deployment

1. Deploy to devnet
2. Create test investor wallets
3. Distribute airdrop to test wallets
4. Verify locks, balances, metadata
5. Document any issues

### Phase 2: Devnet Validation

1. Test OTC investment tracking
2. Test multi-sig operations
3. Test financial tracking
4. Simulate full lifecycle

### Phase 3: Mainnet Preparation

1. Review all devnet results
2. Validate all wallet addresses
3. Verify SOL balance
4. Final configuration review
5. Team approval checkpoint

### Phase 4: Mainnet Deployment

1. Execute launch during low-traffic period
2. Monitor each step completion
3. Verify all distributions
4. Announce to investors
5. Monitor for 48 hours

---

## ⚠️ Known Limitations

### Current Implementation Status

✅ **Implemented:**
- Configuration management
- Token deployment framework
- Airdrop distribution framework
- Orchestration architecture
- State persistence
- Error handling

🚧 **TODO (Mock implementations):**
- Actual Solana RPC calls (using solana-py)
- Raydium pool creation
- Meteora LP locking integration
- Multi-sig wallet creation (Squads/Realms)
- Token-2022 transfer restrictions
- Financial tracking database

### Integration Requirements

**To complete implementation:**

1. **Solana RPC Integration:**
   - Replace mock transaction calls with real `solana-py` calls
   - Implement transaction confirmation logic
   - Add retry logic for network failures

2. **Raydium Integration:**
   - Integrate Raydium SDK for pool creation
   - Calculate optimal pool parameters
   - Handle LP token receipt

3. **Meteora Integration:**
   - Integrate Meteora locking contract
   - Handle lock duration and unlock dates
   - Verify lock creation

4. **Multi-sig Integration:**
   - Choose platform (Squads vs Realms)
   - Implement wallet creation
   - Implement token transfers to multi-sig

5. **Token-2022 Features:**
   - Implement transfer restrictions for locks
   - Set unlock dates via extensions
   - Verify lock enforcement

---

## 🆘 Troubleshooting

### "Insufficient SOL balance"

**Cause:** Wallet doesn't have enough SOL for deployment
**Fix:**
- Devnet: Use faucet at https://faucet.solana.com
- Mainnet: Transfer ~0.3 SOL to deployer wallet

### "Configuration validation failed"

**Cause:** Allocation percentages don't add to 100% or wallet counts mismatch
**Fix:**
```bash
python -m orchestration.economy.config
# Read error message
# Fix config.py
# Validate again
```

### "Wallet count mismatch"

**Cause:** `INVESTOR_WALLETS` list doesn't have 20 addresses
**Fix:** Edit `config.py` and add all 20 wallet addresses

### "State file not found"

**Cause:** Trying to resume but state file doesn't exist
**Fix:** Remove `--resume` flag to start fresh deployment

### "Network connection failed"

**Cause:** RPC endpoint unreachable
**Fix:**
- Check internet connection
- Try alternative RPC: `https://api.mainnet-beta.solana.com`
- Use private RPC (Helius, QuickNode)

---

## 📞 Support

**Documentation:** `docs/economy/MIND_TOKEN_ECONOMICS.md`

**Treasury Architect:** Lucia "Goldscale"

**Calculator says:** The math is in `config.py` - verify everything before mainnet.

**Skeptic says:** Test on devnet first. Then test again. Then verify. Then test one more time.

**Protector says:** Never deploy to mainnet without complete devnet validation.

---

## 🔐 Security Checklist

Before mainnet deployment:

- [ ] All wallet addresses verified (investors + governance)
- [ ] Configuration validated (`python -m orchestration.economy.config`)
- [ ] Devnet deployment successful
- [ ] Airdrop distribution tested
- [ ] Lock mechanisms verified
- [ ] Multi-sig signers confirmed
- [ ] Team approval obtained
- [ ] Backup keypairs secured
- [ ] Recovery plan documented
- [ ] Post-deployment monitoring ready

---

**Built by:** Lucia "Goldscale", Treasury Architect
**Status:** Framework complete, awaiting Solana integration
**Last Updated:** 2025-10-27
