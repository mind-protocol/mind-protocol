'use client';

import { useMemo } from 'react';
import type { Node, Entity } from '../hooks/useGraphData';
import type { EntityActivityEvent } from '../hooks/websocket-types';

interface EntityClusterOverlayProps {
  nodes: Node[];
  entities: Entity[];
  entityActivity?: EntityActivityEvent[];
}

interface EntityCluster {
  entityId: string;
  entityName: string;
  centerX: number;
  centerY: number;
  nodeCount: number;
  avgEnergy: number;
}

/**
 * EntityClusterOverlay
 *
 * Shows entity names floating over their spatial clusters.
 * Makes entity PRESENCE visible in the graph.
 *
 * Design: Large, semi-transparent names positioned at cluster centroids.
 * Hoverable for more info (node count, energy level).
 */
export function EntityClusterOverlay({ nodes, entities, entityActivity = [] }: EntityClusterOverlayProps) {
  const clusters = useMemo(() => {
    return computeEntityClusters(nodes, entities);
  }, [nodes, entities]);

  // Find most recent activity for each entity (within last 5 seconds)
  const recentActivity = useMemo(() => {
    const now = Date.now();
    const recentThreshold = 5000; // 5 seconds
    const activityMap = new Map<string, EntityActivityEvent>();

    entityActivity.forEach(event => {
      const eventTime = new Date(event.timestamp).getTime();
      if (now - eventTime < recentThreshold) {
        // Keep most recent for each entity
        const existing = activityMap.get(event.entity_id);
        if (!existing || new Date(existing.timestamp).getTime() < eventTime) {
          activityMap.set(event.entity_id, event);
        }
      }
    });

    return activityMap;
  }, [entityActivity]);

  if (clusters.length === 0) return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      {clusters.map(cluster => (
        <EntityLabel
          key={cluster.entityId}
          cluster={cluster}
          activity={recentActivity.get(cluster.entityId)}
        />
      ))}
    </div>
  );
}

function EntityLabel({
  cluster,
  activity
}: {
  cluster: EntityCluster;
  activity?: EntityActivityEvent;
}) {
  const isActive = !!activity;

  return (
    <div
      className="absolute pointer-events-auto group transition-opacity hover:opacity-100"
      style={{
        left: cluster.centerX,
        top: cluster.centerY,
        transform: 'translate(-50%, -50%)',
        opacity: Math.max(0.3, cluster.avgEnergy)
      }}
    >
      {/* Entity name - large, visible, pulse if active */}
      <div className={`text-4xl font-bold text-consciousness-green/60 whitespace-nowrap ${
        isActive ? 'animate-pulse-glow' : ''
      }`}>
        {cluster.entityName}
        {isActive && (
          <span className="ml-2 text-xl text-consciousness-green">⚡</span>
        )}
      </div>

      {/* Hover info tooltip */}
      <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2
                      opacity-0 group-hover:opacity-100 transition-opacity
                      consciousness-panel px-3 py-2 text-sm whitespace-nowrap z-50">
        <div className="text-consciousness-green font-semibold">
          {cluster.entityName}
        </div>
        <div className="text-gray-400 text-xs mt-1">
          {cluster.nodeCount} active nodes
        </div>
        <div className="text-gray-400 text-xs">
          Avg energy: {(cluster.avgEnergy * 100).toFixed(0)}%
        </div>
        {activity && (
          <>
            <div className="text-xs text-consciousness-green mt-2">
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

// ============================================================================
// Cluster Computation
// ============================================================================

function computeEntityClusters(nodes: Node[], entities: Entity[]): EntityCluster[] {
  const entityMap = new Map<string, {
    nodes: Node[];
    totalEnergy: number;
  }>();

  // Group nodes by entity
  nodes.forEach(node => {
    if (!node.x || !node.y) return;

    // Try entity_activations first
    if (node.entity_activations && typeof node.entity_activations === 'object') {
      Object.entries(node.entity_activations).forEach(([entityId, activation]) => {
        if (!entityMap.has(entityId)) {
          entityMap.set(entityId, { nodes: [], totalEnergy: 0 });
        }

        const entry = entityMap.get(entityId)!;
        entry.nodes.push(node);
        entry.totalEnergy += (activation as any).energy || 0;
      });
    }
    // Fallback: Use sub_entity_weights if available
    else if (node.sub_entity_weights && typeof node.sub_entity_weights === 'object') {
      Object.entries(node.sub_entity_weights).forEach(([entityId, weight]) => {
        if (!entityMap.has(entityId)) {
          entityMap.set(entityId, { nodes: [], totalEnergy: 0 });
        }

        const entry = entityMap.get(entityId)!;
        entry.nodes.push(node);
        entry.totalEnergy += (weight as number) || 0;
      });
    }
  });

  // Compute centroids
  const clusters: EntityCluster[] = [];

  entityMap.forEach((data, entityId) => {
    if (data.nodes.length === 0) return;

    // Calculate centroid
    let sumX = 0;
    let sumY = 0;
    data.nodes.forEach(node => {
      sumX += node.x!;
      sumY += node.y!;
    });

    const centerX = sumX / data.nodes.length;
    const centerY = sumY / data.nodes.length;
    const avgEnergy = data.totalEnergy / data.nodes.length;

    // Get entity name
    const entity = entities.find(e => e.entity_id === entityId);
    const entityName = entity?.name || entityId;

    clusters.push({
      entityId,
      entityName,
      centerX,
      centerY,
      nodeCount: data.nodes.length,
      avgEnergy
    });
  });

  return clusters;
}
