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
export function normalizeStrideEvent(event: Partial<StrideExecEvent>): StrideExecEvent {
  return {
    type: 'stride.exec',
    frame_id: event.frame_id ?? 0,
    citizen_id: event.citizen_id ?? 'unknown',
    src_node: event.src_node ?? 'unknown',
    dst_node: event.dst_node ?? 'unknown',
    tier: normalizeTier(event.tier),
    reason: normalizeReason(event.reason),
    learning_enabled: event.learning_enabled ?? false,
    timestamp: event.timestamp ?? new Date().toISOString()
  };
}

/**
 * Validate and normalize WeightsUpdatedTraceEvent
 */
export function normalizeWeightEvent(event: Partial<WeightsUpdatedTraceEvent>): WeightsUpdatedTraceEvent {
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
export function normalizeMismatchEvent(
  event: Partial<PhenomenologyMismatchEvent>
): PhenomenologyMismatchEvent {
  return {
    type: 'phenomenology.mismatch',
    frame_id: event.frame_id ?? 0,
    mismatch_detected: event.mismatch_detected ?? false,
    mismatch_type: normalizeMismatchType(event.mismatch_type),
    divergence: event.divergence ?? 0,
    threshold: event.threshold ?? 0.15,
    substrate_valence: event.substrate_valence ?? 0,
    substrate_arousal: event.substrate_arousal ?? 0,
    selfreport_valence: event.selfreport_valence ?? 0,
    selfreport_arousal: event.selfreport_arousal ?? 0,
    timestamp: event.timestamp ?? new Date().toISOString()
  };
}

/**
 * Validate and normalize PhenomenologicalHealthEvent
 */
export function normalizeHealthEvent(
  event: Partial<PhenomenologicalHealthEvent>
): PhenomenologicalHealthEvent {
  return {
    type: 'health.phenomenological',
    frame_id: event.frame_id ?? 0,
    overall_health: clamp(event.overall_health ?? 0, 0, 1),
    flow_state: clamp(event.flow_state ?? 0, 0, 1),
    coherence_alignment: clamp(event.coherence_alignment ?? 0, 0, 1),
    multiplicity_health: clamp(event.multiplicity_health ?? 0, 0, 1),
    thrashing_detected: event.thrashing_detected ?? false,
    status: normalizeHealthStatus(event.status),
    narrative: event.narrative ?? 'No health narrative available',
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
