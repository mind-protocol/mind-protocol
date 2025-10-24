/**
 * WebSocket Event Types
 *
 * Type definitions for real-time consciousness operations events
 * streamed from the backend consciousness engine.
 *
 * Backend: orchestration/control_api.py (/api/ws endpoint)
 * Protocol: WebSocket at ws://localhost:8000/api/ws
 *
 * Author: Iris "The Aperture"
 * Integration with: Felix "Ironhand"'s WebSocket infrastructure
 */

/**
 * Subentity Activity Event
 *
 * Emitted by SubEntity during graph traversal.
 * Frequency: Every node traversal
 * Source: orchestration/sub_entity.py
 */
export interface EntityActivityEvent {
  type: 'entity_activity';
  entity_id: string;              // e.g., "builder", "observer"
  current_node: string;            // Node ID currently exploring
  need_type: string;               // e.g., "pattern_validation", "context_gathering"
  energy_used: number;             // Energy consumed so far this cycle
  energy_budget: number;           // Total energy budget for this cycle
  nodes_visited_count: number;    // Total nodes visited this cycle
  sequence_position: number;       // Global sequence number across all cycles
  timestamp: string;               // ISO 8601 timestamp
}

/**
 * Threshold Crossing Event
 *
 * Emitted when a node crosses activation threshold for an subentity.
 * Frequency: On threshold crossing (up or down)
 * Source: orchestration/dynamic_prompt_generator.py
 */
export interface ThresholdCrossingEvent {
  type: 'threshold_crossing';
  entity_id: string;               // Subentity for which threshold crossed
  node_id: string;                 // Node that crossed threshold
  node_name: string;               // Human-readable node text
  direction: 'on' | 'off';         // Crossed up (activated) or down (deactivated)
  entity_activity: number;         // Current subentity activity level (0-1)
  threshold: number;               // Threshold value that was crossed
  timestamp: string;               // ISO 8601 timestamp
}

/**
 * Consciousness State Event
 *
 * Emitted after global energy measurement.
 * Frequency: After each tick (variable frequency based on system state)
 * Source: orchestration/consciousness_engine.py
 */
export interface ConsciousnessStateEvent {
  type: 'consciousness_state';
  network_id: string;              // e.g., "N1", "N2", "N3"
  global_energy: number;          // System-wide energy (0-1)
  branching_ratio: number;         // Mapped branching ratio (0-1)
  raw_sigma: number;               // Raw branching ratio σ (unbounded)
  tick_interval_ms: number;        // Current tick interval in milliseconds
  tick_frequency_hz: number;       // Current tick frequency in Hz
  consciousness_state: string;     // e.g., "alert", "engaged", "calm", "drowsy", "dormant"
  time_since_last_event: number;   // Seconds since last external event
  timestamp: string;               // ISO 8601 timestamp
}

/**
 * V2 Event Format - Frame-based consciousness streaming
 * Source: orchestration/consciousness_engine_v2.py
 *
 * These events provide frame-by-frame consciousness updates with
 * working memory tracking and link flow visualization.
 */

/**
 * Frame Start Event (v2) / Tick Frame Event
 *
 * Marks the beginning of a consciousness frame.
 * Contains branching ratio (ρ), timing info, and subentity palette.
 *
 * Extended fields per tick_speed.md and criticality.md specs:
 * - dt_ms: wall-clock time since last tick
 * - interval_sched: scheduled interval
 * - dt_used: physics dt actually used (capped)
 * - rho: spectral radius (criticality metric)
 * - safety_state: system stability classification
 * - notes: diagnostic messages (e.g., "dt capped", "EMA smoothing")
 */
export interface FrameStartEvent {
  type: 'frame.start';
  v: '2';
  kind: 'frame.start';
  frame_id: number;

  // Criticality metrics
  rho?: number;                    // Spectral radius (branching ratio)
  safety_state?: 'subcritical' | 'critical' | 'supercritical'; // System stability

  // Timing metrics
  dt_ms?: number;                  // Wall-clock milliseconds since last tick
  interval_sched?: number;         // Scheduled interval (ms)
  dt_used?: number;                // Physics dt actually used (capped)
  notes?: string;                  // Diagnostic notes

