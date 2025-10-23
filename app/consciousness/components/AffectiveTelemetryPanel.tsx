/**
 * Affective Telemetry Panel
 *
 * PR-A: Instrumentation Foundation for Affective Coupling
 *
 * Displays real-time telemetry for affective mechanisms:
 * - Event counts by type (11 affective event types)
 * - Sample rate and buffer utilization
 * - Event schema validation status
 *
 * Per IMPLEMENTATION_PLAN.md PR-A.5:
 * "Add affective telemetry panel to Mind Harbor. Display event counts by type.
 * Show sample rate and buffer utilization. Add event schema validator UI."
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 * PR: PR-A (Instrumentation Foundation - ZERO RISK)
 */

'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

/**
 * Affective event type names per IMPLEMENTATION_PLAN.md A.2
 */
const AFFECTIVE_EVENT_TYPES = [
  'affective.threshold',
  'affective.memory',
  'coherence.persistence',
  'pattern.multiresponse',
  'identity.multiplicity',
  'consolidation',
  'decay.resistance',
  'diffusion.stickiness',
  'affective.priming',
  'coherence.metric',
  'criticality.mode'
] as const;

type AffectiveEventType = typeof AFFECTIVE_EVENT_TYPES[number];

interface EventCounts {
  [key: string]: number;
}

interface TelemetryMetrics {
  sampleRate: number;
  bufferUtilization: number; // 0-1
  bufferSize: number;
  totalEventsEmitted: number;
  totalEventsSampled: number;
}

interface SchemaValidation {
  isValid: boolean;
  errors: string[];
  lastChecked: number;
}

/**
 * Affective Telemetry Panel Component
 *
 * Left sidebar panel showing affective mechanism telemetry.
 */
