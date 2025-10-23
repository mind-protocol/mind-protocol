/**
 * Affective Coupling Panel
 *
 * PR-B: Emotion Couplings Visualization
 *
 * Displays real-time metrics for affective coupling mechanisms:
 * - Threshold Modulation: Affect-aligned nodes activate easier
 * - Affective Memory: High-affect experiences form stronger weights
 * - Coherence Persistence: Warns about emotional "lock-in" risk
 *
 * Per IMPLEMENTATION_PLAN.md PR-B.7:
 * "Dashboard shows threshold/memory/persistence metrics in real-time"
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 * PR: PR-B (Emotion Couplings - LOW RISK)
 */

'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import type {
  AffectiveThresholdEvent,
  AffectiveMemoryEvent,
  CoherencePersistenceEvent
} from '../hooks/websocket-types';

interface ThresholdModulation {
  node_id: string;
  theta_base: number;
  theta_adjusted: number;
  h: number;  // Threshold reduction
  affective_alignment: number;
  emotion_magnitude: number;
  timestamp: number;
}

interface MemoryAmplification {
  node_id: string;
  m_affect: number;  // Multiplier (1.0 - 1.3)
  emotion_magnitude: number;
  delta_log_w_base: number;
  delta_log_w_amplified: number;
  timestamp: number;
}

interface CoherencePersistence {
  entity_id: string;
  coherence_persistence: number;  // Consecutive frames
  lambda_res_effective: number;  // Resonance strength after decay
  lock_in_risk: boolean;
  timestamp: number;
}

const MAX_RECENT_EVENTS = 10;  // Keep last N events per mechanism

/**
 * Affective Coupling Panel Component
 *
 * Shows three affective coupling mechanisms in real-time.
 */
