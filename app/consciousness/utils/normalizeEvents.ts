/**
 * Event Normalization Utilities
 *
 * Ensures consistent handling of backend events across all dashboard panels.
 * Protects frontend from backend schema evolution by providing defaults,
 * enum mappings, and validation.
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Purpose: Prevent dashboard breakage from evolving event schemas
 */

import type {
  StrideExecEvent,
  WeightsUpdatedTraceEvent,
  PhenomenologyMismatchEvent,
  PhenomenologicalHealthEvent
} from '../hooks/websocket-types';

/**
 * Normalize tier values to standard enum
 */
export function normalizeTier(tier: string | undefined): 'strong' | 'medium' | 'weak' | 'unknown' {
  if (!tier) return 'unknown';

  const normalized = tier.toLowerCase().trim();

  if (normalized === 'strong' || normalized === 'high') return 'strong';
  if (normalized === 'medium' || normalized === 'moderate') return 'medium';
  if (normalized === 'weak' || normalized === 'low') return 'weak';

  return 'unknown';
}

/**
 * Normalize learning reason to standard enum
 */
export function normalizeReason(reason: string | undefined): 'co_activation' | 'causal' | 'background' | 'unknown' {
  if (!reason) return 'unknown';

  const normalized = reason.toLowerCase().trim();

  if (normalized === 'co_activation' || normalized === 'coactivation') return 'co_activation';
  if (normalized === 'causal' || normalized === 'causal_credit') return 'causal';
  if (normalized === 'background' || normalized === 'spillover') return 'background';

  return 'unknown';
}

/**
 * Normalize mismatch type to standard enum
 */
export function normalizeMismatchType(
  type: string | undefined
): 'valence_flip' | 'arousal_mismatch' | 'magnitude_divergence' | 'coherent' | 'unknown' {
  if (!type) return 'unknown';

  const normalized = type.toLowerCase().trim();

  if (normalized === 'valence_flip' || normalized === 'valence') return 'valence_flip';
  if (normalized === 'arousal_mismatch' || normalized === 'arousal') return 'arousal_mismatch';
  if (normalized === 'magnitude_divergence' || normalized === 'magnitude') return 'magnitude_divergence';
  if (normalized === 'coherent' || normalized === 'aligned') return 'coherent';

  return 'unknown';
}

/**
 * Normalize health status to standard enum
 */
export function normalizeHealthStatus(
  status: string | undefined
): 'optimal' | 'good' | 'fair' | 'degraded' | 'critical' | 'unknown' {
  if (!status) return 'unknown';

  const normalized = status.toLowerCase().trim();

  if (normalized === 'optimal' || normalized === 'excellent') return 'optimal';
  if (normalized === 'good' || normalized === 'healthy') return 'good';
  if (normalized === 'fair' || normalized === 'moderate') return 'fair';
  if (normalized === 'degraded' || normalized === 'poor') return 'degraded';
  if (normalized === 'critical' || normalized === 'severe') return 'critical';

  return 'unknown';
}

/**
 * Validate and normalize StrideExecEvent
 */
export function normalizeStrideEvent(event: any): StrideExecEvent {
  const normalizedTier = normalizeTier(event.tier);
  const normalizedReason = normalizeReason(event.reason);

  return {
    type: 'stride.exec',
    entity_id: event.entity_id ?? 'unknown',
    source_node_id: event.source_node_id ?? 'unknown',
    target_node_id: event.target_node_id ?? 'unknown',
    link_id: event.link_id ?? 'unknown',
    base_cost: event.base_cost ?? 0,
    resonance_score: event.resonance_score ?? 0,
    complementarity_score: event.complementarity_score ?? 0,
    resonance_multiplier: event.resonance_multiplier ?? 1.0,
    comp_multiplier: event.comp_multiplier ?? 1.0,
    final_cost: event.final_cost ?? 0,
    tier: normalizedTier === 'unknown' ? undefined : normalizedTier,
    tier_scale: event.tier_scale,
    reason: normalizedReason === 'unknown' ? undefined : normalizedReason,
    stride_utility_zscore: event.stride_utility_zscore,
    learning_enabled: event.learning_enabled ?? false,
    timestamp: event.timestamp ?? new Date().toISOString()
  };
}

/**
 * Validate and normalize WeightsUpdatedTraceEvent
 */
