'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import type {
  WebSocketEvent,
  EntityActivityEvent,
  ThresholdCrossingEvent,
  ConsciousnessStateEvent,
  WebSocketStreams,
  V2ConsciousnessState,
  FrameStartEvent,
  WmEmitEvent,
  NodeFlipEvent,
  LinkFlowSummaryEvent,
  FrameEndEvent,
  EmotionColoringState,
  NodeEmotionUpdateEvent,
  LinkEmotionUpdateEvent,
  StrideExecEvent,
  EmotionMetadata,
  TickFrameEvent,
  WeightsUpdatedTraceEvent,
  StrideSelectionEvent,
  PhenomenologyMismatchEvent,
  PhenomenologicalHealthEvent
} from './websocket-types';
import { WebSocketState } from './websocket-types';
import { diagOnEvent } from '../lib/ws-diagnostics';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/ws';
const RECONNECT_DELAY = 3000; // 3 seconds

// 🎯 SINGLETON: Module-scope WebSocket to prevent mount/unmount churn
let _ws: WebSocket | null = null;
let _connecting = false;
const MAX_ENTITY_ACTIVITIES = 100; // Keep last 100 subentity activities
const MAX_THRESHOLD_CROSSINGS = 50; // Keep last 50 threshold crossings
const MAX_NODE_FLIPS = 20; // Keep last 20 node flips (v2)
const MAX_RECENT_STRIDES = 100; // Keep last 100 strides for attribution
const MAX_FRAME_EVENTS = 200; // Keep last 200 frame.start events (Priority 3 tick speed viz)
const MAX_WEIGHT_LEARNING_EVENTS = 200; // Keep last 200 weight learning events (Priority 4 dual-view viz)
const MAX_STRIDE_SELECTION_EVENTS = 200; // Keep last 200 stride selection events (Priority 5 fan-out viz)
const MAX_PHENOMENOLOGY_EVENTS = 200; // Keep last 200 phenomenology events (Priority 6 health viz)
const SATURATION_THRESHOLD = 0.9; // Emotion magnitude threshold for saturation warning

// 🔴 MEMORY LEAK FIX: TTL for emotion and flow maps to prevent unbounded growth
const EMOTION_TTL_MS = 5 * 60 * 1000; // 5 minutes - remove stale emotion data
const CLEANUP_INTERVAL_MS = 60 * 1000; // Run cleanup every 60 seconds

// 🎯 PHASE 4 STABILITY: 10Hz throttling to prevent flicker and excessive re-renders
const UPDATE_THROTTLE_MS = 100; // Batch updates and flush at 10Hz (100ms intervals)

/**
 * useWebSocket Hook
 *
 * Connects to the consciousness operations WebSocket stream
 * and provides real-time event data to visualization components.
 *
 * Features:
 * - Automatic reconnection on disconnect
 * - Separate streams for each event type
 * - Connection state tracking
 * - Error handling
 *
 * Usage:
 * const { entityActivity, thresholdCrossings, consciousnessState } = useWebSocket();
 *
 * Author: Iris "The Aperture"
 * Backend integration: Felix "Ironhand"'s WebSocket infrastructure
 */
