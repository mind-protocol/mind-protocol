/**
 * Space Key — AES-256-GCM encryption for Mind Protocol spaces.
 *
 * Spaces are encrypted with a symmetric key. Content is stored as
 * self-contained ciphertext strings: "base64(iv):base64(tag):base64(ciphertext)".
 * IV is regenerated on every encrypt call — never reused.
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const crypto = require('crypto');

// --- Constants ---

const ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 12;   // 96-bit IV for GCM (NIST recommended)
const TAG_LENGTH = 16;  // 128-bit authentication tag
const KEY_LENGTH = 32;  // 256-bit key

// --- Functions ---

/**
 * Generate a cryptographically random space key.
 * @returns {{ key: Buffer }} 32-byte symmetric key
 */
function generateSpaceKey() {
  return { key: crypto.randomBytes(KEY_LENGTH) };
}

/**
 * Encrypt plaintext content with a space key (AES-256-GCM).
 *
 * Output format: "base64(iv):base64(tag):base64(ciphertext)"
 * A fresh IV is generated on every call — never reused.
 *
 * @param {string} plaintext - The content to encrypt
 * @param {Buffer} key - 32-byte space key
 * @returns {string} Colon-separated base64 ciphertext string
 */
function encryptContent(plaintext, key) {
  if (!Buffer.isBuffer(key) || key.length !== KEY_LENGTH) {
    throw new Error(`Space key must be a ${KEY_LENGTH}-byte Buffer`);
  }
  if (typeof plaintext !== 'string') {
    throw new Error('Plaintext must be a string');
  }

  const iv = crypto.randomBytes(IV_LENGTH);
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv, { authTagLength: TAG_LENGTH });

  const encrypted = Buffer.concat([
    cipher.update(plaintext, 'utf8'),
    cipher.final(),
  ]);

  const tag = cipher.getAuthTag();

  return [
    iv.toString('base64'),
    tag.toString('base64'),
    encrypted.toString('base64'),
  ].join(':');
}

/**
 * Decrypt a ciphertext string produced by encryptContent.
 *
 * @param {string} encrypted - "base64(iv):base64(tag):base64(ciphertext)"
 * @param {Buffer} key - 32-byte space key
 * @returns {string} Decrypted plaintext
 */
function decryptContent(encrypted, key) {
  if (!Buffer.isBuffer(key) || key.length !== KEY_LENGTH) {
    throw new Error(`Space key must be a ${KEY_LENGTH}-byte Buffer`);
  }
  if (typeof encrypted !== 'string') {
    throw new Error('Encrypted content must be a string');
  }

  const parts = encrypted.split(':');
  if (parts.length !== 3) {
    throw new Error('Invalid ciphertext format — expected "iv:tag:ciphertext"');
  }

  const iv = Buffer.from(parts[0], 'base64');
  const tag = Buffer.from(parts[1], 'base64');
  const ciphertext = Buffer.from(parts[2], 'base64');

  if (iv.length !== IV_LENGTH) {
    throw new Error(`Invalid IV length: expected ${IV_LENGTH}, got ${iv.length}`);
  }
  if (tag.length !== TAG_LENGTH) {
    throw new Error(`Invalid tag length: expected ${TAG_LENGTH}, got ${tag.length}`);
  }

  const decipher = crypto.createDecipheriv(ALGORITHM, key, iv, { authTagLength: TAG_LENGTH });
  decipher.setAuthTag(tag);

  const decrypted = Buffer.concat([
    decipher.update(ciphertext),
    decipher.final(),
  ]);

  return decrypted.toString('utf8');
}

/**
 * Detect whether a string looks like encrypted content (the colon-separated base64 format).
 *
 * @param {string} content - String to test
 * @returns {boolean} true if the string matches the ciphertext format
 */
function isEncrypted(content) {
  if (typeof content !== 'string') return false;
  // Three base64 segments separated by colons
  // Base64 charset: A-Z a-z 0-9 + / =
  const BASE64 = '[A-Za-z0-9+/]+=*';
  const pattern = new RegExp(`^${BASE64}:${BASE64}:${BASE64}$`);
  return pattern.test(content);
}

// --- Exports ---

module.exports = {
  ALGORITHM,
  IV_LENGTH,
  TAG_LENGTH,
  KEY_LENGTH,
  generateSpaceKey,
  encryptContent,
  decryptContent,
  isEncrypted,
};
