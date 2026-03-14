/**
 * Crypto library tests — round-trip verification for all modules.
 *
 * Run: node tests/crypto/test_crypto.js
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('../../lib/crypto');

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log(`  PASS  ${label}`);
    passed++;
  } else {
    console.error(`  FAIL  ${label}`);
    failed++;
  }
}

async function testSpaceKeyRoundTrip() {
  console.log('\n--- Space Key: round-trip encrypt/decrypt ---');

  const { key } = crypto.generateSpaceKey();
  assert(Buffer.isBuffer(key) && key.length === 32, 'generateSpaceKey returns 32-byte Buffer');

  const plaintext = 'The graph breathes. Nodes pulse. Edges carry energy like blood.';
  const encrypted = crypto.encryptContent(plaintext, key);
  assert(typeof encrypted === 'string', 'encryptContent returns a string');
  assert(encrypted.split(':').length === 3, 'ciphertext has 3 colon-separated parts');

  const decrypted = crypto.decryptContent(encrypted, key);
  assert(decrypted === plaintext, 'decryptContent recovers original plaintext');

  // Encrypt again — IV must differ (different ciphertext)
  const encrypted2 = crypto.encryptContent(plaintext, key);
  assert(encrypted2 !== encrypted, 'two encryptions of same plaintext produce different ciphertext (fresh IV)');

  // Decrypt second ciphertext
  const decrypted2 = crypto.decryptContent(encrypted2, key);
  assert(decrypted2 === plaintext, 'second ciphertext also decrypts correctly');
}

function testIsEncrypted() {
  console.log('\n--- isEncrypted detection ---');

  const { key } = crypto.generateSpaceKey();
  const ct = crypto.encryptContent('test', key);

  assert(crypto.isEncrypted(ct) === true, 'isEncrypted returns true for ciphertext');
  assert(crypto.isEncrypted('hello world') === false, 'isEncrypted returns false for plaintext');
  assert(crypto.isEncrypted('') === false, 'isEncrypted returns false for empty string');
  assert(crypto.isEncrypted('a:b') === false, 'isEncrypted returns false for two-part string');
  assert(crypto.isEncrypted(123) === false, 'isEncrypted returns false for non-string');
  assert(crypto.isEncrypted('abc:def:ghi') === true, 'isEncrypted returns true for valid-looking three-part base64');
}

async function testActorKeysRoundTrip() {
  console.log('\n--- Actor Keys: generate / store / load ---');

  const kp = await crypto.generateActorKeyPair();
  assert(Buffer.isBuffer(kp.publicKey) && kp.publicKey.length === 32, 'publicKey is 32-byte Buffer');
  assert(Buffer.isBuffer(kp.privateKey) && kp.privateKey.length === 32, 'privateKey is 32-byte Buffer');

  // Store to temp directory
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mind-crypto-test-'));
  await crypto.storeActorKeys(tmpDir, kp);

  const pubFile = path.join(tmpDir, 'public_key.b64');
  const privFile = path.join(tmpDir, 'private_key.b64');
  assert(fs.existsSync(pubFile), 'public_key.b64 written');
  assert(fs.existsSync(privFile), 'private_key.b64 written');

  // Load back
  const loaded = await crypto.loadActorKeys(tmpDir);
  assert(loaded.publicKey.equals(kp.publicKey), 'loaded publicKey matches original');
  assert(loaded.privateKey.equals(kp.privateKey), 'loaded privateKey matches original');

  // Cleanup
  fs.rmSync(tmpDir, { recursive: true, force: true });
}

async function testKeyExchangeRoundTrip() {
  console.log('\n--- Key Exchange: wrap / unwrap space key ---');

  // Generate a space key and an actor key pair
  const { key: spaceKey } = crypto.generateSpaceKey();
  const actor = await crypto.generateActorKeyPair();

  // Encrypt the space key for the actor
  const wrapped = await crypto.encryptSpaceKeyForActor(spaceKey, actor.publicKey);
  assert(typeof wrapped === 'string', 'encryptSpaceKeyForActor returns a base64 string');
  assert(!wrapped.includes(':'), 'sealed box is a single base64 blob (no colons)');

  // Decrypt the space key
  const unwrapped = await crypto.decryptSpaceKeyForActor(wrapped, actor.publicKey, actor.privateKey);
  assert(Buffer.isBuffer(unwrapped), 'decryptSpaceKeyForActor returns a Buffer');
  assert(unwrapped.equals(spaceKey), 'unwrapped space key matches original');

  // Wrong key pair should fail
  const other = await crypto.generateActorKeyPair();
  let threw = false;
  try {
    await crypto.decryptSpaceKeyForActor(wrapped, other.publicKey, other.privateKey);
  } catch (e) {
    threw = true;
  }
  assert(threw, 'decryption with wrong key pair throws an error');
}

async function testErrorHandling() {
  console.log('\n--- Error handling ---');

  let threw;

  // encryptContent with wrong key size
  threw = false;
  try { crypto.encryptContent('test', Buffer.alloc(16)); } catch (e) { threw = true; }
  assert(threw, 'encryptContent rejects 16-byte key');

  // decryptContent with corrupted ciphertext
  threw = false;
  const { key } = crypto.generateSpaceKey();
  try { crypto.decryptContent('bad:data:here', key); } catch (e) { threw = true; }
  assert(threw, 'decryptContent rejects corrupted ciphertext');

  // encryptSpaceKeyForActor with wrong key size
  threw = false;
  try { await crypto.encryptSpaceKeyForActor(Buffer.alloc(16), Buffer.alloc(32)); } catch (e) { threw = true; }
  assert(threw, 'encryptSpaceKeyForActor rejects 16-byte space key');

  // loadActorKeys from non-existent directory
  threw = false;
  try { await crypto.loadActorKeys('/tmp/nonexistent-mind-crypto-test-xyz'); } catch (e) { threw = true; }
  assert(threw, 'loadActorKeys rejects missing directory');
}

// --- Run all tests ---

(async () => {
  console.log('Mind Protocol Crypto — Test Suite');
  console.log('==================================');

  await testSpaceKeyRoundTrip();
  testIsEncrypted();
  await testActorKeysRoundTrip();
  await testKeyExchangeRoundTrip();
  await testErrorHandling();

  console.log('\n==================================');
  console.log(`Results: ${passed} passed, ${failed} failed`);

  if (failed > 0) {
    process.exit(1);
  } else {
    console.log('All tests passed.');
  }
})();
