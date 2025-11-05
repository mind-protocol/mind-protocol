'use client';

// Force rebuild: 2025-11-04 21:17 UTC
import { useState, useCallback, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Tooltip } from './components/Tooltip';
import { DetailPanel } from './components/DetailPanel';
import { Legend } from './components/Legend';
import { Header } from './components/Header';
import { LeftSidebarMenu } from './components/LeftSidebarMenu';
import { ChatPanel } from './components/ChatPanel';
import { ForgedIdentityViewer } from './components/ForgedIdentityViewer';
import { GraphChatInterface } from './components/GraphChatInterface';
import { useWebSocket } from './hooks/useWebSocket';
import { useGraphStream } from './hooks/useGraphStream';
import type {
  Node,
  Link,
  Subentity,
  Operation,
  GraphOption
} from './hooks/useGraphData';
import { WebSocketState } from './hooks/websocket-types';
import GraphDebugBadge from './components/GraphDebugBadge';
import { membraneInject } from '@/app/lib/membrane';

const GraphPixi = dynamic(() => import('./components/GraphPixi'), { ssr: false });
const LintPanel = dynamic(() => import('./components/LintPanel'), { ssr: false });
const SubEntityGraphView = dynamic(() => import('@/app/consciousness/components/SubEntityGraphView').then(mod => ({ default: mod.SubEntityGraphView })), { ssr: false });
const SubEntityClusterOverlay = dynamic(() => import('@/app/consciousness/components/SubEntityClusterOverlay').then(mod => ({ default: mod.SubEntityClusterOverlay })), { ssr: false });
const EnergyFlowParticles = dynamic(() => import('@/app/consciousness/components/EnergyFlowParticles').then(mod => ({ default: mod.EnergyFlowParticles })), { ssr: false });
const ActivationBubbles = dynamic(() => import('@/app/consciousness/components/ActivationBubbles').then(mod => ({ default: mod.ActivationBubbles })), { ssr: false });


const MAX_OPERATIONS = 50;

const toTitleCase = (value: string) =>
  value.replace(/[-_]/g, ' ').replace(/\b\w/g, (char: string) => char.toUpperCase());

type GraphType = 'citizen' | 'organization' | 'ecosystem';

