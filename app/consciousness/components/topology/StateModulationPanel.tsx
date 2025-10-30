/**
 * StateModulationPanel - State-Dependent Weight Modulation Visualization
 *
 * Shows how arousal, precision, and goal_alignment modulate edge weights
 * in real-time. Reveals the dynamic routing mode of consciousness.
 *
 * Implements specs from:
 * - docs/specs/v2/orchestration/STATE_DEPENDENT_WEIGHT_MODULATION.md
 * - docs/specs/v2/orchestration/TOPOLOGY_ANALYZER_EVENT_WIRING.md
 *
 * Event Schema: topology.v1 spec
 * - state_modulation.frame (per consciousness frame)
 *
 * Weight Modulation Formula:
 * w_eff_semantic = w_semantic × precision
 * w_eff_intent = w_intent × goal_alignment
 * w_eff_affect = w_affect × arousal
 * w_eff_experience = w_experience (unmodulated)
 * w_eff_total = (w_eff_sem × w_eff_int × w_eff_aff × w_eff_exp)^0.25
 */

'use client';

import { TopologyState } from '../../hooks/useGraphStream';

interface StateModulationPanelProps {
  topology: TopologyState;
}

export function StateModulationPanel({ topology }: StateModulationPanelProps) {
  const hasData = topology.stateModulation !== null;

  if (!hasData) {
    return (
      <div className="text-center py-4">
        <p className="text-xs text-observatory-silver/60">
          Waiting for state modulation events...
        </p>
        <p className="text-[10px] text-observatory-silver/40 mt-1">
          (Backend must emit state_modulation.frame events)
        </p>
      </div>
    );
  }

  const state = topology.stateModulation!;

  // Determine dominant routing mode
  const modes = [
    { name: 'Affect-Driven', value: state.arousal, color: 'text-pink-400' },
    { name: 'Semantic-Driven', value: state.precision, color: 'text-blue-400' },
    { name: 'Goal-Driven', value: state.goal_alignment, color: 'text-green-400' }
  ];
  const dominantMode = modes.reduce((max, mode) => mode.value > max.value ? mode : max);

  // Format timestamp for last update
  const lastUpdate = topology.lastStateUpdate
    ? new Date(topology.lastStateUpdate).toLocaleTimeString()
    : 'Never';

  return (
    <div className="state-modulation-panel space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between px-2">
        <div className="text-xs font-semibold text-observatory-text/80">
          Routing Mode
        </div>
        <div className="text-[10px] text-observatory-silver/50">
          Updated: {lastUpdate}
        </div>
      </div>

      {/* Dominant Mode Banner */}
      <div className={`px-3 py-2 bg-opacity-20 rounded border ${
        dominantMode.name === 'Affect-Driven'
          ? 'bg-pink-900 border-pink-500/40'
          : dominantMode.name === 'Semantic-Driven'
          ? 'bg-blue-900 border-blue-500/40'
          : 'bg-green-900 border-green-500/40'
      }`}>
        <div className="flex items-center justify-between">
          <span className={`text-sm font-semibold ${dominantMode.color}`}>
            {dominantMode.name}
          </span>
          <span className={`text-xs font-mono ${dominantMode.color}`}>
            {dominantMode.value.toFixed(2)}
          </span>
        </div>
      </div>

      {/* State Dimensions */}
      <div className="space-y-2">
        <StateDimension
          label="Arousal"
          value={state.arousal}
          color="pink"
          description="Amplifies affective edges"
        />
        <StateDimension
          label="Precision"
          value={state.precision}
          color="blue"
          description="Amplifies semantic edges"
        />
        <StateDimension
          label="Goal Alignment"
          value={state.goal_alignment}
          color="green"
          description="Amplifies goal edges"
        />
      </div>

      {/* Top Modulated Edges */}
      {state.top_modulated_edges && state.top_modulated_edges.length > 0 && (
        <div className="pt-2 border-t border-observatory-teal/20">
          <div className="text-xs font-semibold text-observatory-text/80 mb-2 px-2">
            Top Modulated Edges
          </div>
          <div className="space-y-1">
            {state.top_modulated_edges.slice(0, 5).map((edge, idx) => (
              <EdgeModulation key={idx} edge={edge} />
            ))}
          </div>
        </div>
      )}

      {/* Interpretation Guide */}
      <div className="px-2 pt-2 border-t border-observatory-teal/20">
        <div className="text-[10px] text-observatory-silver/50 space-y-1">
          <div className="flex items-start gap-1">
            <span className="text-pink-400">•</span>
            <span>High arousal → Emotion-guided traversal</span>
          </div>
          <div className="flex items-start gap-1">
            <span className="text-blue-400">•</span>
            <span>High precision → Semantic-guided traversal</span>
          </div>
          <div className="flex items-start gap-1">
            <span className="text-green-400">•</span>
            <span>High alignment → Goal-guided traversal</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function StateDimension({
  label,
  value,
  color,
  description
}: {
  label: string;
  value: number;
  color: 'pink' | 'blue' | 'green';
  description: string;
}) {
  const colorClasses = {
    pink: {
      text: 'text-pink-400',
      bg: 'bg-pink-500'
    },
    blue: {
      text: 'text-blue-400',
      bg: 'bg-blue-500'
    },
    green: {
      text: 'text-green-400',
      bg: 'bg-green-500'
    }
  };

  const colors = colorClasses[color];

  return (
    <div className="px-2">
      <div className="flex items-center justify-between mb-1">
        <div>
          <span className={`text-xs font-semibold ${colors.text}`}>{label}</span>
          <span className="text-[10px] text-observatory-silver/50 ml-2">{description}</span>
        </div>
        <span className={`text-xs font-mono ${colors.text}`}>{value.toFixed(2)}</span>
      </div>
      <div className="h-1.5 bg-observatory-dark/50 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${colors.bg}`}
          style={{ width: `${Math.min(value * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}

function EdgeModulation({
  edge
}: {
  edge: { source: string; target: string; w_base: number; w_eff: number };
}) {
  const delta = edge.w_eff - edge.w_base;
  const percentChange = ((delta / edge.w_base) * 100);
  const isAmplified = delta > 0;

  return (
    <div className="px-3 py-1.5 bg-observatory-dark/20 rounded border border-observatory-teal/10">
      <div className="flex items-center justify-between">
        {/* Edge */}
        <div className="flex items-center gap-1 flex-1 min-w-0">
          <span className="text-[10px] text-observatory-silver/70 font-mono truncate">
            {edge.source}
          </span>
          <span className="text-[10px] text-observatory-silver/50">→</span>
          <span className="text-[10px] text-observatory-silver/70 font-mono truncate">
            {edge.target}
          </span>
        </div>

        {/* Weight Change */}
        <div className="flex items-center gap-2">
          <div className="text-right">
            <div className="text-[10px] text-observatory-silver/50">
              {edge.w_base.toFixed(2)} → {edge.w_eff.toFixed(2)}
            </div>
          </div>
          <div className={`text-xs font-semibold ${
            isAmplified ? 'text-green-400' : 'text-red-400'
          }`}>
            {isAmplified ? '+' : ''}{percentChange.toFixed(0)}%
          </div>
        </div>
      </div>
    </div>
  );
}
