/**
 * SubEntity Graph View Component
 *
 * Wrapper that manages subentity-first visualization with drill-down.
 * Converts subentity data to SubEntity format and aggregates emotions.
 *
 * View modes:
 * - SubEntity Mood Map (default): SubEntities as bubbles
 * - Expanded Member View: Nodes within selected subentity
 * - Full Node View: All nodes (current PixiCanvas view)
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 */

'use client';

import { useState, useMemo, useEffect } from 'react';
import { SubEntityMoodMap, type SubEntity } from './SubEntityMoodMap';
import { PixiCanvas } from './PixiCanvas';
import { StrideSparks } from './StrideSparks';
import { ActiveSubentitiesPanel } from './ActiveSubentitiesPanel';
import { aggregateSubEntityEmotion, aggregateSubEntityEnergy, calculateSubEntityCoherence } from '../lib/subentityEmotion';
import { useWebSocket } from '../hooks/useWebSocket';
import type { Node, Link, Subentity, Operation } from '../hooks/useGraphData';
import { selectVisibleGraph } from '../lib/visibleGraphSelector';
import { selectVisibleGraphV2, type RenderNode, type RenderEdge } from '../lib/graph/selectVisibleGraphV2';

interface SubEntityGraphViewProps {
  nodes: Node[];
  links: Link[];
  operations: Operation[];
  subentities: Subentity[];
  workingMemory: Set<string>;
  linkFlows: Map<string, number>;
  recentFlips: Array<{ node_id: string; direction: 'on' | 'off'; dE: number; timestamp: number }>;
  expandedSubEntities: Set<string>;
  toggleSubEntity: (subentityId: string) => void;
  subentityFlows: Record<string, number>; // "A->B" -> strength (from useGraphData)
}

/**
 * SubEntity Graph View
 *
 * Manages three view modes with smooth transitions.
 */
