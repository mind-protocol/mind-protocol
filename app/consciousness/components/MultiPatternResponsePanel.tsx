/**
 * Multi-Pattern Response Panel
 *
 * PR-C: Affective Response Patterns Visualization
 *
 * Displays real-time metrics for three affective response patterns:
 * - Regulation: Intentional affect modulation (goal-driven)
 * - Rumination: Repetitive negative thought loops (with cap detection)
 * - Distraction: Attention shifting away from affect
 *
 * Per IMPLEMENTATION_PLAN.md PR-C.6:
 * "Dashboard shows regulation/rumination/distraction effectiveness over time"
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 * PR: PR-C (Multi-Pattern Response - MEDIUM RISK)
 */

'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface PatternEffectiveness {
  pattern_type: 'regulation' | 'rumination' | 'distraction';
  entity_id: string;
  effectiveness: number;  // 0-1 score
  weight: number;  // Learned weight for this pattern
  consecutive_frames: number;  // How long this pattern has been active
  timestamp: number;
}

interface RuminationCap {
  entity_id: string;
  consecutive_frames: number;
  cap_triggered: boolean;  // True when >= 10 frames
  rumination_weight_penalty: number;  // Weight reduction applied
  timestamp: number;
}

const MAX_RECENT_PATTERNS = 20;  // Keep last N pattern events

/**
 * Multi-Pattern Response Panel Component
 *
 * Shows three affective response patterns in real-time.
 */
