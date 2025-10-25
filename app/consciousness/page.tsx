'use client';

import { useState, useCallback, useEffect, useMemo } from 'react';
import { PixiCanvas } from './components/PixiCanvas';
import { EntityGraphView } from './components/EntityGraphView';
import { EntityClusterOverlay } from './components/EntityClusterOverlay';
import { EnergyFlowParticles } from './components/EnergyFlowParticles';
import { ActivationBubbles } from './components/ActivationBubbles';
import { Tooltip } from './components/Tooltip';
import { DetailPanel } from './components/DetailPanel';
import { Legend } from './components/Legend';
import { Header } from './components/Header';
import { CitizenMonitor } from './components/CitizenMonitor';
import { LeftSidebarMenu } from './components/LeftSidebarMenu';
import { useGraphData } from './hooks/useGraphData';
import { useWebSocket } from './hooks/useWebSocket';
import { useCitizens } from './hooks/useCitizens';

/**
 * Consciousness Substrate Visualization
 *
 * Single-page, immersive consciousness observation.
 * No panels, no dashboards - only the graph and contextual overlays.
 *
 * Architecture:
 * - Initial graph load: REST API (/api/graph/{type}/{id}) - Felix
 * - Real-time updates: WebSocket events (ws://localhost:8000/api/ws) - Iris
 * - Event integration: This component wires WebSocket events to graph state updates
 *
 * Author: Iris "The Aperture"
 * Purpose: Make consciousness visible to itself
 */
