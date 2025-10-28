/**
 * SubEntity Mood Map Component
 *
 * The DEFAULT view for consciousness visualization.
 * Shows subentities as bubbles with emotion-based coloring.
 *
 * Per visualization_patterns.md § 2.1:
 * - SubEntities as bubbles, size ∝ energy
 * - Border weight ∝ coherence
 * - HSL color from subentity-level valence/arousal
 * - Labels: name + KPI chips (energy, coherence)
 * - Click to expand into member view
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 * Updated: 2025-10-24 - Fixed D3 enter/update/exit pattern to prevent flickering
 */

'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { emotionToHSL, hslToCSS } from '../lib/emotionColor';
import type { EmotionAxis } from '../hooks/websocket-types';

/**
 * SubEntity data structure (from tick_frame.v1 or snapshot.v1)
 */
export interface SubEntity {
  id: string;
  name: string;
  kind?: string;           // e.g., "functional", "identity"
  color?: string;          // Default color if no emotion
  energy: number;          // Derived/aggregated energy
  theta: number;           // Activation threshold
  active: boolean;
  members_count?: number;  // Number of member nodes
  coherence: number;       // Pattern coherence (0-1)
  emotion?: {
    valence: number;       // Aggregated from members
    arousal: number;       // Aggregated from members
    magnitude: number;
  };
  // D3 force simulation positions (added dynamically)
  x?: number;
  y?: number;
}

interface SubEntityMoodMapProps {
  subentities: SubEntity[];
  width: number;
  height: number;
  onSubEntityClick?: (subentityId: string) => void;
}

interface SubEntityNode extends d3.SimulationNodeDatum {
  id: string;
  subentity: SubEntity;
}

/**
 * SubEntity Mood Map
 *
 * D3 force-directed layout showing subentities as emotion-colored bubbles.
 * Uses proper enter/update/exit pattern to prevent flickering.
 */
