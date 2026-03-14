/**
 * Cross-language crypto test orchestrator.
 *
 * Verifies that JS and Python produce interoperable ciphertext across
 * all 6 critical paths:
 *
 *   1. JS encryptContent       -> Py decrypt_content        (AES-256-GCM)
 *   2. Py encrypt_content      -> JS decryptContent         (AES-256-GCM)
 *   3. JS encryptSpaceKeyForActor -> Py decrypt_space_key   (Sealed box)
 *   4. Py encrypt_space_key    -> JS decryptSpaceKeyForActor (Sealed box)
 *   5. JS storeActorKeys       -> Py load_actor_keys        (Key file format)
 *   6. Py store_actor_keys     -> JS loadActorKeys          (Key file format)
 *
 * Run: node tests/crypto/test_cross_language.js
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');
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

async function main() {
  console.log('Mind Protocol Crypto — Cross-Language Test Suite');
  console.log('================================================');

  // ---------------------------------------------------------------
  // Phase 1: JS produces artifacts for Python to consume
  // ---------------------------------------------------------------

  console.log('\n--- Phase 1: JS produces artifacts ---');

  // Generate a space key
  const { key: spaceKey } = crypto.generateSpaceKey();
  const spaceKeyHex = spaceKey.toString('hex');

  // Encrypt 3 test strings with AES-256-GCM
  const testStrings = [
    'The graph breathes. Nodes pulse. Edges carry energy like blood.',
    '',
    'Unicode test: \u00e8 \u00e0 \u00f2 \u00f9 \ud83c\udfad \ud83c\udf1f \ud83c\udfe0',
  ];

  const jsEncrypted = testStrings.map((plaintext) => ({
    plaintext,
    ciphertext: crypto.encryptContent(plaintext, spaceKey),
  }));

  // Generate actor key pair
  const actor = await crypto.generateActorKeyPair();
  const actorPubHex = actor.publicKey.toString('hex');
  const actorPrivHex = actor.privateKey.toString('hex');

  // Wrap a space key with sealed box
  const jsWrappedKey = await crypto.encryptSpaceKeyForActor(spaceKey, actor.publicKey);

  // Store keys to temp dir (JS -> Py key file test)
  const jsKeysDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mind-cross-js-keys-'));
  await crypto.storeActorKeys(jsKeysDir, actor);

  // Build the JS artifacts JSON
  const jsArtifacts = {
    aes_gcm: {
      space_key_hex: spaceKeyHex,
      encrypted: jsEncrypted,
    },
    sealed_box: {
      space_key_hex: spaceKeyHex,
      actor_public_key_hex: actorPubHex,
      actor_private_key_hex: actorPrivHex,
      wrapped_key_b64: jsWrappedKey,
    },
    key_files: {
      js_keys_dir: jsKeysDir,
      actor_public_key_hex: actorPubHex,
      actor_private_key_hex: actorPrivHex,
    },
  };

  // Write JS artifacts to temp file
  const inputPath = path.join(os.tmpdir(), `mind-cross-input-${Date.now()}.json`);
  const outputPath = path.join(os.tmpdir(), `mind-cross-output-${Date.now()}.json`);
  fs.writeFileSync(inputPath, JSON.stringify(jsArtifacts, null, 2), 'utf8');

  console.log(`  JS artifacts written to ${inputPath}`);

  // ---------------------------------------------------------------
  // Phase 2: Spawn Python verifier + generator
  // ---------------------------------------------------------------

  console.log('\n--- Phase 2: Python verifies JS artifacts & generates its own ---');

  const pyScript = path.join(__dirname, 'test_cross_language_verify.py');
  const repoRoot = path.resolve(__dirname, '..', '..');

  try {
    const pyResult = execSync(
      `python3 "${pyScript}" --input "${inputPath}" --output "${outputPath}"`,
      {
        cwd: repoRoot,
        encoding: 'utf8',
        timeout: 30000,
        stdio: ['pipe', 'pipe', 'pipe'],
      }
    );
    console.log(pyResult);
  } catch (err) {
    console.error('Python verifier failed:');
    if (err.stdout) console.error(err.stdout);
    if (err.stderr) console.error(err.stderr);
    console.error(`Exit code: ${err.status}`);
    // Count Python failures
    const pyStdout = (err.stdout || '') + (err.stderr || '');
    const pyFails = (pyStdout.match(/FAIL/g) || []).length;
    failed += Math.max(pyFails, 1);
  }

  // ---------------------------------------------------------------
  // Phase 3: JS reads Python output and verifies
  // ---------------------------------------------------------------

  console.log('\n--- Phase 3: JS verifies Python-generated artifacts ---');

  if (!fs.existsSync(outputPath)) {
    console.error(`  FAIL  Python output file not found: ${outputPath}`);
    failed++;
    printSummary();
    return;
  }

  const pyArtifacts = JSON.parse(fs.readFileSync(outputPath, 'utf8'));

  // --- Path 2: Py encrypt_content -> JS decryptContent ---
  console.log('\n  Path 2: Py encrypt_content -> JS decryptContent (AES-256-GCM)');
  const pySpaceKey = Buffer.from(pyArtifacts.aes_gcm.space_key_hex, 'hex');
  for (const item of pyArtifacts.aes_gcm.encrypted) {
    try {
      const decrypted = crypto.decryptContent(item.ciphertext, pySpaceKey);
      assert(decrypted === item.plaintext,
        `JS decrypts Py ciphertext: "${item.plaintext.substring(0, 40)}..."`);
    } catch (err) {
      assert(false, `JS decrypts Py ciphertext: "${item.plaintext.substring(0, 40)}..." — ${err.message}`);
    }
  }

  // --- Path 4: Py encrypt_space_key_for_actor -> JS decryptSpaceKeyForActor ---
  console.log('\n  Path 4: Py encrypt_space_key -> JS decryptSpaceKeyForActor (Sealed box)');
  const pyWrappedSpaceKey = pyArtifacts.sealed_box.wrapped_key_b64;
  const sealedActorPub = Buffer.from(pyArtifacts.sealed_box.actor_public_key_hex, 'hex');
  const sealedActorPriv = Buffer.from(pyArtifacts.sealed_box.actor_private_key_hex, 'hex');
  const pySpaceKeyForSeal = Buffer.from(pyArtifacts.sealed_box.space_key_hex, 'hex');

  try {
    const unwrapped = await crypto.decryptSpaceKeyForActor(
      pyWrappedSpaceKey, sealedActorPub, sealedActorPriv
    );
    assert(unwrapped.equals(pySpaceKeyForSeal),
      'JS unwraps Py sealed box — space key matches');
  } catch (err) {
    assert(false, `JS unwraps Py sealed box — ${err.message}`);
  }

  // --- Path 6: Py store_actor_keys -> JS loadActorKeys ---
  console.log('\n  Path 6: Py store_actor_keys -> JS loadActorKeys (Key file format)');
  const pyKeysDir = pyArtifacts.key_files.py_keys_dir;

  if (pyKeysDir && fs.existsSync(pyKeysDir)) {
    try {
      const loadedKeys = await crypto.loadActorKeys(pyKeysDir);
      const expectedPub = Buffer.from(pyArtifacts.key_files.actor_public_key_hex, 'hex');
      const expectedPriv = Buffer.from(pyArtifacts.key_files.actor_private_key_hex, 'hex');

      assert(loadedKeys.publicKey.equals(expectedPub),
        'JS loads Py public key file — matches');
      assert(loadedKeys.privateKey.equals(expectedPriv),
        'JS loads Py private key file — matches');
    } catch (err) {
      assert(false, `JS loads Py key files — ${err.message}`);
    }
  } else {
    assert(false, `Py keys dir not found: ${pyKeysDir}`);
  }

  // ---------------------------------------------------------------
  // Cleanup
  // ---------------------------------------------------------------

  try { fs.rmSync(jsKeysDir, { recursive: true, force: true }); } catch (_) { /* noop */ }
  try { if (pyKeysDir) fs.rmSync(pyKeysDir, { recursive: true, force: true }); } catch (_) { /* noop */ }
  try { fs.unlinkSync(inputPath); } catch (_) { /* noop */ }
  try { fs.unlinkSync(outputPath); } catch (_) { /* noop */ }

  printSummary();
}

function printSummary() {
  console.log('\n================================================');
  console.log(`Results: ${passed} passed, ${failed} failed`);

  if (failed > 0) {
    process.exit(1);
  } else {
    console.log('All cross-language tests passed.');
  }
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