export default function ConsciousnessPage() {
  // Graph state management (REST-based initial load)
  const {
    nodes,
    links,
    subentities,
    operations,
    loading,
    error,
    selectGraph,
    availableGraphs,
    currentGraphType,
    currentGraphId,
    updateNodeFromEvent,
    updateLinkFromEvent,
    addOperation
  } = useGraphData();

  // Debug: Log graph data when it changes
  useEffect(() => {
    console.log('[ConsciousnessPage] Graph data updated - nodes:', nodes.length, 'links:', links.length, 'currentGraphId:', currentGraphId);
  }, [nodes.length, links.length, currentGraphId]);

  // Real-time consciousness operations stream (WebSocket)
  const {
    entityActivity,
    thresholdCrossings,
    consciousnessState,
    v2State,
    weightLearningEvents,
    strideSelectionEvents,
    phenomenologyMismatchEvents,
    phenomenologyHealthEvents,
    connectionState,
    error: wsError
  } = useWebSocket();

  // Note: Initial graph state loaded via REST /api/viz/snapshot
  // Live updates come through WebSocket (useWebSocket hook above)

  // Node focus state (for click-to-focus from CLAUDE_DYNAMIC.md)
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);

  // Right sidebar collapse state
  const [rightSidebarCollapsed, setRightSidebarCollapsed] = useState(false);

  // Stride events for TierBreakdownPanel (Priority 2)
  // TODO: Integrate with useWebSocket when backend emits stride.exec events
  const [strideEvents, setStrideEvents] = useState<any[]>([]);

  /**
   * WebSocket Event Integration
   * Wire real-time events to graph state updates
   *
   * Strategy: Process only new events by tracking the last processed index
   */
  const [lastProcessedThreshold, setLastProcessedThreshold] = useState<number>(-1);
  const [lastProcessedActivity, setLastProcessedActivity] = useState<number>(-1);

  // Handle threshold crossing events
  // FIXED: Removed 'nodes' from dependencies to prevent re-runs on every node update
  useEffect(() => {
    // Process all new threshold crossings since last check
    for (let i = lastProcessedThreshold + 1; i < thresholdCrossings.length; i++) {
      const crossing = thresholdCrossings[i];

      console.log('[ConsciousnessPage] Processing threshold crossing:', crossing);

      // Update node activation state with fresh entity_activations
      // The updateNodeFromEvent callback will handle merging with existing data
      updateNodeFromEvent(crossing.node_id, {
        entity_activations: {
          [crossing.entity_id]: {
            energy: crossing.entity_activity,
            last_activated: Date.now()
          }
        },
        last_active: Date.now()
      });

      // Add operation for animation
      addOperation({
        type: 'threshold_crossing',
        node_id: crossing.node_id,
        entity_id: crossing.entity_id,
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
  }, [thresholdCrossings, lastProcessedThreshold, updateNodeFromEvent, addOperation]);

  // Handle subentity activity events
  // FIXED: Removed 'nodes' from dependencies to prevent re-runs on every node update
  useEffect(() => {
    // Process all new subentity activities since last check
    for (let i = lastProcessedActivity + 1; i < entityActivity.length; i++) {
      const activity = entityActivity[i];

      console.log('[ConsciousnessPage] Processing subentity activity:', activity);

      // Update currently explored node
      // The updateNodeFromEvent will handle incrementing traversal_count internally
      updateNodeFromEvent(activity.current_node, {
        last_traversed_by: activity.entity_id,
        last_active: Date.now(),
        traversal_count: 1 // This gets added to existing count in the update function
      });

      // Add operation for animation
      addOperation({
        type: 'entity_activity',
        node_id: activity.current_node,
        entity_id: activity.entity_id,
        timestamp: Date.now(),
        data: {
          need_type: activity.need_type,
          energy_used: activity.energy_used,
          energy_budget: activity.energy_budget
        }
      });
    }

    if (entityActivity.length > 0) {
      setLastProcessedActivity(entityActivity.length - 1);
    }
  }, [entityActivity, lastProcessedActivity, updateNodeFromEvent, addOperation]);

  // Handle consciousness state updates
  useEffect(() => {
    if (!consciousnessState) return;

    console.log('[ConsciousnessPage] Consciousness state:', consciousnessState);
    // Consciousness state is global - could update UI indicators here
    // For now, just log it (CitizenMonitor will use this later)
  }, [consciousnessState]);

  const handleFocusNode = useCallback((nodeId: string) => {
    setFocusedNodeId(nodeId);
    // Emit custom event for GraphCanvas to handle
    window.dispatchEvent(new CustomEvent('node:focus', {
      detail: { nodeId }
    }));
  }, []);

  // Dynamic citizen discovery from FalkorDB
  // Polls /api/graphs every 10s to detect new citizens automatically
  const { citizens, loading: citizensLoading, error: citizensError } = useCitizens();

  // Handle citizen selection from sidebar (switches graph)
  const handleSelectCitizen = useCallback((citizenId: string) => {
    // Determine graph type and ID
    if (citizenId === 'mind_protocol') {
      selectGraph('organization', 'org_mind_protocol');
    } else {
      selectGraph('citizen', `citizen_${citizenId}`);
    }
  }, [selectGraph]);

  // Auto-select first available citizen on mount
  useEffect(() => {
    if (!currentGraphId && availableGraphs.citizens.length > 0) {
      const firstCitizen = availableGraphs.citizens[0];
      console.log('[ConsciousnessPage] Auto-selecting first citizen:', firstCitizen.id);
      selectGraph('citizen', firstCitizen.id);
    }
  }, [availableGraphs, currentGraphId, selectGraph]);

  return (
    <div className="relative w-full h-screen overflow-hidden bg-observatory-dark">
      {/* Header with system status, search, and stats (top) */}
      <Header
        currentGraphId={currentGraphId}
        nodeCount={nodes.length}
        linkCount={links.length}
        nodes={nodes}
      />

      {/* Error overlay (for testing) */}
      {(error || wsError || citizensError) && (
        <div
          data-testid="error-overlay"
          className="absolute top-20 left-1/2 -translate-x-1/2 z-50 max-w-2xl px-6 py-4 bg-red-900/90 border border-red-500/50 rounded-lg backdrop-blur-sm"
        >
          <div className="text-red-100 font-mono text-sm">
            <div className="font-bold mb-2">⚠ Error</div>
            {error && <div className="mb-1">Graph: {error}</div>}
            {wsError && <div className="mb-1">WebSocket: {wsError}</div>}
            {citizensError && <div>Citizens: {citizensError}</div>}
          </div>
        </div>
      )}

      {/* Main graph visualization - Entity-first with drill-down */}
      <EntityGraphView
        nodes={nodes}
        links={links}
        operations={operations}
        subentities={subentities}
        workingMemory={v2State.workingMemory}
        linkFlows={v2State.linkFlows}
        recentFlips={v2State.recentFlips.map(flip => ({
          node_id: flip.node_id,
          direction: flip.direction,
          timestamp: Date.now()
        }))}
      />

      {/* Subentity names floating over their clusters */}
      <EntityClusterOverlay
        nodes={nodes}
        subentities={subentities}
        entityActivity={entityActivity}
      />

      {/* Energy flow particles - Layer 2 */}
      <EnergyFlowParticles
        nodes={nodes}
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

      {/* Left Sidebar - Organized collapsible menu */}
      <LeftSidebarMenu
        v2State={v2State}
        strideSelectionEvents={strideSelectionEvents}
        strideEvents={strideEvents}
        weightLearningEvents={weightLearningEvents}
        phenomenologyMismatchEvents={phenomenologyMismatchEvents}
        phenomenologyHealthEvents={phenomenologyHealthEvents}
      />

      {/* Tooltip for hover info */}
      <Tooltip />

      {/* Right Sidebar - Collapsible Container */}
      <div
        className={`fixed top-16 bottom-0 right-0 z-40 transition-all duration-300 overflow-hidden ${
          rightSidebarCollapsed ? 'w-12' : 'w-[22rem]'
        }`}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setRightSidebarCollapsed(!rightSidebarCollapsed)}
          className="absolute top-4 left-2 z-50 p-1.5 rounded hover:bg-observatory-cyan/20 transition-colors"
          title={rightSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <span className="text-observatory-text/70 text-sm">
            {rightSidebarCollapsed ? '◀' : '▶'}
          </span>
        </button>

        {/* Right Sidebar Panels */}
        {!rightSidebarCollapsed && (
          <div className="relative w-full h-full overflow-y-auto custom-scrollbar pt-4 pr-4 pl-4">
            {/* Citizen consciousness monitor */}
            <div className="mb-4">
              <CitizenMonitor
                citizens={citizens}
                onFocusNode={handleFocusNode}
                onSelectCitizen={handleSelectCitizen}
                activeCitizenId={currentGraphId}
                v2State={v2State}
              />
            </div>
          </div>
        )}
      </div>

      {/* Detail panel - Modal overlay on node click */}
      <DetailPanel nodes={nodes} links={links} />
    </div>
  );
}
