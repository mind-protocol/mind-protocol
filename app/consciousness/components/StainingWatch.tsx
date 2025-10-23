/**
 * Staining Watch Component
 *
 * Monitors emotion magnitude saturation across nodes to detect
 * "everything feels the same" failure mode.
 *
 * Displays:
 * - Histogram of emotion magnitudes
 * - Alert when >5% nodes exceed saturation threshold (0.9)
 * - Distribution by magnitude bins
 *
 * Spec: emotion_color_mapping_v2_canonical.md § Staining Watch
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 */

'use client';

import { useMemo } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

const SATURATION_THRESHOLD = 0.9; // From canonical spec
const SATURATION_WARNING_PERCENT = 5; // Alert when >5% nodes saturated

interface HistogramBin {
  min: number;
  max: number;
  count: number;
  label: string;
}

/**
 * Build histogram bins from emotion magnitudes
 */
function buildHistogram(nodeEmotions: Map<string, { magnitude: number }>): HistogramBin[] {
  const bins: HistogramBin[] = [
    { min: 0.0, max: 0.2, count: 0, label: '0.0-0.2' },
    { min: 0.2, max: 0.4, count: 0, label: '0.2-0.4' },
    { min: 0.4, max: 0.6, count: 0, label: '0.4-0.6' },
    { min: 0.6, max: 0.8, count: 0, label: '0.6-0.8' },
    { min: 0.8, max: 1.0, count: 0, label: '0.8-1.0' }
  ];

  // Count nodes into bins
  for (const emotion of nodeEmotions.values()) {
    const mag = emotion.magnitude;
    for (const bin of bins) {
      if (mag >= bin.min && mag < bin.max) {
        bin.count++;
        break;
      }
      // Handle edge case: magnitude exactly 1.0 goes in last bin
      if (mag === 1.0 && bin.max === 1.0) {
        bin.count++;
        break;
      }
    }
  }

  return bins;
}

export function StainingWatch() {
  const { emotionState } = useWebSocket();

  // Build histogram
  const histogram = useMemo(() => {
    return buildHistogram(emotionState.nodeEmotions);
  }, [emotionState.nodeEmotions]);

  // Calculate statistics
  const totalNodes = emotionState.nodeEmotions.size;
  const saturatedCount = emotionState.saturationWarnings.length;
  const saturatedPercent = totalNodes > 0 ? (saturatedCount / totalNodes) * 100 : 0;
  const isWarning = saturatedPercent > SATURATION_WARNING_PERCENT;

  // Find max count for scaling
  const maxCount = Math.max(...histogram.map(b => b.count), 1);

  return (
    <div className="staining-watch bg-slate-900 border border-slate-700 rounded-lg p-4 text-slate-300">
      <h3 className="text-sm font-semibold mb-3 flex items-center justify-between">
        <span>Emotion Saturation Monitor</span>
        {isWarning && (
          <span className="text-xs px-2 py-0.5 bg-red-900/50 text-red-300 rounded">
            ⚠️ High Saturation
          </span>
        )}
      </h3>

      {totalNodes === 0 && (
        <div className="text-xs text-slate-500 py-4 text-center">
          No emotion data yet...
        </div>
      )}

      {totalNodes > 0 && (
        <div className="space-y-3">
          {/* Alert banner */}
          {isWarning && (
            <div className="bg-red-900/20 border border-red-800/50 rounded p-2 text-xs space-y-1">
              <div className="font-semibold text-red-300">
                High saturation detected in {saturatedCount} nodes ({saturatedPercent.toFixed(1)}%)
              </div>
              <div className="text-red-400/80">
                When emotion magnitudes saturate, discrimination is lost.
                Consider adjusting emotion caps or decay rates.
              </div>
            </div>
          )}

          {/* Histogram */}
          <div className="space-y-2">
            <div className="text-xs text-slate-400 mb-2">
              Distribution of Emotion Magnitudes
            </div>
            {histogram.map((bin, i) => (
              <div key={bin.label} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-mono w-16">{bin.label}</span>
                  <span className="text-slate-400 font-mono">{bin.count}</span>
                </div>
                <div className="relative h-6 bg-slate-800 rounded overflow-hidden">
                  <div
                    className={`absolute left-0 top-0 h-full transition-all duration-300 ${
                      bin.min >= 0.8 ? 'bg-red-500/70' :
                      bin.min >= 0.6 ? 'bg-yellow-500/70' :
                      'bg-blue-500/70'
                    }`}
                    style={{ width: `${(bin.count / maxCount) * 100}%` }}
                  />
                  {/* Show count label inside bar if wide enough */}
                  {bin.count > 0 && (bin.count / maxCount) > 0.2 && (
                    <span className="absolute left-2 top-1/2 -translate-y-1/2 text-xs font-mono text-white">
                      {bin.count}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Statistics */}
          <div className="pt-2 border-t border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Total Nodes with Emotion</span>
              <span className="font-mono text-slate-300">{totalNodes}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Saturated (&gt;{SATURATION_THRESHOLD})</span>
              <span className={`font-mono ${isWarning ? 'text-red-400' : 'text-slate-300'}`}>
                {saturatedCount} ({saturatedPercent.toFixed(1)}%)
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Threshold</span>
              <span className="font-mono text-slate-400">
                {SATURATION_WARNING_PERCENT}% (alert trigger)
              </span>
            </div>
          </div>

          {/* Explanation */}
          <div className="text-xs text-slate-400 pt-2 border-t border-slate-800">
            <div className="space-y-1">
              <div className="flex items-start gap-2">
                <span className="text-blue-400">→</span>
                <span>
                  <strong className="text-blue-300">Healthy:</strong> Distribution across bins,
                  few nodes at high magnitudes
                </span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-red-400">→</span>
                <span>
                  <strong className="text-red-300">Saturated:</strong> Many nodes at 0.8-1.0,
                  indicates "everything feels the same" failure
                </span>
              </div>
            </div>
          </div>

          {/* Saturated nodes list (if any) */}
          {saturatedCount > 0 && saturatedCount <= 10 && (
            <div className="pt-2 border-t border-slate-800 space-y-1">
              <div className="text-xs text-slate-400 font-semibold">Saturated Nodes:</div>
              <div className="space-y-1">
                {emotionState.saturationWarnings.slice(0, 10).map(nodeId => {
                  const emotion = emotionState.nodeEmotions.get(nodeId);
                  return (
                    <div key={nodeId} className="text-xs font-mono text-slate-400 flex justify-between">
                      <span className="truncate max-w-[200px]">{nodeId}</span>
                      {emotion && (
                        <span className="text-red-400">{emotion.magnitude.toFixed(2)}</span>
                      )}
                    </div>
                  );
                })}
                {saturatedCount > 10 && (
                  <div className="text-xs text-slate-500 italic">
                    ... and {saturatedCount - 10} more
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
