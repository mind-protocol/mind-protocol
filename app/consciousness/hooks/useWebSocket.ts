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
  FrameEndEvent
} from './websocket-types';
import { WebSocketState } from './websocket-types';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/ws';
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_ENTITY_ACTIVITIES = 100; // Keep last 100 entity activities
const MAX_THRESHOLD_CROSSINGS = 50; // Keep last 50 threshold crossings
const MAX_NODE_FLIPS = 20; // Keep last 20 node flips (v2)

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
    currentFrame: null,
    rho: null,
    workingMemory: new Set<string>(),
    recentFlips: [],
    linkFlows: new Map<string, number>()
  });

  // WebSocket reference (persists across renders)
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isIntentionalCloseRef = useRef(false);

  /**
   * Handle incoming WebSocket messages
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data: WebSocketEvent = JSON.parse(event.data);

      switch (data.type) {
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
          setV2State(prev => {
            // Only update if frame actually changed
            if (prev.currentFrame === frameEvent.frame_id) return prev;

            return {
              ...prev,
              currentFrame: frameEvent.frame_id,
              rho: frameEvent.rho ?? prev.rho,
              // Clear link flows at frame start
              linkFlows: new Map<string, number>()
            };
          });
          break;
        }

        case 'wm.emit': {
          const wmEvent = data as WmEmitEvent;
          setV2State(prev => {
            // Only update if working memory content changed
            const newNodeIds = new Set(wmEvent.node_ids);
            if (prev.workingMemory.size === newNodeIds.size &&
                [...newNodeIds].every(id => prev.workingMemory.has(id))) {
              return prev; // No change, return same object
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
            // Guard: Check if flows array exists
            if (!flowEvent.flows || !Array.isArray(flowEvent.flows)) {
              console.warn('[useWebSocket] link.flow.summary event missing flows array:', flowEvent);
              return prev;
            }

            // Check if any flow values actually changed
            let hasChanges = false;
            for (const flow of flowEvent.flows) {
              if (prev.linkFlows.get(flow.link_id) !== flow.count) {
                hasChanges = true;
                break;
              }
            }

            if (!hasChanges) {
              return prev; // No changes, return same object
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

        case 'frame.end':
          // Frame end is just a marker - no state update needed
          break;

        default:
          console.warn('[WebSocket] Unknown event type:', (data as any).type);
      }
    } catch (err) {
      console.error('[WebSocket] Failed to parse message:', err);
      setError('Failed to parse WebSocket message');
    }
  }, []);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    // Don't reconnect if intentionally closed
    if (isIntentionalCloseRef.current) {
      return;
    }

    try {
      console.log('[WebSocket] Connecting to:', WS_URL);
      setConnectionState(WebSocketState.CONNECTING);
      setError(null);

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        setConnectionState(WebSocketState.CONNECTED);
        setError(null);
      };

      ws.onmessage = handleMessage;

      ws.onerror = (event) => {
        console.error('[WebSocket] Error:', event);
        setConnectionState(WebSocketState.ERROR);
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log('[WebSocket] Disconnected:', event.code, event.reason);
        setConnectionState(WebSocketState.DISCONNECTED);

        // Attempt reconnection if not intentionally closed
        if (!isIntentionalCloseRef.current) {
          console.log(`[WebSocket] Reconnecting in ${RECONNECT_DELAY}ms...`);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, RECONNECT_DELAY);
        }
      };
    } catch (err) {
      console.error('[WebSocket] Connection error:', err);
      setConnectionState(WebSocketState.ERROR);
      setError(err instanceof Error ? err.message : 'Unknown connection error');

      // Attempt reconnection
      if (!isIntentionalCloseRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
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
   * Cleanup on unmount
   */
  useEffect(() => {
    isIntentionalCloseRef.current = false;
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    // V1 events
    entityActivity,
    thresholdCrossings,
    consciousnessState,

    // V2 events
    v2State,

    // Connection
    connectionState,
    error
  };
}
