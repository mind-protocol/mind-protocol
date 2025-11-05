/**
 * Node Event Indicators - Visual Feedback for Node-Level Events
 *
 * Provides visual indicators for:
 * - Threshold crossing notifications (#28) - flash when nodes cross activation threshold
 * - Weight learning indicators (#29) - flash when weights are updated
 * - Working memory selection (#30) - highlight selected nodes
 *
 * Author: Felix "The Engineer"
 * Created: 2025-11-05
 * Priority: Dashboard visualization (items 28-30)
 */

'use client';

import { useState, useEffect, useMemo } from 'react';
import type { Node } from '../hooks/useGraphData';

interface NodeFlipEvent {
  node_id: string;
  frame_id: number;
  timestamp: string;
  old_state: string; // "active" | "inactive"
  new_state: string; // "active" | "inactive"
  energy: number;
  threshold: number;
}

interface WeightUpdateEvent {
  frame_id: number;
  timestamp: string;
  link_id?: string;
  source_id?: string;
  target_id?: string;
  old_weight: number;
  new_weight: number;
  learning_delta: number;
}

interface WMSelectionEvent {
  frame_id: number;
  timestamp: string;
  selected_nodes: string[];
  capacity: number;
  selection_method?: string;
}

interface NodeEventIndicatorsProps {
  nodes: Node[];
  nodeFlipEvents: NodeFlipEvent[];
  weightUpdateEvents: WeightUpdateEvent[];
  wmSelectionEvents: WMSelectionEvent[];
}

interface FlashIndicator {
  nodeId: string;
  x: number;
  y: number;
  type: 'threshold_cross' | 'weight_learn';
  timestamp: number;
}

export default function NodeEventIndicators({
  nodes,
  nodeFlipEvents,
  weightUpdateEvents,
  wmSelectionEvents
}: NodeEventIndicatorsProps) {
  const [flashIndicators, setFlashIndicators] = useState<FlashIndicator[]>([]);

  // Create node position lookup
  const nodePositions = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    nodes.forEach(node => {
      if (node.x !== undefined && node.y !== undefined) {
        map.set(node.id || node.node_id!, { x: node.x, y: node.y });
      }
    });
    return map;
  }, [nodes]);

  // Get currently selected WM nodes
  const wmSelectedNodes = useMemo(() => {
    if (wmSelectionEvents.length === 0) return new Set<string>();
    const latest = wmSelectionEvents[wmSelectionEvents.length - 1];
    return new Set(latest.selected_nodes);
  }, [wmSelectionEvents]);

  // Process threshold crossing events (#28)
  useEffect(() => {
    if (nodeFlipEvents.length === 0) return;

    const latestFlip = nodeFlipEvents[nodeFlipEvents.length - 1];
    const pos = nodePositions.get(latestFlip.node_id);
    if (!pos) return;

    const flash: FlashIndicator = {
      nodeId: latestFlip.node_id,
      x: pos.x,
      y: pos.y,
      type: 'threshold_cross',
      timestamp: Date.now()
    };

    setFlashIndicators(prev => [...prev, flash]);

    // Remove flash after animation completes (800ms)
    setTimeout(() => {
      setFlashIndicators(prev => prev.filter(f => f.timestamp !== flash.timestamp));
    }, 800);
  }, [nodeFlipEvents, nodePositions]);

  // Process weight learning events (#29)
  useEffect(() => {
    if (weightUpdateEvents.length === 0) return;

    const latestUpdate = weightUpdateEvents[weightUpdateEvents.length - 1];

    // Flash both source and target nodes
    const nodeIds = [latestUpdate.source_id, latestUpdate.target_id].filter(Boolean) as string[];
    const now = Date.now();

    const flashes: FlashIndicator[] = nodeIds
      .map(nodeId => {
        const pos = nodePositions.get(nodeId);
        if (!pos) return null;
        return {
          nodeId,
          x: pos.x,
          y: pos.y,
          type: 'weight_learn' as const,
          timestamp: now
        };
      })
      .filter(Boolean) as FlashIndicator[];

    if (flashes.length > 0) {
      setFlashIndicators(prev => [...prev, ...flashes]);

      // Remove flashes after animation completes (600ms)
      setTimeout(() => {
        setFlashIndicators(prev =>
          prev.filter(f => f.timestamp !== now || f.type !== 'weight_learn')
        );
      }, 600);
    }
  }, [weightUpdateEvents, nodePositions]);

  // Clean up old flash indicators every second
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setFlashIndicators(prev => prev.filter(f => now - f.timestamp < 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <svg
      className="absolute inset-0 pointer-events-none"
      style={{ zIndex: 100 }}
    >
      {/* Threshold Crossing Flashes (#28) - Yellow expanding rings */}
      {flashIndicators
        .filter(f => f.type === 'threshold_cross')
        .map((flash, idx) => (
          <g key={`threshold-${flash.timestamp}-${idx}`}>
            <circle
              cx={flash.x}
              cy={flash.y}
              r={0}
              fill="none"
              stroke="rgba(250, 204, 21, 0.8)"
              strokeWidth={3}
            >
              <animate
                attributeName="r"
                from="8"
                to="40"
                dur="0.8s"
                begin="0s"
              />
              <animate
                attributeName="stroke-opacity"
                from="0.8"
                to="0"
                dur="0.8s"
                begin="0s"
              />
            </circle>
            {/* Inner bright flash */}
            <circle
              cx={flash.x}
              cy={flash.y}
              r={12}
              fill="rgba(250, 204, 21, 0.6)"
            >
              <animate
                attributeName="fill-opacity"
                from="0.6"
                to="0"
                dur="0.4s"
                begin="0s"
              />
            </circle>
          </g>
        ))}

      {/* Weight Learning Flashes (#29) - Purple pulse */}
      {flashIndicators
        .filter(f => f.type === 'weight_learn')
        .map((flash, idx) => (
          <g key={`weight-${flash.timestamp}-${idx}`}>
            <circle
              cx={flash.x}
              cy={flash.y}
              r={10}
              fill="rgba(168, 85, 247, 0.7)"
            >
              <animate
                attributeName="r"
                from="6"
                to="20"
                dur="0.6s"
                begin="0s"
              />
              <animate
                attributeName="fill-opacity"
                from="0.7"
                to="0"
                dur="0.6s"
                begin="0s"
              />
            </circle>
            {/* Inner spark */}
            <circle
              cx={flash.x}
              cy={flash.y}
              r={4}
              fill="rgba(255, 255, 255, 0.9)"
            >
              <animate
                attributeName="fill-opacity"
                from="0.9"
                to="0"
                dur="0.3s"
                begin="0s"
              />
            </circle>
          </g>
        ))}

      {/* Working Memory Selection Markers (#30) - Cyan halos */}
      {Array.from(wmSelectedNodes).map(nodeId => {
        const pos = nodePositions.get(nodeId);
        if (!pos) return null;
        return (
          <g key={`wm-${nodeId}`}>
            {/* Pulsing halo */}
            <circle
              cx={pos.x}
              cy={pos.y}
              r={14}
              fill="none"
              stroke="rgba(34, 211, 238, 0.6)"
              strokeWidth={2.5}
              className="animate-pulse"
            />
            {/* Inner glow */}
            <circle
              cx={pos.x}
              cy={pos.y}
              r={10}
              fill="rgba(34, 211, 238, 0.15)"
            />
            {/* Selection indicator */}
            <circle
              cx={pos.x}
              cy={pos.y - 18}
              r={3}
              fill="rgba(34, 211, 238, 1)"
            />
          </g>
        );
      })}
    </svg>
  );
}
