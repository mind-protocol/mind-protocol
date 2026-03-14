/**
 * Mind Protocol — Space Key Cache (JavaScript)
 *
 * In-memory LRU cache for decrypted space keys, keyed on (actorId, spaceId).
 * Avoids repeated sealed-box decryption on every private-Space read.
 *
 * - Max 100 entries
 * - 5-minute TTL per entry
 * - Evicts oldest on overflow
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const DEFAULT_MAX_ENTRIES = 100;
const DEFAULT_TTL_MS = 5 * 60 * 1000; // 5 minutes

class SpaceKeyCache {
  /**
   * @param {object} [opts]
   * @param {number} [opts.maxEntries=100]
   * @param {number} [opts.ttlMs=300000]  TTL in milliseconds
   * @param {function} [opts.now]         Clock function (for testing)
   */
  constructor(opts = {}) {
    this._maxEntries = opts.maxEntries ?? DEFAULT_MAX_ENTRIES;
    this._ttlMs = opts.ttlMs ?? DEFAULT_TTL_MS;
    this._now = opts.now ?? Date.now;

    // Map preserves insertion order — we rely on that for LRU eviction.
    // Key: "actorId\0spaceId"  Value: { spaceKey: Buffer, insertedAt: number }
    this._cache = new Map();
  }

  // ------------------------------------------------------------------
  // Internal helpers
  // ------------------------------------------------------------------

  _key(actorId, spaceId) {
    return `${actorId}\0${spaceId}`;
  }

  _spaceIdFromKey(compositeKey) {
    return compositeKey.split('\0')[1];
  }

  // ------------------------------------------------------------------
  // Public API
  // ------------------------------------------------------------------

  /**
   * @param {string} actorId
   * @param {string} spaceId
   * @returns {Buffer|null}
   */
  get(actorId, spaceId) {
    const k = this._key(actorId, spaceId);
    const entry = this._cache.get(k);
    if (!entry) return null;

    if (this._now() - entry.insertedAt >= this._ttlMs) {
      // Expired
      this._cache.delete(k);
      return null;
    }

    // Move to end (most-recently used)
    this._cache.delete(k);
    this._cache.set(k, entry);

    return entry.spaceKey;
  }

  /**
   * @param {string} actorId
   * @param {string} spaceId
   * @param {Buffer} spaceKey
   */
  put(actorId, spaceId, spaceKey) {
    const k = this._key(actorId, spaceId);

    // Remove existing entry if present (so insertion order resets)
    if (this._cache.has(k)) {
      this._cache.delete(k);
    }

    // Evict oldest while at capacity
    while (this._cache.size >= this._maxEntries) {
      const oldest = this._cache.keys().next().value;
      this._cache.delete(oldest);
    }

    this._cache.set(k, {
      spaceKey,
      insertedAt: this._now(),
    });
  }

  /**
   * Remove ALL entries for a given spaceId (used on key rotation).
   * @param {string} spaceId
   */
  invalidate(spaceId) {
    for (const k of [...this._cache.keys()]) {
      if (this._spaceIdFromKey(k) === spaceId) {
        this._cache.delete(k);
      }
    }
  }

  /** Remove all entries. */
  clear() {
    this._cache.clear();
  }

  /** Current number of entries (useful for tests). */
  get size() {
    return this._cache.size;
  }
}

module.exports = { SpaceKeyCache };