export function AffectiveCouplingPanel() {
  const { connectionState } = useWebSocket();

  // Recent threshold modulation events
  const [recentThresholds, setRecentThresholds] = useState<ThresholdModulation[]>([]);

  // Recent memory amplification events
  const [recentMemory, setRecentMemory] = useState<MemoryAmplification[]>([]);

  // Current coherence persistence by entity
  const [coherenceStates, setCoherenceStates] = useState<Map<string, CoherencePersistence>>(new Map());

  // Subscribe to WebSocket events (will implement handlers when useWebSocket exposes them)
  // For now, we'll poll the telemetry API which aggregates these events

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch('/api/consciousness/affective-coupling/recent-events');
        if (res.ok) {
          const data = await res.json();

          if (data.thresholds) {
            setRecentThresholds(data.thresholds.slice(-MAX_RECENT_EVENTS));
          }

          if (data.memory) {
            setRecentMemory(data.memory.slice(-MAX_RECENT_EVENTS));
          }

          if (data.coherence) {
            const coherenceMap = new Map<string, CoherencePersistence>();
            data.coherence.forEach((event: CoherencePersistence) => {
              coherenceMap.set(event.entity_id, event);
            });
            setCoherenceStates(coherenceMap);
          }
        }
      } catch (error) {
        console.log('[AffectiveCouplingPanel] Events not available yet:', error);
      }
    };

    // Initial fetch
    fetchEvents();

    // Poll every 1 second for real-time feel
    const interval = setInterval(fetchEvents, 1000);

    return () => clearInterval(interval);
  }, []);

  // Calculate aggregate stats
  const avgThresholdReduction = recentThresholds.length > 0
    ? recentThresholds.reduce((sum, t) => sum + Math.abs(t.h), 0) / recentThresholds.length
    : 0;

  const avgMemoryMultiplier = recentMemory.length > 0
    ? recentMemory.reduce((sum, m) => sum + m.m_affect, 0) / recentMemory.length
    : 1.0;

  const entitiesAtRisk = Array.from(coherenceStates.values()).filter(c => c.lock_in_risk).length;

  return (
    <div className="fixed left-4 top-[60vh] z-40 w-80 max-h-[calc(40vh-2rem)] overflow-y-auto custom-scrollbar space-y-3">
      {/* Header */}
      <div className="consciousness-panel p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-consciousness-green font-semibold text-lg">
            Affective Coupling
          </h2>
          <div className={`text-xs font-medium ${
            connectionState === 'connected' ? 'text-green-400' : 'text-red-400'
          }`}>
            {connectionState === 'connected' ? '🟢' : '🔴'}
          </div>
        </div>
        <p className="text-xs text-observatory-text/60">
          PR-B: Threshold · Memory · Persistence
        </p>
      </div>

      {/* Threshold Modulation Display */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>🎯</span>
          <span>Threshold Modulation</span>
        </h3>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-observatory-dark/50 p-3 rounded">
            <div className="text-xs text-observatory-text/60 mb-1">Avg Reduction</div>
            <div className="text-lg font-mono text-consciousness-green">
              {(avgThresholdReduction * 100).toFixed(1)}%
            </div>
          </div>
          <div className="bg-observatory-dark/50 p-3 rounded">
            <div className="text-xs text-observatory-text/60 mb-1">Recent Events</div>
            <div className="text-lg font-mono text-consciousness-green">
              {recentThresholds.length}
            </div>
          </div>
        </div>

        {/* Recent Events */}
        <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
          {recentThresholds.length === 0 ? (
            <div className="text-xs text-observatory-text/40 italic text-center py-2">
              No threshold modulation events yet
            </div>
          ) : (
            recentThresholds.slice().reverse().map((event, i) => (
              <div key={i} className="bg-observatory-dark/30 p-2 rounded text-xs">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-observatory-text/70 truncate flex-1 mr-2">
                    {event.node_id}
                  </span>
                  <span className={`font-mono ${
                    event.h < 0 ? 'text-green-400' : 'text-observatory-text/60'
                  }`}>
                    {event.h > 0 ? '+' : ''}{(event.h * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-observatory-text/50">
                  <span>θ: {event.theta_base.toFixed(3)} → {event.theta_adjusted.toFixed(3)}</span>
                  <span>align: {event.affective_alignment.toFixed(2)}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Affective Memory Display */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>🧠</span>
          <span>Affective Memory</span>
        </h3>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-observatory-dark/50 p-3 rounded">
            <div className="text-xs text-observatory-text/60 mb-1">Avg Multiplier</div>
            <div className="text-lg font-mono text-consciousness-green">
              {avgMemoryMultiplier.toFixed(2)}x
            </div>
          </div>
          <div className="bg-observatory-dark/50 p-3 rounded">
            <div className="text-xs text-observatory-text/60 mb-1">Recent Events</div>
            <div className="text-lg font-mono text-consciousness-green">
              {recentMemory.length}
            </div>
          </div>
        </div>

        {/* Recent Events */}
        <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
          {recentMemory.length === 0 ? (
            <div className="text-xs text-observatory-text/40 italic text-center py-2">
              No memory amplification events yet
            </div>
          ) : (
            recentMemory.slice().reverse().map((event, i) => (
              <div key={i} className="bg-observatory-dark/30 p-2 rounded text-xs">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-observatory-text/70 truncate flex-1 mr-2">
                    {event.node_id}
                  </span>
                  <span className={`font-mono ${
                    event.m_affect > 1.0 ? 'text-green-400' : 'text-observatory-text/60'
                  }`}>
                    {event.m_affect.toFixed(2)}x
                  </span>
                </div>
                <div className="flex items-center justify-between text-observatory-text/50">
                  <span>Δw: {event.delta_log_w_base.toFixed(3)} → {event.delta_log_w_amplified.toFixed(3)}</span>
                  <span>mag: {event.emotion_magnitude.toFixed(2)}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Coherence Persistence Watch */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>⏱️</span>
          <span>Coherence Persistence</span>
        </h3>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className={`p-3 rounded ${
            entitiesAtRisk > 0 ? 'bg-red-500/20 border border-red-500/40' : 'bg-observatory-dark/50'
          }`}>
            <div className="text-xs text-observatory-text/60 mb-1">Lock-in Risk</div>
            <div className={`text-lg font-mono ${
              entitiesAtRisk > 0 ? 'text-red-400' : 'text-green-400'
            }`}>
              {entitiesAtRisk > 0 ? `⚠️ ${entitiesAtRisk}` : '✅ None'}
            </div>
          </div>
          <div className="bg-observatory-dark/50 p-3 rounded">
            <div className="text-xs text-observatory-text/60 mb-1">Tracking</div>
            <div className="text-lg font-mono text-consciousness-green">
              {coherenceStates.size}
            </div>
          </div>
        </div>

        {/* Entity States */}
        <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
          {coherenceStates.size === 0 ? (
            <div className="text-xs text-observatory-text/40 italic text-center py-2">
              No coherence persistence tracking yet
            </div>
          ) : (
            Array.from(coherenceStates.values()).map((event, i) => (
              <div key={i} className={`p-2 rounded text-xs ${
                event.lock_in_risk
                  ? 'bg-red-500/20 border border-red-500/40'
                  : 'bg-observatory-dark/30'
              }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-observatory-text/70 truncate flex-1 mr-2">
                    {event.entity_id}
                  </span>
                  <span className={`font-mono ${
                    event.lock_in_risk ? 'text-red-400' : 'text-observatory-text/60'
                  }`}>
                    {event.coherence_persistence} frames
                  </span>
                </div>
                <div className="flex items-center justify-between text-observatory-text/50">
                  <span>λ_res: {event.lambda_res_effective.toFixed(3)}</span>
                  {event.lock_in_risk && (
                    <span className="text-red-400 font-medium">⚠️ LOCK-IN</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Explanation */}
        {entitiesAtRisk > 0 && (
          <div className="mt-3 p-2 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-300">
            <div className="font-medium mb-1">⚠️ Lock-in Warning</div>
            <div className="text-observatory-text/70">
              Entity stuck in same emotional state for {'>'}20 frames. Resonance weakening to prevent stagnation.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
