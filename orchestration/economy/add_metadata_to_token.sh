#!/bin/bash

# Add Metadata to $MIND Token
# Step-by-step guide

set -e

echo "========================================================================"
echo "📝 ADDING METADATA TO \$MIND TOKEN"
echo "========================================================================"
echo ""

TOKEN_MINT="MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR"

echo "Token Mint: $TOKEN_MINT"
echo ""

# Step 1: Upload metadata JSON to Arweave
echo "========================================================================"
echo "STEP 1: Upload Metadata JSON to Arweave"
echo "========================================================================"
echo ""
echo "📄 Metadata JSON created at:"
echo "   C:\Users\reyno\mind-protocol\orchestration\economy\mind_token_metadata.json"
echo ""
echo "🌐 Upload this file to Irys (same way as logo):"
echo "   https://uploader.irys.xyz/"
echo ""
echo "⚠️  WAIT! Upload the JSON file first, then continue this script."
echo ""
read -p "Paste the Arweave URI for the metadata JSON: " METADATA_URI

if [ -z "$METADATA_URI" ]; then
    echo "❌ Metadata URI required"
    exit 1
fi

echo ""
echo "✅ Metadata URI: $METADATA_URI"

# Step 2: Install Metaboss (if not installed)
echo ""
echo "========================================================================"
echo "STEP 2: Install Metaboss (Metaplex CLI Tool)"
echo "========================================================================"
echo ""

if ! command -v metaboss &> /dev/null; then
    echo "📦 Installing metaboss..."

    # Check if Rust is installed
    if ! command -v cargo &> /dev/null; then
        echo "⚠️  Rust not found. Installing Rust first..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source $HOME/.cargo/env
    fi

    # Install metaboss
    cargo install metaboss

    echo "✅ Metaboss installed"
else
    echo "✅ Metaboss already installed"
fi

# Step 3: Create metadata for token
echo ""
echo "========================================================================"
echo "STEP 3: Create Token Metadata"
echo "========================================================================"
echo ""

echo "Creating metadata for token..."

# Create metadata using metaboss
metaboss create metadata \
    --keypair ~/.config/solana/id.json \
    --mint $TOKEN_MINT \
    --metadata $METADATA_URI \
    --update-authority ~/.config/solana/id.json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Metadata added successfully!"
else
    echo ""
    echo "❌ Failed to add metadata"
    echo ""
    echo "Alternative: Use Token Metadata program directly"
    echo "   npm install -g @metaplex-foundation/mpl-token-metadata"
    exit 1
fi

# Step 4: Verify on Solscan
echo ""
echo "========================================================================"
echo "STEP 4: Verify on Solscan"
echo "========================================================================"
echo ""
echo "🔗 Check your token metadata:"
echo "   https://solscan.io/token/$TOKEN_MINT"
echo ""
echo "You should see:"
echo "   ✅ Logo displaying"
echo "   ✅ Name: MIND"
echo "   ✅ Symbol: \$MIND"
echo "   ✅ Description visible"
echo ""

# Step 5: Lock metadata (optional)
echo "========================================================================"
echo "STEP 5: Lock Metadata (Optional)"
echo "========================================================================"
echo ""
echo "⚠️  WARNING: Locking metadata is PERMANENT and IRREVERSIBLE"
echo "⚠️  Do this ONLY after verifying everything is correct"
echo "⚠️  Do this BEFORE creating the liquidity pool"
echo ""
read -p "Do you want to LOCK metadata now? (type 'LOCK' to confirm): " LOCK_CONFIRM

if [ "$LOCK_CONFIRM" = "LOCK" ]; then
    echo ""
    echo "🔒 Locking metadata..."

    # Remove update authority
    metaboss update authority \
        --keypair ~/.config/solana/id.json \
        --mint $TOKEN_MINT \
        --new-authority null

    echo ""
    echo "✅ Metadata locked permanently!"
    echo "   Update Authority = None"
    echo ""
    echo "🔗 Verify on Solscan:"
    echo "   https://solscan.io/token/$TOKEN_MINT"
else
    echo ""
    echo "⚠️  Metadata NOT locked yet"
    echo "   You can lock it later by running:"
    echo "   metaboss update authority --keypair ~/.config/solana/id.json --mint $TOKEN_MINT --new-authority null"
fi

echo ""
echo "========================================================================"
echo "✅ METADATA PROCESS COMPLETE"
echo "========================================================================"
echo ""