  // Three-Factor Tick Speed (Priority 3)
  tick_reason?: 'stimulus' | 'activation' | 'arousal_floor'; // Which factor won
  interval_stimulus?: number;      // Stimulus-driven interval (ms)
  interval_activation?: number;    // Activation-driven interval (ms)
  interval_arousal?: number;       // Arousal floor interval (ms)
  total_active_energy?: number;    // For activation computation
  mean_arousal?: number;           // For arousal floor computation

  // Entity visualization
  entity_palette?: Array<{
    id: string;
    name?: string;
    color: string;
  }>;
}

/**
 * Working Memory Emission Event (v2)
 *
 * Lists all nodes currently in working memory.
 * Working memory = set of active nodes in consciousness.
 */
export interface WmEmitEvent {
  type: 'wm.emit';
  v: '2';
  kind: 'wm.emit';
  frame_id: number;
  node_ids: string[];              // Node IDs in working memory
}

/**
 * Node Flip Event (v2)
 *
 * Emitted when a node crosses activation threshold.
 */
export interface NodeFlipEvent {
  type: 'node.flip';
  v: '2';
  kind: 'node.flip';
  frame_id: number;
  node_id: string;
  direction: 'on' | 'off';         // Activated or deactivated
  entity_id?: string;              // Which subentity caused the flip
}

/**
 * Link Flow Summary Event (v2)
 *
 * Aggregated link traversal statistics for visualization.
 */
export interface LinkFlowSummaryEvent {
  type: 'link.flow.summary';
  v: '2';
  kind: 'link.flow.summary';
  frame_id: number;
  flows: Array<{
    link_id: string;
    count: number;                 // Number of traversals this frame
    entity_ids: string[];          // Which subentities traversed
  }>;
}

/**
 * Frame End Event (v2)
 *
 * Marks the end of a consciousness frame with diagnostics.
 *
 * Extended fields per diffusion_v2.md spec:
 * - Conservation tracking (energy_in, energy_transferred, energy_decay, deltaE_total)
 * - Frontier size metrics (active_count, shadow_count)
 * - Diffusion metrics (mean_degree_active, diffusion_radius)
 */
export interface FrameEndEvent {
  type: 'frame.end';
  v: '2';
  kind: 'frame.end';
  frame_id: number;

  // Conservation metrics
  energy_in?: number;              // Sum of stimulus injections this frame
  energy_transferred?: number;     // Sum of all |ΔE| moved
  energy_decay?: number;           // Total loss to decay this frame
  deltaE_total?: number;           // Conservation error (should be ≈0)
  conservation_error_pct?: number; // Percentage error

  // Frontier metrics
  active_count?: number;           // Count of nodes above threshold
  shadow_count?: number;           // Count of 1-hop neighbors

  // Diffusion metrics
  mean_degree_active?: number;     // Average out-degree of active nodes
  diffusion_radius?: number;       // Distance from initial stimuli
}

/**
 * Emotion Events - Emotion Coloring Mechanism
 *
 * These events track emotional metadata (separate from activation energy)
 * that colors nodes and links during traversal.
 *
 * Source: orchestration/mechanisms/emotion_coloring.py
 * Spec: docs/specs/v2/emotion/emotion_coloring.md
 */

/**
 * Emotion Axis Value
 *
 * Represents a single axis in the emotion vector with its magnitude.
 * For Phase 1: [("valence", value), ("arousal", value)]
 */
export interface EmotionAxis {
  axis: string;  // e.g., "valence", "arousal"
  value: number; // -1 to +1
}

/**
 * Node Emotion Update Event
 *
 * Emitted when a node's emotion vector is colored during traversal.
 * Sampled at EMOTION_COLOR_SAMPLE_RATE to manage bandwidth.
 *
 * Frequency: Sampled (e.g., 10% of node visits)
 * Source: emotion_coloring.color_element()
 */
export interface NodeEmotionUpdateEvent {
  type: 'node.emotion.update';
  node_id: string;           // Node ID that was colored
  emotion_magnitude: number; // ||E_emo|| after update (0-1)
  top_axes: EmotionAxis[];   // Top K emotion axes, e.g., [{ axis: "valence", value: 0.42 }]
  delta_mag: number;         // Change in magnitude since last update
  timestamp: string;         // ISO 8601 timestamp
}

