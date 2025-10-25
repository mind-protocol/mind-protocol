/**
 * selectVisibleGraphV2.ts
 *
 * Unified selector for two-layer entity/node visualization.
 * Adapted from reference implementation to work with D3-based entity positioning.
 *
 * Input:
 * - Entities with D3 simulation positions (x, y from EntityMoodMap)
 * - Nodes from useGraphData
 * - Links from useGraphData
 * - Expansion state (expandedEntities Set)
 * - Link flows (for entity-to-entity aggregation)
 *
 * Output:
 * - RenderNode[] (entities as super-nodes, member nodes, proxies)
 * - RenderEdge[] (entity edges when collapsed, node edges when expanded)
 *
 * Logic:
 * - Collapsed entity → super-node
 * - Expanded entity → member nodes (canonical + proxies for multi-membership)
 * - Edges route based on expansion state (entity-entity or node-node)
 *
 * Author: Iris "The Aperture" (from Nicolas's reference implementation)
 * Created: 2025-10-25
 */

import { layoutLocal } from './layoutLocal';
import type { Node, Link, Subentity } from '../../hooks/useGraphData';
import type { Entity } from '../../components/EntityMoodMap';

export type RenderNode = {
  id: string;
  x: number;
  y: number;
  r: number;                 // radius in pixels
  energy: number;            // 0-1 normalized
  kind: 'entity' | 'node' | 'proxy';
  entityId?: string;         // container owner (for nodes/proxies)
  canonicalId?: string;      // for proxies: link to canonical node
  label?: string;
  color?: string;            // entity color or node type color
};

export type RenderEdge = {
  id: string;
  from: string;
  to: string;                // ids in the current render set
  w: number;                 // weight for stroke width/alpha mapping
  kind: 'entity' | 'intra' | 'inter';
};

// LOD threshold: hide node labels when too many nodes visible
const LOD_HIDE_NODE_LABELS = 3000;

/**
 * Calculate visual radius for entity super-node
 */
const entityRadius = (entity: Entity) => {
  const baseRadius = 30;
  const energyScale = Math.sqrt(entity.energy || 0) * 20;
  return Math.min(60, baseRadius + energyScale); // Cap at 60px
};

/**
 * Calculate visual radius for member node
 */
const nodeRadius = (node: Node) => {
  const baseRadius = 6;
  const energyScale = (node.energy || 0) * 10;
  return Math.min(16, baseRadius + energyScale); // Cap at 16px
};

/**
 * Fixed radius for proxy nodes (UI-only indicators)
 */
const proxyRadius = 3.5;

/**
 * Create deterministic pair key for entity-to-entity aggregation
 */
const pairKey = (a: string, b: string) => (a < b ? `${a}|${b}` : `${b}|${a}`);

/**
 * Select visible graph for current expansion state
 *
 * This is the main selector that transforms source data into renderable graph.
 *
 * @param entities - Entities with D3 positions (from EntityMoodMap)
 * @param nodes - All knowledge nodes
 * @param links - All knowledge links
 * @param expandedEntities - Set of entity IDs that are expanded
 * @param linkFlows - Map of link_id -> flow count (from link.flow.summary events)
 * @returns Render graph with nodes and edges
 */
