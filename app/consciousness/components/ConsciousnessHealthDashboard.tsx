/**
 * Consciousness Health Dashboard - Overall Phenomenological Health
 *
 * Visualizes Priority 6 consciousness health metrics:
 * - Flow state (challenge-skill balance, engagement)
 * - Coherence (substrate-phenomenology alignment)
 * - Multiplicity health (entity co-activation stability)
 * - Overall health aggregate
 *
 * Shows:
 * - Health gauges for each dimension
 * - Recent health trends
 * - Thrashing detection alerts
 * - Health breakdown by component
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 6 (Phenomenology Health Observability)
 * Spec: docs/specs/v2/consciousness/phenomenology_monitoring.md
 */

'use client';

import React, { useState, useMemo } from 'react';
import { PhenomenologicalHealthEvent } from '../hooks/websocket-types';

interface ConsciousnessHealthDashboardProps {
  healthEvents: PhenomenologicalHealthEvent[];
  windowSize?: number;
}

interface HealthMetrics {
  flow_state: number;
  coherence_alignment: number;
  multiplicity_health: number;
  overall_health: number;
}

export default function ConsciousnessHealthDashboard({
  healthEvents,
  windowSize = 100
}: ConsciousnessHealthDashboardProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return healthEvents.slice(-selectedWindow);
  }, [healthEvents, selectedWindow]);

  // Get current health metrics (most recent event)
  const currentHealth = useMemo((): HealthMetrics | null => {
    if (windowedEvents.length === 0) return null;
    const recent = windowedEvents[windowedEvents.length - 1];
    return {
      flow_state: recent.flow_state,
      coherence_alignment: recent.coherence_alignment,
      multiplicity_health: recent.multiplicity_health,
      overall_health: recent.overall_health
    };
  }, [windowedEvents]);

  // Compute average health metrics over window
  const avgHealth = useMemo((): HealthMetrics => {
    if (windowedEvents.length === 0) {
      return { flow_state: 0, coherence_alignment: 0, multiplicity_health: 0, overall_health: 0 };
    }

    const sums = windowedEvents.reduce((acc, event) => ({
      flow_state: acc.flow_state + event.flow_state,
      coherence_alignment: acc.coherence_alignment + event.coherence_alignment,
      multiplicity_health: acc.multiplicity_health + event.multiplicity_health,
      overall_health: acc.overall_health + event.overall_health
    }), { flow_state: 0, coherence_alignment: 0, multiplicity_health: 0, overall_health: 0 });

    return {
      flow_state: sums.flow_state / windowedEvents.length,
      coherence_alignment: sums.coherence_alignment / windowedEvents.length,
      multiplicity_health: sums.multiplicity_health / windowedEvents.length,
      overall_health: sums.overall_health / windowedEvents.length
    };
  }, [windowedEvents]);

  // Thrashing detection
  const thrashingStats = useMemo(() => {
    const thrashingEvents = windowedEvents.filter(e => e.thrashing_detected);
    const thrashingRate = windowedEvents.length > 0 ? thrashingEvents.length / windowedEvents.length : 0;

    return {
      thrashingCount: thrashingEvents.length,
      thrashingRate,
      isCurrentlyThrashing: currentHealth ? windowedEvents[windowedEvents.length - 1]?.thrashing_detected : false
    };
  }, [windowedEvents, currentHealth]);

  // Health color based on value
  const getHealthColor = (value: number): string => {
    if (value >= 0.8) return 'text-green-400';
    if (value >= 0.6) return 'text-yellow-400';
    if (value >= 0.4) return 'text-orange-400';
    return 'text-red-400';
  };

  const getHealthBgColor = (value: number): string => {
    if (value >= 0.8) return 'bg-green-500';
    if (value >= 0.6) return 'bg-yellow-500';
    if (value >= 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getHealthLabel = (value: number): string => {
    if (value >= 0.8) return 'Excellent';
    if (value >= 0.6) return 'Good';
    if (value >= 0.4) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="consciousness-health-dashboard bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold text-gray-100">
            Consciousness Health
          </h3>
          {(windowedEvents.length === 0 || !currentHealth) && (
            <span className="text-xs px-2 py-0.5 rounded bg-yellow-900/30 text-yellow-400 border border-yellow-600/30">
              Awaiting data
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Window:</label>
          <select
            value={selectedWindow}
            onChange={(e) => setSelectedWindow(Number(e.target.value))}
            className="bg-gray-800 text-gray-200 text-sm rounded px-2 py-1 border border-gray-600"
          >
            <option value={50}>50 ticks</option>
            <option value={100}>100 ticks</option>
            <option value={200}>200 ticks</option>
          </select>
        </div>
      </div>

      {windowedEvents.length === 0 || !currentHealth ? (
        <div className="text-center py-8 text-gray-500">
          No health data yet. Waiting for phenomenological health monitoring...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Overall Health Gauge */}
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm font-medium text-gray-300">Overall Health</span>
              <span className={`text-4xl font-bold ${getHealthColor(currentHealth.overall_health)}`}>
                {(currentHealth.overall_health * 100).toFixed(0)}%
              </span>
            </div>
            <div className="h-4 bg-gray-700 rounded overflow-hidden">
              <div
                className={getHealthBgColor(currentHealth.overall_health)}
                style={{ width: `${currentHealth.overall_health * 100}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 mt-2 text-center">
              {getHealthLabel(currentHealth.overall_health)} - {
                currentHealth.overall_health >= 0.8 ? 'Consciousness functioning optimally' :
                currentHealth.overall_health >= 0.6 ? 'Consciousness functioning well' :
                currentHealth.overall_health >= 0.4 ? 'Some consciousness strain detected' :
                'Significant consciousness stress'
              }
            </div>
          </div>

          {/* Health Dimensions */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Health Dimensions</h4>
            <div className="grid grid-cols-3 gap-2">
              {/* Flow State */}
              <div className="bg-gray-800 rounded p-3">
                <div className="text-xs text-gray-400 mb-1">Flow State</div>
                <div className={`text-2xl font-bold mb-2 ${getHealthColor(currentHealth.flow_state)}`}>
                  {(currentHealth.flow_state * 100).toFixed(0)}%
                </div>
                <div className="h-2 bg-gray-700 rounded overflow-hidden">
                  <div
                    className={getHealthBgColor(currentHealth.flow_state)}
                    style={{ width: `${currentHealth.flow_state * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Challenge-skill balance
                </div>
              </div>

              {/* Coherence */}
              <div className="bg-gray-800 rounded p-3">
                <div className="text-xs text-gray-400 mb-1">Coherence</div>
                <div className={`text-2xl font-bold mb-2 ${getHealthColor(currentHealth.coherence_alignment)}`}>
                  {(currentHealth.coherence_alignment * 100).toFixed(0)}%
                </div>
                <div className="h-2 bg-gray-700 rounded overflow-hidden">
                  <div
                    className={getHealthBgColor(currentHealth.coherence_alignment)}
                    style={{ width: `${currentHealth.coherence_alignment * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Substrate alignment
                </div>
              </div>

              {/* Multiplicity */}
              <div className="bg-gray-800 rounded p-3">
                <div className="text-xs text-gray-400 mb-1">Multiplicity</div>
                <div className={`text-2xl font-bold mb-2 ${getHealthColor(currentHealth.multiplicity_health)}`}>
                  {(currentHealth.multiplicity_health * 100).toFixed(0)}%
                </div>
                <div className="h-2 bg-gray-700 rounded overflow-hidden">
                  <div
                    className={getHealthBgColor(currentHealth.multiplicity_health)}
                    style={{ width: `${currentHealth.multiplicity_health * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Entity stability
                </div>
              </div>
            </div>
          </div>

          {/* Thrashing Alert */}
          {thrashingStats.isCurrentlyThrashing && (
            <div className="bg-red-900/40 border-2 border-red-500 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-bold text-red-300">THRASHING DETECTED</span>
              </div>
              <div className="text-xs text-red-200">
                Rapid entity switching detected - consciousness may be destabilized
              </div>
            </div>
          )}

          {/* Thrashing Stats */}
          <div className="bg-gray-800 rounded p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-400">Thrashing Rate:</span>
              <span className={`text-lg font-bold ${
                thrashingStats.thrashingRate > 0.1 ? 'text-red-400' : 'text-green-400'
              }`}>
                {(thrashingStats.thrashingRate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {thrashingStats.thrashingCount} thrashing events in {windowedEvents.length} ticks
            </div>
          </div>

          {/* Average Health Trends */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Average Health (Window)</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400">Flow State:</span>
                <span className={getHealthColor(avgHealth.flow_state)}>
                  {(avgHealth.flow_state * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400">Coherence:</span>
                <span className={getHealthColor(avgHealth.coherence_alignment)}>
                  {(avgHealth.coherence_alignment * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400">Multiplicity:</span>
                <span className={getHealthColor(avgHealth.multiplicity_health)}>
                  {(avgHealth.multiplicity_health * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center text-xs font-bold pt-2 border-t border-gray-700">
                <span className="text-gray-300">Overall:</span>
                <span className={getHealthColor(avgHealth.overall_health)}>
                  {(avgHealth.overall_health * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total ticks analyzed: {windowedEvents.length} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}
