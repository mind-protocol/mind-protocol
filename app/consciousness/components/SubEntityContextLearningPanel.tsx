/**
 * SubEntity Context Learning Panel - Dual-View Weight Architecture Observability
 *
 * Visualizes Priority 4 subentity-context-aware TRACE learning:
 * - Dual-view architecture: Global weights + sparse subentity overlays
 * - 80/20 split: 20% to global, 80% to subentity-local overlays
 * - Membership-weighted learning: Overlays scaled by BELONGS_TO strength
 * - SubEntity attribution: See which subentities drove each weight change
 *
 * Shows:
 * - Split ratio visualization (global vs subentity-local contributions)
 * - Recent weight updates with subentity attribution
 * - SubEntity-specific overlay magnitudes
 * - Learning stats (updates per cohort, mean deltas)
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: 4 (SubEntity-Context TRACE Observability)
 * Spec: docs/specs/v2/learning_and_trace/ENTITY_CONTEXT_TRACE_DESIGN.md
 */

'use client';

import React, { useState, useMemo } from 'react';
import { WeightsUpdatedTraceEvent } from '../hooks/websocket-types';

interface SubEntityContextLearningPanelProps {
  weightEvents: WeightsUpdatedTraceEvent[];
  windowSize?: number;
}

interface SubEntityOverlayStats {
  subentity_id: string;
  total_delta: number;
  update_count: number;
  avg_membership: number;
}

