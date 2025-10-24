/**
 * Venice Harbor Renderer - Core Types
 *
 * Renderer-agnostic types for graph visualization.
 * These types define the contract between React/data layer and rendering engine.
 */

// ============================================================================
// Data Types
// ============================================================================

export interface NodeData {
  id: string;
  name: string;
  node_type: string;
  description?: string;

  // Visual properties
  weight?: number;
  base_weight?: number;  // FalkorDB base weight (for semantic polarity)
  energy?: number | Record<string, number>;

  // Activity tracking
  last_active?: number;
  last_traversal_time?: number;
  traversal_count?: number;
  last_traversed_by?: string;  // Entity that last traversed this node
  created_by?: string;  // Entity that created this node

  // Content
  text?: string;  // Node text content (for semantic hashing)

  // Subentity activation (for glow colors)
  entity_activations?: Record<string, {
    energy: number;
    last_activated?: number;
  }>;

  // Positioning (may be null for first render)
  x?: number;
  y?: number;
}

export interface LinkData {
  id: string;
  source: string;
  target: string;
  type?: string;

  // Visual properties
  strength?: number;
  valence?: number;
  confidence?: number;

  // Activity tracking
  created_at?: number;
  last_traversal?: number;
  traversal_count?: number;
}

export interface EntityData {
  entity_id: string;
  name?: string;
  color?: string;
}

export interface OperationData {
  type: 'node_activated' | 'link_traversed' | 'energy_transferred';
  timestamp: number;
  node_id?: string;
  link_id?: string;
  details?: any;
}

/**
 * ViewModel - Complete scene data passed to renderer
 */
export interface ViewModel {
  nodes: NodeData[];
  links: LinkData[];
  subentities: EntityData[];
  operations: OperationData[];

  // Viewport state
  selectedSubentity?: string;
  highlightedNodeId?: string;

  // V2 consciousness state
  workingMemory?: Set<string>;  // Node IDs currently in working memory
  linkFlows?: Map<string, number>;  // Link ID -> traversal count
  recentFlips?: Array<{  // Recent threshold crossings
    node_id: string;
    direction: 'on' | 'off';
    timestamp: number;
  }>;

  // Time range for activity filtering
  timeWindow?: {
    start: number;
    end: number;
  };
}

// ============================================================================
// Camera & Interaction
// ============================================================================

export interface CameraState {
  x: number;
  y: number;
  scale: number;
}

export interface PickResult {
  type: 'node' | 'link' | 'none';
  id?: string;
  data?: NodeData | LinkData;
  screenX: number;
  screenY: number;
  worldX: number;
  worldY: number;
}

// ============================================================================
// Renderer Interface
// ============================================================================

/**
 * RendererAdapter - Abstract rendering engine interface
 *
 * Allows swapping between different rendering backends (PixiJS, Three.js, WebGPU)
 * without changing the React components or data layer.
 */
export interface RendererAdapter {
  /**
   * Mount renderer to DOM container
   */
  mount(container: HTMLElement): void;

  /**
   * Unmount and cleanup
   */
  unmount(): void;

  /**
   * Update camera position/zoom
   */
  setCamera(camera: CameraState): void;

  /**
   * Get current camera state
   */
  getCamera(): CameraState;

  /**
   * Update scene data (nodes, links, subentities)
   */
  setData(viewModel: ViewModel): void;

  /**
   * Hit test at screen coordinates
   * Returns what was clicked/hovered
   */
  pick(screenX: number, screenY: number): PickResult;

  /**
   * Resize canvas to match container
   */
  resize(width: number, height: number): void;

  /**
   * Get renderer stats (for debugging)
   */
  getStats(): RendererStats;
}

export interface RendererStats {
  fps: number;
  frameTime: number;
  drawCalls: number;
  nodeCount: number;
  linkCount: number;
  memoryMB?: number;
}

// ============================================================================
// Configuration
// ============================================================================

export interface RendererConfig {
  // Performance
  targetFPS?: number;
  enableCulling?: boolean;
  enableLOD?: boolean;

  // Visual
  enableBloom?: boolean;
  enablePostFX?: boolean;
  colorPalette?: 'sunrise' | 'night';

  // Debug
  showStats?: boolean;
  showBounds?: boolean;
  logPerf?: boolean;
}

// ============================================================================
// WebSocket Event Stream Types (Observability v2)
// ============================================================================

export type FrameId = number;

// Common event envelope
export interface BaseEvent {
  v: "2";
  kind: string;
  frame_id: FrameId;
  t_ms?: number;
}

// Frame lifecycle
export interface FrameStart extends BaseEvent {
  kind: "frame.start";
  rho?: number;
  entity_palette?: Array<{ id: string; name?: string; color: string }>;
}

export interface FrameEnd extends BaseEvent {
  kind: "frame.end";
  stride_budget_used?: number;
  stride_budget_left?: number;
  top_entities?: Array<{ id: string; quota_used: number }>;
  emit_counts?: Record<string, number>;
}

// Stimulus processing
export interface StimulusProcessed extends BaseEvent {
  kind: "stimuli.processed";
  stimuli: Array<{
    stimulus_id: string;
    source_type: string;
    budget: number;
    peripheral_z?: number;
    matches: {
      nodes: Array<{ id: string; sim: number; gap: number; alloc: number }>;
      links: Array<{
        id: string;
        type: string;
        sim: number;
        dom_prior?: number;
        alloc_src: number;
        alloc_tgt: number;
      }>;
    };
  }>;
}

