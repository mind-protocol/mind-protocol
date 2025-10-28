#!/bin/bash

# Alternative approach: Use Sugar CLI to add metadata

set -e

echo "========================================================================"
echo "📝 ADDING METADATA TO \$MIND TOKEN (Alternative Method)"
echo "========================================================================"
echo ""

TOKEN_MINT="MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR"
METADATA_URI="https://arweave.net/Cx5kP2BJSnd1KLwWTiGNZp2YJvha6HdDFFp4C2puKRif"

echo "Token Mint: $TOKEN_MINT"
echo "Metadata URI: $METADATA_URI"
echo ""

# Install Sugar CLI (Metaplex Candy Machine v3 tool)
echo "========================================================================"
echo "Installing Sugar CLI..."
echo "========================================================================"
echo ""

bash <(curl -sSf https://sugar.metaplex.com/install.sh)

# Add sugar to PATH if not already
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

echo ""
echo "✅ Sugar installed"

# Note: Sugar is primarily for Candy Machine, not for fungible tokens
# We need a different approach

echo ""
echo "========================================================================"
echo "Alternative: Using spl-token command directly"
echo "========================================================================"
echo ""

# Create metadata account using Token-2022 standard
echo "⚠️  SPL Token standard requires Token Metadata extension"
echo ""
echo "Since your token was created with basic spl-token (not Token-2022),"
echo "we need to use Metaplex Token Metadata program."
echo ""
echo "Best approach: Use Solana CLI with token metadata instructions"
echo ""

# Create temporary script to add metadata
cat > /tmp/add_metadata.js << 'EOF'
// Add metadata to SPL token using Metaplex
const { Connection, PublicKey, Keypair } = require('@solana/web3.js');
const { Metadata } = require('@metaplex-foundation/mpl-token-metadata');
const fs = require('fs');

async function addMetadata() {
  const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');

  // Load deployer keypair
  const keypairData = JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json'));
  const deployer = Keypair.fromSecretKey(Uint8Array.from(keypairData));

  const tokenMint = new PublicKey('MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR');
  const metadataUri = 'https://arweave.net/Cx5kP2BJSnd1KLwWTiGNZp2YJvha6HdDFFp4C2puKRif';

  // Get metadata PDA
  const [metadataPDA] = await PublicKey.findProgramAddress(
    [
      Buffer.from('metadata'),
      new PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s').toBuffer(),
      tokenMint.toBuffer(),
    ],
    new PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s')
  );

  console.log('Creating metadata account...');
  console.log('Token Mint:', tokenMint.toString());
  console.log('Metadata PDA:', metadataPDA.toString());
  console.log('Metadata URI:', metadataUri);

  // Create metadata instruction
  // This requires @metaplex-foundation/mpl-token-metadata package

  console.log('\n✅ Metadata PDA calculated');
  console.log('\nNext: Create metadata account using Metaplex SDK');
}

addMetadata().catch(console.error);
EOF

echo "========================================================================"
echo "RECOMMENDED: Use Solana Cookbook Method"
echo "========================================================================"
echo ""
echo "We'll use the JavaScript SDK approach. Installing dependencies..."
echo ""

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Create package.json for metadata script
mkdir -p /tmp/mind_metadata
cd /tmp/mind_metadata

cat > package.json << 'EOF'
{
  "name": "mind-token-metadata",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@solana/web3.js": "^1.87.6",
    "@metaplex-foundation/mpl-token-metadata": "^3.2.1",
    "@metaplex-foundation/umi": "^0.9.2",
    "@metaplex-foundation/umi-bundle-defaults": "^0.9.2"
  }
}
EOF

echo "Installing Node.js packages..."
npm install

# Create the actual metadata script
cat > add-metadata.js << 'JSEOF'
import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { createMetadataAccountV3 } from '@metaplex-foundation/mpl-token-metadata';
import { publicKey, keypairIdentity } from '@metaplex-foundation/umi';
import fs from 'fs';
import path from 'path';
import os from 'os';

async function main() {
  // Create UMI instance
  const umi = createUmi('https://api.mainnet-beta.solana.com');

  // Load deployer keypair
  const keypairPath = path.join(os.homedir(), '.config', 'solana', 'id.json');
  const keypairData = JSON.parse(fs.readFileSync(keypairPath, 'utf-8'));
  const keypairBytes = Uint8Array.from(keypairData);

  // Set up keypair identity
  const keypair = umi.eddsa.createKeypairFromSecretKey(keypairBytes);
  umi.use(keypairIdentity(keypair));

  const mint = publicKey('MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR');
  const metadataUri = 'https://arweave.net/Cx5kP2BJSnd1KLwWTiGNZp2YJvha6HdDFFp4C2puKRif';

  console.log('Creating metadata account...');
  console.log('Token Mint:', mint);
  console.log('Metadata URI:', metadataUri);
  console.log('Update Authority:', keypair.publicKey);

  try {
    await createMetadataAccountV3(umi, {
      mint,
      mintAuthority: keypair,
      payer: keypair,
      updateAuthority: keypair.publicKey,
      data: {
        name: 'MIND',
        symbol: '$MIND',
        uri: metadataUri,
        sellerFeeBasisPoints: 0,
        creators: null,
        collection: null,
        uses: null,
      },
      isMutable: true,
      collectionDetails: null,
    }).sendAndConfirm(umi);

    console.log('\n✅ Metadata added successfully!');
    console.log('\n🔗 Verify on Solscan:');
    console.log('   https://solscan.io/token/MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR');

  } catch (error) {
    console.error('❌ Error adding metadata:', error.message);
    process.exit(1);
  }
}

main();
JSEOF

echo ""
echo "✅ Script prepared"
echo ""
echo "Running metadata creation..."
echo ""

node add-metadata.js

echo ""
echo "========================================================================"
echo "✅ COMPLETE"
echo "========================================================================"
