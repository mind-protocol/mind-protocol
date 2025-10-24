/**
 * Compact Autonomy Indicator - Sidebar View
 *
 * Simple autonomy score display.
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-24
 */

'use client';

import type { FrameStartEvent } from '../../hooks/websocket-types';

interface CompactAutonomyProps {
  frameEvents: FrameStartEvent[];
}

export function CompactAutonomy({ frameEvents }: CompactAutonomyProps) {
  if (frameEvents.length === 0) {
    return (
      <div className="text-xs text-slate-500 py-2 text-center">
        No autonomy data yet...
      </div>
    );
  }

  // Get most recent frame's rho value as proxy for autonomy
  const latestFrame = frameEvents[frameEvents.length - 1];
  const rho = latestFrame.rho ?? 1.0;

  // Rho > 1 = expanding (high autonomy)
  // Rho ≈ 1 = stable
  // Rho < 1 = contracting (low autonomy)
  const autonomyScore = Math.min(Math.max((rho - 0.5) / 0.5, 0), 1);

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs text-slate-400">
        <span>Autonomy (ρ)</span>
        <span className="font-mono text-slate-300">{rho.toFixed(2)}</span>
      </div>

      {/* Progress bar */}
      <div className="h-3 bg-slate-800 rounded overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${
            autonomyScore > 0.7 ? 'bg-green-500' :
            autonomyScore > 0.4 ? 'bg-yellow-500' :
            'bg-red-500'
          }`}
          style={{ width: `${autonomyScore * 100}%` }}
        />
      </div>

      <div className="text-xs text-slate-500">
        {rho > 1.05 ? 'Expanding' : rho > 0.95 ? 'Stable' : 'Contracting'}
      </div>
    </div>
  );
}