// Valence computation
export interface ValenceBatch extends BaseEvent {
  kind: "valence.batch";
  subentity: string;
  frontier: Array<{
    src: string;
    tgt: string;
    V: number;
    gates: {
      homeostasis: number;
      goal: number;
      idsubentity: number;
      completeness: number;
      complementarity: number;
      integration: number;
      ease: number;
    };
  }>;
}

// Stride execution (movement along links)
export interface StrideExec extends BaseEvent {
  kind: "stride.exec";
  subentity: string;
  src: string;
  tgt: string;
  ΔE: number;
  φ: number;
  src_entity: string;   // Subentity owning source node
  tgt_entity?: string;  // Subentity owning target node (for cross-layer routing)
  affect?: {
    link_energy?: number;
    affinity?: number;
  };
  lat_us?: number;
}

// Node activation
export interface NodeFlip extends BaseEvent {
  kind: "node.flip";
  node: string;
  E_pre: number;
  E_post: number;
  Θ: number;
  causal_credit?: Array<{ link: string; π: number }>;
}

// Link activity summary (per frame)
export interface LinkFlowSummary extends BaseEvent {
  kind: "link.flow.summary";
  links: Array<{
    id: string;
    ΔE_sum: number;
    φ_max: number;
    z_flow: number;
    dominance?: number;
    src_entity?: string;  // For cross-layer aggregation
    tgt_entity?: string;
  }>;
}

// Weight learning updates
export interface WeightsUpdated extends BaseEvent {
  kind: "weights.updated";
  source: "traversal" | "trace" | "wm";
  updates: Array<{
    item_id: string;
    type: "node" | "link";
    log_weight_before: number;
    log_weight_after: number;
    signals?: Record<string, number>;
    eta?: number;
  }>;
}

// Working memory emission
export interface WmEmit extends BaseEvent {
  kind: "wm.emit";
  selected_nodes?: string[];
  selected_entities?: string[];  // Subentity-level WM selection
}

// Trace parsing results
export interface TraceParsed extends BaseEvent {
  kind: "trace.parsed";
  trace_id: string;
  reinforcement?: {
    nodes?: Record<string, { ΔR: number }>;
    links?: Record<string, { ΔR: number }>;
  };
  formations?: {
    nodes?: Array<{ name: string; type: string; quality: number }>;
    links?: Array<{ name: string; type: string; quality: number }>;
  };
}

// Subentity-level events
export interface EntityFlip extends BaseEvent {
  kind: "subentity.flip";
  subentity: string;
  E_pre: number;
  E_post: number;
  Θ: number;
  contributors?: Array<{ node: string; π: number }>;
}

export interface EntityWeightsUpdated extends BaseEvent {
  kind: "subentity.weights.updated";
  updates: Array<{
    subentity: string;
    log_weight_before: number;
    log_weight_after: number;
    signals?: Record<string, number>;
    eta?: number;
  }>;
}

export interface EntityBoundarySummary extends BaseEvent {
  kind: "subentity.boundary.summary";
  pairs: Array<{
    src: string;
    tgt: string;
    phi_max: number;
    z_flow: number;
    dominance?: number;
    ΔE_sum: number;  // Sum of energy flow across boundary this frame
  }>;
}

export interface EntityMembersDelta extends BaseEvent {
  kind: "subentity.members.delta";
  subentity: string;
  add?: Array<SnapshotNode>;
  remove?: string[];
}

// Union of all event types
export type VizEvent =
  | FrameStart
  | FrameEnd
  | StimulusProcessed
  | ValenceBatch
  | StrideExec
  | NodeFlip
  | LinkFlowSummary
  | WeightsUpdated
  | WmEmit
  | TraceParsed
  | EntityFlip
  | EntityWeightsUpdated
  | EntityBoundarySummary
  | EntityMembersDelta;

// ============================================================================
// Snapshot Types (Initial State)
// ============================================================================

export interface SnapshotNode {
  id: string;
  E: number;
  Theta: number;
  log_weight: number;
  ema_wm_presence?: number;
  primary_entity?: string;  // For cross-layer node→subentity mapping
  memberships?: Array<{ subentity: string; weight: number }>;
  pos?: [number, number];
}

export interface SnapshotLink {
  id: string;
  src: string;
  tgt: string;
  energy?: number;  // Affect metadata (always present)
  ema_phi?: number;
  dominance?: number;
  ΔE_sum?: number;
  z_flow?: number;
}

export interface SnapshotSubentity {
  id: string;
  name?: string;
  kind?: "functional" | "semantic";
  color: string;  // Server-computed from centroid embeddings (OKLCH)
  log_weight: number;
  E: number;
  Theta: number;
  coherence_ema?: number;
  pos?: [number, number];
}

export interface Snapshot {
  nodes: SnapshotNode[];
  links: SnapshotLink[];
  subentities: SnapshotSubentity[];
}

// ============================================================================
// State Cache Types (Client-side)
// ============================================================================

export interface NodeCache {
  E: number;
  Theta: number;
  log_weight: number;
  ema_wm_presence: number;
  active_this_frame: boolean;
}

export interface LinkCache {
  ΔE_sum: number;
  φ_max: number;
  z_flow: number;
  dominance: number;
  energy: number;  // Affect metadata
}

export interface EntityCache {
  E: number;
  Theta: number;
  log_weight: number;
  color: string;
  coherence_ema: number;
  kind: "functional" | "semantic";
  active_this_frame: boolean;
}

export interface EntityMemberCache {
  nodes: SnapshotNode[];
  links: SnapshotLink[];
  fetched_at: number;
}

export interface EntityBoundaryCache {
  src: string;
  tgt: string;
  phi_max: number;
  z_flow: number;
  dominance: number;
  ΔE_sum: number;
}