export function AffectiveTelemetryPanel() {
  const { connectionState } = useWebSocket();

  // Event counters (per event type)
  const [eventCounts, setEventCounts] = useState<EventCounts>({});

  // Telemetry metrics
  const [metrics, setMetrics] = useState<TelemetryMetrics>({
    sampleRate: 1.0,
    bufferUtilization: 0,
    bufferSize: 1000,
    totalEventsEmitted: 0,
    totalEventsSampled: 0
  });

  // Schema validation status
  const [validation, setValidation] = useState<SchemaValidation>({
    isValid: true,
    errors: [],
    lastChecked: Date.now()
  });

  // Poll telemetry metrics from backend
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch('/api/consciousness/affective-telemetry/metrics');
        if (res.ok) {
          const data = await res.json();
          setMetrics(data.metrics || metrics);
          setEventCounts(data.eventCounts || {});
        }
      } catch (error) {
        console.log('[AffectiveTelemetryPanel] Metrics not available yet:', error);
      }
    };

    // Initial fetch
    fetchMetrics();

    // Poll every 2 seconds
    const interval = setInterval(fetchMetrics, 2000);

    return () => clearInterval(interval);
  }, []);

  // Validate event schemas
  const validateSchemas = async () => {
    try {
      const res = await fetch('/api/consciousness/affective-telemetry/validate-schemas');
      if (res.ok) {
        const data = await res.json();
        setValidation({
          isValid: data.isValid,
          errors: data.errors || [],
          lastChecked: Date.now()
        });
      }
    } catch (error) {
      setValidation({
        isValid: false,
        errors: ['Failed to validate schemas: ' + (error as Error).message],
        lastChecked: Date.now()
      });
    }
  };

  // Get total event count across all types
  const totalEvents = Object.values(eventCounts).reduce((sum, count) => sum + count, 0);

  // Get sampling efficiency (sampled / emitted)
  const samplingEfficiency = metrics.totalEventsEmitted > 0
    ? (metrics.totalEventsSampled / metrics.totalEventsEmitted * 100).toFixed(1)
    : '0.0';

  return (
    <div className="fixed left-4 bottom-4 w-80 max-h-[50vh] consciousness-panel border border-observatory-teal overflow-hidden flex flex-col z-40 rounded-lg">
      {/* Header */}
      <div className="p-4 border-b border-observatory-teal/30">
        <h2 className="text-consciousness-green font-semibold text-lg">
          Affective Telemetry
        </h2>
        <p className="text-xs text-observatory-text/60 mt-1">
          PR-A: Instrumentation Foundation
        </p>
      </div>

      {/* Connection Status */}
      <div className="px-4 py-2 border-b border-observatory-teal/20">
        <div className="flex items-center justify-between">
          <span className="text-xs text-observatory-text/70">WebSocket</span>
          <span className={`text-xs font-medium ${
            connectionState === 'connected'
              ? 'text-green-400'
              : connectionState === 'connecting' || connectionState === 'reconnecting'
              ? 'text-yellow-400'
              : 'text-red-400'
          }`}>
            {connectionState === 'connected' ? '🟢 Connected' :
             connectionState === 'connecting' ? '🟡 Connecting...' :
             connectionState === 'reconnecting' ? '🟡 Reconnecting...' :
             '🔴 Disconnected'}
          </span>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {/* Telemetry Metrics Section */}
        <div className="p-4 border-b border-observatory-teal/20">
          <h3 className="text-sm font-semibold text-observatory-cyan mb-3">
            Telemetry Metrics
          </h3>

          <div className="space-y-2">
            {/* Sample Rate */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-observatory-text/70">Sample Rate</span>
              <span className="text-xs font-mono text-consciousness-green">
                {(metrics.sampleRate * 100).toFixed(0)}%
              </span>
            </div>

            {/* Buffer Utilization */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-observatory-text/70">Buffer</span>
              <span className="text-xs font-mono text-consciousness-green">
                {(metrics.bufferUtilization * 100).toFixed(1)}%
              </span>
            </div>

            {/* Buffer Utilization Bar */}
            <div className="w-full h-1.5 bg-observatory-dark rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  metrics.bufferUtilization > 0.8
                    ? 'bg-red-500'
                    : metrics.bufferUtilization > 0.6
                    ? 'bg-yellow-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${metrics.bufferUtilization * 100}%` }}
              />
            </div>

            {/* Total Events */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-observatory-text/70">Total Events</span>
              <span className="text-xs font-mono text-consciousness-green">
                {totalEvents.toLocaleString()}
              </span>
            </div>

            {/* Sampling Efficiency */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-observatory-text/70">Sampling Efficiency</span>
              <span className="text-xs font-mono text-consciousness-green">
                {samplingEfficiency}%
              </span>
            </div>
          </div>
        </div>

        {/* Event Counts Section */}
        <div className="p-4 border-b border-observatory-teal/20">
          <h3 className="text-sm font-semibold text-observatory-cyan mb-3">
            Event Counts by Type
          </h3>

          <div className="space-y-1.5">
            {AFFECTIVE_EVENT_TYPES.map(eventType => {
              const count = eventCounts[eventType] || 0;
              const percentage = totalEvents > 0 ? (count / totalEvents * 100).toFixed(1) : '0.0';

              return (
                <div key={eventType} className="flex items-center justify-between group hover:bg-observatory-cyan/10 px-2 py-1 rounded transition-colors">
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-observatory-text/80 truncate">
                      {eventType}
                    </div>
                    <div className="text-xs text-observatory-text/40">
                      {percentage}%
                    </div>
                  </div>
                  <div className="text-xs font-mono text-consciousness-green ml-2">
                    {count.toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>

          {totalEvents === 0 && (
            <div className="text-xs text-observatory-text/40 italic text-center py-4">
              No affective events yet. Enable AFFECTIVE_TELEMETRY_ENABLED to start.
            </div>
          )}
        </div>

        {/* Schema Validation Section */}
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-observatory-cyan">
              Schema Validation
            </h3>
            <button
              onClick={validateSchemas}
              className="text-xs px-2 py-1 bg-observatory-cyan/20 hover:bg-observatory-cyan/30 rounded transition-colors text-observatory-cyan"
            >
              Validate
            </button>
          </div>

          <div className={`p-3 rounded border ${
            validation.isValid
              ? 'bg-green-500/10 border-green-500/30'
              : 'bg-red-500/10 border-red-500/30'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">
                {validation.isValid ? '✅' : '❌'}
              </span>
              <span className={`text-sm font-medium ${
                validation.isValid ? 'text-green-400' : 'text-red-400'
              }`}>
                {validation.isValid ? 'All schemas valid' : 'Validation errors'}
              </span>
            </div>

            {!validation.isValid && validation.errors.length > 0 && (
              <div className="mt-2 space-y-1">
                {validation.errors.map((error, i) => (
                  <div key={i} className="text-xs text-red-300 font-mono">
                    {error}
                  </div>
                ))}
              </div>
            )}

            <div className="text-xs text-observatory-text/40 mt-2" suppressHydrationWarning>
              Last checked: {new Date(validation.lastChecked).toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>

      {/* Footer with PR info */}
      <div className="px-4 py-2 border-t border-observatory-teal/20">
        <div className="text-xs text-observatory-text/40 text-center">
          PR-A: Telemetry Foundation (ZERO RISK)
        </div>
      </div>
    </div>
  );
}
