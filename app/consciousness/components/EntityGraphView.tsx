/**
 * Entity Graph View Component
 *
 * Wrapper that manages entity-first visualization with drill-down.
 * Converts subentity data to Entity format and aggregates emotions.
 *
 * View modes:
 * - Entity Mood Map (default): Entities as bubbles
 * - Expanded Member View: Nodes within selected entity
 * - Full Node View: All nodes (current PixiCanvas view)
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 */

'use client';

import { useState, useMemo, useEffect } from 'react';
import { EntityMoodMap, type Entity } from './EntityMoodMap';
import { PixiCanvas } from './PixiCanvas';
import { StrideSparks } from './StrideSparks';
import { ActiveSubentitiesPanel } from './ActiveSubentitiesPanel';
import { aggregateEntityEmotion, aggregateEntityEnergy, calculateEntityCoherence } from '../lib/entityEmotion';
import { useWebSocket } from '../hooks/useWebSocket';
import type { Node, Link, Subentity, Operation } from '../hooks/useGraphData';
import { selectVisibleGraph } from '../lib/visibleGraphSelector';

export type ViewMode = 'entity-map' | 'entity-expanded' | 'node-graph';

interface EntityGraphViewProps {
  nodes: Node[];
  links: Link[];
  operations: Operation[];
  subentities: Subentity[];
  workingMemory: Set<string>;
  linkFlows: Map<string, number>;
  recentFlips: Array<{ node_id: string; direction: 'on' | 'off'; dE: number; timestamp: number }>;
  expandedEntities: Set<string>;
  toggleEntity: (entityId: string) => void;
}

/**
 * Entity Graph View
 *
 * Manages three view modes with smooth transitions.
 */
