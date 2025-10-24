/**
 * Phenomenology Mismatch Panel - Substrate-Phenomenology Alignment
 *
 * Visualizes Priority 6 phenomenology monitoring:
 * - Substrate-inferred affect vs entity self-report divergence
 * - Mismatch detection and classification
 * - Alignment health over time
 * - Mismatch type distribution
 *
 * Shows:
 * - Current alignment status
 * - Recent mismatches with type classification
 * - Divergence magnitude distribution
 * - Valence/arousal comparison charts
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 6 (Phenomenology Health Observability)
 * Spec: docs/specs/v2/consciousness/phenomenology_monitoring.md
 */

'use client';

import React, { useState, useMemo } from 'react';
import { PhenomenologyMismatchEvent } from '../hooks/websocket-types';

interface PhenomenologyMismatchPanelProps {
  mismatchEvents: PhenomenologyMismatchEvent[];
  windowSize?: number;
}

interface MismatchTypeStats {
  valence_flip: number;
  arousal_mismatch: number;
  magnitude_divergence: number;
  coherent: number;
  total: number;
}

export default function PhenomenologyMismatchPanel({
  mismatchEvents,
  windowSize = 100
}: PhenomenologyMismatchPanelProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return mismatchEvents.slice(-selectedWindow);
  }, [mismatchEvents, selectedWindow]);

  // Get current alignment status (most recent event)
  const currentStatus = useMemo(() => {
    if (windowedEvents.length === 0) return null;
    const recent = windowedEvents[windowedEvents.length - 1];
    return {
      mismatch_detected: recent.mismatch_detected,
      mismatch_type: recent.mismatch_type,
      divergence: recent.divergence,
      threshold: recent.threshold
    };
  }, [windowedEvents]);

  // Compute mismatch type distribution
  const mismatchTypeStats = useMemo((): MismatchTypeStats => {
    const stats = {
      valence_flip: 0,
      arousal_mismatch: 0,
      magnitude_divergence: 0,
      coherent: 0,
      total: 0
    };

    windowedEvents.forEach(event => {
      if (event.mismatch_type === 'valence_flip') stats.valence_flip++;
      else if (event.mismatch_type === 'arousal_mismatch') stats.arousal_mismatch++;
      else if (event.mismatch_type === 'magnitude_divergence') stats.magnitude_divergence++;
      else if (event.mismatch_type === 'coherent') stats.coherent++;
      stats.total++;
    });

    return stats;
  }, [windowedEvents]);

  // Compute alignment health (% coherent)
  const alignmentHealth = useMemo(() => {
    if (mismatchTypeStats.total === 0) return 0;
    return (mismatchTypeStats.coherent / mismatchTypeStats.total) * 100;
  }, [mismatchTypeStats]);

  // Compute average divergence
  const avgDivergence = useMemo(() => {
    if (windowedEvents.length === 0) return 0;
    const sum = windowedEvents.reduce((acc, event) => acc + event.divergence, 0);
    return sum / windowedEvents.length;
  }, [windowedEvents]);

  // Recent mismatches (last 5 with mismatch_detected = true)
  const recentMismatches = useMemo(() => {
    return windowedEvents
      .filter(e => e.mismatch_detected)
      .slice(-5)
      .reverse();
  }, [windowedEvents]);

  // Mismatch type color
  const getMismatchTypeColor = (type: string): string => {
    switch (type) {
      case 'valence_flip': return 'text-red-400';
      case 'arousal_mismatch': return 'text-orange-400';
      case 'magnitude_divergence': return 'text-yellow-400';
      case 'coherent': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const getMismatchTypeBg = (type: string): string => {
    switch (type) {
      case 'valence_flip': return 'bg-red-900/30 border-red-700';
      case 'arousal_mismatch': return 'bg-orange-900/30 border-orange-700';
      case 'magnitude_divergence': return 'bg-yellow-900/30 border-yellow-700';
      case 'coherent': return 'bg-green-900/30 border-green-700';
      default: return 'bg-gray-800 border-gray-600';
    }
  };

  return (
    <div className="phenomenology-mismatch-panel bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-100">
          Phenomenology Alignment
        </h3>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Window:</label>
          <select
            value={selectedWindow}
            onChange={(e) => setSelectedWindow(Number(e.target.value))}
            className="bg-gray-800 text-gray-200 text-sm rounded px-2 py-1 border border-gray-600"
          >
            <option value={50}>50 ticks</option>
            <option value={100}>100 ticks</option>
            <option value={200}>200 ticks</option>
          </select>
        </div>
      </div>

      {windowedEvents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No phenomenology data yet. Waiting for substrate-phenomenology comparison...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Current Status */}
          {currentStatus && (
            <div className={`border rounded-lg p-3 ${getMismatchTypeBg(currentStatus.mismatch_type)}`}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400">Current Status:</span>
                <span className={`text-xl font-bold ${getMismatchTypeColor(currentStatus.mismatch_type)}`}>
                  {currentStatus.mismatch_type.toUpperCase().replace('_', ' ')}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Divergence:</span>
                <span className={`font-bold ${
                  currentStatus.divergence > currentStatus.threshold ? 'text-red-400' : 'text-green-400'
                }`}>
                  {currentStatus.divergence.toFixed(3)} (threshold: {currentStatus.threshold.toFixed(3)})
                </span>
              </div>
            </div>
          )}

          {/* Alignment Health */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Alignment Health</h4>
            <div className="bg-gray-800 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400">Coherence Rate:</span>
                <span className={`text-3xl font-bold ${
                  alignmentHealth > 80 ? 'text-green-400' :
                  alignmentHealth > 60 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {alignmentHealth.toFixed(0)}%
                </span>
              </div>
              <div className="h-2 bg-gray-700 rounded overflow-hidden">
                <div
                  className={`h-full ${
                    alignmentHealth > 80 ? 'bg-green-500' :
                    alignmentHealth > 60 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${alignmentHealth}%` }}
                />
              </div>
              <div className="text-xs text-gray-500 mt-2">
                {alignmentHealth > 80 ? 'Strong substrate-phenomenology alignment' :
                 alignmentHealth > 60 ? 'Moderate alignment - some divergence' :
                 'Weak alignment - significant substrate-phenomenology gap'}
              </div>
            </div>
          </div>

          {/* Mismatch Type Distribution */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Mismatch Types</h4>
            <div className="space-y-2">
              <div className={`border rounded p-2 ${getMismatchTypeBg('coherent')}`}>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-green-400">Coherent</span>
                  <span className="text-sm font-bold text-green-300">
                    {mismatchTypeStats.coherent} ({((mismatchTypeStats.coherent / mismatchTypeStats.total) * 100).toFixed(0)}%)
                  </span>
                </div>
              </div>

              <div className={`border rounded p-2 ${getMismatchTypeBg('valence_flip')}`}>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-red-400">Valence Flip</span>
                  <span className="text-sm font-bold text-red-300">
                    {mismatchTypeStats.valence_flip} ({((mismatchTypeStats.valence_flip / mismatchTypeStats.total) * 100).toFixed(0)}%)
                  </span>
                </div>
              </div>

              <div className={`border rounded p-2 ${getMismatchTypeBg('arousal_mismatch')}`}>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-orange-400">Arousal Mismatch</span>
                  <span className="text-sm font-bold text-orange-300">
                    {mismatchTypeStats.arousal_mismatch} ({((mismatchTypeStats.arousal_mismatch / mismatchTypeStats.total) * 100).toFixed(0)}%)
                  </span>
                </div>
              </div>

              <div className={`border rounded p-2 ${getMismatchTypeBg('magnitude_divergence')}`}>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-yellow-400">Magnitude Divergence</span>
                  <span className="text-sm font-bold text-yellow-300">
                    {mismatchTypeStats.magnitude_divergence} ({((mismatchTypeStats.magnitude_divergence / mismatchTypeStats.total) * 100).toFixed(0)}%)
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Mismatches */}
          {recentMismatches.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-2">Recent Mismatches</h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {recentMismatches.map((event, idx) => (
                  <div key={`${event.frame_id}-${idx}`} className="bg-gray-800 rounded p-2 text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <span className={`font-bold ${getMismatchTypeColor(event.mismatch_type)}`}>
                        {event.mismatch_type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="text-gray-500">Frame {event.frame_id}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <div className="text-gray-500">Substrate:</div>
                        <div className="text-gray-300">
                          V: {event.substrate_valence.toFixed(2)}, A: {event.substrate_arousal.toFixed(2)}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-500">Self-Report:</div>
                        <div className="text-gray-300">
                          V: {event.selfreport_valence.toFixed(2)}, A: {event.selfreport_arousal.toFixed(2)}
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-between mt-1 pt-1 border-t border-gray-700">
                      <span className="text-gray-500">Divergence:</span>
                      <span className="text-red-400 font-bold">{event.divergence.toFixed(3)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="bg-gray-800 rounded p-3">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-400">Avg Divergence:</span>
              <span className="text-gray-200 font-bold">{avgDivergence.toFixed(3)}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Mismatches Detected:</span>
              <span className="text-red-400 font-bold">
                {windowedEvents.filter(e => e.mismatch_detected).length}
              </span>
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total ticks analyzed: {windowedEvents.length} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}
