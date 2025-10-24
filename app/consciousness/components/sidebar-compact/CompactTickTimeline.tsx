/**
 * Compact Tick Timeline - Sidebar View
 *
 * Minimal sparkline showing tick speed over recent frames.
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-24
 */

'use client';

import type { FrameStartEvent } from '../../hooks/websocket-types';

interface CompactTickTimelineProps {
  frameEvents: FrameStartEvent[];
}

export function CompactTickTimeline({ frameEvents }: CompactTickTimelineProps) {
  if (frameEvents.length === 0) {
    return (
      <div className="text-xs text-slate-500 py-2 text-center">
        No tick data yet...
      </div>
    );
  }

  // Get last 50 frames for sparkline
  const recentFrames = frameEvents.slice(-50);

  // Calculate tick intervals
  const intervals = recentFrames.map(f => f.dt_ms ?? 100);
  const maxInterval = Math.max(...intervals);
  const minInterval = Math.min(...intervals);
  const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs text-slate-400">
        <span>Tick Speed</span>
        <span className="font-mono text-slate-300">{avgInterval.toFixed(0)}ms avg</span>
      </div>

      {/* Sparkline */}
      <div className="h-8 flex items-end gap-px">
        {recentFrames.map((frame, i) => {
          const interval = frame.dt_ms ?? 100;
          const heightPercent = ((interval - minInterval) / (maxInterval - minInterval)) * 100;

          return (
            <div
              key={i}
              className="flex-1 bg-cyan-500/50 rounded-t"
              style={{ height: `${Math.max(heightPercent, 10)}%` }}
            />
          );
        })}
      </div>

      <div className="flex justify-between text-xs text-slate-500">
        <span>{minInterval.toFixed(0)}ms</span>
        <span>{maxInterval.toFixed(0)}ms</span>
      </div>
    </div>
  );
}
