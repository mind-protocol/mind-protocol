/**
 * layoutLocal.ts
 *
 * Deterministic local layout for member nodes inside entity containers.
 * Uses stable radial packing to avoid jitter on expand/collapse.
 *
 * Strategy:
 * - Radial slots arranged in concentric rings
 * - Position deterministic based on nodeId and index
 * - Cached per (entityId, nodeId) for stability across renders
 * - Radius scales with member count (more members = tighter packing)
 *
 * Author: Iris "The Aperture" (from Nicolas's reference implementation)
 * Created: 2025-10-25
 */

/**
 * Cache for local layout positions
 * Outer Map: entityId -> (inner Map: nodeId -> {x, y})
 *
 * This prevents re-layout thrash when nodes enter/exit the entity.
 */
const localLayoutCache: Map<string, Map<string, { x: number; y: number }>> = new Map();

/**
 * Clear the layout cache (useful for debugging or when entity structure changes dramatically)
 */
export function clearLayoutCache() {
  localLayoutCache.clear();
}

/**
 * Clear cache for specific entity (when entity is removed)
 */
export function clearEntityCache(entityId: string) {
  localLayoutCache.delete(entityId);
}

/**
 * Deterministic local layout inside an entity container
 *
 * Returns offset (x, y) relative to entity centroid.
 * Positions are stable across renders (cached by nodeId).
 *
 * @param entityId - Entity container ID
 * @param nodeId - Node being positioned
 * @param idx - Index of this node in member list (0-based)
 * @param count - Total number of members in entity
 * @param radius - Base radius for layout (default 120px)
 * @returns Offset {x, y} relative to entity centroid
 */
export function layoutLocal(
  entityId: string,
  nodeId: string,
  idx: number,
  count: number,
  radius: number = 120
): { x: number; y: number } {
  // Get or create entity cache
  let entityCache = localLayoutCache.get(entityId);
  if (!entityCache) {
    entityCache = new Map();
    localLayoutCache.set(entityId, entityCache);
  }

  // Return cached position if exists
  const cached = entityCache.get(nodeId);
  if (cached) return cached;

  // Calculate new position using radial packing
  // Strategy: Arrange nodes in concentric rings with equal angular spacing

  // Determine ring size (how many nodes per ring)
  const ringSize = Math.max(1, Math.ceil(Math.sqrt(count)));

  // Which ring is this node in? (0-indexed from center outward)
  const ring = Math.floor(idx / ringSize);

  // Position within the ring (0 to ringSize-1)
  const posInRing = idx % ringSize;

  // Angle for this position (distribute evenly around circle)
  const angle = (posInRing / ringSize) * Math.PI * 2;

  // Distance from center (scales with ring number and total count)
  // More members = tighter packing (log scale to avoid huge clouds)
  const scaledRadius = (radius / (1 + Math.log2(1 + count / 50))) * (0.35 + 0.65 * (ring / Math.max(1, ringSize)));

  // Convert polar to cartesian (offset from entity centroid)
  const x = Math.cos(angle) * scaledRadius;
  const y = Math.sin(angle) * scaledRadius;

  // Cache and return
  const position = { x, y };
  entityCache.set(nodeId, position);
  return position;
}

/**
 * Get all cached positions for an entity (useful for debugging)
 */
export function getEntityLayout(entityId: string): Map<string, { x: number; y: number }> | undefined {
  return localLayoutCache.get(entityId);
}

/**
 * Get cache statistics (for monitoring/debugging)
 */
export function getLayoutCacheStats(): {
  entityCount: number;
  totalNodes: number;
  avgNodesPerEntity: number;
} {
  const entityCount = localLayoutCache.size;
  let totalNodes = 0;

  for (const entityCache of localLayoutCache.values()) {
    totalNodes += entityCache.size;
  }

  return {
    entityCount,
    totalNodes,
    avgNodesPerEntity: entityCount > 0 ? totalNodes / entityCount : 0
  };
}
