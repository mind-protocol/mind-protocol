'use client';

import { useEffect, useState, useMemo } from 'react';
import type { Node } from '../hooks/useGraphData';
import type { SubEntityActivityEvent } from '../hooks/websocket-types';
import { getEntityColor } from '../design/tokens';

interface EnergyFlowParticlesProps {
  nodes: Node[];
  subentityActivity: SubEntityActivityEvent[];
}

interface Particle {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  entityColor: string;
  startTime: number;
  duration: number;
}

/**
 * EnergyFlowParticles - Layer 2: Energy Flow Visualization
 *
 * Shows particles moving along links when sub-entities traverse.
 * Uses real-time WebSocket subentity_activity events.
 *
 * Performance: Only animates recent events (last 2 seconds)
 *
 * Author: Iris "The Aperture"
 */
export function EnergyFlowParticles({ nodes, subentityActivity }: EnergyFlowParticlesProps) {
  const [particles, setParticles] = useState<Particle[]>([]);

  // Create node position lookup for fast access
  const nodePositions = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    nodes.forEach(node => {
      if (node.x && node.y) {
        map.set(node.id || node.node_id!, { x: node.x, y: node.y });
      }
    });
    return map;
  }, [nodes]);

  // Process new subentity activity events into particles
  useEffect(() => {
    if (subentityActivity.length === 0) return;

    const now = Date.now();
    const recentThreshold = 2000; // Only show particles for last 2 seconds
    const particleDuration = 500; // Particles travel for 500ms

    // Get the most recent activity event
    const latestEvent = subentityActivity[subentityActivity.length - 1];
    const eventTime = new Date(latestEvent.timestamp).getTime();

    // Only create particle if event is very recent
    if (now - eventTime > recentThreshold) return;

    // Find current node position
    const currentPos = nodePositions.get(latestEvent.current_node);
    if (!currentPos) return;

    // Find a connected node (target of the traversal)
    // We'll use a simple heuristic: find nodes recently activated by same subentity
    const targetNode = nodes.find(n => {
      if (!n.entity_activations || !n.x || !n.y) return false;
      const activation = n.entity_activations[latestEvent.subentity_id];
      if (!activation) return false;

      const lastActivated = (activation as any).last_activated;
      const nodeId = n.id || n.node_id;

      // Target is a node activated within last 100ms by same subentity (but not current node)
      return lastActivated &&
             (now - lastActivated) < 100 &&
             nodeId !== latestEvent.current_node;
    });

    if (!targetNode || !targetNode.x || !targetNode.y) return;

    // Create new particle
    const newParticle: Particle = {
      id: `${latestEvent.subentity_id}-${latestEvent.sequence_position}`,
      sourceX: currentPos.x,
      sourceY: currentPos.y,
      targetX: targetNode.x,
      targetY: targetNode.y,
      entityColor: getEntityColor(latestEvent.subentity_id),
      startTime: now,
      duration: particleDuration
    };

    setParticles(prev => {
      // Remove old particles (finished animating)
      const active = prev.filter(p => (now - p.startTime) < p.duration);
      // Add new particle
      return [...active, newParticle];
    });
    // NOTE: Only depend on subentityActivity - nodes/nodePositions changing during
    // D3 simulation ticks should NOT retrigger particle creation
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [subentityActivity]);

  // Clean up expired particles every second
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setParticles(prev => prev.filter(p => (now - p.startTime) < p.duration));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (particles.length === 0) return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      <svg className="w-full h-full">
        {particles.map(particle => (
          <EnergyParticle key={particle.id} particle={particle} />
        ))}
      </svg>
    </div>
  );
}

function EnergyParticle({ particle }: { particle: Particle }) {
  const [position, setPosition] = useState({ x: particle.sourceX, y: particle.sourceY });

  useEffect(() => {
    const startTime = particle.startTime;
    const duration = particle.duration;

    const animate = () => {
      const now = Date.now();
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Ease-out cubic for smooth deceleration
      const eased = 1 - Math.pow(1 - progress, 3);

      // Interpolate position
      const x = particle.sourceX + (particle.targetX - particle.sourceX) * eased;
      const y = particle.sourceY + (particle.targetY - particle.sourceY) * eased;

      setPosition({ x, y });

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    const animationFrame = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrame);
  }, [particle]);

  return (
    <g>
      {/* Particle glow */}
      <circle
        cx={position.x}
        cy={position.y}
        r={6}
        fill={particle.entityColor}
        opacity={0.3}
        filter="url(#particle-blur)"
      />
      {/* Particle core */}
      <circle
        cx={position.x}
        cy={position.y}
        r={3}
        fill={particle.entityColor}
        opacity={0.9}
      />
    </g>
  );
}
