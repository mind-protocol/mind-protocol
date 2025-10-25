// visibleGraphSelector.ts
// Produces the renderable graph for the current expansion state.
// - Canonical node lives in its primary entity
// - Additional memberships appear as PROXY sprites (UI-only)
// - Node-edges show only when BOTH endpoint entities expanded
// - Otherwise edges contribute to aggregated entity->entity metric
// - Designed for 10 Hz updates (decimated WS)
//
// Author: Iris "The Aperture" (from Nicolas's reference implementation)
// Created: 2025-10-25

import { createSelector } from 'reselect';

// ======== Types ========

export type Node = {
  id: string;
  label: string;
  type: string;
  E: number;                 // 0..100 (engine units)
  theta: number;             // 0..100
  primary_entity?: string;   // placement owner
  entities?: string[];       // all memberships (incl. primary)
};

export type Entity = {
  id: string;
  name: string;
  cx: number;                // world coords for entity centroid
  cy: number;
  members: string[];         // node ids (can be partial/lazy)
  E: number;                 // aggregated energy (for size/halo)
};

export type Link = {
  id: string;
  source: string;            // node id
  target: string;            // node id
  w: number;                 // static weight (0..1 or similar)
};

export type GraphState = {
  // canonical graph
  nodes: Record<string, Node>;
  entities: Record<string, Entity>;
  links: Record<string, Link>;
  memberships: Record<string, Set<string>>; // nodeId -> set(entityId)

  // UI state
  expandedEntities: Set<string>;

  // incremental flow aggregation between entities (A|B -> strength)
  entityToEntity: Record<string, number>;
};

export type RenderNode = {
  id: string;
  x: number; y: number;
  r: number;                 // radius in pixels
  energy: number;            // 0..100 (we normalize in shader)
  kind: "entity" | "node" | "proxy";
  entityId?: string;         // container owner (for nodes/proxies)
  canonicalId?: string;      // for proxies: link to canonical
  label?: string;
};

export type RenderEdge = {
  id: string;
  from: string; to: string;  // ids in the current render set
  w: number;                 // for stroke width/alpha mapping
  kind: "entity" | "intra" | "inter";
};

// ======== Helpers ========

const entityRadius = (e: Entity) =>
  24 + Math.min(16, (e.E || 0) * 0.2);   // quick visual; tune as you like
const nodeRadius   = (n: Node) =>
  6 + Math.min(10, (n.E || 0) * 0.08);
const proxyRadius  = 3.5;

const pairKey = (a: string, b: string) => (a < b ? `${a}|${b}` : `${b}|${a}`);

// Deterministic local layout inside an entity container.
// Fast hex/radial packing seeded by nodeId to avoid re-layout thrash.
// Cache per (entityId, nodeId).
const localLayoutCache: Map<string, Map<string, { x: number; y: number }>> = new Map();

function layoutLocal(entityId: string, nodeId: string, idx: number, count: number, radius = 120): { x: number; y: number } {
  let eCache = localLayoutCache.get(entityId);
  if (!eCache) { eCache = new Map(); localLayoutCache.set(entityId, eCache); }
  const cached = eCache.get(nodeId);
  if (cached) return cached;

  // radial slots
  const ringSize = Math.max(1, Math.ceil(Math.sqrt(count)));
  const ring = Math.floor(idx / ringSize) + 1;
  const posInRing = idx % ringSize;
  const angle = (posInRing / ringSize) * Math.PI * 2;
  const r = (radius / (1 + Math.log2(1 + count / 50))) * (0.35 + 0.65 * (ring / ringSize));
  const x = Math.cos(angle) * r;
  const y = Math.sin(angle) * r;
  const res = { x, y };
  eCache.set(nodeId, res);
  return res;
}

// ======== Selector ========

// LOD: hide node labels above these thresholds
const LOD_HIDE_NODE_LABELS = 3000;

export const visibleGraphSelector = createSelector(
  [
    (s: GraphState) => s.nodes,
    (s: GraphState) => s.entities,
    (s: GraphState) => s.links,
    (s: GraphState) => s.memberships,
    (s: GraphState) => s.expandedEntities,
    (s: GraphState) => s.entityToEntity,
  ],
  (nodes, entities, links, memberships, expanded, entityAgg): { nodes: RenderNode[]; edges: RenderEdge[]; meta: { hideNodeLabels: boolean } } => {
    const rNodes: RenderNode[] = [];
    const rEdges: RenderEdge[] = [];

    // 1) ENTITY SUPER-NODES (draw only if collapsed)
    for (const e of Object.values(entities)) {
      if (!expanded.has(e.id)) {
        rNodes.push({
          id: e.id,
          x: e.cx, y: e.cy,
          r: entityRadius(e),
          energy: e.E || 0,
          kind: "entity",
          label: e.name,
        });
      }
    }

    // 2) EXPANDED ENTITIES → INNER NODES + PROXIES
    for (const eid of expanded) {
      const e = entities[eid];
      if (!e) continue;
      const members = e.members || [];
      const count = members.length;

      members.forEach((nid, i) => {
        const n = nodes[nid];
        if (!n) return;

        // Canonical node only in primary entity
        if (n.primary_entity === eid) {
          const p = layoutLocal(eid, n.id, i, count);
          rNodes.push({
            id: n.id,
            x: e.cx + p.x, y: e.cy + p.y,
            r: nodeRadius(n),
            energy: n.E || 0,
            kind: "node",
            entityId: eid,
            label: n.label,
          });
        }

        // Proxies for other memberships (UI only, not part of physics or edges)
        const mset = memberships[nid];
        if (mset && mset.size > 1) {
          for (const other of mset) {
            if (other !== eid && expanded.has(other)) {
              const p2 = layoutLocal(other, `${nid}::proxy::${other}`, i, count);
              const e2 = entities[other];
              if (!e2) continue;
              rNodes.push({
                id: `${nid}::proxy::${other}`,
                x: e2.cx + p2.x, y: e2.cy + p2.y,
                r: proxyRadius,
                energy: nodes[nid].E || 0,
                kind: "proxy",
                entityId: other,
                canonicalId: nid,
                label: undefined,
              });
            }
          }
        }
      });
    }

    // 3) EDGES
    // 3.a Node-level edges: drawn only if BOTH endpoints' entities are expanded
    for (const L of Object.values(links)) {
      const a = nodes[L.source]; const b = nodes[L.target];
      if (!a || !b) continue;
      const ea = a.primary_entity, eb = b.primary_entity;
      if (ea && eb && expanded.has(ea) && expanded.has(eb)) {
        rEdges.push({
          id: L.id,
          from: a.id, to: b.id,
          w: L.w,
          kind: "intra",
        });
      }
    }

    // 3.b Entity-level edges: aggregated flows; draw only if NOT both expanded
    for (const [key, val] of Object.entries(entityAgg)) {
      const [A, B] = key.split("|");
      if (!entities[A] || !entities[B]) continue;
      // if both expanded we prefer node edges; else draw super-edge
      if (!(expanded.has(A) && expanded.has(B))) {
        rEdges.push({
          id: `E|${key}`,
          from: A, to: B,
          w: val,
          kind: "entity",
        });
      }
    }

    // 4) LOD & meta
    const visibleNodeCount = rNodes.length;
    const hideNodeLabels = visibleNodeCount > LOD_HIDE_NODE_LABELS;

    return { nodes: rNodes, edges: rEdges, meta: { hideNodeLabels } };
  }
);
