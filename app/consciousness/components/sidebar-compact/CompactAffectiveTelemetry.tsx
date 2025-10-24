/**
 * Compact Affective Telemetry - Sidebar View
 *
 * Minimal version showing just valence/arousal metrics.
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-24
 */

'use client';

import { useWebSocket } from '../../hooks/useWebSocket';

export function CompactAffectiveTelemetry() {
  const { emotionState } = useWebSocket();

  const hasData = emotionState.nodeEmotions.size > 0 || emotionState.linkEmotions.size > 0;

  if (!hasData) {
    return (
      <div className="text-xs text-slate-500 py-2 text-center">
        No emotion data yet...
      </div>
    );
  }

  // Calculate average valence and arousal from nodes
  let totalValence = 0;
  let totalArousal = 0;
  let count = 0;

  emotionState.nodeEmotions.forEach(emotion => {
    // Extract valence and arousal from axes array
    const valenceAxis = emotion.axes.find(a => a.axis === 'valence');
    const arousalAxis = emotion.axes.find(a => a.axis === 'arousal');

    if (valenceAxis) totalValence += valenceAxis.value;
    if (arousalAxis) totalArousal += arousalAxis.value;
    count++;
  });

  const avgValence = count > 0 ? totalValence / count : 0;
  const avgArousal = count > 0 ? totalArousal / count : 0;

  // Map to -1 to 1 scale for display
  const valencePercent = ((avgValence + 1) / 2) * 100;
  const arousalPercent = ((avgArousal + 1) / 2) * 100;

  return (
    <div className="space-y-2">
      <div className="text-xs text-slate-400 mb-1">
        Affective State ({count} nodes)
      </div>

      {/* Valence bar */}
      <div>
        <div className="flex justify-between text-xs text-slate-500 mb-1">
          <span>Valence</span>
          <span className="font-mono">{avgValence.toFixed(2)}</span>
        </div>
        <div className="h-2 bg-slate-800 rounded overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-red-500 via-gray-500 to-green-500"
            style={{ width: `${valencePercent}%` }}
          />
        </div>
      </div>

      {/* Arousal bar */}
      <div>
        <div className="flex justify-between text-xs text-slate-500 mb-1">
          <span>Arousal</span>
          <span className="font-mono">{avgArousal.toFixed(2)}</span>
        </div>
        <div className="h-2 bg-slate-800 rounded overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-yellow-500"
            style={{ width: `${arousalPercent}%` }}
          />
        </div>
      </div>
    </div>
  );
}
