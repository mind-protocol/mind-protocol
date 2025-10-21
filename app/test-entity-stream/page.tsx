'use client';

import { useEntityStream } from '../consciousness/hooks/useEntityStream';

/**
 * Test page for useEntityStream hook
 *
 * Verifies that:
 * 1. Hook connects to ws://localhost:8765
 * 2. Receives state_delta.v1 events
 * 3. Updates node/link caches correctly
 * 4. Displays data reactively
 *
 * Author: Iris "The Aperture"
 * Purpose: Verification before integration
 */
export default function TestEntityStreamPage() {
  const { connected, error, currentTick, nodes, links, metrics } = useEntityStream();

  return (
    <div className="p-8 bg-gray-900 text-gray-100 min-h-screen font-mono">
      <h1 className="text-2xl font-bold mb-6">Entity Stream Test</h1>

      {/* Connection Status */}
      <div className="mb-6 p-4 border rounded" style={{
        borderColor: connected ? '#10b981' : '#ef4444',
        backgroundColor: connected ? '#064e3b' : '#7f1d1d'
      }}>
        <div className="font-bold mb-2">
          {connected ? '✓ Connected' : error ? '✗ Error' : '○ Connecting...'}
        </div>
        {error && <div className="text-red-300">{error}</div>}
        <div className="text-sm text-gray-400 mt-2">
          WebSocket: ws://localhost:8765
        </div>
      </div>

      {/* Current State */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-gray-800 rounded">
          <div className="text-gray-400 text-sm">Current Tick</div>
          <div className="text-2xl">{currentTick ?? '-'}</div>
        </div>
        <div className="p-4 bg-gray-800 rounded">
          <div className="text-gray-400 text-sm">Nodes</div>
          <div className="text-2xl">{nodes.size}</div>
        </div>
        <div className="p-4 bg-gray-800 rounded">
          <div className="text-gray-400 text-sm">Links</div>
          <div className="text-2xl">{links.size}</div>
        </div>
      </div>

      {/* Metrics */}
      {metrics && (
        <div className="mb-6 p-4 bg-gray-800 rounded">
          <div className="font-bold mb-3">Metrics</div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Global Energy:</span>{' '}
              {metrics.global_energy?.toFixed(2) ?? '-'}
            </div>
            <div>
              <span className="text-gray-400">Active Nodes:</span>{' '}
              {metrics.active_nodes ?? '-'}
            </div>
            <div>
              <span className="text-gray-400">Active Links:</span>{' '}
              {metrics.active_links ?? '-'}
            </div>
            <div>
              <span className="text-gray-400">Rho:</span>{' '}
              {metrics.rho?.toFixed(2) ?? '-'}
            </div>
          </div>

          {metrics.active_entities && Object.keys(metrics.active_entities).length > 0 && (
            <div className="mt-4">
              <div className="text-gray-400 text-sm mb-2">Active Entities:</div>
              {Object.entries(metrics.active_entities).map(([entity, data]) => (
                <div key={entity} className="text-sm">
                  <span className="text-cyan-400">{entity}</span>:{' '}
                  {data.node_count} nodes, E={data.total_energy.toFixed(2)}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Nodes */}
      <div className="mb-6">
        <div className="font-bold mb-3">Nodes ({nodes.size})</div>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {Array.from(nodes.values()).slice(0, 10).map(node => (
            <div key={node.id} className="p-3 bg-gray-800 rounded text-sm">
              <div className="font-semibold text-cyan-400">{node.id}</div>
              <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                <div>
                  <span className="text-gray-400">Energy:</span>{' '}
                  {node.total_energy.toFixed(3)}
                </div>
                <div>
                  <span className="text-gray-400">Threshold:</span>{' '}
                  {node.threshold.toFixed(3)}
                </div>
                <div>
                  <span className="text-gray-400">Active:</span>{' '}
                  {node.active ? '✓' : '○'}
                </div>
              </div>
              {Object.keys(node.entity_energies).length > 0 && (
                <div className="mt-2 text-xs">
                  <span className="text-gray-400">Entities:</span>{' '}
                  {Object.entries(node.entity_energies).map(([entity, energy]) => (
                    <span key={entity} className="mr-2">
                      {entity}={energy.toFixed(2)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {nodes.size > 10 && (
            <div className="text-gray-400 text-sm">
              ... and {nodes.size - 10} more
            </div>
          )}
        </div>
      </div>

      {/* Links */}
      <div>
        <div className="font-bold mb-3">Links ({links.size})</div>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {Array.from(links.values()).slice(0, 10).map((link, idx) => (
            <div key={idx} className="p-3 bg-gray-800 rounded text-sm">
              <div className="font-semibold">
                <span className="text-green-400">{link.src}</span>
                {' → '}
                <span className="text-green-400">{link.dst}</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-2 text-xs">
                <div>
                  <span className="text-gray-400">Type:</span> {link.type}
                </div>
                <div>
                  <span className="text-gray-400">Weight:</span>{' '}
                  {link.weight.toFixed(2)}
                </div>
                <div>
                  <span className="text-gray-400">Active:</span>{' '}
                  {link.active ? '✓' : '○'}
                </div>
              </div>
            </div>
          ))}
          {links.size > 10 && (
            <div className="text-gray-400 text-sm">
              ... and {links.size - 10} more
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
