/**
 * Mind Protocol Crypto — facade re-exporting all crypto modules.
 *
 * Usage:
 *   const crypto = require('./lib/crypto');
 *   const { key } = crypto.generateSpaceKey();
 *   const ct = crypto.encryptContent('hello', key);
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const spaceKey = require('./space_key');
const actorKeys = require('./actor_keys');
const keyExchange = require('./key_exchange');
const { SpaceKeyCache } = require('./key_cache');

module.exports = {
  // space_key.js
  ...spaceKey,
  // actor_keys.js
  ...actorKeys,
  // key_exchange.js
  ...keyExchange,
  // key_cache.js
  SpaceKeyCache,
};
