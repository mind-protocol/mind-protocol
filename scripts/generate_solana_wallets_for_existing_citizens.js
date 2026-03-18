#!/usr/bin/env node

/**
 * generate_solana_wallets_for_existing_citizens.js
 *
 * Generates Solana Ed25519 wallets for citizens with accessible endpoints.
 *
 * Flow (per citizen):
 *   1. Check endpoint accessibility (health check on citizen's home server)
 *   2. Generate Ed25519 keypair (Solana wallet)
 *   3. Store private key on persistent volume (.keys/solana_private_key.json)
 *   4. Register public key (wallet address) in L4 registry (Neo4j)
 *      as a Thing node (type="wallet") linked from the citizen's Actor node
 *
 * Architecture:
 *   - Private keys NEVER leave the persistent volume (Render disk)
 *   - Public keys are registered in L4 Neo4j (same pattern as citizen_registration_crud_operations.py)
 *   - Endpoint check verifies the citizen's home server is alive before wallet creation
 *   - Same keypair used for $MIND transactions AND Space content decryption
 *
 * Usage:
 *   node scripts/generate_solana_wallets_for_existing_citizens.js \
 *     --citizens-dir /data/citizens/ \
 *     --home-url https://mind-home.onrender.com
 *
 *   # Dry run:
 *   node scripts/generate_solana_wallets_for_existing_citizens.js \
 *     --citizens-dir /data/citizens/ --dry-run
 *
 *   # Single citizen:
 *   node scripts/generate_solana_wallets_for_existing_citizens.js \
 *     --citizens-dir /data/citizens/ --citizen forge --home-url https://mind-home.onrender.com
 */

'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { Keypair } = require('@solana/web3.js');

// ---------------------------------------------------------------------------
// CLI arg parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--citizens-dir' && argv[i + 1]) {
      args.citizensDir = argv[++i];
    } else if (arg === '--citizen' && argv[i + 1]) {
      args.singleCitizen = argv[++i];
    } else if (arg === '--home-url' && argv[i + 1]) {
      args.homeUrl = argv[++i];
    } else if (arg === '--dry-run') {
      args.dryRun = true;
    } else if (arg === '--force') {
      args.force = true;
    } else if (arg === '--skip-endpoint-check') {
      args.skipEndpointCheck = true;
    } else if (arg === '--help' || arg === '-h') {
      args.help = true;
    }
  }
  return args;
}

function printUsage() {
  console.log(`
Usage:
  node scripts/generate_solana_wallets_for_existing_citizens.js \\
    --citizens-dir <path>          Path to citizens on persistent volume     [required]
    [--home-url <url>]             Home server URL for endpoint checks       [optional]
    [--citizen <handle>]           Single citizen to process                 [optional]
    [--dry-run]                    Show what would happen, don't write       [optional]
    [--force]                      Overwrite existing Solana wallet          [optional]
    [--skip-endpoint-check]        Skip health check verification           [optional]
    [--help]                       Show this message

CRITICAL: --citizens-dir must point to the Render persistent volume, NOT a git repo.

Flow per citizen:
  1. Check endpoint is accessible (GET /health or /api/info)
  2. Generate Ed25519 keypair (Solana wallet)
  3. Store private key in {citizens-dir}/{handle}/.keys/solana_private_key.json
  4. Register wallet address in L4 Neo4j registry (Thing node, type="wallet")
`);
}

// ---------------------------------------------------------------------------
// Citizen discovery
// ---------------------------------------------------------------------------

function discoverCitizens(citizensDir, singleCitizen) {
  if (singleCitizen) {
    const citizenDir = path.join(citizensDir, singleCitizen);
    if (!fs.existsSync(citizenDir)) {
      console.error(`Error: Citizen directory not found: ${citizenDir}`);
      process.exit(1);
    }
    return [{ handle: singleCitizen, dir: citizenDir, keysDir: path.join(citizenDir, '.keys') }];
  }

  const entries = fs.readdirSync(citizensDir, { withFileTypes: true });
  return entries
    .filter(e => e.isDirectory() && !e.name.startsWith('.') && e.name !== 'node_modules')
    .map(e => ({
      handle: e.name,
      dir: path.join(citizensDir, e.name),
      keysDir: path.join(citizensDir, e.name, '.keys'),
    }))
    .sort((a, b) => a.handle.localeCompare(b.handle));
}

