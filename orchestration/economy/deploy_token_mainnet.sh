#!/bin/bash

# $MIND Token Deployment Script
# Deploys SPL token to Solana mainnet

set -e  # Exit on any error

echo "========================================================================"
echo "🚀 DEPLOYING \$MIND TOKEN TO MAINNET"
echo "========================================================================"

# Configuration
TOKEN_NAME="MIND"
TOKEN_SYMBOL="\$MIND"
DECIMALS=9
INITIAL_SUPPLY=200000000  # 200 million tokens

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "📋 Token Configuration:"
echo "   Name: $TOKEN_NAME"
echo "   Symbol: $TOKEN_SYMBOL"
echo "   Decimals: $DECIMALS"
echo "   Initial Supply: $INITIAL_SUPPLY tokens"

# Verify we're on mainnet
echo ""
echo "🔍 Verifying network configuration..."
CURRENT_URL=$(solana config get | grep "RPC URL" | awk '{print $3}')
echo "   Current RPC: $CURRENT_URL"

if [[ ! "$CURRENT_URL" =~ "mainnet" ]]; then
    echo -e "${RED}❌ ERROR: Not configured for mainnet!${NC}"
    echo "   Run: solana config set --url mainnet-beta"
    exit 1
fi

# Check balance
echo ""
echo "💰 Checking wallet balance..."
DEPLOYER=$(solana address)
BALANCE=$(solana balance | awk '{print $1}')
echo "   Deployer: $DEPLOYER"
echo "   Balance: $BALANCE SOL"

if (( $(echo "$BALANCE < 0.02" | bc -l) )); then
    echo -e "${RED}❌ ERROR: Insufficient balance (need at least 0.02 SOL)${NC}"
    exit 1
fi

# Confirmation
echo ""
echo -e "${YELLOW}⚠️  WARNING: MAINNET DEPLOYMENT${NC}"
echo -e "${YELLOW}   This will use REAL SOL and create a REAL token${NC}"
echo ""
read -p "Type 'DEPLOY' to confirm: " CONFIRM

if [ "$CONFIRM" != "DEPLOY" ]; then
    echo -e "${RED}❌ Deployment cancelled${NC}"
    exit 0
fi

# Step 1: Create token mint
echo ""
echo "========================================================================"
echo "STEP 1: Creating Token Mint"
echo "========================================================================"

MINT_KEYPAIR="/tmp/mind_token_mint.json"
solana-keygen new --no-bip39-passphrase --silent --outfile "$MINT_KEYPAIR"

echo "Creating token with $DECIMALS decimals..."
TOKEN_MINT=$(spl-token create-token --decimals $DECIMALS "$MINT_KEYPAIR" 2>&1 | grep "Creating token" | awk '{print $3}')

if [ -z "$TOKEN_MINT" ]; then
    echo -e "${RED}❌ Failed to create token mint${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Token mint created: $TOKEN_MINT${NC}"

# Step 2: Create token account
echo ""
echo "========================================================================"
echo "STEP 2: Creating Token Account"
echo "========================================================================"

echo "Creating token account for deployer..."
TOKEN_ACCOUNT=$(spl-token create-account $TOKEN_MINT 2>&1 | grep "Creating account" | awk '{print $3}')

if [ -z "$TOKEN_ACCOUNT" ]; then
    echo -e "${RED}❌ Failed to create token account${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Token account created: $TOKEN_ACCOUNT${NC}"

# Step 3: Mint initial supply
echo ""
echo "========================================================================"
echo "STEP 3: Minting Initial Supply"
echo "========================================================================"

echo "Minting $INITIAL_SUPPLY tokens..."
spl-token mint $TOKEN_MINT $INITIAL_SUPPLY $TOKEN_ACCOUNT

# Verify balance
BALANCE=$(spl-token balance $TOKEN_MINT)
echo -e "${GREEN}✅ Minted $BALANCE tokens${NC}"

# Step 4: Save deployment info
echo ""
echo "========================================================================"
echo "STEP 4: Saving Deployment Info"
echo "========================================================================"

DEPLOYMENT_FILE="$HOME/mind_token_deployment_$(date +%Y%m%d_%H%M%S).json"

cat > "$DEPLOYMENT_FILE" << EOF
{
  "token_name": "$TOKEN_NAME",
  "token_symbol": "$TOKEN_SYMBOL",
  "network": "mainnet-beta",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deployer": "$DEPLOYER",
  "token_mint": "$TOKEN_MINT",
  "token_account": "$TOKEN_ACCOUNT",
  "decimals": $DECIMALS,
  "initial_supply": $INITIAL_SUPPLY,
  "total_supply": 1000000000,
  "initial_emission_percent": 20
}
EOF

echo -e "${GREEN}✅ Deployment info saved: $DEPLOYMENT_FILE${NC}"

# Final summary
echo ""
echo "========================================================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================================================================"
echo ""
echo "📍 Token Mint Address:"
echo "   $TOKEN_MINT"
echo ""
echo "💼 Your Token Account:"
echo "   $TOKEN_ACCOUNT"
echo ""
echo "💎 Initial Supply:"
echo "   $BALANCE tokens"
echo ""
echo "🔗 Solana Explorer:"
echo "   https://solscan.io/token/$TOKEN_MINT"
echo ""
echo "📄 Deployment Details:"
echo "   $DEPLOYMENT_FILE"
echo ""
echo "========================================================================"
echo "NEXT STEPS:"
echo "========================================================================"
echo ""
echo "✅ Token is live on Solana mainnet"
echo "✅ You hold all $BALANCE tokens"
echo ""
echo "Later (when ready):"
echo "  • Create liquidity pool on Raydium"
echo "  • Distribute airdrop to investors"
echo "  • Set up multi-sig governance"
echo ""
echo "⚠️  SAVE THIS ADDRESS: $TOKEN_MINT"
echo "⚠️  BACKUP MINT KEYPAIR: $MINT_KEYPAIR"
echo ""