/**
 * Link Emotion Update Event
 *
 * Emitted when a link's emotion vector is colored during traversal.
 * Sampled at EMOTION_COLOR_SAMPLE_RATE to manage bandwidth.
 *
 * Frequency: Sampled (e.g., 10% of link traversals)
 * Source: emotion_coloring.color_element()
 */
export interface LinkEmotionUpdateEvent {
  type: 'link.emotion.update';
  link_id: string;           // Link ID that was colored
  emotion_magnitude: number; // ||E_emo|| after update (0-1)
  top_axes: EmotionAxis[];   // Top K emotion axes
  delta_mag: number;         // Change in magnitude since last update
  timestamp: string;         // ISO 8601 timestamp
}

/**
 * Stride Execution Event (Planned - Phase 1)
 *
 * Emitted when a stride (link traversal) is executed with emotion attribution.
 * Shows WHY a path was chosen: semantic similarity vs emotional factors.
 *
 * Frequency: Every stride execution
 * Source: sub_entity_traversal.py (planned integration)
 */
export interface StrideExecEvent {
  type: 'stride.exec';
  entity_id: string;          // Active entity executing stride
  source_node_id: string;      // Source node
  target_node_id: string;      // Target node
  link_id: string;             // Link traversed
  base_cost: number;           // Semantic cost before emotion gates
  resonance_score: number;     // Similarity to current affect (0-1)
  complementarity_score: number; // Opposition to current affect (0-1)
  resonance_multiplier: number;  // Cost reduction from resonance (0.5-1.0)
  comp_multiplier: number;       // Cost reduction from complementarity (0.5-1.0)
  final_cost: number;          // Final cost after emotion gates

  // 3-Tier Strengthening Fields (Priority 2)
  tier?: 'strong' | 'medium' | 'weak';  // Strengthening tier
  tier_scale?: number;                   // Scale factor (1.0 | 0.6 | 0.3)
  reason?: 'co_activation' | 'causal' | 'background'; // Why this tier
  stride_utility_zscore?: number;        // Z-scored Φ for noise filtering
  learning_enabled?: boolean;            // Whether learning occurred

  timestamp: string;           // ISO 8601 timestamp
}

/**
 * Affective Telemetry Events - PR-A Instrumentation Foundation
 *
 * Per IMPLEMENTATION_PLAN.md PR-A.2: Event schema definitions for affective coupling mechanisms.
 * These events are emitted when AFFECTIVE_TELEMETRY_ENABLED=true (default: false).
 *
 * Source: orchestration/core/events.py (backend definitions)
 * Author: Felix "Ironhand" (backend), Iris "The Aperture" (frontend types)
 * Date: 2025-10-23
 * PR: PR-A (Instrumentation Foundation - ZERO RISK)
 */

/**
 * Affective Threshold Event
 *
 * Emitted when affect modulates activation threshold (PR-B mechanism).
 * Frequency: Per threshold computation (sampled at TELEMETRY_SAMPLE_RATE)
 */
export interface AffectiveThresholdEvent {
  type: 'affective.threshold';
  node_id: string;
  theta_base: number;              // Base threshold before affect
  theta_adjusted: number;          // Threshold after affective modulation
  h: number;                       // Threshold reduction amount
  affective_alignment: number;     // cos(A, E_emo) alignment score
  emotion_magnitude: number;       // ||E_emo|| magnitude
  timestamp: string;
}

/**
 * Affective Memory Event
 *
 * Emitted when affect amplifies weight updates (PR-B mechanism).
 * Frequency: Per weight update (sampled)
 */
export interface AffectiveMemoryEvent {
  type: 'affective.memory';
  node_id: string;
  m_affect: number;                // Affective multiplier (1.0 - 1.3)
  emotion_magnitude: number;       // ||E_emo|| magnitude
  delta_log_w_base: number;        // Weight update before amplification
  delta_log_w_amplified: number;   // Weight update after amplification
  timestamp: string;
}

/**
 * Coherence Persistence Event
 *
 * Emitted when tracking coherence lock-in risk (PR-B mechanism).
 * Frequency: Per entity tick (sampled)
 */
export interface CoherencePersistenceEvent {
  type: 'coherence.persistence';
  entity_id: string;
  coherence_persistence: number;   // Consecutive frames in same state
  lambda_res_effective: number;    // Resonance strength after decay
  lock_in_risk: boolean;           // True if persistence > threshold
  timestamp: string;
}

