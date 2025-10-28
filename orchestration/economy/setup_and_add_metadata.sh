#!/bin/bash

# Setup and Add Metadata to $MIND Token
# Simple Node.js approach using Metaplex SDK

set -e

echo "========================================================================"
echo "📝 SETUP AND ADD METADATA TO \$MIND TOKEN"
echo "========================================================================"
echo ""

cd "$(dirname "$0")"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo "✅ Node.js installed"
else
    echo "✅ Node.js found: $(node --version)"
fi

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Run the metadata script
echo ""
echo "========================================================================"
echo "Running metadata creation script..."
echo "========================================================================"
echo ""

npm run add-metadata

echo ""
echo "✅ Script complete!"
