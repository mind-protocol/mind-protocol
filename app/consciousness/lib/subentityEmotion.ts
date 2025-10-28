/**
 * SubEntity Emotion Aggregation
 *
 * Aggregates emotion metadata from active member nodes to subentity level.
 * Per visualization_patterns.md § 2.1: SubEntity color from subentity-level valence/arousal
 *
 * Taxonomy Note: "SubEntity" refers to Scale A weighted neighborhoods (e.g., builder, observer)
 * NOT to be confused with individual nodes or higher-level entities.
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 * Updated: 2025-10-26 (Agent 6 - Taxonomy correction entity → subentity)
 */

import type { EmotionMetadata } from '../hooks/websocket-types';
import type { Node } from '../hooks/useGraphData';

/**
 * Aggregate emotion from member nodes to subentity level
 *
 * Strategy:
 * - Only consider active members (energy > threshold)
 * - Weight by node energy (higher energy = more influence)
 * - Compute weighted average of valence and arousal
 * - Final magnitude = average of member magnitudes
 *
 * @param memberNodes Nodes that belong to this subentity
 * @param nodeEmotions Map of node emotions from WebSocket
 * @returns Aggregated subentity emotion or null if no emotional members
 */
export function aggregateSubEntityEmotion(
  memberNodes: Node[],
  nodeEmotions: Map<string, EmotionMetadata>
): { valence: number; arousal: number; magnitude: number } | null {
  // Filter to active members with emotion data
  const emotionalMembers = memberNodes
    .filter(node => {
      const nodeId = node.id || node.node_id;
      if (!nodeId) return false;

      const emotion = nodeEmotions.get(nodeId);
      if (!emotion || emotion.magnitude < 0.05) return false;

      // Only active nodes contribute
      const energy = node.energy || 0;
      const theta = (node as any).activation_threshold || 0.1;
      return energy > theta;
    })
    .map(node => {
      const nodeId = node.id || node.node_id!;
      const emotion = nodeEmotions.get(nodeId)!;
      const energy = node.energy || 0;

      // Extract valence and arousal from axes
      const valence = emotion.axes.find(a => a.axis === 'valence')?.value ?? 0;
      const arousal = emotion.axes.find(a => a.axis === 'arousal')?.value ?? 0;

      return { valence, arousal, magnitude: emotion.magnitude, energy };
    });

  if (emotionalMembers.length === 0) {
    return null;
  }

  // Compute weighted averages
  const totalEnergy = emotionalMembers.reduce((sum, m) => sum + m.energy, 0);

  if (totalEnergy === 0) {
    // Fall back to simple average if no energy
    const avgValence = emotionalMembers.reduce((sum, m) => sum + m.valence, 0) / emotionalMembers.length;
    const avgArousal = emotionalMembers.reduce((sum, m) => sum + m.arousal, 0) / emotionalMembers.length;
    const avgMagnitude = emotionalMembers.reduce((sum, m) => sum + m.magnitude, 0) / emotionalMembers.length;

    return { valence: avgValence, arousal: avgArousal, magnitude: avgMagnitude };
  }

  // Weighted average by energy
  const weightedValence = emotionalMembers.reduce((sum, m) => sum + m.valence * m.energy, 0) / totalEnergy;
  const weightedArousal = emotionalMembers.reduce((sum, m) => sum + m.arousal * m.energy, 0) / totalEnergy;
  const weightedMagnitude = emotionalMembers.reduce((sum, m) => sum + m.magnitude * m.energy, 0) / totalEnergy;

  return {
    valence: weightedValence,
    arousal: weightedArousal,
    magnitude: weightedMagnitude
  };
}

/**
 * Get subentity-level energy from member nodes
 *
 * Per observability_events.md: subentities expose **derived** energy (aggregation)
 *
 * @param memberNodes Nodes that belong to this subentity
 * @returns Sum of active member energies
 */
export function aggregateSubEntityEnergy(memberNodes: Node[]): number {
  return memberNodes.reduce((sum, node) => {
    const energy = node.energy || 0;
    const theta = (node as any).activation_threshold || 0.1;
    // Only count active members
    return energy > theta ? sum + energy : sum;
  }, 0);
}

/**
 * Calculate subentity coherence from member patterns
 *
 * Coherence = how aligned the member emotions are
 * High coherence = members have similar affect
 * Low coherence = members have divergent affect
 *
 * @param memberNodes Nodes that belong to this subentity
 * @param nodeEmotions Map of node emotions
 * @returns Coherence score 0-1
 */
export function calculateSubEntityCoherence(
  memberNodes: Node[],
  nodeEmotions: Map<string, EmotionMetadata>
): number {
  // Get emotional members
  const emotionalMembers = memberNodes
    .filter(node => {
      const nodeId = node.id || node.node_id;
      if (!nodeId) return false;
      const emotion = nodeEmotions.get(nodeId);
      return emotion && emotion.magnitude > 0.05;
    })
    .map(node => {
      const nodeId = node.id || node.node_id!;
      const emotion = nodeEmotions.get(nodeId)!;
      const valence = emotion.axes.find(a => a.axis === 'valence')?.value ?? 0;
      const arousal = emotion.axes.find(a => a.axis === 'arousal')?.value ?? 0;
      return { valence, arousal };
    });

  if (emotionalMembers.length < 2) {
    return 1.0; // Perfect coherence if only one or zero emotional members
  }

  // Calculate average emotion
  const avgValence = emotionalMembers.reduce((sum, m) => sum + m.valence, 0) / emotionalMembers.length;
  const avgArousal = emotionalMembers.reduce((sum, m) => sum + m.arousal, 0) / emotionalMembers.length;

  // Calculate average distance from mean
  const avgDeviation = emotionalMembers.reduce((sum, m) => {
    const dValence = m.valence - avgValence;
    const dArousal = m.arousal - avgArousal;
    const distance = Math.sqrt(dValence * dValence + dArousal * dArousal);
    return sum + distance;
  }, 0) / emotionalMembers.length;

  // Normalize deviation to 0-1 (max possible deviation in 2D unit space is sqrt(8) ≈ 2.83)
  const maxDeviation = 2.83;
  const coherence = 1 - Math.min(avgDeviation / maxDeviation, 1);

  return coherence;
}
