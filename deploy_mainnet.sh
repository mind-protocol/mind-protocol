#!/bin/bash
# ==================================================
# $MIND Token — Mainnet Deployment Script
# ==================================================
# This script deploys the full $MIND token infrastructure:
# 1. TransferHook program (Anchor/Rust)
# 2. $MIND Token (SPL Token 2022 with extensions)
# 3. Initial mint
#
# Usage:
#   ./deploy_mainnet.sh --dry-run     # Preview only
#   ./deploy_mainnet.sh --live        # Execute (requires confirmation)
#
# Prerequisites:
#   - ~2.5 SOL in deployer wallet
#   - Anchor CLI 0.30+
#   - Node.js 18+
#   - Solana CLI 4.0+
# ==================================================

set -e

NETWORK="mainnet-beta"
RPC_URL="https://api.mainnet-beta.solana.com"
KEYPAIR="$HOME/.config/solana/id.json"
PROGRAM_BINARY="target/deploy/mind_transfer_hook.so"
PROGRAM_KEYPAIR="target/deploy/mind_transfer_hook-keypair.json"
INITIAL_MINT_AMOUNT=1000000  # 1M $MIND (total supply per whitepaper)
DRY_RUN=true

# Parse args
for arg in "$@"; do
  case $arg in
    --live) DRY_RUN=false ;;
    --dry-run) DRY_RUN=true ;;
    --amount=*) INITIAL_MINT_AMOUNT="${arg#*=}" ;;
  esac
done

echo "=================================================="
echo "  \$MIND Token — Mainnet Deployment"
echo "=================================================="
echo "  Network:     $NETWORK"
echo "  RPC:         $RPC_URL"
echo "  Dry Run:     $DRY_RUN"
echo "  Mint Amount: $INITIAL_MINT_AMOUNT"
echo "=================================================="
echo ""

# --------------------------------------------------
# STEP 0: Preflight checks
# --------------------------------------------------
echo "[STEP 0] Preflight checks..."

WALLET=$(solana address -k "$KEYPAIR" 2>/dev/null)
echo "  Deployer wallet: $WALLET"

BALANCE=$(solana balance "$WALLET" --url "$RPC_URL" 2>/dev/null | awk '{print $1}')
echo "  SOL balance: $BALANCE SOL"

# Check minimum balance
MIN_SOL="2.0"
if (( $(echo "$BALANCE < $MIN_SOL" | bc -l 2>/dev/null || echo 1) )); then
  echo "  ⚠️  WARNING: Balance ($BALANCE SOL) may be insufficient (need ~$MIN_SOL SOL)"
  if [ "$DRY_RUN" = false ]; then
    echo "  Aborting. Send more SOL to $WALLET"
    exit 1
  fi
fi

echo "  Solana CLI: $(solana --version 2>&1 | head -1)"
echo "  Anchor CLI: $(anchor --version 2>&1)"
echo "  Node.js: $(node --version 2>&1)"
echo "  SPL Token: $(spl-token --version 2>&1)"
echo "  Program binary: $(ls -la $PROGRAM_BINARY 2>/dev/null | awk '{print $5}') bytes"
echo ""

# --------------------------------------------------
# STEP 1: Deploy TransferHook program to mainnet
# --------------------------------------------------
echo "[STEP 1] Deploy TransferHook program..."

# Check if already deployed on mainnet
HOOK_CHECK=$(solana program show "$(solana address -k $PROGRAM_KEYPAIR 2>/dev/null)" --url "$RPC_URL" 2>&1 || echo "NOT_FOUND")

if echo "$HOOK_CHECK" | grep -q "Program Id:"; then
  HOOK_PROGRAM_ID=$(echo "$HOOK_CHECK" | grep "Program Id:" | awk '{print $3}')
  echo "  ✅ TransferHook already deployed: $HOOK_PROGRAM_ID"
else
  HOOK_PROGRAM_ID=$(solana address -k "$PROGRAM_KEYPAIR" 2>/dev/null)
  echo "  TransferHook will deploy as: $HOOK_PROGRAM_ID"

  if [ "$DRY_RUN" = true ]; then
    echo "  DRY RUN: Would run: solana program deploy $PROGRAM_BINARY --url $RPC_URL --keypair $KEYPAIR --program-id $PROGRAM_KEYPAIR"
  else
    echo "  ⚠️  DEPLOYING TransferHook to MAINNET..."
    echo "  Press Enter to confirm or Ctrl+C to abort"
    read -r

    solana program deploy "$PROGRAM_BINARY" \
      --url "$RPC_URL" \
      --keypair "$KEYPAIR" \
      --program-id "$PROGRAM_KEYPAIR" \
      --with-compute-unit-price 1000

    echo "  ✅ TransferHook deployed: $HOOK_PROGRAM_ID"
  fi
fi

echo ""

# --------------------------------------------------
# STEP 2: Install npm dependencies for token creation
# --------------------------------------------------
echo "[STEP 2] Setup npm dependencies..."

if [ ! -d "node_modules/@solana/web3.js" ]; then
  echo "  Installing @solana/web3.js, @solana/spl-token, typescript..."

  if [ "$DRY_RUN" = true ]; then
    echo "  DRY RUN: Would run: npm init -y && npm install @solana/web3.js @solana/spl-token @solana/spl-token-metadata typescript ts-node"
  else
    npm init -y 2>/dev/null || true
    npm install @solana/web3.js @solana/spl-token @solana/spl-token-metadata typescript ts-node
  fi
