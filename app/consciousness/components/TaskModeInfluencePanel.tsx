/**
 * Task Mode Influence Panel - Task Mode Behavioral Analysis
 *
 * Visualizes how task modes shape consciousness behavior:
 * - Task mode distribution (focused/balanced/divergent/methodical)
 * - Mode-specific patterns (top-k values, fanout preferences)
 * - Mode transitions over time
 * - Structure vs mode alignment
 *
 * Shows:
 * - Active task mode frequency
 * - Average top-k by mode
 * - Mode switching patterns
 * - Structural override patterns
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 5 (Task-Mode Fan-out Observability)
 * Spec: docs/specs/v2/traversal/task_mode_fanout.md
 */

'use client';

import React, { useState, useMemo } from 'react';
import { StrideSelectionEvent } from '../hooks/websocket-types';

interface TaskModeInfluencePanelProps {
  strideSelectionEvents: StrideSelectionEvent[];
  windowSize?: number;
}

interface ModePatterns {
  mode: string;
  count: number;
  avg_top_k: number;
  override_rate: number;
}

export default function TaskModeInfluencePanel({
  strideSelectionEvents,
  windowSize = 100
}: TaskModeInfluencePanelProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return strideSelectionEvents.slice(-selectedWindow);
  }, [strideSelectionEvents, selectedWindow]);

  // Get current task mode (most recent)
  const currentMode = useMemo(() => {
    if (windowedEvents.length === 0) return null;
    return windowedEvents[windowedEvents.length - 1].task_mode;
  }, [windowedEvents]);

  // Compute mode patterns
  const modePatterns = useMemo((): ModePatterns[] => {
    const patterns: Map<string, {
      count: number;
      top_k_sum: number;
      override_count: number;
    }> = new Map();

    windowedEvents.forEach(event => {
      const mode = event.task_mode || 'none';
      if (!patterns.has(mode)) {
        patterns.set(mode, {
          count: 0,
          top_k_sum: 0,
          override_count: 0
        });
      }

      const pattern = patterns.get(mode)!;
      pattern.count++;
      pattern.top_k_sum += event.top_k;
      if (event.task_mode_override) {
        pattern.override_count++;
      }
    });

    // Convert to array and compute averages
    const result: ModePatterns[] = [];
    patterns.forEach((data, mode) => {
      result.push({
        mode,
        count: data.count,
        avg_top_k: data.count > 0 ? data.top_k_sum / data.count : 0,
        override_rate: data.count > 0 ? data.override_count / data.count : 0
      });
    });

    // Sort by count (most frequent first)
    return result.sort((a, b) => b.count - a.count);
  }, [windowedEvents]);

  // Compute mode transitions
  const modeTransitions = useMemo(() => {
    let transitionCount = 0;
    let previousMode: string | null = null;

    windowedEvents.forEach(event => {
      const currentMode = event.task_mode || 'none';
      if (previousMode !== null && previousMode !== currentMode) {
        transitionCount++;
      }
      previousMode = currentMode;
    });

    return {
      transitionCount,
      transitionRate: windowedEvents.length > 1 ? transitionCount / (windowedEvents.length - 1) : 0
    };
  }, [windowedEvents]);

  // Mode color mapping
  const getModeColor = (mode: string | null): string => {
    switch (mode) {
      case 'focused': return 'text-blue-400';
      case 'balanced': return 'text-green-400';
      case 'divergent': return 'text-purple-400';
      case 'methodical': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  const getModeBgColor = (mode: string): string => {
    switch (mode) {
      case 'focused': return 'bg-blue-900/30 border-blue-700';
      case 'balanced': return 'bg-green-900/30 border-green-700';
      case 'divergent': return 'bg-purple-900/30 border-purple-700';
      case 'methodical': return 'bg-orange-900/30 border-orange-700';
      default: return 'bg-gray-800 border-gray-600';
    }
  };

  const getModeDescription = (mode: string | null): string => {
    switch (mode) {
      case 'focused': return 'Narrow exploration - pursuing specific goal';
      case 'balanced': return 'Moderate exploration - balanced search';
      case 'divergent': return 'Broad exploration - discovering connections';
      case 'methodical': return 'Systematic exploration - covering territory';
      default: return 'No active task mode - structure-driven';
    }
  };

  return (
    <div className="task-mode-influence-panel bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-100">
          Task Mode Influence
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
          No task mode data yet. Waiting for stride selection events...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Current Mode */}
          <div className={`border rounded-lg p-3 ${getModeBgColor(currentMode || 'none')}`}>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-400">Current Mode:</span>
              <span className={`text-xl font-bold ${getModeColor(currentMode)}`}>
                {currentMode?.toUpperCase() || 'NONE'}
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {getModeDescription(currentMode)}
            </div>
          </div>

          {/* Mode Patterns */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Mode Patterns</h4>
            <div className="space-y-2">
              {modePatterns.map(pattern => (
                <div
                  key={pattern.mode}
                  className={`border rounded p-2 ${getModeBgColor(pattern.mode)}`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className={`text-sm font-bold ${getModeColor(pattern.mode)}`}>
                      {pattern.mode.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-400">
                      {pattern.count} strides
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Avg top-k:</span>
                      <span className="text-gray-300 font-bold">
                        {pattern.avg_top_k.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Override rate:</span>
                      <span className={`font-bold ${
                        pattern.override_rate > 0.5 ? 'text-orange-400' : 'text-green-400'
                      }`}>
                        {(pattern.override_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Mode Switching */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Mode Stability</h4>
            <div className="bg-gray-800 rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400">Transitions:</span>
                <span className="text-lg font-bold text-gray-200">
                  {modeTransitions.transitionCount}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Transition Rate:</span>
                <span className={`text-lg font-bold ${
                  modeTransitions.transitionRate > 0.3 ? 'text-orange-400' : 'text-green-400'
                }`}>
                  {(modeTransitions.transitionRate * 100).toFixed(1)}%
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-2">
                {modeTransitions.transitionRate > 0.3
                  ? 'Frequent mode switching - task context changing rapidly'
                  : 'Stable mode - sustained task focus'}
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total strides analyzed: {windowedEvents.length} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}
