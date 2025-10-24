/**
 * Fanout Strategy Panel - Task-Mode Stride Selection Observability
 *
 * Visualizes Priority 5 adaptive stride selection:
 * - Strategy distribution (selective/balanced/exhaustive)
 * - Task mode influence on candidate selection
 * - WM headroom correlation with strategy choice
 * - Top-k parameter adaptation
 *
 * Shows:
 * - Strategy breakdown over rolling window
 * - Task mode distribution (focused/balanced/divergent/methodical)
 * - WM headroom vs strategy correlation
 * - Override frequency (task mode overriding structure-suggested strategy)
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 5 (Task-Mode Fan-out Observability)
 * Spec: docs/specs/v2/traversal/task_mode_fanout.md
 */

'use client';

import React, { useState, useMemo } from 'react';
import { StrideSelectionEvent } from '../hooks/websocket-types';

interface FanoutStrategyPanelProps {
  strideSelectionEvents: StrideSelectionEvent[];
  windowSize?: number;
}

interface StrategyStats {
  selective: number;
  balanced: number;
  exhaustive: number;
  total: number;
}

interface TaskModeStats {
  focused: number;
  balanced: number;
  divergent: number;
  methodical: number;
  null: number;
  total: number;
}

export default function FanoutStrategyPanel({
  strideSelectionEvents,
  windowSize = 100
}: FanoutStrategyPanelProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return strideSelectionEvents.slice(-selectedWindow);
  }, [strideSelectionEvents, selectedWindow]);

  // Compute strategy distribution
  const strategyStats = useMemo((): StrategyStats => {
    const stats = { selective: 0, balanced: 0, exhaustive: 0, total: 0 };

    windowedEvents.forEach(event => {
      if (event.strategy === 'selective') stats.selective++;
      else if (event.strategy === 'balanced') stats.balanced++;
      else if (event.strategy === 'exhaustive') stats.exhaustive++;
      stats.total++;
    });

    return stats;
  }, [windowedEvents]);

  // Compute task mode distribution
  const taskModeStats = useMemo((): TaskModeStats => {
    const stats = { focused: 0, balanced: 0, divergent: 0, methodical: 0, null: 0, total: 0 };

    windowedEvents.forEach(event => {
      if (event.task_mode === 'focused') stats.focused++;
      else if (event.task_mode === 'balanced') stats.balanced++;
      else if (event.task_mode === 'divergent') stats.divergent++;
      else if (event.task_mode === 'methodical') stats.methodical++;
      else stats.null++;
      stats.total++;
    });

    return stats;
  }, [windowedEvents]);

  // Compute override frequency
  const overrideStats = useMemo(() => {
    const overrideCount = windowedEvents.filter(e => e.task_mode_override).length;
    const total = windowedEvents.length;
    const overrideRate = total > 0 ? overrideCount / total : 0;

    return {
      overrideCount,
      total,
      overrideRate
    };
  }, [windowedEvents]);

  // Compute average WM headroom by strategy
  const wmHeadroomByStrategy = useMemo(() => {
    const byStrategy = {
      selective: [] as number[],
      balanced: [] as number[],
      exhaustive: [] as number[]
    };

    windowedEvents.forEach(event => {
      if (event.strategy in byStrategy) {
        byStrategy[event.strategy as keyof typeof byStrategy].push(event.wm_headroom);
      }
    });

    return {
      selective: byStrategy.selective.length > 0
        ? byStrategy.selective.reduce((sum, val) => sum + val, 0) / byStrategy.selective.length
        : 0,
      balanced: byStrategy.balanced.length > 0
        ? byStrategy.balanced.reduce((sum, val) => sum + val, 0) / byStrategy.balanced.length
        : 0,
      exhaustive: byStrategy.exhaustive.length > 0
        ? byStrategy.exhaustive.reduce((sum, val) => sum + val, 0) / byStrategy.exhaustive.length
        : 0
    };
  }, [windowedEvents]);

  // Compute strategy percentages
  const strategyPercentages = useMemo(() => {
    if (strategyStats.total === 0) {
      return { selective: 0, balanced: 0, exhaustive: 0 };
    }

    return {
      selective: (strategyStats.selective / strategyStats.total) * 100,
      balanced: (strategyStats.balanced / strategyStats.total) * 100,
      exhaustive: (strategyStats.exhaustive / strategyStats.total) * 100
    };
  }, [strategyStats]);

  // Get strategy color
  const getStrategyColor = (strategy: string): string => {
    switch (strategy) {
      case 'selective': return 'bg-blue-500';
      case 'balanced': return 'bg-yellow-500';
      case 'exhaustive': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="fanout-strategy-panel bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-100">
          Stride Selection Strategy
        </h3>

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
          </select>
        </div>
      </div>

      {windowedEvents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No stride selection events yet. Waiting for task-mode fan-out data...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Strategy Distribution */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Strategy Distribution</h4>

            {/* Bar chart */}
            <div className="flex h-6 rounded overflow-hidden mb-3">
              <div
                className="bg-blue-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${strategyPercentages.selective}%` }}
                title={`Selective: ${strategyPercentages.selective.toFixed(1)}%`}
              >
                {strategyPercentages.selective > 15 ? `${strategyPercentages.selective.toFixed(0)}%` : ''}
              </div>
              <div
                className="bg-yellow-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${strategyPercentages.balanced}%` }}
                title={`Balanced: ${strategyPercentages.balanced.toFixed(1)}%`}
              >
                {strategyPercentages.balanced > 15 ? `${strategyPercentages.balanced.toFixed(0)}%` : ''}
              </div>
              <div
                className="bg-red-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${strategyPercentages.exhaustive}%` }}
                title={`Exhaustive: ${strategyPercentages.exhaustive.toFixed(1)}%`}
              >
                {strategyPercentages.exhaustive > 15 ? `${strategyPercentages.exhaustive.toFixed(0)}%` : ''}
              </div>
            </div>

            {/* Stats breakdown */}
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-blue-900/30 border border-blue-700 rounded p-2">
                <div className="text-xs text-gray-400">Selective</div>
                <div className="text-lg font-bold text-blue-400">
                  {strategyStats.selective}
                </div>
                <div className="text-xs text-gray-500">
                  {strategyPercentages.selective.toFixed(1)}%
                </div>
              </div>

              <div className="bg-yellow-900/30 border border-yellow-700 rounded p-2">
                <div className="text-xs text-gray-400">Balanced</div>
                <div className="text-lg font-bold text-yellow-400">
                  {strategyStats.balanced}
                </div>
                <div className="text-xs text-gray-500">
                  {strategyPercentages.balanced.toFixed(1)}%
                </div>
              </div>

              <div className="bg-red-900/30 border border-red-700 rounded p-2">
                <div className="text-xs text-gray-400">Exhaustive</div>
                <div className="text-lg font-bold text-red-400">
                  {strategyStats.exhaustive}
                </div>
                <div className="text-xs text-gray-500">
                  {strategyPercentages.exhaustive.toFixed(1)}%
                </div>
              </div>
            </div>
          </div>

          {/* Task Mode Override */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Task Mode Influence</h4>
            <div className="bg-gray-800 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400">Override Rate:</span>
                <span className={`text-2xl font-bold ${
                  overrideStats.overrideRate > 0.5 ? 'text-orange-400' : 'text-green-400'
                }`}>
                  {(overrideStats.overrideRate * 100).toFixed(1)}%
                </span>
              </div>
              <div className="text-xs text-gray-500">
                {overrideStats.overrideCount} of {overrideStats.total} strides had task mode override structure-suggested strategy
              </div>
            </div>
          </div>

          {/* WM Headroom Correlation */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">WM Headroom by Strategy</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center bg-blue-900/20 rounded p-2">
                <span className="text-xs text-blue-400">Selective:</span>
                <span className="text-sm font-bold text-blue-300">
                  {(wmHeadroomByStrategy.selective * 100).toFixed(0)}% capacity
                </span>
              </div>
              <div className="flex justify-between items-center bg-yellow-900/20 rounded p-2">
                <span className="text-xs text-yellow-400">Balanced:</span>
                <span className="text-sm font-bold text-yellow-300">
                  {(wmHeadroomByStrategy.balanced * 100).toFixed(0)}% capacity
                </span>
              </div>
              <div className="flex justify-between items-center bg-red-900/20 rounded p-2">
                <span className="text-xs text-red-400">Exhaustive:</span>
                <span className="text-sm font-bold text-red-300">
                  {(wmHeadroomByStrategy.exhaustive * 100).toFixed(0)}% capacity
                </span>
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Average WM headroom when each strategy is chosen
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total strides analyzed: {strategyStats.total} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}
