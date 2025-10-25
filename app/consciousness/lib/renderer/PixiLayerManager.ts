// PixiLayerManager.ts
// Minimal scene manager with layers, object pools, and simple expand/collapse animations.
// Works with the render graph produced by visibleGraphSelector.
// Assumes PIXI v7. No external tween libs; a tiny in-house tweener is included.
//
// Author: Iris "The Aperture" (from Nicolas's reference implementation)
// Created: 2025-10-25

import * as PIXI from 'pixi.js';

type RenderNode = {
  id: string; x: number; y: number; r: number; energy: number;
  kind: 'entity'|'node'|'proxy'; label?: string; entityId?: string; canonicalId?: string;
};
type RenderEdge = { id: string; from: string; to: string; w: number; kind: 'entity'|'intra'|'inter' };

type RenderGraph = { nodes: RenderNode[]; edges: RenderEdge[]; meta?: { hideNodeLabels?: boolean } };

type SpriteBundle = {
  g: PIXI.Graphics;     // circle/line
  label?: PIXI.Text;    // optional
  kind: 'node'|'entity'|'proxy'|'edge';
};

export class PixiLayerManager {
  root: PIXI.Container;

  // The ordered layers (z-index increasing)
  entityLayer = new PIXI.Container();      // collapsed entity glyphs
  edgeEntityLayer = new PIXI.Container();  // entity-edges
  edgeNodeLayer = new PIXI.Container();    // node-edges
  nodeLayer = new PIXI.Container();        // canonical nodes
  proxyLayer = new PIXI.Container();       // proxies (UI only)
  haloLayer = new PIXI.Container();        // halos / selection
  labelLayer = new PIXI.Container();       // labels (togglable)

  // Pools & lookup
  nodeMap = new Map<string, SpriteBundle>();
  edgeMap = new Map<string, SpriteBundle>();

  // Small tweener list
  tweens: Array<{id:string; t0:number; dur:number; from:number; to:number; fn:(v:number)=>void; onDone?:()=>void}> = [];

  constructor(root: PIXI.Container) {
    this.root = root;
    // establish ordering
    this.entityLayer.zIndex = 10;
    this.edgeEntityLayer.zIndex = 20;
    this.edgeNodeLayer.zIndex = 30;
    this.nodeLayer.zIndex = 40;
    this.proxyLayer.zIndex = 45;
    this.haloLayer.zIndex = 50;
    this.labelLayer.zIndex = 60;

    [this.entityLayer, this.edgeEntityLayer, this.edgeNodeLayer, this.nodeLayer, this.proxyLayer, this.haloLayer, this.labelLayer]
      .forEach(c => { c.sortableChildren = true; this.root.addChild(c); });
  }

  // ---- Public API ----

  update(rg: RenderGraph) {
    this._applyNodes(rg.nodes, rg.meta?.hideNodeLabels ?? false);
    this._applyEdges(rg.edges, rg.nodes);
  }

  animate(dt: number) {
    // dt = elapsed ms from RAF; run tweens
    const now = performance.now();
    this.tweens = this.tweens.filter(t => {
      const p = Math.min(1, (now - t.t0) / t.dur);
      const v = t.from + (t.to - t.from) * easeOutCubic(p);
      t.fn(v);
      if (p >= 1) { t.onDone && t.onDone(); return false; }
      return true;
    });
  }

  // ---- Internals ----

  private _applyNodes(nodes: RenderNode[], hideLabels: boolean) {
    const seen = new Set<string>();
    // create/update
    for (const n of nodes) {
      seen.add(n.id);
      let bundle = this.nodeMap.get(n.id);
      if (!bundle) {
        bundle = this._createNodeBundle(n);
        this.nodeMap.set(n.id, bundle);
      }
      this._updateNodeBundle(bundle, n, hideLabels);
    }
    // remove stale
    for (const [id, b] of this.nodeMap) {
      if (!seen.has(id)) {
        this._removeNodeBundle(id, b);
      }
    }
  }

