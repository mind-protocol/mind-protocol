/**
 * Compact Exploration Dynamics - Sidebar View
 *
 * Combined view of fanout strategy and task mode influence.
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-24
 */

'use client';

import type { StrideSelectionEvent } from '../../hooks/websocket-types';

interface CompactExplorationProps {
  strideSelectionEvents: StrideSelectionEvent[];
}

export function CompactExploration({ strideSelectionEvents }: CompactExplorationProps) {
  if (strideSelectionEvents.length === 0) {
    return (
      <div className="text-xs text-slate-500 py-2 text-center">
        No exploration data yet...
      </div>
    );
  }

  // Analyze recent strides (last 20)
  const recentStrides = strideSelectionEvents.slice(-20);

  // Count fanout patterns
  const fanoutCounts = {
    narrow: 0,
    balanced: 0,
    wide: 0
  };

  // Count task modes
  const taskModeCounts = {
    focused: 0,
    exploratory: 0,
    balanced: 0
  };

  recentStrides.forEach(stride => {
    // Fanout analysis (based on tier)
    if (stride.tier === 'STRONG') fanoutCounts.narrow++;
    else if (stride.tier === 'MEDIUM') fanoutCounts.balanced++;
    else fanoutCounts.wide++;

    // Task mode analysis (based on need type)
    const need = stride.entity_need_type?.toLowerCase() || '';
    if (need.includes('focus') || need.includes('depth')) taskModeCounts.focused++;
    else if (need.includes('explore') || need.includes('discover')) taskModeCounts.exploratory++;
    else taskModeCounts.balanced++;
  });

  const dominantFanout = fanoutCounts.narrow > fanoutCounts.wide ? 'Narrow' :
                         fanoutCounts.wide > fanoutCounts.narrow ? 'Wide' : 'Balanced';

  const dominantMode = taskModeCounts.focused > taskModeCounts.exploratory ? 'Focused' :
                       taskModeCounts.exploratory > taskModeCounts.focused ? 'Exploratory' : 'Balanced';

  return (
    <div className="space-y-3">
      {/* Fanout Strategy */}
      <div>
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>Fanout</span>
          <span className="text-slate-300">{dominantFanout}</span>
        </div>
        <div className="flex gap-1">
          <div
            className="h-2 bg-blue-500 rounded"
            style={{ width: `${(fanoutCounts.narrow / recentStrides.length) * 100}%` }}
            title="Narrow"
          />
          <div
            className="h-2 bg-yellow-500 rounded"
            style={{ width: `${(fanoutCounts.balanced / recentStrides.length) * 100}%` }}
            title="Balanced"
          />
          <div
            className="h-2 bg-green-500 rounded"
            style={{ width: `${(fanoutCounts.wide / recentStrides.length) * 100}%` }}
            title="Wide"
          />
        </div>
      </div>

      {/* Task Mode */}
      <div>
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>Task Mode</span>
          <span className="text-slate-300">{dominantMode}</span>
        </div>
        <div className="flex gap-1">
          <div
            className="h-2 bg-purple-500 rounded"
            style={{ width: `${(taskModeCounts.focused / recentStrides.length) * 100}%` }}
            title="Focused"
          />
          <div
            className="h-2 bg-cyan-500 rounded"
            style={{ width: `${(taskModeCounts.exploratory / recentStrides.length) * 100}%` }}
            title="Exploratory"
          />
        </div>
      </div>

      <div className="text-xs text-slate-500">
        Based on {recentStrides.length} recent strides
      </div>
    </div>
  );
}
