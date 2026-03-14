/**
 * Mind Protocol — Space Key Cache tests (JavaScript).
 *
 * Tests TTL expiry, LRU eviction, invalidation, and basic get/put.
 *
 * Run: node tests/crypto/test_key_cache.js
 *
 * Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
 */

'use strict';

const crypto = require('crypto');
const { SpaceKeyCache } = require('../../lib/crypto/key_cache');

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

function randomKey() {
  return crypto.randomBytes(32);
}

// ---------------------------------------------------------------------------
// Basic get / put
// ---------------------------------------------------------------------------

function testGetReturnsNullOnEmptyCache() {
  console.log('\n--- Basic get / put ---');

  const cache = new SpaceKeyCache();
  assert(cache.get('actor-1', 'space-1') === null, 'get on empty cache returns null');
}

function testPutThenGet() {
  const cache = new SpaceKeyCache();
  const sk = randomKey();
  cache.put('actor-1', 'space-1', sk);
  const result = cache.get('actor-1', 'space-1');
  assert(result !== null && result.equals(sk), 'put then get returns same key');
}

function testDifferentActorSameSpace() {
  const cache = new SpaceKeyCache();
  const sk1 = randomKey();
  const sk2 = randomKey();
  cache.put('actor-1', 'space-1', sk1);
  cache.put('actor-2', 'space-1', sk2);
  assert(cache.get('actor-1', 'space-1').equals(sk1), 'actor-1 gets sk1');
  assert(cache.get('actor-2', 'space-1').equals(sk2), 'actor-2 gets sk2');
}

function testOverwriteExistingEntry() {
  const cache = new SpaceKeyCache();
  const sk1 = randomKey();
  const sk2 = randomKey();
  cache.put('actor-1', 'space-1', sk1);
  cache.put('actor-1', 'space-1', sk2);
  assert(cache.get('actor-1', 'space-1').equals(sk2), 'overwrite returns new key');
  assert(cache.size === 1, 'overwrite does not increase size');
}

// ---------------------------------------------------------------------------
// TTL expiry
// ---------------------------------------------------------------------------

function testTtlExpiry() {
  console.log('\n--- TTL expiry ---');

  let clock = 1000;
  const cache = new SpaceKeyCache({ ttlMs: 100, now: () => clock });
  const sk = randomKey();

  cache.put('actor-1', 'space-1', sk);
  assert(cache.get('actor-1', 'space-1').equals(sk), 'before TTL: key is present');

  // Advance clock past TTL
  clock += 100;

  assert(cache.get('actor-1', 'space-1') === null, 'after TTL: key is expired');
  assert(cache.size === 0, 'expired entry is removed');
}

function testTtlNotExpiredYet() {
  let clock = 1000;
  const cache = new SpaceKeyCache({ ttlMs: 10000, now: () => clock });
  const sk = randomKey();

  cache.put('actor-1', 'space-1', sk);
  clock += 5000; // halfway through TTL
  assert(cache.get('actor-1', 'space-1').equals(sk), 'before TTL expiry: key still present');
}

// ---------------------------------------------------------------------------
// LRU eviction
// ---------------------------------------------------------------------------

function testLruEvictionAtCapacity() {
  console.log('\n--- LRU eviction ---');

  const cache = new SpaceKeyCache({ maxEntries: 3 });
  const keys = [];
  for (let i = 0; i < 3; i++) {
    const k = randomKey();
    keys.push(k);
    cache.put(`actor-${i}`, 'space-0', k);
  }

  assert(cache.size === 3, 'cache is at capacity');

  // Adding a 4th entry should evict actor-0
  const newKey = randomKey();
  cache.put('actor-new', 'space-0', newKey);

  assert(cache.size === 3, 'cache stays at max capacity');
  assert(cache.get('actor-0', 'space-0') === null, 'oldest entry (actor-0) is evicted');
  assert(cache.get('actor-1', 'space-0').equals(keys[1]), 'actor-1 still present');
  assert(cache.get('actor-2', 'space-0').equals(keys[2]), 'actor-2 still present');
  assert(cache.get('actor-new', 'space-0').equals(newKey), 'new entry is present');
}