/**
 * Multi-Pattern Response Event
 *
 * Emitted when multi-pattern affective response active (PR-C mechanism).
 * Frequency: Per entity tick when AFFECTIVE_RESPONSE_V2=true (sampled)
 */
export interface MultiPatternResponseEvent {
  type: 'pattern.multiresponse';
  entity_id: string;
  pattern_selected: 'regulation' | 'rumination' | 'distraction';
  pattern_weights: [number, number, number]; // [w_reg, w_rum, w_dist]
  m_affect: number;                // Combined affective multiplier
  rumination_streak: number;       // Consecutive rumination frames
  capped: boolean;                 // True if rumination cap hit
  timestamp: string;
}

/**
 * Identity Multiplicity Event
 *
 * Emitted when detecting identity fragmentation (PR-D mechanism).
 * Frequency: Per entity tick when IDENTITY_MULTIPLICITY_ENABLED=true
 */
export interface IdentityMultiplicityEvent {
  type: 'identity.multiplicity';
  entity_id: string;
  multiplicity_detected: boolean;  // True if multiplicity criteria met
  task_progress_rate: number;      // Progress rate (0-1)
  energy_efficiency: number;       // Efficiency (0-1)
  identity_flip_count: number;     // Flips in window
  window_frames: number;           // Rolling window size
  timestamp: string;
}

/**
 * Consolidation Event
 *
 * Emitted when consolidation slows decay (PR-E mechanism).
 * Frequency: Per consolidation application (sampled)
 */
export interface ConsolidationEvent {
  type: 'consolidation';
  node_id: string;
  node_type: string;               // Node type (Memory, Task, etc.)
  decay_factor_base: number;       // Base decay (e.g., 0.95)
  decay_factor_consolidated: number; // After consolidation (e.g., 0.975)
  consolidation_strength: number;  // Strength factor (0-1)
  importance_score: number;        // Why this node was consolidated
  timestamp: string;
}

/**
 * Decay Resistance Event
 *
 * Emitted when structural resistance affects decay (PR-E mechanism).
 * Frequency: Per resistance computation (every N ticks)
 */
export interface DecayResistanceEvent {
  type: 'decay.resistance';
  node_id: string;
  resistance_score: number;        // Structural resistance (0-1)
  in_degree: number;               // Incoming links
  out_degree: number;              // Outgoing links
  betweenness_centrality: number;  // Graph centrality
  decay_reduction: number;         // How much decay was reduced
  timestamp: string;
}

/**
 * Stickiness Event
 *
 * Emitted when diffusion stickiness affects energy flow (PR-E mechanism).
 * Frequency: Per stride execution (sampled)
 */
export interface StickinessEvent {
  type: 'diffusion.stickiness';
  link_id: string;
  source_node_id: string;
  target_node_id: string;
  target_type: string;             // Node type of target
  stickiness_factor: number;       // s_type (0-1)
  energy_retained: number;         // Energy kept at target
  energy_returned: number;         // Energy reflected back
  timestamp: string;
}

/**
 * Affective Priming Event
 *
 * Emitted when affect primes stimulus injection (PR-E mechanism).
 * Frequency: Per stimulus injection (sampled)
 */
export interface AffectivePrimingEvent {
  type: 'affective.priming';
  node_id: string;
  affect_alignment: number;        // cos(A_recent, E_node)
  priming_boost: number;           // Budget multiplier (0-1.15)
  budget_before: number;           // Budget before priming
  budget_after: number;            // Budget after priming
  timestamp: string;
}

/**
 * Coherence Metric Event
 *
 * Emitted when coherence quality metric computed (PR-E mechanism).
 * Frequency: Per tick when COHERENCE_METRIC_ENABLED=true
 */
export interface CoherenceMetricEvent {
  type: 'coherence.metric';
  coherence: number;               // C metric (0-1)
  frontier_similarity: number;     // Frontier cohesion component
  stride_relatedness: number;      // Stride relatedness component
  window_frames: number;           // Rolling window size
  timestamp: string;
}

/**
 * Criticality Mode Event
 *
 * Emitted when criticality mode classified (PR-E mechanism).
 * Frequency: Per tick when CRITICALITY_MODES_ENABLED=true
 */
