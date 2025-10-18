'use client';

import { useState } from 'react';
import type { AvailableGraphs } from '../hooks/useGraphData';

interface GraphControlsProps {
  availableGraphs: AvailableGraphs;
  onSelectGraph: (type: string, id: string) => void;
  connected: boolean;
}

/**
 * GraphControls
 *
 * Collapsible control menu (bottom-left).
 * Graph selection, basic settings, connection status.
 *
 * Design: Minimal, unobtrusive, expands on hover.
 */
export function GraphControls({ availableGraphs, onSelectGraph, connected }: GraphControlsProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className="fixed bottom-4 left-4 z-50 consciousness-panel"
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
    >
      {/* Collapsed state - just connection indicator */}
      {!expanded && (
        <div className="px-4 py-3 flex items-center gap-2 cursor-pointer">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-consciousness-green' : 'bg-red-500'}
                          ${connected ? 'animate-pulse-glow' : ''}`} />
          <span className="text-sm text-gray-400">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      )}

      {/* Expanded state - full controls */}
      {expanded && (
        <div className="p-4 space-y-4 min-w-[300px]">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h3 className="text-consciousness-green font-semibold">Controls</h3>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-consciousness-green' : 'bg-red-500'}
                              ${connected ? 'animate-pulse-glow' : ''}`} />
              <span className="text-xs text-gray-400">
                {connected ? 'Live' : 'Offline'}
              </span>
            </div>
          </div>

          {/* Graph Selection */}
          <div className="space-y-2">
            <label className="text-xs text-gray-400 uppercase tracking-wider">Select Graph</label>

            {/* Citizens */}
            {availableGraphs.citizens.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs text-gray-500">Citizens</div>
                {availableGraphs.citizens.map((graph, index) => (
                  <button
                    key={`citizen-${graph.id || index}`}
                    onClick={() => onSelectGraph('citizen', graph.id)}
                    className="w-full text-left px-3 py-2 rounded text-sm
                             hover:bg-consciousness-green/10 hover:text-consciousness-green
                             transition-colors"
                  >
                    {graph.name || graph.id}
                  </button>
                ))}
              </div>
            )}

            {/* Organizations */}
            {availableGraphs.organizations.length > 0 && (
              <div className="space-y-1 mt-3">
                <div className="text-xs text-gray-500">Organizations</div>
                {availableGraphs.organizations.map((graph, index) => (
                  <button
                    key={`org-${graph.id || index}`}
                    onClick={() => onSelectGraph('organization', graph.id)}
                    className="w-full text-left px-3 py-2 rounded text-sm
                             hover:bg-consciousness-green/10 hover:text-consciousness-green
                             transition-colors"
                  >
                    {graph.name || graph.id}
                  </button>
                ))}
              </div>
            )}

            {/* Ecosystems */}
            {availableGraphs.ecosystems.length > 0 && (
              <div className="space-y-1 mt-3">
                <div className="text-xs text-gray-500">Ecosystems</div>
                {availableGraphs.ecosystems.map((graph, index) => (
                  <button
                    key={`ecosystem-${graph.id || index}`}
                    onClick={() => onSelectGraph('ecosystem', graph.id)}
                    className="w-full text-left px-3 py-2 rounded text-sm
                             hover:bg-consciousness-green/10 hover:text-consciousness-green
                             transition-colors"
                  >
                    {graph.name || graph.id}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Info */}
          <div className="pt-3 border-t border-consciousness-border">
            <div className="text-xs text-gray-500">
              Hover to expand • Real-time updates
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
