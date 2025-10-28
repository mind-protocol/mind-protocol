'use client';

import { useState, useEffect } from 'react';
import type { Node, Operation } from '../hooks/useGraphData';
import type { ThresholdCrossingEvent } from '../hooks/websocket-types';

interface ActivationBubblesProps {
  operations: Operation[];
  nodes: Node[];
  thresholdCrossings?: ThresholdCrossingEvent[];
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
 */
export function ActivationBubbles({ operations, nodes, thresholdCrossings = [] }: ActivationBubblesProps) {
  const [bubbles, setBubbles] = useState<Bubble[]>([]);

  // Process operations (legacy support)
  useEffect(() => {
    if (operations.length === 0) return;

    // Process latest operation
    const latestOp = operations[0];
    const bubble = createBubbleFromOperation(latestOp, nodes);

    if (bubble) {
      setBubbles(prev => [bubble, ...prev.slice(0, 9)]); // Keep max 10 bubbles

      // Remove bubble after 3 seconds
      setTimeout(() => {
        setBubbles(prev => prev.filter(b => b.id !== bubble.id));
      }, 3000);
    }
  }, [operations, nodes]);

  // Process threshold crossings (real-time WebSocket events)
  useEffect(() => {
    if (thresholdCrossings.length === 0) return;

    // Process latest threshold crossing
    const latestCrossing = thresholdCrossings[thresholdCrossings.length - 1];
    const bubble = createBubbleFromThresholdCrossing(latestCrossing, nodes);

    if (bubble) {
      setBubbles(prev => [bubble, ...prev.slice(0, 9)]); // Keep max 10 bubbles

      // Remove bubble after 3 seconds
      setTimeout(() => {
        setBubbles(prev => prev.filter(b => b.id !== bubble.id));
      }, 3000);
    }
  }, [thresholdCrossings, nodes]);

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
    traversal: 'bg-consciousness-green/90',
    activation: 'bg-blue-500/90',
    learning: 'bg-purple-500/90',
    info: 'bg-gray-600/90'
  }[bubble.type];

  return (
    <div
      className={`absolute ${bgColor} text-white text-xs px-3 py-2 rounded-lg shadow-lg
                  animate-[float_3s_ease-out_forwards] opacity-0`}
      style={{
        left: bubble.x,
        top: bubble.y,
        transform: 'translate(-50%, -50%)',
        animation: 'float 3s ease-out forwards',
      }}
    >
      {bubble.message}

      <style jsx>{`
        @keyframes float {
          0% {
            opacity: 0;
            transform: translate(-50%, -50%) translateY(0);
          }
          20% {
            opacity: 1;
          }
          80% {
            opacity: 1;
            transform: translate(-50%, -50%) translateY(-20px);
          }
          100% {
            opacity: 0;
            transform: translate(-50%, -50%) translateY(-30px);
          }
        }
      `}</style>
    </div>
  );
}

// ============================================================================
// Bubble Creation from Operations
// ============================================================================

function createBubbleFromOperation(operation: Operation, nodes: Node[]): Bubble | null {
  const { type, node_id, subentity_id, data } = operation;

  // Find node position
  let node: Node | undefined;
  if (node_id) {
    node = nodes.find(n => n.id === node_id);
  }

  if (!node || !node.x || !node.y) {
    return null;
  }

  let message = '';
  let bubbleType: Bubble['type'] = 'info';

  switch (type) {
    case 'entity_traversal':
      message = `${subentity_id} traversed here`;
      bubbleType = 'traversal';
      break;

    case 'activation_increase':
      const energy = data?.energy?.toFixed(2) || '?';
      message = `Energy increased to ${energy}`;
      bubbleType = 'activation';
      break;

    case 'hebbian_learning':
      message = `Link strengthened`;
      bubbleType = 'learning';
      break;

    case 'node_created':
      message = `New node created`;
      bubbleType = 'info';
      break;

    default:
      message = `${type}`;
      bubbleType = 'info';
  }

  return {
    id: `${operation.timestamp}-${Math.random()}`,
    x: node.x,
    y: node.y - 40, // Appear above node
    message,
    type: bubbleType,
    timestamp: operation.timestamp
  };
}

function createBubbleFromThresholdCrossing(
  event: ThresholdCrossingEvent,
  nodes: Node[]
): Bubble | null {
  // Find node position
  const node = nodes.find(n => n.id === event.node_id);

  if (!node || !node.x || !node.y) {
    return null;
  }

  // Create message based on direction
  let message = '';
  let bubbleType: Bubble['type'] = 'activation';

  if (event.direction === 'on') {
    message = `${event.subentity_id}: activated "${event.node_name}"`;
    bubbleType = 'activation';
  } else {
    message = `${event.subentity_id}: deactivated "${event.node_name}"`;
    bubbleType = 'info';
  }

  return {
    id: `${event.timestamp}-${event.node_id}-${Math.random()}`,
    x: node.x,
    y: node.y - 40, // Appear above node
    message,
    type: bubbleType,
    timestamp: new Date(event.timestamp).getTime()
  };
}
