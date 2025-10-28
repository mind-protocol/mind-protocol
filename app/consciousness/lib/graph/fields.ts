/**
 * SubEntity Field Geometry Utilities
 *
 * Shared utilities for computing soft hull polygons and subentity bridges.
 * Used by both D3 (GraphCanvasV3) and Pixi (PixiRenderer) implementations
 * to ensure visual consistency.
 *
 * Taxonomy Note: "SubEntity" refers to Scale A weighted neighborhoods (e.g., builder, observer)
 * These are NOT individual nodes, but functional/semantic clusters in the consciousness graph.
 *
 * Architecture:
 * - Hulls: convex hull → inflate → smooth
 * - Bridges: cubic Bézier curves between subentity centroids
 * - Membership: ring geometry for multi-subentity nodes
 *
 * Design: "subentities as soft hulls" - no circles, no MEMBER_OF lines
 * Author: Felix "Ironhand"
 * Date: 2025-10-26
 * Updated: 2025-10-26 (Agent 6 - Taxonomy correction entity → subentity)
 */

import * as d3 from 'd3';

// ========================================================================
// TYPE DEFINITIONS
// ========================================================================

export interface SubEntityHull {
  subentityId: string;
  polygon: Array<[number, number]>;  // Smoothed, inflated hull points
  centroid: [number, number];
  rawPath?: string;                   // D3 path string (for SVG)
  label: string;
  size: number;
  energy?: number;                     // Average energy (modulates alpha)
}

export interface SubEntityBridge {
  from: string;                        // Source subentity ID
  to: string;                          // Target subentity ID
  fromPos: [number, number];           // Source centroid
  toPos: [number, number];             // Target centroid
  strength: number;                    // Flow weight (0-1)
  controlPoints?: Array<[number, number]>; // Bézier control points
}

export interface MembershipRing {
  radius: number;
  color: string;
  opacity: number;
}

// ========================================================================
// HULL GEOMETRY
// ========================================================================

/**
 * Compute convex hull from points using d3.polygonHull
 * Returns null if hull cannot be computed (< 3 points)
 */
export function convexHullPath(points: Array<[number, number]>): Array<[number, number]> | null {
  if (points.length < 3) return null;

  // Filter out invalid points
  const validPoints = points.filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (validPoints.length < 3) return null;

  // @ts-ignore - d3.polygonHull exists in d3 v7
  const hull = (d3 as any).polygonHull(validPoints);
  return hull ?? null;
}

/**
 * Inflate polygon by scaling from centroid
 * Creates visual padding around subentity members
 *
 * @param poly - Hull polygon points
 * @param inflate - Inflation distance in pixels (default: 12)
 */
export function inflatePolygon(poly: Array<[number, number]>, inflate = 12): Array<[number, number]> {
  if (poly.length === 0) return poly;

  const cx = d3.mean(poly, p => p[0]) ?? 0;
  const cy = d3.mean(poly, p => p[1]) ?? 0;
  const scale = 1 + inflate / 120; // gentle growth (12px → 10% increase)

  return poly.map(([x, y]) => [
    cx + (x - cx) * scale,
    cy + (y - cy) * scale
  ] as [number, number]);
}

/**
 * Smooth polygon path using Catmull-Rom curve (closed)
 * Returns SVG path string for D3 rendering
 *
 * @param poly - Polygon points
 * @param alpha - Curve tension (0.5 = standard Catmull-Rom)
 */
export function smoothPath(poly: Array<[number, number]>, alpha = 0.5): string {
  if (poly.length < 3) return '';

  const line = d3.line<[number, number]>()
    .curve(d3.curveCatmullRomClosed.alpha(alpha));

  return line(poly) || '';
}

/**
 * Build subentity hull from member node positions
 *
 * @param subentityId - SubEntity identifier (e.g., 'builder', 'observer')
 * @param members - Nodes belonging to this subentity
 * @param inflate - Inflation distance (default: 12px)
 * @returns SubEntityHull or null if hull cannot be computed
 */
export function buildSubEntityHull(
  subentityId: string,
  members: Array<{ x: number; y: number; energy?: number; [key: string]: any }>,
  inflate = 12
): SubEntityHull | null {
  // Extract positions
  const points: Array<[number, number]> = members
    .filter(m => Number.isFinite(m.x) && Number.isFinite(m.y))
    .map(m => [m.x, m.y]);

  if (points.length < 3) return null;

  // Compute hull
  const hull = convexHullPath(points);
  if (!hull) return null;

  // Inflate and smooth
  const inflated = inflatePolygon(hull, inflate);
  const centroid = d3.polygonCentroid(inflated as any) as [number, number];
  const pathString = smoothPath(inflated);

  // Compute average energy
  const avgEnergy = members.length > 0
    ? members.reduce((sum, m) => sum + (m.energy || 0), 0) / members.length
    : 0;

  return {
    subentityId,
    polygon: inflated,
    centroid,
    rawPath: pathString,
    label: `${subentityId} (${members.length})`,
    size: members.length,
    energy: avgEnergy
  };
}