export function MultiPatternResponsePanel() {
  const { connectionState } = useWebSocket();

  // Recent pattern effectiveness events
  const [recentPatterns, setRecentPatterns] = useState<PatternEffectiveness[]>([]);

  // Rumination cap warnings
  const [ruminationCaps, setRuminationCaps] = useState<Map<string, RuminationCap>>(new Map());

  // Current pattern weights by entity
  const [patternWeights, setPatternWeights] = useState<Map<string, {
    regulation: number;
    rumination: number;
    distraction: number;
  }>>(new Map());

  // Subscribe to WebSocket events (poll API for now)
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch('/api/consciousness/multi-pattern/recent-events');
        if (res.ok) {
          const data = await res.json();

          if (data.patterns) {
            setRecentPatterns(data.patterns.slice(-MAX_RECENT_PATTERNS));

            // Build pattern weights map
            const weightsMap = new Map();
            data.patterns.forEach((p: PatternEffectiveness) => {
              if (!weightsMap.has(p.entity_id)) {
                weightsMap.set(p.entity_id, {
                  regulation: 0.5,
                  rumination: 0.3,
                  distraction: 0.2
                });
              }
              weightsMap.get(p.entity_id)[p.pattern_type] = p.weight;
            });
            setPatternWeights(weightsMap);
          }

          if (data.rumination_caps) {
            const capsMap = new Map<string, RuminationCap>();
            data.rumination_caps.forEach((cap: RuminationCap) => {
              capsMap.set(cap.entity_id, cap);
            });
            setRuminationCaps(capsMap);
          }
        }
      } catch (error) {
        console.log('[MultiPatternResponsePanel] Events not available yet:', error);
      }
    };

    // Initial fetch
    fetchEvents();

    // Poll every 2 seconds
    const interval = setInterval(fetchEvents, 2000);

    return () => clearInterval(interval);
  }, []);

  // Calculate aggregate stats
  const patternCounts = recentPatterns.reduce((acc, p) => {
    acc[p.pattern_type] = (acc[p.pattern_type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const avgEffectiveness = (patternType: string) => {
    const patterns = recentPatterns.filter(p => p.pattern_type === patternType);
    if (patterns.length === 0) return 0;
    return patterns.reduce((sum, p) => sum + p.effectiveness, 0) / patterns.length;
  };

  const entitiesAtRisk = Array.from(ruminationCaps.values()).filter(c => c.cap_triggered).length;

  return (
    <div className="fixed left-4 top-[20vh] z-40 w-80 max-h-[calc(40vh-2rem)] overflow-y-auto custom-scrollbar space-y-3">
      {/* Header */}
      <div className="consciousness-panel p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-consciousness-green font-semibold text-lg">
            Pattern Response
          </h2>
          <div className={`text-xs font-medium ${
            connectionState === 'connected' ? 'text-green-400' : 'text-red-400'
          }`}>
            {connectionState === 'connected' ? '🟢' : '🔴'}
          </div>
        </div>
        <p className="text-xs text-observatory-text/60">
          PR-C: Regulation · Rumination · Distraction
        </p>
      </div>

      {/* Pattern Effectiveness Display */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>🎭</span>
          <span>Pattern Effectiveness</span>
        </h3>

        {/* Regulation */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-green-400">Regulation</span>
            <span className="text-xs font-mono text-observatory-text/60">
              {patternCounts.regulation || 0} events
            </span>
          </div>
          <div className="w-full h-2 bg-observatory-dark rounded-full overflow-hidden mb-1">
            <div
              className="h-full bg-green-500 transition-all"
              style={{ width: `${avgEffectiveness('regulation') * 100}%` }}
            />
          </div>
          <div className="text-xs text-observatory-text/60">
            Avg: {(avgEffectiveness('regulation') * 100).toFixed(1)}%
          </div>
        </div>

        {/* Rumination */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-yellow-400">Rumination</span>
            <span className="text-xs font-mono text-observatory-text/60">
              {patternCounts.rumination || 0} events
            </span>
          </div>
          <div className="w-full h-2 bg-observatory-dark rounded-full overflow-hidden mb-1">
            <div
              className="h-full bg-yellow-500 transition-all"
              style={{ width: `${avgEffectiveness('rumination') * 100}%` }}
            />
          </div>
          <div className="text-xs text-observatory-text/60">
            Avg: {(avgEffectiveness('rumination') * 100).toFixed(1)}%
          </div>
        </div>

        {/* Distraction */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-blue-400">Distraction</span>
            <span className="text-xs font-mono text-observatory-text/60">
              {patternCounts.distraction || 0} events
            </span>
          </div>
          <div className="w-full h-2 bg-observatory-dark rounded-full overflow-hidden mb-1">
            <div
              className="h-full bg-blue-500 transition-all"
              style={{ width: `${avgEffectiveness('distraction') * 100}%` }}
            />
          </div>
          <div className="text-xs text-observatory-text/60">
            Avg: {(avgEffectiveness('distraction') * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Rumination Cap Warning */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>⚠️</span>
          <span>Rumination Watch</span>
        </h3>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className={`p-3 rounded ${
            entitiesAtRisk > 0 ? 'bg-red-500/20 border border-red-500/40' : 'bg-observatory-dark/50'
          }`}>
            <div className="text-xs text-observatory-text/60 mb-1">Cap Triggered</div>
            <div className={`text-lg font-mono ${
              entitiesAtRisk > 0 ? 'text-red-400' : 'text-green-400'
            }`}>
              {entitiesAtRisk > 0 ? `⚠️ ${entitiesAtRisk}` : '✅ None'}
            </div>
          </div>
          <div className="bg-observatory-dark/50 p-3 rounded">
            <div className="text-xs text-observatory-text/60 mb-1">Tracking</div>
            <div className="text-lg font-mono text-consciousness-green">
              {ruminationCaps.size}
            </div>
          </div>
        </div>

        {/* Entity States */}
        <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
          {ruminationCaps.size === 0 ? (
            <div className="text-xs text-observatory-text/40 italic text-center py-2">
              No rumination tracking yet
            </div>
          ) : (
            Array.from(ruminationCaps.values()).map((cap, i) => (
              <div key={i} className={`p-2 rounded text-xs ${
                cap.cap_triggered
                  ? 'bg-red-500/20 border border-red-500/40'
                  : 'bg-observatory-dark/30'
              }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-observatory-text/70 truncate flex-1 mr-2">
                    {cap.entity_id}
                  </span>
                  <span className={`font-mono ${
                    cap.cap_triggered ? 'text-red-400' : 'text-observatory-text/60'
                  }`}>
                    {cap.consecutive_frames} frames
                  </span>
                </div>
                {cap.cap_triggered && (
                  <div className="flex items-center justify-between text-observatory-text/50">
                    <span>Penalty: -{(cap.rumination_weight_penalty * 100).toFixed(0)}%</span>
                    <span className="text-red-400 font-medium">⚠️ CAPPED</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Explanation */}
        {entitiesAtRisk > 0 && (
          <div className="mt-3 p-2 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-300">
            <div className="font-medium mb-1">⚠️ Rumination Cap</div>
            <div className="text-observatory-text/70">
              Entity stuck in rumination loop for ≥10 frames. Pattern weight penalized to encourage other strategies.
            </div>
          </div>
        )}
      </div>

      {/* Pattern Weights by Entity */}
      <div className="consciousness-panel p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan mb-3 flex items-center gap-2">
          <span>📊</span>
          <span>Learned Weights</span>
        </h3>

        <div className="space-y-3 max-h-48 overflow-y-auto custom-scrollbar">
          {patternWeights.size === 0 ? (
            <div className="text-xs text-observatory-text/40 italic text-center py-2">
              No pattern weights yet
            </div>
          ) : (
            Array.from(patternWeights.entries()).map(([entityId, weights]) => (
              <div key={entityId} className="bg-observatory-dark/30 p-2 rounded text-xs">
                <div className="text-observatory-text/70 mb-2 truncate">{entityId}</div>

                {/* Regulation */}
                <div className="mb-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-green-400">Regulation</span>
                    <span className="font-mono">{(weights.regulation * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1 bg-observatory-dark rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500"
                      style={{ width: `${weights.regulation * 100}%` }}
                    />
                  </div>
                </div>

                {/* Rumination */}
                <div className="mb-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-yellow-400">Rumination</span>
                    <span className="font-mono">{(weights.rumination * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1 bg-observatory-dark rounded-full overflow-hidden">
                    <div
                      className="h-full bg-yellow-500"
                      style={{ width: `${weights.rumination * 100}%` }}
                    />
                  </div>
                </div>

                {/* Distraction */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-blue-400">Distraction</span>
                    <span className="font-mono">{(weights.distraction * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1 bg-observatory-dark rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500"
                      style={{ width: `${weights.distraction * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
