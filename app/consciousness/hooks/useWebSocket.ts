'use client';

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import type {
  WebSocketEvent,
  SubEntityActivityEvent,
  ThresholdCrossingEvent,
  ConsciousnessStateEvent,
  WebSocketStreams,
  V2ConsciousnessState,
  FrameStartEvent,
  WmEmitEvent,
  WmSelectedEvent,
  NodeFlipEvent,
  NodeFlipRecord,
  LinkFlowSummaryEvent,
  FrameEndEvent,
  EmotionColoringState,
  NodeEmotionUpdateEvent,
  LinkEmotionUpdateEvent,
  StrideExecEvent,
  TierLinkStrengthenedEvent,
  EmotionMetadata,
  TickFrameEvent,
  WeightsUpdatedTraceEvent,
  WeightsUpdatedEvent,
  StrideSelectionEvent,
  PhenomenologyMismatchEvent,
  PhenomenologicalHealthEvent,
  SubentityWeightsUpdatedEvent,
  SubentityMembershipPrunedEvent,
  BoundarySummaryEvent,
  PerceptFrameEvent,
  GraphDeltaEvent,
  GraphNodePayload,
  GraphLinkPayload,
  GraphSubentityPayload,
  ForgedIdentityFrameEvent,
  ForgedIdentityMetricsEvent,
  EconomyOverlayState,
  MembraneInjectAckEvent
} from './websocket-types';
import { WebSocketState } from './websocket-types';
import { diagOnEvent } from '../lib/ws-diagnostics';
import { normalizeEvent } from '../lib/normalizeEvents';

const WS_BROADCAST_URL =
  process.env.NEXT_PUBLIC_WS_BROADCAST ||
  process.env.NEXT_PUBLIC_WS_URL ||
  'ws://localhost:8000/api/ws';
const WS_URL = WS_BROADCAST_URL;
const WS_INJECT_URL =
  process.env.NEXT_PUBLIC_WS_INJECT ||
  process.env.NEXT_PUBLIC_WS_URL?.replace('/ws', '/inject') ||
  'ws://localhost:8000/api/ws';
const RECONNECT_DELAY = 3000; // 3 seconds

// 🎯 SINGLETON: Module-scope WebSocket to prevent mount/unmount churn
let _ws: WebSocket | null = null;
let _connecting = false;
let _injectWs: WebSocket | null = null;
let _injectConnecting = false;
const MAX_ENTITY_ACTIVITIES = 100; // Keep last 100 subentity activities
const MAX_THRESHOLD_CROSSINGS = 50; // Keep last 50 threshold crossings
const MAX_NODE_FLIPS = 20; // Keep last 20 node flips (v2)
const MAX_RECENT_STRIDES = 100; // Keep last 100 strides for attribution
const MAX_FRAME_EVENTS = 200; // Keep last 200 frame.start events (Priority 3 tick speed viz)
const MAX_WEIGHT_LEARNING_EVENTS = 200; // Keep last 200 weight learning events (Priority 4 dual-view viz)
const MAX_STRIDE_SELECTION_EVENTS = 200; // Keep last 200 stride selection events (Priority 5 fan-out viz)
const MAX_PHENOMENOLOGY_EVENTS = 200; // Keep last 200 phenomenology events (Priority 6 health viz)
const MAX_WM_SELECTED_EVENTS = 200; // Keep last 200 wm.selected events for diagnostics
const MAX_WEIGHT_UPDATE_EVENTS = 200; // Keep last 200 direct weight update batches
const MAX_SUBENTITY_WEIGHT_EVENTS = 200; // Keep last 200 subentity weight batches
const MAX_BOUNDARY_SUMMARIES = 200; // Keep last 200 boundary summaries
const MAX_FORGED_IDENTITY_FRAMES = 50; // Keep last 50 forged identity frames for viewer
const MAX_GRAPH_DELTA_EVENTS = 512; // Bounded queue of graph delta events
const SATURATION_THRESHOLD = 0.9; // Emotion magnitude threshold for saturation warning

// 🔴 MEMORY LEAK FIX: TTL for emotion and flow maps to prevent unbounded growth
const EMOTION_TTL_MS = 5 * 60 * 1000; // 5 minutes - remove stale emotion data
const CLEANUP_INTERVAL_MS = 60 * 1000; // Run cleanup every 60 seconds

// 🎯 PHASE 4 STABILITY: 10Hz throttling to prevent flicker and excessive re-renders
const UPDATE_THROTTLE_MS = 100; // Batch updates and flush at 10Hz (100ms intervals)

const memoizedLinkId = (source?: string, target?: string, linkType?: string) =>
  source && target ? `${source}->${target}:${linkType ?? 'link'}` : undefined;

const coalesce = <T>(...values: Array<T | null | undefined>): T | undefined => {
  for (const value of values) {
    if (value !== undefined && value !== null) {
      return value;
    }
  }
  return undefined;
};