export interface CriticalityModeEvent {
  type: 'criticality.mode';
  mode: 'fragmented' | 'exploring' | 'flowing' | 'focused';
  rho: number;                     // Spectral radius
  coherence: number;               // C metric
  description: string;             // Mode explanation
  timestamp: string;
}

/**
 * Weights Updated (TRACE) Event - Priority 4
 *
 * Emitted when TRACE results update node/link weights.
 * Shows context-aware learning (80% to active entities, 20% global).
 * Frequency: Per TRACE application (sampled)
 */
export interface WeightsUpdatedTraceEvent {
  type: 'weights.updated.trace';
  frame_id: number;
  scope: 'link' | 'node' | 'membership';  // What was updated
  cohort: string;                          // Entity cohort
  entity_contexts: string[];               // Which entities (80% split)
  global_context: boolean;                 // Whether 20% global applied
  n: number;                               // Count of weights updated
  d_mu: number;                           // Mean change
  d_sigma: number;                        // Std change
  timestamp: string;
}

/**
 * Weights Updated (Traversal) Event - Priority 4
 *
 * Emitted when traversal strengthening updates weights.
 * Frequency: Per weight learning application (sampled)
 */
export interface WeightsUpdatedTraversalEvent {
  type: 'weights.updated.traversal';
  frame_id: number;
  scope: 'link' | 'node';
  cohort: string;
  entity_attribution: string;              // Which entity's traversal
  n: number;
  d_mu: number;
  d_sigma: number;
  timestamp: string;
}

/**
 * Stride Selection Event - Priority 5
 *
 * Emitted when choosing fanout strategy for traversal.
 * Shows task-mode-aware attention control.
 * Frequency: Per stride selection (sampled)
 */
export interface StrideSelectionEvent {
  type: 'stride.selection';
  frame_id: number;
  node_id: string;                        // Current node
  fanout: number;                         // Out-degree
  strategy: 'selective' | 'balanced' | 'exhaustive'; // Strategy chosen
  top_k: number;                          // Candidates considered
  task_mode: 'focused' | 'balanced' | 'divergent' | 'methodical' | null;
  task_mode_override: boolean;            // Whether mode overrode structure
  structure_would_suggest: string;        // What structure-only would choose
  wm_headroom: number;                    // WM capacity remaining (0-1)
  timestamp: string;
}

/**
 * Phenomenology Mismatch Event - Priority 6
 *
 * Emitted when substrate-inferred affect diverges from entity self-report.
 * Shows consciousness substrate-phenomenology alignment.
 * Frequency: Per tick when mismatch detected
 */
export interface PhenomenologyMismatchEvent {
  type: 'phenomenology.mismatch';
  frame_id: number;
  entity_id: string;
  substrate_valence: number;              // Inferred from emotion vectors
  substrate_arousal: number;
  substrate_mag: number;
  selfreport_valence: number;             // From entity introspection
  selfreport_arousal: number;
  selfreport_mag: number;
  divergence: number;                     // Euclidean distance
  threshold: number;                      // Mismatch threshold
  mismatch_detected: boolean;
  mismatch_type: 'valence_flip' | 'arousal_mismatch' | 'magnitude_divergence' | 'coherent';
  timestamp: string;
}

/**
 * Phenomenological Health Event - Priority 6
 *
 * Emitted to track consciousness health across dimensions.
 * Shows flow state, coherence alignment, multiplicity health.
 * Frequency: Per tick (sampled)
 */
export interface PhenomenologicalHealthEvent {
  type: 'phenomenological_health';
  frame_id: number;
  entity_id: string;

  // Flow state metrics
  flow_state: number;                     // Overall flow (0-1)
  wm_challenge_balance: number;           // WM capacity vs challenge
  engagement: number;                     // Energy investment
  skill_demand_match: number;             // Capability vs demands

  // Coherence metrics
  coherence_alignment: number;            // 0-1
  resonance_dominance_ratio: number;      // res/(res+comp)

  // Multiplicity metrics
  multiplicity_health: number;            // 0-1
  distinct_entities_coactive: number;     // Count
  thrashing_detected: boolean;
  co_activation_stability: number;        // Stability over frames

  overall_health: number;                 // Aggregate (0-1)
  timestamp: string;
}

/**
 * Union type of all WebSocket events
 */
