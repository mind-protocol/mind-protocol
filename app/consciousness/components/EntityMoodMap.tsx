/**
 * Entity Mood Map Component
 *
 * The DEFAULT view for consciousness visualization.
 * Shows entities as bubbles with emotion-based coloring.
 *
 * Per visualization_patterns.md § 2.1:
 * - Entities as bubbles, size ∝ energy
 * - Border weight ∝ coherence
 * - HSL color from entity-level valence/arousal
 * - Labels: name + KPI chips (energy, coherence)
 * - Click to expand into member view
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 */

'use client';

import { useEffect, useRef, useMemo } from 'react';
import * as d3 from 'd3';
import { emotionToHSL, hslToCSS } from '../lib/emotionColor';
import type { EmotionAxis } from '../hooks/websocket-types';

/**
 * Entity data structure (from tick_frame.v1 or snapshot.v1)
 */
export interface Entity {
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
}

interface EntityMoodMapProps {
  entities: Entity[];
  width: number;
  height: number;
  onEntityClick?: (entityId: string) => void;
}

interface EntityNode extends d3.SimulationNodeDatum {
  id: string;
  entity: Entity;
}

/**
 * Entity Mood Map
 *
 * D3 force-directed layout showing entities as emotion-colored bubbles.
 */
export function EntityMoodMap({
  entities,
  width,
  height,
  onEntityClick
}: EntityMoodMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<EntityNode, undefined> | null>(null);

  // Convert entities to D3 nodes
  const nodes = useMemo<EntityNode[]>(() => {
    return entities.map(entity => ({
      id: entity.id,
      entity,
      // Initialize positions near center with small random offset
      x: width / 2 + (Math.random() - 0.5) * 100,
      y: height / 2 + (Math.random() - 0.5) * 100
    }));
  }, [entities, width, height]);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);

    // Clear previous content
    svg.selectAll('*').remove();

    // Create main group
    const g = svg.append('g').attr('class', 'entities');

    // Create force simulation
    const simulation = d3.forceSimulation<EntityNode>(nodes)
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide<EntityNode>().radius(d => {
        // Collision radius based on energy
        const baseRadius = 30;
        const energyScale = Math.sqrt(d.entity.energy || 0) * 20;
        return baseRadius + energyScale;
      }))
      .force('x', d3.forceX(width / 2).strength(0.05))
      .force('y', d3.forceY(height / 2).strength(0.05))
      .alphaDecay(0.01); // Slow decay for stable layout

    simulationRef.current = simulation;

    // Create entity groups
    const entityGroups = g.selectAll<SVGGElement, EntityNode>('g.entity-bubble')
      .data(nodes)
      .join('g')
      .attr('class', 'entity-bubble')
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        if (onEntityClick) {
          onEntityClick(d.id);
        }
      });

    // Add emotion-colored circles
    entityGroups.append('circle')
      .attr('class', 'entity-background')
      .attr('r', d => {
        const baseRadius = 30;
        const energyScale = Math.sqrt(d.entity.energy || 0) * 20;
        return baseRadius + energyScale;
      })
      .attr('fill', d => {
        // If entity has emotion, use HSL coloring
        if (d.entity.emotion && d.entity.emotion.magnitude > 0.05) {
          const color = emotionToHSL(d.entity.emotion.valence, d.entity.emotion.arousal);
          return hslToCSS(color);
        }
        // Otherwise use default color or neutral
        return d.entity.color || '#1e293b';
      })
      .attr('opacity', 0.8)
      .attr('stroke', d => d.entity.active ? '#5efc82' : '#64748b')
      .attr('stroke-width', d => {
        // Border weight ∝ coherence (per spec)
        const coherence = d.entity.coherence || 0;
        return 1 + coherence * 3;
      });

    // Add entity name label
    entityGroups.append('text')
      .attr('class', 'entity-name')
      .attr('text-anchor', 'middle')
      .attr('dy', '-0.5em')
      .style('fill', '#e2e8f0')
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('pointer-events', 'none')
      .text(d => d.entity.name);

    // Add KPI chips
    const kpiGroup = entityGroups.append('g')
      .attr('class', 'kpi-chips')
      .attr('transform', 'translate(0, 12)');

    // Energy chip
    kpiGroup.append('rect')
      .attr('x', -25)
      .attr('y', 0)
      .attr('width', 22)
      .attr('height', 14)
      .attr('rx', 3)
      .style('fill', '#5efc82')
      .style('fill-opacity', 0.2);

    kpiGroup.append('text')
      .attr('x', -14)
      .attr('y', 10)
      .attr('text-anchor', 'middle')
      .style('fill', '#5efc82')
      .style('font-size', '9px')
      .style('font-weight', '600')
      .style('pointer-events', 'none')
      .text(d => `${(d.entity.energy * 100).toFixed(0)}%`);

    // Coherence chip
    kpiGroup.append('rect')
      .attr('x', 3)
      .attr('y', 0)
      .attr('width', 22)
      .attr('height', 14)
      .attr('rx', 3)
      .style('fill', '#3b82f6')
      .style('fill-opacity', 0.2);

    kpiGroup.append('text')
      .attr('x', 14)
      .attr('y', 10)
      .attr('text-anchor', 'middle')
      .style('fill', '#3b82f6')
      .style('font-size', '9px')
      .style('font-weight', '600')
      .style('pointer-events', 'none')
      .text(d => `${(d.entity.coherence * 100).toFixed(0)}%`);

    // Add member count label (bottom)
    entityGroups.append('text')
      .attr('class', 'member-count')
      .attr('text-anchor', 'middle')
      .attr('dy', '2.5em')
      .style('fill', '#94a3b8')
      .style('font-size', '10px')
      .style('pointer-events', 'none')
      .text(d => `${d.entity.members_count || 0} members`);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      entityGroups.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [nodes, width, height, onEntityClick]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="entity-mood-map"
      style={{ background: '#0f172a' }}
    >
      {/* Content rendered by D3 */}
    </svg>
  );
}
