/**
 * Ring Buffer Utility
 *
 * Prevents unbounded array growth in real-time telemetry streams.
 * When buffer reaches max size, removes oldest entries before adding new ones.
 *
 * Author: Atlas (Infrastructure Engineer)
 * Context: Memory leak fix (1.8GB dashboard → bounded growth)
 * Date: 2025-10-25
 */

/**
 * Add item to ring buffer with fixed max size
 *
 * @param arr - Current array
 * @param item - New item to add
 * @param max - Maximum buffer size (default: 5000)
 * @returns Updated array with bounded size
 */
export function pushRing<T>(arr: T[], item: T, max = 5000): T[] {
  // If at capacity, remove oldest entries
  if (arr.length >= max) {
    arr.splice(0, arr.length - max + 1);
  }
  arr.push(item);
  return arr;
}

/**
 * Add multiple items to ring buffer
 *
 * @param arr - Current array
 * @param items - New items to add
 * @param max - Maximum buffer size
 * @returns Updated array with bounded size
 */
export function pushRingBatch<T>(arr: T[], items: T[], max = 5000): T[] {
  const combined = [...arr, ...items];
  if (combined.length > max) {
    return combined.slice(combined.length - max);
  }
  return combined;
}

/**
 * Clean Map entries older than TTL
 *
 * @param map - Map with entries that have lastUpdated timestamp
 * @param ttlMs - Time-to-live in milliseconds
 * @returns New Map with stale entries removed
 */
export function cleanMapByTTL<K, V extends { lastUpdated: number }>(
  map: Map<K, V>,
  ttlMs: number
): Map<K, V> {
  const now = Date.now();
  const cleaned = new Map<K, V>();

  for (const [key, value] of map.entries()) {
    if (now - value.lastUpdated < ttlMs) {
      cleaned.set(key, value);
    }
  }

  return cleaned;
}