function testLruAccessRefreshesOrder() {
  const cache = new SpaceKeyCache({ maxEntries: 3 });
  const sk0 = randomKey();
  const sk1 = randomKey();
  const sk2 = randomKey();

  cache.put('a0', 's', sk0);
  cache.put('a1', 's', sk1);
  cache.put('a2', 's', sk2);

  // Access a0 — moves it to the end (most-recently used)
  cache.get('a0', 's');

  // Insert new entry — should evict a1 (now the oldest)
  const sk3 = randomKey();
  cache.put('a3', 's', sk3);

  assert(cache.get('a0', 's') !== null && cache.get('a0', 's').equals(sk0),
    'a0 still present after access refresh');
  assert(cache.get('a1', 's') === null, 'a1 evicted (was oldest after a0 refreshed)');
  assert(cache.get('a2', 's').equals(sk2), 'a2 still present');
  assert(cache.get('a3', 's').equals(sk3), 'a3 present');
}

// ---------------------------------------------------------------------------
// Invalidation
// ---------------------------------------------------------------------------

function testInvalidateRemovesAllEntriesForSpace() {
  console.log('\n--- Invalidation ---');

  const cache = new SpaceKeyCache();
  cache.put('actor-1', 'space-A', randomKey());
  cache.put('actor-2', 'space-A', randomKey());
  cache.put('actor-1', 'space-B', randomKey());

  assert(cache.size === 3, 'three entries before invalidation');

  cache.invalidate('space-A');

  assert(cache.get('actor-1', 'space-A') === null, 'actor-1/space-A removed');
  assert(cache.get('actor-2', 'space-A') === null, 'actor-2/space-A removed');
  assert(cache.get('actor-1', 'space-B') !== null, 'actor-1/space-B still present');
  assert(cache.size === 1, 'one entry remaining');
}

function testInvalidateNonexistentSpaceIsNoop() {
  const cache = new SpaceKeyCache();
  cache.put('actor-1', 'space-1', randomKey());
  cache.invalidate('space-999');
  assert(cache.size === 1, 'invalidate of non-existent space is a no-op');
}

// ---------------------------------------------------------------------------
// Clear
// ---------------------------------------------------------------------------

function testClear() {
  console.log('\n--- Clear ---');

  const cache = new SpaceKeyCache();
  for (let i = 0; i < 10; i++) {
    cache.put(`actor-${i}`, `space-${i}`, randomKey());
  }
  assert(cache.size === 10, '10 entries before clear');

  cache.clear();
  assert(cache.size === 0, '0 entries after clear');
}

// ---------------------------------------------------------------------------
// Export via index.js
// ---------------------------------------------------------------------------

function testExportedFromIndex() {
  console.log('\n--- Export from index.js ---');

  const cryptoLib = require('../../lib/crypto');
  assert(typeof cryptoLib.SpaceKeyCache === 'function',
    'SpaceKeyCache is exported from lib/crypto/index.js');

  const cache = new cryptoLib.SpaceKeyCache();
  const sk = randomKey();
  cache.put('a', 's', sk);
  assert(cache.get('a', 's').equals(sk), 'cache created from index export works');
}

// ---------------------------------------------------------------------------
// Run all tests
// ---------------------------------------------------------------------------

console.log('Mind Protocol — Space Key Cache — JS Test Suite');
console.log('================================================');

testGetReturnsNullOnEmptyCache();
testPutThenGet();
testDifferentActorSameSpace();
testOverwriteExistingEntry();
testTtlExpiry();
testTtlNotExpiredYet();
testLruEvictionAtCapacity();
testLruAccessRefreshesOrder();
testInvalidateRemovesAllEntriesForSpace();
testInvalidateNonexistentSpaceIsNoop();
testClear();
testExportedFromIndex();

console.log('\n================================================');
console.log(`Results: ${passed} passed, ${failed} failed`);

if (failed > 0) {
  process.exit(1);
} else {
  console.log('All tests passed.');
}
