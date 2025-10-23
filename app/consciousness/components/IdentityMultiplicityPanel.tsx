/**
 * Identity Multiplicity Panel
 *
 * PR-D: Identity Multiplicity Detection Visualization
 *
 * Displays real-time metrics for identity multiplicity detection:
 * - Multiplicity Status: Is entity in multiplicity mode?
 * - Task Progress Rate: Progress on goals per frame
 * - Energy Efficiency: Work output / total energy spent
 * - Identity Flip Count: Frequency of identity switches
 *
 * Per IMPLEMENTATION_PLAN.md PR-D.5:
 * "Dashboard shows multiplicity detection status per entity with outcome metrics"
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 * PR: PR-D (Identity Multiplicity - MEDIUM-HIGH RISK)
 */

'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface MultiplicityStatus {
  entity_id: string;
  is_multiplicity_active: boolean;
  task_progress_rate: number;  // Progress per frame (rolling window)
  energy_efficiency: number;  // Work/energy ratio (rolling window)
  identity_flip_count: number;  // Flips in rolling window
  coherence_score: number;  // Entity coherence (0-1)
  window_frames: number;  // Size of rolling window
  timestamp: number;
}

interface IdentityFlip {
  entity_id: string;
  from_identity: string;
  to_identity: string;
  trigger_reason: string;  // "task_stuck" | "energy_inefficient" | "exploration"
  timestamp: number;
}

const MAX_RECENT_FLIPS = 15;  // Keep last N flip events

/**
 * Identity Multiplicity Panel Component
 *
 * Shows identity multiplicity detection and outcome metrics.
 */
