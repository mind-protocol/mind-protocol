/**
 * SubEntity Field Drawing Utilities (Pixi)
 *
 * Pixi.js drawing helpers for subentities-as-soft-hulls visualization.
 * Matches Mind Harbor design language (La Serenissima palette).
 *
 * Taxonomy Note: "SubEntity" refers to Scale A weighted neighborhoods (e.g., builder, observer)
 * These are rendered as soft polygon hulls enclosing their member nodes.
 *
 * Functions:
 * - drawHull(polygon, energy): Soft polygon with blur
 * - drawBridge(A, B, strength): Fuzzy ribbon with gradient
 * - drawMembershipRings(node, memberships): 1-3 rings for multi-membership
 *
 * Design: All formulas from design/tokens.ts
 * Author: Felix "Ironhand" + Iris "The Aperture"
 * Date: 2025-10-26
 * Updated: 2025-10-26 (Agent 6 - Taxonomy correction entity → subentity)
 */

import * as PIXI from 'pixi.js';
import {
  Colors,
  hullAlpha,
  bridgeWidth,
  bridgeAlpha,
  MembershipRingColors,
  MembershipRingSpacing,
  getEntityColor // Note: This comes from design/tokens.ts, may need update
} from '../../design/tokens';

// ========================================================================
// HULL DRAWING
// ========================================================================

/**
 * Draw subentity hull as soft polygon with blur
 *
 * @param graphics - Pixi Graphics object
 * @param polygon - Hull polygon points (already inflated + smoothed)
 * @param subentityId - SubEntity identifier (e.g., 'builder', 'observer')
 * @param energy - SubEntity energy (0-100, modulates alpha)
 * @param subentityColors - Optional subentity color mapping
 */
export function drawHull(
  graphics: PIXI.Graphics,
  polygon: Array<[number, number]>,
  subentityId: string,
  energy: number = 0,
  subentityColors?: Record<string, string>
): void {
  if (polygon.length < 3) return;

  // Get subentity base color (tinted toward blueLo for water mode)
  const baseColor = getEntityColor(subentityId, subentityColors); // TODO: Rename getEntityColor in tokens.ts
  const fillColor = parseInt(Colors.blueLo.replace('#', ''), 16);

  // Compute alpha from energy (formula from tokens.ts)
  const alpha = hullAlpha(energy);

  graphics.beginFill(fillColor, alpha);
  graphics.moveTo(polygon[0][0], polygon[0][1]);

  for (let i = 1; i < polygon.length; i++) {
    graphics.lineTo(polygon[i][0], polygon[i][1]);
  }

  graphics.closePath();
  graphics.endFill();
}

/**
 * Add soft blur filter to hull container (optional, perf-sensitive)
 * If perf is tight, use dual-fill (solid inner + wider transparent outer) instead
 *
 * @param container - Pixi container holding hull graphics
 * @param blurAmount - Blur radius (default: 4px)
 */
export function addHullBlur(container: PIXI.Container, blurAmount: number = 4): void {
  const blurFilter = new PIXI.BlurFilter(blurAmount);
  blurFilter.quality = 2; // Balance quality vs performance
  container.filters = [blurFilter];
}

/**
 * Draw dual-fill hull (perf fallback, no filter)
 * Solid inner + wider transparent outer for fake blur effect
 */
export function drawHullDualFill(
  graphics: PIXI.Graphics,
  polygon: Array<[number, number]>,
  subentityId: string,
  energy: number = 0,
  subentityColors?: Record<string, string>
): void {
  if (polygon.length < 3) return;

  const baseColor = getEntityColor(subentityId, subentityColors); // TODO: Rename getEntityColor in tokens.ts
  const fillColor = parseInt(Colors.blueLo.replace('#', ''), 16);
  const alpha = hullAlpha(energy);

  // Outer wider fill (translucent)
  graphics.lineStyle(6, fillColor, alpha * 0.3);
  graphics.moveTo(polygon[0][0], polygon[0][1]);
  for (let i = 1; i < polygon.length; i++) {
    graphics.lineTo(polygon[i][0], polygon[i][1]);
  }
  graphics.closePath();

  // Inner solid fill
  graphics.lineStyle(0);
  graphics.beginFill(fillColor, alpha);
  graphics.moveTo(polygon[0][0], polygon[0][1]);
  for (let i = 1; i < polygon.length; i++) {
    graphics.lineTo(polygon[i][0], polygon[i][1]);
  }
  graphics.closePath();
  graphics.endFill();
}