export function selectVisibleGraphV2(
  entities: Entity[],
  nodes: Node[],
  links: Link[],
  expandedEntities: Set<string>,
  linkFlows: Map<string, number>
): {
  nodes: RenderNode[];
  edges: RenderEdge[];
  meta: { hideNodeLabels: boolean };
} {
  const rNodes: RenderNode[] = [];
  const rEdges: RenderEdge[] = [];

  // Build entity lookup for quick access
  const entityMap = new Map<string, Entity>();
  entities.forEach(e => entityMap.set(e.id, e));

  // Build node lookup
  const nodeMap = new Map<string, Node>();
  nodes.forEach(n => {
    const nodeId = n.id || n.node_id;
    if (nodeId) nodeMap.set(nodeId, n);
  });

  // 1) ENTITY SUPER-NODES (draw only if collapsed)
  for (const entity of entities) {
    if (!expandedEntities.has(entity.id)) {
      rNodes.push({
        id: entity.id,
        x: entity.x ?? 0, // D3 simulation position (fallback to 0 if not yet positioned)
        y: entity.y ?? 0,
        r: entityRadius(entity),
        energy: entity.energy || 0,
        kind: 'entity',
        label: entity.name,
        color: entity.color,
      });
    }
  }

  // 2) EXPANDED ENTITIES → INNER NODES + PROXIES
  for (const entityId of expandedEntities) {
    const entity = entityMap.get(entityId);
    if (!entity) continue;

    // Get entity centroid from D3 simulation
    const cx = entity.x ?? 0;
    const cy = entity.y ?? 0;

    // Find member nodes for this entity
    // A node "belongs" to an entity if that entity has activated it recently
    const memberNodes = nodes.filter(node => {
      const nodeId = node.id || node.node_id;
      if (!nodeId) return false;

      // Check if this entity has activated this node (entity_activations field)
      if (node.entity_activations && typeof node.entity_activations === 'object') {
        return entityId in node.entity_activations;
      }

      return false;
    });

    const memberCount = memberNodes.length;

    // Position each member using deterministic local layout
    memberNodes.forEach((node, idx) => {
      const nodeId = node.id || node.node_id!;

      // Determine primary entity (entity that "owns" this node for canonical placement)
      // For now, use first entity in entity_activations (TODO: should be highest activation)
      const primaryEntityId = node.entity_activations
        ? Object.keys(node.entity_activations)[0]
        : entityId;

      // Canonical node only in primary entity
      if (primaryEntityId === entityId) {
        const offset = layoutLocal(entityId, nodeId, idx, memberCount);

        rNodes.push({
          id: nodeId,
          x: cx + offset.x,
          y: cy + offset.y,
          r: nodeRadius(node),
          energy: node.energy || 0,
          kind: 'node',
          entityId: entityId,
          label: node.text || (node as any).name,
        });
      } else {
        // This is a multi-membership case: node's primary entity is elsewhere,
        // but this entity also activates it → create proxy
        const offset = layoutLocal(entityId, `${nodeId}::proxy::${entityId}`, idx, memberCount);

        rNodes.push({
          id: `${nodeId}::proxy::${entityId}`,
          x: cx + offset.x,
          y: cy + offset.y,
          r: proxyRadius,
          energy: node.energy || 0,
          kind: 'proxy',
          entityId: entityId,
          canonicalId: nodeId,
          label: undefined, // Proxies don't show labels
        });
      }
    });
  }

  // 3) EDGES
  // 3.a Node-level edges: drawn only if BOTH endpoints' entities are expanded
  for (const link of links) {
    const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
    const targetId = typeof link.target === 'string' ? link.target : link.target.id;

    const sourceNode = nodeMap.get(sourceId);
    const targetNode = nodeMap.get(targetId);

    if (!sourceNode || !targetNode) continue;

    // Determine primary entities for source and target
    const sourceEntityId = sourceNode.entity_activations
      ? Object.keys(sourceNode.entity_activations)[0]
      : undefined;
    const targetEntityId = targetNode.entity_activations
      ? Object.keys(targetNode.entity_activations)[0]
      : undefined;

    // Draw node-level edge only if both entities are expanded
    if (sourceEntityId && targetEntityId &&
        expandedEntities.has(sourceEntityId) &&
        expandedEntities.has(targetEntityId)) {

      // Get flow weight from linkFlows (if available)
      const linkId = link.id || `${sourceId}-${targetId}`;
      const flow = linkFlows.get(linkId) || 0;

      // Only show edges with flow > 0 (active edges)
      if (flow > 0) {
        const edgeKind = sourceEntityId === targetEntityId ? 'intra' : 'inter';

        rEdges.push({
          id: linkId,
          from: sourceId,
          to: targetId,
          w: flow,
          kind: edgeKind,
        });
      }
    }
  }

  // 3.b Entity-level edges: aggregated flows between entities
  // Draw only if NOT both expanded (prefer node edges when both expanded)
  const entityToEntity = new Map<string, number>();

  // Aggregate link flows by entity pairs
  for (const link of links) {
    const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
    const targetId = typeof link.target === 'string' ? link.target : link.target.id;

    const sourceNode = nodeMap.get(sourceId);
    const targetNode = nodeMap.get(targetId);

    if (!sourceNode || !targetNode) continue;

    const sourceEntityId = sourceNode.entity_activations
      ? Object.keys(sourceNode.entity_activations)[0]
      : undefined;
    const targetEntityId = targetNode.entity_activations
      ? Object.keys(targetNode.entity_activations)[0]
      : undefined;

    if (!sourceEntityId || !targetEntityId) continue;
    if (sourceEntityId === targetEntityId) continue; // Skip intra-entity for aggregation

    const linkId = link.id || `${sourceId}-${targetId}`;
    const flow = linkFlows.get(linkId) || 0;

    if (flow > 0) {
      const key = pairKey(sourceEntityId, targetEntityId);
      const currentFlow = entityToEntity.get(key) || 0;
      entityToEntity.set(key, currentFlow + flow);
    }
  }

  // Create entity-level edges from aggregated flows
  for (const [key, flow] of entityToEntity.entries()) {
    const [entityA, entityB] = key.split('|');

    // Only draw if NOT both expanded (prefer node edges in that case)
    if (!(expandedEntities.has(entityA) && expandedEntities.has(entityB))) {
      rEdges.push({
        id: `E|${key}`,
        from: entityA,
        to: entityB,
        w: flow,
        kind: 'entity',
      });
    }
  }

  // 4) LOD & meta
  const visibleNodeCount = rNodes.length;
  const hideNodeLabels = visibleNodeCount > LOD_HIDE_NODE_LABELS;

  return { nodes: rNodes, edges: rEdges, meta: { hideNodeLabels } };
}