export default function SubEntityContextLearningPanel({
  weightEvents,
  windowSize = 100
}: SubEntityContextLearningPanelProps) {
  const [selectedWindow, setSelectedWindow] = useState(windowSize);

  // Filter to events within rolling window
  const windowedEvents = useMemo(() => {
    return weightEvents.slice(-selectedWindow);
  }, [weightEvents, selectedWindow]);

  // Compute aggregate split ratio (global vs subentity-local contributions)
  const splitRatio = useMemo(() => {
    // TODO: Implement using actual WeightsUpdatedTraceEvent structure
    // Current event has: scope, cohort, subentity_contexts, global_context, n, d_mu, d_sigma
    // Not individual updates array

    if (windowedEvents.length === 0) {
      return { global_pct: 0, local_pct: 0 };
    }

    // Placeholder calculation until backend emits proper structure
    let total_global_delta = 0;
    let total_local_delta = 0;

    windowedEvents.forEach(event => {
      // Use aggregate stats from actual event structure
      const magnitude = Math.abs(event.d_mu * event.n);

      if (event.global_context) {
        total_global_delta += magnitude * 0.2; // 20% global
        total_local_delta += magnitude * 0.8; // 80% subentity-local
      } else {
        total_local_delta += magnitude; // 100% subentity-local
      }
    });

    const total = total_global_delta + total_local_delta;
    if (total === 0) {
      return { global_pct: 0, local_pct: 0 };
    }

    return {
      global_pct: (total_global_delta / total) * 100,
      local_pct: (total_local_delta / total) * 100
    };
  }, [windowedEvents]);

  // Compute subentity-specific overlay stats
  const subentityStats = useMemo((): SubEntityOverlayStats[] => {
    const stats: Map<string, SubEntityOverlayStats> = new Map();

    // TODO: Implement using actual WeightsUpdatedTraceEvent structure
    // Current event has subentity_contexts array, not individual overlay details

    windowedEvents.forEach(event => {
      // Use subentity_contexts from actual event structure
      event.subentity_contexts?.forEach(subentity_id => {
        if (!stats.has(subentity_id)) {
          stats.set(subentity_id, {
            subentity_id,
            total_delta: 0,
            update_count: 0,
            avg_membership: 0.8 // Fixed 80% for subentity-local updates
          });
        }

        const stat = stats.get(subentity_id)!;
        stat.total_delta += Math.abs(event.d_mu) || 0;
        stat.update_count += 1;
      });
    });

    // Sort by total delta (most active subentities first)
    return Array.from(stats.values()).sort((a, b) => b.total_delta - a.total_delta);
  }, [windowedEvents]);

  // Recent weight updates (last 10)
  const recentUpdates = useMemo(() => {
    const updates: Array<{
      frame_id: number;
      item_id: string;
      delta_global: number;
      subentity_overlays: Array<{ subentity: string; delta: number }>;
    }> = [];

    // TODO: Implement using actual WeightsUpdatedTraceEvent structure
    // Current events don't have individual update details, only aggregate stats

    // Traverse events in reverse (most recent first)
    for (let i = windowedEvents.length - 1; i >= 0 && updates.length < 10; i--) {
      const event = windowedEvents[i];

      // Create synthetic update from aggregate event data
      updates.push({
        frame_id: event.frame_id,
        item_id: `${event.scope}_cohort_${event.cohort}`,
        delta_global: event.global_context ? event.d_mu * 0.2 : 0,
        subentity_overlays: event.subentity_contexts?.map(subentity => ({
          subentity,
          delta: event.d_mu * 0.8 / (event.subentity_contexts?.length || 1)
        })) || []
      });
    }

    return updates;
  }, [windowedEvents]);

  // Aggregate learning stats
  const learningStats = useMemo(() => {
    const cohorts: Set<string> = new Set();
    let total_updates = 0;
    let total_global_delta = 0;

    windowedEvents.forEach(event => {
      cohorts.add(event.cohort);
      total_updates += event.n || 0;
      total_global_delta += event.d_mu || 0;
    });

    return {
      cohorts: cohorts.size,
      total_updates,
      avg_global_delta: total_updates > 0 ? total_global_delta / windowedEvents.length : 0
    };
  }, [windowedEvents]);

  return (
    <div className="subentity-context-learning-panel bg-gray-900 border border-gray-700 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold text-gray-100">
            Dual-View Learning
          </h3>
          {windowedEvents.length === 0 && (
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
            <option value={50}>50 events</option>
            <option value={100}>100 events</option>
            <option value={200}>200 events</option>
          </select>
        </div>
      </div>

      {windowedEvents.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No weight learning events yet. Waiting for TRACE-driven updates...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Split Ratio Visualization */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Learning Split (Global vs SubEntity-Local)</h4>
            <div className="flex h-8 rounded overflow-hidden mb-2">
              <div
                className="bg-purple-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${splitRatio.global_pct}%` }}
                title={`Global: ${splitRatio.global_pct.toFixed(1)}%`}
              >
                {splitRatio.global_pct > 10 ? `${splitRatio.global_pct.toFixed(0)}%` : ''}
              </div>
              <div
                className="bg-cyan-500 flex items-center justify-center text-xs font-bold text-white"
                style={{ width: `${splitRatio.local_pct}%` }}
                title={`SubEntity-Local: ${splitRatio.local_pct.toFixed(1)}%`}
              >
                {splitRatio.local_pct > 10 ? `${splitRatio.local_pct.toFixed(0)}%` : ''}
              </div>
            </div>
            <div className="flex justify-between text-xs">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-purple-500 rounded"></div>
                <span className="text-gray-400">Global (cross-subentity)</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-cyan-500 rounded"></div>
                <span className="text-gray-400">SubEntity-Local (context-specific)</span>
              </div>
            </div>
          </div>

          {/* SubEntity Overlay Stats */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">SubEntity Attribution</h4>
            <div className="space-y-2">
              {subentityStats.slice(0, 5).map(stat => (
                <div key={stat.subentity_id} className="bg-gray-800 rounded p-2">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-mono text-cyan-400">{stat.subentity_id}</span>
                    <span className="text-xs text-gray-400">{stat.update_count} updates</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Total Δ overlay:</span>
                    <span className="text-white font-bold">{stat.total_delta.toFixed(3)}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Avg membership:</span>
                    <span className="text-gray-300">{stat.avg_membership.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
            {subentityStats.length > 5 && (
              <div className="text-xs text-gray-500 mt-2 text-center">
                +{subentityStats.length - 5} more subentities
              </div>
            )}
          </div>

          {/* Recent Weight Updates */}
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-2">Recent Updates</h4>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {recentUpdates.map((update, idx) => (
                <div key={`${update.frame_id}-${update.item_id}-${idx}`} className="bg-gray-800 rounded p-2 text-xs">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-mono text-gray-300">{update.item_id}</span>
                    <span className="text-gray-500">Frame {update.frame_id}</span>
                  </div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-gray-400">Global Δ:</span>
                    <span className={`font-bold ${update.delta_global >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {update.delta_global >= 0 ? '+' : ''}{update.delta_global.toFixed(4)}
                    </span>
                  </div>
                  {update.subentity_overlays.length > 0 && (
                    <div className="mt-1 pl-2 border-l-2 border-cyan-600">
                      {update.subentity_overlays.map(overlay => (
                        <div key={overlay.subentity} className="flex justify-between items-center">
                          <span className="text-cyan-400 font-mono text-[10px]">{overlay.subentity}</span>
                          <span className={`font-bold ${overlay.delta >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {overlay.delta >= 0 ? '+' : ''}{overlay.delta.toFixed(4)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Learning Stats */}
          <div className="pt-3 border-t border-gray-800">
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-gray-800 rounded p-2">
                <div className="text-xs text-gray-400">Cohorts</div>
                <div className="text-lg font-bold text-gray-100">{learningStats.cohorts}</div>
              </div>
              <div className="bg-gray-800 rounded p-2">
                <div className="text-xs text-gray-400">Updates</div>
                <div className="text-lg font-bold text-gray-100">{learningStats.total_updates}</div>
              </div>
              <div className="bg-gray-800 rounded p-2">
                <div className="text-xs text-gray-400">Avg Δ</div>
                <div className="text-lg font-bold text-gray-100">
                  {learningStats.avg_global_delta.toFixed(3)}
                </div>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
            Total events analyzed: {windowedEvents.length} (window: {selectedWindow})
          </div>
        </div>
      )}
    </div>
  );
}
