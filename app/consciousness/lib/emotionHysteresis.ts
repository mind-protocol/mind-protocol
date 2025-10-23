/**
 * Emotion Hysteresis Logic
 *
 * Prevents visual flicker from high-frequency emotion updates by applying
 * magnitude and hue thresholds. Only updates visual when change exceeds threshold.
 *
 * Spec: emotion_color_mapping_v2_canonical.md
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 *
 * Two-level flicker prevention:
 * 1. Backend: Sampling at EMOTION_COLOR_SAMPLE_RATE (e.g., 10%)
 * 2. Frontend: Hysteresis thresholds (this module)
 */

import { EmotionVector, valenceToHue, arousalToLightness } from './emotionColor';

/**
 * Hysteresis thresholds (canonical Phase 1)
 */
export const HYSTERESIS_CONFIG = {
  /** Magnitude change required to trigger update (8% of full range) */
  MAG_THRESHOLD: 0.08,

  /** Hue change required to trigger update (12 degrees) */
  HUE_THRESHOLD: 12,

  /** Lightness change required to trigger update (5%) */
  LIGHTNESS_THRESHOLD: 5,
};

/**
 * Emotion display state with hysteresis tracking
 *
 * Stores both the actual (latest) emotion and the displayed (rendered) emotion.
 * Visual updates only when change exceeds threshold.
 */
export interface EmotionDisplayState {
  /** Actual emotion from latest update */
  actual: EmotionVector & { magnitude: number };

  /** Displayed emotion (last rendered) */
  displayed: EmotionVector & { magnitude: number };

  /** Timestamp of last display update */
  lastUpdateTime: number;
}

/**
 * Check if magnitude change exceeds threshold
 *
 * @param displayedMag Last rendered magnitude
 * @param actualMag Current magnitude from event
 * @returns true if update needed
 */
export function shouldUpdateMagnitude(
  displayedMag: number,
  actualMag: number
): boolean {
  return Math.abs(actualMag - displayedMag) > HYSTERESIS_CONFIG.MAG_THRESHOLD;
}

/**
 * Check if hue change exceeds threshold
 *
 * Handles wraparound: 350° → 10° is 20° change, not 340°.
 *
 * @param displayedHue Last rendered hue (0-360)
 * @param actualHue Current hue from converted valence (0-360)
 * @returns true if update needed
 */
export function shouldUpdateHue(
  displayedHue: number,
  actualHue: number
): boolean {
  // Calculate shortest angular distance on color wheel
  let delta = Math.abs(actualHue - displayedHue);

  // Handle wraparound (e.g., 350° to 10° is 20°, not 340°)
  if (delta > 180) {
    delta = 360 - delta;
  }

  return delta > HYSTERESIS_CONFIG.HUE_THRESHOLD;
}

/**
 * Check if lightness change exceeds threshold
 *
 * @param displayedLight Last rendered lightness (0-100)
 * @param actualLight Current lightness from converted arousal (0-100)
 * @returns true if update needed
 */
export function shouldUpdateLightness(
  displayedLight: number,
  actualLight: number
): boolean {
  return Math.abs(actualLight - displayedLight) > HYSTERESIS_CONFIG.LIGHTNESS_THRESHOLD;
}

/**
 * Check if emotion color should be updated (combined logic)
 *
 * Returns true if ANY of the following exceed threshold:
 * - Magnitude change > 0.08
 * - Hue change > 12° (derived from valence)
 * - Lightness change > 5% (derived from arousal)
 *
 * @param state Current emotion display state
 * @returns true if visual update needed
 */
export function shouldUpdateColor(state: EmotionDisplayState): boolean {
  // Check magnitude
  if (shouldUpdateMagnitude(state.displayed.magnitude, state.actual.magnitude)) {
    return true;
  }

  // Check hue (derived from valence)
  const displayedHue = valenceToHue(state.displayed.valence);
  const actualHue = valenceToHue(state.actual.valence);

  if (shouldUpdateHue(displayedHue, actualHue)) {
    return true;
  }

  // Check lightness (derived from arousal)
  const displayedLight = arousalToLightness(state.displayed.arousal);
  const actualLight = arousalToLightness(state.actual.arousal);

  if (shouldUpdateLightness(displayedLight, actualLight)) {
    return true;
  }

  return false;
}

/**
 * Update emotion display state
 *
 * Creates new state with updated actual emotion.
 * If shouldUpdateColor returns true, also updates displayed emotion.
 *
 * @param prevState Previous display state
 * @param newEmotion New emotion from event
 * @returns Updated display state
 */
