'use client';

import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { getMockHealthData } from '../../data/mockHealthData';
import type {
  GraphHealthSnapshotEvent,
  GraphHealthAlertEvent,
  GraphHealthProcedureEvent,
  HealthHistoryResponse,
} from '../../types/health-types';

export interface HealthDashboardProps {
  graph_id: string;
  refresh_interval_ms?: number;  // Default 60000 (60s)
}

/**
 * Health Dashboard - Main orchestrator for graph health monitoring
 *
 * Subscribes to WebSocket events:
 * - graph.health.snapshot (periodic, every 60s)
 * - graph.health.alert (status changes)
 * - graph.health.procedure.* (procedure lifecycle)
 * - graph.health.history.response (historical trends)
 *
 * Renders neurosurgeon-style one-screen overview with:
 * - Overall status indicator
 * - Critical issues panel
 * - 10 core metrics grid
 * - Historical trend charts
 * - Procedure execution controls
 */
export function HealthDashboard({ graph_id, refresh_interval_ms = 60000 }: HealthDashboardProps) {
  const websocket = useWebSocket();

  // State for latest health snapshot
  const [healthSnapshot, setHealthSnapshot] = useState<GraphHealthSnapshotEvent | null>(null);

  // State for alerts (keep last 10)
  const [alerts, setAlerts] = useState<GraphHealthAlertEvent[]>([]);

  // State for active procedures
  const [procedures, setProcedures] = useState<Map<string, GraphHealthProcedureEvent>>(new Map());

  // State for historical data
  const [history, setHistory] = useState<HealthHistoryResponse | null>(null);

  // Subscribe to health snapshot events
  useEffect(() => {
    // TEMPORARY: Load mock data for UI testing
    // This will be replaced by actual WebSocket event subscription when backend is ready
    const mockData = getMockHealthData(graph_id);
    setHealthSnapshot(mockData);

    // TODO: Once useWebSocket is extended with health events, replace mock data with:
    // websocket.on('graph.health.snapshot', (event: GraphHealthSnapshotEvent) => {
    //   if (event.graph_id === graph_id) {
    //     setHealthSnapshot(event);
    //   }
    // });

    // Simulate periodic updates with mock data
    const intervalId = setInterval(() => {
      const updatedMockData = getMockHealthData(graph_id);
      updatedMockData.timestamp = Date.now();
      setHealthSnapshot(updatedMockData);
    }, refresh_interval_ms);

    return () => clearInterval(intervalId);
  }, [graph_id, refresh_interval_ms]);

  // Subscribe to alert events
  useEffect(() => {
    // TODO: Subscribe to graph.health.alert
    // websocket.on('graph.health.alert', (event: GraphHealthAlertEvent) => {
    //   if (event.graph_id === graph_id) {
    //     setAlerts(prev => [event, ...prev].slice(0, 10)); // Keep last 10
    //
    //     if (event.severity === 'RED') {
    //       // Show critical notification
    //       showCriticalNotification(event);
    //     }
    //   }
    // });
  }, [graph_id]);

  // Subscribe to procedure lifecycle events
  useEffect(() => {
    // TODO: Subscribe to graph.health.procedure.* events
    // websocket.on('graph.health.procedure.started', (event: GraphHealthProcedureEvent) => {
    //   setProcedures(prev => new Map(prev).set(event.procedure_id, event));
    // });
    //
    // websocket.on('graph.health.procedure.progress', (event: GraphHealthProcedureEvent) => {
    //   setProcedures(prev => new Map(prev).set(event.procedure_id, event));
    // });
    //
    // websocket.on('graph.health.procedure.completed', (event: GraphHealthProcedureEvent) => {
    //   setProcedures(prev => new Map(prev).set(event.procedure_id, event));
    //   // Refresh health snapshot after completion
    // });
    //
    // websocket.on('graph.health.procedure.failed', (event: GraphHealthProcedureEvent) => {
    //   setProcedures(prev => new Map(prev).set(event.procedure_id, event));
    // });
  }, [graph_id]);

  // Request historical data on mount
  useEffect(() => {
    // TODO: Send WebSocket request for historical data
    // websocket.send({
    //   type: 'graph.health.history.request',
    //   graph_id: graph_id,
    //   window_days: 30
    // });
    //
    // websocket.on('graph.health.history.response', (event: HealthHistoryResponse) => {
    //   if (event.graph_id === graph_id) {
    //     setHistory(event);
    //   }
    // });
  }, [graph_id]);

  // Loading state while waiting for first snapshot
  if (!healthSnapshot) {
    return (
      <div className="text-center py-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-observatory-cyan mx-auto mb-2"></div>
        <p className="text-xs text-observatory-silver/60">Loading health data...</p>
      </div>
    );
  }

  return (
    <div className="health-dashboard space-y-3">
      {/* Overall Status Header */}
      <div className="flex items-center justify-between px-2 py-1">
        <span className="text-xs text-observatory-silver/70">Status</span>
        <div className={`px-2 py-1 rounded text-xs font-semibold ${
          healthSnapshot.overall_status === 'GREEN' ? 'bg-green-500/20 text-green-400' :
          healthSnapshot.overall_status === 'AMBER' ? 'bg-yellow-500/20 text-yellow-400' :
          'bg-red-500/20 text-red-400'
        }`}>
          {healthSnapshot.overall_status === 'GREEN' && '🟢'}
          {healthSnapshot.overall_status === 'AMBER' && '🟡'}
          {healthSnapshot.overall_status === 'RED' && '🔴'}
          {' '}{healthSnapshot.overall_status}
        </div>
      </div>

      {/* Critical Issues Panel (when issues exist) */}
      {healthSnapshot.flagged_metrics.length > 0 && (
        <div className="bg-red-950/30 border border-red-700/50 rounded p-2">
          <div className="text-xs font-semibold text-red-400 mb-1">
            ⚠️ {healthSnapshot.flagged_metrics.length} Issue{healthSnapshot.flagged_metrics.length > 1 ? 's' : ''}
          </div>
          <div className="space-y-1">
            {healthSnapshot.flagged_metrics.map((metric) => (
              <div key={metric} className="text-xs text-observatory-silver">
                • {metric}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Compact Metrics List */}
      <div className="space-y-2">
        <CompactMetric
          label="Density"
          value={healthSnapshot.density.density.toFixed(3)}
          status={healthSnapshot.density.status}
          trend={healthSnapshot.density.trend}
        />
        <CompactMetric
          label="Overlap"
          value={healthSnapshot.overlap.overlap_ratio.toFixed(2)}
          status={healthSnapshot.overlap.status}
          trend={healthSnapshot.overlap.trend}
        />
        <CompactMetric
          label="Orphans"
          value={`${(healthSnapshot.orphans.orphan_ratio * 100).toFixed(1)}%`}
          status={healthSnapshot.orphans.status}
          trend={healthSnapshot.orphans.trend}
        />
        <CompactMetric
          label="Coherence"
          value={healthSnapshot.coherence.overall_median_coherence.toFixed(2)}
          status="GREEN"
          trend="stable"
        />
        <CompactMetric
          label="Highways"
          value={healthSnapshot.highways.total_highways.toString()}
          status={healthSnapshot.highways.status}
          trend="stable"
        />
        <CompactMetric
          label="WM SubEntities"
          value={healthSnapshot.wm_health.mean_selected.toFixed(1)}
          status={healthSnapshot.wm_health.status}
          trend="stable"
        />
      </div>

      <div className="text-xs text-observatory-silver/50 text-center pt-2 border-t border-observatory-silver/10">
        Updated: {new Date(healthSnapshot.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
}

/**
 * CompactMetric - Single-line metric display for sidebar
 */
interface CompactMetricProps {
  label: string;
  value: string;
  status: 'GREEN' | 'AMBER' | 'RED';
  trend: 'rising' | 'stable' | 'falling';
}

function CompactMetric({ label, value, status, trend }: CompactMetricProps) {
  const statusIcon =
    status === 'GREEN' ? '🟢' :
    status === 'AMBER' ? '🟡' :
    '🔴';

  const trendIcon =
    trend === 'rising' ? '↗' :
    trend === 'falling' ? '↘' :
    '→';

  return (
    <div className="flex items-center justify-between px-2 py-1.5 bg-observatory-bg/30 rounded text-xs">
      <span className="text-observatory-silver/70">{label}</span>
      <div className="flex items-center gap-1.5">
        <span className="font-semibold text-observatory-silver">{value}</span>
        <span className="text-observatory-silver/50">{trendIcon}</span>
        <span>{statusIcon}</span>
      </div>
    </div>
  );
}

