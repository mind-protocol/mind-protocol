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
import { aggregateEntityEmotion, aggregateEntityEnergy, calculateEntityCoherence } from '../lib/entityEmotion';
import { useWebSocket } from '../hooks/useWebSocket';
import type { Node, Link, Subentity, Operation } from '../hooks/useGraphData';

export type ViewMode = 'entity-map' | 'entity-expanded' | 'node-graph';

interface EntityGraphViewProps {
  nodes: Node[];
  links: Link[];
  operations: Operation[];
  subentities: Subentity[];
  workingMemory: string[];
  linkFlows: Map<string, number>;
  recentFlips: Array<{ node_id: string; direction: 'on' | 'off'; timestamp: number }>;
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
  recentFlips
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

  // Convert subentities to Entity format with emotion aggregation
  const entities = useMemo<Entity[]>(() => {
    return subentities.map(subentity => {
      // Get member nodes for this subentity
      const memberNodes = nodes.filter(node => {
        const nodeId = node.id || node.node_id;
        if (!nodeId) return false;

        // Check if node belongs to this subentity
        // This depends on how membership is tracked - adjust based on actual data structure
        return (node as any).entity_id === subentity.entity_id ||
               (node as any).primary_entity === subentity.entity_id;
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

  // Handle entity click -> expand to member view
  const handleEntityClick = (entityId: string) => {
    setExpandedEntityId(entityId);
    setViewMode('entity-expanded');
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
    <div className="relative w-full h-full">
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

      {/* Back button for expanded view */}
      {viewMode === 'entity-expanded' && (
        <button
          onClick={handleBackToEntityMap}
          className="absolute top-4 left-4 z-50 px-4 py-2 bg-slate-800/80 text-slate-200 rounded-lg text-sm font-medium backdrop-blur-sm border border-slate-700 hover:bg-slate-700/80 transition-colors"
        >
          ← Back to Entity Map
        </button>
      )}

      {/* Entity count indicator */}
      {viewMode === 'entity-map' && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-slate-900/80 text-slate-300 rounded-lg text-xs font-mono backdrop-blur-sm border border-slate-700">
          {entities.length} entities · {entities.filter(e => e.active).length} active
        </div>
      )}

      {/* Entity Mood Map View */}
      {viewMode === 'entity-map' && (
        <EntityMoodMap
          entities={entities}
          width={dimensions.width}
          height={dimensions.height}
          onEntityClick={handleEntityClick}
        />
      )}

      {/* Expanded Member View */}
      {viewMode === 'entity-expanded' && (
        <div className="w-full h-full relative">
          {/* Entity header */}
          <div className="absolute top-20 left-1/2 -translate-x-1/2 z-40 px-6 py-3 bg-slate-900/90 rounded-lg border border-slate-700 backdrop-blur-sm">
            <div className="text-consciousness-green font-semibold">
              {entities.find(e => e.id === expandedEntityId)?.name || expandedEntityId}
            </div>
            <div className="text-xs text-slate-400 mt-1">
              {expandedMemberNodes.length} members · {expandedMemberLinks.length} active links
            </div>
          </div>

          <PixiCanvas
            nodes={expandedMemberNodes}
            links={expandedMemberLinks}
            operations={operations.filter(op => {
              const memberIds = new Set(expandedMemberNodes.map(n => n.id || n.node_id));
              return memberIds.has(op.node_id);
            })}
            subentities={[]}
            workingMemory={new Set(workingMemory)}
            linkFlows={linkFlows}
            recentFlips={recentFlips.filter(flip => {
              const memberIds = new Set(expandedMemberNodes.map(n => n.id || n.node_id));
              return memberIds.has(flip.node_id);
            })}
          />
        </div>
      )}

      {/* Full Node Graph View */}
      {viewMode === 'node-graph' && (
        <>
          <PixiCanvas
            nodes={nodes}
            links={links}
            operations={operations}
            subentities={subentities}
            workingMemory={new Set(workingMemory)}
            linkFlows={linkFlows}
            recentFlips={recentFlips}
          />
          <StrideSparks nodes={nodes} links={links} />
        </>
      )}

      {/* Stride Sparks for expanded view */}
      {viewMode === 'entity-expanded' && (
        <StrideSparks nodes={expandedMemberNodes} links={expandedMemberLinks} />
      )}
    </div>
  );
}
