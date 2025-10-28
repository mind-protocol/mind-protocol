#!/bin/bash

# Add Metadata to $MIND Token and Lock It
# Run this AFTER token deployment, BEFORE creating LP

set -e

echo "========================================================================"
echo "📝 ADDING METADATA TO \$MIND TOKEN"
echo "========================================================================"

# Get token mint address
echo ""
echo "📍 Enter your token mint address:"
read -p "Token mint: " TOKEN_MINT

if [ -z "$TOKEN_MINT" ]; then
    echo "❌ Token mint required"
    exit 1
fi

echo ""
echo "📋 Metadata Configuration:"
echo ""

# Get metadata details
read -p "Token Name [MIND]: " TOKEN_NAME
TOKEN_NAME=${TOKEN_NAME:-MIND}

read -p "Token Symbol [\$MIND]: " TOKEN_SYMBOL
TOKEN_SYMBOL=${TOKEN_SYMBOL:-\$MIND}

read -p "Token Description: " TOKEN_DESCRIPTION

read -p "Logo/Image URI (Arweave/IPFS): " IMAGE_URI

read -p "Website URL: " WEBSITE_URL

read -p "Twitter URL: " TWITTER_URL

# Summary
echo ""
echo "========================================================================"
echo "METADATA SUMMARY"
echo "========================================================================"
echo "Token Mint: $TOKEN_MINT"
echo "Name: $TOKEN_NAME"
echo "Symbol: $TOKEN_SYMBOL"
echo "Description: $TOKEN_DESCRIPTION"
echo "Image: $IMAGE_URI"
echo "Website: $WEBSITE_URL"
echo "Twitter: $TWITTER_URL"
echo ""

read -p "Does this look correct? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cancelled"
    exit 0
fi

# Create metadata JSON
METADATA_FILE="/tmp/mind_token_metadata.json"
cat > "$METADATA_FILE" << EOF
{
  "name": "$TOKEN_NAME",
  "symbol": "$TOKEN_SYMBOL",
  "description": "$TOKEN_DESCRIPTION",
  "image": "$IMAGE_URI",
  "external_url": "$WEBSITE_URL",
  "properties": {
    "twitter": "$TWITTER_URL"
  }
}
EOF

echo ""
echo "✅ Metadata file created: $METADATA_FILE"

# Upload metadata to Arweave/IPFS (you'll need to do this separately or use a service)
echo ""
echo "⚠️  NEXT STEPS:"
echo ""
echo "1. Upload metadata JSON to Arweave or IPFS"
echo "   File: $METADATA_FILE"
echo ""
echo "2. Get the permanent URI (e.g., ar://... or ipfs://...)"
echo ""
echo "3. Add metadata to token using Metaplex:"
echo "   spl-token create-metadata $TOKEN_MINT <metadata_uri>"
echo ""
echo "4. Verify metadata on Solscan:"
echo "   https://solscan.io/token/$TOKEN_MINT"
echo ""
echo "5. When ready to lock (IRREVERSIBLE):"
echo ""

# Lock metadata option
echo "⚠️  WARNING: LOCKING METADATA IS PERMANENT"
echo ""
read -p "Do you want to LOCK metadata now? (type 'LOCK' to confirm): " LOCK_CONFIRM

if [ "$LOCK_CONFIRM" = "LOCK" ]; then
    echo ""
    echo "🔒 Locking metadata..."

    # Remove update authority
    spl-token authorize $TOKEN_MINT metadata --disable

    echo "✅ Metadata locked! This token's metadata can never be changed."
    echo ""
    echo "🔗 Verify on Solscan:"
    echo "   https://solscan.io/token/$TOKEN_MINT"
    echo "   Should show: Update Authority = None"
else
    echo ""
    echo "⚠️  Metadata NOT locked yet"
    echo "   You can lock it later by running:"
    echo "   spl-token authorize $TOKEN_MINT metadata --disable"
fi

echo ""
echo "========================================================================"
echo "✅ COMPLETE"
echo "========================================================================"
