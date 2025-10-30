/**
 * useGraphStream - Membrane-First Graph State Hook
 *
 * Subscribes to membrane bus broadcasts and builds graph hierarchy
 * from the event stream. NO POLLING - pure event-driven.
 *
 * Topics subscribed:
 * - graph.delta.node.* - Node/SubEntity structure changes
 * - graph.delta.link.* - Link/membership changes
 * - wm.emit - Working memory selection (active SubEntities)
 * - percept.frame - What a SubEntity perceived this frame
 *
 * Architecture: Membrane-First (docs/specs/v2/membrane/CROSS_LEVEL_MEMBRANE.md)
 * - No HTTP polling
 * - currentGraphId derived from event provenance (not hardcoded)
 * - State built incrementally from broadcasts
 */

'use client';

import { useEffect, useState, useCallback } from 'react';

export type GraphId = string; // e.g. "citizen_felix" | "org_mind_protocol"

export interface SubEntityInfo {
  id: string;
  slug?: string;
  name?: string;
  members: Set<string>; // node IDs that are MEMBER_OF this SubEntity
  active?: boolean; // in working memory
  anchorsTop?: string[]; // top attention nodes
  anchorsPeripheral?: string[]; // peripheral attention nodes
  affect?: number;
  novelty?: number;
  uncertainty?: number;
  goalFit?: number;
}

export interface HierarchySnapshot {
  subentities: Record<string, SubEntityInfo>;
  nodes: Record<string, { id: string; name?: string; type?: string }>;
  lastUpdate: number;
}

export interface EmergenceEvent {
  id: string;
  ts: string;
  frame: number;
  type: 'gap' | 'candidate' | 'spawn' | 'redirect' | 'reject' | 'membership';
  payload: any;
}

export interface EmergenceState {
  recentGaps: EmergenceEvent[];
  recentCandidates: EmergenceEvent[];
  recentSpawns: EmergenceEvent[];
  recentRedirects: EmergenceEvent[];
  recentRejects: EmergenceEvent[];
  recentMembershipUpdates: EmergenceEvent[];
  totalGapsDetected: number;
  totalSpawned: number;
  totalRejected: number;
}

export interface RichClubHub {
  node_id: string;
  betweenness: number;
  energy: number;
}

export interface IntegrationMetrics {
  node_id: string;
  depth: number;
  breadth: number;
  closeness: number;
}

export interface StateModulation {
  arousal: number;
  precision: number;
  goal_alignment: number;
  top_modulated_edges?: Array<{
    source: string;
    target: string;
    w_base: number;
    w_eff: number;
  }>;
}

export interface TopologyState {
  richClubHubs: RichClubHub[];
  hubsAtRisk: RichClubHub[];
  integrationMetrics: Map<string, IntegrationMetrics>;
  stateModulation: StateModulation | null;
  lastRichClubUpdate: number;
  lastStateUpdate: number;
}

export interface GraphStreamState {
  graphs: Map<GraphId, HierarchySnapshot>;
  currentGraphId: GraphId | null;
  connected: boolean;
  error: string | null;
  emergence: EmergenceState;
  topology: TopologyState;
}

const MEMBRANE_BUS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/ws';

/**
 * Hook to subscribe to membrane bus and build graph hierarchy from events.
 *
 * @param onGraphIdChange - Callback when currentGraphId changes
 * @returns GraphStreamState with current graphs and selected graphId
 */
