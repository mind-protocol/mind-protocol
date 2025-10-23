'use client';

import { useMemo } from 'react';
import type { Node, Subentity } from '../hooks/useGraphData';
import type { EntityActivityEvent } from '../hooks/websocket-types';
import { getEntityColor } from '../constants/entity-colors';

interface EntityClusterOverlayProps {
  nodes: Node[];
  subentities: Subentity[];
  entityActivity?: EntityActivityEvent[];
}

interface SubEntityCluster {
  entityId: string;
  entityName: string;
  centerX: number;
  centerY: number;
  nodeCount: number;
}

/**
 * EntityClusterOverlay - Sub-Entity Activity Visualization
 *
 * Shows sub-entity names floating over spatial clusters of recently active nodes.
 * Uses last_activated timestamps to identify which nodes each sub-entity is working with.
 *
 * Author: Iris "The Aperture"
 */
export function EntityClusterOverlay({ nodes, subentities, entityActivity = [] }: EntityClusterOverlayProps) {
  // PERFORMANCE: Compute sub-entity clusters from recently active nodes (last 10 seconds)
  // Sub-entity architecture: entity_name = node_name, each active node is its own sub-entity
  const subEntityClusters = useMemo(() => {
    const now = Date.now();
    const workingMemoryWindow = 10000; // 10 seconds
    const clusters: SubEntityCluster[] = [];

    // Each node with recent traversal + energy becomes a visible sub-entity
    nodes.forEach(node => {
      if (!node.x || !node.y) return;

      // Sub-entity detection: recent traversal + non-zero energy
      const lastTraversal = node.last_traversal_time;
      const energy = node.energy || 0;

      if (lastTraversal && energy > 0 && (now - lastTraversal) < workingMemoryWindow) {
        // Sub-entity name = node name
        const entityId = node.node_id || node.id || 'unknown';
        const entityName = node.node_id || node.id || 'Unknown';

        clusters.push({
          entityId,
          entityName,
          centerX: node.x,
          centerY: node.y,
          nodeCount: 1 // Each node is its own sub-entity
        });
      }
    });

    return clusters;
  }, [nodes]);

  // Find most recent activity for each subentity (within last 5 seconds)
  const recentActivity = useMemo(() => {
    const now = Date.now();
    const recentThreshold = 5000; // 5 seconds
    const activityMap = new Map<string, EntityActivityEvent>();

    entityActivity.forEach(event => {
      const eventTime = new Date(event.timestamp).getTime();
      if (now - eventTime < recentThreshold) {
        // Keep most recent for each subentity
        const existing = activityMap.get(event.entity_id);
        if (!existing || new Date(existing.timestamp).getTime() < eventTime) {
          activityMap.set(event.entity_id, event);
        }
      }
    });

    return activityMap;
  }, [entityActivity]);

  if (subEntityClusters.length === 0) return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      {subEntityClusters.map(cluster => (
        <SubEntityLabel
          key={cluster.entityId}
          cluster={cluster}
          activity={recentActivity.get(cluster.entityId)}
        />
      ))}
    </div>
  );
}

function SubEntityLabel({
  cluster,
  activity
}: {
  cluster: SubEntityCluster;
  activity?: EntityActivityEvent;
}) {
  const isActive = !!activity;
  const entityColor = getEntityColor(cluster.entityId);

  return (
    <div
      className="absolute pointer-events-auto group transition-opacity hover:opacity-100"
      style={{
        left: cluster.centerX,
        top: cluster.centerY,
        transform: 'translate(-50%, -50%)',
        opacity: 0.7
      }}
    >
      {/* Sub-entity name - subentity-colored, pulse if active */}
      <div
        className={`text-2xl font-bold whitespace-nowrap ${
          isActive ? 'animate-pulse-glow' : ''
        }`}
        style={{ color: entityColor, textShadow: `0 0 8px ${entityColor}` }}
      >
        {cluster.entityName}
        {isActive && (
          <span className="ml-2 text-lg" style={{ color: entityColor }}>⚡</span>
        )}
      </div>

      {/* Hover info tooltip */}
      <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2
                      opacity-0 group-hover:opacity-100 transition-opacity
                      consciousness-panel px-3 py-2 text-sm whitespace-nowrap z-50">
        <div
          className="font-semibold"
          style={{ color: entityColor }}
        >
          {cluster.entityName}
        </div>
        <div className="text-gray-400 text-xs mt-1">
          {cluster.nodeCount} active nodes
        </div>
        {activity && (
          <>
            <div className="text-xs mt-2" style={{ color: entityColor }}>
              Currently exploring
            </div>
            <div className="text-xs text-gray-400">
              Need: {activity.need_type}
            </div>
            <div className="text-xs text-gray-400">
              Energy: {activity.energy_used}/{activity.energy_budget}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// Cluster computation done inline (above) for performance
// Groups nodes by which sub-entity recently activated them (last 10 seconds)
