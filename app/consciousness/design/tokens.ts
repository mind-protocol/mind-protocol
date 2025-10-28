/**
 * Mind Harbor Design Tokens
 *
 * La Serenissima palette: Warm creams, bright blues, yellow cascade
 * Design Language: "Nodes do work; entities are ambient fields"
 *
 * Principles:
 * - Backgrounds are quiet (warm cream or bright water)
 * - All animation is event-driven (no decorative looping)
 * - Truth stays visible (red only for real issues)
 * - Honest sizing (weight + energy + traversals)
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-26
 */

// ========================================================================
// COLORS (La Serenissima)
// ========================================================================

export const Colors = {
  // Backgrounds (La Serenissima)
  bgCream: '#f5f1e8',  // main land / city mode
  bgWater: '#dbeafe',  // harbor water mode
  panel: '#faf8f3',    // light cream
  border: '#e8e2d5',

  // Cascade energy (Yellow family)
  energyHi: '#fbbf24',
  energyMd: '#fcd34d',
  energyLo: '#fde68a',
  energyFade: '#fef3c7',

  // Calm / water (Bright blues)
  blueHi: '#60a5fa',
  blueMd: '#93c5fd',
  blueLo: '#bfdbfe',

  // Formation (Warm purples)
  formHi: '#c084fc',
  formMd: '#a78bfa',
  formLo: '#e9d5ff',

  // Alerts (Truth stays visible)
  redHi: '#ef4444',
  redMd: '#fca5a5',
  warn: '#fed7aa',

  // Inactive / dormancy
  grayHi: '#9ca3af',
  grayMd: '#d1d5db',
  grayLo: '#e5e7eb',
};

// ========================================================================
// TYPOGRAPHY
// ========================================================================

export const Typo = {
  heading: {
    family: 'Inter, system-ui',
    size: 18,
    weight: 600,
    color: '#1f2937'
  },
  body: {
    family: 'Inter, system-ui',
    size: 14,
    weight: 400,
    color: '#4b5563'
  },
  code: {
    family: '"JetBrains Mono", ui-monospace',
    size: 12,
    weight: 400,
    color: '#6366f1'
  }
};

// ========================================================================
// RHYTHM (8px base unit)
// ========================================================================

export const Rhythm = {
  unit: 8,      // Base spacing unit
  gap: 16,      // Standard gap
  pad: 24,      // Standard padding
  shadowL1: '0 1px 3px rgba(0,0,0,0.1)'
};

// ========================================================================
// TIMING (event-driven animation bands)
// ========================================================================

export const Timing = {
  hover: 150,           // Quick hover response
  panelSlide: 300,      // Panel transitions
  stateFade: 1000,      // State transitions (flips)
  breathing: 1800,      // WM pulse breathing
  flowParticle: null,   // Variable, driven by flow rate
};

// ========================================================================
// VISUAL FORMULAS (data → visual mappings)
// ========================================================================

/**
 * Hull fill opacity from entity energy
 * Formula: alpha = clamp(0.08 + (E_entity/100)*0.12, 0.08, 0.20)
 */
export function hullAlpha(entityEnergy: number): number {
  return Math.min(0.20, Math.max(0.08, 0.08 + (entityEnergy / 100) * 0.12));
}

/**
 * Bridge width from flow strength
 * Formula: w = clamp(1 + 6*strength, 1, 8)
 */
export function bridgeWidth(strength: number): number {
  return Math.min(8, Math.max(1, 1 + 6 * strength));
}

/**
 * Bridge opacity from flow strength
 * Formula: alpha = 0.08 + 0.25*strength (cap 0.5)
 */
export function bridgeAlpha(strength: number): number {
  return Math.min(0.5, 0.08 + 0.25 * strength);
}

/**
 * Node radius from weight, energy, traversals
 * Formula: r = base * (0.8 + 0.4*weight + 0.3*E + 0.3*traversals)
 */
export function nodeRadius(
  base: number,
  weight: number,
  energy: number,
  traversals: number
): number {
  const factor = 0.8 + 0.4 * weight + 0.3 * energy + 0.3 * traversals;
  return base * Math.min(3, Math.max(0.5, factor)); // clamp to reasonable range
}

// ========================================================================
// MEMBERSHIP RINGS
// ========================================================================

export const MembershipRingColors = [
  '#a78bfa', // purple-400 (first extra membership)
  '#60a5fa', // blue-400 (second extra membership)
  '#f59e0b'  // amber-500 (third extra membership)
];

export const MembershipRingSpacing = {
  first: 2,   // r + 2
  second: 5,  // r + 5
  third: 8,   // r + 8
  maxVisible: 3 // Show max 3 rings, then "+n" tooltip
};

// ========================================================================
// LOD (Level of Detail) RULES
// ========================================================================

export const LOD = {
  // Zoom thresholds (scale factor)
  far: 0.5,      // Below this: hulls + bridges only, nodes as points
  medium: 1.0,   // Between far/near: nodes + hairlines + rings
  near: 2.0,     // Above this: full labels, edge annotations

  // Element visibility by LOD
  farMode: {
    hulls: true,
    bridges: true,
    nodes: 'points',    // Render as simple dots
    edges: false,
    labels: false,
    rings: false
  },
  mediumMode: {
    hulls: true,
    bridges: true,
    nodes: 'full',      // Render with emoji/circles
    edges: 'hairlines', // Thin, low-opacity
    labels: 'hover',    // Show on hover only
    rings: true
  },
  nearMode: {
    hulls: true,
    bridges: true,
    nodes: 'full',
    edges: 'full',      // Normal width + opacity
    labels: true,       // Always visible
    rings: true
  }
};

// ========================================================================
// ENTITY COLOR MAPPING (from ENTITY_COLORS constant)
// ========================================================================

/**
 * Get entity base color with Mind Harbor palette fallback
 * Returns blueLo if entity color not defined
 */
export function getEntityColor(
  entityId: string,
  entityColors?: Record<string, string>
): string {
  if (entityColors && entityColors[entityId]) {
    return entityColors[entityId];
  }
  return Colors.blueLo; // Default: bright blue (harbor water)
}

/**
 * Tint entity color toward water mode or cream mode
 */
export function tintEntityColor(baseColor: string, mode: 'water' | 'cream'): string {
  // Simple string interpolation for now
  // In production, use proper color mixing (hex -> rgb -> mix -> hex)
  return mode === 'water' ? Colors.blueLo : Colors.bgCream;
}