export function normalizeWeightEvent(event: any): WeightsUpdatedTraceEvent {
  return {
    type: 'weights.updated.trace',
    frame_id: event.frame_id ?? 0,
    scope: event.scope ?? 'link',
    cohort: event.cohort ?? 'unknown',
    entity_contexts: event.entity_contexts ?? [],
    global_context: event.global_context ?? false,
    n: event.n ?? 0,
    d_mu: event.d_mu ?? 0,
    d_sigma: event.d_sigma ?? 0,
    timestamp: event.timestamp ?? new Date().toISOString()
  };
}

/**
 * Validate and normalize PhenomenologyMismatchEvent
 */
export function normalizeMismatchEvent(event: any): PhenomenologyMismatchEvent {
  const normalizedMismatchType = normalizeMismatchType(event.mismatch_type);

  return {
    type: 'phenomenology.mismatch',
    frame_id: event.frame_id ?? 0,
    entity_id: event.entity_id ?? 'unknown',
    substrate_valence: event.substrate_valence ?? 0,
    substrate_arousal: event.substrate_arousal ?? 0,
    substrate_mag: event.substrate_mag ?? 0,
    selfreport_valence: event.selfreport_valence ?? 0,
    selfreport_arousal: event.selfreport_arousal ?? 0,
    selfreport_mag: event.selfreport_mag ?? 0,
    divergence: event.divergence ?? 0,
    threshold: event.threshold ?? 0.15,
    mismatch_detected: event.mismatch_detected ?? false,
    mismatch_type: normalizedMismatchType === 'unknown' ? 'coherent' : normalizedMismatchType,
    timestamp: event.timestamp ?? new Date().toISOString()
  };
}

/**
 * Validate and normalize PhenomenologicalHealthEvent
 */
export function normalizeHealthEvent(event: any): PhenomenologicalHealthEvent {
  return {
    type: 'phenomenological_health',
    frame_id: event.frame_id ?? 0,
    entity_id: event.entity_id ?? 'unknown',

    // Flow state metrics
    flow_state: clamp(event.flow_state ?? 0, 0, 1),
    wm_challenge_balance: clamp(event.wm_challenge_balance ?? 0, 0, 1),
    engagement: clamp(event.engagement ?? 0, 0, 1),
    skill_demand_match: clamp(event.skill_demand_match ?? 0, 0, 1),

    // Coherence metrics
    coherence_alignment: clamp(event.coherence_alignment ?? 0, 0, 1),
    resonance_dominance_ratio: clamp(event.resonance_dominance_ratio ?? 0, 0, 1),

    // Multiplicity metrics
    multiplicity_health: clamp(event.multiplicity_health ?? 0, 0, 1),
    distinct_entities_coactive: event.distinct_entities_coactive ?? 0,
    thrashing_detected: event.thrashing_detected ?? false,
    co_activation_stability: clamp(event.co_activation_stability ?? 0, 0, 1),

    overall_health: clamp(event.overall_health ?? 0, 0, 1),
    timestamp: event.timestamp ?? new Date().toISOString()
  };
}

/**
 * Clamp value between min and max
 */
function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

/**
 * Check if event is stale (older than threshold)
 */
export function isEventStale(timestamp: string, thresholdMs: number = 30000): boolean {
  try {
    const eventTime = new Date(timestamp).getTime();
    const now = Date.now();
    return (now - eventTime) > thresholdMs;
  } catch {
    return true; // Assume stale if timestamp is invalid
  }
}

/**
 * Get human-readable time ago string
 */
export function getTimeAgo(timestamp: string): string {
  try {
    const eventTime = new Date(timestamp).getTime();
    const now = Date.now();
    const diffSec = Math.floor((now - eventTime) / 1000);

    if (diffSec < 5) return 'just now';
    if (diffSec < 60) return `${diffSec}s ago`;
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    return `${Math.floor(diffSec / 86400)}d ago`;
  } catch {
    return 'unknown';
  }
}

/**
 * Normalize malformed node type field
 *
 * Backend currently returns "[" instead of actual type due to serialization bug.
 * This normalizer handles the issue gracefully until Atlas fixes the API.
 */
export function normalizeNodeType(type: string | undefined): string {
  if (!type) return 'Unknown';

  // Handle malformed serialization (bug: returns "[" instead of type)
  if (type === '[' || type === '[]' || type.length <= 2) {
    return 'Unknown';
  }

  // Clean up any array syntax that might leak through
  const cleaned = type.replace(/[\[\]"']/g, '').trim();

  if (!cleaned) return 'Unknown';

  // Capitalize first letter for display
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}