const normalizeNodePayload = (event: any): GraphNodePayload | null => {
  const directNode = event?.node ?? event?.payload?.node;
  if (directNode?.id) {
    return {
      ...directNode,
      properties: directNode.properties ?? event?.properties ?? event?.updates
    };
  }

  const nodeId = coalesce(
    event?.node_id,
    event?.id,
    event?.payload?.node_id
  );
  if (!nodeId) return null;

  const properties =
    event?.properties ??
    event?.updates ??
    event?.payload?.properties ??
    event?.payload?.updates;

  return {
    id: nodeId,
    name: coalesce(
      event?.name,
      properties?.name,
      event?.payload?.name
    ),
    type: coalesce(
      event?.node_type,
      event?.payload?.node_type,
      properties?.type
    ),
    energy: coalesce(event?.energy, properties?.energy),
    theta: coalesce(event?.theta, properties?.theta),
    log_weight: coalesce(event?.log_weight, properties?.log_weight),
    scope: properties?.scope,
    properties: properties && Object.keys(properties).length ? properties : undefined
  };
};

const normalizeLinkPayload = (event: any): GraphLinkPayload | null => {
  const directLink = event?.link ?? event?.payload?.link;
  const source = coalesce(
    directLink?.source,
    event?.source,
    event?.source_id,
    event?.payload?.source,
    event?.payload?.source_id
  );
  const target = coalesce(
    directLink?.target,
    event?.target,
    event?.target_id,
    event?.payload?.target,
    event?.payload?.target_id
  );
  if (!source || !target) return null;

  const linkType = coalesce(
    directLink?.type,
    event?.link_type,
    event?.payload?.link_type,
    event?.payload?.type
  );

  const baseId = coalesce(
    directLink?.id,
    event?.link_id,
    event?.id,
    event?.payload?.link_id,
    memoizedLinkId(source, target, linkType)
  );

  const weightRaw = coalesce(
    directLink?.weight,
    event?.weight,
    event?.payload?.weight,
    event?.metadata?.weight,
    event?.payload?.metadata?.weight
  );

  const weight =
    typeof weightRaw === 'number'
      ? weightRaw
      : typeof weightRaw?.w_total === 'number'
        ? weightRaw.w_total
        : typeof weightRaw?.weight === 'number'
          ? weightRaw.weight
          : undefined;

  const metadata = {
    ...(directLink?.metadata ?? {}),
    ...(event?.metadata ?? {}),
    ...(event?.payload?.metadata ?? {}),
    ...(typeof weightRaw === 'object' && weightRaw !== null ? { weight_components: weightRaw } : {})
  };

  return {
    id: baseId ?? memoizedLinkId(source, target, linkType) ?? `${source}->${target}`,
    source,
    target,
    type: linkType,
    weight,
    properties: Object.keys(metadata).length ? metadata : undefined
  };
};

const normalizeSubentityPayload = (event: any): GraphSubentityPayload | null => {
  const directSubentity = event?.subentity ?? event?.payload?.subentity;
  if (directSubentity?.id) {
    return {
      ...directSubentity,
      properties: directSubentity.properties ?? event?.properties ?? event?.payload?.properties
    };
  }

  const subId = coalesce(
    event?.subentity_id,
    event?.id,
    event?.payload?.subentity_id
  );
  if (!subId) return null;

  const properties =
    event?.properties ??
    event?.payload?.properties;

  return {
    id: subId,
    name: coalesce(event?.name, properties?.name),
    kind: coalesce(event?.kind, properties?.kind, event?.subentity_type),
    energy: coalesce(event?.energy, properties?.energy),
    threshold: coalesce(event?.threshold, properties?.threshold),
    activation_level: coalesce(event?.activation_level, properties?.activation_level),
    member_count: coalesce(event?.member_count, properties?.member_count),
    quality: coalesce(event?.quality, properties?.quality),
    stability: coalesce(event?.stability, properties?.stability_state),
    properties: properties && Object.keys(properties).length ? properties : undefined
  };
};

const deriveLinkId = (event: any): string | undefined => {
  const link = event?.link ?? event?.payload?.link;
  const source = coalesce(
    link?.source,
    event?.source,
    event?.source_id,
    event?.payload?.source,
    event?.payload?.source_id
  );
  const target = coalesce(
    link?.target,
    event?.target,
    event?.target_id,
    event?.payload?.target,
    event?.payload?.target_id
  );
  const linkType = coalesce(
    link?.type,
    event?.link_type,
    event?.payload?.link_type,
    event?.payload?.type
  );
  return coalesce(
    link?.id,
    event?.link_id,
    event?.id,
    event?.payload?.link_id,
    memoizedLinkId(source, target, linkType)
  );
};

const deriveSubentityId = (event: any): string | undefined =>
  coalesce(
    event?.subentity?.id,
    event?.payload?.subentity?.id,
    event?.subentity_id,
    event?.payload?.subentity_id,
    event?.id
  );

