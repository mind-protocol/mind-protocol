/**
 * Key Exchange — Sealed-box encryption for distributing space keys to actors.
 *
 * Uses libsodium sealed boxes (crypto_box_seal / crypto_box_seal_open).
 * Sealed boxes provide anonymous sender encryption — only the recipient
 * can decrypt, and the sender's identity is not revealed.
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const sodium = require('libsodium-wrappers');

// --- Functions ---

/**
 * Encrypt a space key for a specific actor using their public key.
 *
 * Uses a sealed box — the sender is anonymous. Output is a single
 * opaque base64 string (NOT nonce:ciphertext).
 *
 * @param {Buffer} spaceKey - 32-byte space key to wrap
 * @param {Buffer} actorPublicKey - 32-byte X25519 public key of the recipient
 * @returns {Promise<string>} Base64-encoded sealed box
 */
async function encryptSpaceKeyForActor(spaceKey, actorPublicKey) {
  await sodium.ready;

  if (!Buffer.isBuffer(spaceKey) || spaceKey.length !== 32) {
    throw new Error('spaceKey must be a 32-byte Buffer');
  }
  if (!Buffer.isBuffer(actorPublicKey) || actorPublicKey.length !== 32) {
    throw new Error('actorPublicKey must be a 32-byte Buffer');
  }

  const sealed = sodium.crypto_box_seal(
    new Uint8Array(spaceKey),
    new Uint8Array(actorPublicKey),
  );

  return Buffer.from(sealed).toString('base64');
}

/**
 * Decrypt a sealed-box-encrypted space key using the actor's key pair.
 *
 * Requires BOTH public and private key — libsodium's crypto_box_seal_open
 * needs the full key pair for decryption.
 *
 * @param {string} encryptedKey - Base64-encoded sealed box
 * @param {Buffer} actorPublicKey - 32-byte X25519 public key
 * @param {Buffer} actorPrivateKey - 32-byte X25519 private key
 * @returns {Promise<Buffer>} 32-byte space key
 */
async function decryptSpaceKeyForActor(encryptedKey, actorPublicKey, actorPrivateKey) {
  await sodium.ready;

  if (typeof encryptedKey !== 'string') {
    throw new Error('encryptedKey must be a base64 string');
  }
  if (!Buffer.isBuffer(actorPublicKey) || actorPublicKey.length !== 32) {
    throw new Error('actorPublicKey must be a 32-byte Buffer');
  }
  if (!Buffer.isBuffer(actorPrivateKey) || actorPrivateKey.length !== 32) {
    throw new Error('actorPrivateKey must be a 32-byte Buffer');
  }

  const sealed = new Uint8Array(Buffer.from(encryptedKey, 'base64'));

  const opened = sodium.crypto_box_seal_open(
    sealed,
    new Uint8Array(actorPublicKey),
    new Uint8Array(actorPrivateKey),
  );

  if (!opened) {
    throw new Error('Failed to decrypt space key — invalid key pair or corrupted ciphertext');
  }

  return Buffer.from(opened);
}

// --- Exports ---

module.exports = {
  encryptSpaceKeyForActor,
  decryptSpaceKeyForActor,
};
