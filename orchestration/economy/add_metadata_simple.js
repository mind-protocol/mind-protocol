// Simple script to add metadata to $MIND token
// Uses Metaplex JavaScript SDK

import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { createMetadataAccountV3 } from '@metaplex-foundation/mpl-token-metadata';
import { publicKey, keypairIdentity } from '@metaplex-foundation/umi';
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

async function addMetadata() {
  console.log('========================================================================');
  console.log('📝 ADDING METADATA TO $MIND TOKEN');
  console.log('========================================================================\n');

  // Create UMI instance connected to mainnet
  const umi = createUmi('https://api.mainnet-beta.solana.com');

  // Load deployer keypair from ~/.config/solana/id.json
  const keypairPath = join(homedir(), '.config', 'solana', 'id.json');
  console.log('Loading keypair from:', keypairPath);

  const keypairData = JSON.parse(readFileSync(keypairPath, 'utf-8'));
  const keypairBytes = Uint8Array.from(keypairData);

  const keypair = umi.eddsa.createKeypairFromSecretKey(keypairBytes);
  umi.use(keypairIdentity(keypair));

  console.log('✅ Keypair loaded:', keypair.publicKey, '\n');

  // Token details
  const mint = publicKey('MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR');
  const metadataUri = 'https://arweave.net/Cx5kP2BJSnd1KLwWTiGNZp2YJvha6HdDFFp4C2puKRif';

  console.log('Token Mint:', mint);
  console.log('Metadata URI:', metadataUri);
  console.log('Update Authority:', keypair.publicKey);
  console.log('\nCreating metadata account...\n');

  try {
    const result = await createMetadataAccountV3(umi, {
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
      isMutable: true, // Can update metadata until you lock it
      collectionDetails: null,
    }).sendAndConfirm(umi);

    console.log('✅ Metadata added successfully!');
    console.log('\n🔗 Transaction:', result.signature);
    console.log('\n🔗 Verify on Solscan:');
    console.log('   https://solscan.io/token/MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR');
    console.log('\nYou should see:');
    console.log('   ✅ Logo displaying');
    console.log('   ✅ Name: MIND');
    console.log('   ✅ Symbol: $MIND');
    console.log('   ✅ Description visible');
    console.log('\n========================================================================');
    console.log('✅ METADATA CREATION COMPLETE');
    console.log('========================================================================\n');

  } catch (error) {
    console.error('\n❌ Error adding metadata:', error);

    if (error.message.includes('already in use')) {
      console.log('\n⚠️  Metadata account already exists for this token!');
      console.log('   Check Solscan to see current metadata:');
      console.log('   https://solscan.io/token/MhKddoVAmym987FJYeybQr4L3C5zkLDcogXkNm8QLrR');
    }

    process.exit(1);
  }
}

addMetadata().catch(console.error);