else
  echo "  ✅ npm dependencies already installed"
fi

echo ""

# --------------------------------------------------
# STEP 3: Create $MIND token with all extensions
# --------------------------------------------------
echo "[STEP 3] Create \$MIND Token (SPL Token 2022)..."
echo "  Extensions: TransferFeeConfig, TransferHook, MetadataPointer, TokenMetadata, MintCloseAuthority"
echo "  Freeze Authority: null (censorship resistant)"
echo "  Transfer Fee: 1% (100 basis points)"
echo "  TransferHook Program: $HOOK_PROGRAM_ID"

if [ "$DRY_RUN" = true ]; then
  echo "  DRY RUN: Would generate and execute TypeScript token creation"
  echo "  DRY RUN: Token address would be generated at creation time"
else
  echo ""
  echo "  ⚠️  CREATING \$MIND TOKEN ON MAINNET (IRREVERSIBLE)"
  echo "  Extensions are permanent and cannot be changed after creation."
  echo "  Press Enter to confirm or Ctrl+C to abort"
  read -r

  # Generate TypeScript and execute
  python3 economy/token/spl_token_2022_mint_creator.py --mainnet 2>/dev/null || true

  # If TypeScript was generated, run it
  if [ -f "create_mind_token.ts" ]; then
    npx ts-node create_mind_token.ts

    # Read the output
    if [ -f "mind_token_mint.json" ]; then
      MINT_ADDRESS=$(python3 -c "import json; print(json.load(open('mind_token_mint.json'))['mint'])")
      echo "  ✅ Token created: $MINT_ADDRESS"
    fi
  fi
fi

echo ""

# --------------------------------------------------
# STEP 4: Mint initial supply
# --------------------------------------------------
echo "[STEP 4] Mint initial supply ($INITIAL_MINT_AMOUNT \$MIND)..."

if [ "$DRY_RUN" = true ]; then
  echo "  DRY RUN: Would mint $INITIAL_MINT_AMOUNT tokens to deployer wallet"
  echo "  DRY RUN: spl-token mint <MINT_ADDRESS> $INITIAL_MINT_AMOUNT --url $RPC_URL"
else
  if [ -n "$MINT_ADDRESS" ]; then
    echo "  Minting $INITIAL_MINT_AMOUNT \$MIND to $WALLET..."

    # Create token account
    spl-token create-account "$MINT_ADDRESS" \
      --url "$RPC_URL" \
      --fee-payer "$KEYPAIR" \
      --program-id TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb 2>/dev/null || true

    # Mint
    spl-token mint "$MINT_ADDRESS" "$INITIAL_MINT_AMOUNT" \
      --url "$RPC_URL" \
      --fee-payer "$KEYPAIR" \
      --program-id TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb

    echo "  ✅ Minted $INITIAL_MINT_AMOUNT \$MIND"
  else
    echo "  ❌ No mint address — skipping"
  fi
fi

echo ""

# --------------------------------------------------
# STEP 5: Save deployment info
# --------------------------------------------------
echo "[STEP 5] Saving deployment info..."

DEPLOY_FILE="deploy_output/deployment_mainnet.json"
mkdir -p deploy_output

if [ "$DRY_RUN" = true ]; then
  cat > "$DEPLOY_FILE" << EOF
{
  "network": "$NETWORK",
  "dry_run": true,
  "deployer_wallet": "$WALLET",
  "transfer_hook_program": "$HOOK_PROGRAM_ID",
  "token_mint": "PENDING_DEPLOYMENT",
  "initial_supply": $INITIAL_MINT_AMOUNT,
  "extensions": [
    "TransferFeeConfig (1%)",
    "TransferHook",
    "MetadataPointer",
    "TokenMetadata",
    "MintCloseAuthority"
  ],
  "freeze_authority": null,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
else
  cat > "$DEPLOY_FILE" << EOF
{
  "network": "$NETWORK",
  "dry_run": false,
  "deployer_wallet": "$WALLET",
  "transfer_hook_program": "$HOOK_PROGRAM_ID",
  "token_mint": "${MINT_ADDRESS:-UNKNOWN}",
  "initial_supply": $INITIAL_MINT_AMOUNT,
  "extensions": [
    "TransferFeeConfig (1%)",
    "TransferHook",
    "MetadataPointer",
    "TokenMetadata",
    "MintCloseAuthority"
  ],
  "freeze_authority": null,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
fi

echo "  Saved to $DEPLOY_FILE"
echo ""

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------
echo "=================================================="
echo "  DEPLOYMENT SUMMARY"
echo "=================================================="
echo "  Network:        $NETWORK"
echo "  Wallet:         $WALLET"
echo "  Balance:        $BALANCE SOL"
echo "  Hook Program:   $HOOK_PROGRAM_ID"
echo "  Token Mint:     ${MINT_ADDRESS:-PENDING}"
echo "  Initial Supply: $INITIAL_MINT_AMOUNT \$MIND"
echo "  Dry Run:        $DRY_RUN"
echo "=================================================="

if [ "$DRY_RUN" = true ]; then
  echo ""
  echo "This was a DRY RUN. To deploy for real:"
  echo "  ./deploy_mainnet.sh --live"
fi