const deriveNodeId = (event: any): string | undefined =>
  coalesce(
    event?.node?.id,
    event?.payload?.node?.id,
    event?.node_id,
    event?.payload?.node_id,
    event?.id
  );

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
 * const { subentityActivity, thresholdCrossings, consciousnessState } = useWebSocket();
 *
 * Author: Iris "The Aperture"
 * Backend integration: Felix "Ironhand"'s WebSocket infrastructure
 */
export function useWebSocket(): WebSocketStreams {
  // Connection state
  const [connectionState, setConnectionState] = useState<WebSocketState>(WebSocketState.CONNECTING);
  const [error, setError] = useState<string | null>(null);
  const orgFilterRef = useRef<string | undefined>(process.env.NEXT_PUBLIC_ORG_ID);

  // Event streams (v1 legacy)
  const [subentityActivity, setSubEntityActivity] = useState<SubEntityActivityEvent[]>([]);
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

  // Membrane-first org hierarchy (sidebar routing)
  const [hierarchySnapshot, setHierarchySnapshot] = useState<{
    org?: string;
    ecosystems?: string[];
    citizens?: Array<{ id: string; label?: string; status?: string }>;
    lanes?: Array<{ id: string; capacity: number; ack_policy: string }>;
    ts?: string;
  } | null>(null);

  // Economy overlays keyed by citizen/organization id
  const [economyOverlays, setEconomyOverlays] = useState<Record<string, EconomyOverlayState>>({});

  // Wallet auth + attestation state
  const [walletChallenge, setWalletChallenge] = useState<{ nonce: string; ttl_ms: number } | null>(null);
  const [walletContext, setWalletContext] = useState<{ org?: string; roles?: string[]; citizenIds?: string[]; ecosystems?: string[] } | null>(null);
  const [lastInjectAck, setLastInjectAck] = useState<{ id: string; status: 'accepted' | 'rejected'; reason?: string; ts: string } | null>(null);
  const [citizenResponses, setCitizenResponses] = useState<Array<{ citizenId: string; content: string; timestamp: string }>>([]);

  const [graphNodesState, setGraphNodesState] = useState<Record<string, GraphNodePayload>>({});
  const [graphLinksState, setGraphLinksState] = useState<Record<string, GraphLinkPayload>>({});
  const [graphSubentitiesState, setGraphSubentitiesState] = useState<Record<string, GraphSubentityPayload>>({});

  const updateEconomyOverlay = useCallback((key: string, updates: Partial<{
    balance: number;
    spent60s: number;
    budgetRemain: number;
    softCap: number;
    kEcon: number;
    ubcNextEta: string | undefined;
    lastSigAt: number;
    lastUbcAt: number;
  }>) => {
    setEconomyOverlays(prev => {
      const existing = prev[key] ?? { };
      const next = { ...existing, ...updates };
      return { ...prev, [key]: next };
    });
  }, []);

  // Priority 4: Weight learning events
  const [weightLearningEvents, setWeightLearningEvents] = useState<WeightsUpdatedTraceEvent[]>([]);

  // Priority 5: Stride selection events
  const [strideSelectionEvents, setStrideSelectionEvents] = useState<StrideSelectionEvent[]>([]);

  // Priority 6: Phenomenology health events
  const [phenomenologyMismatchEvents, setPhenomenologyMismatchEvents] = useState<PhenomenologyMismatchEvent[]>([]);
  const [phenomenologyHealthEvents, setPhenomenologyHealthEvents] = useState<PhenomenologicalHealthEvent[]>([]);

  // Subentity activation snapshots (active subentities panel)
  const [subentitySnapshots, setSubentitySnapshots] = useState<Record<string, {
    active: Array<{id: string; name: string; energy: number; theta: number}>;
    wm: Array<{id: string; name: string; share: number}>;
    frame: number;
    t: number;
  }>>({});

  // Working memory + perceptual overlays
  const [wmStream, setWmStream] = useState<WmEmitEvent | null>(null);
  const [wmSelectionEvents, setWmSelectionEvents] = useState<WmSelectedEvent[]>([]);
  const [weightsUpdatedEvents, setWeightsUpdatedEvents] = useState<WeightsUpdatedEvent[]>([]);
  const [subentityWeightEvents, setSubentityWeightEvents] = useState<SubentityWeightsUpdatedEvent[]>([]);
  const [membershipPrunedEvents, setMembershipPrunedEvents] = useState<SubentityMembershipPrunedEvent[]>([]);
  const [boundarySummaries, setBoundarySummaries] = useState<BoundarySummaryEvent[]>([]);
  const [perceptFrames, setPerceptFrames] = useState<Record<string, PerceptFrameEvent>>({});

  const graphDeltaQueueRef = useRef<GraphDeltaEvent[]>([]);
  const graphDeltaBaseRef = useRef(0);
  const [graphDeltaVersion, setGraphDeltaVersion] = useState(0);

  // Forged identity telemetry streams
  const [forgedIdentityFrames, setForgedIdentityFrames] = useState<ForgedIdentityFrameEvent[]>([]);
  const [forgedIdentityMetrics, setForgedIdentityMetrics] = useState<Record<string, ForgedIdentityMetricsEvent>>({});

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
  const forgedFrameTrackerRef = useRef<Map<string, number>>(new Map());

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

    const nodeUpserts: GraphNodePayload[] = [];
    const nodeDeletes: string[] = [];
    const linkUpserts: GraphLinkPayload[] = [];
    const linkDeletes: string[] = [];
    const subentityUpserts: GraphSubentityPayload[] = [];
    const subentityDeletes: string[] = [];

    // Process all updates in single pass
    updates.forEach((data) => {
      const rawType =
        (data as any)?.type ??
        (data as any)?.topic ??
        (data as any)?.kind;

      if (rawType && !(data as any)?.type) {
        (data as any).type = rawType;
      }

      const eventType = rawType as string | undefined;
      if (!eventType) {
        console.warn('[WebSocket] Dropping event without type/topic:', data);
        return;
      }

      switch (eventType) {
        // V1 events (legacy)
        case 'subentity_activity':
          setSubEntityActivity(prev => {
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

        case 'graph.delta.node.upsert':
        case 'graph.delta.node.delete':
        case 'graph.delta.link.upsert':
        case 'graph.delta.link.delete':
        case 'graph.delta.subentity.upsert':
        case 'graph.delta.subentity.delete': {
          const event = data as GraphDeltaEvent & { payload?: any };
          const payload = event?.payload ?? {};
          const normalizedEvent = { ...payload, ...event, type: eventType };

          graphDeltaQueueRef.current.push(event);
          if (graphDeltaQueueRef.current.length > MAX_GRAPH_DELTA_EVENTS) {
            const removed = graphDeltaQueueRef.current.length - MAX_GRAPH_DELTA_EVENTS;
            graphDeltaQueueRef.current.splice(0, removed);
            graphDeltaBaseRef.current += removed;
          }
          setGraphDeltaVersion(prev => prev + 1);

          switch (eventType) {
            case 'graph.delta.node.upsert':
              {
                const resolvedNode = normalizeNodePayload(normalizedEvent);
                if (resolvedNode) {
                  nodeUpserts.push(resolvedNode);
                }
              }
              break;
            case 'graph.delta.node.delete': {
              const id = deriveNodeId(normalizedEvent);
              if (id) nodeDeletes.push(id);
              break;
            }
            case 'graph.delta.link.upsert':
              {
                const resolvedLink = normalizeLinkPayload(normalizedEvent);
                if (resolvedLink) {
                  linkUpserts.push(resolvedLink);
                }
              }
              break;
            case 'graph.delta.link.delete': {
              const id = deriveLinkId(normalizedEvent);
              if (id) linkDeletes.push(id);
              break;
            }
            case 'graph.delta.subentity.upsert':
              {
                const resolvedSubentity = normalizeSubentityPayload(normalizedEvent);
                if (resolvedSubentity) {
                  subentityUpserts.push(resolvedSubentity);
                }
              }
              break;
            case 'graph.delta.subentity.delete': {
              const id = deriveSubentityId(normalizedEvent);
              if (id) subentityDeletes.push(id);
              break;
            }
            default:
              break;
          }
          break;
        }

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
          setWmStream(prev => {
            // Avoid unnecessary updates if payload unchanged (shallow)
            if (prev && prev.frame_id === wmEvent.frame_id && prev.t_ms === wmEvent.t_ms) {
              return prev;
            }
            return wmEvent;
          });
          setV2State(prev => {
            const nodeIds = wmEvent.selected_nodes
              ?? (wmEvent as any).node_ids
              ?? [];

            if (!Array.isArray(nodeIds)) {
              console.warn('[useWebSocket] wm.emit event missing iterable node ids:', wmEvent);
              return prev;
            }

            const newNodeIds = new Set<string>(nodeIds as string[]);
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

        case 'wm.selected': {
          const wmSelectedEvent = data as WmSelectedEvent;
          setWmSelectionEvents(prev => {
            const updated = [...prev, wmSelectedEvent];
            return updated.slice(-MAX_WM_SELECTED_EVENTS);
          });
          break;
        }

        case 'node.flip': {
          const flipEvent = data as NodeFlipEvent;
          setV2State(prev => {
            // Defensive validation: ensure nodes array exists
            if (!flipEvent.nodes || !Array.isArray(flipEvent.nodes)) {
              console.warn('[useWebSocket] node.flip event missing nodes array:', flipEvent);
              return prev;
            }

            // Unpack batch into individual flip records
            const newFlips = flipEvent.nodes.map(node => ({
              node_id: node.id,
              direction: (node.dE > 0 ? 'on' : 'off') as 'on' | 'off',
              dE: node.dE,
              timestamp: Date.now()
            }));

            const updated = [...prev.recentFlips, ...newFlips];
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
            const rawFlows =
              (flowEvent as any).flows ??
              (flowEvent as any).payload?.flows ??
              (flowEvent as any).payload?.flow_summary; // legacy alias

            if (!rawFlows || !Array.isArray(rawFlows)) {
              console.warn('[useWebSocket] link.flow.summary event missing flows array:', flowEvent);
              return prev;
            }

            const flows = rawFlows
              .map((flow: any) => ({
                link_id: flow.link_id ?? flow.link?.id ?? flow.id,
                flow: flow.flow ?? flow.value ?? flow.amount,
              }))
              .filter((flow: any) => flow.link_id);

            if (flows.length === 0) {
              console.warn('[useWebSocket] link.flow.summary event contained no identifiable link_ids:', flowEvent);
              return prev;
            }

            let hasChanges = false;
            for (const flow of flows) {
              if (prev.linkFlows.get(flow.link_id) !== flow.flow) {
                hasChanges = true;
                break;
              }
            }

            if (!hasChanges) {
              return prev;
            }

            const newFlows = new Map(prev.linkFlows);
            flows.forEach(flow => {
              newFlows.set(flow.link_id, flow.flow);
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

        case 'weights.updated': {
          const weightEvent = data as WeightsUpdatedEvent;
          setWeightsUpdatedEvents(prev => {
            const updated = [...prev, weightEvent];
            return updated.slice(-MAX_WEIGHT_UPDATE_EVENTS);
          });
          break;
        }

        case 'subentity.weights.updated': {
          const weightsEvent = data as SubentityWeightsUpdatedEvent;
          setSubentityWeightEvents(prev => {
            const updated = [...prev, weightsEvent];
            return updated.slice(-MAX_SUBENTITY_WEIGHT_EVENTS);
          });
          break;
        }

        case 'subentity.membership.pruned': {
          const prunedEvent = data as SubentityMembershipPrunedEvent;
          setMembershipPrunedEvents(prev => {
            const updated = [...prev, prunedEvent];
            return updated.slice(-MAX_SUBENTITY_WEIGHT_EVENTS);
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

        case 'citizen.response': {
          const response = data as any;
          if (response) {
            setCitizenResponses(prev => {
              const updated = [...prev, {
                citizenId: response.citizen_id ?? response.citizen,
                content: response.response_text ?? response.content ?? '',
                timestamp: response.ts ?? new Date().toISOString()
              }];
              return updated.slice(-200);
            });
          }
          break;
        }

        case 'hierarchy.snapshot@1.0': {
          const snapshot = data as any;
          setHierarchySnapshot({
            org: snapshot.org,
            ecosystems: snapshot.ecosystems,
            citizens: snapshot.citizens,
            lanes: snapshot.lanes,
            ts: snapshot.ts
          });
          break;
        }

        case 'telemetry.economy.spend@1.0': {
          const spend = data as any;
          if (spend.by === 'node' && typeof spend.key === 'string') {
            const citizenKey = spend.key.startsWith('citizen:') ? spend.key.replace(/^citizen:/, '') : spend.key;
            const updates: Record<string, any> = {};
            if (spend.metrics?.balance_mind !== undefined) updates.balance = spend.metrics.balance_mind;
            if (spend.window === '60s' && spend.metrics?.spent_mind !== undefined) updates.spent60s = spend.metrics.spent_mind;
            if (spend.metrics?.budget_remaining_mind !== undefined) updates.budgetRemain = spend.metrics.budget_remaining_mind;
            if (spend.metrics?.soft_cap_mind !== undefined) updates.softCap = spend.metrics.soft_cap_mind;
            if (spend.metrics?.k_econ !== undefined) updates.kEcon = spend.metrics.k_econ;
            if (spend.metrics?.ubc_next_eta !== undefined) updates.ubcNextEta = spend.metrics.ubc_next_eta;
            updateEconomyOverlay(citizenKey, updates);
          }
          break;
        }

        case 'telemetry.economy.ubc_tick@1.0': {
          const tick = data as any;
          if (tick?.citizen_id) {
            updateEconomyOverlay(tick.citizen_id, {
              lastUbcAt: Date.now()
            });
          }
          break;
        }

        case 'wallet.signature.attested@1.0': {
          const attestation = data as any;
          if (attestation?.citizen_id) {
            updateEconomyOverlay(attestation.citizen_id, {
              lastSigAt: Date.now()
            });
          }
          break;
        }

        case 'auth.wallet.challenge.issued@1.0': {
          const issued = data as any;
          setWalletChallenge({
            nonce: issued.nonce,
            ttl_ms: issued.ttl_ms
          });
          break;
        }

        case 'auth.wallet.accepted@1.0': {
          const accepted = data as any;
          setWalletContext({
            org: accepted.org,
            roles: accepted.roles,
            citizenIds: accepted.citizen_ids,
            ecosystems: accepted.ecosystems
          });
          if (accepted.org) {
            orgFilterRef.current = accepted.org;
            if (_ws && _ws.readyState === WebSocket.OPEN) {
              try {
                _ws.send(JSON.stringify({
                  type: 'subscribe@1.0',
                  topics: [
                    'graph.delta.node.*',
                    'graph.delta.link.*',
                    'wm.emit',
                    'percept.frame',
                    'hierarchy.snapshot',
                    'auth.wallet.*',
                    'telemetry.economy.spend',
                    'telemetry.economy.ubc_tick',
                    'wallet.signature.attested',
                    'inject.ack',
                    'membrane.inject.ack'
                  ],
                  filters: { org: orgFilterRef.current }
                }));
              } catch (resubErr) {
                console.error('[WebSocket] Failed to resubscribe after wallet acceptance:', resubErr);
              }
            }
          }
          break;
        }

        case 'inject.ack': {
          const ack = data as any;
          setLastInjectAck({
            id: ack.id,
            status: ack.status,
            reason: ack.reason,
            ts: ack.ts
          });
          break;
        }

        case 'membrane.inject.ack': {
          const ackEvent = data as MembraneInjectAckEvent;
          const payload = ackEvent?.payload ?? (data as any);
          const ackId =
            payload?.envelope_id ??
            payload?.stimulus_id ??
            payload?.id ??
            ackEvent?.id;
          const ackTimestamp =
            typeof payload?.t_ms === 'number'
              ? new Date(payload.t_ms).toISOString()
              : payload?.ts ?? ackEvent?.ts ?? new Date().toISOString();

          setLastInjectAck({
            id: ackId,
            status: payload?.status ?? 'accepted',
            reason: payload?.reason,
            ts: ackTimestamp
          });
          break;
        }

        case 'gap.detected':
        case 'emergence.reject':
        case 'emergence.candidate':
        case 'emergence.spawn':
        case 'emergence.redirect':
        case 'membership.updated':
        case 'mode.snapshot':
        case 'mode.metastable_pattern':
        case 'mode.community.detected':
        case 'state_modulation.frame':
        case 'rich_club.snapshot':
        case 'rich_club.hub_at_risk':
        case 'integration_metrics.node':
        case 'integration_metrics.population':
        case 'subentity.activation':
          // These events feed membrane-first graph streams handled elsewhere; ignore to avoid duplicate state.
          break;

        case 'subscribe.ack@1.0': {
          console.log('[WebSocket] Subscribe ACK:', data);
          break;
        }

        // Subentity activation snapshots (active subentities panel)
        case 'subentity.snapshot': {
          const snapshot = data as any; // {v, frame_id, citizen_id, active, wm, t_ms}
          setSubentitySnapshots(prev => ({
            ...prev,
            [snapshot.citizen_id]: {
              active: snapshot.active || [],
              wm: snapshot.wm || [],
              frame: snapshot.frame_id,
              t: snapshot.t_ms
            }
          }));
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

        case 'se.boundary.summary': {
          const summary = data as BoundarySummaryEvent;
          setBoundarySummaries(prev => {
            const updated = [...prev, summary];
            return updated.slice(-MAX_BOUNDARY_SUMMARIES);
          });
          break;
        }

        case 'percept.frame': {
          const percept = data as PerceptFrameEvent;
          setPerceptFrames(prev => {
            const key = `${percept.entity_id}:${percept.phase ?? 'default'}`;
            const existing = prev[key];
            if (existing && existing.cursor === percept.cursor && existing.ts_ms === percept.ts_ms) {
              return prev;
            }
            const next = { ...prev, [key]: percept };
            const keys = Object.keys(next);
            if (keys.length > 128) {
              const pruned: Record<string, PerceptFrameEvent> = {};
              keys.slice(-128).forEach(k => {
                pruned[k] = next[k];
              });
              return pruned;
            }
            return next;
          });
          break;
        }

        case 'forged.identity.frame': {
          const frameEvent = data as ForgedIdentityFrameEvent;
          const citizenKey = frameEvent.citizen_id || 'unknown';
          const lastMap = forgedFrameTrackerRef.current;
          const lastFrameId = lastMap.get(citizenKey);

          if (lastFrameId !== undefined && frameEvent.frame_id <= lastFrameId) {
            break;
          }

          lastMap.set(citizenKey, frameEvent.frame_id);
          setForgedIdentityFrames(prev => {
            const withoutDuplicates = prev.filter(
              frame => !(frame.citizen_id === citizenKey && frame.frame_id === frameEvent.frame_id)
            );
            const updated = [frameEvent, ...withoutDuplicates];
            return updated.slice(0, MAX_FORGED_IDENTITY_FRAMES);
          });
          break;
        }

        case 'forged.identity.metrics': {
          const metricsEvent = data as ForgedIdentityMetricsEvent;
          if (!metricsEvent.citizen_id) {
            break;
          }

          setForgedIdentityMetrics(prev => {
            const existing = prev[metricsEvent.citizen_id];
            if (
              existing &&
              existing.frame_id === metricsEvent.frame_id &&
              existing.tokens_accumulated === metricsEvent.tokens_accumulated
            ) {
              return prev;
            }

            return {
              ...prev,
              [metricsEvent.citizen_id]: metricsEvent
            };
          });
          break;
        }

        // P2.1.3: Tier link strengthening (Felix) - received but not stored yet
        // Future: Store for detailed link-level learning observability
        case 'tier.link.strengthened':
          break;

        // Internal consciousness engine events (safe to ignore)
        case 'criticality.state':
        case 'decay.tick':
        case 'tick.update':
          break;

        // Raw link events - pass through to useGraphStream (backward compatibility)
        case 'MEMBER_OF':
        case 'ACTIVATES':
        case 'INHIBITS':
          // These are handled by useGraphStream.ts, not useWebSocket.ts
          // No processing needed here, just acknowledge receipt
          break;

        // Snapshot chunks - pass through to useGraphStream (control messages)
        case 'snapshot.begin@1.0':
        case 'snapshot.chunk@1.0':
        case 'snapshot.end@1.0':
          // Handled by useGraphStream.ts for initial graph state loading
          break;

        // WebSocket keepalive (ignore silently)
        case 'ping':
        case 'pong':
          break;

        default:
          // 🎯 Catch unknown events to prevent silent drops
          console.warn('[WebSocket] Unknown event type:', eventType, data);
      }
    });

    if (nodeUpserts.length || nodeDeletes.length) {
      setGraphNodesState(prev => {
        const next = { ...prev };
        nodeUpserts.forEach(node => {
          if (node?.id) {
            next[node.id] = { ...(next[node.id] ?? {}), ...node };
          }
        });
        nodeDeletes.forEach(id => {
          if (id && next[id]) {
            delete next[id];
          }
        });
        return next;
      });
    }

    if (linkUpserts.length || linkDeletes.length) {
      setGraphLinksState(prev => {
        const next = { ...prev };
        linkUpserts.forEach(link => {
          if (link?.id) {
            next[link.id] = { ...(next[link.id] ?? {}), ...link };
          }
        });
        linkDeletes.forEach(id => {
          if (id && next[id]) {
            delete next[id];
          }
        });
        return next;
      });
    }

    if (subentityUpserts.length || subentityDeletes.length) {
      setGraphSubentitiesState(prev => {
        const next = { ...prev };
        subentityUpserts.forEach(sub => {
          if (sub?.id) {
            next[sub.id] = { ...(next[sub.id] ?? {}), ...sub };
          }
        });
        subentityDeletes.forEach(id => {
          if (id && next[id]) {
            delete next[id];
          }
        });
        return next;
      });
    }
  }, []);

  /**
   * Handle incoming WebSocket messages
   * 🎯 PHASE 4: Buffered mode - accumulate events, flush at 10Hz
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const rawData = JSON.parse(event.data);

      // 🎯 STEP A: Transport diagnostic - prove events arrive
      diagOnEvent(rawData);

      // 🎯 PART B: Normalize events (handle backend evolution)
      const data = normalizeEvent(rawData);
      if (data && typeof data === 'object') {
        const typedData = data as Record<string, any>;
        typedData.type =
          typedData.type ??
          typedData.topic ??
          typedData.kind ??
          typedData.event_type ??
          typedData.eventType ??
          typedData.event;
      }

      // Buffer event for batch processing
      // flushPendingUpdates will process at 10Hz
      pendingUpdatesRef.current.push(data);
    } catch (err) {
      // Malformed JSON is expected when server sends concatenated/partial messages
      // Don't treat as error - just skip this message and continue
      console.warn('[WebSocket] Skipping malformed message:', err instanceof Error ? err.message : 'unknown error');
      // Don't set error state - this is not a critical failure
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const debugDispatch = (evt: any) => {
      try {
        handleMessage({ data: JSON.stringify(evt) } as MessageEvent);
      } catch (err) {
        console.error('[WebSocket] Failed to dispatch debug event:', err);
      }
    };

    (window as any).__debugDispatch = debugDispatch;
    return () => {
      if ((window as any).__debugDispatch === debugDispatch) {
        delete (window as any).__debugDispatch;
      }
    };
  }, [handleMessage]);

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

        const subscribePayload: Record<string, any> = {
          type: 'subscribe@1.0',
          topics: [
            'snapshot.*',  // Subscribe to snapshot events (initial graph state)
            'graph.delta.node.*',
            'graph.delta.link.*',
            'wm.emit',
            'percept.frame',
            'hierarchy.snapshot',
            'auth.wallet.*',
            'telemetry.economy.spend',
            'telemetry.economy.ubc_tick',
            'wallet.signature.attested',
            'inject.ack',
            'membrane.inject.ack'
          ]
        };
        if (orgFilterRef.current) {
          subscribePayload.filters = { org: orgFilterRef.current };
        }
        try {
          ws.send(JSON.stringify(subscribePayload));
        } catch (sendErr) {
          console.error('[WebSocket] Failed to send subscribe payload:', sendErr);
        }
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

    // 🔴 CONNECTION LEAK FIX: Close WebSocket on unmount to prevent hot-reload leaks
    // Singleton pattern kept connections alive during hot-reload, causing 47+ connections
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

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

  useEffect(() => {
    (window as any).__ws_debug_dispatch = (payload: any) => {
      try {
        const message = typeof payload === 'string' ? payload : JSON.stringify(payload);
        handleMessage({ data: message } as MessageEvent);
        flushPendingUpdates();
      } catch (err) {
        console.error('[WebSocket] __ws_debug_dispatch failed:', err);
      }
    };

    return () => {
      delete (window as any).__ws_debug_dispatch;
    };
  }, [handleMessage, flushPendingUpdates]);

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

  const ensureInjectSocket = useCallback(() => {
    if (_injectWs && (_injectWs.readyState === WebSocket.OPEN || _injectWs.readyState === WebSocket.CONNECTING)) {
      return _injectWs;
    }

    if (_injectConnecting) {
      return _injectWs;
    }

    try {
      const socket = new WebSocket(WS_INJECT_URL);
      _injectWs = socket;
      _injectConnecting = true;

      socket.onopen = () => {
        _injectConnecting = false;
        console.log('[InjectWS] Connected');
      };

      socket.onclose = () => {
        _injectConnecting = false;
        _injectWs = null;
        console.log('[InjectWS] Disconnected');
      };

      socket.onerror = (err) => {
        console.error('[InjectWS] Error', err);
      };
    } catch (err) {
      console.error('[InjectWS] Failed to open socket', err);
      _injectConnecting = false;
      _injectWs = null;
    }

    return _injectWs;
  }, []);

  const injectStimulus = useCallback((envelope: Record<string, any>) => {
    const id = envelope.id || (typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `stim-${Date.now()}`);
    const payload = {
      v: envelope.v ?? '1.1',
      type: 'membrane.inject',
      id,
      ts: envelope.ts ?? new Date().toISOString(),
      org: envelope.org ?? walletContext?.org ?? orgFilterRef.current,
      scope: envelope.scope ?? 'organizational',
      origin: envelope.origin ?? 'ui',
      ttl_frames: envelope.ttl_frames ?? 300,
      ...envelope
    };

    const socket = ensureInjectSocket();
    if (!socket) {
      throw new Error('Injection socket unavailable');
    }

    const sendPayload = () => {
      try {
        socket.send(JSON.stringify(payload));
      } catch (err) {
        console.error('[InjectWS] Failed to send payload', err);
      }
    };

    if (socket.readyState === WebSocket.OPEN) {
      sendPayload();
    } else {
      const handleOpen = () => {
        socket.removeEventListener('open', handleOpen);
        sendPayload();
      };
      socket.addEventListener('open', handleOpen);
    }

    return id;
  }, [ensureInjectSocket, walletContext]);

  const graphNodes = useMemo(() => Object.values(graphNodesState), [graphNodesState]);
  const graphLinks = useMemo(() => Object.values(graphLinksState), [graphLinksState]);
  const graphSubentities = useMemo(() => Object.values(graphSubentitiesState), [graphSubentitiesState]);

  return {
    // V1 events
    subentityActivity,
    thresholdCrossings,
    consciousnessState,

    // V2 events
    v2State,

    // Emotion coloring
    emotionState,

    // Priority 4: Weight learning
    weightLearningEvents,
    weightsUpdatedEvents,

    // Priority 5: Stride selection
    strideSelectionEvents,

    // Priority 6: Phenomenology health
    phenomenologyMismatchEvents,
    phenomenologyHealthEvents,

    // Subentity activation snapshots
    subentitySnapshots,

    // Working memory + perceptual overlays
    wmStream,
    wmSelectionEvents,
    boundarySummaries,
    perceptFrames,
    subentityWeightEvents,
    membershipPrunedEvents,

    // Graph delta stream
    graphDeltaEvents: graphDeltaQueueRef.current,
    graphDeltaEventsVersion: graphDeltaVersion,
    graphDeltaEventsBase: graphDeltaBaseRef.current,

    // Forged identity observability
    forgedIdentityFrames,
    forgedIdentityMetrics,

    // Membrane-first additions
    hierarchySnapshot,
    economyOverlays,
    walletChallenge,
    walletContext,
    lastInjectAck,
    citizenResponses,
    graphNodes,
    graphLinks,
    graphSubentities,

    injectStimulus,

    // Connection
    connectionState,
    error
  };
}
