"use client";

import { useEffect, useRef } from "react";
import * as PIXI from "pixi.js";
import { useGraphStream } from "../hooks/useGraphStream";
import { useWebSocket } from "../hooks/useWebSocket";

type G = PIXI.Graphics;

const DPR = typeof window !== "undefined" ? window.devicePixelRatio || 1 : 1;

// Node type to color mapping (hex colors)
const NODE_TYPE_COLORS: Record<string, number> = {
  // Generic
  Node: 0x60a5fa,          // blue-400 (most common generic type)

  // Consciousness types
  Citizen: 0x22d3ee,       // cyan-400
  SubEntity: 0x06b6d4,     // cyan-500

  // Knowledge types
  Mechanism: 0xa855f7,     // purple-500
  Principle: 0x3b82f6,     // blue-500
  Realization: 0xfbbf24,   // yellow-400
  Concept: 0x60a5fa,       // blue-400
  Pattern: 0x8b5cf6,       // violet-500

  // Quality/Process
  Best_Practice: 0x10b981, // emerald-500
  Anti_Pattern: 0xef4444,  // red-500
  Decision: 0x8b5cf6,      // violet-500
  Process: 0xf59e0b,       // amber-500

  // Artifacts
  Code: 0x6366f1,          // indigo-500
  Documentation: 0x14b8a6, // teal-500
  File: 0x64748b,          // slate-500

  // People/Org
  Team: 0xec4899,          // pink-500
  Person: 0xf97316,        // orange-500
  Role: 0xf472b6,          // pink-400

  // Memory/Context
  Memory: 0xc084fc,        // purple-400
  Context: 0xa78bfa,       // purple-400
  Experience: 0xfcd34d,    // yellow-300

  default: 0x60a5fa        // blue-400 (changed from slate to blue for visibility)
};

function getNodeTypeColor(nodeType: string): number {
  // Log unique node types we encounter (only in development)
  if (typeof window !== 'undefined' && !window.hasOwnProperty('_seenNodeTypes')) {
    (window as any)._seenNodeTypes = new Set();
  }
  if ((window as any)._seenNodeTypes && !((window as any)._seenNodeTypes as Set<string>).has(nodeType)) {
    ((window as any)._seenNodeTypes as Set<string>).add(nodeType);
    console.log('[GraphPixi] New node type:', nodeType);
  }

  return NODE_TYPE_COLORS[nodeType] || NODE_TYPE_COLORS.default;
}

// simple, deterministic coord if none provided (no physics yet)
function hashPos(id: string, w: number, h: number) {
  let h1 = 2166136261;
  for (let i = 0; i < id.length; i++) h1 = (h1 ^ id.charCodeAt(i)) * 16777619;
  const cols = Math.max(1, Math.floor(w / 28));
  const idx = Math.abs(h1) % (cols * Math.floor(h / 28) || 1);
  const x = 40 + (idx % cols) * 28;
  const y = 40 + Math.floor(idx / cols) * 28;
  return { x, y };
}