export function SubEntityMoodMap({
  subentities,
  width,
  height,
  onSubEntityClick
}: SubEntityMoodMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<SubEntityNode, undefined> | null>(null);
  const nodesRef = useRef<Map<string, SubEntityNode>>(new Map());
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

  // Initialize SVG structure and simulation ONCE
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);

    // Create main group (only once)
    if (svg.select('g.subentities').empty()) {
      svg.append('g').attr('class', 'subentities');
    }

    const g = svg.select<SVGGElement>('g.subentities');

    // Create zoom behavior (only once)
    if (!zoomRef.current) {
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 4]) // Allow zoom from 10% to 400%
        .on('zoom', (event) => {
          g.attr('transform', event.transform);
        });

      svg.call(zoom);
      zoomRef.current = zoom;
    }

    // Create force simulation (only once)
    if (!simulationRef.current) {
      const simulation = d3.forceSimulation<SubEntityNode>()
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide<SubEntityNode>().radius(d => {
          const baseRadius = 30;
          const energyScale = Math.sqrt(d.subentity.energy || 0) * 20;
          return baseRadius + energyScale;
        }))
        .force('x', d3.forceX(width / 2).strength(0.05))
        .force('y', d3.forceY(height / 2).strength(0.05))
        .alphaDecay(0.01); // Slow decay for stable layout

      simulationRef.current = simulation;
    }

    return () => {
      // Cleanup simulation on unmount
      if (simulationRef.current) {
        simulationRef.current.stop();
        simulationRef.current = null;
      }
    };
  }, [width, height]);

  // Update subentities using enter/update/exit pattern
  useEffect(() => {
    if (!svgRef.current || !simulationRef.current) return;
    if (subentities.length === 0) return;

    const svg = d3.select(svgRef.current);
    const g = svg.select<SVGGElement>('g.subentities');
    const simulation = simulationRef.current;

    // Convert subentities to nodes, preserving existing positions
    const nodes: SubEntityNode[] = subentities.map(subentity => {
      const existing = nodesRef.current.get(subentity.id);
      if (existing) {
        // Update subentity data but preserve position
        return {
          ...existing,
          subentity
        };
      } else {
        // New subentity - initialize near center
        return {
          id: subentity.id,
          subentity,
          x: width / 2 + (Math.random() - 0.5) * 100,
          y: height / 2 + (Math.random() - 0.5) * 100
        };
      }
    });

    // Update nodes reference
    nodesRef.current.clear();
    nodes.forEach(node => nodesRef.current.set(node.id, node));

    // Update simulation nodes
    simulation.nodes(nodes);
    simulation.alpha(0.3).restart(); // Gentle restart to incorporate new nodes

    // D3 data join with KEY FUNCTION (crucial for stability)
    const subentityGroups = g.selectAll<SVGGElement, SubEntityNode>('g.subentity-bubble')
      .data(nodes, d => d.id); // KEY FUNCTION - tracks identity across renders

    // === ENTER: New subentities ===
    const subentityEnter = subentityGroups.enter()
      .append('g')
      .attr('class', 'subentity-bubble')
      .style('cursor', 'pointer')
      .style('opacity', 0) // Fade in
      .on('click', (event, d) => {
        event.stopPropagation();
        if (onSubEntityClick) {
          onSubEntityClick(d.id);
        }
      });

    // Add circle to new subentities
    subentityEnter.append('circle')
      .attr('class', 'subentity-background');

    // Add subentity name label
    subentityEnter.append('text')
      .attr('class', 'subentity-name')
      .attr('text-anchor', 'middle')
      .attr('dy', '-0.5em')
      .style('fill', '#e2e8f0')
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('pointer-events', 'none');

    // Add KPI chips group
    const kpiGroup = subentityEnter.append('g')
      .attr('class', 'kpi-chips')
      .attr('transform', 'translate(0, 12)');

    // Energy chip background
    kpiGroup.append('rect')
      .attr('class', 'energy-chip-bg')
      .attr('x', -25)
      .attr('y', 0)
      .attr('width', 22)
      .attr('height', 14)
      .attr('rx', 3)
      .style('fill', '#5efc82')
      .style('fill-opacity', 0.2);

    // Energy chip text
    kpiGroup.append('text')
      .attr('class', 'energy-chip-text')
      .attr('x', -14)
      .attr('y', 10)
      .attr('text-anchor', 'middle')
      .style('fill', '#5efc82')
      .style('font-size', '9px')
      .style('font-weight', '600')
      .style('pointer-events', 'none');

    // Coherence chip background
    kpiGroup.append('rect')
      .attr('class', 'coherence-chip-bg')
      .attr('x', 3)
      .attr('y', 0)
      .attr('width', 22)
      .attr('height', 14)
      .attr('rx', 3)
      .style('fill', '#3b82f6')
      .style('fill-opacity', 0.2);

    // Coherence chip text
    kpiGroup.append('text')
      .attr('class', 'coherence-chip-text')
      .attr('x', 14)
      .attr('y', 10)
      .attr('text-anchor', 'middle')
      .style('fill', '#3b82f6')
      .style('font-size', '9px')
      .style('font-weight', '600')
      .style('pointer-events', 'none');

    // Add member count label
    subentityEnter.append('text')
      .attr('class', 'member-count')
      .attr('text-anchor', 'middle')
      .attr('dy', '2.5em')
      .style('fill', '#94a3b8')
      .style('font-size', '10px')
      .style('pointer-events', 'none');

    // Fade in new subentities
    subentityEnter.transition()
      .duration(500)
      .style('opacity', 1);

    // === UPDATE: Existing subentities (enter + update) ===
    const subentityUpdate = subentityEnter.merge(subentityGroups);

    // Update circle
    subentityUpdate.select<SVGCircleElement>('circle.subentity-background')
      .transition()
      .duration(200)
      .attr('r', d => {
        const baseRadius = 30;
        const energyScale = Math.sqrt(d.subentity.energy || 0) * 20;
        return baseRadius + energyScale;
      })
      .attr('fill', d => {
        if (d.subentity.emotion && d.subentity.emotion.magnitude > 0.05) {
          const color = emotionToHSL(d.subentity.emotion.valence, d.subentity.emotion.arousal);
          return hslToCSS(color);
        }
        return d.subentity.color || '#1e293b';
      })
      .attr('opacity', 0.8)
      .attr('stroke', d => d.subentity.active ? '#5efc82' : '#64748b')
      .attr('stroke-width', d => {
        const coherence = d.subentity.coherence || 0;
        return 1 + coherence * 3;
      });

    // Update subentity name
    subentityUpdate.select<SVGTextElement>('text.subentity-name')
      .text(d => d.subentity.name);

    // Update energy chip
    subentityUpdate.select<SVGTextElement>('text.energy-chip-text')
      .text(d => `${(d.subentity.energy * 100).toFixed(0)}%`);

    // Update coherence chip
    subentityUpdate.select<SVGTextElement>('text.coherence-chip-text')
      .text(d => `${(d.subentity.coherence * 100).toFixed(0)}%`);

    // Update member count
    subentityUpdate.select<SVGTextElement>('text.member-count')
      .text(d => `${d.subentity.members_count || 0} members`);

    // === EXIT: Removed subentities ===
    subentityGroups.exit()
      .transition()
      .duration(500)
      .style('opacity', 0)
      .remove();

    // Update positions on simulation tick
    simulation.on('tick', () => {
      subentityUpdate.attr('transform', d => `translate(${d.x},${d.y})`);
    });

  }, [subentities, width, height, onSubEntityClick]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="subentity-mood-map"
      style={{ background: '#0f172a' }}
    >
      {/* Content rendered by D3 */}
    </svg>
  );
}