export function SubEntityGraphView({
  nodes,
  links,
  operations,
  subentities,
  workingMemory,
  linkFlows,
  recentFlips,
  expandedSubEntities,
  toggleSubEntity,
  subentityFlows
}: SubEntityGraphViewProps) {
  const [expandedSubEntityId, setExpandedSubEntityId] = useState<string | null>(null);

  // Window dimensions for SubEntityMoodMap (set client-side to avoid hydration mismatch)
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
    selectVisibleGraph(nodes, links, subentities, expandedSubEntities),
    [nodes, links, subentities, expandedSubEntities]
  );

  // Convert subentities to SubEntity format with emotion aggregation
  const subentityData = useMemo<SubEntity[]>(() => {
    // DIAGNOSTIC: Log data to understand member count issue
    console.log('[SubEntityGraphView] DIAGNOSTIC:', {
      totalSubentities: subentities.length,
      totalNodes: nodes.length,
      sampleSubentity: subentities[0],
      sampleNode: nodes[0],
      sampleNodeSubEntityActivations: nodes[0]?.entity_activations
    });

    return subentities.map(subentity => {
      // Get member nodes for this subentity
      // Nodes "belong" to subentities that have activated them recently
      const memberNodes = nodes.filter(node => {
        const nodeId = node.id || node.node_id;
        if (!nodeId) return false;

        // Check if this subentity has activated this node (entity_activations field)
        if (node.entity_activations && typeof node.entity_activations === 'object') {
          // Extract short subentity name from full subentity_id
          // Format: 'entity_citizen_{citizen}_{short_name}' → extract '{short_name}'
          const shortName = subentity.subentity_id?.split('_').pop();

          // Check both full subentity_id (new format) and short name (legacy format)
          return subentity.subentity_id in node.entity_activations ||
                 (shortName && shortName in node.entity_activations);
        }

        return false;
      });

      // DIAGNOSTIC: Log member count for each subentity
      if (memberNodes.length === 0) {
        // Sample entity_activations keys from first 3 nodes that have them
        const sampleKeys = nodes
          .filter(n => n.entity_activations && typeof n.entity_activations === 'object')
          .slice(0, 3)
          .map(n => Object.keys(n.entity_activations!));

        console.log(`[SubEntityGraphView] SubEntity ${subentity.subentity_id} has 0 members:`, {
          subentity_id: subentity.subentity_id,
          shortName: subentity.subentity_id?.split('_').pop(),
          totalNodesChecked: nodes.length,
          nodesWithSubEntityActivations: nodes.filter(n => n.entity_activations).length,
          sampleSubEntityActivationKeys: sampleKeys
        });
      }

      // Aggregate emotion from members
      const subentityEmotion = aggregateSubEntityEmotion(memberNodes, emotionState.nodeEmotions);

      // Aggregate energy from active members
      const subentityEnergy = aggregateSubEntityEnergy(memberNodes);

      // Calculate coherence
      const coherence = calculateSubEntityCoherence(memberNodes, emotionState.nodeEmotions);

      // Determine if active (has any active members)
      const isActive = memberNodes.some(node => {
        const energy = node.energy || 0;
        const theta = (node as any).activation_threshold || 0.1;
        return energy > theta;
      });

      return {
        id: subentity.subentity_id,
        name: subentity.name || subentity.subentity_id,
        kind: (subentity as any).kind || 'functional',
        color: (subentity as any).color || '#64748b',
        energy: subentityEnergy,
        theta: (subentity as any).theta || 0,
        active: isActive,
        members_count: memberNodes.length,
        coherence,
        emotion: subentityEmotion || undefined
      };
    });
  }, [subentities, nodes, emotionState.nodeEmotions]);

  // NEW: Compute two-layer visible graph using V2 selector
  const renderGraph = useMemo(() => {
    return selectVisibleGraphV2(subentityData, nodes, links, expandedSubEntities, linkFlows);
  }, [subentityData, nodes, links, expandedSubEntities, linkFlows]);

  // Adapter: Transform RenderGraph to PixiCanvas ViewModel format
  const pixiData = useMemo(() => {
    const pixiNodes = renderGraph.nodes.map(n => ({
      id: n.id,
      name: n.label ?? n.id,
      node_type: n.kind,     // 'subentity' | 'node' | 'proxy'
      energy: n.energy ?? 0,
      x: n.x,
      y: n.y,
      // Pass through other fields PixiCanvas might use
      text: n.label,
      weight: 1.0,
      last_active: undefined,
      last_traversal_time: undefined,
      traversal_count: 0,
      entity_activations: {},
    }));

    const pixiLinks = renderGraph.edges.map(e => ({
      id: e.id,
      source: e.from,
      target: e.to,
      type: e.kind === 'entity' ? 'RELATES_TO' : 'ENABLES', // Any label works for renderer
      strength: e.w ?? 0.5,
      // Pass through other fields PixiCanvas might use
      valence: undefined,
      confidence: undefined,
      created_at: undefined,
      last_traversal: undefined,
      traversal_count: 0,
    }));

    return { nodes: pixiNodes, links: pixiLinks };
  }, [renderGraph]);

  // Click listener: SubEntity super-nodes toggle expand/collapse
  useEffect(() => {
    const onClick = (e: any) => {
      const id: string | undefined = e?.detail?.node?.id;
      if (!id) return;

      // Check if this is a subentity super-node (from renderGraph)
      const clickedNode = renderGraph.nodes.find(n => n.id === id);
      if (clickedNode && clickedNode.kind === 'entity') {
        toggleSubEntity(id);
        // Don't change view mode - stay in current view (Full Graph or SubEntity Map)
        // setExpandedSubEntityId is only needed for subentity-expanded mode, not used in node-graph
      }
    };

    window.addEventListener('node:click', onClick as any);
    return () => window.removeEventListener('node:click', onClick as any);
  }, [renderGraph.nodes, toggleSubEntity]);

  // Handle subentity click -> toggle expansion
  const handleSubEntityClick = (subentityId: string) => {
    toggleSubEntity(subentityId);
    // Also update local expanded state
    if (expandedSubEntityId === subentityId) {
      setExpandedSubEntityId(null);
    } else {
      setExpandedSubEntityId(subentityId);
    }
  };

  // Handle back to subentity map
  const handleBackToSubEntityMap = () => {
    setExpandedSubEntityId(null);
  };

  // Get member nodes for expanded subentity
  const expandedMemberNodes = useMemo(() => {
    if (!expandedSubEntityId) return [];
    return nodes.filter(node => {
      const nodeId = node.id || node.node_id;
      if (!nodeId) return false;
      return (node as any).subentity_id === expandedSubEntityId ||
             (node as any).primary_entity === expandedSubEntityId;
    });
  }, [nodes, expandedSubEntityId]);

  // Get links between expanded members (active links only)
  const expandedMemberLinks = useMemo(() => {
    if (!expandedSubEntityId || expandedMemberNodes.length === 0) return [];

    const memberIds = new Set(expandedMemberNodes.map(n => n.id || n.node_id));

    return links.filter(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;

      // Link must connect two members of this subentity
      if (!memberIds.has(sourceId) || !memberIds.has(targetId)) {
        return false;
      }

      // Only show active links (flow > 0)
      const flowCount = linkFlows.get(link.id || '');
      return flowCount !== undefined && flowCount > 0;
    });
  }, [links, expandedMemberNodes, expandedSubEntityId, linkFlows]);

  return (
    <div className="relative w-full h-full flex flex-col">
      {/* Active Subentities Panel - WM Focus */}
      <ActiveSubentitiesPanel
        subentities={subentities}
        subentityData={subentityData}
        nodes={nodes}
        workingMemory={workingMemory}
      />

      {/* Single High-Performance View - PixiCanvas with Hulls */}
      <div className="relative flex-1">
        <PixiCanvas
          nodes={pixiData.nodes as any}
          links={pixiData.links as any}
          operations={operations}
          subentities={subentities}
          workingMemory={workingMemory}
          linkFlows={linkFlows}
          recentFlips={recentFlips}
        />
        <StrideSparks nodes={nodes} links={links} />
      </div>
    </div>
  );
}
