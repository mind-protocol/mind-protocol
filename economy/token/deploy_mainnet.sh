#!/usr/bin/env bash
# =============================================================================
# $MIND Token — Mainnet Deployment Script
# =============================================================================
#
# SPL Token 2022 with extensions:
#   - TransferFeeConfig (1% protocol fee, max 1 $MIND)
#   - MetadataPointer + TokenMetadata
#   - MintCloseAuthority
#   - TransferHook (optional — requires program deployed first)
#
# Usage:
#   ./deploy_mainnet.sh --dry-run          # Preview all commands
#   ./deploy_mainnet.sh --live             # Execute on mainnet-beta
#   ./deploy_mainnet.sh --live --with-hook # Include TransferHook extension
#
# Wallet: CCsJLZR8b19iDgS9hXUYs9q2c928ihzZdfSgZLPYffWg
# =============================================================================

set -euo pipefail

# --- Configuration ---
NETWORK="mainnet-beta"
RPC_URL="https://api.mainnet-beta.solana.com"
TOKEN_2022_PROGRAM="TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
KEYPAIR="$HOME/.config/solana/id.json"
DECIMALS=9
TOKEN_NAME="MIND"
TOKEN_SYMBOL="MIND"
TOKEN_URI="https://mindprotocol.ai/token.json"
TRANSFER_FEE_BPS=100            # 1%
TRANSFER_FEE_MAX=1.0            # 1 $MIND max fee per transfer (UI amount)
INITIAL_MINT_AMOUNT=100000      # 100,000 $MIND
TRANSFER_HOOK_PROGRAM=""        # Set if deploying with hook
OUTPUT_DIR="./deploy_output"

# --- Parse args ---
DRY_RUN=true
WITH_HOOK=false

for arg in "$@"; do
    case $arg in
        --live) DRY_RUN=false ;;
        --dry-run) DRY_RUN=true ;;
        --with-hook) WITH_HOOK=true ;;
        --hook-program=*) TRANSFER_HOOK_PROGRAM="${arg#*=}" ;;
        *) echo "Unknown arg: $arg"; exit 1 ;;
    esac