export function IdentityMultiplicityPanel() {
  const { connectionState } = useWebSocket();

  // Current multiplicity status by entity
  const [multiplicityStatuses, setMultiplicityStatuses] = useState<Map<string, MultiplicityStatus>>(new Map());

  // Recent identity flip events
  const [recentFlips, setRecentFlips] = useState<IdentityFlip[]>([]);

  // Subscribe to WebSocket events (poll API for now)
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch('/api/consciousness/identity-multiplicity/status');
        if (res.ok) {
          const data = await res.json();

          if (data.statuses) {
            const statusMap = new Map<string, MultiplicityStatus>();
            data.statuses.forEach((status: MultiplicityStatus) => {
              statusMap.set(status.entity_id, status);
            });
            setMultiplicityStatuses(statusMap);
          }

          if (data.recent_flips) {
            setRecentFlips(data.recent_flips.slice(-MAX_RECENT_FLIPS));
          }
        }
      } catch (error) {
        console.log('[IdentityMultiplicityPanel] Events not available yet:', error);
      }
    };

    // Initial fetch
    fetchEvents();

    // Poll every 2 seconds
    const interval = setInterval(fetchEvents, 2000);

    return () => clearInterval(interval);
  }, []);

  // Calculate aggregate stats
  const entitiesInMultiplicity = Array.from(multiplicityStatuses.values()).filter(s => s.is_multiplicity_active).length;
  const totalFlips = recentFlips.length;
  const avgEfficiency = multiplicityStatuses.size > 0
    ? Array.from(multiplicityStatuses.values()).reduce((sum, s) => sum + s.energy_efficiency, 0) / multiplicityStatuses.size
    : 0;

  return (
    <div className="fixed right-4 top-[60vh] z-40 w-80 max-h-[calc(40vh-2rem)] overflow-y-auto custom-scrollbar space-y-3">
      {/* Header */}
      <div className="consciousness-panel p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-consciousness-green font-semibold text-lg">
            Identity Multiplicity
          </h2>
          <div className={`text-xs font-medium ${
            connectionState === 'connected' ? 'text-green-400' : 'text-red-400'
          }`}>
            {connectionState === 'connected' ? '🟢' : '🔴'}
          </div>
        </div>
        <p className="text-xs text-observatory-text/60">
          PR-D: Outcome-Based Detection
        </p>
      </div>

      {/* Multiplicity Overview */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>👥</span>
          <span>System Overview</span>
        </h3>

        <div className="grid grid-cols-2 gap-3">
          <div className={`p-3 rounded ${
            entitiesInMultiplicity > 0 ? 'bg-purple-500/20 border border-purple-500/40' : 'bg-observatory-dark/50'
          }`}>
            <div className="text-xs text-observatory-text/60 mb-1">Active Multiplicity</div>
            <div className={`text-lg font-mono ${
              entitiesInMultiplicity > 0 ? 'text-purple-400' : 'text-observatory-text/60'
            }`}>
              {entitiesInMultiplicity > 0 ? `🔀 ${entitiesInMultiplicity}` : '➡️ None'}
            </div>
          </div>

          <div className="bg-observatory-dark/50 p-3 rounded">
            <div className="text-xs text-observatory-text/60 mb-1">Recent Flips</div>
            <div className="text-lg font-mono text-consciousness-green">
              {totalFlips}
            </div>
          </div>

          <div className="bg-observatory-dark/50 p-3 rounded col-span-2">
            <div className="text-xs text-observatory-text/60 mb-1">Avg Efficiency</div>
            <div className="text-lg font-mono text-consciousness-green">
              {(avgEfficiency * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Entity Multiplicity Status */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>📊</span>
          <span>Entity Status</span>
        </h3>

        <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar">
          {multiplicityStatuses.size === 0 ? (
            <div className="text-xs text-observatory-text/40 italic text-center py-2">
              No multiplicity tracking yet
            </div>
          ) : (
            Array.from(multiplicityStatuses.values()).map((status, i) => (
              <div key={i} className={`p-3 rounded text-xs ${
                status.is_multiplicity_active
                  ? 'bg-purple-500/20 border border-purple-500/40'
                  : 'bg-observatory-dark/30'
              }`}>
                {/* Entity Header */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-observatory-text/70 font-medium truncate flex-1 mr-2">
                    {status.entity_id}
                  </span>
                  <span className={`text-xs font-bold ${
                    status.is_multiplicity_active ? 'text-purple-400' : 'text-observatory-text/60'
                  }`}>
                    {status.is_multiplicity_active ? '🔀 MULTI' : '➡️ SINGLE'}
                  </span>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-2 text-observatory-text/60">
                  <div>
                    <div className="text-[10px] mb-1">Task Progress</div>
                    <div className="font-mono text-observatory-text">
                      {(status.task_progress_rate * 100).toFixed(1)}%/f
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] mb-1">Efficiency</div>
                    <div className="font-mono text-observatory-text">
                      {(status.energy_efficiency * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] mb-1">Flips</div>
                    <div className="font-mono text-observatory-text">
                      {status.identity_flip_count}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] mb-1">Coherence</div>
                    <div className="font-mono text-observatory-text">
                      {(status.coherence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                {status.is_multiplicity_active && (
                  <div className="mt-2">
                    <div className="text-[10px] text-purple-400 mb-1">
                      Window: {status.window_frames} frames
                    </div>
                    <div className="w-full h-1 bg-observatory-dark rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-500"
                        style={{ width: `${Math.min(status.identity_flip_count * 20, 100)}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Identity Flips */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>🔄</span>
          <span>Recent Flips</span>
        </h3>

        <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
          {recentFlips.length === 0 ? (
            <div className="text-xs text-observatory-text/40 italic text-center py-2">
              No identity flips yet
            </div>
          ) : (
            recentFlips.slice().reverse().map((flip, i) => (
              <div key={i} className="bg-observatory-dark/30 p-2 rounded text-xs">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-observatory-text/70 truncate flex-1 mr-2">
                    {flip.entity_id}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    flip.trigger_reason === 'task_stuck' ? 'bg-red-500/20 text-red-400' :
                    flip.trigger_reason === 'energy_inefficient' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {flip.trigger_reason}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-observatory-text/50">
                  <span className="truncate max-w-[100px]">{flip.from_identity}</span>
                  <span>→</span>
                  <span className="truncate max-w-[100px]">{flip.to_identity}</span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Legend */}
        {recentFlips.length > 0 && (
          <div className="mt-3 pt-2 border-t border-observatory-dark">
            <div className="text-[10px] text-observatory-text/50 space-y-1">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-red-500/20 rounded"></span>
                <span>Task Stuck</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-yellow-500/20 rounded"></span>
                <span>Energy Inefficient</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-blue-500/20 rounded"></span>
                <span>Exploration</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Detection Criteria Info */}
      {entitiesInMultiplicity > 0 && (
        <div className="consciousness-panel p-3">
          <div className="text-xs text-observatory-cyan font-medium mb-2">
            💡 Multiplicity Detection
          </div>
          <div className="text-[10px] text-observatory-text/70 space-y-1">
            <div>• Task progress declining</div>
            <div>• Energy efficiency below threshold</div>
            <div>• Frequent identity flips (&gt;3 in window)</div>
            <div>• System exploring multiple strategies</div>
          </div>
        </div>
      )}
    </div>
  );
}
