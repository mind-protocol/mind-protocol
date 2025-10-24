/**
 * Foundations Enrichments Panel
 *
 * PR-E: Six Foundation Mechanisms Visualization
 *
 * Displays real-time metrics for foundational affective mechanisms:
 * 1. Consolidation - Sleep-like memory consolidation during low arousal
 * 2. Decay Resistance - High-affect nodes resist decay
 * 3. Diffusion Stickiness - Affect creates energy "friction"
 * 4. Affective Priming - Recent affect boosts similar nodes
 * 5. Coherence Metric (C) - Alignment between entity affect and graph emotion
 * 6. Criticality Mode - Affect influences ρ target adjustment
 *
 * Per IMPLEMENTATION_PLAN.md PR-E.9:
 * "Dashboard shows all 6 foundation mechanisms with activity indicators"
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-23
 * PR: PR-E (Foundations Enrichments - LOW-MEDIUM RISK)
 */

'use client';

import { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface ConsolidationActivity {
  active: boolean;
  global_arousal: number;  // Current global arousal level
  consolidation_boost: number;  // Multiplier applied (1.0 - 2.0)
  nodes_consolidated: number;  // Nodes affected this frame
  timestamp: number;
}

interface DecayResistance {
  node_id: string;
  emotion_magnitude: number;
  decay_resistance_score: number;  // 0-1, how much decay is resisted
  effective_decay_rate: number;  // Actual decay rate after resistance
  timestamp: number;
}

interface DiffusionStickiness {
  node_id: string;
  stickiness_effect: number;  // Retention multiplier
  energy_retained: number;  // Energy kept due to stickiness
  timestamp: number;
}

interface AffectivePriming {
  node_id: string;
  priming_boost: number;  // Threshold reduction from recent affect
  similarity_to_recent: number;  // Cosine similarity to recent affect
  timestamp: number;
}

interface CoherenceMetric {
  entity_id: string;
  coherence_score: number;  // C = alignment(A, E_graph)
  entity_affect_magnitude: number;
  graph_affect_magnitude: number;
  timestamp: number;
}

interface CriticalityMode {
  mode: 'subcritical' | 'critical' | 'supercritical';
  rho_target: number;  // Desired ρ based on affect
  affect_influence: number;  // How much affect is pushing ρ
  timestamp: number;
}

/**
 * Foundations Enrichments Panel Component
 *
 * Shows 6 foundational affective mechanisms in compact view.
 */
export function FoundationsEnrichmentsPanel() {
  const { connectionState } = useWebSocket();

  // Mechanism states
  const [consolidation, setConsolidation] = useState<ConsolidationActivity | null>(null);
  const [recentDecay, setRecentDecay] = useState<DecayResistance[]>([]);
  const [recentStickiness, setRecentStickiness] = useState<DiffusionStickiness[]>([]);
  const [recentPriming, setRecentPriming] = useState<AffectivePriming[]>([]);
  const [coherenceMetrics, setCoherenceMetrics] = useState<Map<string, CoherenceMetric>>(new Map());
  const [criticalityMode, setCriticalityMode] = useState<CriticalityMode | null>(null);

  // Subscribe to WebSocket events (poll API for now)
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch('/api/consciousness/foundations/status');
        if (res.ok) {
          const data = await res.json();

          if (data.consolidation) setConsolidation(data.consolidation);
          if (data.decay_resistance) setRecentDecay(data.decay_resistance.slice(-10));
          if (data.stickiness) setRecentStickiness(data.stickiness.slice(-10));
          if (data.priming) setRecentPriming(data.priming.slice(-10));

          if (data.coherence) {
            const coherenceMap = new Map<string, CoherenceMetric>();
            data.coherence.forEach((c: CoherenceMetric) => {
              coherenceMap.set(c.entity_id, c);
            });
            setCoherenceMetrics(coherenceMap);
          }

          if (data.criticality) setCriticalityMode(data.criticality);
        }
      } catch (error) {
        console.log('[FoundationsEnrichmentsPanel] Events not available yet:', error);
      }
    };

    // Initial fetch
    fetchEvents();

    // Poll every 2 seconds
    const interval = setInterval(fetchEvents, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed right-4 top-[20vh] z-40 w-80 max-h-[calc(40vh-2rem)] overflow-y-auto custom-scrollbar space-y-3">
      {/* Header */}
      <div className="consciousness-panel p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-consciousness-green font-semibold text-lg">
            Foundations
          </h2>
          <div className={`text-xs font-medium ${
            connectionState === 'connected' ? 'text-green-400' : 'text-red-400'
          }`}>
            {connectionState === 'connected' ? '🟢' : '🔴'}
          </div>
        </div>
        <p className="text-xs text-observatory-text/60">
          PR-E: 6 Foundation Mechanisms
        </p>
      </div>

      {/* Consolidation */}
      <div className="consciousness-panel p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-observatory-cyan flex items-center gap-1">
            <span>💤</span>
            <span>Consolidation</span>
          </h3>
          <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
            consolidation?.active ? 'bg-purple-500/20 text-purple-400' : 'bg-observatory-dark text-observatory-text/60'
          }`}>
            {consolidation?.active ? 'ACTIVE' : 'IDLE'}
          </span>
        </div>

        {consolidation && (
          <div className="grid grid-cols-3 gap-2 text-[10px]">
            <div>
              <div className="text-observatory-text/60 mb-0.5">Arousal</div>
              <div className="font-mono text-observatory-text">
                {(consolidation.global_arousal * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-observatory-text/60 mb-0.5">Boost</div>
              <div className="font-mono text-observatory-text">
                {consolidation.consolidation_boost.toFixed(2)}x
              </div>
            </div>
            <div>
              <div className="text-observatory-text/60 mb-0.5">Nodes</div>
              <div className="font-mono text-observatory-text">
                {consolidation.nodes_consolidated}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Decay Resistance */}
      <div className="consciousness-panel p-3">
        <h3 className="text-xs font-semibold text-observatory-cyan mb-2 flex items-center gap-1">
          <span>🛡️</span>
          <span>Decay Resistance</span>
          <span className="text-[10px] font-normal text-observatory-text/60">
            ({recentDecay.length} active)
          </span>
        </h3>

        <div className="space-y-1 max-h-24 overflow-y-auto custom-scrollbar">
          {recentDecay.length === 0 ? (
            <div className="text-[10px] text-observatory-text/40 italic text-center py-1">
              No resistance events
            </div>
          ) : (
            recentDecay.slice(-5).map((event, i) => (
              <div key={i} className="bg-observatory-dark/30 p-1.5 rounded flex items-center justify-between text-[10px]">
                <span className="text-observatory-text/70 truncate max-w-[120px]">
                  {event.node_id}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-observatory-text/50">
                    {(event.decay_resistance_score * 100).toFixed(0)}%
                  </span>
                  <div className="w-12 h-1 bg-observatory-dark rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500"
                      style={{ width: `${event.decay_resistance_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Diffusion Stickiness */}
      <div className="consciousness-panel p-3">
        <h3 className="text-xs font-semibold text-observatory-cyan mb-2 flex items-center gap-1">
          <span>🧲</span>
          <span>Diffusion Stickiness</span>
          <span className="text-[10px] font-normal text-observatory-text/60">
            ({recentStickiness.length} active)
          </span>
        </h3>

        <div className="space-y-1 max-h-24 overflow-y-auto custom-scrollbar">
          {recentStickiness.length === 0 ? (
            <div className="text-[10px] text-observatory-text/40 italic text-center py-1">
              No stickiness events
            </div>
          ) : (
            recentStickiness.slice(-5).map((event, i) => (
              <div key={i} className="bg-observatory-dark/30 p-1.5 rounded flex items-center justify-between text-[10px]">
                <span className="text-observatory-text/70 truncate max-w-[120px]">
                  {event.node_id}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-observatory-text/50">
                    {(event.stickiness_effect * 100).toFixed(0)}%
                  </span>
                  <span className="text-observatory-text/60">
                    +{event.energy_retained.toFixed(3)}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Affective Priming */}
      <div className="consciousness-panel p-3">
        <h3 className="text-xs font-semibold text-observatory-cyan mb-2 flex items-center gap-1">
          <span>⚡</span>
          <span>Affective Priming</span>
          <span className="text-[10px] font-normal text-observatory-text/60">
            ({recentPriming.length} active)
          </span>
        </h3>

        <div className="space-y-1 max-h-24 overflow-y-auto custom-scrollbar">
          {recentPriming.length === 0 ? (
            <div className="text-[10px] text-observatory-text/40 italic text-center py-1">
              No priming events
            </div>
          ) : (
            recentPriming.slice(-5).map((event, i) => (
              <div key={i} className="bg-observatory-dark/30 p-1.5 rounded flex items-center justify-between text-[10px]">
                <span className="text-observatory-text/70 truncate max-w-[120px]">
                  {event.node_id}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-observatory-text/50">
                    sim: {event.similarity_to_recent.toFixed(2)}
                  </span>
                  <span className="text-green-400">
                    -{(event.priming_boost * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Coherence Metric (C) */}
      <div className="consciousness-panel p-3">
        <h3 className="text-xs font-semibold text-observatory-cyan mb-2 flex items-center gap-1">
          <span>🎯</span>
          <span>Coherence (C)</span>
          <span className="text-[10px] font-normal text-observatory-text/60">
            ({coherenceMetrics.size} entities)
          </span>
        </h3>

        <div className="space-y-1 max-h-24 overflow-y-auto custom-scrollbar">
          {coherenceMetrics.size === 0 ? (
            <div className="text-[10px] text-observatory-text/40 italic text-center py-1">
              No coherence tracking
            </div>
          ) : (
            Array.from(coherenceMetrics.values()).map((metric, i) => (
              <div key={i} className="bg-observatory-dark/30 p-1.5 rounded text-[10px]">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-observatory-text/70 truncate max-w-[120px]">
                    {metric.entity_id}
                  </span>
                  <span className={`font-mono ${
                    metric.coherence_score > 0.7 ? 'text-green-400' :
                    metric.coherence_score > 0.3 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {(metric.coherence_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full h-1 bg-observatory-dark rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      metric.coherence_score > 0.7 ? 'bg-green-500' :
                      metric.coherence_score > 0.3 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${metric.coherence_score * 100}%` }}
                  />
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Criticality Mode */}
      <div className="consciousness-panel p-3">
        <h3 className="text-xs font-semibold text-observatory-cyan mb-2 flex items-center gap-1">
          <span>⚖️</span>
          <span>Criticality Mode</span>
        </h3>

        {criticalityMode ? (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className={`text-xs font-bold ${
                criticalityMode.mode === 'critical' ? 'text-green-400' :
                criticalityMode.mode === 'subcritical' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {criticalityMode.mode.toUpperCase()}
              </span>
              <span className="text-[10px] text-observatory-text/60">
                ρ target: {criticalityMode.rho_target.toFixed(3)}
              </span>
            </div>
            <div className="w-full h-2 bg-observatory-dark rounded-full overflow-hidden">
              <div
                className={`h-full ${
                  criticalityMode.mode === 'critical' ? 'bg-green-500' :
                  criticalityMode.mode === 'subcritical' ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${Math.abs(criticalityMode.affect_influence) * 100}%` }}
              />
            </div>
            <div className="text-[10px] text-observatory-text/60 mt-1">
              Affect influence: {(criticalityMode.affect_influence * 100).toFixed(1)}%
            </div>
          </div>
        ) : (
          <div className="text-[10px] text-observatory-text/40 italic text-center py-1">
            No criticality data
          </div>
        )}
      </div>
    </div>
  );
}