done

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${CYAN}[*]${NC} $1"; }
ok()   { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[-]${NC} $1"; }

run_cmd() {
    local desc="$1"
    shift
    log "$desc"
    echo "    CMD: $*"
    if [ "$DRY_RUN" = true ]; then
        echo "    [DRY RUN — skipped]"
        return 0
    fi
    "$@"
}

# =============================================================================
echo ""
echo "============================================================"
echo "  \$MIND Token 2022 — Mainnet Deployment"
echo "============================================================"
echo ""
echo "  Network:        $NETWORK"
echo "  Dry Run:        $DRY_RUN"
echo "  TransferHook:   $WITH_HOOK"
echo "  Decimals:       $DECIMALS"
echo "  Transfer Fee:   ${TRANSFER_FEE_BPS}bps (1%)"
echo "  Max Fee:        $TRANSFER_FEE_MAX $TOKEN_SYMBOL"
echo "  Initial Mint:   $INITIAL_MINT_AMOUNT $TOKEN_SYMBOL"
echo "  Token URI:      $TOKEN_URI"
echo ""
echo "============================================================"

# --- Step 0: Prerequisites ---
log "Step 0: Checking prerequisites..."

WALLET_ADDR=$(solana address)
log "Wallet: $WALLET_ADDR"

BALANCE=$(solana balance --url "$RPC_URL" | awk '{print $1}')
log "Balance: $BALANCE SOL"

# Check minimum balance
MIN_BALANCE="0.05"
if (( $(echo "$BALANCE < $MIN_BALANCE" | bc -l) )); then
    err "Insufficient balance: $BALANCE SOL (need at least $MIN_BALANCE SOL)"
    exit 1
fi
ok "Balance check passed"

solana --version
spl-token --version
ok "CLI tools available"

# --- Step 1: Create Token 2022 Mint ---
echo ""
log "Step 1: Creating Token 2022 mint..."

CREATE_CMD=(
    spl-token create-token
    --program-id "$TOKEN_2022_PROGRAM"
    --decimals "$DECIMALS"
    --transfer-fee-basis-points "$TRANSFER_FEE_BPS"
    --transfer-fee-maximum-fee "$TRANSFER_FEE_MAX"
    --enable-metadata
    --enable-close
    --url "$RPC_URL"
    --fee-payer "$KEYPAIR"
)

if [ "$WITH_HOOK" = true ]; then
    if [ -z "$TRANSFER_HOOK_PROGRAM" ]; then
        err "TransferHook requested but --hook-program not set"
        err "Deploy the TransferHook program first, then pass:"
        err "  --hook-program=<PROGRAM_ID>"
        exit 1
    fi
    CREATE_CMD+=(--transfer-hook "$TRANSFER_HOOK_PROGRAM")
    log "TransferHook program: $TRANSFER_HOOK_PROGRAM"
fi

if [ "$DRY_RUN" = true ]; then
    log "CREATE TOKEN COMMAND:"
    echo "    ${CREATE_CMD[*]}"
    echo "    [DRY RUN — skipped]"
    MINT_ADDRESS="DRY_RUN_MINT_PLACEHOLDER"
else
    echo ""
    warn "IRREVERSIBLE: This will create a new token on mainnet-beta."
    warn "Extensions are permanent and cannot be changed after creation."
    echo ""
    read -p "Proceed with token creation? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        err "Aborted by user"
        exit 1
    fi

    OUTPUT=$("${CREATE_CMD[@]}" 2>&1)
    echo "$OUTPUT"

    # Parse mint address from output
    MINT_ADDRESS=$(echo "$OUTPUT" | grep -oP '(?:Creating token |Address:  )\K[A-HJ-NP-Za-km-z1-9]{32,44}' | head -1)
    if [ -z "$MINT_ADDRESS" ]; then
        err "Failed to parse mint address from output"
        err "Output: $OUTPUT"
        exit 1
    fi
fi

ok "Token mint: $MINT_ADDRESS"

# --- Step 2: Initialize Metadata ---
echo ""
log "Step 2: Initializing on-chain metadata..."

run_cmd "Setting metadata (name=$TOKEN_NAME, symbol=$TOKEN_SYMBOL)" \
    spl-token initialize-metadata \
    "$MINT_ADDRESS" "$TOKEN_NAME" "$TOKEN_SYMBOL" "$TOKEN_URI" \
    --url "$RPC_URL" \
    --fee-payer "$KEYPAIR"

ok "Metadata initialized"

# --- Step 3: Create Token Account ---
echo ""
log "Step 3: Creating token account for deployer..."

run_cmd "Creating associated token account" \
    spl-token create-account \
    "$MINT_ADDRESS" \
    --url "$RPC_URL" \
    --fee-payer "$KEYPAIR" \
    --program-id "$TOKEN_2022_PROGRAM"

ok "Token account created"

# --- Step 4: Initial Mint ---
echo ""
log "Step 4: Minting initial supply ($INITIAL_MINT_AMOUNT $TOKEN_SYMBOL)..."

if [ "$DRY_RUN" = false ]; then
    echo ""
    warn "This will mint $INITIAL_MINT_AMOUNT $TOKEN_SYMBOL to your wallet."
    read -p "Proceed with minting? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        err "Minting aborted by user"
        # Still save what we have
    else
        spl-token mint \
            "$MINT_ADDRESS" "$INITIAL_MINT_AMOUNT" \
            --url "$RPC_URL" \
            --fee-payer "$KEYPAIR" \
            --program-id "$TOKEN_2022_PROGRAM"
        ok "Minted $INITIAL_MINT_AMOUNT $TOKEN_SYMBOL"
    fi
else
    log "MINT COMMAND:"
    echo "    spl-token mint $MINT_ADDRESS $INITIAL_MINT_AMOUNT --url $RPC_URL --program-id $TOKEN_2022_PROGRAM"
    echo "    [DRY RUN — skipped]"
fi

# --- Step 5: Verify ---
echo ""
log "Step 5: Verification..."

if [ "$DRY_RUN" = false ]; then
    echo ""
    log "Token info:"
    spl-token display "$MINT_ADDRESS" --url "$RPC_URL" --program-id "$TOKEN_2022_PROGRAM" 2>/dev/null || \
    spl-token account-info --address "$MINT_ADDRESS" --url "$RPC_URL" --program-id "$TOKEN_2022_PROGRAM" 2>/dev/null || \
    log "Run: spl-token display $MINT_ADDRESS --url $RPC_URL"

    echo ""
    log "Token balance:"
    spl-token balance "$MINT_ADDRESS" --url "$RPC_URL" --program-id "$TOKEN_2022_PROGRAM" 2>/dev/null || true
fi

# --- Step 6: Save Deployment Info ---
echo ""
log "Step 6: Saving deployment info..."

mkdir -p "$OUTPUT_DIR"

DEPLOY_FILE="$OUTPUT_DIR/deployment_mainnet.json"
cat > "$DEPLOY_FILE" << DEPLOYEOF
{
  "network": "$NETWORK",
  "mint_address": "$MINT_ADDRESS",
  "token_name": "$TOKEN_NAME",
  "token_symbol": "$TOKEN_SYMBOL",
  "decimals": $DECIMALS,
  "token_uri": "$TOKEN_URI",
  "transfer_fee_bps": $TRANSFER_FEE_BPS,
  "transfer_fee_max": "$TRANSFER_FEE_MAX",
  "initial_mint": $INITIAL_MINT_AMOUNT,
  "transfer_hook_program": "$TRANSFER_HOOK_PROGRAM",
  "deployer_wallet": "$WALLET_ADDR",
  "token_program": "$TOKEN_2022_PROGRAM",
  "extensions": [
    "TransferFeeConfig",
    "MetadataPointer",
    "TokenMetadata",
    "MintCloseAuthority"$([ "$WITH_HOOK" = true ] && echo ',
    "TransferHook"')
  ],
  "dry_run": $DRY_RUN,
  "deployed_at": "$(date -Iseconds)"
}
DEPLOYEOF

ok "Deployment info saved to $DEPLOY_FILE"

# --- Summary ---
echo ""
echo "============================================================"
echo "  DEPLOYMENT SUMMARY"
echo "============================================================"
echo ""
echo "  Mint Address:     $MINT_ADDRESS"
echo "  Network:          $NETWORK"
echo "  Extensions:       TransferFee, Metadata, MintClose$([ "$WITH_HOOK" = true ] && echo ', TransferHook')"
echo "  Initial Supply:   $INITIAL_MINT_AMOUNT $TOKEN_SYMBOL"
echo "  Deployer:         $WALLET_ADDR"
echo "  Dry Run:          $DRY_RUN"
echo ""
if [ "$DRY_RUN" = true ]; then
    warn "This was a dry run. Run with --live to execute."
fi
echo "============================================================"
echo ""
