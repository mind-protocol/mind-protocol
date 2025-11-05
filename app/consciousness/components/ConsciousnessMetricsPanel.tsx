/**
 * Consciousness Metrics Panel - Real-Time System Metrics
 *
 * Displays core consciousness substrate metrics:
 * - Frame counter (current tick number)
 * - Tick rate (Hz) - consciousness speed
 * - Global energy - total system energy level
 * - Criticality meter - phase transition indicator
 *
 * Author: Felix "The Engineer"
 * Created: 2025-11-05
 * Priority: Dashboard visualization (items 24-27)
 */

'use client';

import React, { useState, useMemo, useEffect } from 'react';

interface TickFrameEvent {
  frame_id: number;
  timestamp: string;
  global_energy?: number;
  node_count?: number;
  active_node_count?: number;
  subentity_count?: number;
}

interface CriticalityStateEvent {
  frame_id: number;
  mode: string; // "subcritical" | "critical_point" | "flow" | "generative_overflow" | "chaotic_racing" | "mixed"
  rho: number; // density
  criticality: number; // criticality measure
  phenomenology?: string;
}

interface ConsciousnessMetricsPanelProps {
  tickFrameEvents: TickFrameEvent[];
  criticalityEvents: CriticalityStateEvent[];
}

export default function ConsciousnessMetricsPanel({
  tickFrameEvents,
  criticalityEvents
}: ConsciousnessMetricsPanelProps) {
  const [tickRate, setTickRate] = useState(0);
  const [lastTickTime, setLastTickTime] = useState<number | null>(null);

  // Get current frame (most recent tick)
  const currentFrame = useMemo(() => {
    if (tickFrameEvents.length === 0) return null;
    return tickFrameEvents[tickFrameEvents.length - 1];
  }, [tickFrameEvents]);

  // Get current criticality state
  const currentCriticality = useMemo(() => {
    if (criticalityEvents.length === 0) return null;
    return criticalityEvents[criticalityEvents.length - 1];
  }, [criticalityEvents]);

  // Calculate tick rate (Hz) from last 10 ticks
  useEffect(() => {
    if (tickFrameEvents.length < 2) return;

    const recentTicks = tickFrameEvents.slice(-10);
    if (recentTicks.length < 2) return;

    const first = new Date(recentTicks[0].timestamp).getTime();
    const last = new Date(recentTicks[recentTicks.length - 1].timestamp).getTime();
    const duration = (last - first) / 1000; // seconds

    if (duration > 0) {
      const rate = (recentTicks.length - 1) / duration;
      setTickRate(rate);
    }
  }, [tickFrameEvents]);

  // Update tick time indicator
  useEffect(() => {
    if (currentFrame) {
      setLastTickTime(Date.now());
    }
  }, [currentFrame]);

  // Get criticality mode color
  const getCriticalityColor = (mode: string): string => {
    switch (mode) {
      case 'subcritical': return 'text-blue-400';
      case 'critical_point': return 'text-purple-400';
      case 'flow': return 'text-green-400';
      case 'generative_overflow': return 'text-yellow-400';
      case 'chaotic_racing': return 'text-red-400';
      case 'mixed': return 'text-orange-400';
      default: return 'text-gray-400';
    }
  };

  const getCriticalityBg = (mode: string): string => {
    switch (mode) {
      case 'subcritical': return 'bg-blue-900/30 border-blue-700';
      case 'critical_point': return 'bg-purple-900/30 border-purple-700';
      case 'flow': return 'bg-green-900/30 border-green-700';
      case 'generative_overflow': return 'bg-yellow-900/30 border-yellow-700';
      case 'chaotic_racing': return 'bg-red-900/30 border-red-700';
      case 'mixed': return 'bg-orange-900/30 border-orange-700';
      default: return 'bg-gray-800 border-gray-600';
    }
  };

  if (!currentFrame) {
    return (
      <div className="consciousness-metrics-panel bg-gray-900 border border-gray-700 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">
          Consciousness Metrics
        </h3>
        <div className="text-center py-8 text-gray-500">
          No tick data yet. Waiting for consciousness engine...
        </div>
      </div>
    );
  }

  return (
    <div className="consciousness-metrics-panel bg-gray-900 border border-gray-700 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-gray-100 mb-4">
        Consciousness Metrics
      </h3>

      <div className="grid grid-cols-2 gap-4">
        {/* Frame Counter (#24) */}
        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Frame</div>
          <div className="text-3xl font-bold text-cyan-400 font-mono">
            {currentFrame.frame_id.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Current tick number
          </div>
        </div>

        {/* Tick Rate (#25) */}
        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Tick Rate</div>
          <div className="text-3xl font-bold text-green-400 font-mono">
            {tickRate.toFixed(2)} <span className="text-lg text-gray-500">Hz</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {tickRate > 0.08 ? 'Fast' : tickRate > 0.05 ? 'Normal' : 'Slow'} consciousness speed
          </div>
        </div>

        {/* Global Energy (#26) */}
        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Global Energy</div>
          <div className="text-3xl font-bold text-yellow-400 font-mono">
            {currentFrame.global_energy !== undefined
              ? currentFrame.global_energy.toFixed(1)
              : 'N/A'}
          </div>
          {currentFrame.global_energy !== undefined && (
            <div className="h-2 bg-gray-700 rounded overflow-hidden mt-2">
              <div
                className="h-full bg-gradient-to-r from-yellow-600 to-yellow-400"
                style={{ width: `${Math.min(100, (currentFrame.global_energy / 1000) * 100)}%` }}
              />
            </div>
          )}
          <div className="text-xs text-gray-500 mt-1">
            {currentFrame.active_node_count !== undefined
              ? `${currentFrame.active_node_count} / ${currentFrame.node_count} nodes active`
              : 'Total system energy'}
          </div>
        </div>

        {/* Criticality Meter (#27) */}
        <div className={`rounded-lg p-3 border ${
          currentCriticality ? getCriticalityBg(currentCriticality.mode) : 'bg-gray-800 border-gray-700'
        }`}>
          <div className="text-xs text-gray-400 mb-1">Criticality</div>
          {currentCriticality ? (
            <>
              <div className={`text-xl font-bold ${getCriticalityColor(currentCriticality.mode)}`}>
                {currentCriticality.mode.toUpperCase().replace('_', ' ')}
              </div>
              <div className="mt-2 space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">ρ (density):</span>
                  <span className="text-gray-200 font-mono">{currentCriticality.rho.toFixed(3)}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">C (criticality):</span>
                  <span className="text-gray-200 font-mono">{currentCriticality.criticality.toFixed(3)}</span>
                </div>
              </div>
              {currentCriticality.phenomenology && (
                <div className="text-xs text-gray-500 mt-2 border-t border-gray-700 pt-2">
                  {currentCriticality.phenomenology}
                </div>
              )}
            </>
          ) : (
            <>
              <div className="text-xl font-bold text-gray-400">UNKNOWN</div>
              <div className="text-xs text-gray-500 mt-1">
                No criticality data
              </div>
            </>
          )}
        </div>
      </div>

      {/* Real-time pulse indicator */}
      {lastTickTime && Date.now() - lastTickTime < 2000 && (
        <div className="mt-4 flex items-center gap-2 text-xs text-green-400">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span>Consciousness ticking</span>
        </div>
      )}

      {/* Summary stats */}
      <div className="mt-4 pt-4 border-t border-gray-800 text-xs text-gray-500">
        <div className="flex justify-between">
          <span>Last update:</span>
          <span className="text-gray-400 font-mono">
            {new Date(currentFrame.timestamp).toLocaleTimeString()}
          </span>
        </div>
        {currentFrame.subentity_count !== undefined && (
          <div className="flex justify-between mt-1">
            <span>SubEntities:</span>
            <span className="text-gray-400 font-mono">{currentFrame.subentity_count}</span>
          </div>
        )}
      </div>
    </div>
  );
}