  private _createNodeBundle(n: RenderNode): SpriteBundle {
    const g = new PIXI.Graphics();
    g.eventMode = 'passive';
    // Layer routing
    const layer = n.kind === 'entity' ? this.entityLayer : n.kind === 'proxy' ? this.proxyLayer : this.nodeLayer;
    layer.addChild(g);

    // Optional label
    const label = n.kind !== 'proxy' ? new PIXI.Text(n.label ?? '', { fontSize: 11, fill: 0xbfc7d5 }) : undefined;
    if (label) this.labelLayer.addChild(label);

    // Simple appear animation
    g.alpha = 0;
    this._tween(`${n.id}/alpha`, 220, 0, 1, (v) => g.alpha = v);

    return { g, label, kind: n.kind };
  }

  private _updateNodeBundle(bundle: SpriteBundle, n: RenderNode, hideLabels: boolean) {
    const { g, label } = bundle;
    // Geometry
    g.clear();
    const fill = bundle.kind === 'entity' ? 0x7094ff
               : bundle.kind === 'proxy'  ? 0x7f9ab5
               : 0x9cc7ff;
    const line = bundle.kind === 'proxy' ? 0x9db3cf : 0x4a72cf;
    g.lineStyle(1, line, 0.7).beginFill(fill, 0.9).drawCircle(n.x, n.y, n.r).endFill();

    // Label
    if (label) {
      label.visible = !hideLabels && bundle.kind !== 'proxy';
      if (label.visible) {
        label.text = n.label ?? '';
        label.x = n.x + n.r + 4;
        label.y = n.y - 8;
      }
    }
  }

  private _removeNodeBundle(id: string, bundle: SpriteBundle) {
    // fade out then remove (tiny GC-safe tween)
    const g = bundle.g;
    const label = bundle.label;
    const layer = g.parent as PIXI.Container;
    const L = label?.parent as PIXI.Container | undefined;

    this._tween(`${id}/alpha-out`, 140, 1, 0, (v) => { g.alpha = v; if (label) label.alpha = v; }, () => {
      layer?.removeChild(g); g.destroy();
      if (label) { L?.removeChild(label); label.destroy(); }
      this.nodeMap.delete(id);
    });
  }

  private _applyEdges(edges: RenderEdge[], nodes: RenderNode[]) {
    const seen = new Set<string>();

    // Build position lookup from render nodes
    const posMap = new Map<string, {x: number; y: number}>();
    for (const n of nodes) {
      posMap.set(n.id, { x: n.x, y: n.y });
    }

    // Edges are many; draw entity edges as thicker semi-transparent lines,
    // node edges as hairlines (decimated by upstream).
    for (const e of edges) {
      seen.add(e.id);
      let b = this.edgeMap.get(e.id);
      if (!b) {
        b = { g: new PIXI.Graphics(), kind: 'edge' } as SpriteBundle;
        const layer = e.kind === 'entity' ? this.edgeEntityLayer : this.edgeNodeLayer;
        layer.addChild(b.g);
        this.edgeMap.set(e.id, b);
      }
      const g = b.g;

      // Lookup positions from render nodes
      const aPos = posMap.get(e.from);
      const bPos = posMap.get(e.to);
      if (!aPos || !bPos) continue;

      const ax = aPos.x;
      const ay = aPos.y;
      const bx = bPos.x;
      const by = bPos.y;

      g.clear();
      const color = e.kind === 'entity' ? 0x3f6ae8 : 0x7aa9ff;
      const alpha = e.kind === 'entity' ? Math.min(0.9, 0.25 + e.w * 0.5) : Math.min(0.8, 0.2 + e.w * 0.4);
      const width = e.kind === 'entity' ? Math.min(6, 1 + e.w * 4) : Math.min(2, 0.5 + e.w * 1.5);
      g.lineStyle(width, color, alpha).moveTo(ax, ay).lineTo(bx, by);
    }

    // Remove stale
    for (const [id, b] of this.edgeMap) {
      if (!seen.has(id)) {
        b.g.clear();
        b.g.parent?.removeChild(b.g);
        b.g.destroy();
        this.edgeMap.delete(id);
      }
    }
  }

  // ---- Tween helper ----
  private _tween(id: string, dur: number, from: number, to: number, fn: (v: number) => void, onDone?: () => void) {
    // Overwrite same-id tween
    this.tweens = this.tweens.filter(t => t.id !== id);
    this.tweens.push({ id, t0: performance.now(), dur, from, to, fn, onDone });
  }
}

function easeOutCubic(p: number) { return 1 - Math.pow(1 - p, 3); }
