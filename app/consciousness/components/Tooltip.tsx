'use client';

import { useEffect, useState } from 'react';
import type { Node, Link } from '../hooks/useGraphData';

interface TooltipState {
  visible: boolean;
  x: number;
  y: number;
  type: 'node' | 'link' | null;
  data: Node | Link | null;
}

/**
 * Tooltip Component
 *
 * Shows contextual information on hover for nodes and links.
 * Listens to custom events from GraphCanvas.
 */
export function Tooltip() {
  const [tooltip, setTooltip] = useState<TooltipState>({
    visible: false,
    x: 0,
    y: 0,
    type: null,
    data: null
  });

  useEffect(() => {
    const handleNodeHover = (e: Event) => {
      const customEvent = e as CustomEvent;
      const { node, event } = customEvent.detail;

      setTooltip({
        visible: true,
        x: event.clientX,
        y: event.clientY,
        type: 'node',
        data: node
      });
    };

    const handleLinkHover = (e: Event) => {
      const customEvent = e as CustomEvent;
      const { link, event } = customEvent.detail;

      setTooltip({
        visible: true,
        x: event.clientX,
        y: event.clientY,
        type: 'link',
        data: link
      });
    };

    const handleLeave = () => {
      setTooltip(prev => ({ ...prev, visible: false }));
    };

    window.addEventListener('node:hover', handleNodeHover);
    window.addEventListener('link:hover', handleLinkHover);
    window.addEventListener('node:leave', handleLeave);
    window.addEventListener('link:leave', handleLeave);

    return () => {
      window.removeEventListener('node:hover', handleNodeHover);
      window.removeEventListener('link:hover', handleLinkHover);
      window.removeEventListener('node:leave', handleLeave);
      window.removeEventListener('link:leave', handleLeave);
    };
  }, []);

  if (!tooltip.visible || !tooltip.data) return null;

  return (
    <div
      className="fixed z-50 consciousness-panel px-4 py-3 max-w-sm pointer-events-none"
      style={{
        left: tooltip.x + 15,
        top: tooltip.y + 15,
      }}
    >
      {tooltip.type === 'node' ? (
        <NodeTooltipContent node={tooltip.data as Node} />
      ) : (
        <LinkTooltipContent link={tooltip.data as Link} />
      )}
    </div>
  );
}

function NodeTooltipContent({ node }: { node: Node }) {
  // Use node_type (first label extracted by backend) instead of labels[0]
  // because FalkorDB returns labels as string "[Label]" not array
  const nodeType = node.node_type || 'Node';
  const energy = node.energy || 0;
  const confidence = node.confidence || 0;
  const traversals = node.traversal_count || 0;

  return (
    <>
      <div className="text-consciousness-green font-semibold text-sm mb-2">
        {nodeType}
      </div>

      <div className="text-gray-200 text-sm mb-3 max-w-xs break-words">
        {node.text || node.node_id || node.id}
      </div>

      <div className="space-y-1 text-xs">
        <div className="flex justify-between">
          <span className="text-gray-400">Energy:</span>
          <span className="text-gray-200">{(energy * 100).toFixed(0)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Confidence:</span>
          <span className="text-gray-200">{(confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Traversals:</span>
          <span className="text-gray-200">{traversals}</span>
        </div>
        {node.last_traversed_by && (
          <div className="flex justify-between">
            <span className="text-gray-400">Last entity:</span>
            <span className="text-gray-200">{node.last_traversed_by}</span>
          </div>
        )}
      </div>
    </>
  );
}

function LinkTooltipContent({ link }: { link: Link }) {
  const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
  const targetId = typeof link.target === 'object' ? link.target.id : link.target;
  const strength = link.strength || 0;
  const traversals = (link as any).traversal_count || 0;

  return (
    <>
      <div className="text-consciousness-green font-semibold text-sm mb-2">
        {link.type || 'Link'}
      </div>

      <div className="text-xs text-gray-400 mb-3">
        {sourceId} → {targetId}
      </div>

      <div className="space-y-1 text-xs">
        <div className="flex justify-between">
          <span className="text-gray-400">Strength:</span>
          <span className="text-gray-200">{(strength * 100).toFixed(0)}%</span>
        </div>
        {traversals > 0 && (
          <div className="flex justify-between">
            <span className="text-gray-400">Traversals:</span>
            <span className="text-gray-200">{traversals}</span>
          </div>
        )}
        {(link as any).last_entity && (
          <div className="flex justify-between">
            <span className="text-gray-400">Last entity:</span>
            <span className="text-gray-200">{(link as any).last_entity}</span>
          </div>
        )}
      </div>

      {/* Per-entity valences */}
      {link.sub_entity_valences && Object.keys(link.sub_entity_valences).length > 0 && (
        <div className="mt-3 pt-3 border-t border-consciousness-border">
          <div className="text-xs text-gray-400 mb-2">Per-Entity Experience:</div>
          <div className="space-y-1">
            {Object.entries(link.sub_entity_valences).slice(0, 3).map(([entityId, valence]) => (
              <div key={entityId} className="flex justify-between text-xs">
                <span className="text-gray-400">{entityId}:</span>
                <span style={{ color: getValenceColor(valence) }}>
                  {valence.toFixed(2)} {getValenceLabel(valence)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

function getValenceColor(valence: number): string {
  if (valence > 0.3) return '#22c55e';
  if (valence < -0.3) return '#ef4444';
  return '#94a3b8';
}

function getValenceLabel(valence: number): string {
  if (valence > 0.3) return '(positive)';
  if (valence < -0.3) return '(negative)';
  return '(neutral)';
}