export default function ConsciousnessPage() {
  const {
    subentityActivity,
    thresholdCrossings,
    v2State,
    emotionState,
    weightLearningEvents,
    strideSelectionEvents,
    phenomenologyMismatchEvents,
    phenomenologyHealthEvents,
    forgedIdentityFrames,
    forgedIdentityMetrics,
    connectionState,
    error: wsError,
    hierarchySnapshot,
    economyOverlays
  } = useWebSocket();

  // Membrane-first graph stream: derives currentGraphId from event provenance
  const graphStream = useGraphStream();

  const [nodeOverlays, setNodeOverlays] = useState<Record<string, Partial<Node>>>({});
  const [operations, setOperations] = useState<Operation[]>([]);
  const [entityToEntity, setEntityToEntity] = useState<Record<string, number>>({});
  const [expandedEntities, setExpandedEntities] = useState<Set<string>>(new Set());
  const [showForgedIdentityViewer, setShowForgedIdentityViewer] = useState(false);
  const [graphMetadata, setGraphMetadata] = useState<Record<string, GraphOption & { graphType: GraphType; aliases: string[] }>>({});

  // Use currentGraphId from membrane event stream (derived from provenance, not hardcoded)
  const currentGraphId = graphStream.currentGraphId;
  const setCurrentGraphId = graphStream.setCurrentGraphId;
  const [currentGraphType, setCurrentGraphType] = useState<GraphType>('citizen');
  const [lastProcessedThreshold, setLastProcessedThreshold] = useState<number>(-1);
  const [lastProcessedActivity, setLastProcessedActivity] = useState<number>(-1);

  const currentGraph = useMemo(() => {
    // If no graph selected, use first available graph (fallback)
    const selectedId = currentGraphId || graphStream.graphs.keys().next().value;
    if (!selectedId) return null;
    return graphStream.graphs.get(selectedId) || null;
  }, [graphStream.graphs, currentGraphId]);

  const nodes = useMemo<Node[]>(() => {
    if (!currentGraph) return [];
    // currentGraph.nodes is a Map, not an object - use Array.from()
    return Array.from(currentGraph.nodes.values()).map(node => ({
      id: node.id,
      node_id: node.id,
      name: node.name,
      type: node.type,
      // Add other properties as needed, potentially from nodeOverlays
    }));
  }, [currentGraph]);

  const links = useMemo<Link[]>(() => {
    if (!currentGraph) return [];
    // currentGraph.links is a Map, not an object - use Array.from()
    return Array.from(currentGraph.links.values()).map(link => ({
      id: link.id,
      source: link.source,
      target: link.target,
      type: link.type,
      weight: link.weight,
      properties: link.properties,
    }));
  }, [currentGraph]);

  const subentities = useMemo<Subentity[]>(() => {
    if (!currentGraph) return [];
    return Object.values(currentGraph.subentities).map((sub) => ({
      subentity_id: sub.id,
      name: sub.name ?? sub.slug ?? sub.id,
      kind: 'SubEntity',
      energy: 0,
      threshold: 0,
      activation_level: sub.active ? '1.0' : '0.0',
      member_count: sub.members.size,
      members: Array.from(sub.members),
      quality: 0,
      stability: '0',
      properties: {}
    }));
  }, [currentGraph]);

  const strideEvents = emotionState.recentStrides;

  const updateNodeFromEvent = useCallback((nodeId: string, updates: Partial<Node>) => {
    setNodeOverlays(prev => {
      const next = { ...prev };
      const existing = next[nodeId] ?? {};
      next[nodeId] = { ...existing, ...updates };
      return next;
    });
  }, []);

  const addOperation = useCallback((operation: Operation) => {
    setOperations(prev => [operation, ...prev].slice(0, MAX_OPERATIONS));
  }, []);

  const updateEntityToEntityFlow = useCallback((sourceEntityId: string, targetEntityId: string, flowCount: number) => {
    setEntityToEntity(prev => {
      const next: Record<string, number> = {};

      for (const [key, value] of Object.entries(prev)) {
        const decayed = value * 0.95;
        if (decayed > 0.1) {
          next[key] = decayed;
        }
      }

      const edgeKey = `${sourceEntityId}->${targetEntityId}`;
      next[edgeKey] = (next[edgeKey] || 0) + flowCount;
      return next;
    });
  }, []);

  useEffect(() => {
    if (!hierarchySnapshot) return;

    const citizens: GraphOption[] = (hierarchySnapshot.citizens ?? []).map((citizen) => ({
      id: citizen.id,
      name: citizen.label ?? toTitleCase(citizen.id),
      ecosystem: hierarchySnapshot.ecosystems?.[0] ?? 'primary',
      organization: hierarchySnapshot.org,
      citizen: citizen.id,
      slug: citizen.id,
      legacyId: `citizen_${citizen.id.replace(/-/g, '_')}`
    }));

    const organizations: GraphOption[] = hierarchySnapshot.org
      ? [{
          id: hierarchySnapshot.org,
          name: toTitleCase(hierarchySnapshot.org),
          ecosystem: hierarchySnapshot.ecosystems?.[0] ?? 'primary',
          organization: hierarchySnapshot.org,
          slug: hierarchySnapshot.org
        }]
      : [];

    const ecosystems: GraphOption[] = (hierarchySnapshot.ecosystems ?? []).map((ecosystem) => ({
      id: ecosystem,
      name: toTitleCase(ecosystem),
      ecosystem,
      slug: ecosystem
    }));

    const metadata: Record<string, GraphOption & { graphType: GraphType; aliases: string[] }> = {};
    const register = (option: GraphOption, graphType: GraphType) => {
      const aliases = new Set<string>();
      aliases.add(option.id.toLowerCase());
      if (option.slug) aliases.add(option.slug.toLowerCase());
      if (option.citizen) aliases.add(option.citizen.toLowerCase());
      if (option.organization) aliases.add(option.organization.toLowerCase());
      if (option.legacyId) aliases.add(option.legacyId.toLowerCase());
      metadata[option.id] = { ...option, graphType, aliases: Array.from(aliases) };
    };

    citizens.forEach(option => register(option, 'citizen'));
    organizations.forEach(option => register(option, 'organization'));
    ecosystems.forEach(option => register(option, 'ecosystem'));
    setGraphMetadata(metadata);

    // Membrane-first: currentGraphId is derived from event provenance automatically
    // No fallback logic needed - we trust the event stream
  }, [hierarchySnapshot]);

  useEffect(() => {
    for (let i = lastProcessedThreshold + 1; i < thresholdCrossings.length; i++) {
      const crossing = thresholdCrossings[i];

      updateNodeFromEvent(crossing.node_id, {
        entity_activations: {
          [crossing.subentity_id]: {
            energy: crossing.subentity_activity,
            last_activated: Date.now()
          }
        },
        last_active: Date.now()
      });

      addOperation({
        type: 'threshold_crossing',
        node_id: crossing.node_id,
        subentity_id: crossing.subentity_id,
        timestamp: Date.now(),
        data: {
          direction: crossing.direction,
          threshold: crossing.threshold
        }
      });
    }

    if (thresholdCrossings.length > 0) {
      setLastProcessedThreshold(thresholdCrossings.length - 1);
    }
  }, [thresholdCrossings, updateNodeFromEvent, addOperation, lastProcessedThreshold]);

  useEffect(() => {
    for (let i = lastProcessedActivity + 1; i < subentityActivity.length; i++) {
      const activity = subentityActivity[i];

      updateNodeFromEvent(activity.current_node, {
        last_traversed_by: activity.subentity_id,
        last_active: Date.now(),
        traversal_count: 1
      });

      addOperation({
        type: 'subentity_activity',
        node_id: activity.current_node,
        subentity_id: activity.subentity_id,
        timestamp: Date.now(),
        data: {
          need_type: activity.need_type,
          energy_used: activity.energy_used,
          energy_budget: activity.energy_budget
        }
      });
    }

    if (subentityActivity.length > 0) {
      setLastProcessedActivity(subentityActivity.length - 1);
    }
  }, [subentityActivity, updateNodeFromEvent, addOperation, lastProcessedActivity]);

  useEffect(() => {
    v2State.linkFlows.forEach((flowCount, linkId) => {
      if (flowCount <= 0) return;

      const link = links.find(l => l.id === linkId);
      if (!link) return;

      const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
      const targetId = typeof link.target === 'string' ? link.target : link.target.id;

      const sourceNode = nodes.find(n => (n.id || n.node_id) === sourceId);
      const targetNode = nodes.find(n => (n.id || n.node_id) === targetId);

      if (!sourceNode || !targetNode) return;

      updateEntityToEntityFlow(sourceNode.id, targetNode.id, flowCount);
    });
  }, [v2State.linkFlows, links, nodes, updateEntityToEntityFlow]);

  const handleFocusNode = useCallback((nodeId: string) => {
    window.dispatchEvent(new CustomEvent('node:focus', { detail: { nodeId } }));
  }, []);

  const handleSelectCitizen = useCallback((citizenId: string) => {
    // Switch to the selected citizen's graph
    // citizenId should be full hierarchical name (e.g., "mind-protocol_felix")
    setCurrentGraphId(citizenId);
    // Also emit membrane event for telemetry
    membraneInject("ui.select.citizen", { citizen_id: citizenId }, { ts: Date.now() });
  }, [setCurrentGraphId]);

  const currentGraphLabel = useMemo(() => {
    if (!currentGraphId) return '';
    const meta = graphMetadata[currentGraphId];
    if (!meta) return toTitleCase(currentGraphId);
    if (meta.graphType === 'citizen' && meta.organization) {
      return `${toTitleCase(meta.organization)} / ${meta.name}`;
    }
    return meta.name;
  }, [currentGraphId, graphMetadata]);

  const activeChatCitizenId = useMemo(() => {
    if (!currentGraphId) return undefined;
    const meta = graphMetadata[currentGraphId];
    if (!meta) return undefined;
    if (meta.graphType === 'citizen' && meta.citizen) {
      return meta.citizen.replace(/-/g, '_');
    }
    if (meta.graphType === 'organization' && meta.organization) {
      return meta.organization.replace(/-/g, '_');
    }
    return undefined;
  }, [currentGraphId, graphMetadata]);

  const toggleEntity = useCallback((entityId: string) => {
    setExpandedEntities(prev => {
      const next = new Set(prev);
      if (next.has(entityId)) {
        next.delete(entityId);
      } else {
        next.add(entityId);
      }
      return next;
    });
  }, []);

  const collapseAll = useCallback(() => {
    setExpandedEntities(new Set());
  }, []);

  return (
    <div className="relative w-full h-screen overflow-hidden bg-observatory-dark">
      <Header
        currentGraphId={currentGraphId}
        currentGraphLabel={currentGraphLabel}
        nodeCount={nodes.length}
        linkCount={links.length}
        nodes={nodes}
        onToggleForgedIdentity={() => setShowForgedIdentityViewer(!showForgedIdentityViewer)}
        showForgedIdentityViewer={showForgedIdentityViewer}
      />

      {wsError && (
        <div
          data-testid="error-overlay"
          className="absolute top-20 left-1/2 -translate-x-1/2 z-50 max-w-2xl px-6 py-4 bg-red-900/90 border border-red-500/50 rounded-lg backdrop-blur-sm"
        >
          <h2 className="text-red-200 font-semibold text-lg">WebSocket Error</h2>
          <p className="text-sm text-red-100 mt-2">{wsError}</p>
        </div>
      )}

      <Tooltip />
      <Legend />

      <LeftSidebarMenu
        v2State={v2State}
        strideSelectionEvents={strideSelectionEvents}
        strideEvents={strideEvents}
        weightLearningEvents={weightLearningEvents}
        phenomenologyMismatchEvents={phenomenologyMismatchEvents}
        phenomenologyHealthEvents={phenomenologyHealthEvents}
        currentGraphId={currentGraphId}
        emergenceState={graphStream.emergence}
        topologyState={graphStream.topology}
      />

      <ChatPanel activeCitizenId={activeChatCitizenId} onSelectCitizen={handleSelectCitizen} />

      <SubEntityGraphView
        nodes={nodes}
        links={links}
        operations={operations}
        subentities={subentities}
        workingMemory={v2State.workingMemory}
        linkFlows={v2State.linkFlows}
        recentFlips={v2State.recentFlips}
        expandedSubEntities={expandedEntities}
        toggleSubEntity={toggleEntity}
        subentityFlows={entityToEntity}
      />

      <GraphPixi />

      <SubEntityClusterOverlay
        nodes={nodes}
        subentities={subentities}
        subentityActivity={subentityActivity}
      />

      <EnergyFlowParticles nodes={nodes} subentityActivity={subentityActivity} />

      <ActivationBubbles
        operations={operations}
        nodes={nodes}
      />

      <DetailPanel nodes={nodes} links={links} />

      <GraphChatInterface nodes={nodes} links={links} />

      {showForgedIdentityViewer && (
        <ForgedIdentityViewer
          frames={forgedIdentityFrames}
          metrics={forgedIdentityMetrics}
        />
      )}
      <GraphDebugBadge />
      <LintPanel />
    </div>
  );
}
