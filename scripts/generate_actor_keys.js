#!/usr/bin/env node

/**
 * generate_actor_keys.js — Generate X25519 key pair for a Mind Protocol AI citizen.
 *
 * Usage:
 *   node scripts/generate_actor_keys.js --actor nervo --dir citizens/nervo/.keys/
 *   node scripts/generate_actor_keys.js --actor nervo --dir citizens/nervo/.keys/ --graph venezia
 *   node scripts/generate_actor_keys.js --actor nervo --dir citizens/nervo/.keys/ --force
 *
 * Steps:
 *   1. Generates X25519 key pair using libsodium
 *   2. Stores in specified .keys/ directory (public_key.b64, private_key.b64)
 *   3. Optionally registers public key on Actor node in FalkorDB graph
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// CLI arg parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--actor' && argv[i + 1]) {
      args.actor = argv[++i];
    } else if (arg === '--dir' && argv[i + 1]) {
      args.dir = argv[++i];
    } else if (arg === '--graph' && argv[i + 1]) {
      args.graph = argv[++i];
    } else if (arg === '--force') {
      args.force = true;
    } else if (arg === '--help' || arg === '-h') {
      args.help = true;
    }
  }
  return args;
}

function printUsage() {
  console.log(`
Usage:
  node scripts/generate_actor_keys.js --actor <handle> --dir <keys-directory> [--graph <graph-name>] [--force]

Options:
  --actor   Actor handle (e.g. nervo)                    [required]
  --dir     Directory to store key files                 [required]
  --graph   FalkorDB graph name — registers public key   [optional]
  --force   Overwrite existing .keys/ directory           [optional]
  --help    Show this message
`);
}

// ---------------------------------------------------------------------------
// Key generation (libsodium X25519)
// ---------------------------------------------------------------------------

async function generateKeyPair() {
  const sodium = require('libsodium-wrappers');
  await sodium.ready;

  // X25519 key pair for Diffie-Hellman key exchange
  const keyPair = sodium.crypto_box_keypair();

  return {
    publicKey: Buffer.from(keyPair.publicKey),
    privateKey: Buffer.from(keyPair.privateKey),
  };
}

// ---------------------------------------------------------------------------
// Key storage
// ---------------------------------------------------------------------------

function storeKeys(dir, publicKey, privateKey) {
  // Write base64-encoded keys
  const pubPath = path.join(dir, 'public_key.b64');
  const privPath = path.join(dir, 'private_key.b64');

  fs.writeFileSync(pubPath, publicKey.toString('base64') + '\n', 'utf8');
  fs.writeFileSync(privPath, privateKey.toString('base64') + '\n', 'utf8');

  // Restrict private key permissions: owner read-only
  fs.chmodSync(privPath, 0o400);

  return { pubPath, privPath };
}

// ---------------------------------------------------------------------------
// FalkorDB registration (optional)
// ---------------------------------------------------------------------------

async function registerInGraph(graphName, actorId, publicKeyB64) {
  let falkordb;
  try {
    falkordb = require('falkordb');
  } catch (err) {
    console.error('[graph] falkordb module not available — skipping graph registration.');
    console.error('[graph] Install with: npm install falkordb');
    return false;
  }

  const host = process.env.FALKORDB_HOST || 'localhost';
  const port = parseInt(process.env.FALKORDB_PORT || '6379', 10);

  console.log(`[graph] Connecting to FalkorDB at ${host}:${port}...`);

  let client;
  try {
    client = await falkordb.FalkorDB.connect({ socket: { host, port } });
    const graph = client.selectGraph(graphName);

    const query = `MATCH (a:Actor {handle: $handle}) SET a.public_key = $pubkey RETURN a.handle`;
    const result = await graph.query(query, {
      params: { handle: actorId, pubkey: publicKeyB64 },
    });

    if (result && result.data && result.data.length > 0) {
      console.log(`[graph] Public key registered on Actor node '${actorId}' in graph '${graphName}'.`);
    } else {
      console.warn(`[graph] Warning: Actor node '${actorId}' not found in graph '${graphName}'.`);
      console.warn(`[graph] Key was generated but not registered. Seed the graph first.`);
    }

    await client.close();
    return true;
  } catch (err) {
    console.error(`[graph] Failed to register key in graph: ${err.message}`);
    if (client) {
      try { await client.close(); } catch (_) { /* ignore */ }
    }
    return false;
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const args = parseArgs(process.argv);

  if (args.help) {
    printUsage();
    process.exit(0);
  }

  // Validate required args
  if (!args.actor) {
    console.error('Error: --actor is required.');
    printUsage();
    process.exit(1);
  }
  if (!args.dir) {
    console.error('Error: --dir is required.');
    printUsage();
    process.exit(1);
  }

  const keysDir = path.resolve(args.dir);
  const actor = args.actor;

  console.log(`\n--- generate_actor_keys ---`);
  console.log(`Actor:    ${actor}`);
  console.log(`Keys dir: ${keysDir}`);
  if (args.graph) {
    console.log(`Graph:    ${args.graph}`);
  }
  console.log('');

  // Check if directory already exists
  if (fs.existsSync(keysDir)) {
    const hasKeys = fs.existsSync(path.join(keysDir, 'public_key.b64')) ||
                    fs.existsSync(path.join(keysDir, 'private_key.b64'));
    if (hasKeys && !args.force) {
      console.error(`Error: Keys already exist in ${keysDir}`);
      console.error('Use --force to overwrite existing keys.');
      console.error('WARNING: Overwriting keys will invalidate any existing encrypted data.');
      process.exit(1);
    }
    if (hasKeys && args.force) {
      console.warn('Warning: --force specified. Overwriting existing keys.');
    }
  } else {
    fs.mkdirSync(keysDir, { recursive: true });
    console.log(`Created directory: ${keysDir}`);
  }

  // Generate key pair
  console.log('Generating X25519 key pair...');
  const { publicKey, privateKey } = await generateKeyPair();

  // Store keys
  const { pubPath, privPath } = storeKeys(keysDir, publicKey, privateKey);

  const publicKeyB64 = publicKey.toString('base64');

  console.log('');
  console.log('Keys generated successfully:');
  console.log(`  Public key:  ${pubPath}`);
  console.log(`  Private key: ${privPath} (mode 0400)`);
  console.log('');
  console.log(`  Public key (b64): ${publicKeyB64}`);
  console.log('');

  // Optional: register in graph
  if (args.graph) {
    await registerInGraph(args.graph, actor, publicKeyB64);
  }

  console.log('Done.');
  console.log('');
  console.log('IMPORTANT: private_key.b64 must NEVER be committed to git.');
  console.log('           Ensure **/.keys/private_key.b64 is in .gitignore.');
  console.log('');
}

main().catch((err) => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
