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
 * Updated: 2025-10-24 - Fixed D3 enter/update/exit pattern to prevent flickering
 */

'use client';

import { useEffect, useRef } from 'react';
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
 * Uses proper enter/update/exit pattern to prevent flickering.
 */
export function EntityMoodMap({
  entities,
  width,
  height,
  onEntityClick
}: EntityMoodMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<EntityNode, undefined> | null>(null);
  const nodesRef = useRef<Map<string, EntityNode>>(new Map());

  // Initialize SVG structure and simulation ONCE
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);

    // Create main group (only once)
    if (svg.select('g.entities').empty()) {
      svg.append('g').attr('class', 'entities');
    }

    // Create force simulation (only once)
    if (!simulationRef.current) {
      const simulation = d3.forceSimulation<EntityNode>()
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide<EntityNode>().radius(d => {
          const baseRadius = 30;
          const energyScale = Math.sqrt(d.entity.energy || 0) * 20;
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

  // Update entities using enter/update/exit pattern
  useEffect(() => {
    if (!svgRef.current || !simulationRef.current) return;
    if (entities.length === 0) return;

    const svg = d3.select(svgRef.current);
    const g = svg.select<SVGGElement>('g.entities');
    const simulation = simulationRef.current;

    // Convert entities to nodes, preserving existing positions
    const nodes: EntityNode[] = entities.map(entity => {
      const existing = nodesRef.current.get(entity.id);
      if (existing) {
        // Update entity data but preserve position
        return {
          ...existing,
          entity
        };
      } else {
        // New entity - initialize near center
        return {
          id: entity.id,
          entity,
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
    const entityGroups = g.selectAll<SVGGElement, EntityNode>('g.entity-bubble')
      .data(nodes, d => d.id); // KEY FUNCTION - tracks identity across renders

    // === ENTER: New entities ===
    const entityEnter = entityGroups.enter()
      .append('g')
      .attr('class', 'entity-bubble')
      .style('cursor', 'pointer')
      .style('opacity', 0) // Fade in
      .on('click', (event, d) => {
        event.stopPropagation();
        if (onEntityClick) {
          onEntityClick(d.id);
        }
      });

    // Add circle to new entities
    entityEnter.append('circle')
      .attr('class', 'entity-background');

    // Add entity name label
    entityEnter.append('text')
      .attr('class', 'entity-name')
      .attr('text-anchor', 'middle')
      .attr('dy', '-0.5em')
      .style('fill', '#e2e8f0')
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('pointer-events', 'none');

    // Add KPI chips group
    const kpiGroup = entityEnter.append('g')
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
    entityEnter.append('text')
      .attr('class', 'member-count')
      .attr('text-anchor', 'middle')
      .attr('dy', '2.5em')
      .style('fill', '#94a3b8')
      .style('font-size', '10px')
      .style('pointer-events', 'none');

    // Fade in new entities
    entityEnter.transition()
      .duration(500)
      .style('opacity', 1);

    // === UPDATE: Existing entities (enter + update) ===
    const entityUpdate = entityEnter.merge(entityGroups);

    // Update circle
    entityUpdate.select<SVGCircleElement>('circle.entity-background')
      .transition()
      .duration(200)
      .attr('r', d => {
        const baseRadius = 30;
        const energyScale = Math.sqrt(d.entity.energy || 0) * 20;
        return baseRadius + energyScale;
      })
      .attr('fill', d => {
        if (d.entity.emotion && d.entity.emotion.magnitude > 0.05) {
          const color = emotionToHSL(d.entity.emotion.valence, d.entity.emotion.arousal);
          return hslToCSS(color);
        }
        return d.entity.color || '#1e293b';
      })
      .attr('opacity', 0.8)
      .attr('stroke', d => d.entity.active ? '#5efc82' : '#64748b')
      .attr('stroke-width', d => {
        const coherence = d.entity.coherence || 0;
        return 1 + coherence * 3;
      });

    // Update entity name
    entityUpdate.select<SVGTextElement>('text.entity-name')
      .text(d => d.entity.name);

    // Update energy chip
    entityUpdate.select<SVGTextElement>('text.energy-chip-text')
      .text(d => `${(d.entity.energy * 100).toFixed(0)}%`);

    // Update coherence chip
    entityUpdate.select<SVGTextElement>('text.coherence-chip-text')
      .text(d => `${(d.entity.coherence * 100).toFixed(0)}%`);

    // Update member count
    entityUpdate.select<SVGTextElement>('text.member-count')
      .text(d => `${d.entity.members_count || 0} members`);

    // === EXIT: Removed entities ===
    entityGroups.exit()
      .transition()
      .duration(500)
      .style('opacity', 0)
      .remove();

    // Update positions on simulation tick
    simulation.on('tick', () => {
      entityUpdate.attr('transform', d => `translate(${d.x},${d.y})`);
    });

  }, [entities, width, height, onEntityClick]);

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
