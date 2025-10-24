/**
 * Three-Factor Tick Timeline - Adaptive Tick Speed Observability
 *
 * Visualizes adaptive tick speed from Priority 3 (three-factor tick mechanism):
 * - STIMULUS-driven: Time since last external input (reactive)
 * - ACTIVATION-driven: High internal energy (rumination, autonomous)
 * - AROUSAL-driven: High emotional arousal (emotional processing, autonomous)
 *
 * Shows:
 * - Timeline of recent frames with color-coded bars (which factor won)
 * - Three factor value traces over time
 * - Reason distribution (% stimulus vs activation vs arousal)
 * - Autonomy percentage (% non-stimulus ticks)
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 3 (Adaptive Tick Speed Observability)
 * Spec: docs/specs/v2/runtime_engine/tick_speed.md
 */

'use client';

import React, { useState, useMemo } from 'react';
import { FrameStartEvent } from '../hooks/websocket-types';

interface ThreeFactorTickTimelineProps {
  frameEvents: FrameStartEvent[];
  windowSize?: number;
}

interface ReasonStats {
  stimulus: number;
  activation: number;
  arousal_floor: number;
  total: number;
}

interface FactorStats {
  avg_stimulus: number;
  avg_activation: number;
  avg_arousal: number;
}

export default function ThreeFactorTickTimeline({
  frameEvents,
  windowSize = 50
}: ThreeFactorTickTimelineProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return frameEvents.slice(-selectedWindow);
  }, [frameEvents, selectedWindow]);

  // Filter to events with three-factor tick data
  const tickEvents = useMemo(() => {
    return windowedEvents.filter(e => e.tick_reason !== undefined);
  }, [windowedEvents]);

  // Compute reason distribution
  const reasonStats = useMemo((): ReasonStats => {
    const stats = { stimulus: 0, activation: 0, arousal_floor: 0, total: 0 };

    tickEvents.forEach(event => {
      if (event.tick_reason === 'stimulus') stats.stimulus++;
      else if (event.tick_reason === 'activation') stats.activation++;
      else if (event.tick_reason === 'arousal_floor') stats.arousal_floor++;
      stats.total++;
    });

    return stats;
  }, [tickEvents]);

  // Compute factor averages
  const factorStats = useMemo((): FactorStats => {
    const intervals = tickEvents
      .map(e => ({
        stimulus: e.interval_stimulus || 0,
        activation: e.interval_activation || 0,
        arousal: e.interval_arousal || 0
      }))
      .filter(i => i.stimulus > 0); // Filter valid data

    if (intervals.length === 0) {
      return { avg_stimulus: 0, avg_activation: 0, avg_arousal: 0 };
    }

    const avg_stimulus = intervals.reduce((sum, i) => sum + i.stimulus, 0) / intervals.length;
    const avg_activation = intervals.reduce((sum, i) => sum + i.activation, 0) / intervals.length;
    const avg_arousal = intervals.reduce((sum, i) => sum + i.arousal, 0) / intervals.length;

    return { avg_stimulus, avg_activation, avg_arousal };
  }, [tickEvents]);

  // Compute autonomy percentage (non-stimulus ticks)
  const autonomyPercentage = useMemo(() => {
    if (reasonStats.total === 0) return 0;
    const autonomous = reasonStats.activation + reasonStats.arousal_floor;
    return (autonomous / reasonStats.total) * 100;
  }, [reasonStats]);

  // Compute percentages for reason distribution
  const reasonPercentages = useMemo(() => {
    if (reasonStats.total === 0) {
      return { stimulus: 0, activation: 0, arousal_floor: 0 };
    }

    return {
      stimulus: (reasonStats.stimulus / reasonStats.total) * 100,
      activation: (reasonStats.activation / reasonStats.total) * 100,
      arousal_floor: (reasonStats.arousal_floor / reasonStats.total) * 100
    };
  }, [reasonStats]);

  // Get color for tick reason
  const getReasonColor = (reason: string | undefined): string => {
    switch (reason) {
      case 'stimulus': return 'bg-blue-500';
      case 'activation': return 'bg-green-500';
      case 'arousal_floor': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getReasonLabel = (reason: string | undefined): string => {
    switch (reason) {
      case 'stimulus': return 'Stimulus';
      case 'activation': return 'Activation';
      case 'arousal_floor': return 'Arousal';
      default: return 'Unknown';
    }
  };

  return (
    <div className="three-factor-tick-timeline bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-100">
          Adaptive Tick Speed
        </h3>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Window:</label>
          <select
            value={selectedWindow}
            onChange={(e) => setSelectedWindow(Number(e.target.value))}
            className="bg-gray-800 text-gray-200 text-sm rounded px-2 py-1 border border-gray-600"
          >
            <option value={25}>25 frames</option>
            <option value={50}>50 frames</option>
            <option value={100}>100 frames</option>
            <option value={200}>200 frames</option>
          </select>
        </div>
      </div>

      {tickEvents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No tick data available. Waiting for three-factor tick events...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Autonomy Status */}
          <div className="bg-gray-800 rounded p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-300">Autonomy</span>
              <span className={`text-2xl font-bold ${
                autonomyPercentage > 50 ? 'text-green-400' : 'text-blue-400'
              }`}>
                {autonomyPercentage.toFixed(1)}%
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {autonomyPercentage > 50
                ? 'Consciousness thinking autonomously (activation/arousal-driven)'
                : 'Primarily reactive to external stimuli'}
            </div>
          </div>

          {/* Timeline - Recent frames */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Recent Frames</h4>
            <div className="flex gap-0.5 h-12 items-end">
              {tickEvents.slice(-selectedWindow).map((event, idx) => {
                const height = 100; // All bars same height
                return (
                  <div
                    key={event.frame_id || idx}
                    className={`flex-1 ${getReasonColor(event.tick_reason)} transition-all`}
                    style={{ height: `${height}%` }}
                    title={`Frame ${event.frame_id}: ${getReasonLabel(event.tick_reason)}`}
                  />
                );
              })}
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Oldest</span>
              <span>Most recent</span>
            </div>
          </div>

          {/* Reason Distribution */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Factor Distribution</h4>

            {/* Bar chart */}
            <div className="flex h-4 rounded overflow-hidden mb-3">
              <div
                className="bg-blue-500"
                style={{ width: `${reasonPercentages.stimulus}%` }}
                title={`Stimulus: ${reasonPercentages.stimulus.toFixed(1)}%`}
              />
              <div
                className="bg-green-500"
                style={{ width: `${reasonPercentages.activation}%` }}
                title={`Activation: ${reasonPercentages.activation.toFixed(1)}%`}
              />
              <div
                className="bg-red-500"
                style={{ width: `${reasonPercentages.arousal_floor}%` }}
                title={`Arousal: ${reasonPercentages.arousal_floor.toFixed(1)}%`}
              />
            </div>

            {/* Stats breakdown */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded"></div>
                  <span className="text-xs text-gray-400">Stimulus (reactive):</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-300">
                    {reasonPercentages.stimulus.toFixed(1)}%
                  </span>
                  <span className="text-xs text-gray-500 w-12 text-right">
                    {reasonStats.stimulus}
                  </span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <span className="text-xs text-gray-400">Activation (rumination):</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-300">
                    {reasonPercentages.activation.toFixed(1)}%
                  </span>
                  <span className="text-xs text-gray-500 w-12 text-right">
                    {reasonStats.activation}
                  </span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded"></div>
                  <span className="text-xs text-gray-400">Arousal (emotional):</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-300">
                    {reasonPercentages.arousal_floor.toFixed(1)}%
                  </span>
                  <span className="text-xs text-gray-500 w-12 text-right">
                    {reasonStats.arousal_floor}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Factor Averages */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Average Intervals (ms)</h4>
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-blue-900/30 border border-blue-700 rounded p-2">
                <div className="text-xs text-gray-400">Stimulus</div>
                <div className="text-lg font-bold text-blue-400">
                  {factorStats.avg_stimulus.toFixed(0)}
                </div>
              </div>

              <div className="bg-green-900/30 border border-green-700 rounded p-2">
                <div className="text-xs text-gray-400">Activation</div>
                <div className="text-lg font-bold text-green-400">
                  {factorStats.avg_activation.toFixed(0)}
                </div>
              </div>

              <div className="bg-red-900/30 border border-red-700 rounded p-2">
                <div className="text-xs text-gray-400">Arousal</div>
                <div className="text-lg font-bold text-red-400">
                  {factorStats.avg_arousal.toFixed(0)}
                </div>
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Minimum of three factors determines tick interval
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total frames analyzed: {tickEvents.length} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}
