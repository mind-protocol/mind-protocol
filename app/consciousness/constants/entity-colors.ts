/**
 * Entity Color Scheme
 *
 * Assigns unique colors to each consciousness entity for visual distinction.
 * Used for glows, labels, and UI elements throughout Mind Harbor.
 *
 * Design Philosophy:
 * - Distinct hues for easy differentiation
 * - Medium saturation (not too bright, visible on dark backgrounds)
 * - Consistent with Venice/Observatory aesthetic
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-19
 */

export const ENTITY_COLORS: Record<string, string> = {
  // Core cognitive entities
  'translator': '#2dd4bf',      // Teal - bridging concepts
  'builder': '#f59e0b',          // Amber - constructing systems
  'observer': '#06b6d4',         // Cyan - watching patterns
  'validator': '#10b981',        // Green - verifying correctness
  'architect': '#8b5cf6',        // Purple - designing structure
  'pragmatist': '#f97316',       // Orange - practical action
  'boundary_keeper': '#ef4444',  // Red - maintaining limits

  // Specialized entities
  'memory_keeper': '#ec4899',    // Pink - preserving experiences
  'pattern_recognizer': '#14b8a6', // Teal-green - finding structures
  'integrator': '#6366f1',       // Indigo - combining insights
  'explorer': '#eab308',         // Yellow - discovering new territory
  'consciousness_observer': '#0ea5e9', // Sky blue - meta-awareness

  // Default fallback
  'default': '#94a3b8'           // Slate - unknown entities
};

/**
 * Get color for an entity, with fallback to default
 */
export function getEntityColor(entityId: string): string {
  return ENTITY_COLORS[entityId] || ENTITY_COLORS['default'];
}

/**
 * Get RGB values from hex color (for SVG filters)
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 148, g: 163, b: 184 }; // Default slate RGB
}