export function EntityGraphView({
  nodes,
  links,
  operations,
  subentities,
  workingMemory,
  linkFlows,
  recentFlips,
  expandedEntities,
  toggleEntity
}: EntityGraphViewProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('entity-map');
  const [expandedEntityId, setExpandedEntityId] = useState<string | null>(null);

  // Window dimensions for EntityMoodMap (set client-side to avoid hydration mismatch)
  const [dimensions, setDimensions] = useState({ width: 1920, height: 1080 });
  const [isClient, setIsClient] = useState(false);

  const { emotionState } = useWebSocket();

  // Set actual window dimensions on mount (client-side only)
  useEffect(() => {
    setIsClient(true);
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);

    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Compute visible graph based on expansion state (for Pixi rendering)
  const visibleGraph = useMemo(() =>
    selectVisibleGraph(nodes, links, subentities, expandedEntities),
    [nodes, links, subentities, expandedEntities]
  );

  // Convert subentities to Entity format with emotion aggregation
  const entities = useMemo<Entity[]>(() => {
    return subentities.map(subentity => {
      // Get member nodes for this subentity
      // Nodes "belong" to entities that have activated them recently
      const memberNodes = nodes.filter(node => {
        const nodeId = node.id || node.node_id;
        if (!nodeId) return false;

        // Check if this entity has activated this node (entity_activations field)
        if (node.entity_activations && typeof node.entity_activations === 'object') {
          return subentity.entity_id in node.entity_activations;
        }

        return false;
      });

      // Aggregate emotion from members
      const entityEmotion = aggregateEntityEmotion(memberNodes, emotionState.nodeEmotions);

      // Aggregate energy from active members
      const entityEnergy = aggregateEntityEnergy(memberNodes);

      // Calculate coherence
      const coherence = calculateEntityCoherence(memberNodes, emotionState.nodeEmotions);

      // Determine if active (has any active members)
      const isActive = memberNodes.some(node => {
        const energy = node.energy || 0;
        const theta = (node as any).activation_threshold || 0.1;
        return energy > theta;
      });

      return {
        id: subentity.entity_id,
        name: subentity.name || subentity.entity_id,
        kind: (subentity as any).kind || 'functional',
        color: (subentity as any).color || '#64748b',
        energy: entityEnergy,
        theta: (subentity as any).theta || 0,
        active: isActive,
        members_count: memberNodes.length,
        coherence,
        emotion: entityEmotion || undefined
      };
    });
  }, [subentities, nodes, emotionState.nodeEmotions]);

  // Handle entity click -> toggle expansion
  const handleEntityClick = (entityId: string) => {
    toggleEntity(entityId);
    // Also update local expanded state for the entity-expanded view mode
    if (expandedEntityId === entityId) {
      setExpandedEntityId(null);
      setViewMode('entity-map');
    } else {
      setExpandedEntityId(entityId);
      setViewMode('entity-expanded');
    }
  };

  // Handle back to entity map
  const handleBackToEntityMap = () => {
    setExpandedEntityId(null);
    setViewMode('entity-map');
  };

  // Get member nodes for expanded entity
  const expandedMemberNodes = useMemo(() => {
    if (!expandedEntityId) return [];
    return nodes.filter(node => {
      const nodeId = node.id || node.node_id;
      if (!nodeId) return false;
      return (node as any).entity_id === expandedEntityId ||
             (node as any).primary_entity === expandedEntityId;
    });
  }, [nodes, expandedEntityId]);

  // Get links between expanded members (active links only)
  const expandedMemberLinks = useMemo(() => {
    if (!expandedEntityId || expandedMemberNodes.length === 0) return [];

    const memberIds = new Set(expandedMemberNodes.map(n => n.id || n.node_id));

    return links.filter(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;

      // Link must connect two members of this entity
      if (!memberIds.has(sourceId) || !memberIds.has(targetId)) {
        return false;
      }

      // Only show active links (flow > 0)
      const flowCount = linkFlows.get(link.id || '');
      return flowCount !== undefined && flowCount > 0;
    });
  }, [links, expandedMemberNodes, expandedEntityId, linkFlows]);

  return (
    <div className="relative w-full h-full flex flex-col">
      {/* Active Subentities Panel - WM Focus */}
      <ActiveSubentitiesPanel
        subentities={subentities}
        entities={entities}
        nodes={nodes}
        workingMemory={workingMemory}
      />

      {/* Graph View Container */}
      <div className="relative flex-1">
        {/* View Mode Toggle */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 flex gap-2">
        <button
          onClick={() => setViewMode('entity-map')}
          className={`px-4 py-2 rounded-lg text-sm font-medium backdrop-blur-sm transition-colors ${
            viewMode === 'entity-map'
              ? 'bg-consciousness-green/20 text-consciousness-green border border-consciousness-green/50'
              : 'bg-slate-800/50 text-slate-400 border border-slate-700 hover:text-slate-200'
          }`}
        >
          Entity Map
        </button>
        <button
          onClick={() => setViewMode('node-graph')}
          className={`px-4 py-2 rounded-lg text-sm font-medium backdrop-blur-sm transition-colors ${
            viewMode === 'node-graph'
              ? 'bg-consciousness-green/20 text-consciousness-green border border-consciousness-green/50'
              : 'bg-slate-800/50 text-slate-400 border border-slate-700 hover:text-slate-200'
          }`}
        >
          Full Graph
        </button>
      </div>

      {/* Collapse button for expanded entity */}
      {expandedEntityId && viewMode === 'entity-map' && (
        <button
          onClick={handleBackToEntityMap}
          className="absolute top-4 left-4 z-50 px-4 py-2 bg-slate-800/80 text-slate-200 rounded-lg text-sm font-medium backdrop-blur-sm border border-slate-700 hover:bg-slate-700/80 transition-colors"
        >
          ✕ Collapse Entity
        </button>
      )}

      {/* Entity count indicator with visible graph stats */}
      {viewMode === 'entity-map' && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-slate-900/80 text-slate-300 rounded-lg text-xs font-mono backdrop-blur-sm border border-slate-700">
          {entities.length} entities · {entities.filter(e => e.active).length} active · {expandedEntities.size} expanded
          <br />
          Render: {visibleGraph.nodes.filter(n => n.kind === 'entity').length} entity nodes · {visibleGraph.nodes.filter(n => n.kind === 'node').length} member nodes · {visibleGraph.edges.length} edges
          {expandedEntityId && (
            <><br />Expanded: {entities.find(e => e.id === expandedEntityId)?.name || expandedEntityId}</>
          )}
        </div>
      )}

      {/* Entity Mood Map View - Always show when in entity-map mode */}
      {viewMode === 'entity-map' && (
        <>
          <EntityMoodMap
            entities={entities}
            width={dimensions.width}
            height={dimensions.height}
            onEntityClick={handleEntityClick}
          />

          {/* Member nodes overlay - shown when entity is expanded */}
          {expandedEntityId && expandedMemberNodes.length > 0 && (
            <div className="absolute inset-0 pointer-events-none z-30">
              {/* Semi-transparent overlay showing this is expanded state */}
              <div className="absolute top-20 left-1/2 -translate-x-1/2 px-4 py-2 bg-slate-900/90 text-slate-300 rounded-lg text-xs font-mono backdrop-blur-sm border border-consciousness-green/50 pointer-events-auto">
                {entities.find(e => e.id === expandedEntityId)?.name || expandedEntityId} inner structure: {expandedMemberNodes.length} nodes · {expandedMemberLinks.length} links
              </div>

              {/* Render member nodes as overlay */}
              <svg className="absolute inset-0 w-full h-full pointer-events-auto" style={{ zIndex: 25 }}>
                {/* Draw member nodes as smaller circles */}
                {expandedMemberNodes.map(node => {
                  // Position nodes randomly around center for now (need proper layout)
                  const x = dimensions.width / 2 + (Math.random() - 0.5) * 400;
                  const y = dimensions.height / 2 + (Math.random() - 0.5) * 400;
                  const energy = node.energy || 0;
                  const radius = 8 + energy * 12;

                  return (
                    <g key={node.id || node.node_id}>
                      <circle
                        cx={x}
                        cy={y}
                        r={radius}
                        fill="#5efc82"
                        fillOpacity={0.3}
                        stroke="#5efc82"
                        strokeWidth={2}
                      />
                      <text
                        x={x}
                        y={y + radius + 12}
                        textAnchor="middle"
                        fill="#e2e8f0"
                        fontSize="10"
                        fontFamily="monospace"
                      >
                        {(node as any).name || node.node_id}
                      </text>
                    </g>
                  );
                })}

                {/* Draw links between member nodes */}
                {expandedMemberLinks.map((link, i) => {
                  // Simplified link rendering (need actual node positions)
                  const sourceNode = expandedMemberNodes.find(n =>
                    (n.id || n.node_id) === (typeof link.source === 'string' ? link.source : (link.source as any).id)
                  );
                  const targetNode = expandedMemberNodes.find(n =>
                    (n.id || n.node_id) === (typeof link.target === 'string' ? link.target : (link.target as any).id)
                  );

                  if (!sourceNode || !targetNode) return null;

                  // Use same random positioning as nodes (temporary)
                  const x1 = dimensions.width / 2 + (Math.random() - 0.5) * 400;
                  const y1 = dimensions.height / 2 + (Math.random() - 0.5) * 400;
                  const x2 = dimensions.width / 2 + (Math.random() - 0.5) * 400;
                  const y2 = dimensions.height / 2 + (Math.random() - 0.5) * 400;

                  return (
                    <line
                      key={`${sourceNode.id}-${targetNode.id}-${i}`}
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#5efc82"
                      strokeOpacity={0.2}
                      strokeWidth={1}
                    />
                  );
                })}
              </svg>
            </div>
          )}
        </>
      )}

      {/* Full Node Graph View */}
      {viewMode === 'node-graph' && (
        <>
          <PixiCanvas
            nodes={nodes}
            links={links}
            operations={operations}
            subentities={subentities}
            workingMemory={workingMemory}
            linkFlows={linkFlows}
            recentFlips={recentFlips}
          />
          <StrideSparks nodes={nodes} links={links} />
        </>
      )}
      </div> {/* Close Graph View Container */}
    </div> {/* Close root container */}
  );
}
