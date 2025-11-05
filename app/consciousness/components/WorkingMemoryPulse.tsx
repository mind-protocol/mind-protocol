'use client';

import { useMemo } from 'react';
import type { Node } from '../hooks/useGraphData';

interface WorkingMemoryPulseProps {
  workingMemory: Set<string>; // Node IDs in working memory
  nodes: Node[];
}

/**
 * WorkingMemoryPulse - Visual indicator for nodes in working memory
 *
 * Shows a pulsing ring around nodes currently in working memory.
 * Uses CSS animation for smooth, continuous pulse (1800ms breathing cycle).
 *
 * Design: Subtle cyan glow that doesn't overwhelm the graph but clearly
 * indicates "this node is in focus right now."
 *
 * Author: Iris "The Aperture"
 */
export function WorkingMemoryPulse({ workingMemory, nodes }: WorkingMemoryPulseProps) {
  // Find positions for nodes in working memory
  const wmNodes = useMemo(() => {
    if (workingMemory.size === 0) return [];

    return nodes
      .filter(n => {
        const nodeId = n.id || n.node_id;
        return nodeId && workingMemory.has(nodeId) && n.x && n.y;
      })
      .map(n => ({
        id: n.id || n.node_id!,
        x: n.x!,
        y: n.y!,
        name: n.name
      }));
  }, [workingMemory, nodes]);

  if (wmNodes.length === 0) return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      <svg className="w-full h-full">
        <defs>
          {/* Pulsing glow filter */}
          <filter id="wm-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
            <feFlood floodColor="#22d3ee" floodOpacity="0.6" />
            <feComposite in2="blur" operator="in" result="glow" />
            <feMerge>
              <feMergeNode in="glow" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {wmNodes.map(node => (
          <g key={node.id}>
            {/* Outer pulsing ring */}
            <circle
              cx={node.x}
              cy={node.y}
              r={16}
              fill="none"
              stroke="#22d3ee"
              strokeWidth={2}
              opacity={0.6}
              filter="url(#wm-glow)"
              className="wm-pulse-ring"
            />
            {/* Inner subtle ring */}
            <circle
              cx={node.x}
              cy={node.y}
              r={12}
              fill="none"
              stroke="#6FE7E2"
              strokeWidth={1}
              opacity={0.4}
              className="wm-pulse-inner"
            />
          </g>
        ))}
      </svg>

      <style jsx>{`
        @keyframes wm-breathing {
          0%, 100% {
            r: 16;
            opacity: 0.6;
          }
          50% {
            r: 20;
            opacity: 0.3;
          }
        }

        @keyframes wm-inner-breathing {
          0%, 100% {
            r: 12;
            opacity: 0.4;
          }
          50% {
            r: 14;
            opacity: 0.2;
          }
        }

        .wm-pulse-ring {
          animation: wm-breathing 1800ms ease-in-out infinite;
        }

        .wm-pulse-inner {
          animation: wm-inner-breathing 1800ms ease-in-out infinite;
          animation-delay: 300ms;
        }
      `}</style>
    </div>
  );
}
