'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import type {
  WebSocketEvent,
  EntityActivityEvent,
  ThresholdCrossingEvent,
  ConsciousnessStateEvent,
  WebSocketStreams
} from './websocket-types';
import { WebSocketState } from './websocket-types';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/ws';
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_ENTITY_ACTIVITIES = 100; // Keep last 100 entity activities
const MAX_THRESHOLD_CROSSINGS = 50; // Keep last 50 threshold crossings

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

  // Event streams
  const [entityActivity, setEntityActivity] = useState<EntityActivityEvent[]>([]);
  const [thresholdCrossings, setThresholdCrossings] = useState<ThresholdCrossingEvent[]>([]);
  const [consciousnessState, setConsciousnessState] = useState<ConsciousnessStateEvent | null>(null);

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
        case 'entity_activity':
          setEntityActivity(prev => {
            const updated = [...prev, data];
            // Keep only the last N activities to prevent memory issues
            return updated.slice(-MAX_ENTITY_ACTIVITIES);
          });
          break;

        case 'threshold_crossing':
          setThresholdCrossings(prev => {
            const updated = [...prev, data];
            // Keep only the last N crossings
            return updated.slice(-MAX_THRESHOLD_CROSSINGS);
          });
          break;

        case 'consciousness_state':
          // Only keep the latest consciousness state
          setConsciousnessState(data);
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
    entityActivity,
    thresholdCrossings,
    consciousnessState,
    connectionState,
    error
  };
}