// ========================================================================
// BRIDGE DRAWING
// ========================================================================

/**
 * Draw subentity bridge as fuzzy ribbon (cubic Bézier curve)
 *
 * @param graphics - Pixi Graphics object
 * @param fromPos - Source subentity centroid [x, y]
 * @param toPos - Target subentity centroid [x, y]
 * @param strength - Flow strength (0-1, from decayed aggregate)
 * @param fromColor - Source subentity color (optional, for gradient)
 * @param toColor - Target subentity color (optional, for gradient)
 */
export function drawBridge(
  graphics: PIXI.Graphics,
  fromPos: [number, number],
  toPos: [number, number],
  strength: number,
  fromColor?: string,
  toColor?: string
): void {
  const [ax, ay] = fromPos;
  const [bx, by] = toPos;

  // Cubic Bézier control points (gentle S-curve)
  const cx1 = ax + (bx - ax) * 0.35;
  const cy1 = ay - 120;
  const cx2 = ax + (bx - ax) * 0.65;
  const cy2 = by + 120;

  // Compute width and alpha from strength
  const width = bridgeWidth(strength);
  const alpha = bridgeAlpha(strength);

  // Draw bridge (use energyMd for now; can add gradient later)
  const bridgeColor = parseInt(Colors.energyMd.replace('#', ''), 16);

  graphics.lineStyle(width, bridgeColor, alpha);
  graphics.moveTo(ax, ay);
  graphics.bezierCurveTo(cx1, cy1, cx2, cy2, bx, by);
}

/**
 * Draw bridge with gradient (advanced)
 * Requires creating a temporary texture for gradient
 */
export function drawBridgeWithGradient(
  graphics: PIXI.Graphics,
  fromPos: [number, number],
  toPos: [number, number],
  strength: number,
  fromColor: string,
  toColor: string
): void {
  // TODO: Implement gradient using PIXI.Sprite with gradient texture
  // For now, fallback to solid color
  drawBridge(graphics, fromPos, toPos, strength);
}

/**
 * Add flow particles to bridge (event-driven only)
 * Called when link.flow.summary event fires
 *
 * @param container - Container holding particle sprites
 * @param fromPos - Start position
 * @param toPos - End position
 * @param flowRate - Flow magnitude (affects speed)
 */
export function addFlowParticles(
  container: PIXI.Container,
  fromPos: [number, number],
  toPos: [number, number],
  flowRate: number
): void {
  // Create particle sprite (small yellow dot)
  const particle = new PIXI.Graphics();
  particle.beginFill(parseInt(Colors.energyHi.replace('#', ''), 16), 0.8);
  particle.drawCircle(0, 0, 3);
  particle.endFill();
  particle.position.set(fromPos[0], fromPos[1]);

  container.addChild(particle);

  // Animate particle along Bézier path
  const duration = Math.max(500, 2000 / Math.max(0.1, flowRate)); // Variable speed
  const startTime = Date.now();

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const t = Math.min(1, elapsed / duration);

    // Cubic Bézier interpolation
    const [ax, ay] = fromPos;
    const [bx, by] = toPos;
    const cx1 = ax + (bx - ax) * 0.35;
    const cy1 = ay - 120;
    const cx2 = ax + (bx - ax) * 0.65;
    const cy2 = by + 120;

    const x = Math.pow(1 - t, 3) * ax +
              3 * Math.pow(1 - t, 2) * t * cx1 +
              3 * (1 - t) * Math.pow(t, 2) * cx2 +
              Math.pow(t, 3) * bx;

    const y = Math.pow(1 - t, 3) * ay +
              3 * Math.pow(1 - t, 2) * t * cy1 +
              3 * (1 - t) * Math.pow(t, 2) * cy2 +
              Math.pow(t, 3) * by;

    particle.position.set(x, y);
    particle.alpha = 1 - t; // Fade out as it travels

    if (t < 1) {
      requestAnimationFrame(animate);
    } else {
      container.removeChild(particle);
      particle.destroy();
    }
  };

  requestAnimationFrame(animate);
}

// ========================================================================
// MEMBERSHIP RINGS
// ========================================================================