export function useGraphStream(
  onGraphIdChange?: (graphId: GraphId) => void
): GraphStreamState {
  const [graphs, setGraphs] = useState<Map<GraphId, HierarchySnapshot>>(new Map());
  const [currentGraphId, setCurrentGraphId] = useState<GraphId | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emergence, setEmergence] = useState<EmergenceState>({
    recentGaps: [],
    recentCandidates: [],
    recentSpawns: [],
    recentRedirects: [],
    recentRejects: [],
    recentMembershipUpdates: [],
    totalGapsDetected: 0,
    totalSpawned: 0,
    totalRejected: 0
  });

  const [topology, setTopology] = useState<TopologyState>({
    richClubHubs: [],
    hubsAtRisk: [],
    integrationMetrics: new Map(),
    stateModulation: null,
    lastRichClubUpdate: 0,
    lastStateUpdate: 0
  });

  // Helper to get or create graph snapshot
  const ensureGraph = useCallback((graphId: GraphId, graphsMap: Map<GraphId, HierarchySnapshot>) => {
    if (!graphsMap.has(graphId)) {
      graphsMap.set(graphId, {
        subentities: {},
        nodes: {},
        lastUpdate: Date.now()
      });
    }
    return graphsMap.get(graphId)!;
  }, []);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;

    const connect = () => {
      try {
        ws = new WebSocket(MEMBRANE_BUS_URL);

        ws.onopen = () => {
          console.log('[useGraphStream] Connected to membrane bus');
          setConnected(true);
          setError(null);

          // Subscribe to membrane topics
          ws?.send(JSON.stringify({
            type: 'subscribe@1.0',
            topics: [
              'graph.delta.node.*',
              'graph.delta.link.*',
              'graph.delta.subentity.*',
              'wm.emit',
              'percept.frame',
              'emergence.*',
              'mode.*',
              'state_modulation.frame',
              'rich_club.*',
              'integration_metrics.*'
            ]
          }));
        };

        ws.onmessage = (ev) => {
          try {
            const msg = JSON.parse(ev.data);
            const eventType = msg.type ?? msg.topic;

            if (!eventType) {
              console.warn('[useGraphStream] Event missing type/topic field:', msg);
              return;
            }

            if (eventType === 'subscribe.ack@1.0' || eventType === 'subscribe.ack') {
              console.log('[useGraphStream] Subscribe ACK received:', msg.topics ?? msg.spec);
              return;
            }

            if (eventType === 'ping' || eventType === 'pong') {
              return;
            }

            // Validate normative event envelope (unified spec)
            // Required fields: type, id, spec, provenance
            if (!msg.id || !msg.spec || !msg.provenance) {
              console.warn('[useGraphStream] Invalid event envelope - missing required fields (id, spec, provenance):', msg);
              return;
            }

            // Validate spec structure
            if (!msg.spec.name || !msg.spec.rev) {
              console.warn('[useGraphStream] Invalid spec - missing name or rev:', msg.spec);
              return;
            }

            // Validate provenance structure (frozen shape)
            // provenance: { scope, citizen_id?, org_id?, component?, mission_id? }
            if (!msg.provenance.scope ||
                (msg.provenance.scope === 'personal' && !msg.provenance.citizen_id) ||
                (msg.provenance.scope === 'organizational' && !msg.provenance.org_id)) {
              console.warn('[useGraphStream] Invalid provenance - missing required scope fields:', msg.provenance);
              return;
            }

            // Derive graphId from provenance (canonical format)
            const graphId: GraphId = msg.provenance.scope === 'personal' && msg.provenance.citizen_id
              ? `citizen_${msg.provenance.citizen_id}`
              : msg.provenance.scope === 'organizational' && msg.provenance.org_id
                ? `org_${msg.provenance.org_id}`
                : 'unknown';

            if (graphId === 'unknown') {
              console.warn('[useGraphStream] No valid scope in provenance:', msg.provenance);
              return;
            }

            setGraphs(prev => {
              const next = new Map(prev);
              const snap = ensureGraph(graphId, next);

              // Handle event types (normative vocabulary: 'type' not 'topic')
              switch (eventType) {
                case 'graph.delta.node.upsert': {
                  // Felix's emergence.v1 format: msg.payload.node_id, msg.payload.properties
                  console.log('[useGraphStream] 🔵 graph.delta.node.upsert received', {
                    hasPayload: !!msg.payload,
                    payloadKeys: msg.payload ? Object.keys(msg.payload) : [],
                    fullEvent: msg
                  });
                  const payload = msg.payload;
                  if (!payload || !payload.node_id) {
                    console.warn('[useGraphStream] graph.delta.node.upsert missing payload.node_id');
                    break;
                  }

                  const nodeId = payload.node_id;
                  const nodeType = payload.node_type || 'Unknown';
                  const properties = payload.properties || {};

                  if (nodeType === 'SubEntity') {
                    snap.subentities[nodeId] = snap.subentities[nodeId] || {
                      id: nodeId,
                      members: new Set()
                    };
                    // Extract slug from role_or_topic property
                    snap.subentities[nodeId].slug = properties.role_or_topic ?? snap.subentities[nodeId].slug;
                    snap.subentities[nodeId].name = properties.name ?? snap.subentities[nodeId].name;
                  } else {
                    // Regular content node
                    snap.nodes[nodeId] = {
                      id: nodeId,
                      name: properties.name,
                      type: nodeType
                    };
                  }
                  snap.lastUpdate = Date.now();
                  break;
                }

                case 'graph.delta.link.upsert': {
                  // Felix's emergence.v1 format: msg.payload.source, msg.payload.target, msg.payload.type
                  const payload = msg.payload;
                  if (!payload || !payload.source || !payload.target) {
                    console.warn('[useGraphStream] graph.delta.link.upsert missing payload.source or payload.target', {
                      hasPayload: !!payload,
                      payloadKeys: payload ? Object.keys(payload) : [],
                      fullEvent: msg
                    });
                    break;
                  }

                  const linkType = payload.type || 'UNKNOWN';
                  const source = payload.source;
                  const target = payload.target;

                  if (linkType === 'MEMBER_OF') {
                    // Ensure target SubEntity exists
                    if (!snap.subentities[target]) {
                      snap.subentities[target] = {
                        id: target,
                        members: new Set()
                      };
                    }
                    snap.subentities[target].members.add(source);
                  }
                  snap.lastUpdate = Date.now();
                  break;
                }

                case 'wm.emit': {
                  // Mark all SubEntities as inactive first
                  Object.keys(snap.subentities).forEach(seId => {
                    snap.subentities[seId].active = false;
                  });

                  // Mark selected SubEntities as active
                  const subentities = msg.subentities || [];
                  subentities.forEach((seId: string) => {
                    if (!snap.subentities[seId]) {
                      snap.subentities[seId] = {
                        id: seId,
                        members: new Set()
                      };
                    }
                    snap.subentities[seId].active = true;
                  });

                  snap.lastUpdate = Date.now();

                  // First wm.emit sets currentGraphId
                  if (!currentGraphId) {
                    setCurrentGraphId(graphId);
                    if (onGraphIdChange) onGraphIdChange(graphId);
                  }
                  break;
                }

                case 'percept.frame': {
                  const seId = msg.provenance.subentity_id;
                  if (!seId) {
                    console.warn('[useGraphStream] percept.frame missing provenance.subentity_id');
                    break;
                  }

                  if (!snap.subentities[seId]) {
                    snap.subentities[seId] = {
                      id: seId,
                      members: new Set()
                    };
                  }

                  const se = snap.subentities[seId];
                  se.anchorsTop = msg.anchors_top ?? se.anchorsTop;
                  se.anchorsPeripheral = msg.anchors_peripheral ?? se.anchorsPeripheral;
                  se.affect = msg.affect ?? se.affect;
                  se.novelty = msg.novelty ?? se.novelty;
                  se.uncertainty = msg.uncertainty ?? se.uncertainty;
                  se.goalFit = msg.goal_match ?? se.goalFit;

                  snap.lastUpdate = Date.now();

                  // First percept.frame also sets currentGraphId
                  if (!currentGraphId) {
                    setCurrentGraphId(graphId);
                    if (onGraphIdChange) onGraphIdChange(graphId);
                  }
                  break;
                }

                // Emergence Events (emergence.v1 spec)
                case 'emergence.gap.detected':
                case 'gap.detected': {
                  const event: EmergenceEvent = {
                    id: msg.id,
                    ts: msg.ts,
                    frame: msg.provenance.frame,
                    type: 'gap',
                    payload: msg.payload
                  };
                  setEmergence(prev => ({
                    ...prev,
                    recentGaps: [event, ...prev.recentGaps].slice(0, 20),
                    totalGapsDetected: prev.totalGapsDetected + 1
                  }));
                  break;
                }

                case 'emergence.candidate': {
                  const event: EmergenceEvent = {
                    id: msg.id,
                    ts: msg.ts,
                    frame: msg.provenance.frame,
                    type: 'candidate',
                    payload: msg.payload
                  };
                  setEmergence(prev => ({
                    ...prev,
                    recentCandidates: [event, ...prev.recentCandidates].slice(0, 20)
                  }));
                  break;
                }

                case 'emergence.spawn.completed':
                case 'emergence.spawn': {
                  const event: EmergenceEvent = {
                    id: msg.id,
                    ts: msg.ts,
                    frame: msg.provenance.frame,
                    type: 'spawn',
                    payload: msg.payload
                  };
                  setEmergence(prev => ({
                    ...prev,
                    recentSpawns: [event, ...prev.recentSpawns].slice(0, 20),
                    totalSpawned: prev.totalSpawned + 1
                  }));
                  console.log('[useGraphStream] SubEntity spawned:', msg.payload.subentity_id);
                  break;
                }

                case 'emergence.redirect': {
                  const event: EmergenceEvent = {
                    id: msg.id,
                    ts: msg.ts,
                    frame: msg.provenance.frame,
                    type: 'redirect',
                    payload: msg.payload
                  };
                  setEmergence(prev => ({
                    ...prev,
                    recentRedirects: [event, ...prev.recentRedirects].slice(0, 20)
                  }));
                  break;
                }

                case 'emergence.reject': {
                  const event: EmergenceEvent = {
                    id: msg.id,
                    ts: msg.ts,
                    frame: msg.provenance.frame,
                    type: 'reject',
                    payload: msg.payload
                  };
                  setEmergence(prev => ({
                    ...prev,
                    recentRejects: [event, ...prev.recentRejects].slice(0, 20),
                    totalRejected: prev.totalRejected + 1
                  }));
                  break;
                }

                case 'membership.updated': {
                  const event: EmergenceEvent = {
                    id: msg.id,
                    ts: msg.ts,
                    frame: msg.provenance.frame,
                    type: 'membership',
                    payload: msg.payload
                  };
                  setEmergence(prev => ({
                    ...prev,
                    recentMembershipUpdates: [event, ...prev.recentMembershipUpdates].slice(0, 20)
                  }));
                  break;
                }

                // Topology Events (topology.v1 spec)
                case 'rich_club.snapshot': {
                  const hubs = msg.payload?.top_hubs || [];
                  setTopology(prev => ({
                    ...prev,
                    richClubHubs: hubs,
                    lastRichClubUpdate: Date.now()
                  }));
                  console.log('[useGraphStream] Rich-club snapshot received:', hubs.length, 'hubs');
                  break;
                }

                case 'rich_club.hub_at_risk': {
                  const hub: RichClubHub = {
                    node_id: msg.payload?.node_id || 'unknown',
                    betweenness: msg.payload?.betweenness || 0,
                    energy: msg.payload?.energy || 0
                  };
                  setTopology(prev => ({
                    ...prev,
                    hubsAtRisk: [hub, ...prev.hubsAtRisk].slice(0, 10)
                  }));
                  console.warn('[useGraphStream] Hub at risk:', hub.node_id, 'betweenness:', hub.betweenness, 'energy:', hub.energy);
                  break;
                }

                case 'integration_metrics.node': {
                  const metrics: IntegrationMetrics = {
                    node_id: msg.payload?.node_id || 'unknown',
                    depth: msg.payload?.depth || 0,
                    breadth: msg.payload?.breadth || 0,
                    closeness: msg.payload?.closeness || 0
                  };
                  setTopology(prev => {
                    const next = new Map(prev.integrationMetrics);
                    next.set(metrics.node_id, metrics);
                    return { ...prev, integrationMetrics: next };
                  });
                  break;
                }

                case 'integration_metrics.population': {
                  // Population-level stats for distribution histograms
                  console.log('[useGraphStream] Population metrics received:', msg.payload);
                  break;
                }

                case 'state_modulation.frame': {
                  setTopology(prev => ({
                    ...prev,
                    stateModulation: {
                      arousal: msg.payload?.arousal || 0,
                      precision: msg.payload?.precision || 0,
                      goal_alignment: msg.payload?.goal_alignment || 0,
                      top_modulated_edges: msg.payload?.top_modulated_edges || []
                    },
                    lastStateUpdate: Date.now()
                  }));
                  break;
                }

                default:
                  // Unknown topic - log for debugging
                  console.debug('[useGraphStream] Unhandled topic:', msg.topic);
              }

              next.set(graphId, snap);
              return next;
            });
          } catch (err) {
            // Malformed messages are expected - skip gracefully
            console.warn('[useGraphStream] Skipping malformed message:', err instanceof Error ? err.message : 'unknown');
          }
        };

        ws.onerror = (_err) => {
          // WebSocket errors are expected when backend is down - handle gracefully
          setError('Membrane bus unavailable');
          setConnected(false);
        };

        ws.onclose = () => {
          setConnected(false);

          // Graceful reconnect after 5 seconds (don't spam logs)
          reconnectTimeout = setTimeout(() => {
            connect();
          }, 5000);
        };
      } catch (err) {
        // Connection failures are expected when backend is down
        setError('Membrane bus unavailable');
        setConnected(false);
      }
    };

    connect();

    return () => {
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) {
        ws.close();
        ws = null;
      }
    };
  }, [ensureGraph, onGraphIdChange, currentGraphId]);

  return {
    graphs,
    currentGraphId,
    connected,
    error,
    emergence,
    topology
  };
}

/**
 * Dev-only mock frame publisher for testing.
 * Publishes a mock percept.frame event to simulate a live engine.
 *
 * Usage:
 *   const publisher = useMockFramePublisher();
 *   publisher.publish('citizen_felix');
 */
export function useMockFramePublisher() {
  return {
    publish: (citizenId: string) => {
      // Simulate a percept.frame event
      window.dispatchEvent(new CustomEvent('mock:percept.frame', {
        detail: {
          topic: 'percept.frame',
          provenance: {
            citizen_id: citizenId,
            timestamp: Date.now()
          },
          subentity_id: `${citizenId}_se_core`,
          anchors_top: ['node_1', 'node_2'],
          anchors_peripheral: ['node_3', 'node_4'],
          affect: 0.7,
          novelty: 0.5,
          uncertainty: 0.3,
          goal_match: 0.8
        }
      }));
      console.log(`[MockFramePublisher] Published mock frame for ${citizenId}`);
    }
  };
}
