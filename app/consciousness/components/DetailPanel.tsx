'use client';

import { useEffect, useState, useMemo } from 'react';
import type { Node, Link } from '../hooks/useGraphData';
import { useWebSocket } from '../hooks/useWebSocket';
import { AttributionCard } from './AttributionCard';

interface DetailPanelProps {
  nodes: Node[];
  links: Link[];
}

/**
 * DetailPanel Component
 *
 * Shows detailed information for selected node.
 * Appears on right side when node is clicked.
 */
export function DetailPanel({ nodes, links }: DetailPanelProps) {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const { emotionState } = useWebSocket();

  // Find most recent stride involving this node
  const mostRecentStride = useMemo(() => {
    if (!selectedNode) return null;

    // Find strides where this node is source or target
    const relevantStrides = emotionState.recentStrides.filter(stride =>
      stride.source_node_id === selectedNode.id || stride.target_node_id === selectedNode.id
    );

    // Return most recent one (last in array)
    return relevantStrides.length > 0 ? relevantStrides[relevantStrides.length - 1] : null;
  }, [selectedNode, emotionState.recentStrides]);

  // Get edge emotion for the most recent stride
  const strideEdgeEmotion = useMemo(() => {
    if (!mostRecentStride) return undefined;
    return emotionState.linkEmotions.get(mostRecentStride.link_id);
  }, [mostRecentStride, emotionState.linkEmotions]);

  useEffect(() => {
    const handleNodeClick = (e: Event) => {
      const customEvent = e as CustomEvent;
      const { node } = customEvent.detail;
      setSelectedNode(node);
    };

    const handleClose = () => {
      setSelectedNode(null);
    };

    window.addEventListener('node:click', handleNodeClick);
    window.addEventListener('detail:close', handleClose);

    return () => {
      window.removeEventListener('node:click', handleNodeClick);
      window.removeEventListener('detail:close', handleClose);
    };
  }, []);

  if (!selectedNode) return null;

  // Find connected links and deduplicate
  const connectedLinks = links.filter(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    return sourceId === selectedNode.id || targetId === selectedNode.id;
  });

  // Deduplicate: prefer known types over UNKNOWN
  const deduplicateLinks = (linkList: Link[]) => {
    const seen = new Map<string, Link>();
    for (const link of linkList) {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      const key = `${sourceId}→${targetId}`;

      const existing = seen.get(key);
      if (!existing || (existing.type === 'UNKNOWN' && link.type !== 'UNKNOWN')) {
        seen.set(key, link);
      }
    }
    return Array.from(seen.values());
  };

  const incomingLinks = deduplicateLinks(
    connectedLinks.filter(link => {
      const targetId = typeof link.target === 'object' ? link.target.id : link.target;
      return targetId === selectedNode.id;
    })
  );

  const outgoingLinks = deduplicateLinks(
    connectedLinks.filter(link => {
      const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
      return sourceId === selectedNode.id;
    })
  );

  // Use node_type instead of labels[0] (FalkorDB returns labels as string)
  const rawNodeType = selectedNode.node_type || 'Node';
  // Format node type: convert to title case if all lowercase
  const nodeType = rawNodeType === rawNodeType.toLowerCase()
    ? rawNodeType.charAt(0).toUpperCase() + rawNodeType.slice(1)
    : rawNodeType;
  const energy = selectedNode.energy || 0;
  const confidence = selectedNode.confidence || 0;
  const traversals = selectedNode.traversal_count || 0;

  return (
    <>
      {/* Modal Backdrop - Click to close */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 animate-fade-in"
        onClick={() => {
          const event = new CustomEvent('detail:close');
          window.dispatchEvent(event);
        }}
      />

      {/* Modal Panel - Centered */}
      <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
        <div className="w-full max-w-2xl max-h-[80vh] consciousness-panel overflow-hidden pointer-events-auto m-6 animate-scale-in">
          {/* Header */}
          <div className="bg-consciousness-dark/95 backdrop-blur-xl p-4 border-b border-consciousness-border flex items-center justify-between">
            <div>
              <div className="text-consciousness-green font-semibold text-lg">{nodeType}</div>
              <div className="text-xs text-gray-500">Node Details</div>
            </div>
            <button
              onClick={() => {
                const event = new CustomEvent('detail:close');
                window.dispatchEvent(event);
              }}
              className="text-gray-400 hover:text-white transition-colors text-xl"
            >
              ✕
            </button>
          </div>

          {/* Scrollable Content */}
          <div className="overflow-y-auto custom-scrollbar max-h-[calc(80vh-80px)]">

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* All Node Fields (Dynamic) */}
        {renderNodeFields(selectedNode)}

        {/* Consciousness Metadata */}
        <div>
          <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Consciousness</div>
          <div className="space-y-2">
            <MetricRow label="Energy" value={`${(energy * 100).toFixed(0)}%`} color="#5efc82" />
            <MetricRow label="Confidence" value={`${(confidence * 100).toFixed(0)}%`} color="#3b82f6" />
            <MetricRow label="Traversals" value={traversals.toString()} color="#8b5cf6" />
            {selectedNode.last_traversed_by && (
              <MetricRow label="Last Subentity" value={selectedNode.last_traversed_by} color="#f59e0b" />
            )}
          </div>
        </div>

        {/* Subentity Activations */}
        {selectedNode.entity_activations && Object.keys(selectedNode.entity_activations).length > 0 && (
          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Subentity Activations</div>
            <div className="space-y-2">
              {Object.entries(selectedNode.entity_activations).map(([entityId, activation]) => (
                <div key={entityId} className="flex justify-between items-center">
                  <span className="text-sm text-gray-300">{entityId}</span>
                  <span className="text-sm text-consciousness-green">
                    {((activation.energy || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Connections */}
        <div>
          <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">
            Connections ({incomingLinks.length + outgoingLinks.length})
          </div>

          {incomingLinks.length > 0 && (
            <div className="mb-3">
              <div className="text-xs text-gray-500 mb-1">Incoming ({incomingLinks.length})</div>
              <div className="space-y-2">
                {incomingLinks.slice(0, 10).map((link) => {
                  const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                  const sourceNode = nodes.find(n => n.id === sourceId);
                  return (
                    <div key={link.id} className="text-xs text-gray-300 border-l-2 border-gray-700 pl-2 py-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-gray-500">←</span>
                        <span className="text-consciousness-green font-medium">{link.type}</span>
                      </div>
                      <div className="text-gray-200 break-words ml-4">
                        {sourceNode?.text || (sourceNode as any)?.description || sourceId}
                      </div>
                    </div>
                  );
                })}
                {incomingLinks.length > 10 && (
                  <div className="text-xs text-gray-500">+ {incomingLinks.length - 10} more</div>
                )}
              </div>
            </div>
          )}

          {outgoingLinks.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 mb-1">Outgoing ({outgoingLinks.length})</div>
              <div className="space-y-2">
                {outgoingLinks.slice(0, 10).map((link) => {
                  const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                  const targetNode = nodes.find(n => n.id === targetId);
                  return (
                    <div key={link.id} className="text-xs text-gray-300 border-l-2 border-gray-700 pl-2 py-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-gray-500">→</span>
                        <span className="text-consciousness-green font-medium">{link.type}</span>
                      </div>
                      <div className="text-gray-200 break-words ml-4">
                        {targetNode?.text || (targetNode as any)?.description || targetId}
                      </div>
                    </div>
                  );
                })}
                {outgoingLinks.length > 10 && (
                  <div className="text-xs text-gray-500">+ {outgoingLinks.length - 10} more</div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Attribution Card - Shows why edge was chosen (if stride data available) */}
        {mostRecentStride && (
          <div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">
              Recent Traversal Attribution
            </div>
            <AttributionCard
              stride={mostRecentStride}
              edgeEmotion={strideEdgeEmotion}
            />
          </div>
        )}
      </div>
          </div>
        </div>
      </div>
    </>
  );
}

function MetricRow({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-xs text-gray-400">{label}:</span>
      <span className="text-sm font-medium" style={{ color }}>
        {value}
      </span>
    </div>
  );
}

// Render all node fields dynamically
function renderNodeFields(node: Node) {
  // Fields to exclude (technical metadata)
  const excludeFields = new Set([
    'id', 'node_id', 'labels', 'x', 'y', 'vx', 'vy', 'fx', 'fy', 'index',
    'energy', 'confidence', 'traversal_count', 'last_traversed_by',
    'entity_activations', 'sub_entity_weights', 'sub_entity_valences',
    'last_active', 'weight'
  ]);

  // Get all fields that have values
  const fields = Object.entries(node)
    .filter(([key, value]) => !excludeFields.has(key) && value !== null && value !== undefined)
    .sort(([a], [b]) => a.localeCompare(b));

  if (fields.length === 0) {
    return (
      <div>
        <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Content</div>
        <div className="text-sm text-gray-400 italic">No additional fields available</div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {fields.map(([key, value]) => {
        const formattedKey = key
          .split('_')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');

        return (
          <div key={key}>
            <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">
              {formattedKey}
            </div>
            <div className="text-sm text-gray-200 break-words">
              {renderFieldValue(value)}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Render field value based on type
function renderFieldValue(value: any): React.ReactNode {
  if (value === null || value === undefined) {
    return <span className="text-gray-500 italic">none</span>;
  }

  // Array
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span className="text-gray-500 italic">empty</span>;
    }
    return (
      <ul className="list-disc list-inside space-y-1">
        {value.map((item, i) => (
          <li key={i} className="text-sm text-gray-300">
            {typeof item === 'object' ? JSON.stringify(item) : String(item)}
          </li>
        ))}
      </ul>
    );
  }

  // Object
  if (typeof value === 'object') {
    const entries = Object.entries(value);
    if (entries.length === 0) {
      return <span className="text-gray-500 italic">empty</span>;
    }
    return (
      <div className="space-y-1">
        {entries.map(([k, v]) => (
          <div key={k} className="flex gap-2">
            <span className="text-gray-400 text-xs">{k}:</span>
            <span className="text-gray-200 text-xs">{String(v)}</span>
          </div>
        ))}
      </div>
    );
  }

  // Boolean
  if (typeof value === 'boolean') {
    return <span className={value ? 'text-green-400' : 'text-red-400'}>{value ? 'Yes' : 'No'}</span>;
  }

  // Number
  if (typeof value === 'number') {
    return <span className="text-consciousness-green">{value}</span>;
  }

  // String (default)
  return <span>{String(value)}</span>;
}
