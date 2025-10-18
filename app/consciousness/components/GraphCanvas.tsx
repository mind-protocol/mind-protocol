'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import type { Node, Link, Operation } from '../hooks/useGraphData';

interface GraphCanvasProps {
  nodes: Node[];
  links: Link[];
  operations: Operation[];
}

/**
 * GraphCanvas - D3 Force-Directed Graph Visualization
 *
 * Renders consciousness substrate as interactive graph.
 * Emoji-based nodes, valence-colored links, real-time updates.
 *
 * Visual encodings:
 * - Emoji = Node type
 * - Size = Weight (arousal + confidence + traversals)
 * - Glow = Recent activity
 * - Link color = Type (structural) or Valence (entity view)
 * - Link thickness = Hebbian strength
 */
export function GraphCanvas({ nodes, links, operations }: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedEntity, setSelectedEntity] = useState<string>('structural');

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = window.innerWidth;
    const height = window.innerHeight;

    // Clear previous content
    svg.selectAll('*').remove();

    const g = svg.append('g');

    // Define arrow markers for links
    const defs = svg.append('defs');

    // Type-based arrows
    ['JUSTIFIES', 'BUILDS_TOWARD', 'ENABLES', 'USES', 'default'].forEach(type => {
      defs.append('marker')
        .attr('id', `arrow-${type}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 25)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', getLinkTypeColor(type));
    });

    // Valence-based arrow (for entity view)
    defs.append('marker')
      .attr('id', 'arrow-valence')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#94a3b8');

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 10])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom as any);

    // Force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(links)
        .id((d: any) => d.id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(35));

    // Render links
    const linkElements = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', d => getLinkColor(d, selectedEntity))
      .attr('stroke-width', d => Math.max(2.5, (d.strength || 0.5) * 6))
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', d => `url(#arrow-${d.type || 'default'})`)
      .style('cursor', 'pointer')
      .on('mouseenter', (event, d) => {
        // Emit event for tooltip
        const customEvent = new CustomEvent('link:hover', { detail: { link: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseleave', () => {
        const customEvent = new CustomEvent('link:leave');
        window.dispatchEvent(customEvent);
      });

    // Render nodes (emojis as SVG text - better browser compatibility)
    const nodeElements = g.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .style('cursor', 'pointer')
      .style('filter', d => getNodeGlow(d))
      .style('user-select', 'none')
      .style('pointer-events', 'all')
      .style('font-family', '"Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif')
      .style('text-anchor', 'middle')
      .style('dominant-baseline', 'central')
      .attr('font-size', d => getNodeSize(d) * 0.7)
      .text(d => getNodeEmoji(d))
      .call(drag(simulation) as any)
      .on('click', (event, d) => {
        event.stopPropagation();
        // Emit event for detail panel
        const customEvent = new CustomEvent('node:click', { detail: { node: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseenter', (event, d) => {
        // Emit event for tooltip
        const customEvent = new CustomEvent('node:hover', { detail: { node: d, event } });
        window.dispatchEvent(customEvent);
      })
      .on('mouseleave', () => {
        const customEvent = new CustomEvent('node:leave');
        window.dispatchEvent(customEvent);
      });

    // Simulation tick
    simulation.on('tick', () => {
      linkElements
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      nodeElements
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    // Start simulation
    simulation.alpha(0.3).restart();

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [nodes, links, selectedEntity]);

  // Handle node focus from CLAUDE_DYNAMIC.md clicks
  useEffect(() => {
    const handleNodeFocus = (e: Event) => {
      const customEvent = e as CustomEvent;
      const { nodeId } = customEvent.detail;

      // Find the node
      const node = nodes.find(n => n.id === nodeId || n.node_id === nodeId);
      if (!node || !node.x || !node.y || !svgRef.current) return;

      const svg = d3.select(svgRef.current);
      const g = svg.select('g');

      // Center view on node with smooth transition
      const width = window.innerWidth;
      const height = window.innerHeight;

      const scale = 1.5; // Zoom in a bit
      const x = -node.x * scale + width / 2;
      const y = -node.y * scale + height / 2;

      g.transition()
        .duration(750)
        .attr('transform', `translate(${x},${y}) scale(${scale})`);

      // Highlight node temporarily
      svg.selectAll('text')
        .filter((d: any) => d.id === nodeId || d.node_id === nodeId)
        .transition()
        .duration(300)
        .style('filter', 'drop-shadow(0 0 16px #5efc82) drop-shadow(0 0 8px #5efc82)')
        .transition()
        .delay(1000)
        .duration(500)
        .style('filter', (d: any) => getNodeGlow(d));
    };

    window.addEventListener('node:focus', handleNodeFocus);

    return () => {
      window.removeEventListener('node:focus', handleNodeFocus);
    };
  }, [nodes]);

  return (
    <svg
      ref={svgRef}
      className="w-full h-full"
      style={{ background: '#14181c' }}
    />
  );
}

// ============================================================================
// Visual Encoding Functions
// ============================================================================

function getNodeEmoji(node: Node): string {
  const nodeType = (node.labels && node.labels[0]) || 'Node';
  const EMOJIS: Record<string, string> = {
    // N1 - Personal/Individual Consciousness
    'Memory': '💭',
    'Conversation': '💬',
    'Person': '👤',
    'Relationship': '🤝',
    'Personal_Goal': '🎯',
    'Personal_Value': '💎',
    'Personal_Pattern': '🔄',
    'Realization': '💡',
    'Wound': '🩹',
    'Coping_Mechanism': '🛡️',
    'Trigger': '⚡',
    // N2 - Organizational Consciousness
    'Human': '🧑',
    'AI_Agent': '🤖',
    'Team': '👥',
    'Department': '🏢',
    'Decision': '⚖️',
    'Project': '📋',
    'Task': '✅',
    'Milestone': '🏆',
    'Best_Practice': '✨',
    'Anti_Pattern': '⚠️',
    'Risk': '🔴',
    'Metric': '📊',
    'Process': '⚙️',
    // N2/N3 - Conceptual Knowledge
    'Concept': '🧩',
    'Principle': '📜',
    'Mechanism': '🔧',
    'Document': '📄',
    'Documentation': '📖',
    // N3 - Ecosystem Intelligence (External)
    'Company': '🏛️',
    'External_Person': '👔',
    'Wallet_Address': '💰',
    'Social_Media_Account': '📱',
    // N3 - Evidence Nodes
    'Post': '📝',
    'Transaction': '💸',
    'Deal': '🤝',
    'Event': '📅',
    'Smart_Contract': '📜',
    'Integration': '🔗',
    // N3 - Derived Intelligence
    'Psychological_Trait': '🧠',
    'Behavioral_Pattern': '🔁',
    'Market_Signal': '📈',
    'Reputation_Assessment': '⭐',
    'Network_Cluster': '🕸️',
    // Fallback
    'default': '⚪'
  };
  return EMOJIS[nodeType] || EMOJIS['default'];
}

function getNodeSize(node: Node): number {
  const weight = computeNodeWeight(node);
  return Math.max(24, 16 + weight * 16); // 24-32px
}

function computeNodeWeight(node: Node): number {
  const arousal = node.arousal || 0;
  const confidence = node.confidence || 0.5;
  const traversalCount = node.traversal_count || 0;
  const normalizedTraversals = Math.min(1.0, Math.log10(traversalCount + 1) / 2);
  return (arousal * 0.4) + (confidence * 0.3) + (normalizedTraversals * 0.3);
}

function getNodeGlow(node: Node): string {
  // Glow for recently active nodes (last 2 minutes)
  if (node.last_active) {
    const age = Date.now() - node.last_active;
    if (age < 120000) { // 2 minutes = 120000ms
      // Fade glow intensity over time
      const intensity = 1 - (age / 120000);
      const glowSize = 4 + (intensity * 8); // 4px to 12px
      return `drop-shadow(0 0 ${glowSize}px rgba(94, 252, 130, ${intensity})) drop-shadow(0 0 ${glowSize/2}px rgba(94, 252, 130, ${intensity * 0.8}))`;
    }
  }
  return 'none';
}

function getLinkColor(link: Link, selectedEntity: string): string {
  if (selectedEntity === 'structural') {
    return getLinkTypeColor(link.type);
  } else {
    // Valence-based coloring
    const valences = link.sub_entity_valences || {};
    const valence = valences[selectedEntity];
    return getValenceColor(valence);
  }
}

function getLinkTypeColor(type: string): string {
  const COLORS: Record<string, string> = {
    'JUSTIFIES': '#ef4444',
    'BUILDS_TOWARD': '#3b82f6',
    'ENABLES': '#22c55e',
    'USES': '#8b5cf6',
    'default': '#666'
  };
  return COLORS[type] || COLORS['default'];
}

function getValenceColor(valence: number | undefined): string {
  if (valence === null || valence === undefined) return '#64748b';

  const normalized = (valence + 1.0) / 2.0;

  if (normalized < 0.5) {
    const t = normalized * 2;
    return d3.interpolateRgb('#ef4444', '#94a3b8')(t); // Red to gray
  } else {
    const t = (normalized - 0.5) * 2;
    return d3.interpolateRgb('#94a3b8', '#22c55e')(t); // Gray to green
  }
}

// ============================================================================
// Drag Behavior
// ============================================================================

function drag(simulation: d3.Simulation<any, undefined>) {
  function dragstarted(event: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event: any) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event: any) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended);
}
