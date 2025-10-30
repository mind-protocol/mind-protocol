/**
 * Graph Health Diagnostics - Type Definitions
 *
 * WebSocket event types for real-time health monitoring of consciousness graphs.
 * All types match the specification in docs/specs/v2/ops_and_viz/GRAPH_HEALTH_DIAGNOSTICS.md §D
 *
 * Terminology: "SubEntity" (not "Entity") per TAXONOMY_RECONCILIATION.md §3
 */

export type HealthStatus = 'GREEN' | 'AMBER' | 'RED';
export type Trend = 'rising' | 'stable' | 'falling';

/**
 * 1. Subentity-to-Node Density (E/N)
 * Measures number of subentities relative to nodes.
 */
export interface DensityMetric {
  subentities: number;        // Total SubEntity count
  nodes: number;              // Total Node count
  density: number;            // E/N ratio
  percentile: number;         // Where current density sits in history
  trend: Trend;
  status: HealthStatus;
}

/**
 * 2. Membership Overlap (r = M/N)
 * Measures average memberships per node.
 */
export interface OverlapMetric {
  total_memberships: number;  // M
  total_nodes: number;        // N
  overlap_ratio: number;      // M/N
  percentile: number;
  trend: Trend;
  status: HealthStatus;
}

/**
 * 3. SubEntity Size & Dominance
 * Distribution of members per subentity; do a few subentities dominate?
 */
export interface SubEntitySizeMetric {
  median_size: number;
  mean_size: number;
  gini_coefficient: number;   // 0 = perfect equality, 1 = one subentity has all
  size_distribution: {
    q25: number;
    q50: number;
    q75: number;
    q90: number;
  };
  top_subentities: Array<{
    id: string;
    name: string;
    size: number;
    percentile: number;       // Size percentile within this graph
  }>;
  status: HealthStatus;
}

/**
 * 4. Orphan Ratio
 * Fraction of nodes without any MEMBER_OF link.
 */
export interface OrphanMetric {
  total_nodes: number;
  orphan_count: number;
  orphan_ratio: number;         // 0-1
  new_orphans_last_24h: number; // Rate tracking
  percentile: number;
  trend: Trend;
  status: HealthStatus;
  sample_orphans: Array<{       // For targeted inspection
    id: string;
    name: string;
    type: string;
    created_at: number;
  }>;
}

/**
 * 5. SubEntity Coherence
 * Semantic cohesiveness of each subentity (member similarity).
 */
export interface CoherenceMetric {
  subentity_coherence: Array<{
    subentity_id: string;
    subentity_name: string;
    size: number;
    coherence: number;          // 0-1 (mean pairwise similarity)
    coherence_ema: number;      // EMA over time
    coherence_trend: Trend;
    status: HealthStatus;
  }>;
  overall_median_coherence: number;
  flagged_subentities: string[];   // Low coherence + large size
}

/**
 * 6. Highway Health (RELATES_TO)
 * Connectivity between subentities built from executed boundary strides.
 */
export interface HighwayMetric {
  total_highways: number;
  total_crossings: number;      // Sum of all h.count
  mean_crossings_per_highway: number;
  highways: Array<{
    source_id: string;
    source_name: string;
    target_id: string;
    target_name: string;
    ease: number;               // 0-1
    crossings: number;
    last_crossed: number;       // Timestamp
  }>;
  backbone_highways: Array<{    // Top 20 by crossings
    source_name: string;
    target_name: string;
    crossings: number;
  }>;
  status: HealthStatus;
}

/**
 * 7. WM Health
 * SubEntities selected per frame, vitality (E/Θ).
 */
export interface WMHealthMetric {
  window_frames: number;         // How many frames analyzed
  mean_selected: number;         // Mean subentities active per frame
  median_selected: number;
  p90_selected: number;
  mean_vitality: number;         // E/Θ
  flip_rate: number;             // Flips per frame
  stability_score: number;       // Low flip rate + stable count = high
  status: HealthStatus;
}

/**
 * 8. Context Reconstruction Health
 * Time-to-reconstruct and similarity to reference context.
 */
export interface ReconstructionMetric {
  window_reconstructions: number;
  mean_latency_ms: number;
  p50_latency_ms: number;
  p90_latency_ms: number;
  mean_similarity: number;
  p50_similarity: number;
  p10_similarity: number;       // Worst 10%
  status: HealthStatus;
}

/**
 * 9. Learning Flux
 * Rate of MEMBER_OF weight updates and prunes.
 */
export interface LearningFluxMetric {
  window_hours: number;
  weight_updates: number;        // Total weight changes
  prunes: number;                // Total membership removals
  update_rate: number;           // Updates per hour
  prune_rate: number;            // Prunes per hour
  percentile_update: number;     // Where current rate sits historically
  percentile_prune: number;
  trend: Trend;
  status: HealthStatus;
}

