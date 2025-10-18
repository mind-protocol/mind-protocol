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
 * Emitted after global arousal measurement.
 * Frequency: After each tick (variable frequency based on system state)
 * Source: orchestration/consciousness_engine.py
 */
export interface ConsciousnessStateEvent {
  type: 'consciousness_state';
  network_id: string;              // e.g., "N1", "N2", "N3"
  global_arousal: number;          // System-wide arousal (0-1)
  branching_ratio: number;         // Mapped branching ratio (0-1)
  raw_sigma: number;               // Raw branching ratio σ (unbounded)
  tick_interval_ms: number;        // Current tick interval in milliseconds
  tick_frequency_hz: number;       // Current tick frequency in Hz
  consciousness_state: string;     // e.g., "alert", "engaged", "calm", "drowsy", "dormant"
  time_since_last_event: number;   // Seconds since last external event
  timestamp: string;               // ISO 8601 timestamp
}

/**
 * Union type of all WebSocket events
 */
export type WebSocketEvent =
  | EntityActivityEvent
  | ThresholdCrossingEvent
  | ConsciousnessStateEvent;

/**
 * WebSocket connection state
 */
export enum WebSocketState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error'
}

/**
 * Aggregated event streams
 *
 * This is what the useWebSocket hook returns -
 * separate arrays for each event type for easy consumption.
 */
export interface WebSocketStreams {
  entityActivity: EntityActivityEvent[];
  thresholdCrossings: ThresholdCrossingEvent[];
  consciousnessState: ConsciousnessStateEvent | null;
  connectionState: WebSocketState;
  error: string | null;
}
