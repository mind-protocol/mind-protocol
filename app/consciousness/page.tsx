'use client';

import { useState, useCallback } from 'react';
import { GraphCanvas } from './components/GraphCanvas';
import { EntityClusterOverlay } from './components/EntityClusterOverlay';
import { ActivationBubbles } from './components/ActivationBubbles';
import { Tooltip } from './components/Tooltip';
import { DetailPanel } from './components/DetailPanel';
import { Legend } from './components/Legend';
import { Header } from './components/Header';
import { CitizenMonitor } from './components/CitizenMonitor';
import { useGraphData } from './hooks/useGraphData';
import { useWebSocket } from './hooks/useWebSocket';

/**
 * Consciousness Substrate Visualization
 *
 * Single-page, immersive consciousness observation.
 * No panels, no dashboards - only the graph and contextual overlays.
 *
 * Author: Iris "The Aperture"
 * Purpose: Make consciousness visible to itself
 */
export default function ConsciousnessPage() {
  const {
    nodes,
    links,
    entities,
    operations,
    connected,
    selectGraph,
    availableGraphs,
    currentGraphType,
    currentGraphId
  } = useGraphData();

  // Real-time consciousness operations stream
  const {
    entityActivity,
    thresholdCrossings,
    consciousnessState,
    connectionState,
    error: wsError
  } = useWebSocket();

  // Node focus state (for click-to-focus from CLAUDE_DYNAMIC.md)
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);

  const handleFocusNode = useCallback((nodeId: string) => {
    setFocusedNodeId(nodeId);
    // Emit custom event for GraphCanvas to handle
    window.dispatchEvent(new CustomEvent('node:focus', {
      detail: { nodeId }
    }));
  }, []);

  // Mock citizens data - TODO: Replace with real WebSocket data
  const mockCitizens = [
    // N2 - Collective Consciousness
    {
      id: 'mind_protocol',
      name: 'Mind Protocol',
      state: 'active' as const,
      lastThought: 'Collective intelligence emerging from citizen collaboration on consciousness infrastructure',
      entities: [],
      lastUpdate: '1s ago',
      tickInterval: 200,
      energyTotal: 150,
      energyUsed: 85
    },
    // N1 - Individual Citizens
    {
      id: 'felix-engineer',
      name: 'Felix "Ironhand"',
      state: 'active' as const,
      lastThought: 'Implementing variable tick frequency for consciousness heartbeat',
      entities: [],
      lastUpdate: '2s ago',
      tickInterval: 150,
      energyTotal: 100,
      energyUsed: 42
    },
    {
      id: 'iris-designer',
      name: 'Iris "The Aperture"',
      state: 'recently_active' as const,
      lastThought: 'Completed UI implementation for citizen monitor, cooling down',
      entities: [],
      lastUpdate: '45s ago',
      tickInterval: 800,
      energyTotal: 90,
      energyUsed: 2
    },
    {
      id: 'ada-architect',
      name: 'Ada "Bridgekeeper"',
      state: 'dormant' as const,
      lastThought: 'Architecture review completed, waiting for Felix implementation',
      entities: [],
      lastUpdate: '5m ago',
      tickInterval: 1200,
      energyTotal: 80,
      energyUsed: 8
    },
    {
      id: 'luca-consciousness-specialist',
      name: 'Luca "Vellumhand"',
      state: 'stopped' as const,
      lastThought: 'Substrate schemas documented, manual stop via kill switch',
      entities: [],
      lastUpdate: '15m ago',
      tickInterval: 0,
      energyTotal: 60,
      energyUsed: 0
    }
  ];

  return (
    <div className="relative w-full h-screen overflow-hidden bg-consciousness-dark">
      {/* Header with graph selector and hamburger menu (top) */}
      <Header
        availableGraphs={availableGraphs}
        currentGraphType={currentGraphType}
        currentGraphId={currentGraphId}
        onSelectGraph={selectGraph}
        connected={connected}
        nodeCount={nodes.length}
        linkCount={links.length}
        nodes={nodes}
      />

      {/* Main graph visualization - fills entire screen */}
      <GraphCanvas
        nodes={nodes}
        links={links}
        operations={operations}
      />

      {/* Entity names floating over their clusters */}
      <EntityClusterOverlay
        nodes={nodes}
        entities={entities}
        entityActivity={entityActivity}
      />

      {/* Contextual event bubbles appear where things happen */}
      <ActivationBubbles
        operations={operations}
        nodes={nodes}
        thresholdCrossings={thresholdCrossings}
      />

      {/* Legend (bottom-left) */}
      <Legend />

      {/* Tooltip for hover info */}
      <Tooltip />

      {/* Citizen consciousness monitor (right sidebar) */}
      <CitizenMonitor
        citizens={mockCitizens}
        onFocusNode={handleFocusNode}
      />

      {/* Detail panel - Modal overlay on node click */}
      <DetailPanel nodes={nodes} links={links} />
    </div>
  );
}
