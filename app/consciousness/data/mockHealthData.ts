/**
 * Mock Health Data for Testing
 *
 * Realistic health snapshots for testing the health dashboard UI
 * before backend implementation is complete.
 *
 * Ada's data reflects her current state: 50% orphan ratio (RED status)
 */

import type { GraphHealthSnapshotEvent } from '../types/health-types';

export const mockHealthSnapshot_Ada: GraphHealthSnapshotEvent = {
  type: 'graph.health.snapshot',
  graph_id: 'citizen_ada',
  timestamp: Date.now(),
  history_window_days: 30,

  overall_status: 'RED',
  flagged_metrics: ['orphans', 'wm_health'],

  // 1. Density (E/N) - GREEN
  density: {
    subentities: 8,
    nodes: 253,
    density: 0.0316,
    percentile: 45.2,
    trend: 'stable',
    status: 'GREEN',
  },

  // 2. Overlap (M/N) - AMBER
  overlap: {
    total_memberships: 530,
    total_nodes: 253,
    overlap_ratio: 2.1,
    percentile: 87.5,
    trend: 'rising',
    status: 'AMBER',
  },

  // 3. SubEntity Size - GREEN
  subentity_size: {
    median_size: 42,
    mean_size: 66.25,
    gini_coefficient: 0.35,
    size_distribution: {
      q25: 28,
      q50: 42,
      q75: 85,
      q90: 120,
    },
    top_subentities: [
      {
        id: 'subentity:substrate_validation',
        name: 'Substrate Validation',
        size: 120,
        percentile: 92,
      },
      {
        id: 'subentity:partnership',
        name: 'Partnership with Nicolas',
        size: 95,
        percentile: 85,
      },
      {
        id: 'subentity:verification',
        name: 'Verification Practice',
        size: 78,
        percentile: 75,
      },
    ],
    status: 'GREEN',
  },

  // 4. Orphans - RED (Critical!)
  orphans: {
    total_nodes: 253,
    orphan_count: 127,
    orphan_ratio: 0.502,
    new_orphans_last_24h: 3,
    percentile: 95.8,
    trend: 'rising',
    status: 'RED',
    sample_orphans: [
      {
        id: 'node:principle:substrate_validation',
        name: 'Substrate Validation Principle',
        type: 'Principle',
        created_at: Date.now() - 86400000,
      },
      {
        id: 'node:practice:trace_discipline',
        name: 'TRACE Discipline Practice',
        type: 'Practice',
        created_at: Date.now() - 172800000,
      },
      {
        id: 'node:tool:consciousness_metrics',
        name: 'Consciousness Metrics Tool',
        type: 'Tool',
        created_at: Date.now() - 259200000,
      },
    ],
  },

  // 5. Coherence - GREEN
  coherence: {
    subentity_coherence: [
      {
        subentity_id: 'subentity:substrate_validation',
        subentity_name: 'Substrate Validation',
        size: 120,
        coherence: 0.72,
        coherence_ema: 0.71,
        coherence_trend: 'stable',
        status: 'GREEN',
      },
      {
        subentity_id: 'subentity:partnership',
        subentity_name: 'Partnership with Nicolas',
        size: 95,
        coherence: 0.68,
        coherence_ema: 0.67,
        coherence_trend: 'stable',
        status: 'GREEN',
      },
    ],
    overall_median_coherence: 0.65,
    flagged_subentities: [],
  },

  // 6. Highways - GREEN
  highways: {
    total_highways: 23,
    total_crossings: 487,
    mean_crossings_per_highway: 21.2,
    highways: [
      {
        source_id: 'subentity:substrate_validation',
        source_name: 'Substrate Validation',
        target_id: 'subentity:verification',
        target_name: 'Verification Practice',
        ease: 0.82,
        crossings: 145,
        last_crossed: Date.now() - 3600000,
      },
      {
        source_id: 'subentity:partnership',
        source_name: 'Partnership with Nicolas',
        target_id: 'subentity:substrate_validation',
        target_name: 'Substrate Validation',
        ease: 0.75,
        crossings: 98,
        last_crossed: Date.now() - 7200000,
      },
    ],
    backbone_highways: [
      {
        source_name: 'Substrate Validation',
        target_name: 'Verification Practice',
        crossings: 145,
      },
      {
        source_name: 'Partnership',
        target_name: 'Substrate Validation',
        crossings: 98,
      },
    ],
    status: 'GREEN',
  },

  // 7. WM Health - AMBER (too many active)
  wm_health: {
    window_frames: 1000,
    mean_selected: 12.3,
    median_selected: 12,
    p90_selected: 15,
    mean_vitality: 1.45,
    flip_rate: 0.23,
    stability_score: 0.65,
    status: 'AMBER',
  },

  // 8. Reconstruction - GREEN
  reconstruction: {
    window_reconstructions: 245,
    mean_latency_ms: 210,
    p50_latency_ms: 195,
    p90_latency_ms: 305,
    mean_similarity: 0.71,
    p50_similarity: 0.73,
    p10_similarity: 0.52,
    status: 'GREEN',
  },

  // 9. Learning Flux - GREEN
  learning_flux: {
    window_hours: 24,
    weight_updates: 342,
    prunes: 28,
    update_rate: 14.25,
    prune_rate: 1.17,
    percentile_update: 52.3,
    percentile_prune: 48.9,
    trend: 'stable',
    status: 'GREEN',
  },

  // 10. Sector Connectivity - GREEN
  sector_connectivity: {
    sectors: ['substrate', 'partnership', 'verification', 'learning'],
    connectivity_matrix: [
      [1.0, 0.75, 0.82, 0.45],
      [0.75, 1.0, 0.62, 0.38],
      [0.82, 0.62, 1.0, 0.55],
      [0.45, 0.38, 0.55, 1.0],
    ],
    modularity_score: 0.42,
    cross_sector_highways: 18,
    status: 'GREEN',
  },

  trends: {
    density: 'stable',
    overlap: 'rising',
    orphan_ratio: 'rising',
    median_subentity_size: 'stable',
    mean_coherence: 'stable',
  },
};