// ---------------------------------------------------------------------------
// Endpoint health check
// ---------------------------------------------------------------------------

function httpGet(url, timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    const req = mod.get(url, { timeout: timeoutMs }, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => resolve({ status: res.statusCode, data }));
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

async function checkEndpointAccessible(homeUrl) {
  if (!homeUrl) return { accessible: true, skipped: true };

  try {
    const healthUrl = homeUrl.replace(/\/$/, '') + '/health';
    const resp = await httpGet(healthUrl, 10000);
    if (resp.status === 200) {
      const body = JSON.parse(resp.data);
      return {
        accessible: true,
        status: body.status,
        version: body.version,
        citizenCount: body.citizen_count,
      };
    }
    return { accessible: false, reason: `HTTP ${resp.status}` };
  } catch (err) {
    return { accessible: false, reason: err.message };
  }
}

// ---------------------------------------------------------------------------
// Solana wallet generation
// ---------------------------------------------------------------------------

function generateSolanaKeypair() {
  const keypair = Keypair.generate();
  return {
    publicKey: keypair.publicKey.toBase58(),
    secretKey: Array.from(keypair.secretKey), // 64 bytes as JSON array (Solana CLI format)
  };
}

function storeWallet(keysDir, secretKey, dryRun) {
  const walletPath = path.join(keysDir, 'solana_private_key.json');

  if (dryRun) {
    console.log(`    [dry-run] Would write: ${walletPath}`);
    return walletPath;
  }

  if (!fs.existsSync(keysDir)) {
    fs.mkdirSync(keysDir, { recursive: true });
  }

  // Remove existing file if present (force mode — file is 0400)
  if (fs.existsSync(walletPath)) {
    fs.chmodSync(walletPath, 0o600);
    fs.unlinkSync(walletPath);
  }

  // Write in Solana CLI format: JSON array of 64 bytes
  fs.writeFileSync(walletPath, JSON.stringify(secretKey) + '\n', 'utf8');
  fs.chmodSync(walletPath, 0o400);

  return walletPath;
}

// ---------------------------------------------------------------------------
// L4 Neo4j registration
// ---------------------------------------------------------------------------

async function registerWalletInL4(citizenHandle, walletAddress, dryRun) {
  // L4 registry uses Neo4j — connect via env vars
  const uri = process.env.NEO4J_URI;
  const user = process.env.NEO4J_USER || 'neo4j';
  const password = process.env.NEO4J_PASSWORD;
  const database = process.env.NEO4J_DATABASE || 'neo4j';

  if (!uri || !password) {
    console.log(`    [l4] Neo4j not configured (NEO4J_URI/NEO4J_PASSWORD) — skipping L4 registration`);
    return false;
  }

  if (dryRun) {
    console.log(`    [dry-run] Would register ${walletAddress} in L4 Neo4j for ${citizenHandle}`);
    return true;
  }

  let neo4j, driver;
  try {
    neo4j = require('neo4j-driver');
  } catch (err) {
    console.log(`    [l4] neo4j-driver not installed — skipping L4 registration`);
    console.log(`    [l4] Install with: npm install neo4j-driver`);
    return false;
  }

  try {
    driver = neo4j.driver(uri, neo4j.auth.basic(user, password));
    const session = driver.session({ database });

    // Pattern from citizen_registration_crud_operations.py:
    // Wallet is a Thing node (type="wallet") linked from Actor
    // Uses MERGE for idempotency
    const walletNodeId = `${citizenHandle}_wallet`;
    const linkId = `${citizenHandle}_has_wallet`;

    await session.run(`
      MERGE (a {id: $citizenId})
      MERGE (w {id: $walletId})
      SET w.node_type = 'thing',
          w.type = 'wallet',
          w.name = $walletName,
          w.content = $walletAddress,
          w.synthesis = $synthesis,
          w.uri = $uri
      MERGE (a)-[r:link {id: $linkId}]->(w)
      SET r.hierarchy = 1.0,
          r.permanence = 0.8
      RETURN a.id, w.content
    `, {
      citizenId: citizenHandle,
      walletId: walletNodeId,
      walletName: `Wallet ${walletAddress.slice(0, 8)}...`,
      walletAddress: walletAddress,
      synthesis: `Solana wallet for citizen ${citizenHandle}`,
      uri: `solana:${walletAddress}`,
      linkId: linkId,
    });

    await session.close();
    await driver.close();
    return true;
  } catch (err) {
    console.error(`    [l4] Neo4j error: ${err.message}`);
    if (driver) try { await driver.close(); } catch (e) { console.debug('Neo4j driver close error:', e?.message || e); }
    return false;
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const args = parseArgs(process.argv);

  if (args.help) { printUsage(); process.exit(0); }
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

  console.log(`\n--- generate_solana_wallets_for_existing_citizens ---`);
  console.log(`Citizens dir: ${citizensDir}`);
  if (args.homeUrl) console.log(`Home URL:     ${args.homeUrl}`);
  if (args.dryRun) console.log(`Mode:         DRY RUN (no writes)`);
  console.log('');

  // Step 1: Check endpoint if provided
  if (args.homeUrl && !args.skipEndpointCheck) {
    console.log(`Checking endpoint: ${args.homeUrl}`);
    const check = await checkEndpointAccessible(args.homeUrl);
    if (!check.accessible) {
      console.error(`\nEndpoint not accessible: ${check.reason}`);
      console.error(`Cannot generate wallets for citizens on an unreachable server.`);
      console.error(`Use --skip-endpoint-check to override.`);
      process.exit(1);
    }
    console.log(`  Status: ${check.status || 'ok'}`);
    if (check.version) console.log(`  Version: ${check.version}`);
    console.log('');
  }

  // Discover citizens
  const citizens = discoverCitizens(citizensDir, args.singleCitizen);
  console.log(`Found ${citizens.length} citizen(s)\n`);

  if (citizens.length === 0) {
    console.log('No citizens found.');
    process.exit(0);
  }

  // Process each citizen
  const results = { generated: [], skipped: [], failed: [] };

  for (const citizen of citizens) {
    // Check if already has wallet
    const walletPath = path.join(citizen.keysDir, 'solana_private_key.json');
    const hasWallet = fs.existsSync(walletPath);

    if (hasWallet && !args.force) {
      results.skipped.push(citizen.handle);
      continue;
    }

    // Generate keypair
    const { publicKey, secretKey } = generateSolanaKeypair();

    // Store on persistent volume
    storeWallet(citizen.keysDir, secretKey, args.dryRun);

    // Register in L4 Neo4j
    const registered = await registerWalletInL4(citizen.handle, publicKey, args.dryRun);

    if (!args.dryRun) {
      console.log(`  ${citizen.handle}: ${publicKey}${registered ? ' [L4 registered]' : ' [local only]'}`);
    } else {
      console.log(`  ${citizen.handle}: ${publicKey} [dry-run]`);
    }

    results.generated.push({ handle: citizen.handle, wallet: publicKey, l4: registered });
  }

  // Summary
  console.log(`\n--- Summary ---`);
  console.log(`  Generated: ${results.generated.length}`);
  console.log(`  Skipped:   ${results.skipped.length} (already have wallets)`);

  if (!args.dryRun && results.generated.length > 0) {
    console.log(`\nCRITICAL: Private keys are on the persistent volume ONLY.`);
    console.log(`          NEVER copy them to a git repo.`);
    console.log(`\nNext steps:`);
    console.log(`  1. Fund wallets with devnet SOL for transaction fees`);
    console.log(`  2. Trigger M1 mint (10,000 $MIND) for each citizen`);
  }
  console.log('\nDone.');
}

main().catch((err) => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
