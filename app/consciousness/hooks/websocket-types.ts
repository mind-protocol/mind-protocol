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
 * Entity Activity Event
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
 * Emitted when a node crosses activation threshold for an entity.
 * Frequency: On threshold crossing (up or down)
 * Source: orchestration/dynamic_prompt_generator.py
 */
export interface ThresholdCrossingEvent {
  type: 'threshold_crossing';
  entity_id: string;               // Entity for which threshold crossed
  node_id: string;                 // Node that crossed threshold
  node_name: string;               // Human-readable node text
  direction: 'on' | 'off';         // Crossed up (activated) or down (deactivated)
  entity_activity: number;         // Current entity activity level (0-1)
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
 * Frame Start Event (v2)
 *
 * Marks the beginning of a consciousness frame.
 * Contains branching ratio (ρ) and entity palette.
 */
export interface FrameStartEvent {
  type: 'frame.start';
  v: '2';
  kind: 'frame.start';
  frame_id: number;
  rho?: number;                    // Branching ratio (expansion metric)
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
  entity_id?: string;              // Which entity caused the flip
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
    entity_ids: string[];          // Which entities traversed
  }>;
}

/**
 * Frame End Event (v2)
 *
 * Marks the end of a consciousness frame.
 */
export interface FrameEndEvent {
  type: 'frame.end';
  v: '2';
  kind: 'frame.end';
  frame_id: number;
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
  | FrameEndEvent;

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
 */
export interface V2ConsciousnessState {
  currentFrame: number | null;     // Current frame ID
  rho: number | null;               // Branching ratio (ρ) - thought expansion metric
  workingMemory: Set<string>;       // Node IDs currently in working memory
  recentFlips: NodeFlipEvent[];     // Recent threshold crossings (last 20)
  linkFlows: Map<string, number>;   // Link ID -> traversal count this frame
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

  // Connection state
  connectionState: WebSocketState;
  error: string | null;
}