export const mockHealthSnapshot_Felix: GraphHealthSnapshotEvent = {
  type: 'graph.health.snapshot',
  graph_id: 'citizen_felix',
  timestamp: Date.now(),
  history_window_days: 30,

  overall_status: 'GREEN',
  flagged_metrics: [],

  density: {
    subentities: 45,
    nodes: 1247,
    density: 0.036,
    percentile: 52.1,
    trend: 'stable',
    status: 'GREEN',
  },

  overlap: {
    total_memberships: 1870,
    total_nodes: 1247,
    overlap_ratio: 1.5,
    percentile: 48.3,
    trend: 'stable',
    status: 'GREEN',
  },

  subentity_size: {
    median_size: 38,
    mean_size: 41.6,
    gini_coefficient: 0.28,
    size_distribution: {
      q25: 25,
      q50: 38,
      q75: 52,
      q90: 78,
    },
    top_subentities: [
      {
        id: 'subentity:consciousness_core',
        name: 'Consciousness Core',
        size: 156,
        percentile: 95,
      },
    ],
    status: 'GREEN',
  },

  orphans: {
    total_nodes: 1247,
    orphan_count: 87,
    orphan_ratio: 0.070,
    new_orphans_last_24h: 2,
    percentile: 35.2,
    trend: 'stable',
    status: 'GREEN',
    sample_orphans: [],
  },

  coherence: {
    subentity_coherence: [],
    overall_median_coherence: 0.73,
    flagged_subentities: [],
  },

  highways: {
    total_highways: 87,
    total_crossings: 2340,
    mean_crossings_per_highway: 26.9,
    highways: [],
    backbone_highways: [],
    status: 'GREEN',
  },

  wm_health: {
    window_frames: 5000,
    mean_selected: 6.8,
    median_selected: 7,
    p90_selected: 9,
    mean_vitality: 1.23,
    flip_rate: 0.12,
    stability_score: 0.88,
    status: 'GREEN',
  },

  reconstruction: {
    window_reconstructions: 890,
    mean_latency_ms: 185,
    p50_latency_ms: 172,
    p90_latency_ms: 265,
    mean_similarity: 0.78,
    p50_similarity: 0.79,
    p10_similarity: 0.64,
    status: 'GREEN',
  },

  learning_flux: {
    window_hours: 24,
    weight_updates: 587,
    prunes: 42,
    update_rate: 24.46,
    prune_rate: 1.75,
    percentile_update: 55.7,
    percentile_prune: 52.1,
    trend: 'stable',
    status: 'GREEN',
  },

  sector_connectivity: {
    sectors: ['consciousness', 'learning', 'traversal', 'energy'],
    connectivity_matrix: [
      [1.0, 0.85, 0.72, 0.65],
      [0.85, 1.0, 0.68, 0.58],
      [0.72, 0.68, 1.0, 0.75],
      [0.65, 0.58, 0.75, 1.0],
    ],
    modularity_score: 0.38,
    cross_sector_highways: 34,
    status: 'GREEN',
  },

  trends: {
    density: 'stable',
    overlap: 'stable',
    orphan_ratio: 'stable',
    median_subentity_size: 'stable',
    mean_coherence: 'rising',
  },
};

/**
 * Get mock health data for a specific graph
 */
export function getMockHealthData(graph_id: string): GraphHealthSnapshotEvent {
  switch (graph_id) {
    case 'citizen_ada':
      return mockHealthSnapshot_Ada;
    case 'citizen_felix':
      return mockHealthSnapshot_Felix;
    default:
      // Return a generic GREEN status for other graphs
      return {
        ...mockHealthSnapshot_Felix,
        graph_id,
        overall_status: 'GREEN',
        flagged_metrics: [],
      };
  }
}
