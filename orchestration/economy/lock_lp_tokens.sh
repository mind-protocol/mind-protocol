#!/bin/bash

# Lock LP Tokens for 12 Months
# Prevents rug pull concerns, proves commitment

set -e

echo "========================================================================"
echo "🔒 LOCK LP TOKENS (12 MONTHS)"
echo "========================================================================"
echo ""

# Load pool info if available
if [ -f ~/mind_lp_info.json ]; then
    echo "✅ Found pool info from previous step"
    cat ~/mind_lp_info.json
    echo ""

    LP_MINT=$(cat ~/mind_lp_info.json | grep lp_token_mint | cut -d'"' -f4)
    POOL_ADDRESS=$(cat ~/mind_lp_info.json | grep pool_address | cut -d'"' -f4)
else
    echo "⚠️  No pool info found. Continuing manually..."
    echo ""
    read -p "Enter LP token mint address: " LP_MINT
    read -p "Enter pool address: " POOL_ADDRESS
fi

DEPLOYER=$(solana address)

echo "Deployer: $DEPLOYER"
echo "LP Token Mint: $LP_MINT"
echo "Pool Address: $POOL_ADDRESS"
echo ""

# Check LP token balance
echo "Checking LP token balance..."
LP_BALANCE=$(spl-token balance $LP_MINT 2>/dev/null || echo "0")
echo "LP Token Balance: $LP_BALANCE"
echo ""

if [ "$LP_BALANCE" = "0" ]; then
    echo "❌ No LP tokens found!"
    echo "   Make sure you created the pool first."
    exit 1
fi

echo "========================================================================"
echo "LOCK CONFIGURATION"
echo "========================================================================"
echo ""

LOCK_DURATION_DAYS=365
LOCK_END_DATE=$(date -d "+$LOCK_DURATION_DAYS days" +%Y-%m-%d 2>/dev/null || date -v+${LOCK_DURATION_DAYS}d +%Y-%m-%d)

echo "Lock Duration: $LOCK_DURATION_DAYS days (12 months)"
echo "Lock End Date: $LOCK_END_DATE"
echo "LP Tokens to Lock: $LP_BALANCE"
echo ""

echo "⚠️  WARNING: Locked LP tokens CANNOT be withdrawn until lock expires"
echo "⚠️  This is ESSENTIAL for investor trust"
echo ""

read -p "Proceed with locking? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

echo ""
echo "========================================================================"
echo "LOCKING LP TOKENS"
echo "========================================================================"
echo ""

echo "⚠️  MANUAL STEP REQUIRED"
echo ""
echo "LP token locking is done through Meteora or Streamflow:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "OPTION 1: Meteora Locks (Recommended)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Go to: https://app.meteora.ag/lock"
echo ""
echo "2. Connect your wallet"
echo "   Address: $DEPLOYER"
echo ""
echo "3. Click 'Create New Lock'"
echo ""
echo "4. Enter lock details:"
echo "   - Token Mint: $LP_MINT"
echo "   - Amount: $LP_BALANCE (all LP tokens)"
echo "   - Duration: 12 months ($LOCK_END_DATE)"
echo "   - Recipient: $DEPLOYER (yourself)"
echo ""
echo "5. Confirm transaction"
echo ""
echo "6. Save the lock address"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "OPTION 2: Streamflow Finance"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Go to: https://app.streamflow.finance/token-lock"
echo ""
echo "2. Connect wallet: $DEPLOYER"
echo ""
echo "3. Create token lock:"
echo "   - Token: $LP_MINT"
echo "   - Amount: $LP_BALANCE"
echo "   - Release Date: $LOCK_END_DATE"
echo ""
echo "4. Confirm and save lock contract address"
echo ""

echo "Press Enter when you've completed LP locking..."
read

echo ""
read -p "Did you successfully lock the LP tokens? (yes/no): " LOCKED

if [ "$LOCKED" = "yes" ]; then
    echo ""
    read -p "Paste the lock contract address: " LOCK_ADDRESS

    # Update pool info with lock details
    if [ -f ~/mind_lp_info.json ]; then
        # Create updated JSON with lock info
        cat ~/mind_lp_info.json | \
        sed "s/}$/,/" | \
        cat - << EOF > ~/mind_lp_info.json.tmp
  "lp_lock_address": "$LOCK_ADDRESS",
  "lock_duration_days": $LOCK_DURATION_DAYS,
  "lock_end_date": "$LOCK_END_DATE",
  "locked_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
        mv ~/mind_lp_info.json.tmp ~/mind_lp_info.json

        echo ""
        echo "✅ Lock info saved to: ~/mind_lp_info.json"
    fi

    echo ""
    echo "========================================================================"
    echo "✅ LP TOKENS LOCKED SUCCESSFULLY"
    echo "========================================================================"
    echo ""
    echo "🔒 Lock Details:"
    echo "   - LP Tokens: $LP_BALANCE"
    echo "   - Duration: 12 months"
    echo "   - Unlock Date: $LOCK_END_DATE"
    echo "   - Lock Contract: $LOCK_ADDRESS"
    echo ""
    echo "✅ You can now safely:"
    echo "   - Distribute airdrop to investors"
    echo "   - Announce token launch"
    echo "   - Share pool on social media"
    echo ""
    echo "🔗 Verification Links:"
    echo "   - Raydium Pool: https://raydium.io/liquidity/pools/"
    echo "   - DexScreener: https://dexscreener.com/solana/MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR"
    echo "   - Lock Contract: Explorer link for $LOCK_ADDRESS"
    echo ""
    echo "📊 Next Steps:"
    echo "   - Phase C: Distribute airdrop (./distribute_airdrop.sh)"
    echo "   - Phase D: Set up multi-sig governance"
    echo ""
else
    echo ""
    echo "⚠️  LP tokens NOT locked yet"
    echo "   DO NOT proceed with airdrop until LP is locked!"
fi

echo ""
echo "========================================================================"
echo "✅ COMPLETE"
echo "========================================================================"
