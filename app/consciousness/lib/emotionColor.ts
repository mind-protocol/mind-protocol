/**
 * Emotion Color Conversion
 *
 * Canonical Phase 1 recipe for mapping 2D affect space (valence, arousal)
 * to HSL color space for emotion visualization.
 *
 * Spec: emotion_color_mapping_v2_canonical.md
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 *
 * Key principle: Orthogonal visual encoding for debuggability
 * - Valence → Hue + Saturation (independent encoding)
 * - Arousal → Lightness (independent encoding)
 * Each psychological axis contributes to separate perceptual dimension.
 */

/**
 * Emotion color in HSL space
 */
export interface EmotionColor {
  hue: number;        // 0-360° (color type)
  saturation: number; // 0-100% (color intensity)
  lightness: number;  // 0-100% (brightness)
}

/**
 * Emotion vector (canonical Phase 1)
 */
export interface EmotionVector {
  valence: number;    // Signed [-1, 1] (- = unpleasant, + = pleasant)
  arousal: number;    // Signed [-1, 1] (- = low/relaxed, + = high/activated)
}

/**
 * Convert valence to hue angle
 *
 * Maps valence [-1, 1] to hue [320°, 120°] via linear interpolation:
 * - Negative valence (unpleasant) → Magenta/Red (320°)
 * - Positive valence (pleasant) → Green (120°)
 *
 * Formula: h = lerp(320°, 120°, normalize(valence))
 * where normalize(v) = (v + 1) / 2
 *
 * @param valence Signed valence in [-1, 1]
 * @returns Hue angle in [0, 360]°
 */
export function valenceToHue(valence: number): number {
  // Clamp input to valid range
  const clamped = Math.max(-1, Math.min(1, valence));

  // Normalize to [0, 1]
  const normalized = (clamped + 1) / 2;

  // Linear interpolation from 320° to 120°
  // Note: 120° - 320° = -200°, but we want to go the "long way" around
  // the color wheel for smooth progression through warm colors
  const startHue = 320;
  const endHue = 120;

  // Direct lerp (crosses through reds, oranges, yellows)
  const hue = startHue + normalized * (endHue - startHue + 360);

  // Wrap to [0, 360]
  return hue % 360;
}

/**
 * Convert |valence| to saturation
 *
 * Maps absolute valence to saturation [30%, 80%]:
 * - Neutral emotion (|v| ≈ 0) → Low saturation (grayish)
 * - Strong emotion (|v| ≈ 1) → High saturation (vivid)
 *
 * Formula: s = 30% + 50% * |valence|
 *
 * @param valence Signed valence in [-1, 1]
 * @returns Saturation in [0, 100]%
 */
export function valenceToSaturation(valence: number): number {
  const absValence = Math.abs(valence);
  const clamped = Math.min(1, absValence);

  const saturation = 30 + (50 * clamped);

  // Cap at 80% for legibility
  return Math.min(80, saturation);
}

/**
 * Convert arousal to lightness
 *
 * Maps arousal [-1, 1] to lightness [45%, 95%]:
 * - High arousal (activated) → Darker (45%)
 * - Low arousal (relaxed) → Lighter (95%)
 *
 * Formula: l = 70% - 25% * arousal
 *
 * Inverted mapping: high arousal = darker to avoid washed-out high-energy states.
 *
 * @param arousal Signed arousal in [-1, 1]
 * @returns Lightness in [0, 100]%
 */
export function arousalToLightness(arousal: number): number {
  const clamped = Math.max(-1, Math.min(1, arousal));

  const lightness = 70 - (25 * clamped);

  // Clamp to [45%, 95%] for visibility
  return Math.max(45, Math.min(95, lightness));
}

/**
 * Convert emotion vector to HSL color (canonical recipe)
 *
 * Applies orthogonal visual encoding:
 * - Valence → Hue (color type) + Saturation (color intensity)
 * - Arousal → Lightness (brightness)
 *
 * Special case: Near-neutral emotions (|v| < 0.01, |a| < 0.01) → Gray
 *
 * @param valence Signed valence in [-1, 1]
 * @param arousal Signed arousal in [-1, 1]
 * @returns HSL color
 */
export function emotionToHSL(valence: number, arousal: number): EmotionColor {
  // Handle extreme neutral case
  if (Math.abs(valence) < 0.01 && Math.abs(arousal) < 0.01) {
    return {
      hue: 0,
      saturation: 0,
      lightness: 70
    };
  }

  // Apply orthogonal mapping
  const hue = valenceToHue(valence);
  const saturation = valenceToSaturation(valence);
  const lightness = arousalToLightness(arousal);

  return { hue, saturation, lightness };
}

/**
 * Convert emotion vector to HSL color (convenience overload)
 *
 * @param emotion Emotion vector with valence and arousal
 * @returns HSL color
 */
export function emotionVectorToHSL(emotion: EmotionVector): EmotionColor {
  return emotionToHSL(emotion.valence, emotion.arousal);
}

/**
 * Convert HSL color to CSS color string
 *
 * @param color HSL color
 * @returns CSS hsl() string, e.g., "hsl(120, 60%, 70%)"
 */
export function hslToCSS(color: EmotionColor): string {
  return `hsl(${color.hue.toFixed(0)}, ${color.saturation.toFixed(0)}%, ${color.lightness.toFixed(0)}%)`;
}

/**
 * Semantic quadrant labels (UI-derived, not in events)
 *
 * Maps (valence, arousal) to human-readable emotion quadrants.
 * Use for tooltips, badges, attribution cards.
 *
 * @param valence Signed valence in [-1, 1]
 * @param arousal Signed arousal in [-1, 1]
 * @returns Quadrant label
 */
export function getQuadrantLabel(valence: number, arousal: number): string {
  if (valence > 0.2) {
    return arousal > 0.2 ? "excited/engaged" : "calm/pleasant";
  } else if (valence < -0.2) {
    return arousal > 0.2 ? "tense/alert" : "flat/low-mood";
  } else {
    return "neutral";
  }
}

/**
 * Get axis badges (UI-derived, not in events)
 *
 * Returns array of semantic labels for strong axis values.
 * Use for attribution cards to show dominant axes.
 *
 * @param valence Signed valence in [-1, 1]
 * @param arousal Signed arousal in [-1, 1]
 * @returns Array of badge labels (e.g., ["pleasant", "high arousal"])
 */
export function getAxisBadges(valence: number, arousal: number): string[] {
  const badges: string[] = [];

  if (valence > 0.5) badges.push("pleasant");
  if (valence < -0.5) badges.push("aversive");
  if (arousal > 0.5) badges.push("high arousal");
  if (arousal < -0.5) badges.push("low arousal");

  return badges;
}

/**
 * Example color mappings for testing/documentation
 */
export const EXAMPLE_EMOTIONS: Array<{
  label: string;
  valence: number;
  arousal: number;
  expectedColor: string;
}> = [
  {
    label: "Calm, pleasant",
    valence: 0.6,
    arousal: -0.4,
    expectedColor: "Light yellow-green"
  },
  {
    label: "Excited, joyful",
    valence: 0.8,
    arousal: 0.7,
    expectedColor: "Dark vibrant green"
  },
  {
    label: "Tense, anxious",
    valence: -0.7,
    arousal: 0.8,
    expectedColor: "Dark saturated red"
  },
  {
    label: "Sad, low",
    valence: -0.5,
    arousal: -0.6,
    expectedColor: "Light muted red-orange"
  },
  {
    label: "Neutral",
    valence: 0.0,
    arousal: 0.0,
    expectedColor: "Medium gray"
  }
];
