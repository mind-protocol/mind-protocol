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

import { useEffect, useState, useCallback, useRef, useMemo } from 'react';

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
  nodes: Map<string, { id: string; name?: string; type?: string }>;
  links: Map<string, { id: string; source: string; target: string; type: string; weight?: number; properties?: any }>; // PATCH 3: Added missing links property
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
  // PATCH 3: Map store + rAF throttle (foundational refactor)
  // Store graphs in ref (doesn't trigger re-renders on every message)
  const graphsRef = useRef<Map<GraphId, HierarchySnapshot>>(new Map());

  // Frame counter for controlled re-renders (only updates on rAF flush)
  const [frame, setFrame] = useState(0);

  // rAF request ID for throttling
  const rafRef = useRef<number | null>(null);

  // Schedule a single re-render on next animation frame (prevents 60+ renders/sec)
  const scheduleFlush = useCallback(() => {
    if (rafRef.current !== null) return; // Already scheduled
    rafRef.current = requestAnimationFrame(() => {
      rafRef.current = null;
      setFrame(f => f + 1); // Trigger ONE re-render per frame
    });
  }, []);

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

  // Use ref for currentGraphId to avoid recreating ensureGraph on every change
  const currentGraphIdRef = useRef<GraphId | null>(null);

  // Sync ref with state
  useEffect(() => {
    currentGraphIdRef.current = currentGraphId;
  }, [currentGraphId]);

  // PATCH 3 FIX: Helper to create placeholder subentity with all optional fields
  const createPlaceholderSubEntity = useCallback((id: string): SubEntityInfo => ({
    id,
    members: new Set<string>(),
    slug: undefined,
    name: undefined,
    active: undefined,
    anchorsTop: undefined,
    anchorsPeripheral: undefined,
    affect: undefined,
    novelty: undefined,
    uncertainty: undefined,
    goalFit: undefined
  }), []);

  // PATCH 3: Helper to get or create graph snapshot (uses ref directly)
  // Also auto-selects this graph if current selection is empty or null
  const ensureGraph = useCallback((graphId: GraphId) => {
    const graphsMap = graphsRef.current;

    if (!graphsMap.has(graphId)) {
      graphsMap.set(graphId, {
        subentities: {},
        nodes: new Map(),
        links: new Map(),
        lastUpdate: Date.now()
      });
    }

    // Auto-switch to active graph if nothing selected OR current graph is empty
    // Use ref to avoid dependency on currentGraphId
    if (currentGraphIdRef.current === null) {
      console.log('[useGraphStream] 🎯 Auto-selecting first active graph:', graphId);
      setCurrentGraphId(graphId);
    } else {
      const current = graphsMap.get(currentGraphIdRef.current);
      const currentNodeCount = current ? current.nodes.size : 0;
      if (current && currentNodeCount === 0) {
        const incomingNodeCount = graphsMap.get(graphId)?.nodes.size ?? 0;
        if (incomingNodeCount > 0) {
          console.log('[useGraphStream] 🎯 Auto-switching from empty graph to active graph:', {
            from: currentGraphIdRef.current,
            to: graphId,
            incomingNodeCount
          });
          setCurrentGraphId(graphId);
        }
      }
    }

    return graphsMap.get(graphId)!;
  }, []); // No dependencies - uses ref instead

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let isCleaningUp = false;

    const connect = () => {
      if (isCleaningUp) return; // Prevent reconnect during cleanup

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
              'subentity.*',  // Added: Includes subentity.snapshot events
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

            // Log ALL messages (temporary diagnostic)
            if (eventType !== 'ping' && eventType !== 'pong') {
              console.log('[useGraphStream] 📨 Message received:', {
                type: eventType,
                hasCitizenId: !!msg.provenance?.citizen_id,
                citizenId: msg.provenance?.citizen_id,
                hasPayload: !!msg.payload,
                // Show actual payload for snapshot events (debugging graph display issue)
                payload: eventType === 'snapshot.chunk@1.0' || eventType === 'subentity.snapshot'
                  ? msg.payload
                  : undefined
              });
            }

            if (eventType === 'subscribe.ack@1.0' || eventType === 'subscribe.ack') {
              const ackTopics = msg.payload?.topics ?? msg.topics ?? [];
              const citizenId = msg.provenance?.citizen_id;
              console.log('[useGraphStream] Subscribe ACK received:', {
                connectionId: msg.payload?.connection_id ?? msg.connection_id,
                citizenId,
                topics: ackTopics
              });

              return;
            }

            if (eventType === 'snapshot.end@1.0') {
              console.log('[useGraphStream] 📦 snapshot.end@1.0 received', { graphId: msg.provenance?.citizen_id });
              scheduleFlush(); // Ensure a flush after the full snapshot is received
              return;
            }

            if (eventType === 'ping' || eventType === 'pong') {
              return;
            }

            // Special case: snapshot.chunk@1.0 doesn't follow normative envelope format
            // Also allow raw link events (MEMBER_OF, ACTIVATES, INHIBITS) - backward compatibility
            if (eventType === 'snapshot.chunk@1.0') {
              console.log('[useGraphStream] 📦 snapshot.chunk@1.0 received', {
                hasPayload: !!msg.payload,
                payloadKeys: msg.payload ? Object.keys(msg.payload) : [],
                nodeCount: msg.payload?.nodes?.length ?? 0,
                linkCount: msg.payload?.links?.length ?? 0,
                subentityCount: msg.payload?.subentities?.length ?? 0,
                sampleNode: msg.payload?.nodes?.[0],
                sampleLink: msg.payload?.links?.[0],
                sampleSubentity: msg.payload?.subentities?.[0]
              });
              // Continue to switch statement for processing
            } else if (eventType === 'MEMBER_OF' || eventType === 'ACTIVATES' || eventType === 'INHIBITS') {
              // Raw link events - skip normative validation (backward compatibility)
              // Continue to switch statement for processing
            } else {
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
            }

            // Derive graphId from provenance (canonical format for normative events)
            // Backend sends full citizen_id (e.g., "consciousness-infrastructure_mind-protocol_felix")
            // Don't add prefixes - use citizen_id/org_id directly
            let graphId: GraphId;
            if (eventType === 'snapshot.chunk@1.0') {
              graphId = msg.provenance?.citizen_id
                ? msg.provenance.citizen_id
                : msg.payload?.graph_id ?? 'default';
            } else {
              graphId = msg.provenance.scope === 'personal' && msg.provenance.citizen_id
                ? msg.provenance.citizen_id
                : msg.provenance.scope === 'organizational' && msg.provenance.org_id
                  ? msg.provenance.org_id
                  : 'unknown';
            }

            if (graphId === 'unknown') {
              console.warn('[useGraphStream] No valid scope in provenance:', msg.provenance);
              return;
            }

            // PATCH 3: Direct ref mutation instead of state update
            const snap = ensureGraph(graphId);

            // Handle event types (normative vocabulary: 'type' not 'topic')
            switch (eventType) {
                case 'snapshot.begin@1.0': {
                  const graphId = msg.provenance?.citizen_id;
                  if (!graphId) break;

                  console.log(`[useGraphStream] 🎬 snapshot.begin@1.0 received for ${graphId}`);
                  const snap = ensureGraph(graphId);
                  // Clear existing data for a fresh snapshot
                  snap.nodes = new Map();
                  snap.links = new Map();
                  snap.subentities = {}; // Subentities remain a Record for now
                  snap.lastUpdate = Date.now();

                  // Auto-select this graph if nothing is selected
                  if (!currentGraphId) {
                    setCurrentGraphId(graphId);
                  }
                  scheduleFlush();
                  break;
                }
                case 'snapshot.begin@1.0': {
                  const payload = msg.payload ?? {};
                  const citizenId = payload.citizen_id;
                  if (citizenId) {
                    console.log(`[useGraphStream] 📦 snapshot.begin@1.0 received for ${citizenId}. Clearing existing graph data.`);
                    graphsRef.current.set(citizenId, {
                      subentities: {},
                      nodes: new Map(),
                      links: new Map(),
                      lastUpdate: Date.now()
                    });
                    scheduleFlush();
                  }
                  break;
                }
                case 'mode.snapshot':  // Backend sends mode.snapshot events (treat as snapshot)
                case 'snapshot.chunk@1.0': {
                  const payload = msg.payload ?? {};
                  const nodes = Array.isArray(payload.nodes) ? payload.nodes : [];
                  const links = Array.isArray(payload.links) ? payload.links : [];
                  const subentities = Array.isArray(payload.subentities) ? payload.subentities : [];

                  console.log(`[useGraphStream] 📥 ${eventType} received:`, {
                    graphId,
                    nodeCount: nodes.length,
                    linkCount: links.length,
                    subentityCount: subentities.length,
                    payloadKeys: Object.keys(payload),
                    rawPayload: payload
                  });

                  // Set currentGraphId if not already set (allows snapshot to establish base graph)
                  if (!currentGraphId) {
                    setCurrentGraphId(graphId);
                  }

                  nodes.forEach((node: any) => {
                    if (!node) return;
                    const nodeId = node.id ?? node.node_id;
                    if (!nodeId) return;
                    const properties = node.properties ?? {};
                    snap.nodes.set(nodeId, {
                      id: nodeId,
                      name: node.name ?? properties.name,
                      type: node.type ?? node.node_type ?? properties.node_type
                    });
                  });

                  links.forEach((link: any) => {
                    if (!link) return;
                    const source = link.source ?? link.source_id;
                    const target = link.target ?? link.target_id;
                    if (!source || !target) return;
                    const linkType = link.type ?? link.link_type;
                    const linkId = link.id ?? `${source}->${target}:${linkType}`;

                    // Store ALL links in snap.links (not just MEMBER_OF)
                    snap.links.set(linkId, {
                      id: linkId,
                      source,
                      target,
                      type: linkType,
                      weight: link.weight,
                      properties: link.properties ?? {}
                    });

                    // ALSO handle MEMBER_OF for subentity membership
                    if (linkType === 'MEMBER_OF') {
                      if (!snap.subentities[target]) {
                        snap.subentities[target] = createPlaceholderSubEntity(target);
                      }
                      snap.subentities[target].members.add(source);
                    }
                  });

                  subentities.forEach((se: any) => {
                    if (!se) return;
                    const subId = se.id ?? se.subentity_id;
                    if (!subId) return;
                    const members = Array.isArray(se.members)
                      ? se.members
                      : Array.isArray(se.member_ids)
                        ? se.member_ids
                        : [];
                    const existing = snap.subentities[subId] ?? createPlaceholderSubEntity(subId);
                    const nextMembers = new Set(existing.members);
                    members.forEach((member: any) => {
                      if (typeof member === 'string') {
                        nextMembers.add(member);
                      } else if (member?.id) {
                        nextMembers.add(member.id);
                      }
                    });
                    snap.subentities[subId] = {
                      id: subId,
                      slug: se.slug ?? se.role_or_topic ?? existing.slug,
                      name: se.name ?? existing.name ?? se.display_name,
                      members: nextMembers
                    };
                  });

                  snap.lastUpdate = Date.now();

                  // DEBUG: Verify snapshot was stored
                  console.log('[useGraphStream] 🔍 After snapshot processing:', {
                    graphId,
                    snapNodeCount: snap.nodes.size,
                    snapLinkCount: snap.links.size,
                    graphsMapSize: graphsRef.current.size,
                    graphsMapKeys: Array.from(graphsRef.current.keys()),
                    currentGraphId
                  });

                  scheduleFlush(); // CRITICAL: Flush snapshot to React (no global flush for snapshots)
                  break;
                }
                case 'snapshot.end@1.0': {
                  const payload = msg.payload ?? {};
                  const citizenId = payload.citizen_id;
                  if (citizenId) {
                    console.log(`[useGraphStream] 📦 snapshot.end@1.0 received for ${citizenId}. Snapshot complete.`);
                    scheduleFlush();
                  }
                  break;
                }

                case 'snapshot.end@1.0': {
                  const graphId = msg.provenance?.citizen_id;
                  if (!graphId) break;
                  console.log(`[useGraphStream] ✅ snapshot.end@1.0 received for ${graphId}`);
                  // No specific action needed here other than logging, as chunks have already updated the graph.
                  // The scheduleFlush() from the last chunk or begin event will handle the render.
                  break;
                }

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
                    snap.nodes.set(nodeId, {
                      id: nodeId,
                      name: properties.name,
                      type: nodeType
                    });
                  }
                  snap.lastUpdate = Date.now();
                  scheduleFlush(); // Flush when graph data changes
                  break;
                }

                case 'subentity.activation': {
                  // Activation telemetry is consumed by other rendering layers.
                  // Touch lastUpdate so subscribers know we processed the event.
                  snap.lastUpdate = Date.now();
                  scheduleFlush(); // Flush when graph data changes
                  break;
                }

                case 'graph.delta.node.delete': {
                  const payload = msg.payload ?? {};
                  const nodeId = payload.node_id ?? payload.id;
                  if (!nodeId) {
                    console.warn('[useGraphStream] graph.delta.node.delete missing payload.node_id', payload);
                    break;
                  }
                  if (snap.nodes.has(nodeId)) {
                    snap.nodes.delete(nodeId);
                  }
                  Object.values(snap.subentities).forEach(sub => sub.members.delete(nodeId));
                  snap.lastUpdate = Date.now();
                  scheduleFlush(); // Flush when graph data changes
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
                      snap.subentities[target] = createPlaceholderSubEntity(target);
                    }
                    snap.subentities[target].members.add(source);
                  } else {
                    // Create placeholder nodes if they don't exist yet (Patch 4)
                    if (!snap.nodes.has(source)) {
                      snap.nodes.set(source, {
                        id: source,
                        name: source, // Use ID as placeholder name
                        type: 'placeholder' // Mark as placeholder
                      });
                    }
                    if (!snap.nodes.has(target)) {
                      snap.nodes.set(target, {
                        id: target,
                        name: target, // Use ID as placeholder name
                        type: 'placeholder' // Mark as placeholder
                      });
                    }

                    // Store regular links (ENABLES, RELATES_TO, etc.)
                    const linkId = payload.id || `${source}-${target}`;
                    snap.links.set(linkId, {
                      id: linkId,
                      source,
                      target,
                      type: linkType,
                      weight: payload.weight,
                      properties: payload.properties
                    });
                  }
                  snap.lastUpdate = Date.now();
                  scheduleFlush(); // Flush when graph data changes
                  break;
                }

                case 'graph.delta.link.delete': {
                  const payload = msg.payload ?? {};
                  const linkType = payload.type ?? payload.link_type;
                  const source = payload.source ?? payload.source_id;
                  const target = payload.target ?? payload.target_id;
                  if (linkType === 'MEMBER_OF' && source && target) {
                    const subentity = snap.subentities[target];
                    if (subentity) {
                      subentity.members.delete(source);
                    }
                  }
                  snap.lastUpdate = Date.now();
                  scheduleFlush(); // Flush when graph data changes
                  break;
                }

                case 'MEMBER_OF':
                case 'ACTIVATES':
                case 'INHIBITS': {
                  // Handle raw link events (backward compatibility format)
                  // These arrive with type = link type (MEMBER_OF, ACTIVATES, etc.)
                  // Extract link data from root-level fields or payload
                  const source = msg.source ?? msg.payload?.source;
                  const target = msg.target ?? msg.payload?.target;
                  const linkType = eventType; // MEMBER_OF, ACTIVATES, INHIBITS

                  if (!source || !target) {
                    console.warn(`[useGraphStream] ${linkType} event missing source or target:`, msg);
                    break;
                  }

                  console.log(`[useGraphStream] 🔗 ${linkType} link received:`, { source, target });

                  if (linkType === 'MEMBER_OF') {
                    // Ensure target SubEntity exists
                    if (!snap.subentities[target]) {
                      snap.subentities[target] = createPlaceholderSubEntity(target);
                    }
                    snap.subentities[target].members.add(source);
                  } else {
                    // Create placeholder nodes if they don't exist yet
                    if (!snap.nodes.has(source)) {
                      snap.nodes.set(source, {
                        id: source,
                        name: source,
                        type: 'placeholder'
                      });
                    }
                    if (!snap.nodes.has(target)) {
                      snap.nodes.set(target, {
                        id: target,
                        name: target,
                        type: 'placeholder'
                      });
                    }
                    // Store regular links (ENABLES, RELATES_TO, etc.)
                    const linkId = msg.id || `${source}-${target}`;
                    snap.links.set(linkId, {
                      id: linkId,
                      source,
                      target,
                      type: linkType,
                      weight: msg.weight,
                      properties: msg.properties
                    });
                  }
                  snap.lastUpdate = Date.now();
                  scheduleFlush(); // Flush when graph data changes
                  break;
                }

                case 'graph.delta.subentity.upsert': {
                  const payload = msg.payload ?? {};
                  const subentity = payload.subentity ?? payload;
                  const subId = subentity?.id ?? payload.subentity_id;
                  if (!subId) {
                    console.warn('[useGraphStream] graph.delta.subentity.upsert missing id', payload);
                    break;
                  }
                  const existing = snap.subentities[subId] ?? { id: subId, members: new Set<string>() };
                  const members = Array.isArray(subentity.members)
                    ? subentity.members
                    : Array.isArray(subentity.member_ids)
                      ? subentity.member_ids
                      : [];
                  const nextMembers = new Set(existing.members);
                  members.forEach((member: any) => {
                    if (typeof member === 'string') {
                      nextMembers.add(member);
                    } else if (member?.id) {
                      nextMembers.add(member.id);
                    }
                  });
                  snap.subentities[subId] = {
                    id: subId,
                    slug: subentity.slug ?? subentity.role_or_topic ?? existing.slug,
                    name: subentity.name ?? subentity.display_name ?? existing.name,
                    members: nextMembers,
                    active: subentity.active ?? existing.active
                  };
                  snap.lastUpdate = Date.now();
                  scheduleFlush(); // Flush when graph data changes
                  break;
                }

                case 'graph.delta.subentity.delete': {
                  const payload = msg.payload ?? {};
                  const subId = payload.subentity_id ?? payload.id;
                  if (!subId) {
                    console.warn('[useGraphStream] graph.delta.subentity.delete missing id', payload);
                    break;
                  }
                  delete snap.subentities[subId];
                  snap.lastUpdate = Date.now();
                  scheduleFlush(); // Flush when graph data changes
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
                      snap.subentities[seId] = createPlaceholderSubEntity(seId);
                    }
                    snap.subentities[seId].active = true;
                  });

                  snap.lastUpdate = Date.now();


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

            // REMOVED: scheduleFlush() on every message causes 60fps flicker
            // Now only called when graph data actually changes
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
          // But don't reconnect if we're cleaning up
          if (!isCleaningUp) {
            reconnectTimeout = setTimeout(() => {
              connect();
            }, 5000);
          }
        };
      } catch (err) {
        // Connection failures are expected when backend is down
        setError('Membrane bus unavailable');
        setConnected(false);
      }
    };

    connect();

    return () => {
      isCleaningUp = true;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws) {
        ws.close();
        ws = null;
      }
    };
  }, [ensureGraph]); // ANTI-RECONNECT: Removed onGraphIdChange - not used in WebSocket code, only in ensureGraph

  // PATCH 3: Convert ref to state for rendering (only rebuilds on rAF flush)
  // This useMemo runs once per animation frame when `frame` changes
  const graphs = useMemo(() => {
    const snapshot = new Map(graphsRef.current);

    // DEBUG: Log what React is seeing
    console.log('[useGraphStream] 📊 useMemo rebuilding graphs:', {
      frame,
      graphCount: snapshot.size,
      graphKeys: Array.from(snapshot.keys()),
      nodeCountPerGraph: Array.from(snapshot.entries()).map(([key, g]) =>
        [key, Object.keys(g.nodes || {}).length]
      )
    });

    return snapshot; // Return snapshot of current graphs
  }, [frame]); // Only re-compute when frame changes (triggered by scheduleFlush)

  return {
    graphs,
    currentGraphId,
    setCurrentGraphId,
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
