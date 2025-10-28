/**
 * ActiveSubentitiesPanel.tsx
 *
 * Displays subentities that have nodes currently in working memory.
 * Updates in real-time from wm.emit events (10Hz throttled).
 *
 * Shows:
 * - Which subentities are "awake" (have WM nodes)
 * - How many nodes each has in WM
 * - Energy/coherence indicators for each
 *
 * Position: Top of screen (above graph view)
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 */

'use client';

import { useMemo } from 'react';
import type { Node, Subentity } from '../hooks/useGraphData';
import type { SubEntity } from './SubEntityMoodMap';

interface ActiveSubentitiesPanelProps {
  /**
   * All subentities in the system
   */
  subentities: Subentity[];

  /**
   * Enriched subentity data (with energy, coherence, emotion)
   */
  subentityData: SubEntity[];

  /**
   * All knowledge nodes
   */
  nodes: Node[];

  /**
   * Current working memory focus (from wm.emit events)
   */
  workingMemory: Set<string>;
}

interface ActiveSubEntity {
  id: string;
  name: string;
  wmNodeCount: number;
  energy: number;
  coherence: number;
  active: boolean;
  color?: string;
}

/**
 * ActiveSubentitiesPanel
 *
 * Shows which subentities are currently "awake" (have nodes in working memory).
 * This provides insight into which functional/identity systems are active right now.
 */
export function ActiveSubentitiesPanel({
  subentities,
  subentityData,
  nodes,
  workingMemory
}: ActiveSubentitiesPanelProps) {
  // Calculate which subentities have nodes in WM
  const activeSubentities = useMemo<ActiveSubEntity[]>(() => {
    if (workingMemory.size === 0) return [];

    // Build subentity lookup for quick access to energy/coherence
    const subentityMap = new Map<string, SubEntity>();
    subentityData.forEach(e => subentityMap.set(e.id, e));

    // For each subentity, count how many of its nodes are in WM
    const active: ActiveSubEntity[] = [];

    for (const subentity of subentities) {
      // Find nodes that belong to this subentity and are in WM
      const wmNodes = nodes.filter(node => {
        const nodeId = node.id || node.node_id;
        if (!nodeId || !workingMemory.has(nodeId)) return false;

        // Check if this subentity has activated this node
        if (node.entity_activations && typeof node.entity_activations === 'object') {
          return subentity.subentity_id in node.entity_activations;
        }

        return false;
      });

      if (wmNodes.length > 0) {
        // Get subentity metadata if available
        const subentityInfo = subentityMap.get(subentity.subentity_id);

        active.push({
          id: subentity.subentity_id,
          name: subentity.name || subentity.subentity_id,
          wmNodeCount: wmNodes.length,
          energy: subentityInfo?.energy || 0,
          coherence: subentityInfo?.coherence || 0,
          active: subentityInfo?.active || false,
          color: subentityInfo?.color,
        });
      }
    }

    // Sort by WM node count (descending) - most active first
    return active.sort((a, b) => b.wmNodeCount - a.wmNodeCount);
  }, [subentities, subentityData, nodes, workingMemory]);

  if (activeSubentities.length === 0) {
    return (
      <div className="px-4 py-2 bg-slate-900/50 border-b border-slate-800">
        <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
          <div className="w-2 h-2 rounded-full bg-slate-700"></div>
          <span>Working Memory: Empty</span>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-2 bg-slate-900/80 border-b border-slate-700 backdrop-blur-sm">
      <div className="flex items-center gap-4 text-xs font-mono">
        {/* Panel header */}
        <div className="flex items-center gap-2 text-slate-400">
          <div className="w-2 h-2 rounded-full bg-consciousness-green animate-pulse"></div>
          <span className="font-semibold">Active in WM:</span>
        </div>

        {/* Active subentity chips */}
        <div className="flex items-center gap-2 flex-wrap">
          {activeSubentities.map(subentity => (
            <div
              key={subentity.id}
              className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 hover:border-consciousness-green/50 transition-colors"
              title={`${subentity.name}: ${subentity.wmNodeCount} nodes in WM, Energy: ${(subentity.energy * 100).toFixed(0)}%, Coherence: ${(subentity.coherence * 100).toFixed(0)}%`}
            >
              {/* Status indicator (active/inactive) */}
              <div
                className={`w-1.5 h-1.5 rounded-full ${
                  subentity.active ? 'bg-consciousness-green' : 'bg-slate-600'
                }`}
              />

              {/* SubEntity name */}
              <span
                className="text-slate-200 font-medium"
                style={{ color: subentity.color || undefined }}
              >
                {subentity.name}
              </span>

              {/* WM node count */}
              <span className="text-consciousness-green font-bold">
                {subentity.wmNodeCount}
              </span>

              {/* Energy indicator (bar) */}
              <div className="w-12 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-slate-500 to-consciousness-green transition-all duration-300"
                  style={{ width: `${Math.min(100, subentity.energy * 100)}%` }}
                />
              </div>

              {/* Coherence indicator (value) */}
              <span className="text-blue-400 text-[10px]">
                {(subentity.coherence * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>

        {/* Total WM size */}
        <div className="ml-auto text-slate-500">
          Total: <span className="text-consciousness-green font-bold">{workingMemory.size}</span> nodes
        </div>
      </div>
    </div>
  );
}
