/**
 * Visible Graph Selector
 *
 * Derives the renderable graph based on entity expansion state.
 * Implements two-layer entity/node visualization architecture.
 *
 * Architecture:
 * - Collapsed entities: Show as super-nodes with aggregated metrics
 * - Expanded entities: Show member nodes in local layout
 * - Edge routing: Node-level when both expanded, entity-level otherwise
 * - Multi-membership: Primary placement (entity_activations determines membership)
 *
 * Author: Felix "Ironhand"
 * Based on: Nicolas's two-layer graph architecture
 */

import type { Node, Link, Subentity } from '../hooks/useGraphData';

export interface RenderNode {
  id: string;
  x: number;
  y: number;
  r: number;
  energy: number;
  kind: 'entity' | 'node';
  entityId?: string;      // For member nodes: which entity they belong to
  memberCount?: number;   // For entity nodes: how many members
}

export interface RenderEdge {
  id: string;
  from: string;
  to: string;
  w: number;
  kind: 'entity' | 'node';
}

export interface VisibleGraph {
  nodes: RenderNode[];
  edges: RenderEdge[];
}

/**
 * Calculate which nodes and edges should be visible based on expansion state
 */
export function selectVisibleGraph(
  nodes: Node[],
  links: Link[],
  subentities: Subentity[],
  expandedEntities: Set<string>
): VisibleGraph {
  const renderNodes: RenderNode[] = [];
  const renderEdges: RenderEdge[] = [];

  // Build membership index: node.id -> Set<subentity_id>
  const membership = new Map<string, Set<string>>();
  for (const node of nodes) {
    const nodeId = node.id || node.node_id;
    if (!nodeId) continue;

    const memberships = new Set<string>();
    if (node.entity_activations && typeof node.entity_activations === 'object') {
      Object.keys(node.entity_activations).forEach(entityId => {
        memberships.add(entityId);
      });
    }
    membership.set(nodeId, memberships);
  }

  // Build entity member lists
  const entityMembers = new Map<string, Node[]>();
  for (const entity of subentities) {
    const members: Node[] = [];
    for (const node of nodes) {
      const nodeId = node.id || node.node_id;
      if (!nodeId) continue;

      const nodeMemberships = membership.get(nodeId);
      if (nodeMemberships?.has(entity.subentity_id)) {
        members.push(node);
      }
    }
    entityMembers.set(entity.subentity_id, members);
  }

  // Calculate entity positions (simple grid layout for now)
  const entityPositions = new Map<string, { x: number; y: number }>();
  const gridSize = Math.ceil(Math.sqrt(subentities.length));
  const spacing = 400;
  subentities.forEach((entity, index) => {
    const row = Math.floor(index / gridSize);
    const col = index % gridSize;
    entityPositions.set(entity.subentity_id, {
      x: col * spacing + 200,
      y: row * spacing + 200
    });
  });

  // 1) Add entity super-nodes (only for collapsed entities)
  for (const entity of subentities) {
    if (!expandedEntities.has(entity.subentity_id)) {
      const members = entityMembers.get(entity.subentity_id) || [];
      const pos = entityPositions.get(entity.subentity_id) || { x: 0, y: 0 };

      // Aggregate energy from members
      const totalEnergy = members.reduce((sum, n) => sum + (parseFloat(String(n.energy || 0)) || 0), 0);
      const avgEnergy = members.length > 0 ? totalEnergy / members.length : 0;

      renderNodes.push({
        id: entity.subentity_id,
        x: pos.x,
        y: pos.y,
        r: 30 + Math.min(members.length * 0.5, 30), // Size based on member count
        energy: avgEnergy,
        kind: 'entity',
        memberCount: members.length
      });
    }
  }

  // 2) Add member nodes (only for expanded entities)
  for (const entity of subentities) {
    if (expandedEntities.has(entity.subentity_id)) {
      const members = entityMembers.get(entity.subentity_id) || [];
      const entityPos = entityPositions.get(entity.subentity_id) || { x: 0, y: 0 };

      // Simple radial layout around entity center
      const radius = 150;
      members.forEach((node, index) => {
        const nodeId = node.id || node.node_id;
        if (!nodeId) return;

        const angle = (index / members.length) * 2 * Math.PI;
        const x = entityPos.x + radius * Math.cos(angle);
        const y = entityPos.y + radius * Math.sin(angle);

        renderNodes.push({
          id: nodeId,
          x,
          y,
          r: 8 + (parseFloat(String(node.energy || 0)) || 0) * 0.1,
          energy: parseFloat(String(node.energy || 0)) || 0,
          kind: 'node',
          entityId: entity.subentity_id
        });
      });
    }
  }

  // 3) Add edges (routing based on expansion state)
  // For now, simplified: only show node-level edges when both entities expanded
  for (const link of links) {
    const sourceNode = nodes.find(n => (n.id || n.node_id) === link.source);
    const targetNode = nodes.find(n => (n.id || n.node_id) === link.target);

    if (!sourceNode || !targetNode) continue;

    const sourceId = sourceNode.id || sourceNode.node_id;
    const targetId = targetNode.id || targetNode.node_id;
    if (!sourceId || !targetId) continue;

    // Get primary entities for source and target
    const sourceMemberships = membership.get(sourceId);
    const targetMemberships = membership.get(targetId);

    if (!sourceMemberships?.size || !targetMemberships?.size) continue;

    // Use first membership as primary (simplified - should use primary_entity field)
    const sourceEntity = Array.from(sourceMemberships)[0];
    const targetEntity = Array.from(targetMemberships)[0];

    // Both entities expanded -> show node-level edge
    if (expandedEntities.has(sourceEntity) && expandedEntities.has(targetEntity)) {
      renderEdges.push({
        id: link.id,
        from: sourceId,
        to: targetId,
        w: link.weight || 1,
        kind: 'node'
      });
    }
    // At least one collapsed -> aggregate to entity-level edge (TODO)
    // For now, skip aggregated edges - will implement in next iteration
  }

  return { nodes: renderNodes, edges: renderEdges };
}