/**
 * 10. Sector Connectivity
 * How different sectors/roles interact.
 */
export interface SectorConnectivityMetric {
  sectors: string[];
  connectivity_matrix: number[][];  // sectors × sectors adjacency
  modularity_score: number;         // Optional if GDS available
  cross_sector_highways: number;
  status: HealthStatus;
}

/**
 * Recommended Procedure
 */
export interface Procedure {
  metric: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  procedure: string;
  description: string;
  parameters?: Record<string, any>;
}

/**
 * EVENT TYPE 1: Health Snapshot (Periodic)
 * Emitted every 60 seconds with full health metrics
 */
export interface GraphHealthSnapshotEvent {
  type: 'graph.health.snapshot';
  graph_id: string;
  timestamp: number;
  history_window_days: number;      // Used for percentile calculation

  // Summary
  overall_status: HealthStatus;
  flagged_metrics: string[];        // Metrics in AMBER/RED

  // 10 Core Metrics
  density: DensityMetric;
  overlap: OverlapMetric;
  subentity_size: SubEntitySizeMetric;
  orphans: OrphanMetric;
  coherence: CoherenceMetric;
  highways: HighwayMetric;
  wm_health: WMHealthMetric;
  reconstruction: ReconstructionMetric;
  learning_flux: LearningFluxMetric;
  sector_connectivity: SectorConnectivityMetric;

  // Trend indicators (computed from history)
  trends: {
    density: Trend;
    overlap: Trend;
    orphan_ratio: Trend;
    median_subentity_size: Trend;
    mean_coherence: Trend;
  };
}

/**
 * EVENT TYPE 2: Health Alert (Status Change)
 * Emitted when overall status changes or new critical issues detected
 */
export interface GraphHealthAlertEvent {
  type: 'graph.health.alert';
  graph_id: string;
  timestamp: number;
  severity: HealthStatus;
  previous_severity: HealthStatus;

  flagged_metrics: Array<{
    metric: string;
    status: 'AMBER' | 'RED';
    current_value: number;
    percentile: number;
    threshold: string;              // e.g., "q90", "q10"
  }>;

  procedures: Procedure[];
}

/**
 * EVENT TYPE 3: Procedure Execution (Lifecycle)
 * Emitted during procedure execution
 */
export type ProcedureName =
  | 'backfill_orphans'
  | 'sparsify_memberships'
  | 'split_subentity'
  | 'merge_subentities'
  | 'seed_highways';

export type ProcedureEventType =
  | 'graph.health.procedure.started'
  | 'graph.health.procedure.progress'
  | 'graph.health.procedure.completed'
  | 'graph.health.procedure.failed';

export interface GraphHealthProcedureEvent {
  type: ProcedureEventType;
  graph_id: string;
  timestamp: number;
  procedure_id: string;             // Unique execution ID
  procedure: ProcedureName;

  // For started
  parameters?: Record<string, any>;

  // For progress
  progress?: {
    current: number;
    total: number;
    message: string;
  };

  // For completed
  result?: {
    before: Record<string, number>;   // Metrics before procedure
    after: Record<string, number>;    // Metrics after procedure
    changes: {
      orphan_ratio?: number;          // Delta
      overlap_ratio?: number;
      median_subentity_size?: number;
      // ... other metric changes
    };
    duration_ms: number;
  };

  // For failed
  error?: {
    message: string;
    code: string;
    retryable: boolean;
  };
}

/**
 * EVENT TYPE 4: Historical Metrics (On Request)
 * Client sends request, server responds with historical data
 */
export interface HealthHistoryRequest {
  type: 'graph.health.history.request';
  graph_id: string;
  window_days: number;              // How far back to fetch
  metrics?: string[];               // Optional: specific metrics only
}

export interface HealthHistorySample {
  timestamp: number;
  density: number;
  overlap_ratio: number;
  orphan_ratio: number;
  median_subentity_size: number;
  mean_coherence: number;
  highway_count: number;
  mean_wm_subentities: number;
  p90_reconstruction_ms: number;
  update_rate: number;
  prune_rate: number;
}

export interface HealthHistoryResponse {
  type: 'graph.health.history.response';
  graph_id: string;
  window_days: number;

  samples: HealthHistorySample[];

  percentiles: {
    density: { q10: number; q20: number; q80: number; q90: number; };
    overlap_ratio: { q10: number; q20: number; q80: number; q90: number; };
    orphan_ratio: { q10: number; q20: number; q80: number; q90: number; };
    median_subentity_size: { q10: number; q20: number; q80: number; q90: number; };
  };
}

/**
 * Union type for all health WebSocket events
 */
export type HealthWebSocketEvent =
  | GraphHealthSnapshotEvent
  | GraphHealthAlertEvent
  | GraphHealthProcedureEvent
  | HealthHistoryResponse;
