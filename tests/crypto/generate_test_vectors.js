/**
 * Generate static test vectors for cross-language crypto verification.
 *
 * Run: node tests/crypto/generate_test_vectors.js
 *
 * Outputs: tests/crypto/test_vectors.json
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('../../lib/crypto');

async function main() {
  // --- AES-256-GCM vectors ---
  // Known key (deterministic for test purposes)
  const keyHex = 'a1b2c3d4e5f60718293040506070809011a2b3c4d5e6f708192a3b4c5d6e7f80';
  const key = Buffer.from(keyHex, 'hex');

  const plaintexts = [
    'The graph breathes. Nodes pulse. Edges carry energy like blood.',
    '',
    'Unicode test: \u00e8 \u00e0 \u00f2 \u00f9 \ud83c\udfad \ud83c\udf1f \ud83c\udfe0',
  ];

  const aesVectors = plaintexts.map((plaintext) => {
    const ciphertext = crypto.encryptContent(plaintext, key);
    return { key_hex: keyHex, plaintext, ciphertext };
  });

  // --- Actor key pair (sealed box) vectors ---
  const actorKeyPair = await crypto.generateActorKeyPair();
  const spaceKey = crypto.generateSpaceKey().key;
  const wrappedKey = await crypto.encryptSpaceKeyForActor(spaceKey, actorKeyPair.publicKey);

  const sealedBoxVectors = [
    {
      space_key_hex: spaceKey.toString('hex'),
      actor_public_key_hex: actorKeyPair.publicKey.toString('hex'),
      actor_private_key_hex: actorKeyPair.privateKey.toString('hex'),
      wrapped_key_b64: wrappedKey,
    },
  ];

  // --- Key file format vectors ---
  const keyFileVectors = [
    {
      public_key_b64: actorKeyPair.publicKey.toString('base64'),
      private_key_b64: actorKeyPair.privateKey.toString('base64'),
    },
  ];

  // --- Write vectors ---
  const vectors = {
    aes_gcm: aesVectors,
    sealed_box: sealedBoxVectors,
    key_files: keyFileVectors,
  };

  const outPath = path.join(__dirname, 'test_vectors.json');
  fs.writeFileSync(outPath, JSON.stringify(vectors, null, 2) + '\n', 'utf8');
  console.log(`Wrote test vectors to ${outPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