export function updateEmotionState(
  prevState: EmotionDisplayState | null,
  newEmotion: EmotionVector & { magnitude: number }
): EmotionDisplayState {
  // Initialize if first update
  if (!prevState) {
    return {
      actual: newEmotion,
      displayed: newEmotion,
      lastUpdateTime: Date.now()
    };
  }

  // Create candidate state with new actual emotion
  const candidateState: EmotionDisplayState = {
    actual: newEmotion,
    displayed: prevState.displayed, // Keep old displayed for now
    lastUpdateTime: prevState.lastUpdateTime
  };

  // Check if visual update needed
  if (shouldUpdateColor(candidateState)) {
    // Update displayed to match actual
    return {
      actual: newEmotion,
      displayed: newEmotion,
      lastUpdateTime: Date.now()
    };
  }

  // No visual update - keep old displayed
  return candidateState;
}

/**
 * Temporal smoothing (optional bonus feature)
 *
 * Linear interpolation for smooth color transitions.
 * Use for 200ms fade animations.
 */
export interface LerpConfig {
  /** Duration of transition in ms */
  duration: number;

  /** Easing function (default: linear) */
  easing?: (t: number) => number;
}

/**
 * Linear interpolation between two values
 *
 * @param from Start value
 * @param to End value
 * @param t Interpolation factor [0, 1]
 * @returns Interpolated value
 */
export function lerp(from: number, to: number, t: number): number {
  return from + (to - from) * t;
}

/**
 * Angular lerp (for hue on color wheel)
 *
 * Takes shortest path around the color wheel.
 *
 * @param from Start hue (0-360)
 * @param to End hue (0-360)
 * @param t Interpolation factor [0, 1]
 * @returns Interpolated hue (0-360)
 */
export function lerpAngle(from: number, to: number, t: number): number {
  // Calculate shortest angular distance
  let delta = ((to - from + 180) % 360) - 180;

  // Interpolate along shortest path
  return (from + delta * t + 360) % 360;
}

/**
 * Interpolate between two emotion vectors
 *
 * For smooth transitions between emotion states.
 * Use with requestAnimationFrame for 200ms fade.
 *
 * @param from Start emotion
 * @param to End emotion
 * @param t Interpolation factor [0, 1]
 * @returns Interpolated emotion
 */
export function lerpEmotion(
  from: EmotionVector & { magnitude: number },
  to: EmotionVector & { magnitude: number },
  t: number
): EmotionVector & { magnitude: number } {
  return {
    valence: lerp(from.valence, to.valence, t),
    arousal: lerp(from.arousal, to.arousal, t),
    magnitude: lerp(from.magnitude, to.magnitude, t)
  };
}

/**
 * Calculate interpolation factor for elapsed time
 *
 * @param startTime Animation start timestamp
 * @param duration Animation duration in ms
 * @param easing Optional easing function
 * @returns Interpolation factor [0, 1] (clamped)
 */
export function calculateLerpFactor(
  startTime: number,
  duration: number,
  easing?: (t: number) => number
): number {
  const elapsed = Date.now() - startTime;
  let t = elapsed / duration;

  // Clamp to [0, 1]
  t = Math.max(0, Math.min(1, t));

  // Apply easing if provided
  if (easing) {
    t = easing(t);
  }

  return t;
}

/**
 * Standard easing functions
 */
export const EASING = {
  /** Linear interpolation (no easing) */
  linear: (t: number) => t,

  /** Ease in (accelerate) */
  easeIn: (t: number) => t * t,

  /** Ease out (decelerate) */
  easeOut: (t: number) => t * (2 - t),

  /** Ease in-out (S-curve) */
  easeInOut: (t: number) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t)
};

/**
 * Example usage for smooth transitions:
 *
 * ```typescript
 * const [animState, setAnimState] = useState<{
 *   from: EmotionVector;
 *   to: EmotionVector;
 *   startTime: number;
 * } | null>(null);
 *
 * useEffect(() => {
 *   if (!animState) return;
 *
 *   const animate = () => {
 *     const t = calculateLerpFactor(animState.startTime, 200, EASING.easeOut);
 *     const current = lerpEmotion(animState.from, animState.to, t);
 *
 *     // Update rendered color with current
 *     updateNodeColor(current);
 *
 *     if (t < 1) {
 *       requestAnimationFrame(animate);
 *     }
 *   };
 *
 *   requestAnimationFrame(animate);
 * }, [animState]);
 * ```
 */
