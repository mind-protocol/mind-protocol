/**
 * Compact Regulation Index - Sidebar View
 *
 * Minimal version of RegulationIndex for left sidebar accordion.
 * Shows just the essential bar chart without heavy chrome.
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-24
 */

'use client';

import { useWebSocket } from '../../hooks/useWebSocket';

export function CompactRegulationIndex() {
  const { emotionState } = useWebSocket();

  const compRatio = emotionState.regulationRatio ?? 0;
  const resRatio = emotionState.resonanceRatio ?? 0;
  const hasData = compRatio + resRatio > 0;

  if (!hasData) {
    return (
      <div className="text-xs text-slate-500 py-2 text-center">
        Awaiting stride data...
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center text-xs text-slate-400">
        <span>Regulation vs Coherence</span>
        <span className="font-mono text-slate-300">
          {(compRatio * 100).toFixed(0)}/{(resRatio * 100).toFixed(0)}
        </span>
      </div>

      {/* Horizontal bar chart - compact */}
      <div className="relative h-4 bg-slate-800 rounded overflow-hidden">
        <div
          className="absolute left-0 top-0 h-full bg-blue-500/70 transition-all duration-500"
          style={{ width: `${compRatio * 100}%` }}
        />
        <div
          className="absolute right-0 top-0 h-full bg-orange-500/70 transition-all duration-500"
          style={{ width: `${resRatio * 100}%` }}
        />
        <div className="absolute left-1/2 top-0 h-full w-px bg-slate-600" />
      </div>

      {/* Minimal legend */}
      <div className="flex justify-between text-xs text-slate-500">
        <span className="text-blue-400">Comp</span>
        <span className="text-orange-400">Res</span>
      </div>
    </div>
  );
}
