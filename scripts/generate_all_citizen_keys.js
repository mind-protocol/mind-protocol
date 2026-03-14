#!/usr/bin/env node

/**
 * generate_all_citizen_keys.js — Batch key generation for all Mind Protocol citizens.
 *
 * Usage:
 *   node scripts/generate_all_citizen_keys.js --citizens-dir /var/data/citizens/
 *   node scripts/generate_all_citizen_keys.js --citizens-dir /var/data/citizens/ --graph venezia
 *
 * CRITICAL: --citizens-dir must point to the Render persistent volume, NEVER to a git repo.
 *           Repos are public. Keys on persistent storage only.
 *
 * Scans a citizens directory for subdirectories (each is a citizen).
 * Generates X25519 keys for each citizen that doesn't have .keys/ yet.
 * Optionally registers all public keys in the FalkorDB graph.
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
    if (arg === '--citizens-dir' && argv[i + 1]) {
      args.citizensDir = argv[++i];
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
  node scripts/generate_all_citizen_keys.js --citizens-dir <path> [--graph <graph-name>] [--force]

Options:
  --citizens-dir   Path to citizens directory (contains one subdirectory per citizen)  [required]
  --graph          FalkorDB graph name — registers public keys on Actor nodes          [optional]
  --force          Overwrite existing keys for citizens that already have them          [optional]
  --help           Show this message
`);
}

// ---------------------------------------------------------------------------
// Key generation (libsodium X25519)
// ---------------------------------------------------------------------------

async function generateKeyPair() {
  const sodium = require('libsodium-wrappers');
  await sodium.ready;

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
  const pubPath = path.join(dir, 'public_key.b64');
  const privPath = path.join(dir, 'private_key.b64');

  fs.writeFileSync(pubPath, publicKey.toString('base64') + '\n', 'utf8');
  fs.writeFileSync(privPath, privateKey.toString('base64') + '\n', 'utf8');

  // Restrict private key permissions: owner read-only
  fs.chmodSync(privPath, 0o400);

  return { pubPath, privPath };
}

// ---------------------------------------------------------------------------
// Citizen discovery
// ---------------------------------------------------------------------------

function discoverCitizens(citizensDir) {
  const entries = fs.readdirSync(citizensDir, { withFileTypes: true });
  const citizens = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    // Skip hidden directories and common non-citizen dirs
    if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;

    citizens.push({
      handle: entry.name,
      dir: path.join(citizensDir, entry.name),
      keysDir: path.join(citizensDir, entry.name, '.keys'),
    });
  }

  return citizens.sort((a, b) => a.handle.localeCompare(b.handle));
}

// ---------------------------------------------------------------------------
// FalkorDB batch registration (optional)
// ---------------------------------------------------------------------------

async function registerAllInGraph(graphName, keyMap) {
  if (keyMap.length === 0) return;

  let falkordb;
  try {
    falkordb = require('falkordb');
  } catch (err) {
    console.error('\n[graph] falkordb module not available — skipping graph registration.');
    console.error('[graph] Install with: npm install falkordb');
    return;
  }

  const host = process.env.FALKORDB_HOST || 'localhost';
  const port = parseInt(process.env.FALKORDB_PORT || '6379', 10);

  console.log(`\n[graph] Connecting to FalkorDB at ${host}:${port}...`);

  let client;
  try {
    client = await falkordb.FalkorDB.connect({ socket: { host, port } });
    const graph = client.selectGraph(graphName);

    let registered = 0;
    let notFound = 0;

    for (const { handle, publicKeyB64 } of keyMap) {
      try {
        const query = `MATCH (a:Actor {handle: $handle}) SET a.public_key = $pubkey RETURN a.handle`;
        const result = await graph.query(query, {
          params: { handle, pubkey: publicKeyB64 },
        });

        if (result && result.data && result.data.length > 0) {
          registered++;
        } else {
          console.warn(`  [graph] Actor node '${handle}' not found in graph.`);
          notFound++;
        }
      } catch (err) {
        console.error(`  [graph] Error registering '${handle}': ${err.message}`);
      }
    }

    console.log(`[graph] Registered ${registered} public keys in graph '${graphName}'.`);
    if (notFound > 0) {
      console.log(`[graph] ${notFound} actors not found in graph (seed first).`);
    }

    await client.close();
  } catch (err) {
    console.error(`[graph] Failed to connect: ${err.message}`);
    if (client) {
      try { await client.close(); } catch (_) { /* ignore */ }
    }
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

  if (!args.citizensDir) {
    console.error('Error: --citizens-dir is required.');
    printUsage();
    process.exit(1);
  }

  const citizensDir = path.resolve(args.citizensDir);

  if (!fs.existsSync(citizensDir)) {
    console.error(`Error: Citizens directory does not exist: ${citizensDir}`);
    process.exit(1);
  }

  console.log(`\n--- generate_all_citizen_keys ---`);
  console.log(`Citizens dir: ${citizensDir}`);
  if (args.graph) {
    console.log(`Graph:        ${args.graph}`);
  }
  console.log('');

  // Discover citizens
  const citizens = discoverCitizens(citizensDir);
  console.log(`Found ${citizens.length} citizen(s): ${citizens.map(c => c.handle).join(', ')}`);
  console.log('');

  if (citizens.length === 0) {
    console.log('No citizens found. Nothing to do.');
    process.exit(0);
  }

  // Generate keys for each citizen
  const generated = [];
  const skipped = [];
  const keyMap = []; // for graph registration

  for (const citizen of citizens) {
    const hasExistingKeys = fs.existsSync(path.join(citizen.keysDir, 'public_key.b64')) ||
                            fs.existsSync(path.join(citizen.keysDir, 'private_key.b64'));

    if (hasExistingKeys && !args.force) {
      console.log(`  [skip] ${citizen.handle} — keys already exist (use --force to overwrite)`);
      skipped.push(citizen.handle);

      // Still include existing public key for graph registration
      const existingPubPath = path.join(citizen.keysDir, 'public_key.b64');
      if (fs.existsSync(existingPubPath)) {
        const pubKeyB64 = fs.readFileSync(existingPubPath, 'utf8').trim();
        keyMap.push({ handle: citizen.handle, publicKeyB64: pubKeyB64 });
      }
      continue;
    }

    if (hasExistingKeys && args.force) {
      console.log(`  [force] ${citizen.handle} — overwriting existing keys`);
    }

    // Create .keys/ directory if needed
    if (!fs.existsSync(citizen.keysDir)) {
      fs.mkdirSync(citizen.keysDir, { recursive: true });
    }

    // Generate and store
    const { publicKey, privateKey } = await generateKeyPair();
    storeKeys(citizen.keysDir, publicKey, privateKey);

    const publicKeyB64 = publicKey.toString('base64');
    keyMap.push({ handle: citizen.handle, publicKeyB64 });
    generated.push(citizen.handle);

    console.log(`  [new]  ${citizen.handle} — keys generated`);
  }

  console.log('');
  console.log(`Summary: ${generated.length} generated, ${skipped.length} skipped`);

  // Optional: register in graph
  if (args.graph && keyMap.length > 0) {
    await registerAllInGraph(args.graph, keyMap);
  }

  console.log('');
  console.log('CRITICAL: Keys must ONLY exist on the Render persistent volume.');
  console.log('          NEVER write keys to a git repo directory — repos are public.');
  console.log('');
  console.log('Done.');
}

main().catch((err) => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
