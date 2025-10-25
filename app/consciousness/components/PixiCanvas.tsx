/**
 * PixiCanvas - React wrapper for PixiRenderer
 *
 * Strangler pattern: Drop-in replacement for GraphCanvas
 * - Same props interface
 * - Same event emissions (for tooltips/panels)
 * - Better performance (60fps with 2500+ nodes)
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import { PixiRenderer } from '../lib/renderer/PixiRenderer';
import type { RendererAdapter, ViewModel } from '../lib/renderer/types';
import type { Node, Link, Operation } from '../hooks/useGraphData';

interface PixiCanvasProps {
  nodes: Node[];
  links: Link[];
  operations: Operation[];
  subentities?: { entity_id: string; name?: string }[];
  selectedSubentity?: string;
  workingMemory?: Set<string>;
  linkFlows?: Map<string, number>;
  recentFlips?: Array<{ node_id: string; direction: 'on' | 'off'; dE: number; timestamp: number }>;
}

export function PixiCanvas({
  nodes,
  links,
  operations,
  subentities = [],
  selectedSubentity = 'structural',
  workingMemory,
  linkFlows,
  recentFlips,
}: PixiCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<RendererAdapter | null>(null);
  const [stats, setStats] = useState({ fps: 0, nodeCount: 0, linkCount: 0 });

  // Initialize renderer on mount
  useEffect(() => {
    if (!containerRef.current) return;

    const renderer = new PixiRenderer({
      showStats: true,
      enableCulling: false, // Will add in Phase 4
      enableLOD: false,
    });

    rendererRef.current = renderer;
    renderer.mount(containerRef.current);

    return () => {
      renderer.unmount();
      rendererRef.current = null;
    };
  }, []);

  // Update data when nodes/links change
  useEffect(() => {
    if (!rendererRef.current) return;

    const viewModel: ViewModel = {
      nodes: nodes.map((n) => ({
        id: n.id || n.node_id!,
        name: n.text || (n as any).name || 'Unknown',
        node_type: n.node_type || 'Unknown',
        description: (n as any).description,
        weight: n.weight,
        energy: n.energy,
        last_active: n.last_active,
        last_traversal_time: n.last_traversal_time,
        traversal_count: n.traversal_count,
        entity_activations: n.entity_activations,
        x: n.x,
        y: n.y,
      })),
      links: links.map((l) => ({
        id: l.id || `${l.source}-${l.target}`,
        source: typeof l.source === 'object' ? l.source.id : l.source,
        target: typeof l.target === 'object' ? l.target.id : l.target,
        type: l.type,
        strength: (l as any).strength,
        valence: (l as any).valence,
        confidence: (l as any).confidence,
        created_at: (l as any).created_at,
        last_traversal: (l as any).last_traversal,
        traversal_count: (l as any).traversal_count,
      })),
      subentities: subentities.map((e) => ({
        entity_id: e.entity_id,
        name: e.name,
      })),
      operations: operations as any,
      selectedSubentity,
      workingMemory,
      linkFlows,
      recentFlips,
    };

    rendererRef.current.setData(viewModel);

    // Update stats display
    const stats = rendererRef.current.getStats();
    setStats({
      fps: stats.fps,
      nodeCount: stats.nodeCount,
      linkCount: stats.linkCount,
    });
  }, [nodes, links, subentities, selectedSubentity, workingMemory, linkFlows, recentFlips]); // operations excluded - changes too frequently

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current && rendererRef.current) {
        const { clientWidth, clientHeight } = containerRef.current;
        rendererRef.current.resize(clientWidth, clientHeight);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle hover/click events (emit same events as GraphCanvas for tooltip compatibility)
  useEffect(() => {
    const container = containerRef.current;
    if (!container || !rendererRef.current) return;

    const handlePointerMove = (e: PointerEvent) => {
      if (!rendererRef.current) return;

      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const result = rendererRef.current.pick(x, y);

      if (result.type === 'node') {
        const customEvent = new CustomEvent('node:hover', {
          detail: { node: result.data, event: e },
        });
        window.dispatchEvent(customEvent);
      } else if (result.type === 'link') {
        const customEvent = new CustomEvent('link:hover', {
          detail: { link: result.data, event: e },
        });
        window.dispatchEvent(customEvent);
      } else {
        window.dispatchEvent(new CustomEvent('node:leave'));
        window.dispatchEvent(new CustomEvent('link:leave'));
      }
    };

    const handleClick = (e: PointerEvent) => {
      if (!rendererRef.current) return;

      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const result = rendererRef.current.pick(x, y);

      if (result.type === 'node') {
        const customEvent = new CustomEvent('node:click', {
          detail: { node: result.data, event: e },
        });
        window.dispatchEvent(customEvent);
      }
    };

    container.addEventListener('pointermove', handlePointerMove);
    container.addEventListener('click', handleClick);

    return () => {
      container.removeEventListener('pointermove', handlePointerMove);
      container.removeEventListener('click', handleClick);
    };
  }, []);

  return (
    <div className="relative w-full h-full" style={{ transform: 'translateX(-256px)' }}>
      {/* PixiJS canvas container - offset left to center in available space (chat panel right) */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Stats overlay (debugging) */}
      {stats.fps > 0 && (
        <div className="absolute top-4 left-4 bg-black/50 text-white text-xs p-2 rounded font-mono">
          <div>FPS: {stats.fps}</div>
          <div>Nodes: {stats.nodeCount}</div>
          <div>Links: {stats.linkCount}</div>
          <div className="text-cyan-400 mt-1">⚡ WebGL</div>
        </div>
      )}
    </div>
  );
}