export function useWebSocket(): WebSocketStreams {
  // Connection state
  const [connectionState, setConnectionState] = useState<WebSocketState>(WebSocketState.CONNECTING);
  const [error, setError] = useState<string | null>(null);

  // Event streams (v1 legacy)
  const [entityActivity, setEntityActivity] = useState<EntityActivityEvent[]>([]);
  const [thresholdCrossings, setThresholdCrossings] = useState<ThresholdCrossingEvent[]>([]);
  const [consciousnessState, setConsciousnessState] = useState<ConsciousnessStateEvent | null>(null);

  // V2 consciousness state (frame-based)
  const [v2State, setV2State] = useState<V2ConsciousnessState>({
    // Frame tracking
    currentFrame: null,
    frameEvents: [],

    // Criticality metrics
    rho: null,
    safety_state: null,

    // Timing metrics
    dt_ms: null,
    interval_sched: null,
    dt_used: null,

    // Conservation metrics
    deltaE_total: null,
    conservation_error_pct: null,
    energy_in: null,
    energy_transferred: null,
    energy_decay: null,

    // Frontier metrics
    active_count: null,
    shadow_count: null,
    diffusion_radius: null,

    // Working memory and traversal
    workingMemory: new Set<string>(),
    recentFlips: [],
    linkFlows: new Map<string, number>()
  });

  // Emotion coloring state
  const [emotionState, setEmotionState] = useState<EmotionColoringState>({
    nodeEmotions: new Map<string, EmotionMetadata>(),
    linkEmotions: new Map<string, EmotionMetadata>(),
    recentStrides: [],
    regulationRatio: null,
    resonanceRatio: null,
    saturationWarnings: []
  });

  // Priority 4: Weight learning events
  const [weightLearningEvents, setWeightLearningEvents] = useState<WeightsUpdatedTraceEvent[]>([]);

  // Priority 5: Stride selection events
  const [strideSelectionEvents, setStrideSelectionEvents] = useState<StrideSelectionEvent[]>([]);

  // Priority 6: Phenomenology health events
  const [phenomenologyMismatchEvents, setPhenomenologyMismatchEvents] = useState<PhenomenologyMismatchEvent[]>([]);
  const [phenomenologyHealthEvents, setPhenomenologyHealthEvents] = useState<PhenomenologicalHealthEvent[]>([]);

  // WebSocket reference (persists across renders)
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isIntentionalCloseRef = useRef(false);

  // Frame de-duplication to prevent infinite re-render loops
  // Track last processed frame_id instead of time to avoid processing duplicates
  const lastProcessedFrameRef = useRef<number | null>(null);

  // 🎯 PHASE 4: Throttling infrastructure - batch updates and flush at 10Hz
  const pendingUpdatesRef = useRef<any[]>([]);
  const flushIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * 🎯 PHASE 4: Flush pending updates at 10Hz
   * Processes all buffered WebSocket events in single setState batch
   * Reduces React re-render frequency from ~49Hz to 10Hz
   */
  const flushPendingUpdates = useCallback(() => {
    const updates = pendingUpdatesRef.current;
    if (updates.length === 0) return;

    // Clear buffer immediately to avoid processing duplicates
    pendingUpdatesRef.current = [];

    // Process all updates in single pass
    updates.forEach((data) => {
      const eventType = (data as any).type;

      switch (eventType) {
        // V1 events (legacy)
        case 'entity_activity':
          setEntityActivity(prev => {
            const updated = [...prev, data];
            return updated.slice(-MAX_ENTITY_ACTIVITIES);
          });
          break;

        case 'threshold_crossing':
          setThresholdCrossings(prev => {
            const updated = [...prev, data];
            return updated.slice(-MAX_THRESHOLD_CROSSINGS);
          });
          break;

        case 'consciousness_state':
          setConsciousnessState(data);
          break;

        // V2 events (frame-based)
        case 'frame.start': {
          const frameEvent = data as FrameStartEvent;

          // De-duplicate: Skip if we've already processed this frame_id
          if (lastProcessedFrameRef.current === frameEvent.frame_id) {
            break;
          }
          lastProcessedFrameRef.current = frameEvent.frame_id;

          setV2State(prev => {
            if (prev.currentFrame === frameEvent.frame_id) {
              return prev; // Same frame, skip update
            }

            const updatedFrameEvents = [...prev.frameEvents, frameEvent].slice(-MAX_FRAME_EVENTS);

            return {
              ...prev,
              currentFrame: frameEvent.frame_id,
              frameEvents: updatedFrameEvents,
              rho: frameEvent.rho ?? prev.rho,
              safety_state: frameEvent.safety_state ?? prev.safety_state,
              dt_ms: frameEvent.dt_ms ?? prev.dt_ms,
              interval_sched: frameEvent.interval_sched ?? prev.interval_sched,
              dt_used: frameEvent.dt_used ?? prev.dt_used,
              linkFlows: prev.linkFlows.size > 0 ? new Map<string, number>() : prev.linkFlows
            };
          });
          break;
        }

        case 'wm.emit': {
          const wmEvent = data as WmEmitEvent;
          setV2State(prev => {
            const newNodeIds = new Set(wmEvent.node_ids);
            if (prev.workingMemory.size === newNodeIds.size &&
                [...newNodeIds].every(id => prev.workingMemory.has(id))) {
              return prev;
            }
            return {
              ...prev,
              workingMemory: newNodeIds
            };
          });
          break;
        }

        case 'node.flip': {
          setV2State(prev => {
            const updated = [...prev.recentFlips, data as NodeFlipEvent];
            return {
              ...prev,
              recentFlips: updated.slice(-MAX_NODE_FLIPS)
            };
          });
          break;
        }

        case 'link.flow.summary': {
          const flowEvent = data as LinkFlowSummaryEvent;
          setV2State(prev => {
            if (!flowEvent.flows || !Array.isArray(flowEvent.flows)) {
              console.warn('[useWebSocket] link.flow.summary event missing flows array:', flowEvent);
              return prev;
            }

            let hasChanges = false;
            for (const flow of flowEvent.flows) {
              if (prev.linkFlows.get(flow.link_id) !== flow.count) {
                hasChanges = true;
                break;
              }
            }

            if (!hasChanges) {
              return prev;
            }

            const newFlows = new Map(prev.linkFlows);
            flowEvent.flows.forEach(flow => {
              newFlows.set(flow.link_id, flow.count);
            });
            return {
              ...prev,
              linkFlows: newFlows
            };
          });
          break;
        }

        case 'frame.end': {
          const frameEndEvent = data as FrameEndEvent;
          setV2State(prev => {
            if (
              prev.deltaE_total === frameEndEvent.deltaE_total &&
              prev.conservation_error_pct === frameEndEvent.conservation_error_pct &&
              prev.energy_in === frameEndEvent.energy_in &&
              prev.energy_transferred === frameEndEvent.energy_transferred &&
              prev.energy_decay === frameEndEvent.energy_decay &&
              prev.active_count === frameEndEvent.active_count &&
              prev.shadow_count === frameEndEvent.shadow_count &&
              prev.diffusion_radius === frameEndEvent.diffusion_radius
            ) {
              return prev;
            }

            return {
              ...prev,
              deltaE_total: frameEndEvent.deltaE_total ?? prev.deltaE_total,
              conservation_error_pct: frameEndEvent.conservation_error_pct ?? prev.conservation_error_pct,
              energy_in: frameEndEvent.energy_in ?? prev.energy_in,
              energy_transferred: frameEndEvent.energy_transferred ?? prev.energy_transferred,
              energy_decay: frameEndEvent.energy_decay ?? prev.energy_decay,
              active_count: frameEndEvent.active_count ?? prev.active_count,
              shadow_count: frameEndEvent.shadow_count ?? prev.shadow_count,
              diffusion_radius: frameEndEvent.diffusion_radius ?? prev.diffusion_radius
            };
          });
          break;
        }

        // Emotion coloring events
        case 'node.emotion.update': {
          const emotionEvent = data as NodeEmotionUpdateEvent;
          setEmotionState(prev => {
            const metadata: EmotionMetadata = {
              magnitude: emotionEvent.emotion_magnitude,
              axes: emotionEvent.top_axes,
              lastUpdated: Date.parse(emotionEvent.timestamp),
              displayedMagnitude: prev.nodeEmotions.get(emotionEvent.node_id)?.displayedMagnitude ?? emotionEvent.emotion_magnitude
            };

            const newNodeEmotions = new Map(prev.nodeEmotions);
            newNodeEmotions.set(emotionEvent.node_id, metadata);

            const saturationWarnings: string[] = [];
            for (const [nodeId, meta] of newNodeEmotions.entries()) {
              if (meta.magnitude > SATURATION_THRESHOLD) {
                saturationWarnings.push(nodeId);
              }
            }

            return {
              ...prev,
              nodeEmotions: newNodeEmotions,
              saturationWarnings
            };
          });
          break;
        }

        case 'link.emotion.update': {
          const emotionEvent = data as LinkEmotionUpdateEvent;
          setEmotionState(prev => {
            const metadata: EmotionMetadata = {
              magnitude: emotionEvent.emotion_magnitude,
              axes: emotionEvent.top_axes,
              lastUpdated: Date.parse(emotionEvent.timestamp),
              displayedMagnitude: prev.linkEmotions.get(emotionEvent.link_id)?.displayedMagnitude ?? emotionEvent.emotion_magnitude
            };

            const newLinkEmotions = new Map(prev.linkEmotions);
            newLinkEmotions.set(emotionEvent.link_id, metadata);

            return {
              ...prev,
              linkEmotions: newLinkEmotions
            };
          });
          break;
        }

        case 'stride.exec': {
          const strideEvent = data as StrideExecEvent;
          setEmotionState(prev => {
            const updated = [...prev.recentStrides, strideEvent];
            const recentStrides = updated.slice(-MAX_RECENT_STRIDES);

            let compCount = 0;
            let resCount = 0;

            for (const stride of recentStrides) {
              if (stride.comp_multiplier < stride.resonance_multiplier) {
                compCount++;
              } else if (stride.resonance_multiplier < stride.comp_multiplier) {
                resCount++;
              }
            }

            const total = compCount + resCount;
            const regulationRatio = total > 0 ? compCount / total : null;
            const resonanceRatio = total > 0 ? resCount / total : null;

            return {
              ...prev,
              recentStrides,
              regulationRatio,
              resonanceRatio
            };
          });
          break;
        }

        // Priority 4: Weight learning events
        case 'weights.updated.trace': {
          const weightEvent = data as WeightsUpdatedTraceEvent;
          setWeightLearningEvents(prev => {
            const updated = [...prev, weightEvent];
            return updated.slice(-MAX_WEIGHT_LEARNING_EVENTS);
          });
          break;
        }

        // Priority 5: Stride selection events
        case 'stride.selection': {
          const strideSelectionEvent = data as StrideSelectionEvent;
          setStrideSelectionEvents(prev => {
            const updated = [...prev, strideSelectionEvent];
            return updated.slice(-MAX_STRIDE_SELECTION_EVENTS);
          });
          break;
        }

        // Priority 6: Phenomenology health events
        case 'phenomenology.mismatch': {
          const mismatchEvent = data as PhenomenologyMismatchEvent;
          setPhenomenologyMismatchEvents(prev => {
            const updated = [...prev, mismatchEvent];
            return updated.slice(-MAX_PHENOMENOLOGY_EVENTS);
          });
          break;
        }

        case 'phenomenological_health': {
          const healthEvent = data as PhenomenologicalHealthEvent;
          setPhenomenologyHealthEvents(prev => {
            const updated = [...prev, healthEvent];
            return updated.slice(-MAX_PHENOMENOLOGY_EVENTS);
          });
          break;
        }

        case 'tick_frame_v1': {
          const tickEvent = data as TickFrameEvent;
          setV2State(prev => ({
            ...prev,
            currentFrame: tickEvent.frame_id,
            rho: tickEvent.rho ?? prev.rho,
          }));
          break;
        }

        // Internal consciousness engine events (safe to ignore)
        case 'criticality.state':
        case 'decay.tick':
        case 'tick.update':
          break;

        default:
          // 🎯 Catch unknown events to prevent silent drops
          console.warn('[WebSocket] Unknown event type:', eventType, data);
      }
    });
  }, []);

  /**
   * Handle incoming WebSocket messages
   * 🎯 PHASE 4: Buffered mode - accumulate events, flush at 10Hz
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);

      // 🎯 STEP A: Transport diagnostic - prove events arrive
      diagOnEvent(data);

      // Buffer event for batch processing
      // flushPendingUpdates will process at 10Hz
      pendingUpdatesRef.current.push(data);
    } catch (err) {
      console.error('[WebSocket] Failed to parse message:', err);
      setError('Failed to parse WebSocket message');
    }
  }, []);

  /**
   * Connect to WebSocket (singleton pattern)
   * 🎯 Prevents mount/unmount churn by reusing module-scope WebSocket
   */
  const connect = useCallback(() => {
    // If already connected, just update local state and return
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      setConnectionState(WebSocketState.CONNECTED);
      setError(null);
      wsRef.current = _ws;
      return;
    }

    // If already connecting, wait
    if (_connecting) {
      return;
    }

    // Don't reconnect if intentionally closed
    if (isIntentionalCloseRef.current) {
      return;
    }

    _connecting = true;

    try {
      console.log('[WebSocket] Connecting to:', WS_URL);
      setConnectionState(WebSocketState.CONNECTING);
      setError(null);

      const ws = new WebSocket(WS_URL);
      _ws = ws;
      wsRef.current = ws;

      // Expose for diagnostics
      (window as any).__ws = ws;

      ws.onopen = () => {
        _connecting = false;
        console.log('[WebSocket] Connected');
        setConnectionState(WebSocketState.CONNECTED);
        setError(null);
      };

      ws.onmessage = handleMessage;

      ws.onerror = (event) => {
        // WebSocket unavailable is expected degraded state, not error
        console.log('[WebSocket] Connection unavailable - will retry');
        setConnectionState(WebSocketState.ERROR);
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        _connecting = false;
        console.log('[WebSocket] Disconnected:', event.code, event.reason);
        setConnectionState(WebSocketState.DISCONNECTED);

        // Attempt reconnection if not intentionally closed
        if (!isIntentionalCloseRef.current) {
          console.log(`[WebSocket] Reconnecting in ${RECONNECT_DELAY}ms...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            _ws = null; // Clear stale socket
            connect();
          }, RECONNECT_DELAY);
        }
      };
    } catch (err) {
      _connecting = false;
      console.error('[WebSocket] Connection error:', err);
      setConnectionState(WebSocketState.ERROR);
      setError(err instanceof Error ? err.message : 'Unknown connection error');

      // Attempt reconnection
      if (!isIntentionalCloseRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          _ws = null; // Clear stale socket
          connect();
        }, RECONNECT_DELAY);
      }
    }
  }, [handleMessage]);

  /**
   * Disconnect WebSocket
   */
  const disconnect = useCallback(() => {
    isIntentionalCloseRef.current = true;

    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Close WebSocket connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnectionState(WebSocketState.DISCONNECTED);
  }, []);

  /**
   * Initialize WebSocket connection on mount
   * 🎯 SINGLETON: Keep alive across unmounts (no disconnect on cleanup)
   */
  useEffect(() => {
    isIntentionalCloseRef.current = false;
    connect();

    // Don't disconnect on unmount - keep singleton alive across route changes
    return () => {
      // Socket stays open
    };
  }, [connect]);

  /**
   * 🎯 PHASE 4: Start 10Hz flush interval
   * Processes buffered events every 100ms to throttle React re-renders
   */
  useEffect(() => {
    flushIntervalRef.current = setInterval(() => {
      flushPendingUpdates();
    }, UPDATE_THROTTLE_MS);

    // Cleanup on unmount
    return () => {
      if (flushIntervalRef.current) {
        clearInterval(flushIntervalRef.current);
        flushIntervalRef.current = null;
      }

      // Flush any remaining events before unmounting
      flushPendingUpdates();
    };
  }, [flushPendingUpdates]);

  /**
   * 🔴 MEMORY LEAK FIX: Periodic cleanup of emotion Maps
   * Removes entries older than EMOTION_TTL_MS to prevent unbounded growth
   */
  useEffect(() => {
    const cleanupInterval = setInterval(() => {
      const now = Date.now();

      setEmotionState(prev => {
        let hasChanges = false;
        const newNodeEmotions = new Map<string, EmotionMetadata>();
        const newLinkEmotions = new Map<string, EmotionMetadata>();

        // Clean node emotions
        for (const [key, value] of prev.nodeEmotions.entries()) {
          if (now - value.lastUpdated < EMOTION_TTL_MS) {
            newNodeEmotions.set(key, value);
          } else {
            hasChanges = true;
          }
        }

        // Clean link emotions
        for (const [key, value] of prev.linkEmotions.entries()) {
          if (now - value.lastUpdated < EMOTION_TTL_MS) {
            newLinkEmotions.set(key, value);
          } else {
            hasChanges = true;
          }
        }

        // Only update if something changed
        if (!hasChanges) return prev;

        return {
          ...prev,
          nodeEmotions: newNodeEmotions,
          linkEmotions: newLinkEmotions
        };
      });
    }, CLEANUP_INTERVAL_MS);

    return () => clearInterval(cleanupInterval);
  }, []);

  return {
    // V1 events
    entityActivity,
    thresholdCrossings,
    consciousnessState,

    // V2 events
    v2State,

    // Emotion coloring
    emotionState,

    // Priority 4: Weight learning
    weightLearningEvents,

    // Priority 5: Stride selection
    strideSelectionEvents,

    // Priority 6: Phenomenology health
    phenomenologyMismatchEvents,
    phenomenologyHealthEvents,

    // Connection
    connectionState,
    error
  };
}
