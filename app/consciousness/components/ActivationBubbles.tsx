'use client';

import { useState, useEffect } from 'react';
import type { Node } from '../hooks/useGraphData';
import type { NodeFlipRecord } from '../hooks/websocket-types';

interface ActivationBubblesProps {
  recentFlips: NodeFlipRecord[]; // V2: node.flip events
  nodes: Node[];
}

interface Bubble {
  id: string;
  x: number;
  y: number;
  message: string;
  type: 'traversal' | 'activation' | 'learning' | 'info';
  timestamp: number;
}

/**
 * ActivationBubbles
 *
 * Shows contextual event notifications WHERE they happen in the graph.
 * Plain language explanations appear near affected nodes.
 *
 * Design: Small bubbles fade in, float up slightly, fade out after 3s.
 * Message explains what happened in human terms.
 *
 * V2: Uses node.flip events from v2State.recentFlips
 */
export function ActivationBubbles({ recentFlips, nodes }: ActivationBubblesProps) {
  const [bubbles, setBubbles] = useState<Bubble[]>([]);

  // Process node flip events (v2)
  useEffect(() => {
    if (recentFlips.length === 0) return;

    // Process latest flip
    const latestFlip = recentFlips[recentFlips.length - 1];
    const bubble = createBubbleFromFlip(latestFlip, nodes);

    if (bubble) {
      setBubbles(prev => [bubble, ...prev.slice(0, 9)]); // Keep max 10 bubbles

      // Remove bubble after 3 seconds
      setTimeout(() => {
        setBubbles(prev => prev.filter(b => b.id !== bubble.id));
      }, 3000);
    }
  }, [recentFlips, nodes]);

  return (
    <div className="absolute inset-0 pointer-events-none">
      {bubbles.map(bubble => (
        <Bubble key={bubble.id} bubble={bubble} />
      ))}
    </div>
  );
}

function Bubble({ bubble }: { bubble: Bubble }) {
  const bgColor = {
    traversal: 'bg-blue-500',
    activation: 'bg-yellow-500',
    learning: 'bg-purple-500',
    info: 'bg-gray-500'
  }[bubble.type];

  const textColor = 'text-white';

  return (
    <div
      style={{
        position: 'absolute',
        left: bubble.x,
        top: bubble.y,
        transform: 'translate(-50%, -100%)',
        zIndex: 1000
      }}
      className="animate-bubble"
    >
      <div className={`${bgColor} ${textColor} px-3 py-1 rounded-full text-xs whitespace-nowrap shadow-lg`}>
        {bubble.message}
      </div>

      <style jsx>{`
        @keyframes bubble-float {
          0% {
            opacity: 0;
            transform: translate(-50%, -100%) translateY(0px);
          }
          10% {
            opacity: 1;
          }
          90% {
            opacity: 1;
          }
          100% {
            opacity: 0;
            transform: translate(-50%, -100%) translateY(-20px);
          }
        }
        .animate-bubble {
          animation: bubble-float 3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}

// ============================================================================
// Bubble Creation from Node Flips (V2)
// ============================================================================

function createBubbleFromFlip(flip: NodeFlipRecord, nodes: Node[]): Bubble | null {
  // Find node position
  const node = nodes.find(n => (n.id || n.node_id) === flip.node_id);

  if (!node || !node.x || !node.y) {
    return null;
  }

  // Create message based on flip direction
  let message = '';
  let bubbleType: Bubble['type'] = 'activation';

  if (flip.direction === 'on') {
    const nodeName = node.name || flip.node_id;
    message = `Activated: ${nodeName} (+${flip.dE.toFixed(2)} E)`;
    bubbleType = 'activation';
  } else {
    const nodeName = node.name || flip.node_id;
    message = `Deactivated: ${nodeName} (${flip.dE.toFixed(2)} E)`;
    bubbleType = 'info';
  }

  return {
    id: `${flip.timestamp}-${flip.node_id}`,
    x: node.x,
    y: node.y - 40, // Appear above node
    message,
    type: bubbleType,
    timestamp: flip.timestamp
  };
}
