#!/bin/bash

# Create Raydium Liquidity Pool for $MIND Token
# Using Raydium CPMM (Constant Product Market Maker)

set -e

echo "========================================================================"
echo "💧 CREATE RAYDIUM LIQUIDITY POOL"
echo "========================================================================"
echo ""

TOKEN_MINT="MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR"
DEPLOYER=$(solana address)

echo "Token Mint: $TOKEN_MINT"
echo "Deployer: $DEPLOYER"
echo ""

# Check current balances
echo "========================================================================"
echo "Current Balances"
echo "========================================================================"
echo ""

SOL_BALANCE=$(solana balance | awk '{print $1}')
echo "SOL Balance: $SOL_BALANCE SOL"

MIND_BALANCE=$(spl-token balance $TOKEN_MINT 2>/dev/null || echo "0")
echo "MIND Balance: $MIND_BALANCE tokens"
echo ""

# Get current SOL price
echo "Fetching current SOL price..."
SOL_PRICE=$(curl -s "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd" | grep -o '"usd":[0-9.]*' | grep -o '[0-9.]*')
echo "Current SOL Price: \$$SOL_PRICE USD"
echo ""

# Calculate LP parameters
echo "========================================================================"
echo "LP Parameter Options"
echo "========================================================================"
echo ""

echo "Option A: Minimal LP at \$1.00 initial price"
MIND_NEEDED_A=$(echo "scale=2; (0.25 * $SOL_PRICE) / 1.0" | bc)
echo "  - SOL: 0.25 SOL (\$$(echo "scale=2; 0.25 * $SOL_PRICE" | bc))"
echo "  - MIND: $MIND_NEEDED_A tokens"
echo "  - Initial Price: \$1.00 per MIND"
echo ""

echo "Option B: From tokenomics spec (\$0.11 price)"
echo "  - SOL: 0.25 SOL (\$$(echo "scale=2; 0.25 * $SOL_PRICE" | bc))"
echo "  - MIND: 450 tokens"
PRICE_B=$(echo "scale=4; (0.25 * $SOL_PRICE) / 450" | bc)
echo "  - Initial Price: \$$PRICE_B per MIND"
echo ""

echo "Option C: Deeper LP at \$1.00 price"
MIND_NEEDED_C=$(echo "scale=2; (1.0 * $SOL_PRICE) / 1.0" | bc)
echo "  - SOL: 1.0 SOL (\$$(echo "scale=2; 1.0 * $SOL_PRICE" | bc))"
echo "  - MIND: $MIND_NEEDED_C tokens"
echo "  - Initial Price: \$1.00 per MIND"
echo ""

read -p "Choose option (A/B/C): " OPTION

case $OPTION in
    A|a)
        SOL_AMOUNT="0.25"
        MIND_AMOUNT=$(echo "scale=0; (0.25 * $SOL_PRICE) / 1.0" | bc)
        ;;
    B|b)
        SOL_AMOUNT="0.25"
        MIND_AMOUNT="450"
        ;;
    C|c)
        SOL_AMOUNT="1.0"
        MIND_AMOUNT=$(echo "scale=0; (1.0 * $SOL_PRICE) / 1.0" | bc)
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

INITIAL_PRICE=$(echo "scale=4; ($SOL_AMOUNT * $SOL_PRICE) / $MIND_AMOUNT" | bc)

echo ""
echo "========================================================================"
echo "SELECTED LP PARAMETERS"
echo "========================================================================"
echo ""
echo "SOL Amount: $SOL_AMOUNT SOL"
echo "MIND Amount: $MIND_AMOUNT tokens"
echo "Initial Price: \$$INITIAL_PRICE per MIND"
echo ""

read -p "Proceed with pool creation? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

echo ""
echo "========================================================================"
echo "CREATING RAYDIUM POOL"
echo "========================================================================"
echo ""

echo "⚠️  MANUAL STEP REQUIRED"
echo ""
echo "Raydium pool creation is done through their web interface:"
echo ""
echo "1. Go to: https://raydium.io/liquidity/create/"
echo ""
echo "2. Connect your wallet (deployer wallet)"
echo "   Address: $DEPLOYER"
echo ""
echo "3. Select pool type: CPMM (Constant Product)"
echo ""
echo "4. Enter token mint address:"
echo "   $TOKEN_MINT"
echo ""
echo "5. Configure initial liquidity:"
echo "   - SOL: $SOL_AMOUNT"
echo "   - MIND: $MIND_AMOUNT"
echo ""
echo "6. Confirm transaction"
echo ""
echo "7. Save the LP token mint address (you'll need it for locking)"
echo ""

echo "========================================================================"
echo "AFTER POOL CREATION"
echo "========================================================================"
echo ""
echo "✅ Your pool will appear on:"
echo "   - Raydium: https://raydium.io/liquidity/pools/"
echo "   - DexScreener: https://dexscreener.com/solana/$TOKEN_MINT"
echo "   - Birdeye: https://birdeye.so/token/$TOKEN_MINT"
echo ""
echo "✅ You will receive LP tokens representing your position"
echo ""
echo "⚠️  NEXT CRITICAL STEP: Lock LP tokens for 12 months"
echo "   Run: ./lock_lp_tokens.sh"
echo ""
echo "⚠️  DO NOT distribute airdrop until LP is locked!"
echo ""

echo "Press Enter when you've completed pool creation..."
read

echo ""
echo "Did you successfully create the pool? (yes/no): "
read POOL_CREATED

if [ "$POOL_CREATED" = "yes" ]; then
    echo ""
    read -p "Paste the LP token mint address: " LP_MINT
    read -p "Paste the pool address: " POOL_ADDRESS

    # Save pool info
    cat > ~/mind_lp_info.json << EOF
{
  "token_mint": "$TOKEN_MINT",
  "pool_address": "$POOL_ADDRESS",
  "lp_token_mint": "$LP_MINT",
  "sol_amount": $SOL_AMOUNT,
  "mind_amount": $MIND_AMOUNT,
  "initial_price_usd": $INITIAL_PRICE,
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deployer": "$DEPLOYER"
}
EOF

    echo ""
    echo "✅ Pool info saved to: ~/mind_lp_info.json"
    echo ""
    echo "🔒 NEXT STEP: Lock LP tokens"
    echo "   ./lock_lp_tokens.sh"
fi

echo ""
echo "========================================================================"
echo "✅ COMPLETE"
echo "========================================================================"
