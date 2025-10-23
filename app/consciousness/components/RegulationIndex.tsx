/**
 * Regulation vs Coherence Index
 *
 * Shows real-time ratio of complementarity-driven selections (regulation)
 * vs resonance-driven selections (coherence) from recent strides.
 *
 * Visual encoding:
 * - Blue bar = Complementarity (seeking emotional balance)
 * - Orange bar = Resonance (maintaining emotional coherence)
 * - Ratio > 0.5 = Regulation dominant
 * - Ratio < 0.5 = Coherence dominant
 *
 * Spec: emotion_color_mapping_v2_canonical.md § Regulation Index
 * Author: Iris "The Aperture"
 * Date: 2025-10-22
 */

'use client';

import { useWebSocket } from '../hooks/useWebSocket';

export function RegulationIndex() {
  const { emotionState } = useWebSocket();

  const compRatio = emotionState.regulationRatio ?? 0;
  const resRatio = emotionState.resonanceRatio ?? 0;
  const hasData = compRatio + resRatio > 0;

  // Determine dominant mode
  const dominantMode = compRatio > resRatio ? 'regulation' :
                       resRatio > compRatio ? 'coherence' : 'balanced';

  return (
    <div className="regulation-index bg-slate-900 border border-slate-700 rounded-lg p-4 text-slate-300">
      <h3 className="text-sm font-semibold mb-3 flex items-center justify-between">
        <span>Regulation vs Coherence</span>
        {hasData && (
          <span className={`text-xs px-2 py-0.5 rounded ${
            dominantMode === 'regulation' ? 'bg-blue-900/50 text-blue-300' :
            dominantMode === 'coherence' ? 'bg-orange-900/50 text-orange-300' :
            'bg-slate-700 text-slate-400'
          }`}>
            {dominantMode === 'regulation' ? 'Seeking Balance' :
             dominantMode === 'coherence' ? 'Maintaining Mood' :
             'Balanced'}
          </span>
        )}
      </h3>

      {!hasData && (
        <div className="text-xs text-slate-500 py-4 text-center">
          Awaiting stride data...
        </div>
      )}

      {hasData && (
        <div className="space-y-3">
          {/* Horizontal bar chart */}
          <div className="relative h-8 bg-slate-800 rounded overflow-hidden">
            {/* Complementarity bar (blue) */}
            <div
              className="absolute left-0 top-0 h-full bg-blue-500/70 transition-all duration-500"
              style={{ width: `${compRatio * 100}%` }}
            />
            {/* Resonance bar (orange) */}
            <div
              className="absolute right-0 top-0 h-full bg-orange-500/70 transition-all duration-500"
              style={{ width: `${resRatio * 100}%` }}
            />
            {/* Center line */}
            <div className="absolute left-1/2 top-0 h-full w-px bg-slate-600" />
          </div>

          {/* Legend */}
          <div className="flex justify-between items-center text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-500/70 rounded" />
              <span className="text-slate-400">Complementarity</span>
              <span className="font-mono text-blue-400">
                {(compRatio * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-orange-400">
                {(resRatio * 100).toFixed(0)}%
              </span>
              <span className="text-slate-400">Resonance</span>
              <div className="w-3 h-3 bg-orange-500/70 rounded" />
            </div>
          </div>

          {/* Explanation */}
          <div className="text-xs text-slate-400 pt-2 border-t border-slate-800 space-y-1">
            <div className="flex items-start gap-2">
              <span className="text-blue-400">→</span>
              <span>
                <strong className="text-blue-300">Complementarity</strong> seeks opposite emotions for regulation
                (e.g., calm after tension)
              </span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-orange-400">→</span>
              <span>
                <strong className="text-orange-300">Resonance</strong> seeks similar emotions for coherence
                (e.g., maintaining focus)
              </span>
            </div>
          </div>

          {/* Current pattern indicator */}
          {dominantMode !== 'balanced' && (
            <div className="text-xs italic text-slate-400 pt-2 border-t border-slate-800">
              {dominantMode === 'regulation' ? (
                <span>
                  System is actively regulating - seeking emotional balance by choosing opposite affects.
                </span>
              ) : (
                <span>
                  System is maintaining coherence - staying aligned with current emotional state.
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Stride count info */}
      <div className="text-xs text-slate-500 mt-3 pt-2 border-t border-slate-800">
        Based on last {emotionState.recentStrides.length} strides
      </div>
    </div>
  );
}