export type WebSocketEvent =
  | EntityActivityEvent
  | ThresholdCrossingEvent
  | ConsciousnessStateEvent
  | FrameStartEvent
  | WmEmitEvent
  | NodeFlipEvent
  | LinkFlowSummaryEvent
  | FrameEndEvent
  | NodeEmotionUpdateEvent
  | LinkEmotionUpdateEvent
  | StrideExecEvent
  | WeightsUpdatedTraceEvent
  | WeightsUpdatedTraversalEvent
  | StrideSelectionEvent
  | PhenomenologyMismatchEvent
  | PhenomenologicalHealthEvent
  | AffectiveThresholdEvent
  | AffectiveMemoryEvent
  | CoherencePersistenceEvent
  | MultiPatternResponseEvent
  | IdentityMultiplicityEvent
  | ConsolidationEvent
  | DecayResistanceEvent
  | StickinessEvent
  | AffectivePrimingEvent
  | CoherenceMetricEvent
  | CriticalityModeEvent;

/**
 * WebSocket connection state
 */
export enum WebSocketState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  DISCONNECTED = 'disconnected',
  ERROR = 'error'
}

/**
 * V2 Consciousness State
 *
 * Live frame-by-frame consciousness metrics for real-time visualization.
 * Extended with system health metrics per observability_requirements_v2_complete.md
 */
export interface V2ConsciousnessState {
  // Frame tracking
  currentFrame: number | null;     // Current frame ID

  // Criticality metrics (from frame.start)
  rho: number | null;               // Branching ratio (ρ) - thought expansion metric
  safety_state: 'subcritical' | 'critical' | 'supercritical' | null; // System stability

  // Timing metrics (from frame.start)
  dt_ms: number | null;             // Wall-clock time since last tick
  interval_sched: number | null;    // Scheduled interval
  dt_used: number | null;           // Physics dt actually used

  // Conservation metrics (from frame.end)
  deltaE_total: number | null;      // Conservation error (should be ≈0)
  conservation_error_pct: number | null; // Error as percentage
  energy_in: number | null;         // Energy injected this frame
  energy_transferred: number | null; // Energy moved this frame
  energy_decay: number | null;      // Energy lost to decay

  // Frontier metrics (from frame.end)
  active_count: number | null;      // Nodes above threshold
  shadow_count: number | null;      // 1-hop neighbors
  diffusion_radius: number | null;  // Distance from stimuli

  // Working memory and traversal
  workingMemory: Set<string>;       // Node IDs currently in working memory
  recentFlips: NodeFlipEvent[];     // Recent threshold crossings (last 20)
  linkFlows: Map<string, number>;   // Link ID -> traversal count this frame
}

/**
 * Emotion Metadata Store
 *
 * Tracks emotion vectors for nodes and links with hysteresis for flicker prevention.
 */
export interface EmotionMetadata {
  magnitude: number;              // ||E_emo|| (0-1)
  axes: EmotionAxis[];           // Emotion axes with values
  lastUpdated: number;           // Timestamp of last update
  displayedMagnitude: number;    // Last magnitude actually rendered (for hysteresis)
}

/**
 * Emotion Coloring State
 *
 * Real-time emotion metadata for mood map and attribution.
 */
export interface EmotionColoringState {
  nodeEmotions: Map<string, EmotionMetadata>;    // Node ID -> emotion metadata
  linkEmotions: Map<string, EmotionMetadata>;    // Link ID -> emotion metadata
  recentStrides: StrideExecEvent[];               // Last N strides for attribution
  regulationRatio: number | null;                 // Complementarity / (comp + res) ratio
  resonanceRatio: number | null;                  // Resonance / (comp + res) ratio
  saturationWarnings: string[];                   // Node IDs with high saturation (>0.9)
}

/**
 * Aggregated event streams
 *
 * This is what the useWebSocket hook returns -
 * separate arrays for each event type for easy consumption.
 */
export interface WebSocketStreams {
  // V1 events (legacy)
  entityActivity: EntityActivityEvent[];
  thresholdCrossings: ThresholdCrossingEvent[];
  consciousnessState: ConsciousnessStateEvent | null;

  // V2 events (frame-based)
  v2State: V2ConsciousnessState;

  // Emotion coloring events
  emotionState: EmotionColoringState;

  // Connection state
  connectionState: WebSocketState;
  error: string | null;
}
