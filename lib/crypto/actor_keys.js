/**
 * Actor Keys — X25519 key pair generation and storage for Mind Protocol actors.
 *
 * Uses libsodium sealed-box-compatible key pairs (crypto_box_keypair).
 * Keys are stored as base64-encoded 32-byte files: public_key.b64 / private_key.b64.
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const fs = require('fs');
const path = require('path');
const sodium = require('libsodium-wrappers');

// --- Constants ---

const PUBLIC_KEY_FILE = 'public_key.b64';
const PRIVATE_KEY_FILE = 'private_key.b64';
const KEY_LENGTH = 32;

// --- Functions ---

/**
 * Generate an X25519 key pair suitable for sealed-box encryption.
 *
 * Must be called after `await sodium.ready`.
 *
 * @returns {Promise<{ publicKey: Buffer, privateKey: Buffer }>} 32-byte key pair
 */
async function generateActorKeyPair() {
  await sodium.ready;

  const kp = sodium.crypto_box_keypair();

  return {
    publicKey: Buffer.from(kp.publicKey),
    privateKey: Buffer.from(kp.privateKey),
  };
}

/**
 * Store an actor key pair to disk as base64-encoded .b64 files.
 *
 * Creates the directory if it does not exist.
 *
 * @param {string} keysDir - Directory to write key files into
 * @param {{ publicKey: Buffer, privateKey: Buffer }} keyPair
 * @returns {Promise<void>}
 */
async function storeActorKeys(keysDir, keyPair) {
  if (!keyPair || !Buffer.isBuffer(keyPair.publicKey) || !Buffer.isBuffer(keyPair.privateKey)) {
    throw new Error('keyPair must contain publicKey and privateKey Buffers');
  }
  if (keyPair.publicKey.length !== KEY_LENGTH) {
    throw new Error(`publicKey must be ${KEY_LENGTH} bytes, got ${keyPair.publicKey.length}`);
  }
  if (keyPair.privateKey.length !== KEY_LENGTH) {
    throw new Error(`privateKey must be ${KEY_LENGTH} bytes, got ${keyPair.privateKey.length}`);
  }

  fs.mkdirSync(keysDir, { recursive: true });

  const pubPath = path.join(keysDir, PUBLIC_KEY_FILE);
  const privPath = path.join(keysDir, PRIVATE_KEY_FILE);

  fs.writeFileSync(pubPath, keyPair.publicKey.toString('base64'), 'utf8');
  fs.writeFileSync(privPath, keyPair.privateKey.toString('base64'), 'utf8');
}

/**
 * Load an actor key pair from base64-encoded .b64 files on disk.
 *
 * @param {string} keysDir - Directory containing public_key.b64 and private_key.b64
 * @returns {Promise<{ publicKey: Buffer, privateKey: Buffer }>} 32-byte key pair
 */
async function loadActorKeys(keysDir) {
  const pubPath = path.join(keysDir, PUBLIC_KEY_FILE);
  const privPath = path.join(keysDir, PRIVATE_KEY_FILE);

  if (!fs.existsSync(pubPath)) {
    throw new Error(`Public key file not found: ${pubPath}`);
  }
  if (!fs.existsSync(privPath)) {
    throw new Error(`Private key file not found: ${privPath}`);
  }

  const pubB64 = fs.readFileSync(pubPath, 'utf8').trim();
  const privB64 = fs.readFileSync(privPath, 'utf8').trim();

  const publicKey = Buffer.from(pubB64, 'base64');
  const privateKey = Buffer.from(privB64, 'base64');

  if (publicKey.length !== KEY_LENGTH) {
    throw new Error(`Invalid public key length: expected ${KEY_LENGTH}, got ${publicKey.length}`);
  }
  if (privateKey.length !== KEY_LENGTH) {
    throw new Error(`Invalid private key length: expected ${KEY_LENGTH}, got ${privateKey.length}`);
  }

  return { publicKey, privateKey };
}

// --- Exports ---

module.exports = {
  PUBLIC_KEY_FILE,
  PRIVATE_KEY_FILE,
  KEY_LENGTH,
  generateActorKeyPair,
  storeActorKeys,
  loadActorKeys,
};