export default function GraphPixi() {
  const { graphs, currentGraphId } = useGraphStream();
  const { v2State } = useWebSocket();
  const hostRef = useRef<HTMLDivElement | null>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const layerNodes = useRef<PIXI.Container | null>(null);
  const layerLinks = useRef<PIXI.Container | null>(null);
  const spritePool = useRef<Map<string, G>>(new Map());
  const linePool = useRef<Map<string, G>>(new Map());
  const rafIdRef = useRef<number | null>(null);
  const lastRenderRef = useRef<number>(0);

  // mount once
  useEffect(() => {
    if (!hostRef.current || appRef.current) return;

    const app = new PIXI.Application({
      antialias: true,
      backgroundAlpha: 0,
      autoDensity: true,
      resolution: DPR,
      powerPreference: "high-performance",
      resizeTo: hostRef.current,
    });

    const nodesLayer = new PIXI.Container();
    const linksLayer = new PIXI.Container();
    linksLayer.zIndex = 0;
    nodesLayer.zIndex = 1;
    const root = new PIXI.Container();
    root.sortableChildren = true;
    root.addChild(linksLayer, nodesLayer);
    app.stage.addChild(root);

    hostRef.current.appendChild(app.view as any);
    appRef.current = app;
    layerNodes.current = nodesLayer;
    layerLinks.current = linksLayer;

    return () => {
      app.destroy(true, { children: true, texture: true, baseTexture: true });
      appRef.current = null;
      layerNodes.current = null;
      layerLinks.current = null;
      spritePool.current.clear();
      linePool.current.clear();
    };
  }, []);

  // apply data on graph changes (throttled via RAF to prevent flickering)
  useEffect(() => {
    const app = appRef.current;
    if (!app) return;

    // Cancel any pending RAF
    if (rafIdRef.current !== null) {
      cancelAnimationFrame(rafIdRef.current);
    }

    // Schedule render on next frame
    rafIdRef.current = requestAnimationFrame((timestamp) => {
      // Throttle to max 60fps (16ms between renders)
      if (timestamp - lastRenderRef.current < 16) {
        // Schedule for next frame
        rafIdRef.current = requestAnimationFrame(() => render(timestamp));
        return;
      }
      lastRenderRef.current = timestamp;
      render(timestamp);
    });

    function render(timestamp: number) {
      const app = appRef.current;
      if (!app) return;
      const W = app.renderer.width / DPR;
      const H = app.renderer.height / DPR;

      // Get current graph data
      const currentGraph = currentGraphId ? graphs.get(currentGraphId) : null;
      if (!currentGraph) {
        console.log('[GraphPixi] No current graph');
        return;
      }

      // Convert Maps to objects for bracket notation access
      const nodes = currentGraph.nodes instanceof Map
        ? Object.fromEntries(currentGraph.nodes)
        : (currentGraph.nodes || {});
      const links = currentGraph.links instanceof Map
        ? Object.fromEntries(currentGraph.links)
        : (currentGraph.links || {});

      console.log('[GraphPixi] Rendering:', {
        graphId: currentGraphId,
        nodeCount: Object.keys(nodes).length,
        linkCount: Object.keys(links).length,
        canvasSize: { W, H }
      });

    // ---- nodes ----
    const usedNodes = new Set<string>();
    let drawn = 0;
    for (const [id, n] of Object.entries(nodes)) {
      usedNodes.add(id);
      let g = spritePool.current.get(id);
      if (!g) {
        g = new PIXI.Graphics();
        g.eventMode = "passive"; // we can enable interactivity later
        (layerNodes.current as PIXI.Container).addChild(g);
        spritePool.current.set(id, g);
      }
      // position
      const x = Number.isFinite(n.x) ? n.x : hashPos(id, W, H).x;
      const y = Number.isFinite(n.y) ? n.y : hashPos(id, W, H).y;

      // draw (mutate; don't recreate graphics)
      g.clear();

      // Check for recent activation (node flipped within last 500ms)
      const now = Date.now();
      const recentFlip = v2State.recentFlips.find(
        f => f.node_id === id && (now - f.timestamp) < 500
      );
      const justActivated = !!recentFlip;

      // Working Memory highlighting: bright gold with glow for WM nodes
      const inWM = v2State.workingMemory.has(id);

      // Determine base visual style from node properties
      const nodeType = n.node_type || 'default';
      const nodeEnergy = n.energy || n.energy_runtime || 0;
      const nodeWeight = n.weight || n.log_weight || 0;
      const traversals = n.traversal_count || 0;

      // Base color by node type
      let color = getNodeTypeColor(nodeType);

      // Base radius from weight + energy + traversals
      const baseRadius = 4;
      const weightFactor = Math.min(Math.max(nodeWeight, 0), 2); // 0-2
      const energyFactor = Math.min(Math.max(nodeEnergy / 10, 0), 1); // 0-1
      const traversalFactor = Math.min(Math.max(traversals / 100, 0), 1); // 0-1
      let radius = baseRadius * (0.8 + 0.4*weightFactor + 0.3*energyFactor + 0.3*traversalFactor);
      radius = Math.max(3, Math.min(12, radius)); // clamp 3-12px

      let glowRadius = 0;
      let glowAlpha = 0;

      // Override for dynamic states
      if (justActivated) {
        // PULSING: nodes that just flipped get bright pulse
        const pulseProgress = (now - recentFlip.timestamp) / 500; // 0 to 1 over 500ms
        const pulseIntensity = 1 - pulseProgress; // fade out
        color = recentFlip.direction === 'on' ? 0x00FF00 : 0xFF6B6B; // green=on, red=off
        radius = radius + pulseIntensity * 3; // grow then shrink
        glowRadius = 12 + pulseIntensity * 8; // expanding glow
        glowAlpha = pulseIntensity * 0.5;
      } else if (inWM) {
        // WM nodes: bright gold with glow (overlay on base color)
        color = 0xFFD700;
        radius = Math.max(radius, 8); // ensure WM nodes are visible
        glowRadius = 12;
        glowAlpha = 0.3;
      }

      // Draw glow if present
      if (glowRadius > 0) {
        g.beginFill(color, glowAlpha);
        g.drawCircle(0, 0, glowRadius);
        g.endFill();
      }

      // Draw main node
      g.beginFill(color, 1);
      g.drawCircle(0, 0, radius);
      g.endFill();

      g.x = x;
      g.y = y;

      if (++drawn > 1500) break; // cap for 60fps; raise later
    }
    // remove stale node sprites
    for (const [id, g] of spritePool.current) {
      if (!usedNodes.has(id)) {
        g.destroy();
        spritePool.current.delete(id);
      }
    }

    // ---- links (lightweight) ----
    const visibleTypes = new Set([
      "U4_MEMBER_OF",
      "U4_RELATED_TO",
      "U4_DEPENDS_ON",
      "U4_EVIDENCED_BY",
      "U4_GOVERNS",
      "U4_UNLOCKS",
    ]);
    const usedLinks = new Set<string>();
    let drawnL = 0;
    for (const [id, l] of Object.entries(links)) {
      if (!visibleTypes.has(l.type)) continue;
      let g = linePool.current.get(id);
      if (!g) {
        g = new PIXI.Graphics();
        (layerLinks.current as PIXI.Container).addChild(g);
        linePool.current.set(id, g);
      }
      const from = nodes[l.source];
      const to = nodes[l.target];
      if (!from || !to) {
        g.clear();
        continue;
      }
      const { x: x1, y: y1 } =
        Number.isFinite(from.x) && Number.isFinite(from.y)
          ? from
          : hashPos(l.source, W, H);
      const { x: x2, y: y2 } =
        Number.isFinite(to.x) && Number.isFinite(to.y)
          ? to
          : hashPos(l.target, W, H);

      // Dynamic link thickness based on weight and flow
      const baseWeight = l.weight || 0.5; // 0-1 range from graph data
      const flowAmount = v2State.linkFlows.get(id) || 0; // real-time flow count

      // Thickness: 1-6px based on weight (0.5-1.0) + flow boost
      let thickness = 1 + (baseWeight * 3); // 1-4px base
      if (flowAmount > 0) {
        thickness += Math.min(flowAmount / 5, 2); // +0-2px for active flow
      }
      thickness = Math.max(0.5, Math.min(thickness, 6)); // clamp to 0.5-6px

      // Color: brighter when flowing
      let color = 0x7aa7c7; // default blue-gray
      let alpha = 0.6;
      if (flowAmount > 0) {
        color = 0x00D4FF; // bright cyan for active links
        alpha = 0.8 + Math.min(flowAmount / 20, 0.2); // up to 100% opacity
      }

      g.clear();
      g.lineStyle(thickness, color, alpha);
      g.moveTo(x1, y1);
      g.lineTo(x2, y2);

      usedLinks.add(id);
      if (++drawnL > 3000) break; // cap; tune later
    }
    for (const [id, g] of linePool.current) {
      if (!usedLinks.has(id)) {
        g.destroy();
        linePool.current.delete(id);
      }
    }
    } // end render()

    // Cleanup: cancel RAF on unmount or dependency change
    return () => {
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
        rafIdRef.current = null;
      }
    };
  }, [graphs, currentGraphId, v2State]);

  return (
    <div
      ref={hostRef}
      className="graph-pane"
      style={{ width: "100%", height: "100%", overflow: "hidden" }}
    />
  );
}