/**
 * Draw membership rings around node (multi-membership visualization)
 *
 * @param graphics - Pixi Graphics object
 * @param center - Node center position [x, y]
 * @param nodeRadius - Base node radius
 * @param memberships - Array of extra subentity IDs (excluding primary)
 */
export function drawMembershipRings(
  graphics: PIXI.Graphics,
  center: [number, number],
  nodeRadius: number,
  memberships: string[]
): void {
  const [x, y] = center;
  const maxRings = MembershipRingSpacing.maxVisible;
  const rings = memberships.slice(0, maxRings);

  rings.forEach((subentityId, i) => {
    const color = parseInt(MembershipRingColors[i].replace('#', ''), 16);
    const spacing = [
      MembershipRingSpacing.first,
      MembershipRingSpacing.second,
      MembershipRingSpacing.third
    ][i];
    const radius = nodeRadius + spacing;

    graphics.lineStyle(1.5, color, 0.8);
    graphics.drawCircle(x, y, radius);
  });
}

// ========================================================================
// EVENT-DRIVEN ANIMATIONS
// ========================================================================

/**
 * Node flip pulse (threshold crossing)
 * 1000-1200ms ease-in-out halo
 *
 * @param sprite - Node sprite to pulse
 * @param flipOn - True if threshold crossed ON, false if crossed OFF
 */
export function pulseNodeFlip(sprite: PIXI.Container, flipOn: boolean): void {
  const color = flipOn
    ? parseInt(Colors.energyMd.replace('#', ''), 16)
    : parseInt(Colors.grayMd.replace('#', ''), 16);

  // Create halo (outer glow)
  const halo = new PIXI.Graphics();
  halo.lineStyle(3, color, 0.6);
  halo.drawCircle(0, 0, sprite.width / 2 + 6);
  sprite.addChild(halo);

  // Animate pulse (1000-1200ms)
  const duration = 1000 + Math.random() * 200;
  const startTime = Date.now();

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const t = elapsed / duration;

    if (t < 1) {
      // Ease-in-out
      const ease = t < 0.5
        ? 2 * t * t
        : -1 + (4 - 2 * t) * t;

      halo.alpha = 0.6 * (1 - ease);
      halo.scale.set(1 + ease * 0.3);

      requestAnimationFrame(animate);
    } else {
      sprite.removeChild(halo);
      halo.destroy();
    }
  };

  requestAnimationFrame(animate);
}

/**
 * WM breathing animation (working memory top subentities)
 * Gentle alpha modulation, 1800ms cycle
 *
 * @param container - SubEntity hull container
 * @param enabled - True to enable breathing, false to stop
 */
export function breatheHull(container: PIXI.Container, enabled: boolean): void {
  if (!enabled) {
    // Reset alpha to baseline
    container.alpha = 1;
    return;
  }

  const baseAlpha = container.alpha;
  const startTime = Date.now();

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const t = (elapsed % 1800) / 1800; // 1800ms cycle

    // Sine wave: 0.9 → 1.0
    const alpha = 0.9 + 0.1 * Math.sin(t * Math.PI * 2);
    container.alpha = baseAlpha * alpha;

    // Continue if still enabled (check via some flag)
    requestAnimationFrame(animate);
  };

  requestAnimationFrame(animate);
}

/**
 * Stimulus injection spark (dual-channel injector)
 * Brief formation-purple → energy-yellow spark
 *
 * @param container - Particle container
 * @param nodePos - Entry node position [x, y]
 */
export function sparkStimulus(container: PIXI.Container, nodePos: [number, number]): void {
  const [x, y] = nodePos;

  // Create spark graphic
  const spark = new PIXI.Graphics();
  spark.position.set(x, y);
  container.addChild(spark);

  const duration = 600;
  const startTime = Date.now();

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const t = elapsed / duration;

    if (t < 1) {
      // Color transition: formHi → energyHi
      const color = t < 0.5
        ? parseInt(Colors.formHi.replace('#', ''), 16)
        : parseInt(Colors.energyHi.replace('#', ''), 16);

      spark.clear();
      spark.beginFill(color, 0.8 * (1 - t));
      // Draw a simple circle instead of star (PIXI.Graphics doesn't have drawStar in v7)
      spark.drawCircle(0, 0, 4 * (1 + t));
      spark.endFill();

      requestAnimationFrame(animate);
    } else {
      container.removeChild(spark);
      spark.destroy();
    }
  };

  requestAnimationFrame(animate);
}