// ========================================================================
// BRIDGE GEOMETRY
// ========================================================================

/**
 * Compute cubic Bézier control points for subentity bridge
 * Creates gentle arc between subentity centroids
 *
 * @param from - Source centroid
 * @param to - Target centroid
 * @param curve - Curve height in pixels (default: 120)
 * @returns [controlPoint1, controlPoint2]
 */
export function computeBridgeControlPoints(
  from: [number, number],
  to: [number, number],
  curve = 120
): Array<[number, number]> {
  const [ax, ay] = from;
  const [bx, by] = to;

  // Gentle S-curve
  const cx1 = ax + (bx - ax) * 0.35;
  const cy1 = ay - curve;
  const cx2 = ax + (bx - ax) * 0.65;
  const cy2 = by + curve;

  return [[cx1, cy1], [cx2, cy2]];
}

/**
 * Build SVG path for subentity bridge (D3 rendering)
 */
export function buildBridgePath(bridge: SubEntityBridge): string {
  const [ax, ay] = bridge.fromPos;
  const [bx, by] = bridge.toPos;
  const [[cx1, cy1], [cx2, cy2]] = computeBridgeControlPoints(bridge.fromPos, bridge.toPos);

  return `M ${ax} ${ay} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${bx} ${by}`;
}

/**
 * Build subentity bridge from flow data
 *
 * @param fromSubEntity - Source subentity ID
 * @param toSubEntity - Target subentity ID
 * @param fromCentroid - Source subentity centroid
 * @param toCentroid - Target subentity centroid
 * @param strength - Flow strength (0-1)
 */
export function buildSubEntityBridge(
  fromSubEntity: string,
  toSubEntity: string,
  fromCentroid: [number, number],
  toCentroid: [number, number],
  strength: number
): SubEntityBridge {
  const controlPoints = computeBridgeControlPoints(fromCentroid, toCentroid);

  return {
    from: fromSubEntity,
    to: toSubEntity,
    fromPos: fromCentroid,
    toPos: toCentroid,
    strength,
    controlPoints
  };
}

// ========================================================================
// MEMBERSHIP RINGS
// ========================================================================

const RING_COLORS = [
  '#a78bfa',  // purple-400 (first extra membership)
  '#60a5fa',  // blue-400 (second extra membership)
  '#f59e0b'   // amber-500 (third extra membership)
];

/**
 * Compute membership rings for multi-subentity nodes
 *
 * @param nodeRadius - Base node radius
 * @param memberships - Array of subentity IDs (excluding primary)
 * @param maxRings - Maximum rings to show (default: 3)
 * @returns Array of ring specifications
 */
export function computeMembershipRings(
  nodeRadius: number,
  memberships: string[],
  maxRings = 3
): MembershipRing[] {
  const extras = memberships.slice(0, maxRings);

  return extras.map((_, i) => ({
    radius: nodeRadius + 2 + i * 3,
    color: RING_COLORS[i],
    opacity: 0.8
  }));
}

// ========================================================================
// UTILITIES
// ========================================================================

/**
 * Compute subentity centroids from member positions
 * Used for bridge rendering when hulls aren't visible
 */
export function computeSubEntityCentroids(
  clusterNodes: Array<{
    id: string;
    members: Array<{ x: number; y: number }>;
    x?: number;
    y?: number;
  }>
): Map<string, [number, number]> {
  const centroids = new Map<string, [number, number]>();

  clusterNodes.forEach(c => {
    const members = c.members || [];
    const pts = members.map(m => [m.x, m.y]) as Array<[number, number]>;

    if (pts.length > 0) {
      const cx = d3.mean(pts, p => p[0]) ?? c.x ?? 0;
      const cy = d3.mean(pts, p => p[1]) ?? c.y ?? 0;
      centroids.set(c.id, [cx, cy]);
    } else if (c.x !== undefined && c.y !== undefined) {
      centroids.set(c.id, [c.x, c.y]);
    }
  });

  return centroids;
}

/**
 * Compute visual properties for subentity bridge
 * Maps flow strength to stroke width and opacity
 */
export function computeBridgeStyle(strength: number): {
  strokeWidth: number;
  strokeOpacity: number;
} {
  return {
    strokeWidth: Math.min(8, 1 + strength * 6),
    strokeOpacity: Math.min(0.5, 0.08 + strength * 0.25)
  };
}

/**
 * Compute visual properties for subentity hull
 * Maps energy to fill opacity
 */
export function computeHullStyle(energy: number): {
  fillOpacity: number;
} {
  return {
    fillOpacity: Math.min(0.25, 0.12 + energy * 0.15)
  };
}
