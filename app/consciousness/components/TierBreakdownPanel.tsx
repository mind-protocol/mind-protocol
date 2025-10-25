/**
 * Tier Breakdown Panel - 3-Tier Strengthening Observability
 *
 * Visualizes learning tier distribution from Priority 2 (3-tier strengthening):
 * - STRONG tier (1.0x): Co-activation learning
 * - MEDIUM tier (0.6x): Causal credit learning
 * - WEAK tier (0.3x): Background spillover learning
 *
 * Shows:
 * - Tier distribution pie chart (strong/medium/weak %)
 * - Reason histogram (co_activation/causal/background counts)
 * - Noise filtering stats (learning blocked by stride utility threshold)
 * - Rolling window controls
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-24
 * Priority: 2 (3-Tier Strengthening Observability)
 * Spec: docs/specs/v2/learning_and_trace/link_strengthening.md
 */

'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { StrideExecEvent } from '../hooks/websocket-types';

interface TierBreakdownPanelProps {
  strideEvents: StrideExecEvent[];
  windowSize?: number; // Rolling window size (frames)
}

interface TierStats {
  strong: number;
  medium: number;
  weak: number;
  total: number;
}

interface ReasonStats {
  co_activation: number;
  causal: number;
  background: number;
}

interface NoiseFilterStats {
  learning_enabled: number;
  learning_blocked: number;
  block_rate: number;
}

export default function TierBreakdownPanel({
  strideEvents,
  windowSize = 100
}: TierBreakdownPanelProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return strideEvents.slice(-selectedWindow);
  }, [strideEvents, selectedWindow]);

  // Filter to events with tier data (Priority 2 fields present)
  const tierEvents = useMemo(() => {
    return windowedEvents.filter(e => e.tier !== undefined);
  }, [windowedEvents]);

  // Compute tier distribution
  const tierStats = useMemo((): TierStats => {
    const stats = { strong: 0, medium: 0, weak: 0, total: 0 };

    tierEvents.forEach(event => {
      if (event.tier === 'strong') stats.strong++;
      else if (event.tier === 'medium') stats.medium++;
      else if (event.tier === 'weak') stats.weak++;
      stats.total++;
    });

    return stats;
  }, [tierEvents]);

  // Compute reason distribution
  const reasonStats = useMemo((): ReasonStats => {
    const stats = { co_activation: 0, causal: 0, background: 0 };

    tierEvents.forEach(event => {
      if (event.reason === 'co_activation') stats.co_activation++;
      else if (event.reason === 'causal') stats.causal++;
      else if (event.reason === 'background') stats.background++;
    });

    return stats;
  }, [tierEvents]);

  // Compute noise filtering stats
  const noiseStats = useMemo((): NoiseFilterStats => {
    const enabled = tierEvents.filter(e => e.learning_enabled === true).length;
    const blocked = tierEvents.filter(e => e.learning_enabled === false).length;
    const total = enabled + blocked;
    const block_rate = total > 0 ? blocked / total : 0;

    return {
      learning_enabled: enabled,
      learning_blocked: blocked,
      block_rate
    };
  }, [tierEvents]);

  // Compute percentages for pie chart
  const tierPercentages = useMemo(() => {
    if (tierStats.total === 0) return { strong: 0, medium: 0, weak: 0 };

    return {
      strong: (tierStats.strong / tierStats.total) * 100,
      medium: (tierStats.medium / tierStats.total) * 100,
      weak: (tierStats.weak / tierStats.total) * 100
    };
  }, [tierStats]);

  return (
    <div className="tier-breakdown-panel bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold text-gray-100">
            3-Tier Strengthening
          </h3>
          {tierStats.total === 0 && (
            <span className="text-xs px-2 py-0.5 rounded bg-yellow-900/30 text-yellow-400 border border-yellow-600/30">
              Awaiting data
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Window:</label>
          <select
            value={selectedWindow}
            onChange={(e) => setSelectedWindow(Number(e.target.value))}
            className="bg-gray-800 text-gray-200 text-sm rounded px-2 py-1 border border-gray-600"
          >
            <option value={50}>50 strides</option>
            <option value={100}>100 strides</option>
            <option value={200}>200 strides</option>
            <option value={500}>500 strides</option>
          </select>
        </div>
      </div>

      {tierStats.total === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No tier data available. Waiting for 3-tier strengthening events...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Tier Distribution */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Tier Distribution</h4>
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div className="bg-green-900/30 border border-green-700 rounded p-2">
                <div className="text-xs text-gray-400">STRONG (1.0×)</div>
                <div className="text-lg font-bold text-green-400">
                  {tierPercentages.strong.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">{tierStats.strong} strides</div>
              </div>

              <div className="bg-yellow-900/30 border border-yellow-700 rounded p-2">
                <div className="text-xs text-gray-400">MEDIUM (0.6×)</div>
                <div className="text-lg font-bold text-yellow-400">
                  {tierPercentages.medium.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">{tierStats.medium} strides</div>
              </div>

              <div className="bg-blue-900/30 border border-blue-700 rounded p-2">
                <div className="text-xs text-gray-400">WEAK (0.3×)</div>
                <div className="text-lg font-bold text-blue-400">
                  {tierPercentages.weak.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">{tierStats.weak} strides</div>
              </div>
            </div>

            {/* Simple bar chart */}
            <div className="flex h-4 rounded overflow-hidden">
              <div
                className="bg-green-500"
                style={{ width: `${tierPercentages.strong}%` }}
                title={`STRONG: ${tierPercentages.strong.toFixed(1)}%`}
              />
              <div
                className="bg-yellow-500"
                style={{ width: `${tierPercentages.medium}%` }}
                title={`MEDIUM: ${tierPercentages.medium.toFixed(1)}%`}
              />
              <div
                className="bg-blue-500"
                style={{ width: `${tierPercentages.weak}%` }}
                title={`WEAK: ${tierPercentages.weak.toFixed(1)}%`}
              />
            </div>
          </div>

          {/* Reason Breakdown */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Learning Reasons</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Co-activation:</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-800 rounded overflow-hidden">
                    <div
                      className="h-full bg-green-500"
                      style={{
                        width: `${(reasonStats.co_activation / tierStats.total) * 100}%`
                      }}
                    />
                  </div>
                  <span className="text-xs text-gray-300 w-12 text-right">
                    {reasonStats.co_activation}
                  </span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Causal:</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-800 rounded overflow-hidden">
                    <div
                      className="h-full bg-yellow-500"
                      style={{
                        width: `${(reasonStats.causal / tierStats.total) * 100}%`
                      }}
                    />
                  </div>
                  <span className="text-xs text-gray-300 w-12 text-right">
                    {reasonStats.causal}
                  </span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Background:</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-800 rounded overflow-hidden">
                    <div
                      className="h-full bg-blue-500"
                      style={{
                        width: `${(reasonStats.background / tierStats.total) * 100}%`
                      }}
                    />
                  </div>
                  <span className="text-xs text-gray-300 w-12 text-right">
                    {reasonStats.background}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Noise Filtering */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Noise Filtering</h4>
            <div className="bg-gray-800 rounded p-3">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400">Learning enabled:</span>
                <span className="text-green-400">{noiseStats.learning_enabled}</span>
              </div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400">Learning blocked:</span>
                <span className="text-red-400">{noiseStats.learning_blocked}</span>
              </div>
              <div className="flex justify-between text-xs font-medium mt-2 pt-2 border-t border-gray-700">
                <span className="text-gray-300">Block rate:</span>
                <span className="text-orange-400">
                  {(noiseStats.block_rate * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total strides analyzed: {tierStats.total} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}
